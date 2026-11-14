#include "InstrumentView.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <string>

namespace hammond::standalone {
namespace {

constexpr UiColor kMuted{166, 159, 142};
constexpr UiColor kDark{16, 17, 15};
constexpr UiColor kGreen{157, 187, 143};
constexpr UiColor kRed{232, 139, 110};
constexpr UiColor kMetalEdge{102, 89, 65};
constexpr UiColor kBrownCap{129, 77, 43};
constexpr UiColor kIvoryCap{230, 211, 178};
constexpr UiColor kBlackCap{39, 39, 34};

[[nodiscard]] std::size_t manual_index(Manual manual) noexcept {
    return static_cast<std::size_t>(manual);
}

[[nodiscard]] UiRect inset(UiRect bounds, float amount) noexcept {
    return {bounds.x + amount, bounds.y + amount,
            std::max(0.0F, bounds.width - 2.0F * amount),
            std::max(0.0F, bounds.height - 2.0F * amount)};
}

[[nodiscard]] UiColor shade(UiColor value, int change) noexcept {
    const auto component = [change](std::uint8_t channel) {
        return static_cast<std::uint8_t>(std::clamp(static_cast<int>(channel) + change, 0, 255));
    };
    return {component(value.red), component(value.green), component(value.blue), value.alpha};
}

void centered(Drawing& drawing, std::string_view value, UiRect bounds,
              float size, UiColor color, TextFace face = TextFace::Sans) {
    if (!(bounds.width > 0.0F && bounds.height > 0.0F)) return;
    size = std::min(size, bounds.height * 0.72F);
    const float width = drawing.text_width(value, size, face);
    if (width > bounds.width - 6.0F && width > 0.0F) {
        size *= std::max(0.1F, bounds.width - 6.0F) / width;
    }
    drawing.text(value, bounds.x + (bounds.width - drawing.text_width(value, size, face)) / 2.0F,
                 bounds.y + (bounds.height - size * 1.2F) / 2.0F, size, color, face);
}

[[nodiscard]] std::string single_line(std::string_view value) {
    std::string result(value);
    for (char& character : result) {
        if (static_cast<unsigned char>(character) < 32U || character == '\x7f') character = ' ';
    }
    return result;
}

[[nodiscard]] std::size_t fitting_prefix(Drawing& drawing, std::string_view value,
                                         float width, float size) {
    std::size_t first = 0;
    std::size_t last = value.size();
    while (first < last) {
        const auto middle = first + (last - first + 1) / 2;
        if (drawing.text_width(value.substr(0, middle), size) <= width) first = middle;
        else last = middle - 1;
    }
    return first;
}

// Device names and backend errors are untrusted-length presentation strings.
// They stay within their own row; truncation is visible, never an overlap.
void text_line(Drawing& drawing, std::string_view value, UiRect bounds,
               float size, UiColor color) {
    if (!(bounds.width > 0.0F && bounds.height >= size)) return;
    std::string line = single_line(value);
    if (drawing.text_width(line, size) > bounds.width) {
        const float available = bounds.width - drawing.text_width("...", size);
        line.resize(fitting_prefix(drawing, line, std::max(0.0F, available), size));
        line += "...";
    }
    drawing.text(line, bounds.x, bounds.y, size, color);
}

void wrapped(Drawing& drawing, std::string_view value, UiRect bounds,
             float size, UiColor color) {
    if (!(bounds.width > 0.0F && bounds.height >= size)) return;
    const std::string clean = single_line(value);
    std::string_view remainder(clean);
    const float line_height = size * 1.35F;
    const auto lines = static_cast<std::size_t>(std::floor(bounds.height / line_height));
    for (std::size_t row = 0; row < lines && !remainder.empty(); ++row) {
        const UiRect line{bounds.x, bounds.y + static_cast<float>(row) * line_height,
                          bounds.width, line_height};
        if (row + 1 == lines || drawing.text_width(remainder, size) <= bounds.width) {
            text_line(drawing, remainder, line, size, color);
            return;
        }
        std::size_t count = fitting_prefix(drawing, remainder, bounds.width, size);
        if (count == 0) return;
        const auto space = remainder.substr(0, count).find_last_of(' ');
        if (space != std::string_view::npos && space > count / 2) count = space;
        drawing.text(remainder.substr(0, count), line.x, line.y, size, color);
        remainder.remove_prefix(count);
        while (!remainder.empty() && remainder.front() == ' ') remainder.remove_prefix(1);
    }
}

void screw(Drawing& drawing, float x, float y) {
    drawing.rounded({x - 1.0F, y - 1.0F, 8.0F, 8.0F}, 4.0F, {8, 9, 8});
    drawing.rounded({x, y, 6.0F, 6.0F}, 3.0F, {131, 107, 65});
    drawing.line(x + 1.0F, y + 1.0F, x + 4.0F, y + 1.0F, {221, 188, 125});
    drawing.line(x + 1.5F, y + 4.5F, x + 4.5F, y + 1.5F, {34, 29, 20});
}

void panel(Drawing& drawing, UiRect bounds, bool screws = true) {
    if (!(bounds.width > 0.0F && bounds.height > 0.0F)) return;
    drawing.shadow(bounds, 5.0F);
    drawing.rounded(bounds, 6.0F, {9, 10, 9});
    drawing.rounded(inset(bounds, 1.0F), 5.0F, kMetalEdge);
    drawing.rounded(inset(bounds, 2.0F), 4.0F, {21, 22, 20});
    drawing.gradient(inset(bounds, 4.0F), {42, 43, 39}, {24, 26, 23});
    drawing.line(bounds.x + 7.0F, bounds.y + 3.0F,
                 bounds.x + bounds.width - 7.0F, bounds.y + 3.0F, {124, 115, 92, 140});
    drawing.line(bounds.x + 7.0F, bounds.y + bounds.height - 3.0F,
                 bounds.x + bounds.width - 7.0F, bounds.y + bounds.height - 3.0F, {7, 8, 7});
    if (screws) {
        for (const float x : {bounds.x + 7.0F, bounds.x + bounds.width - 13.0F}) {
            screw(drawing, x, bounds.y + 7.0F);
            if (bounds.height > 80.0F) screw(drawing, x, bounds.y + bounds.height - 13.0F);
        }
    }
}

void wood(Drawing& drawing, UiRect bounds) {
    drawing.gradient(bounds, {111, 64, 34}, {54, 28, 17});
    const auto rows = static_cast<int>(bounds.height);
    for (int row = 2; row < rows; row += 3) {
        const auto alpha = static_cast<std::uint8_t>(15 + (row * 29) % 29);
        const float y = bounds.y + static_cast<float>(row);
        drawing.line(bounds.x, y, bounds.x + bounds.width, y, {18, 8, 4, alpha});
        if (row % 9 == 2) {
            drawing.line(bounds.x, y + 1.0F, bounds.x + bounds.width, y + 1.0F, {223, 154, 86, 25});
        }
    }
    drawing.line(bounds.x, bounds.y + 1.0F, bounds.x + bounds.width, bounds.y + 1.0F, {207, 140, 82, 150});
    drawing.line(bounds.x, bounds.y + bounds.height - 1.0F,
                 bounds.x + bounds.width, bounds.y + bounds.height - 1.0F, {17, 9, 5});
}

void heading(Drawing& drawing, std::string_view value, UiRect bounds, float size) {
    centered(drawing, value, bounds, size, kUiBrass, TextFace::Serif);
    const float half_gap = drawing.text_width(value, size, TextFace::Serif) / 2.0F + 14.0F;
    const float middle = bounds.x + bounds.width / 2.0F;
    if (half_gap < bounds.width / 2.0F - 16.0F) {
        const float y = bounds.y + bounds.height / 2.0F;
        drawing.line(bounds.x + 9.0F, y, middle - half_gap, y, kMetalEdge);
        drawing.line(middle + half_gap, y, bounds.x + bounds.width - 9.0F, y, kMetalEdge);
    }
}

void button(Drawing& drawing, UiRect bounds, std::string_view label,
            bool selected = false, bool warning = false,
            TextFace face = TextFace::Sans, bool ivory = false) {
    const bool light = selected || ivory;
    const UiColor cap = selected ? UiColor{236, 205, 151} : ivory ? kIvoryCap : UiColor{47, 44, 37};
    drawing.rounded(bounds, 5.0F, {8, 8, 7});
    drawing.rounded(inset(bounds, 1.0F), 4.0F, selected ? UiColor{175, 130, 65} : UiColor{108, 98, 77});
    drawing.rounded(inset(bounds, 2.0F), 3.0F, {18, 17, 14});
    const UiRect face_bounds{bounds.x + 4.0F, bounds.y + 4.0F,
                             bounds.width - 8.0F, bounds.height - 9.0F};
    drawing.gradient(face_bounds, shade(cap, 15), shade(cap, -9));
    drawing.line(face_bounds.x + 1.0F, face_bounds.y, face_bounds.x + face_bounds.width - 1.0F,
                 face_bounds.y, light ? UiColor{255, 239, 202} : UiColor{119, 110, 90});
    drawing.rect({face_bounds.x, bounds.y + bounds.height - 6.0F,
                  face_bounds.width, 3.0F}, shade(cap, -26));
    centered(drawing, label, inset(bounds, 4.0F), face == TextFace::Serif ? 15.0F : 11.0F,
             warning ? (light ? UiColor{112, 43, 24} : kRed) : light ? UiColor{35, 29, 21} : kUiIvory, face);
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
    case UiControlKind::MidiSettings: return "MIDI";
    case UiControlKind::Help: return "HELP";
    case UiControlKind::Panic: return "PANIC";
    default: return {};
    }
}

[[nodiscard]] bool header_button(UiControlKind kind) noexcept {
    return kind == UiControlKind::SaveControls || kind == UiControlKind::LoadControls ||
        kind == UiControlKind::Help || kind == UiControlKind::AudioSettings ||
        kind == UiControlKind::MidiSettings || kind == UiControlKind::Panic;
}

void drawbar(Drawing& drawing, const UiControlGeometry& geometry,
             std::uint8_t value, std::string_view label, UiColor cap) {
    const bool mixture = geometry.id.kind == UiControlKind::PedalDrawbar;
    centered(drawing, label, geometry.label_bounds, mixture ? 11.0F : 13.0F,
             kUiIvory, mixture ? TextFace::Sans : TextFace::Serif);
    const auto& track = geometry.track;
    const float center = track.x + track.width / 2.0F;
    const float cap_width = std::max(10.0F, std::min(34.0F, geometry.bounds.width - 8.0F));
    const float cap_height = mixture ? 22.0F : 26.0F;
    const float half_height = cap_height / 2.0F;
    const float slot_width = std::min(geometry.bounds.width - 2.0F, cap_width + 8.0F);
    const UiRect slot{center - slot_width / 2.0F, track.y - half_height,
                      slot_width, track.height + cap_height};
    drawing.rounded(slot, 2.0F, {8, 9, 8});
    drawing.line(slot.x, slot.y + 1.0F, slot.x, slot.y + slot.height - 1.0F, {77, 73, 61});
    drawing.line(slot.x + slot.width - 1.0F, slot.y, slot.x + slot.width - 1.0F,
                 slot.y + slot.height, {53, 50, 41});
    drawing.gradient({center - 2.0F, track.y, 4.0F, track.height}, {115, 104, 80}, {48, 45, 36});
    for (int tick = 0; tick <= 8; ++tick) {
        const float y = track.y + track.height * static_cast<float>(tick) / 8.0F;
        drawing.line(slot.x + 1.0F, y, slot.x + 3.0F, y, {103, 94, 72});
    }
    const float y = track.y + track.height * static_cast<float>(value) / 8.0F;
    drawing.gradient({center - 4.0F, track.y, 8.0F, y - track.y}, {130, 116, 85}, {69, 62, 46});
    const UiRect knob{center - cap_width / 2.0F, y - half_height, cap_width, cap_height};
    drawing.rounded({knob.x - 1.0F, knob.y + 2.0F, knob.width + 2.0F, knob.height}, 3.0F, {0, 0, 0, 150});
    drawing.rounded(knob, 3.0F, shade(cap, -30));
    drawing.gradient({knob.x + 1.0F, knob.y + 2.0F, knob.width - 2.0F, knob.height - 7.0F},
                     shade(cap, 27), cap);
    drawing.rect({knob.x + 1.0F, knob.y + knob.height - 7.0F, knob.width - 2.0F, 5.0F}, shade(cap, -16));
    drawing.line(knob.x + 3.0F, knob.y + 2.0F, knob.x + knob.width - 3.0F, knob.y + 2.0F, shade(cap, 65));
    drawing.line(knob.x + 2.0F, knob.y + knob.height - 8.0F,
                 knob.x + knob.width - 2.0F, knob.y + knob.height - 8.0F, shade(cap, 34));
    centered(drawing, std::to_string(value), geometry.value_bounds, 13.0F, kUiBrass);
}

void paint_controls(Drawing& drawing, const UiModel& model) {
    const auto& view = model.view();
    const auto& layout = model.layout();
    const std::array<UiColor, 9> caps{
        kBrownCap, kBrownCap, kIvoryCap, kIvoryCap, kBlackCap,
        kIvoryCap, kBlackCap, kBlackCap, kIvoryCap};
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
                    id.index == 0 ? "MIX 1" : "MIX 2", kBrownCap);
        } else if (id.kind == UiControlKind::Expression) {
            centered(drawing, "NOMINAL EXPRESSION", geometry.label_bounds, 10.5F, kUiIvory);
            const auto& track = geometry.track;
            drawing.rounded({track.x - 3.0F, track.y - 5.0F, track.width + 6.0F, 10.0F}, 3.0F, {8, 9, 8});
            drawing.line(track.x, track.y + 3.0F, track.x + track.width, track.y + 3.0F, kMetalEdge);
            const float x = track.x + static_cast<float>(view.controls.expression) * track.width;
            drawing.rect({track.x, track.y - 1.0F, x - track.x, 2.0F}, kUiBrass);
            drawing.rounded({x - 7.0F, track.y - 11.0F, 14.0F, 22.0F}, 3.0F, {30, 26, 18});
            drawing.gradient({x - 5.0F, track.y - 9.0F, 10.0F, 17.0F}, {220, 193, 140}, {122, 97, 55});
            drawing.line(x - 3.0F, track.y - 7.0F, x + 3.0F, track.y - 7.0F, kUiIvory);
            const auto percent = static_cast<int>(std::round(view.controls.expression * 100.0));
            centered(drawing, std::to_string(percent) + "%", geometry.value_bounds, 11.5F, kUiBrass);
        } else if (id.kind == UiControlKind::Percussion) {
            const auto& settings = view.controls.percussion;
            constexpr std::array<std::string_view, 4> titles{"PERC", "HARMONIC", "VOLUME", "DECAY"};
            std::string_view value;
            switch (id.index) {
            case 0: value = settings.enabled ? "ON" : "OFF"; selected = settings.enabled; break;
            case 1: value = settings.harmonic == PercussionHarmonic::Second ? "2ND" : "3RD"; break;
            case 2: value = settings.volume == PercussionVolume::Normal ? "NORM" : "SOFT"; break;
            default: value = settings.decay == PercussionDecay::Slow ? "SLOW" : "FAST"; break;
            }
            button(drawing, geometry.bounds, {}, selected, false, TextFace::Serif, true);
            centered(drawing, titles[id.index], geometry.label_bounds, 9.0F, {87, 65, 42});
            centered(drawing, value, geometry.value_bounds, 14.0F, {33, 28, 21}, TextFace::Serif);
        } else {
            if (id.kind == UiControlKind::EditBank) selected = view.edited_banks[manual] == id.bank;
            if (id.kind == UiControlKind::SoundingBank) {
                selected = view.applied.controls.route_enabled[manual] &&
                    view.applied.controls.selected_banks[manual] == id.bank;
            }
            if (id.kind == UiControlKind::CancelManual) selected = !view.applied.controls.route_enabled[manual];
            if (id.kind == UiControlKind::KeyboardTarget) selected = static_cast<std::uint8_t>(view.keyboard_target) == id.index;
            button(drawing, geometry.bounds, button_label(id), selected, id.kind == UiControlKind::Panic,
                   header_button(id.kind) ? TextFace::Serif : TextFace::Sans);
        }
        if (view.focus == id) drawing.outline(geometry.bounds, kUiFocusCyan, 2.0F);
    }
}

