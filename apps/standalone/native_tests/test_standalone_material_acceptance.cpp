#include "InstrumentView.h"
#include "FontData.h"

#include <SDL.h>

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <limits>
#include <memory>
#include <span>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace {
using namespace hammond;
using namespace hammond::standalone;
using Pixel = std::array<std::uint8_t, 4>;
constexpr std::size_t kKeys = 2 * kManualKeyCount + kPedalCount;
constexpr Pixel kBed{7, 9, 8, 255};
constexpr Pixel kCard{19, 21, 18, 255};
constexpr Pixel kCyan{kUiFocusCyan.red, kUiFocusCyan.green, kUiFocusCyan.blue, 255};

struct Counts {
    std::size_t checks{}, failures{}, frames{}, states{}, clip_frames{}, outside_pixels{};
    std::size_t held_keys{}, focused_keys{}, surfaces{}, corners{}, cut_clips{};
    std::size_t status_frames{}, status_ink{}, last_row_ink{}, overlay_panels{}, overlay_buttons{};
} counts;
std::array<long double, 2> minimum_contrast{
    std::numeric_limits<long double>::infinity(), std::numeric_limits<long double>::infinity()};
std::vector<std::string> overlay_results;
std::vector<std::string> header_results;
struct MidiCounts {
    std::size_t scenes{}, frames{}, controls{}, glyphs{}, value_changes{}, focused{}, invalid{}, long_text{}, clipped{};
    std::size_t intersected_glyphs{}, resampled_pixels{}, unexplained_pixels{}, literal_mismatches{};
} midi_counts;
std::vector<std::string> midi_clip_results;

struct LiteralText {
    std::string value;
    UiRect band{};
    float x{}, top{}, size{};
    UiColor color{};
    UiColor background{27, 29, 28};
};

void require(bool condition, std::string_view detail) {
    if (!condition) throw std::runtime_error(std::string(detail) + ": " + SDL_GetError());
}

void check(bool condition, std::string_view detail) {
    ++counts.checks;
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
    require(SDL_RenderSetScale(renderer, 1.0F, 1.0F) == 0, "read exact physical renderer state");
    SDL_RenderGetViewport(renderer, &result.viewport);
    SDL_RenderGetClipRect(renderer, &result.clip);
    result.clipped = SDL_RenderIsClipEnabled(renderer) == SDL_TRUE;
    require(SDL_GetRenderDrawBlendMode(renderer, &result.blend) == 0, "read blend mode");
    require(SDL_RenderSetScale(renderer, result.x, result.y) == 0, "restore renderer scale after read");
    return result;
}

bool visible(const State& transform, int x, int y) {
    const int local_x = x - transform.viewport.x, local_y = y - transform.viewport.y;
    return local_x >= 0 && local_y >= 0 && local_x < transform.viewport.w &&
        local_y < transform.viewport.h && (!transform.clipped ||
        (local_x >= transform.clip.x && local_y >= transform.clip.y &&
         local_x < transform.clip.x + transform.clip.w && local_y < transform.clip.y + transform.clip.h));
}

struct Point { long double x{}, y{}; };
Point logical(const State& transform, int x, int y) {
    return {(x + 0.5L - transform.viewport.x) / transform.x,
            (y + 0.5L - transform.viewport.y) / transform.y};
}

bool inside(UiRect bounds, Point p) {
    return p.x >= bounds.x && p.y >= bounds.y &&
        p.x < static_cast<long double>(bounds.x) + bounds.width &&
        p.y < static_cast<long double>(bounds.y) + bounds.height;
}

// Independent long-double half-planes on public vertices. In particular this
// never calls UiQuad::contains(), a hit helper, or a production raster helper.
long double cross(UiPoint a, UiPoint b, Point p) {
    return (static_cast<long double>(b.x) - a.x) * (p.y - a.y) -
           (static_cast<long double>(b.y) - a.y) * (p.x - a.x);
}

bool inside(const UiQuad& quad, Point p) {
    const auto& q = quad.points;
    return cross(q[0], q[1], p) >= 0.0L && cross(q[1], q[2], p) > 0.0L &&
           cross(q[2], q[3], p) > 0.0L && cross(q[3], q[0], p) >= 0.0L;
}

struct Frame {
    int width{}, height{};
    State transform{};
    std::vector<Pixel> pixels;
    [[nodiscard]] std::size_t offset(int x, int y) const {
        return static_cast<std::size_t>(y) * static_cast<std::size_t>(width) + static_cast<std::size_t>(x);
    }
};

std::string fingerprint(const Frame& frame) {
    std::uint64_t hash = 14695981039346656037ULL;
    for (const auto& pixel : frame.pixels)
        for (const auto channel : pixel) hash = (hash ^ channel) * 1099511628211ULL;
    std::ostringstream text;
    text << std::hex << std::setfill('0') << std::setw(16) << hash;
    return text.str();
}

class Target {
public:
    Target(int width, int height)
        : surface_(SDL_CreateRGBSurfaceWithFormat(0, width, height, 32, SDL_PIXELFORMAT_RGBA32), SDL_FreeSurface),
          renderer_(surface_ ? SDL_CreateSoftwareRenderer(surface_.get()) : nullptr, SDL_DestroyRenderer),
          drawing_(renderer_.get()) {
        require(width <= 1920 && height <= 1100, "bounded software surface");
        require(surface_ && renderer_, "create software surface and renderer");
        std::string error;
        require(drawing_.initialize(error), "initialize actual Drawing: " + error);
    }

    void configure(float scale, SDL_Rect viewport, const SDL_Rect* clip = nullptr) {
        require(SDL_RenderSetScale(renderer_.get(), 1.0F, 1.0F) == 0, "configure physical units");
        require(SDL_RenderSetViewport(renderer_.get(), &viewport) == 0, "set caller viewport");
        require(SDL_RenderSetClipRect(renderer_.get(), clip) == 0, "set caller clip");
        require(SDL_RenderSetScale(renderer_.get(), scale, scale) == 0, "set caller scale");
    }

    void logical_clip(SDL_Rect clip) {
        require(SDL_RenderSetClipRect(renderer_.get(), &clip) == 0, "set fractional physical clip in logical units");
    }

    Frame read() {
        require(SDL_RenderFlush(renderer_.get()) == 0, "flush native paint");
        require(SDL_LockSurface(surface_.get()) == 0, "lock entire software surface");
        Frame frame{surface_->w, surface_->h, state(renderer_.get()), std::vector<Pixel>(
            static_cast<std::size_t>(surface_->w) * static_cast<std::size_t>(surface_->h))};
        const auto* bytes = static_cast<const std::uint8_t*>(surface_->pixels);
        static_assert(sizeof(Pixel) == 4);
        for (int y = 0; y < frame.height; ++y) {
            const auto* row = bytes + static_cast<std::size_t>(y) * static_cast<std::size_t>(surface_->pitch);
            for (int x = 0; x < frame.width; ++x) {
                const auto p = static_cast<std::size_t>(x) * 4;
                frame.pixels[frame.offset(x, y)] = {row[p], row[p + 1], row[p + 2], row[p + 3]};
            }
        }
        SDL_UnlockSurface(surface_.get());
        return frame;
    }

    Frame paint(const UiModel& model, const InstrumentViewInfo& info = {}, const UiRect* modal_focus = nullptr) {
        const auto before = state(renderer_.get());
        paint_instrument(drawing_, model, info);
        // Application::render_frame adds this public Drawing primitive after
        // InstrumentView. Native application tests separately own focus traversal.
        if (modal_focus) drawing_.outline(*modal_focus, kUiFocusCyan, 2.0F);
        const auto after = state(renderer_.get());
        check(before.x == after.x && before.y == after.y &&
              equal(before.viewport, after.viewport) && equal(before.clip, after.clip) &&
              equal(before.logical_viewport, after.logical_viewport) &&
              equal(before.logical_clip, after.logical_clip) &&
              before.clipped == after.clipped && before.blend == after.blend,
              "public paint preserves caller scale, physical/logical viewport/clip and blend");
        ++counts.states;
        ++counts.frames;
        auto frame = read();
        const Pixel clear = model.view().presentation == UiPresentation::Flat ? Pixel{18, 21, 20, 255} :
            Pixel{kUiWalnut.red, kUiWalnut.green, kUiWalnut.blue, 255};
        std::size_t leaked = 0, ink = 0;
        for (int y = 0; y < frame.height; ++y)
            for (int x = 0; x < frame.width; ++x) {
                const bool owned = visible(before, x, y);
                if (!owned) ++counts.outside_pixels;
                if (frame.pixels[frame.offset(x, y)] == clear) continue;
                if (owned) ++ink;
                else ++leaked;
            }
        check(leaked == 0 && ink > 0, "all nonclear ink remains in caller viewport/clip");
        ++counts.clip_frames;
        return frame;
    }

