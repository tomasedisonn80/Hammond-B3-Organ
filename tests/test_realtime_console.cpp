#include "TestSupport.h"
#include "hammond/Engine.h"
#include "hammond/InputProcessor.h"
#include "hammond/ParameterBridge.h"

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

// Fixture creation, snapshots, output filling and assertions are deliberately
// outside each observed region. The lambda contains exactly one public API call.
struct Totals {
    std::size_t accepted{};
    std::size_t rejected{};
    std::uint64_t frames{};
    std::uint64_t input_events{};
    std::uint64_t physical_events{};
};

struct Summary {
    Totals engine{};
    Totals translation{};
    Totals owned{};
    Totals parameters{};
    Totals lifecycle{};
};

template <typename Function>
[[nodiscard]] auto observe(const char* label, Function function) {
    CHECK(!allocation_probe::recording);
    allocation_probe::begin();
    const auto result = function();
    const auto counts = allocation_probe::end();
    if (counts.allocations != 0 || counts.deallocations != 0) {
        std::fprintf(stderr, "%s: %zu C++ allocations, %zu C++ deallocations\n",
                     label, counts.allocations, counts.deallocations);
        hammond_test::fail("zero observed C++ heap calls", __FILE__, __LINE__);
    }
    return result;
}

void count_result(Totals& totals, Status actual, Status expected) {
    CHECK(actual == expected);
    if (actual == Status::Ok) ++totals.accepted;
    else ++totals.rejected;
}

struct State {
    bool prepared{};
    double rate{};
    std::uint64_t clock{};
    ControlSnapshot controls{};
    std::array<std::array<bool, kManualKeyCount>, kManualCount> keys{};
    std::array<std::array<ContactKeySnapshot, kManualKeyCount>, kManualCount> contacts{};
    std::array<double, kToneSourceCount> phases{};
    PercussionRoutingDiagnostics percussion{};
    bool operator==(const State&) const noexcept = default;
};

[[nodiscard]] State state_of(const Engine& engine) {
    State result;
    result.prepared = engine.prepared();
    result.rate = engine.sample_rate();
    result.clock = engine.frame_clock();
    result.controls = engine.controls_snapshot();
    result.percussion = engine.percussion_diagnostics();
    if (!result.prepared) return result;
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        for (std::size_t key = 0; key < kManualKeyCount; ++key) {
            const auto midi = static_cast<std::uint32_t>(key) + kMinManualMidiNote;
            result.keys[manual][key] = engine.key_down(static_cast<Manual>(manual), midi);
            CHECK(engine.contact_snapshot(static_cast<Manual>(manual), midi,
                                          result.contacts[manual][key]));
        }
    }
    for (std::size_t tone = 0; tone < kToneSourceCount; ++tone) {
        CHECK(engine.source_phase_turns(static_cast<ToneId>(tone + 1), result.phases[tone]));
    }
    return result;
}

void check_output(std::span<const float> output, std::uint32_t written) {
    for (std::size_t i = 0; i < output.size(); ++i) {
        if (i < written) CHECK(std::isfinite(output[i]) && output[i] != sentinel);
        else CHECK(output[i] == sentinel);
    }
}

void process(Engine& engine, std::uint32_t frames, std::span<float> output,
             std::span<const Event> events, Status expected, Summary& summary) {
    const auto before = state_of(engine);
    std::fill(output.begin(), output.end(), sentinel);
    const auto result = observe("Engine::process", [&]() noexcept {
        return engine.process(frames, output, events);
    });
    count_result(summary.engine, result.status, expected);
    CHECK(result.events_consumed == (expected == Status::Ok ? events.size() : 0));
    check_output(output, expected == Status::Ok ? frames : 0);
    if (expected == Status::Ok) {
        CHECK(engine.frame_clock() == before.clock + frames);
        summary.engine.frames += frames;
        summary.engine.input_events += events.size();
        if (frames == 0) {
            const auto after = state_of(engine);
            CHECK(after.phases == before.phases);
            CHECK(after.percussion.readiness == before.percussion.readiness);
        }
    } else {
        CHECK(state_of(engine) == before);
    }
}

