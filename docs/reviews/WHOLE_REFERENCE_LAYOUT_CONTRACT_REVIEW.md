# Whole wide Play layout: independent design admission

**A33, 15 November 2026 — ADMITTED FOR IMPLEMENTATION.** This review admits the
corrected [wide Play composition contract](../WHOLE_REFERENCE_LAYOUT_CONTRACT.md)
at SHA-256
`55cc841d10dc65004cbfcca83d0fb84dcf54dda779e1d82a376534e2650b730f`.
No production layout, rendering, input, regression or platform acceptance is
claimed for the proposed change. Root retains the integration decision and must
assign implementation and independent qualification against this frozen design.
The user's literal whole-interface **1:1 requirement remains unmet and unwaived**.

The design makes a coordinated reference improvement possible: the performance
band, percussion row, rails, manuals and cabinet have explicit common allocations,
and all real controls have a place. It preserves the correct musical domains
where the concept is wrong or shows features that are not connected. This is a
prospective replacement of active geometry, not permission to reinterpret the
older percussion-only proof as evidence for a new whole-body layout.

## Inspected source and evidence

Read all 539 lines of AGENTS.md and all 293 lines of PLAN.md, the active scope and
checkpoint, the percussion contract, A23/A28/A29 notes, the reference-gap review,
and the complete candidate contract and its corrections. Inspected layout,
validation, control construction, hit precedence, focus traversal, resize/mode
transitions, pointer release ownership, header/control/cabinet painting and the
affected test expectations. No source or build mutation was performed.

Directly viewed the [original reference](../design/atlas-cover-reference.jpg),
the [current wide application](../../examples/demos/standalone-audio-preview-v1/images/play-reference-1672x941.png),
the [1400×820 Cancel frame](../../examples/demos/standalone-audio-preview-v1/percussion-states/images/cancel-stored-on.png)
and the [960×700 application](../../examples/demos/standalone-audio-preview-v1/images/play-minimum-960x700.png).
The latter remains outside the proposed active branch. No generated, retouched
or proposed screenshot is presented as application evidence.

| Inspected input | SHA-256 |
| --- | --- |
| Original reference JPEG | `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187` |
| Current wide PNG | `265a6b718ffb85e67be0ea0920bb7b4a40bb5233add71bfd05bec9f55c85f149` |
| Minimum-active Cancel PNG | `b31b2769bda8c52cdd405482017d34de193cd1dee5b9d192a413986c747036df` |
| `apps/standalone/UiModel.cpp` | `aa4fa2e06c4a8ccb17ba1b1cdfed498372b3626152bb2b8c6c53682b775931c9` |
| `apps/standalone/UiModel.h` | `d94e90be25812c6d21b61f37f2b0547704d14866c45fbbb21131ec70b6389bd3` |
| `apps/standalone/InstrumentView.cpp` | `97971753c23e7da93d84586cf66ede2a3d9a04f319ddaf4831ba83ea7955f7d6` |
| Percussion-only contract | `3d7e9414a6159b6c7ad966312f0d11d03ccc9e3122242735ea1df116851735d8` |

Observed local HEAD during inspection was
`688d0cfd1f053671e5c94917d54f2b42533f1fba`. This is an observation of the local
checkout, not a claim that this commit was published. Exact inspected file hashes
above identify the production basis independently of a later publication's
commit metadata. The review did not query or change the remote.

## Concrete findings resolved before admission

| Finding from independent inspection | Corrected design requirement |
| --- | --- |
| Existing toolbar buttons extend to `toolbar.x+440`; the old minimum cabinet status card is only about 369.96 units wide. Its old caption begins at `x+478` with width `toolbar.width-490`. | Two explicit toolbar rows fit the new 448-unit canonical allocation. Caption has its own positive rectangle. All five IDs and actions remain. |
| Existing `paint_cabinet` runs after the toolbar and pedals. Moving them inside the cabinet without changing this order would erase their background, caption and pedal keys; ordinary buttons happen to paint later. | Active cabinet parent/art/status paint before toolbar and pedal children. The old inactive ordering remains literal. Test actual ink and all focused children. |
| Existing refined drawbar painting constructs a material strip between an above-rail label and a below-rail value. Moving footage below while retaining that formula rejects the strip and can suppress the whole control. | The new active painter derives a valid envelope from the declared track/cap travel; all footage, position digits and focus remain independent live layers. Inactive material arithmetic is unchanged. |
| Changing header top from 16 to 10 while retaining `header.y-4.5` would move the already-close title six units upward. | Canonical title text origin is explicitly y11.5; subtitle y67.5. Origins, width budgets, font scale and fitting are separately specified. |
| Canonical-before-scale keyboard construction was initially ambiguous about fixed 22/30-unit offsets and front-depth clamping. | Active keys use canonical side/top/bottom insets 8/20/8, then map complete hit/top/front vertices. Inactive construction remains unchanged. |
| Independently scaling rectangle position and width can create floating-point gaps or overlaps between preset naturals. | Transform shared endpoints and derive extents; test exact shared endpoints, not only approximate rectangle coordinates. |
| Proposed lower manual x212 would put the first-key front at x220, visibly left of the reference's approximately x232–235 region. | Lower manual is `(224,698,898,172)`, retaining right edge x1122; lower cheek widens to 192 and ends at x224. The front now begins at x232. |
| A common old back factor 0.94 gives visibly excessive first-key slopes at the chosen front allocations. | Active Upper 0.96 and Lower 0.95 are declared image-informed choices with the measured limits below. Inactive manuals retain 0.94. |
| “Inset transformed button by 4” and validation of every value/track field were underspecified. | Construct the canonical inset 4 before mapping. Inapplicable value/track fields remain empty; applicable fields must be finite, positive and contained. |

