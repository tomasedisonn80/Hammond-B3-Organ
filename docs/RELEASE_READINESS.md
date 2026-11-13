# Release readiness and retained assessments

## Current continuation assessment

The repository now includes an optional native standalone instrument window,
keyboard/pointer playing, retained controls, audio-device lifecycle management,
replay, explicit chapel-control auditions and a relocatable nine-file component.
Published `649b12c7d1faa7601fde1019e913347c65a6634a` passed standalone 14/14
and packaging on Linux, Windows and macOS; its remaining Linux core concurrency
assertion and the later timing repair retain separate qualification scopes.
The [current status](STATUS.md), [standalone handoff](STANDALONE_HANDOFF.md) and
[platform follow-up](reviews/STANDALONE_PLATFORM_FOLLOWUP.md) supersede the
historical statements below about an absent standalone application or pending
macOS build. The VST3 surface still uses generic host controls.

The scanner graph/compiler, independent references and prepared numerical
modules now exist. Its observed G5 same-hertz failure remains an explicit
Engine-integration gate. The parallel rotary track has a nominal motion
foundation, while connected AO-28, distinct Leslie 122/147 electronics, physical
captures and end-to-end fidelity remain unresolved dependencies. See the
[scanner handoff](SCANNER_HANDOFF.md), [rotary scope](ROTARY_SCOPE.md),
[calibration scope](CALIBRATION_SCOPE.md) and [next steps](NEXT_STEPS.md).

A keyboard-operable SDL canvas has no qualified native accessibility tree.
Dummy-driver tests do not establish physical devices, latency, desktop capture,
MIDI controllers, DAW workflows, signing or clean-machine distribution. Source,
asset and branding rights retain their separate recorded review requirements.
No release version, production-readiness or physical-fidelity claim is created
by these engineering checkpoints.

## Preserved pedal session assessment at `0ad7240`

The following assessment and tables are retained as historical evidence for
that named source. Its statements about what existed or was next apply to the
pedal session at that checkpoint, not the later standalone/scanner/rotary work.

**The repository supports bounded nominal offline evaluation and native plugin
development. It is not a calibrated B-3/Leslie reproduction or a production-ready
release.** Both manuals and all 25 pedals render through one shared source bank;
the optional headless `HammondB3.vst3` is an actual implemented instrument with
executed native-interface tests. The next model implementation is the reviewed
scanner graph and strict compiler, followed by an independent numerical oracle.
[Milestone matrix](ACCEPTANCE_MATRIX.md), [project plan](PLAN.md).

Assessment date: **2026-11-13**, assignment 58 with subsequent root platform
integration. The latest published fixture repair is
`0ad7240a88803de9d97bc265a8fd2b6e5d5d7e2b`, tree
`41c0b421643d4076c65ecbac8a750b4aae4d5806`; the
[final platform audit](reviews/PEDAL_FINAL_PLATFORM.md) records actual results
and the [repair report](reviews/PEDAL_PLATFORM_FIXTURE_REPAIR.md) retains the
failed earlier run and bounded corrections. Older W8 execution remains scoped
to `d601eb1` and its qualified source `5370890e32045a556cb61a88cdb1f04fb5a18f7e`.
[STATUS.md](STATUS.md), [NEXT_STEPS.md](NEXT_STEPS.md), the
[current handoff](PEDAL_HANDOFF.md) and [development log](DEVELOPMENT_LOG.md)
record final acceptance/publication. This assessment does not create a release,
assign a version/tag or authorize a broader distribution.

### What can be used now

A developer can build the SDK-free C++20 core, render and inspect nominal musical
fixtures, compare manual/pedal source sharing, inspect contact/ownership history,
and reproduce retained audio with documented inputs. The optional pinned-SDK
build permits actual VST3 factory/controller/processor, automation, state and
bundle-relocation experiments. The three-second
[pedal phrase](../examples/demos/pedal-phrase-v1/README.md) supplies actual
synthetic audio and independently checked evidence. Generic host parameter
controls are the present interaction surface; there is no custom editor or
standalone audio-device application.
[Clean setup review](reviews/PEDAL_CLEAN_SETUP_FINAL.md),
[native protocol review](reviews/PEDAL_NATIVE_PROTOCOL_FINAL.md).

