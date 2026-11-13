# Milestone acceptance and evidence matrix

**Current integration addendum:** the coordinator has preserved continuation
commit `7a24a30`, which adds independent nominal contact/percussion components
and model metadata. At that commit, `Engine`, the renderer and `B3CONTROLS1`
remain unchanged. Published `61c6ecb` adds the exhaustive runtime gate, retained
demo and final repairs; all four jobs in run 43368537860 passed 26 suites and
274 Python methods with zero skips. The dated audit below describes its inspected `6c3dd8b`
snapshot; consult [STATUS.md](STATUS.md) and [CI qualification](CI_QUALIFICATION.md)
for later implementation and executed qualification. The independent continuation
owns the next M3 integration wave.

**Audit date: 2026-11-13. Inspected published revision:
`6c3dd8bc923a3c11f6b234425b056e135fbe9f4b`.** This checkpoint implements a useful
nominal dry engine and early retained-bank console behavior. Passing those scoped
software gates does not complete the physical instrument or the M0–M9 product
plan. The requirements below follow [PLAN.md](PLAN.md) and the preserved
[atlas](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf), pp. 445–450 and 481–486.

This is a source and claim audit. The reviewer inspected implementations, test
assertions and retained reports; this assignment executed source inventory,
identity and document-link checks, not a new DSP or hosted test run. Historical
execution results below belong to their named reports and revisions.

## Revision and evidence boundaries

The inspected production graph comprises [Profile](../src/Profile.cpp),
[TonewheelBank](../src/TonewheelBank.cpp), [Engine](../src/Engine.cpp),
[ControlState](../src/ControlState.cpp) and
[ControlStateIO](../src/ControlStateIO.cpp). The engine stores Boolean manual
keys, sums shared sources through selected-bank coefficients and applies a linear
expression multiplier. [CMake](../CMakeLists.txt) builds the core, offline renderer,
benchmark and tests; it contains no plugin, device backend or editor target.
At this revision there are no contact trajectories, percussion, pedal audio,
scanner, AO-28 or Leslie DSP, VST3 adapter, audio-device application or native UI.

