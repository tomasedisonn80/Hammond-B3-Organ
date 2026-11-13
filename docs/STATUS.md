# Development status

## Independent capture and calibration-readiness continuation

The new [calibration session](development/2026-11-13-calibration/README.md)
starts from `38c1fac` with sixty distinct new assignments in ten waves.
Its [scope](CALIBRATION_SCOPE.md) advances offline M0/M8 audio inspection,
corpus integrity/split auditing and fixed comparison evidence. The scanner,
rotary and standalone tracks below remain independent and retain ownership.
All 500 PDF pages were freshly read by six distinct workers; the
[coverage record](research/CALIBRATION_ATLAS_REVIEW.md) retains exact text and
selected visual coverage. The clean starting source passed 85/85 local Release
suites. Audio, corpus and comparison contracts are frozen and independently reviewed.
The first twelve assignments are accepted; the JSON foundation passes 49 methods
and session accounting passes 27 methods. The decoder, corpus auditor and metric
producer are being implemented. The actual manifest distinguishes accepted and
running work. Physical calibration remains unqualified.

## Active native standalone continuation

The independent [standalone session](development/2026-11-13-next-phases/README.md)
has accepted its first **46 distinct assignments**, including seven complete
waves. The [native app](STANDALONE_APP.md) now runs the unchanged nominal dry
engine in a resizable instrument window with keyboard/pointer performance,
separate edited/sounding banks, pedals, percussion, expression, Audio/Help
panels and explicit saved controls. Follow the [operational handoff](STANDALONE_HANDOFF.md)
and actual manifest. The scanner continuation below remains a separate track.

All 500 atlas pages were reread in six disjoint ranges, including selected actual
page images. The [scope](STANDALONE_SCOPE.md) preserves the 45 public parameter
identities, source/profile/maps, saved-state formats and VST3 UUIDs. The pinned
SDL2 dependency is optional; ordinary builds remain SDK-free. The native window
uses reproducible licensed glyphs and geometry shared with input hit testing.

The intermediate SDK-free Release gate passed **81/81 suites** in 61.60 seconds.
Independent Session tests make 156,308 bit-exact stereo comparisons against a
separate direct Engine. Independent UI acceptance covers all 45 parameter IDs
and all 147 playing pitches. State-file acceptance verifies canonical output,
old-format migration, failure preservation, Unicode paths and temporary cleanup.
The maintained real SDL dummy matrix passes all 15 rate/buffer combinations,
observing 75 callbacks and 59,520 frames with zero unexpected audio faults.
Actual complete-app smoke runs at 1280x900 and 960x700 observe a note press,
its held display, its release, successful image capture and joined shutdown.

The frozen runtime checkpoint passed **83/83 Release suites**. The subsequent
assembled standalone gate passed **9/9 suites**: actual callback allocation
calibration observed zero C++ allocations/deallocations in the callback; coherent
Session concurrency also passed a separately fully instrumented ThreadSanitizer
run. App acceptance passed 18 methods and 164 actual invocations after repairing
missing-leaf path aliases and symmetric dangling-symlink hazards. The nine-file
installed component runs after relocation. Replay now drives the ordinary app
handlers and retains pre-shutdown musical observations; its independent workflow
suite passes 11 methods and 15 actual processes. The SDK-free render benchmark
and its automatic source manifest pass nine independent methods and 111 CLI
invocations. The assembled native group passes **11/11 suites** in 22.78 seconds.
The separate [chapel catalog](CHAPEL_PRESETS_CATALOG.md) admits 18 documentary
registrations and all 162 taps from two agreeing readings; independent acceptance
passes 18 methods, 111 CLI invocations, 234 API rejects and five I/O fault probes.
Its canonical CMake target and CTest also pass. The [control-file exporter](CHAPEL_CONTROLS.md)
now passes 205 exact-state vectors and actual C++ Load/Save acceptance for every
registration. The [maximum-plan repair](STANDALONE_REPLAY_BOUNDARIES.md) drains
all 256 allowed resize events within the declared runtime, preserving the
existing event budget and grace period. The [fresh combined-source gate](reviews/STANDALONE_WAVE6_INTEGRATION.md)
passed **94/94 suites** in 98.80 seconds, including the concurrent rotary code;
the later chapel exporter/native additions passed a separate **2/2** focused
CTest gate in 18.22 seconds. These are two scopes, not a claimed 96-suite run.
Four [actual native screenshots](reviews/STANDALONE_WINDOW_DEMO.md) retain exact
source and runtime provenance. Earlier [checkpoint evidence](reviews/STANDALONE_NATIVE_CHECKPOINT.md)
retains its original source scopes.