void owned_process(Engine& engine, NoteOwnership& owners, std::uint32_t frames,
                   std::span<float> output, std::span<const HostNoteEvent> events,
                   Status expected, std::uint32_t expected_physical, Summary& summary) {
    const auto before = state_of(engine);
    const auto previous_owners = owners;
    std::fill(output.begin(), output.end(), sentinel);
    const auto result = observe("process_owned_notes", [&]() noexcept {
        return process_owned_notes(engine, owners, frames, output, events);
    });
    count_result(summary.owned, result.status, expected);
    CHECK(result.host_events_consumed == (expected == Status::Ok ? events.size() : 0));
    CHECK(result.physical_events_consumed == expected_physical);
    check_output(output, expected == Status::Ok ? frames : 0);
    if (expected == Status::Ok) {
        CHECK(engine.frame_clock() == before.clock + frames);
        summary.owned.frames += frames;
        summary.owned.input_events += events.size();
        summary.owned.physical_events += result.physical_events_consumed;
        if (frames == 0) {
            const auto after = state_of(engine);
            CHECK(after.phases == before.phases);
            CHECK(after.percussion.readiness == before.percussion.readiness);
        }
    } else {
        CHECK(state_of(engine) == before);
        CHECK(owners == previous_owners);
    }
}

constexpr std::size_t key_count = kManualCount * kManualKeyCount;
// Preserve the original manual workload's 45 control events and ordering. The
// current-registry probe below independently covers the two appended selectors;
// their musical realtime paths also have test_preset_realtime coverage.
constexpr std::size_t legacy_control_count = 45;
static_assert(kParameterCount == legacy_control_count + 2,
              "Review the retained workload when the append-only registry changes");
struct Fixtures {
    std::array<Event, legacy_control_count> controls{};
    std::array<Event, key_count> full{};
    std::array<Event, key_count> partial{};
    std::array<Event, key_count> release{};
    std::array<Event, legacy_control_count + key_count> first{};
    std::array<Event, kMaxEventsPerBlock> dense{};
    std::array<Event, kMaxEventsPerBlock> flush{};
    std::array<Event, kMaxEventsPerBlock> invalid_tail{};
    std::array<Event, kMaxEventsPerBlock + 1> too_many{};
    std::array<HostNoteEvent, key_count> host_keys{};
    std::array<HostNoteEvent, kMaxEventsPerBlock> host_dense{};
    std::array<HostNoteEvent, kMaxEventsPerBlock + 1> host_too_many{};
    std::array<HostNoteEvent, kHostInputBusCount * kHostInputChannelCount> channel_release{};
};

