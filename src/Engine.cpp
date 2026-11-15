#include "hammond/Engine.h"

#include <cassert>
#include <cmath>
#include <limits>

namespace hammond {
namespace {

[[nodiscard]] bool is_integer_in_range(double value, double maximum) noexcept {
    return value >= 0.0 && value <= maximum && std::trunc(value) == value;
}

[[nodiscard]] bool upper_percussion_eligible(const ControlSnapshot& controls) noexcept {
    return controls.percussion.enabled && controls.route_enabled[0] &&
           controls.fixed_registrations[0] == FixedRegistration::None &&
           controls.selected_banks[0] == DrawbarBank::B;
}

[[nodiscard]] bool valid_event_payload(const Event& event, ContactMode mode) noexcept {
    if (!is_valid_manual(event.manual) || !std::isfinite(event.value)) {
        return false;
    }
    switch (event.type) {
    case EventType::NoteOn:
        return is_valid_manual_midi_note(event.index) &&
               is_integer_in_range(event.value, 127.0);
    case EventType::NoteOff:
        return is_valid_manual_midi_note(event.index) && event.value == 0.0;
    case EventType::KeyPosition:
        return is_valid_manual_midi_note(event.index) &&
               event.value >= 0.0 && event.value <= 1.0 &&
               (mode == ContactMode::LinearTravel ||
                event.value == 0.0 || event.value == 1.0);
    case EventType::Drawbar:
        return event.index < kDrawbarCount && is_integer_in_range(event.value, 8.0);
    case EventType::Expression:
        return event.index == 0 && event.value >= 0.0 && event.value <= 1.0;
    case EventType::AllNotesOff:
        return event.index == 0 && event.value == 0.0;
    case EventType::BankDrawbar:
        return event.index < kDrawbarBankCount * kDrawbarCount &&
               is_integer_in_range(event.value, 8.0);
    case EventType::SelectBank:
        return event.index == 0 && is_integer_in_range(event.value, 1.0);
    case EventType::SelectPreset:
        return event.index == 0 && is_integer_in_range(event.value, 11.0);
    case EventType::Cancel:
        return event.index == 0 && event.value == 0.0;
    case EventType::Percussion:
        return event.manual == Manual::Upper && event.index < 4 &&
               is_integer_in_range(event.value, 1.0);
    case EventType::PedalOn:
        return event.manual == Manual::Lower && is_valid_pedal_id(PedalId{event.index}) &&
               is_integer_in_range(event.value, 127.0);
    case EventType::PedalOff:
        return event.manual == Manual::Lower && is_valid_pedal_id(PedalId{event.index}) &&
               event.value == 0.0;
    case EventType::PedalDrawbar:
        return event.manual == Manual::Lower && event.index < kPedalDrawbarCount &&
               is_integer_in_range(event.value, 8.0);
    case EventType::PedalAllNotesOff:
        return event.manual == Manual::Lower && event.index == 0 && event.value == 0.0;
    }
    return false;
}

} // namespace

Status Engine::prepare(const RuntimeProfile& profile, const ProcessSpec& spec) noexcept {
    return prepare(profile, spec, make_legacy_console_model());
}

Status Engine::prepare(const RuntimeProfile& profile, const ProcessSpec& spec,
                       const ConsoleModel& console_model) noexcept {
    if (!is_supported_sample_rate(spec.sample_rate) || spec.max_block_frames == 0 ||
        spec.max_block_frames > kHardMaxBlockFrames) {
        return Status::InvalidSpec;
    }

    const Status console_status = validate_console_model(console_model, spec.sample_rate);
    if (console_status != Status::Ok) {
        return console_status;
    }

    // Every fallible preparation occurs in local, value-owned candidates before
    // any installed state changes. No candidate retains caller-owned memory.
    TonewheelBank candidate_bank;
    const Status status = candidate_bank.prepare(profile, spec.sample_rate, spec.seed);
    if (status != Status::Ok) {
        return status;
    }
    ContactBank candidate_contacts;
    const Status contact_status = candidate_contacts.prepare(console_model.contacts,
                                                             spec.sample_rate);
    if (contact_status != Status::Ok) {
        return contact_status;
    }
    PercussionState candidate_percussion;
    const Status percussion_status = candidate_percussion.prepare(console_model.percussion,
                                                                  spec.sample_rate);
    if (percussion_status != Status::Ok) {
        return percussion_status;
    }
    PedalBusKernel candidate_pedals;
    const Status pedal_status = candidate_pedals.prepare(compiled_pedal_routes(),
                                                        nominal_pedal_reference_weights());
    if (pedal_status != Status::Ok) {
        return pedal_status;
    }

    profile_ = profile;
    spec_ = spec;
    source_bank_ = candidate_bank;
    source_leakage_ = {};
    source_leakage_configuration_ = {};
    contact_bank_ = candidate_contacts;
    percussion_state_ = candidate_percussion;
    pedal_kernel_ = candidate_pedals;
    held_keys_ = {};
    held_pedals_ = {};
    pedal_frame_ = {};
    controls_ = ControlState{};
    coefficients_.fill(0.0);
    percussion_coefficients_.fill(0.0);
    frame_clock_ = spec.initial_frame;
    percussion_eligible_ = false;
    coefficients_dirty_ = false;
    prepared_ = true;
    return Status::Ok;
}

Status Engine::set_source_leakage(const SourceLeakage& prepared_leakage,
                                 double input_gain) noexcept {
    if (!prepared_) {
        return Status::NotPrepared;
    }
    if (!std::isfinite(input_gain) || input_gain < 0.0 || input_gain > 1.0) {
        return Status::InvalidSpec;
    }
    if (!prepared_leakage.prepared()) {
        return Status::InvalidProfile;
    }

    const auto edge_count = prepared_leakage.edge_count();
    const double row_sum = prepared_leakage.max_row_absolute_gain_sum();
    double guarded_bound = input_gain;
    if (edge_count != 0) {
        if (input_gain == 0.0) {
            guarded_bound = 0.0;
        } else {
            // Preserve this grouping. The relative reserve encloses canonical
            // row/product/addition rounding; the absolute allowance also covers
            // gradual underflow. Outward rounding is part of the admission.
            const double row_bound = (1.0 + row_sum) +
                (64.0 * std::numeric_limits<double>::epsilon());
            const double product_bound = input_gain * row_bound;
            guarded_bound = std::nextafter(
                product_bound + (16.0 * std::numeric_limits<double>::denorm_min()),
                std::numeric_limits<double>::infinity());
        }
    }
    if (!std::isfinite(guarded_bound) || guarded_bound > 1.0) {
        return Status::InvalidSpec;
    }

    // No mutation precedes admission. All storage is fixed and value-owned;
    // even the last pedal diagnostic remains the actual previously heard frame.
    source_leakage_ = prepared_leakage;
    source_leakage_configuration_ = {true, input_gain, edge_count, row_sum, guarded_bound};
    return Status::Ok;
}

Status Engine::clear_source_leakage() noexcept {
    if (!prepared_) {
        return Status::NotPrepared;
    }
    if (source_leakage_configuration_.configured) {
        source_leakage_ = {};
        source_leakage_configuration_ = {};
    }
    return Status::Ok;
}

Status Engine::reconfigure_sample_rate(double sample_rate) noexcept {
    if (!prepared_) {
        return Status::NotPrepared;
    }
    if (!is_supported_sample_rate(sample_rate)) {
        return Status::InvalidSpec;
    }
    if (sample_rate == spec_.sample_rate) {
        return Status::Ok;
    }

    const Status profile_status = validate_runtime_profile(profile_, sample_rate);
    if (profile_status != Status::Ok) {
        return profile_status;
    }

    // Every fallible transition acts on an owned candidate. In particular,
    // contact trajectories and readiness cannot change if a later module fails.
    auto candidate_sources = source_bank_;
    const Status source_status = candidate_sources.reconfigure_sample_rate(sample_rate);
    if (source_status != Status::Ok) {
        return source_status;
    }
    auto candidate_contacts = contact_bank_;
    const Status contact_status = candidate_contacts.reconfigure_sample_rate(sample_rate);
    if (contact_status != Status::Ok) {
        return contact_status;
    }
    auto candidate_percussion = percussion_state_;
    const Status percussion_status = candidate_percussion.reconfigure_sample_rate(sample_rate);
    if (percussion_status != Status::Ok) {
        return percussion_status;
    }

    source_bank_ = candidate_sources;
    contact_bank_ = candidate_contacts;
    percussion_state_ = candidate_percussion;
    spec_.sample_rate = sample_rate;
    // Routing, source amplitudes and current contact connections are unchanged;
    // both coefficient arrays and their existing dirty/eligibility flags remain
    // valid. Pedal routing/voice has no rate-dependent state. Its contacts and
    // last-rendered diagnostic retain their history, including the old rate tag.
    // Preserve all other ProcessSpec fields and the independent clock.
    return Status::Ok;
}

Status Engine::preflight(std::uint32_t frames, std::span<float> mono_output,
                          std::span<const Event> events) const noexcept {
    if (!prepared_) {
        return Status::NotPrepared;
    }
    if (frames > spec_.max_block_frames) {
        return Status::BlockTooLarge;
    }
    if (!mono_output.empty() && mono_output.size() < frames) {
        return Status::InvalidBuffer;
    }
    if (events.size() > kMaxEventsPerBlock) {
        return Status::TooManyEvents;
    }
    if (frames > std::numeric_limits<std::uint64_t>::max() - frame_clock_) {
        return Status::TimelineOverflow;
    }

    std::uint32_t previous_offset = 0;
    for (const Event& event : events) {
        if ((frames == 0 ? event.offset != 0 : event.offset >= frames) ||
            event.offset < previous_offset ||
            !valid_event_payload(event, contact_bank_.mode())) {
            return Status::InvalidEvent;
        }
        previous_offset = event.offset;
    }
    return Status::Ok;
}

ProcessResult Engine::process(std::uint32_t frames, std::span<float> mono_output,
                              std::span<const Event> events) noexcept {
    const Status status = preflight(frames, mono_output, events);
    if (status != Status::Ok) {
        return ProcessResult{status, 0};
    }

    if (frames == 0) {
        for (const Event& event : events) {
            apply_event(event);
        }
        return ProcessResult{Status::Ok, static_cast<std::uint32_t>(events.size())};
    }

    std::array<double, kToneSourceCount> source_samples{};
    std::size_t next_event = 0;
    for (std::uint32_t frame = 0; frame < frames; ++frame) {
        while (next_event < events.size() && events[next_event].offset == frame) {
            apply_event(events[next_event]);
            ++next_event;
        }
        // Same-offset events are dispatched in supplied order. At most one
        // complete routing scan follows the cluster before its sample is mixed.
        if (coefficients_dirty_) {
            rebuild_coefficients();
        }

        const auto percussion_settings = controls_.percussion_settings();
        bool physical_detector = false;
        if (percussion_eligible_) {
            (void)contact_bank_.any_closed(Manual::Upper, kDrawbarCount - 1, physical_detector);
        }
        const bool routed_detector = percussion_eligible_ && physical_detector;

        // Sources advance through silence and disconnected output alike. Every
        // branch referencing a tone consumes this one shared sample of that tone.
        source_bank_.process_frame(source_samples);
        // This is the single source-field boundary: any future selected source
        // bank must emit its bounded frame above, before this shared insertion.
        // Default and explicit empty/gain-one paths perform no new arithmetic.
        if (source_leakage_configuration_.configured &&
            (source_leakage_configuration_.edge_count != 0 ||
             source_leakage_configuration_.input_gain != 1.0)) {
            for (double& sample : source_samples) {
                sample *= source_leakage_configuration_.input_gain;
            }
            if (source_leakage_configuration_.edge_count != 0) {
                [[maybe_unused]] const auto leakage_status =
                    source_leakage_.process_frame(source_samples, source_samples);
                assert(leakage_status == Status::Ok);
            }
        }
        // Source preparation guarantees [-1,1]; optional installation's outward
        // headroom bound preserves that exact pedal domain. Owned unit weights
        // and fixed nominal controls then guarantee both pedal operations below.
        // These invariant checks never introduce a partial-block rejection.
        // Compute even with no connected output, so the last-frame diagnostic
        // describes the same actual source sample regardless of output wiring.
        PedalRenderDiagnostics rendered_pedal;
        rendered_pedal.valid = true;
        rendered_pedal.frame = frame_clock_ + frame;
        rendered_pedal.sample_rate = spec_.sample_rate;
        rendered_pedal.positions = controls_.pedal_drawbar_positions();
        [[maybe_unused]] const auto pedal_status =
            pedal_kernel_.render_frame(source_samples, rendered_pedal.buses);
        assert(pedal_status == Status::Ok);
        [[maybe_unused]] const auto voice_status = render_nominal_pedal_voice(
            rendered_pedal.buses, rendered_pedal.positions, rendered_pedal.voice);
        assert(voice_status == Status::Ok);
        pedal_frame_ = rendered_pedal;
        if (!mono_output.empty()) {
            double mixed = 0.0;
            for (std::size_t tone = 0; tone < kToneSourceCount; ++tone) {
                mixed += coefficients_[tone] * source_samples[tone];
            }
            if (percussion_eligible_) {
                double harmonic = 0.0;
                for (std::size_t tone = 0; tone < kToneSourceCount; ++tone) {
                    harmonic += percussion_coefficients_[tone] * source_samples[tone];
                }
                mixed += harmonic * percussion_state_.gain(percussion_settings);
            }
            // Preserve the complete legacy arithmetic, including signed zero,
            // when the separate lower-path pedal contribution is inaudible.
            if (rendered_pedal.voice.output != 0.0) {
                mixed += rendered_pedal.voice.output;
            }
            mono_output[frame] =
                static_cast<float>(mixed * profile_.output_gain * controls_.expression());
        }

        // Audio used q[n] and the current contact connections. No note event or
        // routing edit can synthesize elapsed recovery time. Both histories also
        // advance when no output is connected; source_bank already advanced once.
        (void)percussion_state_.advance_frame(routed_detector, percussion_settings);
        if (contact_bank_.advance_frame()) {
            coefficients_dirty_ = true;
        }
    }

    frame_clock_ += frames;
    return ProcessResult{Status::Ok, static_cast<std::uint32_t>(events.size())};
}

void Engine::apply_event(const Event& event) noexcept {
    // The full call has already been validated; enum and index conversions are
    // safe here and cannot create a partially accepted process request.
    const auto manual = static_cast<std::size_t>(event.manual);
    switch (event.type) {
    case EventType::NoteOn:
    case EventType::NoteOff:
    case EventType::KeyPosition: {
        const auto key = static_cast<std::size_t>(event.index - kMinManualMidiNote);
        const double target = event.type == EventType::KeyPosition ? event.value :
            (event.type == EventType::NoteOn && event.value != 0.0 ? 1.0 : 0.0);
        held_keys_[manual][key] = target > 0.0;
        double previous_target = 0.0;
        (void)contact_bank_.position_target(event.manual, event.index, previous_target);
        // Compare the actual target, not its held-key Boolean: a positive partial
        // hold must still respond to a subsequent full NoteOn. Equal targets leave
        // the existing trajectory segment and all contact histories untouched.
        if (previous_target != target) {
            (void)contact_bank_.set_position_target(event.manual, event.index, target);
            coefficients_dirty_ = true;
        }
        break;
    }
    case EventType::Drawbar: {
        const auto position = static_cast<std::uint8_t>(event.value);
        std::uint8_t previous = 0;
        (void)controls_.drawbar_position(event.manual, event.index, previous);
        if (previous != position) {
            (void)controls_.set_drawbar(event.manual, event.index, position);
            coefficients_dirty_ = true;
        }
        break;
    }
    case EventType::Expression:
        (void)controls_.set_expression(event.value);
        break;
    case EventType::AllNotesOff:
        for (auto& down : held_keys_[manual]) {
            down = false;
        }
        // A key may have a released target while contacts are still travelling.
        // The explicit panic must open those contacts too, without resetting q.
        (void)contact_bank_.panic_manual(event.manual);
        coefficients_dirty_ = true;
        break;
    case EventType::BankDrawbar: {
        const auto bank = static_cast<DrawbarBank>(event.index / kDrawbarCount);
        const auto drawbar = static_cast<std::size_t>(event.index) % kDrawbarCount;
        const auto position = static_cast<std::uint8_t>(event.value);
        std::uint8_t previous = 0;
        (void)controls_.bank_drawbar_position(event.manual, bank, drawbar, previous);
        if (previous != position) {
            (void)controls_.set_bank_drawbar(event.manual, bank, drawbar, position);
            coefficients_dirty_ = true;
        }
        break;
    }
    case EventType::SelectBank: {
        const auto bank = static_cast<DrawbarBank>(static_cast<std::uint8_t>(event.value));
        const auto previous = controls_.snapshot();
        if (previous.selected_banks[manual] != bank || !previous.route_enabled[manual] ||
            previous.fixed_registrations[manual] != FixedRegistration::None) {
            (void)controls_.select_bank(event.manual, bank);
            coefficients_dirty_ = true;
        }
        break;
    }
    case EventType::SelectPreset: {
        const auto selection =
            static_cast<PresetSelection>(static_cast<std::uint8_t>(event.value));
        const auto previous = controls_.snapshot();
        (void)controls_.select_preset(event.manual, selection);
        const auto current = controls_.snapshot();
        if (previous.selected_banks[manual] != current.selected_banks[manual] ||
            previous.fixed_registrations[manual] != current.fixed_registrations[manual] ||
            previous.route_enabled[manual] != current.route_enabled[manual]) {
            coefficients_dirty_ = true;
        }
        break;
    }
    case EventType::Cancel: {
        bool enabled = false;
        (void)controls_.route_enabled(event.manual, enabled);
        if (enabled) {
            (void)controls_.cancel(event.manual);
            coefficients_dirty_ = true;
        }
        break;
    }
    case EventType::Percussion: {
        auto settings = controls_.percussion_settings();
        const auto selection = static_cast<std::uint8_t>(event.value);
        switch (event.index) {
        case 0: settings.enabled = selection != 0; break;
        case 1: settings.harmonic = static_cast<PercussionHarmonic>(selection); break;
        case 2: settings.volume = static_cast<PercussionVolume>(selection); break;
        case 3: settings.decay = static_cast<PercussionDecay>(selection); break;
        default: break; // Full preflight has already excluded this case.
        }
        if (settings != controls_.percussion_settings()) {
            (void)controls_.set_percussion_settings(settings);
            coefficients_dirty_ = true;
        }
        break;
    }
    case EventType::PedalOn:
    case EventType::PedalOff:
        apply_pedal(PedalId{event.index},
                    event.type == EventType::PedalOn && event.value != 0.0);
        break;
    case EventType::PedalDrawbar:
        (void)controls_.set_pedal_drawbar(event.index, static_cast<std::uint8_t>(event.value));
        break;
    case EventType::PedalAllNotesOff: {
        std::array<PedalContactEdit, kPedalContactPositionCount> edits{};
        for (std::size_t position = 0; position < edits.size(); ++position) {
            edits[position] = {
                PedalId{static_cast<std::uint8_t>(position / kPedalContactCount + 1)},
                static_cast<std::uint8_t>(position % kPedalContactCount), false};
        }
        (void)pedal_kernel_.apply_contacts(edits);
        held_pedals_.fill(false);
        break;
    }
    }
}

void Engine::apply_pedal(PedalId pedal, bool closed) noexcept {
    const auto index = static_cast<std::size_t>(pedal.value) - 1;
    if (held_pedals_[index] == closed) return;
    std::array<PedalContactEdit, kPedalContactCount> edits{};
    for (std::size_t contact = 0; contact < edits.size(); ++contact) {
        edits[contact] = {pedal, static_cast<std::uint8_t>(contact), closed};
    }
    (void)pedal_kernel_.apply_contacts(edits);
    held_pedals_[index] = closed;
}

void Engine::rebuild_coefficients() noexcept {
    coefficients_.fill(0.0);
    percussion_coefficients_.fill(0.0);
    const auto controls = controls_.snapshot();
    percussion_eligible_ = upper_percussion_eligible(controls);
    const std::size_t harmonic_contact =
        controls.percussion.harmonic == PercussionHarmonic::Second ? 3 : 4;
    const double upper_sustain_gain = percussion_state_.upper_sustain_gain(controls.percussion);
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        if (!controls.route_enabled[manual]) {
            continue;
        }
        const auto bank = static_cast<std::size_t>(controls.selected_banks[manual]);
        auto positions = controls.drawbars[manual][bank];
        if (controls.fixed_registrations[manual] != FixedRegistration::None) {
            // Resolve once per enabled manual. The installed snapshot is valid,
            // and the immutable row uses the same nominal profile gain indices.
            (void)fixed_registration_positions(static_cast<Manual>(manual),
                                                controls.fixed_registrations[manual], positions);
        }
        for (std::size_t key = 0; key < kManualKeyCount; ++key) {
            const auto midi_note = static_cast<std::uint32_t>(key) + kMinManualMidiNote;
            for (std::size_t drawbar = 0; drawbar < kDrawbarCount; ++drawbar) {
                bool closed = false;
                (void)contact_bank_.contact_closed(static_cast<Manual>(manual), midi_note,
                                                   drawbar, closed);
                if (!closed) {
                    continue;
                }
                const auto tone = static_cast<std::size_t>(profile_.manual_map[key][drawbar]) - 1;
                const auto position = static_cast<std::size_t>(positions[drawbar]);
                if (manual == 0 && percussion_eligible_) {
                    if (drawbar == harmonic_contact) {
                        // Each currently connected branch shares its existing
                        // source, independent of sustained drawbar position and
                        // physical keying contact. No extra oscillator/return.
                        percussion_coefficients_[tone] += 1.0;
                    }
                    if (drawbar != kDrawbarCount - 1) {
                        coefficients_[tone] += profile_.drawbar_gains[position] * upper_sustain_gain;
                    }
                } else {
                    // Preserve the legacy order and exact arithmetic when the
                    // nominal percussion routing is ineligible or disabled.
                    coefficients_[tone] += profile_.drawbar_gains[position];
                }
            }
        }
    }
    coefficients_dirty_ = false;
}

