// A31 pre-implementation experiment. No application/production sources linked.
#include <SDL.h>
#include <array>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <iterator>
#include <memory>
#include <stdexcept>
#include <vector>

using Pixel = std::array<std::uint8_t, 4>;
void check(bool ok) { if (!ok) throw std::runtime_error(SDL_GetError()); }
struct Frame { int w{}, h{}; SDL_Rect clip{}; std::vector<Pixel> pixels; };
Frame render(const std::vector<char>& raw, float scale, int edge, bool clipped) {
    const int origin_x = scale == 1.5F ? 0 : 13;
    const int origin_y = scale == 1.5F ? 0 : 17;
    const int width = static_cast<int>(std::ceil(1672.0F * scale));
    const int height = static_cast<int>(std::ceil(941.0F * scale));
    Frame result{width + 2 * origin_x, height + 2 * origin_y, {}, {}};
    std::unique_ptr<SDL_Surface, decltype(&SDL_FreeSurface)> surface(
        SDL_CreateRGBSurfaceWithFormat(0, result.w, result.h, 32, SDL_PIXELFORMAT_RGBA32), SDL_FreeSurface);
    std::unique_ptr<SDL_Renderer, decltype(&SDL_DestroyRenderer)> renderer(
        surface ? SDL_CreateSoftwareRenderer(surface.get()) : nullptr, SDL_DestroyRenderer);
    check(surface && renderer);
    check(SDL_SetRenderDrawColor(renderer.get(), 7, 11, 13, 255) == 0);
    check(SDL_RenderClear(renderer.get()) == 0);
    std::unique_ptr<SDL_Texture, decltype(&SDL_DestroyTexture)> texture(
        SDL_CreateTexture(renderer.get(), SDL_PIXELFORMAT_RGB24, SDL_TEXTUREACCESS_STATIC, 1074, 18), SDL_DestroyTexture);
    check(texture && SDL_UpdateTexture(texture.get(), nullptr, raw.data(), 3222) == 0 &&
          SDL_SetTextureBlendMode(texture.get(), SDL_BLENDMODE_NONE) == 0 &&
          SDL_SetTextureScaleMode(texture.get(), SDL_ScaleModeLinear) == 0);
    SDL_Rect viewport{origin_x, origin_y, width, height};
    check(SDL_RenderSetViewport(renderer.get(), &viewport) == 0);
    const int x = static_cast<int>(48.0F * scale), y = static_cast<int>(510.0F * scale);
    const int w = static_cast<int>(1074.0F * scale), h = static_cast<int>(18.0F * scale);
    std::array<SDL_Rect, 4> physical{{{x-2,y-2,4,h+4},{x+w-2,y-2,4,h+4},
                                    {x-2,y-2,w+4,4},{x-2,y+h-2,w+4,4}}};
    std::array<SDL_Rect, 4> logical{{{46,508,4,22},{1120,508,4,22},
                                   {46,508,1078,4},{46,526,1078,4}}};
    if (scale != 1.5F && clipped)
        check(SDL_RenderSetClipRect(renderer.get(), &physical[static_cast<std::size_t>(edge)]) == 0);
    check(SDL_RenderSetScale(renderer.get(), scale, scale) == 0);
    if (scale == 1.5F && clipped)
        check(SDL_RenderSetClipRect(renderer.get(), &logical[static_cast<std::size_t>(edge)]) == 0);
    check(SDL_RenderSetScale(renderer.get(), 1, 1) == 0);
    SDL_RenderGetClipRect(renderer.get(), &result.clip);
    result.clip.x += origin_x;
    result.clip.y += origin_y;
    check(SDL_RenderSetScale(renderer.get(), scale, scale) == 0);
    SDL_FRect dst{48,510,1074,18};
    check(SDL_RenderCopyF(renderer.get(), texture.get(), nullptr, &dst) == 0);
    SDL_RenderPresent(renderer.get());
    result.pixels.resize(static_cast<std::size_t>(result.w) * static_cast<std::size_t>(result.h));
    check(SDL_RenderReadPixels(renderer.get(), nullptr, SDL_PIXELFORMAT_RGBA32, result.pixels.data(), result.w * 4) == 0);
    return result;
}
int main(int argc, char** argv) {
    try {
        if (argc != 2) throw std::runtime_error("usage: probe raw-crop.rgb");
        std::ifstream input(argv[1], std::ios::binary);
        std::vector<char> raw{std::istreambuf_iterator<char>(input), {}};
        if (raw.size() != 57996) throw std::runtime_error("invalid raw size");
        SDL_SetMainReady(); check(SDL_Init(0) == 0);
        std::cout << "{\"protocol\":\"A31-pinned-SDL-linear-copy-preflight-v1\",\"cases\":[";
        bool comma = false;
        for (int edge = 0; edge < 4; ++edge) for (float scale : {1.0F, 1.5F, 2.0F}) {
            const auto full = render(raw, scale, edge, false);
            const auto clip = render(raw, scale, edge, true);
            std::size_t interior = 0, different = 0, outside = 0;
            int first_x = -1, first_y = -1;
            for (int y = 0; y < clip.h; ++y) for (int x = 0; x < clip.w; ++x) {
                const auto index = static_cast<std::size_t>(y) * static_cast<std::size_t>(clip.w) + static_cast<std::size_t>(x);
                if (x >= clip.clip.x && x < clip.clip.x + clip.clip.w && y >= clip.clip.y && y < clip.clip.y + clip.clip.h) {
                    ++interior;
                    if (clip.pixels[index] != full.pixels[index]) {
                        ++different;
                        if (first_x < 0) { first_x = x; first_y = y; }
                    }
                } else if (clip.pixels[index] != Pixel{7,11,13,255}) ++outside;
            }
            if (comma) std::cout << ',';
            comma = true;
            std::cout << "{\"id\":" << 9 + edge * 3 + static_cast<int>(scale * 2 - 2)
                      << ",\"scale\":" << scale << ",\"edge\":" << edge
                      << ",\"clip\":[" << clip.clip.x << ',' << clip.clip.y << ',' << clip.clip.w << ',' << clip.clip.h
                      << "],\"interior_pixels\":" << interior << ",\"interior_differences\":" << different
                      << ",\"outside_changes\":" << outside << ",\"first_difference\":[" << first_x << ',' << first_y << "]}";
        }
        std::cout << "]}\n";
        SDL_Quit();
    } catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
