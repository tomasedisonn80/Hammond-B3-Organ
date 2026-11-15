#include "hammond/LeslieCrossover.h"

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

constexpr std::size_t n = 4;
using RealVector = std::array<double, n>;
using RealMatrix = std::array<RealVector, n>;
using Complex = std::complex<double>;
using ComplexVector = std::array<Complex, n>;
using ComplexMatrix = std::array<ComplexVector, n>;

// Atlas pp.271-272 documentary nominal values. The zero-loss realization and
// resistor loads are explicit numerical assumptions, not measured Leslie data.
constexpr double l2 = 0.0032;
constexpr double l3 = 0.0052;
constexpr double c16a = 0.0000078;
constexpr double c16b = 0.0000125;
constexpr double max_input_volts = 64.0;
constexpr double max_capacitor_volts = 65536.0;
constexpr double max_inductor_amps = 256.0;
constexpr double max_energy_joules = 1.0e6;
constexpr double maximum_preparation_residual = 1.0e-12;

[[nodiscard]] bool valid_rate(double rate) noexcept {
    return rate == 44100.0 || rate == 48000.0 || rate == 96000.0 || rate == 192000.0;
}

[[nodiscard]] bool valid_load(double resistance) noexcept {
    return std::isfinite(resistance) && resistance >= 1.0 && resistance <= 1024.0;
}

[[nodiscard]] bool bounded(double value, double maximum) noexcept {
    return std::isfinite(value) && std::abs(value) <= maximum;
}

template <typename Scalar>
[[nodiscard]] bool finite_scalar(const Scalar& value) noexcept {
    if constexpr (std::is_same_v<Scalar, double>) return std::isfinite(value);
    else return std::isfinite(value.real()) && std::isfinite(value.imag());
}

// Row-scaled, partial-pivot LU with fixed work/storage. Only the stopped
// preparation/response paths factor or divide by matrix pivots.
template <typename Scalar>
struct Factorization {
    using Vector = std::array<Scalar, n>;
    using Matrix = std::array<Vector, n>;
    Matrix lu{};
    RealVector scales{};
    std::array<std::size_t, n> pivots{};

    [[nodiscard]] bool factor(const Matrix& matrix) noexcept {
        for (std::size_t row = 0; row < n; ++row) {
            double scale = 0.0;
            for (const auto& value : matrix[row]) {
                if (!finite_scalar(value)) return false;
                scale = std::max(scale, std::abs(value));
            }
            if (!std::isfinite(scale) || scale <= 0.0) return false;
            scales[row] = scale;
            for (std::size_t column = 0; column < n; ++column) {
                lu[row][column] = matrix[row][column] / scale;
            }
        }
        for (std::size_t column = 0; column < n; ++column) {
            std::size_t pivot = column;
            double magnitude = std::abs(lu[column][column]);
            for (std::size_t row = column + 1; row < n; ++row) {
                const double candidate = std::abs(lu[row][column]);
                if (candidate > magnitude) {
                    magnitude = candidate;
                    pivot = row;
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
                    if (!finite_scalar(lu[row][other])) return false;
                }
            }
        }
        return true;
    }

    [[nodiscard]] bool solve(const Vector& rhs, Vector& destination) const noexcept {
        Vector result{};
        for (std::size_t row = 0; row < n; ++row) {
            if (!finite_scalar(rhs[row])) return false;
            result[row] = rhs[row] / scales[row];
        }
        // Apply all pivots before substitution: later swaps also moved the
        // earlier lower-triangle entries during factorization.
        for (std::size_t row = 0; row < n; ++row) {
            if (pivots[row] != row) std::swap(result[row], result[pivots[row]]);
        }
        for (std::size_t row = 0; row < n; ++row) {
            for (std::size_t column = 0; column < row; ++column) {
                result[row] -= lu[row][column] * result[column];
            }
        }
        for (std::size_t reverse = n; reverse > 0; --reverse) {
            const std::size_t row = reverse - 1;
            for (std::size_t column = row + 1; column < n; ++column) {
                result[row] -= lu[row][column] * result[column];
            }
            result[row] /= lu[row][row];
            if (!finite_scalar(result[row])) return false;
        }
        destination = result;
        return true;
    }
};

template <typename Scalar>
[[nodiscard]] double vector_norm(const std::array<Scalar, n>& value) noexcept {
    double result = 0.0;
    for (const auto& element : value) result = std::max(result, std::abs(element));
    return result;
}

