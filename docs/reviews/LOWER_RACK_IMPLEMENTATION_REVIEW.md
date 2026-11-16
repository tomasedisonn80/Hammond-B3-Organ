# Lower-rack implementation and sampling review

**A16: the bounded painter conforms to its admitted source contract.** Direct
inspection of the actual full frames found no new visual blocker within this
surface. This is **not material acceptance**: the original v1 candidate fails
two of35 numerical screens, and the complete98-pair comparison remains a
separate gate. A source-derived sampling correction is proposed for independent
review. Original v1 criteria, results and failure remain unchanged; literal
whole-interface **1:1 remains unmet and unwaived**.

## Inputs and independent work

A16 read the complete standing instructions, M0–M9 plan, current session scope
and checkpoint, v1 material contract/admission, the live source diff and relevant
geometry/drawing/font code. Live HEAD was
`a411268fd498f65c083203137831bf5afed83bd8`, tree
`37e37d8e038675597b4851961ee698168de435d5`, with root's recorded working overlay.
The owned [audit script](../development/2026-11-16-conversion-material/reports/A16-lower-source-protocol-audit.py)
and [receipt](../development/2026-11-16-conversion-material/reports/A16-lower-source-protocol-audit.json)
retain source, executable, metadata, decoded-pixel and exact measurement facts.
They import no painter, A08/A11 measurement helper or candidate checker.

| Input | SHA-256 |
| --- | --- |
| Genuine before painter | `30ac6cec988ec1834f36456d25d1e53113642071d844d53f81b62b3474cf2c37` |
| Reviewed candidate painter | `45b710a9c207f456701732f55ec1086487d63bdb9a8b6ed995f4de12cd5bdb10` |
| Frozen v1 contract | `84e3c95b4844861ffee71217ced99dbdb52bfb3216b44f4d2817c462cadccb91` |
| Genuine before Lower fixture executable | `1ffcd7e3b70b813e7af2cc5986be0659df93ee0c058ad66f329208d7e11c60ac` |
| Candidate Lower fixture executable | `9206d10ee6b85f6f166a70dd3f01d2536f99560fac369de177d226dd619da3a5` |
| Proposed sampling amendment | `b2ebad8944a31ac6e631f457507017dfac1c6191c721fb961c7adafe9b659695` |

The two already-built native fixtures were each invoked once per audit run with
`--case 28`; before/after JSON metadata matched exactly. Their decoded RGBA hashes
are retained. A16 did not build native inputs or run the32-case or98-pair gates.
Root's separate32-case fixture pass is recorded in its own receipt.

## Source and finite-work review

The only production edit adds the private Lower field/color/painter and material
selector in `InstrumentView.cpp`. Original is the default selector, Upper takes
its existing branch and only `registration_panels[1]` selects Lower. All changed
calls remain inside the existing wide Dimensional Play path. No model geometry,
hit target, control identity, saved state, sound parameter or Engine source changed.

The RGB coefficient table matches v1. Every dependency in the bilinear field,
edge weights, cubic curve and final channel sum follows the frozen parentheses
and calls the unchanged volatile binary64 boundary. Divisions17/508 and497/508
are floating divisions. `std::round`, clamping and alpha255 match the chosen
channel conversion; grain adds its signed amplitude before conversion.

The128 shared edges use the prescribed integer-center boundary. The127 column
indices retain the complete field coordinate through clipping; adjacent spans
share their edge. Row evaluation uses the incoming vertical scale and the
unclipped inset origin/height. Reused raster access observes physical viewport
and clip at scale1 and clips boundaries without renormalizing the material.
Both incoming scales are restored before canonical grain rectangles. The
color guard surrounds all paths and restores saved color, including early exits.
No new texture, viewport, clip-storage or blend mutation is introduced.

The2304 bright/dark pairs, seed `0xB3160A08`, k-order, modulo504/227 origins,
canonical mapping, ±8 amplitude and collision order match v1. Fixed storage is
the128-integer edge array and small value arrays. There is no new allocation,
file access, cache, image buffer, clock or random-device path. For visible inset
rowsR, the helper issues at most **127R+4608 drawing primitives** and **9216 hash
calls**. The admitted boundR≤4028 gives516164 primitives; this is application
work, not an SDL allocation or frame-deadline measurement.

The audit verifies exact bytes for three preserved source regions:9201 bytes of
Upper field/mechanical helpers;10564 bytes of existing wood/heading/drawbar
bodies;14305 bytes covering controls/header/footer before the composition call.
It also verifies the genuine-baseline hashes of UiModel.cpp/.h, Drawing.cpp/.h,
FontData.h and all four original reference-art payload/manifest files. The live
diff preserves the outer panel layers, screws, accents and later children.
These source facts support preservation; independent paired pixels still own
the rendered containment/foreground claim.

## The v1 sampling error and complete patch audit

The last Lower drawbar center1074 and width42 give slot `(1053,311,42,150)`.
Its unchanged opaque right border is `(1094,311,1,150)`, RGBA(36,34,30,255), drawn
after material. It intersects128 pixels of v1 R and one pixel each of RT andRB.
Thus v1's assertion that all seven primary patches avoid wells is false. The
candidate darkens metal next to that retained border; the resulting residual
and slope describe their mixture rather than only the new surface.