std::size_t Engine::active_key_count() const noexcept {
    return active_key_count(Manual::Upper) + active_key_count(Manual::Lower);
}

std::size_t Engine::active_key_count(Manual manual) const noexcept {
    if (!is_valid_manual(manual)) {
        return 0;
    }
    std::size_t count = 0;
    for (const bool down : held_keys_[static_cast<std::size_t>(manual)]) {
        if (down) {
            ++count;
        }
    }
    return count;
}

bool Engine::key_down(Manual manual, std::uint32_t midi_note) const noexcept {
    std::size_t key = 0;
    return is_valid_manual(manual) && manual_midi_to_key_index(midi_note, key) &&
           held_keys_[static_cast<std::size_t>(manual)][key];
}

std::size_t Engine::active_pedal_count() const noexcept {
    std::size_t count = 0;
    for (const bool down : held_pedals_) {
        if (down) ++count;
    }
    return count;
}

bool Engine::pedal_down(PedalId pedal) const noexcept {
    std::size_t index = 0;
    return prepared_ && pedal_id_to_index(pedal, index) && held_pedals_[index];
}

bool Engine::pedal_drawbar_position(std::size_t index,
                                    std::uint8_t& destination) const noexcept {
    return prepared_ && controls_.pedal_drawbar_position(index, destination);
}

