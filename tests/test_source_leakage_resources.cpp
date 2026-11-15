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
#include <bit>
#include <optional>
#include <type_traits>

// Keep the interposition boundary visible under optimization. GCC otherwise
// diagnoses an inlined malloc-backed new paired with sized delete as mismatched.
#if defined(_MSC_VER)
#define HAMMOND_PROBE_NOINLINE __declspec(noinline)
#elif defined(__GNUC__) || defined(__clang__)
#define HAMMOND_PROBE_NOINLINE __attribute__((noinline))
#else
#define HAMMOND_PROBE_NOINLINE
#endif

// This calibrated interposition follows tests/test_realtime.cpp.
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

enum class Interval : std::size_t {
    CorePrepare, CoreProcess, CoreCopyDestroy, CoreQuery, CoreReject,
    EngineInstall, EngineClear, EngineCopy, EngineProcess, EngineFlush,
    EngineReject, EngineQuery, Count
};

struct Totals { std::size_t calls{}, allocations{}, deallocations{}; };
struct Summary {
    std::array<Totals, static_cast<std::size_t>(Interval::Count)> intervals{};
    std::uint64_t core_frames{}, engine_frames{}, engine_events{};
    std::size_t fixtures{};
};

// Fixture setup, assertions, formatting and I/O all occur outside observation.
// Each first call is observed: there is no warm-up hiding lazy allocation.
template<class Operation>
auto measured(Summary& summary, Interval interval, Operation operation) {
    CHECK(!allocation_probe::recording);
    allocation_probe::begin();
    const auto result = operation();
    const auto observed = allocation_probe::end();
    auto& total = summary.intervals[static_cast<std::size_t>(interval)];
    ++total.calls;
    total.allocations += observed.allocations;
    total.deallocations += observed.deallocations;
    CHECK(observed.allocations == 0);
    CHECK(observed.deallocations == 0);
    return result;
}

constexpr std::uint32_t kBlock = 257;
constexpr std::size_t kSetupEvents = kManualCount *
    (kDrawbarBankCount * kDrawbarCount + 1 + kManualKeyCount) +
    kPedalCount + kPedalDrawbarCount + 5;

// Static test storage keeps the observer portable to small Windows stacks.
// The receipt reports its actual sizeof, not a call-stack high-water estimate.
struct Fixtures {
    std::array<SourceLeakageEdge, kMaxSourceLeakageEdges + 1> edges{};
    SourceLeakage graph{}, assigned{};
    std::optional<SourceLeakage> constructed{};
    SourceLeakageProfile profile{};
    SourceLeakageFrame input{}, output{}, expected{}, alias{};
    Engine engine{}, control{};
    std::array<float, kBlock + 1> audio{}, reference{};
    std::array<Event, kSetupEvents> setup{};
    std::array<Event, kMaxEventsPerBlock> dense{}, invalid{};
} fixtures;

void fill_graph(std::span<SourceLeakageEdge> edges) {
    CHECK(edges.size() >= kMaxSourceLeakageEdges);
    std::size_t index = 0;
    for (std::size_t destination = 0; destination < kToneSourceCount; ++destination) {
        for (std::size_t step = 1; step <= 8; ++step) {
            edges[index++] = {static_cast<ToneId>((destination + step) % 91 + 1),
                static_cast<ToneId>(destination + 1), step % 2 == 0 ? -0.0625 : 0.0625};
        }
    }
    CHECK(index == kMaxSourceLeakageEdges);
}

void same_bits(const SourceLeakageFrame& actual, const SourceLeakageFrame& expected) {
    for (std::size_t index = 0; index < actual.size(); ++index)
        CHECK(std::bit_cast<std::uint64_t>(actual[index]) ==
              std::bit_cast<std::uint64_t>(expected[index]));
}

