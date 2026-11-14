#include "Drawing.h"
#include "FontData.h"
#include "ReferenceArtData.h"

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

[[nodiscard]] bool valid_surface(UiRect bounds) noexcept {
    return std::isfinite(bounds.x) && std::isfinite(bounds.y) &&
           std::isfinite(bounds.width) && std::isfinite(bounds.height) &&
           bounds.width > 0.0F && bounds.height > 0.0F;
}

// Rasterize once at each output-pixel center, including on SDL software.
// Its backend truncates fractional vertices and rectangle extents; integer
// spans avoid scaled strip gaps and preserve rounded/sloping silhouettes.
class PixelRaster {
public:
    explicit PixelRaster(SDL_Renderer* renderer) noexcept : renderer_(renderer) {
        if (renderer_ == nullptr) return;
        int width = 0;
        int height = 0;
        if (SDL_GetRendererOutputSize(renderer_, &width, &height) != 0 ||
            width <= 0 || height <= 0) return;
        SDL_RenderGetScale(renderer_, &scale_x_, &scale_y_);
        if (!std::isfinite(scale_x_) || !std::isfinite(scale_y_) ||
            scale_x_ <= 0.0F || scale_y_ <= 0.0F) return;
        // SDL stores viewport/clip coordinates in output pixels. Reading them
        // at scale one avoids losing their physical edges to logical rounding.
        if (SDL_RenderSetScale(renderer_, 1.0F, 1.0F) != 0) return;
        restore_scale_ = true;
        SDL_Rect viewport{};
        SDL_RenderGetViewport(renderer_, &viewport);
        if (viewport.w <= 0 || viewport.h <= 0) return;
        std::int64_t left = std::max<std::int64_t>(0, -static_cast<std::int64_t>(viewport.x));
        std::int64_t top = std::max<std::int64_t>(0, -static_cast<std::int64_t>(viewport.y));
        std::int64_t right = std::min<std::int64_t>(viewport.w,
            static_cast<std::int64_t>(width) - viewport.x);
        std::int64_t bottom = std::min<std::int64_t>(viewport.h,
            static_cast<std::int64_t>(height) - viewport.y);
        if (SDL_RenderIsClipEnabled(renderer_) == SDL_TRUE) {
            SDL_Rect clip{};
            SDL_RenderGetClipRect(renderer_, &clip);
            if (clip.w <= 0 || clip.h <= 0) return;
            left = std::max(left, static_cast<std::int64_t>(clip.x));
            top = std::max(top, static_cast<std::int64_t>(clip.y));
            right = std::min(right, static_cast<std::int64_t>(clip.x) + clip.w);
            bottom = std::min(bottom, static_cast<std::int64_t>(clip.y) + clip.h);
        }
        if (left >= right || top >= bottom) return;
        // The nonempty intersection lies in [0, viewport.w/h], hence in int.
        left_ = static_cast<int>(left);
        right_ = static_cast<int>(right);
        top_ = static_cast<int>(top);
        bottom_ = static_cast<int>(bottom);
    }

    ~PixelRaster() {
        if (restore_scale_) SDL_RenderSetScale(renderer_, scale_x_, scale_y_);
    }
    PixelRaster(const PixelRaster&) = delete;
    PixelRaster& operator=(const PixelRaster&) = delete;

    [[nodiscard]] bool visible() const noexcept { return left_ < right_ && top_ < bottom_; }
    [[nodiscard]] int x_boundary(double logical_x) const noexcept {
        return pixel_boundary(logical_x * scale_x_, left_, right_);
    }
    [[nodiscard]] int y_boundary(double logical_y) const noexcept {
        return pixel_boundary(logical_y * scale_y_, top_, bottom_);
    }
    [[nodiscard]] double logical_y(int row) const noexcept {
        return (static_cast<double>(row) + 0.5) / scale_y_;
    }
    void span(int first, int end, int row) const noexcept {
        if (first >= end) return;
        // SDL software's blended closed line omits a coincident endpoint.
        // A one-pixel span is a point, including for fully opaque blend colors.
        if (end - first == 1) SDL_RenderDrawPoint(renderer_, first, row);
        else SDL_RenderDrawLine(renderer_, first, row, end - 1, row);
    }

private:
    [[nodiscard]] static int pixel_boundary(double edge, int minimum, int maximum) noexcept {
        // Include centers on the left/top edge, exclude centers on right/bottom.
        // Clip the double before integer conversion, even for FLT_MAX vertices.
        const double boundary = std::ceil(edge - 0.5);
        if (boundary <= minimum) return minimum;
        if (boundary >= maximum) return maximum;
        return static_cast<int>(boundary);
    }

    SDL_Renderer* renderer_{};
    float scale_x_{1.0F};
    float scale_y_{1.0F};
    bool restore_scale_{};
    int left_{};
    int right_{};
    int top_{};
    int bottom_{};
};