    Frame literal_last_row(UiRect card) {
        drawing_.clear({19, 21, 18});
        drawing_.text("ROTARY AUDIO: NOT CONNECTED", card.x + 12.0F, card.y + 85.0F,
                      10.0F, {166, 159, 142});
        return read();
    }

    float text_width(std::string_view value, float size) const {
        return drawing_.text_width(value, size);
    }

    Frame literal_mask(std::span<const LiteralText> text) {
        drawing_.clear({0, 0, 0});
        for (const auto& line : text)
            drawing_.text(line.value, line.x, line.top, line.size, {255, 255, 255});
        return read();
    }

    Frame literal_plate(std::span<const LiteralText> text) {
        drawing_.clear({0, 0, 0});
        for (const auto& line : text) {
            drawing_.rect(line.band, line.background);
            drawing_.text(line.value, line.x, line.top, line.size, line.color);
        }
        return read();
    }

private:
    std::unique_ptr<SDL_Surface, decltype(&SDL_FreeSurface)> surface_;
    std::unique_ptr<SDL_Renderer, decltype(&SDL_DestroyRenderer)> renderer_;
    Drawing drawing_;
};

UiModel model_at(int width, int height, UiPresentation presentation) {
    UiModel model;
    require(model.resize(static_cast<float>(width), static_cast<float>(height)), "resize logical model");
    require(model.set_presentation(presentation), "set presentation");
    SessionSnapshot snapshot;
    snapshot.controls = model.view().controls;
    snapshot.publication_revision = 2;
    model.observe(snapshot);
    return model;
}

struct KeyId { std::size_t division{}, index{}; };
std::size_t token(KeyId id) { return id.division * kManualKeyCount + id.index; }
std::span<const UiKeyGeometry> keys(const UiLayout& layout, std::size_t division) {
    if (division < 2) return layout.manual_keys[division];
    return layout.pedal_keys;
}
UiControlId control(KeyId id) {
    return {id.division == 2 ? UiControlKind::PedalKey : UiControlKind::ManualKey,
            id.division == 1 ? Manual::Lower : Manual::Upper, DrawbarBank::A,
            static_cast<std::uint8_t>(id.index)};
}

struct Owners {
    std::vector<int> visible;
    std::array<const UiKeyGeometry*, kKeys> geometry{};
};

Owners owners_for(const UiLayout& layout, const Frame& frame) {
    Owners owners{std::vector<int>(frame.pixels.size(), -1), {}};
    for (const bool accidental : {false, true})
        for (std::size_t division = 0; division < 3; ++division)
            for (std::size_t index = 0; index < keys(layout, division).size(); ++index) {
                const auto& key = keys(layout, division)[index];
                const auto id = token({division, index});
                owners.geometry[id] = &key;
                if (key.accidental != accidental) continue;
                const auto& t = frame.transform;
                const int left = std::clamp(static_cast<int>(std::floor(static_cast<long double>(key.bounds.x) * t.x + t.viewport.x)), 0, frame.width);
                const int right = std::clamp(static_cast<int>(std::ceil((static_cast<long double>(key.bounds.x) + key.bounds.width) * t.x + t.viewport.x)), 0, frame.width);
                const int top = std::clamp(static_cast<int>(std::floor(static_cast<long double>(key.bounds.y) * t.y + t.viewport.y)), 0, frame.height);
                const int bottom = std::clamp(static_cast<int>(std::ceil((static_cast<long double>(key.bounds.y) + key.bounds.height) * t.y + t.viewport.y)), 0, frame.height);
                for (int y = top; y < bottom; ++y)
                    for (int x = left; x < right; ++x)
                        if (visible(t, x, y) && inside(key.hit, logical(t, x, y)))
                            owners.visible[frame.offset(x, y)] = static_cast<int>(id);
            }
    return owners;
}

long double srgb_level(Pixel p) {
    return (2126.0L * p[0] + 7152.0L * p[1] + 722.0L * p[2]) / 10000.0L;
}

Pixel sample(const Frame& frame, const Owners& owners, KeyId id, const UiQuad& quad,
             long double depth, long double across) {
    const auto& q = quad.points;
    const long double y = q[0].y + (static_cast<long double>(q[3].y) - q[0].y) * depth;
    const long double left = q[0].x + (static_cast<long double>(q[3].x) - q[0].x) * depth;
    const long double right = q[1].x + (static_cast<long double>(q[2].x) - q[1].x) * depth;
    const int px = static_cast<int>(std::floor((left + (right - left) * across) * frame.transform.x + frame.transform.viewport.x));
    const int py = static_cast<int>(std::floor(y * frame.transform.y + frame.transform.viewport.y));
    require(px >= 0 && py >= 0 && px < frame.width && py < frame.height, "material sample is in bounded target");
    require(owners.visible[frame.offset(px, py)] == static_cast<int>(token(id)), "material sample has independent visible owner");
    return frame.pixels[frame.offset(px, py)];
}

void surface_checks(const UiModel& model, const Frame& frame, const Owners& owners) {
    for (std::size_t division = 0; division < 3; ++division)
        for (const bool accidental : {false, true}) {
            const std::array<std::size_t, 3> indices = division < 2 ?
                (accidental ? std::array<std::size_t, 3>{1, 30, 58} : std::array<std::size_t, 3>{0, 29, 60}) :
                (accidental ? std::array<std::size_t, 3>{1, 13, 22} : std::array<std::size_t, 3>{0, 12, 24});
            for (const auto index : indices) {
                const KeyId id{division, index};
                const auto& key = *owners.geometry[token(id)];
                require(key.accidental == accidental, "literal representative pitch class");
                if (model.view().presentation == UiPresentation::Flat) {
                    const Pixel expected = accidental ? Pixel{32, 33, 30, 255} : Pixel{242, 230, 204, 255};
                    bool uniform = true;
                    for (const auto depth : {0.25L, 0.55L, 0.90L})
                        for (const auto across : {0.40L, 0.50L, 0.60L})
                            uniform = sample(frame, owners, id, key.hit, depth, across) == expected && uniform;
                    check(uniform, "1.25x Flat top/former-front interior is uniform");
                } else {
                    long double contrast = 0.0L;
                    for (const auto across : {0.40L, 0.50L, 0.60L})
                        for (const auto depth : {0.35L, 0.50L, 0.65L})
                            contrast += srgb_level(sample(frame, owners, id, key.top, depth, across)) -
                                srgb_level(sample(frame, owners, id, key.front, depth, across));
                    contrast /= 9.0L;
                    minimum_contrast[accidental ? 1 : 0] = std::min(minimum_contrast[accidental ? 1 : 0], contrast);
                    check(contrast >= (accidental ? 8.0L : 15.0L), "1.25x projected front remains darker than its top");
                }
                ++counts.surfaces;
            }
        }
    if (model.view().presentation == UiPresentation::Flat) return;
    for (std::size_t manual = 0; manual < 2; ++manual)
        for (const std::size_t index : {std::size_t{0}, kManualKeyCount - 1}) {
            const auto& key = model.layout().manual_keys[manual][index];
            std::size_t exposed = 0, leaked = 0;
            for (int y = 0; y < frame.height; ++y)
                for (int x = 0; x < frame.width; ++x) {
                    const auto p = logical(frame.transform, x, y);
                    const auto at = frame.offset(x, y);
                    if (!visible(frame.transform, x, y) || !inside(key.bounds, p) ||
                        owners.visible[at] >= 0 || inside(key.hit, p)) continue;
                    ++exposed;
                    if (frame.pixels[at] != kBed) ++leaked;
                }
            check(exposed > 4 && leaked == 0, "1.25x sloped AABB corners retain only literal key-bed color");
            ++counts.corners;
        }
}

