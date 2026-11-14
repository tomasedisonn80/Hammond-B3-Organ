#include "PresetTestOracle.h"
#include "TestSupport.h"
#include "hammond/Engine.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <initializer_list>
#include <limits>
#include <span>
#include <vector>

namespace {

using namespace hammond;

constexpr Manual upper = Manual::Upper;
constexpr Manual lower = Manual::Lower;
constexpr std::uint64_t origin = 7000000019ULL;
constexpr std::uint32_t max_block = 4096;
constexpr float sentinel = -731.25F;
std::size_t row_audio_cases = 0;
std::size_t rejected_calls = 0;

static_assert(static_cast<unsigned>(EventType::NoteOn) == 0);
static_assert(static_cast<unsigned>(EventType::PedalAllNotesOff) == 13);
static_assert(static_cast<unsigned>(EventType::SelectPreset) == 14);
static_assert(static_cast<unsigned>(PresetSelection::A) == 9);
static_assert(static_cast<unsigned>(PresetSelection::BankA) == 10);

Event event(std::uint32_t offset, EventType type, Manual manual,
            std::uint8_t index = 0, double value = 0.0) {
    return {offset, type, manual, index, value};
}

Event preset(std::uint32_t offset, Manual manual, PresetSelection selection) {
    return event(offset, EventType::SelectPreset, manual, 0,
                 static_cast<double>(static_cast<std::uint8_t>(selection)));
}

Event bank(std::uint32_t offset, Manual manual, DrawbarBank selection) {
    return event(offset, EventType::SelectBank, manual, 0,
                 static_cast<double>(static_cast<std::uint8_t>(selection)));
}

void process(Engine& engine, std::uint32_t frames, std::span<float> output = {},
             std::span<const Event> events = {}) {
    const auto result = engine.process(frames, output, events);
    CHECK(result.status == Status::Ok);
    CHECK(result.events_consumed == events.size());
}

void flush(Engine& engine, std::initializer_list<Event> events) {
    process(engine, 0, {}, {events.begin(), events.size()});
}

Engine prepared(const RuntimeProfile& profile, double rate = 48000.0, bool travel = false) {
    Engine engine;
    CHECK(engine.prepare(profile, ProcessSpec{rate, max_block, 0x72591U, origin},
                         travel ? make_nominal_console_model() : make_legacy_console_model())
          == Status::Ok);
    return engine;
}

ControlSnapshot retained_controls() {
    ControlSnapshot controls;
    controls.drawbars[0][0] = {8, 0, 6, 0, 4, 0, 2, 0, 1};
    controls.drawbars[0][1] = {0, 7, 0, 5, 0, 3, 0, 1, 8};
    controls.drawbars[1][0] = {1, 2, 3, 4, 5, 6, 7, 8, 0};
    controls.drawbars[1][1] = {8, 7, 6, 5, 4, 3, 2, 1, 0};
    controls.expression = 0.625;
    controls.pedal_drawbars = {4, 7};
    return controls;
}

// Every reference registration comes from A10's literal page-122 fixture.
// Production lookup/generation is deliberately absent from the audio oracle.
DrawbarPositions literal_row(std::size_t manual, std::size_t row) {
    DrawbarPositions result{};
    for (std::size_t bar = 0; bar < result.size(); ++bar) {
        result[bar] = preset_test_oracle::kPositions[manual][row][bar];
    }
    return result;
}

void hold_chords(Engine& engine) {
    for (const auto manual : {upper, lower}) {
        for (const auto note : {36, 37, 48, 60, 84, 95, 96}) {
            flush(engine, {event(0, EventType::NoteOn, manual,
                                 static_cast<std::uint8_t>(note), 96)});
        }
    }
    flush(engine, {event(0, EventType::PedalOn, lower, 1, 127),
                   event(0, EventType::PedalOn, lower, 25, 64)});
}

void same_audio(std::span<const float> left, std::span<const float> right) {
    CHECK(left.size() == right.size());
    for (std::size_t frame = 0; frame < left.size(); ++frame) {
        CHECK(std::bit_cast<std::uint32_t>(left[frame]) ==
              std::bit_cast<std::uint32_t>(right[frame]));
    }
}

void audible(std::span<const float> output) {
    CHECK(std::any_of(output.begin(), output.end(), [](float sample) { return sample != 0.0F; }));
}

struct Histories {
    std::uint64_t clock{};
    std::uint64_t rate{};
    std::uint64_t readiness{};
    std::array<std::uint64_t, kToneSourceCount> phases{};
    std::array<std::array<ContactKeySnapshot, kManualKeyCount>, kManualCount> contacts{};
    std::array<std::array<bool, kManualKeyCount>, kManualCount> keys{};
    std::array<bool, kPedalCount> pedals{};
    PedalContactStates pedal_contacts{};
    PedalRenderDiagnostics last_pedal{};
    bool operator==(const Histories&) const = default;
};

Histories histories(const Engine& engine) {
    Histories result;
    result.clock = engine.frame_clock();
    result.rate = std::bit_cast<std::uint64_t>(engine.sample_rate());
    result.readiness = std::bit_cast<std::uint64_t>(engine.percussion_diagnostics().readiness);
    for (std::size_t tone = 0; tone < kToneSourceCount; ++tone) {
        double phase = -1.0;
        CHECK(engine.source_phase_turns(static_cast<ToneId>(tone + 1), phase));
        result.phases[tone] = std::bit_cast<std::uint64_t>(phase);
    }
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        for (std::size_t key = 0; key < kManualKeyCount; ++key) {
            const auto note = static_cast<std::uint32_t>(key) + kMinManualMidiNote;
            CHECK(engine.contact_snapshot(static_cast<Manual>(manual), note,
                                           result.contacts[manual][key]));
            result.keys[manual][key] = engine.key_down(static_cast<Manual>(manual), note);
        }
    }
    for (std::size_t pedal = 0; pedal < kPedalCount; ++pedal) {
        result.pedals[pedal] = engine.pedal_down(PedalId{static_cast<std::uint8_t>(pedal + 1)});
    }
    CHECK(engine.pedal_contacts_snapshot(result.pedal_contacts));
    result.last_pedal = engine.last_pedal_frame();
    return result;
}

