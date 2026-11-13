#include "hammond/ControlState.h"

#include <cmath>

namespace hammond {
namespace {

[[nodiscard]] bool valid_expression(double expression) noexcept {
    return std::isfinite(expression) && expression >= 0.0 && expression <= 1.0;
}

} // namespace

bool is_valid_control_snapshot(const ControlSnapshot& snapshot) noexcept {
    if (!valid_expression(snapshot.expression) ||
        !is_valid_percussion_settings(snapshot.percussion)) {
        return false;
    }
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        if (!is_valid_drawbar_bank(snapshot.selected_banks[manual])) {
            return false;
        }
        for (const auto& bank : snapshot.drawbars[manual]) {
            for (const auto position : bank) {
                if (position >= kDrawbarPositionCount) {
                    return false;
                }
            }
        }
    }
    return true;
}

bool ControlState::set_bank_drawbar(Manual manual, DrawbarBank bank,
                                    std::size_t index, std::uint8_t position) noexcept {
    if (!is_valid_manual(manual) || !is_valid_drawbar_bank(bank) ||
        index >= kDrawbarCount || position >= kDrawbarPositionCount) {
        return false;
    }
    state_.drawbars[static_cast<std::size_t>(manual)][static_cast<std::size_t>(bank)][index] =
        position;
    return true;
}

bool ControlState::set_drawbar(Manual manual, std::size_t index,
                               std::uint8_t position) noexcept {
    if (!is_valid_manual(manual)) {
        return false;
    }
    return set_bank_drawbar(manual, state_.selected_banks[static_cast<std::size_t>(manual)],
                            index, position);
}

bool ControlState::select_bank(Manual manual, DrawbarBank bank) noexcept {
    if (!is_valid_manual(manual) || !is_valid_drawbar_bank(bank)) {
        return false;
    }
    const auto manual_index = static_cast<std::size_t>(manual);
    state_.selected_banks[manual_index] = bank;
    state_.route_enabled[manual_index] = true;
    return true;
}

bool ControlState::cancel(Manual manual) noexcept {
    if (!is_valid_manual(manual)) {
        return false;
    }
    state_.route_enabled[static_cast<std::size_t>(manual)] = false;
    return true;
}

bool ControlState::set_expression(double expression) noexcept {
    if (!valid_expression(expression)) {
        return false;
    }
    state_.expression = expression;
    return true;
}

bool ControlState::set_percussion_settings(const PercussionSettings& settings) noexcept {
    if (!is_valid_percussion_settings(settings)) {
        return false;
    }
    state_.percussion = settings;
    return true;
}

bool ControlState::restore(const ControlSnapshot& snapshot) noexcept {
    if (!is_valid_control_snapshot(snapshot)) {
        return false;
    }
    state_ = snapshot;
    return true;
}

bool ControlState::bank_drawbar_position(Manual manual, DrawbarBank bank,
                                         std::size_t index,
                                         std::uint8_t& destination) const noexcept {
    if (!is_valid_manual(manual) || !is_valid_drawbar_bank(bank) || index >= kDrawbarCount) {
        return false;
    }
    destination = state_.drawbars[static_cast<std::size_t>(manual)]
                                [static_cast<std::size_t>(bank)][index];
    return true;
}

bool ControlState::drawbar_position(Manual manual, std::size_t index,
                                   std::uint8_t& destination) const noexcept {
    if (!is_valid_manual(manual)) {
        return false;
    }
    return bank_drawbar_position(manual,
                                 state_.selected_banks[static_cast<std::size_t>(manual)],
                                 index, destination);
}

bool ControlState::active_drawbar_position(Manual manual, std::size_t index,
                                          std::uint8_t& destination) const noexcept {
    if (!is_valid_manual(manual) || index >= kDrawbarCount) {
        return false;
    }
    const auto manual_index = static_cast<std::size_t>(manual);
    const auto bank_index = static_cast<std::size_t>(state_.selected_banks[manual_index]);
    destination = state_.route_enabled[manual_index]
                      ? state_.drawbars[manual_index][bank_index][index]
                      : std::uint8_t{0};
    return true;
}

bool ControlState::selected_bank(Manual manual, DrawbarBank& destination) const noexcept {
    if (!is_valid_manual(manual)) {
        return false;
    }
    destination = state_.selected_banks[static_cast<std::size_t>(manual)];
    return true;
}

bool ControlState::route_enabled(Manual manual, bool& destination) const noexcept {
    if (!is_valid_manual(manual)) {
        return false;
    }
    destination = state_.route_enabled[static_cast<std::size_t>(manual)];
    return true;
}

} // namespace hammond
