#include "InstrumentView.h"

#include <SDL.h>

#include <array>
#include <bit>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <limits>
#include <memory>
#include <stdexcept>
#include <string>
#include <string_view>

// This executable compiles the real painter here, exactly once. Do not also
// add InstrumentView.cpp as a CMake source. No production hook or before mode.
#include "../InstrumentView.cpp"

namespace {
using hammond::standalone::Drawing;
using Pixel = std::array<std::uint8_t, 4>;
static_assert(sizeof(Pixel) == 4);
static_assert(sizeof(float) == 4 && std::numeric_limits<float>::is_iec559);
static_assert(std::bit_cast<std::uint32_t>(0.1F) == 0x3dcccccdU);

constexpr int width = 200;
constexpr int height = 120;
constexpr Pixel background{173, 181, 193, 211};
constexpr Pixel incoming{17, 23, 31, 127};

struct ExpectedPixel {
    int y;
    Pixel rgba;
};

// Independent prospective oracle for H1 section 4 at binary32 scale 0.1.
// Enumerating the prescribed mixer gives 21 marks in physical clip (7,0,1,120).
// Opaque collision order leaves the following nine pixels; all others retain
// background. Colors come from the contract's literal knots and arithmetic,
// cross-checked with exact rational interpolation, never from painter output.
// Final pair/mark per row: 7366/1,7493/0,4912/1,8172/0,2467/0,4052/1,
// 4463/0,6686/0,7813/1. See the retained A39 derivation note.
constexpr std::array<ExpectedPixel, 9> expected_grain{{
    {1, {30, 25, 21, 255}},
    {2, {45, 40, 37, 255}},
    {3, {21, 17, 14, 255}},
    {4, {35, 32, 29, 255}},
    {5, {33, 30, 28, 255}},
    {6, {19, 16, 14, 255}},
    {8, {31, 28, 26, 255}},
    {9, {28, 26, 24, 255}},
    {10, {18, 16, 14, 255}},
}};

std::size_t checks{};
std::size_t pixels_checked{};
std::size_t grain_pixels_checked{};
std::string_view current_case{"initialization"};

void check(bool condition, std::string_view message) {
    ++checks;
    if (!condition) throw std::runtime_error(std::string(message));
}
void sdl_check(int result, std::string_view message) {
    ++checks;
    if (result != 0) throw std::runtime_error(std::string(message) + ": " + SDL_GetError());
}
bool same_rect(SDL_Rect a, SDL_Rect b) {
    return a.x == b.x && a.y == b.y && a.w == b.w && a.h == b.h;
}
bool same_scale(float a, float b) {
    return std::bit_cast<std::uint32_t>(a) == std::bit_cast<std::uint32_t>(b);
}
struct RendererState {
    float sx{}, sy{};
    SDL_Rect logical_viewport{}, logical_clip{}, physical_viewport{}, physical_clip{};
    SDL_bool clipped{};
    SDL_BlendMode blend{};
    Pixel color{};
};
RendererState state(SDL_Renderer* renderer) {
    RendererState result;
    SDL_RenderGetScale(renderer, &result.sx, &result.sy);
    SDL_RenderGetViewport(renderer, &result.logical_viewport);
    SDL_RenderGetClipRect(renderer, &result.logical_clip);
    result.clipped = SDL_RenderIsClipEnabled(renderer);
    sdl_check(SDL_GetRenderDrawBlendMode(renderer, &result.blend), "query blend mode");
    sdl_check(SDL_GetRenderDrawColor(renderer, &result.color[0], &result.color[1],
                                    &result.color[2], &result.color[3]), "query draw color");
    sdl_check(SDL_RenderSetScale(renderer, 1.0F, 1.0F), "query physical rectangles at scale one");
    SDL_RenderGetViewport(renderer, &result.physical_viewport);
    SDL_RenderGetClipRect(renderer, &result.physical_clip);
    sdl_check(SDL_RenderSetScale(renderer, result.sx, result.sy), "restore query scale");
    return result;
}
void check_state(const RendererState& before, const RendererState& after) {
    check(same_scale(before.sx, after.sx) && same_scale(before.sy, after.sy),
          "helper restores both exact scale bit patterns");
    check(same_rect(before.logical_viewport, after.logical_viewport) &&
          same_rect(before.physical_viewport, after.physical_viewport),
          "helper preserves logical and physical viewport");
    check(same_rect(before.logical_clip, after.logical_clip) &&
          same_rect(before.physical_clip, after.physical_clip),
          "helper preserves logical and physical clip");
    check(before.clipped == after.clipped, "helper preserves clip enable");
    check(before.blend == after.blend, "helper preserves blend mode");
    check(before.color == after.color, "helper restores incoming RGBA draw color");
}

void run_case(SDL_BlendMode blend, bool empty_clip) {
    using Surface = std::unique_ptr<SDL_Surface, decltype(&SDL_FreeSurface)>;
    using Renderer = std::unique_ptr<SDL_Renderer, decltype(&SDL_DestroyRenderer)>;
    Surface surface(SDL_CreateRGBSurfaceWithFormat(0, width, height, 32,
                                                   SDL_PIXELFORMAT_RGBA32), SDL_FreeSurface);
    check(surface != nullptr, "create fixed 200 by 120 RGBA surface");
    sdl_check(SDL_FillRect(surface.get(), nullptr,
              SDL_MapRGBA(surface->format, background[0], background[1], background[2], background[3])),
              "initialize every pixel, including alpha, independently of painter");
    Renderer renderer(SDL_CreateSoftwareRenderer(surface.get()), SDL_DestroyRenderer);
    check(renderer != nullptr, "create real SDL software renderer");
    Drawing drawing(renderer.get()); // Rectangles need no font/art initialization.
    SDL_RendererInfo info{};
    sdl_check(SDL_GetRendererInfo(renderer.get(), &info), "query renderer backend");
    check(info.name != nullptr && std::string_view(info.name) == "software", "software backend is required");
    int output_width{}, output_height{};
    sdl_check(SDL_GetRendererOutputSize(renderer.get(), &output_width, &output_height), "query physical output");
    check(output_width == width && output_height == height, "literal output dimensions");
    const SDL_Rect viewport{0, 0, width, height};
    const SDL_Rect clip{7, 0, empty_clip ? 0 : 1, height};
    sdl_check(SDL_RenderSetScale(renderer.get(), 1.0F, 1.0F), "install physical state at scale one");
    sdl_check(SDL_RenderSetViewport(renderer.get(), &viewport), "install physical viewport");
    sdl_check(SDL_RenderSetClipRect(renderer.get(), &clip), "install enabled physical clip");
    sdl_check(SDL_RenderSetScale(renderer.get(), 0.1F, 0.1F), "install admitted small positive scale");
    sdl_check(SDL_SetRenderDrawBlendMode(renderer.get(), blend), "install caller blend mode");
    sdl_check(SDL_SetRenderDrawColor(renderer.get(), incoming[0], incoming[1], incoming[2], incoming[3]),
              "install distinct caller RGBA draw color");
    const auto before = state(renderer.get());
    check(same_scale(before.sx, 0.1F) && same_scale(before.sy, 0.1F) &&
          same_rect(before.physical_viewport, viewport) && same_rect(before.physical_clip, clip) &&
          before.clipped == SDL_TRUE && before.blend == blend && before.color == incoming,
          "actual renderer state equals the literal counterexample");

    // Canonical 1672 by 941 composition: exact already-inset header and unit
    // scene scale. The field occupies intrinsic x [8,160), clipped to [8,8).
    // Grain at canonical x78/79 instead truncates to x7 with minimum extent one.
    hammond::standalone::reference_header_h1_material(
        drawing, {76.0F, 14.0F, 1520.0F, 94.0F}, {1.0F, 1.0F, 1.0F});
    check_state(before, state(renderer.get()));
    sdl_check(SDL_RenderFlush(renderer.get()), "flush actual helper drawing");
    check_state(before, state(renderer.get()));
    sdl_check(SDL_LockSurface(surface.get()), "lock exact RGBA surface");
    std::size_t visible{};
    bool pixels_match = true;
    int failed_x = -1, failed_y = -1;
    Pixel failed_expected{}, failed_actual{};
    const auto* bytes = static_cast<const std::uint8_t*>(surface->pixels);
    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            Pixel expected = background;
            if (!empty_clip && x == 7) {
                for (const auto& point : expected_grain) {
                    if (point.y == y) { expected = point.rgba; ++visible; break; }
                }
            }
            Pixel actual{};
            std::memcpy(actual.data(), bytes + static_cast<std::size_t>(y) * static_cast<std::size_t>(surface->pitch) +
                         static_cast<std::size_t>(x) * sizeof(Pixel), sizeof(Pixel));
            ++pixels_checked;
            if (actual != expected && pixels_match) {
                pixels_match = false; failed_x = x; failed_y = y;
                failed_expected = expected; failed_actual = actual;
            }
        }
    }
    SDL_UnlockSurface(surface.get());
    if (!pixels_match) {
        std::string message = "exact RGBA differs at (" + std::to_string(failed_x) + "," + std::to_string(failed_y) + "): expected";
        for (auto channel : failed_expected) message += " " + std::to_string(channel);
        message += "; actual";
        for (auto channel : failed_actual) message += " " + std::to_string(channel);
        throw std::runtime_error(message);
    }
    check(pixels_match, "all 24000 pixels equal independent expected RGBA");
    check(visible == (empty_clip ? 0U : expected_grain.size()), "exact nine grain pixels or enabled-empty clip");
    grain_pixels_checked += visible;
}
} // namespace

