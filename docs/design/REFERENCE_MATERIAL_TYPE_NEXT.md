# Next Lower material, wood and typography implementation slices

**PROPOSAL — A41, 16 November 2026. No new production implementation,
candidate acceptance, frozen tolerance or authorization is recorded here.**
Literal whole-interface **1:1 remains unmet and unwaived**. The implemented
Upper finish keeps its existing contract and admission. This proposal makes the
next work concrete; an independent protocol/mask review must precede its edits.
Read with A39's [whole-window proposal](WHOLE_WINDOW_REFERENCE_NEXT.md), which
retains complete-window differences and semantic residuals without exclusions.

## 1. Actual inspected inputs

A41 read the full standing instructions and M0–M9 plan, recovered the active
scope/ledger and source, and directly viewed the original full image plus the
current actual 1672×941 and 1400×820 gallery frames. The
[observation report](../development/2026-11-15-streaming-continuation/reports/A41-material-type-observations.json)
and its
[reproducer](../development/2026-11-15-streaming-continuation/reports/A41-material-type-observations.py)
bind image, font, painter and asset identities and retain exact sufficient
statistics. No generated artwork, capture, build or broad test was run by A41.

| Input | SHA-256 and scope |
| --- | --- |
| [Original 1672×941 JPEG](atlas-cover-reference.jpg) | `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187`; unchanged atlas pages 1/409 image object; generated visual concept, not physical material data |
| [Current actual reference frame](../../examples/demos/upper-rack-material-v1/images/play-reference-1672x941.png) | `acc8ba94a8c3fee5e39bb26f575b9490767bd65210f2388bf1feabb947a545be`; decoded RGB `f7214cf8626accb548e2244e074607710c501f02d14d34fa8c2e9341c7fb2e24` |
| [Current minimum-active frame](../../examples/demos/upper-rack-material-v1/images/play-minimum-active-1400x820.png) | `3b356fdbdc91be20a581100b577fda51b604d34743d09e0690b834abf6ec3dc0`; directly inspected for small text and complete composition |
| Current `InstrumentView.cpp` | `30ac6cec988ec1834f36456d25d1e53113642071d844d53f81b62b3474cf2c37` |
| Current `FontData.h` | `f1a3121a2707a03a3b2e025c399e68c553ce9498f4b002ec13b18f512e334802` |

The [gallery provenance](../../examples/demos/upper-rack-material-v1/provenance.json)
binds app `c29495e98148767c0d55cab4adc18a245659cea891deb0f37fa160ea976c3cc1`
to base `4aac394cde4da40906b615573a8779aee2d9a37a` **plus its recorded
production overlay**, copied controls and replay. HEAD alone is insufficient.
The runtime PNG is useful visual evidence but its counters/meters are not an
identical-state before/after fixture. The earlier `eb9a501e…` app is the original
pre-Upper baseline; it is not the correct sole baseline for the next slice.

All measurements below use half-open integer rectangles in those unregistered,
unresampled 1672×941 images. Encoded-channel
`Y'=(2126R+7152G+722B)/10000` is an image statistic, not physical luminance.
Pillow 13.0.0/libjpeg-turbo 3.2.0 decoding has no ICC, gamma, EXIF, gain or
retouching step. RMS and slopes use exact rational least-squares sufficient
statistics before converting the displayed result to binary64.

## 2. Slice L1: Lower inner metal, with its own light field

The Lower panel is canonical `(600,269,516,239)` and its four-unit inset is
`(604,273,508,231)`. A39 supplied the two quiet patches below; A41 independently
decoded the original/current pixels and reproduced the means/RMS. These are
**observations for authoring**, with no Lower tolerance presently admitted.

| Lower patch `(x,y,w,h)` | Reference mean / plane-residual RMS | Current mean / plane-residual RMS | Reference vertical slope, Y′ per pixel |
| --- | ---: | ---: | ---: |
| Left `(612,320,18,128)` | 27.929753038194445 / 1.648025041753251 | 31.80559079861111 / 0.554379689237140 | −0.060897572528180 |
| Right `(1094,320,14,128)` | 20.590579464285714 / 1.450712070216063 | 32.01399185267857 / 0.983929468879251 | −0.029729283948518 |

The reference right-minus-left mean is **−7.339173573908731**; the current
difference is **+0.20840105406746**. The current Lower is too bright by about
3.876 on the left and 11.423 on the right. Upper's accepted positive lateral
slope, coefficients, seed and local tolerances do not transfer. Mirroring only
its slope would also miss the different Lower vertical slopes and color.

