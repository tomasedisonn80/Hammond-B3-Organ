#include "Drawing.h"
#include "FontData.h"

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

constexpr int kWidth = 640;
constexpr int kHeight = 96;
constexpr UiColor kBackground{17, 23, 31, 255};
constexpr UiColor kInk{227, 211, 173, 255};
std::size_t failures = 0;
std::size_t glyph_cases = 0;

void require(bool condition, std::string_view detail) {
    if (!condition) throw std::runtime_error(std::string(detail) + ": " + SDL_GetError());
}

void check(bool condition, std::string_view detail) {
    if (!condition) {
        ++failures;
        std::cerr << "FAIL: " << detail << '\n';
    }
}

[[nodiscard]] std::string_view face_name(TextFace face) {
    return face == TextFace::Sans ? "Sans" : "Serif";
}

// Check the committed data itself, independently of the drawing rectangle.
// The authoring generator promises exactly two transparent pixels of gutter.
void check_atlas_gutters(const font_data::Atlas& atlas, TextFace face) {
    constexpr int padding = 2;
    std::vector<std::uint8_t> alpha(static_cast<std::size_t>(atlas.width) * atlas.height);
    require(font_data::decode_alpha(atlas, alpha), "decode font atlas");
    for (std::size_t index = 0; index < atlas.glyphs.size(); ++index) {
        const auto& glyph = atlas.glyphs[index];
        if (glyph.width == 0 || glyph.height == 0) continue;
        const int left = static_cast<int>(glyph.x) - padding;
        const int top = static_cast<int>(glyph.y) - padding;
        const int right = static_cast<int>(glyph.x) + glyph.width + padding;
        const int bottom = static_cast<int>(glyph.y) + glyph.height + padding;
        const auto description = std::string(face_name(face)) + " atlas gutter for ASCII " +
            std::to_string(index + font_data::kFirstCodepoint);
        const bool bounded = left >= 0 && top >= 0 && right <= atlas.width && bottom <= atlas.height;
        check(bounded, description + " stays within the atlas");
        if (!bounded) continue;
        bool transparent = true;
        for (int y = top; y < bottom; ++y) {
            for (int x = left; x < right; ++x) {
                const bool inside_ink_rectangle = x >= glyph.x && y >= glyph.y &&
                    x < static_cast<int>(glyph.x) + glyph.width &&
                    y < static_cast<int>(glyph.y) + glyph.height;
                if (!inside_ink_rectangle) {
                    transparent = transparent && alpha[static_cast<std::size_t>(y) * atlas.width +
                        static_cast<std::size_t>(x)] == 0;
                }
            }
        }
        check(transparent, description + " contains only transparent pixels");
    }
}

struct Coverage {
    std::size_t changed_pixels{};
    int maximum_red_increase{};
};

[[nodiscard]] Coverage render_and_read(Drawing& drawing, std::string_view text,
                                       float size, TextFace face, float fraction = 0.0F) {
    drawing.clear(kBackground);
    drawing.text(text, 32.0F + fraction, 16.0F + fraction, size, kInk, face);
    SDL_RenderPresent(drawing.renderer());
    std::vector<std::uint8_t> pixels(static_cast<std::size_t>(kWidth * kHeight * 4));
    require(SDL_RenderReadPixels(drawing.renderer(), nullptr, SDL_PIXELFORMAT_RGBA32,
                                pixels.data(), kWidth * 4) == 0, "read software-rendered pixels");
    Coverage coverage;
    for (std::size_t offset = 0; offset < pixels.size(); offset += 4) {
        if (pixels[offset] != kBackground.red || pixels[offset + 1] != kBackground.green ||
            pixels[offset + 2] != kBackground.blue) {
            ++coverage.changed_pixels;
            coverage.maximum_red_increase = std::max(coverage.maximum_red_increase,
                static_cast<int>(pixels[offset]) - kBackground.red);
        }
    }
    return coverage;
}

