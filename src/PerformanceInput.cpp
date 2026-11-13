#include "hammond/PerformanceInput.h"

#include <array>
#include <type_traits>

namespace hammond {
namespace {

[[nodiscard]] bool is_control(EventType type) noexcept {
    switch (type) {
    case EventType::Drawbar:
    case EventType::BankDrawbar:
    case EventType::SelectBank:
    case EventType::Cancel:
    case EventType::Expression:
    case EventType::Percussion:
    case EventType::PedalDrawbar:
        return true;
    default:
        return false;
    }
}

[[nodiscard]] bool offset_and_kind(const PerformanceInputEvent& input,
                                    std::uint32_t& offset) noexcept {
    if (const auto* manual = std::get_if<HostNoteEvent>(&input)) {
        offset = manual->offset;
        return true;
    }
    if (const auto* pedal = std::get_if<PedalNoteEvent>(&input)) {
        offset = pedal->offset;
        return true;
    }
    if (const auto* control = std::get_if<Event>(&input)) {
        offset = control->offset;
        return is_control(control->type);
    }
    return false;
}

} // namespace

// The commit relies only on bounded, nonthrowing value assignments. Keep this
// requirement explicit if either adapter or an input alternative later changes.
static_assert(std::is_trivially_copyable_v<NoteOwnership>);
static_assert(std::is_trivially_copyable_v<PedalNoteOwnership>);
static_assert(std::is_trivially_copyable_v<PerformanceInputEvent>);
static_assert(std::is_nothrow_copy_assignable_v<NoteOwnership>);
static_assert(std::is_nothrow_copy_assignable_v<PedalNoteOwnership>);

PerformanceInputResult process_performance_input(
    Engine& engine, NoteOwnership& manual_ownership,
    PedalNoteOwnership& pedal_ownership, std::uint32_t frames,
    std::span<float> mono_output,
    std::span<const PerformanceInputEvent> input) noexcept {
    if (frames > kHardMaxBlockFrames) {
        return {Status::BlockTooLarge, 0, 0};
    }
    if (input.size() > kMaxEventsPerBlock) {
        return {Status::TooManyEvents, 0, 0};
    }
    std::uint32_t previous_offset = 0;
    for (const auto& record : input) {
        std::uint32_t offset = 0;
        if (!offset_and_kind(record, offset) || offset < previous_offset ||
            (frames == 0 ? offset != 0 : offset >= frames)) {
            return {Status::InvalidEvent, 0, 0};
        }
        previous_offset = offset;
    }

    NoteOwnership manual_candidate = manual_ownership;
    PedalNoteOwnership pedal_candidate = pedal_ownership;
    std::array<Event, kMaxEventsPerBlock> physical{};
    std::size_t produced = 0;
    for (const auto& record : input) {
        const auto remaining = std::span<Event>{physical}.subspan(produced);
        if (const auto* manual = std::get_if<HostNoteEvent>(&record)) {
            const auto result = manual_candidate.translate(
                frames, std::span<const HostNoteEvent>{manual, 1}, remaining);
            if (!result) return {result.status, 0, 0};
            produced += result.output_events;
        } else if (const auto* pedal = std::get_if<PedalNoteEvent>(&record)) {
            const auto result = pedal_candidate.translate(
                frames, std::span<const PedalNoteEvent>{pedal, 1}, remaining);
            if (!result) return {result.status, 0, 0};
            produced += result.output_events;
        } else {
            // The preflight above established a permitted Event alternative.
            // Payload validation remains Engine's single authoritative contract.
            if (remaining.empty()) return {Status::TooManyEvents, 0, 0};
            physical[produced] = *std::get_if<Event>(&record);
            ++produced;
        }
    }

    const auto processed = engine.process(
        frames, mono_output, std::span<const Event>{physical.data(), produced});
    if (!processed) return {processed.status, 0, 0};

    // No operation after Engine admission can fail. Install the two candidates
    // only after the one render/flush has accepted its complete emitted prefix.
    manual_ownership = manual_candidate;
    pedal_ownership = pedal_candidate;
    return {Status::Ok, static_cast<std::uint32_t>(input.size()),
            processed.events_consumed};
}

} // namespace hammond