void same_future(Engine left, Engine right) {
    std::array<float, 257> a{}, b{};
    process(left, 257, a);
    process(right, 257, b);
    same_audio(a, b);
    CHECK(histories(left) == histories(right));
    CHECK(left.controls_snapshot() == right.controls_snapshot());
    CHECK(left.percussion_diagnostics() == right.percussion_diagnostics());
}

void check_selection(const Engine& engine, Manual manual, PresetSelection expected) {
    auto selected = static_cast<PresetSelection>(255);
    CHECK(engine.selected_preset(manual, selected));
    CHECK(selected == expected);
}

void test_control_domains_and_transitions() {
    ControlState controls;
    CHECK(controls.snapshot().fixed_registrations ==
          (std::array{FixedRegistration::None, FixedRegistration::None}));
    // All 100 retained mode pairs, both remembered banks, and all route bits.
    for (unsigned upper_mode = 0; upper_mode < 10; ++upper_mode) {
        for (unsigned lower_mode = 0; lower_mode < 10; ++lower_mode) {
            for (unsigned bits = 0; bits < 16; ++bits) {
                auto expected = retained_controls();
                expected.fixed_registrations = {static_cast<FixedRegistration>(upper_mode),
                                                 static_cast<FixedRegistration>(lower_mode)};
                expected.selected_banks = {static_cast<DrawbarBank>(bits & 1U),
                                            static_cast<DrawbarBank>((bits >> 1U) & 1U)};
                expected.route_enabled = {(bits & 4U) != 0, (bits & 8U) != 0};
                CHECK(is_valid_control_snapshot(expected));
                CHECK(controls.restore(expected));
                CHECK(controls.snapshot() == expected);
                for (std::size_t m = 0; m < 2; ++m) {
                    const auto manual = static_cast<Manual>(m);
                    const auto mode = static_cast<unsigned>(expected.fixed_registrations[m]);
                    const auto bank_index = static_cast<std::size_t>(expected.selected_banks[m]);
                    const auto selection = !expected.route_enabled[m] ? PresetSelection::Cancel :
                        (mode != 0 ? static_cast<PresetSelection>(mode) :
                         (bank_index == 0 ? PresetSelection::BankA : PresetSelection::BankB));
                    auto actual = static_cast<PresetSelection>(255);
                    CHECK(control_preset_selection(expected, manual, actual));
                    CHECK(actual == selection);
                    CHECK(controls.selected_preset(manual, actual));
                    CHECK(actual == selection);
                    for (std::size_t bar = 0; bar < kDrawbarCount; ++bar) {
                        std::uint8_t active = 255, remembered = 255;
                        CHECK(controls.active_drawbar_position(manual, bar, active));
                        const auto wanted = !expected.route_enabled[m] ? std::uint8_t{0} :
                            (mode != 0 ? preset_test_oracle::kPositions[m][mode - 1][bar] :
                             expected.drawbars[m][bank_index][bar]);
                        CHECK(active == wanted);
                        CHECK(controls.drawbar_position(manual, bar, remembered));
                        CHECK(remembered == expected.drawbars[m][bank_index][bar]);
                    }
                }
            }
        }
    }

    // Every action from every retained mode/bank/route on either manual.
    for (std::size_t m = 0; m < 2; ++m) {
        const auto manual = static_cast<Manual>(m);
        for (unsigned mode = 0; mode < 10; ++mode) {
            for (unsigned bits = 0; bits < 4; ++bits) {
                for (unsigned selected = 0; selected < 12; ++selected) {
                    auto expected = retained_controls();
                    expected.percussion.enabled = true;
                    expected.fixed_registrations = {FixedRegistration::F, FixedRegistration::G};
                    expected.fixed_registrations[m] = static_cast<FixedRegistration>(mode);
                    expected.selected_banks[m] = static_cast<DrawbarBank>(bits & 1U);
                    expected.route_enabled[m] = (bits & 2U) != 0;
                    CHECK(controls.restore(expected));
                    CHECK(controls.select_preset(manual, static_cast<PresetSelection>(selected)));
                    expected.route_enabled[m] = selected != 0;
                    if (selected >= 10) {
                        expected.fixed_registrations[m] = FixedRegistration::None;
                        expected.selected_banks[m] = selected == 10 ? DrawbarBank::A : DrawbarBank::B;
                    } else if (selected != 0) {
                        expected.fixed_registrations[m] = static_cast<FixedRegistration>(selected);
                    }
                    CHECK(controls.snapshot() == expected);
                    CHECK(controls.select_preset(manual, static_cast<PresetSelection>(selected)));
                    CHECK(controls.snapshot() == expected);
                }
            }
        }
    }

    auto valid = retained_controls();
    valid.fixed_registrations = {FixedRegistration::A, FixedRegistration::CSharp};
    valid.route_enabled = {false, false};
    CHECK(controls.restore(valid));
    for (std::size_t m = 0; m < 2; ++m) {
        for (unsigned raw = 10; raw < 256; ++raw) {
            auto invalid = valid;
            invalid.fixed_registrations[m] = static_cast<FixedRegistration>(raw);
            CHECK(!is_valid_control_snapshot(invalid));
            CHECK(!controls.restore(invalid));
            CHECK(controls.snapshot() == valid);
            // Validation includes the other manual, even when both are cancelled.
            auto destination = PresetSelection::DSharp;
            CHECK(!control_preset_selection(invalid, static_cast<Manual>(1 - m), destination));
            CHECK(destination == PresetSelection::DSharp);
        }
        for (unsigned raw = 12; raw < 256; ++raw) {
            CHECK(!controls.select_preset(static_cast<Manual>(m), static_cast<PresetSelection>(raw)));
            CHECK(controls.snapshot() == valid);
        }
    }
    for (unsigned mutation = 0; mutation < 5; ++mutation) {
        auto invalid = valid;
        if (mutation == 0) invalid.expression = std::numeric_limits<double>::quiet_NaN();
        if (mutation == 1) invalid.pedal_drawbars[1] = 9;
        if (mutation == 2) invalid.drawbars[1][0][8] = 9;
        if (mutation == 3) invalid.selected_banks[1] = static_cast<DrawbarBank>(2);
        if (mutation == 4) invalid.percussion.harmonic = static_cast<PercussionHarmonic>(2);
        auto destination = PresetSelection::DSharp;
        CHECK(!control_preset_selection(invalid, upper, destination));
        CHECK(destination == PresetSelection::DSharp);
    }
    for (const auto raw : {2, 255}) {
        const auto invalid = static_cast<Manual>(raw);
        auto destination = PresetSelection::G;
        CHECK(!controls.selected_preset(invalid, destination));
        CHECK(!control_preset_selection(valid, invalid, destination));
        CHECK(destination == PresetSelection::G);
        CHECK(!controls.select_preset(invalid, PresetSelection::BankA));
        CHECK(controls.snapshot() == valid);
    }
    std::uint8_t position = 217;
    CHECK(!controls.active_drawbar_position(upper, kDrawbarCount, position));
    CHECK(!controls.active_drawbar_position(static_cast<Manual>(255), 0, position));
    CHECK(position == 217);
    Engine unprepared;
    auto destination = PresetSelection::G;
    CHECK(!unprepared.selected_preset(upper, destination));
    CHECK(destination == PresetSelection::G);
}

