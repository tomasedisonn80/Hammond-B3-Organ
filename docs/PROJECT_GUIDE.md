# Project guide

The available program is a nominal dry-organ engine and an offline tool set.
It renders two manuals with retained banks, optional independent contact travel,
partial key targets and shared percussion. Typed note ownership, a normalized
parameter bridge and phase-preserving sample-rate changes provide implemented
foundations for future hosts. The source and console profiles are unmeasured.

Start with the [README quick start](../README.md#build-and-test), listen to the
[two-second console demo](../examples/rendered/nominal-console-v2/README.md), or use
the [current developer handoff](CONTINUATION_HANDOFF.md) for exact commands.
The next development slice is the [prepared pedal-routing kernel](M3_NEXT_GATE.md).
**Full M3, playable VST3/device applications, native UI and physical fidelity
remain open.** The [full plan](PLAN.md) keeps their separate dependencies visible.

## Start with the question you need to answer

| Question | Read |
| --- | --- |
| What is the full product plan? | [PLAN.md](PLAN.md): M0-M9 deliverables, dependencies and exit evidence. |
| What works, and what has actually passed? | [STATUS.md](STATUS.md), then the revision-specific evidence in [CONTINUATION_HANDOFF.md](CONTINUATION_HANDOFF.md) and the [continuation platform review](reviews/CONTINUATION_PLATFORM_REVIEW.md). |
| What should happen next? | [NEXT_STEPS.md](NEXT_STEPS.md), the concrete [M3 pedal-routing gate](M3_NEXT_GATE.md), and the [session ledgers below](#session-ledgers-and-continuation) for current ownership. |
| How do I resume with exact commands and evidence? | [CONTINUATION_HANDOFF.md](CONTINUATION_HANDOFF.md): source identity, build, render, demo verification, diagnostics, installation and publication. |
| Which milestone gates are actually closed? | [ACCEPTANCE_MATRIX.md](ACCEPTANCE_MATRIX.md): software, documentary, specimen and product evidence remain distinct. |
| Why was a choice made, and what failed? | [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md) and the linked assignment notes. |
| What must every development session preserve? | [AGENTS.md](../AGENTS.md): source review, declared evidence, file ownership, coherent builds, shared handoff and the standing commit/push workflow. |

Current status and the newest ledger own the latest implementation and observed
results. A historical review, proposed contract or configured workflow does not
supersede them. The [original handoff](SESSION_HANDOFF.md) and
[original CI qualification](CI_QUALIFICATION.md) retain their dated scopes.

## Build, render, inspect and install

The tools use a C++20 compiler, CMake 3.21+ and Python 3.10+. The core has no
audio/GUI framework or host-SDK dependency.

| Task | Practical reference |
| --- | --- |
| Build and test on Linux, macOS or Windows | [BUILD.md](BUILD.md): presets, explicit commands, generated profile, configurations and sanitizer limits. |
| Render a registration or event score | [RENDER_FORMAT.md](RENDER_FORMAT.md): CLI options, event grammar, sample timing, output format and errors. |
| Hear the current console and reproduce its bundle | [Two-second console demo](../examples/rendered/nominal-console-v2/README.md): partial travel, shared readiness, Cancel and masking, with schema-2 provenance and independent PCM checks. |
| Inspect contact/readiness transitions | [Console traces](CONSOLE_TRACE.md) and [trace plots](CONSOLE_TRACE_PLOTS.md): bounded sample CSV and standalone SVG. The demo's partial-key plot is a separate 120 ms scenario, not a trace of its two-second score. |
| Try the earlier ideal-contact behavior | [Five original fixtures](../examples/README.md), [four-second demo](../examples/rendered/nominal-two-manual-v1/README.md) and [original replay](DEMO_REPLAY.md). Their retained identities remain intact. |
| Retain inputs, logs and serialized audio evidence | [RENDER_EVIDENCE.md](RENDER_EVIDENCE.md), [PCM measurements](AUDIO_MEASUREMENTS.md) and [independent bundle verification](RENDER_VERIFICATION.md). |
| Inspect compiled nominal models and control mappings | [Model metadata](MODEL_METADATA.md) and [parameter bridge](PARAMETER_BRIDGE.md): identities, units and the actual 43 internal mappings. |
| Install or move the offline tools locally | [OFFLINE_INSTALL.md](OFFLINE_INSTALL.md): the exact 16-file component, explicit profile/event paths and relocation checks. |
| Time bounded workloads | [BENCHMARKING.md](BENCHMARKING.md): legacy cases and opt-in `console_motion`, `owned_input` and `console_all` cases; elapsed observations have no deadline pass threshold. |

Build before running CTest; CTest does not compile executables or create the
generated profile. Render to a new filename: the CLI preserves existing outputs
and requires hard-link support for publication. The install contains four native
executables, the Python plotter, a compiled profile, two catalogs and eight event
files. It is an offline package, with no plugin or device application target.

## Find the contract behind a claim

| Area | Contracts and retained evidence |
| --- | --- |
| Initial architecture and sources | [Implementation contract](IMPLEMENTATION_CONTRACT.md), [profile format](PROFILE_FORMAT.md) and [engine API](ENGINE_API.md). The nominal sources are shared and free-running; source IDs, MIDI notes and indices are distinct. |
| Controls and saved state | [Console extension](CONSOLE_EXTENSION.md), [control-state format](CONTROL_STATE_FORMAT.md) and [parameters](PARAMETERS.md). There are 43 internal IDs; `B3CONTROLS2` reads legacy version 1 with explicit defaults. Saved controls exclude keys, owners, source phase and transient DSP histories. |
| Integrated nominal console | [Console dynamics](CONSOLE_DYNAMICS.md), [console acceptance](CONSOLE_ACCEPTANCE.md), [M3 requirements](M3_ACCEPTANCE_CONTRACT.md) and [model metadata](MODEL_METADATA.md). Independent contacts and shared percussion run in the Engine and renderer; the selected values are unmeasured. |
| Typed input and lifecycle | [Parameter bridge](PARAMETER_BRIDGE.md), [note ownership](NOTE_OWNERSHIP.md), [input transaction](INPUT_PROCESSOR.md) and [sample-rate lifecycle](SAMPLE_RATE_LIFECYCLE.md). These implemented core adapters have fixed bounds and same-thread lifecycle rules; a native host SDK/device integration still needs its own qualification. |
| Manual and pedal routing | [Factory comparison](FACTORY_REFERENCE.md), [factory runtime acceptance](FACTORY_RUNTIME_ACCEPTANCE.md) and [pedal routing](PEDAL_ROUTING.md). Documentary comparison covers all mapped positions; the audio gate covers manuals. The [next pedal kernel](M3_NEXT_GATE.md) is a plan, not implemented pedal audio. |
| Diagnostic traces | [Trace contract](CONSOLE_TRACE.md) and [plot contract](CONSOLE_TRACE_PLOTS.md): state timing, retained input hashes, limits and display reductions. Diagnostics do not establish physical authenticity. |
| Processing limits | [Callback audit](REALTIME.md), [numerical bounds](NUMERICAL_BOUNDS.md) and [benchmark](BENCHMARKING.md). Each states its observed scope; none alone qualifies a live device deadline. |
| Physical acquisitions | [Capture format](CAPTURE_FORMAT.md), [capture validation](CAPTURE_VALIDATION.md) and [acquisition protocol](CAPTURE_PROTOCOL.md). Planned metadata, actual recordings, byte integrity and physical admission are separate states. |
| Repository and platforms | [Repository checks](REPOSITORY_CHECKS.md), [CI workflow](CI.md), [current handoff](CONTINUATION_HANDOFF.md) and [continuation platform audit](reviews/CONTINUATION_PLATFORM_REVIEW.md). A pass belongs to the named revision and runner scope. |
| Current continuation reviews | [Runtime boundaries](reviews/RUNTIME_BOUNDARY_REVIEW.md), [platforms](reviews/CONTINUATION_PLATFORM_REVIEW.md) and [legacy audio](reviews/CONTINUATION_LEGACY_AUDIO.md). Each names its actual inspected revision, executed checks and limitations; the continuation ledger records later review progress. |
| Original session's final reviews | [Core](reviews/FINAL_CORE_REVIEW.md), [evidence tooling](reviews/FINAL_EVIDENCE_REVIEW.md), [claims](reviews/FINAL_CLAIMS_REVIEW.md), [integration](reviews/FINAL_INTEGRATION_REVIEW.md), [platforms](reviews/FINAL_PLATFORM_REVIEW.md) and [readiness](reviews/FINAL_READINESS_REVIEW.md). Preserve these as historical evidence for their original snapshots. |
| Future host, device and editor work | [Host integration proposal](HOST_INTEGRATION.md) and the M9 row in [ACCEPTANCE_MATRIX.md](ACCEPTANCE_MATRIX.md). Core adapter tests do not close actual VST3/device, concurrency, native UI or accessibility gates. |

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
six-range review in its own ledger. Later [factory comparison](FACTORY_REFERENCE.md)
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
| Original ten-wave implementation | [Original agent ledger](development/AGENT_LEDGER.md), [wave log](development/WAVE_LOG.md), [agent notes](development/agent-notes/) and [historical handoff](SESSION_HANDOFF.md). Their original assignment IDs 01-60 remain unchanged. |
| Independent 2026-11-13 continuation | [Separate continuation ledger](development/2026-11-13-continuation/README.md), [actual-state manifest](development/2026-11-13-continuation/assignments.json), numbered evidence notes and [current handoff](CONTINUATION_HANDOFF.md). The [continuation checker](CONTINUATION_CHECKS.md) validates this session's own 60-assignment, ten-wave records. |

Read the newest ledger and shared status before claiming a task. Contacts,
percussion, partial-key input and typed core adapters are already implemented;
the next concrete gate is [pedal routing](M3_NEXT_GATE.md). Assignment numbers
belong to their session. Planned rows do not prove dispatched or completed work.
Research waves, development waves and M0-M9 milestones describe different things.

Preserve existing history when `main` advances. Record actual changes, commands,
failures and unrun gates in the assigned note; the integrator owns shared status
and publication. Check the two scopes independently:

```sh
python3 -B tools/check_repository.py --json
python3 -B tools/check_continuation.py --json
```

The first checks its documented [navigation/data scope](REPOSITORY_CHECKS.md)
and the original session's notes. The second reports this continuation's actual
declared complete/running/planned states and validates their retained records.
Use its [explicit final count](CONTINUATION_CHECKS.md) only when all sixty new
assignments have substantively completed. These are record/integrity checks,
not product, external-execution or physical-calibration gates.