void check_individual_glyphs(Drawing& drawing) {
    // Each character gets a freshly cleared surface. A visible neighboring glyph
    // or a nonblank sentence therefore cannot conceal a vanished l, i, or '-'.
    constexpr std::array sizes{9.0F, 9.5F, 10.5F, 16.0F, 24.0F, 32.0F};
    constexpr std::array fractions{0.0F, 0.25F, 0.5F, 0.75F};
    for (const auto face : {TextFace::Sans, TextFace::Serif}) {
        for (const float size : sizes) {
            for (const char glyph : {'l', 'i', '-'}) {
                for (const float fraction : fractions) {
                    const auto coverage = render_and_read(drawing, std::string_view(&glyph, 1),
                                                          size, face, fraction);
                    ++glyph_cases;
                    const auto description = std::string(face_name(face)) + " '" + glyph +
                        "' at " + std::to_string(size) + " px, fraction " + std::to_string(fraction) +
                        ": ink pixels=" + std::to_string(coverage.changed_pixels) +
                        ", maximum red increase=" + std::to_string(coverage.maximum_red_increase);
                    check(coverage.changed_pixels > 0 && coverage.maximum_red_increase >= 8,
                          description);
                }
            }
        }
    }
}

void check_text_and_metrics(Drawing& drawing) {
    constexpr std::string_view instruction = "Close Full --list-midi";
    constexpr std::array sizes{9.0F, 9.5F, 10.5F, 16.0F, 24.0F, 32.0F};
    for (const auto face : {TextFace::Sans, TextFace::Serif}) {
        // Frozen from the pre-repair public text_width results, not recomputed
        // from the copied source rectangle or a second copy of its algorithm.
        const float nominal_width = face == TextFace::Sans ? 317.0F : 414.0F;
        const float nominal_height = face == TextFace::Sans ? 32.0F : 40.0F;
        const float multiline_width = face == TextFace::Sans ? 317.0F : 437.0F;
        for (const float size : sizes) {
            const auto description = std::string(face_name(face)) + " text at " + std::to_string(size);
            check(std::abs(drawing.text_width(instruction, size, face) -
                           nominal_width * size / nominal_height) < 0.001F,
                  description + " preserves advance-based width");
            check(std::abs(drawing.text_width("TONEWHEEL ATLAS\nClose Full --list-midi", size, face) -
                           multiline_width * size / nominal_height) < 0.001F,
                  description + " preserves multiline width");
            check(drawing.text_width("", size, face) == 0.0F, description + " has zero empty width");
            const auto empty = render_and_read(drawing, " ", size, face);
            check(empty.changed_pixels == 0, description + " keeps spaces transparent");
        }
        for (const float size : {16.0F, 24.0F, 32.0F}) {
            for (const auto text : {"TONEWHEEL ATLAS", "NOMINAL DRY ORGAN", "16' 5 1/3' 8'"}) {
                const auto coverage = render_and_read(drawing, text, size, face);
                check(coverage.changed_pixels >= 40 && coverage.maximum_red_increase >= 64,
                      std::string(face_name(face)) + " normal-size label: " + text);
            }
        }
    }
}

// Filled material surfaces must cover every output-pixel center in their
// silhouette. Presence-only checks miss the one-in-three clear rows formerly
// produced by 1-logical-pixel SDL_FRect strips at a renderer scale of 1.5.
using SurfacePixels = std::vector<std::uint8_t>;
std::size_t surface_cases{};
std::size_t surface_pixel_checks{};

struct SurfaceState {
    float scale_x{};
    float scale_y{};
    SDL_Rect viewport{};
    SDL_Rect clip{};
    SDL_bool clipping{};
    SDL_BlendMode blend{};
};

