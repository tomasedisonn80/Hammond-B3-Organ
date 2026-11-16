# Independent review: next causal contact audio stage

**16 November 2026 — A50, `/root/w09_a50`, Wave 9.** The
[A38 proposal](../research/CAUSAL_CONTACT_AUDIO_NEXT.md) is consistent with the
current Python filter's indexing, causal schedule and complete output range.
Its initial N≤256 scope is a reasonable **proposed qualification domain**, not
a change to the admitted 4096-frame trajectory. This review admits those
derivations as planning inputs. **It does not freeze an audio contract, authorize
implementation, or confer an audio, callback, platform or physical grade.**

Before implementation, the owner still needs explicit decisions on portable
cell arithmetic, numerical accumulation, atomic composition, origin/reset
semantics, finite resource limits and independent full-window acceptance.
The requirements below concern the future audio layer; they do not invalidate
the current isolated trajectory's source-specific acceptance.

## Scope, source and independent work

Read the full `AGENTS.md` and [M0–M9 plan](../PLAN.md), current session scope,
checkpoint and ownership records, then inspected the actual
[Python renderer](../../tools/fractional_contact_reference.py),
[grid header](../../include/hammond/research/CausalContactGrid.h) and
[implementation](../../src/research/CausalContactGrid.cpp), their contracts,
the [frozen offline validation](../CONTACT_SWITCHING_VALIDATION.md), and the
[earlier streaming proposal](../CONTACT_STREAMING_NEXT_DESIGN.md).
No production, A38 proposal, shared navigation or existing acceptance file was
changed; no commit was made.

The independent [audit script](../development/2026-11-15-streaming-continuation/reports/A50-audio-contract-audit.py)
and [result](../development/2026-11-15-streaming-continuation/reports/A50-audio-contract-audit.json)
retain exact command, Python/platform, HEAD/tree, script and eleven input hashes.
Run from the repository root:

```sh
python3 -B docs/development/2026-11-15-streaming-continuation/reports/A50-audio-contract-audit.py
```

The bounded check reconstructed the documented kernel directly and compared
all 8193 coefficients with one actual coefficient construction. It checked
index/count algebra at **41,344 output positions across every N=1..256**, plus
the explicit N=0 convention, exact rational counterexamples and work arithmetic.
It called no audio renderer, native trajectory, continuous quadrature, build or
broad test suite. Comparing coefficient equations is not the independently
implemented continuous audio oracle required later.

| Binding | SHA-256 |
| --- | --- |
| A38 proposal | `131ea11770cefdba5f79c95808b7b51977276fcd2a85bbcf1b825e3994121b56` |
| Python numerical module | `fc269514eca98c05ee8fb14ff362248d140862cff942a250a01714bb06788e23` |
| Grid implementation | `17c1c1cdb8e0edb1c90f098e4e92f351eea4f2c50fab1e2282d3f7f304f9e9bd` |
| L256 normalized coefficient bytes | `600df579a3a4c4d4588f567587ad831c4f83114c9d8fb1cd34d6d3afee34a1fe` |

HEAD at inspection was `af2b74760ee195c9497b314a1a29172f5238dd44`, tree
`fb7d9ef7d1fcf24a70395c0671b75eb9c31558d4`; the hash inventory identifies the
working inputs beyond HEAD. A45's filesystem identity repair changes
`contact_switching_io.py` from `e3219265…` to `1281cd07…`. An independent
comparison with that published commit found the complete numerical module and
all eight parser-function source segments unchanged. The changed whole-file
I/O identity must still appear in new report provenance. Historical study
reports retain their old identities; this source check does not rebind them or
qualify the repaired I/O path. See the separate
[Windows repair admission](CONTACT_REFERENCE_WINDOWS_REPAIR_ADMISSION.md).

## 1. Indexing, causality and tails are correctly derived