| Surface | Supported present contract | Practical boundary |
| --- | --- | --- |
| Engine/model | 91 continuously running shared nominal sine sources; two 61-key manuals, four retained A/B drawbar banks, nominal manual travel/percussion and 25 pedals. | Nominal 12-TET/normalized source profile; no measured pickup/gear/phase/loading model, scanner, AO-28 or Leslie stage. [Engine](ENGINE_API.md), [pedals](PEDAL_ENGINE.md). |
| Pedal sound | 200 independent ideal contact positions: 195 connected, five null. Four documentary buses feed `nominal-static-pedal-mixture-v1` and linear positions 0–8. | Labels remain **Pedal Mixture 1/2**. The chosen matrix is an explicit surrogate, not calibrated 16′/8′ reactor response. [Pedal voice](PEDAL_VOICE.md). |
| Offline audio | Stereo PCM16 WAV at 44,100, 48,000 or 96,000 Hz; identical dry channels. | The pedal musical catalog's own executed stationary/phrase gate is at 48 kHz; separate Engine/renderer suites cover the other admitted rates. [Audio acceptance](PEDAL_AUDIO_ACCEPTANCE.md), [render verification](RENDER_VERIFICATION.md). |
| Native audio | Optional `HammondB3.vst3`; no audio input, one stereo float32 dry output; 44.1/48/96 kHz only. Maximum prepared block 1–65,536 frames; callbacks may have zero frames. | Float64 and other rates reject by contract. The SDK base latency is zero; the declared infinite tail conservatively accounts for held voices and is not an implemented reverb/cabinet. [Processor](VST3_PROCESSOR.md). |
| Native musical input | Three event buses: Upper 0, Lower 1 and Pedals 2; 16 channels each. Manuals accept MIDI 36–96, pedals MIDI 36–60 mapped to PedalId 1–25 and typed pedal origin 0. | This is a named software mapping. Positive velocity does not scale sustained gain; finite tuning is admitted but ignored/counted. No physical MIDI device has been qualified. [Processor](VST3_PROCESSOR.md). |
| Permanent controls | 45 exported controls: 36 manual drawbars, expression, two bank selectors, four percussion switches and two pedal mixture positions. | The older 43 complete records and factory UUIDs remain unchanged; new pedal IDs are `0x4000` and `0x4001`. Drawbars are discrete 0–8; expression is the existing linear surrogate. No physical preset, continuous drawbar or scanner mode control is claimed. [Registry](PARAMETERS.md). |
| Defaults and playability | Manual drawbars and pedal mixtures start muted; both selected manual banks default to B, expression to 1 and percussion Off. | Supply a registration to produce sound. Routing-only Cancel retains bank contents; its route bits are saved state outside the 45-scalar inventory. [Registry](PARAMETERS.md), [control state](CONTROL_STATE_FORMAT.md). |
| Automation and saved state | Sample-linear normalized curves, previous-sample anchor, offset-N carry, whole-callback candidate transaction; four pending UI state snapshots. Writer `B3CONTROLS3`, readers 1/2/3 with older states explicitly muting pedals. | Musical controls and route bits are saved. Held owners, phases, contact/percussion history and frame time are not serialized. UI state calls are serialized; rate/setup/activation changes use the declared stopped lifecycle. [Timeline](HOST_TIMELINE.md), [state exchange](STATE_EXCHANGE.md). |
| Offline local package | `OfflineTools`: five native executables, two standard-library Python plot scripts, compiled profile, three catalogs and twelve scores; exactly 23 files. | No audio backend, Python interpreter, compiler/OS runtimes, research PDF or core development headers/archive is installed. [Exact install layout](OFFLINE_INSTALL.md). |
| Native local package | Explicit-prefix `NativeVST3` staging and relocation; actual development bundles and inventories retained by CI. | No automatic plugin-directory installation, signed installer or promised clean-machine runtime support. [Native install](VST3_LOCAL_INSTALL.md), [native CI](VST3_CI.md). |

