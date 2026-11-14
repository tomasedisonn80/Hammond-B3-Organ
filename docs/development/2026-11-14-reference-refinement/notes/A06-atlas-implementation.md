# A06 — Atlas implementation, acceptance and next phases

Assignment: `w01_a06_atlas_implementation`, wave 1 of the new reference-refinement session, 14 November 2026. Owned output: this note only. No production changes, commits, pushes, spawned workers, build runs or physical observations were performed by A06.

## Scope, source identity and complete reading

I read every extracted text page **421–500 inclusive**, in eight complete ten-page displays. The initially truncated combined display of 421–430 was repeated alone before being counted as read. All eight final displays were untruncated. This covers chapters 069–080 and all eight source-directory pages; it is not a claim that every page image or linked external source was independently inspected.

| Source | Observed identity |
| --- | --- |
| Repository at start | Commit `8bd999efc13e309b932e6ac41d72ceb7b9b80a5f`; tree `c37da16cedbb91573476a44bd4eafe5a5e30134a`; local `main` showed the same tracked remote ref. This was a local ref observation, not a fresh remote query. |
| Original PDF | `Hammond_B3_Leslie_Research_Atlas_500pp.pdf`; 21,248,265 bytes; SHA-256 `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`. Rehashed in this assignment. |
| Assigned extraction | `/workspace/scratch/1bb6ee17ad7e/atlas-text/part6-421-500.txt`; 219,812 UTF-8 bytes; SHA-256 `dcd75f9d56b693d37af4a5d86728443b6fe242c53c6d4b1e4d4d3da574526700`. |
| Navigation convention | Atlas PDF ordinals equal its printed page numbers. A separate manual's “PDF 129” or “printed 3-50” is a locator inside that manual, not atlas page 129. |

The following byte counts and SHA-256 values identify each concatenated complete ten-page extraction, including its page headings and whitespace.

| Fully read pages | Page count | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| 421–430 | 10 | 25,882 | `a9519dd81b9f9ddc24471223e31e4148e064d9484364430aa5b89d97ad56341b` |
| 431–440 | 10 | 25,365 | `bb1e81d7c78d533206a5aa847d54708c708772a207e49a8cb88532252a04e704` |
| 441–450 | 10 | 27,896 | `63be3d9a110a3ebb92c64c47428ff01c738b703228470d08bba2e56efc6c8a72` |
| 451–460 | 10 | 25,604 | `39228e7d2d8841b1befd91a219669247360abde7802194a4d36d2201b845aed0` |
| 461–470 | 10 | 26,526 | `01995b99753c7ba3ed9b15b620bdc65795df9c693cf1a29ef60617e05c6c70f9` |
| 471–480 | 10 | 24,601 | `7a4e1d6034ee7fd3d5eed5ac2b78f27d168e73b6f712285bf5f052f3cf51b580` |
| 481–490 | 10 | 25,482 | `cbe278dcc5936018977ffba8eefed9689088edb290fc5d767ff3afbbeff2bb38` |
| 491–500 | 10 | 38,456 | `d497eb3bd55d25063c0d98062a4abc47ca4f6b979b1b6e706f7101996c91dd93` |
| **Total** | **80** | **219,812** | **Contiguous 421–500 coverage** |

Repository reading included [AGENTS.md](../../../../AGENTS.md), the full [README](../../../../README.md), newest [STATUS](../../../STATUS.md) and [NEXT_STEPS](../../../NEXT_STEPS.md), [PLAN](../../../PLAN.md), [atlas review](../../../research/ATLAS_REVIEW.md), current [recovery handoff](../../../INTERFACE_RECOVERY_HANDOFF.md), prior interface [checkpoint](../../2026-11-14-interface-continuation/CHECKPOINT.md), this session's [scope](../README.md), the newest development-log entry, and the workspace/geometry/inspection contracts. I also read [RELEASE_READINESS](../../../RELEASE_READINESS.md) and spot-checked current `InspectionModel.cpp`, `InspectionModel.h`, `UiModel.h` and `InstrumentView.cpp`. This is a document/source review; earlier test results below remain attributed to their retained reports.

## Conclusions for the integrator

The current M9 reference and real-desktop continuation is dependency-ready. The existing nominal dry engine, stable control identities, copied state and native UI provide the contracts the atlas asks to settle before visual polish. Work on panel composition, key depth, restrained materials, truthful status, focus and pointer behavior can proceed without a physical Hammond/Leslie corpus. The atlas expressly permits useful provisional engineering while acquisition remains open (pp. 445, 451, 454, 457, 486, 492).

