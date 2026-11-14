#include "InstrumentView.h"
#include "InspectionModel.h"
#include "FontData.h"

#include <SDL.h>

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <filesystem>
#include <iostream>
#include <limits>
#include <memory>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace {
using namespace hammond;
using namespace hammond::standalone;
using Pixel = std::array<std::uint8_t, 4>;

struct Counts {
    std::size_t failures{}, frames{}, states{}, clips{}, focus{}, service_values{}, service_lines{};
} counts;

void require(bool condition, std::string_view detail) {
    if (!condition) throw std::runtime_error(std::string(detail) + ": " + SDL_GetError());
}

void check(bool condition, std::string_view detail) {
    if (!condition) {
        ++counts.failures;
        std::cerr << "FAIL: " << detail << '\n';
    }
}

bool equal(SDL_Rect a, SDL_Rect b) {
    return a.x == b.x && a.y == b.y && a.w == b.w && a.h == b.h;
}

struct State {
    float x{}, y{};
    SDL_Rect viewport{}, clip{}, logical_viewport{}, logical_clip{};
    bool clipped{};
    SDL_BlendMode blend{};
};

State state(SDL_Renderer* renderer) {
    State result;
    SDL_RenderGetScale(renderer, &result.x, &result.y);
    SDL_RenderGetViewport(renderer, &result.logical_viewport);
    SDL_RenderGetClipRect(renderer, &result.logical_clip);
    // Retain physical edges: logical reads round odd physical edges at 1.5x.
    require(SDL_RenderSetScale(renderer, 1.0F, 1.0F) == 0, "read physical renderer state");
    SDL_RenderGetViewport(renderer, &result.viewport);
    SDL_RenderGetClipRect(renderer, &result.clip);
    result.clipped = SDL_RenderIsClipEnabled(renderer) == SDL_TRUE;
    require(SDL_GetRenderDrawBlendMode(renderer, &result.blend) == 0, "read renderer blend mode");
    require(SDL_RenderSetScale(renderer, result.x, result.y) == 0, "restore scale after state read");
    return result;
}

void check_state(SDL_Renderer* renderer, const State& expected, std::string_view detail) {
    const auto actual = state(renderer);
    ++counts.states;
    check(actual.x == expected.x && actual.y == expected.y &&
        equal(actual.viewport, expected.viewport) && equal(actual.clip, expected.clip) &&
        equal(actual.logical_viewport, expected.logical_viewport) &&
        equal(actual.logical_clip, expected.logical_clip) &&
        actual.clipped == expected.clipped && actual.blend == expected.blend,
        std::string(detail) + " restores scale, physical/logical viewport/clip and blend");
    if (!equal(actual.clip, expected.clip)) {
        std::cerr << "clip before=" << expected.clip.x << ',' << expected.clip.y << ',' <<
            expected.clip.w << ',' << expected.clip.h << " after=" << actual.clip.x << ',' <<
            actual.clip.y << ',' << actual.clip.w << ',' << actual.clip.h << '\n';
    }
}

struct Frame {
    int width{}, height{};
    std::vector<Pixel> pixels;
};

std::size_t offset(int x, int y, int width) {
    return static_cast<std::size_t>(y) * static_cast<std::size_t>(width) + static_cast<std::size_t>(x);
}

class Target {
public:
    Target(int width, int height)
        : surface_(SDL_CreateRGBSurfaceWithFormat(0, width, height, 32, SDL_PIXELFORMAT_RGBA32), SDL_FreeSurface),
          renderer_(surface_ ? SDL_CreateSoftwareRenderer(surface_.get()) : nullptr, SDL_DestroyRenderer),
          drawing_(renderer_.get()) {
        require(surface_ != nullptr && renderer_ != nullptr, "create bounded software renderer target");
        require(width <= 1920 && height <= 1400, "retain bounded raster allocation");
        std::string error;
        require(drawing_.initialize(error), "initialize actual Drawing fonts/art: " + error);
    }

    Drawing& drawing() { return drawing_; }
    SDL_Renderer* renderer() { return renderer_.get(); }
    int width() const { return surface_->w; }
    int height() const { return surface_->h; }

    void configure(float scale, SDL_Rect viewport, const SDL_Rect* clip = nullptr) {
        require(SDL_RenderSetScale(renderer(), 1.0F, 1.0F) == 0, "configure physical renderer coordinates");
        require(SDL_RenderSetViewport(renderer(), &viewport) == 0, "set physical viewport");
        require(SDL_RenderSetClipRect(renderer(), clip) == 0, "set physical clip");
        require(SDL_RenderSetScale(renderer(), scale, scale) == 0, "set output scale");
    }

