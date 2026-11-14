# A09 — Reversed preset-key UI contract

Actual assignment: `/root/w02_a09_ui_contract`, wave 2 of the new preset
continuation. Owned outputs are this note and
[PRESET_UI_DESIGN.md](../../PRESET_UI_DESIGN.md). No production file, reference
asset, source PDF, shared status, README, prior record or Git history was changed.
The integrator owns acceptance, shared documentation and publication.

## Inspected source and current state

Read the standing `AGENTS.md`, current README/status/next steps, M0–M9 plan,
atlas-review consolidation, latest development-log entry and MIDI/UI operational
handoff. Read the new preset selection proposal, A05's complete product-source
report, `UiModel.h/.cpp`, relevant `InstrumentView.h/.cpp`, and the Drawing
interface/implementation. The source baseline was
`b79086f6bb0c42b97130c721c5c73c7c97a13887`; read-only `git ls-remote origin
refs/heads/main` observed that same remote main. Existing concurrent contract and
session changes were preserved. No Git mutation was performed by this worker.

Directly extracted and read complete PDF pages 415 and 440 with Poppler
`pdftotext -f N -l N -layout … -`. These pages confirm separate 61+12 key counts,
four retained banks, 25 pedals, independent editing/routing, routing-only Cancel
and the distinction between a control study and an actual native implementation.
This assignment does not recount A05's 84-page reading as its own.

Directly viewed both full 1672×941 files using `view_image`:

| Input | SHA-256 | Observed role |
|---|---|---|
| [Original cover JPEG](../../design/atlas-cover-reference.jpg) | `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187` | Source material/composition; incorrect generated legends are not authoritative controls. |
| [Prior actual capture](../../../examples/demos/standalone-midi-ui-v1/images/reference-1672x941.png) | `239a38c6f47079e442c4ecb0c62c8e38c81d032153be93d892bc854966835fc7` | Existing runnable surface; visible shallow panels/caps and five cheek buttons per manual. |

An earlier combined output was truncated; the two full images and individual
PDF-page outputs were then inspected separately. A first guessed
`src/standalone/InstrumentView.cpp` path did not exist; `rg --files` located the
actual `apps/standalone/` sources before inspection. These were source-reading
issues, not build or application failures.

## Frozen implementation recommendation

Append `UiControlKind::PresetKey=19` without renumbering existing kinds. Its
semantic identity is manual plus index 0–11 with canonical unused bank A. The
indices exactly match Cancel, nine fixed registrations and adjustable A#/B.
Keep EDIT A/B independent. Removing six PLAY A/B/Cancel geometries and adding
24 keys produces exactly 64 ordinary controls, preserving the existing bound
and all 147 playing-key identities. Presets never own notes.

Preserve the existing row formulas, 1400 cabinet breakpoint and 820 EDIT-placement
breakpoint. Give both manuals a preset cheek at every admitted size, using
`clamp(player_width*0.15,156,168)`. Compact EDIT buttons remain in their rack;
tall EDIT buttons occupy the top of the cheek. All key rectangles are generated
once from a stored preset-panel rectangle. Reverse the colors of seven naturals
and five accidentals; paint naturals before accidentals and hit accidentals
first. Derive focus from the exposed area of those same bounds.

Applied snapshots own sounding highlights; edited-bank identity and desired
controls remain separate. C never latches. Pending commands mark a requested
target without falsely changing the sounding key; rejection restores actual
state and visible status. Stored percussion remains visible while fixed routes
are ineligible. Keyboard access includes all 67 Tab stops, arrows/Home/End,
cross-manual navigation and Space/Enter activation without note ownership.

Native materials can move toward the reference through deeper sockets/cap
fronts, narrow highlighted shafts, neutral charcoal and thicker key fronts
inside shared rectangles. Keep source crops decorative and the cabinet status
factual. Full perspective, missing audio features and actual native semantic
accessibility retain separate gates; neither source art nor this specification
is a new application screenshot or 1:1 acceptance.

## Arithmetic verification actually executed

Ran an independent Python calculation of the documented layout over the
49 combinations of widths 960, 961, 1280, 1399, 1400, 1672, 8192 and heights 700,
701, 819, 820, 900, 941, 8192. Asserted positive preset heights and manual natural-key
widths, then printed minimum/default/reference, both breakpoint cross-products,
960-width transitions and extreme-aspect anchors. The detailed target-size
values are retained in the design contract.

The joint 1400×820 case is the tightest tall cheek: manual height 104.600,
preset height 42.600, natural width 20.000, accidental width 12.000 and accidental
height 26.412. The narrowest tested playing natural at that breakpoint is 19.548.
At 960×700 the manual height is 82, preset height 52 and natural/accidental widths
are 20/12. At 1672×941 they are 138.480, 76.480 and 20.423/12.254 respectively.
All 49 dimensional combinations passed those arithmetic assertions. This probe
does not validate a future C++ implementation, float rounding at every admitted
size, text rasterization, pointer edges or real UI input.

After writing both owned documents, a Python local-link check resolved all
13 Markdown targets successfully (10 in the design contract, 3 in this note).
No executable build, CTest, application capture, audio comparison, native
accessibility or hardware operation was run by this assignment.

## Next task and acceptance

The integrator should freeze this contract with the core and parameter/state
contracts before implementation. UiModel and rendering workers can then own
separate production files. Independent acceptance must check all 24 controls,
147 notes, exact-capacity focus traversal, overlap boundaries, command rejection,
source-identified screenshots and both breakpoint cross-products. Update existing
hardcoded pixel/focus fixtures from the reviewed new geometry while preserving
their musical assertions. The integrator updates README with the resulting
actual captures and residual reference differences, then documents, commits,
pushes and verifies the completed coherent source under the standing rule.
