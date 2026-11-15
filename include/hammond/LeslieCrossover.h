#pragma once

#include "hammond/Types.h"

#include <array>
#include <complex>
#include <cstddef>
#include <cstdint>
#include <span>
#include <string_view>

namespace hammond {

inline constexpr std::string_view kLeslieCrossoverModelId =
    "atlas-leslie-122-ideal-crossover-v1";
inline constexpr std::string_view kLeslieCrossoverRealizationId =
    "physical-trapezoidal-leslie-crossover-v1";
inline constexpr std::size_t kLeslieCrossoverBlockCapacity = 4096;

// These are explicit resistive experiments, not measured loudspeaker loads.
// The documentary fixture uses 16 ohm at each load. Admitted values are [1,1024].
struct LeslieCrossoverLoads {
    double treble_ohms{16.0};
    double bass_ohms{16.0};

    [[nodiscard]] bool operator==(const LeslieCrossoverLoads&) const noexcept = default;
};

struct LeslieCrossoverState {
    std::array<double, 2> capacitor_volts{}; // H-B, W-B
    std::array<double, 2> inductor_amps{};   // A->H through L2, A->W through L3
    double previous_input_volts{0.0};
    // Completed trapezoidal intervals. UINT64_MAX is a valid restored endpoint,
    // but another nonempty processing call rejects with TimelineOverflow.
    std::uint64_t frames{0};

    [[nodiscard]] bool operator==(const LeslieCrossoverState&) const noexcept = default;
};

struct LeslieCrossoverFrame {
    double treble_volts{0.0}, bass_volts{0.0};
    double treble_current_amps{0.0}, bass_current_amps{0.0};
    double input_current_amps{0.0}, energy_joules{0.0};
    std::uint64_t frame{0};

    [[nodiscard]] bool operator==(const LeslieCrossoverFrame&) const noexcept = default;
};

struct LeslieCrossoverResponse {
    std::complex<double> treble_gain{}, bass_gain{}, input_admittance{};
    double normalized_residual{0.0};

    [[nodiscard]] bool operator==(const LeslieCrossoverResponse&) const noexcept = default;
};

// Independent M6 electrical research model; no Engine connection or acoustic
// response is implied. The fixed L/C topology and its evidence are specified in
// docs/LESLIE_CROSSOVER_CONTRACT.md and data/crossover/leslie-122-ideal-v1.json.
// In particular the treble load is floating across A-H, not grounded at H-B.
//
// Externally serialize access. Preparation, rate changes, checkpoint restore and
// response are stopped/offline operations. Processing owns only fixed storage,
// does no factorization/allocation/I/O, and leaves state/output intact on failure.
class LeslieCrossover {
public:
    // Rates: 44100, 48000, 96000, 192000 Hz. Success starts at zero physical
    // state/input and frame 0. Failure preserves the previous object completely.
    [[nodiscard]] Status prepare(double sample_rate, LeslieCrossoverLoads loads = {}) noexcept;
    // Rebuild operators while preserving all physical coordinates, prior input
    // and completed-frame count exactly. Does not advance an artificial sample.
    [[nodiscard]] Status reconfigure_sample_rate(double sample_rate) noexcept;

    [[nodiscard]] bool prepared() const noexcept { return prepared_; }
    [[nodiscard]] double sample_rate() const noexcept { return sample_rate_; }
    [[nodiscard]] LeslieCrossoverLoads loads() const noexcept { return loads_; }
    [[nodiscard]] double preparation_residual() const noexcept { return preparation_residual_; }
    [[nodiscard]] LeslieCrossoverState state() const noexcept { return state_; }

    // This is a numerical checkpoint, not a musical preset. Finite computational
    // limits are 64 V prior input, 65536 V per capacitor, 256 A per inductor and
    // 1e6 J stored energy. They are not physical ratings or clipping levels.
    [[nodiscard]] Status restore_state(const LeslieCrossoverState&) noexcept;
    // Observe the existing right endpoint using its previous_input_volts.
    [[nodiscard]] Status observe(LeslieCrossoverFrame& destination) const noexcept;
    // One interval from the old endpoint to input_volts. The first success
    // reports frame 1. Preparation/overflow precede input/numerical admission.
    [[nodiscard]] Status process_frame(double input_volts,
                                       LeslieCrossoverFrame& destination) noexcept;
    // Equal, nonoverlapping spans, at most 4096 frames. The entire block is one
    // transaction, including late numeric rejection. Equal empty spans are a
    // no-op. Caller storage must remain valid/immutable for both bounded passes.
    // Precedence: unprepared, counts, capacity, clock, alias, numerical admission.
    [[nodiscard]] Status process(std::span<const double> input_volts,
                                 std::span<LeslieCrossoverFrame> destination) noexcept;
    // Unit-volt endpoint sinusoid of the actual prepared recurrence, including
    // exact DC limits. Admits finite 0 <= f < rate/2 and never changes history.
    // Its warped analog agreement is separate from same-Hz audible accuracy.
    [[nodiscard]] Status response(double frequency_hz,
                                  LeslieCrossoverResponse& destination) const noexcept;

private:
    using Vector = std::array<double, 4>;
    using Matrix = std::array<Vector, 4>;
    Matrix transition_{};
    Vector forcing_{};
    LeslieCrossoverState state_{};
    LeslieCrossoverLoads loads_{};
    double sample_rate_{0.0};
    double preparation_residual_{0.0};
    bool prepared_{false};
};

} // namespace hammond
