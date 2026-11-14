# R4 renderer: proposed implementation and independent acceptance plan

**Status: proposed engineering review; no R4 implementation or acceptance is
established by this document.** A42 of the reference-refinement session owns
this review. The separate waveform-continuation track owns its implementation
assignments under its [own scope](development/2026-11-14-waveform-continuation/README.md)
and [checkpoint](development/2026-11-14-waveform-continuation/CHECKPOINT.md).
Reconcile this input with its [renderer brief](ROTARY_RENDERER_PLAN.md) before
assigning code. That brief was inspected at incoming documentation commit
`26ff2fbe66a50260bd7601cbfa54c1f5d35ff3a8`; it is itself pending API review.
Neither session's workers or results count for the other.

The inspected product baseline is `f9c11a498ecd88886349415205fc5dccc627033e`.
The [numerical contract](ROTARY_NUMERICAL_CONTRACT.md),
[immutable propagation contract](ROTARY_PROPAGATION_CONTRACT.md), complete
[M0–M9 plan](PLAN.md), and current [R2](ROTARY_MOTION.md)/[R3](ROTARY_PROPAGATION.md)
runbooks govern this proposal. Their frozen limits, model, interpolation,
latency and acceptance budgets remain unchanged. The
[A42 receipt](development/2026-11-14-reference-refinement/notes/A42-rotary-renderer-next-plan.md)
identifies inspected files and documentary validation; it reports no new
native execution.

## 1. Deliverable and existing API boundary

Implement an independent, prepared C++ research renderer with separate
double-precision normalized Horn and Drum radiation-boundary inputs and Left
and Right outputs. Each receiver sums its Horn path and then its Drum path.
Each rotor has one command owner and one trajectory, queried at two different
emission times. All four paths use the existing point-source equations and
`reference_distance_m / distance_m`; directivity and microphone response are
the named unity/omnidirectional diagnostics. Preserve the qualified gradual
underflow behavior and exclude fast-math/reassociation from acceptance builds.

| Existing surface | Reuse and limitation |
| --- | --- |
| [RotaryTypes.h](../include/hammond/RotaryTypes.h) | Reuse `Profile`, `ProcessSpec`, `CommandEvent`, `ProcessResult`, `SamplePosition`, statuses and constants. These types do not provide a renderer. |
| [RotaryMotion](../include/hammond/RotaryMotion.h) | Value-copy two candidate owners; use `apply_command`, `advance_to`, `segment`, `epoch_initial_state`, `reset` and `reconfigure_sample_rate`. Only the current command anchor is retained. |
| [MotionHistoryView](../include/hammond/RotaryPropagation.h) | An admitted immutable borrowed fixture: first anchor zero, 1–4,097 canonical segments, inclusive endpoint. It cannot become a rolling queue by mutating its backing span. |
| `PreparedRetardedPath` | Copies the borrowed view, not its storage. Its solver has no latency or audio. Its private geometry/history coupling needs a separately reviewed streaming query seam. |
| [RotaryPropagation.cpp](../src/RotaryPropagation.cpp) | Preserve split-position subtraction, widened bracket, cached selected evaluation, endpoint-inclusive 48-evaluation limit, and residual checks when sharing the solver. |

The 4,097-segment fixture bound is not a streaming event capacity: commands
can change at every sample in successive accepted calls, and a 192 kHz delay
window can span more than 4,096 distinct command boundaries. Retaining every
event since epoch zero would also grow throughout the day. Repreparing the
current immutable view inside processing conflicts with its preparation
boundary and does not solve its anchor-zero/capacity restrictions.

## 2. Recommended streaming ownership; review before implementation

Use one bounded ring per rotor. A proposed `FrameCell` contains the absolute
frame tag, that frame's input sample, and a **copy of the current original
`MotionSegment`** after ordered events at that boundary. A segment may be
repeated in many cells. Never reanchor it at each sample or host block: doing
so changes the qualified floating-point evaluation and can break exact
partition identity. The copied segment may have an anchor older than the
ring; its original seed and anchor remain sufficient for the retained query.

Commands have integer frame offsets. For a nonnegative query `{k, mu}`, the
cell tagged `k` therefore identifies the command segment covering `[k,k+1)`.
Require the exact tag and coverage; call `evaluate_motion_segment_at` on that
copy. Missing positive history rejects, even if the current segment could be
extrapolated. Negative queries call `evaluate_motion_prehistory_at` with the
epoch seed; negative waveform indices independently return zero. Do not use
the current accelerating segment for startup.

