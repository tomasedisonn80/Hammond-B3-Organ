#include "hammond/PedalNoteOwnership.h"

namespace hammond {
namespace {

[[nodiscard]] bool valid_payload(const PedalNoteEvent& event) noexcept {
    if (event.bus >= kPedalInputBusCount || event.channel >= kPedalInputChannelCount) {
        return false;
    }
    switch (event.kind) {
    case PedalNoteKind::On:
        return is_valid_pedal_id(event.pedal) && event.velocity <= 127 &&
               event.note_id >= -1;
    case PedalNoteKind::Off:
        return is_valid_pedal_id(event.pedal) && event.velocity == 0 &&
               event.note_id >= -1;
    case PedalNoteKind::AllNotesOff:
        return event.pedal.value == 0 && event.velocity == 0 && event.note_id == -1;
    }
    return false;
}

} // namespace

PedalNoteOwnershipResult PedalNoteOwnership::translate(
    std::uint32_t frames, std::span<const PedalNoteEvent> input,
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

    // All fallible work targets fixed private values. Caller output and the
    // installed owner set are touched only after the complete sequence succeeds.
    PedalNoteOwnership candidate = *this;
    std::array<Event, kMaxEventsPerBlock> emitted{};
    std::size_t produced = 0;
    const std::size_t output_limit =
        output.size() < emitted.size() ? output.size() : emitted.size();
    const auto emit = [&](std::uint32_t offset, EventType type, PedalId pedal,
                          std::uint8_t velocity) noexcept {
        if (produced == output_limit) {
            return false;
        }
        emitted[produced] = Event{offset, type, Manual::Lower, pedal.value,
                                 static_cast<double>(velocity)};
        ++produced;
        return true;
    };

    for (const auto& event : input) {
        if (event.kind == PedalNoteKind::AllNotesOff) {
            // Stable compaction preserves every surviving origin's insertion
            // order. Release a physical pedal only when its last owner retires.
            const std::size_t old_count = candidate.owner_count_;
            std::size_t kept = 0;
            for (std::size_t index = 0; index < old_count; ++index) {
                const auto owner = candidate.owners_[index];
                if (owner.bus == event.bus && owner.channel == event.channel) {
                    const auto pedal_index = static_cast<std::size_t>(owner.pedal.value) - 1;
                    auto& count = candidate.physical_counts_[pedal_index];
                    --count;
                    if (count == 0 && !emit(event.offset, EventType::PedalOff,
                                            owner.pedal, 0)) {
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

        const bool press = event.kind == PedalNoteKind::On && event.velocity != 0;
        if (press) {
            if (event.note_id >= 0) {
                const std::size_t existing = candidate.find_identified(event);
                if (existing != candidate.owner_count_) {
                    if (candidate.owners_[existing].pedal != event.pedal) {
                        return {Status::InvalidEvent, 0, 0};
                    }
                    continue;
                }
            }
            if (candidate.owner_count_ == kMaxPedalNoteOwners) {
                return {Status::TooManyEvents, 0, 0};
            }
            const auto pedal_index = static_cast<std::size_t>(event.pedal.value) - 1;
            auto& count = candidate.physical_counts_[pedal_index];
            if (count == 0 && !emit(event.offset, EventType::PedalOn,
                                    event.pedal, event.velocity)) {
                return {Status::TooManyEvents, 0, 0};
            }
            ++count;
            candidate.owners_[candidate.owner_count_] =
                PedalOwnerSnapshot{event.bus, event.channel, event.pedal, event.note_id};
            ++candidate.owner_count_;
            continue;
        }

        const std::size_t existing = event.note_id >= 0 ? candidate.find_identified(event)
                                                       : candidate.find_anonymous(event);
        if (existing == candidate.owner_count_) {
            continue;
        }
        const auto owner = candidate.owners_[existing];
        if (owner.pedal != event.pedal) {
            return {Status::InvalidEvent, 0, 0};
        }
        const auto pedal_index = static_cast<std::size_t>(owner.pedal.value) - 1;
        auto& count = candidate.physical_counts_[pedal_index];
        --count;
        if (count == 0 && !emit(event.offset, EventType::PedalOff, owner.pedal, 0)) {
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

bool PedalNoteOwnership::owner_count(PedalId pedal,
                                     std::size_t& destination) const noexcept {
    std::size_t index = 0;
    if (!pedal_id_to_index(pedal, index)) {
        return false;
    }
    destination = physical_counts_[index];
    return true;
}

bool PedalNoteOwnership::owner_snapshot(std::size_t index,
                                       PedalOwnerSnapshot& destination) const noexcept {
    if (index >= owner_count_) {
        return false;
    }
    destination = owners_[index];
    return true;
}

std::size_t PedalNoteOwnership::find_identified(const PedalNoteEvent& event) const noexcept {
    for (std::size_t index = 0; index < owner_count_; ++index) {
        const auto& owner = owners_[index];
        if (owner.bus == event.bus && owner.channel == event.channel &&
            owner.note_id == event.note_id) {
            return index;
        }
    }
    return owner_count_;
}

std::size_t PedalNoteOwnership::find_anonymous(const PedalNoteEvent& event) const noexcept {
    for (std::size_t index = 0; index < owner_count_; ++index) {
        const auto& owner = owners_[index];
        if (owner.note_id == -1 && owner.bus == event.bus &&
            owner.channel == event.channel && owner.pedal == event.pedal) {
            return index;
        }
    }
    return owner_count_;
}

void PedalNoteOwnership::erase_owner(std::size_t index) noexcept {
    for (std::size_t next = index + 1; next < owner_count_; ++next) {
        owners_[next - 1] = owners_[next];
    }
    --owner_count_;
    owners_[owner_count_] = {};
}

} // namespace hammond