void paint_key(Drawing& drawing, const UiKeyGeometry& key, bool held, bool focused) {
    const auto& b = key.bounds;
    const float front = std::clamp(b.height * 0.13F, 4.0F, 13.0F);
    // Top plane, front, held state and focus all remain inside the hit region.
    if (key.accidental) {
        drawing.rect(b, {6, 7, 6});
        drawing.gradient({b.x + 1.0F, b.y, b.width - 2.0F, b.height - front},
                         held ? UiColor{134, 111, 67} : UiColor{57, 53, 43},
                         held ? UiColor{91, 75, 43} : UiColor{22, 23, 20});
        drawing.line(b.x + 2.0F, b.y + 2.0F, b.x + 2.0F, b.y + b.height - front - 1.0F,
                     held ? UiColor{179, 150, 93} : UiColor{85, 78, 62});
        drawing.gradient({b.x + 1.0F, b.y + b.height - front, b.width - 2.0F, front - 1.0F},
                         held ? UiColor{77, 61, 34} : UiColor{31, 30, 25}, {8, 9, 8});
        drawing.line(b.x + 2.0F, b.y + b.height - front,
                     b.x + b.width - 2.0F, b.y + b.height - front, {118, 107, 80, 145});
    } else {
        drawing.rect(b, {44, 32, 20});
        drawing.gradient({b.x + 0.7F, b.y, b.width - 1.4F, b.height - front},
                         held ? UiColor{198, 175, 119} : UiColor{214, 201, 172},
                         held ? UiColor{229, 204, 143} : UiColor{250, 235, 205});
        drawing.gradient({b.x + 0.7F, b.y + b.height - front, b.width - 1.4F, front - 1.0F},
                         held ? UiColor{170, 141, 85} : UiColor{197, 174, 135},
                         held ? UiColor{124, 100, 58} : UiColor{143, 119, 81});
        drawing.line(b.x + 1.0F, b.y + b.height - front,
                     b.x + b.width - 1.0F, b.y + b.height - front, {255, 242, 208, 185});
    }
    if (held) drawing.rect({b.x + 3.0F, b.y + b.height - front - 4.0F,
                            std::max(1.0F, b.width - 6.0F), 2.0F}, kUiBrass);
    if (focused) drawing.outline(inset(b, 2.0F), kUiFocusCyan, 2.0F);
}

