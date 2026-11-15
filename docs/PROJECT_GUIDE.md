# Project guide

The repository provides a nominal dry-organ Engine, offline evidence tools,
an optional VST3 instrument and a native standalone window. Two 61-key manuals
and 25 pedals share 91 free-running sources: **147 playing keys**, separate
from **24 reversed presets**. Four retained drawbar banks, fixed registrations,
contacts, percussion and typed note ownership are implemented. The **47 sound
parameters**, **`B3CONTROLS4`** writer and readers 1–3 retain their meanings.
Physical organ/cabinet fidelity and full product release remain separate gates.

The active [product continuation](development/2026-11-15-product-continuation/README.md)
adds scoped native CC120/121, adapter-only CC11 endpoint/inversion calibration,
wide native legibility/material refinement and an independent ideal Leslie
crossover. Start with the [MIDI operating guide](MIDI_EXPRESSION_GUIDE.md) for
playing/configuration or the [crossover developer guide](CROSSOVER_DEVELOPER_GUIDE.md)
for the separate electrical research tools. Before development, read
[AGENTS.md](../AGENTS.md), the [whole M0–M9 plan](PLAN.md) and the
[active checkpoint](development/2026-11-15-product-continuation/CHECKPOINT.md).
The default core remains SDK-free; the playable Engine remains dry.

## Find the right entry point

| Question | Read |
| --- | --- |
| What works and what has actually passed? | [STATUS.md](STATUS.md): current behavior, source-bound local/hosted observations, milestone position and preserved historical results. |
| What is the complete product roadmap? | [PLAN.md](PLAN.md): all M0–M9 deliverables, dependencies and engineering/physical exits. |
| What should happen next? | [NEXT_STEPS.md](NEXT_STEPS.md): current session closure, then the independent M6 electrical-accuracy protocol/candidate and separate acquisition/product tracks. |
| How do I build and play with MIDI/calibration? | [MIDI_EXPRESSION_GUIDE.md](MIDI_EXPRESSION_GUIDE.md), [INTERFACE_RUNBOOK.md](INTERFACE_RUNBOOK.md) and [PRESET_RUNBOOK.md](PRESET_RUNBOOK.md): platform prerequisites, exact options, eleven modal stops, applied-state observations, recovery and Save/Load. |
| How do I build or install the crossover tools? | [Developer guide](CROSSOVER_DEVELOPER_GUIDE.md), [explicit CrossoverTools installation](CROSSOVER_INSTALL.md), [contract](LESLIE_CROSSOVER_CONTRACT.md) and [same-Hz characterization](LESLIE_CROSSOVER_CHARACTERIZATION.md). The component is separate from Engine and the standalone. |
| Where is current UI evidence? | [Visual contract](PRODUCT_VISUAL_REFINEMENT.md), [reference-gap review](design/PRODUCT_REFERENCE_GAPS.md) and the active checkpoint. The new gallery remains pending at this reconciliation; the admitted [v5 gallery](../examples/demos/standalone-interface-preview-v5/README.md) is historical `487064d2` evidence. |
| Who owns R4? | The separate [waveform session](development/2026-11-14-waveform-continuation/README.md) and its [checkpoint](development/2026-11-14-waveform-continuation/CHECKPOINT.md). R5 audible policy and R6 runtime/Engine integration have distinct gates. |
| What prevents a physical or release claim? | [Acquisition sequence](CALIBRATION_NEXT_ACQUISITION.md), [release readiness](RELEASE_READINESS.md), [rights inventory](DEPENDENCIES_AND_RIGHTS.md) and current milestone rows in STATUS/PLAN. |
| Why did something change, and what failed? | [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md), the owning session's actual notes and original source-bound reports. |

## Current source and evidence map

This 15 November 2026 wave-6 reconciliation observes published
`b9d352a82ac1afdec70c76ec5b1987785a37762e`, tree
`b3b8b68e4c1f8312d46962924b5096f4ea10c4d2`. Inspect the live checkpoint and
actual checkout/remote before resuming; a dated document is not a live query.

