# Transactional note input processing

`process_owned_notes()` connects the bounded external ownership policy to the
existing physical-key engine. It implements one accepted or rejected operation
across both objects. It does not define a new instrument model, native host ABI,
MIDI byte protocol or device callback.

The source basis is the [research atlas](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf),
pp. 130, 132 and 151: external owners precede physical-key targets, releases retain
their original manual, ordering is deterministic and elapsed samples alone advance
shared DSP history. The wrapper is an original software implementation of those
ownership boundaries. Its behavior is separate from measured contact physics.

## Public interface

Include [InputProcessor.h](../include/hammond/InputProcessor.h):

```cpp
InputProcessResult process_owned_notes(
    Engine& engine,
    NoteOwnership& ownership,
    std::uint32_t frames,
    std::span<float> mono_output,
    std::span<const HostNoteEvent> input) noexcept;
```

`InputProcessResult` has `status`, `host_events_consumed` and
`physical_events_consumed`, plus `ok()` and an explicit Boolean conversion.
`status` uses the existing `Status` vocabulary. Success consumes the complete
host input, including accepted duplicates and unmatched releases. Physical counts
refer to the prefix that Engine actually consumed. They can be zero for an
ownership-only change, or exceed the host count when one channel release retires
several physical keys. Every failure reports both counts as zero.

The input policy, fields, limits and matching rules are specified in
[NOTE_OWNERSHIP.md](NOTE_OWNERSHIP.md). They are not duplicated or relaxed here.
The engine's sample, buffer and timeline rules remain in
[ENGINE_API.md](ENGINE_API.md) and [CONSOLE_DYNAMICS.md](CONSOLE_DYNAMICS.md).

## Commit sequence and failure behavior

The implementation in [InputProcessor.cpp](../src/InputProcessor.cpp) performs
four steps on the processing thread:

1. Copy the current `NoteOwnership` into a local candidate.
2. Translate all host events with that candidate into a fixed 1,024-event array.
3. Call `Engine::process()` with exactly the emitted prefix and the original
   frame count/output span.
4. Install the candidate only after Engine returns success.

Translation rejects before Engine is called. Engine preflights its complete
request before changing audio or state. The final ownership assignment is a
nonthrowing fixed-value copy; a compile-time assertion requires the ownership
type to remain trivially copyable. The wrapper therefore does not need to copy
the complete engine for each audio block.

A rejected call preserves the live ownership object, the complete engine and
every output sample. No partial input prefix is accepted or retried internally.
The caller decides whether to retry, report the failure or clear its output
outside this transaction. The wrapper does not silently fill output with zero.

Error precedence is deliberate: translation runs first, then Engine admission.
For example, malformed host input returns `InvalidEvent` even if Engine is not
prepared. Valid host input with an unprepared Engine returns `NotPrepared` and
does not install the translated owners.

| Status | Relevant condition |
| --- | --- |
| `InvalidEvent` | Host payload, timestamp/order or identified-pitch conflict |
| `TooManyEvents` | More than 1,024 host inputs, a 257th simultaneous owner, or more than 1,024 emitted physical events |
| `BlockTooLarge` | More than 65,536 frames, or more than Engine's prepared maximum block size |
| `NotPrepared` | Engine has not been successfully prepared |
| `InvalidBuffer` | A nonempty output span is shorter than the requested frame count |
| `TimelineOverflow` | Advancing Engine's 64-bit rendered-frame clock would overflow |

## Time, output and controls

Stable same-offset input order is preserved through translation and Engine
dispatch. Positive offsets are half-open: `offset < frames`. Zero-frame calls
accept only offset-zero input. They can install ownership and physical targets
without advancing source phase, contact motion, percussion readiness or time.
No same-offset release/repress invents a recovery interval.

An empty output span means disconnected output for positive calls. Engine still
processes all frames and advances every dynamic subsystem. Empty host input also
processes the elapsed frames; it is not a request to freeze the engine. Output
entries beyond the requested frames remain unchanged under Engine's contract.

This function accepts only host-note input. Same-thread control-only events and
control snapshots may still change drawbars, preset routes, expression or
percussion without changing external ownership. It does not merge separate host
automation and note streams or assign a priority between them. A future adapter
must define their common order, or split processing at control timestamps and
apply the intended boundary order explicitly.

Changing a bus route affects future owners only. Existing owners retain the
manual stored when they were created. Such routing changes currently occur at
processing boundaries, not inside the host-note event format.

## Single note authority and coordinated lifecycle

The supplied ownership object must be the sole playing-note authority for the
physical keys it controls. Uncoordinated direct `Engine` NoteOn, NoteOff,
partial-key or manual AllNotesOff commands bypass the bookkeeping. Multiple
independent ownership objects targeting the same physical key would have the
same problem: one object's final release could raise a key another still owns.
Merge those input origins through one ownership instance instead.

For a safe ordinary channel release, submit one `HostNoteKind::AllNotesOff` with
the original bus/channel, `midi_note = 0`, `velocity = 0`, `note_id = -1` and a
valid offset through this wrapper. It removes only that input channel's owners
and emits final-owner NoteOffs. Other owners remain effective. With nominal
contacts, those NoteOffs follow normal release travel; they are not an immediate
contact panic. Releasing every bus/channel requires at most 32 such commands
and at most 122 final physical releases, within the fixed capacities.

An intentional immediate full panic is a separate coordinated action. A stopped
or same-thread caller must stage the intended cleared ownership state and both
manuals' Engine AllNotesOff actions, validate their complete application, then
publish both states together. It must preserve configured routes if the policy
calls for that. Simply assigning an empty ownership object can strand Engine
keys; simply panicking Engine can leave owners that suppress a later NoteOn.
No convenience reset is provided here that hides either half of this policy.

Successful `Engine::prepare()` starts a new dynamic state and clears physical
keys. Retaining old external owners across that reset is invalid. Prepare a
candidate engine and a corresponding fresh or deliberately rebuilt ownership
state, then install them together only after preparation succeeds. A rejected
preparation must preserve both previous objects. Ordinary Cancel, bank selection
and musical-control restoration retain keys and do not require such a reset.

All calls and diagnostics require stopped or same-processing-thread access.
There is no concurrent UI publication or automatic transport-reset policy.
The API expects valid caller-owned spans, as do its component APIs; it does not
validate arbitrary pointers, lifetimes or overlapping object storage.

## Storage and qualification boundary

The wrapper uses one automatic ownership copy and one fixed event array. Its
translation call temporarily uses another ownership copy and event array inside
`NoteOwnership::translate()`. No container grows and no allocation, file access,
lock, logging or SDK call occurs. The bounded capacities limit all work, but do
not constitute a measured callback deadline.

On the observed GCC/Linux build, `sizeof(NoteOwnership)` is 3,328 bytes and
`sizeof(Event)` is 16 bytes. The two ownership copies and two 1,024-event arrays
account for 39,424 bytes of declared nested automatic objects during translation.
That excludes other locals, call frames, caller storage, alignment and compiler
optimization; it is not a portable exact stack-usage promise. Future runtime
audits must include this enabled path and the intended host stack budget.

Assignment 29 records focused implementation checks in its
[handoff note](development/2026-11-13-continuation/29-input-processor.md).
Assignment 30 independently verifies rollback, future audio/state equivalence,
multiple owners, route changes and disconnected/zero-frame behavior. Hosted
platform, allocation instrumentation, raw MIDI/controller policy, native host
integration and device deadline qualification remain distinct gates. No current
result establishes a physical B-3 match.
