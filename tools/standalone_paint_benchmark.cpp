// Bounded manual benchmark, deliberately not a timing-sensitive CTest.
// Ordinary build links the current InstrumentView.cpp. For before/after use
// HAMMOND_PAINT_BASELINE and a frozen before translation unit whose three public
// exports alone are renamed with _benchmark_before suffixes. All dependencies,
// model values, renderer, fonts and assets are shared by both painters.
// A separate HAMMOND_PAINT_ALLOCATIONS build enables calibrated global C++
// allocation observation; its results must never be used as timing evidence.
// Usage: standalone_paint_benchmark WIDTH HEIGHT dimensional|flat zero|eight|mixed-held
#include "InstrumentView.h"
#include <SDL.h>
#include <algorithm>
#include <array>
#include <bit>
#include <charconv>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <limits>
#include <locale>
#include <memory>
#include <new>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>

#ifdef HAMMOND_PAINT_BASELINE
namespace hammond::standalone {
void paint_instrument_benchmark_before(Drawing&, const UiModel&, const InstrumentViewInfo&);
}
#endif

#ifdef HAMMOND_PAINT_ALLOCATIONS
#if defined(_MSC_VER)
#include <malloc.h>
#endif

// Probe and twelve-overload calibration follow the standalone callback
// allocation test. They are local to this executable and observe C++ calls.
// Keep the interposition boundary visible under optimization. GCC otherwise
// diagnoses an inlined malloc-backed new paired with sized delete as mismatched.
#if defined(_MSC_VER)
#define HAMMOND_PROBE_NOINLINE __declspec(noinline)
#elif defined(__GNUC__) || defined(__clang__)
#define HAMMOND_PROBE_NOINLINE __attribute__((noinline))
#else
#define HAMMOND_PROBE_NOINLINE
#endif

// These replacements belong only to this test executable. The probe observes
// this thread's global C++ allocation/deallocation calls, not arbitrary C heap,
// system allocation, other threads, locking, or callback elapsed time.
namespace allocation_probe {

struct Counts {
    std::size_t allocations{};
    std::size_t deallocations{};
};

thread_local bool recording = false;
thread_local Counts counts{};

void allocation() noexcept {
    if (recording) ++counts.allocations;
}

void deallocation(void* pointer) noexcept {
    if (recording && pointer != nullptr) ++counts.deallocations;
}

void begin() noexcept {
    counts = {};
    recording = true;
}

[[nodiscard]] Counts end() noexcept {
    recording = false;
    return counts;
}

[[nodiscard]] void* allocate_bytes(std::size_t size) {
    if (size == 0) size = 1;
    for (;;) {
        if (void* pointer = std::malloc(size)) return pointer;
        const auto handler = std::get_new_handler();
        if (handler == nullptr) throw std::bad_alloc{};
        handler();
    }
}

// Supported Unix/Apple/MSVC platforms keep the requested aligned payload size
// at the native allocator boundary, including sanitizer redzones. The portable
// fallback rounds only as C aligned_alloc requires. No sanitizer is disabled.
[[nodiscard]] void* allocate_aligned(std::size_t size, std::size_t alignment) {
    if (size == 0) size = 1;
    if (alignment == 0 || (alignment & (alignment - 1)) != 0) throw std::bad_alloc{};
    alignment = std::max(alignment, alignof(void*));
#if !defined(_MSC_VER) && !defined(__unix__) && !defined(__APPLE__)
    const auto remainder = size % alignment;
    const auto padding = remainder == 0 ? 0 : alignment - remainder;
    if (size > std::numeric_limits<std::size_t>::max() - padding) throw std::bad_alloc{};
    size += padding; // C aligned_alloc requires a whole multiple of alignment.
#endif
    for (;;) {
#if defined(_MSC_VER)
        if (void* pointer = _aligned_malloc(size, alignment)) return pointer;
#elif defined(__unix__) || defined(__APPLE__)
        void* pointer = nullptr;
        if (::posix_memalign(&pointer, alignment, size) == 0) return pointer;
#else
        if (void* pointer = std::aligned_alloc(alignment, size)) return pointer;
#endif
        const auto handler = std::get_new_handler();
        if (handler == nullptr) throw std::bad_alloc{};
        handler();
    }
}

void free_aligned(void* pointer) noexcept {
#if defined(_MSC_VER)
    _aligned_free(pointer);
#else
    std::free(pointer);
#endif
}

} // namespace allocation_probe