void key_matrix(int width, int height, bool cropped) {
    Target target(cropped ? 1750 : 1240, cropped ? 1025 : 915);
    const SDL_Rect clip{19, 17, 1717, 1001};
    target.configure(1.25F, cropped ? SDL_Rect{-17, -9, 1750, 1025} : SDL_Rect{13, 11, 1200, 875},
                     cropped ? &clip : nullptr);
    for (const auto presentation : {UiPresentation::Dimensional, UiPresentation::Flat}) {
        const auto base = model_at(width, height, presentation);
        const auto baseline = target.paint(base);
        const auto owners = owners_for(base.layout(), baseline);
        surface_checks(base, baseline, owners);
        for (const bool accidental : {false, true}) {
            auto held_model = base;
            auto snapshot = base.view().applied;
            snapshot.publication_revision += 2;
            for (std::size_t division = 0; division < 3; ++division)
                for (std::size_t index = 0; index < keys(base.layout(), division).size(); ++index)
                    if (keys(base.layout(), division)[index].accidental == accidental) {
                        if (division < 2) snapshot.held_keys[division][index] = true;
                        else snapshot.held_pedals[index] = true;
                    }
            held_model.observe(snapshot);
            const auto held = target.paint(held_model);
            std::array<std::size_t, kKeys> changed{}, fronts{};
            std::size_t leaked = 0;
            for (int y = 0; y < held.height; ++y)
                for (int x = 0; x < held.width; ++x) {
                    const auto at = held.offset(x, y);
                    if (baseline.pixels[at] == held.pixels[at]) continue;
                    const int owner = owners.visible[at];
                    if (owner < 0 || owners.geometry[static_cast<std::size_t>(owner)]->accidental != accidental) { ++leaked; continue; }
                    ++changed[static_cast<std::size_t>(owner)];
                    if (inside(owners.geometry[static_cast<std::size_t>(owner)]->front, logical(held.transform, x, y)))
                        ++fronts[static_cast<std::size_t>(owner)];
                }
            check(leaked == 0, "1.25x held delta never escapes visible half-plane owner or accidental occlusion");
            for (std::size_t id = 0; id < kKeys; ++id)
                if (owners.geometry[id]->accidental == accidental) {
                    check(changed[id] >= 8 && (presentation == UiPresentation::Flat || fronts[id] > 0),
                          "every held key has visible top/front ink at 1.25x");
                    ++counts.held_keys;
                }
            const std::array<KeyId, 3> focus_ids = accidental ?
                std::array<KeyId, 3>{{{0, 1}, {1, 58}, {2, 13}}} :
                std::array<KeyId, 3>{{{0, 0}, {1, 60}, {2, 12}}};
            for (const auto id : focus_ids) {
                auto focused_model = held_model;
                require(focused_model.activate(control(id)).count == 0 && focused_model.view().focus == control(id),
                        "focus a held playing key without musical commands");
                const auto focused = target.paint(focused_model);
                std::size_t changed_focus = 0, escaped = 0;
                for (int y = 0; y < held.height; ++y)
                    for (int x = 0; x < held.width; ++x) {
                        const auto at = held.offset(x, y);
                        if (held.pixels[at] == focused.pixels[at] ||
                            inside(base.layout().footer, logical(held.transform, x, y))) continue;
                        ++changed_focus;
                        if (owners.visible[at] != static_cast<int>(token(id)) || focused.pixels[at] != kCyan ||
                            !inside(owners.geometry[token(id)]->hit, logical(held.transform, x, y))) ++escaped;
                    }
                check(changed_focus >= 8 && escaped == 0, "1.25x held-key focus is cyan and inside its visible owner");
                ++counts.focused_keys;
            }
        }
    }
}

void cut_clip_matrix() {
    Target target(1240, 915);
    for (const auto presentation : {UiPresentation::Dimensional, UiPresentation::Flat})
        for (const bool logical_units : {false, true}) {
            auto model = model_at(960, 700, presentation);
            const UiControlId id{UiControlKind::ManualKey, Manual::Upper, DrawbarBank::A, 1};
            require(model.activate(id).count == 0, "focus clipped accidental");
            const auto& key = model.layout().manual_keys[0][1];
            const float center = (key.top.points[0].x + key.top.points[1].x) / 2.0F;
            const SDL_Rect clip{static_cast<int>(center * 1.25F), 513, 900, 241};
            target.configure(1.25F, {13, 11, 1200, 875}, &clip);
            if (logical_units) target.logical_clip({static_cast<int>(center), 411, 721, 193});
            const auto frame = target.paint(model);
            std::size_t cyan = 0;
            for (const auto& pixel : frame.pixels) if (pixel == kCyan) ++cyan;
            check(cyan > 0, "cut caller clip retains visible focus on the surviving accidental half");
            ++counts.cut_clips;
        }
}

void compact_status() {
    Target target(1920, 700);
    target.configure(1.0F, {0, 0, 1920, 700});
    const std::string long_text(2048, 'W');
    for (const auto presentation : {UiPresentation::Dimensional, UiPresentation::Flat}) {
        const auto model = model_at(1920, 700, presentation);
        const auto& layout = model.layout();
        const auto& cabinet = layout.cabinet_panel;
        const auto& art = layout.cabinet_art;
        const float below_art = art.y + art.height;
        const UiRect card{cabinet.x + 14.0F, below_art + 61.0F, cabinet.width - 28.0F,
            cabinet.y + cabinet.height - 14.0F - below_art - 61.0F};
        check(layout.show_cabinet && !layout.sidebar_pedals && std::abs(card.height - 101.0F) < 0.001F,
              "1920x700 exercises the actual legacy 101-pixel status card");
        const auto literal = target.literal_last_row(card);
        const auto baseline = target.paint(model);
        InstrumentViewInfo info;
        info.audio_running = true;
        info.sample_rate = std::numeric_limits<int>::max();
        info.buffer_frames = std::numeric_limits<std::uint32_t>::max();
        info.device_name = long_text;
        info.audio_driver = long_text;
        info.status_message = long_text;
        info.midi_available = true;
        info.midi_open = true;
        info.midi_port = long_text;
        info.midi_backend = long_text;
        info.midi_status = long_text;
        const auto long_status = target.paint(model, info);
        for (const auto* frame : {&baseline, &long_status}) {
            const std::array<float, 5> offsets{10.0F, 31.0F, 49.0F, 67.0F, 85.0F};
            std::array<std::size_t, 5> row_ink{};
            std::size_t escaped = 0, final_mismatch = 0, below = 0;
            std::string first_escape;
            for (int y = 0; y < frame->height; ++y)
                for (int x = 0; x < frame->width; ++x) {
                    const auto p = logical(frame->transform, x, y);
                    const auto at = frame->offset(x, y);
                    // The SDL_FRect card fill can truncate its fractional
                    // right edge. Do not call that exposed panel column text;
                    // inspect the inner card and all complete content bands.
                    if (inside(UiRect{card.x + 1.0F, card.y + 2.0F, card.width - 2.0F, card.height - 3.0F}, p) &&
                        frame->pixels[at] != kCard) {
                        bool allowed = false;
                        for (std::size_t row = 0; row < offsets.size(); ++row)
                            if (inside(UiRect{card.x + 12.0F, card.y + offsets[row], card.width - 24.0F, 14.0F}, p)) {
                                ++row_ink[row]; allowed = true;
                            }
                        if (!allowed) {
                            ++escaped;
                            if (first_escape.empty()) first_escape = " first=" + std::to_string(x) + "," + std::to_string(y) +
                                " rgb=" + std::to_string(frame->pixels[at][0]) + "," + std::to_string(frame->pixels[at][1]) + "," + std::to_string(frame->pixels[at][2]);
                        }
                    }
                    if (inside(UiRect{card.x + 12.0F, card.y + 85.0F, card.width - 24.0F, 14.0F}, p) &&
                        frame->pixels[at] != literal.pixels[at]) ++final_mismatch;
                    if (p.x >= card.x && p.x < card.x + card.width && p.y >= card.y + card.height &&
                        p.y < layout.pedal_panel.y && *std::min_element(frame->pixels[at].begin(), frame->pixels[at].begin() + 3) >= 100) ++below;
                }
            check(std::all_of(row_ink.begin(), row_ink.end(), [](std::size_t value) { return value > 20; }),
                  "all compact status rows, including final rotary fact, retain visible ink");
            check(escaped == 0 && final_mismatch == 0 && below == 0,
                  "compact text stays in literal row budgets; final rotary text matches; no ink below card: escaped=" +
                  std::to_string(escaped) + " final_mismatch=" + std::to_string(final_mismatch) +
                  " below=" + std::to_string(below) + first_escape);
            for (const auto ink : row_ink) counts.status_ink += ink;
            counts.last_row_ink += row_ink.back();
            ++counts.status_frames;
        }
        std::size_t leaked = 0, changed = 0, pedal_changes = 0;
        for (int y = 0; y < baseline.height; ++y)
            for (int x = 0; x < baseline.width; ++x) {
                const auto at = baseline.offset(x, y);
                if (baseline.pixels[at] == long_status.pixels[at]) continue;
                ++changed;
                const auto p = logical(baseline.transform, x, y);
                if (inside(layout.pedal_panel, p)) ++pedal_changes;
                if (!inside(UiRect{card.x + 12.0F, card.y + 31.0F, card.width - 24.0F, 14.0F}, p) &&
                    !inside(UiRect{card.x + 12.0F, card.y + 49.0F, card.width - 24.0F, 14.0F}, p) &&
                    !inside(layout.footer, p)) ++leaked;
            }
        check(changed > 100 && leaked == 0 && pedal_changes == 0,
              "long status/configuration strings change only allocated rows/footer and never pedal pixels");
    }
}