These corrections were incorporated before the admitted hash. They are design
findings, not observed defects in an implementation that does not yet exist.
The existing instrument remains qualified only by its own prior source-bound
evidence.

## Independent reference measurements

### Major vertical landmarks

A read-only RGB row-mean probe supports the visual reading. For performance/rack
boundaries, average the three channels across x80–1099 and examine adjacent-row
differences in y250–282. Strong changes occur at 263/265 and 269/271. Across
x240–1099, the y495–549 range shows strong changes at 510/511 and 518/520; a key
onset appears at 548. The y680–728 range has the manual divider at 699–702 and
another key onset at 719. These are edges of shaded JPEG material, not a recovered
CAD drawing or hit-test specification.

| Landmark | Chosen canonical target | Admission |
| --- | --- | --- |
| Performance band | y125–264 | Consistent with the observed band/divider; enables separate cap legends and eligibility. |
| Percussion outer top | y177 | Removes the previous y150 allocation error by specification; actual painted-body comparison remains required. |
| Rack panels | y269–508 | Consistent with the observed top and shaded base; retains a separate y510–528 rim. |
| Upper key surface start | y548 | Matches the observed onset within edge ambiguity. |
| Lower key surface start | y718 | One unit above the observed 719 onset; within the stated approximately ±2 px visual uncertainty. |
| Cabinet crop envelope | `(1132,174,466,397)` | Reuses the retained crop's canonical placement and aspect; responsive containment remains explicit. |

Exact software assertions use the frozen chosen values and 0.002-unit rounding
tolerance. Artwork-edge uncertainty must not become a looser software tolerance.

### Lower front and separate perspective choices

For each row below, inspect x230–399 and take the first run of five consecutive
pixels meeting each of three channel-wise thresholds: `(140,120,80)`,
`(160,145,100)` and `(180,160,110)`. The unchanged original JPEG supplies every
sample. No new image is created. Threshold agreement is useful corroboration;
it does not make a bright material edge equal to a key's outer hit boundary.

| Manual | Row y | First qualifying x for the three thresholds |
| --- | ---: | --- |
| Upper | 570 | 256 / 256 / 256 |
| Upper | 590 | 252 / 252 / 252 |
| Upper | 610 | 248 / 249 / 249 |
| Upper | 630 | 245 / 245 / 245 |
| Upper | 650 | 242 / 242 / 242 |
| Lower | 740 | 250 / 250 / 250 |
| Lower | 760 | 246 / 246 / 247 |
| Lower | 780 | 243 / 243 / 243 |
| Lower | 800 | 240 / 241 / 241 |
| Lower | 820 | 238 / 238 / 238 |
| Lower | 840 | 235 / 235 / 235 |

For a chosen first-key front x `L`, full keyboard width `W`, top y `T`, depth `H`
and back factor `b`, the left outer projective edge at row y is
`L + W*(1-b)/2 * (1-(y-T)/H)`. Use `(L,W,T,H)=(240,874,548,142)` for Upper and
`(232,882,718,144)` for Lower. Compare this edge with every threshold observation;
do not subtract an estimated material inset or fit away a residual.

| Back factor | Upper RMS across 15 observations | Lower RMS across 18 observations |
| --- | ---: | ---: |
| 0.94 | 6.05256 px | 3.35189 px |
| 0.95 | 3.63925 px | **0.99906 px** |
| 0.96 | **1.86890 px** | 1.63511 px |

The chosen factors' maximum absolute residuals are 2.92394 px for Upper and 1.61875 px
for Lower. This supports the selected visual direction among the inspected
candidates. It is not pixel equality, a physical perspective measurement, a
fitted model of the complete reference, or execution of new application paint.
The original x212 lower allocation overshoots near the front by about 12 units;
its correction is separate from the subsequent slope choice.

## Independent specification arithmetic

Reconstructed all 68 canonical controls directly from the contract's literal
tables, without calling `make_ui_layout` or any production helper. Enumerated
all pair intersections and checked finite, positive, viewport-contained bounds.
For the 12 preset records per manual, the five shortened accidentals intentionally
intersect their two neighboring naturals; all other control interiors are disjoint.
Mapped common endpoints in binary32, derived extents, and checked all 12 shared
natural boundaries exactly at every size below.

