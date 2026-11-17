# H1 checker correction: independent admission

**A27 follow-up, 17 November 2026: admit the narrowly corrected checker for a
fresh genuine-baseline demonstration.** Exact admitted tool SHA-256:
`098398562f1b9134739ff9bd6f015892c10ca7ad707ab4703d84051883299f1b`.
This is the same A27 worker, with no additional worker credit. It does not
accept an H1 painter or replace the required complete corrected baseline run.

The [H1 contract](../design/HEADER_MATERIAL_H1_CONTRACT.md), SHA-256
`07d64498a14431b64742d79e7fbe4d2ac71d77fe51d09f71c638f52594fd9282`, and
[accepted protocol admission](HEADER_MATERIAL_H1_ADMISSION.md), SHA-256
`c2e7a216a11d7065262702aaee8f7ec766171a4571cc51c2f9bf7edd021cd6e5`, are
unchanged. Both corrections restore source-defined oracle behavior. No contract
revision or relaxation of the 103 material inequalities is required.

## Preserved failure and exact inputs

The original [checker](../development/2026-11-16-heading-title-continuation/inputs/compare_header_material-initial.py),
SHA-256 `16476f7050b88208a4c63e4e08ea1020419395f838abddf4b4bcb68d43576059`,
and its [failed complete baseline report](../development/2026-11-16-heading-title-continuation/reports/h1-baseline-demonstration/report.json),
SHA-256 `206229c94cefc4216c12556c224405084e35886dff3e0f07bb2f0e5671fb12dd`,
remain unchanged. The [root rejection receipt](../development/2026-11-16-heading-title-continuation/reports/h1-baseline-checker-rejection.json)
records 137 native invocations in 295.712 seconds. It remains a failed run.

Independent read-only inspection reproduced the retained report's failure
classification: all 56 active pairs fail the same independent utility-geometry
expectation; four Help-focus cases additionally fail the cyan-position oracle;
only case29 uncut and case35 main fail the absolute warm-ROI typography screen.
All **64 paired RGBA hashes and complete-model hashes match**, with zero
reported differing pixels. All retained control probes, rules, opaque glyph
cores, literal final ink and strong-glyph checks pass. The four repeats have
exact RGBA/state and fail only the same metadata expectation. All 103 numerical
baseline outcomes reproduce **44 pass / 59 fail**.

The production painter remains accepted T3 revision 2,
`10865a6bad39bc0a254b8b3f4cf6b013bef48770a2b39c7e9f9a70f438d56366`; H1 is not
implemented. The genuine 48-case fixture remains
`a6b65d06067d8941e44ef8680f309433a3c82ce1d6bd54d6f3f5bf8d4bde82d2`. Root's
separate default run records 10,447 checks and 163 paintings. This review
executes neither that fixture nor the comparator.

## 1. Restore the actual utility identity-to-position mapping

`UiModel.h` defines the semantic numeric identities; unchanged
`make_reference_composition` in `UiModel.cpp` supplies this insertion order and
these canonical rectangles:

| Control | Kind ID | x,y,width,height |
| --- | ---: | --- |
| Save | 11 | 1312,25,88,28 |
| Load | 12 | 1409,25,88,28 |
| Help | 14 | 1506,25,88,28 |
| Audio | 13 | 1312,61,88,28 |
| MIDI | 18 | 1409,61,88,28 |
| Panic | 15 | 1506,61,88,28 |

The initial checker incorrectly ordered Audio/MIDI/Help at the last top slot
and first two bottom slots. The correction changes only that literal utility
inventory to Save, Load, Help / Audio, MIDI, Panic. It preserves all ten
controls and their source geometry; it does not learn positions from a frame.

An independent binary32 endpoint and SDL fill calculation for Help's four
source outline rectangles reproduces the *actual* retained cyan mask hashes,
bounds and counts on both sides of all four affected cases:

| Case | Half-open output bounds | Cyan pixels |
| --- | --- | ---: |
| 1 | 2272,54,2404,96 | 1,008 |
| 4 | 1904,49,2014,85 | 564 |
| 7 | 2607,60,2758,107 | 1,152 |
| 44 | 1506,25,1594,53 | 448 |

Thus the source correction also repairs the Help focus oracle without dropping
a cyan pixel, reducing coverage or expanding support. The all-position equality
requirement remains exact.

## 2. Restore the inherited warm-ROI gate's blend domain

The original T3 canonical warm-ROI cohorts are typography cases0–17,
percussion cases0–15 and typography-clips case46. Direct source inspection
shows all use `SDL_BLENDMODE_BLEND`: the first typography cases have no clip,
percussion retains `Drawing::initialize`'s blend mode, and clips case46 is an
even-index BLEND case. The unchanged native material header suite also uses
Drawing's BLEND state; `Target::configure` changes transforms and clips, not
blend.

The initial H1 checker passed a fabricated `suite="clips", case=46` identity
to `warm_geometry` for every canonical uncut H1 frame, including NONE-blend
case29's companion and case35. Under NONE, the unchanged Original panel's
bright grain writes RGB `(212,205,190)` with its low alpha directly through
`Drawing::rect` and SDL software fill. That RGB passes the inherited warm-ink
predicate even when it is material rather than lettering. The original
RGB-only ROI measurement therefore reports 32 caption column groups and
enlarged title/caption bounds in those two cases, while all 29 independently
predicted strong glyphs and 3,804 opaque-core pixels retain correct ink.

The correction adds the source-based predicate `warm_required = spec["blend"]
== 1`. It keeps the **raw warm observations**, including their failed geometry
flags, and explicitly reports their applicability. Only the inherited
whole-ROI warm geometry is non-gating for NONE. This corrects an unintended
extension of the prior BLEND oracle; it does not select exceptions by case ID
or use candidate pixels to decide applicability.

The **4,500–6,000 density band and at-least-40% improvement inequality remain
required on NONE** as well as BLEND. Every NONE frame also retains the complete
independent control, cyan focus, rule, 29-glyph strong-coverage, opaque-core,
literal RGBA, model, renderer, clip and operation-derived support requirements.
The complete unchanged **1,317-assertion native material suite**, including its
24 complete and 16 clipped header cases, remains mandatory. No warm threshold,
geometry tolerance, material inequality, support pixel or state requirement
changes.

## Byte review, limits and handoff

The complete old/new tool diff contains exactly two hunks: the utility literal
order and the explicit warm-geometry applicability/reporting code. Independent
AST comparison finds only `canonical_typography` changed among 57 named
functions/classes; the other 56 are identical. The support, matrix, numerical,
child/core, cyan, metadata-validation, transport, provenance, repeat and native
material execution functions are unchanged. The source-based utility constant
feeds the existing exact checks.

Rehashed the accepted H1 contract/admission, original failed checker/report,
new checker, accepted T3 painter and genuine fixture. The earlier A27 note
remains `66bba0724f7932e89f1201bef372add611e64b7383e92110e8930fa05ef6b10d` and
was not edited. Only this new review was written. Read-only work used source
and JSON inspection, hashing, AST comparison and independent coordinate/mask
arithmetic; no production/tool/test/contract/CMake edit, native execution,
build, capture, candidate simulation, commit or push occurred here.

Root must now run the complete corrected baseline into a **new evidence
directory**, preserving the original failure. Require the same 48 main pairs,
16 companions, four repeats, all complete state/source checks and the original
44/59 numerical baseline outcome. A successful new result qualifies this
checker baseline only. Assign A34's H1 painter only after that result is
reviewed and the existing genuine-before prerequisites remain satisfied.
Candidate numerical, containment, timing, full-frame visual and platform gates
remain unrun; whole-interface **1:1 remains unmet and unwaived**.
