#include "InstrumentView.h"
#include "FontData.h"

#include <SDL.h>

#include <algorithm>
#include <array>
#include <bit>
#include <charconv>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <limits>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

#ifdef _WIN32
#include <cstdio>
#include <fcntl.h>
#include <io.h>
#endif

// Compile the actual painter once, in this translation unit. This permits an
// independent direct private-helper state probe without a production hook or
// modified painter. CMake MUST NOT also compile InstrumentView.cpp for this
// executable. The same source is built against genuine pre-H1 and H1 painters.
#include "../InstrumentView.cpp"

namespace hammond::standalone {
template <typename Drawer>
constexpr bool h1_fixture_helper_present = requires(Drawer& drawing, UiRect bounds,
                                                   ReferenceCompositionScale scale) {
    reference_header_h1_material(drawing, bounds, scale);
};
template <typename Drawer>
bool h1_fixture_invoke_helper(Drawer& drawing, UiRect bounds, ReferenceCompositionScale scale) {
    if constexpr (h1_fixture_helper_present<Drawer>) {
        reference_header_h1_material(drawing, bounds, scale);
        return true;
    } else {
        return false;
    }
}
} // namespace hammond::standalone

// Independently frozen H1 section 7. No field-color oracle, candidate-derived
// support or before-painter switch is present. The comparison owner reconstructs
// exact support, opaque children, glyph cores and all 103 numerical screens.
namespace {
using namespace hammond;
using namespace hammond::standalone;
using Pixel = std::array<std::uint8_t, 4>;
static_assert(sizeof(Pixel) == 4);
static_assert(sizeof(float) == 4 && std::numeric_limits<float>::is_iec559);
constexpr std::string_view protocol = "header-material-h1-v1";
constexpr std::size_t case_count = 48;
constexpr int maximum_width = 3866, maximum_height = 2194;
constexpr Pixel incoming_color{17, 23, 31, 127};

struct Totals {
    std::size_t cases{}, checks{}, paintings{}, clipped_cases{}, empty_cases{}, inactive_cases{};
    std::size_t protected_pixels{}, repaints{}, clip_companions{}, quiet_clip_pixels{};
    std::size_t history_states{}, history_repaints{}, fresh_repaints{}, helper_probes{};
} totals;
void require(bool condition, std::string_view message) {
    ++totals.checks;
    if (!condition) throw std::runtime_error(std::string(message) + ": " + SDL_GetError());
}
float f32(float value) { volatile float rounded = value; return rounded; }
float addf(float a, float b) { return f32(a + b); }
float subf(float a, float b) { return f32(a - b); }
float mulf(float a, float b) { return f32(a * b); }
float divf(float a, float b) { return f32(a / b); }

struct Case {
    float width{1672}, height{941}, rx{1}, ry{1};
    int origin_x{}, origin_y{};
    bool clipped{}, logical_clip{}, resource{}, pending{}, held{true};
    std::string_view clip_kind{"disabled"};
    SDL_Rect clip_request{};
    unsigned level{4};
    PresetSelection route{PresetSelection::BankB}, pending_route{PresetSelection::BankB};
    UiControlId focus{UiControlKind::SaveControls};
    UiWorkspace workspace{UiWorkspace::Play};
    UiPresentation presentation{UiPresentation::Dimensional};
    SDL_BlendMode blend{SDL_BLENDMODE_BLEND};
};
bool active(const Case& c) {
    return c.workspace == UiWorkspace::Play && c.presentation == UiPresentation::Dimensional &&
           c.width >= 1400 && c.width <= 8192 && c.height >= 820 && c.height <= 8192;
}
bool eligible(const Case& c) {
    return active(c) && std::isfinite(c.rx) && std::isfinite(c.ry) &&
           c.rx > 0 && c.ry > 0 && c.rx <= 2 && c.ry <= 2;
}
DrawbarBank edited_bank(const Case& c) {
    return c.route == PresetSelection::BankA ? DrawbarBank::A : DrawbarBank::B;
}
std::string_view route_name(PresetSelection route) {
    switch (route) {
    case PresetSelection::BankA: return "A";
    case PresetSelection::BankB: return "B";
    case PresetSelection::D: return "D";
    case PresetSelection::Cancel: return "Cancel";
    default: throw std::runtime_error("undeclared fixture route");
    }
}
ReferenceCompositionScale independent_scale(const Case& c) {
    const float sx = divf(c.width, 1672), sy = divf(c.height, 941);
    return {sx, sy, std::min(sx, sy)};
}
UiRect independent_panel(const Case& c) {
    const auto s = independent_scale(c);
    const float x = mulf(72, s.sx), y = mulf(10, s.sy);
    return {x, y, subf(mulf(1600, s.sx), x), subf(mulf(112, s.sy), y)};
}
UiRect independent_inset(const Case& c) {
    const auto s = independent_scale(c);
    const auto p = independent_panel(c);
    const float dx = mulf(4, s.sx), dy = mulf(4, s.sy);
    return {addf(p.x, dx), addf(p.y, dy), std::max(0.0F, subf(p.width, mulf(2, dx))),
            std::max(0.0F, subf(p.height, mulf(2, dy)))};
}
SDL_Rect intrinsic_field(const Case& c) {
    const auto i = independent_inset(c);
    const int left = static_cast<int>(std::ceil(static_cast<double>(i.x) * c.rx - 0.5));
    const int top = static_cast<int>(std::ceil(static_cast<double>(i.y) * c.ry - 0.5));
    const int right = static_cast<int>(std::ceil((static_cast<double>(i.x) + i.width) * c.rx - 0.5));
    const int bottom = static_cast<int>(std::ceil((static_cast<double>(i.y) + i.height) * c.ry - 0.5));
    return {left, top, right - left, bottom - top};
}

std::array<Case, case_count> cases() {
    std::array<Case, case_count> result{};
    constexpr std::array<std::array<float, 2>, 3> sizes{{{1672, 941}, {1400, 820}, {1920, 1080}}};
    constexpr std::array<float, 3> scales{1, 1.5F, 2};
    for (std::size_t size = 0; size < sizes.size(); ++size)
        for (std::size_t scale = 0; scale < scales.size(); ++scale) {
            auto& c = result[size * 3 + scale];
            c.width = sizes[size][0]; c.height = sizes[size][1]; c.rx = c.ry = scales[scale];
            c.origin_x = 13; c.origin_y = 17; c.level = static_cast<unsigned>(scale * 4);
            c.route = scale == 0 ? PresetSelection::BankB : scale == 1 ? PresetSelection::BankA : PresetSelection::D;
            c.pending = scale == 1; c.held = scale != 0;
            c.focus = {scale == 0 ? UiControlKind::SaveControls : scale == 1 ? UiControlKind::Help : UiControlKind::Presentation};
        }
    for (std::size_t shape = 0; shape < 2; ++shape)
        for (std::size_t scale = 0; scale < 2; ++scale) {
            auto& c = result[9 + shape * 2 + scale];
            c.width = static_cast<float>(shape == 0 ? 1920 : 1400); c.height = static_cast<float>(shape == 0 ? 820 : 1080);
            c.rx = c.ry = scale == 0 ? 0.75F : 1.25F;
        }
    result[13].width = 1672.5F; result[13].height = 941.25F;
    result[13].rx = 1.5F; result[13].ry = 2; result[13].origin_x = 13; result[13].origin_y = 17;
    result[14].rx = 1.25F; result[14].ry = 0.75F; result[14].origin_x = -13; result[14].origin_y = -17;
    constexpr std::array<std::string_view, 4> edges{"left", "right", "top", "bottom"};
    constexpr std::array<SDL_Rect, 4> logical{{{74, 24, 4, 72}, {1594, 24, 4, 72},
                                             {90, 12, 1490, 4}, {90, 106, 1490, 4}}};
    for (std::size_t edge = 0; edge < edges.size(); ++edge)
        for (std::size_t scale = 0; scale < scales.size(); ++scale) {
            auto& c = result[15 + edge * 3 + scale];
            c.rx = c.ry = scales[scale]; c.origin_x = 13; c.origin_y = 17;
            c.clipped = true; c.logical_clip = scale == 1; c.clip_kind = edges[edge];
            const auto b = intrinsic_field(c);
            const std::array<SDL_Rect, 4> physical{{
                {b.x - 2, b.y - 2, 4, b.h + 4}, {b.x + b.w - 2, b.y - 2, 4, b.h + 4},
                {b.x - 2, b.y - 2, b.w + 4, 4}, {b.x - 2, b.y + b.h - 2, b.w + 4, 4}}};
            c.clip_request = c.logical_clip ? logical[edge] : physical[edge];
        }
    for (std::size_t index = 27; index <= 29; ++index) {
        auto& c = result[index]; c.origin_x = 13; c.origin_y = 17; c.clipped = true;
        const auto b = intrinsic_field(c);
        c.clip_kind = index == 27 ? "disjoint" : index == 28 ? "zero-physical" : "zero-logical";
        c.clip_request = index == 27 ? SDL_Rect{b.x + b.w + 4, b.y + 4, 8, 8} :
                         index == 28 ? SDL_Rect{b.x, b.y, 0, 0} : SDL_Rect{76, 14, 0, 0};
        c.logical_clip = index == 29;
        if (index == 29) c.blend = SDL_BLENDMODE_NONE;
    }
    for (std::size_t scale = 0; scale < scales.size(); ++scale) {
        auto& c = result[30 + scale]; c.width = c.height = 8192; c.rx = c.ry = scales[scale]; c.resource = true;
        const auto b = intrinsic_field(c); c.origin_x = -b.x; c.origin_y = -b.y;
    }
    result[33].rx = 2.01F; result[34].ry = 2.01F;
    result[35].blend = SDL_BLENDMODE_NONE;
    constexpr std::array<std::array<float, 2>, 4> inactive{{{1399, 820}, {1400, 819}, {960, 700}, {1280, 900}}};
    for (std::size_t i = 0; i < inactive.size(); ++i) {
        auto& c = result[36 + i]; c.width = inactive[i][0]; c.height = inactive[i][1];
        c.rx = c.ry = 1.5F; c.origin_x = 13; c.origin_y = 17;
    }
    result[40].presentation = UiPresentation::Flat;
    result[41].workspace = UiWorkspace::Rotary; result[42].workspace = UiWorkspace::Service;
    result[43].width = 1400; result[43].height = 820; result[43].presentation = UiPresentation::Flat;
    result[44].level = 0; result[44].route = PresetSelection::Cancel; result[44].pending = true;
    result[44].pending_route = PresetSelection::BankA; result[44].held = false; result[44].focus = {UiControlKind::Help};
    result[45].level = 8; result[45].route = PresetSelection::D; result[45].pending = true;
    result[45].focus = {UiControlKind::Presentation};
    result[46].focus = {UiControlKind::ManualDrawbar, Manual::Upper, DrawbarBank::B, 4};
    result[47].rx = result[47].ry = 1.25F; result[47].origin_x = -13; result[47].origin_y = -17;
    result[47].clipped = true; result[47].clip_kind = "top-left";
    const auto b = intrinsic_field(result[47]); result[47].clip_request = {b.x - 2, b.y - 2, 8, 8};
    return result;
}

template <typename Range, typename Writer>
void array(std::ostream& out, const Range& values, Writer write) {
    out << '[';
    bool first = true;
    for (const auto& value : values) {
        if (!first) out << ',';
        first = false;
        write(out, value);
    }
    out << ']';
}

void rect(std::ostream& out, UiRect r) {
    out << '[' << r.x << ',' << r.y << ',' << r.width << ',' << r.height << ']';
}
void rect(std::ostream& out, SDL_Rect r) {
    out << '[' << r.x << ',' << r.y << ',' << r.w << ',' << r.h << ']';
}
void control_id(std::ostream& out, UiControlId id) {
    out << '[' << static_cast<unsigned>(id.kind) << ',' << static_cast<unsigned>(id.manual)
        << ',' << static_cast<unsigned>(id.bank) << ',' << static_cast<unsigned>(id.index) << ']';
}
void quad(std::ostream& out, const UiQuad& value) {
    array(out, value.points, [](auto& stream, UiPoint point) {
        stream << '[' << point.x << ',' << point.y << ']';
    });
}
void key_geometry(std::ostream& out, const UiKeyGeometry& key) {
    out << "{\"note\":[" << static_cast<unsigned>(key.note.target) << ','
        << static_cast<unsigned>(key.note.value) << "],\"bounds\":";
    rect(out, key.bounds);
    out << ",\"accidental\":" << key.accidental << ",\"hit\":";
    quad(out, key.hit);
    out << ",\"top\":";
    quad(out, key.top);
    out << ",\"front\":";
    quad(out, key.front);
    out << '}';
}
void controls(std::ostream& out, const ControlSnapshot& value) {
    const auto number = [](auto& stream, auto v) { stream << static_cast<unsigned>(v); };
    out << "{\"drawbars\":";
    array(out, value.drawbars, [&](auto& stream, const auto& manual) {
        array(stream, manual, [&](auto& bank_stream, const auto& bank) { array(bank_stream, bank, number); });
    });
    out << ",\"selected_banks\":";
    array(out, value.selected_banks, number);
    out << ",\"route_enabled\":";
    array(out, value.route_enabled, number);
    out << ",\"expression\":" << value.expression << ",\"percussion\":[" << value.percussion.enabled
        << ',' << static_cast<unsigned>(value.percussion.harmonic)
        << ',' << static_cast<unsigned>(value.percussion.volume)
        << ',' << static_cast<unsigned>(value.percussion.decay) << "],\"pedal_drawbars\":";
    array(out, value.pedal_drawbars, number);
    out << ",\"fixed_registrations\":";
    array(out, value.fixed_registrations, number);
    out << '}';
}
void session(std::ostream& out, const SessionSnapshot& value) {
    out << "{\"controls\":";
    controls(out, value.controls);
    out << ",\"held_keys\":";
    array(out, value.held_keys, [](auto& stream, const auto& manual) {
        array(stream, manual, [](auto& key_stream, bool held) { key_stream << held; });
    });
    out << ",\"held_pedals\":";
    array(out, value.held_pedals, [](auto& stream, bool held) { stream << held; });
    out << ",\"frame_clock\":" << value.frame_clock << ",\"sample_rate\":" << value.sample_rate
        << ",\"peak\":" << value.peak << ",\"prepared\":" << value.prepared
        << ",\"running\":" << value.running << ",\"publication_revision\":" << value.publication_revision
        << ",\"resolved_sequence\":" << value.resolved_sequence
        << ",\"last_applied_sequence\":" << value.last_applied_sequence
        << ",\"recovery_count\":" << value.recovery_count << ",\"queue_overflows\":" << value.queue_overflows
        << ",\"rejected_commands\":" << value.rejected_commands
        << ",\"discarded_commands\":" << value.discarded_commands << ",\"fault_flags\":" << value.fault_flags
        << ",\"last_core_status\":" << static_cast<unsigned>(value.last_core_status) << '}';
}
std::string session_record(const SessionSnapshot& value) {
    std::ostringstream out;
    out << std::boolalpha << std::setprecision(std::numeric_limits<double>::max_digits10);
    session(out, value);
    return out.str();
}

// Explicit, padding-independent serialization covers every public view/layout
// member. The same records are compared around paint and across paired streams;
// no hash collision or implementation-specific struct padding can hide a change.
std::string model_record(const UiModel& model) {
    std::ostringstream out;
    out << std::boolalpha << std::setprecision(std::numeric_limits<double>::max_digits10);
    const auto& view = model.view();
    out << "{\"view\":{\"controls\":";
    controls(out, view.controls);
    out << ",\"applied\":";
    session(out, view.applied);
    const auto number = [](auto& stream, auto v) { stream << static_cast<unsigned>(v); };
    out << ",\"edited_banks\":";
    array(out, view.edited_banks, number);
    out << ",\"focus\":";
    control_id(out, view.focus);
    out << ",\"roving_manual_keys\":";
    array(out, view.roving_manual_keys, number);
    out << ",\"roving_pedal_key\":" << static_cast<unsigned>(view.roving_pedal_key)
        << ",\"keyboard_target\":" << static_cast<unsigned>(view.keyboard_target)
        << ",\"manual_base_midi\":" << static_cast<unsigned>(view.manual_base_midi)
        << ",\"pedal_octave\":" << static_cast<unsigned>(view.pedal_octave)
        << ",\"controls_pending\":" << view.controls_pending << ",\"controls_dirty\":" << view.controls_dirty
        << ",\"text_entry_active\":" << view.text_entry_active << ",\"pointer_captured\":" << view.pointer_captured
        << ",\"input_recovery\":" << view.input_recovery
        << ",\"last_submit_status\":" << static_cast<unsigned>(view.last_submit_status)
        << ",\"workspace\":" << static_cast<unsigned>(view.workspace)
        << ",\"presentation\":" << static_cast<unsigned>(view.presentation) << ",\"workspace_focus\":";
    array(out, view.workspace_focus, [](auto& stream, UiControlId id) { control_id(stream, id); });
    const auto& layout = model.layout();
    out << "},\"layout\":{" << std::setprecision(std::numeric_limits<float>::max_digits10)
        << "\"width\":" << layout.width << ",\"height\":" << layout.height
        << ",\"show_cabinet\":" << layout.show_cabinet
        << ",\"bank_controls_in_cheeks\":" << layout.bank_controls_in_cheeks
        << ",\"sidebar_pedals\":" << layout.sidebar_pedals;
    const auto named_rect = [&](std::string_view name, UiRect bounds) {
        out << ",\"" << name << "\":";
        rect(out, bounds);
    };
    const auto named_rects = [&](std::string_view name, const auto& bounds) {
        out << ",\"" << name << "\":";
        array(out, bounds, [](auto& stream, UiRect r) { rect(stream, r); });
    };
    named_rect("header", layout.header);
    named_rects("registration_panels", layout.registration_panels);
    named_rect("performance_panel", layout.performance_panel);
    named_rect("keyboard_toolbar", layout.keyboard_toolbar);
    named_rects("manual_panels", layout.manual_panels);
    named_rect("pedal_panel", layout.pedal_panel);
    named_rect("footer", layout.footer);
    named_rect("cabinet_panel", layout.cabinet_panel);
    named_rect("cabinet_art", layout.cabinet_art);
    named_rects("manual_rail_panels", layout.manual_rail_panels);
    out << ",\"control_count\":" << layout.control_count << ",\"controls\":";
    array(out, layout.controls, [](auto& stream, const UiControlGeometry& control) {
        stream << "{\"id\":";
        control_id(stream, control.id);
        stream << ",\"bounds\":";
        rect(stream, control.bounds);
        stream << ",\"label_bounds\":";
        rect(stream, control.label_bounds);
        stream << ",\"value_bounds\":";
        rect(stream, control.value_bounds);
        stream << ",\"track\":";
        rect(stream, control.track);
        stream << '}';
    });
    out << ",\"manual_keys\":";
    array(out, layout.manual_keys, [](auto& stream, const auto& manual) {
        array(stream, manual, [](auto& key_stream, const auto& key) { key_geometry(key_stream, key); });
    });
    out << ",\"pedal_keys\":";
    array(out, layout.pedal_keys, [](auto& stream, const auto& key) { key_geometry(stream, key); });
    named_rects("preset_key_panels", layout.preset_key_panels);
    out << ",\"workspace\":" << static_cast<unsigned>(layout.workspace)
        << ",\"presentation\":" << static_cast<unsigned>(layout.presentation);
    named_rect("workspace_panel", layout.workspace_panel);
    out << "}}";
    return out.str();
}

std::string hit_record(const UiModel& model) {
    std::ostringstream out;
    out << std::boolalpha << std::setprecision(std::numeric_limits<float>::max_digits10);
    const auto& layout = model.layout();
    const auto probe = [&](UiPoint point) {
        out << "{\"point\":[" << point.x << ',' << point.y << "],\"hit\":";
        control_id(out, ui_hit_test(layout, point)); out << '}';
    };
    out << "{\"controls\":[";
    for (std::size_t i = 0; i < layout.controls.size(); ++i) {
        if (i) out << ',';
        const auto& geometry = layout.controls[i];
        const auto& b = geometry.bounds;
        out << "{\"id\":"; control_id(out, geometry.id);
        out << ",\"visible\":" << ui_control_visible(layout, geometry.id) << ",\"probes\":[";
        probe({addf(b.x, mulf(b.width, 0.5F)), addf(b.y, mulf(b.height, 0.5F))});
        out << ','; probe({b.x, b.y});
        out << ','; probe({addf(b.x, b.width), b.y});
        out << ','; probe({b.x, addf(b.y, b.height)});
        out << ','; probe({addf(b.x, b.width), addf(b.y, b.height)});
        out << "]}";
    }
    const auto key = [&](const UiKeyGeometry& geometry) {
        out << "{\"note\":[" << static_cast<unsigned>(geometry.note.target) << ','
            << static_cast<unsigned>(geometry.note.value) << "],\"probes\":[";
        const auto& q = geometry.hit.points;
        probe({f32((q[0].x + q[1].x + q[2].x + q[3].x) * 0.25F),
               f32((q[0].y + q[1].y + q[2].y + q[3].y) * 0.25F)});
        for (const auto point : q) { out << ','; probe(point); }
        out << "]}";
    };
    out << "],\"manual_keys\":[";
    for (std::size_t manual = 0; manual < layout.manual_keys.size(); ++manual) {
        if (manual) out << ',';
        out << '[';
        for (std::size_t i = 0; i < layout.manual_keys[manual].size(); ++i) {
            if (i) out << ',';
            key(layout.manual_keys[manual][i]);
        }
        out << ']';
    }
    out << "],\"pedal_keys\":[";
    for (std::size_t i = 0; i < layout.pedal_keys.size(); ++i) {
        if (i) out << ',';
        key(layout.pedal_keys[i]);
    }
    out << "]}";
    return out.str();
}

UiModel state_for(const Case& test) {
    UiModel model;
    require(model.resize(test.width, test.height) && model.set_presentation(test.presentation) &&
            model.set_workspace(test.workspace), "fixed admitted layout");
    SessionSnapshot snapshot;
    snapshot.controls = model.view().controls;
    for (auto& manual : snapshot.controls.drawbars)
        for (auto& bank : manual) bank.fill(static_cast<std::uint8_t>(test.level));
    snapshot.controls.expression = 0.625;
    snapshot.controls.pedal_drawbars = {3, 7};
    snapshot.controls.percussion = {true, PercussionHarmonic::Second, PercussionVolume::Normal, PercussionDecay::Slow};
    ControlState applied;
    require(applied.restore(snapshot.controls) && applied.select_preset(Manual::Upper, test.route) &&
            applied.select_preset(Manual::Lower, PresetSelection::BankB), "complete Upper override and common Lower controls");
    snapshot.controls = applied.snapshot();
    snapshot.held_keys[0][24] = snapshot.held_keys[1][36] = snapshot.held_pedals[12] = test.held;
    snapshot.frame_clock = 38400; snapshot.sample_rate = 48000; snapshot.peak = 0.125F;
    snapshot.prepared = snapshot.running = true; snapshot.publication_revision = 4;
    model.observe(snapshot);
    require(model.activate({UiControlKind::EditBank, Manual::Upper, edited_bank(test)}).count == 0 &&
            model.activate({UiControlKind::EditBank, Manual::Lower, DrawbarBank::B}).count == 0,
            "edited banks emit no musical command");
    auto expected = snapshot.controls;
    if (test.pending) {
        require(model.activate({UiControlKind::PresetKey, Manual::Upper, DrawbarBank::A,
                               static_cast<std::uint8_t>(test.pending_route)}).count == 1,
                "declared unacknowledged Upper preset request");
        ControlState requested;
        require(requested.restore(expected) && requested.select_preset(Manual::Upper, test.pending_route),
                "independent complete desired controls");
        expected = requested.snapshot();
    }
    for (unsigned step = 0; step < 72 && model.view().focus != test.focus; ++step)
        require(model.key({UiKey::Tab, true}).count == 0 && model.key({UiKey::Tab, false}).count == 0,
                "ordinary focus traversal emits no musical command");
    require(model.view().focus == test.focus, "literal focus identity reached through the real model");
    require(model.view().edited_banks[0] == edited_bank(test) && model.view().edited_banks[1] == DrawbarBank::B,
            "both literal edited-bank identities retained");
    require(model.view().controls == expected && session_record(model.view().applied) == session_record(snapshot) &&
            model.view().controls_pending == test.pending, "complete desired/applied snapshots and pending state");
    require(reference_composition_active(model.layout()) == active(test), "independent active/inactive classification");
    // UiModel retains the whole instrument geometry in every workspace. The
    // non-Play workspaces filter visibility; they do not shrink stored arrays.
    require(model.layout().control_count == 68 && model.layout().manual_keys.size() * kManualKeyCount +
            model.layout().pedal_keys.size() == 147, "all workspaces retain 68 stored controls and 147 playing keys");
    require(std::count_if(model.layout().controls.begin(), model.layout().controls.end(), [](const auto& control) {
        return control.id.kind == UiControlKind::PresetKey;
    }) == 24, "all workspaces retain 24 stored preset controls");
    const auto visible_controls = std::count_if(model.layout().controls.begin(), model.layout().controls.end(),
        [&](const auto& control) { return ui_control_visible(model.layout(), control.id); });
    require(visible_controls == (test.workspace == UiWorkspace::Play ? 68 : 10),
            "workspace visibility retains 68 Play or ten common controls");
    if (active(test)) {
        const auto expected_header = independent_panel(test), actual_header = model.layout().header;
        require(actual_header.x == expected_header.x && actual_header.y == expected_header.y &&
                actual_header.width == expected_header.width && actual_header.height == expected_header.height,
                "independent binary32 mapped panel equals live layout geometry");
    }
    return model;
}

bool equal(SDL_Rect a, SDL_Rect b) { return a.x == b.x && a.y == b.y && a.w == b.w && a.h == b.h; }
bool same_float(float a, float b) { return std::bit_cast<std::uint32_t>(a) == std::bit_cast<std::uint32_t>(b); }
struct Transform {
    float sx{}, sy{};
    SDL_Rect viewport{}, clip{}, logical_viewport{}, logical_clip{};
    bool clipped{};
    SDL_BlendMode blend{};
    Pixel color{};
};
Transform transform(SDL_Renderer* renderer) {
    Transform result;
    SDL_RenderGetScale(renderer, &result.sx, &result.sy);
    SDL_RenderGetViewport(renderer, &result.logical_viewport);
    SDL_RenderGetClipRect(renderer, &result.logical_clip);
    result.clipped = SDL_RenderIsClipEnabled(renderer) == SDL_TRUE;
    require(std::isfinite(result.sx) && std::isfinite(result.sy) && result.sx > 0 && result.sy > 0,
            "finite positive renderer scale");
    require(SDL_GetRenderDrawBlendMode(renderer, &result.blend) == 0 &&
            SDL_GetRenderDrawColor(renderer, &result.color[0], &result.color[1], &result.color[2], &result.color[3]) == 0,
            "query actual blend and draw color");
    require(SDL_RenderSetScale(renderer, 1, 1) == 0, "query physical viewport and clip without rounding");
    SDL_RenderGetViewport(renderer, &result.viewport);
    SDL_RenderGetClipRect(renderer, &result.clip);
    require(SDL_RenderSetScale(renderer, result.sx, result.sy) == 0, "restore both exact scale components");
    require(result.viewport.w > 0 && result.viewport.h > 0 && result.clip.w >= 0 && result.clip.h >= 0,
            "positive viewport and nonnegative clip extents");
    return result;
}
bool same_transform(const Transform& a, const Transform& b) {
    return same_float(a.sx, b.sx) && same_float(a.sy, b.sy) && equal(a.viewport, b.viewport) &&
           equal(a.clip, b.clip) && equal(a.logical_viewport, b.logical_viewport) &&
           equal(a.logical_clip, b.logical_clip) && a.clipped == b.clipped && a.blend == b.blend;
}
bool exact_transform(const Transform& a, const Transform& b) { return same_transform(a, b) && a.color == b.color; }
void transform_record(std::ostream& out, const Transform& t) {
    out << "{\"scale\":[" << t.sx << ',' << t.sy << "],\"viewport\":"; rect(out, t.viewport);
    out << ",\"clip\":"; rect(out, t.clip);
    out << ",\"logical_viewport\":"; rect(out, t.logical_viewport);
    out << ",\"logical_clip\":"; rect(out, t.logical_clip);
    out << ",\"clip_enabled\":" << t.clipped << ",\"blend\":" << static_cast<unsigned>(t.blend)
        << ",\"draw_color\":";
    array(out, t.color, [](auto& stream, std::uint8_t channel) { stream << static_cast<unsigned>(channel); });
    out << '}';
}
bool visible(const Transform& t, int x, int y) {
    const auto xx = static_cast<std::int64_t>(x) - t.viewport.x;
    const auto yy = static_cast<std::int64_t>(y) - t.viewport.y;
    return xx >= 0 && yy >= 0 && xx < t.viewport.w && yy < t.viewport.h &&
           (!t.clipped || (xx >= t.clip.x && yy >= t.clip.y &&
                          xx < static_cast<std::int64_t>(t.clip.x) + t.clip.w &&
                          yy < static_cast<std::int64_t>(t.clip.y) + t.clip.h));
}
struct SurfaceSpec { int width{}, height{}; SDL_Rect viewport{}; };
SurfaceSpec surface_spec(const Case& c) {
    require(std::isfinite(c.width) && std::isfinite(c.height) && std::isfinite(c.rx) && std::isfinite(c.ry) &&
            c.width >= 960 && c.height >= 700 && c.width <= 8192 && c.height <= 8192 &&
            c.rx >= 0.75F && c.ry >= 0.75F && c.rx <= 2.01F && c.ry <= 2.01F,
            "bounded finite literal fixture geometry");
    const int w = static_cast<int>(std::ceil(mulf(c.width, c.rx)));
    const int h = static_cast<int>(std::ceil(mulf(c.height, c.ry)));
    const SurfaceSpec result{c.resource ? 64 : w + 2 * std::abs(c.origin_x),
                             c.resource ? 64 : h + 2 * std::abs(c.origin_y), {c.origin_x, c.origin_y, w, h}};
    require(result.width > 0 && result.width <= maximum_width && result.height > 0 && result.height <= maximum_height &&
            w <= 16384 && h <= 16384, "bounded output BEFORE any surface allocation");
    return result;
}
InstrumentViewInfo fixed_info() {
    InstrumentViewInfo info{};
    info.audio_running = true; info.sample_rate = 48000; info.buffer_frames = 512;
    info.audio_driver = "fixed-software-fixture"; info.device_name = "fixed copied state";
    info.status_message = "Frozen header material qualification";
    return info;
}
std::string info_record() {
    const auto info = fixed_info();
    std::ostringstream out;
    out << std::boolalpha
        << "{\"audio_running\":" << info.audio_running << ",\"sample_rate\":" << info.sample_rate
        << ",\"buffer_frames\":" << info.buffer_frames << ",\"audio_driver\":\"" << info.audio_driver
        << "\",\"device_name\":\"" << info.device_name << "\",\"status_message\":\"" << info.status_message
        << "\",\"clipped_samples\":" << info.clipped_samples << ",\"overlay\":" << static_cast<unsigned>(info.overlay)
        << ",\"audio_choices\":[],\"selected_device\":" << info.selected_device
        << ",\"selected_sample_rate\":" << info.selected_sample_rate << ",\"selected_buffer_frames\":" << info.selected_buffer_frames
        << ",\"midi_available\":" << info.midi_available << ",\"midi_open\":" << info.midi_open
        << ",\"midi_backend\":\"\",\"midi_port\":\"\",\"midi_status\":\"\",\"midi_choices\":[],\"selected_midi_port\":"
        << info.selected_midi_port << ",\"selected_midi_channels\":[1,2,3],\"selected_midi_expression\":[0,127,false]"
        << ",\"active_midi_expression\":[0,127,false],\"midi_expression_active\":" << info.midi_expression_active
        << ",\"midi_reconnect_pending\":" << info.midi_reconnect_pending << ",\"midi_messages\":" << info.midi_messages
        << ",\"inspection\":null}";
    return out.str();
}

struct HelperProbe {
    bool present{}, invoked{};
    UiRect bounds{};
    ReferenceCompositionScale scale{};
    Transform before{}, after{};
};
struct Frame {
    int width{}, height{};
    Transform before{}, after{};
    HelperProbe helper{};
    std::vector<Pixel> pixels;
    std::string model_before, model_after, session_before, session_after, hit_before, hit_after, backend;
    std::size_t visible_pixels{}, quiet_pixels{};
    std::size_t at(int x, int y) const { return static_cast<std::size_t>(y) * static_cast<std::size_t>(width) + static_cast<std::size_t>(x); }
};

class Target {
public:
    explicit Target(const Case& test, bool uncut = false) : test_(test), spec_(surface_spec(test)),
        surface_(SDL_CreateRGBSurfaceWithFormat(0, spec_.width, spec_.height, 32, SDL_PIXELFORMAT_RGBA32), SDL_FreeSurface),
        renderer_(surface_ ? SDL_CreateSoftwareRenderer(surface_.get()) : nullptr, SDL_DestroyRenderer), drawing_(renderer_.get()) {
        require(surface_ && renderer_, "create bounded software target");
        std::string error;
        require(drawing_.initialize(error), "initialize unchanged font/art textures");
        require(SDL_RenderSetScale(renderer_.get(), 1, 1) == 0 &&
                SDL_RenderSetViewport(renderer_.get(), &spec_.viewport) == 0 &&
                SDL_RenderSetClipRect(renderer_.get(), nullptr) == 0, "install physical viewport and disabled clip");
        if (test.clipped && !test.logical_clip && !uncut)
            require(SDL_RenderSetClipRect(renderer_.get(), &test.clip_request) == 0, "install physical clip");
        require(SDL_RenderSetScale(renderer_.get(), test.rx, test.ry) == 0, "install declared unequal scale components");
        if (test.clipped && test.logical_clip && !uncut)
            require(SDL_RenderSetClipRect(renderer_.get(), &test.clip_request) == 0, "install logical clip");
        require(SDL_SetRenderDrawBlendMode(renderer_.get(), test.blend) == 0, "install incoming blend mode");
        const auto actual = transform(renderer_.get());
        SDL_Rect expected_clip{};
        if (test.clipped && !uncut) {
            const float rx = test.logical_clip ? test.rx : 1, ry = test.logical_clip ? test.ry : 1;
            expected_clip = {static_cast<int>(std::floor(mulf(static_cast<float>(test.clip_request.x), rx))),
                             static_cast<int>(std::floor(mulf(static_cast<float>(test.clip_request.y), ry))),
                             static_cast<int>(std::floor(mulf(static_cast<float>(test.clip_request.w), rx))),
                             static_cast<int>(std::floor(mulf(static_cast<float>(test.clip_request.h), ry)))};
        }
        require(same_float(actual.sx, test.rx) && same_float(actual.sy, test.ry) && equal(actual.viewport, spec_.viewport) &&
                actual.clipped == (test.clipped && !uncut) && equal(actual.clip, expected_clip) && actual.blend == test.blend,
                "queried physical transform matches literal scenario");
        if (test.clipped && !uncut && (test.clip_request.w == 0 || test.clip_request.h == 0))
            require(actual.clipped && (actual.clip.w == 0 || actual.clip.h == 0), "zero extent stays enabled and empty");
        SDL_RendererInfo details{}; SDL_version version{}; SDL_GetVersion(&version);
        require(SDL_GetRendererInfo(renderer_.get(), &details) == 0 && details.name != nullptr &&
                std::string_view(details.name) == "software", "actual SDL software backend");
        std::ostringstream out;
        out << "{\"name\":\"" << details.name << "\",\"flags\":" << details.flags << ",\"texture_formats\":[";
        for (std::uint32_t i = 0; i < details.num_texture_formats; ++i) { if (i) out << ','; out << details.texture_formats[i]; }
        out << "],\"maximum_texture_size\":[" << details.max_texture_width << ',' << details.max_texture_height
            << "],\"sdl_version\":[" << static_cast<unsigned>(version.major) << ',' << static_cast<unsigned>(version.minor)
            << ',' << static_cast<unsigned>(version.patch) << "],\"surface_format\":" << SDL_PIXELFORMAT_RGBA32 << '}';
        backend_ = out.str();
    }

