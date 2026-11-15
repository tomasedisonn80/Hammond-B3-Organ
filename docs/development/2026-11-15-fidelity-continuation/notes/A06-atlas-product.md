# A06 - Complete atlas product and acceptance reading

Actual worker: `/root/w01_a06_atlas_product`, wave 1, fidelity continuation,
15 November 2026. Owned output: this note only. The inspected checkout starts at
`878d3ce82a10a0ae335dab377683ec543f194957`, tree
`7d63b272d7dd04be65869db5687a1d7f29994e1a`. The live integrator's
[checkpoint](../CHECKPOINT.md) and [assignments](../assignments.json) own later
changes, dispatch counts, builds and publication. This is a fresh reading for
this session, not credit for an earlier completed sixty-worker batch.

## Reading identity and method

I read the entire [AGENTS.md](../../../../AGENTS.md) and
[M0-M9 plan](../../../PLAN.md), then every page of the assigned atlas range
**421-500 inclusive**: chapters 069-080 and all eight source-directory pages.
The complete layout extraction was consumed in bounded page groups; a truncated
combined display was reread before continuing. No page was intentionally skipped.

| Input | Observed identity |
| --- | --- |
| Preserved source PDF | `Hammond_B3_Leslie_Research_Atlas_500pp.pdf`, 21,248,265 bytes; SHA-256 `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769` |
| Assigned complete text | `/workspace/scratch/63071f51f1e4/atlas-text/A06-pages-421-500.txt`, 219,413 bytes, 24,773 whitespace-delimited words; SHA-256 `ca10233e4521401e744cfc16ed0957cb318ff9e3d8489cac688f25bf9b5bec6e` |
| Coverage check | Exactly 80 contiguous page markers, 421 through 500, with no missing or repeated page number |
| Visual inspection | Native PDF pages 434 and 488, rendered with Poppler at a 1,400-pixel longest edge and opened as images |
| Read-only production check | `apps/standalone/MidiDevice.cpp`: SHA-256 `48ee8dbe72a1a243fcc3bc1037df782690894cb26ef2291ba253611b48bfc324`; `apps/standalone/UiModel.h`: SHA-256 `d94e90be25812c6d21b61f37f2b0547704d14866c45fbbb21131ec70b6389bd3` |
| Read-only upstream comparison | Pinned external RtMidi 6.0.0 `RtMidi.cpp`: SHA-256 `184d775e88e5d73b079897363fb42af155122e879f0bc9254a1c7edae4eadb3c` |

I also recovered the current README, status, next steps, latest development-log
entry, product handoff and session records, and checked the relevant native-close
source and retained review. The source directory was read as a directory; I did
not newly retrieve or independently verify every external publication or license.
The atlas's referenced companion reports and source files do not become present
repository artifacts merely because this note has read their names.

## Complete chapter coverage

