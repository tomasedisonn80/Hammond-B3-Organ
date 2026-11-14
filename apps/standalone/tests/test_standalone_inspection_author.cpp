#include "InspectionModel.h"
#include "TestSupport.h"

#include "hammond/ContactBank.h"
#include "hammond/ScannerLine.h"

#include <array>
#include <cstddef>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <new>
#include <string_view>
#include <type_traits>

// This executable observes ordinary C++ new/delete on the calling thread. It is
// not a callback timing, system-allocator, physical fidelity or other-thread test.
namespace inspection_allocation_probe {
thread_local bool active = false;
thread_local std::size_t allocations = 0;
thread_local std::size_t deallocations = 0;
}

#if defined(_MSC_VER)
#define INSPECTION_NOINLINE __declspec(noinline)
#elif defined(__GNUC__) || defined(__clang__)
#define INSPECTION_NOINLINE __attribute__((noinline))
#else
#define INSPECTION_NOINLINE
#endif

INSPECTION_NOINLINE void* operator new(std::size_t size) {
    if (inspection_allocation_probe::active) ++inspection_allocation_probe::allocations;
    if (void* result = std::malloc(size == 0 ? 1 : size)) return result;
    throw std::bad_alloc{};
}
INSPECTION_NOINLINE void* operator new[](std::size_t size) { return ::operator new(size); }
INSPECTION_NOINLINE void operator delete(void* pointer) noexcept {
    if (inspection_allocation_probe::active && pointer != nullptr) {
        ++inspection_allocation_probe::deallocations;
    }
    std::free(pointer);
}
INSPECTION_NOINLINE void operator delete[](void* pointer) noexcept { ::operator delete(pointer); }
INSPECTION_NOINLINE void operator delete(void* pointer, std::size_t) noexcept { ::operator delete(pointer); }
INSPECTION_NOINLINE void operator delete[](void* pointer, std::size_t) noexcept { ::operator delete[](pointer); }

#undef INSPECTION_NOINLINE

