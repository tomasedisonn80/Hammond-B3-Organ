#include "InstrumentView.h"
#include "InspectionModel.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
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

[[nodiscard]] bool material_surface(UiRect bounds) noexcept {
    return std::isfinite(bounds.x) && std::isfinite(bounds.y) &&
        std::isfinite(bounds.width) && std::isfinite(bounds.height) &&
        bounds.width > 0.0F && bounds.height > 0.0F &&
        bounds.width <= kUiMaximumDimension && bounds.height <= kUiMaximumDimension &&
        std::isfinite(bounds.x + bounds.width) && std::isfinite(bounds.y + bounds.height);
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
    if (!material_surface(bounds)) return;
    if (flat) {
        drawing.rect(bounds, {27, 29, 28});
        drawing.outline(bounds, {82, 79, 67});
        return;
    }
    drawing.shadow(bounds, 5.0F);
    drawing.rounded(bounds, 6.0F, {7, 7, 7});
    drawing.rounded(inset(bounds, 1.0F), 5.0F, kMetalEdge);
    drawing.rounded(inset(bounds, 2.0F), 4.0F, {14, 14, 14});
    drawing.gradient(inset(bounds, 4.0F), {43, 41, 38}, {21, 22, 21});
    // Restrained procedural grain belongs to the live charcoal surface, not
    // to a stretched image of controls. Its local-coordinate lattice is fixed
    // in time, leaves room for both marks and emits at most 2,048 point pairs.
    // Over the deck gradient, these alpha ranges perturb any RGB channel by
    // at most eight levels, including integer blending roundoff.
    constexpr std::size_t maximum_grain_pairs = 2048;
    const auto rows = static_cast<int>(std::max(0.0F, std::floor(bounds.height - 16.0F)));
    const auto columns = static_cast<int>(std::max(0.0F, std::floor(bounds.width - 21.0F)));
    int grain_step = std::max(4, static_cast<int>(std::ceil(std::sqrt(
        static_cast<double>(rows) * static_cast<double>(columns) /
        (3.0 * static_cast<double>(maximum_grain_pairs))))));
    const auto pair_count = [rows, columns](int step) {
        const auto row_count = rows > 1 ? static_cast<std::size_t>((rows - 2) / step + 1) : 0;
        const auto column_count = columns > 1 ? static_cast<std::size_t>((columns - 2) / (step * 3) + 1) : 0;
        return row_count * column_count;
    };
    while (pair_count(grain_step) > maximum_grain_pairs) ++grain_step;
    std::size_t grain_pairs = 0;
    for (int row = 1; row < rows && grain_pairs < maximum_grain_pairs; row += grain_step) {
        for (int column = 1; column < columns && grain_pairs < maximum_grain_pairs; column += grain_step * 3) {
            const auto grain = static_cast<std::uint32_t>(row) * 1973U +
                static_cast<std::uint32_t>(column) * 9277U;
            const float x = bounds.x + 7.0F + static_cast<float>(column) +
                static_cast<float>((grain >> 5U) % 3U);
            const float y = bounds.y + 7.0F + static_cast<float>(row);
            drawing.rect({x, y, 1.0F, 1.0F},
                         {212, 205, 190, static_cast<std::uint8_t>(6U + grain % 5U)});
            drawing.rect({x + 3.0F, y + 1.0F, 2.0F, 1.0F},
                         {0, 0, 0, static_cast<std::uint8_t>(10U + (grain >> 3U) % 9U)});
            ++grain_pairs;
        }
    }
    drawing.line(bounds.x + 7.0F, bounds.y + 3.0F,
                 bounds.x + bounds.width - 7.0F, bounds.y + 3.0F, {147, 133, 111, 120});
    drawing.line(bounds.x + 3.0F, bounds.y + 7.0F,
                 bounds.x + 3.0F, bounds.y + bounds.height - 7.0F, {123, 112, 94, 92});
    drawing.line(bounds.x + 7.0F, bounds.y + bounds.height - 3.0F,
                 bounds.x + bounds.width - 7.0F, bounds.y + bounds.height - 3.0F, {7, 8, 7});
    drawing.line(bounds.x + bounds.width - 3.0F, bounds.y + 7.0F,
                 bounds.x + bounds.width - 3.0F, bounds.y + bounds.height - 7.0F, {7, 8, 7});
    if (screws) {
        for (const float x : {bounds.x + 7.0F, bounds.x + bounds.width - 13.0F}) {
            screw(drawing, x, bounds.y + 7.0F);
            if (bounds.height > 80.0F) screw(drawing, x, bounds.y + bounds.height - 13.0F);
        }
    }
}

