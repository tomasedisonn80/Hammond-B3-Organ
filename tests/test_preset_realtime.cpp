#include "TestSupport.h"
#include "PresetTestOracle.h"
#include "hammond/Engine.h"
#include "hammond/HostTimeline.h"
#include "hammond/PerformanceInput.h"

#include <algorithm>
#include <array>
#include <bit>
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
#include <string_view>
#include <type_traits>

// Reuse only the established portable instrumentation from test_realtime.cpp.
// Musical fixtures, expected transitions and measured regions below are local
// to this independent selector acceptance. It has no native SDK dependency.
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

enum class Path : std::size_t { Lookup, Control, Engine, Combined, Timeline, Count };
constexpr std::array<const char*, static_cast<std::size_t>(Path::Count)> kPathNames{
    "lookup", "control", "engine", "combined", "timeline"};
struct Totals {
    std::size_t calls{}, accepted{}, rejected{}, allocations{}, deallocations{};
    std::uint64_t frames{}, records{};
};
std::array<Totals, static_cast<std::size_t>(Path::Count)> totals{};
std::uint64_t compared_samples{}, audible_samples{}, preserved_histories{}, future_probes{};
constexpr float kSentinel = -1234.5F;
constexpr std::uint32_t kFrames = 1024;
constexpr Manual upper = Manual::Upper;
constexpr Manual lower = Manual::Lower;

static_assert(std::is_trivially_copyable_v<Engine>);
static_assert(std::is_trivially_copyable_v<HostTimeline>);
static_assert(std::is_trivially_copyable_v<PerformanceInputEvent>);

template <class Function>
auto observe(Path path, Function&& function) {
    CHECK(!allocation_probe::recording);
    allocation_probe::begin();
    const auto result = function();
    const auto seen = allocation_probe::end();
    auto& total = totals[static_cast<std::size_t>(path)];
    ++total.calls;
    total.allocations += seen.allocations;
    total.deallocations += seen.deallocations;
    CHECK(seen.allocations == 0);
    CHECK(seen.deallocations == 0);
    return result;
}

void record(Path path, bool accepted, std::uint32_t frames = 0,
            std::size_t records = 0) {
    auto& total = totals[static_cast<std::size_t>(path)];
    if (accepted) {
        ++total.accepted;
        total.frames += frames;
        total.records += records;
    } else {
        ++total.rejected;
    }
}

void test_lookup_first_use() {
    // This is the first call to any fixed-data function in this process, before
    // profile loading or preparation. Expected digits come only from A10's
    // independent page-122 transcription, never from generated native data.
    FixedRegistrationPositions positions{};
    const auto first = observe(Path::Lookup, [&] {
        return fixed_registration_positions(upper, FixedRegistration::CSharp, positions);
    });
    record(Path::Lookup, first);
    CHECK(first);
    for (std::size_t bar = 0; bar < kDrawbarCount; ++bar)
        CHECK(positions[bar] == preset_test_oracle::kPositions[0][0][bar]);

    const auto identity = observe(Path::Lookup, [] { return fixed_registration_catalog_id(); });
    record(Path::Lookup, !identity.empty());
    CHECK(identity == "atlas-chapel-nominal-v1");
    const auto sha = observe(Path::Lookup, [] { return fixed_registration_catalog_sha256(); });
    record(Path::Lookup, !sha.empty());
    CHECK(sha == "c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf");

    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        for (std::uint8_t key = 1; key <= 9; ++key) {
            const auto fixed = static_cast<FixedRegistration>(key);
            const bool ok = observe(Path::Lookup, [&] {
                return fixed_registration_positions(static_cast<Manual>(manual), fixed, positions);
            });
            record(Path::Lookup, ok);
            CHECK(ok);
            for (std::size_t bar = 0; bar < kDrawbarCount; ++bar)
                CHECK(positions[bar] == preset_test_oracle::kPositions[manual][key - 1U][bar]);
            const auto label = observe(Path::Lookup, [&] { return fixed_registration_label(fixed); });
            record(Path::Lookup, !label.empty());
            CHECK(label == preset_test_oracle::kKeys[key - 1U]);
        }
    }
    constexpr std::array<std::string_view, 12> labels{
        "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"};
    for (std::size_t key = 0; key < labels.size(); ++key) {
        const auto label = observe(Path::Lookup, [&] {
            return preset_selection_label(static_cast<PresetSelection>(key));
        });
        record(Path::Lookup, !label.empty());
        CHECK(label == labels[key]);
    }
    for (const auto manual : {upper, lower, static_cast<Manual>(255)}) {
        for (const auto fixed : {FixedRegistration::None, static_cast<FixedRegistration>(255)}) {
            positions.fill(37);
            const auto before = positions;
            const bool ok = observe(Path::Lookup, [&] {
                return fixed_registration_positions(manual, fixed, positions);
            });
            record(Path::Lookup, ok);
            CHECK(!ok && positions == before);
        }
    }
}

