#include "TestSupport.h"
#include "hammond/Engine.h"
#include "hammond/PerformanceInput.h"
#include "hammond/HostTimeline.h"
#include "hammond/StateExchange.h"
#include "hammond/ControlStateIO.h"
#include "hammond/ParameterBridge.h"

#include <algorithm>
#include <array>
#include <bit>
#include <chrono>
#include <sstream>
#include <type_traits>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <memory>
#include <new>
#include <span>
#include <vector>

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
constexpr float sentinel = -1234.5F;


// Explicit calls through volatile function pointers prevent new-expression
// allocation elision from making the instrumentation calibration vacuous.
template <typename Function>
[[nodiscard]] Function opaque(Function function) noexcept {
    Function volatile pointer = function;
    return pointer;
}

void test_probe_overloads() {
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

    // Calibration is deliberately separate from all Engine observations.
    allocation_probe::begin();
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
    const auto allocated = allocation_probe::end();
    CHECK(allocated.allocations == pointers.size());
    CHECK(allocated.deallocations == 0);
    for (std::size_t index = 0; index < pointers.size(); ++index) {
        CHECK(pointers[index] != nullptr);
        if (index >= 6) CHECK(reinterpret_cast<std::uintptr_t>(pointers[index]) % 64 == 0);
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
    const auto freed = allocation_probe::end();
    CHECK(freed.allocations == 0);
    CHECK(freed.deallocations == pointers.size());
}

// This audit reuses only the calibrated interposition machinery above. Its
// enabled musical fixtures and expectations are independent of the console
// audit. Preparation, parsing, arrays, snapshots and diagnostics stay outside
// each observed API call. The steady-clock samples include probe overhead.
enum class Path : std::size_t {
    Engine, ManualOwners, PedalOwners, Combined, Timeline, Exchange, Callback,
    Lifecycle, Count
};
struct Totals {
    std::size_t calls{};
    std::size_t accepted{};
    std::size_t rejected{};
    std::uint64_t frames{};
    std::uint64_t records{};
    std::uint64_t physical{};
    std::size_t allocations{};
    std::size_t deallocations{};
    double elapsed_us{};
    double maximum_us{};
};
std::array<Totals, static_cast<std::size_t>(Path::Count)> totals{};
std::uint64_t audio_hash = 14695981039346656037ULL;
std::uint64_t audio_samples = 0;
std::uint64_t phase_comparisons = 0;
std::uint64_t audio_comparisons = 0;
constexpr auto upper = Manual::Upper;
constexpr auto lower = Manual::Lower;

// These are value-owned candidates: no refcount, owning pointer, destructor or
// allocator can be reached by their copy/assignment. Spans in queue inputs are
// borrowed for the call only. This assertion is stronger than observing a few
// successful copies, but does not prove all other code has no C allocator use.
static_assert(std::is_trivially_copyable_v<Engine>);
static_assert(std::is_trivially_copyable_v<NoteOwnership>);
static_assert(std::is_trivially_copyable_v<PedalNoteOwnership>);
static_assert(std::is_trivially_copyable_v<ControlSnapshot>);
static_assert(std::is_trivially_copyable_v<PerformanceInputEvent>);
static_assert(std::is_trivially_copyable_v<HostTimeline>);
static_assert(std::is_trivially_copyable_v<StateExchangeBatch>);
static_assert(!std::is_copy_constructible_v<StateExchange>);
static_assert(std::atomic<std::uint64_t>::is_always_lock_free);
static_assert(std::chrono::steady_clock::is_steady);

Totals& counts(Path path) { return totals[static_cast<std::size_t>(path)]; }
template <typename Function>
auto observe(Path path, Function function) {
    CHECK(!allocation_probe::recording);
    const auto start = std::chrono::steady_clock::now();
    allocation_probe::begin();
    const auto result = function();
    const auto observed = allocation_probe::end();
    const auto end = std::chrono::steady_clock::now();
    CHECK(end >= start);
    const double elapsed = std::chrono::duration<double, std::micro>(end - start).count();
    CHECK(std::isfinite(elapsed) && elapsed >= 0.0);
    auto& total = counts(path);
    ++total.calls;
    total.allocations += observed.allocations;
    total.deallocations += observed.deallocations;
    total.elapsed_us += elapsed;
    total.maximum_us = std::max(total.maximum_us, elapsed);
    CHECK(observed.allocations == 0);
    CHECK(observed.deallocations == 0);
    return result;
}
void record(Path path, bool accepted, std::uint32_t frames = 0,
            std::uint64_t records = 0, std::uint64_t physical = 0) {
    auto& total = counts(path);
    if (accepted) {
        ++total.accepted;
        total.frames += frames;
        total.records += records;
        total.physical += physical;
    } else {
        ++total.rejected;
    }
}
void inspect_audio(std::span<const float> audio, bool audible = true) {
    double energy = 0.0;
    for (const auto sample : audio) {
        CHECK(std::isfinite(sample));
        energy += static_cast<double>(sample) * sample;
        audio_hash ^= std::bit_cast<std::uint32_t>(sample);
        audio_hash *= 1099511628211ULL;
        ++audio_samples;
    }
    CHECK(std::isfinite(energy));
    if (audible) CHECK(energy > 0.0);
}
void same_audio(std::span<const float> a, std::span<const float> b) {
    CHECK(a.size() == b.size());
    for (std::size_t i = 0; i < a.size(); ++i) {
        CHECK(std::bit_cast<std::uint32_t>(a[i]) == std::bit_cast<std::uint32_t>(b[i]));
        ++audio_comparisons;
    }
}
void same_phases(const Engine& a, const Engine& b) {
    for (std::uint32_t source = 1; source <= kToneSourceCount; ++source) {
        double first = -1.0, second = -1.0;
        CHECK(a.source_phase_turns(static_cast<ToneId>(source), first));
        CHECK(b.source_phase_turns(static_cast<ToneId>(source), second));
        CHECK(std::bit_cast<std::uint64_t>(first) == std::bit_cast<std::uint64_t>(second));
        ++phase_comparisons;
    }
}
void same_engine(const Engine& a, const Engine& b) {
    CHECK(a.prepared() == b.prepared());
    CHECK(a.frame_clock() == b.frame_clock());
    CHECK(a.sample_rate() == b.sample_rate());
    CHECK(a.controls_snapshot() == b.controls_snapshot());
    CHECK(a.active_key_count() == b.active_key_count());
    CHECK(a.active_pedal_count() == b.active_pedal_count());
    CHECK(a.percussion_diagnostics() == b.percussion_diagnostics());
    CHECK(a.last_pedal_frame() == b.last_pedal_frame());
    PedalContactStates first{}, second{};
    CHECK(a.pedal_contacts_snapshot(first));
    CHECK(b.pedal_contacts_snapshot(second));
    CHECK(first == second);
    for (std::uint32_t pedal = 1; pedal <= kPedalCount; ++pedal) {
        const PedalId id{static_cast<std::uint8_t>(pedal)};
        CHECK(a.pedal_down(id) == b.pedal_down(id));
    }
    for (const auto manual : {upper, lower}) {
        for (std::uint32_t note = 36; note <= 96; ++note) {
            CHECK(a.key_down(manual, note) == b.key_down(manual, note));
            ContactKeySnapshot ac{}, bc{};
            CHECK(a.contact_snapshot(manual, note, ac));
            CHECK(b.contact_snapshot(manual, note, bc));
            CHECK(ac == bc);
        }
    }
    same_phases(a, b);
}
ControlSnapshot sounding_controls() {
    ControlSnapshot controls;
    for (auto& manual : controls.drawbars) {
        for (auto& bank : manual) bank.fill(6);
    }
    controls.expression = 0.75;
    controls.percussion.enabled = true;
    controls.pedal_drawbars = {8, 6};
    return controls;
}
ProcessResult engine_call(Engine& engine, std::uint32_t frames,
                          std::span<float> output, std::span<const Event> events,
                          Status expected = Status::Ok) {
    const auto before = engine.frame_clock();
    const auto result = observe(Path::Engine, [&] { return engine.process(frames, output, events); });
    record(Path::Engine, result.ok(), frames, result.events_consumed, result.events_consumed);
    CHECK(result.status == expected);
    CHECK(result.events_consumed == (result.ok() ? events.size() : 0));
    CHECK(engine.frame_clock() == before + (result.ok() ? frames : 0));
    return result;
}
void rejected_engine(Engine& engine, std::uint32_t frames,
                     std::span<const Event> events, Status status,
                     std::size_t output_size = 64) {
    Engine reference = engine;
    std::array<float, 128> buffer{};
    buffer.fill(sentinel);
    engine_call(engine, frames, {buffer.data(), output_size}, events, status);
    CHECK(std::all_of(buffer.begin(), buffer.end(), [](float value) { return value == sentinel; }));
    same_engine(engine, reference);
    std::array<float, 32> actual{}, expected{};
    engine_call(engine, 32, actual, {});
    CHECK(reference.process(32, expected, {}));
    same_audio(actual, expected);
    same_engine(engine, reference);
    inspect_audio(actual);
}
void test_engine(const RuntimeProfile& profile) {
    std::array<Event, kManualCount * kManualKeyCount + kPedalCount> on{};
    std::size_t cursor = 0;
    for (const auto manual : {upper, lower}) {
        for (std::uint32_t note = 36; note <= 96; ++note) {
            on[cursor++] = {0, EventType::NoteOn, manual, static_cast<std::uint8_t>(note), 100};
        }
    }
    for (std::uint32_t pedal = 1; pedal <= kPedalCount; ++pedal) {
        on[cursor++] = {0, EventType::PedalOn, lower, static_cast<std::uint8_t>(pedal), 100};
    }
    CHECK(cursor == 147);
    std::array<Event, kMaxEventsPerBlock> dense{};
    for (std::size_t i = 0; i < dense.size(); ++i) {
        const auto offset = static_cast<std::uint32_t>(i);
        if (i % 3 == 0) {
            dense[i] = {offset, EventType::Expression, upper, 0,
                        static_cast<double>(i % 8 + 1) / 8.0};
        } else if (i % 3 == 1) {
            // Keep key96 fully pressed so upper contact8 drives percussion
            // while the other keys perform partial travel.
            dense[i] = {offset, EventType::KeyPosition, (i % 2 == 0 ? upper : lower),
                        static_cast<std::uint8_t>(36 + i % 60), (i % 2 == 0 ? 0.3 : 1.0)};
        } else {
            dense[i] = {offset, EventType::PedalDrawbar, lower,
                        static_cast<std::uint8_t>(i % 2), static_cast<double>(i % 8 + 1)};
        }
    }
    std::vector<float> output(kHardMaxBlockFrames + 2, sentinel);
    const auto console = make_nominal_console_model();
    const auto controls = sounding_controls();
    for (const auto rate : {44100.0, 48000.0, 96000.0}) {
        std::fill(output.begin(), output.end(), sentinel);
        Engine engine;
        CHECK(engine.prepare(profile, {rate, kHardMaxBlockFrames, 37, 1000}, console) == Status::Ok);
        CHECK(engine.restore_controls(controls));
        const Engine initial = engine;
        engine_call(engine, 0, {}, on);
        CHECK(engine.active_key_count() == 122 && engine.active_pedal_count() == 25);
        CHECK(engine.percussion_diagnostics().readiness == 1.0);
        same_phases(engine, initial);
        ContactKeySnapshot key{};
        CHECK(engine.contact_snapshot(upper, 36, key));
        CHECK(key.position == 0.0 && key.target == 1.0);
        PedalContactStates contacts{};
        CHECK(engine.pedal_contacts_snapshot(contacts));
        CHECK(std::all_of(contacts.begin(), contacts.end(), [](bool closed) { return closed; }));
        engine_call(engine, 64, {output.data(), 66}, {});
        CHECK(output[64] == sentinel && output[65] == sentinel);
        inspect_audio({output.data(), 64});
        CHECK(engine.contact_snapshot(upper, 36, key));
        CHECK(key.position > 0.0 && key.position < 1.0);
        engine_call(engine, 1024, {output.data(), 1024}, dense);
        inspect_audio({output.data(), 1024});
        CHECK(engine.active_key_count() == 122 && engine.active_pedal_count() == 25);
        CHECK(engine.percussion_diagnostics().routed_detector);
        CHECK(engine.percussion_diagnostics().readiness < 1.0);
        Engine reference = engine;
        engine_call(engine, 513, {}, {});
        CHECK(reference.process(513, {output.data(), 513}, {}));
        same_engine(engine, reference);
        std::array<float, 32> actual{}, expected{};
        engine_call(engine, 32, actual, {});
        CHECK(reference.process(32, expected, {}));
        same_audio(actual, expected);
        inspect_audio(actual);
        engine_call(engine, kHardMaxBlockFrames, {output.data(), kHardMaxBlockFrames}, {});
        inspect_audio({output.data(), kHardMaxBlockFrames});
        CHECK(engine.last_pedal_frame().valid);
        CHECK(engine.last_pedal_frame().frame + 1 == engine.frame_clock());
        CHECK(engine.last_pedal_frame().positions == engine.controls_snapshot().pedal_drawbars);
        const std::array<Event, 2> late_bad{{
            {0, EventType::PedalOff, lower, 1, 0},
            {3, EventType::PedalDrawbar, lower, 1, 8.5}}};
        rejected_engine(engine, 64, late_bad, Status::InvalidEvent);
        const std::array<Event, 1> boundary{{{64, EventType::PedalOff, lower, 2, 0}}};
        rejected_engine(engine, 64, boundary, Status::InvalidEvent);
        rejected_engine(engine, 64, {}, Status::InvalidBuffer, 63);
        rejected_engine(engine, kHardMaxBlockFrames + 1, {}, Status::BlockTooLarge);
        std::array<Event, kMaxEventsPerBlock + 1> excessive{};
        excessive.fill({0, EventType::PedalDrawbar, lower, 0, 8});
        rejected_engine(engine, 64, excessive, Status::TooManyEvents);
        const Engine before_rate = engine;
        const double new_rate = rate == 96000.0 ? 44100.0 : 96000.0;
        auto status = observe(Path::Lifecycle, [&] { return engine.reconfigure_sample_rate(new_rate); });
        record(Path::Lifecycle, status == Status::Ok);
        CHECK(status == Status::Ok && engine.sample_rate() == new_rate);
        same_phases(engine, before_rate);
        CHECK(engine.frame_clock() == before_rate.frame_clock());
        CHECK(engine.last_pedal_frame() == before_rate.last_pedal_frame());
        CHECK(engine.controls_snapshot() == before_rate.controls_snapshot());
        const Engine migrated = engine;
        status = observe(Path::Lifecycle, [&] { return engine.reconfigure_sample_rate(new_rate); });
        record(Path::Lifecycle, status == Status::Ok);
        CHECK(status == Status::Ok);
        same_engine(engine, migrated);
        status = observe(Path::Lifecycle, [&] { return engine.reconfigure_sample_rate(32000); });
        record(Path::Lifecycle, status == Status::Ok);
        CHECK(status == Status::InvalidSpec);
        same_engine(engine, migrated);
        engine_call(engine, 32, actual, {});
        Engine migrated_reference = migrated;
        CHECK(migrated_reference.process(32, expected, {}));
        same_audio(actual, expected);
        inspect_audio(actual);
        const auto pre_panic = engine;
        const std::array<Event, 1> panic{{{0, EventType::PedalAllNotesOff, lower, 0, 0}}};
        engine_call(engine, 0, {}, panic);
        CHECK(engine.active_pedal_count() == 0 && engine.active_key_count() == 122);
        CHECK(engine.controls_snapshot() == pre_panic.controls_snapshot());
        CHECK(engine.last_pedal_frame() == pre_panic.last_pedal_frame());
        same_phases(engine, pre_panic);
        CHECK(engine.pedal_contacts_snapshot(contacts));
        CHECK(std::none_of(contacts.begin(), contacts.end(), [](bool closed) { return closed; }));
    }
    Engine fresh;
    engine_call(fresh, 0, {}, {}, Status::NotPrepared);
    CHECK(fresh.prepare(profile, {48000, 64, 37, std::numeric_limits<std::uint64_t>::max() - 8},
                        console) == Status::Ok);
    CHECK(fresh.restore_controls(controls));
    engine_call(fresh, 0, {}, on);
    const Engine before_overflow = fresh;
    output.assign(output.size(), sentinel);
    engine_call(fresh, 9, {output.data(), 9}, {}, Status::TimelineOverflow);
    same_engine(fresh, before_overflow);
    CHECK(output.front() == sentinel);
    engine_call(fresh, 8, {output.data(), 8}, {});
    inspect_audio({output.data(), 8});
}

void check_event(const Event& event, EventType type, Manual manual, std::uint8_t index) {
    CHECK(event.type == type && event.manual == manual && event.index == index && event.offset == 0);
}
void test_owners() {
    NoteOwnership manual;
    PedalNoteOwnership pedal;
    std::array<HostNoteEvent, 256> manual_on{};
    std::array<PedalNoteEvent, 256> pedal_on{};
    for (std::size_t i = 0; i < 256; ++i) {
        manual_on[i] = {0, HostNoteKind::On, static_cast<std::uint8_t>((i % 122) / 61),
                        0, static_cast<std::uint8_t>(36 + i % 61), 100,
                        static_cast<std::int32_t>(i)};
        pedal_on[i] = {0, PedalNoteKind::On, static_cast<std::uint8_t>(i % 2), 0,
                       PedalId{static_cast<std::uint8_t>(1 + i % 25)}, 100,
                       static_cast<std::int32_t>(i)};
    }
    const Event marker{999, EventType::Cancel, upper, 99, sentinel};
    std::array<Event, 1024> output{};
    output.fill(marker);
    auto mr = observe(Path::ManualOwners, [&] { return manual.translate(0, manual_on, output); });
    record(Path::ManualOwners, mr.ok(), 0, mr.input_consumed, mr.output_events);
    CHECK(mr && mr.input_consumed == 256 && mr.output_events == 122);
    CHECK(manual.owner_count() == 256);
    for (std::size_t i = 0; i < 122; ++i) {
        check_event(output[i], EventType::NoteOn, i < 61 ? upper : lower,
                    static_cast<std::uint8_t>(36 + i % 61));
    }
    CHECK(output[122].offset == marker.offset);
    output.fill(marker);
    auto pr = observe(Path::PedalOwners, [&] { return pedal.translate(0, pedal_on, output); });
    record(Path::PedalOwners, pr.ok(), 0, pr.input_consumed, pr.output_events);
    CHECK(pr && pr.input_consumed == 256 && pr.output_events == 25);
    CHECK(pedal.owner_count() == 256);
    for (std::size_t i = 0; i < 25; ++i) {
        check_event(output[i], EventType::PedalOn, lower, static_cast<std::uint8_t>(i + 1));
    }
    CHECK(output[25].offset == marker.offset);
    // Duplicate identities consume raw input without adding owners or output.
    mr = observe(Path::ManualOwners, [&] { return manual.translate(64, manual_on, {}); });
    record(Path::ManualOwners, mr.ok(), 0, mr.input_consumed, mr.output_events);
    CHECK(mr && mr.input_consumed == 256 && mr.output_events == 0);
    pr = observe(Path::PedalOwners, [&] { return pedal.translate(64, pedal_on, {}); });
    record(Path::PedalOwners, pr.ok(), 0, pr.input_consumed, pr.output_events);
    CHECK(pr && pr.input_consumed == 256 && pr.output_events == 0);
    const NoteOwnership manual_before = manual;
    const PedalNoteOwnership pedal_before = pedal;
    auto extra_manual = manual_on[0]; extra_manual.note_id = 1000;
    auto extra_pedal = pedal_on[0]; extra_pedal.note_id = 1000;
    output.fill(marker);
    mr = observe(Path::ManualOwners, [&] { return manual.translate(64, {&extra_manual, 1}, output); });
    record(Path::ManualOwners, mr.ok());
    CHECK(mr.status == Status::TooManyEvents && mr.input_consumed == 0 && mr.output_events == 0);
    pr = observe(Path::PedalOwners, [&] { return pedal.translate(64, {&extra_pedal, 1}, output); });
    record(Path::PedalOwners, pr.ok());
    CHECK(pr.status == Status::TooManyEvents && pr.input_consumed == 0 && pr.output_events == 0);
    CHECK(manual == manual_before && pedal == pedal_before);
    CHECK(std::all_of(output.begin(), output.end(), [&](const Event& event) {
        return event.offset == marker.offset && event.value == marker.value;
    }));
    // Invalid final records cannot release a valid earlier owner.
    std::array<HostNoteEvent, 2> bad_manual{{manual_on[0], manual_on[1]}};
    bad_manual[0].kind = HostNoteKind::Off; bad_manual[0].velocity = 0;
    bad_manual[1].offset = 64;
    std::array<PedalNoteEvent, 2> bad_pedal{{pedal_on[0], pedal_on[1]}};
    bad_pedal[0].kind = PedalNoteKind::Off; bad_pedal[0].velocity = 0;
    bad_pedal[1].pedal = PedalId{0};
    mr = observe(Path::ManualOwners, [&] { return manual.translate(64, bad_manual, output); });
    record(Path::ManualOwners, mr.ok());
    pr = observe(Path::PedalOwners, [&] { return pedal.translate(64, bad_pedal, output); });
    record(Path::PedalOwners, pr.ok());
    CHECK(mr.status == Status::InvalidEvent && pr.status == Status::InvalidEvent);
    CHECK(mr.input_consumed == 0 && mr.output_events == 0);
    CHECK(pr.input_consumed == 0 && pr.output_events == 0);
    CHECK(manual == manual_before && pedal == pedal_before);
    CHECK(output.front().offset == marker.offset && output.back().offset == marker.offset);
    // Scope bus 0, then bus 1; all owners are on channel 0. Pedal bus 1 still
    // owns every pitch after bus 0 is cleared, so its first panic emits nothing.
    const std::array<HostNoteEvent, 2> manual_panics{{
        {0, HostNoteKind::AllNotesOff, 0, 0, 0, 0, -1},
        {0, HostNoteKind::AllNotesOff, 1, 0, 0, 0, -1}}};
    const std::array<PedalNoteEvent, 2> pedal_panics{{
        {0, PedalNoteKind::AllNotesOff, 0, 0, PedalId{0}, 0, -1},
        {0, PedalNoteKind::AllNotesOff, 1, 0, PedalId{0}, 0, -1}}};
    mr = observe(Path::ManualOwners, [&] { return manual.translate(0, manual_panics, output); });
    record(Path::ManualOwners, mr.ok(), 0, mr.input_consumed, mr.output_events);
    CHECK(mr && mr.input_consumed == 2 && mr.output_events == 122 && manual.owner_count() == 0);
    pr = observe(Path::PedalOwners, [&] { return pedal.translate(0, {pedal_panics.data(), 1}, output); });
    record(Path::PedalOwners, pr.ok(), 0, pr.input_consumed, pr.output_events);
    CHECK(pr && pr.output_events == 0 && pedal.owner_count() == 128);
    pr = observe(Path::PedalOwners, [&] { return pedal.translate(0, {pedal_panics.data() + 1, 1}, output); });
    record(Path::PedalOwners, pr.ok(), 0, pr.input_consumed, pr.output_events);
    CHECK(pr && pr.output_events == 25 && pedal.owner_count() == 0);
    for (std::size_t i = 0; i < pr.output_events; ++i) CHECK(output[i].type == EventType::PedalOff);
    // A dense stream of anonymous repetitions repeatedly reaches zero. Its
    // expected 1024 transitions follows the independent first/last-owner rule.
    std::array<HostNoteEvent, 1024> dense_manual{};
    std::array<PedalNoteEvent, 1024> dense_pedal{};
    for (std::size_t i = 0; i < 1024; ++i) {
        const bool on = i % 2 == 0;
        dense_manual[i] = {static_cast<std::uint32_t>(i), on ? HostNoteKind::On : HostNoteKind::Off,
                           0, 3, 60, static_cast<std::uint8_t>(on ? 100 : 0), -1};
        dense_pedal[i] = {static_cast<std::uint32_t>(i), on ? PedalNoteKind::On : PedalNoteKind::Off,
                          0, 3, PedalId{13}, static_cast<std::uint8_t>(on ? 100 : 0), -1};
    }
    mr = observe(Path::ManualOwners, [&] { return manual.translate(1024, dense_manual, output); });
    record(Path::ManualOwners, mr.ok(), 0, mr.input_consumed, mr.output_events);
    CHECK(mr && mr.input_consumed == 1024 && mr.output_events == 1024 && manual.owner_count() == 0);
    pr = observe(Path::PedalOwners, [&] { return pedal.translate(1024, dense_pedal, output); });
    record(Path::PedalOwners, pr.ok(), 0, pr.input_consumed, pr.output_events);
    CHECK(pr && pr.input_consumed == 1024 && pr.output_events == 1024 && pedal.owner_count() == 0);
}

PerformanceInputResult combined_call(Engine& engine, NoteOwnership& manual,
                                      PedalNoteOwnership& pedal, std::uint32_t frames,
                                      std::span<float> output,
                                      std::span<const PerformanceInputEvent> input,
                                      Status expected = Status::Ok) {
    const auto clock = engine.frame_clock();
    const auto result = observe(Path::Combined, [&] {
        return process_performance_input(engine, manual, pedal, frames, output, input);
    });
    record(Path::Combined, result.ok(), frames, result.input_events_consumed,
           result.physical_events_consumed);
    CHECK(result.status == expected);
    CHECK(result.input_events_consumed == (result.ok() ? input.size() : 0));
    if (!result) CHECK(result.physical_events_consumed == 0);
    CHECK(engine.frame_clock() == clock + (result.ok() ? frames : 0));
    return result;
}
void test_combined(const RuntimeProfile& profile) {
    Engine engine;
    NoteOwnership manual;
    PedalNoteOwnership pedal;
    const auto console = make_nominal_console_model();
    CHECK(engine.prepare(profile, {48000, kHardMaxBlockFrames, 87, 700}, console) == Status::Ok);
    CHECK(engine.restore_controls(sounding_controls()));
    std::array<PerformanceInputEvent, 512> on{};
    for (std::size_t i = 0; i < 256; ++i) {
        on[2 * i] = HostNoteEvent{0, HostNoteKind::On,
            static_cast<std::uint8_t>((i % 122) / 61), 0,
            static_cast<std::uint8_t>(36 + i % 61), 100, static_cast<std::int32_t>(i)};
        on[2 * i + 1] = PedalNoteEvent{0, PedalNoteKind::On,
            static_cast<std::uint8_t>(i % 2), 0,
            PedalId{static_cast<std::uint8_t>(1 + i % 25)}, 100, static_cast<std::int32_t>(i)};
    }
    const Engine before_notes = engine;
    auto result = combined_call(engine, manual, pedal, 0, {}, on);
    CHECK(result.physical_events_consumed == 147);
    CHECK(manual.owner_count() == 256 && pedal.owner_count() == 256);
    CHECK(engine.active_key_count() == 122 && engine.active_pedal_count() == 25);
    same_phases(engine, before_notes);
    std::vector<float> output(kHardMaxBlockFrames + 2, sentinel);
    result = combined_call(engine, manual, pedal, 64, {output.data(), 66}, on);
    CHECK(result.physical_events_consumed == 0);
    CHECK(output[64] == sentinel && output[65] == sentinel);
    inspect_audio({output.data(), 64});
    std::array<PerformanceInputEvent, 1024> dense{};
    for (std::size_t i = 0; i < dense.size(); ++i) {
        dense[i] = Event{static_cast<std::uint32_t>(i), EventType::Expression, upper,
                         0, static_cast<double>(i % 8 + 1) / 8.0};
    }
    result = combined_call(engine, manual, pedal, 1024, {output.data(), 1024}, dense);
    CHECK(result.physical_events_consumed == 1024);
    inspect_audio({output.data(), 1024});
    CHECK(engine.percussion_diagnostics().routed_detector);
    Engine disconnected_reference = engine;
    result = combined_call(engine, manual, pedal, 257, {}, {});
    CHECK(result.physical_events_consumed == 0);
    CHECK(disconnected_reference.process(257, {output.data(), 257}, {}));
    same_engine(engine, disconnected_reference);
    combined_call(engine, manual, pedal, kHardMaxBlockFrames,
                  {output.data(), kHardMaxBlockFrames}, {});
    inspect_audio({output.data(), kHardMaxBlockFrames});
    // A failed last control must not release the first two physical notes or
    // either ownership identity. Future output also detects hidden mutation.
    const std::array<PerformanceInputEvent, 3> invalid{{
        HostNoteEvent{0, HostNoteKind::Off, 0, 0, 36, 0, 0},
        PedalNoteEvent{0, PedalNoteKind::Off, 0, 0, PedalId{1}, 0, 0},
        Event{3, EventType::PedalDrawbar, lower, 1, std::numeric_limits<double>::quiet_NaN()}}};
    auto reject = [&](std::uint32_t frames, std::span<const PerformanceInputEvent> input,
                      Status status, std::size_t size = 64) {
        Engine reference = engine;
        const auto manual_reference = manual;
        const auto pedal_reference = pedal;
        output.assign(output.size(), sentinel);
        combined_call(engine, manual, pedal, frames, {output.data(), size}, input, status);
        CHECK(std::all_of(output.begin(), output.end(), [](float value) { return value == sentinel; }));
        CHECK(manual == manual_reference && pedal == pedal_reference);
        same_engine(engine, reference);
        std::array<float, 32> expected{};
        combined_call(engine, manual, pedal, 32, {output.data(), 32}, {});
        CHECK(reference.process(32, expected, {}));
        same_audio({output.data(), 32}, expected);
        same_engine(engine, reference);
        inspect_audio({output.data(), 32});
    };
    reject(64, invalid, Status::InvalidEvent);
    const std::array<PerformanceInputEvent, 1> extra_manual{{
        HostNoteEvent{0, HostNoteKind::On, 0, 0, 60, 100, 1000}}};
    const std::array<PerformanceInputEvent, 1> extra_pedal{{
        PedalNoteEvent{0, PedalNoteKind::On, 0, 0, PedalId{13}, 100, 1000}}};
    reject(64, extra_manual, Status::TooManyEvents);
    reject(64, extra_pedal, Status::TooManyEvents);
    reject(64, {}, Status::InvalidBuffer, 63);
    reject(kHardMaxBlockFrames + 1, {}, Status::BlockTooLarge);
    std::array<PerformanceInputEvent, 1025> excessive{};
    excessive.fill(Event{0, EventType::PedalDrawbar, lower, 0, 8});
    reject(64, excessive, Status::TooManyEvents);
    const std::array<PerformanceInputEvent, 4> panics{{
        HostNoteEvent{0, HostNoteKind::AllNotesOff, 0, 0, 0, 0, -1},
        PedalNoteEvent{0, PedalNoteKind::AllNotesOff, 0, 0, PedalId{0}, 0, -1},
        HostNoteEvent{0, HostNoteKind::AllNotesOff, 1, 0, 0, 0, -1},
        PedalNoteEvent{0, PedalNoteKind::AllNotesOff, 1, 0, PedalId{0}, 0, -1}}};
    const auto prior = engine;
    result = combined_call(engine, manual, pedal, 0, {}, panics);
    CHECK(result.physical_events_consumed == 147);
    CHECK(manual.owner_count() == 0 && pedal.owner_count() == 0);
    CHECK(engine.active_key_count() == 0 && engine.active_pedal_count() == 0);
    CHECK(engine.controls_snapshot() == prior.controls_snapshot());
    same_phases(engine, prior);
}

HostTimelineResult timeline_call(HostTimeline& timeline, std::uint32_t frames,
                                  std::span<float> output,
                                  std::span<const HostParameterQueue> parameters,
                                  std::span<const HostMusicalEvent> music,
                                  std::span<const ControlSnapshot> restores = {},
                                  Status expected = Status::Ok) {
    const auto clock = timeline.engine().frame_clock();
    const auto result = observe(Path::Timeline, [&] {
        return timeline.process(frames, output, parameters, music, restores);
    });
    record(Path::Timeline, result.ok(), frames,
           result.input_records_consumed + result.carried_records_consumed,
           result.physical_events_applied);
    CHECK(result.status == expected);
    CHECK(timeline.engine().frame_clock() == clock + (result.ok() ? frames : 0));
    if (!result) {
        CHECK(result.input_records_consumed == 0 && result.carried_records_consumed == 0);
        CHECK(result.restores_consumed == 0 && result.physical_events_applied == 0 && result.engine_calls == 0);
    }
    return result;
}
void same_timeline(const HostTimeline& a, const HostTimeline& b) {
    same_engine(a.engine(), b.engine());
    CHECK(a.manual_ownership() == b.manual_ownership());
    CHECK(a.pedal_ownership() == b.pedal_ownership());
    CHECK(a.max_block_frames() == b.max_block_frames());
    CHECK(a.carry_count() == b.carry_count());
    for (const auto& descriptor : parameter_descriptors()) {
        double first = -1, second = -1;
        CHECK(a.normalized_anchor(descriptor.id, first));
        CHECK(b.normalized_anchor(descriptor.id, second));
        CHECK(std::bit_cast<std::uint64_t>(first) == std::bit_cast<std::uint64_t>(second));
    }
    for (std::size_t i = 0; i < a.carry_count(); ++i) {
        HostCarryEvent first{}, second{};
        CHECK(a.carry_event(i, first) && b.carry_event(i, second));
        CHECK(first.index() == second.index());
        if (const auto* parameter = std::get_if<HostParameterCarry>(&first)) {
            CHECK(*parameter == std::get<HostParameterCarry>(second));
        } else if (const auto* manual = std::get_if<HostNoteEvent>(&first)) {
            const auto other = std::get<HostNoteEvent>(second);
            CHECK(manual->offset == other.offset && manual->kind == other.kind &&
                  manual->bus == other.bus && manual->channel == other.channel &&
                  manual->midi_note == other.midi_note && manual->velocity == other.velocity &&
                  manual->note_id == other.note_id);
        } else {
            const auto pedal = std::get<PedalNoteEvent>(first);
            const auto other = std::get<PedalNoteEvent>(second);
            CHECK(pedal.offset == other.offset && pedal.kind == other.kind &&
                  pedal.bus == other.bus && pedal.channel == other.channel &&
                  pedal.pedal == other.pedal && pedal.velocity == other.velocity &&
                  pedal.note_id == other.note_id);
        }
    }
}
void test_timeline(const RuntimeProfile& profile) {
    // Large fixed workspace has lifetime ownership here, allocated before any
    // audio probe. HostTimeline copies the value-owned Engine into its own work.
    auto timeline = std::make_unique<HostTimeline>();
    auto reference = std::make_unique<HostTimeline>();
    const auto console = make_nominal_console_model();
    CHECK(timeline->prepare(profile, {48000, kHardMaxBlockFrames, 119, 900}, console) == Status::Ok);
    ControlSnapshot restored = sounding_controls();
    std::string serialized, error;
    CHECK(serialize_controls(restored, serialized, error));
    std::istringstream stream(serialized);
    CHECK(parse_controls(stream, restored, error));
    const std::array<HostParameterPoint, 2> expression{{{0, 0.25}, {16, 1.0}}};
    const std::array<HostParameterPoint, 2> pedal_bar{{{0, 0.0}, {16, 1.0}}};
    const std::array<HostParameterQueue, 2> parameters{{{0x2000, expression}, {0x4001, pedal_bar}}};
    const std::array<HostMusicalEvent, 4> music{{
        HostNoteEvent{0, HostNoteKind::On, 0, 0, 60, 100, 1},
        HostNoteEvent{0, HostNoteKind::On, 1, 0, 48, 100, 2},
        PedalNoteEvent{0, PedalNoteKind::On, 0, 0, PedalId{13}, 100, 3},
        PedalNoteEvent{16, PedalNoteKind::On, 0, 0, PedalId{25}, 100, 4}}};
    std::vector<float> output(kHardMaxBlockFrames + 2, sentinel);
    auto result = timeline_call(*timeline, 16, {output.data(), 18}, parameters, music, {&restored, 1});
    CHECK(result.input_records_consumed == 8 && result.restores_consumed == 1);
    CHECK(result.carried_records_consumed == 0 && timeline->carry_count() == 3);
    CHECK(output[16] == sentinel && output[17] == sentinel);
    CHECK(timeline->engine().active_key_count() == 2 && timeline->engine().active_pedal_count() == 1);
    CHECK(timeline->manual_ownership().owner_count() == 2 && timeline->pedal_ownership().owner_count() == 1);
    double anchor = -1;
    CHECK(timeline->normalized_anchor(0x2000, anchor));
    CHECK(anchor == 0.25 + 0.75 * 15.0 / 16.0);
    CHECK(timeline->normalized_anchor(0x4001, anchor) && anchor == 15.0 / 16.0);
    // Independent closed-form stimulus: e[n]=1/4+3*n/64 and bar[n]=round(n/2),
    // 0<=n<16. The endpoint at16 is not rendered in this callback. Engine's
    // sample-at-a-time oracle has no HostTimeline or curve implementation.
    Engine oracle;
    CHECK(oracle.prepare(profile, {48000, kHardMaxBlockFrames, 119, 900}, console) == Status::Ok);
    CHECK(oracle.restore_controls(restored));
    std::array<float, 16> expected{};
    for (std::uint32_t n = 0; n < 16; ++n) {
        std::array<Event, 5> events{{
            {0, EventType::Expression, upper, 0, 0.25 + 0.75 * static_cast<double>(n) / 16.0},
            {0, EventType::PedalDrawbar, lower, 1, static_cast<double>((n + 1) / 2)},
            {0, EventType::NoteOn, upper, 60, 100},
            {0, EventType::NoteOn, lower, 48, 100},
            {0, EventType::PedalOn, lower, 13, 100}}};
        CHECK(oracle.process(1, {expected.data() + n, 1}, {events.data(), n == 0 ? 5U : 2U}));
    }
    same_audio({output.data(), 16}, expected);
    same_engine(timeline->engine(), oracle);
    inspect_audio({output.data(), 16});
    // Reject with retained endpoint records before demonstrating that all three
    // are still consumed exactly once on the next successful callback.
    *reference = *timeline;
    const std::array<HostParameterQueue, 2> duplicate{{{0x2000, {}}, {0x2000, {}}}};
    output.assign(output.size(), sentinel);
    timeline_call(*timeline, 16, {output.data(), 16}, duplicate, {}, {}, Status::InvalidEvent);
    same_timeline(*timeline, *reference);
    CHECK(output.front() == sentinel && output[15] == sentinel);
    result = timeline_call(*timeline, 1, {output.data(), 1}, {}, {});
    CHECK(result.carried_records_consumed == 3 && result.input_records_consumed == 0);
    CHECK(timeline->carry_count() == 0 && timeline->engine().active_pedal_count() == 2);
    CHECK(timeline->engine().expression() == 1.0);
    CHECK(timeline->engine().controls_snapshot().pedal_drawbars[1] == 8);
    std::array<float, 1> continuation{};
    CHECK(reference->process(1, continuation, {}, {}));
    same_audio({output.data(), 1}, continuation);
    same_timeline(*timeline, *reference);
    inspect_audio({output.data(), 1});
    // Fill both owner ledgers without exceeding raw budget; 122 manual and25
    // pedal pitches remain physical despite 512 distinct retained identities.
    auto full = std::make_unique<HostTimeline>();
    CHECK(full->prepare(profile, {48000, kHardMaxBlockFrames, 121, 0}, console) == Status::Ok);
    std::array<HostMusicalEvent, 512> owners{};
    for (std::size_t i = 0; i < 256; ++i) {
        owners[2 * i] = HostNoteEvent{0, HostNoteKind::On,
            static_cast<std::uint8_t>((i % 122) / 61), 0,
            static_cast<std::uint8_t>(36 + i % 61), 100, static_cast<std::int32_t>(i)};
        owners[2 * i + 1] = PedalNoteEvent{0, PedalNoteKind::On,
            static_cast<std::uint8_t>(i % 2), 0,
            PedalId{static_cast<std::uint8_t>(1 + i % 25)}, 100, static_cast<std::int32_t>(i)};
    }
    result = timeline_call(*full, 0, {}, {}, owners, {&restored, 1});
    CHECK(result.input_records_consumed == 512 && result.restores_consumed == 1);
    CHECK(result.physical_events_applied == 147);
    CHECK(full->manual_ownership().owner_count() == 256 && full->pedal_ownership().owner_count() == 256);
    CHECK(full->engine().active_key_count() == 122 && full->engine().active_pedal_count() == 25);
    const std::array<HostParameterPoint, 2> long_ramp{{{0, 0.25}, {65536, 1.0}}};
    const std::array<HostParameterQueue, 1> ramp_queue{{{0x2000, long_ramp}}};
    result = timeline_call(*full, kHardMaxBlockFrames, {output.data(), kHardMaxBlockFrames}, ramp_queue, {});
    CHECK(result.input_records_consumed == 2 && full->carry_count() == 1);
    CHECK(result.physical_events_applied >= kHardMaxBlockFrames);
    CHECK(full->engine().percussion_diagnostics().routed_detector);
    CHECK(full->engine().percussion_diagnostics().readiness < 1.0);
    inspect_audio({output.data(), kHardMaxBlockFrames});
    *reference = *full;
    result = timeline_call(*full, 17, {}, {}, {});
    CHECK(result.carried_records_consumed == 1);
    CHECK(reference->process(17, {output.data(), 17}, {}, {}));
    same_timeline(*full, *reference);
    const auto before_zero = full->engine();
    const std::array<HostParameterPoint, 1> zero_point{{{0, 0.5}}};
    const std::array<HostParameterQueue, 1> zero_queue{{{0x4000, zero_point}}};
    result = timeline_call(*full, 0, {}, zero_queue, {});
    CHECK(result.input_records_consumed == 1 && full->carry_count() == 0);
    CHECK(full->engine().controls_snapshot().pedal_drawbars[0] == 4);
    same_phases(full->engine(), before_zero);
    CHECK(full->engine().last_pedal_frame() == before_zero.last_pedal_frame());
    // At capacity, a new identity must reject without consuming pending curves.
    *reference = *full;
    const std::array<HostMusicalEvent, 1> excess_owner{{
        PedalNoteEvent{0, PedalNoteKind::On, 0, 0, PedalId{13}, 100, 9999}}};
    output.assign(output.size(), sentinel);
    timeline_call(*full, 64, {output.data(), 64}, {}, excess_owner, {}, Status::TooManyEvents);
    same_timeline(*full, *reference);
    CHECK(output.front() == sentinel && output[63] == sentinel);
    timeline_call(*full, 64, {output.data(), 63}, {}, {}, {}, Status::InvalidBuffer);
    same_timeline(*full, *reference);
    timeline_call(*full, kHardMaxBlockFrames + 1, {}, {}, {}, {}, Status::BlockTooLarge);
    same_timeline(*full, *reference);
    // 1024 explicit same-sample points are consumed (not silently coalesced
    // away from accounting). Duplicate endpoints at N consume carry capacity.
    std::array<HostParameterPoint, 1024> dense{};
    for (std::size_t i = 0; i < dense.size(); ++i) {
        dense[i] = {0,
                    static_cast<double>(i % 8 + 1) / 8.0};
    }
    const std::array<HostParameterQueue, 1> dense_queue{{{0x2000, dense}}};
    result = timeline_call(*full, 1, {output.data(), 1}, dense_queue, {});
    CHECK(result.input_records_consumed == 1024 && full->engine().expression() == 1.0);
    inspect_audio({output.data(), 1});
    for (auto& point : dense) point.offset = 1;
    result = timeline_call(*full, 1, {output.data(), 1}, dense_queue, {});
    CHECK(result.input_records_consumed == 1024 && full->carry_count() == 1024);
    *reference = *full;
    output[0] = sentinel;
    timeline_call(*full, 1, {output.data(), 1}, zero_queue, {}, {}, Status::TooManyEvents);
    same_timeline(*full, *reference);
    CHECK(output[0] == sentinel);
    result = timeline_call(*full, 0, {}, {}, {});
    CHECK(result.carried_records_consumed == 1024 && full->carry_count() == 0);
    CHECK(reference->process(0, {}, {}, {}));
    same_timeline(*full, *reference);
    const auto before_rate = full->engine();
    auto status = observe(Path::Lifecycle, [&] { return full->reconfigure(96000, 128); });
    record(Path::Lifecycle, status == Status::Ok);
    CHECK(status == Status::Ok && full->max_block_frames() == 128);
    CHECK(full->engine().sample_rate() == 96000);
    same_phases(full->engine(), before_rate);
    *reference = *full;
    status = observe(Path::Lifecycle, [&] { return full->reconfigure(32000, 128); });
    record(Path::Lifecycle, status == Status::Ok);
    CHECK(status == Status::InvalidSpec);
    same_timeline(*full, *reference);
    timeline_call(*full, 129, {}, {}, {}, {}, Status::BlockTooLarge);
    timeline_call(*full, 64, {output.data(), 64}, {}, {});
    CHECK(reference->process(64, {}, {}, {}));
    same_timeline(*full, *reference);
    inspect_audio({output.data(), 64});
}

StateExchangeStatus exchange_call(auto function, StateExchangeStatus expected,
                                  std::uint64_t consumed = 0) {
    const auto status = observe(Path::Exchange, function);
    record(Path::Exchange, status == StateExchangeStatus::Ok, 0,
           status == StateExchangeStatus::Ok ? consumed : 0);
    CHECK(status == expected);
    return status;
}
struct CallbackResult {
    StateExchangeStatus queue_status{StateExchangeStatus::Ok};
    HostTimelineResult timeline{};
    bool committed{false};
};
void test_exchange_callback(const RuntimeProfile& profile) {
    StateExchange exchange;
    StateExchange other;
    StateExchange finite({1, 1});
    StateExchange invalid_limits({1, std::numeric_limits<std::uint64_t>::max()});
    StateExchangeBatch empty{}, pending{}, foreign{}, saved{};
    const auto controls = sounding_controls();
    StatePublishedControls published{}, old_published{};
    CHECK(exchange.read_published(published));
    CHECK(published.acknowledged_sequence == 0 && published.publication_revision == 0);
    exchange_call([&] { return exchange.audio_peek(empty); }, StateExchangeStatus::Ok);
    CHECK(empty.size() == 0 && empty.last_sequence() == 0);
    exchange_call([&] { return exchange.audio_can_commit(empty); }, StateExchangeStatus::Ok);
    exchange_call([&] { return exchange.audio_commit(empty, controls); }, StateExchangeStatus::Ok);
    CHECK(exchange.read_published(published));
    CHECK(published.controls == controls && published.publication_revision == 2);
    exchange_call([&] { return exchange.audio_can_commit(empty); }, StateExchangeStatus::InvalidBatch);
    exchange_call([&] { return exchange.audio_commit(empty, controls); }, StateExchangeStatus::InvalidBatch);
    // UI state parsing and all enqueue work are explicitly OUTSIDE the probe.
    // The four accepted immutable values are deliberately distinct. No UI-side
    // no-allocation inference is drawn from the measured consumer callbacks.
    std::array<ControlSnapshot, 4> loaded{};
    for (std::size_t i = 0; i < loaded.size(); ++i) {
        loaded[i] = controls;
        loaded[i].expression = static_cast<double>(i + 1) / 8.0;
        loaded[i].pedal_drawbars = {static_cast<std::uint8_t>(5 + i),
                                   static_cast<std::uint8_t>(1 + i)};
        std::string text, error;
        CHECK(serialize_controls(loaded[i], text, error));
        std::istringstream input(text);
        ControlSnapshot parsed{};
        CHECK(parse_controls(input, parsed, error));
        CHECK(parsed == loaded[i]);
        const auto enqueued = exchange.ui_enqueue(parsed);
        CHECK(enqueued && enqueued.sequence == i + 1);
    }
    CHECK(exchange.ui_enqueue(controls).status == StateExchangeStatus::QueueFull);
    ControlSnapshot saved_controls{};
    CHECK(exchange.ui_snapshot_for_save(saved_controls) && saved_controls == loaded.back());
    exchange_call([&] { return exchange.audio_peek(pending); }, StateExchangeStatus::Ok);
    CHECK(pending.size() == 4 && pending.last_sequence() == 4);
    for (std::size_t i = 0; i < 4; ++i) CHECK(pending.snapshots()[i] == loaded[i]);
    exchange_call([&] { return exchange.audio_can_commit(pending); }, StateExchangeStatus::Ok);
    old_published = published;
    auto bad_controls = controls; bad_controls.pedal_drawbars[1] = 9;
    exchange_call([&] { return exchange.audio_commit(pending, bad_controls); },
                  StateExchangeStatus::InvalidSnapshot);
    CHECK(exchange.read_published(published));
    CHECK(published.controls == old_published.controls &&
          published.publication_revision == old_published.publication_revision &&
          published.acknowledged_sequence == old_published.acknowledged_sequence);
    CHECK(exchange.ui_snapshot_for_save(saved_controls) && saved_controls == loaded.back());
    exchange_call([&] { return other.audio_peek(foreign); }, StateExchangeStatus::Ok);
    exchange_call([&] { return exchange.audio_can_commit(foreign); }, StateExchangeStatus::InvalidBatch);
    exchange_call([&] { return exchange.audio_commit(foreign, controls); }, StateExchangeStatus::InvalidBatch);
    // Complete proposed callback: fixed token + candidate timeline + commit and
    // atomic publication + final host copy are all INSIDE one recorded scope.
    // This exercises core integration, not a native VST3 SDK callback.
    auto timeline = std::make_unique<HostTimeline>();
    auto before = std::make_unique<HostTimeline>();
    CHECK(timeline->prepare(profile, {48000, 1024, 311, 8000},
                            make_nominal_console_model()) == Status::Ok);
    std::array<float, 1024> private_output{}, host_output{};
    const std::array<HostParameterPoint, 2> points{{{0, 0.25}, {1024, 0.75}}};
    const std::array<HostParameterQueue, 1> parameters{{{0x2000, points}}};
    const std::array<HostParameterQueue, 2> bad_parameters{{{0x2000, {}}, {0x2000, {}}}};
    std::array<HostMusicalEvent, 512> music{};
    for (std::size_t i = 0; i < 256; ++i) {
        music[2 * i] = HostNoteEvent{0, HostNoteKind::On,
            static_cast<std::uint8_t>((i % 122) / 61), 0,
            static_cast<std::uint8_t>(36 + i % 61), 100, static_cast<std::int32_t>(i)};
        music[2 * i + 1] = PedalNoteEvent{0, PedalNoteKind::On,
            static_cast<std::uint8_t>(i % 2), 0,
            PedalId{static_cast<std::uint8_t>(1 + i % 25)}, 100, static_cast<std::int32_t>(i)};
    }
    auto callback = [&](std::uint32_t frames, std::span<const HostParameterQueue> queues,
                        std::span<const HostMusicalEvent> events, bool connected = true) {
        const auto result = observe(Path::Callback, [&] {
            CallbackResult completed;
            StateExchangeBatch batch;
            completed.queue_status = exchange.audio_peek(batch);
            if (completed.queue_status != StateExchangeStatus::Ok) return completed;
            completed.queue_status = exchange.audio_can_commit(batch);
            if (completed.queue_status != StateExchangeStatus::Ok) return completed;
            completed.timeline = timeline->process(frames,
                connected ? std::span<float>{private_output.data(), frames} : std::span<float>{},
                queues, events, batch.snapshots());
            if (!completed.timeline) return completed;
            completed.queue_status = exchange.audio_commit(batch, timeline->engine().controls_snapshot());
            if (completed.queue_status != StateExchangeStatus::Ok) return completed;
            if (connected) std::copy_n(private_output.data(), frames, host_output.data());
            completed.committed = true;
            return completed;
        });
        record(Path::Callback, result.committed, frames,
               result.timeline.input_records_consumed + result.timeline.carried_records_consumed,
               result.timeline.physical_events_applied);
        return result;
    };
    *before = *timeline;
    host_output.fill(sentinel);
    auto result = callback(1024, bad_parameters, music);
    CHECK(!result.committed && result.timeline.status == Status::InvalidEvent);
    CHECK(result.queue_status == StateExchangeStatus::Ok);
    CHECK(std::all_of(host_output.begin(), host_output.end(), [](float sample) { return sample == sentinel; }));
    same_timeline(*timeline, *before);
    CHECK(exchange.ui_snapshot_for_save(saved_controls) && saved_controls == loaded.back());
    exchange_call([&] { return exchange.audio_peek(saved); }, StateExchangeStatus::Ok);
    CHECK(saved.size() == 4 && saved.last_sequence() == 4);
    result = callback(1024, parameters, music);
    CHECK(result.committed && result.timeline.restores_consumed == 4);
    CHECK(result.timeline.input_records_consumed == 514);
    CHECK(timeline->engine().frame_clock() == 9024);
    CHECK(timeline->manual_ownership().owner_count() == 256 && timeline->pedal_ownership().owner_count() == 256);
    CHECK(timeline->engine().active_key_count() == 122 && timeline->engine().active_pedal_count() == 25);
    CHECK(timeline->engine().controls_snapshot().pedal_drawbars == loaded.back().pedal_drawbars);
    CHECK(timeline->engine().expression() == 0.25 + 0.5 * 1023.0 / 1024.0);
    CHECK(timeline->engine().percussion_diagnostics().routed_detector);
    inspect_audio(host_output);
    CHECK(exchange.read_published(published));
    CHECK(published.controls == timeline->engine().controls_snapshot());
    CHECK(published.acknowledged_sequence == 4 && published.publication_revision == 4);
    CHECK(exchange.ui_snapshot_for_save(saved_controls) && saved_controls == published.controls);
    exchange_call([&] { return exchange.audio_can_commit(pending); }, StateExchangeStatus::InvalidBatch);
    exchange_call([&] { return exchange.audio_commit(pending, controls); }, StateExchangeStatus::InvalidBatch);
    // Carry is consumed even by a zero-frame callback, and publication advances
    // while engine time and prior rendered diagnostics remain unchanged.
    const auto before_zero = timeline->engine();
    result = callback(0, {}, {});
    CHECK(result.committed && result.timeline.carried_records_consumed == 1);
    CHECK(timeline->carry_count() == 0 && timeline->engine().expression() == 0.75);
    CHECK(timeline->engine().frame_clock() == before_zero.frame_clock());
    CHECK(timeline->engine().last_pedal_frame() == before_zero.last_pedal_frame());
    same_phases(timeline->engine(), before_zero);
    // No UI read between these callbacks. A slow observer cannot make the
    // bounded publisher wait; the final value and revision remain coherent.
    for (std::size_t i = 0; i < 32; ++i) {
        result = callback(64, {}, {}, i % 2 == 0);
        CHECK(result.committed && result.timeline.restores_consumed == 0);
        if (i % 2 == 0) inspect_audio({host_output.data(), 64});
    }
    CHECK(exchange.read_published(published));
    CHECK(published.acknowledged_sequence == 4 && published.publication_revision == 70);
    CHECK(published.controls == timeline->engine().controls_snapshot());
    CHECK(timeline->engine().frame_clock() == 11072);
    CHECK(exchange.ui_snapshot_for_save(saved_controls) && saved_controls == published.controls);
    // An append after successful preflight remains queued after this token's
    // commit; it cannot invalidate the reservation or be acknowledged early.
    CHECK(other.ui_enqueue(loaded[0]).sequence == 1);
    exchange_call([&] { return other.audio_peek(foreign); }, StateExchangeStatus::Ok);
    exchange_call([&] { return other.audio_can_commit(foreign); }, StateExchangeStatus::Ok);
    CHECK(other.ui_enqueue(loaded[1]).sequence == 2);
    exchange_call([&] { return other.audio_commit(foreign, loaded[0]); }, StateExchangeStatus::Ok, 1);
    CHECK(other.read_published(published) && published.acknowledged_sequence == 1);
    CHECK(other.ui_snapshot_for_save(saved_controls) && saved_controls == loaded[1]);
    exchange_call([&] { return other.audio_peek(foreign); }, StateExchangeStatus::Ok);
    CHECK(foreign.size() == 1 && foreign.last_sequence() == 2 && foreign.snapshots()[0] == loaded[1]);
    exchange_call([&] { return other.audio_can_commit(foreign); }, StateExchangeStatus::Ok);
    exchange_call([&] { return other.audio_commit(foreign, loaded[1]); }, StateExchangeStatus::Ok, 1);
    CHECK(other.read_published(published) && published.acknowledged_sequence == 2);
    // Legitimate short lifetimes reach overflow protections without modifying
    // private counters or waiting for UINT64_MAX callbacks.
    CHECK(finite.ui_enqueue(controls).sequence == 1);
    exchange_call([&] { return finite.audio_peek(foreign); }, StateExchangeStatus::Ok);
    exchange_call([&] { return finite.audio_can_commit(foreign); }, StateExchangeStatus::Ok);
    exchange_call([&] { return finite.audio_commit(foreign, controls); }, StateExchangeStatus::Ok, 1);
    CHECK(finite.ui_enqueue(loaded[0]).status == StateExchangeStatus::SequenceExhausted);
    exchange_call([&] { return finite.audio_peek(foreign); }, StateExchangeStatus::Ok);
    CHECK(foreign.size() == 0 && foreign.last_sequence() == 1);
    CHECK(finite.read_published(old_published));
    exchange_call([&] { return finite.audio_can_commit(foreign); }, StateExchangeStatus::SequenceExhausted);
    exchange_call([&] { return finite.audio_commit(foreign, controls); }, StateExchangeStatus::SequenceExhausted);
    CHECK(finite.read_published(published));
    CHECK(published.controls == old_published.controls &&
          published.publication_revision == old_published.publication_revision &&
          published.acknowledged_sequence == old_published.acknowledged_sequence);
    saved = foreign;
    exchange_call([&] { return invalid_limits.audio_peek(foreign); }, StateExchangeStatus::InvalidLimits);
    CHECK(foreign.size() == saved.size() && foreign.last_sequence() == saved.last_sequence());
    exchange_call([&] { return invalid_limits.audio_can_commit(foreign); }, StateExchangeStatus::InvalidLimits);
    exchange_call([&] { return invalid_limits.audio_commit(foreign, controls); }, StateExchangeStatus::InvalidLimits);
    CHECK(!invalid_limits.read_published(published));
    CHECK(published.controls == old_published.controls &&
          published.publication_revision == old_published.publication_revision);
}

void report() {
    constexpr std::array<const char*, static_cast<std::size_t>(Path::Count)> names{
        "engine", "manual-owners", "pedal-owners", "combined", "timeline", "exchange",
        "complete-callback", "stopped-lifecycle"};
#if defined(_MSC_VER)
    std::printf("compiler=MSVC-%d ", _MSC_VER);
#elif defined(__clang__)
    std::printf("compiler=Clang-%s ", __clang_version__);
#elif defined(__GNUC__)
    std::printf("compiler=GCC-%s ", __VERSION__);
#endif
    std::printf("pointer_bits=%zu clock=steady_clock timing=observed-only\n", sizeof(void*) * 8);
    std::printf("calibration=12-allocations/12-frees (8-new-overloads,12-delete-overloads)\n");
    for (std::size_t i = 0; i < totals.size(); ++i) {
        const auto& t = totals[i];
        CHECK(t.calls == t.accepted + t.rejected && t.calls > 0);
        CHECK(std::isfinite(t.elapsed_us) && t.elapsed_us >= 0.0);
        CHECK(t.allocations == 0 && t.deallocations == 0);
        std::printf("%s calls=%zu accepted=%zu rejected=%zu frames=%llu records=%llu physical=%llu "
                    "new=%zu delete=%zu elapsed_us=%.3f max_us=%.3f\n", names[i],
                    t.calls, t.accepted, t.rejected, static_cast<unsigned long long>(t.frames),
                    static_cast<unsigned long long>(t.records), static_cast<unsigned long long>(t.physical),
                    t.allocations, t.deallocations, t.elapsed_us, t.maximum_us);
    }
    std::printf("storage_bytes Engine=%zu NoteOwnership=%zu PedalNoteOwnership=%zu "
                "HostTimeline=%zu StateExchange=%zu StateExchangeBatch=%zu ControlSnapshot=%zu\n",
                sizeof(Engine), sizeof(NoteOwnership), sizeof(PedalNoteOwnership), sizeof(HostTimeline),
                sizeof(StateExchange), sizeof(StateExchangeBatch), sizeof(ControlSnapshot));
    std::printf("audio_samples=%llu audio_hash=%016llx exact_audio_comparisons=%llu "
                "phase_comparisons=%llu\n", static_cast<unsigned long long>(audio_samples),
                static_cast<unsigned long long>(audio_hash), static_cast<unsigned long long>(audio_comparisons),
                static_cast<unsigned long long>(phase_comparisons));
    std::printf("scope=calling-thread-global-C++-new/delete; no C-heap/locks/syscalls/SDK/device guarantee\n");
}
} // namespace

int main() {
    test_probe_overloads();
    const auto profile = load_test_profile();
    test_engine(profile);
    test_owners();
    test_combined(profile);
    test_timeline(profile);
    test_exchange_callback(profile);
    report();
    return EXIT_SUCCESS;
}