Use a coherent source snapshot and fresh build directories. The default build
needs C++20, CMake/CTest 3.21+ and Python 3.10+; it downloads no SDK. Native builds
need CMake 3.25+ and the exact externally acquired SDK 3.8.1 build 84 lock.
`BUILD_TESTING` and `HAMMOND_BUILD_VST3` are real options; there is no
`HAMMOND_BUILD_TOOLS` switch. Use the complete commands in the
[current handoff](PEDAL_HANDOFF.md), [build guide](BUILD.md),
[native build](VST3_BUILD.md) and [offline install](OFFLINE_INSTALL.md).
Required filtered CTest invocations must include `--no-tests=error` so a missing
registry cannot appear successful. [Independent setup evidence](reviews/PEDAL_CLEAN_SETUP_FINAL.md).

### Qualified engineering and current platform boundary

| Named evidence | Result | What remains separate |
| --- | --- | --- |
| [W8 local coherent integration](reviews/PEDAL_WAVE8_INTEGRATION.md) | 71/71 ordinary and 8/8 native suites passed with zero failed/disabled/skipped cases. | Later source/tool changes and actual hosted execution. |
| [W8 hosted core](reviews/PEDAL_HOSTED_WAVE8_FINAL.md) | Linux, Windows and Linux ASan/UBSan/leaks each passed 71 suites; 548 Python methods across 33 suites per completed job. | The initial macOS job acquired no runner and executed zero steps; its targeted retry later passed 71/71 and 548 methods. Later-source execution remains separate. |
| [W8 hosted native](reviews/PEDAL_HOSTED_WAVE8_FINAL.md) | Linux 8/8 and Windows 7/7, actual controller/loaded-module/relocation gates and uploaded bundle inventories. Both ABI gates compared 229,725 frames with zero maximum error. | The initial macOS job executed zero steps; its retry exposed the unsupported thread helper in a test. Later repaired native execution is recorded separately. The extra Linux suite is its Linux-only allocation audit, not a skipped Windows test. |
| [Final platform audit](reviews/PEDAL_FINAL_PLATFORM.md) | At `0ad7240`, all four core jobs passed 71/71 suites and 549 Python methods each; native Linux 8/8, macOS 7/7 and Windows 7/7. All ten artifact ZIPs and 16 native payload files were verified, with zero failed/disabled/skipped tests. The actual two-junction Windows regression and native cleanup probes passed. | The earlier `feefe83` macOS/Windows core fixture failures remain retained. These are finite platform/packaging results, not DAW/device or signed release qualification. |
| [Hosted artifact runtime](reviews/PEDAL_HOSTED_RUNTIME_FINAL.md) | The downloaded W8 Linux module passed actual ABI/behavior/dense automation with coherent independent hosts and verified loader bindings. | No local substitute, rebuild, DAW/device or physical-fidelity claim. |
| [Actual SDK validator](reviews/PEDAL_HOSTED_WAVE8_FINAL.md) | 47 passed, zero failed, exit 0. | Logs retain 16 teardown diagnostics, nine unsupported-rate `ERROR` messages and 15 float64 information messages. This is not a warning-free validator or DAW certificate. |
| [Core allocation](PEDAL_REALTIME.md), [native allocation](VST3_REALTIME.md), [native concurrency](VST3_CONCURRENCY.md) | 180 core and 133 actual Linux native measured regions saw no replaceable global C++ allocation/deallocation. Finite actual-module concurrent-state workloads passed Release and fully instrumented TSAN. | Direct C/custom/system allocations, every lock/syscall, other platforms' interposition, all interleavings and device deadlines. |
| [Fresh setup/relocation](reviews/PEDAL_CLEAN_SETUP_FINAL.md) | Unicode/space-path source and build, five native tools/two plotters and actual moved Linux module worked with original source/build paths unavailable. | No clean-OS, actual DAW, hardware controller or device qualification follows. |
| [Later inventory repair](reviews/PEDAL_TOOLS_EVIDENCE_FINAL.md) | Actual Windows reparse/junction acceptance defect corrected; 20 repaired methods passed locally, with three old-tool synthetic negative-control failures. | W8 executed the earlier 19-method suite. The later fixture correction and actual two-junction Windows execution are tracked against their own source in the final platform audit. |

The original macOS acquisition failures were infrastructure nonexecution. The
subsequent native compilation and inventory fixture failures were actual project
test failures; each has its own concrete repair and observed follow-up. A later
retry or publication names its source, run, attempt, executed suites and payloads.
The original failed/repaired Windows and validator records remain part of the
history, and a diagnostic marker alone cannot override a failed test result.

