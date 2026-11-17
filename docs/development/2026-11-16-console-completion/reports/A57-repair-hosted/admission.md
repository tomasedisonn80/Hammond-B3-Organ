# A57 successor native qualification — repair source d2ed03b9

## Decision

**This repair source is not admitted across the required native matrix.** All six original jobs and every recorded step are terminal. Windows now compiles past the P1 helper, but its acceptance step fails three of 78 CTests. Four other normal families passed 78/78; strict sanitizers passed exactly 41/41. Native run `44034656779` concludes failure, attempt 1. No earlier result has been transferred to this source.

This is a follow-up by existing worker A57, `/root/w10_a57`, wave 10, with no additional agent credit. All accepted first-source A57 records remain immutable. This directory contains only successor evidence and review; root owns source repair, acceptance and publication. A57 has performed no local application/build/test execution, source edit, Git operation, CI rerun, or deadline change.

## Exact publication and execution

| Identity | Observed value |
| --- | --- |
| Actual remote commit | `d2ed03b94114e35d0caa65968d11afe896a5e9f5` |
| Tree | `45f3f2bc1bc844061be7d1303b13b10bfaba9938` |
| Sole parent | `cf87a587d0002d106e5210b57a39fd1967245a8f` |
| Native workflow | [44034656779](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44034656779), attempt 1 |
| Workflow SHA-256 | `d298ac55d78ae242b97c5de73be138b4a87c4d4fb343872e58a5c0bd5dc08659` |
| Standalone CMake SHA-256 | `927f48c1feba27889a63c73d7b8223b40b33c8851a07ac3b7feec9a88e713e07` |

A57 independently verified the commit/tree/parent through GitHub and fetched the exact-source workflow, CMake, five repaired files, and both unchanged copied-state diagnostic readers. All nine inspected content hashes match the frozen identities in A59's repair admission. The five changed source snapshots are retained once; unchanged sources and policy refer to the immutable first-source A57 evidence by hash. The earlier local commit hint `5bd11be` was never used as the remote execution identity.

## Observed family results

| Family | Job | Original result |
| --- | --- | --- |
| Linux GCC, MIDI OFF | `133874509299` | 78/78 passed in 413.58 s; all 55 mandatory names; 17-file installed/staged payload |
| Linux GCC, MIDI ON | `133874509183` | 78/78 passed in 443.63 s; all 55 mandatory names; 21-file installed/staged payload |
| macOS ARM64 AppleClang, MIDI ON | `133874509422` | 78/78 passed in 412.98 s; all 55 mandatory names; 21-file installed/staged payload |
| macOS Intel AppleClang, MIDI ON | `133874509606` | 78/78 passed in 569.18 s; all 55 mandatory names; 21-file installed/staged payload |
| Windows MSVC x64, MIDI ON | `133874509242` | **75/78 passed; three failures**, 550.83 s; build succeeded |
| Linux GCC ASan + UBSan + leaks, MIDI OFF | `133874509009` | Exactly 41/41 passed in 937.81 s; strict instrumentation and final source reverification passed |

Original provenance identifies Windows Server 2022 AMD64 with MSVC 19.44.35230.0 and Python 3.12.10; macOS ARM64 15.8.2 and Intel 15.7.9 with AppleClang 17.0.0.17000013 and Python 3.12.10; Linux X64 with GCC 13.3.0 and Python 3.12.16. The sanitizer's compiler/Python versions are read from its retained toolchain log. Actual runner IDs/names, image versions, compiler paths, start/end times, and full step states are recorded per job. Normal MIDI backends are ALSA, CoreMIDI and WinMM as appropriate; MIDI-OFF jobs retain the unavailable backend.

Intel preset raster passed in 21.63 seconds under its unchanged 30-second limit. The four successful normal families and the sanitizer family have zero disabled tests, zero CTest skips, and no method-level skip lines. All 431 cross-platform CTest executions are accounted for: 428 passed and three failed, all on Windows. This execution count does not turn the failed matrix into an admission. Every family's full original log and original diagnostics ZIP are retained. All new Windows discovery names, passing and failing results, conditional skips and downstream skipped steps are retained separately.

All five normal families actually ran the repaired source-only Python suites inside their original CTest invocation: 45 capture methods, 24 header-comparator methods, and 54 P1-comparator methods passed. All six families executed and passed the five LibraryModel suites. The five families with successful numerical gates evaluated all 18 title cases, all 103 H1 inequalities, and all 191 P1 checks including 62 numerical screens. The Windows distinctions below remain explicit.

## Windows: actual copied-state difference

The failure-only diagnostics now execute and identify the first mismatching node:

| Failed CTest | Exact emitted difference | Observed consequence |
| --- | --- | --- |
| `test_standalone_title_density` | `copied view controls differs; view.controls.drawbars[0][1]: list lengths 0 / 9` | Zero of 18 numerical cases evaluated |
| `test_standalone_header_statistics` | `complete canonical copied session differs; session.controls.drawbars[0][1]: list lengths 0 / 9` | Zero of 103 inequalities evaluated |
| `test_standalone_performance_plate_numerical` | Summary: 192 checks evaluated, one failed; 62/62 numerical screens passed | The failed non-screen check is not identified by retained stdout |

The diagnostic implementation first checks identical Python types, then reports list lengths. Consequently, the observed title/header nodes are actual Python lists with value `[]`, compared with expected lists of length nine. The messages establish an empty decoded second bank for the first manual at the comparison boundary. They do not establish a compiler bug, in-memory ControlSnapshot corruption, or the exact emitter/runtime cause. No scalar value or floating-point mismatch is inferred.

