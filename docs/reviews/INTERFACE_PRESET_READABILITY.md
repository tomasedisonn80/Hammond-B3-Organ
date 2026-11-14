# Preset readability and header alignment

**A34 closes the measured accidental-label shrink and the 33-pixel wide-header
offset.** This is a bounded native rendering correction, preserving the existing
24 preset identities, hit rectangles, 61+61+25 playing geometry, selection and
navigation. [A27](INTERFACE_RESPONSIVE_AUDIT.md),
[A28](INTERFACE_SCALE_TEXT_AUDIT.md) and
[A32](INTERFACE_REFERENCE_COMPARISON.md) retain their original observations.

## Actual change

Ivory accidental caps now show the canonical pitch letter above `#`, each at
9-unit Sans. Their label rectangle alone grows from 11 to 20 units high,
remaining two units above the key bottom. Two 11-unit line boxes have a nine-unit
pitch; each 6.46875-unit glyph envelope remains separate. The largest advance is
7.59375, inside the minimum ten-unit label width. Natural single-letter rendering
is unchanged. The [updated preset contract](../PRESET_UI_DESIGN.md) gives exact
formulas; the full semantic caption continues to name D#, C# and other pitches.

At 960×700, Upper D# still has hit bounds `[58,424,12,32.240002]`. Its label is
now `[59,434.239990,10,20]`; both characters retain size **9**, compared with the
old **6.153846** single-line size. At 1400×820, the shortest accidental is
26.411995 units high. Its label begins 4.411988 units below the cap top, leaving
the independent cyan focus stroke visible. The A28 physical-clip restoration
function is byte-for-byte unchanged.

The title now centers its measured advance on the window midpoint, with the
existing fit and clamp retained. All ten header actions keep their geometry.

| Window | Old title center | New center | Focused D# cyan pixels, either mode |
|---|---:|---:|---:|
| 960×700 | 480 | 480 | 18 |
| 1280×900 | 640 | 640 | 49 |
| 1400×820 | 733 | 700 | 6 |
| 1672×941 | 869 | 836 | 50 |

## Executed evidence

The app and five affected targets built with GCC 14.2/C++20 Release and strict
warnings. UI, preset UI, workspace raster and scaled-view suites passed on the
first run. The expanded preset raster passed after correcting its new author
oracle: **192 preserved label/focus cases, 160 full-size glyph rows, 752 isolation
cases and 96 applied/pending/Cancel/rejection checks**, across all four sizes and
both presentations. No original focus, containment or state assertion was weakened.

The first new oracle wrongly required fully opaque reduced glyph pixels; `#`
and `A` have antialiased samples without such a core. Its 96 failed rows are
retained. The corrected oracle reconstructs each actual cap row from an adjacent
unlettered pixel, draws the independent canonical nine-unit glyph, and compares
the native pixels exactly. A separate proof-authoring failure incorrectly equated
opaque title ink with the conservative atlas envelope; the corrected check uses
containment and exact before/after translation. Both failures remain identified.

Sixteen actual app captures cover before/after × four sizes × two presentations,
using dummy audio/video and software rendering. Their inputs and executable stayed
stable. Pixel comparison proves **112 natural labels unchanged** and every changed
pixel confined to an accidental key or the title. The wide title moves exactly
−33 pixels; the source-derived envelopes remain disjoint from all header actions.

Inspected the minimum Dimensional and breakpoint Flat full frames, the complete
reference frame and both literal crop sheets. The complete pitch characters are
visibly larger, the tight focus stroke survives, and header actions remain clear.
Three retained PNGs total **881,230 bytes**:

- [Literal preset comparisons, both modes](../development/2026-11-14-interface-continuation/reports/a34-preset-before-after.png)
- [Literal header comparisons](../development/2026-11-14-interface-continuation/reports/a34-header-before-after.png)
- [Actual reference-size app after correction](../development/2026-11-14-interface-continuation/reports/a34-play-reference-after.png)

The [source/command handoff](../development/2026-11-14-interface-continuation/session34-preset-label-polish.md)
and [proof data](../development/2026-11-14-interface-continuation/reports/a34-proof.json)
identify this pre-A36 application. Nine-unit cap text remains small, especially
on a physical display with unknown scaling; no human accessibility certification
follows. Larger panel proportions, material differences, actual display/GPU
qualification and literal 1:1 reference fidelity remain open.
