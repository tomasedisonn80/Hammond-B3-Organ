#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <string>
#include <string_view>

namespace hammond::standalone {

inline constexpr std::string_view kMidiReplayFormat = "B3MIDIREPLAY1";
inline constexpr std::size_t kMidiReplayMaxEvents = 2048;
inline constexpr std::size_t kMidiReplayMaxBytes = 64 * 1024;
inline constexpr std::size_t kMidiReplayMaxLineBytes = 256;
inline constexpr std::uint32_t kMidiReplayMinimumDurationMs = 250;
inline constexpr std::uint32_t kMidiReplayMaximumDurationMs = 10000;

enum class MidiReplayKind : std::uint8_t {
    Bytes, Connect, Disconnect, BackendFault,
};

struct MidiReplayEvent {
    std::uint32_t at_ms{0};
    MidiReplayKind kind{MidiReplayKind::Bytes};
    std::array<std::uint8_t, 3> bytes{};
    std::uint8_t size{0};
};

// Value-owned synthetic input data. Active records have nondecreasing times
// below duration_ms; equal times retain source order. Bytes records contain
// 1..3 raw bytes, including values that the MIDI decoder may reject. Other
// records have zero size and zero bytes. Inactive array entries are zeroed.
// The runtime starts disconnected and owns connection/release acknowledgments,
// inbox feeding, event cursors and completion; this plan performs no actions.
struct MidiReplayPlan {
    std::array<MidiReplayEvent, kMidiReplayMaxEvents> events{};
    std::size_t event_count{0};
    std::uint32_t duration_ms{0};
};

// Control-thread operations. Failure leaves the entire destination unchanged;
// success owns all records and clears error. No SDL, device SDK, Session or
// Engine dependency. Loading accepts only a bounded regular nonsymlink leaf.
[[nodiscard]] bool parse_midi_replay(std::string_view source,
                                    MidiReplayPlan& destination,
                                    std::string& error);
[[nodiscard]] bool load_midi_replay(const std::filesystem::path& path,
                                   MidiReplayPlan& destination,
                                   std::string& error);

} // namespace hammond::standalone
