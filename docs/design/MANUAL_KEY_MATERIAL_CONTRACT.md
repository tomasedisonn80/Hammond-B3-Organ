# Idle manual key materials — candidate contract v1

**A08, runtime/interface continuation, 16 November 2026. Status: frozen candidate
for independent contract/fixture review; no painter implementation or visual
acceptance is claimed.** The independent review must admit the recipe, reference
windows and comparison protocol before code changes. Literal whole-interface
**1:1 remains unmet and unwaived**.

## 1. Boundary and source identity

Refine the ivory and ebony **top and front faces of idle playing keys on the two
manuals**, only in existing wide Dimensional Play. Keep the current activation:
Play, Dimensional, logical width 1400–8192 and height 820–8192. Within that path,
the new branch requires `manual && !held`. A focused but unheld key receives the
new material under its unchanged opaque cyan cue. Held keys and the `manual=false`
pedal calls take the complete old paint path, including old material colors.

This is finish, lighting and bevel paint on the existing `UiKeyGeometry::top` and
`front`, not a geometry revision. `hit`, `bounds`, all shared vertices, perspective,
front-depth clamp, pitch order and accidental ordering remain byte-identical.
Naturals still paint before accidentals; hit testing still prioritizes accidentals.
Do not modify `UiModel`, `Drawing`, typography, manual/rack panels, rims, wood,
presets, pedals, cabinet, controls, help/modals, compact/Flat or inactive workspaces.
There are still 61+61+25 playing keys, 24 presets and 68 controls including presets.
No sound/state/event/parameter change, new asset, shader, dependency or texture
upload belongs to this contract.

| Input | Identity and role |
| --- | --- |
| Original [cover/page-409 JPEG](atlas-cover-reference.jpg) | SHA-256 `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187`; unchanged 1672×941 design concept, not measured plastic or calibrated geometry |
| Historical [Lower-stage actual capture](../../examples/demos/lower-rack-material-v2/images/play-reference-1672x941.png) | SHA-256 `053dcd23028e865b3899d95ed10bb0172ec20929a67ad13559bca40e9fd1f74a`; executable `131b86779e52776ebab6ee73ec46341b7eeac7888f4df2d1b37cce62ad402da9`; material observations only |
| Initial session base | `3520c96adcdcf4ce4bcb860082354bf0050a89c3`; genuine root-owned app/source retained in `../baseline` |
| Contract-stage source | Root integrated `79bf34091dda5dc0528cf584891cff3e09657c66`, which changes footage typography and portable tests. `reference_key` is unchanged. Current painter SHA-256 at this inspection: `a88e7576700ae306769849ceda36993969a61e848c015ba4fb98fa9c4a7e8cfa` |
| Shared geometry/raster | `UiModel.cpp`: `0ecb0c4ee90d98cdb87c6f06b4685d368a7c12b72f9ea66e6c40228a4a855ecd`; `UiModel.h`: `6d8c0b16ddb6f3059dc14aff41bfc615e37b43c53b2f6e88cc199255a6b674b1`; `Drawing.cpp`: `9b788234405964f6675ab43428735e425b460c8045f2c6eb064c9e19b40a0a5f` |

The [current typography capture](../../examples/demos/footage-typography-v1/images/play-reference-1672x941.png)
belongs to that separate source transition. Do **not** compare a new key candidate
against the pre-typography full frame and permit typography changes in the key mask.
Root must first compile the reviewed new fixture against the genuine complete
before source at 79bf340 (or a separately recorded reconciled before tree), preserve
its executable/source hashes, and run the same fixture source against the candidate.
The old baseline bytes and historical observations remain intact.

## 2. Pre-candidate observations and frozen material windows

A08 inspected both complete images and unresampled manual crops. The source has
a darker, gentler within-front ivory ramp and ebony that brightens toward its
shoulder before a dark front. The current painter already has gradients, outlines,
rear shadows, side highlights and a glint; this work refines those distributions.
In particular, the current ebony inset runs from RGB `(61,58,52)` at the rear to
`(20,22,19)` at the front, opposite to the sampled reference trend.

