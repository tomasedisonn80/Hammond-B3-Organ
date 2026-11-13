#pragma once

#include "hammond/ContactBank.h"
#include "hammond/Percussion.h"

namespace hammond {

// Prepared model parameters only. Musical controls and transient contact/q
// histories live elsewhere. The source RuntimeProfile remains independent.
// Default construction preserves the legacy immediate-contact behavior; the
// nominal percussion coefficients do not enable the percussion control.
struct ConsoleModel {
    ContactProfile contacts{make_ideal_contact_profile()};
    PercussionProfile percussion{make_nominal_percussion_profile()};

    [[nodiscard]] bool operator==(const ConsoleModel&) const noexcept = default;
};

[[nodiscard]] inline ConsoleModel make_legacy_console_model() noexcept {
    return {};
}

// Explicit opt-in to synthetic, normalized contact travel. Neither factory
// produces measured instrument data or a complete AO-28 circuit model.
[[nodiscard]] inline ConsoleModel make_nominal_console_model() noexcept {
    return {make_nominal_contact_profile(), make_nominal_percussion_profile()};
}

// Preparation-time validation; the complete model is checked before an engine
// installs it. Algorithm IDs describe families, not arbitrary custom parameter
// sets: retain exact parameter provenance separately when changing a factory.
[[nodiscard]] inline Status validate_console_model(const ConsoleModel& model,
                                                    double sample_rate) noexcept {
    if (!is_supported_sample_rate(sample_rate)) {
        return Status::InvalidSpec;
    }
    if (!is_valid_contact_profile(model.contacts)) {
        return Status::InvalidProfile;
    }
    return validate_percussion_profile(model.percussion, sample_rate);
}

} // namespace hammond