template <typename Scalar>
[[nodiscard]] double matrix_norm(
    const std::array<std::array<Scalar, n>, n>& value) noexcept {
    double result = 0.0;
    for (const auto& row : value) {
        double sum = 0.0;
        for (const auto& element : row) sum += std::abs(element);
        result = std::max(result, sum);
    }
    return result;
}

template <typename Scalar>
[[nodiscard]] double vector_residual(
    const std::array<std::array<Scalar, n>, n>& matrix,
    const std::array<Scalar, n>& solution,
    const std::array<Scalar, n>& rhs) noexcept {
    std::array<Scalar, n> difference{};
    for (std::size_t row = 0; row < n; ++row) {
        difference[row] = -rhs[row];
        for (std::size_t column = 0; column < n; ++column) {
            difference[row] += matrix[row][column] * solution[column];
        }
    }
    return vector_norm(difference) /
        std::max(1.0, matrix_norm(matrix) * vector_norm(solution) + vector_norm(rhs));
}

[[nodiscard]] double matrix_residual(const RealMatrix& matrix,
                                      const RealMatrix& solution,
                                      const RealMatrix& rhs) noexcept {
    RealMatrix difference{};
    for (std::size_t row = 0; row < n; ++row) {
        for (std::size_t column = 0; column < n; ++column) {
            double value = -rhs[row][column];
            for (std::size_t inner = 0; inner < n; ++inner) {
                value += matrix[row][inner] * solution[inner][column];
            }
            difference[row][column] = value;
        }
    }
    return matrix_norm(difference) /
        std::max(1.0, matrix_norm(matrix) * matrix_norm(solution) + matrix_norm(rhs));
}

[[nodiscard]] bool prepare_operator(double rate, LeslieCrossoverLoads loads,
                                    RealMatrix& transition, RealVector& forcing,
                                    double& residual) noexcept {
    // State [VH-VB, VW-VB, I(L2:A->H), I(L3:A->W)] follows literal KCL.
    RealMatrix derivative{};
    derivative[0][0] = -1.0 / (loads.treble_ohms * c16a);
    derivative[0][2] = 1.0 / c16a;
    derivative[1][1] = -1.0 / (loads.bass_ohms * c16b);
    derivative[1][3] = 1.0 / c16b;
    derivative[2][0] = -1.0 / l2;
    derivative[3][1] = -1.0 / l3;
    const RealVector drive{1.0 / (loads.treble_ohms * c16a), 0.0,
                           1.0 / l2, 1.0 / l3};
    const double half_step = 0.5 / rate;
    RealMatrix left{}, right{}, candidate_transition{};
    RealVector input{}, candidate_forcing{};
    for (std::size_t row = 0; row < n; ++row) {
        input[row] = half_step * drive[row];
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
        for (std::size_t row = 0; row < n; ++row) candidate_transition[row][column] = solution[row];
    }
    if (!factor.solve(input, candidate_forcing)) return false;
    const double candidate_residual = std::max(
        matrix_residual(left, candidate_transition, right),
        vector_residual(left, candidate_forcing, input));
    if (!std::isfinite(candidate_residual)
        || candidate_residual > maximum_preparation_residual) return false;
    transition = candidate_transition;
    forcing = candidate_forcing;
    residual = candidate_residual;
    return true;
}

[[nodiscard]] double stored_energy(const LeslieCrossoverState& state) noexcept {
    return 0.5 * (c16a * state.capacitor_volts[0] * state.capacitor_volts[0]
        + c16b * state.capacitor_volts[1] * state.capacitor_volts[1]
        + l2 * state.inductor_amps[0] * state.inductor_amps[0]
        + l3 * state.inductor_amps[1] * state.inductor_amps[1]);
}

[[nodiscard]] bool valid_state(const LeslieCrossoverState& state) noexcept {
    if (!bounded(state.previous_input_volts, max_input_volts)) return false;
    for (const double value : state.capacitor_volts) {
        if (!bounded(value, max_capacitor_volts)) return false;
    }
    for (const double value : state.inductor_amps) {
        if (!bounded(value, max_inductor_amps)) return false;
    }
    const double energy = stored_energy(state);
    return std::isfinite(energy) && energy >= 0.0 && energy <= max_energy_joules;
}