[[nodiscard]] std::string audio_configuration(const InstrumentViewInfo& info) {
    if (info.sample_rate == 0) return "No active audio configuration";
    return std::to_string(info.sample_rate) + " Hz / " + std::to_string(info.buffer_frames) + " frames";
}

[[nodiscard]] std::string midi_state(const InstrumentViewInfo& info) {
    if (!info.midi_available) return "MIDI UNAVAILABLE";
    return info.midi_open ? "MIDI CONNECTED" : "MIDI NOT CONNECTED";
}

void paint_cabinet(Drawing& drawing, const UiLayout& layout, const InstrumentViewInfo& info) {
    if (!layout.show_cabinet) return;
    const auto& cabinet = layout.cabinet_panel;
    const auto& art = layout.cabinet_art;
    panel(drawing, cabinet);
    heading(drawing, "ROTARY CABINET", {cabinet.x + 17.0F, cabinet.y + 6.0F,
            cabinet.width - 34.0F, 25.0F}, 16.0F);
    drawing.rect({art.x - 2.0F, art.y - 2.0F, art.width + 4.0F, art.height + 4.0F}, {8, 9, 8});
    if (!drawing.reference_art(ReferenceArt::Cabinet, art)) {
        drawing.gradient(art, {34, 25, 18}, {12, 13, 11});
        const UiRect box{art.x + art.width * 0.2F, art.y + art.height * 0.13F,
                         art.width * 0.6F, art.height * 0.73F};
        wood(drawing, box);
        for (int slot = 0; slot < 5; ++slot) {
            drawing.rect({box.x + box.width * 0.08F, box.y + 12.0F + static_cast<float>(slot) * 10.0F,
                          box.width * 0.84F, 4.0F}, {14, 10, 7});
        }
        centered(drawing, "DECORATIVE ART UNAVAILABLE", {art.x + 8.0F, art.y + art.height - 28.0F,
                 art.width - 16.0F, 20.0F}, 10.0F, kMuted);
    }
    const float below_art = art.y + art.height;
    heading(drawing, "CABINET REFERENCE", {cabinet.x + 14.0F, below_art + 9.0F,
            cabinet.width - 28.0F, 21.0F}, 13.0F);
    centered(drawing, "ROTARY AUDIO NOT CONNECTED", {cabinet.x + 14.0F, below_art + 31.0F,
             cabinet.width - 28.0F, 18.0F}, 10.0F, kMuted);
    const UiRect card{cabinet.x + 14.0F, below_art + 61.0F, cabinet.width - 28.0F,
                      cabinet.y + cabinet.height - 14.0F - below_art - 61.0F};
    drawing.rect(card, {19, 21, 18});
    drawing.line(card.x, card.y, card.x + card.width, card.y, kMetalEdge);
    const float x = card.x + 12.0F;
    const float width = card.width - 24.0F;
    text_line(drawing, "INSTRUMENT / DEVICE STATUS", {x, card.y + 10.0F, width, 14.0F}, 10.0F, kUiBrass);
    const bool expanded = card.height >= 255.0F;
    if (expanded) {
        text_line(drawing, info.audio_running ? "AUDIO RUNNING" : "AUDIO STOPPED",
                  {x, card.y + 36.0F, width, 18.0F}, 13.0F, info.audio_running ? kGreen : kRed);
        text_line(drawing, audio_configuration(info), {x, card.y + 56.0F, width, 16.0F}, 11.0F, kUiIvory);
        const std::string device = info.device_name.empty() ? "Default output" : std::string(info.device_name);
        wrapped(drawing, device + (info.audio_driver.empty() ? "" : " / " + std::string(info.audio_driver)),
                {x, card.y + 75.0F, width, 31.0F}, 10.5F, kMuted);
        text_line(drawing, midi_state(info), {x, card.y + 112.0F, width, 18.0F}, 13.0F,
                  info.midi_open ? kGreen : kMuted);
        wrapped(drawing, info.midi_port.empty() ? info.midi_backend : info.midi_port,
                {x, card.y + 133.0F, width, 30.0F}, 10.5F, kUiIvory);
        wrapped(drawing, info.midi_status, {x, card.y + 165.0F, width, 32.0F}, 10.0F, kMuted);
        text_line(drawing, "MIDI packets observed: " + std::to_string(info.midi_messages),
                  {x, card.y + 199.0F, width, 14.0F}, 10.0F, kMuted);
        text_line(drawing, "SCANNER / CHORUS: NOT CONNECTED", {x, card.y + 221.0F, width, 14.0F}, 10.0F, kMuted);
        text_line(drawing, "ROTARY AUDIO: NOT CONNECTED", {x, card.y + 239.0F, width, 14.0F}, 10.0F, kMuted);
    } else {
        const std::string audio = std::string(info.audio_running ? "AUDIO RUNNING / " : "AUDIO STOPPED / ") + audio_configuration(info);
        text_line(drawing, audio, {x, card.y + 31.0F, width, 14.0F}, 10.0F, info.audio_running ? kGreen : kRed);
        text_line(drawing, midi_state(info), {x, card.y + 51.0F, width, 14.0F}, 10.0F, info.midi_open ? kGreen : kMuted);
        text_line(drawing, "SCANNER / CHORUS: NOT CONNECTED", {x, card.y + 71.0F, width, 14.0F}, 10.0F, kMuted);
        text_line(drawing, "ROTARY AUDIO: NOT CONNECTED", {x, card.y + 91.0F, width, 14.0F}, 10.0F, kMuted);
        if (card.height >= 151.0F) wrapped(drawing, info.midi_status,
            {x, card.y + 118.0F, width, card.height - 126.0F}, 10.0F, kMuted);
    }
}

