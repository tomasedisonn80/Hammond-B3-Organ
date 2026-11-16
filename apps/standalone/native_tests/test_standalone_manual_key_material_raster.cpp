#include "InstrumentView.h"

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

// A11: frozen BEFORE any manual-key candidate painter. This file observes the
// real complete painter. Its geometry, masks and state do not come from painted
// pixels, candidate geometry or a material implementation. The independent
// paired checker must compare all state/geometry, outgoing renderer state, RGBA,
// complete cyan sets, the frozen source masks and per-key appearance windows.
// Default execution qualifies the fixture, not the proposed material or 1:1 UI.
namespace {
using namespace hammond;
using namespace hammond::standalone;
using Pixel = std::array<std::uint8_t, 4>;
static_assert(sizeof(Pixel) == 4);
static_assert(sizeof(float) == 4 && std::numeric_limits<float>::is_iec559);
constexpr std::string_view protocol = "manual-key-material-v1";
constexpr std::string_view before_revision = "79bf34091dda5dc0528cf584891cff3e09657c66";
constexpr std::string_view published_before_revision = "f56b0f3b4ac98dd0f4bce289f9509fdad8e03331";
constexpr std::string_view before_tree = "b4e5526d3b08ca90fce4c3c152db8459ddd6c4e6";
constexpr Pixel cyan{165, 228, 223, 255};
constexpr Pixel brass{214, 182, 124, 255};
constexpr Pixel walnut{85, 54, 36, 255};
constexpr std::size_t manual_total = 122;
constexpr std::size_t key_total = 147;

struct Totals {
    std::size_t cases{}, checks{}, state_restorations{}, geometry_keys{};
    std::size_t support_pixels{}, exterior_pixels{}, focus_pixels{}, held_pixels{}, held_cue_pixels{}, outline_pixels{};
    std::size_t clip_companions{}, clip_pixels{}, empty_clip_pixels{}, repeats{}, sample_windows{};
} totals;
void require(bool condition, std::string_view message) {
    ++totals.checks;
    if (!condition) throw std::runtime_error(std::string(message) + ": " + SDL_GetError());
}

enum class Held { None, Mixed, AllManuals };
enum class Clip { None, Crossing, Empty };
struct Case {
    std::string_view name;
    float width{1672}, height{941}, rx{1}, ry{1};
    int origin_x{}, origin_y{};
    Held held{Held::None};
    int focus_manual{-1}, focus_key{-1};
    Clip clip{Clip::None};
    UiPresentation presentation{UiPresentation::Dimensional};
    UiWorkspace workspace{UiWorkspace::Play};
};
constexpr std::array<Case, 16> fixtures{{
    {"01-canonical-idle"},
    {"02-minimum-idle", 1400, 820},
    {"03-unequal-layout", 1920, 820, 1, 1, 13, 17},
    {"04-anisotropic-renderer", 1672, 941, 1.5F, 2, 13, 17},
    {"05-mixed-held", 1672, 941, 1, 1, 0, 0, Held::Mixed, 0, 13},
    {"06-focus-upper-natural", 1672, 941, 1, 1, 0, 0, Held::None, 0, 12},
    {"07-focus-upper-accidental", 1672, 941, 1, 1, 0, 0, Held::None, 0, 13},
    {"08-focus-lower-natural", 1400, 820, 1, 1, 0, 0, Held::None, 1, 48},
    {"09-focus-lower-accidental", 1400, 820, 1.5F, 1.5F, 13, 17, Held::None, 1, 49},
    {"10-all-manuals-held", 1672, 941, 1, 1, 0, 0, Held::AllManuals, 1, 48},
    {"11-crossing-physical-clip", 1672, 941, 1.5F, 2, 13, 17, Held::None, -1, -1, Clip::Crossing},
    {"12-enabled-empty-clip", 1672, 941, 1.5F, 2, 13, 17, Held::None, -1, -1, Clip::Empty},
    {"13-compact-play", 1399, 819},
    {"14-flat-play", 1672, 941, 1, 1, 0, 0, Held::None, -1, -1, Clip::None, UiPresentation::Flat},
    {"15-rotary", 1672, 941, 1, 1, 0, 0, Held::None, -1, -1, Clip::None,
        UiPresentation::Dimensional, UiWorkspace::Rotary},
    {"16-service", 1672, 941, 1, 1, 0, 0, Held::None, -1, -1, Clip::None,
        UiPresentation::Dimensional, UiWorkspace::Service},
}};

bool active(const Case& test) {
    return test.workspace == UiWorkspace::Play && test.presentation == UiPresentation::Dimensional &&
           test.width >= 1400 && test.width <= 8192 && test.height >= 820 && test.height <= 8192;
}
bool whole_equal(const Case& test) {
    return !active(test) || test.held == Held::AllManuals || test.clip == Clip::Empty;
}
bool is_held(const Case& test, std::size_t division, std::size_t index) {
    if (division < 2 && test.held == Held::AllManuals) return true;
    if (test.held != Held::Mixed) return false;
    return division == 0 ? (index == 12 || index == 13) :
           division == 1 ? (index == 48 || index == 49) : (index == 12 || index == 13);
}
bool is_focused(const Case& test, std::size_t division, std::size_t index) {
    return test.focus_manual == static_cast<int>(division) && test.focus_key == static_cast<int>(index);
}
std::string_view clip_name(Clip clip) {
    return clip == Clip::None ? "disabled" : clip == Clip::Crossing ? "physical-crossing" : "physical-empty";
}
SDL_Rect physical_clip(const Case& test) {
    // Viewport-relative OUTPUT pixels, installed at renderer scale one. The
    // crossing rectangle is exactly [500,810)x[580,860) times (1.5,2).
    return test.clip == Clip::Crossing ? SDL_Rect{750, 1160, 465, 560} :
           test.clip == Clip::Empty ? SDL_Rect{750, 1160, 0, 0} : SDL_Rect{};
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

UiControlId expected_focus(const Case& test) {
    if (test.focus_manual >= 0)
        return {UiControlKind::ManualKey, test.focus_manual == 0 ? Manual::Upper : Manual::Lower,
                DrawbarBank::A, static_cast<std::uint8_t>(test.focus_key)};
    if (test.workspace != UiWorkspace::Play)
        return {UiControlKind::Workspace, Manual::Upper, DrawbarBank::A,
                static_cast<std::uint8_t>(test.workspace)};
    return {UiControlKind::EditBank, Manual::Upper, DrawbarBank::B, 0};
}

UiModel state_for(const Case& test) {
    UiModel model;
    require(model.resize(test.width, test.height) && model.set_presentation(test.presentation) &&
            model.set_workspace(test.workspace), "declared layout/presentation/workspace");
    SessionSnapshot snapshot{};
    snapshot.controls.drawbars[0][0] = {8, 0, 4, 1, 2, 3, 4, 5, 6};
    snapshot.controls.drawbars[0][1] = {8, 6, 5, 4, 3, 4, 2, 5, 3};
    snapshot.controls.drawbars[1][0] = {4, 3, 2, 1, 0, 1, 2, 3, 4};
    snapshot.controls.drawbars[1][1] = {0, 0, 8, 0, 0, 0, 0, 0, 0};
    snapshot.controls.selected_banks = {DrawbarBank::B, DrawbarBank::A};
    snapshot.controls.route_enabled = {true, true};
    snapshot.controls.fixed_registrations = {FixedRegistration::None, FixedRegistration::None};
    snapshot.controls.expression = 0.625;
    snapshot.controls.pedal_drawbars = {3, 7};
    snapshot.controls.percussion = {true, PercussionHarmonic::Second, PercussionVolume::Normal, PercussionDecay::Slow};
    ControlState validated;
    require(validated.restore(snapshot.controls), "all four fixed banks and control fields are valid");
    for (std::size_t manual = 0; manual < 2; ++manual)
        for (std::size_t key = 0; key < 61; ++key) snapshot.held_keys[manual][key] = is_held(test, manual, key);
    for (std::size_t key = 0; key < 25; ++key) snapshot.held_pedals[key] = is_held(test, 2, key);
    snapshot.frame_clock = 38400;
    snapshot.sample_rate = 48000;
    snapshot.peak = 0.125F;
    snapshot.prepared = snapshot.running = true;
    snapshot.publication_revision = 4;
    // Remaining counters are explicitly zero through value initialization;
    // last_core_status is the declared Status::Ok member default.
    model.observe(snapshot);
    const auto focus = expected_focus(test);
    require(model.activate(focus).count == 0, "fixture focus creates no musical/app action");
    require(model.view().focus == focus, "exact semantic focus identity");
    require(model.view().controls == snapshot.controls && session_record(model.view().applied) == session_record(snapshot) &&
            !model.view().controls_pending && !model.view().pointer_captured && !model.view().text_entry_active,
            "fixed desired/applied snapshots, no pending gesture or modal input");
    require(reference_composition_active(model.layout()) == active(test), "independent activation predicate agrees");
    require(model.layout().control_count == 68 && model.layout().manual_keys.size() * kManualKeyCount +
            model.layout().pedal_keys.size() == key_total, "complete 68-control / 147-playing-key inventory");
    std::size_t presets = 0, held_manuals = 0, held_pedals = 0;
    for (const auto& control : model.layout().controls)
        if (control.id.kind == UiControlKind::PresetKey) ++presets;
    for (const auto& manual : snapshot.held_keys) for (bool held : manual) if (held) ++held_manuals;
    for (bool held : snapshot.held_pedals) if (held) ++held_pedals;
    require(presets == 24 && held_manuals == (test.held == Held::AllManuals ? 122U : test.held == Held::Mixed ? 4U : 0U) &&
            held_pedals == (test.held == Held::Mixed ? 2U : 0U), "exact presets and declared held counts");
    return model;
}

// Every geometry calculation below was transcribed from the BEFORE source.
// Deliberate local float rounding reproduces stored binary32 vertices. No
// production layout, quad_band, inset, outline or Drawing raster helper is used.
float f32(float value) { volatile float rounded = value; return rounded; }
float add(float a, float b) { return f32(a + b); }
float sub(float a, float b) { return f32(a - b); }
float mul(float a, float b) { return f32(a * b); }
float divf(float a, float b) { return f32(a / b); }
struct Scale { float x{}, y{}; };
Scale layout_scale(const Case& test) { return {divf(test.width, 1672), divf(test.height, 941)}; }
bool accidental(std::size_t index) {
    const auto pitch = index % 12;
    return pitch == 1 || pitch == 3 || pitch == 6 || pitch == 8 || pitch == 10;
}
UiPoint map_point(UiPoint p, Scale scale) { return {mul(p.x, scale.x), mul(p.y, scale.y)}; }
UiQuad map_quad(UiQuad q, Scale scale) {
    for (auto& p : q.points) p = map_point(p, scale);
    return q;
}
UiRect bounds_of(const UiQuad& q) {
    const auto& p = q.points;
    const float left = std::min({p[0].x, p[1].x, p[2].x, p[3].x});
    const float right = std::max({p[0].x, p[1].x, p[2].x, p[3].x});
    const float top = std::min({p[0].y, p[1].y, p[2].y, p[3].y});
    const float bottom = std::max({p[0].y, p[1].y, p[2].y, p[3].y});
    return {left, top, sub(right, left), sub(bottom, top)};
}
UiRect mapped_rect(UiRect q, Scale scale) {
    const auto a = map_point({q.x, q.y}, scale);
    const auto b = map_point({add(q.x, q.width), add(q.y, q.height)}, scale);
    return {a.x, a.y, sub(b.x, a.x), sub(b.y, a.y)};
}
UiQuad rect_quad(UiRect q) {
    const float right = add(q.x, q.width), bottom = add(q.y, q.height);
    return UiQuad{{UiPoint{q.x, q.y}, UiPoint{right, q.y},
                   UiPoint{right, bottom}, UiPoint{q.x, bottom}}};
}

std::array<UiKeyGeometry, key_total> original_keys(const Case& test) {
    constexpr std::array<UiRect, 3> panels{{{232, 528, 890, 170}, {224, 698, 898, 172}, {1138, 752, 450, 110}}};
    constexpr std::array<double, 3> back{0.96, 0.95, 1.0};
    std::array<UiKeyGeometry, key_total> result{};
    const auto scale = layout_scale(test);
    for (std::size_t division = 0; division < 3; ++division) {
        const auto panel = panels[division];
        const float left = add(panel.x, 8), top = add(panel.y, 20);
        const float width = sub(panel.width, 16), height = sub(panel.height, 28);
        const std::size_t natural_count = division == 2 ? 15 : 36;
        const std::size_t count = division == 2 ? 25 : 61;
        const std::size_t offset = division == 2 ? 122 : division * 61;
        const auto project = [&](double u, double v) {
            const double denominator = 1.0 - (1.0 - back[division]) * v;
            return UiPoint{static_cast<float>(left + static_cast<double>(width) / 2.0 +
                static_cast<double>(width) * back[division] * (u - 0.5) / denominator),
                static_cast<float>(top + static_cast<double>(height) * back[division] * v / denominator)};
        };
        std::array<UiPoint, 37> rear{}, front{};
        for (std::size_t edge = 0; edge <= natural_count; ++edge) {
            rear[edge] = project(static_cast<double>(edge) / static_cast<double>(natural_count), 0);
            front[edge] = project(static_cast<double>(edge) / static_cast<double>(natural_count), 1);
        }
        std::size_t natural = 0;
        for (std::size_t index = 0; index < count; ++index) {
            auto& key = result[offset + index];
            key.note = {static_cast<UiTarget>(division), static_cast<std::uint8_t>(division == 2 ? index + 1 : index + 36)};
            key.accidental = accidental(index);
            UiQuad hit;
            if (key.accidental) {
                const double u0 = (static_cast<double>(natural) - 0.30) / static_cast<double>(natural_count);
                const double u1 = (static_cast<double>(natural) + 0.30) / static_cast<double>(natural_count);
                hit.points = {{project(u0, 0), project(u1, 0), project(u1, 0.62), project(u0, 0.62)}};
            } else {
                hit.points = {{rear[natural], rear[natural + 1], front[natural + 1], front[natural]}};
                ++natural;
            }
            const auto& p = hit.points;
            const float h = sub(p[3].y, p[0].y);
            const float depth = std::clamp(mul(h, 0.14F), 6.0F, 18.0F);
            const float split_y = sub(p[3].y, depth), fraction = divf(sub(split_y, p[0].y), h);
            const UiPoint split_left{add(p[0].x, mul(sub(p[3].x, p[0].x), fraction)), split_y};
            const UiPoint split_right{add(p[1].x, mul(sub(p[2].x, p[1].x), fraction)), split_y};
            UiQuad face = hit;
            face.points[2] = split_right; face.points[3] = split_left;
            key.hit = map_quad(hit, scale);
            key.top = map_quad(face, scale);
            key.front = map_quad(UiQuad{{split_left, split_right, p[2], p[3]}}, scale);
            key.bounds = bounds_of(key.hit);
        }
        require(natural == natural_count, "independently reconstructed natural count");
    }
    return result;
}

bool same_float(float a, float b) { return std::bit_cast<std::uint32_t>(a) == std::bit_cast<std::uint32_t>(b); }
bool equal(UiRect a, UiRect b) {
    return same_float(a.x, b.x) && same_float(a.y, b.y) && same_float(a.width, b.width) && same_float(a.height, b.height);
}
bool equal(SDL_Rect a, SDL_Rect b) { return a.x == b.x && a.y == b.y && a.w == b.w && a.h == b.h; }
bool equal(const UiQuad& a, const UiQuad& b) {
    for (std::size_t i = 0; i < 4; ++i)
        if (!same_float(a.points[i].x, b.points[i].x) || !same_float(a.points[i].y, b.points[i].y)) return false;
    return true;
}
void check_geometry(const Case& test, const UiModel& model, const std::array<UiKeyGeometry, key_total>& expected) {
    if (!active(test)) return; // Inactive whole-frame equality admits no material support.
    for (std::size_t owner = 0; owner < key_total; ++owner) {
        const auto& actual = owner < manual_total ? model.layout().manual_keys[owner / 61][owner % 61] :
                                                    model.layout().pedal_keys[owner - manual_total];
        const auto& original = expected[owner];
        require(actual.note == original.note && actual.accidental == original.accidental &&
                equal(actual.bounds, original.bounds) && equal(actual.hit, original.hit) &&
                equal(actual.top, original.top) && equal(actual.front, original.front),
                "every key identity/bounds/hit/top/front equals independent before-source geometry bit-for-bit");
        ++totals.geometry_keys;
    }
    const auto scale = layout_scale(test);
    require(equal(model.layout().pedal_panel, mapped_rect({1138, 752, 450, 110}, scale)) &&
            equal(model.layout().preset_key_panels[0], mapped_rect({58, 607, 164, 81}, scale)) &&
            equal(model.layout().preset_key_panels[1], mapped_rect({42, 777, 172, 83}, scale)),
            "complete independent pedal and preset panel regions");
}

bool valid_quad(const UiQuad& q) {
    const auto& p = q.points;
    for (const auto point : p) if (!std::isfinite(point.x) || !std::isfinite(point.y)) return false;
    return p[0].y == p[1].y && p[2].y == p[3].y && p[3].y > p[0].y &&
           p[1].x > p[0].x && p[2].x > p[3].x;
}
UiQuad band(const UiQuad& q, float a, float b, float inset = 0) {
    const auto& p = q.points;
    const float h = sub(p[3].y, p[0].y);
    if (!(h > 0 && b > a && a >= 0 && b <= 1)) return {};
    const auto point = [&](std::size_t first, std::size_t last, float v, float x) {
        return UiPoint{add(add(p[first].x, mul(sub(p[last].x, p[first].x), v)), x), add(p[0].y, mul(h, v))};
    };
    const UiQuad result{{point(0, 3, a, inset), point(1, 2, a, -inset), point(1, 2, b, -inset), point(0, 3, b, inset)}};
    return valid_quad(result) ? result : UiQuad{};
}
UiQuad inset(const UiQuad& q, float amount, Scale scale) {
    const float h = sub(q.points[3].y, q.points[0].y), y = mul(amount, scale.y);
    return h > mul(2, y) ? band(q, divf(y, h), sub(1, divf(y, h)), mul(amount, scale.x)) : UiQuad{};
}
template <typename Paint>
void outline(const UiQuad& q, float thickness, Scale scale, Paint paint) {
    if (!valid_quad(q)) return;
    const auto& p = q.points;
    const float h = sub(p[3].y, p[0].y);
    const float x = std::min(mul(thickness, scale.x), divf(std::min(sub(p[1].x, p[0].x), sub(p[2].x, p[3].x)), 2));
    const float y = std::min(mul(thickness, scale.y), divf(h, 2));
    paint(band(q, 0, divf(y, h)));
    paint(band(q, sub(1, divf(y, h)), 1));
    if (mul(2, y) >= h) return;
    const auto middle = band(q, divf(y, h), sub(1, divf(y, h)));
    const auto& m = middle.points;
    paint(UiQuad{{m[0], UiPoint{add(m[0].x, x), m[0].y}, UiPoint{add(m[3].x, x), m[3].y}, m[3]}});
    paint(UiQuad{{UiPoint{sub(m[1].x, x), m[1].y}, m[1], m[2], UiPoint{sub(m[2].x, x), m[2].y}}});
}
UiQuad side(const UiQuad& q, bool left, Scale scale) {
    const auto& p = q.points;
    const float h = sub(p[3].y, p[0].y);
    if (!(h > 0)) return {};
    const std::size_t first = left ? 0U : 1U, last = left ? 3U : 2U;
    const float slope = divf(divf(sub(p[last].x, p[first].x), scale.x), divf(h, scale.y));
    const float offset = mul(std::hypot(1.0F, slope), scale.x);
    const auto edge = [&](std::size_t top, std::size_t bottom, float v) { return add(p[top].x, mul(sub(p[bottom].x, p[top].x), v)); };
    constexpr float a = 0.08F, b = 0.88F;
    if (sub(edge(1, 2, a), edge(0, 3, a)) <= mul(3, offset) ||
        sub(edge(1, 2, b), edge(0, 3, b)) <= mul(3, offset)) return {};
    const auto point = [&](float v, float distance) {
        return UiPoint{add(edge(first, last, v), mul(left ? distance : -distance, offset)), add(p[0].y, mul(h, v))};
    };
    return left ? UiQuad{{point(a, 1), point(a, 2), point(b, 2), point(b, 1)}} :
                  UiQuad{{point(a, 2), point(a, 1), point(b, 1), point(b, 2)}};
}

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
    require(SDL_GetRenderDrawBlendMode(renderer, &result.blend) == 0 &&
            SDL_GetRenderDrawColor(renderer, &result.color[0], &result.color[1], &result.color[2], &result.color[3]) == 0,
            "query incoming/outgoing blend and draw color");
    require(SDL_RenderSetScale(renderer, 1, 1) == 0, "read exact physical viewport/clip");
    SDL_RenderGetViewport(renderer, &result.viewport);
    SDL_RenderGetClipRect(renderer, &result.clip);
    require(SDL_RenderSetScale(renderer, result.sx, result.sy) == 0, "restore scale after physical query");
    return result;
}
bool same_transform(const Transform& a, const Transform& b) {
    return same_float(a.sx, b.sx) && same_float(a.sy, b.sy) && equal(a.viewport, b.viewport) && equal(a.clip, b.clip) &&
           equal(a.logical_viewport, b.logical_viewport) && equal(a.logical_clip, b.logical_clip) &&
           a.clipped == b.clipped && a.blend == b.blend;
}
bool visible(const Transform& t, int x, int y) {
    const int xx = x - t.viewport.x, yy = y - t.viewport.y;
    return xx >= 0 && yy >= 0 && xx < t.viewport.w && yy < t.viewport.h &&
        (!t.clipped || (xx >= t.clip.x && yy >= t.clip.y && xx < t.clip.x + t.clip.w && yy < t.clip.y + t.clip.h));
}
struct SurfaceSpec { int width{}, height{}; SDL_Rect viewport{}; };
SurfaceSpec surface_spec(const Case& test) {
    const int width = static_cast<int>(std::ceil(static_cast<double>(test.width) * test.rx));
    const int height = static_cast<int>(std::ceil(static_cast<double>(test.height) * test.ry));
    return {width + 2 * std::abs(test.origin_x), height + 2 * std::abs(test.origin_y),
            {test.origin_x, test.origin_y, width, height}};
}

// Source-derived flags. A zero flag is protected exterior, never a wildcard.
// OriginalIdleFace is a historical union, not permission: Editable is the sole
// admitted change bit after ordered opaque ownership, outline and cue removal.
enum Flag : std::uint16_t {
    OriginalManualFace = 1, OriginalIdleFace = 2, Editable = 4, VisibleHeld = 8,
    VisibleFocus = 16, VisibleHeldCue = 32, VisibleOutline = 64, PedalRegion = 128, PresetRegion = 256
};
constexpr std::uint16_t ownership_flags = Editable | VisibleHeld | VisibleFocus | VisibleHeldCue | VisibleOutline;
struct Mask {
    int width{}, height{};
    std::vector<std::uint16_t> flags;
    std::vector<std::int16_t> owner;
    std::array<std::size_t, 9> counts{};
    std::array<std::size_t, key_total> visible_keys{}, held_keys{}, held_cues{};
    std::array<std::array<std::size_t, 2>, 2> editable_faces{};
    std::size_t exterior{};
    std::size_t at(int x, int y) const {
        return static_cast<std::size_t>(y) * static_cast<std::size_t>(width) + static_cast<std::size_t>(x);
    }
};

// Exact independent center-sampled coverage. Bounds are clipped in physical
// viewport coordinates before conversion, matching the frozen half-open rule.
// This calls no production geometry/raster API and never reads an image/model.
template <typename Paint>
void raster(const UiQuad& q, const SurfaceSpec& spec, const Transform& t, Paint paint, bool obey_clip = true) {
    if (!valid_quad(q)) return;
    int left = std::max(0, -t.viewport.x), top = std::max(0, -t.viewport.y);
    int right = std::min(t.viewport.w, spec.width - t.viewport.x);
    int bottom = std::min(t.viewport.h, spec.height - t.viewport.y);
    if (obey_clip && t.clipped) {
        left = std::max(left, t.clip.x); top = std::max(top, t.clip.y);
        right = std::min(right, t.clip.x + t.clip.w); bottom = std::min(bottom, t.clip.y + t.clip.h);
    }
    if (left >= right || top >= bottom) return;
    const auto edge = [](double value, int lo, int hi) {
        const double boundary = std::ceil(value - 0.5);
        return boundary <= lo ? lo : boundary >= hi ? hi : static_cast<int>(boundary);
    };
    const auto& p = q.points;
    const double height = static_cast<double>(p[3].y) - p[0].y;
    const int first_row = edge(static_cast<double>(p[0].y) * t.sy, top, bottom);
    const int last_row = edge(static_cast<double>(p[3].y) * t.sy, top, bottom);
    for (int row = first_row; row < last_row; ++row) {
        const double y = (static_cast<double>(row) + 0.5) / t.sy;
        const double v = std::clamp((y - p[0].y) / height, 0.0, 1.0);
        const double a = p[0].x + (static_cast<double>(p[3].x) - p[0].x) * v;
        const double b = p[1].x + (static_cast<double>(p[2].x) - p[1].x) * v;
        const int first = edge(a * t.sx, left, right), end = edge(b * t.sx, left, right);
        for (int x = first; x < end; ++x) paint(x + t.viewport.x, row + t.viewport.y);
    }
}

Mask original_mask(const Case& test, const SurfaceSpec& spec, const Transform& t,
                   const std::array<UiKeyGeometry, key_total>& keys) {
    const auto size = static_cast<std::size_t>(spec.width) * static_cast<std::size_t>(spec.height);
    Mask result{spec.width, spec.height, std::vector<std::uint16_t>(size), std::vector<std::int16_t>(size, -1)};
    if (active(test)) {
        const auto scale = layout_scale(test);
        for (std::size_t division = 0; division < 3; ++division) {
            const std::size_t start = division == 2 ? manual_total : division * 61;
            const std::size_t count = division == 2 ? 25 : 61;
            for (bool sharp : {false, true}) for (std::size_t key_index = 0; key_index < count; ++key_index) {
                const std::size_t owner = start + key_index;
                const auto& key = keys[owner];
                if (key.accidental != sharp) continue;
                const bool held = is_held(test, division, key_index), editable = division < 2 && !held;
                const auto apply = [&](const UiQuad& q, auto function) {
                    raster(q, spec, t, [&](int x, int y) { function(result.at(x, y)); });
                };
                const auto base = [&](std::size_t at) {
                    auto& flags = result.flags[at];
                    flags = static_cast<std::uint16_t>(flags & ~ownership_flags);
                    if (division < 2) flags |= OriginalManualFace;
                    if (editable) flags |= OriginalIdleFace | Editable;
                    if (held) flags |= VisibleHeld;
                    result.owner[at] = static_cast<std::int16_t>(owner);
                };
                // The old full top/front paints are opaque. Later accidentals
                // replace earlier natural ownership, even when that natural is
                // held/focused. No bounding box or union of held hit shapes is used.
                apply(key.top, base); apply(key.front, base);
                if (editable) {
                    outline(key.hit, sharp ? 0.8F : 0.7F, scale, [&](const UiQuad& q) {
                        apply(q, [&](std::size_t at) {
                            result.flags[at] = static_cast<std::uint16_t>((result.flags[at] & ~Editable) | VisibleOutline);
                        });
                    });
                    const auto later_material = [&](const UiQuad& q) {
                        apply(q, [&](std::size_t at) {
                            require(result.owner[at] == static_cast<std::int16_t>(owner) &&
                                    (result.flags[at] & OriginalIdleFace) != 0,
                                    "all original editable overlays remain inside this original idle face");
                            result.flags[at] = static_cast<std::uint16_t>((result.flags[at] & ~VisibleOutline) | Editable);
                        });
                    };
                    if (sharp) {
                        outline(inset(key.top, 1.2F, scale), 0.65F, scale, later_material);
                        later_material(band(key.front, 0, 0.12F, scale.x));
                    } else {
                        const float fd = sub(key.front.points[3].y, key.front.points[0].y);
                        const float td = sub(key.top.points[3].y, key.top.points[0].y);
                        const float highlight = fd > 0 ? std::min(0.13F, divf(mul(2, scale.y), fd)) : 0;
                        const float recess = td > 0 ? std::min(0.12F, divf(mul(18, scale.y), td)) : 0;
                        later_material(band(key.front, 0, highlight, mul(0.9F, scale.x)));
                        later_material(band(key.top, 0, recess, mul(0.8F, scale.x)));
                        later_material(side(key.top, true, scale));
                        later_material(side(key.top, false, scale));
                    }
                }
                if (held) apply(band(key.top, 0.91F, 0.96F, mul(2, scale.x)), [&](std::size_t at) {
                    result.flags[at] = static_cast<std::uint16_t>((result.flags[at] & ~(Editable | VisibleOutline)) | VisibleHeldCue);
                });
                if (is_focused(test, division, key_index))
                    outline(inset(key.hit, 2, scale), 2, scale, [&](const UiQuad& q) {
                        apply(q, [&](std::size_t at) {
                            result.flags[at] = static_cast<std::uint16_t>((result.flags[at] & ~(Editable | VisibleOutline | VisibleHeldCue)) | VisibleFocus);
                        });
                    });
            }
        }
        const auto panel = [&](UiRect canonical, Flag flag) {
            // Complete regions, including portions outside the enabled clip.
            // All such pixels are protected even though clear() affects them.
            raster(rect_quad(mapped_rect(canonical, scale)), spec, t,
                [&](int x, int y) { result.flags[result.at(x, y)] |= flag; }, false);
        };
        panel({1138, 752, 450, 110}, PedalRegion);
        panel({58, 607, 164, 81}, PresetRegion);
        panel({42, 777, 172, 83}, PresetRegion);
        for (std::size_t division = 0; division < 2; ++division)
            for (std::size_t index = 0; index < 61; ++index)
                for (std::size_t face = 0; face < 2; ++face)
                    raster(face == 0 ? keys[division * 61 + index].top : keys[division * 61 + index].front, spec, t,
                        [&](int x, int y) {
                            const auto at = result.at(x, y);
                            if ((result.flags[at] & Editable) != 0 && result.owner[at] == static_cast<std::int16_t>(division * 61 + index))
                                ++result.editable_faces[division][face];
                        });
    }
    for (std::size_t at = 0; at < size; ++at) {
        const auto flags = result.flags[at];
        for (std::size_t bit = 0; bit < result.counts.size(); ++bit) if ((flags & (1U << bit)) != 0) ++result.counts[bit];
        if ((flags & Editable) == 0) ++result.exterior;
        if (result.owner[at] >= 0) {
            const auto owner = static_cast<std::size_t>(result.owner[at]);
            ++result.visible_keys[owner];
            if ((flags & VisibleHeld) != 0) ++result.held_keys[owner];
            if ((flags & VisibleHeldCue) != 0) ++result.held_cues[owner];
        }
        require((flags & Editable) == 0 || ((flags & OriginalManualFace) != 0 && (flags & OriginalIdleFace) != 0 &&
                (flags & (VisibleHeld | VisibleFocus | VisibleHeldCue | VisibleOutline | PedalRegion | PresetRegion)) == 0),
                "editable support is an original idle face and excludes every visible protected owner/cue/region");
    }
    require(result.exterior > 0, "every case protects actual full-frame exterior pixels");
    require(whole_equal(test) ? result.counts[2] == 0 : result.counts[2] > 0, "exact whole-frame-equality/support decision");
    if (active(test)) {
        require(result.counts[7] > 0 && result.counts[8] > 0, "complete protected pedal and preset regions are counted");
        if (test.clip != Clip::Empty && test.held != Held::AllManuals)
            for (const auto& manual : result.editable_faces)
                require(manual[0] > 0 && manual[1] > 0, "both manuals retain nonempty top and front editable support");
        if (test.focus_manual >= 0) require(result.counts[4] > 0, "declared final visible focus cue is nonempty");
        if (test.held != Held::None) {
            for (std::size_t owner = 0; owner < key_total; ++owner) {
                const auto division = owner < manual_total ? owner / 61 : 2;
                const auto index = owner < manual_total ? owner % 61 : owner - manual_total;
                if (is_held(test, division, index))
                    require(result.held_keys[owner] > 0 && result.held_cues[owner] > 0,
                            "each declared held key keeps visible protected face and brass cue pixels");
            }
        }
    }
    totals.support_pixels += result.counts[2]; totals.exterior_pixels += result.exterior;
    totals.focus_pixels += result.counts[4]; totals.held_pixels += result.counts[3];
    totals.held_cue_pixels += result.counts[5]; totals.outline_pixels += result.counts[6];
    return result;
}

struct Frame {
    int width{}, height{};
    Transform incoming{}, outgoing{};
    std::vector<Pixel> pixels;
    std::string model, renderer;
    std::size_t at(int x, int y) const {
        return static_cast<std::size_t>(y) * static_cast<std::size_t>(width) + static_cast<std::size_t>(x);
    }
};
InstrumentViewInfo fixed_info() {
    InstrumentViewInfo info{};
    info.audio_running = true; info.sample_rate = 48000; info.buffer_frames = 512;
    info.audio_driver = "fixed-software-fixture"; info.device_name = "fixed copied state";
    info.status_message = "Manual key material qualification";
    return info;
}
std::string info_record() {
    const auto info = fixed_info();
    std::ostringstream out;
    out << std::boolalpha;
    // All strings here are fixed ASCII without escaping requirements. Remaining
    // default members are written so a stream does not hide implicit input.
    out << "{\"audio_running\":" << info.audio_running << ",\"sample_rate\":" << info.sample_rate
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

class Target {
public:
    explicit Target(const Case& test, bool full_companion = false) : spec_(surface_spec(test)),
        surface_(SDL_CreateRGBSurfaceWithFormat(0, spec_.width, spec_.height, 32, SDL_PIXELFORMAT_RGBA32), SDL_FreeSurface),
        renderer_(surface_ ? SDL_CreateSoftwareRenderer(surface_.get()) : nullptr, SDL_DestroyRenderer), drawing_(renderer_.get()) {
        require(spec_.width > 0 && spec_.height > 0 && spec_.width <= 3000 && spec_.height <= 2200 && surface_ && renderer_,
                "bounded complete software surface allocation");
        std::string error;
        require(drawing_.initialize(error), "initialize unchanged font and artwork resources");
        require(SDL_RenderSetScale(renderer_.get(), 1, 1) == 0 && SDL_RenderSetViewport(renderer_.get(), &spec_.viewport) == 0,
                "install physical viewport before renderer scale");
        const auto clip = physical_clip(test);
        require(SDL_RenderSetClipRect(renderer_.get(), !full_companion && test.clip != Clip::None ? &clip : nullptr) == 0 &&
                SDL_RenderSetScale(renderer_.get(), test.rx, test.ry) == 0 &&
                SDL_SetRenderDrawBlendMode(renderer_.get(), SDL_BLENDMODE_BLEND) == 0,
                "install exact physical clip and incoming scale/blend");
        const auto actual = transform(renderer_.get());
        require(actual.sx == test.rx && actual.sy == test.ry && equal(actual.viewport, spec_.viewport) &&
                actual.clipped == (!full_companion && test.clip != Clip::None) && actual.blend == SDL_BLENDMODE_BLEND,
                "actual renderer transform matches the declared fixture");
        if (actual.clipped) require(equal(actual.clip, clip), "physical clip does not round-trip through logical getters");
        SDL_RendererInfo details{};
        SDL_version version{};
        SDL_GetVersion(&version);
        require(SDL_GetRendererInfo(renderer_.get(), &details) == 0 && details.name != nullptr &&
                std::string_view(details.name) == "software", "declared SDL software backend");
        std::ostringstream out;
        out << "{\"name\":\"" << details.name << "\",\"flags\":" << details.flags << ",\"texture_formats\":[";
        for (std::uint32_t i = 0; i < details.num_texture_formats; ++i) { if (i != 0) out << ','; out << details.texture_formats[i]; }
        out << "],\"maximum_texture_size\":[" << details.max_texture_width << ',' << details.max_texture_height
            << "],\"sdl_version\":[" << static_cast<unsigned>(version.major) << ',' << static_cast<unsigned>(version.minor)
            << ',' << static_cast<unsigned>(version.patch) << "],\"surface_format\":" << SDL_PIXELFORMAT_RGBA32 << '}';
        renderer_record_ = out.str();
    }
    Frame paint(const UiModel& model) {
        require(SDL_SetRenderDrawColor(renderer_.get(), 17, 23, 31, 127) == 0, "fixed incoming draw color");
        const auto incoming = transform(renderer_.get());
        const auto copied = model_record(model);
        paint_instrument(drawing_, model, fixed_info());
        const auto outgoing = transform(renderer_.get());
        require(same_transform(incoming, outgoing), "paint restores scale, physical/logical viewport, clip, enabled state and blend");
        require(copied == model_record(model), "paint preserves every copied state/view/layout member");
        ++totals.state_restorations;
        require(SDL_RenderFlush(renderer_.get()) == 0 && SDL_LockSurface(surface_.get()) == 0, "flush/read exact RGBA surface");
        Frame frame{spec_.width, spec_.height, incoming, outgoing,
            std::vector<Pixel>(static_cast<std::size_t>(spec_.width) * static_cast<std::size_t>(spec_.height)), copied, renderer_record_};
        const auto* input = static_cast<const std::uint8_t*>(surface_->pixels);
        for (int y = 0; y < spec_.height; ++y)
            std::memcpy(frame.pixels.data() + frame.at(0, y), input + static_cast<std::size_t>(y) * static_cast<std::size_t>(surface_->pitch),
                        static_cast<std::size_t>(spec_.width) * sizeof(Pixel));
        SDL_UnlockSurface(surface_.get());
        return frame;
    }
private:
    SurfaceSpec spec_;
    std::unique_ptr<SDL_Surface, decltype(&SDL_FreeSurface)> surface_;
    std::unique_ptr<SDL_Renderer, decltype(&SDL_DestroyRenderer)> renderer_;
    Drawing drawing_;
    std::string renderer_record_;
};

void frame_acceptance(const Case& test, const Frame& frame, const Mask& mask,
                      const std::array<UiKeyGeometry, key_total>& keys) {
    std::size_t cyan_count = 0;
    for (std::size_t at = 0; at < frame.pixels.size(); ++at) {
        const auto flags = mask.flags[at];
        const auto pixel = frame.pixels[at];
        require(pixel[3] == 255, "complete painted/cleared frame remains opaque");
        if (pixel == cyan) ++cyan_count;
        if (active(test) && test.focus_manual >= 0)
            require((pixel == cyan) == ((flags & VisibleFocus) != 0),
                    "complete cyan-pixel set equals independent final visible key-focus ink");
        if ((flags & VisibleFocus) != 0) require(pixel == cyan, "every visible focus pixel is exact opaque cyan");
        if ((flags & VisibleHeldCue) != 0) require(pixel == brass, "every visible held-cue pixel is exact opaque brass");
        if ((flags & VisibleOutline) != 0) {
            require(mask.owner[at] >= 0 && mask.owner[at] < static_cast<std::int16_t>(manual_total), "protected idle outline has original manual owner");
            const bool sharp = keys[static_cast<std::size_t>(mask.owner[at])].accidental;
            require(pixel == (sharp ? Pixel{5, 6, 5, 255} : Pixel{83, 65, 42, 255}),
                    "final unchanged opaque hit-outline ink retains its original exact RGBA");
        }
        if ((flags & Editable) != 0) require(pixel != cyan, "editable material contains no unexpected cyan focus pixel");
    }
    if (test.focus_manual >= 0) require(cyan_count == mask.counts[4] && cyan_count > 0, "complete exact nonempty manual focus set");
    else if (test.clip == Clip::None) require(cyan_count > 0, "declared non-key control focus remains visible");
    else require(cyan_count == 0, "physical key-only/empty clips exclude the non-key focus");
    if (active(test) && test.clip == Clip::None)
        for (const auto count : mask.visible_keys) require(count > 0, "all 147 source key faces have final visible pixels");
    if (test.clip == Clip::Empty) {
        require(frame.incoming.clipped && frame.incoming.clip.w == 0 && frame.incoming.clip.h == 0 &&
                mask.counts[0] == 0 && mask.counts[2] == 0, "enabled empty clip has no key/material coverage");
        require(std::all_of(frame.pixels.begin(), frame.pixels.end(), [](Pixel p) { return p == walnut; }),
                "enabled empty clip retains only SDL's full-surface clear");
        totals.empty_clip_pixels += frame.pixels.size();
    }
}
void clip_acceptance(const Case& test, const UiModel& model, const Frame& frame) {
    if (test.clip == Clip::None) return;
    Target companion(test, true);
    const auto full = companion.paint(model);
    require(frame.width == full.width && frame.height == full.height && frame.model == full.model &&
            equal(frame.incoming.viewport, full.incoming.viewport) && frame.renderer == full.renderer,
            "clip companion uses the identical full frame, model, physical viewport and backend");
    std::size_t count = 0;
    for (int y = 0; y < frame.height; ++y) for (int x = 0; x < frame.width; ++x) {
        const auto at = frame.at(x, y);
        if (visible(frame.incoming, x, y)) {
            require(frame.pixels[at] == full.pixels[at], "every visible clipped pixel equals the same full-companion physical pixel");
            ++count;
        } else require(frame.pixels[at] == walnut, "no paint escapes enabled clip/viewport after the documented full clear");
    }
    require(count == (test.clip == Clip::Crossing ? 465U * 560U : 0U), "exact declared physical clip area");
    totals.clip_pixels += count;
    ++totals.clip_companions;
}

struct Sample {
    std::size_t division{}, key{}, band_index{}, count{};
    bool sharp{}, front{};
    std::array<int, 2> source_interval{}, source_face{};
    std::array<std::uint64_t, 4> rgba_sum{};
    std::uint64_t y_numerator{};
};
constexpr std::array<std::string_view, 6> band_names{"back", "middle", "nose", "shoulder", "front_high", "front_low"};
std::vector<Sample> material_samples(std::size_t case_index, const Case& test, const Frame& frame, const Mask& mask,
                                     const std::array<UiKeyGeometry, key_total>& keys) {
    std::vector<Sample> result;
    if (case_index > 1) return result;
    constexpr int intervals[2][2][6][2] = {
        {{{562,568},{607,613},{651,657},{666,669},{674,679},{682,687}},
         {{557,562},{575,580},{595,600},{603,605},{609,614},{617,622}}},
        {{{736,742},{781,787},{825,831},{840,843},{848,853},{856,861}},
         {{730,735},{748,753},{768,773},{776,778},{782,787},{790,795}}}
    };
    constexpr int faces[2][2][2][2] = {
        {{{548,670},{670,690}}, {{548,606},{606,625}}},
        {{{718,844},{844,864}}, {{718,779},{779,798}}}
    };
    constexpr std::size_t indices[2][3] = {{12,29,48},{13,30,49}};
    const auto spec = surface_spec(test);
    for (std::size_t manual = 0; manual < 2; ++manual)
        for (std::size_t material = 0; material < 2; ++material)
            for (const auto index : indices[material]) for (std::size_t b = 0; b < 6; ++b) {
                const auto owner = manual * 61 + index;
                const auto& key = keys[owner];
                require(key.accidental == (material == 1) && !is_held(test, manual, index) && !is_focused(test, manual, index),
                        "appearance witness has the declared idle/unfocused material and pitch");
                const std::size_t front = b >= 4 ? 1 : 0;
                const auto& q = front == 1 ? key.front : key.top;
                Sample sample{manual, index, b, 0, material == 1, front == 1,
                    {intervals[manual][material][b][0], intervals[manual][material][b][1]},
                    {faces[manual][material][front][0], faces[manual][material][front][1]}, {}, 0};
                const double source_height = sample.source_face[1] - sample.source_face[0];
                const double v0 = (sample.source_interval[0] - sample.source_face[0]) / source_height;
                const double v1 = (sample.source_interval[1] - sample.source_face[0]) / source_height;
                const auto& p = q.points;
                raster(q, spec, frame.incoming, [&](int x, int y) {
                    const double logical_y = (static_cast<double>(y - frame.incoming.viewport.y) + 0.5) / frame.incoming.sy;
                    const double v = (logical_y - p[0].y) / (static_cast<double>(p[3].y) - p[0].y);
                    if (v < v0 || v >= v1) return;
                    const double a = p[0].x + (static_cast<double>(p[3].x) - p[0].x) * v;
                    const double z = p[1].x + (static_cast<double>(p[2].x) - p[1].x) * v;
                    const double logical_x = (static_cast<double>(x - frame.incoming.viewport.x) + 0.5) / frame.incoming.sx;
                    const double u = (logical_x - a) / (z - a);
                    if (u < 0.35 || u >= 0.65) return;
                    const auto at = frame.at(x, y);
                    require(mask.owner[at] == static_cast<std::int16_t>(owner) &&
                            (mask.flags[at] & (VisibleHeld | VisibleFocus | VisibleHeldCue)) == 0,
                            "every quiet/shoulder sample is on its unchanged visible idle key face");
                    const auto pixel = frame.pixels[at];
                    for (std::size_t channel = 0; channel < 4; ++channel) sample.rgba_sum[channel] += pixel[channel];
                    sample.y_numerator += 2126U * pixel[0] + 7152U * pixel[1] + 722U * pixel[2];
                    ++sample.count;
                });
                require(sample.count > 0, "each independently registered per-key appearance window has samples");
                result.push_back(sample);
            }
    require(result.size() == 72, "exactly 72 per-key material windows without pooling manuals or keys");
    totals.sample_windows += result.size();
    return result;
}

void write_transform(std::ostream& out, const Transform& t) {
    out << "{\"scale\":[" << t.sx << ',' << t.sy << "],\"viewport\":"; rect(out, t.viewport);
    out << ",\"clip\":"; rect(out, t.clip);
    out << ",\"logical_viewport\":"; rect(out, t.logical_viewport);
    out << ",\"logical_clip\":"; rect(out, t.logical_clip);
    out << ",\"clip_enabled\":" << t.clipped << ",\"blend\":" << static_cast<unsigned>(t.blend) << ",\"draw_color\":";
    array(out, t.color, [](auto& stream, auto value) { stream << static_cast<unsigned>(value); });
    out << '}';
}
void write_case(std::ostream& out, std::size_t index, const Case& test) {
    const auto spec = surface_spec(test);
    out << "{\"index\":" << index << ",\"number\":" << index + 1 << ",\"name\":\"" << test.name
        << "\",\"logical_size\":[" << test.width << ',' << test.height << "],\"scale\":[" << test.rx << ',' << test.ry
        << "],\"origin\":[" << test.origin_x << ',' << test.origin_y << "],\"output_size\":[" << spec.width << ',' << spec.height
        << "],\"viewport\":"; rect(out, spec.viewport);
    out << ",\"clip\":"; rect(out, physical_clip(test));
    out << ",\"clip_kind\":\"" << clip_name(test.clip) << "\",\"clip_enabled\":" << (test.clip != Clip::None)
        << ",\"held_kind\":" << static_cast<unsigned>(test.held) << ",\"focus\":"; control_id(out, expected_focus(test));
    out << ",\"workspace\":" << static_cast<unsigned>(test.workspace)
        << ",\"presentation\":" << static_cast<unsigned>(test.presentation) << ",\"active\":" << active(test)
        << ",\"whole_frame_equality_required\":" << whole_equal(test)
        << ",\"full_clip_companion_index\":";
    if (test.clip != Clip::None) out << 3; else out << "null";
    out << '}';
}
void write_masks(std::ostream& out, const Mask& mask) {
    out << "{\"source\":\"independent-before-source-binary32-geometry\",\"dilation\":0,\"encoding\":\"row-runs-y-xbegin-xend-flags-owner\""
        << ",\"flag_bits\":{\"original_manual_face\":1,\"original_idle_face\":2,\"editable\":4,\"visible_held\":8,"
        << "\"visible_focus\":16,\"visible_held_cue\":32,\"visible_unchanged_outline\":64,\"complete_pedal_region\":128,\"complete_preset_region\":256}"
        << ",\"owner_encoding\":\"Upper=0..60;Lower=61..121;Pedals=122..146;none=-1\""
        << ",\"outline_rule\":\"original-opaque-hit-outline-minus-later-declared-editable-material-overdraw-then-later-opaque-key-occlusion\""
        << ",\"counts_by_bit\":";
    array(out, mask.counts, [](auto& stream, auto value) { stream << value; });
    out << ",\"protected_exterior_pixels\":" << mask.exterior << ",\"editable_faces_by_manual_top_front\":";
    array(out, mask.editable_faces, [](auto& stream, const auto& values) { array(stream, values, [](auto& s, auto value) { s << value; }); });
    out << ",\"visible_pixels_by_key\":"; array(out, mask.visible_keys, [](auto& stream, auto value) { stream << value; });
    out << ",\"held_pixels_by_key\":"; array(out, mask.held_keys, [](auto& stream, auto value) { stream << value; });
    out << ",\"held_cue_pixels_by_key\":"; array(out, mask.held_cues, [](auto& stream, auto value) { stream << value; });
    out << ",\"runs\":[";
    bool first = true;
    for (int y = 0; y < mask.height; ++y) for (int x = 0; x < mask.width;) {
        const auto at = mask.at(x, y);
        const auto flags = mask.flags[at];
        const auto owner = mask.owner[at];
        const int begin = x++;
        while (x < mask.width && mask.flags[mask.at(x, y)] == flags && mask.owner[mask.at(x, y)] == owner) ++x;
        if (flags == 0 && owner < 0) continue;
        if (!first) out << ',';
        first = false;
        out << '[' << y << ',' << begin << ',' << x << ',' << flags << ',' << owner << ']';
    }
    out << "]}";
}
void write_cyan_runs(std::ostream& out, const Frame& frame) {
    out << '[';
    bool first = true;
    for (int y = 0; y < frame.height; ++y) for (int x = 0; x < frame.width;) {
        if (frame.pixels[frame.at(x, y)] != cyan) { ++x; continue; }
        const int begin = x++;
        while (x < frame.width && frame.pixels[frame.at(x, y)] == cyan) ++x;
        if (!first) out << ',';
        first = false;
        out << '[' << y << ',' << begin << ',' << x << ']';
    }
    out << ']';
}
void write_samples(std::ostream& out, const std::vector<Sample>& samples) {
    array(out, samples, [](auto& stream, const Sample& sample) {
        stream << "{\"manual\":" << sample.division << ",\"key\":" << sample.key << ",\"material\":\""
            << (sample.sharp ? "ebony" : "ivory") << "\",\"band\":\"" << band_names[sample.band_index]
            << "\",\"face\":\"" << (sample.front ? "front" : "top") << "\",\"u\":[0.35,0.65],\"source_y\":["
            << sample.source_interval[0] << ',' << sample.source_interval[1] << "],\"source_face_y\":["
            << sample.source_face[0] << ',' << sample.source_face[1] << "],\"count\":" << sample.count << ",\"rgba_sum\":";
        array(stream, sample.rgba_sum, [](auto& s, auto value) { s << value; });
        stream << ",\"encoded_y_numerator\":" << sample.y_numerator
               << ",\"encoded_y_denominator\":" << sample.count * 10000U << '}';
    });
}
void stream(std::size_t index, const Case& test, const Frame& frame, const Mask& mask,
            const std::array<UiKeyGeometry, key_total>& keys, const std::vector<Sample>& samples) {
    std::ostringstream out;
    out << std::boolalpha << std::setprecision(std::numeric_limits<double>::max_digits10)
        << "{\"schema\":1,\"protocol\":\"" << protocol << "\",\"case\":" << index << ",\"case_spec\":";
    write_case(out, index, test);
    out << ",\"oracle_before_revision\":\"" << before_revision << "\",\"oracle_published_before_revision\":\""
        << published_before_revision << "\",\"oracle_before_tree\":\"" << before_tree
        << "\",\"width\":" << frame.width << ",\"height\":" << frame.height << ",\"output_size\":[" << frame.width << ',' << frame.height
        << "],\"scale\":[" << frame.incoming.sx << ',' << frame.incoming.sy << "],\"viewport\":"; rect(out, frame.incoming.viewport);
    out << ",\"clip\":"; rect(out, frame.incoming.clip);
    out << ",\"clip_enabled\":" << frame.incoming.clipped << ",\"incoming_renderer_state\":"; write_transform(out, frame.incoming);
    out << ",\"outgoing_renderer_state\":"; write_transform(out, frame.outgoing);
    out << ",\"renderer\":" << frame.renderer << ",\"view_info\":" << info_record() << ",\"model\":" << frame.model
        << ",\"independent_original_geometry\":";
    if (active(test)) array(out, keys, [](auto& s, const auto& key) { key_geometry(s, key); }); else out << "[]";
    out << ",\"mask\":"; write_masks(out, mask);
    out << ",\"observed_complete_cyan_runs\":"; write_cyan_runs(out, frame);
    out << ",\"material_samples\":"; write_samples(out, samples);
    out << ",\"pixel_format\":\"RGBA8-row-major-top-down\",\"bytes\":" << frame.pixels.size() * sizeof(Pixel) << "}\n";
    std::cout << out.str();
    std::cout.write(reinterpret_cast<const char*>(frame.pixels.data()), static_cast<std::streamsize>(frame.pixels.size() * sizeof(Pixel)));
    std::cout.flush();
    require(static_cast<bool>(std::cout), "write one JSON header then exact raw RGBA payload, without a trailer");
}
} // namespace

int main(int argc, char* argv[]) {
    SDL_SetMainReady();
    std::string_view current = "argument parsing";
    try {
        if (argc == 2 && std::string_view(argv[1]) == "--list") {
            std::cout << std::boolalpha << std::setprecision(std::numeric_limits<float>::max_digits10)
                << "{\"schema\":1,\"protocol\":\"" << protocol << "\",\"cases\":" << fixtures.size() << ",\"index_base\":0,\"fixtures\":[";
            for (std::size_t i = 0; i < fixtures.size(); ++i) { if (i != 0) std::cout << ','; write_case(std::cout, i, fixtures[i]); }
            std::cout << "]}\n";
            return EXIT_SUCCESS;
        }
        std::size_t selected = fixtures.size();
        if (argc != 1) {
            require(argc == 3 && std::string_view(argv[1]) == "--case", "expected --list, --case INDEX, or no arguments");
            const std::string_view value(argv[2]);
            const auto parsed = std::from_chars(value.data(), value.data() + value.size(), selected);
            require(parsed.ec == std::errc{} && parsed.ptr == value.data() + value.size() && selected < fixtures.size(), "bounded zero-based case index 0..15");
#ifdef _WIN32
            require(_setmode(_fileno(stdout), _O_BINARY) != -1, "binary raw-frame stdout");
#endif
        }
        require(SDL_Init(0) == 0, "initialize SDL without an audio device or window");
        for (std::size_t index = 0; index < fixtures.size(); ++index) {
            if (selected != fixtures.size() && selected != index) continue;
            const auto& test = fixtures[index];
            current = test.name;
            const auto model = state_for(test);
            const auto keys = original_keys(test);
            check_geometry(test, model, keys);
            Target target(test);
            const auto frame = target.paint(model);
            const auto mask = original_mask(test, surface_spec(test), frame.incoming, keys);
            frame_acceptance(test, frame, mask, keys);
            clip_acceptance(test, model, frame);
            const auto samples = material_samples(index, test, frame, mask, keys);
            if (selected != fixtures.size()) stream(index, test, frame, mask, keys, samples);
            else if (index < 2) {
                auto alternate = test;
                alternate.held = Held::Mixed; alternate.focus_manual = 0; alternate.focus_key = 13;
                (void)target.paint(state_for(alternate));
                const auto repeated = target.paint(model);
                require(repeated.pixels == frame.pixels && repeated.model == frame.model &&
                        same_transform(repeated.incoming, frame.incoming) && same_transform(repeated.outgoing, frame.outgoing) &&
                        repeated.outgoing.color == frame.outgoing.color, "canonical/minimum repeat exactly after a different held/focus state");
                Target fresh(test);
                const auto recreated = fresh.paint(model);
                require(recreated.pixels == frame.pixels && recreated.model == frame.model &&
                        same_transform(recreated.outgoing, frame.outgoing) && recreated.outgoing.color == frame.outgoing.color,
                        "canonical/minimum repeat exactly on a fresh renderer");
                totals.repeats += 2;
            }
            ++totals.cases;
        }
        SDL_Quit();
        if (selected == fixtures.size()) {
            require(totals.cases == 16 && totals.clip_companions == 2 && totals.repeats == 4 && totals.sample_windows == 144,
                    "all sixteen cases, both clip companions, four repetitions and 144 per-key sample observations executed");
            std::cout << "{\"schema\":1,\"protocol\":\"" << protocol << "\",\"status\":\"passed\",\"scope\":\"fixture-only; paired-material-and-whole-interface-admission-remain-separate\""
                << ",\"cases\":" << totals.cases << ",\"checks\":" << totals.checks << ",\"state_restorations\":" << totals.state_restorations
                << ",\"independently_checked_geometry_keys\":" << totals.geometry_keys << ",\"editable_pixels\":" << totals.support_pixels
                << ",\"protected_exterior_pixels\":" << totals.exterior_pixels << ",\"visible_focus_pixels\":" << totals.focus_pixels
                << ",\"visible_held_pixels\":" << totals.held_pixels << ",\"visible_held_cue_pixels\":" << totals.held_cue_pixels
                << ",\"visible_unchanged_outline_pixels\":" << totals.outline_pixels << ",\"clip_companions\":" << totals.clip_companions
                << ",\"visible_clip_pixels\":" << totals.clip_pixels << ",\"empty_clip_pixels\":" << totals.empty_clip_pixels
                << ",\"same_and_fresh_repeats\":" << totals.repeats << ",\"material_sample_windows\":" << totals.sample_windows << "}\n";
        }
        return EXIT_SUCCESS;
    } catch (const std::exception& error) {
        std::cerr << "Manual-key material fixture failed [" << current << "]: " << error.what() << '\n';
        SDL_Quit();
        return EXIT_FAILURE;
    }
}