void test_all_literal_rows_at_continuing_phase(const RuntimeProfile& profile) {
    for (const auto rate : {44100.0, 48000.0, 96000.0}) {
        for (const bool travel : {false, true}) {
            for (std::size_t m = 0; m < 2; ++m) {
                for (std::size_t row = 0; row < 9; ++row) {
                    auto actual = prepared(profile, rate, travel);
                    auto expected = prepared(profile, rate, travel);
                    const auto retained = retained_controls();
                    auto reference_controls = retained;
                    reference_controls.drawbars[m][0] = literal_row(m, row);
                    CHECK(actual.restore_controls(retained));
                    CHECK(expected.restore_controls(reference_controls));
                    hold_chords(actual);
                    hold_chords(expected);
                    // At the first selection, travel contacts are still moving.
                    process(actual, 137);
                    process(expected, 137);
                    CHECK(histories(actual) == histories(expected));
                    const auto selection = static_cast<PresetSelection>(row + 1);
                    const std::array actual_events{preset(19, static_cast<Manual>(m), selection)};
                    const std::array reference_events{bank(19, static_cast<Manual>(m), DrawbarBank::A)};
                    std::array<float, 257> a{}, b{};
                    process(actual, 257, a, actual_events);
                    process(expected, 257, b, reference_events);
                    same_audio(a, b);
                    audible(a);
                    std::array<float, 513> later_a{}, later_b{};
                    process(actual, 513, later_a);
                    process(expected, 513, later_b);
                    same_audio(later_a, later_b);
                    CHECK(histories(actual) == histories(expected));
                    CHECK(actual.controls_snapshot().drawbars == retained.drawbars);
                    CHECK(actual.controls_snapshot().selected_banks[m] == DrawbarBank::B);
                    check_selection(actual, static_cast<Manual>(m), selection);
                    ++row_audio_cases;
                }
            }
        }
    }
}

