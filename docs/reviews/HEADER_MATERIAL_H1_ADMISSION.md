# H1 header material: independent protocol review

**A27, 17 November 2026: admit the clarified revision 1.1 contract**, SHA-256
`07d64498a14431b64742d79e7fbe4d2ac71d77fe51d09f71c638f52594fd9282`, subject to
its existing accepted-T3, genuine-baseline and independent fixture/checker
prerequisites. No H1 candidate was painted or simulated. All 103 thresholds
remain unchanged; this protocol admission is not immediate painter permission.

The original A22 proposal, SHA-256
`d818189557308c6d8624ec1e1f855a730f3a8aac0ac2abefd0f8e2520bdd99cc`, was held for
the sole arithmetic ambiguity documented below. It is preserved byte-for-byte
as [the original proposal](../development/2026-11-16-heading-title-continuation/inputs/HEADER_MATERIAL_H1_PROPOSAL_v1.md).
The [clarified contract](../design/HEADER_MATERIAL_H1_CONTRACT.md) and original
[observation report](../development/2026-11-16-heading-title-continuation/reports/a22-header-observations.json),
SHA-256 `8f591b6d80bb6934a955ac2eb4b0005b78c4c164434510bc7125b4c511856c7b`,
retain every numerical limit. This is a protocol review, not acceptance of the current
rejected T3 painter, H1 pixels, a frame deadline or whole-interface equality.

## H1-R1: original hold and pre-candidate resolution

The report says to take binary64 square roots, sum errors in
`primary_patch_order`, and divide by 18. The contract refers to that declared
binary64/summation order without naming the summation operation. Independently
reconstructed patch errors expose a one-ULP distinction:

| Aggregation of the same 18 binary64 errors | Baseline mean absolute RMS error |
| --- | ---: |
| Running binary64 accumulator in the declared order, then division | 1.6673172881480463 |
| Python 3.12.14 `sum`, then division | 1.6673172881480465 |
| `math.fsum`, then division | 1.6673172881480465 |

The last two reproduce the original report. Its unchanged maximum is
**0.8336586440740232**, binary64 `0x1.aad54e48a6b98p-1`, exactly half the
recorded baseline `0x1.aad54e48a6b98p+0`. No existing before pass/fail changes;
the ambiguity matters because independently written candidate checkers must
make the same decision at the boundary.

The recommended explicit wording, now incorporated in revision 1.1, was:

> For each primary patch, convert its exact rational SSE/N once to binary64
> and apply Python `math.sqrt`. Compute
> `e_i = abs(rms_candidate_i - rms_reference_i)` in binary64. In
> `primary_patch_order`, aggregate the resulting 18 binary64 errors with
> `math.fsum`, then divide that binary64 sum by `18.0` once. Do not replace
> `math.fsum` with a running binary64 accumulator or ordinary `sum`. The
> recorded baseline `1.6673172881480465` and maximum
> `0.8336586440740232` remain unchanged.

Root preserved the original proposal and report, then submitted the separately
identified [arithmetic clarification](../development/2026-11-16-heading-title-continuation/reports/h1-arithmetic-clarification.json).
A27 independently rehashed both contract versions and the unchanged report and
inspected the complete two-hunk diff. It adds only the visible clarification
note and the explicit aggregation paragraph above. No patch, field coefficient,
seed, support, case or threshold changed. The clarified operation reproduces
the original baseline/limit and resolves H1-R1 before any H1 candidate. The old
hash remains a blocked historical proposal; admission applies only to
`07d64498a14431b64742d79e7fbe4d2ac71d77fe51d09f71c638f52594fd9282`.

## Original images and pre-candidate gates

Read the entire `AGENTS.md` and M0–M9 plan, current session README, checkpoint
and actual ledger, A22's note, H1/T3 contracts and relevant painter, layout,
Drawing, fixture and pinned SDL source. Directly viewed the unchanged full
reference and persisted T2 canonical application frame. The original has
different lateral color and upper falloff from T2; its illustrated preset/gear
shadows cannot become permanent substitutes for the native utilities.

