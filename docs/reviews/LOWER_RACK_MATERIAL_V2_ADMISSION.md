# Independent admission — Lower material sampling amendment v2

**Decision: admit the exact sampling amendment for versioned checker integration.**
Reviewer A22 (`/root/w04_a22`), 2026-11-16, independently admits
[the amendment](../design/LOWER_RACK_MATERIAL_V2_AMENDMENT.md), SHA-256
`b2ebad8944a31ac6e631f457507017dfac1c6191c721fb961c7adafe9b659695`.
This corrects three measurement rectangles and adds foreground-preservation
checks. It does not accept the original v1 numerical result, qualify the entire
candidate, authorize a painter/support/threshold change, or meet whole-interface
1:1. A24 may implement this exact protocol extension; root owns integration and
candidate acceptance.

I read the complete standing `AGENTS.md` and M0–M9 plan, frozen v1 contract and
admission, A16 implementation review, the amendment, A17 complete report and
summary, and relevant source/checker paths. The independent
[audit source](../development/2026-11-16-conversion-material/reports/A22-independent-sampling.py)
imports no A16/A17 or painter helper. Its
[complete result](../development/2026-11-16-conversion-material/reports/A22-independent-sampling.json)
records every original and corrected comparison, reference/before/candidate
statistics, guarded glyph boxes, all protected coordinates, and identities.

## Why exactly these rectangles are justified

`UiModel.cpp` fixes Lower drawbar centers at 685,734,782,830,878,927,975,1024,1074.
The unchanged `reference_drawbar` derives the last slot from track
`(1072,327,4,118)`, cap height32 and slot width42: `(1053,311,42,150)`.
Its opaque right border is the explicit rectangle `(1094,311,1,150)`, RGBA
`[36,34,30,255]`. `Drawing::rounded` and the contained shaft/cap/shadow operations
remain within their source envelopes. The original assertion that every primary
patch avoids wells is therefore false.

| Primary patch | Frozen v1 xywh | Admitted v2 xywh | Border pixels in v1 | Complete column removed |
| --- | --- | --- | ---: | ---: |
| right | 1094,320,14,128 | 1095,320,13,128 | 128 | 128 pixels |
| right_top | 1094,298,14,14 | 1095,298,13,14 | 1 | 14 pixels |
| right_bottom | 1094,460,14,20 | 1095,460,13,20 | 1 | 20 pixels |

Half-open boundaries apply throughout. The correction preserves each y, height
and right edge1108. It is the smallest whole-column removal that keeps each
sample a rectangle and excludes this fixed foreground edge. The short patches
also lose13 and19 otherwise unobscured pixels because a rectangular sample
cannot remove only their single contaminated pixel. This is disclosed; neither
the patch boundary nor the threshold was selected from candidate pixel deltas.
The seven other rectangles, primary/descriptive classification and all35 limits
remain unchanged.

Before either native capture, my audit derived all nine slot envelopes, four
focus strips, panel edge/screw/heading-rule bounds, and68 glyph destinations from
the actual Sans/Serif atlas metrics and binary32 text placement. Each glyph
destination has an additional one-pixel guard on all sides. All seven corrected
primary patches have zero slot, focus, guarded-glyph or other enumerated Lower
decoration intersections. The three descriptive bottom patches also avoid slots
and glyphs. The middle descriptive patch retains the known16 focus pixels; its
statistics remain descriptive, not material acceptance criteria.

This amendment was written after the original failure and a known passing
diagnostic. It is not a blind or preregistered candidate acceptance. The
source-derived explanation, minimal rectangle correction, unchanged limits and
stronger foreground guards justify the explicit versioned amendment.

## Independent native and numerical evidence

I invoked only `--case 28` on the genuine before executable and the already-built
current Lower executable, at1672×941 with scale1, origin0, B route, level4,
held notes, no pending state and Lower index4 focus. Complete header bytes match.
Source and binary identities were checked before and after execution. Six
unchanged drawing/control function slices were also compared byte-for-byte to
the genuine before source. The report binds model, drawing, font, fixture,
reference, contract, comparator and executable hashes.

- All150 pixels at x1094,y311..460 are identical before/current and exactly
  `[36,34,30,255]`, including the20 border pixels outside the original samples.
- All16 pixels at x855..856,y492..499 are identical before/current and exactly
  `[165,228,223,255]`. These follow the2-pixel outline of focused bounds
  `(855,309,46,197)` and stay in the unchanged112-pixel descriptive witness.