The original failed right-strip metrics are reproduced without adjustment:

| V1 right-strip comparison | Candidate signed error | Frozen absolute limit | Result |
| --- | ---: | ---: | --- |
| Plane-residual RMS | +1.865211887973828 | 0.50 | Fail |
| Horizontal slope | −0.3637705528846154 Y′/pixel | 0.060 | Fail |

Independent raw-coordinate exact3×3 normal equations retain all ten patch
statistics, all original35 comparisons and every before/candidate failure.
Mean/slope comparisons use rational arithmetic. RMS pass decisions use the
exact variance inequality for `abs(sqrt(a)-sqrt(b))<=1/2`; the displayed error is
binary64 only. No registration, resampling, color transform or pixel exclusion
is applied to the original measurements.

The geometry audit covers every patch against all nine slot envelopes, the
declared focus and glyph-target envelopes reconstructed from original ASCII
advances/bearings in binary32 with an extra one-pixel guard. No patch intersects
the guarded heading, footage or value glyph support. The three right-patch
intersections above are the only slot intersections. All corrected primary
patches avoid slots and focus.

One descriptive witness has a separate state-related issue: native case28
focuses Lower index4. Its two-pixel left outline x855–856 intersects16 of112
pixels in `(852,492,14,8)`. The receipt preserves that raw statistic and its
identity. It must not be called an unobscured metal sample. A16 checked all150
border pixels and all16 contaminated focus pixels: before/candidate values are
exactly equal to each other and to the unchanged source RGBA colors. The actual
app preview focuses Upper and supplies separate unobscured descriptive bottom
observations, without becoming an identical-state raster fixture.

## Proposed v2, still awaiting independent admission

The separate [sampling amendment](../design/LOWER_RACK_MATERIAL_V2_AMENDMENT.md)
removes x1094 from **all three** right patches, retaining their original right
edge and y extents. This is the minimal complete-column complement of the
source-derived border, with unchanged thresholds, source, support and fixture.
The proposal was written and hashed before A16's own new-patch measurement.
Root's earlier diagnostic was known; neither the proposal nor this review claims
blind selection.

| Separately retained version | Genuine-before result | Candidate authoring result |
| --- | ---: | ---: |
| Original v1 | **7 pass /28 fail** | **33 pass /2 fail** |
| Proposed v2 | **6 pass /29 fail** | **35 pass /0 fail** |

These are authoring observations, not a v2 acceptance result. The new reference
right strip has mean20.49218846153846, RMS1.4651208997940872, horizontal slope
−0.11455879120879121 and vertical slope−0.02941216387531165. Its candidate
values are20.52277848557692,1.5931857180553533,−0.13226671531593406 and
−0.03267268080127618. Exact ratios and sufficient statistics own the comparison.
The baseline gains an additional failure under the correction; no limit was
loosened. All original v1 failures remain failures.

The amendment requires additional complete-border and middle-witness focus
equality checks, explicit versioned results and the original35 comparisons
alongside v2. Independent amendment admission and a separately reviewed checker
implementation are outstanding. A17's v1 checker is deliberately left unchanged.

## Direct full-frame inspection

A16 directly viewed the unmodified original JPEG, the genuine1672×941 before
app PNG, and root's actual changed1672×941 and1400×820 app PNGs. Candidate image
hashes are `053dcd23028e865b3899d95ed10bb0172ec20929a67ad13559bca40e9fd1f74a`
and `1deaebf15d052c38cd418ce1190f5014f5a0fe7d0f1bc355196b240f5078facf`.
The [capture receipt](../development/2026-11-16-conversion-material/reports/root-lower-preview.json)
binds the actual app, painter, commands and dummy-SDL environment.

The Lower panel's rightward darkening is visibly closer to the reference. I saw
no new hard seam, repeating stripe, distracting sparkle or obvious added edge
band in either complete candidate frame. Heading, footage, values and visible
focus remain readable to the same extent in these image inspections; the mixed
footage labels remain visibly smaller than ordinary labels, which is existing
typography work. This is image inspection, not a physical display/DPI journey.

The warm lower reflection is still missing. For the unobscured actual-app bottom
left/middle/right witnesses, reference meanY′ is32.529444/29.123223/22.381538,
while candidate is23.763633/21.353771/18.886071. The title, rack tracking, wood,
keys/cap materials and live-versus-concept control inventory still differ.
No local material score or decorative cabinet agreement closes full-interface
parity or any audio/physical/accessibility gate.

## Handoff

Root may retain the painter's bounded-source review and this scoped visual
finding. Before accepting Lower L1, collect the original98-pair checker result,
independent v2 protocol admission if granted, versioned checker reproduction
including the original failure, foreground/support/state invariants and coherent
affected native tests. Preserve the genuine accepted painter/binaries before
starting typography. No candidate tuning, source amendment, CMake/build, commit
or publication was performed by A16.
