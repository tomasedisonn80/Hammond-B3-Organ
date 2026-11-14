// A41 manual independent acceptance. Not a product or CTest target.
// Link frozen 2e161dc and final painters, renaming the three old public symbols.
#include "InstrumentView.h"
#include "InspectionModel.h"

#include <SDL.h>
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <filesystem>
#include <iomanip>
#include <iostream>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace hammond::standalone {
void paint_instrument_before(Drawing&, const UiModel&, const InstrumentViewInfo&);
}

namespace {
using namespace hammond;
using namespace hammond::standalone;
using Pixel = std::array<std::uint8_t, 4>;
using Frame = std::vector<Pixel>;
constexpr std::array<UiControlId, 10> common{{
    {UiControlKind::Workspace, Manual::Upper, DrawbarBank::A, 0},
    {UiControlKind::Workspace, Manual::Upper, DrawbarBank::A, 1},
    {UiControlKind::Workspace, Manual::Upper, DrawbarBank::A, 2},
    {UiControlKind::SaveControls}, {UiControlKind::LoadControls}, {UiControlKind::Help},
    {UiControlKind::AudioSettings}, {UiControlKind::MidiSettings}, {UiControlKind::Panic},
    {UiControlKind::Presentation}}};
std::size_t failures{}, full_pairs{}, focus_pairs{}, clip_pairs{}, checks{};
std::uint64_t compared_pixels{};

void require(bool value, const std::string& message) {
    if (!value) throw std::runtime_error(message + ": " + SDL_GetError());
}
void check(bool value, const std::string& message) {
    ++checks;
    if (!value) { ++failures; std::cerr << "FAIL " << message << '\n'; }
}
std::string hash(const Frame& frame) {
    std::uint64_t value = 14695981039346656037ULL;
    for (const auto& pixel : frame)
        for (const auto channel : pixel) value = (value ^ channel) * 1099511628211ULL;
    std::ostringstream result;
    result << std::hex << std::setfill('0') << std::setw(16) << value;
    return result.str();
}
bool equal(SDL_Rect a, SDL_Rect b) {
    return a.x == b.x && a.y == b.y && a.w == b.w && a.h == b.h;
}
struct State {
    float scale_x{}, scale_y{};
    SDL_Rect viewport{}, clip{}, logical_viewport{}, logical_clip{};
    SDL_BlendMode blend{};
    bool clipped{};
};
State state(SDL_Renderer* renderer) {
    State s;
    SDL_RenderGetScale(renderer, &s.scale_x, &s.scale_y);
    SDL_RenderGetViewport(renderer, &s.logical_viewport);
    SDL_RenderGetClipRect(renderer, &s.logical_clip);
    require(SDL_RenderSetScale(renderer, 1.0F, 1.0F) == 0, "physical state read");
    SDL_RenderGetViewport(renderer, &s.viewport);
    SDL_RenderGetClipRect(renderer, &s.clip);
    s.clipped = SDL_RenderIsClipEnabled(renderer) == SDL_TRUE;
    require(SDL_GetRenderDrawBlendMode(renderer, &s.blend) == 0, "read blend");
    require(SDL_RenderSetScale(renderer, s.scale_x, s.scale_y) == 0, "restore scale");
    return s;
}
bool equal(const State& a, const State& b) {
    return a.scale_x == b.scale_x && a.scale_y == b.scale_y &&
        equal(a.viewport, b.viewport) && equal(a.clip, b.clip) &&
        equal(a.logical_viewport, b.logical_viewport) && equal(a.logical_clip, b.logical_clip) &&
        a.blend == b.blend && a.clipped == b.clipped;
}
bool visible(const State& state, int x, int y) {
    const int px = x - state.viewport.x, py = y - state.viewport.y;
    return px >= 0 && py >= 0 && px < state.viewport.w && py < state.viewport.h &&
        (!state.clipped || (px >= state.clip.x && py >= state.clip.y &&
         px < state.clip.x + state.clip.w && py < state.clip.y + state.clip.h));
}
bool inside(UiRect r, long double x, long double y, float halo = 0.0F) {
    return x >= r.x - halo && y >= r.y - halo &&
        x < static_cast<long double>(r.x) + r.width + halo &&
        y < static_cast<long double>(r.y) + r.height + halo;
}
class Target {
public:
    Target(int width, int height)
        : surface(SDL_CreateRGBSurfaceWithFormat(0, width, height, 32, SDL_PIXELFORMAT_RGBA32), SDL_FreeSurface),
          renderer(surface ? SDL_CreateSoftwareRenderer(surface.get()) : nullptr, SDL_DestroyRenderer),
          drawing(renderer.get()) {
        require(surface && renderer, "create software surface");
        require(width <= 3840 && height <= 2160, "bounded raster size");
        std::string error;
        require(drawing.initialize(error), "initialize Drawing " + error);
    }
    void configure(float scale, SDL_Rect viewport, const SDL_Rect* clip = nullptr) {
        require(SDL_RenderSetScale(renderer.get(), 1.0F, 1.0F) == 0, "configure physical scale");
        require(SDL_RenderSetViewport(renderer.get(), &viewport) == 0, "configure physical viewport");
        require(SDL_RenderSetClipRect(renderer.get(), clip) == 0, "configure physical clip");
        require(SDL_RenderSetScale(renderer.get(), scale, scale) == 0, "configure output scale");
    }
    Frame paint(const UiModel& model, bool before) {
        InstrumentViewInfo info;
        const auto inspection = make_inspection_document(RuntimeProfile{}, model.view(), {});
        info.inspection = &inspection;
        info.status_message = "A41 fixed copied state; no live audio or MIDI";
        info.midi_status = "No MIDI port opened";
        const State initial = state(renderer.get());
        if (before) paint_instrument_before(drawing, model, info);
        else paint_instrument(drawing, model, info);
        check(equal(initial, state(renderer.get())), "paint preserves caller renderer state");
        require(SDL_RenderFlush(renderer.get()) == 0, "flush software paint");
        SDL_RenderPresent(renderer.get());
        require(SDL_LockSurface(surface.get()) == 0, "lock surface");
        Frame result(static_cast<std::size_t>(width()) * static_cast<std::size_t>(height()));
        const auto* bytes = static_cast<const std::uint8_t*>(surface->pixels);
        for (int y = 0; y < height(); ++y)
            for (int x = 0; x < width(); ++x) {
                const auto at = static_cast<std::size_t>(y) * static_cast<std::size_t>(surface->pitch) +
                    static_cast<std::size_t>(x) * 4;
                result[index(x, y)] = {bytes[at], bytes[at + 1], bytes[at + 2], bytes[at + 3]};
            }
        SDL_UnlockSurface(surface.get());
        return result;
    }
    void save(const std::filesystem::path& path) {
        require(SDL_SaveBMP(surface.get(), path.string().c_str()) == 0, "save actual software paint");
    }
    int width() const { return surface->w; }
    int height() const { return surface->h; }
    std::size_t index(int x, int y) const {
        return static_cast<std::size_t>(y) * static_cast<std::size_t>(width()) + static_cast<std::size_t>(x);
    }
    std::unique_ptr<SDL_Surface, decltype(&SDL_FreeSurface)> surface;
    std::unique_ptr<SDL_Renderer, decltype(&SDL_DestroyRenderer)> renderer;
    Drawing drawing;
};
UiModel model_at(float width, float height, UiWorkspace workspace, UiPresentation presentation) {
    UiModel model;
    require(model.resize(width, height) && model.set_workspace(workspace) &&
        model.set_presentation(presentation), "prepare model");
    SessionSnapshot snapshot;
    snapshot.publication_revision = 2;
    snapshot.frame_clock = 123456;
    snapshot.held_keys[0][24] = true; snapshot.held_keys[0][25] = true;
    snapshot.held_keys[1][36] = true; snapshot.held_keys[1][37] = true;
    snapshot.held_pedals[0] = true; snapshot.held_pedals[1] = true;
    model.observe(snapshot);
    if (workspace == UiWorkspace::Play)
        (void)model.activate({UiControlKind::ManualKey, Manual::Upper, DrawbarBank::A, 24});
    return model;
}
void focus(UiModel& model, UiControlId id) {
    for (unsigned attempt = 0; attempt < 72 && model.view().focus != id; ++attempt) {
        require(model.key({UiKey::Tab, true}).count == 0 &&
            model.key({UiKey::Tab, false}).count == 0, "focus navigation emits no command");
    }
    require(model.view().focus == id, "reached requested common focus");
}
struct Delta {
    std::size_t changed{}, outside_header{}, common_halo{}, leaked_before{}, leaked_after{}, visible_after{};
    std::array<int, 4> bounds{1000000, 1000000, -1, -1};
};
Delta compare(const Target& target, const Frame& before, const Frame& after, const UiModel& model) {
    const auto transform = state(target.renderer.get());
    const auto& layout = model.layout();
    const Pixel clear = layout.presentation == UiPresentation::Flat ? Pixel{18, 21, 20, 255} :
        Pixel{kUiWalnut.red, kUiWalnut.green, kUiWalnut.blue, kUiWalnut.alpha};
    Delta delta;
    for (int y = 0; y < target.height(); ++y)
        for (int x = 0; x < target.width(); ++x) {
            const auto index = target.index(x, y);
            const auto lx = (static_cast<long double>(x) + 0.5L - transform.viewport.x) / transform.scale_x;
            const auto ly = (static_cast<long double>(y) + 0.5L - transform.viewport.y) / transform.scale_y;
            const bool shown = visible(transform, x, y);
            if (!shown) {
                delta.leaked_before += before[index] != clear ? 1U : 0U;
                delta.leaked_after += after[index] != clear ? 1U : 0U;
            } else delta.visible_after += after[index] != clear ? 1U : 0U;
            if (before[index] == after[index]) continue;
            ++delta.changed;
            delta.bounds[0] = std::min(delta.bounds[0], x); delta.bounds[1] = std::min(delta.bounds[1], y);
            delta.bounds[2] = std::max(delta.bounds[2], x + 1); delta.bounds[3] = std::max(delta.bounds[3], y + 1);
            if (!inside(layout.header, lx, ly)) ++delta.outside_header;
            for (const auto& control : layout.controls) {
                if (std::find(common.begin(), common.end(), control.id) == common.end()) continue;
                if (inside(control.bounds, lx, ly, 2.0F)) { ++delta.common_halo; break; }
            }
        }
    compared_pixels += before.size();
    const bool enabled = layout.sidebar_pedals && layout.presentation == UiPresentation::Dimensional;
    check(enabled || delta.changed == 0, "complete Flat/non-sidebar pixel identity");
    check(delta.outside_header == 0, "all changed pixels inside header");
    check(delta.common_halo == 0, "common controls and two-pixel focus halo unchanged");
    check(delta.leaked_before == 0 && delta.leaked_after == 0, "no nonclear ink outside viewport/clip");
    return delta;
}
void row(const char* kind, const Target& target, const UiModel& model, float scale,
         const Frame& before, const Frame& after, const Delta& delta, int focus_index = -1) {
    const auto& layout = model.layout();
    std::cout << std::fixed << std::setprecision(2)
        << "{\"kind\":\"" << kind << "\",\"logical\":[" << layout.width << ',' << layout.height
        << "],\"physical\":[" << target.width() << ',' << target.height() << "],\"scale\":" << scale
        << ",\"workspace\":" << static_cast<unsigned>(layout.workspace)
        << ",\"presentation\":" << static_cast<unsigned>(layout.presentation)
        << ",\"sidebar\":" << (layout.sidebar_pedals ? "true" : "false")
        << ",\"focus_index\":" << focus_index
        << ",\"before_fnv1a64\":\"" << hash(before) << "\",\"after_fnv1a64\":\"" << hash(after)
        << "\",\"changed_pixels\":" << delta.changed << ",\"outside_header\":" << delta.outside_header
        << ",\"control_halo_changes\":" << delta.common_halo
        << ",\"clip_leaks_before\":" << delta.leaked_before << ",\"clip_leaks_after\":" << delta.leaked_after
        << ",\"visible_nonclear_after\":" << delta.visible_after << ",\"changed_bbox\":";
    if (delta.changed == 0) std::cout << "null";
    else std::cout << '[' << delta.bounds[0] << ',' << delta.bounds[1] << ',' << delta.bounds[2] << ',' << delta.bounds[3] << ']';
    std::cout << "}\n";
}
void full(float width, float height, float scale, const std::filesystem::path& output) {
    const int pw = static_cast<int>(std::ceil(width * scale)), ph = static_cast<int>(std::ceil(height * scale));
    Target target(pw, ph);
    target.configure(scale, {0, 0, pw, ph});
    for (const auto presentation : {UiPresentation::Dimensional, UiPresentation::Flat})
        for (const auto workspace : {UiWorkspace::Play, UiWorkspace::Rotary, UiWorkspace::Service}) {
            const auto model = model_at(width, height, workspace, presentation);
            const bool save = scale == 1.0F && workspace == UiWorkspace::Play &&
                presentation == UiPresentation::Dimensional && (width == 1400.0F || width == 1672.0F) &&
                (height == 820.0F || height == 941.0F);
            const std::string stem = width == 1672.0F ? "A41-reference-" : "A41-minimum-sidebar-";
            const auto before = target.paint(model, true);
            if (save) target.save(output / (stem + "before.bmp"));
            const auto after = target.paint(model, false);
            if (save) target.save(output / (stem + "after.bmp"));
            const auto delta = compare(target, before, after, model);
            if (model.layout().sidebar_pedals && presentation == UiPresentation::Dimensional)
                check(delta.changed > 0, "enabled header visibly changes");
            row("full", target, model, scale, before, after, delta);
            ++full_pairs;
        }
}
void focus_strips() {
    for (const float width : {1400.0F, 1672.0F})
        for (const float scale : {1.0F, 1.25F}) {
            const float height = width == 1400.0F ? 820.0F : 941.0F;
            const int pw = static_cast<int>(std::ceil(width * scale));
            Target target(pw, static_cast<int>(std::ceil(125.0F * scale)));
            target.configure(scale, {0, 0, pw, static_cast<int>(std::ceil(height * scale))});
            for (const auto workspace : {UiWorkspace::Play, UiWorkspace::Rotary, UiWorkspace::Service}) {
                auto model = model_at(width, height, workspace, UiPresentation::Dimensional);
                for (std::size_t index = 0; index < common.size(); ++index) {
                    focus(model, common[index]);
                    const auto before = target.paint(model, true), after = target.paint(model, false);
                    const auto delta = compare(target, before, after, model);
                    std::size_t cyan = 0;
                    const auto it = std::find_if(model.layout().controls.begin(), model.layout().controls.end(),
                        [&](const auto& control) { return control.id == common[index]; });
                    require(it != model.layout().controls.end(), "focused control exists");
                    for (int y = 0; y < target.height(); ++y)
                        for (int x = 0; x < target.width(); ++x)
                            if (inside(it->bounds, (x + 0.5L) / scale, (y + 0.5L) / scale, 2.0F) &&
                                after[target.index(x, y)] == Pixel{kUiFocusCyan.red, kUiFocusCyan.green, kUiFocusCyan.blue, 255}) ++cyan;
                    check(cyan > 0, "common control focus remains visible");
                    row("focus-strip", target, model, scale, before, after, delta, static_cast<int>(index));
                    ++focus_pairs;
                }
            }
        }
}
void clips() {
    // Include the admitted maximum logical width without a giant surface.
    for (const float width : {1400.0F, 1672.0F, 8192.0F})
        for (const float scale : {1.0F, 1.25F, 1.5F, 2.0F}) {
            auto model = model_at(width, width == 1400.0F ? 820.0F : 941.0F,
                UiWorkspace::Play, UiPresentation::Dimensional);
            const int pw = static_cast<int>(std::ceil(width * scale));
            Target target(1100, 280);
            const SDL_Rect viewport{(1100 - pw) / 2 + 7, 11, pw, static_cast<int>(std::ceil(941.0F * scale))};
            const SDL_Rect clip{static_cast<int>(std::floor((width * 0.5F - 190.0F) * scale)),
                static_cast<int>(std::floor(24.0F * scale)), static_cast<int>(std::floor(340.0F * scale)),
                static_cast<int>(std::floor(65.0F * scale))};
            target.configure(scale, viewport, &clip);
            const auto before = target.paint(model, true), after = target.paint(model, false);
            const auto delta = compare(target, before, after, model);
            check(delta.changed > 0 && delta.visible_after > 1000, "cut clip has meaningful visible paint");
            row("cut-clip", target, model, scale, before, after, delta);
            ++clip_pairs;
        }
}
int run(int argc, char** argv) {
    require(argc == 2, "usage: OUTPUT_DIRECTORY");
    require(SDL_SetHint(SDL_HINT_RENDER_BATCHING, "1") == SDL_TRUE && SDL_Init(0) == 0, "SDL fixed software setup");
    constexpr std::array<std::array<float, 2>, 11> dimensions{{
        {960, 700}, {1280, 900}, {1399, 819}, {1400, 819}, {1399, 820}, {1400, 820},
        {1400.25F, 820.25F}, {1672, 941}, {1920, 700}, {1920, 819}, {1920, 1080}}};
    for (const auto& size : dimensions)
        for (const float scale : {1.0F, 1.25F}) full(size[0], size[1], scale, argv[1]);
    for (const auto& size : {std::array<float, 2>{1400, 820}, std::array<float, 2>{1672, 941}})
        for (const float scale : {1.5F, 2.0F}) full(size[0], size[1], scale, argv[1]);
    focus_strips();
    clips();
    check(full_pairs == 156 && focus_pairs == 120 && clip_pairs == 12, "complete declared matrices");
    std::cout << "{\"kind\":\"summary\",\"checks\":" << checks << ",\"failures\":" << failures
        << ",\"full_pairs\":" << full_pairs << ",\"focus_pairs\":" << focus_pairs
        << ",\"clip_pairs\":" << clip_pairs << ",\"compared_pixels\":" << compared_pixels << "}\n";
    return failures == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
} // namespace
int main(int argc, char** argv) {
    SDL_SetMainReady();
    try { const int result = run(argc, argv); SDL_Quit(); return result; }
    catch (const std::exception& e) { std::cerr << e.what() << '\n'; SDL_Quit(); return EXIT_FAILURE; }
}
