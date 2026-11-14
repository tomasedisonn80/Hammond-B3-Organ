#include "InstrumentView.h"

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

    Frame paint(const UiModel& model, const InstrumentViewInfo& info = {}) {
        const auto before = state(renderer_.get());
        paint_instrument(drawing_, model, info);
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
} // namespace

int main() {
    SDL_SetMainReady();
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
    std::cout << "]}\n";
    return counts.failures == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
