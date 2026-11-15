# Wide Play composition: next reference layout contract

**Draft version 1, 15 November 2026. A32 design proposal for independent review;
no implementation or acceptance is asserted.** This is the next coordinated
composition after the [percussion-only contract](PERCUSSION_REFERENCE_CONTRACT.md).
It prospectively replaces that contract's *active geometry and paint allocation*
when admitted, while retaining its musical, focus and ownership invariants.
The earlier contract, tests, failures and source-specific captures remain history.

The objective is a substantially closer **whole wide Play composition**, including
the currently missing vertical allocation. The user's literal 1:1 requirement
remains active. Exact geometry below is a chosen software specification; shaded
JPEG edges are observations with uncertainty. This proposal cannot turn missing
scanner/rotary features, incorrect concept text, different type or unqualified
materials into a truthful whole-image equality claim.

## Source and ownership

Directly inspected the [1672×941 original reference](design/atlas-cover-reference.jpg)
and [actual current wide application](../examples/demos/standalone-audio-preview-v1/images/play-reference-1672x941.png).
Read the full AGENTS/M0–M9 plan, audio scope/checkpoint, A09/A15/A18/A23/A28/A29,
the [independent gap analysis](design/AUDIO_REFERENCE_GAPS.md), and
[gallery admission](reviews/AUDIO_GALLERY_ADMISSION.md). The source basis is atlas
pp. 409–420 and A05's complete reading; generated labels/counts are not engineering
authority.

| Frozen inspected input | SHA-256 |
| --- | --- |
| Original reference JPEG | `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187` |
| Current wide PNG | `265a6b718ffb85e67be0ea0920bb7b4a40bb5233add71bfd05bec9f55c85f149` |
| `apps/standalone/UiModel.cpp` | `aa4fa2e06c4a8ccb17ba1b1cdfed498372b3626152bb2b8c6c53682b775931c9` |
| `apps/standalone/UiModel.h` | `d94e90be25812c6d21b61f37f2b0547704d14866c45fbbb21131ec70b6389bd3` |
| `apps/standalone/InstrumentView.cpp` | `97971753c23e7da93d84586cf66ede2a3d9a04f319ddaf4831ba83ea7955f7d6` |
| `apps/standalone/Drawing.cpp` | `9b788234405964f6675ab43428735e425b460c8045f2c6eb064c9e19b40a0a5f` |
| Retained reference-art manifest | `bf1bec09c0dd15d09ab0129f950ccb5370532f92cb9217e347ba69e96d24bc87` |

Expected implementation ownership is `UiModel.cpp` and the active branches in
`InstrumentView.cpp`; a small SDK-free geometry helper/header is permissible if
explicitly assigned. `Drawing.cpp`, font data, reference-art bytes, Engine,
parameters, state serialization, device adapters and modal geometry are outside
the change. Root owns source reconciliation, build configuration and publication.
This overlaps other checkouts' rack/deck work: inspect their diffs read-only and
fetch the real remote before publishing. Unpublished work is neither imported
nor overwritten; an unavailable worker is not a new permission requirement.

## Reference observations versus functional choices

These full-image coordinates are visual landmarks, approximately ±2 px at a
well-defined edge and wider where perspective/shading makes the edge ambiguous.
They are not calibration or physical dimensions.