Python 3.12.14, Pillow 13.0.0 and libjpeg-turbo 3.2.0 independently reproduced
all four input file identities, dimensions and decoded RGB hashes. The original
JPEG hash is `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187`;
the T2 canonical PNG hash is
`96a9fb295200307ffb7b459ee8a146d83579a881aafcd54b1cc73a7ed1b2b55c`.
All 14 source/input identities retained by A22 also still matched when checked.

An independent ordinary-coordinate covariance calculation reproduced all
**200 scalar planes**: 25 rectangles, two images and RGB plus encoded Y′.
For each plane it checked the integer moments, exact rational mean and both
slopes, exact residual SSE, binary64 RMS and recorded decimals. Together with
image/patch identities, **1,466 assertions passed**. A separate reconstruction
of every descriptive grid cell passed **120 assertions**, reproducing all
24 cells and their 48,409 retained pixels. These are existing-image arithmetic
checks; no candidate colors or statistics were calculated.

The 18 primary rectangles total **21,856 pixels** and have no intersection
with the ten declared source/native foreground envelopes. Direct image/source
inspection supports their intended separation from buttons, title, caption,
rules and border accents. This is sufficient for the stated local image
screens, not proof that every original pixel represents isolated physical
roughness. The seven near-title/edge/widget-shadow witnesses remain descriptive.

All **103 original before outcomes** reproduce: **44 pass, 59 fail**. The
90 per-patch inequalities constrain encoded brightness, three channel means
and plane-residual variation; eight slopes and three lateral differences
constrain directional illumination. The two equal-patch-weight aggregate gates
prevent a few large/easy regions from hiding poor small regions. The exact
mean-error baseline is `846310429693/228096000000`, with unchanged half-error
maximum `846310429693/456192000000`. The RMS gate reproduces the report using
the proposed explicit `math.fsum` rule above.

These are meaningful pre-candidate engineering screens with a feasible
statistical target: the reference observations satisfy all their own errors
at zero. This does not predict that the fixed H1 field will pass. Full-frame
rejection for seams, grain, color or reduced child contrast remains binding.

## Literal field, bounded mechanics and state

The Markdown table exactly matches all **144 channel literals** in the report:
12 increasing x knots and four increasing y knots. Half-open interval selection,
final-endpoint handling, x-then-y bilinear evaluation, explicit volatile
binary64 barriers and half-away-from-zero `std::round` specify a reproducible
first field. The 258 boundaries partition 257 spans; the final boundary agrees
with the old gradient endpoint. One-pixel spans use points and wider spans end
at `end-1`. Complete-inset sampling makes clipping a restriction of operations,
not a new field normalization.

Independent coordinate-only enumeration of seed `0xB3A02211` and wrapping
uint32 mixer gives **16,384 ordered marks**, **15,438 distinct origins**, and
inclusive origin bounds x78–1593/y16–105. The ordered `(x,y)` uint16 little-endian
stream hash is `afd3639f16f5ae4ce396ea0a91d7bb4192cb0c7cc6139daa2ee0eb45a1f6a0e6`.
This verifies geometry/order only; no field or grain RGB was evaluated. Bright
then dark order, collisions without retries, amplitude `9−4v` and restored-scale
one-unit squares are explicit. There are exactly 32,768 mixer invocations.

The admitted finite logical domain implies inset height below 819. Renderer
components at most two therefore fit the conservative **1,638-row** ceiling;
clipping can only reduce it. Independent binary32 mapping at 8192²/scale2
reproduces inset y121.87884521484375, height818.3294067382812 and rows
`[244,1880)`, or 1,636 rows. The declared ceilings follow:

| Geometry | Maximum new primitives |
| --- | ---: |
| Canonical, 94 visible rows | 40,542 |
| 64 visible resource rows | 32,832 |
| Conservative 1,638-row bound | 437,350 |

Fixed arrays/knots and scalars suffice. These are application-level work/storage
bounds; SDL command allocations and actual timing remain separate gates.

The inspected reusable guards are consistent with the contract: color guard
outside scale guard; physical viewport/clip queries at scale one; int64
intersection; clip before integer narrowing; both scales restored before
grain; viewport, clip and blend never reconstructed or reset by H1. A
header-only eligibility guard can retain the exact Original path for invalid,
nonpositive or greater-than-two scales without adding queries to Upper/Lower
or other Original calls. This is a proposed implementation boundary, not an
executed invalid-scale/failure-path result.

