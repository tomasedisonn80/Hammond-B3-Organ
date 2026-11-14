#include "TestSupport.h"
#include "hammond/RotaryPropagation.h"

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


namespace {

using namespace hammond::rotary;

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

enum class Interval : std::size_t { Prepare, Query, Copy, Rejection, Count };

struct IntervalTotals {
    std::size_t calls{};
    std::size_t allocations{};
    std::size_t deallocations{};
};

struct Summary {
    std::array<IntervalTotals, static_cast<std::size_t>(Interval::Count)> intervals{};
    std::size_t fixtures{};
    std::size_t calibrations{};
    std::size_t history_queries{};
    std::size_t solved_paths{};
    std::size_t geometry_queries{};
    std::size_t rejected_calls{};
    std::uint32_t maximum_evaluations{};
    double maximum_residual_s{};
};

template<class T>
[[nodiscard]] auto bytes(const T& object) noexcept {
    static_assert(std::is_trivially_copyable_v<T>);
    std::array<std::byte, sizeof(T)> result{};
    std::memcpy(result.data(), &object, sizeof(T));
    return result;
}

// Only the named API or copy operation runs inside an observation. Fixture
// construction, assertions, calibration and reporting remain outside it.
template<class Operation>
[[nodiscard]] Status observe(Summary& summary, Interval interval, Operation operation) {
    allocation_probe::begin();
    const Status status = operation();
    const auto counts = allocation_probe::end();
    auto& total = summary.intervals[static_cast<std::size_t>(interval)];
    ++total.calls;
    total.allocations += counts.allocations;
    total.deallocations += counts.deallocations;
    CHECK(counts.allocations == 0);
    CHECK(counts.deallocations == 0);
    return status;
}

void check_calibration(Summary& summary) {
    CHECK(calibrate().passed());
    ++summary.calibrations;
}

struct HistoryStorage {
    MotionProfile profile{};
    MotionState seed{0.3, 0, 75.0};
    double sample_rate{};
    std::uint64_t through_frame{};
    std::array<MotionSegment, kMaxMotionSegments> segments{};
};
static_assert(std::is_trivially_copyable_v<HistoryStorage>);

// Build directly in stable storage before any view borrows it. Large fixture
// ownership stays outside the call stack and all observed allocation intervals.
// Returning a const owner keeps every borrowed segment immutable and stationary.
[[nodiscard]] std::unique_ptr<const HistoryStorage> make_storage(
    double rate, std::int8_t direction) {
    auto owner = std::make_unique<HistoryStorage>();
    auto& storage = *owner;
    storage.profile = {5.0, 200.0, 0.001, 60.0, direction};
    storage.sample_rate = rate;
    storage.through_frame = kMaxEpochSeconds * static_cast<std::uint64_t>(rate);
    CHECK(make_motion_segment(storage.profile, storage.seed, SpeedCommand::Chorale,
                              0, storage.segments.front()) == Status::Ok);
    for (std::size_t index = 1; index < storage.segments.size(); ++index) {
        const auto anchor = index == kMaxMotionSegments - 1 ? storage.through_frame - 31
                          : index == kMaxMotionSegments - 2 ? storage.through_frame - 1024
                          : 17 * static_cast<std::uint64_t>(index);
        MotionState initial;
        CHECK(evaluate_motion_segment_at(storage.segments[index - 1],
                  {static_cast<std::int64_t>(anchor), 0.0}, rate, initial) == Status::Ok);
        const auto command = index % 2 == 0 ? SpeedCommand::Chorale : SpeedCommand::Tremolo;
        CHECK(make_motion_segment(storage.profile, initial, command, anchor,
                                  storage.segments[index]) == Status::Ok);
    }
    return owner;
}

constexpr Vec3 origin{0.1, -0.2, 0.15};
constexpr double radius_m = 0.375;
constexpr double sound_speed_m_s = 300.0;
constexpr std::array<MicrophoneProfile, 2> microphones{{
    {{2.0, 0.4, 0.3}}, {{-3.0, 0.7, -0.1}}
}};
constexpr std::size_t kObservationCount = 16;
constexpr std::size_t kRepetitions = 32;

[[nodiscard]] auto observations(const HistoryStorage& storage) {
    const auto end = static_cast<std::int64_t>(storage.through_frame);
    const double almost_one = std::nextafter(1.0, 0.0);
    return std::array<SamplePosition, kObservationCount>{{
        {-end + 13000, 0.125}, {-1024, 0.125}, {-1, almost_one}, {0, 0.0},
        {0, std::numeric_limits<double>::denorm_min()}, {16, almost_one},
        {17, 0.0}, {17, 0.25}, {17 * 2048, 0.625}, {17 * 4094, 0.5},
        {end - 1025, almost_one}, {end - 1024, 0.0}, {end - 32, 0.75},
        {end - 31, 0.0}, {end - 1, almost_one}, {end, 0.0}
    }};
}

struct ExpectedObservation {
    MotionState state{};
    std::array<PathResult, microphones.size()> paths{};
    std::array<SamplePosition, microphones.size()> emissions{};
};

struct PreparedCopies {
    MotionHistoryView history{};
    std::array<PreparedRetardedPath, microphones.size()> paths{};
};

void query_history(const MotionHistoryView& history, SamplePosition position,
                   MotionState& state, Summary& summary) {
    CHECK(observe(summary, Interval::Query, [&] {
        return history.state_at(position, state);
    }) == Status::Ok);
    ++summary.history_queries;
}

void solve_path(const PreparedRetardedPath& path, SamplePosition observation,
                PathResult& result, SamplePosition& emission, Summary& summary) {
    CHECK(observe(summary, Interval::Query, [&] {
        return path.solve(observation, result, emission);
    }) == Status::Ok);
    CHECK(std::isfinite(result.delay_s) && result.delay_s > 0.0);
    CHECK(std::isfinite(result.distance_m) && result.distance_m > 0.0);
    CHECK(std::isfinite(result.frequency_ratio) && result.frequency_ratio > 0.0);
    CHECK(std::isfinite(result.residual_s));
    CHECK(std::abs(result.residual_s) <= kMaxSolverResidualSeconds);
    CHECK(result.iterations >= 2 && result.iterations <= kMaxSolverIterations);
    CHECK(emission.fraction >= 0.0 && emission.fraction < 1.0);
    CHECK(emission.frame < observation.frame
          || (emission.frame == observation.frame && emission.fraction < observation.fraction));
    summary.maximum_evaluations = std::max(summary.maximum_evaluations, result.iterations);
    summary.maximum_residual_s = std::max(summary.maximum_residual_s, std::abs(result.residual_s));
    ++summary.solved_paths;
}

// The noinline frame returns before escaped views/paths are exercised. Only
// the caller-owned const storage survives; no expired span is ever queried.
HAMMOND_PROBE_NOINLINE void prepare_escaped_copies(
    const HistoryStorage& storage, const std::array<SamplePosition, kObservationCount>& positions,
    PreparedCopies& escaped, std::array<ExpectedObservation, kObservationCount>& expected,
    Summary& summary) {
    MotionHistoryView original_view;
    CHECK(observe(summary, Interval::Prepare, [&] {
        return original_view.prepare(storage.profile, storage.seed, storage.sample_rate,
                                     storage.segments, storage.through_frame);
    }) == Status::Ok);
    std::array<PreparedRetardedPath, microphones.size()> original_paths{};
    for (std::size_t receiver = 0; receiver < microphones.size(); ++receiver) {
        CHECK(observe(summary, Interval::Prepare, [&] {
            return original_paths[receiver].prepare(original_view, origin, radius_m,
                           microphones[receiver], sound_speed_m_s, 1.0);
        }) == Status::Ok);
        CHECK(original_paths[receiver].bounds().max_tangential_mach == 0.25);
    }
    CHECK(original_paths[0].bounds().max_distance_m < original_paths[1].bounds().min_distance_m);
    for (std::size_t index = 0; index < positions.size(); ++index) {
        query_history(original_view, positions[index], expected[index].state, summary);
        for (std::size_t receiver = 0; receiver < microphones.size(); ++receiver) {
            solve_path(original_paths[receiver], positions[index], expected[index].paths[receiver],
                       expected[index].emissions[receiver], summary);
        }
        CHECK(expected[index].emissions[0] != expected[index].emissions[1]);
    }
    const auto view_before = bytes(original_view);
    const auto paths_before = bytes(original_paths);
    CHECK(observe(summary, Interval::Copy, [&] {
        const MotionHistoryView constructed_view(original_view);
        const auto constructed_paths = original_paths;
        escaped.history = constructed_view;
        escaped.paths = constructed_paths;
        return Status::Ok;
    }) == Status::Ok);
    CHECK(bytes(original_view) == view_before);
    CHECK(bytes(original_paths) == paths_before);
}

template<class Object, class Operation>
void expect_rejection(const Object& object, Status expected, Operation operation, Summary& summary) {
    const auto before = bytes(object);
    CHECK(observe(summary, Interval::Rejection, operation) == expected);
    CHECK(bytes(object) == before);
    ++summary.rejected_calls;
}

void reject_history_query(const MotionHistoryView& history, SamplePosition position,
                          Status expected, Summary& summary) {
    MotionState state{2.25, -1234, 31.0};
    const auto before = bytes(state);
    expect_rejection(history, expected, [&] { return history.state_at(position, state); }, summary);
    CHECK(bytes(state) == before);
}

void reject_path_query(const PreparedRetardedPath& path, SamplePosition observation,
                       Status expected, Summary& summary) {
    PathResult result{9.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2};
    SamplePosition emission{-123, 0.875};
    const auto result_before = bytes(result);
    const auto emission_before = bytes(emission);
    expect_rejection(path, expected, [&] { return path.solve(observation, result, emission); }, summary);
    CHECK(bytes(result) == result_before);
    CHECK(bytes(emission) == emission_before);
}

void check_failures(const HistoryStorage& storage, PreparedCopies& copies, Summary& summary) {
    const auto end = static_cast<std::int64_t>(storage.through_frame);
    const MotionHistoryView unprepared_history;
    const PreparedRetardedPath unprepared_path;
    reject_history_query(unprepared_history, {0, 0.0}, Status::NotPrepared, summary);
    reject_path_query(unprepared_path, {0, 0.0}, Status::NotPrepared, summary);

    const auto reprepare_history = [&](const MotionProfile& profile, double rate,
                                       std::span<const MotionSegment> segments,
                                       std::uint64_t through, Status expected) {
        expect_rejection(copies.history, expected, [&] {
            return copies.history.prepare(profile, storage.seed, rate, segments, through);
        }, summary);
    };
    reprepare_history(storage.profile, 12345.0, storage.segments,
                      storage.through_frame, Status::InvalidSpec);
    reprepare_history(storage.profile, storage.sample_rate, {},
                      storage.through_frame, Status::InvalidSpec);
    // Real preallocated backing objects, including for the rejected oversized
    // span: constructing a span beyond its owner would invalidate this test.
    static const std::array<MotionSegment, kMaxMotionSegments + 1> oversized{};
    reprepare_history(storage.profile, storage.sample_rate, oversized,
                      storage.through_frame, Status::InvalidSpec);
    MotionProfile invalid_profile = storage.profile;
    invalid_profile.direction = 0;
    reprepare_history(invalid_profile, storage.sample_rate, storage.segments,
                      storage.through_frame, Status::InvalidProfile);
    reprepare_history(storage.profile, storage.sample_rate, storage.segments,
                      storage.through_frame + 1, Status::TimelineOverflow);
    reprepare_history(storage.profile, storage.sample_rate, storage.segments,
                      storage.segments.back().anchor_frame - 1, Status::InvalidEvent);
    auto discontinuous = storage.segments.front();
    discontinuous.initial.phase_rad += 0.25;
    reprepare_history(storage.profile, storage.sample_rate, {&discontinuous, 1},
                      storage.through_frame, Status::InvalidProfile);

    for (auto& path : copies.paths) {
        expect_rejection(path, Status::NotPrepared, [&] {
            return path.prepare(unprepared_history, origin, radius_m,
                                microphones.front(), sound_speed_m_s, 1.0);
        }, summary);
        expect_rejection(path, Status::InvalidProfile, [&] {
            return path.prepare(copies.history, origin, 1.0,
                                microphones.front(), sound_speed_m_s, 1.0);
        }, summary);
        const MicrophoneProfile collision{{origin.x + radius_m, origin.y, origin.z}};
        expect_rejection(path, Status::InvalidProfile, [&] {
            return path.prepare(copies.history, origin, radius_m, collision, sound_speed_m_s, 1.0);
        }, summary);
        expect_rejection(path, Status::InvalidProfile, [&] {
            return path.prepare(copies.history, origin, radius_m,
                                microphones.front(), 299.0, 1.0);
        }, summary);
    }
    for (const double fraction : std::array<double, 4>{
             -0.25, 1.0, std::numeric_limits<double>::quiet_NaN(),
             std::numeric_limits<double>::infinity()}) {
        reject_history_query(copies.history, {0, fraction}, Status::InvalidSpec, summary);
        for (const auto& path : copies.paths) {
            reject_path_query(path, {0, fraction}, Status::InvalidSpec, summary);
        }
    }
    for (const SamplePosition invalid : std::array<SamplePosition, 3>{{
             {-end - 1, 0.0}, {end + 1, 0.0}, {end, 0.5}}}) {
        reject_history_query(copies.history, invalid, Status::TimelineOverflow, summary);
        for (const auto& path : copies.paths) {
            reject_path_query(path, invalid, Status::TimelineOverflow, summary);
        }
    }
    for (const auto& path : copies.paths) {
        // Observation is admitted; a bracket emission is outside the epoch.
        // This checks failure after solve entry as well as initial validation.
        reject_path_query(path, {-end, 0.0}, Status::TimelineOverflow, summary);
    }

    MotionHistoryView short_history;
    const auto through = storage.segments[kMaxMotionSegments - 3].anchor_frame + 1;
    const auto prefix = std::span<const MotionSegment>(storage.segments).first(kMaxMotionSegments - 2);
    CHECK(observe(summary, Interval::Prepare, [&] {
        return short_history.prepare(storage.profile, storage.seed, storage.sample_rate, prefix, through);
    }) == Status::Ok);
    PreparedRetardedPath short_path;
    CHECK(observe(summary, Interval::Prepare, [&] {
        return short_path.prepare(short_history, origin, radius_m,
                                  microphones.front(), sound_speed_m_s, 1.0);
    }) == Status::Ok);
    const SamplePosition uncovered{static_cast<std::int64_t>(through), 0.125};
    reject_history_query(short_history, uncovered, Status::InsufficientHistory, summary);
    reject_path_query(short_path, uncovered, Status::InsufficientHistory, summary);

    Vec3 aliased{9.0, 8.0, 7.0};
    const auto before = bytes(aliased);
    CHECK(observe(summary, Interval::Rejection, [&] {
        return evaluate_circular_source(origin, radius_m, storage.seed,
                                        storage.profile.direction, aliased, aliased);
    }) == Status::InvalidBuffer);
    CHECK(bytes(aliased) == before);
    ++summary.rejected_calls;
}

void check_fixture(double rate, std::int8_t direction, Summary& summary) {
    const auto storage_owner = make_storage(rate, direction);
    const auto& storage = *storage_owner;
    // Snapshot the complete object without another large stack temporary.
    // Both fixture allocations and their destruction occur outside observe().
    const auto storage_before = std::make_unique<std::byte[]>(sizeof(storage));
    std::memcpy(storage_before.get(), &storage, sizeof(storage));
    const auto positions = observations(storage);
    std::array<ExpectedObservation, kObservationCount> expected{};
    PreparedCopies copies;
    check_calibration(summary);
    prepare_escaped_copies(storage, positions, copies, expected, summary);
    // original_view, original_paths and intermediate copies have all left
    // their separate stack frame; storage still owns every borrowed segment.
    const auto copied_before = bytes(copies);
    check_failures(storage, copies, summary);

    for (std::size_t repetition = 0; repetition < kRepetitions; ++repetition) {
        for (std::size_t index = 0; index < positions.size(); ++index) {
            MotionState state;
            query_history(copies.history, positions[index], state, summary);
            CHECK(state == expected[index].state);
            for (std::size_t receiver = 0; receiver < copies.paths.size(); ++receiver) {
                PathResult result;
                SamplePosition emission;
                solve_path(copies.paths[receiver], positions[index], result, emission, summary);
                CHECK(result == expected[index].paths[receiver]);
                CHECK(emission == expected[index].emissions[receiver]);
            }
            Vec3 position;
            Vec3 velocity;
            CHECK(observe(summary, Interval::Query, [&] {
                return evaluate_circular_source(origin, radius_m, state, direction, position, velocity);
            }) == Status::Ok);
            CHECK(std::isfinite(position.x) && std::isfinite(position.y));
            CHECK(std::isfinite(velocity.x) && std::isfinite(velocity.y));
            CHECK(position.z == origin.z && velocity.z == 0.0);
            ++summary.geometry_queries;
        }
        reject_history_query(copies.history, {0, -0.25}, Status::InvalidSpec, summary);
        reject_path_query(copies.paths[repetition % copies.paths.size()],
                          {static_cast<std::int64_t>(storage.through_frame), 0.5},
                          Status::TimelineOverflow, summary);
    }
    // Exercise every occupied binary-search position at maximum capacity,
    // including both sides of the densely spaced command transitions.
    for (std::size_t index = 0; index < storage.segments.size(); ++index) {
        const auto& segment = storage.segments[index];
        const auto anchor = static_cast<std::int64_t>(segment.anchor_frame);
        MotionState state;
        query_history(copies.history, {anchor, 0.0}, state, summary);
        CHECK(state == segment.initial);
        const SamplePosition immediately_before{anchor - 1, std::nextafter(1.0, 0.0)};
        MotionState reference;
        if (index == 0) {
            CHECK(evaluate_motion_prehistory_at(storage.seed, direction, immediately_before,
                                                rate, reference) == Status::Ok);
        } else {
            CHECK(evaluate_motion_segment_at(storage.segments[index - 1], immediately_before,
                                             rate, reference) == Status::Ok);
        }
        query_history(copies.history, immediately_before, state, summary);
        CHECK(state == reference);
    }
    CHECK(bytes(copies) == copied_before);
    CHECK(std::memcmp(&storage, storage_before.get(), sizeof(storage)) == 0);
    check_calibration(summary);
    ++summary.fixtures;
}

} // namespace