ControlSnapshot rich_controls() {
    ControlSnapshot value{};
    value.drawbars[0][0] = {7, 1, 6, 2, 5, 3, 4, 2, 1};
    value.drawbars[0][1] = {3, 2, 8, 5, 3, 1, 4, 6, 7};
    value.drawbars[1][0] = {2, 5, 7, 3, 1, 4, 2, 3, 5};
    value.drawbars[1][1] = {4, 1, 6, 3, 2, 5, 1, 2, 4};
    value.selected_banks = {DrawbarBank::B, DrawbarBank::A};
    value.pedal_drawbars = {3, 2};
    value.expression = 0.625;
    value.percussion.enabled = true;
    value.percussion.harmonic = PercussionHarmonic::Third;
    value.percussion.decay = PercussionDecay::Fast;
    return value;
}

// Independent ordinary-control transition oracle, with no ControlState calls.
void select_expected(ControlSnapshot& controls, Manual manual, std::uint8_t key) {
    const auto index = static_cast<std::size_t>(manual);
    if (key == 0) {
        controls.route_enabled[index] = false;
    } else if (key < 10) {
        controls.fixed_registrations[index] = static_cast<FixedRegistration>(key);
        controls.route_enabled[index] = true;
    } else {
        controls.selected_banks[index] = key == 10 ? DrawbarBank::A : DrawbarBank::B;
        controls.fixed_registrations[index] = FixedRegistration::None;
        controls.route_enabled[index] = true;
    }
}

Event selection(Manual manual, double value, std::uint32_t offset = 0) {
    return {offset, EventType::SelectPreset, manual, 0, value};
}

struct History {
    std::uint64_t clock{};
    std::array<double, kToneSourceCount> phases{};
    std::array<std::array<ContactKeySnapshot, kManualKeyCount>, kManualCount> contacts{};
    PedalContactStates pedals{};
    PedalRenderDiagnostics last_pedal{};
    double readiness{};
    bool operator==(const History&) const noexcept = default;
};

History history(const Engine& engine) {
    History result{};
    result.clock = engine.frame_clock();
    result.readiness = engine.percussion_diagnostics().readiness;
    result.last_pedal = engine.last_pedal_frame();
    CHECK(engine.pedal_contacts_snapshot(result.pedals));
    for (std::size_t tone = 0; tone < kToneSourceCount; ++tone)
        CHECK(engine.source_phase_turns(static_cast<ToneId>(tone + 1), result.phases[tone]));
    for (std::size_t manual = 0; manual < kManualCount; ++manual)
        for (std::size_t key = 0; key < kManualKeyCount; ++key)
            CHECK(engine.contact_snapshot(static_cast<Manual>(manual),
                  static_cast<std::uint32_t>(key) + kMinManualMidiNote,
                  result.contacts[manual][key]));
    return result;
}

void inspect_output(std::span<const float> output, std::size_t frames) {
    for (std::size_t index = 0; index < output.size(); ++index) {
        CHECK(std::isfinite(output[index]));
        if (index < frames) {
            CHECK(output[index] != kSentinel);
            if (output[index] != 0.0F) ++audible_samples;
        } else {
            CHECK(output[index] == kSentinel);
        }
    }
}

void same_audio(std::span<const float> actual, std::span<const float> expected) {
    CHECK(actual.size() == expected.size());
    for (std::size_t index = 0; index < actual.size(); ++index) {
        CHECK(std::bit_cast<std::uint32_t>(actual[index]) ==
              std::bit_cast<std::uint32_t>(expected[index]));
        ++compared_samples;
    }
}

void engine_call(Engine& engine, std::uint32_t frames, std::span<float> output,
                 std::span<const Event> events, Status status = Status::Ok) {
    const auto result = observe(Path::Engine, [&] { return engine.process(frames, output, events); });
    record(Path::Engine, result.ok(), frames, events.size());
    CHECK(result.status == status);
    CHECK(result.events_consumed == (result.ok() ? events.size() : 0));
}

