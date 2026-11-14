# A08 - Shared dimensional geometry and reference review

Actual agent: `/root/w02_a08_geometry_contract`, assignment 08, wave 2.
Starting inspected source: `d493e998e5dd7cf44db46854e87309745063ac54`.
Owned outputs are this note and
[`INTERFACE_GEOMETRY_CONTRACT.md`](../../INTERFACE_GEOMETRY_CONTRACT.md).

## Work actually performed

Read the repository's `AGENTS.md`, this continuation's scope, inherited current
plan/status/next-step context and the relevant complete atlas-reading findings
from A05/A06. Inspected `UiModel.h`, key/preset generation, layout formulas,
validation, hit precedence, `Drawing` primitives, `InstrumentView::paint_key`,
and the independent native/model geometry fixtures. Visually inspected both
the unchanged 1672 x 941 source reference and the current published preset
application capture with the image viewer. No application run, source build or
test execution occurred in this assignment.

Verified image SHA-256 values:
source reference `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187`;
published capture `1e668a4191b3a189969c8e17213611d6ffe7ead64f20f423d115a3e2effae1c7`.

The current source has real rectangular key geometry and bounded front shading,
but its manuals have no shared perspective. The reference shows a narrower
back plane, sloping key boundaries and more visible key fronts. Merely drawing
trapezoids over rectangular input regions would create an observable paint/hit
disagreement. The contract therefore makes the same quad determine paint,
overlap, hit ownership and focus.

## Frozen proposal ready for integrator acceptance

- Append `UiQuad hit/top/front` to each `UiKeyGeometry`; preserve note identity,
  accidental flag and a diagnostic AABB. No sound parameter or saved-state
  field changes.
- Use a mild exact homography for each entire manual: back width 94% of the
  front, with all naturals/accidentals projected together. Flat mode has a
  unit projection and no key-front faces. Pedals use the same API with a
  rectangular plan and a dimensional front when requested.
- Use exact half-open horizontal-quad containment and existing black-first
  precedence. A sloped key's AABB corner is not an invisible playable region.
- Keep reversed preset geometry and the existing body rows stable for this
  bounded slice. The application still has 61 + 61 + 25 playing keys and 24
  separate preset keys.
- Add native quad fill and inside-outline primitives. Raster behavior must be
  checked under the actual SDL software renderer; unsupported geometry cannot
  silently become a rectangle.
- Keep reference artwork limited to existing decorative crops. All control
  legends, cap position, note indication and focus remain live rendering.

A07 and A08 coordinated exact enum/field names, the trailing compatible layout
arguments, visibility filtering and presentation semantics. A07 accepted the
`UiQuad hit/top/front` shape API and requires paired pointer release after a
view/presentation change. Root was notified that A14, A19 and A20 need sequential
primitive, layout and renderer integration and coordinated header ownership.

## Visual comparison and limits

The contract retains a source-versus-native landmark table. Reference positions
are clearly labeled approximate visual observations. Native row positions come
from the existing independent 1672 x 941 literal fixture. The proposed upper
manual back would span approximately x275.101..1097.398; its front stays at
x248.858..1123.642. That is visibly closer to the reference's fan perspective
without discarding the real keyboard inventory.

Literal 1:1 equality is still open. The reference has different panel heights,
manual depth, keyboard/preset inventory, cabinet controls and no separate live
pedal row. This task does not claim new pixels exist, does not rename source
art as a native screenshot, and does not equate visual matching with measured
instrument or physical audio fidelity. Native screen-reader semantics remain
a separate product gate.

## Next implementation and verification

A14 supplies the geometry type/drawing primitives, A19 builds and validates
the shared key surfaces/hit behavior, and A20 renders the materials and flat
fallback. Independent acceptance must use projection anchors, representative
sizes and responsive boundaries, all key IDs, half-open edge ownership,
outside-quad rejection, held-note continuity and actual raster/focus checks.
Existing fixture expectations should change only where this contract changes
behavior; an oracle must not call the production layout helper to construct
its expected result. Integrator acceptance and subsequent executed checks,
not this design note, establish implementation completion.

No code, data, dependency, build directory, shared status document, commit or
remote ref was changed. Only the two assigned Markdown files were created.
