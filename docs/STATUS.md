# Development status

## Active pedal development session

The [current sixty-assignment, ten-wave session](development/2026-11-13-pedals/README.md) starts from `b4fc61ccfcc59724f14fb0cee947ed7bb7142075`. **48 new workers have completed eight waves.** Six fresh readers covered all 500 atlas pages and selected actual diagrams; the PDF is unchanged. Earlier sessions below remain historical records.

The core now includes typed 200-position pedal routing, 25 independently held pedals, a named fixed two-mixture voice, two controls and `B3CONTROLS3`. Old state formats explicitly migrate to muted pedals. The registry has 45 records, preserving every field of the earlier 43. Pedals consume the Engine's existing single source frame; lower Cancel, division panics and upper percussion remain independent. Last-rendered diagnostics retain their actual frame/rate tags. The matrix and linear pedal gain are explicit nominal engineering fixtures, not recovered electrical values or measured 16-foot/8-foot responses.

Independent checks cover both CSV maps, all pedals/contacts and supported rates, coherent manual/pedal collisions, bitwise source histories, partition identity, migration during moving contacts and whole-call rejection. The repaired coherent archive `e1828586c35ea40562d6de6be671c206d725edd2` passed **55/55 local Release suites**, zero failures, in 54.86 seconds. The first-run stale allocation-fixture failure and repair remain in the session log. The preceding kernel commit `6768ef2388819ebbaaf7cc23bdf72265dc72c561` passed all 51 local Release suites and all four hosted jobs in [run 43394209142](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43394209142), including leak-enabled ASan/UBSan.

Published pedal Engine commit `e493b9fed9e3ed8a294fb5d95af447132776cb3a` also passed all four hosted jobs in [run 43397574429](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43397574429).

The typed pedal adapter now retains up to 256 owners across two origin buses and 16 channels. A combined ordered manual/pedal/control facade commits both ledgers only after one Engine call accepts the complete block. Independent review covers 256+256 simultaneous owners, 1024/1025 expanded-event limits, three rates, both manual contact models and over 1.16 million exact phase comparisons.

The offline renderer accepts four explicit pedal verbs and `--pedal-drawbars NN`; new render/evidence outputs are schema 3. The independent verifier retains exact schema 1/2 acceptance and rejects pedal additions under those historical grammars. All eight original scores produced byte-identical WAV/PCM versus the frozen starting revision in 24 local runs, including default and explicit 00 pedals. Test-migration fixture failures and their repairs are retained in assignment 23.

The combined input/renderer checkpoint passed **60/60 local Release suites**, zero failures, in 56.10 seconds on frozen tree `f84cacb4e6eb01189ca29136fc838885fdd858f4`.

The first hosted wave-4 run exposed a Windows Unicode argument conversion; a second run caught only an established diagnostic-word mismatch. The [renderer repair review](reviews/PEDAL_WINDOWS_UNICODE.md) retains both failures. Published repair `a451ebd` passed Windows MSVC, Linux Release and Linux ASan/UBSan with leaks in run 43402590446. Its queued macOS job later ended cancelled; no macOS pass or inferred cancellation cause is claimed for that repair run.

Wave 5 adds [same-frame pedal traces](PEDAL_TRACE.md), compiled pedal model metadata and four [independently checked musical scores](PEDAL_AUDIO_ACCEPTANCE.md). Model-info schema 2 appends actual compiled pedal identities without changing the earlier console/source fields. The trace covers unmute, overlap and held-routing scenarios at three rates; the catalog checks exact block partition output and independently fitted source amplitudes.

