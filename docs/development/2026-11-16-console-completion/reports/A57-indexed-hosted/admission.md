# A57 indexed-array source: Native hosted admission

**Decision: admit the six Native standalone hosted families for published source `54859886268ce83c36f359c43327f7c72a77ae82`, run `44038196285`, attempt 1.** All six jobs and every step are terminal. The five ordinary jobs each passed 78/78 CTests; the strict Linux sanitizer job passed 41/41. This is 431/431 CTest instances across the six jobs, with zero failed or skipped CTests. The one Windows FIFO subcase skip remains disclosed below.

This receipt applies only to that published source. Root's pending merge, additional Python admission changes, and any later publication require their own source-specific execution. This is a follow-up by the same actual A57 worker in wave 10 and adds no ledger worker credit. The accepted cf87 and d2ed reports, their original failures, and their retained evidence remain immutable.

## Exact source and workflow

The commit API independently identified tree `f5f8f037af301f8b1ff5b9b4a00ff5581647667a`, with ordered parents `d2ed03b94114e35d0caa65968d11afe896a5e9f5` and `ea02c5465b6c6a896cbbc83b55479d6f62bbf8c9`. A head-SHA-filtered run lookup identified the Native standalone run at this exact commit. Its final API result is success, attempt 1. The all-attempt jobs response contains exactly the six jobs reviewed here; there is no hidden cancelled or failed attempt in that response. Initial and terminal API responses are retained in `source-identity.connector.json.gz` and `terminal-observation.connector.json.gz`.

Exact-commit file API reads independently verified the workflow and standalone CMake bytes against the immutable policy receipt:

| Input | SHA256 |
| --- | --- |
| `.github/workflows/standalone.yml` | `d298ac55d78ae242b97c5de73be138b4a87c4d4fb343872e58a5c0bd5dc08659` |
| `apps/standalone/CMakeLists.txt` | `927f48c1feba27889a63c73d7b8223b40b33c8851a07ac3b7feec9a88e713e07` |
| Indexed footage fixture | `9e3a8fb643194e8ce4dcefb8059e82fef2b0140183c9175449098bf8941a2ecb` |
| Indexed H1 fixture | `8c8226b04931569cdbff78cddcfd6241fd334c1f15c764a04d016d958bc912aa` |
| Indexed P1 fixture | `026489d127d586c8c18384f7064e13f068f400cf08b87099d8c7f03066fe3ec5` |

The commit diff against d2ed contains nine test/fixture/comparator files. Each of the three C++ fixture changes replaces the shared range traversal with an indexed traversal of `values.size()` and `values[index]`. The two standalone Python readers change only their exact frozen fixture SHA256 constants. Their copied-state equality checks and numerical functions retain the d2ed logic. The published P1 comparator admits the exact indexed fixture through complete byte reversal to the already admitted helper-else predecessor; its numerical screens retain their existing bounds. The other published changes extend source admission and source-only comparator tests. The API file bodies and hashes are recorded in [source-identity.json](source-identity.json) and `changed-sources.connector.json.gz`.

Unchanged workflow/CMake bodies are referenced by their existing hashes rather than copied again. No later working-tree bytes were substituted for the published files. The strict lane's original 63-file provenance independently has exactly nine changed hashes against its d2ed predecessor; each of those nine equals the corresponding exact-commit API body. The remaining 54 hashes are unchanged.

## All six actual results

| Family | Job | CTests passed | Required names present and passed | CTest wall time |
| --- | ---: | ---: | ---: | ---: |
| Linux GCC, MIDI OFF | 133886098757 | 78/78 | 55/55 | 475.22 s |
| Linux GCC, MIDI ON | 133886098388 | 78/78 | 55/55 | 445.96 s |
| Windows MSVC x64, MIDI ON | 133886098445 | 78/78 | 55/55 | 415.80 s |
| macOS ARM64 AppleClang, MIDI ON | 133886098398 | 78/78 | 55/55 | 430.96 s |
| macOS Intel AppleClang, MIDI ON | 133886098331 | 78/78 | 55/55 | 537.55 s |
| Linux GCC ASan, UBSan and leaks | 133886098061 | 41/41 | 41/41 | 943.85 s |

