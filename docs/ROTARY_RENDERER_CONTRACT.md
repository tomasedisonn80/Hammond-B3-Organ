# R4 streaming renderer contract

**API frozen: A07 proposal accepted by the integrator after independent A10 and A11 reviews, 14 November 2026.**
`rotary-renderer-v1` implements the unchanged
[rotary-numerics-v1](ROTARY_NUMERICAL_CONTRACT.md), especially sections 2–6.
The public declarations are [RotaryHistory.h](../include/hammond/RotaryHistory.h)
and [RotaryRenderer.h](../include/hammond/RotaryRenderer.h). This is an
implementable ownership/API contract, not an executed R4 result.

The [A04 reading](development/2026-11-14-waveform-continuation/notes/A04-atlas-rotary.md)
records the unchanged atlas basis, especially pp. 289–294 and 301–324. Inputs
are separate normalized double horn/drum radiation-boundary waveforms. Only
retarded direct-point propagation, the specified cubic interpolation and
reference-distance/path-distance pressure gain are included. Preserve the dry
Engine, all 47 parameters, `B3CONTROLS4` and readers 1–3. There is no Engine,
electrical, driver, directivity, cabinet, room or microphone-filter integration.
R5 reconstruction/alias policy, R6 integration/deadlines and physical M7 remain
separate gates. Existing R2 and immutable-fixture R3 interfaces stay unchanged.

## 1. Public owners and implementation split

| Public component | Responsibility | Exclusive implementation file |
| --- | --- | --- |
| `interpolate_cubic_lagrange` | Four admitted support values and one explicit cubic evaluation | `src/RotaryHistory.cpp` |
| `WaveformHistory` | Owned double ring, signed-index reads and complete cubic support admission | `src/RotaryHistory.cpp` |
| `MotionFrameHistory` | Owned bounded ring of original event segments, constant-speed negative history and fractional queries | `src/RotaryHistory.cpp` |
| `PreparedStreamingPath` | Admitted immutable geometry and the bounded R3-equivalent solve over streaming history | `src/RotaryStreamingPath.cpp` |
| `RotaryRenderer` | Preparation/lifecycle, events, four paths, two outputs and whole-call transactions | `src/RotaryRenderer.cpp` and `src/RotaryRendererInternal.h` |

These three production assignments can run independently against the frozen
headers. The renderer owner creates the private storage header described below;
history and path owners do not edit it. Independent tests/oracles belong in
separate files assigned by the integrator. The integrator owns CMake, shared
status/next steps/log, API acceptance and publication. A worker must coordinate
an actual contract defect before changing a frozen declaration.

All calls are serialized, including read-only getters and lifecycle methods.
No concurrency, live profile publication or thread-safe snapshot claim is made.
The renderer is noncopyable and nonmovable; getters return values, never borrowed
internal pointers. Its constructor is small and allocation-free. Destruction,
preparation and rate replacement happen with processing stopped.

### Histories

Both history classes own fixed `std::array` backing storage of
`kMaxHistoryFrames`; preparation selects active capacity `H` in `[1,16384]`.
Neither class allocates. They are intentionally large value types. The renderer
and tests must put full histories, collections of histories and whole-history
snapshots on the heap, not on a platform's approximately 1 MiB stack. A copied
history owns independent bytes; equality is available for bounded off-process
tests. The renderer never copies an entire history in `process()`.

`WaveformHistory::prepare(rate,H)` requires a supported exact rate and capacity,
clears all sample slots and starts `next_frame=0`. `push(x)` admits finite
`x` in `[-1,1]`, writes slot `next_frame % H`, then increments `next_frame`.
The newest written sample is `next_frame-1`; retained nonnegative indices are
`[max(0,next_frame-H), next_frame)`. Every negative index inside the epoch is
declared zero. Other nonnegative indices return `InsufficientHistory`; values
outside the signed one-day epoch return `TimelineOverflow`. No unavailable
positive input becomes implicit zero. Reset clears the samples and clock at
the current rate/capacity.

