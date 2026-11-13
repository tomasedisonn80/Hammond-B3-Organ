#include "hammond/ScannerLine.h"
#include "hammond/generated/ScannerLineData.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <complex>
#include <limits>
#include <numbers>
#include <type_traits>
#include <utility>

namespace hammond {
namespace {

constexpr std::size_t n = kScannerStateCoordinateCount;
using RealVector = std::array<double, n>;
using RealMatrix = std::array<RealVector, n>;
using Complex = std::complex<double>;
using ComplexVector = std::array<Complex, n>;
using ComplexMatrix = std::array<ComplexVector, n>;
static_assert(scanner_generated::kModelId == kScannerLineModelId);
static_assert(scanner_generated::kInductancesH.size() == kScannerSectionCount);
static_assert(scanner_generated::kCapacitancesF.size() == kScannerSectionCount);

// Physical current i is represented by z=Zref*i only inside the recurrence.
// The public stored checkpoint remains volts/amps and is never rate dependent.
struct ReturnCoefficients {
    double input_gain;
    double current_ohms;
};

[[nodiscard]] ReturnCoefficients return_coefficients(ScannerReturnMode mode) noexcept {
    if (mode == ScannerReturnMode::Vibrato) return {0.0, 0.0};
    const double divider = scanner_generated::kDividerUpperOhms[0]
                         + scanner_generated::kDividerLowerOhms[0];
    const double total = scanner_generated::kReturnOhms + divider;
    return {scanner_generated::kReturnOhms / total,
            scanner_generated::kReturnOhms * divider / total};
}

template <typename Scalar>
[[nodiscard]] bool finite_scalar(const Scalar& value) noexcept {
    if constexpr (std::is_same_v<Scalar, double>) {
        return std::isfinite(value);
    } else {
        return std::isfinite(value.real()) && std::isfinite(value.imag());
    }
}

// Fixed-size, row-scaled partial-pivot LU. Only stopped preparation/diagnostics
// use it. No factorization or division by a matrix pivot occurs in process_frame.
template <typename Scalar>
struct Factorization {
    using Vector = std::array<Scalar, n>;
    using Matrix = std::array<Vector, n>;
    Matrix lu{};
    RealVector scales{};
    std::array<std::size_t, n> pivots{};
    double scaled_matrix_norm{0.0};

    [[nodiscard]] bool factor(const Matrix& matrix) noexcept {
        for (std::size_t row = 0; row < n; ++row) {
            double scale = 0.0;
            for (const auto& value : matrix[row]) {
                if (!finite_scalar(value)) return false;
                scale = std::max(scale, std::abs(value));
            }
            if (!std::isfinite(scale) || scale <= 0.0) return false;
            scales[row] = scale;
            double row_norm = 0.0;
            for (std::size_t column = 0; column < n; ++column) {
                lu[row][column] = matrix[row][column] / scale;
                row_norm += std::abs(lu[row][column]);
            }
            scaled_matrix_norm = std::max(scaled_matrix_norm, row_norm);
        }
        for (std::size_t column = 0; column < n; ++column) {
            std::size_t pivot = column;
            double magnitude = std::abs(lu[column][column]);
            for (std::size_t row = column + 1; row < n; ++row) {
                const double candidate = std::abs(lu[row][column]);
                if (candidate > magnitude) {
                    pivot = row;
                    magnitude = candidate;
                }
            }
            if (!std::isfinite(magnitude)
                || magnitude <= 8.0 * std::numeric_limits<double>::epsilon()) return false;
            pivots[column] = pivot;
            if (pivot != column) std::swap(lu[pivot], lu[column]);
            for (std::size_t row = column + 1; row < n; ++row) {
                lu[row][column] /= lu[column][column];
                if (!finite_scalar(lu[row][column])) return false;
                for (std::size_t other = column + 1; other < n; ++other) {
                    lu[row][other] -= lu[row][column] * lu[column][other];
                }
            }
        }
        return std::isfinite(scaled_matrix_norm);
    }

