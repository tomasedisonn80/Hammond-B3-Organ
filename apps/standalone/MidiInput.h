#pragma once

#include "Session.h"

#include <array>
#include <atomic>
#include <cstddef>
#include <cstdint>
#include <span>
#include <string_view>
#include <type_traits>
#include <variant>

namespace hammond::standalone {

inline constexpr std::string_view kMidiInputModelId =
    "standalone-three-division-midi-v1";
inline constexpr std::size_t kMidiInboxCapacity = 256;
inline constexpr std::size_t kMidiDrainBudget = 32;
inline constexpr std::array<std::uint8_t, 3> kMidiOwnerChannels{1, 2, 3};
inline constexpr std::uint8_t kMidiPedalFirstNote = 36;
inline constexpr std::uint8_t kMidiPedalLastNote = 60;

// Complete backend messages, not a running-status byte stream. size is 1..3;
// unused bytes are zeroed by the inbox. Time is steady-clock nanoseconds at
// receipt, used only for diagnostics: it is NOT an Engine frame or deadline.
struct MidiPacket {
    std::array<std::uint8_t, 3> bytes{};
    std::uint8_t size{0};
    std::uint64_t arrival_ns{0};
};

enum class MidiPushResult : std::uint8_t {
    Accepted,
    InvalidSize,
    Faulted,
    Overflow
};

enum class MidiInboxFault : std::uint32_t {
    Overflow = 1U << 0,
    Backend = 1U << 1,
    Disconnected = 1U << 2
};

// Lifetime counters saturate rather than wrap. Live observation is a collection
// of independent atomic counters, not one transactional arrival-time snapshot.
struct MidiInboxDiagnostics {
    std::uint64_t received_packets{0};
    std::uint64_t accepted_packets{0};
    std::uint64_t invalid_size_packets{0};
    std::uint64_t faulted_packets{0};
    std::uint64_t overflow_events{0};
    std::uint64_t popped_packets{0};
    std::uint64_t discarded_packets{0};
    std::uint64_t resets{0};
    std::uint32_t faults{0};
};

// Exactly one backend producer and one main-thread consumer. This queue does
// not enter Session or own any device, UI, Engine, string, lock or allocation.
// signal_fault is the only operation also allowed from an error-reporting
// thread; it sets atomic bits and never changes queue indices or payload.
//
// A full queue faults the entire device epoch. Once faulted, push/pop admit no
// further packets. A packet racing fault publication may already have been
// returned to the consumer; the main thread's subsequent scoped release retires
// its owners too. This is an observable discontinuity, not lossless delivery.
// reset_quiescent may run ONLY after the backend has joined every callback and
// the sole consumer has stopped. It discards the old epoch and retains counters.
class MidiInbox {
public:
    MidiInbox() noexcept = default;
    MidiInbox(const MidiInbox&) = delete;
    MidiInbox& operator=(const MidiInbox&) = delete;
    MidiInbox(MidiInbox&&) = delete;
    MidiInbox& operator=(MidiInbox&&) = delete;

    // Producer only. Fault check precedes size admission. Empty or >3-byte
    // messages reject/count without storing data. No running-status assembly,
    // SysEx accumulation, parsing, waiting, allocation, I/O or Session call.
    [[nodiscard]] MidiPushResult push(std::span<const std::uint8_t> bytes,
                                      std::uint64_t arrival_ns) noexcept;

    // Consumer only. Empty/faulted returns false and preserves destination.
    // FIFO order; never sorts timestamps or overwrites an unread slot.
    [[nodiscard]] bool pop(MidiPacket& destination) noexcept;
    void signal_fault(MidiInboxFault fault) noexcept;
    [[nodiscard]] std::uint32_t faults() const noexcept;

    // Consumer only: bounded momentary size, exact with producer quiesced.
    [[nodiscard]] std::size_t pending() const noexcept;
    [[nodiscard]] MidiInboxDiagnostics diagnostics() const noexcept;
    void reset_quiescent() noexcept;

private:
    // One unused slot distinguishes empty/full without unbounded sequence IDs.
    std::array<MidiPacket, kMidiInboxCapacity + 1> packets_{};
    std::atomic<std::uint32_t> write_index_{0};
    std::atomic<std::uint32_t> read_index_{0};
    std::atomic<std::uint32_t> fault_bits_{0};
    std::atomic<std::uint64_t> received_packets_{0};
    std::atomic<std::uint64_t> accepted_packets_{0};
    std::atomic<std::uint64_t> invalid_size_packets_{0};
    std::atomic<std::uint64_t> faulted_packets_{0};
    std::atomic<std::uint64_t> overflow_events_{0};
    std::atomic<std::uint64_t> popped_packets_{0};
    std::atomic<std::uint64_t> discarded_packets_{0};
    std::atomic<std::uint64_t> resets_{0};
};

// User-facing MIDI channel numbers are ONE-based. Three distinct choices from
// 1..16, mapped to fixed internal namespaces above; UI remains channel zero.
// Routing is immutable during an active device epoch. This is one input port,
// not arbitrary simultaneous sixteen-channel or multiple-device routing.
struct MidiRouting {
    std::uint8_t upper_channel{1};
    std::uint8_t lower_channel{2};
    std::uint8_t pedal_channel{3};

