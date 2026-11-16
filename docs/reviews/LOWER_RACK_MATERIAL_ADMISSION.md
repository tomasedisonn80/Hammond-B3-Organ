# Lower-rack material protocol admission

**A11, 16 November 2026: admit Lower v1 for the frozen independent fixture and
bounded painter sequence.** The same fixture was frozen before root built and ran it against the genuine
unchanged painter, as recorded below. This is protocol admission, not a candidate, visual, native
display or whole-interface 1:1 pass. The complete original reference and genuine
current baseline frames were inspected; the Lower surface remains visibly too
bright and lacks the reference's rightward darkening and warm lower reflection.

## Frozen identities and independent method

The admitted [Lower v1 contract](../design/LOWER_RACK_MATERIAL_CONTRACT.md) has
SHA-256 `84e3c95b4844861ffee71217ced99dbdb52bfb3216b44f4d2817c462cadccb91`.
The current genuine painter has SHA-256
`30ac6cec988ec1834f36456d25d1e53113642071d844d53f81b62b3474cf2c37`.
The original reference JPEG remains
`9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187`;
root's actual baseline PNG is
`835cfac199afa9a060b765c1c39a80f5819fc5f9b1c583002155ed1eea04b925`.

The [independent audit script](../development/2026-11-16-conversion-material/reports/A11-independent-lower-audit.py)
fits each patch using an exact uncentered 3×3 normal matrix and rational Gauss
elimination, independently of A08's centered sufficient-statistic method. It
reads the author's receipt only after computing all measurements. The
[audit receipt](../development/2026-11-16-conversion-material/reports/A11-independent-lower-audit.json)
retains raw matrices/right-hand sides, sums of squares, exact fractions, decoder
identities, source hashes and every baseline inequality. All **320 rational
statistics**, **80 population residual RMS values** and **two decoded RGB
hashes** agree exactly with A08. No resampling, registration, candidate field,
native build, pixel-mask learning or image write occurs in this audit.

## Arithmetic and support admission

The field has explicit per-operation binary64 rounding, parenthesized
coefficient/correction dependencies, floating divisions for 17/508 and 497/508,
and `std::round` channel conversion. The private volatile binary64 boundary can
be reused without changing global flags or Upper behavior. A single boundary
after a fused compound expression would be insufficient. Each local edge term
contains the square of a factor that vanishes at its join, so its value and first
derivative vanish at u=0.2 or u=0.8. The contract makes no claim that this artistic
field recovers the complete reference illumination.

The shared 128-entry edge array makes all 127 columns adjacent. The incoming
vertical renderer scale belongs in row sampling; the incoming horizontal scale
belongs in column boundaries. Clip intersection must retain full-field u/v.
Existing helper inspection confirms the mechanical raster guard can save both
scales, observe physical viewport/clip at scale one and restore scales without
rewriting clip storage. Grain must run after that guard restores caller scale.
The helper color must also be restored; viewport, clip-enabled state and blend
remain untouched, including empty intersections.

Independent operation enumeration covers **19** size/scale combinations:
reference, minimum active, 1920×1080, unequal 1920×820, fractional composition,
and maximum 8192×8192 at scales 1/1.5/2, plus renderer scale (1.5,2). Old and new
grain rectangles are all inside their intrinsic gradient rectangle. The old
canonical grain has **1,485 pairs** (rows 223, columns 495, pitch 5). The new
4,608 marks occupy **4,501 unique origins**, spanning x606–1109 and y275–501.
Ordered little-endian uint16 `(x,y)` pairs have SHA-256
`9851e00a147dd982e8d5eac1136238db6564ca2010512badd75041e2fa54b54e`.
Pinned SDL software fill truncation and minimum-one extents agree with the
contract's operation support. These checks do not import the candidate painter.

Canonical intrinsic support is `[604,1112) × [273,504)`, **117,348 pixels**;
exactly one device pixel of expansion produces **118,830 pixels**. Translate
that independent union by the actual physical viewport and intersect output,
viewport and enabled clip only after expansion. Empty clips receive no
allowance. Do not widen a support envelope after observing changed pixels.