bool Engine::pedal_contact_closed(PedalId pedal, std::uint32_t contact,
                                  bool& destination) const noexcept {
    return prepared_ && pedal_kernel_.contact_closed(pedal, contact, destination);
}

bool Engine::pedal_contacts_snapshot(PedalContactStates& destination) const noexcept {
    if (!prepared_) return false;
    destination = pedal_kernel_.contacts_snapshot();
    return true;
}

bool Engine::drawbar_position(Manual manual, std::size_t index,
                              std::uint8_t& destination) const noexcept {
    return prepared_ && controls_.drawbar_position(manual, index, destination);
}

bool Engine::bank_drawbar_position(Manual manual, DrawbarBank bank, std::size_t index,
                                   std::uint8_t& destination) const noexcept {
    return prepared_ && controls_.bank_drawbar_position(manual, bank, index, destination);
}

bool Engine::selected_bank(Manual manual, DrawbarBank& destination) const noexcept {
    return prepared_ && controls_.selected_bank(manual, destination);
}

bool Engine::selected_preset(Manual manual, PresetSelection& destination) const noexcept {
    return prepared_ && controls_.selected_preset(manual, destination);
}

bool Engine::route_enabled(Manual manual, bool& destination) const noexcept {
    return prepared_ && controls_.route_enabled(manual, destination);
}

