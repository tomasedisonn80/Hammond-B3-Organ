# Bounded external note ownership

`bounded-fifo-note-ownership-v1` converts typed external notes into the engine's
existing physical-key commands. It is a proposed software policy derived from
the [research atlas](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf), pp. 130, 132
and 151. It is not a physical Hammond mechanism, MIDI byte parser, VST3 ABI or
qualified host adapter. The implementation is
[NoteOwnership.h](../include/hammond/NoteOwnership.h) and
[NoteOwnership.cpp](../src/NoteOwnership.cpp).

This adapter commands binary physical-key targets through NoteOn and NoteOff.
Engine separately supports explicit partial-key targets and owns nine contacts
per manual key; uncoordinated direct partial-key input must not bypass this
adapter's ownership, as detailed below. Multiple external owners first pass
through this layer. Only the first owner depresses a physical key; only its final
release raises that key. This keeps a second channel's release from cutting off
an independently held note, without introducing extra oscillators or resetting
percussion readiness.

## Input and capacity contract

`HostNoteEvent` contains a relative `offset`, `kind`, `bus`, `channel`, `midi_note`,
`velocity` and signed 32-bit `note_id`. Bus 0 initially routes to Upper, bus 1 to
Lower. Both buses can be routed to either manual. Channels are 0 through 15.
Pitch values are explicit MIDI numbers 36 through 96, separate from source IDs.
These are software domains and capacity bounds, not measured instrument values.

| Kind | Required payload | Meaning |
| --- | --- | --- |
| `On` | MIDI 36–96; velocity 0–127; note ID -1 or nonnegative | Positive velocity requests an owner; zero velocity uses the release policy |
| `Off` | MIDI 36–96; velocity 0; note ID -1 or nonnegative | Release the matching identified or oldest unidentified owner |
| `AllNotesOff` | MIDI 0; velocity 0; note ID -1 | Retire all owners belonging to the supplied bus and channel |

The only supported negative note ID is -1. A nonnegative ID can be any value
through `INT32_MAX`. `Off` release velocity is intentionally unsupported; an
external protocol adapter must convert it to canonical zero. Other event kinds,
invalid field combinations and out-of-range bus/channel values reject.

The adapter has fixed storage for **256 simultaneous owners**, regardless of
their distribution across the 122 physical keys. Every call admits at most
**1,024 input commands** and emits at most **1,024 physical events**. The supplied
output span may impose a smaller limit. More than 65,536 frames returns
`BlockTooLarge`. Positive calls require `offset < frames`; zero-frame flushes
require offset zero. Input offsets must be nondecreasing. Equal offsets retain
the exact supplied order; the adapter does not sort or coalesce commands.

## Matching and release policy

Identified owners use `(bus, channel, note_id)` as their identity. Pitch and
original destination are retained attributes:

- Repeating an identified `On` with the same pitch is idempotent, even if its
  velocity or the bus's current route changed. It creates no owner or event.
- An identified `On` or release that finds the same identity with a different
  pitch rejects the complete call. It never silently steals or retunes an owner.
- Releasing an absent identity is an accepted no-op. After a proper release,
  the ID can be reused for a different pitch, including at the same offset.
- Identical IDs on different buses or channels are distinct owners.

Unidentified `On` commands each add an owner. Unidentified release uses **FIFO**
among owners with note ID -1 and matching bus, channel and pitch. It never releases
an identified owner. A release with no matching unidentified owner is a no-op.
The fixed array preserves surviving insertion order; it uses no monotonically
increasing sequence counter that could wrap during a long session.

First ownership of `(manual, MIDI pitch)` emits `EventType::NoteOn` with the
input's original positive velocity. Additional owners emit nothing. Velocity
does not scale the engine's sustained amplitude. Removing the final physical
owner emits `EventType::NoteOff` with value zero. Remaining output entries are
untouched. No `Engine::AllNotesOff` is emitted by this adapter.

