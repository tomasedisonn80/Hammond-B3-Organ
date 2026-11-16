# Initial hosted admission: streaming/material source

**A48, Wave 8, 16 November 2026. Decision: admit the observations below; the
initial hosted qualification remains failed.** All thirteen jobs completed:
twelve succeeded and Windows core Release failed. No retry, waiver, repaired-source
qualification or all-green result is recorded here.

The observed commit is
[`af2b74760ee195c9497b314a1a29172f5238dd44`](https://github.com/tomasedisonn80/Hammond-B3-Organ/commit/af2b74760ee195c9497b314a1a29172f5238dd44),
tree `fb7d9ef7d1fcf24a70395c0671b75eb9c31558d4`, parent
`4aac394cde4da40906b615573a8779aee2d9a37a`. A48 independently fetched each run's
metadata, all returned job summaries/steps and all thirteen decoded job logs
through the owner's read-only GitHub connector. The retained observation is
dated `2026-11-16T01:13:35.730Z`. Each run is a completed `push` on `main`,
**attempt 1**, at that exact commit/tree:

| Workflow | Provider run | Conclusion | Jobs |
| --- | --- | --- | --- |
| CI | [43783034126](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43783034126) | failure | 4 success, 1 failure |
| Native VST3 | [43783034176](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43783034176) | success | 3 success |
| Native standalone | [43783034124](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43783034124) | success | 5 success |

The [machine-readable audit](../development/2026-11-15-streaming-continuation/reports/A48-hosted-audit.json)
and [compressed provider evidence](../development/2026-11-15-streaming-continuation/reports/A48-provider-evidence.json.gz)
retain exact job identities, successful/failed/skipped steps, numbered log
excerpts, complete observed CTest result lists, dependency-verification records,
source hashes and cross-checks against root's original completion receipt.

## All thirteen observed jobs

Times below are the logged CTest wall time, except the explicitly separate R4
full experiment's reported wall time. Test totals are actual executed selections;
they are not interchangeable with the local 210-test configuration.

| Job and provider evidence | Configuration | Observed result | Wall seconds |
| --- | --- | --- | ---: |
| [Core Linux GCC](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43783034126/job/133024355960) | Release | **185/185** | 95.73 |
| [Core macOS AppleClang](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43783034126/job/133024355982) | Release | **185/185** | 142.36 |
| [Core Windows MSVC](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43783034126/job/133024356072) | Release | **184/185; failure** | 251.43 |
| [Core Linux ASan/UBSan/leaks](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43783034126/job/133024356107) | **Debug**, sanitizer preset | **185/185** | 236.26 |
| [Complete R4 waveform, Linux](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43783034126/job/133024355788) | Release, full experiment target | `status: pass`, `mode: full`, `failures: []` | 620.224896503 |
| [VST3 Linux GCC](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43783034176/job/133024355801) | Release | **8/8** | 6.13 |
| [VST3 macOS AppleClang](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43783034176/job/133024355469) | Release | **7/7** | 4.33 |
| [VST3 Windows MSVC x64](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43783034176/job/133024355681) | Release | **7/7** | 6.02 |
| [Standalone Linux, MIDI ON](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43783034124/job/133024355923) | Release | **53/53** | 337.18 |
| [Standalone Linux, MIDI OFF](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43783034124/job/133024355755) | Release | **53/53** | 316.30 |
| [Standalone macOS, MIDI ON](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43783034124/job/133024355700) | Release | **53/53** | 317.35 |
| [Standalone Windows x64, MIDI ON](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43783034124/job/133024355471) | Release | **53/53** | 416.64 |
| [Native standalone ASan/UBSan/leaks](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43783034124/job/133024355787) | **Release**, MIDI OFF | **22/22** | 396.20 |

Observed compiler/configuration and version lines are retained per job in the
audit. The core, VST3 and standalone platform jobs report these tool versions:

| Platform | Compiler identification | CMake / CTest | Python |
| --- | --- | --- | --- |
| Linux | GNU **13.3.0** | **3.31.6 / 3.31.6** | **3.12.16** |
| macOS | AppleClang **17.0.0.17000013** | **4.4.5 / 4.4.5** | **3.12.10** |
| Windows | MSVC **19.44.35230.0** | **3.31.6 / 3.31.6** | **3.12.10** |

The R4 job separately reports GNU 13.3.0, CMake 3.31.6 and Python 3.12.16;
its acceptance is the full target, not another 185-test CTest pass. Actual
acquisition/configuration logs verify the source-locked SDL **2.32.10** at
`5d249570393f7a37e037abf22cd6012a4cc56a71`, RtMidi **6.0.0** at
`1e5b49925aa60065db52de44c366d446a902547b` where MIDI is enabled, and the VST3
SDK root at `3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96` with its four locked
submodules. The audited SDK lock names version **3.8.1**. Lock-file hashes and
observed dependency-verification log locations are in the audit; no artifact
bundle was downloaded.

## Retained Windows failure and the new causal suites

The Windows job's build succeeded, then `Run every registered Release test`
failed. The sole failing CTest is `python_test_contact_reference_install`,
specifically
`test_moved_package_runs_cli_and_full_study_admission_without_source_or_build`,
with `contact-switching: input changed after path preflight`. This is the existing
contact-reference package relocation gate. Its failure remains part of the
qualification; successful standalone/VST3 jobs do not clear it.

Root's [original failure receipt](../development/2026-11-15-streaming-continuation/reports/windows-core-af2b747-failure.json)
and [complete compressed failure log](../development/2026-11-15-streaming-continuation/reports/windows-core-af2b747.log.gz)
remain unchanged. A48 rechecked the retained decoded bytes: **526,325 bytes**,
SHA-256 `2858f8f90bb79736630bf72b0fdaca93156baf9f8496afe83cb7500adc47ba6d`.
The independent fetched result, failure text and 184/185 count agree.

All six new causal suites passed on Windows and in the other three core jobs:
`test_causal_contact_grid`, `test_causal_contact_grid_lifecycle`,
`test_causal_contact_grid_resources`, `python_test_causal_contact_grid_cli`,
`python_test_causal_contact_grid_differential` and
`python_test_causal_contact_grid_reference`. This supplies actual hosted
compile/runtime evidence for these selections, including Windows transport.
It supplies no converter, causal audio filter, live Engine route, physical
contact model or callback deadline qualification.

A45's I/O repair and A47's independent review belong to subsequent work. This
audit examines the immutable published source above, so it neither admits nor
qualifies their local repair. Any repaired publication needs its own source
identity and observed hosted results; the original failure must remain retained.

## Upper-rack coverage and preservation of earlier gates

`test_standalone_upper_rack_material_raster` passed in **all four native Release
jobs and the native sanitizer job**. Each printed the same fixture result:
protocol `upper-rack-material-v1.1`, **30 cases, 58,876,889 checks, 49 state
restorations, 15 clip companions, 216 opaque-child probes, 12 focus cases**,
with `status: passed`. The stated backend is **SDL software surface; fixed
copied state; no audio/window**. The sanitizer fixture completed in **42.28 s**.
These are hosted fixture observations, distinct from the earlier 96-pair raster
comparison and twelve application captures; they do not recreate or regrade
those separate evidence sets.

A48 compared the workflow and CMake blobs at the audited commit with its parent:

- CI, Native VST3 and `CMakePresets.json` are byte-identical to the parent. Their
  previous job/test selections remain in place.
- The native Release required-name set grows from **31 to 32**, solely by adding
  the Upper-rack fixture. All four actual Release jobs discovered and executed
  the same **53** `test_standalone_` names, including every required name.
- The native sanitizer mapping grows from **21 to 22** unique CTest names and
  build targets. Every old name-to-target mapping is unchanged, including
  `test_standalone_native_calibration=hammond_standalone_calibration_probe`.
  The actual 22 executed names exactly equal the published mapping.
- Every earlier sanitizer timeout remains unchanged. The added fixture has
  **90 s** ordinary CTest and **240 s** sanitizer limits. Required selections
  retain `--no-tests=error`; no gate or threshold was relaxed.

The complete old/new mappings, required counts, timeout dictionaries and exact
source hashes are retained in `source_checks` in the machine-readable audit.
These comparisons concern the immutable published blobs, not any later working
tree repair.

## Native sanitizer and product evidence boundaries

The native sanitizer job passes its source/instrumentation verification step
and prints discovery of exactly 22 built gates before running them. The retained
complete [native sanitizer log](../development/2026-11-15-streaming-continuation/reports/A48-native-sanitizer-af2b747.log.gz)
contains actual `-fsanitize=address,undefined -fno-omit-frame-pointer` compile
commands for SDL C, project C++, the Upper-rack fixture, its `InstrumentView.cpp`
and the native calibration driver. The exact-source verification step requires
the selected objects, six instrumented archives, linked ASan/UBSan runtimes and
required source membership, including the newly added painter/fixture pair.
Its provider step conclusion is success. No unobserved object count is inferred.

Observed policy is `ASAN_OPTIONS=detect_leaks=1:halt_on_error=1`,
`UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1` and
`LSAN_OPTIONS=exitcode=23`. Native SDL backend compilation is checked, while
execution uses dummy audio/video and the software renderer. System libraries
are not rebuilt under the project's sanitizer instrumentation. The calibration
gate uses the real application entry with a substituted MIDI dependency; it
does not establish actual OS callback retirement or hardware recovery.

Each VST3 job runs the actual module validator with **47 tests passed, zero
failed**. All three pass install, validator, controller, ABI, behavior,
automation and concurrency CTests; Linux also passes `test_native_realtime`.
That fixture name does not establish an audio-device deadline or a DAW journey.

The standalone Release logs report relocated help/dummy-smoke and archive-byte
checks: **20 installed files** for the MIDI ON packages, with observed compiled
backends **ALSA**, **CoreMIDI** and **WinMM**, and **16 files / MIDI unavailable**
for Linux MIDI OFF. These are software packaging/backend observations. They
do not qualify physical MIDI/audio/display devices, native semantic
accessibility, whole-interface 1:1 visual equality, signed distribution or
measured Hammond/Leslie fidelity. All M0–M9 exits remain binding.

## Audit method and handoff

A48 read the full `AGENTS.md` and M0–M9 plan and recovered the active scope,
checkpoint, ledger and relevant status/handoff records. Work ran from
`/workspace/scratch/177e78b1ac09/Hammond-B3-Organ`. Read-only inspection used
GitHub run GETs, workflow-job lists/logs, `git show`, the parent-to-source diff
and local JSON/gzip/hash/set checks. A48 performed no GitHub write, retry,
build, project test run, source edit or commit.

The evidence bundle retains all thirteen job summaries and useful numbered
log lines; only the native sanitizer full log is duplicated for this audit.
Root's original Windows failure log remains the failure source. Gzip round trips
and recorded hashes protect the retained bytes. The native sanitizer decoded
log is **999,586 bytes**, SHA-256
`7b058feda7b5b0c2cf3b928c93dfa61fd848178a790c563ab08e759572c08966`.

Root can use this review to replace stale pending-job statements with the
source-specific **12-success/one-failure** result, preserve the failure, finish
the separately reviewed repair and observe all required jobs at its eventual
published source. This review does not close the sixty-worker session or any
other owner's unfinished product gates.
