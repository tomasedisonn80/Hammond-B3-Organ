#include "InstrumentView.h"

#include <SDL.h>

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <filesystem>
#include <iomanip>
#include <iostream>
#include <limits>
#include <memory>
#include <span>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

// The ordinary CTest target has no historical-source dependency. For the
// documented one-time before/after qualification, link a second translation
// unit made from the unmodified frozen before source, renaming only its three
// exported functions. Both painters then share these exact dependencies/state.
#ifdef HAMMOND_WAVEFORM_BASELINE
namespace hammond::standalone {
void paint_instrument_before(Drawing&, const UiModel&, const InstrumentViewInfo&);
}
#endif

namespace {
using namespace hammond;
using namespace hammond::standalone;
using Pixel = std::array<std::uint8_t, 4>;
using Painter = void (*)(Drawing&, const UiModel&, const InstrumentViewInfo&);
constexpr Pixel kCyan{165, 228, 223, 255};

struct Counts {
    std::size_t checks{}, failures{}, cases{}, frames{}, compared{}, compared_pixels{};
    std::size_t changed{}, drawbar_changes{}, front_changes{}, escaped{}, flat_pairs{}, hidden_pairs{};
    std::size_t cap_joins{}, shaft_sections{}, front_patches{}, focused_keys{}, clipped_cases{};
} counts;
std::string current_case;
std::filesystem::path captures;
double reference_front{}, reference_top{};
std::array<int, 3> reference_stems{};
#ifdef HAMMOND_WAVEFORM_BASELINE
double baseline_front{}, baseline_top{};
std::array<int, 3> baseline_stems{};
#endif

void require(bool condition, std::string_view detail) {
    if (!condition) throw std::runtime_error(std::string(detail) + ": " + SDL_GetError());
}
void check(bool condition, const std::string& detail) {
    ++counts.checks;
    if (!condition) {
        ++counts.failures;
        std::cerr << "FAIL " << current_case << ": " << detail << '\n';
    }
}
bool same(SDL_Rect a, SDL_Rect b) {
    return a.x == b.x && a.y == b.y && a.w == b.w && a.h == b.h;
}

struct Transform {
    float scale_x{}, scale_y{};
    SDL_Rect viewport{}, clip{}, logical_viewport{}, logical_clip{};
    bool clipped{};
    SDL_BlendMode blend{};
};
Transform transform(SDL_Renderer* renderer) {
    Transform result;
    SDL_RenderGetScale(renderer, &result.scale_x, &result.scale_y);
    SDL_RenderGetViewport(renderer, &result.logical_viewport);
    SDL_RenderGetClipRect(renderer, &result.logical_clip);
    require(SDL_RenderSetScale(renderer, 1, 1) == 0, "read physical coordinates");
    SDL_RenderGetViewport(renderer, &result.viewport);
    SDL_RenderGetClipRect(renderer, &result.clip);
    result.clipped = SDL_RenderIsClipEnabled(renderer) == SDL_TRUE;
    require(SDL_GetRenderDrawBlendMode(renderer, &result.blend) == 0, "read blend mode");
    require(SDL_RenderSetScale(renderer, result.scale_x, result.scale_y) == 0, "restore coordinate scale");
    return result;
}
bool same(const Transform& a, const Transform& b) {
    return a.scale_x == b.scale_x && a.scale_y == b.scale_y &&
        same(a.viewport, b.viewport) && same(a.clip, b.clip) &&
        same(a.logical_viewport, b.logical_viewport) && same(a.logical_clip, b.logical_clip) &&
        a.clipped == b.clipped && a.blend == b.blend;
}
struct Point { long double x{}, y{}; };
Point logical(const Transform& t, int x, int y) {
    return {(x + 0.5L - t.viewport.x) / t.scale_x, (y + 0.5L - t.viewport.y) / t.scale_y};
}
bool visible(const Transform& t, int x, int y) {
    const int local_x = x - t.viewport.x, local_y = y - t.viewport.y;
    return local_x >= 0 && local_x < t.viewport.w && local_y >= 0 && local_y < t.viewport.h &&
        (!t.clipped || (local_x >= t.clip.x && local_x < t.clip.x + t.clip.w &&
                        local_y >= t.clip.y && local_y < t.clip.y + t.clip.h));
}
bool inside(UiRect r, Point p) {
    return r.width > 0 && r.height > 0 && p.x >= r.x && p.y >= r.y &&
        p.x < static_cast<long double>(r.x) + r.width && p.y < static_cast<long double>(r.y) + r.height;
}
long double side(UiPoint a, UiPoint b, Point p) {
    return (static_cast<long double>(b.x) - a.x) * (p.y - a.y) -
           (static_cast<long double>(b.y) - a.y) * (p.x - a.x);
}
bool inside(const UiQuad& q, Point p) {
    // Independent clockwise half-planes: do not use UiQuad::contains(),
    // ui_hit_test(), Drawing's raster spans, or the painter's band helpers.
    return side(q.points[0], q.points[1], p) >= 0 && side(q.points[1], q.points[2], p) > 0 &&
        side(q.points[2], q.points[3], p) > 0 && side(q.points[3], q.points[0], p) >= 0;
}

struct Frame {
    int width{}, height{};
    Transform t{};
    std::vector<Pixel> pixels;
    std::size_t at(int x, int y) const {
        return static_cast<std::size_t>(y) * static_cast<std::size_t>(width) + static_cast<std::size_t>(x);
    }
};
#ifdef HAMMOND_WAVEFORM_BASELINE
std::string fingerprint(const Frame& frame) {
    std::uint64_t hash = 14695981039346656037ULL;
    for (const auto& pixel : frame.pixels)
        for (const auto channel : pixel) hash = (hash ^ channel) * 1099511628211ULL;
    std::ostringstream out;
    out << std::hex << std::setfill('0') << std::setw(16) << hash;
    return out.str();
}
#endif
double brightness(Pixel p) { return .2126 * p[0] + .7152 * p[1] + .0722 * p[2]; }

template <typename Visit>
void visit(const Frame& frame, UiRect bounds, Visit action) {
    const auto& t = frame.t;
    const int left = std::clamp(static_cast<int>(std::floor(bounds.x * t.scale_x + static_cast<float>(t.viewport.x))), 0, frame.width);
    const int right = std::clamp(static_cast<int>(std::ceil((bounds.x + bounds.width) * t.scale_x + static_cast<float>(t.viewport.x))), 0, frame.width);
    const int top = std::clamp(static_cast<int>(std::floor(bounds.y * t.scale_y + static_cast<float>(t.viewport.y))), 0, frame.height);
    const int bottom = std::clamp(static_cast<int>(std::ceil((bounds.y + bounds.height) * t.scale_y + static_cast<float>(t.viewport.y))), 0, frame.height);
    for (int y = top; y < bottom; ++y)
        for (int x = left; x < right; ++x)
            if (visible(t, x, y)) action(x, y, logical(t, x, y));
}
double median(std::vector<double> values) {
    require(!values.empty(), "nonempty numeric sample");
    std::sort(values.begin(), values.end());
    const auto middle = values.size() / 2;
    return values.size() % 2 ? values[middle] : (values[middle - 1] + values[middle]) / 2;
}
double patch(const Frame& frame, UiRect bounds) {
    std::vector<double> values;
    visit(frame, bounds, [&](int x, int y, Point p) {
        if (inside(bounds, p)) values.push_back(brightness(frame.pixels[frame.at(x, y)]));
    });
    return median(std::move(values));
}

class Target {
public:
    Target(int width, int height) :
        surface_(SDL_CreateRGBSurfaceWithFormat(0, width, height, 32, SDL_PIXELFORMAT_RGBA32), SDL_FreeSurface),
        renderer_(surface_ ? SDL_CreateSoftwareRenderer(surface_.get()) : nullptr, SDL_DestroyRenderer),
        drawing_(renderer_.get()) {
        require(width <= 3400 && height <= 1900 && surface_ && renderer_, "bounded software target");
        std::string error;
        require(drawing_.initialize(error), "initialize native fonts/art: " + error);
    }
    void configure(float scale, SDL_Rect viewport, const SDL_Rect* clip, bool logical_clip) {
        require(SDL_RenderSetScale(renderer_.get(), 1, 1) == 0, "configure physical units");
        require(SDL_RenderSetViewport(renderer_.get(), &viewport) == 0, "configure viewport");
        require(SDL_RenderSetClipRect(renderer_.get(), logical_clip ? nullptr : clip) == 0, "configure physical clip");
        require(SDL_RenderSetScale(renderer_.get(), scale, scale) == 0, "configure scale");
        if (logical_clip) require(SDL_RenderSetClipRect(renderer_.get(), clip) == 0, "configure logical clip");
    }
    Frame paint(const UiModel& model, Painter painter, const std::string& capture = {}) {
        const auto before = transform(renderer_.get());
        InstrumentViewInfo info;
        info.audio_running = true;
        info.sample_rate = 48000;
        info.buffer_frames = 512;
        info.audio_driver = "dummy";
        info.device_name = "Fixed acceptance state";
        info.status_message = "Fixed material acceptance state";
        painter(drawing_, model, info);
        check(same(before, transform(renderer_.get())), "paint preserves physical/logical scale, viewport, clip and blend");
        require(SDL_RenderFlush(renderer_.get()) == 0, "flush paint");
        if (!capture.empty() && !captures.empty())
            require(SDL_SaveBMP(surface_.get(), (captures / (capture + ".bmp")).string().c_str()) == 0, "capture fixed-state frame");
        require(SDL_LockSurface(surface_.get()) == 0, "lock raster");
        Frame frame{surface_->w, surface_->h, before, std::vector<Pixel>(
            static_cast<std::size_t>(surface_->w) * static_cast<std::size_t>(surface_->h))};
        const auto* bytes = static_cast<const std::uint8_t*>(surface_->pixels);
        for (int y = 0; y < frame.height; ++y)
            for (int x = 0; x < frame.width; ++x) {
                const auto* p = bytes + static_cast<std::size_t>(y) * static_cast<std::size_t>(surface_->pitch) +
                                static_cast<std::size_t>(x) * 4;
                frame.pixels[frame.at(x, y)] = {p[0], p[1], p[2], p[3]};
            }
        SDL_UnlockSurface(surface_.get());
        ++counts.frames;
        return frame;
    }
private:
    std::unique_ptr<SDL_Surface, decltype(&SDL_FreeSurface)> surface_;
    std::unique_ptr<SDL_Renderer, decltype(&SDL_DestroyRenderer)> renderer_;
    Drawing drawing_;
};

std::span<const UiKeyGeometry> keys(const UiLayout& layout, std::size_t division) {
    return division < 2 ? std::span<const UiKeyGeometry>(layout.manual_keys[division]) :
                          std::span<const UiKeyGeometry>(layout.pedal_keys);
}
#ifdef HAMMOND_WAVEFORM_BASELINE
bool held(const UiModel& model, std::size_t division, std::size_t index) {
    return division < 2 ? model.view().applied.held_keys[division][index] : model.view().applied.held_pedals[index];
}
#endif
struct Case {
    int width{}, height{}, value{};
    float scale{1};
    UiPresentation presentation{UiPresentation::Dimensional};
    UiWorkspace workspace{UiWorkspace::Play};
    int focus{}; // 0..3 cap families; 4/5 held natural/accidental; 6/7 idle pedal front.
    bool clipped{}, logical_clip{}, audition{};
};
UiModel model_for(const Case& test) {
    UiModel model;
    require(model.resize(static_cast<float>(test.width), static_cast<float>(test.height)) &&
        model.set_presentation(test.presentation), "admit fixed logical geometry");
    SessionSnapshot snapshot;
    snapshot.controls = model.view().controls;
    snapshot.publication_revision = 2;
    snapshot.prepared = snapshot.running = true;
    snapshot.sample_rate = 48000;
    snapshot.frame_clock = 10240;
    for (auto& manual : snapshot.controls.drawbars)
        for (auto& bank : manual) bank.fill(static_cast<std::uint8_t>(test.value));
    snapshot.controls.pedal_drawbars.fill(static_cast<std::uint8_t>(test.value));
    snapshot.held_keys[0][24] = true;
    if (test.audition) {
        for (auto& manual : snapshot.controls.drawbars)
            for (auto& bank : manual) bank.fill(0);
        snapshot.controls.drawbars[0][1] = {8, 8, 8, 0, 0, 0, 0, 0, 0};
        snapshot.controls.drawbars[1][1] = {0, 0, 8, 0, 0, 0, 0, 0, 0};
        snapshot.controls.pedal_drawbars = {8, 0};
    } else {
        snapshot.held_keys[0][1] = snapshot.held_keys[1][24] = snapshot.held_keys[1][1] = true;
        snapshot.held_pedals[12] = snapshot.held_pedals[13] = true;
    }
    model.observe(snapshot);
    if (!test.audition && test.workspace == UiWorkspace::Play) {
        UiControlId id{UiControlKind::ManualDrawbar, Manual::Upper, DrawbarBank::B,
            static_cast<std::uint8_t>(test.focus == 0 ? 0 : test.focus == 1 ? 2 : 4)};
        if (test.focus == 3) id = {UiControlKind::PedalDrawbar};
        if (test.focus == 4 || test.focus == 5) id = {UiControlKind::ManualKey, Manual::Upper,
            DrawbarBank::A, static_cast<std::uint8_t>(test.focus == 4 ? 24 : 1)};
        if (test.focus == 6 || test.focus == 7) id = {UiControlKind::PedalKey, Manual::Upper,
            DrawbarBank::A, static_cast<std::uint8_t>(test.focus == 6 ? 0 : 1)};
        require(model.activate(id).count == 0 && model.view().focus == id, "focus without musical command");
    }
    require(model.set_workspace(test.workspace), "set workspace without musical change");
    return model;
}

struct DrawbarRegion { UiRect slot{}, cap{}; Pixel join{}; bool mixture{}; };
DrawbarRegion drawbar_region(const UiModel& model, const UiControlGeometry& geometry) {
    // The product legibility contract changes only wide Dimensional manual
    // caps to 32/8. Retain the 26/7 compact and 22/6 pedal allocations.
    // No private production geometry helper is called.
    const bool mixture = geometry.id.kind == UiControlKind::PedalDrawbar;
    const bool wide = model.layout().sidebar_pedals &&
        model.view().presentation == UiPresentation::Dimensional;
    const float height = mixture ? 22.0F : wide ? 32.0F : 26.0F;
    const float width = std::clamp(geometry.bounds.width - 8.0F, 10.0F, 34.0F);
    const float slot_width = std::min(geometry.bounds.width - 2.0F, width + 8.0F);
    const float center = geometry.track.x + geometry.track.width / 2;
    const auto value = mixture ? model.view().controls.pedal_drawbars[geometry.id.index] :
        model.view().controls.drawbars[static_cast<std::size_t>(geometry.id.manual)]
                                     [static_cast<std::size_t>(geometry.id.bank)][geometry.id.index];
    const float position = geometry.track.y + geometry.track.height * static_cast<float>(value) / 8;
    const auto index = geometry.id.index;
    const bool brown = mixture || index < 2;
    const bool black = !mixture && (index == 4 || index == 6 || index == 7);
    return {{center - slot_width / 2, geometry.track.y - height / 2, slot_width, geometry.track.height + height},
        {center - width / 2, position - height / 2, width, height},
        brown ? Pixel{163, 111, 77, 255} : black ? Pixel{70, 69, 66, 255} : Pixel{244, 224, 186, 255}, mixture};
}

void targets(const UiModel& model, const Frame& frame) {
    for (const auto& geometry : std::span(model.layout().controls).first(model.layout().control_count)) {
        if (geometry.id.kind != UiControlKind::ManualDrawbar && geometry.id.kind != UiControlKind::PedalDrawbar) continue;
        const auto region = drawbar_region(model, geometry);
        const auto& t = frame.t;
        const float center = region.cap.x + region.cap.width / 2;
        const int x = static_cast<int>(center * t.scale_x + static_cast<float>(t.viewport.x));
        const bool wide = model.layout().sidebar_pedals &&
            model.view().presentation == UiPresentation::Dimensional;
        const float front = region.mixture ? 6.0F : wide ? 8.0F : 7.0F;
        const float join_y = region.cap.y + region.cap.height - 1 - front;
        std::vector<double> join_rows;
        visit(frame, {center - 1, region.cap.y + 3, 2, region.cap.height - 3}, [&](int px, int py, Point p) {
            if (px == x && frame.pixels[frame.at(px, py)] == region.join) join_rows.push_back(static_cast<double>(p.y));
        });
        check(!join_rows.empty() && std::abs(median(join_rows) - join_y) <= 1,
              "observed cap join is within one logical pixel of the 8-unit wide, 7-unit compact or 6-unit pedal front");
        ++counts.cap_joins;
        const float exposed = region.cap.y - geometry.track.y;
        if (exposed < 4) continue; // Value 0 has no exposed extension by definition.
        for (const float fraction : {.30F, .65F}) {
            const int y = static_cast<int>((geometry.track.y + exposed * fraction) * t.scale_y + static_cast<float>(t.viewport.y));
            int body = 0, edge = 0, bright = 0;
            const int left = static_cast<int>((center - 7) * t.scale_x + static_cast<float>(t.viewport.x));
            const int right = static_cast<int>((center + 7) * t.scale_x + static_cast<float>(t.viewport.x));
            for (int px = left; px < right; ++px) {
                const double level = brightness(frame.pixels[frame.at(px, y)]);
                if (level > 25) ++bright;
                if (level > 85) ++edge;
                if (level > 25 && level <= 85) ++body;
            }
            check(bright >= static_cast<int>(7 * t.scale_x) && bright <= static_cast<int>(10 * t.scale_x) + 1 &&
                  edge >= 1 && edge <= static_cast<int>(2 * t.scale_x) + 1 && body >= static_cast<int>(4 * t.scale_x),
                  "exposed shaft has a 7-10-unit dark body with a narrow brighter edge");
            ++counts.shaft_sections;
        }
    }
    // Sample six idle end-key fronts, including the minimum-size short pedals.
    // A wide center band avoids side outlines; it is derived from public quads.
    for (std::size_t division = 0; division < 3; ++division)
        for (const auto index : {std::size_t{0}, keys(model.layout(), division).size() - 1}) {
            const auto& q = keys(model.layout(), division)[index].front;
            const auto bounds = keys(model.layout(), division)[index].bounds;
            std::vector<double> levels;
            visit(frame, bounds, [&](int x, int y, Point p) {
                if (!inside(q, p)) return;
                const long double fraction = (p.y - q.points[0].y) / (q.points[3].y - q.points[0].y);
                const long double left = q.points[0].x + fraction * (q.points[3].x - q.points[0].x);
                const long double right = q.points[1].x + fraction * (q.points[2].x - q.points[1].x);
                if (fraction >= .30L && fraction < .85L && p.x >= left + .30L * (right - left) &&
                    p.x < left + .70L * (right - left)) levels.push_back(brightness(frame.pixels[frame.at(x, y)]));
            });
            check(!levels.empty() && median(levels) >= 110 && median(levels) <= 170,
                  "idle natural front has the accepted darker middle band");
            ++counts.front_patches;
        }
}

std::array<int, 3> stem_anchor(const Frame& frame) {
    std::array<int, 3> result{};
    const std::array<int, 3> rows{350, 365, 380};
    for (std::size_t row = 0; row < rows.size(); ++row)
        for (int x = 103; x < 119; ++x)
            if (brightness(frame.pixels[frame.at(x, rows[row])]) > 25) ++result[row];
    return result;
}

#ifdef HAMMOND_WAVEFORM_BASELINE
void compare(const UiModel& model, const Frame& before, const Frame& after) {
    require(before.width == after.width && before.height == after.height && same(before.t, after.t), "matched comparison coordinates");
    const bool flat = model.view().presentation == UiPresentation::Flat;
    const bool hidden = model.view().workspace != UiWorkspace::Play;
    std::vector<std::uint16_t> permitted(after.pixels.size(), 0);
    std::array<std::size_t, kKeyCount + 21> changed_by_region{};
    std::size_t populated_fronts = 0;
    if (!flat && !hidden) {
        std::uint16_t drawbar = 0;
        for (const auto& geometry : std::span(model.layout().controls).first(model.layout().control_count)) {
            if (geometry.id.kind != UiControlKind::ManualDrawbar && geometry.id.kind != UiControlKind::PedalDrawbar) continue;
            ++drawbar;
            const auto region = drawbar_region(model, geometry);
            visit(after, region.slot, [&](int x, int y, Point p) {
                if (inside(region.slot, p) || inside(region.cap, p)) permitted[after.at(x, y)] = drawbar;
            });
        }
        std::vector<std::uint16_t> owners(after.pixels.size(), 0);
        // Occlusion is resolved from public hit quads, natural then accidental.
        // An accidental's pixels cannot be excused by an underlying natural.
        for (const bool accidental : {false, true})
            for (std::size_t division = 0; division < 3; ++division)
                for (std::size_t index = 0; index < keys(model.layout(), division).size(); ++index) {
                    const auto& key = keys(model.layout(), division)[index];
                    if (key.accidental != accidental) continue;
                    const auto owner = static_cast<std::uint16_t>(21 + division * kManualKeyCount + index);
                    visit(after, key.bounds, [&](int x, int y, Point p) {
                        if (inside(key.hit, p)) owners[after.at(x, y)] = owner;
                    });
                }
        for (std::size_t division = 0; division < 3; ++division)
            for (std::size_t index = 0; index < keys(model.layout(), division).size(); ++index) {
                const auto& key = keys(model.layout(), division)[index];
                if (key.accidental || held(model, division, index)) continue;
                const auto owner = static_cast<std::uint16_t>(21 + division * kManualKeyCount + index);
                std::size_t area = 0;
                visit(after, key.bounds, [&](int x, int y, Point p) {
                    if (owners[after.at(x, y)] == owner && inside(key.front, p)) {
                        permitted[after.at(x, y)] = owner;
                        ++area;
                    }
                });
                if (area > 0) ++populated_fronts;
            }
    }
    std::size_t changed = 0, escaped = 0, drawbars = 0, fronts = 0;
    std::string first_escape;
    for (int y = 0; y < after.height; ++y)
        for (int x = 0; x < after.width; ++x) {
            const auto at = after.at(x, y);
            if (before.pixels[at] == after.pixels[at]) continue;
            ++changed;
            const auto region = permitted[at];
            if (!visible(after.t, x, y) || region == 0) {
                ++escaped;
                if (first_escape.empty()) first_escape = " first=" + std::to_string(x) + "," + std::to_string(y);
            } else {
                ++changed_by_region[region];
                if (region <= 20) ++drawbars; else ++fronts;
            }
        }
    check(escaped == 0, "all before/after deltas stay in original slot/cap or visible idle-front half-planes; escaped=" +
          std::to_string(escaped) + first_escape);
    if (flat || hidden) check(changed == 0, "Flat/hidden Play pixels remain byte-identical");
    else {
        check(changed > 0, "dimensional material comparison is nonvacuous");
        if (!after.t.clipped) {
            const auto changed_fronts = std::count_if(changed_by_region.begin() + 21, changed_by_region.end(),
                [](std::size_t value) { return value > 0; });
            check(static_cast<std::size_t>(changed_fronts) == populated_fronts &&
                  std::all_of(changed_by_region.begin() + 1, changed_by_region.begin() + 21,
                              [](std::size_t value) { return value > 0; }),
                  "all 20 drawbars and every visible idle natural front participate");
        }
    }
    ++counts.compared;
    counts.compared_pixels += after.pixels.size();
    counts.changed += changed;
    counts.escaped += escaped;
    counts.drawbar_changes += drawbars;
    counts.front_changes += fronts;
    if (flat) ++counts.flat_pairs;
    if (hidden) ++counts.hidden_pairs;
    std::cout << "{\"case\":\"" << current_case << "\",\"before_fnv1a64\":\"" << fingerprint(before)
        << "\",\"after_fnv1a64\":\"" << fingerprint(after) << "\",\"pixels\":" << after.pixels.size()
        << ",\"changed\":" << changed << ",\"drawbar_changes\":" << drawbars << ",\"front_changes\":" << fronts
        << ",\"escaped\":" << escaped << "}\n";
}
#endif

void run(const Case& test) {
    std::ostringstream name;
    name << (test.audition ? "audition" : "matrix") << '-' << test.width << 'x' << test.height << "-s" << test.scale
         << "-v" << test.value << "-p" << static_cast<int>(test.presentation) << "-w" << static_cast<int>(test.workspace)
         << "-f" << test.focus << "-c" << test.clipped << "-l" << test.logical_clip;
    current_case = name.str();
    const auto model = model_for(test);
    const int width = static_cast<int>(static_cast<float>(test.width) * test.scale);
    const int height = static_cast<int>(static_cast<float>(test.height) * test.scale);
    const int offset = test.clipped ? 11 : 0;
    Target target(width + offset * 2, height + offset * 2);
    SDL_Rect clip{};
    if (test.clipped) {
        const auto& key = test.focus < 6 ? model.layout().manual_keys[0][test.focus == 4 ? 24 : 1] :
            model.layout().pedal_keys[test.focus == 6 ? 0 : 1];
        const float center = (key.front.points[0].x + key.front.points[1].x) / 2;
        const float top = key.front.points[0].y - 8;
        const float units = test.logical_clip ? 1 : test.scale;
        clip = {static_cast<int>(center * units), static_cast<int>(top * units),
                static_cast<int>((static_cast<float>(test.width) - center - 3) * units),
                static_cast<int>((static_cast<float>(test.height) - top - 5) * units)};
    }
    target.configure(test.scale, {offset, offset, width, height}, test.clipped ? &clip : nullptr, test.logical_clip);
#ifdef HAMMOND_WAVEFORM_BASELINE
    const auto before = target.paint(model, paint_instrument_before, test.audition ? current_case + "-before" : "");
#endif
    const auto after = target.paint(model, paint_instrument, test.audition ? current_case + "-after" : "");
    if (test.presentation == UiPresentation::Dimensional && test.workspace == UiWorkspace::Play && !test.clipped)
        targets(model, after);
    if (test.clipped) {
        std::size_t outside_ink = 0, focus_ink = 0;
        const Pixel clear = test.presentation == UiPresentation::Flat ? Pixel{18, 21, 20, 255} : Pixel{85, 54, 36, 255};
        const auto& key = test.focus < 6 ? model.layout().manual_keys[0][test.focus == 4 ? 24 : 1] :
            model.layout().pedal_keys[test.focus == 6 ? 0 : 1];
        for (int y = 0; y < after.height; ++y)
            for (int x = 0; x < after.width; ++x) {
                const auto pixel = after.pixels[after.at(x, y)];
                if (!visible(after.t, x, y) && pixel != clear) ++outside_ink;
                if (pixel == kCyan && inside(key.hit, logical(after.t, x, y))) ++focus_ink;
            }
        check(outside_ink == 0 && focus_ink > 0, "clipped/offset focus survives without ink outside the caller's clip");
        ++counts.clipped_cases;
        ++counts.focused_keys;
    }
    if (test.audition && test.width == 1672) {
        reference_front = patch(after, {708, 677, 7, 5});
        reference_top = patch(after, {708, 653, 7, 5});
        reference_stems = stem_anchor(after);
        check(reference_front >= 125 && reference_front <= 140, "reference isolated idle-front median is 125-140 encoded-RGB levels");
        check(std::all_of(reference_stems.begin(), reference_stems.end(), [](int width_) { return width_ >= 7 && width_ <= 10; }),
              "reference stem has 7-10 bright pixels at all three fixed rows");
#ifdef HAMMOND_WAVEFORM_BASELINE
        baseline_front = patch(before, {708, 677, 7, 5});
        baseline_top = patch(before, {708, 653, 7, 5});
        baseline_stems = stem_anchor(before);
        check(baseline_front - reference_front >= 19 && baseline_top == reference_top,
              "isolated front darkens at least 19 levels and adjacent top pixels retain their median");
        check(std::all_of(baseline_stems.begin(), baseline_stems.end(), [](int width_) { return width_ == 3; }),
              "frozen before renderer reproduces the three-pixel stem anchor");
#endif
    }
#ifdef HAMMOND_WAVEFORM_BASELINE
    compare(model, before, after);
#endif
    ++counts.cases;
}
} // namespace

