#include "Drawing.h"

#include <SDL.h>

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <memory>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace {

using namespace hammond::standalone;

constexpr int kWidth = 128;
constexpr int kHeight = 96;
constexpr UiColor kBackground{7, 11, 19, 255};
constexpr UiColor kInk{231, 207, 163, 255};
constexpr UiQuad kKey{{UiPoint{40.0F, 12.0F}, UiPoint{88.0F, 12.0F},
                        UiPoint{104.0F, 84.0F}, UiPoint{24.0F, 84.0F}}};
std::size_t failures{};
std::size_t mask_checks{};

void require(bool condition, std::string_view detail) {
    if (!condition) throw std::runtime_error(std::string(detail) + ": " + SDL_GetError());
}

void check(bool condition, std::string_view detail) {
    if (!condition) {
        ++failures;
        std::cerr << "FAIL: " << detail << '\n';
    }
}

using Pixels = std::vector<std::uint8_t>;

[[nodiscard]] Pixels read_pixels(Drawing& drawing, SDL_Surface* surface) {
    // Read the complete software target even when the renderer has a viewport.
    // SDL_RenderReadPixels(nullptr) otherwise reads only that viewport.
    require(SDL_RenderFlush(drawing.renderer()) == 0, "flush software drawing");
    require(SDL_LockSurface(surface) == 0, "lock software target");
    Pixels pixels(static_cast<std::size_t>(kWidth * kHeight * 4));
    const auto* source = static_cast<const std::uint8_t*>(surface->pixels);
    for (int row = 0; row < kHeight; ++row) {
        std::copy_n(source + static_cast<std::size_t>(row) * static_cast<std::size_t>(surface->pitch),
                    kWidth * 4, pixels.data() + static_cast<std::size_t>(row * kWidth * 4));
    }
    SDL_UnlockSurface(surface);
    return pixels;
}

[[nodiscard]] UiColor pixel(const Pixels& pixels, int x, int y) {
    const auto index = static_cast<std::size_t>((y * kWidth + x) * 4);
    return {pixels[index], pixels[index + 1], pixels[index + 2], pixels[index + 3]};
}

[[nodiscard]] bool changed(const Pixels& pixels, int x, int y) {
    const auto value = pixel(pixels, x, y);
    return value.red != kBackground.red || value.green != kBackground.green ||
           value.blue != kBackground.blue;
}

template <typename Expected>
void check_mask(const Pixels& pixels, Expected expected, std::string_view description) {
    std::size_t mismatches{};
    for (int y = 0; y < kHeight; ++y) {
        for (int x = 0; x < kWidth; ++x) {
            if (changed(pixels, x, y) != expected(x, y)) ++mismatches;
        }
    }
    ++mask_checks;
    check(mismatches == 0, std::string(description) + ": mismatched pixels=" +
          std::to_string(mismatches));
}

// Independent literal fixture: sides move 16 pixels over 72 vertical pixels.
// Neither the production contains() helper nor the raster implementation forms
// this oracle, so rectangular painting or an outward focus stroke will fail.
[[nodiscard]] bool key_contains(double x, double y) {
    return y >= 12.0 && y < 84.0 && x >= 40.0 - (y - 12.0) * 2.0 / 9.0 &&
           x < 88.0 + (y - 12.0) * 2.0 / 9.0;
}

[[nodiscard]] bool key_focus(double x, double y) {
    return key_contains(x, y) && (y < 14.0 || y >= 82.0 ||
        x < 42.0 - (y - 12.0) * 2.0 / 9.0 ||
        x >= 86.0 + (y - 12.0) * 2.0 / 9.0);
}

void check_color(UiColor actual, UiColor expected, int tolerance, std::string_view description) {
    const auto close = [tolerance](std::uint8_t first, std::uint8_t second) {
        return std::abs(static_cast<int>(first) - static_cast<int>(second)) <= tolerance;
    };
    check(close(actual.red, expected.red) && close(actual.green, expected.green) &&
          close(actual.blue, expected.blue), description);
}

void check_silhouette_and_gradient(Drawing& drawing, SDL_Surface* surface) {
    drawing.clear(kBackground);
    drawing.quad(kKey, kInk, kInk);
    check_mask(read_pixels(drawing, surface), [](int x, int y) {
        return key_contains(x + 0.5, y + 0.5);
    }, "sloping key silhouette and half-open bottom");

    constexpr UiColor top{240, 210, 160, 255};
    constexpr UiColor bottom{80, 70, 60, 255};
    drawing.clear(kBackground);
    drawing.quad(kKey, top, bottom);
    const auto pixels = read_pixels(drawing, surface);
    for (const int y : {12, 48, 83}) {
        const double fraction = (y + 0.5 - 12.0) / 72.0;
        const auto channel = [fraction](int a, int b) {
            return static_cast<std::uint8_t>(std::lround(a + (b - a) * fraction));
        };
        check_color(pixel(pixels, 64, y), {channel(240, 80), channel(210, 70),
                    channel(160, 60), 255}, 1, "vertical gradient sample at row " + std::to_string(y));
    }
    check_mask(pixels, [](int x, int y) { return key_contains(x + 0.5, y + 0.5); },
               "gradient preserves the exact key silhouette");

    constexpr UiQuad top_face{{UiPoint{40.0F, 12.0F}, UiPoint{88.0F, 12.0F},
                                UiPoint{100.0F, 66.0F}, UiPoint{28.0F, 66.0F}}};
    constexpr UiQuad front_face{{UiPoint{28.0F, 66.0F}, UiPoint{100.0F, 66.0F},
                                  UiPoint{104.0F, 84.0F}, UiPoint{24.0F, 84.0F}}};
    drawing.clear(kBackground);
    drawing.quad(top_face, {244, 233, 209, 255}, {193, 178, 145, 255});
    drawing.quad(front_face, {119, 100, 72, 255}, {74, 60, 43, 255});
    const auto faces = read_pixels(drawing, surface);
    check_mask(faces, [](int x, int y) { return key_contains(x + 0.5, y + 0.5); },
               "adjacent top/front surfaces have no gap or expanded edge");
    check(pixel(faces, 64, 65).red > pixel(faces, 64, 66).red + 60,
          "front face remains visibly darker at the shared split");
    check(pixel(faces, 64, 66).red > pixel(faces, 64, 83).red + 35,
          "front face retains its own vertical gradient");
}

void check_inside_focus(Drawing& drawing, SDL_Surface* surface) {
    drawing.clear(kBackground);
    constexpr UiColor focus{231, 207, 163, 128};
    drawing.quad_outline(kKey, focus, 2.0F);
    const auto pixels = read_pixels(drawing, surface);
    check_mask(pixels, [](int x, int y) { return key_focus(x + 0.5, y + 0.5); },
               "two-pixel focus follows the inside of all four edges");
    const auto blend = [](std::uint8_t source, std::uint8_t background) {
        return static_cast<std::uint8_t>(std::lround((source * 128.0 + background * 127.0) / 255.0));
    };
    const UiColor expected{blend(focus.red, kBackground.red), blend(focus.green, kBackground.green),
                           blend(focus.blue, kBackground.blue), 255};
    bool painted_once = true;
    for (int y = 0; y < kHeight; ++y) {
        for (int x = 0; x < kWidth; ++x) {
            if (!changed(pixels, x, y)) continue;
            const auto actual = pixel(pixels, x, y);
            painted_once = painted_once && std::abs(static_cast<int>(actual.red) - expected.red) <= 1 &&
                std::abs(static_cast<int>(actual.green) - expected.green) <= 1 &&
                std::abs(static_cast<int>(actual.blue) - expected.blue) <= 1;
        }
    }
    check(painted_once, "translucent focus corners and side bands are painted exactly once");

    constexpr UiQuad narrow{{UiPoint{60.0F, 10.0F}, UiPoint{64.0F, 10.0F},
                              UiPoint{66.0F, 32.0F}, UiPoint{58.0F, 32.0F}}};
    drawing.clear(kBackground);
    drawing.quad_outline(narrow, kInk, 100.0F);
    const auto small = read_pixels(drawing, surface);
    check_mask(small, [](int x, int y) {
        const double px = x + 0.5;
        const double py = y + 0.5;
        const double slope = (py - 10.0) / 11.0;
        const bool inside = py >= 10.0 && py < 32.0 && px >= 60.0 - slope && px < 64.0 + slope;
        return inside && (py < 12.0 || py >= 30.0 || px < 62.0 - slope || px >= 62.0 + slope);
    }, "thickness clamps safely on a four-pixel accidental");
    check(changed(small, 60, 10) && !changed(small, 62, 21),
          "small accidental has visible focus while retaining an unpainted center");
}

void check_shared_edges(Drawing& drawing, SDL_Surface* surface) {
    // Pixel centers lie exactly on every outside and shared boundary here.
    // Translucency exposes a double-owned seam as well as a missing column.
    constexpr UiQuad left{{UiPoint{10.5F, 10.5F}, UiPoint{26.5F, 10.5F},
                            UiPoint{26.5F, 21.5F}, UiPoint{10.5F, 21.5F}}};
    constexpr UiQuad right{{UiPoint{26.5F, 10.5F}, UiPoint{42.5F, 10.5F},
                             UiPoint{42.5F, 21.5F}, UiPoint{26.5F, 21.5F}}};
    constexpr UiColor translucent{231, 207, 163, 128};
    drawing.clear(kBackground);
    drawing.quad(left, translucent, translucent);
    drawing.quad(right, translucent, translucent);
    const auto pixels = read_pixels(drawing, surface);
    check_mask(pixels, [](int x, int y) {
        return x >= 10 && x < 42 && y >= 10 && y < 21;
    }, "fractional shared edges retain exactly one half-open pixel owner");
    check_color(pixel(pixels, 26, 15), pixel(pixels, 20, 15), 0,
                "shared edge receives one alpha blend rather than two");
}

void check_invalid_inputs(Drawing& drawing, SDL_Surface* surface) {
    const float nan = std::numeric_limits<float>::quiet_NaN();
    const float infinity = std::numeric_limits<float>::infinity();
    std::array<UiQuad, 9> invalid{};
    invalid.fill(kKey);
    invalid[0] = {};
    invalid[1].points[0].x = nan;
    invalid[2].points[2].y = infinity;
    invalid[3].points[1].y = 13.0F;
    invalid[4].points[2].y = 85.0F;
    invalid[5].points[1].x = 40.0F;
    invalid[6].points[2].x = 23.0F;
    invalid[7].points[2].y = invalid[7].points[3].y = 12.0F;
    invalid[8].points[2].y = invalid[8].points[3].y = 11.0F;
    drawing.clear(kBackground);
    for (const auto& shape : invalid) {
        drawing.quad(shape, kInk, kInk);
        drawing.quad_outline(shape, kInk, 2.0F);
    }
    for (const float thickness : {0.0F, -1.0F, nan, infinity}) {
        drawing.quad_outline(kKey, kInk, thickness);
    }
    check_mask(read_pixels(drawing, surface), [](int, int) { return false; },
               "empty/nonfinite/malformed shapes and invalid thickness are no-ops");
    Drawing missing_renderer(nullptr);
    missing_renderer.quad(kKey, kInk, kInk);
    missing_renderer.quad_outline(kKey, kInk);
}

[[nodiscard]] bool same_rect(SDL_Rect a, SDL_Rect b) {
    return a.x == b.x && a.y == b.y && a.w == b.w && a.h == b.h;
}

struct RenderState {
    float scale_x{};
    float scale_y{};
    SDL_Rect viewport{};
    SDL_Rect clip{};
    SDL_bool clipping{};
    SDL_BlendMode blend{};
};

[[nodiscard]] RenderState state(SDL_Renderer* renderer) {
    RenderState result;
    SDL_RenderGetScale(renderer, &result.scale_x, &result.scale_y);
    SDL_RenderGetViewport(renderer, &result.viewport);
    SDL_RenderGetClipRect(renderer, &result.clip);
    result.clipping = SDL_RenderIsClipEnabled(renderer);
    require(SDL_GetRenderDrawBlendMode(renderer, &result.blend) == 0, "read draw blend mode");
    return result;
}

void check_state(SDL_Renderer* renderer, const RenderState& before, std::string_view description) {
    const auto after = state(renderer);
    check(before.scale_x == after.scale_x && before.scale_y == after.scale_y &&
          same_rect(before.viewport, after.viewport) && same_rect(before.clip, after.clip) &&
          before.clipping == after.clipping && before.blend == after.blend, description);
}

void reset_renderer(SDL_Renderer* renderer) {
    require(SDL_RenderSetScale(renderer, 1.0F, 1.0F) == 0, "reset scale");
    require(SDL_RenderSetViewport(renderer, nullptr) == 0, "reset viewport");
    require(SDL_RenderSetClipRect(renderer, nullptr) == 0, "reset clip");
}

void check_scaled_and_clipped(Drawing& drawing, SDL_Surface* surface) {
    auto* renderer = drawing.renderer();
    for (const float scale : {1.0F, 1.5F, 2.0F}) {
        reset_renderer(renderer);
        drawing.clear(kBackground);
        const SDL_Rect viewport{10, 8, 100, 80};
        require(SDL_RenderSetViewport(renderer, &viewport) == 0, "set translated viewport");
        require(SDL_RenderSetScale(renderer, scale, scale) == 0, "set renderer scale");
        const SDL_Rect clip{4, 3, 60, 48};
        require(SDL_RenderSetClipRect(renderer, &clip) == 0, "set logical clipping rectangle");
        const auto before = state(renderer);
        drawing.quad(kKey, kInk, kInk);
        check_state(renderer, before, "quad preserves scale, viewport, clip and blend mode");
        const auto pixels = read_pixels(drawing, surface);
        check_mask(pixels, [scale](int x, int y) {
            const int px = x - 10;
            const int py = y - 8;
            const double logical_x = (px + 0.5) / scale;
            const double logical_y = (py + 0.5) / scale;
            return px >= 0 && px < 100 && py >= 0 && py < 80 &&
                px >= static_cast<int>(4.0F * scale) && px < static_cast<int>(64.0F * scale) &&
                py >= static_cast<int>(3.0F * scale) && py < static_cast<int>(51.0F * scale) &&
                key_contains(logical_x, logical_y);
        }, "scaled translated quad with clip at scale " + std::to_string(scale));

        drawing.clear(kBackground);
        drawing.quad_outline(kKey, kInk, 2.0F);
        check_state(renderer, before, "focus preserves scale, viewport, clip and blend mode");
        check_mask(read_pixels(drawing, surface), [scale](int x, int y) {
            const int px = x - 10;
            const int py = y - 8;
            return px >= 0 && px < 100 && py >= 0 && py < 80 &&
                px >= static_cast<int>(4.0F * scale) && px < static_cast<int>(64.0F * scale) &&
                py >= static_cast<int>(3.0F * scale) && py < static_cast<int>(51.0F * scale) &&
                key_focus((px + 0.5) / scale, (py + 0.5) / scale);
        }, "scaled focus stays inside clipped silhouette at scale " + std::to_string(scale));
    }
    reset_renderer(renderer);
}

void check_bounded_work(Drawing& drawing, SDL_Surface* surface) {
    auto* renderer = drawing.renderer();
    constexpr float maximum = std::numeric_limits<float>::max();
    const UiQuad huge{{UiPoint{-maximum, -maximum}, UiPoint{maximum, -maximum},
                        UiPoint{maximum, maximum}, UiPoint{-maximum, maximum}}};
    drawing.clear(kBackground);
    const SDL_Rect viewport{-7, -5, 150, 110};
    require(SDL_RenderSetViewport(renderer, &viewport) == 0, "set partially off-target viewport");
    const SDL_Rect clip{19, 15, 23, 17};
    require(SDL_RenderSetClipRect(renderer, &clip) == 0, "set small clip for huge shape");
    const auto before = state(renderer);
    drawing.quad(huge, kInk, kInk);
    check_state(renderer, before, "huge quad restores renderer state");
    check_mask(read_pixels(drawing, surface), [](int x, int y) {
        return x >= 12 && x < 35 && y >= 10 && y < 27;
    }, "FLT_MAX quad is bounded by actual viewport/output/clip");

    drawing.clear(kBackground);
    drawing.quad_outline(huge, kInk, 2.0F);
    check_mask(read_pixels(drawing, surface), [](int, int) { return false; },
               "offscreen edges of huge quad do not become viewport focus edges");
    const SDL_Rect empty_clip{1, 1, 0, 1};
    require(SDL_RenderSetClipRect(renderer, &empty_clip) == 0, "set empty clipping rectangle");
    const auto empty_before = state(renderer);
    drawing.quad(huge, kInk, kInk);
    drawing.quad_outline(kKey, kInk, 2.0F);
    check_state(renderer, empty_before, "empty clipped quad restores renderer state");
    check_mask(read_pixels(drawing, surface), [](int, int) { return false; },
               "empty clip never paints");

    reset_renderer(renderer);
    const UiQuad offscreen{{UiPoint{maximum / 2.0F, maximum / 2.0F},
                             UiPoint{maximum, maximum / 2.0F},
                             UiPoint{maximum, maximum}, UiPoint{maximum / 2.0F, maximum}}};
    drawing.quad(offscreen, kInk, kInk);
    drawing.quad_outline(offscreen, kInk, 2.0F);
    check_mask(read_pixels(drawing, surface), [](int, int) { return false; },
               "huge offscreen shape completes without painting or unbounded iteration");
}

} // namespace

