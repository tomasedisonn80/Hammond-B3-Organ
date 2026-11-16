# Project guide

**Code qualification update, 16 November 2026:** implementation `af2b747` and the
Windows I/O repair `2f57723` are published and independently fetched. All **13
hosted jobs pass at `2f57723`**, as recorded in the
[completed platform receipt](development/2026-11-15-streaming-continuation/reports/hosted-2f57723-complete.json).
The original `af2b747` Windows failure remains separate. Local qualification is
[210/210 in 191.90 seconds](development/2026-11-15-streaming-continuation/reports/final-coherent-qualification.json),
then the [sole EOF cleanup](development/2026-11-15-streaming-continuation/reports/publication-source-qualification.json),
then [3/3 affected I/O suites](development/2026-11-15-streaming-continuation/reports/windows-repair-qualification.json).
Earlier receipts keep their original inputs and timings. The
[session checkpoint](development/2026-11-15-streaming-continuation/CHECKPOINT.md)
records completed worker closure and source-qualified publication history.
[All 60 accepted records pass strict validation](development/2026-11-15-streaming-continuation/reports/streaming-session-strict.json).
Code qualification does not close physical, whole-interface 1:1, device or accessibility gates.

The repository provides a nominal dry-organ Engine, offline evidence tools,
an optional VST3 instrument and a native standalone window. Two 61-key manuals
and 25 pedals share 91 free-running sources: **147 playing keys**, separate
from **24 reversed presets**. Four retained drawbar banks, fixed registrations,
contacts, percussion and typed note ownership are implemented. The **47 sound
parameters**, **`B3CONTROLS4`** writer and readers 1–3 retain their meanings.
Physical organ/cabinet fidelity and full product release remain separate gates.

The active [streaming/material continuation](development/2026-11-15-streaming-continuation/README.md)
adds the isolated `causal-contact-grid-v1` trajectory and a narrow Upper-rack
inner-metal refinement. Its coherent Linux Release gate passed **210/210 CTests
in 191.89 seconds** at its original inputs. Implementation `af2b747` and repair
`2f57723` are published; all 13 repaired-source hosted jobs pass. The requested
sixty-worker record closure passes with all 60 scoped deliveries accepted. Start with the
[causal-grid guide](CAUSAL_CONTACT_GRID_GUIDE.md) for this finite research API or
the [current gallery](../examples/demos/upper-rack-material-v1/README.md) for
actual native UI evidence. Before development, read
[AGENTS.md](../AGENTS.md), the [whole M0–M9 plan](PLAN.md) and the
[active checkpoint](development/2026-11-15-streaming-continuation/CHECKPOINT.md).
The [MIDI operating guide](MIDI_EXPRESSION_GUIDE.md) retains playing/configuration
instructions, while the [crossover guide](CROSSOVER_DEVELOPER_GUIDE.md) covers
separate electrical research. The default core remains SDK-free; the playable
Engine remains dry. Literal whole-interface 1:1 and physical/display/accessibility
gates remain open.

## Find the right entry point