### Release gates and their next actions

The product target remains one inspectable B-3/AO-28/Leslie-122 model plus VST3,
standalone operation and accessible dimensional/flat interfaces. A prototype
build can be useful while that work is unfinished. The [acceptance matrix](ACCEPTANCE_MATRIX.md)
classifies each M0–M9 milestone; these are the practical exits needed before a
broader product or fidelity claim.

| Gate | Present limitation | Next concrete evidence/action |
| --- | --- | --- |
| Source/reference and physical M2 | Documentary routes and nominal source profile exist; specimen/revision, gearing, spectra, phase and loading are not measured. | Record the actual organ/generator/AO-28/cabinet identity, condition, applicable drawings and permissions. Admit calibrated captures and a separately identified profile under [capture protocol](CAPTURE_PROTOCOL.md). |
| Remaining physical/behavioral M3 | Current A/B/Cancel, discrete positions, nominal contact/percussion, static pedal matrix and scalar expression do not implement the full console network. | Independently transcribe all 162 fixed-preset digits; model eleven-bit latches/overlap with loaded routing, continuous drawbar conductance, switching bandwidth, loaded expression and the persistent four-bus/two-output pedal reactor. Retain the nominal references and independent measurements. [Concrete M3 gate](M3_REMAINING_AND_SCANNER_GATE.md). |
| M4 numerical and source admission | Candidate scanner graph, diagram review and rational DC results exist; no compiler, independent AC/transient oracle or prepared DSP exists. Primary-circuit applicability and the 16-position traversal remain open. | Execute the first task below, then independent signed/load-sensitive AC/transient/energy/constraint tests before runtime. Close the original source/rotor erratum and physical response gates separately. |
| M5–M7 signal chain | No connected AO-28, Leslie amplifier/crossover/driver or rotor/acoustic model is implemented. | Establish connected revision-specific ports/loading first; qualify linear models, then nonlinear/convergence/alias behavior and independent physical data. Keep 122 and 147 profiles separate; validate the dry organ before cabinet fitting. [Plan](PLAN.md). |
| M8 calibration/listening | Synthetic evidence tools exist; no admitted hardware corpus, fitted/held-out validation or physical listening result. | Acquire rights-qualified raw masters with clock/calibration/load/lineage, freeze whole-group splits and acceptance with uncertainty, then retain fit and held-out results including failures. [Capture validation](CAPTURE_VALIDATION.md). |
| Exact-source platforms | W8 Windows/Linux executed; current macOS retries and later Windows reparse repair have separate pending scope. | Inspect actual final-checkpoint logs and artifacts, including real junction rejection on Windows and any acquired macOS runner. Record unexecuted platforms explicitly; do not combine unrelated revisions into a full matrix pass. [Status](STATUS.md). |
| Actual DAWs and device operation | SDK harnesses and validator operate the module; no actual DAW project or audio device gate is retained. | Select and record host/OS/version combinations; test discovery, three-bus routing, 45 descriptors/automation, project save/reopen and state 1/2/3 behavior, deactivate/restart/rate changes and bounded failures. Add device callback deadline/underrun/latency evidence and standalone device operation. [Host contract](HOST_INTEGRATION.md). |
| User interface and accessibility | Generic host parameter controls only; no custom dimensional/flat editor, keyboard/focus/screen-reader or scaled layout gate. | Select actual UI dependencies/assets with terms, implement the specified interaction and accessible alternate presentation, then execute keyboard, focus, assistive-technology, scaling and host-resize coverage. [Plan](PLAN.md). |
| Release packaging and runtimes | Current local components/development archives are unsigned staging layouts; compiler/OS runtimes and Python are unbundled. | Define intended OS/architecture/minimum-runtime targets, inspect actual linked imports and all distributed runtime files, include notices, then verify clean-target install/relocation/uninstall/update. Qualify signing/notarization and resulting payloads for the selected channels. [Dependency inventory](DEPENDENCIES_AND_RIGHTS.md). |
| Project, research and asset rights | No project-wide `LICENSE` was present in the reviewed source; supplied atlas/embedded material and future recordings/assets have unresolved permitted uses. | Obtain and record the owner's project-license selection and applicable author/asset/recording permissions for the intended source/binary distribution. Keep actual SDK license inventory separate; no inventory or test result grants these rights. [Rights/source record](research/RIGHTS_AND_SOURCES.md). |
| Windows package branding | Actual `PlugIn.ico` and `desktop.ini` use the pinned SDK's default VST logo asset. Its bytes and separate upstream logo conditions are known; intended branding treatment is unresolved. | Choose and document the intended asset/branding treatment. For an original owned icon, set `SMTG_PACKAGE_ICON_PATH` to an existing ICO before `smtg_add_vst3plugin`, then requalify actual Windows payload/inventory. Empty or missing paths fall back to the SDK logo and do not omit it. [Artifact/rights review](reviews/PEDAL_DEPENDENCY_ARTIFACT_FINAL.md). |

