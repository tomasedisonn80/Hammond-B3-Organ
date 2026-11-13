# Proposed host, device and editor integration

**Status: design handoff; no adapter is implemented or qualified.** The product
will share `hammond::Engine` across offline, plugin and device clients. The current
CLI writes WAV files; it is not an audio-device application. This proposal adds
no SDK, framework, dependency choice or exported plugin contract.

The next product implementation remains **M3 contact trajectories, then shared
percussion/recharge**, preserving M2 source identities. Adapter preparation may
proceed independently; it does not close M9 or M0 specimen/revision/permission
gates. Sources are the [plan](PLAN.md), [atlas index](research/chapter-index.json)
and [atlas](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf) chapters 062–065
(pp. 379–402), 071–073 (pp. 433–450), and 079 (pp. 481–486). External SDK APIs
must be checked against primary documentation when a concrete wrapper is chosen.

## 1. Reuse the implemented boundary

The inspected [headers](../include/hammond/Engine.h),
[types](../include/hammond/Types.h) and [implementation](../src/Engine.cpp) establish:

| Current core contract | Adapter obligation |
| --- | --- |
| Rates exactly 44,100, 48,000 or 96,000 samples/s | Reject other rates at setup; no implicit resampler. |
| Prepared maximum `P`: 1–65,536 frames | Allocate scratch before activation; each core call uses at most `P`. |
| At most 1,024 events per call | Bound translation and merging before dispatch. |
| Mono `float` output; empty span means disconnected | Validate buffer extent/layout; deliberate channel conversion belongs outside the core. |
| Whole-call preflight; rejection consumes zero events and changes no output/state | Check status and exact consumed count; supply an adapter failure policy. |

Preparation requires stopped processing. `prepare(profile, spec)` validates before
replacement, copies the value-owned profile and starts a new seeded source field.
Success clears keys and banks, selects B, enables both routes, sets expression to
1 and adopts `initial_frame`; failure preserves the previous engine. That frame is
an origin, not elapsed simulated history. Parse files, allocate, prepare, replace
and destroy outside active callbacks. Rate changes require this stopped lifecycle;
current controls cannot migrate source phases. Reapply validated controls after
successful reprepare and begin a new owner epoch; reconcile held input explicitly.
See [ENGINE_API](ENGINE_API.md).

One serialized audio execution context owns all mutable engine state; successive
calls may run on different threads, but cannot overlap. Diagnostics, including
`controls_snapshot()` and `frame_clock()`, have the same ownership restriction.
The initial proposed output is mono or identical dry left/right float channels,
with no audio input. Stage mono in prepared scratch; qualify layout, null/inactive
channels and alias handling before advertising another format or bus.

## 2. Translate clocks and block boundaries once

At callback entry let `C = frame_clock()` and `N` be the admitted frame count.
Host transport position is separate metadata: seek, loop, play/stop and editor
closure never implicitly call `prepare` or reset phases. With no callbacks, render
time freezes. Positive disconnected or muted processing still advances all 91
sources. A mute policy must keep processing and explicitly zero output.

Validate signed offsets before unsigned conversion. A positive block owns
`[C, C + N)`; check addition before dispatch. For a slice starting `s` frames into
the callback, events with `s <= h < s + n` become relative offset `h - s`.
An admitted event at `h == N` belongs to the adapter's next-boundary carry, never
the current core call. Reject negative offsets and offsets beyond `N`. Preserve
carried records' identity and consume each exactly once.

Proposed merge order is `(core frame, producer rank, producer sequence)`: host
parameters, host notes, numbered device-input slots, then UI commands. Preserve
order within each producer and use fixed ranks across slices. This is a project
policy for otherwise unordered streams, not a claim about native SDK ordering.
A zero-frame call dispatches only current-frame events at offset zero; it consumes
them without advancing source phase or time. Do not replay its commands in the
next positive call. Snapshot restoration, when supported, commits before that
boundary's ordinary events.

For a device backend, retain a clock epoch and a qualified monotonic-time anchor
`(t0, C0)`. Proposed conversion is `Cevent = C0 + ceil((t - t0) * Fs)`, with checked
signed arithmetic and range/finite checks before integer conversion. Qualify the
driver-clock relationship and rounding independently. Late records apply at the
next boundary with a late counter; they lose sample-accurate status. Device loss
invalidates the epoch. Neither transport jumps nor wall-clock gaps imply catch-up.