The separate [console continuation ledger](development/2026-11-13-continuation/README.md)
records active M3 contact/percussion development. Its reviewed wave 01 is complete
and wave 02 is in progress. That is a different session and assignment namespace
from [this session's wave log](development/WAVE_LOG.md). **Before starting M3,
inspect the newest continuation ledger, published commits and actual code.**
This dated absence inventory must not be used to duplicate or overwrite newer
console work, nor does a planned continuation entry establish implemented audio.

The [factory runtime test](../tests/test_factory_runtime.cpp),
[host design handoff](HOST_INTEGRATION.md) and
[rights inventory](DEPENDENCIES_AND_RIGHTS.md) were also inspected as local work
awaiting integration. They are not contents qualified by an older hosted run.
The inspected runtime-test SHA-256 is
`3b1bd39d1bf52f889b9e1ba5c1b1f171e6d1863fb7303d8d41fe9cd5d233212d`.

| Evidence record | Retained identity and observed scope | Qualification limit |
| --- | --- | --- |
| Complete atlas review | [Coverage record](research/ATLAS_REVIEW.md), six original notes covering all 500 pages; source SHA-256 `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`. | Documentary coverage. Absent companion code, original acceptance reports and measurements are not recovered or executed by reading their descriptions. This audit directly reread pp. 445–450 and 481–486, not all 500 pages. |
| Earlier complete hosted baseline | Commit `9c8068c95f6843dce95f7f22d729738eef8074f6`, [run 43363048563](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43363048563): 16/16 suites in each of Linux GCC, macOS AppleClang and Windows MSVC Release, plus Linux ASan/UBSan with leak detection. | Qualifies that offline software revision and configured runners. Later additions do not inherit this pass. |
| Retained failed matrix | Commit `7c2ad2089f795b2147f5fc72cf10a4542d953a8c`, [run 43364414017](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43364414017): Linux/macOS 18/18; Windows and sanitizer 17/18 each. [CI_QUALIFICATION.md](CI_QUALIFICATION.md) retains full-log counts, zero skips, toolchains, archive IDs/hashes, failures and local repairs. | Complete matrix failed. A repository-path assertion failure and an executable-mutation test failure remain historical failures even after repair. The sanitizer failure's underlying exception was not established. |
| Inspected published checkpoint | Commit `6c3dd8bc923a3c11f6b234425b056e135fbe9f4b`; integrator reports 21/21 local suites and observed successful completion of all four jobs in hosted [run 43365901429](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43365901429). This includes the native matrix for the checker/capture repairs and offline install gate. | The integrator subsequently audited all four complete archives: 21 suites, 257 Python methods and zero test skips per job. This reviewer did not independently inspect those newly completed hosted logs. Agent 47's added test is outside this revision and inherits no hosted pass. |
| Local exhaustive runtime routing | [Agent 47 report](FACTORY_RUNTIME_ACCEPTANCE.md) and [execution note](development/agent-notes/47-factory-runtime.md): GCC 14.2 Release; `test_factory_runtime` plus `python_test_factory_reference` passed locally. 1,098 one-hot manual routes, 64 additional rate/boundary cases, six coherent cases, eight Cancel/reselection stages and two required negative probes. | Local working-tree evidence, pending publication and hosted qualification. The expected routes come from frozen CSVs; the source waveform oracle reuses `TonewheelBank`. It is independent routing evidence, not an independent source-physics implementation or pedal test. |

## M0–M9 acceptance matrix

“Passed scope” means the named tests exercised that behavior in the retained
execution record. “Open” names a requirement still missing from the milestone;
it is not a failed test unless a report records an actual failure. Unimplemented
and unrun requirements remain visible even when every registered test passes.

| Milestone and required scope | Actual implementation and inspected tests | Evidence disposition and remaining exit evidence |
| --- | --- | --- |
| **M0 — reference and contracts.** Versioned identities, evidence classes, units, variants, unknowns, rights and acquisition order. | [Nominal profile](../data/profiles/nominal-unmeasured-v1.json), [compiler](../tools/compile_profile.py), [runtime loader](../src/Profile.cpp), [profile tests](../tests/test_profile.cpp) and [compiler tests](../tests/test_compile_profile.py). The compiler checks exact model/provenance fields and all nominal rows; the tests reject missing evidence, wrong units, malformed inputs and silent profile changes. [Source manifest](research/source-manifest.json) retains the supplied PDF and absent companions. | **Nominal contract gate passed; reference lock open.** Profile remains `nominal-unmeasured-v1`, with null specimen/revision/measurement fields. The [capture protocol](CAPTURE_PROTOCOL.md) supplies a concrete acquisition queue, not completed acquisition. Close physical reference lock with actual organ/generator/AO-28/cabinet identities, condition/modifications, applicable drawings and permissions. Resolve [rights gates](DEPENDENCIES_AND_RIGHTS.md) for the intended distribution. |
| **M1 — testable skeleton.** Prepared host-independent graph, bounded events, clock, offline audio, diagnostics and failure/lifetime checks. | [Engine API](../include/hammond/Engine.h), [processing](../src/Engine.cpp), [renderer](../tools/render.cpp), [scheduler tests](../tests/test_engine.cpp), [renderer tests](../tests/test_render.py), [robustness tests](../tests/test_core_robustness.cpp) and [allocation test](../tests/test_realtime.cpp). Assertions inspect exact ties/offsets, zero-frame consumption, atomic rejection, profile ownership, clock overflow and same-build audio/state equality across partitions at all three rates. | **Scoped offline engineering gate passed.** The renderer produces actual stereo PCM16, preserves existing outputs and subdivides dense scores. [REALTIME.md](REALTIME.md) retains 96 observed callbacks with zero C++ allocation/deallocation calls, within its stated interception scope. [Render evidence](RENDER_EVIDENCE.md) and [independent verification](RENDER_VERIFICATION.md) retain identities and actual metrics. Complete host curves, multi-producer note ownership, concurrent publication/retirement and actual device deadlines are not implemented or qualified; they require adapter-specific gates. |
| **M2 — shared generator.** 91 continuous sources, distinct identity domains, complete maps and coherent phase-preserving reuse. | [TonewheelBank](../src/TonewheelBank.cpp), [Engine coefficient routing](../src/Engine.cpp), [source tests](../tests/test_tonewheel.cpp), [numerical tests](../tests/test_numerics.cpp), [factory comparison tests](../tests/test_factory_reference.py) and [pedal-map tests](../tests/test_pedal_map.py). Source tests exercise fixed seed answers, waveform/phase anchors and muted advancement; engine tests compare coherent collisions and continued phase during silent/disconnected processing. | **Nominal generator and documentary map gates passed; complete M2 physical scope open.** [Factory comparison](FACTORY_REFERENCE.md) corroborates all 549 manual assignments and all 200 pedal positions, including five disconnections. Agent 47 adds the local CSV-to-audio gate above. [NUMERICAL_BOUNDS.md](NUMERICAL_BOUNDS.md) records the `2^-53` turns/sample support floor and bounded drift. Still missing: production gearing, mechanical/tooth phase relationships, pickup waves/levels/loading, leakage and specimen calibration. Pedal mapping is data, not runtime pedal audio. |
| **M3 — console behavior.** Nine contact trajectories per key, retained banks, physical presets, pedals, shared percussion/recharge and loaded expression. | [ControlState](../src/ControlState.cpp), [control persistence](../src/ControlStateIO.cpp), [console tests](../tests/test_controls.cpp), [persistence tests](../tests/test_control_io.cpp) and [parameter tests](../tests/test_parameters.py). Tests inspect hidden-bank edits, exact-sample held-key switches, Cancel/reselection versus panic, snapshot atomicity, all bank/route combinations and partition invariance. [Pedal data](../data/pedal-map.json) has no engine consumer. | **Early bank/state gate passed; M3 incomplete at the inspected revision.** Four manual A/B banks, routing-only Cancel, a linear expression surrogate and 39 proposed internal controls exist. Boolean keys, exclusive A/B selection and saved controls do not supply nine-contact trajectories, fixed-preset latch/loading behavior, shared recharge or pedal shaping. Complete and test the newest continuation's nominal contact/percussion work, then remaining preset/pedal/expression semantics; measured qualification separately needs the [P2/P3 captures](CAPTURE_PROTOCOL.md). |
| **M4 — scanner.** Reviewed LC topology, one continuous scanner history, six modes, loaded independent AC/transient agreement and stability. | No scanner implementation, scanner mode controls, LC graph or production scanner suite occurs in the inspected source/build inventory. [Review 03](development/agent-notes/03-atlas-pages-169-252.md) and [ERRATA.md](research/ERRATA.md) retain source-equation and traversal hazards. | **Engineering not implemented; tests not run; physical evidence missing.** Reconstruct the selected connectivity and loads, resolve the 15-entry/16-position traversal and algebra issues independently, then compare all signed outputs/modes and transitions with a separate solver. Historical equations/results printed in the atlas do not qualify this repository. Actual scanner captures close the separate specimen-response gate. |
| **M5 — organ electronics.** Connected revision-specific AO-28 graph, loaded linear model before nonlinear stages, G-G diagnostics, convergence and alias protection. | The inspected engine ends in normalized dry mixing and a linear gain. It has no AO-28 netlist, transformer/device solver, oversampling or physical G-G output. [Review 03](development/agent-notes/03-atlas-pages-169-252.md) records the distinction between component inventory and connectivity. | **Engineering not implemented; tests not run; physical evidence missing.** Close revision/connectivity and component/transformer/load uncertainties; retain independent operating-point, AC, time-domain, convergence, state and alias tests. Admit calibrated dry G-G captures and validate the complete dry organ before cabinet fitting. The normalized renderer and Table V service values do not supply this port or calibration. |
| **M6 — Leslie electronics.** Separate 122/147 amplifier, transformer, crossover and coupled driver loads with signed differential ports. | No Leslie electrical module or loaded electrical test exists in the inspected inventory. [Review 04](development/agent-notes/04-atlas-pages-253-336.md), [errata](research/ERRATA.md) and [downstream capture gates](CAPTURE_PROTOCOL.md) specify variant and return/polarity boundaries. | **Engineering not implemented; tests not run; physical evidence missing.** Identify cabinet/amplifier/driver revisions; retain connected graphs, independent loaded AC/polarity checks and nonlinear stability evidence. Measure real driver impedance and electrical response. A nominal resistive load or a 122 result cannot establish a 147 or acoustic match. |
| **M7 — rotary acoustics.** Independent horn/drum dynamics, causal moving paths, directivity, cabinet/microphone geometry and optional room. | No rotor, delay/interpolation, radiation, microphone or room DSP is present. [Reviews 04](development/agent-notes/04-atlas-pages-253-336.md) and [05](development/agent-notes/05-atlas-pages-337-420.md) retain the proposed effect ownership and causal path requirements. | **Engineering not implemented; tests not run; physical evidence missing.** Implement independent mathematical moving-path/interpolation, transition, tail, stereo/mono and sample-rate gates. Acquire synchronized horn/drum trajectories, stationary-angle responses and qualified geometry/room evidence. Identical channels in a dry WAV are not rotary stereo or acoustic validation. |
| **M8 — calibration.** Immutable acquisitions and ancestry, whole-group splits, upstream fitting, uncertainty, predeclared thresholds and held-out/listening results. | [Capture validator](../tools/validate_capture.py), [schema](../data/capture.schema.json), [planned example](../data/capture-planned-example.json) and [41-method suite](../tests/test_capture.py). Inspected assertions distinguish metadata from optional byte checks, reject changed files/aliases and retain explicit unknowns. [PCM analysis](AUDIO_MEASUREMENTS.md) concerns generated digital samples. | **Metadata/byte-integrity tooling passed; physical calibration not run.** [CAPTURE_VALIDATION.md](CAPTURE_VALIDATION.md) gives the exact software limit. No admitted hardware corpus, calibrated fit or held-out result exists at this checkpoint. Close with actual rights-qualified captures, independent signal-header/chain/clock/load review, restored bytes, corpus-wide ancestry/duplicate audit, frozen group/purpose ledger, uncertainty and final untouched evaluation. The current validator does not enforce those corpus/physical gates. |
| **M9 — product and release.** VST3/device adapters, stable exports/state, native accessible UI, actual hosts/devices and qualified packages. | [CMake OfflineTools rules](../CMakeLists.txt) and [install test](../tests/test_install.py) install eight offline files, relocate a prefix with spaces, compare actual WAV/PCM/JSON and reject a missing profile. [Internal parameters](PARAMETERS.md), [saved controls](CONTROL_STATE_FORMAT.md) and the local [host handoff](HOST_INTEGRATION.md) prepare future contracts. | **Offline installation gate passed; product implementation and native qualification open.** The local report is supplemented by the integrator's observed four-job success at `6c3dd8b` above. No VST3, audio-device standalone or native UI exists at that revision. The 39 internal IDs are not host exports, and `B3CONTROLS1` is not a DSP checkpoint or released wrapper migration. Host/device/accessibility/release closure requires the actual evidence below. |

## What the strongest existing passes establish

The factory chain has three distinct links. Two frozen image transcriptions
corroborate the existing data; the Python comparison checks all compiled manual
routes against those CSVs; Agent 47's local test checks actual engine samples
against CSV-selected branches. The first two are in the inspected published
checkpoint; the third is pending integration. The raw authoring profile remains
`d17a266ed97cbbd3a2925ebebafafbd6c0e3f84763635732e0a9351d0eab2bff`, and its
retained compiled profile remains
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.
The original `independent_factory_verification=false` and pedal provenance
`missing` record original authoring history; the later
[attestation](FACTORY_REFERENCE.md) adds corroboration without rewriting those
identities. It does not close gearing or physical response.

The callback gate observed zero global C++ allocation/deallocation calls in 63
accepted and 33 rejected requests, covering 216,255 frames and 23,919 events.
Its [report](REALTIME.md) excludes direct C/system/custom allocation, linked
runtime internals, other threads, dynamic lock/I/O interception, concurrency and
deadlines. The [benchmark](BENCHMARKING.md) records elapsed observations without
a timing pass threshold. Neither result qualifies a live device callback.

The numerical gate rejects source increments too small to guarantee binary64
phase progress. Its independent elapsed-time oracle checks nominal extreme
sources over 262,144 frames per supported rate, with a maximum reported checked
phase error of `7.722181563901e-12` turns. This is bounded numerical evidence;
the support floor is not frequency accuracy near that floor, and the test is
not an unlimited-duration or physical tuning claim. The synthetic 1,098-branch
maximum-mix case also permits values far above PCM full scale. See
[NUMERICAL_BOUNDS.md](NUMERICAL_BOUNDS.md).

Five [event fixtures](../examples/README.md) have retained actual-render checks.
The [producer](RENDER_EVIDENCE.md), [independent consumer](RENDER_VERIFICATION.md)
and [PCM analyzer](AUDIO_MEASUREMENTS.md) separately test stable artifact identity,
documented assertions and serialized samples. Their exercised suites include
19 producer methods after the portability repair, 27 verifier methods and 15
analyzer methods in the retained reports. The reported A4 crossing estimate
`439.9999816417002 Hz` is for a declared nominal single-tone window, not an
instrument measurement. Hash consistency does not authenticate authorship or
associate a binary with source; the verifier does not replay it. Same-build
partition/replay equality is not cross-toolchain bitwise identity.

## Material open product gates and evidence that would close them

| Gate | Current disposition | Required reviewable closure evidence |
| --- | --- | --- |
| Current integrated offline software | Published `6c3dd8b` passed all four hosted jobs; the completed integrator audit records 21 suites, 257 Python methods and zero skips per job. New local Agent 47 test has no hosted result. | Preserve the retained full-log audit. Build and qualify the next integrated commit/tree/profile, with a later four-job run that actually includes the added runtime test before claiming its hosted coverage. Preserve older failures. |
| Complete console and dry organ | M3 partly implemented; M4/M5 absent at inspected revision. Separate continuation actively advances M3. | Newest code and model identities; contact/percussion/preset/pedal/expression behavior tests with continuous histories, partial releases, same-frame changes and retained states. Follow with independently reviewed scanner/AO-28 connectivity, loaded numerical comparisons and complete dry-port validation. |
| Specimen-specific organ/cabinet fidelity | Physical reference, acquisitions and M4–M8 response evidence missing. | Identity/permissions, calibrated clocks and signal boundaries, actual dry/electrical/rotor/acoustic recordings, uncertainty and repeatability; independent whole-group holdouts and predeclared decisions including failures/inconclusive outcomes. [CAPTURE_PROTOCOL.md](CAPTURE_PROTOCOL.md) gives the dependency order. |
| Native VST3 and standalone playback | Adapters and backends absent; proposed cases are `not_run`. | Actual binaries and export enumeration; validator plus named DAW/device sessions; same-fixture equivalence, varying blocks/flushes, automation/transport, multi-instance state/lifecycle, device loss/reconnect, latency/tails/bypass and ownership/fault recovery. Retain host/driver/OS/rate/buffer/build identities. |
| Callback deadlines and concurrent state | Core allocation observation only; no live queues, publication/retirement protocol or hard-deadline qualification. | Bounded adapter admission and recovery; delayed-reader/full-queue/generation/lifetime tests; target-specific allocator/lock/I/O/race evidence; declared callback budgets and actual duration/underrun/late-event/loss telemetry under cold start, dense input and UI load. Re-audit after callback dependencies change. |
| Saved product state and native UI | Internal controls/save format exist; wrapper migrations and native dimensional/flat UI absent. | Versioned wrapper/profile/registry migrations and retained recall fixtures; stable automation gestures/IDs across bank/camera changes; actual keyboard, screen-reader, resize/DPI, focus/input-owner, reduced-motion and editor-absent playback sessions. Design diagrams and browser labels cannot qualify these tasks. |
| Distribution and reproducible release | Local eight-file layout only; project license and affected source/asset rights unresolved. | Selected dependency/SDK/backend versions and primary terms; applicable notices in the actual staged package; reviewed asset/capture rights; source-to-binary provenance and payload hashes; clean-machine install/uninstall, runtime compatibility and applicable signing/notarization reports for each advertised platform. [Rights inventory](DEPENDENCIES_AND_RIGHTS.md) and [install contract](OFFLINE_INSTALL.md) retain the present boundary. |

Close a gate only for the claim, revision, boundary and operating domain actually
tested. When source, model, profile, topology, load, capture rig or state contract
changes, retain the earlier result and identify the affected checks to repeat.
M3 nominal engineering can continue while physical acquisition is pending; later
cabinet fitting must follow dry-organ validation. Agent-wave completion, a complete
page review, a valid schema, an attractive UI or a green subset of CI supplies
none of the missing evidence by itself.

This audit's inspected/executed boundary and the stale claim found during review
and reconciled by the integrator are retained in
[Agent 49's note](development/agent-notes/49-acceptance-matrix.md).
