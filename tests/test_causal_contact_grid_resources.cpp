#include "TestSupport.h"
#include "hammond/research/CausalContactGrid.h"

#if defined(HAMMOND_GRID_WORK_RECEIPT)
#include "CausalContactGridWorkCounters.h"
#endif

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <limits>
#include <memory>
#include <new>
#include <span>
#include <type_traits>

#if defined(_MSC_VER)
#include <malloc.h>
#endif

// Probe and twelve-overload calibration follow test_leslie_crossover_allocation.
// Only the named public grid calls below are armed; setup and assertions are not. They are local to this executable and observe C++ calls.
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

using namespace hammond::research;

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

// The optional diagnostic is compiled only against a generated scratch copy of
// the implementation. Normal CMake tests do not instrument production code.
#if defined(HAMMOND_GRID_WORK_RECEIPT)
using WorkCounts = hammond::research::work_receipt::Counts;
constexpr bool workAvailable = true;
#else
struct WorkCounts {
    std::uint64_t target_validations{}, target_applications{};
    std::uint64_t position_evaluations{}, contact_examinations{};
    std::uint64_t reached_roots{}, gcd_normalizations{}, euclidean_remainders{};
    std::uint64_t edge_comparisons{}, committed_edge_copies{};
};
constexpr bool workAvailable = false;
#endif

enum class Api : std::size_t { construct, prepare, process, snapshot, close, reset, destroy, count };
constexpr std::array<const char*, 7> apiNames{
    "construct", "prepare", "process", "snapshot", "close_observation", "reset", "destroy"};
constexpr ContactGridEdge sentinel{{4294967295U, 0, 1}, 4294967295U, 4294967295U, true};
constexpr std::uint64_t digestSeed = 14695981039346656037ULL;

// Semantic hashes use fields and a fixed byte order, never padding or pointers.
void hash_word(std::uint64_t& hash, std::uint64_t value) noexcept {
    for (unsigned shift = 0; shift < 64; shift += 8) {
        hash ^= (value >> shift) & 255U;
        hash *= 1099511628211ULL;
    }
}

void hash_snapshot(std::uint64_t& hash, const ContactGridSnapshot& state) noexcept {
    hash_word(hash, static_cast<std::uint64_t>(state.phase));
    hash_word(hash, state.config.sampleRateHz);
    hash_word(hash, state.config.keyCount);
    for (const auto& key : state.config.keys) {
        hash_word(hash, key.pressUnitsPerTick);
        hash_word(hash, key.releaseUnitsPerTick);
        for (const auto& threshold : key.contacts) {
            hash_word(hash, threshold.off);
            hash_word(hash, threshold.on);
        }
    }
    hash_word(hash, state.cursorFrames);
    hash_word(hash, state.commandCount);
    hash_word(hash, state.edgeCount);
    for (const auto& key : state.keys) {
        hash_word(hash, key.position);
        hash_word(hash, key.target);
        hash_word(hash, key.anchorPosition);
        hash_word(hash, key.anchorTick);
        for (const bool closed : key.closed) hash_word(hash, closed);
    }
}

struct Record {
    const char* scenario{};
    Api api{};
    std::uint32_t rate{}, keys{};
    std::size_t supplied{};
    ContactGridStatus status{};
    std::uint32_t edges{}, required{};
    allocation_probe::Counts allocation{};
    WorkCounts work{};
};
struct Summary {
    std::array<Record, 384> records{};
    std::size_t used{}, calibrations{}, edgeChecks{}, snapshotChecks{};
    std::uint64_t semanticHash{digestSeed};
};

void record_result(Record& record, Summary& summary, ContactGridStatus status) {
    record.status = status;
    hash_word(summary.semanticHash, static_cast<std::uint64_t>(status));
}
void record_result(Record& record, Summary& summary, ContactGridResult result) {
    record.status = result.status;
    record.edges = result.edgesWritten;
    record.required = result.requiredEdges;
    hash_word(summary.semanticHash, static_cast<std::uint64_t>(result.status));
    hash_word(summary.semanticHash, result.edgesWritten);
    hash_word(summary.semanticHash, result.requiredEdges);
}
void record_result(Record&, Summary& summary, const ContactGridSnapshot& state) {
    hash_snapshot(summary.semanticHash, state);
}

