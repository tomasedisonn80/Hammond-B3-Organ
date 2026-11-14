# A01 - Atlas foundation and reference constraints

## Assignment and source identity

- Actual assignment: `/root/w01_a01_atlas_foundation`, wave 1, A01, in the new
  `2026-11-14-reference-refinement` session.
- Scope: read every extracted PDF page **1-84 inclusive**, identify the complete
  plan and constraints relevant to the next native-interface work, and write this
  note. No product code, shared status, historical evidence or git history changed.
- Inspected source: commit `8bd999efc13e309b932e6ac41d72ceb7b9b80a5f`, tree
  `c37da16cedbb91573476a44bd4eafe5a5e30134a`.
- Canonical PDF: `Hammond_B3_Leslie_Research_Atlas_500pp.pdf`, 500 pages,
  SHA-256 `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
- Reading used the root-prepared `pdftotext -layout` extraction, split on form
  feeds. Seven complete, untruncated batches covered pages 1-12, 13-24, 25-36,
  37-48, 49-60, 61-72 and 73-84. This is full assigned text coverage, not a search
  or a reading of summaries alone.
- Original PDF pages **1 and 36** were also rendered with `pdftoppm -png
  -scale-to 1100` and visually inspected. Other figures in this range received
  textual/caption reading only; this note does not claim inspection of every
  image or of any external source cited by the atlas.

## Whole project contract from the opening pages

The target is one identified vintage electromechanical B-3 with an identified
AO-28 revision and a Leslie 122. Leslie 147, regional mains configurations,
modern digital organs and modified specimens require their own applicability
records (pp. 2-5, 13-18, 55-60). The complete sequence is M0 reference lock,
M1 deterministic framework-independent skeleton, M2 shared generator, M3 console
behavior, M4 scanner, M5 organ electronics, M6 cabinet electronics, M7 rotary
acoustics, M8 calibration, and M9 product/release (p. 5). The ten research waves
and this session's ten agent waves are distinct organizational schemes.

Three acceptance domains remain independent: **functional correspondence,
specimen/audio correspondence, and visual correspondence** (pp. 13, 18).
An image match cannot establish electronics or audio calibration; software tests
cannot supply a missing measured instrument. The source explicitly acquired no
physical instrument measurements (p. 2). Referenced companion catalogs, JSON,
prototype and physical inventory are statements in the atlas, not proof that
those files exist in this repository (pp. 2, 6, 12, 36).

Every physical parameter needs units, evidence kind, source locator, applicable
revision, conditions and uncertainty or an explicit unknown (pp. 12, 15, 21).
Missing is not zero. Mutable performance controls are separate from immutable
specimen identity; an evidence/profile revision must not silently reinterpret a
saved performance (pp. 15-18).

## Complete page coverage and implementation findings

| Read pages | Main subject | Consequence for continued development |
|---|---|---|
| 1-12 | Scope, source types, full contents, dependency order and agent contract | The cover is proposed interface art. Engineering specifications govern its controls; do not implement imaginary behavior merely because it appears in the picture. |
| 13-18 | Reference configuration and acceptance | Preserve named nominal/unmeasured status, immutable identities and separate behavior/audio/UI/deployment reports. |
| 19-24 | Source editions, page locators, transcription and rights | The 220-page factory collection and 73-page compilation with three 1995 redraws are different sources. Topology precedes component fitting; an unverified underside GIF remains an acquisition, not inspected evidence. |
| 25-30 | Generator/scanner/drawbar/percussion/Leslie patents | Patents describe alternatives and history. A 24-section patent scanner must not overwrite a selected production line. Shared phase, physical routing and no duplicated Doppler remain architectural constraints. |
| 31-36 | Cabinet appearance, geometry, materials and acceptance | Separate artistic appearance from measured geometry. Keep neutral and final-lighting review, explicit landmarks, camera and uncertainty. Retouched photographs cannot establish geometry. |
| 37-42 | Keys, nine contacts, timing and measurement | Each manual has 61 playing keys and 549 playing contacts. GUI animation cannot create audio timing. A MIDI surrogate is not a measured finger trajectory. |
| 43-48 | Persistent generator mechanics | 91 active sources differ from 96 physical disk positions and 48 rotating subassemblies. A note cannot reset shared sources. Mechanical parameters and production gear inventory remain incomplete. |
| 49-54 | Drawbars, presets, switches and control acceptance | Keep all 38 independent drawbar values, semantic IDs, inactive-bank memory, exclusive selector behavior, upper-B percussion eligibility and distinct global/percussion soft meanings. |
| 55-60 | Leslie family and geometry | Balanced 122 and unbalanced 147 are distinct electrical targets. Stationary drivers and rotating acoustic channels are separate. Generated imagery is art direction, not hardware authority. |
| 61-66 | Source identity, tuning, phase and numerical anchors | Tone ID, array index, terminal and MIDI note are separate. 12-TET, software-derived ratios and measured tuning are distinct profiles; shared phase continues through silence and UI changes. |
| 67-72 | Pickup source boundary and waveform representations | Nominal sine, measured terminal Fourier coefficients and physical flux-linkage models have different evidence requirements. Do not filter a post-filter capture twice. |
| 73-78 | Generator filters, revision and loaded response | Early filter groups and the 1965 bulletin are distinct. Microfarads must not become millifarads; source/load impedance and complex phase matter. Proposed numerical tolerance is not achieved physical fidelity. |
| 79-84 | Leakage topology, sparse models and identification | Frequency neighbors are not physical neighbors. Injection boundary, shared source state and raw captured residuals matter. The atlas supplies no measured 91-source coupling matrix. |

## Native-interface constraints that must survive the visual work

1. **Rendering observes state.** Page 34 requires a read-only snapshot and one
   stable control identity across perspective and flat views. Hiding meshes must
   not alter saved audio state. Page 40 requires audio-sample contact timing,
   bounded publication and GUI-frame-rate independence. Textures, mesh work,
   image loading, GPU waits and other rendering work stay off the callback.
2. **Controls remain musical.** Pages 49-54 define four nine-drawbar manual banks
   plus two pedal drawbars, preserved independently. C cancels; C#-A select fixed
   registrations; A#/B select left/right banks. Upper B alone is percussion
   eligible when enabled. Preset keys do not sound extra notes. The optional
   multi-latch physical model is separately identified; it does not invalidate
   the current explicitly exclusive software selector contract.
3. **Illustration cannot invent capabilities.** The cover visibly includes
   scanner and rotor controls. Pages 1, 6, 12, 13 and 18 require verified behavior
   and honest model status. Current unconnected scanner/Leslie controls must not
   appear to alter sound. Any reference-shaped unavailable control needs a clear
   unavailable state, or must remain artwork rather than an active control.
4. **Visual matching needs a declared target.** The cover is a generated UI
   concept, not a calibrated photograph of a specimen. Its pixel composition is
   usable as the requested art target. It cannot establish cabinet dimensions,
   materials or component interiors (pp. 6, 31-36, 58). Reference-pixel alignment
   and physical dimensional fidelity require different reports.
5. **Never hide an input regression behind polish.** Pages 40, 42 and 54 require
   invariant timing, state and routing; retain held notes through workspace,
   resize and presentation changes. Validate hit regions, release ownership and
   keyboard operation alongside actual rendered frames.

## Repository inspection and next concrete task

Read `AGENTS.md`, the current top sections of `docs/STATUS.md` and
`docs/NEXT_STEPS.md`, `README.md`, `docs/PLAN.md`, and the opening
`docs/research/ATLAS_REVIEW.md` navigation/contract sections. Inspected current
handoff/log sections and the native inspection data types. Focused code reading
covered `apps/standalone/UiModel.cpp` layout construction and
`apps/standalone/InspectionModel.h` plus count/unit sites in
`InspectionModel.cpp`. This was source inspection, not execution or verification
of the inherited test counts.

The current source computes manual height as the remainder after header,
performance, rack, toolbar, pedals, footer and gaps. At the reference size that
creates the previously documented shallower manuals. A dependency-ready M9 task
is to **reallocate wide-view space to the manuals, then refine panel/wood/brass
lighting from the preserved reference while retaining shared paint/hit geometry**.
Keep minimum-size and Flat layouts usable and preserve 24 preset keys, 147
playing keys, all sound parameters and saved-control semantics. The current
inspection formatter uses literal `targets` for held counts, so singular copy is
a small concrete companion repair.

Acceptance should retain: the exact reference asset and its crop/scale; an
actual 1672x941 native screenshot and agreed landmark table; before/after
manual-depth and panel-boundary residuals; minimum-size/Flat/focus/held captures;
and meaningful geometry, ownership, saved-state and presentation/audio
invariance tests from one coherent source. Update the README with the new actual
captures after those checks. Do not assert literal 1:1 equality from a subjective
improvement or compare only decorative source art against itself.

Separate follow-up inputs remain a complete desktop pointer/capture-return and
normal shutdown journey, actual pending-state visual evidence, native DPI and
accessibility, real MIDI/audio/DAW trials, scanner numerical G5 resolution,
revision-correct AO-28/Leslie graphs and a real capture corpus. None is completed
by this reading assignment.

## Executed work and limits

- Read all 84 assigned text pages using Python form-feed page indexing; every
  batch completed without output truncation.
- Rendered and viewed original PDF pages 1 and 36 using Poppler.
- Inspected the named source files and actual checkout commit/tree; verified the
  PDF SHA-256. This note is the only authored repository path.
- No product build, audio test, device test, external-source retrieval,
  measurement, push or physical-fidelity verification was performed by A01.
- The parent integrator owns dispatch accounting, shared documentation,
  implementation selection, all publication and final acceptance.
