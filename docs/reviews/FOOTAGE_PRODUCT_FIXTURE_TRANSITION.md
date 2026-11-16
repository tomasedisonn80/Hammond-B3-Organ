# T1 product visual fixture: precise assertion transition

**A35 admits the versioned product visual assertion transition.** A fresh root
build and execution pass all 76 cases and 12,952 checks under
`product-visual-t1-v1`. Only active wide manual footage expectations change;
the original literal contrast and padded-row criteria, case matrix, cap checks,
control inventory, focus, pending feedback, clipping and historical comparison
code remain intact.

This supplements the admitted [T1 typography contract](../design/FOOTAGE_TYPOGRAPHY_CONTRACT.md),
[independent production comparison](FOOTAGE_TYPOGRAPHY_COMPARISON.md),
[material-fixture transition](FOOTAGE_MATERIAL_FIXTURE_TRANSITION.md) and
[actual-image review](FOOTAGE_TYPOGRAPHY_VISUAL_ADMISSION.md). It does not modify
their frozen production allowances or reinterpret their earlier results.

## Original failure and preserved source

Root's coherent full run passed 218 of 219 CTests, with unchanged input hashes
through the run. The sole failure was `test_standalone_product_visual`: its
historical active-wide footage plans still expected a single fitted Serif
string requested at `19 * min(sx, sy)`. T1 intentionally replaces that layout
with ordinary 20.5-sized lettering and five measured fraction runs. The old
fixture failed 4,464 per-glyph checks: 62 manual footage glyphs across each of
the 72 full active cases. The complete
[original run](../development/2026-11-16-conversion-material/reports/wave06-before-rim-ctest.log)
and [input qualification](../development/2026-11-16-conversion-material/reports/wave06-before-rim-qualification.json)
remain preserved. This was an obsolete placement expectation, not a passing
test to be silently relabelled.

Before editing, A35 archived all 37,628 original fixture bytes in
[the exact source archive](../development/2026-11-16-conversion-material/reports/A35-product-visual-before-t1.txt).
SHA-256 is `97bb4d5afc5d7e72694a522d5b1c1f4bb9c30e51eecf470933865d4323f0697f`.
The archive equals the published source at
`3520c96adcdcf4ce4bcb860082354bf0050a89c3`.

## Exact edited surface

The [current fixture](../../apps/standalone/native_tests/test_standalone_product_visual.cpp)
adds the pinned font-metrics include, an explicit binary32 rounding helper,
an opt-in manual-footage plan tag, a private independent expected-run renderer
and a protocol label. Only the active-wide manual footage plan enables that
tag. Ordinary text plans and the `legacy_digits` branch keep their existing
behavior. The current source SHA-256 is
`f9b6d76250cb10d9c75210b8bccae8c426bde079fc49c0b29650952aaa48c040`.

The [source audit](../development/2026-11-16-conversion-material/reports/A35-transition-audit.py)
reverses exactly those additions and the single changed plan initializer.
Its [passing receipt](../development/2026-11-16-conversion-material/reports/A35-transition-audit.json)
requires every restored byte to equal the archived published original. The
entire `text_acceptance` sampler is byte-identical. Eight deliberately altered
out-of-scope assertions are detected by that exact reversal, including the
contrast thresholds, nonempty-glyph criterion, row containment, level matrix,
focus count, caller exterior and cap invocation.

The audit's first negative probe used a substring that occurred in both the
glyph sampler and historical comparison. The script correctly refused that
ambiguous mutation before writing a result. Its
[original source](../development/2026-11-16-conversion-material/reports/A35-transition-audit-initial.txt)
and [setup correction](../development/2026-11-16-conversion-material/reports/A35-audit-setup-correction.json)
remain retained. Narrowing the probe to the complete glyph condition fixed the
audit setup; native source and acceptance criteria did not change.

## Independent expected glyphs and unchanged criteria

The helper declares the nine complete correct ASCII footages by index. It
explicitly declares each mixed fraction as whole numeral, numerator, slash,
denominator and apostrophe, then reconstructs the complete string and checks
it against both the musical inventory and the plan value. Both manuals retain
`1 3/5'`. It neither calls the private production footage helper nor imports a
candidate-produced geometry mask.

