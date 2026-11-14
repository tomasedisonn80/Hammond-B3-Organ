// A34 actual-model geometry and independent atlas-metric exporter; not a CTest target.
#include "UiModel.h"
#include "FontData.h"

#include <algorithm>
#include <array>
#include <iomanip>
#include <iostream>
#include <limits>
#include <string_view>

using namespace hammond;
using namespace hammond::standalone;

namespace {
void rect(UiRect r) {
    std::cout << '[' << r.x << ',' << r.y << ',' << r.width << ',' << r.height << ']';
}
float advance(std::string_view text, float size, const font_data::Atlas& atlas) {
    float width = 0;
    for (const char c : text)
        width += static_cast<float>(font_data::glyph(atlas, static_cast<unsigned char>(c)).advance_64) *
            size / static_cast<float>(atlas.pixel_height) / 64.0F;
    return width;
}
UiRect ink(std::string_view text, float x, float y, float size, const font_data::Atlas& atlas) {
    float left = std::numeric_limits<float>::max(), top = left, right = -left, bottom = -left;
    const float scale = size / static_cast<float>(atlas.pixel_height);
    for (const char c : text) {
        const auto& glyph = font_data::glyph(atlas, static_cast<unsigned char>(c));
        if (glyph.width != 0 && glyph.height != 0) {
            const float gx = x + static_cast<float>(glyph.bearing_x) * scale;
            const float gy = y + static_cast<float>(atlas.ascent + glyph.bearing_y) * scale;
            left = std::min(left, gx); top = std::min(top, gy);
            right = std::max(right, gx + static_cast<float>(glyph.width) * scale);
            bottom = std::max(bottom, gy + static_cast<float>(glyph.height) * scale);
        }
        x += static_cast<float>(glyph.advance_64) * scale / 64.0F;
    }
    return {left, top, right - left, bottom - top};
}
bool sharp(unsigned i) { return i == 1 || i == 3 || i == 6 || i == 8 || i == 10; }
}

int main() {
    std::cout << std::setprecision(9) << "[";
    bool first = true;
    for (const auto dimensions : std::array<std::array<int, 2>, 4>{{
        {960,700}, {1280,900}, {1400,820}, {1672,941}}}) {
        UiModel model;
        if (!model.resize(static_cast<float>(dimensions[0]), static_cast<float>(dimensions[1]))) return 1;
        const auto& layout = model.layout();
        if (!first) std::cout << ',';
        first = false;
        float left = 0, right = 0;
        std::cout << "{\"window\":[" << dimensions[0] << ',' << dimensions[1] << "],\"header_controls\":[";
        for (std::size_t i = 0; i < kUiCommonControlCount; ++i) {
            const auto& control = layout.controls[i];
            if (i != 0) std::cout << ',';
            std::cout << "{\"kind\":" << static_cast<unsigned>(control.id.kind) << ",\"index\":"
                      << static_cast<unsigned>(control.id.index) << ",\"bounds\":";
            rect(control.bounds); std::cout << '}';
            if (control.id.kind == UiControlKind::Workspace && control.id.index == 2)
                left = control.bounds.x + control.bounds.width + 12;
            if (control.id.kind == UiControlKind::SaveControls) right = control.bounds.x - 12;
        }
        constexpr std::string_view title = "TONEWHEEL ATLAS";
        float size = layout.show_cabinet ? 40.0F : 28.0F;
        const float natural = advance(title, size, font_data::kSerif);
        if (natural > right - left) size *= (right - left) / natural;
        const float width = advance(title, size, font_data::kSerif);
        const float before = left + (right - left - width) / 2;
        const float after = std::clamp((layout.width - width) / 2, left, std::max(left, right - width));
        const float y = layout.header.y + (layout.show_cabinet ? 4.0F : 8.0F);
        std::cout << "],\"title\":{\"size\":" << size << ",\"advance\":" << width
                  << ",\"available\":[" << left << ',' << right << "],\"before_center\":"
                  << before + width / 2 << ",\"after_center\":" << after + width / 2
                  << ",\"before_ink\":";
        rect(ink(title, before, y, size, font_data::kSerif));
        std::cout << ",\"after_ink\":"; rect(ink(title, after, y, size, font_data::kSerif));
        std::cout << "},\"presets\":[";
        bool first_key = true;
        constexpr std::array<std::string_view,12> names{"C","C#","D","D#","E","F","F#","G","G#","A","A#","B"};
        for (std::size_t i = 0; i < layout.control_count; ++i) {
            const auto& key = layout.controls[i];
            if (key.id.kind != UiControlKind::PresetKey) continue;
            if (!first_key) std::cout << ',';
            first_key = false;
            std::cout << "{\"manual\":" << static_cast<unsigned>(key.id.manual) << ",\"index\":"
                      << static_cast<unsigned>(key.id.index) << ",\"bounds\":";
            rect(key.bounds); std::cout << ",\"label\":"; rect(key.label_bounds);
            std::cout << ",\"glyphs\":[";
            const auto name = names[key.id.index];
            const unsigned rows = sharp(key.id.index) ? 2U : 1U;
            for (unsigned row = 0; row < rows; ++row) {
                if (row != 0) std::cout << ',';
                const auto text = name.substr(row, 1);
                const float width_glyph = advance(text, 9, font_data::kSans);
                const float x = key.label_bounds.x + (key.label_bounds.width - width_glyph) / 2;
                const float gy = key.label_bounds.y + 0.1F + 9 * static_cast<float>(row);
                std::cout << "{\"text\":\"" << text << "\",\"size\":9,\"advance\":" << width_glyph << ",\"ink\":";
                rect(ink(text, x, gy, 9, font_data::kSans)); std::cout << '}';
            }
            std::cout << "]}";
        }
        std::cout << "],\"playing_counts\":[" << layout.manual_keys[0].size() << ','
                  << layout.manual_keys[1].size() << ',' << layout.pedal_keys.size() << "]}";
    }
    std::cout << "]\n";
}
