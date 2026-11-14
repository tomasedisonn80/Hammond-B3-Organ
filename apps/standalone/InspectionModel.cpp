#include "InspectionModel.h"

#include "hammond/ContactBank.h"
#include "hammond/ScannerLine.h"

#include <charconv>
#include <cmath>
#include <system_error>

namespace hammond::standalone {
namespace {

using Availability = InspectionAvailability;
using Evidence = InspectionEvidence;

// No exported TonewheelBank constant exists for this documented family.
constexpr std::string_view kGeneratorModel = "ideal-shared-sine-v1";
constexpr std::string_view kGeneratorSource =
    "include/hammond/Profile.h; TonewheelBank.h; atlas pp. 61-72";
constexpr std::string_view kContactsSource =
    "apps/standalone/Session.h/.cpp; ContactBank.h; atlas pp. 37-42, 115-120";
constexpr std::string_view kPedalSource =
    "include/hammond/PedalVoice.h; atlas pp. 139-144";
constexpr std::string_view kScannerSource =
    "src/Engine.cpp; ScannerLine.h; docs/SCANNER_HANDOFF.md; atlas pp. 157-192";
constexpr std::string_view kAo28Source =
    "include/hammond/ConsoleModel.h; Percussion.h; docs/PLAN.md; atlas pp. 193-252";
constexpr std::string_view kLeslieSource =
    "docs/PLAN.md; docs/ROTARY_SCOPE.md; atlas pp. 253-348";
constexpr std::string_view kControlsSource =
    "include/hammond/ControlState.h; FixedRegistration.h; UiModel.h; atlas pp. 109-156, 397-402";

// The builder does not accept arbitrary external display text. Still bound every
// append so future wording cannot silently overrun the fixed document storage.
class TextWriter {
public:
    explicit TextWriter(InspectionText& text) noexcept : text_(text) { text_ = {}; }

    void append(std::string_view value) noexcept {
        if (text_.truncated) return;
        constexpr auto capacity = kInspectionTextCapacity - 1;
        const auto remaining = capacity - text_.size;
        const auto copied = value.size() < remaining ? value.size() : remaining;
        for (std::size_t index = 0; index < copied; ++index) {
            text_.bytes[text_.size + index] = value[index];
        }
        text_.size = static_cast<std::uint16_t>(text_.size + copied);
        if (copied != value.size()) {
            text_.size = static_cast<std::uint16_t>(capacity);
            for (std::size_t index = capacity - 3; index < capacity; ++index) {
                text_.bytes[index] = '.';
            }
            text_.truncated = true;
        }
        text_.bytes[text_.size] = '\0';
    }

    void integer(std::size_t value) noexcept {
        std::array<char, 32> buffer{};
        const auto result = std::to_chars(buffer.data(), buffer.data() + buffer.size(), value);
        if (result.ec != std::errc{}) {
            append("Invalid");
            return;
        }
        append({buffer.data(), static_cast<std::size_t>(result.ptr - buffer.data())});
    }

