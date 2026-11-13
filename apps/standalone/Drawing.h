#pragma once

#include "UiModel.h"

#include <SDL.h>

#include <string>
#include <string_view>

namespace hammond::standalone {

enum class TextFace { Sans, Serif };

// Main-thread SDL painting only. Glyph textures are prepared once and own no
// audio state. Labels remain dynamic text over separately painted geometry.
class Drawing {
public:
    explicit Drawing(SDL_Renderer* renderer) noexcept : renderer_(renderer) {}
    ~Drawing();
    Drawing(const Drawing&) = delete;
    Drawing& operator=(const Drawing&) = delete;

    [[nodiscard]] bool initialize(std::string& error);
    void clear(UiColor color) const noexcept;
    void rect(UiRect bounds, UiColor color) const noexcept;
    void rounded(UiRect bounds, float radius, UiColor color) const noexcept;
    void outline(UiRect bounds, UiColor color, float thickness = 1.0F) const noexcept;
    void gradient(UiRect bounds, UiColor top, UiColor bottom) const noexcept;
    void line(float x1, float y1, float x2, float y2, UiColor color) const noexcept;
    void shadow(UiRect bounds, float radius = 7.0F) const noexcept;
    void text(std::string_view value, float x, float top, float size,
              UiColor color, TextFace face = TextFace::Sans) const noexcept;
    [[nodiscard]] float text_width(std::string_view value, float size,
                                   TextFace face = TextFace::Sans) const noexcept;
    [[nodiscard]] bool save_bmp(const std::string& path, std::string& error) const;
    [[nodiscard]] SDL_Renderer* renderer() const noexcept { return renderer_; }

private:
    SDL_Renderer* renderer_{};
    SDL_Texture* sans_{};
    SDL_Texture* serif_{};
};

} // namespace hammond::standalone