void test_remembered_bank_edits_and_old_selection(const RuntimeProfile& profile) {
    auto actual = prepared(profile);
    auto controls = retained_controls();
    controls.fixed_registrations = {FixedRegistration::E, FixedRegistration::A};
    CHECK(actual.restore_controls(controls));
    hold_chords(actual);
    process(actual, 127);
    auto unchanged = actual;
    const std::array edits{
        event(0, EventType::Drawbar, upper, 8, 5),
        event(17, EventType::BankDrawbar, upper, 0, 2),
        event(31, EventType::Drawbar, lower, 2, 8),
        event(63, EventType::BankDrawbar, lower, 2, 7)};
    controls.drawbars[0][1][8] = 5;
    controls.drawbars[0][0][0] = 2;
    controls.drawbars[1][1][2] = 8;
    controls.drawbars[1][0][2] = 7;
    std::array<float, 257> a{}, b{};
    process(actual, 257, a, edits);
    process(unchanged, 257, b);
    same_audio(a, b);
    CHECK(actual.controls_snapshot() == controls);
    CHECK(histories(actual) == histories(unchanged));
    for (std::size_t m = 0; m < 2; ++m) {
        for (std::size_t selected = 0; selected < 2; ++selected) {
            auto selected_engine = actual;
            auto cancelled_engine = actual;
            auto reference = actual;
            auto reference_controls = controls;
            reference_controls.fixed_registrations[m] = FixedRegistration::None;
            reference_controls.selected_banks[m] = DrawbarBank::A;
            reference_controls.drawbars[m][0] = controls.drawbars[m][selected];
            CHECK(reference.restore_controls(reference_controls));
            flush(selected_engine, {bank(0, static_cast<Manual>(m), static_cast<DrawbarBank>(selected))});
            flush(cancelled_engine, {event(0, EventType::Cancel, static_cast<Manual>(m))});
            CHECK(cancelled_engine.controls_snapshot().fixed_registrations[m] == controls.fixed_registrations[m]);
            flush(cancelled_engine, {bank(0, static_cast<Manual>(m), static_cast<DrawbarBank>(selected))});
            CHECK(cancelled_engine.controls_snapshot() == selected_engine.controls_snapshot());
            CHECK(histories(cancelled_engine) == histories(selected_engine));
            check_selection(selected_engine, static_cast<Manual>(m),
                            selected == 0 ? PresetSelection::BankA : PresetSelection::BankB);
            CHECK(selected_engine.controls_snapshot().fixed_registrations[m] == FixedRegistration::None);
            CHECK(selected_engine.controls_snapshot().drawbars == controls.drawbars);
            process(selected_engine, 257, a);
            process(reference, 257, b);
            same_audio(a, b);
            process(cancelled_engine, 257, b);
            same_audio(a, b);
        }
    }
}