[HostTimeline](HOST_TIMELINE.md) now reconstructs sample-linear normalized curves from previous-sample anchors, applies exact existing discrete thresholds and retains offset-N endpoints correctly. It owns one whole-callback transaction for audio, owners, controls, anchors and carry. [StateExchange](STATE_EXCHANGE.md) provides four pending UI loads and coherent atomic publication without accessing live Engine state on the UI thread. Its focused Release and ThreadSanitizer stress gates passed. The [enabled-path allocation audit](PEDAL_REALTIME.md) measured 180 actual API regions with zero observed global C++ allocations/deallocations, including the complete proposed callback protocol. These results are scoped; no audio-device deadline is inferred. Root's combined frozen tree `06786b70f1cffcc6371600fd6e14306f16e8c985` passed **65/65 local Release suites**, zero failures, in 65.41 seconds. Published commit `88c36b4a72a07f6498f73279f25023278accd350` has exact remote/local tree identity and passed Linux Release, Windows MSVC and Linux ASan/UBSan with leak checking in [run 43404272839](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43404272839). Its first macOS acquisition failed before any step; one targeted retry then passed **65/65 suites** on macOS ARM64 in 45.86 seconds. Run attempt 2 is now observed successful across all four jobs. The [runner record](reviews/PEDAL_RUNNER_AVAILABILITY.md) retains the initial infrastructure failure and actual recovery.

Wave 6 implemented the [optional native VST3 build](VST3_BUILD.md): an actual `HammondB3.vst3` module, original processor/controller UUIDs, three event buses, 45 parameter exports, float32 stereo, bounded automation and active UI state calls. SDK acquisition is explicit, pins and selected licenses are checked, and tracked/untracked/ignored source changes reject. Ordinary builds remain SDK-free. The bundle embeds the unchanged nominal profile and includes scoped SDK notices.

The actual Linux bundle passed independent [ABI](VST3_ABI_ACCEPTANCE.md) and [behavior](VST3_BEHAVIOR_ACCEPTANCE.md) gates against plain Engine references, including all three rates, audible isolated divisions, 512 owners, 1024-record/carry limits, four pending states and failed-call future-audio preservation. The native controller gate passed 41,795 checks with all 45 metadata records and strict state streams. The SDK validator reports 47 passed/zero failed/exit zero, while retaining 16 contradictory teardown diagnostics and nine unsupported-rate error messages; it is not a warning-free or arbitrary-format qualification. The independent harness verifies balanced supported lifecycle directly.

A separate [native CI workflow](VST3_CI.md) acquires the locked SDK, builds all test inputs, runs one verbose native test pass, and retains actual platform bundles, byte inventories and complete logs. Local acquisition, inventory and archive transport checks passed. The coherent sixth-wave tree `b2dae50dcde294bde8e7acb7addb14456197a779` passed **67/67 SDK-free Release suites** in 78.43 seconds and **4/4 focused native suites** in 5.23 seconds, with zero failures or skips. The [integration review](reviews/PEDAL_NATIVE_INTEGRATION.md) records the exact module and logs. First hosted execution found specific macOS/Windows integration defects while native Linux passed. The [portability repair review](reviews/PEDAL_NATIVE_PORTABILITY.md) records the observed failures, scoped fixes and successful focused local checks; hosted recovery of native execution is observed on Windows/macOS, while Windows inventory still requires the fresh-path follow-up below. Wave 7 adds consistent CLI Unicode handling, explicit install/relocation, actual native callback allocation/concurrency and further automation/legacy acceptance. Full M3, scanner/AO-28/Leslie, specimen calibration, audio-device operation, custom UI and signed distribution remain open.


Wave 7 completed [shared CLI Unicode handling](CLI_UNICODE.md), a 22-file
[offline install](OFFLINE_INSTALL.md), and explicit [native local staging and
relocation](VST3_LOCAL_INSTALL.md). The relocated actual Linux bundle passed
its ABI test. The [native allocation audit](VST3_REALTIME.md) measured 133 API
regions with zero observed C++ new/delete calls and proved module interposition
without substituting host Engine symbols. The [dense automation review](VST3_AUTOMATION_REVIEW.md)
checks all 45 curves, internal event slicing, carry, restores and exact future
audio. The [native concurrency gate](VST3_CONCURRENCY.md) passed Release and a
fully instrumented loaded-module ThreadSanitizer run.

