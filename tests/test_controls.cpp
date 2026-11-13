#include "TestSupport.h"
#include "hammond/ControlState.h"
#include "hammond/Engine.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cstddef>
#include <cstdint>
#include <initializer_list>
#include <limits>
#include <span>
#include <vector>

namespace {

using hammond::ControlSnapshot;
using hammond::ControlState;
using hammond::DrawbarBank;
using hammond::DrawbarPositions;
using hammond::Engine;
using hammond::Event;
using hammond::EventType;
using hammond::Manual;
using hammond::ProcessSpec;
using hammond::RuntimeProfile;
using hammond::Status;

constexpr Manual upper = Manual::Upper;
constexpr Manual lower = Manual::Lower;
constexpr DrawbarBank bank_a = DrawbarBank::A;
constexpr DrawbarBank bank_b = DrawbarBank::B;
constexpr std::uint32_t max_block = 1024;
constexpr std::uint64_t clock_origin = 9000000017ULL;
constexpr float sentinel = -4321.75F;
constexpr DrawbarPositions silence{};

static_assert(static_cast<unsigned>(EventType::NoteOn) == 0);
static_assert(static_cast<unsigned>(EventType::NoteOff) == 1);
static_assert(static_cast<unsigned>(EventType::Drawbar) == 2);
static_assert(static_cast<unsigned>(EventType::Expression) == 3);
static_assert(static_cast<unsigned>(EventType::AllNotesOff) == 4);
static_assert(static_cast<unsigned>(EventType::BankDrawbar) == 5);
static_assert(static_cast<unsigned>(EventType::SelectBank) == 6);
static_assert(static_cast<unsigned>(EventType::Cancel) == 7);

[[nodiscard]] Event event(std::uint32_t offset, EventType type, Manual manual,
                          std::uint8_t index = 0, double value = 0.0) {
    return {offset, type, manual, index, value};
}

[[nodiscard]] Event select(std::uint32_t offset, Manual manual, DrawbarBank bank) {
    return event(offset, EventType::SelectBank, manual, 0,
                 static_cast<double>(static_cast<unsigned>(bank)));
}

void process_ok(Engine& engine, std::uint32_t frames, std::span<float> output = {},
                std::span<const Event> events = {}) {
    const auto result = engine.process(frames, output, events);
    CHECK(result.status == Status::Ok);
    CHECK(result.events_consumed == events.size());
}

void flush(Engine& engine, std::initializer_list<Event> events) {
    process_ok(engine, 0, {}, std::span<const Event>(events.begin(), events.size()));
}

[[nodiscard]] Engine prepared_engine(const RuntimeProfile& profile,
                                      double rate = 48000.0) {
    Engine engine;
    CHECK(engine.prepare(profile, ProcessSpec{rate, max_block, 0, clock_origin}) == Status::Ok);
    return engine;
}

[[nodiscard]] ControlSnapshot registrations() {
    ControlSnapshot result;
    result.drawbars[0][0] = {8, 0, 6, 0, 4, 0, 2, 0, 1};
    result.drawbars[0][1] = {0, 7, 0, 5, 0, 3, 0, 1, 0};
    result.drawbars[1][0] = {1, 2, 3, 4, 5, 6, 7, 8, 0};
    result.drawbars[1][1] = {8, 7, 6, 5, 4, 3, 2, 1, 0};
    result.expression = 0.625;
    return result;
}

void append_banks(std::vector<Event>& events, const ControlSnapshot& controls) {
    for (std::size_t manual = 0; manual < 2; ++manual) {
        for (std::size_t bank = 0; bank < 2; ++bank) {
            for (std::size_t bar = 0; bar < 9; ++bar) {
                events.push_back(event(0, EventType::BankDrawbar, static_cast<Manual>(manual),
                    static_cast<std::uint8_t>(bank * 9 + bar),
                    controls.drawbars[manual][bank][bar]));
            }
        }
    }
}

// This reference uses only pre-extension Drawbar/Expression/note events. Its
// bank B remains selected throughout. It does not call the new state API or
// translate production console events through ControlState.
void append_legacy_registration(std::vector<Event>& events, std::uint32_t offset,
                                Manual manual, const DrawbarPositions& positions) {
    for (std::size_t bar = 0; bar < positions.size(); ++bar) {
        events.push_back(event(offset, EventType::Drawbar, manual,
                               static_cast<std::uint8_t>(bar), positions[bar]));
    }
}

void apply_legacy_controls(Engine& engine, const ControlSnapshot& expected) {
    std::vector<Event> events;
    for (std::size_t manual = 0; manual < 2; ++manual) {
        const auto bank = static_cast<std::size_t>(expected.selected_banks[manual]);
        append_legacy_registration(events, 0, static_cast<Manual>(manual),
            expected.route_enabled[manual] ? expected.drawbars[manual][bank] : silence);
    }
    events.push_back(event(0, EventType::Expression, upper, 0, expected.expression));
    process_ok(engine, 0, {}, events);
}

void install_banks(Engine& engine, const ControlSnapshot& controls) {
    std::vector<Event> events;
    append_banks(events, controls);
    events.push_back(event(0, EventType::Expression, upper, 0, controls.expression));
    process_ok(engine, 0, {}, events);
}

void hold_keys(Engine& engine) {
    flush(engine, {event(0, EventType::NoteOn, upper, 36, 1),
                   event(0, EventType::NoteOn, upper, 60, 127),
                   event(0, EventType::NoteOn, lower, 48, 64)});
}

void same_audio(std::span<const float> actual, std::span<const float> expected) {
    CHECK(actual.size() == expected.size());
    for (std::size_t frame = 0; frame < actual.size(); ++frame) {
        CHECK(std::bit_cast<std::uint32_t>(actual[frame]) ==
              std::bit_cast<std::uint32_t>(expected[frame]));
    }
}

void audible(std::span<const float> samples) {
    CHECK(std::any_of(samples.begin(), samples.end(), [](float value) { return value != 0.0F; }));
}

void silent(std::span<const float> samples) {
    CHECK(std::all_of(samples.begin(), samples.end(), [](float value) { return value == 0.0F; }));
}

// Capture values rather than object padding, including every held key and all
// source phases. Musical control restore must leave this entire group alone.
struct RuntimeState {
    bool prepared{};
    std::uint64_t clock{};
    std::array<std::size_t, 3> counts{};
    std::array<std::array<bool, 61>, 2> keys{};
    std::array<std::uint64_t, 91> phases{};
    bool operator==(const RuntimeState&) const = default;
};

[[nodiscard]] RuntimeState runtime_of(const Engine& engine) {
    RuntimeState result;
    result.prepared = engine.prepared();
    result.clock = engine.frame_clock();
    result.counts = {engine.active_key_count(), engine.active_key_count(upper),
                     engine.active_key_count(lower)};
    for (std::size_t manual = 0; manual < 2; ++manual) {
        for (std::size_t key = 0; key < 61; ++key) {
            result.keys[manual][key] = engine.key_down(static_cast<Manual>(manual),
                                                       static_cast<std::uint32_t>(key) + 36);
        }
    }
    for (std::size_t source = 0; source < 91; ++source) {
        double phase = -19.0;
        CHECK(engine.source_phase_turns(static_cast<hammond::ToneId>(source + 1), phase) ==
              result.prepared);
        if (!result.prepared) CHECK(phase == -19.0);
        result.phases[source] = std::bit_cast<std::uint64_t>(phase);
    }
    return result;
}

struct FullState {
    RuntimeState runtime;
    ControlSnapshot controls;
    std::uint64_t expression_bits{};
    bool operator==(const FullState&) const = default;
};

[[nodiscard]] FullState state_of(const Engine& engine) {
    return {runtime_of(engine), engine.controls_snapshot(),
             std::bit_cast<std::uint64_t>(engine.expression())};
}

void check_controls(const Engine& engine, const ControlSnapshot& expected) {
    CHECK(engine.controls_snapshot() == expected);
    CHECK(engine.expression() == expected.expression);
    for (std::size_t manual = 0; manual < 2; ++manual) {
        const auto m = static_cast<Manual>(manual);
        DrawbarBank selected = static_cast<DrawbarBank>(255);
        bool enabled = !expected.route_enabled[manual];
        CHECK(engine.selected_bank(m, selected));
        CHECK(selected == expected.selected_banks[manual]);
        CHECK(engine.route_enabled(m, enabled));
        CHECK(enabled == expected.route_enabled[manual]);
        for (std::size_t bank = 0; bank < 2; ++bank) {
            for (std::size_t bar = 0; bar < 9; ++bar) {
                std::uint8_t position = 255;
                CHECK(engine.bank_drawbar_position(m, static_cast<DrawbarBank>(bank),
                                                   bar, position));
                CHECK(position == expected.drawbars[manual][bank][bar]);
                if (static_cast<DrawbarBank>(bank) == selected) {
                    position = 255;
                    CHECK(engine.drawbar_position(m, bar, position));
                    CHECK(position == expected.drawbars[manual][bank][bar]);
                }
            }
        }
    }
}

[[nodiscard]] std::vector<ControlSnapshot> invalid_snapshots() {
    auto otherwise_valid = registrations();
    otherwise_valid.selected_banks = {bank_a, bank_a};
    otherwise_valid.route_enabled = {false, true};
    otherwise_valid.expression = 0.25;
    std::vector<ControlSnapshot> result;
    for (std::size_t manual = 0; manual < 2; ++manual) {
        for (const auto invalid : {std::uint8_t{2}, std::uint8_t{255}}) {
            auto candidate = otherwise_valid;
            candidate.selected_banks[manual] = static_cast<DrawbarBank>(invalid);
            result.push_back(candidate);
        }
        for (std::size_t bank = 0; bank < 2; ++bank) {
            for (std::size_t bar = 0; bar < 9; ++bar) {
                for (const auto invalid : {std::uint8_t{9}, std::uint8_t{255}}) {
                    auto candidate = otherwise_valid;
                    candidate.drawbars[manual][bank][bar] = invalid;
                    result.push_back(candidate);
                }
            }
        }
    }
    for (std::size_t pedal = 0; pedal < hammond::kPedalDrawbarCount; ++pedal) {
        for (const auto invalid : {std::uint8_t{9}, std::uint8_t{255}}) {
            auto candidate = otherwise_valid;
            candidate.pedal_drawbars[pedal] = invalid;
            result.push_back(candidate);
        }
    }
    for (const double invalid : {-0.001, 1.001, std::numeric_limits<double>::infinity(),
                                 -std::numeric_limits<double>::infinity(),
                                 std::numeric_limits<double>::quiet_NaN()}) {
        auto candidate = otherwise_valid;
        candidate.expression = invalid;
        result.push_back(candidate);
    }
    return result;
}

void test_control_state_defaults_all_positions_and_ownership() {
    ControlState controls;
    const ControlSnapshot initial;
    CHECK(controls.snapshot() == initial);
    CHECK(initial.drawbars == hammond::AllDrawbarBanks{});
    CHECK(controls.expression() == 1.0);
    CHECK(hammond::is_valid_control_snapshot(initial));
    CHECK(hammond::is_valid_drawbar_bank(bank_a));
    CHECK(hammond::is_valid_drawbar_bank(bank_b));
    CHECK(!hammond::is_valid_drawbar_bank(static_cast<DrawbarBank>(2)));

    auto expected = initial;
    // Every legal value reaches every one of the 36 retained positions. Compare
    // the complete state after each write to catch aliasing between banks.
    for (std::size_t manual = 0; manual < 2; ++manual) {
        const auto m = static_cast<Manual>(manual);
        DrawbarBank selected = bank_a;
        bool enabled = false;
        CHECK(controls.selected_bank(m, selected));
        CHECK(selected == bank_b);
        CHECK(controls.route_enabled(m, enabled));
        CHECK(enabled);
        for (std::size_t bank = 0; bank < 2; ++bank) {
            for (std::size_t bar = 0; bar < 9; ++bar) {
                for (std::uint8_t position = 0; position < 9; ++position) {
                    CHECK(controls.set_bank_drawbar(m, static_cast<DrawbarBank>(bank), bar,
                                                    position));
                    expected.drawbars[manual][bank][bar] = position;
                    CHECK(controls.snapshot() == expected);
                    std::uint8_t observed = 255;
                    CHECK(controls.bank_drawbar_position(m, static_cast<DrawbarBank>(bank),
                                                         bar, observed));
                    CHECK(observed == position);
                }
            }
        }
    }

    auto source = registrations();
    CHECK(controls.restore(source));
    const auto retained = source;
    source.drawbars[0][1][8] = 8;
    source.expression = 0.0;
    CHECK(controls.snapshot() == retained);
    auto copied = controls.snapshot();
    copied.drawbars[1][0][7] = 0;
    copied.selected_banks[0] = bank_a;
    copied.route_enabled[0] = false;
    auto copied_banks = controls.drawbar_banks();
    copied_banks[0][0][0] = 0;
    CHECK(copied != retained);
    CHECK(copied_banks != retained.drawbars);
    CHECK(controls.snapshot() == retained);

    expected = retained;
    CHECK(controls.select_bank(upper, bank_a));
    expected.selected_banks[0] = bank_a;
    CHECK(controls.set_drawbar(upper, 8, 6));
    expected.drawbars[0][0][8] = 6;
    CHECK(controls.cancel(upper));
    CHECK(controls.cancel(upper)); // Accepted no-op.
    expected.route_enabled[0] = false;
    CHECK(controls.set_drawbar(upper, 0, 2));
    expected.drawbars[0][0][0] = 2;
    CHECK(controls.snapshot() == expected);
    std::uint8_t retained_position = 255;
    std::uint8_t active_position = 255;
    CHECK(controls.drawbar_position(upper, 0, retained_position));
    CHECK(retained_position == 2);
    CHECK(controls.active_drawbar_position(upper, 0, active_position));
    CHECK(active_position == 0);
    CHECK(controls.active_drawbar_position(lower, 0, active_position));
    CHECK(active_position == expected.drawbars[1][1][0]);
    CHECK(controls.select_bank(upper, bank_a)); // Same bank reconnects.
    expected.route_enabled[0] = true;
    CHECK(controls.snapshot() == expected);
    CHECK(controls.active_drawbar_position(upper, 0, active_position));
    CHECK(active_position == 2);
    for (double value : {0.0, 0.5, 1.0}) {
        CHECK(controls.set_expression(value));
        CHECK(controls.expression() == value);
    }
}

void test_control_state_validation_and_checked_getters() {
    ControlState controls;
    CHECK(controls.restore(registrations()));
    CHECK(controls.cancel(lower));
    const auto before = controls.snapshot();
    const auto preserved = [&] { CHECK(controls.snapshot() == before); };
    for (const auto invalid : {std::uint8_t{2}, std::uint8_t{255}}) {
        const auto manual = static_cast<Manual>(invalid);
        const auto bank = static_cast<DrawbarBank>(invalid);
        CHECK(!controls.set_bank_drawbar(manual, bank_a, 0, 8)); preserved();
        CHECK(!controls.set_bank_drawbar(upper, bank, 0, 8)); preserved();
        CHECK(!controls.set_drawbar(manual, 0, 8)); preserved();
        CHECK(!controls.select_bank(manual, bank_a)); preserved();
        CHECK(!controls.select_bank(upper, bank)); preserved();
        CHECK(!controls.cancel(manual)); preserved();
        std::uint8_t position = 217;
        CHECK(!controls.bank_drawbar_position(manual, bank_a, 0, position));
        CHECK(position == 217);
        CHECK(!controls.bank_drawbar_position(upper, bank, 0, position));
        CHECK(position == 217);
        CHECK(!controls.drawbar_position(manual, 0, position));
        CHECK(position == 217);
        CHECK(!controls.active_drawbar_position(manual, 0, position));
        CHECK(position == 217);
        DrawbarBank selected = static_cast<DrawbarBank>(217);
        CHECK(!controls.selected_bank(manual, selected));
        CHECK(selected == static_cast<DrawbarBank>(217));
        for (const bool initial : {false, true}) {
            bool enabled = initial;
            CHECK(!controls.route_enabled(manual, enabled));
            CHECK(enabled == initial);
        }
    }
    for (std::size_t index : {std::size_t{9}, std::numeric_limits<std::size_t>::max()}) {
        CHECK(!controls.set_bank_drawbar(upper, bank_a, index, 8)); preserved();
        CHECK(!controls.set_drawbar(lower, index, 8)); preserved();
        std::uint8_t position = 217;
        CHECK(!controls.bank_drawbar_position(lower, bank_b, index, position));
        CHECK(position == 217);
        CHECK(!controls.drawbar_position(upper, index, position));
        CHECK(position == 217);
        CHECK(!controls.active_drawbar_position(lower, index, position));
        CHECK(position == 217);
    }
    for (const auto position : {std::uint8_t{9}, std::uint8_t{255}}) {
        CHECK(!controls.set_bank_drawbar(lower, bank_a, 8, position)); preserved();
        CHECK(!controls.set_drawbar(upper, 8, position)); preserved();
    }
    for (const auto& candidate : invalid_snapshots()) {
        CHECK(!hammond::is_valid_control_snapshot(candidate));
        CHECK(!controls.restore(candidate)); preserved();
    }
    for (double value : {-0.001, 1.001, std::numeric_limits<double>::quiet_NaN(),
                         std::numeric_limits<double>::infinity(),
                         -std::numeric_limits<double>::infinity()}) {
        CHECK(!controls.set_expression(value)); preserved();
    }
}

void test_engine_defaults_and_checked_getters(const RuntimeProfile& profile) {
    Engine engine;
    const auto unprepared = state_of(engine);
    CHECK(!engine.restore_controls(registrations()));
    CHECK(state_of(engine) == unprepared);
    for (const bool prepare : {false, true}) {
        if (prepare) {
            engine = prepared_engine(profile);
            check_controls(engine, ControlSnapshot{});
        }
        const auto before = state_of(engine);
        std::uint8_t position = 219;
        DrawbarBank selected = static_cast<DrawbarBank>(219);
        if (!prepare) {
            CHECK(!engine.bank_drawbar_position(upper, bank_a, 0, position));
            CHECK(position == 219);
            CHECK(!engine.drawbar_position(upper, 0, position));
            CHECK(position == 219);
            CHECK(!engine.selected_bank(upper, selected));
            CHECK(selected == static_cast<DrawbarBank>(219));
            for (const bool initial : {false, true}) {
                bool enabled = initial;
                CHECK(!engine.route_enabled(upper, enabled));
                CHECK(enabled == initial);
            }
        }
        for (const auto invalid : {std::uint8_t{2}, std::uint8_t{255}}) {
            const auto manual = static_cast<Manual>(invalid);
            CHECK(!engine.bank_drawbar_position(manual, bank_a, 0, position));
            CHECK(position == 219);
            CHECK(!engine.bank_drawbar_position(lower, static_cast<DrawbarBank>(invalid),
                                                0, position));
            CHECK(position == 219);
            CHECK(!engine.drawbar_position(manual, 0, position));
            CHECK(position == 219);
            CHECK(!engine.selected_bank(manual, selected));
            CHECK(selected == static_cast<DrawbarBank>(219));
            for (const bool initial : {false, true}) {
                bool enabled = initial;
                CHECK(!engine.route_enabled(manual, enabled));
                CHECK(enabled == initial);
            }
        }
        for (std::size_t index : {std::size_t{9}, std::numeric_limits<std::size_t>::max()}) {
            CHECK(!engine.bank_drawbar_position(upper, bank_b, index, position));
            CHECK(position == 219);
            CHECK(!engine.drawbar_position(lower, index, position));
            CHECK(position == 219);
        }
        CHECK(state_of(engine) == before);
    }
}

void test_flattened_banks_hidden_edits_and_legacy_target(const RuntimeProfile& profile) {
    auto engine = prepared_engine(profile);
    auto reference = prepared_engine(profile);
    auto expected = registrations();
    const auto initial_runtime = runtime_of(engine);
    install_banks(engine, expected); // Direct indices 0..17 on both manuals.
    CHECK(runtime_of(engine) == initial_runtime);
    check_controls(engine, expected);
    apply_legacy_controls(reference, expected);
    hold_keys(engine);
    hold_keys(reference);
    std::array<float, 97> actual{};
    std::array<float, 97> wanted{};
    process_ok(engine, 97, actual);
    process_ok(reference, 97, wanted);
    same_audio(actual, wanted);
    audible(actual);

    const auto before_hidden_edit = runtime_of(engine);
    std::vector<Event> hidden;
    for (std::size_t manual = 0; manual < 2; ++manual) {
        for (std::size_t bar = 0; bar < 9; ++bar) {
            const auto position = static_cast<std::uint8_t>((manual + bar + 2) % 9);
            hidden.push_back(event(0, EventType::BankDrawbar, static_cast<Manual>(manual),
                                    static_cast<std::uint8_t>(bar), position));
            expected.drawbars[manual][0][bar] = position;
        }
    }
    process_ok(engine, 0, {}, hidden);
    CHECK(runtime_of(engine) == before_hidden_edit);
    check_controls(engine, expected);
    process_ok(engine, 97, actual);
    process_ok(reference, 97, wanted);
    same_audio(actual, wanted);
    CHECK(runtime_of(engine) == runtime_of(reference));

    // Reverse the active/hidden banks and exercise legacy Drawbar ownership on
    // different selections for the two manuals, without changing held keys.
    flush(engine, {select(0, upper, bank_a)});
    expected.selected_banks[0] = bank_a;
    flush(engine, {event(0, EventType::Drawbar, upper, 8, 6),
                   event(0, EventType::Drawbar, lower, 0, 2),
                   event(0, EventType::BankDrawbar, upper, 9, 8)});
    expected.drawbars[0][0][8] = 6;
    expected.drawbars[1][1][0] = 2;
    expected.drawbars[0][1][0] = 8;
    check_controls(engine, expected);
    apply_legacy_controls(reference, expected);
    process_ok(engine, 97, actual);
    process_ok(reference, 97, wanted);
    same_audio(actual, wanted);
    CHECK(runtime_of(engine) == runtime_of(reference));

    // An edit arriving in the middle of a sounding block must also stay hidden.
    const std::array edit{event(31, EventType::BankDrawbar, upper, 17, 8)};
    process_ok(engine, 97, actual, edit);
    process_ok(reference, 97, wanted);
    expected.drawbars[0][1][8] = 8;
    same_audio(actual, wanted);
    check_controls(engine, expected);
    CHECK(runtime_of(engine) == runtime_of(reference));
}

void test_held_key_switch_at_exact_sample(const RuntimeProfile& profile) {
    auto engine = prepared_engine(profile);
    auto reference = prepared_engine(profile);
    auto unchanged = prepared_engine(profile);
    auto expected = registrations();
    install_banks(engine, expected);
    apply_legacy_controls(reference, expected);
    apply_legacy_controls(unchanged, expected);
    hold_keys(engine); hold_keys(reference); hold_keys(unchanged);
    const auto before = runtime_of(engine);
    const std::array switches{select(17, upper, bank_a), select(34, lower, bank_a),
                              select(59, upper, bank_b), select(63, lower, bank_b)};
    std::vector<Event> legacy;
    append_legacy_registration(legacy, 17, upper, expected.drawbars[0][0]);
    append_legacy_registration(legacy, 34, lower, expected.drawbars[1][0]);
    append_legacy_registration(legacy, 59, upper, expected.drawbars[0][1]);
    append_legacy_registration(legacy, 63, lower, expected.drawbars[1][1]);
    std::array<float, 97> actual{}, wanted{}, unchanging{};
    process_ok(engine, 97, actual, switches);
    process_ok(reference, 97, wanted, legacy);
    process_ok(unchanged, 97, unchanging);
    same_audio(actual, wanted);
    same_audio(std::span<const float>(actual).first(17),
               std::span<const float>(unchanging).first(17));
    CHECK(actual[17] != unchanging[17]);
    CHECK(runtime_of(engine).keys == before.keys);
    CHECK(runtime_of(engine) == runtime_of(reference));
    CHECK(runtime_of(engine) == runtime_of(unchanged));
    check_controls(engine, expected);
}

void test_cancel_edits_reselect_and_panic(const RuntimeProfile& profile) {
    auto engine = prepared_engine(profile);
    auto reference = prepared_engine(profile);
    auto expected = registrations();
    install_banks(engine, expected);
    apply_legacy_controls(reference, expected);
    hold_keys(engine); hold_keys(reference);
    process_ok(engine, 43); process_ok(reference, 43);
    const auto before_cancel = runtime_of(engine);
    flush(engine, {event(0, EventType::Cancel, upper)});
    expected.route_enabled[0] = false;
    check_controls(engine, expected);
    CHECK(runtime_of(engine) == before_cancel);
    apply_legacy_controls(reference, expected);
    std::array<float, 89> actual{}, wanted{};
    process_ok(engine, 89, actual); process_ok(reference, 89, wanted);
    same_audio(actual, wanted);
    audible(actual); // Cancelling upper does not suppress lower.

    const auto before_lower_cancel = runtime_of(engine);
    flush(engine, {event(0, EventType::Cancel, lower)});
    expected.route_enabled[1] = false;
    check_controls(engine, expected);
    CHECK(runtime_of(engine) == before_lower_cancel);
    apply_legacy_controls(reference, expected);
    process_ok(engine, 89, actual); process_ok(reference, 89, wanted);
    silent(actual);
    same_audio(actual, wanted);
    CHECK(runtime_of(engine) == runtime_of(reference));
    CHECK(runtime_of(engine).phases != before_lower_cancel.phases);

    const auto before_edit = runtime_of(engine);
    flush(engine, {event(0, EventType::Drawbar, upper, 2, 3),
                   event(0, EventType::BankDrawbar, upper, 1, 8),
                   event(0, EventType::BankDrawbar, lower, 9, 4)});
    expected.drawbars[0][1][2] = 3;
    expected.drawbars[0][0][1] = 8;
    expected.drawbars[1][1][0] = 4;
    check_controls(engine, expected);
    CHECK(runtime_of(engine) == before_edit);
    process_ok(engine, 89, actual); process_ok(reference, 89, wanted);
    silent(actual);
    same_audio(actual, wanted);

    // Resume without note events; reference sources have advanced through the
    // same muted duration, so a phase reset or lost key changes the audio.
    const std::array reselect{select(11, upper, bank_b), select(47, lower, bank_a)};
    std::vector<Event> legacy;
    append_legacy_registration(legacy, 11, upper, expected.drawbars[0][1]);
    append_legacy_registration(legacy, 47, lower, expected.drawbars[1][0]);
    process_ok(engine, 89, actual, reselect); process_ok(reference, 89, wanted, legacy);
    same_audio(actual, wanted);
    silent(std::span<const float>(actual).first(11));
    CHECK(actual[11] != 0.0F);
    expected.route_enabled = {true, true};
    expected.selected_banks[1] = bank_a;
    check_controls(engine, expected);
    CHECK(engine.active_key_count() == 3);
    CHECK(runtime_of(engine) == runtime_of(reference));

    flush(engine, {event(0, EventType::Cancel, upper)});
    expected.route_enabled[0] = false;
    apply_legacy_controls(reference, expected);
    const auto before_panic = runtime_of(engine);
    flush(engine, {event(0, EventType::AllNotesOff, upper)});
    flush(reference, {event(0, EventType::AllNotesOff, upper)});
    check_controls(engine, expected);
    CHECK(engine.active_key_count(upper) == 0);
    CHECK(engine.active_key_count(lower) == 1);
    CHECK(engine.key_down(lower, 48));
    CHECK(runtime_of(engine).phases == before_panic.phases);
    CHECK(engine.frame_clock() == before_panic.clock);
    CHECK(runtime_of(engine).keys[1] == before_panic.keys[1]);
    flush(engine, {select(0, upper, bank_b)});
    expected.route_enabled[0] = true;
    apply_legacy_controls(reference, expected);
    process_ok(engine, 89, actual); process_ok(reference, 89, wanted);
    same_audio(actual, wanted); // Reselect cannot recreate panicked upper keys.
    audible(actual);
    flush(engine, {event(0, EventType::AllNotesOff, lower)});
    check_controls(engine, expected);
    CHECK(engine.active_key_count() == 0);
    process_ok(engine, 89, actual);
    silent(actual);
}

void test_engine_snapshot_restore_ownership_and_atomicity(const RuntimeProfile& profile) {
    auto engine = prepared_engine(profile);
    auto reference = prepared_engine(profile);
    auto old_controls = registrations();
    install_banks(engine, old_controls);
    apply_legacy_controls(reference, old_controls);
    hold_keys(engine); hold_keys(reference);
    process_ok(engine, 83); process_ok(reference, 83);
    const auto original = state_of(engine);
    auto returned_copy = engine.controls_snapshot();
    returned_copy.drawbars[0][1][8] = 8;
    returned_copy.expression = 0.0;
    returned_copy.route_enabled[0] = false;
    CHECK(returned_copy != old_controls);
    CHECK(state_of(engine) == original);

    auto candidate = registrations();
    candidate.selected_banks = {bank_a, bank_a};
    candidate.route_enabled = {true, false};
    candidate.drawbars[0][0][8] = 7;
    candidate.expression = 0.375;
    const auto expected = candidate;
    CHECK(engine.restore_controls(candidate));
    CHECK(runtime_of(engine) == original.runtime);
    check_controls(engine, expected);
    candidate.drawbars[0][0].fill(0);
    candidate.expression = 0.0;
    CHECK(engine.controls_snapshot() == expected);
    apply_legacy_controls(reference, expected);
    std::array<float, 73> actual{}, wanted{};
    process_ok(engine, 73, actual); process_ok(reference, 73, wanted);
    same_audio(actual, wanted);
    audible(actual);
    CHECK(runtime_of(engine) == runtime_of(reference));

    // A stale musical snapshot must not rewind a now-later DSP state.
    const auto later_runtime = runtime_of(engine);
    CHECK(engine.restore_controls(old_controls));
    CHECK(runtime_of(engine) == later_runtime);
    apply_legacy_controls(reference, old_controls);
    process_ok(engine, 73, actual); process_ok(reference, 73, wanted);
    same_audio(actual, wanted);
    for (const auto& invalid : invalid_snapshots()) {
        auto subject = engine;
        auto untouched = engine;
        const auto before = state_of(subject);
        CHECK(!subject.restore_controls(invalid));
        CHECK(state_of(subject) == before);
        process_ok(subject, 73, actual); process_ok(untouched, 73, wanted);
        same_audio(actual, wanted); // Also detects corrupted private gain caches.
        CHECK(state_of(subject) == state_of(untouched));
    }
}

[[nodiscard]] std::vector<Event> invalid_console_events() {
    std::vector<Event> events;
    for (const auto type : {EventType::BankDrawbar, EventType::SelectBank, EventType::Cancel}) {
        for (const auto invalid_manual : {std::uint8_t{2}, std::uint8_t{255}})
            events.push_back(event(0, type, static_cast<Manual>(invalid_manual)));
        for (const auto invalid_index : {std::uint8_t{18}, std::uint8_t{255}})
            events.push_back(event(0, type, upper, invalid_index));
        for (const double invalid : {-1.0, 0.5, 9.0,
                                     std::numeric_limits<double>::quiet_NaN(),
                                     std::numeric_limits<double>::infinity(),
                                     -std::numeric_limits<double>::infinity()})
            events.push_back(event(0, type, lower, 0, invalid));
    }
    events.push_back(event(0, EventType::SelectBank, upper, 1, 0));
    events.push_back(event(0, EventType::SelectBank, upper, 0, 2));
    events.push_back(event(0, EventType::Cancel, lower, 1, 0));
    events.push_back(event(0, EventType::Cancel, lower, 0, 1));
    return events;
}

void test_invalid_console_events_reject_whole_call(const RuntimeProfile& profile) {
    auto baseline = prepared_engine(profile);
    install_banks(baseline, registrations());
    hold_keys(baseline);
    flush(baseline, {select(0, upper, bank_a), event(0, EventType::Cancel, lower)});
    process_ok(baseline, 29);
    for (const auto invalid : invalid_console_events()) {
        for (const std::uint32_t frames : {0U, 17U}) {
            auto engine = baseline;
            auto reference = baseline;
            const auto before = state_of(engine);
            std::vector<Event> events{
                event(0, EventType::BankDrawbar, lower, 17, 8),
                select(0, lower, bank_a), event(0, EventType::NoteOff, upper, 36),
                event(0, EventType::Expression, upper, 0, 0.125),
                event(0, EventType::Cancel, upper), invalid};
            events.back().offset = frames == 0 ? 0 : frames - 1;
            std::array<float, 23> output;
            output.fill(sentinel);
            const auto rejected = engine.process(frames, output, events);
            CHECK(rejected.status == Status::InvalidEvent);
            CHECK(rejected.events_consumed == 0);
            CHECK(state_of(engine) == before);
            CHECK(std::all_of(output.begin(), output.end(),
                              [](float value) { return value == sentinel; }));
            std::array<float, 47> actual{}, wanted{};
            process_ok(engine, 47, actual); process_ok(reference, 47, wanted);
            same_audio(actual, wanted);
            CHECK(state_of(engine) == state_of(reference));
        }
    }
}

struct Timeline {
    std::vector<Event> console;
    std::vector<Event> legacy;
    ControlSnapshot final_controls;
};

[[nodiscard]] Timeline timeline() {
    Timeline result;
    auto& actual = result.console;
    auto& legacy = result.legacy;
    auto expected = registrations();
    append_banks(actual, expected);
    append_legacy_registration(legacy, 0, upper, expected.drawbars[0][1]);
    append_legacy_registration(legacy, 0, lower, expected.drawbars[1][1]);
    const auto both = [&](Event item) { actual.push_back(item); legacy.push_back(item); };
    both(event(0, EventType::Expression, upper, 0, expected.expression));
    both(event(0, EventType::NoteOn, upper, 36, 1));
    both(event(0, EventType::NoteOn, upper, 60, 127));
    both(event(0, EventType::NoteOn, lower, 48, 64));

    // Explicit expected registrations form an independently authored audible
    // timeline; no loop interprets console events into reference state.
    actual.push_back(event(1, EventType::BankDrawbar, upper, 2, 7));
    expected.drawbars[0][0][2] = 7;
    actual.push_back(select(16, upper, bank_a));
    append_legacy_registration(legacy, 16, upper, expected.drawbars[0][0]);
    actual.push_back(event(17, EventType::Cancel, upper));
    actual.push_back(select(17, upper, bank_b));
    append_legacy_registration(legacy, 17, upper, expected.drawbars[0][1]);
    actual.push_back(select(31, lower, bank_a));
    append_legacy_registration(legacy, 31, lower, expected.drawbars[1][0]);
    actual.push_back(select(64, upper, bank_a));
    actual.push_back(event(64, EventType::Cancel, upper));
    append_legacy_registration(legacy, 64, upper, silence);
    actual.push_back(event(65, EventType::BankDrawbar, lower, 13, 8));
    expected.drawbars[1][1][4] = 8;
    actual.push_back(event(127, EventType::Cancel, lower));
    append_legacy_registration(legacy, 127, lower, silence);
    actual.push_back(event(128, EventType::Drawbar, upper, 8, 3));
    expected.drawbars[0][0][8] = 3;
    actual.push_back(select(129, upper, bank_a));
    append_legacy_registration(legacy, 129, upper, expected.drawbars[0][0]);
    both(event(255, EventType::AllNotesOff, upper));
    both(event(256, EventType::NoteOn, upper, 60, 1));
    actual.push_back(select(257, lower, bank_b));
    append_legacy_registration(legacy, 257, lower, expected.drawbars[1][1]);
    actual.push_back(event(511, EventType::Cancel, upper));
    actual.push_back(event(511, EventType::Drawbar, upper, 0, 8));
    expected.drawbars[0][0][0] = 8;
    actual.push_back(select(511, upper, bank_a));
    append_legacy_registration(legacy, 511, upper, expected.drawbars[0][0]);
    actual.push_back(select(512, lower, bank_a));
    actual.push_back(event(512, EventType::Cancel, lower));
    append_legacy_registration(legacy, 512, lower, silence);
    both(event(513, EventType::AllNotesOff, lower));
    both(event(777, EventType::Expression, upper, 0, 0.25));
    expected.expression = 0.25;
    both(event(1023, EventType::NoteOn, lower, 36, 127));
    actual.push_back(select(1024, lower, bank_a));
    append_legacy_registration(legacy, 1024, lower, expected.drawbars[1][0]);
    actual.push_back(select(1025, upper, bank_b));
    append_legacy_registration(legacy, 1025, upper, expected.drawbars[0][1]);
    actual.push_back(event(1555, EventType::Cancel, upper));
    actual.push_back(event(1555, EventType::Cancel, lower));
    append_legacy_registration(legacy, 1555, upper, silence);
    append_legacy_registration(legacy, 1555, lower, silence);
    actual.push_back(event(1556, EventType::BankDrawbar, upper, 12, 8));
    expected.drawbars[0][1][3] = 8;
    actual.push_back(select(1700, upper, bank_b));
    append_legacy_registration(legacy, 1700, upper, expected.drawbars[0][1]);
    actual.push_back(select(2017, lower, bank_b));
    append_legacy_registration(legacy, 2017, lower, expected.drawbars[1][1]);
    both(event(2052, EventType::AllNotesOff, upper));
    both(event(2053, EventType::NoteOn, upper, 61, 17));
    actual.push_back(event(2112, EventType::Cancel, upper));
    actual.push_back(select(2112, upper, bank_a));
    actual.push_back(select(2112, lower, bank_a));
    actual.push_back(event(2112, EventType::Cancel, lower));
    append_legacy_registration(legacy, 2112, upper, expected.drawbars[0][0]);
    append_legacy_registration(legacy, 2112, lower, silence);
    expected.selected_banks = {bank_a, bank_a};
    expected.route_enabled = {true, false};
    result.final_controls = expected;
    return result;
}

struct Rendered {
    std::vector<float> audio;
    Engine engine;
};

[[nodiscard]] Rendered render(const RuntimeProfile& profile, double rate,
                              std::span<const Event> events, std::uint32_t partition) {
    constexpr std::uint32_t frames = 2113;
    Rendered result{std::vector<float>(frames, sentinel), prepared_engine(profile, rate)};
    std::size_t event_cursor = 0;
    for (std::uint32_t cursor = 0; cursor < frames;) {
        const auto count = std::min(partition, frames - cursor);
        std::vector<Event> block_events;
        while (event_cursor < events.size() && events[event_cursor].offset < cursor + count) {
            auto relative = events[event_cursor++];
            CHECK(relative.offset >= cursor);
            relative.offset -= cursor;
            block_events.push_back(relative);
        }
        process_ok(result.engine, count, std::span<float>(result.audio).subspan(cursor, count),
                    block_events);
        cursor += count;
    }
    CHECK(event_cursor == events.size());
    return result;
}

void test_partition_invariance_same_frame_order_and_velocity(const RuntimeProfile& profile) {
    const auto fixture = timeline();
    for (const double rate : {44100.0, 48000.0, 96000.0}) {
        const auto reference = render(profile, rate, fixture.legacy, 53);
        const auto baseline = render(profile, rate, fixture.console, 1024);
        same_audio(baseline.audio, reference.audio);
        check_controls(baseline.engine, fixture.final_controls);
        CHECK(runtime_of(baseline.engine) == runtime_of(reference.engine));
        CHECK(baseline.engine.active_key_count() == 2);
        CHECK(baseline.engine.key_down(upper, 61));
        CHECK(baseline.engine.key_down(lower, 36));
        CHECK(baseline.engine.frame_clock() == clock_origin + 2113);
        // The fixed timeline has audible and silent intervals, including edits
        // while cancelled and both possible same-frame Cancel/select orders.
        audible(std::span<const float>(baseline.audio).subspan(17, 14));
        silent(std::span<const float>(baseline.audio).subspan(127, 2));
        silent(std::span<const float>(baseline.audio).subspan(1555, 145));
        CHECK(baseline.audio[1700] != 0.0F);
        CHECK(baseline.audio[2112] != 0.0F);
        for (const std::uint32_t partition : {1U, 17U, 64U, 127U, 511U}) {
            const auto actual = render(profile, rate, fixture.console, partition);
            same_audio(actual.audio, baseline.audio);
            CHECK(state_of(actual.engine) == state_of(baseline.engine));
        }
        auto low_velocity = fixture.console;
        auto high_velocity = fixture.console;
        for (auto& item : low_velocity)
            if (item.type == EventType::NoteOn) item.value = 1;
        for (auto& item : high_velocity)
            if (item.type == EventType::NoteOn) item.value = 127;
        const auto soft = render(profile, rate, low_velocity, 64);
        const auto hard = render(profile, rate, high_velocity, 127);
        same_audio(soft.audio, hard.audio);
        same_audio(soft.audio, baseline.audio);
        CHECK(state_of(soft.engine) == state_of(hard.engine));
    }
}

} // namespace

int main() {
    const auto profile = load_test_profile();
    test_control_state_defaults_all_positions_and_ownership();
    test_control_state_validation_and_checked_getters();
    test_engine_defaults_and_checked_getters(profile);
    test_flattened_banks_hidden_edits_and_legacy_target(profile);
    test_held_key_switch_at_exact_sample(profile);
    test_cancel_edits_reselect_and_panic(profile);
    test_engine_snapshot_restore_ownership_and_atomicity(profile);
    test_invalid_console_events_reject_whole_call(profile);
    test_partition_invariance_same_frame_order_and_velocity(profile);
    return 0;
}
