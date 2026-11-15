#include "TestSupport.h"
#include "hammond/LeslieCrossover.h"

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

enum class Interval : std::size_t {
    Scalar, Block, Empty, Observe, Reject,
    OfflinePrepare, OfflineRestore, OfflineRate, OfflineResponse, Count
};

struct Totals {
    std::size_t calls{}, allocations{}, deallocations{};
};
struct Summary {
    std::array<Totals, static_cast<std::size_t>(Interval::Count)> intervals{};
    std::size_t fixtures{}, calibrations{}, scalar_frames{}, block_frames{};
};

// All storage, assertions, formatting and fixture setup stay outside recording.
// In particular, the test observes the very first successful processing call;
// it does not warm up and conceal a hypothetical lazy allocation.
template<class Operation>
[[nodiscard]] Status measured(Summary& summary, Interval interval, Operation operation) {
    allocation_probe::begin();
    const Status status = operation();
    const auto observed = allocation_probe::end();
    auto& total = summary.intervals[static_cast<std::size_t>(interval)];
    ++total.calls;
    total.allocations += observed.allocations;
    total.deallocations += observed.deallocations;
    CHECK(observed.allocations == 0);
    CHECK(observed.deallocations == 0);
    return status;
}

void calibration(Summary& summary) {
    CHECK(calibrate().passed());
    ++summary.calibrations;
}

// Real storage backs even the intentionally oversized spans. Static test
// buffers avoid imposing a large stack requirement on the Windows runner.
struct Buffers {
    std::array<double, kLeslieCrossoverBlockCapacity + 1> input{};
    std::array<LeslieCrossoverFrame, kLeslieCrossoverBlockCapacity + 1> output{};
    std::array<LeslieCrossoverFrame, kLeslieCrossoverBlockCapacity + 1> saved{};
};
Buffers buffers;
constexpr LeslieCrossoverFrame sentinel{11.0, -12.0, 13.0, -14.0, 15.0, 16.0, 17};

