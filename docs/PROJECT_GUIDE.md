# Project guide

The available programs include a nominal dry-organ engine, offline tools, an
optional actual VST3 instrument and a native standalone instrument window. Two manuals and 25 pedals share the same 91
free-running sources. Retained banks, independent contact travel, partial keys,
shared percussion, typed note ownership and phase-preserving rate changes are
implemented. The source, console and fixed pedal mixtures remain unmeasured.

Start with the [interface operating guide](INTERFACE_RUNBOOK.md) and
[current interface checkpoint](development/2026-11-14-interface-continuation/CHECKPOINT.md),
[scanner handoff](SCANNER_HANDOFF.md) or [calibration handoff](CALIBRATION_HANDOFF.md)
for the relevant active track. The [earlier standalone handoff](STANDALONE_HANDOFF.md)
retains its named source and qualification. The [pedal handoff](PEDAL_HANDOFF.md) retains
offline rendering and VST3 commands. The default build stays SDK-free.
**Full M3, actual DAW/device qualification, a native accessibility tree, calibrated
physical fidelity and signed distribution remain open.** The [full plan](PLAN.md) keeps
their separate dependencies visible; a built and tested module does not close
those product gates.

## Start with the question you need to answer

| Question | Read |
| --- | --- |
| What is the full product plan? | [PLAN.md](PLAN.md): M0-M9 deliverables, dependencies and exit evidence. |
| What works, and what has actually passed? | [STATUS.md](STATUS.md), the relevant active handoff, and the named source-specific platform/test reports linked there. |
| What should happen next? | [NEXT_STEPS.md](NEXT_STEPS.md), [M3 requirements](M3_ACCEPTANCE_CONTRACT.md), and the [session ledgers below](#session-ledgers-and-continuation) for current ownership. |
| How do I resume with exact commands and evidence? | [Current interface checkpoint](development/2026-11-14-interface-continuation/CHECKPOINT.md) and [operating guide](INTERFACE_RUNBOOK.md), [SCANNER_HANDOFF.md](SCANNER_HANDOFF.md), [CALIBRATION_HANDOFF.md](CALIBRATION_HANDOFF.md), or [PEDAL_HANDOFF.md](PEDAL_HANDOFF.md), according to the selected task. |
| Which milestone gates are actually closed? | [ACCEPTANCE_MATRIX.md](ACCEPTANCE_MATRIX.md): software, documentary, specimen and product evidence remain distinct. |
| Why was a choice made, and what failed? | [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md) and the linked assignment notes. |
| What must every development session preserve? | [AGENTS.md](../AGENTS.md): source review, declared evidence, file ownership, coherent builds, shared handoff and the standing commit/push workflow. |

Current status and the newest ledger own the latest implementation and observed
results. A historical review, proposed contract or configured workflow does not
supersede them. The [original handoff](SESSION_HANDOFF.md),
[console continuation handoff](CONTINUATION_HANDOFF.md) and
[original CI qualification](CI_QUALIFICATION.md) retain their dated scopes.

## Build, render, inspect and install

The default tools use a C++20 compiler, CMake 3.21+ and Python 3.10+. The core has
no audio/GUI framework or host-SDK dependency. The optional VST3 build requires
CMake 3.25+ and its explicitly acquired, verified SDK; the standalone build uses
CMake 3.21+ and pinned SDL2. Follow the selected adapter's actual prerequisites.

| Task | Practical reference |
| --- | --- |
| Play the standalone window | [Interface runbook](INTERFACE_RUNBOOK.md), [preset/build guide](PRESET_RUNBOOK.md) and [standalone app](STANDALONE_APP.md): Play/Rotary/Service, Flat, keyboard/pointer/MIDI, saved controls and bounded replay. |
| Audition documentary chapel registrations | [Chapel export](CHAPEL_CONTROLS.md): explicit ordinary B3CONTROLS3 files, with physical preset/loading limits retained. |
| Measure the Session render workload | [Standalone benchmark](STANDALONE_BENCHMARK.md): four fixed workloads, source identity and raw intervals without a timing pass threshold. |
| Inspect, compare and replay acquisition evidence | [Calibration runbook](CALIBRATION_RUNBOOK.md) and [handoff](CALIBRATION_HANDOFF.md): actual commands, complete reports, expected outcomes, source/runtime identities and recovery. |
| Prepare the next physical acquisition | [A1–A6 sequence](CALIBRATION_NEXT_ACQUISITION.md): required real inputs, roles, artifacts and separate physical acceptance. |
| Install and move the capture pipeline | [CaptureTools installation](CAPTURE_TOOLS_INSTALL.md): 57 Python/data/documentation files, separate from the 23-file native OfflineTools component. |
| Build and test on Linux, macOS or Windows | [BUILD.md](BUILD.md): presets, explicit commands, generated profile, configurations and sanitizer limits. |
| Render a registration or event score | [RENDER_FORMAT.md](RENDER_FORMAT.md): CLI options, event grammar, sample timing, output format and errors. |
| Hear the pedals with both manuals | [Pedal demo](PEDAL_DEMO.md) and [retained three-second example](../examples/demos/pedal-phrase-v1/README.md): actual schema-3 bundle, score, source inventory, PCM reports and replay commands. |
| Inspect actual pedal buses, mixtures and contacts | [Pedal traces](PEDAL_TRACE.md) and [pedal plots](PEDAL_TRACE_PLOTS.md): three fixed 120 ms scenarios, same-frame CSV and bounded standalone SVG. These are distinct from the three-second musical score. |
| Hear the current console and reproduce its bundle | [Two-second console demo](../examples/rendered/nominal-console-v2/README.md): partial travel, shared readiness, Cancel and masking, with schema-2 provenance and independent PCM checks. |
| Inspect contact/readiness transitions | [Console traces](CONSOLE_TRACE.md) and [trace plots](CONSOLE_TRACE_PLOTS.md): bounded sample CSV and standalone SVG. The demo's partial-key plot is a separate 120 ms scenario, not a trace of its two-second score. |
| Try the earlier ideal-contact behavior | [Five original fixtures](../examples/README.md), [four-second demo](../examples/rendered/nominal-two-manual-v1/README.md) and [original replay](DEMO_REPLAY.md). Their retained identities remain intact. |
| Retain inputs, logs and serialized audio evidence | [RENDER_EVIDENCE.md](RENDER_EVIDENCE.md), [PCM measurements](AUDIO_MEASUREMENTS.md) and [independent bundle verification](RENDER_VERIFICATION.md). |
| Inspect compiled nominal models and control mappings | [Model metadata](MODEL_METADATA.md) and [parameter bridge](PARAMETER_BRIDGE.md): console/pedal identities, units and all 47 compiled mappings. Offline metadata does not inspect a native module. |
| Install or move the offline tools locally | [OFFLINE_INSTALL.md](OFFLINE_INSTALL.md): exact current component payload, five native tools, explicit data paths and relocation checks. |
| Build, test and stage the actual VST3 | [Native build](VST3_BUILD.md), [native CI](VST3_CI.md) and [explicit local bundle installation](VST3_LOCAL_INSTALL.md). The core/default build remains independent. |
| Time bounded workloads | [BENCHMARKING.md](BENCHMARKING.md): legacy cases and opt-in `console_motion`, `owned_input` and `console_all` cases; elapsed observations have no deadline pass threshold. |

Build before running CTest; CTest does not compile executables or create the
generated profile. Render to a new filename: the CLI preserves existing outputs
and requires hard-link support for publication. The `OfflineTools` install
component contains the offline tools and its declared data/scripts. The separate,
opt-in `NativeVST3` component stages a complete built bundle to a new local
destination. The separate opt-in [Standalone component](STANDALONE_INSTALL.md)
stages 15 files with MIDI disabled or 19 with MIDI enabled, including the app
and six operating/model/install guides. These explicit
local components do not register a plugin in a DAW scan directory. Use the current install manifests rather
than carrying forward a historical console-only file count.

## Find the contract behind a claim

| Area | Contracts and retained evidence |
| --- | --- |
| Initial architecture and sources | [Implementation contract](IMPLEMENTATION_CONTRACT.md), [profile format](PROFILE_FORMAT.md) and [engine API](ENGINE_API.md). The nominal sources are shared and free-running; source IDs, MIDI notes and indices are distinct. |
| Controls and saved state | [Console extension](CONSOLE_EXTENSION.md), [control-state format](CONTROL_STATE_FORMAT.md) and [parameters](PARAMETERS.md). There are 47 permanent IDs, preserving the earlier 45 records. The writer emits `B3CONTROLS4`; readers 1–3 retain their existing migrations and initialize fixed modes to None. Saved controls exclude keys, owners, source phase and transient DSP histories. |
| Integrated nominal console | [Console dynamics](CONSOLE_DYNAMICS.md), [console acceptance](CONSOLE_ACCEPTANCE.md), [M3 requirements](M3_ACCEPTANCE_CONTRACT.md) and [model metadata](MODEL_METADATA.md). Independent contacts and shared percussion run in the Engine and renderer; the selected values are unmeasured. |
| Typed input and lifecycle | [Parameter bridge](PARAMETER_BRIDGE.md), [manual ownership](NOTE_OWNERSHIP.md), [pedal ownership](PEDAL_NOTE_OWNERSHIP.md), [combined input](PERFORMANCE_INPUT.md) and [sample-rate lifecycle](SAMPLE_RATE_LIFECYCLE.md). Native callback qualification is recorded separately from the core adapters. |
| Manual and pedal routing | [Factory comparison](FACTORY_REFERENCE.md), [pedal routing](PEDAL_ROUTING.md), [Engine integration](PEDAL_ENGINE.md), [fixed nominal voice](PEDAL_VOICE.md) and [independent audio acceptance](PEDAL_AUDIO_ACCEPTANCE.md). The implemented 200-position map preserves five disconnected contacts; documentary routing is distinct from measured electrical shaping. |
| Actual native callback and state handoff | [Processor](VST3_PROCESSOR.md), [controller](VST3_CONTROLLER.md), [automation timeline](HOST_TIMELINE.md), [state exchange](STATE_EXCHANGE.md), [actual ABI](VST3_ABI_ACCEPTANCE.md) and [behavior](VST3_BEHAVIOR_ACCEPTANCE.md). Three event buses and 47 controls drive the existing Engine, with generic host controls; historical native reports retain their original source/count. |
| Native allocation, automation and concurrency | [Allocation audit](VST3_REALTIME.md), [dense automation review](VST3_AUTOMATION_REVIEW.md) and [concurrency/TSAN evidence](VST3_CONCURRENCY.md). Their recorded workloads, interposition and instrumentation boundaries remain explicit. |
| Diagnostic traces | [Trace contract](CONSOLE_TRACE.md) and [plot contract](CONSOLE_TRACE_PLOTS.md): state timing, retained input hashes, limits and display reductions. Diagnostics do not establish physical authenticity. |
| Processing limits | [Callback audit](REALTIME.md), [numerical bounds](NUMERICAL_BOUNDS.md) and [benchmark](BENCHMARKING.md). Each states its observed scope; none alone qualifies a live device deadline. |
| Physical acquisitions | [Capture format](CAPTURE_FORMAT.md), [capture validation](CAPTURE_VALIDATION.md) and [acquisition protocol](CAPTURE_PROTOCOL.md). Planned metadata, actual recordings, byte integrity and physical admission are separate states. |
| Repository and platforms | [Repository checks](REPOSITORY_CHECKS.md), [core/native CI](CI.md), [standalone CI](STANDALONE_CI.md) and the active handoffs. A pass belongs to its named revision, job and artifact scope. |
| Historical final continuation reviews | [Core runtime](reviews/FINAL_CONTINUATION_RUNTIME.md), [input and persistence](reviews/FINAL_CONTINUATION_INPUT.md), [offline evidence](reviews/FINAL_CONTINUATION_EVIDENCE.md), [handoff](reviews/FINAL_CONTINUATION_HANDOFF.md), [platforms](reviews/FINAL_CONTINUATION_PLATFORM.md) and [readiness](reviews/FINAL_CONTINUATION_READINESS.md). Each retains its actual inspected revision, observed findings, checks and limits. The [legacy audio comparison](reviews/CONTINUATION_LEGACY_AUDIO.md) remains separate compatibility evidence. |
| Original session's final reviews | [Core](reviews/FINAL_CORE_REVIEW.md), [evidence tooling](reviews/FINAL_EVIDENCE_REVIEW.md), [claims](reviews/FINAL_CLAIMS_REVIEW.md), [integration](reviews/FINAL_INTEGRATION_REVIEW.md), [platforms](reviews/FINAL_PLATFORM_REVIEW.md) and [readiness](reviews/FINAL_READINESS_REVIEW.md). Preserve these as historical evidence for their original snapshots. |
| Remaining product host, device and editor work | [Native contract](VST3_SPIKE_CONTRACT.md), [host integration proposal](HOST_INTEGRATION.md) and the M9 row in [ACCEPTANCE_MATRIX.md](ACCEPTANCE_MATRIX.md). An actual module test does not close DAW save/reopen, device deadlines, native accessibility or signed release gates. |

Evidence classes describe inputs: `documented`, `measured`, `derived`, `proposed`
and `unknown`. Test outcomes describe execution: `pass`, `failed`, `blocked`,
`not_run` and `inconclusive`. Keep the exact code/data identity, setup, criterion,
observed result and limitation with every acceptance claim.

## Read the source and complete reviews

The unchanged [500-page atlas](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf) is the
supplied source. Its [manifest](research/source-manifest.json) retains the exact
identity and absence of referenced companion files at baseline. The
[chapter index](research/chapter-index.json) covers all 80 chapters;
[errata](research/ERRATA.md) records implementation hazards.

The [complete atlas review](research/ATLAS_REVIEW.md) consolidates the original six
disjoint review ranges. The independent continuation retained another complete
six-range review in its own ledger; completed pedal work and the separate
standalone/scanner/rotary/calibration sessions retain their own complete readings. Later [factory comparison](FACTORY_REFERENCE.md)
adds documentary routing corroboration; current engineering results belong in
[STATUS.md](STATUS.md). Neither reading recovers absent companion data or replaces
acquired instrument measurements.

## Check rights and distributed material

The [dependency and rights inventory](DEPENDENCIES_AND_RIGHTS.md) distinguishes
repository contents, the local install, CI dependencies and generated outputs.
[Third-party notices](../THIRD_PARTY_NOTICES.md) and the
[source-rights record](research/RIGHTS_AND_SOURCES.md) preserve identified sources
and unresolved permissions. No project-wide license has been selected. Source
identity, public availability and build/test passes do not establish redistribution
rights. Record provenance and applicable rights before adding a release payload.

## Session ledgers and continuation

| Session | Assignment and evidence records |
| --- | --- |
| Current 2026-11-14 interface continuation | [Session](development/2026-11-14-interface-continuation/README.md), [actual manifest](development/2026-11-14-interface-continuation/assignments.json) and [checkpoint](development/2026-11-14-interface-continuation/CHECKPOINT.md); current M9 interface ownership and source-specific evidence. |
| Original ten-wave implementation | [Original agent ledger](development/AGENT_LEDGER.md), [wave log](development/WAVE_LOG.md), [agent notes](development/agent-notes/) and [historical handoff](SESSION_HANDOFF.md). Their original assignment IDs 01-60 remain unchanged. |
| Completed 2026-11-13 console continuation | [Separate continuation ledger](development/2026-11-13-continuation/README.md), [actual-state manifest](development/2026-11-13-continuation/assignments.json), numbered evidence notes and [historical handoff](CONTINUATION_HANDOFF.md). The [continuation checker](CONTINUATION_CHECKS.md) validates that session's own 60-assignment, ten-wave records. |
| Completed 2026-11-13 pedal/native session | [Retained ledger](development/2026-11-13-pedals/README.md), [actual-state manifest](development/2026-11-13-pedals/assignments.json), substantive numbered notes and [operational handoff](PEDAL_HANDOFF.md). Its sixty new assignments and ten waves are independent of both completed sessions. |
| Native standalone session | [Actual ledger](development/2026-11-13-next-phases/README.md), [manifest](development/2026-11-13-next-phases/assignments.json) and [handoff](STANDALONE_HANDOFF.md); sixty distinct assignments in ten waves for this user request. |
| Scanner session | [Actual ledger](development/2026-11-13-scanner/README.md) and [handoff](SCANNER_HANDOFF.md); retain its independent numerical gates and ownership. |
| Rotary session | [Actual ledger](development/2026-11-13-rotary/README.md) and [scope](ROTARY_SCOPE.md); separate nominal M7 development. |
| Completed calibration session | [Sixty actual workers / ten waves](development/2026-11-13-calibration/README.md), [strict completion](development/2026-11-13-calibration/completion-check.json) and [handoff](CALIBRATION_HANDOFF.md); qualified M0/M8 tooling with separate physical acquisition/fitting gates. |

The console continuation's sixty assignments are complete, with sixty distinct actual
identities and retained notes. Its explicit final gate passes; original-session
notes contribute no credit to that count. These completed assignment scopes do
not imply full M3 or physical product completion.

Read the newest ledger and shared status before claiming a task. Contacts,
percussion, pedals, typed core adapters and an optional native module are already
implemented; current integration, acquisition and product gates are in
[NEXT_STEPS.md](NEXT_STEPS.md). Assignment numbers
belong to their session. Planned rows do not prove dispatched or completed work.
Research waves, development waves and M0-M9 milestones describe different things.

Preserve existing history when `main` advances. Record actual changes, commands,
failures and unrun gates in the assigned note; the integrator owns shared status
and publication. Check source integrity and the selected session independently:

```sh
python3 -B tools/check_repository.py --json
python3 -B tools/check_standalone_session.py --repo . --json
```

The first checks its documented [navigation/data scope](REPOSITORY_CHECKS.md)
and the original session's notes. The second validates this standalone session's
retained actual states; other active tracks have their own checkers. Use the
selected ledger's current checker and
explicit final-count procedure when available; do not reuse historical workers
or mark planned assignments complete. These are record/integrity checks, not
product, external-execution or physical-calibration gates.
