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

// Supplemental caller-clip fixtures for T2/T3. The same fixture is linked with
// independently preserved painters. No heading/title drawing oracle, text
// constants, candidate-derived support or permission mask belongs here.
namespace {
using namespace hammond;
using namespace hammond::standalone;
using Pixel = std::array<std::uint8_t, 4>;
static_assert(sizeof(Pixel) == 4);
constexpr std::string_view protocol = "typography-clips-v1";
constexpr std::size_t case_count = 48;
constexpr int maximum_width = 2160, maximum_height = 1240;

struct Totals {
    std::size_t cases{}, checks{}, paintings{}, clipped_cases{}, empty_cases{}, inactive_cases{};
    std::size_t protected_pixels{}, repaints{}, history_repaints{};
} totals;

void require(bool condition, std::string_view message) {
    ++totals.checks;
    if (!condition) throw std::runtime_error(std::string(message) + ": " + SDL_GetError());
}

struct Case {
    float width{1672}, height{941}, scale{1};
    int origin_x{}, origin_y{};
    std::string_view region{"scene"}, clip_kind{"disabled"};
    SDL_Rect clip_request{};
    bool clipped{}, logical_clip{}, pending{}, held{};
    unsigned level{}, focus_index{};
    Manual focus_manual{Manual::Upper};
    PresetSelection route{PresetSelection::BankA};
    UiWorkspace workspace{UiWorkspace::Play};
    UiPresentation presentation{UiPresentation::Dimensional};
    SDL_BlendMode blend{SDL_BLENDMODE_BLEND};
};

std::vector<Case> cases() {
    struct Cut { std::string_view region, edge; SDL_Rect clip; };
    // These are fixed caller windows, not text-support rectangles. Their edges
    // cross the original visible heading/title regions and four side rules.
    constexpr std::array<Cut, 16> cuts{{
        {"upper", "left", {279, 278, 301, 28}},
        {"upper", "right", {130, 278, 294, 28}},
        {"upper", "top", {130, 290, 450, 16}},
        {"upper", "bottom", {130, 278, 450, 16}},
        {"lower", "left", {799, 278, 301, 28}},
        {"lower", "right", {650, 278, 294, 28}},
        {"lower", "top", {650, 290, 450, 16}},
        {"lower", "bottom", {650, 278, 450, 16}},
        {"title", "left", {675, 14, 405, 46}},
        {"title", "right", {590, 14, 390, 46}},
        {"title", "top", {590, 31, 490, 29}},
        {"title", "bottom", {590, 14, 490, 25}},
        {"upper", "left-rule", {170, 288, 20, 7}},
        {"upper", "right-rule", {540, 288, 20, 7}},
        {"lower", "left-rule", {690, 288, 20, 7}},
        {"lower", "right-rule", {1060, 288, 20, 7}},
    }};
    constexpr std::array<PresetSelection, 4> routes{
        PresetSelection::BankA, PresetSelection::BankB, PresetSelection::D, PresetSelection::Cancel};
    std::vector<Case> result;
    const auto append = [&](Case c) {
        const auto i = result.size();
        c.origin_x = i % 2 == 0 ? 13 : -11;
        c.origin_y = i % 2 == 0 ? 17 : -7;
        c.level = static_cast<unsigned>((i % 3) * 4);
        c.route = routes[i % routes.size()];
        c.pending = i % 3 == 1;
        c.held = i % 3 != 0;
        c.focus_manual = static_cast<Manual>(i % 2);
        c.focus_index = static_cast<unsigned>(i % kDrawbarCount);
        c.blend = i % 2 == 0 ? SDL_BLENDMODE_BLEND : SDL_BLENDMODE_NONE;
        result.push_back(c);
    };
    for (const float scale : {1.0F, 1.25F})
        for (const auto& cut : cuts) {
            Case c;
            c.scale = scale; c.logical_clip = scale != 1;
            c.region = cut.region; c.clip_kind = cut.edge;
            c.clip_request = cut.clip; c.clipped = true;
            append(c);
        }
    constexpr std::array<Cut, 3> empty{{
        {"upper", "empty-width", {279, 278, 0, 28}},
        {"lower", "empty-height", {799, 278, 301, 0}},
        {"title", "empty-both", {675, 14, 0, 0}},
    }};
    for (const float scale : {1.0F, 1.25F})
        for (const auto& cut : empty) {
            Case c;
            c.scale = scale; c.logical_clip = scale != 1;
            c.region = cut.region; c.clip_kind = cut.edge;
            c.clip_request = cut.clip; c.clipped = true;
            append(c);
        }
    for (const float scale : {1.0F, 1.25F}) {
        Case c;
        c.scale = scale; c.logical_clip = scale != 1;
        c.clip_kind = "disjoint"; c.clip_request = {1690, 955, 8, 8}; c.clipped = true;
        append(c);
    }
    Case c;
    c.presentation = UiPresentation::Flat; append(c);               // 40
    c = {}; c.workspace = UiWorkspace::Rotary; append(c);            // 41
    c = {}; c.workspace = UiWorkspace::Service; c.scale = 1.25F; append(c); // 42
    c = {}; c.width = 960; c.height = 700; append(c);                 // 43
    c = {}; c.width = std::nextafter(1400.0F, 0.0F); c.scale = 1.25F; append(c); // 44
    c = {}; c.height = std::nextafter(820.0F, 0.0F); append(c);        // 45
    c = {}; append(c); result.back().origin_x = result.back().origin_y = 0; // 46
    c = {}; c.scale = 1.25F; append(c);                              // 47
    require(result.size() == case_count, "fixed 48-case supplemental inventory");
    return result;
}

bool active(const Case& c) {
    return c.workspace == UiWorkspace::Play && c.presentation == UiPresentation::Dimensional &&
           c.width >= 1400 && c.width <= kUiMaximumDimension &&
           c.height >= 820 && c.height <= kUiMaximumDimension;
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
            applied.select_preset(Manual::Lower, test.route), "complete fixed applied controls");
    snapshot.controls = applied.snapshot();
    snapshot.held_keys[0][24] = snapshot.held_keys[1][36] = snapshot.held_pedals[12] = test.held;
    snapshot.frame_clock = 38400; snapshot.sample_rate = 48000; snapshot.peak = 0.125F;
    snapshot.prepared = snapshot.running = true; snapshot.publication_revision = 4;
    model.observe(snapshot);
    for (const auto manual : {Manual::Upper, Manual::Lower})
        require(model.activate({UiControlKind::EditBank, manual, edited_bank(test)}).count == 0,
                "edited bank emits no musical command");
    auto expected = snapshot.controls;
    if (test.pending) {
        const auto desired = test.route == PresetSelection::BankB ? PresetSelection::BankA : PresetSelection::BankB;
        require(model.activate({UiControlKind::PresetKey, test.focus_manual, DrawbarBank::A,
                               static_cast<std::uint8_t>(desired)}).count == 1, "unacknowledged pending route");
        ControlState requested;
        require(requested.restore(expected) && requested.select_preset(test.focus_manual, desired),
                "independent complete desired controls");
        expected = requested.snapshot();
    }
    if (test.workspace == UiWorkspace::Play) {
        const UiControlId focus{UiControlKind::ManualDrawbar, test.focus_manual, edited_bank(test),
                               static_cast<std::uint8_t>(test.focus_index)};
        for (unsigned step = 0; step < 72 && model.view().focus != focus; ++step)
            require(model.key({UiKey::Tab, true}).count == 0 && model.key({UiKey::Tab, false}).count == 0,
                    "normal focus traversal emits no musical command");
        require(model.view().focus == focus, "declared focus identity");
        require(model.layout().control_count == 68 && model.layout().manual_keys.size() * kManualKeyCount +
                model.layout().pedal_keys.size() == 147, "complete control and playing-key inventory");
        const auto presets = std::count_if(model.layout().controls.begin(), model.layout().controls.end(),
            [](const auto& control) { return control.id.kind == UiControlKind::PresetKey; });
        require(presets == 24, "complete preset inventory");
    }
    require(model.view().edited_banks[0] == edited_bank(test) && model.view().edited_banks[1] == edited_bank(test),
            "both edited banks retained");
    require(model.view().controls == expected && session_record(model.view().applied) == session_record(snapshot) &&
            model.view().controls_pending == test.pending, "complete desired/applied snapshots and pending state");
    require(reference_composition_active(model.layout()) == active(test), "independent active/inactive classification");
    return model;
}