[[nodiscard]] LeslieCrossoverFrame frame_for(const LeslieCrossoverState& state,
                                             LeslieCrossoverLoads loads) noexcept {
    LeslieCrossoverFrame result;
    result.treble_volts = state.previous_input_volts - state.capacitor_volts[0];
    result.bass_volts = state.capacitor_volts[1];
    result.treble_current_amps = result.treble_volts / loads.treble_ohms;
    result.bass_current_amps = result.bass_volts / loads.bass_ohms;
    result.input_current_amps = state.inductor_amps[0] + result.treble_current_amps
                             + state.inductor_amps[1];
    result.energy_joules = stored_energy(state);
    result.frame = state.frames;
    return result;
}

[[nodiscard]] bool finite_frame(const LeslieCrossoverFrame& value) noexcept {
    return std::isfinite(value.treble_volts) && std::isfinite(value.bass_volts)
        && std::isfinite(value.treble_current_amps) && std::isfinite(value.bass_current_amps)
        && std::isfinite(value.input_current_amps) && std::isfinite(value.energy_joules);
}

// Same expression/evaluation order in scalar calls and both block passes.
// The caller has already proved counter capacity. Only callers with admitted
// finite inputs may commit this candidate.
[[nodiscard]] LeslieCrossoverState advance(const LeslieCrossoverState& previous,
                                            double input, const RealMatrix& transition,
                                            const RealVector& forcing) noexcept {
    const RealVector current{previous.capacitor_volts[0], previous.capacitor_volts[1],
                              previous.inductor_amps[0], previous.inductor_amps[1]};
    RealVector next{};
    const double endpoints = input + previous.previous_input_volts;
    for (std::size_t row = 0; row < n; ++row) {
        double value = forcing[row] * endpoints;
        for (std::size_t column = 0; column < n; ++column) {
            value += transition[row][column] * current[column];
        }
        next[row] = value;
    }
    return {{next[0], next[1]}, {next[2], next[3]}, input, previous.frames + 1};
}

// Counts have already been bounded before this address-only check. Avoid
// pointer arithmetic outside either allocation and reject a wrapping byte range.
[[nodiscard]] bool overlapping(const void* left, std::size_t left_bytes,
                                const void* right, std::size_t right_bytes) noexcept {
    const auto left_start = reinterpret_cast<std::uintptr_t>(left);
    const auto right_start = reinterpret_cast<std::uintptr_t>(right);
    constexpr auto maximum = std::numeric_limits<std::uintptr_t>::max();
    if (left_bytes > maximum - left_start || right_bytes > maximum - right_start) return true;
    return left_start < right_start + right_bytes && right_start < left_start + left_bytes;
}

} // namespace

Status LeslieCrossover::prepare(double sample_rate, LeslieCrossoverLoads loads) noexcept {
    if (!valid_rate(sample_rate) || !valid_load(loads.treble_ohms)
        || !valid_load(loads.bass_ohms)) return Status::InvalidSpec;
    RealMatrix transition;
    RealVector forcing;
    double residual = 0.0;
    if (!prepare_operator(sample_rate, loads, transition, forcing, residual)) return Status::InvalidSpec;
    transition_ = transition;
    forcing_ = forcing;
    loads_ = loads;
    sample_rate_ = sample_rate;
    preparation_residual_ = residual;
    state_ = {};
    prepared_ = true;
    return Status::Ok;
}

Status LeslieCrossover::reconfigure_sample_rate(double sample_rate) noexcept {
    if (!prepared_) return Status::NotPrepared;
    if (!valid_rate(sample_rate)) return Status::InvalidSpec;
    RealMatrix transition;
    RealVector forcing;
    double residual = 0.0;
    if (!prepare_operator(sample_rate, loads_, transition, forcing, residual)) return Status::InvalidSpec;
    transition_ = transition;
    forcing_ = forcing;
    sample_rate_ = sample_rate;
    preparation_residual_ = residual;
    return Status::Ok;
}

Status LeslieCrossover::restore_state(const LeslieCrossoverState& state) noexcept {
    if (!prepared_) return Status::NotPrepared;
    if (!valid_state(state)) return Status::InvalidProfile;
    state_ = state;
    return Status::Ok;
}

Status LeslieCrossover::observe(LeslieCrossoverFrame& destination) const noexcept {
    if (!prepared_) return Status::NotPrepared;
    const auto candidate = frame_for(state_, loads_);
    if (!finite_frame(candidate)) return Status::InvalidBuffer;
    destination = candidate;
    return Status::Ok;
}