void test_zero_time_cancel_restore_and_partial_contacts(const RuntimeProfile& profile) {
    auto actual = prepared(profile, 48000.0, true);
    auto controls = retained_controls();
    controls.percussion.enabled = true;
    CHECK(actual.restore_controls(controls));
    hold_chords(actual);
    process(actual, 1024);
    flush(actual, {event(0, EventType::KeyPosition, upper, 60, 0.55),
                    event(0, EventType::KeyPosition, lower, 96, 0.43)});
    process(actual, 97);
    ContactKeySnapshot partial;
    CHECK(actual.contact_snapshot(upper, 60, partial));
    CHECK(partial.position > partial.target && partial.position < 1.0);
    const auto before = histories(actual);
    CHECK(actual.percussion_diagnostics().readiness < 1.0);
    flush(actual, {preset(0, upper, PresetSelection::E),
                    preset(0, lower, PresetSelection::A)});
    CHECK(histories(actual) == before);
    CHECK(!actual.percussion_diagnostics().eligible);
    CHECK(actual.percussion_diagnostics().upper_sustain_gain == 1.0);
    const auto fixed = actual.controls_snapshot();
    flush(actual, {event(0, EventType::Cancel, upper)});
    auto cancelled = fixed;
    cancelled.route_enabled[0] = false;
    CHECK(actual.controls_snapshot() == cancelled);
    CHECK(histories(actual) == before);
    check_selection(actual, upper, PresetSelection::Cancel);
    flush(actual, {preset(0, upper, PresetSelection::Cancel),
                    event(0, EventType::Drawbar, upper, 0, 8)});
    cancelled.drawbars[0][1][0] = 8;
    CHECK(actual.controls_snapshot() == cancelled);
    CHECK(histories(actual) == before);

    // Independently silence upper sustain with an empty ineligible bank. Lower
    // fixed sound and both held pedals must still reach the same output.
    auto reference = actual;
    auto reference_controls = cancelled;
    reference_controls.route_enabled[0] = true;
    reference_controls.fixed_registrations[0] = FixedRegistration::None;
    reference_controls.selected_banks[0] = DrawbarBank::A;
    reference_controls.drawbars[0][0] = {};
    CHECK(reference.restore_controls(reference_controls));
    std::array<float, 257> a{}, b{};
    process(actual, 257, a);
    process(reference, 257, b);
    same_audio(a, b);
    audible(a);
    CHECK(histories(actual) == histories(reference));
    CHECK(actual.controls_snapshot().fixed_registrations[0] == FixedRegistration::E);
    CHECK(actual.active_key_count() == 14);
    CHECK(actual.active_pedal_count() == 2);

    const auto after_cancel = histories(actual);
    auto restored = actual.controls_snapshot();
    restored.fixed_registrations = {FixedRegistration::GSharp, FixedRegistration::CSharp};
    restored.route_enabled = {true, true};
    CHECK(actual.restore_controls(restored));
    CHECK(histories(actual) == after_cancel);
    check_selection(actual, upper, PresetSelection::GSharp);
    CHECK(!actual.percussion_diagnostics().eligible);
    auto invalid_manual_destination = PresetSelection::D;
    CHECK(!actual.selected_preset(static_cast<Manual>(255), invalid_manual_destination));
    CHECK(invalid_manual_destination == PresetSelection::D);
    flush(actual, {event(0, EventType::SelectPreset, upper, 0, -0.0)});
    check_selection(actual, upper, PresetSelection::Cancel);
    CHECK(actual.controls_snapshot().fixed_registrations[0] == FixedRegistration::GSharp);
    CHECK(histories(actual) == after_cancel);
}