HAMMOND_PROBE_NOINLINE void* operator new(std::size_t size) {
    allocation_probe::allocation();
    return allocation_probe::allocate_bytes(size);
}
HAMMOND_PROBE_NOINLINE void* operator new[](std::size_t size) { return ::operator new(size); }
HAMMOND_PROBE_NOINLINE void* operator new(std::size_t size, const std::nothrow_t&) noexcept {
    try { return ::operator new(size); } catch (...) { return nullptr; }
}
HAMMOND_PROBE_NOINLINE void* operator new[](std::size_t size, const std::nothrow_t&) noexcept {
    try { return ::operator new[](size); } catch (...) { return nullptr; }
}
HAMMOND_PROBE_NOINLINE void operator delete(void* pointer) noexcept {
    allocation_probe::deallocation(pointer);
    std::free(pointer);
}
HAMMOND_PROBE_NOINLINE void operator delete[](void* pointer) noexcept { ::operator delete(pointer); }
HAMMOND_PROBE_NOINLINE void operator delete(void* pointer, std::size_t) noexcept {
    ::operator delete(pointer);
}
HAMMOND_PROBE_NOINLINE void operator delete[](void* pointer, std::size_t) noexcept {
    ::operator delete[](pointer);
}
HAMMOND_PROBE_NOINLINE void operator delete(void* pointer, const std::nothrow_t&) noexcept {
    ::operator delete(pointer);
}
HAMMOND_PROBE_NOINLINE void operator delete[](void* pointer, const std::nothrow_t&) noexcept {
    ::operator delete[](pointer);
}

HAMMOND_PROBE_NOINLINE void* operator new(std::size_t size, std::align_val_t alignment) {
    allocation_probe::allocation();
    return allocation_probe::allocate_aligned(size, static_cast<std::size_t>(alignment));
}
HAMMOND_PROBE_NOINLINE void* operator new[](std::size_t size, std::align_val_t alignment) {
    return ::operator new(size, alignment);
}
HAMMOND_PROBE_NOINLINE void* operator new(std::size_t size, std::align_val_t alignment,
                   const std::nothrow_t&) noexcept {
    try { return ::operator new(size, alignment); } catch (...) { return nullptr; }
}
HAMMOND_PROBE_NOINLINE void* operator new[](std::size_t size, std::align_val_t alignment,
                     const std::nothrow_t&) noexcept {
    try { return ::operator new[](size, alignment); } catch (...) { return nullptr; }
}
HAMMOND_PROBE_NOINLINE void operator delete(void* pointer, std::align_val_t) noexcept {
    allocation_probe::deallocation(pointer);
    allocation_probe::free_aligned(pointer);
}
HAMMOND_PROBE_NOINLINE void operator delete[](void* pointer, std::align_val_t alignment) noexcept {
    ::operator delete(pointer, alignment);
}
HAMMOND_PROBE_NOINLINE void operator delete(void* pointer, std::size_t,
                                           std::align_val_t alignment) noexcept {
    ::operator delete(pointer, alignment);
}
HAMMOND_PROBE_NOINLINE void operator delete[](void* pointer, std::size_t,
                                             std::align_val_t alignment) noexcept {
    ::operator delete[](pointer, alignment);
}
HAMMOND_PROBE_NOINLINE void operator delete(void* pointer, std::align_val_t alignment,
                                           const std::nothrow_t&) noexcept {
    ::operator delete(pointer, alignment);
}
HAMMOND_PROBE_NOINLINE void operator delete[](void* pointer, std::align_val_t alignment,
                       const std::nothrow_t&) noexcept {
    ::operator delete[](pointer, alignment);
}


