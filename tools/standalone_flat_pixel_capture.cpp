// Capture-only companion for the prospectively reviewed P1 Flat witness.
// The included benchmark stays byte-for-byte unchanged. Its renamed entry,
// run(), draw() and all clock/statistics paths are never invoked by this entry.
// Initialization below is copied verbatim from its pinned run() prefix.
#if defined(HAMMOND_PAINT_BASELINE) || defined(HAMMOND_PAINT_ALLOCATIONS)
#error "The Flat pixel companion forbids paired and allocation-instrumented builds"
#endif
#define main retained_benchmark_entry_not_called
#include "standalone_paint_benchmark.cpp"
#undef main
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif

namespace {
int capture_fixed_flat(int argc, char** argv) {
    require(argc == 5 && std::string_view(argv[1]) == "1672" &&
            std::string_view(argv[2]) == "941" && std::string_view(argv[3]) == "flat" &&
            std::string_view(argv[4]) == "mixed-held", "only the fixed Flat timing scene is admitted");
// BEGIN exact pinned benchmark initialization
    require(argc == 5, "usage: WIDTH HEIGHT dimensional|flat zero|eight|mixed-held");
    const int width = integer(argv[1]), height = integer(argv[2]);
    require((width == 960 && height == 700) || (width == 1280 && height == 900) ||
            (width == 1400 && height == 820) || (width == 1672 && height == 941) ||
            (width == 1920 && height == 1080), "only bounded contract dimensions are admitted");
    const std::string_view presentation_name = argv[3], scenario_name = argv[4];
    require(presentation_name == "dimensional" || presentation_name == "flat", "invalid presentation");
    require(scenario_name == "zero" || scenario_name == "eight" || scenario_name == "mixed-held",
            "invalid fixed instrument state");
    const auto presentation = presentation_name == "flat" ? UiPresentation::Flat : UiPresentation::Dimensional;
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
            (renderer_info.flags & SDL_RENDERER_SOFTWARE) != 0, "verify software renderer");
    require(SDL_RenderSetScale(renderer.get(), 1, 1) == 0 &&
            SDL_RenderSetViewport(renderer.get(), nullptr) == 0 &&
            SDL_RenderSetClipRect(renderer.get(), nullptr) == 0, "configure fixed output transform");
    Drawing drawing(renderer.get());
    std::string error;
    require(drawing.initialize(error), "initialize Drawing before warmup: " + error);

