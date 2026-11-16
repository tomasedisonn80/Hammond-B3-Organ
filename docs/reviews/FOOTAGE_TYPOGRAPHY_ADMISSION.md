# T1 footage typography — independent admission

A25 independently admits [contract v1](../design/FOOTAGE_TYPOGRAPHY_CONTRACT.md),
SHA-256 `e000682c74c3ef488cf89dd60396a3d129f8c525cf41a049334cc62030cb3f8a`,
for a bounded candidate **only after root records a passing genuine pre-edit
fixture run and preserves that executable**. This is protocol/fixture admission,
not candidate paint, image parity, new native-device evidence, or M9 closure.
The painter remains the accepted Lower stage. Whole-interface 1:1 remains unmet.

## Independently inspected inputs

Read the complete standing `AGENTS.md`, M0–M9 plan, current scope/checkpoint,
A41 material/type proposal, A52 independent review, actual layout/control
insertion, paint paths, `Drawing::text`/`text_width`, atlas metrics and native
material/percussion fixture assertions. Directly viewed the original complete
reference and the accepted Lower actual 1672×941 gallery frame. The root's
original proposal is preserved byte-for-byte in
[A25-proposal-before-admission.txt](../development/2026-11-16-conversion-material/reports/A25-proposal-before-admission.txt),
SHA `58e1fca471fdecb5672ad2816402ca0604381f7bc3cdb202c3bec431884199e1`.

| Input | SHA-256 |
| --- | --- |
| Accepted Lower painter | `45b710a9c207f456701732f55ec1086487d63bdb9a8b6ed995f4de12cd5bdb10` |
| Unchanged Drawing implementation | `9b788234405964f6675ab43428735e425b460c8045f2c6eb064c9e19b40a0a5f` |
| Font atlas | `f1a3121a2707a03a3b2e025c399e68c553ce9498f4b002ec13b18f512e334802` |
| UiModel implementation | `0ecb0c4ee90d98cdb87c6f06b4685d368a7c12b72f9ea66e6c40228a4a855ecd` |
| Original reference JPEG | `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187` |
| New fixture, prepared before paint | `facc85f516454964ed55e406f95db4046923d7a2441fdf72e65719b3685fec4f` |

The independent standard-library
[audit](../development/2026-11-16-conversion-material/reports/A25-typography-audit.py)
parses raw atlas entries, evaluates each declared operation with explicit
binary32 rounding, and reconstructs both old and new true glyph-copy quads.
It imports neither the painter nor A41/A52 numerical helpers. Its
[receipt](../development/2026-11-16-conversion-material/reports/A25-typography-audit.json)
contains **126 complete-label records and 378 passing geometry checks** across
seven logical-size pairs and both manuals. Every glyph stays inside its label
row and above the value row, and every recognized run fits the padded width.
These are source calculations, not observed candidate raster/legibility results.

## Arithmetic and semantic decision

The source confirms all nine correct strings, with `1 3/5'` at index 6. There
are four mixed labels and five ordinary labels per manual. Their admitted run
structure gives **50 text calls and 62 nonempty glyph copies**, not 90 actual
calls. The larger 90 bounds are conservative for fixed current string lengths.
Font size uses `f=min(sx,sy)`; baseline offsets use `sy`; the two half-unit gaps
use `sx`. A mixed advance is mathematically `39.9*f+sx`. Runtime advances are
measured rounded floats, so mathematical decimal sums are explanatory only.

The independent audit's initial assertion compared an actual binary32 width
with an unrounded binary64 decimal literal. It failed, and the
[original failure record](../development/2026-11-16-conversion-material/reports/A25-audit-initial-failure.json)
retains that test-authoring error and original script identity. Comparing with
the rounded `f32(31.2625)` fixed the assertion; no geometry, numerical criterion,
production code or image changed.

The root proposal left the native matrix open. The admitted contract now fixes
all 44 exact case IDs and state/transform tuples. It also makes new-helper
binary32 operation boundaries explicit, using volatile-float rounding to avoid
contraction/regrouping. Existing layout and Drawing arithmetic remain untouched.
The actual baseline reconstructed inside `Drawing::text` must be included in
support derivation; ideal requested baselines do not replace it. The audited
records happen to reconstruct the requested baselines exactly.

No glyph image or Unicode fraction is introduced. The new helper must preserve
all rectangles and actual musical control identities. The concept's inaccurate
footage lettering cannot replace the correct complete live strings. Unrecognized
future strings retain the old complete-string fallback.

## Observed clip failure and independently corroborated correction

Root's preliminary new-fixture build passed, but `--before` failed on the
unchanged accepted Lower painter when the fixture required every clipped glyph
pixel to equal its unclipped counterpart. A25 added failure coordinates, used
root's rebuilt existing binary under explicit diagnostic permission, and retained
[the exact diagnostic receipt](../development/2026-11-16-conversion-material/reports/A25-clip-diagnostic.json),
[log](../development/2026-11-16-conversion-material/reports/A25-clip-diagnostic.log),
and [failing fixture source](../development/2026-11-16-conversion-material/reports/A25-clip-failure-fixture.txt).
The pre-correction contract remains in
[A25-contract-before-clip-correction.txt](../development/2026-11-16-conversion-material/reports/A25-contract-before-clip-correction.txt).