void core_resources(Summary& summary) {
    auto& f = fixtures;
    fill_graph(f.edges);
    const auto full = std::span<const SourceLeakageEdge>(f.edges).first(kMaxSourceLeakageEdges);
    f.output.fill(17.0);
    f.expected = f.output;
    CHECK(measured(summary, Interval::CoreReject, [&] {
        return f.graph.process_frame(f.input, f.output);
    }) == Status::NotPrepared);
    same_bits(f.output, f.expected);

    // Author storage truly leaves scope; corruption precedes that lifetime end.
    {
        std::array<SourceLeakageEdge, kMaxSourceLeakageEdges> author;
        fill_graph(author);
        CHECK(measured(summary, Interval::CorePrepare, [&] {
            return f.graph.prepare(author);
        }) == Status::Ok);
        for (auto& edge : author) edge = {0, 0, std::numeric_limits<double>::quiet_NaN()};
    }
    CHECK(f.graph.edge_count() == 728);
    CHECK(f.graph.max_row_absolute_gain_sum() == 0.5);
    CHECK(measured(summary, Interval::CoreCopyDestroy, [&] {
        f.constructed.emplace(f.graph);
        f.assigned = f.graph;
        return f.constructed->prepared() && f.assigned.prepared();
    }));

    for (std::size_t frame = 0; frame < 1024; ++frame) {
        for (std::size_t index = 0; index < f.input.size(); ++index)
            f.input[index] = static_cast<double>(static_cast<int>((index * 29 + frame) % 257) - 128) / 128.0;
        // Exact dyadic algebra is independent of stored rows/canonical order.
        for (std::size_t destination = 0; destination < 91; ++destination) {
            double value = f.input[destination];
            for (std::size_t step = 1; step <= 8; ++step)
                value += f.input[(destination + step) % 91] * (step % 2 == 0 ? -0.0625 : 0.0625);
            f.expected[destination] = value;
        }
        CHECK(measured(summary, Interval::CoreProcess, [&] {
            return f.graph.process_frame(f.input, f.output);
        }) == Status::Ok);
        same_bits(f.output, f.expected);
        f.alias = f.input;
        CHECK(measured(summary, Interval::CoreProcess, [&] {
            return f.constructed->process_frame(f.alias, f.alias);
        }) == Status::Ok);
        same_bits(f.alias, f.expected);
        summary.core_frames += 2;
    }
    for (ToneId id = 1; id <= 91; ++id) {
        double row = -1.0;
        CHECK(measured(summary, Interval::CoreQuery, [&] {
            return f.graph.row_absolute_gain_sum(id, row);
        }));
        CHECK(row == 0.5);
    }
    double row = 13.0;
    CHECK(!measured(summary, Interval::CoreQuery, [&] {
        return f.graph.row_absolute_gain_sum(0, row);
    }));
    CHECK(row == 13.0);

    // A real backing array covers the oversized span. The other rejection
    // traverses the full maximum graph before failing its final row sum.
    CHECK(measured(summary, Interval::CoreReject, [&] {
        return f.graph.prepare(f.edges);
    }) == Status::InvalidProfile);
    f.edges[kMaxSourceLeakageEdges - 1].gain = 0.125;
    CHECK(measured(summary, Interval::CoreReject, [&] {
        return f.graph.prepare(full);
    }) == Status::InvalidProfile);
    CHECK(measured(summary, Interval::CoreProcess, [&] {
        return f.graph.process_frame(f.input, f.output);
    }) == Status::Ok);
    same_bits(f.output, f.expected);
    ++summary.core_frames;
    const auto sentinel = f.output;
    f.input.back() = std::numeric_limits<double>::quiet_NaN();
    CHECK(measured(summary, Interval::CoreReject, [&] {
        return f.graph.process_frame(f.input, f.output);
    }) == Status::InvalidBuffer);
    same_bits(f.output, sentinel);
    f.input.back() = -0.0;

    fill_graph(f.edges);
    for (std::size_t repetition = 0; repetition < 16; ++repetition) {
        CHECK(measured(summary, Interval::CorePrepare, [&] {
            return f.assigned.prepare(full);
        }) == Status::Ok);
        CHECK(measured(summary, Interval::CorePrepare, [&] {
            return f.assigned.prepare({});
        }) == Status::Ok);
    }
    CHECK(measured(summary, Interval::CoreProcess, [&] {
        return f.assigned.process_frame(f.input, f.output);
    }) == Status::Ok);
    same_bits(f.input, f.output);
    ++summary.core_frames;
    CHECK(measured(summary, Interval::CoreCopyDestroy, [&] {
        f.constructed.reset();
        return !f.constructed.has_value();
    }));

    constexpr std::string_view profile_id = "synthetic-resource-v1";
    std::copy(profile_id.begin(), profile_id.end(), f.profile.profile_id.begin());
    std::fill_n(f.profile.authoring_sha256.begin(), 64, 'a');
    std::copy(full.begin(), full.end(), f.profile.edges.begin());
    f.profile.edge_count = full.size();
    std::sort(f.profile.edges.begin(), f.profile.edges.end(), [](const auto& a, const auto& b) {
        return a.destination < b.destination ||
            (a.destination == b.destination && a.source < b.source);
    });
    CHECK(measured(summary, Interval::CoreQuery, [&] {
        return validate_source_leakage_profile(f.profile);
    }) == Status::Ok);
    f.profile.edges.back().gain = 1.0;
    CHECK(measured(summary, Interval::CoreReject, [&] {
        return validate_source_leakage_profile(f.profile);
    }) == Status::InvalidProfile);
}

