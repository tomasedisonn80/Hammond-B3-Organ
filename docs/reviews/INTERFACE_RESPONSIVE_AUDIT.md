# Responsive ordinary-control and inventory audit

Actual worker: `/root/w05_a27_responsive_inventory`, A27 of the current
sixty-worker interface continuation. **The ordinary-control geometry audit
passes; preset-label readability remains open for A34.** No production source,
CMake file, build tree, sound state or parameter identity was changed.

The [machine-readable result](../development/2026-11-14-interface-continuation/reports/a27-responsive-inventory.json)
retains the counts, coordinates, font samples and source identities. The
[reproduction note](../development/2026-11-14-interface-continuation/session27-responsive-inventory.md)
names the exact probe and commands. This result applies to the identified
working overlay on published HEAD `5d81199a9822874b55f3b0a124715cbd6eadf0e5`,
not to HEAD alone or to later renderer changes.

## Scope and independent method

Read the standing instructions, full project plan, current scope/checkpoint,
[workspace contract](../INTERFACE_WORKSPACE_CONTRACT.md),
[geometry contract](../INTERFACE_GEOMETRY_CONTRACT.md), current
[operating guide](../INTERFACE_RUNBOOK.md), and A18/A19 acceptance. Inspected
all eight actual gallery PNGs with the image viewer, including minimum Play,
Flat, Service and Rotary; also inspected the unchanged atlas reference.
The [gallery](../../examples/demos/standalone-interface-preview-v1/README.md)
records actual SDL dummy-driver/software-renderer captures from executable
`005db1e2006bd1929e07dff3acaa40a5a6e6fa60a2bc8f07eb992d972b04b364`.
This assignment did not launch another native process or recreate that gallery.

The retained C++ probe exports actual `make_ui_layout` ordinary-control
rectangles and `ui_hit_test` responses. A separate Python audit checks panel,
control, label, value, track and paint-envelope composition using independent
rectangle arithmetic with a 0.001-logical-pixel tolerance. Atlas glyph metrics
and the inspected centered-text fitting rule give effective font sizes and
conservative glyph envelopes. These are source-derived measurements, not
physical-pixel, physical-DPI or human-legibility certification.

Nine sizes × three workspaces × two presentations produce **54 layouts**:
960×700, 1280×900, 1672×941, all four 1399/1400×819/820 combinations,
8192×700 and 960×8192. One edited-bank combination, Upper A/Lower B, suffices
for this rectangle audit: bank identity does not change these rectangles.
A18 already tests bank/visibility/focus behavior; A19 already independently
qualifies all 147 playing-key shapes over 288 layouts. Neither proof is repeated
or claimed as newly executed here.

## Inventory and measured result

| Ordinary-control family | Retained records | Visible in Play | Visible in Rotary/Service |
| --- | ---: | ---: | ---: |
| Play / Rotary / Service tabs | 3 | 3 | 3 |
| Save / Load / Help / Audio / MIDI / Panic | 6 | 6 | 6 |
| Flat | 1 | 1 | 1 |
| Edit A/B, both manuals | 4 | 4 | 0 |
| Reversed preset octaves | 24 | 24 | 0 |
| Drawbars for the two currently edited banks | 18 | 18 | 0 |
| Percussion choices | 4 | 4 | 0 |
| Expression | 1 | 1 | 0 |
| Pedal mixtures | 2 | 2 | 0 |
| Keyboard target / octave controls | 5 | 5 | 0 |
| **Total** | **68** | **68** | **10** |

Both retained banks per manual remain available through the four Edit controls;
the interface paints nine drawbars per currently edited manual, not 36 sliders
at once. The focus census is **71 in Play** (68 ordinary controls plus three
roving playing-key groups) and **10 in each other workspace**. Service cards
and Rotary inspection rows are read-only body content and add no focus targets.
This is a composition census; A18 remains the actual traversal/transition gate.

Across the 54 cases, all 3,672 retained records and 1,584 visible records have
the expected inventory and unique visible identities. There were:

- 1,584 control-bound and 1,584 label-region containment checks, 450 nonempty
  value-region checks and 378 nonempty track-region checks, all passing.