    UiModel model;
    require(model.resize(static_cast<float>(width), static_cast<float>(height)) &&
            model.set_presentation(presentation), "prepare current model and geometry");
    SessionSnapshot snapshot;
    snapshot.publication_revision = 2;
    snapshot.prepared = true;
    snapshot.running = true;
    snapshot.sample_rate = 48000;
    for (std::size_t manual = 0; manual < kManualCount; ++manual)
        for (std::size_t bank = 0; bank < kDrawbarBankCount; ++bank)
            for (std::size_t index = 0; index < kDrawbarCount; ++index)
                snapshot.controls.drawbars[manual][bank][index] = scenario_name == "zero" ? 0 :
                    scenario_name == "eight" ? 8 : static_cast<std::uint8_t>((index + manual + bank) % 9);
    snapshot.controls.pedal_drawbars = {8, 0};
    snapshot.controls.expression = 0.75;
    if (scenario_name == "mixed-held") {
        snapshot.controls.fixed_registrations[0] = FixedRegistration::CSharp;
        snapshot.controls.selected_banks[1] = DrawbarBank::A;
        snapshot.held_keys[0][24] = true; snapshot.held_keys[0][25] = true;
        snapshot.held_keys[1][0] = true; snapshot.held_keys[1][60] = true;
        snapshot.held_pedals[3] = true;
    }
    require(is_valid_control_snapshot(snapshot.controls), "admit fixed musical snapshot");
    model.observe(snapshot);
    require(model.view().applied.controls == snapshot.controls, "observe fixed copied controls");
    const auto layout_hash = layout_fingerprint(model.layout());
    InstrumentViewInfo info;
    info.audio_running = true;
    info.sample_rate = 48000;
    info.buffer_frames = 512;
    info.audio_driver = "fixed fixture";
    info.device_name = "No device opened";
    info.status_message = "Paired paint fixture; no audio device or window";
    info.overlay = ViewOverlay::None;

// END exact pinned benchmark initialization
    static_assert(kWarmup == 30 && kSamples == 300);
    constexpr std::size_t paints = kWarmup + kSamples + 1;
    for (std::size_t frame = 0; frame < paints; ++frame) {
        paint_instrument(drawing, model, info);
        const int status = SDL_RenderFlush(renderer.get());
        SDL_RenderPresent(renderer.get());
        require(status == 0, "flush unmeasured Flat witness");
    }
    require(layout_fingerprint(model.layout()) == layout_hash &&
            model.view().applied.controls == snapshot.controls &&
            model.view().applied.held_keys == snapshot.held_keys &&
            model.view().applied.held_pedals == snapshot.held_pedals,
            "painting preserves copied model and geometry");
    const auto fingerprint = pixels(surface.get());
    SDL_version version{};
    SDL_GetVersion(&version);
    const auto row_bytes = static_cast<std::size_t>(width) * 4U;
    const auto byte_count = row_bytes * static_cast<std::size_t>(height);
    std::cout.imbue(std::locale::classic());
    std::cout << "{\"schema\":\"standalone-benchmark-flat-pixels-v1\",\"width\":" << width
              << ",\"height\":" << height
              << ",\"presentation\":\"flat\",\"scenario\":\"mixed-held\",\"workspace\":\"Play\",\"overlay\":\"none\""
              << ",\"paints\":" << paints << ",\"timing_samples\":0,\"paired\":false,\"heap_instrumentation\":false"
              << ",\"preservation_assertions_passed\":true,\"render_batching\":\"" << SDL_GetHint(SDL_HINT_RENDER_BATCHING)
              << "\",\"surface_format\":\"" << SDL_GetPixelFormatName(surface->format->format) << '"'
              << ",\"renderer\":\"" << renderer_info.name << "\",\"renderer_flags\":" << renderer_info.flags
              << ",\"sdl_version\":\"" << static_cast<unsigned>(version.major) << '.'
              << static_cast<unsigned>(version.minor) << '.' << static_cast<unsigned>(version.patch)
              << "\",\"pixel_format\":\"RGBA32\",\"row_order\":\"top-to-bottom\",\"row_stride\":" << row_bytes
              << ",\"bytes\":" << byte_count << ",\"scale\":[1,1],\"viewport\":[0,0,1672,941],\"clip\":null"
              << ",\"layout_fnv1a64\":\"" << std::hex << layout_hash
              << "\",\"current_pixels_fnv1a64\":\"" << fingerprint << "\"}\n" << std::dec;
    require(SDL_LockSurface(surface.get()) == 0, "lock completed Flat witness");
    const auto* bytes = static_cast<const char*>(surface->pixels);
    for (int row = 0; row < height; ++row) {
        const auto offset = static_cast<std::size_t>(row) * static_cast<std::size_t>(surface->pitch);
        std::cout.write(bytes + offset, static_cast<std::streamsize>(row_bytes));
    }
    SDL_UnlockSurface(surface.get());
    require(static_cast<bool>(std::cout), "write complete Flat witness");
    return EXIT_SUCCESS;
}
} // namespace

int main(int argc, char** argv) {
    SDL_SetMainReady();
    try {
#ifdef _WIN32
        require(_setmode(_fileno(stdout), _O_BINARY) != -1, "set binary stdout");
#endif
        const int result = capture_fixed_flat(argc, argv);
        SDL_Quit();
        return result;
    } catch (const std::exception& error) {
        std::cerr << "Flat capture failed: " << error.what() << '\n';
        SDL_Quit();
        return EXIT_FAILURE;
    }
}