The [legacy review](reviews/PEDAL_LEGACY_FINAL.md) preserved 57 baseline files,
all earlier 43 full registry records and complete audio bytes in 24 original-score
runs. Parameter-info schema 2 states its SDK-free diagnostic verification scope;
registry, state and render-evidence versions are unchanged. Root's [coherent
seventh-wave gate](reviews/PEDAL_WAVE7_INTEGRATION.md) passed 8/8 native suites
and initially 67/68 SDK-free suites; the one stale install-schema assertion was
repaired and its two methods passed. The fresh-path inventory follow-up passed
19 methods. All compiled inputs are unchanged across those focused repairs; no
second full 68/68 execution is claimed. At separate repair `9403debd`, all three
platforms passed actual native tests, Linux/macOS completed artifacts, and core
Windows passed 66/67 with inventory still failing. The new inventory repair's
Windows execution and exact wave-7 hosted matrix remain pending.

## Wave 8: retained demo, plots and resumable development

Assignments 43–48 completed the [retained pedal phrase](PEDAL_DEMO.md), its
[independent acceptance](reviews/PEDAL_DEMO_ACCEPTANCE.md), the [pedal SVG
plotter](PEDAL_TRACE_PLOTS.md), the [operational handoff](PEDAL_HANDOFF.md), the
[remaining M3/scanner gate](M3_REMAINING_AND_SCANNER_GATE.md) and a [checker for
this actual session](PEDAL_SESSION_CHECKS.md). The three-second 48 kHz stereo
WAV retains all inputs, schema-3 evidence, seven PCM windows and all 474 original
source-blob identities. Independent local replay and block partitions match;
component renders agree within the stated quantization bound. It remains
synthetic nominal-model evidence, with no physical or subjective listening claim.

The standalone standard-library plotter checks the full pedal CSV contract,
retains every state-transition boundary and min/max envelope bins, and embeds
its exact CSV hash and metadata. Three actual 48 kHz SVGs were rendered and
visually inspected. Root added it to the explicit 23-file OfflineTools component;
all three relocated pedal plots are compared with their source-script execution.
The [coherent eighth-wave gate](reviews/PEDAL_WAVE8_INTEGRATION.md) passed
**71/71 SDK-free Release suites in 54.37 seconds** and **8/8 focused native
suites in 7.87 seconds**, with zero failures, disabled tests or skips.

The new session checker passed the actual 48-complete gate: eight complete waves,
51 dispatched workers, three running assignments and nine planned rows. This
validates retained record consistency; root separately accepted the actual work.
The remaining twelve assignments continue final code, evidence, install,
platform and handoff reviews. No earlier session's sixty agents are recounted.

At wave-7 commit `7fb9b612`, Windows subsequently passed **68/68 SDK-free suites**
and **7/7 native suites**, including inventory and bundle publication. Linux
passed its core, sanitizer and **8/8 native** gates and uploaded its bundle.
Root downloaded both ZIPs and matched their digests and every payload member's
bytes, mode and hash. macOS remained queued at this observation. Exact artifacts,
failures and recovery are in the [portability review](reviews/PEDAL_NATIVE_PORTABILITY.md).

## Earlier checkpoints and retained history

Foundation session started 2026-11-12 (America/Halifax), baseline `501c68b`.
The [console continuation](development/2026-11-13-continuation/README.md) started
2026-11-13 (UTC) from `9c8068c`; its new assignments are counted separately.

**Original requested session complete:** all 60 distinct worker assignments in
ten waves of six have finished. The [execution ledger](development/AGENT_LEDGER.md)
records every actual scope, outcome and limitation; the separate continuation's
workers are excluded. The final session record follows the qualified code/demo
checkpoint `61c6ecb`. Current product work continues at the scoped stage below.

