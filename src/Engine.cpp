#include "hammond/Engine.h"

#include <cmath>
#include <limits>

namespace hammond {
namespace {

[[nodiscard]] bool is_integer_in_range(double value, double maximum) noexcept {
    return value >= 0.0 && value <= maximum && std::trunc(value) == value;
}

[[nodiscard]] bool valid_event_payload(const Event& event) noexcept {
    if (!is_valid_manual(event.manual) || !std::isfinite(event.value)) {
        return false;
    }
    switch (event.type) {
    case EventType::NoteOn:
        return is_valid_manual_midi_note(event.index) &&
               is_integer_in_range(event.value, 127.0);
    case EventType::NoteOff:
        return is_valid_manual_midi_note(event.index) && event.value == 0.0;
    case EventType::Drawbar:
        return event.index < kDrawbarCount && is_integer_in_range(event.value, 8.0);
    case EventType::Expression:
        return event.index == 0 && event.value >= 0.0 && event.value <= 1.0;
    case EventType::AllNotesOff:
        return event.index == 0 && event.value == 0.0;
    }
    return false;
}

} // namespace

Status Engine::prepare(const RuntimeProfile& profile, const ProcessSpec& spec) noexcept {
    if (!is_supported_sample_rate(spec.sample_rate) || spec.max_block_frames == 0 ||
        spec.max_block_frames > kHardMaxBlockFrames) {
        return Status::InvalidSpec;
    }

    // All fallible validation occurs in a local bank before replacing state.
    // Both the bank and profile are fixed-size values; this path allocates nothing.
    TonewheelBank candidate_bank;
    const Status status = candidate_bank.prepare(profile, spec.sample_rate, spec.seed);
    if (status != Status::Ok) {
        return status;
    }

    profile_ = profile;
    spec_ = spec;
    source_bank_ = candidate_bank;
    held_keys_ = {};
    drawbars_ = {};
    coefficients_.fill(0.0);
    expression_ = 1.0;
    frame_clock_ = spec.initial_frame;
    coefficients_dirty_ = false;
    prepared_ = true;
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
            event.offset < previous_offset || !valid_event_payload(event)) {
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

        // Sources advance through silence and disconnected output alike. Every
        // branch referencing a tone consumes this one shared sample of that tone.
        source_bank_.process_frame(source_samples);
        if (!mono_output.empty()) {
            double mixed = 0.0;
            for (std::size_t tone = 0; tone < kToneSourceCount; ++tone) {
                mixed += coefficients_[tone] * source_samples[tone];
            }
            mono_output[frame] = static_cast<float>(mixed * profile_.output_gain * expression_);
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
    case EventType::NoteOff: {
        const auto key = static_cast<std::size_t>(event.index - kMinManualMidiNote);
        const bool down = event.type == EventType::NoteOn && event.value != 0.0;
        if (held_keys_[manual][key] != down) {
            held_keys_[manual][key] = down;
            coefficients_dirty_ = true;
        }
        break;
    }
    case EventType::Drawbar: {
        const auto position = static_cast<std::uint8_t>(event.value);
        if (drawbars_[manual][event.index] != position) {
            drawbars_[manual][event.index] = position;
            coefficients_dirty_ = true;
        }
        break;
    }
    case EventType::Expression:
        expression_ = event.value;
        break;
    case EventType::AllNotesOff:
        for (auto& down : held_keys_[manual]) {
            if (down) {
                down = false;
                coefficients_dirty_ = true;
            }
        }
        break;
    }
}

void Engine::rebuild_coefficients() noexcept {
    coefficients_.fill(0.0);
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        for (std::size_t key = 0; key < kManualKeyCount; ++key) {
            if (!held_keys_[manual][key]) {
                continue;
            }
            for (std::size_t drawbar = 0; drawbar < kDrawbarCount; ++drawbar) {
                const auto tone = static_cast<std::size_t>(profile_.manual_map[key][drawbar]) - 1;
                const auto position = static_cast<std::size_t>(drawbars_[manual][drawbar]);
                coefficients_[tone] += profile_.drawbar_gains[position];
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
    if (!prepared_ || !is_valid_manual(manual) || index >= kDrawbarCount) {
        return false;
    }
    destination = drawbars_[static_cast<std::size_t>(manual)][index];
    return true;
}

bool Engine::source_phase_turns(ToneId id, double& destination) const noexcept {
    return source_bank_.phase_turns(id, destination);
}

} // namespace hammond