[[nodiscard]] SurfaceState surface_state(SDL_Renderer* renderer) {
    SurfaceState result;
    SDL_RenderGetScale(renderer, &result.scale_x, &result.scale_y);
    require(SDL_RenderSetScale(renderer, 1.0F, 1.0F) == 0, "read physical renderer state");
    SDL_RenderGetViewport(renderer, &result.viewport);
    SDL_RenderGetClipRect(renderer, &result.clip);
    result.clipping = SDL_RenderIsClipEnabled(renderer);
    require(SDL_GetRenderDrawBlendMode(renderer, &result.blend) == 0, "read surface blend mode");
    require(SDL_RenderSetScale(renderer, result.scale_x, result.scale_y) == 0,
            "restore observed renderer scale");
    return result;
}

void check_surface_state(SDL_Renderer* renderer, const SurfaceState& before,
                         std::string_view description) {
    const auto after = surface_state(renderer);
    const auto same_rect = [](SDL_Rect a, SDL_Rect b) {
        return a.x == b.x && a.y == b.y && a.w == b.w && a.h == b.h;
    };
    check(before.scale_x == after.scale_x && before.scale_y == after.scale_y &&
          same_rect(before.viewport, after.viewport) && same_rect(before.clip, after.clip) &&
          before.clipping == after.clipping && before.blend == after.blend,
          std::string(description) + " preserves scale, physical viewport/clip and blend mode");
}

void reset_surface_renderer(SDL_Renderer* renderer) {
    require(SDL_RenderSetScale(renderer, 1.0F, 1.0F) == 0, "reset surface scale");
    require(SDL_RenderSetViewport(renderer, nullptr) == 0, "reset surface viewport");
    require(SDL_RenderSetClipRect(renderer, nullptr) == 0, "reset surface clip");
}

[[nodiscard]] SurfacePixels surface_pixels(Drawing& drawing, SDL_Surface* surface) {
    // Read the whole backing target, including pixels outside the viewport.
    require(SDL_RenderFlush(drawing.renderer()) == 0, "flush filled surfaces");
    require(SDL_LockSurface(surface) == 0, "lock filled-surface target");
    SurfacePixels pixels(static_cast<std::size_t>(kWidth * kHeight * 4));
    const auto* source = static_cast<const std::uint8_t*>(surface->pixels);
    for (int row = 0; row < kHeight; ++row) {
        std::copy_n(source + static_cast<std::size_t>(row) * static_cast<std::size_t>(surface->pitch),
                    kWidth * 4, pixels.data() + static_cast<std::size_t>(row * kWidth * 4));
    }
    SDL_UnlockSurface(surface);
    return pixels;
}

[[nodiscard]] UiColor surface_pixel(const SurfacePixels& pixels, int x, int y) {
    const auto offset = static_cast<std::size_t>((y * kWidth + x) * 4);
    return {pixels[offset], pixels[offset + 1], pixels[offset + 2], pixels[offset + 3]};
}

[[nodiscard]] bool same_surface_color(UiColor a, UiColor b, int tolerance = 0) {
    return std::abs(static_cast<int>(a.red) - b.red) <= tolerance &&
           std::abs(static_cast<int>(a.green) - b.green) <= tolerance &&
           std::abs(static_cast<int>(a.blue) - b.blue) <= tolerance &&
           std::abs(static_cast<int>(a.alpha) - b.alpha) <= tolerance;
}

[[nodiscard]] bool surface_visible(const SurfaceState& state, int x, int y) {
    const int px = x - state.viewport.x;
    const int py = y - state.viewport.y;
    return px >= 0 && px < state.viewport.w && py >= 0 && py < state.viewport.h &&
        (state.clipping == SDL_FALSE || (px >= state.clip.x && px < state.clip.x + state.clip.w &&
                                        py >= state.clip.y && py < state.clip.y + state.clip.h));
}

[[nodiscard]] bool rectangle_contains(UiRect bounds, double x, double y) {
    return x >= bounds.x && x < static_cast<double>(bounds.x) + bounds.width &&
           y >= bounds.y && y < static_cast<double>(bounds.y) + bounds.height;
}