The diagnostic returned exit 1 in **10.1721 seconds**. In case 26, output pixel
(203,492) was RGBA `(206,196,176,255)` with clipping and `(198,189,169,255)`
without it. Subtracting viewport (13,17) gives (190,475), inside the first `5`
glyph of Upper drawbar 1. Its old mixed string fits to approximately 15; the
software queue truncates that glyph's destination to `[186,193) × [472,482)`
before viewport translation.

The pinned SDL 2.32.10 `SW_QueueCopy` truncates float destination coordinates
and extents. For a scaled glyph entirely inside the output surface,
`SDL_PrivateUpperBlitScaled` clips the source/destination proportionally,
rounds the resulting source rectangle, then rescales it. It therefore need not
produce an exact crop of the original uncut glyph. Destinations extending beyond
the surface instead use a temporary full scaled copy. A29 independently inspected
these source paths and reconstructed the failing glyph/pixel math before
endorsing the narrow correction. No candidate painter existed during this
finding or correction.

The corrected fixture preserves exact clipped/full equality outside the
**current expected glyph-copy quads plus at most one device pixel**, computes
that region from source metrics, and counts inner glyph pixels/differences
separately. It also renders the complete expected label under the identical
caller clip and checks every surviving strong literal glyph pixel for contrast.
Invisible glyphs in a partial clip cannot satisfy a nonempty requirement; full
active cases continue to require all glyphs. Caller-exterior pixels, state,
scales, clip enablement, viewport and blend remain strict. The old bottom clip
can be below the smaller old lettering, which is recorded rather than treated
as a clipping-coverage success.

**This is a correction to a false prepaint fixture premise.** It changes no
before/after T1 allowance, full-frame content requirement, material threshold,
old fixture or old report. The separate paired checker still requires zero
escapes outside independently derived old/new glyph support and exact complete
frames for disjoint, empty and inactive cases.

## Fixture boundary and required subsequent work

The new source has explicit `--before` and default-new assertion modes while
`--case` frame generation stays independent of mode. It retains the established
padding-independent whole-model serialization and renderer observations, with
new both-manual state/focus inventory and source-derived glyph geometry. There
are 26 full active cases, eight partial glyph clips, disjoint/two enabled-empty
clips, five inactive layouts and two maximum-size 64×64 crops. No resource crop
can establish outside-region preservation.

All full active cases verify every label/value/hit rectangle, every correct
footage glyph, all value glyphs, opaque child probes and exact focus outlines.
The 18 canonical cases cover every focused manual drawbar, both edited/applied
bank routes, levels 0/4/8, held notes and pending-route state. Case 1 repeats on
its existing renderer after different states and on a fresh renderer. No real
window, audio device or MIDI input is involved.

Both retained material fixtures explicitly expect old Serif19 centered footage
in `full_frame_children`; the Upper call and Lower call will legitimately fail
after T1. Root must first retain those candidate failures, then obtain A32's
independent versioned assertion transition. Keep all original sources/hashes,
material comparisons, value/heading/focus/state/clip criteria and old evidence.
Do not skip the calls, permit either style, relax contrast, or enlarge material
support. The percussion fixture does not need a footage expectation change.

Root must qualify and preserve the genuine new before executable, then the
implementation owner may edit only the manual footage path. A29 independently
owns the paired support/verification; actual complete-frame and per-label visual
review remain mandatory after compilation. A25 authored no production painter,
CMake, shared navigation, dependency, commit or push, and performed no candidate
build or capture. Native baseline execution and candidate acceptance are
separately recorded by root and later owners. Physical fidelity, real display/DPI,
accessibility, audio and whole-interface 1:1 remain open.

## Observed genuine pre-edit gate

Root subsequently rebuilt the frozen corrected fixture and ran `--before`
against the unchanged accepted Lower painter. The
[retained root log](../development/2026-11-16-conversion-material/reports/typography-before-final.log)
reports **44/44 cases passed**, 23,499,525 checks, 59 state restorations,
11 clip companions, 583 exact non-glyph visible companion pixels, 563 glyph-domain
pixels and **125 explicitly retained clipped/full glyph differences**. It also
reports 936 opaque probes / 231,858 pixels, 2,094 literal glyph checks / 42,143
strong-ink samples, 26 focus cases / 25,690 cyan pixels and both deterministic
repeats. Root's [build log](../development/2026-11-16-conversion-material/reports/typography-before-final-build.log)
records the coordinated rebuild. A25 observed these logs and root's explicit
result message; root performed that successful build/run. The passing source
is the frozen fixture hash above. Root must still preserve/bind its executable
before A28 changes production. No further contract or fixture modification is
needed for this gate.