void fixture(double rate, LeslieCrossoverLoads loads, Summary& summary) {
    calibration(summary);
    LeslieCrossover crossover;
    LeslieCrossoverFrame frame = sentinel;
    const auto input = std::span<const double>(buffers.input).first(kLeslieCrossoverBlockCapacity);
    const auto output = std::span<LeslieCrossoverFrame>(buffers.output).first(input.size());
    std::fill(buffers.output.begin(), buffers.output.end(), sentinel);
    for (std::size_t index = 0; index < buffers.input.size(); ++index) {
        buffers.input[index] = static_cast<double>(static_cast<int>(index % 17) - 8) / 8.0;
    }
    CHECK(measured(summary, Interval::Reject, [&] {
        return crossover.process_frame(0.0, frame);
    }) == Status::NotPrepared);
    CHECK(measured(summary, Interval::Reject, [&] {
        return crossover.process(input, output);
    }) == Status::NotPrepared);
    CHECK(measured(summary, Interval::Reject, [&] {
        return crossover.observe(frame);
    }) == Status::NotPrepared);
    CHECK(frame == sentinel);
    CHECK(measured(summary, Interval::OfflinePrepare, [&] {
        return crossover.prepare(rate, loads);
    }) == Status::Ok);
    CHECK(measured(summary, Interval::Observe, [&] { return crossover.observe(frame); }) == Status::Ok);
    CHECK(frame.frame == 0);

    constexpr std::array<double, 8> scalar_inputs{
        0.0, -0.0, 1.0, -1.0, 0.25, -0.75,
        std::numeric_limits<double>::denorm_min(), -std::numeric_limits<double>::denorm_min()};
    for (std::size_t index = 0; index < 128; ++index) {
        CHECK(measured(summary, Interval::Scalar, [&] {
            return crossover.process_frame(scalar_inputs[index % scalar_inputs.size()], frame);
        }) == Status::Ok);
        CHECK(frame.frame == crossover.state().frames);
        CHECK(std::isfinite(frame.input_current_amps));
        ++summary.scalar_frames;
        if (index % 16 == 0) {
            const auto expected = frame;
            CHECK(measured(summary, Interval::Observe, [&] { return crossover.observe(frame); }) == Status::Ok);
            CHECK(frame == expected);
        }
    }
    constexpr std::array<std::size_t, 5> sizes{1, 7, 64, 257, kLeslieCrossoverBlockCapacity};
    for (std::size_t repetition = 0; repetition < 8; ++repetition) {
        for (const auto size : sizes) {
            const auto before = crossover.state().frames;
            CHECK(measured(summary, Interval::Block, [&] {
                return crossover.process(input.first(size), output.first(size));
            }) == Status::Ok);
            CHECK(crossover.state().frames == before + size);
            CHECK(output[size - 1].frame == crossover.state().frames);
            summary.block_frames += size;
        }
    }
    const auto stable = crossover.state();
    CHECK(measured(summary, Interval::Empty, [&] { return crossover.process({}, {}); }) == Status::Ok);
    CHECK(crossover.state() == stable);

    // Late input failure traverses the complete maximum-size validation pass.
    std::fill(buffers.output.begin(), buffers.output.end(), sentinel);
    buffers.saved = buffers.output;
    buffers.input[kLeslieCrossoverBlockCapacity - 1] = std::numeric_limits<double>::quiet_NaN();
    CHECK(measured(summary, Interval::Reject, [&] {
        return crossover.process(input, output);
    }) == Status::InvalidBuffer);
    CHECK(crossover.state() == stable);
    CHECK(buffers.output == buffers.saved);
    buffers.input[kLeslieCrossoverBlockCapacity - 1] = 0.0;
    CHECK(measured(summary, Interval::Block, [&] {
        return crossover.process(input, output);
    }) == Status::Ok);
    summary.block_frames += input.size();

    const auto before_rejection = crossover.state();
    frame = sentinel;
    for (const auto invalid : std::array<double, 4>{
             std::numeric_limits<double>::infinity(), -std::numeric_limits<double>::infinity(),
             std::numeric_limits<double>::quiet_NaN(), std::nextafter(64.0, 65.0)}) {
        CHECK(measured(summary, Interval::Reject, [&] {
            return crossover.process_frame(invalid, frame);
        }) == Status::InvalidBuffer);
        CHECK(frame == sentinel);
        CHECK(crossover.state() == before_rejection);
    }
    CHECK(measured(summary, Interval::Reject, [&] {
        return crossover.process(input.first(1), {});
    }) == Status::InvalidBuffer);
    CHECK(measured(summary, Interval::Reject, [&] {
        return crossover.process(buffers.input, buffers.output);
    }) == Status::BlockTooLarge);
    CHECK(measured(summary, Interval::Reject, [&] {
        return crossover.process({&frame.treble_volts, 1}, {&frame, 1});
    }) == Status::InvalidBuffer);
    CHECK(frame == sentinel);
    CHECK(crossover.state() == before_rejection);

    // Offline paths have their own counters and are not relabelled realtime.
    LeslieCrossoverResponse response;
    for (const auto frequency : std::array<double, 3>{0.0, 800.0, rate * 0.49}) {
        CHECK(measured(summary, Interval::OfflineResponse, [&] {
            return crossover.response(frequency, response);
        }) == Status::Ok);
    }
    CHECK(measured(summary, Interval::OfflineResponse, [&] {
        return crossover.response(std::numeric_limits<double>::quiet_NaN(), response);
    }) == Status::InvalidSpec);
    CHECK(measured(summary, Interval::OfflineRate, [&] {
        return crossover.reconfigure_sample_rate(rate == 96000.0 ? 48000.0 : 96000.0);
    }) == Status::Ok);
    CHECK(crossover.state() == before_rejection);
    CHECK(measured(summary, Interval::OfflineRate, [&] {
        return crossover.reconfigure_sample_rate(0.0);
    }) == Status::InvalidSpec);
    CHECK(measured(summary, Interval::OfflinePrepare, [&] {
        return crossover.prepare(rate, {0.0, 16.0});
    }) == Status::InvalidSpec);
    CHECK(crossover.state() == before_rejection);

    auto exhausted = crossover.state();
    exhausted.frames = std::numeric_limits<std::uint64_t>::max();
    CHECK(measured(summary, Interval::OfflineRestore, [&] {
        return crossover.restore_state(exhausted);
    }) == Status::Ok);
    CHECK(measured(summary, Interval::Reject, [&] {
        return crossover.process_frame(0.0, frame);
    }) == Status::TimelineOverflow);
    CHECK(measured(summary, Interval::Reject, [&] {
        return crossover.process(input.first(1), output.first(1));
    }) == Status::TimelineOverflow);
    CHECK(measured(summary, Interval::Empty, [&] { return crossover.process({}, {}); }) == Status::Ok);
    CHECK(measured(summary, Interval::Observe, [&] { return crossover.observe(frame); }) == Status::Ok);
    CHECK(frame.frame == exhausted.frames);
    auto invalid = exhausted;
    invalid.previous_input_volts = std::numeric_limits<double>::infinity();
    CHECK(measured(summary, Interval::OfflineRestore, [&] {
        return crossover.restore_state(invalid);
    }) == Status::InvalidProfile);
    CHECK(crossover.state() == exhausted);
    CHECK(measured(summary, Interval::OfflineRestore, [&] {
        return crossover.restore_state(before_rejection);
    }) == Status::Ok);
    CHECK(measured(summary, Interval::Scalar, [&] {
        return crossover.process_frame(0.0, frame);
    }) == Status::Ok);
    ++summary.scalar_frames;
    calibration(summary);
    ++summary.fixtures;
}