template<class Operation>
auto observed(Summary& summary, Api api, const char* scenario, std::uint32_t rate,
              std::uint32_t keys, std::size_t supplied, Operation operation) {
    CHECK(summary.used < summary.records.size());
#if defined(HAMMOND_GRID_WORK_RECEIPT)
    hammond::research::work_receipt::begin();
#endif
    allocation_probe::begin();
    const auto result = operation();
    const auto allocation = allocation_probe::end();
    WorkCounts work{};
#if defined(HAMMOND_GRID_WORK_RECEIPT)
    work = hammond::research::work_receipt::end();
#endif
    // The probe is disarmed before record writes, checks, hashing or formatting.
    auto& record = summary.records[summary.used++];
    record.scenario = scenario;
    record.api = api;
    record.rate = rate;
    record.keys = keys;
    record.supplied = supplied;
    record.allocation = allocation;
    record.work = work;
    record_result(record, summary, result);
    CHECK(allocation.allocations == 0);
    CHECK(allocation.deallocations == 0);
    return result;
}

// All large objects, including the grid's placement-new backing storage, live
// on the heap. Their allocation and final release are outside armed scopes.
struct Buffers {
    alignas(CausalContactGrid) std::array<std::byte, sizeof(CausalContactGrid)> object{};
    std::array<ContactGridTarget, kContactGridMaxCommands + 1> commands{};
    std::array<ContactGridEdge, kContactGridMaxEdges + 1> output{};
    std::array<ContactGridEdge, kContactGridMaxEdges + 1> saved{};
};

struct Harness {
    Summary& summary;
    std::uint32_t rate{}, keys{};
    std::unique_ptr<Buffers> buffers{std::make_unique<Buffers>()};
    CausalContactGrid* grid{};

    Harness(Summary& summaryIn, std::uint32_t rateIn) : summary(summaryIn), rate(rateIn) {
        CHECK(observed(summary, Api::construct, "placement_construct", rate, 0, 0, [&] {
            grid = ::new (static_cast<void*>(buffers->object.data())) CausalContactGrid;
            return ContactGridStatus::ok;
        }) == ContactGridStatus::ok);
    }
    ~Harness() {
        CHECK(observed(summary, Api::destroy, "explicit_destroy", rate, keys, 0, [&] {
            std::destroy_at(grid);
            return ContactGridStatus::ok;
        }) == ContactGridStatus::ok);
    }
    ContactGridStatus prepare(const char* label, const ContactGridConfig& config) {
        const auto result = observed(summary, Api::prepare, label, rate, keys, 0,
                                     [&] { return grid->prepare(config); });
        if (result == ContactGridStatus::ok) keys = config.keyCount;
        return result;
    }
    ContactGridResult process(const char* label, std::uint32_t frames,
                              std::size_t supplied, std::size_t capacity) {
        const auto input = std::span<const ContactGridTarget>(buffers->commands).first(supplied);
        const auto output = std::span<ContactGridEdge>(buffers->output).first(capacity);
        return observed(summary, Api::process, label, rate, keys, supplied,
                        [&] { return grid->process(frames, input, output); });
    }
    ContactGridStatus close(const char* label, std::size_t supplied = 0) {
        const auto input = std::span<const ContactGridTarget>(buffers->commands).first(supplied);
        return observed(summary, Api::close, label, rate, keys, supplied,
                        [&] { return grid->close_observation(input); });
    }
    ContactGridStatus reset(const char* label) {
        return observed(summary, Api::reset, label, rate, keys, 0, [&] { return grid->reset(); });
    }
    ContactGridSnapshot snapshot(const char* label) {
        return observed(summary, Api::snapshot, label, rate, keys, 0, [&] { return grid->snapshot(); });
    }
    void mark_output() {
        buffers->output.fill(sentinel);
        std::memcpy(buffers->saved.data(), buffers->output.data(), sizeof(buffers->output));
    }
    void output_unchanged() const {
        CHECK(std::memcmp(buffers->saved.data(), buffers->output.data(), sizeof(buffers->output)) == 0);
    }
};