| Area | Observed reference landmarks | Chosen functional treatment |
| --- | --- | --- |
| Header | Tabs near x100/240/380, y50; title glyphs near y20 and subtitle near y71; body ends about y112 | Larger tabs with the same three workspaces; retain all six real tools and Flat. Keep the truthful NOMINAL DRY ORGAN subtitle. |
| Performance | Outer band about y125–264; divider x556; cap bodies near x164/256/337/418, y177–229 | Allocate the full band. Correct PERC/VOL/DECAY/HARM values remain live; the right half keeps expression and both real pedal mixtures. |
| Racks | Top y269–271; bases about y508–511; center divider x600; rails roughly y311–461 | Two adjacent panels, explicit rail centers and footage below. Move EDIT BANK/SOUNDING cues into the matching real preset cheek. |
| Rack horizontal rhythm | Upper cap centers about 158,206,254,302,351,400,449,498,548; lower 685,734,782,830,878,927,975,1024,1074 | Use those chosen centers with 46-unit control columns. All nine correct footage labels and true 0–8 readouts remain present. |
| Manuals | Upper key start near y548; split near y699–702; lower key start near y719 | Keep all 61+61 playable keys and real 12+12 preset keys. Use a shared projective hit/paint construction with starts y548 and y718. |
| Cabinet | Header around y125–173; image around x1132–1598, y174–571 | Reuse the existing 466:397 decorative crop at its exact retained aspect. The lower area contains the relocated keyboard controls, truthful status and real 25-note pedalboard. |
| Lower furniture | Wood rim around y510–528, front plinth around y887–941 | Restore the rim interval; retain the live status/focus/error footer on the lower furniture. |

The image's six scanner tablets, microphone knobs, speed controls and Studio 122
widget do not establish connected capabilities. Do not paint them as active,
disabled-but-selectable or invisible hit targets. No copied control art replaces
live text/geometry. The concept's wrong percussion domains, questionable footage,
illustrative preset inventory and reversed scale cannot change musical behavior.

## Activation, canonical space and shared edges

Activate **only** when workspace is Play, presentation is Dimensional,
width ≥1400 and height ≥820. The maximum remains 8192 in either dimension.
Use the same predicate for layout and all new paint branches. Compact, short-wide,
Flat, Rotary and Service retain their old geometry, records, typography and
pixels for identical state. Their header is unchanged too; only the active Play
header changes. Existing modal layout/state and input capture remain unchanged.

The active composition is authored in a **1672×941 canonical space**. Set
`sx = width / 1672`, `sy = height / 941` in the normal binary32 layout domain.
Canonical rectangles below are `(left, top, width, height)`. Map their common
left/right/top/bottom endpoints, then derive extents by subtraction. **Do not
independently scale a left coordinate and its stored width** when it partitions
adjacent targets: that can create floating-point gaps or overlaps. Reuse common
partition endpoints for neighboring preset naturals and keyboard vertices.
Transform each complete hit/top/front quad from the canonical construction;
derive its AABB from the transformed vertices. Borders do not enlarge hits.

Use the actual `UiLayout` records for input, focus and painting. Make no second
paint-only keyboard or control arrangement. Build a candidate and publish it
only after validation; rejected sizes/banks/workspaces/presentations preserve
the complete destination and focused semantic identity. Validate applicable
value/track rectangles, key quads, label clearance and finite extents as well as
ordinary bounds. Preserve canonical empty value/track fields for controls that
do not use them, including button/preset records; require positive finite extents
only where the field is applicable. Today's `valid_layout` alone does not check
all these new obligations.

The independent horizontal/vertical scaling is a responsive choice, not a
claim that the single reference specifies every aspect ratio. The cabinet crop
is aspect-contained as described below. At extreme admitted aspect ratios,
finite geometry, complete inventory and reachability are required; visual
similarity is assessed at the reference and ordinary desktop sizes separately.

## Canonical parent allocations

