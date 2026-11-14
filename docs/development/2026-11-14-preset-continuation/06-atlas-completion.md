# A06 — complete atlas reading, pages 421–500

## Scope and actual evidence

This is assignment **A06, wave 1**, in the 2026-11-14 preset continuation. It records one actual worker's complete reading of the final 80 atlas pages. It is not an implementation result, an executed audio test, or evidence that any M0–M9 milestone is complete. The atlas's ten research waves, this session's ten development waves, and its M0–M9 product milestones are different concepts.

Read [AGENTS.md](../../../AGENTS.md), the complete [project plan](../../PLAN.md), and the complete [next steps](../../NEXT_STEPS.md) before making these recommendations. This worker changed only this report; the parent owns production changes, shared documentation, integration, commits and publication.

| Identity | Value |
| --- | --- |
| Source | [Hammond_B3_Leslie_Research_Atlas_500pp.pdf](../../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf) |
| Edition | Evidence edition, 12 November 2026; 500 pages |
| File size | 21,248,265 bytes |
| PDF SHA-256 | `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769` |
| Inspected repository HEAD | `b79086f6bb0c42b97130c721c5c73c7c97a13887` |
| Inspected HEAD tree | `b0210756bf704017d9e56ebca97f935cc9c451c9` |
| Reader | Poppler `pdftotext` 25.03.0, layout extraction |
| Assigned complete coverage | PDF pages 421–500 inclusive, 80 pages |
| Combined extraction size | 217,733 UTF-8 bytes; 80 form feeds; 24,373 whitespace-delimited words |
| Combined extraction SHA-256 | `26b86051963ad59991bb0382488f4b0f584187d59468aafb182cd1921590d440` |

Every page was read through seven bounded extractions: **421–432, 433–444, 445–456, 457–468, 469–480, 481–492, and 493–500**. Each extraction was returned without truncation. Reproduction command, run separately for each pair:

```sh
pdftotext -f START -l END -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
```

The combined identity above comes from the same command with `START=421`, `END=500`. Selected pages were rendered with `pdftoppm -r 95 -singlefile -png` and actually inspected as images: **424, 437, 440, 447 and 486**. These cover profile activation, rendering/state ownership, the original control-layout study, the M3/M4 milestones, and the definition of done. Pages 428 and 450 were also rendered as scratch intermediates but were not separately visually inspected; their complete text was read. No claim is made that every page was visually inspected. Reading the source directory does not mean visiting or independently revalidating each external reference.

## Complete section coverage

| Pages | Chapter / content | Development consequence |
| --- | --- | --- |
| 421–426 | 069: service and evidence interface | Keep source values, proposals, model values and unknowns distinct. Validate immutable candidates off the audio thread, activate the exact version, and display acknowledged state. Inspection must not change sound. |
| 427–432 | 070: geometry, materials, cameras and asset delivery | Reference appearance is a visual target. Retouched images and generated concepts cannot establish dimensions, wiring or measured material properties. Stable semantic control identities survive mesh, camera and level-of-detail changes. |
| 433–438 | 071: accessibility, resizing and rendering | Focus, latched preset, edited bank and sounding route require distinct states and cues. Both visual skins share commands and bounded snapshots. Native accessibility and scale behavior require actual platform evidence. |
| 439–444 | 072: earlier executable control study | The atlas's fake-DOM tests establish limited interaction behavior. Its original layout is not an application screenshot. It specifies 12 reversed preset keys plus 61 playing keys per manual, independent bank editing, route-only Cancel and ordinary exclusive selection. |
| 445–450 | 073: M0–M9 implementation plan | Dependency-ready M3 behavior can proceed using a named surrogate before a complete AO-28 graph exists. M8 physical calibration and M9 product qualification have separate gates. |
| 451–456 | 074: agent implementation contract | Deliver useful inspectable software with bounded claims, typed profiles, explicit assumptions, immutable publication, reproducible commands and honest status. Freeze actual public identity before compatibility claims. |
| 457–462 | 075: risk and dependency triage | Block only the affected claim. Missing physical data does not stop unrelated runtime or control work. Preserve known failures, unresolved connectivity and corrected source findings. |
| 463–468 | 076: technical corrections and misconceptions | Preserve continuous shared source phase, per-contact histories, shared percussion readiness, retained masked contact state and non-panic Cancel. Inventory and static checks do not establish physical or host fidelity. |
| 469–474 | 077: physical acquisition plan | The 88 task families are acquisition requirements, not acquired photographs or measurements. Preserve original pixels, scale/calibration, specimen identity, rights and independent review. |
| 475–480 | 078: rights and delivery review | Engineering authority and permission to redistribute are separate. Inspect actual deliverables, dependency versions and asset ancestry. The atlas's historical review is not a license audit of the new build. |
| 481–486 | 079: acceptance and definition of done | Each claim names its boundary, inputs, setup, criterion and result. Preserve failed, blocked, not-run and inconclusive outcomes. Revisions invalidate affected gates; a new threshold cannot retroactively pass an old result. |
| 487–492 | 080: final research handoff | Research delivery is not a completed engine or calibrated instrument. Continue source/profile compilation and acquisition in parallel, then qualify each implementation layer with its own evidence. |
| 493–500 | Complete source directory | Read all listed primary-source references and locators. They span factory documentation, DSP, event semantics, measurement, runtime, UI, accessibility, provenance and licensing; they are references to inspect when a specific implementation decision requires them. |