### A lower-specific initialization, not a fitted full-panel answer

For canonical pixel centers define `u=(x+0.5−604)/508` and
`v=(y+0.5−273)/231`. Interpolate the two observed means at their mean u/v and
their two independent vertical slopes with `a+b*u+c*v+d*u*v`. A41 obtains:

| Encoded channel | a | b | c | d |
| --- | ---: | ---: | ---: | ---: |
| R | 35.320924203 | −10.874155773 | −12.501738043 | 6.205237100 |
| G | 34.943428203 | −11.336804366 | −14.777279430 | 7.789951248 |
| B | 35.610452235 | −13.973112652 | −15.176662864 | 10.100565245 |
| Y′, diagnostic only | 35.071842987 | −11.428786733 | −14.322334815 | 7.619867351 |

The report retains exact coefficient fractions. The RGB equations describe an
unrounded smooth initialization; the Y′ equation is not a second color path.
The interpolation constrains two strips only. Interior, boundaries and corners
are extrapolations, and texture, JPEG residuals, wells and heading shadows are
not identified by the fit. Use additional uncontaminated center/top/bottom
observations and whole-frame inspection before freezing a first candidate.
Do not tune only the two scoring strips or paint them specially.

Proposed implementation shape after independent admission:

1. In [InstrumentView.cpp](../../apps/standalone/InstrumentView.cpp), add a
   private Lower surface selection to `reference_panel`, used only at
   `layout.registration_panels[1]` in `paint_reference_composition`. An explicit
   private selector can avoid a second ambiguous boolean. Preserve every old
   default/Upper branch and its arithmetic byte-for-byte unless a separately
   reviewed refactor proves exact preservation.
2. Add `reference_lower_rack_material` with distinct Lower coefficients and
   deterministic, nonperiodic grain parameters. It may reuse a reviewed
   physical-span abstraction; it must not call the Upper field with translated
   coordinates or silently change Upper's constants. Freeze channel rounding,
   evaluation order, clipping coordinates, seed, mark count, collision order,
   mark sizes/amplitudes and maximum work before its first production edit.
3. Fit grain toward the observed residual scale, without asserting that an
   image's plane RMS measures real metal roughness. Use bounded canonical
   marks/spans, fixed storage and no clock/random-device/viewport-origin seed.
   Clips must sample the complete field rather than renormalize it.
4. Replace only this call's inset gradient/grain. Keep its five outer shadows,
   rounded layers, four border accents, screws and all subsequent child draws
   in their existing order. Restore renderer scale/color, viewport/clip
   observations, enabled-empty-clip behavior and blend state on every path.

This slice leaves wells, caps, all text and key materials to separate slices.
Their antialiased edge RGB may blend differently over changed metal inside the
allowance; their arguments, geometry, opaque interiors and focus must survive.

## 3. Slice W1: narrow keyboard rim, then a separate plinth slice

The current `reference_wood` in `InstrumentView.cpp` uses a vertical gradient,
full-width dark rows every three canonical units and a highlight every ninth
row. At a fixed y, its unoccluded RGB is constant across x. That explains the
visible horizontal striping; a new palette alone cannot produce the reference
wood variation or narrow polished edge.

The following row-residual RMS removes each row's own mean first. It measures
horizontal variation, unlike the plane-detrended metal statistic. These are
descriptive inputs with no proposed pass threshold.

| Quiet wood patch `(x,y,w,h)` | Reference mean Y′ / horizontal RMS | Current mean Y′ / horizontal RMS |
| --- | ---: | ---: |
| Rim left `(280,518,120,6)` | 62.431289 / 10.441933 | 48.523267 / 0 |
| Rim middle `(650,518,120,6)` | 60.567912 / 8.041064 | 48.523267 / 0 |
| Rim right `(980,518,120,6)` | 61.021781 / 14.817863 | 48.523267 / 0 |
| Plinth left `(240,928,160,8)` | 27.726958 / 5.914356 | 39.447575 / 0 |
| Plinth middle `(748,928,176,8)` | 26.837882 / 3.558000 | 39.447575 / 0 |
| Plinth right `(1170,928,160,8)` | 25.867360 / 5.877757 | 39.447575 / 0 |