| Record | What it establishes |
| --- | --- |
| [Current publication receipt](development/2026-11-15-product-continuation/reports/calibration-install-publication.json), [original Linux failure](development/2026-11-15-product-continuation/reports/b9-linux-crossover-install-failure.txt) and [live repair checkpoint](development/2026-11-15-product-continuation/CHECKPOINT.md) | Verified `b9d352a` publication, with observed install/core/native portability failures. The policy-independent ancestor-loop repair passes a separate 14/14 local recheck; narrow Windows fixture repairs and repaired-source hosted qualification remain pending. The original local A31 result retains its tested CMake scope. |
| [Feature build](development/2026-11-15-product-continuation/reports/wave4-coherent-build.json) and [hosted statuses](development/2026-11-15-product-continuation/reports/implementation-hosted-status.json) | The earlier `ff41d412` feature source passed 176/176 local Release tests; thirteen hosted job statuses are successful. Primary-log audit remains separate and later changed inputs do not inherit the result. |
| [Product compatibility](PRODUCT_COMPATIBILITY.md) and [code review](reviews/PRODUCT_CONTINUATION_CODE_REVIEW.md) | Named-source preservation of musical/core/VST3 boundaries, reviewed native behavior and the scoped benchmark metadata correction. |
| [A26 lifecycle evidence](development/2026-11-15-product-continuation/reports/A26-root-native-calibration.json) | Real application and adapter with an isolated synchronous MIDI dependency: nine tests, ten processes, seven lifecycles. It is not physical-device or asynchronous driver-race evidence. |
| [Visual gap record](design/PRODUCT_REFERENCE_GAPS.md) | Current provisional native previews, accepted scoped raster/timing evidence and remaining differences. Fresh final gallery admission and actual display journeys remain separate. |
| [Completed reference-refinement closure](REFERENCE_REFINEMENT_CLOSURE.md) | Earlier `fd2f606` combined-source qualification, its sixty accepted assignments, original failures and the `487064d2` v5 capture boundary. It does not close this new session. |

Preserve the original failed, blocked and cancelled observations. A successful
build, job status, retained image, native input journey and physical device test
answer different questions. Source/executable identity binds a result to inputs;
it does not establish calibrated fidelity or native accessibility.

## Build, render, inspect and install

The default tools use a C++20 compiler, CMake 3.21+ and Python 3.10+. Optional
standalone and VST3 adapters have their own pinned dependencies and prerequisites.
Use the selected guide's complete recipe and keep dependency checkouts separate
from builds. The active checkpoint records the managed environment's exact
compiler, CMake/CTest/Ninja and read-only dependency paths.