[[nodiscard]] Fixtures make_fixtures() {
    Fixtures result;
    std::size_t count = 0;
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        for (std::size_t bar = 0; bar < kDrawbarBankCount * kDrawbarCount; ++bar) {
            result.controls[count++] = {0, EventType::BankDrawbar, static_cast<Manual>(manual),
                                       static_cast<std::uint8_t>(bar), 8.0};
        }
        result.controls[count++] = {0, EventType::SelectBank, static_cast<Manual>(manual), 0, 1.0};
        for (std::size_t key = 0; key < kManualKeyCount; ++key) {
            const auto slot = manual * kManualKeyCount + key;
            const auto note = static_cast<std::uint8_t>(key + kMinManualMidiNote);
            result.full[slot] = {0, EventType::NoteOn, static_cast<Manual>(manual), note, 100.0};
            result.partial[slot] = {0, EventType::KeyPosition, static_cast<Manual>(manual), note, 0.5};
            result.release[slot] = {0, EventType::NoteOff, static_cast<Manual>(manual), note, 0.0};
            result.host_keys[slot] = {0, HostNoteKind::On, static_cast<std::uint8_t>(manual),
                                    0, note, 100, static_cast<std::int32_t>(key)};
        }
    }
    result.controls[count++] = {0, EventType::Expression, Manual::Upper, 0, 1.0};
    for (std::uint8_t field = 0; field < 4; ++field) {
        result.controls[count++] = {0, EventType::Percussion, Manual::Upper, field,
                                   field == 0 || field == 3 ? 1.0 : 0.0};
    }
    // Keep this retained manual workload muted on the appended pedal controls.
    // Enabled pedal ownership/audio receives its own independent allocation gate.
    for (std::uint8_t mixture = 0; mixture < 2; ++mixture) {
        result.controls[count++] = {0, EventType::PedalDrawbar, Manual::Lower, mixture, 0.0};
    }
    CHECK(count == result.controls.size());
    std::copy(result.controls.begin(), result.controls.end(), result.first.begin());
    std::copy(result.partial.begin(), result.partial.end(),
              result.first.begin() + static_cast<std::ptrdiff_t>(count));
    for (std::size_t i = 0; i < kMaxEventsPerBlock; ++i) {
        const auto offset = static_cast<std::uint32_t>(i);
        const auto manual = static_cast<Manual>((i / 8) % 2);
        const auto note = static_cast<std::uint8_t>(36 + (i / 8) % 61);
        Event event{offset, EventType::KeyPosition, manual, note, (i / 8) % 2 == 0 ? 0.4 : 1.0};
        switch (i % 8) {
        case 0: break;
        case 1: event = {offset, EventType::Percussion, Manual::Upper,
                         static_cast<std::uint8_t>((i / 8) % 4),
                         static_cast<double>((i / 32) % 2)}; break;
        case 2: event = {offset, EventType::BankDrawbar, manual,
                         static_cast<std::uint8_t>((i / 8) % 18),
                         (i / 8) % 2 == 0 ? 7.0 : 8.0}; break;
        case 3: event = {offset, EventType::SelectBank, manual, 0,
                         static_cast<double>((i / 8) % 2)}; break;
        case 4: event = {offset, EventType::Cancel, manual, 0, 0.0}; break;
        case 5: event = {offset, EventType::Expression, manual, 0, 0.75}; break;
        case 6: event = {offset, EventType::NoteOn, manual, note, 100.0}; break;
        case 7: event = {offset, EventType::NoteOff, manual, note, 0.0}; break;
        }
        result.dense[i] = event;
        event.offset = 0;
        result.flush[i] = event;
        result.host_dense[i] = {offset, i % 2 == 0 ? HostNoteKind::On : HostNoteKind::Off,
            0, 0, 60, static_cast<std::uint8_t>(i % 2 == 0 ? 100 : 0),
            static_cast<std::int32_t>(1000 + i / 2)};
    }
    result.invalid_tail = result.dense;
    result.invalid_tail.back() = {dense_frames - 1, EventType::KeyPosition, Manual::Upper,
                                 60, std::numeric_limits<double>::quiet_NaN()};
    result.too_many.fill({0, EventType::KeyPosition, Manual::Upper, 60, 0.5});
    result.host_too_many.fill({0, HostNoteKind::Off, 0, 0, 60, 0, -1});
    for (std::size_t i = 0; i < result.channel_release.size(); ++i) {
        result.channel_release[i] = {0, HostNoteKind::AllNotesOff,
            static_cast<std::uint8_t>(i / kHostInputChannelCount),
            static_cast<std::uint8_t>(i % kHostInputChannelCount), 0, 0, -1};
    }
    return result;
}

