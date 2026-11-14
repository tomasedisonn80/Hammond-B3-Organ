#pragma once

#include "hammond/RotaryMotion.h"

#include <array>
#include <cstddef>
#include <cstdint>

// Independent R4 streaming storage. This does not replace R3's borrowed,
// immutable MotionHistoryView or change the default Engine signal path.
// Contract: docs/ROTARY_RENDERER_CONTRACT.md / rotary-numerics-v1.
namespace hammond::rotary {

class RotaryRenderer;
namespace detail {
struct RotaryRendererTestAccess;
}

// Samples are ordered x[k-1], x[k], x[k+1], x[k+2]. The pure kernel admits
// fraction in [0,1], including the next integer endpoint for characterization;
// SamplePosition-based queries remain canonical in [0,1). Samples must be finite
// in [-1,1]. All reads precede publication, so destination may alias one sample.
// Rejection preserves destination. There is no clipping or normalization.
[[nodiscard]] Status interpolate_cubic_lagrange(const std::array<double, 4>& samples,
                                               double fraction,
                                               double& destination) noexcept;

// Fixed owned backing storage: no method allocates. The active capacity is
// chosen during preparation; unused slots are not queryable. This is a large
// value type; the renderer places it in prepared heap storage, never on its
// process stack. Copies own independent sample bytes and are allocation-free.
class WaveformHistory {
public:
    [[nodiscard]] bool operator==(const WaveformHistory&) const noexcept = default;
    [[nodiscard]] Status prepare(double sample_rate, std::size_t capacity_frames) noexcept;
    [[nodiscard]] Status reset() noexcept;
    [[nodiscard]] bool prepared() const noexcept { return prepared_; }
    [[nodiscard]] double sample_rate() const noexcept { return sample_rate_; }
    [[nodiscard]] std::size_t capacity_frames() const noexcept { return capacity_frames_; }
    [[nodiscard]] std::uint64_t next_frame() const noexcept { return next_frame_; }
    [[nodiscard]] std::uint64_t oldest_frame() const noexcept {
        return next_frame_ > capacity_frames_ ? next_frame_ - capacity_frames_ : 0;
    }

    // Append exactly one finite [-1,1] sample at next_frame(), then advance it.
    // Negative indices inside the epoch are declared zero. A nonnegative index
    // outside [oldest_frame(),next_frame()) returns InsufficientHistory.
    [[nodiscard]] Status push(double sample) noexcept;
    [[nodiscard]] Status sample_at(std::int64_t frame, double& destination) const noexcept;
    // All four nodes must exist, including zero-weight nodes at an endpoint.
    [[nodiscard]] Status interpolate(SamplePosition position, double& destination) const noexcept;

private:
    friend class RotaryRenderer;
    friend struct detail::RotaryRendererTestAccess;
    std::array<double, kMaxHistoryFrames> samples_{};
    double sample_rate_{0.0};
    std::size_t capacity_frames_{0};
    std::uint64_t next_frame_{0};
    std::uint64_t max_frame_{0};
    bool prepared_{false};
};

// One original event-anchored MotionSegment per retained integer interval.
// Appending at n records the owning segment for [n,n+1), without changing its
// anchor or initial state. A floor-index query is O(1), even after arbitrarily
// many events within the admitted epoch. No event queue grows with duration.
// This is also a large fixed-storage value type: place it and any whole-history
// test snapshots on the heap, particularly on platforms with a 1 MiB stack.
class MotionFrameHistory {
public:
    [[nodiscard]] bool operator==(const MotionFrameHistory&) const noexcept = default;
    // The owner must be prepared at frame zero. Copies its epoch metadata;
    // retains no reference to the owner and allocates no storage.
    [[nodiscard]] Status prepare(const RotaryMotion& owner, std::size_t capacity_frames) noexcept;
    [[nodiscard]] bool prepared() const noexcept { return prepared_; }
    [[nodiscard]] double sample_rate() const noexcept { return sample_rate_; }
    [[nodiscard]] MotionProfile profile() const noexcept { return profile_; }
    [[nodiscard]] MotionState epoch_initial_state() const noexcept { return epoch_initial_; }
    [[nodiscard]] std::size_t capacity_frames() const noexcept { return capacity_frames_; }
    [[nodiscard]] std::uint64_t next_frame() const noexcept { return next_frame_; }
    [[nodiscard]] std::uint64_t oldest_frame() const noexcept {
        return next_frame_ > capacity_frames_ ? next_frame_ - capacity_frames_ : 0;
    }

    // The matching owner must be observed at next_frame(), after all commands
    // at that boundary. Exact continuity and the next endpoint are admitted
    // before writing. Repeated/equal-frame events are already owned by motion.
    [[nodiscard]] Status append(const RotaryMotion& owner) noexcept;
    // Positive coverage is [oldest_frame(),next_frame()], including only the
    // exact final boundary. An empty history admits {0,0}. The final boundary
    // uses the last retained segment; negative time uses the epoch seed.
    [[nodiscard]] Status state_at(SamplePosition position, MotionState& destination) const noexcept;

private:
    friend class RotaryRenderer;
    friend struct detail::RotaryRendererTestAccess;
    std::array<MotionSegment, kMaxHistoryFrames> segments_{};
    MotionProfile profile_{};
    MotionState epoch_initial_{};
    double sample_rate_{0.0};
    std::size_t capacity_frames_{0};
    std::uint64_t next_frame_{0};
    std::uint64_t max_frame_{0};
    bool prepared_{false};
};

} // namespace hammond::rotary
