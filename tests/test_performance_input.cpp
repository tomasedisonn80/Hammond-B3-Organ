#include "TestSupport.h"
#include "hammond/PerformanceInput.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <iostream>
#include <limits>
#include <span>
#include <variant>
#include <vector>

namespace {

using namespace hammond;
using Input = PerformanceInputEvent;
constexpr float sentinel = -4321.25F;

struct Totals {
    std::uint64_t accepted{};
    std::uint64_t rejected{};
    std::uint64_t samples{};
    std::uint64_t phases{};
    std::uint64_t partitions{};
} totals;

struct Runtime {
    Engine engine;
    NoteOwnership manuals;
    PedalNoteOwnership pedals;
};

struct State {
    bool prepared{};
    std::uint64_t frame{};
    double rate{};
    ControlSnapshot controls{};
    std::array<std::array<bool, kManualKeyCount>, kManualCount> keys{};
    std::array<std::array<ContactKeySnapshot, kManualKeyCount>, kManualCount> contacts{};
    std::array<bool, kPedalCount> pedals{};
    PedalContactStates pedal_contacts{};
    PedalRenderDiagnostics last_pedal{};
    PercussionRoutingDiagnostics percussion{};
    std::array<std::uint64_t, kToneSourceCount> phase_bits{};
    bool operator==(const State&) const noexcept = default;
};

[[nodiscard]] State state(const Engine& engine) {
    State result;
    result.prepared = engine.prepared();
    result.frame = engine.frame_clock();
    result.rate = engine.sample_rate();
    result.controls = engine.controls_snapshot();
    result.last_pedal = engine.last_pedal_frame();
    result.percussion = engine.percussion_diagnostics();
    if (!result.prepared) return result;
    for (std::size_t m = 0; m < kManualCount; ++m) {
        for (std::size_t k = 0; k < kManualKeyCount; ++k) {
            const auto midi = static_cast<std::uint32_t>(k + kMinManualMidiNote);
            result.keys[m][k] = engine.key_down(static_cast<Manual>(m), midi);
            CHECK(engine.contact_snapshot(static_cast<Manual>(m), midi,
                                           result.contacts[m][k]));
        }
    }
    for (std::size_t p = 0; p < kPedalCount; ++p) {
        result.pedals[p] = engine.pedal_down(PedalId{static_cast<std::uint8_t>(p + 1)});
    }
    CHECK(engine.pedal_contacts_snapshot(result.pedal_contacts));
    for (std::size_t t = 0; t < kToneSourceCount; ++t) {
        double phase = 0.0;
        CHECK(engine.source_phase_turns(static_cast<ToneId>(t + 1), phase));
        result.phase_bits[t] = std::bit_cast<std::uint64_t>(phase);
    }
    return result;
}

void equal_state(const Engine& actual, const Engine& expected) {
    CHECK(state(actual) == state(expected));
    totals.phases += kToneSourceCount;
}

void equal_audio(std::span<const float> actual, std::span<const float> expected) {
    CHECK(actual.size() == expected.size());
    for (std::size_t i = 0; i < actual.size(); ++i) {
        CHECK(std::bit_cast<std::uint32_t>(actual[i]) ==
              std::bit_cast<std::uint32_t>(expected[i]));
        ++totals.samples;
    }
}

[[nodiscard]] Runtime prepared(double rate = 48000.0, bool nominal = true,
                               std::uint32_t maximum = 65536,
                               std::uint64_t first_frame = 37) {
    Runtime result;
    const auto profile = load_test_profile();
    const ProcessSpec spec{rate, maximum, 913, first_frame};
    CHECK(result.engine.prepare(profile, spec, nominal ? make_nominal_console_model()
                                                       : make_legacy_console_model()) == Status::Ok);
    return result;
}

[[nodiscard]] HostNoteEvent manual_on(std::uint32_t at, std::uint8_t bus,
                                     std::uint8_t channel, std::uint8_t note,
                                     std::int32_t id = -1) {
    return {at, HostNoteKind::On, bus, channel, note, 100, id};
}

[[nodiscard]] HostNoteEvent manual_off(std::uint32_t at, std::uint8_t bus,
                                      std::uint8_t channel, std::uint8_t note,
                                      std::int32_t id = -1) {
    return {at, HostNoteKind::Off, bus, channel, note, 0, id};
}

[[nodiscard]] PedalNoteEvent pedal_on(std::uint32_t at, std::uint8_t bus,
                                     std::uint8_t channel, std::uint8_t pedal,
                                     std::int32_t id = -1) {
    return {at, PedalNoteKind::On, bus, channel, PedalId{pedal}, 100, id};
}

[[nodiscard]] PedalNoteEvent pedal_off(std::uint32_t at, std::uint8_t bus,
                                      std::uint8_t channel, std::uint8_t pedal,
                                      std::int32_t id = -1) {
    return {at, PedalNoteKind::Off, bus, channel, PedalId{pedal}, 0, id};
}

void accepted(Runtime& runtime, std::uint32_t frames, std::span<float> output,
              std::span<const Input> input, std::size_t physical) {
    const auto clock = runtime.engine.frame_clock();
    const auto result = process_performance_input(
        runtime.engine, runtime.manuals, runtime.pedals, frames, output, input);
    CHECK(result.ok());
    CHECK(result.input_events_consumed == input.size());
    CHECK(result.physical_events_consumed == physical);
    CHECK(runtime.engine.frame_clock() == clock + frames);
    ++totals.accepted;
}

// Each rejection is followed by a fresh rendered suffix against the untouched
// pre-call copy, not only queries of the immediately visible state.
void rejected(Runtime runtime, std::uint32_t frames, std::span<const Input> input,
              Status expected, std::size_t output_size = 96) {
    Runtime untouched = runtime;
    const auto before = state(runtime.engine);
    std::vector<float> output(output_size, sentinel);
    const auto result = process_performance_input(
        runtime.engine, runtime.manuals, runtime.pedals, frames, output, input);
    CHECK(result.status == expected);
    CHECK(!result.ok());
    CHECK(result.input_events_consumed == 0);
    CHECK(result.physical_events_consumed == 0);
    CHECK(runtime.manuals == untouched.manuals);
    CHECK(runtime.pedals == untouched.pedals);
    CHECK(state(runtime.engine) == before);
    CHECK(std::all_of(output.begin(), output.end(), [](float v) { return v == sentinel; }));
    if (runtime.engine.prepared() &&
        runtime.engine.frame_clock() <= std::numeric_limits<std::uint64_t>::max() - 32) {
        std::array<float, 32> actual{}, reference{};
        accepted(runtime, 32, actual, {}, 0);
        accepted(untouched, 32, reference, {}, 0);
        equal_audio(actual, reference);
        equal_state(runtime.engine, untouched.engine);
    }
    ++totals.rejected;
}

[[nodiscard]] std::vector<Input> score() {
    return {
        Event{0, EventType::BankDrawbar, Manual::Upper, 13, 8.0},
        Event{0, EventType::Drawbar, Manual::Lower, 4, 5.0},
        Event{0, EventType::PedalDrawbar, Manual::Lower, 0, 6.0},
        Event{0, EventType::Percussion, Manual::Upper, 0, 1.0},
        manual_on(0, 0, 0, 60, 10), pedal_on(0, 0, 0, 1, 11),
        manual_on(0, 1, 2, 48), manual_on(4, 0, 1, 60, 12),
        pedal_on(4, 1, 3, 1), Event{7, EventType::Expression, Manual::Upper, 0, 0.5},
        manual_off(9, 0, 0, 60, 10), pedal_off(9, 0, 0, 1, 11),
        Event{12, EventType::Cancel, Manual::Lower, 0, 0.0},
        Event{12, EventType::SelectBank, Manual::Upper, 0, 0.0},
        Event{12, EventType::Drawbar, Manual::Upper, 4, 3.0},
        manual_off(14, 0, 1, 60, 12), pedal_off(14, 1, 3, 1),
        Event{20, EventType::SelectBank, Manual::Lower, 0, 1.0},
        manual_off(21, 1, 2, 48),
        Event{24, EventType::PedalDrawbar, Manual::Lower, 1, 4.0},
        pedal_on(24, 0, 2, 25, 2),
        PedalNoteEvent{27, PedalNoteKind::AllNotesOff, 0, 2, PedalId{0}, 0, -1},
        Event{30, EventType::Expression, Manual::Upper, 0, 0.75},
    };
}

// Hand-authored physical expectations, deliberately not generated with either
// production adapter. The four overlapping-owner edits emit no physical event.
[[nodiscard]] std::vector<Event> physical_score() {
    return {
        {0, EventType::BankDrawbar, Manual::Upper, 13, 8.0},
        {0, EventType::Drawbar, Manual::Lower, 4, 5.0},
        {0, EventType::PedalDrawbar, Manual::Lower, 0, 6.0},
        {0, EventType::Percussion, Manual::Upper, 0, 1.0},
        {0, EventType::NoteOn, Manual::Upper, 60, 100.0},
        {0, EventType::PedalOn, Manual::Lower, 1, 100.0},
        {0, EventType::NoteOn, Manual::Lower, 48, 100.0},
        {7, EventType::Expression, Manual::Upper, 0, 0.5},
        {12, EventType::Cancel, Manual::Lower, 0, 0.0},
        {12, EventType::SelectBank, Manual::Upper, 0, 0.0},
        {12, EventType::Drawbar, Manual::Upper, 4, 3.0},
        {14, EventType::NoteOff, Manual::Upper, 60, 0.0},
        {14, EventType::PedalOff, Manual::Lower, 1, 0.0},
        {20, EventType::SelectBank, Manual::Lower, 0, 1.0},
        {21, EventType::NoteOff, Manual::Lower, 48, 0.0},
        {24, EventType::PedalDrawbar, Manual::Lower, 1, 4.0},
        {24, EventType::PedalOn, Manual::Lower, 25, 100.0},
        {27, EventType::PedalOff, Manual::Lower, 25, 0.0},
        {30, EventType::Expression, Manual::Upper, 0, 0.75},
    };
}

void test_actual_engine_and_partition() {
    const auto input = score();
    const auto expected_events = physical_score();
    for (const auto rate : {44100.0, 48000.0, 96000.0}) {
        for (const bool nominal : {false, true}) {
            auto whole = prepared(rate, nominal);
            auto direct = prepared(rate, nominal);
            std::array<float, 512> actual{}, expected{};
            accepted(whole, 512, actual, input, expected_events.size());
            CHECK(direct.engine.process(512, expected, expected_events));
            equal_audio(actual, expected);
            equal_state(whole.engine, direct.engine);
            CHECK(whole.manuals.owner_count() == 0);
            CHECK(whole.pedals.owner_count() == 0);
            CHECK(std::any_of(actual.begin(), actual.end(), [](float v) { return v != 0.0F; }));
            for (const std::uint32_t block : {1U, 7U, 31U, 64U, 127U, 256U, 512U}) {
                auto split = prepared(rate, nominal);
                std::array<float, 512> rendered{};
                std::size_t next = 0;
                std::size_t produced = 0;
                for (std::uint32_t at = 0; at < 512;) {
                    const auto count = std::min(block, 512U - at);
                    std::vector<Input> current;
                    while (next < input.size()) {
                        const auto offset = std::visit([](const auto& e) { return e.offset; }, input[next]);
                        if (offset >= at + count) break;
                        auto event = input[next++];
                        std::visit([at](auto& e) { e.offset -= at; }, event);
                        current.push_back(event);
                    }
                    const auto result = process_performance_input(split.engine, split.manuals,
                        split.pedals, count, std::span<float>{rendered}.subspan(at, count), current);
                    CHECK(result);
                    CHECK(result.input_events_consumed == current.size());
                    produced += result.physical_events_consumed;
                    ++totals.accepted;
                    at += count;
                }
                CHECK(next == input.size());
                CHECK(produced == expected_events.size());
                CHECK(split.manuals == whole.manuals && split.pedals == whole.pedals);
                equal_audio(rendered, actual);
                equal_state(split.engine, whole.engine);
                ++totals.partitions;
            }
        }
    }
}

void test_flush_disconnect_and_route_retention() {
    auto runtime = prepared();
    auto direct = prepared();
    const std::array<Input, 7> flush{
        Event{0, EventType::Drawbar, Manual::Upper, 4, 8.0},
        manual_on(0, 0, 2, 60, 41), pedal_on(0, 0, 3, 12, 41),
        Event{0, EventType::Cancel, Manual::Lower, 0, 0.0},
        Event{0, EventType::PedalDrawbar, Manual::Lower, 0, 8.0},
        manual_on(0, 0, 2, 60, 41), pedal_on(0, 0, 3, 12, 41)};
    const std::array<Event, 5> physical{{
        {0, EventType::Drawbar, Manual::Upper, 4, 8.0},
        {0, EventType::NoteOn, Manual::Upper, 60, 100.0},
        {0, EventType::PedalOn, Manual::Lower, 12, 100.0},
        {0, EventType::Cancel, Manual::Lower, 0, 0.0},
        {0, EventType::PedalDrawbar, Manual::Lower, 0, 8.0}}};
    const auto initial = state(runtime.engine);
    std::array<float, 9> untouched;
    untouched.fill(sentinel);
    accepted(runtime, 0, untouched, flush, physical.size());
    CHECK(direct.engine.process(0, {}, physical));
    equal_state(runtime.engine, direct.engine);
    CHECK(state(runtime.engine).phase_bits == initial.phase_bits);
    CHECK(!runtime.engine.last_pedal_frame().valid);
    CHECK(std::all_of(untouched.begin(), untouched.end(), [](float v) { return v == sentinel; }));
    CHECK(runtime.manuals.owner_count() == 1 && runtime.pedals.owner_count() == 1);
    CHECK(runtime.engine.pedal_down(PedalId{12}));

    Runtime connected = runtime;
    std::array<float, 513> discard{};
    accepted(runtime, 513, {}, {}, 0);
    accepted(connected, 513, discard, {}, 0);
    equal_state(runtime.engine, connected.engine);
    CHECK(runtime.engine.last_pedal_frame().frame == 549);
    std::array<float, 73> actual{}, reference{};
    actual.fill(sentinel);
    reference.fill(sentinel);
    accepted(runtime, 64, actual, {}, 0);
    accepted(connected, 64, reference, {}, 0);
    equal_audio(actual, reference);
    CHECK(std::all_of(actual.begin() + 64, actual.end(), [](float v) { return v == sentinel; }));

    // An owner's original destination survives a future bus remap. Pedal IDs
    // belong to a separate namespace even when the identified note ID is equal.
    CHECK(runtime.manuals.set_bus_route(0, Manual::Lower));
    const std::array<Input, 4> remapped{manual_on(0, 0, 2, 60, 41),
        manual_off(0, 0, 2, 60, 41), manual_on(0, 0, 2, 62, 42),
        pedal_off(0, 0, 3, 12, 41)};
    accepted(runtime, 0, {}, remapped, 3);
    CHECK(!runtime.engine.key_down(Manual::Upper, 60));
    CHECK(runtime.engine.key_down(Manual::Lower, 62));
    CHECK(!runtime.engine.pedal_down(PedalId{12}));
    CHECK(runtime.manuals.owner_count() == 1 && runtime.pedals.owner_count() == 0);
}

void test_all_physical_notes() {
    auto runtime = prepared(96000.0, false);
    auto direct = prepared(96000.0, false);
    std::vector<Input> input;
    std::vector<Event> expected;
    const std::array<Event, 4> controls{{
        {0, EventType::Drawbar, Manual::Upper, 4, 4.0},
        {0, EventType::Drawbar, Manual::Lower, 4, 3.0},
        {0, EventType::PedalDrawbar, Manual::Lower, 0, 5.0},
        {0, EventType::PedalDrawbar, Manual::Lower, 1, 2.0}}};
    for (const auto control : controls) { input.emplace_back(control); expected.push_back(control); }
    for (std::uint8_t pedal = 1; pedal <= 25; ++pedal) {
        input.emplace_back(pedal_on(0, 0, 0, pedal));
        expected.push_back({0, EventType::PedalOn, Manual::Lower, pedal, 100.0});
    }
    for (std::uint8_t key = 36; key <= 96; ++key) {
        for (std::uint8_t bus = 0; bus < 2; ++bus) {
            input.emplace_back(manual_on(0, bus, 0, key));
            expected.push_back({0, EventType::NoteOn, static_cast<Manual>(bus), key, 100.0});
        }
    }
    std::array<float, 257> actual{}, reference{};
    accepted(runtime, 257, actual, input, expected.size());
    CHECK(direct.engine.process(257, reference, expected));
    equal_audio(actual, reference);
    equal_state(runtime.engine, direct.engine);
    CHECK(runtime.engine.active_key_count() == 122 && runtime.engine.active_pedal_count() == 25);
    CHECK(runtime.manuals.owner_count() == 122 && runtime.pedals.owner_count() == 25);
}

void test_rejections_and_admission_order() {
    auto ready = prepared();
    const std::array<Input, 4> seed{manual_on(0, 0, 0, 60, 91),
        pedal_on(0, 0, 0, 3, 91), Event{0, EventType::Drawbar, Manual::Upper, 4, 8.0},
        Event{0, EventType::PedalDrawbar, Manual::Lower, 0, 8.0}};
    accepted(ready, 0, {}, seed, 4);
    const std::vector<Input> prefix{manual_on(0, 1, 0, 48, 7), pedal_on(1, 1, 0, 4, 7),
        Event{2, EventType::Expression, Manual::Upper, 0, 0.25}};
    const auto late = [&](Input invalid, Status status = Status::InvalidEvent) {
        auto input = prefix;
        input.push_back(invalid);
        rejected(ready, 64, input, status);
    };
    for (const auto type : {EventType::NoteOn, EventType::NoteOff, EventType::AllNotesOff,
                            EventType::KeyPosition, EventType::PedalOn, EventType::PedalOff,
                            EventType::PedalAllNotesOff, static_cast<EventType>(255)}) {
        late(Event{63, type, Manual::Lower, 0, 0.0});
    }
    late(Event{63, EventType::Expression, Manual::Upper, 0,
               std::numeric_limits<double>::quiet_NaN()});
    late(Event{63, EventType::PedalDrawbar, Manual::Upper, 0, 4.0});
    late(Event{63, EventType::Drawbar, Manual::Upper, 4, 9.0});
    late(Event{63, EventType::Cancel, Manual::Lower, 0, 1.0});
    late(manual_on(63, 2, 0, 60));
    late(manual_on(63, 0, 16, 60));
    late(manual_on(63, 0, 0, 35));
    late(manual_on(63, 0, 0, 60, -2));
    late(HostNoteEvent{63, HostNoteKind::On, 0, 0, 60, 128, -1});
    late(HostNoteEvent{63, HostNoteKind::Off, 0, 0, 60, 1, -1});
    late(HostNoteEvent{63, static_cast<HostNoteKind>(255), 0, 0, 60, 0, -1});
    late(manual_on(63, 0, 0, 61, 91));
    late(manual_off(63, 0, 0, 61, 91));
    late(pedal_on(63, 2, 0, 3));
    late(pedal_on(63, 0, 16, 3));
    late(pedal_on(63, 0, 0, 0));
    late(pedal_on(63, 0, 0, 26));
    late(pedal_on(63, 0, 0, 3, -2));
    late(PedalNoteEvent{63, PedalNoteKind::On, 0, 0, PedalId{3}, 128, -1});
    late(PedalNoteEvent{63, PedalNoteKind::Off, 0, 0, PedalId{3}, 1, -1});
    late(PedalNoteEvent{63, static_cast<PedalNoteKind>(255), 0, 0, PedalId{3}, 0, -1});
    late(pedal_on(63, 0, 0, 4, 91));
    late(pedal_off(63, 0, 0, 4, 91));
    late(pedal_on(64, 0, 0, 1));
    late(Event{1, EventType::Expression, Manual::Upper, 0, 0.5});

    const std::array<Input, 1> nonzero{pedal_on(1, 0, 0, 1)};
    rejected(ready, 0, nonzero, Status::InvalidEvent);
    rejected(ready, 64, prefix, Status::InvalidBuffer, 63);
    rejected(ready, 65537, prefix, Status::BlockTooLarge);
    auto small = prepared(48000.0, true, 64);
    rejected(small, 65, prefix, Status::BlockTooLarge);
    Runtime unprepared;
    rejected(unprepared, 64, prefix, Status::NotPrepared);
    rejected(unprepared, 65537, {}, Status::BlockTooLarge);
    auto exhausted = prepared(48000.0, true, 65536,
                              std::numeric_limits<std::uint64_t>::max() - 1);
    rejected(exhausted, 2, {}, Status::TimelineOverflow);
    std::vector<Input> raw_overflow(1025, Event{0, EventType::Expression, Manual::Upper, 0, 1.0});
    rejected(ready, 64, raw_overflow, Status::TooManyEvents);
}

void test_capacity_and_scoped_panics() {
    auto runtime = prepared();
    std::vector<Input> seed{manual_on(0, 0, 0, 60), manual_on(0, 0, 0, 61)};
    for (std::uint8_t p = 1; p <= 25; ++p) seed.emplace_back(pedal_on(0, 0, 0, p));
    accepted(runtime, 0, {}, seed, 27);
    const HostNoteEvent manual_panic{0, HostNoteKind::AllNotesOff, 0, 0, 0, 0, -1};
    const PedalNoteEvent pedal_panic{0, PedalNoteKind::AllNotesOff, 0, 0, PedalId{0}, 0, -1};
    std::vector<Input> expanded(998, Event{0, EventType::Expression, Manual::Upper, 0, 0.75});
    expanded.emplace_back(manual_panic);
    expanded.emplace_back(pedal_panic);
    CHECK(expanded.size() == 1000); // 998 controls + 2 + 25 physical releases = 1025.
    rejected(runtime, 64, expanded, Status::TooManyEvents);
    expanded.erase(expanded.begin());
    accepted(runtime, 0, {}, expanded, 1024);
    CHECK(runtime.manuals.owner_count() == 0 && runtime.pedals.owner_count() == 0);
    CHECK(runtime.engine.active_key_count() == 0 && runtime.engine.active_pedal_count() == 0);

    std::vector<Input> exact_raw(1024, Event{0, EventType::Expression, Manual::Upper, 0, 0.5});
    accepted(runtime, 0, {}, exact_raw, 1024);

    // A completely full emitted prefix still admits a later duplicate with no
    // emission, but never drops a required final release to fit capacity.
    const std::array<Input, 3> hold{pedal_on(0, 0, 0, 1, 8),
        manual_on(0, 0, 0, 60, 9), manual_on(0, 0, 0, 61, 10)};
    accepted(runtime, 0, {}, hold, 3);
    std::vector<Input> capacity(1022, Event{0, EventType::Expression, Manual::Upper, 0, 0.5});
    capacity.emplace_back(manual_panic);
    capacity.emplace_back(pedal_off(0, 0, 0, 1, 8));
    rejected(runtime, 64, capacity, Status::TooManyEvents);
    capacity.pop_back();
    capacity.emplace_back(pedal_on(0, 0, 0, 1, 8));
    CHECK(capacity.size() == 1024);
    accepted(runtime, 0, {}, capacity, 1024);

    auto full = prepared();
    std::vector<Input> owners;
    for (std::int32_t id = 0; id < 256; ++id) {
        owners.emplace_back(manual_on(0, 0, 0, 60, id));
        owners.emplace_back(pedal_on(0, 0, 0, 3, id));
    }
    accepted(full, 0, {}, owners, 2);
    CHECK(full.manuals.owner_count() == 256 && full.pedals.owner_count() == 256);
    const std::array<Input, 2> late_pedal_overflow{
        manual_off(0, 0, 0, 60, 0), pedal_on(0, 0, 0, 4, 999)};
    rejected(full, 64, late_pedal_overflow, Status::TooManyEvents);
    const std::array<Input, 2> late_manual_overflow{
        pedal_off(0, 0, 0, 3, 0), manual_on(0, 0, 0, 62, 999)};
    rejected(full, 64, late_manual_overflow, Status::TooManyEvents);
    const std::array<Input, 4> free_and_reuse{
        manual_off(0, 0, 0, 60, 0), pedal_off(0, 0, 0, 3, 0),
        manual_on(0, 0, 0, 62, 999), pedal_on(0, 0, 0, 4, 999)};
    accepted(full, 0, {}, free_and_reuse, 2);
    CHECK(full.manuals.owner_count() == 256 && full.pedals.owner_count() == 256);
}

} // namespace

int main() {
    test_actual_engine_and_partition();
    test_flush_disconnect_and_route_retention();
    test_all_physical_notes();
    test_rejections_and_admission_order();
    test_capacity_and_scoped_panics();
    std::cout << "performance input: " << totals.accepted << " accepted calls, "
              << totals.rejected << " atomic rejection/future checks, "
              << totals.samples << " bitwise audio samples, "
              << totals.phases << " bitwise source phase comparisons, "
              << totals.partitions << " partition cases\n";
}