Current published checkpoint `5b8e2419d23fe27c51709d717812060eafd44dcc`, tree
`880682248c467a51cce14d920189cf0009b68d22`, preserves concurrent calibration
foundation `5026f67`. Its Native standalone Linux and Windows jobs passed build,
tests, installation/relocation and packaging. macOS compilation exposed two
unused drawing constants; their narrow removal passes strict local syntax with
an explicit unused-constant warning, and actual macOS rerun remains pending.
Core CI at the same revision passed its sanitizer job but failed Linux Release
on an incidental scheduling assertion, Windows on chapel file admission and a
calibration path mock, and macOS on that same path mock. The
[platform follow-up](reviews/STANDALONE_PLATFORM_FOLLOWUP.md) retains exact
failures and repair requirements. The reader and concurrency
oracle repairs now pass their full independent suites and root's four-suite
canonical focus in 17.28 seconds; the corrected concurrency test also passes a
fresh coherent TSAN run. Assignment 47 owns the instrumented timing repair,
while 48/49 audit hosted artifacts and fresh setup. No later platform pass is presumed.

The separate [fully instrumented native audit](reviews/STANDALONE_NATIVE_SANITIZERS.md)
built core, Session/app and all SDL C sources with ASan/UBSan. Its frozen earlier
source passed **92/94 suites**; app capture and resize-observation assertions
failed under instrumentation. No ASan/UBSan diagnostic was observed. A separate
leak-runtime probe hit the environment's ptrace restriction, so the full run
explicitly disabled leak detection. This is not a full acceptance or leak pass.

[Output removal](STANDALONE_DEVICE_REMOVAL.md) is now restricted to the actual
open SDL output handle. The old application-source probe reproduced unrelated
removal closing active audio; the repaired probes pass. Independent maintained
acceptance observes three lifecycle cycles and 93 queued events, and root's
assembled device/allocation/removal gate passed **3/3** in 2.94 seconds. Handle
reuse remains explicit; physical disconnect/reconnect is not established.

Earlier published `219821d` retains its own Linux package audit and Native VST3
results. Its [downloaded package](reviews/STANDALONE_HOSTED_LINUX_ARTIFACT.md)
independently passed inventory/source checks and actual relocated ELF execution;
that binary requires GLIBC 2.38 and GLIBCXX 3.4.32. It does not qualify arbitrary
Linux compatibility or the later code. Earlier Windows/macOS test compilation
failures and [their repairs](reviews/STANDALONE_PORTABILITY_REPAIR.md) remain
historical evidence.

Native physical devices, latency/underruns, hotplug, high-DPI pointer
capture, screen readers and signed distribution remain unqualified. The two
existing hosted workflows succeeded at published contract/assets checkpoint
`96a37a977ef22b7adf38e1a841f57ffcf32519a7`; those results do not qualify later code.

## Parallel rotary foundation

The distinct [rotary session](development/2026-11-13-rotary/README.md) starts
from `96a37a9` with its own sixty-agent, ten-wave scope. Its first **12 actual
assignments** are complete. Six readers covered every PDF text page and selected
actual visuals. Wave 2 supplies the frozen [numerical contract](ROTARY_NUMERICAL_CONTRACT.md),
strict proposed [profile](ROTARY_PROFILE.md), independent [reference](ROTARY_REFERENCE.md)
and native [motion foundation](ROTARY_MOTION.md).

Profile admission passes 33 maintained methods and an explicitly separate
358-case schema audit. The independent reference passes 33 maintained methods
after correcting full-day Decimal decay representation; its original failing
cases remain in the record. Native motion has author checks; independent R2
acceptance and wave-3 geometry/history work are in progress. See the actual
manifest for running versus accepted assignments. No whole-renderer, audible
policy or physical acceptance is claimed at this checkpoint.