struct PatchResult { std::size_t pixels{}, wrong{}, variations{}; };
PatchResult patch(const Frame& frame, UiRect area, Pixel expected) {
    PatchResult result;
    Pixel first{};
    for (int y = 0; y < frame.height; ++y)
        for (int x = 0; x < frame.width; ++x) {
            if (!inside(area, logical(frame.transform, x, y))) continue;
            const auto pixel = frame.pixels[frame.offset(x, y)];
            if (result.pixels == 0) first = pixel;
            ++result.pixels;
            if (pixel != expected) ++result.wrong;
            if (pixel != first) ++result.variations;
        }
    return result;
}

void overlays() {
    for (const float scale : {1.0F, 1.25F}) {
        Target target(static_cast<int>(960.0F * scale), static_cast<int>(700.0F * scale));
        target.configure(scale, {0, 0, static_cast<int>(960.0F * scale), static_cast<int>(700.0F * scale)});
        for (const auto presentation : {UiPresentation::Dimensional, UiPresentation::Flat})
            for (const auto overlay : {ViewOverlay::Audio, ViewOverlay::Midi, ViewOverlay::Help}) {
                const auto model = model_at(960, 700, presentation);
                InstrumentViewInfo info;
                info.overlay = overlay;
                info.midi_available = true;
                const auto frame = target.paint(model, info);
                const auto audio = audio_overlay_layout(960.0F, 700.0F);
                const auto midi = midi_overlay_layout(960.0F, 700.0F);
                const auto panel = overlay == ViewOverlay::Midi ? midi.panel : audio.panel;
                // This narrow strip is after screws and before every label or
                // control. Button strips likewise avoid centered label ink.
                const auto panel_patch = patch(frame, {panel.x + 17.0F, panel.y + 65.0F, 6.0F, panel.height - 85.0F},
                                               {27, 29, 28, 255});
                const bool flat = presentation == UiPresentation::Flat;
                const std::string name = overlay == ViewOverlay::Audio ? "Audio" : overlay == ViewOverlay::Midi ? "MIDI" : "Help";
                check(panel_patch.pixels > 100 && (flat ? panel_patch.wrong == 0 : panel_patch.variations > 0),
                      name + (flat ? " Flat panel interior has no grain/gradient" : " dimensional control patch retains material variation"));
                ++counts.overlay_panels;
                std::vector<std::pair<UiRect, bool>> buttons;
                if (overlay == ViewOverlay::Midi) buttons = {{midi.close, false}, {midi.previous_port, false},
                    {midi.next_port, false}, {midi.upper_channel, false}, {midi.lower_channel, false},
                    {midi.pedal_channel, false}, {midi.apply, true}, {midi.disconnect, false}};
                else if (overlay == ViewOverlay::Audio) buttons = {{audio.close, false}, {audio.previous_device, false},
                    {audio.next_device, false}, {audio.sample_rate, false}, {audio.buffer_frames, false}, {audio.apply, true}};
                else buttons = {{audio.close, false}};
                std::size_t wrong_buttons = 0, button_pixels = 0;
                for (const auto& [bounds, selected] : buttons) {
                    const auto result = patch(frame, {bounds.x + 8.0F, bounds.y + 4.0F, 3.0F, bounds.height - 8.0F},
                        selected ? Pixel{238, 204, 145, 255} : Pixel{45, 41, 36, 255});
                    check(result.pixels > 20 && (flat ? result.wrong == 0 : result.variations > 0),
                          name + (flat ? " Flat button interior has no bevel/gradient" : " dimensional button retains material variation"));
                    wrong_buttons += result.wrong;
                    button_pixels += result.pixels;
                    ++counts.overlay_buttons;
                }
                std::ostringstream row;
                row << "{\"overlay\":\"" << name << "\",\"flat\":" << (flat ? "true" : "false")
                    << ",\"scale\":" << scale << ",\"panel_pixels\":" << panel_patch.pixels
                    << ",\"panel_nonflat_pixels\":" << panel_patch.wrong << ",\"button_pixels\":" << button_pixels
                    << ",\"button_nonflat_pixels\":" << wrong_buttons << ",\"rgba_fnv1a64\":\"" << fingerprint(frame) << "\"}";
                overlay_results.push_back(row.str());
            }
    }
}

SDL_Rect pixel_region(const Frame& frame, UiRect bounds) {
    const auto& t = frame.transform;
    const int left = std::clamp(static_cast<int>(std::floor(bounds.x * t.x + static_cast<float>(t.viewport.x))), 0, frame.width);
    const int top = std::clamp(static_cast<int>(std::floor(bounds.y * t.y + static_cast<float>(t.viewport.y))), 0, frame.height);
    const int right = std::clamp(static_cast<int>(std::ceil((bounds.x + bounds.width) * t.x + static_cast<float>(t.viewport.x))), 0, frame.width);
    const int bottom = std::clamp(static_cast<int>(std::ceil((bounds.y + bounds.height) * t.y + static_cast<float>(t.viewport.y))), 0, frame.height);
    return {left, top, right - left, bottom - top};
}

void literal_text_checks(Target& target, const Frame& actual, std::span<const LiteralText> text) {
    const auto mask = target.literal_mask(text);
    for (const auto& line : text) {
        const auto scan = pixel_region(actual, line.band);
        const std::array<int, 3> ink{line.color.red, line.color.green, line.color.blue};
        std::size_t core = 0, wrong = 0;
        for (int y = scan.y; y < scan.y + scan.h; ++y)
            for (int x = scan.x; x < scan.x + scan.w; ++x) {
                if (!visible(actual.transform, x, y) || !inside(line.band, logical(actual.transform, x, y))) continue;
                const auto at = actual.offset(x, y);
                const int coverage = mask.pixels[at][0];
                if (coverage >= 192) ++core;
                // Literal glyph coverage supplies a foreground interval over
                // any dark material in [0,110]. This checks the complete shape,
                // including empty glyph gaps, without duplicating text fitting
                // or assuming a flat background beneath dimensional labels.
                bool match = true;
                for (std::size_t channel = 0; channel < ink.size(); ++channel) {
                    const int lower = ink[channel] * coverage / 255 - 3;
                    const int upper = (ink[channel] * coverage + 110 * (255 - coverage)) / 255 + 3;
                    const int observed = actual.pixels[at][channel];
                    match = match && observed >= lower && observed <= upper;
                }
                if (!match) ++wrong;
            }
        check(core > 0 && wrong == 0 && target.text_width(line.value, line.size) <= line.band.width,
              "MIDI complete literal glyphs fit their separate band: " + line.value +
              " mismatched_pixels=" + std::to_string(wrong));
        ++midi_counts.glyphs;
    }
}

std::vector<std::size_t> modal_delta(const Frame& before, const Frame& after, UiRect scope,
                                   std::span<const UiRect> allowed, std::string_view detail) {
    std::vector<std::size_t> changes(allowed.size());
    std::size_t escaped = 0;
    const auto scan = pixel_region(before, scope);
    for (int y = scan.y; y < scan.y + scan.h; ++y)
        for (int x = scan.x; x < scan.x + scan.w; ++x) {
            const auto at = before.offset(x, y);
            if (before.pixels[at] == after.pixels[at]) continue;
            const auto p = logical(before.transform, x, y);
            if (!inside(scope, p)) continue;
            bool owned = false;
            for (std::size_t index = 0; index < allowed.size(); ++index)
                if (inside(allowed[index], p)) { ++changes[index]; owned = true; }
            if (!owned) ++escaped;
        }
    check(escaped == 0 && std::all_of(changes.begin(), changes.end(), [](std::size_t n) { return n > 0; }),
          std::string(detail) + " escaped_pixels=" + std::to_string(escaped));
    return changes;
}

