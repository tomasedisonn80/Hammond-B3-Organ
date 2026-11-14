#pragma once

#include "hammond/ParameterBridge.h"
#include "hammond/PerformanceInput.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <span>
#include <string_view>
#include <variant>

namespace hammond {

inline constexpr std::string_view kHostTimelineModelId =
    "bounded-linear-host-timeline-v1";
inline constexpr std::size_t kMaxHostStateRestores = 4;

// A callback-local, signed sample offset. Positive callbacks admit 0..N:
// N is both a curve endpoint and a retained next-callback boundary point.
// Zero-frame callbacks admit only zero and apply it once, without carrying it.
struct HostParameterPoint {
    std::int32_t offset{0};
    double normalized{0.0};
};

// Views are borrowed only for process(); no pointer into host storage survives.
// IDs must be one of the 47 compiled descriptors. Duplicate queues reject,
// including duplicate empty queues; points are nondecreasing, with last-wins
// ties. Values must be finite and in [0,1].
struct HostParameterQueue {
    std::uint32_t parameter_id{0};
    std::span<const HostParameterPoint> points{};
};

using HostMusicalEvent = std::variant<HostNoteEvent, PedalNoteEvent>;

struct HostParameterCarry {
    std::uint32_t parameter_id{0};
    double normalized{0.0};

    [[nodiscard]] bool operator==(const HostParameterCarry&) const noexcept = default;
};

// Every raw endpoint record is retained, including last-wins parameter ties.
// Musical alternatives have offset zero. This makes the 1024-record carry plus
// fresh-work budget observable and avoids silently discarding boundary work.
using HostCarryEvent = std::variant<HostParameterCarry, HostNoteEvent, PedalNoteEvent>;

struct HostTimelineResult {
    Status status{Status::Ok};
    std::uint32_t input_records_consumed{0};
    std::uint32_t carried_records_consumed{0};
    std::uint32_t restores_consumed{0};
    std::uint32_t physical_events_applied{0};
    std::uint32_t engine_calls{0};

    [[nodiscard]] constexpr bool ok() const noexcept { return status == Status::Ok; }
    [[nodiscard]] constexpr explicit operator bool() const noexcept { return ok(); }
};

// Single-processing-thread runtime with fixed live/candidate Engine, ownership,
// anchors, boundary records and private output storage. Allocate/construct the
// object outside the audio callback. No method below allocates or performs I/O.
// There is no native SDK, file parser, concurrent UI access or state queue here.
// The native wrapper validates/peeks its state queue before process(), supplies
// at most four copied snapshots, and acknowledges/publishes only after success.
class HostTimeline {
public:
    HostTimeline() noexcept = default;

    // Fresh successful preparation starts a new epoch. The Engine is prepared
    // for 65536 frames; spec.max_block_frames is this host's active callback
    // limit, in 1..65536. Invalid preparation preserves all live state.
    [[nodiscard]] Status prepare(const RuntimeProfile& profile,
                                 const ProcessSpec& spec) noexcept;
    [[nodiscard]] Status prepare(const RuntimeProfile& profile,
                                 const ProcessSpec& spec,
                                 const ConsoleModel& console_model) noexcept;

    // Quiescent/same-thread lifecycle change: preserve source/console/owner
    // history, normalized anchors and carry. No reseed or simulated catch-up.
    [[nodiscard]] Status reconfigure(double sample_rate,
                                     std::uint32_t max_block_frames) noexcept;

    // Total fresh points + fresh musical records + retained carry <=1024.
    // Queue count <=47; state restores <=4. Musical offsets are globally sorted
    // in 0..N. All payload/identity/capacity/control/output/clock errors reject
    // the whole callback, preserving live state and every caller output sample.
    // Counts are all zero on failure; only opaque fixed scratch may change.
    //
    // Restores run first, preserving histories and resetting all curve anchors:
    // remembered bank for old bank IDs, effective selection for new preset IDs.
    // Carried parameter points at0 precede new points at0 for that ID. Evaluate
    // all curves in parameter-ID order before musical events at that sample.
    // Carried musical events precede fresh same-offset music; each list is stable.
    // Previous raw rendered values form sample-1 anchors; absent queues hold
    // them without reasserting commands. Ordinary callback completion does not
    // derive anchors from applied controls. Discrete conversion is delegated to
    // ParameterBridge, including its frozen binary64 preset thresholds.
    // An explicit point applies its control even if its plain value is unchanged
    // (an old bank point clears fixed mode and reconnects its manual route).
    // The higher-ID new preset command runs after old bank controls at a tie;
    // unchanged interpolation plateaus do not reassert either selection.
    //
    // Candidate-only slices sum to N; bounded zero-frame flushes may handle a
    // dense same-sample group. Caller output, Engine, owners, anchors and carry
    // commit only after every slice succeeds. Empty output still advances time.
    [[nodiscard]] HostTimelineResult process(
        std::uint32_t frames, std::span<float> mono_output,
        std::span<const HostParameterQueue> parameter_queues,
        std::span<const HostMusicalEvent> musical_events,
        std::span<const ControlSnapshot> restores = {}) noexcept;

    // Change only the destination of future manual owners. Existing releases
    // retain their original manual. Requires stopped/same-thread access.
    [[nodiscard]] bool set_manual_bus_route(std::uint32_t bus, Manual manual) noexcept;

    [[nodiscard]] const Engine& engine() const noexcept { return engine_; }
    [[nodiscard]] const NoteOwnership& manual_ownership() const noexcept { return manual_; }
    [[nodiscard]] const PedalNoteOwnership& pedal_ownership() const noexcept { return pedal_; }
    [[nodiscard]] std::uint32_t max_block_frames() const noexcept { return max_block_frames_; }
    [[nodiscard]] std::size_t carry_count() const noexcept { return retained_.carry_count; }
    // Checked copied diagnostics, never concurrent UI publication. An anchor
    // is the last raw normalized curve value, not the current applied route.
    [[nodiscard]] bool normalized_anchor(std::uint32_t parameter_id,
                                          double& destination) const noexcept;
    [[nodiscard]] bool carry_event(std::size_t index, HostCarryEvent& destination) const noexcept;

private:
    struct Retained {
        std::array<double, kParameterCount> anchors{};
        std::array<HostCarryEvent, kMaxEventsPerBlock> carry{};
        std::size_t carry_count{0};
    };

    struct Workspace {
        Engine engine{};
        NoteOwnership manual{};
        PedalNoteOwnership pedal{};
        Retained retained{};
        std::array<float, kHardMaxBlockFrames> mono{};
        std::array<Event, kMaxEventsPerBlock> events{};
    };

    Engine engine_{};
    NoteOwnership manual_{};
    PedalNoteOwnership pedal_{};
    Retained retained_{};
    std::uint32_t max_block_frames_{0};
    Workspace work_{};
};

} // namespace hammond
