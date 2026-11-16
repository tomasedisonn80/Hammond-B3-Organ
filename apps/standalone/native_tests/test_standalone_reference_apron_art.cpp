#include "Drawing.h"
#include "ReferenceApronData.h"

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

using hammond::standalone::Drawing;
using hammond::standalone::UiRect;
namespace apron = hammond::standalone::reference_apron;
using Pixel = std::array<std::uint8_t, 4>;
using Pixels = std::vector<std::uint8_t>;

constexpr int kWidth = 2560;
constexpr int kHeight = 180;
constexpr int kApronLeft = 16;
constexpr int kApronTop = 24;
constexpr int kApronWidth = 1640;
constexpr int kApronHeight = 54;
constexpr std::size_t kHoleTexels = 56016;
constexpr std::size_t kOpaqueTexels = 32544;
constexpr UiRect kBounds{16.0F, 24.0F, 1640.0F, 54.0F};
constexpr Pixel kBlue{7, 37, 241, 255};
constexpr Pixel kGold{239, 191, 11, 255};
std::size_t checks{};
std::size_t failures{};
std::size_t canonical_probes{};
std::size_t state_probes{};
std::size_t invalid_probes{};

void require(bool condition, std::string_view detail) {
    if (!condition) throw std::runtime_error(std::string(detail) + ": " + SDL_GetError());
}

void check(bool condition, std::string_view detail) {
    ++checks;
    if (condition) return;
    ++failures;
    std::cerr << "FAIL: " << detail << '\n';
}

[[nodiscard]] std::size_t offset(int x, int y, int width) {
    return (static_cast<std::size_t>(y) * static_cast<std::size_t>(width) +
            static_cast<std::size_t>(x)) * 4;
}

[[nodiscard]] Pixel pixel(const std::uint8_t* bytes, int x, int y, int width) {
    const auto at = offset(x, y, width);
    return {bytes[at], bytes[at + 1], bytes[at + 2], bytes[at + 3]};
}

[[nodiscard]] bool in_hole(int x, int y) {
    return x >= 32 && x < 1588 && y >= 2 && y < 38;
}

void check_embedded_mask() {
    require(apron::kApron.width == kApronWidth && apron::kApron.height == kApronHeight &&
            apron::kApron.pitch == kApronWidth * 4 &&
            apron::kApron.byte_count == 354240 && apron::kTotalPixelBytes == 354240,
            "exact embedded apron extent and pitch");
    std::size_t holes = 0;
    std::size_t opaque = 0;
    std::size_t incorrect = 0;
    for (int y = 0; y < kApronHeight; ++y) {
        for (int x = 0; x < kApronWidth; ++x) {
            const auto source = pixel(apron::kApron.pixels, x, y, kApronWidth);
            if (in_hole(x, y)) {
                ++holes;
                if (source != Pixel{}) ++incorrect;
            } else {
                ++opaque;
                if (source[3] != 255) ++incorrect;
            }
        }
    }
    check(holes == kHoleTexels && opaque == kOpaqueTexels && incorrect == 0,
          "all 56016 hole texels are zero RGBA and all 32544 exterior texels are opaque");
    // The independent asset suite compares this embedded source's byte stream
    // to the pinned JPEG decode. This native probe tests its actual compositing.
}

struct RendererState {
    float scale_x{};
    float scale_y{};
    SDL_Rect viewport{};
    SDL_Rect clip{};
    SDL_bool clipped{};
    SDL_BlendMode blend{};
    Pixel color{};
};

[[nodiscard]] RendererState renderer_state(SDL_Renderer* renderer) {
    RendererState state;
    SDL_RenderGetScale(renderer, &state.scale_x, &state.scale_y);
    require(SDL_RenderSetScale(renderer, 1.0F, 1.0F) == 0, "observe physical renderer state");
    SDL_RenderGetViewport(renderer, &state.viewport);
    SDL_RenderGetClipRect(renderer, &state.clip);
    state.clipped = SDL_RenderIsClipEnabled(renderer);
    require(SDL_GetRenderDrawBlendMode(renderer, &state.blend) == 0, "observe draw blend mode");
    require(SDL_GetRenderDrawColor(renderer, &state.color[0], &state.color[1],
                                  &state.color[2], &state.color[3]) == 0,
            "observe draw color");
    require(SDL_RenderSetScale(renderer, state.scale_x, state.scale_y) == 0,
            "restore observed scale");
    return state;
}

