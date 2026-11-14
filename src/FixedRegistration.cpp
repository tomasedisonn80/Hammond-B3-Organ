#include "hammond/FixedRegistration.h"
#include "hammond/generated/FixedRegistrationData.h"

namespace hammond {
namespace {

constexpr std::array<std::string_view, kPresetSelectionCount> kSelectionLabels{
    "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B",
};

} // namespace

bool fixed_registration_positions(Manual manual, FixedRegistration registration,
                                  FixedRegistrationPositions& destination) noexcept {
    if (!is_valid_manual(manual) || !is_valid_fixed_registration(registration) ||
        registration == FixedRegistration::None) {
        return false;
    }
    const auto manual_index = static_cast<std::size_t>(manual);
    const auto registration_index = static_cast<std::size_t>(registration) - 1;
    destination = generated::kFixedRegistrationPositions[manual_index][registration_index];
    return true;
}

std::string_view fixed_registration_catalog_id() noexcept {
    return generated::kFixedRegistrationCatalogId;
}

std::string_view fixed_registration_catalog_sha256() noexcept {
    return generated::kFixedRegistrationCatalogRawSha256;
}

std::string_view fixed_registration_label(FixedRegistration registration) noexcept {
    if (!is_valid_fixed_registration(registration)) return {};
    if (registration == FixedRegistration::None) return "none";
    return kSelectionLabels[static_cast<std::size_t>(registration)];
}

std::string_view preset_selection_label(PresetSelection selection) noexcept {
    if (!is_valid_preset_selection(selection)) return {};
    return kSelectionLabels[static_cast<std::size_t>(selection)];
}

} // namespace hammond