void prepare_events() {
    auto& f = fixtures;
    std::size_t index = 0;
    for (const auto manual : {Manual::Upper, Manual::Lower}) {
        for (std::size_t bar = 0; bar < kDrawbarBankCount * kDrawbarCount; ++bar)
            f.setup[index++] = {0, EventType::BankDrawbar, manual, static_cast<std::uint8_t>(bar), 8.0};
        f.setup[index++] = {0, EventType::SelectBank, manual, 0, 1.0};
        for (std::uint32_t note = kMinManualMidiNote; note <= kMaxManualMidiNote; ++note)
            f.setup[index++] = {0, EventType::NoteOn, manual, static_cast<std::uint8_t>(note), 127.0};
    }
    for (std::uint8_t pedal = 1; pedal <= kPedalCount; ++pedal)
        f.setup[index++] = {0, EventType::PedalOn, Manual::Lower, pedal, 127.0};
    for (std::uint8_t mixture = 0; mixture < kPedalDrawbarCount; ++mixture)
        f.setup[index++] = {0, EventType::PedalDrawbar, Manual::Lower, mixture, 8.0};
    for (std::uint8_t setting = 0; setting < 4; ++setting)
        f.setup[index++] = {0, EventType::Percussion, Manual::Upper, setting, 1.0};
    f.setup[index++] = {0, EventType::Expression, Manual::Upper, 0, 0.75};
    CHECK(index == f.setup.size());
    for (std::size_t i = 0; i < f.dense.size(); ++i)
        f.dense[i] = {static_cast<std::uint32_t>(i / 4), EventType::Drawbar,
            i % 2 == 0 ? Manual::Upper : Manual::Lower, static_cast<std::uint8_t>(i % 9),
            i % 2 == 0 ? 7.0 : 8.0};
    f.invalid = f.dense;
    f.invalid.back().value = std::numeric_limits<double>::quiet_NaN();
}

void process(Summary& summary, Engine& engine, std::uint32_t frames,
             std::span<float> output, std::span<const Event> events = {},
             Status expected = Status::Ok) {
    const auto clock = engine.frame_clock();
    const auto interval = expected != Status::Ok ? Interval::EngineReject :
        frames == 0 ? Interval::EngineFlush : Interval::EngineProcess;
    const auto result = measured(summary, interval, [&] {
        return engine.process(frames, output, events);
    });
    CHECK(result.status == expected);
    CHECK(result.events_consumed == (expected == Status::Ok ? events.size() : 0));
    CHECK(engine.frame_clock() == clock + (expected == Status::Ok ? frames : 0));
    if (expected == Status::Ok) {
        summary.engine_frames += frames;
        summary.engine_events += events.size();
    }
}

