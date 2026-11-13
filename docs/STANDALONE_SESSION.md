# Standalone Session contract v1

**Frozen interface, not an implementation result.**
[`Session.h`](../apps/standalone/Session.h) defines the SDK-free boundary for
the optional native application. Wave 3 implements it without changing the
core, public parameter identities, state formats, profiles or VST3 UUIDs.
The model identifier is `standalone-callback-boundary-session-v1`.

This contract implements [the standalone scope](STANDALONE_SCOPE.md) and the
wave 1 [product review](development/2026-11-13-next-phases/05-atlas-product.md)
and [closure review](development/2026-11-13-next-phases/06-atlas-closure.md).
Their source basis is atlas pages 379-396, 425, 433-434, 442, 450 and 453.
The current core headers and behavior remain authoritative for musical payloads.

## Ownership and public calls

`hammond::standalone::Session` owns exactly one Engine, one NoteOwnership and
one PedalNoteOwnership. The Engine's default routes remain manual bus 0 to
Upper and bus 1 to Lower. The two pedal buses are separate origin namespaces
for the same 25 pedals. Session exposes no mutable Engine, queue slot or ledger.

| Caller | Permitted operations | Constraint |
| --- | --- | --- |
| One main/UI producer | `post(SessionCommand)` | Serial calls only, including any future external input forwarded by that thread. |
| One audio consumer | `render(frames, stereo)` | One serialized callback; never overlapping invocations. |
| Snapshot observers | `read_snapshot(destination)` | Copied atomic publication; failure preserves destination. |
| Main thread with all callbacks and readers quiescent | Construction, destruction, `prepare`, `start`, `stop` | Device pause/close and callback completion are the application's responsibility. |

A second producer, overlapping callbacks, lifecycle calls racing processing,
or destruction while an observer is active violate the API precondition. No
runtime lock is added to make these unsupported usages appear safe. A callback
thread may change between device opens only after the previous consumer stops.
The constructor may allocate its PIMPL; prepare may initialize fixed storage.
All allocation, reclamation, device handling, parsing, formatting, logging and
file access remain outside `post`, `render` and `read_snapshot`.

## Commands, identity and timing

`SessionCommand` is a bounded copied variant of `PerformanceInputEvent`, an
entire `ControlSnapshot`, `ReleaseUiNotes`, or `Panic`. Its storage and queue
contain no borrowed pointer or dynamically sized object.

| Command | Boundary behavior |
| --- | --- |
| `PerformanceInputEvent` | Use `process_performance_input` with the shared Engine and both existing ownership adapters. Manual/pedal note identity, duplicate ownership, release matching and payload admission retain their core contracts. The Event alternative permits only the existing musical control types. |
| `ControlSnapshot` | Validate the whole value before enqueue and call `Engine::restore_controls` in FIFO order. Retain held notes, contacts, readiness, source phases and clock; do not restore a DSP checkpoint. |
| `ReleaseUiNotes` | Submit typed channel-AllNotesOff records for channel 0 on both manual buses and both pedal buses, through `process_performance_input`. Final-owner release rules preserve independently held notes on channels 1-15. |
| `Panic` | Clear every manual/pedal owner and physical key/contact. Use one coordinated zero-frame Engine panic transaction and reset both ledgers only on its success, or an equivalent demonstrated ownership-safe operation. Retain musical controls, readiness, source phases and clock. |

UI uses `kUiInputChannel == 0`; distinct nonnegative note IDs identify physical
computer-key slots, pointer playing and focused-key audition. A press captures
its bus, channel, note/pedal and note ID. Release uses that original identity
after a manual, octave or focus change. Session neither remaps these identities
nor generates keyboard-repeat presses. Channels 1-15 remain admissible for
independent owners, even though this slice does not promise a MIDI device adapter.
An explicit global panic can affect those owners; normal UI release cannot.

Every performance offset must be **zero**. These messages have no acquisition
timestamp: they are applied before the first sample of the next callback that
captures them. A producer append after the callback captures its queue prefix
waits until a later callback. FIFO order breaks ties across notes, controls,
restores, releases and panic. Do not silently convert a nonzero offset or claim
sample-accurate hardware acquisition. At zero frames, the same boundary applies
once without source, contact, readiness or frame-clock advancement.

