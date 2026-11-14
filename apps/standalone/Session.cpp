#include "Session.h"

#include <algorithm>
#include <atomic>
#include <bit>
#include <cmath>
#include <limits>
#include <type_traits>

namespace hammond::standalone {
namespace {

static_assert(std::atomic<std::uint32_t>::is_always_lock_free);
static_assert(std::atomic<std::uint64_t>::is_always_lock_free);
static_assert(std::is_trivially_copyable_v<SessionCommand>);
static_assert(std::is_nothrow_copy_assignable_v<SessionCommand>);
static_assert(std::is_nothrow_copy_assignable_v<Engine>);
static_assert(sizeof(double) == sizeof(std::uint64_t));
static_assert(sizeof(float) == sizeof(std::uint32_t));

constexpr auto kMaximum = std::numeric_limits<std::uint64_t>::max();

void increment(std::uint64_t& value) noexcept {
    if (value != kMaximum) ++value;
}

void increment(std::atomic<std::uint64_t>& value) noexcept {
    // Each producer counter has exactly one writer. No retry loop is needed.
    const auto previous = value.load(std::memory_order_relaxed);
    if (previous != kMaximum) value.store(previous + 1, std::memory_order_release);
}

[[nodiscard]] std::uint64_t saturated_sum(std::uint64_t left,
                                          std::uint64_t right) noexcept {
    return right > kMaximum - left ? kMaximum : left + right;
}

[[nodiscard]] constexpr std::uint32_t fault(SessionFault value) noexcept {
    return static_cast<std::uint32_t>(value);
}

[[nodiscard]] bool admitted_command_shape(const SessionCommand& command) noexcept {
    if (const auto* input = std::get_if<PerformanceInputEvent>(&command)) {
        if (const auto* manual = std::get_if<HostNoteEvent>(input)) {
            return manual->offset == 0;
        }
        if (const auto* pedal = std::get_if<PedalNoteEvent>(input)) {
            return pedal->offset == 0;
        }
        if (const auto* control = std::get_if<Event>(input)) {
            if (control->offset != 0) return false;
            switch (control->type) {
            case EventType::Drawbar:
            case EventType::BankDrawbar:
            case EventType::SelectBank:
            case EventType::Cancel:
            case EventType::Expression:
            case EventType::Percussion:
            case EventType::PedalDrawbar:
            case EventType::SelectPreset:
                return true;
            default:
                return false;
            }
        }
        return false;
    }
    if (const auto* controls = std::get_if<ControlSnapshot>(&command)) {
        return is_valid_control_snapshot(*controls);
    }
    return std::holds_alternative<ReleaseUiNotes>(command) ||
           std::holds_alternative<Panic>(command);
}

// Only canonical values are packed, never the struct's padding or object
// representation. Every concurrently accessed payload word is itself atomic.
constexpr std::size_t kSnapshotWords = 22;
using SnapshotWords = std::array<std::uint64_t, kSnapshotWords>;
constexpr std::uint64_t kSnapshotByteMask = 0xffU;
constexpr std::size_t kFixedModeWord = 4;
constexpr unsigned kUpperFixedModeShift = 32;
constexpr unsigned kLowerFixedModeShift = 40;
static_assert(kManualCount == 2 && kDrawbarBankCount == 2 && kDrawbarCount == 9);
static_assert(kManualCount * kDrawbarBankCount * kDrawbarCount == 36);
static_assert(kFixedModeWord * 8 + kUpperFixedModeShift / 8 == 36);
static_assert(kLowerFixedModeShift == kUpperFixedModeShift + 8);
static_assert(kLowerFixedModeShift + 8 <= 64);
static_assert(std::is_same_v<std::underlying_type_t<FixedRegistration>, std::uint8_t>);
static_assert(kFixedRegistrationCount == 9);
static_assert(static_cast<std::uint8_t>(FixedRegistration::A) == 9);
static_assert(static_cast<std::uint8_t>(FixedRegistration::A) <= kSnapshotByteMask);

[[nodiscard]] SnapshotWords pack(const SessionSnapshot& snapshot) noexcept {
    SnapshotWords words{};
    std::size_t byte = 0;
    for (const auto& manual : snapshot.controls.drawbars) {
        for (const auto& bank : manual) {
            for (const auto position : bank) {
                words[byte / 8] |= static_cast<std::uint64_t>(position) << ((byte % 8) * 8);
                ++byte;
            }
        }
    }
    const auto& controls = snapshot.controls;
    // The first 36 bytes retain all four banks; word 4's next two bytes retain
    // raw fixed modes independently of the route bits and remembered banks.
    words[kFixedModeWord] |=
        (static_cast<std::uint64_t>(controls.fixed_registrations[0]) & kSnapshotByteMask)
        << kUpperFixedModeShift;
    words[kFixedModeWord] |=
        (static_cast<std::uint64_t>(controls.fixed_registrations[1]) & kSnapshotByteMask)
        << kLowerFixedModeShift;
    words[5] = static_cast<std::uint64_t>(controls.selected_banks[0]) |
               (static_cast<std::uint64_t>(controls.selected_banks[1]) << 8) |
               (static_cast<std::uint64_t>(controls.route_enabled[0]) << 16) |
               (static_cast<std::uint64_t>(controls.route_enabled[1]) << 17) |
               (static_cast<std::uint64_t>(controls.percussion.enabled) << 18) |
               (static_cast<std::uint64_t>(controls.percussion.harmonic) << 24) |
               (static_cast<std::uint64_t>(controls.percussion.volume) << 32) |
               (static_cast<std::uint64_t>(controls.percussion.decay) << 40) |
               (static_cast<std::uint64_t>(controls.pedal_drawbars[0]) << 48) |
               (static_cast<std::uint64_t>(controls.pedal_drawbars[1]) << 56);
    words[6] = std::bit_cast<std::uint64_t>(controls.expression);
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        for (std::size_t key = 0; key < kManualKeyCount; ++key) {
            words[7 + manual] |= static_cast<std::uint64_t>(snapshot.held_keys[manual][key]) << key;
        }
    }
    for (std::size_t pedal = 0; pedal < kPedalCount; ++pedal) {
        words[9] |= static_cast<std::uint64_t>(snapshot.held_pedals[pedal]) << pedal;
    }
    words[10] = snapshot.frame_clock;
    words[11] = std::bit_cast<std::uint64_t>(snapshot.sample_rate);
    words[12] = std::bit_cast<std::uint32_t>(snapshot.peak);
    words[13] = static_cast<std::uint64_t>(snapshot.prepared) |
                (static_cast<std::uint64_t>(snapshot.running) << 1);
    words[14] = snapshot.resolved_sequence;
    words[15] = snapshot.last_applied_sequence;
    words[16] = snapshot.recovery_count;
    words[17] = snapshot.queue_overflows;
    words[18] = snapshot.rejected_commands;
    words[19] = snapshot.discarded_commands;
    words[20] = snapshot.fault_flags;
    words[21] = static_cast<std::uint64_t>(snapshot.last_core_status);
    return words;
}

[[nodiscard]] SessionSnapshot unpack(const SnapshotWords& words,
                                      std::uint64_t revision) noexcept {
    SessionSnapshot snapshot;
    std::size_t byte = 0;
    for (auto& manual : snapshot.controls.drawbars) {
        for (auto& bank : manual) {
            for (auto& position : bank) {
                position = static_cast<std::uint8_t>((words[byte / 8] >> ((byte % 8) * 8)) & 255U);
                ++byte;
            }
        }
    }
    auto& controls = snapshot.controls;
    controls.fixed_registrations[0] = static_cast<FixedRegistration>(
        (words[kFixedModeWord] >> kUpperFixedModeShift) & kSnapshotByteMask);
    controls.fixed_registrations[1] = static_cast<FixedRegistration>(
        (words[kFixedModeWord] >> kLowerFixedModeShift) & kSnapshotByteMask);
    controls.selected_banks[0] = static_cast<DrawbarBank>(words[5] & 255U);
    controls.selected_banks[1] = static_cast<DrawbarBank>((words[5] >> 8) & 255U);
    controls.route_enabled[0] = ((words[5] >> 16) & 1U) != 0;
    controls.route_enabled[1] = ((words[5] >> 17) & 1U) != 0;
    controls.percussion.enabled = ((words[5] >> 18) & 1U) != 0;
    controls.percussion.harmonic = static_cast<PercussionHarmonic>((words[5] >> 24) & 255U);
    controls.percussion.volume = static_cast<PercussionVolume>((words[5] >> 32) & 255U);
    controls.percussion.decay = static_cast<PercussionDecay>((words[5] >> 40) & 255U);
    controls.pedal_drawbars[0] = static_cast<std::uint8_t>((words[5] >> 48) & 255U);
    controls.pedal_drawbars[1] = static_cast<std::uint8_t>((words[5] >> 56) & 255U);
    controls.expression = std::bit_cast<double>(words[6]);
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        for (std::size_t key = 0; key < kManualKeyCount; ++key) {
            snapshot.held_keys[manual][key] = ((words[7 + manual] >> key) & 1U) != 0;
        }
    }
    for (std::size_t pedal = 0; pedal < kPedalCount; ++pedal) {
        snapshot.held_pedals[pedal] = ((words[9] >> pedal) & 1U) != 0;
    }
    snapshot.frame_clock = words[10];
    snapshot.sample_rate = std::bit_cast<double>(words[11]);
    snapshot.peak = std::bit_cast<float>(static_cast<std::uint32_t>(words[12]));
    snapshot.prepared = (words[13] & 1U) != 0;
    snapshot.running = ((words[13] >> 1) & 1U) != 0;
    snapshot.publication_revision = revision;
    snapshot.resolved_sequence = words[14];
    snapshot.last_applied_sequence = words[15];
    snapshot.recovery_count = words[16];
    snapshot.queue_overflows = words[17];
    snapshot.rejected_commands = words[18];
    snapshot.discarded_commands = words[19];
    snapshot.fault_flags = static_cast<std::uint32_t>(words[20]);
    snapshot.last_core_status = static_cast<Status>(words[21]);
    return snapshot;
}

} // namespace

