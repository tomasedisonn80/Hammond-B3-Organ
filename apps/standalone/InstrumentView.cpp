#include "InstrumentView.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <string>

namespace hammond::standalone {
namespace {

constexpr UiColor kMuted{158, 160, 146};
constexpr UiColor kDark{17, 20, 18};
constexpr UiColor kGreen{151, 188, 145};
constexpr UiColor kRed{230, 130, 100};

[[nodiscard]] std::size_t manual_index(Manual manual) noexcept {
    return static_cast<std::size_t>(manual);
}

void centered(Drawing& drawing, std::string_view text, UiRect bounds,
              float size, UiColor color) {
    size = std::min(size, std::max(9.0F, bounds.height * 0.65F));
    const float natural_width = drawing.text_width(text, size);
    if (natural_width > bounds.width - 4.0F && natural_width > 0.0F) {
        size *= std::max(0.1F, bounds.width - 4.0F) / natural_width;
    }
    drawing.text(text, bounds.x + (bounds.width - drawing.text_width(text, size)) / 2.0F,
                 bounds.y + (bounds.height - size * 1.2F) / 2.0F, size, color);
}

void panel(Drawing& drawing, UiRect bounds) {
    drawing.shadow(bounds);
    drawing.rounded(bounds, 8.0F, {25, 28, 25});
    drawing.gradient({bounds.x + 3.0F, bounds.y + 3.0F, bounds.width - 6.0F,
                      bounds.height - 6.0F}, {46, 49, 43}, {28, 31, 28});
    drawing.line(bounds.x + 9.0F, bounds.y + 1.0F,
                  bounds.x + bounds.width - 9.0F, bounds.y + 1.0F, {89, 87, 70});
    for (const float x : {bounds.x + 8.0F, bounds.x + bounds.width - 10.0F}) {
        drawing.rounded({x, bounds.y + 8.0F, 4.0F, 4.0F}, 2.0F, {12, 14, 12});
    }
}

void button(Drawing& drawing, UiRect bounds, std::string_view label,
            bool selected = false, bool warning = false) {
    drawing.rounded({bounds.x, bounds.y + 2.0F, bounds.width, bounds.height}, 4.0F, {9, 11, 10});
    drawing.rounded(bounds, 4.0F, selected ? UiColor{89, 81, 58} : UiColor{48, 52, 46});
    drawing.line(bounds.x + 5.0F, bounds.y + 1.0F,
                  bounds.x + bounds.width - 5.0F, bounds.y + 1.0F,
                  selected ? kUiBrass : UiColor{84, 87, 76});
    centered(drawing, label, bounds, 12.0F, warning ? kRed : selected ? kUiIvory : kMuted);
}

[[nodiscard]] std::string_view button_label(const UiControlId& id) noexcept {
    switch (id.kind) {
    case UiControlKind::EditBank: return id.bank == DrawbarBank::A ? "EDIT A" : "EDIT B";
    case UiControlKind::SoundingBank: return id.bank == DrawbarBank::A ? "PLAY A" : "PLAY B";
    case UiControlKind::CancelManual: return "CANCEL";
    case UiControlKind::KeyboardTarget:
        return id.index == 0 ? "UPPER" : id.index == 1 ? "LOWER" : "PEDALS";
    case UiControlKind::OctaveDown: return "OCT -";
    case UiControlKind::OctaveUp: return "OCT +";
    case UiControlKind::SaveControls: return "SAVE";
    case UiControlKind::LoadControls: return "LOAD";
    case UiControlKind::AudioSettings: return "AUDIO";
    case UiControlKind::Help: return "HELP";
    case UiControlKind::Panic: return "PANIC";
    default: return {};
    }
}

void drawbar(Drawing& drawing, const UiControlGeometry& geometry,
             std::uint8_t value, std::string_view label, UiColor cap) {
    centered(drawing, label, geometry.label_bounds, 11.5F, kUiIvory);
    const auto& track = geometry.track;
    drawing.rounded({track.x - 5.0F, track.y - 11.0F,
                     track.width + 10.0F, track.height + 22.0F}, 4.0F, kDark);
    drawing.rect({track.x + track.width / 2.0F - 2.0F, track.y,
                  4.0F, track.height}, {67, 69, 60});
    for (int tick = 0; tick <= 8; ++tick) {
        const float y = track.y + track.height * static_cast<float>(tick) / 8.0F;
        drawing.line(track.x - 2.0F, y, track.x + track.width + 2.0F, y, {63, 66, 57});
    }
    const float y = track.y + track.height * static_cast<float>(value) / 8.0F;
    drawing.gradient({track.x + track.width / 2.0F - 5.0F, track.y - 3.0F,
                      10.0F, y - track.y + 4.0F}, {180, 173, 149}, {94, 94, 79});
    const float width = std::max(16.0F, std::min(29.0F, geometry.bounds.width - 5.0F));
    const float x = track.x + track.width / 2.0F - width / 2.0F;
    drawing.rounded({x + 1.0F, y - 7.0F, width, 22.0F}, 4.0F, {0, 0, 0, 120});
    drawing.rounded({x, y - 10.0F, width, 22.0F}, 4.0F, cap);
    drawing.line(x + 3.0F, y - 8.0F, x + width - 3.0F, y - 8.0F, {255, 250, 220, 80});
    drawing.line(x + 4.0F, y + 6.0F, x + width - 4.0F, y + 6.0F, {0, 0, 0, 70});
    centered(drawing, std::to_string(value), geometry.value_bounds, 13.0F, kUiBrass);
}

void paint_controls(Drawing& drawing, const UiModel& model) {
    const auto& view = model.view();
    const auto& layout = model.layout();
    const std::array<UiColor, 9> caps{{
        {135, 92, 57}, {135, 92, 57}, {222, 216, 193}, {222, 216, 193},
        {39, 43, 40}, {222, 216, 193}, {39, 43, 40}, {39, 43, 40}, {222, 216, 193}}};
    for (std::size_t index = 0; index < layout.control_count; ++index) {
        const auto& geometry = layout.controls[index];
        const auto& id = geometry.id;
        const auto manual = manual_index(id.manual);
        bool selected = false;
        if (id.kind == UiControlKind::ManualDrawbar) {
            const auto value = view.controls.drawbars[manual][static_cast<std::size_t>(id.bank)][id.index];
            drawbar(drawing, geometry, value, kUiFootageLabels[id.index], caps[id.index]);
        } else if (id.kind == UiControlKind::PedalDrawbar) {
            drawbar(drawing, geometry, view.controls.pedal_drawbars[id.index],
                    id.index == 0 ? "MIX 1" : "MIX 2", {135, 92, 57});
        } else if (id.kind == UiControlKind::Expression) {
            centered(drawing, "EXPRESSION", geometry.label_bounds, 10.5F, kUiIvory);
            const auto& track = geometry.track;
            drawing.rounded({track.x - 3.0F, track.y - 5.0F, track.width + 6.0F, 10.0F}, 4.0F, kDark);
            const float x = track.x + static_cast<float>(view.controls.expression) * track.width;
            drawing.rect({track.x, track.y - 1.0F, x - track.x, 2.0F}, kUiBrass);
            drawing.rounded({x - 6.0F, track.y - 10.0F, 12.0F, 20.0F}, 4.0F, {169, 147, 103});
            const auto percent = static_cast<int>(std::round(view.controls.expression * 100.0));
            centered(drawing, std::to_string(percent) + "%", geometry.value_bounds, 12.0F, kUiBrass);
        } else if (id.kind == UiControlKind::Percussion) {
            const auto& settings = view.controls.percussion;
            constexpr std::array<std::string_view, 4> titles{"PERC", "HARM", "VOLUME", "DECAY"};
            std::string_view value;
            switch (id.index) {
            case 0: value = settings.enabled ? "ON" : "OFF"; selected = settings.enabled; break;
            case 1: value = settings.harmonic == PercussionHarmonic::Second ? "2ND" : "3RD"; break;
            case 2: value = settings.volume == PercussionVolume::Normal ? "NORM" : "SOFT"; break;
            default: value = settings.decay == PercussionDecay::Slow ? "SLOW" : "FAST"; break;
            }
            button(drawing, geometry.bounds, {}, selected);
            centered(drawing, titles[id.index], geometry.label_bounds, 9.0F, kMuted);
            centered(drawing, value, geometry.value_bounds, 11.5F, selected ? kUiBrass : kUiIvory);
        } else {
            if (id.kind == UiControlKind::EditBank) selected = view.edited_banks[manual] == id.bank;
            if (id.kind == UiControlKind::SoundingBank) {
                selected = view.applied.controls.route_enabled[manual] &&
                    view.applied.controls.selected_banks[manual] == id.bank;
            }
            if (id.kind == UiControlKind::CancelManual) selected = !view.applied.controls.route_enabled[manual];
            if (id.kind == UiControlKind::KeyboardTarget) selected = static_cast<std::uint8_t>(view.keyboard_target) == id.index;
            button(drawing, geometry.bounds, button_label(id), selected, id.kind == UiControlKind::Panic);
        }
        if (view.focus == id) drawing.outline(geometry.bounds, kUiFocusCyan, 2.0F);
    }
}

void paint_key(Drawing& drawing, const UiKeyGeometry& key, bool held, bool focused) {
    const auto& b = key.bounds;
    if (key.accidental) {
        drawing.rect({b.x + 1.0F, b.y + 3.0F, b.width, b.height}, {0, 0, 0, 120});
        drawing.gradient(b, held ? UiColor{128, 113, 76} : UiColor{48, 51, 47},
                          held ? UiColor{81, 78, 54} : UiColor{12, 15, 13});
        drawing.line(b.x + 2.0F, b.y + 2.0F, b.x + b.width - 2.0F, b.y + 2.0F,
                      held ? kUiBrass : UiColor{76, 78, 70});
        drawing.rect({b.x + 1.0F, b.y + b.height - 6.0F, b.width - 2.0F, 5.0F}, {13, 16, 14});
    } else {
        drawing.gradient({b.x + 0.5F, b.y, b.width - 1.0F, b.height},
                          held ? UiColor{205, 192, 146} : UiColor{229, 225, 206},
                          held ? UiColor{170, 159, 116} : UiColor{248, 242, 218});
        drawing.rect({b.x + 0.5F, b.y + b.height - 6.0F, b.width - 1.0F, 5.0F},
                     held ? UiColor{130, 127, 96} : UiColor{190, 186, 162});
    }
    if (held) drawing.rect({b.x + 3.0F, b.y + b.height - 12.0F,
                            std::max(1.0F, b.width - 6.0F), 3.0F}, kUiBrass);
    if (focused) drawing.outline({b.x + 2.0F, b.y + 2.0F, b.width - 4.0F, b.height - 4.0F}, kUiFocusCyan, 2.0F);
}

void overlay(Drawing& drawing, const UiLayout& layout, const InstrumentViewInfo& info) {
    if (info.overlay == ViewOverlay::None) return;
    drawing.rect({0, 0, layout.width, layout.height}, {0, 0, 0, 185});
    const auto boxes = audio_overlay_layout(layout.width, layout.height);
    panel(drawing, boxes.panel);
    const float x = boxes.panel.x + 28.0F;
    const float y = boxes.panel.y + 22.0F;
    drawing.text(info.overlay == ViewOverlay::Audio ? "Audio output" : "Playing the instrument",
                  x, y, 28.0F, kUiIvory, TextFace::Serif);
    button(drawing, boxes.close, "CLOSE");
    if (info.overlay == ViewOverlay::Help) {
        constexpr std::array<std::string_view, 9> help{
            "A W S E D F T G Y H U J K O L P ;   Play notes",
            "F1 / F2 / F3   Upper / Lower / Pedals",
            "[ / ]   Shift the keyboard octave",
            "Tab / Shift+Tab   Move between controls",
            "Arrow keys   Adjust controls or move on a manual",
            "Space   Hold the focused key; release to stop",
            "EDIT A/B prepares a bank. PLAY A/B selects its sound.",
            "CANCEL mutes one manual route. PANIC releases all notes.",
            "Saves contain controls, not held keys or sound history."};
        for (std::size_t i = 0; i < help.size(); ++i) {
            drawing.text(help[i], x, y + 64.0F + static_cast<float>(i) * 30.0F, 15.0F,
                         i < 6 ? kUiIvory : kMuted);
        }
        return;
    }
    drawing.text("OUTPUT DEVICE", x, y + 60.0F, 12.0F, kUiBrass);
    std::string_view choice = "Default output";
    if (info.selected_device < info.audio_choices.size()) choice = info.audio_choices[info.selected_device];
    centered(drawing, choice, {x + 48.0F, y + 90.0F, boxes.panel.width - 152.0F, 34.0F}, 16.0F, kUiIvory);
    button(drawing, boxes.previous_device, "<");
    button(drawing, boxes.next_device, ">");
    drawing.text("SAMPLE RATE", x, y + 150.0F, 12.0F, kUiBrass);
    drawing.text("CALLBACK FRAMES", x + 270.0F, y + 150.0F, 12.0F, kUiBrass);
    button(drawing, boxes.sample_rate, std::to_string(info.selected_sample_rate) + " Hz");
    button(drawing, boxes.buffer_frames, std::to_string(info.selected_buffer_frames));
    drawing.text("Click a value to cycle through supported settings.", x, y + 234.0F, 14.0F, kMuted);
    drawing.text("Applying settings stops notes and restarts the audio device.", x, y + 265.0F, 14.0F, kMuted);
    drawing.text("Your drawbars and other musical controls are retained.", x, y + 292.0F, 14.0F, kMuted);
    button(drawing, boxes.apply, "APPLY AUDIO SETTINGS", true);
}

} // namespace

AudioOverlayLayout audio_overlay_layout(float width, float height) noexcept {
    const UiRect panel_rect{(width - 660.0F) / 2.0F, (height - 440.0F) / 2.0F, 660.0F, 440.0F};
    return {panel_rect,
            {panel_rect.x + 28.0F, panel_rect.y + 112.0F, 40.0F, 34.0F},
            {panel_rect.x + 592.0F, panel_rect.y + 112.0F, 40.0F, 34.0F},
            {panel_rect.x + 28.0F, panel_rect.y + 204.0F, 220.0F, 38.0F},
            {panel_rect.x + 298.0F, panel_rect.y + 204.0F, 220.0F, 38.0F},
            {panel_rect.x + 28.0F, panel_rect.y + 370.0F, 270.0F, 40.0F},
            {panel_rect.x + 548.0F, panel_rect.y + 24.0F, 84.0F, 32.0F}};
}

void paint_instrument(Drawing& drawing, const UiModel& model, const InstrumentViewInfo& info) {
    const auto& layout = model.layout();
    const auto& view = model.view();
    drawing.clear({23, 25, 22});
    drawing.gradient({0, 0, layout.width, layout.height}, {88, 57, 37}, {42, 29, 21});
    for (int row = 0; row < static_cast<int>(layout.height); row += 3) {
        const auto shade = static_cast<std::uint8_t>(12 + (row * 19) % 18);
        drawing.line(0, static_cast<float>(row), layout.width, static_cast<float>(row), {0, 0, 0, shade});
    }
    const float margin = layout.header.x;
    drawing.rounded({margin - 8.0F, margin - 8.0F, layout.width - 2.0F * margin + 16.0F,
                     layout.height - 2.0F * margin + 16.0F}, 12.0F, kDark);
    drawing.text("B-3 Workshop", layout.header.x + 8.0F, layout.header.y - 3.0F,
                  layout.width >= 1120.0F ? 30.0F : 27.0F, kUiIvory, TextFace::Serif);
    drawing.text("NOMINAL DRY ORGAN", layout.header.x + 10.0F, layout.header.y + 37.0F,
                  10.5F, kUiBrass);
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        const auto& bounds = layout.registration_panels[manual];
        panel(drawing, bounds);
        drawing.text(manual == 0 ? "UPPER / SWELL" : "LOWER / GREAT",
                      bounds.x + 14.0F, bounds.y + 5.0F, 12.5F, kUiIvory);
        const bool connected = view.applied.controls.route_enabled[manual];
        const std::string sounding = connected ?
            (view.applied.controls.selected_banks[manual] == DrawbarBank::A ? "SOUNDING A" : "SOUNDING B") : "CANCELLED";
        const float label_width = drawing.text_width(sounding, 9.5F);
        drawing.text(sounding, bounds.x + bounds.width - label_width - 14.0F,
                      bounds.y + 8.0F, 9.5F, connected ? kUiBrass : kMuted);
    }
    panel(drawing, layout.performance_panel);
    drawing.text("PERFORMANCE", layout.performance_panel.x + 14.0F,
                  layout.performance_panel.y + 5.0F, 12.5F, kUiIvory);
    const bool eligible = view.applied.controls.route_enabled[0] &&
        view.applied.controls.selected_banks[0] == DrawbarBank::B;
    centered(drawing, eligible ? "PERCUSSION ROUTE: UPPER B" : "PERCUSSION REQUIRES UPPER B",
              {layout.performance_panel.x + 10.0F, layout.performance_panel.y + 75.0F,
               layout.performance_panel.width - 20.0F, 20.0F}, 9.0F, eligible ? kGreen : kMuted);
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        const auto& bounds = layout.manual_panels[manual];
        panel(drawing, bounds);
        drawing.text(manual == 0 ? "UPPER MANUAL" : "LOWER MANUAL",
                      bounds.x + 14.0F, bounds.y + 3.0F, 10.5F, kUiBrass);
        for (const bool accidental : {false, true}) {
            for (std::size_t index = 0; index < kManualKeyCount; ++index) {
                const auto& key = layout.manual_keys[manual][index];
                if (key.accidental != accidental) continue;
                const bool focused = view.focus.kind == UiControlKind::ManualKey &&
                    manual_index(view.focus.manual) == manual && view.focus.index == index;
                paint_key(drawing, key, view.applied.held_keys[manual][index], focused);
            }
        }
    }
    panel(drawing, layout.pedal_panel);
    drawing.text("PEDALBOARD / 25 NOTES", layout.pedal_panel.x + 14.0F,
                  layout.pedal_panel.y + 3.0F, 10.5F, kUiBrass);
    for (const bool accidental : {false, true}) {
        for (std::size_t index = 0; index < kPedalCount; ++index) {
            const auto& key = layout.pedal_keys[index];
            if (key.accidental == accidental) {
                paint_key(drawing, key, view.applied.held_pedals[index],
                          view.focus.kind == UiControlKind::PedalKey && view.focus.index == index);
            }
        }
    }
    paint_controls(drawing, model);
    const auto& footer = layout.footer;
    drawing.rounded({footer.x + 5.0F, footer.y + 11.0F, 7.0F, 7.0F}, 3.5F,
                     info.audio_running ? kGreen : kRed);
    std::string audio = info.audio_running ? "AUDIO RUNNING" : "NO AUDIO";
    if (!info.audio_driver.empty()) audio += " [" + std::string(info.audio_driver) + "]";
    if (info.sample_rate != 0) audio += "  " + std::to_string(info.sample_rate) + " Hz / " + std::to_string(info.buffer_frames) + " frames";
    drawing.text(audio, footer.x + 21.0F, footer.y + 6.0F, 11.0F, kUiIvory);
    std::string status;
    if (!info.status_message.empty()) status = info.status_message;
    else if (view.input_recovery) status = "Input recovered. Release held keys before playing again.";
    else if (view.controls_pending) status = "Applying controls...";
    else status = "A W S E D F T G Y H U J K O L P ;  play   |   F1/F2/F3 select manual   |   [ / ] octave";
    const float maximum_width = footer.width - 28.0F;
    while (!status.empty() && drawing.text_width(status, 10.0F) > maximum_width) status.pop_back();
    drawing.text(status, footer.x + 21.0F, footer.y + 24.0F, 10.0F, kMuted);
    const float meter_width = 100.0F;
    const float meter_x = footer.x + footer.width - meter_width - 14.0F;
    drawing.rect({meter_x, footer.y + 10.0F, meter_width, 6.0F}, {54, 57, 49});
    drawing.rect({meter_x, footer.y + 10.0F,
                  meter_width * std::clamp(view.applied.peak, 0.0F, 1.0F), 6.0F},
                 info.clipped_samples > 0 ? kRed : kGreen);
    if (view.controls_dirty) drawing.text("UNSAVED", meter_x - 76.0F, footer.y + 4.0F, 10.0F, kUiBrass);
    overlay(drawing, layout, info);
}

} // namespace hammond::standalone