[[nodiscard]] std::array<Event, kParameterCount> test_parameters(Summary& summary) {
    const auto descriptors = observe("parameter_descriptors", []() noexcept {
        return parameter_descriptors();
    });
    CHECK(descriptors.size() == kParameterCount);
    ++summary.parameters.accepted;
    std::array<Event, kParameterCount> events{};
    for (std::size_t i = 0; i < descriptors.size(); ++i) {
        ParameterDescriptor copied{};
        CHECK(observe("parameter_descriptor", [&]() noexcept {
            return parameter_descriptor(descriptors[i].id, copied);
        }));
        CHECK(copied == descriptors[i]);
        ++summary.parameters.accepted;
        CHECK(observe("normalized_to_event", [&]() noexcept {
            return normalized_to_event(descriptors[i].id, 0.5, 0, events[i]);
        }));
        CHECK(events[i].type == copied.event_type && events[i].manual == copied.manual &&
              events[i].index == copied.index);
        ++summary.parameters.accepted;
        double normalized = -5.0;
        CHECK(observe("plain_to_normalized", [&]() noexcept {
            return plain_to_normalized(descriptors[i].id, events[i].value, normalized);
        }));
        CHECK(normalized >= 0.0 && normalized <= 1.0);
        ++summary.parameters.accepted;
    }
    Event destination{17, EventType::Cancel, Manual::Lower, 0, 0.0};
    for (const double value : {-0.1, 1.1, std::numeric_limits<double>::infinity(),
                               std::numeric_limits<double>::quiet_NaN()}) {
        CHECK(!observe("rejected normalized value", [&]() noexcept {
            return normalized_to_event(12288, value, 0, destination);
        }));
        CHECK(destination.offset == 17 && destination.type == EventType::Cancel &&
              destination.manual == Manual::Lower && destination.index == 0 && destination.value == 0.0);
        ++summary.parameters.rejected;
    }
    CHECK(!observe("unknown parameter ID", [&]() noexcept {
        return normalized_to_event(0, 0.5, 0, destination);
    }));
    ++summary.parameters.rejected;
    double normalized = -5.0;
    CHECK(!observe("rejected discrete plain value", [&]() noexcept {
        return plain_to_normalized(4096, 0.5, normalized);
    }));
    CHECK(normalized == -5.0);
    ++summary.parameters.rejected;
    ParameterDescriptor descriptor = descriptors.front();
    CHECK(!observe("unknown descriptor", [&]() noexcept {
        return parameter_descriptor(0, descriptor);
    }));
    CHECK(descriptor == descriptors.front());
    ++summary.parameters.rejected;
    return events;
}

void test_engine(const RuntimeProfile& profile, const Fixtures& fixtures,
                 const std::array<Event, kParameterCount>& mapped, double rate, Summary& summary) {
    Engine engine;
    CHECK(engine.prepare(profile, {rate, kHardMaxBlockFrames, 43, 137},
                         make_nominal_console_model()) == Status::Ok);
    std::vector<float> output(kHardMaxBlockFrames + 3, sentinel);
    process(engine, 1, output, fixtures.first, Status::Ok, summary);
    CHECK(engine.active_key_count() == key_count);
    ContactKeySnapshot key;
    CHECK(engine.contact_snapshot(Manual::Upper, 60, key));
    CHECK(key.position > 0.0 && key.position < 0.5 && key.target == 0.5);
    const auto settle = static_cast<std::uint32_t>(std::ceil(rate * 0.01));
    process(engine, settle, output, {}, Status::Ok, summary);
    CHECK(engine.contact_snapshot(Manual::Upper, 60, key));
    CHECK(key.position == 0.5 && key.closed[3] && !key.closed[4] && !key.closed[8]);
    CHECK(engine.percussion_diagnostics().eligible &&
          engine.percussion_diagnostics().readiness == 1.0);
    process(engine, dense_frames, output, fixtures.full, Status::Ok, summary);
    CHECK(engine.percussion_diagnostics().routed_detector &&
          engine.percussion_diagnostics().readiness < 1.0);
    process(engine, kHardMaxBlockFrames, output, {}, Status::Ok, summary);

    const std::array cancel{Event{0, EventType::Cancel, Manual::Upper, 0, 0.0}};
    const std::array reselect{Event{0, EventType::SelectBank, Manual::Upper, 0, 1.0}};
    process(engine, 0, output, cancel, Status::Ok, summary);
    CHECK(engine.percussion_diagnostics().physical_detector &&
          !engine.percussion_diagnostics().routed_detector);
    const auto before_recovery = engine.percussion_diagnostics().readiness;
    process(engine, 64, output, {}, Status::Ok, summary);
    CHECK(engine.percussion_diagnostics().readiness > before_recovery);
    process(engine, 64, output, reselect, Status::Ok, summary);
    CHECK(engine.percussion_diagnostics().routed_detector);
    process(engine, 32, output, fixtures.partial, Status::Ok, summary);
    CHECK(engine.contact_snapshot(Manual::Upper, 60, key));
    CHECK(key.position > 0.5 && key.position < 1.0);
    process(engine, 32, output, fixtures.full, Status::Ok, summary);
    process(engine, 0, {}, mapped, Status::Ok, summary);
    process(engine, dense_frames, output, fixtures.dense, Status::Ok, summary);
    process(engine, 0, output, fixtures.flush, Status::Ok, summary);
    process(engine, 0, {}, {}, Status::Ok, summary);

    auto disconnected = engine;
    process(engine, dense_frames, output, fixtures.dense, Status::Ok, summary);
    process(disconnected, dense_frames, {}, fixtures.dense, Status::Ok, summary);
    CHECK(state_of(engine) == state_of(disconnected));
    process(engine, 0, {}, fixtures.controls, Status::Ok, summary);
    process(engine, dense_frames, output, fixtures.full, Status::Ok, summary);
    const auto decayed = engine.percussion_diagnostics().readiness;
    process(engine, static_cast<std::uint32_t>(std::ceil(rate * 0.02)), output,
            fixtures.release, Status::Ok, summary);
    CHECK(!engine.percussion_diagnostics().physical_detector);
    CHECK(engine.percussion_diagnostics().readiness > decayed);
    const std::array panic{Event{0, EventType::AllNotesOff, Manual::Upper, 0, 0.0},
                           Event{0, EventType::AllNotesOff, Manual::Lower, 0, 0.0}};
    process(engine, 0, output, panic, Status::Ok, summary);
    process(engine, 1, output, {}, Status::Ok, summary);
    CHECK(output[0] == 0.0F);

    process(engine, kHardMaxBlockFrames + 1, {}, {}, Status::BlockTooLarge, summary);
    process(engine, 2, std::span<float>(output).first(1), {}, Status::InvalidBuffer, summary);
    process(engine, 0, output, fixtures.too_many, Status::TooManyEvents, summary);
    process(engine, dense_frames, output, fixtures.invalid_tail, Status::InvalidEvent, summary);
    const std::array bad_target{Event{0, EventType::KeyPosition, Manual::Upper, 60, 1.1}};
    process(engine, 1, output, bad_target, Status::InvalidEvent, summary);
    Engine ideal;
    CHECK(ideal.prepare(profile, {rate, 64, 43, 0}) == Status::Ok);
    process(ideal, 1, output, fixtures.partial, Status::InvalidEvent, summary);
}