class Session::Impl {
public:
    explicit Impl(SessionLimits limits) noexcept : limits_(limits) {
        const auto initial = pack(SessionSnapshot{});
        for (std::size_t index = 0; index < kSnapshotWords; ++index) {
            snapshot_words_[index].store(initial[index], std::memory_order_relaxed);
        }
    }

    [[nodiscard]] SessionStatus prepare(const RuntimeProfile& profile,
                                         const ProcessSpec& spec) noexcept {
        if (running_) return SessionStatus::AlreadyRunning;
        if (limits_.publications > kMaximum / 2) return SessionStatus::InvalidSpec;

        // All fallible candidate preparation precedes changes to the installed
        // Engine, owners, queue, lifecycle and publication allowance.
        Engine candidate;
        const auto status = candidate.prepare(profile, spec);
        if (status != Status::Ok) {
            return status == Status::InvalidSpec ? SessionStatus::InvalidSpec
                                                : SessionStatus::InvalidProfile;
        }
        if (!publication_available()) return SessionStatus::SequenceExhausted;

        const auto boundary = queue_state_.load(std::memory_order_acquire);
        discard_through(boundary & kCursorMask);
        engine_ = candidate;
        manual_ownership_ = NoteOwnership{};
        pedal_ownership_ = PedalNoteOwnership{};
        max_block_frames_ = spec.max_block_frames;
        peak_ = 0.0F;
        core_failed_ = false;
        queue_state_.fetch_and(~kCoreFailed, std::memory_order_relaxed);
        const bool recovered = (boundary & kRecovery) != 0;
        if (recovered) increment(recovery_count_);
        publish();
        if (recovered) acknowledge_recovery();
        return SessionStatus::Ok;
    }