**Continuation complete:** all 60 distinct new worker assignments in ten waves
of six have finished, with sixty retained notes and no planned/running slots in
the [separate manifest](development/2026-11-13-continuation/assignments.json).
The explicit sixty-complete checker passes. These workers are separate from the
original session above. Qualified code `7469ebf` passes all 46 suites and 372
Python methods on all four hosted jobs in
[run 43380966473](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43380966473).
The final result publication preserves those code/test/data identities. The next
product task is the prepared pedal-routing kernel below; full M3 remains open.

## Earlier console checkpoint scope (historical)

The following retained narrative describes the preceding console session; the active pedal/native status above supersedes its parameter/state and unimplemented-pedal statements.

The M0 engineering foundation and a scoped M1/M2 nominal dry engine are implemented.
The engine owns 91 shared sine sources, explicit manual routing, independent contacts,
manual drawbars and a linear expression surrogate. It consumes bounded sample-offset
events with atomic rejection, stable ties, zero-frame flushes and an independent
64-bit render clock. Source phase continues through silence and disconnected output.

The offline renderer writes actual stereo PCM16 WAV files, reports signal metrics,
subdivides dense event blocks and publishes without overwriting existing files.
Independent profile, generator, scheduler and renderer tests passed their assigned
Debug/Release scopes. Source pitch, coherent foldback, same-build block partition
identity and malformed-input behavior have retained software evidence.

M3 remains a partial nominal implementation. It includes four retained A/B banks,
hidden-bank edits, routing-only Cancel/reselect, 1,098 independent contacts and one
shared upper-B percussion readiness state. The optional linear-travel model has
separate make/break thresholds, explicit partial-key input, incomplete
return and hysteresis. Its proposed times and thresholds are unmeasured. Percussion
uses the physical ninth contact detector, second/third harmonic routing, retained
normal/soft and slow/fast controls, finite recovery and upper-only one-foot masking.
Ideal contacts and percussion off preserve original renderer defaults.

Control serialization writes `B3CONTROLS2` and migrates `B3CONTROLS1` with percussion
Off/Second/Normal/Slow. It preserves 43 controls plus route-enable bits, excluding
key ownership, trajectories, readiness, source phases and time. All 39 earlier
registry records are unchanged; four new IDs append percussion controls. These
are proposed identities, without actual VST3 exports.

The typed host-input foundation now has a fixed 256-owner adapter with stable
channel/note-ID handling, FIFO anonymous releases and retained original manual
routing. The transactional facade commits ownership only after Engine accepts
its physical events. A native bridge maps all 43 normalized internal controls to
fixed Engine targets, including exact half-step boundaries under all four standard
rounding modes. JSON parsing stays outside processing. Native host exports, MIDI
byte decoding, automation curves, device operation and deadlines remain separate.
The native-input checkpoint `093d985` passed all 34 local Release suites on its
exact staged tree. Hosted [run 43371559575](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43371559575)
passed Linux GCC, macOS AppleClang and Windows MSVC Release plus Linux
ASan/UBSan with leak checking.

The [sample-rate lifecycle](SAMPLE_RATE_LIFECYCLE.md) now provides an explicit
stopped/same-thread transaction between 44.1, 48 and 96 kHz when the owned profile
supports the target rate. It preserves phases, contact position and hysteresis,
readiness, held targets, controls and frame count. Same-rate requests are exact
no-ops; rejected changes preserve state and future output. Mixed-rate elapsed
seconds require the caller's rate schedule. This core API provides no native
host/device transition or concurrent publication protocol. Its combined clean
Release archive passed all 39 CTest suites. Published commit `53bb6e1` also passed
all four hosted jobs in [run 43372984603](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43372984603),
including the leak-enabled sanitizer job.