int main(int argc, char** argv) {
    SDL_SetMainReady();
    try {
        require(argc == 1 || (argc == 3 && std::string_view(argv[1]) == "--capture-dir"), "usage: test [--capture-dir existing-directory]");
        if (argc == 3) { captures = argv[2]; require(std::filesystem::is_directory(captures), "existing capture directory"); }
        require(SDL_Init(0) == 0, "initialize SDL without audio/window subsystems");
        const std::array<float, 4> scales{1, 1.25F, 1.5F, 2};
        for (const auto size : {std::array<int, 2>{1672, 941}, std::array<int, 2>{1280, 900}, std::array<int, 2>{960, 700}}) {
            for (std::size_t scale = 0; scale < scales.size(); ++scale)
                for (const int value : {0, 4, 8})
                    run({size[0], size[1], value, scales[scale], UiPresentation::Dimensional, UiWorkspace::Play, static_cast<int>(scale)});
            run({size[0], size[1], 8, 1, UiPresentation::Dimensional, UiWorkspace::Play, 0, false, false, true});
#ifdef HAMMOND_WAVEFORM_BASELINE
            for (const auto workspace : {UiWorkspace::Rotary, UiWorkspace::Service})
                for (const auto presentation : {UiPresentation::Dimensional, UiPresentation::Flat})
                    run({size[0], size[1], 4, 1, presentation, workspace});
#endif
        }
        for (std::size_t scale = 0; scale < scales.size(); ++scale) {
            for (const int focus : {4, 5, 6, 7})
                run({960, 700, 4, scales[scale], UiPresentation::Dimensional, UiWorkspace::Play,
                    focus, true, scale % 2 != 0});
#ifdef HAMMOND_WAVEFORM_BASELINE
            for (const int value : {0, 4, 8})
                run({960, 700, value, scales[scale], UiPresentation::Flat, UiWorkspace::Play, static_cast<int>(scale)});
#endif
        }
        SDL_Quit();
    } catch (const std::exception& error) {
        std::cerr << "Waveform material setup failed: " << error.what() << '\n';
        SDL_Quit();
        return EXIT_FAILURE;
    }
    std::cout << std::fixed << std::setprecision(4)
        << "{\"summary\":true,\"checks\":" << counts.checks << ",\"failures\":" << counts.failures
        << ",\"cases\":" << counts.cases << ",\"frames\":" << counts.frames << ",\"compared_pairs\":" << counts.compared
        << ",\"compared_pixels\":" << counts.compared_pixels << ",\"changed_pixels\":" << counts.changed
        << ",\"drawbar_changes\":" << counts.drawbar_changes << ",\"idle_front_changes\":" << counts.front_changes
        << ",\"escaped_pixels\":" << counts.escaped << ",\"flat_pairs\":" << counts.flat_pairs << ",\"hidden_pairs\":" << counts.hidden_pairs
        << ",\"cap_joins\":" << counts.cap_joins << ",\"shaft_sections\":" << counts.shaft_sections
        << ",\"front_patches\":" << counts.front_patches << ",\"focused_clips\":" << counts.focused_keys
        << ",\"reference_front_median\":" << reference_front << ",\"reference_top_median\":" << reference_top
        << ",\"reference_stem_widths\":[" << reference_stems[0] << ',' << reference_stems[1] << ',' << reference_stems[2]
        << ']';
#ifdef HAMMOND_WAVEFORM_BASELINE
    std::cout << ",\"baseline_comparison\":true,\"before_front_median\":" << baseline_front
        << ",\"before_top_median\":" << baseline_top << ",\"before_stem_widths\":["
        << baseline_stems[0] << ',' << baseline_stems[1] << ',' << baseline_stems[2] << ']';
#else
    std::cout << ",\"baseline_comparison\":false";
#endif
    std::cout << ",\"backend\":\"SDL software surface; fixed copied state; no audio/window\"}\n";
    return counts.failures == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