void expect(ContactGridResult actual, ContactGridStatus status,
            std::uint32_t written = 0, std::uint32_t required = 0) {
    CHECK(actual.status == status);
    CHECK(actual.edgesWritten == written);
    CHECK(actual.requiredEdges == required);
}

void expect_snapshot(Summary& summary, const ContactGridSnapshot& actual,
                     const ContactGridSnapshot& expected) {
    CHECK(actual.phase == expected.phase);
    CHECK(actual.config.sampleRateHz == expected.config.sampleRateHz);
    CHECK(actual.config.keyCount == expected.config.keyCount);
    CHECK(actual.cursorFrames == expected.cursorFrames);
    CHECK(actual.commandCount == expected.commandCount);
    CHECK(actual.edgeCount == expected.edgeCount);
    for (std::size_t k = 0; k < 4; ++k) {
        CHECK(actual.config.keys[k].pressUnitsPerTick == expected.config.keys[k].pressUnitsPerTick);
        CHECK(actual.config.keys[k].releaseUnitsPerTick == expected.config.keys[k].releaseUnitsPerTick);
        for (std::size_t c = 0; c < 9; ++c) {
            CHECK(actual.config.keys[k].contacts[c].off == expected.config.keys[k].contacts[c].off);
            CHECK(actual.config.keys[k].contacts[c].on == expected.config.keys[k].contacts[c].on);
        }
        CHECK(actual.keys[k].position == expected.keys[k].position);
        CHECK(actual.keys[k].target == expected.keys[k].target);
        CHECK(actual.keys[k].anchorPosition == expected.keys[k].anchorPosition);
        CHECK(actual.keys[k].anchorTick == expected.keys[k].anchorTick);
        CHECK(actual.keys[k].closed == expected.keys[k].closed);
    }
    ++summary.snapshotChecks;
}

void expect_edge(Summary& summary, const ContactGridEdge& actual,
                 ContactGridTime time, std::uint32_t key, std::uint32_t contact, bool closed) {
    CHECK(actual.time.tick == time.tick);
    CHECK(actual.time.numerator == time.numerator);
    CHECK(actual.time.denominator == time.denominator);
    CHECK(actual.keyIndex == key);
    CHECK(actual.contactIndex == contact);
    CHECK(actual.closedAfter == closed);
    hash_word(summary.semanticHash, actual.time.tick);
    hash_word(summary.semanticHash, actual.time.numerator);
    hash_word(summary.semanticHash, actual.time.denominator);
    hash_word(summary.semanticHash, actual.keyIndex);
    hash_word(summary.semanticHash, actual.contactIndex);
    hash_word(summary.semanticHash, actual.closedAfter);
    ++summary.edgeChecks;
}

ContactGridConfig configuration(std::uint32_t rate, std::uint32_t speed = 1,
                                std::uint64_t off = 1, std::uint64_t on = 100) {
    ContactGridConfig result{};
    result.sampleRateHz = rate;
    result.keyCount = 4;
    for (auto& key : result.keys) {
        key.pressUnitsPerTick = speed;
        key.releaseUnitsPerTick = speed;
        key.contacts.fill({off, on});
    }
    return result;
}

ContactGridSnapshot ready_snapshot(const ContactGridConfig& config) {
    ContactGridSnapshot result{};
    result.phase = ContactGridPhase::ready;
    result.config = config;
    return result;
}

