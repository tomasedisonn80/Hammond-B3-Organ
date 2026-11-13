#include "TestSupport.h"
#include "hammond/Percussion.h"

#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <limits>

namespace {

using namespace hammond;

constexpr std::array<double, 3> kRates{44100.0, 48000.0, 96000.0};
// Project numerical target for the bounded tests below, not hardware tolerance.
constexpr long double kAnalyticTolerance = 1.0e-11L;
long double maximum_analytic_error = 0.0L;
std::size_t analytic_comparisons = 0;
std::size_t invalid_profiles = 0;

[[nodiscard]] PercussionSettings enabled_settings() {
    PercussionSettings settings;
    settings.enabled = true;
    return settings;
}

[[nodiscard]] long double decay_after(long double initial, std::uint32_t frames,
                                      double rate, double tau) {
    // Solve the continuous constant-coefficient segment directly. Do not reuse
    // the implementation's per-sample coefficient or recurrence.
    const long double elapsed = static_cast<long double>(frames) /
                                static_cast<long double>(rate);
    return initial * std::exp(-elapsed / static_cast<long double>(tau));
}

[[nodiscard]] long double recovery_after(long double initial, std::uint32_t frames,
                                         double rate, double tau) {
    const long double elapsed = static_cast<long double>(frames) /
                                static_cast<long double>(rate);
    return initial + (1.0L - initial) *
                         -std::expm1(-elapsed / static_cast<long double>(tau));
}

void check_analytic(double actual, long double expected) {
    const long double error = std::fabs(static_cast<long double>(actual) - expected);
    if (error > maximum_analytic_error) maximum_analytic_error = error;
    ++analytic_comparisons;
    CHECK_NEAR(actual, expected, kAnalyticTolerance);
}

void advance(PercussionState& state, std::uint32_t frames, bool detector,
             const PercussionSettings& settings) {
    for (std::uint32_t frame = 0; frame < frames; ++frame) {
        CHECK(state.advance_frame(detector, settings));
        CHECK(std::isfinite(state.readiness()));
        CHECK(state.readiness() >= 0.0 && state.readiness() <= 1.0);
    }
}

void equal_future(PercussionState actual, PercussionState reference) {
    CHECK(actual.diagnostics() == reference.diagnostics());
    auto settings = enabled_settings();
    for (std::uint32_t frame = 0; frame < 97; ++frame) {
        settings.harmonic = frame % 2 == 0 ? PercussionHarmonic::Second
                                            : PercussionHarmonic::Third;
        settings.volume = frame % 3 == 0 ? PercussionVolume::Soft
                                         : PercussionVolume::Normal;
        settings.decay = frame % 5 == 0 ? PercussionDecay::Fast
                                        : PercussionDecay::Slow;
        CHECK(actual.gain(settings) == reference.gain(settings));
        CHECK(actual.upper_sustain_gain(settings) == reference.upper_sustain_gain(settings));
        CHECK(actual.advance_frame(frame % 7 != 0, settings));
        CHECK(reference.advance_frame(frame % 7 != 0, settings));
        CHECK(actual.diagnostics() == reference.diagnostics());
    }
}

void test_unprepared_and_defaults() {
    PercussionState state;
    const PercussionDiagnostics initial{false, 0.0, 0.0};
    CHECK(state.diagnostics() == initial);
    CHECK(!state.prepared());
    CHECK(state.readiness() == 0.0);
    auto settings = enabled_settings();
    CHECK(state.gain(settings) == 0.0);
    CHECK(state.upper_sustain_gain(settings) == 1.0);
    CHECK(!state.advance_frame(true, settings));
    CHECK(!state.advance_frame(false, settings));
    CHECK(state.diagnostics() == initial);
    CHECK(state.prepare(PercussionProfile{}, 48000.0) == Status::InvalidProfile);
    CHECK(state.diagnostics() == initial);

    const PercussionSettings defaults;
    CHECK(is_valid_percussion_settings(defaults));
    CHECK(!defaults.enabled);
    CHECK(defaults.harmonic == PercussionHarmonic::Second);
    CHECK(defaults.volume == PercussionVolume::Normal);
    CHECK(defaults.decay == PercussionDecay::Slow);
    CHECK(state.prepare(make_nominal_percussion_profile(), 48000.0) == Status::Ok);
    CHECK(state.readiness() == 1.0);
    CHECK(state.gain(defaults) == 0.0);
    CHECK(state.upper_sustain_gain(defaults) == 1.0);
    CHECK(!state.advance_frame(true, defaults));
    CHECK(state.readiness() == 1.0);
    CHECK(state.advance_frame(false, defaults));
    CHECK(state.readiness() == 1.0);
}

void test_closed_form_segments() {
    const auto profile = make_nominal_percussion_profile();
    // Independent component arithmetic checks what the named factory supplies.
    CHECK_NEAR(profile.slow_decay_seconds, 4.7e6L * 0.33e-6L, 1.0e-15L);
    CHECK_NEAR(profile.fast_decay_seconds,
               0.33e-6L / (1.0L / 1.5e6L + 1.0L / 4.7e6L), 1.0e-15L);
    CHECK_NEAR(profile.recovery_seconds, (82.0e3L + 22.0e3L) * 0.33e-6L, 1.0e-16L);

    for (const double rate : kRates) {
        for (const auto decay : {PercussionDecay::Slow, PercussionDecay::Fast}) {
            PercussionState state;
            CHECK(state.prepare(profile, rate) == Status::Ok);
            auto settings = enabled_settings();
            settings.decay = decay;
            const double tau = decay == PercussionDecay::Slow
                                   ? profile.slow_decay_seconds : profile.fast_decay_seconds;
            const double initial_gain = decay == PercussionDecay::Slow ? 1.0 : 1.5;
            // The first rendered sample uses q[0], not an already advanced q[1].
            CHECK(state.gain(settings) == initial_gain);
            CHECK(state.readiness() == 1.0);
            const auto one_second = static_cast<std::uint32_t>(rate);
            const std::array<std::uint32_t, 7> checkpoints{
                0, 1, 3, 127, 1024, one_second / 3, one_second};
            std::uint32_t previous = 0;
            for (const auto frame : checkpoints) {
                advance(state, frame - previous, true, settings);
                const long double expected = decay_after(1.0L, frame, rate, tau);
                check_analytic(state.readiness(), expected);
                CHECK_NEAR(state.gain(settings), expected * initial_gain, 2.0e-11L);
                previous = frame;
            }

            // Continue from the theoretical endpoint, not from the actual q,
            // so a defect in the decay path cannot calibrate the recovery oracle.
            const long double start = decay_after(1.0L, one_second, rate, tau);
            const auto recovery_frames = one_second / 10;
            double last = state.readiness();
            for (std::uint32_t frame = 1; frame <= recovery_frames; ++frame) {
                CHECK(state.advance_frame(false, settings));
                CHECK(state.readiness() >= last && state.readiness() <= 1.0);
                last = state.readiness();
                if (frame == 1 || frame == 7 || frame == recovery_frames) {
                    check_analytic(last, recovery_after(start, frame, rate, profile.recovery_seconds));
                }
            }
        }
    }
}

void test_controls_and_piecewise_history() {
    const auto profile = make_nominal_percussion_profile();
    for (const double rate : kRates) {
        PercussionState state;
        CHECK(state.prepare(profile, rate) == Status::Ok);
        auto settings = enabled_settings();
        const auto slow_frames = static_cast<std::uint32_t>(rate) / 4;
        advance(state, slow_frames, true, settings);
        long double expected = decay_after(1.0L, slow_frames, rate, profile.slow_decay_seconds);
        check_analytic(state.readiness(), expected);

        // Arbitrarily many same-time setting/diagnostic queries consume no
        // samples. They cannot create recharge for an off/on or routing edit.
        const auto before = state.diagnostics();
        for (const bool enabled : {false, true}) {
            for (const auto harmonic : {PercussionHarmonic::Second, PercussionHarmonic::Third}) {
                for (const auto volume : {PercussionVolume::Normal, PercussionVolume::Soft}) {
                    for (const auto decay : {PercussionDecay::Slow, PercussionDecay::Fast}) {
                        settings = {enabled, harmonic, volume, decay};
                        const double level = volume == PercussionVolume::Normal ? 1.0 : 0.5;
                        const double boost = decay == PercussionDecay::Fast ? 1.5 : 1.0;
                        CHECK_NEAR(state.gain(settings),
                                   enabled ? before.readiness * level * boost : 0.0, 1.0e-15);
                        CHECK(state.upper_sustain_gain(settings) ==
                              (enabled && volume == PercussionVolume::Normal
                                   ? profile.normal_sustain_gain : 1.0));
                        CHECK(state.diagnostics() == before);
                    }
                }
            }
        }

        // A continuing physical detector with changed harmonic/volume joins
        // the existing readiness. Only changing decay changes its time slope.
        settings = {true, PercussionHarmonic::Third, PercussionVolume::Soft, PercussionDecay::Fast};
        const auto fast_frames = static_cast<std::uint32_t>(rate) / 8;
        advance(state, fast_frames, true, settings);
        expected = decay_after(expected, fast_frames, rate, profile.fast_decay_seconds);
        check_analytic(state.readiness(), expected);
        CHECK_NEAR(state.gain(settings), expected * 0.75L, kAnalyticTolerance);

        settings.enabled = false;
        const auto released_frames = static_cast<std::uint32_t>(rate) / 100;
        advance(state, released_frames, false, settings);
        expected = recovery_after(expected, released_frames, rate, profile.recovery_seconds);
        check_analytic(state.readiness(), expected);
        CHECK(state.gain(settings) == 0.0);
        settings.enabled = true;
        CHECK_NEAR(state.gain(settings), expected * 0.75L, kAnalyticTolerance);

        const auto continuing_frames = static_cast<std::uint32_t>(rate) / 20;
        advance(state, continuing_frames, true, settings);
        expected = decay_after(expected, continuing_frames, rate, profile.fast_decay_seconds);
        check_analytic(state.readiness(), expected);

        // Positive release gaps recover monotonically; a zero gap is an exact
        // unchanged copy. All cases begin with one common nonzero history.
        const PercussionState held = state;
        double preceding_gap = held.readiness();
        for (const std::uint32_t gap : {0U, 1U, 2U, 17U, 127U, 1024U}) {
            auto released = held;
            advance(released, gap, false, settings);
            CHECK(released.readiness() >= preceding_gap);
            check_analytic(released.readiness(),
                           recovery_after(expected, gap, rate, profile.recovery_seconds));
            if (gap == 0) CHECK(released.diagnostics() == held.diagnostics());
            preceding_gap = released.readiness();
        }
    }
}

void test_invalid_inputs_are_atomic() {
    const auto valid_profile = make_nominal_percussion_profile();
    auto settings = enabled_settings();
    PercussionState baseline;
    CHECK(baseline.prepare(valid_profile, 48000.0) == Status::Ok);
    advance(baseline, 12345, true, settings);
    const auto before = baseline.diagnostics();

    const auto reject_profile = [&](const PercussionProfile& profile) {
        auto candidate = baseline;
        CHECK(validate_percussion_profile(profile, 48000.0) == Status::InvalidProfile);
        CHECK(candidate.prepare(profile, 48000.0) == Status::InvalidProfile);
        CHECK(candidate.diagnostics() == before);
        equal_future(candidate, baseline);
        ++invalid_profiles;
    };
    const double nan = std::numeric_limits<double>::quiet_NaN();
    const double infinity = std::numeric_limits<double>::infinity();
    const std::array<double PercussionProfile::*, 3> times{
        &PercussionProfile::slow_decay_seconds, &PercussionProfile::fast_decay_seconds,
        &PercussionProfile::recovery_seconds};
    for (const auto member : times) {
        for (const double invalid : {nan, infinity, -infinity, -1.0, 0.0,
                                    std::nextafter(0.0001, 0.0),
                                    std::nextafter(60.0, infinity)}) {
            auto profile = valid_profile;
            profile.*member = invalid;
            reject_profile(profile);
        }
    }
    const std::array<double PercussionProfile::*, 4> gains{
        &PercussionProfile::normal_gain, &PercussionProfile::soft_gain,
        &PercussionProfile::fast_gain_multiplier, &PercussionProfile::normal_sustain_gain};
    for (const auto member : gains) {
        const double maximum = member == &PercussionProfile::normal_sustain_gain ? 1.0 : 4.0;
        for (const double invalid : {nan, infinity, -infinity,
                                    std::nextafter(0.0, -1.0),
                                    std::nextafter(maximum, infinity)}) {
            auto profile = valid_profile;
            profile.*member = invalid;
            reject_profile(profile);
        }
    }

    for (const double rate : {nan, infinity, -infinity, 0.0, -48000.0,
                             22050.0, 192000.0, std::nextafter(48000.0, infinity)}) {
        auto candidate = baseline;
        CHECK(validate_percussion_profile(valid_profile, rate) == Status::InvalidSpec);
        CHECK(candidate.prepare(valid_profile, rate) == Status::InvalidSpec);
        equal_future(candidate, baseline);
    }

    for (std::uint16_t invalid = 2; invalid <= 255; ++invalid) {
        for (std::size_t field = 0; field < 3; ++field) {
            auto bad = settings;
            if (field == 0) bad.harmonic = static_cast<PercussionHarmonic>(invalid);
            if (field == 1) bad.volume = static_cast<PercussionVolume>(invalid);
            if (field == 2) bad.decay = static_cast<PercussionDecay>(invalid);
            auto candidate = baseline;
            CHECK(!is_valid_percussion_settings(bad));
            CHECK(candidate.gain(bad) == 0.0);
            CHECK(candidate.upper_sustain_gain(bad) == 1.0);
            CHECK(!candidate.advance_frame(true, bad));
            CHECK(!candidate.advance_frame(false, bad));
            equal_future(candidate, baseline);
        }
    }
    settings.enabled = false;
    auto inconsistent = baseline;
    CHECK(!inconsistent.advance_frame(true, settings));
    equal_future(inconsistent, baseline);
}

void test_support_boundaries_and_tail() {
    auto settings = enabled_settings();
    for (const double rate : kRates) {
        for (const double tau : {0.0001, 60.0}) {
            const PercussionProfile profile{tau, tau, tau, 4.0, 4.0, 4.0, 0.0};
            PercussionState state;
            CHECK(validate_percussion_profile(profile, rate) == Status::Ok);
            CHECK(state.prepare(profile, rate) == Status::Ok);
            settings.decay = PercussionDecay::Fast;
            CHECK(state.gain(settings) == 16.0);
            CHECK(state.upper_sustain_gain(settings) == 0.0);
            const auto frames = static_cast<std::uint32_t>(rate) / 1000;
            advance(state, frames, true, settings);
            const auto expected = decay_after(1.0L, frames, rate, tau);
            check_analytic(state.readiness(), expected);
            CHECK(state.gain(settings) >= 0.0 && state.gain(settings) <= 16.0);
            advance(state, frames, false, settings);
            check_analytic(state.readiness(), recovery_after(expected, frames, rate, tau));
        }

        // The declared truncation is at binary64's smallest *normal* value.
        // Observe an entire fast tail: no exposed nonzero subnormal survives.
        const PercussionProfile tiny{0.0001, 0.0001, 0.03432, 1.0, 0.0, 1.0, 1.0};
        PercussionState state;
        CHECK(state.prepare(tiny, rate) == Status::Ok);
        const long double normal = std::numeric_limits<double>::min();
        const long double boundary_frames = -std::log(normal) *
                                           static_cast<long double>(rate) * 0.0001L;
        const auto just_before = static_cast<std::uint32_t>(std::floor(boundary_frames)) - 2U;
        const auto safely_after = static_cast<std::uint32_t>(std::ceil(boundary_frames)) + 2U;
        double previous = state.readiness();
        for (std::uint32_t frame = 1; frame <= safely_after; ++frame) {
            CHECK(state.advance_frame(true, settings));
            const double value = state.readiness();
            CHECK(value >= 0.0 && value <= previous);
            CHECK(value == 0.0 || std::fpclassify(value) == FP_NORMAL);
            if (frame == just_before) CHECK(value > 0.0);
            previous = value;
        }
        CHECK(state.readiness() == 0.0);
        CHECK(state.gain(settings) == 0.0);
        advance(state, 100, true, settings);
        CHECK(state.readiness() == 0.0);
        CHECK(state.advance_frame(false, settings));
        CHECK(state.readiness() > 0.0);
        CHECK_NEAR(state.readiness(), recovery_after(0.0L, 1, rate, tiny.recovery_seconds), 1.0e-16L);

        auto zero = make_nominal_percussion_profile();
        zero.normal_gain = 0.0;
        zero.soft_gain = 0.0;
        zero.fast_gain_multiplier = 0.0;
        zero.normal_sustain_gain = 1.0;
        CHECK(state.prepare(zero, rate) == Status::Ok);
        advance(state, 17, true, settings);
        CHECK(state.gain(settings) == 0.0);
        CHECK(state.upper_sustain_gain(settings) == 1.0);
    }
}

void test_profile_ownership_and_explicit_reset() {
    PercussionProfile caller{0.25, 0.125, 0.5, 1.25, 0.375, 2.25, 0.8};
    PercussionState state;
    CHECK(state.prepare(caller, 48000.0) == Status::Ok);
    const PercussionState reference = state;
    caller = {};
    CHECK(caller.slow_decay_seconds == 0.0);
    auto settings = enabled_settings();
    settings.volume = PercussionVolume::Soft;
    settings.decay = PercussionDecay::Fast;
    CHECK(state.gain(settings) == 0.84375);
    advance(state, 12000, true, settings);
    check_analytic(state.readiness(), std::exp(-2.0L));
    CHECK_NEAR(state.gain(settings), std::exp(-2.0L) * 0.84375L, kAnalyticTolerance);
    CHECK(reference.readiness() == 1.0);
    auto independent = reference;
    advance(independent, 12000, true, settings);
    equal_future(state, independent);

    // Successful prepare is the explicit reset boundary; mere settings edits
    // above never have this effect. A caller-created invalid profile cannot.
    CHECK(state.prepare(make_nominal_percussion_profile(), 44100.0) == Status::Ok);
    CHECK(state.readiness() == 1.0);
    CHECK(state.diagnostics().sample_rate == 44100.0);
}

} // namespace

int main() {
    test_unprepared_and_defaults();
    test_closed_form_segments();
    test_controls_and_piecewise_history();
    test_invalid_inputs_are_atomic();
    test_support_boundaries_and_tail();
    test_profile_ownership_and_explicit_reset();
    std::cout << "Percussion checks passed: " << analytic_comparisons
              << " closed-form comparisons, " << invalid_profiles
              << " invalid profiles, 762 invalid enum settings; maximum absolute q error="
              << std::setprecision(12) << maximum_analytic_error << '\n';
    return 0;
}
