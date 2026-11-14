#include "TestSupport.h"
#include "hammond/RotaryMotion.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <limits>
#include <vector>

namespace {
using namespace hammond::rotary;

constexpr std::array<double, 4> kRates{44100.0, 48000.0, 96000.0, 192000.0};
constexpr MotionProfile kProfile{4.0, 40.0, 0.7, 1.1, 1};
constexpr MotionState kSentinel{0.875, -91, 123.25};
std::size_t rejected_calls = 0;
std::size_t rate_replacements = 0;
std::size_t partition_sample_states = 0;
std::size_t partition_calls = 0;
std::size_t zero_frame_calls = 0;

bool same_state(const MotionState& a, const MotionState& b) {
    return std::bit_cast<std::uint64_t>(a.phase_rad) == std::bit_cast<std::uint64_t>(b.phase_rad)
        && a.turns == b.turns
        && std::bit_cast<std::uint64_t>(a.speed_rad_s) == std::bit_cast<std::uint64_t>(b.speed_rad_s);
}

template <typename Call>
void reject_owner(RotaryMotion& owner, Status expected, Call call) {
    const auto before = owner;
    CHECK(call() == expected);
    CHECK(owner == before);
    ++rejected_calls;
}

template <typename Call>
void reject_state(Status expected, Call call) {
    MotionState output = kSentinel;
    CHECK(call(output) == expected);
    CHECK(same_state(output, kSentinel));
    ++rejected_calls;
}

template <typename Call>
void reject_evaluation(Status expected, Call call) {
    MotionEvaluation output{kSentinel, -0.875};
    const auto before = output;
    CHECK(call(output) == expected);
    CHECK(same_state(output.state, before.state));
    CHECK(std::bit_cast<std::uint64_t>(output.angle_increment_rad)
          == std::bit_cast<std::uint64_t>(before.angle_increment_rad));
    ++rejected_calls;
}

void admission_and_rejection() {
    const double nan = std::numeric_limits<double>::quiet_NaN();
    const double infinity = std::numeric_limits<double>::infinity();
    RotaryMotion empty;
    reject_owner(empty, Status::NotPrepared, [&] { return empty.advance_to(0); });
    reject_owner(empty, Status::NotPrepared, [&] { return empty.apply_command(0, SpeedCommand::Tremolo); });
    reject_owner(empty, Status::NotPrepared, [&] { return empty.reset(); });
    reject_owner(empty, Status::NotPrepared, [&] { return empty.reconfigure_sample_rate(48000); });
    reject_state(Status::NotPrepared, [&](MotionState& out) { return empty.state_at({0, 0}, out); });

    RotaryMotion owner;
    CHECK(owner.prepare(kProfile, 0.3, 20, SpeedCommand::Chorale, 48000) == Status::Ok);
    CHECK(owner.apply_command(17, SpeedCommand::Tremolo) == Status::Ok);
    CHECK(owner.advance_to(1000) == Status::Ok);
    std::vector<MotionProfile> invalid_profiles;
    for (double value : {-1.0, 201.0, nan, infinity}) {
        auto invalid = kProfile;
        invalid.slow_rad_s = value;
        invalid_profiles.push_back(invalid);
    }
    for (double value : {-1.0, 3.0, 201.0, nan, infinity}) {
        auto invalid = kProfile;
        invalid.fast_rad_s = value;
        invalid_profiles.push_back(invalid);
    }
    for (double value : {0.0, 0.000999, 60.001, nan, infinity}) {
        auto invalid = kProfile;
        invalid.tau_up_s = value;
        invalid_profiles.push_back(invalid);
        invalid = kProfile;
        invalid.tau_down_s = value;
        invalid_profiles.push_back(invalid);
    }
    for (std::int8_t value : std::array<std::int8_t, 4>{-2, 0, 2, 127}) {
        auto invalid = kProfile;
        invalid.direction = value;
        invalid_profiles.push_back(invalid);
    }
    for (const auto profile : invalid_profiles) {
        CHECK(validate_motion_profile(profile) == Status::InvalidProfile);
        reject_owner(owner, Status::InvalidProfile, [&] {
            return owner.prepare(profile, 0.3, 20, SpeedCommand::Chorale, 48000);
        });
        auto output = owner.segment();
        const auto before = output;
        CHECK(make_motion_segment(profile, kSentinel, SpeedCommand::Chorale, 0, output)
              == Status::InvalidProfile);
        CHECK(output == before);
        ++rejected_calls;
    }
    for (double rate : {0.0, -48000.0, 22050.0, 48000.5, nan, infinity}) {
        reject_owner(owner, Status::InvalidSpec, [&] { return owner.reconfigure_sample_rate(rate); });
        reject_owner(owner, Status::InvalidSpec, [&] {
            return owner.prepare(kProfile, 0.3, 20, SpeedCommand::Chorale, rate);
        });
        reject_state(Status::InvalidSpec, [&](MotionState& out) {
            return evaluate_motion_segment_at(owner.segment(), {1000, 0}, rate, out);
        });
        reject_state(Status::InvalidSpec, [&](MotionState& out) {
            return evaluate_motion_prehistory_at(kSentinel, 1, {-1, 0.5}, rate, out);
        });
    }
    for (double phase : {-1.0, kTwoPi, nan, infinity}) {
        const MotionState invalid{phase, 0, 20};
        CHECK(validate_motion_state(invalid) == Status::InvalidProfile);
        reject_owner(owner, Status::InvalidProfile, [&] {
            return owner.prepare(kProfile, phase, 20, SpeedCommand::Chorale, 48000);
        });
        reject_evaluation(Status::InvalidProfile, [&](MotionEvaluation& out) {
            return evaluate_motion_prehistory(invalid, 1, -1, out);
        });
    }
    for (double speed : {-1.0, 201.0, nan, infinity}) {
        reject_owner(owner, Status::InvalidProfile, [&] {
            return owner.prepare(kProfile, 0.3, speed, SpeedCommand::Chorale, 48000);
        });
        auto invalid = owner.segment();
        invalid.initial.speed_rad_s = speed;
        reject_evaluation(Status::InvalidProfile, [&](MotionEvaluation& out) {
            return evaluate_motion_segment(invalid, 1, out);
        });
        invalid = owner.segment();
        invalid.target_rad_s = speed;
        reject_evaluation(Status::InvalidProfile, [&](MotionEvaluation& out) {
            return evaluate_motion_segment(invalid, 1, out);
        });
    }
    for (double elapsed : {-1.0, 86401.0, nan, infinity}) {
        reject_evaluation(Status::InvalidSpec, [&](MotionEvaluation& out) {
            return evaluate_motion_segment(owner.segment(), elapsed, out);
        });
    }
    for (double elapsed : {1.0, -86401.0, nan, -infinity}) {
        reject_evaluation(Status::InvalidSpec, [&](MotionEvaluation& out) {
            return evaluate_motion_prehistory(kSentinel, -1, elapsed, out);
        });
    }
    for (double tau : {0.0, 0.000999, 60.001, nan, infinity}) {
        auto invalid = owner.segment();
        invalid.tau_s = tau;
        reject_evaluation(Status::InvalidProfile, [&](MotionEvaluation& out) {
            return evaluate_motion_segment(invalid, 1, out);
        });
    }
    for (std::int8_t sign : std::array<std::int8_t, 3>{-2, 0, 2}) {
        auto invalid = owner.segment();
        invalid.direction = sign;
        reject_evaluation(Status::InvalidProfile, [&](MotionEvaluation& out) {
            return evaluate_motion_segment(invalid, 1, out);
        });
        reject_evaluation(Status::InvalidProfile, [&](MotionEvaluation& out) {
            return evaluate_motion_prehistory(kSentinel, sign, -1, out);
        });
    }
    {
        auto output = owner.segment();
        const auto before = output;
        CHECK(make_motion_segment(kProfile, kSentinel, static_cast<SpeedCommand>(255), 0, output)
              == Status::InvalidEvent);
        CHECK(output == before);
        ++rejected_calls;
        CHECK(make_motion_segment(kProfile, kSentinel, SpeedCommand::Chorale,
                                  86400ULL * 192000ULL + 1, output) == Status::TimelineOverflow);
        CHECK(output == before);
        ++rejected_calls;
    }
    for (double fraction : {-1.0, 1.0, nan, infinity}) {
        reject_state(Status::InvalidSpec, [&](MotionState& out) { return owner.state_at({1000, fraction}, out); });
        reject_state(Status::InvalidSpec, [&](MotionState& out) { return owner.state_at({-1, fraction}, out); });
    }
    const auto maximum = static_cast<std::int64_t>(owner.max_frame());
    for (const auto position : std::array<SamplePosition, 4>{
             SamplePosition{maximum + 1, 0}, {maximum, 0.5}, {-maximum - 1, 0},
             {std::numeric_limits<std::int64_t>::min(), 0}}) {
        reject_state(Status::TimelineOverflow, [&](MotionState& out) { return owner.state_at(position, out); });
    }
    reject_state(Status::InsufficientHistory, [&](MotionState& out) { return owner.state_at({16, 0.75}, out); });
    reject_state(Status::InsufficientHistory, [&](MotionState& out) {
        return evaluate_motion_segment_at(owner.segment(), {-1, 0.5}, 48000, out);
    });
    reject_state(Status::InvalidSpec, [&](MotionState& out) {
        return evaluate_motion_prehistory_at(kSentinel, 1, {0, 0.5}, 48000, out);
    });
    reject_state(Status::InvalidSpec, [&](MotionState& out) {
        return evaluate_motion_prehistory_at(kSentinel, 1, {1, 0}, 48000, out);
    });
    reject_owner(owner, Status::InvalidEvent, [&] { return owner.advance_to(999); });
    reject_owner(owner, Status::InvalidEvent, [&] { return owner.apply_command(999, SpeedCommand::Chorale); });
    reject_owner(owner, Status::InvalidEvent, [&] { return owner.apply_command(1000, static_cast<SpeedCommand>(255)); });
    reject_owner(owner, Status::InvalidEvent, [&] {
        return owner.prepare(kProfile, 0.3, 20, static_cast<SpeedCommand>(255), 48000);
    });
    reject_owner(owner, Status::TimelineOverflow, [&] { return owner.advance_to(owner.max_frame() + 1); });
    reject_owner(owner, Status::TimelineOverflow, [&] {
        return owner.apply_command(owner.max_frame() + 1, SpeedCommand::Chorale);
    });
    auto invalid = owner.segment();
    invalid.anchor_frame = 86400ULL * 192000ULL + 1;
    reject_evaluation(Status::TimelineOverflow, [&](MotionEvaluation& out) {
        return evaluate_motion_segment(invalid, 0, out);
    });
    invalid.anchor_frame = owner.max_frame() + 1;
    reject_state(Status::TimelineOverflow, [&](MotionState& out) {
        return evaluate_motion_segment_at(invalid, {1000, 0}, 48000, out);
    });
    for (int sign : {-1, 1}) {
        const auto turns = sign == 1 ? std::numeric_limits<std::int64_t>::max()
                                    : std::numeric_limits<std::int64_t>::min();
        MotionSegment overflow{0, {0.5, turns, 200}, 200, 1, static_cast<std::int8_t>(sign)};
        reject_evaluation(Status::TimelineOverflow, [&](MotionEvaluation& out) {
            return evaluate_motion_segment(overflow, 1, out);
        });
        MotionEvaluation zero;
        CHECK(evaluate_motion_segment(overflow, 0, zero) == Status::Ok);
        CHECK(same_state(zero.state, overflow.initial));
        CHECK(zero.angle_increment_rad == 0.0);
    }
}

void lifecycle() {
    for (const double old_rate : kRates) {
        for (const double new_rate : kRates) {
            for (const std::int8_t sign : std::array<std::int8_t, 2>{-1, 1}) {
                auto profile = kProfile;
                profile.direction = sign;
                RotaryMotion owner;
                CHECK(owner.prepare(profile, 0.3, 20, SpeedCommand::Chorale, old_rate) == Status::Ok);
                const auto original = owner.state();
                CHECK(owner.segment().tau_s == profile.tau_down_s);
                const auto before_query = owner;
                MotionState prediction;
                const auto event_frame = static_cast<std::uint64_t>(old_rate);
                CHECK(owner.state_at({static_cast<std::int64_t>(event_frame), 0}, prediction) == Status::Ok);
                CHECK(owner == before_query);
                CHECK(owner.advance_to(event_frame) == Status::Ok);
                CHECK(same_state(prediction, owner.state()));
                const auto at_event = owner.state();
                CHECK(owner.apply_command(event_frame, SpeedCommand::Tremolo) == Status::Ok);
                CHECK(same_state(owner.state(), at_event));
                CHECK(owner.segment().tau_s == profile.tau_up_s);
                CHECK(owner.apply_command(event_frame, SpeedCommand::Chorale) == Status::Ok);
                CHECK(same_state(owner.state(), at_event));
                CHECK(owner.apply_command(event_frame, SpeedCommand::Tremolo) == Status::Ok);
                const auto anchor = owner.segment();
                CHECK(owner.apply_command(event_frame + 1, SpeedCommand::Tremolo) == Status::Ok);
                CHECK(owner.segment() == anchor);
                MotionState negative, expected_negative;
                CHECK(owner.state_at({-1, 0.75}, negative) == Status::Ok);
                CHECK(evaluate_motion_prehistory_at(original, sign, {-1, 0.75}, old_rate,
                                                    expected_negative) == Status::Ok);
                CHECK(same_state(negative, expected_negative));
                const auto current = owner.state();
                const auto current_command = owner.command();
                CHECK(owner.reconfigure_sample_rate(new_rate) == Status::Ok);
                ++rate_replacements;
                CHECK(owner.frame() == 0);
                CHECK(owner.max_frame() == 86400ULL * static_cast<std::uint64_t>(new_rate));
                CHECK(owner.sample_rate() == new_rate);
                CHECK(owner.profile() == profile);
                CHECK(owner.command() == current_command);
                CHECK(same_state(owner.state(), current));
                CHECK(same_state(owner.epoch_initial_state(), current));
                CHECK(same_state(owner.segment().initial, current));
                CHECK(owner.segment().anchor_frame == 0);
                CHECK(owner.state_at({-1, 0.75}, negative) == Status::Ok);
                CHECK(evaluate_motion_prehistory_at(current, sign, {-1, 0.75}, new_rate,
                                                    expected_negative) == Status::Ok);
                CHECK(same_state(negative, expected_negative));
                CHECK(owner.advance_to(static_cast<std::uint64_t>(new_rate)) == Status::Ok);
                CHECK(owner.reset() == Status::Ok);
                CHECK(owner.sample_rate() == new_rate);
                CHECK(owner.frame() == 0);
                CHECK(owner.command() == SpeedCommand::Chorale);
                CHECK(same_state(owner.state(), original));
                CHECK(same_state(owner.epoch_initial_state(), original));
                CHECK(owner.advance_to(owner.max_frame()) == Status::Ok);
                reject_owner(owner, Status::TimelineOverflow, [&] { return owner.advance_to(owner.max_frame() + 1); });
            }
        }
    }
    // A command name alone does not select the direction of acceleration.
    RotaryMotion below_slow;
    CHECK(below_slow.prepare(kProfile, 0, 0, SpeedCommand::Tremolo, 48000) == Status::Ok);
    CHECK(below_slow.apply_command(0, SpeedCommand::Chorale) == Status::Ok);
    CHECK(below_slow.segment().tau_s == kProfile.tau_up_s);
    RotaryMotion above_fast;
    CHECK(above_fast.prepare(kProfile, 0, 200, SpeedCommand::Chorale, 48000) == Status::Ok);
    CHECK(above_fast.apply_command(0, SpeedCommand::Tremolo) == Status::Ok);
    CHECK(above_fast.segment().tau_s == kProfile.tau_down_s);
}

struct Event { std::uint64_t frame; SpeedCommand command; };
struct PartitionResult { std::vector<MotionState> samples; RotaryMotion owner; };

PartitionResult run_partition(double rate, std::int8_t sign,
                              const std::vector<std::uint64_t>& pattern, bool defer_ties) {
    constexpr auto slow = SpeedCommand::Chorale;
    constexpr auto fast = SpeedCommand::Tremolo;
    constexpr std::array<Event, 16> events{{
        {0, fast}, {0, slow}, {0, fast}, {1, slow}, {17, fast}, {17, slow},
        {128, fast}, {129, fast}, {1024, slow}, {1024, fast}, {2048, slow},
        {4096, fast}, {4096, slow}, {8192, fast}, {8192, slow}, {8192, slow}}};
    constexpr std::uint64_t frames = 8192;
    auto profile = kProfile;
    profile.direction = sign;
    PartitionResult result;
    CHECK(result.owner.prepare(profile, 0.3, 20, slow, rate) == Status::Ok);
    result.samples.reserve(frames + 1);
    std::size_t event = 0;
    auto apply = [&](std::uint64_t frame, bool one) {
        while (event < events.size() && events[event].frame == frame) {
            CHECK(result.owner.apply_command(frame, events[event].command) == Status::Ok);
            ++event;
            if (one) break;
        }
    };
    std::uint64_t frame = 0;
    std::size_t block = 0;
    while (frame < frames) {
        const auto count = std::min(pattern[block++ % pattern.size()], frames - frame);
        if (count == 0) {
            apply(frame, false);
            ++zero_frame_calls;
            continue;
        }
        for (std::uint64_t offset = 0; offset < count; ++offset) {
            apply(frame + offset, false);
            CHECK(result.owner.advance_to(frame + offset) == Status::Ok);
            result.samples.push_back(result.owner.state());
        }
        frame += count;
        // Splitting tied commands between offset-N and the next offset-zero
        // call preserves their order and leaves the next sample identical.
        apply(frame, defer_ties);
        CHECK(result.owner.advance_to(frame) == Status::Ok);
        ++partition_calls;
    }
    apply(frames, false);
    CHECK(event == events.size());
    result.samples.push_back(result.owner.state());
    return result;
}

void exact_partition_identity() {
    const std::array<std::vector<std::uint64_t>, 5> patterns{{
        {1}, {17, 31, 64, 3, 511}, {1024}, {4096}, {0, 128, 0, 511, 1, 0, 4096}}};
    for (const double rate : kRates) {
        for (const std::int8_t sign : std::array<std::int8_t, 2>{-1, 1}) {
            const auto baseline = run_partition(rate, sign, {1}, false);
            for (const auto& pattern : patterns) {
                const auto candidate = run_partition(rate, sign, pattern, true);
                CHECK(candidate.samples.size() == baseline.samples.size());
                for (std::size_t i = 0; i < candidate.samples.size(); ++i) {
                    CHECK(same_state(candidate.samples[i], baseline.samples[i]));
                    ++partition_sample_states;
                }
                CHECK(candidate.owner == baseline.owner);
            }
        }
    }
}
} // namespace

int main() {
    admission_and_rejection();
    lifecycle();
    exact_partition_identity();
    std::cout << "{\"status\":\"pass\",\"gate\":\"R2 owner lifecycle and partition identity\","
              << "\"rejected_calls\":" << rejected_calls
              << ",\"rate_replacements\":" << rate_replacements
              << ",\"partition_sample_states\":" << partition_sample_states
              << ",\"partition_calls\":" << partition_calls
              << ",\"zero_frame_calls\":" << zero_frame_calls
              << ",\"physical_status\":\"unmeasured\"}\n";
}
