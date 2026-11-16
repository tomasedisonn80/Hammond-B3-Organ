# Contact-grid conversion resource and arithmetic review

**A19: scoped resource acceptance passes for the recorded public API and repaired
source.** The final suite passes **23/23 methods in 3.254 seconds**. The unchanged
independent numerical suite also passes **12/12 methods**, retaining all 71
inputs and all 51 accepted exact comparisons. This is finite synthetic offline
qualification; it is not a callback memory, physical or audio accuracy result.

The [resource receipt](../development/2026-11-16-conversion-material/reports/A19-resource-final.json),
[numerical rerun](../development/2026-11-16-conversion-material/reports/A19-numerical-rerun.json)
and [external-process receipt](../development/2026-11-16-conversion-material/reports/A19-process-final.json)
bind the actual sources, commands, original outcomes and observations. Each test
process had a 60-second external timeout. No timeout occurred. Production and
test inputs stayed unchanged during the final runs.

## Actual capacity boundaries

The new [test suite](../../tests/test_contact_grid_conversion_resources.py)
constructs its own complete inputs and mathematical expectations. It imports
the candidate only at its public conversion/encoding/exception boundary and
does not use the candidate replay or private budget helpers as an oracle.
Every route in the maximum-motion fixture has zero gain: silence must not remove
contact histories or exempt any trajectory check.

At 48 kHz with binary-exact duration 1/8192 second, complete travel takes exactly
375/64 frames. Commanding alternating full press/release every eight frames
therefore completes 512 moves within 4096 frames. The test independently derives
every source and grid edge/arrival time, including all contact identities.

| Constructed case | Observed result |
| --- | --- |
| 512 complete moves, one key | Accepted: **4608 edges, 512 arrivals, 5634 labels**, 1537 union samples; all exact root times match the independent closed-form expectations |
| Same maximum case | **162464 work units**, maximum retained rational size 49 bits; encoded certificate **4555161 bytes**, CGGRID1 text **10865 bytes** |
| 511 off-grid no-op commands, four keys | Accepted: **4096 union knots**, exactly 1024 per key; all positions remain zero; 29933 work units |
| 512 off-grid no-op commands, four keys | Refused with `resource/position_samples`: **3078 retained + 1026 next-key knots**, exceeding 4096; no truncated accepted result |
| Four keys, 512 complete moves after positive initial holds | Exactly **1028 segments per replay**: 512 command intervals, four initial holds and 512 post-arrival holds; an injected limit of 1028 accepts and 1027 refuses |
| First binary64 fraction above 2^-53 at frame 1 | Accepted with exact fraction **2^-53 + 2^-105**; retained rationals reach **135 bits**, and all nine edges plus one arrival encode correctly |

The 1032-segment limit is conservative. A replay has at most C+K nonempty
command/end intervals, and a reached target can split an interval once. Thus
segments are at most C+K+A, no more than 512+4+512=1028 under the existing input
authority. The constructive test reaches that bound. No claim is made that a
normal admitted input can exceed the conservative 1032 limit.

The knot case has 511 source command times, 511 distinct rounded times, and two
boundaries. All four keys retain that global union, so 4*(2*511+2)=4096. One
additional command raises the required total to 4104. This exercises the actual
normal limit rather than an artificially reduced one.

## Rational arithmetic and the 8193-bit sum question

The frozen [contract](../CONTACT_GRID_CONVERSION_CONTRACT.md) limits **transient
products** to 8192 bits and every reduced retained numerator/denominator to 4096
bits. It does not assert that every unreduced addition accumulator fits 8192.
The production comment uses the same product-specific wording.

If both operands have at most 4096-bit numerator/denominator, multiplication,
division and comparison cross-products have at most 8192 bits. Addition can sum
two such products and require **8193 bits**. The independent arithmetic test
constructs this explicitly; its reduced result still exceeds 4096 bits and
would require refusal before retention. This is an arithmetic illustration,
not a claim that the public binary64 source domain reaches those operands.

Source review finds checks on both operands before each `calc` operation and
on the reduced result before retention/use. Unary sign/absolute operations
preserve bit lengths. The fraction library's addition may use the extra sum bit;
its products remain within the admitted product bound. Consequently the proposed
8193-bit concern requires **no arithmetic change or threshold relaxation**.

