#include "Drawing.h"
#include <SDL.h>
#include <cstdint>
#include <iostream>

int main() {
    SDL_SetMainReady();
    if (SDL_Init(0) != 0) return 2;
    auto* surface = SDL_CreateRGBSurfaceWithFormat(0, 128, 96, 32, SDL_PIXELFORMAT_RGBA32);
    auto* renderer = surface == nullptr ? nullptr : SDL_CreateSoftwareRenderer(surface);
    if (renderer == nullptr) return 2;
    using namespace hammond::standalone;
    Drawing drawing(renderer);
    SDL_SetRenderDrawBlendMode(renderer, SDL_BLENDMODE_BLEND);
    int failures = 0;
    for (const float scale : {1.0F, 1.5F, 2.0F}) {
        SDL_RenderSetScale(renderer, scale, scale);
        for (const bool rounded : {false, true}) {
            drawing.clear({17, 23, 31, 255});
            if (rounded) drawing.rounded({12, 8, 40, 24}, 6, {227, 211, 173, 255});
            else drawing.gradient({12, 8, 40, 24}, {227, 211, 173, 255}, {227, 211, 173, 255});
            SDL_RenderFlush(renderer);
            SDL_LockSurface(surface);
            int missing = 0;
            int expected = 0;
            for (int y = 0; y < surface->h; ++y) {
                for (int x = 0; x < surface->w; ++x) {
                    const double px = (x + 0.5) / scale;
                    const double py = (y + 0.5) / scale;
                    // A strictly interior rectangle is guaranteed opaque for
                    // both shapes, independently of corner raster policy.
                    if (px < 18 || px >= 46 || py < 14 || py >= 26) continue;
                    ++expected;
                    const auto* p = static_cast<const std::uint8_t*>(surface->pixels) +
                        static_cast<std::size_t>(y) * static_cast<std::size_t>(surface->pitch) +
                        static_cast<std::size_t>(x) * 4;
                    if (p[0] != 227 || p[1] != 211 || p[2] != 173) ++missing;
                }
            }
            SDL_UnlockSurface(surface);
            std::cout << (rounded ? "rounded" : "gradient") << " scale=" << scale <<
                " expected_opaque_interior=" << expected << " missing=" << missing << '\n';
            failures += missing != 0;
        }
    }
    SDL_DestroyRenderer(renderer);
    SDL_FreeSurface(surface);
    SDL_Quit();
    return failures == 0 ? 0 : 1;
}