    Frame paint(const UiModel& model, const InspectionDocument& document, std::string_view detail) {
        const State before = state(renderer());
        InstrumentViewInfo info;
        info.inspection = &document;
        info.audio_running = true;
        info.sample_rate = 48000;
        info.buffer_frames = 512;
        info.audio_driver = "injected software-test driver";
        info.device_name = "injected copied state; no physical device";
        info.midi_backend = "not opened";
        paint_instrument(drawing_, model, info);
        check_state(renderer(), before, detail);
        require(SDL_RenderFlush(renderer()) == 0, "flush actual instrument paint");
        // SDL_RenderReadPixels(nullptr) observes a viewport, not the full target.
        // Direct surface reads keep all outside pixels in the clipping oracle.
        require(SDL_LockSurface(surface_.get()) == 0, "lock full software target");
        Frame frame{width(), height(), std::vector<Pixel>(
            static_cast<std::size_t>(width()) * static_cast<std::size_t>(height()))};
        static_assert(sizeof(Pixel) == 4);
        const auto* bytes = static_cast<const std::uint8_t*>(surface_->pixels);
        for (int y = 0; y < height(); ++y) {
            const auto* row = bytes + static_cast<std::size_t>(y) * static_cast<std::size_t>(surface_->pitch);
            for (int x = 0; x < width(); ++x) {
                const auto p = static_cast<std::size_t>(x) * 4;
                frame.pixels[offset(x, y, width())] = {row[p], row[p + 1], row[p + 2], row[p + 3]};
            }
        }
        SDL_UnlockSurface(surface_.get());
        ++counts.frames;
        return frame;
    }

    void save(const std::filesystem::path& path) {
        require(SDL_RenderFlush(renderer()) == 0 && SDL_SaveBMP(surface_.get(), path.string().c_str()) == 0,
            "save injected native renderer frame");
    }

private:
    std::unique_ptr<SDL_Surface, decltype(&SDL_FreeSurface)> surface_;
    std::unique_ptr<SDL_Renderer, decltype(&SDL_DestroyRenderer)> renderer_;
    Drawing drawing_;
};

UiModel model_at(int width, int height, UiWorkspace workspace, UiPresentation presentation) {
    UiModel model;
    require(model.resize(static_cast<float>(width), static_cast<float>(height)), "set logical model size");
    require(model.set_workspace(workspace) && model.set_presentation(presentation), "set presentation");
    SessionSnapshot snapshot;
    snapshot.controls = model.view().controls;
    snapshot.prepared = true;
    snapshot.running = true;
    snapshot.publication_revision = 46;
    snapshot.frame_clock = 123456;
    snapshot.held_keys[0][24] = true;
    snapshot.held_keys[0][28] = true;
    snapshot.held_keys[1][31] = true;
    snapshot.held_pedals[3] = true;
    for (std::size_t manual = 0; manual < 2; ++manual)
        for (std::size_t bank = 0; bank < 2; ++bank)
            for (std::size_t index = 0; index < 9; ++index)
                snapshot.controls.drawbars[manual][bank][index] =
                    static_cast<std::uint8_t>((manual * 2 + bank + index) % 9);
    snapshot.controls.expression = 0.456789;
    snapshot.controls.percussion.enabled = true;
    model.observe(snapshot);
    return model;
}

InspectionDocument document_for(const UiModel& model) {
    // Deliberately injected display fixture, never a Session prepare or a claim
    // that this partial profile can produce audio.
    RuntimeProfile profile;
    std::copy(kNominalProfileId.begin(), kNominalProfileId.end(), profile.profile_id.begin());
    std::fill_n(profile.authoring_sha256.begin(), kSha256HexLength, 'a');
    profile.output_gain = 0.0123456;
    profile.sources[45].frequency_hz = 442.125;
    return make_inspection_document(profile, model.view(), {true, true});
}

std::string name(int width, int height, float scale, UiWorkspace workspace, UiPresentation presentation) {
    constexpr std::array<std::string_view, 3> workspaces{"Play", "Rotary", "Service"};
    return std::to_string(width) + "x" + std::to_string(height) + " @" + std::to_string(scale) + " " +
        std::string(workspaces[static_cast<std::size_t>(workspace)]) +
        (presentation == UiPresentation::Flat ? " Flat" : " Dimensional");
}