void compare_future(Engine& engine, Engine& unchanged) {
    std::array<float, 67> actual{}, expected{};
    actual.fill(kSentinel);
    expected.fill(kSentinel);
    engine_call(engine, 64, actual, {});
    CHECK(unchanged.process(64, expected, {}).ok());
    same_audio(actual, expected);
    CHECK(history(engine) == history(unchanged));
    CHECK(engine.controls_snapshot() == unchanged.controls_snapshot());
    ++future_probes;
}

void test_engine(const RuntimeProfile& profile, double rate, const ConsoleModel& model) {
    Engine engine{};
    CHECK(engine.prepare(profile, {rate, kFrames, 79, 17}, model) == Status::Ok);
    auto expected = rich_controls();
    const auto restored = observe(Path::Control, [&] { return engine.restore_controls(expected); });
    record(Path::Control, restored);
    CHECK(restored);
    std::array<float, kFrames + 3> output{};
    const std::array<Event, 10> first{{
        selection(upper, 1), selection(lower, 9),
        {0, EventType::NoteOn, upper, 36, 127},
        {0, EventType::NoteOn, upper, 60, 93},
        {0, EventType::NoteOn, upper, 96, 1},
        {0, EventType::NoteOn, lower, 48, 127},
        {0, EventType::NoteOn, lower, 72, 50},
        {0, EventType::PedalOn, lower, 1, 127},
        {0, EventType::PedalOn, lower, 25, 1},
        {0, EventType::KeyPosition, upper, 65,
            model.contacts.mode == ContactMode::LinearTravel ? 0.55 : 1.0}}};
    // No process call has warmed this Engine instance before the observation.
    output.fill(kSentinel);
    engine_call(engine, 128, output, first);
    inspect_output(output, 128);
    select_expected(expected, upper, 1);
    select_expected(expected, lower, 9);
    CHECK(engine.controls_snapshot() == expected);
    CHECK(engine.active_key_count() == 6 && engine.active_pedal_count() == 2);
    if (model.contacts.mode == ContactMode::LinearTravel) {
        ContactKeySnapshot partial{};
        CHECK(engine.contact_snapshot(upper, 65, partial));
        CHECK(partial.position > 0.0 && partial.position < partial.target && partial.target == 0.55);
    }

    for (const auto manual : {upper, lower}) {
        for (std::uint8_t key = 0; key < 12; ++key) {
            const auto before = history(engine);
            const std::array<Event, 1> event{{selection(manual, key == 0 ? -0.0 : key)}};
            output.fill(kSentinel);
            engine_call(engine, 0, output, event);
            inspect_output(output, 0);
            select_expected(expected, manual, key);
            CHECK(engine.controls_snapshot() == expected);
            CHECK(history(engine) == before);
            ++preserved_histories;
            PresetSelection selected{};
            const bool queried = observe(Path::Control, [&] {
                return engine.selected_preset(manual, selected);
            });
            record(Path::Control, queried);
            CHECK(queried && static_cast<std::uint8_t>(selected) == key);
            const auto diag = engine.percussion_diagnostics();
            const bool eligible = expected.route_enabled[0] &&
                expected.fixed_registrations[0] == FixedRegistration::None &&
                expected.selected_banks[0] == DrawbarBank::B;
            CHECK(diag.eligible == eligible);
            engine_call(engine, 32, output, {});
            inspect_output(output, 32);
        }
    }

    // A full admitted event budget changes fixed/bank/Cancel routes repeatedly.
    std::array<Event, kMaxEventsPerBlock> dense{};
    for (std::size_t index = 0; index < dense.size(); ++index) {
        const auto manual = index % 2 == 0 ? upper : lower;
        const auto key = static_cast<std::uint8_t>((index / 2) % 12);
        dense[index] = selection(manual, key, static_cast<std::uint32_t>(index));
        select_expected(expected, manual, key);
    }
    output.fill(kSentinel);
    engine_call(engine, kFrames, output, dense);
    inspect_output(output, kFrames);
    CHECK(engine.controls_snapshot() == expected);
    CHECK(engine.active_key_count() == 6 && engine.active_pedal_count() == 2);
    const auto disconnected = engine.frame_clock();
    engine_call(engine, 32, {}, {});
    CHECK(engine.frame_clock() == disconnected + 32);

    const std::array<Event, 7> invalid{{
        {0, EventType::SelectPreset, static_cast<Manual>(2), 0, 1},
        {0, EventType::SelectPreset, upper, 1, 1},
        selection(lower, -1), selection(upper, 12), selection(lower, 0.5),
        selection(upper, std::numeric_limits<double>::infinity()),
        selection(lower, std::numeric_limits<double>::quiet_NaN())}};
    for (const auto& bad : invalid) {
        for (const auto frames : {0U, 64U}) {
            auto unchanged = engine;
            const auto before = history(engine);
            const std::array<Event, 3> events{{selection(upper, 3),
                {0, EventType::NoteOn, lower, 80, 127}, bad}};
            output.fill(kSentinel);
            engine_call(engine, frames, output, events, Status::InvalidEvent);
            inspect_output(output, 0);
            CHECK(history(engine) == before && engine.controls_snapshot() == expected);
            compare_future(engine, unchanged);
        }
    }
    auto invalid_controls = expected;
    invalid_controls.fixed_registrations[1] = static_cast<FixedRegistration>(255);
    invalid_controls.route_enabled[1] = false;
    auto unchanged = engine;
    const bool accepted = observe(Path::Control, [&] {
        return engine.restore_controls(invalid_controls);
    });
    record(Path::Control, accepted);
    CHECK(!accepted);
    compare_future(engine, unchanged);
}