    [[nodiscard]] bool operator==(const MidiRouting&) const noexcept = default;
};

[[nodiscard]] bool valid_midi_routing(const MidiRouting& routing) noexcept;

// A main-thread control edit, NOT a separately posted Session Event. Apply it
// through UiModel's shared desired-control state, then dispatch its normal
// ControlSnapshot action/submission acknowledgment. Otherwise a later UI edit
// could silently overwrite an accepted CC with a stale complete snapshot.
struct MidiParameterEdit {
    std::uint32_t parameter_id{0};
    double normalized{0.0};
};

using MidiAction = std::variant<SessionCommand, MidiParameterEdit>;

enum class MidiDecodeStatus : std::uint8_t {
    Action,
    Unsupported,
    UnmappedChannel,
    OutOfRange,
    Malformed,
    Inactive
};

struct MidiDecoded {
    MidiDecodeStatus status{MidiDecodeStatus::Inactive};
    MidiAction action{}; // Relevant ONLY when status == Action.
    std::uint64_t arrival_ns{0};
    bool timestamp_regressed{false};
};

struct MidiInputDiagnostics {
    std::uint64_t packets{0};
    std::uint64_t actions{0};
    std::uint64_t unsupported{0};
    std::uint64_t unmapped_channels{0};
    std::uint64_t out_of_range{0};
    std::uint64_t malformed{0};
    std::uint64_t inactive{0};
    std::uint64_t timestamp_regressions{0};
    std::uint64_t epochs{0};
};

// Main thread only, fixed storage. Pop/decode at most kMidiDrainBudget packets
// per UI-loop turn, dispatching each successful action before decoding the next.
// Stop at the first inbox/Session fault; never batch-and-truncate note releases.
// Notes use existing anonymous FIFO owners (note_id=-1); no per-pitch duplicate
// coalescing, steady-velocity gain, source reset or private note ledger is added.
class MidiInput {
public:
    // Reject invalid routing or an already active epoch without changing any
    // state/counter. The caller must first retire the preceding epoch's owners,
    // quiesce/reset its inbox and complete the release acknowledgment barrier.
    [[nodiscard]] bool begin_epoch(const MidiRouting& routing = {}) noexcept;
    // Stops translation and clears only timestamp comparison history. It does
    // not close hardware, reset the inbox or post any musical command.
    void end_epoch() noexcept;
    [[nodiscard]] bool active() const noexcept { return active_; }
    [[nodiscard]] const MidiRouting& routing() const noexcept { return routing_; }

    // Exactly one complete packet becomes zero or one action. Canonical notes
    // and CC123 release use SessionCommand; CC11/manual-B drawbars/pedal values
    // use MidiParameterEdit. All other voice/system messages are unsupported.
    // Arrival order wins over regressing/equal timestamps; offsets are zero.
    [[nodiscard]] MidiDecoded decode(const MidiPacket& packet) noexcept;
    [[nodiscard]] const MidiInputDiagnostics& diagnostics() const noexcept {
        return diagnostics_;
    }

private:
    MidiRouting routing_{};
    MidiInputDiagnostics diagnostics_{};
    std::uint64_t last_arrival_ns_{0};
    bool have_arrival_{false};
    bool active_{false};
};

// Fixed retirement sequence: upper(bus0,channel1), lower(bus1,channel2), then
// pedals(bus0,channel3), all at offset zero. These are scoped AllNotesOff input
// events, never Panic/ReleaseUiNotes or an Engine-wide physical release.
// Submit in order once; any failed submit enters existing Session recovery.
[[nodiscard]] std::array<SessionCommand, 3> midi_release_commands() noexcept;

static_assert(std::atomic<std::uint32_t>::is_always_lock_free,
              "MIDI inbox requires lock-free 32-bit atomics");
static_assert(std::atomic<std::uint64_t>::is_always_lock_free,
              "MIDI diagnostics require lock-free 64-bit atomics");
static_assert(std::is_trivially_copyable_v<MidiPacket>);
static_assert(std::is_trivially_copyable_v<MidiParameterEdit>);
static_assert(kMidiInboxCapacity < UINT32_MAX);
static_assert(kMidiOwnerChannels[0] != kUiInputChannel &&
              kMidiOwnerChannels[1] != kUiInputChannel &&
              kMidiOwnerChannels[2] != kUiInputChannel);

} // namespace hammond::standalone