void test_fixed_percussion_exclusion_and_readiness(const RuntimeProfile& profile) {
    for (const auto rate : {44100.0, 48000.0, 96000.0}) {
        auto baseline = prepared(profile, rate);
        auto controls = retained_controls();
        controls.drawbars[1] = {};
        controls.pedal_drawbars = {};
        controls.percussion.enabled = true;
        controls.percussion.decay = PercussionDecay::Fast;
        CHECK(baseline.restore_controls(controls));
        flush(baseline, {event(0, EventType::NoteOn, upper, 36, 127),
                         event(0, EventType::NoteOn, upper, 60, 127),
                         event(0, EventType::NoteOn, upper, 96, 127)});
        process(baseline, 1024);
        const auto percussion = make_nominal_percussion_profile();
        const double held_q = baseline.percussion_diagnostics().readiness;
        const auto decay_expected = std::exp(-1024.0L /
            (static_cast<long double>(rate) * percussion.fast_decay_seconds));
        CHECK_NEAR(held_q, decay_expected, 2.0e-12L);
        CHECK(held_q < 1.0 && held_q > 0.0);
        for (std::size_t row = 0; row < 9; ++row) {
            auto actual = baseline;
            auto reference = baseline;
            auto reference_controls = controls;
            reference_controls.selected_banks[0] = DrawbarBank::A;
            reference_controls.drawbars[0][0] = literal_row(0, row);
            reference_controls.percussion.enabled = false;
            CHECK(reference.restore_controls(reference_controls));
            flush(actual, {preset(0, upper, static_cast<PresetSelection>(row + 1))});
            const auto diagnostic = actual.percussion_diagnostics();
            CHECK(diagnostic.physical_detector && !diagnostic.eligible && !diagnostic.routed_detector);
            CHECK(diagnostic.gain == 0.0 && diagnostic.upper_sustain_gain == 1.0);
            CHECK(diagnostic.readiness == held_q);
            std::array<float, 257> a{}, b{};
            process(actual, 257, a);
            process(reference, 257, b);
            same_audio(a, b); // Includes all fixed 1-foot taps and uncompensated sustain.
            CHECK(histories(actual) == histories(reference));
            const auto recovery_expected = 1.0L - (1.0L - held_q) * std::exp(-257.0L /
                (static_cast<long double>(rate) * percussion.recovery_seconds));
            CHECK_NEAR(actual.percussion_diagnostics().readiness, recovery_expected, 2.0e-12L);
            const auto recovered = histories(actual);
            flush(actual, {bank(0, upper, DrawbarBank::B)}); // B was still remembered.
            CHECK(histories(actual) == recovered);
            CHECK(actual.percussion_diagnostics().eligible);
            CHECK(actual.percussion_diagnostics().readiness > held_q);
            CHECK(actual.percussion_diagnostics().readiness < 1.0);
            reference_controls.selected_banks[0] = DrawbarBank::B;
            reference_controls.percussion.enabled = true;
            CHECK(reference.restore_controls(reference_controls));
            process(actual, 257, a);
            process(reference, 257, b);
            same_audio(a, b);
            CHECK(histories(actual) == histories(reference));
        }

        auto no_elapsed = baseline;
        const auto before = histories(no_elapsed);
        flush(no_elapsed, {preset(0, upper, PresetSelection::BankB),
                            preset(0, upper, PresetSelection::E),
                            bank(0, upper, DrawbarBank::B)});
        CHECK(histories(no_elapsed) == before);
        CHECK(no_elapsed.controls_snapshot() == baseline.controls_snapshot());
        same_future(no_elapsed, baseline);
        const std::array tied{preset(47, upper, PresetSelection::E),
                               bank(47, upper, DrawbarBank::B)};
        std::array<float, 257> a{}, b{};
        process(no_elapsed, 257, a, tied);
        process(baseline, 257, b);
        same_audio(a, b);
        CHECK(histories(no_elapsed) == histories(baseline));

        auto reversed = baseline;
        auto direct_fixed = baseline;
        const std::array reverse_tie{bank(47, upper, DrawbarBank::B),
                                     preset(47, upper, PresetSelection::E)};
        const std::array fixed_only{preset(47, upper, PresetSelection::E)};
        process(reversed, 257, a, reverse_tie);
        process(direct_fixed, 257, b, fixed_only);
        same_audio(a, b);
        check_selection(reversed, upper, PresetSelection::E);
        CHECK(histories(reversed) == histories(direct_fixed));

        auto lower_only = baseline;
        flush(lower_only, {preset(0, lower, PresetSelection::A)});
        CHECK(lower_only.percussion_diagnostics() == baseline.percussion_diagnostics());
        process(lower_only, 257, a);
        process(baseline, 257, b);
        same_audio(a, b); // No lower note: upper audio/history must be unchanged.
        CHECK(histories(lower_only) == histories(baseline));
    }
}

