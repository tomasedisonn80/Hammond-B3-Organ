#include "InstrumentView.h"

#include <SDL.h>

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <memory>
#include <span>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

// Ordinary CTest needs only current source. The one-time qualification links
// the source-identified af006b0 painter with its three public names renamed.
// No historical renderer is shipped or included in the ordinary target.
#ifdef HAMMOND_PRODUCT_BASELINE
namespace hammond::standalone {
void paint_instrument_product_before(Drawing&, const UiModel&, const InstrumentViewInfo&);
}
#endif

namespace {
using namespace hammond;
using namespace hammond::standalone;
using Pixel = std::array<std::uint8_t, 4>;
using Painter = void (*)(Drawing&, const UiModel&, const InstrumentViewInfo&);
constexpr Pixel cyan{165, 228, 223, 255};
constexpr Pixel amber{235, 169, 73, 255};
constexpr std::array<std::string_view, 9> footage{
    "16'", "5 1/3'", "8'", "4'", "2 2/3'", "2'", "1 3/5'", "1 1/3'", "1'"};
constexpr std::array<std::string_view, 12> sounding{
    "CANCELLED", "SOUNDING FIXED C#", "SOUNDING FIXED D", "SOUNDING FIXED D#",
    "SOUNDING FIXED E", "SOUNDING FIXED F", "SOUNDING FIXED F#", "SOUNDING FIXED G",
    "SOUNDING FIXED G#", "SOUNDING FIXED A", "SOUNDING A#", "SOUNDING B"};

struct Totals {
    std::size_t checks{}, failures{}, cases{}, frames{}, caps{}, glyphs{}, text_pixels{};
    std::size_t compared{}, pixels{}, changed{}, racks{}, tops{}, escaped{}, unchanged{};
    std::size_t clips{}, pending{}, focused{}, idle_keys{}, readout_leaks{};
} totals;
std::string case_name;

void require(bool condition, const std::string& message) {
    if (!condition) throw std::runtime_error(message + ": " + SDL_GetError());
}
void check(bool condition, const std::string& message) {
    ++totals.checks;
    if (!condition) {
        ++totals.failures;
        if (totals.failures <= 30) std::cerr << "FAIL " << case_name << ": " << message << '\n';
    }
}
double light(Pixel pixel) { return .2126 * pixel[0] + .7152 * pixel[1] + .0722 * pixel[2]; }

struct Point { long double x{}, y{}; };
bool inside(UiRect r, Point p) {
    return r.width > 0 && r.height > 0 && p.x >= r.x && p.y >= r.y &&
        p.x < static_cast<long double>(r.x) + r.width && p.y < static_cast<long double>(r.y) + r.height;
}
[[maybe_unused]] long double side(UiPoint a, UiPoint b, Point p) {
    return (static_cast<long double>(b.x) - a.x) * (p.y - a.y) -
        (static_cast<long double>(b.y) - a.y) * (p.x - a.x);
}
[[maybe_unused]] bool inside(const UiQuad& q, Point p) {
    // Physical pixel centers and clockwise half-planes, independently of
    // UiQuad::contains, hit testing, quad raster spans or painter helpers.
    return side(q.points[0], q.points[1], p) >= 0 && side(q.points[1], q.points[2], p) > 0 &&
        side(q.points[2], q.points[3], p) > 0 && side(q.points[3], q.points[0], p) >= 0;
}
bool equal(SDL_Rect a, SDL_Rect b) {
    return a.x == b.x && a.y == b.y && a.w == b.w && a.h == b.h;
}
struct Transform {
    float sx{}, sy{};
    SDL_Rect viewport{}, clip{}, logical_viewport{}, logical_clip{};
    bool clipped{};
    SDL_BlendMode blend{};
};
Transform observe_transform(SDL_Renderer* renderer) {
    Transform t;
    SDL_RenderGetScale(renderer, &t.sx, &t.sy);
    SDL_RenderGetViewport(renderer, &t.logical_viewport);
    SDL_RenderGetClipRect(renderer, &t.logical_clip);
    require(SDL_RenderSetScale(renderer, 1, 1) == 0, "observe physical transform");
    SDL_RenderGetViewport(renderer, &t.viewport);
    SDL_RenderGetClipRect(renderer, &t.clip);
    t.clipped = SDL_RenderIsClipEnabled(renderer) == SDL_TRUE;
    require(SDL_GetRenderDrawBlendMode(renderer, &t.blend) == 0, "observe blend mode");
    require(SDL_RenderSetScale(renderer, t.sx, t.sy) == 0, "restore transform");
    return t;
}
bool equal(const Transform& a, const Transform& b) {
    return a.sx == b.sx && a.sy == b.sy && equal(a.viewport, b.viewport) && equal(a.clip, b.clip) &&
        equal(a.logical_viewport, b.logical_viewport) && equal(a.logical_clip, b.logical_clip) &&
        a.clipped == b.clipped && a.blend == b.blend;
}
Point logical(const Transform& t, int x, int y) {
    return {(x + .5L - t.viewport.x) / t.sx, (y + .5L - t.viewport.y) / t.sy};
}
bool visible(const Transform& t, int x, int y) {
    const int xx = x - t.viewport.x, yy = y - t.viewport.y;
    return xx >= 0 && yy >= 0 && xx < t.viewport.w && yy < t.viewport.h &&
        (!t.clipped || (xx >= t.clip.x && yy >= t.clip.y && xx < t.clip.x + t.clip.w && yy < t.clip.y + t.clip.h));
}
struct Frame {
    int width{}, height{};
    Transform transform{};
    std::vector<Pixel> pixels;
    std::size_t at(int x, int y) const {
        return static_cast<std::size_t>(y) * static_cast<std::size_t>(width) + static_cast<std::size_t>(x);
    }
};
template <typename Action>
void visit(const Frame& frame, UiRect bounds, Action action) {
    const auto& t = frame.transform;
    const int left = std::clamp(static_cast<int>(std::floor(bounds.x * t.sx + static_cast<float>(t.viewport.x))), 0, frame.width);
    const int top = std::clamp(static_cast<int>(std::floor(bounds.y * t.sy + static_cast<float>(t.viewport.y))), 0, frame.height);
    const int right = std::clamp(static_cast<int>(std::ceil((bounds.x + bounds.width) * t.sx + static_cast<float>(t.viewport.x))), 0, frame.width);
    const int bottom = std::clamp(static_cast<int>(std::ceil((bounds.y + bounds.height) * t.sy + static_cast<float>(t.viewport.y))), 0, frame.height);
    for (int y = top; y < bottom; ++y)
        for (int x = left; x < right; ++x)
            if (visible(t, x, y)) action(x, y, logical(t, x, y));
}

struct Text {
    std::string value;
    UiRect box{};
    float size{}, padding{};
    TextFace face{TextFace::Sans};
    bool fit{true};
};
struct Glyph {
    UiRect advance{}, permitted{};
    char character{};
};
class Target {
public:
    Target(int width, int height) :
        surface_(SDL_CreateRGBSurfaceWithFormat(0, width, height, 32, SDL_PIXELFORMAT_RGBA32), SDL_FreeSurface),
        renderer_(surface_ ? SDL_CreateSoftwareRenderer(surface_.get()) : nullptr, SDL_DestroyRenderer),
        drawing_(renderer_.get()) {
        require(width <= 4300 && height <= 2400 && surface_ && renderer_, "bounded software target");
        std::string error;
        require(drawing_.initialize(error), "initialize fonts and art " + error);
    }
    void configure(float scale, SDL_Rect viewport, const SDL_Rect* clip, bool logical_clip) {
        require(SDL_RenderSetScale(renderer_.get(), 1, 1) == 0, "physical coordinates");
        require(SDL_RenderSetViewport(renderer_.get(), &viewport) == 0, "viewport");
        require(SDL_RenderSetClipRect(renderer_.get(), logical_clip ? nullptr : clip) == 0, "physical clip");
        require(SDL_RenderSetScale(renderer_.get(), scale, scale) == 0, "output scale");
        if (logical_clip) require(SDL_RenderSetClipRect(renderer_.get(), clip) == 0, "logical clip");
    }
    Frame paint(const UiModel& model, Painter painter) {
        const auto before = observe_transform(renderer_.get());
        InstrumentViewInfo info;
        info.audio_running = true;
        info.sample_rate = 48000;
        info.buffer_frames = 512;
        info.audio_driver = "dummy";
        info.status_message = "Fixed product acceptance state";
        info.device_name = "Fixed software target";
        painter(drawing_, model, info);
        check(equal(before, observe_transform(renderer_.get())), "paint preserves caller transform and blend");
        return read(before);
    }
    Frame text(const std::vector<Text>& plans, std::vector<Glyph>& glyphs) {
        const auto transform = observe_transform(renderer_.get());
        drawing_.clear({0, 0, 0, 0});
        for (const auto& plan : plans) {
            float size = plan.fit ? std::min(plan.size, plan.box.height / 1.2F) : plan.size;
            const float advance = drawing_.text_width(plan.value, size, plan.face);
            const float available = plan.box.width - 2 * plan.padding;
            if (plan.fit && advance > available) size *= available / advance;
            const float left = plan.box.x + (plan.box.width - drawing_.text_width(plan.value, size, plan.face)) / 2;
            const float line_height = plan.fit ? 1.2F * size : 16.8F;
            const float top = plan.box.y + (plan.box.height - line_height) / 2;
            drawing_.text(plan.value, left, top, size, {255, 255, 255}, plan.face);
            float x = left;
            for (const auto character : plan.value) {
                const float width = drawing_.text_width(std::string_view(&character, 1), size, plan.face);
                if (character != ' ') glyphs.push_back({{x, plan.box.y, width, plan.box.height},
                    {plan.box.x + plan.padding, plan.box.y, plan.box.width - 2 * plan.padding, plan.box.height}, character});
                x += width;
            }
        }
        return read(transform);
    }
private:
    Frame read(const Transform& transform) {
        require(SDL_RenderFlush(renderer_.get()) == 0 && SDL_LockSurface(surface_.get()) == 0, "read software pixels");
        Frame frame{surface_->w, surface_->h, transform, std::vector<Pixel>(
            static_cast<std::size_t>(surface_->w) * static_cast<std::size_t>(surface_->h))};
        const auto* bytes = static_cast<const std::uint8_t*>(surface_->pixels);
        for (int y = 0; y < frame.height; ++y)
            for (int x = 0; x < frame.width; ++x) {
                const auto* p = bytes + static_cast<std::size_t>(y) * static_cast<std::size_t>(surface_->pitch) + static_cast<std::size_t>(x) * 4;
                frame.pixels[frame.at(x, y)] = {p[0], p[1], p[2], p[3]};
            }
        SDL_UnlockSurface(surface_.get());
        ++totals.frames;
        return frame;
    }
    std::unique_ptr<SDL_Surface, decltype(&SDL_FreeSurface)> surface_;
    std::unique_ptr<SDL_Renderer, decltype(&SDL_DestroyRenderer)> renderer_;
    Drawing drawing_;
};

struct Case {
    float width{1672}, height{941}, scale{1};
    int value{}, variant{};
    UiPresentation presentation{UiPresentation::Dimensional};
    UiWorkspace workspace{UiWorkspace::Play};
    bool clipped{}, logical_clip{};
};
struct FixedState {
    UiModel model;
    std::array<int, 2> presets{};
};
FixedState state_for(const Case& test) {
    FixedState result;
    auto& model = result.model;
    require(model.resize(test.width, test.height) && model.set_presentation(test.presentation), "fixed admitted layout");
    SessionSnapshot snapshot;
    snapshot.controls = model.view().controls;
    for (auto& manual : snapshot.controls.drawbars)
        for (auto& bank : manual) bank.fill(static_cast<std::uint8_t>(test.value));
    snapshot.controls.pedal_drawbars = {4, 7};
    constexpr std::array<int, 5> presets{0, 1, 9, 10, 11};
    for (std::size_t manual = 0; manual < 2; ++manual) {
        result.presets[manual] = presets[(static_cast<std::size_t>(test.variant) + manual) % presets.size()];
        ControlState controls;
        require(controls.restore(snapshot.controls) && controls.select_preset(static_cast<Manual>(manual),
            static_cast<PresetSelection>(result.presets[manual])), "fixed copied route");
        snapshot.controls = controls.snapshot();
        snapshot.held_keys[manual][24] = snapshot.held_keys[manual][1] = true;
    }
    snapshot.held_pedals[12] = snapshot.held_pedals[13] = true;
    snapshot.publication_revision = 3;
    snapshot.prepared = snapshot.running = true;
    snapshot.sample_rate = 48000;
    snapshot.frame_clock = 16384;
    model.observe(snapshot);
    for (std::size_t manual = 0; manual < 2; ++manual)
        require(model.activate({UiControlKind::EditBank, static_cast<Manual>(manual),
            static_cast<DrawbarBank>((static_cast<std::size_t>(test.variant) + manual) % 2)}).count == 0, "edit bank is presentation only");
    if (test.variant % 2 != 0 && test.workspace == UiWorkspace::Play) {
        const int desired = (result.presets[0] + 5) % 12;
        require(model.activate({UiControlKind::PresetKey, Manual::Upper, DrawbarBank::A,
            static_cast<std::uint8_t>(desired)}).count == 1 && model.view().controls_pending, "pending desired route differs from applied route");
    }
    if (test.workspace == UiWorkspace::Play) {
        const int focus = test.variant % 7;
        UiControlId id{UiControlKind::ManualDrawbar, Manual::Upper, model.view().edited_banks[0],
            static_cast<std::uint8_t>(focus < 3 ? focus * 2 : 0)};
        if (focus >= 3) id = {UiControlKind::ManualKey, Manual::Upper, DrawbarBank::A,
            static_cast<std::uint8_t>(focus == 3 ? 0 : focus == 4 ? 60 : focus == 5 ? 24 : 1)};
        require(model.activate(id).count == 0, "focus without performance command");
    }
    require(model.set_workspace(test.workspace), "workspace retains controls");
    return result;
}
std::vector<Text> plans_for(const FixedState& state, int value, bool legacy_digits = false) {
    std::vector<Text> plans;
    for (const auto& control : std::span(state.model.layout().controls).first(state.model.layout().control_count)) {
        if (control.id.kind != UiControlKind::ManualDrawbar) continue;
        if (!legacy_digits) plans.push_back({std::string(footage[control.id.index]),
            {control.label_bounds.x, control.label_bounds.y, control.label_bounds.width, 20}, 17, 2, TextFace::Serif});
        plans.push_back({std::to_string(value), control.value_bounds, legacy_digits ? 13.0F : 14.0F,
            0, TextFace::Sans, legacy_digits});
    }
    if (!legacy_digits) for (std::size_t manual = 0; manual < 2; ++manual) {
        const auto panel = state.model.layout().registration_panels[manual];
        const float width = panel.width * .43F;
        const float x = panel.x + panel.width - width - 14;
        plans.push_back({state.model.view().edited_banks[manual] == DrawbarBank::A ? "EDIT BANK A" : "EDIT BANK B",
            {x, panel.y + 2, width, 14}, 11.5F, 3, TextFace::Sans});
        plans.push_back({std::string(sounding[static_cast<std::size_t>(state.presets[manual])]),
            {x, panel.y + 16, width, 14}, 11.5F, 3, TextFace::Sans});
    }
    return plans;
}
void text_acceptance(const Frame& actual, const Frame& expected, const std::vector<Glyph>& glyphs) {
    for (const auto& glyph : glyphs) {
        std::size_t samples = 0, matches = 0, escaped = 0;
        visit(expected, glyph.advance, [&](int x, int y, Point p) {
            const auto at = expected.at(x, y);
            if (light(expected.pixels[at]) < 160) return;
            ++samples;
            if (!inside(glyph.permitted, p)) ++escaped;
            // Background is dark charcoal. Strong white-template ink must
            // coincide with readable actual ink, including each slash/prime.
            if (light(actual.pixels[at]) >= 90) ++matches;
        });
        check(samples > 0 && matches == samples && escaped == 0,
            "complete literal glyph '" + std::string(1, glyph.character) + "' remains readable in its own row; samples=" +
            std::to_string(samples) + " missing=" + std::to_string(samples - matches));
        ++totals.glyphs;
        totals.text_pixels += samples;
    }
}
double middle(std::vector<double> values) {
    require(!values.empty(), "nonempty measured line");
    std::sort(values.begin(), values.end());
    return values[values.size() / 2];
}
void caps(const UiModel& model, const Frame& frame, int value) {
    for (const auto& control : std::span(model.layout().controls).first(model.layout().control_count)) {
        if (control.id.kind != UiControlKind::ManualDrawbar) continue;
        const float x = control.track.x + control.track.width / 2;
        const float center = control.track.y + control.track.height * static_cast<float>(value) / 8;
        const int column = static_cast<int>(x * frame.transform.sx + static_cast<float>(frame.transform.viewport.x));
        const bool brown = control.id.index < 2;
        const bool black = control.id.index == 4 || control.id.index == 6 || control.id.index == 7;
        const Pixel top = brown ? Pixel{194, 142, 108, 255} : black ? Pixel{101, 100, 97, 255} : Pixel{255, 248, 224, 255};
        const Pixel join = brown ? Pixel{163, 111, 77, 255} : black ? Pixel{70, 69, 66, 255} : Pixel{244, 224, 186, 255};
        std::vector<double> tops, joins;
        visit(frame, {x - 1, center - 16, 2, 32}, [&](int px, int py, Point p) {
            if (px != column) return;
            const auto pixel = frame.pixels[frame.at(px, py)];
            if (pixel == top) tops.push_back(static_cast<double>(p.y));
            if (pixel == join) joins.push_back(static_cast<double>(p.y));
        });
        check(!tops.empty() && !joins.empty(), "cap top and front join are observable for every family/position");
        if (!tops.empty() && !joins.empty()) {
            check(std::abs(middle(tops) - (center - 14)) <= 1 && std::abs(middle(joins) - (center + 7)) <= 1,
                "32-pixel cap has the separately measured 8-pixel front at the exact unchanged track center");
        }
        check(center - 16 >= control.label_bounds.y + 21 && center + 16 <= control.value_bounds.y - 1,
            "endpoint cap stays between legend and readout with the declared material margin");
        ++totals.caps;
    }
}

#ifdef HAMMOND_PRODUCT_BASELINE
bool permitted_top(const UiKeyGeometry& key, Point p) {
    if (!inside(key.top, p)) return false;
    const auto& q = key.top.points;
    const long double depth = static_cast<long double>(q[3].y) - q[0].y;
    const long double fraction = (p.y - q[0].y) / depth;
    const long double left_slope = (static_cast<long double>(q[3].x) - q[0].x) / depth;
    const long double right_slope = (static_cast<long double>(q[2].x) - q[1].x) / depth;
    const long double left = q[0].x + left_slope * (p.y - q[0].y);
    const long double right = q[1].x + right_slope * (p.y - q[0].y);
    const long double dl = (p.x - left) / std::sqrt(1 + left_slope * left_slope);
    const long double dr = (right - p.x) / std::sqrt(1 + right_slope * right_slope);
    // The epsilon admits only float construction roundoff, far below a pixel.
    constexpr long double eps = .00005L;
    const bool edge = fraction >= .08L - eps && fraction < .88L + eps &&
        ((dl >= 1 - eps && dl < 2 + eps) || (dr >= 1 - eps && dr < 2 + eps));
    const bool rear = fraction >= 0 && fraction < std::min(.12L, 18 / depth) + eps &&
        p.x >= left + .8L - eps && p.x < right - .8L + eps;
    return rear || edge;
}
void compare(const FixedState& state, const Frame& before, const Frame& after,
             const Frame* expected, const Frame* legacy) {
    const auto& model = state.model;
    const auto& layout = model.layout();
    const bool active = layout.sidebar_pedals && layout.presentation == UiPresentation::Dimensional &&
        layout.workspace == UiWorkspace::Play;
    require(before.pixels.size() == after.pixels.size() && equal(before.transform, after.transform), "same before/after coordinates");
    std::vector<std::uint8_t> allowed(after.pixels.size());
    std::vector<std::uint16_t> owners(after.pixels.size());
    std::array<std::size_t, 122> changes{};
    if (active) {
        for (const auto& panel : layout.registration_panels)
            visit(after, {panel.x + 1, panel.y + 1, panel.width - 2, 30}, [&](int x, int y, Point p) {
                if (inside(UiRect{panel.x + 1, panel.y + 1, panel.width - 2, 30}, p)) allowed[after.at(x, y)] = 1;
            });
        for (const auto& control : std::span(layout.controls).first(layout.control_count))
            if (control.id.kind == UiControlKind::ManualDrawbar)
                visit(after, control.bounds, [&](int x, int y, Point p) {
                    if (inside(control.bounds, p)) allowed[after.at(x, y)] = 1;
                });
        for (const bool accidental : {false, true})
            for (std::size_t manual = 0; manual < 2; ++manual)
                for (std::size_t index = 0; index < 61; ++index) {
                    const auto& key = layout.manual_keys[manual][index];
                    if (key.accidental != accidental) continue;
                    visit(after, key.bounds, [&](int x, int y, Point p) {
                        if (inside(key.hit, p)) owners[after.at(x, y)] = static_cast<std::uint16_t>(1 + manual * 61 + index);
                    });
                }
        for (std::size_t manual = 0; manual < 2; ++manual)
            for (std::size_t index = 0; index < 61; ++index) {
                const auto& key = layout.manual_keys[manual][index];
                if (key.accidental || model.view().applied.held_keys[manual][index]) continue;
                const auto owner = 1 + manual * 61 + index;
                visit(after, key.bounds, [&](int x, int y, Point p) {
                    if (owners[after.at(x, y)] == owner && permitted_top(key, p)) allowed[after.at(x, y)] = 2;
                });
            }
    }
    std::size_t changed = 0, escaped = 0, rack_changes = 0, top_changes = 0;
    std::string first;
    for (int y = 0; y < after.height; ++y)
        for (int x = 0; x < after.width; ++x) {
            const auto at = after.at(x, y);
            if (before.pixels[at] == after.pixels[at]) continue;
            ++changed;
            if (!visible(after.transform, x, y) || allowed[at] == 0) {
                ++escaped;
                if (first.empty()) first = " first=" + std::to_string(x) + "," + std::to_string(y);
            } else if (allowed[at] == 1) ++rack_changes;
            else { ++top_changes; ++changes[static_cast<std::size_t>(owners[at] - 1U)]; }
        }
    check(escaped == 0, "deltas stay in manual racks and independently bounded idle-top bands; escaped=" + std::to_string(escaped) + first);
    if (!active) {
        check(changed == 0, "compact, Flat and hidden workspaces stay byte-identical");
        ++totals.unchanged;
    } else if (!after.transform.clipped) {
        check(rack_changes > 0 && top_changes > 0, "active before/after comparison is nonvacuous");
        for (std::size_t manual = 0; manual < 2; ++manual)
            for (std::size_t index = 0; index < 61; ++index)
                if (!layout.manual_keys[manual][index].accidental && !model.view().applied.held_keys[manual][index]) {
                    check(changes[manual * 61 + index] > 0, "every visible idle natural has a local lighting change");
                    ++totals.idle_keys;
                }
        require(expected && legacy, "readout template witnesses");
        for (const auto& control : std::span(layout.controls).first(layout.control_count))
            if (control.id.kind == UiControlKind::ManualDrawbar) {
                std::size_t leaks = 0;
                visit(after, control.value_bounds, [&](int x, int y, Point p) {
                    const auto at = after.at(x, y);
                    // Alpha=1 glyph edges can blend black RGB to zero while
                    // changing a charcoal destination by one integer level.
                    // Retain their exact coverage instead of adding tolerance
                    // for material differences outside the two digit shapes.
                    if (inside(control.value_bounds, p) && before.pixels[at] != after.pixels[at] &&
                        expected->pixels[at][3] == 0 && legacy->pixels[at][3] == 0) ++leaks;
                });
                check(leaks == 0, "readout differences are only old/new digit ink, never cap shadow");
                totals.readout_leaks += leaks;
            }
    }
    ++totals.compared;
    totals.pixels += after.pixels.size();
    totals.changed += changed;
    totals.escaped += escaped;
    totals.racks += rack_changes;
    totals.tops += top_changes;
}
#endif

void run(const Case& test) {
    std::ostringstream name;
    name << test.width << 'x' << test.height << "-s" << test.scale << "-v" << test.value << "-r" << test.variant
         << "-p" << static_cast<int>(test.presentation) << "-w" << static_cast<int>(test.workspace) << "-clip" << test.clipped;
    case_name = name.str();
    const auto state = state_for(test);
    const auto& model = state.model;
    const auto& layout = model.layout();
    check(layout.control_count == 68 && std::count_if(layout.controls.begin(), layout.controls.end(),
        [](const UiControlGeometry& c) { return c.id.kind == UiControlKind::PresetKey; }) == 24 &&
        layout.manual_keys[0].size() + layout.manual_keys[1].size() + layout.pedal_keys.size() == 147,
        "live control, preset and playing-key inventory retained");
    const int width = static_cast<int>(std::ceil(test.width * test.scale));
    const int height = static_cast<int>(std::ceil(test.height * test.scale));
    const int offset = test.clipped ? 11 : 0;
    Target target(width + 2 * offset, height + 2 * offset);
    SDL_Rect clip{};
    if (test.clipped) {
        const auto& key = layout.manual_keys[0][0];
        const float units = test.logical_clip ? 1 : test.scale;
        const float x = key.top.points[0].x + 1, y = key.top.points[0].y + 3;
        clip = {static_cast<int>(x * units), static_cast<int>(y * units),
            static_cast<int>((test.width - x - 5) * units), static_cast<int>((test.height - y - 7) * units)};
    }
    target.configure(test.scale, {offset, offset, width, height}, test.clipped ? &clip : nullptr, test.logical_clip);
#ifdef HAMMOND_PRODUCT_BASELINE
    const auto before = target.paint(model, paint_instrument_product_before);
#endif
    const auto after = target.paint(model, paint_instrument);
    const bool active = layout.sidebar_pedals && test.presentation == UiPresentation::Dimensional && test.workspace == UiWorkspace::Play;
    Frame expected, legacy;
    if (active && !test.clipped) {
        caps(model, after, test.value);
        std::vector<Glyph> glyphs;
        expected = target.text(plans_for(state, test.value), glyphs);
        text_acceptance(after, expected, glyphs);
#ifdef HAMMOND_PRODUCT_BASELINE
        glyphs.clear();
        legacy = target.text(plans_for(state, test.value, true), glyphs);
#endif
    }
    if (test.clipped) {
        const Pixel clear = test.presentation == UiPresentation::Flat ? Pixel{18, 21, 20, 255} : Pixel{85, 54, 36, 255};
        std::size_t outside = 0;
        for (int y = 0; y < after.height; ++y)
            for (int x = 0; x < after.width; ++x)
                if (!visible(after.transform, x, y) && after.pixels[after.at(x, y)] != clear) ++outside;
        check(outside == 0, "offset/clip excludes every painter pixel outside caller visibility");
        ++totals.clips;
    }
    if (test.workspace == UiWorkspace::Play) {
        const auto focus_pixels = std::count(after.pixels.begin(), after.pixels.end(), cyan);
        check(focus_pixels > 0, "live cyan focus survives refined material and clips");
        ++totals.focused;
        if (model.view().controls_pending && !test.clipped) {
            check(std::count(after.pixels.begin(), after.pixels.end(), amber) > 0, "pending route retains independent amber feedback");
            ++totals.pending;
        }
    }
#ifdef HAMMOND_PRODUCT_BASELINE
    compare(state, before, after, &expected, &legacy);
#endif
    ++totals.cases;
}

void focus_inventory() {
    UiModel model;
    require(model.resize(1672, 941), "focus inventory layout");
    const auto tab = [&]() {
        require(model.key({UiKey::Tab, true}).count == 0, "focus does not issue sound changes");
        require(model.key({UiKey::Tab, false}).count == 0, "release navigation key");
    };
    tab();
    const auto first = model.view().focus;
    std::vector<UiControlId> sequence{first};
    for (std::size_t index = 0; index < 100; ++index) {
        tab();
        if (model.view().focus == first) break;
        check(std::find(sequence.begin(), sequence.end(), model.view().focus) == sequence.end(), "distinct focus stop");
        sequence.push_back(model.view().focus);
    }
    check(sequence.size() == 71 && model.view().focus == first, "Play has exactly 71 cyclic focus stops");
    for (const auto workspace : {UiWorkspace::Rotary, UiWorkspace::Service}) {
        require(model.set_workspace(workspace), "common focus workspace");
        tab();
        const auto start = model.view().focus;
        std::size_t count = 1;
        for (; count <= 20; ++count) {
            tab();
            if (model.view().focus == start) break;
        }
        check(count == 10, "hidden workspace has exactly ten common focus stops");
    }
}
} // namespace

