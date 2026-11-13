#pragma once

#include "hammond/ControlState.h"
#include "hammond/PerformanceInput.h"
#include "hammond/Profile.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <memory>
#include <span>
#include <string_view>
#include <variant>

namespace hammond::standalone {

inline constexpr std::string_view kSessionModelId =
    "standalone-callback-boundary-session-v1";
inline constexpr std::size_t kSessionCommandCapacity = 256;
inline constexpr std::size_t kSessionSnapshotReadAttempts = 8;
inline constexpr std::uint8_t kUiInputChannel = 0;

// UI owners use channel 0 on either origin bus. Other channels are independent.
// Distinct nonnegative note_id values distinguish simultaneous UI gestures.
struct ReleaseUiNotes {};
struct Panic {};

// Offset-zero input, one whole control restore, scoped UI release, or global
// panic. No pointer, parser, device handle, string, or dynamic payload is owned.
using SessionCommand =
    std::variant<PerformanceInputEvent, ControlSnapshot, ReleaseUiNotes, Panic>;

// Finite limits permit actual exhaustion tests. They never reset at prepare().
// publications must be <= UINT64_MAX / 2; zero is a valid exhausted limit.
struct SessionLimits {
    std::uint64_t command_sequences{std::numeric_limits<std::uint64_t>::max()};
    std::uint64_t publications{std::numeric_limits<std::uint64_t>::max() / 2};
};

enum class SessionStatus : std::uint8_t {
    Ok,
    NotPrepared,
    AlreadyRunning,
    NotRunning,
    InvalidSpec,
    InvalidProfile,
    InvalidBuffer,
    BlockTooLarge,
    TimelineOverflow,
    InvalidCommand,
    QueueFull,
    RecoveryPending,
    SequenceExhausted,
    CoreFailure
};

struct SubmitResult {
    SessionStatus status{SessionStatus::Ok};
    std::uint64_t sequence{0}; // Nonzero only for an accepted copied command.

    [[nodiscard]] constexpr bool ok() const noexcept {
        return status == SessionStatus::Ok;
    }
    [[nodiscard]] constexpr explicit operator bool() const noexcept { return ok(); }
};

struct RenderResult {
    SessionStatus status{SessionStatus::Ok};
    std::uint32_t frames_rendered{0};

    [[nodiscard]] constexpr bool ok() const noexcept {
        return status == SessionStatus::Ok;
    }
    [[nodiscard]] constexpr explicit operator bool() const noexcept { return ok(); }
};

enum class SessionFault : std::uint32_t {
    QueueOverflow = 1U << 0,
    RejectedCommand = 1U << 1,
    SequenceExhausted = 1U << 2,
    RenderRejected = 1U << 3,
    CoreFailure = 1U << 4
};

// One coherent copied observation. Held values are logical physical targets,
// not individual owners, contact positions or an audibility claim. Array key
// index is MIDI note minus kMinManualMidiNote; pedal index is PedalId minus one.
struct SessionSnapshot {
    ControlSnapshot controls{};
    std::array<std::array<bool, kManualKeyCount>, kManualCount> held_keys{};
    std::array<bool, kPedalCount> held_pedals{};
    std::uint64_t frame_clock{0};
    double sample_rate{0.0};
    float peak{0.0F}; // max(abs(sample)) of last positive successful callback.
    bool prepared{false};
    bool running{false};
    std::uint64_t publication_revision{0}; // Even; never wraps or resets.
    std::uint64_t resolved_sequence{0}; // Applied, rejected or discarded through here.
    std::uint64_t last_applied_sequence{0}; // Latest actually applied command only.
    std::uint64_t recovery_count{0}; // Completed emergency recoveries, not Panic actions.
    std::uint64_t queue_overflows{0};
    std::uint64_t rejected_commands{0};
    std::uint64_t discarded_commands{0};
    std::uint32_t fault_flags{0}; // Sticky bitwise SessionFault values.
    Status last_core_status{Status::Ok}; // Most recent non-Ok core result, if any.
};

// One main/UI producer, one serialized audio consumer. No other thread may call
// post(), prepare(), start() or stop(). read_snapshot() is the only concurrent
// observation of audio-owned state. No live Engine/ownership access is exposed.
//
// Constructor may allocate the PIMPL and throw std::bad_alloc. Construction,
// destruction and lifecycle calls require complete callback/reader quiescence.
// post(), render() and read_snapshot() allocate/destroy no dynamic resources,
// take no lock, perform no I/O and wait for no other thread. Copy/move is absent.
// This header freezes requirements; implementation/qualification are separate.
class Session {
public:
    explicit Session(SessionLimits limits = {});
    ~Session();
    Session(const Session&) = delete;
    Session& operator=(const Session&) = delete;
    Session(Session&&) = delete;
    Session& operator=(Session&&) = delete;