## What the whole project plan requires

The target is a source-identified vintage B-3/AO-28 and a specifically identified Leslie 122, with compatible offline, standalone and VST3 delivery. Other circuit variants require separate profiles. The plan distinguishes engineering correctness, a nominal or synthetic model, measured calibration, a bounded fidelity claim, and release readiness. It explicitly permits useful provisional implementation while the physical acquisition program remains open. See pages 445, 451, 454, 481 and 486.

| Milestone | Required implementation | Evidence that can close its engineering scope | Remaining physical/product boundary |
| --- | --- | --- | --- |
| M0 — reference identity | Name the specimen/revision, cabinet variant, modifications and intended ports; retain unknowns. | Consistent, traceable reference/profile manifest. | Missing specimen identity and measurements stay unresolved. Page 445. |
| M1 — deterministic core | Typed immutable profiles, compiler, offline renderer, event ordering, diagnostic ports and bounded lifetime. | Rate/block invariance, ties, half-open ranges, zero-frame flush without advancing clocks and exact replay. | A functioning renderer does not calibrate its model. Page 446. |
| M2 — shared generator | 91 continuously running sources, separate source/terminal/MIDI identities and explicit routing. | Phase, pitch, foldback, mapping and coherent-sum tests. | Production frequencies, pickup waves, phases, levels and leakage need identified evidence. Pages 446, 459, 464. |
| M3 — console behavior | Contact trajectories, four retained manual banks, pedal controls, preset routing/latches, shared percussion and expression. | Held-note switching, partial release, repeated notes, bank changes, non-panic Cancel and preserved state history. | Physical loading, contact timing, expression and percussion response remain separate. Page 447. |
| M4 — scanner | Loaded 18-section LC network, 19 ground-referenced outputs and scanner routing; count chorus return once. | Independent loaded AC agreement, transient and stability tests under declared reconstruction. | Numerical agreement is not specimen agreement. Pages 447, 465. |
| M5 — organ circuit | Revision-specific connected AO-28, loaded linear model followed by qualified nonlinear stages. | Independently reviewed graph and operating points, loaded comparisons, alias/state migration checks. | Placement inventory is not a connected netlist; dry G–G measurements precede downstream fitting. Pages 448, 458, 488. |
| M6 — Leslie electronics | Specific 122 amplifier/transformer/crossover with real branch/load boundaries. | Polarity, loaded electrical behavior, numerical stability and independent comparisons. | A nominal resistor is not measured driver impedance; 147 stays separate. Pages 448, 460. |
| M7 — motion and acoustics | Independent horn/drum trajectories, physically consistent multiple microphones and retarded propagation. | Trajectory/time ownership and single-owner effect tests. | Geometry, acceleration, directivity and room/microphone data require captures. Pages 449, 467. |
| M8 — calibration | Fit upstream subsystems first, preserve group-held-out data and declare criteria before evaluation. | Reproducible optimization and held-out measurements with uncertainty and identifiability analysis. | Unknown uncertainty cannot be zero; an inconclusive comparison is not a pass. Pages 449, 455, 484. |
| M9 — product | One core across adapters, stable automation/state, native UI, packaging and release material. | Actual validators, DAWs, devices, callback/lifetime behavior, state migration, accessibility and platform builds. | Compiling the adapter, static assertions or screenshots do not close host, physical device or accessibility gates. Pages 450, 456, 485. |

Acquisition proceeds in parallel. M3 behavior and M4 numerical work may proceed together after M2 identities and ports are stable. An early adapter can expose the core after M1/M2 without implying M9 completion. Physical failures should remain attached to the specific affected acceptance boundary, rather than stopping every other milestone (pages 447, 450, 454, 457 and 492).