`MotionFrameHistory::prepare(owner,H)` requires a prepared `RotaryMotion` at
frame zero. It copies that owner's motion profile, rate and epoch seed, clears
all segment slots and starts empty at zero. It retains no reference to the
owner. `append(owner)` requires matching rate/profile/epoch seed and
`owner.frame()==next_frame`. It checks continuity against the previously
retained segment's evaluation at that boundary (the epoch seed at zero), and
checks the new segment's endpoint at `next_frame+1`, before mutation. State
comparison is exact native `MotionState` equality, including turns. An append
at `n` stores `owner.segment()` unchanged in slot `n % H`, then increments
`next_frame`. It never creates a segment anchored at `n` merely to store it.

The stored segment owns `[n,n+1)`. Positive queries choose the record for the
query's integer floor and call `evaluate_motion_segment_at` with the original
anchor. Retiring the slot that contained a command frame does not discard that
anchor: every subsequent retained interval still contains its complete original
segment until a real command changes it. This is constant storage across any
number of accepted calls/events in the admitted epoch, including repeated
zero-frame calls; the immutable R3 4,097-event fixture cap is irrelevant here.

Motion coverage is `[oldest_frame(), next_frame()]`, with the final endpoint
admitting only fraction zero. That endpoint evaluates the last retained segment;
an empty history admits exactly `{0,0}` as its epoch seed. A command at this
endpoint changes future motion but preserves the endpoint state. The next
append records its final effective segment. Negative positions always use
`evaluate_motion_prehistory_at` with the epoch seed and fixed direction, even
after positive slots retire. Validate fraction and one-day epoch bounds before
coverage; old/future uncovered positive positions return `InsufficientHistory`.

Every primitive rejection preserves its object and destination values. Capacity
does not silently grow; modulo indexing is performed only after preparation.

### Cubic kernel

`interpolate_cubic_lagrange` receives `{x[k-1],x[k],x[k+1],x[k+2]}` and admits a
finite fraction in the **closed interval `[0,1]`**. Zero returns `x[k]`; one
returns `x[k+1]`. Explicit endpoint selection is allowed and preserves exact
endpoint values. The interior is the four-node Lagrange expression in the
numerical contract, accumulated in support order `-1,0,1,2`. Each input must
be finite and in `[-1,1]`. Stage the answer before writing it, so destination
aliasing one supplied sample is safe. Do not clamp the interpolated value.

`WaveformHistory::interpolate(SamplePosition,...)` admits only canonical
fractions `[0,1)`. The equivalent representation of fraction one is
`{frame+1,0}`. Check signed arithmetic and read **all four** nodes, even nodes
whose coefficient is zero at an endpoint; each must be retained or declared
negative-time zero. The standalone kernel's closed endpoint is retained for
the required `j/256`, `j=0..256`, characterization rather than omitted from it.

## 2. Streaming geometry and solve

`PreparedStreamingPath::prepare(rotor,microphone,c,reference_distance)` owns
only copied admitted geometry and the motion profile. Validate the complete
rotor projection, including initial phase/speed/command, and all frozen geometry
limits. Calculate full-orbit bounds exactly as R3 does, using the speed envelope
`max(original_initial_speed,slow,fast)`. Invalid profile initial commands are
`InvalidProfile` here and in renderer preparation; event commands remain
`InvalidEvent` during processing. Preserve the prior prepared path on failure.

The path is rate-independent. `solve(history,observation,...)` borrows a history
only for that call. Require a prepared matching motion profile and an epoch seed
speed no greater than its admitted speed envelope. This allows reset and stopped
rate epochs without replacing the original geometry or enlarging its Mach bound.
An incompatible history is `InvalidProfile`. Observe history's full query range,
including its retired positive lower bound; every evaluated emission must also
be covered. Both returned destinations are staged and unchanged on rejection.

Use the qualified R3 algorithm and arithmetic conventions from
[ROTARY_PROPAGATION_CONTRACT.md](ROTARY_PROPAGATION_CONTRACT.md): split-frame
delay subtraction; full analytical distance bracket with the same 32-ulp distance
padding; derivative allowance `2e-15`; at most 48 total geometry evaluations,
including endpoints; `1e-14 s` early target and `1e-11 s` success residual; cached
selected evaluation, no uncounted final solve. Output positive delay, emission
strictly before observation, the same radial-speed sign, gain and frequency
ratio. The path applies no algorithmic latency. Keep existing `RotaryMotion.cpp`
and `RotaryPropagation.cpp` unchanged. A small separate streaming implementation
may reuse their public motion/geometry primitives and mirror the qualified solve;
do not adapt a mutable ring into R3's immutable borrowed view.