namespace {

using namespace hammond;

// Explicit calls through volatile function pointers prevent new-expression
// allocation elision from making the instrumentation calibration vacuous.
template <typename Function>
[[nodiscard]] Function opaque(Function function) noexcept {
    Function volatile pointer = function;
    return pointer;
}

struct Calibration {
    allocation_probe::Counts allocated{};
    allocation_probe::Counts freed{};
    bool valid_storage{true};

    [[nodiscard]] bool passed() const noexcept {
        return valid_storage && allocated.allocations == 12 && allocated.deallocations == 0 &&
               freed.allocations == 0 && freed.deallocations == 12;
    }
};

// No assertion, formatting or fixture construction occurs while recording.
// Both calibration intervals are disjoint from the observed primitive calls.
[[nodiscard]] Calibration calibrate() noexcept {
    using New = void* (*)(std::size_t);
    using NothrowNew = void* (*)(std::size_t, const std::nothrow_t&) noexcept;
    using AlignedNew = void* (*)(std::size_t, std::align_val_t);
    using AlignedNothrowNew = void* (*)(std::size_t, std::align_val_t,
                                      const std::nothrow_t&) noexcept;
    using Delete = void (*)(void*) noexcept;
    using SizedDelete = void (*)(void*, std::size_t) noexcept;
    using NothrowDelete = void (*)(void*, const std::nothrow_t&) noexcept;
    using AlignedDelete = void (*)(void*, std::align_val_t) noexcept;
    using AlignedSizedDelete = void (*)(void*, std::size_t, std::align_val_t) noexcept;
    using AlignedNothrowDelete = void (*)(void*, std::align_val_t,
                                        const std::nothrow_t&) noexcept;
    constexpr std::align_val_t alignment{64};
    std::array<void*, 12> pointers{};
    Calibration result;

    allocation_probe::begin();
    try {
        pointers[0] = opaque(static_cast<New>(&::operator new))(0);
        pointers[1] = opaque(static_cast<New>(&::operator new[]))(23);
        pointers[2] = opaque(static_cast<New>(&::operator new))(31);
        pointers[3] = opaque(static_cast<New>(&::operator new[]))(41);
        pointers[4] = opaque(static_cast<NothrowNew>(&::operator new))(51, std::nothrow);
        pointers[5] = opaque(static_cast<NothrowNew>(&::operator new[]))(61, std::nothrow);
        pointers[6] = opaque(static_cast<AlignedNew>(&::operator new))(0, alignment);
        pointers[7] = opaque(static_cast<AlignedNew>(&::operator new[]))(77, alignment);
        pointers[8] = opaque(static_cast<AlignedNew>(&::operator new))(83, alignment);
        pointers[9] = opaque(static_cast<AlignedNew>(&::operator new[]))(89, alignment);
        pointers[10] = opaque(static_cast<AlignedNothrowNew>(&::operator new))(
            97, alignment, std::nothrow);
        pointers[11] = opaque(static_cast<AlignedNothrowNew>(&::operator new[]))(
            101, alignment, std::nothrow);
    } catch (...) {
        result.valid_storage = false;
    }
    result.allocated = allocation_probe::end();
    for (std::size_t index = 0; index < pointers.size(); ++index) {
        if (pointers[index] == nullptr ||
            (index >= 6 && reinterpret_cast<std::uintptr_t>(pointers[index]) % 64 != 0)) {
            result.valid_storage = false;
        }
    }

    allocation_probe::begin();
    opaque(static_cast<Delete>(&::operator delete))(pointers[0]);
    opaque(static_cast<Delete>(&::operator delete[]))(pointers[1]);
    opaque(static_cast<SizedDelete>(&::operator delete))(pointers[2], 31);
    opaque(static_cast<SizedDelete>(&::operator delete[]))(pointers[3], 41);
    opaque(static_cast<NothrowDelete>(&::operator delete))(pointers[4], std::nothrow);
    opaque(static_cast<NothrowDelete>(&::operator delete[]))(pointers[5], std::nothrow);
    opaque(static_cast<AlignedDelete>(&::operator delete))(pointers[6], alignment);
    opaque(static_cast<AlignedDelete>(&::operator delete[]))(pointers[7], alignment);
    opaque(static_cast<AlignedSizedDelete>(&::operator delete))(pointers[8], 83, alignment);
    opaque(static_cast<AlignedSizedDelete>(&::operator delete[]))(pointers[9], 89, alignment);
    opaque(static_cast<AlignedNothrowDelete>(&::operator delete))(
        pointers[10], alignment, std::nothrow);
    opaque(static_cast<AlignedNothrowDelete>(&::operator delete[]))(
        pointers[11], alignment, std::nothrow);
    result.freed = allocation_probe::end();
    return result;
}

} // namespace
#endif