void late_numerical_failure(Summary& summary) {
    // Published author fixture: prove the rejected block reaches a numerical
    // failure on interval3, rather than merely rejecting its initial inputs.
    calibration(summary);
    LeslieCrossover crossover;
    CHECK(measured(summary, Interval::OfflinePrepare, [&] {
        return crossover.prepare(192000.0);
    }) == Status::Ok);
    const LeslieCrossoverState precharge{{60000.0, 0.0}, {}, 0.0, 0};
    CHECK(measured(summary, Interval::OfflineRestore, [&] {
        return crossover.restore_state(precharge);
    }) == Status::Ok);
    std::array<double, 3> zeros{};
    std::array<LeslieCrossoverFrame, 3> destination{sentinel, sentinel, sentinel};
    const auto unchanged = destination;
    CHECK(measured(summary, Interval::Reject, [&] {
        return crossover.process(zeros, destination);
    }) == Status::InvalidBuffer);
    CHECK(destination == unchanged);
    CHECK(crossover.state() == precharge);
    LeslieCrossoverFrame frame = sentinel;
    for (std::size_t index = 0; index < 2; ++index) {
        CHECK(measured(summary, Interval::Scalar, [&] {
            return crossover.process_frame(0.0, frame);
        }) == Status::Ok);
        ++summary.scalar_frames;
    }
    const auto last_success = crossover.state();
    frame = sentinel;
    CHECK(measured(summary, Interval::Reject, [&] {
        return crossover.process_frame(0.0, frame);
    }) == Status::InvalidBuffer);
    CHECK(frame == sentinel);
    CHECK(crossover.state() == last_success);
    calibration(summary);
}

} // namespace

#undef HAMMOND_PROBE_NOINLINE

int main() {
    static_assert(std::is_trivially_copyable_v<hammond::LeslieCrossover>);
    static_assert(std::is_trivially_destructible_v<hammond::LeslieCrossover>);
    Summary summary;
    for (const double rate : std::array<double, 4>{44100.0, 48000.0, 96000.0, 192000.0}) {
        for (const LeslieCrossoverLoads loads : std::array<LeslieCrossoverLoads, 3>{
                 LeslieCrossoverLoads{16.0, 16.0}, {1.0, 1024.0}, {1024.0, 1.0}}) {
            fixture(rate, loads, summary);
        }
    }
    late_numerical_failure(summary);
    CHECK(summary.fixtures == 12);
    CHECK(summary.calibrations == 26);
    CHECK(summary.scalar_frames == 1550);
    CHECK(summary.block_frames == 473952);
    std::cout << "{\"status\":\"passed\",\"observer\":\"current-thread-global-C++-allocation-calls\""
              << ",\"fixtures\":" << summary.fixtures
              << ",\"calibrations\":" << summary.calibrations
              << ",\"positive_control_allocations\":" << summary.calibrations * 12
              << ",\"positive_control_deallocations\":" << summary.calibrations * 12
              << ",\"scalar_frames\":" << summary.scalar_frames
              << ",\"block_frames\":" << summary.block_frames
              << ",\"intervals\":{";
    constexpr std::array<const char*, 9> names{
        "scalar", "block", "empty", "observe", "rejection",
        "offline_prepare", "offline_restore", "offline_rate_change", "offline_response"};
    for (std::size_t index = 0; index < names.size(); ++index) {
        if (index != 0) std::cout << ',';
        const auto& result = summary.intervals[index];
        std::cout << '\"' << names[index] << "\":{\"calls\":" << result.calls
                  << ",\"allocations\":" << result.allocations
                  << ",\"deallocations\":" << result.deallocations << '}';
    }
    std::cout << "}}\n";
    return EXIT_SUCCESS;
}