    [[nodiscard]] SessionStatus start() noexcept {
        if (!engine_.prepared()) return SessionStatus::NotPrepared;
        if (running_) return SessionStatus::AlreadyRunning;
        if (core_failed_) return SessionStatus::CoreFailure;
        if (!publication_available()) return SessionStatus::SequenceExhausted;
        running_ = true;
        publish();
        return SessionStatus::Ok;
    }

    [[nodiscard]] SessionStatus stop() noexcept {
        if (!engine_.prepared()) return SessionStatus::NotPrepared;
        if (!publication_available()) return SessionStatus::SequenceExhausted;
        const auto boundary = queue_state_.load(std::memory_order_acquire);
        const auto status = global_panic();
        if (status != Status::Ok) return fail_core(status);
        discard_through(boundary & kCursorMask);
        running_ = false;
        peak_ = 0.0F;
        core_failed_ = false;
        queue_state_.fetch_and(~kCoreFailed, std::memory_order_relaxed);
        const bool recovered = (boundary & kRecovery) != 0;
        if (recovered) increment(recovery_count_);
        publish();
        if (recovered) acknowledge_recovery();
        return SessionStatus::Ok;
    }

    [[nodiscard]] SubmitResult post(const SessionCommand& command) noexcept {
        if (!engine_.prepared()) return {SessionStatus::NotPrepared, 0};
        auto observed = queue_state_.load(std::memory_order_acquire);
        if ((observed & kExhausted) != 0) return {SessionStatus::SequenceExhausted, 0};
        if ((observed & (kRecovery | kCoreFailed)) != 0) {
            return {SessionStatus::RecoveryPending, 0};
        }
        if (!admitted_command_shape(command)) {
            increment(producer_rejections_);
            return {SessionStatus::InvalidCommand, 0};
        }
        if (command_sequence_ >= limits_.command_sequences) {
            queue_state_.fetch_or(kCommandExhausted | kRecovery, std::memory_order_acq_rel);
            return {SessionStatus::SequenceExhausted, 0};
        }

        const auto cursor = observed & kCursorMask;
        const auto consumed = consumed_cursor_.load(std::memory_order_acquire);
        if (distance(consumed, cursor) == kSessionCommandCapacity) {
            // Publish the diagnostic before the release operation that requests
            // recovery, so its acknowledgment includes this overflow.
            increment(queue_overflows_);
            queue_state_.fetch_or(kRecovery, std::memory_order_acq_rel);
            return {SessionStatus::QueueFull, 0};
        }

        auto& slot = queue_[cursor & kSlotMask];
        slot.command = command;
        slot.sequence = command_sequence_ + 1;
        const auto desired = (observed & ~kCursorMask) | advance(cursor);
        // The commit and recovery request share one atomic modification order.
        // A request winning this race prevents publication of this ordinary slot.
        if (!queue_state_.compare_exchange_strong(observed, desired,
                                                  std::memory_order_acq_rel,
                                                  std::memory_order_acquire)) {
            return {(observed & kExhausted) != 0 ? SessionStatus::SequenceExhausted
                                               : SessionStatus::RecoveryPending, 0};
        }
        ++command_sequence_;
        return {SessionStatus::Ok, command_sequence_};
    }