Let L=256, H=16, and let C[j] be L times the integral over the centered cell,
with the raw signal gated to [0,N). The source constructs normalized c[k] for
k=0..32L from the centered kernel at `(k−16L)/L`. It forces both support
endpoints to **positive binary64 zero** and mirrors the evaluated half exactly.
The observed normalizer is 256.0011286257794, coefficient sum 1.0 and absolute
sum 1.8402427952028448. The independent equation calculation reproduced every
coefficient byte on this interpreter.

Actual `render` iterates cells in ascending j, so the correct translated form is:

```text
y[n] = fsum_j C[j] * c[nL - j + 16L]
z[m] = y[m - 16] = fsum_j C[j] * c[mL - j]
```

After removing the zero endpoint weights, the potentially contributing indices
are `(m−32)L+1 <= j <= mL−1`, clipped to `0 <= j <= NL`. The newest cell ends at
`m−1/(2L) = m−1/512`, before input time m. C[mL] crosses time m but has zero
weight in z[m]. Emitting z[m] before integrating [m,m+1) is therefore causal.
The decimator must select mL, with phase zero. A conventional FIR library's
coefficient orientation, initial padding and decimation phase require an
explicit mapping to this equation.

D=16 is also the least integer delay under this particular emit-before-input
schedule: D=15 would need a cell ending at `m+511/512`. This is algebraic
latency, not observed host/device latency. A coefficient such as c[255] is
nonzero, so a signal connected early enough can produce ringing before output
index 16. Only z[0] is universally the leading endpoint zero; forcing a
16-sample zero prefix changes the signal.

| Input length | Process outputs m | Drain outputs m | Reference indices n | Total |
| --- | --- | --- | --- | --- |
| N=0 | None | None | Empty convention, first_frame=0 | 0 |
| N=1 | 0 | 1..33 | −16..17 | 34 |
| N=256 | 0..255 | 256..288 | −16..272 | 289 |

For every N>0, the inclusive reference interval −16..N+16 has **N+33**
samples. N samples have already been emitted by processing, leaving exactly
**33**, including z[N+32]=0. This remains true for silent nonempty epochs.
N=0 is a deliberate exception, not a 33-zero drain.

## 2. Partial cells and closure need more than final contact bits

Cell boundaries are exactly `256j−128` and `256j+128` grid ticks. The initial
cell is clipped to [0,1/512); the terminal cell NL is clipped to
[N−1/512,N). At each ordinary host boundary, the cell centered there is only
partially known. Its accumulated completed pieces and any still-open connected
piece must survive the callback. An unchanged piece is completed at its true
cell/contact/gate boundary, independent of how calls were partitioned.

This matters even when the integral formula is mathematically additive. The
bounded audit finds a full cell centered at frame 1, frequency 0.1 cycles/frame
and phase .137 whose integral differs by `2.220446049250313e-16` when split
and rounded at the host boundary. It also reproduces
`fsum(1,2^-54,-1)=2^-54`, whereas first rounding `fsum(1,2^-54)` loses that
residual. A callback-dependent subdivision or prematurely combined gain is
incompatible with the proposed exact same-build partition result.

The grid returns incoming edges through the processing endpoint. Audio replay
must start from **entry** bits and apply these edges in exact order; final bits
cannot reconstruct the interval. At N, a physical break leaves a disconnected
final bit but may have a nonzero left-half terminal cell. A make exactly at N
can leave a connected final bit with no corresponding audible interval.
Closure then applies endpoint targets without travel, retains the physical
snapshot and gates only the right side to zero. The terminal gate jump uses the
ungated **left limit**, not post-edge bits. Release remains an ordinary target
plus subsequent processing.

The proposed ring is plausible only with a frozen eviction and interleaving
invariant. Before z[m], retain its needed completed cells and the open cell;
after emission, prune only cells below the next output's lower support bound.
The nonzero-support span plus the open cell needs at most 8192 consecutive cell
indices, within the proposed 8194 slots. This says nothing about rollback or
an algorithm that integrates an entire 256-frame call before producing its
early outputs; such an algorithm can overwrite required history. Storage and
work admission must cover the actual chosen schedule.

