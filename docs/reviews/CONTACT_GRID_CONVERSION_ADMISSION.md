# Independent admission of the contact-grid conversion contract

**A10 decision: admit the corrected contract for implementation and independent
acceptance work.** This admits the finite, offline trajectory certificate
`fractional-to-contact-grid-rne-v1`, not an implementation, an audio result,
native integration or physical fidelity. No mathematical or interface blocker
remains in the corrected version reviewed here.

| Input | SHA-256 |
| --- | --- |
| [Admitted contract](../CONTACT_GRID_CONVERSION_CONTRACT.md) | `e5b4d26e9d74aef41fc5c6abe351597d43097da3faed5af6a26d0e3e557e18c0` |
| [Preserved original proposal](../development/2026-11-16-conversion-material/reports/converter-proposal-before-admission.md) | `dfc2f4a1828d98434528c6d17e94a50724470fb3ff239e0c712f88fe8155b894` |

A10 read the complete standing instructions and M0–M9 plan, current session
entry/checkpoint, the earlier [A49 review](CONTACT_GRID_CONVERSION_NEXT_REVIEW.md),
the unchanged fractional admission/trajectory kernel, integer-grid target,
position, crossing, interval and closure implementation, native probe grammar,
filesystem preflight, and the actual F09 input. The
[independent calculation](../development/2026-11-16-conversion-material/reports/A10-independent-arithmetic.py)
and [receipt](../development/2026-11-16-conversion-material/reports/A10-independent-arithmetic.json)
retain source hashes. No candidate helper, native process, build, waveform or
36-fixture conversion study was used for this decision.

## Corrections completed before admission

The original proposal had one publication-boundary inconsistency: an
unconditional interrupt/unchanged-output promise conflicted with successful
`os.replace` being the commit point. The corrected contract promises destination
preservation for interruption observed before publication. A completed
replacement is irrevocably committed; post-commit handling cannot report that
publication failed or promise rollback. Implementation must respect that
boundary, including temporary cleanup and asynchronous-interruption handling.

Root also clarified the shared **4,096 union-knot total across all keys**, ASCII
lexicographic label order, and a deterministic changed-relation witness that
does not require quadratic pair search. These corrections change no numerical
tolerance, input domain, source model or physical claim. The original proposal
bytes remain retained separately.

## Arithmetic and event correspondence

Exact rational RNE correctly maps time to ticks, normalized position to `2^48`
units, and duration to `2^32/(F*P)` units/tick. The independent script agrees with
Python's `Fraction` rounding in **24 midpoint/neighbour cases**, checks the six
rate/duration domain endpoints, and verifies the effective-duration error
denominator is the **rounded speed**. Its four scalar collision fragments and
actual F09 equality calculation reproduce the prior findings. F09's source edge
equals `375/32` frames, while the rounded-grid edge is earlier by exactly
`7/2932031008` frames. A small numerical error cannot excuse that changed tie.

The collision set includes implicit zero/full travel and all key thresholds and
targets. Global time admission covers different keys, while canonical source
and gain subnormals survive in the bit sidecar. A positive subnormal target
colliding with zero is explicitly refused. Distinct contacts remain distinct
when they share a source or are muted.

The new predicate checks command movement signs/repeated-target facts, contact
occurrences, reached-target arrivals, boundaries, final bits and final-target
mapping. Adding arrivals closes the earlier ambiguity around clamping and
command-at-arrival equality. Positive-duration travel owns an arrival; a
zero-duration intermediate command does not invent one. No-op commands still
count and remain in event evidence. Persistent anchors follow the named replay
semantics: unchanged targets preserve them, genuine target changes—including
tied intermediate changes—anchor at that command's exact position/time.
Implementers must not substitute callback-dependent anchors when constructing
analytic root bounds.

A sequence of exact-time equality groups determines every pair's `<`, `=` or
`>` relation. Equal label universes and equal prior groups ensure that the first
different groups S/G are nonempty. If x belongs to S only, x occurs later in the
grid; any y in G is either source-tied with x or source-later. Their relation
therefore changes. The symmetric case is identical. Choosing x from the
lexicographically first symmetric difference and y as the other group's minimum
is sufficient. ASCII-sorting the reported pair only fixes its orientation.

