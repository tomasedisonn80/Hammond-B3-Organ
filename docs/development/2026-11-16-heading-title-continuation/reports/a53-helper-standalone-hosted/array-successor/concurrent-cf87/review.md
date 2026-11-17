# Concurrent cf87 standalone observation

## Disposition

The standalone workflow for source `cf87a587d0002d106e5210b57a39fd1967245a8f` finished with **five successful jobs and one Windows compilation failure**. All six jobs in run [44030833294](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44030833294), attempt 1, are terminal. This observation does not establish the state of other workflows, and it does not qualify the future reconciled source.

The exact tree is `2565ac86f9d31b7ab9d24d0d5353289c2359bf12`, with parents `6287055a111dc4e2747564da3d48edc9b65e2e3e` and `8cd9034f7e1dd21dab373f0e4ad0d1be0bab61e7`. The actual checkout output in every retained job log identifies cf87. The [run receipt](run-44030833294.json) preserves actual job IDs, runners, timestamps, all step outcomes and artifact metadata without account identity fields.

| Family | Job | Actual CTests | CTest seconds | Install/package outcome |
| --- | ---: | --- | ---: | --- |
| Linux GCC, MIDI ON | 133862109056 | 78/78 passed | 443.85 | 21 files, ALSA, relocation/archive assertions passed |
| Linux GCC, MIDI OFF | 133862109037 | 78/78 passed | 412.88 | 17 files, unavailable MIDI, relocation/archive assertions passed |
| macOS ARM AppleClang, MIDI ON | 133862109073 | 78/78 passed | 454.22 | 21 files, CoreMIDI, relocation/archive assertions passed |
| macOS Intel AppleClang, MIDI ON | 133862108651 | 78/78 passed | 607.59 | 21 files, CoreMIDI, relocation/archive assertions passed |
| Windows MSVC x64, MIDI ON | 133862108913 | Not executed | — | Compilation failed; later gates skipped |
| Linux GCC ASan/UBSan/leaks | 133862108476 | 41/41 passed | 595.90 | Sanitizer workflow has no package stage |

Every per-job JSON in this directory binds its complete original log, exact result rows, source checkout, compiler, native child counters, protocol summaries and actual API step outcomes. The [summary](summary.json) provides the compact source-specific disposition.

## Expanded inventory

The [inventory receipt](inventory.json) binds workflow SHA-256 `d298ac55d78ae242b97c5de73be138b4a87c4d4fb343872e58a5c0bd5dc08659` and CMake SHA-256 `927f48c1feba27889a63c73d7b8223b40b33c8851a07ac3b7feec9a88e713e07`. This workflow explicitly requires 55 names. Its normal filter actually discovers **78 tests: 75 standalone-prefixed tests and three Python comparator/capture tests**. The four successful normal logs contain exactly the same 78 names, each passed. The Windows build stops before discovery.

Compared with the earlier 68-test inventory, the added tests are five library model/session/storage/recall/roundtrip tests, the native P1 fixture, its numerical gate, and three Python tool suites. Registration-library coverage already existed. The sanitizer mapping contains **41 gates and 37 build targets**; the observed 41 result names exactly match that mapping. Future qualification must audit this expanded inventory rather than reuse the historical 68/34 counts.

The normal job allowance remains 40 minutes and the sanitizer allowance 35 minutes. P1 numerical binds the exact six-argument Python invocation with `--candidate-only --after <fixture>`, required labels, and a 180-second normal CTest bound. Both P1 sanitizer CTests have 480-second bounds. No bound was changed by this observer.

## Windows failure and its observation boundary

MSVC 19.44.35230.0 reports **C4702, unreachable code**, at `apps/standalone/native_tests/test_standalone_performance_plate.cpp(50,1)`, followed by C2220 because warnings remain errors. The actual build exits 1 under the existing `/W4 /WX` policy. The source's dependent `if constexpr` returns true for the present helper and is followed by an unconditional `return false;` at that line.

