// Manual paint-cost benchmark, deliberately not a timing-sensitive CTest.
// Link this unchanged source against two InstrumentView translation units and
// the SAME current Drawing, standalone support/UiModel, core and SDL archives.
// Usage: standalone_material_timing WIDTH HEIGHT dimensional|flat none|help|audio|midi
// Only the three contract sizes are admitted; warmup/sample counts are fixed.
#include "InstrumentView.h"

#include <SDL.h>

#include <algorithm>
#include <array>
#include <bit>
#include <charconv>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>

namespace {
using namespace hammond;
using namespace hammond::standalone;
using Clock = std::chrono::steady_clock;
constexpr std::size_t kWarmup = 30;
constexpr std::size_t kSamples = 300;
static_assert(Clock::is_steady);

void require(bool condition, std::string_view message) {
    if (!condition) throw std::runtime_error(std::string(message) + ": " + SDL_GetError());
}

int integer(std::string_view value) {
    int result{};
    const auto parsed = std::from_chars(value.data(), value.data() + value.size(), result);
    if (parsed.ec != std::errc{} || parsed.ptr != value.data() + value.size())
        throw std::runtime_error("invalid integer argument");
    return result;
}

struct Fingerprint {
    std::uint64_t value{14695981039346656037ULL};
    void byte(std::uint8_t part) noexcept { value = (value ^ part) * 1099511628211ULL; }
    void word(std::uint32_t part) noexcept {
        for (unsigned shift = 0; shift < 32; shift += 8)
            byte(static_cast<std::uint8_t>((part >> shift) & 255U));
    }
    void scalar(float part) noexcept { word(std::bit_cast<std::uint32_t>(part)); }
    void rect(UiRect part) noexcept {
        scalar(part.x); scalar(part.y); scalar(part.width); scalar(part.height);
    }
    void quad(const UiQuad& part) noexcept {
        for (const auto point : part.points) { scalar(point.x); scalar(point.y); }
    }
    void key(const UiKeyGeometry& part) noexcept {
        word(static_cast<std::uint32_t>(part.note.target)); word(part.note.value);
        word(part.accidental ? 1U : 0U);
        rect(part.bounds); quad(part.hit); quad(part.top); quad(part.front);
    }
};

// Field-wise, never padded object bytes: proves all benchmark paint geometry
// is identical between executables independently of their differing pixels.
std::uint64_t layout_fingerprint(const UiLayout& layout) noexcept {
    Fingerprint hash;
    hash.scalar(layout.width); hash.scalar(layout.height);
    hash.word(layout.show_cabinet ? 1U : 0U);
    hash.word(layout.bank_controls_in_cheeks ? 1U : 0U);
    hash.word(layout.sidebar_pedals ? 1U : 0U);
    hash.word(static_cast<std::uint32_t>(layout.workspace));
    hash.word(static_cast<std::uint32_t>(layout.presentation));
    hash.rect(layout.header);
    for (const auto rect : layout.registration_panels) hash.rect(rect);
    hash.rect(layout.performance_panel); hash.rect(layout.keyboard_toolbar);
    for (const auto rect : layout.manual_panels) hash.rect(rect);
    hash.rect(layout.pedal_panel); hash.rect(layout.footer); hash.rect(layout.cabinet_panel);
    hash.rect(layout.cabinet_art); hash.rect(layout.workspace_panel);
    for (const auto rect : layout.manual_rail_panels) hash.rect(rect);
    for (const auto rect : layout.preset_key_panels) hash.rect(rect);
    hash.word(static_cast<std::uint32_t>(layout.control_count));
    for (std::size_t index = 0; index < layout.control_count; ++index) {
        const auto& control = layout.controls[index];
        hash.word(static_cast<std::uint32_t>(control.id.kind));
        hash.word(static_cast<std::uint32_t>(control.id.manual));
        hash.word(static_cast<std::uint32_t>(control.id.bank)); hash.word(control.id.index);
        hash.rect(control.bounds); hash.rect(control.label_bounds);
        hash.rect(control.value_bounds); hash.rect(control.track);
    }
    for (const auto& manual : layout.manual_keys)
        for (const auto& key : manual) hash.key(key);
    for (const auto& key : layout.pedal_keys) hash.key(key);
    return hash.value;
}

struct Sample {
    std::int64_t paint_ns{};
    std::int64_t flush_present_ns{};
    std::int64_t total_ns{};
};

Sample draw(Drawing& drawing, const UiModel& model, const InstrumentViewInfo& info) {
    const auto start = Clock::now();
    paint_instrument(drawing, model, info);
    const auto painted = Clock::now();
    const int status = SDL_RenderFlush(drawing.renderer());
    SDL_RenderPresent(drawing.renderer());
    const auto completed = Clock::now();
    // Error reporting is outside the measured interval. No capture, pixel
    // hashing, file access, logging, sorting or model mutation occurs in it.
    require(status == 0, "flush software renderer");
    return {std::chrono::duration_cast<std::chrono::nanoseconds>(painted - start).count(),
            std::chrono::duration_cast<std::chrono::nanoseconds>(completed - painted).count(),
            std::chrono::duration_cast<std::chrono::nanoseconds>(completed - start).count()};
}

void statistics(std::array<std::int64_t, kSamples> values) {
    std::sort(values.begin(), values.end());
    constexpr double to_ms = 1.0e-6;
    const double median = (static_cast<double>(values[kSamples / 2 - 1]) +
                           static_cast<double>(values[kSamples / 2])) * 0.5;
    // Nearest-rank p95 = sorted sample 285 of 300 (one-based).
    constexpr std::size_t p95_index = (95 * kSamples + 99) / 100 - 1;
    std::cout << "{\"median_ms\":" << median * to_ms
              << ",\"p95_ms\":" << static_cast<double>(values[p95_index]) * to_ms
              << ",\"minimum_ms\":" << static_cast<double>(values.front()) * to_ms
              << ",\"maximum_ms\":" << static_cast<double>(values.back()) * to_ms << '}';
}

int run(int argc, char** argv) {
    require(argc == 5, "usage: WIDTH HEIGHT dimensional|flat none|help|audio|midi");
    const int width = integer(argv[1]), height = integer(argv[2]);
    require((width == 960 && height == 700) || (width == 1280 && height == 900) ||
            (width == 1672 && height == 941), "only bounded contract dimensions are admitted");
    const std::string_view presentation_name = argv[3], overlay_name = argv[4];
    require(presentation_name == "dimensional" || presentation_name == "flat", "invalid presentation");
    const auto presentation = presentation_name == "flat" ? UiPresentation::Flat : UiPresentation::Dimensional;
    ViewOverlay overlay{};
    if (overlay_name == "none") overlay = ViewOverlay::None;
    else if (overlay_name == "help") overlay = ViewOverlay::Help;
    else if (overlay_name == "audio") overlay = ViewOverlay::Audio;
    else if (overlay_name == "midi") overlay = ViewOverlay::Midi;
    else throw std::runtime_error("invalid overlay");

    require(SDL_SetHint(SDL_HINT_RENDER_BATCHING, "1") == SDL_TRUE, "enable fixed renderer batching");
    require(SDL_Init(0) == 0, "initialize SDL without window or audio subsystems");
    const std::unique_ptr<SDL_Surface, decltype(&SDL_FreeSurface)> surface(
        SDL_CreateRGBSurfaceWithFormat(0, width, height, 32, SDL_PIXELFORMAT_RGBA32), SDL_FreeSurface);
    require(surface != nullptr, "allocate bounded RGBA32 surface");
    const std::unique_ptr<SDL_Renderer, decltype(&SDL_DestroyRenderer)> renderer(
        SDL_CreateSoftwareRenderer(surface.get()), SDL_DestroyRenderer);
    require(renderer != nullptr, "create software renderer");
    SDL_RendererInfo renderer_info{};
    require(SDL_GetRendererInfo(renderer.get(), &renderer_info) == 0 &&
            std::string_view(renderer_info.name) == "software" &&
            (renderer_info.flags & SDL_RENDERER_SOFTWARE) != 0, "verify actual software renderer");
    require(SDL_RenderSetScale(renderer.get(), 1.0F, 1.0F) == 0 &&
            SDL_RenderSetViewport(renderer.get(), nullptr) == 0 &&
            SDL_RenderSetClipRect(renderer.get(), nullptr) == 0, "configure identical scale/viewport/clip");
    Drawing drawing(renderer.get());
    std::string error;
    require(drawing.initialize(error), "initialize Drawing before warmup: " + error);

    UiModel model;
    require(model.resize(static_cast<float>(width), static_cast<float>(height)) &&
            model.set_presentation(presentation), "prepare current model and geometry");
    SessionSnapshot snapshot;
    snapshot.publication_revision = 2;
    snapshot.held_keys[0][24] = true; snapshot.held_keys[0][25] = true;
    snapshot.held_keys[1][36] = true; snapshot.held_keys[1][37] = true;
    snapshot.held_pedals[0] = true; snapshot.held_pedals[1] = true;
    model.observe(snapshot);
    (void)model.activate({UiControlKind::ManualKey, Manual::Upper, DrawbarBank::A, 24});
    const std::array<std::string, 2> audio_choices{"Default output", "Benchmark output fixture"};
    const std::array<std::string, 2> midi_choices{"No input", "Benchmark input fixture"};
    InstrumentViewInfo info;
    info.status_message = "UI timing fixture; no audio device";
    info.overlay = overlay;
    info.audio_choices = audio_choices; info.selected_device = 1;
    info.midi_available = true; info.midi_backend = "fixture";
    info.midi_status = "Copied benchmark state; no MIDI port opened";
    info.midi_choices = midi_choices; info.selected_midi_port = 1;

    std::array<Sample, kSamples> samples{};
    for (std::size_t frame = 0; frame < kWarmup; ++frame) (void)draw(drawing, model, info);
    for (auto& sample : samples) sample = draw(drawing, model, info);

    // Direct surface bytes after all timing: no screenshot or image file is
    // needed to establish that actual paint reached the target.
    require(SDL_LockSurface(surface.get()) == 0, "lock completed surface");
    Fingerprint pixels;
    const auto* bytes = static_cast<const std::uint8_t*>(surface->pixels);
    for (int y = 0; y < height; ++y)
        for (int x = 0; x < width * 4; ++x)
            pixels.byte(bytes[static_cast<std::size_t>(y) * static_cast<std::size_t>(surface->pitch) +
                              static_cast<std::size_t>(x)]);
    SDL_UnlockSurface(surface.get());
    std::array<std::int64_t, kSamples> paint{}, flush{}, total{};
    for (std::size_t index = 0; index < kSamples; ++index) {
        paint[index] = samples[index].paint_ns;
        flush[index] = samples[index].flush_present_ns;
        total[index] = samples[index].total_ns;
    }
    SDL_version version{};
    SDL_GetVersion(&version);
    const auto& key = model.layout().manual_keys[0][24];
    std::cout << std::fixed << std::setprecision(6)
              << "{\"schema\":\"standalone-material-timing-v1\",\"width\":" << width
              << ",\"height\":" << height << ",\"presentation\":\"" << presentation_name
              << "\",\"overlay\":\"" << overlay_name
              << "\",\"workspace\":\"Play\",\"warmup\":" << kWarmup << ",\"samples\":" << kSamples
              << ",\"renderer\":\"" << renderer_info.name << "\",\"renderer_flags\":" << renderer_info.flags
              << ",\"sdl_version\":\"" << static_cast<unsigned>(version.major) << '.'
              << static_cast<unsigned>(version.minor) << '.' << static_cast<unsigned>(version.patch)
              << "\",\"surface_format\":\"" << SDL_GetPixelFormatName(surface->format->format)
              << "\",\"surface_bytes\":" << static_cast<std::size_t>(surface->pitch) * static_cast<std::size_t>(height)
              << ",\"render_batching\":\"" << SDL_GetHint(SDL_HINT_RENDER_BATCHING)
              << "\",\"scale\":[1,1],\"viewport\":[0,0," << width << ',' << height
              << "],\"clip\":null,\"clock\":\"std::chrono::steady_clock\",\"clock_period\":["
              << Clock::period::num << ',' << Clock::period::den
              << "],\"layout_fnv1a64\":\"" << std::hex << layout_fingerprint(model.layout())
              << "\",\"final_pixels_fnv1a64\":\"" << pixels.value << std::dec
              << "\",\"upper_c_hit_depth\":" << key.hit.points[3].y - key.hit.points[0].y
              << ",\"paint\":";
    statistics(paint);
    std::cout << ",\"flush_and_surface_present\":";
    statistics(flush);
    std::cout << ",\"total\":";
    statistics(total);
    std::cout << ",\"samples_total_ns\":[";
    for (std::size_t index = 0; index < kSamples; ++index) {
        if (index != 0) std::cout << ',';
        std::cout << total[index];
    }
    std::cout << "]}\n";
    return EXIT_SUCCESS;
}
} // namespace

int main(int argc, char** argv) {
    SDL_SetMainReady();
    try {
        const int status = run(argc, argv);
        SDL_Quit();
        return status;
    } catch (const std::exception& error) {
        std::cerr << "Material timing setup failed: " << error.what() << '\n';
        SDL_Quit();
        return EXIT_FAILURE;
    }
}