- The original JPEG decoded RGB identity matches the frozen reference. No
  resampling, registration, color normalization, gamma transform or smoothing
  occurred. Means/slopes use exact rational arithmetic; population plane
  residual variance comes from explicitly summing each fitted residual square.
  RMS acceptance uses an exact rational inequality, not rounded display values.
- Frozen v1: before7/35, candidate33/35. The candidate still fails right
  residual RMS, error1.865211887973828 versus limit0.5, and right x slope,
  error`3026571/8320000` versus limit`3/50`. All35 original outcomes remain
  present, and140 exact original before/candidate statistics match A17.
- Amended sampling reproduction: before6/35, candidate35/35. Corrected right
  RMS is reference1.4651208997940872 and candidate1.5931857180553533; corrected
  right x slope is reference`-208497/1820000` and
  candidate`-15406427/116480000`. This is a two-capture protocol reproduction,
  not a new full98-pair run or full-frame visual acceptance.
- Canonical source support independently reduces to
  `[604,1112) × [273,504)` after enumerating all1485 old grain pairs and bounding
  all4608 new marks by their source modulo ranges. The unchanged one-device-pixel
  expansion gives118830 allowed pixels. The capture pair changes58229 pixels,
  with zero changes outside that allowance.

## Comparator extension review and requirements

I found no blocker in the existing v1 support or result separation that prevents
A24 from extending it. The checker derives binary32 grain fill boxes and gradient
boundaries from operations, asserts each grain box is inside the gradient for
the finite98-case matrix, expands the union once by one physical pixel, and
then intersects viewport/output/clip. It writes its mask before paired pixel
streams. It does not learn an allowance from differences. It compares RGBA,
complete metadata, protected children/focus and whole frames when required.

Its `preservation_passed` is captured before adding the material screen. The
retained report therefore correctly says98/98 preservation passes,37 required
whole frames identical, zero escaping pixels/channels, but **overall v1 failed**
with97/98 combined case passes. I verified the retained report/mask and all five
failure-image identities. The report SHA remains
`1db2294e250a36aa73d0a354b264656eff3d1e5f292628bc2c7c28e560b623ed`;
the existing full98 evidence is reused here, not represented as a fresh A22 run.

A24 must preserve that original report, comparator snapshot, all35 original
outcomes and failed v1 status; expose v2 rect/stat/screen results separately;
bind this admission and the exact amendment hash; recompute reference and
before metrics at the corrected rectangles; and enforce the full150/16 guards
against both equality and expected source colors. The native fixture's v1 name
and32 cases stay unchanged because the input matrix did not change. Support,
thresholds, painter, all98 preservation obligations, resource limits and failure
artifacts stay intact. A v2 numerical pass cannot silently convert the retained
v1 result into a pass. Root must combine the versioned checker evidence with
the unchanged paired/native/source/visual evidence for any scoped acceptance.

## Reproduction, identities and remaining gates

From `/workspace/scratch/0d55e62af118/Hammond-B3-Organ`:

```sh
python3 -B docs/development/2026-11-16-conversion-material/reports/A22-independent-sampling.py
```

Executed successfully with Python3.12.14 and Pillow13.0.0. No configure/build,
full98 rerun, production mutation, commit or push was performed. Live HEAD was
`a411268fd498f65c083203137831bf5afed83bd8`; the root-owned candidate overlay was
present. The report freezes the exact inputs and fails if they change.

| Evidence | SHA-256 |
| --- | --- |
| A22 audit source | `40f73638758ca75858b70a22f09f9ec00586fc9ee6a336f1725f7011ff4352b3` |
| A22 audit result | `370a5a3f4445c4a01aed1ddb385a7fc6615da8a725061bb200c528680d873371` |
| Current painter | `45b710a9c207f456701732f55ec1086487d63bdb9a8b6ed995f4de12cd5bdb10` |
| Genuine before RGBA | `9b14823952a726017f5cf4aac5597abb03066d1799bcf74a40939039a3c78dd6` |
| Current RGBA | `68e55a46b93ee72462326bad4acbe74343e6e14c5fd8440ec5937b24e56f265c` |

Next: A24 implements and adversarially verifies the exact extension; root accepts
the integrated Lower stage before making a genuine next-stage baseline. Whole
interface1:1 remains unmet and unwaived, including the lower reflected warmth,
mixed-footage typography and other existing residuals. Real-display/DPI/input,
semantic accessibility, hosted sanitizers and platform/device acceptance remain
separate gates. This sampling admission supplies no audio or physical-fidelity
acceptance.
