#include "InstrumentView.h"

#include <SDL.h>

#include <algorithm>
#include <array>
#include <charconv>
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

#ifdef _WIN32
#include <cstdio>
#include <fcntl.h>
#include <io.h>
#endif

// Ordinary CTest uses only current source. For one-time paired qualification,
// compile this SAME harness against the identified historical UiModel.cpp and
// InstrumentView.cpp, then compare --case streams with the current executable.
// No old geometry formula, painter or historical file is embedded here.
namespace {
using namespace hammond;
using namespace hammond::standalone;
using Pixel = std::array<std::uint8_t, 4>;

struct Totals {
    std::size_t cases{}, checks{}, glyphs{}, ink_pixels{}, focus_cases{}, clips{};
} totals;

void require(bool condition, std::string_view message) {
    ++totals.checks;
    if (!condition) throw std::runtime_error(std::string(message) + ": " + SDL_GetError());
}

struct Case {
    float width{1672}, height{941}, scale{1};
    unsigned values{}, focus{}, route{};
    bool pending{};
    UiPresentation presentation{UiPresentation::Dimensional};
    UiWorkspace workspace{UiWorkspace::Play};
    unsigned clip{}; // 1 physical clip, 2 logical clip; both cross tablet edges.
};

std::vector<Case> cases() {
    std::vector<Case> result;
    for (unsigned value = 0; value < 16; ++value)
        result.push_back({1672, 941, 1, value, value % 4, value % 4, value % 2 != 0});
    for (const float scale : {1.5F, 2.0F})
        result.push_back({1672, 941, scale, 15, 3, 0, true});
    for (const auto size : {UiPoint{1400, 820}, UiPoint{1920, 1080}})
        for (const float scale : {1.0F, 1.5F, 2.0F})
            result.push_back({size.x, size.y, scale, 9, 1, 1, false});
    for (const auto size : {UiPoint{1399, 820}, UiPoint{1400, 819}})
        for (const float scale : {1.0F, 1.5F, 2.0F})
            result.push_back({size.x, size.y, scale, 6, 2, 2, true});
    for (const auto size : {UiPoint{960, 700}, UiPoint{1280, 900}})
        for (const float scale : {1.0F, 2.0F})
            result.push_back({size.x, size.y, scale, 5, 0, 3, false});
    for (const auto size : {UiPoint{1672, 941}, UiPoint{1920, 1080}})
        for (const float scale : {1.0F, 1.5F, 2.0F})
            result.push_back({size.x, size.y, scale, 10, 3, 0, true, UiPresentation::Flat});
    for (const auto workspace : {UiWorkspace::Rotary, UiWorkspace::Service})
        for (const auto presentation : {UiPresentation::Dimensional, UiPresentation::Flat})
            for (const float scale : {1.0F, 1.5F, 2.0F})
                result.push_back({1672, 941, scale, 11, 1, 2, false, presentation, workspace});
    for (const auto size : {UiPoint{1400.25F, 820.75F}, UiPoint{1672.5F, 941.25F}})
        result.push_back({size.x, size.y, 1.5F, 14, 2, 0, false});
    for (const float scale : {1.0F, 1.5F, 2.0F})
        for (const unsigned clip : {1U, 2U})
            result.push_back({1672, 941, scale, 13, 0, 0, true,
                              UiPresentation::Dimensional, UiWorkspace::Play, clip});
    // These straddle the separate-eligibility-line threshold independently of
    // the activation threshold. Neither expected height is computed here.
    for (const float height : {933.25F, 933.5F})
        for (const float scale : {1.0F, 1.5F, 2.0F})
            result.push_back({1672, height, scale, 3, 2, 3, true});
    return result;
}

UiModel state_for(const Case& test) {
    UiModel model;
    require(model.resize(test.width, test.height) && model.set_presentation(test.presentation),
            "admitted fixed geometry");
    SessionSnapshot snapshot;
    snapshot.controls = model.view().controls;
    for (auto& manual : snapshot.controls.drawbars)
        for (auto& bank : manual)
            for (std::size_t i = 0; i < bank.size(); ++i) bank[i] = static_cast<std::uint8_t>(i % 9);
    snapshot.controls.pedal_drawbars = {3, 7};
    snapshot.controls.expression = 0.625;
    snapshot.controls.percussion = {
        (test.values & 1U) != 0,
        (test.values & 2U) != 0 ? PercussionHarmonic::Third : PercussionHarmonic::Second,
        (test.values & 4U) != 0 ? PercussionVolume::Soft : PercussionVolume::Normal,
        (test.values & 8U) != 0 ? PercussionDecay::Fast : PercussionDecay::Slow};
    constexpr std::array<unsigned, 4> selections{11, 10, 2, 0};
    ControlState applied;
    require(applied.restore(snapshot.controls) && applied.select_preset(Manual::Upper,
        static_cast<PresetSelection>(selections[test.route])), "fixed applied route");
    snapshot.controls = applied.snapshot();
    snapshot.held_keys[0][24] = snapshot.held_keys[1][36] = true;
    snapshot.held_pedals[12] = true;
    snapshot.frame_clock = 38400;
    snapshot.sample_rate = 48000;
    snapshot.peak = 0.125F;
    snapshot.prepared = snapshot.running = true;
    snapshot.publication_revision = 4;
    model.observe(snapshot);
    ControlSnapshot expected = snapshot.controls;
    if (test.pending) {
        const unsigned desired = test.route == 0 ? 10U : 11U;
        require(model.activate({UiControlKind::PresetKey, Manual::Upper, DrawbarBank::A,
            static_cast<std::uint8_t>(desired)}).count == 1, "fixed pending route");
        ControlState requested;
        require(requested.restore(expected) && requested.select_preset(Manual::Upper,
            static_cast<PresetSelection>(desired)), "independent requested state");
        expected = requested.snapshot();
    }
    const UiControlId focus{UiControlKind::Percussion, Manual::Upper, DrawbarBank::A,
                            static_cast<std::uint8_t>(test.focus)};
    for (unsigned i = 0; i < 72 && model.view().focus != focus; ++i) {
        require(model.key({UiKey::Tab, true}).count == 0 &&
                model.key({UiKey::Tab, false}).count == 0, "focus emits no commands");
    }
    require(model.view().focus == focus, "same semantic focus in each historical/current model");
    require(model.set_workspace(test.workspace), "fixed workspace");
    require(model.view().controls == expected && model.view().applied.controls == snapshot.controls &&
            model.view().controls_pending == test.pending &&
            model.view().applied.frame_clock == snapshot.frame_clock &&
            model.view().applied.held_keys == snapshot.held_keys &&
            model.view().applied.held_pedals == snapshot.held_pedals,
            "painting receives identical desired/applied controls, clock and held notes");
    return model;
}

bool active(const Case& test) {
    return test.workspace == UiWorkspace::Play && test.presentation == UiPresentation::Dimensional &&
           test.width >= 1400 && test.height >= 820;
}
bool equal(SDL_Rect a, SDL_Rect b) { return a.x == b.x && a.y == b.y && a.w == b.w && a.h == b.h; }
struct Transform {
    float sx{}, sy{};
    SDL_Rect viewport{}, clip{}, logical_viewport{}, logical_clip{};
    bool clipped{};
    SDL_BlendMode blend{};
};
Transform transform(SDL_Renderer* renderer) {
    Transform result;
    SDL_RenderGetScale(renderer, &result.sx, &result.sy);
    SDL_RenderGetViewport(renderer, &result.logical_viewport);
    SDL_RenderGetClipRect(renderer, &result.logical_clip);
    result.clipped = SDL_RenderIsClipEnabled(renderer) == SDL_TRUE;
    require(SDL_GetRenderDrawBlendMode(renderer, &result.blend) == 0, "query blend");
    require(SDL_RenderSetScale(renderer, 1, 1) == 0, "query physical coordinates");
    SDL_RenderGetViewport(renderer, &result.viewport);
    SDL_RenderGetClipRect(renderer, &result.clip);
    require(SDL_RenderSetScale(renderer, result.sx, result.sy) == 0, "restore scale");
    return result;
}
bool equal(const Transform& a, const Transform& b) {
    return a.sx == b.sx && a.sy == b.sy && equal(a.viewport, b.viewport) && equal(a.clip, b.clip) &&
           equal(a.logical_viewport, b.logical_viewport) && equal(a.logical_clip, b.logical_clip) &&
           a.clipped == b.clipped && a.blend == b.blend;
}
bool visible(const Transform& t, int x, int y) {
    const int xx = x - t.viewport.x, yy = y - t.viewport.y;
    return xx >= 0 && yy >= 0 && xx < t.viewport.w && yy < t.viewport.h &&
           (!t.clipped || (xx >= t.clip.x && yy >= t.clip.y &&
                          xx < t.clip.x + t.clip.w && yy < t.clip.y + t.clip.h));
}
struct Frame {
    int width{}, height{};
    Transform coordinates;
    std::vector<Pixel> pixels;
    std::size_t at(int x, int y) const {
        return static_cast<std::size_t>(y) * static_cast<std::size_t>(width) + static_cast<std::size_t>(x);
    }
};
class Target {
public:
    explicit Target(const Case& test) :
        width_(static_cast<int>(std::ceil(test.width * test.scale)) + (test.clip ? 14 : 0)),
        height_(static_cast<int>(std::ceil(test.height * test.scale)) + (test.clip ? 14 : 0)),
        surface_(SDL_CreateRGBSurfaceWithFormat(0, width_, height_, 32, SDL_PIXELFORMAT_RGBA32), SDL_FreeSurface),
        renderer_(surface_ ? SDL_CreateSoftwareRenderer(surface_.get()) : nullptr, SDL_DestroyRenderer),
        drawing_(renderer_.get()) {
        require(width_ <= 3900 && height_ <= 2200 && surface_ && renderer_, "bounded software target");
        std::string error;
        require(drawing_.initialize(error), "initialize identical fonts/art");
        const SDL_Rect viewport{test.clip ? 7 : 0, test.clip ? 7 : 0,
            static_cast<int>(std::ceil(test.width * test.scale)),
            static_cast<int>(std::ceil(test.height * test.scale))};
        require(SDL_RenderSetViewport(renderer_.get(), &viewport) == 0, "viewport");
        if (test.clip == 1) {
            const SDL_Rect clip{static_cast<int>(180 * test.scale), static_cast<int>(138 * test.scale),
                static_cast<int>(275 * test.scale), static_cast<int>(77 * test.scale)};
            require(SDL_RenderSetClipRect(renderer_.get(), &clip) == 0, "physical boundary clip");
        }
        require(SDL_RenderSetScale(renderer_.get(), test.scale, test.scale) == 0, "scale");
        if (test.clip == 2) {
            const SDL_Rect clip{161, 174, 252, 41};
            require(SDL_RenderSetClipRect(renderer_.get(), &clip) == 0, "logical boundary clip");
        }
    }
    Frame paint(const UiModel& model) {
        const auto before = transform(renderer_.get());
        InstrumentViewInfo info;
        info.audio_running = true;
        info.sample_rate = 48000;
        info.buffer_frames = 512;
        info.audio_driver = "fixed-software-fixture";
        info.device_name = "fixed copied state";
        info.status_message = "Percussion raster qualification";
        paint_instrument(drawing_, model, info);
        require(equal(before, transform(renderer_.get())), "paint preserves caller renderer state");
        return read(before);
    }
    Frame text(std::string_view value, UiRect box, float requested, TextFace face,
               std::vector<UiRect>& glyphs) {
        const auto coordinates = transform(renderer_.get());
        drawing_.clear({0, 0, 0, 0});
        float size = std::min(requested, box.height / 1.2F);
        const float width = drawing_.text_width(value, size, face);
        if (width > box.width - 6 && width > 0) size *= std::max(0.1F, box.width - 6) / width;
        const float left = box.x + (box.width - drawing_.text_width(value, size, face)) / 2;
        const float top = box.y + (box.height - size * 1.2F) / 2;
        drawing_.text(value, left, top, size, {255, 255, 255}, face);
        float x = left;
        for (const char character : value) {
            const float advance = drawing_.text_width(std::string_view(&character, 1), size, face);
            if (character != ' ') glyphs.push_back({x, box.y, advance, box.height});
            x += advance;
        }
        return read(coordinates);
    }
private:
    Frame read(const Transform& coordinates) {
        require(SDL_RenderFlush(renderer_.get()) == 0 && SDL_LockSurface(surface_.get()) == 0, "read pixels");
        Frame frame{width_, height_, coordinates, std::vector<Pixel>(
            static_cast<std::size_t>(width_) * static_cast<std::size_t>(height_))};
        const auto* input = static_cast<const std::uint8_t*>(surface_->pixels);
        for (int y = 0; y < height_; ++y)
            for (int x = 0; x < width_; ++x) {
                const auto* p = input + static_cast<std::size_t>(y) * static_cast<std::size_t>(surface_->pitch) +
                    static_cast<std::size_t>(x) * 4;
                frame.pixels[frame.at(x, y)] = {p[0], p[1], p[2], p[3]};
            }
        SDL_UnlockSurface(surface_.get());
        return frame;
    }
    int width_, height_;
    std::unique_ptr<SDL_Surface, decltype(&SDL_FreeSurface)> surface_;
    std::unique_ptr<SDL_Renderer, decltype(&SDL_DestroyRenderer)> renderer_;
    Drawing drawing_;
};

double light(Pixel p) { return .2126 * p[0] + .7152 * p[1] + .0722 * p[2]; }
void literal_ink(Target& target, const Frame& actual, std::string_view value, UiRect box,
                 float size, TextFace face, bool dark) {
    std::vector<UiRect> glyphs;
    const auto expected = target.text(value, box, size, face, glyphs);
    const auto& t = actual.coordinates;
    for (const auto& glyph : glyphs) {
        std::size_t samples = 0, matches = 0;
        const int left = std::max(0, static_cast<int>(std::floor(glyph.x * t.sx + static_cast<float>(t.viewport.x))));
        const int right = std::min(actual.width, static_cast<int>(std::ceil((glyph.x + glyph.width) * t.sx + static_cast<float>(t.viewport.x))));
        const int top = std::max(0, static_cast<int>(std::floor(glyph.y * t.sy + static_cast<float>(t.viewport.y))));
        const int bottom = std::min(actual.height, static_cast<int>(std::ceil((glyph.y + glyph.height) * t.sy + static_cast<float>(t.viewport.y))));
        for (int y = top; y < bottom; ++y)
            for (int x = left; x < right; ++x) {
                const auto at = actual.at(x, y);
                if (light(expected.pixels[at]) < 180) continue;
                ++samples;
                if (dark ? light(actual.pixels[at]) < 130 : light(actual.pixels[at]) > 90) ++matches;
            }
        require(samples > 0 && samples == matches, "every literal glyph has complete contrasting raster ink");
        ++totals.glyphs;
        totals.ink_pixels += samples;
    }
}

void ordinary_acceptance(const Case& test, const UiModel& model, Target& target, const Frame& frame) {
    if (test.clip) {
        const Pixel clear = test.presentation == UiPresentation::Flat ? Pixel{18, 21, 20, 255} : Pixel{85, 54, 36, 255};
        for (int y = 0; y < frame.height; ++y)
            for (int x = 0; x < frame.width; ++x)
                if (!visible(frame.coordinates, x, y))
                    require(frame.pixels[frame.at(x, y)] == clear, "no paint escapes caller clip/viewport");
        ++totals.clips;
        return;
    }
    if (!active(test)) return;
    const auto& layout = model.layout();
    constexpr std::array<std::string_view, 4> captions{"PERC", "HARM", "VOL", "DECAY"};
    const std::array<std::string_view, 4> values{
        (test.values & 1U) != 0 ? "ON" : "OFF", (test.values & 2U) != 0 ? "3RD" : "2ND",
        (test.values & 4U) != 0 ? "SOFT" : "NORM", (test.values & 8U) != 0 ? "FAST" : "SLOW"};
    for (const auto& control : std::span(layout.controls).first(layout.control_count)) {
        if (control.id.kind != UiControlKind::Percussion) continue;
        literal_ink(target, frame, captions[control.id.index], control.label_bounds, 10.5F, TextFace::Serif, false);
        literal_ink(target, frame, values[control.id.index], control.value_bounds, 17, TextFace::Serif, true);
        if (control.id.index == test.focus) {
            std::size_t cyan = 0;
            const auto& t = frame.coordinates;
            for (int y = 0; y < frame.height; ++y)
                for (int x = 0; x < frame.width; ++x) {
                    const UiPoint p{(static_cast<float>(x) + .5F - static_cast<float>(t.viewport.x)) / t.sx,
                                    (static_cast<float>(y) + .5F - static_cast<float>(t.viewport.y)) / t.sy};
                    if (control.bounds.contains(p) && frame.pixels[frame.at(x, y)] == Pixel{165, 228, 223, 255}) ++cyan;
                }
            require(cyan > 0, "focused semantic tablet retains actual cyan ink");
            ++totals.focus_cases;
        }
    }
    const auto p = layout.performance_panel;
    const float group = p.width * .46F;
    const bool eligible = test.route == 0;
    if (p.height >= 104) {
        literal_ink(target, frame, eligible ? "UPPER B ROUTE ACTIVE" : "REQUIRES UPPER B",
            {p.x + 12, p.y + p.height - 16, group - 24, 11}, 9, TextFace::Sans, false);
    } else {
        literal_ink(target, frame, eligible ? "PERCUSSION / UPPER B ACTIVE" : "PERCUSSION / REQUIRES UPPER B",
            {p.x + 17, p.y + 3, group - 34, 18}, 10.5F, TextFace::Serif, false);
    }
}

void rect(std::ostream& out, UiRect r) { out << '[' << r.x << ',' << r.y << ',' << r.width << ',' << r.height << ']'; }
void stream(std::size_t index, const Case& test, const UiModel& model, const Frame& frame) {
    std::ostringstream out;
    out << std::setprecision(std::numeric_limits<float>::max_digits10)
        << "{\"schema\":1,\"case\":" << index << ",\"width\":" << frame.width << ",\"height\":" << frame.height
        << ",\"scale\":" << test.scale << ",\"offset\":" << (test.clip ? 7 : 0)
        << ",\"active\":" << (active(test) ? "true" : "false") << ",\"fixture\":["
        << test.width << ',' << test.height << ',' << test.values << ',' << test.focus << ',' << test.route << ','
        << test.pending << ',' << static_cast<unsigned>(test.presentation) << ',' << static_cast<unsigned>(test.workspace)
        << ',' << test.clip << "],\"regions\":[";
    bool first = true;
    const auto add = [&](UiRect value) {
        if (!first) out << ',';
        first = false;
        rect(out, value);
    };
    for (const auto& control : std::span(model.layout().controls).first(model.layout().control_count))
        if (control.id.kind == UiControlKind::Percussion) {
            add(control.bounds); add(control.label_bounds); add(control.value_bounds);
        }
    const auto p = model.layout().performance_panel;
    const float group = p.width * .46F;
    add({p.x + 17, p.y + 3, group - 34, 18});
    // The two expressly admitted old/new eligibility rectangles; neither
    // expands the mask to the whole panel or neighboring expression/divider.
    if (p.height >= 92) add({p.x + 12, p.y + 73, group - 24, 16});
    if (active(test) && p.height >= 104) add({p.x + 12, p.y + p.height - 16, group - 24, 11});
    out << "],\"bytes\":" << frame.pixels.size() * sizeof(Pixel) << "}\n";
    std::cout << out.str();
    std::cout.write(reinterpret_cast<const char*>(frame.pixels.data()),
                    static_cast<std::streamsize>(frame.pixels.size() * sizeof(Pixel)));
    std::cout.flush();
    require(static_cast<bool>(std::cout), "write bounded frame stream");
}
} // namespace