// Independent two-dimensional circle-distance oracle; it neither computes
// scanline insets nor calls production geometry/rounding helpers.
[[nodiscard]] bool rounded_contains(UiRect bounds, float requested_radius, double x, double y) {
    if (!rectangle_contains(bounds, x, y)) return false;
    const double radius = std::clamp(static_cast<double>(requested_radius), 0.0,
        std::min(static_cast<double>(bounds.width), static_cast<double>(bounds.height)) / 2.0);
    const double right = static_cast<double>(bounds.x) + bounds.width;
    const double bottom = static_cast<double>(bounds.y) + bounds.height;
    const double dx = x - std::clamp(x, bounds.x + radius, right - radius);
    const double dy = y - std::clamp(y, bounds.y + radius, bottom - radius);
    const double distance_squared = dx * dx + dy * dy;
    return distance_squared < radius * radius ||
        (distance_squared == radius * radius && (radius == 0.0 || x < right - radius));
}

template <typename Contains>
void check_surface_coverage(const SurfacePixels& pixels, const SurfaceState& state,
                            Contains contains, UiColor expected, int tolerance,
                            std::string_view description) {
    std::size_t missing{};
    std::size_t overpaint{};
    std::size_t wrong_color{};
    for (int y = 0; y < kHeight; ++y) {
        for (int x = 0; x < kWidth; ++x) {
            const bool inside = surface_visible(state, x, y) &&
                contains((x - state.viewport.x + 0.5) / state.scale_x,
                         (y - state.viewport.y + 0.5) / state.scale_y);
            const auto actual = surface_pixel(pixels, x, y);
            const bool background = same_surface_color(actual, kBackground);
            if (inside && background) ++missing;
            else if (inside && !same_surface_color(actual, expected, tolerance)) ++wrong_color;
            else if (!inside && !background) ++overpaint;
        }
    }
    ++surface_cases;
    surface_pixel_checks += static_cast<std::size_t>(kWidth * kHeight);
    check(missing == 0 && overpaint == 0 && wrong_color == 0,
          std::string(description) + ": missing=" + std::to_string(missing) +
          ", overpaint=" + std::to_string(overpaint) + ", wrong/summed color=" +
          std::to_string(wrong_color));
}

void check_filled_surface_coverage(Drawing& drawing, SDL_Surface* surface) {
    constexpr std::array scales{std::array{1.0F, 1.0F}, std::array{1.5F, 1.5F},
        std::array{2.0F, 2.0F}, std::array{0.75F, 0.75F}, std::array{1.25F, 1.25F},
        std::array{1.25F, 1.75F}};
    constexpr std::array bounds{UiRect{12.0F, 8.0F, 40.0F, 24.0F},
        UiRect{10.5F, 6.5F, 36.0F, 24.0F}, UiRect{-2.25F, -3.25F, 56.5F, 40.75F},
        UiRect{25.25F, 14.75F, 1.25F, 7.5F}};
    constexpr std::array radii{6.0F, 5.0F, 9.25F, 10.0F};
    for (const auto& scale : scales) {
        for (int viewport_case = 0; viewport_case < 3; ++viewport_case) {
            reset_surface_renderer(drawing.renderer());
            if (viewport_case != 0) {
                const SDL_Rect viewport = viewport_case == 1 ? SDL_Rect{7, 5, 117, 83} :
                                                               SDL_Rect{-9, -7, 140, 110};
                const SDL_Rect clip = viewport_case == 1 ? SDL_Rect{3, 7, 91, 61} :
                                                           SDL_Rect{13, 11, 79, 55};
                require(SDL_RenderSetViewport(drawing.renderer(), &viewport) == 0,
                        "set physical filled-surface viewport");
                require(SDL_RenderSetClipRect(drawing.renderer(), &clip) == 0,
                        "set physical filled-surface clip");
            }
            require(SDL_RenderSetScale(drawing.renderer(), scale[0], scale[1]) == 0,
                    "set filled-surface scale");
            const auto before = surface_state(drawing.renderer());
            for (std::size_t shape = 0; shape < bounds.size(); ++shape) {
                for (const std::uint8_t alpha : {std::uint8_t{255}, std::uint8_t{128}}) {
                    const UiColor ink{kInk.red, kInk.green, kInk.blue, alpha};
                    const auto blended = [alpha](std::uint8_t a, std::uint8_t b) {
                        return static_cast<std::uint8_t>(std::lround((a * static_cast<double>(alpha) +
                            b * (255.0 - alpha)) / 255.0));
                    };
                    const UiColor expected{blended(ink.red, kBackground.red),
                        blended(ink.green, kBackground.green), blended(ink.blue, kBackground.blue), 255};
                    for (const bool rounded : {false, true}) {
                        drawing.clear(kBackground);
                        if (rounded) drawing.rounded(bounds[shape], radii[shape], ink);
                        else drawing.gradient(bounds[shape], ink, ink);
                        const auto description = std::string(rounded ? "rounded" : "gradient") +
                            " scale=" + std::to_string(scale[0]) + "," + std::to_string(scale[1]) +
                            " viewport=" + std::to_string(viewport_case) + " shape=" +
                            std::to_string(shape) + " alpha=" + std::to_string(alpha);
                        check_surface_state(drawing.renderer(), before, description);
                        check_surface_coverage(surface_pixels(drawing, surface), before,
                            [shape, rounded, &bounds, &radii](double x, double y) {
                                return rounded ? rounded_contains(bounds[shape], radii[shape], x, y) :
                                                 rectangle_contains(bounds[shape], x, y);
                            }, expected, alpha == 255 ? 0 : 1, description);
                    }
                }
            }
        }
    }
    reset_surface_renderer(drawing.renderer());
}