The independent expectation follows the admitted arithmetic: font scale is
`min(sx, sy)`; nominal sizes are 20.5, 13, 16, 13 and 20.5; baseline offsets are
21.5, 15.5, 19.5, 21.5 and 21.5 multiplied by `sy`; the two horizontal gaps are
`0.5 * sx`. Each multiply, cumulative extent, gap addition, centering operation,
baseline and cursor update retains its declared binary32 boundary. The helper
uses the unchanged `Drawing::text_width` and `Drawing::text` public APIs.

Every nonempty character receives its actual pinned Serif atlas copy bounds,
including bearings, reconstructed baseline, glyph advance and conditional
transparent gutter. This replaces only the obsolete uniform advance-cell
geometry for those manual labels. The enclosing permitted rectangle remains
the original label row inset by its original horizontal padding. No geometric
permission is added to the historical before/after comparison.

For every character, the original sampler still requires:

- At least one expected white-template sample with encoded luma **at least 160**.
- Actual encoded luma **at least 90** at every such sample.
- Every sampled pixel inside the same padded label row.

There is no old-or-new acceptance alternative, skipped fraction character,
reduced threshold, new tolerance or removed label. All ordinary value and
edited/sounding-route expectations remain byte-identical. The expected ink
population changes because T1 changes glyph sizes and placement; that count
is descriptive, not a relaxed success threshold.

## Fresh build and observed native result

Root first successfully rebuilt the changed target, then ran the required
selection with `--no-tests=error`:

```sh
cmake --build ../build-native --target test_standalone_product_visual --parallel 3
ctest --test-dir ../build-native --output-on-failure --no-tests=error \
  -R '^test_standalone_product_visual$'
```

The [build receipt](../development/2026-11-16-conversion-material/reports/typography-product-transition-build.json)
records a successful 4.25-second build. The
[test qualification](../development/2026-11-16-conversion-material/reports/typography-product-transition-qualified.json)
and [native output](../development/2026-11-16-conversion-material/reports/typography-product-transition-LastTest.log)
record a successful 18.25-second CTest; the enclosing command took 18.36 seconds.

| Observation | Original candidate failure | Fresh transitioned fixture |
| --- | ---: | ---: |
| Cases / frames | 76 / 148 | 76 / 148 |
| Checks | 12,952 | 12,952 |
| Failures | 4,464 | 0 |
| Complete literal glyphs | 8,717 | 8,717 |
| Strong text samples | 353,867 | 385,644 |
| Cap measurements | 1,296 | 1,296 |
| Caller-clipped cases | 4 | 4 |
| Pending-route cases | 42 | 42 |
| Focused cases | 76 | 76 |
| Historical compared pairs | 0 | 0 |

The current native executable SHA-256 is
`f011eeaac97a7de9f552cd0f35b6f8473b0da0768b8403a1ab96d1317efaa675`;
the production painter remains
`a88e7576700ae306769849ceda36993969a61e848c015ba4fb98fa9c4a7e8cfa`.
A35 independently checked both current hashes, the fixture hash, all six audit
source identities, root's successful receipts and the exact emitted result.
The [readback receipt](../development/2026-11-16-conversion-material/reports/A35-qualified-native-readback.json)
binds eleven retained inputs and preserves both original and fresh native rows.
This is readback of root's execution, not an invented second execution.

## Historical mode, further assumptions and handoff

The original fixture emitted an unlabelled `schema_version=1` result. The new
fixture retains that JSON schema and adds `protocol: product-visual-t1-v1` to
identify its changed assertion. Historical one-time comparison results remain
bound to their original source and executables. The `HAMMOND_PRODUCT_BASELINE`
branch, painter selection, masks, comparison checks and `legacy_digits` logic
are unchanged. That optional historical mode was not built or executed here;
the ordinary result correctly reports zero compared pairs. Current source must
not be substituted into an earlier historical qualification.

A bounded search of the other native fixtures found no additional direct
old-footage/Serif-19/y467 expectations outside the three transitioned fixtures
and the separately admitted T1 fixture. That source inspection does not replace
root's 218 other passing tests or qualify future changes. No production, font,
model, CMake, workflow, core, audio or plugin source was edited by A35.

Root can combine the unchanged 218 passing inputs with this freshly rebuilt
passing target, preserve the accepted T1 baseline and publish its concrete
source tree before releasing the separate rim change. This finite software
fixture does not close physical display/DPI, live audio/MIDI, semantic
accessibility, or literal whole-interface 1:1 requirements.