At 8192×8192 and renderer scale 2 the intrinsic row count is **4,022**, within
the conservative contract bound of 4,028. Thus the stated upper bound is
516,164 drawing primitives plus 9,216 hash calls; a resource fixture exposes at
most 64 rows, bounded by 12,736 primitives. These are application-work bounds,
not an SDL allocation, deadline or full-display performance claim.

## Frozen fixture and genuine-before handoff

The new source is
[`test_standalone_lower_rack_material_raster.cpp`](../../apps/standalone/native_tests/test_standalone_lower_rack_material_raster.cpp),
SHA-256 `281df1de3edce6a91a851d0b5674677646f1741fac1512f474ea7ffda67350e7`.
It adapts the unchanged Upper fixture, whose SHA-256 remains
`38a35be03a2b6a346cee13c614b4c7cfe57c0be4fd9e96738910d3181959bdae`.
The new source was frozen while the genuine painter still matched the identity
above. A11 did not edit CMake, production painting or existing tests and did not
run a native build.

The fixture exposes target `test_standalone_lower_rack_material_raster`:

- No arguments run all 32 cases, clipping companions, full-frame foreground
  assertions and exact same-renderer/fresh-renderer case-28 repetition.
- `--list` emits schema 1, protocol `lower-rack-material-v1`, and count 32.
- `--case N` emits one newline-terminated JSON header followed by exactly
  `width*height*4` RGBA bytes. Windows stdout switches to binary mode.

All route, edit, pending and focused-control ownership is Lower. All nine
centers, rack bounds, heading, edge/empty clips, resource viewport origins and
opaque child probes use the Lower specification. Both renderer scales have
independent fields and dimensions; case 30 uses unequal composition scales and
case 31 uses `(rx,ry)=(1.5,2)`. Both manuals' declared held notes and all four
banks remain in the complete copied model. No candidate material, coefficient,
seed or allowance mask is present in the fixture or its stream.

Built-in assertions check the copied model and full geometry, 68 controls,
147 keys, 24 presets, ordinary Lower focus traversal, both transform scales,
physical/logical viewport and clip, enabled empty clips, blend mode, full-clip
companions, glyph contrast and exact cyan focus ink. The external independent
checker still owns **before/after opaque-child RGBA equality**, operation-derived
support and numerical material screens. An opaque alpha probe by itself is not
that equality check. Normal output is at most 3900×2200, and maximum logical
geometry uses only a 64×64 output allocation.

Root completed the genuine-before build/run while this admission was being
finalized. The [root identity receipt](../development/2026-11-16-conversion-material/reports/lower-before-identity.json)
confirms the unchanged painter and exact frozen fixture hashes. All **32 cases**
passed, including 58,957,343 assertions, 51 state restorations, 15 clip companions,
252 opaque child probes, 826 glyphs, 14 focus cases and both repeat checks.
The preserved executable SHA-256 is
`1ffcd7e3b70b813e7af2cc5986be0659df93ee0c058ad66f329208d7e11c60ac`.
A11 read this receipt and rechecked the current painter/fixture source hashes;
the build/run itself was performed by root. These results qualify the before
fixture machinery and do not grade the proposed Lower material.

The bounded painter may now proceed with the identical fixture source. Preserve
the existing 66-case percussion pair unchanged; together the pairs comprise
**98 cases**. Do not label the new supplemental before binary as an original
historical one.

## Baseline failures and remaining acceptance

The independently measured original baseline passes **7 of 35** Lower material
screens and fails **28**. This is a preserved starting observation, not failure
of the new fixture's state/clip/foreground invariants. Both long-strip horizontal
slopes and the right-minus-left mean fail; their reference values are
+0.067456761158411, −0.131003434065934 and −7.339173573908731 respectively.
Keep every inequality and failure, the exact source statistics, and all three
descriptive bottom-interior witnesses. No threshold or patch is amended here.

Candidate acceptance still needs the genuine 98-case before/after comparison,
35 reference screens, exact outside-support and inactive preservation, child
source/opaque-interior/focus checks, coherent affected native suites with
`--no-tests=error`, and independent full-frame inspection at 1672×941 and
1400×820. Numeric passes cannot waive seams, bands, sparkle or worse legibility.
Actual app captures need matching replay and source/binary/state provenance
before a README gallery update. Bottom reflections and all other material/type
residuals remain open; literal whole-interface **1:1 remains unmet and unwaived**.