void modal_focus_check(const Frame& plain, const Frame& focused, UiRect expected) {
    const UiRect outer{expected.x - 1.0F, expected.y - 1.0F, expected.width + 2.0F, expected.height + 2.0F};
    const UiRect inner{expected.x + 3.0F, expected.y + 3.0F, expected.width - 6.0F, expected.height - 6.0F};
    std::size_t changed = 0, escaped = 0, missed = 0;
    for (int y = 0; y < focused.height; ++y)
        for (int x = 0; x < focused.width; ++x) {
            const auto at = focused.offset(x, y);
            if (plain.pixels[at] == focused.pixels[at]) continue;
            ++changed;
            const auto p = logical(focused.transform, x, y);
            if (!inside(outer, p) || inside(inner, p) || focused.pixels[at] != kCyan) ++escaped;
        }
    // Probe complete side runs, leaving the corner joins independent of SDL's
    // fractional rectangle rounding. A misplaced or incomplete ring fails even
    // when it happens to contain a large number of cyan pixels elsewhere.
    for (int side = 0; side < 4; ++side) {
        const float extent = side < 2 ? expected.width : expected.height;
        for (float along = 4.0F; along < extent - 4.0F; along += 1.0F) {
            const float px = side < 2 ? expected.x + along :
                expected.x + (side == 2 ? 0.75F : expected.width - 1.25F);
            const float py = side < 2 ? expected.y + (side == 0 ? 0.75F : expected.height - 1.25F) :
                expected.y + along;
            const int x = static_cast<int>(std::floor(px * focused.transform.x + static_cast<float>(focused.transform.viewport.x)));
            const int y = static_cast<int>(std::floor(py * focused.transform.y + static_cast<float>(focused.transform.viewport.y)));
            if (focused.pixels[focused.offset(x, y)] != kCyan) ++missed;
        }
    }
    check(changed > 0 && escaped == 0 && missed == 0,
          "MIDI focus covers the intended four sides; labels, other controls and panel stay unchanged: escaped=" +
          std::to_string(escaped) + " missed=" + std::to_string(missed));
    ++midi_counts.focused;
}

bool long_row_filled(const Frame& frame, UiRect band) {
    const auto scan = pixel_region(frame, band);
    int left = frame.width, right = 0;
    for (int y = scan.y; y < scan.y + scan.h; ++y)
        for (int x = scan.x; x < scan.x + scan.w; ++x) {
            const auto& p = frame.pixels[frame.offset(x, y)];
            if (inside(band, logical(frame.transform, x, y)) && p[0] >= 140 && p[1] >= 100 && p[2] >= 65) {
                left = std::min(left, x); right = std::max(right, x + 1);
            }
        }
    return static_cast<float>(right - left) >= band.width * frame.transform.x * 0.85F;
}

struct CutGlyph { SDL_Rect bounds{}; std::size_t line{}, character{}, changed{}; };

std::vector<CutGlyph> intersected_glyphs(const Frame& frame, std::span<const LiteralText> text) {
    std::vector<CutGlyph> result;
    const auto& t = frame.transform;
    const SDL_Rect cut{t.viewport.x + t.clip.x, t.viewport.y + t.clip.y, t.clip.w, t.clip.h};
    for (std::size_t line = 0; line < text.size(); ++line) {
        const auto& literal = text[line];
        const auto& font = font_data::kSans;
        const float size = literal.size / static_cast<float>(font.pixel_height);
        float pen = literal.x;
        for (std::size_t index = 0; index < literal.value.size(); ++index) {
            const auto& glyph = font_data::glyph(font, static_cast<unsigned char>(literal.value[index]));
            if (glyph.width != 0 && glyph.height != 0) {
                // Read the frozen asset's destination footprint, including its
                // documented two-pixel gutter for subpixel strokes. SDL's
                // software Copy queue truncates the scaled destination before
                // applying the physical viewport. This locates individual
                // boundary-crossing glyphs; it does not implement blit sampling.
                const int gx = static_cast<float>(glyph.width) * size < 1.0F ? 2 : 0;
                const int gy = static_cast<float>(glyph.height) * size < 1.0F ? 2 : 0;
                const float left = pen + static_cast<float>(glyph.bearing_x - gx) * size;
                const float top = literal.top + static_cast<float>(font.ascent) * size +
                    static_cast<float>(glyph.bearing_y - gy) * size;
                const SDL_Rect bounds{
                    static_cast<int>(left * t.x) + t.viewport.x, static_cast<int>(top * t.y) + t.viewport.y,
                    static_cast<int>(static_cast<float>(glyph.width + 2 * gx) * size * t.x),
                    static_cast<int>(static_cast<float>(glyph.height + 2 * gy) * size * t.y)};
                const bool intersects = bounds.x < cut.x + cut.w && bounds.y < cut.y + cut.h &&
                    bounds.x + bounds.w > cut.x && bounds.y + bounds.h > cut.y;
                const bool crosses = bounds.x < cut.x || bounds.y < cut.y ||
                    bounds.x + bounds.w > cut.x + cut.w || bounds.y + bounds.h > cut.y + cut.h;
                if (intersects && crosses) result.push_back({bounds, line, index, 0});
            }
            pen += static_cast<float>(glyph.advance_64) * size / 64.0F;
        }
    }
    return result;
}