| Task | Practical reference |
| --- | --- |
| Build core or platform configurations | [BUILD.md](BUILD.md), [core CI](CI.md), [standalone CI](STANDALONE_CI.md) and [VST3 build](VST3_BUILD.md). |
| Play and configure the current standalone | [MIDI/expression guide](MIDI_EXPRESSION_GUIDE.md), [interface runbook](INTERFACE_RUNBOOK.md), [preset runbook](PRESET_RUNBOOK.md) and [standalone app](STANDALONE_APP.md). |
| Install a local standalone or VST3 | [Standalone component](STANDALONE_INSTALL.md), [VST3 local bundle](VST3_LOCAL_INSTALL.md) and [native CI](VST3_CI.md). Follow their explicit manifests and destination rules; staging is separate from DAW/device qualification. |
| Develop or install the ideal crossover | [CROSSOVER_DEVELOPER_GUIDE.md](CROSSOVER_DEVELOPER_GUIDE.md) and [CROSSOVER_INSTALL.md](CROSSOVER_INSTALL.md). The explicit copy-only component contains six files and preserves the registry-relative reference layout. |
| Reproduce nominal rotary numerical work | [Motion](ROTARY_MOTION.md), [propagation](ROTARY_PROPAGATION.md), [renderer contract](ROTARY_RENDERER_CONTRACT.md) and [offline renderer](ROTARY_RENDER_CLI.md). Coordinate with the independent R4 owner. |
| Render registrations or sample-timed events | [Render format](RENDER_FORMAT.md), [offline installation](OFFLINE_INSTALL.md), [render evidence](RENDER_EVIDENCE.md) and [independent verification](RENDER_VERIFICATION.md). |
| Inspect console or pedal transitions | [Console trace](CONSOLE_TRACE.md), [console plots](CONSOLE_TRACE_PLOTS.md), [pedal trace](PEDAL_TRACE.md) and [pedal plots](PEDAL_TRACE_PLOTS.md). Bounded diagnostic scenarios remain separate from musical demos. |
| Replay retained musical examples | [Original examples](../examples/README.md), [two-second console](../examples/rendered/nominal-console-v2/README.md), [pedal phrase](../examples/demos/pedal-phrase-v1/README.md) and [chapel controls](CHAPEL_CONTROLS.md). Preserve each source/profile/schema identity. |
| Inspect model metadata and parameters | [Model metadata](MODEL_METADATA.md), [parameter bridge](PARAMETER_BRIDGE.md) and [parameters](PARAMETERS.md). Offline metadata is not runtime inspection of a native module. |
| Run capture/corpus/comparison workflows | [Calibration runbook](CALIBRATION_RUNBOOK.md), [handoff](CALIBRATION_HANDOFF.md) and [CaptureTools installation](CAPTURE_TOOLS_INSTALL.md). |
| Acquire the next physical evidence | [A1–A6 acquisition sequence](CALIBRATION_NEXT_ACQUISITION.md), [capture protocol](CAPTURE_PROTOCOL.md) and [validation](CAPTURE_VALIDATION.md). |
| Measure declared workloads | [Standalone benchmark](STANDALONE_BENCHMARK.md), [core benchmark](BENCHMARKING.md) and [current paint observations](development/2026-11-15-product-continuation/notes/A27-paint-performance.md). Relative regression results and raw intervals do not qualify device deadlines. |

Agree one configure/build/CTest owner per build tree. The product integrator
owns `/workspace/scratch/5b7d983ac078/build-native`; the waveform owner has a
separate checkout/build under `/workspace/scratch/e3cacb90cc81/`. Reuse pinned
dependencies, freeze relevant source and rebuild changed consumers coherently.
Build required inputs before CTest and use `--no-tests=error` for required
filtered gates. Never mix an old library with changed live headers or reset
another session's working files. Use current install manifests instead of
copying a historical payload count into a new package claim.

## Find the contract behind a claim