`post` rejects nonzero offsets, non-control physical Event alternatives and
invalid whole snapshots immediately with `InvalidCommand`, sequence zero and
no musical or queue change. Other payload checks and ownership-dependent
conflicts/capacity remain at the core's authoritative consumer admission; a
successful enqueue is not evidence that such a command later applied.

## Queue admission, acknowledgment and recovery

There are exactly **256 usable command slots**. Do not silently reserve one
slot while advertising 256. Successful posts receive increasing nonzero
sequences, starting at one. Invalid or failed posts receive zero. The producer
publishes a fully copied slot with release semantics; the consumer acquires the
published cursor. The consumer releases a slot only after its outcome is known.
No thread reads an ordinary slot while the other can mutate it.

Each render captures one upper sequence bound and applies at most 256 commands;
it must not drain until empty while the producer keeps appending. Process FIFO
commands as zero-frame transactions, then make one positive-frame core render
with no duplicated boundary events. Coalescing or batch rejection must not alter
observable FIFO behavior. The complete callback is not a rollback transaction:
earlier successfully applied controls survive a later rejected command.

`last_applied_sequence` identifies the newest command actually applied.
`resolved_sequence` identifies the highest queued sequence whose outcome is
final, including rejected or discarded commands. A resolved sequence is **not**
a successful load acknowledgment. After recovery, the UI must use the published
controls and reset pending optimistic edits; it must not replay discarded notes
or assume a discarded restore succeeded. For save, copy published controls only
after the desired edit has been resolved without a new rejection/recovery. File
serialization itself uses the existing strict control-state format off callback.

### Overflow is a global recovery boundary

On a full queue, the failed command is not enqueued. `post` returns `QueueFull`,
records the overflow and raises a lock-free out-of-queue recovery request. This
request cannot itself fail because the queue is full. Until the consumer has
published recovery acknowledgment, subsequent posts return `RecoveryPending`
without changing the queue or allocating another recovery generation.

At the first **valid** callback boundary that observes the request, the consumer
discards the accepted pending prefix, performs a coordinated global panic,
publishes empty held keys/pedals and the still-current controls, increments
`recovery_count`, and releases the producer barrier. QueueOverflow is sticky.
The failed post counts as an overflow; `discarded_commands` counts accepted
queued commands actually discarded, not that failed post. The resolved cursor
advances across those discarded sequences. Controls already applied in an
earlier callback remain installed; a discarded queued restore does not apply.
The current valid callback then renders its requested elapsed frames normally.

The request can race a callback that has already captured its boundary. In that
case that callback may finish its captured work; the request remains latched
until a subsequent valid boundary recovers. Producer publication remains blocked
through recovery acknowledgment, so no accepted post can cross the discarded
epoch and later reappear. The implementation must prove this interleaving,
including release/acquire ordering; a plain shared Boolean is insufficient.

Global recovery is intentional: accepted typed events can originate from any
channel, and discarding another channel's queued release must not strand it.
Normal focus loss still posts the scoped `ReleaseUiNotes`. The UI clears its
gesture records after overflow/recovery and suppresses already held physical
inputs until their release, requiring a fresh press to play again.

### Consumer rejection and sequence exhaustion

If a queued command fails authoritative core admission, that command has no
partial effect under the core transaction contract. Mark it resolved/rejected,
record its non-Ok core status and RejectedCommand, discard the unprocessed
suffix captured for that boundary, and perform global recovery before rendering.
Earlier successful commands remain applied. Atomically request the same producer
barrier used for overflow: posts that race this rejection may already be queued;
they must also be discarded at the recovery boundary, never replayed afterward.
That bounded extra prefix is at most the queue capacity and is not a new drain
loop. New posts are allowed only after the coherent recovery acknowledgment.
Thus command application is bounded to 256 and emergency discard may examine
one additional prefix of at most 256; neither path chases ongoing publication.

Counters and revisions never wrap. `SessionLimits` permits smaller finite command
and publication limits for real exhaustion tests; publication limits above
`UINT64_MAX / 2` reject prepare as `InvalidSpec`. Command-sequence exhaustion
returns `SequenceExhausted`, requests global recovery, and permanently disables
further posts for that Session. Stopped recovery remains possible; replacing the
Session after full quiescence is the way to obtain new sequence capacity.
Diagnostic counts saturate rather than wrap.

