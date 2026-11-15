# Product continuation: native visual refinement

Design identity: `standalone-wide-legibility-v1`. This is the implementation
contract for the product continuation's paint slice. The frozen paint behavior
below is implemented with the bounded qualification recorded here; current
gallery admission and literal whole-interface equality remain separate gates.
It amends the text-size/cap-footprint preservation clauses of the earlier
[material contract](REFERENCE_REFINEMENT_MATERIALS.md) and
[waveform paint contract](WAVEFORM_UI_DESIGN.md) only within the scope below.
The [layout contract](REFERENCE_REFINEMENT_LAYOUT.md) remains unchanged.

## Implementation and evidence status — 15 November 2026

[A15's implementation](development/2026-11-15-product-continuation/notes/A15-visual-implementation.md)
adds complete fitted footage, 32-pixel manual caps with eight-pixel fronts,
14-pixel numeric ink, separate EDIT BANK/applied SOUNDING rows, and restrained
idle-natural edge lighting/reduced rear recess. The wide Dimensional activation
and all unchanged-layout requirements below remain in force. The later MIDI
overlay occupies a separately owned paint path; it is not part of the fixed-state
whole-frame comparison.

| Evidence | Observed result | Qualification boundary |
| --- | --- | --- |
| [A23 independent raster report](development/2026-11-15-product-continuation/reports/A23-visual-acceptance.json) | 19,712 checks, 110 paired cases and 336,015,828 compared pixels; zero escaped pixels and readout-shadow leaks; 34 byte-identical compact/Flat/hidden pairs. Complete literal glyphs, cap separation, applied captions, held/focus/pending states, scale and clipping are witnessed. | Identified SDL software surfaces and fixed copied state, overlay None. This establishes containment and preserved paths in the tested cases, not perceptual resemblance, display readability or native accessibility. |
| [A23 retained material fixture](development/2026-11-15-product-continuation/notes/A23-visual-acceptance.md) | 1,917 checks in 55 cases pass with 32/8 wide caps, unchanged compact/pedal expectations and unchanged front contrast. | Exact source and fixture identities remain in the report, including initial harness failures and their corrections. |
| [A27 paired paint report](development/2026-11-15-product-continuation/reports/A27-paint-performance.json) | All six scale-1 cases stay within the declared regression budget; largest median increase is 1.380 ms / 1.228%. Wide Dimensional observed C++ allocations/frees fall 21 to 19 per draw; compact and Flat counts are unchanged. | Thirty warmups and 300 measured draws per painter; a separate calibrated heap observer. Absolute current wide medians are 112.441–113.713 ms on the pinned shared-host software fixture. This is not a 60-fps, display-latency, audio-deadline, leak-freedom or hardware-resource pass. |
| [A34 current reference review](design/PRODUCT_REFERENCE_GAPS.md) | Direct inspection of the original reference, historical v5 and two provisional current application images confirms the visible local changes and documents remaining differences. Current source/executable and image bytes were independently rehashed. | The two current images are review previews, not an admitted product gallery. The minimum-size MIDI preview does not extend wide-painter or real-device qualification. |

The before painter is `af006b0ae293c7c9a5f44b5dfe1dc9942fe9e12d`'s
`InstrumentView.cpp`, SHA-256
`aae710a6e4eb8d7eccfe8fd7e5cf3cb98109ee1bc0143229e5b5b8b63f3c7a4c`.
Both A23 and A27 identify the after painter as
`3687f96db4490e600d6107e6b39d7b7d568bdeb183f16f6aa397535a5f688567`;
A34 verified those after bytes remain present. A23 retains the original
contract-document hash; both reports retain their original execution context.
This status addition does not rewrite those identities or change the frozen
contract below.

**Next UI gate:** admit fresh source/executable/pixel-bound application captures
at reference/default/minimum sizes and Flat, plus the separate MIDI overlay,
then refresh README from the accepted images. The
[prioritized gap record](design/PRODUCT_REFERENCE_GAPS.md#next-ui-gates)
defines the remaining display/usability and material work. Preserve v1–v5 and
their actual capture identities; a newly reviewed preview is not a recapture
of historical evidence.

## Source and exact scope

Directly inspected the original [cover/page-409 reference](design/atlas-cover-reference.jpg)
and the actual [v5 Play frame](../examples/demos/standalone-interface-preview-v5/images/play-reference-1672x941.png).
Their SHA-256 values are respectively
`9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187` and
`f5bf973c949b71d900572cffba72d617f1f2e61efb640b3e9ce97f90d2c30a19`.
The latter retains its actual `487064d2` capture identity. Review at a newer
checkout does not create a new capture.

Activate this paint treatment **only when `layout.sidebar_pedals` is true and
presentation is Dimensional**, equivalent to `W >= 1400 && H >= 820` for
admitted layouts. Its changed surfaces are the two manual drawbar racks and
idle natural keys of the two manuals. Preserve other workspaces, all header
paint, cabinet artwork/status, presets, pedals, percussion, expression and
footer. The separate MIDI calibration overlay has its own contract and must be
excluded explicitly from fixed-state whole-frame identity comparisons.

Own `InstrumentView.cpp` paint helpers/call sites and scoped native tests.
Do not change `UiModel`, control/track rectangles, fonts, `Drawing` APIs,
assets, dependencies or audio code. Preserve **68 controls, 24 presets,
147 playing keys, 71 Play/ten common focus stops, 47 parameters and state4**.
Compact and Flat rendering retain their original path and pixels.

The atlas's pp.409/411/431 exclude incorrect concept key counts and legends.
Keep actual `1 3/5` footage and drawbar direction **0 at the top, 8 toward the
player**. Do not add unsupported scanner, microphone, Stop or preset controls.

## Source-derived geometry constraints

These values were calculated from current `make_ui_layout` arithmetic, not
measured from a new executable. All units are logical pixels. Each label row
is 24 high; each value row is 16 high.

| Window | Rack width | Label width | Label top | Track top / bottom | Value top |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1400x820 | 430.8222 | 41.2025 | 258.4 | 296.4 / 387.2 | 405.2 |
| 1672x941 | 516.4677 | 50.7186 | 272.92 | 310.92 / 430.76 | 448.76 |
| 1920x1080 | 601.8320 | 60.2036 | 278 | 316 / 446 | 464 |

There are only **14 pixels between the original label-row end and track top**,
and **18 between track bottom and value-row start**. A naive 32-34-pixel cap
enlargement therefore overlaps the existing label band or extends its shadow
into the numeric row. The following treatment must solve that explicitly.

## Frozen paint behavior

### Drawbar legends and caps

Use the upper **20 pixels** of each unchanged manual label rectangle for the
footage ink. Start at **17** logical-pixel serif type; fit the complete label
using actual glyph advances, keeping at least two pixels of horizontal inset.
`centered` naturally limits a 20-pixel row to 16.667 type. At narrow columns,
ASCII numerator/denominator groups may be stacked at 8-9 pixels beside the
whole-number glyph, with a drawn fraction bar. The existing font contains
printable ASCII only: do not send Unicode fractions or prime characters to it.
Keep the footage complete, including its apostrophe. No ellipsis, omitted digit,
or expanded text boundary is permitted. Numeric values remain legible within
their unchanged 16-pixel row; an increase may use only measured available ink.

Set the candidate manual cap height to **32 pixels** while retaining the
existing width and exact center `track.y + track.height * value / 8`. A height
up to 34 is permitted only when the same independent containment checks pass;
32 is the default. At 32, the upper endpoint begins two pixels below the new
20-pixel legend box, and the lower endpoint ends two pixels above the value row.
Retain the existing brown/ivory/black grouping, dark shaft and sculpted cap front.
Use an 8-pixel internal front; material differences remain inside the cap.

Bound the recess, cap shadow and any new ornament to the interior strip
**from `label_bounds.y + 21` through `value_bounds.y - 1`** and to the existing
control bounds. Reduce/intersect shadow rectangles before painting, including
the lower endpoint, rather than allowing a shadow to cover the readout.
Reject empty/nonfinite local geometry. Do not alter ticks, travel, hit targets,
drag ownership or focus outlines. Footage/value text and focus paint remain
above the finished material. Pedal-mixture caps keep their existing 22-pixel path.

### Separate edit and sounding information

Keep the rack title in its left allocation. Use the existing rightmost **43%**
of each rack for two distinct rows: `EDIT BANK A/B` and
`SOUNDING FIXED C#`, `SOUNDING A#`, `SOUNDING B`, `CANCELLED`, or
`SOUNDING UNAVAILABLE`, as appropriate. The first row comes from the edited-bank
selection; the second comes only from the copied applied controls.

Use row boxes at rack y+2 and y+16, each 14 high, with initial 11.5-pixel sans
type and bounded width fitting. Their ink ends before the footage row at y+32.
Keep the current title size and truthful route coloring. These rows do not
replace independent amber pending or cyan focus indicators. Do not relabel a
desired fixed registration as already sounding.

### Manual natural-key lighting

Retain existing `top`, `front` and `hit` quads and the qualified darker fronts.
For **idle manual naturals only**, add a restrained warm left-edge reflection
and a narrow dark right counterpart inside the top quad. Their normal width
is at most one logical pixel, inset at least one pixel from the silhouette,
and bounded to the middle 8%-88% of top depth. Interpolate from the supplied
quad; never use its bounding rectangle. Use fixed colors/alpha, no animation.
Reduce the rear recess's maximum alpha from 90 to a candidate **70** while
retaining its 12%/18-pixel depth cap and fade to zero.

Leave accidental, held-key and pedal paths unchanged. Preserve the original
top gradient away from these small bands and preserve front-face pixels.
Paint held markers and focus last. No rectangle or line may leak across a
sloping seam, neighboring key or active drawing clip.

## Independent acceptance and promotion

1. Freeze before/after product inputs and copied view/device facts. At 960x700,
   1280x900, 1399x820, 1400x819 and all Flat sizes, require identical body/header
   pixels. At active sizes, deltas must be confined to manual rack interiors
   and idle natural top quads. Preserve all existing geometry/state/ownership
   tests and earlier historical results.
2. Exercise 1400x820, 1672x941 and 1920x1080, fractional sizes, and output scales
   1, 1.25, 1.5 and 2. Test all nine drawbar positions and each cap family,
   both banks/manuals, fixed/adjustable/Cancel states, pending edits and focus.
   Independently measure complete label ink, cap/readout separation and zero
   changed pixels outside allowed regions. Retain existing contrast and clip
   assertions; do not weaken them to admit a regression.
3. Verify idle/held/focused naturals and accidentals, including manual ends,
   neighboring black keys and clipped/offset viewports. Front-face and held
   palettes remain unchanged; existing front-contrast minima still apply.
4. Use the earlier **30 warmup + 300 measured draws** procedure on one renderer,
   excluding capture/I/O. Retain median/p95 and investigate growth exceeding
   both **15% and 2 ms**. This is a UI regression budget, not an audio deadline.
   Fixed new primitives must not add per-frame heap allocation or textures.
5. Capture the real changed native app at reference/default/minimum sizes and
   Flat, plus the separately changed MIDI overlay. Bind source/executable/pixel
   hashes, inspect lossless images, record specific remaining reference gaps,
   and refresh README only after acceptance. Preserve the original v1-v5 images.

Larger legible controls and improved local lighting do not establish literal
whole-interface equality. Complete manuals/presets/pedals, functional utilities,
the dry-organ caption, current registrations and unavailable cabinet/scanner
features continue to differ from the concept. Hardware fidelity, actual display
readability, screen-reader semantics and physical MIDI/audio remain separate gates.
