# Native scaling, text and clipping audit

Actual worker: `/root/w05_a28_scale_text_audit`, A28 of the current interface
continuation. **The scoped native state/clipping/value-presence gates pass after
one repaired clip bug. Fractional-scale appearance does not pass:** the retained
1.5× images expose repeated unpainted rows in dimensional surfaces, now assigned
to A31. Tiny preset accidental legends remain the separate A34 readability gap.

The [result record](../development/2026-11-14-interface-continuation/reports/a28-scale-text-audit.json),
[final native log](../development/2026-11-14-interface-continuation/reports/a28-ctest.txt),
and [source/build identities](../development/2026-11-14-interface-continuation/reports/a28-final-identities.json)
identify this working overlay on published HEAD
`5d81199a9822874b55f3b0a124715cbd6eadf0e5`. HEAD alone does not identify the tested UI.

| Claim | Observed result |
| --- | --- |
| Strict Release compile and affected native gates | Pass: 2/2 suites; 27.90 seconds total. |
| Complete-view renderer state and clipping | Pass at the specified 1×, 1.5× and 2× fixtures after the narrow preset-focus repair. |
| Service values and row budgets | All 28 values measured at minimum/default; all 58 expected value lines across both sizes produce native ink at 1.5×. |
| Complete fractional-scale appearance | **Open defect:** every third row is unpainted in the measured dimensional-card interior at 1.5×. A31 owns repair. |
| Small preset legends | **Open readability gap:** minimum D# is 6.153846 logical units. A34 owns review/repair. |
| Native display/DPI, GPU, accessibility or human legibility | Not qualified by these software-surface tests. |

## Scope, source and actual execution

Read the standing instructions, full project plan, current scope/checkpoint,
workspace/geometry/inspection contracts, A14 primitive evidence, A25's full-view
raster source and the current actual application gallery. Inspected the actual
minimum Play/Service gallery images and both new full-size 1.5× proof PNGs.
A27 owns the ordinary-control responsive inventory; its
[font/geometry review](INTERFACE_RESPONSIVE_AUDIT.md) remains separate.
A14's primitive masks and A25's 1× held-state/occlusion cases were not rerun as
new coverage here.

Added `apps/standalone/native_tests/test_standalone_scaled_view.cpp`. It calls
actual `paint_instrument` and initializes the actual `Drawing` fonts and art on
an SDL 2.32.10 software renderer backed by an RGBA surface. `UiModel::observe`
receives an injected copied `SessionSnapshot`; the inspector receives deliberately
injected display-profile values. No Session, application window, audio/MIDI device
or physical display is opened. A screenshot's injected `CURRENT SNAPSHOT` and
`AUDIO RUNNING` labels are fixture fields, not observations of active devices.

Root registered the test with drawing/support libraries, `SDL_MAIN_HANDLED` and
a 60-second timeout. GCC 14.2.0/C++20 Release compilation passed the repository's
strict conversion, sign-conversion, shadow and other warning flags as errors.
After the authorized repair, both affected raster targets and
`hammond_standalone` were rebuilt from coherent source. The final source hashes
were unchanged before and after the focused gate.

Final `InstrumentView.cpp` SHA-256:
`6b498c9ba2c47acf432216189159b928d2a5d31368ec34c1fe8dc906710e8a67`.
Final application SHA-256:
`55b0947985ee562cce3d04eae66cc4d44f805420f475dd578f00373dd2bef6cd`.
Final scaled-test SHA-256:
`95a15c6e411d78eacd63cbb7c7f0d6edaf7df231a2b2dc83cb1426dc01e3db63`.
The identity report also retains source/header/atlas/CMake, linked archive,
generated art/profile, compiler and pinned-SDL identities. The first failed run
has its own pre-repair source record.

## What the 168-frame gate establishes

The complete renderer was exercised for Play, Rotary and Service, in both
Dimensional and Flat presentations, at logical 960×700 and 1280×900 with
renderer scales 1, 1.5 and 2. The default-size 2× output is covered by four
overlapping 1920×1400 tiles of its 2560×1800 virtual viewport; no large complete
surface or screenshot was retained. The maximum allocated target is 1920×1400.

The matrix contains 54 full-view/tile frames, 18 translated-viewport/body-clip
frames, 18 preset-focus clipping frames, 20 playing-key focus/baseline frames,
and 58 Service baseline/value-color frames. It retains:

- **168 state checks:** scale, physical and logical viewport/clip queries, clip
  enable and blend mode survive each complete mixed quad/font/control paint.
