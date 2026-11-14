#include "hammond/RotaryRenderer.h"
#include "hammond/RotaryPropagation.h"

#include <algorithm>
#include <cmath>
#include <limits>

// The admitted R3 direct-path equations and finite evaluation budget are
// retained here with a separately owned streaming-history query. The immutable
// MotionHistoryView API/source is unchanged. Independent R4 acceptance must
// qualify this adapter; source reuse alone is not an executed parity result.
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

Status PreparedStreamingPath::prepare(const RotorProfile& rotor,
                                      const MicrophoneProfile& microphone,
                                      double sound_speed_m_s,
                                      double reference_distance_m) noexcept {
    Status status = validate_motion_profile(rotor.motion);
    if (status != Status::Ok) return status;
    status = validate_motion_state(MotionState{rotor.initial_phase_rad, 0,
                                               rotor.initial_speed_rad_s});
    if (status != Status::Ok) return status;
    if (!is_valid_command(rotor.initial_command)
        || !valid_vector(rotor.origin_m) || !valid_vector(microphone.position_m)
        || !bounded(rotor.radius_m, 0.0, kMaxRadiusMetres)
        || !bounded(sound_speed_m_s, kMinSoundSpeedMetresPerSecond, kMaxSoundSpeedMetresPerSecond)
        || !bounded(reference_distance_m, kMinReferenceDistanceMetres, kMaxReferenceDistanceMetres)) {
        return Status::InvalidProfile;
    }
    const double horizontal = std::hypot(microphone.position_m.x - rotor.origin_m.x,
                                         microphone.position_m.y - rotor.origin_m.y);
    const double height = microphone.position_m.z - rotor.origin_m.z;
    const double speed = std::max({rotor.initial_speed_rad_s, rotor.motion.slow_rad_s,
                                   rotor.motion.fast_rad_s});
    const PathBounds bounds{std::hypot(horizontal - rotor.radius_m, height),
                            std::hypot(horizontal + rotor.radius_m, height),
                            rotor.radius_m * speed / sound_speed_m_s};
    if (!std::isfinite(bounds.min_distance_m) || !std::isfinite(bounds.max_distance_m)
        || !std::isfinite(bounds.max_tangential_mach)
        || bounds.min_distance_m < kMinPathMetres
        || bounds.max_distance_m > kMaxPathMetres
        || bounds.max_tangential_mach > kMaxTangentialMach) {
        return Status::InvalidProfile;
    }
    motion_profile_ = rotor.motion;
    origin_m_ = rotor.origin_m;
    microphone_ = microphone;
    bounds_ = bounds;
    radius_m_ = rotor.radius_m;
    sound_speed_m_s_ = sound_speed_m_s;
    reference_distance_m_ = reference_distance_m;
    max_speed_rad_s_ = speed;
    prepared_ = true;
    return Status::Ok;
}

Status PreparedStreamingPath::solve(const MotionFrameHistory& history,
                                     SamplePosition observation, PathResult& result,
                                     SamplePosition& emission) const noexcept {
    if (!prepared_) return Status::NotPrepared;
    if (!history.prepared()) return Status::NotPrepared;
    if (history.profile() != motion_profile_
        || history.epoch_initial_state().speed_rad_s > max_speed_rad_s_) {
        return Status::InvalidProfile;
    }
    // The observation itself must be in retained coverage. Each endpoint and
    // midpoint independently admits its earlier emission through the history.
    MotionState observation_state;
    Status status = history.state_at(observation, observation_state);
    if (status != Status::Ok) return status;
    std::uint32_t evaluations = 0;
    const auto evaluate = [&](double delay_s, Evaluation& destination) noexcept -> Status {
        ++evaluations;
        Evaluation candidate;
        Status current = subtract_delay(observation, delay_s, history.sample_rate(), candidate.emission);
        if (current != Status::Ok) return current;
        MotionState state;
        current = history.state_at(candidate.emission, state);
        if (current != Status::Ok) return current;
        Vec3 position;
        Vec3 velocity;
        current = evaluate_circular_source(origin_m_, radius_m_, state,
                                             history.profile().direction, position, velocity);
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
