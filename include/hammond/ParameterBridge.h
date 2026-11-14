#pragma once

#include "hammond/Types.h"

#include <cstddef>
#include <cstdint>
#include <span>
#include <string_view>

namespace hammond {

inline constexpr std::size_t kParameterCount = 47;
inline constexpr std::uint32_t kParameterRegistrySchemaVersion = 4;
inline constexpr std::string_view kParameterRegistryModel =
    "exclusive-fixed-percussion-pedal-console-v4";

// Immutable compiled descriptors for the proposed internal registry. Text views
// refer only to program-lifetime literals; no JSON or host SDK is needed here.
// Minimum is always zero. step_count==0 denotes continuous expression; all other
// descriptors have exactly step_count+1 discrete values from zero to maximum.
struct ParameterDescriptor {
    std::uint32_t id{0};
    std::string_view path{};
    std::string_view kind{};
    std::string_view unit{};
    double maximum{0.0};
    double default_plain{0.0};
    std::uint8_t step_count{0};
    EventType event_type{EventType::BankDrawbar};
    Manual manual{Manual::Upper};
    std::uint8_t index{0};

    [[nodiscard]] bool operator==(const ParameterDescriptor&) const noexcept = default;
};

// Sorted by numeric ID, but array position is not a parameter identity.
[[nodiscard]] std::span<const ParameterDescriptor, kParameterCount>
parameter_descriptors() noexcept;

// Unknown ID rejects and leaves the destination unchanged. Holes in ID ranges
// are not valid controls. Preset selectors include Cancel as value 0; no
// AllNotesOff, per-key control or host program identity is invented.
[[nodiscard]] bool parameter_descriptor(std::uint32_t id,
                                       ParameterDescriptor& destination) noexcept;

// Convert one finite normalized scalar in [0,1] into a fixed-identity event.
// Discrete half thresholds choose the higher value, using exact comparisons so
// adjacent binary64 inputs and the caller's rounding mode cannot shift a step.
// The new preset selectors compare against frozen nearest-binary64 midpoints.
// Expression is passed through, including signed zero. Offset is copied exactly;
// the caller/Engine owns block bounds and stable event ordering. No state, clock,
// trajectory, gesture, smoothing or native automation curve is changed here.
// Every failure leaves the complete destination Event unchanged.
[[nodiscard]] bool normalized_to_event(std::uint32_t id, double normalized,
                                       std::uint32_t offset, Event& destination) noexcept;

// Validate a plain scalar and return its canonical normalized representation.
// Discrete values must be exact integers. Preset selectors use frozen canonical
// binary64 values and canonicalize plain -0 to +0. All older signed-zero behavior
// is retained. Failure leaves destination unchanged; rounding mode is untouched.
[[nodiscard]] bool plain_to_normalized(std::uint32_t id, double plain,
                                       double& destination) noexcept;

} // namespace hammond