- 9,504 successful ordinary-control hits: center, four inset exposed corners
  and label center for every visible control. Preset naturals use the exposed
  lower strip for corner/center samples, so intended accidental occlusion is
  not misreported as a defect.
- 1,134 contained drawbar/expression slot and endpoint-cap rectangles. Their
  movement is linear inside these extents; decorative shadows are excluded
  from the interactive-paint claim.
- No unexpected control or primary-panel intersection. The 360 intersecting
  preset pairs are the intended natural/accidental overlaps: 20 per Play layout.
- 2,106 contained control-text glyph envelopes and no overlapping envelopes
  between different control labels/values in the tested text variants. All
  header action labels meet the 11-unit font floor; every non-preset ordinary
  label/value sample is at least 10 units.

The hit checks sample finite locations; they are not an exhaustive per-pixel
proof. Contained regions plus disjoint parent panels exclude an accidental key
occluding a drawbar, Edit button, header action or other ordinary control in this
matrix. All tested label centers are independently reachable by the same
semantic ID. There is no observed clipped control text or unreachable sampled
interactive cap region at these source identities.

## The common header stays above the body

Every one of the ten controls lies in `layout.header`, outside
`layout.workspace_panel`. At a given size the bounds are identical across all
three workspaces and both presentations. The common controls are not substituted
with body controls. Header title/caption glyph envelopes also remain disjoint
from the ten action regions.

The minimum-size header is `[16, 16, 928, 82]`; its workspace body starts at
y=106. Bounds below are `[x, y, width, height]` in logical units.

| Control | 960×700 bounds | 1672×941 bounds, rounded to 0.001 |
| --- | --- | --- |
| Play | `[16, 50, 72, 32]` | `[71.896, 46, 112, 42]` |
| Rotary | `[94, 50, 72, 32]` | `[191.896, 46, 112, 42]` |
| Service | `[172, 50, 72, 32]` | `[311.896, 46, 112, 42]` |
| Save | `[716, 26, 72, 28]` | `[1314.104, 26, 90, 30]` |
| Load | `[794, 26, 72, 28]` | `[1412.104, 26, 90, 30]` |
| Help | `[872, 26, 72, 28]` | `[1510.104, 26, 90, 30]` |
| Audio | `[716, 60, 72, 28]` | `[1314.104, 62, 90, 30]` |
| MIDI | `[794, 60, 72, 28]` | `[1412.104, 62, 90, 30]` |
| Panic | `[872, 60, 72, 28]` | `[1510.104, 62, 90, 30]` |
| Flat | `[644, 68, 60, 24]` | `[1232.104, 76, 70, 24]` |

At minimum size the title uses 28 units and occupies glyph envelope
`[327.050, 29.600, 304.500, 21.700]`; the nominal-output caption uses 11.
Dimensional SERVICE fits at 12.146597 units, ROTARY at 13.257143 and FLAT at
13.333333. Flat presentation uses 11-unit Sans for these buttons. The JSON
retains the corresponding header positions for all nine sizes.

## Breakpoints preserve Edit controls and preset access

Crossing width 1400 adds the cabinet and narrows the player column. Crossing
height 820 moves Edit A/B from each rack into its manual cheek. All four Edit
buttons, 24 presets and the 18 current-bank drawbars remain visible and
independently hittable on both sides. The preset panels become shorter at the
height transition to make room for Edit; this is a significant usability change
even though no control disappears.

| Size | Cabinet | Edit location | Upper Edit A bounds | Exposed Upper C preset, width × height |
| --- | --- | --- | --- | --- |
| 960×700 | Hidden | Rack | `[28, 218, 76, 26]` | 20 × 19.760 |
| 1280×900 | Hidden | Cheek | `[24, 496, 74, 24]` | 21.714 × 28.880 |
| 1672×941 | Shown | Cheek | `[79.896, 526.760, 69.481, 24]` | 20.423 × 29.062 |
| 1399×819 | Hidden | Rack | `[28, 232.280, 76, 26]` | 21.714 × 32.422 |
| 1399×820 | Hidden | Cheek | `[24, 467.200, 74, 24]` | 21.714 × 20.368 |
| 1400×819 | Shown | Rack | `[72.200, 232.280, 76, 26]` | 20 × 32.422 |
| 1400×820 | Shown | Cheek | `[68.200, 483.200, 68, 24]` | **20 × 16.188** |
| 8192×700 | Shown | Rack | `[84, 218, 76, 26]` | 21.714 × 19.760 |
| 960×8192 | Hidden | Cheek | `[24, 526, 68, 24]` | 20 × 1406.380 |

