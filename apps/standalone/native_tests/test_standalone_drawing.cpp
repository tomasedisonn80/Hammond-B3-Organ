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
        }
        SDL_Quit();
    } catch (const std::exception& error) {
        std::cerr << "SDL drawing test setup failed: " << error.what() << '\n';
        SDL_Quit();
        return EXIT_FAILURE;
    }
    std::cout << glyph_cases << " individual glyph cases, 18 normal-size labels, " <<
        "12 width/multiline/space cases; failures=" << failures << '\n';
    return failures == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
