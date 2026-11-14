#pragma once

#include "hammond/RotaryHistory.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <memory>
#include <span>
#include <string_view>

// Independent nominal R4 research renderer. It does not connect Engine audio,
// change musical parameters/state, or declare R5/R6/physical cabinet acceptance.
// Contract: docs/ROTARY_RENDERER_CONTRACT.md / rotary-numerics-v1.
namespace hammond::rotary {

inline constexpr std::string_view kRendererContractId = "rotary-renderer-v1";

namespace detail {
struct RotaryRendererStorage;
struct RotaryRendererTestAccess;
}

// Immutable admitted geometry, separate from the immutable-fixture R3 path.
// This object owns no history and retains no pointer to the solve argument.
// Rates come from history; the admitted speed envelope includes the original
// rotor seed and both targets, so reset and stopped rate epochs share geometry.
class PreparedStreamingPath {
public:
    [[nodiscard]] Status prepare(const RotorProfile& rotor,
                                  const MicrophoneProfile& microphone,
                                  double sound_speed_m_s,
                                  double reference_distance_m) noexcept;
    [[nodiscard]] bool prepared() const noexcept { return prepared_; }
    [[nodiscard]] PathBounds bounds() const noexcept { return bounds_; }
    [[nodiscard]] Status solve(const MotionFrameHistory& history,
                               SamplePosition observation,
                               PathResult& result,
                               SamplePosition& emission) const noexcept;

private:
    MotionProfile motion_profile_{};
    Vec3 origin_m_{};
    MicrophoneProfile microphone_{};
    PathBounds bounds_{};
    double radius_m_{0.0};
    double sound_speed_m_s_{0.0};
    double reference_distance_m_{0.0};
    double max_speed_rad_s_{0.0};
    bool prepared_{false};
};

// Copied physical state, deliberately without process-call counters. Array
// order is Horn, Drum. frame is the next input frame and both owners' observed
// boundary, including all commands accepted at that boundary. This is an
// inspection value, not a serialized replay or musical-preset format.
struct RendererState {
    bool prepared{false};
    double sample_rate{0.0};
    std::uint64_t frame{0};
    std::uint64_t max_frame{0};
    std::array<MotionState, kRotorCount> motion{};
    std::array<MotionState, kRotorCount> epoch_initial{};
    std::array<SpeedCommand, kRotorCount> commands{};
    std::array<MotionSegment, kRotorCount> segments{};
    [[nodiscard]] bool operator==(const RendererState&) const noexcept = default;
};

// Copied epoch diagnostics. Path order is Horn/Left, Horn/Right, Drum/Left,
// Drum/Right. last_* fields describe the final accepted sample; maxima are
// over successful path solves in accepted samples in the current epoch.
// Successful zero-frame calls leave these diagnostics unchanged. Failure
// observations belong only to the returned ProcessResult, never these fields.
struct RendererDiagnostics {
    bool has_rendered_sample{false};
    std::uint64_t last_input_frame{0};
    SamplePosition last_observation{};
    std::array<PathResult, kPathCount> last_paths{};
    std::array<SamplePosition, kPathCount> last_emissions{};
    double max_solver_residual_s{0.0}; // Maximum absolute residual.
    std::uint32_t max_solver_iterations{0};
    [[nodiscard]] bool operator==(const RendererDiagnostics&) const noexcept = default;
};

// A single serialized owner. All methods, including getters, require external
// exclusion from concurrent calls. Lifecycle allocation/destruction is outside
// processing. No public method exposes borrowed mutable internal storage.
class RotaryRenderer {
public:
    RotaryRenderer() noexcept;
    ~RotaryRenderer();
    RotaryRenderer(const RotaryRenderer&) = delete;
    RotaryRenderer& operator=(const RotaryRenderer&) = delete;
    RotaryRenderer(RotaryRenderer&&) = delete;
    RotaryRenderer& operator=(RotaryRenderer&&) = delete;

    [[nodiscard]] Status prepare(const Profile& profile, const ProcessSpec& spec) noexcept;
    [[nodiscard]] bool prepared() const noexcept;
    [[nodiscard]] Profile profile() const noexcept;
    // An unprepared spec is {0,0}, distinct from ProcessSpec's authoring defaults.
    [[nodiscard]] ProcessSpec spec() const noexcept;
    [[nodiscard]] RendererState state() const noexcept;
    [[nodiscard]] RendererDiagnostics diagnostics() const noexcept;
    [[nodiscard]] std::array<PathBounds, kPathCount> path_bounds() const noexcept;
    [[nodiscard]] std::size_t history_capacity_frames() const noexcept;
    [[nodiscard]] std::uint32_t tail_flush_frames() const noexcept;
    [[nodiscard]] static constexpr std::uint32_t algorithmic_latency_frames() noexcept {
        return kAlgorithmicLatencyFrames;
    }

    // All four spans have the same N, including N=0. Horn/drum may overlap;
    // outputs must be disjoint from each other and both input spans. Events
    // are stable/nondecreasing in [0,N]; ties retain their supplied order.
    // Every rejection consumes zero events and preserves retained histories,
    // owners, persistent diagnostics and caller outputs. Unobservable prepared
    // output/journal scratch is not a persistent history or inspection value.
    [[nodiscard]] ProcessResult process(std::span<const double> horn,
                                         std::span<const double> drum,
                                         std::span<double> left,
                                         std::span<double> right,
                                         std::span<const CommandEvent> events = {}) noexcept;

    // Reset restores original profile seeds/commands at the current rate.
    // Both operations clear audio/retained motion histories and diagnostics.
    // Reconfiguration (even to the same rate) preserves current physical state
    // and commands, starts a new frame-zero epoch and discards old audio tails.
    [[nodiscard]] Status reset() noexcept;
    [[nodiscard]] Status reconfigure_sample_rate(double sample_rate) noexcept;

private:
    // The test accessor has no shipping implementation or public control. It
    // may inspect/corrupt a retained slot in a dedicated late-failure fixture.
    friend struct detail::RotaryRendererTestAccess;
    std::unique_ptr<detail::RotaryRendererStorage> storage_;
};

} // namespace hammond::rotary
