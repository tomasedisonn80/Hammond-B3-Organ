#include "InstrumentView.h"

#include <SDL.h>

#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <filesystem>
#include <iostream>
#include <limits>
#include <memory>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace {
using namespace hammond;
using namespace hammond::standalone;

using Pixel = std::array<std::uint8_t, 4>;
constexpr std::size_t kPlayingKeys = 2 * kManualKeyCount + kPedalCount;
constexpr std::array<std::size_t, 3> kManualNaturals{0, 29, 60};
constexpr std::array<std::size_t, 3> kManualAccidentals{1, 30, 58};
constexpr std::array<std::size_t, 3> kPedalNaturals{0, 12, 24};
constexpr std::array<std::size_t, 3> kPedalAccidentals{1, 13, 22};

struct Counts {
    std::size_t failures{}, frames{}, held{}, focus{}, surfaces{}, occlusions{}, corners{}, hidden{};
} counts;
std::array<long double, 2> minimum_contrast{
    std::numeric_limits<long double>::infinity(), std::numeric_limits<long double>::infinity()};

void require(bool condition, std::string_view detail) {
    if (!condition) throw std::runtime_error(std::string(detail) + ": " + SDL_GetError());
}

void check(bool condition, std::string_view detail) {
    if (!condition) {
        ++counts.failures;
        std::cerr << "FAIL: " << detail << '\n';
    }
}

struct KeyId { std::size_t division{}, index{}; };

std::size_t token(KeyId id) { return id.division * kManualKeyCount + id.index; }

std::span<const UiKeyGeometry> keys(const UiLayout& layout, std::size_t division) {
    if (division < 2) return layout.manual_keys[division];
    return layout.pedal_keys;
}

const std::array<std::size_t, 3>& representatives(std::size_t division, bool accidental) {
    if (division < 2) return accidental ? kManualAccidentals : kManualNaturals;
    return accidental ? kPedalAccidentals : kPedalNaturals;
}

UiControlId control(KeyId id) {
    return {id.division == 2 ? UiControlKind::PedalKey : UiControlKind::ManualKey,
            id.division == 1 ? Manual::Lower : Manual::Upper, DrawbarBank::A,
            static_cast<std::uint8_t>(id.index)};
}

std::string description(int width, int height, UiPresentation presentation, KeyId id) {
    constexpr std::array<std::string_view, 3> names{"Upper", "Lower", "Pedals"};
    return std::to_string(width) + "x" + std::to_string(height) +
        (presentation == UiPresentation::Flat ? " Flat " : " Dimensional ") +
        std::string(names[id.division]) + " index " + std::to_string(id.index);
}

// Independent convex half-plane oracle. Vertex coordinates are shared data;
// no production contains(), hit-test, projection or raster helper is called.
// TL->TR and BL->TL include their boundary. Right/bottom edges exclude theirs.
// Long-double cross products avoid repeating the painter's double division.
long double cross(UiPoint a, UiPoint b, long double x, long double y) {
    return (static_cast<long double>(b.x) - a.x) * (y - a.y) -
           (static_cast<long double>(b.y) - a.y) * (x - a.x);
}

bool inside(const UiQuad& quad, long double x, long double y) {
    const auto& p = quad.points;
    return cross(p[0], p[1], x, y) >= 0.0L && cross(p[1], p[2], x, y) > 0.0L &&
           cross(p[2], p[3], x, y) > 0.0L && cross(p[3], p[0], x, y) >= 0.0L;
}

long double edge_distance(const UiQuad& quad, long double x, long double y) {
    long double result = std::numeric_limits<long double>::infinity();
    for (std::size_t edge = 0; edge < 4; ++edge) {
        const auto a = quad.points[edge];
        const auto b = quad.points[(edge + 1) % 4];
        const long double dx = static_cast<long double>(b.x) - a.x;
        const long double dy = static_cast<long double>(b.y) - a.y;
        result = std::min(result, cross(a, b, x, y) / std::sqrt(dx * dx + dy * dy));
    }
    return result;
}