int main(int argc, char* argv[]) {
    SDL_SetMainReady();
    try {
        const auto fixtures = cases();
        if (argc == 2 && std::string_view(argv[1]) == "--list") {
            std::cout << "{\"schema\":1,\"cases\":" << fixtures.size() << "}\n";
            return 0;
        }
        std::size_t selected = fixtures.size();
        if (argc != 1) {
            require(argc == 3 && std::string_view(argv[1]) == "--case", "expected --case INDEX or --list");
            const std::string_view value(argv[2]);
            const auto parsed = std::from_chars(value.data(), value.data() + value.size(), selected);
            require(parsed.ec == std::errc{} && parsed.ptr == value.data() + value.size() && selected < fixtures.size(),
                    "bounded case index");
#ifdef _WIN32
            require(_setmode(_fileno(stdout), _O_BINARY) != -1, "binary frame stdout");
#endif
        }
        require(SDL_Init(0) == 0, "initialize SDL without window or audio");
        for (std::size_t index = 0; index < fixtures.size(); ++index) {
            if (selected != fixtures.size() && index != selected) continue;
            const auto& test = fixtures[index];
            const auto model = state_for(test);
            Target target(test);
            const auto frame = target.paint(model);
            if (selected != fixtures.size()) stream(index, test, model, frame);
            else ordinary_acceptance(test, model, target, frame);
            ++totals.cases;
        }
        SDL_Quit();
        if (selected == fixtures.size())
            std::cout << "{\"schema\":1,\"status\":\"passed\",\"cases\":" << totals.cases
                << ",\"checks\":" << totals.checks << ",\"literal_glyphs\":" << totals.glyphs
                << ",\"strong_ink_pixels\":" << totals.ink_pixels << ",\"focus_cases\":" << totals.focus_cases
                << ",\"clipped_cases\":" << totals.clips
                << ",\"backend\":\"SDL software surface; fixed copied state; no audio/window\"}\n";
        return EXIT_SUCCESS;
    } catch (const std::exception& error) {
        std::cerr << "Percussion raster acceptance failed: " << error.what() << '\n';
        SDL_Quit();
        return EXIT_FAILURE;
    }
}
