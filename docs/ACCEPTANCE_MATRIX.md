# Milestone acceptance and evidence matrix

**Current engineering position: a nominal dry organ with two manuals, 25 pedals,
offline evidence tools and an actual headless VST3 prototype.** Nominal M1/M2
behavior and a substantial M3 subset have executed software evidence. Full M3,
scanner/electronics/acoustics, physical calibration and the production product
remain open. The [M0–M9 plan](PLAN.md) remains the milestone authority; the
[release assessment](RELEASE_READINESS.md) states the usable prototype surface
and exact next product task.

This 2026-11-13 assessment combines assignment 58's milestone review with
root's subsequent platform integration. The latest published test-fixture repair
is `0ad7240a88803de9d97bc265a8fd2b6e5d5d7e2b`, tree
`41c0b421643d4076c65ecbac8a750b4aae4d5806`. Its source and actual results belong
to the [final platform audit](reviews/PEDAL_FINAL_PLATFORM.md). Production model
inputs retain their W8 identity; the [repair records](reviews/PEDAL_PLATFORM_FIXTURE_REPAIR.md)
identify later inventory and test-harness changes. [STATUS.md](STATUS.md), the
[current handoff](PEDAL_HANDOFF.md) and [session ledger](development/2026-11-13-pedals/README.md)
own final record/publication outcomes. Historical console results remain below.

The source gates are in the [atlas, pp. 445–450](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=445)
and [pp. 481–486](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=481).
The [independent source/plan review](reviews/PEDAL_SOURCE_PLAN_FINAL.md) verifies
unchanged source identities, all six fresh reader records covering pages 1–500,
and the candidate scanner's exact-rational DC answers. It supplies neither an
acquired instrument corpus nor executed scanner DSP.

## Current evidence attached to identified revisions

| Evidence | Actual observed scope | Consequence and limit |
| --- | --- | --- |
| [Wave-8 local integration](reviews/PEDAL_WAVE8_INTEGRATION.md) | Fresh coherent Release builds: 71/71 ordinary suites and 8/8 actual native suites passed, with zero failed, disabled or skipped tests. | Qualifies the named compiled/data inputs, including real offline/native relocation. Later code or changed tool inputs require their own checks. |
| [Wave-8 hosted audit](reviews/PEDAL_HOSTED_WAVE8_FINAL.md) | At `d601eb1`, Linux Release, Windows Release and Linux ASan/UBSan/leaks each passed 71 suites and 548 Python methods. Native Linux passed 8 suites; Windows passed 7. Complete logs and all seven downloaded artifact ZIPs were checked. | Actual platform and artifact evidence. Both initial macOS jobs failed runner acquisition with zero steps; this was not a complete four-job core/three-platform native matrix pass. The actual core retry later passed 71/71; native macOS failed test compilation before the separately recorded thread-helper repair. |
| [Final platform audit](reviews/PEDAL_FINAL_PLATFORM.md) and [fixture repair](reviews/PEDAL_PLATFORM_FIXTURE_REPAIR.md) | Published `0ad7240`: all four core jobs passed 71/71 suites and 549 Python methods each; native Linux 8/8, macOS 7/7 and Windows 7/7, zero failed/disabled/skipped cases. Ten ZIPs and all 16 native payload files match retained identities. The actual two-junction Windows regression passed. | Closes these source-specific platform/test-fixture gates. Earlier `feefe83` macOS/Windows core failures and their concrete repairs remain retained; DAW/device, physical and release exits remain separate. |
| [Hosted Linux artifact execution](reviews/PEDAL_HOSTED_RUNTIME_FINAL.md) | The actual downloaded W8 module passed ABI, behavior and dense automation against coherent reference hosts; loader bindings resolve inside that artifact. | Adds finite artifact runtime evidence, not DAW/device, other-OS execution or physical calibration. |
| [Core/input review](reviews/PEDAL_CORE_INPUT_FINAL.md) and [native protocol review](reviews/PEDAL_NATIVE_PROTOCOL_FINAL.md) | Independently identified unchanged compiled inputs; 20 core/input suites and seven protocol executable gates passed in their respective reviews. Actual-module tests execute native interfaces. | No actionable production defect found in the reviewed transactions, state/automation and pedal paths. Finite executed coverage does not establish all scheduler histories or hardware behavior. |
| [Enabled core allocation](PEDAL_REALTIME.md), [native allocation](VST3_REALTIME.md) and [native concurrency](VST3_CONCURRENCY.md) | 180 core measured API regions and 133 actual Linux native regions each observed zero replaceable global C++ allocations/deallocations. Actual loaded-module UI/audio stress passed Release and a fully instrumented TSAN run. | Scoped calling-thread C++ allocation and finite concurrency evidence. Direct C/custom/system allocation, all locks/syscalls, device deadlines and concurrent profile replacement are not qualified. |
| [Tools/evidence final review](reviews/PEDAL_TOOLS_EVIDENCE_FINAL.md) | 173 methods across nine focused suites passed. A concrete Windows reparse/junction admission defect was repaired in two files; the repaired inventory suite passed 20 local Linux methods with meaningful old-tool negative controls. | W8 had the earlier 19-method inventory suite. Later hosted execution exposed alias/command/metadata defects in its test fixture; the isolated correction and exact-source Windows execution belong to the final platform audit, not W8. |
| [Fresh setup review](reviews/PEDAL_CLEAN_SETUP_FINAL.md) | All 534 archived files matched Git; fresh Unicode/space-path build, 23-file OfflineTools install and four-file Linux native install relocated successfully with original source/build paths unavailable. Twenty-five operations succeeded; three deliberate invalid operations rejected. | Reproducible local Linux setup and relocation, including actual relocated ABI execution. This is not a new full test-matrix, clean-OS or DAW qualification. |
| [Legacy review](reviews/PEDAL_LEGACY_FINAL.md), [pedal acceptance](PEDAL_AUDIO_ACCEPTANCE.md) and [retained phrase](../examples/demos/pedal-phrase-v1/README.md) | All 57 original assets and 43 older parameter records preserved. Twenty-four legacy renders retained exact WAV/PCM/common metrics at the recorded toolchain. The original three-second phrase has 144,000 actual frames, independent PCM/window checks, partition replay and schema-3 evidence. | Nominal routing/mixture and compatibility evidence. The phrase retains its original `d7b8861` source provenance; no hardware recording, physical timbre or arbitrary cross-toolchain bit identity is inferred. |
| [Dependency/artifact review](reviews/PEDAL_DEPENDENCY_ARTIFACT_FINAL.md) | Inspected pinned external SDK licenses, actual bundle bytes/imports and the copied Windows SDK-default icon. | Identifies actual package boundaries and unresolved decisions. It does not choose a project license or grant research-asset, branding or runtime redistribution clearance. |