Explicit `KeyPosition` events and the matching offline score command now expose
partial targets through the Engine. Ideal mode accepts endpoints only; mode and
payload errors reject before rendering/output creation. The nominal
[console trace](CONSOLE_TRACE.md) exports three bounded scenarios with current
contact bits, readiness, routing, source phase and same-frame audio. Independent
checks compare all 67716 rows at three rates against separate numerical models.
A bounded [SVG plotter](CONSOLE_TRACE_PLOTS.md) preserves contact transitions and
documented extrema with input-byte provenance. The continuation ledger separates
these focused checks from publication. The combined clean Release source passed
all 43 CTest suites. Published commit `9a5c99a` passed all four jobs in
[run 43375043990](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43375043990),
with 352 Python methods and zero skipped tests in every complete diagnostic
archive. The [continuation platform review](reviews/CONTINUATION_PLATFORM_REVIEW.md)
retains the actual toolchains, logs and artifact identities.

Pedal mapping data contains 195 connections and five explicit disconnections;
runtime pedal audio remains open. Physical preset latching, continuous drawbar
travel, contact bounce/antialiasing, loaded expression, scanner, AO-28, Leslie DSP,
VST3, audio-device standalone and native UI remain unimplemented. Full M0 specimen
lock, factory gearing, source calibration and measured instrument fidelity remain
open despite the working nominal implementation.

Two independently frozen factory Table III transcriptions now agree with all
549 manual assignments and all 200 pedal positions in the existing data. The
[factory comparison](FACTORY_REFERENCE.md) records the exact source, page locators,
hashes and five disconnections. This later documentary attestation leaves the
original nominal profile identity and its original authoring provenance unchanged.

The proposed [capture contract](CAPTURE_FORMAT.md) and validator distinguish
planned work, declared recorded metadata and optional artifact-byte verification.
The committed example is a plan with no invented specimen, recording, timestamp
or calibration. Its 41-method software suite passes locally and in the hosted
matrix at `6c3dd8b`. Actual acquisitions,
physical admission and corpus-wide holdout independence remain open.
The [acquisition protocol](CAPTURE_PROTOCOL.md) provides prioritized dry-organ
tasks, explicit evidence gates and whole-take holdout grouping for that work.

## Reproducible software evidence

Five versioned musical/event fixtures cover both manuals, nominal A4, low/high
coherent foldback, and held-note bank/Cancel transitions. All five passed their
assigned actual-render checks with no reported clipping. A reproducible wrapper
retains input/compiled/WAV hashes, raw logs, actual float metrics and separate PCM
statistics. An independent PCM analyzer provides bounded window measurements and
qualified crossing-rate estimates. None authenticates a physical instrument.

[Hosted CI run 43368537860](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43368537860)
passed all 26 CTest suites at `61c6ecb` on Linux GCC, macOS AppleClang and Windows
MSVC Release, plus Linux ASan/UBSan with leak detection enabled. Each complete
diagnostic archive contains 274 Python methods and zero test skips. Qualification
applies to this offline software and those runners; native audio-device and
plugin-host gates remain open.

The historical `7c2ad20` checkpoint exposed a Windows repository-diagnostic path
mismatch and a Linux sanitizer render-evidence mutation-test failure. The repairs
were incorporated in `6c3dd8b`; its hosted matrix passed. The
[CI audit](CI_QUALIFICATION.md) retains the earlier failure evidence.

The contact/percussion module checkpoint `7a24a30` passed all **24/24** suites in
a clean archive of its exact staged source tree. Hosted
[run 43366836424](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43366836424)
passed Linux GCC, macOS AppleClang, Windows MSVC Release, and Linux ASan/UBSan with
leak checking. This qualification predates the subsequent Engine/CLI integration.
The continuation ledger records the next checkpoint's complete checks separately;
focused integration tests alone do not establish a new full-matrix pass.

