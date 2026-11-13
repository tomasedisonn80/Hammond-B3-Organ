# Concurrent control state exchange

`StateExchange` implements the fixed UI/audio handoff specified by
[VST3_SPIKE_CONTRACT.md, section 5](VST3_SPIKE_CONTRACT.md). It is SDK independent:
the queue contains copied `ControlSnapshot` values, never an `IBStream`, parser,
string, Engine pointer or host-owned view. Its model identity is
`bounded-spsc-control-state-exchange-v1`.

The source basis is the [research atlas](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf),
pp. 389–390, 393–394 and 400–401: controls are saved through safe publication;
concurrent readers, generations and state-load history need explicit tests;
presets do not represent complete DSP checkpoints. The exact queue capacity,
atomic payload, finite lifetime and retry budget are the engineering contract
in section 5, not physical Hammond specifications.

## Ownership and API

| Operation | Owner | Result and bound |
| --- | --- | --- |
| `ui_enqueue(snapshot)` | One serialized UI/main thread | Validate and copy one snapshot; return status and monotonically increasing accepted sequence. Capacity is four. |
| `audio_peek(batch)` | One audio thread | Copy zero to four current records without consuming them. The batch owns its copies. |
| `audio_can_commit(batch)` | Same audio thread | Check originating object, current consumer position, publication revision, queued range and publication lifetime before rendering. |
| `audio_commit(batch, current_controls)` | Same audio thread | Publish coherent controls/acknowledgement, then release consumed queue slots. All rejection checks precede mutation. |
| `read_published(destination)` | UI or additional observers | Read atomic storage only; at most eight attempts, then `false`. |
| `ui_snapshot_for_save(destination)` | Same serialized UI producer | Read a coherent publication; select the newest accepted UI snapshot while pending, or current published controls after acknowledgement. |

Methods perform no allocation, parsing, I/O, locks, waits or dynamic retry loop.
The eight-attempt reader is bounded. Audio publication has one fixed pass over
48 cells and does not wait for a reader. This is an algorithmic work bound, not
a platform audio-deadline measurement. Instrumented callback allocation and
timing qualification are a separate gate.

The two UI methods share producer-private data and **must not overlap on
different threads**. SDK wrappers must keep their main-thread state calls
serialized. `read_published` may have additional observers because it touches
only immutable configuration and atomic publication storage. Engine diagnostics
and `controls_snapshot()` remain audio-owned; this class does not make concurrent
direct Engine access safe.

The public batch offers only `snapshots()`, `size()` and `last_sequence()`.
Its origin, copied snapshots, count, consumer range and publication revision
cannot be changed through the API. A default batch, another exchange's batch,
or a batch from a prior successful publication is invalid. Even an empty
successful callback invalidates its old tokens. A token must not outlive the
exchange that produced it.

## Native callback transaction

The wrapper's order is part of the correctness contract:

1. Admit the complete host output shape and input views. Peek a state batch and
   call `audio_can_commit` **before** candidate processing.
2. Pass `batch.snapshots()` to `HostTimeline::process`, using private mono output.
   Timeline applies up to four restores before ordinary input and resets its
   automation anchors. The headers have no dependency on one another.
3. If the timeline rejects, omit `audio_commit`. Leave host output untouched;
   all queued states and their acknowledgement remain available for retry.
4. On complete timeline success, obtain its valid
   `timeline.engine().controls_snapshot()`, call `audio_commit` with the same
   token, then copy private mono output into already-admitted host channels.

Successful preflight guarantees the post-render commit succeeds under the
contract. The token captures the current audio consumer and publication revision;
only this audio thread changes them. The UI can only append, so its queued
sequence cannot move below the token's end and it cannot recycle unretired
slots. Publication exhaustion was already checked and only audio can advance
that counter. The remaining `audio_commit` check validates the caller's
snapshot; a successful Engine owns a valid snapshot. Thus there is no capacity
reservation, allocation or resource decision left after timeline success.

Calling another commit between preflight and commit, supplying an invalid
snapshot, using an expired token, or adding another audio consumer violates
those preconditions. `audio_commit` still rejects invalid inputs before its own
mutation, but a wrapper must not use such rejection as a normal late rollback
mechanism for an already-installed Engine.

## Queue ownership proof

The UI owns `producer_sequence_` and `latest_accepted_`; audio owns
`consumer_sequence_` and its publication revision. Opposite threads never read
those plain fields. Shared queue positions are atomic 64-bit values:

- UI writes a plain snapshot slot and then release-stores `queued_sequence_`.
  Audio acquire-loads that cursor before reading each included slot. The
  acquired release, or a later release from the same producer, orders all of
  those payload writes before the audio copies.
- Audio only release-stores `consumed_sequence_` after a successful callback's
  publication. The UI acquire-loads that cursor before deciding whether a slot
  can be reused. This orders the old audio slot reads before its overwrite.
- Producer minus consumed count cannot exceed four. A queue-full load is an
  explicit failure and leaves every pending record, the newest accepted UI
  value and every cursor unchanged. Validation precedes capacity checking.
- Peek copies into a value-owned batch without advancing the consumer. Appends
  can occupy only other free slots; they cannot change copied records or
  invalidate preflight. A commit retires exactly the captured range. A later
  append remains queued for another callback.