void midi_overlay(Drawing& drawing, const UiLayout& layout, const InstrumentViewInfo& info) {
    const auto boxes = midi_overlay_layout(layout.width, layout.height);
    panel(drawing, boxes.panel);
    const float x = boxes.panel.x + 28.0F;
    const float y = boxes.panel.y;
    drawing.text("MIDI input", x, y + 22.0F, 28.0F, kUiIvory, TextFace::Serif);
    button(drawing, boxes.close, "CLOSE");
    text_line(drawing, "INPUT PORT / EXACT NAME", {x, y + 73.0F, boxes.panel.width - 56.0F, 16.0F}, 11.0F, kUiBrass);
    std::string_view choice = "No input";
    if (info.selected_midi_port < info.midi_choices.size()) choice = info.midi_choices[info.selected_midi_port];
    const UiRect port{boxes.previous_port.x + boxes.previous_port.width + 12.0F, y + 98.0F,
                       boxes.next_port.x - boxes.previous_port.x - boxes.previous_port.width - 24.0F, 77.0F};
    drawing.rect(inset({port.x - 6.0F, port.y - 5.0F, port.width + 12.0F, port.height + 10.0F}, 1.0F), {13, 15, 13});
    wrapped(drawing, choice, port, 12.0F, kUiIvory);
    button(drawing, boxes.previous_port, "<");
    button(drawing, boxes.next_port, ">");
    text_line(drawing, "Close and reopen to refresh ports. Full exact names: --list-midi",
              {x, y + 184.0F, boxes.panel.width - 56.0F, 16.0F}, 10.5F, kMuted);
    constexpr std::array<std::string_view, 3> names{"UPPER CHANNEL", "LOWER CHANNEL", "PEDAL CHANNEL"};
    const std::array<UiRect, 3> channels{boxes.upper_channel, boxes.lower_channel, boxes.pedal_channel};
    for (std::size_t index = 0; index < channels.size(); ++index) {
        const auto& bounds = channels[index];
        text_line(drawing, names[index], {bounds.x, bounds.y - 22.0F, bounds.width, 16.0F}, 11.0F, kUiBrass);
        button(drawing, bounds, std::to_string(info.selected_midi_channels[index]));
    }
    const auto& selected = info.selected_midi_channels;
    const bool distinct = selected[0] != selected[1] && selected[0] != selected[2] && selected[1] != selected[2];
    text_line(drawing, distinct ? "Three distinct wire channels, 1-16. Click or use arrows to change." :
              "Channels must be distinct. Change the repeated channel before Apply.",
              {x, y + 289.0F, boxes.panel.width - 56.0F, 18.0F}, 11.0F, distinct ? kMuted : kRed);
    const UiRect status{x, y + 322.0F, boxes.panel.width - 56.0F, 83.0F};
    drawing.rect(status, {17, 19, 16});
    text_line(drawing, midi_state(info) + (info.midi_backend.empty() ? "" : " / " + std::string(info.midi_backend)),
              {x + 12.0F, status.y + 8.0F, status.width - 24.0F, 18.0F}, 12.0F,
              info.midi_open ? kGreen : kUiBrass);
    wrapped(drawing, info.midi_status, {x + 12.0F, status.y + 31.0F, status.width - 24.0F, 45.0F}, 11.5F, kUiIvory);
    button(drawing, boxes.apply, "APPLY / CONNECT", distinct && info.midi_available);
    button(drawing, boxes.disconnect, "DISCONNECT");
    text_line(drawing, "Apply changes the MIDI route. Disconnect releases MIDI-owned notes.",
              {x, y + 477.0F, boxes.panel.width - 56.0F, 16.0F}, 11.0F, kMuted);
    text_line(drawing, "Tab / Shift+Tab selects a control. Enter activates. Escape closes.",
              {x, y + 495.0F, boxes.panel.width - 56.0F, 16.0F}, 10.5F, kMuted);
}

