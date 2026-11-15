# Contact streaming: next engineering proposal

**Status: unadmitted proposal, 15 November 2026.** This specifies the next
isolated prototype and review evidence; no streaming implementation, callback
qualification or physical result is delivered here. Preserve all 47 parameter
identities, `B3CONTROLS4`/readers 1–3, 91 source identities and default dry Engine
behavior.

The [accepted offline results](CONTACT_SWITCHING_RESULTS.md) cover 36 fixtures,
144 renders, complete 289-sample convergence and independent continuous
admission at 64 probes per fixture. [A30's review](development/2026-11-15-execution-continuation/notes/A30.md)
and the [final identity receipt](development/2026-11-15-execution-continuation/reports/qualified-study-numeric-identity.json)
bind that evidence to the repaired installed execution. The
[frozen model](FRACTIONAL_CONTACT_REFERENCE.md) and
[protocol](CONTACT_SWITCHING_VALIDATION.md) remain unchanged. Their exact input,
implementation, fixture, probe and report hashes remain the comparison baseline.

## Independent review conditions

The [A40 review](reviews/CONTACT_STREAMING_DESIGN_REVIEW.md) accepts only the
isolated representation/trajectory design task. Its next contract must retain
rounded command-coordinate collision history across callbacks; prove exact
arithmetic and intermediate bounds including binary64 subnormals; distinguish
syntactic maxima from cases admitted by the frozen work ceiling; and specify
deterministic partial-cell accumulation plus complete transactional rollback.
At L256/N4096/K4/M512 the conservative count is 71,595,078, above 20 million.
The delay/drain derivation below stands; no streaming implementation is admitted.

## 1. Causal signal boundary and latency

Start with a separate C++20 research module, provisionally
`contact-stream-prototype-v1`, using the same fixed-load switched sine equations.
Initially retain the reference domain: 44.1/48/96 kHz, at most four keys,
36 explicit sources, 512 commands and 4096 input frames per epoch. Use L=256,
H=16 and beta=0.45. These prototype limits do not qualify full-organ polyphony
or indefinite live operation; extending them needs another boundedness review.

Declare output timeline m to contain `z[m]=y_L[m−16]`: algorithmic delay D=16
host frames, with the reference gain unchanged. At integer m, emit the delayed
sample from completed cells, then integrate input interval `[m,m+1)`. The last
nonzero contributing cell is centered at `m−1/L` and ends at `m−1/(2L)`;
the coefficients at ±16L are exactly zero. Thus this kernel needs no future
input beyond m. This is a proposed scheduling convention, not measured device
latency. A later extra buffering frame must be separately declared.

Carry the unfinished centered cell across each host boundary. Never synthesize
missing future commands, switch a base-rate waveform before upsampling, or
restart convolution at a callback boundary. Evaluate each source from its
absolute **input** time and common phase origin, including silent/disconnected
periods. Delay shifts output timestamps; it does not change source phase.

## 2. Histories, ordering and runtime number representation

Keep position, target, movement anchor and nine contact bits independently for
each key. Foldback/shared sources permit shared waveform evaluation only after
those histories have been resolved. Signed and zero-gain routes retain their
events. Do not prematurely combine route gains when cancellation can expose a
smaller contribution.

Resolve the incoming segment through an event time, including threshold
equality, before applying commands at that time in caller order. Their last
target controls outgoing motion; commands themselves create no edge. Repeated
targets are exact no-ops and must not rebase an ongoing movement. Use full
unsaturated velocity for roots, split at arrivals, preserve hysteresis while
holding, and order genuinely equal roots by key then contact input index.

The offline `Fraction` operations needing a reviewed replacement are command
coordinate construction; position/velocity/arrival arithmetic; target and
threshold equality; eligibility and root ordering; cell/gate clipping; and
endpoint subtraction/midpoints before waveform conversion. Two distinct exact
roots may have the **same rounded display time**. Preserve their order and
nonempty intervening interval; neither epsilon merging nor subtracting two
rounded endpoints is acceptable. Retain the existing rejection of distinct
supplied command pairs colliding at a binary64 absolute coordinate.

For the bounded first prototype, propose prepared fixed-capacity integer/rational
state with checked arithmetic and precomputed per-key denominators. An independent
derivation must establish limb widths, intermediate-product bounds and maximum
operation counts for the entire admitted domain before implementation. Arbitrary
`Fraction` arithmetic is an offline reference technique, not a callback plan.
If exact bounded arithmetic proves impractical, propose a separately identified
quantized input model and measure its errors; do not silently narrow v1 or call
rounded histories equivalent. Prepare the exact outward raw bound B off-thread,
including subnormal products; nonzero routing must never become a zero-bound case.

## 3. Proposed public API and lifecycle

Proposed new paths are `include/hammond/research/ContactStream.h` and its isolated
implementation/tests; these names describe future files. No Engine, host SDK,
parameter registry or saved-control dependency belongs in this prototype.

| Operation | Required meaning |
| --- | --- |
| `prepare(config, limits)` | Outside processing: validate the complete configuration, prepare coefficients/representation, allocate all storage and return explicit capacities. |
| `process(frames, targets, output)` | `noexcept`, contiguous internal cursor; accept sorted targets in `[cursor,cursor+frames)`, retaining caller tie order. Emit exactly `frames` delayed samples. Endpoint commands belong to the next call. |
| `close_observation(endpoint_targets)` | At the current integer cursor N: resolve incoming equality, apply commands at N without travel, retain the final key snapshot, and close the synthetic raw gate. Record its jump from the ungated left limit separately from physical edges. |
| `drain(output)` | After gate closure, feed zero raw input and emit every remaining delayed sample; bounded partial drains preserve state. Return an explicit completed status. |
| `reset(origin)` | Stopped/drained only: clear travel, contacts, cells and tails; explicitly declare the new absolute phase origin. Never use reset for note release. |

Whole-call validation precedes mutation. Capacity, invalid-input and numerical
failures preserve output, cursor and all state using prepared staging storage.
Preparation owns copied immutable configuration; processing borrows spans only
for the call. Processing after gate closure is rejected.
An empty process with no targets and an empty drain are identities; a zero-frame
process with targets is rejected. An N=0 observation accepts ordered endpoint
targets but generates no edges or audio, matching the reference empty case.

For N>0, process emits m=0 through N−1; drainage emits m=N through N+32,
**33 additional samples**, preserving every reference n=−16 through N+16.
This counts delay plus terminal support, including endpoint zeros. A physical
release is a target toward zero and continues travel/source/filter evolution;
it never closes the observation gate. Gate closure is the experiment's explicit
truncation. Streaming shutdown happens after drainage and callback retirement;
destruction stays off-thread. An explicitly requested hard abort discards tails
and cannot pass a continuity claim.

Reject rate changes while active. Drain at the old rate, then prepare/reset a
new epoch with an explicit phase-origin policy. This does not claim seamless
rate conversion. Preserve all live histories through ordinary block partitions.

## 4. Storage and processing budget

Prepare coefficients, a ring of at least `32L+2` cell values, a partial-cell
accumulator, per-key/contact state, bounded command/edge scratch, rollback state
and output staging for a declared maximum block. No whole-epoch audio array is
required. Admit command/epoch/work limits before processing; overflow rejects
the call instead of dropping events or resetting histories.

Use bounded deterministic summation and fixed-capacity event handling. Processing,
drain and failure paths must perform no allocation/deallocation, locks, file I/O,
logging or exceptions. Preparation may be expensive; its cost and ownership are
separate. The offline study's wall time and resident memory establish no callback
deadline.

## 5. Independent acceptance before live wiring

Freeze a new protocol and fixture manifest before examining candidate errors.
An independent author must extend continuous quadrature to **all 289 samples**
of every retained row, reconstructing trajectories and integration boundaries
without candidate helpers. Retain all refinement levels, complete arrays,
response grids, tails, source/fixture/toolchain hashes, failures and resources.
The existing 64-probe admission cannot supply this missing grade.
Expanded quadrature needs separately admitted operation/time/memory budgets;
the original 10-million-node ceiling is not silently extended.

Proposed, **unadmitted** starting budgets are oracle refinement peak/B ≤1e−9
and eligible NRMSE ≤1e−7; streaming versus admitted continuous output peak/B
≤1e−4 and eligible NRMSE ≤1e−4. Review their justification and freeze them
before execution. Retain scaled metrics, the normalized RMS eligibility floor
1e−8 and exact silence for B=0. Apply only the declared D=16 alignment, with
no fitted gain/delay or tail trimming. These proposals do not regrade v1.

Require exact event identity/order/final contact bits; same-build output and
state must be identical across single-frame, irregular and maximum-block
partitions. Add equal-display/distinct-root cases, endpoint ties, no-ops,
reversals, source cancellation, subnormal bounds, partial drains, N=0, capacity
failures and successful continuation afterward. Changing future commands must
not change already emitted output. Review long-run phase/counter and full-manual
capacity extensions separately before product use.

Measure prepared bytes, operation counts, allocation hooks, callback distributions
and worst observed time on named Release builds/hardware, including maximum
event bursts, one-frame blocks, silence and drainage. Freeze platform-specific
deadline/headroom criteria before grading; averages alone cannot qualify them.

Before Engine/VST3 wiring, review numerical/lifecycle/resource receipts and the
physical acquisition gate: identified specimen/revision, synchronized travel,
nine contact traces, source phase and dry output, calibrated clocks/bandwidth,
probe loading, repeatability, uncertainty and untouched held-out trials. Missing
captures keep physical fidelity open. Bounce, resistance, transformer loading,
harmonics/leakage, percussion and expression need their own model boundaries.
Any later adapter integration additionally needs latency reporting, musical
ownership, scheduling, callback-retirement and unchanged-default PCM evidence.

## 6. First implementation task and exit evidence

First assign an isolated representation-and-trajectory spike: prove the bounded
arithmetic above, expose the proposed admission/state API, and replay the retained
commands causally against independently reconstructed exact histories. Freeze
its contract before coding; do not implement the audio filter until review admits
the representation, equality/order cases, rejection rollback and D=16 schedule.
Exit evidence is a source-bound independent review with retained counterexamples,
capacity/operation derivations and replay results. Then implement and grade the
isolated streaming filter under the new full-window protocol. This sequence is
the durable next task, not completion of the real-time phase.