    // Stopped-only transaction. Uses Engine::prepare's nominal ideal contacts
    // and unchanged defaults; rates 44100/48000/96000 and block bounds follow
    // ProcessSpec. Success starts fresh DSP at spec.initial_frame, clears both
    // ledgers, discards pending commands and publishes a stopped snapshot.
    // Failure preserves prior music/queue/lifecycle. Counters remain lifetime
    // scoped. The app may explicitly post a proposed initial registration.
    [[nodiscard]] SessionStatus prepare(const RuntimeProfile& profile,
                                        const ProcessSpec& spec) noexcept;

    // Call start before activating the device. AlreadyRunning is a no-op error.
    // A stopped prepared session accepts commands for its next render boundary.
    [[nodiscard]] SessionStatus start() noexcept;

    // FIRST pause/close the actual device and prove callbacks have returned.
    // Session cannot stop a device or join a callback. Idempotent after prepare;
    // clears all owners/contacts and pending commands at zero elapsed frames,
    // retaining controls, source phases, readiness and frame clock. Publishes
    // stopped state with peak zero. No phase reset or wall-clock catch-up.
    [[nodiscard]] SessionStatus stop() noexcept;

    // One producer; copies one command. Accepted means queued, not applied.
    // FIFO sequence starts at one and never wraps. Nonzero input offsets,
    // forbidden physical Event alternatives and invalid ControlSnapshots reject
    // immediately; other core payload/owner admission happens at the boundary.
    // QueueFull requests out-of-queue GLOBAL recovery, and further posts return
    // RecoveryPending until its acknowledgment. Sequence exhaustion likewise
    // releases owners but permanently rejects new commands for this object.
    [[nodiscard]] SubmitResult post(const SessionCommand& command) noexcept;

    // Sole audio context; requires start(). Exact 2*frames float samples, with
    // frames <= prepared max_block_frames. Empty span is valid only at frames=0.
    // Invalid calls preserve caller output, pending commands and musical state;
    // the device adapter must silence its own buffer after a failed result.
    // At entry freeze one queued prefix (<=256), recover if requested, then
    // apply its FIFO commands at offset zero before processing any sample.
    // Concurrent later posts remain for a later call. Stereo is literal L=R
    // copies of Engine mono, without clipping, gain, resampling or extra DSP.
    // Zero frames flush commands without advancing time or replacing peak.
    // Every successful call publishes controls, holds, clock, peak and faults
    // coherently. See docs/STANDALONE_SESSION.md for command-failure recovery.
    [[nodiscard]] RenderResult render(std::uint32_t frames,
                                      std::span<float> interleaved_stereo) noexcept;

    // At most eight attempts, atomic payload cells plus coherent revision.
    // Busy/exhausted publication returns false and preserves destination.
    // Additional serialized readers are permitted; no ordinary payload may be
    // read concurrently with a write merely because a revision was checked.
    [[nodiscard]] bool read_snapshot(SessionSnapshot& destination) const noexcept;

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace hammond::standalone