[[nodiscard]] bool same_rect(const SDL_Rect& first, const SDL_Rect& second) {
    return first.x == second.x && first.y == second.y &&
           first.w == second.w && first.h == second.h;
}

void check_state(SDL_Renderer* renderer, const RendererState& before) {
    const auto after = renderer_state(renderer);
    check(before.scale_x == after.scale_x && before.scale_y == after.scale_y &&
          same_rect(before.viewport, after.viewport) && same_rect(before.clip, after.clip) &&
          before.clipped == after.clipped && before.blend == after.blend &&
          before.color == after.color,
          "apron copy preserves scale, physical viewport, physical clip/enabled flag, blend and color");
}

class Target {
public:
    Target()
        : surface_(SDL_CreateRGBSurfaceWithFormat(0, kWidth, kHeight, 32, SDL_PIXELFORMAT_RGBA32),
                   SDL_FreeSurface),
          renderer_(surface_ ? SDL_CreateSoftwareRenderer(surface_.get()) : nullptr,
                    SDL_DestroyRenderer) {
        require(surface_ != nullptr && renderer_ != nullptr, "create software target");
    }

    [[nodiscard]] SDL_Renderer* renderer() const noexcept { return renderer_.get(); }

    void clear(Pixel backdrop) const {
        require(SDL_RenderSetScale(renderer(), 1.0F, 1.0F) == 0, "reset scale");
        require(SDL_RenderSetViewport(renderer(), nullptr) == 0, "reset viewport");
        require(SDL_RenderSetClipRect(renderer(), nullptr) == 0, "reset clip");
        require(SDL_SetRenderDrawBlendMode(renderer(), SDL_BLENDMODE_NONE) == 0,
                "set backdrop blend mode");
        require(SDL_SetRenderDrawColor(renderer(), backdrop[0], backdrop[1],
                                      backdrop[2], backdrop[3]) == 0, "set backdrop");
        require(SDL_RenderClear(renderer()) == 0, "clear entire target");
    }

    void configure(float scale_x, float scale_y, const SDL_Rect& viewport,
                   const SDL_Rect* clip, SDL_BlendMode blend) const {
        require(SDL_RenderSetScale(renderer(), 1.0F, 1.0F) == 0, "configure physical scale");
        require(SDL_RenderSetViewport(renderer(), &viewport) == 0, "configure physical viewport");
        require(SDL_RenderSetClipRect(renderer(), clip) == 0, "configure physical clip");
        require(SDL_RenderSetScale(renderer(), scale_x, scale_y) == 0, "configure incoming scale");
        require(SDL_SetRenderDrawBlendMode(renderer(), blend) == 0, "configure incoming blend");
        require(SDL_SetRenderDrawColor(renderer(), 9, 57, 105, 183) == 0,
                "configure unrelated draw color");
    }

    [[nodiscard]] Pixels read() const {
        require(SDL_RenderFlush(renderer()) == 0, "flush apron copy");
        Pixels result(static_cast<std::size_t>(kWidth) * static_cast<std::size_t>(kHeight) * 4);
        require(SDL_LockSurface(surface_.get()) == 0, "lock software target");
        const auto* source = static_cast<const std::uint8_t*>(surface_->pixels);
        for (int y = 0; y < kHeight; ++y) {
            std::copy_n(source + static_cast<std::size_t>(y) *
                        static_cast<std::size_t>(surface_->pitch), kWidth * 4,
                        result.data() + offset(0, y, kWidth));
        }
        SDL_UnlockSurface(surface_.get());
        return result;
    }

private:
    std::unique_ptr<SDL_Surface, decltype(&SDL_FreeSurface)> surface_;
    std::unique_ptr<SDL_Renderer, decltype(&SDL_DestroyRenderer)> renderer_;
};

