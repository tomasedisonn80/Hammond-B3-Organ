# A09 — Native reference layout contract

Actual worker: `/root/w02_a09_visual_contract`; wave 2, assignment A09.

Owned outputs are this note and [REFERENCE_UI_DESIGN.md](../../REFERENCE_UI_DESIGN.md).
No production code, shared status, previous ledger, reference image or source
PDF was edited. No commit or push was performed by this worker.

## Inspected inputs

- `AGENTS.md`, current MIDI/UI scope and A05/A06 source reviews.
- Actual `UiModel.h`, layout/key generation and hit testing in `UiModel.cpp`,
  `Drawing.h/.cpp`, and `InstrumentView.h/.cpp`.
- The exact 1672 × 941 cover/page409 image, viewed through `view_image`:
  SHA-256 `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187`.
- Source PDF identity retained by the parent:
  `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
- The checkout advanced from `0f7b90037e51e101d8fa0bfe31af40209d751659` to
  `94d3470713a925d78ba09a080817b20500109833` during this contract assignment;
  concurrent changes were preserved. This note qualifies no later code.

Combined tool output initially truncated part of the long inherited source
notes; the remaining A05 section and full A06 note were read in separate bounded
outputs. This assignment does not recount their complete PDF readings as its own.

## Design decisions

The highest-value appearance change is the reference's main composition:
performance strip above adjacent drawbar racks, two keyboards beneath, warm
wood cheeks, centered serif heading and a right cabinet at widths of at least
1400. The current app instead puts the performance group beside the drawbars
and spans every keyboard across the whole window.

The contract defines one layout algorithm and shared rectangles, with exact
reference and minimum-size coordinates. It moves the five bank actions into
manual cheeks at taller sizes, then moves those same controls back above the
drawbars at heights below 820. The cabinet collapses before controls shrink.
Resize preserves identity, held notes and focus while ending the current
parameter drag under the existing interaction contract.

Parent integration explicitly approved these boundaries:

- Default 1280 × 900 remains; a 1672 × 941 capture demonstrates the wide reference view.
- Exactly one new ordinary UI control, MIDI settings, gives 46; all 45 core
  parameter identities remain unchanged.
- Existing SAVE/LOAD/HELP and AUDIO/MIDI/PANIC actions receive source-styled
  header tablets. No new tab state or fictitious view interaction is introduced.
- Cabinet lower space is a read-only service card, not a fake rotary/microphone
  control panel.

The artwork specification identifies a cabinet-only crop `(1132,174,466,397)`
and two wood-cheek strips. It explicitly excludes source MIC/SPEED controls
and the lower rail's baked DESIGN CONCEPT lettering. An asset worker must verify
the delivered crop/decoding identities; this contract does not create assets or
claim runtime texture execution.

## Geometry verification actually executed

An independent arithmetic probe evaluated the proposed formulas at:
1672 × 941, 1440 × 900, 1400 × 700, 1399 × 900, 1280 × 900 and 960 × 700. For each, the footer
ended exactly 16 logical units above the bottom, the manual rows were at least 82
units high, each drawbar panel exceeded 420 units, and natural-key widths
exceeded 19 units after applicable cheeks/insets. This checks the dimensional
proposal only; it does not validate the future renderer or text rasterization.

The first probe exposed a short-window issue: keeping the wide 90-unit header
and 10-unit gaps at 1400 × 700 reduced manual height to 71. The final contract uses
the dense 82-unit header and 8-unit gaps whenever height is below 820, regardless
of width, restoring 82-unit manual rows while preserving the cabinet breakpoint.
The original failed dimensional assumption was repaired before freezing the
contract; it is not reported as a native product failure.

All source/current APIs were inspected read-only. No executable build, runtime
image capture, MIDI operation, hardware test or pixel-equivalence experiment
was performed by A09.

## Handoff to implementation and independent acceptance

The layout owner should implement the shared formulas and relocate existing
control geometries without changing IDs/interaction laws. The renderer owner
should consume those fields, paint real dynamic controls and keep decorative
texture loading/lifetime outside audio. The asset owner should verify only the
approved source-art areas and preserve provenance. The app owner should add the
MIDI overlay with one shared paint/input/focus layout.

The independent visual/input worker must update old hardcoded C4 pixel locations
and 45-control expectations using reviewed new geometry, keep meaningful musical
assertions, capture real windows at the three declared sizes, and exercise both
layout breakpoints with held UI/MIDI notes. Actual 1:1 equivalence remains open:
the contract retains intentional semantic corrections, visible pedals, different
navigation text and rectangular rather than perspective playing geometry.
