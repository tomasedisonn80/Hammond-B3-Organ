#include "MidiInput.h"

#include <limits>

namespace hammond::standalone {
namespace {

constexpr std::uint32_t ring_size = static_cast<std::uint32_t>(kMidiInboxCapacity + 1);
constexpr auto maximum_counter = std::numeric_limits<std::uint64_t>::max();

[[nodiscard]] constexpr std::uint32_t next_index(std::uint32_t index) noexcept {
    return index + 1 == ring_size ? 0 : index + 1;
}

[[nodiscard]] constexpr std::uint64_t saturated_sum(std::uint64_t value,
                                                   std::uint64_t amount) noexcept {
    return amount > maximum_counter - value ? maximum_counter : value + amount;
}

void increment(std::uint64_t& counter) noexcept {
    counter = saturated_sum(counter, 1);
}

// Each diagnostic counter has exactly one writer during an active epoch.
// Reset-only counters are changed with both participants quiescent. Atomic
// load/store therefore suffices for concurrent observers, without a retry loop.
void add(std::atomic<std::uint64_t>& counter, std::uint64_t amount = 1) noexcept {
    counter.store(saturated_sum(counter.load(std::memory_order_relaxed), amount),
                  std::memory_order_relaxed);
}

[[nodiscard]] SessionCommand scoped_release(std::size_t division) noexcept {
    if (division == 2) {
        return PerformanceInputEvent{PedalNoteEvent{
            0, PedalNoteKind::AllNotesOff, 0, kMidiOwnerChannels[division],
            PedalId{0}, 0, -1}};
    }
    return PerformanceInputEvent{HostNoteEvent{
        0, HostNoteKind::AllNotesOff, static_cast<std::uint8_t>(division),
        kMidiOwnerChannels[division], 0, 0, -1}};
}

} // namespace

MidiPushResult MidiInbox::push(std::span<const std::uint8_t> bytes,
                               std::uint64_t arrival_ns) noexcept {
    add(received_packets_);
    if (fault_bits_.load(std::memory_order_acquire) != 0) {
        add(faulted_packets_);
        return MidiPushResult::Faulted;
    }
    if (bytes.empty() || bytes.size() > 3) {
        add(invalid_size_packets_);
        return MidiPushResult::InvalidSize;
    }

    const auto write = write_index_.load(std::memory_order_relaxed);
    const auto next = next_index(write);
    if (next == read_index_.load(std::memory_order_acquire)) {
        add(overflow_events_);
        signal_fault(MidiInboxFault::Overflow);
        return MidiPushResult::Overflow;
    }

    MidiPacket packet{};
    packet.size = static_cast<std::uint8_t>(bytes.size());
    packet.arrival_ns = arrival_ns;
    for (std::size_t index = 0; index < bytes.size(); ++index) {
        packet.bytes[index] = bytes[index];
    }
    packets_[write] = packet;
    // Publish the complete ordinary payload only after acquiring the consumer's
    // completed read of a reused slot. A racing fault is retired by the owner.
    write_index_.store(next, std::memory_order_release);
    add(accepted_packets_);
    return MidiPushResult::Accepted;
}

bool MidiInbox::pop(MidiPacket& destination) noexcept {
    if (fault_bits_.load(std::memory_order_acquire) != 0) return false;
    const auto read = read_index_.load(std::memory_order_relaxed);
    if (read == write_index_.load(std::memory_order_acquire)) return false;

    destination = packets_[read];
    // The producer may reuse this slot only after acquiring the completed copy.
    read_index_.store(next_index(read), std::memory_order_release);
    add(popped_packets_);
    return true;
}

void MidiInbox::signal_fault(MidiInboxFault fault) noexcept {
    fault_bits_.fetch_or(static_cast<std::uint32_t>(fault), std::memory_order_release);
}

std::uint32_t MidiInbox::faults() const noexcept {
    return fault_bits_.load(std::memory_order_acquire);
}

std::size_t MidiInbox::pending() const noexcept {
    const auto read = read_index_.load(std::memory_order_relaxed);
    const auto write = write_index_.load(std::memory_order_acquire);
    return write >= read ? write - read : ring_size - read + write;
}

MidiInboxDiagnostics MidiInbox::diagnostics() const noexcept {
    return {
        received_packets_.load(std::memory_order_relaxed),
        accepted_packets_.load(std::memory_order_relaxed),
        invalid_size_packets_.load(std::memory_order_relaxed),
        faulted_packets_.load(std::memory_order_relaxed),
        overflow_events_.load(std::memory_order_relaxed),
        popped_packets_.load(std::memory_order_relaxed),
        discarded_packets_.load(std::memory_order_relaxed),
        resets_.load(std::memory_order_relaxed),
        faults()};
}

void MidiInbox::reset_quiescent() noexcept {
    add(discarded_packets_, static_cast<std::uint64_t>(pending()));
    read_index_.store(0, std::memory_order_relaxed);
    write_index_.store(0, std::memory_order_relaxed);
    add(resets_);
    fault_bits_.store(0, std::memory_order_release);
}

bool valid_midi_routing(const MidiRouting& routing) noexcept {
    const auto valid = [](std::uint8_t channel) noexcept {
        return channel >= 1 && channel <= 16;
    };
    return valid(routing.upper_channel) && valid(routing.lower_channel) &&
           valid(routing.pedal_channel) &&
           routing.upper_channel != routing.lower_channel &&
           routing.upper_channel != routing.pedal_channel &&
           routing.lower_channel != routing.pedal_channel;
}

bool MidiInput::begin_epoch(const MidiRouting& routing) noexcept {
    if (active_ || !valid_midi_routing(routing)) return false;
    routing_ = routing;
    last_arrival_ns_ = 0;
    have_arrival_ = false;
    active_ = true;
    increment(diagnostics_.epochs);
    return true;
}

void MidiInput::end_epoch() noexcept {
    active_ = false;
    last_arrival_ns_ = 0;
    have_arrival_ = false;
}

MidiDecoded MidiInput::decode(const MidiPacket& packet) noexcept {
    increment(diagnostics_.packets);
    MidiDecoded result{};
    const auto finish = [&](MidiDecodeStatus status) noexcept {
        result.status = status;
        switch (status) {
        case MidiDecodeStatus::Action: increment(diagnostics_.actions); break;
        case MidiDecodeStatus::Unsupported: increment(diagnostics_.unsupported); break;
        case MidiDecodeStatus::UnmappedChannel: increment(diagnostics_.unmapped_channels); break;
        case MidiDecodeStatus::OutOfRange: increment(diagnostics_.out_of_range); break;
        case MidiDecodeStatus::Malformed: increment(diagnostics_.malformed); break;
        case MidiDecodeStatus::Inactive: increment(diagnostics_.inactive); break;
        }
        return result;
    };
    if (!active_) return finish(MidiDecodeStatus::Inactive);

    result.arrival_ns = packet.arrival_ns;
    result.timestamp_regressed = have_arrival_ && packet.arrival_ns < last_arrival_ns_;
    if (result.timestamp_regressed) increment(diagnostics_.timestamp_regressions);
    last_arrival_ns_ = packet.arrival_ns;
    have_arrival_ = true;

    if (packet.size < 1 || packet.size > 3 || packet.bytes[0] < 0x80) {
        return finish(MidiDecodeStatus::Malformed);
    }
    const auto status = packet.bytes[0];
    if (status >= 0xF0) return finish(MidiDecodeStatus::Unsupported);

    const auto family = status & 0xF0U;
    const std::uint8_t required_size = family == 0xC0U || family == 0xD0U ? 2 : 3;
    if (packet.size != required_size) return finish(MidiDecodeStatus::Malformed);
    for (std::size_t index = 1; index < packet.size; ++index) {
        if (packet.bytes[index] >= 0x80) return finish(MidiDecodeStatus::Malformed);
    }

    const auto wire_channel = static_cast<std::uint8_t>((status & 0x0FU) + 1);
    std::size_t division = 0;
    if (wire_channel == routing_.upper_channel) {
        division = 0;
    } else if (wire_channel == routing_.lower_channel) {
        division = 1;
    } else if (wire_channel == routing_.pedal_channel) {
        division = 2;
    } else {
        return finish(MidiDecodeStatus::UnmappedChannel);
    }

    if (family == 0x80U || family == 0x90U) {
        const auto pitch = packet.bytes[1];
        const bool pedal = division == 2;
        if (pedal ? pitch < kMidiPedalFirstNote || pitch > kMidiPedalLastNote
                  : !is_valid_manual_midi_note(pitch)) {
            return finish(MidiDecodeStatus::OutOfRange);
        }
        const bool on = family == 0x90U && packet.bytes[2] != 0;
        const std::uint8_t velocity = on ? packet.bytes[2] : 0;
        if (pedal) {
            result.action = SessionCommand{PerformanceInputEvent{PedalNoteEvent{
                0, on ? PedalNoteKind::On : PedalNoteKind::Off, 0,
                kMidiOwnerChannels[division],
                PedalId{static_cast<std::uint8_t>(pitch - kMidiPedalFirstNote + 1)},
                velocity, -1}}};
        } else {
            result.action = SessionCommand{PerformanceInputEvent{HostNoteEvent{
                0, on ? HostNoteKind::On : HostNoteKind::Off,
                static_cast<std::uint8_t>(division), kMidiOwnerChannels[division],
                pitch, velocity, -1}}};
        }
        return finish(MidiDecodeStatus::Action);
    }

    if (family == 0xB0U) {
        const auto controller = packet.bytes[1];
        if (controller == 123) {
            result.action = scoped_release(division);
            return finish(MidiDecodeStatus::Action);
        }

        std::uint32_t parameter_id = 0;
        if (controller == 11) {
            parameter_id = 8192;
        } else if (controller >= 16 && controller <= 24 && division < 2) {
            // Permanent upper/lower B-bank IDs. Neither the edited nor the
            // sounding bank affects these identities or selects/enables B.
            parameter_id = (division == 0 ? 4112U : 4144U) + controller - 16U;
        } else if (division == 2 && controller >= 16 && controller <= 17) {
            parameter_id = 16384U + controller - 16U;
        } else {
            return finish(MidiDecodeStatus::Unsupported);
        }
        result.action = MidiParameterEdit{
            parameter_id, static_cast<double>(packet.bytes[2]) / 127.0};
        return finish(MidiDecodeStatus::Action);
    }
    return finish(MidiDecodeStatus::Unsupported);
}

std::array<SessionCommand, 3> midi_release_commands() noexcept {
    return {scoped_release(0), scoped_release(1), scoped_release(2)};
}

} // namespace hammond::standalone
