#pragma once

#include "hammond/ControlState.h"
#include "hammond/ConsoleModel.h"
#include "hammond/PedalVoice.h"
#include "hammond/Profile.h"
#include "hammond/TonewheelBank.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <span>

namespace hammond {

struct PercussionRoutingDiagnostics {
    bool prepared{false};
    double readiness{0.0};
    bool physical_detector{false};
    bool eligible{false};
    bool routed_detector{false};
    double gain{0.0};
    double upper_sustain_gain{1.0};

    [[nodiscard]] bool operator==(const PercussionRoutingDiagnostics&) const noexcept = default;
};

// The last actual rendered pedal frame, separate from current controls/contacts.
// Frame is the absolute zero-based sample identity; rate is the rate used then.
// Fresh preparation leaves valid=false. Zero-frame edits, control restores and
// rate changes preserve this historical record until another sample renders.
struct PedalRenderDiagnostics {
    bool valid{false};
    std::uint64_t frame{0};
    double sample_rate{0.0};
    PedalDrawbarPositions positions{};
    PedalBusFrame buses{};
    PedalVoiceFrame voice{};

    [[nodiscard]] bool operator==(const PedalRenderDiagnostics&) const noexcept = default;
};

// Nominal organ: independent contacts, retained manual drawbar banks, one shared
// percussion readiness state, nominal ideal-contact pedals, and one free-running
// source field. Default manual contact
// preparation preserves the legacy immediate key behavior. No measured console,
// scanner, AO-28 or cabinet model is implied.
// Prepare and all diagnostics require stopped or same-processing-thread access;
// no concurrent UI snapshot or live profile publication protocol is provided.
class Engine {
public:
    // Success installs an owned profile and starts a new seeded source field.
    // Initial controls: no keys/pedals, all banks and both pedal mixtures zero,
    // bank B selected, routes enabled,
    // expression one, percussion Off/Second/Normal/Slow, and readiness one.
    // The two-argument overload uses ideal contacts. Any failure preserves the
    // complete previous engine, including contact/readiness histories and clock.
    [[nodiscard]] Status prepare(const RuntimeProfile& profile,
                                 const ProcessSpec& spec) noexcept;
    [[nodiscard]] Status prepare(const RuntimeProfile& profile,
                                 const ProcessSpec& spec,
                                 const ConsoleModel& console_model) noexcept;

    // Stopped or same-processing-thread lifecycle operation; never call it
    // concurrently with processing or diagnostics. Validate the owned source
    // profile and all three rate-dependent module candidates before installing
    // any change. Success preserves controls, keys, current contact positions/
    // targets/connections, readiness, all source phases, caches and frame clock.
    // No sample elapses and no source is reseeded. Only the installed rate and
    // rate-dependent coefficients/trajectory segment bookkeeping change.
    // NotPrepared precedes InvalidSpec; an unsupported source increment reports
    // InvalidProfile. Failure preserves the complete engine and future output.
    // The same rate is an exact no-op. The render clock remains a count of frames,
    // so elapsed seconds across rate changes require an external segment record.
    [[nodiscard]] Status reconfigure_sample_rate(double sample_rate) noexcept;

    // Preflights the entire request. Rejection changes no state or output and
    // consumes no events. Positive calls accept empty (disconnected) output or
    // at least frames samples; extra output samples are untouched. Events use
    // half-open offsets and retain input order for ties. Zero-frame calls apply
    // offset-zero events once without advancing sources, contact travel,
    // readiness or the frame clock. Positive samples render current state before
    // advancing each dynamic module exactly once, even with disconnected output.
    // KeyPosition accepts finite normalized targets in [0,1] on either manual;
    // Ideal contacts accept only 0/1. Any invalid partial target rejects the full
    // call before mutation. Targets are idempotent and preserve contact history;
    // NoteOn commands full press even after a partial hold. Direct key events
    // require coordinated note authority when an ownership adapter is in use.
    [[nodiscard]] ProcessResult process(std::uint32_t frames,
                                        std::span<float> mono_output,
                                        std::span<const Event> events) noexcept;

