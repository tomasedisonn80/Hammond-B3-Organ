# Source leakage contract admission - A10

**Decision: admit the corrected v1 contract for implementation.** This is a
design/admission review, not an implementation, DSP execution, physical-fidelity
or Engine-headroom acceptance result.

- Reviewer: `/root/w02_a10_leakage_review`, wave 2, assignment A10.
- Checkout: `/workspace/scratch/7802a6528f89/Hammond-B3-Organ`.
- Observed local HEAD: `56d448f64fd37ffa10ad93ac6e2c5b4f27917b21`.
- Original A07 contract SHA-256:
  `bd374b8318be321667dfcd978b8cac7fb944349f843865bc40bf7e4a2a008c9e`.
- Corrected admitted contract SHA-256:
  `277e82d3aa9ec6a4b57dbbbc50fdce4990de5042b745234bcf8fdecd6b55a7c3`.
- Read the complete AGENTS.md and M0-M9 plan, A01/A07, session scope/checkpoint,
  the complete core and audition proposals, and the existing Decimal API.
  A truncated instruction output was reread before review.

## Corrections incorporated before admission

| Finding | Correction and why it matters |
| --- | --- |
| Compiler/native row admission was underspecified across summation algorithms. | Both explicitly accumulate absolute binary64 gains from positive zero in canonical source order, rounding each addition. Python `sum`, `math.fsum`, exact/decimal sums and reordered reductions cannot replace this operation. |
| The exact mathematical output limit was overstated as 1.5. | Distinguish the exact coefficient sum from its stored rounded sum. The latter defines admission; exact coefficients and evaluated arithmetic may exceed the nominal 1.5 bound by roundoff. The separately reviewed explicit Engine gain/reserve remains necessary. |
| Spectral acceptance did not name transform normalization or inspected bins. | Freeze N=1024, source bins 7/31/97, input amplitudes at most 0.5, no window, positive-bin complex normalization 2/N, bins 1-511, and separate 1/N DC/Nyquist checks. Record graph/recipient/phase choices before production execution; derive expected coefficients independently. |
| Syntactically complete bytes could be confused with a successful read. | Explicitly reject an observed underlying stream I/O failure even when its prefix contains `end`; clean EOF remains valid. Destination-preserving rejection is retained. |
| Allowed subnormal coefficients need an explicit floating-point environment. | Name round-to-nearest binary64 with gradual underflow (FTZ/DAZ disabled) as the numerical domain; A12 independently owns the integration reserve for very small input gains. |

The first distinction is practical across supported Python versions: the
[official Python 3.12 `sum` documentation](https://docs.python.org/3.12/library/functions.html#sum)
records a changed floating summation algorithm. More accurate accumulation is
useful generally, but substituting it would change this contract's explicitly
chosen admission semantics. This review does not prohibit accurate independent
oracles; it only fixes the compiler/native acceptance operation.

The integrator approved the minimal clarifications before editing. A07 was sent
the findings and exact boundary fixtures; no API, capacity, gain limit, physical
assumption or model equation was changed.

## Concrete boundary fixture and derivation

Use destination 91, distinct sources 1-8, and positive gains in their canonical
source order. Both following assignments obey individual gain and count limits:

- `[0.25, six copies of 2^-56, 0.25]`: each tiny addition to 0.25 is one quarter
  of its binary64 ulp and rounds away. The stored sum is exactly 0.5: **admit**.
- `[six copies of 2^-56, 0.25, 0.25]`: the six tiny terms add exactly; their sum
  is 1.5 ulps at 0.25. Ties-to-even rounds that addition upward by two ulps,
  yielding `nextafter(0.5,+infinity)` after the final 0.25: **reject**.

These are different assignments of gains to donors, not two permitted
accumulation orders of one graph. Shuffling an input list before canonical
preparation must preserve that graph's result. Their equal exact coefficient
sum is slightly above 0.5, illustrating why the stored admission result must not
be described as an exact physical or mathematical sum. This is a binary64
derivation and predeclared future fixture; no candidate implementation was run.

## Remaining implementation acceptance

The corrected contract is coherent and implementable with fixed value-owned
storage. Its simultaneous `x + Cx` definition admits cycles without feedback,
canonical ordering prevents caller-order dependence, and a complete candidate
frame preserves alias safety and failure atomicity. The 91-value input domain,
8/728 limits and bounded gains prevent finite arithmetic overflow; downstream
unit bounds are a separate integration obligation. Exact empty/uncoupled copies
preserve signed zeros. Preparation has no reason to retain external memory.

Implementation reviewers must still observe all declared gates, especially:

1. Independent dense-reference cases, cancellation, bidirectional edges and a
   three-node chain that would expose accidental `C*C` propagation.
2. Native and compiler agreement on both boundary fixtures, subnormals,
   duplicate/self edges, malformed metadata and count/order limits.
3. Sentinel preservation after invalid input, invalid reprepare and read errors;
   in-place processing; valid empty-graph identity; invalid ID queries.
4. Actual bounded storage, zero core allocation/deallocation and no retained
   pointers; meaningful maximum-capacity timing with identified inputs.
5. Source-bound compiler/native round trip and spectral evidence at all declared
   rates, followed by separately qualified Engine/headroom/CLI behavior.

The `synthetic` provenance and `excludes-leakage` input assumption remain explicit.
The author digest is a supplied declaration until actual source bytes are
compared. Nothing here qualifies acquired coupling, physical adjacency, default
audio changes, host state migration or the user's whole-interface 1:1 objective.

Only the contract, this review and A10's note were edited. No production code,
build configuration, tests, commits or publication were performed by A10.