The [observation script](../development/2026-11-16-runtime-continuation/reports/A08-manual-reference-measurements.py)
and [frozen report](../development/2026-11-16-runtime-continuation/reports/A08-manual-reference-measurements.json)
retain **72 fixed source rectangles in 24 groups**, exact RGB sums, exact rational
Y′ means, decoded pixel identities and historical gallery observations. There is
no candidate input. Run with Python/Pillow using the script's recorded input
hashes; no build or app execution is performed. Y′ means
`(2126 R + 7152 G + 722 B)/10000` on encoded 8-bit channels, not physical luminance.

Each group pools three equal-sized quiet rectangles. All bounds are half-open and
source pixels are decoded directly, without scaling, threshold masking, fitted
registration or gain. Ivory x starts are **544, 566, 599**, each width 6. Ebony x
starts are **529, 585, 620** for Upper and **529, 584, 622** for Lower, each width 5.
These narrow strips avoid seams and accidental occlusion; shoulder strips are
separate intentionally bright witnesses rather than quiet-body samples.

| Material band | Upper source y interval | Lower source y interval |
| --- | --- | --- |
| Ivory top: back / middle / nose | [562,568) / [607,613) / [651,657) | [736,742) / [781,787) / [825,831) |
| Ivory shoulder | [666,669) | [840,843) |
| Ivory front: high / low | [674,679) / [682,687) | [848,853) / [856,861) |
| Ebony top: back / middle / nose | [557,562) / [575,580) / [595,600) | [730,735) / [748,753) / [768,773) |
| Ebony shoulder | [603,605) | [776,778) |
| Ebony front: high / low | [609,614) / [617,622) | [782,787) / [790,795) |

The source's visually selected face y extents, used only to register material
coordinates, are ivory top Upper [548,670], Lower [718,844]; ivory front [670,690]
and [844,864]; ebony top [548,606] and [718,779]; ebony front [606,625] and [779,798].
They are neither a replacement layout nor a claim that the concept's incorrect
key count is authoritative. Each source y band maps to local
`v=(y-face_top)/(face_bottom-face_top)`. Actual-app samples use those same v bounds,
local width `u in [0.35,0.65)`, and pixel centers in the **unchanged actual quads**.
Use natural key indices **12,29,48** and accidental indices **13,30,49** on each
manual, all idle and unfocused in the canonical appearance fixture. The independent
checker must verify the snapshots and geometry before sampling.

| Y′ observation | Upper source / historical app | Lower source / historical app |
| --- | ---: | ---: |
| Ivory back | 211.400 / 216.156 | 190.605 / 217.418 |
| Ivory middle | 233.226 / 228.493 | 229.366 / 229.164 |
| Ivory nose | 241.781 / 240.354 | 235.406 / 240.360 |
| Ivory front high | 118.166 / 147.953 | 107.340 / 148.000 |
| Ivory front low | 107.519 / 120.469 | 93.728 / 120.298 |
| Ebony back | 19.042 / 51.124 | 17.215 / 49.800 |
| Ebony middle | 51.903 / 39.326 | 51.925 / 38.727 |
| Ebony nose | 63.970 / 26.184 | 63.499 / 25.903 |
| Ebony front high | 9.240 / 30.679 | 9.901 / 31.360 |
| Ebony front low | 10.366 / 17.947 | 10.196 / 18.606 |

Historical app columns average the three independently located live-key means.
The new fixture's genuine before pixels own grading, not these historical columns.
The JSON's exact sufficient statistics own source values. Record shoulder RGB/Y′
and all individual-key observations even where they are descriptive, not gates.

## 3. Chosen bounded painter recipe

These are artistic constants based on the source trends, **not measured material
reflectance or a recovered lighting model**. They define one candidate that can be
reviewed and implemented directly. A later change in recipe or criteria needs a
versioned amendment retaining this version and any failed candidate observations.

For every existing horizontal-edge quad Q, let v run rear-to-front (top-to-bottom
on a front face). For adjacent color stops `(v_i,C_i)` and `(v_j,C_j)`, draw
`quad_band(Q,v_i,v_j,0)` with opaque endpoint RGB colors. Within that band,

```text
t = clamp((v-v_i)/(v_j-v_i), 0, 1)
C(v) = round(C_i + (C_j-C_i)*t), per channel
```

Use the existing `quad_band` binary32 geometry and existing `Drawing::quad`
pixel-center interpolation/rounding. Adjacent bands share the same stored v edge;
there is no image resampling, row-count-dependent reparameterization or new raster
API. Skip invalid/degenerate derived quads through the existing validators.

### Ivory