void calibration_modals() {
    struct Scene { int width, height; float scale; UiPresentation presentation; };
    constexpr std::array<Scene, 4> scenes{{
        {960, 700, 1.0F, UiPresentation::Dimensional}, {960, 700, 1.0F, UiPresentation::Flat},
        {1672, 941, 1.0F, UiPresentation::Dimensional}, {960, 700, 1.25F, UiPresentation::Flat}}};
    // Independent reviewed minimum-window anchors, in documented focus order.
    // These do not call the production layout to construct the expected image.
    constexpr std::array<UiRect, 11> anchors{{
        {138, 163, 40, 42}, {782, 163, 40, 42}, {138, 289, 212, 38},
        {374, 289, 212, 38}, {610, 289, 212, 38}, {138, 382, 212, 38},
        {374, 382, 212, 38}, {610, 382, 212, 38}, {138, 560, 252, 38},
        {406, 560, 188, 38}, {738, 74, 84, 32}}};
    constexpr std::array<std::string_view, 3> labels{
        "EXPRESSION MIN", "EXPRESSION MAX", "EXPRESSION DIRECTION"};
    const std::array<std::string, 2> choices{"No input", "Calibration controller"};
    const std::string long_text(2048, 'W');
    const std::array<std::string, 2> long_choices{"No input", "Controller " + long_text};
    for (std::size_t scene = 0; scene < scenes.size(); ++scene) {
        const auto& s = scenes[scene];
        const float dx = static_cast<float>(s.width - 960) / 2.0F;
        const float dy = static_cast<float>(s.height - 700) / 2.0F;
        const auto shifted = [dx, dy](UiRect b) { b.x += dx; b.y += dy; return b; };
        const UiRect panel = shifted({110, 50, 740, 600});
        const UiRect canvas{0, 0, static_cast<float>(s.width), static_cast<float>(s.height)};
        const bool scaled = s.scale != 1.0F;
        const SDL_Rect viewport{scaled ? 13 : 0, scaled ? 11 : 0,
            static_cast<int>(static_cast<float>(s.width) * s.scale), static_cast<int>(static_cast<float>(s.height) * s.scale)};
        Target target(viewport.w + (scaled ? 40 : 0), viewport.h + (scaled ? 40 : 0));
        target.configure(s.scale, viewport);
        const auto model = model_at(s.width, s.height, s.presentation);
        const auto actual = midi_overlay_layout(static_cast<float>(s.width), static_cast<float>(s.height));
        const std::array<UiRect, 11> controls{actual.previous_port, actual.next_port, actual.upper_channel,
            actual.lower_channel, actual.pedal_channel, actual.expression_minimum, actual.expression_maximum,
            actual.expression_direction, actual.apply, actual.disconnect, actual.close};
        const auto same = [](UiRect a, UiRect b) {
            return std::abs(a.x - b.x) < 0.001F && std::abs(a.y - b.y) < 0.001F &&
                std::abs(a.width - b.width) < 0.001F && std::abs(a.height - b.height) < 0.001F;
        };
        check(same(actual.panel, panel) && panel.x >= 50.0F && panel.y >= 50.0F &&
              panel.x + panel.width <= canvas.width - 50.0F && panel.y + panel.height <= canvas.height - 50.0F,
              "740x600 MIDI panel retains complete minimum-window margins");
        bool separated = true;
        for (std::size_t index = 0; index < controls.size(); ++index) {
            const auto& a = controls[index];
            check(same(a, shifted(anchors[index])), "MIDI control matches independent anchor " + std::to_string(index));
            ++midi_counts.controls;
            separated = separated && a.width >= 32.0F && a.height >= 32.0F &&
                a.x > panel.x && a.y > panel.y && a.x + a.width < panel.x + panel.width &&
                a.y + a.height < panel.y + panel.height;
            for (std::size_t other = 0; other < index; ++other) {
                const auto& b = controls[other];
                separated = separated && (a.x + a.width + 4.0F <= b.x || b.x + b.width + 4.0F <= a.x ||
                    a.y + a.height + 4.0F <= b.y || b.y + b.height + 4.0F <= a.y);
            }
        }
        check(separated, "all eleven MIDI targets are contained, usable size and separated by at least four pixels");
        const std::array<UiRect, 3> expression{shifted(anchors[5]), shifted(anchors[6]), shifted(anchors[7])};
        InstrumentViewInfo info;
        info.overlay = ViewOverlay::Midi;
        info.midi_available = true;
        info.midi_open = true;
        info.midi_choices = choices;
        info.selected_midi_port = 1;
        info.midi_backend = "Fixture backend";
        info.midi_status = "Connected for raster acceptance.";
        info.midi_expression_active = true;
        info.active_midi_expression = {7, 111, false};
        const auto glyphs = [&](std::array<std::string, 3> values, bool invalid = false) {
            std::vector<LiteralText> result;
            for (std::size_t index = 0; index < expression.size(); ++index) {
                const auto& b = expression[index];
                result.push_back({std::string(labels[index]), {b.x, b.y - 22.0F, b.width, 16},
                    b.x, b.y - 22.0F, 11, {214, 182, 124}});
                result.push_back({values[index], {b.x + 6, b.y + 6, b.width - 12, b.height - 12},
                    b.x + 106.0F - target.text_width(values[index], 11) / 2.0F, b.y + 12.4F, 11,
                    {242, 231, 207}, {45, 41, 36}});
            }
            result.push_back({"ACTIVE CALIBRATION: min 7 / max 111 / NORMAL", shifted({150, 488, 660, 17}),
                150 + dx, 488 + dy, 11, {157, 187, 143}, {17, 19, 16}});
            result.push_back({invalid ? "Expression minimum must be less than maximum. Change either value before Apply." :
                "Selected calibration: raw 0-127. Arrows adjust; Home / End set bounds.", shifted({138, 432, 684, 18}),
                138 + dx, 432 + dy, 11, invalid ? UiColor{232, 139, 110} : UiColor{166, 159, 142}});
            return result;
        };
        const auto baseline = target.paint(model, info);
        literal_text_checks(target, baseline, glyphs({"0", "127", "NORMAL"}));
        for (const auto& b : expression) {
            const auto material = patch(baseline, {b.x + 8, b.y + 4, 3, b.height - 8}, {45, 41, 36, 255});
            check(material.pixels > 20 && (s.presentation == UiPresentation::Flat ? material.wrong == 0 : material.variations > 0),
                  "each new calibration button retains the chosen Flat or dimensional material");
        }
        info.selected_midi_expression = {20, 100, true};
        const auto changed = target.paint(model, info);
        literal_text_checks(target, changed, glyphs({"20", "100", "INVERTED"}));
        modal_delta(baseline, changed, canvas, expression,
                    "selected endpoint/direction edits change exactly their three controls and preserve active calibration");
        midi_counts.value_changes += 3;
        midi_counts.frames += 2;
        if (scene < 2) {
            auto invalid = info;
            invalid.selected_midi_expression = {100, 100, true};
            const auto invalid_frame = target.paint(model, invalid);
            literal_text_checks(target, invalid_frame, glyphs({"100", "100", "INVERTED"}, true));
            const std::array<UiRect, 3> invalid_regions{expression[0], shifted({138, 432, 684, 18}), shifted(anchors[8])};
            modal_delta(changed, invalid_frame, canvas, invalid_regions,
                        "invalid endpoints retain selected/active readouts and change only minimum, error row and Apply");
            ++midi_counts.invalid; ++midi_counts.frames;
        }
        if (scene == 0 || scaled) {
            auto long_info = info;
            long_info.midi_choices = long_choices;
            long_info.midi_backend = long_text;
            long_info.midi_status = long_text;
            long_info.midi_reconnect_pending = true;
            const auto long_frame = target.paint(model, long_info);
            literal_text_checks(target, long_frame, glyphs({"20", "100", "INVERTED"}));
            const std::array<UiRect, 3> text_regions{shifted({190, 148, 580, 77}),
                shifted({150, 468, 660, 18}), shifted({150, 509, 660, 32})};
            modal_delta(changed, long_frame, panel, text_regions,
                        "long exact port/backend/status and pending state stay in their allotted text bands");
            check(long_row_filled(long_frame, text_regions[1]) &&
                  long_row_filled(long_frame, shifted({150, 509, 660, 15.525F})) &&
                  long_row_filled(long_frame, shifted({150, 524.525F, 660, 16.475F})),
                  "long connection and both status rows retain visible text across their allocated width");
            ++midi_counts.long_text; ++midi_counts.frames;
        }
        const std::size_t first = scene < 2 ? 0 : scaled ? 0 : 2;
        const std::size_t end = scene < 2 ? 3 : first + 1;
        for (std::size_t index = first; index < end; ++index) {
            const auto focused = target.paint(model, info, &controls[5 + index]);
            modal_focus_check(changed, focused, expression[index]);
            ++midi_counts.frames;
            if (!scaled) continue;
            // Deliberately cut through the minimum field and its ring, retaining
            // part of the label/value and neighboring controls in an offset view.
            auto clip_text = glyphs({"20", "100", "INVERTED"});
            clip_text.push_back({"MIDI CONNECTED / Fixture backend", {150, 468, 660, 18},
                150, 468, 12, {157, 187, 143}, {17, 19, 16}});
            clip_text.push_back({"Connected for raster acceptance.", {150, 509, 660, 32},
                150, 509, 11.5F, {242, 231, 207}, {17, 19, 16}});
            clip_text.push_back({"APPLY / CONNECT", {144, 566, 240, 26},
                264.0F - target.text_width("APPLY / CONNECT", 11) / 2.0F, 572.4F, 11,
                {35, 29, 21}, {238, 204, 145}});
            clip_text.push_back({"DISCONNECT", {412, 566, 176, 26},
                500.0F - target.text_width("DISCONNECT", 11) / 2.0F, 572.4F, 11,
                {242, 231, 207}, {45, 41, 36}});
            clip_text.push_back({"Apply uses selected settings; reconnect and Disconnect release MIDI-owned notes.",
                {138, 609, 684, 16}, 138, 609, 11, {166, 159, 142}});
            clip_text.push_back({"Tab / Shift+Tab selects a control. Enter activates. Escape closes.",
                {138, 628, 684, 14}, 138, 628, 10.5F, {166, 159, 142}});
            const auto full_plate = target.literal_plate(clip_text);
            const SDL_Rect cut{305, 460, 700, 340};
            target.configure(s.scale, viewport, &cut);
            const auto clipped = target.paint(model, info, &controls[5 + index]);
            const auto cut_plate = target.literal_plate(clip_text);
            auto cut_glyphs = intersected_glyphs(clipped, clip_text);
            std::size_t mismatches = 0, surviving_focus = 0, hidden_focus = 0;
            std::size_t unexplained = 0, wrong_literal = 0, wrong_difference_set = 0, partial_pixels = 0;
            std::string first_wrong;
            for (int y = 0; y < clipped.height; ++y)
                for (int x = 0; x < clipped.width; ++x) {
                    const auto at = clipped.offset(x, y);
                    if (visible(clipped.transform, x, y)) {
                        const bool different = focused.pixels[at] != clipped.pixels[at];
                        if (different) ++mismatches;
                        const auto owner = std::find_if(cut_glyphs.begin(), cut_glyphs.end(), [x, y](const CutGlyph& glyph) {
                            const auto& b = glyph.bounds;
                            return x >= b.x && y >= b.y && x < b.x + b.w && y < b.y + b.h;
                        });
                        bool wrong = false;
                        if (owner == cut_glyphs.end()) {
                            if (different) { ++unexplained; wrong = true; }
                        } else {
                            ++partial_pixels;
                            if (different) ++owner->changed;
                            if (focused.pixels[at] != full_plate.pixels[at] || clipped.pixels[at] != cut_plate.pixels[at]) {
                                ++wrong_literal; wrong = true;
                            }
                            if (different != (full_plate.pixels[at] != cut_plate.pixels[at])) {
                                ++wrong_difference_set; wrong = true;
                            }
                        }
                        if (wrong && first_wrong.empty()) {
                            std::ostringstream sample;
                            sample << " first_wrong=" << x << ',' << y << " full/cut/literal_full/literal_cut=";
                            for (const auto* frame : {&focused, &clipped, &full_plate, &cut_plate}) {
                                const auto& pixel = frame->pixels[at];
                                sample << static_cast<int>(pixel[0]) << ',' << static_cast<int>(pixel[1]) << ','
                                       << static_cast<int>(pixel[2]) << ';';
                            }
                            first_wrong = sample.str();
                        }
                        if (clipped.pixels[at] == kCyan) ++surviving_focus;
                    } else if (focused.pixels[at] == kCyan) ++hidden_focus;
                }
            // SDL 2.32.10 rescales a rounded source subrectangle when a caller
            // clip bisects a glyph texture. Require exact literal RGBA and the
            // exact changed-pixel set there; every complete glyph, nontext pixel
            // and focus pixel must remain identical. No text-band exclusion or
            // numeric pixel tolerance is applied to this cut case.
            check(!cut_glyphs.empty() && partial_pixels > 0 && unexplained == 0 && wrong_literal == 0 &&
                  wrong_difference_set == 0 && surviving_focus > 0 && hidden_focus > 0,
                  "fractional cut preserves complete glyphs/primitives/focus and exactly matches literal boundary glyphs: resampled=" +
                  std::to_string(mismatches) + " unexplained=" + std::to_string(unexplained) +
                  " literal_mismatches=" + std::to_string(wrong_literal) + " difference_set_mismatches=" +
                  std::to_string(wrong_difference_set) + first_wrong);
            midi_counts.intersected_glyphs += cut_glyphs.size();
            midi_counts.resampled_pixels += mismatches;
            midi_counts.unexplained_pixels += unexplained;
            midi_counts.literal_mismatches += wrong_literal + wrong_difference_set;
            for (const auto& glyph : cut_glyphs) {
                const auto& b = glyph.bounds;
                std::ostringstream row;
                row << "{\"line\":" << glyph.line << ",\"character\":" << glyph.character
                    << ",\"ascii\":" << static_cast<unsigned>(clip_text[glyph.line].value[glyph.character])
                    << ",\"physical_rect\":[" << b.x << ',' << b.y << ',' << b.w << ',' << b.h
                    << "],\"changed_pixels\":" << glyph.changed << '}';
                midi_clip_results.push_back(row.str());
            }
            ++midi_counts.clipped; ++midi_counts.frames;
        }
        ++midi_counts.scenes;
    }
    check(midi_counts.scenes == 4 && midi_counts.frames == 21 && midi_counts.controls == 44 &&
          midi_counts.glyphs == 96 && midi_counts.value_changes == 12 && midi_counts.focused == 8 &&
          midi_counts.invalid == 2 && midi_counts.long_text == 2 && midi_counts.clipped == 1,
          "all bounded calibration-modal raster cases executed");
}