Recommended new names are `MotionWindowView` and `PreparedStreamingPath`;
**neither exists in the inspected API**. The former should be an internal,
immutable, non-owning view of already admitted frame cells, epoch metadata
and explicit oldest/through coverage. The latter should own admitted geometry
only and accept a window for the duration of `solve`, retaining no window.
Use an internal concrete/template query seam to share the existing solver;
do not introduce user callbacks, concurrent publication or an unbounded search.
Keep the old view/path signatures and lifetime contract intact.

For each rendered frame: finish both ring writes, create the two read-only
window views, solve four paths, consume their results, and end **every** window
borrow before the next write or rollback. Allocated ring objects remain at
stable addresses throughout processing. A view copied into a persistent path
would defeat this lifetime rule. Preparation/reset/rate replacement are
serialized with processing and occur with no live window borrow.

Apply every tied event in input order to candidate owners. A command changed
away and back at the same frame may produce a new final anchor; reducing the
tie group merely to its net command would lose that behavior. Retain the final
segment when the frame is actually rendered. End-boundary and zero-frame
events update the owner, but create no waveform sample or speculative future
cell. The next positive call records their final effective segment before its
first sample. Thus arbitrarily many separate zero-frame calls do not grow a
history queue, and an offset-zero event follows the preceding offset-N event.

## 3. Exact capacity and causal coverage

For rotor `r`, let `Rr` be the maximum admitted `PathBounds::max_distance_m`
over its two receivers, `D_r = ceil(Fs * Rr / c)`, and prepare
`C_r = D_r + 2 + 4` cells. This is the frozen waveform-history formula.
The proposed combined cells use the same bounded frame window for motion.

| Rate (Hz) | Maximum `D_r = Fs*20/300` | `C_r = D_r+6` | Complete flush `D_r+4` | Epoch frames `86400*Fs` |
| ---: | ---: | ---: | ---: | ---: |
| 44,100 | 2,940 | 2,946 | 2,944 | 3,810,240,000 |
| 48,000 | 3,200 | 3,206 | 3,204 | 4,147,200,000 |
| 96,000 | 6,400 | 6,406 | 6,404 | 8,294,400,000 |
| 192,000 | 12,800 | 12,806 | 12,804 | 16,588,800,000 |

These are engineering maxima, not cabinet dimensions. `12,806 <= 16,384`
leaves 3,578 cells below the per-history cap. Reserving the full cap is also
permitted, but is a preparation choice, not a reason to change admission.
Check size arithmetic before allocation. Cell byte size depends on the C++
layout; report actual `sizeof` values rather than assuming packed structs.
At maximum derived capacity, waveform values alone occupy
`2*12806*8 = 204896` bytes; segment copies/tags and work storage are additional.

Account for the **actual R3 widened bracket**. At `rmax <= 20 m`, its largest
margin is `32*ulp(20) = 2^-43 m`, approximately `1.1368683772161603e-13 m`.
At 192 kHz and 300 m/s that adds at most
`2^-43*192000/300 = 7.275957614183426e-11` frames. Hence every evaluated
delay, including both endpoints, is less than `D_r+1` frames. It also remains
below the current subtraction helper's 13,000-frame guard. Do not treat a
rounded-up bracket endpoint as exactly the physical maximum.

After writing sample `n`, a `C_r` ring retains nonnegative tags from
`max(0,n-C_r+1)` through `n`. Observation is the split position `{n-2,0}`.
For emission `s=n-2-d_frames`, positivity gives `s<n-2`, so its floor
`k<=n-3` and the latest cubic tap `k+2<=n-1`: no future input is required.
The widened upper bound gives `k>=n-D_r-3`, so the oldest tap satisfies
`k-1>=n-D_r-4`. The ring starts no later than `n-D_r-5`; therefore all four
taps and the earlier bracket lookup remain covered, with one conservative
cell to spare. At startup, any negative tap is declared zero and negative
motion uses the seed. The minimum physical delay at the lowest rate is
`44100*0.02/380 = 2.321052631578947` frames; it does not remove the fixed
two-frame algorithmic latency.

Use checked integer epoch/frame arithmetic and floor indices throughout.
Never compute `double(n)+fraction` or subtract large absolute seconds.
`SamplePosition` already carries the required split representation; reuse the
qualified local-delay subtraction when factoring the solver. Enforce inclusive
motion coverage at `{n,0}`, rejecting `{n,positive_fraction}`. The last audio
index is `epoch_frames-1`; the end state and an end-boundary command may be at
`epoch_frames`. A further positive call rejects transactionally.

