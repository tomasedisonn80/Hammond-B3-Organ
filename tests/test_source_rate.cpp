#include "TestSupport.h"
#include "hammond/TonewheelBank.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <cstdint>
#include <limits>
#include <numbers>

namespace {
using hammond::RuntimeProfile;
using hammond::Status;
using hammond::ToneId;
using hammond::TonewheelBank;
using Frame = std::array<double, hammond::kToneSourceCount>;

constexpr std::array<double, 3> kRates{44100.0, 48000.0, 96000.0};
constexpr std::uint64_t kSeed = 0x3571acf04b682de9ULL;
constexpr long double kTwoPi = 2.0L * std::numbers::pi_v<long double>;

struct Observations {
    std::size_t transitions{0};
    std::size_t rejections{0};
    std::size_t phase_oracles{0};
    std::size_t sample_oracles{0};
    std::size_t exact_frames{0};
    long double maximum_phase_error{0.0L};
    long double maximum_sample_error{0.0L};
};

ToneId tone_id(std::size_t index) {
    CHECK(index < hammond::kToneSourceCount);
    return static_cast<ToneId>(index + 1);
}

Frame phases(const TonewheelBank& bank) {
    Frame result{};
    for (std::size_t i = 0; i < result.size(); ++i) {
        CHECK(bank.phase_turns(tone_id(i), result[i]));
        CHECK(std::isfinite(result[i]) && result[i] >= 0.0 && result[i] < 1.0);
    }
    return result;
}

void same_bits(const Frame& actual, const Frame& expected) {
    for (std::size_t i = 0; i < actual.size(); ++i) {
        CHECK(std::bit_cast<std::uint64_t>(actual[i]) ==
              std::bit_cast<std::uint64_t>(expected[i]));
    }
}

void advance(TonewheelBank& bank, std::uint32_t frames) {
    Frame discarded{};
    for (std::uint32_t i = 0; i < frames; ++i) {
        bank.process_frame(discarded);
    }
}

void same_future(TonewheelBank& actual, TonewheelBank& control,
                 std::uint32_t frames, Observations& observed) {
    Frame a{}, b{};
    CHECK(actual.prepared() == control.prepared());
    CHECK(actual.sample_rate() == control.sample_rate());
    same_bits(phases(actual), phases(control));
    for (std::uint32_t i = 0; i < frames; ++i) {
        actual.process_frame(a);
        control.process_frame(b);
        same_bits(a, b);
        ++observed.exact_frames;
    }
    same_bits(phases(actual), phases(control));
}

void rejected(const TonewheelBank& initial, double rate, Status status,
              Observations& observed) {
    TonewheelBank actual = initial;
    TonewheelBank control = initial;
    const Frame before = phases(actual);
    CHECK(actual.reconfigure_sample_rate(rate) == status);
    CHECK(actual.sample_rate() == initial.sample_rate());
    same_bits(phases(actual), before);
    same_future(actual, control, 513, observed);
    ++observed.rejections;
}

long double wrapped(long double turns) {
    return turns - std::floor(turns);
}

long double circular_distance(long double a, long double b) {
    const long double d = std::fabs(a - b);
    return std::min(d, 1.0L - d);
}

long double phase_allowance(std::uint64_t frames, long double cycles,
                            std::size_t segments) {
    // Bounded binary64 accumulation plus the elapsed-time oracle's arithmetic.
    // This remains conservative when long double has only binary64 precision.
    // It is deliberately unrelated to the production per-frame recurrence.
    return 8.0L * std::numeric_limits<double>::epsilon() *
               (static_cast<long double>(frames) + 1.0L) +
           16.0L * std::numeric_limits<long double>::epsilon() *
               (std::fabs(cycles) + 1.0L) * static_cast<long double>(segments + 1);
}

void phase_oracle(const TonewheelBank& bank, const RuntimeProfile& profile,
                  const Frame& initial, long double seconds, std::uint64_t frames,
                  std::size_t segments, Observations& observed) {
    const Frame actual = phases(bank);
    for (std::size_t i = 0; i < actual.size(); ++i) {
        const long double cycles =
            static_cast<long double>(profile.sources[i].frequency_hz) * seconds;
        const long double expected = wrapped(static_cast<long double>(initial[i]) + cycles);
        const long double error = circular_distance(actual[i], expected);
        CHECK_NEAR(error, 0.0L, phase_allowance(frames, cycles, segments));
        observed.maximum_phase_error = std::max(observed.maximum_phase_error, error);
        ++observed.phase_oracles;
    }
}

void sample_oracle(const Frame& actual, const RuntimeProfile& profile,
                   const Frame& initial, long double seconds, std::uint64_t frames,
                   std::size_t segments, Observations& observed) {
    for (std::size_t i = 0; i < actual.size(); ++i) {
        const long double cycles =
            static_cast<long double>(profile.sources[i].frequency_hz) * seconds;
        const long double phase = wrapped(static_cast<long double>(initial[i]) + cycles);
        const long double amplitude = profile.sources[i].peak_amplitude;
        const long double expected = amplitude * std::sin(kTwoPi * phase);
        const long double tolerance = amplitude *
            (kTwoPi * phase_allowance(frames, cycles, segments) +
             16.0L * std::numeric_limits<double>::epsilon());
        CHECK(std::isfinite(actual[i]));
        CHECK_NEAR(actual[i], expected, tolerance);
        observed.maximum_sample_error = std::max(observed.maximum_sample_error,
            std::fabs(static_cast<long double>(actual[i]) - expected));
        ++observed.sample_oracles;
    }
}

RuntimeProfile varied_profile(const RuntimeProfile& nominal) {
    auto result = nominal;
    for (std::size_t i = 0; i < result.sources.size(); ++i) {
        // Synthetic, separately owned amplitudes/phases; no PRNG is reproduced.
        result.sources[i].peak_amplitude = i % 7 == 0 ? 0.0 :
            static_cast<double>((i % 16) + 1) / 16.0;
        result.sources[i].base_phase_turns = static_cast<double>(i % 13) / 16.0;
    }
    return result;
}

void test_unprepared_and_prepare_rate(const RuntimeProfile& profile,
                                     Observations& observed) {
    TonewheelBank bank;
    CHECK(!bank.prepared());
    CHECK(bank.sample_rate() == 0.0);
    constexpr std::array<double, 8> values{0.0, -0.0, -48000.0, 44100.0,
                                         48000.0, 96000.0, 192000.0, 1.0};
    for (const double rate : values) {
        CHECK(bank.reconfigure_sample_rate(rate) == Status::NotPrepared);
        CHECK(!bank.prepared() && bank.sample_rate() == 0.0);
        ++observed.rejections;
    }
    for (const double rate : {std::numeric_limits<double>::quiet_NaN(),
                             std::numeric_limits<double>::infinity(),
                             -std::numeric_limits<double>::infinity()}) {
        CHECK(bank.reconfigure_sample_rate(rate) == Status::NotPrepared);
        CHECK(!bank.prepared() && bank.sample_rate() == 0.0);
        ++observed.rejections;
    }
    double sentinel = 27.0;
    CHECK(!bank.phase_turns(46, sentinel));
    CHECK(sentinel == 27.0);
    Frame output{};
    output.fill(19.0);
    bank.process_frame(output);
    CHECK(output == Frame{});

    CHECK(bank.prepare(profile, 22050.0, kSeed) == Status::InvalidSpec);
    CHECK(!bank.prepared() && bank.sample_rate() == 0.0);
    for (const double rate : kRates) {
        CHECK(bank.prepare(profile, rate, kSeed) == Status::Ok);
        CHECK(bank.prepared() && bank.sample_rate() == rate);
        advance(bank, 333);
        TonewheelBank control = bank;
        auto invalid = profile;
        invalid.sources.back().peak_amplitude = -1.0;
        CHECK(bank.prepare(invalid, 96000.0, kSeed + 1) == Status::InvalidProfile);
        CHECK(bank.sample_rate() == rate);
        same_future(bank, control, 129, observed);
        CHECK(bank.prepare(profile, -rate, kSeed + 1) == Status::InvalidSpec);
        CHECK(bank.sample_rate() == rate);
        same_future(bank, control, 129, observed);
    }
}

void test_every_rate_pair(const RuntimeProfile& profile, Observations& observed) {
    constexpr std::array<std::uint32_t, 9> checkpoints{0, 1, 2, 3, 8, 127, 512, 1024, 2048};
    for (const double old_rate : kRates) {
        for (const double new_rate : kRates) {
            TonewheelBank bank;
            CHECK(bank.prepare(profile, old_rate, kSeed) == Status::Ok);
            advance(bank, 257);
            const Frame initial = phases(bank);
            TonewheelBank old_rate_control = bank;
            CHECK(bank.reconfigure_sample_rate(new_rate) == Status::Ok);
            ++observed.transitions;
            CHECK(bank.sample_rate() == new_rate);
            same_bits(phases(bank), initial);
            Frame old_first{};
            old_rate_control.process_frame(old_first);
            Frame output{};
            for (std::uint32_t frame = 0; frame <= checkpoints.back(); ++frame) {
                const bool inspect = std::find(checkpoints.begin(), checkpoints.end(), frame) !=
                                     checkpoints.end();
                const long double seconds = static_cast<long double>(frame) / new_rate;
                if (inspect) phase_oracle(bank, profile, initial, seconds, frame, 1, observed);
                bank.process_frame(output);
                if (frame == 0) same_bits(output, old_first);
                if (inspect) sample_oracle(output, profile, initial, seconds, frame, 1, observed);
            }
        }
    }
}

void test_same_rate_is_exact_noop(const RuntimeProfile& profile, Observations& observed) {
    for (const double rate : kRates) {
        TonewheelBank bank;
        CHECK(bank.prepare(profile, rate, kSeed) == Status::Ok);
        advance(bank, 179);
        TonewheelBank control = bank;
        Frame a{}, b{};
        for (std::uint32_t frame = 0; frame < 8192; ++frame) {
            CHECK(bank.reconfigure_sample_rate(rate) == Status::Ok);
            bank.process_frame(a);
            control.process_frame(b);
            same_bits(a, b);
            ++observed.exact_frames;
        }
        same_bits(phases(bank), phases(control));
        CHECK(bank.sample_rate() == rate);
    }
}

void test_invalid_rates(const RuntimeProfile& profile, Observations& observed) {
    const std::array<double, 17> invalid{
        0.0, -0.0, -44100.0, -48000.0, -96000.0, 1.0, 22050.0, 88200.0, 192000.0,
        std::numeric_limits<double>::denorm_min(), std::numeric_limits<double>::max(),
        std::numeric_limits<double>::quiet_NaN(), std::numeric_limits<double>::infinity(),
        -std::numeric_limits<double>::infinity(), std::nextafter(44100.0, 0.0),
        std::nextafter(48000.0, 96000.0), std::nextafter(96000.0, 0.0)};
    for (const double rate : kRates) {
        TonewheelBank bank;
        CHECK(bank.prepare(profile, rate, kSeed) == Status::Ok);
        advance(bank, 751);
        for (const double value : invalid) rejected(bank, value, Status::InvalidSpec, observed);
    }
}

void test_increment_admission(const RuntimeProfile& nominal, Observations& observed) {
    for (const std::size_t index : {std::size_t{0}, std::size_t{45}, std::size_t{90}}) {
        auto high = nominal;
        high.sources[index].frequency_hz = 30000.0;
        high.sources[index].peak_amplitude = 0.0; // Muting cannot bypass admission.
        TonewheelBank bank;
        CHECK(bank.prepare(high, 96000.0, kSeed) == Status::Ok);
        advance(bank, 231);
        rejected(bank, 44100.0, Status::InvalidProfile, observed);
        rejected(bank, 48000.0, Status::InvalidProfile, observed);

        auto tiny = nominal;
        tiny.sources[index].frequency_hz = 44100.0 * 0x1p-53;
        tiny.sources[index].peak_amplitude = 0.0;
        CHECK(bank.prepare(tiny, 44100.0, kSeed) == Status::Ok);
        advance(bank, 97);
        rejected(bank, 48000.0, Status::InvalidProfile, observed);
        rejected(bank, 96000.0, Status::InvalidProfile, observed);

        for (const double target : kRates) {
            auto boundary = nominal;
            boundary.sources[index].frequency_hz = target * 0x1p-53;
            boundary.sources[index].peak_amplitude = 0.0;
            CHECK(bank.prepare(boundary, 44100.0, kSeed) == Status::Ok);
            advance(bank, 31);
            const Frame before = phases(bank);
            CHECK(bank.reconfigure_sample_rate(target) == Status::Ok);
            CHECK(bank.sample_rate() == target);
            same_bits(phases(bank), before);
            Frame frame{};
            bank.process_frame(frame);
            CHECK(phases(bank)[index] != before[index]);
            CHECK(frame[index] == 0.0);
            ++observed.transitions;
        }
        for (const double target : {44100.0, 48000.0}) {
            auto boundary = nominal;
            boundary.sources[index].frequency_hz = target * 0.5;
            CHECK(bank.prepare(boundary, 96000.0, kSeed) == Status::Ok);
            advance(bank, 13);
            rejected(bank, target, Status::InvalidProfile, observed);
            boundary.sources[index].frequency_hz =
                std::nextafter(boundary.sources[index].frequency_hz, 0.0);
            CHECK(bank.prepare(boundary, 96000.0, kSeed) == Status::Ok);
            advance(bank, 13);
            const Frame before = phases(bank);
            CHECK(bank.reconfigure_sample_rate(target) == Status::Ok);
            same_bits(phases(bank), before);
            ++observed.transitions;
        }
    }
}

void test_mixed_rate_time_and_owned_profile(const RuntimeProfile& profile,
                                           Observations& observed) {
    struct Segment { double rate; std::uint32_t frames; };
    constexpr std::array<Segment, 9> schedule{{
        {96000.0, 257}, {44100.0, 1021}, {48000.0, 17},
        {48000.0, 4093}, {96000.0, 2047}, {44100.0, 37},
        {48000.0, 521}, {44100.0, 4093}, {96000.0, 1031}}};
    auto caller_profile = profile;
    TonewheelBank bank;
    CHECK(bank.prepare(caller_profile, 48000.0, kSeed) == Status::Ok);
    advance(bank, 281);
    const Frame initial = phases(bank);
    caller_profile = RuntimeProfile{};
    long double seconds = 0.0L;
    std::uint64_t elapsed_frames = 0;
    std::size_t segments = 0;
    Frame output{};
    for (const Segment& segment : schedule) {
        const Frame before = phases(bank);
        CHECK(bank.reconfigure_sample_rate(segment.rate) == Status::Ok);
        CHECK(bank.sample_rate() == segment.rate);
        same_bits(phases(bank), before);
        ++observed.transitions;
        ++segments;
        // Source generation continues even when the caller discards its samples.
        advance(bank, segment.frames);
        elapsed_frames += segment.frames;
        seconds += static_cast<long double>(segment.frames) / segment.rate;
        phase_oracle(bank, profile, initial, seconds, elapsed_frames, segments, observed);
        // One deliberately observed frame after each discarded interval.
        bank.process_frame(output);
        sample_oracle(output, profile, initial, seconds, elapsed_frames, segments, observed);
        ++elapsed_frames;
        seconds += 1.0L / segment.rate;
    }
    // Successful full prepare still resets the seeded field; migration never
    // became an implicit substitute for that explicit lifecycle operation.
    TonewheelBank fresh;
    CHECK(bank.prepare(profile, 44100.0, kSeed) == Status::Ok);
    CHECK(fresh.prepare(profile, 44100.0, kSeed) == Status::Ok);
    same_future(bank, fresh, 1025, observed);
}
} // namespace

int main() {
    const RuntimeProfile nominal = load_test_profile();
    const RuntimeProfile varied = varied_profile(nominal);
    Observations observed;
    test_unprepared_and_prepare_rate(nominal, observed);
    test_every_rate_pair(nominal, observed);
    test_every_rate_pair(varied, observed);
    test_same_rate_is_exact_noop(varied, observed);
    test_invalid_rates(varied, observed);
    test_increment_admission(nominal, observed);
    test_mixed_rate_time_and_owned_profile(varied, observed);
    std::cout << "source rate checks passed; transitions=" << observed.transitions
              << "; rejected=" << observed.rejections
              << "; phase oracles=" << observed.phase_oracles
              << "; sample oracles=" << observed.sample_oracles
              << "; exact future frames=" << observed.exact_frames
              << std::setprecision(14)
              << "; maximum phase error=" << observed.maximum_phase_error
              << " turns; maximum sample error=" << observed.maximum_sample_error << '\n';
}
