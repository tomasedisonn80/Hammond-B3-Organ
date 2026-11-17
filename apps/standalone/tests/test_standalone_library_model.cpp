#include "LibraryModel.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <functional>
#include <iostream>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

// Independent copied-state contract tests. No Session, parser, filesystem or
// production scope-merge helper supplies the oracle. Real Session and storage
// integration have separate suites and cannot be established by these copies.
namespace {
using namespace hammond;
using namespace hammond::standalone;

std::size_t checks = 0;
std::string_view current_case;

void check(bool condition, std::string_view expression, int line) {
    ++checks;
    if (!condition) {
        throw std::runtime_error(std::string(current_case) + ": line " +
            std::to_string(line) + ": " + std::string(expression));
    }
}
#define REQUIRE(expression) check(static_cast<bool>(expression), #expression, __LINE__)

constexpr auto kMax = std::numeric_limits<std::uint64_t>::max();

ControlSnapshot stored_controls() {
    ControlSnapshot value;
    value.drawbars[0][0] = {8, 0, 3, 1, 6, 2, 7, 4, 5};
    value.drawbars[0][1] = {1, 2, 3, 4, 5, 6, 7, 8, 0};
    value.drawbars[1][0] = {2, 4, 6, 8, 0, 1, 3, 5, 7};
    value.drawbars[1][1] = {7, 5, 3, 1, 8, 6, 4, 2, 0};
    value.selected_banks = {DrawbarBank::A, DrawbarBank::B};
    value.route_enabled = {false, true};
    value.fixed_registrations = {FixedRegistration::DSharp, FixedRegistration::GSharp};
    value.pedal_drawbars = {7, 3};
    value.expression = 0.25;
    value.percussion = {true, PercussionHarmonic::Third,
        PercussionVolume::Soft, PercussionDecay::Fast};
    return value;
}

ControlSnapshot other_controls() {
    ControlSnapshot value;
    value.drawbars[0][0] = {0, 8, 2, 6, 3, 7, 1, 5, 4};
    value.drawbars[0][1] = {8, 7, 6, 5, 4, 3, 2, 1, 0};
    value.drawbars[1][0] = {1, 3, 5, 7, 2, 4, 6, 8, 0};
    value.drawbars[1][1] = {2, 3, 4, 5, 6, 7, 8, 0, 1};
    value.selected_banks = {DrawbarBank::B, DrawbarBank::A};
    value.route_enabled = {true, false};
    value.fixed_registrations = {FixedRegistration::A, FixedRegistration::CSharp};
    value.pedal_drawbars = {2, 8};
    value.expression = 0.5;
    value.percussion = {false, PercussionHarmonic::Second,
        PercussionVolume::Normal, PercussionDecay::Slow};
    return value;
}

LibraryEntry entry(std::string name = "Alpha",
    RegistrationScope scope = RegistrationScope::Registration,
    const ControlSnapshot& controls = stored_controls()) {
    LibraryEntry value;
    value.name = std::move(name);
    value.scope = scope;
    value.key = value.name + (scope == RegistrationScope::Registration ?
        ".b3registration" : ".b3performance");
    value.status = LibraryEntryStatus::Valid;
    value.controls = controls;
    return value;
}

LibraryEntry disabled(std::string name, LibraryEntryStatus status) {
    auto value = entry(std::move(name));
    value.status = status;
    value.controls.reset();
    value.reason = "Fixture unavailable";
    return value;
}

// Rows are supplied in explicit contract order. This helper does not sort or
// validate them; malformed-catalog cases change these independent fixtures.
LibraryCatalog catalog(std::vector<LibraryEntry> rows = {}) {
    LibraryCatalog value;
    value.status = rows.empty() ? LibraryCatalogStatus::Empty : LibraryCatalogStatus::Ready;
    value.entries = std::move(rows);
    value.candidate_count = value.entries.size();
    value.directory_items = value.entries.size();
    for (const auto& row : value.entries) {
        if (row.status == LibraryEntryStatus::Ambiguous) ++value.ambiguous_entry_count;
        else if (row.status != LibraryEntryStatus::Valid) ++value.invalid_entry_count;
    }
    return value;
}

SessionSnapshot snapshot(const ControlSnapshot& controls = other_controls()) {
    SessionSnapshot value;
    value.controls = controls;
    value.prepared = true;
    value.running = true;
    value.publication_revision = 2;
    value.sample_rate = 48000.0;
    value.frame_clock = 128;
    value.peak = 0.125F;
    value.held_keys[0][24] = true;
    value.held_keys[1][19] = true;
    value.held_pedals[4] = true;
    return value;
}

LibraryObservation observed(const SessionSnapshot& value, bool enabled = true) {
    return {value, enabled};
}

LibraryObservation failed_read(bool enabled = true) {
    return {std::nullopt, enabled};
}

LibraryOperationView operation(const LibraryModel& model) {
    const auto view = model.view();
    REQUIRE(view.operation.has_value());
    return *view.operation;
}

LibraryCurrentReferenceView reference(const LibraryModel& model) {
    const auto view = model.view();
    REQUIRE(view.current_reference.has_value());
    return *view.current_reference;
}

void terminal(const LibraryModel& model, LibraryOutcome outcome) {
    const auto receipt = operation(model);
    REQUIRE(receipt.phase == LibraryOperationPhase::Finished);
    REQUIRE(receipt.outcome == outcome);
}

std::uint64_t publish(LibraryModel& model, LibraryCatalog value) {
    const auto refresh = model.request_refresh();
    REQUIRE(refresh.has_value());
    REQUIRE(refresh->generation != 0);
    value.generation = refresh->generation;
    REQUIRE(model.replace_catalog(value));
    REQUIRE(!model.view().catalog_stale);
    return refresh->generation;
}

void initialize(LibraryModel& model, const SessionSnapshot& actual,
    std::vector<LibraryEntry> rows = {}) {
    (void)publish(model, catalog(std::move(rows)));
    model.observe(observed(actual), 0);
    REQUIRE(model.view().observation_fresh);
}

LibraryControlIntent submit_control(LibraryModel& model, const ControlSnapshot& controls,
    const LibraryObservation& before, std::uint64_t sequence) {
    const auto intent = model.note_control_intent(controls, before);
    REQUIRE(intent.has_value());
    REQUIRE(intent->desired_revision != 0);
    REQUIRE(intent->expected_controls == controls);
    REQUIRE(model.submitted({SessionStatus::Ok, sequence}, intent) == LibraryOutcome::Accepted);
    return *intent;
}

SessionSnapshot acknowledged(const SessionSnapshot& before, const ControlSnapshot& controls,
    std::uint64_t sequence) {
    auto value = before;
    value.controls = controls;
    value.publication_revision += 2;
    value.resolved_sequence = sequence;
    value.last_applied_sequence = sequence;
    return value;
}

SessionSnapshot prove_controls(LibraryModel& model, const SessionSnapshot& before,
    const ControlSnapshot& controls = stored_controls(), std::uint64_t sequence = 1,
    std::uint64_t now = 1) {
    (void)submit_control(model, controls, observed(before), sequence);
    const auto after = acknowledged(before, controls, sequence);
    model.observe(observed(after), now);
    REQUIRE(!model.view().controls_pending);
    REQUIRE(model.view().observation_fresh);
    return after;
}

LibraryRecallIntent recall(LibraryModel& model, const LibraryEntry& target,
    const SessionSnapshot& actual, const ControlSnapshot& desired = other_controls(),
    std::uint64_t now = 10) {
    REQUIRE(model.select(target.key));
    const auto request = model.request_recall(target, desired, observed(actual), now);
    REQUIRE(request.outcome == LibraryOutcome::Accepted);
    REQUIRE(request.recall.has_value());
    REQUIRE(request.recall->operation_id != 0);
    REQUIRE(operation(model).phase == LibraryOperationPhase::AwaitingSubmission);
    return *request.recall;
}

SessionSnapshot prove_recall(LibraryModel& model, const LibraryEntry& target,
    const SessionSnapshot& before, std::uint64_t sequence = 1,
    std::uint64_t now = 10) {
    const auto intent = recall(model, target, before, before.controls, now);
    REQUIRE(model.submitted({SessionStatus::Ok, sequence}, intent.control_intent) ==
        LibraryOutcome::Accepted);
    const auto after = acknowledged(before, intent.control_intent.expected_controls, sequence);
    model.observe(observed(after), now + 1);
    terminal(model, LibraryOutcome::Applied);
    return after;
}

LibrarySaveIntent stage_save(LibraryModel& model, const SessionSnapshot& actual,
    std::string_view name = "Saved", std::uint64_t now = 10) {
    REQUIRE(model.set_name(name));
    const auto request = model.request_save_new(observed(actual, actual.running), now);
    REQUIRE(request.outcome == LibraryOutcome::Accepted);
    REQUIRE(!request.recall.has_value());
    REQUIRE(operation(model).phase == LibraryOperationPhase::ReadyToSave);
    const auto effect = model.take_save_intent(observed(actual, actual.running), now + 1);
    REQUIRE(effect.has_value());
    REQUIRE(operation(model).phase == LibraryOperationPhase::Saving);
    return *effect;
}

LibrarySaveResult committed(const LibrarySaveIntent& effect,
    LibrarySaveStatus status = LibrarySaveStatus::Saved) {
    LibrarySaveResult result;
    result.status = status;
    result.committed_entry = entry(effect.name, effect.scope, effect.acknowledged_controls);
    result.refreshed_catalog = catalog({*result.committed_entry});
    REQUIRE(result.refreshed_catalog->generation == 0);
    return result;
}

void initial_state_drafts_and_copied_views() {
    LibraryModel model;
    const auto initial = model.view();
    REQUIRE(initial.catalog_stale);
    REQUIRE(initial.catalog.entries.empty());
    REQUIRE(initial.name_draft.empty());
    REQUIRE(initial.save_scope == RegistrationScope::Registration);
    REQUIRE(!initial.selected_key && !initial.selected_preview);
    REQUIRE(!initial.current_reference && !initial.operation);
    REQUIRE(!initial.controls_pending && !initial.observation_fresh);
    (void)model.select_relative(0);
    REQUIRE(!model.view().selected_key);
    REQUIRE(!model.select("Alpha.b3registration"));

    for (const auto draft : {"", " ", "-", "_", "CON", "trailing ", " Upper-A_2 "}) {
        REQUIRE(model.set_name(draft));
        REQUIRE(model.view().name_draft == draft);
    }
    const std::string longest(48, 'A');
    REQUIRE(model.set_name(longest));
    const std::array<std::string, 9> invalid{{std::string(49, 'A'), "A.B", "A/B", "A\\B",
        "A:B", "A\nB", std::string("A\0B", 3), std::string("A\xC3\xA9"), "A?B"}};
    for (const auto& draft : invalid) {
        REQUIRE(!model.set_name(draft));
        REQUIRE(model.view().name_draft == longest);
    }
    REQUIRE(model.set_save_scope(RegistrationScope::Performance));
    REQUIRE(!model.set_save_scope(static_cast<RegistrationScope>(255)));
    REQUIRE(model.view().save_scope == RegistrationScope::Performance);
    auto copied = model.view();
    copied.name_draft = "External";
    copied.save_scope = RegistrationScope::Registration;
    REQUIRE(model.view().name_draft == longest);
    REQUIRE(model.view().save_scope == RegistrationScope::Performance);
}

void catalog_generations_selection_and_failures() {
    LibraryModel model;
    auto unsolicited = catalog({entry()});
    unsolicited.generation = 1;
    REQUIRE(!model.replace_catalog(unsolicited));
    REQUIRE(model.view().catalog.entries.empty());
    const auto first = model.request_refresh();
    const auto second = model.request_refresh();
    REQUIRE(first && second && first->generation == 1 && second->generation == 2);
    unsolicited.generation = first->generation;
    REQUIRE(!model.replace_catalog(unsolicited));
    unsolicited.generation = 0;
    REQUIRE(!model.replace_catalog(unsolicited));
    auto rows = catalog({disabled("Alpha", LibraryEntryStatus::InvalidPayload),
        entry("beta"), entry("beta", RegistrationScope::Performance), entry("Zulu")});
    rows.generation = second->generation;
    REQUIRE(model.replace_catalog(rows));
    REQUIRE(model.view().selected_key == std::optional<std::string>{"Alpha.b3registration"});
    REQUIRE(!model.replace_catalog(rows));
    REQUIRE(!model.select("alpha.b3registration"));
    REQUIRE(model.view().selected_preview->status == LibraryEntryStatus::InvalidPayload);
    REQUIRE(model.select_relative(std::numeric_limits<int>::max()));
    REQUIRE(model.view().selected_key == std::optional<std::string>{"Zulu.b3registration"});
    REQUIRE(model.select_relative(std::numeric_limits<int>::min()));
    REQUIRE(model.view().selected_key == std::optional<std::string>{"Alpha.b3registration"});
    REQUIRE(model.select("beta.b3performance"));
    (void)publish(model, catalog({entry("Able"), entry("beta", RegistrationScope::Performance),
        entry("Zulu")}));
    REQUIRE(model.view().selected_key == std::optional<std::string>{"beta.b3performance"});
    (void)publish(model, catalog({entry("Able"), entry("Zulu")}));
    REQUIRE(!model.view().selected_key && !model.view().selected_preview);
    (void)model.select_relative(0);
    REQUIRE(!model.view().selected_key);
    REQUIRE(model.select_relative(-1));
    REQUIRE(model.view().selected_key == std::optional<std::string>{"Zulu.b3registration"});
    (void)publish(model, catalog());
    REQUIRE(!model.view().selected_key);
    (void)publish(model, catalog({entry("Able"), entry("Zulu")}));
    REQUIRE(!model.view().selected_key); // Removed selection is not silently replaced.
    REQUIRE(model.select_relative(1));
    REQUIRE(model.view().selected_key == std::optional<std::string>{"Able.b3registration"});

    const auto retained = model.view();
    const auto pending = model.request_refresh();
    REQUIRE(pending && model.view().catalog_stale);
    auto failed = catalog({entry("Injected")});
    failed.generation = pending->generation;
    failed.status = LibraryCatalogStatus::DirectoryUnavailable;
    failed.reason = std::string(500, 'X');
    (void)model.replace_catalog(failed);
    const auto stale = model.view();
    REQUIRE(stale.catalog_stale);
    REQUIRE(stale.catalog.generation == retained.catalog.generation);
    REQUIRE(stale.catalog.entries.size() == 2);
    REQUIRE(stale.catalog.entries[0].key == "Able.b3registration");
    REQUIRE(stale.selected_key == retained.selected_key);
    REQUIRE(stale.last_scan_status == LibraryCatalogStatus::DirectoryUnavailable);
    REQUIRE(!stale.last_scan_reason.empty() && stale.last_scan_reason.size() <= 256);
    REQUIRE(model.select("Zulu.b3registration"));
    const auto denied = model.request_recall(entry("Zulu"), other_controls(), observed(snapshot()), 1);
    REQUIRE(denied.outcome == LibraryOutcome::CatalogUnavailable);
    REQUIRE(!denied.recall);
    auto copy = model.view();
    copy.catalog.entries[0].name = "External";
    copy.selected_preview->name = "External";
    REQUIRE(model.view().catalog.entries[0].name == "Able");
    REQUIRE(model.view().selected_preview->name == "Zulu");
}

void complete_catalog_statuses_and_bounds() {
    for (const auto status : {LibraryCatalogStatus::Empty, LibraryCatalogStatus::MissingDirectory}) {
        LibraryModel model;
        auto value = catalog();
        value.status = status;
        (void)publish(model, value);
        REQUIRE(model.view().last_scan_status == status);
        REQUIRE(!model.view().selected_key);
    }
    LibraryModel full;
    std::vector<LibraryEntry> rows;
    for (unsigned index = 0; index < 128; ++index) {
        auto number = std::to_string(index);
        number.insert(0, 3 - number.size(), '0');
        rows.push_back(entry("Row" + number));
    }
    auto exact = catalog(rows);
    exact.directory_items = 512;
    (void)publish(full, exact);
    REQUIRE(full.view().catalog.entries.size() == 128);
    REQUIRE(full.view().catalog.directory_items == 512);

    using Mutation = std::function<void(LibraryCatalog&)>;
    const std::array<Mutation, 16> mutations{{
        [](auto& value) { value.entries.push_back(entry("Row128")); ++value.candidate_count; },
        [](auto& value) { value.directory_items = 513; },
        [](auto& value) { value.candidate_count = 129; },
        [](auto& value) { value.candidate_count = 127; },
        [](auto& value) { value.directory_items = 127; },
        [](auto& value) { value.invalid_name_count = 1; },
        [](auto& value) { value.invalid_entry_count = 1; },
        [](auto& value) { value.ambiguous_entry_count = 1; },
        [](auto& value) { value.invalid_name_count = std::numeric_limits<std::size_t>::max(); },
        [](auto& value) { value.candidate_count = std::numeric_limits<std::size_t>::max(); },
        [](auto& value) { value.directory_items = std::numeric_limits<std::size_t>::max(); },
        [](auto& value) { value.status = LibraryCatalogStatus::Empty; },
        [](auto& value) { value.status = LibraryCatalogStatus::MissingDirectory; },
        [](auto& value) { value.status = static_cast<LibraryCatalogStatus>(255); },
        [](auto& value) { std::swap(value.entries[0], value.entries[1]); },
        [](auto& value) { value.entries[1] = value.entries[0]; }
    }};
    for (const auto& mutate : mutations) {
        LibraryModel model;
        const auto original = publish(model, catalog({entry("Retained")}));
        auto bad = exact;
        mutate(bad);
        const auto refresh = model.request_refresh();
        REQUIRE(refresh);
        bad.generation = refresh->generation;
        REQUIRE(!model.replace_catalog(bad));
        REQUIRE(model.view().catalog_stale);
        REQUIRE(model.view().catalog.generation == original);
        REQUIRE(model.view().catalog.entries.size() == 1);
        REQUIRE(model.view().catalog.entries[0].name == "Retained");
    }
    LibraryModel omitted;
    auto valid_omission = catalog({entry()});
    valid_omission.invalid_name_count = 127;
    valid_omission.candidate_count = 128;
    valid_omission.directory_items = 128;
    (void)publish(omitted, valid_omission);
    REQUIRE(omitted.view().catalog.invalid_name_count == 127);
}

void catalog_row_admission_and_case_ambiguity() {
    using Mutation = std::function<void(LibraryCatalog&)>;
    const std::array<Mutation, 13> mutations{{
        [](auto& value) { value.entries[0].key = "Other.b3registration"; },
        [](auto& value) { value.entries[0].key = "Alpha.b3performance"; },
        [](auto& value) { value.entries[0].name = "../Alpha"; },
        [](auto& value) { value.entries[0].scope = static_cast<RegistrationScope>(255); },
        [](auto& value) { value.entries[0].status = static_cast<LibraryEntryStatus>(255); },
        [](auto& value) { value.entries[0].controls.reset(); },
        [](auto& value) { value.entries[0].controls->expression = -0.1; },
        [](auto& value) { value.entries[0].controls->drawbars[1][1][8] = 9; },
        [](auto& value) { value.entries[0].controls->fixed_registrations[1] =
            static_cast<FixedRegistration>(255); },
        [](auto& value) { value.entries[0].status = LibraryEntryStatus::InvalidPayload;
            value.invalid_entry_count = 1; },
        [](auto& value) { value.entries[0].status = LibraryEntryStatus::Ambiguous;
            value.ambiguous_entry_count = 1; },
        [](auto& value) { value.entries.push_back(entry("alpha"));
            value.directory_items = 2; value.candidate_count = 2; },
        [](auto& value) { value.entries = {entry("Alpha", RegistrationScope::Performance),
            entry("Alpha")}; value.directory_items = 2; value.candidate_count = 2; }
    }};
    for (const auto& mutate : mutations) {
        LibraryModel model;
        auto bad = catalog({entry()});
        mutate(bad);
        const auto refresh = model.request_refresh();
        REQUIRE(refresh);
        bad.generation = refresh->generation;
        REQUIRE(!model.replace_catalog(bad));
        REQUIRE(model.view().catalog_stale && model.view().catalog.entries.empty());
    }

    LibraryModel model;
    const auto actual = snapshot();
    auto upper = disabled("Alpha", LibraryEntryStatus::Ambiguous);
    auto lower = disabled("alpha", LibraryEntryStatus::Ambiguous);
    upper.reason = std::string(300, 'A');
    initialize(model, actual, {upper, lower, entry("Alpha", RegistrationScope::Performance)});
    REQUIRE(model.view().catalog.ambiguous_entry_count == 2);
    REQUIRE(model.view().catalog.entries[0].reason.size() <= 256);
    REQUIRE(model.select("Alpha.b3registration"));
    const auto denied = model.request_recall(entry(), actual.controls, observed(actual), 1);
    REQUIRE(denied.outcome == LibraryOutcome::InvalidEntry);
    REQUIRE(!denied.recall && !model.view().operation);
    REQUIRE(model.view().selected_preview->status == LibraryEntryStatus::Ambiguous);
    REQUIRE(model.view().catalog.ambiguous_entry_count == 2);
    (void)publish(model, catalog({entry(), entry("Alpha", RegistrationScope::Performance)}));
    REQUIRE(model.view().catalog.ambiguous_entry_count == 0);
    REQUIRE(recall(model, entry(), actual, actual.controls, 2).operation_id == 1);
}

void revalidation_is_explicit_and_atomic() {
    LibraryModel model;
    const auto actual = snapshot();
    initialize(model, actual, {entry(), entry("Beta")});
    auto mismatched = entry("Beta");
    const auto wrong = model.request_recall(mismatched, actual.controls, observed(actual), 1);
    REQUIRE(wrong.outcome == LibraryOutcome::InvalidEntry);
    REQUIRE(!wrong.recall && !model.view().operation);
    REQUIRE(model.view().selected_preview->key == "Alpha.b3registration");

    auto invalid_desired = actual.controls;
    invalid_desired.percussion.harmonic = static_cast<PercussionHarmonic>(255);
    REQUIRE(model.request_recall(entry(), invalid_desired, observed(actual), 2).outcome ==
        LibraryOutcome::InvalidInput);
    REQUIRE(!model.view().operation && !model.view().controls_pending);

    auto changed = entry();
    changed.controls->drawbars[1][1][8] = 8;
    const auto review = model.request_recall(changed, actual.controls, observed(actual), 3);
    REQUIRE(review.outcome == LibraryOutcome::EntryChanged);
    REQUIRE(!review.recall && !model.view().operation);
    REQUIRE(model.view().selected_preview->controls == changed.controls);
    REQUIRE(model.view().catalog.entries[0].controls == changed.controls);
    REQUIRE(model.view().catalog.invalid_entry_count == 0);
    const auto request = model.request_recall(changed, actual.controls, observed(actual), 4);
    REQUIRE(request.outcome == LibraryOutcome::Accepted && request.recall);
    REQUIRE(request.recall->control_intent.desired_revision == 1);

    LibraryModel unavailable;
    initialize(unavailable, actual, {entry()});
    const auto bad = disabled("Alpha", LibraryEntryStatus::Unavailable);
    const auto failed = unavailable.request_recall(bad, actual.controls, observed(actual), 1);
    REQUIRE(failed.outcome == LibraryOutcome::InvalidEntry && !failed.recall);
    REQUIRE(unavailable.view().selected_preview->status == LibraryEntryStatus::Unavailable);
    REQUIRE(unavailable.view().catalog.invalid_entry_count == 1);
    REQUIRE(!unavailable.view().selected_preview->controls);
    const auto recovered = unavailable.request_recall(entry(), actual.controls, observed(actual), 2);
    REQUIRE(recovered.outcome == LibraryOutcome::EntryChanged && !recovered.recall);
    REQUIRE(unavailable.view().catalog.invalid_entry_count == 0);
    REQUIRE(unavailable.view().selected_preview->controls == entry().controls);
    REQUIRE(unavailable.request_recall(entry(), actual.controls, observed(actual), 3).recall);
}

void literal_scope_restore_and_latest_desired_expression() {
    for (const auto scope : {RegistrationScope::Registration, RegistrationScope::Performance}) {
        LibraryModel model;
        const auto actual = snapshot();
        const auto target = entry("Alpha", scope);
        initialize(model, actual, {target});
        auto pending_desired = actual.controls;
        pending_desired.expression = 0.625;
        const auto old = submit_control(model, pending_desired, observed(actual), 1);
        auto latest_desired = pending_desired;
        latest_desired.expression = 0.875;
        const auto named = recall(model, target, actual, latest_desired);
        REQUIRE(named.control_intent.desired_revision > old.desired_revision);
        auto expected = stored_controls();
        expected.expression = scope == RegistrationScope::Registration ? 0.875 : 0.25;
        REQUIRE(named.control_intent.expected_controls == expected);
        REQUIRE(named.control_intent.expected_controls.drawbars[0][0] ==
            (DrawbarPositions{8, 0, 3, 1, 6, 2, 7, 4, 5}));
        REQUIRE(named.control_intent.expected_controls.drawbars[0][1] ==
            (DrawbarPositions{1, 2, 3, 4, 5, 6, 7, 8, 0}));
        REQUIRE(named.control_intent.expected_controls.drawbars[1][0] ==
            (DrawbarPositions{2, 4, 6, 8, 0, 1, 3, 5, 7}));
        REQUIRE(named.control_intent.expected_controls.drawbars[1][1] ==
            (DrawbarPositions{7, 5, 3, 1, 8, 6, 4, 2, 0}));
        REQUIRE(named.control_intent.expected_controls.pedal_drawbars ==
            (PedalDrawbarPositions{7, 3}));
        REQUIRE(named.control_intent.expected_controls.route_enabled == (std::array{false, true}));
        REQUIRE(named.control_intent.expected_controls.fixed_registrations ==
            (std::array{FixedRegistration::DSharp, FixedRegistration::GSharp}));
        REQUIRE(model.submitted({SessionStatus::Ok, 2}, named.control_intent) ==
            LibraryOutcome::Accepted);
        const auto old_applied = acknowledged(actual, pending_desired, 1);
        model.observe(observed(old_applied), 11);
        REQUIRE(model.view().controls_pending && !model.view().current_reference);
        REQUIRE(operation(model).phase == LibraryOperationPhase::AwaitingAcknowledgment);
        const auto named_applied = acknowledged(old_applied, expected, 2);
        model.observe(observed(named_applied), 12);
        terminal(model, LibraryOutcome::Applied);
        REQUIRE(reference(model).scope == scope);
        REQUIRE(reference(model).origin == LibraryReferenceOrigin::Recall);
        REQUIRE(!reference(model).modified);
        REQUIRE(!model.view().controls_pending);
    }
}

void selected_current_and_operation_identities() {
    LibraryModel model;
    const auto first = entry("Alpha", RegistrationScope::Performance);
    const auto second = entry("Beta", RegistrationScope::Registration, other_controls());
    const auto third = entry("Gamma");
    const auto initial = snapshot();
    initialize(model, initial, {first, second, third});
    const auto actual = prove_recall(model, first, initial);
    REQUIRE(reference(model).key == first.key);
    const auto pending = recall(model, second, actual, actual.controls, 12);
    REQUIRE(model.select(third.key));
    REQUIRE(model.set_name("New draft"));
    REQUIRE(model.set_save_scope(RegistrationScope::Performance));
    const auto view = model.view();
    REQUIRE(view.selected_key == std::optional<std::string>{third.key});
    REQUIRE(view.current_reference->key == first.key);
    REQUIRE(view.operation->target_key == second.key);
    REQUIRE(view.operation->target_name == "Beta");
    REQUIRE(view.operation->target_scope == RegistrationScope::Registration);
    REQUIRE(view.name_draft == "New draft");
    REQUIRE(view.save_scope == RegistrationScope::Performance);
    const auto busy = model.request_recall(third, actual.controls, observed(actual), 13);
    REQUIRE(busy.outcome == LibraryOutcome::Busy && !busy.recall);
    REQUIRE(model.request_save_new(observed(actual), 13).outcome == LibraryOutcome::Busy);
    REQUIRE(operation(model).operation_id == pending.operation_id);
    REQUIRE(model.submitted({SessionStatus::Ok, 2}, pending.control_intent) == LibraryOutcome::Accepted);
    const auto after = acknowledged(actual, pending.control_intent.expected_controls, 2);
    model.observe(observed(after), 14);
    terminal(model, LibraryOutcome::Applied);
    REQUIRE(reference(model).key == second.key);
    REQUIRE(model.view().selected_key == std::optional<std::string>{third.key});
    REQUIRE(model.view().name_draft == "New draft");

    const auto receipt = operation(model);
    REQUIRE(!model.select("Removed.b3registration"));
    const auto wrong = model.request_recall(first, actual.controls, observed(after), 15);
    REQUIRE(!wrong.recall && wrong.outcome != LibraryOutcome::Accepted);
    REQUIRE(operation(model).operation_id == receipt.operation_id);
    REQUIRE(operation(model).outcome == LibraryOutcome::Applied);
}

void queued_equal_controls_need_original_newer_proof() {
    LibraryModel model;
    const auto target = entry("Alpha", RegistrationScope::Performance);
    const auto before = snapshot(stored_controls());
    initialize(model, before, {target});
    const auto named = recall(model, target, before, before.controls);
    REQUIRE(named.control_intent.expected_controls == before.controls);
    REQUIRE(!model.view().current_reference);
    REQUIRE(model.view().controls_pending);
    REQUIRE(model.submitted({SessionStatus::Ok, 1}, named.control_intent) == LibraryOutcome::Accepted);
    REQUIRE(operation(model).phase == LibraryOperationPhase::AwaitingAcknowledgment);
    model.observe(observed(before), 11);
    REQUIRE(!model.view().current_reference && model.view().controls_pending);
    auto still_queued = before;
    still_queued.publication_revision = 4;
    model.observe(observed(still_queued), 12);
    REQUIRE(!model.view().current_reference);
    REQUIRE(operation(model).phase == LibraryOperationPhase::AwaitingAcknowledgment);
    const auto after = acknowledged(still_queued, before.controls, 1);
    model.observe(observed(after), 13);
    terminal(model, LibraryOutcome::Applied);
    REQUIRE(reference(model).key == target.key);

    // Session resolves consumed commands, including rejected/discarded ones.
    // Once this command is resolved without application, a later applied
    // sequence cannot establish that the original command ever applied.
    LibraryModel consumed;
    initialize(consumed, before, {target});
    const auto original = recall(consumed, target, before, before.controls);
    REQUIRE(consumed.submitted({SessionStatus::Ok, 1}, original.control_intent) == LibraryOutcome::Accepted);
    auto resolved_only = before;
    resolved_only.publication_revision = 4;
    resolved_only.resolved_sequence = 1;
    consumed.observe(observed(resolved_only), 12);
    terminal(consumed, LibraryOutcome::Unconfirmed);
    REQUIRE(!consumed.view().current_reference && !consumed.view().controls_pending);
    const auto unrelated_later = acknowledged(resolved_only, before.controls, 2);
    consumed.observe(observed(unrelated_later), 13);
    terminal(consumed, LibraryOutcome::Unconfirmed);
    REQUIRE(!consumed.view().current_reference);
}

void same_value_intent_supersedes_without_revival() {
    LibraryModel model;
    const auto target = entry("Alpha", RegistrationScope::Performance);
    const auto before = snapshot();
    initialize(model, before, {target});
    const auto named = recall(model, target, before);
    REQUIRE(model.submitted({SessionStatus::Ok, 1}, named.control_intent) == LibraryOutcome::Accepted);
    const auto next = model.note_control_intent(named.control_intent.expected_controls, observed(before));
    REQUIRE(next && next->desired_revision == named.control_intent.desired_revision + 1);
    terminal(model, LibraryOutcome::Superseded);
    REQUIRE(model.view().controls_pending);
    REQUIRE(model.submitted({SessionStatus::Ok, 2}, next) == LibraryOutcome::Accepted);
    const auto old_ack = acknowledged(before, next->expected_controls, 1);
    model.observe(observed(old_ack), 11);
    REQUIRE(model.view().controls_pending && !model.view().current_reference);
    const auto new_ack = acknowledged(old_ack, next->expected_controls, 2);
    model.observe(observed(new_ack), 12);
    REQUIRE(!model.view().controls_pending);
    REQUIRE(!model.view().current_reference);
    terminal(model, LibraryOutcome::Superseded);
    REQUIRE(operation(model).operation_id == named.operation_id);
}

void no_startup_unsubmitted_or_unrelated_control_proof() {
    LibraryModel model;
    auto actual = snapshot(stored_controls());
    initialize(model, actual);
    REQUIRE(model.set_name("Save candidate"));
    REQUIRE(model.request_save_new(observed(actual), 1).outcome ==
        LibraryOutcome::NoAcknowledgedControls);
    REQUIRE(!model.view().operation);
    REQUIRE(model.submitted({SessionStatus::Ok, 1}) == LibraryOutcome::Accepted);
    actual = acknowledged(actual, actual.controls, 1);
    model.observe(observed(actual), 2);
    REQUIRE(model.request_save_new(observed(actual), 3).outcome ==
        LibraryOutcome::NoAcknowledgedControls);
    const auto intent = model.note_control_intent(actual.controls, observed(actual));
    REQUIRE(intent && model.view().controls_pending);
    REQUIRE(model.request_save_new(observed(actual), 4).outcome ==
        LibraryOutcome::NoAcknowledgedControls);
    REQUIRE(!model.take_save_intent(observed(actual), 5));
    REQUIRE(model.submitted({SessionStatus::Ok, 2}, intent) == LibraryOutcome::Accepted);
    REQUIRE(model.request_save_new(observed(actual), 6).outcome == LibraryOutcome::Accepted);
    REQUIRE(operation(model).phase == LibraryOperationPhase::AwaitingAcknowledgment);
    REQUIRE(!model.take_save_intent(observed(actual), 7));
    actual = acknowledged(actual, actual.controls, 2);
    model.observe(observed(actual), 8);
    REQUIRE(operation(model).phase == LibraryOperationPhase::ReadyToSave);
}

void missing_prepost_read_cannot_be_repaired() {
    LibraryModel model;
    const auto before = snapshot();
    initialize(model, before);
    (void)submit_control(model, stored_controls(), failed_read(), 1);
    const auto after = acknowledged(before, stored_controls(), 1);
    model.observe(observed(after), 1);
    REQUIRE(model.set_name("No original proof"));
    REQUIRE(model.request_save_new(observed(after), 2).outcome ==
        LibraryOutcome::NoAcknowledgedControls);
    REQUIRE(!model.take_save_intent(observed(after), 3));
    REQUIRE(!model.view().current_reference);
}

void failed_old_and_malformed_observations_supply_no_proof() {
    LibraryModel model;
    const auto target = entry("Alpha", RegistrationScope::Performance);
    const auto before = snapshot();
    initialize(model, before, {target});
    const auto named = recall(model, target, before);
    REQUIRE(model.submitted({SessionStatus::Ok, 1}, named.control_intent) == LibraryOutcome::Accepted);
    model.observe(failed_read(), 11);
    REQUIRE(!model.view().observation_fresh && !model.view().current_reference);
    auto impossible = acknowledged(before, stored_controls(), 1);
    impossible.resolved_sequence = 0;
    model.observe(observed(impossible), 12);
    REQUIRE(!model.view().observation_fresh && !model.view().current_reference);
    auto odd = acknowledged(before, stored_controls(), 1);
    odd.publication_revision = 3;
    model.observe(observed(odd), 13);
    REQUIRE(!model.view().observation_fresh && !model.view().current_reference);
    auto bad_controls = acknowledged(before, stored_controls(), 1);
    bad_controls.controls.expression = std::numeric_limits<double>::quiet_NaN();
    model.observe(observed(bad_controls), 14);
    REQUIRE(!model.view().observation_fresh && !model.view().current_reference);
    auto incoherent_lifecycle = acknowledged(before, stored_controls(), 1);
    incoherent_lifecycle.prepared = false;
    model.observe(observed(incoherent_lifecycle), 15);
    REQUIRE(!model.view().observation_fresh && !model.view().current_reference);
    const auto after = acknowledged(before, stored_controls(), 1);
    model.observe(observed(after), 16);
    terminal(model, LibraryOutcome::Applied);
    REQUIRE(!reference(model).modified);
    model.observe(observed(before), 17);
    REQUIRE(!model.view().observation_fresh && !reference(model).modified);
    model.observe(failed_read(), 18);
    REQUIRE(!model.view().observation_fresh && !reference(model).modified);
    terminal(model, LibraryOutcome::Applied);
}

void repeated_publication_requires_every_field_equal() {
    using Mutation = std::function<void(SessionSnapshot&)>;
    const std::array<Mutation, 18> mutations{{
        [](auto& value) { value.controls.expression = 0.75; },
        [](auto& value) { value.held_keys[0][24] = false; },
        [](auto& value) { value.held_keys[1][19] = false; },
        [](auto& value) { value.held_pedals[4] = false; },
        [](auto& value) { ++value.frame_clock; },
        [](auto& value) { value.sample_rate = 44100.0; },
        [](auto& value) { value.peak = 0.25F; },
        [](auto& value) { value.prepared = false; value.running = false; },
        [](auto& value) { value.running = false; },
        [](auto& value) { ++value.resolved_sequence; },
        [](auto& value) { value.last_applied_sequence = 0; },
        [](auto& value) { ++value.recovery_count; },
        [](auto& value) { ++value.queue_overflows; },
        [](auto& value) { ++value.rejected_commands; },
        [](auto& value) { ++value.discarded_commands; },
        [](auto& value) { value.fault_flags = static_cast<std::uint32_t>(SessionFault::RenderRejected); },
        [](auto& value) { value.last_core_status = Status::InvalidBuffer; },
        [](auto& value) { value.controls.fixed_registrations[0] = FixedRegistration::None; }
    }};
    for (const auto& mutate : mutations) {
        LibraryModel model;
        const auto target = entry("Alpha", RegistrationScope::Performance);
        const auto before = snapshot();
        initialize(model, before, {target});
        const auto actual = prove_recall(model, target, before);
        REQUIRE(!reference(model).modified);
        auto conflict = actual;
        mutate(conflict);
        model.observe(observed(conflict), 12);
        REQUIRE(!model.view().observation_fresh);
        REQUIRE(!reference(model).modified);
        terminal(model, LibraryOutcome::Applied);
        model.observe(observed(actual), 13);
        REQUIRE(model.view().observation_fresh);
        REQUIRE(!reference(model).modified);
    }
}

void failure_guards_prevent_larger_sequence_substitution() {
    using Counter = std::uint64_t SessionSnapshot::*;
    constexpr std::array<Counter, 3> counters{{&SessionSnapshot::recovery_count,
        &SessionSnapshot::rejected_commands, &SessionSnapshot::discarded_commands}};
    for (const auto counter : counters) {
        LibraryModel model;
        const auto target = entry("Alpha", RegistrationScope::Performance);
        const auto before = snapshot();
        initialize(model, before, {target});
        const auto named = recall(model, target, before);
        REQUIRE(model.submitted({SessionStatus::Ok, 1}, named.control_intent) == LibraryOutcome::Accepted);
        REQUIRE(model.submitted({SessionStatus::Ok, 2}) == LibraryOutcome::Accepted);
        auto later_note = acknowledged(before, stored_controls(), 2);
        ++(later_note.*counter);
        model.observe(observed(later_note), 11);
        terminal(model, LibraryOutcome::Rejected);
        REQUIRE(!model.view().controls_pending && !model.view().current_reference);
        REQUIRE(model.set_name("No recaptured proof"));
        REQUIRE(model.request_save_new(observed(later_note), 12).outcome ==
            LibraryOutcome::NoAcknowledgedControls);
        later_note.publication_revision += 2;
        later_note.resolved_sequence = 3;
        later_note.last_applied_sequence = 3;
        model.observe(observed(later_note), 13);
        terminal(model, LibraryOutcome::Rejected);
        REQUIRE(!model.view().current_reference);
        REQUIRE(model.request_save_new(observed(later_note), 14).outcome ==
            LibraryOutcome::NoAcknowledgedControls);
    }
    for (const auto counter : counters) {
        LibraryModel model;
        auto before = snapshot();
        before.*counter = kMax;
        initialize(model, before, {entry()});
        const auto result = model.request_recall(entry(), before.controls, observed(before), 1);
        REQUIRE(!result.recall);
        REQUIRE(result.outcome != LibraryOutcome::Accepted);
        REQUIRE(!model.view().operation);
    }
}

void unrelated_synchronous_failures_invalidate_waits() {
    for (const auto status : {SessionStatus::InvalidCommand, SessionStatus::QueueFull,
             SessionStatus::RecoveryPending, SessionStatus::NotRunning,
             SessionStatus::SequenceExhausted}) {
        LibraryModel model;
        const auto before = snapshot();
        const auto target = entry("Alpha", RegistrationScope::Performance);
        initialize(model, before, {target});
        const auto named = recall(model, target, before);
        REQUIRE(model.submitted({SessionStatus::Ok, 1}, named.control_intent) == LibraryOutcome::Accepted);
        REQUIRE(model.submitted({status, 0}) == LibraryOutcome::Rejected);
        terminal(model, LibraryOutcome::Rejected);
        REQUIRE(!model.view().controls_pending);
        const auto apparent_ack = acknowledged(before, stored_controls(), 1);
        model.observe(observed(apparent_ack), 11);
        terminal(model, LibraryOutcome::Rejected);
        REQUIRE(!model.view().current_reference);
        REQUIRE(model.set_name("Not acknowledged"));
        REQUIRE(model.request_save_new(observed(apparent_ack), 12).outcome ==
            LibraryOutcome::NoAcknowledgedControls);
    }

    // An older failed expression must not replace the explicit current desired
    // expression supplied at the next Registration activation.
    LibraryModel model;
    const auto actual = snapshot();
    initialize(model, actual, {entry()});
    auto optimistic = actual.controls;
    optimistic.expression = 0.9375;
    const auto intent = model.note_control_intent(optimistic, observed(actual));
    REQUIRE(intent);
    REQUIRE(model.submitted({SessionStatus::InvalidCommand, 0}, intent) == LibraryOutcome::Rejected);
    REQUIRE(!model.view().controls_pending);
    const auto named = recall(model, entry(), actual, actual.controls);
    REQUIRE(named.control_intent.expected_controls.expression == 0.5);
}

void malformed_submission_tokens_fail_closed() {
    for (unsigned variant = 0; variant < 6; ++variant) {
        LibraryModel model;
        const auto before = snapshot();
        const auto target = entry("Alpha", RegistrationScope::Performance);
        initialize(model, before, {target});
        const auto named = recall(model, target, before);
        auto token = named.control_intent;
        SubmitResult result{SessionStatus::Ok, 1};
        if (variant == 0) result.sequence = 0;
        if (variant == 1) result.status = SessionStatus::QueueFull;
        if (variant == 2) token.desired_revision = 0;
        if (variant == 3) ++token.desired_revision;
        if (variant == 4) token.expected_controls.expression = 0.875;
        if (variant == 5) {
            REQUIRE(model.submitted({SessionStatus::Ok, 1}, token) == LibraryOutcome::Accepted);
            result.sequence = 2;
        }
        REQUIRE(model.submitted(result, token) == LibraryOutcome::ProtocolError);
        terminal(model, LibraryOutcome::ProtocolError);
        const auto after = acknowledged(before, stored_controls(), 2);
        model.observe(observed(after), 11);
        REQUIRE(!model.view().current_reference);
    }
    LibraryModel model;
    REQUIRE(model.submitted({SessionStatus::Ok, 5}) == LibraryOutcome::Accepted);
    REQUIRE(model.submitted({SessionStatus::Ok, 4}) == LibraryOutcome::ProtocolError);
    REQUIRE(model.submitted({SessionStatus::Ok, 5}) == LibraryOutcome::ProtocolError);
}

void actual_modified_pending_and_missing_are_distinct() {
    for (const auto scope : {RegistrationScope::Registration, RegistrationScope::Performance}) {
        LibraryModel model;
        const auto target = entry("Alpha", scope);
        const auto before = snapshot();
        initialize(model, before, {target, entry("Beta")});
        auto actual = prove_recall(model, target, before);
        auto desired = actual.controls;
        desired.expression = 0.875;
        (void)submit_control(model, desired, observed(actual), 2);
        REQUIRE(model.view().controls_pending);
        REQUIRE(!reference(model).modified); // Optimism is not actual modification.
        actual = acknowledged(actual, desired, 2);
        model.observe(observed(actual), 12);
        REQUIRE(!model.view().controls_pending);
        REQUIRE(reference(model).modified == (scope == RegistrationScope::Performance));
        actual.controls.drawbars[1][0][8] = 8;
        actual.publication_revision += 2;
        model.observe(observed(actual), 13);
        REQUIRE(reference(model).modified);
        const auto generation = model.request_refresh();
        REQUIRE(generation);
        auto failed = catalog();
        failed.generation = generation->generation;
        failed.status = LibraryCatalogStatus::DirectoryUnavailable;
        failed.reason = "Directory unavailable";
        (void)model.replace_catalog(failed);
        REQUIRE(!reference(model).missing);
        (void)publish(model, catalog({entry("Beta")}));
        REQUIRE(reference(model).missing);
        auto invalid = disabled("Alpha", LibraryEntryStatus::InvalidPayload);
        if (scope == RegistrationScope::Performance) {
            invalid.scope = scope;
            invalid.key = "Alpha.b3performance";
        }
        (void)publish(model, catalog({invalid, entry("Beta")}));
        REQUIRE(!reference(model).missing && reference(model).modified);
        REQUIRE(reference(model).origin == LibraryReferenceOrigin::Recall);
    }
}

void audio_gates_and_explicit_lifecycle_boundaries() {
    for (unsigned variant = 0; variant < 3; ++variant) {
        LibraryModel model;
        auto before = snapshot();
        bool enabled = true;
        if (variant == 0) before = SessionSnapshot{};
        if (variant == 1) before.running = false;
        if (variant == 2) enabled = false;
        (void)publish(model, catalog({entry()}));
        const auto denied = model.request_recall(entry(), other_controls(), observed(before, enabled), 1);
        REQUIRE(denied.outcome == LibraryOutcome::NoAudio);
        REQUIRE(!denied.recall && !model.view().controls_pending && !model.view().operation);
    }
    for (const auto transition : {LibraryAudioTransition::Stop, LibraryAudioTransition::Start,
             LibraryAudioTransition::Prepare}) {
        LibraryModel model;
        const auto before = snapshot();
        initialize(model, before, {entry()});
        const auto named = recall(model, entry(), before);
        REQUIRE(model.submitted({SessionStatus::Ok, 1}, named.control_intent) == LibraryOutcome::Accepted);
        model.audio_lifecycle_changed(transition);
        terminal(model, LibraryOutcome::Cancelled);
        const auto after = acknowledged(before, named.control_intent.expected_controls, 1);
        model.observe(observed(after), 11);
        terminal(model, LibraryOutcome::Cancelled);
        REQUIRE(!model.view().current_reference);
        REQUIRE(model.set_name("Cancelled basis"));
        REQUIRE(model.request_save_new(observed(after), 12).outcome ==
            LibraryOutcome::NoAcknowledgedControls);
    }
    for (unsigned variant = 0; variant < 2; ++variant) {
        LibraryModel model;
        const auto before = snapshot();
        initialize(model, before, {entry()});
        const auto named = recall(model, entry(), before);
        REQUIRE(model.submitted({SessionStatus::Ok, 1}, named.control_intent) == LibraryOutcome::Accepted);
        auto after = acknowledged(before, named.control_intent.expected_controls, 1);
        if (variant == 0) after.running = false;
        model.observe(observed(after, variant == 0), 11);
        terminal(model, LibraryOutcome::Cancelled);
        REQUIRE(!model.view().current_reference);
    }
}

void monotonic_time_deadline_and_overflow() {
    for (const std::uint64_t elapsed : {std::uint64_t{1999}, std::uint64_t{2000}}) {
        LibraryModel model;
        const auto target = entry("Alpha", RegistrationScope::Performance);
        const auto before = snapshot();
        initialize(model, before, {target});
        const auto named = recall(model, target, before, before.controls, 100);
        REQUIRE(model.submitted({SessionStatus::Ok, 1}, named.control_intent) == LibraryOutcome::Accepted);
        const auto after = acknowledged(before, stored_controls(), 1);
        model.observe(observed(after), 100 + elapsed);
        terminal(model, elapsed == 1999 ? LibraryOutcome::Applied : LibraryOutcome::Unconfirmed);
        REQUIRE(model.view().current_reference.has_value() == (elapsed == 1999));
        model.observe(observed(after), 2101);
        terminal(model, elapsed == 1999 ? LibraryOutcome::Applied : LibraryOutcome::Unconfirmed);
    }
    LibraryModel timeout;
    const auto before = snapshot();
    initialize(timeout, before, {entry()});
    (void)recall(timeout, entry(), before, before.controls, 100);
    timeout.observe(failed_read(), 2099);
    REQUIRE(operation(timeout).phase == LibraryOperationPhase::AwaitingSubmission);
    timeout.observe(failed_read(), 2100);
    terminal(timeout, LibraryOutcome::Unconfirmed);

    LibraryModel regression;
    initialize(regression, before, {entry()});
    const auto named = recall(regression, entry(), before, before.controls, 100);
    REQUIRE(regression.submitted({SessionStatus::Ok, 1}, named.control_intent) == LibraryOutcome::Accepted);
    const auto after = acknowledged(before, named.control_intent.expected_controls, 1);
    regression.observe(observed(after), 99);
    REQUIRE(!regression.view().observation_fresh && !regression.view().current_reference);
    regression.observe(observed(after), 101);
    terminal(regression, LibraryOutcome::Applied);
    REQUIRE(regression.request_recall(entry(), before.controls, observed(after), 100).outcome ==
        LibraryOutcome::InvalidInput);
    terminal(regression, LibraryOutcome::Applied);

    for (const std::uint64_t start : {kMax - 1999, kMax}) {
        LibraryModel model;
        initialize(model, before, {entry()});
        const auto denied = model.request_recall(entry(), before.controls, observed(before), start);
        REQUIRE(denied.outcome == LibraryOutcome::InvalidInput && !denied.recall);
        REQUIRE(!model.view().operation && !model.view().controls_pending);
    }
    LibraryModel last_deadline;
    initialize(last_deadline, before, {entry()});
    const auto accepted = recall(last_deadline, entry(), before, before.controls, kMax - 2000);
    REQUIRE(last_deadline.submitted({SessionStatus::Ok, 1}, accepted.control_intent) ==
        LibraryOutcome::Accepted);
    last_deadline.observe(failed_read(), kMax - 1);
    REQUIRE(operation(last_deadline).phase == LibraryOperationPhase::AwaitingAcknowledgment);
    last_deadline.observe(failed_read(), kMax);
    terminal(last_deadline, LibraryOutcome::Unconfirmed);
}

void stopped_proved_save_has_one_effect_and_permission() {
    LibraryModel model;
    const auto before = snapshot();
    initialize(model, before, {entry("Alpha")});
    auto actual = prove_controls(model, before);
    model.audio_lifecycle_changed(LibraryAudioTransition::Stop);
    model.audio_lifecycle_changed(LibraryAudioTransition::Start);
    model.audio_lifecycle_changed(LibraryAudioTransition::Stop);
    actual.running = false;
    actual.peak = 0.0F;
    actual.publication_revision += 2;
    model.observe(observed(actual, false), 2);
    REQUIRE(model.set_save_scope(RegistrationScope::Performance));
    const auto effect = stage_save(model, actual, "Saved performance");
    REQUIRE(effect.name == "Saved performance");
    REQUIRE(effect.key == "Saved performance.b3performance");
    REQUIRE(effect.scope == RegistrationScope::Performance);
    REQUIRE(effect.acknowledged_controls == stored_controls());
    REQUIRE(model.select("Alpha.b3registration"));
    REQUIRE(model.set_name("Later form"));
    REQUIRE(model.set_save_scope(RegistrationScope::Registration));
    REQUIRE(operation(model).target_name == "Saved performance");
    REQUIRE(operation(model).target_scope == RegistrationScope::Performance);
    REQUIRE(!model.take_save_intent(observed(actual, false), 12));
    REQUIRE(!model.authorize_save(effect.operation_id + 1, observed(actual, false), 12).permitted);
    REQUIRE(operation(model).phase == LibraryOperationPhase::Saving);
    REQUIRE(model.authorize_save(effect.operation_id, observed(actual, false), 12).permitted);
    REQUIRE(!model.authorize_save(effect.operation_id, observed(actual, false), 13).permitted);
    REQUIRE(model.request_save_new(observed(actual, false), 13).outcome == LibraryOutcome::Busy);
    const auto result = committed(effect);
    REQUIRE(model.complete_save(effect.operation_id, result) == LibraryOutcome::Saved);
    terminal(model, LibraryOutcome::Saved);
    REQUIRE(reference(model).key == effect.key);
    REQUIRE(reference(model).origin == LibraryReferenceOrigin::AcknowledgedSave);
    REQUIRE(!reference(model).modified && !reference(model).missing);
    REQUIRE(model.view().selected_key == std::optional<std::string>{effect.key});
    REQUIRE(model.view().name_draft == "Later form");
    REQUIRE(model.view().save_scope == RegistrationScope::Registration);
    REQUIRE(!model.view().controls_pending);
    REQUIRE(model.complete_save(effect.operation_id, result) == LibraryOutcome::StaleResult);
    REQUIRE(model.complete_save(effect.operation_id + 1, result) == LibraryOutcome::StaleResult);
    terminal(model, LibraryOutcome::Saved);
    REQUIRE(reference(model).key == effect.key);
}

void save_wait_retains_original_receipt_and_failure_guards() {
    LibraryModel model;
    const auto before = snapshot();
    initialize(model, before);
    (void)submit_control(model, stored_controls(), observed(before), 1);
    REQUIRE(model.set_name("Waiting original"));
    REQUIRE(model.request_save_new(observed(before), 10).outcome == LibraryOutcome::Accepted);
    const auto receipt = operation(model);
    REQUIRE(receipt.phase == LibraryOperationPhase::AwaitingAcknowledgment);
    REQUIRE(receipt.submitted_sequence == 1);
    REQUIRE(model.set_name("Different draft"));
    REQUIRE(model.set_save_scope(RegistrationScope::Performance));
    REQUIRE(model.submitted({SessionStatus::Ok, 2}) == LibraryOutcome::Accepted);
    auto rejected = acknowledged(before, stored_controls(), 2);
    rejected.discarded_commands = 1;
    model.observe(observed(rejected), 11);
    terminal(model, LibraryOutcome::Rejected);
    REQUIRE(!model.take_save_intent(observed(rejected), 12));
    REQUIRE(operation(model).target_name == "Waiting original");
    REQUIRE(operation(model).target_scope == RegistrationScope::Registration);
    REQUIRE(model.request_save_new(observed(rejected), 13).outcome ==
        LibraryOutcome::NoAcknowledgedControls);

    // A proved unchanged copy can support a later new Save after an unrelated
    // failure. The intervening failure still cancels an already waiting Save.
    LibraryModel retained;
    initialize(retained, before);
    const auto actual = prove_controls(retained, before);
    REQUIRE(retained.set_name("Old request"));
    REQUIRE(retained.request_save_new(observed(actual), 10).outcome == LibraryOutcome::Accepted);
    REQUIRE(retained.submitted({SessionStatus::InvalidCommand, 0}) == LibraryOutcome::Rejected);
    terminal(retained, LibraryOutcome::Rejected);
    REQUIRE(!retained.take_save_intent(observed(actual), 11));
    REQUIRE(retained.set_name("Fresh request"));
    REQUIRE(retained.request_save_new(observed(actual), 12).outcome == LibraryOutcome::Accepted);
    REQUIRE(operation(retained).phase == LibraryOperationPhase::ReadyToSave);
    const auto effect = retained.take_save_intent(observed(actual), 13);
    REQUIRE(effect && effect->name == "Fresh request");
    REQUIRE(retained.authorize_save(effect->operation_id, observed(actual), 14).permitted);
}

void take_requires_a_fresh_unchanged_observation() {
    for (unsigned variant = 0; variant < 4; ++variant) {
        LibraryModel model;
        const auto before = snapshot();
        initialize(model, before);
        auto actual = prove_controls(model, before);
        REQUIRE(model.set_name("Fresh at take"));
        REQUIRE(model.request_save_new(observed(actual), 10).outcome == LibraryOutcome::Accepted);
        if (variant == 0) {
            REQUIRE(!model.take_save_intent(failed_read(), 11));
        } else if (variant == 1) {
            actual.controls.expression = 0.75;
            actual.publication_revision += 2;
            REQUIRE(!model.take_save_intent(observed(actual), 11));
        } else if (variant == 2) {
            ++actual.rejected_commands;
            actual.publication_revision += 2;
            REQUIRE(!model.take_save_intent(observed(actual), 11));
        } else {
            REQUIRE(!model.take_save_intent(observed(actual), 2010));
            terminal(model, LibraryOutcome::Unconfirmed);
        }
        REQUIRE(operation(model).phase != LibraryOperationPhase::Saving);
        REQUIRE(!model.view().current_reference);
        REQUIRE(model.view().name_draft == "Fresh at take");
    }
}

void preauthorization_intent_failure_read_and_deadline_changes() {
    for (unsigned variant = 0; variant < 6; ++variant) {
        LibraryModel model;
        const auto before = snapshot();
        initialize(model, before);
        auto actual = prove_controls(model, before);
        const auto effect = stage_save(model, actual, "Staged original");
        auto fresh = observed(actual);
        std::uint64_t now = 12;
        if (variant == 0) {
            // Equal-value edits still change intent identity.
            REQUIRE(model.note_control_intent(actual.controls, observed(actual)));
            terminal(model, LibraryOutcome::Superseded);
        } else if (variant == 1) {
            REQUIRE(model.submitted({SessionStatus::InvalidCommand, 0}) == LibraryOutcome::Rejected);
        } else if (variant == 2) fresh = failed_read();
        else if (variant == 3) {
            actual.publication_revision += 2;
            ++actual.recovery_count;
            fresh = observed(actual);
        } else if (variant == 4) now = 2010;
        else model.audio_lifecycle_changed(LibraryAudioTransition::Prepare);
        const auto authorization = model.authorize_save(effect.operation_id, fresh, now);
        REQUIRE(!authorization.permitted && !authorization.reason.empty());
        const auto refused = operation(model);
        REQUIRE(refused.phase == LibraryOperationPhase::Finished);
        REQUIRE(refused.outcome != LibraryOutcome::Saved && refused.outcome != LibraryOutcome::SavedWithWarning);
        REQUIRE(!model.authorize_save(effect.operation_id, observed(actual), now).permitted);
        LibrarySaveResult denied;
        denied.status = LibrarySaveStatus::NotAuthorized;
        denied.reason = "Storage authorizer refused";
        REQUIRE(model.complete_save(effect.operation_id, denied) == refused.outcome);
        REQUIRE(operation(model).outcome == refused.outcome);
        REQUIRE(!model.view().current_reference);
        REQUIRE(model.view().name_draft == "Staged original");
    }
}

void authorized_commit_retains_truth_after_later_changes() {
    for (const auto status : {LibrarySaveStatus::Saved, LibrarySaveStatus::SavedWithWarning}) {
        LibraryModel model;
        const auto before = snapshot();
        initialize(model, before);
        const auto actual = prove_controls(model, before);
        const auto effect = stage_save(model, actual, "Committed past copy");
        REQUIRE(model.authorize_save(effect.operation_id, observed(actual), 12).permitted);
        auto desired = other_controls();
        desired.expression = 0.875;
        (void)submit_control(model, desired, observed(actual), 2);
        REQUIRE(operation(model).phase == LibraryOperationPhase::Saving);
        const auto later = acknowledged(actual, desired, 2);
        model.observe(observed(later), 13);
        model.audio_lifecycle_changed(LibraryAudioTransition::Stop);
        model.audio_lifecycle_changed(LibraryAudioTransition::Start);
        model.audio_lifecycle_changed(LibraryAudioTransition::Prepare);
        model.observe(failed_read(), 5000);
        REQUIRE(operation(model).phase == LibraryOperationPhase::Saving);
        REQUIRE(!model.take_save_intent(observed(later), 5001));
        auto result = committed(effect, status);
        result.reason = status == LibrarySaveStatus::Saved ? "" : "Committed; staging cleanup failed";
        const auto expected = status == LibrarySaveStatus::Saved ?
            LibraryOutcome::Saved : LibraryOutcome::SavedWithWarning;
        REQUIRE(model.complete_save(effect.operation_id, result) == expected);
        terminal(model, expected);
        REQUIRE(reference(model).key == effect.key);
        REQUIRE(reference(model).origin == LibraryReferenceOrigin::AcknowledgedSave);
        REQUIRE(reference(model).modified && !reference(model).missing);
        REQUIRE(!model.view().controls_pending);
        REQUIRE(effect.acknowledged_controls == stored_controls());
        REQUIRE(model.complete_save(effect.operation_id, result) == LibraryOutcome::StaleResult);
        terminal(model, expected);
    }
}

void committed_warning_and_inconsistent_metadata_truth() {
    using Mutation = std::function<void(LibrarySaveResult&)>;
    const std::array<Mutation, 7> mutations{{
        [](auto& value) { value.committed_entry.reset(); },
        [](auto& value) { value.committed_entry->key = "False.b3registration"; },
        [](auto& value) { value.committed_entry->name = "False"; },
        [](auto& value) { value.committed_entry->scope = RegistrationScope::Performance; },
        [](auto& value) { value.committed_entry->controls->pedal_drawbars[1] = 8; },
        [](auto& value) { value.committed_entry->controls.reset(); },
        [](auto& value) { value.committed_entry->status = LibraryEntryStatus::Unavailable; }
    }};
    for (const auto& mutate : mutations) {
        LibraryModel model;
        const auto before = snapshot();
        initialize(model, before);
        const auto actual = prove_controls(model, before);
        const auto effect = stage_save(model, actual);
        REQUIRE(model.authorize_save(effect.operation_id, observed(actual), 12).permitted);
        auto result = committed(effect);
        mutate(result);
        REQUIRE(model.complete_save(effect.operation_id, result) == LibraryOutcome::SavedWithWarning);
        terminal(model, LibraryOutcome::SavedWithWarning);
        REQUIRE(!operation(model).reason.empty());
        REQUIRE(!model.view().current_reference);
        REQUIRE(!model.take_save_intent(observed(actual), 13));
        REQUIRE(model.complete_save(effect.operation_id, result) == LibraryOutcome::StaleResult);
        terminal(model, LibraryOutcome::SavedWithWarning);
    }

    LibraryModel model;
    const auto before = snapshot();
    initialize(model, before, {entry("Retained")});
    const auto actual = prove_controls(model, before);
    const auto old_generation = model.view().catalog.generation;
    const auto effect = stage_save(model, actual);
    REQUIRE(model.authorize_save(effect.operation_id, observed(actual), 12).permitted);
    auto result = committed(effect, LibrarySaveStatus::SavedWithWarning);
    result.reason = "Committed; refresh unavailable";
    result.refreshed_catalog->status = LibraryCatalogStatus::DirectoryUnavailable;
    result.refreshed_catalog->reason = "Scan failed";
    result.refreshed_catalog->entries.clear();
    REQUIRE(model.complete_save(effect.operation_id, result) == LibraryOutcome::SavedWithWarning);
    REQUIRE(model.view().catalog_stale);
    REQUIRE(model.view().catalog.generation == old_generation);
    REQUIRE(model.view().catalog.entries[0].name == "Retained");
    REQUIRE(reference(model).key == effect.key && !reference(model).missing);
    REQUIRE(!model.take_save_intent(observed(actual), 13));
}

void failed_storage_and_foreign_completions() {
    for (const auto status : {LibrarySaveStatus::StagingFailed, LibrarySaveStatus::WriteFailed,
             LibrarySaveStatus::FlushFailed, LibrarySaveStatus::CloseFailed,
             LibrarySaveStatus::NameExists, LibrarySaveStatus::CommitFailed}) {
        for (const bool authorize : {false, true}) {
            LibraryModel model;
            const auto before = snapshot();
            initialize(model, before);
            const auto actual = prove_controls(model, before);
            const auto effect = stage_save(model, actual);
            if (authorize) REQUIRE(model.authorize_save(effect.operation_id, observed(actual), 12).permitted);
            LibrarySaveResult result;
            result.status = status;
            result.reason = "Independent storage failure";
            REQUIRE(model.complete_save(effect.operation_id + 1, result) == LibraryOutcome::StaleResult);
            REQUIRE(operation(model).phase == LibraryOperationPhase::Saving);
            REQUIRE(model.complete_save(effect.operation_id, result) == LibraryOutcome::SaveFailed);
            terminal(model, LibraryOutcome::SaveFailed);
            REQUIRE(!model.view().current_reference);
            REQUIRE(model.view().name_draft == "Saved");
            REQUIRE(model.complete_save(effect.operation_id, result) == LibraryOutcome::StaleResult);
            terminal(model, LibraryOutcome::SaveFailed);
        }
    }
}

void compound_generation_zero_and_newer_refresh_order() {
    for (const bool newer_refresh : {false, true}) {
        LibraryModel model;
        const auto before = snapshot();
        initialize(model, before, {entry("Retained")});
        const auto actual = prove_controls(model, before);
        const auto old_generation = model.view().catalog.generation;
        const auto effect = stage_save(model, actual);
        std::optional<LibraryRefreshIntent> refresh;
        if (newer_refresh) {
            refresh = model.request_refresh();
            REQUIRE(refresh && refresh->generation > old_generation + 1);
            auto latest = catalog({entry("Latest")});
            latest.generation = refresh->generation;
            REQUIRE(model.replace_catalog(latest));
        }
        REQUIRE(model.authorize_save(effect.operation_id, observed(actual), 12).permitted);
        const auto result = committed(effect);
        REQUIRE(result.refreshed_catalog->generation == 0);
        REQUIRE(model.complete_save(effect.operation_id, result) == LibraryOutcome::Saved);
        REQUIRE(reference(model).key == effect.key && !reference(model).missing);
        if (newer_refresh) {
            REQUIRE(model.view().catalog.generation == refresh->generation);
            REQUIRE(model.view().catalog.entries[0].name == "Latest");
        } else {
            REQUIRE(model.view().catalog.generation == old_generation + 1);
            REQUIRE(model.view().catalog.entries[0].name == "Saved");
            REQUIRE(model.view().selected_key == std::optional<std::string>{effect.key});
        }
        (void)publish(model, catalog());
        REQUIRE(reference(model).missing);
    }
}

void save_name_collision_capacity_and_prepare_admission() {
    const auto before = snapshot();
    for (const auto draft : {"", "CON", "aux", "COM9", "Lpt1", " Leading", "Trailing "}) {
        LibraryModel model;
        initialize(model, before);
        const auto actual = prove_controls(model, before);
        REQUIRE(model.set_name(draft));
        const auto denied = model.request_save_new(observed(actual), 10);
        REQUIRE(denied.outcome == LibraryOutcome::InvalidInput);
        REQUIRE(!model.view().operation && !model.take_save_intent(observed(actual), 11));
        REQUIRE(model.view().name_draft == draft);
    }
    for (unsigned variant = 0; variant < 3; ++variant) {
        LibraryModel model;
        auto existing = catalog({entry("Alpha")});
        if (variant == 1) {
            existing.invalid_name_count = 127;
            existing.candidate_count = 128;
            existing.directory_items = 128;
        }
        if (variant == 2) existing.directory_items = 512;
        (void)publish(model, existing);
        model.observe(observed(before), 0);
        const auto actual = prove_controls(model, before);
        REQUIRE(model.set_name(variant == 0 ? "aLPHA" : "Another"));
        const auto denied = model.request_save_new(observed(actual), 10);
        REQUIRE(denied.outcome != LibraryOutcome::Accepted && !denied.reason.empty());
        REQUIRE(!model.view().operation && !model.take_save_intent(observed(actual), 11));
    }
    LibraryModel separate_scope;
    initialize(separate_scope, before, {entry("Alpha")});
    const auto actual = prove_controls(separate_scope, before);
    REQUIRE(separate_scope.set_save_scope(RegistrationScope::Performance));
    const auto effect = stage_save(separate_scope, actual, "Alpha");
    REQUIRE(effect.key == "Alpha.b3performance");

    LibraryModel prepared;
    initialize(prepared, before);
    const auto proved = prove_controls(prepared, before);
    prepared.audio_lifecycle_changed(LibraryAudioTransition::Prepare);
    REQUIRE(prepared.set_name("No pre-prepare proof"));
    REQUIRE(prepared.request_save_new(observed(proved), 10).outcome ==
        LibraryOutcome::NoAcknowledgedControls);
}

void operation_id_zero_last_and_exhausted() {
    for (const std::uint64_t limit : {std::uint64_t{0}, std::uint64_t{1}}) {
        LibraryModelLimits limits;
        limits.operation_ids = limit;
        LibraryModel model(limits);
        const auto target = entry("Alpha", RegistrationScope::Performance);
        const auto before = snapshot();
        initialize(model, before, {target});
        if (limit == 1) {
            const auto named = recall(model, target, before);
            REQUIRE(named.operation_id == 1 && !model.view().mutations_exhausted);
            REQUIRE(model.submitted({SessionStatus::Ok, 1}, named.control_intent) == LibraryOutcome::Accepted);
            const auto actual = acknowledged(before, stored_controls(), 1);
            model.observe(observed(actual), 11);
            terminal(model, LibraryOutcome::Applied);
            REQUIRE(!model.view().mutations_exhausted);
            REQUIRE(model.request_recall(target, actual.controls, observed(actual), 12).outcome ==
                LibraryOutcome::Exhausted);
            terminal(model, LibraryOutcome::Applied);
        } else {
            REQUIRE(model.request_recall(target, before.controls, observed(before), 10).outcome ==
                LibraryOutcome::Exhausted);
            REQUIRE(!model.view().operation && !model.view().controls_pending);
        }
        REQUIRE(model.view().mutations_exhausted);
    }
}

void desired_revision_zero_last_and_exhausted() {
    for (const std::uint64_t limit : {std::uint64_t{0}, std::uint64_t{1}}) {
        LibraryModelLimits limits;
        limits.desired_revisions = limit;
        LibraryModel model(limits);
        const auto before = snapshot();
        initialize(model, before);
        auto invalid = stored_controls();
        invalid.pedal_drawbars[1] = 9;
        REQUIRE(!model.note_control_intent(invalid, observed(before)));
        REQUIRE(!model.view().mutations_exhausted);
        if (limit == 1) {
            const auto token = model.note_control_intent(stored_controls(), observed(before));
            REQUIRE(token && token->desired_revision == 1);
            REQUIRE(!model.view().mutations_exhausted);
            REQUIRE(model.submitted({SessionStatus::Ok, 1}, token) == LibraryOutcome::Accepted);
            const auto actual = acknowledged(before, stored_controls(), 1);
            model.observe(observed(actual), 1);
            const auto effect = stage_save(model, actual);
            REQUIRE(model.authorize_save(effect.operation_id, observed(actual), 12).permitted);
            REQUIRE(model.complete_save(effect.operation_id, committed(effect)) == LibraryOutcome::Saved);
            REQUIRE(!model.view().mutations_exhausted);
            REQUIRE(!model.note_control_intent(stored_controls(), observed(actual)));
        } else REQUIRE(!model.note_control_intent(stored_controls(), observed(before)));
        REQUIRE(model.view().mutations_exhausted);
        REQUIRE(model.view().action_outcome == LibraryOutcome::Exhausted);
    }
}

void failure_revision_zero_last_and_exhausted() {
    for (const std::uint64_t limit : {std::uint64_t{0}, std::uint64_t{1}}) {
        LibraryModelLimits limits;
        limits.submission_failure_revisions = limit;
        LibraryModel model(limits);
        const auto before = snapshot();
        initialize(model, before);
        if (limit == 1) {
            REQUIRE(model.submitted({SessionStatus::InvalidCommand, 0}) == LibraryOutcome::Rejected);
            REQUIRE(!model.view().mutations_exhausted);
            const auto actual = prove_controls(model, before);
            REQUIRE(model.set_name("Last failure revision"));
            REQUIRE(model.request_save_new(observed(actual), 10).outcome == LibraryOutcome::Accepted);
            REQUIRE(operation(model).phase == LibraryOperationPhase::ReadyToSave);
        }
        REQUIRE(model.submitted({SessionStatus::QueueFull, 0}) == LibraryOutcome::Exhausted);
        REQUIRE(model.view().mutations_exhausted);
        REQUIRE(!model.note_control_intent(stored_controls(), observed(before)));
        REQUIRE(!model.take_save_intent(observed(before), 11));
    }
}

void catalog_generation_zero_last_and_save_reservation() {
    LibraryModelLimits zero_limits;
    zero_limits.catalog_generations = 0;
    LibraryModel zero(zero_limits);
    REQUIRE(!zero.request_refresh());
    REQUIRE(zero.view().mutations_exhausted);
    REQUIRE(zero.view().catalog.generation == 0);

    LibraryModelLimits one_limits;
    one_limits.catalog_generations = 1;
    LibraryModel one(one_limits);
    const auto before = snapshot();
    initialize(one, before);
    REQUIRE(one.view().catalog.generation == 1 && !one.view().mutations_exhausted);
    const auto actual = prove_controls(one, before);
    REQUIRE(one.set_name("Cannot reserve refresh"));
    REQUIRE(one.request_save_new(observed(actual), 10).outcome == LibraryOutcome::Accepted);
    REQUIRE(!one.take_save_intent(observed(actual), 11));
    REQUIRE(one.view().mutations_exhausted);
    terminal(one, LibraryOutcome::Exhausted);
    REQUIRE(!one.authorize_save(operation(one).operation_id, observed(actual), 12).permitted);
    REQUIRE(one.view().catalog.generation == 1);

    LibraryModelLimits two_limits;
    two_limits.catalog_generations = 2;
    LibraryModel two(two_limits);
    initialize(two, before);
    const auto proved = prove_controls(two, before);
    const auto effect = stage_save(two, proved);
    REQUIRE(!two.view().mutations_exhausted);
    REQUIRE(two.authorize_save(effect.operation_id, observed(proved), 12).permitted);
    REQUIRE(two.complete_save(effect.operation_id, committed(effect)) == LibraryOutcome::Saved);
    REQUIRE(two.view().catalog.generation == 2 && !two.view().mutations_exhausted);
    REQUIRE(!two.request_refresh());
    REQUIRE(two.view().mutations_exhausted);
    REQUIRE(two.view().catalog.generation == 2);
    terminal(two, LibraryOutcome::Saved);
    REQUIRE(reference(two).key == effect.key);
}

} // namespace

