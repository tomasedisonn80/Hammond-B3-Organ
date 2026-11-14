# R4 renderer implementation readiness: independent boundary review

**A57, 14 November 2026 — design review, with implementation acceptance still
open.** The proposed original-anchor frame cells, `D+6` capacity and `D+4`
flush are consistent with the inspected solver and frozen numerical contract.
The streaming interface still needs explicit trajectory binding, borrow scope,
storage restoration and flush ownership before it can be accepted. These are
implementation preconditions, not permission to change the frozen budgets.

This review leaves [A42's original plan](../ROTARY_RENDERER_IMPLEMENTATION_PLAN.md)
and the [waveform owner's brief](../ROTARY_RENDERER_PLAN.md) unchanged. That
separate session owns R4 code and its eventual evidence. Inspection used HEAD
`0881d1f4c5a26ce9c75dda7a3adde46382e5ab6b`, tree
`f8144b771cda1264a8788f8297f5bfec999f4a08`, with unrelated documentation and
session work present. The [receipt](../development/2026-11-14-reference-refinement/reports/A57-r4-plan-independent-review.json)
records exact inspected source hashes and scope; the
[arithmetic record](../development/2026-11-14-reference-refinement/reports/A57-r4-boundary-proof.json)
contains a reproducible, scratch-only calculation. Neither is a native execution,
rendered waveform, allocation observation or R4 pass.

## Established APIs and the required streaming seam

The full [numerical contract](../ROTARY_NUMERICAL_CONTRACT.md),
[propagation contract](../ROTARY_PROPAGATION_CONTRACT.md) and native
[motion](../../src/RotaryMotion.cpp)/[propagation](../../src/RotaryPropagation.cpp)
implementations establish the following facts.

| Existing fact | Consequence for the proposal |
| --- | --- |
| `RotaryMotion::apply_command` evaluates the retained segment at the event frame and replaces the anchor only when the command changes. `advance_to` does not reanchor. | Copy `segment()` after all events at each written frame. Evaluating the retained original segment gives the same arithmetic regardless of process partition. A per-frame state used as a fresh seed would change that arithmetic. |
| `MotionHistoryView::prepare` requires anchor zero, strictly increasing later anchors, canonical native continuity and at most 4,097 segments. It borrows a contiguous immutable span. | A wrapped frame ring, duplicated anchors or a dropped frame-zero prefix cannot be passed to this API. The cap is a finite-fixture limit, not a streaming event allowance. |
| `PreparedRetardedPath` copies the view, including its borrow; preparation uses its actual epoch seed, speed targets and direction. | Keeping this path alive while overwriting the backing segments violates its existing lifetime contract. A newly reviewed streaming path must retain no ring view between calls. |
| The solver uses split observation positions, evaluates both widened endpoints and counts every evaluation within 48. It publishes its cached selected result. | Sharing a solver kernel must preserve subtraction, evaluation accounting, residual checks and output staging. A new final geometry evaluation cannot be added outside the bound. |

**Required precondition 1 — bind geometry and trajectory.** “Geometry-only”
should mean no retained storage borrow; it must not discard trajectory admission.
The current full-orbit Mach bound uses
`radius*max(epoch_seed_speed,slow,fast)/sound_speed`. A new path accepting an
arbitrary window cannot assume that a different rotor, direction, epoch seed or
rate remains the prepared one. Either make construction/use internal to the
renderer so this relationship is guaranteed, or validate the relevant immutable
metadata at the streaming boundary. Rebuild or re-admit the relationship during
stopped rate replacement. The exact internal interface and mismatch status are
still proposed, not declarations supplied by the current headers.

**Required precondition 2 — end every borrow before mutation.** After both
rotor cells for frame `n` are written, construct read-only windows, solve all
four paths and consume value results inside one bounded scope. End that scope
before another cell write, journal replay, reset, replacement or destruction.
Stable allocation alone does not make mutation safe. Do not expose a retained
window through diagnostic access or a prepared path; copied physical values are
sufficient. Window construction must establish admission without rescanning a
whole ring per query or calling user code.

For nonnegative `{k,mu}`, integer events imply that cell tag `k` selects the
segment for `[k,k+1)`. Verify the tag and original anchor before native segment
evaluation; a valid-looking modulo slot is insufficient. Reject unavailable
positive history even if the current owner could predict it. Negative motion
uses the epoch seed at constant speed, while negative audio independently reads
as zero. Coverage at the newest written cell is inclusive only at `{n,0}`.
An end-boundary event at `n+1` changes the owner but creates no speculative cell.

## Independent capacity and support derivation

Let `R` be the larger admitted maximum distance for one rotor's two receivers,
`D=ceil(Fs*R/c)`, and `C=D+6`. The actual solver widens distance by
`m=32*ulp(max(1,R))`; over the admitted domain, `m<=2^-43 m`.
The mathematical widening contributes at most
`2^-43*192000/300 = 7.275957614183426e-11` frames.

A42's quoted number is the widening contribution, not a complete floating-point
endpoint-error bound. **Required arithmetic detail:** establish `d_frames<D+1`
for the implementation's actual capacity and endpoint operation orders. Under
qualified binary64 rounding to nearest, the present `(R+m)/c` then `*Fs` order,
and `ceil((Fs*R)/c)`, addition/division/multiplication rounding, including a
downward capacity-expression rounding, adds less than `3*ulp(12800)` frames.
The combined conservative bound is below `7.83e-11` frames, hence far below
one frame and the existing 13,000-frame subtraction guard. This is an explicit
proof precondition, not a changed numerical tolerance or an added history cell.
Other arithmetic or floating environments need their own justification.

After writing frame `n`, a full ring retains tags `n-C+1=n-D-5` through `n`.
Observation is the integer split position `{n-2,0}`. For any evaluated positive
delay `0<d_frames<D+1`, emission `s=n-2-d_frames` satisfies

```text
n-D-3 < s < n-2
n-D-3 <= floor(s) <= n-3
n-D-4 <= oldest cubic tap; newest cubic tap <= n-1
```

Thus the oldest four-tap support is one cell newer than the ring's oldest tag;
the endpoint motion lookup is two cells newer. Startup replaces negative tags
with the declared prehistory/zero policy. No positive future sample is needed,
including at an integer emission where all four support positions must still
be available. The proof uses integer/fractional subtraction, not a large
floating absolute sample index. At the epoch endpoint the last audio index is
`86400*Fs-1`; the final owner/event boundary may equal `86400*Fs`.

| Rate, Hz | Maximum `D` | Per-rotor `C=D+6` | Zero-input flush `D+4` |
| ---: | ---: | ---: | ---: |
| 44,100 | 2,940 | 2,946 | 2,944 |
| 48,000 | 3,200 | 3,206 | 3,204 |
| 96,000 | 6,400 | 6,406 | 6,404 |
| 192,000 | 12,800 | 12,806 | 12,804 |

The largest capacity remains 3,578 below the frozen 16,384-frame cap. The
smallest admitted stationary-point example has `D=3`, `C=9`. A permitted
4,096-frame call can consequently overwrite one slot 456 times. Neither
`block_size<=ring_capacity` nor one journal entry per unique slot is an
assumption of A42's proposed per-write journal.

The cubic signs also give a direct output-bound check. For `0<=mu<=1`, the
outer weights are nonpositive and sum to `mu*(mu-1)/2`; the four weights sum
to one. Their absolute sum is therefore `1+mu*(1-mu)<=1.25`. Two signed paths
with gains at most `10/0.02` can approach 1,250 normalized units. Double output,
Horn-then-Drum order and an explicit later file-format policy remain necessary;
an implicit limiter would change the specified operator.

## Events and complete transaction ownership

A tied change away from and back to the same command must still be applied in
input order: it creates a new final anchor even when its final command matches
the entry command. An unchanged command retains its anchor. Offset-N events
precede the next call's offset-zero events; arbitrarily many zero-frame calls
consume commands without adding ring cells. At a later positive call, record
their final effective segment before solving that frame. Copying both native
owners lets final-boundary failures reject without changing committed motion.

**Required precondition 3 — define exact storage restoration.** A42 requires
restoring retained bytes, including unused initialized cells. A member-value
copy into `JournalEntry` must not be assumed to preserve an object's padding or
representation. Use a defined initialized cell representation and appropriate
byte snapshots/restoration of trivially copyable storage, or another reviewed
mechanism that meets the same requirement. Do not weaken byte preservation to
only phase/speed equality. Stage or journal occupancy, oldest/through metadata,
write indices, clocks and persistent diagnostics as well as sample/segment
cells. Initialize and restore the canonical journal/scratch representation,
including touched unused entries and counters.

With exactly one write per rotor per rendered frame, `N<=B<=4096` implies at
most `2B=8192` journal entries, independently of event density or wraps. Secure
each old cell before overwriting it and replay in reverse: a slot whose old
values were `A,B,C` must be restored `C,B,A`; forward replay would leave `C`.
Staging needs `2B` doubles, at most 65,536 bytes. Cell/journal byte capacity
depends on actual native layout and must use checked size arithmetic; this
review did not measure `sizeof` or allocate renderer storage.

Preflight every sample/event, span length, block/timeline bound and overlap
before any persistent mutation. Rendering can still fail late. Keep caller
outputs untouched until all paths, offset-N events and final owner advances
succeed; then publish through bounded nonthrowing operations. Rollback occurs
only after borrowed windows have ended. Do not clear the journal before the
last possible failure. The resulting guarantee is serialized per-call atomic
behavior, not concurrent publication. Failure returns zero consumed events;
returned observations may differ, while persistent diagnostics must not.

The API review still owns overlap with event storage, invalid-sample status,
status precedence, empty-span treatment, renderer copy/move policy and the
meaning of failure diagnostics. `ProcessResult` currently has no failing
frame/path locator. Native `solve` also leaves `PathResult` untouched on failure;
that destination cannot supply the failed solve's residual or evaluation count.
Define neutral failure fields or review a separate internal observation channel
while preserving the old public API. Per-call residual/iteration summaries also
need not be partition invariant: compare the frozen physical state and audio
across partitions, while checking all persistent diagnostics for rejection
restoration.

## Flush and stopped lifecycle

Let the last potentially nonzero input index be `L` and the first zero index
be `Z=L+1`. With `F=max_r(D_r)+4`, the final flushed output is at `n=L+F`.
Its oldest tap is at least `L`; a widened-bracket emission just below the next
integer can still give that last sample a small nonzero outer cubic weight.
The following frame `n=L+F+1` has every oldest tap at or after `L+1=Z` and is
therefore clear. This proves the prescribed complete flush; it does not require
its final output sample to be zero or authorize omitting it.

**Required precondition 4 — define who performs the flush.** Expose the
prepared count and let the caller supply exactly `F` zero-input frames through
ordinary bounded process calls, with motion continuing. The per-call rollback
guarantee does not automatically make a multi-call flush one transaction. If a
convenience wrapper is introduced, specify that scope and check total remaining
epoch space before its first call. Never wrap the clock, implicitly reset,
discard a remaining tail or hide `TimelineOverflow`. Silence already advances
the ordinary renderer; absence of processing freezes it.

All 16 ordered supported-rate pairs, including the four diagonal pairs, are
required. Native `reconfigure_sample_rate` starts a new epoch even for the same
rate; copying owners and invoking that method preserves phase, signed turns,
speed, commands and the separate original reset seed. Reconstructing a fresh
owner from the current state through `prepare` would lose those distinctions.
Rate replacement must rebuild silent waveform history and constant-current-
speed negative motion, recompute capacities and re-admit all four paths before
publication. Reset then restores the original preparation seeds/commands at
the current rate. Invalid or allocation-failed replacements preserve future
output exactly. No renderer allocation result or lifecycle test has been run
by this review.

## Frozen implementation acceptance remains complete

| Acceptance | Required evidence after implementation |
| --- | --- |
| Cubic operator | All 257 fractions `j/256`, integer endpoints, degree 0–3 independent polynomials with bounded support, negative indices, all four taps and unavailable history; error `<=2e-12`. |
| Static characterization | All `65*512=33,280` complex-error cells with no fitted phase. For `k=0..102` on `k/1024`, error `<=0.005`; retain the full higher-band characterization. |
| Same-cubic parity | At least ten seconds at each of the four rates with separate inputs, nonzero history, impulses, bounded signals and ramps. Independent motion/root/cubic oracle; each receiver's normalized maximum `<=2e-5`, plus raw maximum/RMS and worst coordinates. |
| Partition identity | One admitted absolute stream across blocks 1, 7, 64, 257, 4,096 and recorded irregular schedules, including ties/end events/zero frames/silence/suspension. Audio and final physical state bit identical on the same executable. |
| Ring and solver seam | Exact tags, before/on/after boundaries, both bracket endpoints, negative startup, repeated wraps, original anchors older than the retained ring, newest/oldest coverage and late-epoch fractions. Compare new and immutable paths where both histories cover the query; requalify affected R2/R3 gates after shared-kernel changes. |
| Transactions and lifecycle | Nonzero histories, rejected first/last inputs/events, missing support, repeated slot overwrites, every path's late failure and final-boundary failure; byte snapshots plus identical future continuation. All 16 rate pairs, original-seed reset, allocation-failed replacement, complete flush and epoch overflow. |
| Structural scene tests | Separate inputs, coincident receivers, full receiver swap, signed cancellation and admitted common translations/+z rotations. Exact structural symmetries and tolerance-based coordinate transforms must not be confused. |

Construct dense-event stress legally: changes to both rotors at every rendered
frame need two events per frame, so calls contain at most 512 such frames
under the unchanged 1,024-event cap. Continue these calls across multiple ring
lengths. Separately test a maximum 4,096-frame call with at most 1,024 events
and repeated wraps; choose the partition-identity stream so every partition
also meets that event limit. A 4,096-frame block containing 8,192 events is an
invalid-input test, not a valid maximum-load case.

Use a private deterministic failure seam to reach actual late rollback exits
that valid inputs cannot reliably provoke; never dereference expired storage,
corrupt memory or weaken solver limits. The existing general reference tool
has no waveform operator, so it is not already an R4 oracle. Preserve separate
identical-trajectory solver error and independently computed motion error.

The next decision belongs to the waveform owner: resolve these four interface
preconditions and the remaining API choices, then implement narrowly owned
history, solver-seam and transactional-renderer packets with the frozen
acceptance matrix. R4 discrete parity, R5 audible reconstruction policy, R6
runtime/Engine/device integration and physical M7 fidelity remain separate.
The [complete M0–M9 plan](../PLAN.md), M5/M6 dependencies and scanner G5 failure
remain intact. No dry Engine, parameter or saved-state change is proposed here.
