#include "TestSupport.h"
#include "hammond/PedalRouting.h"

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
#include <chrono>

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
    std::size_t observations{};
    std::size_t accepted{};
    std::size_t rejected{};
    std::size_t rendered_frames{};
    std::size_t accepted_edits{};
    double checksum{};
};

// Construct every argument, expected value and fixture before this boundary.
// Assertions and diagnostics execute after recording ends, even on failure.
template <typename Operation>
[[nodiscard]] auto observe(const char* label, Operation operation, Summary& summary) {
    CHECK(!allocation_probe::recording);
    allocation_probe::begin();
    const auto result = operation();
    const auto counts = allocation_probe::end();
    if (counts.allocations != 0 || counts.deallocations != 0) {
        std::fprintf(stderr, "%s: observed %zu C++ allocations and %zu deallocations\n",
                     label, counts.allocations, counts.deallocations);
        std::exit(EXIT_FAILURE);
    }
    ++summary.observations;
    return result;
}

template <typename Operation>
void observe_status(const char* label, Operation operation, Status expected, Summary& summary) {
    const auto result = observe(label, operation, summary);
    CHECK(result == expected);
    if (result == Status::Ok) ++summary.accepted;
    else ++summary.rejected;
}

using ContactEdits = std::array<PedalContactEdit, kPedalContactPositionCount>;

[[nodiscard]] ContactEdits all_contacts(bool closed) {
    ContactEdits result{};
    for (std::size_t index = 0; index < result.size(); ++index) {
        result[index] = {PedalId{static_cast<std::uint8_t>(index / kPedalContactCount + 1)},
                         static_cast<std::uint8_t>(index % kPedalContactCount), closed};
    }
    return result;
}

[[nodiscard]] double sum_buses(const PedalBusFrame& buses) noexcept {
    double result = 0.0;
    for (const double value : buses) result += value;
    return result;
}