| Chapter and pages | Findings and implementation consequence |
| --- | --- |
| **069, 421-426: Service inspection** | Separate represented assembly, evidence, running model and unavailable observations. Component designators, stock numbers and model-module IDs are distinct. Comparisons require matching terminals, units, loads and clocks. An editable draft is not the active immutable profile; stale worker results cannot activate a newer draft. Telemetry uses bounded snapshots, reports lost/stale coverage and leaves musical commands intact. The five proposed Service gates concern unknowns, variants, stale results, probe mismatch and accessible status; the PDF does not execute them. |
| **070, 427-432: Assets and presentation** | Preserve the distinction between specimen geometry and artistic styling. Retouched P005/P020 cannot provide dimensions. Authoring-to-glTF conversion is `(x,y,z) -> (x,z,-y)`, applied once; asset, manufacturer and automation IDs remain distinct. Materials are appearance recipes, not measured chemistry. Text and interaction proxies must remain usable independently of exposure or LOD. Renderer budgets and 60/30-fps targets are proposals. Page 431 explicitly allows the concept's charcoal/brass direction without reproducing incorrect controls. The future asset pack needs actual provenance, validation, memory/timing and retained unknowns. |
| **071, 433-438: Accessibility and scale** | One semantic binding model must serve both visual skins and native accessibility. Four banks retain identities independently of the displayed bank and sounding preset. Keyboard navigation, note ownership, gesture boundaries and direct controls require actual platform behavior. Page 435's contrast/target references are proposed evaluation criteria, not a conformance result. Page 436 prioritizes collapsing the cabinet before reducing operational text and deriving visual, hit and accessible bounds from one transform. Reduced motion never becomes an audio brake. Screen-reader, host and display-scale journeys remain separate gates. |
| **072, 439-444: Historical UI study** | The atlas reports 28 JavaScript state checks after three corrections, under limited DOM/event/storage doubles. Its browser execution was blocked. The corrections preserve incremental drag movement when Shift changes, truthful reduced-motion state and one current roving-key Tab entry. The pictured control study is explicitly a diagram, not an observed HTML/native screenshot. Host gestures, native dispatch, audio integration and accessibility need their own implementation and evidence. Historical 36-drawbar retention, 61+61 playing keys, 24 presets and 25 pedals are separate inventories. |
| **073, 445-450: M0-M9 sequence** | M0 locks identity/evidence; M1 establishes prepared storage, deterministic events and offline rendering; M2 keeps 91 continuous shared sources; M3 supplies console semantics; M4 supplies independently compared scanner behavior; M5 closes the coupled dry organ; M6 models Leslie electronics; M7 adds moving radiation; M8 fits identified/held-out evidence; M9 qualifies actual products. Missing physical inputs do not stop explicitly identified nominal engineering. M6 reference work may proceed during M5, but cabinet EQ cannot compensate a dry-organ error. |
| **074, 451-456: Agent operating contract** | Useful provisional software is an explicit deliverable tier. Unknowns, evidence classes, units and effects ownership survive compilation. Preparation, allocation and reclamation remain off the audio callback, with mutable runtime ownership and retirement acknowledgments defined. Each milestone hands over source/data identities, actual commands/results and unresolved inputs. Actual host mapping, state migration, packaging, rights and signing remain distinct from compilation and synthetic results. The historical 62-entry proposed registry does not override today's implemented 47-parameter contract. |
| **075, 457-462: Risk register** | Prioritize reference acquisition, the deterministic runtime and complete AO-28 connectivity in parallel. The 124 placement/section records are not a solver graph or installed-package count. Dry source/control/scanner boundaries precede cabinet/microphone fitting; nominal crossover topology supplies neither actual impedances nor losses. Close the claim affected by a blocker, and keep completed documentary corrections closed. Page 461's statement that UI-state checks are pending conflicts with later reconciled results; this is already preserved as ERRATA E04. |
| **076, 463-468: Technical corrections** | Preserve repeated manual foldback, explicit pedal disconnections, shared phases and independent contact states. Scanner outputs are 18 sections/19 ground-relative outputs with one return contribution; wave signs and prewarp units need the reviewed conventions. AO-28 variants remain mutually exclusive, and treble A-H remains floating. Electrical signs do not determine acoustic polarity. One rotor trajectory serves differing emission times; interpolation, time-varying convolution order and variable-inductance energy terms have explicit checks. Documentary or mathematical corrections do not close native, physical or sonic gates. |
| **077, 469-474: Acquisition** | The 88 items are acquisition task families, not photographs or completed captures. Each image has an intended claim: identity, topology, geometry, appearance, condition or timing. Same-plane scale, independent endpoints, raw masters and declared transforms govern dimensional use. Terminal adjacency/color cannot invent a wire. Keep original, corrected, annotated and shipped assets separate. Close each task using its requested evidence and independent review, not image volume. |
| **078, 475-480: Rights and distribution** | Permission to reproduce and authority for an engineering claim are independent. Preserve exact asset licenses, creators, alterations and included-byte hashes. Patent/research figures retain source-specific scope. Dependency terms belong to the selected pinned revision; one SDK's terms do not cover framework, images or recordings. Build the release manifest from staged deliverables and repeat final artifact checks. This edition's source audit does not establish commercial-product clearance or a physical corpus. |
| **079, 481-486: Acceptance** | A pass belongs to one versioned claim and boundary. Recorded documentary, mathematical and syntax results cannot silently promote production or physical gates. Compare an actual time-domain algorithm to an independent formulation at declared frequencies, then test tails, state changes, hard valid inputs and rates. Freeze criteria before final comparisons; a changed threshold is a new study. Preserve failed, blocked, inconclusive and unrun outcomes. VST3 validator, native/device/DAW journeys, callback deadlines, UI and distribution each need their own evidence. |
| **080, 487-492: Final research handoff** | The atlas is an implementation handoff, not a measured organ or finished plugin. A complete AO-28 graph still needs selected variants, pins, nodes, feedback/transformer conventions and independent loaded/DC/transient references. Compile one owned graph with exact units, boundaries, immutable storage and off-thread retirement; never duplicate a transfer or delay. Acquire evidence that distinguishes competing models and reserve whole conditions before fitting. The final claim must name its tested specimen, conditions, outputs and exclusions. |
| **493-500: Complete source directory** | Read all eight pages. They identify the factory/scanner/rotary/driver literature, software and host APIs, schema/metrology/listening sources, asset/rights records and accessibility references. A locator is a path to verification; it is not a fresh source inspection, acquired waveform or delivered companion file. |