int main() {
    SDL_SetMainReady();
    try {
        sdl_check(SDL_Init(0), "initialize SDL without window or audio device");
        current_case = "BLEND narrow clip"; run_case(SDL_BLENDMODE_BLEND, false);
        current_case = "NONE narrow clip"; run_case(SDL_BLENDMODE_NONE, false);
        current_case = "BLEND enabled-empty clip"; run_case(SDL_BLENDMODE_BLEND, true);
        current_case = "NONE enabled-empty clip"; run_case(SDL_BLENDMODE_NONE, true);
        check(pixels_checked == 96000 && grain_pixels_checked == 18, "complete four-case coverage");
        SDL_Quit();
        std::cout << "{\"schema\":1,\"protocol\":\"header-h1-grain-bounds-v1\",\"status\":\"passed\","
                  << "\"cases\":4,\"checks\":" << checks << ",\"pixels_checked\":" << pixels_checked
                  << ",\"grain_pixels_checked\":" << grain_pixels_checked
                  << ",\"unchanged_pixels_checked\":" << pixels_checked - grain_pixels_checked
                  << ",\"backend\":\"SDL software surface; no window or audio\"}\n";
        return EXIT_SUCCESS;
    } catch (const std::exception& error) {
        std::cerr << "Header H1 grain bounds failed in " << current_case << ": " << error.what() << '\n';
        SDL_Quit();
        return EXIT_FAILURE;
    }
}