## Exact support and the 48-case matrix

Read `Drawing::gradient`, `Drawing::rect`, reference endpoint/inset mapping and
SDL 2.32.10 software fill conversion directly. Source hashes were
`ae904d0fd11c6122c77d78909538b26694b4d57a9b6b722c51e0417d4709be54`
for `SDL_render.c` and
`2e3bbc7ab7d6d59310c634d6374eabb60da185d8c7cfc8526baa45318e6d3257`
for `SDL_render_sw.c`.

Independent geometry-only construction used assignment-rounded binary32
mapped panel/inset values, shared center-based field boundaries, both old and
new grain operations, and actual viewport/output/clip intersections. It used
no candidate image, difference mask, arbitrary dilation or color evaluation.
At canonical case46 it reproduces exactly **`[76,1596)×[14,108)`**, or
**142,880 allowed and 1,430,472 protected output pixels**. The old grain has
1,717 pairs at every constructed active matrix geometry.

All **48 declared cases** can be constructed from their fixed geometry and
state choices. Their main outputs contain 131,641,918 pixels in total; the
largest ordinary output is 3866×2194, or 8,482,004 pixels. Paired streaming
comparison is therefore practical without keeping the whole matrix resident.
Clipped companions and repeats remain additional required observations.

There are **13 empty-allowance cases**: 27–29, 33–34 and 36–43. They require
whole-frame equality. The twelve edge clips retain nonzero support, from
188 through 6,705 pixels. Resource cases30–32 each have exactly 4,096 allowed
pixels and **zero exterior**; their bounds/state observations cannot be
credited as exterior containment. Positive/negative origins, unequal scales,
fractional dimensions, logical/physical clips, NONE blend, threshold-adjacent
inactive layouts, fallback and state/repeat/fresh-renderer cases remain useful
independent failure modes.

## Live children and implementation prerequisites

The current source diff from accepted T2 changes only the five rejected T3
title passes. UpperRack, LowerRack, Original, panel shadows/rounding/accents,
control calls, rules, caption and model geometry remain unchanged. H1 permits
only an additional private selector/helper and the header call's interior
selection. The future source review must establish that exact restriction.

All ten header controls remain real `UiModel` geometry painted by the existing
button primitives. Their opaque inner surfaces and cyan focus, the two opaque
rules, and independently derived T3/caption opaque cores can be checked without
requiring antialiased edges over a changed field to match. Fully visible cases
supply nonempty control/glyph coverage; cut, empty, inactive and resource
observations must explicitly identify absent probes rather than credit
invisible children. Exact complete snapshots and hit/layout records remain
required. Source review also protects every child argument and call order.

The [original T3 rejection](../development/2026-11-16-heading-title-continuation/reports/t3-v1-rejection.json)
remains binding: current painter
`40de44893f3b88fef04732bf5a7607d4ce7db3cd4206f3712a5b71fa070a9029` is not an
accepted H1 baseline. H1 must wait for an independently admitted T3 revision
to pass its unchanged gates, then for genuine immediately-before source/app/
fixture binaries and exact equality of all 18 primary RGB patches to T2.

Next owners, in order:

1. Root retains both protocol versions and the clarification receipt, completes
   separate T3 acceptance and freezes the genuine pre-H1 inputs.
2. Independent fixture and checker owners freeze the 48-case transport,
   state/child/support oracles and helper-color probe, and demonstrate the
   genuine baseline without a candidate switch.
3. Only then assign the bounded painter. Root owns coherent builds, affected
   existing gates, timing and original failure retention; a separate reviewer
   owns actual whole-header/full-frame visual admission.

No source/test/CMake edit or execution, build, native run, capture, commit or
push was performed here. H1 native comparisons, failure/fallback execution,
child/state tests, timing, candidate statistics, visual admission and platform
qualification are unrun. The protected musical identities and nominal dry
Engine remain binding. Literal whole-interface **1:1 remains unmet and unwaived**.