void fixture(std::uint32_t rate, Summary& summary) {
    CHECK(calibrate().passed());
    ++summary.calibrations;
    Harness h(summary, rate);
    auto config = configuration(rate);
    h.mark_output();
    expect_snapshot(summary, h.snapshot("unprepared_snapshot"), {});
    expect(h.process("unprepared_empty", 0, 0, 0), ContactGridStatus::invalid_state);
    expect(h.process("unprepared_process", 1, 0, 4608), ContactGridStatus::invalid_state);
    CHECK(h.close("unprepared_close") == ContactGridStatus::invalid_state);
    CHECK(h.reset("unprepared_reset") == ContactGridStatus::invalid_state);
    auto invalid = config;
    invalid.sampleRateHz = 1;
    CHECK(h.prepare("invalid_rate", invalid) == ContactGridStatus::invalid_configuration);
    invalid = config;
    invalid.keyCount = 5;
    CHECK(h.prepare("invalid_key_count", invalid) == ContactGridStatus::invalid_configuration);
    invalid = config;
    invalid.keys[3].releaseUnitsPerTick = 0;
    CHECK(h.prepare("late_invalid_speed", invalid) == ContactGridStatus::invalid_configuration);
    invalid = config;
    invalid.keys[3].contacts[8].off = invalid.keys[3].contacts[8].on;
    CHECK(h.prepare("late_invalid_threshold", invalid) == ContactGridStatus::invalid_configuration);
    CHECK(h.prepare("first_prepare", config) == ContactGridStatus::ok);
    CHECK(h.prepare("ready_prepare", config) == ContactGridStatus::ok);
    const auto ready = ready_snapshot(config);
    expect_snapshot(summary, h.snapshot("ready_snapshot"), ready);
    CHECK(h.reset("ready_reset") == ContactGridStatus::invalid_state);
    expect(h.process("ready_empty", 0, 0, 4608), ContactGridStatus::ok);
    h.buffers->commands.fill({0, 0, 128});
    expect(h.process("empty_nonempty_input", 0, 1, 4608), ContactGridStatus::invalid_target);
    expect(h.process("excess_frames", 4294967295U, 0, 4608), ContactGridStatus::frame_limit);
    expect(h.process("excess_commands", 1, 513, 4608), ContactGridStatus::command_limit);
    h.buffers->commands[511].keyIndex = 4;
    expect(h.process("late_invalid_key", 1, 512, 4608), ContactGridStatus::invalid_target);
    h.buffers->commands[511] = {0, 0, kContactGridFullTravel + 1};
    expect(h.process("late_invalid_position", 1, 512, 4608), ContactGridStatus::invalid_target);
    h.buffers->commands[511] = {65536, 0, 128};
    expect(h.process("late_invalid_tick", 1, 512, 4608), ContactGridStatus::invalid_target);
    h.buffers->commands[511] = {0, 0, 128};
    h.buffers->commands[0].tick = 1;
    expect(h.process("unordered_targets", 1, 512, 4608), ContactGridStatus::unordered_targets);
    h.buffers->commands[511].position = kContactGridFullTravel + 1;
    expect(h.process("domain_before_order", 1, 512, 4608), ContactGridStatus::invalid_target);
    h.buffers->commands.fill({0, 0, 128});
    CHECK(h.close("excess_closing_commands", 513) == ContactGridStatus::command_limit);
    h.buffers->commands[511].tick = 1;
    CHECK(h.close("late_invalid_closing_tick", 512) == ContactGridStatus::invalid_target);
    h.output_unchanged();
    expect_snapshot(summary, h.snapshot("rejections_preserve_ready"), ready);

    // Admitted independent construction: every batch has 36 reverse-time roots.
    // All 512 commands produce nine edges; insertion sort makes 128*630 comparisons.
    for (std::uint32_t k = 0; k < 4; ++k) {
        for (std::uint32_t c = 0; c < 9; ++c) {
            const auto i = 9 * k + c;
            config.keys[k].contacts[c] = {1 + i, 100 - i};
        }
    }
    CHECK(h.prepare("maximum_capacity_prepare", config) == ContactGridStatus::ok);
    for (std::uint32_t group = 0; group < 128; ++group) {
        for (std::uint32_t key = 0; key < 4; ++key) {
            h.buffers->commands[4 * group + key] = {128 * group, key, group % 2 == 0 ? 128U : 0U};
        }
    }
    h.mark_output();
    expect(h.process("maximum_capacity_short", 4096, 512, 4607),
           ContactGridStatus::output_too_small, 0, 4608);
    h.output_unchanged();
    expect_snapshot(summary, h.snapshot("short_output_snapshot"), ready_snapshot(config));
    expect(h.process("maximum_capacity_retry", 4096, 512, 4608), ContactGridStatus::ok, 4608, 4608);
    for (std::uint32_t group = 0; group < 128; ++group) {
        for (std::uint32_t item = 0; item < 36; ++item) {
            const auto i = 35 - item;
            expect_edge(summary, h.buffers->output[36 * group + item],
                        {128 * group + (group % 2 == 0 ? 100U : 127U) - i, 0, 1},
                        i / 9, i % 9, group % 2 == 0);
        }
    }
    CHECK(std::memcmp(&h.buffers->output[4608], &h.buffers->saved[4608], sizeof(ContactGridEdge)) == 0);
    auto expected = ready_snapshot(config);
    expected.phase = ContactGridPhase::active;
    expected.cursorFrames = 4096;
    expected.commandCount = 512;
    expected.edgeCount = 4608;
    for (auto& key : expected.keys) {
        key.anchorPosition = 128;
        key.anchorTick = 16256;
    }
    expect_snapshot(summary, h.snapshot("maximum_capacity_snapshot"), expected);
    h.mark_output();
    expect(h.process("exhausted_empty", 0, 0, 4608), ContactGridStatus::ok);
    expect(h.process("exhausted_frames", 1, 0, 4608), ContactGridStatus::frame_limit);
    expect(h.process("exhausted_commands", 0, 1, 4608), ContactGridStatus::command_limit);
    CHECK(h.prepare("active_prepare", config) == ContactGridStatus::invalid_state);
    CHECK(h.reset("active_reset") == ContactGridStatus::invalid_state);
    CHECK(h.close("exhausted_closing_commands", 1) == ContactGridStatus::command_limit);
    CHECK(h.close("active_empty_close") == ContactGridStatus::ok);
    expected.phase = ContactGridPhase::closed;
    expect_snapshot(summary, h.snapshot("closed_snapshot"), expected);
    expect(h.process("closed_empty", 0, 0, 4608), ContactGridStatus::invalid_state);
    expect(h.process("closed_process", 1, 0, 4608), ContactGridStatus::invalid_state);
    CHECK(h.close("repeated_close") == ContactGridStatus::invalid_state);
    CHECK(h.reset("closed_reset") == ContactGridStatus::ok);
    expect_snapshot(summary, h.snapshot("reset_snapshot"), ready_snapshot(config));
    h.output_unchanged();

    // Distinct command ticks attain 4*(512+1) position evaluations. Four initial
    // holds reduce candidate visits from the conservative ceiling by 90.
    config = configuration(rate, 1, kContactGridFullTravel - 1, kContactGridFullTravel);
    CHECK(h.prepare("maximum_traversal_prepare", config) == ContactGridStatus::ok);
    for (std::uint32_t i = 0; i < 512; ++i) {
        h.buffers->commands[i] = {i + 1, i < 4 ? i : 0, kContactGridFullTravel};
    }
    expect(h.process("maximum_traversal", 4096, 512, 0), ContactGridStatus::ok);
    expected = ready_snapshot(config);
    expected.phase = ContactGridPhase::active;
    expected.cursorFrames = 4096;
    expected.commandCount = 512;
    for (std::uint32_t key = 0; key < 4; ++key) {
        expected.keys[key].position = 268435456U - (key + 1);
        expected.keys[key].target = kContactGridFullTravel;
        expected.keys[key].anchorTick = key + 1;
    }
    expect_snapshot(summary, h.snapshot("maximum_traversal_snapshot"), expected);
    CHECK(h.close("maximum_traversal_close") == ContactGridStatus::ok);

    // Consecutive Fibonacci operands force a long 32-bit Euclidean chain.
    config = configuration(rate, 2971215073U, 0, 1836311903U);
    CHECK(h.prepare("fibonacci_prepare_closed", config) == ContactGridStatus::ok);
    for (std::uint32_t key = 0; key < 4; ++key) h.buffers->commands[key] = {0, key, kContactGridFullTravel};
    expect(h.process("fibonacci_roots", 1, 4, 36), ContactGridStatus::ok, 36, 36);
    for (std::uint32_t i = 0; i < 36; ++i) {
        expect_edge(summary, h.buffers->output[i], {0, 1836311903U, 2971215073U}, i / 9, i % 9, true);
    }
    expected = ready_snapshot(config);
    expected.phase = ContactGridPhase::active;
    expected.cursorFrames = 1;
    expected.commandCount = 4;
    expected.edgeCount = 36;
    for (auto& key : expected.keys) {
        key.position = std::uint64_t{65536} * 2971215073U;
        key.target = kContactGridFullTravel;
        key.closed.fill(true);
    }
    expect_snapshot(summary, h.snapshot("fibonacci_snapshot"), expected);
    for (std::uint32_t key = 0; key < 4; ++key) h.buffers->commands[key] = {65536, key, 0};
    CHECK(h.close("nonempty_close", 4) == ContactGridStatus::ok);
    expected.phase = ContactGridPhase::closed;
    expected.commandCount = 8;
    for (auto& key : expected.keys) {
        key.anchorPosition = key.position;
        key.anchorTick = 65536;
        key.target = 0;
    }
    expect_snapshot(summary, h.snapshot("nonempty_closed_snapshot"), expected);
    CHECK(h.reset("nonempty_closed_reset") == ContactGridStatus::ok);

    config = configuration(rate, 4294967295U, kContactGridFullTravel / 4, kContactGridFullTravel / 2);
    CHECK(h.prepare("maximum_speed_prepare", config) == ContactGridStatus::ok);
    for (std::uint32_t key = 0; key < 4; ++key) h.buffers->commands[key] = {0, key, kContactGridFullTravel};
    expect(h.process("maximum_speed", 4096, 4, 36), ContactGridStatus::ok, 36, 36);
    for (std::uint32_t i = 0; i < 36; ++i) {
        expect_edge(summary, h.buffers->output[i], {32768, 32768, 4294967295U}, i / 9, i % 9, true);
    }
    expected = ready_snapshot(config);
    expected.phase = ContactGridPhase::active;
    expected.cursorFrames = 4096;
    expected.commandCount = 4;
    expected.edgeCount = 36;
    for (auto& key : expected.keys) {
        key.position = kContactGridFullTravel;
        key.target = kContactGridFullTravel;
        key.closed.fill(true);
    }
    expect_snapshot(summary, h.snapshot("maximum_speed_snapshot"), expected);
    CHECK(h.close("maximum_speed_close") == ContactGridStatus::ok);

    // N=0 closure can consume the complete budget without any motion or edge.
    CHECK(h.prepare("zero_epoch_prepare", config) == ContactGridStatus::ok);
    h.buffers->commands.fill({0, 0, kContactGridFullTravel});
    CHECK(h.close("zero_epoch_maximum_close", 512) == ContactGridStatus::ok);
    expected = ready_snapshot(config);
    expected.phase = ContactGridPhase::closed;
    expected.commandCount = 512;
    expected.keys[0].target = kContactGridFullTravel;
    expect_snapshot(summary, h.snapshot("zero_epoch_snapshot"), expected);
    CHECK(h.reset("zero_epoch_reset") == ContactGridStatus::ok);
    CHECK(h.close("ready_empty_close") == ContactGridStatus::ok);
    CHECK(calibrate().passed());
    ++summary.calibrations;
}

