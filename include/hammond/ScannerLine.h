#pragma once

#include "hammond/Types.h"

#include <array>
#include <complex>
#include <cstddef>
#include <cstdint>
#include <string_view>

namespace hammond {

inline constexpr std::size_t kScannerSectionCount = 18;
inline constexpr std::size_t kScannerTapCount = 19;
inline constexpr std::size_t kScannerStateCoordinateCount = 36;
inline constexpr std::string_view kScannerLineModelId = "atlas-late-b3-nominal-line-v1";
inline constexpr std::string_view kScannerLineRealizationId =
    "scaled-physical-trapezoidal-scanner-line-v1";
// sqrt(0.5 H / 4e-9 F), rounded to binary64. Scaled current is Zref * amps.
inline constexpr double kScannerCurrentScaleOhms = 11180.339887498949;
// Computational admission limits, not measured operating limits or clipping.
inline constexpr double kScannerMaxInputVolts = 64.0;
inline constexpr double kScannerMaxCapacitorVolts = 65536.0;
inline constexpr double kScannerMaxInductorAmps = 2.0;
inline constexpr double kScannerMaxEnergyJoules = 1.0;
inline constexpr double kScannerMaxOutputVolts = 131072.0;
inline constexpr double kScannerMaxInputCurrentAmps = 4.0;

enum class ScannerReturnMode : std::uint8_t { Vibrato = 0, Chorus = 1 };

[[nodiscard]] constexpr bool is_valid_scanner_return_mode(ScannerReturnMode mode) noexcept {
    return mode == ScannerReturnMode::Vibrato || mode == ScannerReturnMode::Chorus;
}

// Internal research rates. This does not change the Engine/native host-rate API.
[[nodiscard]] constexpr bool is_supported_scanner_sample_rate(double rate) noexcept {
    for (const double host : std::array<double, 3>{44100.0, 48000.0, 96000.0}) {
        for (const double factor : std::array<double, 5>{1.0, 2.0, 4.0, 8.0, 16.0}) {
            if (rate == host * factor) return true;
        }
    }
    return false;
}

struct ScannerLineState {
    // x[k] = V(p(k+1))-V(r); i[k] flows p(k)->p(k+1).
    std::array<double, kScannerSectionCount> capacitor_volts{};
    std::array<double, kScannerSectionCount> inductor_amps{};
    double previous_input_volts{0.0};
    // Number of completed intervals. UINT64_MAX is a restorable checkpoint,
    // but a subsequent process_frame rejects with TimelineOverflow.
    std::uint64_t frames{0};

    [[nodiscard]] bool operator==(const ScannerLineState&) const noexcept = default;
};

struct ScannerLineFrame {
    std::array<double, kScannerTapCount> taps_volts{};
    double return_volts{0.0};
    double input_current_amps{0.0}; // positive from ideal source into the line
    double energy_joules{0.0};
    // Completed-interval count of the observed endpoint, matching state().frames.
    // The cold checkpoint observes frame 0; first process_frame produces frame 1.
    std::uint64_t frame{0};

    [[nodiscard]] bool operator==(const ScannerLineFrame&) const noexcept = default;
};

struct ScannerLineResponse {
    // Transfers for a unit-volt sinusoidal input at the discrete endpoint.
    std::array<std::complex<double>, kScannerTapCount> taps{};
    std::complex<double> return_gain{};
    std::complex<double> input_admittance{}; // ampere per volt
    double normalized_residual{0.0};
    // Infinity condition number of the row-scaled recurrence response matrix.
    double condition_inf{0.0};

    [[nodiscard]] bool operator==(const ScannerLineResponse&) const noexcept = default;
};

// One separately identified, unloaded nominal LC line. No rotor, Engine route,
// musical controls, resampler or hardware-calibrated voltage mapping is implied.
// Externally serialize access; preparation/response are stopped/offline work.
class ScannerLine {
public:
    // On success prepare resets to the zero checkpoint. Failed preparation
    // preserves the previous operators, rate and physical state exactly.
    [[nodiscard]] Status prepare(double sample_rate) noexcept;
    // Rebuild both operators while preserving the complete physical checkpoint.
    [[nodiscard]] Status reconfigure_sample_rate(double sample_rate) noexcept;
    [[nodiscard]] bool prepared() const noexcept { return prepared_; }
    [[nodiscard]] double sample_rate() const noexcept { return sample_rate_; }
    [[nodiscard]] double preparation_residual() const noexcept { return preparation_residual_; }
    [[nodiscard]] static std::string_view authoring_sha256() noexcept;

    [[nodiscard]] ScannerLineState state() const noexcept { return state_; }
    // Invalid arguments: mode -> InvalidEvent, input -> InvalidBuffer,
    // restore checkpoint -> InvalidProfile, rate/frequency -> InvalidSpec.
    // NotPrepared takes precedence for methods requiring preparation.
    // Replay checkpoint only, not ordinary musical/preset state. Bounds include
    // total stored energy <= 1 J. Any rejection leaves the previous state intact.
    [[nodiscard]] Status restore_state(const ScannerLineState& state) noexcept;
    // Read the existing endpoint using previous_input_volts, without advancing
    // time or changing state. A changed return mode reconstructs algebraic nodes.
    [[nodiscard]] Status observe(ScannerReturnMode mode, ScannerLineFrame& destination) const noexcept;
    // One trapezoidal interval from (state, previous input) to current input.
    // Taps are reconstructed after the step. Invalid input/mode, overflow or
    // numerical admission failure preserves state and destination. No allocation,
    // factorization, locks, I/O or unbounded loops occur here.
    [[nodiscard]] Status process_frame(double input_volts, ScannerReturnMode mode,
                                       ScannerLineFrame& destination) noexcept;
    // Offline response of the actual prepared recurrence, not analog A alone.
    // Accepts 0 <= frequency_hz < sample_rate/2. Does not change physical state.
    // Returns finite results and a solve residual/condition; callers grade the
    // declared numerical contract, including same-Hz warping separately.
    [[nodiscard]] Status response(double frequency_hz, ScannerReturnMode mode,
                                 ScannerLineResponse& destination) const noexcept;

private:
    using Vector = std::array<double, kScannerStateCoordinateCount>;
    using Matrix = std::array<Vector, kScannerStateCoordinateCount>;
    struct Operator {
        Matrix transition{};
        Vector forcing{};
    };
    std::array<Operator, 2> operators_{};
    ScannerLineState state_{};
    double sample_rate_{0.0};
    double preparation_residual_{0.0};
    bool prepared_{false};
};

} // namespace hammond
