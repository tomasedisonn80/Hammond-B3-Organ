# Typed pedal note ownership

`PedalNoteOwnership` translates bounded external pedal owners into the Engine's
Boolean physical pedal commands. It keeps explicit `PedalId` values separate
from manual MIDI pitches, source numbers and array indices. Two logical input
origins can share one pedal without one origin's release silencing the other.
This is the pedal counterpart of [manual ownership](NOTE_OWNERSHIP.md).

The identity is **`bounded-fifo-pedal-note-ownership-v1`**. Its ownership policy
is a software contract; it adds no physical contact timing or calibrated pedal
response. Engine alone owns the eight simultaneous ideal closures and the
[nominal voice](PEDAL_ENGINE.md), based on the documentary pedal domain in
[atlas pp. 139–150](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=139).

## Input domains

`PedalNoteEvent` contains `offset`, `kind`, `bus`, `channel`, `pedal`, `velocity`
and `note_id`. The adapter has no preparation step and initially owns nothing.

| Field | Admitted values and meaning |
| --- | --- |
| Kind | `PedalNoteKind::On`, `Off`, or `AllNotesOff` |
| Origin bus | 0 or 1; two software ownership namespaces targeting the same physical division |
| Channel | 0–15, scoped within its origin bus |
| Pedal | Checked one-based `PedalId{1}` through `PedalId{25}` for On/Off |
| Note identity | `-1` for anonymous; any nonnegative `int32_t` for identified notes |
| On velocity | Integer 0–127; zero means release; positive values do not scale steady amplitude |
| Off velocity | Exactly zero |
| Channel panic | `pedal.value == 0`, velocity zero and note identity `-1` |
| Offset | Positive calls: `0 <= offset < frames`; zero-frame calls: exactly zero |

Origin indices are not native VST3 event-bus indices. This adapter accepts no
MIDI octave convention or raw packet. The implemented [native processor](VST3_PROCESSOR.md)
validates its own bus/pitch domain before constructing these records: native
event bus 2 maps MIDI pitches 36–60 to `PedalId{1}`–`PedalId{25}`, using pedal
origin 0. Its native bus index is not stored as the pedal-origin index. The
[VST3 contract](VST3_SPIKE_CONTRACT.md) retains that separate software policy;
this mapping is not evidence of a physical MIDI-equipped pedalboard.

Inputs must already be in nondecreasing offset order. Equal offsets retain
supplied order. A zero-frame flush applies commands once and advances no clock.
The translator never renders or advances sources even for a positive frame count;
the count only bounds event offsets.

## Ownership semantics

The first owner of a physical pedal emits `PedalOn`; its final retirement emits
`PedalOff`. Every emitted event uses canonical `Manual::Lower` and the explicit
one-based pedal index. No third `Manual` value or lower-manual MIDI key is used.
The first On's positive velocity is retained in that physical event. Subsequent
owners do not emit duplicate physical presses or change its sustained amplitude.

An identified key is `(origin bus, channel, note_id)`. Repeating its On for the
same pedal is an accepted no-op, including at the owner-capacity limit. Reusing
the key for a different pedal rejects the complete call. Identified Off or
zero-velocity On also requires the matching pedal if that identity exists.
A missing matching release is accepted without changing anything.

Anonymous repetitions each consume a separate owner. Their releases remove the
oldest surviving anonymous owner with the same origin, channel and pedal.
They never consume identified owners. Snapshots retain surviving insertion order.

`AllNotesOff` retires only its selected origin/channel. It emits individual final
`PedalOff` events in owner retirement order, so other channels and origins keep
their claims. It never emits Engine's division-wide `PedalAllNotesOff`. An
empty channel panic is accepted, including with zero output capacity.

For example, origin 0 presses pedal 13, origin 1 presses it, then origin 0
releases. Only the first command emits a physical On; pedal 13 remains held until
origin 1 releases. Neither manual ownership nor upper percussion readiness is
stored or consulted by this adapter.

## Bounds, errors and transaction

Storage is fixed: 256 owner records and 25 physical counts. At most 1,024 raw
inputs and 1,024 emitted events are admitted per call, with a hard frame bound
of 65,536. Output capacity can be smaller; zero capacity works when no physical
change is required. A single scoped panic can emit multiple events, so raw and
emitted counts need separate limits. Larger output spans do not raise the limit.