#undef HAMMOND_PROBE_NOINLINE

int main() {
    static_assert(kMaxMotionSegments == 4097);
    static_assert(kMaxSolverIterations == 48);
    static_assert(std::is_nothrow_copy_constructible_v<MotionHistoryView>);
    static_assert(std::is_nothrow_copy_assignable_v<MotionHistoryView>);
    static_assert(std::is_nothrow_copy_constructible_v<PreparedRetardedPath>);
    static_assert(std::is_nothrow_copy_assignable_v<PreparedRetardedPath>);
    Summary summary;
    for (const double rate : std::array<double, 4>{44100.0, 48000.0, 96000.0, 192000.0}) {
        for (const std::int8_t direction : std::array<std::int8_t, 2>{-1, 1}) {
            check_fixture(rate, direction, summary);
        }
    }
    CHECK(summary.fixtures == 8);
    CHECK(summary.calibrations == 16);
    CHECK(summary.history_queries == 8 * (2 * kMaxMotionSegments + 33 * kObservationCount));
    CHECK(summary.solved_paths == 8 * 33 * kObservationCount * microphones.size());
    CHECK(summary.geometry_queries == 8 * kRepetitions * kObservationCount);
    std::cout << std::setprecision(std::numeric_limits<double>::max_digits10)
              << "{\"status\":\"passed\",\"fixtures\":" << summary.fixtures
              << ",\"segments_per_fixture\":" << kMaxMotionSegments
              << ",\"repetitions\":" << kRepetitions
              << ",\"calibrations\":" << summary.calibrations
              << ",\"calibration_allocations\":" << 12 * summary.calibrations
              << ",\"calibration_deallocations\":" << 12 * summary.calibrations
              << ",\"history_queries\":" << summary.history_queries
              << ",\"solved_paths\":" << summary.solved_paths
              << ",\"geometry_queries\":" << summary.geometry_queries
              << ",\"rejected_calls\":" << summary.rejected_calls
              << ",\"maximum_evaluations\":" << summary.maximum_evaluations
              << ",\"maximum_residual_s\":" << summary.maximum_residual_s
              << ",\"intervals\":{";
    constexpr std::array<const char*, 4> names{"prepare", "query", "copy", "rejection"};
    for (std::size_t index = 0; index < names.size(); ++index) {
        const auto& total = summary.intervals[index];
        if (index != 0) std::cout << ',';
        std::cout << '"' << names[index] << "\":{\"calls\":" << total.calls
                  << ",\"allocations\":" << total.allocations
                  << ",\"deallocations\":" << total.deallocations << '}';
    }
    std::cout << "}}\n";
    return EXIT_SUCCESS;
}