| Question | Read |
| --- | --- |
| What works and what has actually passed? | [STATUS.md](STATUS.md): current behavior, source-bound local/hosted observations, milestone position and preserved historical results. |
| What is the complete product roadmap? | [PLAN.md](PLAN.md): all M0–M9 deliverables, dependencies and engineering/physical exits. |
| What should happen next? | [NEXT_STEPS.md](NEXT_STEPS.md): converter and causal audio schedule/partial-cell/filter/drain/full-window work after the completed trajectory; full-organ/indefinite and Engine lifecycle gates; remaining UI materials/type, display/accessibility and separately owned numerical/adapter tracks. |
| How does a future agent recover this workspace? | [Current checkpoint](development/2026-11-15-streaming-continuation/CHECKPOINT.md), [scope](development/2026-11-15-streaming-continuation/SCOPE.md), [current setup](STATUS.md#current-workspace-and-setup) and [ownership map](PLAN.md#current-ownership-and-source). [PRODUCT_HANDOFF.md](PRODUCT_HANDOFF.md) retains dated product recovery and clean-checkout recipes; its earlier paths and results do not override this session's ownership. |
| How are this session's actual records checked? | [Current record guidance](NEXT_STEPS.md#validate-this-sessions-actual-records) and [actual streaming ledger](development/2026-11-15-streaming-continuation/assignments.json). All 60 scoped deliveries are accepted in ten waves; the [matching strict receipt](development/2026-11-15-streaming-continuation/reports/streaming-session-strict.json) verifies the retained records/notes. Older results and followups supply no worker credit; the checker is not external-dispatch or product proof. |
| How do I inspect the new causal trajectory? | [Developer guide](CAUSAL_CONTACT_GRID_GUIDE.md), [frozen contract](CAUSAL_CONTACT_GRID_CONTRACT.md), [implementation review](reviews/CAUSAL_CONTACT_GRID_IMPLEMENTATION_REVIEW.md) and [resource admission](reviews/CAUSAL_CONTACT_GRID_RESOURCE_ADMISSION.md). Exactness applies to the declared finite integer domain, without a float converter, audio stage or Engine route. |
| How do I reproduce the earlier offline contact study? | [Operating guide](CONTACT_SWITCHING_GUIDE.md), [executed results](CONTACT_SWITCHING_RESULTS.md) and [ContactReferenceTools installation](CONTACT_REFERENCE_INSTALL.md). The acausal binary64-input reference and its original 36×4 results remain separate from causal-grid acceptance. |
| How do I build and play with MIDI/calibration? | [MIDI_EXPRESSION_GUIDE.md](MIDI_EXPRESSION_GUIDE.md), [INTERFACE_RUNBOOK.md](INTERFACE_RUNBOOK.md) and [PRESET_RUNBOOK.md](PRESET_RUNBOOK.md): platform prerequisites, exact options, eleven modal stops, applied-state observations, recovery and Save/Load. |
| How do I build or install the crossover tools? | [Developer guide](CROSSOVER_DEVELOPER_GUIDE.md), [explicit CrossoverTools installation](CROSSOVER_INSTALL.md), [contract](LESLIE_CROSSOVER_CONTRACT.md) and [same-Hz characterization](LESLIE_CROSSOVER_CHARACTERIZATION.md). The component is separate from Engine and the standalone. |
| Where is current UI evidence? | [Twelve Upper-rack material views](../examples/demos/upper-rack-material-v1/README.md), [gallery admission](reviews/UPPER_RACK_GALLERY_ADMISSION.md), [paired-comparison admission](reviews/UPPER_RACK_COMPARISON_ADMISSION.md) and [painter review](reviews/UPPER_RACK_PAINTER_REVIEW.md). The actual app hash begins `c29495e9`; the [earlier wide-composition gallery](../examples/demos/whole-reference-layout-v1/README.md), product captures and v5 retain their own identities. Whole-interface 1:1 remains unmet. |
| Who owns the other active tracks? | [Current ownership map](PLAN.md#current-ownership-and-source): execution/contact/composition, audio/leakage, playable/harmonic sources, scanner/library, fidelity/crossover/native retirement and waveform/R4 keep distinct recovery authorities. |
| Who owns R4? | The separate [waveform session](development/2026-11-14-waveform-continuation/README.md) and its [checkpoint](development/2026-11-14-waveform-continuation/CHECKPOINT.md). R5 audible policy and R6 runtime/Engine integration have distinct gates. |
| What prevents a physical or release claim? | [Acquisition sequence](CALIBRATION_NEXT_ACQUISITION.md), [release readiness](RELEASE_READINESS.md), [rights inventory](DEPENDENCIES_AND_RIGHTS.md) and current milestone rows in STATUS/PLAN. |
| Why did something change, and what failed? | [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md), the owning session's actual notes and original source-bound reports. |

## Current source and evidence map

The streaming session started from `4aac394cde4da40906b615573a8779aee2d9a37a`,
tree `3605c9ce098a052afc10b2969fefe31e15644fe9`. The
[implementation publication](development/2026-11-15-streaming-continuation/reports/implementation-publication.json)
verifies `af2b747`, and the [Windows repair publication](development/2026-11-15-streaming-continuation/reports/repair-publication.json)
verifies `2f57723`, tree `cee5fdc4b07d95185ebd9e4d1c5f236f88a787f9`.
All [13 repaired-source hosted jobs](development/2026-11-15-streaming-continuation/reports/hosted-2f57723-complete.json)
pass; the initial Windows failure remains a separate record. The qualification
update above binds the first coherent run, later 210/210 gate, sole EOF cleanup
and two-file I/O repair without relabelling older results. All 60 retained worker
records are accepted and strictly verified. Inspect checkout/index/HEAD/remote
and checkpoint before resuming;
receipts do not qualify changed inputs or real devices.

| Current record | What it establishes |
| --- | --- |
| [Baseline qualification](development/2026-11-15-streaming-continuation/reports/baseline-qualification.json) and [coherent qualification](development/2026-11-15-streaming-continuation/reports/coherent-qualification.json) | The unchanged starting source passed 203/203 in 192.21 s; the later identified streaming/material inputs passed 210/210 in 191.89 s. Their original logs, configurations and executable hashes remain distinct. |
| [Causal contract admission](reviews/CAUSAL_CONTACT_GRID_ADMISSION.md) and [implementation review](reviews/CAUSAL_CONTACT_GRID_IMPLEMENTATION_REVIEW.md) | The finite integer model's arithmetic, exact roots/order, anchor persistence, causal partitions and transactional lifecycle have independently reviewed source arguments. No binary64 conversion, audio or physical grade follows. |
| [Independent differential suite](development/2026-11-15-streaming-continuation/notes/A21.md), [lifecycle suite](development/2026-11-15-streaming-continuation/notes/A22.md) and [transport suite](development/2026-11-15-streaming-continuation/notes/A24.md) | The Fraction/native comparison passed 11 methods / 199 probe invocations; separate lifecycle/rollback and 17-method / 150-process CLI checks retain their own boundaries. Coherent qualification supplies the final integrated Linux result. |
| [Resource admission](reviews/CAUSAL_CONTACT_GRID_RESOURCE_ADMISSION.md) and [portability review](reviews/CAUSAL_CONTACT_GRID_PORTABILITY.md) | Both retained resource binaries reproduced the receipts: 192 scopes with zero hooked C++ allocations/frees, local object size 113,056 B and bounded per-call work. Hook/ABI/epoch limits remain explicit. Windows raw-stdin was repaired in source; [initial hosted review](reviews/STREAMING_INITIAL_HOSTED_ADMISSION.md) verifies all six causal suites on Windows and the other core jobs. Repaired `2f57723` passes Windows 185/185. The forced mode-failure branch remains unexecuted. |
| [Upper material contract](design/UPPER_RACK_MATERIAL_CONTRACT.md), [comparison admission](reviews/UPPER_RACK_COMPARISON_ADMISSION.md) and [painter review](reviews/UPPER_RACK_PAINTER_REVIEW.md) | 96 genuine old/new pairs cover 307,095,606 pixels with zero support escapes, 37 exact required whole frames and five passing local reference screens. Baseline failures remain; resource crops protect zero exterior pixels. Source review separately admits painter arithmetic/state/work limits. |
| [Current gallery](../examples/demos/upper-rack-material-v1/README.md) and [gallery admission](reviews/UPPER_RACK_GALLERY_ADMISSION.md) | Twelve actual app images pass 641 identity/state/pixel checks and direct full-frame inspection at app hash `c29495e9…`. Runtime counter/meter drift remains; these are separate from exact-state comparison pairs. Whole-interface 1:1, display/DPI and semantic accessibility remain open. |
| [Compatibility review](reviews/STREAMING_CONTINUATION_COMPATIBILITY.md) | Original Engine, 91-source, 47-parameter, state4/readers 1–3, UUID, PDF/art and earlier fixture identities are retained. One dry fixture matches its full WAV and all 16,384 decoded samples. The old receipt's mislabeled WAV/PCM hash is explained without rewriting that evidence. Its original 48-file package equality is source-bound: the [later I/O repair](reviews/CONTACT_REFERENCE_WINDOWS_REPAIR_ADMISSION.md) changes one wrapper, preserving all 48 names, other 47 hashes and install rules. |

### Prepared continuation routes

The [reviewed next-proposal table](NEXT_STEPS.md#reviewed-next-proposals-and-decisions)
records concrete blockers and exclusive-owner boundaries. Start from
[conversion](research/CONTACT_GRID_CONVERSION_NEXT.md) / [review](reviews/CONTACT_GRID_CONVERSION_NEXT_REVIEW.md),
[isolated audio](research/CAUSAL_CONTACT_AUDIO_NEXT.md) / [review](reviews/CAUSAL_CONTACT_AUDIO_NEXT_REVIEW.md),
[capacity](research/CAUSAL_CONTACT_CAPACITY_NEXT.md) / [review](reviews/CAUSAL_CONTACT_CAPACITY_NEXT_REVIEW.md),
[whole-window comparison](design/WHOLE_WINDOW_REFERENCE_NEXT.md) and
[materials/type](design/REFERENCE_MATERIAL_TYPE_NEXT.md) / [review](reviews/REFERENCE_MATERIAL_NEXT_REVIEW.md),
then [native use/accessibility](design/NATIVE_ACCESSIBILITY_JOURNEY_NEXT.md) /
[review](reviews/NATIVE_ACCESSIBILITY_JOURNEY_NEXT_REVIEW.md). These are completed
planning/review inputs, **not admitted implementation contracts**. Lower L1 needs
its own field/criteria; T1 separately needs unequal-aspect type geometry. Conversion needs event
correspondence as well as scalar error; audio needs bounded wider-rational
arithmetic, atomic history and full-window grading. Capacity, native semantics
and physical acquisition keep separate exits.

### Earlier execution evidence

The [earlier execution session](development/2026-11-15-execution-continuation/README.md)
delivered the offline fractional-contact reference and canonical wide composition
from base `33fa95d51e44234eef47ee21c03d29b2b311a5ee`, tree
`f5d9406ef099f6569a5d1f3fee27358b520bc928`. Its
[installed 36×4 study](CONTACT_SWITCHING_RESULTS.md) retains zero failed cells,
21.728087337 s external wall and 36,974,592 bytes exact-child peak RSS. Continuous
admission covers 64 probes per fixture; convergence covers all 289 samples.
Its [203/203 local result in 191.37 s](development/2026-11-15-execution-continuation/reports/coherent-qualification.json)
and [twelve-frame wide-layout admission](reviews/WHOLE_REFERENCE_GALLERY_ADMISSION.md)
remain source-specific history, including original failures and the 34-pixel
minimum protected active region. The
[earlier checkpoint](development/2026-11-15-execution-continuation/CHECKPOINT.md)
and [ledger](development/2026-11-15-execution-continuation/assignments.json) retain
unfinished accounting and owner-local work; this continuation does not declare
that earlier sixty-worker ledger complete.

### Earlier completed product qualification

The completed product session published
`80b8cce1773e4c31bf64cb6c2b7f43e8445ec3fe`, tree
`d310be065db2bb9b0012c11a0c5ec2beda4c9384`, with verified parent c4486ba.
Its sixty actual worker results are accepted, strict validation passes and all
thirteen required hosted jobs pass at that exact source. These records do not
qualify the current overlay or supply worker credit to this request. The
[batch record](PRODUCT_CONTINUATION_CLOSURE.md) retains its unmet, unwaived 1:1
UI requirement and original next work orders; the current PLAN/NEXT_STEPS route
the subsequent implemented work and remaining gates.
Its [eight normal views](../examples/demos/standalone-product-preview-v1/README.md),
[three MIDI overlays](../examples/demos/standalone-product-preview-v1/midi-overlay/README.md)
and the earlier [v5 gallery](../examples/demos/standalone-interface-preview-v5/README.md)
remain historical captures with their original source/executable identities.

| Record | What it establishes |
| --- | --- |
| [Repaired publication](development/2026-11-15-product-continuation/reports/checker-portability-publication.json) and [required hosted gate](development/2026-11-15-product-continuation/reports/root-final-hosted.json) | Exact 80b8cce commit/tree/parent and guarded nonforced update. All thirteen required jobs pass at 80b8cce, including strict actual-sixty execution; original c448 remains eleven successful / two failed jobs. |
| [Portable checker review](development/2026-11-15-product-continuation/reports/final-checker-portability-independent-review.json) and [root affected gate](development/2026-11-15-product-continuation/reports/checker-portability-root-verification.json) | Mac temporary-path fault targets and Windows cross-API metadata are repaired. The repaired 23-method module, four reader methods / 30 subcases and registered affected CTest pass locally. All actual sixty notes/identities remain unchanged and strict validation passes. |
| [Earlier d8 publication](development/2026-11-15-product-continuation/reports/gallery-publication.json) and [hosted statuses](development/2026-11-15-product-continuation/reports/d8-hosted-status.json) | Verified d8 commit/tree/parent and expected-head/non-force update; all thirteen hosted jobs succeed at that source. Later checker/plot-admission changes are outside those inputs. |
| Primary [Linux](reviews/PRODUCT_LINUX_HOSTED_REVIEW.md), [Windows](reviews/PRODUCT_WINDOWS_HOSTED_REVIEW.md), [macOS](reviews/PRODUCT_MACOS_HOSTED_REVIEW.md) and [VST3](reviews/PRODUCT_VST3_HOSTED_REVIEW.md) reviews | At d8: core Release 155/155 on each platform; Linux core sanitizers 155/155; four native Release configurations 48/48 each; expanded Linux native sanitizers 21/21; VST3 8/7/7 with 47/47 plug-in validator checks per platform. The full R4 pass qualifies its published inputs without closing another owner's unfinished work. |
| [Later coherent local build/CTest](development/2026-11-15-product-continuation/reports/wave8-coherent-build.json) and [full log](development/2026-11-15-product-continuation/reports/wave8-full-ctest.txt) | d8 plus accepted A46/A48 changes passes 180/180 in 507.55 s, with 366 frozen code/test/build/data inputs unchanged. GCC 14.2 Release, standalone ON, native MIDI backend OFF, VST3 OFF and dummy SDL. Those original inputs were published at c448; the subsequent checker/test portability changes retain separate qualification above. |
| [Original b9 Linux failure](development/2026-11-15-product-continuation/reports/b9-linux-crossover-install-failure.txt), [Windows history](reviews/PRODUCT_WINDOWS_HOSTED_REVIEW.md) and [d556 sanitizer build failure](development/2026-11-15-product-continuation/reports/d556-native-sanitizer-build-failure.json) | Earlier failed outcomes remain intact beside the d8 repaired-source passes. The numeric ancestor-loop, owned SDL environment strings, Windows newline comparison and test-facade clear/push-back repairs retain their exact scopes; no new sanitizer exception was added. |
| [Earlier feature build](development/2026-11-15-product-continuation/reports/wave4-coherent-build.json) and [statuses](development/2026-11-15-product-continuation/reports/implementation-hosted-status.json) | `ff41d412` passed 176/176 local Release tests and has thirteen successful hosted statuses. Its earlier fixture/install inputs stay distinct from d8 and subsequent changes. |
| [Product compatibility](PRODUCT_COMPATIBILITY.md) and [code review](reviews/PRODUCT_CONTINUATION_CODE_REVIEW.md) | Named-source preservation of musical/core/VST3 boundaries, reviewed native behavior and the scoped benchmark metadata correction. |
| [A26 lifecycle evidence](development/2026-11-15-product-continuation/reports/A26-root-native-calibration.json) | Real application and adapter with an isolated synchronous MIDI dependency: nine tests, ten processes, seven lifecycles. It is not physical-device or asynchronous driver-race evidence. |
| [Gallery admission](reviews/PRODUCT_GALLERY_ADMISSION.md), [modal raster receipt](development/2026-11-15-product-continuation/reports/A42-calibration-modal-raster.json) and [visual gap record](design/PRODUCT_REFERENCE_GAPS.md) | Eleven admitted d556 native frames and its 1,293 material assertions/109 frames retain source, state and pixel identities. These earlier captures remain preserved; original BMPs remain unavailable. Literal 1:1 equality remains unmet; actual display/accessibility journeys remain unqualified. |
| [Installed workflow](STANDALONE_INSTALL.md), [A43 receipt](development/2026-11-15-product-continuation/reports/A43-root-installed-ctest.txt) and primary native reviews | At that source the Standalone inventory is 16 files MIDI-OFF / 20 MIDI-ON, including the calibration guide. Local eight-method acceptance and hosted relocation/package assertions pass in their named configurations; CrossoverTools remains six files. |
| [Native recovery review](reviews/PRODUCT_NATIVE_RECOVERY_REVIEW.md) | A47-N1 identifies suppressed WinMM/CoreMIDI native-close failures before the wrapper can establish callback retirement. This is a source-proven gap and unexecuted risk model, not an observed hardware failure/use-after-free. The next gate is below-RtMidi fault injection and checked-close/lifetime acceptance. |
| [Numerical admission review](reviews/PRODUCT_NUMERICAL_ADMISSION_REVIEW.md) and [plot refresh](development/2026-11-15-product-continuation/reports/crossover-plot-admission-refresh.json) | The repaired admission tool rejects incomplete/contradictory reports while retaining numerical source/probe/thresholds. The grid is 126 in-band / 130 total points per group. Refreshed plot pixels are identical; only generator-hash metadata changed. |
| [Completed reference-refinement closure](REFERENCE_REFINEMENT_CLOSURE.md) | Earlier `fd2f606` combined-source qualification, its sixty accepted assignments, original failures and the `487064d2` v5 capture boundary. Its worker credit and source qualification remain separate from this session. |

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
| Build and inspect the isolated causal contact grid | [Causal-grid developer guide](CAUSAL_CONTACT_GRID_GUIDE.md): SDK-free C++ API/probe, exact finite input domain, transport examples, lifecycle and affected checks. It is separate from the frozen offline installation payload. |
| Reproduce the offline fractional-contact reference | [Contact operating guide](CONTACT_SWITCHING_GUIDE.md), [results](CONTACT_SWITCHING_RESULTS.md) and [ContactReferenceTools installation](CONTACT_REFERENCE_INSTALL.md): 48-file component with one later [reviewed I/O repair](reviews/CONTACT_REFERENCE_WINDOWS_REPAIR_ADMISSION.md), 47 other payload hashes/install rules unchanged, and original synthetic-study source bounds retained. |
| Develop or install the ideal crossover | [CROSSOVER_DEVELOPER_GUIDE.md](CROSSOVER_DEVELOPER_GUIDE.md) and [CROSSOVER_INSTALL.md](CROSSOVER_INSTALL.md). The explicit copy-only component contains six files and preserves the registry-relative reference layout. |
| Reproduce nominal rotary numerical work | [Motion](ROTARY_MOTION.md), [propagation](ROTARY_PROPAGATION.md), [renderer contract](ROTARY_RENDERER_CONTRACT.md) and [offline renderer](ROTARY_RENDER_CLI.md). Coordinate with the independent R4 owner. |
| Render registrations or sample-timed events | [Render format](RENDER_FORMAT.md), [offline installation](OFFLINE_INSTALL.md), [render evidence](RENDER_EVIDENCE.md) and [independent verification](RENDER_VERIFICATION.md). |
| Inspect console or pedal transitions | [Console trace](CONSOLE_TRACE.md), [console plots](CONSOLE_TRACE_PLOTS.md), [pedal trace](PEDAL_TRACE.md) and [pedal plots](PEDAL_TRACE_PLOTS.md). Bounded diagnostic scenarios remain separate from musical demos. |
| Replay retained musical examples | [Original examples](../examples/README.md), [two-second console](../examples/rendered/nominal-console-v2/README.md), [pedal phrase](../examples/demos/pedal-phrase-v1/README.md) and [chapel controls](CHAPEL_CONTROLS.md). Preserve each source/profile/schema identity. |
| Inspect model metadata and parameters | [Model metadata](MODEL_METADATA.md), [parameter bridge](PARAMETER_BRIDGE.md) and [parameters](PARAMETERS.md). Offline metadata is not runtime inspection of a native module. |
| Run capture/corpus/comparison workflows | [Calibration runbook](CALIBRATION_RUNBOOK.md), [handoff](CALIBRATION_HANDOFF.md) and [CaptureTools installation](CAPTURE_TOOLS_INSTALL.md). |
| Acquire the next physical evidence | [A1–A6 acquisition sequence](CALIBRATION_NEXT_ACQUISITION.md), [capture protocol](CAPTURE_PROTOCOL.md) and [validation](CAPTURE_VALIDATION.md). |
| Measure declared workloads | [Standalone benchmark](STANDALONE_BENCHMARK.md), [core benchmark](BENCHMARKING.md), [causal-grid resource admission](reviews/CAUSAL_CONTACT_GRID_RESOURCE_ADMISSION.md), [Upper painter work review](reviews/UPPER_RACK_PAINTER_REVIEW.md) and [earlier paint observations](development/2026-11-15-product-continuation/notes/A27-paint-performance.md). Work bounds, relative regression results and raw intervals do not qualify device deadlines. |

Agree one configure/build/CTest owner per build tree. The current integrator owns
`/workspace/scratch/177e78b1ac09/build-native` beside the sole writable session
checkout `/workspace/scratch/177e78b1ac09/Hammond-B3-Organ`. Its pinned SDL
dependency `/workspace/scratch/ade21b726509/SDL2` is read-only. The earlier product
build `/workspace/scratch/5b7d983ac078/build-native`, execution checkout/build
under `/workspace/scratch/ade21b726509/` and waveform checkout/build under
`/workspace/scratch/e3cacb90cc81/` retain their owners. Reuse pinned
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
| Isolated causal contact trajectory | [Grid contract](CAUSAL_CONTACT_GRID_CONTRACT.md), [guide](CAUSAL_CONTACT_GRID_GUIDE.md), [source review](reviews/CAUSAL_CONTACT_GRID_IMPLEMENTATION_REVIEW.md) and [resources](reviews/CAUSAL_CONTACT_GRID_RESOURCE_ADMISSION.md). 44,100/48,000/96,000 Hz fixed per epoch; 65,536 ticks/frame; 1–4 keys × nine contacts; integer positions 0–`2^48`, speeds 1–`UINT32_MAX`; at most 4,096 frames, 512 supplied commands and 4,608 edges. Exact rational outputs do not establish binary64 conversion, indefinite performance or audio parity. |
| Contact audio continuation | [Earlier reference](FRACTIONAL_CONTACT_REFERENCE.md), [frozen validation](CONTACT_SWITCHING_VALIDATION.md), [results](CONTACT_SWITCHING_RESULTS.md), [streaming proposal](CONTACT_STREAMING_NEXT_DESIGN.md) and [independent design review](reviews/CONTACT_STREAMING_DESIGN_REVIEW.md). Next admit conversion/error policy, absolute phase, proposed D=16 schedule, partial-cell integration/filter, 33-sample nonempty drain and full-window criteria; full-organ/Engine/host lifecycle remains separate. |
| Input ownership and native calibration | [Performance input](PERFORMANCE_INPUT.md), [manual ownership](NOTE_OWNERSHIP.md), [pedal ownership](PEDAL_NOTE_OWNERSHIP.md), [channel modes](MIDI_CHANNEL_MODE_CONTRACT.md), [expression calibration](MIDI_EXPRESSION_CALIBRATION.md), [sample-rate lifecycle](SAMPLE_RATE_LIFECYCLE.md) and [native recovery review](reviews/PRODUCT_NATIVE_RECOVERY_REVIEW.md). Calibration belongs to the adapter, outside sound state; below-RtMidi callback retirement needs its own evidence. |
| Native UI and copied inspection | [Workspace](INTERFACE_WORKSPACE_CONTRACT.md), [geometry](INTERFACE_GEOMETRY_CONTRACT.md), [inspection](INTERFACE_INSPECTION_CONTRACT.md), [wide composition](WHOLE_REFERENCE_LAYOUT_CONTRACT.md), [Upper material](design/UPPER_RACK_MATERIAL_CONTRACT.md), [earlier visual refinement](PRODUCT_VISUAL_REFINEMENT.md) and [reference gaps](design/PRODUCT_REFERENCE_GAPS.md). Keep 147 playing keys, 24 presets and 68 controls including presets. Scoped material/containment does not close whole-interface 1:1. |
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
retains earlier milestone assessments; current STATUS/PLAN own the isolated M3/M9
scope and preserve the complete M0–M9 exits and independent owners.

## Source and reading records

The unchanged [500-page atlas](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf) has
SHA-256 `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
The [source manifest](research/source-manifest.json), [chapter index](research/chapter-index.json)
and [errata](research/ERRATA.md) retain its provenance, 80 chapters and known
implementation hazards. The streaming session's **six new readers** cover all
500 textual pages without gaps or overlap; their note/extract hashes and actual
identities are retained in the
[current coverage receipt](development/2026-11-15-streaming-continuation/reports/atlas-reading-coverage.json).

| Pages | Current streaming-session reading |
| --- | --- |
| 1–84 | [A01 atlas and governance](development/2026-11-15-streaming-continuation/notes/A01-atlas-governance.md) |
| 85–168 | [A02 atlas and UI](development/2026-11-15-streaming-continuation/notes/A02-atlas-ui.md) |
| 169–252 | [A03 atlas and build](development/2026-11-15-streaming-continuation/notes/A03-atlas-build.md) |
| 253–336 | [A04 atlas and numerical models](development/2026-11-15-streaming-continuation/notes/A04-atlas-numerics.md) |
| 337–420 | [A05 atlas and visual requirements](development/2026-11-15-streaming-continuation/notes/A05-atlas-visual.md) |
| 421–500 | [A06 atlas and completion gates](development/2026-11-15-streaming-continuation/notes/A06-atlas-completion.md) |

### Earlier execution-session coverage

The earlier [execution reading receipt](development/2026-11-15-execution-continuation/reports/atlas-reading-coverage.json)
retains its different contiguous ranges and independent extract identities:

| Pages | Earlier execution reading |
| --- | --- |
| 1–84 | [A01](development/2026-11-15-execution-continuation/notes/A01.md) |
| 85–167 | [A02](development/2026-11-15-execution-continuation/notes/A02.md) |
| 168–250 | [A03](development/2026-11-15-execution-continuation/notes/A03.md) |
| 251–334 | [A04](development/2026-11-15-execution-continuation/notes/A04.md) |
| 335–417 | [A05](development/2026-11-15-execution-continuation/notes/A05.md) |
| 418–500 | [A06](development/2026-11-15-execution-continuation/notes/A06.md) |

### Earlier product-session coverage

The completed product session's original six readings remain separate:

| Pages | Earlier product reading |
| --- | --- |
| 1–84 | [A01 foundations and generator](development/2026-11-15-product-continuation/notes/A01-atlas-foundation.md) |
| 85–168 | [A02 console](development/2026-11-15-product-continuation/notes/A02-atlas-console.md) |
| 169–252 | [A03 electronics](development/2026-11-15-product-continuation/notes/A03-atlas-electronics.md) |
| 253–336 | [A04 electrical cabinet and rotary boundaries](development/2026-11-15-product-continuation/notes/A04-atlas-rotary.md) |
| 337–420 | [A05 calibration/runtime and native visuals](development/2026-11-15-product-continuation/notes/A05-atlas-visual.md) |
| 421–500 | [A06 product, full milestones and acceptance](development/2026-11-15-product-continuation/notes/A06-atlas-product.md) |

Each note retains its extract hash and specific findings. No earlier reader is
recounted for the current worker request. These readings do
not independently verify every external source/figure or recover missing
companions. Earlier [atlas review](research/ATLAS_REVIEW.md),
[reference-refinement review](research/REFERENCE_REFINEMENT_ATLAS_REVIEW.md)
and [waveform review](research/WAVEFORM_ATLAS_REVIEW.md) remain separate records.

## Ownership, historical records and continuation

| Session | Recovery records |
| --- | --- |
| Active streaming/material continuation | [Scope](development/2026-11-15-streaming-continuation/SCOPE.md), [checkpoint](development/2026-11-15-streaming-continuation/CHECKPOINT.md) and [actual ledger](development/2026-11-15-streaming-continuation/assignments.json). Current isolated causal grid and Upper material, single coordinated build and closed sixty-worker/ten-wave records; root owns integration/publication. See the [closure handoff](STREAMING_CONTINUATION_CLOSURE.md). |
| Earlier execution continuation | [Scope](development/2026-11-15-execution-continuation/SCOPE.md), [checkpoint](development/2026-11-15-execution-continuation/CHECKPOINT.md) and [actual ledger](development/2026-11-15-execution-continuation/assignments.json). Preserve offline contact/composition results and unfinished owner-local work; no ledger closure is inferred. |
| Audio continuation | [Checkpoint](development/2026-11-15-audio-continuation/CHECKPOINT.md) owns additive sparse leakage/offline audition and remaining local work; earlier percussion captures keep their identities. |
| Playable continuation | [Checkpoint](development/2026-11-15-playable-continuation/CHECKPOINT.md) owns harmonic-source/offline and reference-rack work. Recover actual source/publication before integration. |
| Next-phase continuation | [Checkpoint](development/2026-11-15-next-phase/CHECKPOINT.md) owns ScannerLineFoh and registration/performance library/browser gates. |
| Fidelity continuation | [Checkpoint](development/2026-11-15-fidelity-continuation/CHECKPOINT.md) owns same-Hz crossover, MIDI close/retirement and visual-deck work; preserve unfinished source. |
| Completed product continuation | [Scope](development/2026-11-15-product-continuation/README.md), [checkpoint](development/2026-11-15-product-continuation/CHECKPOINT.md), [actual manifest](development/2026-11-15-product-continuation/assignments.json) and [ten-wave plan](development/2026-11-15-product-continuation/WAVES.md). Its sixty accepted results and 80b8cce hosted passes remain historical; its 1:1 objective is explicit in the batch record. |
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

The current request's sixty actual scoped deliveries are accepted in ten waves,
and the matching strict record check passes. Preserve those source-bound records
and the [closure handoff](STREAMING_CONTINUATION_CLOSURE.md) when assigning new work.
The passing strict [product-checker result](development/2026-11-15-product-continuation/reports/product-session-strict.json)
and thirteen required jobs at 80b8cce belong only to that completed older batch;
the previous execution ledger is not declared complete. Continue from the
implemented trajectory and Upper material into their admitted next gates, and
coordinate with the M6/native-close and other independent owners. Keep updating
the actual source/evidence and publishing authorized accepted work
with a fresh expected head and no force; verify the fetched commit/tree and
its required hosted results. Do not recount the completed product batch.
Historical checkers, planned assignments and a publication request do not prove
new acceptance. No project-wide license has been selected; the
[notices](../THIRD_PARTY_NOTICES.md) and [source-rights record](research/RIGHTS_AND_SOURCES.md)
retain the applicable provenance and unresolved distribution decisions.