struct HeaderInk {
    UiRect bounds{};
    std::size_t pixels{}, letters{}, outside_header{}, on_controls{};
};

HeaderInk header_ink(const Frame& frame, const UiLayout& layout, UiRect region) {
    HeaderInk result;
    int left = frame.width, right = 0, top = frame.height, bottom = 0;
    std::vector<bool> columns(static_cast<std::size_t>(frame.width));
    for (int y = 0; y < frame.height; ++y)
        for (int x = 0; x < frame.width; ++x) {
            const auto p = logical(frame.transform, x, y);
            const auto pixel = frame.pixels[frame.offset(x, y)];
            // The independent reference review's warm-light mask, applied to
            // native pixels without image resampling or production metrics.
            if (!inside(region, p) || pixel[0] < 130 || pixel[1] < 105 ||
                pixel[0] < pixel[1] || pixel[2] * 10 > pixel[0] * 9) continue;
            ++result.pixels;
            left = std::min(left, x); right = std::max(right, x + 1);
            top = std::min(top, y); bottom = std::max(bottom, y + 1);
            columns[static_cast<std::size_t>(x)] = true;
            if (!inside(layout.header, p)) ++result.outside_header;
            for (std::size_t index = 0; index < layout.control_count; ++index)
                if (ui_control_visible(layout, layout.controls[index].id) &&
                    inside(layout.controls[index].bounds, p)) ++result.on_controls;
        }
    bool previous = false;
    for (const bool ink : columns) {
        if (ink && !previous) ++result.letters;
        previous = ink;
    }
    if (result.pixels != 0) {
        result.bounds = {(static_cast<float>(left) - static_cast<float>(frame.transform.viewport.x)) / frame.transform.x,
                         (static_cast<float>(top) - static_cast<float>(frame.transform.viewport.y)) / frame.transform.y,
                         static_cast<float>(right - left) / frame.transform.x,
                         static_cast<float>(bottom - top) / frame.transform.y};
    }
    return result;
}