| Area | Contracts and evidence boundary |
| --- | --- |
| Architecture and source identity | [Implementation contract](IMPLEMENTATION_CONTRACT.md), [profile format](PROFILE_FORMAT.md), [Engine API](ENGINE_API.md) and [factory routing comparison](FACTORY_REFERENCE.md). Source IDs, terminals, MIDI notes and indices remain distinct. |
| Musical controls and persistence | [State format](CONTROL_STATE_FORMAT.md), [parameters](PARAMETERS.md), [preset contract](PRESET_SELECTION_CONTRACT.md) and [compatibility review](PRODUCT_COMPATIBILITY.md). Saved controls exclude key owners, source phase and transient DSP history. |
| Console and pedals | [Console dynamics](CONSOLE_DYNAMICS.md), [M3 acceptance](M3_ACCEPTANCE_CONTRACT.md), [pedal routing](PEDAL_ROUTING.md), [pedal Engine](PEDAL_ENGINE.md) and [pedal audio acceptance](PEDAL_AUDIO_ACCEPTANCE.md). Nominal behavior is distinct from physical loading. |
| Input ownership and native calibration | [Performance input](PERFORMANCE_INPUT.md), [manual ownership](NOTE_OWNERSHIP.md), [pedal ownership](PEDAL_NOTE_OWNERSHIP.md), [channel modes](MIDI_CHANNEL_MODE_CONTRACT.md), [expression calibration](MIDI_EXPRESSION_CALIBRATION.md) and [sample-rate lifecycle](SAMPLE_RATE_LIFECYCLE.md). Calibration belongs to the adapter, outside sound state. |
| Native UI and copied inspection | [Workspace](INTERFACE_WORKSPACE_CONTRACT.md), [geometry](INTERFACE_GEOMETRY_CONTRACT.md), [inspection](INTERFACE_INSPECTION_CONTRACT.md), [visual refinement](PRODUCT_VISUAL_REFINEMENT.md) and [remaining reference gaps](design/PRODUCT_REFERENCE_GAPS.md). Keep 147 playing keys, 24 presets and 68 controls including presets. |
| VST3 audio/state/automation | [Processor](VST3_PROCESSOR.md), [controller](VST3_CONTROLLER.md), [timeline](HOST_TIMELINE.md), [state exchange](STATE_EXCHANGE.md), [ABI](VST3_ABI_ACCEPTANCE.md) and [behavior](VST3_BEHAVIOR_ACCEPTANCE.md). Native MIDI channel-mode changes do not add a VST3 mapping. |
| Runtime resources and concurrency | [Core callback audit](REALTIME.md), [native allocation](VST3_REALTIME.md), [automation review](VST3_AUTOMATION_REVIEW.md), [VST3 concurrency](VST3_CONCURRENCY.md) and [numerical bounds](NUMERICAL_BOUNDS.md). Each result retains its instrumented workload and exclusions. |
| Scanner | [Scanner handoff](SCANNER_HANDOFF.md), [numerical contract](SCANNER_NUMERICAL_CONTRACT.md) and [AC parity](SCANNER_AC_PARITY.md). Preserve the unresolved G5 same-Hz failure before live integration. |
| Leslie crossover | [Frozen circuit contract](LESLIE_CROSSOVER_CONTRACT.md), [developer workflow](CROSSOVER_DEVELOPER_GUIDE.md) and [same-Hz observations](LESLIE_CROSSOVER_CHARACTERIZATION.md). Ideal 16-ohm defaults are not driver measurements; no Engine route exists. |
| Rotary | [Numerical contract](ROTARY_NUMERICAL_CONTRACT.md), [R4 renderer](ROTARY_RENDERER_CONTRACT.md) and [waveform acceptance](ROTARY_WAVEFORM_ACCEPTANCE.md). R4 discrete parity, R5 audible policy, R6 runtime integration and physical fidelity are distinct. |
| Physical and release evidence | [Capture format](CAPTURE_FORMAT.md), [acquisition protocol](CAPTURE_PROTOCOL.md), [release readiness](RELEASE_READINESS.md) and [dependencies/rights](DEPENDENCIES_AND_RIGHTS.md). Tool acceptance does not establish hardware or distribution permission. |

Evidence classes describe inputs: `documented`, `measured`, `derived`, `proposed`
and `unknown`. Outcomes describe execution: `pass`, `failed`, `blocked`,
`not_run` and `inconclusive`. Keep the input identity, setup, criterion, actual
result and limitation together. The [acceptance matrix](ACCEPTANCE_MATRIX.md)
retains earlier milestone assessments; current STATUS/PLAN own the new M6/M9 scope.

## Source and reading records