The narrowest preset accidentals are 12 units wide. At 1400×820 the Upper D#
rectangle is `[102.200, 515.200, 12, 26.412]`; its center `(108.200, 528.406)`
hits D#. The exposed C strip is `[68.200, 541.612, 20, 16.188]`; its center
`(78.200, 549.706)` hits C. These measurements establish usable sample locations
and a six-unit minimum horizontal center clearance for accidentals. They do not
establish a touch-target standard, motor-accessibility result or physical size.

At 8192×700 the first manual drawbar hit region widens to 305.422×100 while
its travel remains 28 units. At 960×8192 the first preset natural becomes
20×3701 and its 12-unit-wide accidental becomes 2294.620 units tall. Both
extremes retain bounded geometry and the ordinary-control inventory. Their
disproportionate geometry is not evidence of good interaction on an extreme
display; no extreme native screenshot or rendering-throughput claim is made.

## Open readability finding: preset accidental labels

**A34 must address or explicitly retain this issue before the final handoff.**
The geometry pass does not close the contract's readable-label goal. A22 already
flagged small reversed-preset labels qualitatively; this audit supplies exact
measurements for that retained limitation.

Reproduce with Play at **960×700**, either presentation. Upper D# has hit bounds
`[58, 424, 12, 32.240002]` and label bounds
`[59, 443.240002, 10, 11]`. Its requested 9-unit Sans has advance 14.625 units,
so `centered` shrinks it to **6.153846**. The atlas-derived glyph envelope is
`[59.576923, 446.393829, 9.038464, 4.423065]`. Upper C# similarly shrinks to
6.530612. Natural single-letter preset labels retain size 9. The same narrow
font sizes remain at 960×8192 because the cheek width stays 156 units. Simply
making the window taller cannot resolve this label-width constraint.

The small legend is contained and its label center hits the correct control;
the issue is readability, not clipping or incorrect ownership. A focused preset
has a full semantic 10.5-unit footer caption in the renderer. The inspected
gallery visibly demonstrates full focused drawbar and workspace captions, but
this audit does not claim native pixels for every possible focused preset.
A28 separately owns full native scale/text verification.

A useful repair must preserve the 24 preset IDs, actual hit geometry and focus
labels. Options are a dedicated legible legend/readout or a separately reviewed
cheek/preset layout change. Keeping the same font and a single line requires
roughly a **210-unit cheek for a 9-unit D#**, or **229 units for a 10-unit D#**,
instead of 156: `(font advance + 2) × 7 / 0.6 + 16`. A wider cheek would consume
manual width at the minimum and therefore needs new responsive/key acceptance.
Do not enlarge only the painted text into an adjacent preset or merely relabel
this measured shrink as a pass.

## Source boundary and remaining gates

Core audited hashes are `UiModel.cpp` `c536c460…`, `UiModel.h` `1c51aaa4…`,
`InstrumentView.cpp` `5f5f209d…`, `Drawing.cpp` `84b91089…`, and `FontData.h`
`f1a3121a…`; complete SHA-256 values and before/after equality are retained in
the report. The probe compiled with GCC 14.2.0 and all project warning flags,
including conversion/sign/shadow warnings as errors. It compiled current
`UiModel.cpp` directly and reused unchanged support/core archives read-only.

No hidden-input, ownership, homography or full focus-transition tests were
rerun. Those remain the source-qualified A18/A19 results. Modal layout and
Service/Rotary text wrapping, scaled native rendering, persistent pointer
capture, physical devices, native accessibility and deadlines remain their
separate gates. The original source concept and actual gallery still differ
in row heights, cabinet composition, material/lighting detail, labels and the
correct full manuals, presets and pedal inventory. **Literal 1:1 reference
fidelity is not established.**
