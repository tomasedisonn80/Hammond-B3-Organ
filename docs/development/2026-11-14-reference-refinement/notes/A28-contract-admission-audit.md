# A28 — Independent contract and admission audit

Actual worker `/root/w05_a28_contract_admission_audit`, wave 5. Reviewed standing instructions, current scope/checkpoint/manifest, the complete M0–M9 plan, frozen R2/R3 contracts, final native Motion/Propagation, and A17/A19/A27 acceptance sources. Observed HEAD `e4968b2acd37b6f79683704356350070fe2fc329`; uncommitted inputs are individually identified in [the report](../reports/A28-contract-admission-audit.json). Root owns shared builds, status and publication. No production or budget changes.

## Independent conclusions

History admission matches the specified domains/statuses, exact native continuity including turns, inclusive coverage, negative epoch prehistory and final-endpoint overflow validation. Same-frame replacement and omission of unchanged snapshots remain caller responsibilities. The immutable backing segment objects must outlive every view/path copy; the original view need not survive. Upper-bound search chooses the new anchor at equality and takes at most `floor(log2(4097))+1 = 13` comparisons.

The circular distance norm is 1-Lipschitz, giving `rmax-rmin <= 2*radius <= 2 m`. The specified widening has `m <= 32*ulp(20) = 2^-43 m`; hence bracket width `W <= (2+2m)/300 s`. For an evaluable covered bracket, after `k` midpoint evaluations the exact-arithmetic residual bound is `1.25*W/2^k`. At `k=40` this is below `7.58e-15 s`: 40 midpoints plus two endpoints fit the 48-evaluation limit. The actual implementation counts every evaluation and publishes cached geometry. This derivation supplements its finite residual/derivative checks; it does not presume floating arithmetic or unavailable histories always succeed.

Local subtraction converts only bounded delay to split frames, checks integer subtraction and normalizes fractional borrow/carry. Every rejection exit in motion helpers/lifecycle, history preparation/query, geometry and path preparation/solve was inspected: public destinations/member publication occur only after successful validation/evaluation. More specific helper errors propagate. No production mismatch was found.

## Concrete coverage improvement

Existing negative-epoch solve cases reject at the first bracket endpoint. Root authorized one added test, `check_second_endpoint_turn_overflow`, in `tests/test_rotary_propagation.cpp`.

The admitted seed has phase `0.5`, speed `75 rad/s`, turns `INT64_MIN`, rate `48000`, and coverage through zero. Radius `1 m`, receiver `(2,0,0) m`, sound speed `300 m/s` give bracket `[1/300,3/300] s`. The first emission has phase about `0.25` without a turn borrow; the second would require phase `-0.25` and an overflowing negative turn. The test independently verifies those historical states, then requires `TimelineOverflow` with byte-identical path, history, segment and both caller outputs. Borrowed storage remains valid and immutable.

After root released the A25 quiet interval, isolated GCC 14.2.0 C++20/O2 compilation with warnings-as-errors passed. A temporary wrapper invoked only the new regression: **1/1 passed**, exit zero. The report retains exact argv, wrapper source, executable hash and stdout; reviewed production/test hashes remained unchanged. `git diff --check` passed. No shared build or logs were modified, and no whole-oracle replay is claimed.

## Material clarification and remaining scope

There is no contract failure from A26's `14.6426` accidental mean. MATERIALS acceptance 2 applies the ≥15 weighted-sRGB criterion specifically to natural-key centers. A26 reports paired means, not medians or per-pixel minima; its natural minimum paired mean is `63.8004`. No ≥15 accidental requirement exists.

Next: root integrates the added regression through its coherent CMake/CTest checkpoint. R4 waveform ownership/rendering, R5 policy, Engine/R6 integration, device deadlines and physical cabinet qualification remain separate.