int main() {
    using Test = std::pair<std::string_view, void (*)()>;
    const std::array tests{
        Test{"initial state, drafts and owned copies", initial_state_drafts_and_copied_views},
        Test{"catalog generations and stable selection", catalog_generations_selection_and_failures},
        Test{"catalog statuses, exact bounds and count arithmetic", complete_catalog_statuses_and_bounds},
        Test{"catalog row admission and case ambiguity", catalog_row_admission_and_case_ambiguity},
        Test{"explicit revalidation and atomic refusal", revalidation_is_explicit_and_atomic},
        Test{"literal scope and explicit latest expression", literal_scope_restore_and_latest_desired_expression},
        Test{"selected, current and operation identities", selected_current_and_operation_identities},
        Test{"equal queued controls require newer original proof", queued_equal_controls_need_original_newer_proof},
        Test{"same-value newer intent supersedes", same_value_intent_supersedes_without_revival},
        Test{"startup, unsubmitted and unrelated sequence have no proof", no_startup_unsubmitted_or_unrelated_control_proof},
        Test{"failed pre-post read cannot be repaired", missing_prepost_read_cannot_be_repaired},
        Test{"failed, old and malformed observations", failed_old_and_malformed_observations_supply_no_proof},
        Test{"same-publication equality covers every field", repeated_publication_requires_every_field_equal},
        Test{"failure guards defeat sequence substitution", failure_guards_prevent_larger_sequence_substitution},
        Test{"unrelated synchronous failures invalidate waits", unrelated_synchronous_failures_invalidate_waits},
        Test{"malformed and duplicate submission tokens", malformed_submission_tokens_fail_closed},
        Test{"actual Modified, Pending and Missing are independent", actual_modified_pending_and_missing_are_distinct},
        Test{"audio gates and explicit lifecycle boundaries", audio_gates_and_explicit_lifecycle_boundaries},
        Test{"monotonic clock, exact timeout and overflow", monotonic_time_deadline_and_overflow},
        Test{"stopped proved Save consumes one effect and permission", stopped_proved_save_has_one_effect_and_permission},
        Test{"waiting Save retains original receipt", save_wait_retains_original_receipt_and_failure_guards},
        Test{"taking Save requires fresh unchanged observation", take_requires_a_fresh_unchanged_observation},
        Test{"preauthorization changes refuse publication", preauthorization_intent_failure_read_and_deadline_changes},
        Test{"authorized Save preserves later committed truth", authorized_commit_retains_truth_after_later_changes},
        Test{"commit warnings and inconsistent metadata", committed_warning_and_inconsistent_metadata_truth},
        Test{"failed storage and foreign completions", failed_storage_and_foreign_completions},
        Test{"compound scan generation zero and newer refresh", compound_generation_zero_and_newer_refresh_order},
        Test{"Save names, collisions, capacity and Prepare", save_name_collision_capacity_and_prepare_admission},
        Test{"operation ID zero, last and exhausted", operation_id_zero_last_and_exhausted},
        Test{"desired revision zero, last and exhausted", desired_revision_zero_last_and_exhausted},
        Test{"failure revision zero, last and exhausted", failure_revision_zero_last_and_exhausted},
        Test{"catalog generation zero, last and reserved", catalog_generation_zero_last_and_save_reservation}
    };
    std::size_t failures = 0;
    for (const auto& [name, test] : tests) {
        current_case = name;
        try { test(); }
        catch (const std::exception& error) {
            ++failures;
            std::cerr << error.what() << '\n';
        }
    }
    std::cout << "Independent LibraryModel contract: " << tests.size() << " groups, "
              << checks << " assertions, " << failures << " failed groups\n";
    return failures == 0 ? 0 : 1;
}