void overlay(Drawing& drawing, const UiLayout& layout, const InstrumentViewInfo& info) {
    if (info.overlay == ViewOverlay::None) return;
    drawing.rect({0, 0, layout.width, layout.height}, {0, 0, 0, 185});
    if (info.overlay == ViewOverlay::Midi) {
        midi_overlay(drawing, layout, info);
        return;
    }
    const auto boxes = audio_overlay_layout(layout.width, layout.height);
    panel(drawing, boxes.panel);
    const float x = boxes.panel.x + 28.0F;
    const float y = boxes.panel.y + 22.0F;
    drawing.text(info.overlay == ViewOverlay::Audio ? "Audio output" : "Playing the instrument",
                  x, y, 28.0F, kUiIvory, TextFace::Serif);
    button(drawing, boxes.close, "CLOSE");
    if (info.overlay == ViewOverlay::Help) {
        constexpr std::array<std::string_view, 10> help{
            "A W S E D F T G Y H U J K O L P ;   Play notes",
            "F1 / F2 / F3   Upper / Lower / Pedals",
            "[ / ]   Shift the keyboard octave",
            "Tab / Shift+Tab   Move between controls",
            "Arrow keys   Adjust controls or move on a manual",
            "Space   Hold the focused key; release to stop",
            "EDIT A/B prepares a bank. PLAY A/B selects its sound.",
            "CANCEL mutes one manual route. PANIC releases all notes.",
            "Ctrl+M   MIDI input, port and three wire-channel settings",
            "Saves contain controls, not held keys or sound history."};
        for (std::size_t index = 0; index < help.size(); ++index) {
            text_line(drawing, help[index], {x, y + 64.0F + static_cast<float>(index) * 29.0F,
                      boxes.panel.width - 56.0F, 22.0F}, 14.0F, index < 6 ? kUiIvory : kMuted);
        }
        return;
    }
    drawing.text("OUTPUT DEVICE", x, y + 60.0F, 12.0F, kUiBrass);
    std::string_view choice = "Default output";
    if (info.selected_device < info.audio_choices.size()) choice = info.audio_choices[info.selected_device];
    wrapped(drawing, choice, {x + 48.0F, y + 88.0F, boxes.panel.width - 152.0F, 47.0F}, 13.0F, kUiIvory);
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

void paint_header(Drawing& drawing, const UiLayout& layout) {
    panel(drawing, layout.header, false);
    float title_left = layout.header.x;
    float title_right = layout.header.x + layout.header.width;
    for (std::size_t index = 0; index < layout.control_count; ++index) {
        const auto& control = layout.controls[index];
        if (control.id.kind == UiControlKind::Help) title_left = control.bounds.x + control.bounds.width + 16.0F;
        if (control.id.kind == UiControlKind::AudioSettings) title_right = control.bounds.x - 16.0F;
    }
    constexpr std::string_view title = "TONEWHEEL ATLAS";
    float size = layout.show_cabinet ? 40.0F : 28.0F;
    const float natural_width = drawing.text_width(title, size, TextFace::Serif);
    if (natural_width > title_right - title_left) size *= (title_right - title_left) / natural_width;
    const float width = drawing.text_width(title, size, TextFace::Serif);
    const float desired_x = layout.header.x + (layout.header.width - width) / 2.0F;
    const float x = std::clamp(desired_x, title_left, std::max(title_left, title_right - width));
    const float y = layout.header.y + (layout.show_cabinet ? 4.0F : 8.0F);
    drawing.text(title, x + 1.0F, y + 2.0F, size, {4, 5, 4}, TextFace::Serif);
    drawing.text(title, x, y, size, kUiBrass, TextFace::Serif);
    centered(drawing, "NOMINAL DRY ORGAN", {title_left, layout.header.y + (layout.show_cabinet ? 58.0F : 48.0F),
             title_right - title_left, 20.0F}, 11.0F, kUiIvory);
}

void paint_footer(Drawing& drawing, const UiModel& model, const InstrumentViewInfo& info) {
    const auto& footer = model.layout().footer;
    const auto& view = model.view();
    drawing.gradient(footer, {29, 29, 24}, {18, 20, 17});
    drawing.line(footer.x, footer.y, footer.x + footer.width, footer.y, kMetalEdge);
    drawing.rounded({footer.x + 6.0F, footer.y + 8.0F, 6.0F, 6.0F}, 3.0F,
                    info.audio_running ? kGreen : kRed);
    std::string audio = info.audio_running ? "AUDIO RUNNING" : "AUDIO STOPPED";
    if (info.sample_rate != 0) audio += "  " + audio_configuration(info);
    audio += "  /  " + midi_state(info);
    const float meter_width = 84.0F;
    const float meter_x = footer.x + footer.width - meter_width - 12.0F;
    text_line(drawing, audio, {footer.x + 20.0F, footer.y + 4.0F,
              footer.width - 220.0F, 15.0F}, 10.0F, kUiIvory);
    if (view.controls_dirty) drawing.text("UNSAVED", meter_x - 67.0F, footer.y + 4.0F, 9.0F, kUiBrass);
    drawing.rect({meter_x, footer.y + 7.0F, meter_width, 5.0F}, {49, 50, 42});
    drawing.rect({meter_x, footer.y + 7.0F, meter_width * std::clamp(view.applied.peak, 0.0F, 1.0F), 5.0F},
                 info.clipped_samples > 0 ? kRed : kGreen);
    std::string_view status;
    if (!info.status_message.empty()) status = info.status_message;
    else if (view.input_recovery) status = "Input recovered. Release held keys before playing again.";
    else if (view.controls_pending) status = "Applying controls...";
    else status = "A W S E D F T G Y H U J K O L P ;  play  /  F1-F3 target  /  [ ] octave  /  Ctrl+M MIDI";
    text_line(drawing, status, {footer.x + 20.0F, footer.y + 21.0F, footer.width - 32.0F, 14.0F}, 9.5F, kMuted);
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

MidiOverlayLayout midi_overlay_layout(float width, float height) noexcept {
    const UiRect panel_rect{(width - 740.0F) / 2.0F, (height - 520.0F) / 2.0F, 740.0F, 520.0F};
    return {panel_rect,
            {panel_rect.x + 28.0F, panel_rect.y + 113.0F, 40.0F, 42.0F},
            {panel_rect.x + 672.0F, panel_rect.y + 113.0F, 40.0F, 42.0F},
            {panel_rect.x + 28.0F, panel_rect.y + 239.0F, 212.0F, 38.0F},
            {panel_rect.x + 264.0F, panel_rect.y + 239.0F, 212.0F, 38.0F},
            {panel_rect.x + 500.0F, panel_rect.y + 239.0F, 212.0F, 38.0F},
            {panel_rect.x + 28.0F, panel_rect.y + 424.0F, 252.0F, 40.0F},
            {panel_rect.x + 296.0F, panel_rect.y + 424.0F, 188.0F, 40.0F},
            {panel_rect.x + 628.0F, panel_rect.y + 24.0F, 84.0F, 32.0F}};
}

void paint_instrument(Drawing& drawing, const UiModel& model, const InstrumentViewInfo& info) {
    const auto& layout = model.layout();
    const auto& view = model.view();
    drawing.clear(kUiWalnut);
    wood(drawing, {0, 0, layout.width, layout.height});
    const float margin = layout.header.x;
    const bool left_art = drawing.reference_art(ReferenceArt::LeftWoodCheek, {0, 0, margin, layout.height});
    const bool right_art = drawing.reference_art(ReferenceArt::RightWoodCheek,
        {layout.width - margin, 0, margin, layout.height});
    (void)left_art;
    (void)right_art;
    drawing.rounded({margin - 7.0F, 8.0F, layout.width - 2.0F * margin + 14.0F,
                     layout.height - 24.0F}, 9.0F, {10, 11, 9});
    drawing.line(margin - 4.0F, 17.0F, margin - 4.0F, layout.height - 23.0F, {143, 89, 48, 160});
    drawing.line(layout.width - margin + 3.0F, 17.0F, layout.width - margin + 3.0F,
                 layout.height - 23.0F, {143, 89, 48, 160});
    paint_header(drawing, layout);
    panel(drawing, layout.performance_panel);
    const auto& performance = layout.performance_panel;
    const float divider = performance.x + performance.width * 0.46F;
    drawing.line(divider, performance.y + 12.0F, divider, performance.y + performance.height - 12.0F, kMetalEdge);
    const bool eligible = view.applied.controls.route_enabled[0] &&
        view.applied.controls.selected_banks[0] == DrawbarBank::B;
    const bool separate_eligibility = performance.height >= 92.0F;
    heading(drawing, separate_eligibility ? "PERCUSSION" : eligible ? "PERCUSSION / UPPER B ACTIVE" : "PERCUSSION / UPPER B ONLY",
            {performance.x + 17.0F, performance.y + 3.0F, divider - performance.x - 34.0F, 18.0F},
            separate_eligibility ? 13.5F : 10.5F);
    if (separate_eligibility) centered(drawing, eligible ? "UPPER B ROUTE ACTIVE" : "REQUIRES SOUNDING UPPER B",
        {performance.x + 12.0F, performance.y + 73.0F, divider - performance.x - 24.0F, 16.0F}, 9.0F, eligible ? kGreen : kMuted);
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        const auto& bounds = layout.registration_panels[manual];
        panel(drawing, bounds);
        const std::string state = std::string("EDIT ") + (view.edited_banks[manual] == DrawbarBank::A ? "A / " : "B / ") +
            (view.applied.controls.route_enabled[manual] ?
             (view.applied.controls.selected_banks[manual] == DrawbarBank::A ? "SOUNDING A" : "SOUNDING B") : "CANCELLED");
        const float state_width = std::min(bounds.width * 0.43F, drawing.text_width(state, 9.5F) + 8.0F);
        heading(drawing, manual == 0 ? "UPPER DRAWBARS" : "LOWER DRAWBARS",
                {bounds.x + 16.0F, bounds.y + 3.0F, bounds.width - state_width - 32.0F, 23.0F}, 14.0F);
        centered(drawing, state, {bounds.x + bounds.width - state_width - 14.0F, bounds.y + 5.0F, state_width, 20.0F},
                 9.5F, view.applied.controls.route_enabled[manual] ? kUiBrass : kMuted);
        if (layout.bank_controls_in_cheeks) {
            const auto& rail = layout.manual_rail_panels[manual];
            wood(drawing, rail);
            drawing.rect(inset(rail, 5.0F), {25, 24, 20});
            centered(drawing, manual == 0 ? "UPPER / SWELL" : "LOWER / GREAT",
                     {rail.x + 8.0F, rail.y + 3.0F, rail.width - 16.0F, 17.0F}, 10.5F, kUiBrass, TextFace::Serif);
            if (rail.height >= 126.0F) centered(drawing, "61 PLAYING KEYS",
                {rail.x + 8.0F, rail.y + 109.0F, rail.width - 16.0F, 16.0F}, 8.5F, kMuted);
        }
    }
    drawing.gradient(layout.keyboard_toolbar, {30, 31, 26}, {18, 20, 17});
    const std::string octave = view.keyboard_target == UiTarget::Pedals ?
        "COMPUTER KEYS / PEDAL OCTAVE " + std::to_string(view.pedal_octave) :
        "COMPUTER KEYS / BASE C" + std::to_string(static_cast<int>(view.manual_base_midi) / 12 - 1);
    text_line(drawing, octave, {layout.keyboard_toolbar.x + 478.0F, layout.keyboard_toolbar.y + 7.0F,
              layout.keyboard_toolbar.width - 490.0F, 15.0F}, 10.0F, kMuted);
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        const auto& bounds = layout.manual_panels[manual];
        panel(drawing, bounds, false);
        centered(drawing, manual == 0 ? "UPPER MANUAL" : "LOWER MANUAL",
                 {bounds.x + 12.0F, bounds.y + 3.0F, bounds.width - 24.0F, 16.0F}, 9.5F, kUiBrass, TextFace::Serif);
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
    panel(drawing, layout.pedal_panel, false);
    centered(drawing, "PEDALBOARD / 25 NOTES", {layout.pedal_panel.x + 12.0F, layout.pedal_panel.y + 3.0F,
             layout.pedal_panel.width - 24.0F, 16.0F}, 9.5F, kUiBrass, TextFace::Serif);
    for (const bool accidental : {false, true}) {
        for (std::size_t index = 0; index < kPedalCount; ++index) {
            const auto& key = layout.pedal_keys[index];
            if (key.accidental == accidental) {
                paint_key(drawing, key, view.applied.held_pedals[index],
                          view.focus.kind == UiControlKind::PedalKey && view.focus.index == index);
            }
        }
    }
    paint_cabinet(drawing, layout, info);
    paint_controls(drawing, model);
    paint_footer(drawing, model, info);
    overlay(drawing, layout, info);
}

} // namespace hammond::standalone