    [[nodiscard]] std::uint64_t frame_clock() const noexcept { return frame_clock_; }
    [[nodiscard]] bool prepared() const noexcept { return prepared_; }
    // Installed samples per second, or zero before the first successful prepare.
    [[nodiscard]] double sample_rate() const noexcept {
        return prepared_ ? spec_.sample_rate : 0.0;
    }

    // Copied diagnostics only. Invalid manuals/notes report zero/false; checked
    // output-parameter queries leave the destination unchanged on failure.
    // Active/down means target > 0, including partial holds; it does not mean
    // that any or all contacts have closed, or that releasing contacts are open.
    [[nodiscard]] std::size_t active_key_count() const noexcept;
    [[nodiscard]] std::size_t active_key_count(Manual manual) const noexcept;
    [[nodiscard]] bool key_down(Manual manual, std::uint32_t midi_note) const noexcept;
    // Pedals have a distinct identity and count; active_key_count stays manual-
    // only with a maximum of 122. Invalid/unprepared pedal_down reports false.
    [[nodiscard]] std::size_t active_pedal_count() const noexcept;
    [[nodiscard]] bool pedal_down(PedalId pedal) const noexcept;
    [[nodiscard]] bool pedal_drawbar_position(std::size_t index,
                                              std::uint8_t& destination) const noexcept;
    // All 200 independent states are exposed, including the five disconnected
    // positions. Checked queries preserve their destination on invalid input or
    // before preparation. There is no independently editable live contact API.
    [[nodiscard]] bool pedal_contact_closed(PedalId pedal, std::uint32_t contact,
                                           bool& destination) const noexcept;
    [[nodiscard]] bool pedal_contacts_snapshot(PedalContactStates& destination) const noexcept;
    [[nodiscard]] PedalRenderDiagnostics last_pedal_frame() const noexcept {
        return pedal_frame_;
    }
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

    // Current state for the next sample to render. Held-key diagnostics above
    // describe targets, while these contacts may still be releasing. Invalid
    // checked queries preserve their destination. No concurrent UI protocol.
    [[nodiscard]] bool contact_snapshot(Manual manual, std::uint32_t midi_note,
                                         ContactKeySnapshot& destination) const noexcept;
    [[nodiscard]] ContactMode contact_mode() const noexcept { return contact_bank_.mode(); }
    [[nodiscard]] PercussionRoutingDiagnostics percussion_diagnostics() const noexcept;

    // Copied musical controls only, not a DSP checkpoint. Same-thread or stopped
    // access only. Restore requires preparation and validates before mutation;
    // rejection preserves all state, and success preserves keys, contact motion,
    // readiness, source phases and clock. Routing eligibility changes immediately.
    [[nodiscard]] ControlSnapshot controls_snapshot() const noexcept { return controls_.snapshot(); }
    [[nodiscard]] bool restore_controls(const ControlSnapshot& snapshot) noexcept;

private:
    [[nodiscard]] Status preflight(std::uint32_t frames,
                                    std::span<float> mono_output,
                                    std::span<const Event> events) const noexcept;
    void apply_event(const Event& event) noexcept;
    void apply_pedal(PedalId pedal, bool closed) noexcept;
    void rebuild_coefficients() noexcept;

    RuntimeProfile profile_{};
    ProcessSpec spec_{};
    TonewheelBank source_bank_{};
    ContactBank contact_bank_{};
    PercussionState percussion_state_{};
    PedalBusKernel pedal_kernel_{};
    std::array<std::array<bool, kManualKeyCount>, kManualCount> held_keys_{};
    std::array<bool, kPedalCount> held_pedals_{};
    PedalRenderDiagnostics pedal_frame_{};
    ControlState controls_{};
    std::array<double, kToneSourceCount> coefficients_{};
    std::array<double, kToneSourceCount> percussion_coefficients_{};
    std::uint64_t frame_clock_{0};
    bool percussion_eligible_{false};
    bool coefficients_dirty_{false};
    bool prepared_{false};
};

} // namespace hammond