void test_combined(const RuntimeProfile& profile, const ConsoleModel& model) {
    Engine engine{};
    CHECK(engine.prepare(profile, {48000, kFrames, 59, 0}, model) == Status::Ok);
    CHECK(engine.restore_controls(rich_controls()));
    NoteOwnership manual{};
    PedalNoteOwnership pedals{};
    std::array<float, 67> output{};
    const std::array<PerformanceInputEvent, 5> first{{
        selection(upper, 3), HostNoteEvent{0, HostNoteKind::On, 0, 2, 60, 127, 51},
        HostNoteEvent{0, HostNoteKind::On, 1, 5, 48, 91, 52},
        PedalNoteEvent{0, PedalNoteKind::On, 1, 7, PedalId{1}, 80, 53}, selection(lower, 7)}};
    output.fill(kSentinel);
    auto result = observe(Path::Combined, [&] {
        return process_performance_input(engine, manual, pedals, 64, output, first);
    });
    record(Path::Combined, result.ok(), 64, first.size());
    CHECK(result.ok() && result.input_events_consumed == first.size());
    inspect_output(output, 64);
    CHECK(manual.owner_count() == 2 && pedals.owner_count() == 1);
    const auto kept_manual = manual;
    const auto kept_pedals = pedals;
    const std::array<PerformanceInputEvent, 5> changes{{selection(upper, 0),
        selection(lower, 0), selection(upper, 10),
        Event{0, EventType::SelectBank, upper, 0, 1}, selection(lower, 9)}};
    const auto before = history(engine);
    output.fill(kSentinel);
    result = observe(Path::Combined, [&] {
        return process_performance_input(engine, manual, pedals, 0, output, changes);
    });
    record(Path::Combined, result.ok(), 0, changes.size());
    CHECK(result.ok());
    CHECK(manual == kept_manual && pedals == kept_pedals);
    CHECK(history(engine) == before);
    ++preserved_histories;
    inspect_output(output, 0);
    const auto snapshot = engine.controls_snapshot();
    CHECK(snapshot.fixed_registrations[0] == FixedRegistration::None);
    CHECK(snapshot.selected_banks[0] == DrawbarBank::B && snapshot.route_enabled[0]);
    CHECK(snapshot.fixed_registrations[1] == FixedRegistration::A && snapshot.route_enabled[1]);

    const std::array<PerformanceInputEvent, 3> invalid{{
        HostNoteEvent{0, HostNoteKind::On, 0, 2, 66, 127, 54},
        selection(upper, 4), selection(lower, 12)}};
    auto unchanged = engine;
    result = observe(Path::Combined, [&] {
        return process_performance_input(engine, manual, pedals, 64, output, invalid);
    });
    record(Path::Combined, result.ok(), 64, invalid.size());
    CHECK(result.status == Status::InvalidEvent && result.input_events_consumed == 0 &&
          result.physical_events_consumed == 0);
    inspect_output(output, 0);
    CHECK(manual == kept_manual && pedals == kept_pedals);
    compare_future(engine, unchanged);
}