## 4. Rendering and proposed public call

The following is an API-review sketch, not callable repository code:

```cpp
Status prepare(const Profile&, const ProcessSpec&) noexcept;
ProcessResult process(std::span<const double> horn,
                      std::span<const double> drum,
                      std::span<double> left,
                      std::span<double> right,
                      std::span<const CommandEvent> events) noexcept;
Status reset() noexcept;
Status reconfigure_sample_rate(double) noexcept;
```

Recommend equal-length waveform spans, with `N=horn.size()`, and prepared
maximum block size in `[1,4096]`. Inputs may overlap each other. Outputs must
be disjoint from one another and from input storage. Specify whether this
includes the event span in the API review; the recommended rule includes it.
For zero frames, empty waveform spans are valid. Span lifetime/accessibility
remains the C++ caller's obligation; validation cannot prove arbitrary pointers
are valid. Freeze overflow-safe byte-range checking and status precedence before
acceptance. Recommend `InvalidBuffer` for length/overlap/nonfinite/out-of-range
sample rejection; the existing enum has no separate invalid-sample status.

Process sample boundaries in order: apply events, record Horn/Drum input and
segments, query the four paths at `{n-2,0}`, then interpolate each corresponding
rotor input at the returned emission. Use the prescribed Lagrange nodes
`k-1,k,k+1,k+2`; verify all support, even at a zero-weight endpoint. Integer
emission selects `x[k]`. Stage `HornGain*HornCubic + DrumGain*DrumCubic` for
each receiver in that order; preserve polarity. The frequency ratio is only a
diagnostic. Check finite results; do not clamp, normalize or add a pitch LFO.

The cubic absolute-weight sum is at most `1.25`, path gain at most
`10/0.02 = 500`, and two-path magnitude at most `2*1.25*500 = 1250` before
roundoff. Output must therefore remain double precision without an implicit
`[-1,1]` limiter. A later file adapter owns its explicit format/clipping policy.
Report latency as exactly two frames in addition to physical travel time.

## 5. Whole-call transaction and bounded resources

Preparation validates all motion fields and all four full-orbit geometries,
including the actual epoch seed speed, then allocates rings, scratch and
rollback capacity outside processing. Build a replacement completely before
publishing it; invalid input or allocation failure preserves the old renderer.
Keep large arrays on prepared heap storage rather than the callback stack.

Before any mutation, admit preparation state, equal span lengths, block/event
counts, checked end frame, valid rotor/command enums, nondecreasing offsets
in `[0,N]`, buffer ranges/overlap and **every** finite input in `[-1,1]`.
An invalid final event or final sample must not partially render earlier data.

Recommended transaction implementation:

1. Copy both small `RotaryMotion` owners and candidate clock/diagnostics into
   local values. Keep the committed owners untouched while rendering.
2. Before each rotor cell overwrite, append its exact old contents and slot
   identity to a prepared journal. Write the candidate cell only after its
   journal entry is secured. Repeated overwrites of a slot get separate entries.
3. Stage all `2*N` output samples. End each borrowed-window scope before any
   subsequent mutation. Apply offset-N events and advance candidate owners to
   the final boundary; their failures still reject the **entire** call.
4. On any late failure, reverse the journal, restore all modified ring bytes,
   discard candidate owners/diagnostics and leave caller audio untouched.
   Return the failure with `events_consumed=0`.
5. On success, commit caller audio and candidate owners/clock/diagnostics using
   bounded, nonthrowing operations after the last possible failure. This is a
   serialized call transaction, not concurrent atomic publication.

Scratch and journal storage must return to their pre-call canonical contents
on both exits; a rejected call must not leave private persistent counters or
work-storage state changed. Preserve old cell bytes in the journal, including
overwritten unused cells. Tests should snapshot all initialized retained
storage, not merely current angle and audio. Returned failure observations are
caller values, not persistent diagnostics. `ProcessResult` currently has status,
events consumed and maximum residual/iteration fields, but no failed frame/path
locator: agree their exact failure meaning or review a renderer-specific result
extension before promising more detail.