Publication exhaustion must be preflighted before consuming commands or advancing
audio. Latch exhaustion, reject processing with `SequenceExhausted`, and make
`read_snapshot` fail without changing its destination rather than returning a
fresh-looking stale acknowledgment. Clear ownership with a zero-time panic even
when no publication remains; output is silenced by the device adapter. This is
an emergency safety action, not successfully rendered frames or a new published
snapshot. No later prepare/start resets finite lifetime counters.

## Lifecycle and audio contract

1. Construct Session with callbacks absent. Before preparation its coherent
   snapshot has default controls, no holds, sample rate/clock/peak zero and
   prepared/running false. Revision zero is that initial publication and does
   not consume a configured publication allowance.
2. Call `prepare(profile, ProcessSpec)` while stopped. Validate all inputs and
   candidates before mutation; support exactly 44,100, 48,000 and 96,000 Hz,
   `max_block_frames` in 1-65,536, and the core seed/initial-frame semantics.
   Success prepares a new nominal ideal-contact Engine, discards pending
   commands, clears both ledgers, publishes stopped state and peak zero.
   Reprepare is a fresh DSP preparation, not phase-preserving rate migration.
   Failures preserve the previous musical state, queue and lifecycle.
3. Core default registrations stay muted: all four retained banks and both
   pedal mixtures zero, B selected, routes enabled, expression one and existing
   percussion defaults. Any immediately playable app registration is an explicit
   proposed `ControlSnapshot` posted by the application, with its own identity.
4. A prepared stopped Session accepts queued commands. Call `start()` before
   unpausing the device; it publishes running state, preserving pending commands.
   Starting unprepared returns `NotPrepared`; starting already running returns
   `AlreadyRunning` without mutation. Preparing while running also returns
   `AlreadyRunning`.
5. `render(frames, interleaved_stereo)` requires running state, a frame count at
   or below the prepared maximum, no frame-clock overflow, and exactly
   `2 * frames` output floats. Zero frames requires an empty span. Byte-count,
   sample-format, endian, channel and device-buffer validation belong to the
   transport before forming that span. No resampling or implicit chunking.
6. Rejection order is lifecycle, block bound, output length, timeline bound,
   then publication availability. Before that admission completes, consume no
   command, change no musical state and leave caller output untouched. A failed
   result has zero `frames_rendered`. The device callback clears its complete
   valid output buffer on any failure and records the error off callback.
   Rejected render diagnostics may set RenderRejected and a core status; the
   next coherent publication carries them. Exhaustion has the emergency
   ownership exception specified above.
7. Render one mono core frame per requested frame into prepared fixed storage,
   then copy each sample unchanged to L and R. No limiter, clipping, normalization,
   effects, extra source advance or host-dependent gain. Peak is the
   maximum absolute mono sample of the last positive successful callback, in
   normalized engineering sample units; it may exceed one. A zero-frame flush
   preserves the preceding peak. Positive silent callbacks still advance time.
8. To stop, first pause or close the actual audio device and wait for every
   callback to return, then call `stop()`. It performs global zero-time panic,
   resolves/discards pending commands, publishes stopped state and peak zero,
   while preserving controls, source phases, readiness and frame clock. It is
   idempotent for a prepared Session; unprepared returns `NotPrepared`.
   Another start resumes that source state with no wall-clock catch-up.
9. To change rate/buffer/profile, quiesce and stop first, save copied controls if
   desired, prepare the new spec, explicitly post those controls and start the
   new device. This path releases notes and resets DSP as declared in step 2.
   Destroy only after callbacks and readers are quiescent.

An unexpected failure of a recovery panic or final core render sets CoreFailure,
retains the failing core status, returns `CoreFailure` with zero rendered frames,
and blocks further command admission pending stopped lifecycle recovery. No
rollback of already applied boundary commands or already advanced core frames
is claimed. The audio-device layer owns finite/range guards and their diagnostic
counters; Session introduces no extra output law or clipping behavior.

## Coherent snapshot publication