int main() {
    SDL_SetMainReady();
    try {
        require(SDL_Init(0) == 0, "initialize SDL without window or audio subsystems");
        focus_inventory();
        constexpr std::array<float, 4> scales{1, 1.25F, 1.5F, 2};
        for (std::size_t scale = 0; scale < scales.size(); ++scale)
            for (int value = 0; value <= 8; ++value)
                run({1672, 941, scales[scale], value, value + static_cast<int>(scale)});
        for (const auto size : {std::array<float, 2>{1400, 820}, std::array<float, 2>{1920, 1080}})
            for (std::size_t scale = 0; scale < scales.size(); ++scale)
                for (const int value : {0, 4, 8}) run({size[0], size[1], scales[scale], value, value + static_cast<int>(scale)});
        for (const auto size : {std::array<float, 2>{1400.25F, 820.75F}, std::array<float, 2>{1672.5F, 941.25F},
                               std::array<float, 2>{1920.75F, 1080.5F}})
            for (const float scale : {1.25F, 1.5F})
                for (const int value : {0, 8}) run({size[0], size[1], scale, value, value + 1});
        for (std::size_t scale = 0; scale < scales.size(); ++scale)
            run({1672, 941, scales[scale], 4, 3 + static_cast<int>(scale), UiPresentation::Dimensional,
                UiWorkspace::Play, true, scale % 2 != 0});
#ifdef HAMMOND_PRODUCT_BASELINE
        for (const auto size : {std::array<float, 2>{960, 700}, std::array<float, 2>{1280, 900},
                               std::array<float, 2>{1399, 820}, std::array<float, 2>{1400, 819}})
            for (const float scale : {1.0F, 1.5F}) run({size[0], size[1], scale, 4, 1});
        for (const auto size : {std::array<float, 2>{960, 700}, std::array<float, 2>{1280, 900},
                               std::array<float, 2>{1399, 820}, std::array<float, 2>{1400, 819},
                               std::array<float, 2>{1400, 820}, std::array<float, 2>{1672, 941}, std::array<float, 2>{1920, 1080}})
            for (const float scale : {1.0F, 2.0F}) run({size[0], size[1], scale, 8, 2, UiPresentation::Flat});
        for (const auto workspace : {UiWorkspace::Rotary, UiWorkspace::Service})
            for (const auto presentation : {UiPresentation::Dimensional, UiPresentation::Flat})
                for (const auto size : {std::array<float, 2>{960, 700}, std::array<float, 2>{1672, 941}, std::array<float, 2>{1920, 1080}})
                    run({size[0], size[1], 1, 4, 0, presentation, workspace});
#endif
        SDL_Quit();
    } catch (const std::exception& error) {
        std::cerr << "Product visual setup failed: " << error.what() << '\n';
        SDL_Quit();
        return EXIT_FAILURE;
    }
    std::cout << "{\"schema_version\":1,\"checks\":" << totals.checks << ",\"failures\":" << totals.failures
        << ",\"cases\":" << totals.cases << ",\"frames\":" << totals.frames << ",\"cap_measurements\":" << totals.caps
        << ",\"literal_glyphs\":" << totals.glyphs << ",\"strong_text_pixels\":" << totals.text_pixels
        << ",\"compared_pairs\":" << totals.compared << ",\"compared_pixels\":" << totals.pixels
        << ",\"changed_pixels\":" << totals.changed << ",\"rack_changes\":" << totals.racks
        << ",\"idle_top_changes\":" << totals.tops << ",\"escaped_pixels\":" << totals.escaped
        << ",\"byte_identical_pairs\":" << totals.unchanged << ",\"clipped_cases\":" << totals.clips
        << ",\"pending_cases\":" << totals.pending << ",\"focused_cases\":" << totals.focused
        << ",\"changed_idle_keys\":" << totals.idle_keys << ",\"readout_shadow_leaks\":" << totals.readout_leaks
        << ",\"backend\":\"SDL software surface; fixed copied state; no audio/window\"}\n";
    return totals.failures == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
