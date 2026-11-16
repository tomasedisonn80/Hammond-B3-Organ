# T1 material-fixture assertion transition

**A32 admits this precise, versioned assertion transition.** The Upper and Lower
material fixtures now require the previously admitted T1 footage runs. Their
original sources, protocols and observed failures remain preserved. The fresh
root build succeeded and both updated native fixtures passed. This decision
does not revise any material-comparison allowance or reference threshold.

The production typography was independently admitted before implementation in
the [T1 contract](../design/FOOTAGE_TYPOGRAPHY_CONTRACT.md) and
[A25 review](FOOTAGE_TYPOGRAPHY_ADMISSION.md). The subsequent
[110-pair comparison](FOOTAGE_TYPOGRAPHY_COMPARISON.md) establishes protected
pixel, model and material preservation. The independent
[actual-image review](FOOTAGE_TYPOGRAPHY_VISUAL_ADMISSION.md) is a separate gate.
None of these documents claims whole-interface 1:1 correspondence.

## Why a version transition is necessary

The unchanged historical material fixtures rendered expected footage as a
single fitted Serif string requested at `19 * min(sx, sy)`. Mixed labels were
fitted smaller by that existing helper. The admitted T1 implementation instead
uses a `20.5 * min(sx, sy)` ordinary label and five measured runs for each mixed
fraction. Keeping the historical assertion against that intentionally changed
ink would require the wrong typography.

Root rebuilt and ran the **original** fixture sources against the candidate
painter before this transition. Both failed at `every literal glyph retains all
strong contrasting ink`. The
[initial candidate receipt](../development/2026-11-16-conversion-material/reports/typography-candidate-native-initial.json),
[Upper log](../development/2026-11-16-conversion-material/reports/typography-candidate-test_standalone_upper_rack_material_raster.log)
and [Lower log](../development/2026-11-16-conversion-material/reports/typography-candidate-test_standalone_lower_rack_material_raster.log)
remain unchanged. They are expected historical-assertion failures, not evidence
that the new implementation had already passed these fixtures.

Before editing, A32 archived each exact raw source:

| Fixture | Original source SHA-256 | Original protocol | New protocol |
| --- | --- | --- | --- |
| [Upper archive](../development/2026-11-16-conversion-material/reports/A32-upper-material-before-t1.txt) | `38a35be03a2b6a346cee13c614b4c7cfe57c0be4fd9e96738910d3181959bdae` | `upper-rack-material-v1.1` | `upper-rack-material-v1.2` |
| [Lower archive](../development/2026-11-16-conversion-material/reports/A32-lower-material-before-t1.txt) | `281df1de3edce6a91a851d0b5674677646f1741fac1512f474ea7ffda67350e7` | `lower-rack-material-v1` | `lower-rack-material-v1.1` |

The archive bytes equal the corresponding files at genuine published commit
`3520c96adcdcf4ce4bcb860082354bf0050a89c3`. Native protocol versions identify
assertion behavior; **Lower native protocol v1.1 is not the Lower material
measurement contract v2**. The original material comparators continue to require
their original protocols and binaries. Their historical passing and failing
reports remain interpreted under their original inputs. Do not make those
comparators accept both protocols or silently run new binaries as historical
ones.

## Exact changed source surface

Each fixture adds `FontData.h`, a local expected-run renderer and a local footage
ink sampler. It replaces the one historical footage call inside
`full_frame_children`, changes the native protocol string, and records the
transition in the introductory comment. There are no production or CMake edits
in this assignment.

The [bounded source audit](../development/2026-11-16-conversion-material/reports/A32-transition-audit.py)
removes precisely those additions, restores the old call/comment/protocol, and
requires equality to every byte of the archived original. Its
[passing receipt](../development/2026-11-16-conversion-material/reports/A32-transition-audit.json)
also requires the new footage sampler's entire sampling body to equal the old
`literal_ink` sampling body. Both Upper and Lower expected helpers are
byte-identical. Consequently, these existing requirements are unchanged:

- All 30 Upper and 32 Lower case definitions, state variants, renderer transforms,
  maximum-size crops, resource bounds, and repeat checks.
- Model/layout/session serialization, state restoration, model invariants,
  value and heading text, opaque-child/material probes, and cyan-focus checks.
- Caller clip restoration, exact visible clip-companion comparison and cleared
  caller-exterior behavior. The separate T1 supplemental fixture's documented
  scaled-glyph clipping correction is not applied to these material fixtures.
- Every strong-ink threshold, nonempty-glyph requirement and per-glyph sample
  count requirement. The original `literal_ink` function remains unchanged for
  all other text.
- Frame generation and stream structure. Only the explicit protocol value
  changes the emitted metadata.

## Independent expected typography

The new helper declares all nine correct ASCII identities by musical-label
index, rather than calling the private production helper or extracting runs
from the candidate. Ordinary labels are `16'`, `8'`, `4'`, `2'`, and `1'`. Mixed
labels are explicitly declared as the five parts of `5 1/3'`, `2 2/3'`,
`1 3/5'`, and `1 1/3'`. Reconstructing each full string must equal the fixture's
unchanged musical-label inventory. The historical artwork's incorrect label is
not copied into musical semantics.

With `sx = W / 1672`, `sy = H / 941`, `f = min(sx, sy)` and `r` denoting the
existing explicit binary32 rounding helper, the expectation independently
implements the contract:

| Run | Requested size | Baseline from label top | Gap after run |
| --- | --- | --- | --- |
| Whole numeral / complete ordinary label | `r(20.5 * f)` | `r(21.5 * sy)` | Mixed only: `r(0.5 * sx)` |
| Numerator | `r(13 * f)` | `r(15.5 * sy)` | 0 |
| Slash | `r(16 * f)` | `r(19.5 * sy)` | 0 |
| Denominator | `r(13 * f)` | `r(21.5 * sy)` | `r(0.5 * sx)` |
| Apostrophe | `r(20.5 * f)` | `r(21.5 * sy)` | 0 |

Advance widths come from unchanged `Drawing::text_width`. Width is accumulated
left to right, rounding each addition and each applicable gap separately. The
first cursor is `r(box.x + r(r(box.width - extent) / 2))`. Every requested
baseline is `r(box.y + r(offset * sy))`; the text top is
`r(baseline - r(r(38 * size) / 40))`. Subsequent cursor advances and applicable
gaps retain their separate rounding boundaries. Font size uses `f`, vertical
offsets use `sy`, and horizontal gaps use `sx`; no uniformly scaled substitute
is permitted at unequal dimensions.

The expectation renders the literal runs through unchanged `Drawing::text`.
It independently derives each actual glyph-copy rectangle from the pinned
Serif atlas, including bearings, reconstructed ascent baseline, advance and
the existing conditional two-pixel transparent gutter. This includes the
numerator, slash, denominator and apostrophe separately. A nonempty glyph is
required for every declared character.

Within each such rectangle the unchanged criterion samples expected encoded
luma at least 180, requires actual encoded luma strictly above 90 at **every**
sample, and requires at least one sample. It neither skips the old call's
responsibility nor accepts an old-or-new alternative. These rectangles bound
literal-ink checks; they grant no new before/after material permission. The
independent A29 comparator still owns the admitted glyph-union allowance and
exact protected-pixel checks.

## Compiler failure and fresh native validation

The first candidate helper used an implicit `char` to `unsigned char` range-loop
conversion. GCC's existing warnings-as-errors gate rejected it. The
[first Upper candidate](../development/2026-11-16-conversion-material/reports/A32-upper-material-sign-conversion-failure.txt)
and [first Lower candidate](../development/2026-11-16-conversion-material/reports/A32-lower-material-sign-conversion-failure.txt)
are archived. The
[correction receipt](../development/2026-11-16-conversion-material/reports/A32-sign-conversion-correction.json)
records the explicit conversion at glyph lookup; no literal, arithmetic,
threshold or assertion changed.

Root retained the
[initial build/test sequencing failure](../development/2026-11-16-conversion-material/reports/typography-material-transition-initial.json).
Tests accidentally started after that failed build ran stale executables and
are expressly excluded from source qualification. Root then verified the
[successful rebuild](../development/2026-11-16-conversion-material/reports/typography-material-transition-fixed-build.log)
before the [fresh CTest invocation](../development/2026-11-16-conversion-material/reports/typography-material-transition-fixed-ctest.log):

| Fresh native gate | Result |
| --- | --- |
| `test_standalone_upper_rack_material_raster` | Pass, 13.78 seconds |
| `test_standalone_lower_rack_material_raster` | Pass, 13.86 seconds |
| Combined selected run | 2/2 pass, 27.65 seconds wall time |

The [qualified identity receipt](../development/2026-11-16-conversion-material/reports/typography-material-transition-qualified.json)
binds both executables, their sources, the painter and all build/test logs.
The retained [native invariant output](../development/2026-11-16-conversion-material/reports/typography-material-transition-LastTest.log)
records the complete successful results:

| Invariant observation | Upper | Lower |
| --- | ---: | ---: |
| Cases / assertions | 30 / 58,877,477 | 32 / 58,958,029 |
| State restorations / clip companions | 49 / 15 | 51 / 15 |
| Exact visible clip pixels | 29,916 | 29,340 |
| Opaque child probes / pixels | 216 / 121,526 | 252 / 142,099 |
| Literal glyph checks / strong-ink samples | 708 / 36,526 | 826 / 42,526 |
| Focus cases / cyan pixels | 12 / 21,864 | 14 / 25,508 |
| Same-renderer / fresh-renderer repeats | Both pass | Both pass |

The accepted source hashes are Upper
`4167125e89fa1289c230b511e0a75a137a83379689ac5cc49362f6c0af2554e3`
and Lower
`2cc82460d6946ded81f321a3bce74affb61a233339f14e04c0f88e36ec12cf4b`.
The bound production painter remains
`a88e7576700ae306769849ceda36993969a61e848c015ba4fb98fa9c4a7e8cfa`.
Source hashes identify inputs; the successful fresh compilation and executions
provide the runtime evidence.

## Continuation rule

Root may integrate the scoped T1 stage after reading this review, the visual
admission and the independently passed 110-pair comparison. Preserve that
accepted stage's genuine source and native binaries before any subsequent rim
edit. Future changes to typography require their own admitted contract,
before/after evidence and explicit fixture version transition; the old material
acceptance must never be redefined by widening masks or relaxing glyph checks.

Physical display/DPI, semantic accessibility, real audio/MIDI devices and
literal whole-interface 1:1 remain outside this finite software gate.