| `UiLayout` role | Exact canonical rectangle | Approximate rectangle at 1400×820 |
| --- | --- | --- |
| Header | `(72,10,1528,102)` | `(60.2871,8.7141,1279.4258,88.8842)` |
| Performance | `(72,125,1044,139)` | `(60.2871,108.9267,874.1627,121.1265)` |
| Upper rack | `(72,269,528,239)` | `(60.2871,234.4102,442.1053,208.2678)` |
| Lower rack | `(600,269,516,239)` | `(502.3923,234.4102,432.0574,208.2678)` |
| Upper playing manual | `(232,528,890,170)` | `(194.2584,460.1063,745.2153,148.1403)` |
| Lower playing manual | `(224,698,898,172)` | `(187.5598,608.2465,751.9139,149.8831)` |
| Upper preset cheek | `(48,528,184,170)` | Transform endpoints as specified |
| Lower preset cheek | `(32,698,192,172)` | Transform endpoints as specified |
| Cabinet parent | `(1126,125,478,745)` | `(942.8230,108.9267,400.2392,649.2030)` |
| Relocated keyboard toolbar | `(1140,614,448,64)` | `(954.5455,535.0478,375.1196,55.7705)` |
| Pedalboard | `(1138,752,450,110)` | `(952.8708,655.3029,376.7943,95.8555)` |
| Live footer | `(48,889,1556,36)` | `(40.1914,774.6865,1302.8708,31.3709)` |
| Workspace allocation | `(72,125,1528,745)` | Transform endpoints as specified |

The extended lower cheeks intentionally reach left of the header; they remain
inside the viewport. Cabinet parent now contains the pedalboard and toolbar;
this is decorative containment, not overlapping interactive targets. Rack panels
share x600 and manual panels share y698 as visual borders. No target lies on a
second target's interior merely because its parent panel touches another panel.
The noninteractive wooden rim occupies `(48,510,1074,18)`; retain 2 units above it
after the rack and do not insert the old toolbar into this interval.

The lower manual's chosen front left is x232 (panel x224 plus the 8-unit key
inset). Independent reference brightness-row readings place its lit left edge
around x235 at y840; this is closer than the earlier draft's x220 front. The
material threshold is not hit geometry, and varying shadows remain an explicit
comparison uncertainty. The corrected lower cheek ends at x224 as well.

## All real controls in the new allocation

### Header

The three workspace bounds are `(100+140*i,50,130,46)`, indices 0–2. Save/Load/Help
use `(1312+97*i,25,88,28)`; Audio/MIDI/Panic use the same x values at y61. Flat is
`(1228,78,70,24)`. Retain semantic IDs, tool actions, focus membership and record
order. Construct every button label rectangle by insetting its **canonical**
bounds by 4 units, then map endpoints; do not subtract an unscaled 4 units after
transformation. This applies equally to edit-bank and relocated toolbar buttons.

Keep the title's canonical **text origin y11.5**, centered at x836 in the safe
interval between Service and Save, requested Serif 42.75. Do not reuse
`header.y-4.5`, which would move this already-close title 6 units upward. Keep
the subtitle's canonical text origin y67.5, requested Sans 17 and centered tracked
width at most 374. Map these canonical origins by sx/sy, the tracked-width budget
by sx and the requested font size by f; 374 is not a fixed window-space width.
Fit within the actual tools/Flat allowances. Decorative brass
rules may occupy `(528,40,50,1)` and `(1094,40,108,1)` without crossing title ink.
Requested tab type is Serif 18; tool type is Serif 11.5.

### Percussion and nominal performance controls

Percussion visual order stays `[0,2,3,1]` for PERC/VOL/DECAY/HARM and the four
unchanged parameter IDs. Canonical cap bounds have lefts **164,256,337,418**,
top **177**, width **74**, height **52**. Value rectangles inset left/right by 5,
top by 6 and bottom by 8. Exterior legends are `(x-2,233,78,14)`, requested Serif
13.5; values request Serif 20. Only the cap bounds are targets. The unchanged
selected rule follows stored enable; the copied applied Upper B route determines
eligibility. Heading is `(90,136,448,26)`, requested Serif 15. Eligibility is
`(90,248,448,14)`, requested Sans 12, using the same two truthful messages/colors.
The new active band always has this separate line; no old height-104 branch.

At 1400×820, cap lefts are approximately **137.3206,214.3541,282.1770,350.0000**,
top **154.2402**, width **61.9617**, height **45.3135**. At 1672×941 the y150-versus-
y177 allocation error is removed by construction. A layout assertion is not a
new native capture or proof of the shaded face's exact photographic edge.