bool equal(SDL_Rect a, SDL_Rect b) { return a.x == b.x && a.y == b.y && a.w == b.w && a.h == b.h; }
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
    require(std::isfinite(result.sx) && std::isfinite(result.sy) && result.sx > 0 && result.sy > 0,
            "finite positive renderer scale");
    require(SDL_GetRenderDrawBlendMode(renderer, &result.blend) == 0, "query blend mode");
    require(SDL_RenderSetScale(renderer, 1, 1) == 0, "query physical viewport and clip without logical rounding");
    SDL_RenderGetViewport(renderer, &result.viewport);
    SDL_RenderGetClipRect(renderer, &result.clip);
    require(SDL_RenderSetScale(renderer, result.sx, result.sy) == 0, "restore observed scale");
    require(result.viewport.w > 0 && result.viewport.h > 0 && result.clip.w >= 0 && result.clip.h >= 0,
            "valid finite viewport and nonnegative clip extents");
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
struct SurfaceSpec { int width{}, height{}; SDL_Rect viewport{}; };
SurfaceSpec surface_spec(const Case& c) {
    require(std::isfinite(c.width) && std::isfinite(c.height) && std::isfinite(c.scale) &&
            c.width >= kUiMinimumWidth && c.height >= kUiMinimumHeight && c.width <= 1672 &&
            c.height <= 941 && (c.scale == 1 || c.scale == 1.25F), "bounded finite fixture geometry");
    const int w = static_cast<int>(std::ceil(c.width * c.scale));
    const int h = static_cast<int>(std::ceil(c.height * c.scale));
    const SurfaceSpec spec{w + 2 * std::abs(c.origin_x), h + 2 * std::abs(c.origin_y),
                           {c.origin_x, c.origin_y, w, h}};
    require(spec.width > 0 && spec.width <= maximum_width && spec.height > 0 && spec.height <= maximum_height,
            "bounded output before any surface allocation");
    return spec;
}
struct Frame {
    int width{}, height{};
    Transform coordinates;
    std::vector<Pixel> pixels;
    std::string model, session;
    std::size_t visible_pixels{};
};

