#pragma once

#include "hammond/PedalRouting.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <string_view>

namespace hammond {

using PedalDrawbarPositions = std::array<std::uint8_t, kPedalDrawbarCount>;
using PedalMixtureMatrix =
    std::array<std::array<double, kPedalBusCount>, kPedalDrawbarCount>;

inline constexpr std::size_t kPedalDrawbarPositionCount = 9;
inline constexpr std::string_view kNominalPedalVoiceModelId =
    "nominal-static-pedal-mixture-v1";
inline constexpr std::string_view kNominalPedalGainLawId =
    "linear-pedal-position-v1";
inline constexpr std::array<std::string_view, kPedalDrawbarCount>
    kNominalPedalMixtureLabels{"Pedal Mixture 1", "Pedal Mixture 2"};

// Original, dimensionless engineering fixture, not measured reactor response,
// physical conductance, calibrated voltage or a verified 16ft/8ft pedal voice.
// Bus columns are Brown, Red, Orange, Yellow. Each row sums exactly to one.
inline constexpr PedalMixtureMatrix kNominalPedalMixtureMatrix{{
    {{0.5, 0.25, 0.125, 0.125}},
    {{0.125, 0.5, 0.25, 0.125}},
}};
inline constexpr std::array<double, kPedalDrawbarPositionCount>
    kNominalPedalPositionGains{0.0, 0.125, 0.25, 0.375, 0.5,
                              0.625, 0.75, 0.875, 1.0};
inline constexpr double kNominalPedalBusInputLimit = 50.0;
inline constexpr double kNominalPedalMixtureOutputLimit = 50.0;
inline constexpr double kNominalPedalOutputLimit = 100.0;

// The playable reference explicitly supplies +1 to every independent branch,
// including the five disconnected positions. This is not an implicit default
// of PedalBusKernel, nor a claim about missing physical resistance/loading.
[[nodiscard]] constexpr PedalWeights nominal_pedal_reference_weights() noexcept {
    PedalWeights weights{};
    weights.fill(1.0);
    return weights;
}

[[nodiscard]] constexpr bool is_valid_pedal_drawbar_positions(
    const PedalDrawbarPositions& positions) noexcept {
    for (const auto position : positions) {
        if (position >= kPedalDrawbarPositionCount) return false;
    }
    return true;
}

struct PedalVoiceFrame {
    // Both pre-control mixtures remain available even when controls are muted.
    std::array<double, kPedalDrawbarCount> mixtures{};
    // P, before common Engine expression and output gain.
    double output{0.0};

    [[nodiscard]] bool operator==(const PedalVoiceFrame&) const noexcept = default;
};

// Pure, fixed-model operation; no preparation, sample rate, source clock,
// ownership, envelope or other mutable history. Every bus must be finite and
// within [-50,50], including with both controls muted: otherwise InvalidBuffer.
// Then every retained position must be in 0..8: otherwise InvalidEvent.
// Rejection preserves destination exactly. Success computes both matrix rows
// in Brown/Red/Orange/Yellow order, then P = gain[p0]*z0 + gain[p1]*z1.
// The [0,0] case returns canonical +0 for P, retaining both mixture diagnostics.
// All values are dimensionless source-normalized quantities. No clipping,
// polyphony normalization, source evaluation, allocation or custom coefficients.
// Arbitrary coefficients must not be represented by this model identity.
[[nodiscard]] Status render_nominal_pedal_voice(
    const PedalBusFrame& buses, const PedalDrawbarPositions& positions,
    PedalVoiceFrame& destination) noexcept;

} // namespace hammond
