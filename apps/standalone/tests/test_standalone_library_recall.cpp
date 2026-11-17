#include "UiModel.h"

#include <array>
#include <bit>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <string_view>
#include <tuple>
#include <type_traits>
#include <utility>
#include <variant>
#include <vector>

// Independent public-API tests for the named-recall semantic operation.
// SessionSnapshot and SubmitResult values below are explicit synthetic boundary
// inputs. No Session, storage, parser, browser, native SDK or production scope
// merge supplies an oracle or receives an action in this suite. Real Session
// sequencing, external owner coexistence and combined storage journeys require
// their separate integration gates.
namespace {
using namespace hammond;
using namespace hammond::standalone;

static_assert(std::is_same_v<decltype(std::declval<UiModel&>().recall_controls(
    std::declval<const ControlSnapshot&>())), UiActions>);
static_assert(noexcept(std::declval<UiModel&>().recall_controls(
    std::declval<const ControlSnapshot&>())));

std::size_t checks = 0;
std::size_t invalid_cases = 0;
std::size_t presentation_cases = 0;
std::string_view current_case;

void check(bool condition, std::string_view expression, int line) {
    ++checks;
    if (!condition) {
        throw std::runtime_error(std::string(current_case) + ": line " +
            std::to_string(line) + ": " + std::string(expression));
    }
}
#define REQUIRE(expression) check(static_cast<bool>(expression), #expression, __LINE__)

// Two independent literal complete snapshots. Retained fixed memories under
// Cancel, all four banks and both pedals make per-field UI replay observably
// different from copying the requested snapshot once.
ControlSnapshot legacy_saved() {
    ControlSnapshot value;
    value.drawbars[0][0] = {0, 1, 2, 3, 4, 5, 6, 7, 8};
    value.drawbars[0][1] = {8, 7, 6, 5, 4, 3, 2, 1, 0};
    value.drawbars[1][0] = {1, 3, 5, 7, 0, 2, 4, 6, 8};
    value.drawbars[1][1] = {2, 4, 6, 8, 1, 3, 5, 7, 0};
    value.selected_banks = {DrawbarBank::A, DrawbarBank::B};
    value.route_enabled = {true, false};
    value.expression = 0.75;
    value.percussion = {false, PercussionHarmonic::Second,
        PercussionVolume::Normal, PercussionDecay::Slow};
    value.pedal_drawbars = {2, 7};
    value.fixed_registrations = {FixedRegistration::None, FixedRegistration::CSharp};
    return value;
}

ControlSnapshot named_controls() {
    ControlSnapshot value;
    value.drawbars[0][0] = {8, 6, 4, 2, 0, 7, 5, 3, 1};
    value.drawbars[0][1] = {1, 2, 3, 4, 5, 6, 7, 8, 0};
    value.drawbars[1][0] = {7, 0, 6, 1, 5, 2, 4, 3, 8};
    value.drawbars[1][1] = {6, 5, 4, 3, 2, 1, 0, 8, 7};
    value.selected_banks = {DrawbarBank::B, DrawbarBank::A};
    value.route_enabled = {false, true};
    value.expression = 0.125;
    value.percussion = {true, PercussionHarmonic::Third,
        PercussionVolume::Soft, PercussionDecay::Fast};
    value.pedal_drawbars = {8, 3};
    value.fixed_registrations = {FixedRegistration::GSharp, FixedRegistration::A};
    return value;
}

void same_controls(const ControlSnapshot& actual, const ControlSnapshot& expected) {
    REQUIRE(actual.drawbars == expected.drawbars);
    REQUIRE(actual.selected_banks == expected.selected_banks);
    REQUIRE(actual.route_enabled == expected.route_enabled);
    REQUIRE(std::bit_cast<std::uint64_t>(actual.expression) ==
            std::bit_cast<std::uint64_t>(expected.expression));
    REQUIRE(actual.percussion.enabled == expected.percussion.enabled);
    REQUIRE(actual.percussion.harmonic == expected.percussion.harmonic);
    REQUIRE(actual.percussion.volume == expected.percussion.volume);
    REQUIRE(actual.percussion.decay == expected.percussion.decay);
    REQUIRE(actual.pedal_drawbars == expected.pedal_drawbars);
    REQUIRE(actual.fixed_registrations == expected.fixed_registrations);
}

const SessionCommand& one_command(const UiActions& actions) {
    REQUIRE(actions.count == 1);
    REQUIRE(actions.span().size() == 1);
    REQUIRE(std::holds_alternative<SessionCommand>(actions.items[0]));
    return std::get<SessionCommand>(actions.items[0]);
}

const ControlSnapshot& one_snapshot(const UiActions& actions,
                                    const ControlSnapshot& expected) {
    const auto& command = one_command(actions);
    REQUIRE(std::holds_alternative<ControlSnapshot>(command));
    const auto& actual = std::get<ControlSnapshot>(command);
    same_controls(actual, expected);
    return actual;
}

void no_actions(const UiActions& actions) {
    REQUIRE(actions.count == 0);
    REQUIRE(actions.span().empty());
}

void app_request(const UiActions& actions, UiAppRequest expected) {
    REQUIRE(actions.count == 1);
    REQUIRE(std::holds_alternative<UiAppRequest>(actions.items[0]));
    REQUIRE(std::get<UiAppRequest>(actions.items[0]) == expected);
}

void same_observation(const SessionSnapshot& actual, const SessionSnapshot& expected) {
    same_controls(actual.controls, expected.controls);
    REQUIRE(std::tie(actual.held_keys, actual.held_pedals, actual.frame_clock,
        actual.sample_rate, actual.prepared, actual.running,
        actual.publication_revision, actual.resolved_sequence,
        actual.last_applied_sequence, actual.recovery_count,
        actual.queue_overflows, actual.rejected_commands,
        actual.discarded_commands, actual.fault_flags, actual.last_core_status) ==
        std::tie(expected.held_keys, expected.held_pedals, expected.frame_clock,
        expected.sample_rate, expected.prepared, expected.running,
        expected.publication_revision, expected.resolved_sequence,
        expected.last_applied_sequence, expected.recovery_count,
        expected.queue_overflows, expected.rejected_commands,
        expected.discarded_commands, expected.fault_flags, expected.last_core_status));
    REQUIRE(std::bit_cast<std::uint32_t>(actual.peak) ==
            std::bit_cast<std::uint32_t>(expected.peak));
}

// Compare every public member other than the three intended recall changes:
// desired controls, pending and comparison to the unchanged legacy baseline.
void same_noncontrol_view(const UiViewState& actual, const UiViewState& expected) {
    same_observation(actual.applied, expected.applied);
    REQUIRE(std::tie(actual.edited_banks, actual.focus, actual.roving_manual_keys,
        actual.roving_pedal_key, actual.keyboard_target, actual.manual_base_midi,
        actual.pedal_octave, actual.text_entry_active, actual.pointer_captured,
        actual.input_recovery, actual.last_submit_status, actual.workspace,
        actual.presentation, actual.workspace_focus) ==
        std::tie(expected.edited_banks, expected.focus, expected.roving_manual_keys,
        expected.roving_pedal_key, expected.keyboard_target, expected.manual_base_midi,
        expected.pedal_octave, expected.text_entry_active, expected.pointer_captured,
        expected.input_recovery, expected.last_submit_status, expected.workspace,
        expected.presentation, expected.workspace_focus));
}

void same_view(const UiViewState& actual, const UiViewState& expected) {
    same_noncontrol_view(actual, expected);
    same_controls(actual.controls, expected.controls);
    REQUIRE(actual.controls_pending == expected.controls_pending);
    REQUIRE(actual.controls_dirty == expected.controls_dirty);
}

void same_rect(const UiRect& a, const UiRect& b) {
    REQUIRE(std::tie(a.x, a.y, a.width, a.height) ==
            std::tie(b.x, b.y, b.width, b.height));
}

void same_key_geometry(const UiKeyGeometry& a, const UiKeyGeometry& b) {
    REQUIRE(a.note == b.note && a.accidental == b.accidental);
    same_rect(a.bounds, b.bounds);
    for (std::size_t index = 0; index < 4; ++index) {
        REQUIRE(a.hit.points[index].x == b.hit.points[index].x);
        REQUIRE(a.hit.points[index].y == b.hit.points[index].y);
        REQUIRE(a.top.points[index].x == b.top.points[index].x);
        REQUIRE(a.top.points[index].y == b.top.points[index].y);
        REQUIRE(a.front.points[index].x == b.front.points[index].x);
        REQUIRE(a.front.points[index].y == b.front.points[index].y);
    }
}

// Preservation only: this is not another layout/geometry conformance suite.
void same_layout(const UiLayout& a, const UiLayout& b) {
    REQUIRE(std::tie(a.width, a.height, a.show_cabinet, a.bank_controls_in_cheeks,
        a.sidebar_pedals, a.control_count, a.workspace, a.presentation) ==
        std::tie(b.width, b.height, b.show_cabinet, b.bank_controls_in_cheeks,
        b.sidebar_pedals, b.control_count, b.workspace, b.presentation));
    same_rect(a.header, b.header);
    same_rect(a.performance_panel, b.performance_panel);
    same_rect(a.keyboard_toolbar, b.keyboard_toolbar);
    same_rect(a.pedal_panel, b.pedal_panel);
    same_rect(a.footer, b.footer);
    same_rect(a.cabinet_panel, b.cabinet_panel);
    same_rect(a.cabinet_art, b.cabinet_art);
    same_rect(a.workspace_panel, b.workspace_panel);
    for (std::size_t manual = 0; manual < 2; ++manual) {
        same_rect(a.registration_panels[manual], b.registration_panels[manual]);
        same_rect(a.manual_panels[manual], b.manual_panels[manual]);
        same_rect(a.manual_rail_panels[manual], b.manual_rail_panels[manual]);
        same_rect(a.preset_key_panels[manual], b.preset_key_panels[manual]);
        for (std::size_t key = 0; key < 61; ++key)
            same_key_geometry(a.manual_keys[manual][key], b.manual_keys[manual][key]);
    }
    for (std::size_t key = 0; key < 25; ++key)
        same_key_geometry(a.pedal_keys[key], b.pedal_keys[key]);
    for (std::size_t index = 0; index < a.controls.size(); ++index) {
        REQUIRE(a.controls[index].id == b.controls[index].id);
        same_rect(a.controls[index].bounds, b.controls[index].bounds);
        same_rect(a.controls[index].label_bounds, b.controls[index].label_bounds);
        same_rect(a.controls[index].value_bounds, b.controls[index].value_bounds);
        same_rect(a.controls[index].track, b.controls[index].track);
    }
}

SessionSnapshot observation(const ControlSnapshot& controls,
    std::uint64_t publication = 10, std::uint64_t resolved = 40,
    std::uint64_t applied = 40) {
    SessionSnapshot value;
    value.controls = controls;
    value.frame_clock = 8192;
    value.sample_rate = 48000.0;
    value.peak = 0.375F;
    value.prepared = true;
    value.running = true;
    value.publication_revision = publication;
    value.resolved_sequence = resolved;
    value.last_applied_sequence = applied;
    value.held_keys[0][24] = true;
    value.held_keys[0][41] = true;
    value.held_keys[1][31] = true;
    value.held_keys[1][38] = true;
    value.held_pedals[16] = true;
    return value;
}

void establish_legacy_baseline(UiModel& model) {
    model.observe(observation(legacy_saved()));
    model.mark_saved(legacy_saved());
    same_controls(model.view().controls, legacy_saved());
    REQUIRE(!model.view().controls_dirty && !model.view().controls_pending);
}

void accepted(UiModel& model, const UiActions& actions, std::uint64_t sequence) {
    no_actions(model.submitted(one_command(actions), {SessionStatus::Ok, sequence}));
    REQUIRE(model.view().last_submit_status == SessionStatus::Ok);
}

void acknowledged(UiModel& model, const UiActions& actions,
    const ControlSnapshot& expected, std::uint64_t sequence, std::uint64_t publication) {
    one_snapshot(actions, expected);
    accepted(model, actions, sequence);
    model.observe(observation(expected, publication, sequence, sequence));
    REQUIRE(!model.view().controls_pending);
    same_controls(model.view().controls, expected);
}

void whole_snapshot_and_value_lifetime() {
    UiModel model;
    establish_legacy_baseline(model);
    const auto before = model.view();
    const auto layout_before = model.layout();
    auto candidate = named_controls();
    const auto recalled = model.recall_controls(candidate);
    one_snapshot(recalled, named_controls());
    same_controls(model.view().controls, named_controls());
    REQUIRE(model.view().controls_pending && model.view().controls_dirty);
    same_noncontrol_view(model.view(), before);
    same_layout(model.layout(), layout_before);

    // Both the command and desired copy outlive caller edits; one action means
    // no parameter, preset, note, release, panic or app-request replay escapes.
    candidate = legacy_saved();
    candidate.expression = std::numeric_limits<double>::quiet_NaN();
    one_snapshot(recalled, named_controls());
    same_controls(model.view().controls, named_controls());
    const auto aliased = model.recall_controls(model.view().controls);
    one_snapshot(aliased, named_controls());
    REQUIRE(model.view().controls_dirty && model.view().controls_pending);
    same_noncontrol_view(model.view(), before);
    one_snapshot(recalled, named_controls());

    // Finite expression endpoints and their nearest interior values are valid
    // complete recalls; copying also retains the admitted sign of zero.
    for (const double expression : {0.0, -0.0, 1.0,
            std::nextafter(0.0, 1.0), std::nextafter(1.0, 0.0)}) {
        auto boundary = named_controls();
        boundary.expression = expression;
        one_snapshot(model.recall_controls(boundary), boundary);
        same_controls(model.view().controls, boundary);
        REQUIRE(model.view().controls_dirty && model.view().controls_pending);
        same_noncontrol_view(model.view(), before);
    }
    one_snapshot(recalled, named_controls());
    one_snapshot(aliased, named_controls());
}

void clean_equal_requires_its_submission() {
    UiModel model;
    establish_legacy_baseline(model);
    const auto before = model.view();
    const auto equal = model.recall_controls(model.view().controls);
    one_snapshot(equal, legacy_saved());
    REQUIRE(model.view().controls_pending && !model.view().controls_dirty);
    same_noncontrol_view(model.view(), before);

    // Equality and newer publications cannot resolve an unsubmitted intent.
    model.observe(observation(legacy_saved(), 12, 41, 41));
    REQUIRE(model.view().controls_pending && !model.view().controls_dirty);
    accepted(model, equal, 42);
    model.observe(observation(legacy_saved(), 14, 41, 41));
    REQUIRE(model.view().controls_pending);

    // A later non-control post must not replace the recall's tracked sequence.
    const SessionCommand note = PerformanceInputEvent{
        HostNoteEvent{0, HostNoteKind::On, 0, 0, 67, 127, 9}};
    no_actions(model.submitted(note, {SessionStatus::Ok, 43}));
    model.observe(observation(legacy_saved(), 16, 42, 42));
    REQUIRE(!model.view().controls_pending && !model.view().controls_dirty);
    REQUIRE(model.view().applied.resolved_sequence == 42);
    REQUIRE(model.view().applied.last_applied_sequence == 42);

    // Every explicit clean-equal activation still emits another whole copy.
    const auto again = model.recall_controls(legacy_saved());
    one_snapshot(again, legacy_saved());
    REQUIRE(model.view().controls_pending && !model.view().controls_dirty);
    model.observe(observation(legacy_saved(), 18, 43, 43));
    REQUIRE(model.view().controls_pending);
    acknowledged(model, again, legacy_saved(), 44, 20);
    REQUIRE(!model.view().controls_dirty);
}

void dirty_equal_supersedes_older_control_sequence() {
    UiModel model;
    establish_legacy_baseline(model);
    const auto first = model.recall_controls(named_controls());
    one_snapshot(first, named_controls());
    accepted(model, first, 51);

    const auto equal_pending = model.recall_controls(named_controls());
    one_snapshot(equal_pending, named_controls());
    REQUIRE(model.view().controls_dirty && model.view().controls_pending);
    model.observe(observation(named_controls(), 12, 51, 51));
    REQUIRE(model.view().controls_pending && model.view().controls_dirty);
    accepted(model, equal_pending, 52);
    model.observe(observation(named_controls(), 14, 51, 51));
    REQUIRE(model.view().controls_pending);
    model.observe(observation(named_controls(), 16, 52, 52));
    REQUIRE(!model.view().controls_pending && model.view().controls_dirty);

    const auto equal_applied = model.recall_controls(model.view().controls);
    one_snapshot(equal_applied, named_controls());
    REQUIRE(model.view().controls_pending && model.view().controls_dirty);
    accepted(model, equal_applied, 53);
    model.observe(observation(named_controls(), 18, 52, 52));
    REQUIRE(model.view().controls_pending);
    model.observe(observation(named_controls(), 20, 53, 53));
    REQUIRE(!model.view().controls_pending && model.view().controls_dirty);

    // A preceding ordinary edit must likewise not acknowledge a new recall.
    auto ordinary_expected = named_controls();
    ordinary_expected.expression = 0.5;
    const auto ordinary = model.external_parameter(8192, 0.5);
    one_snapshot(ordinary, ordinary_expected);
    accepted(model, ordinary, 54);
    const auto return_to_saved = model.recall_controls(legacy_saved());
    one_snapshot(return_to_saved, legacy_saved());
    REQUIRE(model.view().controls_pending && !model.view().controls_dirty);
    model.observe(observation(ordinary_expected, 22, 54, 54));
    REQUIRE(model.view().controls_pending && !model.view().controls_dirty);
    same_controls(model.view().controls, legacy_saved());
    acknowledged(model, return_to_saved, legacy_saved(), 55, 24);
    REQUIRE(!model.view().controls_dirty);
}

void retained_baseline_and_legacy_operations() {
    UiModel model;
    establish_legacy_baseline(model);
    acknowledged(model, model.recall_controls(named_controls()), named_controls(), 61, 12);
    REQUIRE(model.view().controls_dirty);

    auto named_with_saved_expression = named_controls();
    named_with_saved_expression.expression = 0.75;
    one_snapshot(model.external_parameter(8192, 0.75), named_with_saved_expression);
    REQUIRE(model.view().controls_dirty); // Matching expression alone is not clean.
    const auto restored = model.recall_controls(legacy_saved());
    one_snapshot(restored, legacy_saved());
    REQUIRE(!model.view().controls_dirty && model.view().controls_pending);
    acknowledged(model, restored, legacy_saved(), 62, 14);

    auto expression_edit = legacy_saved();
    expression_edit.expression = 0.25;
    one_snapshot(model.external_parameter(8192, 0.25), expression_edit);
    REQUIRE(model.view().controls_dirty);
    one_snapshot(model.external_parameter(8192, 0.75), legacy_saved());
    REQUIRE(!model.view().controls_dirty && model.view().controls_pending);

    // Legacy Load intentionally establishes a different clean-file reference.
    const auto loaded = model.load_controls(named_controls());
    one_snapshot(loaded, named_controls());
    REQUIRE(!model.view().controls_dirty && model.view().controls_pending);
    acknowledged(model, loaded, named_controls(), 63, 16);
    const auto equal_load = model.load_controls(named_controls());
    one_snapshot(equal_load, named_controls());
    REQUIRE(!model.view().controls_dirty && model.view().controls_pending);
    acknowledged(model, equal_load, named_controls(), 64, 18);

    const auto old_file_recall = model.recall_controls(legacy_saved());
    one_snapshot(old_file_recall, legacy_saved());
    REQUIRE(model.view().controls_dirty && model.view().controls_pending);
    const auto before_save = model.view();
    model.mark_saved(named_controls()); // Late Save of the exact prior copy.
    same_view(model.view(), before_save);
    model.mark_saved(legacy_saved());
    REQUIRE(!model.view().controls_dirty && model.view().controls_pending);
    same_noncontrol_view(model.view(), before_save);
    same_controls(model.view().controls, legacy_saved());
    acknowledged(model, old_file_recall, legacy_saved(), 65, 20);

    auto invalid = named_controls();
    invalid.expression = std::numeric_limits<double>::quiet_NaN();
    const auto before_invalid_legacy = model.view();
    model.mark_saved(invalid);
    no_actions(model.load_controls(invalid));
    same_view(model.view(), before_invalid_legacy);
    one_snapshot(model.recall_controls(named_controls()), named_controls());
    REQUIRE(model.view().controls_dirty); // Neither invalid legacy call rebased.
    one_snapshot(model.recall_controls(legacy_saved()), legacy_saved());
    REQUIRE(!model.view().controls_dirty && model.view().controls_pending);
}

struct InvalidSnapshot {
    std::string label;
    ControlSnapshot controls;
};

std::vector<InvalidSnapshot> invalid_snapshots() {
    std::vector<InvalidSnapshot> result;
    for (std::size_t manual = 0; manual < 2; ++manual) {
        for (std::size_t bank = 0; bank < 2; ++bank) {
            for (std::size_t drawbar = 0; drawbar < 9; ++drawbar) {
                for (const std::uint8_t bad : {std::uint8_t{9}, std::uint8_t{255}}) {
                    auto value = legacy_saved();
                    value.drawbars[manual][bank][drawbar] = bad;
                    result.push_back({"drawbar " + std::to_string(manual) + "/" +
                        std::to_string(bank) + "/" + std::to_string(drawbar) +
                        " = " + std::to_string(bad), value});
                }
            }
        }
        for (const std::uint8_t bad : {std::uint8_t{2}, std::uint8_t{255}}) {
            auto value = legacy_saved();
            value.selected_banks[manual] = static_cast<DrawbarBank>(bad);
            result.push_back({"selected bank " + std::to_string(manual) +
                " = " + std::to_string(bad), value});
        }
        for (const std::uint8_t bad : {std::uint8_t{10}, std::uint8_t{255}}) {
            auto value = legacy_saved();
            value.fixed_registrations[manual] = static_cast<FixedRegistration>(bad);
            result.push_back({"fixed memory " + std::to_string(manual) +
                " = " + std::to_string(bad), value});
        }
    }
    for (std::size_t pedal = 0; pedal < 2; ++pedal) {
        for (const std::uint8_t bad : {std::uint8_t{9}, std::uint8_t{255}}) {
            auto value = legacy_saved();
            value.pedal_drawbars[pedal] = bad;
            result.push_back({"pedal drawbar " + std::to_string(pedal) +
                " = " + std::to_string(bad), value});
        }
    }
    for (const std::uint8_t bad : {std::uint8_t{2}, std::uint8_t{255}}) {
        auto value = legacy_saved();
        value.percussion.harmonic = static_cast<PercussionHarmonic>(bad);
        result.push_back({"percussion harmonic = " + std::to_string(bad), value});
        value = legacy_saved();
        value.percussion.volume = static_cast<PercussionVolume>(bad);
        result.push_back({"percussion volume = " + std::to_string(bad), value});
        value = legacy_saved();
        value.percussion.decay = static_cast<PercussionDecay>(bad);
        result.push_back({"percussion decay = " + std::to_string(bad), value});
    }
    const double infinity = std::numeric_limits<double>::infinity();
    const std::array<std::pair<std::string_view, double>, 7> expressions{{
        {"negative expression", -0.001},
        {"immediately below zero", std::nextafter(0.0, -infinity)},
        {"immediately above one", std::nextafter(1.0, infinity)},
        {"expression above one", 1.001},
        {"positive infinity", infinity}, {"negative infinity", -infinity},
        {"NaN", std::numeric_limits<double>::quiet_NaN()}}};
    for (const auto& [label, expression] : expressions) {
        auto value = legacy_saved();
        value.expression = expression;
        result.push_back({std::string(label), value});
    }
    auto several = legacy_saved();
    several.drawbars[0][0][0] = 9;
    several.fixed_registrations[1] = static_cast<FixedRegistration>(255);
    several.expression = infinity;
    result.push_back({"invalid early, scalar and final fields together", several});
    return result;
}

void invalid_complete_snapshots_are_atomic() {
    const auto candidates = invalid_snapshots();
    REQUIRE(candidates.size() == 98);
    for (const auto& candidate : candidates) {
        current_case = candidate.label;
        UiModel model;
        establish_legacy_baseline(model);
        const auto valid = model.recall_controls(named_controls());
        one_snapshot(valid, named_controls());
        accepted(model, valid, 71);
        const auto before = model.view();
        const auto layout_before = model.layout();
        no_actions(model.recall_controls(candidate.controls));
        same_view(model.view(), before);
        same_layout(model.layout(), layout_before);

        // Refusal cannot discard or replace a previously submitted sequence.
        model.observe(observation(legacy_saved(), 12, 70, 70));
        REQUIRE(model.view().controls_pending && model.view().controls_dirty);
        same_controls(model.view().controls, named_controls());
        model.observe(observation(named_controls(), 14, 71, 71));
        REQUIRE(!model.view().controls_pending && model.view().controls_dirty);
        same_controls(model.view().controls, named_controls());

        // The private saved reference is tested through its visible effect.
        one_snapshot(model.recall_controls(legacy_saved()), legacy_saved());
        REQUIRE(!model.view().controls_dirty && model.view().controls_pending);
        ++invalid_cases;
    }
}

void tap(UiModel& model, UiKey key) {
    no_actions(model.key({key, true}));
    no_actions(model.key({key, false}));
}

void manual_note_command(const SessionCommand& command, HostNoteKind kind,
                         std::uint8_t bus, std::uint8_t midi, std::int32_t owner) {
    REQUIRE(std::holds_alternative<PerformanceInputEvent>(command));
    const auto& input = std::get<PerformanceInputEvent>(command);
    REQUIRE(std::holds_alternative<HostNoteEvent>(input));
    const auto& note = std::get<HostNoteEvent>(input);
    REQUIRE(note.offset == 0 && note.channel == 0);
    REQUIRE(note.kind == kind && note.bus == bus && note.midi_note == midi);
    REQUIRE(note.note_id == owner);
    REQUIRE(note.velocity == (kind == HostNoteKind::On ? 127 : 0));
}

void manual_note(const UiActions& actions, HostNoteKind kind,
                 std::uint8_t bus, std::uint8_t midi, std::int32_t owner) {
    manual_note_command(one_command(actions), kind, bus, midi, owner);
}

void pedal_note(const UiActions& actions, PedalNoteKind kind,
                std::uint8_t pedal, std::int32_t owner) {
    const auto& command = one_command(actions);
    REQUIRE(std::holds_alternative<PerformanceInputEvent>(command));
    const auto& input = std::get<PerformanceInputEvent>(command);
    REQUIRE(std::holds_alternative<PedalNoteEvent>(input));
    const auto& note = std::get<PedalNoteEvent>(input);
    REQUIRE(note.offset == 0 && note.bus == 0 && note.channel == 0);
    REQUIRE(note.kind == kind && note.pedal.value == pedal && note.note_id == owner);
    REQUIRE(note.velocity == (kind == PedalNoteKind::On ? 127 : 0));
}

UiPoint lower_g_pointer_point(const UiModel& model) {
    // The public geometry supplies only the event location. The expected note,
    // bus and owner are literal Lower MIDI 67 and pointer owner 100 below.
    const auto& corners = model.layout().manual_keys[1][31].hit.points;
    const float left = corners[0].x + 0.9F * (corners[3].x - corners[0].x);
    const float right = corners[1].x + 0.9F * (corners[2].x - corners[1].x);
    return {(left + right) * 0.5F,
        corners[0].y + 0.9F * (corners[3].y - corners[0].y)};
}

void establish_owned_presses(UiModel& model) {
    manual_note(model.key({UiKey::A, true}), HostNoteKind::On, 0, 60, 1);
    tap(model, UiKey::F2);
    tap(model, UiKey::RightBracket);
    manual_note(model.key({UiKey::S, true}), HostNoteKind::On, 1, 74, 3);
    tap(model, UiKey::F3);
    tap(model, UiKey::RightBracket);
    pedal_note(model.key({UiKey::D, true}), PedalNoteKind::On, 17, 5);
    manual_note(model.pointer({UiPointerKind::Down, lower_g_pointer_point(model)}),
        HostNoteKind::On, 1, 67, 100);
    no_actions(model.activate({UiControlKind::ManualKey, Manual::Upper, DrawbarBank::A, 41}));
    manual_note(model.key({UiKey::Space, true}), HostNoteKind::On, 0, 77, 101);
    REQUIRE(model.view().pointer_captured);
}

void original_releases(UiModel& model) {
    // Up still owns the original identity while a text editor or another
    // workspace is active. Modifiers on release do not retarget that identity.
    manual_note(model.key({UiKey::A, false, false, true, true, true, true}),
        HostNoteKind::Off, 0, 60, 1);
    manual_note(model.key({UiKey::S, false}), HostNoteKind::Off, 1, 74, 3);
    pedal_note(model.key({UiKey::D, false}), PedalNoteKind::Off, 17, 5);
    manual_note(model.key({UiKey::Space, false}), HostNoteKind::Off, 0, 77, 101);
    manual_note(model.pointer({UiPointerKind::Up, {-500.0F, -500.0F}}),
        HostNoteKind::Off, 1, 67, 100);
    REQUIRE(!model.view().pointer_captured);
    for (const auto key : {UiKey::A, UiKey::S, UiKey::D, UiKey::Space})
        no_actions(model.key({key, false}));
    no_actions(model.pointer({UiPointerKind::Up, {}}));
}

void presentation_and_original_owners() {
    constexpr std::array<UiWorkspace, 3> workspaces{
        UiWorkspace::Play, UiWorkspace::Rotary, UiWorkspace::Service};
    constexpr std::array<UiPresentation, 2> presentations{
        UiPresentation::Dimensional, UiPresentation::Flat};
    constexpr std::array<UiTarget, 3> targets{
        UiTarget::Upper, UiTarget::Lower, UiTarget::Pedals};
    constexpr std::array<std::array<DrawbarBank, 2>, 4> edited{{
        {DrawbarBank::A, DrawbarBank::A}, {DrawbarBank::A, DrawbarBank::B},
        {DrawbarBank::B, DrawbarBank::A}, {DrawbarBank::B, DrawbarBank::B}}};
    for (const auto workspace : workspaces) {
        for (const auto presentation : presentations) {
            for (const auto target : targets) {
                for (const auto& banks : edited) {
                    const std::string label = "presentation/owner case " +
                        std::to_string(presentation_cases);
                    current_case = label;
                    UiModel model;
                    establish_legacy_baseline(model);
                    REQUIRE(model.resize(1672.0F, 941.0F));
                    establish_owned_presses(model);
                    no_actions(model.activate({UiControlKind::EditBank, Manual::Upper, banks[0]}));
                    no_actions(model.activate({UiControlKind::EditBank, Manual::Lower, banks[1]}));
                    tap(model, target == UiTarget::Upper ? UiKey::F1 :
                        target == UiTarget::Lower ? UiKey::F2 : UiKey::F3);
                    no_actions(model.activate({UiControlKind::ManualKey,
                        Manual::Upper, DrawbarBank::A, 43}));
                    no_actions(model.activate({UiControlKind::ManualKey,
                        Manual::Lower, DrawbarBank::A, 17}));
                    no_actions(model.activate({UiControlKind::PedalKey,
                        Manual::Upper, DrawbarBank::A, 18}));
                    const UiControlId play_focus{
                        UiControlKind::ManualDrawbar, Manual::Lower, banks[1], 6};
                    no_actions(model.activate(play_focus));
                    REQUIRE(model.set_workspace(UiWorkspace::Rotary));
                    app_request(model.activate({UiControlKind::Help}), UiAppRequest::Help);
                    REQUIRE(model.set_workspace(UiWorkspace::Service));
                    app_request(model.activate({UiControlKind::AudioSettings}), UiAppRequest::AudioSettings);
                    REQUIRE(model.set_workspace(workspace));
                    REQUIRE(model.set_presentation(presentation));
                    model.set_text_entry_active(true);
                    REQUIRE(model.view().workspace == workspace);
                    REQUIRE(model.view().presentation == presentation);
                    REQUIRE(model.view().edited_banks == banks);
                    REQUIRE(model.view().keyboard_target == target);
                    REQUIRE(model.view().manual_base_midi == 72 && model.view().pedal_octave == 1);
                    REQUIRE((model.view().roving_manual_keys == std::array<std::uint8_t, 2>{43, 17}));
                    REQUIRE(model.view().roving_pedal_key == 18);
                    const std::array<UiControlId, 3> memories{
                        play_focus, UiControlId{UiControlKind::Help}, UiControlId{UiControlKind::AudioSettings}};
                    REQUIRE(model.view().workspace_focus == memories);
                    REQUIRE(model.view().focus == memories[static_cast<std::size_t>(workspace)]);
                    const auto before = model.view();
                    const auto layout_before = model.layout();

                    // Invalid recall must preserve hidden note owners too.
                    auto invalid = named_controls();
                    invalid.fixed_registrations[1] = static_cast<FixedRegistration>(255);
                    no_actions(model.recall_controls(invalid));
                    same_view(model.view(), before);
                    one_snapshot(model.recall_controls(named_controls()), named_controls());
                    REQUIRE(model.view().controls_pending && model.view().controls_dirty);
                    same_noncontrol_view(model.view(), before);
                    same_layout(model.layout(), layout_before);
                    original_releases(model);
                    same_controls(model.view().controls, named_controls());
                    REQUIRE(model.view().controls_pending && model.view().controls_dirty);

                    model.set_text_entry_active(false);
                    const auto down = model.key({UiKey::A, true});
                    const auto up = model.key({UiKey::A, false});
                    if (target == UiTarget::Pedals) {
                        pedal_note(down, PedalNoteKind::On, 13, 1);
                        pedal_note(up, PedalNoteKind::Off, 13, 1);
                    } else {
                        const std::uint8_t bus = target == UiTarget::Upper ? 0 : 1;
                        manual_note(down, HostNoteKind::On, bus, 72, 1);
                        manual_note(up, HostNoteKind::Off, bus, 72, 1);
                    }
                    ++presentation_cases;
                }
            }
        }
    }
    REQUIRE(presentation_cases == 72);
}

UiControlGeometry control_geometry(const UiModel& model, UiControlId id) {
    for (const auto& geometry : model.layout().controls) {
        if (geometry.id == id) return geometry;
    }
    throw std::runtime_error("test setup could not locate the requested visible control");
}

void active_gestures_survive() {
    for (const bool expression : {false, true}) {
        UiModel model;
        establish_legacy_baseline(model);
        no_actions(model.activate({UiControlKind::EditBank, Manual::Upper, DrawbarBank::A}));
        const UiControlId id = expression ? UiControlId{UiControlKind::Expression} :
            UiControlId{UiControlKind::ManualDrawbar, Manual::Upper, DrawbarBank::A, 0};
        const auto geometry = control_geometry(model, id);
        const UiPoint start{geometry.track.x + (expression ? 0.0F : 1.0F), geometry.track.y};
        if (expression) {
            auto expected_start = legacy_saved();
            expected_start.expression = 0.0;
            one_snapshot(model.pointer({UiPointerKind::Down, start}), expected_start);
        } else {
            no_actions(model.pointer({UiPointerKind::Down, start}));
        }
        REQUIRE(model.view().pointer_captured && model.view().focus == id);
        const auto before = model.view();
        auto invalid = named_controls();
        invalid.expression = -std::numeric_limits<double>::infinity();
        no_actions(model.recall_controls(invalid));
        same_view(model.view(), before);
        one_snapshot(model.recall_controls(named_controls()), named_controls());
        same_noncontrol_view(model.view(), before);

        auto expected = named_controls();
        UiPoint end;
        if (expression) {
            expected.expression = 1.0;
            end = {geometry.track.x + geometry.track.width + 1.0F, geometry.track.y};
        } else {
            // Named value at this index is 8; the still-active gesture edits
            // only its originally captured bank to the opposite endpoint.
            expected.drawbars[0][0][0] = 0;
            end = start;
        }
        one_snapshot(model.pointer({UiPointerKind::Move, end}), expected);
        REQUIRE(model.view().pointer_captured && model.view().focus == id);
        same_controls(model.view().controls, expected);
        no_actions(model.pointer({UiPointerKind::Up, {-500.0F, -500.0F}}));
        REQUIRE(!model.view().pointer_captured);
    }

    // Unlike the workspace matrix, this pointer has not been suppressed by a
    // layout transition. Recall must retain its ongoing musical gesture too.
    UiModel model;
    establish_legacy_baseline(model);
    manual_note(model.pointer({UiPointerKind::Down, lower_g_pointer_point(model)}),
        HostNoteKind::On, 1, 67, 100);
    const auto before = model.view();
    one_snapshot(model.recall_controls(named_controls()), named_controls());
    same_noncontrol_view(model.view(), before);
    const auto& corners = model.layout().manual_keys[0][24].hit.points;
    const float left = corners[0].x + 0.9F * (corners[3].x - corners[0].x);
    const float right = corners[1].x + 0.9F * (corners[2].x - corners[1].x);
    const UiPoint upper_c{(left + right) * 0.5F,
        corners[0].y + 0.9F * (corners[3].y - corners[0].y)};
    const auto moved = model.pointer({UiPointerKind::Move, upper_c});
    REQUIRE(moved.count == 2 && moved.span().size() == 2);
    REQUIRE(std::holds_alternative<SessionCommand>(moved.items[0]));
    REQUIRE(std::holds_alternative<SessionCommand>(moved.items[1]));
    manual_note_command(std::get<SessionCommand>(moved.items[0]), HostNoteKind::Off, 1, 67, 100);
    manual_note_command(std::get<SessionCommand>(moved.items[1]), HostNoteKind::On, 0, 60, 100);
    manual_note(model.pointer({UiPointerKind::Up, {-500.0F, -500.0F}}),
        HostNoteKind::Off, 0, 60, 100);
    same_controls(model.view().controls, named_controls());
    REQUIRE(model.view().controls_pending && model.view().controls_dirty);
}

void synchronous_rejection_retains_saved_reference() {
    for (const auto status : {SessionStatus::QueueFull, SessionStatus::RecoveryPending,
                             SessionStatus::SequenceExhausted, SessionStatus::NotRunning,
                             SessionStatus::InvalidCommand}) {
        UiModel model;
        establish_legacy_baseline(model);
        const auto before = model.view();
        const auto recalled = model.recall_controls(named_controls());
        one_snapshot(recalled, named_controls());
        REQUIRE(model.view().controls_dirty && model.view().controls_pending);
        const auto recovery = model.submitted(one_command(recalled), {status, 0});
        if (status == SessionStatus::InvalidCommand) {
            REQUIRE(std::holds_alternative<ReleaseUiNotes>(one_command(recovery)));
            no_actions(model.submitted(one_command(recalled), {status, 0}));
        } else {
            no_actions(recovery);
        }
        REQUIRE(model.view().last_submit_status == status);
        REQUIRE(model.view().input_recovery && !model.view().controls_pending);
        REQUIRE(!model.view().controls_dirty);
        same_controls(model.view().controls, legacy_saved());
        same_observation(model.view().applied, before.applied);

        // A later valid recall is a fresh intent, never an automatic retry or
        // a silent Load baseline. Existing recovery/status indications survive.
        const auto recovered_before = model.view();
        one_snapshot(model.recall_controls(named_controls()), named_controls());
        REQUIRE(model.view().controls_dirty && model.view().controls_pending);
        same_noncontrol_view(model.view(), recovered_before);
        one_snapshot(model.recall_controls(legacy_saved()), legacy_saved());
        REQUIRE(!model.view().controls_dirty && model.view().controls_pending);
    }
}

void rejected_observation_resolves_without_claiming_application() {
    UiModel model;
    establish_legacy_baseline(model);
    const auto recalled = model.recall_controls(named_controls());
    one_snapshot(recalled, named_controls());
    accepted(model, recalled, 81);
    const auto before = model.view();

    auto invalid_observation = observation(named_controls(), 12, 81, 81);
    invalid_observation.controls.expression = std::numeric_limits<double>::quiet_NaN();
    model.observe(invalid_observation);
    same_view(model.view(), before);
    model.observe(observation(legacy_saved(), 8, 40, 40));
    same_view(model.view(), before);

    auto rejected = observation(legacy_saved(), 12, 81, 40);
    rejected.rejected_commands = 1;
    rejected.fault_flags = static_cast<std::uint32_t>(SessionFault::RejectedCommand);
    model.observe(rejected);
    REQUIRE(!model.view().controls_pending && !model.view().controls_dirty);
    REQUIRE(!model.view().input_recovery);
    REQUIRE(model.view().last_submit_status == SessionStatus::Ok);
    same_controls(model.view().controls, legacy_saved());
    same_observation(model.view().applied, rejected);
    REQUIRE(model.view().applied.resolved_sequence == 81);
    REQUIRE(model.view().applied.last_applied_sequence == 40);

    // UiModel's pending flag means consumed/resolved, not the LibraryModel
    // receipt's stronger Applied proof. A recovery likewise adopts actual
    // controls and preserves the legacy baseline, without another action.
    const auto next = model.recall_controls(named_controls());
    accepted(model, next, 82);
    auto recovered = rejected;
    recovered.publication_revision = 14;
    recovered.resolved_sequence = 82;
    recovered.recovery_count = 1;
    recovered.discarded_commands = 1;
    recovered.held_keys = {};
    recovered.held_pedals = {};
    model.observe(recovered);
    REQUIRE(model.view().input_recovery && !model.view().controls_pending);
    REQUIRE(!model.view().controls_dirty);
    same_controls(model.view().controls, legacy_saved());
    same_observation(model.view().applied, recovered);
    one_snapshot(model.recall_controls(named_controls()), named_controls());
    REQUIRE(model.view().controls_dirty);
    one_snapshot(model.recall_controls(legacy_saved()), legacy_saved());
    REQUIRE(!model.view().controls_dirty);
}
} // namespace