The divider is canonical x556, y137–252. The right-side heading is
`NOMINAL EXPRESSION / PEDAL MIXTURES` in `(578,136,514,26)`, requested Serif 14.
Preserve ordinary expression and two pedal-mixture controls:

| Control | Bounds | Label | Value | Track |
| --- | --- | --- | --- | --- |
| Expression | `(578,165,254,85)` | `(582,165,246,16)` | `(582,232,246,16)` | `(594,200,222,4)` |
| Mixture 1 | `(850,165,112,85)` | `(854,165,104,16)` | `(924,200,32,40)` | `(891,193,4,43)` |
| Mixture 2 | `(978,165,112,85)` | `(982,165,104,16)` | `(1052,200,32,40)` | `(1019,193,4,43)` |

Retain their range, drag direction, keys, value meaning and labels. The nominal
mixture cap is 34×22 with a 42-wide slot in canonical space; its complete travel
stays between y182 and247. No apparent scanner selector is added.

### Drawbars and retained/applied cues

Use upper centers `[158,206,254,302,351,400,449,498,548]` and lower centers
`[685,734,782,830,878,927,975,1024,1074]`. For each center `c`, its canonical
control bounds are `(c-23,309,46,197)`, track `(c-2,327,4,118)`, footage label
`(c-23,467,46,23)` and numeric value `(c-23,491,46,15)`. Preserve the current
top→0, bottom→8 mapping and shared source parameter. A 34×32 cap travels with
its center from y327 to445; its 42-wide slot is y311–461. Correct footage uses
`kUiFootageLabels`, fitted completely at requested Serif 19, padding 2; the true
position readout requests Sans 12. A left guide may label **0 at top through 8
at bottom**, centered on those same nine positions, with numbers in x110–125
(Upper) or x638–653 (Lower) and ticks ending before the first control column.
Never reproduce the concept's opposite direction as a live gain scale.

Headings `UPPER MANUAL DRAWBARS` / `LOWER MANUAL DRAWBARS` occupy each rack's
canonical inset `(16,8,width-32,27)`, requested Serif 16. The new active painter
must derive its material envelope from track/cap travel, **not** the old
`label_bounds.y+21` to `value_bounds.y-1` strip: footage is now below the rail,
so that old calculation would reject painting. Retain the existing cap colors,
live held/selection state and focus semantics. No baked lettering.

For each preset cheek `(x,y,w,h)`, put its manual name at `(x+8,y+3,w-16,17)`,
`EDIT BANK A/B` at `(x+8,y+20,w-16,14)` and the current `sounding_caption` at
`(x+8,y+34,w-16,14)`. Requested types are Serif 13, Sans 12 and Sans 12.
Edit A/B buttons are `(x+10+i*(b+4),y+51,b,22)`, `b=(w-24)/2`.
The real reversed preset-key panel is `(x+10,y+79,w-20,h-89)`; its 12 semantic
records and seven shared natural divisions retain their existing meaning.
Selected applied preset and desired-pending outlines remain distinct.

### Manuals, keyboard controls and pedals

Generate canonical playing-key quads with side insets 8, top inset **20** and
bottom inset **8**; use the existing projective construction with active back
factors **0.96 Upper, 0.95 Lower and 1 for pedals**, 0.62 accidental depth, and
the same 36/36/15 natural key counts. Compute front-depth
`clamp(0.14*key_height,6,18)` in canonical space
before scaling. Then transform the complete shared hit/top/front vertices;
do not reapply fixed 22/30 offsets or a fresh front clamp in window space.
The inactive helper retains its original offsets/arithmetic. Upper/lower
canonical playing-key starts are y548/y718, about 477.5345/625.6748 at 1400×820.
Keep natural-first painting, accidental-first hit testing, all 147 note identities,
roving focus and retained note-off ownership.

