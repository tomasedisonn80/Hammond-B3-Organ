# Reference apron contract admission — A12

16 November 2026. **Design accepted in principle; protocol freeze is blocked by
the two concrete corrections below.** This is independent source/image review,
not executed asset, raster, native-display or whole-interface acceptance. Reviewed
[contract v1](../design/REFERENCE_APRON_CONTRACT.md) SHA-256
`400cb8d7c0027835699f3ccd1ad3ffec785f0319ea0a73703c79f8288aa58e35`.

## Source, mask and paint-order findings

Direct inspection of the [unchanged reference](../design/atlas-cover-reference.jpg)
places its central DESIGN CONCEPT lettering and both horizontal ornaments inside
F = `[48,1604) × [889,925)`. The proposed hole H is precisely F translated by
R's `(16,887)` origin. Its zeroed RGBA bytes remove the baked lettering from the
asset itself, including hidden RGB. No visible lettering was found in R minus F.
This visual finding is not an independently segmented glyph measurement.

An independent Pillow `load(); convert("RGB")` read reproduced the pinned source
size, JPEG hash and decoded RGB hash. Observed decoder: Pillow 13.0.0,
libjpeg API 6.2, libjpeg-turbo 3.2.0. Arithmetic agrees: 88,560 total texels,
56,016 zero texels, 32,544 retained source texels and 354,240 RGBA bytes.
No generated asset exists yet; its independent byte comparison remains required.

[InstrumentView.cpp](../../apps/standalone/InstrumentView.cpp),
`paint_reference_composition`, paints R after the full-background wood, cheek art
and dark parent, and before the live children. The manuals/cheeks end at canonical
y870, pedals at y862 and cabinet at y870; they do not intersect R. The later
`reference_footer` writes an opaque gradient across all of F before its live text,
meter and status. `overlay` follows it. Consequently the canonical exact-source
test over R minus F and baseline equality within F are appropriate. The contract
correctly keeps overlays and dynamic text outside the artwork.

[UiModel.h](../../apps/standalone/UiModel.h) confirms the active predicate and
float endpoint mapping. The proposed independent package, unchanged existing
three-art manifest/enum, prepared texture lifecycle, finite bounds rejection and
original-call fallback are appropriately narrow. Explicit nearest sampling is
necessary: the existing `make_art` helper in
[Drawing.cpp](../../apps/standalone/Drawing.cpp) uses RGB24, blend NONE and linear
sampling, so it cannot be reused unchanged for this RGBA asset.

## Required surgical corrections

1. **Expose the promised alpha/backdrop behavior.** All 25 whole-instrument cases
   paint the opaque footer over H. Therefore a texture that incorrectly ignores
   alpha can still pass their footer comparison. Add a bounded, candidate-only
   direct `Drawing::apron_art` verification before painting any footer, on two
   fixed contrasting opaque backdrops. At canonical mapping require every H pixel
   to retain its backdrop, every other texel to equal the source, and renderer
   state to remain unchanged. Bind it to the same candidate executable/source
   and asset identities; it is not a 26th paired whole-UI case or a substitute
   for the genuine baseline. Independently inspect the actual texture setup for
   RGBA32, blend BLEND, identity modulation and explicit Nearest. This closes a
   specific observability gap in already-required behavior.

2. **Make the lower-edge clip case nonvacuous.** R's bottom equals the logical
   layout bottom, y941. A viewport ending there provides no protected pixels
   below R after viewport intersection; increasing output alone does not help.
   Freeze case 9 and its 10–15 companions with a viewport and output extending
   at least two physical pixels beyond the transformed apron bottom, while
   retaining logical 1672×941 and physical origin `(13,17)`. Freeze all exact
   physical strip rectangles and report nonzero visible apron/interior and
   protected exterior populations for the four edge strips. Set/query physical
   viewport and clip at scale one, then restore the declared scale. This adds no
   cases and preserves the existing floor/ceil containment boundary and zero
   halo allowance.

## Baseline and implementation handoff

The 25-case selection otherwise covers the stated sizes, aspect changes,
fractional/unequal scales, live footer conditions, overlay and inactive branches.
The half-open transformed envelope, footer-center protection, empty/disjoint
whole-frame equality and separately reported clipped/full sample differences
are sound. Nearest sampling must remain SDL's configured behavior; do not invent
a custom resampling oracle or relax exact canonical equality after failures.

The current [baseline receipt](../development/2026-11-16-preset-library-continuation/reports/baseline-qualification.json)
names standalone, render and paint-benchmark binaries. It does **not** yet retain
the new 25-case fixture executable. Independently freeze the complete fixture,
manifest, deterministic state and portable transport before root builds it
against the unchanged current production painter. Retain that actual executable
and its inputs; use identical fixture bytes for candidate pairs. A reconstructed
old painter, existing gallery or forced fallback cannot supply this baseline.

After the two corrections are frozen, implementation can proceed only after that
baseline retention. Forced-decoration failure, state restoration, repetition,
asset/compiler rejection, all paired pixels and three genuine application
captures remain unexecuted requirements. Dummy-SDL results must retain their
label; real display/DPI/input/accessibility and literal whole-interface 1:1 stay
open. No additional numerical, audio or physical gate is introduced here.