void clipped_pixels(const Frame& frame, const State& transform, UiPresentation presentation,
                    std::string_view detail) {
    const Pixel background = presentation == UiPresentation::Flat ? Pixel{18, 21, 20, 255} :
        Pixel{kUiWalnut.red, kUiWalnut.green, kUiWalnut.blue, kUiWalnut.alpha};
    std::size_t leaked = 0;
    std::size_t ink = 0;
    for (int y = 0; y < frame.height; ++y) {
        for (int x = 0; x < frame.width; ++x) {
            const int local_x = x - transform.viewport.x;
            const int local_y = y - transform.viewport.y;
            const bool viewport = local_x >= 0 && local_y >= 0 &&
                local_x < transform.viewport.w && local_y < transform.viewport.h;
            const bool clip = !transform.clipped || (local_x >= transform.clip.x && local_y >= transform.clip.y &&
                local_x < transform.clip.x + transform.clip.w && local_y < transform.clip.y + transform.clip.h);
            if (frame.pixels[offset(x, y, frame.width)] == background) continue;
            if (viewport && clip) ++ink;
            else ++leaked;
        }
    }
    ++counts.clips;
    // paint_instrument intentionally clears the complete target first. SDL's
    // clear is not clipped; only the declared uniform clear color is exempt.
    check(ink > 1000 && leaked == 0, std::string(detail) +
        " has visible mixed drawing and no ink outside viewport/clip; leaked=" + std::to_string(leaked));
}

void full_matrix() {
    constexpr std::array<std::array<int, 2>, 2> sizes{{{960, 700}, {1280, 900}}};
    for (const auto size : sizes) {
        for (const float scale : {1.0F, 1.5F, 2.0F}) {
            const int physical_width = static_cast<int>(static_cast<float>(size[0]) * scale);
            const int physical_height = static_cast<int>(static_cast<float>(size[1]) * scale);
            Target target(std::min(1920, physical_width), std::min(1400, physical_height));
            // Default 2x uses four overlapping tiles; the union covers every
            // output pixel without allocating a 2560x1800 surface or capture.
            const std::array<int, 2> offsets_x{0, physical_width - target.width()};
            const std::array<int, 2> offsets_y{0, physical_height - target.height()};
            const std::size_t nx = offsets_x[1] == 0 ? 1 : 2;
            const std::size_t ny = offsets_y[1] == 0 ? 1 : 2;
            for (std::size_t ix = 0; ix < nx; ++ix) {
                for (std::size_t iy = 0; iy < ny; ++iy) {
                    target.configure(scale, {-offsets_x[ix], -offsets_y[iy], physical_width, physical_height});
                    for (const auto workspace : {UiWorkspace::Play, UiWorkspace::Rotary, UiWorkspace::Service}) {
                        for (const auto presentation : {UiPresentation::Dimensional, UiPresentation::Flat}) {
                            const auto model = model_at(size[0], size[1], workspace, presentation);
                            const auto document = document_for(model);
                            const auto detail = name(size[0], size[1], scale, workspace, presentation);
                            const auto expected = state(target.renderer());
                            const auto frame = target.paint(model, document, detail);
                            clipped_pixels(frame, expected, presentation, detail);
                        }
                    }
                }
            }
        }
    }
}