The [coherent wave-2 integration](reviews/ROTARY_WAVE2_INTEGRATION.md) passed
**81/81 Release suites** in 38.03 seconds; after integrating standalone commit
`219821d`, the combined source passed **85/85** in 38.91 seconds, zero failures.
The clean starting source passed [79/79 Release suites](reviews/ROTARY_BASELINE.md).
The wave-1 published tree and both successful hosted workflows are recorded
there. Scanner and native standalone development retain their separate ownership;
M5/M6 and measured-capture dependencies remain open under [ROTARY_SCOPE.md](ROTARY_SCOPE.md).

## Active scanner continuation

The new [scanner session](development/2026-11-13-scanner/README.md) has completed its first 20 distinct assignments; the combined stage and its independent tests are in progress in wave 4. Six fresh readers covered every atlas page; follow its [handoff](SCANNER_HANDOFF.md), actual manifest and [frozen numerical contract](SCANNER_NUMERICAL_CONTRACT.md). Frequency/process and rotor qualification are complete; full matched-step stage qualification is in progress.

| Current scanner evidence | Observed result |
| --- | --- |
| Graph admission | Strict 27-node, 50-passive, 19-output fixture/schema/compiler; all 50components and 19outputs independently match the atlas and primary paper. |
| Independent source review | Primary circuit/rotor figures corroborate the graph and 16-position traversal. The chosen phase origin is shifted by pi/8 from the paper; its approximate 6Hz does not verify 412rpm. |
| Independent AC references | 564 solves and 10,716 tap transfers; nodal residual at most 3.2486101684985267e-16. A separately implemented loaded-ladder recursion agrees within 5.6647284161045834e-14. |
| Maintained regression | 19 graph/compiler and 16 AC methods passed locally, including literal edges, rational DC, full-grid power/loading/polarity, same-DC/wrong-AC topology mutations and atomic failures. |
| Build admission | CMake generates native constants only after full graph validation. The default dry Engine, 45 parameters, existing state formats and native processing remain unchanged. |

Independent review found and repaired a schema-only duplicate-ID admission gap in assumption/unknown arrays; the compiler had already rejected those cases. The tests retain the regression. These results qualify nominal graph/reference engineering. The prepared 36-coordinate line, independent full-graph transient reference and rotor now exist. All 160,740 logical positive tap comparisons and 88 actual process carriers pass their G3 frequency budgets; independently tested rotor behavior passes G4. Full matched-step and combined-stage acceptance are in progress. No converged sideband, integrated host or measured-hardware pass is claimed.

**Observed numerical limit:** the separate G5 same-hertz grid fails at every investigated internal rate, including 1,536,000 Hz. The full comparison retains 40,786 failing tap comparisons across distinct rate/mode cases. No multiplier alone qualifies an audible policy. The module remains a documented nominal research implementation while an alternative realization/policy, converged transients, rotating output and actual filtering remain required. See [frequency qualification](SCANNER_AC_PARITY.md).

The [coherent line/rotor checkpoint](reviews/SCANNER_WAVE3_INTEGRATION.md) at `babb897`, tree `14572ab24e67489997cee20ae452c0635178dca0`, passed **77/77 Release suites** in 50.64 seconds, zero failures. It excludes unfinished combined-stage work.

The [coherent scanner foundation](reviews/SCANNER_WAVE2_INTEGRATION.md) at commit `74473fa` passed **73/73 Release suites**, zero failures, from a new detached-source build. The original local baseline passed 71/71 Release suites. The optional VST3 baseline built and its project native checks passed; an initially unbuilt SDK validator was built explicitly and its previously unrun gate then passed. Earlier pedal/native hosted results below remain qualification of their named revisions.

## Current position

The repository contains a working **nominal dry organ**, offline rendering and
evidence tools, and an actual headless VST3 prototype. It has two manuals,
25 independently held pedals and 91 shared, continuously running sources.
Nominal M1/M2 and a substantial M3 subset have software evidence; the complete
M3 console, scanner, AO-28, Leslie, physical calibration and production product
remain open. The [M0–M9 plan](PLAN.md) is the milestone authority, and the
[acceptance matrix](ACCEPTANCE_MATRIX.md) classifies each exit separately.