    void number(double value) noexcept {
        // Admission belongs to the value's caller; normalize display-only -0.
        if (value == 0.0) value = 0.0;
        std::array<char, 64> buffer{};
        const auto result = std::to_chars(buffer.data(), buffer.data() + buffer.size(),
                                          value, std::chars_format::general, 6);
        if (result.ec != std::errc{}) {
            append("Invalid");
            return;
        }
        append({buffer.data(), static_cast<std::size_t>(result.ptr - buffer.data())});
    }

private:
    InspectionText& text_;
};

[[nodiscard]] InspectionText text(std::string_view value) noexcept {
    InspectionText result{};
    TextWriter(result).append(value);
    return result;
}

[[nodiscard]] InspectionRow row(std::string_view id, std::string_view label,
                                 std::string_view value, Availability availability,
                                 Evidence evidence, std::string_view unit,
                                 std::string_view source) noexcept {
    return {id, label, text(value), unit, source, availability, evidence};
}

void set_number(InspectionRow& target, double value, bool valid) noexcept {
    if (!valid) {
        target.value = text("Invalid");
        target.availability = Availability::Invalid;
        target.evidence = Evidence::Unknown;
        return;
    }
    TextWriter(target.value).number(value);
}

[[nodiscard]] bool unit_interval(double value) noexcept {
    return std::isfinite(value) && value >= 0.0 && value <= 1.0;
}

[[nodiscard]] bool valid_profile_id(const RuntimeProfile& profile) noexcept {
    for (std::size_t index = 0; index < profile.profile_id.size(); ++index) {
        const char expected = index < kNominalProfileId.size() ? kNominalProfileId[index] : '\0';
        if (profile.profile_id[index] != expected) return false;
    }
    return true;
}

[[nodiscard]] bool valid_digest(const RuntimeProfile& profile) noexcept {
    for (std::size_t index = 0; index < kSha256HexLength; ++index) {
        const char value = profile.authoring_sha256[index];
        if (!((value >= '0' && value <= '9') || (value >= 'a' && value <= 'f'))) return false;
    }
    return profile.authoring_sha256[kSha256HexLength] == '\0';
}

[[nodiscard]] InspectionSnapshotState snapshot_state(
    const UiViewState& view, const InspectionRuntimeInfo& runtime) noexcept {
    if (!runtime.snapshot_available) return InspectionSnapshotState::Unavailable;
    if (!view.applied.prepared) return InspectionSnapshotState::Unprepared;
    if (!runtime.snapshot_read_succeeded) return InspectionSnapshotState::Retained;
    if (!view.applied.running) return InspectionSnapshotState::Stopped;
    return InspectionSnapshotState::Current;
}

template <std::size_t Count>
void held_count(InspectionRow& target, const std::array<bool, Count>& values,
                bool observed) noexcept {
    if (!observed) return;
    std::size_t count = 0;
    for (const bool held : values) {
        if (held) ++count;
    }
    TextWriter(target.value).integer(count);
    target.availability = Availability::Available;
    target.evidence = Evidence::Software;
}

void selection(InspectionRow& target, const UiViewState& view, Manual manual,
                bool observed, bool valid_controls) noexcept {
    const auto index = static_cast<std::size_t>(manual);
    TextWriter writer(target.value);
    writer.append("Sound ");
    if (!observed) {
        writer.append("Not observed");
    } else if (!valid_controls) {
        writer.append("Invalid snapshot");
        target.availability = Availability::Invalid;
    } else {
        PresetSelection selected{};
        // The complete copied controls have already passed validation.
        if (!control_preset_selection(view.applied.controls, manual, selected)) {
            writer.append("Invalid snapshot");
            target.availability = Availability::Invalid;
        } else {
            switch (selected) {
            case PresetSelection::Cancel: writer.append("Cancel"); break;
            case PresetSelection::BankA: writer.append("Bank A"); break;
            case PresetSelection::BankB: writer.append("Bank B"); break;
            default:
                writer.append("Fixed ");
                writer.append(preset_selection_label(selected));
                break;
            }
            target.availability = Availability::Available;
            target.evidence = Evidence::Software;
        }
    }
    writer.append(" / Edit ");
    if (!is_valid_drawbar_bank(view.edited_banks[index])) {
        writer.append("Invalid edit bank");
        target.availability = Availability::Invalid;
        target.evidence = Evidence::Unknown;
    } else {
        writer.append(view.edited_banks[index] == DrawbarBank::A ? "A" : "B");
    }
}

void retained_controls(InspectionCard& card, const UiViewState& view,
                       bool observed) noexcept {
    const auto& controls = view.applied.controls;
    const bool valid = observed && is_valid_control_snapshot(controls);
    card = {InspectionSection::Controls, "Retained controls",
            "Applied sound and bank memories; Edit is UI state. Readiness is not observed."};
    card.row_count = 6;
    constexpr std::array<std::string_view, 6> ids{
        "controls.upper", "controls.lower", "controls.banks", "controls.pedals",
        "controls.expression", "controls.percussion"};
    constexpr std::array<std::string_view, 6> labels{
        "Upper", "Lower", "Bank memories", "Nominal pedals", "Expression", "Percussion"};
    for (std::size_t index = 0; index < card.row_count; ++index) {
        card.rows[index] = row(ids[index], labels[index],
            !observed ? "Not observed" : (valid ? "" : "Invalid snapshot"),
            !observed ? Availability::NotObserved : (valid ? Availability::Available : Availability::Invalid),
            valid ? Evidence::Software : Evidence::Unknown, "", kControlsSource);
    }
    card.rows[3].unit = "positions 0-8";
    card.rows[4].unit = "normalized 0-1";
    selection(card.rows[0], view, Manual::Upper, observed, valid);
    selection(card.rows[1], view, Manual::Lower, observed, valid);
    if (!valid) {
        // A bad number is never formatted, even if another field also failed.
        if (observed && !unit_interval(controls.expression)) {
            card.rows[4].value = text("Invalid");
        }
        return;
    }

    TextWriter banks(card.rows[2].value);
    constexpr std::array<std::string_view, 4> bank_labels{"UA ", "UB ", "LA ", "LB "};
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        for (std::size_t bank = 0; bank < kDrawbarBankCount; ++bank) {
            const auto ordinal = manual * kDrawbarBankCount + bank;
            if (ordinal != 0) banks.append(" / ");
            banks.append(bank_labels[ordinal]);
            for (const auto position : controls.drawbars[manual][bank]) banks.integer(position);
        }
    }
    TextWriter pedals(card.rows[3].value);
    pedals.append("Mixture 1 ");
    pedals.integer(controls.pedal_drawbars[0]);
    pedals.append(" / Mixture 2 ");
    pedals.integer(controls.pedal_drawbars[1]);
    set_number(card.rows[4], controls.expression, true);

