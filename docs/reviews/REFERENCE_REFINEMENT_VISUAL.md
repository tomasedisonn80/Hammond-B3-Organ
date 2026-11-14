# Actual v3 interface against the original reference

## Finding and evidence

The deeper manuals and cabinet column now follow the reference's large-scale
composition closely. **Literal 1:1 equality remains unmet.** The clearest bounded
next improvement is the wide Dimensional header: its title is smaller and lower,
and its truthful nominal-dry subtitle occupies much less of the reference's
subtitle footprint. Key-edge lighting and deck texture remain larger material
differences. This review found no visible crop, overlapping content or false
connected-model label in the eight inspected views.

A36 directly inspected the unchanged [original cover/page-409 JPEG](../design/atlas-cover-reference.jpg)
and all eight original PNGs in the [v3 native gallery](../../examples/demos/standalone-interface-preview-v3/README.md).
The gallery identifies product commit `2e161dc3a60fc3442051799574feed37bffbfc5c`
and executable SHA-256 `97ed35cbf618792155c15106862d8bc5f416b7cf6d073c9e37e94babdf8bc9a9`.
The [measurement report](../development/2026-11-14-reference-refinement/reports/A36-reference-visual-review.json)
retains all nine image hashes/dimensions, decoded RGBA identities, selected source
identities, coordinates, masks and font-metric calculations. The inspected
InstrumentView, UiModel, Drawing and FontData bytes equal both the captured
qualification and published blobs.

These are digital composition measurements. The source image is a generated
concept, not calibrated hardware geometry. Visual inspection does not establish
input, accessibility, physical display/DPI, device, sound or deadline acceptance.
No image was edited, cropped, resampled or overwritten; A36 ran no app, GUI,
shared build or project test.

## Measured composition at 1672×941

Coordinates use the original images. Reference panel/key landmarks are visual
estimates with the uncertainty shown. Native values are the reviewed logical
allocations, cross-checked against the displayed original capture. Normalization
divides x by 1672 and y by 941; it is not an image registration or fidelity score.

| Landmark | Reference px | Native logical px | Reference normalized | Native normalized |
| --- | ---: | ---: | ---: | ---: |
| Cabinet panel left x | 1125 ±2 | 1124.831 | 0.672847 | 0.672746 |
| Upper key top y | 548 ±2 | 542.760 | 0.582359 | 0.576791 |
| Upper key bottom y | 692 ±2 | 686.880 | 0.735388 | 0.729947 |
| Lower key top y | 720 ±3 | 726.880 | 0.765143 | 0.772455 |
| Lower key bottom y | 867 ±3 | 871.000 | 0.921360 | 0.925611 |
| Drawbar rack top y | 267 ±2 | 240.920 | 0.283741 | 0.256026 |
| Drawbar rack bottom y | 509 ±2 | 472.760 | 0.540914 | 0.502402 |

The native upper key depth is 144.12 logical pixels against approximately 144
reference pixels; its position remains about five pixels higher. The lower
manual starts about seven pixels lower. The rack is visibly higher and shorter;
the working expression/mixtures and separate computer-key toolbar account for
part of this allocation. Changing it would reopen the accepted geometry budget.

The actual decorative cabinet source crop is exactly `(1132,174,466,397)` in
[its manifest](../../assets/standalone/reference/manifest.json). Native placement
is `(1132.831312,174,459.272688,391.268792)`: the same aspect at scale
`0.985564`, about 1.44% smaller, with unchanged source content. This is already a
close positional match; enlarging it would consume the explicit status/pedal
reserve in the [layout contract](../REFERENCE_REFINEMENT_LAYOUT.md).

### Header ink, measured without resampling

A fixed warm-light mask selects `R≥130`, `G≥105`, `R≥G`, `B≤0.9R` within named
regions. The rectangles below are half-open. The three native reference-sized
workspaces have identical title results. Subtitle strings differ, so their
footprints compare hierarchy and spacing, not glyph-by-glyph equality.

| Ink | Reference bbox / size | Native bbox / size |
| --- | --- | --- |
| Title | `[603,20,1067,53]` / 464×33 | `[617,28,1051,59]` / 434×31 |
| Subtitle | `[650,71,1021,83]` / 371×12 | `[769,93,888,100]` / 119×7 |

The title is 30 pixels narrower and eight pixels lower. The native subtitle is
22 pixels lower and is slightly left of the window center because its existing
allowance ends before Flat. This creates excess space between title and caption
and weakens the reference's centered two-line hierarchy.

## Eight-view inspection