struct Region { int left{}, top{}, right{}, bottom{}; };

Region region(UiRect rect, int width, int height) {
    return {std::clamp(static_cast<int>(std::floor(rect.x)), 0, width),
            std::clamp(static_cast<int>(std::floor(rect.y)), 0, height),
            std::clamp(static_cast<int>(std::ceil(rect.x + rect.width)), 0, width),
            std::clamp(static_cast<int>(std::ceil(rect.y + rect.height)), 0, height)};
}

std::size_t offset(int x, int y, int width) {
    return static_cast<std::size_t>(y) * static_cast<std::size_t>(width) +
           static_cast<std::size_t>(x);
}

struct Frame {
    int width{}, height{};
    std::vector<Pixel> pixels;
};

Frame render(Drawing& drawing, const UiModel& model, int width, int height) {
    // Deliberately fixed/null inspector: copied held state cannot legitimately
    // change Service/Rotary text, so any changed pixel exposes hidden paint.
    const InstrumentViewInfo info;
    paint_instrument(drawing, model, info);
    SDL_RenderPresent(drawing.renderer());
    Frame result{width, height, std::vector<Pixel>(
        static_cast<std::size_t>(width) * static_cast<std::size_t>(height))};
    static_assert(sizeof(Pixel) == 4);
    require(SDL_RenderReadPixels(drawing.renderer(), nullptr, SDL_PIXELFORMAT_RGBA32,
        result.pixels.data(), width * 4) == 0, "read actual paint_instrument raster");
    ++counts.frames;
    return result;
}

struct Ownership {
    std::vector<int> visible;
    std::array<const UiKeyGeometry*, kPlayingKeys> geometry{};
};

Ownership ownership(const UiLayout& layout, int width, int height) {
    Ownership result{std::vector<int>(
        static_cast<std::size_t>(width) * static_cast<std::size_t>(height), -1), {}};
    for (const bool accidental : {false, true}) {
        for (std::size_t division = 0; division < 3; ++division) {
            const auto group = keys(layout, division);
            for (std::size_t index = 0; index < group.size(); ++index) {
                const auto& key = group[index];
                const auto id = token({division, index});
                result.geometry[id] = &key;
                if (key.accidental != accidental) continue;
                const auto area = region(key.bounds, width, height);
                for (int y = area.top; y < area.bottom; ++y)
                    for (int x = area.left; x < area.right; ++x)
                        if (inside(key.hit, x + 0.5L, y + 0.5L))
                            result.visible[offset(x, y, width)] = static_cast<int>(id);
            }
        }
    }
    return result;
}

bool color_is(Pixel pixel, UiColor color) {
    return pixel == Pixel{color.red, color.green, color.blue, color.alpha};
}

long double luminance(Pixel pixel) {
    return (2126.0L * pixel[0] + 7152.0L * pixel[1] + 722.0L * pixel[2]) / 10000.0L;
}

struct Sample { int x{}, y{}; };

Sample sample(const UiQuad& quad, long double vertical, long double horizontal = 0.5L) {
    const auto& p = quad.points;
    const long double y = p[0].y + (static_cast<long double>(p[3].y) - p[0].y) * vertical;
    const long double left = p[0].x + (static_cast<long double>(p[3].x) - p[0].x) * vertical;
    const long double right = p[1].x + (static_cast<long double>(p[2].x) - p[1].x) * vertical;
    return {static_cast<int>(std::floor(left + (right - left) * horizontal)),
            static_cast<int>(std::floor(y))};
}

Pixel pixel_at(const Frame& frame, const Ownership& owners, KeyId id, Sample point) {
    require(point.x >= 0 && point.y >= 0 && point.x < frame.width && point.y < frame.height,
            "independent surface probe is inside the frame");
    const auto position = offset(point.x, point.y, frame.width);
    require(owners.visible[position] == static_cast<int>(token(id)),
            "independent surface probe belongs to its visible key");
    return frame.pixels[position];
}

