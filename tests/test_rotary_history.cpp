#include "TestSupport.h"
#include "hammond/RotaryHistory.h"

#include <array>
#include <bit>
#include <cstdint>
#include <memory>

namespace hammond::rotary::detail {

// This executable's test-only definition inspects fields rather than struct
// padding. Full histories and their rejection snapshots stay on the heap.
struct RotaryRendererTestAccess {
    static bool same_double(double a, double b) {
        return std::bit_cast<std::uint64_t>(a) == std::bit_cast<std::uint64_t>(b);
    }

    static bool same_state(const MotionState& a, const MotionState& b) {
        return same_double(a.phase_rad, b.phase_rad) && a.turns == b.turns
            && same_double(a.speed_rad_s, b.speed_rad_s);
    }

    static bool same_profile(const MotionProfile& a, const MotionProfile& b) {
        return same_double(a.slow_rad_s, b.slow_rad_s)
            && same_double(a.fast_rad_s, b.fast_rad_s)
            && same_double(a.tau_up_s, b.tau_up_s)
            && same_double(a.tau_down_s, b.tau_down_s)
            && a.direction == b.direction;
    }

    static bool same_segment(const MotionSegment& a, const MotionSegment& b) {
        return a.anchor_frame == b.anchor_frame && same_state(a.initial, b.initial)
            && same_double(a.target_rad_s, b.target_rad_s)
            && same_double(a.tau_s, b.tau_s) && a.direction == b.direction;
    }

    static bool same_history(const WaveformHistory& a, const WaveformHistory& b) {
        if (!same_double(a.sample_rate_, b.sample_rate_)
            || a.capacity_frames_ != b.capacity_frames_ || a.next_frame_ != b.next_frame_
            || a.max_frame_ != b.max_frame_ || a.prepared_ != b.prepared_) return false;
        for (std::size_t i = 0; i < a.samples_.size(); ++i) {
            if (!same_double(a.samples_[i], b.samples_[i])) return false;
        }
        return true;
    }

    static bool same_history(const MotionFrameHistory& a, const MotionFrameHistory& b) {
        if (!same_profile(a.profile_, b.profile_) || !same_state(a.epoch_initial_, b.epoch_initial_)
            || !same_double(a.sample_rate_, b.sample_rate_)
            || a.capacity_frames_ != b.capacity_frames_ || a.next_frame_ != b.next_frame_
            || a.max_frame_ != b.max_frame_ || a.prepared_ != b.prepared_) return false;
        for (std::size_t i = 0; i < a.segments_.size(); ++i) {
            if (!same_segment(a.segments_[i], b.segments_[i])) return false;
        }
        return true;
    }

    static MotionSegment retained_segment(const MotionFrameHistory& history, std::uint64_t frame) {
        return history.segments_[static_cast<std::size_t>(frame % history.capacity_frames_)];
    }

    static void shorten_append_limit(WaveformHistory& history, std::uint64_t maximum) {
        history.max_frame_ = maximum;
    }

    static void shorten_append_limit(MotionFrameHistory& history, std::uint64_t maximum) {
        history.max_frame_ = maximum;
    }
};

} // namespace hammond::rotary::detail

