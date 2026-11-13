#include "AudioDevice.h"
#include "TestSupport.h"

#include <SDL.h>

#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <memory>
#include <new>
#include <string>
#include <string_view>

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

// Portable aligned storage: retain the malloc base in bytes preceding the
// aligned payload. No dependency on POSIX or MSVC aligned-allocation APIs.
[[nodiscard]] void* allocate_aligned(std::size_t size, std::size_t alignment) {
    if (size == 0) size = 1;
    if (alignment == 0 || (alignment & (alignment - 1)) != 0) throw std::bad_alloc{};
    alignment = std::max(alignment, alignof(void*));
    constexpr auto maximum = std::numeric_limits<std::size_t>::max();
    if (alignment - 1 > maximum - sizeof(void*)) throw std::bad_alloc{};
    const auto overhead = sizeof(void*) + alignment - 1;
    if (size > maximum - overhead) throw std::bad_alloc{};
    void* base = allocate_bytes(size + overhead);
    void* payload = static_cast<unsigned char*>(base) + sizeof(void*);
    auto space = size + alignment - 1;
    if (std::align(alignment, size, payload, space) == nullptr) {
        std::free(base);
        throw std::bad_alloc{};
    }
    std::memcpy(static_cast<unsigned char*>(payload) - sizeof(base), &base, sizeof(base));
    return payload;
}