void check_surface_gradients(Drawing& drawing, SDL_Surface* surface) {
    struct Sample { float scale; int row; UiColor expected; };
    // Frozen hand-calculated stops for a ten-logical-pixel ramp whose first
    // and last logical pixel centers retain the old integer-scale palette.
    constexpr std::array samples{
        Sample{1.0F, 0, {240, 40, 20, 255}}, Sample{1.0F, 1, {220, 60, 40, 255}},
        Sample{1.0F, 4, {160, 120, 100, 255}}, Sample{1.0F, 9, {60, 220, 200, 255}},
        Sample{1.5F, 0, {240, 40, 20, 255}}, Sample{1.5F, 1, {230, 50, 30, 255}},
        Sample{1.5F, 7, {150, 130, 110, 255}}, Sample{1.5F, 13, {70, 210, 190, 255}},
        Sample{1.5F, 14, {60, 220, 200, 255}}, Sample{2.0F, 0, {240, 40, 20, 255}},
        Sample{2.0F, 1, {235, 45, 25, 255}}, Sample{2.0F, 9, {155, 125, 105, 255}},
        Sample{2.0F, 10, {145, 135, 115, 255}}, Sample{2.0F, 18, {65, 215, 195, 255}},
        Sample{2.0F, 19, {60, 220, 200, 255}}};
    for (const float scale : {1.0F, 1.5F, 2.0F}) {
        reset_surface_renderer(drawing.renderer());
        require(SDL_RenderSetScale(drawing.renderer(), scale, scale) == 0, "set gradient scale");
        drawing.clear(kBackground);
        drawing.gradient({12.0F, 8.0F, 40.0F, 10.0F}, {240, 40, 20, 255}, {60, 220, 200, 255});
        const auto complete = surface_pixels(drawing, surface);
        for (const auto& sample : samples) {
            if (sample.scale != scale) continue;
            check(same_surface_color(surface_pixel(complete, static_cast<int>(24.0F * scale),
                  static_cast<int>(8.0F * scale) + sample.row), sample.expected),
                  "literal gradient stop at scale=" + std::to_string(scale) +
                  " row=" + std::to_string(sample.row));
        }
        // A cropped gradient must be identical to its original pixels, so the
        // clip must neither move its color stops nor normalize the visible rows.
        require(SDL_RenderSetScale(drawing.renderer(), 1.0F, 1.0F) == 0, "set physical ramp clip");
        const SDL_Rect clip{19, 15, 45, 14};
        require(SDL_RenderSetClipRect(drawing.renderer(), &clip) == 0, "crop ramp");
        require(SDL_RenderSetScale(drawing.renderer(), scale, scale) == 0, "restore ramp scale");
        const auto before = surface_state(drawing.renderer());
        drawing.clear(kBackground);
        drawing.gradient({12.0F, 8.0F, 40.0F, 10.0F}, {240, 40, 20, 255}, {60, 220, 200, 255});
        check_surface_state(drawing.renderer(), before, "clipped gradient");
        const auto cropped = surface_pixels(drawing, surface);
        std::size_t mismatches{};
        for (int y = 0; y < kHeight; ++y) {
            for (int x = 0; x < kWidth; ++x) {
                const UiColor expected = surface_visible(before, x, y) ? surface_pixel(complete, x, y) :
                                                                      kBackground;
                if (!same_surface_color(surface_pixel(cropped, x, y), expected)) ++mismatches;
            }
        }
        ++surface_cases;
        surface_pixel_checks += static_cast<std::size_t>(kWidth * kHeight);
        check(mismatches == 0, "clipping preserves gradient colors and surrounding pixels");
    }
    reset_surface_renderer(drawing.renderer());
}