### Actual dependency and notice boundary

The selected external SDK root and four required submodules have retained
revision-specific MIT texts; selected embedded `json.h` has its separate
Unlicense record. This does not assign the same terms to every omitted SDK
sample, to the project itself, or to research/branding assets. The actual native
module contains selected SDK code, while its bundle does not contain the SDK
source tree, built validator, Python interpreter or atlas. The native component
includes the selected SDK license and project notices.
[Dependencies and rights](DEPENDENCIES_AND_RIGHTS.md).

`OfflineTools` currently stages neither `THIRD_PARTY_NOTICES.md` nor the dependency
inventory. A redistribution package must add its applicable notices and review
any runtime files it actually includes. The five executables need compatible
OS/compiler runtimes; the two plot scripts need a separately installed Python
interpreter. No universal license clearance or clean-machine compatibility is
inferred from an unbundled dependency. The recorded Windows icon is 254,170 bytes,
SHA-256 `1dda09aceb9fa930a3894cce4ad57edd8fa48ce58157c97ba5f971d2d4e79821`.
Its copying is an observed packaging fact; this assessment grants no branding
permission or legal clearance. [Current inventory](DEPENDENCIES_AND_RIGHTS.md).

### First next product task: scanner graph admission

**Task:** add an explicitly reconstructed nominal scanner authoring fixture,
strict schema/compiler and independent endpoint/source-review record. Preserve
the current Engine, dry audio accumulation, parameter/state identities and native
payload. This is the first numerical-data admission step of M4, while remaining
M3 work stays open. The detailed authority is
[M3_REMAINING_AND_SCANNER_GATE.md](M3_REMAINING_AND_SCANNER_GATE.md); the
[independent final source review](reviews/PEDAL_SOURCE_PLAN_FINAL.md) supports the
atlas connectivity and DC arithmetic without claiming a primary production
circuit, AC solver or physical response pass.

### Inputs and proposed owned files

Use the unchanged atlas, especially pp. 157–159, 175 and 181–186, and the reviewed
candidate endpoint list. Proposed new paths are:

- `data/scanner/atlas-late-b3-nominal-v1.json`
- `data/scanner-line.schema.json`
- `tools/compile_scanner_line.py`
- `tests/test_scanner_line_profile.py`
- A separately owned source-review/evidence note identifying page images,
  endpoint transcription, independent comparisons and unresolved applicability.

Use proposed identity `atlas-late-b3-nominal-line-v1` and explicit documentary
reconstruction provenance. The absent original `025-scanner-network.json`,
`scanner_ac_reference.py` and response companion are not recovered by creating
new files with comparable functions. The JSON/compiler contract must name its
units, signed endpoints, output references, admitted bounds and unknown physical
quantities before a runtime artifact is accepted.

### Acceptance for that first commit

1. **Literal connected graph:** retain ground `g`, `p0..p18`, return `r`, and
   `d1..d6`: 27 named nodes, 18 inductors, 18 capacitors and 14 resistors.
   Ideal drive and return switch are separate boundaries. Each early divider
   attaches **before** its inductor. Export exactly 19 ground-referenced taps;
   do not reinterpret them as 19 delay sections or independent memories.