## 3. Admission and explicit recovery

Proposed first-adapter limits are an activation-time host maximum `H <= 65,536`,
`1 <= P <= H`, and **1,024 examined input and 1,024 translated records per callback**,
including carried and queued input. Each producer queue, pending-event store and
input-owner table also has a fixed capacity, initially 1,024 records. Permit at
most 16 device-input producers and one UI producer, besides the two host streams.
Never drain until empty. Preflight the
entire callback, including all slices, before the first musical mutation. The
offline renderer's dense-block subdivision is not a live queue/deadline guarantee.

Malformed accepted-domain values, ordering corruption or exhausted musical
capacity fault the event epoch; do not clip values, discard note-offs or silently
keep only the newest timed automation. Ignore deliberately unsupported message
types/unmapped channels only under the published input map, with filtered counts.

Fault recovery is a **separate, visible transaction**, not successful playback:
discard the bounded epoch, clear adapter owners, and issue an internal zero-frame
`AllNotesOff` for each manual. Preserve controls and phase. If `N`, buffers and
`C + N` remain valid, write silence and advance the core disconnected in bounded
slices without user events. Otherwise suspend at the last valid core frame and
request lifecycle recovery. Touch only validated writable buffer extents; invalid
buffer metadata cannot justify a write. Latch the reason and discontinuity count
for reporting outside audio. Never repeatedly retry a rejected request.

At `UINT64_MAX`, positive processing must stop; the core still permits an
offset-zero flush. Never wrap or silently rebase the clock. A new prepared epoch
is an explicit stopped reset. Test failure atomicity separately from subsequent
adapter recovery; the engine's unchanged-output guarantee is not output silencing.

## 4. Publication requires new implementation and tests

The current core contains no concurrent command queue, UI snapshot publication or
live profile exchange. The [callback audit](REALTIME.md) establishes only its
declared allocation-observation scope; it proves neither adapter deadlines nor
concurrent safety.

Use fixed-size copied command records and separate queues per independent
producer, or merge producers outside audio. An SPSC design cannot accept multiple
writers by convention. Qualify target atomics, ordering and bounded operations;
no locks, allocation, final ownership destruction, logging, I/O or retry loops
belong in the callback. Only untimed idempotent targets may coalesce; notes,
scheduled automation, Cancel and same-value bank reselect commands may not.

Audio publishes copied snapshots containing controls, frame/epoch, applied-command
sequence and fault/loss counters. UI and accessibility read their own acquired
snapshot, never the engine. A reader owns its slot until release; the producer
cannot overwrite it. Full display/telemetry queues may skip publication and count
loss without blocking audio. Pending commands remain distinguishable from
acknowledged state; later snapshots carry the acknowledged sequence.

Keep profile replacement stopped. Any future live exchange needs prepared slots
and generations, reserved retirement capacity, an explicit state-migration rule,
delayed-reader tests and non-audio reclamation after the last reader. Full
retirement storage must defer activation. None of those guarantees follows from
copying `RuntimeProfile` or declaring `noexcept`.

## 5. Musical mapping, stable controls and recall

**Proposed default MIDI map:** channel 1 upper, channel 2 lower (human numbering),
notes 36–96;
persist explicit input-port/channel overrides. This is software configuration,
not factory wiring. Pedal routing data does not implement pedal audio; advertise
no pedal channel. Velocity zero releases; nonzero velocity never scales sustained
level in the current ideal engine.

The adapter owns input identities. Use `(port, channel, note-id)` where available,
otherwise `(port, channel, key)` with repeated presses idempotent. Combine owners
per manual/key and send core press/release only on empty/nonempty transitions.
An owner's release cannot release another device's held key. Device loss or editor
closure releases only that source's owners; focus movement does not. Epoch fault
recovery deliberately releases all owners. Cancel changes routing, not ownership.

Use [registry version 1](PARAMETERS.md), model `ideal-exclusive-ab-console-v1`:

| Permanent internal IDs | Target |
| --- | --- |
| `0x1000`–`0x1008`; `0x1010`–`0x1018` | Upper A; Upper B, nine drawbars each |
| `0x1020`–`0x1028`; `0x1030`–`0x1038` | Lower A; Lower B, nine drawbars each |
| `0x2000` | Global expression |
| `0x2010`; `0x2011` | Upper; lower bank selector |

