# Source leakage audition: independent contract admission

**Decision: admitted after the A12 numerical-bound correction.** This admits
the implementation contract, not an implementation, production test run,
hardware result or combined harmonic/leakage release.

Reviewer: `/root/w02_a12_audition_review`, wave 2, 15 November 2026. Production
source inspected at `276664ee8570c208bb007cca59f496963ca13ef5`: `Engine`,
`PedalRouting`, `Profile`, and renderer argument/path/setup/summary/publication
code. Read the full AGENTS/M0–M9 plan and both leakage contracts. The original
A08 audition draft SHA-256 was
`74e912dd473e4f85f125b3c84f8bab9000d7ca43812744dd5f1e40e8164d6f04`.
The final corrected contract hash is retained in the [A12 note](../development/2026-11-15-audio-continuation/notes/A12.md).

## 1. Numerical defect and retained counterexample

The original relative reserve is sufficient to keep the very small example
below inside `[-1,1]`, but it is not always an upper bound on its output. Let
`eta = denorm_min(double)`, use eight distinct incoming sources with gain
`1/16`, put all original source values at `+1`, and select input gain `9*eta`.
Canonical row sum is exactly `0.5`.

| Quantity | Original binary64 result |
| --- | --- |
| Explicit input gain | `0x0.0000000000009p-1022` |
| `(1 + R) + 64*epsilon` | `0x1.8000000000040p+0` |
| Original reported bound | `14*eta`, `0x0.000000000000ep-1022` |
| Canonical leakage result | `17*eta`, `0x0.0000000000011p-1022` |
| Corrected outward bound | `31*eta`, `0x0.000000000001fp-1022` |

Each donor product rounds from `9/16*eta` to `eta`, so eight additions produce
`9*eta + 8*eta`. A purely relative allowance vanishes at this scale. This is a
real bound-reporting defect, not an observed unsafe pedal input.

The parent authorized the narrow correction before implementation. For a
nonempty graph and positive gain, the contract now uses:

```text
row_bound = (1.0 + R) + 64.0 * epsilon
product_bound = input_gain * row_bound
guarded_bound = nextafter(product_bound + 16.0 * eta, +infinity)
```

Require finite `guarded_bound <= 1`. A nonempty graph at gain zero has bound
exactly zero; an empty graph retains bound `input_gain`, including the exact
gain-one arithmetic bypass. No coefficient limit, pedal domain, parameter or
default audio behavior is weakened. L-A3 now requires actual sample magnitude
to remain within both the reported bound and `[-1,1]`.

## 2. Bound argument under the stated arithmetic

The assumptions are binary64, round-to-nearest, gradual underflow, the specified
order and no fast-math reassociation. Let `u = epsilon/2` and
`gamma_k = k*u/(1-k*u)`. There are at most eight incoming terms.

1. Correctly rounded multiplication is monotone, so `abs(fl(g*x)) <= g` for
   admitted `g >= 0` and `abs(x) <= 1`, including subnormal `g`.
2. For exact coefficient sum `S`, the stored positive canonical sum `R` gives
   `S <= R/(1-gamma_7)`. Positive addition is exact in the subnormal region;
   normal additions satisfy the usual relative bound. Thus the rounded sum's
   possible underestimate is included, rather than assuming `S == R`.
3. Bound the eight donor products and eight additions using relative error `u`
   and absolute underflow error at most `eta/2` per rounded operation. For
   `R <= 0.5`, a conservative enclosure is
   `abs(y) <= g*(1 + R + 16*epsilon) + 9*eta`. Signed cancellation cannot
   enlarge the absolute-value enclosure. A fused product/add, if supported,
   has no more rounding error than this separate-operation enclosure.
4. The written `64*epsilon` reserve leaves ample room for the rounded `1+R`
   and gain product: the intermediate product is at least
   `g*(1 + R + 62*epsilon) - eta/2`. Adding `16*eta` covers the absolute
   remainder; outward `nextafter` prevents the final addition from rounding
   the assembled upper bound downward.

The corrected bound therefore encloses the canonical output. The reserve is
deliberately conservative and is not a calibrated physical uncertainty.
Production acceptance must still exercise its exact compiler/arithmetic and
real pedal consumer; this argument does not excuse an ignored runtime failure.

