#pragma once

#include "hammond/ControlState.h"
#include "hammond/Profile.h"
#include "hammond/TonewheelBank.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <span>

namespace hammond {

// Nominal dry organ: ideal boolean keys, retained manual drawbar banks, and one
// shared free-running source field. This is not a measured console model.
// Prepare and all diagnostics require stopped or same-processing-thread access;
// no concurrent UI snapshot or live profile publication protocol is provided.
class Engine {
public:
    // Success installs an owned profile and starts a new seeded source field.
    // Initial controls: no keys, all banks zero, bank B selected, routes enabled,
    // expression one. Any failure preserves the previous engine and clock.
    [[nodiscard]] Status prepare(const RuntimeProfile& profile,
                                 const ProcessSpec& spec) noexcept;

    // Preflights the entire request. Rejection changes no state or output and
    // consumes no events. Positive calls accept empty (disconnected) output or
    // at least frames samples; extra output samples are untouched. Events use
    // half-open offsets and retain input order for ties. Zero-frame calls apply
    // offset-zero events once without advancing sources or the frame clock.
    [[nodiscard]] ProcessResult process(std::uint32_t frames,
                                        std::span<float> mono_output,
                                        std::span<const Event> events) noexcept;

    [[nodiscard]] std::uint64_t frame_clock() const noexcept { return frame_clock_; }
    [[nodiscard]] bool prepared() const noexcept { return prepared_; }

    // Copied diagnostics only. Invalid manuals/notes report zero/false; checked
    // output-parameter queries leave the destination unchanged on failure.
    [[nodiscard]] std::size_t active_key_count() const noexcept;
    [[nodiscard]] std::size_t active_key_count(Manual manual) const noexcept;
    [[nodiscard]] bool key_down(Manual manual, std::uint32_t midi_note) const noexcept;
    // Checked control queries require preparation. drawbar_position returns the
    // selected bank's retained position, including while its route is cancelled.
    [[nodiscard]] bool drawbar_position(Manual manual, std::size_t index,
                                        std::uint8_t& destination) const noexcept;
    [[nodiscard]] bool bank_drawbar_position(Manual manual, DrawbarBank bank,
                                             std::size_t index,
                                             std::uint8_t& destination) const noexcept;
    [[nodiscard]] bool selected_bank(Manual manual, DrawbarBank& destination) const noexcept;
    [[nodiscard]] bool route_enabled(Manual manual, bool& destination) const noexcept;
    [[nodiscard]] double expression() const noexcept { return controls_.expression(); }
    [[nodiscard]] bool source_phase_turns(ToneId id, double& destination) const noexcept;

    // Copied musical controls only, not a DSP checkpoint. Same-thread or stopped
    // access only. Restore requires preparation and validates before mutation;
    // rejection preserves all state, and success preserves keys/phases/clock.
    [[nodiscard]] ControlSnapshot controls_snapshot() const noexcept { return controls_.snapshot(); }
    [[nodiscard]] bool restore_controls(const ControlSnapshot& snapshot) noexcept;

private:
    [[nodiscard]] Status preflight(std::uint32_t frames,
                                    std::span<float> mono_output,
                                    std::span<const Event> events) const noexcept;
    void apply_event(const Event& event) noexcept;
    void rebuild_coefficients() noexcept;

    RuntimeProfile profile_{};
    ProcessSpec spec_{};
    TonewheelBank source_bank_{};
    std::array<std::array<bool, kManualKeyCount>, kManualCount> held_keys_{};
    ControlState controls_{};
    std::array<double, kToneSourceCount> coefficients_{};
    std::uint64_t frame_clock_{0};
    bool coefficients_dirty_{false};
    bool prepared_{false};
};

} // namespace hammond