Channel `AllNotesOff` retires only owners with the requested original bus and
channel. Other buses/channels continue holding their keys. Retirement scans
surviving insertion order; a physical NoteOff is emitted when that scan removes
its final owner. This defines the order of multiple emitted events at one offset.
It is an ordinary release trajectory in nominal contact mode, not an immediate
physical-contact panic.

## Routing changes and state ownership

`set_bus_route()` and `set_routes()` validate before mutation. They affect future
owners only. An owner retains its original manual until it is released, as the
atlas explicitly requires on p. 151. For example, an unidentified upper C owner
can remain held while bus 0 is changed to Lower and another unidentified C owner
is added. The first FIFO release raises the original upper C; the second raises
the lower C. An identified duplicate retains its original upper destination.

Route changes are explicit calls at processing boundaries, not timestamped
events. To schedule one within a host block, split processing at that timestamp
under a separately defined host command order. The class has no UI, transport,
sample-rate or wall-clock dependency. All access is stopped or on the same
processing thread; its copied diagnostics provide no concurrent snapshot protocol.

The adapter should be the single playing-note authority for its physical keys.
Uncoordinated direct Engine note/panic calls can invalidate ownership. Cancel,
bank selection and control restoration do not release keys and do not require an
ownership reset. A deliberate global panic must atomically coordinate Engine's
physical release with retirement/replacement of the external ownership state.
There is no convenience reset method that silently clears owners while leaving
the engine's keys held. Replacing this object with a default instance resets its
routes too; that is only appropriate within a coordinated stopped/reset action.

## Transactional translation and Engine consumption

`translate(frames, input, output)` returns `NoteOwnershipResult` with `status`,
`input_consumed` and `output_events`. On success all input commands are consumed,
including duplicates and unmatched releases; only the reported output prefix is
written. Empty output is valid when translation emits no physical changes.

Every failure preserves the complete adapter and every output entry and reports
both counts as zero:

| Status | Rejection |
| --- | --- |
| `InvalidEvent` | Invalid payload, offsets, order or an identified pitch conflict |
| `TooManyEvents` | More than 1,024 inputs, a 257th simultaneous owner, or insufficient/bounded physical output capacity |
| `BlockTooLarge` | More than 65,536 frames |

Structural validation precedes state work. Dynamic identity and capacity checks
run against a value-owned candidate and a fixed output array. Only complete
success copies the output prefix and installs the candidate. No allocation,
deallocation, logging, file access or lock occurs. Work is bounded by the input
and owner capacities; identity lookup and individual erasure are linear in at
most 256 owners. Channel retirement compacts survivors in one pass. Physical-key
counts use fixed 16-bit counters whose maximum is 256.

The object is 3,328 bytes and `Event` is 16 bytes on the observed GCC/Linux build;
these are build observations, not portable ABI promises. Translation additionally
uses one candidate and a 1,024-event array on the stack. Overflow reporting uses
the returned status. A host may count rejected calls outside this state; no
internal counter changes on a failure because that would break the transaction.

Translation success does **not** establish that Engine accepted the events. For
one atomic ownership/audio operation, copy the adapter, translate with that copy,
call Engine with the emitted prefix and install the candidate only if Engine
accepts. An unprepared engine, invalid output buffer or render-clock overflow
must not leave committed owners without corresponding physical keys. Assignment
29 owns that integration wrapper and its acceptance evidence.

## Verification and remaining scope

Assignment 25's strict Release compilation and 35 initial assertions passed;
the retained [implementation note](development/2026-11-13-continuation/25-note-ownership.md)
records the observed scope. Independent permanent tests are a separate wave-5
assignment and must cover capacities, invalid whole-call rejection, duplicate and
FIFO policies, route changes, channel isolation, stable ties and block partitioning.

No sustain-controller policy, pedal playing keys, raw MIDI decoding, native host
export, re-strike gesture, contact calibration or deadline qualification follows
from this implementation. The actual contact and shared-readiness contracts are
in [CONSOLE_DYNAMICS.md](CONSOLE_DYNAMICS.md); their dynamic state remains separate
from external ownership and from saved musical controls.