void reference_headers() {
    std::size_t complete = 0, clipped = 0;
    for (const auto size : {std::array<int, 2>{1400, 820}, std::array<int, 2>{1672, 941}})
        for (const float scale : {1.0F, 1.25F, 1.5F, 2.0F}) {
            const float width = static_cast<float>(size[0]);
            const int viewport_width = static_cast<int>(std::ceil(width * scale));
            const int surface_width = std::min(1920, viewport_width + 20);
            Target target(surface_width, static_cast<int>(std::ceil(128.0F * scale)) + 14);
            const SDL_Rect viewport{(surface_width - viewport_width) / 2, 7, viewport_width,
                static_cast<int>(std::ceil(static_cast<float>(size[1]) * scale))};
            target.configure(scale, viewport);
            const UiRect title_region{width / 2.0F - 260.0F, 16.0F, 520.0F, 46.0F};
            const UiRect caption_region{width / 2.0F - 220.0F, 64.0F, 440.0F, 24.0F};
            auto model = model_at(size[0], size[1], UiPresentation::Dimensional);
            for (const auto workspace : {UiWorkspace::Play, UiWorkspace::Rotary, UiWorkspace::Service}) {
                require(model.set_workspace(workspace), "select reference-header workspace");
                const bool whole_composition = workspace == UiWorkspace::Play;
                const float sx = width / 1672.0F;
                const float sy = static_cast<float>(size[1]) / 941.0F;
                const float f = std::min(sx, sy);
                // Independent canonical regions. Geometry is anisotropically
                // mapped, but the font uses the smaller scale on both axes.
                const UiRect observed_title = whole_composition ?
                    UiRect{576 * sx, 16 * sy, 520 * sx, 46 * sy} : title_region;
                const UiRect observed_caption = whole_composition ?
                    UiRect{616 * sx, 64 * sy, 440 * sx, 24 * sy} : caption_region;
                const auto frame = target.paint(model);
                const auto title = header_ink(frame, model.layout(), observed_title);
                const auto caption = header_ink(frame, model.layout(), observed_caption);
                const auto& t = title.bounds;
                const auto& c = caption.bounds;
                // Keep the original measured ink tolerances. Active Play maps
                // the canonical text origins and scales type isotropically;
                // Rotary and Service retain their exact historical assertions.
                if (whole_composition) {
                    check(title.pixels > 1000 && std::abs(t.width - 464 * f) <= 3.0F &&
                          std::abs(t.height - 33 * f) <= 1.0F &&
                          std::abs(t.y - (11.5F * sy + 8.5F * f)) <= 1.0F &&
                          std::abs(t.x + t.width / 2.0F - (width / 2.0F - f)) <= 2.0F,
                          "active title ink meets independently scaled reference size/top/center");
                    check(caption.pixels > 300 && std::abs(c.width - 371 * sx) <= 4.0F &&
                          std::abs(c.height - 12 * f) <= 1.0F &&
                          std::abs(c.y - (67.5F * sy + 3.5F * f)) <= 1.0F &&
                          std::abs(c.x + c.width / 2.0F - (width / 2.0F - .5F * f)) <= 2.0F,
                          "active truthful caption ink meets independently scaled reference hierarchy");
                } else {
                    check(title.pixels > 1000 && std::abs(t.width - 464.0F) <= 3.0F &&
                          std::abs(t.height - 33.0F) <= 1.0F && std::abs(t.y - 20.0F) <= 1.0F &&
                          std::abs(t.x + t.width / 2.0F - (width / 2.0F - 1.0F)) <= 2.0F,
                          "wide title ink meets independently measured reference size/top/center");
                    check(caption.pixels > 300 && std::abs(c.width - 371.0F) <= 4.0F &&
                          std::abs(c.height - 12.0F) <= 1.0F && std::abs(c.y - 71.0F) <= 1.0F &&
                          std::abs(c.x + c.width / 2.0F - (width / 2.0F - 0.5F)) <= 2.0F,
                          "truthful caption ink meets independently measured reference hierarchy");
                }
                check(caption.letters == 15 && title.outside_header == 0 && caption.outside_header == 0 &&
                      title.on_controls == 0 && caption.on_controls == 0 &&
                      t.y + t.height < c.y,
                      "all fifteen caption letters remain distinct; both lines fit apart from controls");
                const auto flat = std::find_if(model.layout().controls.begin(),
                    model.layout().controls.begin() + static_cast<std::ptrdiff_t>(model.layout().control_count),
                    [](const UiControlGeometry& control) { return control.id.kind == UiControlKind::Presentation; });
                require(flat != model.layout().controls.begin() + static_cast<std::ptrdiff_t>(model.layout().control_count),
                        "header retains Flat control");
                check(c.x + c.width <= flat->bounds.x - 10.0F,
                      "caption retains at least ten logical pixels before Flat");
                std::ostringstream row;
                row << "{\"size\":[" << size[0] << ',' << size[1] << "],\"scale\":" << scale
                    << ",\"workspace\":" << static_cast<unsigned>(workspace)
                    << ",\"title\":[" << t.x << ',' << t.y << ',' << t.width << ',' << t.height
                    << "],\"caption\":[" << c.x << ',' << c.y << ',' << c.width << ',' << c.height
                    << "],\"caption_letters\":" << caption.letters << '}';
                header_results.push_back(row.str());
                ++complete;
            }
            // Cut through both title and caption with a caller-owned clip.
            // Target::paint also checks every pixel outside that physical clip.
            const SDL_Rect cut{static_cast<int>(width * scale / 2.0F),
                static_cast<int>(25.0F * scale), static_cast<int>(260.0F * scale),
                static_cast<int>(60.0F * scale)};
            target.configure(scale, viewport, &cut);
            const auto frame = target.paint(model);
            const auto title = header_ink(frame, model.layout(), title_region);
            const auto caption = header_ink(frame, model.layout(), caption_region);
            check(title.pixels > 300 && caption.pixels > 100 &&
                  title.bounds.x >= width / 2.0F && caption.bounds.x >= width / 2.0F &&
                  title.bounds.y >= 24.0F && title.outside_header == 0 && caption.outside_header == 0,
                  "fractional clipped header retains visible ink only on the surviving halves");
            ++clipped;
            // Add the changed Play header to the same caller-clip gate. The
            // existing Service clip above remains unchanged and still runs.
            require(model.set_workspace(UiWorkspace::Play), "select active clipped header");
            const float sx = width / 1672.0F;
            const float sy = static_cast<float>(size[1]) / 941.0F;
            const SDL_Rect active_cut{static_cast<int>(width * scale / 2.0F),
                static_cast<int>(25.0F * sy * scale), static_cast<int>(260.0F * sx * scale),
                static_cast<int>(60.0F * sy * scale)};
            target.configure(scale, viewport, &active_cut);
            const auto active_frame = target.paint(model);
            const auto active_title = header_ink(active_frame, model.layout(),
                {576 * sx, 16 * sy, 520 * sx, 46 * sy});
            const auto active_caption = header_ink(active_frame, model.layout(),
                {616 * sx, 64 * sy, 440 * sx, 24 * sy});
            check(active_title.pixels > 300 && active_caption.pixels > 100 &&
                  active_title.bounds.x >= width / 2.0F && active_caption.bounds.x >= width / 2.0F &&
                  active_title.bounds.y >= 24.0F * sy &&
                  active_title.outside_header == 0 && active_caption.outside_header == 0,
                  "active fractional clipped header retains only surviving title/caption ink");
            ++clipped;
        }
    check(complete == 24 && clipped == 16, "all header sizes/workspaces/scales and old/new cut clips executed");
}
} // namespace

int main() {
    SDL_SetMainReady();
    std::size_t legacy_checks = 0, header_checks = 0, midi_checks = 0;
    try {
        require(SDL_Init(0) == 0, "initialize SDL without window/audio subsystems");
        key_matrix(960, 700, false);
        key_matrix(1400, 820, true);
        cut_clip_matrix();
        compact_status();
        overlays();
        check(counts.frames == 56 && counts.states == 56 && counts.clip_frames == 56 &&
              counts.held_keys == 588 && counts.focused_keys == 24 && counts.surfaces == 72 &&
              counts.corners == 8 && counts.cut_clips == 4 && counts.status_frames == 4 &&
              counts.overlay_panels == 12 && counts.overlay_buttons == 60,
              "all focused material acceptance cases executed");
        legacy_checks = counts.checks;
        check(legacy_checks == 901, "all original 901 material assertions remain executed");
        reference_headers();
        header_checks = counts.checks - legacy_checks;
        calibration_modals();
        midi_checks = counts.checks - legacy_checks - header_checks;
        SDL_Quit();
    } catch (const std::exception& error) {
        std::cerr << "Material acceptance setup failed: " << error.what() << '\n';
        SDL_Quit();
        return EXIT_FAILURE;
    }
    std::cout << "{\"checks\":" << counts.checks << ",\"failures\":" << counts.failures
        << ",\"frames\":" << counts.frames << ",\"state_checks\":" << counts.states
        << ",\"clip_frames\":" << counts.clip_frames << ",\"outside_pixels\":" << counts.outside_pixels
        << ",\"held_keys\":" << counts.held_keys << ",\"focused_keys\":" << counts.focused_keys
        << ",\"surfaces\":" << counts.surfaces << ",\"sloped_corners\":" << counts.corners
        << ",\"cut_clips\":" << counts.cut_clips << ",\"status_frames\":" << counts.status_frames
        << ",\"status_ink_pixels\":" << counts.status_ink << ",\"last_row_ink_pixels\":" << counts.last_row_ink
        << ",\"minimum_natural_top_front_srgb_levels\":" << static_cast<double>(minimum_contrast[0])
        << ",\"minimum_accidental_top_front_srgb_levels\":" << static_cast<double>(minimum_contrast[1])
        << ",\"overlay_panels\":" << counts.overlay_panels << ",\"overlay_buttons\":" << counts.overlay_buttons
        << ",\"backend\":\"SDL software surface; no window/audio\",\"overlays\":[";
    for (std::size_t index = 0; index < overlay_results.size(); ++index)
        std::cout << (index == 0 ? "" : ",") << overlay_results[index];
    std::cout << "],\"legacy_checks\":" << legacy_checks
              << ",\"header_checks\":" << header_checks << ",\"headers\":[";
    for (std::size_t index = 0; index < header_results.size(); ++index)
        std::cout << (index == 0 ? "" : ",") << header_results[index];
    std::cout << "],\"calibration_modal\":{\"checks\":" << midi_checks
              << ",\"scenes\":" << midi_counts.scenes << ",\"frames\":" << midi_counts.frames
              << ",\"controls\":" << midi_counts.controls << ",\"literal_glyph_regions\":" << midi_counts.glyphs
              << ",\"changed_values\":" << midi_counts.value_changes << ",\"focused_controls\":" << midi_counts.focused
              << ",\"invalid_frames\":" << midi_counts.invalid << ",\"long_text_frames\":" << midi_counts.long_text
              << ",\"clipped_frames\":" << midi_counts.clipped << ",\"intersected_glyphs\":" << midi_counts.intersected_glyphs
              << ",\"resampled_pixels\":" << midi_counts.resampled_pixels << ",\"unexplained_pixels\":" << midi_counts.unexplained_pixels
              << ",\"literal_mismatches\":" << midi_counts.literal_mismatches << ",\"cut_glyphs\":[";
    for (std::size_t index = 0; index < midi_clip_results.size(); ++index)
        std::cout << (index == 0 ? "" : ",") << midi_clip_results[index];
    std::cout << "]}}\n";
    return counts.failures == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
