#include "hammond/ScannerLineFoh.h"
#include "hammond/generated/ScannerLineData.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <complex>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <numbers>
#include <type_traits>
#include <utility>

namespace hammond {
namespace {

constexpr std::size_t n = kScannerStateCoordinateCount;
constexpr std::size_t augmented_n = n + 2;
constexpr double maximum_residual = 1.0e-9;
constexpr double maximum_condition_roundoff = 1.0e-4;
constexpr std::uint32_t maximum_squarings = 16;
template <typename Scalar, std::size_t Size>
using Vector = std::array<Scalar, Size>;
template <typename Scalar, std::size_t Size>
using Matrix = std::array<Vector<Scalar, Size>, Size>;
using RealVector = Vector<double, n>;
using RealMatrix = Matrix<double, n>;
using AugmentedVector = Vector<double, augmented_n>;
using AugmentedMatrix = Matrix<double, augmented_n>;
using Complex = std::complex<double>;
using ComplexVector = Vector<Complex, n>;
using ComplexMatrix = Matrix<Complex, n>;
static_assert(std::numeric_limits<double>::is_iec559
              && std::numeric_limits<double>::digits == 53
              && sizeof(double) == 8);
static_assert(scanner_generated::kModelId == kScannerLineModelId);
static_assert(scanner_generated::kInductancesH.size() == kScannerSectionCount);
static_assert(scanner_generated::kCapacitancesF.size() == kScannerSectionCount);
static_assert(scanner_generated::kDividerUpperOhms.size() == 6);
static_assert(scanner_generated::kDividerLowerOhms.size() == 6);
static_assert(sizeof(ScannerLineFoh) <= 24 * 1024);

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

// One row-scaled, partial-pivot LU for all right-hand sides. The dimension is
// 38 for stopped preparation and 36 for the stopped complex response solve.
template <typename Scalar, std::size_t Size>
struct Factorization {
    Matrix<Scalar, Size> lu{};
    Vector<double, Size> scales{};
    std::array<std::size_t, Size> pivots{};
    double scaled_matrix_norm{0.0};

    [[nodiscard]] bool factor(const Matrix<Scalar, Size>& matrix) noexcept {
        scaled_matrix_norm = 0.0;
        for (std::size_t row = 0; row < Size; ++row) {
            double scale = 0.0;
            for (const auto& value : matrix[row]) {
                if (!finite_scalar(value)) return false;
                const double magnitude = std::abs(value);
                if (!std::isfinite(magnitude)) return false;
                scale = std::max(scale, magnitude);
            }
            if (!(scale > 0.0)) return false;
            scales[row] = scale;
            double row_norm = 0.0;
            for (std::size_t column = 0; column < Size; ++column) {
                lu[row][column] = matrix[row][column] / scale;
                if (!finite_scalar(lu[row][column])) return false;
                row_norm += std::abs(lu[row][column]);
            }
            if (!std::isfinite(row_norm)) return false;
            scaled_matrix_norm = std::max(scaled_matrix_norm, row_norm);
        }
        for (std::size_t column = 0; column < Size; ++column) {
            std::size_t pivot = column;
            double magnitude = std::abs(lu[column][column]);
            for (std::size_t row = column + 1; row < Size; ++row) {
                const double candidate = std::abs(lu[row][column]);
                if (!std::isfinite(candidate)) return false;
                if (candidate > magnitude) {
                    pivot = row;
                    magnitude = candidate;
                }
            }
            if (!std::isfinite(magnitude)
                || magnitude <= 8.0 * std::numeric_limits<double>::epsilon()) return false;
            pivots[column] = pivot;
            if (pivot != column) std::swap(lu[pivot], lu[column]);
            for (std::size_t row = column + 1; row < Size; ++row) {
                lu[row][column] /= lu[column][column];
                if (!finite_scalar(lu[row][column])) return false;
                for (std::size_t other = column + 1; other < Size; ++other) {
                    lu[row][other] -= lu[row][column] * lu[column][other];
                    if (!finite_scalar(lu[row][other])) return false;
                }
            }
        }
        return true;
    }