    TextWriter percussion(card.rows[5].value);
    percussion.append(controls.percussion.enabled ? "On" : "Off");
    percussion.append(controls.percussion.harmonic == PercussionHarmonic::Second ? " / Second" : " / Third");
    percussion.append(controls.percussion.volume == PercussionVolume::Normal ? " / Normal" : " / Soft");
    percussion.append(controls.percussion.decay == PercussionDecay::Slow ? " / Slow" : " / Fast");
    const bool eligible = controls.route_enabled[0] &&
                          controls.fixed_registrations[0] == FixedRegistration::None &&
                          controls.selected_banks[0] == DrawbarBank::B;
    percussion.append(eligible ? " / Upper B eligible" : " / Upper B ineligible");
}

} // namespace

std::string_view InspectionText::view() const noexcept {
    return {bytes.data(), size};
}

InspectionDocument make_inspection_document(
    const RuntimeProfile& profile, const UiViewState& view,
    const InspectionRuntimeInfo& runtime) noexcept {
    InspectionDocument result{};
    result.snapshot_state = snapshot_state(view, runtime);
    result.controls_pending = view.controls_pending;
    if (runtime.snapshot_available) {
        result.frame_clock = view.applied.frame_clock;
        result.publication_revision = view.applied.publication_revision;
    }
    result.profile_id = valid_profile_id(profile)
        ? text({profile.profile_id.data(), kNominalProfileId.size()})
        : text("Unsupported or invalid profile ID");
    result.profile_authoring_sha256 = valid_digest(profile)
        ? text({profile.authoring_sha256.data(), kSha256HexLength})
        : text("Invalid authoring digest");
    const bool observed = runtime.snapshot_available && view.applied.prepared;

    auto& generator = result.sections[0];
    generator = {InspectionSection::Generator, "Generator",
                 "Loaded nominal model values; no measured pickup waves, levels or tuning."};
    generator.row_count = 4;
    generator.rows[0] = row("generator.model", "Family", kGeneratorModel,
        Availability::Available, Evidence::Software, "", kGeneratorSource);
    generator.rows[1] = row("generator.sources", "Shared sources", "",
        Availability::Available, Evidence::Software, "sources", kGeneratorSource);
    TextWriter(generator.rows[1].value).integer(kToneSourceCount);
    generator.rows[2] = row("generator.tone46_hz", "Tone 46", "",
        Availability::Available, Evidence::Proposed, "Hz", kGeneratorSource);
    set_number(generator.rows[2], profile.sources[45].frequency_hz,
               std::isfinite(profile.sources[45].frequency_hz) && profile.sources[45].frequency_hz > 0.0);
    generator.rows[3] = row("generator.output_gain", "Output gain", "",
        Availability::Available, Evidence::Proposed, "normalized amplitude", kGeneratorSource);
    set_number(generator.rows[3], profile.output_gain, unit_interval(profile.output_gain));

    auto& contacts = result.sections[1];
    contacts = {InspectionSection::ContactsRouting, "Contacts / routing",
                "Held targets do not prove audibility. Pedal mixtures are not a measured reactor."};
    contacts.row_count = 6;
    contacts.rows[0] = row("contacts.model", "Contact family", kIdealContactModelId,
        Availability::Available, Evidence::Software, "", kContactsSource);
    contacts.rows[1] = row("contacts.upper_held", "Upper held", "Not observed",
        Availability::NotObserved, Evidence::Unknown, "targets", kContactsSource);
    contacts.rows[2] = row("contacts.lower_held", "Lower held", "Not observed",
        Availability::NotObserved, Evidence::Unknown, "targets", kContactsSource);
    contacts.rows[3] = row("contacts.pedals_held", "Pedals held", "Not observed",
        Availability::NotObserved, Evidence::Unknown, "targets", kContactsSource);
    held_count(contacts.rows[1], view.applied.held_keys[0], observed);
    held_count(contacts.rows[2], view.applied.held_keys[1], observed);
    held_count(contacts.rows[3], view.applied.held_pedals, observed);
    contacts.rows[4] = row("contacts.inventory", "Inventory", "",
        Availability::Available, Evidence::Software, "", kContactsSource);
    TextWriter inventory(contacts.rows[4].value);
    inventory.integer(kManualKeyCount);
    inventory.append(" + ");
    inventory.integer(kManualKeyCount);
    inventory.append(" manual keys / ");
    inventory.integer(kPedalCount);
    inventory.append(" pedals");
    contacts.rows[5] = row("contacts.pedal_model", "Pedal family", kNominalPedalVoiceModelId,
        Availability::Available, Evidence::Proposed, "", kPedalSource);

    auto& scanner = result.sections[2];
    scanner = {InspectionSection::Scanner, "Scanner",
               "Research module only; absent from this dry audio path. No specimen captures."};
    scanner.row_count = 3;
    scanner.rows[0] = row("scanner.audio", "Audio path", "Not connected",
        Availability::NotIntegrated, Evidence::Software, "", kScannerSource);
    scanner.rows[1] = row("scanner.research_model", "Research module only", kScannerLineModelId,
        Availability::Available, Evidence::Proposed, "", kScannerSource);
    scanner.rows[2] = row("scanner.physical_capture", "Specimen captures", "Not acquired",
        Availability::NotAcquired, Evidence::Unknown, "", kScannerSource);

    auto& ao28 = result.sections[3];
    ao28 = {InspectionSection::Ao28, "AO-28",
            "Percussion is a nominal surrogate, not a complete AO-28 circuit or readiness measurement."};
    ao28.row_count = 4;
    ao28.rows[0] = row("ao28.circuit", "Complete circuit", "Not connected",
        Availability::NotIntegrated, Evidence::Software, "", kAo28Source);
    ao28.rows[1] = row("ao28.percussion_model", "Percussion surrogate", kPercussionModelId,
        Availability::Available, Evidence::Proposed, "", kAo28Source);
    ao28.rows[2] = row("ao28.specimen", "Specimen / revision", "Not acquired",
        Availability::NotAcquired, Evidence::Unknown, "", kAo28Source);
    ao28.rows[3] = row("ao28.voltage", "Physical voltage", "Unavailable",
        Availability::NotAcquired, Evidence::Unknown, "V", kAo28Source);

    auto& leslie = result.sections[4];
    leslie = {InspectionSection::Leslie, "Leslie",
              "Documentary target, not an installed specimen. No captures qualify physical fidelity."};
    leslie.row_count = 5;
    leslie.rows[0] = row("leslie.audio", "Cabinet audio", "Not connected",
        Availability::NotIntegrated, Evidence::Software, "", kLeslieSource);
    leslie.rows[1] = row("leslie.target", "Documentary target", "122 baseline; 147 separate",
        Availability::Available, Evidence::Documented, "", kLeslieSource);
    leslie.rows[2] = row("leslie.horn_speed", "Horn speed", "Unavailable",
        Availability::NotIntegrated, Evidence::Unknown, "rpm", kLeslieSource);
    leslie.rows[3] = row("leslie.drum_speed", "Drum speed", "Unavailable",
        Availability::NotIntegrated, Evidence::Unknown, "rpm", kLeslieSource);
    leslie.rows[4] = row("leslie.microphone", "Microphone geometry", "Not acquired",
        Availability::NotAcquired, Evidence::Unknown, "m", kLeslieSource);

    retained_controls(result.sections[5], view, observed);

    result.rotary_row_count = 6;
    result.rotary_rows[0] = row("rotary.path", "Audio path",
        "Nominal dry organ; cabinet audio not connected", Availability::NotIntegrated,
        Evidence::Software, "", "src/Engine.cpp; apps/standalone/Session.cpp");
    result.rotary_rows[1] = row("rotary.target", "Documentary target",
        "Leslie 122 baseline; 147 separate", Availability::Available,
        Evidence::Documented, "", "docs/PLAN.md; atlas pp. 55-60, 253-264");
    result.rotary_rows[2] = row("rotary.artwork", "Artwork", "Atlas concept, decorative",
        Availability::Available, Evidence::Documented, "",
        "docs/design/atlas-reference.json; atlas cover, p. 409");
    result.rotary_rows[3] = row("rotary.speeds", "Rotor speeds",
        "Horn unavailable / Drum unavailable", Availability::NotIntegrated,
        Evidence::Unknown, "rpm", kLeslieSource);
    result.rotary_rows[4] = row("rotary.microphone", "Microphone geometry", "Not acquired",
        Availability::NotAcquired, Evidence::Unknown, "m", kLeslieSource);
    result.rotary_rows[5] = row("rotary.brake", "Stop / brake", "Not modeled",
        Availability::NotIntegrated, Evidence::Software, "",
        "docs/ROTARY_SCOPE.md; atlas pp. 256, 289, 413 (optional accessory)");
    return result;
}

} // namespace hammond::standalone
