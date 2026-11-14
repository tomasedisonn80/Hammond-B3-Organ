#pragma once

#include <cstddef>
#include <cstdint>
#include <memory>
#include <string>
#include <string_view>
#include <vector>

namespace hammond::standalone {

class MidiInbox;

inline constexpr std::string_view kMidiDeviceModelId =
    "standalone-rtmidi-short-input-v1";
inline constexpr std::size_t kMidiMaximumPorts = 256;
inline constexpr std::size_t kMidiMaximumPortNameBytes = 1024;
inline constexpr std::uint64_t kMidiConnectionPollMilliseconds = 250;
inline constexpr std::uint64_t kMidiCloseGuardWaitMilliseconds = 250;

enum class MidiDeviceState : std::uint8_t {
    Unavailable,
    Closed,
    Open,
    Disconnected,
    Faulted
};

struct MidiDeviceInfo {
    MidiDeviceState state{MidiDeviceState::Unavailable};
    std::string backend{}; // "ALSA", "WinMM", "CoreMIDI", or "unavailable".
    std::string port_name{}; // Exact selected backend name; never a hardware ID.
    std::uint32_t opened_port_index{0}; // Historical enumeration index at open.
    std::uint64_t generation{0}; // Successful opens; never wraps or resets.
};

// Lifetime counters survive close/reopen and saturate. Individual atomic reads
// may span a callback; this is diagnostic observation, not a coherent musical
// snapshot. No upstream allocation/latency guarantee is implied.
struct MidiDeviceDiagnostics {
    std::uint64_t callback_messages{0};
    std::uint64_t forwarded_messages{0};
    std::uint64_t filtered_messages{0};
    std::uint64_t admission_failures{0};
    std::uint64_t backend_errors{0};
    std::uint64_t callback_contentions{0};
    std::uint64_t disconnects{0};
    std::uint64_t close_errors{0};
    std::uint64_t last_arrival_ns{0}; // Absolute steady_clock acquisition time.
};

// Optional one-port transport. Every instance method, including diagnostics(),
// belongs to the main thread; the only concurrent access is its private input
// callback to the caller-owned MidiInbox and atomic diagnostic cells. No public
// method is an audio-callback operation. Construction, enumeration, open, poll,
// close and destruction may allocate, enter the OS or wait for native teardown.
//
// The inbox MUST outlive this device and all callbacks. Declare the inbox before
// the device in an owning aggregate, or explicitly close before either dies.
// This adapter never reads/changes Engine, UiModel, Session or note ownership.
// Main translates/drains and posts all musical commands through the sole Session
// producer. Backend callbacks never call Session::post().
//
// This header freezes implementation requirements. Platform close behavior and
// physical hotplug/timing require their own evidence; see docs/MIDI_BACKEND.md.
class MidiDevice {
public:
    MidiDevice();
    ~MidiDevice();
    MidiDevice(const MidiDevice&) = delete;
    MidiDevice& operator=(const MidiDevice&) = delete;
    MidiDevice(MidiDevice&&) = delete;
    MidiDevice& operator=(MidiDevice&&) = delete;

    // Compile-time availability of the selected platform backend. Does not
    // initialize MIDI, enumerate devices, probe permissions or imply hardware.
    [[nodiscard]] static bool backend_available() noexcept;
    [[nodiscard]] static std::string_view backend_name() noexcept;

    // Value-owned OS query, on the main thread or one exclusively owned discovery
    // worker. It creates/tears down its own RtMidi query object and never touches a live
    // MidiDevice. Success may return an empty list. Failure preserves
    // destination and reports an error; an unavailable build is a failure, not
    // a fabricated successful empty list. Retain exact UTF-8 backend names and
    // their order. More than 256 ports or a zero/overlong/NUL-containing name
    // rejects the complete enumeration. No silent truncation or backend retry.
    [[nodiscard]] static bool enumerate_input_ports(
        std::vector<std::string>& destination, std::string& error);

    // Refuses an already-open object, empty/invalid name, exhausted generation,
    // nonempty/faulted inbox or missing/ambiguous exact name. Enumeration indices
    // are resolved afresh; verify the chosen index/name immediately before and
    // after opening. Never default to port zero or a different backend/device.
    //
    // Install immutable callback/error context and ignore SysEx/clock/sensing
    // before activating input. Callback copies only complete 1..3-byte messages
    // with absolute steady-clock nanoseconds; it cannot log, allocate, lock,
    // inspect UI/Session, retain the vector, or throw. Reentrant input is a
    // fault, never a second producer of the SPSC inbox.
    //
    // Backend/open errors are returned with partial transport closed while the
    // inbox and callback context remain alive. If input activation was attempted,
    // failure faults that inbox epoch; main must retire it before trying again.
    // Routine argument rejection leaves the prior object/inbox unchanged.
    [[nodiscard]] bool open(MidiInbox& inbox, std::string_view exact_port_name,
                            std::string& error);

    // Main calls approximately every 250ms while open, and promptly on a latched
    // inbox/backend fault. A healthy uniquely present exact name returns true.
    // Missing/ambiguous name, enumeration failure, backend error or closed native
    // port latches a fault and closes/quiesces the transport before returning
    // false. Calling when already closed returns false without opening anything.
    //
    // Does NOT clear/discard/reset the inbox, post notes, reset an input decoder,
    // or reconnect. Main owns scoped release and next-epoch acknowledgment.
    // Name polling cannot detect every unplug/replug or certify physical identity.
    [[nodiscard]] bool poll_connection(std::string& error);

    // Idempotent main-thread teardown. First close admission and latch the
    // attached inbox's Disconnected fault, then close native input with context
    // alive, wait for entered callbacks to leave, and only then detach/cancel or
    // destroy backend callback storage. cancelCallback alone is NOT a join.
    // Keep close errors observable. Never reset or destroy the caller's inbox.
    // Caller may retire/reset an epoch only after actual quiescent close; native
    // driver failure must not be converted into an invented teardown success.
    // After the OS close returns, the adapter's entered-callback wait is bounded
    // to 250ms. Failure poisons this object, refuses reopen, and retains its one
    // callback context instead of freeing possibly referenced memory. The app
    // reports MIDI shutdown failure and requires process restart. This exceptional
    // retained object is not the ordinary close path; OS call duration itself is
    // outside the adapter's timing bound. See the contract for platform limits.
    void close() noexcept;

    [[nodiscard]] bool is_open() const noexcept;
    // True only with no live input source and no entered callback. A driver
    // teardown failure keeps this false, preventing unsafe inbox reuse. An
    // unopened/disabled device is quiescent. This is an adapter state claim,
    // separately qualified per native backend, not a physical hotplug result.
    [[nodiscard]] bool is_quiescent() const noexcept;
    [[nodiscard]] MidiDeviceInfo info() const;
    [[nodiscard]] MidiDeviceDiagnostics diagnostics() const noexcept;

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace hammond::standalone