The user-requested [pedal/native session](development/2026-11-13-pedals/README.md)
has completed **60 distinct new worker assignments in ten logical waves of six**.
All sixty substantive results are accepted; no planned or running assignments
remain. The [final integration gate](reviews/PEDAL_SESSION_INTEGRATION.md)
passed the explicit sixty-complete check from a coherent 562-file source archive.
The [manifest](development/2026-11-13-pedals/assignments.json)
records actual states and links each substantive note; neither earlier
sixty-agent session is counted again. Six fresh readers covered all 500 atlas
pages and selected actual diagrams. Independent final review rechecked the PDF,
coverage and preserved source assets; external sources and every diagram have
not all been independently verified.

Start with the [operational handoff](PEDAL_HANDOFF.md) for exact setup, build,
render, trace, plot, install and native commands. The
[release assessment](RELEASE_READINESS.md) describes usable behavior and the
separate product gates. [NEXT_STEPS.md](NEXT_STEPS.md) names the first next change.

## Implemented behavior

| Area | Current contract |
| --- | --- |
| Shared engine and manuals | One 91-source frame per sample feeds both manuals and pedals; note events do not restart source phase. Four retained A/B registrations, routing-only Cancel, optional contact travel/partial-key targets and shared upper-B percussion are implemented. |
| Pedals | Typed 25-by-8 routing preserves all 200 positions, 195 connections, five null contacts and seven repeated-source pairs. Two named nominal mixtures use four shared bus excitations; positions 0–8 and default `00` are software controls, not measured footage responses. |
| State and identity | 45 permanent parameter records preserve every field of the previous 43. `B3CONTROLS3` writes control-only snapshots; versions 1/2 migrate explicitly to muted pedals. Source/profile/PDF/maps and original examples retain their identities. |
| Musical input | Separate bounded manual/pedal ownership and one combined transaction preserve original routing, overlapping owners and scoped releases. Whole-call rejection preserves Engine histories, ledgers and caller audio. |
| Automation and control exchange | Bounded sample-linear normalized curves, exact discrete thresholds, offset-N carry, stable ordering and whole-callback rollback are implemented. Four pending UI restores and coherent published controls avoid direct UI access to live Engine state under the stated ownership contract. |
| Offline evidence | Five native command-line tools, two bounded SVG plotters, schema-3 render bundles with strict historical schema-1/2 verification, same-frame pedal traces and a 23-file relocatable OfflineTools installation. |
| Actual VST3 | Original processor/controller UUIDs; Upper, Lower and Pedals event buses; 45 controls; float32 identical-channel dry stereo at 44.1/48/96 kHz; at most 65,536 frames. Generic host controls, strict state streams, explicit locked SDK acquisition and separate native tests/install/CI. |

The [three-second pedal phrase](../examples/demos/pedal-phrase-v1/README.md)
contains the actual 144,000-frame WAV, score, unchanged profile, source inventory,
seven analysis windows and schema-3 evidence. Independent replay checks exact
local block-partition output and deliberate corruption. All eight earlier
scores retained exact local WAV/PCM/common metrics in 24 baseline/current runs.
These are synthetic nominal-model results, with the recorded toolchain scope.

## Retained pedal baseline qualification

