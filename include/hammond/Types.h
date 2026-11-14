#pragma once

#include <cstddef>
#include <cstdint>

namespace hammond {

inline constexpr std::size_t kToneSourceCount = 91;
inline constexpr std::size_t kManualCount = 2;
inline constexpr std::size_t kManualKeyCount = 61;
inline constexpr std::size_t kDrawbarCount = 9;
inline constexpr std::size_t kDrawbarPositionCount = 9;
inline constexpr std::size_t kMaxEventsPerBlock = 1024;
inline constexpr std::uint32_t kHardMaxBlockFrames = 65536;
inline constexpr std::uint8_t kMinManualMidiNote = 36;
inline constexpr std::uint8_t kMaxManualMidiNote = 96;
inline constexpr std::uint8_t kMinToneId = 1;
inline constexpr std::uint8_t kMaxToneId = 91;
inline constexpr std::uint8_t kMinManualToneId = 13;

// A tone ID is one-based; array storage is zero-based. Neither is a physical
// generator terminal, and a manual MIDI note is a separate domain.
using ToneId = std::uint8_t;

enum class Manual : std::uint8_t { Upper = 0, Lower = 1 };

enum class EventType : std::uint8_t {
    NoteOn = 0,
    NoteOff = 1,
    Drawbar = 2,
    Expression = 3,
    AllNotesOff = 4,
    BankDrawbar = 5,
    SelectBank = 6,
    Cancel = 7,
    Percussion = 8,
    KeyPosition = 9,
    PedalOn = 10,
    PedalOff = 11,
    PedalDrawbar = 12,
    PedalAllNotesOff = 13,
    SelectPreset = 14,
};

// Offsets are relative to the current block; equal offsets retain input order.
// Note index: MIDI 36..96; NoteOn value: velocity 0..127 (zero means release).
// NoteOn with positive velocity commands target 1, including after a partial
// hold; NoteOff/zero velocity command target 0 using ordinary release travel.
// KeyPosition index: MIDI 36..96 on either manual; value: finite normalized
// target 0..1. LinearTravel preserves current position and contact hysteresis;
// Ideal accepts endpoints only. Identical targets do not restart motion. These
// commands consume no elapsed time and do not reset shared source/readiness state.
// Drawbar index: physical order 0..8 in the selected bank; value: integer 0..8.
// BankDrawbar index: bank*9 + drawbar, 0..17 (A=0, B=1); value: integer 0..8.
// SelectBank index: 0; value: integer 0=A or 1=B. Selection enables the route.
// SelectPreset index: 0; value: integer 0..11 for Cancel, nine fixed keys,
// bank A, bank B. Fixed/bank selection enables the route; banks clear fixed mode.
// Cancel index/value: 0. Disconnects one manual without releasing held keys.
// Percussion is Upper only, value: integer 0 or 1. Index 0: Off/On;
// 1: Second/Third harmonic; 2: Normal/Soft volume; 3: Slow/Fast decay.
// Expression is global with value 0..1. AllNotesOff immediately panics one manual.
// Note velocity does not scale sustained amplitude or select a motion curve.
// KeyPosition is direct physical input, not counted external note ownership or
// a saved control. Keep one coordinated note authority for each physical key.
// Pedal events require canonical Manual::Lower, without reusing manual MIDI
// keys or extending Manual. PedalOn/Off index: one-based pedal ID 1..25.
// On value: integer velocity 0..127; zero releases, positive closes all eight
// ideal pedal contacts without velocity-dependent gain. Off value: exactly 0.
// PedalDrawbar index: mixture 0..1; value: integer position 0..8.
// PedalAllNotesOff index/value: 0. It opens every pedal contact and preserves
// manual keys, all controls and source/percussion histories.
struct Event {
    std::uint32_t offset{0};
    EventType type{EventType::NoteOn};
    Manual manual{Manual::Upper};
    std::uint8_t index{0};
    double value{0.0};
};

struct ProcessSpec {
    double sample_rate{48000.0};
    std::uint32_t max_block_frames{1024};
    std::uint64_t seed{0};
    std::uint64_t initial_frame{0};
};

// Stable, allocation-free error vocabulary shared by prepare and process.
enum class Status : std::uint8_t {
    Ok = 0,
    NotPrepared = 1,
    InvalidSpec = 2,
    InvalidProfile = 3,
    InvalidEvent = 4,
    InvalidBuffer = 5,
    TooManyEvents = 6,
    BlockTooLarge = 7,
    TimelineOverflow = 8,
};

struct ProcessResult {
    Status status{Status::Ok};
    std::uint32_t events_consumed{0};

    [[nodiscard]] constexpr bool ok() const noexcept {
        return status == Status::Ok;
    }
    [[nodiscard]] constexpr explicit operator bool() const noexcept {
        return ok();
    }
};

[[nodiscard]] constexpr bool is_supported_sample_rate(double rate) noexcept {
    return rate == 44100.0 || rate == 48000.0 || rate == 96000.0;
}

[[nodiscard]] constexpr bool is_valid_manual(Manual manual) noexcept {
    return manual == Manual::Upper || manual == Manual::Lower;
}

[[nodiscard]] constexpr bool is_valid_manual_midi_note(std::uint32_t note) noexcept {
    return note >= kMinManualMidiNote && note <= kMaxManualMidiNote;
}

// Checked conversions leave the destination unchanged on an invalid input.
[[nodiscard]] constexpr bool tone_id_to_index(ToneId id, std::size_t& index) noexcept {
    if (id < kMinToneId || id > kMaxToneId) {
        return false;
    }
    index = static_cast<std::size_t>(id) - 1;
    return true;
}

[[nodiscard]] constexpr bool manual_midi_to_key_index(std::uint32_t note,
                                                     std::size_t& index) noexcept {
    if (!is_valid_manual_midi_note(note)) {
        return false;
    }
    index = static_cast<std::size_t>(note - kMinManualMidiNote);
    return true;
}

[[nodiscard]] constexpr const char* status_name(Status status) noexcept {
    switch (status) {
    case Status::Ok: return "ok";
    case Status::NotPrepared: return "not_prepared";
    case Status::InvalidSpec: return "invalid_spec";
    case Status::InvalidProfile: return "invalid_profile";
    case Status::InvalidEvent: return "invalid_event";
    case Status::InvalidBuffer: return "invalid_buffer";
    case Status::TooManyEvents: return "too_many_events";
    case Status::BlockTooLarge: return "block_too_large";
    case Status::TimelineOverflow: return "timeline_overflow";
    }
    return "unknown_status";
}

} // namespace hammond