HostTimelineResult timeline_call(HostTimeline& host, std::uint32_t frames,
        std::span<float> output, std::span<const HostParameterQueue> queues,
        std::span<const HostMusicalEvent> music = {},
        std::span<const ControlSnapshot> restores = {}) {
    const auto result = observe(Path::Timeline, [&] {
        return host.process(frames, output, queues, music, restores);
    });
    record(Path::Timeline, result.ok(), frames, result.input_records_consumed);
    return result;
}

void compare_host_future(HostTimeline& host, HostTimeline& unchanged) {
    std::array<float, 67> actual{}, expected{};
    actual.fill(kSentinel);
    expected.fill(kSentinel);
    CHECK(timeline_call(host, 64, actual, {}).ok());
    CHECK(unchanged.process(64, expected, {}, {}).ok());
    same_audio(actual, expected);
    CHECK(history(host.engine()) == history(unchanged.engine()));
    CHECK(host.engine().controls_snapshot() == unchanged.engine().controls_snapshot());
    CHECK(host.manual_ownership() == unchanged.manual_ownership());
    CHECK(host.pedal_ownership() == unchanged.pedal_ownership());
    CHECK(host.carry_count() == unchanged.carry_count());
    ++future_probes;
}

void test_timeline(const RuntimeProfile& profile, double rate, const ConsoleModel& model) {
    // Allocate these large fixed-capacity objects before the probe, avoiding
    // dependence on the platform's default thread-stack reserve.
    auto host = std::make_unique<HostTimeline>();
    auto unchanged = std::make_unique<HostTimeline>();
    CHECK(host->prepare(profile, {rate, kFrames, 67, 0}, model) == Status::Ok);
    std::array<ControlSnapshot, 4> restores{};
    for (std::size_t index = 0; index < restores.size(); ++index) {
        restores[index] = rich_controls();
        restores[index].fixed_registrations = {static_cast<FixedRegistration>(index + 1),
                                              FixedRegistration::A};
        restores[index].route_enabled[0] = index % 2 != 0;
    }
    const std::array<HostParameterPoint, 1> upper_fixed{{{0, 0.25}}}; // literal D# bin
    const std::array<HostParameterPoint, 1> lower_fixed{{{0, 0.5}}}; // exact midpoint -> F#
    const std::array<HostParameterPoint, 1> old_b{{{0, 1.0}}};
    // Deliberately reverse native queue order; numeric ID is the command order.
    const std::array<HostParameterQueue, 3> queues{{
        {20481, lower_fixed}, {20480, upper_fixed}, {8208, old_b}}};
    const std::array<HostMusicalEvent, 3> music{{
        HostNoteEvent{0, HostNoteKind::On, 0, 0, 60, 127, 81},
        HostNoteEvent{0, HostNoteKind::On, 1, 1, 48, 127, 82},
        PedalNoteEvent{0, PedalNoteKind::On, 0, 2, PedalId{13}, 127, 83}}};
    std::array<float, 67> output{};
    output.fill(kSentinel);
    auto result = timeline_call(*host, 0, output, queues, music, restores);
    CHECK(result.ok() && result.restores_consumed == 4);
    inspect_output(output, 0);
    auto expected = restores.back();
    expected.selected_banks[0] = DrawbarBank::B;
    select_expected(expected, upper, 3);
    select_expected(expected, lower, 6);
    CHECK(host->engine().controls_snapshot() == expected);
    CHECK(host->manual_ownership().owner_count() == 2 && host->pedal_ownership().owner_count() == 1);
    CHECK(timeline_call(*host, 64, output, {}).ok());
    inspect_output(output, 64);

    const std::array<HostParameterPoint, 1> endpoint{{{64, 0.0}}};
    const std::array<HostParameterQueue, 1> carry{{{20481, endpoint}}};
    output.fill(kSentinel);
    CHECK(timeline_call(*host, 64, output, carry).ok());
    CHECK(host->carry_count() == 1);
    inspect_output(output, 64);
    // Carried lower Cancel and repeated unchanged old upper B apply without
    // emitting a note or resetting time. New upper D# still wins their tie.
    const std::array<HostParameterQueue, 2> alias{{{20480, upper_fixed}, {8208, old_b}}};
    const auto before = history(host->engine());
    const auto kept_manual = host->manual_ownership();
    const auto kept_pedals = host->pedal_ownership();
    output.fill(kSentinel);
    result = timeline_call(*host, 0, output, alias);
    CHECK(result.ok() && result.carried_records_consumed == 1 && host->carry_count() == 0);
    inspect_output(output, 0);
    CHECK(history(host->engine()) == before);
    ++preserved_histories;
    CHECK(host->manual_ownership() == kept_manual && host->pedal_ownership() == kept_pedals);
    CHECK(host->engine().controls_snapshot().fixed_registrations[0] == FixedRegistration::DSharp);
    CHECK(!host->engine().controls_snapshot().route_enabled[1]);

    std::array<HostParameterPoint, kMaxEventsPerBlock> dense{};
    for (std::size_t index = 0; index < dense.size(); ++index)
        dense[index] = {0, index % 2 == 0 ? 0.25 : 1.0};
    const std::array<HostParameterQueue, 1> dense_queue{{{20480, dense}}};
    result = timeline_call(*host, 0, output, dense_queue);
    CHECK(result.ok() && result.input_records_consumed == dense.size());
    CHECK(host->engine().controls_snapshot().fixed_registrations[0] == FixedRegistration::None);
    CHECK(host->engine().controls_snapshot().selected_banks[0] == DrawbarBank::B);

    // Now traverse every new selector threshold while lower/pedal owners hold.
    const std::array<HostParameterPoint, 2> sweep{{{0, 0.0}, {64, 1.0}}};
    const std::array<HostParameterQueue, 1> sweep_queue{{{20480, sweep}}};
    output.fill(kSentinel);
    CHECK(timeline_call(*host, 64, output, sweep_queue).ok());
    inspect_output(output, 64);
    CHECK(host->carry_count() == 1);

    const std::array<HostParameterPoint, 1> nan{{{0, std::numeric_limits<double>::quiet_NaN()}}};
    const std::array<HostParameterQueue, 1> invalid{{{20480, nan}}};
    const std::array<HostMusicalEvent, 1> fresh{{
        HostNoteEvent{0, HostNoteKind::On, 0, 0, 72, 127, 84}}};
    *unchanged = *host;
    output.fill(kSentinel);
    result = timeline_call(*host, 64, output, invalid, fresh);
    CHECK(result.status == Status::InvalidEvent && result.input_records_consumed == 0 &&
          result.carried_records_consumed == 0 && result.restores_consumed == 0);
    inspect_output(output, 0);
    CHECK(history(host->engine()) == history(unchanged->engine()));
    CHECK(host->carry_count() == 1 && host->manual_ownership() == kept_manual);
    compare_host_future(*host, *unchanged);

    auto hidden_invalid = rich_controls();
    hidden_invalid.route_enabled[0] = false;
    hidden_invalid.fixed_registrations[0] = static_cast<FixedRegistration>(255);
    const std::array<ControlSnapshot, 1> invalid_restore{{hidden_invalid}};
    *unchanged = *host;
    output.fill(kSentinel);
    result = timeline_call(*host, 0, output, {}, {}, invalid_restore);
    CHECK(result.status == Status::InvalidEvent);
    inspect_output(output, 0);
    compare_host_future(*host, *unchanged);
}

} // namespace