void equal_engine_output() {
    const auto& f = fixtures;
    for (std::size_t index = 0; index < kBlock; ++index)
        CHECK(std::bit_cast<std::uint32_t>(f.audio[index]) ==
              std::bit_cast<std::uint32_t>(f.reference[index]));
    CHECK(f.engine.frame_clock() == f.control.frame_clock());
    CHECK(f.engine.last_pedal_frame() == f.control.last_pedal_frame());
}

void engine_resources(const RuntimeProfile& profile, double rate, bool travel, Summary& summary) {
    auto& f = fixtures;
    CHECK(f.engine.prepare(profile, {rate, kBlock, 9187, 0},
        travel ? make_nominal_console_model() : make_legacy_console_model()) == Status::Ok);
    {
        SourceLeakage author;
        CHECK(author.prepare(std::span<const SourceLeakageEdge>(f.edges).first(728)) == Status::Ok);
        CHECK(measured(summary, Interval::EngineInstall, [&] {
            return f.engine.set_source_leakage(author, 0.5);
        }) == Status::Ok);
        CHECK(measured(summary, Interval::EngineCopy, [&] {
            f.control = f.engine;
            return f.control.prepared();
        }));
        CHECK(author.prepare({}) == Status::Ok);
    }
    const auto configuration = measured(summary, Interval::EngineQuery, [&] {
        return f.engine.source_leakage_configuration();
    });
    CHECK(configuration.configured && configuration.edge_count == 728);
    CHECK(configuration.guarded_output_bound <= 1.0);

    // First positive call after setup is observed while silent.
    process(summary, f.engine, kBlock, f.audio);
    process(summary, f.control, kBlock, f.reference);
    equal_engine_output();
    CHECK(std::all_of(f.audio.begin(), f.audio.begin() + kBlock, [](float x) { return x == 0.0F; }));
    process(summary, f.engine, 0, {}, f.setup);
    process(summary, f.control, 0, {}, f.setup);
    CHECK(f.engine.active_key_count() == 122 && f.engine.active_pedal_count() == 25);
    for (std::size_t block = 0; block < 24; ++block) {
        const bool disconnected = block % 3 == 0;
        process(summary, f.engine, kBlock, disconnected ? std::span<float>{} : std::span<float>(f.audio));
        process(summary, f.control, kBlock, f.reference);
        if (!disconnected) equal_engine_output();
        CHECK(f.engine.last_pedal_frame() == f.control.last_pedal_frame());
        CHECK(std::isfinite(f.engine.last_pedal_frame().voice.output));
    }
    // Full event capacity also exercises coefficient rebuilds at every frame.
    process(summary, f.engine, kBlock, f.audio, f.dense);
    process(summary, f.control, kBlock, f.reference, f.dense);
    equal_engine_output();

    const auto before = f.engine.frame_clock();
    const auto last_pedal = f.engine.last_pedal_frame();
    const SourceLeakage unprepared;
    for (const double invalid_gain : {1.0, -0.5, std::numeric_limits<double>::quiet_NaN()})
        CHECK(measured(summary, Interval::EngineReject, [&] {
            return f.engine.set_source_leakage(f.graph, invalid_gain);
        }) == Status::InvalidSpec);
    CHECK(measured(summary, Interval::EngineReject, [&] {
        return f.engine.set_source_leakage(unprepared, 0.5);
    }) == Status::InvalidProfile);
    process(summary, f.engine, kBlock, f.audio, f.invalid, Status::InvalidEvent);
    process(summary, f.engine, kBlock, std::span<float>(f.audio).first(kBlock - 1), {}, Status::InvalidBuffer);
    process(summary, f.engine, kBlock + 1, f.audio, {}, Status::BlockTooLarge);
    CHECK(f.engine.frame_clock() == before && f.engine.last_pedal_frame() == last_pedal);
    CHECK(f.engine.source_leakage_configuration() == configuration);
    process(summary, f.engine, kBlock, f.audio);
    process(summary, f.control, kBlock, f.reference);
    equal_engine_output();

    for (Engine* engine : {&f.engine, &f.control}) {
        CHECK(measured(summary, Interval::EngineInstall, [&] {
            return engine->set_source_leakage(f.graph, 0.0);
        }) == Status::Ok);
    }
    process(summary, f.engine, kBlock, f.audio);
    process(summary, f.control, kBlock, f.reference);
    equal_engine_output();
    CHECK(std::all_of(f.audio.begin(), f.audio.begin() + kBlock, [](float x) { return x == 0.0F; }));
    for (Engine* engine : {&f.engine, &f.control}) {
        CHECK(measured(summary, Interval::EngineClear, [&] {
            return engine->clear_source_leakage();
        }) == Status::Ok);
        CHECK(measured(summary, Interval::EngineClear, [&] {
            return engine->clear_source_leakage();
        }) == Status::Ok);
    }
    process(summary, f.engine, kBlock, f.audio);
    process(summary, f.control, kBlock, f.reference);
    equal_engine_output();
    CHECK(!f.engine.source_leakage_configuration().configured);
    ++summary.fixtures;
}

} // namespace