[[nodiscard]] bool equal_event(const Event& left, const Event& right) noexcept {
    return left.offset == right.offset && left.type == right.type &&
        left.manual == right.manual && left.index == right.index && left.value == right.value;
}

void translate(NoteOwnership& owners, std::uint32_t frames,
               std::span<const HostNoteEvent> input, std::span<Event> output,
               Status expected, std::uint32_t expected_physical, Summary& summary) {
    const auto before = owners;
    const Event marker{7, static_cast<EventType>(255), Manual::Lower, 96, -1234.5};
    std::fill(output.begin(), output.end(), marker);
    const auto result = observe("NoteOwnership::translate", [&]() noexcept {
        return owners.translate(frames, input, output);
    });
    count_result(summary.translation, result.status, expected);
    CHECK(result.input_consumed == (expected == Status::Ok ? input.size() : 0));
    CHECK(result.output_events == expected_physical);
    for (std::size_t i = result.output_events; i < output.size(); ++i) {
        CHECK(equal_event(output[i], marker));
    }
    if (expected != Status::Ok) CHECK(owners == before);
    else {
        summary.translation.input_events += input.size();
        summary.translation.physical_events += result.output_events;
    }
}

void test_translation(const Fixtures& fixtures, Summary& summary) {
    NoteOwnership owners;
    std::array<Event, kMaxEventsPerBlock> output{};
    std::array<HostNoteEvent, kMaxNoteOwners> full{};
    for (std::size_t i = 0; i < full.size(); ++i) {
        full[i] = {0, HostNoteKind::On, static_cast<std::uint8_t>((i / 61) % 2),
            static_cast<std::uint8_t>(i / 122), static_cast<std::uint8_t>(36 + i % 61),
            100, static_cast<std::int32_t>(i)};
    }
    translate(owners, 0, full, output, Status::Ok, 122, summary);
    CHECK(owners.owner_count() == kMaxNoteOwners);
    const std::array extra{HostNoteEvent{0, HostNoteKind::On, 0, 3, 60, 100, 9999}};
    translate(owners, 0, extra, output, Status::TooManyEvents, 0, summary);
    CHECK(owners.set_bus_route(0, Manual::Lower));
    translate(owners, 0, fixtures.channel_release, output, Status::Ok, 122, summary);
    CHECK(owners.owner_count() == 0);
    translate(owners, dense_frames, fixtures.host_dense, output, Status::Ok, dense_frames, summary);
    CHECK(owners.owner_count() == 0);
    translate(owners, dense_frames, fixtures.host_dense,
              std::span<Event>(output).first(kMaxEventsPerBlock - 1),
              Status::TooManyEvents, 0, summary);
    auto bad = fixtures.host_dense;
    bad.back().bus = 2;
    translate(owners, dense_frames, bad, output, Status::InvalidEvent, 0, summary);
}