The product must continue to distinguish four different things: a rendered decorative object, documentary evidence about an assembly, a running nominal model, and a measured specimen response. The reference artwork supports appearance decisions; it cannot supply calibrated dimensions, rotor telemetry, voltages, microphone positions or evidence of a connected cabinet. A more convincing rendering must not weaken these distinctions (pp. 421–423, 427–432, 469–474, 479–480).

The atlas's 62 proposed parameter records and statements that no audio engine existed describe its research handoff. They do not override the repository's later 47 production parameter identities, state4 with readers 1–3, implemented fixed registration selector, real standalone or qualified VST3 adapter. Preserve the newer implementation and its exact evidence; do not reintroduce historical absences as current blockers (pp. 440, 450, 452, 468, 482; current README/STATUS/PLAN).

## Complete page-locator findings

### Chapter 069 — Service inspection, pp. 421–426

- **421:** Service identifies the physical assembly, supporting evidence, running model and missing observations. Profile/revision/connection/draft status stays visible. Inspection selection does not alter sound or start diagnostic excitation. Proposed Parts, Signal, Profiles and Validation workspaces are richer than the present six-card implementation.
- **422:** Keep assembly callout, circuit designator, stock number, revision, documented value and model value separate. Unknown R62 retains both readings and locators. Alternatives are not “missing components.” Evidence labels describe provenance; no single authenticity score can replace the lineage.
- **423:** Comparisons require matching port/microphone boundary, units, reference/polarity, load, clock, control state and analysis. Factory G–G readings are not raw pickup gains. Preserve raw captures and separately identified transforms; residual error is not measurement uncertainty.
- **424:** An immutable active profile, editable draft, validation, offline preview, ready candidate, activation acknowledgment and off-thread retirement are distinct states. A late worker cannot activate an obsolete draft. Undo affects a draft transaction, not raw evidence or an already running profile implicitly.
- **425:** Telemetry has bounded storage/work, identity, frame range, units, sequence and loss/failure counts. UI consumes copies. Stale data and sequence gaps are visible; FFT/export remain outside audio. Diagnostic overflow must not discard musical events or delay the callback.
- **426:** Implementation order is evidence-only inspection, draft profile editing, offline analysis/engine bridge, then live telemetry and physical comparisons. SC-01 through SC-05 cover unknown preservation, revision separation, stale-worker rejection, probe incompatibility and accessible status. These are proposed gates, not atlas-executed product results.

### Chapter 070 — Assets, materials and cameras, pp. 427–432

- **427:** Separate specimen geometry from product styling. Dimensions require endpoints, units, uncertainty and specimen identity. Factory envelope includes bench/pedals; it does not specify the bare console. P005 and P020 are retouched context assets, excluded from dimensional reconstruction.
- **428:** Use stable semantic asset IDs independent of node order, stock numbers and parameter IDs. The authoring-to-glTF transform is `(x, y, z) → (x, z, -y)` exactly once, preserving handedness. Moving rotors/keys and stationary drivers have distinct hierarchy/pivots. Graphics consumes audio snapshots; it never advances the acoustic trajectory.
- **429:** “Walnut-style,” cap colors, brass-colored trim and proposed metalness/roughness are appearance recipes. They do not establish substrate chemistry or specimen material constants. Decorative valve glow cannot become a voltage reading.
- **430:** Transfer functions and texture channels are explicit; LOD variants retain semantic bindings, pivots and usable interaction bounds. Actual decoded memory, mips and render targets control the budget. Proposed GLB/native packs had not been produced in the atlas.
- **431:** Camera and LOD/lighting are presentation state, separate from acoustic microphones and saved sound parameters. Flat controls stay fully usable. Resource loss/hide/show cannot affect audio. Reduced motion stops decoration independently of sound; triangle/memory/frame-rate figures are proposed initial budgets, not measurements.
- **432:** Future scene/geometry ledger, GLB/manifest, materials/cameras and fallback/validation reports need hashes, provenance, rights and actual acceptance. A format-validator pass is separate from measured geometry, interaction and performance. Landmark residuals require calibrated cameras and bounds fixed before fitting. No 1:1 verification was claimed.

### Chapter 071 — Native accessibility and resizing, pp. 433–438