namespace {
using namespace hammond;
using namespace hammond::standalone;
using Availability = InspectionAvailability;
using Evidence = InspectionEvidence;
using State = InspectionSnapshotState;
constexpr InspectionRuntimeInfo current{true, true};

UiViewState ready_view() {
    UiViewState view{};
    view.applied.prepared = true;
    view.applied.running = true;
    view.applied.sample_rate = 48000.0;
    view.applied.frame_clock = 12345;
    view.applied.publication_revision = 82;
    return view;
}

const InspectionRow& find_row(const InspectionDocument& document, std::string_view id) {
    for (const auto& card : document.sections) {
        CHECK(card.row_count <= card.rows.size());
        for (std::size_t index = 0; index < card.row_count; ++index) {
            if (card.rows[index].id == id) return card.rows[index];
        }
    }
    CHECK(document.rotary_row_count <= document.rotary_rows.size());
    for (std::size_t index = 0; index < document.rotary_row_count; ++index) {
        if (document.rotary_rows[index].id == id) return document.rotary_rows[index];
    }
    hammond_test::fail("required inspection row exists", __FILE__, __LINE__, id);
}

std::string_view value(const InspectionDocument& document, std::string_view id) {
    return find_row(document, id).value.view();
}

void bounded_text(const InspectionText& item) {
    CHECK(item.bytes.size() == 128);
    CHECK(item.size < item.bytes.size());
    CHECK(item.view().size() == item.size);
    CHECK(item.bytes[item.size] == '\0');
    for (const char byte : item.view()) CHECK(byte >= ' ' && byte <= '~');
    if (item.truncated) CHECK(item.view().ends_with("..."));
}

bool equal_row(const InspectionRow& left, const InspectionRow& right) {
    return left.id == right.id && left.label == right.label &&
           left.value.bytes == right.value.bytes && left.value.size == right.value.size &&
           left.value.truncated == right.value.truncated && left.unit == right.unit &&
           left.source == right.source && left.availability == right.availability &&
           left.evidence == right.evidence;
}

void equal_documents(const InspectionDocument& left, const InspectionDocument& right) {
    CHECK(left.snapshot_state == right.snapshot_state);
    CHECK(left.controls_pending == right.controls_pending);
    CHECK(left.frame_clock == right.frame_clock);
    CHECK(left.publication_revision == right.publication_revision);
    CHECK(left.profile_id.bytes == right.profile_id.bytes);
    CHECK(left.profile_id.size == right.profile_id.size);
    CHECK(left.profile_id.truncated == right.profile_id.truncated);
    CHECK(left.profile_authoring_sha256.bytes == right.profile_authoring_sha256.bytes);
    CHECK(left.profile_authoring_sha256.size == right.profile_authoring_sha256.size);
    CHECK(left.profile_authoring_sha256.truncated == right.profile_authoring_sha256.truncated);
    for (std::size_t section = 0; section < left.sections.size(); ++section) {
        const auto& a = left.sections[section];
        const auto& b = right.sections[section];
        CHECK(a.section == b.section && a.title == b.title && a.summary == b.summary);
        CHECK(a.row_count == b.row_count);
        for (std::size_t index = 0; index < a.rows.size(); ++index) CHECK(equal_row(a.rows[index], b.rows[index]));
    }
    CHECK(left.rotary_row_count == right.rotary_row_count);
    for (std::size_t index = 0; index < left.rotary_rows.size(); ++index) {
        CHECK(equal_row(left.rotary_rows[index], right.rotary_rows[index]));
    }
}

struct ExpectedRow {
    std::string_view id;
    std::string_view unit;
    Availability availability;
    Evidence evidence;
    std::string_view source_fragment;
};

void stable_inventory_and_truth(const RuntimeProfile& profile) {
    const auto document = make_inspection_document(profile, ready_view(), current);
    constexpr std::array<std::size_t, 6> counts{4, 6, 3, 4, 5, 6};
    constexpr std::array expected{
        ExpectedRow{"generator.model", "", Availability::Available, Evidence::Software, "TonewheelBank.h"},
        ExpectedRow{"generator.sources", "sources", Availability::Available, Evidence::Software, "Profile.h"},
        ExpectedRow{"generator.tone46_hz", "Hz", Availability::Available, Evidence::Proposed, "61-72"},
        ExpectedRow{"generator.output_gain", "normalized amplitude", Availability::Available, Evidence::Proposed, "Profile.h"},
        ExpectedRow{"contacts.model", "", Availability::Available, Evidence::Software, "ContactBank.h"},
        ExpectedRow{"contacts.upper_held", "targets", Availability::Available, Evidence::Software, "Session.h/.cpp"},
        ExpectedRow{"contacts.lower_held", "targets", Availability::Available, Evidence::Software, "Session.h/.cpp"},
        ExpectedRow{"contacts.pedals_held", "targets", Availability::Available, Evidence::Software, "Session.h/.cpp"},
        ExpectedRow{"contacts.inventory", "", Availability::Available, Evidence::Software, "37-42"},
        ExpectedRow{"contacts.pedal_model", "", Availability::Available, Evidence::Proposed, "PedalVoice.h"},
        ExpectedRow{"scanner.audio", "", Availability::NotIntegrated, Evidence::Software, "Engine.cpp"},
        ExpectedRow{"scanner.research_model", "", Availability::Available, Evidence::Proposed, "ScannerLine.h"},
        ExpectedRow{"scanner.physical_capture", "", Availability::NotAcquired, Evidence::Unknown, "SCANNER_HANDOFF.md"},
        ExpectedRow{"ao28.circuit", "", Availability::NotIntegrated, Evidence::Software, "ConsoleModel.h"},
        ExpectedRow{"ao28.percussion_model", "", Availability::Available, Evidence::Proposed, "Percussion.h"},
        ExpectedRow{"ao28.specimen", "", Availability::NotAcquired, Evidence::Unknown, "193-252"},
        ExpectedRow{"ao28.voltage", "V", Availability::NotAcquired, Evidence::Unknown, "PLAN.md"},
        ExpectedRow{"leslie.audio", "", Availability::NotIntegrated, Evidence::Software, "ROTARY_SCOPE.md"},
        ExpectedRow{"leslie.target", "", Availability::Available, Evidence::Documented, "253-348"},
        ExpectedRow{"leslie.horn_speed", "rpm", Availability::NotIntegrated, Evidence::Unknown, "ROTARY_SCOPE.md"},
        ExpectedRow{"leslie.drum_speed", "rpm", Availability::NotIntegrated, Evidence::Unknown, "ROTARY_SCOPE.md"},
        ExpectedRow{"leslie.microphone", "m", Availability::NotAcquired, Evidence::Unknown, "ROTARY_SCOPE.md"},
        ExpectedRow{"controls.upper", "", Availability::Available, Evidence::Software, "ControlState.h"},
        ExpectedRow{"controls.lower", "", Availability::Available, Evidence::Software, "FixedRegistration.h"},
        ExpectedRow{"controls.banks", "", Availability::Available, Evidence::Software, "UiModel.h"},
        ExpectedRow{"controls.pedals", "positions 0-8", Availability::Available, Evidence::Software, "109-156"},
        ExpectedRow{"controls.expression", "normalized 0-1", Availability::Available, Evidence::Software, "ControlState.h"},
        ExpectedRow{"controls.percussion", "", Availability::Available, Evidence::Software, "397-402"},
        ExpectedRow{"rotary.path", "", Availability::NotIntegrated, Evidence::Software, "Engine.cpp"},
        ExpectedRow{"rotary.target", "", Availability::Available, Evidence::Documented, "55-60, 253-264"},
        ExpectedRow{"rotary.artwork", "", Availability::Available, Evidence::Documented, "atlas-reference.json"},
        ExpectedRow{"rotary.speeds", "rpm", Availability::NotIntegrated, Evidence::Unknown, "ROTARY_SCOPE.md"},
        ExpectedRow{"rotary.microphone", "m", Availability::NotAcquired, Evidence::Unknown, "ROTARY_SCOPE.md"},
        ExpectedRow{"rotary.brake", "", Availability::NotIntegrated, Evidence::Software, "256, 289, 413"},
    };
    std::size_t ordinal = 0;
    for (std::size_t section = 0; section < document.sections.size(); ++section) {
        const auto& card = document.sections[section];
        CHECK(static_cast<std::size_t>(card.section) == section);
        CHECK(!card.title.empty() && !card.summary.empty());
        CHECK(card.row_count == counts[section]);
        for (std::size_t index = 0; index < card.rows.size(); ++index) {
            if (index < card.row_count) CHECK(card.rows[index].id == expected[ordinal++].id);
            else CHECK(card.rows[index].id.empty() && card.rows[index].value.size == 0);
        }
    }
    CHECK(document.rotary_row_count == 6);
    for (const auto& item : document.rotary_rows) CHECK(item.id == expected[ordinal++].id);
    CHECK(ordinal == expected.size());
    for (const auto& item : expected) {
        const auto& actual = find_row(document, item.id);
        CHECK(actual.unit == item.unit && actual.availability == item.availability);
        CHECK(actual.evidence == item.evidence && actual.source.find(item.source_fragment) != std::string_view::npos);
        CHECK(!actual.label.empty());
        bounded_text(actual.value);
        CHECK(!actual.value.truncated);
    }
    CHECK(value(document, "generator.model") == "ideal-shared-sine-v1");
    CHECK(value(document, "generator.sources") == "91");
    CHECK(value(document, "contacts.model") == kIdealContactModelId);
    CHECK(value(document, "contacts.model") != kNominalContactModelId);
    CHECK(value(document, "contacts.inventory") == "61 + 61 manual keys / 25 pedals");
    CHECK(value(document, "contacts.pedal_model") == kNominalPedalVoiceModelId);
    CHECK(value(document, "scanner.research_model") == kScannerLineModelId);
    CHECK(find_row(document, "scanner.research_model").label == "Research module only");
    CHECK(value(document, "ao28.percussion_model") == kPercussionModelId);
    for (const auto id : {"scanner.audio", "ao28.circuit", "leslie.audio"}) CHECK(value(document, id) == "Not connected");
    for (const auto id : {"ao28.voltage", "leslie.horn_speed", "leslie.drum_speed"}) CHECK(value(document, id) == "Unavailable");
    for (const auto id : {"scanner.physical_capture", "ao28.specimen", "leslie.microphone", "rotary.microphone"}) {
        CHECK(value(document, id) == "Not acquired");
    }
    CHECK(value(document, "rotary.path") == "Nominal dry organ; cabinet audio not connected");
    CHECK(value(document, "rotary.target") == "Leslie 122 baseline; 147 separate");
    CHECK(value(document, "rotary.artwork") == "Atlas concept, decorative");
    CHECK(value(document, "rotary.speeds") == "Horn unavailable / Drum unavailable");
    CHECK(value(document, "rotary.brake") == "Not modeled");
}

void snapshot_precedence(const RuntimeProfile& profile) {
    for (const bool available : {false, true}) {
        for (const bool prepared : {false, true}) {
            for (const bool read : {false, true}) {
                for (const bool running : {false, true}) {
                    auto view = ready_view();
                    view.applied.prepared = prepared;
                    view.applied.running = running;
                    view.applied.held_keys[0][60] = true;
                    view.controls_pending = true;
                    const auto document = make_inspection_document(profile, view, {available, read});
                    const auto expected = !available ? State::Unavailable : !prepared ? State::Unprepared :
                                          !read ? State::Retained : !running ? State::Stopped : State::Current;
                    CHECK(document.snapshot_state == expected);
                    CHECK(document.controls_pending);
                    CHECK(document.frame_clock == (available ? 12345U : 0U));
                    CHECK(document.publication_revision == (available ? 82U : 0U));
                    if (available && prepared) {
                        CHECK(value(document, "contacts.upper_held") == "1");
                        CHECK(value(document, "controls.expression") == "1");
                    } else {
                        CHECK(value(document, "contacts.upper_held") == "Not observed");
                        CHECK(value(document, "controls.expression") == "Not observed");
                        CHECK(find_row(document, "controls.expression").availability == Availability::NotObserved);
                        CHECK(value(document, "controls.upper") == "Sound Not observed / Edit B");
                    }
                }
            }
        }
    }
    auto zero_clock = ready_view();
    zero_clock.applied.frame_clock = 0;
    zero_clock.applied.publication_revision = 0;
    CHECK(make_inspection_document(profile, zero_clock, current).snapshot_state == State::Current);
    CHECK(make_inspection_document(profile, zero_clock, {true, false}).snapshot_state == State::Retained);
}

void profile_values_and_admission(RuntimeProfile profile) {
    profile.sources[45].frequency_hz = 443.987654;
    profile.output_gain = 0.123456789;
    profile.authoring_sha256.fill('a');
    profile.authoring_sha256.back() = '\0';
    const auto document = make_inspection_document(profile, ready_view(), current);
    CHECK(document.profile_id.view() == kNominalProfileId);
    CHECK(document.profile_authoring_sha256.size == 64);
    CHECK(document.profile_authoring_sha256.view() == std::string_view(profile.authoring_sha256.data(), 64));
    CHECK(value(document, "generator.tone46_hz") == "443.988");
    CHECK(value(document, "generator.output_gain") == "0.123457");
    bounded_text(document.profile_id);
    bounded_text(document.profile_authoring_sha256);
    CHECK(!document.profile_id.truncated && !document.profile_authoring_sha256.truncated);

    for (std::size_t variant = 0; variant < 6; ++variant) {
        auto invalid = profile;
        switch (variant) {
        case 0: invalid.profile_id[0] = 'x'; break;
        case 1: invalid.profile_id[0] = '\n'; break;
        case 2: invalid.profile_id[0] = static_cast<char>(0xFF); break;
        case 3: invalid.profile_id[4] = '\0'; break;
        case 4: invalid.profile_id.back() = 'x'; break;
        default: invalid.profile_id.fill('x'); break;
        }
        const auto result = make_inspection_document(invalid, ready_view(), current);
        CHECK(result.profile_id.view() == "Unsupported or invalid profile ID");
        bounded_text(result.profile_id);
    }
    for (std::size_t variant = 0; variant < 6; ++variant) {
        auto invalid = profile;
        switch (variant) {
        case 0: invalid.authoring_sha256[0] = 'A'; break;
        case 1: invalid.authoring_sha256[0] = '\n'; break;
        case 2: invalid.authoring_sha256[0] = static_cast<char>(0xFF); break;
        case 3: invalid.authoring_sha256[4] = '\0'; break;
        case 4: invalid.authoring_sha256[63] = '\0'; break;
        default: invalid.authoring_sha256.back() = 'a'; break;
        }
        const auto result = make_inspection_document(invalid, ready_view(), current);
        CHECK(result.profile_authoring_sha256.view() == "Invalid authoring digest");
        bounded_text(result.profile_authoring_sha256);
    }
    for (const double invalid : {0.0, -0.0, -1.0, std::numeric_limits<double>::infinity(),
                                 -std::numeric_limits<double>::infinity(), std::numeric_limits<double>::quiet_NaN()}) {
        auto candidate = profile;
        candidate.sources[45].frequency_hz = invalid;
        const auto result = make_inspection_document(candidate, ready_view(), current);
        CHECK(value(result, "generator.tone46_hz") == "Invalid");
        CHECK(find_row(result, "generator.tone46_hz").availability == Availability::Invalid);
    }
    for (const double invalid : {-0.001, 1.001, std::numeric_limits<double>::infinity(),
                                 -std::numeric_limits<double>::infinity(), std::numeric_limits<double>::quiet_NaN()}) {
        auto candidate = profile;
        candidate.output_gain = invalid;
        const auto result = make_inspection_document(candidate, ready_view(), current);
        CHECK(value(result, "generator.output_gain") == "Invalid");
        CHECK(find_row(result, "generator.output_gain").availability == Availability::Invalid);
    }
    profile.output_gain = -0.0;
    CHECK(value(make_inspection_document(profile, ready_view(), current), "generator.output_gain") == "0");
}

void applied_desired_edit_and_held(const RuntimeProfile& profile) {
    auto view = ready_view();
    auto& applied = view.applied.controls;
    applied.drawbars[0][0].fill(1);
    applied.drawbars[0][1].fill(2);
    applied.drawbars[1][0].fill(3);
    applied.drawbars[1][1].fill(4);
    applied.fixed_registrations = {FixedRegistration::CSharp, FixedRegistration::E};
    applied.selected_banks = {DrawbarBank::A, DrawbarBank::B};
    applied.route_enabled = {true, false};
    applied.pedal_drawbars = {3, 7};
    applied.expression = 0.375;
    applied.percussion = {true, PercussionHarmonic::Third, PercussionVolume::Soft, PercussionDecay::Fast};
    view.edited_banks = {DrawbarBank::B, DrawbarBank::A};
    view.controls_pending = true;
    view.controls.drawbars[0][0].fill(8);
    view.controls.expression = 0.99;
    view.controls.pedal_drawbars = {8, 0};
    // Even invalid desired values cannot contaminate applied inspection.
    view.controls.selected_banks[0] = static_cast<DrawbarBank>(255);
    view.applied.held_keys[0][0] = view.applied.held_keys[0][31] = view.applied.held_keys[0][60] = true;
    view.applied.held_keys[1][0] = view.applied.held_keys[1][60] = true;
    view.applied.held_pedals.fill(true);
    const auto document = make_inspection_document(profile, view, current);
    CHECK(document.controls_pending);
    CHECK(value(document, "controls.upper") == "Sound Fixed C# / Edit B");
    CHECK(value(document, "controls.lower") == "Sound Cancel / Edit A");
    CHECK(value(document, "controls.banks") == "UA 111111111 / UB 222222222 / LA 333333333 / LB 444444444");
    CHECK(value(document, "controls.pedals") == "Mixture 1 3 / Mixture 2 7");
    CHECK(value(document, "controls.expression") == "0.375");
    CHECK(value(document, "controls.percussion") == "On / Third / Soft / Fast / Upper B ineligible");
    CHECK(value(document, "contacts.upper_held") == "3");
    CHECK(value(document, "contacts.lower_held") == "2");
    CHECK(value(document, "contacts.pedals_held") == "25");
    applied.route_enabled[0] = false;
    const auto cancelled = make_inspection_document(profile, view, current);
    CHECK(value(cancelled, "controls.upper") == "Sound Cancel / Edit B");
    CHECK(value(cancelled, "controls.banks") == value(document, "controls.banks"));
    CHECK(value(cancelled, "contacts.upper_held") == "3");
}

void percussion_boundaries(const RuntimeProfile& profile) {
    for (unsigned mask = 0; mask < 128; ++mask) {
        auto view = ready_view();
        auto& controls = view.applied.controls;
        controls.route_enabled[0] = (mask & 1U) != 0;
        controls.selected_banks[0] = (mask & 2U) != 0 ? DrawbarBank::B : DrawbarBank::A;
        controls.fixed_registrations[0] = (mask & 4U) != 0 ? FixedRegistration::FSharp : FixedRegistration::None;
        controls.percussion.enabled = (mask & 8U) != 0;
        controls.percussion.harmonic = (mask & 16U) != 0 ? PercussionHarmonic::Third : PercussionHarmonic::Second;
        controls.percussion.volume = (mask & 32U) != 0 ? PercussionVolume::Soft : PercussionVolume::Normal;
        controls.percussion.decay = (mask & 64U) != 0 ? PercussionDecay::Fast : PercussionDecay::Slow;
        const auto document = make_inspection_document(profile, view, current);
        const auto actual = value(document, "controls.percussion");
        CHECK(actual.starts_with(controls.percussion.enabled ? "On / " : "Off / "));
        CHECK(actual.find((mask & 16U) != 0 ? " / Third" : " / Second") != std::string_view::npos);
        CHECK(actual.find((mask & 32U) != 0 ? " / Soft" : " / Normal") != std::string_view::npos);
        CHECK(actual.find((mask & 64U) != 0 ? " / Fast" : " / Slow") != std::string_view::npos);
        const bool eligible = (mask & 7U) == 3U;
        CHECK(actual.ends_with(eligible ? " / Upper B eligible" : " / Upper B ineligible"));
    }
}

void invalid_control_admission(const RuntimeProfile& profile) {
    for (unsigned variant = 0; variant < 14; ++variant) {
        auto view = ready_view();
        auto& controls = view.applied.controls;
        switch (variant) {
        case 0: controls.selected_banks[0] = static_cast<DrawbarBank>(255); break;
        case 1: controls.selected_banks[1] = static_cast<DrawbarBank>(2); break;
        case 2: controls.fixed_registrations[0] = static_cast<FixedRegistration>(10); break;
        case 3: controls.fixed_registrations[1] = static_cast<FixedRegistration>(255); break;
        case 4: controls.percussion.harmonic = static_cast<PercussionHarmonic>(255); break;
        case 5: controls.percussion.volume = static_cast<PercussionVolume>(2); break;
        case 6: controls.percussion.decay = static_cast<PercussionDecay>(2); break;
        case 7: controls.drawbars[0][0][0] = 9; break;
        case 8: controls.drawbars[1][1][8] = 255; break;
        case 9: controls.pedal_drawbars[0] = 9; break;
        case 10: controls.pedal_drawbars[1] = 255; break;
        case 11: controls.expression = std::numeric_limits<double>::quiet_NaN(); break;
        case 12: controls.expression = -0.001; break;
        default: controls.expression = 1.001; break;
        }
        const auto document = make_inspection_document(profile, view, current);
        for (const auto& item : document.sections[5].rows) CHECK(item.availability == Availability::Invalid);
        CHECK(value(document, "controls.upper").starts_with("Sound Invalid snapshot"));
        CHECK(value(document, "controls.lower").starts_with("Sound Invalid snapshot"));
        CHECK(value(document, "controls.banks") == "Invalid snapshot");
        CHECK(value(document, "controls.percussion") == "Invalid snapshot");
        CHECK(value(document, "controls.expression") == (variant >= 11 ? "Invalid" : "Invalid snapshot"));
    }
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        auto view = ready_view();
        view.edited_banks[manual] = static_cast<DrawbarBank>(255);
        const auto document = make_inspection_document(profile, view, current);
        const auto& bad = document.sections[5].rows[manual];
        CHECK(bad.value.view() == "Sound Bank B / Edit Invalid edit bank");
        CHECK(bad.availability == Availability::Invalid);
        CHECK(document.sections[5].rows[1 - manual].availability == Availability::Available);
        CHECK(find_row(document, "controls.banks").availability == Availability::Available);
    }
}