Independent canonical outer-keyboard anchors are Upper back x257.48–1096.52 at
y548, front x240–1114 at y690; Lower back x254.05–1091.95 at y718, front x232–1114
at y862. A33 checked three brightness thresholds and several source-image rows:
the chosen factors reduce edge RMS from about 6.05 to 1.87 px for Upper and from
3.35 to 1.00 px for Lower compared with 0.94 at the same chosen front allocations.
These are source-art brightness edges, **not hit boundaries or an application
measurement**; the factors are declared visual choices, not physical estimates.
Inactive manuals retain their existing 0.94 factor and exact output.

The moved toolbar is explicitly two rows: Upper/Lower/Pedals bounds are
`(1148+148*i,616,136,26)`; octave down/up are `(1148,648,84,26)` and
`(1244,648,84,26)`. The current octave/target caption is `(1340,654,240,14)`.
This fits the minimum active cabinet; the old 440-unit row and caption offset
`toolbar.x+478` do not. Keep all five IDs, actions, keyboard shortcuts and
insertion order. Requested button/caption type is Sans 12.

The pedalboard parent keeps its explicit `PEDALBOARD / 25 NOTES` heading in
`(1150,755,426,16)`, requested Sans 12, and the same 25 live pedal targets.
Its canonical key surface begins y772 and ends y854. Cabinet art and status
must not cover this panel or its focus outlines.

## Cabinet, paint order, materials and text fitting

Map the canonical art envelope **`(1132,174,466,397)`**, then aspect-contain the
existing 466:397 asset within it, center horizontally and align its top. Thus at
1672×941 the retained source crop's placement matches its exact original crop;
at unequal sx/sy it remains undistorted. The header reads ROTARY CABINET in
`(1143,131,444,31)`, requested Serif 16. The art is decorative and no microphone
or rotor handle is implied.

Place `ROTARY AUDIO NOT CONNECTED` in `(1144,584,442,17)`, requested Sans 12.
Three status rows in `(1144,691,442,54)` show current audio running/configuration,
current MIDI state, and `SCANNER / CHORUS: NOT CONNECTED` at canonical y692/710/728,
each 15 high and requested Sans 12. The separate rotary row plus these three
retain all four truth statements. Detailed devices/errors remain accessible in
their existing dialogs/Service view; untrusted long strings retain explicit
ellipsis, never spill into the toolbar or pedals.

**Required active paint order:** background/furniture; parent panels including
the whole cabinet; cabinet art/heading/truth/status; rack and cheek content;
manuals; toolbar background/caption; pedal panel/keys; ordinary controls and
their focus; footer; modal overlays. Equivalent ordering is allowed only with
the same ownership and no overdraw. In today's code `paint_cabinet` follows both
toolbar and pedals. Merely moving their rectangles would erase their background,
caption and keys; the active call must move before those children. Preserve the
old order literally in inactive modes. Cabinet decoration is not a hit target.

Reuse existing metal, walnut, ivory, brass, cap and key materials. Active scaling
must map material insets/bevel/front/slot metrics with sx/sy, including the new
52-high percussion cap; do not change shared painters' inactive output. A small
active-only helper is preferable to modifying the global button/drawbar material.
Text, values and focus remain separate live layers. This is a composition
contract, **not a newly admitted material/color equality target**: A29's 64×47
reference bright component and color probes remain observations, not hit bounds.
More faithful lighting/bevels require their own declared material comparisons.

For active text, let `f=min(sx,sy)` and scale requested point sizes by f; map text
boxes by sx/sy and use the existing measured fitting rules and scaled padding.
Do not stretch glyph textures anisotropically. Required semantic labels must
retain every glyph and fit their own rows at minimum/reference sizes. The live
footer keeps its exact existing priority rules for recovery/error, pending preset,
focused control, unsaved state and peak. Scale its canonical offsets within the
new footer; do not replace it with DESIGN CONCEPT. Existing colors remain;
focus stays visibly cyan and must not be hidden under another layer.

## Independent acceptance before calling the change ready

1. Freeze the reviewed specification before implementation. Check exact chosen
   parent/control/key landmarks independently at 1672×941 and 1400×820 (0.002
   logical-unit float tolerance), 1920×1080, fractional dimensions, both adjacent
   threshold neighbors and 8192×820/1400×8192/8192×8192. Check actual shared
   endpoints, no control overlap, complete hit coverage, all value/track/label
   bounds, valid cap extrema and transactional invalid inputs.