bool Engine::restore_controls(const ControlSnapshot& snapshot) noexcept {
    if (!prepared_ || !controls_.restore(snapshot)) {
        return false;
    }
    coefficients_dirty_ = true;
    return true;
}

bool Engine::source_phase_turns(ToneId id, double& destination) const noexcept {
    return source_bank_.phase_turns(id, destination);
}

bool Engine::contact_snapshot(Manual manual, std::uint32_t midi_note,
                              ContactKeySnapshot& destination) const noexcept {
    return prepared_ && contact_bank_.key_snapshot(manual, midi_note, destination);
}

PercussionRoutingDiagnostics Engine::percussion_diagnostics() const noexcept {
    if (!prepared_) {
        return {};
    }
    // Derive routes from current controls rather than the audio coefficient
    // cache: zero-frame events and stopped control restoration may dirty it.
    const auto controls = controls_.snapshot();
    bool physical_detector = false;
    (void)contact_bank_.any_closed(Manual::Upper, kDrawbarCount - 1, physical_detector);
    const bool eligible = upper_percussion_eligible(controls);
    return {true, percussion_state_.readiness(), physical_detector, eligible,
            eligible && physical_detector,
            eligible ? percussion_state_.gain(controls.percussion) : 0.0,
            eligible ? percussion_state_.upper_sustain_gain(controls.percussion) : 1.0};
}

} // namespace hammond