The rim middle's six reference row means at y518…523 are
**131.663, 152.909, 22.455, 13.774, 22.170, 20.437**; the current means are
**50.210, 51.210, 48.857, 43.576, 55.780, 41.508**. A mean-only target would
hide the dominant missing two-row highlight and the dark recess immediately
below it. Preserve full row profiles and spatial differences.

Start W1 at only the existing call for `(48,510,1074,18)` in
`paint_reference_composition`. Introduce a private rim-specific helper or
style; do not change global `reference_wood`, whose other callers include the
whole background, preset cheeks, plinth and cabinet fallback. The proposed
surface needs a canonical vertical profile with a narrow crest around y518–519,
a darker lower face, and spatially varying elongated grain/reflections. The
left end overlaps a different reference cheek/rim geometry, so the three
listed patches cannot determine the complete rim profile. Independently
annotate that transition before freezing support and coefficients.

Use a fixed-count deterministic segment/curve scheme with explicitly bounded
horizontal lengths, vertical displacement, opacity and evaluation count. Clip
its output to the declared rim; preserve the field's uncut phase at clips and
resizes. Reject a repeated tile, unbounded per-device-pixel noise, a continuous
unvarying highlight stripe, or visibly new seams. Specify exact finite work
and SDL raster support before implementation, not after seeing escapes.

W2 may later target only `(16,887,1640,54)`. Its visible bottom wood is too
bright in the sampled strips, while the live footer covers most of its center.
Freeze its material support and the retained footer paint order separately.
Never replace the footer/status/meter with the reference's baked
`DESIGN CONCEPT` lettering. Cheeks and fallback cabinet wood remain later work;
the original decorative assets retain their bytes and placement.

## 4. Typography: dynamic glyph geometry before changing font assets

### T1: footage baseline and fraction layout

The existing `reference_drawbar` calls `centered` with Serif size 19, a 46×23
label box at canonical y467 and two units of horizontal padding. Current atlas
advances force every mixed fraction to **15 px**, while ordinary footages stay
**19 px**. `centered` changes the top as it shrinks; `Drawing::text` then uses
the Serif ascent 38/40. Reconstructing those actual source formulas gives:

| Live labels | Current fitted size | Current logical baseline |
| --- | ---: | ---: |
| `16'`, `8'`, `4'`, `2'`, `1'` | 19 | 485.15 |
| `5 1/3'`, `2 2/3'`, `1 3/5'`, `1 1/3'` | 15 | 483.75 |

At the descriptive Y′≥100 warm-ink threshold, original `16'`, `8'`, `4'` and
`1'` ink occupies y473…488 inclusive; current ink occupies y470…483. The
report retains each ROI and bounding box, including `2'`'s different last row.
This is an observed displacement/height mismatch, not permission to copy the
reference's incorrect footage or rasterize its lettering into an asset.

Propose a private `reference_footage_text` called only for the eighteen manual
drawbars; pedal-mixture labels keep their current path. Keep the existing
label/value/hit boxes and dynamic complete strings in
[`kUiFootageLabels`](../../apps/standalone/UiModel.h). Compose recognized
whole number, numerator, slash, denominator and apostrophe from existing ASCII
glyphs, with width measured as the sum of the same rendered advances. Center
the complete run on the unchanged drawbar center; do not move a control.

An explicit starting candidate for protocol review is: major numeral and
apostrophe size **20.5**, baseline **488.5**; fraction numerator/denominator
size **13**, baselines **482.5/488.5**; slash size **16**, baseline **486.5**;
canonical gaps **0.5** after the whole numeral and before the apostrophe.
These existing advances total **40.9** units for each mixed label, inside the
42-unit padded width. Ordinary `16'` totals 31.2625. Font sizes scale by `f`,
baseline positions by `sy`, and horizontal positions/gaps by `sx`; compute
the final top from `baseline − ascent*size/40`, not from each run's box height.
These are unrendered proposal values, not accepted pixel outcomes.

Freeze all nine complete strings, run metrics and glyph supports before T1.
At 1400×820 the 13-unit fraction text becomes about **10.885 px** in isotropic
font size; actual ink is smaller and must be judged on the real display/DPI
journey. If the compact fraction layout impairs reading, retain a readable
full-string alternative and revise the candidate openly. No illegible fraction
may be accepted because its silhouette improves an image score. Keep values
in y491–506, all focus outlines, edited/sounding/pending cues and the correct
`1 3/5'`; no Unicode fraction can be sent to this ASCII-only atlas.

### T2: rack tracking and heading baseline