Paint the full existing `top` with the following four bands. The earlier broad
rear shadow is included in the first band; **do not also apply the old recess
overlay**. The last narrow band supplies the rounded shoulder.

| v | Upper RGB | Lower RGB |
| ---: | --- | --- |
| 0.00 | (181,157,130) | (135,110,82) |
| 0.18 | (239,218,191) | (227,203,175) |
| 0.55 | (250,235,214) | (248,231,209) |
| 0.97 | (253,242,224) | (251,235,215) |
| 1.00 | (255,248,232) | (254,245,227) |

Paint the full existing `front` with two bands:

| v | Upper RGB | Lower RGB |
| ---: | --- | --- |
| 0.00 | (174,139,100) | (165,126,87) |
| 0.16 | (151,115,79) | (145,107,73) |
| 1.00 | (130,97,66) | (111,81,56) |

Keep the original `(83,65,42)` hit outline, thickness `0.7`, with its existing
scaled geometry. Remove the old ivory front highlight overlay in the new branch;
otherwise it would put the old bright ramp over the new front body. Keep the
existing `reference_idle_key_side` shapes unchanged. Its left RGBA endpoints become
`(255,245,219,38)` to `(255,245,219,12)`; its right endpoints become
`(36,26,17,22)` to `(36,26,17,8)`. These quieter edge highlights/shadows prevent the
repeated rails from overwhelming the broad face. There is no added cast shadow
outside the key or across a neighboring key.

### Ebony

Keep the same base/inset/front/outline/glint ordering and existing shapes. Paint
the full top base from `(18,18,17)` to `(11,12,11)`. On the existing
`reference_inset_quad(key.top,1.4,scale)`, use three bands:

| local inset v | RGB, both manuals |
| ---: | --- |
| 0.00 | (13,14,15) |
| 0.20 | (21,21,22) |
| 0.52 | (54,52,53) |
| 1.00 | (68,64,65) |

Paint `front` from `(15,13,11)` to `(8,8,7)`. Keep the original opaque
`(5,6,5)` hit outline and `0.8` thickness. Keep the inset-top outline's shape,
inset `1.2` and thickness `0.65`, but use `(96,94,91,65)` instead of the earlier
strong warm border. Keep the existing front-glint band `v in [0,0.12]`, side inset
`scale.sx`. Its Upper RGBA endpoints are `(176,172,167,200)` to
`(176,172,167,20)`; its Lower endpoints are `(155,151,147,180)` to
`(155,151,147,15)`. The glint remains thin and the rest of the front remains dark.
This slice does not claim to reproduce the source's every curved highlight.

### Preserved state cues and finite work

After material paint, retain the exact old held-band and focus-outline operations,
arguments and ordering. `kUiBrass`, `kUiFocusCyan`, their widths, offsets and opacity
do not change. The held branch is fully old paint, not new paint tinted afterward.
Do not make rendering mutate key owners, focus, saved controls or SDL/audio state.

At most **24 `Drawing::quad` calls per manual key**, including four possible focus
outline quads, is a conservative bound: this recipe uses fewer. Thus the two
manuals emit at most **2928** such calls. Each primitive uses the already clipped
quad row loop; work is bounded by `24 * sum(visible device rows of each key)` span
attempts, with fixed scalar/quad storage. At logical H≤8192 and renderer ry≤2,
the longest key is the Lower natural: canonical height 144, giving a conservative
**2510 device rows per key** and **7,349,280** span attempts for this loose bound.
This is a source work ceiling, not a frame deadline or a claim about SDL internals.
No per-pixel new material loop, allocation, random state, clock, texture generation,
cache or unbounded refinement is allowed.

Use existing Drawing operations. Do not change renderer scale, viewport, physical
clip storage, clip-enabled state, blend mode or texture modulation. The existing
quad helper temporarily uses scale one and restores scale. If an implementation
introduces a raw-renderer helper, it must save/restore every borrowed state on every
return, including draw color; that addition requires review. Paired complete-paint
fixtures must observe identical outgoing draw color and renderer state, not merely
assume preservation because the images look alike.

## 4. Independent actual-support and cue protection

The checker owns its mask and independently reconstructs the unchanged geometry
and paint ordering from the **before source**. It may consume emitted geometry to
check agreement, but not use candidate-generated allowances or changed pixels to
define support. At a key face with top y0 and bottom y1, row center y has
`v=(y-y0)/(y1-y0)`. Interpolate the original left/right side edges at that v.
For incoming positive renderer scale rx, ry and physical viewport origin ox, oy,
the quad's viewport-relative row and span bounds are:

