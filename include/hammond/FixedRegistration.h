#pragma once

#include "hammond/Types.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <string_view>

namespace hammond {

inline constexpr std::size_t kFixedRegistrationCount = 9;
inline constexpr std::size_t kPresetSelectionCount = 12;
using FixedRegistrationPositions = std::array<std::uint8_t, kDrawbarCount>;

enum class FixedRegistration : std::uint8_t {
    None = 0, CSharp = 1, D = 2, DSharp = 3, E = 4,
    F = 5, FSharp = 6, G = 7, GSharp = 8, A = 9,
};

enum class PresetSelection : std::uint8_t {
    Cancel = 0, CSharp = 1, D = 2, DSharp = 3, E = 4,
    F = 5, FSharp = 6, G = 7, GSharp = 8, A = 9,
    BankA = 10, BankB = 11,
};

[[nodiscard]] constexpr bool is_valid_fixed_registration(
    FixedRegistration registration) noexcept {
    return static_cast<std::uint8_t>(registration) <= 9;
}

[[nodiscard]] constexpr bool is_valid_preset_selection(
    PresetSelection selection) noexcept {
    return static_cast<std::uint8_t>(selection) <= 11;
}

// Copy one documentary row of tap indices, never calibrated amplitudes.
// None, invalid registrations and invalid manuals preserve the destination.
[[nodiscard]] bool fixed_registration_positions(
    Manual manual, FixedRegistration registration,
    FixedRegistrationPositions& destination) noexcept;

// All views have program lifetime. The digest identifies the frozen authoring
// file bytes; no runtime file access, initialization or allocation is needed.
[[nodiscard]] std::string_view fixed_registration_catalog_id() noexcept;
[[nodiscard]] std::string_view fixed_registration_catalog_sha256() noexcept;
[[nodiscard]] std::string_view fixed_registration_label(
    FixedRegistration registration) noexcept;
[[nodiscard]] std::string_view preset_selection_label(
    PresetSelection selection) noexcept;

} // namespace hammond