## 3. Renderer preparation and copied values

`prepare(profile,spec)` first admits the exact supported rate, positive
`max_block_frames<=4096`, both complete rotor projections and all four full-orbit
paths. Initial turns are zero. Let `rmax` be the maximum of all four admitted
path maxima, and calculate:

```text
D = ceil(Fs * rmax / c)
H = D + 2 + 4
flush_frames = D + 2 + 2
```

Use the same `H` for both waveform and both motion rings. Require `H<=16384`;
maximum admitted propagation gives `D=12800`. The guards cover the padded solve
bracket, two-frame observation lag and all cubic supports. Reserve maximum
fixed backing storage even when `H` is smaller. The declared active capacity
and flush length are copied getters, zero when unprepared. Fixed algorithmic
latency is always two frames and is never combined with physical travel time.

Validate with small temporary motion/path objects before allocating one new
`detail::RotaryRendererStorage`. Initialize that candidate fully, then replace
the prior pointer and destroy old storage only after success, outside processing.
Allocation failure returns `AllocationFailure` and preserves the old instance.
No history-sized local temporaries are permitted.

`profile()` and `spec()` return copies; the unprepared projection is `Profile{}`
and spec `{0,0}`. `state()` returns the declared `RendererState`: current frame,
rate/limit, both current physical states, commands, epoch seeds and exact active
segments. Its frame is the next input sample and the observed boundary of both
motion owners. It excludes call counts, scratch and saved-state serialization.
Snapshots and future samples must agree for prescribed block partitions. Test
bit identity field by field; struct padding is not an observable physical value.

Diagnostics are copied `RendererDiagnostics`, with path order Horn/Left,
Horn/Right, Drum/Left, Drum/Right. They retain the last accepted sample's path
results/emissions/observation and the epoch's largest absolute accepted residual
and largest iteration count. There are no call-dependent persistent counters.
When `has_rendered_sample` is false, last-path fields are their type defaults
and carry no path observation claim. Zero-frame successes leave diagnostics
unchanged. Rejected-call observations appear only in `ProcessResult`.

## 4. Exact processing and admission

`process(horn,drum,left,right,events)` takes its frame count `N` from
`horn.size()`; all four spans must have exactly `N` elements. Span lifetimes,
valid C++ object storage and exclusion of concurrent modification are caller
preconditions. Inputs may partially or completely overlap each other. Left
and right byte ranges must be disjoint from one another and both audio inputs;
adjacent ranges are allowed. Empty spans have no overlap. Event storage remains
readable throughout the call and is not retained. No additional alias policy
is imposed on it; every event is read before successful output publication.

Preflight occurs before persistent mutation, in this order:

1. Prepared state (`NotPrepared`).
2. `N<=spec.max_block_frames` (`BlockTooLarge`), and at most 1,024 events
   (`TooManyEvents`).
3. Equal audio lengths, non-null data for nonempty audio/event spans and legal
   audio range overlap (`InvalidBuffer`). Check address-range integer arithmetic
   for overflow before comparing ranges; do not subtract unrelated pointers.
4. `N<=max_frame-current_frame` (`TimelineOverflow`).
5. Valid rotor and command enumerators, offsets in `[0,N]`, nondecreasing
   offsets (`InvalidEvent`). No event sorting, merging or skipping is allowed.
6. Every input sample finite and in `[-1,1]` (`InvalidBuffer`).

For each absolute input frame `n`, advance the staged owners to `n`, apply all
events at that boundary in supplied order, retain their final original segments
and write both inputs. Observe `SamplePosition{int64(n)-2,0}`; solve paths in
declared array order and read the appropriate input's cubic at each emission.
Multiply by that path's pressure gain. Left is Horn/Left plus Drum/Left; right
is Horn/Right plus Drum/Right, in that order. Stage both finite sums. There is
no extra oscillator, panner, limiter, normalization or output clamp.