## 3. Portable exact clipping remains a required arithmetic contract

The grid proves that two 32-bit fractions can be compared by unsigned 64-bit
products. That proof does **not** cover endpoint addition, subtraction,
midpoints, or conversion from tick coordinates to host coordinates. The tighter
N≤256 proposal does not make all those operations fit a single uint64.

The audit retains two realizable one-key examples with press speed `2^32−1`
and release speed `2^32−2`:

- A make just before host frame 255 and a break just after it both display as
  binary64 255.0. Their positive exact width has an **80-bit denominator**;
  subtracting the two displayed endpoints incorrectly produces zero.
- A connected interval inside cell 65535 has an exact width requiring a
  **72-bit numerator / 80-bit denominator**, and a midpoint requiring an
  **89-bit numerator / 81-bit denominator**. All commands, positions, thresholds
  and roots lie within the proposed 256-frame grid domain.

These are counterexamples to a naive single-word rational implementation, not
an impossibility result. A reviewed mixed representation or fixed multiword
algorithm can handle them. Before coding, derive intermediate widths, signed
difference handling, canonicalization, exact clipping and rounding to binary64,
with finite operation bounds on every path. Account for the negative initial
cell boundary before gate clipping. A source phase formula must receive the
exactly formed midpoint; tiny nonzero widths must not disappear through prior
endpoint rounding.

Prepare the outward raw bound separately. The audit also records two smallest
positive binary64 route factors whose product rounds to zero while the exact
product is positive. Their correct outward B is the smallest positive
binary64 value. Cancellation, gain grouping or underflow cannot justify the
exact-zero routing fast path.

## 4. Required API and numerical decisions before implementation

| Decision | Missing concrete contract and required evidence |
| --- | --- |
| **A50-C1: arithmetic and summation** | Freeze the exact clipping representation and its proofs above; deterministic route/piece order; bounded replacement for `math.fsum`; handling of full-cell versus partial-cell operation order, signed zero, subnormals, rounding environment and contraction. Define cross-language comparison tolerances separately from exact same-build partition identity. |
| **A50-C2: atomic composition** | Specify a private stage/commit seam covering grid state, edge replay, audio cells/pieces, ring, source-origin state and output cursor. Current `process` commits its noncopyable grid after writing staged edges; `snapshot()` cannot restore it. Calling it first and then attempting audio rollback is insufficient. Include `close_observation`, whose grid commit otherwise precedes terminal-cell numeric work. Prove public grid semantics remain unchanged and require late-failure/short-output/retry preservation. |
| **A50-C3: state machine and results** | Freeze types, statuses, precedence, limits, required output lengths, extra-span handling and observable snapshots. Specify zero-count drain in each phase, the ready/active/closed/draining/drained transitions, partial-drain completion, repeated closure, output alias preconditions and serialized access. The proposal supplies intended behaviors, not these complete signatures and precedence rules. |
| **A50-C4: phase origin and reset** | Give `origin` an exact type, unit and admitted range. State whether reset reinterprets immutable phase values at the new origin for an independent replay or derives new per-source phases for continuity from an earlier absolute origin. Do not silently substitute one for the other. Within an epoch, phase depends on input time; notes, silence and callbacks never restart it, and drain advances only output m. Define the stopped/off-thread reset/reprepare/destruction boundary and old-rate drain before any new-rate epoch. |
| **A50-C5: finite resources** | Freeze per-call and per-epoch capacities for pending pieces, simultaneous events, exact arithmetic, summation, ring rollback and output staging. A valid one-cell burst can contain 4608 edges and 2304 connected pieces, as constructed below. Prove bounded sweeps without scanning every edge for every cell, and count all rejection/drain work. Measure prepared/object/stack bytes and allocation/free hooks on named builds; freeze deadline/headroom criteria separately for any later callback claim. |
| **A50-C6: independent grading** | Freeze exact-grid fixtures/oracle inputs, conversion/topology criteria for original fixtures, all output indices, numeric budgets, resource ceilings and retained reports before observing errors. Require independent trajectories and boundaries, all refinement levels, complete tails/responses, exact events/state, causal-prefix checks and same-build partition identity. An agreed test list alone is not a frozen acceptance protocol. |