The [OfflineTools local install](OFFLINE_INSTALL.md) now contains four native
executables, the trace plotter, the compiled profile, two catalogs and eight
scores. Its focused Linux gate passed installation and prefix relocation with
unchanged WAVs, metadata, CSV and SVG outputs from an unrelated directory. Earlier
install versions passed hosted macOS/Windows qualification; the expanded 16-file
component passed the combined 45-suite local Release gate and all four hosted
jobs at `2046b93` in [run 43376892064](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43376892064).

The [factory runtime acceptance](FACTORY_RUNTIME_ACCEPTANCE.md), retained
[four-second demo](../examples/rendered/nominal-two-manual-v1/README.md),
[independent local replay](DEMO_REPLAY.md) and final persistence/evidence repairs
are now published in `61c6ecb`. Its exact clean staged source passed all 26
Release suites and 274 Python methods with zero skips. The route gate exercises
all 1,098 key/drawbar routes across both manuals with CSV-selected expected
sources. Their hosted gates passed in run 43368537860, independently audited in
the [final platform review](reviews/FINAL_PLATFORM_REVIEW.md). None establishes
physical fidelity. Those historical results predate this continuation's Engine/CLI extension.

The console integration `4ead769` passed **30/30** local Release suites on its
exact published tree. Hosted run 43369940466 passed Linux Release and sanitizer
checks; Windows and macOS each passed 29/30, failing the same producer test's
unresolved-versus-canonical temporary-path comparison. The
[CI repair review](reviews/CONSOLE_CI_REPAIR.md) retains the observed cause and
portable regression. All 28 producer methods pass locally after the test repair;
hosted [run 43370542634](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43370542634)
subsequently passed all four jobs at repair commit `72b5062`, including Linux
ASan/UBSan with leak checking. This closes that observed portability failure.

The [enabled-path allocation audit](REALTIME.md) observed zero C++ allocation
and deallocation calls in 126 Engine/facade requests, plus separately measured
translation, parameter and stopped lifecycle operations. Its calibration detects
all replaced overloads. The historical 96-call ideal/off evidence remains scoped
separately. Contact edges can require a coefficient rebuild without new events,
so the current conservative bound is one rebuild per rendered frame. This scope
does not establish native callback deadlines or general system allocator behavior.
The independent bundle verifier retains schema1 compatibility and current schema2
grammar, while distinguishing artifact integrity from authenticity.

The [runtime boundary review](reviews/RUNTIME_BOUNDARY_REVIEW.md) found no
actionable defect in the inspected core transactions. The
[legacy audio comparison](reviews/CONTINUATION_LEGACY_AUDIO.md) passed exact
WAV/PCM comparisons against a fresh earlier-revision build and preserved the
existing fields alongside three intentional schema2 additions. The bounded
benchmark adds explicit console-motion and owned-input workloads; its observed
stdout-failure repair and scoped checks are retained in
[BENCHMARKING.md](BENCHMARKING.md). Timing values never become pass thresholds.

Preparation also rejects increments too small to advance the binary64 source
phase reliably. [Numerical bounds](NUMERICAL_BOUNDS.md) record the exact support
floor, atomic rejection and bounded nominal drift checks. The
[benchmark](BENCHMARKING.md) reports observed processing intervals without a timing
pass threshold. The [repository checker](REPOSITORY_CHECKS.md) verifies retained
source/index/link/data identities and supports an explicit final agent count.

## Final continuation review and qualification

All six final review records are retained: [core runtime](reviews/FINAL_CONTINUATION_RUNTIME.md),
[input and persistence](reviews/FINAL_CONTINUATION_INPUT.md),
[offline evidence](reviews/FINAL_CONTINUATION_EVIDENCE.md),
[handoff](reviews/FINAL_CONTINUATION_HANDOFF.md),
[platforms](reviews/FINAL_CONTINUATION_PLATFORM.md), and
[readiness](reviews/FINAL_CONTINUATION_READINESS.md). Their observed snapshots and
pending-at-the-time gates remain historical evidence; this section records the
later integrated outcome.

