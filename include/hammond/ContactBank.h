#pragma once

#include "hammond/Types.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <string_view>

namespace hammond {

enum class ContactMode : std::uint8_t { Ideal = 0, LinearTravel = 1 };

inline constexpr std::string_view kIdealContactModelId = "ideal-contacts-v1";
inline constexpr std::string_view kNominalContactModelId = "nominal-linear-travel-v1";
inline constexpr double kMinContactTravelSeconds = 0.0001;
inline constexpr double kMaxContactTravelSeconds = 1.0;

// Normalized motion, not millimetres or measured B-3 geometry. These defaults
// are proposed engineering values: 8 ms full press, 12 ms full release, and
// nine distinct thresholds with 0.08 hysteresis. Every key owns its own copy.
struct ContactKeyProfile {
    std::array<double, kDrawbarCount> on_thresholds{
        0.12, 0.22, 0.32, 0.42, 0.52, 0.62, 0.72, 0.82, 0.92};
    std::array<double, kDrawbarCount> off_thresholds{
        0.04, 0.14, 0.24, 0.34, 0.44, 0.54, 0.64, 0.74, 0.84};
    double press_seconds{0.008};
    double release_seconds{0.012};

    [[nodiscard]] bool operator==(const ContactKeyProfile&) const noexcept = default;
};

using ManualContactProfiles = std::array<ContactKeyProfile, kManualKeyCount>;

struct ContactProfile {
    ContactMode mode{ContactMode::Ideal};
    std::array<ManualContactProfiles, kManualCount> keys{};

    [[nodiscard]] bool operator==(const ContactProfile&) const noexcept = default;
};

[[nodiscard]] constexpr bool is_valid_contact_mode(ContactMode mode) noexcept {
    return mode == ContactMode::Ideal || mode == ContactMode::LinearTravel;
}

// These identify the algorithm family; a custom profile still needs its own
// retained parameter identity. Invalid enum values return an empty string.
[[nodiscard]] constexpr std::string_view contact_model_id(ContactMode mode) noexcept {
    switch (mode) {
    case ContactMode::Ideal: return kIdealContactModelId;
    case ContactMode::LinearTravel: return kNominalContactModelId;
    }
    return {};
}

[[nodiscard]] ContactProfile make_ideal_contact_profile() noexcept;
[[nodiscard]] ContactProfile make_nominal_contact_profile() noexcept;

// All parameters are checked in both modes, including the currently unused
// travel parameters in Ideal. Requires finite 0 <= off < on <= 1 independently
// for all 1,098 contacts and full-travel durations in [0.0001, 1] seconds.
[[nodiscard]] bool is_valid_contact_profile(const ContactProfile& profile) noexcept;

struct ContactKeySnapshot {
    double position{0.0};
    double target{0.0};
    std::array<bool, kDrawbarCount> closed{};

    [[nodiscard]] bool operator==(const ContactKeySnapshot&) const noexcept = default;
};

// Fixed-storage, sample-clock-owned contact state. This module has no source,
// drawbar, preset, percussion, host ownership or audio-buffer dependencies.
// Prepare/queries require stopped or same-processing-thread access. There is
// no concurrent publication protocol and no allocation in any operation.
class ContactBank {
public:
    // Success starts all positions/targets at zero with every contact open.
    // Failure preserves the complete previous bank. The profile is copied.
    [[nodiscard]] Status prepare(const ContactProfile& profile, double sample_rate) noexcept;

    // Physical-key commands are idempotent targets, not counted MIDI owners.
    // Ideal immediately updates all nine contacts/position to 0 or 1.
    // LinearTravel changes only the target; it never advances time here.
    [[nodiscard]] bool set_key_target(Manual manual, std::uint32_t midi_note,
                                      bool down) noexcept;

    // Explicit normalized partial-position extension. LinearTravel accepts
    // finite [0,1]; Ideal accepts only the endpoints 0 and 1. Changing a target
    // preserves the current position and contact hysteresis. Repeated targets
    // do not restart travel. This is not inferred or measured finger motion.
    [[nodiscard]] bool set_position_target(Manual manual, std::uint32_t midi_note,
                                           double target) noexcept;

    // Immediately opens/resets one manual, including interrupted travel.
    // This does not reset shared sources, percussion or any external clock.
    [[nodiscard]] bool panic_manual(Manual manual) noexcept;

    // Call exactly once AFTER rendering each current-frame sample, including
    // silent/disconnected output. Advance positions, then resolve each contact
    // with its own hysteresis. Returns whether any connection changed; position
    // alone may advance while this returns false. Unprepared/Ideal: no change.
    // A zero-frame flush must not call this method.
    [[nodiscard]] bool advance_frame() noexcept;

    // State describes the next sample to render. Every invalid/unprepared
    // checked query returns false and leaves its destination unchanged.
    [[nodiscard]] bool key_snapshot(Manual manual, std::uint32_t midi_note,
                                     ContactKeySnapshot& destination) const noexcept;
    [[nodiscard]] bool position(Manual manual, std::uint32_t midi_note,
                                double& destination) const noexcept;
    [[nodiscard]] bool position_target(Manual manual, std::uint32_t midi_note,
                                       double& destination) const noexcept;
    // True means target > 0, including an explicit partial hold. This flag is
    // distinct from contacts that remain closed while a target-zero key rises.
    [[nodiscard]] bool key_target(Manual manual, std::uint32_t midi_note,
                                  bool& destination) const noexcept;
    [[nodiscard]] bool contact_closed(Manual manual, std::uint32_t midi_note,
                                      std::size_t contact, bool& destination) const noexcept;
    [[nodiscard]] bool any_closed(Manual manual, std::size_t contact,
                                  bool& destination) const noexcept;

    [[nodiscard]] bool prepared() const noexcept { return prepared_; }
    [[nodiscard]] ContactMode mode() const noexcept { return mode_; }

private:
    struct Key {
        ContactKeyProfile profile{};
        ContactKeySnapshot state{};
        double press_step{0.0};
        double release_step{0.0};
        double travel_origin{0.0};
        std::uint32_t travel_frames{0};
    };

    [[nodiscard]] const Key* checked_key(Manual manual,
                                         std::uint32_t midi_note) const noexcept;
    [[nodiscard]] Key* checked_key(Manual manual, std::uint32_t midi_note) noexcept;

    std::array<std::array<Key, kManualKeyCount>, kManualCount> keys_{};
    ContactMode mode_{ContactMode::Ideal};
    bool prepared_{false};
};

} // namespace hammond