class Target {
public:
    explicit Target(const Case& test) :
        spec_(surface_spec(test)),
        surface_(SDL_CreateRGBSurfaceWithFormat(0, spec_.width, spec_.height, 32, SDL_PIXELFORMAT_RGBA32), SDL_FreeSurface),
        renderer_(surface_ ? SDL_CreateSoftwareRenderer(surface_.get()) : nullptr, SDL_DestroyRenderer),
        drawing_(renderer_.get()) {
        require(surface_ && renderer_, "create bounded software target");
        std::string error;
        require(drawing_.initialize(error), "initialize unchanged font/art textures");
        require(SDL_RenderSetScale(renderer_.get(), 1, 1) == 0 &&
                SDL_RenderSetViewport(renderer_.get(), &spec_.viewport) == 0 &&
                SDL_RenderSetClipRect(renderer_.get(), nullptr) == 0, "install physical viewport and disabled clip");
        if (test.clipped && !test.logical_clip)
            require(SDL_RenderSetClipRect(renderer_.get(), &test.clip_request) == 0, "install physical clip");
        require(SDL_RenderSetScale(renderer_.get(), test.scale, test.scale) == 0, "install declared scale");
        if (test.clipped && test.logical_clip)
            require(SDL_RenderSetClipRect(renderer_.get(), &test.clip_request) == 0, "install logical clip");
        require(SDL_SetRenderDrawBlendMode(renderer_.get(), test.blend) == 0, "install incoming blend mode");
        const auto actual = transform(renderer_.get());
        SDL_Rect expected_clip{};
        if (test.clipped) {
            const double scale = test.logical_clip ? test.scale : 1.0;
            expected_clip = {static_cast<int>(std::floor(test.clip_request.x * scale)),
                             static_cast<int>(std::floor(test.clip_request.y * scale)),
                             static_cast<int>(std::floor(test.clip_request.w * scale)),
                             static_cast<int>(std::floor(test.clip_request.h * scale))};
        }
        require(actual.sx == test.scale && actual.sy == test.scale && equal(actual.viewport, spec_.viewport) &&
                actual.clipped == test.clipped && equal(actual.clip, expected_clip) && actual.blend == test.blend,
                "actual queried physical transform matches declared scenario");
        if (test.clipped && (test.clip_request.w == 0 || test.clip_request.h == 0))
            require(actual.clipped && (actual.clip.w == 0 || actual.clip.h == 0), "zero extent stays enabled and empty");
    }