Grid `prepare` and `reset` currently allow a new epoch after trajectory closure.
An audio wrapper must impose the stricter **fully drained** requirement to avoid
discarding tails, without changing the standalone grid's public behavior.
N=0 closure may enter drained immediately. Any future hard-abort policy needs an
explicit discarded-tail result; it cannot masquerade as normal drain/reset.

## 5. N≤256 and work counts are planning constraints

For L256, K4 and M512, independent evaluation of the current reference's W gives:

| Term | N=256 | N=4096 |
| --- | ---: | ---: |
| `(N+33)*(32L+1)` | 2,367,777 | 33,828,897 |
| `(NL+1)*9K` | 2,359,332 | 37,748,772 |
| `18M + (32L+1)` | 17,409 | 17,409 |
| **W** | **4,744,518** | **71,595,078** |

The first lies below the offline 20-million cap; the second exceeds it. N≤256
is explicitly the future audio qualification proposal. The existing grid remains
4096 frames / 512 commands / 4608 edges, and the offline reference retains its
own syntactic domain plus W admission. None of these counts measures a native
callback deadline or fully bounds the new arithmetic/rollback algorithm.

One 8194-double ring uses 65,552 bytes; 8193 coefficients use another 65,544.
An illustrative two-ring rollback design plus coefficients and 256 staged
outputs already uses **198,696 bytes**, before grid state, event/piece storage,
exact arithmetic, metadata, ABI padding and stack. This is accounting, not a
selected implementation or admitted memory budget.

The audit constructs a burst from the grid's affine equation: four keys, nine
contacts each with off=0/on=1, both speeds `UINT32_MAX`; command every key to
position 1 on even ticks and 0 on odd ticks from 0 through 127. The 512 commands
produce 4608 roots at `tick+1/UINT32_MAX`, all strictly inside cell zero's
positive half [0,128) ticks. They form **2304 separate connected pieces** in
that one cell, within an N=1 epoch. This is an exact counting construction,
not an executed native or audio test. A design can accumulate pieces without
storing every one, but must prove that accumulator's capacity, order and rollback.

## 6. Required next inputs and grade boundary

Grid speed s corresponds to full-travel duration
`P=2^48/(65536*s*F)=2^32/(s*F)` seconds. At all three admitted rates F has an odd
factor, so P is non-dyadic for every positive integer s and cannot be represented
exactly by a finite binary64 duration. Some speeds also fall outside the old
`.0001..1`-second range. A rounded duration can therefore change roots and
contact topology. A new exact-grid oracle is necessary; separately admit
conversion of the retained binary64 fixtures, preserving their originals.

The existing continuous admission grades 64 frozen probes per row. Its
all-289-sample L128→L256 convergence test does not supply the missing all-sample
continuous reference. A future protocol must extend independently converged
quadrature to every sample of every retained 289-sample row, preserve the old
refinements, response/tail diagnostics and failures, and separately freeze the
expanded time/memory/integrand budgets. The old 10-million-evaluation ceiling
cannot silently be enlarged. Proposed peak/B and eligible NRMSE `1e-4` limits
remain unadmitted, with the normalized RMS floor, B=0 behavior and only D=16
alignment still explicit.

The next concrete deliverable is an independently reviewed
`docs/CAUSAL_CONTACT_AUDIO_CONTRACT.md` resolving A50-C1 through C6, accompanied
by the portable arithmetic proof, private transaction design and frozen oracle/
resource protocol. Only then can an isolated implementation be graded. Extending
to 4096-frame audio, full-organ or indefinite processing, Engine/standalone/VST3
scheduling, host latency and callback retirement remains separate work.
Physical bounce, resistance, loading and calibration still require synchronized
identified contact/source/dry acquisitions; this review supplies none.