int main() {
    test_probe_overloads();
    test_lookup_first_use();
    const auto profile = load_test_profile();
    for (const double rate : {44100.0, 48000.0, 96000.0}) {
        for (const auto& model : {make_legacy_console_model(), make_nominal_console_model()}) {
            test_engine(profile, rate, model);
            test_timeline(profile, rate, model);
        }
    }
    for (const auto& model : {make_legacy_console_model(), make_nominal_console_model()})
        test_combined(profile, model);
    CHECK(audible_samples > 0 && compared_samples > 0);
    CHECK(!allocation_probe::recording);
    std::printf("preset realtime: calibration=12/12, compared_samples=%llu, audible_samples=%llu, "
                "preserved_histories=%llu, future_probes=%llu\n",
        static_cast<unsigned long long>(compared_samples),
        static_cast<unsigned long long>(audible_samples),
        static_cast<unsigned long long>(preserved_histories),
        static_cast<unsigned long long>(future_probes));
    for (std::size_t index = 0; index < totals.size(); ++index) {
        const auto& value = totals[index];
        CHECK(value.calls == value.accepted + value.rejected);
        std::printf("%s calls=%zu accepted=%zu rejected=%zu frames=%llu records=%llu "
                    "new=%zu delete=%zu\n", kPathNames[index], value.calls,
            value.accepted, value.rejected, static_cast<unsigned long long>(value.frames),
            static_cast<unsigned long long>(value.records), value.allocations, value.deallocations);
    }
}
