#pragma once

#include "hammond/Engine.h"
#include "hammond/NoteOwnership.h"
#include "hammond/PedalNoteOwnership.h"

#include <cstdint>
#include <span>
#include <string_view>
#include <variant>

namespace hammond {

inline constexpr std::string_view kPerformanceInputModelId =
    "bounded-single-clock-performance-input-v1";

// One global timeline. The active alternative owns its complete offset/payload.
// The Event alternative accepts only Drawbar, BankDrawbar, SelectBank, Cancel,
// Expression, Percussion, PedalDrawbar and SelectPreset. Physical note/partial-key/panic Event
// alternatives reject: manual and pedal note authority belongs to the two typed
// ownership adapters. Values and their variant carry no dynamic storage.
using PerformanceInputEvent = std::variant<HostNoteEvent, PedalNoteEvent, Event>;

struct PerformanceInputResult {
    Status status{Status::Ok};
    std::uint32_t input_events_consumed{0};
    std::uint32_t physical_events_consumed{0};

    [[nodiscard]] constexpr bool ok() const noexcept { return status == Status::Ok; }
    [[nodiscard]] constexpr explicit operator bool() const noexcept { return ok(); }
};

// One transaction across both external ownership namespaces and Engine. Input
// offsets must be globally nondecreasing; ties retain the supplied order across
// all alternatives. Positive calls require offset < frames, zero calls offset 0.
// Maximum 1024 raw records and 1024 combined emitted notes/controls; a channel
// panic can expand to several final-owner releases. Existing per-adapter owner
// limits remain independent. No supported record is dropped to fit a capacity.
//
// Admission order: hard block bound; raw count; global offsets/control-kind
// preflight; candidate ownership simulation and aggregate output capacity; then
// Engine's full prepared/block/buffer/clock/control-payload admission. No live
// state or caller output changes before all admission succeeds. All failures
// report zero counts and preserve both adapters, Engine and caller output.
//
// Success calls Engine::process exactly once, even with no input or disconnected
// output, then installs both value-owned candidate adapters. It consumes all raw
// records, including duplicates and unmatched releases. Physical count includes
// every admitted control and each emitted note/release. Zero-frame flushes edit
// controls/ownership once without source, contact, readiness or clock advancement.
// No allocation, deallocation, locks, I/O, parsing or host SDK is involved.
//
// Use on the sole processing thread or while stopped. These owners must be the
// sole authority for their physical notes. Do not interleave direct physical
// Engine events or replace/reprepare Engine while retaining stale owners. A full
// reset must coordinate all three objects; musical control restore is not a
// note-owner reset. The existing manual-only process_owned_notes stays separate.
[[nodiscard]] PerformanceInputResult process_performance_input(
    Engine& engine, NoteOwnership& manual_ownership,
    PedalNoteOwnership& pedal_ownership, std::uint32_t frames,
    std::span<float> mono_output,
    std::span<const PerformanceInputEvent> input) noexcept;

} // namespace hammond