`reference_heading` currently renders untracked Serif text and computes its
side-rule gap using the same untracked width. At Y′≥160 with warm ink, the
Upper original/current bounds are `(223,285,496,297)` /
`(214,284,457,296)` in half-open xyxy form. Lower is
`(734,285,1017,297)` / `(733,284,981,296)`. Thus widening alone misses the
reference's rightward visual centers and one-row lower heading ink.

Propose a private measured/tracked helper for these **two rack headings only**.
Keep size 16 initially, with authoring starts of Upper tracking 1.5 and Lower
tracking 1.7 canonical units, approximate visual centers x360/x875.5 and a
one-unit lower baseline. Current exact natural advances are 246/251.2; these
starts give total advances 276/285.2. Independently review glyph bearings and
actual raster coverage before fixing final anchors. Both ruler gaps must use
the final tracked run width. Do not alter shared `centered`, all
`reference_heading` callers or `Drawing::text_width` globally.

### T3: title weight and emboss, separately

The same-string title already has similar gross extent: at Y′≥100 the
reference/current ink bounds are `(603,20,1067,53)` /
`(602,20,1065,53)`. Yet the reference has **5,415** qualifying pixels and the
current has **3,863**. The current count remains lower at every reported
threshold 80/100/120/140/160; changing only title size is poorly targeted.
Threshold counts combine color, antialiasing and shape and are not a font-weight
measurement or acceptance score.

`reference_header` is the extension point: current title size 42.75×f,
center x836×sx, top y11.5×sy, one dark shadow at `(sx,2sy)` and one solid brass
pass. First retain these layout anchors and investigate a bounded, explicitly
specified live-glyph weight/highlight/shadow composition. Freeze its offsets,
alpha/color and actual glyph-support union before editing. If the retained
Book glyph shape cannot achieve the intended appearance, a separately sourced
font candidate needs its own pinned bytes, coverage, license and atlas review.
No new font was acquired, and no font/title candidate is accepted here. Preserve
the truthful `NOMINAL DRY ORGAN` caption and all live utility controls.

## 5. Provenance and preservation boundaries

Existing [font provenance](../STANDALONE_FONTS.md) records unmodified DejaVu
Sans Book and Serif Book **2.37**, copied locally. Their hashes are
`57f73e11f51999432bf7ab22ce55b6f945d5eca1bf824404cfa9ec2e3718c84e` and
`8cb29f7db250ebb2551a6ce2c1e0bfd5a0eb520e9e233370db0493e82e1f36f7`.
The complete Bitstream permission/trademark notice and public-domain DejaVu
changes are in `assets/standalone/fonts/LICENSE-DejaVu.txt`, hash
`22308e512b54800ba9fe6f9aecd6bea42b71f68f77dbc83196715aac50e631d6`.
Retain the full notice with distributions; Debian packaging's separate GPL
section is not the font license. This record settles no unrelated artwork rights.

`FontData.h` contains 95 glyphs per face, Sans 32 px and Serif 40 px, authored
with Pillow 13.0.0/FreeType 2.14.3 BASIC layout and two transparent pixels of
gutter. Ordinary builds/runtime require neither Pillow nor a font rasterizer.
`Drawing::text` owns the existing tiny-glyph gutter fix, bearings and advances;
`text_width` has no kerning/shaping or tracking. T1/T2 can use these unchanged
glyphs and private layout helpers, avoiding an unnecessary global font change.

[Decorative art provenance](../REFERENCE_ART_ASSETS.md) admits only the cabinet
`(1132,174,466,397)`, left cheek `(0,0,24,941)` and right cheek
`(1604,0,68,941)` crops. Manifest hash is
`bf1bec09c0dd15d09ab0129f950ccb5370532f92cb9217e347ba69e96d24bc87`;
compiler verification pins those source/blob identities. The broader rejected
left crop contained control lettering; the bottom rail contains baked text.
Neither is a usable shortcut. This proposal adds no art or dependency and
leaves the source-publication rights gate unchanged.

Each slice must preserve `UiModel` geometry/hits and all musical state: 68
controls, 147 playing keys, 24 presets, four banks, 71 Play focus stops, 47
parameter meanings, `B3CONTROLS4` and readers 1–3, held-key ownership and
releases. Retain 0-at-top/8-toward-player drawbar travel, stored percussion
versus applied eligibility, explicit unconnected-model labels, Flat/reduced
motion and all nonactive layouts. No painter/font/asset operation belongs in
the audio callback.

## 6. Gates before any implementation and actionable handoff

