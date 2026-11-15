# Next whole-reference material work

**A38 prospective proposal, 15 November 2026.** Literal whole-interface **1:1
remains unmet and unwaived**. These are proposed future criteria, not newly
discovered passes for existing pixels. Independent review must freeze the
candidate, measurements and tests before implementation.

## Independent review conditions

The [A41 review](../reviews/WHOLE_REFERENCE_MATERIAL_NEXT_REVIEW.md) accepts this
direction for protocol authoring only. Before implementation, freeze a new narrow
physical mask from the candidate's actual fill/gradient rules; preserve child draw
operations and semantics while accounting for blended pixels over changed
backgrounds; retain unrounded metric inputs and reference-size scope; and declare
bounded deterministic grain work plus renderer-state restoration. The broad v2
composition mask cannot qualify this smaller material change.

## Inspected basis and aligned composition

Directly viewed the original and both admitted full application frames. File
identities were independently rehashed:

| Input | SHA-256 |
| --- | --- |
| [Original 1672×941 JPEG](atlas-cover-reference.jpg) | `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187` |
| [Actual reference-size PNG](../../examples/demos/whole-reference-layout-v1/images/play-reference-1672x941.png) | `f554c348a4dc63901726d8e297c0808ee942052a40babccf2333ef8111be3eae` |
| [Actual minimum-active PNG](../../examples/demos/whole-reference-layout-v1/images/play-minimum-active-1400x820.png) | `416203fa55e808b635b8c64a9cb67033adc2d5462203d90d453a18108925735c` |

[A32 admission](../reviews/WHOLE_REFERENCE_GALLERY_ADMISSION.md), its
[audit](../development/2026-11-15-execution-continuation/reports/A32-gallery-admission.json)
and [provenance](../../examples/demos/whole-reference-layout-v1/provenance.json)
bind the captures to executable `eb9a501e…823c`, base `33fa95d5` **plus its
production overlay**, controls and replays. They qualify dummy-SDL/software
output, not physical-display behavior.

Keep the [canonical contract](../WHOLE_REFERENCE_LAYOUT_CONTRACT.md): performance
y125–264, percussion bounds y177, racks y269–508, below-rail footage, manual
starts y548/y718, and relocated toolbar/pedals. These allocations already align;
bright faces, outlines and shadows are separate measurements. At reference size,
the decorative cabinet rectangle `(1132,174,466,397)` exactly matches all 185,002
original RGB pixels. Preserve that crop and minimum-size aspect containment.
Neither establishes equality of its surrounding header/status or the full UI.

## Ranked visible residuals

Coordinates below are canonical regions, not new hit bounds. Rank reflects
visible consequence and implementation order, not a similarity score.

| Rank | Actual region | Remaining difference and next treatment |
| --- | --- | --- |
| 1 | Racks `(72,269,1044,239)`; performance `(72,125,1044,139)` | Native metal is brighter and laterally uniform; wells, rails and cap shadows look sharply rectangular. Reference illumination varies across textured charcoal and softened recess edges. Begin with one metal surface; qualify wells and cap bevels separately. |
| 2 | Upper/lower manual panels `(232,528,890,170)` / `(224,698,898,172)`; preset cheeks to their left | Native naturals have broad pale faces, abrupt brown fronts and repetitive edge lines; accidentals lack the reference's graded reflections. Add directional top/front shading, contact shadows and narrow edge highlights using existing quads. Apply the same material language to all 24 real reversed presets without changing selection/pending cues. |
| 3 | Rim `(48,510,1074,18)`; plinth `(16,887,1640,54)` | Native straight repeating brown bands lack the reference's irregular walnut grain and localized polished highlights. Use deterministic, spatially varied grain and a continuous light field; preserve live footer visibility and existing side-art identities. |
| 4 | Title around x600–1068/y20–54; footage rows y467–490 | Native title strokes are thinner and less sculpted; footage fractions have different spacing and baseline rhythm. Compare glyph silhouettes, stroke weights, tracking, baselines and emboss shadows separately. Keep live measured text and all nine correct labels, including `1 3/5'`; do not copy the erroneous reference lettering. |
| 5 | Cabinet header/lower panel y125–173/y571–870; utility header x1228–1594 | Reference mic/speed/preset widgets differ from actual tools, toolbar, status and pedals. Refine borders/type density while retaining truthful content. These semantic differences remain explicit residuals; decorative controls cannot be presented as connected scanner/Leslie features. |