int main() {
    struct TestCase { std::string_view name; void (*run)(); };
    const std::array<TestCase, 9> cases{{
        {"complete snapshot and copied lifetime", whole_snapshot_and_value_lifetime},
        {"clean equal recall and sequence", clean_equal_requires_its_submission},
        {"dirty equal recall and supersession", dirty_equal_supersedes_older_control_sequence},
        {"retained baseline and legacy Load/Save", retained_baseline_and_legacy_operations},
        {"invalid complete snapshot atomicity", invalid_complete_snapshots_are_atomic},
        {"presentation and original UI owners", presentation_and_original_owners},
        {"active parameter and pointer gestures", active_gestures_survive},
        {"synchronous recall rejection", synchronous_rejection_retains_saved_reference},
        {"resolved rejection and recovery observations", rejected_observation_resolves_without_claiming_application}
    }};
    std::size_t failures = 0;
    for (const auto& test : cases) {
        current_case = test.name;
        try {
            test.run();
            std::cout << "PASS " << test.name << '\n';
        } catch (const std::exception& error) {
            ++failures;
            std::cerr << "FAIL " << error.what() << '\n';
        }
    }
    std::cout << "Standalone named recall: " << cases.size() << " groups, "
        << checks << " assertions, " << invalid_cases << " invalid snapshots, "
        << presentation_cases << " presentation/owner contexts, " << failures
        << " failures (synthetic UiModel boundary inputs)\n";
    return failures == 0 ? 0 : 1;
}