    [[nodiscard]] RenderResult render(std::uint32_t frames,
                                       std::span<float> stereo) noexcept {
        if (!engine_.prepared()) {
            return reject_render(SessionStatus::NotPrepared, Status::NotPrepared);
        }
        if (!running_) return reject_render(SessionStatus::NotRunning);
        if (frames > max_block_frames_) {
            return reject_render(SessionStatus::BlockTooLarge, Status::BlockTooLarge);
        }
        if (stereo.size() != static_cast<std::size_t>(frames) * 2) {
            return reject_render(SessionStatus::InvalidBuffer, Status::InvalidBuffer);
        }
        if (engine_.frame_clock() > kMaximum - frames) {
            return reject_render(SessionStatus::TimelineOverflow, Status::TimelineOverflow);
        }
        if (!publication_available()) return reject_render(SessionStatus::SequenceExhausted);
        if (core_failed_) return reject_render(SessionStatus::CoreFailure);

        // One acquired boundary, never a drain-until-empty loop. Recovery that
        // arrives after this capture stays latched for the next valid callback.
        const auto boundary = queue_state_.load(std::memory_order_acquire);
        bool recovered = (boundary & kRecovery) != 0;
        if (recovered) {
            discard_through(boundary & kCursorMask);
            const auto status = global_panic();
            if (status != Status::Ok) return {fail_core(status), 0};
        } else {
            const auto count = distance(consumer_cursor_, boundary & kCursorMask);
            for (std::size_t index = 0; index < count; ++index) {
                const auto& slot = queue_[consumer_cursor_ & kSlotMask];
                const auto sequence = slot.sequence;
                const auto status = apply(slot.command);
                resolved_sequence_ = sequence;
                if (status == Status::Ok) last_applied_sequence_ = sequence;
                release_slot();
                if (status != Status::Ok) {
                    increment(consumer_rejections_);
                    fault_flags_ |= fault(SessionFault::RejectedCommand);
                    last_core_status_ = status;
                    // Closing admission atomically captures every raced commit.
                    // The remaining prefix, including later posts, is <=256.
                    const auto closed = queue_state_.fetch_or(kRecovery, std::memory_order_acq_rel);
                    discard_through(closed & kCursorMask);
                    const auto panic_status = global_panic();
                    if (panic_status != Status::Ok) return {fail_core(panic_status), 0};
                    recovered = true;
                    break;
                }
            }
        }

        const auto rendered = engine_.process(
            frames, std::span<float>{mono_.data(), static_cast<std::size_t>(frames)}, {});
        if (!rendered) return {fail_core(rendered.status), 0};
        if (frames != 0) {
            float peak = 0.0F;
            for (std::size_t index = 0; index < frames; ++index) {
                const auto sample = mono_[index];
                stereo[2 * index] = sample;
                stereo[2 * index + 1] = sample;
                peak = std::max(peak, std::abs(sample));
            }
            peak_ = peak;
        }
        if (recovered) increment(recovery_count_);
        publish();
        if (recovered) acknowledge_recovery();
        return {SessionStatus::Ok, frames};
    }