namespace {
using namespace hammond;
using namespace hammond::standalone;
using Clock = std::chrono::steady_clock;
constexpr std::size_t kWarmup = 30;
#ifdef HAMMOND_PAINT_ALLOCATIONS
constexpr std::size_t kSamples = 32;
#else
constexpr std::size_t kSamples = 300;
#endif
static_assert(Clock::is_steady);
void require(bool condition, std::string_view message) {
    if (!condition) throw std::runtime_error(std::string(message) + ": " + SDL_GetError());
}
int integer(std::string_view value) {
    int result{};
    const auto parsed = std::from_chars(value.data(), value.data() + value.size(), result);
    if (value.empty() || parsed.ec != std::errc{} || parsed.ptr != value.data() + value.size())
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

using Painter = void (*)(Drawing&, const UiModel&, const InstrumentViewInfo&);

Sample draw(Painter painter, Drawing& drawing, const UiModel& model, const InstrumentViewInfo& info) {
    const auto start = Clock::now();
    painter(drawing, model, info);
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

[[maybe_unused]] void statistics(std::array<std::int64_t, kSamples> values) {
    std::sort(values.begin(), values.end());
    constexpr double to_ms = 1.0e-6;
    const double median = (static_cast<double>(values[kSamples / 2 - 1]) +
                           static_cast<double>(values[kSamples / 2])) * 0.5;
    // Nearest-rank percentile of the fixed sample count.
    constexpr std::size_t p95_index = (95 * kSamples + 99) / 100 - 1;
    std::cout << "{\"median_ms\":" << median * to_ms
              << ",\"p95_ms\":" << static_cast<double>(values[p95_index]) * to_ms
              << ",\"minimum_ms\":" << static_cast<double>(values.front()) * to_ms
              << ",\"maximum_ms\":" << static_cast<double>(values.back()) * to_ms << '}';
}


[[maybe_unused]] double median(std::array<std::int64_t, kSamples> values) {
    std::sort(values.begin(), values.end());
    return 0.5 * (static_cast<double>(values[kSamples / 2 - 1]) + static_cast<double>(values[kSamples / 2]));
}

std::uint64_t pixels(SDL_Surface* surface) {
    require(SDL_LockSurface(surface) == 0, "lock completed surface");
    Fingerprint hash;
    const auto* bytes = static_cast<const std::uint8_t*>(surface->pixels);
    for (int y = 0; y < surface->h; ++y)
        for (int x = 0; x < surface->w * 4; ++x)
            hash.byte(bytes[static_cast<std::size_t>(y) * static_cast<std::size_t>(surface->pitch) +
                            static_cast<std::size_t>(x)]);
    SDL_UnlockSurface(surface);
    return hash.value;
}

[[maybe_unused]] void print_samples(const std::array<Sample, kSamples>& samples) {
    std::array<std::int64_t, kSamples> paint{}, flush{}, total{};
    for (std::size_t index = 0; index < kSamples; ++index) {
        paint[index] = samples[index].paint_ns;
        flush[index] = samples[index].flush_present_ns;
        total[index] = samples[index].total_ns;
    }
    std::cout << "{\"paint\":"; statistics(paint);
    std::cout << ",\"flush_and_surface_present\":"; statistics(flush);
    std::cout << ",\"total\":"; statistics(total);
    std::cout << ",\"samples_total_ns\":[";
    for (std::size_t index = 0; index < kSamples; ++index) {
        if (index != 0) std::cout << ',';
        std::cout << total[index];
    }
    std::cout << "]}";
}

int run(int argc, char** argv) {
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

    constexpr Painter current = &paint_instrument;
#ifdef HAMMOND_PAINT_BASELINE
    constexpr Painter before = &paint_instrument_benchmark_before;
    constexpr bool paired = true;
#else
    constexpr Painter before = nullptr;
    constexpr bool paired = false;
#endif
    for (std::size_t frame = 0; frame < kWarmup; ++frame) {
        if (paired && frame % 2 == 0) (void)draw(before, drawing, model, info);
        (void)draw(current, drawing, model, info);
        if (paired && frame % 2 != 0) (void)draw(before, drawing, model, info);
    }

#ifdef HAMMOND_PAINT_ALLOCATIONS
    const auto first_calibration = calibrate();
    require(first_calibration.passed(), "positive allocation/free calibration before observation");
    std::array<allocation_probe::Counts, kSamples> before_counts{}, current_counts{};
    const auto observe = [&](Painter painter) {
        allocation_probe::begin();
        painter(drawing, model, info);
        const int status = SDL_RenderFlush(renderer.get());
        SDL_RenderPresent(renderer.get());
        const auto counts = allocation_probe::end();
        require(status == 0, "flush during heap observation");
        return counts;
    };
    for (std::size_t frame = 0; frame < kSamples; ++frame) {
        if (paired && frame % 2 == 0) before_counts[frame] = observe(before);
        current_counts[frame] = observe(current);
        if (paired && frame % 2 != 0) before_counts[frame] = observe(before);
    }
    const auto last_calibration = calibrate();
    require(last_calibration.passed(), "positive allocation/free calibration after observation");
#else
    std::array<Sample, kSamples> before_samples{}, current_samples{};
    for (std::size_t frame = 0; frame < kSamples; ++frame) {
        if (paired && frame % 2 == 0) before_samples[frame] = draw(before, drawing, model, info);
        current_samples[frame] = draw(current, drawing, model, info);
        if (paired && frame % 2 != 0) before_samples[frame] = draw(before, drawing, model, info);
    }
#endif
    require(layout_fingerprint(model.layout()) == layout_hash &&
            model.view().applied.controls == snapshot.controls &&
            model.view().applied.held_keys == snapshot.held_keys &&
            model.view().applied.held_pedals == snapshot.held_pedals,
            "painting preserves copied model and geometry");
    std::uint64_t before_pixels{};
    if (paired) { (void)draw(before, drawing, model, info); before_pixels = pixels(surface.get()); }
    (void)draw(current, drawing, model, info);
    const auto current_pixels = pixels(surface.get());
    if (paired && (!model.layout().sidebar_pedals || presentation == UiPresentation::Flat))
        require(before_pixels == current_pixels, "inactive refinement keeps identical final pixels");

    SDL_version version{};
    SDL_GetVersion(&version);
    std::cout.imbue(std::locale::classic());
    std::cout << std::fixed << std::setprecision(6)
              << "{\"schema\":\"standalone-paired-paint-v1\",\"width\":" << width
              << ",\"height\":" << height << ",\"presentation\":\"" << presentation_name
              << "\",\"scenario\":\"" << scenario_name << "\",\"overlay\":\"none\",\"workspace\":\"Play\""
              << ",\"paired\":" << (paired ? "true" : "false")
              << ",\"alternating_order\":true,\"warmup_each\":" << kWarmup << ",\"samples_each\":" << kSamples
              << ",\"renderer\":\"" << renderer_info.name << "\",\"renderer_flags\":" << renderer_info.flags
              << ",\"sdl_version\":\"" << static_cast<unsigned>(version.major) << '.'
              << static_cast<unsigned>(version.minor) << '.' << static_cast<unsigned>(version.patch)
              << "\",\"surface_format\":\"" << SDL_GetPixelFormatName(surface->format->format)
              << "\",\"surface_bytes\":" << static_cast<std::size_t>(surface->pitch) * static_cast<std::size_t>(height)
              << ",\"render_batching\":\"" << SDL_GetHint(SDL_HINT_RENDER_BATCHING)
              << "\",\"scale\":[1,1],\"viewport\":[0,0," << width << ',' << height << "],\"clip\":null"
              << ",\"layout_fnv1a64\":\"" << std::hex << layout_hash
              << "\",\"current_pixels_fnv1a64\":\"" << current_pixels
              << "\",\"before_pixels_fnv1a64\":";
    if (paired) std::cout << '"' << before_pixels << '"';
    else std::cout << "null";
    std::cout << std::dec;
#ifdef HAMMOND_PAINT_ALLOCATIONS
    const auto output_counts = [](const auto& counts) {
        std::size_t allocations{}, frees{}, maximum_allocations{}, maximum_frees{};
        for (const auto count : counts) {
            allocations += count.allocations; frees += count.deallocations;
            maximum_allocations = std::max(maximum_allocations, count.allocations);
            maximum_frees = std::max(maximum_frees, count.deallocations);
        }
        std::cout << "{\"allocations\":" << allocations << ",\"frees\":" << frees
                  << ",\"maximum_allocations_per_draw\":" << maximum_allocations
                  << ",\"maximum_frees_per_draw\":" << maximum_frees << '}';
    };
    std::cout << ",\"measurement\":\"current-thread-global-C++-heap\",\"timing_qualified\":false"
              << ",\"positive_calibrations\":2,\"calibrated_allocations\":24,\"calibrated_frees\":24,\"before\":";
    if (paired) output_counts(before_counts); else std::cout << "null";
    std::cout << ",\"current\":"; output_counts(current_counts);
#else
    std::cout << ",\"measurement\":\"software-paint-flush-surface-present\""
              << ",\"heap_instrumentation\":false,\"clock\":\"std::chrono::steady_clock\",\"clock_period\":["
              << Clock::period::num << ',' << Clock::period::den << "],\"before\":";
    if (paired) print_samples(before_samples); else std::cout << "null";
    std::cout << ",\"current\":"; print_samples(current_samples);
    if (paired) {
        std::array<std::int64_t, kSamples> old_total{}, new_total{}, paired_delta{};
        for (std::size_t frame = 0; frame < kSamples; ++frame) {
            old_total[frame] = before_samples[frame].total_ns;
            new_total[frame] = current_samples[frame].total_ns;
            paired_delta[frame] = new_total[frame] - old_total[frame];
        }
        const double before_median = static_cast<double>(median(old_total));
        const double growth_ns = static_cast<double>(median(new_total)) - before_median;
        require(before_median > 0, "positive baseline duration");
        const double growth_percent = 100 * growth_ns / before_median;
        std::cout << ",\"median_growth_ms\":" << growth_ns * 1e-6
                  << ",\"median_growth_percent\":" << growth_percent
                  << ",\"paired_delta\":"; statistics(paired_delta);
        std::cout << ",\"investigation_required\":" <<
            (growth_ns > 2000000 && growth_percent > 15 ? "true" : "false");
    }
#endif
    std::cout << "}\n";
    return EXIT_SUCCESS;
}
} // namespace

int main(int argc, char** argv) {
    SDL_SetMainReady();
    try {
        const int result = run(argc, argv);
        SDL_Quit();
        return result;
    } catch (const std::exception& error) {
        std::cerr << "Paint benchmark failed: " << error.what() << '\n';
        SDL_Quit();
        return EXIT_FAILURE;
    }
}
