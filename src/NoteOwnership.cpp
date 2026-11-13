#include "hammond/NoteOwnership.h"

namespace hammond {
namespace {

[[nodiscard]] bool valid_payload(const HostNoteEvent& event) noexcept {
    if (event.bus >= kHostInputBusCount || event.channel >= kHostInputChannelCount) {
        return false;
    }
    switch (event.kind) {
    case HostNoteKind::On:
        return is_valid_manual_midi_note(event.midi_note) &&
               event.velocity <= 127 && event.note_id >= -1;
    case HostNoteKind::Off:
        return is_valid_manual_midi_note(event.midi_note) &&
               event.velocity == 0 && event.note_id >= -1;
    case HostNoteKind::AllNotesOff:
        return event.midi_note == 0 && event.velocity == 0 && event.note_id == -1;
    }
    return false;
}

} // namespace

NoteOwnershipResult NoteOwnership::translate(
    std::uint32_t frames, std::span<const HostNoteEvent> input,
    std::span<Event> output) noexcept {
    if (frames > kHardMaxBlockFrames) {
        return {Status::BlockTooLarge, 0, 0};
    }
    if (input.size() > kMaxEventsPerBlock) {
        return {Status::TooManyEvents, 0, 0};
    }
    std::uint32_t previous_offset = 0;
    for (const auto& event : input) {
        if ((frames == 0 ? event.offset != 0 : event.offset >= frames) ||
            event.offset < previous_offset || !valid_payload(event)) {
            return {Status::InvalidEvent, 0, 0};
        }
        previous_offset = event.offset;
    }

    // Identity conflicts and actual output/owner capacities depend on preceding
    // same-call commands. Apply them only to a bounded candidate. Neither the
    // caller's output nor the installed owners are touched before all succeed.
    NoteOwnership candidate = *this;
    std::array<Event, kMaxEventsPerBlock> emitted{};
    std::size_t produced = 0;
    const std::size_t output_limit =
        output.size() < emitted.size() ? output.size() : emitted.size();
    const auto emit = [&](std::uint32_t offset, EventType type, Manual manual,
                          std::uint8_t note, std::uint8_t velocity) noexcept {
        if (produced == output_limit) {
            return false;
        }
        emitted[produced] = Event{offset, type, manual, note,
                                 static_cast<double>(velocity)};
        ++produced;
        return true;
    };

    for (const auto& event : input) {
        if (event.kind == HostNoteKind::AllNotesOff) {
            // Retire this channel's owners in insertion order. A single pass
            // compacts survivors; only the last physical owner emits a release.
            const std::size_t old_count = candidate.owner_count_;
            std::size_t kept = 0;
            for (std::size_t index = 0; index < old_count; ++index) {
                const auto owner = candidate.owners_[index];
                if (owner.bus == event.bus && owner.channel == event.channel) {
                    const auto manual = static_cast<std::size_t>(owner.manual);
                    const auto key = static_cast<std::size_t>(
                        owner.midi_note - kMinManualMidiNote);
                    auto& count = candidate.physical_counts_[manual][key];
                    --count;
                    if (count == 0 && !emit(event.offset, EventType::NoteOff,
                                            owner.manual, owner.midi_note, 0)) {
                        return {Status::TooManyEvents, 0, 0};
                    }
                } else {
                    candidate.owners_[kept] = owner;
                    ++kept;
                }
            }
            for (std::size_t index = kept; index < old_count; ++index) {
                candidate.owners_[index] = {};
            }
            candidate.owner_count_ = kept;
            continue;
        }

        const bool press = event.kind == HostNoteKind::On && event.velocity != 0;
        if (press) {
            if (event.note_id >= 0) {
                const std::size_t existing = candidate.find_identified(event);
                if (existing != candidate.owner_count_) {
                    if (candidate.owners_[existing].midi_note != event.midi_note) {
                        return {Status::InvalidEvent, 0, 0};
                    }
                    // An identified duplicate retains its original destination,
                    // including if the bus route changed since its first On.
                    continue;
                }
            }
            if (candidate.owner_count_ == kMaxNoteOwners) {
                return {Status::TooManyEvents, 0, 0};
            }
            const Manual destination = candidate.routes_[event.bus];
            const auto manual = static_cast<std::size_t>(destination);
            const auto key = static_cast<std::size_t>(event.midi_note - kMinManualMidiNote);
            auto& count = candidate.physical_counts_[manual][key];
            if (count == 0 && !emit(event.offset, EventType::NoteOn, destination,
                                    event.midi_note, event.velocity)) {
                return {Status::TooManyEvents, 0, 0};
            }
            ++count;
            candidate.owners_[candidate.owner_count_] = NoteOwnerSnapshot{
                event.bus, event.channel, event.midi_note, event.note_id, destination};
            ++candidate.owner_count_;
            continue;
        }

        const std::size_t existing = event.note_id >= 0 ? candidate.find_identified(event)
                                                       : candidate.find_unidentified(event);
        if (existing == candidate.owner_count_) {
            continue;
        }
        const auto owner = candidate.owners_[existing];
        if (owner.midi_note != event.midi_note) {
            return {Status::InvalidEvent, 0, 0};
        }
        const auto manual = static_cast<std::size_t>(owner.manual);
        const auto key = static_cast<std::size_t>(owner.midi_note - kMinManualMidiNote);
        auto& count = candidate.physical_counts_[manual][key];
        --count;
        if (count == 0 && !emit(event.offset, EventType::NoteOff,
                                owner.manual, owner.midi_note, 0)) {
            return {Status::TooManyEvents, 0, 0};
        }
        candidate.erase_owner(existing);
    }

    for (std::size_t index = 0; index < produced; ++index) {
        output[index] = emitted[index];
    }
    *this = candidate;
    return {Status::Ok, static_cast<std::uint32_t>(input.size()),
            static_cast<std::uint32_t>(produced)};
}

bool NoteOwnership::set_bus_route(std::uint32_t bus, Manual manual) noexcept {
    if (bus >= kHostInputBusCount || !is_valid_manual(manual)) {
        return false;
    }
    routes_[bus] = manual;
    return true;
}

bool NoteOwnership::set_routes(
    const std::array<Manual, kHostInputBusCount>& routes) noexcept {
    for (const auto manual : routes) {
        if (!is_valid_manual(manual)) {
            return false;
        }
    }
    routes_ = routes;
    return true;
}

bool NoteOwnership::bus_route(std::uint32_t bus, Manual& destination) const noexcept {
    if (bus >= kHostInputBusCount) {
        return false;
    }
    destination = routes_[bus];
    return true;
}

bool NoteOwnership::owner_count(Manual manual, std::uint32_t midi_note,
                                std::size_t& destination) const noexcept {
    std::size_t key = 0;
    if (!is_valid_manual(manual) || !manual_midi_to_key_index(midi_note, key)) {
        return false;
    }
    destination = physical_counts_[static_cast<std::size_t>(manual)][key];
    return true;
}

bool NoteOwnership::owner_snapshot(std::size_t index,
                                  NoteOwnerSnapshot& destination) const noexcept {
    if (index >= owner_count_) {
        return false;
    }
    destination = owners_[index];
    return true;
}

std::size_t NoteOwnership::find_identified(const HostNoteEvent& event) const noexcept {
    for (std::size_t index = 0; index < owner_count_; ++index) {
        const auto& owner = owners_[index];
        if (owner.bus == event.bus && owner.channel == event.channel &&
            owner.note_id == event.note_id) {
            return index;
        }
    }
    return owner_count_;
}

std::size_t NoteOwnership::find_unidentified(const HostNoteEvent& event) const noexcept {
    for (std::size_t index = 0; index < owner_count_; ++index) {
        const auto& owner = owners_[index];
        if (owner.note_id == -1 && owner.bus == event.bus &&
            owner.channel == event.channel && owner.midi_note == event.midi_note) {
            return index;
        }
    }
    return owner_count_;
}

void NoteOwnership::erase_owner(std::size_t index) noexcept {
    for (std::size_t next = index + 1; next < owner_count_; ++next) {
        owners_[next - 1] = owners_[next];
    }
    --owner_count_;
    owners_[owner_count_] = {};
}

} // namespace hammond