For prepared block bound `B<=4096`, journal at most `2*B<=8192` cell writes and
stage `2*B<=8192` doubles (65,536 bytes). End/zero-frame events require no ring
write. A call can exceed a short scene's ring size: reverse journaling handles
multiple wraps without requiring `B<=C_r` or enlarging the frozen history cap.
There are at most `4*B*48 = 786432` path evaluations, `16*B = 65536` cubic
tap reads and 1,024 event applications per maximum call. Each proposed motion
lookup is one tag lookup plus bounded native segment evaluation. These are
operation bounds, not measured execution time or an audio deadline pass.
No process allocation/deallocation, resource destruction, lock, file, logging,
UI access or caller callback is permitted.

## 6. Stopped lifecycle and tails

Reset restores the **originally prepared** rotor states/commands at the current
rate, frame zero, silent waveform history and original constant-speed negative
motion. Stage both owner resets before clearing/publishing storage. Do not make
reset adopt the most recent rate-epoch seed as its original seed.

A stopped rate replacement preserves current phase, signed turns, speed and
commands; calls the existing owners' rate replacement on copies; starts a new
zero frame; recomputes capacities and full-orbit admission with those seeds;
and replaces waveform history with silence. Its negative motion is uniform at
the preserved current speed. Old acoustic tails are explicitly discarded.
The existing owner also starts a new epoch for an accepted same-rate call;
include that diagonal case unless a separate API review changes the wrapper's
documented call semantics. Invalid/allocation-failed replacement preserves all
old output behavior. Time constants remain seconds.

Silence advances motion and history; absence of processing freezes them.
Zero-frame calls apply offset-zero commands without advancing either clock or
waveform history. No STOP/brake command, note/transport reset or GUI clock is
introduced. Musical presets do not save these transient histories.

After the final nonzero input sample, flush `max_r(D_r)+2+2` zero-input frames
through ordinary processing, splitting by the prepared block bound. Motion
continues. With the widened-bracket inequality above, the next frame after this
flush has its oldest cubic tap at or after the first zero input; include an
explicit test of the final possible tail and the following zero output.
Do not flush past the epoch limit implicitly; report overflow or arrange a
shorter admitted render in advance.

## 7. Independent acceptance to execute after implementation

All cases below are **planned**, with unchanged frozen thresholds. Retain
source/compiler/executable/profile/oracle hashes, commands, seeds, actual
maximum/RMS error, worst coordinates and every failed original result.

| Gate | Exact required experiment |
| --- | --- |
| Cubic operator | Integer endpoints and all 257 fractions `j/256`, `j=0..256`; represent the last fraction as the next integer position. Independently evaluate degree 0–3 polynomials with four support samples bounded by one. Error against the specified expression `<=2e-12`; cover negative floor indices and all four taps. |
| Static characterization | All `65*512=33280` cells: fractions `j/64`, frequencies `k/1024` cycles/sample, `k=0..511`. Compare `sum_j w_j(mu)*exp(i*2*pi*f*j)` against `exp(i*2*pi*f*mu)` with no fitted phase. For `k=0..102` (`f<=0.1`), complex error `<=0.005`; retain the full higher-band grid and failures without a broadband claim. |
| Window/solver seam | Before/on/after events and oldest/through boundaries, negative startup, unavailable tags, repeated ring wraps, initial/maximum capacities, both bracket endpoints and late-epoch split fractions. Compare the new window's states/roots against immutable canonical fixtures where both cover the same history; rerun affected R2/R3 budgets after solver extraction. Never dereference expired storage to test lifetime. |
| Native same-cubic rendering | At **each** of 44.1/48/96/192 kHz, at least ten seconds with separate Horn/Drum impulses, bounded deterministic signals, populated history, signs and command ramps. Use an independent event timeline/root solver and independently expressed cubic weights, not native output as the expected signal. Per receiver, `G=sum_rotors(reference_distance/r_min)` and `max(abs(native-reference))/G<=2e-5`. Retain raw absolute/normalized maxima and RMS; no gain/phase/time fitting. |
| Partition/event identity | Same executable, same absolute stream: blocks 1, 7, 64, 257, 4,096 and recorded seeded irregular partitions; events before/on/after boundaries, ties, unchanged commands, offset-N then offset-zero, zero-frame calls, silence and suspension. Require bit-identical audio and final physical state; inspect retained original anchors. Choose a reproducible seed before execution, e.g. `20261114042`, and retain the full schedule. |
| Two-input/two-receiver identity | Isolate each input; coincident microphones; swap both receiver positions completely; identical-path signed cancellation; common translations and rotations about +z with phase transformed and every coordinate still admitted. These are rigid transforms representable by the frozen horizontal-orbit model; arbitrary tilted axes require a different model. Apply the same-cubic budget to transforms; exact structural symmetries should be bit identical on one executable. |
| Transactions and capacity | Invalid first/last sample, event, bounds, overlap and timeline; event count 1,025; block 4,097 or prepared-bound+1; valid maximum counts and dense changes at every frame over multiple ring lengths. Snapshot nonzero history, owners, diagnostics and sentinel output bytes, reject, then compare future accepted output exactly with a control run. Exercise failure after earlier output has been staged, all four path positions, an overwritten slot visited repeatedly, and final offset-N processing. |
| Lifecycle/tails | All **16 ordered** supported-rate pairs, including same-rate calls, with nonzero histories and active ramps; preserve current state/commands, clear tails, restart constant-speed prehistory, then reset to original seeds at the new rate. Invalid rate/spec/profile and injected preparation-allocation failure preserve future output. Check complete flush and epoch endpoint/overflow. |