## 3. Independent arithmetic observations

Executed Python binary64 arithmetic only; no new C++ implementation or build
was run. The six rows were eight `1/16` gains, two `1/4`, five `0.1`, two
`nextafter(1/4,0)`, eight `eta`, and `[eta,1/4,eta,1/4]`. Inputs used aligned
signs at unit magnitude. Gains covered signed zero, `k*eta` for `k=1..512`,
the smallest normal and its neighbors, `0.5`, `0.65`, the admitted normal
boundary and its next value, and `1`. Rejected gains were excluded from the
output-bound comparison.

| Observed arithmetic check | Result |
| --- | --- |
| Admitted row/gain cases | 3,121 |
| Original reported-bound violations | 540 |
| Corrected reported-bound violations | 0 |
| Pedal-domain violations in admitted cases | 0 |
| Eight-`1/16` largest admitted gain | `0x1.555555555551cp-1` |
| Its corrected bound / output | `0x1.0000000000000p+0` / `0x1.fffffffffffacp-1` |
| Next gain, correctly rejected | `0x1.555555555551dp-1` |
| Next gain's corrected bound | `0x1.0000000000001p+0` |

The original counterexample can be reproduced without production code:

```python
import math, sys
eta, eps = math.ulp(0.0), sys.float_info.epsilon
g = 9 * eta
old = g * ((1.0 + 0.5) + 64 * eps)
new = math.nextafter(old + 16 * eta, math.inf)
y = g
for _ in range(8):
    y += (1 / 16) * g
assert (old / eta, y / eta, new / eta) == (14.0, 17.0, 31.0)
```

These observations support the stated bound argument and retain the failure.
They are not exhaustive production testing or evidence about a physical organ.

## 4. Lifecycle, source and offline integration admission

The current Engine already prepares candidates before committing, preflights
events before changing state, advances one source field through disconnected
output, and computes the pedal diagnostic even when output is absent. The
required insertion point is after source generation and before the first pedal,
manual or percussion consumer. Configuration installation must not relabel the
last pedal frame, change route coefficient caches, or synthesize elapsed time.
The contract's set/clear/error precedence, preparation reset, control-restore
independence and rate preservation are coherent with those existing boundaries.
The configuration query now explicitly returns defaults before first prepare.

The harmonic owner was inspected read-only at its exact local commit
`3622651d248ea13de4bccc32fb2c2043fb3db53d`. Its harmonic producer uses the same
sine-then-cosine ordering as its admitted L1 bound, with separately rounded
products; each term's magnitude is no larger than its coefficient magnitude.
Monotone ordered accumulation bounds the result by the stored nonnegative L1
sum. Suppressed terms become zero, the final amplitude is in `[0,1]`, and the
exact-fundamental branch preserves the legacy bounded sample. This supports
the required `[-1,1]` input invariant for that inspected source. It does not
establish publication, integration or combined execution in this checkout.

The renderer's existing canonical regular-input checks, absent-output policy,
private temporary WAV and no-overwrite hard-link publication are suitable for
the added graph path. Add the graph to preflight collision checks and complete
loading/headroom setup before temporary output creation. The current renderer
publishes before its final stdout confirmation; a later stdout failure can
coexist with a newly published WAV. Do not reinterpret that inherited behavior
as a rejected-setup rollback guarantee. The new schema-5 fields are correctly
conditional; old default summaries and PCM remain subject to exact regression.

## 5. Required implementation evidence

The existing L-A1–L-A7 gates are admitted with the correction. Prioritize the
retained underflow example and normal adjacent gain, actual pedal `Ok` results
at aligned full rows, rejection-preserved future Engine samples, exact
default/identity samples and PCM, donor-without-donor-key routing, zero-frame
and disconnected-phase continuity, graph/output alias refusal, paired flag
failures, and schema-5 facts bound to actual input bytes. Test physical controls
and harmonic composition only after their relevant source is integrated.

No production model, audio test, callback timing, host/device qualification,
whole-interface equality or specimen-fidelity result is admitted by this review.
