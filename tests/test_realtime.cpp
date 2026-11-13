#include "TestSupport.h"
#include "hammond/Engine.h"

#include <algorithm>
#include <array>
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
constexpr std::uint32_t dense_frames = static_cast<std::uint32_t>(kMaxEventsPerBlock);

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

struct Summary {
    std::size_t accepted{};
    std::size_t rejected{};
    std::uint64_t frames{};
    std::uint64_t events{};
};

void observe(const char* label, Engine& engine, std::uint32_t frames,
             std::span<float> output, std::span<const Event> events,
             Status expected, Summary& summary) {
    CHECK(engine.prepared());
    CHECK(!allocation_probe::recording);
    // Arguments, profile, buffers, events and expected state already exist.
    // There is no assertion, formatting, logging or fixture work in this region.
    allocation_probe::begin();
    const ProcessResult result = engine.process(frames, output, events);
    const auto counts = allocation_probe::end();

    if (counts.allocations != 0 || counts.deallocations != 0) {
        std::fprintf(stderr, "%s: %zu C++ allocations, %zu C++ deallocations\n",
                     label, counts.allocations, counts.deallocations);
        hammond_test::fail("zero C++ heap calls during prepared process", __FILE__, __LINE__);
    }
    if (result.status != expected) {
        std::fprintf(stderr, "%s: expected %s, got %s\n", label,
                     status_name(expected), status_name(result.status));
        hammond_test::fail("expected process status", __FILE__, __LINE__);
    }
    CHECK(result.events_consumed == (expected == Status::Ok ? events.size() : 0));
    if (expected == Status::Ok) {
        ++summary.accepted;
        summary.frames += frames;
        summary.events += events.size();
    } else {
        ++summary.rejected;
    }
}

struct State {
    std::uint64_t clock{};
    ControlSnapshot controls{};
    std::array<std::array<bool, kManualKeyCount>, kManualCount> keys{};
    std::array<double, kToneSourceCount> phases{};
    bool operator==(const State&) const noexcept = default;
};

[[nodiscard]] State state_of(const Engine& engine) {
    State result;
    result.clock = engine.frame_clock();
    result.controls = engine.controls_snapshot();
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        for (std::size_t key = 0; key < kManualKeyCount; ++key) {
            result.keys[manual][key] = engine.key_down(static_cast<Manual>(manual),
                static_cast<std::uint32_t>(key) + kMinManualMidiNote);
        }
    }
    for (std::size_t tone = 0; tone < kToneSourceCount; ++tone) {
        CHECK(engine.source_phase_turns(static_cast<ToneId>(tone + 1), result.phases[tone]));
    }
    return result;
}

struct Fixtures {
    static constexpr std::size_t setup_count =
        kManualCount * (kDrawbarBankCount * kDrawbarCount + kManualKeyCount + 1) + 1;
    std::array<Event, setup_count> all_keys{};
    std::array<Event, kMaxEventsPerBlock> dense_drawbars{};
    std::array<Event, kMaxEventsPerBlock> mixed{};
    std::array<Event, kMaxEventsPerBlock> flush{};
    std::array<Event, kMaxEventsPerBlock> invalid_tail{};
    std::array<Event, kMaxEventsPerBlock + 1> too_many{};
};

[[nodiscard]] Fixtures make_fixtures() {
    Fixtures result;
    std::size_t cursor = 0;
    for (std::size_t manual_index = 0; manual_index < kManualCount; ++manual_index) {
        const auto manual = static_cast<Manual>(manual_index);
        for (std::size_t bar = 0; bar < kDrawbarBankCount * kDrawbarCount; ++bar) {
            result.all_keys[cursor++] = {0, EventType::BankDrawbar, manual,
                                         static_cast<std::uint8_t>(bar), 8.0};
        }
        result.all_keys[cursor++] = {0, EventType::SelectBank, manual, 0, 1.0};
        for (std::size_t key = 0; key < kManualKeyCount; ++key) {
            result.all_keys[cursor++] = {0, EventType::NoteOn, manual,
                static_cast<std::uint8_t>(key + kMinManualMidiNote), 127.0};
        }
    }
    result.all_keys[cursor++] = {0, EventType::Expression, Manual::Upper, 0, 1.0};
    CHECK(cursor == result.all_keys.size());

    for (std::size_t index = 0; index < kMaxEventsPerBlock; ++index) {
        const auto offset = static_cast<std::uint32_t>(index);
        const auto manual = static_cast<Manual>((index / 8) % kManualCount);
        const auto note = static_cast<std::uint8_t>((index / 8) % kManualKeyCount +
                                                   kMinManualMidiNote);
        // Every event changes a selected drawbar while all 122 keys stay down.
        result.dense_drawbars[index] = {offset, EventType::Drawbar,
            static_cast<Manual>((index / 2) % kManualCount), 0, index % 2 == 0 ? 7.0 : 8.0};
        Event event{offset, EventType::NoteOn, manual, note, 127.0};
        switch (index % 8) {
        case 0: break;
        case 1: event = {offset, EventType::NoteOff, manual, note, 0.0}; break;
        case 2: event = {offset, EventType::Drawbar, manual,
                         static_cast<std::uint8_t>((index / 8) % kDrawbarCount), 5.0}; break;
        case 3: event = {offset, EventType::Expression, manual, 0, 0.375}; break;
        case 4: event = {offset, EventType::AllNotesOff, manual, 0, 0.0}; break;
        case 5: event = {offset, EventType::BankDrawbar, manual,
                         static_cast<std::uint8_t>((index / 8) %
                             (kDrawbarBankCount * kDrawbarCount)), 3.0}; break;
        case 6: event = {offset, EventType::SelectBank, manual, 0,
                         static_cast<double>((index / 8) % 2)}; break;
        case 7: event = {offset, EventType::Cancel, manual, 0, 0.0}; break;
        }
        result.mixed[index] = event;
        event.offset = 0;
        result.flush[index] = event;
    }
    result.invalid_tail = result.dense_drawbars;
    result.invalid_tail.back().value = std::numeric_limits<double>::quiet_NaN();
    result.too_many.fill(Event{0, EventType::Expression, Manual::Upper, 0, 0.5});
    return result;
}