These **39 proposed internal IDs** are not verified host exports. Never bind an
automation lane to the visible slider index or recycle an accepted ID. Drawbar
events use `BankDrawbar`, index `bank * 9 + drawbar`; selection cannot retarget them.
For discrete `K = 8` or `1`, `u = k/K` and exact round-half-up
`k = floor(u*K + 0.5)` apply to finite `u` in `[0,1]`. Preserve adjacent-double
threshold behavior from the [Python oracle](../tools/validate_parameters.py);
naive intermediate rounding can differ. Position 4 is not amplitude 0.5.
Expression uses `x = u`, the existing linear-gain surrogate. Reject invalid
domains. Do not substitute the different atlas p. 398 law or claim native curve
reconstruction: current events are steps. A native conversion/curve contract and
retained migration fixtures precede any released export.

[B3CONTROLS1](CONTROL_STATE_FORMAT.md) retains all controls plus two route-enable
bits, with a 16,384-byte input limit. Parse/serialize off audio. Replaying 39 scalar
parameters cannot restore Cancel: selector replay reconnects a route. Restore a
complete validated snapshot on the audio owner or while stopped. Running restore
preserves currently held keys, phases and clock; fresh preparation has no keys.
Neither saved controls nor a seed is a DSP checkpoint. A future wrapper envelope
must version profile identity/digest, registry, input mapping and compatibility;
editor camera/layout and machine device setup stay separate. Missing resources or
unknown required versions fail visibly, preserving the previous state.

## 6. Focused acceptance and dependency-ready tasks

All adapter cases below are **not_run**. Existing core tests provide reusable
oracles, not a host pass; [Agent 46's note](development/agent-notes/46-host-integration.md)
records inspections and document checks.

| Case | Required observable result |
| --- | --- |
| Lifecycle/value ownership | Failed prepare preserves continuation; caller profile edits cannot affect prepared audio; teardown waits for quiescence. |
| Timing/partitions | At all three rates, identical admitted fixtures across 1/17/64/irregular/maximum slices match direct-core samples, keys, controls, all phases and clock; offset-end carry and ties execute once. |
| Flush/transport | Repeated empty flushes advance nothing; consumed commands do not repeat; seek/loop/editor absence do not reset phase; disconnected positive frames advance it. |
| Bounds/faults | Exercise 1,024/1,025 records, short/null/aliased buffers, `H+1`, malformed final input and clock maximum; verify preflight and the separate recovery transaction, with no stuck owners. |
| Owners/console | Two devices hold one pitch; release one, close UI, lose device, Cancel, edit hidden bank and reselect unchanged bank; verify only intended keys/routes change. |
| Parameters/state | Enumerate all 39 exports, canonical and adjacent-threshold conversions, every retained bank/route combination, unsupported versions and missing profiles; restore never invents saved keys. |
| Publication | Delayed consumers, full queues, repeated generations, save-during-play and shutdown preserve slot ownership; correctness/race instrumentation and callback allocation checks remain separate. |
| Native UI/device | Keyboard and screen-reader tasks, resize/scaling, lost capture, reduced motion, headless playback, device reconnect and clock conversion retain declared behavior and diagnostic evidence. |

Implement a dependency-free translation/admission harness first, using
[engine tests](../tests/test_engine.cpp), [console tests](../tests/test_controls.cpp)
and [parameter tests](../tests/test_parameters.py) as references. Next implement
and stress the publication/owner protocol. Then select a reviewed adapter/backend
with the dependency/rights inventory, verify primary native contracts, and test
headless wrapper equivalence before device recovery and editor binding. This queue
does not displace M3 contacts/percussion.

Native accessibility remains requested and unimplemented: both dimensional and
flat skins need stable semantic names, ranges, keyboard operation and balanced
gestures bound to their original ID. Close each gesture once before rebinding;
host-origin updates redraw without echoing new edit commands. Browser labels or screenshots do not qualify
native assistive workflows. Closing a view cannot stop external MIDI or audio.

Actual device timing also remains unqualified. Predeclare target hardware and
budget; retain callback durations, maximum and percentiles, underruns, clock error,
late-event and telemetry-loss counts under cold start, dense input and UI load.
`N/Fs` is a nominal interval, not round-trip latency. Reports identify binary,
profile, OS, architecture, host/device/driver, rate, buffer and layout, and separate
pass, failed, blocked and not_run. Offline tests, platform builds and source
inspection cannot close those product gates or establish instrument fidelity.