- **90 complete-target clipping checks:** direct locked-surface reads inspect
  pixels outside the viewport as well as inside it. There is no non-background
  ink outside the admitted viewport/clip. `paint_instrument` intentionally calls
  `SDL_RenderClear`, which clears the entire target independently of clipping;
  that declared uniform clear color is explicitly exempt from the ink oracle.
- **16 scaled focus cases:** Upper indices 0/30, Lower 60 and Pedal 13 at 1.5×/2×
  in both presentations. Changed key-area pixels remain cyan and inside the
  focused key, with at least eight visible pixels. Semantic footer changes are
  excluded from the key-only comparison. These extend A25 to output scaling;
  they do not repeat its full held-state/occlusion acceptance.
- **56 Service value probes / 58 line probes:** each row's unchanged value/units
  is repainted with an alternate availability color. Every expected value line
  changes at least three physical pixels, and changes remain in that row's card.
  This checks actual native value ink, not OCR or complete glyph recognition.

The existing preset raster suite also passes: 96 preserved label/focus cases,
376 other-manual/accidental isolation cases and 48 applied/pending/Cancel/rejection
checks. This recheck is necessary because the observed repair touches preset
focus painting.

## Repaired failure: scaled preset focus changed the caller's clip

The [first native run](../development/2026-11-14-interface-continuation/reports/a28-ctest-first.txt)
completed 156 frames with four failures, all in accidental preset focus. At 1.5×,
physical clip `[17,19,1361,957]` became `[16,18,1360,957]`; at 2×,
`[17,19,1841,1307]` became `[16,18,1840,1306]`. Both presentations failed.
All other first-run state/ink/focus/Service checks passed.

`paint_preset_focus` read and restored an integer clip while the renderer was
scaled. Pinned SDL divides its stored physical rectangle by the current scale
and floors each component when returning `SDL_RenderGetClipRect`; restoring
those rounded logical integers loses odd physical edges. The common application
path normally has no caller clip, so this was a renderer composition defect,
not an observed ordinary application input failure.

After root explicitly authorized this narrow production change, the function
captures the original physical clip at scale one and intersects its temporary
focus clip in physical coordinates. It restores the original logical clip when
that round trip preserves the physical rectangle, retaining ordinary half-pixel
components from 1.5× logical clips; otherwise it restores the saved physical
rectangle. The original scale is restored. Geometry, labels, font sizes, material
colors and musical state are unchanged. No other production function changed.

The final regression includes clips originally defined in physical units,
clips defined at the current logical scale, and a clip edge crossing D# itself.
It checks both physical and logical query values and outside ink. The original
failure and its source hashes remain retained; no threshold was relaxed.

## Open visual failure: dimensional surfaces have gaps at 1.5×

The required visual review found a defect that the numeric oracles above do
not measure. The retained Play and Service proofs show horizontal walnut lines
through dimensional panels, buttons and drawbar caps. This is not a lossless
PNG conversion artifact: decoded BMP and PNG pixels were compared exactly.

In the Service PNG, the blank Generator-card interior patch
`x=60..439, y=444..518` contains 28,500 pixels. All **9,500 pixels on rows where
`y % 3 == 2` equal the exact clear walnut RGBA `(85,54,36,255)`**. None of the
19,000 pixels on the other two row classes equals that clear color. Thus 25
complete rows of this 75-row interior are unpainted. The
[retained measurement](../development/2026-11-14-interface-continuation/reports/a28-fractional-surface-gap.json)
uses the existing, unchanged PNG; it does not introduce another native run.

Source diagnosis: `Drawing::gradient` and `Drawing::rounded` iterate logical
rows and emit rectangles of height 1. Pinned SDL's software `SW_QueueFillRects`
converts scaled rectangle heights to integer pixels. At 1.5×, a 1.5-pixel height
becomes one pixel, while consecutive row origins advance by alternating one and
two pixels. The omitted rows expose the background. A14's quad raster already
works in physical pixel centers, so its key silhouettes/focus can pass while
these older surface routines remain defective.

**A31 owns the scaled gradient/rounded repair and an interior-coverage regression.**
Root requested no further production/test edits during the coherent gate. A28's
passing numeric suite must not be described as a complete scale-appearance pass.
The original defect images must remain available even after a later repair.

## Header and preset text measurements

The [font measurements](../development/2026-11-14-interface-continuation/reports/a28-font-metrics.json)
independently recompute advances from committed atlas records and the inspected
fitting rule. These source-derived budgets agree with A27; they are not physical
DPI or human-legibility certification. The glyph atlases cover printable ASCII
32–126, with `?` fallback for unsupported bytes, and do not perform Unicode
shaping or kerning.