At 1400×820 the layout remains intact, but small footage, preset and status text
requires separate native-display review. Enlarging or thinning text solely to
improve a screenshot statistic is not sufficient acceptance.

## First candidate: Upper rack inner metal only

After independent admission, assign a painter owner
[`InstrumentView.cpp`](../../apps/standalone/InstrumentView.cpp): add an opt-in
inner-surface treatment used only for `layout.registration_panels[0]` inside
`paint_reference_composition`. Replace that panel's inset gradient/grain with a
deterministic lateral/vertical light field and nonperiodic fine grain. Keep its
outer shadows, rounding, borders and screws, all children, other panel calls,
`UiModel`, font data and reference artwork unchanged. The candidate changes
neither wells/caps nor typography; subsequent candidates own those separately.

The intended paint allowance is the mapped inner rectangle **`(76,273,520,231)`**,
intersected with the caller's clip. An independent checker must derive physical
coverage from mapped endpoints and actual raster rules before authoring, with
at most one outward device pixel. No mask may be learned from the resulting
diff or expanded to the whole composition. Restore renderer state after painting.

### Independent measurements to freeze

A38 read decoded RGB bytes without modifying images. Use half-open rectangles
and **Y′ = 0.2126R + 0.7152G + 0.0722B**, on 0–255 encoded channels. This is an
image statistic, not physical luminance. Texture RMS is the residual after
least-squares fitting `a + bx + cy` within each patch.

| Quiet patch `(x,y,w,h)` | Reference mean Y′ / RMS | Admitted native mean Y′ / RMS |
| --- | --- | --- |
| Left `(88,320,18,128)` | 18.291 / 1.377 | 31.841 / 0.487 |
| Right `(572,320,14,128)` | 25.323 / 1.563 | 31.819 / 0.622 |

Proposed candidate screens: each mean within **2.0** of its reference value;
each RMS within **0.4**; right-minus-left mean within **1.5** of **7.032**. These
are prospective engineering tolerances for one surface. Independent full-frame
inspection must also reject visible periodic grain, seams, banding and impaired
text contrast. Matching these local statistics, a palette or a global similarity
score cannot establish material identity or literal 1:1. Retain spatial
difference data and all failed measurements.

## Captures, tests and decision before implementation

Freeze genuine before/after executable, source-overlay, dependency, state, replay
and decoded-pixel identities. Use identical deterministic `UiModel` and
`InstrumentViewInfo` snapshots for pixel comparisons; independently advancing
runtime counters are unsuitable for exact equality. Actual application captures
must additionally replay the admitted scene: Upper 60/64, Lower 67, pedal 3,
retained Upper B 16-foot 7→8 with fixed C# sounding, expression 0.75, mixtures
8/0 and On/Second/Normal/Slow percussion. Preserve original galleries.

Predeclare paired reference/minimum-active/1920×1080 cases at renderer scales
**1/1.5/2**, origin and offset **(13,17)**, full clip and clips crossing every
candidate edge. Freeze drawbar **0/4/8**, adjustable/fixed routes, desired/applied
pending state, focus and held-note cases. Include exact threshold neighbors
1399×820 and 1400×819, compact 1280×900/960×700, Flat, Rotary and Service.

Before the production edit, independently add the narrow surface/mask assertions
and demonstrate the existing baseline's recorded result. Root then builds
coherent inputs and runs geometry/input, material acceptance, product visual,
scaled-view, preset/percussion raster and affected waveform-material suites;
required selections use `--no-tests=error`. Preserve old expectations and actual
failures when introducing a versioned candidate fixture.

Accept only this scoped candidate when local criteria and full-frame review
agree, changes escape no declared active allowance, all inactive pixels remain
identical, and all **68 controls / 147 playing keys / 47 parameter meanings**,
24 presets, 71 Play focus stops, ownership/releases and state readers survive.
Require correct 0-at-top/8-toward-player travel, percussion domains and
stored-enable versus applied-eligibility cues. Reject hidden functionality,
baked control lettering, obscured focus/status, disconnected controls presented
as working, or weakened criteria. Failed/inconclusive results remain failures;
revise the next proposal openly. Root's later source-bound captures, independent
admission and coherent/platform gates precede publication. Whole-interface 1:1,
display usability, accessibility and audio fidelity remain separate open goals.