“Passed” below names an implemented, executed **scope**, not completion of all
requirements in that milestone. A planned, unrun or infrastructure-blocked gate
is distinguished from an observed project-test failure. Ten development waves
and sixty accepted worker records do not substitute for M0–M9 product exits.

## M0–M9 gates and concrete next evidence

| Milestone | Current classification and implemented evidence | Open exit and exact next action |
| --- | --- | --- |
| **M0 — reference and contracts** | **Nominal contract/source-identity gate passed; physical reference lock open.** Strict [profile](PROFILE_FORMAT.md), [source manifest](research/source-manifest.json), source/evidence classes, units, unknowns and factory routing records are retained. The [source review](reviews/PEDAL_SOURCE_PLAN_FINAL.md) confirms the original PDF and source identities and all fresh atlas reader ranges. | Identify one organ/generator/AO-28/cabinet specimen, revision, condition and modifications; establish applicable drawings and permitted uses in the [capture protocol](CAPTURE_PROTOCOL.md). Resolve intended distribution rights under the [dependency inventory](DEPENDENCIES_AND_RIGHTS.md). Planned capture metadata and documentary agreement cannot close this exit. |
| **M1 — testable skeleton** | **Scoped offline/native engineering gates passed; full host/device lifecycle open.** Prepared [Engine](ENGINE_API.md), bounded input, whole-call rejection, one clock, disconnected processing and [stopped rate migration](SAMPLE_RATE_LIFECYCLE.md) are implemented. [Combined input](PERFORMANCE_INPUT.md), [HostTimeline](HOST_TIMELINE.md), [concurrent control exchange](STATE_EXCHANGE.md) and the [native processor](VST3_PROCESSOR.md) have separate executed gates. | Retain the declared one-audio-owner/serialized-UI lifecycle. Design and qualify concurrent profile publication/retirement only when required; current control snapshots are not profile replacement. Execute actual host/device lifecycle and deadline/underrun coverage before making that claim. |
| **M2 — shared generator** | **Nominal shared-source and documentary routing gates passed; physical generator open.** Ninety-one continuously advancing sources feed both manuals and the [25-pedal consumer](PEDAL_ENGINE.md). [Manual routing acceptance](FACTORY_RUNTIME_ACCEPTANCE.md) covers 1,098 manual branches; [pedal review](reviews/PEDAL_CORE_INPUT_FINAL.md) covers all 200 positions, 195 connected/five null and seven repeated-source pairs. [Numerical bounds](NUMERICAL_BOUNDS.md) and source-history/rate tests retain declared limits. | Acquire selected production gearing, mechanical/tooth phases, pickup spectra/levels/loading and leakage evidence. Admit a new measured profile with uncertainty and specimen identity; preserve the existing 12-TET sine/normalized nominal profile and source-clock compatibility. |
| **M3 — console and pedals** | **Substantial nominal engineering subset passed; full M3 open.** [Console dynamics](CONSOLE_DYNAMICS.md) provides independent manual contacts and shared upper-B percussion. Four retained A/B banks, routing-only Cancel and partial targets coexist with eight ideal contacts per pedal and the named [two-mixture nominal voice](PEDAL_VOICE.md). [45 controls](PARAMETERS.md), separate manual/pedal owners, the combined transaction and [B3CONTROLS3 with v1/v2 readers](CONTROL_STATE_FORMAT.md) are implemented. | Follow the [remaining M3 gate](M3_REMAINING_AND_SCANNER_GATE.md): independently admit the 162 fixed-preset digits, model physical preset latches/overlap and loaded routes, continuous drawbar travel/conductance, finite switching bandwidth, loaded expression and the four-input/two-output pedal reactor network. Keep each nominal reference and its identity; acquire independent physical/circuit evidence before calibrating or relabeling pedal mixtures as measured footage responses. |
| **M4 — scanner** | **Source/contract review passed; graph/compiler, AC oracle and runtime implementation remain open.** The [concrete gate](M3_REMAINING_AND_SCANNER_GATE.md) specifies 50 candidate passive elements, 27 nodes, 19 signed outputs and mode/routing/history requirements. A [separate review](reviews/PEDAL_SOURCE_PLAN_FINAL.md) read the actual diagrams and independently solved exact-rational DC cases. No scanner AC/transient/runtime suite has executed. | **First task:** implement the named graph, strict schema/compiler and independent endpoint/source comparison in [release readiness](RELEASE_READINESS.md#first-next-product-task-scanner-graph-admission). Then build the independent finite-frequency AC/transient oracle before prepared runtime integration. Keep the 15-entry/16-position traversal erratum, loading, depth maps, signed common return and physical captures as explicit gates. DC agreement alone cannot detect after-inductor divider misattachment. |
| **M5 — organ electronics** | **Engineering not implemented; acceptance not run.** Current audio is normalized dry mixing with a scalar expression surrogate. There is no connected AO-28, valve/transformer model, oversampling/alias qualification or calibrated G-G output. [Plan](PLAN.md), [remaining boundary contract](M3_REMAINING_AND_SCANNER_GATE.md). | Select revision-specific connected topology and source/load/feedback boundaries before component solving. Retain independent operating-point, loaded AC/transient, convergence and alias comparisons. Resolve device/transformer values and acquire calibrated dry G-G captures before fitting cabinet effects. |
| **M6 — Leslie electronics** | **Engineering not implemented; acceptance not run.** No connected Leslie amplifier, crossover or driver-load stage is present. [Plan](PLAN.md). | Lock the selected **122** revision, transformer/crossover and driver impedances; keep **147** as a separate profile. Implement signed differential ports with independent loaded AC/polarity, nonlinear convergence/stability and physical electrical evidence. An unloaded component list cannot establish this exit. |
| **M7 — rotary acoustics** | **Engineering not implemented; acceptance not run.** No horn/drum dynamics, moving-path propagation, directivity, microphone or room DSP is present. Native/offline left and right channels currently contain the same dry signal. [Plan](PLAN.md). | Specify separate horn/drum histories and causal path/interpolation/geometry, then execute transitions, tails, stereo/mono, supported-rate and convergence gates. Acquire calibrated rotor trajectories, stationary-angle/driver responses and microphone/room records before acoustic matching. |
| **M8 — calibration and listening** | **Metadata/byte-integrity and synthetic measurement tooling passed; physical calibration not run.** [Capture validation](CAPTURE_VALIDATION.md), [render verification](RENDER_VERIFICATION.md), [PCM analysis](AUDIO_MEASUREMENTS.md) and pedal fixtures check declared files and synthetic signals. | Admit rights-qualified specimen captures with clock, calibration, load, lineage and duplicate checks. Freeze whole-group fit/holdout splits, uncertainty and thresholds before fitting; retain unsuccessful/inconclusive fits and independent listening evaluations. No supplied companion capture corpus or measured reference response is present. |
| **M9 — product and release** | **Offline tools and native prototype gates passed in their named environments; playable/releasable product open.** The [23-file OfflineTools component](OFFLINE_INSTALL.md) contains five native tools and two plotters. The actual [headless VST3](VST3_PROCESSOR.md) exports 45 controls, three event buses and float32 dry stereo at 44.1/48/96 kHz; state/automation/native staging have executed gates. | Finish exact-source platform qualification, then actual DAW discovery/bus routing/project save/reopen/state migrations and device scheduling. Implement standalone device operation and accessible dimensional/flat UI with real accessibility/input checks. Resolve runtime packaging, project/research rights and Windows icon treatment; qualify installers/signing/notarization/update behavior for selected platforms. The detailed [release gates](RELEASE_READINESS.md#release-gates-and-their-next-actions) remain separate from prototype tests. |

## What the strongest checks establish

**Routing and sources.** Independent factory CSVs and signed basis cases can
expose routing/branch mistakes. Tests that reuse the existing `TonewheelBank`
are not independent physical oscillator implementations. The nominal generator,
contact/percussion timings, pedal matrix and expression law remain unmeasured.
Twenty-five working pedals do not close the physical pedal reactor gate.
[Pedal acceptance](PEDAL_AUDIO_ACCEPTANCE.md) and the
[legacy audit](reviews/PEDAL_LEGACY_FINAL.md) retain their exact oracle boundaries.

**Processing, state and concurrency.** The current native adapter exists and
its actual module was loaded. Scoped allocation and fully instrumented TSAN
results qualify their executed boundaries. They do not prove every allocator,
interleaving or audio deadline. Saved controls exclude held-note owners, source
phase, contact/percussion history and the frame clock. The combined facade calls
Engine once; HostTimeline independently uses candidate state and bounded slices.
Calling both for one interval would advance time twice.
[Core review](reviews/PEDAL_CORE_INPUT_FINAL.md),
[native review](reviews/PEDAL_NATIVE_PROTOCOL_FINAL.md).

**Validator and artifacts.** The actual SDK validator reported 47 passed,
zero failed and exit 0 while retaining 16 teardown diagnostics, nine
unsupported-rate `ERROR` messages and 15 float64 informational messages. Its
summary is not warning-free certification. A hash/inventory records bytes and
caller-declared provenance; it is not a signature, source-to-binary attestation,
DAW load or legal clearance. [Hosted audit](reviews/PEDAL_HOSTED_WAVE8_FINAL.md),
[dependencies and rights](DEPENDENCIES_AND_RIGHTS.md).

**Source and numerical evidence.** Reading all 500 atlas pages establishes
review coverage, not physical calibration or recovery of absent companions.
The exact-rational scanner DC solve is new useful engineering evidence; it
neither executes AC/transient DSP nor resolves primary production drawings,
traversal applicability or unknown physical loading.
[Source/plan review](reviews/PEDAL_SOURCE_PLAN_FINAL.md).

## Next actionable gate and durable handoff

After the integrator publishes and qualifies the final review/repair checkpoint,
implement the first graph-admission task in [RELEASE_READINESS.md](RELEASE_READINESS.md)
and [M3_REMAINING_AND_SCANNER_GATE.md](M3_REMAINING_AND_SCANNER_GATE.md).
The order is **reviewed graph/schema/compiler → independent offline oracle →
prepared line runtime → rotor/mode acceptance → opt-in Engine/native integration**.
Physical M3 and acquisition work can proceed in parallel; none disappears when
scanner software passes.

Every future agent follows [AGENTS.md](../AGENTS.md): inspect identified source,
read current contracts and relevant PDF pages, declare owned paths and evidence,
preserve prior identities/fixtures, qualify coherent inputs, retain failures and
open gates, and leave the next action explicit. The integrator updates shared
status/log/handoff and commits/pushes authorized work with an expected-head guard
and observed remote verification. The [pedal-session checker](PEDAL_SESSION_CHECKS.md)
counts this session only; require its sixty-complete gate only after sixty actual
accepted assignments. Earlier completed sessions cannot contribute new credit.

## Historical console and original-session evidence

The following table is retained from the previous matrix. Its named results are
historical evidence for the preceding console continuation, including its then
16-file payload and 43-control scope. They are not the current pedal/native
capability or latest-source qualification. Its separate ledgers and failures
remain intact.

| Evidence | Observed scope | What it establishes |
| --- | --- | --- |
| Final qualified code, `7469ebf759ced820cc34fc9012beff6f772e4b89` | [Run 43380966473](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43380966473): all four jobs pass 46 suites (24 C++ and 22 Python), with 372 Python methods and zero failed/disabled/skipped tests. The [final platform audit](reviews/FINAL_CONTINUATION_PLATFORM.md) verifies complete archives, actual instrumentation and the retained earlier CRLF failure. | The completed nominal software scope and its two final repairs on the named platforms. Native host/device, physical fidelity and full M3 remain open. |
| Published qualification checkpoint, `2046b9388f6aab1122e37646b2f20199b5c6079f` | The integrator observed all 45 local Release suites pass in 12.91 seconds and all four jobs in [run 43376892064](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43376892064) report 45 suites passed. The local frozen tree and Markdown-only publication differences are retained in the [handoff](CONTINUATION_HANDOFF.md). | Revision-specific offline engineering evidence, including enabled allocation checks, the 16-file install and explicit console/owned-input benchmark cases. Assignment 52 did not independently download those job archives; the later final platform audit verified them separately. |
| Independently audited prior checkpoint, `9a5c99a862daf26a2bab9b05613c98803727a3e7` | The [platform review](reviews/CONTINUATION_PLATFORM_REVIEW.md) checked all four complete job archives: 43 suites, 352 Python methods, zero failed/disabled/skipped tests per job. Linux/macOS/Windows Release and Linux ASan/UBSan/leak instrumentation were inspected. | Published partial-key, ownership, lifecycle, trace and plot behavior on the actual named runners. Later changes require their own checks. |
| Scoped runtime review | [Runtime boundary review](reviews/RUNTIME_BOUNDARY_REVIEW.md): coherent frozen-source inspection and six focused Release suites; no actionable defect found. | Admission, atomic ownership, event timing, partial-key history, rate changes and parameter conversion within the reviewed scope. |
| Independent legacy comparison | [Legacy audio review](reviews/CONTINUATION_LEGACY_AUDIO.md): 11 exact WAV/PCM comparisons against a fresh pre-continuation build, 11 default-versus-explicit ideal/Off comparisons and six additional partition comparisons. All 15 old JSON metric fields agree after removing the three schema-2 additions. | Same-toolchain compatibility of the retained nominal model and selected cases; not cross-toolchain bit identity or unchanged metadata schema. |
| New retained example | [Two-second console demo](../examples/rendered/nominal-console-v2/README.md): actual 96,000-frame audio, untouched schema-2 bundle, independent byte/PCM checks and matching block-64/block-127 WAVs. Its 120 ms partial trace/plot has a different schedule and registration. | A reproducible synthetic example. Its recorded source is `9a5c99a`; publishing the later demonstration does not change that provenance or establish hardware fidelity. |
| Complete source review and factory maps | [Atlas review](research/ATLAS_REVIEW.md), the continuation's separate six-range review and [factory comparison](FACTORY_REFERENCE.md). All 549 manual assignments and 200 pedal positions are corroborated by two independent factory-image readings. | Documentary coverage and routing agreement. Absent companion code, physical captures, production gearing and instrument calibration remain absent. |

The [original ledger](development/AGENT_LEDGER.md), [original acceptance note](development/agent-notes/49-acceptance-matrix.md),
[original CI qualification](CI_QUALIFICATION.md) and
[console CI repair](reviews/CONSOLE_CI_REPAIR.md) retain earlier snapshots and
failures. A later repair does not erase a failed run. Original assignment IDs
01-60 are separate from the continuation's new IDs; planned rows are not
completed participation.
