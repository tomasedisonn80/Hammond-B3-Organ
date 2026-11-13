#include "TestSupport.h"
#include "hammond/Percussion.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <limits>

namespace {

using namespace hammond;

constexpr std::array<double, 3> kRates{44100.0, 48000.0, 96000.0};
// Bounded binary64 accumulation allowance, not a physical calibration tolerance.
constexpr long double kTolerance = 1.0e-11L;
std::size_t migration_checks = 0;
std::size_t rejected_changes = 0;
std::size_t analytic_comparisons = 0;
std::size_t future_frames = 0;
std::size_t same_rate_calls = 0;
std::size_t instantaneous_gain_checks = 0;
long double maximum_error = 0.0L;

[[nodiscard]] std::uint64_t bits(double value) {
    return std::bit_cast<std::uint64_t>(value);
}

[[nodiscard]] PercussionSettings settings_for(std::size_t mode) {
    return {mode != 3, PercussionHarmonic::Second, PercussionVolume::Normal,
            mode == 1 ? PercussionDecay::Fast : PercussionDecay::Slow};
}

[[nodiscard]] std::array<PercussionSettings, 16> all_settings() {
    std::array<PercussionSettings, 16> result{};
    std::size_t index = 0;
    for (const bool enabled : {false, true}) {
        for (const auto harmonic : {PercussionHarmonic::Second, PercussionHarmonic::Third}) {
            for (const auto volume : {PercussionVolume::Normal, PercussionVolume::Soft}) {
                for (const auto decay : {PercussionDecay::Slow, PercussionDecay::Fast}) {
                    result[index++] = {enabled, harmonic, volume, decay};
                }
            }
        }
    }
    return result;
}

[[nodiscard]] long double closed_form(long double initial, std::uint32_t frames,
                                     double rate, double tau, bool detector) {
    // One continuous-time solution for the whole segment; neither the core's
    // per-sample coefficient nor its floating-point recurrence is copied.
    const long double elapsed = static_cast<long double>(frames) /
                                static_cast<long double>(rate);
    const long double exponent = -elapsed / static_cast<long double>(tau);
    return detector ? initial * std::exp(exponent)
                    : initial + (1.0L - initial) * -std::expm1(exponent);
}

void analytic(double actual, long double expected) {
    const long double error = std::fabs(static_cast<long double>(actual) - expected);
    if (error > maximum_error) maximum_error = error;
    ++analytic_comparisons;
    CHECK_NEAR(actual, expected, kTolerance);
}

void advance(PercussionState& state, std::uint32_t frames, bool detector,
             const PercussionSettings& settings) {
    for (std::uint32_t frame = 0; frame < frames; ++frame) {
        CHECK(state.advance_frame(detector, settings));
        const double value = state.readiness();
        CHECK(std::isfinite(value));
        CHECK(value >= 0.0 && value <= 1.0);
        CHECK(value == 0.0 || std::fpclassify(value) == FP_NORMAL);
    }
}

void migrate(PercussionState& state, double rate) {
    const auto before = state;
    CHECK(state.reconfigure_sample_rate(rate) == Status::Ok);
    ++migration_checks;
    CHECK(state.prepared());
    CHECK(state.diagnostics().sample_rate == rate);
    CHECK(bits(state.readiness()) == bits(before.readiness()));
    for (const auto settings : all_settings()) {
        CHECK(bits(state.gain(settings)) == bits(before.gain(settings)));
        CHECK(bits(state.upper_sustain_gain(settings)) ==
              bits(before.upper_sustain_gain(settings)));
        instantaneous_gain_checks += 2;
    }
}

void exact_future(PercussionState actual, PercussionState reference) {
    // First use the installed rate without reconfiguring again. Recomputing it
    // immediately could hide a failed change that corrupted old coefficients.
    for (std::size_t segment = 0; segment < 4; ++segment) {
        CHECK(actual.diagnostics() == reference.diagnostics());
        CHECK(bits(actual.readiness()) == bits(reference.readiness()));
        if (segment != 0) {
            const double rate = kRates[segment - 1];
            CHECK(actual.reconfigure_sample_rate(rate) == Status::Ok);
            CHECK(reference.reconfigure_sample_rate(rate) == Status::Ok);
        }
        for (std::uint32_t frame = 0; frame < 127; ++frame) {
            auto settings = settings_for(static_cast<std::size_t>(frame) % 4);
            settings.harmonic = frame % 2 == 0 ? PercussionHarmonic::Second
                                                : PercussionHarmonic::Third;
            settings.volume = frame % 5 == 0 ? PercussionVolume::Soft
                                             : PercussionVolume::Normal;
            const bool detector = settings.enabled && frame % 7 != 0;
            CHECK(bits(actual.gain(settings)) == bits(reference.gain(settings)));
            CHECK(bits(actual.upper_sustain_gain(settings)) ==
                  bits(reference.upper_sustain_gain(settings)));
            CHECK(actual.advance_frame(detector, settings));
            CHECK(reference.advance_frame(detector, settings));
            CHECK(actual.diagnostics() == reference.diagnostics());
            CHECK(bits(actual.readiness()) == bits(reference.readiness()));
            ++future_frames;
        }
    }
}

void test_all_rate_pairs_and_support_profiles() {
    const std::array<PercussionProfile, 5> profiles{
        make_nominal_percussion_profile(),
        PercussionProfile{0.0001, 60.0, 0.75, 4.0, 0.0, 4.0, 0.0},
        PercussionProfile{60.0, 0.0001, 60.0, 0.0, 4.0, 0.0, 1.0},
        PercussionProfile{0.0001, 0.0001, 0.0001, 1.25, 0.25, 0.5, 0.375},
        PercussionProfile{60.0, 60.0, 60.0, 4.0, 4.0, 4.0, 1.0}};
    constexpr std::array<std::uint32_t, 6> checkpoints{0, 1, 3, 17, 127, 401};
    for (const auto profile : profiles) {
        for (const double old_rate : kRates) {
            for (const double new_rate : kRates) {
                for (std::size_t mode = 0; mode < 4; ++mode) {
                    PercussionState state;
                    CHECK(state.prepare(profile, old_rate) == Status::Ok);
                    const double duration = std::min(0.02, profile.fast_decay_seconds * 0.25);
                    const auto warm_frames = std::max(1U,
                        static_cast<std::uint32_t>(old_rate * duration));
                    advance(state, warm_frames, true, settings_for(1));
                    const long double initial = closed_form(
                        1.0L, warm_frames, old_rate, profile.fast_decay_seconds, true);
                    CHECK(state.readiness() > 0.0 && state.readiness() < 1.0);
                    analytic(state.readiness(), initial);

                    const auto settings = settings_for(mode);
                    const bool detector = mode < 2;
                    const double tau = !detector ? profile.recovery_seconds :
                        settings.decay == PercussionDecay::Fast
                            ? profile.fast_decay_seconds : profile.slow_decay_seconds;
                    migrate(state, new_rate);
                    std::uint32_t previous = 0;
                    for (const auto frame : checkpoints) {
                        advance(state, frame - previous, detector, settings);
                        analytic(state.readiness(), closed_form(initial, frame, new_rate, tau, detector));
                        previous = frame;
                    }
                    if (!settings.enabled) CHECK(state.gain(settings) == 0.0);
                }
            }
        }
    }
}

void test_mixed_rate_elapsed_time_and_owned_profile() {
    struct Segment {
        double rate;
        std::uint32_t frames;
        std::size_t mode;
    };
    constexpr std::array<Segment, 12> segments{{
        {44100.0, 733, 0}, {96000.0, 1201, 0}, {48000.0, 127, 1},
        {96000.0, 2003, 2}, {44100.0, 887, 3}, {48000.0, 0, 0},
        {44100.0, 4093, 1}, {44100.0, 123, 1}, {96000.0, 511, 2},
        {48000.0, 881, 3}, {96000.0, 379, 0}, {44100.0, 1337, 1}}};
    const std::array<PercussionProfile, 3> profiles{
        make_nominal_percussion_profile(),
        PercussionProfile{0.003125, 0.0125, 0.00625, 3.5, 0.125, 2.25, 0.25},
        PercussionProfile{60.0, 0.0001, 60.0, 0.0, 4.0, 4.0, 0.0}};
    for (auto profile : profiles) {
        const auto owned = profile;
        PercussionState state;
        CHECK(state.prepare(profile, 48000.0) == Status::Ok);
        // Destroy the caller's values after prepare. Migration must retain the
        // installed profile, not reread borrowed or newly selected parameters.
        profile = PercussionProfile{};
        long double expected = 1.0L;
        for (const auto segment : segments) {
            migrate(state, segment.rate);
            const auto settings = settings_for(segment.mode);
            const bool detector = segment.mode < 2;
            const double tau = !detector ? owned.recovery_seconds :
                settings.decay == PercussionDecay::Fast
                    ? owned.fast_decay_seconds : owned.slow_decay_seconds;
            advance(state, segment.frames, detector, settings);
            expected = closed_form(expected, segment.frames, segment.rate, tau, detector);
            analytic(state.readiness(), expected);
            if (expected < static_cast<long double>(std::numeric_limits<double>::min())) {
                CHECK(state.readiness() == 0.0);
                expected = 0.0L;
            }
            const auto before = state;
            auto disabled = settings;
            disabled.enabled = false;
            CHECK(!state.advance_frame(true, disabled));
            CHECK(state.diagnostics() == before.diagnostics());
            exact_future(state, before);
        }
        // The explicit reset operation remains distinct from rate migration.
        CHECK(state.prepare(owned, 96000.0) == Status::Ok);
        CHECK(state.readiness() == 1.0);
        CHECK(state.diagnostics().sample_rate == 96000.0);
    }
}

void test_invalid_rates_and_not_prepared_precedence() {
    const double infinity = std::numeric_limits<double>::infinity();
    const std::array<double, 19> invalid_rates{
        std::numeric_limits<double>::quiet_NaN(), infinity, -infinity,
        0.0, -0.0, -48000.0, 1.0, 22050.0, 88200.0, 192000.0,
        std::numeric_limits<double>::denorm_min(), std::numeric_limits<double>::max(),
        std::nextafter(44100.0, 0.0), std::nextafter(44100.0, infinity),
        std::nextafter(48000.0, 0.0), std::nextafter(48000.0, infinity),
        std::nextafter(96000.0, 0.0), std::nextafter(96000.0, infinity), 48000.25};
    PercussionState empty;
    const auto initial = empty.diagnostics();
    for (const double rate : invalid_rates) {
        CHECK(empty.reconfigure_sample_rate(rate) == Status::NotPrepared);
        CHECK(empty.diagnostics() == initial);
        ++rejected_changes;
    }
    for (const double rate : kRates) {
        CHECK(empty.reconfigure_sample_rate(rate) == Status::NotPrepared);
        CHECK(empty.diagnostics() == initial);
        ++rejected_changes;
    }

    for (const double installed_rate : kRates) {
        for (std::size_t history = 0; history < 4; ++history) {
            auto profile = make_nominal_percussion_profile();
            if (history == 3) profile.slow_decay_seconds = profile.fast_decay_seconds = 0.0001;
            PercussionState baseline;
            CHECK(baseline.prepare(profile, installed_rate) == Status::Ok);
            if (history != 0) advance(baseline, history == 3 ? 10000U : 773U, true, settings_for(1));
            if (history == 2) advance(baseline, 219, false, settings_for(3));
            if (history == 3) CHECK(baseline.readiness() == 0.0);
            for (const double rate : invalid_rates) {
                auto actual = baseline;
                CHECK(actual.reconfigure_sample_rate(rate) == Status::InvalidSpec);
                CHECK(actual.diagnostics() == baseline.diagnostics());
                CHECK(bits(actual.readiness()) == bits(baseline.readiness()));
                ++rejected_changes;
                exact_future(actual, baseline);
            }
        }
    }
}

void test_same_rate_is_an_exact_no_op() {
    const std::array<PercussionProfile, 3> profiles{
        make_nominal_percussion_profile(),
        PercussionProfile{0.0001, 60.0, 0.0001, 4.0, 0.0, 4.0, 0.0},
        PercussionProfile{60.0, 0.0001, 60.0, 0.0, 4.0, 0.0, 1.0}};
    for (const auto profile : profiles) {
        for (const double rate : kRates) {
            PercussionState actual;
            CHECK(actual.prepare(profile, rate) == Status::Ok);
            advance(actual, 139, true, settings_for(1));
            auto reference = actual;
            for (std::uint32_t frame = 0; frame < 2048; ++frame) {
                const auto before = actual.diagnostics();
                const std::size_t repetitions = frame % 128 == 0 ? 17 : 1;
                for (std::size_t repeat = 0; repeat < repetitions; ++repeat) {
                    CHECK(actual.reconfigure_sample_rate(rate) == Status::Ok);
                    CHECK(actual.diagnostics() == before);
                    CHECK(bits(actual.readiness()) == bits(before.readiness));
                    ++same_rate_calls;
                }
                const auto settings = settings_for(static_cast<std::size_t>(frame / 19) % 4);
                const bool detector = settings.enabled && frame % 7 != 0;
                CHECK(bits(actual.gain(settings)) == bits(reference.gain(settings)));
                CHECK(actual.advance_frame(detector, settings));
                CHECK(reference.advance_frame(detector, settings));
                CHECK(actual.diagnostics() == reference.diagnostics());
                ++future_frames;
            }
        }
    }
}

void test_zero_and_normal_tail_survive_migration() {
    const PercussionProfile profile{0.0001, 0.0001, 0.0001, 1.0, 0.5, 1.5, 0.75};
    const auto active = settings_for(1);
    const long double minimum = std::numeric_limits<double>::min();
    const long double threshold_seconds = -std::log(minimum) * 0.0001L;
    for (const double old_rate : kRates) {
        PercussionState baseline;
        CHECK(baseline.prepare(profile, old_rate) == Status::Ok);
        const auto before_tail = static_cast<std::uint32_t>(
            std::floor(threshold_seconds * static_cast<long double>(old_rate))) - 8U;
        advance(baseline, before_tail, true, active);
        CHECK(baseline.readiness() >= std::numeric_limits<double>::min());
        const long double elapsed = static_cast<long double>(before_tail) /
                                    static_cast<long double>(old_rate);
        for (const double new_rate : kRates) {
            auto state = baseline;
            migrate(state, new_rate);
            const auto predicted = static_cast<std::uint32_t>(std::ceil(
                (threshold_seconds - elapsed) * static_cast<long double>(new_rate)));
            CHECK(predicted > 1);
            std::uint32_t first_zero = 0;
            for (std::uint32_t frame = 1; frame <= predicted + 3U; ++frame) {
                const double previous = state.readiness();
                advance(state, 1, true, active);
                CHECK(state.readiness() <= previous);
                if (state.readiness() == 0.0 && first_zero == 0) first_zero = frame;
            }
            CHECK(first_zero >= predicted - 1U && first_zero <= predicted + 1U);
            CHECK(state.readiness() == 0.0);
            migrate(state, old_rate);
            CHECK(bits(state.readiness()) == bits(0.0));
            advance(state, 7, true, active);
            CHECK(state.readiness() == 0.0);
            const auto off = settings_for(3);
            advance(state, 1, false, off);
            CHECK(state.readiness() > 0.0);
            CHECK(state.gain(off) == 0.0);
            analytic(state.readiness(), closed_form(0.0L, 1, old_rate,
                                                    profile.recovery_seconds, false));
        }
    }
}

} // namespace

int main() {
    test_all_rate_pairs_and_support_profiles();
    test_mixed_rate_elapsed_time_and_owned_profile();
    test_invalid_rates_and_not_prepared_precedence();
    test_same_rate_is_an_exact_no_op();
    test_zero_and_normal_tail_survive_migration();
    std::cout << "Percussion rate lifecycle passed: " << migration_checks
              << " tracked migrations, " << rejected_changes << " rejected changes, "
              << same_rate_calls << " exact same-rate calls, " << analytic_comparisons
              << " analytic comparisons, " << instantaneous_gain_checks
              << " instantaneous gain checks, " << future_frames << " exact future frames; max q error "
              << std::setprecision(17) << static_cast<double>(maximum_error) << '\n';
}
