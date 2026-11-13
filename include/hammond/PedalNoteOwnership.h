#pragma once

#include "hammond/PedalRouting.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <span>
#include <string_view>

namespace hammond {

inline constexpr std::size_t kPedalInputBusCount = 2;
inline constexpr std::size_t kPedalInputChannelCount = 16;
inline constexpr std::size_t kMaxPedalNoteOwners = 256;
inline constexpr std::string_view kPedalNoteOwnershipModelId =
    "bounded-fifo-pedal-note-ownership-v1";

enum class PedalNoteKind : std::uint8_t { On = 0, Off = 1, AllNotesOff = 2 };

// Typed logical input, not a MIDI packet or a native host bus number. The two
// origin buses are independent ownership namespaces targeting the same pedals.
// Positive calls require offset < frames; zero-frame flushes require offset 0.
// On/Off: explicit PedalId 1..25, note_id == -1 (anonymous) or >= 0. On accepts
// velocity 0..127; zero means release. Off requires velocity zero.
// AllNotesOff: pedal.value=0, velocity=0, note_id=-1; bus/channel select scope.
struct PedalNoteEvent {
    std::uint32_t offset{0};
    PedalNoteKind kind{PedalNoteKind::On};
    std::uint8_t bus{0};
    std::uint8_t channel{0};
    PedalId pedal{1};
    std::uint8_t velocity{0};
    std::int32_t note_id{-1};
};

struct PedalNoteOwnershipResult {
    Status status{Status::Ok};
    std::uint32_t input_consumed{0};
    std::uint32_t output_events{0};

    [[nodiscard]] constexpr bool ok() const noexcept { return status == Status::Ok; }
    [[nodiscard]] constexpr explicit operator bool() const noexcept { return ok(); }
};

// Surviving insertion order is observable, including repeated anonymous owners.
struct PedalOwnerSnapshot {
    std::uint8_t bus{0};
    std::uint8_t channel{0};
    PedalId pedal{};
    std::int32_t note_id{-1};

    [[nodiscard]] bool operator==(const PedalOwnerSnapshot&) const noexcept = default;
};

// Value-owned fixed storage, initially empty. This adapter owns no Engine,
// source phase, clock, controls or contacts. Use on the processing thread or
// while stopped; it is not a concurrent UI publication protocol.
class PedalNoteOwnership {
public:
    // First physical owner emits PedalOn; the final owner emits PedalOff. All
    // output uses canonical Manual::Lower and explicit one-based pedal indices.
    // Identified duplicate On is idempotent; conflicting reuse of an ID within
    // one bus/channel rejects. Anonymous releases are FIFO in bus/channel/pedal.
    // Missing releases are accepted no-ops. Channel panic removes only matching
    // owners and emits individual final releases, never PedalAllNotesOff.
    //
    // Entire-call transaction, matching NoteOwnership admission order:
    // BlockTooLarge for frames > 65536; then TooManyEvents for >1024 inputs;
    // then InvalidEvent for any payload, sorted-order or offset failure;
    // then candidate simulation in supplied order detects identity conflicts
    // (InvalidEvent) or owner/output capacity (TooManyEvents). Maximum 256
    // simultaneous owners and 1024 output events, even with a larger span.
    // Failure changes neither this object nor any output and reports zero
    // counts. Success writes only the emitted prefix and preserves its tail.
    //
    // Success commits this adapter only, without calling Engine. A combined
    // input transaction must translate on a copy and install it only after
    // Engine accepts every resulting note and control event. No allocation,
    // deallocation, locking, I/O, parsing or source advancement occurs here.
    [[nodiscard]] PedalNoteOwnershipResult translate(
        std::uint32_t frames, std::span<const PedalNoteEvent> input,
        std::span<Event> output) noexcept;

    [[nodiscard]] std::size_t owner_count() const noexcept { return owner_count_; }
    // Invalid queries preserve destination.
    [[nodiscard]] bool owner_count(PedalId pedal,
                                    std::size_t& destination) const noexcept;
    [[nodiscard]] bool owner_snapshot(std::size_t index,
                                      PedalOwnerSnapshot& destination) const noexcept;

    [[nodiscard]] bool operator==(const PedalNoteOwnership&) const noexcept = default;

private:
    [[nodiscard]] std::size_t find_identified(const PedalNoteEvent& event) const noexcept;
    [[nodiscard]] std::size_t find_anonymous(const PedalNoteEvent& event) const noexcept;
    void erase_owner(std::size_t index) noexcept;

    std::array<PedalOwnerSnapshot, kMaxPedalNoteOwners> owners_{};
    std::array<std::uint16_t, kPedalCount> physical_counts_{};
    std::size_t owner_count_{0};
};

} // namespace hammond