void viewport_matrix() {
    for (const float scale : {1.0F, 1.5F, 2.0F}) {
        const int width = static_cast<int>(960.0F * scale);
        const int height = static_cast<int>(700.0F * scale);
        Target target(width, height);
        const SDL_Rect viewport{13, 11, width - 26, height - 22};
        const SDL_Rect clip{17, 19, width - 79, height - 93};
        for (const auto workspace : {UiWorkspace::Play, UiWorkspace::Rotary, UiWorkspace::Service}) {
            for (const auto presentation : {UiPresentation::Dimensional, UiPresentation::Flat}) {
                target.configure(scale, viewport, &clip);
                auto model = model_at(960, 700, workspace, presentation);
                const auto document = document_for(model);
                const auto detail = name(960, 700, scale, workspace, presentation) + " translated physical clip";
                const auto expected = state(target.renderer());
                const auto frame = target.paint(model, document, detail);
                clipped_pixels(frame, expected, presentation, detail);
            }
        }
        // Preset focus is the one complete-view path that temporarily narrows
        // a caller's clip; exercise it alongside fonts, controls and quads.
        for (const auto presentation : {UiPresentation::Dimensional, UiPresentation::Flat}) {
            for (const int clip_case : {0, 1, 2}) {
                target.configure(scale, viewport, &clip);
                if (clip_case == 1) {
                    // Half-pixel physical components created in logical units
                    // must retain the original logical query as well as pixels.
                    const SDL_Rect logical_clip{11, 13, 900, 630};
                    require(SDL_RenderSetClipRect(target.renderer(), &logical_clip) == 0,
                        "set caller clip in current logical coordinates");
                } else if (clip_case == 2) {
                    // Cut through D# itself, so an outward intersection error
                    // produces visible focus ink outside the original clip.
                    SDL_Rect crossing = clip;
                    crossing.x = scale == 1.0F ? 61 : scale == 1.5F ? 91 : 119;
                    target.configure(scale, viewport, &crossing);
                }
                auto model = model_at(960, 700, UiWorkspace::Play, presentation);
                const UiControlId id{UiControlKind::PresetKey, Manual::Upper, DrawbarBank::A, 3};
                static_cast<void>(model.activate(id));
                require(model.view().focus == id, "focus narrow accidental preset");
                const auto detail = name(960, 700, scale, UiWorkspace::Play, presentation) +
                    " preset D# focus clip case " + std::to_string(clip_case);
                const auto expected = state(target.renderer());
                const auto frame = target.paint(model, document_for(model), detail);
                clipped_pixels(frame, expected, presentation, detail);
            }
        }
    }
}

long double cross(UiPoint a, UiPoint b, long double x, long double y) {
    return (static_cast<long double>(b.x) - a.x) * (y - a.y) -
        (static_cast<long double>(b.y) - a.y) * (x - a.x);
}

bool inside(const UiQuad& quad, long double x, long double y) {
    const auto& p = quad.points;
    return cross(p[0], p[1], x, y) >= 0.0L && cross(p[1], p[2], x, y) > 0.0L &&
        cross(p[2], p[3], x, y) > 0.0L && cross(p[3], p[0], x, y) >= 0.0L;
}

void scaled_focus(const std::filesystem::path& captures) {
    constexpr std::array<UiControlId, 4> ids{{
        {UiControlKind::ManualKey, Manual::Upper, DrawbarBank::A, 0},
        {UiControlKind::ManualKey, Manual::Upper, DrawbarBank::A, 30},
        {UiControlKind::ManualKey, Manual::Lower, DrawbarBank::A, 60},
        {UiControlKind::PedalKey, Manual::Upper, DrawbarBank::A, 13}}};
    for (const float scale : {1.5F, 2.0F}) {
        const int width = static_cast<int>(960.0F * scale);
        const int height = static_cast<int>(700.0F * scale);
        Target target(width, height);
        target.configure(scale, {0, 0, width, height});
        for (const auto presentation : {UiPresentation::Dimensional, UiPresentation::Flat}) {
            const auto model = model_at(960, 700, UiWorkspace::Play, presentation);
            const auto document = document_for(model);
            const auto baseline = target.paint(model, document, "fractional/doubled focus baseline");
            for (const auto id : ids) {
                auto focused = model;
                require(focused.activate(id).count == 0 && focused.view().focus == id, "focus actual playing key");
                const auto frame = target.paint(focused, document, "scaled focus frame");
                const auto& key = id.kind == UiControlKind::PedalKey ? model.layout().pedal_keys[id.index] :
                    model.layout().manual_keys[static_cast<std::size_t>(id.manual)][id.index];
                const int footer = static_cast<int>(model.layout().footer.y * scale);
                std::size_t changed = 0;
                std::size_t leaked = 0;
                const Pixel cyan{kUiFocusCyan.red, kUiFocusCyan.green, kUiFocusCyan.blue, kUiFocusCyan.alpha};
                for (int y = 0; y < footer; ++y) {
                    for (int x = 0; x < width; ++x) {
                        const auto index = offset(x, y, width);
                        if (baseline.pixels[index] == frame.pixels[index]) continue;
                        ++changed;
                        if (frame.pixels[index] != cyan ||
                            !inside(key.hit, (x + 0.5L) / scale, (y + 0.5L) / scale)) ++leaked;
                    }
                }
                ++counts.focus;
                check(changed >= 8 && leaked == 0, "scaled full-view focus remains visible only inside its key");
                if (!captures.empty() && scale == 1.5F && presentation == UiPresentation::Dimensional && id == ids[1])
                    target.save(captures / "injected-renderer-play-960x700-at-1p5.bmp");
            }
        }
    }
}

