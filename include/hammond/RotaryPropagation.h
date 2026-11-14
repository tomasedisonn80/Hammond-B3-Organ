#pragma once

#include "hammond/RotaryMotion.h"

#include <span>

// Independent nominal M7 history and direct-path primitives. These do not
// render waveforms, add algorithmic latency or connect the Engine audio path.
// Contract: docs/ROTARY_PROPAGATION_CONTRACT.md / rotary-numerics-v1.
namespace hammond::rotary {

inline constexpr std::size_t kMaxMotionSegments = 4097;

// Borrowed immutable storage: the segment objects must outlive every copy of
// this view and every prepared path. Moving/reallocating or mutating that
// storage invalidates the contract. Preparation validates once, without
// allocating. Queries use at most 13 binary-search comparisons.
class MotionHistoryView {
public:
    [[nodiscard]] Status prepare(const MotionProfile& profile,
                                  const MotionState& epoch_initial,
                                  double sample_rate,
                                  std::span<const MotionSegment> segments,
                                  std::uint64_t through_frame) noexcept;
    [[nodiscard]] bool prepared() const noexcept { return prepared_; }
    [[nodiscard]] double sample_rate() const noexcept { return sample_rate_; }
    [[nodiscard]] MotionProfile profile() const noexcept { return profile_; }
    [[nodiscard]] MotionState epoch_initial_state() const noexcept { return epoch_initial_; }
    [[nodiscard]] std::uint64_t through_frame() const noexcept { return through_frame_; }
    [[nodiscard]] Status state_at(SamplePosition position, MotionState& destination) const noexcept;

private:
    std::span<const MotionSegment> segments_{};
    MotionProfile profile_{};
    MotionState epoch_initial_{};
    double sample_rate_{0.0};
    std::uint64_t through_frame_{0};
    bool prepared_{false};
};

// Direction is fixed at -1 or +1. Both vectors are staged before publication;
// identical destinations reject with InvalidBuffer. An origin may alias a
// destination because all input reads finish before either output is written.
[[nodiscard]] Status evaluate_circular_source(const Vec3& origin_m, double radius_m,
                                               const MotionState& state,
                                               std::int8_t direction,
                                               Vec3& position_m,
                                               Vec3& velocity_m_s) noexcept;

// A small view copy retains the caller's storage lifetime requirement, not the
// lifetime of the original MotionHistoryView object. All failures preserve the
// complete prepared object and caller outputs. No query allocates or mutates.
class PreparedRetardedPath {
public:
    [[nodiscard]] Status prepare(const MotionHistoryView& history,
                                  const Vec3& origin_m, double radius_m,
                                  const MicrophoneProfile& microphone,
                                  double sound_speed_m_s,
                                  double reference_distance_m) noexcept;
    [[nodiscard]] bool prepared() const noexcept { return prepared_; }
    [[nodiscard]] PathBounds bounds() const noexcept { return bounds_; }
    [[nodiscard]] Status solve(SamplePosition observation, PathResult& result,
                               SamplePosition& emission) const noexcept;

private:
    MotionHistoryView history_{};
    Vec3 origin_m_{};
    MicrophoneProfile microphone_{};
    PathBounds bounds_{};
    double radius_m_{0.0};
    double sound_speed_m_s_{0.0};
    double reference_distance_m_{0.0};
    bool prepared_{false};
};

} // namespace hammond::rotary