The latest code/test repair is published and fetched as
[`0ad7240a88803de9d97bc265a8fd2b6e5d5d7e2b`](https://github.com/tomasedisonn80/Hammond-B3-Organ/commit/0ad7240a88803de9d97bc265a8fd2b6e5d5d7e2b),
tree `41c0b421643d4076c65ecbac8a750b4aae4d5806`. Root verified exact remote/local
tree identity. The [repair record](reviews/PEDAL_REVIEW_REPAIR_INTEGRATION.md)
identifies the preceding qualifications and the only later non-documentation
changes: fresh Windows reparse rejection in bundle inventory, its regression,
and a portable thread helper in the native concurrency test. The
[fixture follow-up](reviews/PEDAL_PLATFORM_FIXTURE_REPAIR.md) fixes the later
macOS/Windows regression setup failures without changing production inventory. Production
Engine/processor/SDK/CMake/profile and retained musical/runtime fixture inputs
remain unchanged from W8.

| Evidence | Observed scope |
| --- | --- |
| [W8 local coherent integration](reviews/PEDAL_WAVE8_INTEGRATION.md) | 71/71 ordinary Release suites and 8/8 native suites; zero failures, disabled tests or skips. |
| [W8 hosted review](reviews/PEDAL_HOSTED_WAVE8_FINAL.md) and [retry/repair](reviews/PEDAL_REVIEW_REPAIR_INTEGRATION.md) | Linux, Windows and sanitizer core jobs passed; the actual macOS retry subsequently passed 71/71 and 548 Python methods. Linux/Windows native passed. The native macOS retry failed compilation before CTest because its standard library lacks the test's former jthread/stop_token types. |
| [Focused repair integration](reviews/PEDAL_REVIEW_REPAIR_INTEGRATION.md) | 44 Python methods across two CTest suites passed. Fresh native configuration/build and the repaired concurrency suite passed 1/1, including exception-unwind stop/join cleanup. All 549 tracked source bytes/modes matched the recorded repaired tree. |
| [Final platform audit](reviews/PEDAL_FINAL_PLATFORM.md) | At `0ad7240`, core [43424724290](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43424724290) passed all four jobs: 71/71 suites, including 549 methods across 33 Python suites, per job. Native [43424724580](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43424724580) passed Linux 8/8, macOS 7/7 and Windows 7/7. Zero failed/disabled/skipped cases. Ten ZIPs and all 16 native payload files were independently verified. The real two-junction Windows regression and all native cleanup probes passed. |
| [Actual hosted Linux artifact execution](reviews/PEDAL_HOSTED_RUNTIME_FINAL.md) | The W8 downloaded module, distinct from the local build, passed ABI, behavior and dense automation gates. ABI compared 229,725 frames with zero maximum audio error; loader tracing proved resolution inside the actual artifact. |
| [Fresh setup/relocation](reviews/PEDAL_CLEAN_SETUP_FINAL.md) | Unicode/space-path builds and moved offline/native prefixes worked with original source/build paths unavailable; the moved actual Linux module passed ABI execution. |
| [Core allocation](PEDAL_REALTIME.md), [native allocation](VST3_REALTIME.md), [native concurrency](VST3_CONCURRENCY.md) | 180 core and 133 actual Linux native API regions observed zero replaceable C++ allocations/deallocations. Finite loaded-module concurrency workloads passed Release and fully instrumented TSAN under their recorded assumptions. |

The actual SDK validator reports **47 passed, zero failed, exit 0**, while its
complete logs retain 16 teardown diagnostics, nine unsupported-rate `ERROR`
messages and 15 float64 information messages. This is a scoped validator result,
not a warning-free log or DAW qualification. The independent harness separately
checks the supported lifecycle. Allocation/concurrency results do not establish
all allocations, locks, scheduler histories or audio-device deadlines.

## Next implementation and remaining product gates

The next task is the prepared 36-coordinate line runtime and independently stamped transient reference, followed by warp-aware AC/state tests, rotor modes and a declared audible-rate policy. The graph/compiler and independent AC references are implemented and reviewed; their actual commands and source identities are in [SCANNER_HANDOFF.md](SCANNER_HANDOFF.md). [SCANNER_NUMERICAL_CONTRACT.md](SCANNER_NUMERICAL_CONTRACT.md) separates discrete parity, full-band audible policy and later Engine/native integration. The original [scanner gate](M3_REMAINING_AND_SCANNER_GATE.md) retains the detailed physical and architectural requirements.

Physical M3 work remains: preset latch/loading behavior, continuous drawbars,
switching bandwidth, loaded expression and the pedal reactor network. M5–M7
require connected revision-specific organ/Leslie circuits and rotary acoustics;
M8 requires actual admitted captures and held-out calibration. M9 still needs
DAW project save/reopen, audio-device/standalone operation, accessible custom UI,
runtime distribution, signing and release qualification. The actual SDK-default
Windows icon, project-license decision and research/runtime rights remain in the
[dependency inventory](DEPENDENCIES_AND_RIGHTS.md), not silently cleared.

## Durable handoff and preserved history

[AGENTS.md](../AGENTS.md) requires every future agent to read current status,
next steps, plan and relevant source; claim a bounded scope; preserve identities
and unrelated work; retain actual commands/results/failures; update the shared
handoff; and commit/push completed authorized work with an expected-head guard.
Publication and product/fidelity claims require their own observed evidence.

The detailed chronological record is in [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md)
and the [current session ledger](development/2026-11-13-pedals/README.md).
The [original session](development/AGENT_LEDGER.md) and
[console continuation](development/2026-11-13-continuation/README.md) preserve
both earlier sixty-agent histories. Their dated pending tasks and test counts
remain historical; use the current documents above to resume.