    [[nodiscard]] bool read_snapshot(SessionSnapshot& destination) const noexcept {
        for (std::size_t attempt = 0; attempt < kSessionSnapshotReadAttempts; ++attempt) {
            if ((queue_state_.load(std::memory_order_acquire) & kPublicationExhausted) != 0) {
                return false;
            }
            const auto before = snapshot_revision_.load(std::memory_order_acquire);
            if ((before & 1U) != 0) continue;
            SnapshotWords words{};
            for (std::size_t index = 0; index < kSnapshotWords; ++index) {
                words[index] = snapshot_words_[index].load(std::memory_order_acquire);
            }
            const auto after = snapshot_revision_.load(std::memory_order_acquire);
            if (before == after &&
                (queue_state_.load(std::memory_order_acquire) & kPublicationExhausted) == 0) {
                destination = unpack(words, after);
                return true;
            }
        }
        return false;
    }

private:
    // The ring cursor is modulo 512, not a lifetime sequence. The extra lap bit
    // gives all 256 slots usable storage without an empty sentinel slot.
    static constexpr std::uint32_t kSlotMask = 255;
    static constexpr std::uint32_t kCursorMask = 511;
    static constexpr std::uint32_t kRecovery = 1U << 9;
    static constexpr std::uint32_t kRecoveryEpoch = 1U << 10;
    static constexpr std::uint32_t kCommandExhausted = 1U << 11;
    static constexpr std::uint32_t kPublicationExhausted = 1U << 12;
    static constexpr std::uint32_t kCoreFailed = 1U << 13;
    static constexpr std::uint32_t kExhausted = kCommandExhausted | kPublicationExhausted;
    static_assert(kSessionCommandCapacity == kSlotMask + 1);

    struct Slot {
        SessionCommand command{};
        std::uint64_t sequence{0};
    };

    [[nodiscard]] static constexpr std::uint32_t advance(std::uint32_t cursor) noexcept {
        return (cursor + 1) & kCursorMask;
    }

    [[nodiscard]] static constexpr std::size_t distance(std::uint32_t first,
                                                        std::uint32_t last) noexcept {
        return static_cast<std::size_t>((last - first) & kCursorMask);
    }

    void release_slot() noexcept {
        consumer_cursor_ = advance(consumer_cursor_);
        // The outcome and the last ordinary slot read precede reuse by producer.
        consumed_cursor_.store(consumer_cursor_, std::memory_order_release);
    }

    void discard_through(std::uint32_t upper) noexcept {
        const auto count = distance(consumer_cursor_, upper);
        for (std::size_t index = 0; index < count; ++index) {
            resolved_sequence_ = queue_[consumer_cursor_ & kSlotMask].sequence;
            increment(discarded_commands_);
            release_slot();
        }
    }