void test_owned(const RuntimeProfile& profile, const Fixtures& fixtures,
                double rate, Summary& summary) {
    Engine engine;
    CHECK(engine.prepare(profile, {rate, kHardMaxBlockFrames, 43, 157},
                         make_nominal_console_model()) == Status::Ok);
    NoteOwnership owners;
    std::vector<float> output(kHardMaxBlockFrames + 3, sentinel);
    process(engine, 0, {}, fixtures.controls, Status::Ok, summary);
    owned_process(engine, owners, 1, output, fixtures.host_keys, Status::Ok, 122, summary);
    owned_process(engine, owners, static_cast<std::uint32_t>(std::ceil(rate * 0.01)),
                  output, {}, Status::Ok, 0, summary);
    CHECK(engine.percussion_diagnostics().routed_detector);
    CHECK(owners.set_bus_route(0, Manual::Lower));
    std::array<HostNoteEvent, kMaxNoteOwners - key_count> extra{};
    for (std::size_t i = 0; i < extra.size(); ++i) {
        extra[i] = {0, HostNoteKind::On, 0, 1, 60, 100, static_cast<std::int32_t>(2000 + i)};
    }
    owned_process(engine, owners, 0, output, extra, Status::Ok, 0, summary);
    CHECK(owners.owner_count() == kMaxNoteOwners);
    const std::array capacity{HostNoteEvent{0, HostNoteKind::On, 0, 2, 61, 100, 9999}};
    owned_process(engine, owners, 1, output, capacity, Status::TooManyEvents, 0, summary);
    const std::array candidate_release{HostNoteEvent{0, HostNoteKind::Off, 0, 0, 36, 0, 0}};
    owned_process(engine, owners, 2, std::span<float>(output).first(1), candidate_release,
                  Status::InvalidBuffer, 0, summary);
    owned_process(engine, owners, kHardMaxBlockFrames + 1, {}, {},
                  Status::BlockTooLarge, 0, summary);
    owned_process(engine, owners, 0, output, fixtures.host_too_many,
                  Status::TooManyEvents, 0, summary);
    auto invalid_tail = fixtures.host_too_many;
    invalid_tail[kMaxEventsPerBlock - 1].bus = 2;
    owned_process(engine, owners, dense_frames, output,
                  std::span<const HostNoteEvent>(invalid_tail).first(kMaxEventsPerBlock),
                  Status::InvalidEvent, 0, summary);
    owned_process(engine, owners, 0, output, fixtures.channel_release, Status::Ok, 122, summary);
    CHECK(owners.owner_count() == 0 && engine.active_key_count() == 0);
    owned_process(engine, owners, kHardMaxBlockFrames, output, {}, Status::Ok, 0, summary);
    CHECK(!engine.percussion_diagnostics().physical_detector);
    auto disconnected = engine;
    auto disconnected_owners = owners;
    owned_process(engine, owners, dense_frames, output, fixtures.host_dense,
                  Status::Ok, dense_frames, summary);
    owned_process(disconnected, disconnected_owners, dense_frames, {}, fixtures.host_dense,
                  Status::Ok, dense_frames, summary);
    CHECK(state_of(engine) == state_of(disconnected));
    CHECK(owners == disconnected_owners);

    Engine exhausted;
    CHECK(exhausted.prepare(profile, {rate, 64, 43, std::numeric_limits<std::uint64_t>::max()},
                            make_nominal_console_model()) == Status::Ok);
    NoteOwnership empty;
    const auto one = std::span<const HostNoteEvent>(fixtures.host_keys).first(1);
    owned_process(exhausted, empty, 1, output, one, Status::TimelineOverflow, 0, summary);
    owned_process(exhausted, empty, 0, {}, one, Status::Ok, 1, summary);
    CHECK(empty.owner_count() == 1 && exhausted.key_down(Manual::Upper, 36));
    Engine unprepared;
    NoteOwnership untouched;
    owned_process(unprepared, untouched, 1, output, one, Status::NotPrepared, 0, summary);
}