The runtime and input reviews found no actionable core defect in their stated
scopes and passed twelve focused binaries between them. Evidence review found
and fixed buffered stdout failures in renderer help and JSON reporting. The new
regression reproduced both old failures; all 35 renderer methods pass and the
repaired demo replay exactly matches the retained WAV. A complete WAV can remain
if subsequent summary delivery fails, as specified in
[the render contract](RENDER_FORMAT.md). Stale host/ownership guidance now matches
the implemented FIFO, 43-control migration and stopped rate APIs.

The corrected combined source passed 46 local Release suites and 371 Python
methods before publication as `6bdce06`. Its first hosted run passed Linux,
macOS and sanitizers, while Windows failed only the new accounting suite. Root
and assignment 59 independently reproduced the CRLF owner-line defect; a bounded
normalization and permanent explicit-CRLF regression fixed it. The
[repair record](reviews/CONTINUATION_CRLF_REPAIR.md) preserves that failure.

Repair commit `7469ebf759ced820cc34fc9012beff6f772e4b89`, tree
`096e2cd13c5aa3fc40e996c923ed80be36b0f622`, passed **46/46 suites, including
372 Python methods, on every job** in
[run 43380966473](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43380966473).
All four complete diagnostic archives were independently length/hash verified.
There are zero failed, disabled or skipped tests; actual sanitizer compilation,
linking and leak-enabled test settings were inspected. These checks qualify the
stated offline software scope on the named runners, while native device/host,
concurrency, physical fidelity and complete M3 retain their separate gates.

## Current handoff and next implementation

The [current developer handoff](CONTINUATION_HANDOFF.md) gives the first build,
render, evidence, trace, plot, benchmark and relocation commands. The verified
[two-second nominal console example](../examples/rendered/nominal-console-v2/README.md)
retains its genuine schema2 bundle, measurements and a separate diagnostic plot.
It reports zero clipping and exact same-build block-partition replay.
The [identity review](reviews/CONTINUATION_IDENTITY_REVIEW.md) confirms the
preserved PDF, profile, maps and original fixture identities, all 39 original
parameter records, four appended controls and the stated migration boundaries.
The [continuation record checker](CONTINUATION_CHECKS.md) separately validates
this session's actual assignment states and notes; the original sixty remain
a distinct completed session.

The [next M3 gate](M3_NEXT_GATE.md) is a prepared pedal routing/reference kernel.
Begin with typed admission of the complete 25-by-8 map, then return four bounded
bus excitations from the existing shared 91-source frame. Preserve all 200
contact positions, five disconnections and distinct repeated-source branches.
Playable controls, host mapping, state migration and physical voicing follow
separate gates; this proposed kernel is not yet implemented.

## Evidence boundary

The separate [console continuation](development/2026-11-13-continuation/README.md)
completed its sixty assigned scopes and qualified the nominal partial-M3 code.
Its review notes, standing instructions, corrections and observed checks remain
in history. Inspect the current code and next pedal gate before starting further
integration work. The original
[assignment ledger](development/AGENT_LEDGER.md), [acceptance matrix](ACCEPTANCE_MATRIX.md)
and [operational handoff](SESSION_HANDOFF.md) retain session-specific evidence.

- All 500 source pages were read across six complete page-range assignments;
  their notes retain coverage and visual checks.
- Companion JSON, reference code, source catalogs, original verification outputs
  and measured captures referenced by the atlas are absent from the baseline.
- Reconstruction from PDF formulas/printed tables is labeled as such.
- Specimen identity, AO-28 revision, tuning/phase/pickup calibration, contact and
  circuit response, Leslie measurements and host qualification remain open.

See [PLAN.md](PLAN.md), [IMPLEMENTATION_CONTRACT.md](IMPLEMENTATION_CONTRACT.md),
[DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md) and [NEXT_STEPS.md](NEXT_STEPS.md).
