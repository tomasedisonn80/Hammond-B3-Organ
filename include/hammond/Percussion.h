#pragma once

#include "hammond/Types.h"

#include <cstdint>
#include <string_view>

namespace hammond {

inline constexpr std::string_view kPercussionModelId = "shared-readiness-v1";

enum class PercussionHarmonic : std::uint8_t { Second = 0, Third = 1 };
enum class PercussionVolume : std::uint8_t { Normal = 0, Soft = 1 };
enum class PercussionDecay : std::uint8_t { Slow = 0, Fast = 1 };

// Retained controls only. Eligibility, physical contacts and the evolving
// readiness state are separate; changing these controls never initializes q.
struct PercussionSettings {
    bool enabled{false};
    PercussionHarmonic harmonic{PercussionHarmonic::Second};
    PercussionVolume volume{PercussionVolume::Normal};
    PercussionDecay decay{PercussionDecay::Slow};

    [[nodiscard]] bool operator==(const PercussionSettings&) const noexcept = default;
};

[[nodiscard]] constexpr bool is_valid_percussion_settings(
    const PercussionSettings& settings) noexcept {
    return (settings.harmonic == PercussionHarmonic::Second ||
            settings.harmonic == PercussionHarmonic::Third) &&
           (settings.volume == PercussionVolume::Normal ||
            settings.volume == PercussionVolume::Soft) &&
           (settings.decay == PercussionDecay::Slow ||
            settings.decay == PercussionDecay::Fast);
}

// All times are seconds; all gains are dimensionless normalized amplitudes.
// Zero initialization is deliberately invalid. Bounds are engineering support
// limits, not manufacturer specifications: taus [1e-4, 60], percussion gains and
// fast multiplier [0, 4], upper-sustain gain [0, 1].
struct PercussionProfile {
    double slow_decay_seconds{0.0};
    double fast_decay_seconds{0.0};
    double recovery_seconds{0.0};
    double normal_gain{0.0};
    double soft_gain{0.0};
    double fast_gain_multiplier{0.0};
    double normal_sustain_gain{0.0};

    [[nodiscard]] bool operator==(const PercussionProfile&) const noexcept = default;
};

// Unmeasured readiness surrogate. Atlas p.135 gives the isolated RC hypotheses:
// C31=0.33 uF, R57=1.5 Mohm, R58=4.7 Mohm, R55+R56=104 kohm. They are NOT
// measured audible decay lengths or a complete AO-28 transfer. The gain choices
// and F(q)=q are proposed normalized engineering values; see assignment 08.
[[nodiscard]] constexpr PercussionProfile make_nominal_percussion_profile() noexcept {
    return {1.551, ((1.5e6 * 4.7e6) / (1.5e6 + 4.7e6)) * 3.3e-7,
            0.03432, 1.0, 0.5, 1.5, 0.70710678118654752440};
}

[[nodiscard]] Status validate_percussion_profile(const PercussionProfile& profile,
                                                 double sample_rate) noexcept;

struct PercussionDiagnostics {
    bool prepared{false};
    double readiness{0.0};
    double sample_rate{0.0};

    [[nodiscard]] bool operator==(const PercussionDiagnostics&) const noexcept = default;
};

// One shared state per organ. This is not a per-note envelope, a voltage model,
// a complete percussion circuit, or a calibrated instrument. No source lookup,
// allocation, file access or host/UI state belongs here. All access is stopped
// or on the processing thread; there is no concurrent publication protocol.
class PercussionState {
public:
    // Validate and precompute coefficients before installation. Success starts
    // q=1; failure preserves all previous state. Only the project's three
    // supported rates are accepted. Rate migration is not this reset operation.
    [[nodiscard]] Status prepare(const PercussionProfile& profile,
                                 double sample_rate) noexcept;

    // Recompute rate-dependent coefficients from the owned profile without
    // advancing time or changing readiness/gains. Requires preparation; only
    // the three supported rates are accepted. Same-rate calls are exact no-ops.
    // Every failure preserves all state and future behavior. Like preparation,
    // this stopped/same-thread lifecycle action evaluates exponentials; it is
    // not part of advance_frame or a concurrent host/device change protocol.
    [[nodiscard]] Status reconfigure_sample_rate(double sample_rate) noexcept;

    [[nodiscard]] bool prepared() const noexcept { return prepared_; }
    [[nodiscard]] double readiness() const noexcept { return readiness_; }
    [[nodiscard]] PercussionDiagnostics diagnostics() const noexcept {
        return {prepared_, readiness_, sample_rate_};
    }

    // Read gain for sample n BEFORE advance_frame. The engine additionally gates
    // percussion on upper-B route eligibility and supplies the existing shared
    // second/third-harmonic contact audio independently of drawbar gain.
    // Disabled, invalid or unprepared settings produce zero percussion gain.
    [[nodiscard]] double gain(const PercussionSettings& settings) const noexcept;

    // Apply only to eligible upper-B sustained audio, never lower/manual-global
    // or percussion audio. Disabled, Soft, invalid or unprepared returns unity.
    // The engine separately masks the eligible sustained 1-foot branch while
    // retaining its physical contact and stored drawbar position.
    [[nodiscard]] double upper_sustain_gain(const PercussionSettings& settings) const noexcept;

    // Advance n -> n+1 AFTER rendering current q[n]. The detector is already
    // resolved by Engine: eligible && OR(upper physical contact index 8).
    // Active detector decays; an open detector recovers, including while routing
    // is ineligible. This held-key routing policy is nominal pending captures.
    // No event, route/tablet change, or newly joining note resets readiness.
    // A zero-frame host call must not call this method. Invalid settings,
    // unprepared use, or a connected detector with disabled percussion returns
    // false and changes nothing. Success advances exactly one sample.
    // Decay values below the smallest normal double are flushed to zero to
    // avoid persistent subnormal arithmetic; see the explicit numerical note.
    [[nodiscard]] bool advance_frame(bool routed_detector,
                                      const PercussionSettings& settings) noexcept;

private:
    PercussionProfile profile_{};
    double slow_decay_factor_{0.0};
    double fast_decay_factor_{0.0};
    double recovery_step_{0.0};
    double readiness_{0.0};
    double sample_rate_{0.0};
    bool prepared_{false};
};

} // namespace hammond