After the samples, advance owners to the end boundary and apply offset-`N`
events in order. They are effective before the following call's offset-zero
events. A zero-frame call accepts only offset-zero events, advances no clock
or ring, and still applies them in order. An unchanged command never reanchors;
different same-frame commands can replace their common future segment, without
discarding any event from `events_consumed`. Silence runs this same operator.
Suspension means no calls and freezes state.

On success consume every supplied event. `ProcessResult` maxima describe only
the current call's completed path solves; zero-frame calls have zero maxima.
On any failure consume zero events. The result may retain maxima from completed
solves before a late failure; a failed solve's staged destinations do not supply
an invented residual or iteration count. No rejected-call maximum enters
persistent diagnostics. Preserve specific primitive failure statuses.

## 5. Private storage and whole-call transaction

The renderer owner's private `RotaryRendererInternal.h` defines
`detail::RotaryRendererStorage` with exactly these responsibility groups:

- Copied original profile, current spec, common `H`, flush length, two
  `RotaryMotion` owners, four `PreparedStreamingPath` objects and committed
  diagnostics. Both owners and all four rings agree on next frame at public
  call boundaries.
- Two `WaveformHistory` and two `MotionFrameHistory` values, owned once.
- Two output scratch arrays of `kMaxBlockFrames` doubles.
- An undo array of `kMaxBlockFrames` records. Each record contains one physical
  ring slot index, its two prior doubles and its two prior `MotionSegment`s.

The storage has bounded heap size determined by those fixed constants. Do not
place the storage, journal or full history backups on the process stack.
Small local motion-owner, diagnostics and counter copies are permitted.

Stage both motion owners and diagnostics by value. Before the first ring write
for frame `n`, record **all four** old slot values at `n%H`, and count that undo
record as live before attempting any write. Then append the two samples and
two original segments. A helper can fail after only some writes: the record
must already be able to restore all of them. Save the four pre-call
`next_frame` metadata values separately; append changes no other ring metadata.

On any subsequent failure, replay all live undo records in reverse, restoring
the exact prior doubles and segments, then restore all four `next_frame`
values. Discard staged owners and diagnostics, and never write caller outputs.
Repeated wraps in one block are safe: the journal records **each overwrite**,
not just distinct slots. Thus `N>H` requires no special history copying and
rollback returns even retired physical slot bytes to their pre-call values.
Zero-frame events need no journal entries.

After the last possible failing operation succeeds, publish staged owners and
diagnostics and copy both output scratch prefixes to the admitted output spans.
There must be no fallible operation after publication starts. Serialized access
makes this a whole-call visibility guarantee, not a concurrent atomic snapshot.
An accepted call performs work bounded by `N`, events and 48 evaluations per
path; a rejected late call adds at most `N` reverse undo records. There is no
process allocation/deallocation, container growth, history-sized copy, lock,
I/O, logging, user callback or hidden preparation.

**The rollback guarantee covers every retained waveform/motion slot, all ring
metadata, physical owners, prepared configuration, persistent diagnostics and
caller output bytes.** Output scratch and inactive journal-record bytes are
unobservable work storage and may change on rejection. They are never exposed
by getters, compared as public state or consulted by a later call except after
being overwritten for that new call. This explicit scratch exception does not
weaken history preservation or future-output equivalence.

The declared `detail::RotaryRendererTestAccess` friend has no production
implementation and introduces no public failure switch. A dedicated test may
include the private storage header, corrupt one retained slot that a later
sample will query, observe earlier samples completing internally before that
failure, then restore that slot. A separate fixture may shorten only the second
motion ring's private append limit, leaving the renderer and both motion owners'
limits intact, so an otherwise admitted call fails after more than two complete
ring wraps. Choose the limit so earlier ring writes at the failing frame have
occurred and its undo record is already live. This exercises partial-frame and
repeated-overwrite rollback through the actual `process()` failure path; no
production callback, switch or new public API is introduced. Verify caller
output sentinels, copied state, diagnostics, ring metadata and every retained
slot value against pre-call values, including bit representations of floating
fields. The deliberately corrupt slot or shortened limit is part of the
rejected call's pre-state and must itself survive rejection. Restore only that
injected value afterward, then compare accepted continuation with an unmodified
control. Retain both fixtures: a retained slot is overwritten within one ring
cycle and alone cannot demonstrate a failure after multiple complete wraps.
These are late failures, not merely invalid-input preflight.