    [[nodiscard]] Status global_panic() noexcept {
        constexpr std::array<Event, 3> events{{
            {0, EventType::AllNotesOff, Manual::Upper, 0, 0.0},
            {0, EventType::AllNotesOff, Manual::Lower, 0, 0.0},
            {0, EventType::PedalAllNotesOff, Manual::Lower, 0, 0.0}
        }};
        const auto result = engine_.process(0, {}, events);
        if (result) {
            manual_ownership_ = NoteOwnership{};
            pedal_ownership_ = PedalNoteOwnership{};
        }
        return result.status;
    }

    [[nodiscard]] Status apply(const SessionCommand& command) noexcept {
        if (const auto* input = std::get_if<PerformanceInputEvent>(&command)) {
            return process_performance_input(engine_, manual_ownership_, pedal_ownership_,
                                             0, {}, {input, 1}).status;
        }
        if (const auto* controls = std::get_if<ControlSnapshot>(&command)) {
            return engine_.restore_controls(*controls) ? Status::Ok : Status::InvalidEvent;
        }
        if (std::holds_alternative<ReleaseUiNotes>(command)) {
            const std::array<PerformanceInputEvent, 4> releases{{
                HostNoteEvent{0, HostNoteKind::AllNotesOff, 0, kUiInputChannel, 0, 0, -1},
                HostNoteEvent{0, HostNoteKind::AllNotesOff, 1, kUiInputChannel, 0, 0, -1},
                PedalNoteEvent{0, PedalNoteKind::AllNotesOff, 0, kUiInputChannel, PedalId{0}, 0, -1},
                PedalNoteEvent{0, PedalNoteKind::AllNotesOff, 1, kUiInputChannel, PedalId{0}, 0, -1}
            }};
            return process_performance_input(engine_, manual_ownership_, pedal_ownership_,
                                             0, {}, releases).status;
        }
        if (std::holds_alternative<Panic>(command)) return global_panic();
        return Status::InvalidEvent;
    }

    [[nodiscard]] SessionStatus fail_core(Status status) noexcept {
        core_failed_ = true;
        last_core_status_ = status;
        fault_flags_ |= fault(SessionFault::CoreFailure);
        queue_state_.fetch_or(kCoreFailed | kRecovery, std::memory_order_acq_rel);
        return SessionStatus::CoreFailure;
    }

    [[nodiscard]] RenderResult reject_render(SessionStatus status,
                                             Status core = Status::Ok) noexcept {
        fault_flags_ |= fault(SessionFault::RenderRejected);
        if (core != Status::Ok) last_core_status_ = core;
        return {status, 0};
    }

    [[nodiscard]] bool publication_available() noexcept {
        if ((queue_state_.load(std::memory_order_acquire) & kPublicationExhausted) != 0) {
            return false;
        }
        if (publication_count_ < limits_.publications) return true;
        // No command is consumed and no output sample is touched. The declared
        // emergency exception only releases owners/contacts at zero elapsed time.
        queue_state_.fetch_or(kPublicationExhausted | kRecovery, std::memory_order_acq_rel);
        fault_flags_ |= fault(SessionFault::SequenceExhausted);
        if (engine_.prepared()) {
            const auto status = global_panic();
            if (status != Status::Ok) static_cast<void>(fail_core(status));
        }
        return false;
    }

    void acknowledge_recovery() noexcept {
        // Release admission only after the coherent acknowledgment is published.
        // Flip the epoch as well as opening the gate: a producer suspended before
        // the request cannot successfully CAS its old open state after this ack.
        // One bit suffices: while that sole producer is suspended, no second
        // command-induced recovery can follow the emptied, closed epoch. Lifecycle
        // calls require producer/callback quiescence; exhaustion stays permanent.
        queue_state_.fetch_xor(kRecovery | kRecoveryEpoch, std::memory_order_release);
    }