    Frame paint(const UiModel& model, bool probe_helper = true) {
        require(SDL_SetRenderDrawColor(renderer_.get(), incoming_color[0], incoming_color[1], incoming_color[2], incoming_color[3]) == 0,
                "install fixed incoming draw color");
        Frame frame;
        frame.width = spec_.width; frame.height = spec_.height; frame.backend = backend_;
        frame.helper.present = h1_fixture_helper_present<Drawing>;
        frame.helper.bounds = independent_inset(test_); frame.helper.scale = independent_scale(test_);
        frame.helper.before = transform(renderer_.get());
        if (probe_helper && eligible(test_) && frame.helper.present) {
            frame.helper.invoked = h1_fixture_invoke_helper(drawing_, frame.helper.bounds, frame.helper.scale);
            require(frame.helper.invoked, "present eligible helper is directly probed");
            ++totals.helper_probes;
        }
        frame.helper.after = transform(renderer_.get());
        require(exact_transform(frame.helper.before, frame.helper.after), "private H1 helper restores color and exact complete renderer state");
        // The actual whole painter clears its target. Probe pixels never supply
        // a before image, input texture or image-derived permission mask.
        frame.before = transform(renderer_.get());
        frame.model_before = model_record(model); frame.session_before = session_record(model.view().applied);
        frame.hit_before = hit_record(model);
        paint_instrument(drawing_, model, fixed_info());
        frame.after = transform(renderer_.get());
        frame.model_after = model_record(model); frame.session_after = session_record(model.view().applied);
        frame.hit_after = hit_record(model);
        require(same_transform(frame.before, frame.after), "paint preserves both scales, logical/physical viewport/clip, enable and blend");
        require(frame.model_before == frame.model_after && frame.session_before == frame.session_after &&
                frame.hit_before == frame.hit_after, "paint preserves complete copied model, layout, session and hit observations");
        require(SDL_RenderFlush(renderer_.get()) == 0 && SDL_LockSurface(surface_.get()) == 0, "flush and read exact RGBA bytes");
        frame.pixels.resize(static_cast<std::size_t>(spec_.width) * static_cast<std::size_t>(spec_.height));
        const auto* input = static_cast<const std::uint8_t*>(surface_->pixels);
        for (int y = 0; y < spec_.height; ++y)
            std::memcpy(frame.pixels.data() + frame.at(0, y), input + static_cast<std::size_t>(y) * static_cast<std::size_t>(surface_->pitch),
                        static_cast<std::size_t>(spec_.width) * sizeof(Pixel));
        SDL_UnlockSurface(surface_.get());
        ++totals.paintings;
        return frame;
    }
private:
    Case test_;
    SurfaceSpec spec_;
    std::unique_ptr<SDL_Surface, decltype(&SDL_FreeSurface)> surface_;
    std::unique_ptr<SDL_Renderer, decltype(&SDL_DestroyRenderer)> renderer_;
    Drawing drawing_;
    std::string backend_;
};

// A quiet-pixel exclusion is a source-derived glyph-copy destination envelope,
// not a material allowance. SDL 2.32.10 clips a resampled glyph's source and
// destination together, so a clipped copy need not equal an uncut image crop.
// The independent checker additionally reconstructs opaque glyph cores and the
// pinned clipped-copy sampling. This fixture never relaxes exterior containment.
float measured_width(std::string_view value, float size, const font_data::Atlas& atlas) {
    const float scale = divf(size, static_cast<float>(atlas.pixel_height));
    float width = 0;
    for (const char character : value)
        width = addf(width, divf(mulf(static_cast<float>(font_data::glyph(atlas, static_cast<unsigned char>(character)).advance_64), scale), 64));
    return width;
}
void text_destinations(std::vector<SDL_Rect>& output, const Case& test, std::string_view value,
                       float x, float top, float size, const font_data::Atlas& atlas) {
    const float scale = divf(size, static_cast<float>(atlas.pixel_height));
    const float baseline = addf(top, mulf(static_cast<float>(atlas.ascent), scale));
    for (const char character : value) {
        const auto& glyph = font_data::glyph(atlas, static_cast<unsigned char>(character));
        if (glyph.width != 0 && glyph.height != 0) {
            const int px = mulf(static_cast<float>(glyph.width), scale) < 1 ? 2 : 0;
            const int py = mulf(static_cast<float>(glyph.height), scale) < 1 ? 2 : 0;
            const float gx = addf(x, mulf(static_cast<float>(glyph.bearing_x - px), scale));
            const float gy = addf(baseline, mulf(static_cast<float>(glyph.bearing_y - py), scale));
            const float gw = mulf(static_cast<float>(glyph.width + 2 * px), scale);
            const float gh = mulf(static_cast<float>(glyph.height + 2 * py), scale);
            const float dx = mulf(gx, test.rx), dy = mulf(gy, test.ry);
            const float dw = mulf(gw, test.rx), dh = mulf(gh, test.ry);
            // All header glyph destinations in the frozen matrix are positive.
            // floor(start)..ceil(start+extent) contains both the uncut integer
            // copy and every clipped fragment without arbitrary dilation.
            const int left = static_cast<int>(std::floor(dx)), top_row = static_cast<int>(std::floor(dy));
            const int right = static_cast<int>(std::ceil(static_cast<double>(dx) + dw));
            const int bottom = static_cast<int>(std::ceil(static_cast<double>(dy) + dh));
            output.push_back({left + test.origin_x, top_row + test.origin_y, right - left, bottom - top_row});
        }
        x = addf(x, divf(mulf(static_cast<float>(glyph.advance_64), scale), 64));
    }
}
std::string_view header_label(UiControlId id) {
    switch (id.kind) {
    case UiControlKind::Workspace: return id.index == 0 ? "PLAY" : id.index == 1 ? "ROTARY" : "SERVICE";
    case UiControlKind::SaveControls: return "SAVE";
    case UiControlKind::LoadControls: return "LOAD";
    case UiControlKind::AudioSettings: return "AUDIO";
    case UiControlKind::MidiSettings: return "MIDI";
    case UiControlKind::Help: return "HELP";
    case UiControlKind::Panic: return "PANIC";
    case UiControlKind::Presentation: return "FLAT";
    default: return {};
    }
}
std::vector<SDL_Rect> header_glyph_destinations(const Case& test, const UiModel& model) {
    std::vector<SDL_Rect> result;
    if (!active(test)) return result;
    result.reserve(256);
    const auto scale = independent_scale(test);
    const auto& layout = model.layout();
    float title_left = layout.header.x, title_right = addf(layout.header.x, layout.header.width), flat_left = title_right;
    std::size_t common = 0;
    for (std::size_t i = 0; i < layout.control_count; ++i) {
        const auto& control = layout.controls[i];
        const auto label = header_label(control.id);
        if (label.empty()) continue;
        ++common;
        if (control.id.kind == UiControlKind::Workspace && control.id.index == 2)
            title_left = addf(addf(control.bounds.x, control.bounds.width), mulf(12, scale.sx));
        if (control.id.kind == UiControlKind::SaveControls) title_right = subf(control.bounds.x, mulf(12, scale.sx));
        if (control.id.kind == UiControlKind::Presentation) flat_left = control.bounds.x;
        const auto& b = control.label_bounds;
        float size = mulf(control.id.kind == UiControlKind::Workspace ? 18.0F : 11.5F, scale.f);
        size = std::min(size, divf(b.height, 1.2F));
        const float width = measured_width(label, size, font_data::kSerif);
        const float padding = mulf(3, scale.sx), available = subf(b.width, mulf(2, padding));
        if (width > available && width > 0) size = mulf(size, divf(std::max(0.1F, available), width));
        const float x = addf(b.x, divf(subf(b.width, measured_width(label, size, font_data::kSerif)), 2));
        const float y = addf(b.y, divf(subf(b.height, mulf(size, 1.2F)), 2));
        text_destinations(result, test, label, x, y, size, font_data::kSerif);
    }
    require(common == 10, "source-derived header text inventory has ten controls");
    const float middle = mulf(836, scale.sx);
    const float half_width = std::max(0.0F, std::min(subf(middle, title_left), subf(title_right, middle)));
    title_left = subf(middle, half_width); title_right = addf(middle, half_width);
    constexpr std::string_view title = "TONEWHEEL ATLAS";
    float size = mulf(42.75F, scale.f);
    const float natural = measured_width(title, size, font_data::kSerif);
    if (natural > subf(title_right, title_left)) size = mulf(size, divf(subf(title_right, title_left), natural));
    const float width = measured_width(title, size, font_data::kSerif);
    const float x = std::clamp(subf(middle, divf(width, 2)), title_left, std::max(title_left, subf(title_right, width)));
    const float y = mulf(11.5F, scale.sy);
    text_destinations(result, test, title, addf(x, scale.sx), addf(y, mulf(2, scale.sy)), size, font_data::kSerif);
    text_destinations(result, test, title, addf(x, scale.f), addf(y, scale.f), size, font_data::kSerif);
    text_destinations(result, test, title, x, subf(y, mulf(0.125F, scale.f)), size, font_data::kSerif);
    text_destinations(result, test, title, addf(x, scale.f), y, size, font_data::kSerif);
    text_destinations(result, test, title, x, y, size, font_data::kSerif);
    constexpr std::string_view caption = "NOMINAL DRY ORGAN";
    constexpr float gaps = static_cast<float>(caption.size() - 1);
    const float caption_half = std::max(0.0F, std::min(subf(middle, title_left),
        subf(std::min(title_right, subf(flat_left, mulf(10, scale.sx))), middle)));
    const float caption_width = std::min(mulf(374, scale.sx), mulf(2, caption_half));
    float caption_size = mulf(17, scale.f), natural_caption = measured_width(caption, caption_size, font_data::kSans);
    const float tracking = std::max(0.0F, divf(subf(caption_width, natural_caption), gaps));
    if (natural_caption > caption_width) {
        caption_size = mulf(caption_size, divf(caption_width, natural_caption));
        natural_caption = measured_width(caption, caption_size, font_data::kSans);
    }
    float cursor = subf(middle, divf(addf(natural_caption, mulf(gaps, tracking)), 2));
    for (std::size_t i = 0; i < caption.size(); ++i) {
        const auto glyph = caption.substr(i, 1);
        text_destinations(result, test, glyph, cursor, mulf(67.5F, scale.sy), caption_size, font_data::kSans);
        cursor = addf(cursor, addf(measured_width(glyph, caption_size, font_data::kSans), tracking));
    }
    require(result.size() <= 256, "fixed bounded header glyph-copy destination inventory");
    return result;
}
bool contains(SDL_Rect b, int x, int y) { return x >= b.x && y >= b.y && x < b.x + b.w && y < b.y + b.h; }
void check_clip(const Case& test, Frame& frame) {
    // SDL_RenderClear clears the entire target independently of caller state.
    const UiColor color = test.presentation == UiPresentation::Flat ? UiColor{18, 21, 20} : kUiWalnut;
    const Pixel clear{color.red, color.green, color.blue, color.alpha};
    bool contained = true;
    frame.visible_pixels = 0;
    for (int y = 0; y < frame.height; ++y) for (int x = 0; x < frame.width; ++x) {
        if (visible(frame.before, x, y)) ++frame.visible_pixels;
        else { contained = contained && frame.pixels[frame.at(x, y)] == clear; ++totals.protected_pixels; }
    }
    require(contained, "no paint beyond caller viewport/clip after full-target clear");
    if (frame.before.clipped && (frame.before.clip.w == 0 || frame.before.clip.h == 0)) {
        require(frame.visible_pixels == 0, "enabled zero clip remains empty");
        ++totals.empty_cases;
    } else require(frame.visible_pixels > 0, "declared nonempty caller intersection remains observable");
}
void same_frame(const Frame& a, const Frame& b, std::string_view message) {
    require(a.width == b.width && a.height == b.height && a.pixels == b.pixels &&
            a.model_before == b.model_before && a.model_after == b.model_after &&
            a.session_before == b.session_before && a.session_after == b.session_after &&
            a.hit_before == b.hit_before && a.hit_after == b.hit_after && a.backend == b.backend &&
            exact_transform(a.before, b.before) && exact_transform(a.after, b.after) &&
            a.helper.present == b.helper.present && a.helper.invoked == b.helper.invoked &&
            exact_transform(a.helper.before, b.helper.before) && exact_transform(a.helper.after, b.helper.after), message);
}
void check_companion(const Case& test, const UiModel& model, Frame& frame, const Frame& full) {
    require(test.clipped && frame.before.clipped && !full.before.clipped && frame.width == full.width &&
            frame.height == full.height && frame.model_before == full.model_before && frame.model_after == full.model_after &&
            frame.session_before == full.session_before && frame.hit_before == full.hit_before && frame.backend == full.backend &&
            equal(frame.before.viewport, full.before.viewport) && same_float(frame.before.sx, full.before.sx) &&
            same_float(frame.before.sy, full.before.sy) && frame.before.blend == full.before.blend,
            "uncut companion keeps identical model, output, viewport, scale, blend and backend");
    const auto glyphs = header_glyph_destinations(test, model);
    auto field = intrinsic_field(test); field.x += test.origin_x; field.y += test.origin_y;
    bool equal_quiet = true;
    for (int y = std::max(0, field.y); y < std::min(frame.height, field.y + field.h); ++y)
        for (int x = std::max(0, field.x); x < std::min(frame.width, field.x + field.w); ++x) {
            if (!visible(frame.before, x, y) || std::any_of(glyphs.begin(), glyphs.end(),
                [&](SDL_Rect glyph) { return contains(glyph, x, y); })) continue;
            equal_quiet = equal_quiet && frame.pixels[frame.at(x, y)] == full.pixels[full.at(x, y)];
            ++frame.quiet_pixels;
        }
    require(equal_quiet, "all source-derived quiet material pixels equal uncut companion exactly");
    if (test.clip_kind == "disjoint" || test.clip_request.w == 0 || test.clip_request.h == 0)
        require(frame.quiet_pixels == 0, "disjoint material and enabled-empty clips have no quiet material probe");
    else require(frame.quiet_pixels > 0, "every partial header clip has nonempty independent quiet probes");
    totals.quiet_clip_pixels += frame.quiet_pixels; ++totals.clip_companions;
}

void scenario(std::ostream& out, std::size_t index, const Case& c) {
    const auto spec = surface_spec(c);
    out << "\"case\":" << index << ",\"logical_size\":[" << c.width << ',' << c.height
        << "],\"output_size\":[" << spec.width << ',' << spec.height << "],\"scale\":[" << c.rx << ',' << c.ry
        << "],\"origin\":[" << c.origin_x << ',' << c.origin_y << "],\"clip_kind\":\"" << c.clip_kind
        << "\",\"clip_space\":\"" << (c.logical_clip ? "logical" : "physical") << "\",\"clip_request\":";
    rect(out, c.clip_request);
    out << ",\"requested_clip_enabled\":" << c.clipped << ",\"level\":" << c.level
        << ",\"route\":\"" << route_name(c.route) << "\",\"route_index\":" << static_cast<unsigned>(c.route)
        << ",\"pending\":" << c.pending << ",\"pending_route\":";
    if (c.pending) out << '"' << route_name(c.pending_route) << '"'; else out << "\"None\"";
    out << ",\"pending_route_index\":";
    if (c.pending) out << static_cast<unsigned>(c.pending_route); else out << -1;
    out << ",\"held\":" << c.held << ",\"edited_bank\":\"" << (edited_bank(c) == DrawbarBank::A ? 'A' : 'B')
        << "\",\"lower_route\":\"B\",\"lower_edited_bank\":\"B\",\"focus\":";
    control_id(out, c.focus);
    out << ",\"blend\":" << static_cast<unsigned>(c.blend) << ",\"workspace\":" << static_cast<unsigned>(c.workspace)
        << ",\"presentation\":" << static_cast<unsigned>(c.presentation) << ",\"active_reference\":" << active(c)
        << ",\"eligible_h1\":" << eligible(c) << ",\"resource_crop\":" << c.resource;
}
void stream(std::size_t index, const Case& test, const Frame& frame, std::string_view variant) {
    std::ostringstream out;
    out << std::boolalpha << std::setprecision(std::numeric_limits<float>::max_digits10)
        << "{\"schema\":1,\"protocol\":\"" << protocol << "\",";
    scenario(out, index, test);
    out << ",\"variant\":\"" << variant << "\",\"width\":" << frame.width << ",\"height\":" << frame.height
        << ",\"viewport\":"; rect(out, frame.before.viewport);
    out << ",\"clip\":"; rect(out, frame.before.clip);
    out << ",\"logical_viewport\":"; rect(out, frame.before.logical_viewport);
    out << ",\"logical_clip\":"; rect(out, frame.before.logical_clip);
    out << ",\"clip_enabled\":" << frame.before.clipped << ",\"renderer_before\":";
    transform_record(out, frame.before); out << ",\"renderer_after\":"; transform_record(out, frame.after);
    out << ",\"model_before\":" << frame.model_before << ",\"model_after\":" << frame.model_after
        << ",\"session_before\":" << frame.session_before << ",\"session_after\":" << frame.session_after
        << ",\"hit_before\":" << frame.hit_before << ",\"hit_after\":" << frame.hit_after
        << ",\"info\":" << info_record() << ",\"backend\":" << frame.backend << ",\"helper_probe\":{\"present\":"
        << frame.helper.present << ",\"invoked\":" << frame.helper.invoked << ",\"bounds\":";
    rect(out, frame.helper.bounds);
    out << ",\"composition_scale\":[" << frame.helper.scale.sx << ',' << frame.helper.scale.sy << ',' << frame.helper.scale.f
        << "],\"before\":"; transform_record(out, frame.helper.before);
    out << ",\"after\":"; transform_record(out, frame.helper.after);
    out << ",\"unchanged\":true},\"checks\":{\"transform_unchanged\":true,\"model_unchanged\":true,\"session_unchanged\":true,"
           "\"hit_unchanged\":true,\"clip_containment\":true,\"deterministic_repaint\":true,\"inactive_classification\":true,"
           "\"clip_companion_checked\":" << (test.clipped && variant == "main")
        << ",\"after_all_repeat_checked\":" << (variant == "after-all") << ",\"fresh_repeat_checked\":" << (variant == "fresh")
        << "},\"visible_clip_pixels\":" << frame.visible_pixels << ",\"quiet_clip_pixels\":" << frame.quiet_pixels
        << ",\"history_states\":" << (variant == "after-all" ? case_count : 0)
        << ",\"bytes\":" << frame.pixels.size() * sizeof(Pixel) << "}\n";
    const auto header = out.str();
    require(header.size() < 512 * 1024, "bounded JSON header");
    std::cout << header;
    std::cout.write(reinterpret_cast<const char*>(frame.pixels.data()),
                    static_cast<std::streamsize>(frame.pixels.size() * sizeof(Pixel)));
    std::cout.flush();
    require(static_cast<bool>(std::cout), "write one JSON line followed by exact bounded RGBA bytes");
}
Frame after_all(Target& target, const std::array<Case, case_count>& fixtures, const Frame& original) {
    for (const auto& test : fixtures) { (void)target.paint(state_for(test), false); ++totals.history_states; }
    auto repeated = target.paint(state_for(fixtures[46]));
    same_frame(original, repeated, "case46 is byte/state identical after all 48 copied states on one renderer");
    check_clip(fixtures[46], repeated); ++totals.history_repaints;
    return repeated;
}
} // namespace

