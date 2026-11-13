#include "hammond/StateExchange.h"

#include <bit>
#include <limits>

namespace hammond {
namespace {

static_assert(kParameterCount == 45, "Update the explicit state payload for a registry change");
static_assert(kManualCount == 2 && kDrawbarBankCount == 2 && kDrawbarCount == 9);
static_assert(sizeof(double) == sizeof(std::uint64_t));
static_assert(std::numeric_limits<double>::is_iec559);

using Payload = std::array<std::uint64_t, kStatePublicationCellCount>;

// Cells follow compiled descriptor order, not external parameter IDs. Integer
// controls retain their exact plain values; expression retains binary64 bits
// (including signed zero). Route bits and the acknowledgement follow them.
[[nodiscard]] Payload encode(const ControlSnapshot& snapshot, std::uint64_t ack) noexcept {
    Payload cells{};
    std::size_t index = 0;
    for (const auto& manual : snapshot.drawbars) {
        for (const auto& bank : manual) {
            for (const auto position : bank) cells[index++] = position;
        }
    }
    cells[index++] = std::bit_cast<std::uint64_t>(snapshot.expression);
    for (const auto bank : snapshot.selected_banks) {
        cells[index++] = static_cast<std::uint64_t>(bank);
    }
    cells[index++] = snapshot.percussion.enabled ? 1 : 0;
    cells[index++] = static_cast<std::uint64_t>(snapshot.percussion.harmonic);
    cells[index++] = static_cast<std::uint64_t>(snapshot.percussion.volume);
    cells[index++] = static_cast<std::uint64_t>(snapshot.percussion.decay);
    for (const auto position : snapshot.pedal_drawbars) cells[index++] = position;
    for (const auto enabled : snapshot.route_enabled) cells[index++] = enabled ? 1 : 0;
    cells[index] = ack;
    return cells;
}

// Only validated writers can produce this payload. Domain checks additionally
// keep destination unchanged if a future encoding change violates that rule.
[[nodiscard]] bool decode(const Payload& cells, StatePublishedControls& destination) noexcept {
    StatePublishedControls candidate{};
    std::size_t index = 0;
    for (auto& manual : candidate.controls.drawbars) {
        for (auto& bank : manual) {
            for (auto& position : bank) {
                if (cells[index] > 8) return false;
                position = static_cast<std::uint8_t>(cells[index++]);
            }
        }
    }
    candidate.controls.expression = std::bit_cast<double>(cells[index++]);
    for (auto& bank : candidate.controls.selected_banks) {
        if (cells[index] > 1) return false;
        bank = static_cast<DrawbarBank>(cells[index++]);
    }
    if (cells[index] > 1) return false;
    candidate.controls.percussion.enabled = cells[index++] != 0;
    if (cells[index] > 1) return false;
    candidate.controls.percussion.harmonic = static_cast<PercussionHarmonic>(cells[index++]);
    if (cells[index] > 1) return false;
    candidate.controls.percussion.volume = static_cast<PercussionVolume>(cells[index++]);
    if (cells[index] > 1) return false;
    candidate.controls.percussion.decay = static_cast<PercussionDecay>(cells[index++]);
    for (auto& position : candidate.controls.pedal_drawbars) {
        if (cells[index] > 8) return false;
        position = static_cast<std::uint8_t>(cells[index++]);
    }
    for (auto& enabled : candidate.controls.route_enabled) {
        if (cells[index] > 1) return false;
        enabled = cells[index++] != 0;
    }
    candidate.acknowledged_sequence = cells[index];
    if (!is_valid_control_snapshot(candidate.controls)) return false;
    destination = candidate;
    return true;
}

} // namespace

StateExchange::StateExchange(StateExchangeLimits limits) noexcept
    : limits_(limits),
      valid_limits_(limits.publications <= std::numeric_limits<std::uint64_t>::max() / 2) {
    const auto initial = encode(ControlSnapshot{}, 0);
    for (std::size_t i = 0; i < initial.size(); ++i) {
        published_cells_[i].store(initial[i], std::memory_order_seq_cst);
    }
}

StateEnqueueResult StateExchange::ui_enqueue(const ControlSnapshot& snapshot) noexcept {
    if (!valid_limits_) return {StateExchangeStatus::InvalidLimits, 0};
    if (!is_valid_control_snapshot(snapshot)) return {StateExchangeStatus::InvalidSnapshot, 0};
    if (producer_sequence_ >= limits_.accepted_states) {
        return {StateExchangeStatus::SequenceExhausted, 0};
    }
    const auto consumed = consumed_sequence_.load(std::memory_order_acquire);
    if (producer_sequence_ - consumed >= kStateQueueCapacity) {
        return {StateExchangeStatus::QueueFull, 0};
    }
    const auto next = producer_sequence_ + 1; // Checked before addition; never wraps.
    slots_[producer_sequence_ % kStateQueueCapacity] = snapshot;
    latest_accepted_ = snapshot;
    producer_sequence_ = next;
    queued_sequence_.store(next, std::memory_order_release);
    return {StateExchangeStatus::Ok, next};
}

StateExchangeStatus StateExchange::audio_peek(StateExchangeBatch& destination) noexcept {
    if (!valid_limits_) return StateExchangeStatus::InvalidLimits;
    const auto queued = queued_sequence_.load(std::memory_order_acquire);
    if (queued < consumer_sequence_ || queued - consumer_sequence_ > kStateQueueCapacity) {
        return StateExchangeStatus::InvalidBatch;
    }
    StateExchangeBatch candidate{};
    candidate.origin_ = this;
    candidate.base_sequence_ = consumer_sequence_;
    candidate.end_sequence_ = queued;
    candidate.publication_revision_ = audio_publication_revision_;
    candidate.count_ = static_cast<std::size_t>(queued - consumer_sequence_);
    for (std::size_t i = 0; i < candidate.count_; ++i) {
        candidate.snapshots_[i] = slots_[(consumer_sequence_ + i) % kStateQueueCapacity];
    }
    destination = candidate;
    return StateExchangeStatus::Ok;
}

StateExchangeStatus StateExchange::audio_can_commit(const StateExchangeBatch& batch) const noexcept {
    if (!valid_limits_) return StateExchangeStatus::InvalidLimits;
    if (batch.origin_ != this || batch.base_sequence_ != consumer_sequence_ ||
        batch.publication_revision_ != audio_publication_revision_ ||
        batch.end_sequence_ < batch.base_sequence_ ||
        batch.end_sequence_ - batch.base_sequence_ != batch.count_ ||
        batch.count_ > kStateQueueCapacity ||
        queued_sequence_.load(std::memory_order_acquire) < batch.end_sequence_) {
        return StateExchangeStatus::InvalidBatch;
    }
    if (audio_publication_revision_ / 2 >= limits_.publications) {
        return StateExchangeStatus::SequenceExhausted;
    }
    return StateExchangeStatus::Ok;
}

StateExchangeStatus StateExchange::audio_commit(
    const StateExchangeBatch& batch, const ControlSnapshot& current_controls) noexcept {
    const auto preflight = audio_can_commit(batch);
    if (preflight != StateExchangeStatus::Ok) return preflight;
    if (!is_valid_control_snapshot(current_controls)) return StateExchangeStatus::InvalidSnapshot;
    const auto payload = encode(current_controls, batch.end_sequence_);
    const auto next_revision = audio_publication_revision_ + 2;
    published_revision_.store(audio_publication_revision_ + 1, std::memory_order_seq_cst);
    for (std::size_t i = 0; i < payload.size(); ++i) {
        published_cells_[i].store(payload[i], std::memory_order_seq_cst);
    }
    published_revision_.store(next_revision, std::memory_order_seq_cst);
    audio_publication_revision_ = next_revision;
    consumer_sequence_ = batch.end_sequence_;
    consumed_sequence_.store(consumer_sequence_, std::memory_order_release);
    return StateExchangeStatus::Ok;
}

bool StateExchange::read_published(StatePublishedControls& destination) const noexcept {
    if (!valid_limits_) return false;
    for (std::size_t attempt = 0; attempt < kStateReadAttempts; ++attempt) {
        const auto before = published_revision_.load(std::memory_order_seq_cst);
        if ((before & 1U) != 0) continue;
        Payload payload{};
        for (std::size_t i = 0; i < payload.size(); ++i) {
            payload[i] = published_cells_[i].load(std::memory_order_seq_cst);
        }
        const auto after = published_revision_.load(std::memory_order_seq_cst);
        if (before != after || (after & 1U) != 0) continue;
        StatePublishedControls candidate{};
        if (!decode(payload, candidate) || candidate.acknowledged_sequence > limits_.accepted_states) {
            return false;
        }
        candidate.publication_revision = after;
        destination = candidate;
        return true;
    }
    return false;
}

bool StateExchange::ui_snapshot_for_save(ControlSnapshot& destination) const noexcept {
    StatePublishedControls published{};
    if (!read_published(published) || published.acknowledged_sequence > producer_sequence_) return false;
    destination = published.acknowledged_sequence < producer_sequence_
        ? latest_accepted_ : published.controls;
    return true;
}

} // namespace hammond