[[nodiscard]] Pixels canonical_probe(Target& target, Drawing& drawing, Pixel backdrop,
                                     SDL_BlendMode blend) {
    target.clear(backdrop);
    target.configure(1.0F, 1.0F, {0, 0, kWidth, kHeight}, nullptr, blend);
    const auto before = renderer_state(target.renderer());
    check(drawing.apron_art(kBounds), "canonical apron copy succeeds");
    check_state(target.renderer(), before);
    auto actual = target.read();
    std::size_t hole_matches = 0;
    std::size_t opaque_matches = 0;
    std::size_t exterior_changes = 0;
    for (int y = 0; y < kHeight; ++y) {
        for (int x = 0; x < kWidth; ++x) {
            const auto observed = pixel(actual.data(), x, y, kWidth);
            const bool inside = x >= kApronLeft && x < kApronLeft + kApronWidth &&
                                y >= kApronTop && y < kApronTop + kApronHeight;
            if (!inside) {
                if (observed != backdrop) ++exterior_changes;
                continue;
            }
            const int source_x = x - kApronLeft;
            const int source_y = y - kApronTop;
            if (in_hole(source_x, source_y)) {
                if (observed == backdrop) ++hole_matches;
            } else if (observed == pixel(apron::kApron.pixels, source_x, source_y, kApronWidth)) {
                ++opaque_matches;
            }
        }
    }
    check(hole_matches == kHoleTexels, "every H pixel retains the exact opaque backdrop RGBA");
    check(opaque_matches == kOpaqueTexels, "every opaque texel retains exact embedded source RGBA");
    check(exterior_changes == 0, "canonical copy changes no pixel outside its destination");
    ++canonical_probes;
    return actual;
}

[[nodiscard]] bool inside_rect(const SDL_Rect& bounds, int x, int y) {
    return x >= bounds.x && y >= bounds.y &&
           x < bounds.x + bounds.w && y < bounds.y + bounds.h;
}

[[nodiscard]] bool permitted_pixel(const RendererState& state, int x, int y) {
    if (!inside_rect(state.viewport, x, y)) return false;
    if (state.clipped == SDL_TRUE &&
        !inside_rect(state.clip, x - state.viewport.x, y - state.viewport.y)) return false;
    const double left = state.viewport.x + static_cast<double>(kBounds.x) * state.scale_x;
    const double top = state.viewport.y + static_cast<double>(kBounds.y) * state.scale_y;
    const double right = state.viewport.x +
        static_cast<double>(kBounds.x + kBounds.width) * state.scale_x;
    const double bottom = state.viewport.y +
        static_cast<double>(kBounds.y + kBounds.height) * state.scale_y;
    return x >= std::floor(left) && x < std::ceil(right) &&
           y >= std::floor(top) && y < std::ceil(bottom);
}

void transformed_probe(Target& target, Drawing& drawing, float scale_x, float scale_y,
                       const SDL_Rect* clip, SDL_BlendMode blend, bool visible) {
    target.clear(kGold);
    target.configure(scale_x, scale_y, {13, 17, 2527, 149}, clip, blend);
    const auto before = renderer_state(target.renderer());
    check(drawing.apron_art(kBounds), "valid transformed/empty-clipped apron copy succeeds");
    check_state(target.renderer(), before);
    const auto actual = target.read();
    std::size_t changed = 0;
    std::size_t escaped = 0;
    for (int y = 0; y < kHeight; ++y) {
        for (int x = 0; x < kWidth; ++x) {
            if (pixel(actual.data(), x, y, kWidth) == kGold) continue;
            ++changed;
            if (!permitted_pixel(before, x, y)) ++escaped;
        }
    }
    check(escaped == 0, "transformed copy respects the output, viewport, clip and destination envelope");
    check(visible ? changed > 0 : changed == 0,
          "visible copies are nonvacuous and empty/disjoint clips preserve every pixel");
    ++state_probes;
}

