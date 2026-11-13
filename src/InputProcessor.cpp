#include "hammond/InputProcessor.h"

#include <array>
#include <type_traits>

namespace hammond {

// The transaction relies on fixed, nonthrowing value copies rather than a
// dynamically allocated host container. Keep that dependency explicit.
static_assert(std::is_trivially_copyable_v<NoteOwnership>);

InputProcessResult process_owned_notes(
    Engine& engine, NoteOwnership& ownership, std::uint32_t frames,
    std::span<float> mono_output, std::span<const HostNoteEvent> input) noexcept {
    NoteOwnership candidate = ownership;
    std::array<Event, kMaxEventsPerBlock> physical_events{};
    const auto translated = candidate.translate(frames, input, physical_events);
    if (!translated) {
        return {translated.status, 0, 0};
    }

    const auto processed = engine.process(
        frames, mono_output,
        std::span<const Event>{physical_events.data(), translated.output_events});
    if (!processed) {
        return {processed.status, 0, 0};
    }

    // Engine's success contract consumes its full prefix. The candidate's
    // nonthrowing value assignment is the only remaining state change.
    ownership = candidate;
    return {Status::Ok, translated.input_consumed, processed.events_consumed};
}

} // namespace hammond
