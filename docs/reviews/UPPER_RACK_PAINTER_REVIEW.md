# Upper-rack painter source review

**A29, 16 November 2026: admit the private painter for frozen v1.1 scope.**
No blocker was found. Whole-interface **1:1 remains unmet and unwaived**.

Read complete AGENTS/PLAN, scope/records, the
[contract](../design/UPPER_RACK_MATERIAL_CONTRACT.md),
[A11 admission](UPPER_RACK_MATERIAL_ADMISSION.md), genuine original/candidate,
Drawing, UiModel, fixture and pinned SDL. The
[audit receipt](../development/2026-11-15-streaming-continuation/reports/A29-painter-audit.json)
retains checks. A29 performed no build, candidate run, recapture or production edit.

## Source binding and preserved paths

| Input | SHA-256 |
| --- | --- |
| Candidate painter | `30ac6cec988ec1834f36456d25d1e53113642071d844d53f81b62b3474cf2c37` |
| Genuine `../baseline/InstrumentView.cpp` | `0614f236e1e5bbe0cd8ac89210b27c77140724be5da49e3f2f4e67583b159c0a` |
| Frozen v1.1 | `baca5edb5878713291316751ad496e31513251c8bf8ce893605ede0496d00868` |

Reversing only the added include/helper, comment, default-off option, fallback
indentation and Upper call replacement reconstructs every original byte. The
original equals base `4aac394`'s file. Of 187 baseline inventory entries, 185
remain exact; only painter/standalone CMake differ. Drawing, UiModel, fonts,
assets, state and Engine remain unchanged; generated art and SDL match admitted
hashes.

Only registration panel 0 opts in; other panels retain their order/default path.
The five shadows, rounded layers, four accents, screws and all later heading,
guide, well, cap, footage, value and focus arguments/order are unchanged. The
unchanged predicate requires Dimensional Play, width 1400–8192 and height
820–8192. No control or saved state is added.

## Arithmetic and physical raster

The helper takes the actual binary32 inset. Each prescribed binary64 operation
in boundaries, vertical sampling and field evaluation has its
own volatile double boundary. No multiply/add join contracts across those stores.
Channels use `std::round`, clamp, conversion and opaque alpha. Independent
arithmetic reproduces column 32/row 388: `q=21.5`, RGB `(23,22,21)`.

A deliberate libm FMA contrast changes 2,692 of 15,015 canonical field `q` values
when both joins contract, yet changes no rounded RGB. Pixel agreement alone
therefore cannot prove evaluation order; source barriers supply that evidence.
Release flags contain no fast-math; other compiler/architecture runs remain open.

The 66 shared boundaries partition 65 columns using binary64 endpoints and
pixel-center `ceil(edge-.5)`, clipped before int conversion. Spans use a point
at width one, otherwise an inclusive line to `end-1`, matching PixelRaster.
Rows retain complete-inset coordinates through clipping/translation. Scale is
restored before grain's `Drawing::rect` and SDL's binary32 origin/extent truncation.

Unsigned mixing wraps at 32 bits with the frozen seed and bright-then-dark order.
Independent enumeration gives 4,096 marks, 4,041 unique origins, x78–593/y275–501
and the admitted ordered-origin hash. Collisions need no retry/storage; field
and grain have no frame/focus dependence.

## State and bounded work

Both scale components are saved; physical viewport/clip are queried at scale one.
Viewport, clip and blend are never set, preserving fractional stored coordinates
without reconstruction through logical getters. Empty/disjoint/early returns
leave through guards. The outer color guard outlives the inner scale
guard; grain runs after the latter restores scale.

Negative viewport translation and clip endpoint sums use int64 arithmetic. A
nonempty intersection satisfies `0 <= left < right <= viewport.w`, analogously
for y, before narrowing. This avoids signed-int overflow/out-of-range conversion
and agrees with SDL's floored physical getters/queued bounds.

Custom storage is 66 ints plus fixed guards/scalars. Nonempty work uses exactly
8,192 mixes and at most `65*R+4096` drawing primitives; empty intersection may
skip grain. At logical height 8192/scale 2, independent endpoint arithmetic gives
4,022 rows and a 265,526-primitive bound. The 64-row resource crop bound is 8,256.
These are source bounds, not SDL allocation/deadline receipts.

## Executed evidence and limits

Root's [coherent receipt](../development/2026-11-15-streaming-continuation/reports/coherent-qualification.json)
records **210/210 CTests passing in 191.89 seconds**. Rehashed 505 inputs,
three logs and binaries. Ordinary fixture source checks physical/logical
transforms, enabled-empty clips, NONE blend, negative resource viewports, 15 clip
companions, strong glyphs, focus and repeats. Its scale pairs are equal; helper
color restoration is source-proven, not directly instrumented by that whole-view
fixture.

[A25](UPPER_RACK_COMPARISON_ADMISSION.md) owns the 96-pair containment/numerical
admission; [A26](UPPER_RACK_GALLERY_ADMISSION.md) owns all twelve captures. A29
viewed complete reference/minimum-active candidates, prior Play and original JPEG:
no conspicuous new bands, seams, periodic grain or impaired label/focus readability.
Other material, key/cap and typography differences remain.

Maximum-geometry crops protect zero output pixels; a full maximum-size display
is unqualified. Next: preserve this source binding through integration/platform
gates; future material changes need a declared protocol. SDL internal allocations,
real display/DPI/input, semantic accessibility, devices, callback deadlines,
physical fidelity and whole-interface equality remain unqualified by these results.