template <typename Paint>
void quad_rows(const UiQuad& shape, const PixelRaster& raster, Paint paint) noexcept {
    const auto& top_left = shape.points[0];
    const auto& top_right = shape.points[1];
    const auto& bottom_right = shape.points[2];
    const auto& bottom_left = shape.points[3];
    const double height = static_cast<double>(bottom_left.y) - top_left.y;
    const int first_row = raster.y_boundary(top_left.y);
    const int end_row = raster.y_boundary(bottom_left.y);
    for (int row = first_row; row < end_row; ++row) {
        const double y = raster.logical_y(row);
        const double fraction = std::clamp((y - top_left.y) / height, 0.0, 1.0);
        const double left = top_left.x +
            (static_cast<double>(bottom_left.x) - top_left.x) * fraction;
        const double right = top_right.x +
            (static_cast<double>(bottom_right.x) - top_right.x) * fraction;
        const int first = raster.x_boundary(left);
        const int end = raster.x_boundary(right);
        if (first < end) paint(row, first, end, y, left, right, fraction);
    }
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

[[nodiscard]] SDL_Texture* make_art(SDL_Renderer* renderer,
                                    const reference_art::RgbImage& art) noexcept {
    if (art.width <= 0 || art.height <= 0 || art.width > 8192 || art.height > 8192 ||
        art.pitch != art.width * 3 || art.pixels == nullptr ||
        art.byte_count != static_cast<std::size_t>(art.pitch) * static_cast<std::size_t>(art.height)) {
        return nullptr;
    }
    auto* texture = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_RGB24,
        SDL_TEXTUREACCESS_STATIC, art.width, art.height);
    if (texture == nullptr) return nullptr;
    if (SDL_UpdateTexture(texture, nullptr, art.pixels, art.pitch) != 0 ||
        SDL_SetTextureBlendMode(texture, SDL_BLENDMODE_NONE) != 0 ||
        SDL_SetTextureScaleMode(texture, SDL_ScaleModeLinear) != 0) {
        SDL_DestroyTexture(texture);
        return nullptr;
    }
    return texture;
}

} // namespace