    Frame paint(const UiModel& model) {
        const auto before = transform(renderer_.get());
        const auto copied_model = model_record(model), copied_session = session_record(model.view().applied);
        InstrumentViewInfo info;
        info.audio_running = true; info.sample_rate = 48000; info.buffer_frames = 512;
        info.audio_driver = "fixed-software-fixture"; info.device_name = "fixed copied state";
        info.status_message = "Frozen typography clip qualification";
        paint_instrument(drawing_, model, info);
        require(equal(before, transform(renderer_.get())), "paint preserves logical/physical transforms and blend");
        require(copied_model == model_record(model), "paint preserves every copied view/layout member");
        require(copied_session == session_record(model.view().applied), "paint preserves complete session snapshot");
        require(SDL_RenderFlush(renderer_.get()) == 0 && SDL_LockSurface(surface_.get()) == 0, "read exact RGBA bytes");
        Frame frame{spec_.width, spec_.height, before,
                    std::vector<Pixel>(static_cast<std::size_t>(spec_.width) * static_cast<std::size_t>(spec_.height)),
                    copied_model, copied_session, 0};
        const auto* input = static_cast<const std::uint8_t*>(surface_->pixels);
        for (int y = 0; y < spec_.height; ++y)
            std::memcpy(frame.pixels.data() + static_cast<std::size_t>(y) * static_cast<std::size_t>(spec_.width),
                        input + static_cast<std::size_t>(y) * static_cast<std::size_t>(surface_->pitch),
                        static_cast<std::size_t>(spec_.width) * sizeof(Pixel));
        SDL_UnlockSurface(surface_.get());
        ++totals.paintings;
        return frame;
    }
private:
    SurfaceSpec spec_;
    std::unique_ptr<SDL_Surface, decltype(&SDL_FreeSurface)> surface_;
    std::unique_ptr<SDL_Renderer, decltype(&SDL_DestroyRenderer)> renderer_;
    Drawing drawing_;
};

void check_clip(const Case& test, Frame& frame) {
    // SDL_RenderClear intentionally clears the entire target, independently of
    // the caller clip/viewport. All subsequent paint must respect their exact
    // intersection; a clipped glyph is not compared to an uncut resampling.
    const UiColor color = test.presentation == UiPresentation::Flat ? UiColor{18, 21, 20} : kUiWalnut;
    const Pixel background{color.red, color.green, color.blue, color.alpha};
    bool contained = true;
    for (int y = 0; y < frame.height; ++y)
        for (int x = 0; x < frame.width; ++x) {
            if (visible(frame.coordinates, x, y)) ++frame.visible_pixels;
            else {
                const auto at = static_cast<std::size_t>(y) * static_cast<std::size_t>(frame.width) + static_cast<std::size_t>(x);
                contained = contained && frame.pixels[at] == background;
                ++totals.protected_pixels;
            }
        }
    require(contained, "no paint beyond the exact caller viewport/clip after the whole-target clear");
    if (test.clipped && (test.clip_request.w == 0 || test.clip_request.h == 0 || test.clip_kind == "disjoint")) {
        require(frame.visible_pixels == 0, "enabled empty/disjoint clip leaves only the whole-target clear");
        ++totals.empty_cases;
    } else require(frame.visible_pixels > 0, "nonempty declared caller window survives viewport/output intersection");
    if (test.clipped) ++totals.clipped_cases;
    if (!active(test)) ++totals.inactive_cases;
}
void same_frame(const Frame& a, const Frame& b, std::string_view message) {
    require(a.width == b.width && a.height == b.height && a.pixels == b.pixels && a.model == b.model &&
            a.session == b.session && equal(a.coordinates, b.coordinates), message);
}