int main() {
    SDL_SetMainReady();
    try {
        require(SDL_Init(0) == 0, "initialize SDL without hardware subsystems");
        {
            const std::unique_ptr<SDL_Surface, decltype(&SDL_FreeSurface)> surface(
                SDL_CreateRGBSurfaceWithFormat(0, kWidth, kHeight, 32, SDL_PIXELFORMAT_RGBA32),
                SDL_FreeSurface);
            require(surface != nullptr, "create software target");
            const std::unique_ptr<SDL_Renderer, decltype(&SDL_DestroyRenderer)> renderer(
                SDL_CreateSoftwareRenderer(surface.get()), SDL_DestroyRenderer);
            require(renderer != nullptr, "create software renderer");
            SDL_RendererInfo info{};
            require(SDL_GetRendererInfo(renderer.get(), &info) == 0, "identify renderer");
            require((info.flags & SDL_RENDERER_SOFTWARE) != 0, "require software rasterization");
            require(SDL_SetRenderDrawBlendMode(renderer.get(), SDL_BLENDMODE_BLEND) == 0,
                    "set normal drawing blend mode");
            Drawing drawing(renderer.get());
            // Primitive testing needs no fonts, decorative assets, window,
            // hardware device, Session or sound-model construction.
            check_silhouette_and_gradient(drawing, surface.get());
            check_inside_focus(drawing, surface.get());
            check_shared_edges(drawing, surface.get());
            check_invalid_inputs(drawing, surface.get());
            check_scaled_and_clipped(drawing, surface.get());
            check_bounded_work(drawing, surface.get());
            SDL_version version{};
            SDL_GetVersion(&version);
            std::cout << "SDL " << static_cast<int>(version.major) << '.' <<
                static_cast<int>(version.minor) << '.' << static_cast<int>(version.patch) <<
                ", renderer=" << info.name << ", no window/audio; " << mask_checks <<
                " full-target coverage checks; failures=" << failures << '\n';
        }
        SDL_Quit();
    } catch (const std::exception& error) {
        std::cerr << "Quad drawing test setup failed: " << error.what() << '\n';
        SDL_Quit();
        return EXIT_FAILURE;
    }
    return failures == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