    [[nodiscard]] bool solve(const Vector& rhs, Vector& destination) const noexcept {
        Vector value{};
        for (std::size_t row = 0; row < n; ++row) value[row] = rhs[row] / scales[row];
        // Apply the complete final permutation before triangular substitution;
        // later pivot swaps also moved the previously computed lower columns.
        for (std::size_t row = 0; row < n; ++row) {
            if (pivots[row] != row) std::swap(value[row], value[pivots[row]]);
        }
        for (std::size_t row = 0; row < n; ++row) {
            for (std::size_t column = 0; column < row; ++column) {
                value[row] -= lu[row][column] * value[column];
            }
        }
        for (std::size_t reverse = n; reverse > 0; --reverse) {
            const std::size_t row = reverse - 1;
            for (std::size_t column = row + 1; column < n; ++column) {
                value[row] -= lu[row][column] * value[column];
            }
            value[row] /= lu[row][row];
            if (!finite_scalar(value[row])) return false;
        }
        destination = value;
        return true;
    }

    [[nodiscard]] bool condition(double& destination) const noexcept {
        RealVector inverse_row_sums{};
        for (std::size_t column = 0; column < n; ++column) {
            Vector rhs{}, solution{};
            // solve scales its RHS, so this is a unit RHS for the scaled matrix.
            rhs[column] = scales[column];
            if (!solve(rhs, solution)) return false;
            for (std::size_t row = 0; row < n; ++row) {
                inverse_row_sums[row] += std::abs(solution[row]);
            }
        }
        const double inverse_norm = *std::max_element(inverse_row_sums.begin(), inverse_row_sums.end());
        const double result = scaled_matrix_norm * inverse_norm;
        if (!std::isfinite(result) || result <= 0.0) return false;
        destination = result;
        return true;
    }
};

template <typename Scalar>
[[nodiscard]] double residual(
    const std::array<std::array<Scalar, n>, n>& matrix,
    const std::array<Scalar, n>& rhs, const std::array<Scalar, n>& solution,
    const RealVector& scales) noexcept {
    double matrix_norm = 0.0, rhs_norm = 0.0, state_norm = 0.0, residual_norm = 0.0;
    for (std::size_t row = 0; row < n; ++row) {
        Scalar difference = -rhs[row] / scales[row];
        double row_norm = 0.0;
        for (std::size_t column = 0; column < n; ++column) {
            const Scalar coefficient = matrix[row][column] / scales[row];
            difference += coefficient * solution[column];
            row_norm += std::abs(coefficient);
        }
        residual_norm = std::max(residual_norm, std::abs(difference));
        matrix_norm = std::max(matrix_norm, row_norm);
        rhs_norm = std::max(rhs_norm, std::abs(rhs[row] / scales[row]));
        state_norm = std::max(state_norm, std::abs(solution[row]));
    }
    const double denominator = matrix_norm * state_norm + rhs_norm;
    if (denominator == 0.0) {
        return residual_norm == 0.0 ? 0.0 : std::numeric_limits<double>::infinity();
    }
    return residual_norm / denominator;
}

[[nodiscard]] bool prepare_operator(double rate, ScannerReturnMode mode,
                                    RealMatrix& transition, RealVector& forcing,
                                    double& maximum_residual) noexcept {
    RealMatrix derivative{};
    RealVector drive{};
    for (std::size_t section = 0; section < kScannerSectionCount; ++section) {
        const double capacitance = scanner_generated::kCapacitancesF[section];
        const double inductance = scanner_generated::kInductancesH[section];
        if (!std::isfinite(capacitance) || capacitance <= 0.0
            || !std::isfinite(inductance) || inductance <= 0.0) return false;
        const double current_coefficient = 1.0 / (capacitance * kScannerCurrentScaleOhms);
        derivative[section][kScannerSectionCount + section] = current_coefficient;
        if (section + 1 < kScannerSectionCount) {
            derivative[section][kScannerSectionCount + section + 1] = -current_coefficient;
        }
        // Divider k+1 attaches to pk, before L(k+1); the first divider is
        // instead part of the input/common-return algebraic boundary below.
        if (section < 5) {
            const double resistance = scanner_generated::kDividerUpperOhms[section + 1]
                                    + scanner_generated::kDividerLowerOhms[section + 1];
            derivative[section][section] = -1.0 / (capacitance * resistance);
        } else if (section + 1 == kScannerSectionCount) {
            derivative[section][section] = -1.0 / (capacitance * scanner_generated::kTerminationOhms);
        }
        const std::size_t current_row = kScannerSectionCount + section;
        const double voltage_coefficient = kScannerCurrentScaleOhms / inductance;
        derivative[current_row][section] = -voltage_coefficient;
        if (section != 0) derivative[current_row][section - 1] = voltage_coefficient;
    }
    const ReturnCoefficients boundary = return_coefficients(mode);
    derivative[kScannerSectionCount][kScannerSectionCount] =
        -boundary.current_ohms / scanner_generated::kInductancesH[0];
    drive[kScannerSectionCount] = kScannerCurrentScaleOhms
                               * (1.0 - boundary.input_gain)
                               / scanner_generated::kInductancesH[0];

    const double half_step = 0.5 / rate;
    RealMatrix left{}, right{};
    for (std::size_t row = 0; row < n; ++row) {
        for (std::size_t column = 0; column < n; ++column) {
            const double identity = row == column ? 1.0 : 0.0;
            left[row][column] = identity - half_step * derivative[row][column];
            right[row][column] = identity + half_step * derivative[row][column];
        }
    }
    Factorization<double> factor;
    if (!factor.factor(left)) return false;
    for (std::size_t column = 0; column < n; ++column) {
        RealVector rhs{}, solution{};
        for (std::size_t row = 0; row < n; ++row) rhs[row] = right[row][column];
        if (!factor.solve(rhs, solution)) return false;
        const double error = residual(left, rhs, solution, factor.scales);
        if (!std::isfinite(error) || error > 1.0e-9) return false;
        maximum_residual = std::max(maximum_residual, error);
        for (std::size_t row = 0; row < n; ++row) transition[row][column] = solution[row];
    }
    RealVector rhs{};
    for (std::size_t row = 0; row < n; ++row) rhs[row] = half_step * drive[row];
    if (!factor.solve(rhs, forcing)) return false;
    const double error = residual(left, rhs, forcing, factor.scales);
    if (!std::isfinite(error) || error > 1.0e-9) return false;
    maximum_residual = std::max(maximum_residual, error);
    return true;
}

[[nodiscard]] double energy(const ScannerLineState& state) noexcept {
    double result = 0.0;
    for (std::size_t section = 0; section < kScannerSectionCount; ++section) {
        result += 0.5 * scanner_generated::kCapacitancesF[section]
                * state.capacitor_volts[section] * state.capacitor_volts[section];
        result += 0.5 * scanner_generated::kInductancesH[section]
                * state.inductor_amps[section] * state.inductor_amps[section];
    }
    return result;
}

[[nodiscard]] bool valid_input(double value) noexcept {
    return std::isfinite(value) && std::abs(value) <= kScannerMaxInputVolts;
}

[[nodiscard]] bool valid_state(const ScannerLineState& state) noexcept {
    if (!valid_input(state.previous_input_volts)) return false;
    for (std::size_t section = 0; section < kScannerSectionCount; ++section) {
        if (!std::isfinite(state.capacitor_volts[section])
            || std::abs(state.capacitor_volts[section]) > kScannerMaxCapacitorVolts
            || !std::isfinite(state.inductor_amps[section])
            || std::abs(state.inductor_amps[section]) > kScannerMaxInductorAmps) return false;
    }
    const double stored = energy(state);
    return std::isfinite(stored) && stored >= 0.0 && stored <= kScannerMaxEnergyJoules;
}

template <typename Scalar>
struct Observation {
    std::array<Scalar, kScannerTapCount> taps{};
    Scalar return_value{};
    Scalar input_current{};
};

template <typename Scalar>
[[nodiscard]] Observation<Scalar> reconstruct(
    const std::array<Scalar, kScannerSectionCount>& capacitor_volts,
    const std::array<Scalar, kScannerSectionCount>& inductor_amps,
    Scalar input, ScannerReturnMode mode) noexcept {
    Observation<Scalar> result;
    const ReturnCoefficients boundary = return_coefficients(mode);
    result.return_value = boundary.input_gain * input + boundary.current_ohms * inductor_amps[0];
    for (std::size_t tap = 0; tap < 6; ++tap) {
        const Scalar local = tap == 0 ? input - result.return_value : capacitor_volts[tap - 1];
        const double divider = scanner_generated::kDividerUpperOhms[tap]
                             + scanner_generated::kDividerLowerOhms[tap];
        result.taps[tap] = result.return_value
                        + local * (scanner_generated::kDividerLowerOhms[tap] / divider);
    }
    for (std::size_t tap = 6; tap < kScannerTapCount; ++tap) {
        result.taps[tap] = result.return_value + capacitor_volts[tap - 1];
    }
    const double first_divider = scanner_generated::kDividerUpperOhms[0]
                               + scanner_generated::kDividerLowerOhms[0];
    result.input_current = inductor_amps[0] + (input - result.return_value) / first_divider;
    return result;
}

[[nodiscard]] bool make_frame(const ScannerLineState& state, ScannerReturnMode mode,
                              ScannerLineFrame& destination) noexcept {
    const auto values = reconstruct(state.capacitor_volts, state.inductor_amps,
                                    state.previous_input_volts, mode);
    if (!std::isfinite(values.return_value)
        || std::abs(values.return_value) > kScannerMaxOutputVolts
        || !std::isfinite(values.input_current)
        || std::abs(values.input_current) > kScannerMaxInputCurrentAmps) return false;
    for (const double tap : values.taps) {
        if (!std::isfinite(tap) || std::abs(tap) > kScannerMaxOutputVolts) return false;
    }
    ScannerLineFrame result;
    result.taps_volts = values.taps;
    result.return_volts = values.return_value;
    result.input_current_amps = values.input_current;
    result.energy_joules = energy(state);
    result.frame = state.frames;
    destination = result;
    return true;
}

} // namespace

std::string_view ScannerLine::authoring_sha256() noexcept {
    return scanner_generated::kAuthoringSha256;
}

Status ScannerLine::prepare(double rate) noexcept {
    if (!is_supported_scanner_sample_rate(rate)) return Status::InvalidSpec;
    std::array<Operator, 2> candidate{};
    double maximum_residual = 0.0;
    for (std::size_t index = 0; index < candidate.size(); ++index) {
        if (!prepare_operator(rate, static_cast<ScannerReturnMode>(index),
                              candidate[index].transition, candidate[index].forcing,
                              maximum_residual)) return Status::InvalidProfile;
    }
    operators_ = candidate;
    state_ = ScannerLineState{};
    sample_rate_ = rate;
    preparation_residual_ = maximum_residual;
    prepared_ = true;
    return Status::Ok;
}

Status ScannerLine::reconfigure_sample_rate(double rate) noexcept {
    if (!prepared_) return Status::NotPrepared;
    if (!is_supported_scanner_sample_rate(rate)) return Status::InvalidSpec;
    if (rate == sample_rate_) return Status::Ok;
    ScannerLine candidate;
    const Status result = candidate.prepare(rate);
    if (result != Status::Ok) return result;
    candidate.state_ = state_;
    *this = candidate;
    return Status::Ok;
}

Status ScannerLine::restore_state(const ScannerLineState& replacement) noexcept {
    if (!prepared_) return Status::NotPrepared;
    if (!valid_state(replacement)) return Status::InvalidProfile;
    state_ = replacement;
    return Status::Ok;
}

Status ScannerLine::observe(ScannerReturnMode mode, ScannerLineFrame& destination) const noexcept {
    if (!prepared_) return Status::NotPrepared;
    if (!is_valid_scanner_return_mode(mode)) return Status::InvalidEvent;
    ScannerLineFrame candidate;
    if (!make_frame(state_, mode, candidate)) return Status::InvalidBuffer;
    destination = candidate;
    return Status::Ok;
}

Status ScannerLine::process_frame(double input, ScannerReturnMode mode,
                                  ScannerLineFrame& destination) noexcept {
    if (!prepared_) return Status::NotPrepared;
    if (!is_valid_scanner_return_mode(mode)) return Status::InvalidEvent;
    if (!valid_input(input)) return Status::InvalidBuffer;
    if (state_.frames == std::numeric_limits<std::uint64_t>::max()) return Status::TimelineOverflow;
    const Operator& op = operators_[static_cast<std::size_t>(mode)];
    RealVector previous{}, next{};
    for (std::size_t section = 0; section < kScannerSectionCount; ++section) {
        previous[section] = state_.capacitor_volts[section];
        previous[kScannerSectionCount + section] = kScannerCurrentScaleOhms * state_.inductor_amps[section];
    }
    const double input_sum = input + state_.previous_input_volts;
    for (std::size_t row = 0; row < n; ++row) {
        double value = op.forcing[row] * input_sum;
        for (std::size_t column = 0; column < n; ++column) {
            value += op.transition[row][column] * previous[column];
        }
        next[row] = value;
    }
    ScannerLineState candidate;
    for (std::size_t section = 0; section < kScannerSectionCount; ++section) {
        candidate.capacitor_volts[section] = next[section];
        candidate.inductor_amps[section] = next[kScannerSectionCount + section] / kScannerCurrentScaleOhms;
    }
    candidate.previous_input_volts = input;
    candidate.frames = state_.frames + 1;
    if (!valid_state(candidate)) return Status::InvalidBuffer;
    ScannerLineFrame frame;
    if (!make_frame(candidate, mode, frame)) return Status::InvalidBuffer;
    state_ = candidate;
    destination = frame;
    return Status::Ok;
}

Status ScannerLine::response(double frequency_hz, ScannerReturnMode mode,
                            ScannerLineResponse& destination) const noexcept {
    if (!prepared_) return Status::NotPrepared;
    if (!is_valid_scanner_return_mode(mode)) return Status::InvalidEvent;
    if (!std::isfinite(frequency_hz) || frequency_hz < 0.0
        || frequency_hz >= sample_rate_ * 0.5) return Status::InvalidSpec;
    const Operator& op = operators_[static_cast<std::size_t>(mode)];
    const double angle = 2.0 * std::numbers::pi * frequency_hz / sample_rate_;
    const Complex delay{std::cos(angle), -std::sin(angle)};
    ComplexMatrix matrix{};
    ComplexVector rhs{}, solution{};
    for (std::size_t row = 0; row < n; ++row) {
        rhs[row] = op.forcing[row] * (Complex{1.0, 0.0} + delay);
        for (std::size_t column = 0; column < n; ++column) {
            matrix[row][column] = (row == column ? Complex{1.0, 0.0} : Complex{})
                                - delay * op.transition[row][column];
        }
    }
    Factorization<Complex> factor;
    if (!factor.factor(matrix) || !factor.solve(rhs, solution)) return Status::InvalidBuffer;
    ScannerLineResponse candidate;
    candidate.normalized_residual = residual(matrix, rhs, solution, factor.scales);
    if (!std::isfinite(candidate.normalized_residual)
        || !factor.condition(candidate.condition_inf)) return Status::InvalidBuffer;
    std::array<Complex, kScannerSectionCount> capacitor_volts{}, inductor_amps{};
    for (std::size_t section = 0; section < kScannerSectionCount; ++section) {
        capacitor_volts[section] = solution[section];
        inductor_amps[section] = solution[kScannerSectionCount + section] / kScannerCurrentScaleOhms;
    }
    const auto values = reconstruct(capacitor_volts, inductor_amps, Complex{1.0, 0.0}, mode);
    if (!finite_scalar(values.return_value) || !finite_scalar(values.input_current)) return Status::InvalidBuffer;
    for (const auto& tap : values.taps) if (!finite_scalar(tap)) return Status::InvalidBuffer;
    candidate.taps = values.taps;
    candidate.return_gain = values.return_value;
    candidate.input_admittance = values.input_current;
    destination = candidate;
    return Status::Ok;
}

} // namespace hammond