    void publish() noexcept {
        SessionSnapshot snapshot;
        snapshot.controls = engine_.controls_snapshot();
        for (std::size_t manual = 0; manual < kManualCount; ++manual) {
            for (std::size_t key = 0; key < kManualKeyCount; ++key) {
                snapshot.held_keys[manual][key] = engine_.key_down(
                    static_cast<Manual>(manual),
                    static_cast<std::uint32_t>(key) + kMinManualMidiNote);
            }
        }
        for (std::size_t pedal = 0; pedal < kPedalCount; ++pedal) {
            snapshot.held_pedals[pedal] = engine_.pedal_down(PedalId{
                static_cast<std::uint8_t>(pedal + 1)});
        }
        snapshot.frame_clock = engine_.frame_clock();
        snapshot.sample_rate = engine_.sample_rate();
        snapshot.peak = peak_;
        snapshot.prepared = engine_.prepared();
        snapshot.running = running_;
        snapshot.resolved_sequence = resolved_sequence_;
        snapshot.last_applied_sequence = last_applied_sequence_;
        snapshot.recovery_count = recovery_count_;
        snapshot.queue_overflows = queue_overflows_.load(std::memory_order_acquire);
        snapshot.rejected_commands = saturated_sum(
            consumer_rejections_, producer_rejections_.load(std::memory_order_acquire));
        snapshot.discarded_commands = discarded_commands_;
        snapshot.fault_flags = fault_flags_;
        if (snapshot.queue_overflows != 0) snapshot.fault_flags |= fault(SessionFault::QueueOverflow);
        if (snapshot.rejected_commands != 0) snapshot.fault_flags |= fault(SessionFault::RejectedCommand);
        if ((queue_state_.load(std::memory_order_acquire) & kExhausted) != 0) {
            snapshot.fault_flags |= fault(SessionFault::SequenceExhausted);
        }
        snapshot.last_core_status = last_core_status_;
        const auto words = pack(snapshot);
        ++publication_count_; // preflight guarantees <= UINT64_MAX / 2.
        const auto revision = publication_count_ * 2;
        snapshot_revision_.store(revision - 1, std::memory_order_relaxed);
        for (std::size_t index = 0; index < kSnapshotWords; ++index) {
            snapshot_words_[index].store(words[index], std::memory_order_release);
        }
        // If a reader sees a future payload word, its acquire load observes the
        // preceding odd revision; revision coherence then forbids accepting an
        // older even revision. Acquiring the final even revision also prevents
        // older payload reads. There is no ordinary shared payload or reader wait.
        snapshot_revision_.store(revision, std::memory_order_release);
    }

    const SessionLimits limits_;
    Engine engine_{};
    NoteOwnership manual_ownership_{};
    PedalNoteOwnership pedal_ownership_{};
    std::array<float, kHardMaxBlockFrames> mono_{};
    std::array<Slot, kSessionCommandCapacity> queue_{};
    std::atomic<std::uint32_t> queue_state_{0};
    std::atomic<std::uint32_t> consumed_cursor_{0};
    std::uint32_t consumer_cursor_{0};
    std::uint64_t command_sequence_{0}; // Sole producer, never reset or wrapped.
    std::atomic<std::uint64_t> queue_overflows_{0};
    std::atomic<std::uint64_t> producer_rejections_{0};
    std::uint64_t consumer_rejections_{0};
    std::uint64_t resolved_sequence_{0};
    std::uint64_t last_applied_sequence_{0};
    std::uint64_t recovery_count_{0};
    std::uint64_t discarded_commands_{0};
    std::uint64_t publication_count_{0};
    std::uint32_t fault_flags_{0};
    Status last_core_status_{Status::Ok};
    std::uint32_t max_block_frames_{0};
    float peak_{0.0F};
    bool running_{false};
    bool core_failed_{false};
    std::array<std::atomic<std::uint64_t>, kSnapshotWords> snapshot_words_{};
    std::atomic<std::uint64_t> snapshot_revision_{0};
};

Session::Session(SessionLimits limits) : impl_(std::make_unique<Impl>(limits)) {}
Session::~Session() = default;

SessionStatus Session::prepare(const RuntimeProfile& profile, const ProcessSpec& spec) noexcept {
    return impl_->prepare(profile, spec);
}

SessionStatus Session::start() noexcept { return impl_->start(); }
SessionStatus Session::stop() noexcept { return impl_->stop(); }
SubmitResult Session::post(const SessionCommand& command) noexcept { return impl_->post(command); }

RenderResult Session::render(std::uint32_t frames,
                             std::span<float> interleaved_stereo) noexcept {
    return impl_->render(frames, interleaved_stereo);
}

bool Session::read_snapshot(SessionSnapshot& destination) const noexcept {
    return impl_->read_snapshot(destination);
}

} // namespace hammond::standalone