// Measurement helpers below reproduce the inspected layout policy only to
// report space budgets. They are not independent proof of that policy. The
// independent evidence is each complete renderer frame and changed value ink.
float advance(std::string_view text, float size) {
    std::uint32_t units = 0;
    for (const char c : text)
        units += font_data::glyph(font_data::kSans, static_cast<unsigned char>(c)).advance_64;
    return static_cast<float>(units) * size / (64.0F * static_cast<float>(font_data::kSans.pixel_height));
}

std::vector<std::string> lines(std::string_view text, float width, float size) {
    std::vector<std::string> result;
    while (!text.empty()) {
        std::size_t count = 0;
        while (count < text.size() && advance(text.substr(0, count + 1), size) <= width) ++count;
        require(count > 0, "measured Service width admits a character");
        if (count < text.size()) {
            const auto space = text.substr(0, count).find_last_of(' ');
            if (space != std::string_view::npos && space > count / 2) count = space;
        }
        result.emplace_back(text.substr(0, count));
        text.remove_prefix(count);
        while (!text.empty() && text.front() == ' ') text.remove_prefix(1);
    }
    return result;
}

struct MeasuredRow {
    std::size_t section{}, row{};
    UiRect card{}, value{};
    float size{}, line_height{}, summary_top{}, bottom{};
    std::vector<std::string> text;
};

std::vector<MeasuredRow> measure_service(const UiModel& model, const InspectionDocument& document) {
    const auto& body = model.layout().workspace_panel;
    const float card_width = (body.width - 20.0F) / 3.0F;
    const float card_height = (body.height - 55.0F) / 2.0F;
    const bool compact = card_height < 280.0F;
    const float padding = compact ? 9.0F : 13.0F;
    const float text_width = card_width - 2.0F * padding;
    const float label_height = (compact ? 10.0F : 11.0F) * 1.15F;
    const float value_size = compact ? 10.5F : 12.0F;
    const float line_height = value_size * 1.25F;
    std::vector<MeasuredRow> result;
    for (std::size_t section = 0; section < 6; ++section) {
        const auto& card = document.sections[section];
        const UiRect bounds{body.x + static_cast<float>(section % 3) * (card_width + 10.0F),
            body.y + 45.0F + static_cast<float>(section / 3) * (card_height + 10.0F), card_width, card_height};
        const float summary_size = compact ? 10.0F : 11.0F;
        const float summary_height = static_cast<float>(lines(card.summary, text_width, summary_size).size()) * summary_size * 1.25F;
        const float summary_top = bounds.y + bounds.height - padding - summary_height;
        float y = bounds.y + (compact ? 31.0F : 39.0F);
        std::vector<std::vector<std::string>> content;
        float required = 0.0F;
        for (std::size_t row = 0; row < card.row_count; ++row) {
            std::string value(card.rows[row].value.view());
            if (!card.rows[row].unit.empty()) value += " " + std::string(card.rows[row].unit);
            content.push_back(lines(value, text_width, value_size));
            required += label_height + static_cast<float>(content.back().size()) * line_height;
        }
        const float extra = card.row_count > 1 ? std::clamp((summary_top - 9.0F - y - required) /
            static_cast<float>(card.row_count - 1), 0.0F, compact ? 3.0F : 10.0F) : 0.0F;
        for (std::size_t row = 0; row < card.row_count; ++row) {
            y += label_height;
            const float used = static_cast<float>(content[row].size()) * line_height;
            const float ink_bottom = y + static_cast<float>(content[row].size() - 1) * line_height + value_size;
            check(ink_bottom <= summary_top - 7.0F, "all Service value lines fit above the card summary");
            result.push_back({section, row, bounds, {bounds.x + padding, y, text_width, used},
                value_size, line_height, summary_top, ink_bottom, content[row]});
            std::cout << "SERVICE|" << model.layout().width << 'x' << model.layout().height << '|' <<
                card.rows[row].id << '|' << value_size << '|' << content[row].size() << '|' <<
                text_width << '|' << y << '|' << ink_bottom << '|' << summary_top - 7.0F - ink_bottom;
            for (const auto& text : content[row]) std::cout << '|' << text;
            std::cout << '\n';
            y += used + extra;
        }
    }
    check(result.size() == 28, "all 28 contracted Service values are measured");
    return result;
}

