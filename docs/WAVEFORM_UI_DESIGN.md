# Waveform continuation: drawbar and key-front refinement

Design identity: `waveform-live-materials-v1`; A09 proposal accepted by the
integrator, with actual changed-product qualification pending. This is a paint-only
amendment to [the material contract](REFERENCE_REFINEMENT_MATERIALS.md).
The [accepted layout](REFERENCE_REFINEMENT_LAYOUT.md), shared geometry and
musical meanings remain authoritative. No implementation or visual pass is
claimed by this document.

## Observed target and bounded ownership

A09 directly inspected the exact [cover/page-409 reference](design/atlas-cover-reference.jpg)
and the current 1672×941 native baseline. Their identities and reproducible
measurements are in [the assignment note](development/2026-11-14-waveform-continuation/notes/A09-visual-design.md).
The live renderer already includes the previous deeper layout, grain, ivory
gradients and recess bands; repeating that work would not narrow the remaining
gaps. The reference has dark, substantial drawbar stems with narrow reflections,
deeper cap fronts, and darker ivory key fronts.

Prioritize **drawbar recess/stem/cap separation**, followed by **idle natural-key
front shading**. Own only the Dimensional branches of `drawbar()` and
`paint_key()` in `apps/standalone/InstrumentView.cpp`. Existing `Drawing::rect`,
`gradient`, `line`, `rounded` and `quad` suffice; **no Drawing API or UiModel
change is required**. Keep new local helpers inside those ownership boundaries.

The preceding session's A40/A41 owns `paint_header()` typography and its
acceptance. [Its measured visual review](reviews/REFERENCE_REFINEMENT_VISUAL.md)
records the smaller/lower title and subtitle. Do not edit `paint_header()`,
`heading()`, fonts or their call sites here. Preserve current panel grain, wood,
cheek/cabinet crops, buttons, presets, status and footer paint. The source-backed
wood crops already supply the main walnut character; a new rail-texture pass
lacks a measured benefit sufficient to expand this slice.

## Exact paint changes

All distances are existing logical units; the renderer still owns output scale.
Use stationary lighting. Retain validation of finite positive surfaces, existing
paint order, label/value strings and final focus/held ink.

### 1. Drawbars: keep position and footprint, add readable depth

Retain the current `slot`, `knob`, `cap_width`, `cap_height` and
`y = track.y + track.height * value / 8` calculations exactly. Manual caps remain
26 units tall, pedal-mixture caps 22; their centers, clickable controls, track
endpoints, nine ticks and 0–8 direction do not move. Cap width and cap shadow
footprints remain unchanged. Apply the same material recipe to both manuals and
the two mixtures; retain brown/ivory/black identities.

Paint in this order, entirely inside the existing slot/cap allocations:

| Layer | Bounded implementation |
| --- | --- |
| Recess floor | Retain the rounded `(5,5,5)` slot. Add a left wall up to 3 units wide, `(47,43,36)→(22,21,18)`, and right wall up to 2 units wide, `(27,26,23)→(13,14,12)`, inset 1 unit from the slot sides. Stop both 1 unit before its bottom. Preserve the original outer edge lines. |
| Rear recess | Inside the slot, add a top band of height `min(6, slot.height/4)`, black alpha `135→0`. Draw it before ticks and the shaft. No rectangle extends across the adjacent panel or label. |
| Shaft body | Replace the current 3.5-unit strip with a centered `shaft_width = min(9, slot.width - 8)` strip, guarded positive. Paint the full track `(37,36,31)→(20,22,19)`; the exposed segment above the cap uses `(70,65,54)→(43,41,34)`. Bound exposed height to `max(0, knob.y - track.y)`; a value-0 cap hides the upper segment. This is illustration inside the unchanged track control, not a wider gesture or a new travel range. |
| Shaft edges | Within the exposed strip, paint one 1-unit warm reflection along its left edge, `(174,158,129)` at alpha 170, and one 1-unit dark right edge `(15,16,14)`. Preserve dark body between them. Below the cap the full-track strip remains subdued; it must not look like a second active extension. |
| Cap front | Change only the internal `front` thickness from `clamp(height*.18,3,5)` to **7 manual / 6 mixture** units. Keep the existing face calculation, cap palette, top highlight, front gradient, edge lines and shadow, so the extra depth comes out of the face inside the same knob. This moves the face/front join upward by 2.32 units for manual caps and 2.04 for mixtures. |

Paint the ticks after recess walls and before the shaft/cap. Retain their existing
positions and colors. Do not widen the bright reflection into a luminous bar,
add numbers to the shaft, reverse travel, or use an image of the reference rack.
No new work is proportional to time or audio; the additions are a fixed number
of primitives per visible drawbar.

### 2. Natural-key fronts: darken the front, preserve the top

In `paint_key()`'s non-Flat, non-accidental branch, replace only the **idle**
`key.front` gradient from `(215,190,148)→(164,132,89)` with
**`(198,168,124)→(131,96,62)`**. Keep the natural top gradient, rear recess,
front split, existing at-most-2-unit highlight and outline untouched. Keep held
palettes/marker, accidental paint, focus cyan and their ordering unchanged.