void rate_change(Engine& engine, double rate, Status expected, Summary& summary) {
    auto before = state_of(engine);
    const auto result = observe("stopped Engine::reconfigure_sample_rate", [&]() noexcept {
        return engine.reconfigure_sample_rate(rate);
    });
    count_result(summary.lifecycle, result, expected);
    if (expected == Status::Ok) before.rate = rate;
    CHECK(state_of(engine) == before);
}

void test_stopped_lifecycle(const RuntimeProfile& profile, const Fixtures& fixtures,
                            double rate, Summary& summary) {
    Engine engine;
    CHECK(engine.prepare(profile, {rate, 1024, 43, 179}, make_nominal_console_model()) == Status::Ok);
    // Create a moving partial-key state outside the lifecycle observation.
    CHECK(engine.process(17, {}, fixtures.first));
    rate_change(engine, rate, Status::Ok, summary);
    rate_change(engine, rate == 44100.0 ? 48000.0 : rate == 48000.0 ? 96000.0 : 44100.0,
                Status::Ok, summary);
    rate_change(engine, 12345.0, Status::InvalidSpec, summary);
    rate_change(engine, std::numeric_limits<double>::quiet_NaN(), Status::InvalidSpec, summary);
}

void print_totals(const char* label, const Totals& totals) {
    std::printf("%s: %zu accepted, %zu rejected; %llu rendered frames, "
                "%llu input events, %llu physical events; zero C++ allocations/deallocations.\n",
                label, totals.accepted, totals.rejected,
                static_cast<unsigned long long>(totals.frames),
                static_cast<unsigned long long>(totals.input_events),
                static_cast<unsigned long long>(totals.physical_events));
}

} // namespace

int main() {
    test_probe_overloads();
    const auto profile = load_test_profile();
    const auto fixtures = make_fixtures();
    Summary summary;
    // Parameter lookup/conversion and standalone translation do not depend on rate.
    const auto mapped = test_parameters(summary);
    test_translation(fixtures, summary);
    for (const double rate : {44100.0, 48000.0, 96000.0}) {
        test_engine(profile, fixtures, mapped, rate, summary);
        test_owned(profile, fixtures, rate, summary);
        test_stopped_lifecycle(profile, fixtures, rate, summary);
    }
    Engine unprepared;
    rate_change(unprepared, 48000.0, Status::NotPrepared, summary);
    auto high_profile = profile;
    high_profile.sources[0].frequency_hz = 30000.0;
    Engine high;
    CHECK(high.prepare(high_profile, {96000.0, 64, 43, 0}, make_nominal_console_model()) == Status::Ok);
    rate_change(high, 48000.0, Status::InvalidProfile, summary);
    CHECK(!allocation_probe::recording);
    print_totals("Enabled Engine processing", summary.engine);
    print_totals("Standalone ownership translation", summary.translation);
    print_totals("Owned-input processing", summary.owned);
    print_totals("Parameter APIs (rate independent)", summary.parameters);
    print_totals("Stopped sample-rate lifecycle", summary.lifecycle);
    std::printf("Calibration separately observed 12 allocations and 12 deallocations.\n");
    return 0;
}