## Recommended immediate slice: exclusive fixed registrations

The current next-step document already identifies the missing M3 selector. The final atlas chapters support making it the next bounded production change. Page 440 explicitly chooses ordinary exclusive selection for the control prototype, while keeping simultaneous physical preset latches as a future engine requirement. Page 447 requires preserving held-key state and shared percussion history. This gives a concrete scope that can be implemented and tested without pretending to solve physical latch loading.

1. **Use one explicit sounding selector per manual.** Its domain must distinguish Cancel, each of that manual's nine fixed registrations, A-sharp and B. Do not infer the sounding registration from whichever drawbar bank happens to be visible. Use the source-qualified fixed-registration table already identified by the implementation contract; the existence of 18 fixed registrations does not prove the table values independently match a factory specimen.
2. **Retain all four drawbar banks and pedal settings.** Choosing a fixed registration must neither overwrite the selected manual's A-sharp/B storage nor edit the other manual. Editing an inactive bank should become audible only when that bank is routed. Keep semantic parameter identity independent of its screen position (pages 433, 440 and 442).
3. **Preserve musical ownership and continuous history.** Preset selection and Cancel are routing events, not note-off or panic. Held playing keys, pedal ownership, shared source phase and relevant percussion state remain intact. In particular, a trip through a fixed registration must not grant a fresh percussion envelope merely by returning to upper B. Physical behavior beyond the declared exclusive mode remains a measurement gate (pages 440, 447 and 464).
4. **Make compatibility append-only.** The current next-step document identifies 45 existing public controls and requires their identities, UUIDs and legacy fixtures to remain stable. The proposed two new route parameters and control state version 4 need explicit migration rules before implementation. Version 4 is this session's design, not a requirement quoted from the atlas; no new container-format version is proposed. Preserve the old bank-selected route when loading a legacy state, reject invalid selectors atomically, and retain unrelated values and state on failure (pages 450, 453 and 456).
5. **Use the same selector throughout the engine, adapters and native UI.** Route actual UI actions through the production command path. Define same-sample ordering and native normalized enumeration endpoints. Show accepted state rather than making the renderer a second audio-state owner (pages 424, 442 and 453).

### Concrete acceptance for this slice

These are proposed tests, not results executed by A06:

| Case | Required observable result |
| --- | --- |
| All 18 fixed registrations | For each manual/registration, the active drawbar weighting agrees with its identified table while the underlying generator clock continues. |
| Fixed preset versus equivalent retained bank | With equivalent registration values and declared equal state/history, outputs agree under the same event timeline. Account explicitly for upper-B percussion eligibility. |
| Switch during held chords | Note owners/contact state survive; the route changes at its declared sample without an artificial release/retrigger or source reset. |
| Cancel during held chords and pedals | Only the chosen manual route cancels. Other manual/pedals and held-key ownership remain intact. |
| Inactive bank edits | Edited values persist without affecting the currently sounding fixed registration; selecting the edited bank subsequently uses those values. |
| Upper B → fixed → upper B | Shared readiness/recharge and held-note history follow the declared M3 semantics; the switch does not manufacture a new trigger. |
| Same-sample input and variable blocks | Ties use the documented deterministic order; different block partitions and zero-frame flushes preserve the event result and clock contract. |
| State and public identity | Legacy versions migrate to the same audible route; new selectors round-trip; corrupt/truncated/out-of-domain state is rejected without partial mutation; all old IDs/UUIDs stay unchanged. |
| Actual native preset interaction | Both 12-key reversed-color strips select the intended semantic route, expose a clear selected state and preserve live MIDI/playing-key ownership. |

A passing set would close the declared exclusive-routing implementation slice. It would not close all of M3, physical multi-latch behavior, factory table independence, contact loading, component-exact expression/percussion or calibrated sound.

## UI/UX implications of the reference requirement

The user has requested a 1:1 visual target. This reading supports a more faithful native control surface and an explicit README comparison, but cannot itself establish a completed match. The inspected original layout on page 440 has **12 reversed preset keys and 61 playing keys per manual**, with the preset zone visibly separate from the playing keys. Four retained manual banks and two pedal controls remain semantically present even when a compact editor shows fewer controls. The original diagram is labeled a design study rather than an application screenshot.

