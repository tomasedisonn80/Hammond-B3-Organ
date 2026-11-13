#pragma once

#include "hammond/Types.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>
#include <string_view>

namespace hammond {

inline constexpr std::size_t kPedalCount = 25;
inline constexpr std::size_t kPedalContactCount = 8;
inline constexpr std::size_t kPedalBusCount = 4;
inline constexpr std::size_t kPedalDrawbarCount = 2;
inline constexpr std::size_t kPedalContactPositionCount = kPedalCount * kPedalContactCount;
inline constexpr std::string_view kPedalBusReferenceModelId = "linear-pedal-bus-reference-v1";

// A physical pedal's one-based identity, never a MIDI note, tone source or
// array index. Zero initialization is invalid; all public operations validate.
struct PedalId {
    std::uint8_t value{0};

    [[nodiscard]] bool operator==(const PedalId&) const noexcept = default;
};

enum class PedalBus : std::uint8_t { Brown = 0, Red = 1, Orange = 2, Yellow = 3 };

// Exactly one record per position, in row-major pedal/contact order. Empty tone
// means an unconnected branch; an engaged tone zero is invalid. Repeated tones
// are distinct branches, including when their bus identities differ.
struct PedalRoute {
    PedalId pedal{};
    std::uint8_t contact{0};
    PedalBus bus{PedalBus::Brown};
    std::optional<ToneId> tone{};

    [[nodiscard]] bool operator==(const PedalRoute&) const noexcept = default;
};

using PedalRouteDefinition = std::array<PedalRoute, kPedalContactPositionCount>;
using PedalWeights = std::array<double, kPedalContactPositionCount>;
using PedalSourceFrame = std::array<double, kToneSourceCount>;
using PedalBusFrame = std::array<double, kPedalBusCount>;
using PedalContactStates = std::array<bool, kPedalContactPositionCount>;

struct PedalContactEdit {
    PedalId pedal{};
    std::uint8_t contact{0};
    bool closed{false};

    [[nodiscard]] bool operator==(const PedalContactEdit&) const noexcept = default;
};

[[nodiscard]] constexpr bool is_valid_pedal_id(PedalId pedal) noexcept {
    return pedal.value >= 1 && pedal.value <= kPedalCount;
}

// Checked domain conversions preserve the destination on failure.
[[nodiscard]] constexpr bool make_pedal_id(std::uint32_t value,
                                          PedalId& destination) noexcept {
    if (value < 1 || value > kPedalCount) return false;
    destination = PedalId{static_cast<std::uint8_t>(value)};
    return true;
}

[[nodiscard]] constexpr bool pedal_id_to_index(PedalId pedal,
                                              std::size_t& destination) noexcept {
    if (!is_valid_pedal_id(pedal)) return false;
    destination = static_cast<std::size_t>(pedal.value) - 1;
    return true;
}

[[nodiscard]] constexpr bool pedal_contact_to_index(PedalId pedal,
                                                   std::uint32_t contact,
                                                   std::size_t& destination) noexcept {
    std::size_t pedal_index = 0;
    if (!pedal_id_to_index(pedal, pedal_index) || contact >= kPedalContactCount) {
        return false;
    }
    destination = pedal_index * kPedalContactCount + contact;
    return true;
}

// Metadata belongs to the compiled documentary input below, not to an arbitrary
// caller-authored table passed to prepare(). Views have program lifetime. Hashes
// identify retained input bytes/canonical data, not measured electrical values.
struct PedalRoutingIdentity {
    std::string_view model_id{};
    std::string_view map_id{};
    std::string_view map_raw_sha256{};
    std::string_view map_canonical_sha256{};
    std::string_view factory_comparison_id{};
    std::string_view factory_comparison_raw_sha256{};
    std::string_view review_a_sha256{};
    std::string_view review_b_sha256{};
};

[[nodiscard]] const PedalRouteDefinition& compiled_pedal_routes() noexcept;
[[nodiscard]] PedalRoutingIdentity compiled_pedal_identity() noexcept;

// Fixed-storage linear reference kernel. Four outputs are dimensionless source-
// normalized excitations, not volts or calibrated pedal voices. This object owns
// neither sources nor a clock: the caller supplies the one shared source frame.
// Every operation requires stopped or same-processing-thread access. There is
// no concurrent publication protocol, allocation, I/O, locking or logging here.
class PedalBusKernel {
public:
    // Admit exactly 200 canonical rows. Require pedal 1..25 and contact 0..7 in
    // row-major order, bus == contact/2, and each engaged tone in 1..91. Every
    // supplied weight must be finite and in [-1,1], including unused positions.
    // Generic structural validation does not attest to the factory map; that
    // stronger admission belongs to the offline compiler/independent CSV gates.
    // Success copies the complete definition/weights and opens all contacts.
    // InvalidProfile preserves the complete prior object. No default weights.
    [[nodiscard]] Status prepare(std::span<const PedalRoute> routes,
                                 const PedalWeights& weights) noexcept;

    // NotPrepared precedes size/payload checks; then >200 edits reports
    // TooManyEvents. Every edit is checked before any contact changes; invalid
    // pedal/contact reports InvalidEvent with the complete state preserved.
    // Supplied order is retained, so repeated positions use the final edit.
    // Empty input is an accepted no-op on a prepared kernel. Null branches still
    // retain their contact state. Edits advance no source or elapsed time.
    [[nodiscard]] Status apply_contacts(std::span<const PedalContactEdit> edits) noexcept;

    // NotPrepared precedes input checks. Any of the 91 samples that is nonfinite
    // or outside [-1,1] reports InvalidBuffer, even when unused; destination is
    // unchanged. Success scans 200 branches in canonical order and sums each
    // closed connected branch's weight*source into its bus. At most 50 terms per
    // bus imply absolute output <=50 under the normalization bounds. Rendering
    // changes no kernel state and does not advance the supplied sources.
    [[nodiscard]] Status render_frame(const PedalSourceFrame& sources,
                                      PedalBusFrame& destination) const noexcept;

    [[nodiscard]] bool prepared() const noexcept { return prepared_; }
    [[nodiscard]] std::size_t closed_contact_count() const noexcept;
    [[nodiscard]] PedalContactStates contacts_snapshot() const noexcept { return contacts_; }
    // Invalid or unprepared queries leave the destination unchanged.
    [[nodiscard]] bool contact_closed(PedalId pedal, std::uint32_t contact,
                                      bool& destination) const noexcept;

    [[nodiscard]] bool operator==(const PedalBusKernel&) const noexcept = default;

private:
    PedalRouteDefinition routes_{};
    PedalWeights weights_{};
    PedalContactStates contacts_{};
    bool prepared_{false};
};

} // namespace hammond