```text
row_begin = ceil(y0*ry - 0.5)
row_end   = ceil(y1*ry - 0.5)
logical_y = (row+0.5)/ry
span_begin = ceil(left(logical_y)*rx - 0.5)
span_end   = ceil(right(logical_y)*rx - 0.5)
```

Use binary32 source vertices promoted to binary64, the existing half-open raster
rule, and independently reproduced `quad_band`/inset/outline vertices. Translate
by the actual physical viewport origin; intersect with output, viewport and the
enabled physical clip. Do not round-trip physical clips through logical getters.

Intrinsic editable support is the union of **top/front quad raster coverage of
idle manual keys**. Subtract later opaque coverage of held keys and visible focus
ink, respecting natural-first/accidental-last order. This subtraction matters:
an idle black key may legitimately change over the otherwise held natural's hit
quad, while the exposed held natural must be identical. The original hit-outline
operations, colors and geometry remain unchanged and are source-reviewed. Exact
pixel equality applies to the final visible unchanged opaque outline ink: begin
with independently reconstructed hit-outline coverage, subtract later intentionally
editable material overlays of that key (the old ivory front highlight, rear recess
and idle side bands; the ebony inset outline and front glint), then apply later key
occlusion in the original natural-first/accidental-last order. These pre-candidate
source-defined subtractions are necessary because the old ivory recess already
alpha-blends over its top hit outline, while the recipe explicitly removes that
recess. They grant no area beyond the original idle top/front faces. Held-key-owned
pixels and the final visible opaque cyan/brass cues remain exactly protected. All
new paint remains within the original faces. **No dilation, rectangular keyboard
allowance, title/rim allowance or image-derived exception is permitted.** This
source-order clarification was independently raised by A11 and admitted by root
before any candidate painter existed; A08's original delivery and observations
remain recorded in its note.

Require zero changed RGBA channels outside this support in every pair. Additionally
require pixel equality on each visible held-key-owned region, the complete pedal
and preset regions, and the independent visible focus/held-cue masks. Compare the
complete frame's cyan-pixel set and exact cue pixels before/after; do not merely
count enough cyan pixels. Equal geometry and snapshots are separate prerequisites.
For inactive composition, Flat, all-manual-held or empty-support clips, require
**whole-frame equality**. Full-frame protected pixels must be nonzero and counted;
a crop containing only keys cannot qualify exterior containment.

For each pair retain input/build/executable/source/state/geometry hashes, dimensions,
renderer identity, physical viewport/clip/scale, intrinsic support and protected
pixel counts, changed pixel/channel counts, maximum delta, bounding box and
per-row changes. Retain lossless before/after/difference on failure. Never enlarge
the mask or loosen a limit because the candidate fails.

## 5. Exactly sixteen representative paired cases

The fixture freezes these cases before painter changes. All use fixed snapshots,
no runtime clock/meter drift and the same source fixture linked once to genuine
before paint and once to candidate paint. Unstated keys are idle and no modal is
open. All four banks, presets, state fields and geometry remain equal between each
pair. Origin is physical; renderer scale is separate from layout scale.

| # | Logical size; renderer scale; origin | State / purpose |
| ---: | --- | --- |
| 01 | 1672×941; (1,1); (0,0) | Canonical all idle, focus on a non-key control; source appearance screens |
| 02 | 1400×820; (1,1); (0,0) | Minimum active, all idle; same local trend signs and full-frame inspection |
| 03 | 1920×820; (1,1); (13,17) | Unequal-aspect layout, all idle |
| 04 | 1672×941; (1.5,2); (13,17) | Anisotropic renderer, all idle; full-clip companion for 11/12 |
| 05 | 1672×941; (1,1); (0,0) | Hold Upper 12/13 and Lower 48/49, hold a natural and accidental pedal; focus Upper 13; verify exposed held faces/cues and pedal equality |
| 06 | 1672×941; (1,1); (0,0) | Idle Upper natural 12 focused |
| 07 | 1672×941; (1,1); (0,0) | Idle Upper accidental 13 focused |
| 08 | 1400×820; (1,1); (0,0) | Idle Lower natural 48 focused |
| 09 | 1400×820; (1.5,1.5); (13,17) | Idle Lower accidental 49 focused |
| 10 | 1672×941; (1,1); (0,0) | All 122 manual keys held, Lower 48 focused; complete frame must be identical |
| 11 | As 04 | Physical clip corresponding to canonical [500,810)×[580,860), crossing key slopes, both manuals and front splits |
| 12 | As 04 | Enabled empty physical clip; empty material support and whole-frame equality |
| 13 | 1399×819; (1,1); (0,0) | Compact Dimensional Play; complete frame identical |
| 14 | 1672×941; (1,1); (0,0) | Flat Play; complete frame identical |
| 15 | 1672×941; (1,1); (0,0) | Rotary workspace; complete frame identical |
| 16 | 1672×941; (1,1); (0,0) | Service workspace; complete frame identical |