## Relation to the current repository

The atlas's original missing-engine statements describe its research edition.
They must not erase the implementation now present. Conversely, existing code or
an older passing report does not eliminate the atlas's remaining acquisition and
release requirements. Current state comes from the repository and the relevant
source-bound evidence in [PLAN](../../../PLAN.md),
[STATUS](../../../STATUS.md) and [NEXT_STEPS](../../../NEXT_STEPS.md).

| Milestone | Current foundation and next boundary |
| --- | --- |
| M0 | The unchanged PDF, source identities, nominal profile and acquisition planning exist. An identified, calibrated specimen is still absent from the declared physical claims. |
| M1 | The offline/core/adapters and meaningful scheduling/lifetime fixtures exist. Preserve one coherent source/build and bounded fault behavior when adding new models. |
| M2 | The nominal engine owns 91 shared free-running sources. Current documentary mapping work is not undone by the atlas's older, narrower transcription counts; physical tuning, pickup and loading remain separate. |
| M3 | Manuals, pedals, four banks, exclusive fixed registrations, Cancel, percussion, expression and state4 are implemented. Physical multiple-latch/loading/contact behavior remains outside this nominal contract. |
| M4 | Scanner numerical research exists, with the retained G5 same-Hz failure. Visual work must not relabel the scanner as connected or claim that its open gate passed. |
| M5 | Full revision-qualified AO-28 connectivity, operating points, transformers and loaded dry validation remain necessary. Neither inventory rows nor source artwork supplies them. |
| M6 | The independent four-state ideal crossover, analog reference, probe and lifecycle evidence exist. A separately identified same-Hz numerical experiment is ready; coupled amplifier/real driver/electrical fidelity remains open. |
| M7 | R2/R3 and R4 implementation/evidence exist under separate ownership. Preserve that owner's unfinished integration/acceptance and the R5/R6 boundaries; do not count their workers here. |
| M8 | Capture/corpus/comparison infrastructure exists. Identified actual acquisitions, fitting, held-out results and listening evidence cannot be replaced by synthetic fixtures. |
| M9 | Native standalone workspaces and MIDI calibration/channel modes, optional VST3, stable parameters/state and admitted captures exist. Reference fidelity, native retirement, actual devices/hosts/accessibility/deadlines and release qualification retain their separate gaps. |

`UiModel.h` directly confirms 68 ordinary controls including 24 presets, separate
147 playing-key slots, 61-key manuals, 25 pedals and 47 parameters. Preserve
those current identities; the PDF's proposed registry and erroneous concept
details are not an authorization to replace them.

