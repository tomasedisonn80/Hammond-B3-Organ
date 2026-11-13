#include "TestSupport.h"
#include "hammond/Engine.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <limits>
#include <numbers>

namespace {
using hammond::Engine;
using hammond::Event;
using hammond::EventType;
using hammond::Manual;
using hammond::ProcessSpec;
using hammond::RuntimeProfile;
using hammond::Status;
using hammond::ToneId;
using hammond::TonewheelBank;
using SourceFrame = std::array<double, hammond::kToneSourceCount>;

static_assert(std::numeric_limits<double>::radix == 2 &&
              std::numeric_limits<double>::digits == 53);
constexpr std::array<double, 3> kRates{44100.0, 48000.0, 96000.0};
constexpr double kMinimumIncrement = 0x1p-53;
// Frozen seed-zero answers; no production PRNG or phase recurrence in this test.
constexpr double kTone1Offset = 0x1.c4415072f63b9p-1;
constexpr double kTone13Offset = 0x1.0c43407fc177bp-1;
constexpr double kTone91Offset = 0x1.0e371331cd614p-3;

SourceFrame bank_phases(const TonewheelBank& bank) {
    SourceFrame result{};
    for (std::size_t i = 0; i < result.size(); ++i) {
        CHECK(bank.phase_turns(static_cast<ToneId>(i + 1), result[i]));
    }
    return result;
}

SourceFrame engine_phases(const Engine& engine) {
    SourceFrame result{};
    for (std::size_t i = 0; i < result.size(); ++i) {
        CHECK(engine.source_phase_turns(static_cast<ToneId>(i + 1), result[i]));
    }
    return result;
}

void advance_equal(TonewheelBank& bank, TonewheelBank& reference, unsigned frames) {
    SourceFrame actual{};
    SourceFrame expected{};
    for (unsigned frame = 0; frame < frames; ++frame) {
        bank.process_frame(actual);
        reference.process_frame(expected);
        CHECK(actual == expected);
    }
    CHECK(bank_phases(bank) == bank_phases(reference));
}

void test_increment_floor(const RuntimeProfile& nominal) {
    for (double rate : kRates) {
        const double minimum_hz = rate * kMinimumIncrement;
        const double below_hz = std::nextafter(minimum_hz, 0.0);
        const double above_hz = std::nextafter(minimum_hz,
                                              std::numeric_limits<double>::infinity());
        CHECK(below_hz / rate == std::nextafter(kMinimumIncrement, 0.0));
        CHECK(minimum_hz / rate == kMinimumIncrement);
        CHECK(above_hz / rate == std::nextafter(kMinimumIncrement, 1.0));

        TonewheelBank bank;
        TonewheelBank reference;
        CHECK(bank.prepare(nominal, rate, 0) == Status::Ok);
        CHECK(reference.prepare(nominal, rate, 0) == Status::Ok);
        advance_equal(bank, reference, 19);
        for (double rejected_hz : {1e-300, below_hz}) {
            auto rejected = nominal;
            for (auto& source : rejected.sources) {
                source.peak_amplitude = 0.25;
                source.base_phase_turns = 0.25;
            }
            // Failure follows 90 otherwise valid candidate source preparations.
            rejected.sources.back().frequency_hz = rejected_hz;
            CHECK(rejected_hz / rate > 0.0);
            CHECK(hammond::validate_runtime_profile(rejected, rate) == Status::Ok);
            const auto before = bank_phases(bank);
            CHECK(bank.prepare(rejected, rate, 1) == Status::InvalidProfile);
            CHECK(bank.prepared());
            CHECK(bank_phases(bank) == before);
            advance_equal(bank, reference, 257);

            TonewheelBank fresh;
            CHECK(fresh.prepare(rejected, rate, 1) == Status::InvalidProfile);
            CHECK(!fresh.prepared());
            SourceFrame silence{};
            silence.fill(1.0);
            fresh.process_frame(silence);
            CHECK(silence == SourceFrame{});
            double destination = -1.0;
            CHECK(!fresh.phase_turns(1, destination));
            CHECK(destination == -1.0);
        }

        const std::array<double, 5> starts{
            0.0, 0.25, 0.5, 0.75, std::nextafter(1.0, 0.0)};
        for (double accepted_hz : {minimum_hz, above_hz}) {
            for (double start : starts) {
                auto boundary = nominal;
                boundary.sources.front().frequency_hz = accepted_hz;
                boundary.sources.front().base_phase_turns =
                    (start >= kTone1Offset ? start : 1.0 + start) - kTone1Offset;
                TonewheelBank progressing;
                CHECK(progressing.prepare(boundary, rate, 0) == Status::Ok);
                double previous = -1.0;
                CHECK(progressing.phase_turns(1, previous));
                CHECK(previous == start);
                SourceFrame output{};
                for (unsigned frame = 0; frame < 8; ++frame) {
                    progressing.process_frame(output);
                    double next = -1.0;
                    CHECK(progressing.phase_turns(1, next));
                    CHECK(std::isfinite(next) && next >= 0.0 && next < 1.0);
                    CHECK(next != previous);
                    if (frame == 0 && start == starts.back()) CHECK(next < previous);
                    else CHECK(next > previous);
                    previous = next;
                }
            }
        }
    }
}

void test_engine_floor_rejection(const RuntimeProfile& nominal) {
    constexpr std::array<Event, 3> controls{{
        {0, EventType::Drawbar, Manual::Upper, 0, 8.0},
        {0, EventType::NoteOn, Manual::Upper, 60, 100.0},
        {0, EventType::Expression, Manual::Upper, 0, 0.75}}};
    for (double rate : kRates) {
        const ProcessSpec spec{rate, 64, 0, 731};
        Engine engine;
        Engine reference;
        CHECK(engine.prepare(nominal, spec) == Status::Ok);
        CHECK(reference.prepare(nominal, spec) == Status::Ok);
        std::array<float, 64> actual{};
        std::array<float, 64> expected{};
        CHECK(engine.process(64, actual, controls).ok());
        CHECK(reference.process(64, expected, controls).ok());
        CHECK(actual == expected);
        const auto before_phases = engine_phases(engine);
        const auto before_controls = engine.controls_snapshot();
        const auto before_clock = engine.frame_clock();
        auto rejected = nominal;
        rejected.output_gain = 0.0;
        rejected.sources.back().frequency_hz =
            std::nextafter(rate * kMinimumIncrement, 0.0);
        CHECK(engine.prepare(rejected, ProcessSpec{rate, 1, 99, 0}) == Status::InvalidProfile);
        CHECK(engine.prepared());
        CHECK(engine.frame_clock() == before_clock);
        CHECK(engine.controls_snapshot() == before_controls);
        CHECK(engine.active_key_count() == 1);
        CHECK(engine.key_down(Manual::Upper, 60));
        CHECK(engine_phases(engine) == before_phases);
        // Includes cached mix/profile, maximum block size, source state and clock.
        CHECK(engine.process(64, actual, {}).ok());
        CHECK(reference.process(64, expected, {}).ok());
        CHECK(actual == expected);
        CHECK(engine.frame_clock() == reference.frame_clock());
        CHECK(engine_phases(engine) == engine_phases(reference));
    }
}

struct RationalIncrement { std::uint64_t numerator; std::uint64_t denominator; };

RationalIncrement exact_increment(double frequency, double rate) {
    // The two nominal extremes admit an exact uint64 denominator at all rates.
    // Binary64 f = significand * 2^(exponent-53); no rounded f/rate is reused.
    int exponent = 0;
    const double mantissa = std::frexp(frequency, &exponent);
    CHECK(exponent > 0 && exponent < 53);
    const auto shift = static_cast<unsigned>(53 - exponent);
    const auto integer_rate = static_cast<std::uint64_t>(rate);
    CHECK(integer_rate <= (std::numeric_limits<std::uint64_t>::max() >> shift));
    return {static_cast<std::uint64_t>(std::ldexp(mantissa, 53)), integer_rate << shift};
}

std::uint64_t add_mod(std::uint64_t a, std::uint64_t b, std::uint64_t modulus) {
    // a,b < modulus. This form avoids overflow even when modulus exceeds 2^63.
    return a >= modulus - b ? a - (modulus - b) : a + b;
}

long double reference_phase(RationalIncrement increment, double initial,
                           std::uint64_t frames) {
    std::uint64_t remainder = 0;
    std::uint64_t addend = increment.numerator % increment.denominator;
    while (frames != 0) {
        if ((frames & 1U) != 0) remainder = add_mod(remainder, addend, increment.denominator);
        frames >>= 1U;
        if (frames != 0) addend = add_mod(addend, addend, increment.denominator);
    }
    // Exact elapsed-frame integer residue, followed only by bounded [0,2) FP
    // arithmetic. Independent of recurrence; works when long double == double.
    const long double fraction = static_cast<long double>(remainder) /
                                 static_cast<long double>(increment.denominator);
    return std::fmod(static_cast<long double>(initial) + fraction, 1.0L);
}

long double phase_budget(std::uint64_t frames) {
    // RN binary64 addition below 1.5: <= 2^-53; division below 0.5: <= 2^-55.
    // Subtracting 1 at wrap is exact. Extra budget covers oracle conversions.
    return static_cast<long double>(frames) * (0x1p-53L + 0x1p-55L) +
           8.0L * std::numeric_limits<long double>::epsilon();
}

void test_nominal_extreme_drift(const RuntimeProfile& nominal) {
    constexpr std::uint64_t frames = 262144;
    constexpr std::array<std::size_t, 2> indices{0, 90};
    constexpr std::array<double, 2> offsets{kTone1Offset, kTone91Offset};
    constexpr long double two_pi = 2.0L * std::numbers::pi_v<long double>;
    for (double rate : kRates) {
        TonewheelBank bank;
        CHECK(bank.prepare(nominal, rate, 0) == Status::Ok);
        std::array<RationalIncrement, 2> increments{};
        for (std::size_t anchor = 0; anchor < indices.size(); ++anchor) {
            const auto& source = nominal.sources[indices[anchor]];
            CHECK(source.base_phase_turns == 0.0);
            increments[anchor] = exact_increment(source.frequency_hz, rate);
        }
        std::array<long double, 2> worst_phase{};
        std::array<long double, 2> worst_sample{};
        SourceFrame output{};
        for (std::uint64_t frame = 0; frame <= frames; ++frame) {
            const bool checkpoint = frame < 16 || frame % 1024 == 0;
            std::array<long double, 2> expected_phase{};
            for (std::size_t anchor = 0; anchor < indices.size(); ++anchor) {
                double actual_phase = -1.0;
                CHECK(bank.phase_turns(static_cast<ToneId>(indices[anchor] + 1), actual_phase));
                CHECK(std::isfinite(actual_phase) && actual_phase >= 0.0 && actual_phase < 1.0);
                if (checkpoint) {
                    expected_phase[anchor] = reference_phase(increments[anchor], offsets[anchor], frame);
                    const long double difference = std::fabs(actual_phase - expected_phase[anchor]);
                    const long double error = std::min(difference, 1.0L - difference);
                    worst_phase[anchor] = std::max(worst_phase[anchor], error);
                    CHECK_NEAR(error, 0.0L, phase_budget(frame));
                }
            }
            if (frame == frames) break;
            bank.process_frame(output);
            for (std::size_t anchor = 0; anchor < indices.size(); ++anchor) {
                const std::size_t index = indices[anchor];
                const double amplitude = nominal.sources[index].peak_amplitude;
                CHECK(std::isfinite(output[index]) && std::fabs(output[index]) <= amplitude);
                if (checkpoint) {
                    const long double expected = amplitude * std::sin(two_pi * expected_phase[anchor]);
                    worst_sample[anchor] = std::max(worst_sample[anchor],
                        std::fabs(static_cast<long double>(output[index]) - expected));
                    const long double tolerance = amplitude *
                        (two_pi * phase_budget(frame) + 8.0L * std::numeric_limits<double>::epsilon());
                    CHECK_NEAR(output[index], expected, tolerance);
                }
            }
        }
        for (std::size_t anchor = 0; anchor < indices.size(); ++anchor) {
            std::cout << "nominal " << rate << " Hz, tone " << indices[anchor] + 1
                      << ": maximum checked phase error " << worst_phase[anchor]
                      << " turns, sample error " << worst_sample[anchor] << '\n';
        }
    }
    std::cout << "phase budget at " << frames << " frames: " << phase_budget(frames)
              << " turns; long-double significand bits: " << std::numeric_limits<long double>::digits << '\n';
}

void test_all_keys_maximum_mix(const RuntimeProfile& nominal) {
    constexpr std::size_t branches = hammond::kManualCount * hammond::kManualKeyCount *
                                     hammond::kDrawbarCount;
    static_assert(branches == 1098);
    std::array<Event, hammond::kManualCount * (hammond::kDrawbarCount + hammond::kManualKeyCount)> events{};
    std::size_t next = 0;
    for (Manual manual : {Manual::Upper, Manual::Lower}) {
        for (std::size_t bar = 0; bar < hammond::kDrawbarCount; ++bar) {
            events[next++] = {0, EventType::Drawbar, manual, static_cast<std::uint8_t>(bar), 8.0};
        }
        for (unsigned note = hammond::kMinManualMidiNote; note <= hammond::kMaxManualMidiNote; ++note) {
            events[next++] = {0, EventType::NoteOn, manual, static_cast<std::uint8_t>(note), 127.0};
        }
    }
    CHECK(next == events.size());
    const float bound = static_cast<float>(branches);
    const float rounded_bound = std::nextafter(bound, std::numeric_limits<float>::infinity());
    for (double rate : kRates) {
        auto maximum = nominal;
        maximum.output_gain = 1.0;
        for (auto& row : maximum.manual_map) row.fill(13);
        maximum.sources[12].peak_amplitude = 1.0;
        maximum.sources[12].base_phase_turns = 1.25 - kTone13Offset;
        maximum.sources[12].frequency_hz = rate * 0.25;
        Engine engine;
        CHECK(engine.prepare(maximum, ProcessSpec{rate, 256, 0, 0}) == Status::Ok);
        std::array<float, 256> output{};
        CHECK(engine.process(256, output, events).ok());
        CHECK(engine.active_key_count() == 122);
        for (float sample : output) {
            CHECK(std::isfinite(sample));
            CHECK(std::fabs(sample) <= rounded_bound);
        }
        // Synthetic coherent routing attains both signs of the 1098-unit bound.
        CHECK_NEAR(output[0], bound, rounded_bound - bound);
        CHECK_NEAR(output[2], -bound, rounded_bound - bound);
        std::cout << "maximum mix " << rate << " Hz: " << output[0] << ", " << output[2]
                  << "; finite bound including one float ULP: " << rounded_bound << '\n';
    }
}
} // namespace

int main() {
    const RuntimeProfile nominal = load_test_profile();
    std::cout << std::setprecision(std::numeric_limits<long double>::max_digits10);
    test_increment_floor(nominal);
    test_engine_floor_rejection(nominal);
    test_nominal_extreme_drift(nominal);
    test_all_keys_maximum_mix(nominal);
    std::cout << "numerical boundary checks passed\n";
}