The native H1 fixture independently passed 48 cases, 10,542 checks and 95 helper probes. The repaired P1 fixture passed 34 cases, 53,648 checks and 61 helper probes. P1's 62 numerical screens passed even though its complete gate failed. Title and H1 numerical criteria did not run, so their failures cannot be described as numerical threshold failures.

The complete original Windows job log is 659,407 decoded UTF-8 bytes with SHA-256 `d4c08f3bde380b7f69fdf8e26fde70b6a326125e4624f4713062036a341351fc`. Original diagnostic artifact `14307123053` is 179,500 bytes, SHA-256 `18d22990fc61b0dd3cc46f14be794b03da68346a26ca39c1165b0a355cead25a`; its digest matches GitHub metadata. Its 42 members include CTest discovery, full verbose logs, JUnit, LastTest/LastTestsFailed, compiler, backend and source provenance. They do **not** include rejected raw frame headers, P1 captured stdout streams, or the temporary full P1 report. The single P1 failed check identifier therefore remains unavailable from original retained evidence.

Windows's repaired Python suites actually passed all 45 capture methods, all 24 header-comparator methods, and all 54 P1-comparator methods. All five LibraryModel CTests passed. JUnit reports zero skipped CTests; the full verbose log records one inner FIFO subcase skip in `test_standalone_replay_boundaries`, because FIFO creation is unsupported on the platform. This conditional coverage limit is preserved explicitly.

The build and backend verification steps passed. After acceptance failed, final source/dependency reverification, relocated package smoke, and successful package upload were skipped. The always-run diagnostics upload succeeded. No failed stage was retried, and no package qualification is claimed for Windows.

## Preserved policy and evidence boundaries

The exact workflow and CMake retain the first-source [policy inventory](../A57-native-hosted/source-policy-preflight.json): five normal families, all 55 mandatory platform names, and exactly 41 strict sanitizer gates mapped to 37 build targets. Normal jobs retain 40-minute budgets; sanitizer retains 35 minutes. CTest remains verbose, serial, `--no-tests=error`, with global 180-second timeout and unchanged explicit per-test deadlines. Normal preset raster remains 30 seconds. The five LibraryModel tests inherit the global timeout. No test, method, numerical bound, input pin or expected copied-state record has been relaxed by this review.

Strict sanitizer settings remain ASan `detect_leaks=1:halt_on_error=1`, UBSan `print_stacktrace=1:halt_on_error=1`, and LSan `exitcode=23`. The observed 41 selected gates contain no disabled tests or sanitizer-environment overrides. Original instrumentation records and the retained compile database verify 291 selected compile commands across 44 target groups with both address/undefined sanitizers and frame pointers; all 196 selected SDL C objects are instrumented; every selected target has nonempty instrumented objects. Seven archives have ASan/UBSan symbol references, and all 37 executable link commands and retained runtime records contain both sanitizers without missing dependencies.

The exact 41-test/37-target mapping and 63-input inventory match the unchanged policy. Comparing original hosted provenance against the immutable first-source provenance identifies exactly the five admitted repaired inputs and 58 unchanged inputs; no later local candidate bytes were used. Actual CTest output and all seven retained calibration stderr streams contain no sanitizer diagnostic. Ten calibration subprocesses, seven native lifecycles and two expected application-level failures are recorded. Final source and locked SDL reverification passed.

Observed sanitizer CTest durations remain within unchanged explicit limits: H1 fixture 145.80 s of 480 s, P1 fixture 86.85 s of 480 s, scaled view 108.23 s of 360 s, and preset raster 86.51 s of 300 s. These are observed CI durations, not physical timing or performance qualification. The original job completed without timeout, cancellation or retry.

The machine-readable [report](report.json), [Windows diagnosis](windows-copied-state-diagnosis.json), [source identity](source-identity.json), [artifact index](artifacts-index.json), and per-job receipts preserve what actually executed. The six complete original decoded job logs total 6,421,827 bytes, compressed to 704,703 bytes; the six original digest-verified diagnostic ZIPs total 2,048,394 bytes. Four successful package artifacts are recorded by API metadata; their binaries were not downloaded. Unchanged first-source policy and source evidence are referenced by hash instead of copied.

A single in-progress Windows log request returned GitHub 404 BlobNotFound; that availability observation is retained and is not treated as a job failure or CI retry. The full terminal log was fetched once it became available. Final exact-head API retrieval confirms one Native attempt, all six jobs terminal, and the other two exact-head workflows also terminal. Their substantive qualification belongs to their respective reviewers.

Root subsequently began a separate indexed-array working candidate. The [dated notice](later-working-candidate-notice.json) explicitly excludes those later local bytes from this source-bound receipt. A57 independently rehashed all 62 files in the first-source evidence inventory plus its accepted report/review/note references; all remain byte-identical.

Earlier `6287055` copied-state failures and `cf87a587` P1 compilation failure remain intact in the first-source evidence. This source's new failures remain intact as well. Any later source needs its own publication identity and execution. Candidate-only P1 screens do not establish paired before/after admission, native LibraryModel boundary suites do not qualify a completed library browser/main integration, and dummy/software or substituted MIDI tests do not qualify physical hardware, driver timing, accessibility, DAW use, callback retirement, physical fidelity, signed release, or literal whole-interface 1:1. Those limits remain separate and unwaived.