Keep **keyboard focus, selected preset, edited bank and sounding route** distinguishable (pages 433 and 435). A bank-edit toggle must not silently select an audible registration. The visual state should follow the production selector and command acknowledgment. Keyboard, pointer and any automation path must address the same semantic control. Rendering, resizing, reduced motion, editor closure and graphics failure must not change source clocks, routing, notes or rotary trajectories (pages 436–438 and 442).

For the README update, pair the identified original reference with an actual screenshot produced by the current native build. Name the source revision, build configuration, image dimensions, UI scale and capture procedure. Document measured layout/control differences and the next concrete adjustment. A static SVG or HTML study cannot substitute for observing the live C++ editor. This worker has not inspected the cover/reference image itself or the current editor; it therefore does not assess the current visual distance to the cover.

Operational labels should remain legible on stable surfaces, with focus and selection cues that do not rely only on color. The atlas proposes 44×44 ordinary controls and discusses qualified exceptions for dense keyboard targets; it does not justify declaring an entire instrument surface exempt. Final composited contrast, hit regions, resize behavior and native accessibility need their own checks. Page 437's visually inspected diagram assigns one semantic view model to the flat/3D skins and native accessibility, backed by bounded state snapshots and commands. A photorealistic surface alone cannot establish those behaviors.

Pages 427 and 431 allow reference palette/material styling while retaining verified control placement. They explicitly prohibit treating generated or retouched appearance as dimensional or circuit evidence. No new image, mesh, measured geometry or rendering benchmark was created by this assignment.

## Durable continuation and release rules

The following should remain enforced by the shared `AGENTS.md`, session ledger and handoff documents; this report does not duplicate ownership of those shared files:

- **Start with current identities.** Read the current instructions, plan, next steps, actual source/remote state and the smallest relevant evidence section. Do not inherit a prior agent's claimed test outcome without its exact source, command and retained result.
- **Record the actual worker assignment.** Record its wave, scope, file ownership, input identities and delivered result. Count newly dispatched workers. Atlas research workers, prior sessions and milestone numbers cannot satisfy this session's 60-agent accounting.
- **Bound every claim.** Separate documentary evidence, mathematical/numerical checks, production implementation, measured specimen fit, actual native/host/device behavior, visual comparison and release readiness. Preserve `failed`, `blocked`, `not run`, `inconclusive` and explicit exclusions alongside passes (pages 451, 481 and 486).
- **Keep a resumable handoff.** State what changed, why, how it was checked, exact results and limitations, current milestone position, next dependency-ready step, required commands and unresolved inputs. Include schema/parameter/state changes and migration behavior. The parent integrates and publishes coherent changes rather than letting independently edited shared status drift.
- **Preserve source qualification.** Each physical assertion needs a revision/specimen/variant and a page or capture locator. Unknowns retain a reason and provenance. Nominal/synthetic surrogates must remain named and replaceable. Do not turn a proposed value into a measurement because it appears in a working slider (pages 422, 424, 452 and 489).
- **Preserve realtime boundaries.** Parsing, compilation, allocation-heavy setup, file/asset work and storage retirement stay outside processing. The audio thread owns DSP state; readers consume copied bounded snapshots. Publication and acknowledgment need version/lifetime discipline (pages 424–425 and 453).
- **Retest affected gates after changes.** Preserve the earlier report and identify the dependency that changed. A passing build or new screenshot cannot erase an unrelated scanner failure, missing physical corpus or unexecuted native accessibility test. Threshold revisions create a new study, not a retroactive pass (pages 483 and 486).
- **Publish verifiable outcomes.** Record source and artifact identities, tool versions, actual build/test commands, retained outputs, staged rights/dependency notices and supported configurations. A successful push and observed remote revision are separate from CI completion, host qualification, signing or a release (pages 450, 456 and 479–486).

## Assignment result and next handoff

**Completed:** all pages 421–500 read in full, source and extraction identities verified, five relevant pages visually inspected, and current plan/next-step constraints reviewed. The selected diagrams confirm the text's route/state distinctions and separate acceptance gates. No production implementation, audio test, native UI capture, physical measurement, external-reference audit, Git mutation or release qualification was performed by A06.

**Recommendation to the parent:** proceed to independent review of the exclusive preset-selection and state-migration contract, then implement and test the engine/adapters/native preset strips against that reviewed contract. Update the README with actual reference/editor evidence and retain explicit remaining visual differences. Preserve existing scanner, AO-28 connectivity, physical acquisition, platform and native accessibility gates as separate open work. The next agent should be able to resume from the source-pinned contract and retained test evidence without rereading an unstructured session transcript.