void scenario(std::ostream& out, std::size_t index, const Case& c) {
    const auto spec = surface_spec(c);
    out << "\"case\":" << index << ",\"logical_size\":[" << c.width << ',' << c.height
        << "],\"output_size\":[" << spec.width << ',' << spec.height << "],\"scale\":[" << c.scale << ',' << c.scale
        << "],\"origin\":[" << c.origin_x << ',' << c.origin_y << "],\"region\":\"" << c.region
        << "\",\"clip_kind\":\"" << c.clip_kind << "\",\"clip_space\":\"" << (c.logical_clip ? "logical" : "physical")
        << "\",\"clip_request\":";
    rect(out, c.clip_request);
    out << ",\"level\":" << c.level << ",\"route\":\"" << route_name(c.route)
        << "\",\"route_index\":" << static_cast<unsigned>(c.route) << ",\"pending\":" << c.pending
        << ",\"held\":" << c.held << ",\"edited_bank\":\"" << (edited_bank(c) == DrawbarBank::A ? 'A' : 'B')
        << "\",\"focus_manual\":" << static_cast<unsigned>(c.focus_manual) << ",\"focus_index\":" << c.focus_index
        << ",\"blend\":" << static_cast<unsigned>(c.blend) << ",\"clip_enabled\":" << c.clipped
        << ",\"workspace\":" << static_cast<unsigned>(c.workspace)
        << ",\"presentation\":" << static_cast<unsigned>(c.presentation)
        << ",\"active_typography\":" << active(c) << ",\"resource_crop\":false";
}
void stream(std::size_t index, const Case& test, const UiModel& model, const Frame& frame) {
    const auto& t = frame.coordinates;
    std::ostringstream out;
    out << std::boolalpha << std::setprecision(std::numeric_limits<float>::max_digits10)
        << "{\"schema\":1,\"protocol\":\"" << protocol << "\",";
    scenario(out, index, test);
    out << ",\"width\":" << frame.width << ",\"height\":" << frame.height << ",\"viewport\":";
    rect(out, t.viewport);
    out << ",\"clip\":"; rect(out, t.clip);
    out << ",\"logical_viewport\":"; rect(out, t.logical_viewport);
    out << ",\"logical_clip\":"; rect(out, t.logical_clip);
    out << ",\"focus\":"; control_id(out, model.view().focus);
    out << ",\"checks\":{\"transform_unchanged\":true,\"model_unchanged\":true,\"session_unchanged\":true,"
           "\"finite_clip\":true,\"clip_containment\":true,\"deterministic_repaint\":true,\"inactive_classification\":true}"
        << ",\"visible_clip_pixels\":" << frame.visible_pixels << ",\"model\":" << frame.model
        << ",\"bytes\":" << frame.pixels.size() * sizeof(Pixel) << "}\n";
    const auto header = out.str();
    require(header.size() < 512 * 1024, "bounded JSON header");
    std::cout << header;
    std::cout.write(reinterpret_cast<const char*>(frame.pixels.data()),
                    static_cast<std::streamsize>(frame.pixels.size() * sizeof(Pixel)));
    std::cout.flush();
    require(static_cast<bool>(std::cout), "write one JSON header and exact RGBA bytes");
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
            require(static_cast<bool>(std::cout), "write inventory");
            return EXIT_SUCCESS;
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
        require(SDL_Init(0) == 0, "initialize SDL without audio or a window");
        for (std::size_t index = 0; index < fixtures.size(); ++index) {
            if (selected != fixtures.size() && index != selected) continue;
            current_case = index;
            const auto& test = fixtures[index];
            const auto model = state_for(test);
            Target target(test);
            auto frame = target.paint(model);
            check_clip(test, frame);
            same_frame(frame, target.paint(model), "identical deterministic repaint on the same renderer");
            ++totals.repaints;
            if (selected != fixtures.size()) stream(index, test, model, frame);
            else if (index == 46) {
                auto alternate = test;
                alternate.level = 8; alternate.route = PresetSelection::BankB;
                alternate.held = !test.held; alternate.pending = !test.pending;
                alternate.focus_manual = Manual::Lower; alternate.focus_index = 8;
                (void)target.paint(state_for(alternate));
                same_frame(frame, target.paint(model), "exact repaint after different controls, focus and held-note state");
                Target fresh(test);
                same_frame(frame, fresh.paint(model), "exact repaint on a fresh renderer");
                totals.history_repaints += 2;
            }
            ++totals.cases;
        }
        SDL_Quit();
        if (selected == fixtures.size())
            std::cout << "{\"schema\":1,\"protocol\":\"" << protocol << "\",\"status\":\"passed\",\"cases\":" << totals.cases
                << ",\"checks\":" << totals.checks << ",\"paintings\":" << totals.paintings
                << ",\"clipped_cases\":" << totals.clipped_cases << ",\"empty_or_disjoint_cases\":" << totals.empty_cases
                << ",\"inactive_cases\":" << totals.inactive_cases << ",\"protected_pixels\":" << totals.protected_pixels
                << ",\"deterministic_repaints\":" << totals.repaints << ",\"history_repaints\":" << totals.history_repaints
                << ",\"backend\":\"SDL software surface; copied state; no audio/window\"}\n";
        return EXIT_SUCCESS;
    } catch (const std::exception& error) {
        std::cerr << "Typography clip fixture failed in case " << current_case << ": " << error.what() << '\n';
        SDL_Quit();
        return EXIT_FAILURE;
    }
}
