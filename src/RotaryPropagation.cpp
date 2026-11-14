#include "hammond/RotaryPropagation.h"

#include <algorithm>
#include <cmath>
#include <limits>

namespace hammond::rotary {
namespace {

[[nodiscard]] bool bounded(double value, double minimum, double maximum) noexcept {
    return std::isfinite(value) && value >= minimum && value <= maximum;
}

[[nodiscard]] bool valid_vector(const Vec3& value) noexcept {
    return bounded(value.x, -kMaxCoordinateMetres, kMaxCoordinateMetres)
        && bounded(value.y, -kMaxCoordinateMetres, kMaxCoordinateMetres)
        && bounded(value.z, -kMaxCoordinateMetres, kMaxCoordinateMetres);
}

[[nodiscard]] std::uint64_t epoch_frames(double sample_rate) noexcept {
    // Preparation admitted one of four exact integer rates before this call.
    return kMaxEpochSeconds * static_cast<std::uint64_t>(sample_rate);
}

[[nodiscard]] Status query_range(SamplePosition position, double sample_rate,
                                  std::uint64_t through_frame) noexcept {
    if (!std::isfinite(position.fraction)
        || position.fraction < 0.0 || position.fraction >= 1.0) {
        return Status::InvalidSpec;
    }
    const auto maximum = static_cast<std::int64_t>(epoch_frames(sample_rate));
    if (position.frame < -maximum || position.frame > maximum
        || (position.frame == maximum && position.fraction != 0.0)) {
        return Status::TimelineOverflow;
    }
    if (position.frame >= 0
        && (static_cast<std::uint64_t>(position.frame) > through_frame
            || (static_cast<std::uint64_t>(position.frame) == through_frame
                && position.fraction != 0.0))) {
        return Status::InsufficientHistory;
    }
    return Status::Ok;
}

[[nodiscard]] bool earlier(SamplePosition left, SamplePosition right) noexcept {
    return left.frame < right.frame
        || (left.frame == right.frame && left.fraction < right.fraction);
}

// Only the short propagation delay is converted to fractional frames. The
// absolute observation frame is never converted to double. The admitted local
// delay is below 0.067 seconds, so all integer conversions are bounded.
[[nodiscard]] Status subtract_delay(SamplePosition observation, double delay_s,
                                     double sample_rate, SamplePosition& result) noexcept {
    const double delay_frames = delay_s * sample_rate;
    if (!std::isfinite(delay_frames) || delay_frames <= 0.0
        || delay_frames >= 13000.0) {
        return Status::NumericalFailure;
    }
    double whole = 0.0;
    const double part = std::modf(delay_frames, &whole);
    const auto integer = static_cast<std::int64_t>(whole);
    if (observation.frame < std::numeric_limits<std::int64_t>::min() + integer) {
        return Status::TimelineOverflow;
    }
    auto frame = observation.frame - integer;
    double fraction = observation.fraction - part;
    if (fraction < 0.0) {
        if (frame == std::numeric_limits<std::int64_t>::min()) return Status::TimelineOverflow;
        --frame;
        fraction += 1.0;
    }
    // A sub-ulp negative fraction may round to 1 when normalized. Carry it
    // rather than returning a noncanonical position to the history query.
    if (fraction >= 1.0) {
        if (frame == std::numeric_limits<std::int64_t>::max()) return Status::TimelineOverflow;
        ++frame;
        fraction -= 1.0;
    }
    if (fraction == 0.0) fraction = 0.0;
    const SamplePosition candidate{frame, fraction};
    if (!earlier(candidate, observation)) return Status::NumericalFailure;
    result = candidate;
    return Status::Ok;
}

struct Evaluation {
    PathResult path{};
    SamplePosition emission{};
};

} // namespace

Status MotionHistoryView::prepare(const MotionProfile& profile,
                                  const MotionState& epoch_initial,
                                  double sample_rate,
                                  std::span<const MotionSegment> segments,
                                  std::uint64_t through_frame) noexcept {
    if (!is_supported_sample_rate(sample_rate)
        || segments.empty() || segments.size() > kMaxMotionSegments) {
        return Status::InvalidSpec;
    }
    Status status = validate_motion_profile(profile);
    if (status != Status::Ok) return status;
    status = validate_motion_state(epoch_initial);
    if (status != Status::Ok) return status;
    const std::uint64_t maximum = epoch_frames(sample_rate);
    if (through_frame > maximum) return Status::TimelineOverflow;
    if (segments.front().anchor_frame > maximum) return Status::TimelineOverflow;
    if (segments.front().anchor_frame != 0) return Status::InvalidEvent;

    for (std::size_t index = 0; index < segments.size(); ++index) {
        const MotionSegment& segment = segments[index];
        if (segment.anchor_frame > maximum) return Status::TimelineOverflow;
        if (segment.anchor_frame > through_frame
            || (index != 0 && segment.anchor_frame <= segments[index - 1].anchor_frame)) {
            return Status::InvalidEvent;
        }
        status = validate_motion_state(segment.initial);
        if (status != Status::Ok) return status;
        const double expected_tau = segment.target_rad_s >= segment.initial.speed_rad_s
                                  ? profile.tau_up_s : profile.tau_down_s;
        if (segment.direction != profile.direction
            || (segment.target_rad_s != profile.slow_rad_s
                && segment.target_rad_s != profile.fast_rad_s)
            || segment.tau_s != expected_tau) {
            return Status::InvalidProfile;
        }
        MotionState expected = epoch_initial;
        if (index != 0) {
            status = evaluate_motion_segment_at(segments[index - 1],
                SamplePosition{static_cast<std::int64_t>(segment.anchor_frame), 0.0},
                sample_rate, expected);
            if (status != Status::Ok) return status;
        }
        if (segment.initial != expected) return Status::InvalidProfile;
    }
    MotionState final_state;
    status = evaluate_motion_segment_at(segments.back(),
        SamplePosition{static_cast<std::int64_t>(through_frame), 0.0},
        sample_rate, final_state);
    if (status != Status::Ok) return status;

    segments_ = segments;
    profile_ = profile;
    epoch_initial_ = epoch_initial;
    sample_rate_ = sample_rate;
    through_frame_ = through_frame;
    prepared_ = true;
    return Status::Ok;
}

Status MotionHistoryView::state_at(SamplePosition position, MotionState& destination) const noexcept {
    if (!prepared_) return Status::NotPrepared;
    const Status status = query_range(position, sample_rate_, through_frame_);
    if (status != Status::Ok) return status;
    if (position.frame < 0) {
        return evaluate_motion_prehistory_at(epoch_initial_, profile_.direction,
                                             position, sample_rate_, destination);
    }
    const auto frame = static_cast<std::uint64_t>(position.frame);
    std::size_t lo = 0;
    std::size_t hi = segments_.size();
    while (lo < hi) {
        const std::size_t middle = lo + (hi - lo) / 2;
        if (segments_[middle].anchor_frame <= frame) lo = middle + 1;
        else hi = middle;
    }
    return evaluate_motion_segment_at(segments_[lo - 1], position, sample_rate_, destination);
}

Status evaluate_circular_source(const Vec3& origin_m, double radius_m,
                                const MotionState& state, std::int8_t direction,
                                Vec3& position_m, Vec3& velocity_m_s) noexcept {
    if (&position_m == &velocity_m_s) return Status::InvalidBuffer;
    if (!valid_vector(origin_m) || !bounded(radius_m, 0.0, kMaxRadiusMetres)
        || (direction != -1 && direction != 1)) {
        return Status::InvalidProfile;
    }
    const Status status = validate_motion_state(state);
    if (status != Status::Ok) return status;
    const double cosine = std::cos(state.phase_rad);
    const double sine = std::sin(state.phase_rad);
    const double signed_speed = static_cast<double>(direction) * state.speed_rad_s;
    const Vec3 position{origin_m.x + radius_m * cosine,
                        origin_m.y + radius_m * sine, origin_m.z};
    const Vec3 velocity{-radius_m * signed_speed * sine,
                        radius_m * signed_speed * cosine, 0.0};
    position_m = position;
    velocity_m_s = velocity;
    return Status::Ok;
}

Status PreparedRetardedPath::prepare(const MotionHistoryView& history,
                                     const Vec3& origin_m, double radius_m,
                                     const MicrophoneProfile& microphone,
                                     double sound_speed_m_s,
                                     double reference_distance_m) noexcept {
    if (!history.prepared()) return Status::NotPrepared;
    if (!valid_vector(origin_m) || !valid_vector(microphone.position_m)
        || !bounded(radius_m, 0.0, kMaxRadiusMetres)
        || !bounded(sound_speed_m_s, kMinSoundSpeedMetresPerSecond, kMaxSoundSpeedMetresPerSecond)
        || !bounded(reference_distance_m, kMinReferenceDistanceMetres, kMaxReferenceDistanceMetres)) {
        return Status::InvalidProfile;
    }
    const double horizontal = std::hypot(microphone.position_m.x - origin_m.x,
                                          microphone.position_m.y - origin_m.y);
    const double height = microphone.position_m.z - origin_m.z;
    const MotionProfile profile = history.profile();
    const double speed = std::max({history.epoch_initial_state().speed_rad_s,
                                   profile.slow_rad_s, profile.fast_rad_s});
    const PathBounds bounds{std::hypot(horizontal - radius_m, height),
                            std::hypot(horizontal + radius_m, height),
                            radius_m * speed / sound_speed_m_s};
    if (!std::isfinite(bounds.min_distance_m) || !std::isfinite(bounds.max_distance_m)
        || !std::isfinite(bounds.max_tangential_mach)
        || bounds.min_distance_m < kMinPathMetres
        || bounds.max_distance_m > kMaxPathMetres
        || bounds.max_tangential_mach > kMaxTangentialMach) {
        return Status::InvalidProfile;
    }

    history_ = history;
    origin_m_ = origin_m;
    microphone_ = microphone;
    bounds_ = bounds;
    radius_m_ = radius_m;
    sound_speed_m_s_ = sound_speed_m_s;
    reference_distance_m_ = reference_distance_m;
    prepared_ = true;
    return Status::Ok;
}

Status PreparedRetardedPath::solve(SamplePosition observation, PathResult& result,
                                   SamplePosition& emission) const noexcept {
    if (!prepared_) return Status::NotPrepared;
    Status status = query_range(observation, history_.sample_rate(), history_.through_frame());
    if (status != Status::Ok) return status;
    std::uint32_t evaluations = 0;
    const auto evaluate = [&](double delay_s, Evaluation& destination) noexcept -> Status {
        ++evaluations;
        Evaluation candidate;
        Status current = subtract_delay(observation, delay_s, history_.sample_rate(), candidate.emission);
        if (current != Status::Ok) return current;
        MotionState state;
        current = history_.state_at(candidate.emission, state);
        if (current != Status::Ok) return current;
        Vec3 position;
        Vec3 velocity;
        current = evaluate_circular_source(origin_m_, radius_m_, state,
                                             history_.profile().direction, position, velocity);
        if (current != Status::Ok) return current;
        const Vec3 difference{microphone_.position_m.x - position.x,
                               microphone_.position_m.y - position.y,
                               microphone_.position_m.z - position.z};
        const double distance = std::hypot(difference.x, difference.y, difference.z);
        if (!std::isfinite(distance) || distance <= 0.0) return Status::NumericalFailure;
        const double radial = std::fma(difference.x / distance, velocity.x,
            std::fma(difference.y / distance, velocity.y, (difference.z / distance) * velocity.z));
        const double derivative = 1.0 - radial / sound_speed_m_s_;
        if (!bounded(derivative, 0.75 - 2.0e-15, 1.25 + 2.0e-15)) {
            return Status::NumericalFailure;
        }
        candidate.path = PathResult{delay_s, distance, state.phase_rad, radial,
            1.0 / derivative, reference_distance_m_ / distance,
            delay_s - distance / sound_speed_m_s_, 0};
        if (!std::isfinite(candidate.path.residual_s)
            || !std::isfinite(candidate.path.distance_gain)
            || !std::isfinite(candidate.path.frequency_ratio)) {
            return Status::NumericalFailure;
        }
        destination = candidate;
        return Status::Ok;
    };

    const double scale = std::max(1.0, bounds_.max_distance_m);
    const double margin = 32.0 * (std::nextafter(scale, std::numeric_limits<double>::infinity()) - scale);
    double lo = std::max(0.0, bounds_.min_distance_m - margin) / sound_speed_m_s_;
    double hi = (bounds_.max_distance_m + margin) / sound_speed_m_s_;
    Evaluation low;
    Evaluation high;
    status = evaluate(lo, low);
    if (status != Status::Ok) return status;
    status = evaluate(hi, high);
    if (status != Status::Ok) return status;
    if (low.path.residual_s > 0.0 || high.path.residual_s < 0.0) {
        return Status::NumericalFailure;
    }
    Evaluation selected = std::abs(low.path.residual_s) <= std::abs(high.path.residual_s) ? low : high;
    constexpr double early_residual_s = 1.0e-14;
    while (evaluations < kMaxSolverIterations
           && std::abs(selected.path.residual_s) > early_residual_s) {
        const double middle = lo + (hi - lo) * 0.5;
        if (middle == lo || middle == hi) break;
        Evaluation candidate;
        status = evaluate(middle, candidate);
        if (status != Status::Ok) return status;
        if (std::abs(candidate.path.residual_s) < std::abs(selected.path.residual_s)) selected = candidate;
        if (candidate.path.residual_s < 0.0) lo = middle;
        else hi = middle;
    }
    if (!std::isfinite(selected.path.residual_s)
        || std::abs(selected.path.residual_s) > kMaxSolverResidualSeconds
        || selected.path.delay_s <= 0.0 || !earlier(selected.emission, observation)) {
        return Status::NumericalFailure;
    }
    selected.path.iterations = evaluations;
    result = selected.path;
    emission = selected.emission;
    return Status::Ok;
}

} // namespace hammond::rotary