UiModel prepared(int width, int height, UiPresentation presentation) {
    UiModel model;
    require(model.resize(static_cast<float>(width), static_cast<float>(height)), "resize model");
    require(model.set_presentation(presentation), "choose presentation");
    SessionSnapshot snapshot;
    snapshot.publication_revision = 2;
    model.observe(snapshot);
    return model;
}

void hold(SessionSnapshot& snapshot, KeyId id) {
    if (id.division < 2) snapshot.held_keys[id.division][id.index] = true;
    else snapshot.held_pedals[id.index] = true;
}

void surface_checks(const UiModel& model, const Frame& baseline, const Ownership& owners) {
    const auto presentation = model.view().presentation;
    for (std::size_t division = 0; division < 3; ++division) {
        for (const bool accidental : {false, true}) {
            for (const auto index : representatives(division, accidental)) {
                const KeyId id{division, index};
                const auto& key = keys(model.layout(), division)[index];
                const auto detail = description(baseline.width, baseline.height, presentation, id);
                require(key.accidental == accidental, "literal representative pitch class");
                if (presentation == UiPresentation::Flat) {
                    const UiColor expected = accidental ? UiColor{32, 33, 30} : UiColor{242, 230, 204};
                    bool uniform = true;
                    for (const long double depth : {0.25L, 0.55L, 0.90L})
                        for (const long double across : {0.40L, 0.50L, 0.60L})
                            uniform = color_is(pixel_at(baseline, owners, id,
                                sample(key.hit, depth, across)), expected) && uniform;
                    check(uniform, detail + " has a uniform Flat surface through the former front area");
                    check(std::all_of(key.front.points.begin(), key.front.points.end(),
                        [](UiPoint p) { return p.x == 0.0F && p.y == 0.0F; }),
                        detail + " has no Flat front quad");
                } else {
                    // A short accidental's cap tail can legitimately approach
                    // its front shade. Compare the central planes, away from
                    // side bevels and the front seam, across nine paired pixels.
                    constexpr std::array<long double, 3> top_depths{0.30L, 0.50L, 0.65L};
                    constexpr std::array<long double, 3> front_depths{0.35L, 0.55L, 0.75L};
                    long double difference = 0.0L;
                    std::size_t darker = 0;
                    for (std::size_t row = 0; row < top_depths.size(); ++row) {
                        for (const long double across : {0.40L, 0.50L, 0.60L}) {
                            const auto upper = pixel_at(baseline, owners, id, sample(key.top, top_depths[row], across));
                            const auto front = pixel_at(baseline, owners, id, sample(key.front, front_depths[row], across));
                            const long double contrast = luminance(upper) - luminance(front);
                            difference += contrast;
                            if (contrast > 0.0L) ++darker;
                        }
                    }
                    difference /= 9.0L;
                    const auto kind = accidental ? std::size_t{1} : std::size_t{0};
                    minimum_contrast[kind] = std::min(minimum_contrast[kind], difference);
                    check(difference >= (accidental ? 8.0L : 20.0L) && darker >= 6,
                          detail + " has darker front-plane samples (mean contrast " +
                          std::to_string(static_cast<double>(difference)) + ", darker pairs " +
                          std::to_string(darker) + "/9)");
                }
                ++counts.surfaces;
                if (!accidental) continue;
                std::array<std::size_t, 2> underneath{kPlayingKeys, kPlayingKeys};
                bool dark = true;
                for (std::size_t side = 0; side < 2; ++side) {
                    const auto point = sample(key.top, 0.40L, side == 0 ? 0.25L : 0.75L);
                    dark = dark && luminance(pixel_at(baseline, owners, id, point)) < 100.0L;
                    const auto group = keys(model.layout(), division);
                    for (std::size_t natural = 0; natural < group.size(); ++natural)
                        if (!group[natural].accidental &&
                            inside(group[natural].hit, point.x + 0.5L, point.y + 0.5L))
                            underneath[side] = natural;
                }
                check(dark && underneath[0] < kPlayingKeys && underneath[1] < kPlayingKeys &&
                      underneath[0] != underneath[1],
                      detail + " visibly occludes both adjacent naturals");
                ++counts.occlusions;
            }
        }
    }
    if (presentation != UiPresentation::Dimensional) return;
    for (std::size_t division = 0; division < 2; ++division) {
        for (const std::size_t index : {std::size_t{0}, kManualKeyCount - 1}) {
            const KeyId id{division, index};
            const auto& key = keys(model.layout(), division)[index];
            const auto area = region(key.bounds, baseline.width, baseline.height);
            std::size_t exposed = 0, painted = 0;
            for (int y = area.top; y < area.bottom; ++y) {
                for (int x = area.left; x < area.right; ++x) {
                    const auto position = offset(x, y, baseline.width);
                    if (x + 0.5L < key.bounds.x || y + 0.5L < key.bounds.y ||
                        x + 0.5L >= static_cast<long double>(key.bounds.x) + key.bounds.width ||
                        y + 0.5L >= static_cast<long double>(key.bounds.y) + key.bounds.height) continue;
                    if (owners.visible[position] != -1 || inside(key.hit, x + 0.5L, y + 0.5L)) continue;
                    ++exposed;
                    if (!color_is(baseline.pixels[position], {7, 9, 8})) ++painted;
                }
            }
            check(exposed > 4 && painted == 0,
                  description(baseline.width, baseline.height, presentation, id) +
                  " leaves sloped AABB corners at the literal dark key bed");
            ++counts.corners;
        }
    }
}

