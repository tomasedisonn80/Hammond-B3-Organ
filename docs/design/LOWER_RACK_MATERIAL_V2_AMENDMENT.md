# Lower-rack material v2 — sampling correction proposal

**A16: proposed protocol correction, awaiting independent admission.** This
document changes no production source, field, grain, support, fixture, threshold
or existing result. Lower v1 remains a failed candidate measurement: its original
35 comparisons and the reason for each failure must remain visible. The proposal
must be independently reviewed before a v2 result can be accepted. Literal
whole-interface **1:1 remains unmet and unwaived**.

Read with the unchanged [v1 contract](LOWER_RACK_MATERIAL_CONTRACT.md), SHA-256
`84e3c95b4844861ffee71217ced99dbdb52bfb3216b44f4d2817c462cadccb91`, and its
[original admission](../reviews/LOWER_RACK_MATERIAL_ADMISSION.md). That admission
reproduced the statistics but missed foreground contamination. This document
does not retroactively make the v1 patch-selection claim true.

## 1. Source-derived cause and minimal correction

The unchanged [UiModel.cpp](../../apps/standalone/UiModel.cpp) places the final
Lower drawbar at center x1074, track y327 with height118. The unchanged
`reference_drawbar` in
[InstrumentView.cpp](../../apps/standalone/InstrumentView.cpp) gives manual slots
width42 and cap height32. Its slot is therefore `(1053,311,42,150)`. A later
opaque right-border rectangle is `(1094,311,1,150)`, RGB **(36,34,30)**, alpha255.
This rectangle is foreground drawn after the Lower material, not the metal
surface. At canonical size and renderer scale1 it owns x1094 and y311–460.

All three right-hand v1 patches intersect that border. The v1 assertion that
the primary patches avoid wells is consequently false. The long strip includes
128 border pixels; the top and bottom patches include one each. These are
geometric intersections, independent of candidate RGB and whether a numerical
comparison passes. No other column of those three patches intersects a manual
slot. The correction removes exactly that one complete column while preserving
the previous right edge, y positions and heights:

| Patch | V1 half-open `(x,y,w,h)` | Proposed v2 `(x,y,w,h)` | Removed border pixels |
| --- | --- | --- | ---: |
| R | `(1094,320,14,128)` | **`(1095,320,13,128)`** | 128 |
| RT | `(1094,298,14,14)` | **`(1095,298,13,14)`** | 1 |
| RB | `(1094,460,14,20)` | **`(1095,460,13,20)`** | 1 |

The remaining seven patch rectangles keep their exact coordinates. In particular,
L, LT, CT and LB remain primary, and the three bottom-interior witnesses remain
descriptive. A16 chose the same minimal border-complement rule for all three
right patches before computing their own v2 statistics. Root had already supplied
a passing diagnostic for the cropped long strip; this is **not a blind study**.
The geometry and complete original failures, rather than that diagnostic's
outcome, justify submitting this correction for independent review.

Do not tune the field to camouflage an opaque well border. Do not make a
changed-pixel mask, remove isolated high-error pixels, shift a patch to a
different region, enlarge its right edge, change its weight, or loosen a
threshold. The new coordinates are frozen by this document, not learned by a
checker after seeing candidate differences.

## 2. The same 35 numerical limits on the corrected metal samples

Use original unresampled RGB and the same native **Lower case28**, canonical
1672×941, renderer scales(1,1), origin(0,0), full clip. Preserve exact rational
sufficient statistics and least-squares plane residuals, with
`Y'=(2126R+7152G+722B)/10000`. There is no registration, gamma/ICC transform,
normalization, retouching or alternative decoder. Record file and decoded hashes
and decoder identities as before.

V2 retains every numerical limit from v1:

- For each of the seven primary patches, absolute mean Y′ error ≤2.5 and
  absolute mean error in each RGB channel ≤3.0: 28 comparisons.
