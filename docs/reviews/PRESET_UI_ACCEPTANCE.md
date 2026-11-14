# Independent preset UI and raster acceptance

A25 (`/root/w05_a25_ui_acceptance`) independently accepted the preset UI model
and found two responsive focus defects in the native renderer. The final
affected tests pass. This review qualifies the named source and SDL software
surface; it does not establish literal equality with the reference, native
screen-reader semantics, physical-device behavior or complete product release.

The authoritative behavior comes from [the frozen UI design](../PRESET_UI_DESIGN.md)
and [selection contract](../PRESET_SELECTION_CONTRACT.md). The test expectations
do not use the generated registration matrix or `ControlState::select_preset`
to construct the expected state transition. A25 read the standing instructions,
complete M0–M9 plan, current status/next steps/log, the complete atlas-review
consolidation and A18/A23 implementation evidence. The six source readers remain
the complete-PDF readers; this assignment does not claim another full reading.

## Model acceptance

[`test_standalone_preset_ui.cpp`](../../apps/standalone/tests/test_standalone_preset_ui.cpp)
uses a real `Session` and Engine for owner retention, with independent literal
expectations for selector transitions and semantic navigation. Its final
renamed target passes **1/1 in 0.07 seconds**.

| Acceptance area | Executed evidence |
|---|---|
| Geometry and occlusion | Twelve admitted layouts, including the three main sizes, both responsive thresholds and extreme aspect ratios. Seven literal arithmetic anchors are checked. **549,388** sampled points are independently classified from seven natural divisions and five ivory-key overlaps. |
| Inventory and focus | Exactly 24 preset controls, 64 ordinary controls, all 61 + 61 + 25 playing identities, and a literal 67-stop Tab/Shift+Tab order. **144** arrow/Home/End moves leave controls and playing-key roving positions unchanged. |
| Pointer selection | **288** cases: either manual × every initial effective selector × every target. Every click emits exactly one copied-control command, including explicit reselection. Duplicate Down, held-pointer motion, Up and capture loss add no selector or note event. |
| Ownership and reflow | A UI Upper C owner overlaps an external Upper C owner, with separate external Lower and pedal owners. Every transition preserves all holds and clock through zero-frame application and three responsive reflows. Releasing UI C leaves the external owner held. |
| Keyboard activation | **48** cases: both manuals × twelve keys × Space/Enter. Repeat and release suppression preserve note ownership. |
| Invalid identities | **753** invalid manual/bank/index byte values preserve destination parameter IDs, focus, desired controls and dirty/pending state. |
| Pending and rejection | Delayed prefix acknowledgment cannot replace a newer desired copy. A not-yet-submitted copy remains pending, stale publications cannot undo a later route, and rejection restores applied controls with the existing recovery policy. |

The test was initially named `test_preset_ui_acceptance`; that target also
passed 1/1 in 0.07 seconds. The integrator requested the final
`test_standalone_preset_ui` name so the hosted standalone workflow's
`^test_standalone_` filter includes it. Only the affected renamed target was
rebuilt and rerun. Neither result is a claim that every discovered suite ran.

## Native findings and repairs

[`test_standalone_preset_raster.cpp`](../../apps/standalone/native_tests/test_standalone_preset_raster.cpp)
paints the actual `InstrumentView.cpp` and `Drawing.cpp` to an SDL software RGBA
surface. It initializes no window or audio subsystem. At 960×700, 1280×900,
1672×941 and the shortest 1400×820 layout, it compares unfocused and focused
pixels, isolation from other keys, and applied/requested/Cancel/rejected states.

The first execution against A23's renderer failed **32 assertions**:

- **14 natural-key focus failures at 1400×820.** Repainting the whole label
  rectangle after drawing focus erased every light focus pixel in the short
  natural-key focus region.
- **14 fractional accidental-label differences.** Independent high-contrast
  ink classification in the next run confirmed that these included original
  glyph pixels, rather than only blank label margins. Redrawing scaled glyphs
  through a tighter clip changed the rendered result at those positions.
- **Four test-oracle errors.** The Cancel comparison originally included C's
  full rectangle, which also contains the overlapping C# key. C# legitimately
  changes when the route is cancelled. The corrected oracle checks C's exposed
  lower face. There was no demonstrated Cancel-paint production defect.

The integrator authorized a minimal renderer repair. Naturals retain the
original two-tone outline without a full-label repaint; their single-letter
ink remains intact. Accidentals draw the same contracted focus outline with
its ink clipped above the existing label, so the original glyph/material is
never repainted. Hit rectangles, focus bounds, pending markers, route semantics
and the UI model remain unchanged. The caller's existing clip is restored.

An intermediate natural-only candidate passed all focus-visibility and
corrected Cancel checks but retained the **14 accidental ink failures**. The
complete repair passes the native target **1/1 in 15.45 seconds**:

| Check | Passed count |
|---|---:|
| Visible independent focus and preserved original high-contrast pitch ink | 96 |
| Other-manual and overlapping-accidental pixel isolation | 376 |
| Applied/requested distinction, acknowledgment, momentary Cancel, hidden raw memory and rejected request pixels | 48 |
| Reported failures | 0 |

The label oracle excludes blank margins, bevels and faint filtered edges; it
requires nonempty high-contrast original ink and exact preservation of those
pixels. This detects the observed overwriting/resampling problems. It is not an
OCR score, general readability metric or accessibility conformance test.

Original failures and final results remain in the
[machine-readable evidence](../development/2026-11-14-preset-continuation/reports/a25-ui-acceptance.json)
and linked raw logs:
[first raster](../development/2026-11-14-preset-continuation/reports/a25-raster-first.txt),
[natural-only candidate](../development/2026-11-14-preset-continuation/reports/a25-raster-natural.txt),
[final raster](../development/2026-11-14-preset-continuation/reports/a25-raster-final.txt),
[final model](../development/2026-11-14-preset-continuation/reports/a25-ui-final.txt).

## Actual visual inspection and remaining differences

A25 visually inspected the exact
[cover/page-409 reference](../design/atlas-cover-reference.jpg), A23's complete
application captures at 960×700, 1280×900 and 1672×941, its 1672×941 Cancel frame,
and its minimum-size Help frame. The full-frame source identities are in
[A23's renderer review](PRESET_RENDERER_IMPLEMENTATION.md). Those captures
precede the A25 focus repairs and must be regenerated for the integrated gallery.

The inspected application shows all 24 reversed preset keys, separate EDIT and
sounding captions, stored percussion choices with `REQUIRES UPPER B`, an
unlatched Cancel with an explicit cancelled caption, and Help that distinguishes
fixed A from adjustable A#. No clipping of the Help content was observed at
960×700. The source palette, wood/cabinet decoration and deeper control faces
guide the native result, while these differences remain visible:

- Manuals retain rectangular shared hit geometry instead of the reference's
  perspective and tapered fronts. Materials and panel composition still differ.
- Functional utility controls, expression/pedal controls, permanent pedals and
  factual cabinet/device status differ from the concept composition.
- The source art's three cheek tablets are replaced by the atlas-specified
  twelve reversed keys. Correct footage and implemented control legends retain
  their semantic meaning.
- Accidental pitch labels remain very small on the 12–13-unit keys. The focus
  repair preserves their pixels; it does not make them large or establish
  universal legibility. Native semantic accessibility remains separate.

After repair, a separate harness using the qualified actual renderer produced
1400×820 natural-D focus and 1280×900 accidental-G# focus images. A25 inspected
their full frames and 4× nearest-neighbor QA crops: D has a visible two-tone
ring at the shortest layout, and G# keeps its label below the open focus stroke.
These are native renderer-surface inspections, not whole-application screenshots.
Their hashes and provenance are in the machine-readable record; local files are
under `/tmp/hammond-preset-a25/`.

**Literal 1:1 equality remains open.** Keep this distinction beside the README's
actual application gallery, and retain these behavioral/raster regressions when
later material or perspective work changes the renderer.

## Source and execution identity

Committed checkout base: `35554c068492fe2b20c1f8a602d8354ae762dc42`.
The build includes the concurrent preset implementation overlay; this base
alone does not identify the tested code. Copied sources were compiled together
in `/tmp/hammond-preset-a25/`, with no rebuild or reconfiguration of the preserved
baseline/native directories. A final comparison found **all 56 selected live
core, UI, drawing, configuration and test inputs equal to the tested copy**.

| Identity | SHA-256 |
|---|---|
| Final 1,249-file source manifest | `85f93c43931f416479fb67dc9e4d6fd268f03062fcac70df39e7b22430c7d906` |
| Final `InstrumentView.cpp` | `c4be416d5a0e715d26d0d582d6f4539224561e591220bbae165ea2b00a0246e7` |
| SDK-free model test executable | `37b5204614828740179ca71f5532cbe05a61fae1a24f55ad9ef77f04cfa23cf9` |
| Native raster test executable | `d5a81932916e17825e6fce1586f7dfc6033af356a4b615ca7c143adffe400fea` |

Toolchain: GNU C++ 14.2.0, CMake/CTest 4.4.4, Python 3.12.14, C++20 Release with
the repository's strict warning policy. Native dependency: SDL 2.32.10, pinned
commit `5d249570393f7a37e037abf22cd6012a4cc56a71`. MIDI and VST3 are disabled
in these focused builds. Commands and owned-path handoff are in
[A25's assignment note](../development/2026-11-14-preset-continuation/25-ui-acceptance.md).