void test_rejected_calls_preserve_future(const RuntimeProfile& profile) {
    auto baseline = prepared(profile, 48000.0, true);
    auto controls = retained_controls();
    controls.percussion.enabled = true;
    CHECK(baseline.restore_controls(controls));
    hold_chords(baseline);
    process(baseline, 1024);
    flush(baseline, {preset(0, upper, PresetSelection::E),
                     preset(0, lower, PresetSelection::A),
                     event(0, EventType::KeyPosition, upper, 60, 0.53)});
    process(baseline, 71);
    std::vector<Event> invalid;
    for (const double value : {-1.0, 12.0, 255.0, 0.5, 10.5,
                              std::numeric_limits<double>::denorm_min(),
                              std::numeric_limits<double>::infinity(),
                              -std::numeric_limits<double>::infinity(),
                              std::numeric_limits<double>::quiet_NaN()}) {
        invalid.push_back(event(0, EventType::SelectPreset, upper, 0, value));
    }
    for (unsigned index = 1; index < 256; ++index) {
        invalid.push_back(event(0, EventType::SelectPreset, lower,
                                static_cast<std::uint8_t>(index), 11.0));
    }
    for (const auto raw : {2, 255}) {
        invalid.push_back(preset(0, static_cast<Manual>(raw), PresetSelection::BankA));
    }
    for (const auto bad : invalid) {
        for (const std::uint32_t frames : {0U, 64U}) {
            auto actual = baseline;
            const auto before = histories(actual);
            const auto saved = actual.controls_snapshot();
            const auto percussion = actual.percussion_diagnostics();
            const std::array events{preset(0, upper, PresetSelection::G),
                event(0, EventType::NoteOff, lower, 96),
                event(0, EventType::PedalOff, lower, 1),
                event(0, EventType::Expression, upper, 0, 0.125), bad};
            std::array<float, 67> output;
            output.fill(sentinel);
            const auto result = actual.process(frames, output, events);
            CHECK(result.status == Status::InvalidEvent && result.events_consumed == 0);
            CHECK(std::all_of(output.begin(), output.end(), [](float sample) { return sample == sentinel; }));
            CHECK(histories(actual) == before);
            CHECK(actual.controls_snapshot() == saved);
            CHECK(actual.percussion_diagnostics() == percussion);
            same_future(actual, baseline);
            ++rejected_calls;
        }
    }
    for (const std::uint32_t frames : {0U, 64U}) {
        auto actual = baseline;
        const std::array beyond{preset(frames == 0 ? 1 : frames, upper, PresetSelection::F)};
        const auto result = actual.process(frames, {}, beyond);
        CHECK(result.status == Status::InvalidEvent && result.events_consumed == 0);
        same_future(actual, baseline);
    }
    auto actual = baseline;
    const std::array unordered{preset(1, upper, PresetSelection::F),
                               preset(0, lower, PresetSelection::G)};
    CHECK(actual.process(64, {}, unordered).status == Status::InvalidEvent);
    same_future(actual, baseline);
    for (std::size_t m = 0; m < 2; ++m) {
        for (const auto raw : {10, 255}) {
            auto invalid_controls = baseline.controls_snapshot();
            invalid_controls.fixed_registrations[m] = static_cast<FixedRegistration>(raw);
            invalid_controls.route_enabled[m] = false;
            invalid_controls.expression = 0.125;
            CHECK(!actual.restore_controls(invalid_controls));
            CHECK(actual.controls_snapshot() == baseline.controls_snapshot());
            CHECK(histories(actual) == histories(baseline));
            same_future(actual, baseline);
        }
    }
}

