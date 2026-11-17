# T2: two live rack headings

**Draft frozen candidate for independent review; A07, 16 November 2026.**
No implementation or visual acceptance is established by this document. A10's
independent review must admit the exact contract and its support before the
assigned painter changes. If a candidate fails, retain that observation and
review an explicit contract revision; never move its thresholds retrospectively.

## Scope and source

Change only `UPPER MANUAL DRAWBARS`, `LOWER MANUAL DRAWBARS` and their four
flanking rules in the existing active reference composition. Implement a private
rack-specific helper in `apps/standalone/InstrumentView.cpp`; replace only its two
manual-rack call sites. Preserve `reference_heading` and all other callers,
`centered`, `Drawing`, `FontData`, layout/control geometry and every sound/state
interface. T3 title treatment is a separate change and comparison.

The active predicate is unchanged: Dimensional Play, width at least 1400 and
height at least 820, within `kUiMaximumDimension`. Every inactive frame must be
identical. Fonts remain the existing licensed DejaVu Serif Book atlas; no image
contains baked heading text. PDF pp. 409–411 establish the visual direction,
correct control inventory and separation of live text from material artwork.
The [earlier T2 proposal](REFERENCE_MATERIAL_TYPE_NEXT.md#t2-rack-tracking-and-heading-baseline)
supplies authoring observations, not prior implementation acceptance.

| Inspected input | SHA-256 |
| --- | --- |
| Original `atlas-cover-reference.jpg`, 1672×941 | `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187` |
| Existing `native-gallery-preset-v1/images/play-reference-1672x941.png` | `6ac89798b41026533b474bbd523424134873af903a7bd1f9a58d09a583e0923a` |
| Pre-edit `InstrumentView.cpp` | `63bede9eb5fccde155d6d6ddfbbcbfa7566ab06dcf2726d92b84bc7ad0e72a77` |
| `Drawing.cpp` | `666e998cc61a9d501238783c8f2917d9be30db0bac76739f91bc23eb54f34b0a` |
| `FontData.h` | `f1a3121a2707a03a3b2e025c399e68c553ce9498f4b002ec13b18f512e334802` |
| `UiModel.h` | `6d8c0b16ddb6f3059dc14aff41bfc615e37b43c53b2f6e88cc199255a6b674b1` |
| `UiModel.cpp` | `0ecb0c4ee90d98cdb87c6f06b4685d368a7c12b72f9ea66e6c40228a4a855ecd` |

These are inspected-source identities. Root must separately bind the genuine
pre-edit executable and fixture to its build inputs. A historical gallery is
useful for authoring, but does not replace a genuine paired baseline.

## Measured image inputs

Rectangles below are half-open integer `xyxy` in the original, unresampled
images. Decode RGB without color or geometric transformation. Define warm ink
by `R >= G >= B` and `2126*R + 7152*G + 722*B >= 1600000`.
Use exactly these text-only `xywh` regions: Upper `(210,278,300,25)` and Lower
`(720,278,308,25)`. They exclude the source's bright side rules.

| Heading | Reference warm-ink bounds / count | Existing gallery bounds / count |
| --- | --- | --- |
| Upper | `(223,285,496,297)` / 726 | `(214,284,457,296)` / 561 |
| Lower | `(734,285,1017,297)` / 734 | `(733,284,981,296)` / 581 |

At source row 292, warm pixels with the lower threshold
`2126*R + 7152*G + 722*B >= 750000` and strict `R > G > B` occupy
`[140,205)`, `[513,564)`, `[662,715)` and `[1035,1083)` inside the separately
selected rule windows `[130,220)`, `[505,575)`, `[650,730)` and `[1025,1090)`.
These observations motivate the frozen placement below. They measure encoded
image appearance, not physical luminance or original hardware dimensions.

## Frozen live-text geometry

All arithmetic is C++ `float`/binary32 in the written operation order. Obtain
`sx`, `sy` and `f=min(sx,sy)` through the unchanged
`reference_composition_scale`. The two strings each contain 21 ASCII bytes,
including two spaces, so each run has 20 tracking gaps.

| Constant in canonical logical units | Upper | Lower |
| --- | ---: | ---: |
| String | `UPPER MANUAL DRAWBARS` | `LOWER MANUAL DRAWBARS` |
| Font size before scaling | 16 | 16 |
| Tracking between bytes | 1.5 | 1.7 |
| Run center x | 360 | 875.5 |
| New outer rule endpoints | 140, 564 | 662, 1083 |
| Inner rule gap from tracked advance edge | 16 | 16 |
| Rule y / thickness | 292 / 1 | 292 / 1 |

For each manual, derive the unchanged heading box from the actual mapped rack:

```text
box.x      = rack.x + 16*sx
box.y      = rack.y + 8*sy
box.width  = rack.width - 32*sx
box.height = 27*sy
size       = 16*f
tracking   = (Upper ? 1.5 : 1.7)*sx
center     = (Upper ? 360 : 875.5)*sx
top        = box.y + (box.height - size*1.2)/2 + sy
```

These fixed strings fit every supported active composition; do not introduce
an extra fitting/shrinking or clipping policy. For each one-byte `string_view`
glyph, obtain `advance[i] = drawing.text_width(glyph,size,TextFace::Serif)`.
Accumulate `natural` from zero in string order, then compute
`run_width = natural + tracking*20` and `left = center - run_width/2`.
Draw each glyph at the current cursor with unchanged `kUiBrass` and Serif face,
then perform **one grouped update** `cursor += advance[i] + tracking`.
The unused final tracking addition paints nothing. Do not insert tracking into
the global font API or derive it from viewport origin/clip extent.

At canonical size the mathematical natural advances are 246 and 251.2; the
actual binary32 sums are approximately 246.0000153 and 251.2000122. Total run
widths are 276 and 285.2000122. The old top/baseline 280.9/296.1 become
281.9/297.1, with the unchanged atlas ascent 38 at nominal pixel height 40.
The new run starts are 222 and approximately 732.9000244. These are derived
layout values, not claims about executed candidate ink bounds.

Draw rules after text, preserving their existing color `kMetalEdge` and using
exactly these logical endpoints:

```text
outer_left  = (Upper ? 140 : 662)*sx
outer_right = (Upper ? 564 : 1083)*sx
inner_left  = left - 16*sx
inner_right = (center + run_width/2) + 16*sx
y           = 292*sy
left rule   = {outer_left, y, inner_left-outer_left, sy}
right rule  = {inner_right, y, outer_right-inner_right, sy}
```

Retain the `Drawing::rect` nonpositive-extent guard. At canonical size the
proposed spans are `[140,206)` / `[514,564)` and approximately
`[662,716.9000244)` / `[1034.0999756,1083)`. Their small differences from source
spans are explicit: this is live type with symmetric 16-unit gaps. Do not claim
exact reference-rule pixels or change colors to conceal those residuals.

## Exact change support

An independent comparator must construct **the union of old/new glyph COPY
destination rectangles and old/new rule FILL rectangles** before observing
candidate pixel differences. No whole heading box, rack box, guessed rectangle,
changed-pixel-derived allowance or prior material mask is an admissible mask.

For the old path reproduce `centered` and `reference_heading` from the pinned
pre-edit source, including size fitting, its sequential whole-string advances,
center at the box midpoint, 14*sx inner gap, old outer inset 9*sx and old rule
y at the box's vertical midpoint. For the new path use only the equations and
constants above, not a candidate-exported mask or candidate layout helper.

For each glyph the unchanged atlas gives width, height, bearing and advance.
Let `q=size/40`, `baseline=top+38*q`. `Drawing::text` adds two transparent atlas
pixels in a dimension only when `glyph_dimension*q < 1`; include the same
padding in its bearing and copy extent. Each target is:

```text
x = cursor + (bearing_x-padding_x)*q
y = baseline + (bearing_y-padding_y)*q
w = (glyph_width+2*padding_x)*q
h = (glyph_height+2*padding_y)*q
```

Zero-ink spaces supply advance/tracking but no COPY rectangle. SDL 2.32.10 at
locked `5d249570393f7a37e037abf22cd6012a4cc56a71` independently multiplies each
coordinate/extent by renderer x/y scale. Software COPY truncates each resulting
float to an integer; zero extents paint nothing. Software FILL likewise
truncates x/y but takes `max(trunc(w),1)` and `max(trunc(h),1)` after a positive
logical rectangle passed `Drawing::rect`. Add the actual physical viewport
origin after these conversions. Intersect support with the output, viewport
and effective enabled clip, retaining an enabled-empty clip as empty. No
dilation is initially admitted. If exact SDL support cannot be established,
stop the containment claim and review it explicitly before implementation.

Paint preserves renderer scale/viewport/clip/blend state and model/session
state. This helper has a fixed maximum of 42 one-byte text calls and four
rectangle calls across both headings; no new allocation, font acquisition,
texture preparation or time source is introduced by its own logic. SDL's
existing command storage is not a new allocation-free UI claim, and none of
this work belongs in audio processing.

## Frozen acceptance

1. **Reference placement at 1672×941:** for each text-only region and exact
   threshold above, candidate warm-ink bounds exist, every bound differs from
   its reference by at most two pixels, and the sum of the four absolute bound
   errors is no greater than half the genuine baseline error. Candidate width
   differs from the reference width by at most three pixels. Bounds/density are
   separate observations; no threshold on ink count or whole-interface score
   is inferred.
2. **Preservation:** every differing pixel in genuine paired same-state frames
   belongs to the independently derived support. Require zero out-of-support
   changes; inactive and enabled-empty/disjoint frames are exactly equal.
   Compare complete padding-independent UI/session records before/after paint
   and across pairs. Require unchanged control/key/preset geometry and focus.
3. **Finite stress set:** canonical 1672×941, minimum active 1400×820, larger
   1920×1080, unequal logical 1920×820 and 1400×1080, fractional dimensions,
   renderer scales 0.75/1/1.25 and unequal 1.5×2, negative/positive viewport
   origins, partial clips through each heading/rule, enabled-empty/disjoint
   clips, Flat/Rotary/Service, 960×700 and thresholds immediately below
   1400/820. Preserve stated resource-crop limitations at maximum dimensions.
   Include held notes, focus, pending controls and A/B/fixed routes using the
   same predeclared states in both binaries.
4. **Visual admission:** independently inspect actual full frames and heading
   crops at canonical, minimum active and wide sizes. Reject clipping, broken
   letters, rule contact, illegibility or overlap even if numerical bounds pass.
   Keep both complete strings, correct footage labels, value/focus cues and
   nominal/unconnected-model labels. Preserve Flat/reduced-motion behavior.
5. **Integration:** rebuild coherently, run affected existing UI/control tests
   plus the new independent transition checks, retain original failures and
   source/binary identities, and update actual README captures. Real display,
   DPI, native accessibility and device/host qualification remain separate.

These gates admit T2 only. They establish neither T3, literal whole-interface
1:1, physical fidelity, complete M9 nor signed distribution.