- For L and corrected R, absolute population plane-residual Y′ RMS error ≤0.50,
  horizontal-slope error ≤0.060 Y′/pixel and vertical-slope error
  ≤0.025 Y′/pixel: six comparisons.
- Absolute error in corrected-R-minus-L mean Y′ ≤1.75: one comparison.

Recompute the reference and genuine-before statistics at the three new
rectangles; copying the old right-strip reference values into these comparisons
is invalid. Preserve exact ratios, sums and unrounded comparisons; displayed
decimal rounding cannot decide a pass. The reference images, painter constants
and fixture bytes are unchanged. The complete 98-pair support/foreground/state
requirements, visual rejection criteria and coherent affected gates remain
unchanged.

## 3. Required retained v1 failure and new foreground checks

Every v2 report must still contain **all original 35 v1 comparisons for the
genuine before and candidate**, with original rectangles and limits, and their
original failed status. Store v2 under a separate version/key with its amendment
and review hashes. Do not overwrite the v1 report or report “35/35” without its
version and the retained v1 result. Both old and new right-patch statistics must
remain inspectable. The complete ten original descriptive records also remain.

In addition to existing opaque-child/focus preservation checks, compare the
source-derived excluded border at **all150 pixels** `(1094,311,1,150)` in native
case28. Require before/candidate RGBA equality and the exact source color
`[36,34,30,255]`. This covers all130 contaminated primary pixels and the other20
border pixels. A change to that protected foreground is a failure, not a reason
to crop differently. The underlying surface's containment allowance is unchanged;
this border equality is an additional assertion inside that allowance.

## 4. All-ten-patch foreground audit and descriptive focus annotation

L/LT/LB lie left of the first Lower manual slot and numbered guide. CT is above
the slot and focus tops. The corrected R/RT/RB start immediately after the last
slot and remain left of the panel border/screws. Footage is below the slot,
separate from the primary corner strips in x; displayed value glyphs are centered
on the drawbars. An implementation review must retain source/pixel evidence for
this audit rather than assuming that any dark patch is unobscured metal.

Native Lower case28 deliberately focuses index4 at center878. The unchanged
two-pixel focus outline on bounds `(855,309,46,197)` includes x855–856 at
y492–499. Thus **16 of112 pixels** of the original descriptive middle-bottom
patch `(852,492,14,8)` are cyan foreground. Keep its raw native statistic and
identify that contamination. It is not a numerical acceptance patch and must
not be presented as an unobscured material measurement. Require those16 pixels
to remain exactly equal before/candidate and equal the source focus color.
Do not change the fixed fixture, focus, witness rectangle or source merely to
obtain a quieter measurement.

The actual application previews with Upper focus leave these Lower bottom
witnesses unobscured. They may retain separate descriptive material observations
with their own source/state/pixel identities, but they are not identical-state
native before/after fixtures. The warmer reference bottom reflection remains an
unmatched visual residual regardless of a v2 primary-patch pass.

## 5. Review and acceptance sequence

1. Retain the original v1 candidate report and lossless failure evidence.
2. An independent reviewer checks the source geometry, all-ten-patch audit,
   exact minimal correction, unchanged limits and added border/focus guards.
   Record admission or rejection against this document's exact hash.
3. A separately assigned checker owner implements v2 explicitly, reproduces all
   v1 outcomes, computes the new reference/baseline metrics, and retains both
   versions without broadening the existing operation-derived mask.
4. Root combines that result with the unchanged 98 genuine pair requirements,
   native invariant suites and full-frame inspection before accepting L1 under
   v2. This authoring proposal and its own calculations do not accept a candidate.

The current painter is frozen at SHA-256
`45b710a9c207f456701732f55ec1086487d63bdb9a8b6ed995f4de12cd5bdb10`.
Any later painter/source or fixture change needs its own source-qualified
evidence. Future typography begins from the then-accepted genuine painter.
Native display/DPI/input/accessibility, physical calibration, audio and complete
reference equality remain separate unfinished requirements.