These two ownership transfers establish happens-before relationships for every
plain slot access. No plain snapshot is simultaneously read and overwritten.
Repeated peek, processing failure and delayed consumption do not release slots.

## Atomic publication proof

The payload contains exactly 48 `atomic<uint64_t>` cells:

| Cells | Meaning |
| --- | --- |
| 0–35 | Four manual banks of nine retained drawbar positions, in compiled descriptor order |
| 36 | Expression's binary64 representation, including the sign bit of zero |
| 37–38 | Upper/lower selected bank |
| 39–42 | Percussion enable, harmonic, volume and decay |
| 43–44 | Two pedal drawbar positions |
| 45–46 | Upper/lower route-enable bits, additional to the 45 exposed parameters |
| 47 | Last state sequence acknowledged by this publication |

The mapping does not introduce or change any stable parameter ID. Discrete
values retain their plain integer representation. Expression uses `bit_cast`,
not a numeric integer conversion. A compile-time assertion rejects a registry
count change until the explicit mapping is reviewed. A second set of assertions
requires binary64 and always-lock-free 64-bit atomics; an unsupported target
does not silently fall back to a library mutex.

Publication uses sequentially consistent operations throughout. The sole audio
writer stores an odd revision, stores every atomic payload cell, then stores
the next even revision. A reader loads a revision, skips odd values, loads all
cells, and loads the revision again. It accepts only matching even values.

All these atomic operations participate in a single order consistent with each
thread's program order. A writer's odd revision precedes its payload stores and
its even revision follows them. If a read overlapped a writer in a way that
could mix payload generations, the bracketing revision loads cannot both
observe the same even value. If both observe that even value, all accepted
cells belong to the completed publication it identifies. No counter can wrap
back to an older value. Every payload access is atomic even on a failed attempt,
so rejected mixtures do not create a C++ data race. This is not a seqlock over
plain, concurrently accessed `ControlSnapshot` storage.

After at most eight attempts, failure is explicit and preserves the entire
destination. There is no cached fallback presented as a successful fresh save.
A continuously publishing writer can cause bounded read failures; caller retry
policy belongs off the audio thread. A reader that stops or stalls owns no slot
and cannot block publication. Its next successful read observes a coherent
publication, and after audio quiesces a read returns the final one.

## Save selection, state migration and lifetime

Construction initializes coherent `ControlSnapshot{}` defaults, acknowledgement
zero and revision zero before activation. UI enqueue retains the newest accepted
snapshot privately. Save reads a coherent publication each time: if its
acknowledgement is below the UI sequence, save returns that newest accepted
snapshot; otherwise it returns published audio controls. Subsequent automation
therefore becomes visible after the load is acknowledged. A failed enqueue
never replaces the UI's pending save value.

`ControlStateIO` remains the byte boundary off audio. Parse bounded state bytes
into a local value, then enqueue only a completely validated result. Versions
1 and 2 migrate to muted pedal controls; version 1 also supplies the existing
percussion defaults. Serialize a successfully selected save snapshot as
`B3CONTROLS3`. Parsing errors and stream lifetime do not enter this queue. The
snapshot retains both route bits but contains no held keys, pedal contacts,
source phases, percussion readiness or processing clock.

`StateExchangeLimits` is immutable. Defaults allow `UINT64_MAX` accepted states
and `UINT64_MAX / 2` publications. Accepted sequences begin at one. Enqueue tests
its limit before adding one. Publications begin at revision zero and advance by
two; at the maximum limit the final even revision is `UINT64_MAX - 1`. Preflight
tests the publication count before the next odd/even pair can be formed.
Neither counter wraps, no reset API exists, and same-object token ABA is
excluded throughout the supported lifetime.

Smaller limits, including zero, are valid configurations and make exhaustion
directly testable without private-state mutation. A publication limit above
`UINT64_MAX / 2` fails closed: enqueue/peek/preflight/commit return `InvalidLimits`,
and copied reads return `false` without changing their destinations. Exhaustion
returns `SequenceExhausted` and retains all pending state. Replacement with a
new exchange requires actual callback/UI quiescence; a stopped flag alone does
not establish safe destruction or authorize resetting a live counter.

## Executed qualification and remaining work

`tests/test_state_exchange.cpp` checks four-slot saturation, copied ownership,
stale and foreign tokens, append-after-preflight, rejected callback retention,
signed-zero bits, invalid whole snapshots, defaults, exact finite lifetime
boundaries, canonical v1/v2/v3 state migration and serialization, and 24,000
publications while the UI performs no reads. Three threads exercise 12,000
accepted loads, audio batches, same-producer saves and a separate atomic-only
observer; all successful reads must match independently generated complete
control values. Busy reads must preserve caller sentinels.

The actual Engine integration holds manual keys and pedals with moving contacts
and decayed percussion readiness. Restores preserve every manual contact,
all pedal contact bits, held targets, all 91 source phases, readiness, clock and
last-rendered pedal diagnostics. An invalid candidate callback does not
acknowledge its batch. A successful restore's subsequent audio matches an
independent Engine copy exactly.

See the [assignment 29 record](development/2026-11-13-pedals/29-state-exchange.md)
for frozen inputs, commands, observed results and sanitizer qualification.
This is a core state-exchange gate. Native wrapper integration, SDK validation,
host lifecycle tests, cross-platform builds and callback allocation/timing
measurement retain their separately assigned gates.