    [[nodiscard]] bool solve(const Vector<Scalar, Size>& rhs,
                             Vector<Scalar, Size>& destination) const noexcept {
        Vector<Scalar, Size> value{};
        for (std::size_t row = 0; row < Size; ++row) {
            value[row] = rhs[row] / scales[row];
            if (!finite_scalar(value[row])) return false;
        }
        // Later pivot swaps move earlier L columns too; apply the complete row
        // permutation before either triangular solve, for every right-hand side.
        for (std::size_t row = 0; row < Size; ++row) {
            if (pivots[row] != row) std::swap(value[row], value[pivots[row]]);
        }
        for (std::size_t row = 0; row < Size; ++row) {
            for (std::size_t column = 0; column < row; ++column) {
                value[row] -= lu[row][column] * value[column];
                if (!finite_scalar(value[row])) return false;
            }
        }
        for (std::size_t reverse = Size; reverse > 0; --reverse) {
            const std::size_t row = reverse - 1;
            for (std::size_t column = row + 1; column < Size; ++column) {
                value[row] -= lu[row][column] * value[column];
                if (!finite_scalar(value[row])) return false;
            }
            value[row] /= lu[row][row];
            if (!finite_scalar(value[row])) return false;
        }
        destination = value;
        return true;
    }

    [[nodiscard]] bool condition(double& destination) const noexcept {
        Vector<double, Size> inverse_row_sums{};
        for (std::size_t column = 0; column < Size; ++column) {
            Vector<Scalar, Size> rhs{}, solution{};
            // solve() scales its RHS. This gives a unit column for scaled Q,
            // so the condition and residual refer to precisely the same system.
            rhs[column] = scales[column];
            if (!solve(rhs, solution)) return false;
            for (std::size_t row = 0; row < Size; ++row) {
                inverse_row_sums[row] += std::abs(solution[row]);
                if (!std::isfinite(inverse_row_sums[row])) return false;
            }
        }
        const double inverse_norm =
            *std::max_element(inverse_row_sums.begin(), inverse_row_sums.end());
        const double result = scaled_matrix_norm * inverse_norm;
        if (!std::isfinite(result) || result <= 0.0) return false;
        destination = result;
        return true;
    }
};

template <typename Scalar, std::size_t Size>
[[nodiscard]] bool residual(const Matrix<Scalar, Size>& matrix,
                            const Vector<Scalar, Size>& rhs,
                            const Vector<Scalar, Size>& solution,
                            const Vector<double, Size>& scales,
                            double& destination) noexcept {
    double matrix_norm = 0.0;
    double rhs_norm = 0.0;
    double solution_norm = 0.0;
    double residual_norm = 0.0;
    for (std::size_t row = 0; row < Size; ++row) {
        const Scalar scaled_rhs = rhs[row] / scales[row];
        if (!finite_scalar(scaled_rhs) || !finite_scalar(solution[row])) return false;
        Scalar difference = -scaled_rhs;
        double row_norm = 0.0;
        for (std::size_t column = 0; column < Size; ++column) {
            const Scalar coefficient = matrix[row][column] / scales[row];
            if (!finite_scalar(coefficient)) return false;
            difference += coefficient * solution[column];
            if (!finite_scalar(difference)) return false;
            row_norm += std::abs(coefficient);
        }
        const double error = std::abs(difference);
        const double rhs_magnitude = std::abs(scaled_rhs);
        const double solution_magnitude = std::abs(solution[row]);
        if (!std::isfinite(row_norm) || !std::isfinite(error)
            || !std::isfinite(rhs_magnitude) || !std::isfinite(solution_magnitude)) return false;
        residual_norm = std::max(residual_norm, error);
        matrix_norm = std::max(matrix_norm, row_norm);
        rhs_norm = std::max(rhs_norm, rhs_magnitude);
        solution_norm = std::max(solution_norm, solution_magnitude);
    }
    const double denominator = matrix_norm * solution_norm + rhs_norm;
    if (!std::isfinite(denominator)) return false;
    if (denominator == 0.0) {
        if (residual_norm != 0.0) return false;
        destination = 0.0;
        return true;
    }
    const double result = residual_norm / denominator;
    if (!std::isfinite(result)) return false;
    destination = result;
    return true;
}

[[nodiscard]] bool multiply(const AugmentedMatrix& left, const AugmentedMatrix& right,
                            AugmentedMatrix& destination) noexcept {
    // Every caller supplies distinct destination storage. No temporary inverse,
    // dynamic storage, sparsity threshold or input-dependent work is involved.
    for (std::size_t row = 0; row < augmented_n; ++row) {
        for (std::size_t column = 0; column < augmented_n; ++column) {
            double value = 0.0;
            for (std::size_t inner = 0; inner < augmented_n; ++inner) {
                value += left[row][inner] * right[inner][column];
                if (!std::isfinite(value)) return false;
            }
            destination[row][column] = value;
        }
    }
    return true;
}

[[nodiscard]] bool positive_finite(double value) noexcept {
    return std::isfinite(value) && value > 0.0;
}

[[nodiscard]] bool augmented_generator(double rate, ScannerReturnMode mode,
                                       AugmentedMatrix& matrix) noexcept {
    const double step = 1.0 / rate;
    if (!positive_finite(step) || !positive_finite(scanner_generated::kReturnOhms)
        || !positive_finite(scanner_generated::kTerminationOhms)) return false;
    for (std::size_t divider = 0; divider < 6; ++divider) {
        if (!positive_finite(scanner_generated::kDividerUpperOhms[divider])
            || !positive_finite(scanner_generated::kDividerLowerOhms[divider])) return false;
    }
    for (std::size_t section = 0; section < kScannerSectionCount; ++section) {
        const double capacitance = scanner_generated::kCapacitancesF[section];
        const double inductance = scanner_generated::kInductancesH[section];
        if (!positive_finite(capacitance) || !positive_finite(inductance)) return false;
        const double current_coefficient = step / (capacitance * kScannerCurrentScaleOhms);
        matrix[section][kScannerSectionCount + section] = current_coefficient;
        if (section + 1 < kScannerSectionCount) {
            matrix[section][kScannerSectionCount + section + 1] = -current_coefficient;
        }
        // D2..D6 load p1..p5, before their corresponding inductor. D1 instead
        // belongs to the ideal input/common-return boundary below.
        if (section < 5) {
            const double resistance = scanner_generated::kDividerUpperOhms[section + 1]
                                    + scanner_generated::kDividerLowerOhms[section + 1];
            matrix[section][section] = -step / (capacitance * resistance);
        } else if (section + 1 == kScannerSectionCount) {
            matrix[section][section] =
                -step / (capacitance * scanner_generated::kTerminationOhms);
        }
        const std::size_t current_row = kScannerSectionCount + section;
        const double voltage_coefficient = step * kScannerCurrentScaleOhms / inductance;
        matrix[current_row][section] = -voltage_coefficient;
        if (section != 0) matrix[current_row][section - 1] = voltage_coefficient;
    }
    const ReturnCoefficients boundary = return_coefficients(mode);
    matrix[kScannerSectionCount][kScannerSectionCount] =
        -step * boundary.current_ohms / scanner_generated::kInductancesH[0];
    matrix[kScannerSectionCount][n] = step * kScannerCurrentScaleOhms
                                    * (1.0 - boundary.input_gain)
                                    / scanner_generated::kInductancesH[0];
    // Normalized interval time: du/dtau = delta_u. This is 1, not step.
    matrix[n][n + 1] = 1.0;
    for (const auto& row : matrix) {
        for (const double value : row) if (!std::isfinite(value)) return false;
    }
    return true;
}

[[nodiscard]] bool prepare_operator(double rate, ScannerReturnMode mode,
                                    RealMatrix& transition, RealVector& previous_forcing,
                                    RealVector& current_forcing,
                                    ScannerLineFohPreparation& diagnostics) noexcept {
    AugmentedMatrix x{};
    if (!augmented_generator(rate, mode, x)) return false;
    double norm_one = 0.0;
    for (std::size_t column = 0; column < augmented_n; ++column) {
        double sum = 0.0;
        for (std::size_t row = 0; row < augmented_n; ++row) sum += std::abs(x[row][column]);
        if (!std::isfinite(sum)) return false;
        norm_one = std::max(norm_one, sum);
    }
    double scaled_norm = norm_one;
    std::uint32_t squarings = 0;
    while (scaled_norm > 0.5 && squarings < maximum_squarings) {
        scaled_norm *= 0.5;
        ++squarings;
    }
    if (!std::isfinite(scaled_norm) || scaled_norm > 0.5) return false;
    for (auto& row : x) {
        for (double& value : row) {
            value = std::ldexp(value, -static_cast<int>(squarings));
            if (!std::isfinite(value)) return false;
        }
    }

    // Common positive c0 normalization of both polynomials is permitted by the
    // contract. Preserve Higham's degree-13 evaluation order: six dense products.
    constexpr double c0 = 64764752532480000.0;
    constexpr std::array<double, 14> c{
        1.0, 32382376266240000.0 / c0, 7771770303897600.0 / c0,
        1187353796428800.0 / c0, 129060195264000.0 / c0, 10559470521600.0 / c0,
        670442572800.0 / c0, 33522128640.0 / c0, 1323241920.0 / c0,
        40840800.0 / c0, 960960.0 / c0, 16380.0 / c0, 182.0 / c0, 1.0 / c0};
    AugmentedMatrix x2{}, x4{}, x6{}, inner{}, work{}, u{}, v{}, q{}, p{}, exponential{};
    if (!multiply(x, x, x2) || !multiply(x2, x2, x4) || !multiply(x2, x4, x6)) return false;
    for (std::size_t row = 0; row < augmented_n; ++row) {
        for (std::size_t column = 0; column < augmented_n; ++column) {
            inner[row][column] = c[13] * x6[row][column] + c[11] * x4[row][column]
                               + c[9] * x2[row][column];
            if (!std::isfinite(inner[row][column])) return false;
        }
    }
    if (!multiply(x6, inner, work)) return false;
    for (std::size_t row = 0; row < augmented_n; ++row) {
        for (std::size_t column = 0; column < augmented_n; ++column) {
            inner[row][column] = work[row][column] + c[7] * x6[row][column]
                               + c[5] * x4[row][column] + c[3] * x2[row][column]
                               + (row == column ? c[1] : 0.0);
            if (!std::isfinite(inner[row][column])) return false;
        }
    }
    if (!multiply(x, inner, u)) return false;
    for (std::size_t row = 0; row < augmented_n; ++row) {
        for (std::size_t column = 0; column < augmented_n; ++column) {
            inner[row][column] = c[12] * x6[row][column] + c[10] * x4[row][column]
                               + c[8] * x2[row][column];
            if (!std::isfinite(inner[row][column])) return false;
        }
    }
    if (!multiply(x6, inner, v)) return false;
    for (std::size_t row = 0; row < augmented_n; ++row) {
        for (std::size_t column = 0; column < augmented_n; ++column) {
            v[row][column] = v[row][column] + c[6] * x6[row][column]
                           + c[4] * x4[row][column] + c[2] * x2[row][column]
                           + (row == column ? c[0] : 0.0);
            q[row][column] = v[row][column] - u[row][column];
            p[row][column] = v[row][column] + u[row][column];
            if (!std::isfinite(v[row][column]) || !std::isfinite(q[row][column])
                || !std::isfinite(p[row][column])) return false;
        }
    }
    Factorization<double, augmented_n> factor;
    if (!factor.factor(q)) return false;
    double worst_residual = 0.0;
    for (std::size_t column = 0; column < augmented_n; ++column) {
        AugmentedVector rhs{}, solution{};
        for (std::size_t row = 0; row < augmented_n; ++row) rhs[row] = p[row][column];
        double error = 0.0;
        if (!factor.solve(rhs, solution)
            || !residual(q, rhs, solution, factor.scales, error)
            || error > maximum_residual) return false;
        worst_residual = std::max(worst_residual, error);
        for (std::size_t row = 0; row < augmented_n; ++row) exponential[row][column] = solution[row];
    }
    double condition = 0.0;
    if (!factor.condition(condition)
        || condition * std::numeric_limits<double>::epsilon() > maximum_condition_roundoff) return false;
    for (std::uint32_t step = 0; step < squarings; ++step) {
        if (!multiply(exponential, exponential, work)) return false;
        exponential = work;
    }
    for (std::size_t row = 0; row < n; ++row) {
        for (std::size_t column = 0; column < n; ++column) {
            const double value = exponential[row][column];
            if (!std::isfinite(value)) return false;
            transition[row][column] = value;
        }
        current_forcing[row] = exponential[row][n + 1];
        previous_forcing[row] = exponential[row][n] - current_forcing[row];
        if (!std::isfinite(current_forcing[row]) || !std::isfinite(previous_forcing[row])) return false;
    }
    diagnostics.augmented_norm_one = norm_one;
    diagnostics.squarings = squarings;
    diagnostics.normalized_residual = worst_residual;
    diagnostics.condition_inf = condition;
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
    const double stored = energy(state);
    if (!std::isfinite(stored) || stored < 0.0 || stored > kScannerMaxEnergyJoules) return false;
    ScannerLineFrame result;
    result.taps_volts = values.taps;
    result.return_volts = values.return_value;
    result.input_current_amps = values.input_current;
    result.energy_joules = stored;
    result.frame = state.frames;
    destination = result;
    return true;
}

} // namespace

std::string_view ScannerLineFoh::authoring_sha256() noexcept {
    return scanner_generated::kAuthoringSha256;
}

Status ScannerLineFoh::prepare(double rate) noexcept {
    if (!is_supported_scanner_sample_rate(rate)) return Status::InvalidSpec;
    std::array<Operator, 2> candidate{};
    std::array<ScannerLineFohPreparation, 2> diagnostics{};
    double worst_residual = 0.0;
    for (std::size_t index = 0; index < candidate.size(); ++index) {
        if (!prepare_operator(rate, static_cast<ScannerReturnMode>(index),
                              candidate[index].transition, candidate[index].previous_forcing,
                              candidate[index].current_forcing, diagnostics[index])) return Status::InvalidProfile;
        worst_residual = std::max(worst_residual, diagnostics[index].normalized_residual);
    }
    operators_ = candidate;
    diagnostics_ = diagnostics;
    state_ = ScannerLineState{};
    sample_rate_ = rate;
    preparation_residual_ = worst_residual;
    prepared_ = true;
    return Status::Ok;
}

Status ScannerLineFoh::reconfigure_sample_rate(double rate) noexcept {
    if (!prepared_) return Status::NotPrepared;
    if (!is_supported_scanner_sample_rate(rate)) return Status::InvalidSpec;
    if (rate == sample_rate_) return Status::Ok;
    ScannerLineFoh candidate;
    const Status status = candidate.prepare(rate);
    if (status != Status::Ok) return status;
    candidate.state_ = state_;
    *this = candidate;
    return Status::Ok;
}

Status ScannerLineFoh::restore_state(const ScannerLineState& replacement) noexcept {
    if (!prepared_) return Status::NotPrepared;
    if (!valid_state(replacement)) return Status::InvalidProfile;
    state_ = replacement;
    return Status::Ok;
}

Status ScannerLineFoh::observe(ScannerReturnMode mode, ScannerLineFrame& destination) const noexcept {
    if (!prepared_) return Status::NotPrepared;
    if (!is_valid_scanner_return_mode(mode)) return Status::InvalidEvent;
    ScannerLineFrame candidate;
    if (!make_frame(state_, mode, candidate)) return Status::InvalidBuffer;
    destination = candidate;
    return Status::Ok;
}

Status ScannerLineFoh::process_frame(double input, ScannerReturnMode mode,
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
    for (std::size_t row = 0; row < n; ++row) {
        double value = op.previous_forcing[row] * state_.previous_input_volts
                     + op.current_forcing[row] * input;
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

Status ScannerLineFoh::response(double frequency_hz, ScannerReturnMode mode,
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
        rhs[row] = op.current_forcing[row] + delay * op.previous_forcing[row];
        for (std::size_t column = 0; column < n; ++column) {
            matrix[row][column] = (row == column ? Complex{1.0, 0.0} : Complex{})
                                - delay * op.transition[row][column];
        }
    }
    Factorization<Complex, n> factor;
    if (!factor.factor(matrix) || !factor.solve(rhs, solution)) return Status::InvalidBuffer;
    ScannerLineResponse candidate;
    if (!residual(matrix, rhs, solution, factor.scales, candidate.normalized_residual)
        || candidate.normalized_residual > maximum_residual
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