- **433:** A semantic model serves both skins and a native accessibility layer. All four banks retain identity; editing and sounding selection remain distinct. Web ARIA does not establish native semantics, and custom-editor concealment is not VST3 `kIsHidden`.
- **434:** Keyboard/direct numeric/pointer/assistive edits address the same control. One Tab entry per manual is a composite-navigation proposal. Focus alone does not sound a note. Original press owners survive internal focus; deactivation/close release only UI-owned notes. The proposed 0.1/0.01 drawbar input resolutions are not a mandate to migrate current discrete production controls during this UI slice.
- **435:** Readability is checked on final composited pixels and hit regions. Text/shape distinguish focus, latched preset, edited bank and sounding route. The chapter cites web contrast/target criteria and proposes larger product targets; it does not certify native conformance from a screenshot.
- **436:** Reflow labels/help/inspectors while preserving musical identities and holds. Host coordinate units vary by backend. Share visible geometry, hit transforms and accessibility bounds; actual scale/cross-monitor journeys remain separate from equal logical/drawable software captures.
- **437:** Reduced motion and Flat are complete presentation alternatives. Freezing visual rotation is not an audio brake. Requested, modeled and stale display states remain distinct. Accessibility queries must read copied UI state, never enter processing synchronously.
- **438:** A11Y-01…05 require real navigation, semantics, ownership, presentation and host integration workflows with named OS/backend/reader/scale. Retain trees, transcripts, events, failures and not-run cases. Keyboard-operable canvas or labels alone do not satisfy this gate.

### Chapter 072 — Prototype execution and boundaries, pp. 439–444

- **439:** Actual embedded JavaScript passed 28 scoped checks after three failures were fixed. Its limited DOM/event/storage double did not test browser layout, hit dispatch, native accessibility or audio. Browser execution remained blocked; syntax acceptance was not a browser pass.
- **440:** The prototype retained 36 drawbars, two pedal values, 61 playing plus 12 preset keys per manual and 25 pedals. Editing bank and routed registration were independent. Ordinary exclusive selection was implemented; simultaneous physical latches remained future work. Two proposed microphones were not a complete registry export.
- **441:** Reproduced fixes addressed Shift sensitivity jumps, reduced-motion control truth and roving Tab focus. Accumulate deltas against the captured semantic target; changing bank closes the original drag. A shaft CSS correction remained visually unverified.
- **442:** Replace direct UI mutation with stable semantic adapter commands and acknowledgments. Parameter gestures retain their original target across bank/tab changes. Cancel differs from panic. Real pointer capture needs platform dispatch tests beyond a test double.
- **443:** A permitted browser acceptance procedure needs executed results and reviewed screenshots at declared sizes; screen readers, touch and native DPI require their own observations. Proposed scripts remain not_run until executed.
- **444:** Preserve exact artifact/test scope. Seven malformed cases within an aggregate check are not seven extra top-level checks. The source study's no-audio and browser-blocked limits do not qualify future native or physical behavior.

### Chapter 073 — Ordered implementation, pp. 445–450

- **445 / M0:** Lock one B-3/AO-28/122 identity and variants, evidence classes, units, uncertainty and acquisition queue; compile a separately named surrogate where useful. Engineering and fidelity advance separately.
- **446 / M1–M2:** Build an immutable prepared profile, deterministic offline clock, half-open event intervals, zero-frame flushes and same-frame order before the shared source bank. Preserve source/terminal/MIDI distinctions and continuously running phases. Candidate frequencies and amplitude fixtures remain derived/proposed.
- **447 / M3–M4:** Contacts, retained banks, preset routing, continuous percussion recharge and loaded expression precede physical circuit claims. A replaceable organ surrogate is allowed. Scanner has 18 LC sections and 19 ground-referenced outputs; include the chorus return once and compare against independent loaded references.
- **448 / M5–M6:** Build a connected revision-specific AO-28 graph, loaded linear model and operating points before nonlinear fitting. Validate dry G–G before cabinet compensation. Keep Leslie 122/147 separate and preserve floating treble A–H and bass W–B ports plus real loading.
- **449 / M7–M8:** One trajectory per horn/drum serves microphone-specific retarded times; assign delay/filter/cabinet/room ownership once. Acquire/fill upstream before downstream and keep whole held-out conditions. Uncertainty can make a result inconclusive.
- **450 / M9:** Early adapters can be useful after M1/M2. Product closure still requires exact exported IDs, lifetime/retirement, real hosts/devices, latency/tails/bypass, deadlines, accessible UI, rights and reproducible release artifacts. Saved controls are not an exact DSP checkpoint.

### Chapter 074 — Agent operating contract, pp. 451–456

