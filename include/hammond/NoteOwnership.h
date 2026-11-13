#pragma once

#include "hammond/Types.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <span>
#include <string_view>

namespace hammond {

inline constexpr std::size_t kHostInputBusCount = 2;
inline constexpr std::size_t kHostInputChannelCount = 16;
inline constexpr std::size_t kMaxNoteOwners = 256;
inline constexpr std::string_view kNoteOwnershipModelId =
    "bounded-fifo-note-ownership-v1";

enum class HostNoteKind : std::uint8_t { On = 0, Off = 1, AllNotesOff = 2 };

// An internal typed host command, not a MIDI byte packet or a native VST3 ABI.
// Positive blocks use offset < frames; zero-frame flushes require offset zero.
// On/Off: MIDI 36..96 and note_id == -1 (unidentified) or >= 0. On accepts
// velocity 0..127; velocity zero is a release. Off requires velocity zero.
// AllNotesOff: midi_note=0, velocity=0, note_id=-1; bus/channel select its scope.
struct HostNoteEvent {
    std::uint32_t offset{0};
    HostNoteKind kind{HostNoteKind::On};
    std::uint8_t bus{0};
    std::uint8_t channel{0};
    std::uint8_t midi_note{kMinManualMidiNote};
    std::uint8_t velocity{0};
    std::int32_t note_id{-1};
};

struct NoteOwnershipResult {
    Status status{Status::Ok};
    std::uint32_t input_consumed{0};
    std::uint32_t output_events{0};

    [[nodiscard]] constexpr bool ok() const noexcept { return status == Status::Ok; }
    [[nodiscard]] constexpr explicit operator bool() const noexcept { return ok(); }
};

// The original manual is retained even after the bus is remapped. Snapshots are
// ordered by surviving insertion order, including repeated unidentified owners.
struct NoteOwnerSnapshot {
    std::uint8_t bus{0};
    std::uint8_t channel{0};
    std::uint8_t midi_note{0};
    std::int32_t note_id{-1};
    Manual manual{Manual::Upper};

    [[nodiscard]] bool operator==(const NoteOwnerSnapshot&) const noexcept = default;
};

// Fixed-capacity host ownership, separate from Engine's Boolean physical keys.
// Default routes: bus 0 -> Upper, bus 1 -> Lower; no initial owners. No prepare,
// allocation, file access, lock, source phase or percussion state is involved.
// Use only on the processing thread or while stopped; no concurrent UI protocol.
class NoteOwnership {
public:
    // First physical owner emits NoteOn; final owner emits NoteOff. Identified
    // duplicate On is idempotent; a reused ID with a conflicting pitch rejects.
    // Unidentified repetitions use FIFO release within bus/channel/pitch. A
    // missing matching release is accepted as a no-op. Channel AllNotesOff never
    // emits Engine AllNotesOff, which would release other channels' owners.
    //
    // Entire-call transaction: bad offsets/payload/identity, over 1024 inputs,
    // more than 256 simultaneous owners, or insufficient output capacity changes
    // neither this object nor output and returns both counts zero. Output is
    // also bounded to 1024 events even if a larger span is supplied. Success
    // writes only output_events entries, preserving the remaining output tail.
    // BlockTooLarge: frames > 65536. TooManyEvents: input/owner/output capacity.
    // InvalidEvent: payload, ordering, offset or conflicting identified pitch.
    //
    // Success only translates/commits ownership; it does not call Engine. To
    // coordinate both atomically, translate with a copy and install that copy
    // only after Engine accepts the complete translated event block.
    [[nodiscard]] NoteOwnershipResult translate(
        std::uint32_t frames, std::span<const HostNoteEvent> input,
        std::span<Event> output) noexcept;

    // Change destinations for future owners only. Existing owners and later
    // releases retain their original manual. Invalid arguments change nothing.
    [[nodiscard]] bool set_bus_route(std::uint32_t bus, Manual manual) noexcept;
    [[nodiscard]] bool set_routes(
        const std::array<Manual, kHostInputBusCount>& routes) noexcept;
    [[nodiscard]] bool bus_route(std::uint32_t bus, Manual& destination) const noexcept;

    [[nodiscard]] std::size_t owner_count() const noexcept { return owner_count_; }
    [[nodiscard]] bool owner_count(Manual manual, std::uint32_t midi_note,
                                    std::size_t& destination) const noexcept;
    [[nodiscard]] bool owner_snapshot(std::size_t index,
                                      NoteOwnerSnapshot& destination) const noexcept;

    [[nodiscard]] bool operator==(const NoteOwnership&) const noexcept = default;

private:
    [[nodiscard]] std::size_t find_identified(const HostNoteEvent& event) const noexcept;
    [[nodiscard]] std::size_t find_unidentified(const HostNoteEvent& event) const noexcept;
    void erase_owner(std::size_t index) noexcept;

    std::array<Manual, kHostInputBusCount> routes_{Manual::Upper, Manual::Lower};
    std::array<NoteOwnerSnapshot, kMaxNoteOwners> owners_{};
    std::array<std::array<std::uint16_t, kManualKeyCount>, kManualCount> physical_counts_{};
    std::size_t owner_count_{0};
};

} // namespace hammond
