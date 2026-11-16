# Upper-rack material protocol admission

**A11, 15 November 2026: admit v1.1 for independent fixture/mask authoring.**
Painter work remains dependent on freezing and executing the supplemental
before harness. No candidate, runtime, display or whole-interface 1:1 pass is
claimed. Reviewed complete AGENTS/PLAN, session scope, A08's note and contract,
actual composition/children, `Drawing.cpp`, the 66-case harness and pinned SDL
2.32.10 source. Production/dependency hashes match A08's recorded inputs.

## Resolved documentary defect and identity

Proposed v1 SHA-256:
`cd742c7355cc0d1c47394497fa0c4caab2e9d6e20f19a463b6ed6e5533dea684`.
Admitted [v1.1 contract](../design/UPPER_RACK_MATERIAL_CONTRACT.md) SHA-256:
`baca5edb5878713291316751ad496e31513251c8bf8ce893605ede0496d00868`.

V1 left half-tie rounding unspecified. At reference column 32 and viewport row
388, `u=v=0.5`, `q=21.5`: C++ `std::round` gives RGB `(23,22,21)`, while
ties-to-even gives `(22,22,20)`. Root approved v1.1's explicit half-away rule
and separately rounded binary64 operations. Constants, support, seed, cases
and all tolerances are unchanged. No other blocking contradiction was found.

Portable implementation: keep contraction control private to the new helper.
For example, a small `round64(double x)` that stores `x` into a `volatile
double` local and returns that local can materialize each specified operation:
`lateral=round64(7.6*u)`, `vertical=round64(9.4*v)`,
`base=round64(22.4+lateral)`, `q=round64(base-vertical)`. Apply the same boundary
at other multiplication/addition joins in field/column calculations. One store
after an already fused expression is insufficient. Do not change global
compiler flags or existing Drawing behavior. Use `std::round` for channel
conversion; uint32 hash products wrap explicitly.

## Independent arithmetic and matrix checks

Binary32 enumeration covers every represented active size/scale combination.
Every old/new grain rectangle lies inside its intrinsic gradient rectangle;
the original canonical grain has 1,530 pairs. Center-based double gradient
endpoints and separately truncated SDL float origins/extents agree with the
actual implementations. Canonical intrinsic coverage is `[76,596)×[273,504)`;
the one-device-pixel expansion has exactly 121,626 pixels. Intersect only after
expansion with physical viewport, clip and output. Never learn this mask from
pixels or substitute the old percussion/composition masks.

The 66 original cases contain 38 active / 32 nonempty allowances: 28 inactive
and six clipped cases require whole-frame equality. The supplemental 30 have
27 nonempty allowances; IDs 21–23 require whole-frame equality. Edge IDs 9–20
cover each edge at all three scales. IDs 24–26 each expose 4,096 output pixels;
they qualify bounded-output maximum geometry, not a full maximum-size display.
IDs 27–29 provide the unobscured origin/scale-one numerical cases. Compare
metadata to the declared cases and run all clip companions and case-28 repeats.

The hash produces 4,096 marks at 4,041 unique origins, spanning x78–593 and
y275–501. Ordered little-endian uint16 `(x,y)` pairs hash to
`827dab5c1773d437058ea21cb69fb63fc2241ae10b342a649efbc559b1db90eb`.
Nonempty rendering uses 8,192 mixes and at most `65*R+4096` primitives; empty
intersection may skip them as expressly allowed. At 8192×8192/scale 2 the
intrinsic row count is 4,022; the resource cases expose only 64 rows. This is
an application-work bound, not an SDL-allocation/deadline guarantee.

## State, children and acceptance handoff

SDL stores viewport/clip in physical doubles; scale setters leave them intact,
while getters and queue conversion floor. Save both scale components and query
physical bounds at scale one; never reset clips/viewports through rounded
logical getters. End the field guard before grain's `Drawing::rect` calls so
grain uses the incoming scale. Preserve enabled-empty clips, blend mode and
helper draw color on every exit; compare physical and logical observations.

Source inspection confirms the declared eroded well/cap probes remain within
opaque child paint at levels 0/4/8, including minimum size. Preserve operations,
font/art identities, geometry and state; compare opaque probes and actual focus
positions exactly. Independent literal glyph rendering must retain all strong
ink, using the existing contrast method, rather than testing one nonempty pixel.

Independently decoded reference/native RGB with Pillow 13.0.0, JPEG API 6.2 /
libjpeg-turbo 3.2.0; exact rational sums/SSE reproduce every A08 statistic and
both decoded hashes. All five original baseline screens still fail. Keep mean
±2.0, RMS ±0.4 and lateral ±1.5 screens unchanged, retaining each inequality.
Reject grain periodicity, seams, banding, sparkle or worse text/focus contrast
on complete reference/minimum-active captures even if patch metrics pass.

Next: independent fixture and mask source freeze, genuine supplemental before
build/run by root, then private Upper-only painter, coherent affected suites,
paired comparison and independent actual-application capture admission. This
review used source inspection and in-memory arithmetic only; no builds or
candidate pixels were produced. Physical fidelity and literal 1:1 remain open.