- **451:** Documentary atlas, provisional instrument, fitted profile, fidelity claim and release candidate are separate deliverable tiers. Every approximation names assumptions, omitted interactions and replacement gate.
- **452:** Schema validity does not authenticate specimens or measurements. Resolve units, references, asset hashes, connectivity and effect ownership; null required inputs block that physical algorithm. The source's frequencies, G–G values, component placements and registry each retain their original scope.
- **453:** Prepare offline; audio exclusively owns mutable active DSP; control reclaims only after retirement acknowledgment. Bounded queues and declaration-only interfaces do not prove implementation. Preserve timeline/automation anchors and distinguish prevalidation rejection from solver failure.
- **454:** M0–M9 each produce executable artifacts, actual commands/results and unresolved inputs. Missing acquisition blocks the associated claim, not independent useful work.
- **455:** Actual identities, clocks, loads, warm-up, settings, restoration history, permissions and uncertainty accompany captures. Group splits precede fitting; no derivative escapes its acquisition group. Residual minimization alone does not establish an identifiable physical explanation.
- **456:** Actual adapter mapping, host workflows, native UI/assets, pinned dependency rights, bundle resources, signing, installers and rollback are separate product deliverables. Research-date license statements need review against selected shipped versions; no legal or release clearance follows from reading this chapter.

### Chapter 075 — Risk register, pp. 457–462

- **457:** Reference acquisition, deterministic harness and AO-28 connectivity can proceed in parallel. Forty reported risk items express dependencies and exits, not invented probability/budget/dates. Unknown identity cannot become plausible-filled metadata.
- **458:** Original AO-28 is upper Figure 24, manual printed 3-50/PDF 129. Its 124 placements/sections across alternatives have no connectivity edges. Independently review terminals, grounds, valve pins, transformers and switch states; keep redraw differences and R62 uncertainty visible.
- **459:** Dry acquisition order is clock/source identity, loaded waves/leakage, control/contact/percussion, scanner and held-out dry G–G. Continuous source/ownership semantics allow later parameter calibration without architectural rewrites.
- **460:** Measure Leslie electrical loading before rotating pressure response, then separate horn/drum trajectories, geometry/angles and microphone/room paths. Cabinet photos/inventories are not production CAD; optional brake and other variants stay separate.
- **461:** Runtime, host/state, accessibility and distribution each need actual engineering evidence. Callback contracts, registry checks and plausible artwork do not qualify them.
- **462:** Keep resolved corrections closed: independent 91-value Table V transcription, treble driver 020305 versus spacer 020313, and AO-28 locator. Remaining calibration, installed-condition and connectivity gaps are different tasks. Mirrors are not independent corroboration.

### Chapter 076 — Technical claim audit, pp. 463–468

- **463:** Vintage B-3 mechanisms, selected originals, later redraws, patents and modern models have different applicability. Documentary correction, mathematical fixture, measurement and product execution are distinct evidence classes.
- **464:** Preserve repeated octave foldback, the stated top-key route, five pedal disconnections, shared phases and continuous percussion recharge. Cancel is routing-only. The seven double-fold locations were already corrected and verified in the source record; do not reopen that summary issue as new work.
- **465:** Scanner outputs/counts, common return and WDF signs/memory are convention-sensitive. The independently derived Gamma and prewarp corrections need relevant regression fixtures; they are not author-issued errata or proof of a finished physical solver. Compare all 19 signed outputs before normalization.
- **466:** Preserve AO-28 C59/T7 interpretations, mutually exclusive branches and unresolved R62/expression. Treble A–H floats; electrical sign is not acoustic polarity. A service adjustment time is not universal horn/drum tau. Historical brake is optional, distinct from modern servo behavior.
- **467:** Use retarded emission geometry, endpoint-correct interpolation and explicit coordinates; a Leslie 600 research experiment is not a 122 calibration. Time-varying convolution ordering matters. Variable inductance requires matching electrical and mechanical energy terms; general copper/driver references do not identify an installed coil.
- **468:** Keep actual host parameter exports, VST3 prior-block anchors/flush behavior, convolution lifetime, glTF transforms, runtime and physical evidence independent. Failed, blocked and not-run are not pass.

### Chapter 077 — Acquisition checklist, pp. 469–474