void test_runtime(Summary& summary) {
    // These are the first observed accesses to the compiled table/identity in
    // this process. Their views must not hide a first-call dynamic allocation.
    const auto* routes = observe("first compiled table access",
        [] { return &compiled_pedal_routes(); }, summary);
    const auto identity = observe("first compiled identity access",
        [] { return compiled_pedal_identity(); }, summary);
    CHECK(routes->size() == 200 && identity.model_id == kPedalBusReferenceModelId);
    CHECK(identity.map_id == "atlas-derived-b3-c3-pedal-v1");

    PedalWeights weights{};
    weights.fill(1.0); // Explicit dimensionless test fixture, never physical gain.
    PedalSourceFrame positive{};
    positive.fill(1.0);
    PedalSourceFrame negative{};
    negative.fill(-0.5);
    auto invalid_sources = positive;
    invalid_sources.back() = std::numeric_limits<double>::quiet_NaN();
    const PedalBusFrame sentinel{1234.5, -678.0, 91.25, -42.5};
    PedalBusFrame buses = sentinel;
    const auto close = all_contacts(true);
    const auto open = all_contacts(false);
    auto invalid_edits = open;
    invalid_edits.back().pedal = PedalId{0};
    std::array<PedalContactEdit, kPedalContactPositionCount + 1> oversized{};
    oversized.fill({PedalId{1}, 0, true});
    auto invalid_routes = *routes;
    invalid_routes.back().tone = ToneId{92};
    auto invalid_weights = weights;
    invalid_weights.back() = std::numeric_limits<double>::infinity();

    PedalBusKernel kernel;
    const auto unprepared = kernel;
    observe_status("unprepared contact request", [&] { return kernel.apply_contacts(close); },
                   Status::NotPrepared, summary);
    observe_status("unprepared render", [&] { return kernel.render_frame(positive, buses); },
                   Status::NotPrepared, summary);
    CHECK(kernel == unprepared && buses == sentinel);
    bool closed = true;
    CHECK(!observe("unprepared checked query",
        [&] { return kernel.contact_closed(PedalId{1}, 0, closed); }, summary));
    CHECK(closed);
    CHECK(!observe("unprepared flag", [&] { return kernel.prepared(); }, summary));

    // First prepare is measured, not warmed by an unobserved successful call.
    observe_status("first preparation", [&] { return kernel.prepare(*routes, weights); },
                   Status::Ok, summary);
    CHECK(observe("prepared flag", [&] { return kernel.prepared(); }, summary));
    CHECK(observe("open contact count", [&] { return kernel.closed_contact_count(); }, summary) == 0);
    const auto all_open = observe("open contact snapshot",
        [&] { return kernel.contacts_snapshot(); }, summary);
    CHECK(std::none_of(all_open.begin(), all_open.end(), [](bool value) { return value; }));
    observe_status("open contact render", [&] { return kernel.render_frame(positive, buses); },
                   Status::Ok, summary);
    ++summary.rendered_frames;
    CHECK(buses == PedalBusFrame{});
    const auto before_empty = kernel;
    observe_status("empty contact batch", [&] { return kernel.apply_contacts({}); },
                   Status::Ok, summary);
    CHECK(kernel == before_empty);

    observe_status("maximum occupancy close", [&] { return kernel.apply_contacts(close); },
                   Status::Ok, summary);
    summary.accepted_edits += close.size();
    const auto all_closed = kernel;
    observe_status("repeat maximum occupancy", [&] { return kernel.apply_contacts(close); },
                   Status::Ok, summary);
    summary.accepted_edits += close.size();
    CHECK(kernel == all_closed);
    CHECK(observe("full contact count", [&] { return kernel.closed_contact_count(); }, summary) == 200);
    const auto snapshot = observe("full contact snapshot",
        [&] { return kernel.contacts_snapshot(); }, summary);
    CHECK(std::all_of(snapshot.begin(), snapshot.end(), [](bool value) { return value; }));
    const bool every_contact_closed = observe("all 200 checked contact queries", [&] {
        bool result = true;
        for (const auto& edit : close) {
            bool value = false;
            const bool found = kernel.contact_closed(edit.pedal, edit.contact, value);
            result = result && found && value;
        }
        return result;
    }, summary);
    CHECK(every_contact_closed); // Includes the five inaudible contact positions.
    closed = true;
    CHECK(!observe("invalid checked query",
        [&] { return kernel.contact_closed(PedalId{26}, 0, closed); }, summary));
    CHECK(closed);

    observe_status("occupied documentary maximum", [&] { return kernel.render_frame(positive, buses); },
                   Status::Ok, summary);
    ++summary.rendered_frames;
    CHECK((buses == PedalBusFrame{45.0, 50.0, 50.0, 50.0}));
    CHECK(sum_buses(buses) == 195.0);
    observe_status("invalid final source sample", [&] { return kernel.render_frame(invalid_sources, buses); },
                   Status::InvalidBuffer, summary);
    CHECK((buses == PedalBusFrame{45.0, 50.0, 50.0, 50.0}));
    CHECK(kernel == all_closed);

    observe_status("invalid final contact edit", [&] { return kernel.apply_contacts(invalid_edits); },
                   Status::InvalidEvent, summary);
    CHECK(kernel == all_closed);
    observe_status("201 contact edits", [&] { return kernel.apply_contacts(oversized); },
                   Status::TooManyEvents, summary);
    CHECK(kernel == all_closed);
    observe_status("invalid final route", [&] { return kernel.prepare(invalid_routes, weights); },
                   Status::InvalidProfile, summary);
    CHECK(kernel == all_closed);
    observe_status("invalid final weight", [&] { return kernel.prepare(*routes, invalid_weights); },
                   Status::InvalidProfile, summary);
    CHECK(kernel == all_closed);
    observe_status("199 routes", [&] {
        return kernel.prepare(std::span<const PedalRoute>(*routes).first(199), weights);
    }, Status::InvalidProfile, summary);
    CHECK(kernel == all_closed);

    // Maximum occupancy stays enabled for every call. Alternating exactly
    // representable source frames force nonzero result consumption. Both
    // positive and negative branch products are executed, not just silence.
    constexpr std::size_t frames = 4096;
    const auto begin = std::chrono::steady_clock::now();
    for (std::size_t frame = 0; frame < frames; ++frame) {
        const auto& sources = frame % 2 == 0 ? positive : negative;
        observe_status("full occupancy frame", [&] { return kernel.render_frame(sources, buses); },
                       Status::Ok, summary);
        ++summary.rendered_frames;
        const double sum = sum_buses(buses);
        CHECK(sum == (frame % 2 == 0 ? 195.0 : -97.5));
        summary.checksum += sum;
    }
    const auto end = std::chrono::steady_clock::now();
    CHECK(summary.checksum == static_cast<double>(frames / 2) * 97.5);
    CHECK(summary.checksum > 0.0 && kernel == all_closed);
    const double seconds = std::chrono::duration<double>(end - begin).count();
    // Observation only: includes probe/assert overhead; never a pass threshold.
    std::printf("Pedal maximum-occupancy observation: %zu frames, checksum %.17g, "
                "elapsed %.9f seconds (not a device deadline claim).\n",
                frames, summary.checksum, seconds);

    ContactEdits repeated{};
    for (std::size_t index = 0; index < repeated.size(); ++index) {
        repeated[index] = {PedalId{1}, 0, index % 2 == 0};
    }
    observe_status("200 ordered edits of one position", [&] { return kernel.apply_contacts(repeated); },
                   Status::Ok, summary);
    summary.accepted_edits += repeated.size();
    CHECK(kernel.closed_contact_count() == 199);
    observe_status("partially open render", [&] { return kernel.render_frame(positive, buses); },
                   Status::Ok, summary);
    ++summary.rendered_frames;
    CHECK((buses == PedalBusFrame{44.0, 50.0, 50.0, 50.0}));
    observe_status("maximum occupancy open", [&] { return kernel.apply_contacts(open); },
                   Status::Ok, summary);
    summary.accepted_edits += open.size();
    CHECK(kernel.closed_contact_count() == 0);
    observe_status("released silence", [&] { return kernel.render_frame(positive, buses); },
                   Status::Ok, summary);
    ++summary.rendered_frames;
    CHECK(buses == PedalBusFrame{});

    // Structural ceiling fixture: connected at all 200 positions. This is
    // deliberately not the corroborated factory map or physical pedal voicing.
    auto all_connected = *routes;
    for (auto& route : all_connected) route.tone = ToneId{1};
    observe_status("all-connected reference preparation",
        [&] { return kernel.prepare(all_connected, weights); }, Status::Ok, summary);
    observe_status("all-connected reference close", [&] { return kernel.apply_contacts(close); },
                   Status::Ok, summary);
    summary.accepted_edits += close.size();
    observe_status("50-term bus ceiling", [&] { return kernel.render_frame(positive, buses); },
                   Status::Ok, summary);
    ++summary.rendered_frames;
    CHECK((buses == PedalBusFrame{50.0, 50.0, 50.0, 50.0}));
    CHECK(kernel.closed_contact_count() == 200);
    observe_status("successful reprepare opens contacts",
        [&] { return kernel.prepare(*routes, weights); }, Status::Ok, summary);
    CHECK(kernel.closed_contact_count() == 0);
    observe_status("reprepared silence", [&] { return kernel.render_frame(positive, buses); },
                   Status::Ok, summary);
    ++summary.rendered_frames;
    CHECK(buses == PedalBusFrame{});
}

} // namespace

int main() {
    test_probe_overloads();
    Summary summary;
    test_runtime(summary);
    CHECK(!allocation_probe::recording);
    CHECK(summary.rendered_frames == 4102 && summary.accepted_edits == 1000);
    std::printf("Pedal allocation observations: %zu measured regions, %zu accepted "
                "and %zu rejected status calls; %zu rendered frames, %zu accepted "
                "contact edits; zero observed C++ allocations/deallocations.\n",
                summary.observations, summary.accepted, summary.rejected,
                summary.rendered_frames, summary.accepted_edits);
    std::printf("Observed fixed storage: kernel=%zu bytes, source frame=%zu, "
                "bus frame=%zu, 200-edit batch=%zu; architecture-specific sizes.\n",
                sizeof(PedalBusKernel), sizeof(PedalSourceFrame), sizeof(PedalBusFrame),
                sizeof(ContactEdits));
    return 0;
}