This shared branch also shades idle pedal fronts; retain their own supplied
quads and verify their shorter front at the minimum size. No side strip,
bounding-box shadow or enlarged silhouette is authorized. A later directional
key-edge pass needs its own seam and timing evidence.

## Before/after raster acceptance

These are digital appearance criteria, not physical reflectance or hardware
measurements. Use the actual executable at matched state, source, backend,
drawable size and scale. Retain lossless before/after PNGs and exact hashes;
freeze copied status when requiring pixel equality. Do not compare changing
audio counters as a deterministic raster oracle.

The baseline uses SDL 2.32.10 dummy video/audio, software rendering, MIDI OFF,
1672×941 logical/drawable pixels, Upper B `888000000`, Lower B `008000000`,
pedals `80`, and one held Upper key. For numeric samples use
`Y′ = .2126R + .7152G + .0722B` on encoded RGB, then median over the half-open
patch. This is a reproducible brightness statistic, not linear-light luminance.

| Check | Observed baseline | Required changed raster |
| --- | --- | --- |
| First Upper drawbar's exposed stem | At rows 350, 365 and 380, only 3 pixels in x `[103,119)` exceed `Y′=25`. | 7–10 pixels exceed 25 at each row, with a narrow brighter edge and darker body visibly separated from the recess. The cap center, label, ticks and value remain in place. |
| Manual ivory cap face/front join, Upper 8-foot cap at value 8 | Computed join y438.08; front thickness 4.68. | Join y435.76, raster within ±1 pixel; front thickness 7±1 pixels including its top edge. Mixture front thickness 6±1. No cap silhouette expansion or new overlap at values 0/4/8. |
| Idle upper natural-key front, x708–715 / y677–682 | Native median **159.06**; reference **119.48**. Other unobstructed source patches range 107.49–125.36. | Native median **125–140**: at least 19 levels darker, within 21 levels of this source patch. This closes part of the observed gap without changing the top. |
| Adjacent natural top, x708–715 / y653–658 | Native **240.82**; reference **242.40**. | Exact baseline pixels for this isolated slice; no overall ivory darkening. |
| Containment and unaffected paint | Geometry/crops supplied by the current product. | Fixed-state deltas only inside the existing drawbar slots/knobs and idle natural fronts. Header, wood, cabinet image, labels, values, presets and other pixels stay identical for this slice. |

The reference samples are local appearance anchors; different key counts and
register settings prevent a whole-image registration score from proving equality.
If A40 typography is integrated first, establish the before frame on that source
and compare this slice independently; do not weaken the containment rule by
silently treating unrelated header changes as material output.

Require actual Play captures at **1672×941, 1280×900 and 960×700**, plus minimum
Flat, held natural/accidental and focused key/cap states. Exercise manual and
mixture values 0, 4 and 8 with each cap family. At output scales **1, 1.25, 1.5
and 2**, inspect corners, inter-key seams, clipped/offset viewports and shortened
pedal fronts. No new pixel may cross the original `UiQuad` silhouette, drawing
clip or intended control allocation. All Flat pixels and hidden Play regions in
Rotary/Service remain unchanged in a fixed-state comparison.

Use the existing drawing, quad, workspace-raster, material-acceptance,
scaled-view and preset-raster gates, and existing geometry/ownership checks.
Add independent raster checks only for the new measurable targets; derive their
expected patch/half-plane bounds separately from production paint helpers.
Retain existing natural/accidental front-contrast minima (15/8), visible held
and focus tests, text contrast, value mapping and all previous rejection gates.
Do not relax an existing test to accept a newly exposed seam.

## UI timing and unchanged musical scope

Keep UI timing separate from R4 rendering, audio deadlines and physical devices.
On one identified renderer/build/machine, compare **30 warmup + 300 measured
draws**, excluding capture/file I/O, at the same reference geometry and state.
Record median/p95 for before and after. Investigate p95 growth exceeding **both
15% and 2 ms**; retain original samples and any repeat separately. The darker
key front adds no draw calls; the fixed drawbar additions still require observed
timing. No new assets, dependencies, font uploads, per-frame allocation or audio
thread work belongs to this slice.

Preserve minimum **960×700**, all layout breakpoints and maximum admission,
Flat, 68 control records including 24 presets, 147 playing keys, 71 Play/ten
common focus stops, all four banks, 47 parameters, state4/readers 1–3 and original
gesture/note owners. Resize, tab and skin changes retain their existing behavior.

## What still prevents literal 1:1 equality

This slice targets material gaps only. Correct full manuals/pedals and reversed
presets, the computer-key toolbar, actual tool/status inventory, truthful
nominal-dry caption and real register settings differ from the generated art.
Rack heights/positions, manual offsets, cap silhouettes, light falloff, key-edge
softness, panel grain and rail texture also remain visibly different. Header
qualification belongs to A40/A41; their success cannot close these other gaps.
The cabinet crop remains decorative and slightly smaller than its source area.

Do not add functioning scanner, rotary-speed, Stop/brake or microphone controls
to obtain a visual match. Their supported models and integration are separate
gates. Root should update README with fresh actual application captures only
after acceptance, stating both the measured improvement and residual differences.
Literal equality remains unmet until an actual complete comparison establishes it.
