#include "InstrumentView.h"

#include <SDL.h>

#include <algorithm>
#include <array>
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

// Frozen supplemental fixtures for LOWER_RACK_MATERIAL_CONTRACT.md v1.
// Build this same source against the genuine before painter before changing
// production paint. Streams carry observations, never material allowances or
// an alternative material implementation. The paired checker owns its mask,
// before/after opaque-child equality and numerical reference screens.
namespace {
using namespace hammond;
using namespace hammond::standalone;
using Pixel = std::array<std::uint8_t, 4>;
static_assert(sizeof(Pixel) == 4);
constexpr std::string_view protocol = "lower-rack-material-v1";
constexpr std::array<float, 9> centers{685, 734, 782, 830, 878, 927, 975, 1024, 1074};
constexpr std::array<std::string_view, 9> footage{
    "16'", "5 1/3'", "8'", "4'", "2 2/3'", "2'", "1 3/5'", "1 1/3'", "1'"};

struct Totals {
    std::size_t cases{}, checks{}, state_restorations{}, clip_companions{}, clip_pixels{};
    std::size_t child_probes{}, probe_pixels{}, glyphs{}, ink_pixels{}, focus_cases{}, focus_pixels{}, repeats{};
} totals;

void require(bool condition, std::string_view message) {
    ++totals.checks;
    if (!condition) throw std::runtime_error(std::string(message) + ": " + SDL_GetError());
}

enum class Clip { None, Left, Right, Top, Bottom, Disjoint, PhysicalEmpty, LogicalEmpty };
struct Case {
    float width{1672}, height{941}, scale_x{1}, scale_y{1};
    unsigned level{4};
    PresetSelection route{PresetSelection::BankB};
    bool pending{}, held{true};
    int origin_x{13}, origin_y{17};
    Clip clip{Clip::None};
    bool resource{};
};

Case isotropic(float width, float height, float scale, unsigned level,
               PresetSelection route, bool pending, bool held,
               int origin_x = 13, int origin_y = 17,
               Clip clip = Clip::None, bool resource = false) {
    return {width, height, scale, scale, level, route, pending, held,
            origin_x, origin_y, clip, resource};
}

std::vector<Case> cases() {
    std::vector<Case> result{
        isotropic(1672, 941, 1, 0, PresetSelection::BankB, false, false),
        isotropic(1672, 941, 1.5F, 4, PresetSelection::BankA, true, true),
        isotropic(1672, 941, 2, 8, PresetSelection::D, false, true),
        isotropic(1400, 820, 1, 4, PresetSelection::Cancel, true, false),
        isotropic(1400, 820, 1.5F, 8, PresetSelection::BankB, false, false),
        isotropic(1400, 820, 2, 0, PresetSelection::BankA, true, true),
        isotropic(1920, 1080, 1, 8, PresetSelection::D, true, true),
        isotropic(1920, 1080, 1.5F, 0, PresetSelection::Cancel, false, false),
        isotropic(1920, 1080, 2, 4, PresetSelection::BankB, true, false),
    };
    for (const auto clip : {Clip::Left, Clip::Right, Clip::Top, Clip::Bottom})
        for (const float scale : {1.0F, 1.5F, 2.0F})
            result.push_back(isotropic(1672, 941, scale, 4, PresetSelection::BankB, false, true,
                                      scale == 1.5F ? 0 : 13, scale == 1.5F ? 0 : 17, clip));
    result.push_back(isotropic(1672, 941, 1, 4, PresetSelection::BankB, false, true, 13, 17, Clip::Disjoint));
    result.push_back(isotropic(1672, 941, 1.5F, 4, PresetSelection::BankB, false, true, 13, 17, Clip::PhysicalEmpty));
    result.push_back(isotropic(1672, 941, 2, 4, PresetSelection::BankB, false, true, 13, 17, Clip::LogicalEmpty));
    for (const float scale : {1.0F, 1.5F, 2.0F})
        result.push_back(isotropic(8192, 8192, scale, 4, PresetSelection::BankB, false, true,
                                  0, 0, Clip::None, true));
    result.push_back(isotropic(1672, 941, 1, 0, PresetSelection::BankB, false, false, 0, 0));
    result.push_back(isotropic(1672, 941, 1, 4, PresetSelection::BankB, false, true, 0, 0));
    result.push_back(isotropic(1672, 941, 1, 8, PresetSelection::D, true, true, 0, 0));
    result.push_back(isotropic(1920, 820, 1, 4, PresetSelection::BankB, false, true));
    result.push_back({1672, 941, 1.5F, 2, 8, PresetSelection::BankA, true, true});
    require(result.size() == 32, "exactly 32 supplemental indices");
    return result;
}

DrawbarBank edited_bank(const Case& test) {
    return test.route == PresetSelection::BankA ? DrawbarBank::A : DrawbarBank::B;
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

std::string_view clip_name(const Case& test) {
    switch (test.clip) {
    case Clip::None: return "disabled";
    case Clip::Left: return test.scale_x == 1.5F ? "logical-left" : "physical-left";
    case Clip::Right: return test.scale_x == 1.5F ? "logical-right" : "physical-right";
    case Clip::Top: return test.scale_x == 1.5F ? "logical-top" : "physical-top";
    case Clip::Bottom: return test.scale_x == 1.5F ? "logical-bottom" : "physical-bottom";
    case Clip::Disjoint: return "physical-disjoint";
    case Clip::PhysicalEmpty: return "physical-empty";
    case Clip::LogicalEmpty: return "logical-empty";
    }
    throw std::runtime_error("undeclared fixture clip");
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

UiModel state_for(const Case& test) {
    UiModel model;
    require(model.resize(test.width, test.height) && model.set_presentation(UiPresentation::Dimensional) &&
            model.set_workspace(UiWorkspace::Play), "admitted fixed Dimensional Play geometry");
    SessionSnapshot snapshot;
    snapshot.controls = model.view().controls;
    for (auto& manual : snapshot.controls.drawbars)
        for (auto& bank : manual) bank.fill(static_cast<std::uint8_t>(test.level));
    snapshot.controls.expression = 0.625;
    snapshot.controls.pedal_drawbars = {3, 7};
    snapshot.controls.percussion = {true, PercussionHarmonic::Second, PercussionVolume::Normal, PercussionDecay::Slow};
    ControlState applied;
    require(applied.restore(snapshot.controls) && applied.select_preset(Manual::Lower, test.route), "fixed applied route");
    snapshot.controls = applied.snapshot();
    snapshot.held_keys[0][24] = snapshot.held_keys[1][36] = snapshot.held_pedals[12] = test.held;
    snapshot.frame_clock = 38400;
    snapshot.sample_rate = 48000;
    snapshot.peak = 0.125F;
    snapshot.prepared = snapshot.running = true;
    snapshot.publication_revision = 4;
    model.observe(snapshot);
    require(model.activate({UiControlKind::EditBank, Manual::Lower, edited_bank(test)}).count == 0,
            "editing bank emits no musical command");
    auto expected = snapshot.controls;
    if (test.pending) {
        const auto desired = test.route == PresetSelection::BankB ? PresetSelection::BankA : PresetSelection::BankB;
        require(model.activate({UiControlKind::PresetKey, Manual::Lower, DrawbarBank::A,
                               static_cast<std::uint8_t>(desired)}).count == 1, "unacknowledged pending route");
        ControlState requested;
        require(requested.restore(expected) && requested.select_preset(Manual::Lower, desired), "independent desired snapshot");
        expected = requested.snapshot();
    }
    const UiControlId focus{UiControlKind::ManualDrawbar, Manual::Lower, edited_bank(test),
                            static_cast<std::uint8_t>(test.level)};
    for (unsigned step = 0; step < 72 && model.view().focus != focus; ++step)
        require(model.key({UiKey::Tab, true}).count == 0 && model.key({UiKey::Tab, false}).count == 0,
                "normal focus traversal emits no commands");
    require(model.view().focus == focus && model.view().edited_banks[1] == edited_bank(test),
            "declared Lower drawbar focus in edited bank");
    require(model.view().controls == expected && session_record(model.view().applied) == session_record(snapshot) &&
            model.view().controls_pending == test.pending, "identical complete desired/applied copied snapshots");
    require(model.layout().control_count == 68 && model.layout().manual_keys.size() * kManualKeyCount +
            model.layout().pedal_keys.size() == 147, "complete control and playing-key inventory");
    std::size_t presets = 0;
    for (const auto& control : model.layout().controls)
        if (control.id.kind == UiControlKind::PresetKey) ++presets;
    require(presets == 24, "complete preset inventory");
    return model;
}

// These calculations configure declared fixtures only. The checker must derive
// material support separately; no support or mask is emitted in a stream.
float f32(float value) {
    volatile float rounded = value;
    return rounded;
}
UiRect canonical(const Case& test, float left, float top, float width, float height) {
    const float sx = f32(test.width / 1672.0F), sy = f32(test.height / 941.0F);
    const float x = f32(left * sx), y = f32(top * sy);
    return {x, y, f32(f32(f32(left + width) * sx) - x),
                  f32(f32(f32(top + height) * sy) - y)};
}
UiRect inset_for(const Case& test) {
    const float sx = f32(test.width / 1672.0F), sy = f32(test.height / 941.0F);
    const float bx = f32(600.0F * sx), by = f32(269.0F * sy);
    const float bw = f32(f32(1116.0F * sx) - bx), bh = f32(f32(508.0F * sy) - by);
    const float dx = f32(4.0F * sx), dy = f32(4.0F * sy);
    return {f32(bx + dx), f32(by + dy), std::max(0.0F, f32(bw - f32(2.0F * dx))),
            std::max(0.0F, f32(bh - f32(2.0F * dy)))};
}
SDL_Rect intrinsic(const Case& test) {
    const auto inset = inset_for(test);
    const auto edge_x = [&](double value) { return static_cast<int>(std::ceil(value * test.scale_x - 0.5)); };
    const auto edge_y = [&](double value) { return static_cast<int>(std::ceil(value * test.scale_y - 0.5)); };
    const int left = edge_x(inset.x), top = edge_y(inset.y);
    return {left, top, edge_x(static_cast<double>(inset.x) + inset.width) - left,
                       edge_y(static_cast<double>(inset.y) + inset.height) - top};
}

bool equal(SDL_Rect a, SDL_Rect b) { return a.x == b.x && a.y == b.y && a.w == b.w && a.h == b.h; }
bool equal(UiRect a, UiRect b) {
    return a.x == b.x && a.y == b.y && a.width == b.width && a.height == b.height;
}
struct Transform {
    float sx{}, sy{};
    SDL_Rect viewport{}, clip{}, logical_viewport{}, logical_clip{};
    bool clipped{};
    SDL_BlendMode blend{};
};
Transform transform(SDL_Renderer* renderer) {
    Transform result;
    SDL_RenderGetScale(renderer, &result.sx, &result.sy);
    SDL_RenderGetViewport(renderer, &result.logical_viewport);
    SDL_RenderGetClipRect(renderer, &result.logical_clip);
    result.clipped = SDL_RenderIsClipEnabled(renderer) == SDL_TRUE;
    require(SDL_GetRenderDrawBlendMode(renderer, &result.blend) == 0, "query blend mode");
    require(SDL_RenderSetScale(renderer, 1, 1) == 0, "query exact physical observations");
    SDL_RenderGetViewport(renderer, &result.viewport);
    SDL_RenderGetClipRect(renderer, &result.clip);
    require(SDL_RenderSetScale(renderer, result.sx, result.sy) == 0, "restore scale after query");
    return result;
}
bool equal(const Transform& a, const Transform& b) {
    return a.sx == b.sx && a.sy == b.sy && equal(a.viewport, b.viewport) && equal(a.clip, b.clip) &&
           equal(a.logical_viewport, b.logical_viewport) && equal(a.logical_clip, b.logical_clip) &&
           a.clipped == b.clipped && a.blend == b.blend;
}
bool visible(const Transform& t, int x, int y) {
    const int xx = x - t.viewport.x, yy = y - t.viewport.y;
    return xx >= 0 && yy >= 0 && xx < t.viewport.w && yy < t.viewport.h &&
           (!t.clipped || (xx >= t.clip.x && yy >= t.clip.y &&
                          xx < t.clip.x + t.clip.w && yy < t.clip.y + t.clip.h));
}

struct Frame {
    int width{}, height{};
    Transform coordinates;
    std::vector<Pixel> pixels;
    std::string model;
    std::size_t at(int x, int y) const {
        return static_cast<std::size_t>(y) * static_cast<std::size_t>(width) + static_cast<std::size_t>(x);
    }
};
struct SurfaceSpec {
    int width{}, height{};
    SDL_Rect viewport{};
};
SurfaceSpec surface_spec(const Case& test) {
    const int width = static_cast<int>(std::ceil(test.width * test.scale_x));
    const int height = static_cast<int>(std::ceil(test.height * test.scale_y));
    const auto inset = intrinsic(test);
    if (test.resource) return {64, 64, {-inset.x, -inset.y, width, height}};
    return {width + 2 * test.origin_x, height + 2 * test.origin_y,
            {test.origin_x, test.origin_y, width, height}};
}

class Target {
public:
    explicit Target(const Case& test, bool full_clip_companion = false) :
        spec_(surface_spec(test)),
        surface_(SDL_CreateRGBSurfaceWithFormat(0, spec_.width, spec_.height, 32, SDL_PIXELFORMAT_RGBA32), SDL_FreeSurface),
        renderer_(surface_ ? SDL_CreateSoftwareRenderer(surface_.get()) : nullptr, SDL_DestroyRenderer),
        drawing_(renderer_.get()) {
        require(spec_.width > 0 && spec_.height > 0 && spec_.width <= 3900 && spec_.height <= 2200 &&
                surface_ && renderer_, "bounded software output allocation");
        require(!test.resource || (spec_.width == 64 && spec_.height == 64), "maximum geometry has 64x64 output");
        std::string error;
        require(drawing_.initialize(error), "initialize unchanged fonts/art");
        require(SDL_RenderSetScale(renderer_.get(), 1, 1) == 0 &&
                SDL_RenderSetViewport(renderer_.get(), &spec_.viewport) == 0, "install physical viewport");
        require(SDL_RenderSetClipRect(renderer_.get(), nullptr) == 0, "start with disabled clip");
        const auto box = intrinsic(test);
        const int left = box.x, top = box.y, right = box.x + box.w, bottom = box.y + box.h;
        if (!full_clip_companion && test.clip != Clip::None && test.clip != Clip::LogicalEmpty &&
            (test.scale_x != 1.5F || test.clip == Clip::PhysicalEmpty)) {
            SDL_Rect clip{};
            switch (test.clip) {
            case Clip::Left: clip = {left - 2, top - 2, 4, box.h + 4}; break;
            case Clip::Right: clip = {right - 2, top - 2, 4, box.h + 4}; break;
            case Clip::Top: clip = {left - 2, top - 2, box.w + 4, 4}; break;
            case Clip::Bottom: clip = {left - 2, bottom - 2, box.w + 4, 4}; break;
            case Clip::Disjoint: clip = {right + 4, top + 4, 8, 8}; break;
            case Clip::PhysicalEmpty: clip = {left, top, 0, 0}; break;
            default: throw std::runtime_error("unexpected physical clip case");
            }
            require(SDL_RenderSetClipRect(renderer_.get(), &clip) == 0, "install physical edge/empty clip");
        }
        require(SDL_RenderSetScale(renderer_.get(), test.scale_x, test.scale_y) == 0, "install incoming scale pair");
        if (!full_clip_companion && (test.clip == Clip::LogicalEmpty ||
            (test.scale_x == 1.5F && test.clip >= Clip::Left && test.clip <= Clip::Bottom))) {
            SDL_Rect clip{};
            switch (test.clip) {
            case Clip::Left: clip = {602, 300, 4, 160}; break;
            case Clip::Right: clip = {1110, 300, 4, 160}; break;
            case Clip::Top: clip = {618, 271, 474, 4}; break;
            case Clip::Bottom: clip = {618, 502, 474, 4}; break;
            case Clip::LogicalEmpty: clip = {604, 273, 0, 0}; break;
            default: throw std::runtime_error("unexpected logical clip case");
            }
            require(SDL_RenderSetClipRect(renderer_.get(), &clip) == 0, "install logical edge/empty clip");
        }
        const auto blend = test.clip == Clip::LogicalEmpty ? SDL_BLENDMODE_NONE : SDL_BLENDMODE_BLEND;
        require(SDL_SetRenderDrawBlendMode(renderer_.get(), blend) == 0, "install declared incoming blend");
        const auto actual = transform(renderer_.get());
        require(actual.sx == test.scale_x && actual.sy == test.scale_y && equal(actual.viewport, spec_.viewport) &&
                actual.clipped == (!full_clip_companion && test.clip != Clip::None) && actual.blend == blend,
                "actual physical viewport, scale, clip-enabled and blend match fixture");
        if (!full_clip_companion && (test.clip == Clip::PhysicalEmpty || test.clip == Clip::LogicalEmpty))
            require(actual.clipped && actual.clip.w == 0 && actual.clip.h == 0, "empty clips remain enabled");
    }

    Frame paint(const UiModel& model) {
        const auto before = transform(renderer_.get());
        const auto copied_model = model_record(model);
        InstrumentViewInfo info;
        info.audio_running = true;
        info.sample_rate = 48000;
        info.buffer_frames = 512;
        info.audio_driver = "fixed-software-fixture";
        info.device_name = "fixed copied state";
        info.status_message = "Percussion raster qualification";
        paint_instrument(drawing_, model, info);
        require(equal(before, transform(renderer_.get())), "paint restores physical/logical viewport, clip, scale and blend");
        require(copied_model == model_record(model), "paint preserves every copied view/state and geometry member");
        ++totals.state_restorations;
        auto frame = read(before);
        frame.model = copied_model;
        return frame;
    }

    Frame text(std::string_view value, UiRect box, float requested, TextFace face,
               std::vector<UiRect>& glyphs, float padding) {
        const auto coordinates = transform(renderer_.get());
        drawing_.clear({0, 0, 0, 0});
        float size = std::min(requested, box.height / 1.2F);
        const float width = drawing_.text_width(value, size, face);
        if (width > box.width - 2 * padding && width > 0)
            size *= std::max(0.1F, box.width - 2 * padding) / width;
        const float left = box.x + (box.width - drawing_.text_width(value, size, face)) / 2;
        const float top = box.y + (box.height - size * 1.2F) / 2;
        drawing_.text(value, left, top, size, {255, 255, 255}, face);
        float x = left;
        for (const char character : value) {
            const float advance = drawing_.text_width(std::string_view(&character, 1), size, face);
            if (character != ' ') glyphs.push_back({x, box.y, advance, box.height});
            x += advance;
        }
        require(equal(coordinates, transform(renderer_.get())), "literal ink render preserves transform");
        return read(coordinates);
    }

    Frame focus(UiRect bounds, float sx, float sy) {
        const auto coordinates = transform(renderer_.get());
        drawing_.clear({0, 0, 0, 0});
        const float x = std::min(2.0F * sx, bounds.width / 2.0F);
        const float y = std::min(2.0F * sy, bounds.height / 2.0F);
        drawing_.rect({bounds.x, bounds.y, bounds.width, y}, {165, 228, 223});
        drawing_.rect({bounds.x, bounds.y + bounds.height - y, bounds.width, y}, {165, 228, 223});
        drawing_.rect({bounds.x, bounds.y + y, x, bounds.height - 2.0F * y}, {165, 228, 223});
        drawing_.rect({bounds.x + bounds.width - x, bounds.y + y, x, bounds.height - 2.0F * y}, {165, 228, 223});
        require(equal(coordinates, transform(renderer_.get())), "independent focus render preserves transform");
        return read(coordinates);
    }

private:
    Frame read(const Transform& coordinates) {
        require(SDL_RenderFlush(renderer_.get()) == 0 && SDL_LockSurface(surface_.get()) == 0, "read exact RGBA bytes");
        Frame frame{spec_.width, spec_.height, coordinates, std::vector<Pixel>(
            static_cast<std::size_t>(spec_.width) * static_cast<std::size_t>(spec_.height)), {}};
        const auto* input = static_cast<const std::uint8_t*>(surface_->pixels);
        for (int y = 0; y < spec_.height; ++y)
            std::memcpy(frame.pixels.data() + frame.at(0, y),
                input + static_cast<std::size_t>(y) * static_cast<std::size_t>(surface_->pitch),
                static_cast<std::size_t>(spec_.width) * sizeof(Pixel));
        SDL_UnlockSurface(surface_.get());
        return frame;
    }
    SurfaceSpec spec_;
    std::unique_ptr<SDL_Surface, decltype(&SDL_FreeSurface)> surface_;
    std::unique_ptr<SDL_Renderer, decltype(&SDL_DestroyRenderer)> renderer_;
    Drawing drawing_;
};

double light(Pixel pixel) { return .2126 * pixel[0] + .7152 * pixel[1] + .0722 * pixel[2]; }
void literal_ink(Target& target, const Frame& actual, std::string_view value, UiRect box,
                 float size, TextFace face, float padding) {
    std::vector<UiRect> glyphs;
    const auto expected = target.text(value, box, size, face, glyphs, padding);
    const auto& t = actual.coordinates;
    for (const auto& glyph : glyphs) {
        std::size_t samples = 0, matches = 0;
        const int left = std::max(0, static_cast<int>(std::floor(glyph.x * t.sx + static_cast<float>(t.viewport.x))));
        const int right = std::min(actual.width, static_cast<int>(std::ceil((glyph.x + glyph.width) * t.sx + static_cast<float>(t.viewport.x))));
        const int top = std::max(0, static_cast<int>(std::floor(glyph.y * t.sy + static_cast<float>(t.viewport.y))));
        const int bottom = std::min(actual.height, static_cast<int>(std::ceil((glyph.y + glyph.height) * t.sy + static_cast<float>(t.viewport.y))));
        for (int y = top; y < bottom; ++y)
            for (int x = left; x < right; ++x) {
                const auto at = actual.at(x, y);
                if (light(expected.pixels[at]) < 180) continue;
                ++samples;
                if (light(actual.pixels[at]) > 90) ++matches;
            }
        require(samples > 0 && samples == matches, "every literal glyph retains all strong contrasting ink");
        ++totals.glyphs;
        totals.ink_pixels += samples;
    }
}

void opaque_probe(const Case& test, const Frame& frame, UiRect canonical_probe) {
    const auto box = canonical(test, canonical_probe.x, canonical_probe.y, canonical_probe.width, canonical_probe.height);
    const auto& t = frame.coordinates;
    const int left = static_cast<int>(std::ceil(static_cast<double>(box.x) * t.sx - 0.5)) + t.viewport.x + 1;
    const int top = static_cast<int>(std::ceil(static_cast<double>(box.y) * t.sy - 0.5)) + t.viewport.y + 1;
    const int right = static_cast<int>(std::ceil((static_cast<double>(box.x) + box.width) * t.sx - 0.5)) + t.viewport.x - 1;
    const int bottom = static_cast<int>(std::ceil((static_cast<double>(box.y) + box.height) * t.sy - 0.5)) + t.viewport.y - 1;
    require(right > left && bottom > top, "independent eroded child probe is nonempty");
    for (int y = top; y < bottom; ++y)
        for (int x = left; x < right; ++x) {
            require(x >= 0 && y >= 0 && x < frame.width && y < frame.height && visible(t, x, y),
                    "full-frame child probe is visible");
            require(frame.pixels[frame.at(x, y)][3] == 255, "child probe retains opaque RGBA");
            ++totals.probe_pixels;
        }
    ++totals.child_probes;
}

void full_frame_children(const Case& test, const UiModel& model, Target& target, const Frame& frame) {
    const float sx = test.width / 1672.0F, sy = test.height / 941.0F, font_scale = std::min(sx, sy);
    const auto rack = canonical(test, 600, 269, 516, 239);
    literal_ink(target, frame, "LOWER MANUAL DRAWBARS",
        {rack.x + 16.0F * sx, rack.y + 8.0F * sy, rack.width - 32.0F * sx, 27.0F * sy},
        16 * font_scale, TextFace::Serif, 3 * sx);
    const auto value = std::to_string(test.level);
    for (std::size_t index = 0; index < centers.size(); ++index) {
        const float center = centers[index];
        opaque_probe(test, frame, {center - 12, 320, 4, 130});
        opaque_probe(test, frame, {center - 10, 327 + 118 * static_cast<float>(test.level) / 8 - 10, 20, 12});
        literal_ink(target, frame, footage[index], canonical(test, center - 23, 467, 46, 23),
                    19 * font_scale, TextFace::Serif, 2 * sx);
        literal_ink(target, frame, value, canonical(test, center - 23, 491, 46, 15),
                    12 * font_scale, TextFace::Sans, 3 * sx);
    }
    const auto expected_bounds = canonical(test, centers[test.level] - 23, 309, 46, 197);
    const auto& layout = model.layout();
    const auto found = std::find_if(layout.controls.begin(), layout.controls.end(), [&](const auto& control) {
        return control.id == model.view().focus;
    });
    require(found != layout.controls.end() && equal(found->bounds, expected_bounds), "focus uses independently mapped control bounds");
    const auto expected_focus = target.focus(expected_bounds, sx, sy);
    const auto& t = frame.coordinates;
    const int left = std::max(0, static_cast<int>(std::floor(expected_bounds.x * t.sx)) + t.viewport.x - 1);
    const int top = std::max(0, static_cast<int>(std::floor(expected_bounds.y * t.sy)) + t.viewport.y - 1);
    const int right = std::min(frame.width, static_cast<int>(std::ceil((expected_bounds.x + expected_bounds.width) * t.sx)) + t.viewport.x + 1);
    const int bottom = std::min(frame.height, static_cast<int>(std::ceil((expected_bounds.y + expected_bounds.height) * t.sy)) + t.viewport.y + 1);
    std::size_t count = 0;
    for (int y = top; y < bottom; ++y)
        for (int x = left; x < right; ++x) {
            const auto at = frame.at(x, y);
            const bool actual = frame.pixels[at] == Pixel{165, 228, 223, 255};
            const bool expected = expected_focus.pixels[at] == Pixel{165, 228, 223, 255};
            require(actual == expected, "actual cyan focus positions equal complete independent outline");
            if (actual) ++count;
        }
    require(count > 0, "declared focus retains nonempty cyan ink");
    ++totals.focus_cases;
    totals.focus_pixels += count;
}

void ordinary_acceptance(const Case& test, const UiModel& model, Target& target, const Frame& frame) {
    if (test.clip != Clip::None) {
        Target companion(test, true);
        const auto full = companion.paint(model);
        require(full.width == frame.width && full.height == frame.height &&
                equal(full.coordinates.viewport, frame.coordinates.viewport) && full.model == frame.model,
                "full-clip companion retains output, viewport and complete model");
        for (int y = 0; y < frame.height; ++y)
            for (int x = 0; x < frame.width; ++x) {
                const auto at = frame.at(x, y);
                if (visible(frame.coordinates, x, y)) {
                    require(frame.pixels[at] == full.pixels[at], "clipping does not shift grain or illumination");
                    ++totals.clip_pixels;
                } else require(frame.pixels[at] == Pixel{85, 54, 36, 255}, "no paint escapes caller clip/viewport");
            }
        ++totals.clip_companions;
    } else if (!test.resource) full_frame_children(test, model, target, frame);
}

void stream(std::size_t index, const Case& test, const UiModel& model, const Frame& frame) {
    const auto& t = frame.coordinates;
    std::ostringstream out;
    out << std::boolalpha << std::setprecision(std::numeric_limits<float>::max_digits10)
        << "{\"schema\":1,\"protocol\":\"" << protocol << "\",\"case\":" << index
        << ",\"logical_size\":[" << test.width << ',' << test.height << ']'
        << ",\"width\":" << frame.width << ",\"height\":" << frame.height
        << ",\"output_size\":[" << frame.width << ',' << frame.height << ']'
        << ",\"scale\":[" << t.sx << ',' << t.sy << "],\"viewport\":";
    rect(out, t.viewport);
    out << ",\"clip\":";
    rect(out, t.clip);
    out << ",\"logical_viewport\":";
    rect(out, t.logical_viewport);
    out << ",\"logical_clip\":";
    rect(out, t.logical_clip);
    out << ",\"clip_enabled\":" << t.clipped << ",\"blend\":" << static_cast<unsigned>(t.blend)
        << ",\"clip_kind\":\"" << clip_name(test) << "\",\"level\":" << test.level
        << ",\"route\":\"" << route_name(test.route) << "\",\"route_index\":" << static_cast<unsigned>(test.route)
        << ",\"pending\":" << test.pending << ",\"held\":" << test.held
        << ",\"edited_bank\":\"" << (edited_bank(test) == DrawbarBank::A ? 'A' : 'B') << "\",\"focus\":";
    control_id(out, model.view().focus);
    out << ",\"resource_crop\":" << test.resource << ",\"model\":" << frame.model
        << ",\"bytes\":" << frame.pixels.size() * sizeof(Pixel) << "}\n";
    std::cout << out.str();
    std::cout.write(reinterpret_cast<const char*>(frame.pixels.data()),
                    static_cast<std::streamsize>(frame.pixels.size() * sizeof(Pixel)));
    std::cout.flush();
    require(static_cast<bool>(std::cout), "write JSON header and exact bounded RGBA bytes");
}
} // namespace

int main(int argc, char* argv[]) {
    SDL_SetMainReady();
    try {
        const auto fixtures = cases();
        if (argc == 2 && std::string_view(argv[1]) == "--list") {
            std::cout << "{\"schema\":1,\"protocol\":\"" << protocol << "\",\"cases\":" << fixtures.size() << "}\n";
            return 0;
        }
        std::size_t selected = fixtures.size();
        if (argc != 1) {
            require(argc == 3 && std::string_view(argv[1]) == "--case", "expected --case INDEX or --list");
            const std::string_view value(argv[2]);
            const auto parsed = std::from_chars(value.data(), value.data() + value.size(), selected);
            require(parsed.ec == std::errc{} && parsed.ptr == value.data() + value.size() && selected < fixtures.size(),
                    "bounded supplemental case index");
#ifdef _WIN32
            require(_setmode(_fileno(stdout), _O_BINARY) != -1, "binary frame stdout");
#endif
        }
        require(SDL_Init(0) == 0, "initialize SDL without window or audio");
        for (std::size_t index = 0; index < fixtures.size(); ++index) {
            if (selected != fixtures.size() && index != selected) continue;
            const auto& test = fixtures[index];
            const auto model = state_for(test);
            Target target(test);
            const auto frame = target.paint(model);
            if (selected != fixtures.size()) stream(index, test, model, frame);
            else {
                ordinary_acceptance(test, model, target, frame);
                if (index == 28) {
                    (void)target.paint(state_for(fixtures[27]));
                    (void)target.paint(state_for(fixtures[29]));
                    const auto repeated = target.paint(model);
                    require(repeated.pixels == frame.pixels && repeated.model == frame.model &&
                            equal(repeated.coordinates, frame.coordinates), "case 28 repeats exactly after other states on same renderer");
                    Target fresh(test);
                    const auto recreated = fresh.paint(model);
                    require(recreated.pixels == frame.pixels && recreated.model == frame.model &&
                            equal(recreated.coordinates, frame.coordinates), "case 28 repeats exactly on fresh renderer");
                    totals.repeats += 2;
                }
            }
            ++totals.cases;
        }
        SDL_Quit();
        if (selected == fixtures.size())
            std::cout << "{\"schema\":1,\"protocol\":\"" << protocol << "\",\"status\":\"passed\",\"cases\":" << totals.cases
                << ",\"checks\":" << totals.checks << ",\"state_restorations\":" << totals.state_restorations
                << ",\"clip_companions\":" << totals.clip_companions << ",\"visible_clip_pixels\":" << totals.clip_pixels
                << ",\"opaque_child_probes\":" << totals.child_probes << ",\"opaque_probe_pixels\":" << totals.probe_pixels
                << ",\"literal_glyphs\":" << totals.glyphs << ",\"strong_ink_pixels\":" << totals.ink_pixels
                << ",\"focus_cases\":" << totals.focus_cases << ",\"cyan_focus_pixels\":" << totals.focus_pixels
                << ",\"case_28_repeats\":" << totals.repeats
                << ",\"backend\":\"SDL software surface; fixed copied state; no audio/window\"}\n";
        return EXIT_SUCCESS;
    } catch (const std::exception& error) {
        std::cerr << "Lower-rack material raster acceptance failed: " << error.what() << '\n';
        SDL_Quit();
        return EXIT_FAILURE;
    }
}