The [frozen failure-retention receipt](windows-build-failure-retention.json), SHA-256 `b6d8f2954ac90600862a9155572e3128eefaa449a82a44d15ccda553863f7f51`, binds the complete Windows log and exact original CRLF compiler/final-failure blocks, with separate readable LF views. This is the compile failure actually observed; it is independent of any prospective remedy.

No CTest ran. Compiled MIDI verification, the new failure-only title/header runtime diagnostics, source/dependency post-verification, installation/relocation and packaging were not reached. Although the P1 source contains a serializer analogous to the earlier H1/footage serializer, its malformed Windows runtime output is **unobserved** here. A54 owns the separate prospective source review; this report neither edits source nor admits a repair by analogy.

## Actual native, numerical and sanitizer evidence

All five successful jobs report title density 18/18 cases from a validated 44-case inventory; H1 material 48 cases, 10,542 checks, 163 paintings and 95 helper probes; H1 statistics 103/103 criteria; and grain bounds four cases/170 checks. The source-specific H1 canonical header hash is `1a7b0b316dc771428f2241eec9fbd25668ba337a6a2232b5787a2014f86eaaac`; the complete RGBA hash is `56392ccf2d9d3600533d08955879d43c4a916b720463f3c541d1113b4f854fb2`. No cross-source pixel equality is inferred.

P1 native reports 34 cases, 24 main cases, 53,648 checks, 111 paintings and 61 helper probes. P1 numerical reports mode `candidate-only-frozen62`, 191 evaluated checks with zero failures and all 62 frozen screens passing. That numerical mode captures one canonical candidate; it does not execute the complete paired 34-case comparison, timing study or visual acceptance. Its printed complete JSON is preserved in the job log. A53 did not download the separately named temporary report file.

The sanitizer's successful instrumentation step checks actual SDL C and project C++ object files, compile flags, seven archives, 37 executable identities and linked ASan/UBSan runtimes. It checks P1's real painter inclusion and linked inputs, library model/core links, private production support MIDI=0, and isolated calibration-probe MIDI=1 with its fake dependency. It then verifies exact enabled test commands, finite bounds and the absence of per-test sanitizer overrides.

The job uses `ASAN_OPTIONS=detect_leaks=1:halt_on_error=1`, `UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1`, and `LSAN_OPTIONS=exitcode=23`. Its explicit postcheck confirms ten calibration subprocesses, seven lifecycle scenarios, two deliberately failed replays and clean sanitizer diagnostics for captured failure streams. Both real-application paint gates execute two children apiece against instrumented application SHA-256 `b7f298ddaaef04cd376020ba488d68777dc4d074cc1ab7029713667de4029de7`. Final source and locked-SDL reverification succeeds. The normal successful jobs likewise execute their native children and source/dependency postchecks.

## Packaging, retention and remaining limits

The four successful normal jobs pass all eight install unittest methods and their final packaging stage. The exact install source includes Unicode `prefix Ω` and `relocated Ω` paths, custom directories, calibration and unchanged-payload checks; individual method names are not printed in these logs. The executed workflow verifies staged member bytes, relocation, help, a 600 ms dummy smoke, capability metadata and archived-byte equality. The evidence establishes those executed assertions. A53 inspected artifact API metadata and did **not** directly download or independently unpack these packages.

[The complete-log manifest](complete-log-archives.json) retains all six original decoded logs losslessly in deterministic gzip files: **6,219,052 decoded bytes and 664,783 stored bytes**, with original newlines, individual hashes, empty gzip filename, mtime zero and verified round trips. Original frozen Windows blocks remain untouched.

Intel's preset raster passes here at 22.89 seconds under the unchanged normal 30-second guard. This is a separate source-specific observation; the earlier 03c timeout remains failed and no timing cause, repair or stability claim follows. Focused ea02 Windows success also remains a separate two-CTest/capture result. A reconciled source and its final matrix had not been released to A53 when this record was completed.

No native execution, build, test, CI retry, remote mutation or source edit was performed by A53 for this observation. Dummy-device, copied-state and software-surface checks leave physical MIDI/audio, real-display/DPI behavior, native accessibility and literal whole-UI 1:1 acceptance open.
