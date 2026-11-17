# Console native hosted admission — A57

## Current decision

**The published console source is not admitted across all six required native families.** All original jobs are terminal: Windows failed compilation in the new P1 fixture under the existing `/W4 /WX` policy; the other four normal families passed 78/78 CTests each; Linux sanitizers passed exactly 41/41. These are source-bound results, not an approval of the whole interface, physical hardware behavior, or a signed release.

This review is performed by actual worker `/root/w10_a57`, wave 10. A57 has not built or run the application or tests locally, changed source or test policies, used Git, triggered a CI rerun, or published a revision. Root owns repair, acceptance, and publication.

## Published source and original execution

| Identity | Independently observed value |
| --- | --- |
| Commit | `cf87a587d0002d106e5210b57a39fd1967245a8f` |
| Tree | `2565ac86f9d31b7ab9d24d0d5353289c2359bf12` |
| Ordered parents | `6287055a111dc4e2747564da3d48edc9b65e2e3e`, `8cd9034f7e1dd21dab373f0e4ad0d1be0bab61e7` |
| Native workflow run | [44030833294](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44030833294), attempt 1 |
| Workflow | `.github/workflows/standalone.yml`, SHA-256 `d298ac55d78ae242b97c5de73be138b4a87c4d4fb343872e58a5c0bd5dc08659` |
| Standalone CMake | `apps/standalone/CMakeLists.txt`, SHA-256 `927f48c1feba27889a63c73d7b8223b40b33c8851a07ac3b7feec9a88e713e07` |

The commit API, exact-revision file API, run `head_sha`, every job `head_sha`, and retained hosted provenance bind the evidence to this source. The workflow and standalone CMake agree byte-for-byte with A57's prepublication inspection. The earlier local 46-build/78-test/15-capture acceptance and the predecessor's hosted runs are retained as separate evidence and confer no new-source qualification.

## Family outcomes

All six original jobs were confirmed terminal at 2026-11-17 06:42:36 UTC. Every recorded step is terminal, including the explicitly skipped steps. Native run `44030833294` concluded **failure**, attempt 1. All six complete original job logs and diagnostic archives have been reviewed; no rerun exists in the observed exact-head execution.

| Family / hosted runner | Job | Actual outcome | CTest / package evidence |
| --- | --- | --- | --- |
| Linux GCC, MIDI OFF / `ubuntu-24.04`, X64 | `133862109037` | Passed | 78/78, 412.88 s; all 55 mandatory names; 17 installed payload files; relocation smoke passed |
| Linux GCC, MIDI ON / `ubuntu-24.04`, X64, ALSA | `133862109056` | Passed | 78/78, 443.85 s; all 55 mandatory names; 21 installed payload files; relocation smoke passed |
| macOS AppleClang, MIDI ON / `macos-15`, ARM64, CoreMIDI | `133862109073` | Passed | 78/78, 454.22 s; all 55 mandatory names; 21 installed payload files; relocation smoke passed |
| macOS Intel AppleClang, MIDI ON / `macos-15-intel`, X64, CoreMIDI | `133862108651` | Passed | 78/78, 607.59 s; all 55 mandatory names; 21 installed payload files; relocation smoke passed |
| Windows MSVC, MIDI ON / `windows-2022`, X64, WinMM | `133862108913` | **Compilation failed** | 0 CTests executed; acceptance and downstream package gates skipped |
| Linux GCC ASan + UBSan + leaks / `ubuntu-24.04`, X64, MIDI OFF | `133862108476` | Passed | Exactly 41/41, 595.90 s; 37 build targets; strict instrumentation and source reverification passed |

Linux successful jobs used GCC 13.3.0 and Python 3.12.16. ARM64 used macOS 15.8.2; Intel used macOS 15.7.9. Both used AppleClang 17.0.0.17000013 and Python 3.12.10. The failed Windows job used Windows Server 2022 AMD64, MSVC 19.44.35230.0, and Python 3.12.10. Exact runner names, image versions, compiler paths, job and step timestamps, and all terminal conclusions are in the per-job receipts.

Intel preset raster passed in 22.89 seconds under its unchanged 30-second normal CTest limit. This observed pass does not erase an earlier timeout or authorize retrying a failed gate. The four successful normal jobs preserved their installed payload exactly during staging; the 17-file MIDI-OFF and 21-file MIDI-ON inventories and relocation output are retained. The successful package artifact IDs and digests are recorded, while package binaries were not downloaded for this review.