Assign independent protocol/mask ownership, then separate painter and admission
ownership. Freeze **one slice at a time**. A39's reporting partition is not an
edit mask; the old composition and Upper masks cannot admit these new supports.

For L1 derive Lower's mapped panel from actual binary32 edges x600/x1116,
y269/y508, then apply `reference_inset(4)` in its actual operation order.
Do not directly scale the displayed canonical inset and assume equal endpoints.
Independently enumerate the old gradient/grain and proposed new support using
the real `Drawing::gradient` center-span and pinned SDL fill-rectangle rules.
Read viewport/clip at physical scale one; retain enabled-empty clips. A proposed
one-device-pixel outward allowance, if independently justified, would be
`[603,1113) × [272,505)` at reference scale/origin, **118,830 pixels**. This
number is prospective and must be verified from the chosen candidate's support.
It is not permission to modify the inset's border or children.

W1/W2 require distinct supports from their finite primitives and restored
caller clip, with no whole-background allowance. T1/T2/T3 require unions of
old/new actual glyph quads, all offsets and changed ruler primitives under
SDL's subpixel rules; no full-header/rack rectangle may replace that derivation.
Freeze unrounded target data, sensible slice-specific tolerances and baseline
outcomes before tuning. Neither Upper's five screens nor A41's descriptive
thresholds are new Lower/wood/type acceptance criteria.

Before source edits, root preserves the **current** source overlay, dependencies,
app and existing fixture binaries as the new genuine baseline. Build any
supplemental harness once against that preserved painter and matching inputs,
then against the candidate. Do not manufacture a before frame by bypassing a
new painter branch or relabel the original pre-Upper binary as the new baseline.
Preserve all existing frozen fixtures, failures and galleries.

The independently frozen matrix must cover reference/minimum-active/1920×1080,
scales 1/1.5/2, physical origin and `(13,17)` offsets, each changed edge's
physical/fractional logical clips, disjoint and enabled-zero clips, drawbars
0/4/8 on both manuals, focus across changed surfaces/text, fixed/adjustable/
Cancel routes, pending/applied state and held notes. Include 1399×820,
1400×819, 1280×900, 960×700, Flat, Rotary and Service exact-preservation cases.
Retain extreme-size bounded-output/resource coverage separately from ordinary
full frames with a nonempty protected exterior. The Upper fixture alone does
not exercise Lower-focused material/text cases.

Require zero changed RGBA pixels/channels outside each admitted support,
whole-frame equality for inactive/disjoint cases, clip/full-frame companion
agreement, restored renderer state and repeat/fresh-renderer determinism.
Check opaque child interiors, exact focus ink, geometry and copied snapshots
independently; do not demand alpha-blended text-edge RGB equality over changed
metal or accept one nonempty glyph pixel as legibility evidence. Retain raw
differences and failed screens. Inspect complete actual before/after native
captures, including all labels, at reference and minimum-active sizes; obtain
independent source/state/pixel admission and update README afterward.

Immediate reproducible documentary commands, from the repository root:

```sh
python3 -B docs/development/2026-11-15-streaming-continuation/reports/A41-material-type-observations.py
git diff --check -- docs/design/REFERENCE_MATERIAL_TYPE_NEXT.md \
  docs/development/2026-11-15-streaming-continuation/notes/A41.md \
  docs/development/2026-11-15-streaming-continuation/reports/A41-*
```

Root's later integrity command is `python3 -B tools/check_repository.py --json`.
After an admitted production slice, root rebuilds the actual coherent inputs
and runs the affected geometry/input, drawing, material, waveform-material,
product-visual, scaled-view, preset and percussion raster gates plus its new
independent pair checker. Existing exact test names are in
[standalone CMake](../../apps/standalone/CMakeLists.txt); for example, after the
required build:

```sh
ctest --test-dir ../build-native -C Release --output-on-failure --no-tests=error \
  -R '^test_standalone_(drawing|quad_drawing|material_acceptance|waveform_material|product_visual|scaled_view|preset_raster|percussion_raster|upper_rack_material_raster)$'
```

That existing selection is only part of the future gate; it supplies no new
Lower/wood/type fixture automatically. No such test/build/capture was run here.
Recommended order is **L1 → W1 → T1 → T2**, each independently admitted;
W2/title/key-cap materials follow their own inputs. Even passing every slice
would leave whole-interface 1:1, actual display/DPI/input, native semantic
accessibility, physical/audio fidelity and release/platform requirements open.