namespace {

using namespace hammond::rotary;
using Access = detail::RotaryRendererTestAccess;
constexpr std::array<double, 4> kRates{44100.0, 48000.0, 96000.0, 192000.0};
constexpr MotionProfile kProfile{4.0, 40.0, 0.7, 1.1, 1};
constexpr MotionState kSentinel{0.875, -91, 123.25};
std::size_t rejected_calls = 0;
std::size_t retained_queries = 0;
std::size_t lifetime_events = 0;
std::size_t rate_epochs = 0;

template <typename History, typename Call>
void reject_history(History& history, Status expected, Call call) {
    const auto before = std::make_unique<History>(history);
    CHECK(call() == expected);
    CHECK(Access::same_history(history, *before));
    ++rejected_calls;
}

template <typename Call>
void reject_sample(Status expected, Call call) {
    double output = -0.0;
    CHECK(call(output) == expected);
    CHECK(Access::same_double(output, -0.0));
    ++rejected_calls;
}

template <typename Call>
void reject_state(Status expected, Call call) {
    MotionState output = kSentinel;
    CHECK(call(output) == expected);
    CHECK(Access::same_state(output, kSentinel));
    ++rejected_calls;
}

void check_state(const MotionFrameHistory& history, SamplePosition position,
                 const MotionSegment& expected_segment, double rate) {
    MotionState actual = kSentinel;
    MotionState expected = kSentinel;
    CHECK(evaluate_motion_segment_at(expected_segment, position, rate, expected) == Status::Ok);
    CHECK(history.state_at(position, actual) == Status::Ok);
    CHECK(Access::same_state(actual, expected));
    ++retained_queries;
}

double waveform_value(std::uint64_t frame) {
    return static_cast<double>(static_cast<int>(frame % 9) - 4) / 4.0;
}

void cubic_admission_aliasing_and_overshoot() {
    std::array<double, 4> signed_endpoints{-1.0, -0.0, 0.0, 1.0};
    double output = 0.75;
    CHECK(interpolate_cubic_lagrange(signed_endpoints, 0.0, output) == Status::Ok);
    CHECK(Access::same_double(output, -0.0));
    CHECK(interpolate_cubic_lagrange(signed_endpoints, 1.0, output) == Status::Ok);
    CHECK(Access::same_double(output, 0.0));
    CHECK(interpolate_cubic_lagrange({-1.0, 1.0, 1.0, -1.0}, 0.5, output) == Status::Ok);
    CHECK(output == 1.25); // The frozen cubic overshoots; no hidden clamp.

    constexpr std::array<double, 4> samples{0.25, -0.75, 0.5, -0.25};
    for (std::size_t alias = 0; alias < samples.size(); ++alias) {
        auto aliased = samples;
        CHECK(interpolate_cubic_lagrange(aliased, 0.5, aliased[alias]) == Status::Ok);
        CHECK(aliased[alias] == -0.140625); // Exact midpoint weights {-1,9,9,-1}/16.
    }
    const double infinity = std::numeric_limits<double>::infinity();
    const double nan = std::numeric_limits<double>::quiet_NaN();
    for (double fraction : {-1.0, std::nextafter(1.0, 2.0), -infinity, infinity, nan}) {
        reject_sample(Status::InvalidSpec, [&](double& out) {
            return interpolate_cubic_lagrange(samples, fraction, out);
        });
    }
    for (std::size_t node = 0; node < samples.size(); ++node) {
        for (double invalid : {-1.01, 1.01, -infinity, infinity, nan}) {
            for (double fraction : {0.0, 0.5, 1.0}) {
                auto poisoned = samples;
                poisoned[node] = invalid;
                const auto before = poisoned;
                CHECK(interpolate_cubic_lagrange(poisoned, fraction, poisoned[node])
                      == Status::InvalidBuffer);
                for (std::size_t i = 0; i < poisoned.size(); ++i) {
                    CHECK(Access::same_double(poisoned[i], before[i]));
                }
                ++rejected_calls;
            }
        }
    }
}

void waveform_storage_and_rejections() {
    const auto history = std::make_unique<WaveformHistory>();
    CHECK(!history->prepared());
    CHECK(history->sample_rate() == 0.0 && history->capacity_frames() == 0);
    CHECK(history->next_frame() == 0 && history->oldest_frame() == 0);
    reject_history(*history, Status::NotPrepared, [&] { return history->reset(); });
    reject_history(*history, Status::NotPrepared, [&] { return history->push(0.25); });
    reject_sample(Status::NotPrepared, [&](double& out) { return history->sample_at(-1, out); });
    reject_sample(Status::NotPrepared, [&](double& out) { return history->interpolate({-3, 0}, out); });

    const double infinity = std::numeric_limits<double>::infinity();
    const double nan = std::numeric_limits<double>::quiet_NaN();
    for (double rate : kRates) {
        CHECK(history->prepare(rate, 7) == Status::Ok);
        double output = 0.75;
        CHECK(history->interpolate({-3, 0.75}, output) == Status::Ok);
        CHECK(Access::same_double(output, 0.0));
        reject_sample(Status::InsufficientHistory, [&](double& out) {
            return history->interpolate({-2, 0.0}, out);
        });
        for (std::uint64_t frame = 0; frame < 24; ++frame) {
            CHECK(history->push(waveform_value(frame)) == Status::Ok);
        }
        CHECK(history->sample_rate() == rate && history->capacity_frames() == 7);
        CHECK(history->next_frame() == 24 && history->oldest_frame() == 17);
        for (std::int64_t frame = -3; frame < 24; ++frame) {
            if (frame >= 0 && frame < 17) {
                reject_sample(Status::InsufficientHistory, [&](double& out) {
                    return history->sample_at(frame, out);
                });
            } else {
                CHECK(history->sample_at(frame, output) == Status::Ok);
                CHECK(output == (frame < 0 ? 0.0 : waveform_value(static_cast<std::uint64_t>(frame))));
            }
        }
        for (std::int64_t frame = 18; frame <= 21; ++frame) {
            CHECK(history->interpolate({frame, 0.0}, output) == Status::Ok);
            CHECK(output == waveform_value(static_cast<std::uint64_t>(frame)));
        }
        for (std::int64_t frame : {17, 22, 23, 24}) {
            reject_sample(Status::InsufficientHistory, [&](double& out) {
                return history->interpolate({frame, 0.0}, out);
            });
        }

        const auto maximum = static_cast<std::int64_t>(kMaxEpochSeconds * static_cast<std::uint64_t>(rate));
        CHECK(history->sample_at(-maximum, output) == Status::Ok && output == 0.0);
        CHECK(history->interpolate({-maximum + 1, 0.5}, output) == Status::Ok && output == 0.0);
        for (std::int64_t frame : {-maximum - 1, maximum + 1,
                                  std::numeric_limits<std::int64_t>::min(),
                                  std::numeric_limits<std::int64_t>::max()}) {
            reject_sample(Status::TimelineOverflow, [&](double& out) { return history->sample_at(frame, out); });
            reject_sample(Status::TimelineOverflow, [&](double& out) { return history->interpolate({frame, 0}, out); });
        }
        for (SamplePosition position : {SamplePosition{-maximum, 0.0},
                                        SamplePosition{maximum - 1, 0.0},
                                        SamplePosition{maximum, 0.5}}) {
            reject_sample(Status::TimelineOverflow, [&](double& out) { return history->interpolate(position, out); });
        }
        reject_sample(Status::InsufficientHistory, [&](double& out) { return history->sample_at(maximum, out); });
        for (double fraction : {-0.5, 1.0, infinity, -infinity, nan}) {
            reject_sample(Status::InvalidSpec, [&](double& out) { return history->interpolate({18, fraction}, out); });
        }
        for (double sample : {-1.01, 1.01, infinity, -infinity, nan}) {
            reject_history(*history, Status::InvalidBuffer, [&] { return history->push(sample); });
        }
        for (double invalid_rate : {-1.0, 0.0, 22050.0, 47999.5, infinity, nan}) {
            reject_history(*history, Status::InvalidSpec, [&] { return history->prepare(invalid_rate, 7); });
        }
        for (std::size_t capacity : {std::size_t{0}, kMaxHistoryFrames + 1,
                                     std::numeric_limits<std::size_t>::max()}) {
            reject_history(*history, Status::InvalidSpec, [&] { return history->prepare(rate, capacity); });
        }
        const auto copy = std::make_unique<WaveformHistory>(*history);
        CHECK(Access::same_history(*history, *copy));
        CHECK(history->push(0.5) == Status::Ok);
        CHECK(copy->sample_at(17, output) == Status::Ok && output == waveform_value(17));
        reject_sample(Status::InsufficientHistory, [&](double& out) { return history->sample_at(17, out); });
        CHECK(history->reset() == Status::Ok);
        const auto fresh = std::make_unique<WaveformHistory>();
        CHECK(fresh->prepare(rate, 7) == Status::Ok);
        CHECK(Access::same_history(*history, *fresh));
    }

    CHECK(history->prepare(48000, 4) == Status::Ok);
    CHECK(history->push(-0.0) == Status::Ok);
    CHECK(history->push(0.5) == Status::Ok);
    CHECK(history->push(0.75) == Status::Ok);
    reject_sample(Status::InsufficientHistory, [&](double& out) { return history->interpolate({1, 0}, out); });
    CHECK(history->push(1.0) == Status::Ok);
    double output = 1.0;
    CHECK(history->sample_at(0, output) == Status::Ok && Access::same_double(output, -0.0));
    CHECK(history->interpolate({1, 0}, output) == Status::Ok && output == 0.5);
    CHECK(history->push(-0.25) == Status::Ok);
    reject_sample(Status::InsufficientHistory, [&](double& out) { return history->interpolate({1, 0}, out); });
    CHECK(history->interpolate({2, 0}, output) == Status::Ok && output == 0.75);
    Access::shorten_append_limit(*history, history->next_frame());
    reject_history(*history, Status::TimelineOverflow, [&] { return history->push(0.25); });

    CHECK(history->prepare(48000, 1) == Status::Ok);
    CHECK(history->push(-0.0) == Status::Ok);
    CHECK(history->interpolate({-2, 0}, output) == Status::Ok && output == 0.0);
    CHECK(history->push(1.0) == Status::Ok);
    reject_sample(Status::InsufficientHistory, [&](double& out) { return history->interpolate({-2, 0}, out); });
    CHECK(history->prepare(192000, kMaxHistoryFrames) == Status::Ok);
    for (std::uint64_t frame = 0; frame < 2 * kMaxHistoryFrames + 3; ++frame) {
        CHECK(history->push(waveform_value(frame)) == Status::Ok);
    }
    CHECK(history->oldest_frame() == kMaxHistoryFrames + 3);
    CHECK(history->sample_at(static_cast<std::int64_t>(history->oldest_frame()), output) == Status::Ok);
    CHECK(output == waveform_value(history->oldest_frame()));
}

void motion_admission_and_boundary_ownership() {
    const auto history = std::make_unique<MotionFrameHistory>();
    RotaryMotion empty;
    CHECK(!history->prepared() && history->next_frame() == 0 && history->capacity_frames() == 0);
    reject_history(*history, Status::NotPrepared, [&] { return history->prepare(empty, 5); });
    reject_history(*history, Status::NotPrepared, [&] { return history->append(empty); });
    reject_state(Status::NotPrepared, [&](MotionState& out) { return history->state_at({0, 0}, out); });

    RotaryMotion owner;
    CHECK(owner.prepare(kProfile, 0.3, 20, SpeedCommand::Chorale, 48000) == Status::Ok);
    CHECK(history->prepare(owner, 5) == Status::Ok);
    MotionState output = kSentinel;
    CHECK(history->state_at({0, 0}, output) == Status::Ok);
    CHECK(Access::same_state(output, owner.epoch_initial_state()));
    reject_state(Status::InsufficientHistory, [&](MotionState& out) {
        return history->state_at({0, std::numeric_limits<double>::denorm_min()}, out);
    });
    for (std::size_t capacity : {std::size_t{0}, kMaxHistoryFrames + 1,
                                 std::numeric_limits<std::size_t>::max()}) {
        reject_history(*history, Status::InvalidSpec, [&] { return history->prepare(owner, capacity); });
    }
    CHECK(owner.apply_command(0, SpeedCommand::Tremolo) == Status::Ok);
    CHECK(owner.apply_command(0, SpeedCommand::Chorale) == Status::Ok);
    CHECK(owner.apply_command(0, SpeedCommand::Tremolo) == Status::Ok);
    const auto first_segment = owner.segment();
    const auto observed_owner = owner;
    CHECK(history->append(owner) == Status::Ok);
    CHECK(owner == observed_owner);
    reject_history(*history, Status::InvalidEvent, [&] { return history->append(owner); });
    CHECK(owner.advance_to(1) == Status::Ok);
    check_state(*history, {1, 0}, first_segment, 48000);
    CHECK(owner.apply_command(1, SpeedCommand::Chorale) == Status::Ok);
    CHECK(owner.apply_command(1, SpeedCommand::Tremolo) == Status::Ok);
    CHECK(owner.apply_command(1, SpeedCommand::Chorale) == Status::Ok);
    const auto second_segment = owner.segment();
    check_state(*history, {1, 0}, first_segment, 48000);
    reject_state(Status::InsufficientHistory, [&](MotionState& out) { return history->state_at({1, 0.5}, out); });
    CHECK(history->append(owner) == Status::Ok);
    check_state(*history, {1, 0.5}, second_segment, 48000);
    check_state(*history, {0, 0.5}, first_segment, 48000);
    for (std::uint64_t frame = 2; frame < 81; ++frame) {
        CHECK(owner.apply_command(frame, SpeedCommand::Chorale) == Status::Ok);
        CHECK(owner.segment().anchor_frame == 1);
        CHECK(history->append(owner) == Status::Ok);
    }
    CHECK(history->oldest_frame() == 76 && history->next_frame() == 81);
    for (std::uint64_t frame = 76; frame < 81; ++frame) {
        CHECK(Access::same_segment(Access::retained_segment(*history, frame), second_segment));
        check_state(*history, {static_cast<std::int64_t>(frame), 0.375}, second_segment, 48000);
    }
    check_state(*history, {81, 0}, second_segment, 48000);
    CHECK(owner.advance_to(81) == Status::Ok);
    reject_state(Status::InsufficientHistory, [&](MotionState& out) { return history->state_at({75, 0.999}, out); });
    reject_state(Status::InsufficientHistory, [&](MotionState& out) { return history->state_at({81, 0.125}, out); });
    reject_state(Status::InsufficientHistory, [&](MotionState& out) { return history->state_at({82, 0}, out); });
    reject_history(*history, Status::InvalidEvent, [&] { return history->prepare(owner, 5); });
    reject_history(*history, Status::NotPrepared, [&] { return history->append(empty); });

    RotaryMotion mismatch;
    CHECK(mismatch.prepare(kProfile, 0.3, 20, SpeedCommand::Chorale, 44100) == Status::Ok);
    CHECK(mismatch.advance_to(81) == Status::Ok);
    reject_history(*history, Status::InvalidSpec, [&] { return history->append(mismatch); });
    auto profile = kProfile;
    profile.direction = -1;
    CHECK(mismatch.prepare(profile, 0.3, 20, SpeedCommand::Chorale, 48000) == Status::Ok);
    CHECK(mismatch.advance_to(81) == Status::Ok);
    reject_history(*history, Status::InvalidProfile, [&] { return history->append(mismatch); });
    CHECK(mismatch.prepare(kProfile, 0.31, 20, SpeedCommand::Chorale, 48000) == Status::Ok);
    CHECK(mismatch.advance_to(81) == Status::Ok);
    reject_history(*history, Status::InvalidProfile, [&] { return history->append(mismatch); });
    CHECK(mismatch.prepare(kProfile, 0.3, 21, SpeedCommand::Chorale, 48000) == Status::Ok);
    CHECK(mismatch.advance_to(81) == Status::Ok);
    reject_history(*history, Status::InvalidProfile, [&] { return history->append(mismatch); });
    CHECK(mismatch.prepare(kProfile, 0.3, 20, SpeedCommand::Chorale, 48000) == Status::Ok);
    CHECK(mismatch.advance_to(81) == Status::Ok);
    CHECK(mismatch.profile() == owner.profile() && mismatch.epoch_initial_state() == owner.epoch_initial_state());
    CHECK(mismatch.state() != owner.state()); // Same metadata, incompatible retained trajectory.
    reject_history(*history, Status::InvalidProfile, [&] { return history->append(mismatch); });
    mismatch = owner;
    CHECK(mismatch.advance_to(82) == Status::Ok);
    reject_history(*history, Status::InvalidEvent, [&] { return history->append(mismatch); });

    const auto copied = std::make_unique<MotionFrameHistory>(*history);
    CHECK(Access::same_history(*history, *copied));
    CHECK(history->append(owner) == Status::Ok);
    check_state(*copied, {76, 0.5}, second_segment, 48000);
    reject_state(Status::InsufficientHistory, [&](MotionState& out) { return history->state_at({76, 0.5}, out); });
    CHECK(owner.advance_to(82) == Status::Ok);
    Access::shorten_append_limit(*history, 82);
    reject_history(*history, Status::TimelineOverflow, [&] { return history->append(owner); });
}

void motion_rates_signs_events_and_prehistory() {
    const auto history = std::make_unique<MotionFrameHistory>();
    for (double rate : kRates) {
        for (std::int8_t direction : std::array<std::int8_t, 2>{-1, 1}) {
            auto profile = kProfile;
            profile.direction = direction;
            RotaryMotion owner;
            CHECK(owner.prepare(profile, 0.3, 20, SpeedCommand::Chorale, rate) == Status::Ok);
            CHECK(history->prepare(owner, 7) == Status::Ok);
            const auto maximum = static_cast<std::int64_t>(owner.max_frame());
            MotionState negative_before;
            CHECK(history->state_at({-3, 0.25}, negative_before) == Status::Ok);
            for (std::uint64_t frame = 0; frame < 5005; ++frame) {
                CHECK(owner.advance_to(frame) == Status::Ok);
                if (frame % 13 == 0) {
                    CHECK(owner.apply_command(frame, SpeedCommand::Tremolo) == Status::Ok);
                    CHECK(owner.apply_command(frame, SpeedCommand::Chorale) == Status::Ok);
                    lifetime_events += 2;
                }
                const auto command = frame % 2 == 0 ? SpeedCommand::Chorale : SpeedCommand::Tremolo;
                CHECK(owner.apply_command(frame, command) == Status::Ok);
                ++lifetime_events;
                const auto segment = owner.segment();
                CHECK(history->append(owner) == Status::Ok);
                CHECK(Access::same_segment(Access::retained_segment(*history, frame), segment));
                check_state(*history, {static_cast<std::int64_t>(frame), 0.25}, segment, rate);
                check_state(*history, {static_cast<std::int64_t>(frame + 1), 0.0}, segment, rate);
            }
            CHECK(history->next_frame() == 5005 && history->oldest_frame() == 4998);
            MotionState negative_after;
            CHECK(history->state_at({-3, 0.25}, negative_after) == Status::Ok);
            CHECK(Access::same_state(negative_before, negative_after));
            for (SamplePosition position : {SamplePosition{-maximum, 0.0},
                                            SamplePosition{-1, std::nextafter(1.0, 0.0)}}) {
                MotionState expected;
                MotionState actual;
                CHECK(evaluate_motion_prehistory_at(owner.epoch_initial_state(), direction,
                                                    position, rate, expected) == Status::Ok);
                CHECK(history->state_at(position, actual) == Status::Ok);
                CHECK(Access::same_state(actual, expected));
                ++retained_queries;
            }
            for (double fraction : {-0.5, 1.0, std::numeric_limits<double>::infinity(),
                                    std::numeric_limits<double>::quiet_NaN()}) {
                reject_state(Status::InvalidSpec, [&](MotionState& out) {
                    return history->state_at({4998, fraction}, out);
                });
            }
            for (SamplePosition position : {SamplePosition{-maximum - 1, 0.0},
                                            SamplePosition{maximum + 1, 0.0},
                                            SamplePosition{maximum, 0.5},
                                            SamplePosition{std::numeric_limits<std::int64_t>::min(), 0.0},
                                            SamplePosition{std::numeric_limits<std::int64_t>::max(), 0.0}}) {
                reject_state(Status::TimelineOverflow, [&](MotionState& out) { return history->state_at(position, out); });
            }
            reject_state(Status::InsufficientHistory, [&](MotionState& out) { return history->state_at({maximum, 0}, out); });
            reject_state(Status::InsufficientHistory, [&](MotionState& out) { return history->state_at({4997, 0.5}, out); });
        }
    }
}

void motion_rate_epochs_lifetime_and_capacity() {
    const auto history = std::make_unique<MotionFrameHistory>();
    for (double old_rate : kRates) {
        for (double new_rate : kRates) {
            RotaryMotion owner;
            CHECK(owner.prepare(kProfile, 0.3, 20, SpeedCommand::Chorale, old_rate) == Status::Ok);
            CHECK(owner.apply_command(0, SpeedCommand::Tremolo) == Status::Ok);
            CHECK(owner.advance_to(static_cast<std::uint64_t>(3 * old_rate)) == Status::Ok);
            const auto physical_state = owner.state();
            CHECK(physical_state.turns != 0);
            CHECK(owner.reconfigure_sample_rate(new_rate) == Status::Ok);
            CHECK(history->prepare(owner, 1) == Status::Ok);
            CHECK(history->sample_rate() == new_rate);
            CHECK(Access::same_state(history->epoch_initial_state(), physical_state));
            MotionState output;
            CHECK(history->state_at({0, 0}, output) == Status::Ok);
            CHECK(Access::same_state(output, physical_state));
            const auto segment = owner.segment();
            for (std::uint64_t frame = 0; frame < 5; ++frame) {
                CHECK(owner.advance_to(frame) == Status::Ok);
                CHECK(history->append(owner) == Status::Ok);
                check_state(*history, {static_cast<std::int64_t>(frame), 0.5}, segment, new_rate);
                check_state(*history, {static_cast<std::int64_t>(frame + 1), 0}, segment, new_rate);
            }
            CHECK(owner.reset() == Status::Ok);
            CHECK(history->prepare(owner, 1) == Status::Ok);
            CHECK(history->next_frame() == 0 && history->oldest_frame() == 0);
            CHECK(history->epoch_initial_state().turns == 0);
            const auto fresh = std::make_unique<MotionFrameHistory>();
            CHECK(fresh->prepare(owner, 1) == Status::Ok);
            CHECK(Access::same_history(*history, *fresh));
            ++rate_epochs;
        }
    }

    MotionSegment retained;
    {
        RotaryMotion temporary_owner;
        CHECK(temporary_owner.prepare(kProfile, 0.3, 20, SpeedCommand::Chorale, 48000) == Status::Ok);
        CHECK(history->prepare(temporary_owner, kMaxHistoryFrames) == Status::Ok);
        retained = temporary_owner.segment();
        for (std::uint64_t frame = 0; frame < 2 * kMaxHistoryFrames + 3; ++frame) {
            CHECK(temporary_owner.advance_to(frame) == Status::Ok);
            CHECK(history->append(temporary_owner) == Status::Ok);
        }
    }
    CHECK(history->capacity_frames() == kMaxHistoryFrames);
    CHECK(history->oldest_frame() == kMaxHistoryFrames + 3);
    check_state(*history, {static_cast<std::int64_t>(history->oldest_frame()), 0.5}, retained, 48000);
    check_state(*history, {static_cast<std::int64_t>(history->next_frame()), 0}, retained, 48000);
}

} // namespace

int main() {
    cubic_admission_aliasing_and_overshoot();
    waveform_storage_and_rejections();
    motion_admission_and_boundary_ownership();
    motion_rates_signs_events_and_prehistory();
    motion_rate_epochs_lifetime_and_capacity();
    std::cout << "rotary_history: rejected_calls=" << rejected_calls
              << " retained_queries=" << retained_queries
              << " lifetime_events=" << lifetime_events
              << " rate_epochs=" << rate_epochs
              << " waveform_bytes=" << sizeof(WaveformHistory)
              << " motion_bytes=" << sizeof(MotionFrameHistory) << '\n';
}