void write_work(const WorkCounts& work) {
    std::cout << "{\"target_validations\":" << work.target_validations
              << ",\"target_applications\":" << work.target_applications
              << ",\"position_evaluations\":" << work.position_evaluations
              << ",\"contact_examinations\":" << work.contact_examinations
              << ",\"reached_roots\":" << work.reached_roots
              << ",\"gcd_normalizations\":" << work.gcd_normalizations
              << ",\"euclidean_remainders\":" << work.euclidean_remainders
              << ",\"edge_comparisons\":" << work.edge_comparisons
              << ",\"committed_edge_copies\":" << work.committed_edge_copies << '}';
}

void report(const Summary& summary) {
    constexpr auto stateBytes = sizeof(ContactGridSnapshot);
    constexpr auto stagedEdgeBytes = sizeof(std::array<ContactGridEdge, kContactGridMaxEdges>);
    constexpr auto intervalBytes = sizeof(std::array<ContactGridEdge, 36>);
    std::array<std::size_t, 7> apiCounts{};
    for (std::size_t i = 0; i < summary.used; ++i) ++apiCounts[static_cast<std::size_t>(summary.records[i].api)];
    std::cout << "{\"schema_version\":1,\"model\":\"causal-contact-grid-v1\",\"passed\":true"
              << ",\"work_instrumented\":" << (workAvailable ? "true" : "false")
              << ",\"semantic_hash_fnv1a64\":\"" << std::hex << summary.semanticHash << std::dec << '"'
              << ",\"calibrations\":" << summary.calibrations
              << ",\"calibration_allocations_each\":12,\"calibration_deallocations_each\":12"
              << ",\"edge_assertions\":" << summary.edgeChecks
              << ",\"snapshot_assertions\":" << summary.snapshotChecks
              << ",\"sizes\":{\"object_bytes\":" << sizeof(CausalContactGrid)
              << ",\"snapshot_bytes\":" << stateBytes
              << ",\"edge_bytes\":" << sizeof(ContactGridEdge)
              << ",\"staged_edges_bytes\":" << stagedEdgeBytes
              << ",\"interval_edges_bytes\":" << intervalBytes
              << ",\"embedded_scratch_payload_bytes\":" << stateBytes + stagedEdgeBytes + intervalBytes
              << ",\"object_minus_live_snapshot_bytes\":" << sizeof(CausalContactGrid) - stateBytes
              << ",\"fixture_heap_bytes\":" << sizeof(Buffers)
              << "},\"api_counts\":{";
    for (std::size_t i = 0; i < apiCounts.size(); ++i) {
        if (i != 0) std::cout << ',';
        std::cout << '"' << apiNames[i] << "\":" << apiCounts[i];
    }
    std::cout << "},\"calls\":[";
    for (std::size_t i = 0; i < summary.used; ++i) {
        if (i != 0) std::cout << ',';
        const auto& record = summary.records[i];
        std::cout << "{\"scenario\":\"" << record.scenario << "\",\"rate\":" << record.rate
                  << ",\"api\":\"" << apiNames[static_cast<std::size_t>(record.api)]
                  << "\",\"configured_keys\":" << record.keys << ",\"supplied_commands\":" << record.supplied
                  << ",\"status\":" << static_cast<unsigned>(record.status)
                  << ",\"edges_written\":" << record.edges << ",\"required_edges\":" << record.required
                  << ",\"allocations\":" << record.allocation.allocations
                  << ",\"deallocations\":" << record.allocation.deallocations << ",\"work\":";
        if (workAvailable) write_work(record.work); else std::cout << "null";
        std::cout << '}';
    }
    std::cout << "]}\n";
}

} // namespace

int main() {
    // Summary storage is also allocated before any API observation starts.
    auto summary = std::make_unique<Summary>();
    for (const auto rate : std::array<std::uint32_t, 3>{44100, 48000, 96000}) fixture(rate, *summary);
    report(*summary);
    return EXIT_SUCCESS;
}