void free_aligned(void* pointer) noexcept {
    if (pointer == nullptr) return;
    void* base = nullptr;
    std::memcpy(&base, static_cast<unsigned char*>(pointer) - sizeof(base), sizeof(base));
    std::free(base);
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

#undef HAMMOND_PROBE_NOINLINE

namespace {

using namespace hammond;
using namespace hammond::standalone;
using Clock = std::chrono::steady_clock;

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
// Both calibration intervals are disjoint from the production callback interval.
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

constexpr auto kMaximum = std::numeric_limits<std::uint64_t>::max();
constexpr std::size_t kWorkloadsPerBound = 8;
constexpr std::size_t kTimelineRecord = 2 * kWorkloadsPerBound;
constexpr std::size_t kPublicationRecord = kTimelineRecord + 1;
constexpr std::size_t kRecordCount = kPublicationRecord + 1;
constexpr std::array<const char*, kWorkloadsPerBound> kWorkloadNames{
    "cold controls/manuals/pedals/percussion", "full 256-command prefix",
    "manual and pedal note-off", "scoped UI release", "global Panic",
    "active owners before recovery", "pending-release queue overflow",
    "authoritative command rejection"};

struct Observation {
    std::atomic<std::uint64_t> callbacks{};
    std::atomic<std::uint64_t> allocations{};
    std::atomic<std::uint64_t> deallocations{};
    std::atomic<std::uint64_t> before_calibrations{};
    std::atomic<std::uint64_t> after_calibrations{};
    std::atomic<std::uint64_t> calibration_allocations{};
    std::atomic<std::uint64_t> calibration_deallocations{};
    std::atomic<std::uint64_t> thread_failures{};
    std::atomic<std::uint64_t> first_callbacks{};
    std::atomic<std::uint64_t> silent_callbacks{};
    std::atomic<std::uint64_t> nonzero_callbacks{};
    std::atomic<std::uint64_t> output_failures{};
};

// Fixed storage supports exactly one actual SDL device at a time. Main-thread
// setup/teardown is outside all observations and happens with callbacks absent.
struct Capture {
    SDL_AudioCallback original{};
    void* original_userdata{};
    SDL_AudioDeviceID device_id{};
    SDL_threadID main_thread{};
    std::uint32_t buffer_bytes{};
    std::atomic<std::size_t> record{kRecordCount};
    std::atomic<std::uint64_t> callbacks{};
    std::atomic<SDL_threadID> callback_thread{};
    std::atomic<std::uint64_t> harness_failures{};
} capture;

std::array<Observation, kRecordCount> observations;
std::uint64_t observed_posts{};
std::uint64_t observed_reads{};

void add(std::atomic<std::uint64_t>& destination, std::uint64_t value = 1) noexcept {
    destination.fetch_add(value, std::memory_order_relaxed);
}

void SDLCALL observing_callback(void* userdata, Uint8* stream, int byte_count) noexcept {
    auto& context = *static_cast<Capture*>(userdata);
    const auto index = context.record.load(std::memory_order_acquire);
    if (index >= observations.size() || context.original == nullptr) {
        add(context.harness_failures);
        if (stream != nullptr && byte_count > 0) {
            std::memset(stream, 0, static_cast<std::size_t>(byte_count));
        }
        return;
    }
    auto& observation = observations[index];
    const auto ordinal = context.callbacks.fetch_add(1, std::memory_order_relaxed);
    const auto thread = SDL_ThreadID();
    if (ordinal == 0) context.callback_thread.store(thread, std::memory_order_relaxed);
    if (thread == context.main_thread ||
        thread != context.callback_thread.load(std::memory_order_relaxed)) {
        add(observation.thread_failures);
    }

    const auto before = calibrate();
    // The measured region contains only the original AudioDevice callback with
    // its original userdata and the real SDL-provided stream/byte extent.
    allocation_probe::begin();
    context.original(context.original_userdata, stream, byte_count);
    const auto measured = allocation_probe::end();
    const auto after = calibrate();

    add(observation.allocations, static_cast<std::uint64_t>(measured.allocations));
    add(observation.deallocations, static_cast<std::uint64_t>(measured.deallocations));
    if (before.passed()) add(observation.before_calibrations);
    if (after.passed()) add(observation.after_calibrations);
    add(observation.calibration_allocations, static_cast<std::uint64_t>(
        before.allocated.allocations + before.freed.allocations +
        after.allocated.allocations + after.freed.allocations));
    add(observation.calibration_deallocations, static_cast<std::uint64_t>(
        before.allocated.deallocations + before.freed.deallocations +
        after.allocated.deallocations + after.freed.deallocations));
    if (ordinal == 0) add(observation.first_callbacks);

    // Output checks also occur outside the allocation observation. They retain
    // no dynamic buffers and attest actual callback output, including silence.
    if (stream == nullptr || byte_count <= 0 ||
        static_cast<std::uint32_t>(byte_count) != context.buffer_bytes ||
        reinterpret_cast<std::uintptr_t>(stream) % alignof(float) != 0) {
        add(observation.output_failures);
    } else {
        const auto* samples = reinterpret_cast<const float*>(stream);
        const auto count = static_cast<std::size_t>(byte_count) / sizeof(float);
        bool nonzero = false;
        bool invalid = false;
        for (std::size_t sample = 0; sample < count; sample += 2) {
            nonzero = nonzero || samples[sample] != 0.0F || samples[sample + 1] != 0.0F;
            invalid = invalid || !std::isfinite(samples[sample]) ||
                      samples[sample] != samples[sample + 1];
        }
        if (invalid) add(observation.output_failures);
        add(nonzero ? observation.nonzero_callbacks : observation.silent_callbacks);
    }
    observation.callbacks.fetch_add(1, std::memory_order_release);
}

} // namespace

// Only the test's separately compiled AudioDevice.cpp sees the preprocessor
// alias SDL_OpenAudioDevice=hammond_probe_open_audio_device. This translation
// unit uses ordinary SDL.h and delegates to the real SDL_OpenAudioDevice API.
extern "C" SDL_AudioDeviceID SDLCALL hammond_probe_open_audio_device(
    const char* device, int iscapture, const SDL_AudioSpec* desired,
    SDL_AudioSpec* obtained, int allowed_changes) {
    if (capture.device_id != 0 || desired == nullptr || desired->callback == nullptr) {
        SDL_SetError("allocation probe requires one paused callback device");
        return 0;
    }
    capture.original = desired->callback;
    capture.original_userdata = desired->userdata;
    capture.main_thread = SDL_ThreadID();
    capture.callbacks.store(0, std::memory_order_relaxed);
    capture.callback_thread.store(0, std::memory_order_relaxed);
    SDL_AudioSpec wrapped = *desired;
    wrapped.callback = &observing_callback;
    wrapped.userdata = &capture;
    capture.device_id = SDL_OpenAudioDevice(device, iscapture, &wrapped, obtained,
                                            allowed_changes);
    if (capture.device_id != 0 && obtained != nullptr) capture.buffer_bytes = obtained->size;
    return capture.device_id;
}

namespace {

[[nodiscard]] SubmitResult observed_post(Session& session, const SessionCommand& command,
                                          SessionStatus expected = SessionStatus::Ok) {
    allocation_probe::begin();
    const auto result = session.post(command);
    const auto measured = allocation_probe::end();
    CHECK(measured.allocations == 0 && measured.deallocations == 0);
    CHECK(result.status == expected);
    CHECK((result.sequence != 0) == (expected == SessionStatus::Ok));
    ++observed_posts;
    return result;
}

[[nodiscard]] bool observed_read(const Session& session, SessionSnapshot& snapshot) {
    allocation_probe::begin();
    const bool read = session.read_snapshot(snapshot);
    const auto measured = allocation_probe::end();
    CHECK(measured.allocations == 0 && measured.deallocations == 0);
    ++observed_reads;
    return read;
}

[[nodiscard]] SessionSnapshot read(const Session& session) {
    SessionSnapshot snapshot;
    CHECK(observed_read(session, snapshot));
    return snapshot;
}

[[nodiscard]] SessionCommand manual(HostNoteKind kind, std::uint8_t bus,
                                     std::uint8_t channel, std::uint8_t note,
                                     std::int32_t id) {
    return PerformanceInputEvent{HostNoteEvent{
        0, kind, bus, channel, note,
        static_cast<std::uint8_t>(kind == HostNoteKind::On ? 100 : 0), id}};
}

[[nodiscard]] SessionCommand pedal(PedalNoteKind kind) {
    return PerformanceInputEvent{PedalNoteEvent{
        0, kind, 0, kUiInputChannel, PedalId{13},
        static_cast<std::uint8_t>(kind == PedalNoteKind::On ? 100 : 0), 13}};
}

[[nodiscard]] ControlSnapshot registration() {
    ControlSnapshot controls;
    controls.drawbars[0][0][5] = 2;
    controls.drawbars[0][1][2] = 8;
    controls.drawbars[1][1][2] = 6;
    controls.expression = 0.125;
    controls.pedal_drawbars = {6, 4};
    controls.percussion.enabled = true;
    CHECK(is_valid_control_snapshot(controls));
    return controls;
}

[[nodiscard]] std::uint64_t post_notes(Session& session) {
    static_cast<void>(observed_post(session, manual(HostNoteKind::On, 0, 0, 60, 11)));
    static_cast<void>(observed_post(session, manual(HostNoteKind::On, 1, 0, 67, 12)));
    static_cast<void>(observed_post(session, pedal(PedalNoteKind::On)));
    // An independent channel must survive normal UI-scoped release.
    return observed_post(session, manual(HostNoteKind::On, 0, 2, 64, 14)).sequence;
}

[[nodiscard]] bool held(const SessionSnapshot& snapshot, std::size_t manual_index,
                         std::uint8_t note) {
    return snapshot.held_keys[manual_index][note - kMinManualMidiNote];
}

[[nodiscard]] bool no_holds(const SessionSnapshot& snapshot) {
    for (const auto& keys : snapshot.held_keys) {
        if (std::any_of(keys.begin(), keys.end(), [](bool value) { return value; })) return false;
    }
    return std::none_of(snapshot.held_pedals.begin(), snapshot.held_pedals.end(),
                        [](bool value) { return value; });
}

// Pausing only the real SDL device retains Session's running musical state.
// It makes exactly-full queue fixtures deterministic; these main-thread SDL
// pause/lock calls are outside the probe and are never timing observations.
void pause_callbacks() {
    CHECK(capture.device_id != 0);
    SDL_PauseAudioDevice(capture.device_id, 1);
    SDL_LockAudioDevice(capture.device_id);
    SDL_UnlockAudioDevice(capture.device_id);
}

void run_callbacks(AudioDevice& device, Session& session, std::size_t index,
                   bool first = false, std::uint64_t minimum = 2) {
    CHECK(index < observations.size());
    CHECK(observations[index].callbacks.load(std::memory_order_relaxed) == 0);
    capture.record.store(index, std::memory_order_release);
    if (first) {
        std::string error;
        CHECK(device.start(error));
    } else {
        SDL_PauseAudioDevice(capture.device_id, 0);
    }
    const auto deadline = Clock::now() + std::chrono::milliseconds{1500};
    while (observations[index].callbacks.load(std::memory_order_acquire) < minimum) {
        // This independent main-thread observation also exercises publication
        // while the actual callback may be writing it. Busy/exhausted is legal.
        SessionSnapshot snapshot;
        static_cast<void>(observed_read(session, snapshot));
        CHECK(Clock::now() < deadline);
        SDL_Delay(1);
    }
    pause_callbacks();
}

void verify_observation(std::size_t index, const char* label, std::uint16_t frames,
                        bool first = false) {
    const auto& observation = observations[index];
    const auto calls = observation.callbacks.load(std::memory_order_acquire);
    CHECK(calls >= 2);
    CHECK(observation.allocations.load() == 0);
    CHECK(observation.deallocations.load() == 0);
    CHECK(observation.before_calibrations.load() == calls);
    CHECK(observation.after_calibrations.load() == calls);
    CHECK(observation.calibration_allocations.load() == calls * 24);
    CHECK(observation.calibration_deallocations.load() == calls * 24);
    CHECK(observation.thread_failures.load() == 0);
    CHECK(observation.first_callbacks.load() == (first ? 1U : 0U));
    CHECK(observation.output_failures.load() == 0);
    CHECK(observation.silent_callbacks.load() + observation.nonzero_callbacks.load() == calls);
    std::cout << frames << " frames / " << label << ": " << calls
              << " observed callbacks, C++ new=0/delete=0, " << calls * 2
              << " positive callback-thread calibrations\n";
}

void open(AudioDevice& device, Session& session, const RuntimeProfile& profile,
          std::uint16_t frames, std::uint64_t initial_frame = 0) {
    std::string error;
    CHECK(device.open(session, profile, {{}, 48000, frames, 731, initial_frame}, error));
    CHECK(capture.device_id != 0 && capture.original != nullptr);
    const auto info = device.info();
    CHECK(info.driver == "dummy");
    CHECK(info.sample_rate == 48000 && info.buffer_frames == frames);
    CHECK(info.sample_format == AUDIO_F32SYS && info.channels == 2);
    CHECK(info.buffer_bytes == static_cast<std::uint32_t>(frames) * 2U * sizeof(float));
    CHECK(capture.callbacks.load() == 0 && device.diagnostics().callback_count == 0);
}

void close(AudioDevice& device) {
    device.close(); // Actual SDL close joins the callback before capture reuse.
    CHECK(device.diagnostics().callback_count == capture.callbacks.load());
    CHECK(capture.harness_failures.load() == 0);
    capture.device_id = 0;
    capture.original = nullptr;
    capture.original_userdata = nullptr;
    capture.record.store(kRecordCount, std::memory_order_release);
}

void test_empty_session() {
    Session session;
    const auto empty = read(session);
    CHECK(!empty.prepared && empty.publication_revision == 0 && no_holds(empty));
    static_cast<void>(observed_post(session, Panic{}, SessionStatus::NotPrepared));
}

void test_bound(const RuntimeProfile& profile, std::uint16_t frames, std::size_t base) {
    Session session;
    AudioDevice device;
    open(device, session, profile, frames);
    auto controls = registration();
    static_cast<void>(observed_post(session, controls));
    auto sequence = post_notes(session);
    CHECK(read(session).last_applied_sequence == 0); // Still queued before first callback.
    run_callbacks(device, session, base, true);
    auto snapshot = read(session);
    CHECK(snapshot.last_applied_sequence == sequence && snapshot.controls == controls);
    CHECK(held(snapshot, 0, 60) && held(snapshot, 1, 67) && held(snapshot, 0, 64));
    CHECK(snapshot.held_pedals[12] && snapshot.peak > 0.0F);
    CHECK(snapshot.controls.percussion.enabled);
    CHECK(observations[base].nonzero_callbacks.load() != 0);

    // The exact capacity is queued with actual callback quiescence, then the
    // production consumer applies the entire frozen prefix in a real callback.
    for (std::size_t index = 0; index < kSessionCommandCapacity; ++index) {
        controls.expression = 0.125 + static_cast<double>(index % 4) * 0.015625;
        sequence = observed_post(session, controls).sequence;
    }
    run_callbacks(device, session, base + 1);
    snapshot = read(session);
    CHECK(snapshot.last_applied_sequence == sequence && snapshot.resolved_sequence == sequence);
    CHECK(snapshot.controls == controls && snapshot.rejected_commands == 0);
    CHECK(snapshot.discarded_commands == 0 && snapshot.queue_overflows == 0);
    CHECK(held(snapshot, 0, 60) && held(snapshot, 1, 67) && snapshot.held_pedals[12]);

    static_cast<void>(observed_post(session, manual(HostNoteKind::Off, 1, 0, 67, 12)));
    sequence = observed_post(session, pedal(PedalNoteKind::Off)).sequence;
    run_callbacks(device, session, base + 2);
    snapshot = read(session);
    CHECK(snapshot.last_applied_sequence == sequence && !held(snapshot, 1, 67));
    CHECK(!snapshot.held_pedals[12] && held(snapshot, 0, 60) && held(snapshot, 0, 64));

    sequence = observed_post(session, ReleaseUiNotes{}).sequence;
    run_callbacks(device, session, base + 3);
    snapshot = read(session);
    CHECK(snapshot.last_applied_sequence == sequence && !held(snapshot, 0, 60));
    CHECK(held(snapshot, 0, 64)); // Channel 2 survives UI channel 0 release.

    sequence = observed_post(session, Panic{}).sequence;
    run_callbacks(device, session, base + 4);
    snapshot = read(session);
    CHECK(snapshot.last_applied_sequence == sequence && no_holds(snapshot));

    sequence = post_notes(session);
    run_callbacks(device, session, base + 5);
    snapshot = read(session);
    CHECK(snapshot.last_applied_sequence == sequence && snapshot.held_pedals[12]);
    CHECK(held(snapshot, 0, 60) && held(snapshot, 1, 67) && held(snapshot, 0, 64));
    const auto before_overflow = snapshot;
    auto discarded_controls = controls;
    discarded_controls.expression = 0.75;
    for (std::size_t index = 0; index + 1 < kSessionCommandCapacity; ++index) {
        static_cast<void>(observed_post(session, discarded_controls));
    }
    // A pending ordinary release is among the commands discarded by overflow.
    sequence = observed_post(session, manual(HostNoteKind::Off, 0, 0, 60, 11)).sequence;
    static_cast<void>(observed_post(session, ReleaseUiNotes{}, SessionStatus::QueueFull));
    static_cast<void>(observed_post(session, Panic{}, SessionStatus::RecoveryPending));
    run_callbacks(device, session, base + 6);
    snapshot = read(session);
    CHECK(no_holds(snapshot) && snapshot.resolved_sequence == sequence);
    CHECK(snapshot.last_applied_sequence == before_overflow.last_applied_sequence);
    CHECK(snapshot.controls == controls && snapshot.queue_overflows == 1);
    CHECK(snapshot.recovery_count == 1 && snapshot.discarded_commands == kSessionCommandCapacity);
    CHECK((snapshot.fault_flags & static_cast<std::uint32_t>(SessionFault::QueueOverflow)) != 0);

    // The public shape accepts this zero-offset note, then the real core
    // rejects bus 2. The later Panic is discarded and recovery is published.
    const auto rejected = observed_post(session, manual(HostNoteKind::On, 2, 0, 60, 91));
    sequence = observed_post(session, Panic{}).sequence;
    run_callbacks(device, session, base + 7);
    snapshot = read(session);
    CHECK(snapshot.resolved_sequence == sequence && rejected.sequence + 1 == sequence);
    CHECK(snapshot.last_applied_sequence == before_overflow.last_applied_sequence);
    CHECK(snapshot.recovery_count == 2 && snapshot.rejected_commands == 1);
    CHECK(snapshot.discarded_commands == kSessionCommandCapacity + 1 && no_holds(snapshot));
    CHECK(snapshot.last_core_status == Status::InvalidEvent);
    CHECK(snapshot.controls == controls);

    CHECK(device.stop() == SessionStatus::Ok);
    const auto diagnostics = device.diagnostics();
    CHECK(diagnostics.callback_count == capture.callbacks.load());
    CHECK(diagnostics.rendered_frames == diagnostics.callback_count * frames);
    CHECK(diagnostics.render_failures == 0 && diagnostics.format_failures == 0);
    CHECK(diagnostics.nonfinite_failures == 0 && diagnostics.overrange_failures == 0);
    for (std::size_t index = 0; index < kWorkloadsPerBound; ++index) {
        verify_observation(base + index, kWorkloadNames[index], frames, index == 0);
    }
    close(device);
}

void test_render_faults(const RuntimeProfile& profile) {
    {
        Session session;
        AudioDevice device;
        open(device, session, profile, 128, kMaximum - 64);
        static_cast<void>(observed_post(session, registration()));
        static_cast<void>(post_notes(session));
        run_callbacks(device, session, kTimelineRecord, true, 3);
        const auto diagnostics = device.diagnostics();
        CHECK(diagnostics.last_render_status == SessionStatus::TimelineOverflow);
        CHECK(diagnostics.render_failures == diagnostics.callback_count);
        CHECK(diagnostics.rendered_frames == 0 && diagnostics.format_failures == 0);
        CHECK(observations[kTimelineRecord].silent_callbacks.load() == diagnostics.callback_count);
        const auto snapshot = read(session);
        CHECK(snapshot.frame_clock == kMaximum - 64 && snapshot.last_applied_sequence == 0);
        CHECK(device.stop() == SessionStatus::Ok);
        verify_observation(kTimelineRecord, "actual timeline-overflow silence", 128, true);
        close(device);
    }
    {
        // Prepare/start use two publications; two actual successful callbacks
        // leave active owners before the next callback reaches exhaustion.
        Session session{SessionLimits{kMaximum, 4}};
        AudioDevice device;
        open(device, session, profile, 128);
        static_cast<void>(observed_post(session, registration()));
        static_cast<void>(post_notes(session));
        run_callbacks(device, session, kPublicationRecord, true, 4);
        const auto diagnostics = device.diagnostics();
        CHECK(diagnostics.last_render_status == SessionStatus::SequenceExhausted);
        CHECK(diagnostics.rendered_frames == 256);
        CHECK(diagnostics.render_failures == diagnostics.callback_count - 2);
        CHECK(diagnostics.format_failures == 0 && diagnostics.nonfinite_failures == 0);
        CHECK(observations[kPublicationRecord].nonzero_callbacks.load() == 2);
        CHECK(observations[kPublicationRecord].silent_callbacks.load() == diagnostics.render_failures);
        SessionSnapshot unchanged;
        unchanged.frame_clock = 1234;
        unchanged.publication_revision = 42;
        unchanged.controls.expression = 0.625;
        CHECK(!observed_read(session, unchanged));
        CHECK(unchanged.frame_clock == 1234 && unchanged.publication_revision == 42);
        CHECK(unchanged.controls.expression == 0.625);
        static_cast<void>(observed_post(session, Panic{}, SessionStatus::SequenceExhausted));
        CHECK(device.stop() == SessionStatus::SequenceExhausted);
        verify_observation(kPublicationRecord, "active-state publication exhaustion", 128, true);
        close(device);
    }
}

} // namespace

int main() {
    const auto* selected = SDL_getenv("SDL_AUDIODRIVER");
    CHECK(selected != nullptr && std::string_view{selected} == "dummy");
    const auto profile = load_test_profile();
    CHECK(calibrate().passed()); // Separate main-thread post/read calibration.
    test_empty_session();
    SDL_SetMainReady();
    CHECK(SDL_Init(SDL_INIT_AUDIO) == 0);
    CHECK(std::string_view{SDL_GetCurrentAudioDriver()} == "dummy");
    test_bound(profile, 128, 0);
    test_bound(profile, 2048, kWorkloadsPerBound);
    test_render_faults(profile);
    CHECK(capture.device_id == 0 && capture.harness_failures.load() == 0);
    SDL_Quit();
    CHECK(calibrate().passed());
    CHECK((SDL_WasInit(SDL_INIT_AUDIO) & SDL_INIT_AUDIO) == 0);

    std::uint64_t callbacks = 0;
    for (const auto& observation : observations) callbacks += observation.callbacks.load();
    CHECK(callbacks >= 39);
    CHECK(observed_posts > 1024 && observed_reads != 0);
    std::cout << "Calibrated standalone callback allocation: " << kRecordCount
              << " workload observations, " << callbacks << " real SDL dummy callbacks, "
              << callbacks * 24 << " positive calibration allocations and frees, "
              << observed_posts << " main-thread posts, " << observed_reads
              << " main-thread snapshot reads; production regions C++ new=0/delete=0.\n"
              << "Scope excludes C/system allocation, locks, deadlines, physical devices, "
                 "and other platforms.\n";
    return 0;
}