void held_checks(const UiModel& model, const Frame& baseline, const Frame& held,
                 const Ownership& owners, bool accidental) {
    std::array<bool, kPlayingKeys> selected{};
    for (std::size_t division = 0; division < 3; ++division)
        for (const auto index : representatives(division, accidental)) selected[token({division, index})] = true;
    std::array<std::size_t, kPlayingKeys> changed{}, upper{}, front{}, brass{};
    std::size_t leaked = 0;
    std::string first_leak;
    const Region area{0, 0, baseline.width, baseline.height};
    for (int y = area.top; y < area.bottom; ++y) {
        for (int x = area.left; x < area.right; ++x) {
            const auto position = offset(x, y, baseline.width);
            const int owner = owners.visible[position];
            const bool expected = owner >= 0 && selected[static_cast<std::size_t>(owner)];
            if (expected && color_is(held.pixels[position], kUiBrass)) ++brass[static_cast<std::size_t>(owner)];
            if (baseline.pixels[position] == held.pixels[position]) continue;
            if (!expected) {
                ++leaked;
                if (first_leak.empty()) first_leak = " at " + std::to_string(x) + "," + std::to_string(y) +
                    " independent owner " + std::to_string(owner);
                continue;
            }
            const auto id = static_cast<std::size_t>(owner);
            const auto& key = *owners.geometry[id];
            ++changed[id];
            if (inside(key.top, x + 0.5L, y + 0.5L)) ++upper[id];
            if (inside(key.front, x + 0.5L, y + 0.5L)) ++front[id];
        }
    }
    check(leaked == 0, description(baseline.width, baseline.height, model.view().presentation, {0, 0}) +
          (accidental ? " accidental" : " natural") + " held batch has no outside/neighbor/occlusion ink" + first_leak);
    for (std::size_t division = 0; division < 3; ++division) {
        for (const auto index : representatives(division, accidental)) {
            const KeyId id{division, index};
            const auto number = token(id);
            const auto detail = description(baseline.width, baseline.height, model.view().presentation, id);
            check(changed[number] >= 8 && upper[number] > 0 && brass[number] > 0,
                  detail + " shows copied held state and a bounded brass top highlight");
            check(model.view().presentation == UiPresentation::Flat || front[number] > 0,
                  detail + " also changes its dimensional front when held");
            ++counts.held;
        }
    }
}