- **469:** Eighty-eight task families are not 88 photos. Each image declares supported uses: identity, topology, geometry, appearance, condition or timing. P005/P020 alterations prohibit dimensional inference. Generated reconstruction cannot supply hidden physical details.
- **470:** Capture identity/as-found condition, exterior/legends, permitted interiors and restored state. Systematic terminal/key/bank coverage cannot be replaced by a representative closeup. Optional assemblies remain conditional.
- **471:** Geometry needs a same-plane scale, defined endpoints, camera/lens/pose information, uncertainty and an independent cross-check. Preserve master pixels; corrections and stacks are derivatives. Pixel resolution is not geometric uncertainty.
- **472:** A supported endpoint-to-endpoint conductor/continuity observation admits an edge; color, crossings, OCR or stock sequence do not. Use stable physical terminals, orientation, revision namespaces, image regions and independent review.
- **473:** Masters, corrected images, annotated topology, 3D/UI derivatives and distributed assets retain separate identity/lineage/rights. Hashes prove unchanged bytes, not measurement truth or permission.
- **474:** A task closes on intended-feature coverage, identity, uncertainty, rights and review, otherwise stays blocked/rejected/reacquire or justified not-applicable. All 88 source tasks remained not_acquired. Photo coverage cannot close electrical/acoustic tests.

### Chapter 078 — Rights and artifact audit, pp. 475–480

- **475:** Reproduction permission and engineering authority are separate decisions. The reported audit covers 43 visuals and 28 patent plates; its review scope is retained, not independently reproduced here.
- **476:** Preserve exact license versions, creators, derivative authors and alteration history. P005, P006, P012, P016/017, P020 and P037 have distinct changes. P028/P030 cabinet identity and example-versus-installed valves remain qualified.
- **477:** Patent plates require source-specific applicability/rights review; patent expiry alone is not the stated copyright basis. Authors' 122A context, recorded response and simulation figures are different evidence classes, not new project recordings.
- **478:** Select and record actual dependency revisions, notices, transitive imports and distribution intent. Research references to VST3, JUCE, setBfree or fonts do not license every implementation or asset. No new dependency/license determination was performed in this assignment.
- **479:** Build manifests from staged release contents and attach source/distributed hashes, notices and modifications. Exclude unapproved full source scans. Generated art and original control diagrams remain illustrations, never captured application output.
- **480:** The atlas's 71-path audit and license inspections qualify its particular staging snapshot. Repeat final artifact checks after assembly; later ZIPs do not inherit old passes. Future corpus permissions, selected dependencies and branding remain separate gates.

### Chapter 079 — Acceptance and definition of done, pp. 481–486

- **481:** A pass belongs to one claim, input revision and boundary. A surrogate cannot lend a pass to a physical model missing connectivity. Keep engineering and specimen status separate; evidence changes invalidate affected dependent results.
- **482:** Source counts have exact scopes: 549 algorithmic route assignments, 144 independently reread manual cells, 91 service readings, 39 schema cases, 19 compile-time assertions, 62 proposed parameters and 28 limited UI checks. These are atlas report claims, not A06 executions or the repository's current parameter count.
- **483:** Independently reproduce a graph, then compare production time integration at comparable physical frequencies/boundaries, followed by transitions, tails and challenging states. Warped-frequency parity does not establish same-hertz parity. Moving filters and past history need moving-case evidence; do not invent a pass threshold after seeing residuals.
- **484:** Acquire a pilot and establish repeatability/calibration/noise/drift before freezing held-out metrics/bounds. Mean residual within tolerance is insufficient if uncertainty crosses the decision boundary. Listening discrimination, similarity, preference and equivalence have distinct meanings.
- **485:** Real validator/hosts/devices/state/lifecycle, callback deadlines, native focus/scale/pointer/reduced-motion tasks and distribution each have their own gates. A render stall cannot alter source time or accepted releases; screenshots and illustrations have different authority.
- **486:** Every completed report identifies code, profile/data, setup, criterion, result and reviewer. Changed criteria create a revised study, not retroactive success. Not-applicable requires explicit product exclusion. A useful provisional build can ship only with a claim matching the qualified scope and resolved intended distribution requirements.

### Chapter 080 — Integration handoff, pp. 487–492

- **487:** Research inventories, value placements, netlists and manufacturing BOMs are not interchangeable. Scanner/divider graphs are complete only within their stated idealizations. Unknown remains unknown through export/build.
- **488:** AO-28 order is selected revision/chassis, active instances/pins, every connection, coupling/feedback/polarity, required parameters, independent DC/AC/transient solve, then measured ports/held-out controls. The 124-row registry cannot generate a faithful graph by sorting designators.
- **489:** Compile authoring evidence offline: validate, resolve/hash, select alternatives, convert units, check named ports/effect ownership/loading, prepare all storage, publish immutable generation, render with one state owner, retire outside callback. Fuse electrically coupled stages when a cascade is unjustified.
- **490:** Acquire measurements that distinguish competing models at intermediate boundaries, with repeated takes and held-out conditions. Pair photo task IDs with actual electrical/acoustic protocols; a photograph does not measure a transfer or trajectory.
- **491:** Preserve completed source corrections and narrowly scoped checks. Browser blocking and the no-audio source UI remain historical limits. Numerical/source audit results cannot become acquired hardware or current product passes by relabeling.
- **492:** Execute M0/M1 in parallel with acquisition; M2–M5 direct-organ behavior and ports precede integrated M6/M7 tuning; M8 fits actual evidence; M9 qualifies actual delivered products. Processor lifecycle, buses, state and audio/UI responsibility require execution against the selected SDK.

