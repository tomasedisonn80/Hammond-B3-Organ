#pragma once

#include "hammond/ScannerLine.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <string_view>

namespace hammond {

inline constexpr std::size_t kScannerTerminalCount = 9;
inline constexpr std::size_t kScannerPositionCount = 16;
inline constexpr double kScannerNominalSpeedHz = 412.0 / 60.0;
inline constexpr std::string_view kScannerRotorModelId =
    "nominal-unloaded-triangular-scanner-rotor-v1";

// The historical selector has six modes; bypass is owned by the tablets.
// These are research-module values, not new Engine/native parameter IDs.
enum class ScannerMode : std::uint8_t { V1 = 0, V2 = 1, V3 = 2, C1 = 3, C2 = 4, C3 = 5 };

[[nodiscard]] constexpr bool is_valid_scanner_mode(ScannerMode mode) noexcept {
    return static_cast<std::uint8_t>(mode) <= static_cast<std::uint8_t>(ScannerMode::C3);
}

// Checked conversions preserve the destination when the mode is invalid.
[[nodiscard]] constexpr bool scanner_mode_return(ScannerMode mode,
                                                ScannerReturnMode& destination) noexcept {
    if (!is_valid_scanner_mode(mode)) return false;
    destination = static_cast<std::uint8_t>(mode) < 3
                ? ScannerReturnMode::Vibrato : ScannerReturnMode::Chorus;
    return true;
}

[[nodiscard]] constexpr bool scanner_mode_depth(ScannerMode mode,
                                               std::size_t& destination) noexcept {
    if (!is_valid_scanner_mode(mode)) return false;
    destination = static_cast<std::size_t>(mode) % 3;
    return true;
}

// Invalid modes have no name, rather than silently acquiring a valid mode.
[[nodiscard]] constexpr std::string_view scanner_mode_name(ScannerMode mode) noexcept {
    switch (mode) {
    case ScannerMode::V1: return "V1";
    case ScannerMode::V2: return "V2";
    case ScannerMode::V3: return "V3";
    case ScannerMode::C1: return "C1";
    case ScannerMode::C2: return "C2";
    case ScannerMode::C3: return "C3";
    }
    return {};
}

struct ScannerRotorState {
    // One continuing phase, in turns, in [0,1). Zero observes terminal 1.
    double phase_turns{0.0};
    // Completed read-and-advance intervals. UINT64_MAX can be observed/restored,
    // but a subsequent process_frame rejects with TimelineOverflow.
    std::uint64_t frames{0};

    [[nodiscard]] bool operator==(const ScannerRotorState&) const noexcept = default;
};

struct ScannerRotorSelection {
    double phase_turns{0.0};
    std::size_t position_index{0}; // zero-based mechanical position, 0..15
    std::array<std::size_t, 2> terminal_indices{}; // zero-based terminals, 0..8
    std::array<std::size_t, 2> tap_indices{}; // zero-based line outputs, 0..18
    std::array<double, 2> weights{}; // complementary nonnegative overlap weights

    [[nodiscard]] bool operator==(const ScannerRotorSelection&) const noexcept = default;
};

struct ScannerRotorFrame {
    ScannerRotorSelection selection{};
    double output_volts{0.0}; // signed, relative to ground, with no added dry term
    // observe: current completed count; process: count after successful advance.
    // Static evaluate has no clock and reports zero here.
    std::uint64_t frame{0};

    [[nodiscard]] bool operator==(const ScannerRotorFrame&) const noexcept = default;
};

// Nominal unloaded two-terminal capacitive overlap only. The documented speed,
// linear overlap and selected circuit taps are not specimen measurements.
// No line state, Engine route, public controls, load, resampler or filter lives
// here. Call once for every elapsed sample, including silence/bypassed routes.
// Serialize access externally. All methods use bounded storage/work and allocate
// no memory; rejected operations preserve the whole object and destination.
class ScannerRotor {
public:
    // Success resets phase/count. An invalid rate preserves the old preparation.
    [[nodiscard]] Status prepare(double sample_rate) noexcept;
    // Stopped rate change preserves phase and completed count exactly.
    [[nodiscard]] Status reconfigure_sample_rate(double sample_rate) noexcept;
    [[nodiscard]] bool prepared() const noexcept { return prepared_; }
    [[nodiscard]] double sample_rate() const noexcept { return sample_rate_; }
    [[nodiscard]] double phase_increment_turns() const noexcept { return increment_turns_; }
    [[nodiscard]] ScannerRotorState state() const noexcept { return state_; }
    [[nodiscard]] Status restore_state(const ScannerRotorState& state) noexcept;

    // All 19 taps must be finite and within +/-kScannerMaxOutputVolts, including
    // taps not selected by this mode. Both V/C pairs use the same depth map;
    // the caller/line owns their different electrical return topology.
    [[nodiscard]] Status observe(const std::array<double, kScannerTapCount>& taps_volts,
                                 ScannerMode mode, ScannerRotorFrame& destination) const noexcept;
    // Read this phase, then advance it once by (412/60)/sample_rate turns.
    // The first successful call reports phase zero and completed count one.
    [[nodiscard]] Status process_frame(const std::array<double, kScannerTapCount>& taps_volts,
                                       ScannerMode mode, ScannerRotorFrame& destination) noexcept;

    // Stateless diagnostics/observation, available without preparation. Phase
    // must be finite in [0,1); it is never wrapped, clamped or silently repaired.
    [[nodiscard]] static Status select(double phase_turns, ScannerMode mode,
                                        ScannerRotorSelection& destination) noexcept;
    [[nodiscard]] static Status evaluate(double phase_turns,
                                          const std::array<double, kScannerTapCount>& taps_volts,
                                          ScannerMode mode,
                                          ScannerRotorFrame& destination) noexcept;

private:
    ScannerRotorState state_{};
    double sample_rate_{0.0};
    double increment_turns_{0.0};
    bool prepared_{false};
};

} // namespace hammond
