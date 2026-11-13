#include "TestSupport.h"
#include "hammond/TonewheelBank.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <limits>
#include <numbers>
#include <vector>

namespace {
using hammond::RuntimeProfile;
using hammond::Status;
using hammond::ToneId;
using hammond::TonewheelBank;
using Frame = std::array<double, hammond::kToneSourceCount>;

constexpr std::array<double, 3> kSampleRates{44100.0, 48000.0, 96000.0};
constexpr std::uint64_t kSeed = 0x0123456789abcdef;
constexpr long double kTwoPi = 2.0L * std::numbers::pi_v<long double>;

struct Errors {
    long double sample{0.0L};
    long double phase{0.0L};
};

ToneId tone_id(std::size_t index) {
    CHECK(index < hammond::kToneSourceCount);
    return static_cast<ToneId>(index + 1);
}

Frame phases(const TonewheelBank& bank) {
    Frame result{};
    for (std::size_t index = 0; index < result.size(); ++index) {
        CHECK(bank.phase_turns(tone_id(index), result[index]));
        CHECK(std::isfinite(result[index]));
        CHECK(result[index] >= 0.0 && result[index] < 1.0);
    }
    return result;
}

long double wrapped(long double turns) {
    return turns - std::floor(turns);
}

long double phase_distance(long double actual, long double expected) {
    const long double distance = std::fabs(actual - expected);
    return std::min(distance, 1.0L - distance);
}

long double reference_phase(double initial, double frequency, double sample_rate,
                            std::uint64_t elapsed_frames) {
    // An elapsed-time oracle, not another copy of the bank's phase recurrence.
    return wrapped(static_cast<long double>(initial) +
        static_cast<long double>(elapsed_frames) * static_cast<long double>(frequency) /
        static_cast<long double>(sample_rate));
}

long double phase_tolerance(std::uint64_t elapsed_frames) {
    // Conservative double-roundoff allowance: eight epsilons per accumulated
    // frame, including division/addition/wrapping and the initial phase.
    return 8.0L * std::numeric_limits<double>::epsilon() *
        (static_cast<long double>(elapsed_frames) + 1.0L);
}

void check_phases(const TonewheelBank& bank, const RuntimeProfile& profile,
                  const Frame& initial, double sample_rate,
                  std::uint64_t elapsed_frames, Errors& errors) {
    const Frame actual = phases(bank);
    for (std::size_t index = 0; index < actual.size(); ++index) {
        const long double expected = reference_phase(initial[index],
            profile.sources[index].frequency_hz, sample_rate, elapsed_frames);
        const long double error = phase_distance(actual[index], expected);
        errors.phase = std::max(errors.phase, error);
        CHECK_NEAR(error, 0.0L, phase_tolerance(elapsed_frames));
    }
}

void check_samples(const Frame& actual, const RuntimeProfile& profile,
                   const Frame& initial, double sample_rate,
                   std::uint64_t elapsed_frames, Errors& errors) {
    // |sin(a)-sin(b)| <= |a-b|; add a small allowance for the sine evaluation.
    const long double tolerance = kTwoPi * phase_tolerance(elapsed_frames) + 2e-15L;
    for (std::size_t index = 0; index < actual.size(); ++index) {
        const auto& source = profile.sources[index];
        const long double expected_phase = reference_phase(initial[index],
            source.frequency_hz, sample_rate, elapsed_frames);
        const long double expected = static_cast<long double>(source.peak_amplitude) *
            std::sin(kTwoPi * expected_phase);
        errors.sample = std::max(errors.sample,
            std::fabs(static_cast<long double>(actual[index]) - expected));
        CHECK_NEAR(actual[index], expected, tolerance);
    }
}

void check_bounds(const Frame& frame, const RuntimeProfile& profile) {
    for (std::size_t index = 0; index < frame.size(); ++index) {
        CHECK(std::isfinite(frame[index]));
        CHECK(std::fabs(frame[index]) <= profile.sources[index].peak_amplitude);
    }
}

void advance_equal(TonewheelBank& first, TonewheelBank& second, std::size_t count) {
    Frame first_frame{};
    Frame second_frame{};
    for (std::size_t frame = 0; frame < count; ++frame) {
        first.process_frame(first_frame);
        second.process_frame(second_frame);
        CHECK(first_frame == second_frame);
    }
    CHECK(phases(first) == phases(second));
}

void test_numeric_identity_and_anchors(const RuntimeProfile& profile) {
    CHECK(hammond::kToneSourceCount == 91);
    CHECK(hammond::kMinToneId == 1);
    CHECK(hammond::kMaxToneId == 91);
    for (unsigned raw_id = 0; raw_id <= 255; ++raw_id) {
        std::size_t destination = 999;
        const bool valid = raw_id >= 1 && raw_id <= 91;
        CHECK(hammond::tone_id_to_index(static_cast<ToneId>(raw_id), destination) == valid);
        CHECK(destination == (valid ? static_cast<std::size_t>(raw_id - 1) : 999));
    }

    struct Anchor { ToneId id; unsigned nominal_midi; long double frequency_hz; };
    // Numerical 12-TET fixtures from the atlas convention, not physical terminals,
    // factory gearing, a measured tuning table, or the manual's MIDI range.
    constexpr std::array<Anchor, 8> anchors{{
        {1, 24, 32.703195662574829L}, {13, 36, 65.406391325149658L},
        {46, 69, 440.0L}, {58, 81, 880.0L}, {70, 93, 1760.0L},
        {73, 96, 2093.0045224047890L}, {82, 105, 3520.0L},
        {91, 114, 5919.9107633861500L}}};

    for (double sample_rate : kSampleRates) {
        TonewheelBank bank;
        CHECK(bank.prepare(profile, sample_rate, kSeed) == Status::Ok);
        const Frame before = phases(bank);
        Frame output{};
        bank.process_frame(output);
        const Frame after = phases(bank);
        for (const auto& anchor : anchors) {
            std::size_t index = 999;
            CHECK(hammond::tone_id_to_index(anchor.id, index));
            CHECK(index + 1 == anchor.id);
            CHECK(static_cast<unsigned>(anchor.id) + 23U == anchor.nominal_midi);
            CHECK_NEAR(profile.sources[index].frequency_hz, anchor.frequency_hz, 2e-10L);
            const long double advance = wrapped(static_cast<long double>(after[index]) -
                                                static_cast<long double>(before[index]));
            CHECK_NEAR(advance * sample_rate, anchor.frequency_hz, 5e-10L);
        }
    }
}

void test_seed_known_answers(const RuntimeProfile& profile) {
    constexpr std::array<ToneId, 6> ids{1, 2, 3, 46, 90, 91};
    constexpr std::array<std::uint64_t, 3> seeds{
        0, kSeed, std::numeric_limits<std::uint64_t>::max()};
    // Fixed known answers for the documented SplitMix64 convention (note13).
    // The test contains no PRNG recurrence. Hexadecimal values retain exact
    // top-53-bit offsets, including unsigned wrap and late source draw positions.
    constexpr std::array<std::array<double, 6>, 3> expected{{
        {{0x1.c4415072f63b9p-1, 0x1.b9e279aa86e58p-2, 0x1.b117462002500p-6,
          0x1.d9dccac614d23p-1, 0x1.010da3274de56p-1, 0x1.0e371331cd614p-3}},
        {{0x1.57a3807a48fa8p-4, 0x1.aae6a5366943ap-1, 0x1.7c85b974cb6e4p-3,
          0x1.a7e0aa74fb57ap-2, 0x1.8bab013bfe908p-2, 0x1.6475a47df0dbcp-2}},
        {{0x1.c9b2e2ee36ca5p-1, 0x1.d33ff0cfb7ed0p-1, 0x1.c17fc26593940p-3,
          0x1.fef5432ddefd8p-4, 0x1.fc92e5b816ed8p-4, 0x1.cce19841632b4p-3}}}};

    auto zero_base = profile;
    for (auto& source : zero_base.sources) {
        source.base_phase_turns = 0.0;
        source.peak_amplitude = 0.0; // Muted sources must still consume their draw.
    }
    for (double sample_rate : kSampleRates) {
        for (std::size_t seed_index = 0; seed_index < seeds.size(); ++seed_index) {
            TonewheelBank bank;
            CHECK(bank.prepare(zero_base, sample_rate, seeds[seed_index]) == Status::Ok);
            for (std::size_t anchor = 0; anchor < ids.size(); ++anchor) {
                double actual = -1.0;
                CHECK(bank.phase_turns(ids[anchor], actual));
                CHECK(actual == expected[seed_index][anchor]);
            }
        }
    }
}

void test_seed_replay(const RuntimeProfile& profile) {
    for (double sample_rate : kSampleRates) {
        TonewheelBank first;
        TonewheelBank replay;
        TonewheelBank changed;
        CHECK(first.prepare(profile, sample_rate, 0) == Status::Ok);
        CHECK(replay.prepare(profile, sample_rate, 0) == Status::Ok);
        CHECK(changed.prepare(profile, sample_rate, 1) == Status::Ok);
        const Frame initial = phases(first);
        CHECK(initial == phases(replay));
        CHECK(initial != phases(changed));
        Frame first_output{};
        Frame replay_output{};
        Frame changed_output{};
        Frame first_sample{};
        bool changed_audio = false;
        for (std::size_t frame = 0; frame < 2048; ++frame) {
            first.process_frame(first_output);
            replay.process_frame(replay_output);
            changed.process_frame(changed_output);
            CHECK(first_output == replay_output);
            changed_audio = changed_audio || first_output != changed_output;
            if (frame == 0) first_sample = first_output;
        }
        CHECK(changed_audio);
        CHECK(phases(first) == phases(replay));
        CHECK(first.prepare(profile, sample_rate, 0) == Status::Ok);
        CHECK(phases(first) == initial);
        first.process_frame(first_output);
        CHECK(first_output == first_sample);
    }
}

RuntimeProfile varied_sources(const RuntimeProfile& nominal, double sample_rate) {
    auto result = nominal;
    const std::array<double, 5> base_phases{
        0.0, 0.25, 0.5, 0.75, std::nextafter(1.0, 0.0)};
    for (std::size_t index = 0; index < result.sources.size(); ++index) {
        auto& source = result.sources[index];
        source.frequency_hz = 37.25 + 17.125 * static_cast<double>(index);
        source.peak_amplitude = static_cast<double>(index % 9) / 8.0;
        source.base_phase_turns = base_phases[index % base_phases.size()];
    }
    result.sources.back().frequency_hz = sample_rate * 0.499;
    result.sources.back().peak_amplitude = 1.0;
    return result;
}

void test_base_phases_and_current_sample(const RuntimeProfile& nominal, Errors& errors) {
    for (double sample_rate : kSampleRates) {
        const RuntimeProfile profile = varied_sources(nominal, sample_rate);
        auto zero_base = profile;
        for (auto& source : zero_base.sources) source.base_phase_turns = 0.0;
        TonewheelBank bank;
        TonewheelBank offsets;
        CHECK(bank.prepare(profile, sample_rate, kSeed) == Status::Ok);
        CHECK(offsets.prepare(zero_base, sample_rate, kSeed) == Status::Ok);
        const Frame initial = phases(bank);
        const Frame seeded = phases(offsets);
        for (std::size_t index = 0; index < initial.size(); ++index) {
            const long double expected = wrapped(static_cast<long double>(seeded[index]) +
                static_cast<long double>(profile.sources[index].base_phase_turns));
            CHECK_NEAR(phase_distance(initial[index], expected), 0.0L, 3e-16L);
        }

        Frame output{};
        for (std::uint64_t frame = 0; frame < 1025; ++frame) {
            output.fill(std::numeric_limits<double>::quiet_NaN());
            bank.process_frame(output);
            check_bounds(output, profile);
            check_samples(output, profile, initial, sample_rate, frame, errors);
            check_phases(bank, profile, initial, sample_rate, frame + 1, errors);
        }
        // At frame zero the oracle uses the supplied current phase; after that
        // very call diagnostics must already identify the next sample's phase.
    }
}

void test_all_muted_sources_advance(const RuntimeProfile& nominal, Errors& errors) {
    for (double sample_rate : kSampleRates) {
        auto profile = nominal;
        for (auto& source : profile.sources) source.peak_amplitude = 0.0;
        TonewheelBank bank;
        CHECK(bank.prepare(profile, sample_rate, kSeed) == Status::Ok);
        const Frame initial = phases(bank);
        Frame output{};
        constexpr std::uint64_t frame_count = 4097;
        for (std::uint64_t frame = 0; frame < frame_count; ++frame) {
            output.fill(std::numeric_limits<double>::quiet_NaN());
            bank.process_frame(output);
            for (double sample : output) CHECK(sample == 0.0);
        }
        check_phases(bank, profile, initial, sample_rate, frame_count, errors);
    }
}

void test_one_second_waveforms(const RuntimeProfile& profile, Errors& errors) {
    for (double sample_rate : kSampleRates) {
        TonewheelBank bank;
        CHECK(bank.prepare(profile, sample_rate, kSeed) == Status::Ok);
        const Frame initial = phases(bank);
        const auto intervals = static_cast<std::uint64_t>(sample_rate);
        Frame output{};
        double previous = 0.0;
        std::size_t crossings = 0;
        long double first_crossing = 0.0L;
        long double last_crossing = 0.0L;
        // N+1 emitted samples provide exactly N intervals (one full second).
        for (std::uint64_t frame = 0; frame <= intervals; ++frame) {
            output.fill(std::numeric_limits<double>::quiet_NaN());
            bank.process_frame(output);
            check_bounds(output, profile);
            if (frame < 16 || frame % 251 == 0 || frame == intervals) {
                check_samples(output, profile, initial, sample_rate, frame, errors);
                check_phases(bank, profile, initial, sample_rate, frame + 1, errors);
            }
            const double current = output[45]; // Tone 46, not MIDI or terminal 46.
            if (frame > 0 && previous < 0.0 && current >= 0.0) {
                const long double fraction = -static_cast<long double>(previous) /
                    (static_cast<long double>(current) - static_cast<long double>(previous));
                const long double crossing = static_cast<long double>(frame - 1) + fraction;
                if (crossings == 0) first_crossing = crossing;
                last_crossing = crossing;
                ++crossings;
            }
            previous = current;
        }
        CHECK(crossings == 440);
        const long double frequency = static_cast<long double>(crossings - 1) * sample_rate /
                                      (last_crossing - first_crossing);
        // Linear zero interpolation has a small finite-sampling error. This
        // 0.0001 Hz allowance is numerical, not a physical tuning tolerance.
        CHECK_NEAR(frequency, 440.0L, 0.0001L);
        std::cout << "tonewheel " << sample_rate << " Hz: " << crossings
                  << " positive crossings in 1 s, estimated "
                  << std::setprecision(12) << frequency << " Hz\n";
    }
}

void test_grouped_frame_calls(const RuntimeProfile& profile) {
    const std::array<std::vector<std::size_t>, 4> groupings{{
        {1}, {32, 64, 127, 512, 1024}, {0, 7, 0, 253, 1, 0, 2053}, {65536}}};
    for (double sample_rate : kSampleRates) {
        TonewheelBank reference;
        CHECK(reference.prepare(profile, sample_rate, kSeed) == Status::Ok);
        std::vector<Frame> expected(10003);
        for (auto& frame : expected) reference.process_frame(frame);
        const Frame final_phases = phases(reference);
        for (const auto& grouping : groupings) {
            TonewheelBank bank;
            CHECK(bank.prepare(profile, sample_rate, kSeed) == Status::Ok);
            std::size_t ticks = 0;
            std::size_t group_index = 0;
            Frame actual{};
            while (ticks < expected.size()) {
                const std::size_t count = std::min(grouping[group_index], expected.size() - ticks);
                // Only loop grouping changes: the real bank API always consumes
                // one frame per call, and an empty group makes no call at all.
                for (std::size_t in_group = 0; in_group < count; ++in_group) {
                    bank.process_frame(actual);
                    CHECK(actual == expected[ticks]);
                    ++ticks;
                }
                group_index = (group_index + 1) % grouping.size();
            }
            CHECK(ticks == expected.size());
            CHECK(phases(bank) == final_phases);
        }
    }
}

void test_unprepared_and_diagnostics(const RuntimeProfile& profile) {
    TonewheelBank bank;
    CHECK(!bank.prepared());
    for (unsigned raw_id = 0; raw_id <= 255; ++raw_id) {
        double destination = -123.5;
        CHECK(!bank.phase_turns(static_cast<ToneId>(raw_id), destination));
        CHECK(destination == -123.5);
    }
    Frame output{};
    for (unsigned call = 0; call < 2; ++call) {
        output.fill(std::numeric_limits<double>::quiet_NaN());
        bank.process_frame(output);
        for (double sample : output) CHECK(sample == 0.0);
        CHECK(!bank.prepared());
    }
    const std::array<double, 8> invalid_rates{0.0, -48000.0, 32000.0, 44100.5,
        192000.0, std::numeric_limits<double>::infinity(),
        -std::numeric_limits<double>::infinity(), std::numeric_limits<double>::quiet_NaN()};
    for (double rate : invalid_rates) {
        CHECK(bank.prepare(profile, rate, kSeed) == Status::InvalidSpec);
        CHECK(!bank.prepared());
    }
    CHECK(bank.prepare(RuntimeProfile{}, 48000.0, kSeed) == Status::InvalidProfile);
    CHECK(!bank.prepared());
    output.fill(std::numeric_limits<double>::quiet_NaN());
    bank.process_frame(output);
    for (double sample : output) CHECK(sample == 0.0);

    CHECK(bank.prepare(profile, 48000.0, kSeed) == Status::Ok);
    CHECK(bank.prepared());
    const Frame before = phases(bank);
    for (unsigned raw_id = 0; raw_id <= 255; ++raw_id) {
        double destination = -123.5;
        const bool valid = raw_id >= 1 && raw_id <= 91;
        CHECK(bank.phase_turns(static_cast<ToneId>(raw_id), destination) == valid);
        CHECK(destination == (valid ? before[static_cast<std::size_t>(raw_id - 1)] : -123.5));
    }
    CHECK(phases(bank) == before); // Diagnostics themselves do not advance time.
}

void test_failed_prepare_preserves_future(const RuntimeProfile& profile) {
    TonewheelBank bank;
    TonewheelBank control;
    CHECK(bank.prepare(profile, 48000.0, kSeed) == Status::Ok);
    CHECK(control.prepare(profile, 48000.0, kSeed) == Status::Ok);
    advance_equal(bank, control, 137);

    auto rejected = [&](const RuntimeProfile& candidate, double rate, Status status) {
        const Frame before = phases(bank);
        CHECK(bank.prepare(candidate, rate, std::numeric_limits<std::uint64_t>::max()) == status);
        CHECK(bank.prepared());
        CHECK(phases(bank) == before);
        // Compare future output, not merely the flag or a visible phase snapshot.
        advance_equal(bank, control, 257);
    };
    rejected(profile, 0.0, Status::InvalidSpec);
    rejected(profile, 96001.0, Status::InvalidSpec);
    rejected(profile, std::numeric_limits<double>::quiet_NaN(), Status::InvalidSpec);
    rejected(RuntimeProfile{}, 48000.0, Status::InvalidProfile);

    auto invalid = varied_sources(profile, 48000.0);
    invalid.sources.back().frequency_hz = 0.0;
    rejected(invalid, 48000.0, Status::InvalidProfile);
    invalid.sources.back().frequency_hz = 24000.0;
    rejected(invalid, 48000.0, Status::InvalidProfile);
    invalid.sources.back().frequency_hz = std::numeric_limits<double>::infinity();
    rejected(invalid, 48000.0, Status::InvalidProfile);
    invalid.sources.back().frequency_hz = std::numeric_limits<double>::denorm_min();
    CHECK(hammond::validate_runtime_profile(invalid, 48000.0) == Status::Ok);
    // The last division underflows after 90 otherwise valid candidate sources.
    rejected(invalid, 48000.0, Status::InvalidProfile);

    invalid = profile;
    invalid.sources[45].peak_amplitude = std::numeric_limits<double>::quiet_NaN();
    rejected(invalid, 48000.0, Status::InvalidProfile);
    invalid = profile;
    invalid.sources.back().base_phase_turns = 1.0;
    rejected(invalid, 48000.0, Status::InvalidProfile);
    invalid = profile;
    invalid.output_gain = -1.0;
    rejected(invalid, 48000.0, Status::InvalidProfile);
    invalid = profile;
    invalid.manual_map.back().back() = 0;
    rejected(invalid, 48000.0, Status::InvalidProfile);
}

void test_profile_value_ownership(const RuntimeProfile& profile) {
    for (double sample_rate : kSampleRates) {
        auto caller_profile = profile;
        TonewheelBank bank;
        TonewheelBank control;
        CHECK(bank.prepare(caller_profile, sample_rate, kSeed) == Status::Ok);
        CHECK(control.prepare(profile, sample_rate, kSeed) == Status::Ok);
        caller_profile = RuntimeProfile{}; // Mutate before the first source read.
        CHECK(phases(bank) == phases(control));
        advance_equal(bank, control, 4097);
        caller_profile = varied_sources(profile, sample_rate);
        advance_equal(bank, control, 257); // Mutate again after phase advancement.
    }
}
} // namespace

int main() {
    const RuntimeProfile profile = load_test_profile();
    Errors errors;
    test_numeric_identity_and_anchors(profile);
    test_seed_known_answers(profile);
    test_seed_replay(profile);
    test_base_phases_and_current_sample(profile, errors);
    test_all_muted_sources_advance(profile, errors);
    test_one_second_waveforms(profile, errors);
    test_grouped_frame_calls(profile);
    test_unprepared_and_diagnostics(profile);
    test_failed_prepare_preserves_future(profile);
    test_profile_value_ownership(profile);
    std::cout << "tonewheel checks passed; maximum analytical sample error "
              << std::setprecision(12) << errors.sample << ", phase error "
              << errors.phase << " turns\n";
}
