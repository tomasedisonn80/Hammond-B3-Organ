#pragma once

#include "hammond/FixedRegistration.h"
#include "hammond/Percussion.h"
#include "hammond/PedalVoice.h"
#include "hammond/Types.h"

#include <array>
#include <cstddef>
#include <cstdint>

namespace hammond {

inline constexpr std::size_t kDrawbarBankCount = 2;

enum class DrawbarBank : std::uint8_t { A = 0, B = 1 };

using DrawbarPositions = std::array<std::uint8_t, kDrawbarCount>;
using ManualDrawbarBanks = std::array<DrawbarPositions, kDrawbarBankCount>;
using AllDrawbarBanks = std::array<ManualDrawbarBanks, kManualCount>;

// Musical controls only: no held keys/pedals, contact histories, source phases
// or processing clock. Pedal positions are independent of manual routing.
// Array order is [manual][bank][drawbar], using the enums' storage indices.
struct ControlSnapshot {
    AllDrawbarBanks drawbars{};
    std::array<DrawbarBank, kManualCount> selected_banks{DrawbarBank::B, DrawbarBank::B};
    std::array<bool, kManualCount> route_enabled{true, true};
    double expression{1.0}; // Global normalized linear-gain surrogate, finite 0..1.
    PercussionSettings percussion{}; // Retained controls; no readiness/history.
    PedalDrawbarPositions pedal_drawbars{}; // Mixture 1/2 positions 0..8, initially muted.
    std::array<FixedRegistration, kManualCount> fixed_registrations{
        FixedRegistration::None, FixedRegistration::None};

    [[nodiscard]] bool operator==(const ControlSnapshot&) const noexcept = default;
};

[[nodiscard]] constexpr bool is_valid_drawbar_bank(DrawbarBank bank) noexcept {
    return bank == DrawbarBank::A || bank == DrawbarBank::B;
}

[[nodiscard]] bool is_valid_control_snapshot(const ControlSnapshot& snapshot) noexcept;

// Effective selection from a completely validated copy. Cancel preserves both
// the remembered bank and fixed mode; invalid input preserves destination.
[[nodiscard]] bool control_preset_selection(const ControlSnapshot& snapshot,
                                            Manual manual,
                                            PresetSelection& destination) noexcept;

// Exclusive fixed/A/B selector; not a physical multi-preset latch/loading model.
// Owns fixed-size values only. All operations are allocation-free and require
// same-processing-thread or stopped access; there is no concurrent UI protocol.
class ControlState {
public:
    ControlState() noexcept = default;

    // A true result means valid input, including an accepted no-op. Invalid
    // input leaves all controls unchanged. Drawbar indices/positions are 0..8.
    // Editing never selects or reconnects.
    [[nodiscard]] bool set_bank_drawbar(Manual manual, DrawbarBank bank,
                                        std::size_t index, std::uint8_t position) noexcept;
    [[nodiscard]] bool set_drawbar(Manual manual, std::size_t index,
                                   std::uint8_t position) noexcept;
    // Bank selection clears fixed mode and reconnects the manual. Fixed
    // selection preserves the remembered bank; Cancel only disconnects routing.
    [[nodiscard]] bool select_bank(Manual manual, DrawbarBank bank) noexcept;
    [[nodiscard]] bool select_preset(Manual manual, PresetSelection selection) noexcept;
    [[nodiscard]] bool cancel(Manual manual) noexcept;
    [[nodiscard]] bool set_expression(double expression) noexcept;
    // Stores controls independently of upper-B eligibility and dynamic q.
    [[nodiscard]] bool set_percussion_settings(const PercussionSettings& settings) noexcept;
    // Pedal mixture indices are 0..1 and positions 0..8. Manual selection and
    // Cancel do not change these independent retained settings.
    [[nodiscard]] bool set_pedal_drawbar(std::size_t index,
                                        std::uint8_t position) noexcept;

    [[nodiscard]] ControlSnapshot snapshot() const noexcept { return state_; }
    // Validate the complete candidate before replacing any retained control.
    [[nodiscard]] bool restore(const ControlSnapshot& snapshot) noexcept;
    [[nodiscard]] AllDrawbarBanks drawbar_banks() const noexcept { return state_.drawbars; }
    [[nodiscard]] PedalDrawbarPositions pedal_drawbar_positions() const noexcept {
        return state_.pedal_drawbars;
    }

    // Copied diagnostics. Invalid input leaves the destination unchanged.
    [[nodiscard]] bool bank_drawbar_position(Manual manual, DrawbarBank bank,
                                             std::size_t index,
                                             std::uint8_t& destination) const noexcept;
    // The remembered bank's position, including while fixed or cancelled.
    [[nodiscard]] bool drawbar_position(Manual manual, std::size_t index,
                                       std::uint8_t& destination) const noexcept;
    // Nominal gain position: zero when cancelled, otherwise fixed or bank mode.
    [[nodiscard]] bool active_drawbar_position(Manual manual, std::size_t index,
                                              std::uint8_t& destination) const noexcept;
    [[nodiscard]] bool selected_bank(Manual manual, DrawbarBank& destination) const noexcept;
    [[nodiscard]] bool selected_preset(Manual manual,
                                       PresetSelection& destination) const noexcept;
    [[nodiscard]] bool route_enabled(Manual manual, bool& destination) const noexcept;
    [[nodiscard]] bool pedal_drawbar_position(std::size_t index,
                                             std::uint8_t& destination) const noexcept;
    [[nodiscard]] double expression() const noexcept { return state_.expression; }
    [[nodiscard]] PercussionSettings percussion_settings() const noexcept {
        return state_.percussion;
    }

private:
    ControlSnapshot state_{};
};

} // namespace hammond
