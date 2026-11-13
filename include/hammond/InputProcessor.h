#pragma once

#include "hammond/Engine.h"
#include "hammond/NoteOwnership.h"

#include <cstdint>
#include <span>

namespace hammond {

struct InputProcessResult {
    Status status{Status::Ok};
    std::uint32_t host_events_consumed{0};
    std::uint32_t physical_events_consumed{0};

    [[nodiscard]] constexpr bool ok() const noexcept { return status == Status::Ok; }
    [[nodiscard]] constexpr explicit operator bool() const noexcept { return ok(); }
};

// One transaction across external ownership and the existing physical-key engine.
// Translate with a private ownership copy and fixed event storage, process the
// emitted prefix, then install ownership only after Engine accepts the whole call.
// Any failure preserves live ownership, Engine and every output sample, and
// reports both counts as zero. Translation errors precede Engine admission errors.
// Success consumes every host command, including duplicates/unmatched releases;
// physical_events_consumed can be smaller or zero; one channel release can also
// emit several physical releases. No input is retried internally.
//
// The NoteOwnership bounds and Engine's prepared block/buffer/clock limits all
// apply. Stable equal-offset ordering, zero-frame flushes and disconnected output
// retain their existing semantics. Empty host input still processes elapsed frames.
// Uses fixed automatic storage; no allocation, I/O, locks or host SDK. Call only
// while stopped or on the processing thread; no concurrent publication protocol.
//
// The supplied ownership object must be the sole note authority for its physical
// keys. Do not interleave uncoordinated direct Engine note/partial-key/manual-panic
// commands, replace ownership, or reprepare Engine while retaining old ownership.
// Channel releases go through this wrapper. A deliberate full panic/reset must
// coordinate both objects outside this operation; see docs/INPUT_PROCESSOR.md.
// Independent same-thread drawbar, preset, expression and percussion edits remain
// valid, but this function does not merge arbitrary note/control event streams.
[[nodiscard]] InputProcessResult process_owned_notes(
    Engine& engine, NoteOwnership& ownership, std::uint32_t frames,
    std::span<float> mono_output, std::span<const HostNoteEvent> input) noexcept;

} // namespace hammond