int main() {
    static_assert(std::is_trivially_copyable_v<SourceLeakage>);
    static_assert(std::is_trivially_destructible_v<SourceLeakage>);
    static_assert(sizeof(SourceLeakage) <= 32768);
    const auto profile = load_test_profile(); // Parsing/I/O is deliberately outside observation.
    Summary summary;
    test_probe_overloads();
    core_resources(summary);
    prepare_events();
    for (const double rate : {44100.0, 48000.0, 96000.0})
        for (const bool travel : {false, true}) engine_resources(profile, rate, travel, summary);
    test_probe_overloads();
    CHECK(summary.fixtures == 6);
    CHECK(summary.core_frames == 2050);
    constexpr std::array<const char*, 12> names{
        "core_prepare", "core_process", "core_copy_destroy", "core_query", "core_rejection",
        "engine_install", "engine_clear", "engine_copy", "engine_process", "engine_flush",
        "engine_rejection", "engine_query"};
    std::cout << "{\"status\":\"passed\",\"observer\":\"current-thread-global-C++-allocation-calls\""
              << ",\"positive_control_allocations\":24,\"positive_control_deallocations\":24"
              << ",\"maximum_edges\":728,\"source_leakage_bytes\":" << sizeof(SourceLeakage)
              << ",\"source_frame_bytes\":" << sizeof(SourceLeakageFrame)
              << ",\"source_profile_bytes\":" << sizeof(SourceLeakageProfile)
              << ",\"engine_bytes\":" << sizeof(Engine)
              << ",\"static_test_fixture_bytes\":" << sizeof(Fixtures)
              << ",\"stack_high_water_measured\":false,\"timing_measured\":false"
              << ",\"fixtures\":" << summary.fixtures << ",\"core_frames\":" << summary.core_frames
              << ",\"engine_frames\":" << summary.engine_frames
              << ",\"engine_events\":" << summary.engine_events << ",\"intervals\":{";
    for (std::size_t index = 0; index < names.size(); ++index) {
        const auto& total = summary.intervals[index];
        CHECK(total.calls != 0);
        if (index != 0) std::cout << ',';
        std::cout << '\"' << names[index] << "\":{\"calls\":" << total.calls
                  << ",\"allocations\":" << total.allocations
                  << ",\"deallocations\":" << total.deallocations << '}';
    }
    std::cout << "}}\n";
    return EXIT_SUCCESS;
}