std::vector<Event> timeline(bool travel) {
    return {
        event(0, EventType::NoteOn, upper, 36, 127),
        event(0, EventType::NoteOn, upper, 96, 127),
        event(0, EventType::NoteOn, lower, 60, 127),
        event(0, EventType::PedalOn, lower, 13, 127),
        event(0, EventType::Percussion, upper, 0, 1),
        preset(1, upper, PresetSelection::CSharp),
        preset(17, lower, PresetSelection::A),
        event(64, EventType::Drawbar, upper, 8, 8),
        preset(127, upper, PresetSelection::Cancel),
        preset(128, upper, PresetSelection::A),
        bank(255, upper, DrawbarBank::B),
        preset(255, upper, PresetSelection::E),
        bank(256, upper, DrawbarBank::B),
        event(257, EventType::KeyPosition, upper, 96, travel ? 0.51 : 0.0),
        preset(511, lower, PresetSelection::Cancel),
        bank(512, lower, DrawbarBank::A),
        preset(512, lower, PresetSelection::GSharp),
        preset(777, upper, PresetSelection::G),
        event(1023, EventType::NoteOff, upper, 36),
        preset(1024, upper, PresetSelection::BankB),
        event(1024, EventType::NoteOn, upper, 96, 127),
        preset(1536, upper, PresetSelection::FSharp),
        preset(1536, upper, PresetSelection::BankB),
        event(1555, EventType::PedalOff, lower, 13),
        event(2048, EventType::Expression, upper, 0, 0.375),
        preset(2048, lower, PresetSelection::BankA),
        preset(2048, lower, PresetSelection::DSharp),
        preset(2304, upper, PresetSelection::Cancel)};
}

void render_partitioned(Engine& engine, std::span<float> output, std::span<const Event> events,
                         std::span<const std::uint32_t> pattern, bool disconnected) {
    std::uint32_t frame = 0;
    std::size_t next = 0, partition = 0;
    while (frame < output.size()) {
        const auto frames = std::min(pattern[partition++ % pattern.size()],
                                    static_cast<std::uint32_t>(output.size()) - frame);
        std::vector<Event> local;
        while (next < events.size() && events[next].offset < frame + frames) {
            auto current = events[next++];
            current.offset -= frame;
            local.push_back(current);
        }
        process(engine, 0); // Empty flushes cannot affect an absolute timeline.
        process(engine, frames, disconnected ? std::span<float>{} : output.subspan(frame, frames), local);
        frame += frames;
    }
    CHECK(next == events.size());
}

void test_partitions_rates_and_disconnected_output(const RuntimeProfile& profile) {
    for (const auto rate : {44100.0, 48000.0, 96000.0}) {
        for (const bool travel : {false, true}) {
            auto baseline = prepared(profile, rate, travel);
            CHECK(baseline.restore_controls(retained_controls()));
            auto partitioned = baseline;
            auto disconnected = baseline;
            const auto events = timeline(travel);
            std::array<float, 2305> expected{}, actual{}, unused{};
            const std::array<std::uint32_t, 6> pattern{1, 17, 64, 127, 512, 1024};
            process(baseline, static_cast<std::uint32_t>(expected.size()), expected, events);
            render_partitioned(partitioned, actual, events, pattern, false);
            render_partitioned(disconnected, unused, events, pattern, true);
            same_audio(actual, expected);
            CHECK(histories(partitioned) == histories(baseline));
            CHECK(histories(disconnected) == histories(baseline));
            CHECK(partitioned.controls_snapshot() == baseline.controls_snapshot());
            CHECK(disconnected.controls_snapshot() == baseline.controls_snapshot());
            check_selection(partitioned, upper, PresetSelection::Cancel);
            check_selection(partitioned, lower, PresetSelection::DSharp);
            same_future(partitioned, baseline);
            same_future(disconnected, baseline);
        }
    }
}

} // namespace

int main() {
    const auto profile = load_test_profile();
    test_control_domains_and_transitions();
    test_all_literal_rows_at_continuing_phase(profile);
    test_remembered_bank_edits_and_old_selection(profile);
    test_zero_time_cancel_restore_and_partial_contacts(profile);
    test_fixed_percussion_exclusion_and_readiness(profile);
    test_rejected_calls_preserve_future(profile);
    test_partitions_rates_and_disconnected_output(profile);
    std::cout << "fixed registration engine: " << row_audio_cases
              << " literal-row/rate/contact audio cases, " << rejected_calls
              << " rejected calls with future-audio continuation; passed\n";
}
