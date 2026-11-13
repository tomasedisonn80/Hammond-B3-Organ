#include "Drawing.h"
#include "FontData.h"

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <vector>

namespace hammond::standalone {
namespace {

void color(SDL_Renderer* renderer, UiColor value) noexcept {
    SDL_SetRenderDrawColor(renderer, value.red, value.green, value.blue, value.alpha);
}

[[nodiscard]] SDL_Texture* make_font(SDL_Renderer* renderer,
                                     const font_data::Atlas& atlas,
                                     std::string& error) {
    const auto width = static_cast<std::size_t>(atlas.width);
    const auto height = static_cast<std::size_t>(atlas.height);
    if (width == 0 || height == 0 || width > 8192 || height > 8192) {
        error = "Invalid embedded font dimensions";
        return nullptr;
    }
    std::vector<std::uint8_t> alpha(width * height);
    if (!font_data::decode_alpha(atlas, alpha)) {
        error = "Invalid embedded font data";
        return nullptr;
    }
    std::vector<std::uint8_t> rgba(width * height * 4);
    for (std::size_t pixel = 0; pixel < alpha.size(); ++pixel) {
        rgba[pixel * 4] = 255;
        rgba[pixel * 4 + 1] = 255;
        rgba[pixel * 4 + 2] = 255;
        rgba[pixel * 4 + 3] = alpha[pixel];
    }
    auto* texture = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_RGBA32,
        SDL_TEXTUREACCESS_STATIC, static_cast<int>(width), static_cast<int>(height));
    if (texture == nullptr) {
        error = SDL_GetError();
        return nullptr;
    }
    if (SDL_UpdateTexture(texture, nullptr, rgba.data(), static_cast<int>(width * 4)) != 0 ||
        SDL_SetTextureBlendMode(texture, SDL_BLENDMODE_BLEND) != 0 ||
        SDL_SetTextureScaleMode(texture, SDL_ScaleModeLinear) != 0) {
        error = SDL_GetError();
        SDL_DestroyTexture(texture);
        return nullptr;
    }
    return texture;
}

} // namespace

Drawing::~Drawing() {
    SDL_DestroyTexture(sans_);
    SDL_DestroyTexture(serif_);
}

bool Drawing::initialize(std::string& error) {
    if (renderer_ == nullptr || sans_ != nullptr || serif_ != nullptr) {
        error = "Drawing requires one fresh renderer";
        return false;
    }
    sans_ = make_font(renderer_, font_data::kSans, error);
    if (sans_ == nullptr) return false;
    serif_ = make_font(renderer_, font_data::kSerif, error);
    if (serif_ == nullptr) {
        SDL_DestroyTexture(sans_);
        sans_ = nullptr;
        return false;
    }
    if (SDL_SetRenderDrawBlendMode(renderer_, SDL_BLENDMODE_BLEND) != 0) {
        error = SDL_GetError();
        SDL_DestroyTexture(sans_);
        SDL_DestroyTexture(serif_);
        sans_ = nullptr;
        serif_ = nullptr;
        return false;
    }
    error.clear();
    return true;
}

void Drawing::clear(UiColor value) const noexcept {
    color(renderer_, value);
    SDL_RenderClear(renderer_);
}

void Drawing::rect(UiRect bounds, UiColor value) const noexcept {
    if (!(bounds.width > 0.0F && bounds.height > 0.0F)) return;
    const SDL_FRect target{bounds.x, bounds.y, bounds.width, bounds.height};
    color(renderer_, value);
    SDL_RenderFillRectF(renderer_, &target);
}

void Drawing::rounded(UiRect bounds, float radius, UiColor value) const noexcept {
    if (!(bounds.width > 0.0F && bounds.height > 0.0F)) return;
    radius = std::clamp(radius, 0.0F, std::min(bounds.width, bounds.height) / 2.0F);
    if (radius < 1.0F) {
        rect(bounds, value);
        return;
    }
    color(renderer_, value);
    const auto rows = static_cast<int>(std::ceil(bounds.height));
    for (int row = 0; row < rows; ++row) {
        const float y = static_cast<float>(row) + 0.5F;
        const float edge = std::min(y, bounds.height - y);
        float inset = 0.0F;
        if (edge < radius) {
            const float distance = radius - edge;
            inset = radius - std::sqrt(std::max(0.0F, radius * radius - distance * distance));
        }
        const SDL_FRect strip{bounds.x + inset, bounds.y + static_cast<float>(row),
                             bounds.width - 2.0F * inset, 1.0F};
        SDL_RenderFillRectF(renderer_, &strip);
    }
}

void Drawing::outline(UiRect bounds, UiColor value, float thickness) const noexcept {
    thickness = std::max(0.0F, std::min(thickness, std::min(bounds.width, bounds.height) / 2.0F));
    rect({bounds.x, bounds.y, bounds.width, thickness}, value);
    rect({bounds.x, bounds.y + bounds.height - thickness, bounds.width, thickness}, value);
    rect({bounds.x, bounds.y, thickness, bounds.height}, value);
    rect({bounds.x + bounds.width - thickness, bounds.y, thickness, bounds.height}, value);
}