Public certificate tests separately verify the exact retained-number boundary:
a well-formed 4096-bit forged rational passes shape/bit admission but fails the
mandatory numerical reconstruction; a 4097-bit numerator or denominator receives
a `resource` refusal first. Oversized decimal strings are bounded before integer
decoding. The tests do not call a private arithmetic helper to manufacture an
unreachable source case.

The unchanged original parser rejects a subnormal fractional time at frame 1
because adding it to the frame loses it in binary64. At frame 0 the same fraction
passes that original admission but the converter correctly refuses its interior
time collapsing onto tick zero. Both outcomes are now explicit tests. An initial
stress-test assumption to the contrary is retained in the
[failed additional-probe run](../development/2026-11-16-conversion-material/reports/A19-resource-verified.txt);
it was a test error, not a candidate failure or reason to change original input
admission.

## Schema, work, byte and deadline guards

The suite checks all declared array families, aggregate preorder-label count,
Boolean/integer alias rejection, long numeric/transport strings, cyclic and
10000-level malformed certificate values. Fixed schema admission rejects these
before any recursive equality comparison. It also exercises the actual 32 MiB
aggregate string guard using aliased in-memory rows whose expanded JSON would
exceed 120 MiB; aliasing keeps the adversarial fixture small while every repeated
field still counts toward the representation bound.

Explicitly labeled fault injections lower the work, edge, arrival, event,
segment, transport and encoded-byte limits to known case boundaries, then lower
them by one. They prove guard behavior, not that normal inputs reach every
conservative limit. The certificate test includes the final LF in its byte
boundary. The ordinary limits and all frozen fixtures remain unchanged.

Source review covers the named operation counter: command applications, segment
and contact visits, emitted roots, swept knot lookups and event-sort
key/comparator evaluations use the common budget. Position lookup indexes only
advance across sorted knots, avoiding a new full segment scan per knot. The
reported-count boundary test verifies enforcement; it is not an independent
proof of counter completeness. These are complementary source and execution
checks.

Deadline tests exercise exact expiry, expiry during conversion, invalid and
nonfinite deadline inputs, and expiry on JSON output iteration. They observe
cooperative refusal. No hard process deadline or portable resource ceiling is
inferred from them.

## Retained diagnostic defect and minimal repair

The public `ConversionRefusal` constructor originally allowed an uncaught
`RecursionError` when its caller supplied a deeply nested diagnostic witness.
The original failing single-test run and source hash are retained in
[A19-diagnostic-initial.txt](../development/2026-11-16-conversion-material/reports/A19-diagnostic-initial.txt)
and its [receipt](../development/2026-11-16-conversion-material/reports/A19-diagnostic-initial.json).
Normal converter-created witnesses have bounded, shallow shapes; this is a
narrow public-constructor robustness gap.

After root assigned the production file sequentially from A13, A19 added only
`RecursionError` to the existing JSON-sizing exception tuple. It now uses the
same bounded `resource/diagnostic` fallback. No API, numerical operation,
ordering, counter, original model, contract or frozen expected value changed.
Tests also cover exact 8192-byte diagnostics, the first oversized byte, cycles,
nonfinite values and non-JSON witness objects.

| Numerical source | SHA-256 |
| --- | --- |
| Original A13 source, failure observed | `77d48ab503daf4ebaf89e1195685d0a78957989ce7fe67e8881c68928ea81c93` |
| Repaired and qualified source | `eff387f8457040ea67400dcb378ee1c2049b604d7c862fd6ca683b52c8f93797` |

## Observed resources and remaining gates

The final resource test process took **3.254644 seconds** and reached a Linux
process high-water RSS of **187764736 bytes**. This includes unittest, adversarial
objects, conversion, certificate reconstruction and encoding. It is not an
allocation count or per-call peak, and the 32 MiB output limit is **not** a
32 MiB process-memory promise. No large certificate or audio payload is retained
in the repository; input recipes, hashes, sizes and small reports reproduce the
observations.

Native exact-grid equivalence belongs to A21; CLI transaction/process acceptance
belongs to A20; installation/relocation, coherent CMake integration and exact
published-source platform results remain root's separate gates. Audio filtering,
full-window error, indefinite/full-organ operation, live Engine integration,
callback deadlines and physical contact calibration remain unqualified.
