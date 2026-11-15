#pragma once

#include "hammond/ScannerLine.h"

#include <array>
#include <cstdint>
#include <string_view>

namespace hammond {

inline constexpr std::string_view kScannerLineFohRealizationId =
    "scaled-physical-exponential-foh-scanner-line-v1";
inline constexpr std::string_view kScannerLineFohPreparationId =
    "scanner-augmented38-pade13-scaling-squaring-v1";

// Diagnostics of the row-scaled 38-coordinate Pade denominator solve, before
// squaring. Neither the residual nor the condition is an exponential error bound.
struct ScannerLineFohPreparation {
    double augmented_norm_one{0.0};
    std::uint32_t squarings{0};
    double normalized_residual{0.0};
    double condition_inf{0.0};
};

// Independent unloaded nominal LC line with a linear input between supplied
// internal-rate endpoints. The 36 physical checkpoint coordinates retain the
// existing volts/amps convention; the two augmented preparation coordinates are
// temporary. No rotor, resampler, Engine route or calibrated voltage is implied.
// Externally serialize access. Preparation and response are stopped operations.
class ScannerLineFoh {
public:
    // Prepare both return modes transactionally, then reset to the cold endpoint.
    // Failure preserves all previous operators, diagnostics and physical history.
    [[nodiscard]] Status prepare(double sample_rate) noexcept;
    [[nodiscard]] Status reconfigure_sample_rate(double sample_rate) noexcept;
    [[nodiscard]] bool prepared() const noexcept { return prepared_; }
    [[nodiscard]] double sample_rate() const noexcept { return sample_rate_; }
    [[nodiscard]] double preparation_residual() const noexcept { return preparation_residual_; }
    // Ordered [Vibrato, Chorus]. All fields are zero before preparation.
    [[nodiscard]] std::array<ScannerLineFohPreparation, 2>
        preparation_diagnostics() const noexcept { return diagnostics_; }
    [[nodiscard]] static std::string_view authoring_sha256() noexcept;

    [[nodiscard]] ScannerLineState state() const noexcept { return state_; }
    // Restores only the physical checkpoint, including input history and count.
    // UINT64_MAX remains restorable and observable, but cannot be advanced.
    [[nodiscard]] Status restore_state(const ScannerLineState& state) noexcept;
    [[nodiscard]] Status observe(ScannerReturnMode mode,
                                 ScannerLineFrame& destination) const noexcept;
    // One interval from the stored previous endpoint to input_volts. The mode
    // applies to the complete interval. Reconstruct the new endpoint, then commit
    // state and destination together. No allocation, factorization or I/O occurs.
    // Cold history is at -1/fs; the first call supplies u[0] and returns frame 1.
    [[nodiscard]] Status process_frame(double input_volts, ScannerReturnMode mode,
                                       ScannerLineFrame& destination) noexcept;
    // Response of the actual prepared recurrence at 0 <= frequency_hz < fs/2.
    // A finite conditioning-limited estimate remains diagnostic evidence; callers
    // must independently grade forward accuracy and same-physical-Hz agreement.
    [[nodiscard]] Status response(double frequency_hz, ScannerReturnMode mode,
                                  ScannerLineResponse& destination) const noexcept;

private:
    using Vector = std::array<double, kScannerStateCoordinateCount>;
    using Matrix = std::array<Vector, kScannerStateCoordinateCount>;
    struct Operator {
        Matrix transition{};
        Vector previous_forcing{};
        Vector current_forcing{};
    };
    // Exactly 2 * (36*36 + 2*36) persistent binary64 operator coefficients.
    std::array<Operator, 2> operators_{};
    ScannerLineState state_{};
    std::array<ScannerLineFohPreparation, 2> diagnostics_{};
    double sample_rate_{0.0};
    double preparation_residual_{0.0};
    bool prepared_{false};
};

} // namespace hammond