A deterministic private test seam may force a late solver/numerical failure
that valid admitted public inputs cannot reliably induce. Keep it out of the
production public API; do not weaken residual limits or rely on corrupted or
expired memory. Review its coverage of the actual rollback exit, including
the last frame, before accepting transactional evidence.

Reuse the independent high-precision motion/root infrastructure in
[the R2 gate](../tests/test_rotary_motion_acceptance.py) and
[the R3 gate](../tests/test_rotary_propagation_acceptance.py) where appropriate.
The general [reference tool](../tools/rotary_reference.py) has no waveform
operator; its ordinary geometry is binary64. Do not label it an already
complete high-precision R4 oracle. Preserve the R3 distinction between
identical-trajectory solver error and independently computed motion error.

## 8. Dependency-ready code tasks and open decisions

These are proposed work packets for the waveform owner, not assignments or
claims that the named new files exist:

| Order | Narrow proposed ownership | Acceptance before the next packet |
| --- | --- | --- |
| 1 — API review | Reconcile this review and the concurrent brief; specify `RotaryHistory.h`, a streaming path surface, and `RotaryRenderer.h` declarations. | Resolve window visibility/lifetime, exact-capacity versus full-cap allocation, copy/move policy, span/status rules, failure diagnostics and private fault-injection ownership. Recommend no copied/moved renderer while prepared/processing, and value-only external inspection. Record approval without editing frozen budgets. |
| 2 — History/operator | New `include/hammond/RotaryHistory.h`, `src/RotaryHistory.cpp`, focused new history tests. | Own tagged combined cells and pure cubic lookup; prove oldest/newest/negative support, original-anchor retention, ties, wrap and fixed allocation. No Engine or solver change in this packet. |
| 3 — Streaming solver | New streaming path header/source and a narrowly shared internal kernel extracted from `src/RotaryPropagation.cpp`; preserve the old public API. | Compare old/new query paths on common fixtures and pass affected exact R2/R3 gates, with unchanged arithmetic/evaluation counting and no borrowed view surviving a write. |
| 4 — Transactional renderer | New `include/hammond/RotaryRenderer.h`, `src/RotaryRenderer.cpp`, focused lifecycle/transaction tests. | Full four-path rendering, preflight, journal rollback, final events, scratch restoration, rate/reset/tail behavior and source-only research API. |
| 5 — Independent R4 gate | Separate native renderer probe, Python same-cubic oracle/acceptance file, and evidence report; owner coordinates minimal CMake/test registration later. | Execute the full matrix above; retain source-identified failures and parity/partition results. No guessed CTest target or unexecuted pass. |
| 6 — Runtime scope | A calibrated allocation/deallocation probe and sanitizer workload on the **new renderer's** actual accepted/rejected/lifecycle calls. | Establish only the recorded renderer runtime workload. Existing R3 allocation evidence does not cover R4 storage, journals or calls; deadlines/integration still need their own evidence. |

R5 requires its own frozen reconstruction/filter/alias policy and converged
spectral reference. R6 Engine/host integration needs explicit controls, saved
state, latency and device evidence. No proposed task here connects Engine,
changes the 47 parameters or state4/readers 1–3, or resolves scanner G5.
M5 dry-organ validation and revision-specific M6 electrical/driver ownership
remain prerequisites for downstream fitting. Horn transit, crossover, driver,
cabinet, room and directional/microphone filters have no owner in this renderer.
An identified Leslie 122/147 specimen, geometry/motion/acoustic captures and
held-out comparison remain necessary for physical M7; synthetic R4 parity
cannot supply them.
