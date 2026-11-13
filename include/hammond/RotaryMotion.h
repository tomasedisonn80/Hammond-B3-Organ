#pragma once

#include "hammond/RotaryTypes.h"

namespace hammond::rotary {

// The separately reported increment preserves observable tiny motion even when
// its addition to an existing phase cannot be represented by binary64.
struct MotionEvaluation {
    MotionState state{};
    double angle_increment_rad{0.0}; // Signed, before phase wrapping.
    [[nodiscard]] bool operator==(const MotionEvaluation&) const noexcept = default;
};

// These check kinematics only. They do not admit full radiation geometry,
// authoring provenance, an acoustic history or a measured motor model.
[[nodiscard]] Status validate_motion_profile(const MotionProfile& profile) noexcept;
[[nodiscard]] Status validate_motion_state(const MotionState& state) noexcept;

// Every rejected operation preserves its output. Initial turn counts may be
// nonzero for composition and stopped rate changes. The chosen tau follows the
// sign of target minus initial speed; equal speed selects the upward tau.
[[nodiscard]] Status make_motion_segment(const MotionProfile& profile,
                                         const MotionState& initial,
                                         SpeedCommand command,
                                         std::uint64_t anchor_frame,
                                         MotionSegment& destination) noexcept;

// Pure physical-time evaluation for 0 <= elapsed_s <= kMaxEpochSeconds.
// The segment anchor is checked against the largest admitted epoch; its rate-
// specific meaning is checked by evaluate_motion_segment_at instead.
[[nodiscard]] Status evaluate_motion_segment(const MotionSegment& segment,
                                             double elapsed_s,
                                             MotionEvaluation& destination) noexcept;

// Evaluate a retained constant-command segment at a floor-index plus fraction.
// Positive times preceding its anchor return InsufficientHistory. Split integer
// frame differences retain fractional timing near the end of a long epoch.
[[nodiscard]] Status evaluate_motion_segment_at(const MotionSegment& segment,
                                                SamplePosition position,
                                                double sample_rate,
                                                MotionState& destination) noexcept;

// Explicit startup/rate-epoch history: uniform motion at the epoch seed's speed.
// Physical-time input is in [-kMaxEpochSeconds,0]. Sample positions use the
// corresponding negative epoch range and may include exactly frame zero.
[[nodiscard]] Status evaluate_motion_prehistory(const MotionState& epoch_initial,
                                               std::int8_t direction,
                                               double seconds_before_zero,
                                               MotionEvaluation& destination) noexcept;
[[nodiscard]] Status evaluate_motion_prehistory_at(const MotionState& epoch_initial,
                                                  std::int8_t direction,
                                                  SamplePosition position,
                                                  double sample_rate,
                                                  MotionState& destination) noexcept;

// One serialized kinematic owner. All methods are allocation-free and bounded;
// rejections preserve the complete object and caller destinations. This retains
// only the current event anchor. A separate renderer/history owner retains older
// anchors or per-frame snapshots and chooses the correct one for a past query.
class RotaryMotion {
public:
    [[nodiscard]] bool operator==(const RotaryMotion&) const noexcept = default;
    // Preparation starts at frame zero with zero completed turns. It replaces
    // the original reset seed only after every argument has been admitted.
    [[nodiscard]] Status prepare(const MotionProfile& profile,
                                  double initial_phase_rad,
                                  double initial_speed_rad_s,
                                  SpeedCommand initial_command,
                                  double sample_rate) noexcept;
    [[nodiscard]] bool prepared() const noexcept { return prepared_; }
    [[nodiscard]] double sample_rate() const noexcept { return sample_rate_; }
    [[nodiscard]] std::uint64_t frame() const noexcept { return frame_; }
    [[nodiscard]] std::uint64_t max_frame() const noexcept { return max_frame_; }
    [[nodiscard]] MotionProfile profile() const noexcept { return profile_; }
    [[nodiscard]] MotionState state() const noexcept { return state_; }
    [[nodiscard]] MotionState epoch_initial_state() const noexcept { return epoch_initial_; }
    [[nodiscard]] SpeedCommand command() const noexcept { return command_; }
    [[nodiscard]] MotionSegment segment() const noexcept { return segment_; }

    // Advancing or commanding a frame before frame() is rejected. An unchanged
    // command can advance the observation, but never replaces its event anchor.
    [[nodiscard]] Status advance_to(std::uint64_t frame) noexcept;
    [[nodiscard]] Status apply_command(std::uint64_t frame, SpeedCommand command) noexcept;

    // Read-only prediction is allowed through max_frame(). Earlier positive
    // segments require external history; negative time always uses epoch_initial.
    [[nodiscard]] Status state_at(SamplePosition position, MotionState& destination) const noexcept;

    // Reset uses the originally prepared seed/command at the CURRENT rate.
    // A stopped rate change instead preserves current state/command, starts a
    // new frame-zero epoch and changes its negative-time seed. Acoustic history
    // replacement belongs to the enclosing renderer, outside this class.
    [[nodiscard]] Status reset() noexcept;
    [[nodiscard]] Status reconfigure_sample_rate(double sample_rate) noexcept;

private:
    MotionProfile profile_{};
    MotionState original_initial_{};
    MotionState epoch_initial_{};
    MotionState state_{};
    MotionSegment segment_{};
    SpeedCommand original_command_{SpeedCommand::Chorale};
    SpeedCommand command_{SpeedCommand::Chorale};
    double sample_rate_{0.0};
    std::uint64_t frame_{0};
    std::uint64_t max_frame_{0};
    bool prepared_{false};
};

} // namespace hammond::rotary