Admission uses the same precedence as `NoteOwnership`:

1. An excessive frame count returns `BlockTooLarge`.
2. More than 1,024 input records returns `TooManyEvents`.
3. All static payloads, offsets and ordering are checked before simulation;
   any failure returns `InvalidEvent`.
4. A private value copy then applies the sequence in supplied order. An identity
   conflict returns `InvalidEvent`; owner or emitted-output exhaustion returns
   `TooManyEvents` at the command that encounters it.

Any failure preserves the complete live adapter and every caller output element,
including preceding valid work in the same call. Both returned counts are zero.
Success commits the candidate and writes only the emitted output prefix; the
unused tail is untouched. It consumes every raw command, including no-ops.
Releasing an owner early in a call can free its slot for a later On.

The implementation uses fixed automatic candidate/output storage. Searching and
compaction are bounded by the 256 owners; the complete callback cannot admit an
unbounded input or retry loop. No allocation, destruction of dynamic storage,
lock, I/O, parsing, Engine query or source access occurs. The class is trivially
copyable and has no caller-owned references. This design statement is distinct
from the later enabled-path allocation and callback-budget instrumentation.

## Combining ownership with Engine

`translate(frames, input, output)` commits ownership only. To make a complete
audio transaction, translate on an ownership copy, merge the resulting pedal
events with the manual/control events in their declared stable order, and call
Engine exactly once for that frame interval. Install candidate ownership only
after Engine accepts the full event sequence. Discarding a failed candidate
preserves release matching and future physical events.

Do not call a manual processing facade and then a pedal processing facade for
the same interval: each Engine call would advance the shared timeline. The
existing [manual-only facade](INPUT_PROCESSOR.md) remains unchanged. The
implemented [combined transaction](PERFORMANCE_INPUT.md) coordinates manual,
pedal and control input with one Engine call and commits both owner candidates
only after that call succeeds. The native [HostTimeline](HOST_TIMELINE.md) has
its own whole-callback candidate/slicing transaction over the same ownership
types; it does not call the combined facade separately for the same interval.

Use one coordinated authority for these physical pedals. Direct Engine
`PedalOn`, `PedalOff` or `PedalAllNotesOff` calls bypass the owner ledger. A full
reset must clear the adapter and Engine targets together while stopped or on the
processing thread. Fresh Engine preparation likewise requires a fresh adapter.
Musical control restore changes neither owners nor physical targets; snapshots
of owners are diagnostics, not entries in `B3CONTROLS3`.

`owner_count()` returns the total. `owner_count(PedalId, destination)` returns
the number sharing one pedal; `owner_snapshot(index, destination)` returns a
copied insertion-order record. Invalid queries leave the destination unchanged.
All methods require stopped or same-processing-thread access. They provide no
concurrent UI publication protocol.

## Executed acceptance and remaining gates

[The native unit test](../tests/test_pedal_note_ownership.cpp) declares expected
physical events and surviving owners independently. It covers every pedal and
all 32 origin/channel pairs, identified and anonymous overlap, FIFO retirement,
scoped panic, stable ties, invalid payloads, late rollback, 256-owner exhaustion,
1,024 raw/emitted boundaries, output-tail preservation, future events after
rejection and seven block partitions. The original manual adapter suite is run
unchanged against the same coherent core.

[Assignment 19](development/2026-11-13-pedals/19-pedal-ownership.md) records the
source identities, exact commands and actual results for the original adapter
gate. Later work has separate executed evidence for [combined Engine input](PERFORMANCE_INPUT.md),
[independent mixed-input acceptance](development/2026-11-13-pedals/24-input-acceptance.md),
[enabled core allocation](PEDAL_REALTIME.md), [actual native conversion and ABI](VST3_ABI_ACCEPTANCE.md)
and [native callback allocation](VST3_REALTIME.md). These results preserve their
named source, platform and instrumentation limits. Consult [current status](STATUS.md)
and the [operational handoff](PEDAL_HANDOFF.md) for the latest publication and
hosted outcomes; none of these software gates establishes physical pedal calibration.