| Checked window | Controls | Intentional preset intersections | Unintended control intersections | Exact shared natural boundaries |
| --- | ---: | ---: | ---: | ---: |
| 1400×820 | 68 | 20 | 0 | 12 |
| 1672×941 | 68 | 20 | 0 | 12 |
| 1920×1080 | 68 | 20 | 0 | 12 |
| 1400.25×820.25 | 68 | 20 | 0 | 12 |
| 1672.5×941.25 | 68 | 20 | 0 | 12 |
| 8192×820 | 68 | 20 | 0 | 12 |
| 1400×8192 | 68 | 20 | 0 | 12 |
| 8192×8192 | 68 | 20 | 0 | 12 |

For example, the minimum-active percussion top evaluates to 154.24017333984375;
the corrected lower manual maps to
`(187.559814453125,608.24658203125,751.9138793945312,149.883056640625)`.
The slight differences from the contract's decimal table are below 0.002.
At the reference size the percussion top is exactly 177 and the lower manual
is exactly `(224,698,898,172)`.

The pre-correction scaling hazard is reproducible: separate x/width scaling of
the original proposed upper preset panel `(58,607,164,81)` leaves a 7.62939453125e-6
gap at 1400; at 8192 it can leave a 6.103515625e-5 gap. That illustrative counterexample
is superseded by the contract's shared-endpoint rule, not hidden by its rounding
tolerance. These are arithmetic checks of the specification. They do not qualify
production quads, input, glyphs, clipping, or the complete native interface.

## Focus, hit behavior and musical ownership

Current source constructs 68 ordinary controls, including 24 presets. Its Tab order
walks visible control records then adds one roving stop for each manual and one
for pedals: 71 in Play, 10 outside Play. Stable semantic IDs and unchanged insertion
order can therefore preserve the cycle while controls move. This conclusion
comes from source inspection; no new-layout focus test has yet run.

The existing model remembers the original note owner for pointer/keyboard release.
Resize and presentation/workspace changes cancel an active drag and suppress a
held pointer from acquiring a new target until release. Relocation must retain
these paths and test them against the new geometry. The stepped header positions
when entering/leaving the active branch must not convert a still-held press into
a second action. Preset accidental precedence and playing-key accidental precedence
remain independent; backgrounds, legends and status text add no hit targets.

Correct top→0/bottom→8 drawbar travel, all 47 sound parameters, B3CONTROLS4/readers 1–3,
61+61+25 playing keys, four retained banks and the applied-versus-pending cues are
mandatory. The concept's opposite numeric scale, incorrect DECAY/HARM values,
illustrative preset buttons and unavailable scanner/rotary controls cannot replace
these meanings. The new cheek rows preserve full EDIT BANK and SOUNDING cues;
their actual readability and desired/applied distinction need native evidence.

## Implementation and acceptance gates still open

1. Root freezes this design and explicitly assigns active layout and painter
   ownership, reconciles other sessions' actual remote advances, and preserves
   inactive code paths. No unreviewed shared material/font/Engine change follows
   from this admission.
2. Independently verify real produced parent/control/quad geometry, all applicable
   value/track/label rectangles, extrema, shared edges and transactional failures.
   Cover exact threshold neighbors, fractional and extreme sizes, complete key
   coverage, real control hits and all 71 focus stops. Specification arithmetic
   above is not that execution.
3. Verify real interactions through Session/MIDI ownership: every relocated
   target, held UI/MIDI notes, route/cancel/bank changes, repeat suppression,
   pending/applied cues, original releases and resize/Flat/workspace round trips.
4. Build genuine old/new identical-state native fixtures with common fonts,
   material inputs, renderer and view state. Require exact inactive frames;
   predeclare the active old/new composition envelope with at most one outward
   device pixel. Separately check all semantic glyphs, complete footage, state
   cues, focus, toolbar/pedal visibility, scale 1/1.5/2 and crossing clips.
5. Capture the newly built application at reference, minimum-active, default and
   Flat sizes, with real state changes and moved toolbar/pedal focus. Independently
   compare complete reference/current frames, then refresh README and source
   binding. Retain the old galleries and original failures unchanged.
6. Run the affected coherent native suites and required full/platform gates.
   Prospective active expectations in geometry, projection, percussion/product
   raster and header/material tests must change deliberately. Preserve their
   domain, ownership, clipping, renderer-state and inactive assertions; do not
   disable suites or expand old tolerances to absorb the new design.

No new build, production test, capture, runtime timing, physical display/device
journey or remote publication was performed for this review. The first read-only
pixel-probe command had a scratch Python `SyntaxError` at
`if start is not None and1124-start>=3`; adding the missing space corrected it.
The subsequent source-image probes and eight-case specification arithmetic
completed successfully. This authoring error was not a project/runtime failure.

## Remaining visual requirement

The new design can remove the known percussion allocation error and substantially
improve the whole composition. The supplied concept still has unavailable
scanner/microphone/speed/preset widgets, incorrect text, a different preset
inventory, material shading and type treatment. The usable instrument's truthful
controls and complete manuals/pedals remain visible in their place. New geometry
and source-derived decoration alone cannot establish literal 1:1 equality, native
semantic accessibility, hardware usability or audio fidelity. Those requirements
remain explicit after this design admission and must be reported from actual
subsequent evidence.