void ownership_determinism_and_allocation(RuntimeProfile profile) {
    static_assert(std::is_trivially_copyable_v<InspectionDocument>);
    static_assert(std::is_trivially_copyable_v<RuntimeProfile>);
    static_assert(std::is_trivially_copyable_v<UiViewState>);
    auto view = ready_view();
    std::array<std::byte, sizeof(profile)> profile_before{};
    std::array<std::byte, sizeof(view)> view_before{};
    std::memcpy(profile_before.data(), &profile, sizeof(profile));
    std::memcpy(view_before.data(), &view, sizeof(view));
    const auto first = make_inspection_document(profile, view, current);
    const auto second = make_inspection_document(profile, view, current);
    equal_documents(first, second);
    CHECK(std::memcmp(profile_before.data(), &profile, sizeof(profile)) == 0);
    CHECK(std::memcmp(view_before.data(), &view, sizeof(view)) == 0);
    profile.profile_id.fill('x');
    profile.authoring_sha256.fill('x');
    profile.sources[45].frequency_hz = 123.0;
    view.applied.controls.expression = 0.123;
    equal_documents(first, second);
    CHECK(first.profile_id.view() == kNominalProfileId);
    CHECK(value(first, "controls.expression") == "1");

    // Explicit calls through volatile function pointers calibrate interposition
    // without permitting new-expression elision to make the guard vacuous.
    using Allocate = void* (*)(std::size_t);
    using Free = void (*)(void*) noexcept;
    Allocate volatile allocate = static_cast<Allocate>(&::operator new);
    Free volatile release = static_cast<Free>(&::operator delete);
    inspection_allocation_probe::allocations = 0;
    inspection_allocation_probe::deallocations = 0;
    inspection_allocation_probe::active = true;
    void* calibration = allocate(37);
    release(calibration);
    inspection_allocation_probe::active = false;
    CHECK(inspection_allocation_probe::allocations == 1);
    CHECK(inspection_allocation_probe::deallocations == 1);

    inspection_allocation_probe::allocations = 0;
    inspection_allocation_probe::deallocations = 0;
    inspection_allocation_probe::active = true;
    const auto guarded = make_inspection_document(profile, view, {true, false});
    inspection_allocation_probe::active = false;
    CHECK(inspection_allocation_probe::allocations == 0);
    CHECK(inspection_allocation_probe::deallocations == 0);
    CHECK(guarded.snapshot_state == State::Retained);
    CHECK(value(guarded, "generator.tone46_hz") == "123");
}

} // namespace

int main() {
    const auto profile = load_test_profile();
    stable_inventory_and_truth(profile);
    snapshot_precedence(profile);
    profile_values_and_admission(profile);
    applied_desired_edit_and_held(profile);
    percussion_boundaries(profile);
    invalid_control_admission(profile);
    ownership_determinism_and_allocation(profile);
    std::cout << "Inspection author checks passed: bounded copied facts, truthful models and observations.\n";
}