void invalid_bounds_probe(Target& target, Drawing& drawing) {
    target.clear(kBlue);
    target.configure(1.25F, 1.5F, {13, 17, 2527, 149}, nullptr, SDL_BLENDMODE_ADD);
    const auto before = renderer_state(target.renderer());
    const auto original = target.read();
    const float nan = std::numeric_limits<float>::quiet_NaN();
    const float infinity = std::numeric_limits<float>::infinity();
    const std::array invalid{
        UiRect{16.0F, 24.0F, 0.0F, 54.0F}, UiRect{16.0F, 24.0F, 1640.0F, 0.0F},
        UiRect{16.0F, 24.0F, -1.0F, 54.0F}, UiRect{16.0F, 24.0F, 1640.0F, -1.0F},
        UiRect{nan, 24.0F, 1640.0F, 54.0F}, UiRect{16.0F, nan, 1640.0F, 54.0F},
        UiRect{16.0F, 24.0F, nan, 54.0F}, UiRect{16.0F, 24.0F, 1640.0F, nan},
        UiRect{infinity, 24.0F, 1640.0F, 54.0F}, UiRect{16.0F, infinity, 1640.0F, 54.0F},
        UiRect{16.0F, 24.0F, infinity, 54.0F}, UiRect{16.0F, 24.0F, 1640.0F, infinity},
        UiRect{-infinity, 24.0F, 1640.0F, 54.0F}, UiRect{16.0F, -infinity, 1640.0F, 54.0F},
        UiRect{16.0F, 24.0F, -infinity, 54.0F}, UiRect{16.0F, 24.0F, 1640.0F, -infinity}};
    for (const auto bounds : invalid) {
        check(!drawing.apron_art(bounds), "nonfinite/nonpositive bounds return false");
        check_state(target.renderer(), before);
        check(target.read() == original, "rejected bounds do not draw");
        ++invalid_probes;
    }
    Drawing unprepared(target.renderer());
    check(!unprepared.apron_art(kBounds), "unprepared optional apron returns false");
    check_state(target.renderer(), before);
    check(target.read() == original, "unprepared apron does not draw");
    Drawing absent(nullptr);
    check(!absent.apron_art(kBounds), "absent renderer and texture return false");
}

} // namespace

int main() {
    SDL_SetMainReady();
    try {
        require(SDL_Init(0) == 0, "initialize SDL without hardware subsystems");
        check_embedded_mask();
        Pixels canonical;
        {
            Target target;
            SDL_RendererInfo info{};
            require(SDL_GetRendererInfo(target.renderer(), &info) == 0, "identify renderer");
            require((info.flags & SDL_RENDERER_SOFTWARE) != 0, "explicit software renderer");
            SDL_version version{};
            SDL_GetVersion(&version);
            std::cout << "SDL " << static_cast<int>(version.major) << '.'
                      << static_cast<int>(version.minor) << '.' << static_cast<int>(version.patch)
                      << "; renderer=" << info.name << "; bounded direct apron probe\n";
            Drawing drawing(target.renderer());
            std::string error;
            require(drawing.initialize(error), "initialize Drawing");
            canonical = canonical_probe(target, drawing, kBlue, SDL_BLENDMODE_NONE);
            (void)canonical_probe(target, drawing, kGold, SDL_BLENDMODE_ADD);
            const SDL_Rect partial{37, 30, 2390, 105};
            const SDL_Rect empty{3, 7, 0, 41};
            const SDL_Rect disjoint{2, 2, 23, 9};
            transformed_probe(target, drawing, 1.5F, 1.5F, nullptr, SDL_BLENDMODE_MOD, true);
            transformed_probe(target, drawing, 2.0F, 2.0F, &partial, SDL_BLENDMODE_NONE, true);
            transformed_probe(target, drawing, 1.25F, 1.5F, &partial, SDL_BLENDMODE_ADD, true);
            transformed_probe(target, drawing, 1.25F, 1.5F, &empty, SDL_BLENDMODE_BLEND, false);
            transformed_probe(target, drawing, 1.5F, 1.5F, &disjoint, SDL_BLENDMODE_MOD, false);
            invalid_bounds_probe(target, drawing);
            check(canonical_probe(target, drawing, kBlue, SDL_BLENDMODE_NONE) == canonical,
                  "canonical pixels repeat after another backdrop and renderer state");
        }
        {
            Target fresh;
            Drawing drawing(fresh.renderer());
            std::string error;
            require(drawing.initialize(error), "initialize fresh Drawing");
            check(canonical_probe(fresh, drawing, kBlue, SDL_BLENDMODE_NONE) == canonical,
                  "fresh Drawing produces identical canonical pixels");
        }
        SDL_Quit();
    } catch (const std::exception& error) {
        std::cerr << "Direct reference apron probe setup failed: " << error.what() << '\n';
        SDL_Quit();
        return EXIT_FAILURE;
    }
    std::cout << "{\"checks\":" << checks << ",\"failures\":" << failures
              << ",\"canonical_probes\":" << canonical_probes
              << ",\"renderer_state_probes\":" << state_probes
              << ",\"invalid_bounds_probes\":" << invalid_probes
              << ",\"hole_texels_per_canonical_probe\":" << kHoleTexels
              << ",\"opaque_texels_per_canonical_probe\":" << kOpaqueTexels
              << ",\"backend\":\"SDL software surface; no audio or window\"}\n";
    return failures == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