void check_surface_bounds(Drawing& drawing, SDL_Surface* surface) {
    const float maximum = std::numeric_limits<float>::max();
    const float nan = std::numeric_limits<float>::quiet_NaN();
    const float infinity = std::numeric_limits<float>::infinity();
    const UiRect valid{12.0F, 8.0F, 40.0F, 24.0F};
    drawing.clear(kBackground);
    for (const UiRect invalid : {UiRect{}, UiRect{12, 8, -1, 24}, UiRect{12, 8, 40, -1},
        UiRect{nan, 8, 40, 24}, UiRect{12, infinity, 40, 24}, UiRect{12, 8, infinity, 24},
        UiRect{12, 8, 40, nan}, UiRect{maximum / 2, maximum / 2, maximum / 4, maximum / 4}}) {
        drawing.gradient(invalid, kInk, kInk);
        drawing.rounded(invalid, 6.0F, kInk);
    }
    drawing.rounded(valid, nan, kInk);
    drawing.rounded(valid, infinity, kInk);
    check_surface_coverage(surface_pixels(drawing, surface), surface_state(drawing.renderer()),
        [](double, double) { return false; }, kInk, 0, "invalid and huge off-target surfaces are no-ops");
    for (const float radius : {0.0F, -2.0F}) {
        drawing.clear(kBackground);
        drawing.rounded(valid, radius, kInk);
        check_surface_coverage(surface_pixels(drawing, surface), surface_state(drawing.renderer()),
            [valid](double x, double y) { return rectangle_contains(valid, x, y); }, kInk, 0,
            "zero and negative radii produce the bounded rectangle");
    }
    drawing.clear(kBackground);
    constexpr UiRect thin{12.5F, 8.5F, 8.0F, 0.75F};
    drawing.gradient(thin, kInk, {0, 0, 0, 255});
    check_surface_coverage(surface_pixels(drawing, surface), surface_state(drawing.renderer()),
        [thin](double x, double y) { return rectangle_contains(thin, x, y); }, kInk, 0,
        "subpixel-height gradient retains its first color without expanding its bounds");
    const SDL_Rect viewport{-9, -7, 140, 110};
    const SDL_Rect clip{22, 18, 37, 19};
    require(SDL_RenderSetViewport(drawing.renderer(), &viewport) == 0, "set huge-surface viewport");
    require(SDL_RenderSetClipRect(drawing.renderer(), &clip) == 0, "set huge-surface clip");
    require(SDL_RenderSetScale(drawing.renderer(), 1.5F, 1.75F) == 0, "scale huge surface");
    const UiRect huge{-maximum / 4, -maximum / 4, maximum / 2, maximum / 2};
    for (const bool rounded : {false, true}) {
        drawing.clear(kBackground);
        const auto before = surface_state(drawing.renderer());
        if (rounded) drawing.rounded(huge, maximum, kInk);
        else drawing.gradient(huge, kInk, kInk);
        check_surface_state(drawing.renderer(), before, "huge clipped surface");
        check_surface_coverage(surface_pixels(drawing, surface), before,
            [](double, double) { return true; }, kInk, 0,
            "huge surface is bounded by the actual output, viewport and clip");
    }
    drawing.clear(kBackground);
    const SDL_Rect empty{1, 1, 0, 1};
    require(SDL_RenderSetClipRect(drawing.renderer(), &empty) == 0, "set empty surface clip");
    const auto before = surface_state(drawing.renderer());
    drawing.gradient(valid, kInk, kInk);
    drawing.rounded(valid, 6.0F, kInk);
    check_surface_state(drawing.renderer(), before, "empty-clipped surfaces");
    check_surface_coverage(surface_pixels(drawing, surface), before,
        [](double, double) { return false; }, kInk, 0, "empty clip remains empty");
    reset_surface_renderer(drawing.renderer());
    Drawing no_renderer(nullptr);
    no_renderer.gradient(valid, kInk, kInk);
    no_renderer.rounded(valid, 6.0F, kInk);
}

} // namespace

