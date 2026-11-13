#include "hammond/ScannerRotor.h"

#include <array>
#include <cmath>
#include <limits>

namespace hammond {
namespace {

// Store explicitly zero-based output indices, converted once from the reviewed
// one-based atlas p.170 / DAFx2016 Table2 maps. These are connection maps, not
// interpolated output indices. V/C mode pairs share only their depth map.
constexpr std::array<std::array<std::size_t, kScannerTerminalCount>, 3> depth_maps{{
    {0, 1, 2, 3, 4, 5, 6, 7, 8},
    {0, 1, 2, 4, 6, 8, 10, 11, 12},
    {0, 1, 3, 6, 9, 12, 15, 17, 18},
}};

// Atlas p.166 omits the final 1 in print. The primary paper's figures1/3
// independently support this full16-position cycle under the stated phase
// origin; see SCANNER_PRIMARY_REVIEW.md and retained erratumE01.
constexpr std::array<std::size_t, kScannerPositionCount> traversal{
    0, 1, 2, 3, 4, 5, 6, 7, 8, 7, 6, 5, 4, 3, 2, 1};

[[nodiscard]] bool valid_phase(double phase) noexcept {
    return std::isfinite(phase) && phase >= 0.0 && phase < 1.0;
}

} // namespace

Status ScannerRotor::prepare(double rate) noexcept {
    if (!is_supported_scanner_sample_rate(rate)) return Status::InvalidSpec;
    sample_rate_ = rate;
    increment_turns_ = kScannerNominalSpeedHz / rate;
    state_ = ScannerRotorState{};
    prepared_ = true;
    return Status::Ok;
}

Status ScannerRotor::reconfigure_sample_rate(double rate) noexcept {
    if (!prepared_) return Status::NotPrepared;
    if (!is_supported_scanner_sample_rate(rate)) return Status::InvalidSpec;
    sample_rate_ = rate;
    increment_turns_ = kScannerNominalSpeedHz / rate;
    return Status::Ok;
}

Status ScannerRotor::restore_state(const ScannerRotorState& replacement) noexcept {
    if (!prepared_) return Status::NotPrepared;
    if (!valid_phase(replacement.phase_turns)) return Status::InvalidProfile;
    state_ = replacement;
    return Status::Ok;
}

Status ScannerRotor::select(double phase, ScannerMode mode,
                            ScannerRotorSelection& destination) noexcept {
    std::size_t depth = 0;
    if (!scanner_mode_depth(mode, depth)) return Status::InvalidEvent;
    if (!valid_phase(phase)) return Status::InvalidSpec;
    // Multiplication by16 is an exact exponent shift in this bounded range.
    const double position = phase * static_cast<double>(kScannerPositionCount);
    const auto index = static_cast<std::size_t>(position);
    const double fraction = position - static_cast<double>(index);
    const auto next = index + 1 == kScannerPositionCount ? 0 : index + 1;
    ScannerRotorSelection candidate;
    candidate.phase_turns = phase;
    candidate.position_index = index;
    candidate.terminal_indices = {traversal[index], traversal[next]};
    candidate.tap_indices = {depth_maps[depth][candidate.terminal_indices[0]],
                             depth_maps[depth][candidate.terminal_indices[1]]};
    candidate.weights = {1.0 - fraction, fraction};
    destination = candidate;
    return Status::Ok;
}

Status ScannerRotor::evaluate(double phase,
                              const std::array<double, kScannerTapCount>& taps,
                              ScannerMode mode, ScannerRotorFrame& destination) noexcept {
    ScannerRotorFrame candidate;
    const Status selected = select(phase, mode, candidate.selection);
    if (selected != Status::Ok) return selected;
    for (const double value : taps) {
        if (!std::isfinite(value) || std::abs(value) > kScannerMaxOutputVolts) {
            return Status::InvalidBuffer;
        }
    }
    // std::lerp evaluates the complementary linear blend while preserving
    // finite convex endpoint bounds; it does not rectify signed voltages.
    candidate.output_volts = std::lerp(taps[candidate.selection.tap_indices[0]],
                                       taps[candidate.selection.tap_indices[1]],
                                       candidate.selection.weights[1]);
    if (!std::isfinite(candidate.output_volts)
        || std::abs(candidate.output_volts) > kScannerMaxOutputVolts) {
        return Status::InvalidBuffer;
    }
    destination = candidate;
    return Status::Ok;
}

Status ScannerRotor::observe(const std::array<double, kScannerTapCount>& taps,
                             ScannerMode mode, ScannerRotorFrame& destination) const noexcept {
    if (!prepared_) return Status::NotPrepared;
    ScannerRotorFrame candidate;
    const Status result = evaluate(state_.phase_turns, taps, mode, candidate);
    if (result != Status::Ok) return result;
    candidate.frame = state_.frames;
    destination = candidate;
    return Status::Ok;
}

Status ScannerRotor::process_frame(const std::array<double, kScannerTapCount>& taps,
                                   ScannerMode mode, ScannerRotorFrame& destination) noexcept {
    if (!prepared_) return Status::NotPrepared;
    ScannerRotorFrame candidate;
    const Status result = evaluate(state_.phase_turns, taps, mode, candidate);
    if (result != Status::Ok) return result;
    if (state_.frames == std::numeric_limits<std::uint64_t>::max()) {
        return Status::TimelineOverflow;
    }
    double next_phase = state_.phase_turns + increment_turns_;
    if (next_phase >= 1.0) next_phase -= 1.0;
    candidate.frame = state_.frames + 1;
    state_ = ScannerRotorState{next_phase, candidate.frame};
    destination = candidate;
    return Status::Ok;
}

} // namespace hammond