Drawing::~Drawing() {
    SDL_DestroyTexture(sans_);
    SDL_DestroyTexture(serif_);
    SDL_DestroyTexture(cabinet_);
    SDL_DestroyTexture(left_wood_);
    SDL_DestroyTexture(right_wood_);
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
    // Decoration is optional. Failed preparation cannot make the instrument
    // unusable; all controls and their procedural surface remain independent.
    cabinet_ = make_art(renderer_, hammond::standalone::reference_art::kCabinet);
    left_wood_ = make_art(renderer_, hammond::standalone::reference_art::kLeftWoodCheek);
    right_wood_ = make_art(renderer_, hammond::standalone::reference_art::kRightWoodCheek);
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
    if (!valid_surface(bounds) || !std::isfinite(radius)) return;
    const double corner_radius = std::clamp(static_cast<double>(radius), 0.0,
        std::min(static_cast<double>(bounds.width), static_cast<double>(bounds.height)) / 2.0);
    const PixelRaster raster(renderer_);
    if (!raster.visible()) return;
    const double right = static_cast<double>(bounds.x) + bounds.width;
    const double bottom = static_cast<double>(bounds.y) + bounds.height;
    const int first_row = raster.y_boundary(bounds.y);
    const int end_row = raster.y_boundary(bottom);
    color(renderer_, value);
    for (int row = first_row; row < end_row; ++row) {
        const double y = raster.logical_y(row);
        const double edge = std::min(y - bounds.y, bottom - y);
        double inset = 0.0;
        if (edge < corner_radius) {
            const double distance = corner_radius - edge;
            inset = corner_radius - std::sqrt(std::max(0.0,
                corner_radius * corner_radius - distance * distance));
        }
        raster.span(raster.x_boundary(bounds.x + inset),
                    raster.x_boundary(right - inset), row);
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
    if (!valid_surface(bounds)) return;
    const PixelRaster raster(renderer_);
    if (!raster.visible()) return;
    const int first = raster.x_boundary(bounds.x);
    const int end = raster.x_boundary(static_cast<double>(bounds.x) + bounds.width);
    if (first >= end) return;
    const int first_row = raster.y_boundary(bounds.y);
    const int end_row = raster.y_boundary(static_cast<double>(bounds.y) + bounds.height);
    for (int row = first_row; row < end_row; ++row) {
        // Anchor stops at the first/last logical pixel centers. This preserves
        // the old integer-aligned scale-one palette while sampling every output
        // row continuously at fractional scales, independently of clipping.
        const float fraction = bounds.height <= 1.0F ? 0.0F : static_cast<float>(std::clamp(
            (raster.logical_y(row) - bounds.y - 0.5) / (bounds.height - 1.0), 0.0, 1.0));
        const auto mix = [fraction](std::uint8_t first_channel, std::uint8_t last_channel) {
            const float value = static_cast<float>(first_channel) +
                (static_cast<float>(last_channel) - static_cast<float>(first_channel)) * fraction;
            return static_cast<std::uint8_t>(std::clamp(std::round(value), 0.0F, 255.0F));
        };
        color(renderer_, {mix(top.red, bottom.red), mix(top.green, bottom.green),
                          mix(top.blue, bottom.blue), mix(top.alpha, bottom.alpha)});
        raster.span(first, end, row);
    }
}

void Drawing::quad(const UiQuad& shape, UiColor top, UiColor bottom) const noexcept {
    // A valid horizontal-edge quad always contains its top-left vertex. Reuse
    // the shared validator so drawing and hit testing admit identical shapes.
    if (!shape.contains(shape.points[0])) return;
    const PixelRaster raster(renderer_);
    if (!raster.visible()) return;
    quad_rows(shape, raster, [this, &raster, top, bottom](int row, int first, int end,
              double, double, double, double fraction) noexcept {
        const auto mix = [fraction](std::uint8_t a, std::uint8_t b) noexcept {
            const double value = a + (static_cast<double>(b) - a) * fraction;
            return static_cast<std::uint8_t>(std::clamp(std::round(value), 0.0, 255.0));
        };
        color(renderer_, {mix(top.red, bottom.red), mix(top.green, bottom.green),
                          mix(top.blue, bottom.blue), mix(top.alpha, bottom.alpha)});
        raster.span(first, end, row);
    });
}

void Drawing::quad_outline(const UiQuad& shape, UiColor value, float thickness) const noexcept {
    if (!shape.contains(shape.points[0]) || !std::isfinite(thickness) || thickness <= 0.0F) return;
    const double height = static_cast<double>(shape.points[3].y) - shape.points[0].y;
    const double top_width = static_cast<double>(shape.points[1].x) - shape.points[0].x;
    const double bottom_width = static_cast<double>(shape.points[2].x) - shape.points[3].x;
    const double inset = std::min({static_cast<double>(thickness), height / 2.0,
                                  top_width / 2.0, bottom_width / 2.0});
    const double inner_top = shape.points[0].y + inset;
    const double inner_bottom = shape.points[3].y - inset;
    const PixelRaster raster(renderer_);
    if (!raster.visible()) return;
    color(renderer_, value);
    quad_rows(shape, raster, [&raster, inset, inner_top, inner_bottom](int row, int first,
              int end, double y, double left, double right, double) noexcept {
        if (y < inner_top || y >= inner_bottom) {
            raster.span(first, end, row);
            return;
        }
        // Evaluate the original sloping sides at this y before insetting them.
        // The two side bands and end bands never overlap, even with alpha.
        const int inner_first = raster.x_boundary(left + inset);
        const int inner_end = raster.x_boundary(right - inset);
        if (inner_first >= inner_end) {
            raster.span(first, end, row);
        } else {
            raster.span(first, inner_first, row);
            raster.span(inner_end, end, row);
        }
    });
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

bool Drawing::reference_art(ReferenceArt art, UiRect bounds) const noexcept {
    SDL_Texture* texture = nullptr;
    switch (art) {
    case ReferenceArt::Cabinet: texture = cabinet_; break;
    case ReferenceArt::LeftWoodCheek: texture = left_wood_; break;
    case ReferenceArt::RightWoodCheek: texture = right_wood_; break;
    }
    if (texture == nullptr || !(bounds.width > 0.0F && bounds.height > 0.0F)) return false;
    const SDL_FRect target{bounds.x, bounds.y, bounds.width, bounds.height};
    return SDL_RenderCopyF(renderer_, texture, nullptr, &target) == 0;
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
            // The atlas generator verifies two transparent pixels around every
            // ink rectangle, including at its edges. Include that gutter in a
            // subpixel dimension so l/i strokes and hyphens survive the SDL
            // software renderer's integer destination extent. Keep the existing
            // sampling in other dimensions and offset the bearing identically.
            const int padding_x = static_cast<float>(glyph.width) * scale < 1.0F ? 2 : 0;
            const int padding_y = static_cast<float>(glyph.height) * scale < 1.0F ? 2 : 0;
            const SDL_Rect source{static_cast<int>(glyph.x) - padding_x,
                                  static_cast<int>(glyph.y) - padding_y,
                                  static_cast<int>(glyph.width) + 2 * padding_x,
                                  static_cast<int>(glyph.height) + 2 * padding_y};
            const SDL_FRect target{x + static_cast<float>(glyph.bearing_x - padding_x) * scale,
                                  baseline + static_cast<float>(glyph.bearing_y - padding_y) * scale,
                                  static_cast<float>(source.w) * scale,
                                  static_cast<float>(source.h) * scale};
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
