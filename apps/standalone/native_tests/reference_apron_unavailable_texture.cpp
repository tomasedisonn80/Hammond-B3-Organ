#include <SDL.h>

// Test-only link seam: only the separately compiled fault Drawing object maps
// SDL_CreateTexture to this function. The unchanged raster fixture then tests
// the genuine procedural fallback without a production flag or alternate paint.
extern "C" SDL_Texture* SDLCALL hammond_test_create_texture(
    SDL_Renderer* renderer, Uint32 format, int access, int width, int height) {
    if (format == SDL_PIXELFORMAT_RGBA32 && width == 1640 && height == 54) {
        SDL_SetError("Injected optional apron texture unavailability");
        return nullptr;
    }
    return SDL_CreateTexture(renderer, format, access, width, height);
}
