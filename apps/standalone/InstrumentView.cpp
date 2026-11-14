#include "InstrumentView.h"
#include "InspectionModel.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <string>

namespace hammond::standalone {
namespace {

constexpr UiColor kMuted{166, 159, 142};
constexpr UiColor kGreen{157, 187, 143};
constexpr UiColor kRed{232, 139, 110};
constexpr UiColor kMetalEdge{91, 78, 59};
constexpr UiColor kBrownCap{129, 77, 43};
constexpr UiColor kIvoryCap{234, 214, 179};
constexpr UiColor kBlackCap{36, 35, 32};
constexpr UiColor kPresetPending{235, 169, 73};

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
              float size, UiColor color, TextFace face = TextFace::Sans,
              float padding = 3.0F) {
    if (!(bounds.width > 0.0F && bounds.height > 0.0F)) return;
    size = std::min(size, bounds.height / 1.2F);
    const float width = drawing.text_width(value, size, face);
    if (width > bounds.width - 2.0F * padding && width > 0.0F) {
        size *= std::max(0.1F, bounds.width - 2.0F * padding) / width;
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

void panel(Drawing& drawing, UiRect bounds, bool screws = true, bool flat = false) {
    if (!(bounds.width > 0.0F && bounds.height > 0.0F)) return;
    if (flat) {
        drawing.rect(bounds, {27, 29, 28});
        drawing.outline(bounds, {82, 79, 67});
        return;
    }
    drawing.shadow(bounds, 5.0F);
    drawing.rounded(bounds, 6.0F, {7, 7, 7});
    drawing.rounded(inset(bounds, 1.0F), 5.0F, kMetalEdge);
    drawing.rounded(inset(bounds, 2.0F), 4.0F, {14, 14, 14});
    drawing.gradient(inset(bounds, 4.0F), {35, 34, 33}, {18, 18, 18});
    // Restrained procedural grain belongs to the live charcoal surface, not
    // to a stretched image of controls. It never changes their shared bounds.
    const auto rows = static_cast<int>(std::max(0.0F, bounds.height - 14.0F));
    const auto columns = static_cast<int>(std::max(0.0F, bounds.width - 14.0F));
    const int grain_step = std::max(4, static_cast<int>(std::max(bounds.width, bounds.height) / 180.0F));
    for (int row = 1; row < rows; row += grain_step) {
        for (int column = 1; column < columns; column += grain_step * 3) {
            const auto grain = static_cast<std::uint32_t>(row) * 1973U +
                static_cast<std::uint32_t>(column) * 9277U;
            const float x = bounds.x + 7.0F + static_cast<float>(column) +
                static_cast<float>((grain >> 5U) % 3U);
            const float y = bounds.y + 7.0F + static_cast<float>(row);
            drawing.rect({x, y, 1.0F, 1.0F},
                         {231, 223, 208, static_cast<std::uint8_t>(3U + grain % 5U)});
            drawing.rect({x + 3.0F, y + 1.0F, 2.0F, 1.0F}, {0, 0, 0, 17});
        }
    }
    drawing.line(bounds.x + 7.0F, bounds.y + 3.0F,
                 bounds.x + bounds.width - 7.0F, bounds.y + 3.0F, {147, 133, 111, 104});
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
            TextFace face = TextFace::Sans, bool ivory = false, bool flat = false) {
    const bool light = selected || ivory;
    const UiColor cap = selected ? UiColor{238, 204, 145} : ivory ? kIvoryCap : UiColor{45, 41, 36};
    if (flat) {
        drawing.rect(bounds, cap);
        drawing.outline(bounds, selected ? kUiBrass : kMetalEdge);
        centered(drawing, label, inset(bounds, 3.0F), 11.0F,
                 warning ? (light ? UiColor{112, 43, 24} : kRed) : light ? UiColor{35, 29, 21} : kUiIvory,
                 TextFace::Sans);
        return;
    }
    drawing.rounded(bounds, 5.0F, {5, 5, 5});
    drawing.rounded(inset(bounds, 1.0F), 4.0F, selected ? UiColor{137, 105, 62} : UiColor{77, 69, 56});
    drawing.rounded(inset(bounds, 2.0F), 3.0F, {18, 17, 15});
    const float recess = selected ? 1.0F : 0.0F;
    const UiRect cap_bounds{bounds.x + 4.0F, bounds.y + 3.0F + recess,
                            bounds.width - 10.0F, bounds.height - 8.0F - recess};
    drawing.rounded({cap_bounds.x + 2.0F, cap_bounds.y + 3.0F,
                     cap_bounds.width, cap_bounds.height}, 3.0F, {0, 0, 0, 210});
    drawing.rounded(cap_bounds, 3.0F, shade(cap, -35));
    const float front = std::clamp(bounds.height * 0.12F, 3.0F, 5.0F);
    const UiRect face_bounds{cap_bounds.x + 1.0F, cap_bounds.y + 1.0F,
                             cap_bounds.width - 2.0F, cap_bounds.height - front - 1.0F};
    // The shallow light band and softer lower face keep a live tablet legible
    // without the bright double frame competing with its label.
    drawing.gradient(face_bounds, shade(cap, 20), shade(cap, -7));
    drawing.gradient({face_bounds.x, face_bounds.y, face_bounds.width,
                      std::min(5.0F, face_bounds.height * 0.25F)},
                     light ? UiColor{255, 248, 225, 75} : UiColor{190, 174, 147, 42},
                     {255, 244, 219, 0});
    drawing.line(face_bounds.x + 1.0F, face_bounds.y, face_bounds.x + face_bounds.width - 1.0F,
                 face_bounds.y, light ? UiColor{255, 245, 218} : UiColor{122, 108, 88});
    drawing.gradient({face_bounds.x, face_bounds.y + face_bounds.height,
                      face_bounds.width, front}, shade(cap, -17), shade(cap, -42));
    drawing.line(face_bounds.x, face_bounds.y + face_bounds.height,
                 face_bounds.x + face_bounds.width, face_bounds.y + face_bounds.height,
                 shade(cap, 14));
    centered(drawing, label, inset(bounds, 4.0F), face == TextFace::Serif ? 15.0F : 11.0F,
             warning ? (light ? UiColor{112, 43, 24} : kRed) : light ? UiColor{35, 29, 21} : kUiIvory, face);
}

[[nodiscard]] std::string_view button_label(const UiControlId& id) noexcept {
    switch (id.kind) {
    case UiControlKind::EditBank: return id.bank == DrawbarBank::A ? "EDIT A" : "EDIT B";
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
    case UiControlKind::Workspace:
        return id.index == 0 ? "PLAY" : id.index == 1 ? "ROTARY" : "SERVICE";
    case UiControlKind::Presentation: return "FLAT";
    default: return {};
    }
}

[[nodiscard]] bool header_button(UiControlKind kind) noexcept {
    return kind == UiControlKind::SaveControls || kind == UiControlKind::LoadControls ||
        kind == UiControlKind::Help || kind == UiControlKind::AudioSettings ||
        kind == UiControlKind::MidiSettings || kind == UiControlKind::Panic ||
        kind == UiControlKind::Workspace || kind == UiControlKind::Presentation;
}

void drawbar(Drawing& drawing, const UiControlGeometry& geometry,
             std::uint8_t value, std::string_view label, UiColor cap, bool flat) {
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
    const float y = track.y + track.height * static_cast<float>(value) / 8.0F;
    const UiRect knob{center - cap_width / 2.0F, y - half_height, cap_width, cap_height};
    if (flat) {
        drawing.rect(slot, {13, 15, 14});
        drawing.rect({center - 1.0F, track.y, 2.0F, track.height}, kMuted);
        for (int tick = 0; tick <= 8; ++tick) {
            const float tick_y = track.y + track.height * static_cast<float>(tick) / 8.0F;
            drawing.line(slot.x + 1.0F, tick_y, slot.x + 4.0F, tick_y, kMuted);
        }
        drawing.rect(knob, cap);
        drawing.outline(knob, shade(cap, 42));
        centered(drawing, std::to_string(value), geometry.value_bounds, 13.0F, kUiBrass);
        return;
    }
    drawing.rounded(slot, 2.0F, {5, 5, 5});
    drawing.line(slot.x, slot.y + 1.0F, slot.x, slot.y + slot.height - 1.0F, {63, 58, 49});
    drawing.line(slot.x + slot.width - 1.0F, slot.y, slot.x + slot.width - 1.0F,
                 slot.y + slot.height, {36, 34, 30});
    drawing.gradient({center - 1.75F, track.y, 3.5F, track.height}, {79, 75, 67}, {30, 30, 28});
    for (int tick = 0; tick <= 8; ++tick) {
        const float tick_y = track.y + track.height * static_cast<float>(tick) / 8.0F;
        drawing.line(slot.x + 1.0F, tick_y, slot.x + 3.0F, tick_y, {103, 94, 72});
    }
    drawing.gradient({center - 1.75F, track.y, 3.5F, y - track.y}, {144, 135, 116}, {83, 77, 64});
    drawing.line(center - 0.75F, track.y, center - 0.75F, y, {192, 179, 153, 125});
    drawing.rounded({knob.x - 1.0F, knob.y + 3.0F, knob.width + 3.0F, knob.height + 1.0F}, 3.0F, {0, 0, 0, 210});
    drawing.rounded(knob, 3.0F, shade(cap, -38));
    drawing.gradient({knob.x + 1.0F, knob.y + 2.0F, knob.width - 2.0F, knob.height - 10.0F},
                     shade(cap, 29), shade(cap, -2));
    drawing.line(knob.x + 1.0F, knob.y + 4.0F, knob.x + 1.0F,
                 knob.y + knob.height - 10.0F, shade(cap, 48));
    drawing.line(knob.x + knob.width - 2.0F, knob.y + 4.0F,
                 knob.x + knob.width - 2.0F, knob.y + knob.height - 3.0F, shade(cap, -48));
    drawing.gradient({knob.x + 1.0F, knob.y + knob.height - 8.0F, knob.width - 2.0F, 6.0F},
                     shade(cap, -13), shade(cap, -34));
    drawing.line(knob.x + 3.0F, knob.y + 2.0F, knob.x + knob.width - 3.0F, knob.y + 2.0F, shade(cap, 65));
    drawing.line(knob.x + 2.0F, knob.y + knob.height - 9.0F,
                 knob.x + knob.width - 2.0F, knob.y + knob.height - 9.0F, shade(cap, 34));
    centered(drawing, std::to_string(value), geometry.value_bounds, 13.0F, kUiBrass);
}

[[nodiscard]] bool preset_accidental(std::uint8_t index) noexcept {
    return index == 1 || index == 3 || index == 6 || index == 8 || index == 10;
}

[[nodiscard]] bool pending_preset(const UiViewState& view, Manual manual,
                                  PresetSelection& desired) noexcept {
    PresetSelection applied{};
    return view.controls_pending &&
        control_preset_selection(view.controls, manual, desired) &&
        control_preset_selection(view.applied.controls, manual, applied) && desired != applied;
}

[[nodiscard]] std::string registration_caption(const UiViewState& view,
                                               Manual manual, bool compact = false) {
    const auto index = manual_index(manual);
    std::string result = std::string("EDIT ") +
        (view.edited_banks[index] == DrawbarBank::A ? "A / " : "B / ");
    PresetSelection applied{};
    if (!control_preset_selection(view.applied.controls, manual, applied)) return result + "ROUTE UNAVAILABLE";
    if (applied == PresetSelection::Cancel) return result + "CANCELLED";
    if (!compact) result += "SOUNDING ";
    if (applied != PresetSelection::BankA && applied != PresetSelection::BankB) result += "FIXED ";
    result += preset_selection_label(applied);
    return result;
}

// Use the exposed natural region for independent focus/request outlines, so
// the last paint pass never crosses an overlapping ivory accidental.
[[nodiscard]] UiRect preset_indicator_bounds(const UiControlGeometry& geometry,
                                              float amount) noexcept {
    if (preset_accidental(geometry.id.index)) return inset(geometry.bounds, amount);
    const auto& bounds = geometry.bounds;
    return {bounds.x + amount, bounds.y + bounds.height * 0.62F + amount,
            bounds.width - 2.0F * amount, bounds.height * 0.38F - 2.0F * amount};
}

void paint_preset_key(Drawing& drawing, const UiControlGeometry& geometry, bool selected, bool flat) {
    const auto& bounds = geometry.bounds;
    const bool ivory = preset_accidental(geometry.id.index);
    // C is a momentary Cancel command, never a latched route.
    selected = selected && geometry.id.index != 0;
    if (flat) {
        drawing.rect(bounds, ivory ? kIvoryCap : UiColor{28, 29, 27});
        drawing.outline(bounds, {6, 7, 6});
        if (selected) drawing.rect({bounds.x + 2.0F, bounds.y + 3.0F,
            std::max(1.0F, bounds.width - 4.0F), 2.0F}, kUiBrass);
        centered(drawing, preset_selection_label(static_cast<PresetSelection>(geometry.id.index)),
                 geometry.label_bounds, 9.0F, ivory ? UiColor{37, 29, 20} : kUiIvory,
                 TextFace::Sans, 0.0F);
        return;
    }
    const float recess = selected ? 2.0F : 0.0F;
    const float front = std::clamp(bounds.height * 0.16F, 6.0F, 12.0F);
    drawing.rect(bounds, {5, 5, 5});
    const UiRect face{bounds.x + 1.0F, bounds.y + recess,
                      bounds.width - 2.0F, bounds.height - front - recess};
    drawing.gradient(face, ivory ? UiColor{254, 238, 204} : UiColor{49, 46, 41},
                     ivory ? UiColor{225, 204, 168} : UiColor{20, 20, 19});
    drawing.line(face.x, face.y + 1.0F, face.x, face.y + face.height - 1.0F,
                 ivory ? UiColor{255, 247, 222} : UiColor{101, 92, 75});
    drawing.line(bounds.x + bounds.width - 2.0F, face.y + 1.0F,
                 bounds.x + bounds.width - 2.0F, bounds.y + bounds.height - 2.0F,
                 ivory ? UiColor{155, 130, 93} : UiColor{9, 9, 9});
    drawing.gradient({face.x, bounds.y + bounds.height - front, face.width, front - 1.0F},
                     ivory ? UiColor{209, 183, 141} : UiColor{39, 36, 31},
                     ivory ? UiColor{148, 119, 78} : UiColor{12, 12, 11});
    drawing.line(face.x, bounds.y + bounds.height - front,
                 face.x + face.width, bounds.y + bounds.height - front,
                 ivory ? UiColor{251, 230, 191} : UiColor{79, 69, 52});
    drawing.gradient({face.x, face.y, face.width, 4.0F}, {0, 0, 0, 105}, {0, 0, 0, 0});
    if (selected) {
        drawing.rect({face.x + 1.0F, face.y + 3.0F,
                      std::max(1.0F, face.width - 2.0F), 2.0F}, kUiBrass);
    }
    centered(drawing, preset_selection_label(static_cast<PresetSelection>(geometry.id.index)),
             geometry.label_bounds, 9.0F, ivory ? UiColor{37, 29, 20} : kUiIvory,
             TextFace::Sans, 0.0F);
}

void paint_preset_focus(Drawing& drawing, const UiControlGeometry& geometry) {
    const auto bounds = preset_indicator_bounds(geometry, 2.0F);
    const auto paint = [&] {
        drawing.outline(bounds, {5, 6, 6}, 3.0F);
        drawing.outline(inset(bounds, 1.0F), kUiFocusCyan, 1.0F);
    };
    // A natural's single-letter pitch fits between the side strokes. Its
    // shortest exposed region is almost all label bounds, so repainting that
    // whole rectangle would erase the independent focus indicator.
    if (!preset_accidental(geometry.id.index)) {
        paint();
        return;
    }
    // A 12-unit accidental needs an opening through the stroke at its label.
    // Clip the focus ink above the original label; redrawing a scaled glyph
    // through a tighter clip can change its sampling at fractional positions.
    // The contracted ring and hit bounds remain unchanged, and the original
    // glyph/material pixels are never painted twice. Preserve a caller's clip.
    const int left = static_cast<int>(std::floor(geometry.bounds.x));
    const int top = static_cast<int>(std::floor(geometry.bounds.y));
    SDL_Rect focus_clip{left, top,
        static_cast<int>(std::ceil(geometry.bounds.x + geometry.bounds.width)) - left,
        static_cast<int>(std::floor(geometry.label_bounds.y)) - top};
    auto* renderer = drawing.renderer();
    const bool clipped = SDL_RenderIsClipEnabled(renderer) == SDL_TRUE;
    SDL_Rect previous{};
    SDL_RenderGetClipRect(renderer, &previous);
    float scale_x = 1.0F;
    float scale_y = 1.0F;
    SDL_RenderGetScale(renderer, &scale_x, &scale_y);
    // A scaled integer clip read can lose an odd physical edge. Intersect in
    // output pixels, retaining the original physical clip for exact restoration.
    SDL_RenderSetScale(renderer, 1.0F, 1.0F);
    SDL_Rect previous_physical{};
    SDL_RenderGetClipRect(renderer, &previous_physical);
    SDL_RenderSetScale(renderer, scale_x, scale_y);
    SDL_RenderSetClipRect(renderer, &focus_clip);
    SDL_RenderSetScale(renderer, 1.0F, 1.0F);
    SDL_RenderGetClipRect(renderer, &focus_clip);
    const bool visible = !clipped ||
        SDL_IntersectRect(&focus_clip, &previous_physical, &focus_clip) == SDL_TRUE;
    SDL_RenderSetClipRect(renderer, &focus_clip);
    SDL_RenderSetScale(renderer, scale_x, scale_y);
    if (visible) paint();
    // Keep a caller's ordinary logical clip when its round trip is exact; this
    // also retains fractional physical coordinates from logical 1.5x clips.
    SDL_RenderSetClipRect(renderer, clipped ? &previous : nullptr);
    SDL_RenderSetScale(renderer, 1.0F, 1.0F);
    SDL_Rect restored{};
    SDL_RenderGetClipRect(renderer, &restored);
    if (clipped && SDL_RectEquals(&restored, &previous_physical) == SDL_FALSE)
        SDL_RenderSetClipRect(renderer, &previous_physical);
    SDL_RenderSetScale(renderer, scale_x, scale_y);
}

void paint_presets(Drawing& drawing, const UiModel& model) {
    const auto& view = model.view();
    const auto& layout = model.layout();
    if (!ui_control_visible(layout, {UiControlKind::PresetKey})) return;
    const bool flat = view.presentation == UiPresentation::Flat;
    std::array<PresetSelection, kManualCount> applied{};
    std::array<bool, kManualCount> valid{};
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        valid[manual] = control_preset_selection(view.applied.controls,
                                                static_cast<Manual>(manual), applied[manual]);
        const auto& panel = layout.preset_key_panels[manual];
        drawing.rect({panel.x - 1.0F, panel.y - 3.0F, panel.width + 2.0F, panel.height + 4.0F}, {4, 4, 4});
    }
    // The semantic control array is in pitch order; paint order is explicitly
    // natural first, accidental second, independently of that array order.
    for (const bool accidental : {false, true}) {
        for (std::size_t index = 0; index < layout.control_count; ++index) {
            const auto& geometry = layout.controls[index];
            if (!ui_control_visible(layout, geometry.id) || geometry.id.kind != UiControlKind::PresetKey ||
                preset_accidental(geometry.id.index) != accidental) continue;
            const auto manual = manual_index(geometry.id.manual);
            const bool selected = valid[manual] && applied[manual] != PresetSelection::Cancel &&
                static_cast<std::uint8_t>(applied[manual]) == geometry.id.index;
            paint_preset_key(drawing, geometry, selected, flat);
        }
    }
    for (std::size_t index = 0; index < layout.control_count; ++index) {
        const auto& geometry = layout.controls[index];
        if (!ui_control_visible(layout, geometry.id) || geometry.id.kind != UiControlKind::PresetKey) continue;
        PresetSelection desired{};
        if (pending_preset(view, geometry.id.manual, desired) &&
            static_cast<std::uint8_t>(desired) == geometry.id.index) {
            drawing.outline(preset_indicator_bounds(geometry, 1.0F), kPresetPending, 1.0F);
        }
    }
    for (std::size_t index = 0; index < layout.control_count; ++index) {
        const auto& geometry = layout.controls[index];
        if (!ui_control_visible(layout, geometry.id) || geometry.id.kind != UiControlKind::PresetKey || geometry.id != view.focus) continue;
        paint_preset_focus(drawing, geometry);
    }
}

void paint_controls(Drawing& drawing, const UiModel& model) {
    const auto& view = model.view();
    const auto& layout = model.layout();
    const bool flat = view.presentation == UiPresentation::Flat;
    const std::array<UiColor, 9> caps{
        kBrownCap, kBrownCap, kIvoryCap, kIvoryCap, kBlackCap,
        kIvoryCap, kBlackCap, kBlackCap, kIvoryCap};
    for (std::size_t index = 0; index < layout.control_count; ++index) {
        const auto& geometry = layout.controls[index];
        const auto& id = geometry.id;
        if (!ui_control_visible(layout, id)) continue;
        if (id.kind == UiControlKind::PresetKey || id.kind == UiControlKind::SoundingBank ||
            id.kind == UiControlKind::CancelManual) continue;
        const auto manual = manual_index(id.manual);
        bool selected = false;
        if (id.kind == UiControlKind::ManualDrawbar) {
            const auto value = view.controls.drawbars[manual][static_cast<std::size_t>(id.bank)][id.index];
            drawbar(drawing, geometry, value, kUiFootageLabels[id.index], caps[id.index], flat);
        } else if (id.kind == UiControlKind::PedalDrawbar) {
            drawbar(drawing, geometry, view.controls.pedal_drawbars[id.index],
                    id.index == 0 ? "MIX 1" : "MIX 2", kBrownCap, flat);
        } else if (id.kind == UiControlKind::Expression) {
            centered(drawing, "NOMINAL EXPRESSION", geometry.label_bounds, 10.5F, kUiIvory);
            const auto& track = geometry.track;
            drawing.rounded({track.x - 3.0F, track.y - 5.0F, track.width + 6.0F, 10.0F}, 3.0F, {8, 9, 8});
            drawing.line(track.x, track.y + 3.0F, track.x + track.width, track.y + 3.0F, kMetalEdge);
            const float x = track.x + static_cast<float>(view.controls.expression) * track.width;
            drawing.rect({track.x, track.y - 1.0F, x - track.x, 2.0F}, kUiBrass);
            drawing.rounded({x - 7.0F, track.y - 11.0F, 14.0F, 22.0F}, 3.0F, {30, 26, 18});
            if (flat) drawing.rect({x - 5.0F, track.y - 9.0F, 10.0F, 17.0F}, kUiBrass);
            else drawing.gradient({x - 5.0F, track.y - 9.0F, 10.0F, 17.0F}, {220, 193, 140}, {122, 97, 55});
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
            button(drawing, geometry.bounds, {}, selected, false, TextFace::Serif, true, flat);
            centered(drawing, titles[id.index], geometry.label_bounds, 10.0F, {74, 54, 35});
            centered(drawing, value, geometry.value_bounds, 14.0F, {33, 28, 21}, TextFace::Serif);
        } else {
            if (id.kind == UiControlKind::EditBank) selected = view.edited_banks[manual] == id.bank;
            if (id.kind == UiControlKind::KeyboardTarget) selected = static_cast<std::uint8_t>(view.keyboard_target) == id.index;
            if (id.kind == UiControlKind::Workspace) selected = static_cast<std::uint8_t>(view.workspace) == id.index;
            if (id.kind == UiControlKind::Presentation) selected = flat;
            button(drawing, geometry.bounds, button_label(id), selected, id.kind == UiControlKind::Panic,
                   header_button(id.kind) ? TextFace::Serif : TextFace::Sans, false, flat);
        }
        if (view.focus == id) drawing.outline(geometry.bounds, kUiFocusCyan, 2.0F);
    }
    paint_presets(drawing, model);
}

// Interpolate the original side edges before insetting. All material, held
// and focus ink follows the shared hit/top/front quads, never their AABBs.
[[nodiscard]] UiQuad quad_band(const UiQuad& shape, float start, float finish,
                               float side_inset = 0.0F) noexcept {
    const auto& points = shape.points;
    const float height = points[3].y - points[0].y;
    if (!(height > 0.0F && finish > start && start >= 0.0F && finish <= 1.0F)) return {};
    const auto edge = [&](std::size_t top, std::size_t bottom, float fraction, float offset) {
        return UiPoint{points[top].x + (points[bottom].x - points[top].x) * fraction + offset,
                       points[0].y + height * fraction};
    };
    UiQuad result{{edge(0, 3, start, side_inset), edge(1, 2, start, -side_inset),
                   edge(1, 2, finish, -side_inset), edge(0, 3, finish, side_inset)}};
    if (result.points[1].x <= result.points[0].x || result.points[2].x <= result.points[3].x) return {};
    return result;
}

[[nodiscard]] UiQuad inset_quad(const UiQuad& shape, float amount) noexcept {
    const float height = shape.points[3].y - shape.points[0].y;
    if (!(height > 2.0F * amount)) return {};
    return quad_band(shape, amount / height, 1.0F - amount / height, amount);
}

void paint_key(Drawing& drawing, const UiKeyGeometry& key, bool held, bool focused, bool flat) {
    if (flat) {
        const UiColor color = key.accidental ? (held ? UiColor{143, 115, 66} : UiColor{32, 33, 30}) :
            (held ? UiColor{230, 195, 123} : UiColor{242, 230, 204});
        drawing.quad(key.top, color, color);
        drawing.quad_outline(key.hit, key.accidental ? UiColor{9, 11, 10} : UiColor{86, 78, 61}, 0.8F);
    } else if (key.accidental) {
        drawing.quad(key.top,
            held ? UiColor{150, 124, 77} : UiColor{40, 39, 35},
            held ? UiColor{96, 77, 43} : UiColor{10, 12, 10});
        // A narrow bevel follows the projected cap; no rectangular highlight
        // may cross its sloping side or the neighboring natural key.
        drawing.quad(inset_quad(key.top, 1.4F),
            held ? UiColor{166, 138, 88} : UiColor{66, 63, 56},
            held ? UiColor{104, 84, 48} : UiColor{23, 25, 22});
        drawing.quad(key.front,
            held ? UiColor{95, 75, 40} : UiColor{41, 39, 32},
            held ? UiColor{55, 42, 24} : UiColor{9, 11, 9});
        drawing.quad_outline(key.hit, {5, 6, 5}, 0.8F);
        drawing.quad_outline(inset_quad(key.top, 1.2F),
            held ? UiColor{185, 151, 92, 170} : UiColor{127, 115, 91, 130}, 0.65F);
        drawing.quad(quad_band(key.front, 0.0F, 0.12F, 1.0F),
                     {155, 139, 106, 145}, {155, 139, 106, 70});
    } else {
        drawing.quad(key.top,
            held ? UiColor{209, 181, 122} : UiColor{226, 211, 181},
            held ? UiColor{244, 213, 149} : UiColor{255, 244, 220});
        drawing.quad(key.front,
            held ? UiColor{190, 157, 96} : UiColor{225, 203, 163},
            held ? UiColor{145, 115, 62} : UiColor{174, 144, 99});
        drawing.quad_outline(key.hit, {83, 65, 42}, 0.7F);
        drawing.quad(quad_band(key.front, 0.0F, 0.13F, 0.9F),
                     {255, 245, 217, 220}, {255, 245, 217, 60});
        drawing.quad(quad_band(key.top, 0.0F, 0.08F, 0.8F), {20, 17, 13, 70}, {20, 17, 13, 0});
    }
    if (held) drawing.quad(quad_band(key.top, 0.91F, 0.96F, 2.0F), kUiBrass, kUiBrass);
    if (focused) drawing.quad_outline(inset_quad(key.hit, 2.0F), kUiFocusCyan, 2.0F);
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
    if (layout.workspace != UiWorkspace::Play || !layout.show_cabinet) return;
    const auto& cabinet = layout.cabinet_panel;
    const auto& art = layout.cabinet_art;
    panel(drawing, cabinet, true, layout.presentation == UiPresentation::Flat);
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

[[nodiscard]] std::string_view snapshot_caption(InspectionSnapshotState state) noexcept {
    switch (state) {
    case InspectionSnapshotState::Current: return "CURRENT SNAPSHOT";
    case InspectionSnapshotState::Retained: return "RETAINED SNAPSHOT";
    case InspectionSnapshotState::Stopped: return "STOPPED SNAPSHOT";
    case InspectionSnapshotState::Unprepared: return "UNPREPARED SNAPSHOT";
    case InspectionSnapshotState::Unavailable: return "SNAPSHOT UNAVAILABLE";
    }
    return "SNAPSHOT UNAVAILABLE";
}

[[nodiscard]] std::string_view availability_caption(InspectionAvailability availability) noexcept {
    switch (availability) {
    case InspectionAvailability::Available: return "Available";
    case InspectionAvailability::NotObserved: return "Not observed";
    case InspectionAvailability::NotIntegrated: return "Not integrated";
    case InspectionAvailability::NotAcquired: return "Not acquired";
    case InspectionAvailability::Invalid: return "Invalid";
    }
    return "Invalid";
}

[[nodiscard]] std::string_view evidence_caption(InspectionEvidence evidence) noexcept {
    switch (evidence) {
    case InspectionEvidence::Software: return "Software";
    case InspectionEvidence::Documented: return "Documented";
    case InspectionEvidence::Derived: return "Derived";
    case InspectionEvidence::Proposed: return "Proposed";
    case InspectionEvidence::Unknown: return "Unknown";
    }
    return "Unknown";
}

[[nodiscard]] std::string inspection_value(const InspectionRow& row) {
    std::string value(row.value.view());
    if (!row.unit.empty()) value += " " + std::string(row.unit);
    return value;
}

[[nodiscard]] std::string inspection_badges(const InspectionRow& row) {
    return "A:" + std::string(availability_caption(row.availability)) +
        " / E:" + std::string(evidence_caption(row.evidence));
}

// The inspector has a declared readable minimum instead of scaling an entire
// card down. Values may wrap; the availability/evidence legend stays explicit.
float inspection_text(Drawing& drawing, std::string_view value, UiRect bounds,
                      float size, UiColor color, bool paint = true) {
    const std::string clean = single_line(value);
    std::string_view remainder(clean);
    const float line_height = size * 1.25F;
    float used = 0.0F;
    while (!remainder.empty()) {
        std::size_t count = fitting_prefix(drawing, remainder, bounds.width, size);
        if (count == 0) break;
        if (count < remainder.size()) {
            const auto space = remainder.substr(0, count).find_last_of(' ');
            if (space != std::string_view::npos && space > count / 2) count = space;
        }
        if (paint && used + size <= bounds.height) {
            drawing.text(remainder.substr(0, count), bounds.x, bounds.y + used, size, color);
        }
        used += line_height;
        remainder.remove_prefix(count);
        while (!remainder.empty() && remainder.front() == ' ') remainder.remove_prefix(1);
    }
    return used;
}

void inspection_banner(Drawing& drawing, UiRect bounds, const InspectionDocument* document) {
    const auto state = document ? document->snapshot_state : InspectionSnapshotState::Unavailable;
    const UiColor status_color = state == InspectionSnapshotState::Current ? kGreen :
        state == InspectionSnapshotState::Retained ? kPresetPending : kMuted;
    std::string status(snapshot_caption(state));
    if (document && state != InspectionSnapshotState::Unavailable && state != InspectionSnapshotState::Unprepared) {
        status += " / Frame " + std::to_string(document->frame_clock) +
            " / Revision " + std::to_string(document->publication_revision);
    }
    if (document && document->controls_pending) status += " / DESIRED CONTROLS PENDING";
    text_line(drawing, status, {bounds.x + 2.0F, bounds.y + 1.0F, bounds.width - 4.0F, 17.0F},
              11.5F, status_color);
    const std::string profile = "Loaded profile: " +
        (document ? std::string(document->profile_id.view()) : "Not observed");
    const float legend_width = std::min(310.0F, bounds.width * 0.42F);
    text_line(drawing, profile, {bounds.x + 2.0F, bounds.y + 21.0F,
              bounds.width - legend_width - 14.0F, 16.0F}, 10.5F, kUiIvory);
    text_line(drawing, "A = Availability / E = Evidence", {bounds.x + bounds.width - legend_width,
              bounds.y + 21.0F, legend_width, 16.0F}, 10.5F, kMuted);
}

void inspection_card(Drawing& drawing, UiRect bounds, const InspectionCard& card, bool flat) {
    panel(drawing, bounds, false, flat);
    const bool compact = bounds.height < 280.0F;
    const float label_size = compact ? 10.0F : 11.0F;
    const float value_size = compact ? 10.5F : 12.0F;
    const float badge_size = 10.0F;
    const float padding = compact ? 9.0F : 13.0F;
    const float x = bounds.x + padding;
    const float width = bounds.width - 2.0F * padding;
    text_line(drawing, card.title, {x, bounds.y + 8.0F, width, 22.0F}, compact ? 16.0F : 19.0F, kUiBrass);
    const float summary_size = compact ? 10.0F : 11.0F;
    const float summary_height = inspection_text(drawing, card.summary,
        {x, 0.0F, width, bounds.height}, summary_size, kMuted, false);
    const float summary_top = bounds.y + bounds.height - padding - summary_height;
    drawing.line(x, summary_top - 5.0F, x + width, summary_top - 5.0F, kMetalEdge);
    inspection_text(drawing, card.summary, {x, summary_top, width, summary_height}, summary_size, kMuted);
    float y = bounds.y + (compact ? 31.0F : 39.0F);
    const auto row_count = std::min(card.row_count, card.rows.size());
    float required = 0.0F;
    for (std::size_t index = 0; index < row_count; ++index) {
        required += label_size * 1.15F + inspection_text(drawing, inspection_value(card.rows[index]),
            {x, 0.0F, width, bounds.height}, value_size, kUiIvory, false);
    }
    const float extra = row_count > 1 ? std::clamp((summary_top - 9.0F - y - required) /
        static_cast<float>(row_count - 1), 0.0F, compact ? 3.0F : 10.0F) : 0.0F;
    for (std::size_t index = 0; index < row_count; ++index) {
        const auto& row = card.rows[index];
        const std::string badges = inspection_badges(row);
        const float badge_width = drawing.text_width(badges, badge_size);
        text_line(drawing, row.label, {x, y, std::max(0.0F, width - badge_width - 6.0F), label_size * 1.15F},
                  label_size, kMuted);
        drawing.text(badges, x + width - badge_width, y, badge_size,
                     row.availability == InspectionAvailability::Invalid ? kRed : kMuted);
        y += label_size * 1.15F;
        const float height = inspection_text(drawing, inspection_value(row),
            {x, y, width, std::max(0.0F, summary_top - 7.0F - y)}, value_size,
            row.availability == InspectionAvailability::Invalid ? kRed : kUiIvory);
        y += height + extra;
    }
}

void paint_service(Drawing& drawing, const UiLayout& layout, const InstrumentViewInfo& info) {
    if (layout.workspace != UiWorkspace::Service) return;
    const auto& body = layout.workspace_panel;
    const bool flat = layout.presentation == UiPresentation::Flat;
    inspection_banner(drawing, {body.x, body.y, body.width, 39.0F}, info.inspection);
    const float gap = 10.0F;
    // Three columns keep all six cards readable at 960x700. A tall narrow
    // window has room for two wider columns and three rows.
    const std::size_t columns = body.width < 1100.0F && body.height >= 900.0F ? 2 : 3;
    const std::size_t rows = kInspectionSectionCount / columns;
    const float card_width = (body.width - gap * static_cast<float>(columns - 1)) / static_cast<float>(columns);
    const float card_height = (body.height - 45.0F - gap * static_cast<float>(rows - 1)) / static_cast<float>(rows);
    constexpr std::array<std::string_view, kInspectionSectionCount> titles{
        "Generator", "Contacts / routing", "Scanner", "AO-28", "Leslie", "Retained controls"};
    for (std::size_t index = 0; index < kInspectionSectionCount; ++index) {
        const UiRect bounds{body.x + static_cast<float>(index % columns) * (card_width + gap),
            body.y + 45.0F + static_cast<float>(index / columns) * (card_height + gap), card_width, card_height};
        if (info.inspection) inspection_card(drawing, bounds, info.inspection->sections[index], flat);
        else {
            panel(drawing, bounds, false, flat);
            text_line(drawing, titles[index], {bounds.x + 12.0F, bounds.y + 10.0F, bounds.width - 24.0F, 24.0F},
                      18.0F, kUiBrass);
            wrapped(drawing, "Inspection document unavailable. Applied values are not observed.",
                    {bounds.x + 12.0F, bounds.y + 45.0F, bounds.width - 24.0F, bounds.height - 57.0F},
                    12.0F, kMuted);
        }
    }
}

void paint_rotary(Drawing& drawing, const UiLayout& layout, const InstrumentViewInfo& info) {
    if (layout.workspace != UiWorkspace::Rotary) return;
    const auto& body = layout.workspace_panel;
    const bool flat = layout.presentation == UiPresentation::Flat;
    const float gap = 16.0F;
    const float art_panel_width = body.width * 0.43F;
    const UiRect art_panel{body.x, body.y, art_panel_width, body.height};
    panel(drawing, art_panel, true, flat);
    heading(drawing, "CABINET REFERENCE", {art_panel.x + 16.0F, art_panel.y + 9.0F,
            art_panel.width - 32.0F, 27.0F}, 19.0F);
    const float art_width = std::min(art_panel.width - 32.0F, (art_panel.height - 165.0F) * 466.0F / 397.0F);
    const UiRect art{art_panel.x + (art_panel.width - art_width) / 2.0F, art_panel.y + 47.0F,
                     art_width, art_width * 397.0F / 466.0F};
    drawing.rect(inset({art.x - 3.0F, art.y - 3.0F, art.width + 6.0F, art.height + 6.0F}, 0.0F), {8, 9, 8});
    drawing.outline({art.x - 2.0F, art.y - 2.0F, art.width + 4.0F, art.height + 4.0F}, kMetalEdge);
    if (!drawing.reference_art(ReferenceArt::Cabinet, art)) {
        drawing.rect(art, {29, 26, 21});
        centered(drawing, "DECORATIVE ART UNAVAILABLE", art, 12.0F, kMuted);
    }
    const float below = art.y + art.height + 16.0F;
    text_line(drawing, "ATLAS CONCEPT / DECORATIVE", {art_panel.x + 18.0F, below,
              art_panel.width - 36.0F, 18.0F}, 11.5F, kUiBrass);
    wrapped(drawing, "Cabinet audio is not connected. No specimen captures qualify physical fidelity.",
            {art_panel.x + 18.0F, below + 26.0F, art_panel.width - 36.0F,
             art_panel.y + art_panel.height - below - 40.0F}, 12.0F, kUiIvory);
    const UiRect facts{body.x + art_panel_width + gap, body.y, body.width - art_panel_width - gap, body.height};
    panel(drawing, facts, false, flat);
    const float x = facts.x + 15.0F;
    const float width = facts.width - 30.0F;
    text_line(drawing, "ROTARY / READ ONLY", {x, facts.y + 13.0F, width, 27.0F}, 22.0F, kUiBrass);
    inspection_banner(drawing, {x, facts.y + 49.0F, width, 39.0F}, info.inspection);
    if (!info.inspection) {
        wrapped(drawing, "Inspection document unavailable. Rotor speeds and microphone geometry are not observed.",
                {x, facts.y + 114.0F, width, facts.height - 130.0F}, 13.0F, kMuted);
        return;
    }
    const auto count = std::min(info.inspection->rotary_row_count, info.inspection->rotary_rows.size());
    const float row_height = (facts.height - 105.0F) / static_cast<float>(std::max<std::size_t>(1, count));
    for (std::size_t index = 0; index < count; ++index) {
        const auto& row = info.inspection->rotary_rows[index];
        const float y = facts.y + 99.0F + static_cast<float>(index) * row_height;
        drawing.line(x, y, x + width, y, kMetalEdge);
        text_line(drawing, row.label, {x, y + 7.0F, width, 16.0F}, 11.5F, kUiBrass);
        inspection_text(drawing, inspection_value(row), {x, y + 25.0F, width, row_height - 41.0F}, 12.0F, kUiIvory);
        text_line(drawing, "Availability: " + std::string(availability_caption(row.availability)) +
                  " / Evidence: " + std::string(evidence_caption(row.evidence)),
                  {x, y + row_height - 15.0F, width, 13.0F}, 10.0F, kMuted);
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
        constexpr std::array<std::string_view, 15> help{
            "61 playing keys per manual; 12 preset keys per manual; 25 pedals.",
            "A W S E D F T G Y H U J K O L P ;   Play notes",
            "F1 / F2 / F3   Upper / Lower / Pedals; [ / ]   Shift octave",
            "F4 / F5 / F6   Play / Rotary / Service; playing continues.",
            "F7   Toggle Flat presentation; sound controls stay the same.",
            "Tab / Shift+Tab moves focus. Arrows / Home / End navigate.",
            "Space holds a focused playing key; release stops that key.",
            "On presets, Space / Enter selects; release keeps the route.",
            "Preset C cancels one manual. C# through A select fixed rows.",
            "Preset A# sounds adjustable bank A; preset B sounds bank B.",
            "EDIT A/B shows a bank for editing without changing the route.",
            "Fixed A and adjustable A# are separate choices.",
            "Preset arrows move focus; Up / Down chooses the manual.",
            "Ctrl+M opens MIDI. PANIC releases all notes.",
            "Save/Load contains controls, not held notes or sound history."};
        for (std::size_t index = 0; index < help.size(); ++index) {
            text_line(drawing, help[index], {x, y + 64.0F + static_cast<float>(index) * 22.0F,
                      boxes.panel.width - 56.0F, 20.0F}, 12.5F, index < 8 ? kUiIvory : kMuted);
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
    panel(drawing, layout.header, false, layout.presentation == UiPresentation::Flat);
    float title_left = layout.header.x;
    float title_right = layout.header.x + layout.header.width;
    float flat_left = title_right;
    for (std::size_t index = 0; index < layout.control_count; ++index) {
        const auto& control = layout.controls[index];
        if (!ui_control_visible(layout, control.id)) continue;
        if (control.id.kind == UiControlKind::Workspace && control.id.index == 2)
            title_left = control.bounds.x + control.bounds.width + 12.0F;
        if (control.id.kind == UiControlKind::SaveControls) title_right = control.bounds.x - 12.0F;
        if (control.id.kind == UiControlKind::Presentation) flat_left = control.bounds.x;
    }
    constexpr std::string_view title = "TONEWHEEL ATLAS";
    float size = layout.show_cabinet ? 40.0F : 28.0F;
    const float natural_width = drawing.text_width(title, size, TextFace::Serif);
    if (natural_width > title_right - title_left) size *= (title_right - title_left) / natural_width;
    const float width = drawing.text_width(title, size, TextFace::Serif);
    const float desired_x = title_left + (title_right - title_left - width) / 2.0F;
    const float x = std::clamp(desired_x, title_left, std::max(title_left, title_right - width));
    const float y = layout.header.y + (layout.show_cabinet ? 4.0F : 8.0F);
    drawing.text(title, x + 1.0F, y + 2.0F, size, {4, 5, 4}, TextFace::Serif);
    drawing.text(title, x, y, size, kUiBrass, TextFace::Serif);
    centered(drawing, "NOMINAL DRY ORGAN", {title_left, layout.header.y + layout.header.height - 29.0F,
             std::max(0.0F, flat_left - title_left - 10.0F), 22.0F}, 11.0F, kUiIvory);
}

[[nodiscard]] std::string focused_control_caption(const UiModel& model) {
    const auto& view = model.view();
    const auto& id = view.focus;
    if (!ui_control_visible(model.layout(), id)) return {};
    const std::string manual = id.manual == Manual::Upper ? "Upper" : "Lower";
    if (id.kind == UiControlKind::ManualKey) {
        constexpr std::array<std::string_view, 12> notes{"C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"};
        const unsigned midi = model.layout().manual_keys[manual_index(id.manual)][id.index].note.value;
        return manual + " manual / " + std::string(notes[midi % 12]) +
            std::to_string(static_cast<int>(midi / 12) - 1) + " / MIDI " + std::to_string(midi) +
            " / Hold Space to play";
    }
    if (id.kind == UiControlKind::PedalKey)
        return "Pedal " + std::to_string(static_cast<unsigned>(id.index) + 1) + " of 25 / Hold Space to play";
    if (id.kind == UiControlKind::ManualDrawbar)
        return manual + " drawbar bank " + (id.bank == DrawbarBank::A ? "A / " : "B / ") +
            std::string(kUiFootageLabels[id.index]) + " / Position " +
            std::to_string(view.controls.drawbars[manual_index(id.manual)][static_cast<std::size_t>(id.bank)][id.index]);
    if (id.kind == UiControlKind::PedalDrawbar)
        return "Nominal pedal mixture " + std::to_string(static_cast<unsigned>(id.index) + 1) +
            " / Position " + std::to_string(view.controls.pedal_drawbars[id.index]);
    if (id.kind == UiControlKind::Expression)
        return "Nominal expression / " + std::to_string(static_cast<int>(std::round(view.controls.expression * 100.0))) + "%";
    if (id.kind == UiControlKind::Percussion) {
        constexpr std::array<std::string_view, 4> names{"Percussion enable", "Percussion harmonic", "Percussion volume", "Percussion decay"};
        return std::string(names[id.index]) + " / Enter or Space changes the setting";
    }
    if (id.kind == UiControlKind::EditBank) return manual + " / " + std::string(button_label(id)) + " / Changes the bank shown for editing";
    if (id.kind == UiControlKind::Workspace) return std::string(button_label(id)) + " workspace / F4 Play / F5 Rotary / F6 Service";
    if (id.kind == UiControlKind::Presentation) return "Flat presentation / F7 toggles / Sound controls are retained";
    return std::string(button_label(id));
}

void paint_footer(Drawing& drawing, const UiModel& model, const InstrumentViewInfo& info) {
    const auto& footer = model.layout().footer;
    const auto& view = model.view();
    drawing.gradient(footer, {27, 26, 24}, {16, 16, 16});
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
    std::string status;
    bool preset_request = false;
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        PresetSelection desired{};
        if (!pending_preset(view, static_cast<Manual>(manual), desired)) continue;
        if (!status.empty()) status += " / ";
        status += manual == 0 ? "PRESET UPPER " : "PRESET LOWER ";
        status += preset_selection_label(desired);
        status += " PENDING";
        preset_request = true;
    }
    if (view.input_recovery || view.last_submit_status != SessionStatus::Ok) {
        status = info.status_message.empty() ?
            "Input recovered. Release held keys before playing again." : std::string(info.status_message);
    } else if (!preset_request && view.focus.kind == UiControlKind::PresetKey) {
        const auto selection = static_cast<PresetSelection>(view.focus.index);
        status = view.focus.manual == Manual::Upper ? "Upper preset " : "Lower preset ";
        status += preset_selection_label(selection);
        status += selection == PresetSelection::Cancel ? ": Cancel manual route" :
            selection == PresetSelection::BankA ? ": adjustable bank A" :
            selection == PresetSelection::BankB ? ": adjustable bank B" : ": fixed registration";
        status += " / " + registration_caption(view, view.focus.manual);
        if (!info.status_message.empty()) status += " / " + std::string(info.status_message);
    } else if (!preset_request && !focused_control_caption(model).empty()) {
        status = focused_control_caption(model);
        if (view.controls_pending) status += " / CONTROLS PENDING";
        if (!info.status_message.empty()) status += " / " + std::string(info.status_message);
    } else if (!preset_request && !info.status_message.empty()) status = info.status_message;
    else if (!preset_request && view.controls_pending) status = "Applying controls...";
    else if (!preset_request) status = "A W S E D F T G Y H U J K O L P ; play / F1-F3 target / F4-F6 workspace / F7 Flat / [ ] octave";
    text_line(drawing, status, {footer.x + 20.0F, footer.y + 21.0F, footer.width - 32.0F, 14.0F},
              10.5F, preset_request ? kPresetPending : kMuted);
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
    const bool flat = view.presentation == UiPresentation::Flat;
    drawing.clear(flat ? UiColor{18, 21, 20} : kUiWalnut);
    const float margin = layout.header.x;
    if (!flat) {
        wood(drawing, {0, 0, layout.width, layout.height});
        const bool left_art = drawing.reference_art(ReferenceArt::LeftWoodCheek, {0, 0, margin, layout.height});
        const bool right_art = drawing.reference_art(ReferenceArt::RightWoodCheek,
            {layout.width - margin, 0, margin, layout.height});
        (void)left_art;
        (void)right_art;
    }
    drawing.rounded({margin - 7.0F, 8.0F, layout.width - 2.0F * margin + 14.0F,
                     layout.height - 24.0F}, 9.0F, {10, 11, 9});
    drawing.line(margin - 4.0F, 17.0F, margin - 4.0F, layout.height - 23.0F, {143, 89, 48, 160});
    drawing.line(layout.width - margin + 3.0F, 17.0F, layout.width - margin + 3.0F,
                 layout.height - 23.0F, {143, 89, 48, 160});
    paint_header(drawing, layout);
    if (ui_control_visible(layout, {UiControlKind::ManualKey})) {
    panel(drawing, layout.performance_panel, true, flat);
    const auto& performance = layout.performance_panel;
    const float divider = performance.x + performance.width * 0.46F;
    drawing.line(divider, performance.y + 12.0F, divider, performance.y + performance.height - 12.0F, kMetalEdge);
    const bool eligible = view.applied.controls.route_enabled[0] &&
        view.applied.controls.fixed_registrations[0] == FixedRegistration::None &&
        view.applied.controls.selected_banks[0] == DrawbarBank::B;
    const bool separate_eligibility = performance.height >= 92.0F;
    heading(drawing, separate_eligibility ? "PERCUSSION" : eligible ? "PERCUSSION / UPPER B ACTIVE" : "PERCUSSION / REQUIRES UPPER B",
            {performance.x + 17.0F, performance.y + 3.0F, divider - performance.x - 34.0F, 18.0F},
            separate_eligibility ? 13.5F : 10.5F);
    if (separate_eligibility) centered(drawing, eligible ? "UPPER B ROUTE ACTIVE" : "REQUIRES UPPER B",
        {performance.x + 12.0F, performance.y + 73.0F, divider - performance.x - 24.0F, 16.0F}, 10.0F, eligible ? kGreen : kMuted);
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        const auto& bounds = layout.registration_panels[manual];
        panel(drawing, bounds, true, flat);
        std::string state = registration_caption(view, static_cast<Manual>(manual));
        const float maximum_state_width = bounds.width * 0.43F;
        if (drawing.text_width(state, 10.5F) > maximum_state_width - 6.0F) {
            state = registration_caption(view, static_cast<Manual>(manual), true);
        }
        const float state_width = std::min(maximum_state_width, drawing.text_width(state, 10.5F) + 8.0F);
        heading(drawing, manual == 0 ? "UPPER DRAWBARS" : "LOWER DRAWBARS",
                {bounds.x + 16.0F, bounds.y + 3.0F, bounds.width - state_width - 32.0F, 23.0F}, 14.0F);
        centered(drawing, state, {bounds.x + bounds.width - state_width - 14.0F, bounds.y + 5.0F, state_width, 20.0F},
                 10.5F, view.applied.controls.route_enabled[manual] ? kUiBrass : kMuted);
        const auto& rail = layout.manual_rail_panels[manual];
        if (flat) drawing.rect(rail, {36, 38, 35});
        else wood(drawing, rail);
        drawing.rect(inset(rail, 5.0F), {19, 18, 17});
        drawing.line(rail.x + 6.0F, rail.y + 5.0F, rail.x + rail.width - 6.0F, rail.y + 5.0F, {112, 87, 59});
        centered(drawing, manual == 0 ? "UPPER / SWELL" : "LOWER / GREAT",
                 {rail.x + 8.0F, rail.y + 3.0F, rail.width - 16.0F, 17.0F}, 10.5F, kUiBrass, TextFace::Serif);
    }
    if (flat) drawing.rect(layout.keyboard_toolbar, {27, 29, 28});
    else drawing.gradient(layout.keyboard_toolbar, {27, 26, 25}, {16, 16, 16});
    const std::string octave = view.keyboard_target == UiTarget::Pedals ?
        "COMPUTER KEYS / PEDAL OCTAVE " + std::to_string(view.pedal_octave) :
        "COMPUTER KEYS / BASE C" + std::to_string(static_cast<int>(view.manual_base_midi) / 12 - 1);
    text_line(drawing, octave, {layout.keyboard_toolbar.x + 478.0F, layout.keyboard_toolbar.y + 7.0F,
              layout.keyboard_toolbar.width - 490.0F, 15.0F}, 10.0F, kMuted);
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        const auto& bounds = layout.manual_panels[manual];
        panel(drawing, bounds, false, flat);
        drawing.rect({bounds.x + 6.0F, bounds.y + 20.0F, bounds.width - 12.0F,
                      bounds.height - 26.0F}, {7, 9, 8});
        centered(drawing, manual == 0 ? "UPPER MANUAL" : "LOWER MANUAL",
                 {bounds.x + 12.0F, bounds.y + 3.0F, bounds.width - 24.0F, 16.0F}, 10.5F, kUiBrass);
        for (const bool accidental : {false, true}) {
            for (std::size_t index = 0; index < kManualKeyCount; ++index) {
                const auto& key = layout.manual_keys[manual][index];
                const UiControlId id{UiControlKind::ManualKey, static_cast<Manual>(manual),
                                     DrawbarBank::A, static_cast<std::uint8_t>(index)};
                if (!ui_control_visible(layout, id) || key.accidental != accidental) continue;
                const bool focused = view.focus.kind == UiControlKind::ManualKey &&
                    manual_index(view.focus.manual) == manual && view.focus.index == index;
                paint_key(drawing, key, view.applied.held_keys[manual][index], focused, flat);
            }
        }
    }
    panel(drawing, layout.pedal_panel, false, flat);
    centered(drawing, "PEDALBOARD / 25 NOTES", {layout.pedal_panel.x + 12.0F, layout.pedal_panel.y + 3.0F,
             layout.pedal_panel.width - 24.0F, 16.0F}, 10.5F, kUiBrass);
    for (const bool accidental : {false, true}) {
        for (std::size_t index = 0; index < kPedalCount; ++index) {
            const auto& key = layout.pedal_keys[index];
            const UiControlId id{UiControlKind::PedalKey, Manual::Upper,
                                 DrawbarBank::A, static_cast<std::uint8_t>(index)};
            if (ui_control_visible(layout, id) && key.accidental == accidental) {
                paint_key(drawing, key, view.applied.held_pedals[index],
                          view.focus.kind == UiControlKind::PedalKey && view.focus.index == index, flat);
            }
        }
    }
    paint_cabinet(drawing, layout, info);
    } else if (layout.workspace == UiWorkspace::Service) {
        paint_service(drawing, layout, info);
    } else if (layout.workspace == UiWorkspace::Rotary) {
        paint_rotary(drawing, layout, info);
    }
    paint_controls(drawing, model);
    paint_footer(drawing, model, info);
    overlay(drawing, layout, info);
}

} // namespace hammond::standalone
