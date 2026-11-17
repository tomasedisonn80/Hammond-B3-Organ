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
#include <utility>
#include <vector>

#ifdef _WIN32
#include <cstdio>
#include <fcntl.h>
#include <io.h>
#endif

// Build this IDENTICAL fixture before and after P1. The real painter is included
// exactly once so its private helper can be observed without a production hook.
// Do not also compile InstrumentView.cpp into this executable. The dependent
// lookup below works against genuine pre-P1 source, where the helper is absent.
#include "../InstrumentView.cpp"

namespace hammond::standalone {
template <typename Drawer>
constexpr bool p1_fixture_helper_present = requires(Drawer& drawing, UiRect bounds,
                                                   ReferenceCompositionScale scale) {
    reference_performance_p1_material(drawing, bounds, scale);
};
template <typename Drawer>
bool p1_fixture_invoke_helper(Drawer& drawing, UiRect bounds, ReferenceCompositionScale scale) {
    if constexpr (p1_fixture_helper_present<Drawer>) {
        reference_performance_p1_material(drawing, bounds, scale);
        return true;
    } else {
        return false;
    }
}
} // namespace hammond::standalone

// Frozen P1 section 5. There is no field oracle, alternate before painter,
// candidate-derived material mask, source hash gate or image dependency here.
// JSON is one newline-terminated UTF-8 object, followed by exactly `bytes`
// row-major RGBA bytes (R,G,B,A; no pitch padding, trailer or subsequent object).
// --list inventories every export, including companions and state witnesses.
namespace {
using namespace hammond;
using namespace hammond::standalone;
using Pixel = std::array<std::uint8_t, 4>;
static_assert(sizeof(Pixel) == 4);
static_assert(sizeof(float) == 4 && std::numeric_limits<float>::is_iec559);
constexpr std::string_view protocol = "performance-plate-p1-v1";
constexpr std::size_t main_count = 24, companion_count = 5, scenario_count = 34;
constexpr int maximum_width = 3866, maximum_height = 2194;
constexpr Pixel incoming_color{17, 23, 31, 127};
constexpr Pixel mask_white{255, 255, 255, 255};
constexpr Pixel focus_cyan{165, 228, 223, 255};

struct Totals {
    std::size_t cases{}, checks{}, paintings{}, main_cases{}, clipped_cases{}, empty_cases{}, inactive_cases{};
    std::size_t protected_pixels{}, repaints{}, clip_companions{}, quiet_clip_pixels{};
    std::size_t history_states{}, history_repaints{}, fresh_repaints{}, helper_probes{};
    std::size_t eligibility_witnesses{}, opaque_probes{}, opaque_pixels{}, text_runs{}, glyph_core_pixels{};
    std::size_t nonempty_text_runs{}, focus_witnesses{}, focus_pixels{};
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
    bool clipped{}, resource{};
    std::string_view clip_kind{"disabled"};
    SDL_Rect clip_request{};
    PresetSelection route{PresetSelection::BankB};
    UiControlId focus{UiControlKind::ManualDrawbar, Manual::Upper, DrawbarBank::B, 4};
    UiWorkspace workspace{UiWorkspace::Play};
    UiPresentation presentation{UiPresentation::Dimensional};
    SDL_BlendMode blend{SDL_BLENDMODE_BLEND};
    PercussionSettings percussion{true, PercussionHarmonic::Second, PercussionVolume::Normal, PercussionDecay::Slow};
    double expression{0.625};
    std::array<std::uint8_t, kPedalDrawbarCount> pedals{3, 7};
};
bool active(const Case& c) {
    return c.workspace == UiWorkspace::Play && c.presentation == UiPresentation::Dimensional &&
           c.width >= 1400 && c.width <= 8192 && c.height >= 820 && c.height <= 8192;
}
bool eligible(const Case& c) {
    return active(c) && std::isfinite(c.rx) && std::isfinite(c.ry) &&
           c.rx > 0 && c.ry > 0 && c.rx <= 2 && c.ry <= 2;
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
UiRect canonical(const Case& c, UiRect r) {
    const auto s = independent_scale(c);
    const float x = mulf(r.x, s.sx), y = mulf(r.y, s.sy);
    return {x, y, subf(mulf(addf(r.x, r.width), s.sx), x),
            subf(mulf(addf(r.y, r.height), s.sy), y)};
}
UiRect independent_panel(const Case& c) { return canonical(c, {72, 125, 1044, 139}); }
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
std::array<Case, main_count> cases() {
    std::array<Case, main_count> result{};
    const auto percussion_focus = [](std::uint8_t index) {
        return UiControlId{UiControlKind::Percussion, Manual::Upper, DrawbarBank::A, index};
    };
    result[1].width = 1400; result[1].height = 820; result[1].focus = percussion_focus(0);
    result[1].percussion.enabled = false;
    result[2].width = 1920; result[2].height = 1080; result[2].focus = percussion_focus(1);
    result[2].percussion.harmonic = PercussionHarmonic::Third;
    result[3].width = 1920; result[3].height = 820; result[3].focus = percussion_focus(2);
    result[3].percussion.volume = PercussionVolume::Soft;
    result[4].width = 1400; result[4].height = 1080; result[4].focus = percussion_focus(3);
    result[4].percussion.decay = PercussionDecay::Fast;
    result[5].rx = result[5].ry = 1.5F; result[5].origin_x = 13; result[5].origin_y = 17;
    result[5].focus = {UiControlKind::Expression}; result[5].expression = 0;
    result[6].rx = result[6].ry = 2; result[6].origin_x = -13; result[6].origin_y = -17;
    result[6].focus = {UiControlKind::PedalDrawbar, Manual::Upper, DrawbarBank::A, 0};
    result[6].pedals = {0, 8};
    result[7].rx = 1.25F; result[7].ry = 0.75F; result[7].origin_x = 13; result[7].origin_y = -17;
    result[7].focus = {UiControlKind::PedalDrawbar, Manual::Upper, DrawbarBank::A, 1};
    result[7].blend = SDL_BLENDMODE_NONE;
    result[8].rx = 2.01F; result[9].ry = 2.01F;
    result[10].rx = result[10].ry = 1.5F; result[10].origin_x = 13; result[10].origin_y = 17;
    result[11].rx = result[11].ry = 2; result[11].origin_x = -13; result[11].origin_y = 17;
    result[12].rx = 1.25F; result[12].ry = 0.75F; result[12].origin_x = -13; result[12].origin_y = -17;
    result[13].origin_x = 13; result[13].origin_y = -17;
    constexpr std::array<std::string_view, 4> edges{"left", "right", "top", "bottom"};
    for (std::size_t edge = 0; edge < edges.size(); ++edge) {
        auto& c = result[10 + edge]; c.clipped = true; c.clip_kind = edges[edge];
        const auto b = intrinsic_field(c);
        const std::array<SDL_Rect, 4> clips{{
            {b.x - 2, b.y - 2, 4, b.h + 4}, {b.x + b.w - 2, b.y - 2, 4, b.h + 4},
            {b.x - 2, b.y - 2, b.w + 4, 4}, {b.x - 2, b.y + b.h - 2, b.w + 4, 4}}};
        c.clip_request = clips[edge];
    }
    for (std::size_t index = 14; index <= 15; ++index) {
        auto& c = result[index]; c.clipped = true;
        const auto b = intrinsic_field(c);
        c.clip_kind = index == 14 ? "empty" : "disjoint";
        c.clip_request = index == 14 ? SDL_Rect{b.x, b.y, 0, 0} : SDL_Rect{b.x + b.w + 4, b.y + 4, 8, 8};
    }
    result[16].width = result[16].height = 8192; result[16].rx = result[16].ry = 2; result[16].resource = true;
    const auto resource = intrinsic_field(result[16]);
    result[16].origin_x = -resource.x; result[16].origin_y = -resource.y;
    constexpr std::array<std::array<float, 2>, 4> inactive{{{1399, 820}, {1400, 819}, {960, 700}, {1280, 900}}};
    for (std::size_t i = 0; i < inactive.size(); ++i) { result[17 + i].width = inactive[i][0]; result[17 + i].height = inactive[i][1]; }
    result[21].presentation = UiPresentation::Flat;
    result[22].workspace = UiWorkspace::Rotary; result[23].workspace = UiWorkspace::Service;
    return result;
}
struct Scenario { Case test; std::string id; std::string_view kind{"main"}; std::size_t source{}; };
std::array<Scenario, scenario_count> scenarios() {
    const auto main = cases();
    std::array<Scenario, scenario_count> result{};
    for (std::size_t i = 0; i < main_count; ++i) result[i] = {main[i], "main-" + std::to_string(i), "main", i};
    constexpr std::array<std::size_t, companion_count> clipped{10, 11, 12, 13, 15};
    for (std::size_t i = 0; i < clipped.size(); ++i) {
        const auto source = clipped[i]; Case uncut = main[source];
        uncut.clipped = false; uncut.clip_kind = "disabled"; uncut.clip_request = {};
        result[24 + i] = {uncut, "uncut-" + std::to_string(source), "uncut-companion", source};
    }
    result[29] = {main[0], "repeat-after-all-0", "after-all", 0};
    result[30] = {main[0], "repeat-fresh-0", "fresh", 0};
    constexpr std::array<PresetSelection, 3> routes{PresetSelection::BankA, PresetSelection::Cancel, PresetSelection::D};
    constexpr std::array<std::string_view, 3> names{"upper-applied-A", "upper-cancelled", "upper-fixed-D"};
    for (std::size_t i = 0; i < routes.size(); ++i) {
        Case witness = main[0]; witness.route = routes[i];
        result[31 + i] = {witness, std::string(names[i]), "eligibility-witness", 0};
    }
    return result;
}

template <typename Range, typename Writer>
void array(std::ostream& out, const Range& values, Writer write) {
    out << '[';
    for (std::size_t index = 0; index < values.size(); ++index) {
        if (index != 0) out << ',';
        write(out, values[index]);
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
    // Public focus traversal happens in Play; switching workspaces then lets
    // the real model select its visible workspace focus and retain Play memory.
    require(model.resize(test.width, test.height) && model.set_presentation(test.presentation), "fixed public layout setup");
    SessionSnapshot snapshot;
    snapshot.controls = model.view().controls;
    for (auto& manual : snapshot.controls.drawbars) for (auto& bank : manual) bank.fill(4);
    snapshot.controls.expression = test.expression;
    snapshot.controls.pedal_drawbars = test.pedals;
    snapshot.controls.percussion = test.percussion;
    ControlState applied;
    require(applied.restore(snapshot.controls) && applied.select_preset(Manual::Upper, test.route) &&
            applied.select_preset(Manual::Lower, PresetSelection::BankB), "complete literal applied routes");
    snapshot.controls = applied.snapshot();
    snapshot.held_keys[0][24] = snapshot.held_keys[1][36] = snapshot.held_pedals[12] = true;
    snapshot.frame_clock = 38400; snapshot.sample_rate = 48000; snapshot.peak = 0.125F;
    snapshot.prepared = snapshot.running = true; snapshot.publication_revision = 4;
    model.observe(snapshot);
    require(model.activate({UiControlKind::EditBank, Manual::Upper, DrawbarBank::B}).count == 0 &&
            model.activate({UiControlKind::EditBank, Manual::Lower, DrawbarBank::B}).count == 0,
            "both edited B banks emit no musical commands");
    for (unsigned step = 0; step < 72 && model.view().focus != test.focus; ++step)
        require(model.key({UiKey::Tab, true}).count == 0 && model.key({UiKey::Tab, false}).count == 0,
                "ordinary semantic focus traversal emits no musical commands");
    require(model.view().focus == test.focus, "literal requested Play focus reached");
    require(model.set_workspace(test.workspace), "public workspace transition");
    require(model.view().edited_banks == std::array{DrawbarBank::B, DrawbarBank::B}, "both edited banks remain B in every witness");
    require(model.view().controls == snapshot.controls && session_record(model.view().applied) == session_record(snapshot) &&
            !model.view().controls_pending, "complete fixed desired/applied snapshots without pending requests");
    require(model.view().controls.percussion == test.percussion && model.view().applied.controls.percussion == test.percussion,
            "stored percussion is independent of Upper eligibility");
    require(reference_composition_active(model.layout()) == active(test), "independent reference eligibility agrees with public layout");
    require(model.layout().control_count == 68 && model.layout().manual_keys.size() * kManualKeyCount +
            model.layout().pedal_keys.size() == 147, "68 stored controls and 147 playing keys");
    require(std::count_if(model.layout().controls.begin(), model.layout().controls.end(), [](const auto& control) {
        return control.id.kind == UiControlKind::PresetKey;
    }) == 24, "24 stored preset controls");
    const auto visible_controls = std::count_if(model.layout().controls.begin(), model.layout().controls.end(),
        [&](const auto& control) { return ui_control_visible(model.layout(), control.id); });
    require(visible_controls == (test.workspace == UiWorkspace::Play ? 68 : 10), "unchanged workspace control visibility");
    if (active(test)) {
        const auto expected = independent_panel(test), actual = model.layout().performance_panel;
        require(actual.x == expected.x && actual.y == expected.y && actual.width == expected.width && actual.height == expected.height,
                "independent binary32 mapped performance panel equals live layout");
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
    info.status_message = "Frozen performance plate qualification";
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

// A span is [row, first_x, end_x), in physical OUTPUT coordinates. Every span
// is sorted, disjoint, nonempty and bounded by the exported width/height.
struct Span {
    int row{}, first{}, end{};
    bool operator==(const Span&) const noexcept = default;
};
std::size_t span_pixels(const std::vector<Span>& spans) {
    std::size_t result = 0;
    for (const auto span : spans) result += static_cast<std::size_t>(span.end - span.first);
    return result;
}
std::vector<Span> make_spans(std::vector<std::size_t> positions, int width) {
    std::sort(positions.begin(), positions.end());
    positions.erase(std::unique(positions.begin(), positions.end()), positions.end());
    std::vector<Span> result;
    for (const auto at : positions) {
        const auto stride = static_cast<std::size_t>(width);
        const int row = static_cast<int>(at / stride), x = static_cast<int>(at % stride);
        if (!result.empty() && result.back().row == row && result.back().end == x) ++result.back().end;
        else result.push_back({row, x, x + 1});
    }
    return result;
}
struct HelperProbe {
    bool present{}, invoked{};
    UiRect bounds{};
    ReferenceCompositionScale scale{};
    Transform before{}, after{};
};
struct TextRun {
    std::string id, text;
    UiRect box{};
    float requested{}, padding{}, x{}, top{}, size{};
    TextFace face{};
    Pixel color{};
    std::vector<SDL_Rect> destinations;
    std::vector<Span> cores;
};
struct OpaqueProbe {
    std::string id;
    std::vector<UiRect> regions;
    std::vector<Span> samples;
};
struct Witnesses {
    bool full_required{};
    std::vector<TextRun> text;
    std::vector<OpaqueProbe> opaque;
    UiControlId focus_id{};
    UiRect focus_bounds{};
    std::vector<UiRect> focus_regions;
    std::vector<Span> focus_expected, focus_actual;
};
struct Frame {
    int width{}, height{};
    Transform before{}, after{};
    HelperProbe helper{};
    Witnesses witnesses;
    std::vector<Pixel> pixels;
    std::string model_before, model_after, session_before, session_after, hit_before, hit_after, backend;
    std::size_t visible_pixels{}, quiet_pixels{}, history_states{};
    bool companion_checked{}, after_all_checked{}, fresh_checked{};
    std::size_t at(int x, int y) const {
        return static_cast<std::size_t>(y) * static_cast<std::size_t>(width) + static_cast<std::size_t>(x);
    }
};

class Target {
public:
    explicit Target(const Case& test) : test_(test), spec_(surface_spec(test)),
        surface_(SDL_CreateRGBSurfaceWithFormat(0, spec_.width, spec_.height, 32, SDL_PIXELFORMAT_RGBA32), SDL_FreeSurface),
        renderer_(surface_ ? SDL_CreateSoftwareRenderer(surface_.get()) : nullptr, SDL_DestroyRenderer), drawing_(renderer_.get()) {
        require(surface_ && renderer_, "create bounded software target");
        std::string error;
        require(drawing_.initialize(error), "initialize unchanged font/art textures");
        configure(test);
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
    // Reconfiguration is also used for the history witness. Its allocated
    // canonical output stays fixed while all declared transforms and copied
    // states pass through the SAME renderer before case0 is restored.
    void configure(const Case& test) {
        test_ = test;
        const auto desired = surface_spec(test);
        require(SDL_RenderSetScale(renderer_.get(), 1, 1) == 0 &&
                SDL_RenderSetViewport(renderer_.get(), &desired.viewport) == 0 &&
                SDL_RenderSetClipRect(renderer_.get(), nullptr) == 0, "install physical viewport and disabled clip");
        if (test.clipped) require(SDL_RenderSetClipRect(renderer_.get(), &test.clip_request) == 0, "install frozen physical clip at scale one");
        require(SDL_RenderSetScale(renderer_.get(), test.rx, test.ry) == 0 &&
                SDL_SetRenderDrawBlendMode(renderer_.get(), test.blend) == 0, "install declared scales and incoming blend");
        const auto actual = transform(renderer_.get());
        require(same_float(actual.sx, test.rx) && same_float(actual.sy, test.ry) && equal(actual.viewport, desired.viewport) &&
                actual.clipped == test.clipped && equal(actual.clip, test.clipped ? test.clip_request : SDL_Rect{}) &&
                actual.blend == test.blend, "queried physical renderer state equals the frozen scenario");
        if (test.clipped && (test.clip_request.w == 0 || test.clip_request.h == 0))
            require(actual.clipped && (actual.clip.w == 0 || actual.clip.h == 0), "zero clip remains enabled and empty");
    }
    Frame paint(const UiModel& model, bool probe_helper = true) {
        require(SDL_SetRenderDrawColor(renderer_.get(), incoming_color[0], incoming_color[1], incoming_color[2], incoming_color[3]) == 0,
                "install fixed incoming draw color");
        Frame frame;
        frame.width = spec_.width; frame.height = spec_.height; frame.backend = backend_;
        frame.helper.present = p1_fixture_helper_present<Drawing>;
        frame.helper.bounds = independent_inset(test_); frame.helper.scale = independent_scale(test_);
        frame.helper.before = transform(renderer_.get());
        if (probe_helper && eligible(test_) && frame.helper.present) {
            frame.helper.invoked = p1_fixture_invoke_helper(drawing_, frame.helper.bounds, frame.helper.scale);
            require(frame.helper.invoked, "present eligible P1 helper is directly observed");
            ++totals.helper_probes;
        }
        frame.helper.after = transform(renderer_.get());
        require(exact_transform(frame.helper.before, frame.helper.after), "private P1 helper restores color and complete renderer state");
        // Helper-only pixels cannot become a before image or permission mask:
        // the genuine whole painter clears its target unconditionally below.
        frame.before = transform(renderer_.get());
        frame.model_before = model_record(model); frame.session_before = session_record(model.view().applied);
        frame.hit_before = hit_record(model);
        paint_instrument(drawing_, model, fixed_info());
        frame.after = transform(renderer_.get());
        frame.model_after = model_record(model); frame.session_after = session_record(model.view().applied);
        frame.hit_after = hit_record(model);
        require(same_transform(frame.before, frame.after), "paint preserves scales, physical/logical viewport/clip, enable and blend");
        require(frame.model_before == frame.model_after && frame.session_before == frame.session_after &&
                frame.hit_before == frame.hit_after, "paint preserves all copied model, layout, key/hit, focus and musical state");
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
    template <typename Paint>
    std::vector<Span> mask(Paint paint, const std::vector<SDL_Rect>& envelopes) {
        const auto before = transform(renderer_.get());
        drawing_.clear({0, 0, 0, 0});
        paint(drawing_);
        require(SDL_RenderFlush(renderer_.get()) == 0 && SDL_LockSurface(surface_.get()) == 0, "read independent white witness mask");
        std::vector<std::size_t> positions;
        const auto* input = static_cast<const std::uint8_t*>(surface_->pixels);
        for (const auto bounds : envelopes)
            for (int y = std::max(0, bounds.y); y < std::min(spec_.height, bounds.y + bounds.h); ++y)
                for (int x = std::max(0, bounds.x); x < std::min(spec_.width, bounds.x + bounds.w); ++x) {
                    const auto* p = input + static_cast<std::size_t>(y) * static_cast<std::size_t>(surface_->pitch) +
                        static_cast<std::size_t>(x) * sizeof(Pixel);
                    if (Pixel{p[0], p[1], p[2], p[3]} == mask_white)
                        positions.push_back(static_cast<std::size_t>(y) * static_cast<std::size_t>(spec_.width) + static_cast<std::size_t>(x));
                }
        SDL_UnlockSurface(surface_.get());
        require(SDL_SetRenderDrawColor(renderer_.get(), before.color[0], before.color[1], before.color[2], before.color[3]) == 0 &&
                exact_transform(before, transform(renderer_.get())), "fixture masks preserve complete incoming renderer state");
        return make_spans(std::move(positions), spec_.width);
    }
private:
    Case test_;
    SurfaceSpec spec_;
    std::unique_ptr<SDL_Surface, decltype(&SDL_FreeSurface)> surface_;
    std::unique_ptr<SDL_Renderer, decltype(&SDL_DestroyRenderer)> renderer_;
    Drawing drawing_;
    std::string backend_;
};

float measured_width(std::string_view value, float size, const font_data::Atlas& atlas) {
    const float scale = divf(size, static_cast<float>(atlas.pixel_height));
    float width = 0;
    for (const char character : value)
        width = addf(width, divf(mulf(static_cast<float>(font_data::glyph(atlas, static_cast<unsigned char>(character)).advance_64), scale), 64));
    return width;
}
SDL_Rect destination_envelope(const Case& test, UiRect logical) {
    const float x = mulf(logical.x, test.rx), y = mulf(logical.y, test.ry);
    const float w = mulf(logical.width, test.rx), h = mulf(logical.height, test.ry);
    const int left = static_cast<int>(std::floor(x)), top = static_cast<int>(std::floor(y));
    const int right = static_cast<int>(std::ceil(static_cast<double>(x) + w));
    const int bottom = static_cast<int>(std::ceil(static_cast<double>(y) + h));
    return {left + test.origin_x, top + test.origin_y, right - left, bottom - top};
}
std::vector<SDL_Rect> region_envelopes(const Case& test, const std::vector<UiRect>& regions) {
    std::vector<SDL_Rect> result;
    for (const auto region : regions) {
        auto r = destination_envelope(test, region);
        // Merely a read window for a fixture-owned white mask, never an
        // allowance for changed pixels. Include SDL's one-pixel min extent.
        --r.x; --r.y; r.w += 2; r.h += 2; result.push_back(r);
    }
    return result;
}
void text_destinations(TextRun& run, const Case& test) {
    const auto& atlas = run.face == TextFace::Sans ? font_data::kSans : font_data::kSerif;
    const float scale = divf(run.size, static_cast<float>(atlas.pixel_height));
    const float baseline = addf(run.top, mulf(static_cast<float>(atlas.ascent), scale));
    float x = run.x;
    for (const char character : run.text) {
        const auto& glyph = font_data::glyph(atlas, static_cast<unsigned char>(character));
        if (glyph.width != 0 && glyph.height != 0) {
            const int px = mulf(static_cast<float>(glyph.width), scale) < 1 ? 2 : 0;
            const int py = mulf(static_cast<float>(glyph.height), scale) < 1 ? 2 : 0;
            const UiRect destination{
                addf(x, mulf(static_cast<float>(glyph.bearing_x - px), scale)),
                addf(baseline, mulf(static_cast<float>(glyph.bearing_y - py), scale)),
                mulf(static_cast<float>(glyph.width + 2 * px), scale),
                mulf(static_cast<float>(glyph.height + 2 * py), scale)};
            run.destinations.push_back(destination_envelope(test, destination));
        }
        x = addf(x, divf(mulf(static_cast<float>(glyph.advance_64), scale), 64));
    }
}
TextRun literal_text(const Case& test, std::string id, std::string value, UiRect box,
                     float requested, TextFace face, Pixel color, float padding) {
    TextRun run;
    run.id = std::move(id); run.text = std::move(value); run.box = box;
    run.requested = requested; run.padding = padding; run.face = face; run.color = color;
    const auto& atlas = face == TextFace::Sans ? font_data::kSans : font_data::kSerif;
    run.size = std::min(requested, divf(box.height, 1.2F));
    const float width = measured_width(run.text, run.size, atlas), available = subf(box.width, mulf(2, padding));
    if (width > available && width > 0) run.size = mulf(run.size, divf(std::max(0.1F, available), width));
    run.x = addf(box.x, divf(subf(box.width, measured_width(run.text, run.size, atlas)), 2));
    run.top = addf(box.y, divf(subf(box.height, mulf(run.size, 1.2F)), 2));
    text_destinations(run, test);
    return run;
}
bool same_rect(UiRect a, UiRect b) {
    return same_float(a.x, b.x) && same_float(a.y, b.y) && same_float(a.width, b.width) && same_float(a.height, b.height);
}
const UiControlGeometry& control_geometry(const UiModel& model, UiControlId id) {
    const auto& controls = model.layout().controls;
    const auto found = std::find_if(controls.begin(), controls.end(), [&](const auto& g) { return g.id == id; });
    require(found != controls.end(), "literal semantic control has public geometry");
    return *found;
}
void geometry_matches(const Case& test, const UiControlGeometry& actual, UiRect bounds, UiRect label, UiRect value, UiRect track = {}) {
    require(same_rect(actual.bounds, canonical(test, bounds)) && same_rect(actual.label_bounds, canonical(test, label)) &&
            same_rect(actual.value_bounds, canonical(test, value)) && same_rect(actual.track, canonical(test, track)),
            "live control rectangles equal independently frozen canonical endpoints");
}
Witnesses witness_spec(const Case& test, const UiModel& model) {
    Witnesses result;
    if (!active(test)) return result;
    result.full_required = !test.clipped && !test.resource;
    const auto scale = independent_scale(test);
    constexpr Pixel brass{214, 182, 124, 255}, ivory{242, 231, 207, 255}, dark{33, 28, 21, 255};
    const auto add_text = [&](std::string id, std::string text, UiRect box, float size, TextFace face, Pixel color, float padding) {
        result.text.push_back(literal_text(test, std::move(id), std::move(text), box, mulf(size, scale.f), face, color, mulf(padding, scale.sx)));
    };
    const auto add_probe = [&](std::string id, UiRect region) { result.opaque.push_back({std::move(id), {region}, {}}); };
    const auto heading = [&](std::string id, std::string text, UiRect nominal, float size) {
        const auto box = canonical(test, nominal);
        add_text(id, text, box, size, TextFace::Serif, brass, 3);
        const float gap = addf(divf(measured_width(text, mulf(size, scale.f), font_data::kSerif), 2), mulf(14, scale.sx));
        const float middle = addf(box.x, divf(box.width, 2));
        require(gap < subf(divf(box.width, 2), mulf(16, scale.sx)), "both frozen heading rule segments exist");
        const float y = addf(box.y, divf(box.height, 2));
        const float left = addf(box.x, mulf(9, scale.sx));
        add_probe(id + "-rule-left", {left, y, subf(subf(subf(middle, gap), box.x), mulf(9, scale.sx)), scale.sy});
        add_probe(id + "-rule-right", {addf(middle, gap), y,
            subf(subf(subf(addf(box.x, box.width), mulf(9, scale.sx)), middle), gap), scale.sy});
    };
    heading("percussion-heading", "PERCUSSION", {90, 136, 448, 26}, 15);
    heading("expression-heading", "NOMINAL EXPRESSION / PEDAL MIXTURES", {578, 136, 514, 26}, 14);
    const auto& applied = model.view().applied.controls;
    const bool upper_b = applied.route_enabled[0] && applied.fixed_registrations[0] == FixedRegistration::None &&
        applied.selected_banks[0] == DrawbarBank::B;
    add_text("eligibility", upper_b ? "UPPER B ROUTE ACTIVE" : "REQUIRES UPPER B", canonical(test, {90, 248, 448, 14}),
             12, TextFace::Sans, upper_b ? Pixel{157, 187, 143, 255} : Pixel{166, 159, 142, 255}, 3);
    constexpr std::array<float, 4> lefts{164, 418, 256, 337};
    constexpr std::array<std::string_view, 4> labels{"PERC", "HARM", "VOL", "DECAY"};
    const std::array<std::string_view, 4> values{
        test.percussion.enabled ? "ON" : "OFF", test.percussion.harmonic == PercussionHarmonic::Second ? "2ND" : "3RD",
        test.percussion.volume == PercussionVolume::Normal ? "NORM" : "SOFT",
        test.percussion.decay == PercussionDecay::Slow ? "SLOW" : "FAST"};
    for (std::size_t i = 0; i < lefts.size(); ++i) {
        const auto& g = control_geometry(model, {UiControlKind::Percussion, Manual::Upper, DrawbarBank::A, static_cast<std::uint8_t>(i)});
        geometry_matches(test, g, {lefts[i], 177, 74, 52}, {lefts[i] - 2, 233, 78, 14}, {lefts[i] + 5, 183, 64, 38});
        add_text("percussion-" + std::to_string(i) + "-label", std::string(labels[i]), g.label_bounds, 13.5F, TextFace::Serif, ivory, 3);
        add_text("percussion-" + std::to_string(i) + "-value", std::string(values[i]), g.value_bounds, 20, TextFace::Serif, dark, 3);
        add_probe("percussion-" + std::to_string(i) + "-cap", {addf(g.bounds.x, mulf(12, scale.sx)),
            addf(g.bounds.y, mulf(44, scale.sy)), mulf(50, scale.sx), mulf(2, scale.sy)});
    }
    const auto& expression = control_geometry(model, {UiControlKind::Expression});
    geometry_matches(test, expression, {578, 165, 254, 85}, {582, 165, 246, 16}, {582, 232, 246, 16}, {594, 200, 222, 4});
    add_text("expression-label", "NOMINAL EXPRESSION", expression.label_bounds, 10.5F, TextFace::Sans, ivory, 3);
    add_text("expression-value", std::to_string(static_cast<int>(std::round(test.expression * 100.0))) + "%",
             expression.value_bounds, 11.5F, TextFace::Sans, brass, 3);
    const auto track = expression.track;
    const float handle = addf(track.x, mulf(static_cast<float>(test.expression), track.width));
    add_probe("expression-track", {addf(track.x, mulf(test.expression < 0.5 ? 100.0F : 10.0F, scale.sx)),
        addf(track.y, scale.sy), mulf(80, scale.sx), scale.sy});
    add_probe("expression-handle", {subf(handle, mulf(3, scale.sx)), subf(track.y, mulf(3, scale.sy)),
        mulf(6, scale.sx), mulf(6, scale.sy)});
    for (std::size_t i = 0; i < test.pedals.size(); ++i) {
        const float left = addf(850, mulf(128, static_cast<float>(i)));
        const auto& g = control_geometry(model, {UiControlKind::PedalDrawbar, Manual::Upper, DrawbarBank::A, static_cast<std::uint8_t>(i)});
        geometry_matches(test, g, {left, 165, 112, 85}, {left + 4, 165, 104, 16}, {left + 74, 200, 32, 40}, {left + 41, 193, 4, 43});
        add_text("pedal-" + std::to_string(i) + "-label", i == 0 ? "MIX 1" : "MIX 2", g.label_bounds, 11, TextFace::Sans, ivory, 2);
        add_text("pedal-" + std::to_string(i) + "-value", std::to_string(test.pedals[i]), g.value_bounds, 13, TextFace::Sans, brass, 3);
        const float center = addf(g.track.x, divf(g.track.width, 2));
        const float position = addf(g.track.y, divf(mulf(g.track.height, static_cast<float>(test.pedals[i])), 8));
        add_probe("pedal-" + std::to_string(i) + "-track", {subf(center, mulf(20, scale.sx)), addf(g.track.y, mulf(3, scale.sy)),
            mulf(2, scale.sx), subf(g.track.height, mulf(6, scale.sy))});
        add_probe("pedal-" + std::to_string(i) + "-cap", {subf(center, mulf(12, scale.sx)), subf(position, mulf(4, scale.sy)),
            mulf(24, scale.sx), mulf(3, scale.sy)});
    }
    add_probe("divider", canonical(test, {556, 145, 1, 100}));
    const auto panel = independent_panel(test);
    const std::array<float, 2> screw_x{addf(panel.x, mulf(7, scale.sx)), subf(addf(panel.x, panel.width), mulf(13, scale.sx))};
    const std::array<float, 2> screw_y{addf(panel.y, mulf(7, scale.sy)), subf(addf(panel.y, panel.height), mulf(13, scale.sy))};
    for (std::size_t row = 0; row < screw_y.size(); ++row) for (std::size_t column = 0; column < screw_x.size(); ++column)
        add_probe("screw-" + std::to_string(row) + "-" + std::to_string(column),
            {addf(screw_x[column], mulf(2, scale.sx)), addf(screw_y[row], mulf(2, scale.sy)), mulf(2, scale.sx), mulf(2, scale.sy)});
    result.focus_id = model.view().focus;
    result.focus_bounds = control_geometry(model, result.focus_id).bounds;
    const auto b = result.focus_bounds;
    const float tx = std::min(mulf(2, scale.sx), divf(b.width, 2));
    const float ty = std::min(mulf(2, scale.sy), divf(b.height, 2));
    result.focus_regions = {{b.x, b.y, b.width, ty}, {b.x, subf(addf(b.y, b.height), ty), b.width, ty},
        {b.x, addf(b.y, ty), tx, subf(b.height, mulf(2, ty))},
        {subf(addf(b.x, b.width), tx), addf(b.y, ty), tx, subf(b.height, mulf(2, ty))}};
    require(result.text.size() == 17 && result.opaque.size() == 19, "complete frozen 17 text and 19 opaque probe inventory");
    return result;
}

template <typename Check>
void every_sample(const Frame& frame, const std::vector<Span>& spans, Check check, std::string_view message) {
    bool valid = true;
    for (const auto span : spans) {
        require(span.row >= 0 && span.row < frame.height && span.first >= 0 && span.first < span.end && span.end <= frame.width,
                "every witness span is bounded and nonempty");
        for (int x = span.first; x < span.end; ++x) valid = valid && check(frame.pixels[frame.at(x, span.row)]);
    }
    require(valid, message);
}
void observe_witnesses(const Case& test, const UiModel& model, Target& target, Frame& frame) {
    frame.witnesses = witness_spec(test, model);
    auto& witnesses = frame.witnesses;
    if (!active(test)) return;
    // Each mask is generated solely from literal text/font/color/placement or
    // source-derived opaque geometry, never selected from candidate pixels.
    // The pinned Drawing/SDL text path retains its genuine clipped-copy rules.
    for (auto& run : witnesses.text) {
        run.cores = target.mask([&](Drawing& drawing) {
            drawing.text(run.text, run.x, run.top, run.size, {255, 255, 255, 255}, run.face);
        }, run.destinations);
        const auto count = span_pixels(run.cores);
        if (witnesses.full_required) require(count > 0, "each required literal text run has nonempty opaque glyph cores");
        every_sample(frame, run.cores, [&](Pixel actual) { return actual == run.color; },
                     "all independently rendered opaque glyph cores have exact literal RGBA");
        ++totals.text_runs; totals.glyph_core_pixels += count;
        if (count) ++totals.nonempty_text_runs;
    }
    for (auto& probe : witnesses.opaque) {
        probe.samples = target.mask([&](Drawing& drawing) {
            for (const auto region : probe.regions) drawing.rect(region, {255, 255, 255, 255});
        }, region_envelopes(test, probe.regions));
        const auto count = span_pixels(probe.samples);
        if (witnesses.full_required) require(count > 0, "every required opaque child/control probe is nonempty");
        every_sample(frame, probe.samples, [](Pixel actual) { return actual[3] == 255; }, "all child core probes remain opaque");
        ++totals.opaque_probes; totals.opaque_pixels += count;
    }
    witnesses.focus_expected = target.mask([&](Drawing& drawing) {
        for (const auto region : witnesses.focus_regions) drawing.rect(region, {255, 255, 255, 255});
    }, region_envelopes(test, witnesses.focus_regions));
    std::vector<std::size_t> actual_focus;
    for (std::size_t at = 0; at < frame.pixels.size(); ++at)
        if (frame.pixels[at] == focus_cyan) actual_focus.push_back(at);
    witnesses.focus_actual = make_spans(std::move(actual_focus), frame.width);
    require(witnesses.focus_expected == witnesses.focus_actual, "all exact cyan positions and counts match the independent focused-control outline");
    const auto count = span_pixels(witnesses.focus_expected);
    if (witnesses.full_required) require(count > 0, "every required full-frame focus witness has nonempty cyan ink");
    ++totals.focus_witnesses; totals.focus_pixels += count;
}

bool contains(SDL_Rect b, int x, int y) { return x >= b.x && y >= b.y && x < b.x + b.w && y < b.y + b.h; }
void check_clip(const Case& test, Frame& frame) {
    // SDL_RenderClear clears the WHOLE target regardless of viewport or clip.
    const Pixel clear = test.presentation == UiPresentation::Flat ? Pixel{18, 21, 20, 255} : Pixel{85, 54, 36, 255};
    bool contained = true;
    frame.visible_pixels = 0;
    for (int y = 0; y < frame.height; ++y) for (int x = 0; x < frame.width; ++x) {
        if (visible(frame.before, x, y)) ++frame.visible_pixels;
        else { contained = contained && frame.pixels[frame.at(x, y)] == clear; ++totals.protected_pixels; }
    }
    require(contained, "no paint beyond caller viewport/clip after whole-target clear");
    if (frame.before.clipped && (frame.before.clip.w == 0 || frame.before.clip.h == 0)) {
        require(frame.visible_pixels == 0, "enabled empty clip has no visible pixels"); ++totals.empty_cases;
    } else require(frame.visible_pixels > 0, "declared nonempty caller intersection is observed");
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
void check_companion(const Case& clipped, const UiModel& model, Frame& frame, const Frame& full) {
    require(clipped.clipped && frame.before.clipped && !full.before.clipped && frame.width == full.width &&
            frame.height == full.height && frame.model_before == full.model_before && frame.model_after == full.model_after &&
            frame.session_before == full.session_before && frame.hit_before == full.hit_before && frame.backend == full.backend &&
            equal(frame.before.viewport, full.before.viewport) && same_float(frame.before.sx, full.before.sx) &&
            same_float(frame.before.sy, full.before.sy) && frame.before.blend == full.before.blend,
            "uncut companion keeps identical state, output, viewport, scales, blend and backend");
    const auto specification = witness_spec(clipped, model);
    std::vector<SDL_Rect> glyphs;
    for (const auto& run : specification.text)
        glyphs.insert(glyphs.end(), run.destinations.begin(), run.destinations.end());
    auto field = intrinsic_field(clipped); field.x += clipped.origin_x; field.y += clipped.origin_y;
    bool equal_quiet = true;
    for (int y = std::max(0, field.y); y < std::min(frame.height, field.y + field.h); ++y)
        for (int x = std::max(0, field.x); x < std::min(frame.width, field.x + field.w); ++x) {
            if (!visible(frame.before, x, y) || std::any_of(glyphs.begin(), glyphs.end(),
                [&](SDL_Rect glyph) { return contains(glyph, x, y); })) continue;
            equal_quiet = equal_quiet && frame.pixels[frame.at(x, y)] == full.pixels[full.at(x, y)];
            ++frame.quiet_pixels;
        }
    require(equal_quiet, "all quiet material intersection pixels equal the uncut companion exactly");
    if (clipped.clip_kind == "disjoint") require(frame.quiet_pixels == 0, "disjoint clip has no quiet material intersection");
    else require(frame.quiet_pixels > 0, "every nonempty edge clip has independently derived quiet material witnesses");
    frame.companion_checked = true;
    totals.quiet_clip_pixels += frame.quiet_pixels; ++totals.clip_companions;
}

void pixel(std::ostream& out, Pixel value) {
    array(out, value, [](auto& stream, std::uint8_t channel) { stream << static_cast<unsigned>(channel); });
}
void span_record(std::ostream& out, const std::vector<Span>& spans) {
    array(out, spans, [](auto& stream, Span s) { stream << '[' << s.row << ',' << s.first << ',' << s.end << ']'; });
}
void witness_record(std::ostream& out, const Witnesses& w) {
    out << "{\"full_required\":" << w.full_required << ",\"opaque_probes\":";
    array(out, w.opaque, [](auto& stream, const OpaqueProbe& p) {
        stream << "{\"id\":\"" << p.id << "\",\"logical_regions\":";
        array(stream, p.regions, [](auto& sink, UiRect r) { rect(sink, r); });
        stream << ",\"pixels\":" << span_pixels(p.samples) << ",\"spans\":"; span_record(stream, p.samples); stream << '}';
    });
    out << ",\"text_runs\":";
    array(out, w.text, [](auto& stream, const TextRun& run) {
        stream << "{\"id\":\"" << run.id << "\",\"text\":\"" << run.text << "\",\"box\":"; rect(stream, run.box);
        stream << ",\"requested_size\":" << run.requested << ",\"padding\":" << run.padding
            << ",\"face\":\"" << (run.face == TextFace::Sans ? "Sans" : "Serif") << "\",\"color\":"; pixel(stream, run.color);
        stream << ",\"text_arguments\":[" << run.x << ',' << run.top << ',' << run.size << "],\"glyph_destinations\":";
        array(stream, run.destinations, [](auto& sink, SDL_Rect r) { rect(sink, r); });
        stream << ",\"opaque_pixels\":" << span_pixels(run.cores) << ",\"opaque_spans\":"; span_record(stream, run.cores); stream << '}';
    });
    out << ",\"focus\":{\"id\":"; control_id(out, w.focus_id);
    out << ",\"bounds\":"; rect(out, w.focus_bounds);
    out << ",\"logical_regions\":"; array(out, w.focus_regions, [](auto& stream, UiRect r) { rect(stream, r); });
    out << ",\"color\":"; pixel(out, focus_cyan);
    out << ",\"expected_pixels\":" << span_pixels(w.focus_expected) << ",\"actual_pixels\":" << span_pixels(w.focus_actual)
        << ",\"expected_spans\":"; span_record(out, w.focus_expected);
    out << ",\"actual_spans\":"; span_record(out, w.focus_actual);
    out << "}}";
}
bool whole_frame_required(const Case& c) {
    return !eligible(c) || c.clip_kind == "empty" || c.clip_kind == "disjoint";
}
void scenario(std::ostream& out, std::size_t index, const Scenario& item) {
    const auto& c = item.test; const auto spec = surface_spec(c);
    out << "\"case\":" << index << ",\"id\":\"" << item.id << "\",\"kind\":\"" << item.kind
        << "\",\"source_main\":" << item.source << ",\"logical_size\":[" << c.width << ',' << c.height
        << "],\"output_size\":[" << spec.width << ',' << spec.height << "],\"scale\":[" << c.rx << ',' << c.ry
        << "],\"origin\":[" << c.origin_x << ',' << c.origin_y << "],\"viewport_request\":"; rect(out, spec.viewport);
    out << ",\"clip_kind\":\"" << c.clip_kind << "\",\"clip_space\":\"physical-at-scale-one\",\"clip_request\":"; rect(out, c.clip_request);
    out << ",\"requested_clip_enabled\":" << c.clipped << ",\"route\":\"" << route_name(c.route)
        << "\",\"route_index\":" << static_cast<unsigned>(c.route) << ",\"lower_route\":\"B\",\"edited_banks\":[\"B\",\"B\"]"
        << ",\"pending\":false,\"drawbar_level\":4,\"expression\":" << c.expression << ",\"pedal_levels\":";
    array(out, c.pedals, [](auto& stream, std::uint8_t value) { stream << static_cast<unsigned>(value); });
    out << ",\"percussion\":[" << c.percussion.enabled << ',' << static_cast<unsigned>(c.percussion.harmonic)
        << ',' << static_cast<unsigned>(c.percussion.volume) << ',' << static_cast<unsigned>(c.percussion.decay)
        << "],\"requested_play_focus\":"; control_id(out, c.focus);
    out << ",\"blend\":" << static_cast<unsigned>(c.blend) << ",\"workspace\":" << static_cast<unsigned>(c.workspace)
        << ",\"presentation\":" << static_cast<unsigned>(c.presentation) << ",\"active_reference\":" << active(c)
        << ",\"eligible_p1\":" << eligible(c) << ",\"resource_crop\":" << c.resource
        << ",\"paired_whole_frame_equality_required\":" << whole_frame_required(c)
        << ",\"independent_panel\":"; rect(out, independent_panel(c));
    out << ",\"independent_inset\":"; rect(out, independent_inset(c));
    out << ",\"intrinsic_inset\":"; rect(out, intrinsic_field(c));
}
void stream(std::size_t index, const Scenario& item, const Frame& frame) {
    std::ostringstream out;
    out << std::boolalpha << std::setprecision(std::numeric_limits<double>::max_digits10)
        << "{\"schema\":1,\"protocol\":\"" << protocol << "\",";
    scenario(out, index, item);
    out << ",\"width\":" << frame.width << ",\"height\":" << frame.height
        << ",\"pixel_format\":\"RGBA8\",\"row_order\":\"top-to-bottom\",\"row_stride\":" << frame.width * 4
        << ",\"renderer_before\":"; transform_record(out, frame.before);
    out << ",\"renderer_after\":"; transform_record(out, frame.after);
    out << ",\"model_before\":" << frame.model_before << ",\"model_after\":" << frame.model_after
        << ",\"session_before\":" << frame.session_before << ",\"session_after\":" << frame.session_after
        << ",\"hit_before\":" << frame.hit_before << ",\"hit_after\":" << frame.hit_after
        << ",\"info\":" << info_record() << ",\"backend\":" << frame.backend << ",\"helper_probe\":{\"present\":"
        << frame.helper.present << ",\"invoked\":" << frame.helper.invoked << ",\"bounds\":"; rect(out, frame.helper.bounds);
    out << ",\"composition_scale\":[" << frame.helper.scale.sx << ',' << frame.helper.scale.sy << ',' << frame.helper.scale.f
        << "],\"before\":"; transform_record(out, frame.helper.before);
    out << ",\"after\":"; transform_record(out, frame.helper.after);
    out << ",\"unchanged\":true},\"witnesses\":"; witness_record(out, frame.witnesses);
    out << ",\"checks\":{\"transform_unchanged\":true,\"model_unchanged\":true,\"session_unchanged\":true,"
           "\"hit_unchanged\":true,\"clip_containment\":true,\"deterministic_repaint\":true,\"inactive_classification\":true,"
           "\"text_cores_exact\":true,\"opaque_probes_nonempty_when_required\":true,\"focus_positions_exact\":true,"
           "\"clip_companion_checked\":" << frame.companion_checked
        << ",\"after_all_repeat_checked\":" << frame.after_all_checked << ",\"fresh_repeat_checked\":" << frame.fresh_checked
        << "},\"visible_clip_pixels\":" << frame.visible_pixels << ",\"quiet_clip_pixels\":" << frame.quiet_pixels
        << ",\"history_states\":" << frame.history_states
        << ",\"bytes\":" << frame.pixels.size() * sizeof(Pixel) << "}\n";
    const auto header = out.str();
    require(header.size() < 2 * 1024 * 1024, "bounded JSON metadata header");
    std::cout << header;
    std::cout.write(reinterpret_cast<const char*>(frame.pixels.data()), static_cast<std::streamsize>(frame.pixels.size() * sizeof(Pixel)));
    std::cout.flush();
    require(static_cast<bool>(std::cout), "write one JSON line followed by exact bounded RGBA bytes");
}

std::size_t companion_index(std::size_t main) {
    if (main >= 10 && main <= 13) return 24 + main - 10;
    if (main == 15) return 28;
    return scenario_count;
}
Frame qualify(const Scenario& item, const std::array<Scenario, scenario_count>& fixtures) {
    const auto& test = item.test; const auto model = state_for(test);
    Target target(test); auto frame = target.paint(model);
    check_clip(test, frame); observe_witnesses(test, model, target, frame);
    same_frame(frame, target.paint(model), "exact same-renderer repaint after independent witness rendering"); ++totals.repaints;
    if (item.kind == "main") {
        const auto companion = companion_index(item.source);
        if (companion < scenario_count) {
            Target uncut(fixtures[companion].test);
            check_companion(test, model, frame, uncut.paint(model)); ++totals.clipped_cases;
        }
        ++totals.main_cases;
    } else if (item.kind == "uncut-companion") {
        const auto& clipped = fixtures[item.source].test;
        Target cut(clipped); auto clipped_frame = cut.paint(model);
        check_companion(clipped, model, clipped_frame, frame);
        frame.companion_checked = true; frame.quiet_pixels = clipped_frame.quiet_pixels;
    } else if (item.kind == "eligibility-witness") ++totals.eligibility_witnesses;
    if (!active(test)) ++totals.inactive_cases;
    ++totals.cases;
    return frame;
}
Frame after_all(Target& history, const Frame& original, const std::array<Scenario, scenario_count>& fixtures) {
    // All 24 declared main transforms, the five uncut transforms, and three
    // eligibility states exercise one already initialized canonical renderer.
    // History outputs are not graded as replacements for the full matrix.
    for (std::size_t i = 0; i < fixtures.size(); ++i) {
        if (i == 29 || i == 30) continue;
        history.configure(fixtures[i].test);
        (void)history.paint(state_for(fixtures[i].test), false); ++totals.history_states;
    }
    history.configure(fixtures[0].test);
    const auto model = state_for(fixtures[0].test);
    auto repeated = history.paint(model);
    same_frame(original, repeated, "case0 RGBA and copied state are exact after all declared states and transforms");
    check_clip(fixtures[0].test, repeated); observe_witnesses(fixtures[0].test, model, history, repeated);
    same_frame(repeated, history.paint(model), "history witness remains exact after independent probe rendering");
    repeated.after_all_checked = true; repeated.history_states = 32;
    ++totals.history_repaints; ++totals.repaints; ++totals.cases;
    return repeated;
}
Frame fresh_repeat(const Frame& original, const std::array<Scenario, scenario_count>& fixtures) {
    const auto& test = fixtures[0].test; const auto model = state_for(test);
    Target fresh(test); auto frame = fresh.paint(model);
    same_frame(original, frame, "case0 RGBA and complete copied state match a fresh renderer");
    check_clip(test, frame); observe_witnesses(test, model, fresh, frame);
    same_frame(frame, fresh.paint(model), "fresh witness remains exact after independent probe rendering");
    frame.fresh_checked = true;
    ++totals.fresh_repaints; ++totals.repaints; ++totals.cases;
    return frame;
}
} // namespace

int main(int argc, char* argv[]) {
    SDL_SetMainReady();
    std::size_t current_case = scenario_count;
    try {
        const auto fixtures = scenarios();
        if (argc == 2 && std::string_view(argv[1]) == "--list") {
            std::cout << std::boolalpha << std::setprecision(std::numeric_limits<double>::max_digits10)
                << "{\"schema\":1,\"protocol\":\"" << protocol << "\",\"cases\":" << fixtures.size()
                << ",\"main_cases\":24,\"companions\":5,\"repeats\":2,\"eligibility_witnesses\":3,"
                   "\"stream\":\"one JSON line then bytes packed RGBA8; no trailer\","
                   "\"span_format\":\"[physical output row, first x, exclusive end x]\",\"inventory\":[";
            for (std::size_t i = 0; i < fixtures.size(); ++i) {
                if (i) std::cout << ',';
                std::cout << '{'; scenario(std::cout, i, fixtures[i]); std::cout << '}';
            }
            std::cout << "]}\n";
            require(static_cast<bool>(std::cout), "write all fixed main/companion/repeat/witness identifiers");
            return EXIT_SUCCESS;
        }
        std::size_t selected = fixtures.size();
        if (argc != 1) {
            require(argc == 3 && std::string_view(argv[1]) == "--case", "expected --case INDEX or --list");
            const std::string_view value(argv[2]);
            const auto parsed = std::from_chars(value.data(), value.data() + value.size(), selected);
            require(parsed.ec == std::errc{} && parsed.ptr == value.data() + value.size() && selected < fixtures.size(), "bounded case index");
#ifdef _WIN32
            require(_setmode(_fileno(stdout), _O_BINARY) != -1, "binary frame stdout");
#endif
        }
        require(SDL_Init(0) == 0, "initialize SDL without audio or a window");
        {
            if (selected == fixtures.size()) {
                // Create the anchor before the whole ordinary matrix. Its
                // original frame survives all other cases and fresh targets.
                Target history(fixtures[0].test);
                const auto original = history.paint(state_for(fixtures[0].test));
                for (std::size_t index = 0; index < fixtures.size(); ++index) {
                    if (index == 29 || index == 30) continue;
                    current_case = index; (void)qualify(fixtures[index], fixtures);
                }
                current_case = 29; (void)after_all(history, original, fixtures);
                current_case = 30; (void)fresh_repeat(original, fixtures);
                require(totals.cases == 34 && totals.main_cases == 24 && totals.repaints == 34 &&
                        totals.clipped_cases == 5 && totals.clip_companions == 10 &&
                        totals.history_states == 32 && totals.history_repaints == 1 && totals.fresh_repaints == 1 &&
                        totals.eligibility_witnesses == 3, "complete frozen 24+5+2+3 inventory and all repetition/companion checks");
            } else {
                current_case = selected;
                if (selected == 29 || selected == 30) {
                    Target history(fixtures[0].test);
                    const auto original = history.paint(state_for(fixtures[0].test));
                    auto frame = selected == 29 ? after_all(history, original, fixtures) : fresh_repeat(original, fixtures);
                    stream(selected, fixtures[selected], frame);
                } else {
                    const auto frame = qualify(fixtures[selected], fixtures);
                    stream(selected, fixtures[selected], frame);
                }
            }
        }
        SDL_Quit();
        if (selected == fixtures.size())
            std::cout << "{\"schema\":1,\"protocol\":\"" << protocol << "\",\"status\":\"passed\",\"cases\":" << totals.cases
                << ",\"main_cases\":" << totals.main_cases << ",\"checks\":" << totals.checks << ",\"paintings\":" << totals.paintings
                << ",\"clipped_cases\":" << totals.clipped_cases << ",\"empty_cases\":" << totals.empty_cases
                << ",\"inactive_cases\":" << totals.inactive_cases << ",\"protected_pixels\":" << totals.protected_pixels
                << ",\"deterministic_repaints\":" << totals.repaints << ",\"clip_companions\":" << totals.clip_companions
                << ",\"quiet_clip_pixels\":" << totals.quiet_clip_pixels << ",\"history_states\":" << totals.history_states
                << ",\"history_repaints\":" << totals.history_repaints << ",\"fresh_repaints\":" << totals.fresh_repaints
                << ",\"eligibility_witnesses\":" << totals.eligibility_witnesses << ",\"opaque_probes\":" << totals.opaque_probes
                << ",\"opaque_pixels\":" << totals.opaque_pixels << ",\"text_runs\":" << totals.text_runs
                << ",\"nonempty_text_runs\":" << totals.nonempty_text_runs << ",\"glyph_core_pixels\":" << totals.glyph_core_pixels
                << ",\"focus_witnesses\":" << totals.focus_witnesses << ",\"focus_pixels\":" << totals.focus_pixels
                << ",\"helper_present\":" << (p1_fixture_helper_present<Drawing> ? "true" : "false")
                << ",\"helper_probes\":" << totals.helper_probes
                << ",\"backend\":\"SDL software surface; fixed copied state; no audio/window\"}\n";
        return EXIT_SUCCESS;
    } catch (const std::exception& error) {
        std::cerr << "Performance plate fixture failed in case " << current_case << ": " << error.what() << '\n';
        SDL_Quit();
        return EXIT_FAILURE;
    }
}