The unchanged [500-page atlas](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf) has
SHA-256 `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
The [source manifest](research/source-manifest.json), [chapter index](research/chapter-index.json)
and [errata](research/ERRATA.md) retain its provenance, 80 chapters and known
implementation hazards. Current A01–A06 retain complete textual coverage:

| Pages | Current session reading |
| --- | --- |
| 1–84 | [A01 foundations and generator](development/2026-11-15-product-continuation/notes/A01-atlas-foundation.md) |
| 85–168 | [A02 console](development/2026-11-15-product-continuation/notes/A02-atlas-console.md) |
| 169–252 | [A03 electronics](development/2026-11-15-product-continuation/notes/A03-atlas-electronics.md) |
| 253–336 | [A04 electrical cabinet and rotary boundaries](development/2026-11-15-product-continuation/notes/A04-atlas-rotary.md) |
| 337–420 | [A05 calibration/runtime and native visuals](development/2026-11-15-product-continuation/notes/A05-atlas-visual.md) |
| 421–500 | [A06 product, full milestones and acceptance](development/2026-11-15-product-continuation/notes/A06-atlas-product.md) |

Each note retains its extract hash and specific findings. This coverage does
not independently verify every external source/figure or recover missing
companions. Earlier [atlas review](research/ATLAS_REVIEW.md),
[reference-refinement review](research/REFERENCE_REFINEMENT_ATLAS_REVIEW.md)
and [waveform review](research/WAVEFORM_ATLAS_REVIEW.md) remain separate records.

## Ownership, historical records and continuation

| Session | Recovery records |
| --- | --- |
| Active product continuation | [Scope](development/2026-11-15-product-continuation/README.md), [checkpoint](development/2026-11-15-product-continuation/CHECKPOINT.md), [actual manifest](development/2026-11-15-product-continuation/assignments.json) and [ten-wave plan](development/2026-11-15-product-continuation/WAVES.md). Only actual accepted work counts toward its sixty assignments. |
| Separate waveform continuation | [Scope](development/2026-11-14-waveform-continuation/README.md), [checkpoint](development/2026-11-14-waveform-continuation/CHECKPOINT.md) and [actual manifest](development/2026-11-14-waveform-continuation/assignments.json). It retains R4 and its other checkout. |
| Completed reference refinement | [Closure](REFERENCE_REFINEMENT_CLOSURE.md), [checkpoint](development/2026-11-14-reference-refinement/CHECKPOINT.md) and [strict completion result](development/2026-11-14-reference-refinement/completion-check.json). Preserve its sixty accepted workers and exact-source qualification. |
| Earlier product sessions | [Interface recovery](INTERFACE_RECOVERY_HANDOFF.md), [preset session](development/2026-11-14-preset-continuation/README.md), [MIDI/UI handoff](MIDI_UI_HANDOFF.md), [standalone handoff](STANDALONE_HANDOFF.md) and [pedal handoff](PEDAL_HANDOFF.md). |
| Independent research/acquisition tracks | [Scanner](SCANNER_HANDOFF.md), [rotary foundation](ROTARY_SCOPE.md) and [completed calibration tooling](CALIBRATION_HANDOFF.md). Physical acquisition remains separate. |
| Original and console histories | [Original ledger](development/AGENT_LEDGER.md), [wave log](development/WAVE_LOG.md), [original handoff](SESSION_HANDOFF.md) and [console continuation](CONTINUATION_HANDOFF.md). |

The [concurrent handoff](development/2026-11-14-reference-refinement/CONCURRENT_HANDOFF.md)
retains cross-session ownership boundaries. Recover the full plan and actual
source, choose a dependency-ready task, retain exact verification and update
setup/status/next steps/log through the assigned owner. Interface changes need
new actual captures before README promotion. Checkpoint each wave; preserve
compact evidence before removing only owned reproducible intermediates.

The integrator completes this session's own actual records and strict checker,
then commits and publishes authorized accepted work with a fresh expected head
and no force. Verify the fetched commit/tree and required hosted results.
Historical checkers, planned assignments and a publication request do not prove
new acceptance. No project-wide license has been selected; the
[notices](../THIRD_PARTY_NOTICES.md) and [source-rights record](research/RIGHTS_AND_SOURCES.md)
retain the applicable provenance and unresolved distribution decisions.