Status LeslieCrossover::process_frame(double input_volts,
                                      LeslieCrossoverFrame& destination) noexcept {
    if (!prepared_) return Status::NotPrepared;
    if (state_.frames == std::numeric_limits<std::uint64_t>::max()) return Status::TimelineOverflow;
    if (!bounded(input_volts, max_input_volts)) return Status::InvalidBuffer;
    const auto candidate_state = advance(state_, input_volts, transition_, forcing_);
    if (!valid_state(candidate_state)) return Status::InvalidBuffer;
    const auto candidate_frame = frame_for(candidate_state, loads_);
    if (!finite_frame(candidate_frame)) return Status::InvalidBuffer;
    state_ = candidate_state;
    destination = candidate_frame;
    return Status::Ok;
}

Status LeslieCrossover::process(std::span<const double> input_volts,
                                std::span<LeslieCrossoverFrame> destination) noexcept {
    if (!prepared_) return Status::NotPrepared;
    if (input_volts.size() != destination.size()) return Status::InvalidBuffer;
    if (input_volts.size() > kLeslieCrossoverBlockCapacity) return Status::BlockTooLarge;
    if (input_volts.empty()) return Status::Ok;
    const auto count = static_cast<std::uint64_t>(input_volts.size());
    if (state_.frames > std::numeric_limits<std::uint64_t>::max() - count) return Status::TimelineOverflow;
    if (input_volts.data() == nullptr || destination.data() == nullptr
        || overlapping(input_volts.data(), input_volts.size_bytes(),
                       destination.data(), destination.size_bytes())) return Status::InvalidBuffer;

    // Validate the complete trajectory before writing any output. A second,
    // identical bounded pass avoids a 4096-frame scratch buffer and cannot
    // discover a new numerical rejection while immutable inputs are retained.
    auto candidate = state_;
    for (const double input : input_volts) {
        if (!bounded(input, max_input_volts)) return Status::InvalidBuffer;
        candidate = advance(candidate, input, transition_, forcing_);
        if (!valid_state(candidate) || !finite_frame(frame_for(candidate, loads_))) return Status::InvalidBuffer;
    }
    auto replay = state_;
    for (std::size_t index = 0; index < input_volts.size(); ++index) {
        replay = advance(replay, input_volts[index], transition_, forcing_);
        destination[index] = frame_for(replay, loads_);
    }
    state_ = replay;
    return Status::Ok;
}

Status LeslieCrossover::response(double frequency_hz,
                                 LeslieCrossoverResponse& destination) const noexcept {
    if (!prepared_) return Status::NotPrepared;
    if (!std::isfinite(frequency_hz) || frequency_hz < 0.0
        || frequency_hz >= sample_rate_ / 2.0) return Status::InvalidSpec;
    const Complex inverse_z = std::polar(1.0, -2.0 * std::numbers::pi * frequency_hz / sample_rate_);
    ComplexMatrix left{};
    ComplexVector rhs{}, solution{};
    for (std::size_t row = 0; row < n; ++row) {
        rhs[row] = forcing_[row] * (1.0 + inverse_z);
        for (std::size_t column = 0; column < n; ++column) {
            left[row][column] = (row == column ? 1.0 : 0.0) - transition_[row][column] * inverse_z;
        }
    }
    if (frequency_hz == 0.0) {
        // Known DC equilibrium of this same recurrence, with its actual
        // numerical residual retained. No division by a zero s*C occurs.
        solution = {1.0, 1.0, 0.0, 1.0 / loads_.bass_ohms};
    } else {
        Factorization<Complex> factor;
        if (!factor.factor(left) || !factor.solve(rhs, solution)) return Status::InvalidSpec;
    }
    LeslieCrossoverResponse candidate;
    candidate.treble_gain = 1.0 - solution[0];
    candidate.bass_gain = solution[1];
    candidate.input_admittance = solution[2] + candidate.treble_gain / loads_.treble_ohms
                              + solution[3];
    candidate.normalized_residual = vector_residual(left, solution, rhs);
    if (!finite_scalar(candidate.treble_gain) || !finite_scalar(candidate.bass_gain)
        || !finite_scalar(candidate.input_admittance)
        || !std::isfinite(candidate.normalized_residual)) return Status::InvalidSpec;
    destination = candidate;
    return Status::Ok;
}

} // namespace hammond