## 6. Lifecycle and error vocabulary

`reset()` requires a prepared renderer. Stage both existing owners, call their
reset at the current rate and admit all resulting metadata before any clearing.
Then clear both waveform rings, prepare empty motion histories from those
original seed owners, publish owners and default diagnostics. Preserve current
spec/capacity/geometry and original profile. Reset allocates no storage and
restores original commands/phase/speed with zero original turns.

`reconfigure_sample_rate(rate)` requires a prepared renderer and an exact
supported rate. Even the same rate starts a new epoch. Prepare replacement
storage outside processing with the current physical state/turns/commands,
while retaining each owner's originally prepared reset seed. Start all clocks
at zero, use constant-current-speed negative motion and silent waveform history,
recalculate `H`/flush length, clear diagnostics and discard old acoustic tails.
The original admitted speed envelope remains valid for both this epoch and a
later reset. Invalid/allocation-failed replacements preserve the old object.

There is no special implicit tail renderer. `tail_flush_frames()` gives the
required total explicit zero-input frames, divided into legal blocks, while
motion continues. A flush consumes ordinary epoch time and obeys the same
timeline limit. At the full-day boundary only zero-frame commands can remain
admitted; reset/rate replacement is required before more audio frames.

| Condition outside process preflight | Status |
| --- | --- |
| Unprepared required owner/history/path | `NotPrepared` |
| Unsupported rate, invalid capacity/spec or noncanonical fraction | `InvalidSpec` |
| Invalid geometry/kinematics/profile seed, incompatible history or discontinuity | `InvalidProfile` |
| Nonzero owner at history preparation, wrong owner append frame | `InvalidEvent` |
| Invalid standalone cubic support sample | `InvalidBuffer` |
| Epoch/support-index/turn overflow | `TimelineOverflow` |
| Retired or unavailable nonnegative history/support | `InsufficientHistory` |
| Failed finite/bracket/residual/derivative computation | `NumericalFailure` |
| Stopped renderer-storage allocation failure | `AllocationFailure` |

`MotionFrameHistory::append` uses `InvalidSpec` for a mismatched owner rate;
matching-profile/seed/continuity failures use `InvalidProfile`. Specific existing
motion helper failures remain intact. Every failure preserves the prior object
and caller destinations. Never reinterpret a rejection as a silent sample.

## 7. Acceptance responsibilities

The numerical contract's complete experiments and budgets are unchanged:
closed integer/fraction endpoints, all `j/256` fractions and degree 0–3
polynomials; signed indices, all four supports, oldest/future history and wrap;
the full static `j/64` by `k/1024` grid with high-band failures retained; and
at least ten seconds of independent same-cubic parity at every supported rate,
normalized maximum error `<=2e-5` without fitted alignment or rescaling.

Independent streaming/history tests must additionally demonstrate original
anchor retention after the anchor slot retires, more than 4,097 lifetime
events, same-frame order, unchanged commands and multiple ring wraps per call.
Independent renderer tests retain blocks 1/7/64/257/4096 and recorded irregular
partitions with bit-identical audio/final physical state, offset-`N`/next-zero
ordering, nonzero-history rollback (including the late seam), separate inputs,
signed cancellation, coincident/swapped receivers, rigid scene transforms,
explicit tails/reset and every stopped rate pair including equal-rate epochs.

Allocation/deallocation probes cover actual accepted, early-rejected and
late-rejected processing, with a calibrated detector; stopped allocation failure
must preserve a previously working renderer. Numerical parity and zero observed
callback allocation do not pass R5, device deadlines, host integration or
physical fidelity. Retain exact source/build/oracle/profile hashes, commands,
worst/RMS errors and all failures. The 155/155 session baseline predates this
new API and is not renderer implementation evidence.
