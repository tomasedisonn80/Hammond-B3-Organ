#pragma once

#include "Drawing.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <span>
#include <string>
#include <string_view>

namespace hammond::standalone {

enum class ViewOverlay { None, Help, Audio, Midi };

struct InstrumentViewInfo {
    bool audio_running{false};
    int sample_rate{0};
    std::uint32_t buffer_frames{0};
    std::string_view audio_driver{};
    std::string_view device_name{};
    std::string_view status_message{};
    std::uint64_t clipped_samples{0};
    ViewOverlay overlay{ViewOverlay::None};
    // First choice is the default device; remaining strings are exact names.
    std::span<const std::string> audio_choices{};
    std::size_t selected_device{0};
    int selected_sample_rate{48000};
    std::uint32_t selected_buffer_frames{512};
    bool midi_available{false};
    bool midi_open{false};
    std::string_view midi_backend{};
    std::string_view midi_port{};
    std::string_view midi_status{};
    std::span<const std::string> midi_choices{};
    std::size_t selected_midi_port{0};
    std::array<std::uint8_t, 3> selected_midi_channels{1, 2, 3};
    std::uint64_t midi_messages{0};
};

struct AudioOverlayLayout {
    UiRect panel{};
    UiRect previous_device{};
    UiRect next_device{};
    UiRect sample_rate{};
    UiRect buffer_frames{};
    UiRect apply{};
    UiRect close{};
};

struct MidiOverlayLayout {
    UiRect panel{};
    UiRect previous_port{};
    UiRect next_port{};
    UiRect upper_channel{};
    UiRect lower_channel{};
    UiRect pedal_channel{};
    UiRect apply{};
    UiRect disconnect{};
    UiRect close{};
};

// These shared rectangles also drive the app's modal hit testing.
[[nodiscard]] AudioOverlayLayout audio_overlay_layout(float width, float height) noexcept;
[[nodiscard]] MidiOverlayLayout midi_overlay_layout(float width, float height) noexcept;
void paint_instrument(Drawing& drawing, const UiModel& model,
                       const InstrumentViewInfo& info);

} // namespace hammond::standalone
