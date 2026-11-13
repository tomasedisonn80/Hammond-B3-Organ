#include "hammond/Percussion.h"

#include <algorithm>
#include <cmath>
#include <limits>

namespace hammond {
namespace {

[[nodiscard]] bool finite_in_range(double value, double minimum, double maximum) noexcept {
    return std::isfinite(value) && value >= minimum && value <= maximum;
}

} // namespace

Status validate_percussion_profile(const PercussionProfile& profile,
                                   double sample_rate) noexcept {
    if (!is_supported_sample_rate(sample_rate)) {
        return Status::InvalidSpec;
    }
    if (!finite_in_range(profile.slow_decay_seconds, 1.0e-4, 60.0) ||
        !finite_in_range(profile.fast_decay_seconds, 1.0e-4, 60.0) ||
        !finite_in_range(profile.recovery_seconds, 1.0e-4, 60.0) ||
        !finite_in_range(profile.normal_gain, 0.0, 4.0) ||
        !finite_in_range(profile.soft_gain, 0.0, 4.0) ||
        !finite_in_range(profile.fast_gain_multiplier, 0.0, 4.0) ||
        !finite_in_range(profile.normal_sustain_gain, 0.0, 1.0)) {
        return Status::InvalidProfile;
    }
    return Status::Ok;
}

Status PercussionState::prepare(const PercussionProfile& profile,
                                double sample_rate) noexcept {
    const Status validation = validate_percussion_profile(profile, sample_rate);
    if (validation != Status::Ok) {
        return validation;
    }

    // Exponentials belong to preparation. expm1 retains the small positive
    // recovery fraction without subtracting two nearly equal doubles.
    const double slow_factor = std::exp(-1.0 / (sample_rate * profile.slow_decay_seconds));
    const double fast_factor = std::exp(-1.0 / (sample_rate * profile.fast_decay_seconds));
    const double recovery_step = -std::expm1(-1.0 / (sample_rate * profile.recovery_seconds));
    if (!std::isfinite(slow_factor) || slow_factor <= 0.0 || slow_factor >= 1.0 ||
        !std::isfinite(fast_factor) || fast_factor <= 0.0 || fast_factor >= 1.0 ||
        !std::isfinite(recovery_step) || recovery_step <= 0.0 || recovery_step >= 1.0) {
        return Status::InvalidProfile;
    }

    profile_ = profile;
    slow_decay_factor_ = slow_factor;
    fast_decay_factor_ = fast_factor;
    recovery_step_ = recovery_step;
    readiness_ = 1.0;
    sample_rate_ = sample_rate;
    prepared_ = true;
    return Status::Ok;
}

Status PercussionState::reconfigure_sample_rate(double sample_rate) noexcept {
    if (!prepared_) {
        return Status::NotPrepared;
    }
    if (!is_supported_sample_rate(sample_rate)) {
        return Status::InvalidSpec;
    }
    if (sample_rate == sample_rate_) {
        return Status::Ok;
    }

    // Reuse the same validated coefficient calculation as preparation, but
    // retain this organ's charge surrogate instead of installing a fresh q=1.
    // The candidate owns its profile, and every fallible step precedes commit.
    PercussionState candidate;
    const Status status = candidate.prepare(profile_, sample_rate);
    if (status != Status::Ok) {
        return status;
    }
    candidate.readiness_ = readiness_;
    *this = candidate;
    return Status::Ok;
}

double PercussionState::gain(const PercussionSettings& settings) const noexcept {
    if (!prepared_ || !is_valid_percussion_settings(settings) || !settings.enabled) {
        return 0.0;
    }
    const double level = settings.volume == PercussionVolume::Normal
                           ? profile_.normal_gain : profile_.soft_gain;
    const double fast_scale = settings.decay == PercussionDecay::Fast
                                ? profile_.fast_gain_multiplier : 1.0;
    return readiness_ * level * fast_scale;
}

double PercussionState::upper_sustain_gain(const PercussionSettings& settings) const noexcept {
    if (!prepared_ || !is_valid_percussion_settings(settings) || !settings.enabled ||
        settings.volume == PercussionVolume::Soft) {
        return 1.0;
    }
    return profile_.normal_sustain_gain;
}

bool PercussionState::advance_frame(bool routed_detector,
                                   const PercussionSettings& settings) noexcept {
    if (!prepared_ || !is_valid_percussion_settings(settings) ||
        (routed_detector && !settings.enabled)) {
        return false;
    }

    if (routed_detector) {
        const double factor = settings.decay == PercussionDecay::Slow
                                ? slow_decay_factor_ : fast_decay_factor_;
        const double next = readiness_ * factor;
        readiness_ = next < std::numeric_limits<double>::min() ? 0.0 : next;
    } else {
        // This form preserves the recovery step close to q=0 and reaches a
        // bounded binary64 approximation near q=1, without a block-size term.
        readiness_ += (1.0 - readiness_) * recovery_step_;
    }
    readiness_ = std::clamp(readiness_, 0.0, 1.0);
    return true;
}

} // namespace hammond