### Source directory, pp. 493–500

| Page | Directory coverage read | Implementation use and limit |
| --- | --- | --- |
| 493 | Hammond originals/redraws/modern manuals, Leslie 122/147 information, patents, organ photographs and keyboard-action research | Locate exact historical variant, original circuit and image origin; patent/modern/context evidence is not a selected specimen. |
| 494 | Generator and Leslie images/manuals, bulletin 16, setBfree numeric source, synthesis research, schemas/RFCs and SDK documentation | Trace nominal frequency/filtering assumptions, metadata grammar and alternative models; no inherited captures or source-code license substitution. |
| 495 | MIDI/VST events/queues, scanner paper/WDF sources, MNA/ngspice/SciPy, valve datasheets and nonlinear model references | Primary route to terminal/timeline/numerical conventions and candidate device models, with actual implementation/version still selected separately. |
| 496 | Leslie electrical/acoustic/rotor references, nonlinear filtering/transformer work, driver data, interpolation and microphones | Separate electrical, mechanical, radiation and recording boundaries; preserve 122/600/122A applicability differences. |
| 497 | Time-varying convolution/room/driver/thermal research, capture/calibration/uncertainty, schemas, identifiability and listening methods | Source for independent numerical and physical study contracts; no supplied waveform/corpus is inferred. |
| 498 | Real-time/atomics/SIMD, VST processing/state/parameters/buses, JUCE lifecycle/build and SDK/license references | Verify the selected adapter/dependency implementation and exact runtime contract independently of research prose. |
| 499 | Platform signing/notarization, validators, ARIA/WCAG, PROV, FIFO/undo, glTF/material/context and native accessibility references | Product acceptance/lineage/navigation source map; proposed design guidance is not actual platform, accessibility or distribution qualification. |
| 500 | Pointer/Node/Playwright, FADGI/BagIt, CC and image-alteration/creator records, fonts, uncertainty/schema and processor call sequence | Locate evidence/rights/test-method detail; this directory reading did not retrieve or revalidate each external source. |

## Whole M0–M9 reconciliation with the current product

The following compares the complete plan with the current repository as documented at the inspected baseline. “Exists” and reported qualification are not new A06 test results. The atlas research waves, M0–M9 milestones and this session's worker waves remain separate organizations.