void check_written_output(std::span<const float> output, std::size_t frames) {
    for (std::size_t index = 0; index < output.size(); ++index) {
        if (index < frames) CHECK(std::isfinite(output[index]) && output[index] != sentinel);
        else CHECK(output[index] == sentinel);
    }
}

void check_all_keys(const Engine& engine) {
    CHECK(engine.active_key_count() == kManualCount * kManualKeyCount);
    for (const Manual manual : {Manual::Upper, Manual::Lower}) {
        CHECK(engine.active_key_count(manual) == kManualKeyCount);
        bool enabled = false;
        CHECK(engine.route_enabled(manual, enabled) && enabled);
    }
}

void check_released_and_cancelled(const Engine& engine) {
    CHECK(engine.active_key_count() == 0);
    for (const Manual manual : {Manual::Upper, Manual::Lower}) {
        bool enabled = true;
        CHECK(engine.route_enabled(manual, enabled) && !enabled);
    }
    CHECK(engine.expression() == 0.375);
}

void test_successes(const RuntimeProfile& profile, const Fixtures& fixtures,
                    double sample_rate, Summary& summary) {
    Engine engine;
    CHECK(engine.prepare(profile, {sample_rate, kHardMaxBlockFrames, 17, 1234}) == Status::Ok);
    std::array<float, kMaxEventsPerBlock + 3> output{};
    std::vector<float> maximum_output(static_cast<std::size_t>(kHardMaxBlockFrames) + 3,
                                      sentinel);

    // No Engine process call warms this instance before its first observation.
    output.fill(sentinel);
    observe("first positive callback, all keys", engine, 1, output, fixtures.all_keys,
            Status::Ok, summary);
    check_written_output(output, 1);
    check_all_keys(engine);
    for (const std::uint32_t frames : {17U, 64U, 257U, dense_frames}) {
        output.fill(sentinel);
        observe("sustained connected", engine, frames, output, {}, Status::Ok, summary);
        check_written_output(output, frames);
    }
    CHECK(std::any_of(output.begin(), output.begin() + dense_frames,
                      [](float sample) { return sample != 0.0F; }));
    observe("hard maximum block", engine, kHardMaxBlockFrames, maximum_output, {},
            Status::Ok, summary);
    check_written_output(maximum_output, kHardMaxBlockFrames);

    auto before = state_of(engine);
    observe("sustained disconnected", engine, dense_frames, {}, {}, Status::Ok, summary);
    auto after = state_of(engine);
    CHECK(after.clock == before.clock + dense_frames && after.phases != before.phases);
    check_all_keys(engine);

    output.fill(sentinel);
    before = state_of(engine);
    observe("empty zero-frame call", engine, 0, output, {}, Status::Ok, summary);
    CHECK(state_of(engine) == before);
    check_written_output(output, 0);
    observe("1024 per-frame routing rebuilds", engine, dense_frames, output,
            fixtures.dense_drawbars, Status::Ok, summary);
    check_written_output(output, dense_frames);
    check_all_keys(engine);

    output.fill(sentinel);
    observe("1024 mixed events", engine, dense_frames, output, fixtures.mixed,
            Status::Ok, summary);
    check_written_output(output, dense_frames);
    check_released_and_cancelled(engine);

    before = state_of(engine);
    output.fill(sentinel);
    observe("zero-frame all-key setup", engine, 0, output, fixtures.all_keys,
            Status::Ok, summary);
    check_all_keys(engine);
    observe("1024-event zero-frame flush", engine, 0, output, fixtures.flush,
            Status::Ok, summary);
    after = state_of(engine);
    CHECK(after.clock == before.clock && after.phases == before.phases);
    check_written_output(output, 0);
    check_released_and_cancelled(engine);
    observe("disconnected zero-frame flush", engine, 0, {}, fixtures.all_keys,
            Status::Ok, summary);
    check_all_keys(engine);
    observe("1024 same-offset positive events", engine, 1, output, fixtures.flush,
            Status::Ok, summary);
    check_released_and_cancelled(engine);

    output.fill(sentinel);
    observe("positive silence after release", engine, 64, output, {}, Status::Ok, summary);
    check_written_output(output, 64);
    CHECK(std::all_of(output.begin(), output.begin() + 64,
                      [](float sample) { return sample == 0.0F; }));

    observe("restore held keys through zero frames", engine, 0, {}, fixtures.all_keys,
            Status::Ok, summary);
    auto disconnected = engine;
    output.fill(sentinel);
    observe("connected dense reference", engine, dense_frames, output, fixtures.mixed,
            Status::Ok, summary);
    observe("disconnected dense controls", disconnected, dense_frames, {}, fixtures.mixed,
            Status::Ok, summary);
    CHECK(state_of(engine) == state_of(disconnected));
    check_written_output(output, dense_frames);
}