The independent fixture spells out exact physical integer clip coordinates and
all nonmaterial snapshot values before compiling the before executable. Case 11
visible pixels must equal its full-clip companion at the same physical positions;
no clip-local relighting is allowed. Record unchanged incoming/outgoing scale,
viewport, physical/logical clip observations, clip-enabled state and blend mode;
outgoing color must equal the before execution. The source proof covers valid
maximum geometry; this contract does not add a giant raster campaign.

## 6. Separate local appearance and complete-frame admission

These are limited material screens, not a pixel-perfect score or whole-interface
similarity percentage. Evaluate **each manual and each of its three representative
keys separately** in case 01. Let R be the fixed source group's exact Y′ mean, B
the genuine before fixture mean and C the candidate mean. No test may pool Upper
and Lower or hide a failed key in a keyboard-wide average.

1. **Ivory front body:** the sum of absolute source errors for `front_high` and
   `front_low` must be at most half its before value. The candidate high-minus-low
   Y′ must stay positive, and its distance from the source high-minus-low contrast
   must be at most half the before contrast error. This targets the too-bright,
   steep existing front ramp rather than just darkening every pixel.
2. **Ebony sheen:** the sum of absolute errors over back/middle/nose must be at most
   half its before value. Require `back < middle < nose` and the nose-minus-back
   contrast error at most half its before error. Both front-body Y′ means must be
   ≤25 and neither front-body source error may increase. This directly rejects the
   current reverse-direction sheen and an accidentally gray front.
3. **Ivory top protection:** at back/middle/nose, each source error may be no more
   than its before error plus **4 encoded Y′ levels**. This is a predeclared small
   quantization/art-direction allowance, not a measured uncertainty. Require
   back < middle ≤ nose. The Lower rear shadow may be deeper than Upper as in the
   source. Record all RGB means, not only Y′, to expose undesirable hue shifts.
4. **Bevel and shoulder:** retain shoulder means and top/front contrast statistics
   for both materials. Visually inspect the source, before and candidate at native
   size and a nearest-neighbor detail view. The rounded ivory shoulder must remain
   narrow, ebony glint must stay on the front edge, and no new repeated bright
   rails, detached shadows, doubled borders, gaps, stair-step discontinuities or
   ambiguous held/focus cues are admitted. This is an independent visual decision;
   this version does not pretend to measure the source's exact curved highlights.

For case 02 require the same ordering signs, ebony front limit, unchanged geometry
and exact cue/exterior gates; record the complete metric set without adding new
cross-size error tolerances after inspection. Inspect full frames 01–04 and 05–09,
plus the inactive before/after frames, directly. The independent reviewer must say
whether the chosen material change is visually useful at full window size and
identify residual differences; passing patch means alone is insufficient.

Finally capture the **running changed application**, at least canonical and
minimum active sizes with one visible held/focus example, against the original
reference. Bind images to executable/source/input/diagnostic/pixel identities and
update README's current screenshot through root. These actual captures are a
separate gallery from deterministic fixture pairs. Real display/DPI/input,
assistive semantics, physical authenticity, all other M0–M9 exits and literal
whole-interface 1:1 remain separate, open gates.

## 7. Handoff and admission status

A08 supplies the bounded recipe, original-image observations and proposed frozen
protocol. No candidate has been rendered, built, graded or accepted by A08. Next:
independent review admits or amends this version; root builds and retains the new
fixture against genuine before source; the assigned painter implements only the
admitted branch; independent before/after and visual review then decide acceptance.
Preserve old failures and exact-source evidence throughout the handoff.