void Drawing::gradient(UiRect bounds, UiColor top, UiColor bottom) const noexcept {
    const auto rows = static_cast<int>(std::ceil(bounds.height));
    if (rows <= 0) return;
    for (int row = 0; row < rows; ++row) {
        const float fraction = rows == 1 ? 0.0F : static_cast<float>(row) / static_cast<float>(rows - 1);
        const auto mix = [fraction](std::uint8_t first, std::uint8_t last) {
            const float value = static_cast<float>(first) +
                (static_cast<float>(last) - static_cast<float>(first)) * fraction;
            return static_cast<std::uint8_t>(std::clamp(std::round(value), 0.0F, 255.0F));
        };
        rect({bounds.x, bounds.y + static_cast<float>(row), bounds.width, 1.0F},
             {mix(top.red, bottom.red), mix(top.green, bottom.green),
              mix(top.blue, bottom.blue), mix(top.alpha, bottom.alpha)});
    }
}

void Drawing::line(float x1, float y1, float x2, float y2, UiColor value) const noexcept {
    color(renderer_, value);
    SDL_RenderDrawLineF(renderer_, x1, y1, x2, y2);
}

void Drawing::shadow(UiRect bounds, float radius) const noexcept {
    for (int layer = 5; layer >= 1; --layer) {
        const float spread = static_cast<float>(layer);
        rounded({bounds.x - spread, bounds.y + 2.0F - spread,
                 bounds.width + spread * 2.0F, bounds.height + spread * 2.0F},
                radius + spread, {0, 0, 0, 16});
    }
}

float Drawing::text_width(std::string_view value, float size, TextFace face) const noexcept {
    const auto& atlas = face == TextFace::Sans ? font_data::kSans : font_data::kSerif;
    const float scale = size / static_cast<float>(atlas.pixel_height);
    float width = 0.0F;
    float maximum = 0.0F;
    for (const char character : value) {
        if (character == '\n') {
            maximum = std::max(maximum, width);
            width = 0.0F;
        } else {
            width += static_cast<float>(font_data::glyph(atlas,
                static_cast<unsigned char>(character)).advance_64) * scale / 64.0F;
        }
    }
    return std::max(maximum, width);
}

void Drawing::text(std::string_view value, float x, float top, float size,
                   UiColor value_color, TextFace face) const noexcept {
    const auto& atlas = face == TextFace::Sans ? font_data::kSans : font_data::kSerif;
    auto* texture = face == TextFace::Sans ? sans_ : serif_;
    if (texture == nullptr || !(size > 0.0F)) return;
    SDL_SetTextureColorMod(texture, value_color.red, value_color.green, value_color.blue);
    SDL_SetTextureAlphaMod(texture, value_color.alpha);
    const float scale = size / static_cast<float>(atlas.pixel_height);
    const float origin = x;
    float baseline = top + static_cast<float>(atlas.ascent) * scale;
    for (const char character : value) {
        if (character == '\n') {
            x = origin;
            baseline += size * 1.3F;
            continue;
        }
        const auto& glyph = font_data::glyph(atlas, static_cast<unsigned char>(character));
        if (glyph.width != 0 && glyph.height != 0) {
            const SDL_Rect source{static_cast<int>(glyph.x), static_cast<int>(glyph.y),
                                  static_cast<int>(glyph.width), static_cast<int>(glyph.height)};
            const SDL_FRect target{x + static_cast<float>(glyph.bearing_x) * scale,
                                  baseline + static_cast<float>(glyph.bearing_y) * scale,
                                  static_cast<float>(glyph.width) * scale,
                                  static_cast<float>(glyph.height) * scale};
            SDL_RenderCopyF(renderer_, texture, &source, &target);
        }
        x += static_cast<float>(glyph.advance_64) * scale / 64.0F;
    }
}

bool Drawing::save_bmp(const std::string& path, std::string& error) const {
    int width = 0;
    int height = 0;
    if (SDL_GetRendererOutputSize(renderer_, &width, &height) != 0) {
        error = SDL_GetError();
        return false;
    }
    auto* surface = SDL_CreateRGBSurfaceWithFormat(0, width, height, 32, SDL_PIXELFORMAT_RGBA32);
    if (surface == nullptr) {
        error = SDL_GetError();
        return false;
    }
    const bool success = SDL_RenderReadPixels(renderer_, nullptr, surface->format->format,
        surface->pixels, surface->pitch) == 0 && SDL_SaveBMP(surface, path.c_str()) == 0;
    if (!success) error = SDL_GetError();
    else error.clear();
    SDL_FreeSurface(surface);
    return success;
}

} // namespace hammond::standalone