2. Preserve 47 parameter identities, B3CONTROLS4/readers1–3, 68 ordinary controls,
   147 playing keys, 24 presets and 71 Play focus stops (10 outside Play). Exercise
   every relocated target by pointer and keyboard, focus wrap/reflow, all preset
   routes, desired versus applied/pending cues, held UI and independent MIDI
   owners, repeated Down, cancellation and original releases after resize/mode
   changes. No view change emits a musical edit or restarts audio state.
3. Use a genuine old/new identical-state native comparison. Inactive compact,
   Flat, Rotary and Service frames require **complete exact pixel equality**,
   including headers. The active change spans the listed full composition;
   predeclare a union of old/new parent/furniture/control/text bounds with at most
   one outward device pixel, and report escaped pixels. Do not reuse A23's
   percussion-only mask or call its old 66-pair receipt evidence for new code.
   Independently require correct active literal glyphs, all-nine full footages,
   eligibility, edited/sounding cues, cabinet/toolbar/pedal non-occlusion and all
   focus ink. Cover states, scales 1/1.5/2, offsets and crossing clips.
4. Capture the **actual newly built application** at reference, minimum active,
   default and Flat sizes, with live presets/drawbars/percussion/held notes and
   toolbar/pedal focus. Preserve source/build/executable/replay/state/PNG/native
   pixel identities and compare both complete reference/current frames. Measure
   performance bottom, percussion top, rack top/base, manual key starts and
   cabinet crop placement separately from materials and semantic substitutions.
   The integrator updates README with actual new frames and honest residuals.
5. Run the affected native suites from one coherent build, then the required
   full/platform gates. Record original failures and every legitimate expectation
   migration. A source count, screenshot, synthetic timing or software raster
   cannot close native accessibility, real display/device, audio fidelity or
   literal whole-interface equality.

### Existing tests that need prospective expectations, not weakened invariants

The geometry assertions in `test_standalone_percussion_reference.cpp` deliberately
pin old active caps and active=Flat neighboring allocations; replace only those
active expectations with this contract and keep its domain/interaction/inactive
checks. `test_standalone_reference_layout.cpp` pins old manual/cabinet/pedal
landmarks and a 10-unit separate-cabinet gap; the new nested allocation supersedes
that active gap. `test_standalone_projection.cpp`, `test_standalone_ui.cpp` and
`test_standalone_preset_ui.cpp` need review of canonical-before-scale insets and
shared endpoints. Workspace acceptance must distinguish deliberately changed
active geometry from identical inactive geometry without relaxing continuity.

`test_standalone_percussion_raster.cpp` pins old typography/eligibility locations;
`test_standalone_product_visual.cpp` pins above-rail footage, old state rows and
material envelopes; `test_standalone_material_acceptance.cpp` includes exact
header ink landmarks. Their old-source receipts remain immutable. Migrate active
literal expectations or add a clearly versioned new fixture; keep all semantic,
renderer-state, clipping and inactive gates. Inspect `test_standalone_scaled_view`,
workspace/preset/waveform raster cases and real replay coordinates for affected
active allocations. Do not blanket-disable suites or widen tolerances until they
pass. Root owns CMake/CTest registration and coherent qualification.

## Completion wording and next step

If accepted and implemented, this removes the known 27-unit percussion-row
allocation error at the reference size and reconstructs the larger band/rack/
manual/cabinet relationship while preserving the usable instrument. The supplied
concept still contains controls/words/inventory that the truthful product must
represent differently, and materials/type remain separately judged. Report
**the measured composition improvement and the actual remaining differences**;
do not call this proposal, its later geometry tests or the previous gallery 1:1.
Next: independent A33 review, root's admitted version and assignment of production
and separate geometry/input/raster/capture owners before any source rewrite.