The ordinary runners actually report Linux x86_64 with GCC 13.3.0 and Python 3.12.16; Windows Server 2022 AMD64 with MSVC 19.44.35230.0 and Python 3.12.10; macOS ARM64 15.8.2 and Intel 15.7.9 with AppleClang 17.0.0.17000013 and Python 3.12.10. Both ordinary Linux jobs used the Azure 7.0.0-1017 kernel/image `20261111.370.1`. The sanitizer runner used the AWS 7.0.0-1014 kernel/image `20261111.127.1`, with GCC 13.3.0 and Python 3.12.16. Windows image `20261112.366.7`, ARM image `20261104.0514.1`, and Intel image `20260824.0482.1` are recorded in the original provenance.

Each ordinary job executed the source-only capture, H1 comparator, and P1 comparator suites with **45, 32, and 64 methods**, respectively. These counts belong to source 548 and must not be replaced with counts from root's additional pending Python changes. All five LibraryModel/recall/roundtrip/session/storage suites passed in every family, including the strict lane. The complete per-test names, result, deadline, duration, and serial property are in each `job-…-review.json`; original discovery JSON, XML, verbose stdout, and LastTest logs remain in the diagnostic ZIPs.

## Windows copied-state and P1 result

Windows compiled the complete selected application and fixture set, including the P1 helper and indexed emitter. Backend verification, acceptance, source/dependency re-verification, relocation smoke, diagnostic upload, and package upload all succeeded.

The actual copied-state guards now pass, so the job reaches the previously blocked numerical evaluation:

| Gate | Actual source-548 Windows result |
| --- | --- |
| Title density | All 18 cases evaluated and passed |
| Native H1 fixture | 48 cases, 10,542 checks passed |
| H1 statistics | Complete canonical protocol and copied-state checks passed; 103/103 inequalities evaluated and passed |
| Native P1 fixture | 34 cases, 53,648 checks passed |
| P1 numerical | 191 evaluated checks, zero failed; all 62/62 candidate screens passed |

The original d2ed Windows receipt remains unchanged: it reported `view.controls.drawbars[0][1]: list lengths 0 / 9` for title, `session.controls.drawbars[0][1]: list lengths 0 / 9` for H1, and one unidentified non-screen P1 failure. That d2ed job had 75/78 CTests passing. Its failed P1 summary counted 192 checks, while the successful d2ed Linux job already counted 191. Source 548's 191 passing checks therefore match the preceding successful count; its 62 numerical screens all remain present and passing. The earlier cf87 P1 compile failure also remains preserved separately.

This establishes successful execution of the indexed successor through the previously failing Windows boundaries. It does not establish a precise compiler/runtime cause for the earlier empty nested arrays. CI did not upload the raw title/H1/P1 frame headers or the entire temporary P1 report. The complete available job stdout and diagnostic artifacts are retained, and no missing payload is reconstructed or invented. See [windows-copied-state-result.json](windows-copied-state-result.json), [the immutable d2ed diagnosis](../A57-repair-hosted/windows-copied-state-diagnosis.json), and [the immutable cf87 report](../A57-native-hosted.json).

All six new families report the same successful headline numerical coverage: title 18 cases, H1 103 inequalities, P1 191 checks and 62 screens. The full emitted numerical reports are retained separately as `job-…-numerical-reports.json.gz`, while their original text remains in the lossless job logs and ZIPs.

## Strict sanitizer provenance

The retained strict-lane evidence was inspected independently of the green job status. Its 41 discovered test names, test-to-target mapping, 37 built executable targets, and 63 source-input names exactly match the unchanged policy.

The compile database contains 411 generated entries. The 291 entries belonging to the 44 selected compiled groups match the recorded source lists, use both address/undefined sanitizers and frame pointers, and have corresponding nonempty instrumented object counts. This includes all 196 selected SDL C sources and 196 SDL instrumented objects. The retained CI instrumentation record checks ASan/UBSan references in seven archives. All 37 executable link records use the sanitizer flags; all 37 retained runtime-library records contain both ASan and UBSan with no missing library. The source and locked SDL2 re-verification step succeeded after acceptance.

The actual environment remains `ASAN_OPTIONS=detect_leaks=1:halt_on_error=1`, `UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1`, and `LSAN_OPTIONS=exitcode=23`. None of the 41 selected tests is disabled or supplies a sanitizer-environment override. No sanitizer diagnostic occurs in the actual CTest output or seven retained calibration stderr streams.