| Milestone and atlas authority | Current engineering scope to preserve | Next substantive phase and blocking evidence |
| --- | --- | --- |
| **M0 — pp. 445, 452, 457, 490** | Source PDF/hash, nominal identities, evidence/unknown contracts and acquisition tooling exist. | Select actual organ/generator/AO-28/cabinet revisions and condition, permissions and calibration boundaries. Acquire only the evidence a stated model requires. A named nominal profile can continue meanwhile. |
| **M1 — pp. 446, 453, 489** | SDK-independent prepared core, bounded events, offline renderer, control exchange and preserved error/lifecycle contracts exist. | Extend graphs only with offline preparation, borrowed-data lifetime, rollback and retirement evidence. Actual device deadlines remain separate from allocation/scheduler engineering. |
| **M2 — pp. 446, 459, 464** | 91 shared continuously running nominal sources; full manual/pedal routing now has a later independent factory comparison. Source phases and IDs are stable. | Acquire production gearing, calibrated loaded waveforms/levels/phases and leakage. Keep 12-TET/ideal sine/normalized units explicitly nominal. Do not redo closed routing corrections as absent research. |
| **M3 — pp. 447, 455, 464** | Four retained banks, exclusive fixed registrations, Cancel memory/ownership, nominal percussion, pedals and state4 compatibility are implemented. | Physical multi-latch/contact trajectories, continuous loaded drawbars, expression/percussion and pedal reactor need identified circuits/captures. The underlying factory Table IV admission remains separate from two readings of the atlas catalog. |
| **M4 — pp. 447, 465, 483** | Graph/compiler, independent AC/transient references and prepared scanner research modules exist. | Resolve observed G5 same-hertz failure under the frozen numerical policy before Engine integration. Existing warp-matched/discrete agreement does not close that gate. Use independently converged transients, signed loaded outputs and actual filters/latency; preserve the failure. Physical captures remain later. |
| **M5 — pp. 448, 458, 488** | Current audio boundary remains nominal dry; complete AO-28 quantities are explicitly unresolved. | Select a revision, transcribe independently reviewed pin/node connectivity and coupling, acquire required transformer/operating-point/control data, establish loaded linear and nonlinear references, then validate dry G–G. No inventory-to-netlist shortcut. |
| **M6 — pp. 448, 460, 466** | 122 baseline and 147 variant separation are retained in contracts/inspection. Cabinet audio is unconnected. | Selected electrical graph, real complex driver load, floating A–H/W–B polarity and amplifier/transformer/crossover behavior need independent electrical observations. Documentary/reference work can proceed while M5 develops. |
| **M7 — pp. 449, 460, 467** | Separate nominal motion/propagation track and frozen numerical foundation exist; it does not alter the dry Engine. | Continue independent motion, full-orbit propagation/history and dual-rotor numerical acceptance under that track's ownership. Physical qualification needs actual rotor trajectories, geometry and angle/position captures; assign propagation/filter/room effects once and wait for M5/M6 integration inputs. |
| **M8 — pp. 449, 455, 484, 490** | Audio/corpus/split/comparison/study/declaration/replay tools and relocatable CaptureTools exist with their own reported engineering evidence. | Run the external-output pilot with real identities, physical clock/channel/load calibration, repeatability and uncertainty. Freeze whole-acquisition train/held-out splits and decision bounds before fitting. Synthetic fixtures do not close calibration. |
| **M9 — pp. 450, 456, 461, 485** | Play/Rotary/Service, Flat, shared paint/hit geometry, copied-state inspection, optional MIDI, explicit musical Save/Load, VST3 and packaging are implemented. The prior a517 matrix is retained reported qualification. | Immediate reference composition/material/status refinement and full real-desktop ownership journey; then real devices/DAWs, native accessibility, physical scale, deadline/latency measurements, custom VST3 editor integration, intended-release rights/signing/runtime gates. Each has distinct evidence. |

The current actual UI inventory is **47 sound parameter records, 68 ordinary control records including 24 reversed preset keys, 147 playing keys, 71 Play focus stops, ten common focus stops in Rotary/Service, six Service cards with 28 rows, and 91 shared sources**. The writer is `B3CONTROLS4`, with readers 1–3. These values come from current README/handoff/contracts and source spot-checks; they replace no physical measurement.

`InspectionModel.cpp` confirms that applied counts/controls use `view.applied`, desired pending state is separate, model/evidence/availability are different fields, scanner/AO-28/Leslie remain unconnected, and missing voltages/speeds/geometry display unavailable/not acquired. The held-count rows currently carry the literal unit `targets`; the known singular wording issue is therefore a small presentation change. Existing read-only cards are an appropriate first Service tier, not completion of the proposed parts-tree, draft-profile, spectral-comparison or live telemetry workflows.

## Next feasible phases and concrete acceptance

### 1. Reference-led composition and readable material refinement

Use the preserved cover/page-409 source and a fresh actual 1672×941 native frame. Treat the approximately 108-versus-144-pixel manual-depth observation in the current handoff as a recorded visual comparison, not a physical dimension or a newly measured A06 result. Adjust the shared layout rather than painting a deeper shape over an unchanged hit region. Retain full manuals, presets, pedals, working header tools, correct footage and honest unsupported-model status even where the concept omits or mislabels them (pp. 428, 431, 435–437; current geometry contract).

Acceptance should retain independently checked key/control inventories, shared-edge and accidental precedence, no new hidden hits, readable text/focus/held/pending states at minimum/default/reference sizes and responsive breakpoints, and equivalent Flat operation. Verify unchanged sound/state/owner behavior against an equivalent no-navigation timeline. Capture actual new native frames, source/binary/input/driver identities and residual visual differences. Do not copy obsolete raster baselines or assert literal equality merely because the surface is more convincing.

### 2. Complete the real-desktop ownership journey

