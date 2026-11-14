#include "InspectionModel.h"
#include "TestSupport.h"

#include "hammond/Engine.h"
#include "hammond/ScannerLine.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <limits>
#include <span>
#include <string_view>
#include <type_traits>
#include <variant>

// Independent acceptance uses actual loaded-profile Session publications and
// command acknowledgments. Forged copies below test defensive formatting only;
// they are never claimed to be observable Engine state or physical evidence.
namespace {
using namespace hammond;
using namespace hammond::standalone;
using Availability = InspectionAvailability;
using Evidence = InspectionEvidence;
using State = InspectionSnapshotState;
constexpr InspectionRuntimeInfo copied_now{true, true};
constexpr std::string_view bank_memory =
    "UA 012345678 / UB 876543210 / LA 135702468 / LB 864207531";
constexpr std::string_view declared_digest =
    "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef";

template <class Value>
auto bytes_of(const Value& value) {
    static_assert(std::is_trivially_copyable_v<Value>);
    std::array<std::byte, sizeof(Value)> bytes{};
    std::memcpy(bytes.data(), &value, sizeof(Value));
    return bytes;
}

void bounded(const InspectionText& text) {
    CHECK(text.size < kInspectionTextCapacity);
    CHECK(text.view().data() == text.bytes.data());
    CHECK(text.view().size() == text.size);
    CHECK(text.bytes[text.size] == '\0');
    CHECK(!text.truncated); // Every currently accepted field fits, including SHA-256.
    for (const char byte : text.view()) CHECK(byte >= ' ' && byte <= '~');
}

const InspectionRow& lookup(const InspectionDocument& document, std::string_view id) {
    const InspectionRow* found = nullptr;
    for (const auto& card : document.sections) {
        CHECK(card.row_count <= card.rows.size());
        for (std::size_t index = 0; index < card.row_count; ++index) {
            if (card.rows[index].id == id) {
                CHECK(found == nullptr);
                found = &card.rows[index];
            }
        }
    }
    CHECK(document.rotary_row_count <= document.rotary_rows.size());
    for (std::size_t index = 0; index < document.rotary_row_count; ++index) {
        if (document.rotary_rows[index].id == id) {
            CHECK(found == nullptr);
            found = &document.rotary_rows[index];
        }
    }
    if (found == nullptr) hammond_test::fail("required row exists once", __FILE__, __LINE__, id);
    return *found;
}

std::string_view value(const InspectionDocument& document, std::string_view id) {
    return lookup(document, id).value.view();
}

void same_document(const InspectionDocument& left, const InspectionDocument& right) {
    CHECK(left.snapshot_state == right.snapshot_state);
    CHECK(left.controls_pending == right.controls_pending);
    CHECK(left.frame_clock == right.frame_clock);
    CHECK(left.publication_revision == right.publication_revision);
    CHECK(left.profile_id.view() == right.profile_id.view());
    CHECK(left.profile_authoring_sha256.view() == right.profile_authoring_sha256.view());
    const auto same_row = [](const InspectionRow& a, const InspectionRow& b) {
        CHECK(a.id == b.id && a.label == b.label && a.value.view() == b.value.view());
        CHECK(a.value.truncated == b.value.truncated);
        CHECK(a.unit == b.unit && a.source == b.source);
        CHECK(a.availability == b.availability && a.evidence == b.evidence);
    };
    for (std::size_t index = 0; index < left.sections.size(); ++index) {
        const auto& a = left.sections[index];
        const auto& b = right.sections[index];
        CHECK(a.section == b.section && a.title == b.title && a.summary == b.summary);
        CHECK(a.row_count == b.row_count);
        for (std::size_t row = 0; row < a.rows.size(); ++row) same_row(a.rows[row], b.rows[row]);
    }
    CHECK(left.rotary_row_count == right.rotary_row_count);
    for (std::size_t index = 0; index < left.rotary_rows.size(); ++index) {
        same_row(left.rotary_rows[index], right.rotary_rows[index]);
    }
}

InspectionDocument inspect(const RuntimeProfile& profile, const UiViewState& view,
                           InspectionRuntimeInfo runtime = copied_now) {
    const auto profile_before = bytes_of(profile);
    const auto view_before = bytes_of(view);
    const auto runtime_before = bytes_of(runtime);
    const auto first = make_inspection_document(profile, view, runtime);
    const auto second = make_inspection_document(profile, view, runtime);
    same_document(first, second);
    CHECK(bytes_of(profile) == profile_before);
    CHECK(bytes_of(view) == view_before);
    CHECK(bytes_of(runtime) == runtime_before);
    bounded(first.profile_id);
    bounded(first.profile_authoring_sha256);
    for (const auto& card : first.sections) {
        CHECK(card.row_count <= card.rows.size());
        for (std::size_t index = 0; index < card.rows.size(); ++index) {
            bounded(card.rows[index].value);
            if (index >= card.row_count) {
                CHECK(card.rows[index].id.empty());
                CHECK(card.rows[index].value.size == 0);
            }
        }
    }
    for (const auto& row : first.rotary_rows) bounded(row.value);
    return first;
}

RuntimeProfile distinct_profile() {
    auto profile = load_test_profile();
    profile.sources[45].frequency_hz = 431.7654321;
    profile.output_gain = 0.0623456789;
    profile.authoring_sha256.fill('\0');
    std::copy(declared_digest.begin(), declared_digest.end(), profile.authoring_sha256.begin());
    CHECK(validate_runtime_profile(profile, 48000.0) == Status::Ok);
    return profile;
}

ControlSnapshot distinct_controls() {
    ControlSnapshot controls{};
    controls.drawbars[0][0] = {0, 1, 2, 3, 4, 5, 6, 7, 8};
    controls.drawbars[0][1] = {8, 7, 6, 5, 4, 3, 2, 1, 0};
    controls.drawbars[1][0] = {1, 3, 5, 7, 0, 2, 4, 6, 8};
    controls.drawbars[1][1] = {8, 6, 4, 2, 0, 7, 5, 3, 1};
    controls.selected_banks = {DrawbarBank::A, DrawbarBank::B};
    controls.fixed_registrations = {FixedRegistration::GSharp, FixedRegistration::CSharp};
    controls.expression = 0.3125;
    controls.pedal_drawbars = {2, 6};
    controls.percussion = {true, PercussionHarmonic::Third, PercussionVolume::Soft, PercussionDecay::Fast};
    CHECK(is_valid_control_snapshot(controls));
    return controls;
}

SessionSnapshot read(const Session& session) {
    SessionSnapshot snapshot{};
    CHECK(session.read_snapshot(snapshot));
    return snapshot;
}

void submit(Session& session, UiModel& ui, const SessionCommand& command) {
    const auto result = session.post(command);
    CHECK(result.ok());
    CHECK(ui.submitted(command, result).count == 0);
}

void submit(Session& session, UiModel& ui, const UiActions& actions) {
    CHECK(actions.count == 1);
    const auto* command = std::get_if<SessionCommand>(&actions.items[0]);
    CHECK(command != nullptr);
    submit(session, ui, *command);
}

SessionCommand manual_note(HostNoteKind kind, std::uint8_t bus, std::uint8_t pitch,
                           std::int32_t owner) {
    return PerformanceInputEvent{HostNoteEvent{0, kind, bus, 0, pitch,
        static_cast<std::uint8_t>(kind == HostNoteKind::On ? 127 : 0), owner}};
}

SessionCommand selection_command(Manual manual, PresetSelection selection) {
    return PerformanceInputEvent{Event{0, EventType::SelectPreset, manual, 0,
                                       static_cast<double>(selection)}};
}

void publish(Session& session, UiModel& ui, std::uint32_t frames = 0) {
    std::array<float, 128> stereo{};
    CHECK(frames <= stereo.size() / 2);
    CHECK(session.render(frames, std::span<float>{stereo.data(), static_cast<std::size_t>(frames) * 2}));
    ui.observe(read(session));
}

void missing_applied_values(const InspectionDocument& document) {
    for (const auto id : {"contacts.upper_held", "contacts.lower_held", "contacts.pedals_held",
                          "controls.banks", "controls.pedals", "controls.expression", "controls.percussion"}) {
        CHECK(value(document, id) == "Not observed");
        CHECK(lookup(document, id).availability == Availability::NotObserved);
    }
    CHECK(value(document, "controls.upper").starts_with("Sound Not observed / Edit "));
    CHECK(value(document, "controls.lower").starts_with("Sound Not observed / Edit "));
}

void inventory_from_real_publication(const RuntimeProfile& profile, const UiViewState& view) {
    // Oracle is derived from the reviewed contract and real fixture, not another
    // call to the production row builder or the author test's default snapshot.
    struct Expected {
        std::string_view id, text, unit, source;
        Availability availability;
        Evidence evidence;
    };
    constexpr auto available = Availability::Available;
    constexpr auto software = Evidence::Software;
    const std::array expected{
        Expected{"generator.model", "ideal-shared-sine-v1", "", "TonewheelBank.h", available, software},
        Expected{"generator.sources", "91", "sources", "Profile.h", available, software},
        Expected{"generator.tone46_hz", "431.765", "Hz", "61-72", available, Evidence::Proposed},
        Expected{"generator.output_gain", "0.0623457", "normalized amplitude", "Profile.h", available, Evidence::Proposed},
        Expected{"contacts.model", kIdealContactModelId, "", "Session.h/.cpp", available, software},
        Expected{"contacts.upper_held", "2", "targets", "ContactBank.h", available, software},
        Expected{"contacts.lower_held", "3", "targets", "ContactBank.h", available, software},
        Expected{"contacts.pedals_held", "2", "targets", "Session.h/.cpp", available, software},
        Expected{"contacts.inventory", "61 + 61 manual keys / 25 pedals", "", "37-42, 115-120", available, software},
        Expected{"contacts.pedal_model", kNominalPedalVoiceModelId, "", "PedalVoice.h", available, Evidence::Proposed},
        Expected{"scanner.audio", "Not connected", "", "Engine.cpp", Availability::NotIntegrated, software},
        Expected{"scanner.research_model", kScannerLineModelId, "", "ScannerLine.h", available, Evidence::Proposed},
        Expected{"scanner.physical_capture", "Not acquired", "", "SCANNER_HANDOFF.md", Availability::NotAcquired, Evidence::Unknown},
        Expected{"ao28.circuit", "Not connected", "", "ConsoleModel.h", Availability::NotIntegrated, software},
        Expected{"ao28.percussion_model", kPercussionModelId, "", "Percussion.h", available, Evidence::Proposed},
        Expected{"ao28.specimen", "Not acquired", "", "PLAN.md", Availability::NotAcquired, Evidence::Unknown},
        Expected{"ao28.voltage", "Unavailable", "V", "193-252", Availability::NotAcquired, Evidence::Unknown},
        Expected{"leslie.audio", "Not connected", "", "ROTARY_SCOPE.md", Availability::NotIntegrated, software},
        Expected{"leslie.target", "122 baseline; 147 separate", "", "PLAN.md", available, Evidence::Documented},
        Expected{"leslie.horn_speed", "Unavailable", "rpm", "ROTARY_SCOPE.md", Availability::NotIntegrated, Evidence::Unknown},
        Expected{"leslie.drum_speed", "Unavailable", "rpm", "ROTARY_SCOPE.md", Availability::NotIntegrated, Evidence::Unknown},
        Expected{"leslie.microphone", "Not acquired", "m", "253-348", Availability::NotAcquired, Evidence::Unknown},
        Expected{"controls.upper", "Sound Fixed G# / Edit A", "", "ControlState.h", available, software},
        Expected{"controls.lower", "Sound Fixed C# / Edit B", "", "FixedRegistration.h", available, software},
        Expected{"controls.banks", bank_memory, "", "UiModel.h", available, software},
        Expected{"controls.pedals", "Mixture 1 2 / Mixture 2 6", "positions 0-8", "109-156", available, software},
        Expected{"controls.expression", "0.3125", "normalized 0-1", "ControlState.h", available, software},
        Expected{"controls.percussion", "On / Third / Soft / Fast / Upper B ineligible", "", "397-402", available, software},
        Expected{"rotary.path", "Nominal dry organ; cabinet audio not connected", "", "Session.cpp", Availability::NotIntegrated, software},
        Expected{"rotary.target", "Leslie 122 baseline; 147 separate", "", "55-60, 253-264", available, Evidence::Documented},
        Expected{"rotary.artwork", "Atlas concept, decorative", "", "atlas-reference.json", available, Evidence::Documented},
        Expected{"rotary.speeds", "Horn unavailable / Drum unavailable", "rpm", "ROTARY_SCOPE.md", Availability::NotIntegrated, Evidence::Unknown},
        Expected{"rotary.microphone", "Not acquired", "m", "ROTARY_SCOPE.md", Availability::NotAcquired, Evidence::Unknown},
        Expected{"rotary.brake", "Not modeled", "", "256, 289, 413", Availability::NotIntegrated, software},
    };
    static_assert(expected.size() == 34);
    static_assert(kToneSourceCount == 91 && kManualKeyCount == 61 && kPedalCount == 25);
    const auto document = inspect(profile, view);
    CHECK(document.profile_id.view() == kNominalProfileId);
    CHECK(document.profile_authoring_sha256.view() == declared_digest);
    CHECK(document.profile_authoring_sha256.size == 64);
    std::size_t row_count = document.rotary_row_count;
    constexpr std::array<std::size_t, 6> card_sizes{4, 6, 3, 4, 5, 6};
    for (std::size_t index = 0; index < card_sizes.size(); ++index) {
        const auto& card = document.sections[index];
        CHECK(static_cast<std::size_t>(card.section) == index);
        CHECK(!card.title.empty() && !card.summary.empty());
        CHECK(card.row_count == card_sizes[index]);
        row_count += card.row_count;
    }
    CHECK(row_count == expected.size() && document.rotary_row_count == 6);
    for (const auto& item : expected) {
        const auto& row = lookup(document, item.id);
        CHECK(row.value.view() == item.text);
        CHECK(row.unit == item.unit && row.source.find(item.source) != std::string_view::npos);
        CHECK(row.availability == item.availability && row.evidence == item.evidence);
        CHECK(!row.label.empty());
    }
    CHECK(lookup(document, "scanner.research_model").label == "Research module only");
    CHECK(document.sections[2].summary.find("absent from this dry audio path") != std::string_view::npos);
    CHECK(document.sections[3].summary.find("nominal surrogate") != std::string_view::npos);
    CHECK(document.sections[4].summary.find("not an installed specimen") != std::string_view::npos);
    CHECK(document.sections[5].summary.find("Readiness is not observed") != std::string_view::npos);
}

void real_commands_and_conflicting_desired(const RuntimeProfile& profile, Session& session, UiModel& ui) {
    CHECK(ui.activate({UiControlKind::EditBank, Manual::Upper, DrawbarBank::A, 0}).count == 0);
    submit(session, ui, ui.load_controls(distinct_controls()));
    const auto queued = inspect(profile, ui.view());
    CHECK(queued.controls_pending);
    CHECK(value(queued, "controls.expression") == "1");
    CHECK(value(queued, "controls.upper") == "Sound Bank B / Edit A");
    submit(session, ui, manual_note(HostNoteKind::On, 0, 36, 101));
    submit(session, ui, manual_note(HostNoteKind::On, 0, 36, 102)); // Same target, second owner.
    submit(session, ui, manual_note(HostNoteKind::On, 0, 96, 103));
    for (const auto pitch : {36, 60, 96}) {
        submit(session, ui, manual_note(HostNoteKind::On, 1, static_cast<std::uint8_t>(pitch), pitch));
    }
    for (const auto pedal : {1, 25}) {
        submit(session, ui, SessionCommand{PerformanceInputEvent{PedalNoteEvent{
            0, PedalNoteKind::On, 0, 0, PedalId{static_cast<std::uint8_t>(pedal)}, 127, pedal}}});
    }
    publish(session, ui, 32);
    CHECK(!ui.view().controls_pending);
    inventory_from_real_publication(profile, ui.view());

    constexpr std::array selections{PresetSelection::BankA, PresetSelection::BankB,
                                    PresetSelection::FSharp, PresetSelection::Cancel};
    constexpr std::array<std::string_view, 4> upper_text{
        "Sound Bank A / Edit B", "Sound Bank B / Edit B",
        "Sound Fixed F# / Edit B", "Sound Cancel / Edit B"};
    constexpr std::array<std::string_view, 4> lower_text{
        "Sound Bank A / Edit A", "Sound Bank B / Edit A",
        "Sound Fixed F# / Edit A", "Sound Cancel / Edit A"};
    for (const auto manual : {Manual::Upper, Manual::Lower}) {
        for (std::size_t index = 0; index < selections.size(); ++index) {
            submit(session, ui, selection_command(manual, selections[index]));
            publish(session, ui);
            auto hostile_desired = ui.view();
            hostile_desired.controls = {}; // Desired values must not supply applied data.
            hostile_desired.controls.expression = std::numeric_limits<double>::quiet_NaN();
            hostile_desired.controls.selected_banks.fill(static_cast<DrawbarBank>(255));
            hostile_desired.controls.fixed_registrations.fill(static_cast<FixedRegistration>(255));
            hostile_desired.controls.drawbars[0][0].fill(255);
            hostile_desired.controls.pedal_drawbars = {255, 255};
            hostile_desired.controls.percussion.harmonic = static_cast<PercussionHarmonic>(255);
            hostile_desired.edited_banks = {DrawbarBank::B, DrawbarBank::A};
            hostile_desired.controls_pending = true;
            const auto document = inspect(profile, hostile_desired);
            CHECK(document.controls_pending && document.snapshot_state == State::Current);
            CHECK(value(document, manual == Manual::Upper ? "controls.upper" : "controls.lower") ==
                  (manual == Manual::Upper ? upper_text[index] : lower_text[index]));
            CHECK(value(document, "controls.banks") == bank_memory);
            CHECK(value(document, "controls.expression") == "0.3125");
            CHECK(value(document, "controls.pedals") == "Mixture 1 2 / Mixture 2 6");
            CHECK(value(document, "contacts.upper_held") == "2");
            CHECK(value(document, "contacts.lower_held") == "3");
            CHECK(value(document, "contacts.pedals_held") == "2");
            const bool eligible = manual == Manual::Upper && selections[index] == PresetSelection::BankB;
            CHECK(value(document, "controls.percussion") == (eligible ?
                "On / Third / Soft / Fast / Upper B eligible" :
                "On / Third / Soft / Fast / Upper B ineligible"));
            if (selections[index] == PresetSelection::Cancel) {
                const auto manual_index = static_cast<std::size_t>(manual);
                CHECK(ui.view().applied.controls.fixed_registrations[manual_index] == FixedRegistration::FSharp);
                CHECK(ui.view().applied.controls.selected_banks[manual_index] == DrawbarBank::B);
            }
        }
    }
    submit(session, ui, selection_command(Manual::Upper, PresetSelection::BankB));
    submit(session, ui, SessionCommand{PerformanceInputEvent{Event{0, EventType::Percussion, Manual::Upper, 0, 0.0}}});
    publish(session, ui);
    CHECK(value(inspect(profile, ui.view()), "controls.percussion") ==
          "Off / Third / Soft / Fast / Upper B eligible");
    submit(session, ui, selection_command(Manual::Upper, PresetSelection::Cancel));
    publish(session, ui);
    // Isolate the route boundary: adjustable B and no fixed mode are retained.
    CHECK(ui.view().applied.controls.selected_banks[0] == DrawbarBank::B);
    CHECK(ui.view().applied.controls.fixed_registrations[0] == FixedRegistration::None);
    CHECK(!ui.view().applied.controls.route_enabled[0]);
    CHECK(value(inspect(profile, ui.view()), "controls.percussion") ==
          "Off / Third / Soft / Fast / Upper B ineligible");
    submit(session, ui, manual_note(HostNoteKind::Off, 0, 36, 101));
    publish(session, ui);
    CHECK(value(inspect(profile, ui.view()), "contacts.upper_held") == "2");
    submit(session, ui, manual_note(HostNoteKind::Off, 0, 36, 102));
    publish(session, ui);
    CHECK(value(inspect(profile, ui.view()), "contacts.upper_held") == "1");
}

void lifecycle_and_failed_reads(const RuntimeProfile& profile) {
    Session session;
    UiModel ui;
    ui.observe(read(session));
    const auto unprepared = inspect(profile, ui.view());
    CHECK(unprepared.snapshot_state == State::Unprepared);
    missing_applied_values(unprepared);
    CHECK(inspect(profile, ui.view(), {true, false}).snapshot_state == State::Unprepared);
    CHECK(session.prepare(profile, {48000.0, 64, 819, 0}) == SessionStatus::Ok);
    ui.observe(read(session));
    CHECK(inspect(profile, ui.view()).snapshot_state == State::Stopped);
    CHECK(session.start() == SessionStatus::Ok);
    ui.observe(read(session));
    CHECK(ui.view().applied.frame_clock == 0);
    CHECK(inspect(profile, ui.view()).snapshot_state == State::Current);
    real_commands_and_conflicting_desired(profile, session, ui);

    const auto retained_view = ui.view();
    const auto retained = inspect(profile, retained_view, {true, false});
    CHECK(session.stop() == SessionStatus::Ok);
    // An actual Session changed after this copy. Formatting cannot discover it.
    same_document(retained, inspect(profile, retained_view, {true, false}));
    CHECK(retained.snapshot_state == State::Retained);
    CHECK(value(retained, "contacts.upper_held") == "1");
    ui.observe(read(session));
    const auto stopped = inspect(profile, ui.view());
    CHECK(stopped.snapshot_state == State::Stopped);
    CHECK(value(stopped, "contacts.upper_held") == "0");
    CHECK(stopped.frame_clock == retained.frame_clock);
    CHECK(stopped.publication_revision > retained.publication_revision);
    const auto unavailable = inspect(profile, retained_view, {false, true});
    CHECK(unavailable.snapshot_state == State::Unavailable);
    missing_applied_values(unavailable);

    // Finite publication allowance causes a real bounded read failure without
    // racing threads or inventing a failed-read flag around a successful read.
    Session limited({std::numeric_limits<std::uint64_t>::max(), 3});
    UiModel limited_ui;
    CHECK(limited.prepare(profile, {48000.0, 64, 819, 0}) == SessionStatus::Ok);
    CHECK(limited.start() == SessionStatus::Ok);
    limited_ui.observe(read(limited));
    submit(limited, limited_ui, limited_ui.load_controls(distinct_controls()));
    submit(limited, limited_ui, manual_note(HostNoteKind::On, 0, 60, 701));
    publish(limited, limited_ui, 7);
    auto last = limited_ui.view().applied;
    const auto before = bytes_of(last);
    auto next_controls = distinct_controls();
    next_controls.expression = 0.875;
    submit(limited, limited_ui, limited_ui.load_controls(next_controls));
    CHECK(limited.render(0, {}).status == SessionStatus::SequenceExhausted);
    const bool read_succeeded = limited.read_snapshot(last);
    CHECK(!read_succeeded && bytes_of(last) == before);
    const auto failed = inspect(profile, limited_ui.view(), {true, read_succeeded});
    CHECK(failed.snapshot_state == State::Retained && failed.controls_pending);
    CHECK(failed.frame_clock == 7 && failed.publication_revision == 6);
    CHECK(value(failed, "controls.expression") == "0.3125");
    CHECK(value(failed, "contacts.upper_held") == "1");

    Session stopped_limited({std::numeric_limits<std::uint64_t>::max(), 1});
    UiModel stopped_ui;
    constexpr auto distant_frame = std::uint64_t{1} << 60;
    CHECK(stopped_limited.prepare(profile, {48000.0, 64, 819, distant_frame}) == SessionStatus::Ok);
    stopped_ui.observe(read(stopped_limited));
    CHECK(inspect(profile, stopped_ui.view()).snapshot_state == State::Stopped);
    CHECK(stopped_limited.start() == SessionStatus::SequenceExhausted);
    auto last_stopped = stopped_ui.view().applied;
    CHECK(!stopped_limited.read_snapshot(last_stopped));
    const auto retained_stopped = inspect(profile, stopped_ui.view(), {true, false});
    CHECK(retained_stopped.snapshot_state == State::Retained);
    CHECK(retained_stopped.frame_clock == distant_frame);
    CHECK(retained_stopped.publication_revision == 2);
}

void defensive_copies_and_lifetime(RuntimeProfile profile) {
    Session session;
    UiModel ui;
    CHECK(session.prepare(profile, {48000.0, 64, 912, 0}) == SessionStatus::Ok);
    CHECK(session.start() == SessionStatus::Ok);
    ui.observe(read(session));
    submit(session, ui, ui.load_controls(distinct_controls()));
    publish(session, ui);
    const auto good_view = ui.view();

    for (unsigned variant = 0; variant < 6; ++variant) {
        auto bad_view = good_view;
        auto& controls = bad_view.applied.controls;
        controls.route_enabled[0] = false;
        controls.percussion.enabled = false;
        switch (variant) {
        case 0: controls.selected_banks[0] = static_cast<DrawbarBank>(2); break;
        case 1: controls.fixed_registrations[0] = static_cast<FixedRegistration>(255); break;
        case 2: controls.drawbars[1][0][8] = 9; break; // Silent, unselected memory still validates.
        case 3: controls.percussion.harmonic = static_cast<PercussionHarmonic>(2); break;
        case 4: controls.expression = std::numeric_limits<double>::quiet_NaN(); break;
        default: controls.expression = std::numeric_limits<double>::infinity(); break;
        }
        const auto document = inspect(profile, bad_view);
        for (const auto& row : document.sections[5].rows) CHECK(row.availability == Availability::Invalid);
        CHECK(value(document, "controls.upper").starts_with("Sound Invalid snapshot"));
        CHECK(value(document, "controls.banks") == "Invalid snapshot");
        CHECK(value(document, "controls.expression") == (variant >= 4 ? "Invalid" : "Invalid snapshot"));
        CHECK(lookup(document, "contacts.upper_held").availability == Availability::Available);
    }
    auto bad_edit = good_view;
    bad_edit.edited_banks[1] = static_cast<DrawbarBank>(255);
    const auto edit = inspect(profile, bad_edit);
    CHECK(value(edit, "controls.lower") == "Sound Fixed C# / Edit Invalid edit bank");
    CHECK(lookup(edit, "controls.lower").availability == Availability::Invalid);
    CHECK(lookup(edit, "controls.upper").availability == Availability::Available);
    CHECK(value(edit, "controls.banks") == bank_memory);

    for (unsigned variant = 0; variant < 4; ++variant) {
        auto bad_profile = profile;
        switch (variant) {
        case 0: bad_profile.profile_id[kNominalProfileId.size() - 1] = '2'; break;
        case 1: bad_profile.profile_id.fill('n'); break;
        case 2: bad_profile.profile_id[kNominalProfileId.size() + 1] = '\n'; break;
        default: bad_profile.profile_id[0] = static_cast<char>(0x80); break;
        }
        CHECK(inspect(bad_profile, good_view).profile_id.view() == "Unsupported or invalid profile ID");
    }
    for (unsigned variant = 0; variant < 4; ++variant) {
        auto bad_profile = profile;
        switch (variant) {
        case 0: bad_profile.authoring_sha256.fill('a'); break;
        case 1: bad_profile.authoring_sha256[0] = 'A'; break;
        case 2: bad_profile.authoring_sha256[63] = '\0'; break;
        default: bad_profile.authoring_sha256[1] = '\n'; break;
        }
        CHECK(inspect(bad_profile, good_view).profile_authoring_sha256.view() == "Invalid authoring digest");
    }

    const auto owning_copy = [profile, mutable_view = good_view]() mutable {
        const auto document = inspect(profile, mutable_view);
        auto moved_copy = document;
        profile.profile_id.fill('x');
        profile.authoring_sha256.fill('x');
        profile.sources[45].frequency_hz = 1.0;
        profile.output_gain = 1.0;
        mutable_view.applied.controls = {};
        same_document(moved_copy, document);
        return moved_copy;
    }();
    CHECK(owning_copy.profile_id.view() == kNominalProfileId);
    CHECK(owning_copy.profile_authoring_sha256.view() == declared_digest);
    CHECK(value(owning_copy, "generator.tone46_hz") == "431.765");
    CHECK(value(owning_copy, "controls.banks") == bank_memory);
    bounded(owning_copy.profile_id);
    for (const auto& card : owning_copy.sections) {
        for (const auto& row : card.rows) bounded(row.value);
    }

    // Adjacent finite values distinguish admission from six-digit rounding.
    // These forged profiles exercise display domains, not Session preparation
    // or Nyquist/phase-increment admission, which has a separate contract.
    for (const double gain : {0.0, 1.0, std::nextafter(1.0, 0.0), std::numeric_limits<double>::min()}) {
        auto finite_profile = profile;
        finite_profile.output_gain = gain;
        auto finite_view = good_view;
        finite_view.applied.controls.expression = gain;
        const auto document = inspect(finite_profile, finite_view);
        CHECK(lookup(document, "generator.output_gain").availability == Availability::Available);
        CHECK(lookup(document, "controls.expression").availability == Availability::Available);
    }
    for (const double outside : {std::nextafter(1.0, 2.0), -std::numeric_limits<double>::min()}) {
        auto finite_profile = profile;
        finite_profile.output_gain = outside;
        auto finite_view = good_view;
        finite_view.applied.controls.expression = outside;
        const auto document = inspect(finite_profile, finite_view);
        CHECK(value(document, "generator.output_gain") == "Invalid");
        CHECK(value(document, "controls.expression") == "Invalid");
    }
    for (const double frequency : {std::numeric_limits<double>::min(), 1.0e300}) {
        auto finite_profile = profile;
        finite_profile.sources[45].frequency_hz = frequency;
        CHECK(lookup(inspect(finite_profile, good_view), "generator.tone46_hz").availability == Availability::Available);
    }
    for (const double frequency : {-std::numeric_limits<double>::min(),
                                   std::numeric_limits<double>::quiet_NaN()}) {
        auto invalid_profile = profile;
        invalid_profile.sources[45].frequency_hz = frequency;
        CHECK(value(inspect(invalid_profile, good_view), "generator.tone46_hz") == "Invalid");
    }
    auto negative_zero = good_view;
    negative_zero.applied.controls.expression = -0.0;
    CHECK(value(inspect(profile, negative_zero), "controls.expression") == "0");
    CHECK(std::signbit(negative_zero.applied.controls.expression));
}

} // namespace

int main() {
    const auto profile = distinct_profile();
    Engine actual_default;
    CHECK(actual_default.prepare(profile, {48000.0, 64, 819, 0}) == Status::Ok);
    CHECK(actual_default.contact_mode() == ContactMode::Ideal);
    CHECK(contact_model_id(actual_default.contact_mode()) == kIdealContactModelId);
    CHECK(make_legacy_console_model().contacts.mode != make_nominal_console_model().contacts.mode);
    lifecycle_and_failed_reads(profile);
    defensive_copies_and_lifetime(profile);
    std::cout << "Inspection independent acceptance passed: 34 source-qualified rows, actual Session commands, "
                 "four selections per manual, real failed reads, owned immutable copies and finite admission.\n";
}