Native calibration exercised 10 subprocesses and seven lifecycles. Its two deliberately failing application replays still return their expected failure status and pass the common assertions; their original stderr is retained and explicitly identified in `instrumentation_review.calibration_stderr`. These expected application failures are not hidden or relabelled as sanitizer findings. System libraries were not rebuilt. The calibration boundary remains the real application/adapter with SDL dummy callbacks and a substituted MIDI dependency; it does not qualify physical devices or driver timing.

## Deadlines, exclusions, and skips

The workflow and CMake policy are unchanged: ordinary jobs have a 40-minute budget, the strict job 35 minutes, and CTest uses verbose serial execution, `--no-tests=error`, and a 180-second global timeout. The selected timeout and serial properties of every new CTest match the corresponding d2ed record. No timeout, count, failure predicate, or retry policy was weakened by this review.

| Selected gate | Ordinary deadline | Strict deadline | Actual strict duration |
| --- | ---: | ---: | ---: |
| Title density | 90 s | 240 s | 16.64 s |
| H1 fixture | 180 s | 480 s | 146.28 s |
| H1 statistics | 90 s | 240 s | 2.02 s |
| P1 fixture | 180 s | 480 s | 87.68 s |
| P1 numerical | 180 s | 480 s | 2.29 s |
| Scaled view | 60 s | 360 s | 108.88 s |
| Preset raster | 30 s | 300 s | 86.93 s |
| Native calibration | 90 s | 180 s | 21.15 s |

The Intel ordinary preset raster took 18.36 seconds under its unchanged 30-second deadline. Child-process limits remain title 20 seconds; H1 20 ordinary/60 strict; P1 60; native calibration 15; and replay/semantic paint boundaries 12 ordinary/30 strict. Full bounds and the complete mandatory-name lists remain in [the immutable source policy](../A57-native-hosted/source-policy-preflight.json).

Windows has one intentional FIFO subcase skip because FIFO creation is unsupported. Both the subcase line and `OK (skipped=1)` are retained; those two lines describe one skip. Its containing replay-boundary CTest passed. The other families have no method-skip lines. All six XML files report zero skipped and zero disabled CTests.

The ordinary `test_standalone_midi_backend_quarantine` retains its existing `ASAN_OPTIONS=detect_leaks=0:halt_on_error=1` property. This test is excluded entirely from the strict 41-test lane. The ordinary override is disclosed; it is not used to describe the strict lane's leak policy. OS-inapplicable setup/configuration steps, and external RtMidi acquisition in MIDI-OFF, are the only skipped workflow steps. Every selected acceptance, post-acceptance source verification, and applicable package step completed successfully.

## Packages, retention, and limits

Each ordinary job stages and relocates its exact installed payload, passes help and the 600 ms dummy smoke, and uploads a package. The staged byte inventory exactly equals the installed payload: 17 files for MIDI-OFF and 21 for each MIDI-ON job. Retained smoke JSON confirms dummy audio/video, software rendering, successful note-on/release observation, and completed shutdown. These are software smoke results.

Six diagnostic ZIPs were downloaded once and checked against their API byte counts and SHA256 digests. Together they retain 2,254,750 bytes. The six complete decoded original job streams contain 6,566,664 UTF-8 bytes and are retained losslessly in 730,885 gzip bytes. Each decompressed stream was checked against its original connector envelope without line normalization or clipping. Original full job/step metadata, discovery JSON, XML, provenance, compiler evidence, numerical output, and available stderr remain available. Five successful executable-package artifacts are recorded by API identity/digest; their payload ZIPs were not redundantly downloaded because exact installed/staged inventories and smoke diagnostics are retained in the diagnostic ZIPs. See [artifacts-index.json](artifacts-index.json).

All 62 inventoried files in the accepted first-source directory and all 53 in the d2ed repair directory rehash to their recorded values. See [immutable-prior-evidence.json](immutable-prior-evidence.json). This follow-up made no production, test, workflow, navigation, Git, index, or ref change; performed no local native build or application test; and issued no CI rerun, cancellation, or retry.

This admission covers the six stated hosted families at source 548 only. It does not claim physical MIDI/audio/display qualification, driver timing, OS callback retirement, accessibility, native browser/main integration, DAW acceptance, physical Hammond fidelity, signed release status, or literal whole-interface 1:1 completion. Those boundaries remain separate and unwaived.

The machine-readable result is [report.json](report.json). Every retained file is listed with byte size and SHA256 in [evidence-inventory.json](evidence-inventory.json).