2. **Values and assumptions:** admit the reviewed positive nominal R/L/C values,
   convert units once, retain printed values and source locators, and represent
   the vibrato return short as a constraint/contraction. Ideal coils/drive and
   negligible scanner loading are named model approximations. Actual winding
   resistance, mutual/stray coupling, drive impedance and receiver loading remain
   unknown; they cannot acquire measured-looking zeros or an invented normalized
   amplitude-to-volts scale.
3. **Independent source comparison:** check all endpoints, output references,
   values and return state against the rendered atlas and a separately identified
   primary circuit/paper when available. Preserve the exact source edition and
   unresolved specimen applicability. The completed atlas/DC review is useful
   evidence, but does not supply the missing primary comparison. Keep admission
   provisional where that source gate remains unresolved.
4. **Strict deterministic admission:** reject duplicate IDs/keys, dangling or
   missing references, unknown fields, nonfinite/nonpositive values, wrong unit
   prefixes/counts, after-inductor divider mutations, a tap referenced to `r`,
   and a missing/wrong return switch. Bound bytes, strings, nodes and components;
   failed admission preserves the previous destination. Keep independently
   retained edge/output expectations rather than testing only arrays generated
   by the production compiler.
5. **Compatibility and handoff:** execute the meaningful focused compiler and
   source-contract gates at an identified revision; retain exact input/output
   hashes, commands and failures. Verify the original profile/PDF/fixtures,
   45 parameter records, state migrations and Engine/native compiled inputs
   are unchanged. Update status, next steps, acceptance and the assigned record,
   then commit/push through the integrator's normal expected-head workflow.
   Passing this task establishes graph admission only.

### Follow-on tasks and exit order

| Order | Implemented result required before proceeding | Acceptance that controls the next step |
| --- | --- | --- |
| 1. Graph admission | The fixture/schema/compiler and independent source record above. | Exact named graph, provenance, strict rejection and preserved old inputs; unresolved primary applicability remains visible. |
| 2. Independent offline oracle | Readable independently stamped modified-nodal AC reference, both return states and all 19 signed outputs; converged transient/physical-state reference. | Exact-rational DC answers, finite-frequency endpoint mutations, input-current/loading sensitivity, scaling/conditioning and residuals. Freeze 20 Hz–20 kHz plus resonance/null refinement and proposed error budgets before grading runtime. Do not share stamping/factorization/tap reconstruction with it. |
| 3. Prepared line runtime | Independently implemented bounded solver with prepared operators and physical capacitor/inductor state. | AC parity with bilinear warp-matched and same-physical-Hz comparisons, converged transient/nonzero-state/energy checks, supported rates, partitions and stopped-rate state conversion. Singular descriptor constraints are handled explicitly. |
| 4. Rotor and modes | One continuing rotor phase, 19 outputs/9 selected terminals/16 mechanical positions, three depth maps and V1–V3/C1–C3 semantics. | Resolve or explicitly label the page-166 inferred traversal; independently test centers/intervals/wrap, signed common return exactly once, sidebands and higher-rate convergence. No arbitrary 50:50 chorus replacement. |
| 5. Opt-in Engine/native integration | Defined U/L/P/Q boundaries, one shared scanner, continuous physical history and preserved existing dry branch when disabled. | Legacy dry audio, phase/history, controls/state migration, whole-callback rollback including precharged states, automation/carry and newly enabled allocation/concurrency/native gates. Physical matching still needs admitted captures. |

The already checked DC input resistances are approximately 9,775.932618884532 Ω
in vibrato and 31,775.932618884533 Ω in chorus; the common-return ratio is
0.6923478931008726 in chorus. These are mathematical properties of the ideal
candidate graph. The independent reviewer deliberately moved dividers after
inductors and obtained the **same DC answers**, because inductors short at DC.
Finite-frequency source/connectivity checks are therefore essential before
runtime confidence. [Independent rational solve](reviews/PEDAL_SOURCE_PLAN_FINAL.md).

No scanner controls are appended during graph/oracle work. Later controls and
saved-state migrations must preserve old identity meanings and default legacy
states to the prior dry path. Physical preset, drawbar, switching, expression
and pedal-network work can proceed as separate dependency-ready tasks with the
same evidence discipline. Future agents must use [AGENTS.md](../AGENTS.md) and
the current handoff, preserve historical failures and source identities, record
what was actually executed, and leave the next actionable gate explicit.
