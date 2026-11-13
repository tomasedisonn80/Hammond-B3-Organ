#include "hammond/RotaryMotion.h"

#include <cmath>
#include <limits>

namespace hammond::rotary {
namespace {

constexpr std::uint64_t kLargestEpochFrames = kMaxEpochSeconds * 192000ULL;

[[nodiscard]] bool direction_valid(std::int8_t direction) noexcept {
    return direction == -1 || direction == 1;
}

[[nodiscard]] bool bounded(double value, double minimum, double maximum) noexcept {
    return std::isfinite(value) && value >= minimum && value <= maximum;
}

[[nodiscard]] std::uint64_t epoch_frames(double sample_rate) noexcept {
    // Call only after the exact four-rate admission. The product is integral
    // and far below either uint64_t or binary64's exact-integer limit.
    return kMaxEpochSeconds * static_cast<std::uint64_t>(sample_rate);
}

[[nodiscard]] Status valid_position(SamplePosition position, double sample_rate) noexcept {
    if (!is_supported_sample_rate(sample_rate)
        || !std::isfinite(position.fraction)
        || position.fraction < 0.0 || position.fraction >= 1.0) {
        return Status::InvalidSpec;
    }
    const auto maximum = static_cast<std::int64_t>(epoch_frames(sample_rate));
    if (position.frame < -maximum || position.frame > maximum
        || (position.frame == maximum && position.fraction != 0.0)) {
        return Status::TimelineOverflow;
    }
    return Status::Ok;
}

[[nodiscard]] Status valid_segment(const MotionSegment& segment) noexcept {
    const Status state_status = validate_motion_state(segment.initial);
    if (state_status != Status::Ok) return state_status;
    if (!bounded(segment.target_rad_s, 0.0, kMaxSpeedRadiansPerSecond)
        || !bounded(segment.tau_s, kMinTimeConstantSeconds, kMaxTimeConstantSeconds)
        || !direction_valid(segment.direction)) {
        return Status::InvalidProfile;
    }
    if (segment.anchor_frame > kLargestEpochFrames) return Status::TimelineOverflow;
    return Status::Ok;
}

// g(z)=z+expm1(-z). The alternating polynomial is evaluated only for z<1/8;
// its terms through z^12 leave less than 4e-20 relative remainder there.
// Unlike subtracting z from expm1, this preserves the O(z^2) start-from-rest
// angle. Fixed work and no termination test depend on the input's magnitude.
[[nodiscard]] double small_angle_remainder(double z) noexcept {
    double polynomial = 1.0 / 479001600.0; // +1/12!
    polynomial = -1.0 / 39916800.0 + z * polynomial;
    polynomial = 1.0 / 3628800.0 + z * polynomial;
    polynomial = -1.0 / 362880.0 + z * polynomial;
    polynomial = 1.0 / 40320.0 + z * polynomial;
    polynomial = -1.0 / 5040.0 + z * polynomial;
    polynomial = 1.0 / 720.0 + z * polynomial;
    polynomial = -1.0 / 120.0 + z * polynomial;
    polynomial = 1.0 / 24.0 + z * polynomial;
    polynomial = -1.0 / 6.0 + z * polynomial;
    polynomial = 0.5 + z * polynomial;
    return z * (z * polynomial);
}

// Add bounded physical angle without ever converting the retained integer
// turn count to floating point. fma retains the local remainder when the
// displacement itself spans millions of turns. Canonicalization can round a
// sub-ulp wrap to zero; MotionEvaluation still retains the signed increment.
[[nodiscard]] Status add_angle(const MotionState& initial, double delta,
                               double speed, MotionState& destination) noexcept {
    if (!std::isfinite(delta) || !bounded(speed, 0.0, kMaxSpeedRadiansPerSecond)) {
        return Status::NumericalFailure;
    }
    const double quotient = std::floor(delta / kTwoPi);
    // Physical-time bounds make this at most about 2.8 million. Check before
    // conversion anyway, so this internal primitive never makes an unsafe cast.
    constexpr double max_turn_delta = 3000000.0;
    if (quotient < -max_turn_delta || quotient > max_turn_delta) {
        return Status::TimelineOverflow;
    }
    auto turns = static_cast<std::int64_t>(quotient);
    double remainder = std::fma(-quotient, kTwoPi, delta);
    if (remainder < 0.0) {
        remainder += kTwoPi;
        --turns;
    } else if (remainder >= kTwoPi) {
        remainder -= kTwoPi;
        ++turns;
    }
    double phase = initial.phase_rad + remainder;
    if (phase >= kTwoPi) {
        phase -= kTwoPi;
        ++turns;
    }
    if (phase == 0.0) phase = 0.0; // Canonical positive zero after arithmetic.
    if (turns > 0 && initial.turns > std::numeric_limits<std::int64_t>::max() - turns) {
        return Status::TimelineOverflow;
    }
    if (turns < 0 && initial.turns < std::numeric_limits<std::int64_t>::min() - turns) {
        return Status::TimelineOverflow;
    }
    if (!std::isfinite(phase) || phase < 0.0 || phase >= kTwoPi) {
        return Status::NumericalFailure;
    }
    destination = MotionState{phase, initial.turns + turns, speed};
    return Status::Ok;
}

[[nodiscard]] Status evaluate_split(const MotionSegment& segment,
                                    std::uint64_t integer_frames, double fraction,
                                    double sample_rate, MotionState& destination) noexcept {
    const auto rate = static_cast<std::uint64_t>(sample_rate);
    const std::uint64_t seconds = integer_frames / rate;
    const std::uint64_t remaining = integer_frames % rate;
    const double subsecond = (static_cast<double>(remaining) + fraction) / sample_rate;
    MotionEvaluation whole;
    Status status = evaluate_motion_segment(segment, static_cast<double>(seconds), whole);
    if (status != Status::Ok) return status;
    if (subsecond == 0.0) {
        destination = whole.state;
        return Status::Ok;
    }
    MotionSegment tail = segment;
    tail.initial = whole.state;
    MotionEvaluation part;
    status = evaluate_motion_segment(tail, subsecond, part);
    if (status != Status::Ok) return status;
    destination = part.state;
    return Status::Ok;
}

} // namespace

Status validate_motion_profile(const MotionProfile& profile) noexcept {
    if (!bounded(profile.slow_rad_s, 0.0, kMaxSpeedRadiansPerSecond)
        || !bounded(profile.fast_rad_s, profile.slow_rad_s, kMaxSpeedRadiansPerSecond)
        || !bounded(profile.tau_up_s, kMinTimeConstantSeconds, kMaxTimeConstantSeconds)
        || !bounded(profile.tau_down_s, kMinTimeConstantSeconds, kMaxTimeConstantSeconds)
        || !direction_valid(profile.direction)) {
        return Status::InvalidProfile;
    }
    return Status::Ok;
}

Status validate_motion_state(const MotionState& state) noexcept {
    if (!std::isfinite(state.phase_rad) || state.phase_rad < 0.0 || state.phase_rad >= kTwoPi
        || !bounded(state.speed_rad_s, 0.0, kMaxSpeedRadiansPerSecond)) {
        return Status::InvalidProfile;
    }
    return Status::Ok;
}

Status make_motion_segment(const MotionProfile& profile, const MotionState& initial,
                           SpeedCommand command, std::uint64_t anchor_frame,
                           MotionSegment& destination) noexcept {
    Status status = validate_motion_profile(profile);
    if (status != Status::Ok) return status;
    status = validate_motion_state(initial);
    if (status != Status::Ok) return status;
    if (!is_valid_command(command)) return Status::InvalidEvent;
    if (anchor_frame > kLargestEpochFrames) return Status::TimelineOverflow;
    const double target = command == SpeedCommand::Chorale
                        ? profile.slow_rad_s : profile.fast_rad_s;
    destination = MotionSegment{anchor_frame, initial, target,
        target >= initial.speed_rad_s ? profile.tau_up_s : profile.tau_down_s,
        profile.direction};
    return Status::Ok;
}

Status evaluate_motion_segment(const MotionSegment& segment, double elapsed_s,
                               MotionEvaluation& destination) noexcept {
    const Status admitted = valid_segment(segment);
    if (admitted != Status::Ok) return admitted;
    if (!bounded(elapsed_s, 0.0, static_cast<double>(kMaxEpochSeconds))) {
        return Status::InvalidSpec;
    }
    if (elapsed_s == 0.0) {
        destination = MotionEvaluation{segment.initial, 0.0};
        return Status::Ok;
    }
    const double start = segment.initial.speed_rad_s;
    const double target = segment.target_rad_s;
    const double tau = segment.tau_s;
    const double z = elapsed_s / tau;
    const double difference = target - start;
    double speed = start;
    double distance = start * elapsed_s;
    if (difference != 0.0) {
        const double q = -std::expm1(-z);
        if (z < 0.125) {
            speed = std::fma(difference, q, start);
            distance = std::fma(difference * tau, small_angle_remainder(z), distance);
        } else {
            // This retains a nonzero decaying tail when the target is zero.
            speed = std::fma(start - target, std::exp(-z), target);
            distance = std::fma((start - target) * tau, q, target * elapsed_s);
        }
    }
    const double increment = static_cast<double>(segment.direction) * distance;
    MotionState state;
    const Status advanced = add_angle(segment.initial, increment, speed, state);
    if (advanced != Status::Ok) return advanced;
    destination = MotionEvaluation{state, increment};
    return Status::Ok;
}

Status evaluate_motion_segment_at(const MotionSegment& segment, SamplePosition position,
                                  double sample_rate, MotionState& destination) noexcept {
    const Status admitted = valid_position(position, sample_rate);
    if (admitted != Status::Ok) return admitted;
    const Status segment_status = valid_segment(segment);
    if (segment_status != Status::Ok) return segment_status;
    if (segment.anchor_frame > epoch_frames(sample_rate)) return Status::TimelineOverflow;
    if (position.frame < 0
        || static_cast<std::uint64_t>(position.frame) < segment.anchor_frame) {
        return Status::InsufficientHistory;
    }
    const auto difference = static_cast<std::uint64_t>(position.frame) - segment.anchor_frame;
    return evaluate_split(segment, difference, position.fraction, sample_rate, destination);
}

Status evaluate_motion_prehistory(const MotionState& initial, std::int8_t direction,
                                 double seconds_before_zero,
                                 MotionEvaluation& destination) noexcept {
    const Status admitted = validate_motion_state(initial);
    if (admitted != Status::Ok) return admitted;
    if (!direction_valid(direction)) return Status::InvalidProfile;
    if (!bounded(seconds_before_zero, -static_cast<double>(kMaxEpochSeconds), 0.0)) {
        return Status::InvalidSpec;
    }
    if (seconds_before_zero == 0.0) {
        destination = MotionEvaluation{initial, 0.0};
        return Status::Ok;
    }
    const double increment = static_cast<double>(direction) * initial.speed_rad_s * seconds_before_zero;
    MotionState state;
    const Status advanced = add_angle(initial, increment, initial.speed_rad_s, state);
    if (advanced != Status::Ok) return advanced;
    destination = MotionEvaluation{state, increment};
    return Status::Ok;
}

Status evaluate_motion_prehistory_at(const MotionState& initial, std::int8_t direction,
                                    SamplePosition position, double sample_rate,
                                    MotionState& destination) noexcept {
    const Status admitted = valid_position(position, sample_rate);
    if (admitted != Status::Ok) return admitted;
    if (position.frame > 0 || (position.frame == 0 && position.fraction != 0.0)) {
        return Status::InvalidSpec;
    }
    // valid_position excludes INT64_MIN before this negation.
    const auto magnitude = static_cast<std::uint64_t>(-position.frame);
    const auto rate = static_cast<std::uint64_t>(sample_rate);
    std::uint64_t seconds = magnitude / rate;
    std::uint64_t remaining = magnitude % rate;
    if (remaining == 0 && position.fraction != 0.0) {
        --seconds;
        remaining = rate;
    }
    const double subsecond = (static_cast<double>(remaining) - position.fraction) / sample_rate;
    MotionEvaluation whole;
    Status status = evaluate_motion_prehistory(initial, direction,
                                              -static_cast<double>(seconds), whole);
    if (status != Status::Ok) return status;
    if (subsecond == 0.0) {
        destination = whole.state;
        return Status::Ok;
    }
    MotionEvaluation part;
    status = evaluate_motion_prehistory(whole.state, direction, -subsecond, part);
    if (status != Status::Ok) return status;
    destination = part.state;
    return Status::Ok;
}

Status RotaryMotion::prepare(const MotionProfile& profile, double phase, double speed,
                             SpeedCommand command, double rate) noexcept {
    if (!is_supported_sample_rate(rate)) return Status::InvalidSpec;
    const MotionState initial{phase, 0, speed};
    MotionSegment segment;
    const Status admitted = make_motion_segment(profile, initial, command, 0, segment);
    if (admitted != Status::Ok) return admitted;
    profile_ = profile;
    original_initial_ = initial;
    epoch_initial_ = initial;
    state_ = initial;
    segment_ = segment;
    original_command_ = command;
    command_ = command;
    sample_rate_ = rate;
    frame_ = 0;
    max_frame_ = epoch_frames(rate);
    prepared_ = true;
    return Status::Ok;
}

Status RotaryMotion::advance_to(std::uint64_t frame) noexcept {
    if (!prepared_) return Status::NotPrepared;
    if (frame > max_frame_) return Status::TimelineOverflow;
    if (frame < frame_) return Status::InvalidEvent;
    MotionState candidate;
    const Status evaluated = evaluate_motion_segment_at(segment_,
        SamplePosition{static_cast<std::int64_t>(frame), 0.0}, sample_rate_, candidate);
    if (evaluated != Status::Ok) return evaluated;
    state_ = candidate;
    frame_ = frame;
    return Status::Ok;
}

Status RotaryMotion::apply_command(std::uint64_t frame, SpeedCommand command) noexcept {
    if (!prepared_) return Status::NotPrepared;
    if (!is_valid_command(command)) return Status::InvalidEvent;
    if (frame > max_frame_) return Status::TimelineOverflow;
    if (frame < frame_) return Status::InvalidEvent;
    MotionState candidate;
    Status status = evaluate_motion_segment_at(segment_,
        SamplePosition{static_cast<std::int64_t>(frame), 0.0}, sample_rate_, candidate);
    if (status != Status::Ok) return status;
    MotionSegment new_segment = segment_;
    if (command != command_) {
        status = make_motion_segment(profile_, candidate, command, frame, new_segment);
        if (status != Status::Ok) return status;
    }
    state_ = candidate;
    segment_ = new_segment;
    command_ = command;
    frame_ = frame;
    return Status::Ok;
}

Status RotaryMotion::state_at(SamplePosition position, MotionState& destination) const noexcept {
    if (!prepared_) return Status::NotPrepared;
    if (position.frame < 0) {
        return evaluate_motion_prehistory_at(epoch_initial_, profile_.direction,
                                             position, sample_rate_, destination);
    }
    return evaluate_motion_segment_at(segment_, position, sample_rate_, destination);
}

Status RotaryMotion::reset() noexcept {
    if (!prepared_) return Status::NotPrepared;
    MotionSegment segment;
    const Status status = make_motion_segment(profile_, original_initial_, original_command_, 0, segment);
    if (status != Status::Ok) return status;
    epoch_initial_ = original_initial_;
    state_ = original_initial_;
    segment_ = segment;
    command_ = original_command_;
    frame_ = 0;
    return Status::Ok;
}

Status RotaryMotion::reconfigure_sample_rate(double rate) noexcept {
    if (!prepared_) return Status::NotPrepared;
    if (!is_supported_sample_rate(rate)) return Status::InvalidSpec;
    MotionSegment segment;
    const Status status = make_motion_segment(profile_, state_, command_, 0, segment);
    if (status != Status::Ok) return status;
    epoch_initial_ = state_;
    segment_ = segment;
    frame_ = 0;
    sample_rate_ = rate;
    max_frame_ = epoch_frames(rate);
    return Status::Ok;
}

} // namespace hammond::rotary