The current recovery handoff records only partial X11 click/focus/released-endpoint evidence. It does not close held ownership through navigation, Flat, resize, sustained capture or capture return. Run the existing complete journey on an observed desktop backend with named executable/build dependencies. Preserve original keyboard/pointer owners while crossing workspaces and sizes; require the original release to terminate the original owner, no hidden new note/drag, and ordinary joined shutdown. Retain before/after lossless desktop frames and diagnostic/command evidence. An ineffective close shortcut followed by supervisor termination is a distinct outcome, not ordinary-close acceptance (pp. 434, 436, 442–443, 485).

Do not weaken the full script, release/Save assertions, time bounds or sampled-state oracle to manufacture a pass. A presentation result remains separate from a physical MIDI/audio, high-DPI or screen-reader result. Preserve unavailable capture-return telemetry as unavailable unless directly observed.

### 3. Finish the known Service presentation gap

Correct singular/plural held-target wording without changing counts, evidence labels, audio state or row identities. Retain an actual pending-state capture, with a source-identified accepted request and acknowledgment boundary so the image really demonstrates pending controls. A final settled capture or injected label cannot stand in for this state. Check current/retained/stopped/unprepared/unavailable labels and applied-versus-desired controls at the same time; the existing bounded copied-state API is the correct ownership boundary (pp. 421, 425–426, 437, 442).

### 4. Native accessibility as an independent follow-on

The existing semantic IDs, roving groups, Flat mode and keyboard paths are useful inputs. Choose one actual platform accessibility bridge and expose stable names, roles, ranges, units, values, editability, selected bank/route and focus from copied state. Keep decorative assets out of navigation and use persistent failure/status text without telemetry announcement floods. Qualify a complete musician workflow with a named screen reader, scale and host/backend, retaining tree snapshots, transcripts and event ownership. The proposed atlas A11Y-01…05 gates provide the exit structure; SDL keyboard acceptance is not that bridge (pp. 433–438).

### 5. Evidence inspection and model research after the current slice

If Service expands, add source-qualified read-only assembly/parts navigation and persistent source/evidence locators before editable physical values. Preserve null/reason/acquisition tasks and revision alternatives. Draft editing needs its own schema/compilation/worker-version/activation/retirement contract; actual signal comparison needs compatible captures and units before being enabled. These are substantive later features, not prerequisites for the present visual/desktop improvements (pp. 421–426).

The next independent model work is the scanner realization/policy decision under the existing frozen G5 budget, plus selected AO-28 connectivity and physical acquisition planning. A numerical alternative requires new independent reference evidence; changing the acceptance rule after seeing failures creates a revised study with the old failure preserved (pp. 483, 486). AO-28 documentary transcription can proceed with a selected original branch and clear source locators; specimen applicability and missing physical solver parameters must remain explicit (p. 488). M6 references and M7 synthetic numerical work can run in parallel without claiming a calibrated integrated cabinet.

### 6. Product and release evidence

For a future supported release, retain exact binary/source/dependency identities and actual host/device session restoration, automation, bounce, multi-instance, rate/buffer/lifecycle and failure results. Measure callback deadlines/underruns and latency on named systems rather than using CPU averages or a no-allocation result as a substitute. Qualify native DPI/accessibility and the actual final install/update/uninstall payload. Review intended asset/dependency/project-license/branding rights and any required signing against the bytes to distribute (pp. 450, 456, 475–480, 485–486).

## Documentation reconciliation and handoff limits

The newest STATUS/NEXT_STEPS and recovery handoff correctly distinguish completed nominal engineering from missing physical/desktop/release gates. They preserve the qualified `a517203` reports, the earlier b1 macOS failure, original local 146/147 result, repaired source, separate runner cancellations and unavailable raw local archive. This assignment neither reran those tests nor reconstructed missing evidence. Newly authored recovery prose must stay distinct from original raw artifacts.

One current-navigation issue remains: the opening **“Current continuation assessment”** in `RELEASE_READINESS.md` still leads with the older 183/621/272 qualifications and nine-file standalone package. Its later pedal material is correctly labelled historical, but that opening predates the current 47-parameter/state4 interface and 19/15-file packaging boundary described by the newest handoff. Refresh only the current summary/pointers when integrating this session; retain all dated historical evidence. Do not turn that stale entry point into a reason to repeat already completed fixed-selector, scanner-foundation or standalone work.

Verification performed here was limited to complete text reading, source/document spot checks, local commit/tree/ref/status inspection, and SHA-256/byte accounting of the original PDF and extraction/chunks. No physical measurement, external-source revalidation, visual comparison, accessibility session, native execution, compiler/test invocation, publication or release gate is claimed. Root owns shared documentation, source implementation, coherent qualification, actual gallery refresh and guarded publication.