The independent script enumerates **all 75 total preorders of four labels** and
checks all **5,625 ordered pairs** against direct pairwise relations. All
**5,550 unequal pairs** yield the prescribed valid witness. This finite check
supports the general argument; it is not a candidate replay test.

## Numerical budgets and evidence limits

The chosen maxima, **`2^-18` normalized travel** and **`2^-10` host frames**,
have explicit units and are appropriate as conservative limits defining a
research subset. They are neither Hammond specifications nor perceptual/audio
tolerances. The root allowance is 64 ticks, approximately 10.17–22.14 ns across
the admitted rates. Rejections remain legitimate results; admission rates must
not become a reason to loosen these limits after inspecting candidates.

Both paths are continuous and piecewise affine. On every interval of the union
of their knots, their difference is affine, and its absolute value reaches a
maximum at an endpoint. Evaluating that complete union—including 0/N, commands,
arrivals and hold boundaries—therefore gives the continuous position supremum.
N=0 still requires the zero-position endpoint observation. Maximum witnesses
must follow the contract's key/time tie order.

For matched eligible roots, write `r=a+d/v` and `r'=a'+d'/v'`, with positive
speed magnitudes. The triangle inequality gives

```text
|r'-r| <= |a'-a| + |d'-d|/v' + d*|v'-v|/(v*v')
         <= Ea + (Etheta+Ep)/v' + d*Ev/(v*v').
```

This works for both movement directions because `d` and `d'` are positive
distances; topology and matching directions are checked first. The script
independently verifies **128 rational examples across both directions**.
Propagated anchor-position error must be used, rather than the scalar half-unit
bound. Bounds alone establish neither root eligibility nor identical contact
functions between shifted roots.

## Schema, work, transport and publication

The single JSON artifact resolves the earlier multi-file publication ambiguity.
It carries the explicit grid case, canonical admitted binary64 bits, exact
records/witnesses, numerical maxima and one-block CGGRID1 transport (close-only
for N=0). The transport's **131,072-byte** limit and final-endpoint commands
match the existing native probe. Native full snapshots and partition/retry
behaviour remain implementation acceptance tasks.

Strict nested type/shape admission must precede exact comparison: Python's
Boolean/integer equality is not a substitute for rejecting Boolean counts.
The encoder's bounded sidecar reconstruction and second conversion reject
inconsistent supplied facts. That replay is a consistency guard, **not an
independent oracle**. Original-byte metadata can only be bound by the CLI's
actual admitted read; the encoder cannot authenticate bytes it never received.

The segment, edge, arrival, record, shared-knot, integer-bit, work, report and
diagnostic caps are finite and permit explicit resource refusal. They do not
constitute an observed memory or deadline result. Implementation review must
verify checks occur before further use, source bounds cover all loops, and
event ordering/witnesses contain no hidden quadratic scan. The second conversion
shares the cooperative CLI deadline. External timeouts are unqualified runs,
not accepted cases. Exact witnesses that exceed the refusal cap become explicit
resource refusals, rather than silently truncated mathematical evidence.

Existing path admission rejects aliases, output-leaf symlinks and nonregular
endpoints; a same-parent temporary plus rechecks and replacement implements the
declared single-file transaction. Failure injection and real platform results
are still required. The separate five-file installation component must preserve
the old 48-file component and unchanged kernels; no implicit native-probe or
audio installation is admitted.

## Required next evidence

Freeze and retain A12's independent full fixtures, then implement the separate
numerical and CLI modules. Before completion, require independent trajectory
comparison, all 36 original outcomes, native edge/full-snapshot comparison over
partitions/retries, malformed/forged certificate cases, filesystem/interrupt
failure injection, resource observations and exact source bindings. Retain any
failures. This protocol admission supplies no causal audio/filter/tail result,
live Engine route, full-organ capacity or physical calibration.