int main(int argc, char* argv[]) {
    SDL_SetMainReady();
    std::size_t current_case = case_count;
    try {
        const auto fixtures = cases();
        if (argc == 2 && std::string_view(argv[1]) == "--list") {
            std::cout << std::boolalpha << std::setprecision(std::numeric_limits<float>::max_digits10)
                << "{\"schema\":1,\"protocol\":\"" << protocol << "\",\"cases\":" << fixtures.size() << ",\"inventory\":[";
            for (std::size_t i = 0; i < fixtures.size(); ++i) {
                if (i) std::cout << ',';
                std::cout << '{'; scenario(std::cout, i, fixtures[i]); std::cout << '}';
            }
            std::cout << "]}\n";
            require(static_cast<bool>(std::cout), "write fixed inventory");
            return EXIT_SUCCESS;
        }
        std::size_t selected = fixtures.size();
        std::string_view variant = "main";
        if (argc != 1) {
            require((argc == 3 || argc == 4) && std::string_view(argv[1]) == "--case", "expected --case INDEX [--uncut|--after-all|--fresh] or --list");
            const std::string_view value(argv[2]);
            const auto parsed = std::from_chars(value.data(), value.data() + value.size(), selected);
            require(parsed.ec == std::errc{} && parsed.ptr == value.data() + value.size() && selected < fixtures.size(), "bounded case index");
            if (argc == 4) {
                const std::string_view option(argv[3]);
                if (option == "--uncut") { require(fixtures[selected].clipped, "uncut companion requires a declared clipped case"); variant = "uncut"; }
                else if (option == "--after-all") { require(selected == 46, "history export belongs to case46"); variant = "after-all"; }
                else if (option == "--fresh") { require(selected == 46, "fresh export belongs to case46"); variant = "fresh"; }
                else require(false, "unknown case variant");
            }
#ifdef _WIN32
            require(_setmode(_fileno(stdout), _O_BINARY) != -1, "binary frame stdout");
#endif
        }
        require(SDL_Init(0) == 0, "initialize SDL without audio or a window");
        {
            // The anchor exists before any default-matrix states. Later all 48
            // copied states pass through this same canonical target; renderer
            // changes caused by the helper cannot be hidden by reconstruction.
            std::unique_ptr<Target> history;
            Frame original46;
            if (selected == fixtures.size() || variant == "after-all" || variant == "fresh") {
                history = std::make_unique<Target>(fixtures[46]);
                original46 = history->paint(state_for(fixtures[46]));
            }
            if (variant == "after-all") {
                current_case = 46;
                auto repeated = after_all(*history, fixtures, original46);
                same_frame(repeated, history->paint(state_for(fixtures[46])), "history export retains deterministic repaint");
                stream(46, fixtures[46], repeated, variant);
            } else if (variant == "fresh") {
                current_case = 46;
                Target fresh(fixtures[46]); auto frame = fresh.paint(state_for(fixtures[46]));
                same_frame(original46, frame, "case46 matches a fresh renderer");
                same_frame(frame, fresh.paint(state_for(fixtures[46])), "fresh export retains deterministic repaint");
                check_clip(fixtures[46], frame); ++totals.fresh_repaints;
                stream(46, fixtures[46], frame, variant);
            } else {
                for (std::size_t index = 0; index < fixtures.size(); ++index) {
                    if (selected != fixtures.size() && index != selected) continue;
                    current_case = index;
                    const auto& test = fixtures[index]; const auto model = state_for(test);
                    Target target(test, variant == "uncut"); auto frame = target.paint(model);
                    check_clip(test, frame);
                    same_frame(frame, target.paint(model), "deterministic same-renderer repaint"); ++totals.repaints;
                    if (test.clipped && variant != "uncut") {
                        Target companion(test, true); const auto full = companion.paint(model);
                        check_companion(test, model, frame, full); ++totals.clipped_cases;
                    }
                    if (!active(test)) ++totals.inactive_cases;
                    if (selected != fixtures.size()) stream(index, test, frame, variant);
                    ++totals.cases;
                }
                if (selected == fixtures.size()) {
                    current_case = 46;
                    (void)after_all(*history, fixtures, original46);
                    Target fresh(fixtures[46]);
                    same_frame(original46, fresh.paint(state_for(fixtures[46])), "case46 is identical on a fresh renderer after all states");
                    ++totals.fresh_repaints;
                    require(totals.cases == 48 && totals.repaints == 48 && totals.clip_companions == 16 &&
                            totals.history_states == 48 && totals.history_repaints == 1 && totals.fresh_repaints == 1,
                            "complete literal case, companion, deterministic and history inventories");
                }
            }
        }
        SDL_Quit();
        if (selected == fixtures.size())
            std::cout << "{\"schema\":1,\"protocol\":\"" << protocol << "\",\"status\":\"passed\",\"cases\":" << totals.cases
                << ",\"checks\":" << totals.checks << ",\"paintings\":" << totals.paintings
                << ",\"clipped_cases\":" << totals.clipped_cases << ",\"empty_cases\":" << totals.empty_cases
                << ",\"inactive_cases\":" << totals.inactive_cases << ",\"protected_pixels\":" << totals.protected_pixels
                << ",\"deterministic_repaints\":" << totals.repaints << ",\"clip_companions\":" << totals.clip_companions
                << ",\"quiet_clip_pixels\":" << totals.quiet_clip_pixels << ",\"history_states\":" << totals.history_states
                << ",\"history_repaints\":" << totals.history_repaints << ",\"fresh_repaints\":" << totals.fresh_repaints
                << ",\"helper_present\":" << (h1_fixture_helper_present<Drawing> ? "true" : "false")
                << ",\"helper_probes\":" << totals.helper_probes
                << ",\"backend\":\"SDL software surface; copied state; no audio/window\"}\n";
        return EXIT_SUCCESS;
    } catch (const std::exception& error) {
        std::cerr << "Header material fixture failed in case " << current_case << ": " << error.what() << '\n';
        SDL_Quit();
        return EXIT_FAILURE;
    }
}

