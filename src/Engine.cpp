#include "hammond/Engine.h"

#include <cmath>
#include <limits>

namespace hammond {
namespace {

[[nodiscard]] bool is_integer_in_range(double value, double maximum) noexcept {
    return value >= 0.0 && value <= maximum && std::trunc(value) == value;
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
    case EventType::Cancel:
        return event.index == 0 && event.value == 0.0;
    case EventType::Percussion:
        return event.manual == Manual::Upper && event.index < 4 &&
               is_integer_in_range(event.value, 1.0);
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

    profile_ = profile;
    spec_ = spec;
    source_bank_ = candidate_bank;
    contact_bank_ = candidate_contacts;
    percussion_state_ = candidate_percussion;
    held_keys_ = {};
    controls_ = ControlState{};
    coefficients_.fill(0.0);
    percussion_coefficients_.fill(0.0);
    frame_clock_ = spec.initial_frame;
    percussion_eligible_ = false;
    coefficients_dirty_ = false;
    prepared_ = true;
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
    // valid. Preserve all other ProcessSpec fields and the independent clock.
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
        DrawbarBank previous = DrawbarBank::B;
        bool enabled = false;
        (void)controls_.selected_bank(event.manual, previous);
        (void)controls_.route_enabled(event.manual, enabled);
        if (previous != bank || !enabled) {
            (void)controls_.select_bank(event.manual, bank);
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
    }
}

void Engine::rebuild_coefficients() noexcept {
    coefficients_.fill(0.0);
    percussion_coefficients_.fill(0.0);
    const auto controls = controls_.snapshot();
    percussion_eligible_ = controls.percussion.enabled && controls.route_enabled[0] &&
                           controls.selected_banks[0] == DrawbarBank::B;
    const std::size_t harmonic_contact =
        controls.percussion.harmonic == PercussionHarmonic::Second ? 3 : 4;
    const double upper_sustain_gain = percussion_state_.upper_sustain_gain(controls.percussion);
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        if (!controls.route_enabled[manual]) {
            continue;
        }
        const auto bank = static_cast<std::size_t>(controls.selected_banks[manual]);
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
                const auto position =
                    static_cast<std::size_t>(controls.drawbars[manual][bank][drawbar]);
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
    const bool eligible = controls.percussion.enabled && controls.route_enabled[0] &&
                          controls.selected_banks[0] == DrawbarBank::B;
    return {true, percussion_state_.readiness(), physical_detector, eligible,
            eligible && physical_detector,
            eligible ? percussion_state_.gain(controls.percussion) : 0.0,
            eligible ? percussion_state_.upper_sustain_gain(controls.percussion) : 1.0};
}

} // namespace hammond