## Windows failure and unresolved copied-state boundary

The original new-source Windows log reports `warning C4702: unreachable code` at `apps/standalone/native_tests/test_standalone_performance_plate.cpp(50,1)`, promoted to `error C2220` by warnings-as-errors. Exact published source shows `p1_fixture_invoke_helper()` returning true inside its present-helper `if constexpr` branch, followed by the unconditional `return false` at line 50. Compilation finished with one warning and one error. This is a concrete fixture compilation failure; no timeout or numerical failure occurred at this source on Windows.

The acceptance step was skipped. Consequently, the newly published title/header failure diagnostics did not run, and the rejected copied-state scalar/path/type/value remains unknown. Final source verification, relocation smoke, and successful package upload were also skipped. The always-run diagnostics upload succeeded. A57 retained the complete 455,495-byte decoded UTF-8 job log (SHA-256 `580ad243484bb9cc5d8759ce5392abfdb31735255256ba83f6212b50c9b22fcc`) and the original 68,666-byte diagnostics ZIP, whose digest was checked against GitHub metadata.

At the distinct predecessor `6287055a111dc4e2747564da3d48edc9b65e2e3e`, Windows compilation succeeded and 66/68 tests passed. Title density rejected copied controls before evaluating any of its 18 numerical cases; header statistics rejected the canonical copied session before evaluating any of its 103 criteria. The H1 native fixture itself passed 10,542 checks. Those logs did not contain the rejected payload. Exact fixture serialization and Python validation were inspected, but neither a specific value/type mismatch nor a numerical cause was proved.

Root subsequently added first-difference diagnostics only on the existing failure paths of the two Python readers. A57's independent admission verified that equality predicates, expected records, numerical functions, bounds, process deadlines, and success behavior stayed unchanged. The new P1 compiler failure prevents observing those diagnostic paths on Windows in this run. Any repair needs a newly identified source and fresh execution; this run will not be retried or rewritten as a pass.

## Actual successful-job coverage

The four successful normal families agree across original CTest discovery JSON, verbose output, and JUnit on 78 executed names, zero disabled tests, zero skipped CTests, and no method-level skip lines. All 55 mandatory normal-platform gates are present. The sanitizer job independently agrees on its exact 41-name set, with the same zero-disabled/zero-skip result and no selected sanitizer environment overrides. Full verbose logs are retained because JUnit truncates long successful outputs at 1,024 bytes; numerical counts below were read from complete output.

| Gate | Actual output in each of the five successful families |
| --- | --- |
| Library model | 32 groups; 3,250 assertions; zero failed groups |
| Library recall | 9 groups; 743,728 assertions; 98 invalid snapshots; 72 presentation/owner contexts; zero failures; synthetic UiModel boundary inputs |
| Library round trip | 4 groups; 1,489 checks; 138 snapshots; 20 renders; real Session and filesystem; native browser explicitly unqualified |
| Library session | 12 groups; 42,634 assertions; 696 real snapshots; 150 renders; 428 accepted posts; 6,252 paired stereo samples; 10,101 phase checks; 60 percussion-history checks; zero failed groups |
| Library storage | 9 groups; 1,115 checks; zero failures; synthetic control proof and real filesystem |
| Title density | All 18 numerical cases passed; 44-case native inventory validated |
| H1 fixture | 48 cases; 10,542 checks; 163 paintings; 95 helper probes; passed |
| H1 statistics | All 103 inequalities evaluated and passed |
| P1 fixture | 34 cases, including 24 main cases; 53,648 checks; 111 paintings; 61 helper probes; passed |
| P1 numerical | Candidate-only frozen62 mode; 191 checks evaluated; zero failed; 62/62 candidate screens passed |
| Native calibration | 9 Python methods; 10 actual fixture subprocesses; 7 native lifecycles; 2 deliberately failed replays handled by the existing assertions |
| Replay / semantic paint boundaries | Two actual native subprocesses per gate, with emitted presentation visits and executable hashes retained |

These are regression and boundary results. Candidate-only numerical screens do not replace paired before/after admission, whole-interface visual review, measured performance or physical fidelity. Library tests do not establish a completed native library browser or its integration into `main`.