## Concrete next work for this session

### Native visual refinement

Use the integrator's visible native journey to identify actual text/focus/input
issues before freezing a new candidate. Preserve minimum/default/reference sizes,
Flat behavior, both layout-breakpoint directions, held owners, original press
release, off-window release, modal staging and joined shutdown. Record the named
display/backend/scale and observed limitations; a remote desktop does not become
a physical controller/audio/host qualification.

Choose a bounded rack/deck/rim/material or typography change from the current
[reference-gap record](../../../design/PRODUCT_REFERENCE_GAPS.md). Keep actual
buttons, complete labels, retained banks and edited-versus-sounding state. After
implementation, obtain fixed-state actual-app captures, compare with the
unaltered reference and update README through the integrator. A closer material
or geometry result must retain remaining literal 1:1 differences. Page 434's
illustration was visually confirmed to be a labeled design study, so it cannot
be substituted for these captures. Page 431's proposed frame budgets are not an
existing performance pass.

### Independent M6 numerical candidate

Freeze the protocol before the realization: signal reconstruction/hold, external
rates, load family, signed electrical ports, check grid, frequency domain,
magnitude/phase criteria above a justified gain floor, complex criteria below it
and a separate input-admittance condition. Page 483 explicitly distinguishes
warped-frequency parity from a same-frequency comparison. Keep v1 and its
documentary L/C values as the reproducible baseline.

Test actual processed output and precharged transient evolution against an
independent reference, including state-preserving stopped rate changes,
partition equivalence, bounded storage, energy behavior, late-failure rollback
and continued processing afterward. Exact held-input integration is exact for
that reconstruction; it does not by itself prove exact analog-sinusoid response.
Report a candidate's failed criterion without changing the old threshold.
No numerical result supplies real driver impedance or enables an Engine route.

### Native MIDI failure handling

The inspected wrapper calls `closePort()`, then checks the stored open flag,
exceptions, reported errors and wrapper-entry count before cancellation and
destruction. The pinned upstream WinMM input close ignores native reset/stop/
close results; CoreMIDI close ignores disposal results before clearing handles.
That confirms the mechanism described by
[A47-N1](../../../reviews/PRODUCT_NATIVE_RECOVERY_REVIEW.md), not an executed
hardware failure or observed use-after-free.

The dependency-ready task is a below-RtMidi fault experiment that parks a native
callback before wrapper entry and retains the old behavior, followed by a
reviewed checked-close implementation. Failure must preserve native handles,
RtMidi callback storage, adapter context and inbox, mark the connection poisoned,
and prevent reopen/reset. Ordinary successful close must retain its leak-free
teardown gate. Native callback retirement after a successful OS result needs its
own platform evidence; the wrapper counter cannot establish the earlier native
storage lifetime. Preserve the locked original dependency and record any
reviewed prepared-source patch through the dependency workflow.

### Durable continuation

Keep this session's actual sixty identities, ten waves, owned paths, notes and
acceptance separate from every completed session. The integrator owns current
AGENTS/README/plan/status/next-step/log routing and publication. Each accepted
change needs exact source/input identities, executed verification and the next
concrete command or task. Preserve old failures and reports, bound storage,
checkpoint after each wave, and publish authorized completed changes to `main`
without force after checking concurrent advances. The PDF's historical immediate
M0/M1 starting commits are already superseded by the actual implementation; do
not restart the project from that prose.

## Actual verification and limits

Executed read-only checks: local commit/tree/status inspection; contiguous
80-page extraction verification and SHA-256 computations; PDF rendering/viewing
of pages 434 and 488; current UI inventory declarations; wrapper close control
flow and pinned upstream native-close source. The source PDF remained unchanged.

This assignment did not configure/build, run CTest, launch an application,
measure runtime/audio, acquire hardware evidence, re-run hosted CI, change a
production file or publish a commit. Parent/native and previous-session results
remain their own evidence. Only this owned Markdown note is delivered.