void wood(Drawing& drawing, UiRect bounds) {
    if (!material_surface(bounds)) return;
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
    const float underside = std::min(3.0F, bounds.height);
    drawing.gradient({bounds.x, bounds.y + bounds.height - underside, bounds.width, underside},
                     {20, 10, 6, 0}, {20, 10, 6, 155});
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
    if (!material_surface(bounds)) return;
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
    const UiColor face_top = selected ? UiColor{254, 226, 173} :
        ivory ? UiColor{250, 237, 207} : shade(cap, 20);
    const UiColor face_bottom = selected ? UiColor{225, 185, 115} :
        ivory ? UiColor{225, 204, 166} : shade(cap, -7);
    const UiColor front_top = selected ? UiColor{197, 151, 86} :
        ivory ? UiColor{205, 180, 139} : shade(cap, -17);
    const UiColor front_bottom = selected ? UiColor{153, 110, 56} :
        ivory ? UiColor{165, 135, 91} : shade(cap, -42);
    // One small upper highlight and a darker front give the live tablet depth;
    // all labels and focus ink are still painted over the finished material.
    drawing.gradient(face_bounds, face_top, face_bottom);
    drawing.gradient({face_bounds.x, face_bounds.y, face_bounds.width,
                      std::min(4.0F, face_bounds.height * 0.12F)},
                     light ? UiColor{255, 248, 225, 75} : UiColor{190, 174, 147, 42},
                     {255, 244, 219, 0});
    drawing.line(face_bounds.x + 1.0F, face_bounds.y, face_bounds.x + face_bounds.width - 1.0F,
                 face_bounds.y, light ? UiColor{255, 245, 218} : UiColor{122, 108, 88});
    drawing.gradient({face_bounds.x, face_bounds.y + face_bounds.height,
                      face_bounds.width, front}, front_top, front_bottom);
    drawing.line(face_bounds.x, face_bounds.y + face_bounds.height,
                 face_bounds.x + face_bounds.width, face_bounds.y + face_bounds.height,
                 light ? shade(face_bottom, 14) : shade(cap, 14));
    drawing.line(face_bounds.x, face_bounds.y + 1.0F, face_bounds.x,
                 face_bounds.y + face_bounds.height - 1.0F,
                 light ? UiColor{255, 246, 219, 175} : UiColor{120, 106, 86, 150});
    drawing.line(face_bounds.x + face_bounds.width - 1.0F, face_bounds.y + 1.0F,
                 face_bounds.x + face_bounds.width - 1.0F, face_bounds.y + face_bounds.height + front - 1.0F,
                 light ? UiColor{124, 98, 63, 180} : UiColor{11, 11, 10, 200});
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
             std::uint8_t value, std::string_view label, UiColor cap, bool flat,
             bool wide_legibility = false) {
    if (!material_surface(geometry.bounds) || !material_surface(geometry.track)) return;
    const bool mixture = geometry.id.kind == UiControlKind::PedalDrawbar;
    const bool refined = wide_legibility && !flat && !mixture;
    UiRect material_strip{};
    if (refined) {
        if (!material_surface(geometry.label_bounds) || !material_surface(geometry.value_bounds) || value > 8) return;
        material_strip = {geometry.bounds.x, geometry.label_bounds.y + 21.0F,
                          geometry.bounds.width, geometry.value_bounds.y - geometry.label_bounds.y - 22.0F};
        if (!material_surface(material_strip)) return;
    } else {
        centered(drawing, label, geometry.label_bounds, mixture ? 11.0F : 13.0F,
                 kUiIvory, mixture ? TextFace::Sans : TextFace::Serif);
    }
    const auto& track = geometry.track;
    const float center = track.x + track.width / 2.0F;
    const float cap_width = std::max(10.0F, std::min(34.0F, geometry.bounds.width - 8.0F));
    const float cap_height = mixture ? 22.0F : refined ? 32.0F : 26.0F;
    const float half_height = cap_height / 2.0F;
    const float slot_width = std::min(geometry.bounds.width - 2.0F, cap_width + 8.0F);
    const UiRect slot{center - slot_width / 2.0F, track.y - half_height,
                      slot_width, track.height + cap_height};
    const float y = track.y + track.height * static_cast<float>(value) / 8.0F;
    const UiRect knob{center - cap_width / 2.0F, y - half_height, cap_width, cap_height};
    // Both endpoints fit between the unchanged text rows. Reject malformed
    // local geometry instead of letting material enter a label or readout.
    if (refined && (!material_surface(slot) || !material_surface(knob) ||
        slot.x < material_strip.x || slot.x + slot.width > material_strip.x + material_strip.width ||
        slot.y < material_strip.y || slot.y + slot.height > material_strip.y + material_strip.height ||
        knob.x < material_strip.x || knob.x + knob.width > material_strip.x + material_strip.width ||
        knob.y < material_strip.y || knob.y + knob.height > material_strip.y + material_strip.height)) return;
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
    // Recess walls and a substantial dark stem follow the reference material,
    // entirely inside the existing live slot and gesture geometry.
    if (slot.width > 4.0F && slot.height > 2.0F) {
        const float wall_height = std::max(0.0F, slot.height - 2.0F);
        drawing.gradient({slot.x + 1.0F, slot.y + 1.0F,
                          std::min(3.0F, slot.width - 2.0F), wall_height},
                         {47, 43, 36}, {22, 21, 18});
        drawing.gradient({slot.x + slot.width - 3.0F, slot.y + 1.0F,
                          2.0F, wall_height}, {27, 26, 23}, {13, 14, 12});
        drawing.gradient({slot.x + 1.0F, slot.y + 1.0F,
                          slot.width - 2.0F, std::min(6.0F, slot.height / 4.0F)},
                         {0, 0, 0, 135}, {0, 0, 0, 0});
    }
    drawing.line(slot.x, slot.y + 1.0F, slot.x, slot.y + slot.height - 1.0F, {63, 58, 49});
    drawing.line(slot.x + slot.width - 1.0F, slot.y, slot.x + slot.width - 1.0F,
                 slot.y + slot.height, {36, 34, 30});
    for (int tick = 0; tick <= 8; ++tick) {
        const float tick_y = track.y + track.height * static_cast<float>(tick) / 8.0F;
        drawing.line(slot.x + 1.0F, tick_y, slot.x + 3.0F, tick_y, {103, 94, 72});
    }
    const float shaft_width = std::min(9.0F, slot.width - 8.0F);
    const float exposed_height = std::max(0.0F, knob.y - track.y);
    if (shaft_width > 0.0F) {
        const float shaft_left = center - shaft_width / 2.0F;
        drawing.gradient({shaft_left, track.y, shaft_width, track.height},
                         {37, 36, 31}, {20, 22, 19});
        if (exposed_height > 0.0F) {
            drawing.gradient({shaft_left, track.y, shaft_width, exposed_height},
                             {70, 65, 54}, {43, 41, 34});
            drawing.rect({shaft_left, track.y, 1.0F, exposed_height}, {174, 158, 129, 170});
            drawing.rect({shaft_left + shaft_width - 1.0F, track.y, 1.0F, exposed_height},
                         {15, 16, 14});
        }
    }
    if (refined) {
        const float left = std::max(knob.x - 1.0F, material_strip.x);
        const float top = std::max(knob.y + 3.0F, material_strip.y);
        const float right = std::min(knob.x + knob.width + 2.0F, material_strip.x + material_strip.width);
        const float bottom = std::min(knob.y + knob.height + 4.0F, material_strip.y + material_strip.height);
        const UiRect shadow{left, top, right - left, bottom - top};
        if (material_surface(shadow)) drawing.rounded(shadow, 3.0F, {0, 0, 0, 210});
    } else {
        drawing.rounded({knob.x - 1.0F, knob.y + 3.0F, knob.width + 3.0F, knob.height + 1.0F}, 3.0F, {0, 0, 0, 210});
    }
    drawing.rounded(knob, 3.0F, shade(cap, -38));
    const bool ivory = cap.red == kIvoryCap.red && cap.green == kIvoryCap.green && cap.blue == kIvoryCap.blue;
    const float front = mixture ? 6.0F : refined ? 8.0F : 7.0F;
    const UiRect face{knob.x + 1.0F, knob.y + 2.0F, knob.width - 2.0F, knob.height - front - 3.0F};
    drawing.gradient(face, ivory ? UiColor{250, 237, 207} : shade(cap, 29),
                     ivory ? UiColor{225, 204, 166} : shade(cap, -2));
    drawing.gradient({face.x, face.y, face.width, std::min(4.0F, face.height * 0.12F)},
                     ivory ? UiColor{255, 248, 225, 75} : UiColor{222, 197, 162, 40},
                     {255, 244, 219, 0});
    drawing.gradient({face.x, face.y + face.height, face.width, front},
                     ivory ? UiColor{205, 180, 139} : shade(cap, -13),
                     ivory ? UiColor{165, 135, 91} : shade(cap, -34));
    drawing.line(face.x, face.y + 1.0F, face.x, face.y + face.height - 1.0F,
                 ivory ? UiColor{255, 246, 219} : shade(cap, 48));
    drawing.line(face.x + face.width - 1.0F, face.y + 1.0F,
                 face.x + face.width - 1.0F, face.y + face.height + front - 1.0F,
                 ivory ? UiColor{145, 118, 80} : shade(cap, -48));
    drawing.line(face.x + 2.0F, face.y, face.x + face.width - 2.0F, face.y,
                 ivory ? UiColor{255, 248, 224} : shade(cap, 65));
    drawing.line(face.x + 1.0F, face.y + face.height, face.x + face.width - 1.0F,
                 face.y + face.height, ivory ? UiColor{244, 224, 186} : shade(cap, 34));
    if (refined) {
        centered(drawing, label, {geometry.label_bounds.x, geometry.label_bounds.y,
                 geometry.label_bounds.width, 20.0F}, 17.0F, kUiIvory, TextFace::Serif, 2.0F);
        const char digit = static_cast<char>('0' + value);
        const std::string_view text{&digit, 1};
        const auto& bounds = geometry.value_bounds;
        // The pinned sans digits' ink at 14 px fits within this 16 px row;
        // its nominal 1.2-em line box is intentionally allowed to overhang.
        drawing.text(text, bounds.x + (bounds.width - drawing.text_width(text, 14.0F)) / 2.0F,
                     bounds.y + (bounds.height - 16.8F) / 2.0F, 14.0F, kUiBrass);
    } else {
        centered(drawing, std::to_string(value), geometry.value_bounds, 13.0F, kUiBrass);
    }
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

[[nodiscard]] std::string_view sounding_caption(const UiViewState& view, Manual manual) noexcept {
    constexpr std::array<std::string_view, 12> captions{
        "CANCELLED", "SOUNDING FIXED C#", "SOUNDING FIXED D", "SOUNDING FIXED D#",
        "SOUNDING FIXED E", "SOUNDING FIXED F", "SOUNDING FIXED F#", "SOUNDING FIXED G",
        "SOUNDING FIXED G#", "SOUNDING FIXED A", "SOUNDING A#", "SOUNDING B"};
    PresetSelection applied{};
    if (!control_preset_selection(view.applied.controls, manual, applied)) return "SOUNDING UNAVAILABLE";
    const auto index = static_cast<std::size_t>(applied);
    return index < captions.size() ? captions[index] : "SOUNDING UNAVAILABLE";
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

void paint_preset_label(Drawing& drawing, const UiControlGeometry& geometry) {
    const auto label = preset_selection_label(static_cast<PresetSelection>(geometry.id.index));
    const auto& bounds = geometry.label_bounds;
    if (preset_accidental(geometry.id.index)) {
        // The narrow ivory caps retain both characters at full size. Two
        // 11-unit line boxes at a 9-unit pitch have separated glyph ink while
        // leaving the top focus stroke visible even at the shortest breakpoint.
        centered(drawing, label.substr(0, 1), {bounds.x, bounds.y, bounds.width, 11.0F},
                 9.0F, {37, 29, 20}, TextFace::Sans, 0.0F);
        centered(drawing, label.substr(1), {bounds.x, bounds.y + 9.0F, bounds.width, 11.0F},
                 9.0F, {37, 29, 20}, TextFace::Sans, 0.0F);
        return;
    }
    centered(drawing, label, bounds, 9.0F, kUiIvory, TextFace::Sans, 0.0F);
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
        paint_preset_label(drawing, geometry);
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
    paint_preset_label(drawing, geometry);
}

void paint_preset_focus(Drawing& drawing, const UiControlGeometry& geometry) {
    const auto bounds = preset_indicator_bounds(geometry, 2.0F);
    // A natural's pitch fits between the side strokes. Leave the frame's lower
    // edge open: a full-width bottom stroke can cover the final glyph pixels
    // when the sidebar's lower manual lands at a fractional y coordinate.
    // This keeps the original label pixels and full-height side ink independent.
    if (!preset_accidental(geometry.id.index)) {
        const auto open_frame = [&](UiRect frame, float stroke, UiColor color) {
            drawing.rect({frame.x, frame.y, frame.width, stroke}, color);
            drawing.rect({frame.x, frame.y, stroke, frame.height}, color);
            drawing.rect({frame.x + frame.width - stroke, frame.y, stroke, frame.height}, color);
        };
        open_frame(bounds, 3.0F, {5, 6, 6});
        open_frame(inset(bounds, 1.0F), 1.0F, kUiFocusCyan);
        return;
    }
    const auto paint = [&] {
        drawing.outline(bounds, {5, 6, 6}, 3.0F);
        drawing.outline(inset(bounds, 1.0F), kUiFocusCyan, 1.0F);
    };
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
            drawbar(drawing, geometry, value, kUiFootageLabels[id.index], caps[id.index], flat,
                    layout.sidebar_pedals && !flat);
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
            const bool reference_percussion = layout.workspace == UiWorkspace::Play &&
                layout.sidebar_pedals && layout.presentation == UiPresentation::Dimensional;
            if (reference_percussion) {
                constexpr std::array<std::string_view, 4> reference_titles{"PERC", "HARM", "VOL", "DECAY"};
                centered(drawing, reference_titles[id.index], geometry.label_bounds, 10.5F, kUiIvory, TextFace::Serif);
                centered(drawing, value, geometry.value_bounds, 17.0F, {33, 28, 21}, TextFace::Serif);
            } else {
                centered(drawing, titles[id.index], geometry.label_bounds, 10.0F, {74, 54, 35});
                centered(drawing, value, geometry.value_bounds, 14.0F, {33, 28, 21}, TextFace::Serif);
            }
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

// A one-pixel band, one pixel inside the original sloping edge. Horizontal
// offsets are adjusted by its slope so width and inset are measured normally.
[[nodiscard]] UiQuad idle_key_side_band(const UiQuad& shape, bool left) noexcept {
    for (const auto& point : shape.points) {
        if (!std::isfinite(point.x) || !std::isfinite(point.y)) return {};
    }
    const auto& points = shape.points;
    const float height = points[3].y - points[0].y;
    if (!(height > 0.0F)) return {};
    const std::size_t top = left ? 0U : 1U;
    const std::size_t bottom = left ? 3U : 2U;
    const float offset = std::hypot(1.0F, (points[bottom].x - points[top].x) / height);
    if (!std::isfinite(offset)) return {};
    const auto edge_x = [&](std::size_t first, std::size_t last, float fraction) {
        return points[first].x + (points[last].x - points[first].x) * fraction;
    };
    constexpr float start = 0.08F;
    constexpr float finish = 0.88F;
    if (edge_x(1, 2, start) - edge_x(0, 3, start) <= 3.0F * offset ||
        edge_x(1, 2, finish) - edge_x(0, 3, finish) <= 3.0F * offset) return {};
    const auto point = [&](float fraction, float distance) {
        return UiPoint{edge_x(top, bottom, fraction) + (left ? distance : -distance) * offset,
                       points[0].y + height * fraction};
    };
    return left ? UiQuad{{point(start, 1.0F), point(start, 2.0F),
                          point(finish, 2.0F), point(finish, 1.0F)}} :
                  UiQuad{{point(start, 2.0F), point(start, 1.0F),
                          point(finish, 1.0F), point(finish, 2.0F)}};
}

void paint_key(Drawing& drawing, const UiKeyGeometry& key, bool held, bool focused, bool flat,
               bool wide_manual = false) {
    if (!material_surface(key.bounds)) return;
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
            held ? UiColor{166, 138, 88} : UiColor{61, 58, 52},
            held ? UiColor{104, 84, 48} : UiColor{20, 22, 19});
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
            held ? UiColor{190, 157, 96} : UiColor{198, 168, 124},
            held ? UiColor{145, 115, 62} : UiColor{131, 96, 62});
        drawing.quad_outline(key.hit, {83, 65, 42}, 0.7F);
        const float front_depth = key.front.points[3].y - key.front.points[0].y;
        const float front_highlight = front_depth > 0.0F ? std::min(0.13F, 2.0F / front_depth) : 0.0F;
        drawing.quad(quad_band(key.front, 0.0F, front_highlight, 0.9F),
                     {255, 245, 217, 220}, {255, 245, 217, 60});
        const float top_depth = key.top.points[3].y - key.top.points[0].y;
        const float rear_recess = top_depth > 0.0F ? std::min(0.12F, 18.0F / top_depth) : 0.0F;
        const bool refined = wide_manual && !held;
        drawing.quad(quad_band(key.top, 0.0F, rear_recess, 0.8F),
                     {20, 17, 13, static_cast<std::uint8_t>(refined ? 70 : 90)}, {20, 17, 13, 0});
        if (refined) {
            drawing.quad(idle_key_side_band(key.top, true), {255, 245, 219, 75}, {255, 245, 219, 28});
            drawing.quad(idle_key_side_band(key.top, false), {36, 26, 17, 40}, {36, 26, 17, 16});
        }
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
    if (!material_surface(cabinet) || !material_surface(art)) return;
    const bool flat = layout.presentation == UiPresentation::Flat;
    panel(drawing, cabinet, true, flat);
    heading(drawing, "ROTARY CABINET", {cabinet.x + 17.0F, cabinet.y + 6.0F,
            cabinet.width - 34.0F, 25.0F}, 16.0F);
    // The shared art rectangle is authoritative. Its small recess and rim stay
    // in the cabinet allocation; the separate sidebar pedal panel is untouched.
    const float recess = flat ? 2.0F : 3.0F;
    drawing.rect({art.x - recess, art.y - recess,
                  art.width + 2.0F * recess, art.height + 2.0F * recess}, {8, 9, 8});
    if (!drawing.reference_art(ReferenceArt::Cabinet, art)) {
        drawing.gradient(art, {34, 25, 18}, {12, 13, 11});
        const UiRect box{art.x + art.width * 0.2F, art.y + art.height * 0.13F,
                         art.width * 0.6F, art.height * 0.73F};
        if (flat) drawing.rect(box, kUiWalnut);
        else wood(drawing, box);
        for (int slot = 0; slot < 5; ++slot) {
            drawing.rect({box.x + box.width * 0.08F, box.y + 12.0F + static_cast<float>(slot) * 10.0F,
                          box.width * 0.84F, 4.0F}, {14, 10, 7});
        }
        centered(drawing, "DECORATIVE ART UNAVAILABLE", {art.x + 8.0F, art.y + art.height - 28.0F,
                 art.width - 16.0F, 20.0F}, 10.0F, kMuted);
    }
    if (!flat) {
        drawing.line(art.x - 2.0F, art.y - 3.0F, art.x + art.width + 2.0F,
                     art.y - 3.0F, {132, 112, 82, 170});
        drawing.line(art.x - 3.0F, art.y - 2.0F, art.x - 3.0F,
                     art.y + art.height + 2.0F, {95, 81, 61, 130});
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
        text_line(drawing, midi_state(info), {x, card.y + 49.0F, width, 14.0F}, 10.0F, info.midi_open ? kGreen : kMuted);
        text_line(drawing, "SCANNER / CHORUS: NOT CONNECTED", {x, card.y + 67.0F, width, 14.0F}, 10.0F, kMuted);
        text_line(drawing, "ROTARY AUDIO: NOT CONNECTED", {x, card.y + 85.0F, width, 14.0F}, 10.0F, kMuted);
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
    const bool flat = layout.presentation == UiPresentation::Flat;
    panel(drawing, boxes.panel, true, flat);
    const float x = boxes.panel.x + 28.0F;
    const float y = boxes.panel.y;
    drawing.text("MIDI input", x, y + 22.0F, 28.0F, kUiIvory, TextFace::Serif);
    button(drawing, boxes.close, "CLOSE", false, false, TextFace::Sans, false, flat);
    text_line(drawing, "SELECTED INPUT PORT / EXACT NAME", {x, y + 73.0F, boxes.panel.width - 56.0F, 16.0F}, 11.0F, kUiBrass);
    std::string_view choice = "No input";
    if (info.selected_midi_port < info.midi_choices.size()) choice = info.midi_choices[info.selected_midi_port];
    const UiRect port{boxes.previous_port.x + boxes.previous_port.width + 12.0F, y + 98.0F,
                       boxes.next_port.x - boxes.previous_port.x - boxes.previous_port.width - 24.0F, 77.0F};
    drawing.rect(inset({port.x - 6.0F, port.y - 5.0F, port.width + 12.0F, port.height + 10.0F}, 1.0F), {13, 15, 13});
    wrapped(drawing, choice, port, 12.0F, kUiIvory);
    button(drawing, boxes.previous_port, "<", false, false, TextFace::Sans, false, flat);
    button(drawing, boxes.next_port, ">", false, false, TextFace::Sans, false, flat);
    text_line(drawing, "Close and reopen to refresh ports. Full exact names: --list-midi",
              {x, y + 184.0F, boxes.panel.width - 56.0F, 16.0F}, 10.5F, kMuted);
    constexpr std::array<std::string_view, 3> names{"UPPER CHANNEL", "LOWER CHANNEL", "PEDAL CHANNEL"};
    const std::array<UiRect, 3> channels{boxes.upper_channel, boxes.lower_channel, boxes.pedal_channel};
    for (std::size_t index = 0; index < channels.size(); ++index) {
        const auto& bounds = channels[index];
        text_line(drawing, names[index], {bounds.x, bounds.y - 22.0F, bounds.width, 16.0F}, 11.0F, kUiBrass);
        button(drawing, bounds, std::to_string(info.selected_midi_channels[index]),
               false, false, TextFace::Sans, false, flat);
    }
    const auto& selected = info.selected_midi_channels;
    const bool distinct = selected[0] != selected[1] && selected[0] != selected[2] && selected[1] != selected[2];
    text_line(drawing, distinct ? "Three distinct wire channels, 1-16. Click or use arrows to change." :
              "Channels must be distinct. Change the repeated channel before Apply.",
              {x, y + 289.0F, boxes.panel.width - 56.0F, 18.0F}, 11.0F, distinct ? kMuted : kRed);
    constexpr std::array<std::string_view, 3> expression_names{
        "EXPRESSION MIN", "EXPRESSION MAX", "EXPRESSION DIRECTION"};
    const std::array<UiRect, 3> expression_controls{
        boxes.expression_minimum, boxes.expression_maximum, boxes.expression_direction};
    const auto& calibration = info.selected_midi_expression;
    const std::array<std::string, 3> expression_values{
        std::to_string(calibration.minimum), std::to_string(calibration.maximum),
        calibration.inverted ? "INVERTED" : "NORMAL"};
    for (std::size_t index = 0; index < expression_controls.size(); ++index) {
        const auto& bounds = expression_controls[index];
        text_line(drawing, expression_names[index],
                  {bounds.x, bounds.y - 22.0F, bounds.width, 16.0F}, 11.0F, kUiBrass);
        button(drawing, bounds, expression_values[index], false, false, TextFace::Sans, false, flat);
    }
    const bool valid_calibration = valid_midi_expression_calibration(calibration);
    text_line(drawing, valid_calibration ?
              "Selected calibration: raw 0-127. Arrows adjust; Home / End set bounds." :
              "Expression minimum must be less than maximum. Change either value before Apply.",
              {x, y + 382.0F, boxes.panel.width - 56.0F, 18.0F}, 11.0F,
              valid_calibration ? kMuted : kRed);
    const UiRect status{x, y + 410.0F, boxes.panel.width - 56.0F, 88.0F};
    drawing.rect(status, {17, 19, 16});
    const std::string connection = info.midi_reconnect_pending ? "MIDI RECONNECT PENDING" : midi_state(info);
    text_line(drawing, connection + (info.midi_backend.empty() ? "" : " / " + std::string(info.midi_backend)),
              {x + 12.0F, status.y + 8.0F, status.width - 24.0F, 18.0F}, 12.0F,
              info.midi_open && !info.midi_reconnect_pending ? kGreen : kUiBrass);
    std::string active_calibration = "ACTIVE CALIBRATION: none (inactive)";
    if (info.midi_expression_active) {
        const auto& active = info.active_midi_expression;
        active_calibration = "ACTIVE CALIBRATION: min " + std::to_string(active.minimum) +
            " / max " + std::to_string(active.maximum) + (active.inverted ? " / INVERTED" : " / NORMAL");
    }
    text_line(drawing, active_calibration,
              {x + 12.0F, status.y + 28.0F, status.width - 24.0F, 17.0F}, 11.0F,
              info.midi_expression_active ? kGreen : kMuted);
    wrapped(drawing, info.midi_status, {x + 12.0F, status.y + 49.0F, status.width - 24.0F, 32.0F}, 11.5F, kUiIvory);
    button(drawing, boxes.apply, "APPLY / CONNECT", distinct && valid_calibration && info.midi_available,
           false, TextFace::Sans, false, flat);
    button(drawing, boxes.disconnect, "DISCONNECT", false, false, TextFace::Sans, false, flat);
    text_line(drawing, "Apply uses selected settings; reconnect and Disconnect release MIDI-owned notes.",
              {x, y + 559.0F, boxes.panel.width - 56.0F, 16.0F}, 11.0F, kMuted);
    text_line(drawing, "Tab / Shift+Tab selects a control. Enter activates. Escape closes.",
              {x, y + 578.0F, boxes.panel.width - 56.0F, 14.0F}, 10.5F, kMuted);
}

void overlay(Drawing& drawing, const UiLayout& layout, const InstrumentViewInfo& info) {
    if (info.overlay == ViewOverlay::None) return;
    drawing.rect({0, 0, layout.width, layout.height}, {0, 0, 0, 185});
    if (info.overlay == ViewOverlay::Midi) {
        midi_overlay(drawing, layout, info);
        return;
    }
    const auto boxes = audio_overlay_layout(layout.width, layout.height);
    const bool flat = layout.presentation == UiPresentation::Flat;
    panel(drawing, boxes.panel, true, flat);
    const float x = boxes.panel.x + 28.0F;
    const float y = boxes.panel.y + 22.0F;
    drawing.text(info.overlay == ViewOverlay::Audio ? "Audio output" : "Playing the instrument",
                  x, y, 28.0F, kUiIvory, TextFace::Serif);
    button(drawing, boxes.close, "CLOSE", false, false, TextFace::Sans, false, flat);
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
    button(drawing, boxes.previous_device, "<", false, false, TextFace::Sans, false, flat);
    button(drawing, boxes.next_device, ">", false, false, TextFace::Sans, false, flat);
    drawing.text("SAMPLE RATE", x, y + 150.0F, 12.0F, kUiBrass);
    drawing.text("CALLBACK FRAMES", x + 270.0F, y + 150.0F, 12.0F, kUiBrass);
    button(drawing, boxes.sample_rate, std::to_string(info.selected_sample_rate) + " Hz",
           false, false, TextFace::Sans, false, flat);
    button(drawing, boxes.buffer_frames, std::to_string(info.selected_buffer_frames),
           false, false, TextFace::Sans, false, flat);
    drawing.text("Click a value to cycle through supported settings.", x, y + 234.0F, 14.0F, kMuted);
    drawing.text("Applying settings stops notes and restarts the audio device.", x, y + 265.0F, 14.0F, kMuted);
    drawing.text("Your drawbars and other musical controls are retained.", x, y + 292.0F, 14.0F, kMuted);
    button(drawing, boxes.apply, "APPLY AUDIO SETTINGS", true, false, TextFace::Sans, false, flat);
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
    if (layout.sidebar_pedals) {
        // Fit inside an interval symmetric about the window center. The wider
        // workspace tabs must not push the title toward the narrower tools.
        const float middle = layout.width / 2.0F;
        const float half_width = std::max(0.0F, std::min(middle - title_left, title_right - middle));
        title_left = middle - half_width;
        title_right = middle + half_width;
    }
    constexpr std::string_view title = "TONEWHEEL ATLAS";
    const bool reference_header = layout.sidebar_pedals && layout.presentation == UiPresentation::Dimensional;
    float size = reference_header ? 42.75F : (layout.show_cabinet ? 40.0F : 28.0F);
    const float natural_width = drawing.text_width(title, size, TextFace::Serif);
    if (natural_width > title_right - title_left) size *= (title_right - title_left) / natural_width;
    const float width = drawing.text_width(title, size, TextFace::Serif);
    const float desired_x = (layout.width - width) / 2.0F;
    const float x = std::clamp(desired_x, title_left, std::max(title_left, title_right - width));
    const float y = layout.header.y + (reference_header ? -4.5F : (layout.show_cabinet ? 4.0F : 8.0F));
    drawing.text(title, x + 1.0F, y + 2.0F, size, {4, 5, 4}, TextFace::Serif);
    drawing.text(title, x, y, size, kUiBrass, TextFace::Serif);
    if (reference_header) {
        // Match the reference's two-line hierarchy with the truthful caption.
        // Its fixed seventeen glyphs fit symmetrically before Flat: reduce
        // tracking first, then size, without allocating or dropping letters.
        constexpr std::string_view caption = "NOMINAL DRY ORGAN";
        constexpr float gaps = static_cast<float>(caption.size() - 1);
        const float middle = layout.width / 2.0F;
        const float half_width = std::max(0.0F, std::min(middle - title_left,
            std::min(title_right, flat_left - 10.0F) - middle));
        const float caption_width = std::min(374.0F, 2.0F * half_width);
        float caption_size = 17.0F;
        float natural_caption_width = drawing.text_width(caption, caption_size);
        const float tracking = std::max(0.0F, (caption_width - natural_caption_width) / gaps);
        if (natural_caption_width > caption_width) {
            caption_size *= caption_width / natural_caption_width;
            natural_caption_width = drawing.text_width(caption, caption_size);
        }
        float cursor = middle - (natural_caption_width + gaps * tracking) / 2.0F;
        for (std::size_t index = 0; index < caption.size(); ++index) {
            const auto glyph = caption.substr(index, 1);
            drawing.text(glyph, cursor, layout.header.y + 51.5F, caption_size, kUiBrass);
            cursor += drawing.text_width(glyph, caption_size) + tracking;
        }
    } else {
        centered(drawing, "NOMINAL DRY ORGAN", {title_left, layout.header.y + layout.header.height - 29.0F,
                 std::max(0.0F, flat_left - title_left - 10.0F), 22.0F}, 11.0F, kUiIvory);
    }
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

// Active composition helpers use mapped model geometry. Only their local
// material distances are scaled here; glyph sizes remain isotropic. Helpers
// preserve the incoming renderer transform and the live hit layout.
[[nodiscard]] UiRect reference_inset(UiRect bounds, float amount,
                                      ReferenceCompositionScale scale) noexcept {
    const float x = amount * scale.sx;
    const float y = amount * scale.sy;
    return {bounds.x + x, bounds.y + y,
            std::max(0.0F, bounds.width - 2.0F * x),
            std::max(0.0F, bounds.height - 2.0F * y)};
}

void reference_outline(Drawing& drawing, UiRect bounds, UiColor color, float thickness,
                       ReferenceCompositionScale scale) {
    if (!material_surface(bounds)) return;
    const float x = std::min(thickness * scale.sx, bounds.width / 2.0F);
    const float y = std::min(thickness * scale.sy, bounds.height / 2.0F);
    drawing.rect({bounds.x, bounds.y, bounds.width, y}, color);
    drawing.rect({bounds.x, bounds.y + bounds.height - y, bounds.width, y}, color);
    drawing.rect({bounds.x, bounds.y + y, x, bounds.height - 2.0F * y}, color);
    drawing.rect({bounds.x + bounds.width - x, bounds.y + y, x,
                  bounds.height - 2.0F * y}, color);
}

void reference_screw(Drawing& drawing, float x, float y, ReferenceCompositionScale scale) {
    drawing.rounded({x - scale.sx, y - scale.sy, 8.0F * scale.sx, 8.0F * scale.sy},
                    4.0F * scale.f, {8, 9, 8});
    drawing.rounded({x, y, 6.0F * scale.sx, 6.0F * scale.sy}, 3.0F * scale.f, {131, 107, 65});
    drawing.rect({x + scale.sx, y + scale.sy, 3.0F * scale.sx, scale.sy}, {221, 188, 125});
    drawing.line(x + 1.5F * scale.sx, y + 4.5F * scale.sy,
                 x + 4.5F * scale.sx, y + 1.5F * scale.sy, {34, 29, 20});
}

// The v1.1 material arithmetic rounds each operation separately to binary64.
// A private volatile boundary prevents contraction across multiply/add joins
// without changing compilation or arithmetic in the existing painters.
[[nodiscard]] double upper_rack_binary64(double value) noexcept {
    volatile double rounded = value;
    return rounded;
}

[[nodiscard]] double upper_rack_field(double u, double v) noexcept {
    const double lateral = upper_rack_binary64(7.6 * u);
    const double vertical = upper_rack_binary64(9.4 * v);
    const double base = upper_rack_binary64(22.4 + lateral);
    return upper_rack_binary64(base - vertical);
}

[[nodiscard]] UiColor upper_rack_color(double q) noexcept {
    const auto channel = [](double value) {
        return static_cast<std::uint8_t>(std::clamp(std::round(value), 0.0, 255.0));
    };
    return {channel(upper_rack_binary64(q + 1.0)), channel(q),
            channel(upper_rack_binary64(q - 1.0)), 255};
}

class UpperRackColorGuard {
public:
    explicit UpperRackColorGuard(SDL_Renderer* renderer) noexcept : renderer_(renderer) {
        saved_ = SDL_GetRenderDrawColor(renderer_, &color_.red, &color_.green,
                                       &color_.blue, &color_.alpha) == 0;
    }
    ~UpperRackColorGuard() {
        if (saved_) SDL_SetRenderDrawColor(renderer_, color_.red, color_.green,
                                           color_.blue, color_.alpha);
    }
    UpperRackColorGuard(const UpperRackColorGuard&) = delete;
    UpperRackColorGuard& operator=(const UpperRackColorGuard&) = delete;
    [[nodiscard]] bool saved() const noexcept { return saved_; }

private:
    SDL_Renderer* renderer_{};
    UiColor color_{};
    bool saved_{};
};

// Private counterpart of Drawing's PixelRaster: physical clipping and integer
// center spans, with a scoped scale change. Viewport, clip (including enabled
// empty clips) and blend mode are never reset through rounded logical getters.
class UpperRackRaster {
public:
    explicit UpperRackRaster(SDL_Renderer* renderer) noexcept : renderer_(renderer) {
        int width = 0;
        int height = 0;
        if (SDL_GetRendererOutputSize(renderer_, &width, &height) != 0 ||
            width <= 0 || height <= 0) return;
        SDL_RenderGetScale(renderer_, &scale_x_, &scale_y_);
        if (!std::isfinite(scale_x_) || !std::isfinite(scale_y_) ||
            scale_x_ <= 0.0F || scale_y_ <= 0.0F) return;
        if (SDL_RenderSetScale(renderer_, 1.0F, 1.0F) != 0) return;
        restore_scale_ = true;
        SDL_Rect viewport{};
        SDL_RenderGetViewport(renderer_, &viewport);
        if (viewport.w <= 0 || viewport.h <= 0) return;
        std::int64_t left = std::max<std::int64_t>(0, -static_cast<std::int64_t>(viewport.x));
        std::int64_t top = std::max<std::int64_t>(0, -static_cast<std::int64_t>(viewport.y));
        std::int64_t right = std::min<std::int64_t>(viewport.w,
            static_cast<std::int64_t>(width) - viewport.x);
        std::int64_t bottom = std::min<std::int64_t>(viewport.h,
            static_cast<std::int64_t>(height) - viewport.y);
        if (SDL_RenderIsClipEnabled(renderer_) == SDL_TRUE) {
            SDL_Rect clip{};
            SDL_RenderGetClipRect(renderer_, &clip);
            if (clip.w <= 0 || clip.h <= 0) return;
            left = std::max(left, static_cast<std::int64_t>(clip.x));
            top = std::max(top, static_cast<std::int64_t>(clip.y));
            right = std::min(right, static_cast<std::int64_t>(clip.x) + clip.w);
            bottom = std::min(bottom, static_cast<std::int64_t>(clip.y) + clip.h);
        }
        if (left >= right || top >= bottom) return;
        left_ = static_cast<int>(left);
        right_ = static_cast<int>(right);
        top_ = static_cast<int>(top);
        bottom_ = static_cast<int>(bottom);
    }

    ~UpperRackRaster() {
        if (restore_scale_) SDL_RenderSetScale(renderer_, scale_x_, scale_y_);
    }
    UpperRackRaster(const UpperRackRaster&) = delete;
    UpperRackRaster& operator=(const UpperRackRaster&) = delete;
    [[nodiscard]] bool visible() const noexcept { return left_ < right_ && top_ < bottom_; }
    [[nodiscard]] int x_boundary(double x) const noexcept {
        return boundary(upper_rack_binary64(x * static_cast<double>(scale_x_)), left_, right_);
    }
    [[nodiscard]] int y_boundary(double y) const noexcept {
        return boundary(upper_rack_binary64(y * static_cast<double>(scale_y_)), top_, bottom_);
    }
    [[nodiscard]] double logical_y(int row) const noexcept {
        return upper_rack_binary64(upper_rack_binary64(static_cast<double>(row) + 0.5) /
                                   static_cast<double>(scale_y_));
    }
    void span(int first, int end, int row) const noexcept {
        if (first >= end) return;
        if (end - first == 1) SDL_RenderDrawPoint(renderer_, first, row);
        else SDL_RenderDrawLine(renderer_, first, row, end - 1, row);
    }

private:
    [[nodiscard]] static int boundary(double edge, int minimum, int maximum) noexcept {
        const double value = std::ceil(upper_rack_binary64(edge - 0.5));
        if (value <= minimum) return minimum;
        if (value >= maximum) return maximum;
        return static_cast<int>(value);
    }

    SDL_Renderer* renderer_{};
    float scale_x_{1.0F};
    float scale_y_{1.0F};
    bool restore_scale_{};
    int left_{};
    int right_{};
    int top_{};
    int bottom_{};
};

[[nodiscard]] std::uint32_t upper_rack_mix(std::uint32_t value) noexcept {
    value ^= value >> 16U;
    value = static_cast<std::uint32_t>(value * 0x7FEB352DU);
    value ^= value >> 15U;
    value = static_cast<std::uint32_t>(value * 0x846CA68BU);
    value ^= value >> 16U;
    return value;
}

void reference_upper_rack_material(Drawing& drawing, UiRect bounds,
                                   ReferenceCompositionScale scale) noexcept {
    if (!material_surface(bounds) || drawing.renderer() == nullptr) return;
    auto* renderer = drawing.renderer();
    const UpperRackColorGuard color_guard(renderer);
    if (!color_guard.saved()) return;
    {
        const UpperRackRaster raster(renderer);
        if (!raster.visible()) return;
        std::array<int, 66> edges{};
        for (std::size_t column = 0; column < edges.size(); ++column) {
            const double product = upper_rack_binary64(static_cast<double>(bounds.width) *
                                                       static_cast<double>(column));
            const double offset = upper_rack_binary64(product / 65.0);
            edges[column] = raster.x_boundary(upper_rack_binary64(
                static_cast<double>(bounds.x) + offset));
        }
        const int first_row = raster.y_boundary(bounds.y);
        const int end_row = raster.y_boundary(upper_rack_binary64(
            static_cast<double>(bounds.y) + static_cast<double>(bounds.height)));
        if (edges.front() >= edges.back() || first_row >= end_row) return;
        const double height = upper_rack_binary64(static_cast<double>(bounds.height) - 1.0);
        for (int row = first_row; row < end_row; ++row) {
            const double offset = upper_rack_binary64(raster.logical_y(row) -
                                                      static_cast<double>(bounds.y));
            const double center = upper_rack_binary64(offset - 0.5);
            const double v = bounds.height <= 1.0F ? 0.0 : std::clamp(
                upper_rack_binary64(center / height), 0.0, 1.0);
            for (std::size_t column = 0; column < 65; ++column) {
                if (edges[column] >= edges[column + 1]) continue;
                const double u = upper_rack_binary64(upper_rack_binary64(
                    static_cast<double>(column) + 0.5) / 65.0);
                const UiColor color = upper_rack_color(upper_rack_field(u, v));
                SDL_SetRenderDrawColor(renderer, color.red, color.green, color.blue, color.alpha);
                raster.span(edges[column], edges[column + 1], row);
            }
        }
    }
    // The field guard has restored the incoming scale before Drawing::rect.
    // All 2,048 pairs are visited in order, even when only a clip is visible.
    constexpr std::uint32_t seed = 0xB3A08E11U;
    for (std::uint32_t pair = 0; pair < 2048U; ++pair) {
        for (std::uint32_t mark = 0; mark < 2U; ++mark) {
            const std::uint32_t k = 4U * pair + 2U * mark;
            const std::uint32_t cx = 78U + upper_rack_mix(seed ^ k) % 516U;
            const std::uint32_t cy = 275U + upper_rack_mix(seed ^ (k + 1U)) % 227U;
            const double center = upper_rack_binary64(static_cast<double>(cx) + 0.5);
            const double u = upper_rack_binary64(upper_rack_binary64(center - 76.0) / 520.0);
            const double v = upper_rack_binary64(upper_rack_binary64(
                static_cast<double>(cy) - 273.0) / 230.0);
            const double q = upper_rack_binary64(upper_rack_field(u, v) + (mark == 0U ? 8.0 : -8.0));
            const auto origin = reference_composition_point(
                {static_cast<float>(cx), static_cast<float>(cy)}, scale);
            drawing.rect({origin.x, origin.y, scale.sx, scale.sy}, upper_rack_color(q));
        }
    }
}

// Lower v1 has its own illumination and grain. The existing mechanical raster
// helpers are reused without changing the independently admitted Upper field.
[[nodiscard]] std::array<double, 3> lower_rack_field(double u, double v) noexcept {
    const auto r = upper_rack_binary64;
    const double t = r(v - 0.48);
    const double t2 = r(t * t);
    const double t3 = r(t2 * t);
    const double left_weight = std::max(0.0, r(1.0 - r(5.0 * u)));
    const double right_weight = std::max(0.0, r(1.0 - r(5.0 * r(1.0 - u))));
    const double left = r(r(r(61.0 * r(u - r(17.0 / 508.0))) * left_weight) * left_weight);
    const double right = r(r(r(-74.0 * r(u - r(497.0 / 508.0))) * right_weight) * right_weight);
    const double curve = r(r(r(40.0 - r(52.0 * u)) * t3) +
                           r(r(4.0 * u) * r(t2 - 0.02581)));
    const double correction = r(r(left + right) + curve);
    constexpr std::array<std::array<double, 4>, 3> coefficients{{
        {35.320924203, -10.874155773, -12.501738043, 6.205237100},
        {34.943428203, -11.336804366, -14.777279430, 7.789951248},
        {35.610452235, -13.973112652, -15.176662864, 10.100565245},
    }};
    std::array<double, 3> result{};
    for (std::size_t channel = 0; channel < result.size(); ++channel) {
        const auto& c = coefficients[channel];
        const double base = r(r(r(c[0] + r(c[1] * u)) + r(c[2] * v)) + r(r(c[3] * u) * v));
        result[channel] = r(base + correction);
    }
    return result;
}

[[nodiscard]] UiColor lower_rack_color(const std::array<double, 3>& field,
                                      double grain = 0.0) noexcept {
    const auto channel = [grain](double value) {
        return static_cast<std::uint8_t>(std::clamp(
            std::round(upper_rack_binary64(value + grain)), 0.0, 255.0));
    };
    return {channel(field[0]), channel(field[1]), channel(field[2]), 255};
}

void reference_lower_rack_material(Drawing& drawing, UiRect bounds,
                                   ReferenceCompositionScale scale) noexcept {
    if (!material_surface(bounds) || drawing.renderer() == nullptr) return;
    auto* renderer = drawing.renderer();
    const UpperRackColorGuard color_guard(renderer);
    if (!color_guard.saved()) return;
    const auto r = upper_rack_binary64;
    {
        const UpperRackRaster raster(renderer);
        if (!raster.visible()) return;
        std::array<int, 128> edges{};
        for (std::size_t column = 0; column < edges.size(); ++column) {
            const double product = r(static_cast<double>(bounds.width) * static_cast<double>(column));
            edges[column] = raster.x_boundary(r(static_cast<double>(bounds.x) + r(product / 127.0)));
        }
        const int first_row = raster.y_boundary(bounds.y);
        const int end_row = raster.y_boundary(r(static_cast<double>(bounds.y) +
                                                static_cast<double>(bounds.height)));
        if (edges.front() >= edges.back() || first_row >= end_row) return;
        const double height = r(static_cast<double>(bounds.height) - 1.0);
        for (int row = first_row; row < end_row; ++row) {
            const double offset = r(raster.logical_y(row) - static_cast<double>(bounds.y));
            const double center = r(offset - 0.5);
            const double v = bounds.height <= 1.0F ? 0.0 : std::clamp(r(center / height), 0.0, 1.0);
            for (std::size_t column = 0; column < 127; ++column) {
                if (edges[column] >= edges[column + 1]) continue;
                const double u = r(r(static_cast<double>(column) + 0.5) / 127.0);
                const auto color = lower_rack_color(lower_rack_field(u, v));
                SDL_SetRenderDrawColor(renderer, color.red, color.green, color.blue, color.alpha);
                raster.span(edges[column], edges[column + 1], row);
            }
        }
    }
    // The raster guard restores both incoming scales before canonical marks.
    constexpr std::uint32_t seed = 0xB3160A08U;
    for (std::uint32_t pair = 0; pair < 2304U; ++pair) {
        for (std::uint32_t mark = 0; mark < 2U; ++mark) {
            const std::uint32_t k = 4U * pair + 2U * mark;
            const std::uint32_t cx = 606U + upper_rack_mix(seed ^ k) % 504U;
            const std::uint32_t cy = 275U + upper_rack_mix(seed ^ (k + 1U)) % 227U;
            const double u = r(r(r(static_cast<double>(cx) + 0.5) - 604.0) / 508.0);
            const double v = r(r(static_cast<double>(cy) - 273.0) / 230.0);
            const auto color = lower_rack_color(lower_rack_field(u, v), mark == 0U ? 8.0 : -8.0);
            const auto origin = reference_composition_point(
                {static_cast<float>(cx), static_cast<float>(cy)}, scale);
            drawing.rect({origin.x, origin.y, scale.sx, scale.sy}, color);
        }
    }
}

enum class ReferencePanelMaterial { Original, UpperRack, LowerRack };

void reference_panel(Drawing& drawing, UiRect bounds, ReferenceCompositionScale scale,
                     bool screws = true, ReferencePanelMaterial material = ReferencePanelMaterial::Original) {
    if (!material_surface(bounds)) return;
    for (int layer = 5; layer >= 1; --layer) {
        const float spread = static_cast<float>(layer);
        drawing.rounded({bounds.x - spread * scale.sx, bounds.y + (2.0F - spread) * scale.sy,
                         bounds.width + 2.0F * spread * scale.sx,
                         bounds.height + 2.0F * spread * scale.sy},
                        (5.0F + spread) * scale.f, {0, 0, 0, 16});
    }
    drawing.rounded(bounds, 6.0F * scale.f, {7, 7, 7});
    drawing.rounded(reference_inset(bounds, 1.0F, scale), 5.0F * scale.f, kMetalEdge);
    drawing.rounded(reference_inset(bounds, 2.0F, scale), 4.0F * scale.f, {14, 14, 14});
    if (material == ReferencePanelMaterial::UpperRack) {
        reference_upper_rack_material(drawing, reference_inset(bounds, 4.0F, scale), scale);
    } else if (material == ReferencePanelMaterial::LowerRack) {
        reference_lower_rack_material(drawing, reference_inset(bounds, 4.0F, scale), scale);
    } else {
        drawing.gradient(reference_inset(bounds, 4.0F, scale), {43, 41, 38}, {21, 22, 21});
        constexpr std::size_t maximum_grain_pairs = 2048;
        const auto rows = static_cast<int>(std::max(0.0F, std::floor(bounds.height / scale.sy - 16.0F)));
        const auto columns = static_cast<int>(std::max(0.0F, std::floor(bounds.width / scale.sx - 21.0F)));
        int step = std::max(4, static_cast<int>(std::ceil(std::sqrt(
            static_cast<double>(rows) * static_cast<double>(columns) /
            (3.0 * static_cast<double>(maximum_grain_pairs))))));
        const auto pair_count = [rows, columns](int pitch) {
            const auto row_count = rows > 1 ? static_cast<std::size_t>((rows - 2) / pitch + 1) : 0;
            const auto column_count = columns > 1 ? static_cast<std::size_t>((columns - 2) / (pitch * 3) + 1) : 0;
            return row_count * column_count;
        };
        while (pair_count(step) > maximum_grain_pairs) ++step;
        std::size_t pairs = 0;
        for (int row = 1; row < rows && pairs < maximum_grain_pairs; row += step) {
            for (int column = 1; column < columns && pairs < maximum_grain_pairs; column += step * 3) {
                const auto grain = static_cast<std::uint32_t>(row) * 1973U +
                    static_cast<std::uint32_t>(column) * 9277U;
                const float x = bounds.x + (7.0F + static_cast<float>(column) +
                    static_cast<float>((grain >> 5U) % 3U)) * scale.sx;
                const float y = bounds.y + (7.0F + static_cast<float>(row)) * scale.sy;
                drawing.rect({x, y, scale.sx, scale.sy},
                             {212, 205, 190, static_cast<std::uint8_t>(6U + grain % 5U)});
                drawing.rect({x + 3.0F * scale.sx, y + scale.sy, 2.0F * scale.sx, scale.sy},
                             {0, 0, 0, static_cast<std::uint8_t>(10U + (grain >> 3U) % 9U)});
                ++pairs;
            }
        }
    }
    drawing.rect({bounds.x + 7.0F * scale.sx, bounds.y + 3.0F * scale.sy,
                  bounds.width - 14.0F * scale.sx, scale.sy}, {147, 133, 111, 120});
    drawing.rect({bounds.x + 3.0F * scale.sx, bounds.y + 7.0F * scale.sy,
                  scale.sx, bounds.height - 14.0F * scale.sy}, {123, 112, 94, 92});
    drawing.rect({bounds.x + 7.0F * scale.sx, bounds.y + bounds.height - 3.0F * scale.sy,
                  bounds.width - 14.0F * scale.sx, scale.sy}, {7, 8, 7});
    drawing.rect({bounds.x + bounds.width - 3.0F * scale.sx, bounds.y + 7.0F * scale.sy,
                  scale.sx, bounds.height - 14.0F * scale.sy}, {7, 8, 7});
    if (screws) {
        for (const float x : {bounds.x + 7.0F * scale.sx,
                              bounds.x + bounds.width - 13.0F * scale.sx}) {
            reference_screw(drawing, x, bounds.y + 7.0F * scale.sy, scale);
            if (bounds.height > 80.0F * scale.sy)
                reference_screw(drawing, x, bounds.y + bounds.height - 13.0F * scale.sy, scale);
        }
    }
}

void reference_wood(Drawing& drawing, UiRect bounds, ReferenceCompositionScale scale) {
    if (!material_surface(bounds)) return;
    drawing.gradient(bounds, {111, 64, 34}, {54, 28, 17});
    const auto rows = static_cast<int>(bounds.height / scale.sy);
    for (int row = 2; row < rows; row += 3) {
        const auto alpha = static_cast<std::uint8_t>(15 + (row * 29) % 29);
        const float y = bounds.y + static_cast<float>(row) * scale.sy;
        drawing.rect({bounds.x, y, bounds.width, scale.sy}, {18, 8, 4, alpha});
        if (row % 9 == 2)
            drawing.rect({bounds.x, y + scale.sy, bounds.width, scale.sy}, {223, 154, 86, 25});
    }
    drawing.rect({bounds.x, bounds.y + scale.sy, bounds.width, scale.sy}, {207, 140, 82, 150});
    const float underside = std::min(3.0F * scale.sy, bounds.height);
    drawing.gradient({bounds.x, bounds.y + bounds.height - underside, bounds.width, underside},
                     {20, 10, 6, 0}, {20, 10, 6, 155});
    drawing.rect({bounds.x, bounds.y + bounds.height - scale.sy, bounds.width, scale.sy}, {17, 9, 5});
}

void reference_heading(Drawing& drawing, std::string_view value, UiRect bounds, float size,
                       ReferenceCompositionScale scale) {
    centered(drawing, value, bounds, size * scale.f, kUiBrass, TextFace::Serif, 3.0F * scale.sx);
    const float half_gap = drawing.text_width(value, size * scale.f, TextFace::Serif) / 2.0F + 14.0F * scale.sx;
    const float middle = bounds.x + bounds.width / 2.0F;
    if (half_gap < bounds.width / 2.0F - 16.0F * scale.sx) {
        const float y = bounds.y + bounds.height / 2.0F;
        drawing.rect({bounds.x + 9.0F * scale.sx, y,
                      middle - half_gap - bounds.x - 9.0F * scale.sx, scale.sy}, kMetalEdge);
        drawing.rect({middle + half_gap, y,
                      bounds.x + bounds.width - 9.0F * scale.sx - middle - half_gap, scale.sy}, kMetalEdge);
    }
}

// T2 is confined to the two manual racks; other reference headings retain
// their original centered text and rules. Tracking uses the same live glyph
// advances as painting, with fixed storage and no font or layout mutation.
void reference_rack_heading(Drawing& drawing, UiRect bounds, bool upper,
                            ReferenceCompositionScale scale) {
    constexpr std::string_view upper_text = "UPPER MANUAL DRAWBARS";
    constexpr std::string_view lower_text = "LOWER MANUAL DRAWBARS";
    static_assert(upper_text.size() == 21 && lower_text.size() == upper_text.size());
    const auto value = upper ? upper_text : lower_text;
    const float size = 16.0F * scale.f;
    const float tracking = (upper ? 1.5F : 1.7F) * scale.sx;
    const float center = (upper ? 360.0F : 875.5F) * scale.sx;
    const float top = bounds.y + (bounds.height - size * 1.2F) / 2.0F + scale.sy;
    std::array<float, upper_text.size()> advances{};
    float natural = 0.0F;
    for (std::size_t index = 0; index < value.size(); ++index) {
        advances[index] = drawing.text_width(value.substr(index, 1), size, TextFace::Serif);
        natural += advances[index];
    }
    const float run_width = natural + tracking * 20.0F;
    const float left = center - run_width / 2.0F;
    float cursor = left;
    for (std::size_t index = 0; index < value.size(); ++index) {
        drawing.text(value.substr(index, 1), cursor, top, size, kUiBrass, TextFace::Serif);
        cursor += advances[index] + tracking;
    }
    const float outer_left = (upper ? 140.0F : 662.0F) * scale.sx;
    const float outer_right = (upper ? 564.0F : 1083.0F) * scale.sx;
    const float inner_left = left - 16.0F * scale.sx;
    const float inner_right = (center + run_width / 2.0F) + 16.0F * scale.sx;
    const float y = 292.0F * scale.sy;
    drawing.rect({outer_left, y, inner_left - outer_left, scale.sy}, kMetalEdge);
    drawing.rect({inner_right, y, outer_right - inner_right, scale.sy}, kMetalEdge);
}

void reference_button(Drawing& drawing, const UiControlGeometry& geometry,
                      std::string_view label, float size, ReferenceCompositionScale scale,
                      bool selected = false, bool warning = false,
                      TextFace face = TextFace::Sans, bool ivory = false) {
    const auto& bounds = geometry.bounds;
    if (!material_surface(bounds)) return;
    const bool light = selected || ivory;
    const UiColor cap = selected ? UiColor{238, 204, 145} : ivory ? kIvoryCap : UiColor{45, 41, 36};
    drawing.rounded(bounds, 5.0F * scale.f, {5, 5, 5});
    drawing.rounded(reference_inset(bounds, 1.0F, scale), 4.0F * scale.f,
                    selected ? UiColor{137, 105, 62} : UiColor{77, 69, 56});
    drawing.rounded(reference_inset(bounds, 2.0F, scale), 3.0F * scale.f, {18, 17, 15});
    const float recess = selected ? scale.sy : 0.0F;
    const UiRect cap_bounds{bounds.x + 4.0F * scale.sx, bounds.y + 3.0F * scale.sy + recess,
                            bounds.width - 10.0F * scale.sx, bounds.height - 8.0F * scale.sy - recess};
    drawing.rounded({cap_bounds.x + 2.0F * scale.sx, cap_bounds.y + 3.0F * scale.sy,
                     cap_bounds.width, cap_bounds.height}, 3.0F * scale.f, {0, 0, 0, 210});
    drawing.rounded(cap_bounds, 3.0F * scale.f, shade(cap, -35));
    const float front = std::clamp(bounds.height / scale.sy * 0.12F, 3.0F, 5.0F) * scale.sy;
    const UiRect surface{cap_bounds.x + scale.sx, cap_bounds.y + scale.sy,
                         cap_bounds.width - 2.0F * scale.sx, cap_bounds.height - front - scale.sy};
    const UiColor top = selected ? UiColor{254, 226, 173} : ivory ? UiColor{250, 237, 207} : shade(cap, 20);
    const UiColor bottom = selected ? UiColor{225, 185, 115} : ivory ? UiColor{225, 204, 166} : shade(cap, -7);
    drawing.gradient(surface, top, bottom);
    drawing.gradient({surface.x, surface.y, surface.width, std::min(4.0F * scale.sy, surface.height * 0.12F)},
                     light ? UiColor{255, 248, 225, 75} : UiColor{190, 174, 147, 42}, {255, 244, 219, 0});
    drawing.rect({surface.x + scale.sx, surface.y, surface.width - 2.0F * scale.sx, scale.sy},
                 light ? UiColor{255, 245, 218} : UiColor{122, 108, 88});
    drawing.gradient({surface.x, surface.y + surface.height, surface.width, front},
                     selected ? UiColor{197, 151, 86} : ivory ? UiColor{205, 180, 139} : shade(cap, -17),
                     selected ? UiColor{153, 110, 56} : ivory ? UiColor{165, 135, 91} : shade(cap, -42));
    drawing.rect({surface.x, surface.y + surface.height, surface.width, scale.sy},
                 light ? shade(bottom, 14) : shade(cap, 14));
    drawing.rect({surface.x, surface.y + scale.sy, scale.sx, surface.height - 2.0F * scale.sy},
                 light ? UiColor{255, 246, 219, 175} : UiColor{120, 106, 86, 150});
    drawing.rect({surface.x + surface.width - scale.sx, surface.y + scale.sy,
                  scale.sx, surface.height + front - 2.0F * scale.sy},
                 light ? UiColor{124, 98, 63, 180} : UiColor{11, 11, 10, 200});
    centered(drawing, label, geometry.label_bounds, size * scale.f,
             warning ? (light ? UiColor{112, 43, 24} : kRed) : light ? UiColor{35, 29, 21} : kUiIvory,
             face, 3.0F * scale.sx);
}

[[nodiscard]] float reference_footage_round(float value) noexcept {
    // Keep the admitted binary32 operation boundaries even when contraction is enabled.
    volatile float rounded = value;
    return rounded;
}

void reference_manual_footage(Drawing& drawing, std::string_view label, UiRect bounds,
                              ReferenceCompositionScale scale) {
    if (!(bounds.width > 0.0F && bounds.height > 0.0F)) return;
    const bool mixed = label == "5 1/3'" || label == "2 2/3'" ||
        label == "1 3/5'" || label == "1 1/3'";
    const bool ordinary = label == "16'" || label == "8'" || label == "4'" ||
        label == "2'" || label == "1'";
    if (!mixed && !ordinary) {
        centered(drawing, label, bounds, 19.0F * scale.f,
                 kUiIvory, TextFace::Serif, 2.0F * scale.sx);
        return;
    }

    // Mixed footages keep their complete ASCII identity in five measured runs.
    // Only font size uses f; vertical baselines use sy and the two gaps use sx.
    std::array<std::string_view, 5> runs{label, {}, {}, {}, {}};
    if (mixed) {
        runs = {label.substr(0, 1), label.substr(2, 1), label.substr(3, 1),
                label.substr(4, 1), label.substr(5, 1)};
    }
    constexpr std::array<float, 5> nominal_sizes{20.5F, 13.0F, 16.0F, 13.0F, 20.5F};
    constexpr std::array<float, 5> baseline_offsets{21.5F, 15.5F, 19.5F, 21.5F, 21.5F};
    std::array<float, 5> sizes{};
    std::array<float, 5> advances{};
    const std::size_t count = mixed ? 5U : 1U;
    const float gap = reference_footage_round(0.5F * scale.sx);
    float width = 0.0F;
    for (std::size_t i = 0; i < count; ++i) {
        sizes[i] = reference_footage_round(nominal_sizes[i] * scale.f);
        advances[i] = drawing.text_width(runs[i], sizes[i], TextFace::Serif);
        width = reference_footage_round(width + advances[i]);
        if (mixed && (i == 0 || i == 3)) width = reference_footage_round(width + gap);
    }
    float x = reference_footage_round(bounds.x + reference_footage_round(
        reference_footage_round(bounds.width - width) / 2.0F));
    for (std::size_t i = 0; i < count; ++i) {
        const float baseline = reference_footage_round(bounds.y +
            reference_footage_round(baseline_offsets[i] * scale.sy));
        const float top = reference_footage_round(baseline - reference_footage_round(
            reference_footage_round(38.0F * sizes[i]) / 40.0F));
        drawing.text(runs[i], x, top, sizes[i], kUiIvory, TextFace::Serif);
        x = reference_footage_round(x + advances[i]);
        if (mixed && (i == 0 || i == 3)) x = reference_footage_round(x + gap);
    }
}

void reference_drawbar(Drawing& drawing, const UiControlGeometry& geometry,
                       std::uint8_t value, std::string_view label, UiColor cap,
                       ReferenceCompositionScale scale) {
    if (!material_surface(geometry.bounds) || !material_surface(geometry.track) || value > 8) return;
    const bool mixture = geometry.id.kind == UiControlKind::PedalDrawbar;
    const auto& track = geometry.track;
    const float center = track.x + track.width / 2.0F;
    const float cap_width = 34.0F * scale.sx;
    const float cap_height = (mixture ? 22.0F : 32.0F) * scale.sy;
    const float slot_width = 42.0F * scale.sx;
    const UiRect slot{center - slot_width / 2.0F, track.y - cap_height / 2.0F,
                      slot_width, track.height + cap_height};
    const float position = track.y + track.height * static_cast<float>(value) / 8.0F;
    const UiRect knob{center - cap_width / 2.0F, position - cap_height / 2.0F, cap_width, cap_height};
    // The rail/cap travel owns the material envelope. Footage now has its own
    // row below that envelope, so label-to-value arithmetic is not applicable.
    const UiRect material_strip{geometry.bounds.x, slot.y, geometry.bounds.width, slot.height};
    drawing.rounded(slot, 2.0F * scale.f, {5, 5, 5});
    drawing.gradient({slot.x + scale.sx, slot.y + scale.sy, 3.0F * scale.sx,
                      slot.height - 2.0F * scale.sy}, {47, 43, 36}, {22, 21, 18});
    drawing.gradient({slot.x + slot.width - 3.0F * scale.sx, slot.y + scale.sy,
                      2.0F * scale.sx, slot.height - 2.0F * scale.sy}, {27, 26, 23}, {13, 14, 12});
    drawing.gradient({slot.x + scale.sx, slot.y + scale.sy, slot.width - 2.0F * scale.sx,
                      std::min(6.0F * scale.sy, slot.height / 4.0F)}, {0, 0, 0, 135}, {0, 0, 0, 0});
    drawing.rect({slot.x, slot.y + scale.sy, scale.sx, slot.height - 2.0F * scale.sy}, {63, 58, 49});
    drawing.rect({slot.x + slot.width - scale.sx, slot.y, scale.sx, slot.height}, {36, 34, 30});
    for (int tick = 0; tick <= 8; ++tick) {
        const float y = track.y + track.height * static_cast<float>(tick) / 8.0F;
        drawing.rect({slot.x + scale.sx, y, 2.0F * scale.sx, scale.sy}, {103, 94, 72});
    }
    const float shaft_left = center - 4.5F * scale.sx;
    const float exposed_height = std::max(0.0F, knob.y - track.y);
    drawing.gradient({shaft_left, track.y, 9.0F * scale.sx, track.height}, {37, 36, 31}, {20, 22, 19});
    if (exposed_height > 0.0F) {
        drawing.gradient({shaft_left, track.y, 9.0F * scale.sx, exposed_height}, {70, 65, 54}, {43, 41, 34});
        drawing.rect({shaft_left, track.y, scale.sx, exposed_height}, {174, 158, 129, 170});
        drawing.rect({shaft_left + 8.0F * scale.sx, track.y, scale.sx, exposed_height}, {15, 16, 14});
    }
    const float left = std::max(knob.x - scale.sx, material_strip.x);
    const float top = std::max(knob.y + 3.0F * scale.sy, material_strip.y);
    const float right = std::min(knob.x + knob.width + 2.0F * scale.sx, material_strip.x + material_strip.width);
    const float bottom = std::min(knob.y + knob.height + 4.0F * scale.sy, material_strip.y + material_strip.height);
    drawing.rounded({left, top, right - left, bottom - top}, 3.0F * scale.f, {0, 0, 0, 210});
    drawing.rounded(knob, 3.0F * scale.f, shade(cap, -38));
    const bool ivory = cap.red == kIvoryCap.red && cap.green == kIvoryCap.green && cap.blue == kIvoryCap.blue;
    const float front = (mixture ? 6.0F : 8.0F) * scale.sy;
    const UiRect surface{knob.x + scale.sx, knob.y + 2.0F * scale.sy,
                         knob.width - 2.0F * scale.sx, knob.height - front - 3.0F * scale.sy};
    drawing.gradient(surface, ivory ? UiColor{250, 237, 207} : shade(cap, 29),
                     ivory ? UiColor{225, 204, 166} : shade(cap, -2));
    drawing.gradient({surface.x, surface.y, surface.width, std::min(4.0F * scale.sy, surface.height * 0.12F)},
                     ivory ? UiColor{255, 248, 225, 75} : UiColor{222, 197, 162, 40}, {255, 244, 219, 0});
    drawing.gradient({surface.x, surface.y + surface.height, surface.width, front},
                     ivory ? UiColor{205, 180, 139} : shade(cap, -13),
                     ivory ? UiColor{165, 135, 91} : shade(cap, -34));
    drawing.rect({surface.x, surface.y + scale.sy, scale.sx, surface.height - 2.0F * scale.sy},
                 ivory ? UiColor{255, 246, 219} : shade(cap, 48));
    drawing.rect({surface.x + surface.width - scale.sx, surface.y + scale.sy,
                  scale.sx, surface.height + front - 2.0F * scale.sy},
                 ivory ? UiColor{145, 118, 80} : shade(cap, -48));
    drawing.rect({surface.x + 2.0F * scale.sx, surface.y, surface.width - 4.0F * scale.sx, scale.sy},
                 ivory ? UiColor{255, 248, 224} : shade(cap, 65));
    drawing.rect({surface.x + scale.sx, surface.y + surface.height,
                  surface.width - 2.0F * scale.sx, scale.sy},
                 ivory ? UiColor{244, 224, 186} : shade(cap, 34));
    if (mixture) {
        centered(drawing, label, geometry.label_bounds, 11.0F * scale.f,
                 kUiIvory, TextFace::Sans, 2.0F * scale.sx);
    } else {
        reference_manual_footage(drawing, label, geometry.label_bounds, scale);
    }
    centered(drawing, std::to_string(value), geometry.value_bounds, (mixture ? 13.0F : 12.0F) * scale.f,
             kUiBrass, TextFace::Sans, 3.0F * scale.sx);
}

[[nodiscard]] UiQuad reference_inset_quad(const UiQuad& shape, float amount,
                                         ReferenceCompositionScale scale) noexcept {
    const float height = shape.points[3].y - shape.points[0].y;
    const float y = amount * scale.sy;
    if (!(height > 2.0F * y)) return {};
    return quad_band(shape, y / height, 1.0F - y / height, amount * scale.sx);
}

void reference_quad_outline(Drawing& drawing, const UiQuad& shape, UiColor color,
                            float thickness, ReferenceCompositionScale scale) {
    if (!shape.contains(shape.points[0])) return;
    const auto& points = shape.points;
    const float height = points[3].y - points[0].y;
    const float x = std::min(thickness * scale.sx,
        std::min(points[1].x - points[0].x, points[2].x - points[3].x) / 2.0F);
    const float y = std::min(thickness * scale.sy, height / 2.0F);
    drawing.quad(quad_band(shape, 0.0F, y / height), color, color);
    drawing.quad(quad_band(shape, 1.0F - y / height, 1.0F), color, color);
    if (2.0F * y >= height) return;
    const auto middle = quad_band(shape, y / height, 1.0F - y / height);
    const auto& p = middle.points;
    drawing.quad(UiQuad{{p[0], UiPoint{p[0].x + x, p[0].y}, UiPoint{p[3].x + x, p[3].y}, p[3]}}, color, color);
    drawing.quad(UiQuad{{UiPoint{p[1].x - x, p[1].y}, p[1], p[2], UiPoint{p[2].x - x, p[2].y}}}, color, color);
}

[[nodiscard]] UiQuad reference_idle_key_side(const UiQuad& shape, bool left,
                                            ReferenceCompositionScale scale) noexcept {
    const auto& points = shape.points;
    const float height = points[3].y - points[0].y;
    if (!(height > 0.0F)) return {};
    const std::size_t top = left ? 0U : 1U;
    const std::size_t bottom = left ? 3U : 2U;
    // Measure the normal in canonical space before applying the x metric.
    const float offset = std::hypot(1.0F,
        (points[bottom].x - points[top].x) / scale.sx / (height / scale.sy)) * scale.sx;
    const auto edge = [&](std::size_t first, std::size_t last, float fraction) {
        return points[first].x + (points[last].x - points[first].x) * fraction;
    };
    constexpr float start = 0.08F;
    constexpr float finish = 0.88F;
    if (edge(1, 2, start) - edge(0, 3, start) <= 3.0F * offset ||
        edge(1, 2, finish) - edge(0, 3, finish) <= 3.0F * offset) return {};
    const auto point = [&](float fraction, float distance) {
        return UiPoint{edge(top, bottom, fraction) + (left ? distance : -distance) * offset,
                       points[0].y + height * fraction};
    };
    return left ? UiQuad{{point(start, 1.0F), point(start, 2.0F), point(finish, 2.0F), point(finish, 1.0F)}} :
                  UiQuad{{point(start, 2.0F), point(start, 1.0F), point(finish, 1.0F), point(finish, 2.0F)}};
}

void reference_key(Drawing& drawing, const UiKeyGeometry& key, bool held, bool focused,
                   bool manual, ReferenceCompositionScale scale) {
    if (!material_surface(key.bounds)) return;
    if (key.accidental) {
        drawing.quad(key.top, held ? UiColor{150, 124, 77} : UiColor{40, 39, 35},
                     held ? UiColor{96, 77, 43} : UiColor{10, 12, 10});
        drawing.quad(reference_inset_quad(key.top, 1.4F, scale),
                     held ? UiColor{166, 138, 88} : UiColor{61, 58, 52},
                     held ? UiColor{104, 84, 48} : UiColor{20, 22, 19});
        drawing.quad(key.front, held ? UiColor{95, 75, 40} : UiColor{41, 39, 32},
                     held ? UiColor{55, 42, 24} : UiColor{9, 11, 9});
        reference_quad_outline(drawing, key.hit, {5, 6, 5}, 0.8F, scale);
        reference_quad_outline(drawing, reference_inset_quad(key.top, 1.2F, scale),
            held ? UiColor{185, 151, 92, 170} : UiColor{127, 115, 91, 130}, 0.65F, scale);
        drawing.quad(quad_band(key.front, 0.0F, 0.12F, scale.sx), {155, 139, 106, 145}, {155, 139, 106, 70});
    } else {
        drawing.quad(key.top, held ? UiColor{209, 181, 122} : UiColor{226, 211, 181},
                     held ? UiColor{244, 213, 149} : UiColor{255, 244, 220});
        drawing.quad(key.front, held ? UiColor{190, 157, 96} : UiColor{198, 168, 124},
                     held ? UiColor{145, 115, 62} : UiColor{131, 96, 62});
        reference_quad_outline(drawing, key.hit, {83, 65, 42}, 0.7F, scale);
        const float front_depth = key.front.points[3].y - key.front.points[0].y;
        const float highlight = front_depth > 0.0F ? std::min(0.13F, 2.0F * scale.sy / front_depth) : 0.0F;
        drawing.quad(quad_band(key.front, 0.0F, highlight, 0.9F * scale.sx),
                     {255, 245, 217, 220}, {255, 245, 217, 60});
        const float top_depth = key.top.points[3].y - key.top.points[0].y;
        const float recess = top_depth > 0.0F ? std::min(0.12F, 18.0F * scale.sy / top_depth) : 0.0F;
        const bool refined = manual && !held;
        drawing.quad(quad_band(key.top, 0.0F, recess, 0.8F * scale.sx),
                     {20, 17, 13, static_cast<std::uint8_t>(refined ? 70 : 90)}, {20, 17, 13, 0});
        if (refined) {
            drawing.quad(reference_idle_key_side(key.top, true, scale), {255, 245, 219, 75}, {255, 245, 219, 28});
            drawing.quad(reference_idle_key_side(key.top, false, scale), {36, 26, 17, 40}, {36, 26, 17, 16});
        }
    }
    if (held) drawing.quad(quad_band(key.top, 0.91F, 0.96F, 2.0F * scale.sx), kUiBrass, kUiBrass);
    if (focused) reference_quad_outline(drawing, reference_inset_quad(key.hit, 2.0F, scale),
                                        kUiFocusCyan, 2.0F, scale);
}

[[nodiscard]] UiRect reference_preset_indicator(const UiControlGeometry& geometry,
                                               float amount, ReferenceCompositionScale scale) noexcept {
    if (preset_accidental(geometry.id.index)) return reference_inset(geometry.bounds, amount, scale);
    const auto& bounds = geometry.bounds;
    return reference_inset({bounds.x, bounds.y + bounds.height * 0.62F,
                            bounds.width, bounds.height * 0.38F}, amount, scale);
}

void reference_preset_label(Drawing& drawing, const UiControlGeometry& geometry,
                            ReferenceCompositionScale scale) {
    const auto label = preset_selection_label(static_cast<PresetSelection>(geometry.id.index));
    const auto& bounds = geometry.label_bounds;
    if (preset_accidental(geometry.id.index)) {
        centered(drawing, label.substr(0, 1), {bounds.x, bounds.y, bounds.width, 11.0F * scale.sy},
                 9.0F * scale.f, {37, 29, 20}, TextFace::Sans, 0.0F);
        centered(drawing, label.substr(1), {bounds.x, bounds.y + 9.0F * scale.sy, bounds.width, 11.0F * scale.sy},
                 9.0F * scale.f, {37, 29, 20}, TextFace::Sans, 0.0F);
    } else {
        centered(drawing, label, bounds, 9.0F * scale.f, kUiIvory, TextFace::Sans, 0.0F);
    }
}

void reference_preset_key(Drawing& drawing, const UiControlGeometry& geometry,
                          bool selected, ReferenceCompositionScale scale) {
    const auto& bounds = geometry.bounds;
    const bool ivory = preset_accidental(geometry.id.index);
    selected = selected && geometry.id.index != 0;
    const float recess = selected ? 2.0F * scale.sy : 0.0F;
    const float front = std::clamp(bounds.height / scale.sy * 0.16F, 6.0F, 12.0F) * scale.sy;
    drawing.rect(bounds, {5, 5, 5});
    const UiRect surface{bounds.x + scale.sx, bounds.y + recess,
                         bounds.width - 2.0F * scale.sx, bounds.height - front - recess};
    drawing.gradient(surface, ivory ? UiColor{254, 238, 204} : UiColor{49, 46, 41},
                     ivory ? UiColor{225, 204, 168} : UiColor{20, 20, 19});
    drawing.rect({surface.x, surface.y + scale.sy, scale.sx, surface.height - 2.0F * scale.sy},
                 ivory ? UiColor{255, 247, 222} : UiColor{101, 92, 75});
    drawing.rect({bounds.x + bounds.width - 2.0F * scale.sx, surface.y + scale.sy,
                  scale.sx, bounds.height - recess - 3.0F * scale.sy},
                 ivory ? UiColor{155, 130, 93} : UiColor{9, 9, 9});
    drawing.gradient({surface.x, bounds.y + bounds.height - front, surface.width, front - scale.sy},
                     ivory ? UiColor{209, 183, 141} : UiColor{39, 36, 31},
                     ivory ? UiColor{148, 119, 78} : UiColor{12, 12, 11});
    drawing.rect({surface.x, bounds.y + bounds.height - front, surface.width, scale.sy},
                 ivory ? UiColor{251, 230, 191} : UiColor{79, 69, 52});
    drawing.gradient({surface.x, surface.y, surface.width, 4.0F * scale.sy}, {0, 0, 0, 105}, {0, 0, 0, 0});
    if (selected) drawing.rect({surface.x + scale.sx, surface.y + 3.0F * scale.sy,
                               std::max(scale.sx, surface.width - 2.0F * scale.sx), 2.0F * scale.sy}, kUiBrass);
    reference_preset_label(drawing, geometry, scale);
}

void reference_preset_focus(Drawing& drawing, const UiControlGeometry& geometry,
                            ReferenceCompositionScale scale) {
    const auto bounds = reference_preset_indicator(geometry, 2.0F, scale);
    if (!preset_accidental(geometry.id.index)) {
        const auto open_frame = [&](UiRect frame, float stroke, UiColor color) {
            drawing.rect({frame.x, frame.y, frame.width, stroke * scale.sy}, color);
            drawing.rect({frame.x, frame.y, stroke * scale.sx, frame.height}, color);
            drawing.rect({frame.x + frame.width - stroke * scale.sx, frame.y,
                          stroke * scale.sx, frame.height}, color);
        };
        open_frame(bounds, 3.0F, {5, 6, 6});
        open_frame(reference_inset(bounds, 1.0F, scale), 1.0F, kUiFocusCyan);
        return;
    }
    const auto paint = [&] {
        reference_outline(drawing, bounds, {5, 6, 6}, 3.0F, scale);
        reference_outline(drawing, reference_inset(bounds, 1.0F, scale), kUiFocusCyan, 1.0F, scale);
    };
    // Preserve the original glyph pixels, and intersect the opening with the
    // caller's physical clip before restoring its exact logical/physical state.
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
    SDL_RenderSetScale(renderer, 1.0F, 1.0F);
    SDL_Rect previous_physical{};
    SDL_RenderGetClipRect(renderer, &previous_physical);
    SDL_RenderSetScale(renderer, scale_x, scale_y);
    SDL_RenderSetClipRect(renderer, &focus_clip);
    SDL_RenderSetScale(renderer, 1.0F, 1.0F);
    SDL_RenderGetClipRect(renderer, &focus_clip);
    const bool visible = !clipped || SDL_IntersectRect(&focus_clip, &previous_physical, &focus_clip) == SDL_TRUE;
    SDL_RenderSetClipRect(renderer, &focus_clip);
    SDL_RenderSetScale(renderer, scale_x, scale_y);
    if (visible) paint();
    SDL_RenderSetClipRect(renderer, clipped ? &previous : nullptr);
    SDL_RenderSetScale(renderer, 1.0F, 1.0F);
    SDL_Rect restored{};
    SDL_RenderGetClipRect(renderer, &restored);
    if (clipped && SDL_RectEquals(&restored, &previous_physical) == SDL_FALSE)
        SDL_RenderSetClipRect(renderer, &previous_physical);
    SDL_RenderSetScale(renderer, scale_x, scale_y);
}

void reference_presets(Drawing& drawing, const UiModel& model, ReferenceCompositionScale scale) {
    const auto& view = model.view();
    const auto& layout = model.layout();
    std::array<PresetSelection, kManualCount> applied{};
    std::array<bool, kManualCount> valid{};
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        valid[manual] = control_preset_selection(view.applied.controls, static_cast<Manual>(manual), applied[manual]);
        const auto& bounds = layout.preset_key_panels[manual];
        drawing.rect({bounds.x - scale.sx, bounds.y - 3.0F * scale.sy,
                      bounds.width + 2.0F * scale.sx, bounds.height + 4.0F * scale.sy}, {4, 4, 4});
    }
    for (const bool accidental : {false, true}) {
        for (std::size_t index = 0; index < layout.control_count; ++index) {
            const auto& geometry = layout.controls[index];
            if (!ui_control_visible(layout, geometry.id) || geometry.id.kind != UiControlKind::PresetKey ||
                preset_accidental(geometry.id.index) != accidental) continue;
            const auto manual = manual_index(geometry.id.manual);
            const bool selected = valid[manual] && applied[manual] != PresetSelection::Cancel &&
                static_cast<std::uint8_t>(applied[manual]) == geometry.id.index;
            reference_preset_key(drawing, geometry, selected, scale);
        }
    }
    for (std::size_t index = 0; index < layout.control_count; ++index) {
        const auto& geometry = layout.controls[index];
        if (!ui_control_visible(layout, geometry.id) || geometry.id.kind != UiControlKind::PresetKey) continue;
        PresetSelection desired{};
        if (pending_preset(view, geometry.id.manual, desired) && static_cast<std::uint8_t>(desired) == geometry.id.index)
            reference_outline(drawing, reference_preset_indicator(geometry, 1.0F, scale), kPresetPending, 1.0F, scale);
    }
    for (std::size_t index = 0; index < layout.control_count; ++index) {
        const auto& geometry = layout.controls[index];
        if (ui_control_visible(layout, geometry.id) && geometry.id.kind == UiControlKind::PresetKey && geometry.id == view.focus)
            reference_preset_focus(drawing, geometry, scale);
    }
}

void reference_controls(Drawing& drawing, const UiModel& model, ReferenceCompositionScale scale) {
    const auto& view = model.view();
    const auto& layout = model.layout();
    const std::array<UiColor, 9> caps{kBrownCap, kBrownCap, kIvoryCap, kIvoryCap, kBlackCap,
                                     kIvoryCap, kBlackCap, kBlackCap, kIvoryCap};
    for (std::size_t index = 0; index < layout.control_count; ++index) {
        const auto& geometry = layout.controls[index];
        const auto& id = geometry.id;
        if (!ui_control_visible(layout, id) || id.kind == UiControlKind::PresetKey ||
            id.kind == UiControlKind::SoundingBank || id.kind == UiControlKind::CancelManual) continue;
        const auto manual = manual_index(id.manual);
        bool selected = false;
        if (id.kind == UiControlKind::ManualDrawbar) {
            reference_drawbar(drawing, geometry, view.controls.drawbars[manual][static_cast<std::size_t>(id.bank)][id.index],
                              kUiFootageLabels[id.index], caps[id.index], scale);
        } else if (id.kind == UiControlKind::PedalDrawbar) {
            reference_drawbar(drawing, geometry, view.controls.pedal_drawbars[id.index],
                              id.index == 0 ? "MIX 1" : "MIX 2", kBrownCap, scale);
        } else if (id.kind == UiControlKind::Expression) {
            centered(drawing, "NOMINAL EXPRESSION", geometry.label_bounds, 10.5F * scale.f,
                     kUiIvory, TextFace::Sans, 3.0F * scale.sx);
            const auto& track = geometry.track;
            drawing.rounded({track.x - 3.0F * scale.sx, track.y - 5.0F * scale.sy,
                             track.width + 6.0F * scale.sx, 10.0F * scale.sy}, 3.0F * scale.f, {8, 9, 8});
            drawing.rect({track.x, track.y + 3.0F * scale.sy, track.width, scale.sy}, kMetalEdge);
            const float x = track.x + static_cast<float>(view.controls.expression) * track.width;
            drawing.rect({track.x, track.y - scale.sy, x - track.x, 2.0F * scale.sy}, kUiBrass);
            drawing.rounded({x - 7.0F * scale.sx, track.y - 11.0F * scale.sy,
                             14.0F * scale.sx, 22.0F * scale.sy}, 3.0F * scale.f, {30, 26, 18});
            drawing.gradient({x - 5.0F * scale.sx, track.y - 9.0F * scale.sy,
                              10.0F * scale.sx, 17.0F * scale.sy}, {220, 193, 140}, {122, 97, 55});
            drawing.rect({x - 3.0F * scale.sx, track.y - 7.0F * scale.sy,
                          6.0F * scale.sx, scale.sy}, kUiIvory);
            centered(drawing, std::to_string(static_cast<int>(std::round(view.controls.expression * 100.0))) + "%",
                     geometry.value_bounds, 11.5F * scale.f, kUiBrass, TextFace::Sans, 3.0F * scale.sx);
        } else if (id.kind == UiControlKind::Percussion) {
            const auto& settings = view.controls.percussion;
            constexpr std::array<std::string_view, 4> titles{"PERC", "HARM", "VOL", "DECAY"};
            std::string_view value;
            switch (id.index) {
            case 0: value = settings.enabled ? "ON" : "OFF"; selected = settings.enabled; break;
            case 1: value = settings.harmonic == PercussionHarmonic::Second ? "2ND" : "3RD"; break;
            case 2: value = settings.volume == PercussionVolume::Normal ? "NORM" : "SOFT"; break;
            default: value = settings.decay == PercussionDecay::Slow ? "SLOW" : "FAST"; break;
            }
            reference_button(drawing, geometry, {}, 20.0F, scale, selected, false, TextFace::Serif, true);
            centered(drawing, titles[id.index], geometry.label_bounds, 13.5F * scale.f,
                     kUiIvory, TextFace::Serif, 3.0F * scale.sx);
            centered(drawing, value, geometry.value_bounds, 20.0F * scale.f,
                     {33, 28, 21}, TextFace::Serif, 3.0F * scale.sx);
        } else {
            if (id.kind == UiControlKind::EditBank) selected = view.edited_banks[manual] == id.bank;
            if (id.kind == UiControlKind::KeyboardTarget) selected = static_cast<std::uint8_t>(view.keyboard_target) == id.index;
            if (id.kind == UiControlKind::Workspace) selected = static_cast<std::uint8_t>(view.workspace) == id.index;
            const bool header = header_button(id.kind);
            const float size = id.kind == UiControlKind::Workspace ? 18.0F : header ? 11.5F : 12.0F;
            reference_button(drawing, geometry, button_label(id), size, scale, selected,
                              id.kind == UiControlKind::Panic, header ? TextFace::Serif : TextFace::Sans);
        }
        if (view.focus == id) reference_outline(drawing, geometry.bounds, kUiFocusCyan, 2.0F, scale);
    }
    reference_presets(drawing, model, scale);
}

void reference_header(Drawing& drawing, const UiLayout& layout, ReferenceCompositionScale scale) {
    reference_panel(drawing, layout.header, scale, false);
    float title_left = layout.header.x;
    float title_right = layout.header.x + layout.header.width;
    float flat_left = title_right;
    for (std::size_t index = 0; index < layout.control_count; ++index) {
        const auto& control = layout.controls[index];
        if (!ui_control_visible(layout, control.id)) continue;
        if (control.id.kind == UiControlKind::Workspace && control.id.index == 2)
            title_left = control.bounds.x + control.bounds.width + 12.0F * scale.sx;
        if (control.id.kind == UiControlKind::SaveControls) title_right = control.bounds.x - 12.0F * scale.sx;
        if (control.id.kind == UiControlKind::Presentation) flat_left = control.bounds.x;
    }
    const float middle = 836.0F * scale.sx;
    const float half_width = std::max(0.0F, std::min(middle - title_left, title_right - middle));
    title_left = middle - half_width;
    title_right = middle + half_width;
    constexpr std::string_view title = "TONEWHEEL ATLAS";
    float size = 42.75F * scale.f;
    const float natural_width = drawing.text_width(title, size, TextFace::Serif);
    if (natural_width > title_right - title_left) size *= (title_right - title_left) / natural_width;
    const float width = drawing.text_width(title, size, TextFace::Serif);
    const float x = std::clamp(middle - width / 2.0F, title_left, std::max(title_left, title_right - width));
    const float y = 11.5F * scale.sy;
    drawing.text(title, x + scale.sx, y + 2.0F * scale.sy, size, {4, 5, 4, 255}, TextFace::Serif);
    drawing.text(title, x + scale.f, y + scale.f, size, {100, 65, 28, 255}, TextFace::Serif);
    drawing.text(title, x, y - 0.125F * scale.f, size, {255, 231, 184, 255}, TextFace::Serif);
    drawing.text(title, x + scale.f, y, size, {212, 171, 103, 255}, TextFace::Serif);
    drawing.text(title, x, y, size, {226, 192, 135, 255}, TextFace::Serif);
    drawing.rect(reference_composition_rect({528.0F, 40.0F, 50.0F, 1.0F}, scale), kMetalEdge);
    drawing.rect(reference_composition_rect({1094.0F, 40.0F, 108.0F, 1.0F}, scale), kMetalEdge);
    constexpr std::string_view caption = "NOMINAL DRY ORGAN";
    constexpr float gaps = static_cast<float>(caption.size() - 1);
    const float caption_half_width = std::max(0.0F, std::min(middle - title_left,
        std::min(title_right, flat_left - 10.0F * scale.sx) - middle));
    const float caption_width = std::min(374.0F * scale.sx, 2.0F * caption_half_width);
    float caption_size = 17.0F * scale.f;
    float natural_caption_width = drawing.text_width(caption, caption_size);
    const float tracking = std::max(0.0F, (caption_width - natural_caption_width) / gaps);
    if (natural_caption_width > caption_width) {
        caption_size *= caption_width / natural_caption_width;
        natural_caption_width = drawing.text_width(caption, caption_size);
    }
    float cursor = middle - (natural_caption_width + gaps * tracking) / 2.0F;
    for (std::size_t index = 0; index < caption.size(); ++index) {
        const auto glyph = caption.substr(index, 1);
        drawing.text(glyph, cursor, 67.5F * scale.sy, caption_size, kUiBrass);
        cursor += drawing.text_width(glyph, caption_size) + tracking;
    }
}

void reference_cabinet(Drawing& drawing, const UiLayout& layout,
                       const InstrumentViewInfo& info, ReferenceCompositionScale scale) {
    reference_panel(drawing, layout.cabinet_panel, scale);
    reference_heading(drawing, "ROTARY CABINET",
        reference_composition_rect({1143.0F, 131.0F, 444.0F, 31.0F}, scale), 16.0F, scale);
    const auto& art = layout.cabinet_art;
    drawing.rect({art.x - 3.0F * scale.sx, art.y - 3.0F * scale.sy,
                  art.width + 6.0F * scale.sx, art.height + 6.0F * scale.sy}, {8, 9, 8});
    if (!drawing.reference_art(ReferenceArt::Cabinet, art)) {
        drawing.gradient(art, {34, 25, 18}, {12, 13, 11});
        const float art_scale = art.width / 466.0F;
        const UiRect box{art.x + art.width * 0.2F, art.y + art.height * 0.13F,
                         art.width * 0.6F, art.height * 0.73F};
        reference_wood(drawing, box, {art_scale, art_scale, art_scale});
        for (int slot = 0; slot < 5; ++slot)
            drawing.rect({box.x + box.width * 0.08F,
                          box.y + (12.0F + static_cast<float>(slot) * 10.0F) * art_scale,
                          box.width * 0.84F, 4.0F * art_scale}, {14, 10, 7});
        centered(drawing, "DECORATIVE ART UNAVAILABLE",
                 {art.x + 8.0F * art_scale, art.y + art.height - 28.0F * art_scale,
                  art.width - 16.0F * art_scale, 20.0F * art_scale},
                 10.0F * scale.f, kMuted, TextFace::Sans, 3.0F * scale.sx);
    }
    drawing.rect({art.x - 2.0F * scale.sx, art.y - 3.0F * scale.sy,
                  art.width + 4.0F * scale.sx, scale.sy}, {132, 112, 82, 170});
    drawing.rect({art.x - 3.0F * scale.sx, art.y - 2.0F * scale.sy,
                  scale.sx, art.height + 4.0F * scale.sy}, {95, 81, 61, 130});
    centered(drawing, "ROTARY AUDIO NOT CONNECTED",
             reference_composition_rect({1144.0F, 584.0F, 442.0F, 17.0F}, scale),
             12.0F * scale.f, kMuted, TextFace::Sans, 3.0F * scale.sx);
    drawing.rect(reference_composition_rect({1144.0F, 691.0F, 442.0F, 54.0F}, scale), {19, 21, 18});
    const std::string audio = std::string(info.audio_running ? "AUDIO RUNNING / " : "AUDIO STOPPED / ") + audio_configuration(info);
    text_line(drawing, audio, reference_composition_rect({1144.0F, 692.0F, 442.0F, 15.0F}, scale),
              12.0F * scale.f, info.audio_running ? kGreen : kRed);
    text_line(drawing, midi_state(info), reference_composition_rect({1144.0F, 710.0F, 442.0F, 15.0F}, scale),
              12.0F * scale.f, info.midi_open ? kGreen : kMuted);
    text_line(drawing, "SCANNER / CHORUS: NOT CONNECTED",
              reference_composition_rect({1144.0F, 728.0F, 442.0F, 15.0F}, scale), 12.0F * scale.f, kMuted);
}

void reference_footer(Drawing& drawing, const UiModel& model, const InstrumentViewInfo& info,
                      ReferenceCompositionScale scale) {
    const auto& footer = model.layout().footer;
    const auto& view = model.view();
    drawing.gradient(footer, {27, 26, 24}, {16, 16, 16});
    drawing.rect({footer.x, footer.y, footer.width, scale.sy}, kMetalEdge);
    drawing.rounded({footer.x + 6.0F * scale.sx, footer.y + 8.0F * scale.sy,
                     6.0F * scale.sx, 6.0F * scale.sy}, 3.0F * scale.f, info.audio_running ? kGreen : kRed);
    std::string audio = info.audio_running ? "AUDIO RUNNING" : "AUDIO STOPPED";
    if (info.sample_rate != 0) audio += "  " + audio_configuration(info);
    audio += "  /  " + midi_state(info);
    const float meter_width = 84.0F * scale.sx;
    const float meter_x = footer.x + footer.width - meter_width - 12.0F * scale.sx;
    text_line(drawing, audio, {footer.x + 20.0F * scale.sx, footer.y + 4.0F * scale.sy,
              footer.width - 220.0F * scale.sx, 15.0F * scale.sy}, 10.0F * scale.f, kUiIvory);
    if (view.controls_dirty)
        drawing.text("UNSAVED", meter_x - 67.0F * scale.sx, footer.y + 4.0F * scale.sy, 9.0F * scale.f, kUiBrass);
    drawing.rect({meter_x, footer.y + 7.0F * scale.sy, meter_width, 5.0F * scale.sy}, {49, 50, 42});
    drawing.rect({meter_x, footer.y + 7.0F * scale.sy,
                  meter_width * std::clamp(view.applied.peak, 0.0F, 1.0F), 5.0F * scale.sy},
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
    text_line(drawing, status, {footer.x + 20.0F * scale.sx, footer.y + 21.0F * scale.sy,
              footer.width - 32.0F * scale.sx, 14.0F * scale.sy},
              10.5F * scale.f, preset_request ? kPresetPending : kMuted);
}

void paint_reference_composition(Drawing& drawing, const UiModel& model, const InstrumentViewInfo& info) {
    const auto& layout = model.layout();
    const auto& view = model.view();
    const auto scale = reference_composition_scale(layout);
    const auto mapped = [scale](UiRect bounds) { return reference_composition_rect(bounds, scale); };
    drawing.clear(kUiWalnut);
    reference_wood(drawing, {0.0F, 0.0F, layout.width, layout.height}, scale);
    const float margin = layout.header.x;
    (void)drawing.reference_art(ReferenceArt::LeftWoodCheek, {0.0F, 0.0F, margin, layout.height});
    (void)drawing.reference_art(ReferenceArt::RightWoodCheek,
        {layout.width - margin, 0.0F, margin, layout.height});
    drawing.rounded(mapped({65.0F, 8.0F, 1542.0F, 917.0F}), 9.0F * scale.f, {10, 11, 9});
    drawing.rect(mapped({68.0F, 17.0F, 1.0F, 901.0F}), {143, 89, 48, 160});
    drawing.rect(mapped({1603.0F, 17.0F, 1.0F, 901.0F}), {143, 89, 48, 160});
    if (!drawing.apron_art(mapped({16.0F, 887.0F, 1640.0F, 54.0F})))
        reference_wood(drawing, mapped({16.0F, 887.0F, 1640.0F, 54.0F}), scale);
    reference_wood(drawing, mapped({48.0F, 510.0F, 1074.0F, 18.0F}), scale);
    reference_header(drawing, layout, scale);
    reference_panel(drawing, layout.performance_panel, scale);
    reference_panel(drawing, layout.registration_panels[0], scale, true, ReferencePanelMaterial::UpperRack);
    for (std::size_t manual = 1; manual < layout.registration_panels.size(); ++manual)
        reference_panel(drawing, layout.registration_panels[manual], scale, true,
                        manual == 1 ? ReferencePanelMaterial::LowerRack : ReferencePanelMaterial::Original);
    // The cabinet is a parent of the moved toolbar and pedals. Finish its art
    // and truth rows now, before painting any nested live surfaces or focus.
    reference_cabinet(drawing, layout, info, scale);
    drawing.rect(mapped({556.0F, 137.0F, 1.0F, 115.0F}), kMetalEdge);
    reference_heading(drawing, "PERCUSSION", mapped({90.0F, 136.0F, 448.0F, 26.0F}), 15.0F, scale);
    reference_heading(drawing, "NOMINAL EXPRESSION / PEDAL MIXTURES",
                      mapped({578.0F, 136.0F, 514.0F, 26.0F}), 14.0F, scale);
    const bool eligible = view.applied.controls.route_enabled[0] &&
        view.applied.controls.fixed_registrations[0] == FixedRegistration::None &&
        view.applied.controls.selected_banks[0] == DrawbarBank::B;
    centered(drawing, eligible ? "UPPER B ROUTE ACTIVE" : "REQUIRES UPPER B",
             mapped({90.0F, 248.0F, 448.0F, 14.0F}), 12.0F * scale.f,
             eligible ? kGreen : kMuted, TextFace::Sans, 3.0F * scale.sx);
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        const auto& rack = layout.registration_panels[manual];
        reference_rack_heading(drawing,
            {rack.x + 16.0F * scale.sx, rack.y + 8.0F * scale.sy,
             rack.width - 32.0F * scale.sx, 27.0F * scale.sy}, manual == 0, scale);
        // Numbered guide follows the same stored track endpoints as the caps.
        for (std::size_t index = 0; index < layout.control_count; ++index) {
            const auto& control = layout.controls[index];
            if (control.id.kind != UiControlKind::ManualDrawbar ||
                manual_index(control.id.manual) != manual || control.id.index != 0) continue;
            const float left = (manual == 0 ? 110.0F : 638.0F) * scale.sx;
            for (int tick = 0; tick <= 8; ++tick) {
                const float y = control.track.y + control.track.height * static_cast<float>(tick) / 8.0F;
                centered(drawing, std::to_string(tick), {left, y - 7.0F * scale.sy, 15.0F * scale.sx, 14.0F * scale.sy},
                         12.0F * scale.f, kUiIvory, TextFace::Sans, 0.0F);
                drawing.rect({left + 17.0F * scale.sx, y,
                              control.bounds.x - left - 20.0F * scale.sx, scale.sy}, kMetalEdge);
            }
            break;
        }
        const auto& cheek = layout.manual_rail_panels[manual];
        reference_wood(drawing, cheek, scale);
        drawing.rect(reference_inset(cheek, 5.0F, scale), {19, 18, 17});
        drawing.rect({cheek.x + 6.0F * scale.sx, cheek.y + 5.0F * scale.sy,
                      cheek.width - 12.0F * scale.sx, scale.sy}, {112, 87, 59});
        centered(drawing, manual == 0 ? "UPPER / SWELL" : "LOWER / GREAT",
                 {cheek.x + 8.0F * scale.sx, cheek.y + 3.0F * scale.sy,
                  cheek.width - 16.0F * scale.sx, 17.0F * scale.sy},
                 13.0F * scale.f, kUiBrass, TextFace::Serif, 3.0F * scale.sx);
        const UiColor state_color = view.applied.controls.route_enabled[manual] ? kUiBrass : kMuted;
        centered(drawing, view.edited_banks[manual] == DrawbarBank::A ? "EDIT BANK A" : "EDIT BANK B",
                 {cheek.x + 8.0F * scale.sx, cheek.y + 20.0F * scale.sy,
                  cheek.width - 16.0F * scale.sx, 14.0F * scale.sy},
                 12.0F * scale.f, state_color, TextFace::Sans, 3.0F * scale.sx);
        centered(drawing, sounding_caption(view, static_cast<Manual>(manual)),
                 {cheek.x + 8.0F * scale.sx, cheek.y + 34.0F * scale.sy,
                  cheek.width - 16.0F * scale.sx, 14.0F * scale.sy},
                 12.0F * scale.f, state_color, TextFace::Sans, 3.0F * scale.sx);
    }
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        const auto& bounds = layout.manual_panels[manual];
        reference_panel(drawing, bounds, scale, false);
        drawing.rect({bounds.x + 6.0F * scale.sx, bounds.y + 20.0F * scale.sy,
                      bounds.width - 12.0F * scale.sx, bounds.height - 26.0F * scale.sy}, {7, 9, 8});
        centered(drawing, manual == 0 ? "UPPER MANUAL" : "LOWER MANUAL",
                 {bounds.x + 12.0F * scale.sx, bounds.y + 3.0F * scale.sy,
                  bounds.width - 24.0F * scale.sx, 16.0F * scale.sy},
                 10.5F * scale.f, kUiBrass, TextFace::Sans, 3.0F * scale.sx);
        for (const bool accidental : {false, true}) {
            for (std::size_t index = 0; index < kManualKeyCount; ++index) {
                const auto& key = layout.manual_keys[manual][index];
                if (key.accidental != accidental) continue;
                const bool focused = view.focus.kind == UiControlKind::ManualKey &&
                    manual_index(view.focus.manual) == manual && view.focus.index == index;
                reference_key(drawing, key, view.applied.held_keys[manual][index], focused, true, scale);
            }
        }
    }
    drawing.gradient(layout.keyboard_toolbar, {27, 26, 25}, {16, 16, 16});
    const std::string octave = view.keyboard_target == UiTarget::Pedals ?
        "COMPUTER KEYS / PEDAL OCTAVE " + std::to_string(view.pedal_octave) :
        "COMPUTER KEYS / BASE C" + std::to_string(static_cast<int>(view.manual_base_midi) / 12 - 1);
    text_line(drawing, octave, mapped({1340.0F, 654.0F, 240.0F, 14.0F}), 12.0F * scale.f, kMuted);
    reference_panel(drawing, layout.pedal_panel, scale, false);
    centered(drawing, "PEDALBOARD / 25 NOTES", mapped({1150.0F, 755.0F, 426.0F, 16.0F}),
             12.0F * scale.f, kUiBrass, TextFace::Sans, 3.0F * scale.sx);
    for (const bool accidental : {false, true}) {
        for (std::size_t index = 0; index < kPedalCount; ++index) {
            const auto& key = layout.pedal_keys[index];
            if (key.accidental != accidental) continue;
            reference_key(drawing, key, view.applied.held_pedals[index],
                view.focus.kind == UiControlKind::PedalKey && view.focus.index == index, false, scale);
        }
    }
    reference_controls(drawing, model, scale);
    reference_footer(drawing, model, info, scale);
    overlay(drawing, layout, info);
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
    const UiRect panel_rect{(width - 740.0F) / 2.0F, (height - 600.0F) / 2.0F, 740.0F, 600.0F};
    return {panel_rect,
            {panel_rect.x + 28.0F, panel_rect.y + 113.0F, 40.0F, 42.0F},
            {panel_rect.x + 672.0F, panel_rect.y + 113.0F, 40.0F, 42.0F},
            {panel_rect.x + 28.0F, panel_rect.y + 239.0F, 212.0F, 38.0F},
            {panel_rect.x + 264.0F, panel_rect.y + 239.0F, 212.0F, 38.0F},
            {panel_rect.x + 500.0F, panel_rect.y + 239.0F, 212.0F, 38.0F},
            {panel_rect.x + 28.0F, panel_rect.y + 332.0F, 212.0F, 38.0F},
            {panel_rect.x + 264.0F, panel_rect.y + 332.0F, 212.0F, 38.0F},
            {panel_rect.x + 500.0F, panel_rect.y + 332.0F, 212.0F, 38.0F},
            {panel_rect.x + 28.0F, panel_rect.y + 510.0F, 252.0F, 38.0F},
            {panel_rect.x + 296.0F, panel_rect.y + 510.0F, 188.0F, 38.0F},
            {panel_rect.x + 628.0F, panel_rect.y + 24.0F, 84.0F, 32.0F}};
}

void paint_instrument(Drawing& drawing, const UiModel& model, const InstrumentViewInfo& info) {
    const auto& layout = model.layout();
    if (reference_composition_active(layout)) {
        paint_reference_composition(drawing, model, info);
        return;
    }
    const auto& view = model.view();
    const bool flat = view.presentation == UiPresentation::Flat;
    const bool wide_legibility = layout.sidebar_pedals && !flat;
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
    const bool reference_percussion = layout.workspace == UiWorkspace::Play &&
        layout.sidebar_pedals && layout.presentation == UiPresentation::Dimensional;
    const bool separate_eligibility = performance.height >= (reference_percussion ? 104.0F : 92.0F);
    heading(drawing, separate_eligibility ? "PERCUSSION" : eligible ? "PERCUSSION / UPPER B ACTIVE" : "PERCUSSION / REQUIRES UPPER B",
            {performance.x + 17.0F, performance.y + 3.0F, divider - performance.x - 34.0F, 18.0F},
            separate_eligibility ? 13.5F : 10.5F);
    if (separate_eligibility) {
        if (reference_percussion) {
            centered(drawing, eligible ? "UPPER B ROUTE ACTIVE" : "REQUIRES UPPER B",
                {performance.x + 12.0F, performance.y + performance.height - 16.0F,
                 divider - performance.x - 24.0F, 11.0F}, 9.0F, eligible ? kGreen : kMuted);
        } else {
            centered(drawing, eligible ? "UPPER B ROUTE ACTIVE" : "REQUIRES UPPER B",
                {performance.x + 12.0F, performance.y + 73.0F, divider - performance.x - 24.0F, 16.0F}, 10.0F, eligible ? kGreen : kMuted);
        }
    }
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        const auto& bounds = layout.registration_panels[manual];
        panel(drawing, bounds, true, flat);
        if (wide_legibility) {
            const float state_width = bounds.width * 0.43F;
            const float state_x = bounds.x + bounds.width - state_width - 14.0F;
            heading(drawing, manual == 0 ? "UPPER DRAWBARS" : "LOWER DRAWBARS",
                    {bounds.x + 16.0F, bounds.y + 3.0F, bounds.width - state_width - 32.0F, 23.0F}, 14.0F);
            const UiColor state_color = view.applied.controls.route_enabled[manual] ? kUiBrass : kMuted;
            centered(drawing, view.edited_banks[manual] == DrawbarBank::A ? "EDIT BANK A" : "EDIT BANK B",
                     {state_x, bounds.y + 2.0F, state_width, 14.0F}, 11.5F, state_color);
            centered(drawing, sounding_caption(view, static_cast<Manual>(manual)),
                     {state_x, bounds.y + 16.0F, state_width, 14.0F}, 11.5F, state_color);
        } else {
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
        }
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
                paint_key(drawing, key, view.applied.held_keys[manual][index], focused, flat, wide_legibility);
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