## Observed strict sanitizer instrumentation

The original sanitizer archive contains the full compile database, instrumentation JSON, all 37 runtime dependency records, selected discovery/JUnit/verbose output, and native calibration evidence. Independent inspection found 291 selected compile commands across 44 target groups, each carrying `-fsanitize=address,undefined` and `-fno-omit-frame-pointer`. All 196 selected SDL C objects were recorded as instrumented; every selected target group has nonempty instrumented objects. All seven recorded archives contain both ASan and UBSan references. All 37 executable link commands carry sanitizer flags, and each retained runtime record resolves both libraries with no missing dependency. The 37-target set, 41-test mapping, and 63-input provenance set match the recovered exact-source policy.

The complete CTest stream and all seven retained native-calibration stderr files contain no ASan, UBSan, or leak diagnostic. The two deliberately failed replays contain only their expected application-level failure messages and retain expected exit 1; their common assertions passed. Ten subprocesses, seven native lifecycles, and both deliberate failures are recorded explicitly. These use the real application/adapter and SDL dummy callbacks with a substituted MIDI dependency; system libraries were not rebuilt and hardware/driver timing remains unqualified. Final source and locked SDL reverification succeeded.

## Preserved execution policy

Normal jobs retain 40-minute budgets and the sanitizer job 35 minutes. Matrix fail-fast is false. CTest uses verbose output, `--parallel 1`, `--no-tests=error`, and global `--timeout 180`; explicit test deadlines continue to override that default. The five new LibraryModel suites inherit the global 180-second limit. There is no same-source automatic retry.

| Gate | Normal CTest limit | Sanitizer CTest limit | Child process limit, normal / sanitizer |
| --- | ---: | ---: | ---: |
| Preset raster | 30 s | 300 s | — |
| Workspace raster | 60 s | 180 s | — |
| Scaled view | 60 s | 360 s | — |
| H1 fixture | 180 s | 480 s | — |
| H1 statistics | 90 s | 240 s | 20 / 60 s |
| H1 grain bounds | 30 s | 90 s | — |
| P1 fixture / numerical | 180 s | 480 s | Numerical: 60 / 60 s |
| Title density | 90 s | 240 s | 20 / 20 s |
| Replay / semantic paint boundary | 60 s | 90 s | 12 / 30 s |
| Native calibration | 90 s | 180 s | 15 / 15 s |

The strict sanitizer selection requires exactly 41 gates, 37 build targets, and its retained 63-input provenance inventory. ASan is `detect_leaks=1:halt_on_error=1`; UBSan is `print_stacktrace=1:halt_on_error=1`; LSan is `exitcode=23`. The workflow checks real SDL C and project C++ object instrumentation, seven archives, 37 executable link lines and runtime dependencies, and the separate apron-fault seam. No selected test may disable itself or override the sanitizer environment. The intentional MIDI quarantine test is included in normal acceptance with its existing process-lifetime policy and excluded from this strict sanitizer set.

Previous failures, timeouts, and concurrency cancellations remain historical failures; normal preset raster's 30-second guard has not been relaxed. Current concurrency policy can cancel an older same-ref run. Every original job is now terminal, so a later publication cannot cancel this run; any later source still requires its own fresh qualification.

## Evidence and remaining limits

The machine-readable index is [A57-native-hosted.json](../development/2026-11-16-console-completion/reports/A57-native-hosted.json). Its evidence directory retains exact connector observations, complete decoded job logs compressed without line rewriting, original digest-verified diagnostics ZIPs, per-job reviews, full extracted numerical records, source identity receipts, the predecessor diagnosis, and the diagnostic-only source admission. The six original decoded job streams total 6,219,052 bytes and compress to 664,783 bytes; the six original diagnostic ZIPs total 1,937,290 bytes. Every stream and archive has a retained digest. Artifact retention on GitHub is 14 days; local retained archives preserve the original evidence beyond that service window.

The source keeps the nominal dry Engine, 47 parameter IDs, B3CONTROLS4 with readers 1–3, 91 shared free-running sources, and existing UUID boundary intact. This admission does not waive the unresolved literal whole-interface 1:1 requirement, physical MIDI/audio/display behavior, native accessibility, OS callback retirement, DAW qualification, physical fidelity, or signed-release gates. Root owns the next source repair and its admission.