At both minimum and default size, the ten header actions meet the declared
11-logical-unit floor. Dimensional PLAY and six tools use 15; ROTARY fits at
13.257143, SERVICE at 12.146597, and FLAT at 13.333333. Flat presentation uses
11-unit Sans for all ten. The compact title uses 28-unit Serif and the nominal
caption uses 11. All remain logically separate from the body; A27 supplies the
complete responsive rectangle/envelope census.

A narrow preset accidental has a 12-unit hit width and 10-unit label width.
A requested 9-unit D# has 14.625 units of advance and therefore shrinks to
**6.153846**; its conservative glyph height is **4.423077 logical units**.
At 1.5×/2× that envelope is about 6.635/8.846 physical pixels before raster
sampling. C# fits at 6.530612, while natural single-letter caps retain 9. These
labels are bounded but below the compact-text goal. The full focused semantic
footer caption uses 10.5 logical units; it is useful context, not a substitute
for resolving the small-cap readability finding. **A34 owns that separate work.**

## All 28 Service values and their row budgets

Minimum cards are approximately 302.667×239.5 logical units, with 284.667 units
of text width; default cards are 409.333×339.5, with 383.333 units of text width.
Minimum labels/badges/summaries use 10, values 10.5; default labels/summaries use
11, values 12, badges 10. Values use a 1.25× line pitch without font shrinking.
The fixture contains unequal bank memories, held counts 2/1/1, expression
0.456789, source-46 value 442.125 Hz and gain 0.0123456. These are injected display
inputs, not measurements or application-device observations.

Every required row is represented below. The line count is the same at minimum
and default for this fixture. Full coordinates, actual strings and remaining
vertical margins are in the [56-row record](../development/2026-11-14-interface-continuation/reports/a28-service-layout.json).

| Card | Required rows checked | Value lines per row |
| --- | --- | --- |
| Generator | `generator.model`, `generator.sources`, `generator.tone46_hz`, `generator.output_gain` | 1, 1, 1, 1 |
| Contacts/routing | `contacts.model`, `contacts.upper_held`, `contacts.lower_held`, `contacts.pedals_held`, `contacts.inventory`, `contacts.pedal_model` | 1, 1, 1, 1, 1, 1 |
| Scanner | `scanner.audio`, `scanner.research_model`, `scanner.physical_capture` | 1, 1, 1 |
| AO-28 | `ao28.circuit`, `ao28.percussion_model`, `ao28.specimen`, `ao28.voltage` | 1, 1, 1, 1 |
| Leslie | `leslie.audio`, `leslie.target`, `leslie.horn_speed`, `leslie.drum_speed`, `leslie.microphone` | 1, 1, 1, 1, 1 |
| Retained controls | `controls.upper`, `controls.lower`, `controls.banks`, `controls.pedals`, `controls.expression`, `controls.percussion` | 1, 1, **2**, 1, 1, 1 |

The bank string wraps once and preserves all four memories. No measured value
line exceeds its vertical budget. The tightest minimum-card budget is the final
percussion line, which ends 4.625 logical units before the reserved seven-unit
summary guard; at default the corresponding margin is 25.100. This establishes
bounded complete values for the named fixture. It does not prove every future
wording, every invalid-state string, every individual glyph, or human readability.
A23 owns inspection semantics; the unpainted-row visual issue above remains open.

## Retained proof and next steps

The two images total **669,453 bytes**. Each is 1440×1050 physical pixels for a
960×700 logical model at 1.5×. They are **injected native renderer frames, not
full application screenshots**. The [image record](../development/2026-11-14-interface-continuation/reports/a28-proof-images.json)
retains original BMP, decoded-pixel and PNG hashes and verified lossless
conversion. Only this assignment's redundant BMPs were removed.

- [Injected Play frame, including visible scaled focus and surface gaps](../development/2026-11-14-interface-continuation/reports/a28-injected-renderer-play-960x700-at-1p5.png)
- [Injected Service frame, all 28 values and visible surface gaps](../development/2026-11-14-interface-continuation/reports/a28-injected-renderer-service-960x700-at-1p5.png)

A31 should repair fractional strip coverage and retain before/after evidence
from newly identified source. A34 should improve the tiny preset legends while
preserving hit inventory and semantic focus. Root owns the coherent suite,
actual application gallery refresh, shared status and publication. No A28 commit
or stage occurred. GPU/native display/DPI behavior, screen readers, devices,
physical fidelity and literal atlas-image equality remain separate gates.