bool inside_rect(const UiRect& rect, float x, float y, float tolerance = 0.0F) {
    return x >= rect.x - tolerance && y >= rect.y - tolerance &&
        x < rect.x + rect.width + tolerance && y < rect.y + rect.height + tolerance;
}

void service_values(const std::filesystem::path& captures) {
    for (const auto size : {std::array<int, 2>{960, 700}, std::array<int, 2>{1280, 900}}) {
        constexpr float scale = 1.5F;
        const int width = static_cast<int>(static_cast<float>(size[0]) * scale);
        const int height = static_cast<int>(static_cast<float>(size[1]) * scale);
        Target target(width, height);
        target.configure(scale, {0, 0, width, height});
        const auto model = model_at(size[0], size[1], UiWorkspace::Service, UiPresentation::Dimensional);
        const auto document = document_for(model);
        const auto measured = measure_service(model, document);
        const auto baseline = target.paint(model, document, "Service complete values baseline");
        if (!captures.empty() && size[0] == 960)
            target.save(captures / "injected-renderer-service-960x700-at-1p5.bmp");
        for (const auto& item : measured) {
            auto changed = document;
            auto& row = changed.sections[item.section].rows[item.row];
            require(row.availability != InspectionAvailability::Invalid, "valid synthetic display row");
            // This changes only the row's badge and value color. All actual
            // value bytes/units, wrapping and card geometry remain identical.
            row.availability = InspectionAvailability::Invalid;
            const auto frame = target.paint(model, changed, std::string(row.id) + " value color probe");
            std::vector<std::size_t> line_ink(item.text.size());
            std::size_t leaked = 0;
            for (int y = 0; y < height; ++y) {
                for (int x = 0; x < width; ++x) {
                    const auto index = offset(x, y, width);
                    if (baseline.pixels[index] == frame.pixels[index]) continue;
                    const float logical_x = (static_cast<float>(x) + 0.5F) / scale;
                    const float logical_y = (static_cast<float>(y) + 0.5F) / scale;
                    if (!inside_rect(item.card, logical_x, logical_y)) ++leaked;
                    for (std::size_t line = 0; line < item.text.size(); ++line) {
                        const UiRect band{item.value.x, item.value.y + static_cast<float>(line) * item.line_height,
                            item.value.width, item.line_height};
                        if (inside_rect(band, logical_x, logical_y)) ++line_ink[line];
                    }
                }
            }
            ++counts.service_values;
            check(leaked == 0, std::string(row.id) + " value/badge probe stays in its card");
            for (std::size_t line = 0; line < line_ink.size(); ++line) {
                ++counts.service_lines;
                check(line_ink[line] >= 3, std::string(row.id) + " line " + std::to_string(line + 1) +
                    " has visible actual value ink; pixels=" + std::to_string(line_ink[line]));
            }
        }
    }
}

} // namespace

int main(int argc, char** argv) {
    SDL_SetMainReady();
    try {
        require(argc == 1 || argc == 2, "optional argument is a fresh capture directory");
        const char* capture_environment = SDL_getenv("HAMMOND_SCALED_VIEW_CAPTURE_DIR");
        const std::filesystem::path captures = argc == 2 ? std::filesystem::path(argv[1]) :
            capture_environment != nullptr ? std::filesystem::path(capture_environment) : std::filesystem::path{};
        if (!captures.empty()) require(std::filesystem::create_directory(captures), "create fresh proof directory");
        require(SDL_Init(0) == 0, "initialize SDL with no window/audio/MIDI subsystems");
        full_matrix();
        viewport_matrix();
        scaled_focus(captures);
        service_values(captures);
        SDL_version version{};
        SDL_GetVersion(&version);
        std::cout << "SDL " << static_cast<int>(version.major) << '.' << static_cast<int>(version.minor) << '.' <<
            static_cast<int>(version.patch) << "; injected full paint_instrument software frames, no application/window/device\n";
        SDL_Quit();
    } catch (const std::exception& error) {
        std::cerr << "Scaled view setup failed: " << error.what() << '\n';
        SDL_Quit();
        return EXIT_FAILURE;
    }
    std::cout << "RESULT frames=" << counts.frames << " renderer_states=" << counts.states <<
        " clipped_frames=" << counts.clips << " scaled_focus=" << counts.focus <<
        " service_values=" << counts.service_values << " service_lines=" << counts.service_lines <<
        " failures=" << counts.failures << '\n';
    return counts.failures == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
