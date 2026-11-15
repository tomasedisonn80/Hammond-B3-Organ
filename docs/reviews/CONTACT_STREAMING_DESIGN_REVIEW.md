# Independent review of the contact streaming proposal

**A40, 15 November 2026 — accepted as a direction for the isolated arithmetic
and trajectory design spike, with the contract conditions below.** This is
source and mathematical review, not acceptance of a streaming implementation,
callback deadline, physical model or Engine/VST3 integration.

## Reviewed basis

The [proposal](../CONTACT_STREAMING_NEXT_DESIGN.md) is explicitly unadmitted.
It preserves the [frozen model](../FRACTIONAL_CONTACT_REFERENCE.md),
[v1 protocol](../CONTACT_SWITCHING_VALIDATION.md) and their source-specific
[executed results](../CONTACT_SWITCHING_RESULTS.md). These inspected SHA-256
identities bind this review:

| Input | SHA-256 |
| --- | --- |
| Streaming proposal | `58d794fddfee5b27c9319453359948f2eb97215d0fa384f38cfb1cf5fe5b4908` |
| Frozen model | `3c05da4c3f35fcdc53fac05f1592ddc97e444f5038d9c147afae71f46e8deecd` |
| Frozen protocol | `5ccbba4d08a2272bef4f7d553446a7ca9582e289fba80f9bcfa223a2d6efb2b5` |
| [Offline kernel](../../tools/fractional_contact_reference.py) | `fc269514eca98c05ee8fb14ff362248d140862cff942a250a01714bb06788e23` |
| [Study runner](../../tools/contact_switching_study.py) | `eb4d374cc46ed1c16448ab3b1c2f03c5714a27c20bfdd0c3dba6e005d8f8066e` |
| [Independent oracle](../../tools/contact_switching_oracle.py) | `17f6d93fb5d8fbb5eb1b0d36c609449f9c8b9b94e44ab10a80450f04bb2cf9d4` |

## Delay, cells and drainage

The proposed **D=16** schedule is mathematically consistent. For
`z[m]=y_L[m−16]`, the greatest contributing cell index is
`j=(m−16)L−(−16L+1)=mL−1`: the coefficient at `r=−16L` is exactly zero.
That cell ends at `m−1/(2L)`, before host time m. Emitting before integrating
`[m,m+1)` therefore needs no future input. Counting the zero endpoint tap as
requiring the cell centered at m would incorrectly add a frame.

The oldest nonzero tap reaches `(m−32)L+1`; the proposed `32L+2` ring is ample
for this support and a partial centered cell, subject to an explicit retention
and eviction invariant. A cell straddling an integer boundary must survive it.
At N, gate closure finalizes the centered cell's remaining portion as zero;
it must preserve the already integrated left portion. None of this permits
reinitialization at callback boundaries.

N processing outputs cover reference indices −16 through N−17. The 33 drain
outputs cover N−16 through N+16, giving exactly N+33 outputs overall. Both
zero endpoints remain present. N=0 correctly retains the separate empty-render
exception. Incoming physical edges at N, the pre-edge ungated left limit used
for the gate jump, endpoint commands and the final snapshot must remain distinct.

## Conditions for the first frozen spike contract

1. **Preserve admission across calls.** The proposal retains v1's rounded
   command-coordinate collision rejection, but the implementation contract must
   define the retained state. In binary64, `(frame=1, fraction=nextafter(1,0))`
   and `(frame=2, fraction=0)` both display as 2, although their exact times
   differ. They can arrive in adjacent callbacks. A per-call-only duplicate
   check is insufficient; the later conflicting call must fail transactionally.
   Identical pairs retain their allowed caller ordering. Define which identity
   state survives processing, closure and reset.
2. **Prove the arithmetic representation before coding it.** Thresholds,
   targets and time-zero fractions permit binary64 subnormals. A literal
   numerator/denominator encoding of `2^-1074` already needs a 1075-bit
   denominator; ordinary fixed 64/128-bit rational pairs are insufficient.
   Exponent-based alternatives need their own proof. With fixed press/release
   velocities, a common-denominator representation may avoid denominator growth
   per command, but no bound is established by this proposal. Derive all
   position, arrival, root, clipping, midpoint and comparison intermediate
   bounds, including cross-products and every overflow rejection. Count worst
   operations; finite storage alone does not establish callback feasibility.
3. **Separate syntactic limits from admitted work.** The reference permits up
   to 4096 frames syntactically, but at L=256, K=4 and M=512 its conservative W
   is **71,595,078**, exceeding 20,000,000. “Retain the reference domain” cannot
   mean every combination of those maxima is already render-admitted. Specify
   the spike's admitted set and budgets explicitly; any extension and its
   comparison-reference execution need separately identified admission.
4. **Freeze partition-independent accumulation and rollback.** Callback edges
   must not create extra rounding boundaries. Specify a fixed host/cell/event
   traversal and deterministic accumulation state, preserving small signed
   contributions exposed by cancellation. Rejection must leave cursor, key
   histories, unfinished cells, ring, collision history and output unchanged;
   successful continuation afterward must be checked.

These conditions refine the next contract; they do not identify a defect in the
accepted offline kernel. The proposal already requires representation review
before filter implementation and keeps preparation/destruction outside processing.

## Evidence boundary and disposition

The proposed all-289-sample oracle, D=16-only alignment, retained tails,
partition equivalence and future-command causality checks are appropriate new
gates. The proposed `1e-4` limits and expanded quadrature resources are clearly
**unadmitted**, so they neither loosen nor retrospectively regrade v1's
64-probe admission. Their justification must be frozen before candidate errors
are inspected. Existing offline timing/RSS cannot qualify callback deadlines.

Proceed with the bounded representation derivation and independently specified
trajectory spike, incorporating the four conditions. Filter implementation,
full-window numerical admission, platform resource qualification, physical
acquisition and later adapters remain separate steps. This review inspected
documents/source and performed the displayed arithmetic and binary64 collision
calculation only; it ran no build, numerical study or runtime test.