int main() {
    SDL_SetMainReady();
    try {
        // Software rendering directly to a surface needs no video window,
        // physical display, audio device, MIDI device, or application Session.
        require(SDL_Init(0) == 0, "initialize SDL without hardware subsystems");
        {
            const std::unique_ptr<SDL_Surface, decltype(&SDL_FreeSurface)> surface(
                SDL_CreateRGBSurfaceWithFormat(0, kWidth, kHeight, 32, SDL_PIXELFORMAT_RGBA32),
                SDL_FreeSurface);
            require(surface != nullptr, "create software target surface");
            const std::unique_ptr<SDL_Renderer, decltype(&SDL_DestroyRenderer)> renderer(
                SDL_CreateSoftwareRenderer(surface.get()), SDL_DestroyRenderer);
            require(renderer != nullptr, "create SDL software renderer");
            SDL_RendererInfo info{};
            require(SDL_GetRendererInfo(renderer.get(), &info) == 0, "identify renderer");
            check((info.flags & SDL_RENDERER_SOFTWARE) != 0, "renderer is explicitly software");
            SDL_version version{};
            SDL_GetVersion(&version);
            std::cout << "SDL " << static_cast<int>(version.major) << '.' <<
                static_cast<int>(version.minor) << '.' << static_cast<int>(version.patch) <<
                ", renderer=" << info.name << ", no window/audio\n";

            Drawing drawing(renderer.get());
            std::string error;
            require(drawing.initialize(error), "initialize Drawing: " + error);
            check_atlas_gutters(font_data::kSans, TextFace::Sans);
            check_atlas_gutters(font_data::kSerif, TextFace::Serif);
            check_individual_glyphs(drawing);
            check_text_and_metrics(drawing);
            check_filled_surface_coverage(drawing, surface.get());
            check_surface_gradients(drawing, surface.get());
            check_surface_bounds(drawing, surface.get());
        }
        SDL_Quit();
    } catch (const std::exception& error) {
        std::cerr << "SDL drawing test setup failed: " << error.what() << '\n';
        SDL_Quit();
        return EXIT_FAILURE;
    }
    std::cout << glyph_cases << " individual glyph cases, 18 normal-size labels, " <<
        "12 width/multiline/space cases; " << surface_cases <<
        " full-target surface checks (" << surface_pixel_checks << " pixels); failures=" << failures << '\n';
    return failures == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
