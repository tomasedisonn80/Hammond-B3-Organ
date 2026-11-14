#include "hammond/RotaryHistory.h"

#include <cmath>

namespace hammond::rotary {
namespace {

[[nodiscard]] bool valid_capacity(std::size_t capacity) noexcept {
    return capacity != 0 && capacity <= kMaxHistoryFrames;
}

[[nodiscard]] std::uint64_t epoch_frames(double sample_rate) noexcept {
    // All callers first admit one of the four exact, integral sample rates.
    return kMaxEpochSeconds * static_cast<std::uint64_t>(sample_rate);
}

[[nodiscard]] std::size_t slot_for(std::uint64_t frame, std::size_t capacity) noexcept {
    // Prepared capacities are positive and no larger than kMaxHistoryFrames.
    return static_cast<std::size_t>(frame % static_cast<std::uint64_t>(capacity));
}

[[nodiscard]] Status valid_position(SamplePosition position,
                                    std::uint64_t max_frame) noexcept {
    if (!std::isfinite(position.fraction)
        || position.fraction < 0.0 || position.fraction >= 1.0) {
        return Status::InvalidSpec;
    }
    const auto maximum = static_cast<std::int64_t>(max_frame);
    if (position.frame < -maximum || position.frame > maximum
        || (position.frame == maximum && position.fraction != 0.0)) {
        return Status::TimelineOverflow;
    }
    return Status::Ok;
}

} // namespace

Status interpolate_cubic_lagrange(const std::array<double, 4>& samples,
                                  double fraction, double& destination) noexcept {
    if (!std::isfinite(fraction) || fraction < 0.0 || fraction > 1.0) {
        return Status::InvalidSpec;
    }
    for (const double sample : samples) {
        if (!std::isfinite(sample)
            || sample < -kMaxInputMagnitude || sample > kMaxInputMagnitude) {
            return Status::InvalidBuffer;
        }
    }

    // Admit every support value even at an endpoint, then preserve the exact
    // selected sample (including signed zero). All reads precede publication.
    if (fraction == 0.0) {
        destination = samples[1];
        return Status::Ok;
    }
    if (fraction == 1.0) {
        destination = samples[2];
        return Status::Ok;
    }
    const double before = fraction - 1.0;
    const double after = fraction - 2.0;
    const double first = -fraction * before * after / 6.0;
    const double second = (fraction + 1.0) * before * after / 2.0;
    const double third = -(fraction + 1.0) * fraction * after / 2.0;
    const double fourth = (fraction + 1.0) * fraction * before / 6.0;
    double answer = first * samples[0];
    answer += second * samples[1];
    answer += third * samples[2];
    answer += fourth * samples[3];
    if (!std::isfinite(answer)) return Status::NumericalFailure;
    destination = answer;
    return Status::Ok;
}

Status WaveformHistory::prepare(double sample_rate, std::size_t capacity_frames) noexcept {
    if (!is_supported_sample_rate(sample_rate) || !valid_capacity(capacity_frames)) {
        return Status::InvalidSpec;
    }
    samples_.fill(0.0);
    sample_rate_ = sample_rate;
    capacity_frames_ = capacity_frames;
    next_frame_ = 0;
    max_frame_ = epoch_frames(sample_rate);
    prepared_ = true;
    return Status::Ok;
}

Status WaveformHistory::reset() noexcept {
    if (!prepared_) return Status::NotPrepared;
    samples_.fill(0.0);
    next_frame_ = 0;
    return Status::Ok;
}

Status WaveformHistory::push(double sample) noexcept {
    if (!prepared_) return Status::NotPrepared;
    if (!std::isfinite(sample)
        || sample < -kMaxInputMagnitude || sample > kMaxInputMagnitude) {
        return Status::InvalidBuffer;
    }
    if (next_frame_ >= max_frame_) return Status::TimelineOverflow;
    samples_[slot_for(next_frame_, capacity_frames_)] = sample;
    ++next_frame_;
    return Status::Ok;
}

Status WaveformHistory::sample_at(std::int64_t frame, double& destination) const noexcept {
    if (!prepared_) return Status::NotPrepared;
    const auto maximum = static_cast<std::int64_t>(max_frame_);
    if (frame < -maximum || frame > maximum) return Status::TimelineOverflow;
    if (frame < 0) {
        destination = 0.0;
        return Status::Ok;
    }
    const auto index = static_cast<std::uint64_t>(frame);
    if (index < oldest_frame() || index >= next_frame_) return Status::InsufficientHistory;
    destination = samples_[slot_for(index, capacity_frames_)];
    return Status::Ok;
}

Status WaveformHistory::interpolate(SamplePosition position, double& destination) const noexcept {
    if (!prepared_) return Status::NotPrepared;
    const Status admitted = valid_position(position, max_frame_);
    if (admitted != Status::Ok) return admitted;
    const auto maximum = static_cast<std::int64_t>(max_frame_);
    // Admit the entire support domain before forming k-1 and k+2. The one-day
    // bound is far inside int64_t, so these checked additions cannot overflow.
    if (position.frame <= -maximum || position.frame > maximum - 2) {
        return Status::TimelineOverflow;
    }
    std::array<double, 4> samples{};
    for (std::size_t node = 0; node < samples.size(); ++node) {
        const auto frame = position.frame + static_cast<std::int64_t>(node) - 1;
        const Status status = sample_at(frame, samples[node]);
        if (status != Status::Ok) return status;
    }
    return interpolate_cubic_lagrange(samples, position.fraction, destination);
}

Status MotionFrameHistory::prepare(const RotaryMotion& owner,
                                    std::size_t capacity_frames) noexcept {
    if (!owner.prepared()) return Status::NotPrepared;
    if (!valid_capacity(capacity_frames)) return Status::InvalidSpec;
    if (owner.frame() != 0) return Status::InvalidEvent;
    segments_.fill(MotionSegment{});
    profile_ = owner.profile();
    epoch_initial_ = owner.epoch_initial_state();
    sample_rate_ = owner.sample_rate();
    capacity_frames_ = capacity_frames;
    next_frame_ = 0;
    max_frame_ = owner.max_frame();
    prepared_ = true;
    return Status::Ok;
}

Status MotionFrameHistory::append(const RotaryMotion& owner) noexcept {
    if (!prepared_ || !owner.prepared()) return Status::NotPrepared;
    if (owner.sample_rate() != sample_rate_) return Status::InvalidSpec;
    if (owner.profile() != profile_ || owner.epoch_initial_state() != epoch_initial_) {
        return Status::InvalidProfile;
    }
    if (owner.frame() != next_frame_) return Status::InvalidEvent;
    if (next_frame_ >= max_frame_) return Status::TimelineOverflow;

    MotionState expected = epoch_initial_;
    if (next_frame_ != 0) {
        const MotionSegment& previous = segments_[slot_for(next_frame_ - 1, capacity_frames_)];
        const Status status = evaluate_motion_segment_at(previous,
            {static_cast<std::int64_t>(next_frame_), 0.0}, sample_rate_, expected);
        if (status != Status::Ok) return status;
    }
    if (owner.state() != expected) return Status::InvalidProfile;

    const MotionSegment segment = owner.segment();
    MotionState endpoint;
    const Status status = evaluate_motion_segment_at(segment,
        {static_cast<std::int64_t>(next_frame_ + 1), 0.0}, sample_rate_, endpoint);
    if (status != Status::Ok) return status;
    // Retain the original event anchor and seed, not an interval-local
    // approximation. Retirement of the anchor's own slot changes no trajectory.
    segments_[slot_for(next_frame_, capacity_frames_)] = segment;
    ++next_frame_;
    return Status::Ok;
}

Status MotionFrameHistory::state_at(SamplePosition position,
                                    MotionState& destination) const noexcept {
    if (!prepared_) return Status::NotPrepared;
    const Status admitted = valid_position(position, max_frame_);
    if (admitted != Status::Ok) return admitted;
    if (position.frame < 0) {
        return evaluate_motion_prehistory_at(epoch_initial_, profile_.direction,
                                             position, sample_rate_, destination);
    }
    const auto frame = static_cast<std::uint64_t>(position.frame);
    if (frame < oldest_frame() || frame > next_frame_
        || (frame == next_frame_ && position.fraction != 0.0)) {
        return Status::InsufficientHistory;
    }
    if (next_frame_ == 0) {
        destination = epoch_initial_;
        return Status::Ok;
    }
    // Only the exact final boundary uses the preceding interval. Every other
    // nonnegative query selects the segment owning its integer floor.
    const auto interval = frame == next_frame_ ? frame - 1 : frame;
    return evaluate_motion_segment_at(segments_[slot_for(interval, capacity_frames_)],
                                       position, sample_rate_, destination);
}

} // namespace hammond::rotary