void focus_checks(const UiModel& model, const Frame& held, const Frame& focused,
                  const Ownership& owners, KeyId id) {
    const auto& key = *owners.geometry[token(id)];
    const Region area{0, 0, held.width, held.height};
    // The full semantic focus caption legitimately changes in the footer.
    // Every other frame pixel, including header and surrounding wood, is gated.
    const auto footer = region(model.layout().footer, held.width, held.height);
    std::size_t changed = 0, leaked = 0, other_ink = 0;
    long double minimum_inset = std::numeric_limits<long double>::infinity();
    std::string first_leak;
    for (int y = area.top; y < area.bottom; ++y) {
        for (int x = area.left; x < area.right; ++x) {
            const auto position = offset(x, y, held.width);
            if (held.pixels[position] == focused.pixels[position]) continue;
            if (x >= footer.left && x < footer.right && y >= footer.top && y < footer.bottom) continue;
            ++changed;
            if (owners.visible[position] != static_cast<int>(token(id)) ||
                !inside(key.hit, x + 0.5L, y + 0.5L)) {
                ++leaked;
                if (first_leak.empty()) first_leak = " at " + std::to_string(x) + "," + std::to_string(y) +
                    " edge distance " + std::to_string(static_cast<double>(edge_distance(key.hit, x + 0.5L, y + 0.5L)));
            }
            if (!color_is(focused.pixels[position], kUiFocusCyan)) ++other_ink;
            minimum_inset = std::min(minimum_inset, edge_distance(key.hit, x + 0.5L, y + 0.5L));
        }
    }
    const auto detail = description(held.width, held.height, model.view().presentation, id);
    check(changed >= 4 && other_ink == 0, detail + " has visible cyan focus while held");
    check(leaked == 0, detail + " focus is contained and respects accidental occlusion" + first_leak);
    check(changed > 0 && minimum_inset >= 1.0L, detail + " focus remains at least one pixel inside its silhouette");
    ++counts.focus;
}

void play_matrix(Drawing& drawing, int width, int height, UiPresentation presentation,
                 const std::filesystem::path& capture_directory) {
    const auto base = prepared(width, height, presentation);
    const auto owners = ownership(base.layout(), width, height);
    const auto baseline = render(drawing, base, width, height);
    surface_checks(base, baseline, owners);
    for (const bool accidental : {false, true}) {
        auto held_model = base;
        auto snapshot = base.view().applied;
        snapshot.publication_revision += 2;
        for (std::size_t division = 0; division < 3; ++division)
            for (const auto index : representatives(division, accidental)) hold(snapshot, {division, index});
        held_model.observe(snapshot);
        const auto held = render(drawing, held_model, width, height);
        held_checks(held_model, baseline, held, owners, accidental);
        for (std::size_t division = 0; division < 3; ++division) {
            for (const auto index : representatives(division, accidental)) {
                const KeyId id{division, index};
                auto focused_model = held_model;
                require(focused_model.activate(control(id)).count == 0 && focused_model.view().focus == control(id),
                        "focus actual model key without a musical action");
                const auto focused = render(drawing, focused_model, width, height);
                focus_checks(focused_model, held, focused, owners, id);
                if (!capture_directory.empty() && width == 1672 && division == 0 && index == 30) {
                    const auto name = presentation == UiPresentation::Flat ?
                        "native-renderer-test-flat-1672x941.bmp" : "native-renderer-test-dimensional-1672x941.bmp";
                    std::string error;
                    require(drawing.save_bmp((capture_directory / name).string(), error),
                            "save optional native renderer test frame: " + error);
                }
            }
        }
    }
}