void reject(const char* label, Engine& engine, std::uint32_t frames,
            std::span<float> output, std::span<const Event> events,
            Status status, Summary& summary) {
    const auto before = state_of(engine);
    std::fill(output.begin(), output.end(), sentinel);
    observe(label, engine, frames, output, events, status, summary);
    CHECK(state_of(engine) == before);
    check_written_output(output, 0);
}

void test_rejections(const RuntimeProfile& profile, const Fixtures& fixtures,
                     double sample_rate, Summary& summary) {
    Engine engine;
    CHECK(engine.prepare(profile, {sample_rate, kHardMaxBlockFrames, 31, 77}) == Status::Ok);
    std::array<float, kMaxEventsPerBlock + 3> output{};
    const std::array unsorted{
        Event{1, EventType::Expression, Manual::Upper, 0, 0.125},
        Event{0, EventType::Cancel, Manual::Lower, 0, 0.0}};
    const std::array end_boundary{Event{64, EventType::Expression, Manual::Upper, 0, 0.5}};
    const std::array invalid_type{Event{0, static_cast<EventType>(255), Manual::Upper, 0, 0.0}};
    const std::array invalid_manual{Event{0, EventType::Cancel, static_cast<Manual>(255), 0, 0.0}};
    observe("prepare active rejection fixture", engine, 0, {}, fixtures.all_keys,
            Status::Ok, summary);
    reject("oversized block", engine, kHardMaxBlockFrames + 1, {}, {},
           Status::BlockTooLarge, summary);
    reject("undersized output", engine, dense_frames,
           std::span<float>(output).first(dense_frames - 1), {}, Status::InvalidBuffer, summary);
    reject("1025 positive events", engine, dense_frames, output, fixtures.too_many,
           Status::TooManyEvents, summary);
    reject("1025 zero-frame events", engine, 0, output, fixtures.too_many,
           Status::TooManyEvents, summary);
    reject("invalid 1024th payload", engine, dense_frames, output, fixtures.invalid_tail,
           Status::InvalidEvent, summary);
    reject("unsorted offsets", engine, 64, output, unsorted, Status::InvalidEvent, summary);
    reject("end-boundary offset", engine, 64, output, end_boundary,
           Status::InvalidEvent, summary);
    reject("nonzero zero-frame offset", engine, 0, output, end_boundary,
           Status::InvalidEvent, summary);
    reject("unknown event type", engine, 64, output, invalid_type,
           Status::InvalidEvent, summary);
    reject("unknown manual", engine, 64, output, invalid_manual,
           Status::InvalidEvent, summary);

    Engine near_overflow;
    CHECK(near_overflow.prepare(profile, {sample_rate, 64, 0,
        std::numeric_limits<std::uint64_t>::max() - 1}) == Status::Ok);
    observe("last representable positive frame", near_overflow, 1, output, {},
            Status::Ok, summary);
    reject("timeline overflow", near_overflow, 1, output, {}, Status::TimelineOverflow, summary);
    const auto before = state_of(near_overflow);
    observe("flush at maximum clock", near_overflow, 0, {}, fixtures.flush,
            Status::Ok, summary);
    CHECK(near_overflow.frame_clock() == std::numeric_limits<std::uint64_t>::max());
    CHECK(state_of(near_overflow).phases == before.phases);
}

} // namespace

int main() {
    test_probe_overloads();
    const auto profile = load_test_profile();
    const auto fixtures = make_fixtures();
    Summary summary;
    for (const double sample_rate : {44100.0, 48000.0, 96000.0}) {
        test_successes(profile, fixtures, sample_rate, summary);
        test_rejections(profile, fixtures, sample_rate, summary);
    }
    CHECK(!allocation_probe::recording);
    std::printf("Prepared process observations: %zu accepted, %zu rejected; "
                "%llu frames, %llu consumed events; zero observed C++ allocations/deallocations.\n",
                summary.accepted, summary.rejected,
                static_cast<unsigned long long>(summary.frames),
                static_cast<unsigned long long>(summary.events));
    return 0;
}