Every successful render, including a zero-frame flush, publishes the fields in
SessionSnapshot as one observation. Lifecycle publications occur only while
quiescent. Use atomics for every concurrently observed payload cell and a
coherent even revision, or another equally demonstrated bounded scheme. A
seqlock around an ordinary concurrently written C++ struct is a data race and
does not satisfy this contract. Use always-lock-free atomics on supported
targets; unsupported targets must fail build/admission instead of using hidden
locks. Read at most eight times; return false without changing destination when
busy. No reader can stall the audio writer.

The snapshot describes applied controls, logical physical held targets, current
frame clock, last callback peak, lifecycle and fault accounting. It is not the
producer's requested state, a per-owner list, a contact trajectory, a DSP
checkpoint, elapsed wall-clock time, a calibrated acoustic level or a device
latency measurement. Fault flags remain sticky for the object's lifetime;
successful ordinary calls do not clear `last_core_status` after an error.

## Wave 3 acceptance requirements

Implement `apps/standalone/Session.cpp` and standalone-local tests without any
SDL/host SDK dependency. An integrator owns build wiring. The following gates
must execute against one coherent source tree; a header compiling is only an
interface check.

| Gate | Required assertions and retained evidence |
| --- | --- |
| Header and core isolation | C++20 include/compile with core includes only; no SDL/VST3 types or links; command/snapshot value-copy traits; source audit proves one shared Engine and existing ownership processor. |
| Nominal defaults and rates | All initial controls match unmodified Engine at each supported rate; invalid/NaN/infinite rate, zero/over-hard bound and invalid profile preserve a precharged stopped Session. An app registration requires explicit enqueue. |
| Exact core parity | Use the same profile, seed, initial controls and boundary schedule in Session and direct Engine/ownership calls. Assert bit-identical mono-to-both-channel output and final controls/holds/clock at all three rates. Compare irregular partitions only with identical absolute event boundaries; a changed callback boundary legitimately changes UI event timing. |
| FIFO boundary | Interleave On, restore, control edit, Off, scoped release and Panic; prove stable order, no source advance during flush, no duplicate events, post-after-capture deferral, and correct peak for positive/zero frames. |
| Ownership | Keyboard/pointer overlap, both manuals, both pedal origins, repeated identified On, original release identity, channel0 plus independent-channel coincidence, scoped release preserving independent owners, and global panic clearing all. Cancel only changes routing. |
| Restore and save | All four banks, two pedal controls, selections, route enables, expression and percussion copied atomically; invalid snapshot rejected without partial application; held state and phase/readiness preserved by valid restore; no transient state serialized. |
| Queue pressure | Fill all 256 usable slots, fail the 257th including a note-off/restore/Panic, verify the failed post is never applied, accepted suffix discard accounting, sticky fault and global release. Exercise a request racing an active captured callback and recovery acknowledgment before producer resumption. No stranded independent-channel release. |
| Consumer rejection | Queue invalid payload, conflicting note ID and 257th simultaneous owner after precharged valid work; prove core rejection, retained earlier controls, bounded suffix discard, global recovery and no later replay of raced producer posts. |
| Exhaustion | Use small SessionLimits to exhaust command and publication sequences; no wrap, reuse, false success or stale snapshot acknowledgment. Exercise sequence exhaustion while notes are held and while stopped. |
| Lifecycle and bad calls | Actual start/stop/reprepare loops with callbacks explicitly quiesced; invalid buffer/frame/timeline calls preserve music and queue; stop clears owners/pending input yet preserves controls/phase/clock; no catch-up while stopped; destroy only after join. |
| Publication under contention | Producer and callback stress with a real concurrent reader; paired control patterns and held/clock/peak invariants never tear; bounded read failures are permitted. Run a race detector where supported and retain unsupported runner limits. |
| Callback resources | Calibrated allocation/deallocation hook catches a deliberately allocating control, then sees zero operations inside real render on normal, restore, maximum pressure, recovery, invalid and zero-frame paths. Audit hidden locks/I/O; measure bounded work separately from deadlines. |

For every gate retain the exact source/profile/toolchain identity, commands,
observed counts, failures and corrections. Tests of Session do not qualify a
native device, actual SDL callback, desktop interaction, physical latency,
underruns, accessibility, hardware fidelity or a complete M9 product. Later
backend/UI work must execute those separate gates.