void hidden_bodies(Drawing& drawing, int width, int height, UiPresentation presentation) {
    for (const auto workspace : {UiWorkspace::Service, UiWorkspace::Rotary}) {
        auto model = prepared(width, height, presentation);
        require(model.activate(control({1, 58})).count == 0, "remember a Play key focus");
        require(model.set_workspace(workspace), "select hidden-performance workspace");
        const auto baseline = render(drawing, model, width, height);
        auto snapshot = model.view().applied;
        snapshot.publication_revision += 2;
        for (auto& manual : snapshot.held_keys) manual.fill(true);
        snapshot.held_pedals.fill(true);
        model.observe(snapshot);
        const auto held = render(drawing, model, width, height);
        const auto name = workspace == UiWorkspace::Service ? " Service " : " Rotary ";
        check(baseline.pixels == held.pixels,
              std::to_string(width) + "x" + std::to_string(height) + name +
              (presentation == UiPresentation::Flat ? "Flat" : "Dimensional") +
              " paints no hidden performance body when all 147 copied held bits change");
        ++counts.hidden;
    }
}
} // namespace

int main(int argc, char** argv) {
    SDL_SetMainReady();
    const auto started = std::chrono::steady_clock::now();
    try {
        require(argc == 1 || argc == 2, "usage: test_standalone_workspace_raster [capture-directory]");
        const char* capture_option = argc == 2 ? argv[1] : SDL_getenv("HAMMOND_WORKSPACE_RASTER_CAPTURE_DIR");
        const std::filesystem::path capture_directory = capture_option == nullptr ? "" : capture_option;
        if (!capture_directory.empty()) std::filesystem::create_directories(capture_directory);
        require(SDL_Init(0) == 0, "initialize SDL without hardware subsystems");
        for (const auto dimensions : std::array<std::array<int, 2>, 3>{{
                 {960, 700}, {1280, 900}, {1672, 941}}}) {
            const int width = dimensions[0], height = dimensions[1];
            const std::unique_ptr<SDL_Surface, decltype(&SDL_FreeSurface)> surface(
                SDL_CreateRGBSurfaceWithFormat(0, width, height, 32, SDL_PIXELFORMAT_RGBA32), SDL_FreeSurface);
            require(surface != nullptr, "create SDL software target");
            const std::unique_ptr<SDL_Renderer, decltype(&SDL_DestroyRenderer)> renderer(
                SDL_CreateSoftwareRenderer(surface.get()), SDL_DestroyRenderer);
            require(renderer != nullptr, "create SDL software renderer");
            Drawing drawing(renderer.get());
            std::string error;
            require(drawing.initialize(error), "initialize native Drawing: " + error);
            for (const auto presentation : {UiPresentation::Dimensional, UiPresentation::Flat}) {
                play_matrix(drawing, width, height, presentation, capture_directory);
                hidden_bodies(drawing, width, height, presentation);
            }
        }
        check(counts.frames == 150 && counts.held == 108 && counts.focus == 108 &&
              counts.surfaces == 108 && counts.occlusions == 54 && counts.corners == 12 && counts.hidden == 12,
              "complete literal representative matrix executed");
        SDL_Quit();
    } catch (const std::exception& error) {
        std::cerr << "Workspace raster setup failed: " << error.what() << '\n';
        SDL_Quit();
        return EXIT_FAILURE;
    }
    const auto elapsed = std::chrono::duration<double>(std::chrono::steady_clock::now() - started).count();
    std::cout << "Native workspace raster: " << counts.frames << " frames; " << counts.held << " held, "
              << counts.focus << " held+focus, " << counts.surfaces << " front/Flat, "
              << counts.occlusions << " two-natural occlusion, " << counts.corners << " sloped-corner, "
              << counts.hidden << " hidden-body checks; failures=" << counts.failures << "; " << elapsed
              << " seconds; minimum top/front mean contrast=" << static_cast<double>(minimum_contrast[0])
              << " natural / " << static_cast<double>(minimum_contrast[1])
              << " accidental; actual paint_instrument, independent half-plane oracle, SDL software surface, no window/audio\n";
    return counts.failures == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