| View | Observed result and boundary |
| --- | --- |
| Reference Play | Complete manuals, live fixed/bank/edit distinctions, two Upper/one Lower/one pedal indicators, cyan focus and disjoint sidebar pedals remain visible. |
| Default Play | Cabinet hides; both full manuals, full-width pedals and retained bank controls fit. No visible footer or control crop. |
| Minimum Play | Compact Edit controls move into racks; all keys/presets remain visible. Preset legends are tiny and still need real display/DPI usability review. |
| Minimum Flat | Plain panels and rectangular keys preserve visible held state and focus. It is intentionally a distinct usable presentation. |
| Both Service sizes | Six cards / 28 rows fit, including the singular “1 target”. Unavailable voltage/rpm, unacquired geometry and retained controls are explicitly distinguished. |
| Both Rotary sizes | Decorative/read-only framing remains clear; unconnected audio, unavailable speeds and unmodeled brake are not presented as live controls. |

The concept's three tablets beside each manual, vibrato selectors, preset/settings
block and microphone/speed controls differ from the implemented inventory. Keep
61+61+25 playing keys, 24 reversed presets, real header tools and truthful model
availability. Visible additions/substitutions necessarily prevent literal pixel
equality; they must remain explicit in README rather than being hidden under art.

## Prioritized implementation proposals

### 1. Wide Dimensional title and nominal-dry subtitle

This is the recommended next bounded change in `paint_header()` only. Activate
it when `layout.sidebar_pedals && presentation == Dimensional`; retain the
existing Flat and every non-sidebar paint path exactly. The integrator should
record a narrow amendment to the material contract's text-size freeze. No
UiModel, control bounds, focus, hit, parameter or saved-state change is needed.

- Set the Serif title's proposed size to **42.75**, preserving existing symmetric
  safe-interval fitting and centered advance. Use text top `header.y - 4.5`.
  Frozen font metrics predict advance 467.04375 and ink rectangle width 464.90625,
  height 33.13125; at reference size its predicted top is 20.05. These are
  calculations, not a rendered pass. Target measured ink width **464±3**, height
  **33±1**, top **20±1**, and visual center **835±2**.
- Keep the exact string **NOMINAL DRY ORGAN**. Use the existing Sans atlas at
  **17**, `kUiBrass`, top `header.y + 51.5`, and desired total advance **374**.
  With the current 188.59375 natural advance and 17 characters, spacing between
  characters is `(374−188.59375)/16 = 11.587890625`. Center it on the window;
  fit the entire line inside a symmetric interval also ending at least ten
  pixels before Flat. Reduce tracking and then size only if needed; never drop
  glyphs. Predictive ink width is 370.8125 and top 71.21875. Target measured ink
  **371±4 × 12±1**, top **71±1**, center **835.5±2**. Seventeen single-character
  draws are fixed bounded work and need no allocated text buffer.

Accept only after a real raster comparison at 1672×941 and the minimum sidebar
1400×820, plus fractional scales 1, 1.25, 1.5 and 2. Check all three workspaces,
common-control/focus separation and clip/viewport limits. Fixed-state frames
must preserve every pixel outside the changed header, and preserve whole
Flat/non-sidebar frames. A live app's asynchronous frame/revision text is not a
valid fixed-pixel oracle. Run affected drawing/view/material gates and the
existing same-geometry timing rule (30 warmups/300 measured draws; investigate
growth above both 15% and 2 ms). Retain v3 and produce fresh source-identified
captures for the changed product before updating README.

### 2. Key-edge optical depth

The live keys have correct projected silhouettes and clear fronts, but more
uniform side outlines than the concept's softened, directional bevels. A later
paint-only candidate can add narrow warm left-edge and dark right-edge strips
inside the original top quads, below held/focus ink. Keep the hit shape, front
split, palette meaning and Flat branch unchanged; do not add rectangular shadows
or silently change the shared raster's half-open ownership. This requires
independent corner/seam checks at all four scales, retained natural-front
contrast, held/focus visibility and timing. Extra per-key passes may cost more
than the header change; no performance or fidelity improvement is claimed yet.

### 3. Less regular deck grain

The current deck uses a regular row lattice with horizontal jitter; the concept
has less regular fine surface variation. A later candidate can introduce bounded
vertical jitter within each existing cell while retaining at most 2,048 pairs,
nonoverlap and the ≤8-channel perturbation budget. Preserve rim, label layering,
normal-text contrast, deterministic time-independent output and unchanged Flat.
This is a subtle texture change, not permission to increase global brightness,
add textures or disguise controls with the reference image. Qualify the actual
grain field and timing before deciding whether its visual benefit warrants it.

## Reproduction and next owner

From repository root, with Pillow 13.0.0, run:

```sh
python docs/development/2026-11-14-reference-refinement/reports/A36-measurements.py
```

The script writes JSON to stdout only and checks selected source hashes against
both captured inputs and the named published commit. Reproduce on that source
snapshot; after a product edit its identity assertion deliberately fails. It does not launch a GUI
or modify images. Root owns implementation assignment, contract amendment,
fresh acceptance, captures, README and publication. The full [M0–M9 plan](../PLAN.md)
and unconnected physical/model gates remain unchanged.
