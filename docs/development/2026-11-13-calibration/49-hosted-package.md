# Assignment 49 — completed hosted package/replay recheck

Actual worker: **`/root/cal_w9_a49`**, assignment **49**, logical wave **9**,
calibration session `2026-11-13-calibration`. Work performed on 2026-11-14 UTC.
This is one actual new worker, distinct from earlier hosted reviewer 39.

## Owned files and result

Owned only this note and
[CALIBRATION_HOSTED_PACKAGE_RECHECK.md](../../reviews/CALIBRATION_HOSTED_PACKAGE_RECHECK.md).
No production, test, workflow, shared status, ledger, Git-ref or external-message
mutation was performed. Root owns acceptance, integration, commit and push.

The completed review records all ten observed hosted outcomes at source
`3b0979bd0d30ce96bca0bcd57bd8f730eaadd1bf`, tree
`656c5f117060210b3df656c62318d5a672fc306d`: nine successful jobs and one Windows
Release failure, 102/103 suites. It independently confirms the earlier demo
repair actually passed all 43 Windows methods without skips; report replay ran
69 methods with one Windows capability skip. The later root installation-fixture
repair passes the independently executed one-case local focus; a repaired
Windows result is not yet claimed.

Read standing AGENTS.md, current calibration scope, plan, status/next steps,
handoff, development context, prior hosted review, relevant installation source
and tests, and the exact published workflow selections. The preceding six-reader
atlas consolidation provides this session's complete source-reading record;
assignment 49 does not count another full-PDF reading. This task adds actual
source/platform evidence under the existing M0/M8 scope, not physical evidence.

## Observation and source control

Git/API inspection observed the published source/tree above and its parents
`6214032f3565f9e221fcf3988e33a22a73bb4ea8` and
`7caee9e5a1aadfa36f2a87b6855684cbd730d803`. The three workflow metadata records
all identify the same head SHA, push event, attempt 1 and creation time
2026-11-14T00:36:44Z. Metadata was retrieved at **2026-11-14 00:48:20 UTC**,
when every job was completed. The last workflow update was CI at 00:43:32Z.
The local checkout then had root's later `c352d68` commit and concurrent
uncommitted CLI work. No live source was substituted for the hosted revision.

Read-only retrieval used the owner connection
`link_6af409c021988191b91f89217024f014`, repository
`tomasedisonn80/Hammond-B3-Organ`. Exact API resources:

```text
GET /repos/tomasedisonn80/Hammond-B3-Organ/actions/runs/43535351721
GET /repos/tomasedisonn80/Hammond-B3-Organ/actions/runs/43535351721/jobs?per_page=100
GET /repos/tomasedisonn80/Hammond-B3-Organ/actions/runs/43535351733
GET /repos/tomasedisonn80/Hammond-B3-Organ/actions/runs/43535351733/jobs?per_page=100
GET /repos/tomasedisonn80/Hammond-B3-Organ/actions/runs/43535351667
GET /repos/tomasedisonn80/Hammond-B3-Organ/actions/runs/43535351667/jobs?per_page=100
GET /repos/tomasedisonn80/Hammond-B3-Organ/git/commits/3b0979bd0d30ce96bca0bcd57bd8f730eaadd1bf
```

`github_fetch_workflow_job_logs` retrieved each completed job's decoded full log.
The existing `github_fetch_workflow_run_artifacts` and
`github_download_workflow_artifact` tools retrieved the four core diagnostic
ZIPs; their temporary file URLs were used only to read those returned bytes,
never retained as durable links or sent elsewhere. API metadata, raw decoded
logs, downloaded ZIPs, exact LastTest.log files and the finite extraction tables
are retained in scratch `a49-hosted/`. Their identities and outcomes below are
durable even if that temporary workspace or the hosted retention expires.

Every complete job log contains the exact published SHA and post-job cleanup.
The independently retrieved Windows log is byte-identical to root's original
`checks/3b-windows-release.log`; its 267,078 bytes include cleanup. The earlier
metadata's in-progress observation did not mean those fetched bytes were partial.

## All ten decoded log identities

SHA-256 values below identify the exact UTF-8 encoding of the connector's decoded
log, retaining its BOM and native newline characters. They are not hashes of an
unretrieved compressed server-side job-log archive.

| Job ID | Scope | Bytes | SHA-256 |
| ---: | --- | ---: | --- |
| 132262885153 | Native VST3 (macOS AppleClang) | 288,672 | `ebecf6de9bf5d286098d416104067edb08180cba247118a13bb103ced9453656` |
| 132262885553 | Native VST3 (Windows MSVC x64) | 195,101 | `b3a1039f4828041e7071f1fc752820e2dff17a5c9ab1a278d40ee67ff742f4ec` |
| 132262885564 | Release (Linux GCC) | 213,742 | `82f4a3d09d1ba74816e281cc39be4d30562a39517c96c0a16f52253dbe2e8d0d` |
| 132262885570 | Native VST3 (Linux GCC) | 283,582 | `b58110dfb173c603bf5b60af9fac2265bf39763c9a7e9fa13b79bdb7874002aa` |
| 132262885865 | Release (Windows MSVC) | 267,078 | `58b41c56153eff93e5c4c031043e249efd9d2d5520a4bb677405dd1797a712f0` |
| 132262885892 | Release (macOS AppleClang) | 194,024 | `98c99694f6a6abaa9a5d4e5f89d64ed84e45020f78389be90f4440617b913a7c` |
| 132262885949 | Native standalone (Windows MSVC x64) | 243,799 | `1e4668c7f8e3b5f21416a81fc449e2b7cb2dcbe7ca9854483167ab4fe7f6a9ee` |
| 132262885976 | Native standalone (Linux GCC) | 546,777 | `62e357375f8dd163bc460ac19dacf7711136e56d7bbaeb0b036583c4a023c85d` |
| 132262886012 | Linux GCC ASan + UBSan + leaks | 221,511 | `f8d1e6d522c405b95b09808c16bccd1051ea12a39e1b6b298bf112df41c44a20` |
| 132262886173 | Native standalone (macOS AppleClang) | 534,582 | `bb8166419c3956ae07d941d0c2be6dfd80b7e7820860a71b69b50c7e3530552d` |

Each core Release run configures and builds the exact selected checkout, then
uses `ctest --preset release --parallel 2 --timeout 300 --no-tests=error`.
The sanitizer run uses `ctest --preset sanitizers --parallel 2 --timeout 600
--no-tests=error`. All produce JUnit diagnostics. The actual native selections
are:

```sh
ctest --test-dir build-standalone -C Release -V --parallel 1 --no-tests=error --timeout 180 -R '^test_standalone_'
ctest --test-dir build-native -C Release -V --no-tests=error --timeout 300 -R '^(hammond_vst3_validator|test_native_)'
```

Their actual workflow commands also pass the documented output-JUnit paths and
retain stdout/stderr logs. The native build aggregates precede these tests.
The source-qualified review retains all ten counts, elapsed values and platform
toolchains. No local rerun or workflow retry is credited as the hosted result.

## Actual core diagnostic artifacts

All four ZIPs matched the exact API size and digest, and their
`ci-logs/source-revision.txt` bytes identified the published 3b0979b source.
No ZIP entry was executed. Only explicitly named diagnostics were read; no
untrusted archive paths were expanded into the repository.

| Artifact ID | Name | ZIP bytes | ZIP SHA-256 |
| ---: | --- | ---: | --- |
| 14090030133 | ci-linux-gcc-sanitizers-1 | 53,382 | `6ad12d90453b92a4c50a7d12e3e06dec884649bcd994355c8dd6badcd862c7aa` |
| 14089810717 | ci-windows-2022-release-1 | 58,215 | `6f54a4b2842b32b17b7a3eb6378266354d2713f3ad7ef5bee9228bec4ecd5497` |
| 14088819301 | ci-ubuntu-24.04-release-1 | 52,536 | `26d70f55a130a8b378859b0f928edaab100c44d818eb2ef21827639be1c93918` |
| 14088304614 | ci-macos-15-release-1 | 57,114 | `7aedf8295c25c52c48162a1fbeb56363995dbdb7520e863c586cfff4e7c0ba71` |

The API says these artifacts expire on 2026-11-28 at their respective upload
times. That retention is not permanent evidence storage; the complete substantive
outcome, original failure and source identities are retained in these documents.

| Artifact | LastTest.log bytes | LastTest.log SHA-256 |
| --- | ---: | --- |
| 14089810717 | 147,264 | `f84d4ba363e5f68a1dd053b22de4bc64d28ba90697ef7fd19e23a27c18d685b2` |
| 14088819301 | 141,265 | `8e98ca57a6f456a6b2fb1054c96bcc668448095b5f3a12289eac87d64abd5735` |
| 14088304614 | 141,049 | `360d6764791b9dc431b3f6e3fcd391058d6b02b9b244f70361f40b7e1c48a6ad` |
| 14090030133 | 141,564 | `206f500853b2da4440ee7c53f6a9dabadfbb7a610b3599c66ce8683b869e3db9` |

## Complete capture unittest observations

The artifact logs expose successful output suppressed by ordinary CTest step
logs. Below, `OK / n skips` is the actual unittest summary, not a subtraction
claim about every nested subcase. Method counts are those emitted by unittest.
The only failing capture summary is the installation fixture on Windows.

| Suite suffix | Methods | Linux Release | macOS Release | Windows Release | Linux sanitizers |
| --- | ---: | --- | --- | --- | --- |
| `audio` | 41 | OK | OK | OK | OK |
| `audio_admission` | 63 | OK (skipped=1) | OK (skipped=1) | OK (skipped=5) | OK (skipped=1) |
| `common` | 49 | OK | OK | OK (skipped=2) | OK |
| `comparison` | 42 | OK | OK | OK | OK |
| `corpus` | 47 | OK | OK | OK | OK |
| `corpus_admission` | 59 | OK | OK | OK (skipped=6) | OK |
| `demo` | 43 | OK | OK | OK | OK |
| `install` | 16 | OK | OK | FAILED (failures=1, skipped=1) | OK |
| `job` | 81 | OK | OK (skipped=1) | OK (skipped=2) | OK |
| `numerics` | 19 | OK | OK | OK | OK |
| `policy` | 49 | OK | OK | OK | OK |
| `readiness` | 65 | OK | OK | OK | OK |
| `replay` | 69 | OK | OK | OK (skipped=1) | OK |
| `study` | 61 | OK | OK | OK (skipped=1) | OK |

The Windows artifact also records one skip in the separate 27-method calibration
session checker and one in the separate 33-method rotary reference suite. Those
are not new capture-method evidence. The native Windows standalone log explicitly
reports the unsupported FIFO subcase. Other capability-specific native output
retains its own scope; no universal skip-free assertion is made.

The Windows demo output has all 43 dots, `Ran 43 tests in 3.605s`, and `OK` with
no skip annotation. The source's repaired dangling-symlink method therefore
executed successfully. The Windows replay output has 69 methods, 18.198 seconds,
`OK (skipped=1)`; it cannot be described as all 69 method bodies running without
capability exclusions. Linux/macOS/sanitizer replay summaries are plain OK.

## Original failure and root's later repair

Original Windows capture-install output:

```text
FAIL: test_late_install_abort_preserves_partial_package
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_install.py", line 513
    self.assertEqual(marker.read_bytes(), b"preserve other writer\n")
AssertionError: b'preserve other writer\r\n' != b'preserve other writer\n'
Ran 16 tests in 37.421s
FAILED (failures=1, skipped=1)
```

This is the actual failed assertion, not an intentionally failing new probe.
The exact original test and installer source identities appear below. The
intentional CMake abort and partial-warning assertions had passed. The subsequent
package-file inventory assertions in that method were not reached on this run.

Root changed only the foreign marker fixture: it now writes literal
`b"preserve other writer\r\n\x00unchanged\n"` to a private source and copies those
bytes after the first real install copy. CMake text newline conversion is no
longer an oracle dependency. The marker must remain exactly equal to those bytes;
all reached-abort, partial-warning and remaining-package assertions remain.

Reviewed exact diff:

```sh
git diff 3b0979b c352d68 -- tests/test_capture_install.py
```

Root's later immutable commit is `c352d684e636b370edcdbbf0249a884623cbbfb1`, tree
`1ce57555f10fc533b5d303e9e53c5631ca1d2090`. The source archive is
`/workspace/scratch/c9f3ead4c910/w8-install-fixture-source`.
Assignment 49 independently checked thirteen archive inputs against this commit,
then executed only the affected maintained test:

```sh
HAMMOND_TEST_CMAKE=/home/agent/.cache/uv/archive-v0/kvsqq5-iHdbf13RC/cmake/data/bin/cmake python3 -B /workspace/scratch/c9f3ead4c910/w8-install-fixture-source/tests/test_capture_install.py CaptureInstallAcceptance.test_late_install_abort_preserves_partial_package -v
```

Working directory was `/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ`; the
absolute test path resolves all fixture inputs from the immutable archive.
Observed runtime: CPython 3.12.14 (`Clang 22.1.3` build), Linux 6.18.57 x86_64,
glibc 2.41; the exact CMake executable reports 4.4.4. Result: **1/1 passed in
0.870 seconds, no skips**. All thirteen identified inputs remained unchanged.
The source before/after inventory and focused log are retained in scratch.
This was the only local test invocation by assignment 49. It had no initial
harness/test failure, retry, threshold adjustment or producer repair.

Root separately ran all sixteen methods in 6.133 seconds. I verified that
retained 115-byte log's hash and outcome, without reattributing its execution.
The comparison of local results does not establish a later Windows result.
Local primary documentation from `cmake --help-command file` also identifies
`COPY_FILE` as added in 3.21; the fixture uses no later optional argument.

## Source and focused-evidence identities

| File / revision | Bytes | SHA-256 |
| --- | ---: | --- |
| `.github/workflows/ci.yml` at 3b0979b | 5,898 | `4835cbd72231c81c082c6545bde58e1514843626ffe4c9b88078c380f79dc87e` |
| `.github/workflows/standalone.yml` at 3b0979b | 19,893 | `b7f8c70ff9a4ee38d36427999efdbfd39b8c6a06a2e4921c5196e3b8604b5eba` |
| `.github/workflows/native-vst3.yml` at 3b0979b | 8,261 | `2376f41bfd96ff5afa2c821299588de05e5c49221879aef91a82074955649721` |
| `tests/test_capture_install.py` at 3b0979b | 34,023 | `a797443fe7d208bbdaebedae836edca988524d8371938dd95e9368738f26bb74` |
| `tests/test_capture_demo.py` at 3b0979b | 39,162 | `a0b5ed53d59ef91e224d477b5996ca1f7f594d8f3d4a7592559e0352bba03112` |
| `cmake/InstallCaptureTools.cmake` at 3b0979b | 11,069 | `b7658c5ac2083e7661dd01d6ebf1cb66ee838a73e71fa2300c6d9b1affd5f015` |
| `tools/capture_corpus.py` at 3b0979b | 39,220 | `1c68ca13157f767847258ccb74f3a22f49cc1d56f323cddeebd52f3ab85ed5ba` |
| Repaired test at c352d68 | 34,298 | `c7731f8bbcec56ed65243bb483cf59031048d978ebd0b9a7582ea6a429ea3602` |
| Assignment-49 independent focus log | 240 | `1fb877231483ea0c6e3feb281d7bcffbd3fb77f2f4209dadc32f560867409b5b` |
| Root sixteen-method log | 115 | `87b2615ab5ffb33a7193d35a2dad101617eb0b271186f10ac60b27c60162f9b9` |

The thirteen focused source inputs match c352d68, not a mixed live source:

| Archive path | Bytes | SHA-256 |
| --- | ---: | --- |
| `tests/test_capture_install.py` | 34,298 | `c7731f8bbcec56ed65243bb483cf59031048d978ebd0b9a7582ea6a429ea3602` |
| `cmake/InstallCaptureTools.cmake` | 11,069 | `b7658c5ac2083e7661dd01d6ebf1cb66ee838a73e71fa2300c6d9b1affd5f015` |
| `CMakeLists.txt` | 16,412 | `98843ed4e797cc4ce7caac14d995d8962492ed50b8756d3a6d8b19d0c316aed0` |
| `tools/make_capture_demo.py` | 22,329 | `d6006b6856ad484f5936e56786aeb5013c148c91fa49e373913ef1bb5484d204` |
| `tools/verify_capture_report.py` | 23,380 | `23dc1c316232c27345ce35beec667a1e604847dc30b31b9b0b8bfc63423dd2d4` |
| `tools/validate_capture.py` | 24,827 | `a872e069ba9744f6f8078f87b78ea300df1ee28aec58e104859580cdc09877af` |
| `tools/compare_capture.py` | 33,448 | `220a593499539db5f1e635db2eb15ba3c0aa7c6d001c80407fbffe93f75a9a0a` |
| `tools/capture_common.py` | 9,625 | `e06dd82e37dd178863af61aa66bee877da1fc7e498a47b729e060215ca79c3f2` |
| `tools/capture_study.py` | 16,740 | `4b627a8c213ff43691e8011dca0a4206db8f4184dd32b5ea6edad4471f90e69d` |
| `tools/capture_audio.py` | 29,951 | `b1f6228932c15f6483808cbb36a407dcdd6919f5894439d93f8888b01d66113c` |
| `tools/capture_corpus.py` | 39,312 | `751ce8e3d6a712ac8873c57aae9ab71311396921098e82b1d0fcd1720ffa9ded` |
| `tools/capture_readiness.py` | 11,247 | `215b2abd3614195151c5751248f2d40850653d794af1786e95eaedccf13bdc76` |
| `tools/capture_job.py` | 24,302 | `147002ac866a4451e6740eae69da9f914116339f89b657bae7d4c6ef41e3eded` |

## Boundaries and next action

No job was queued, in progress, cancelled or retried at the recorded final
observation. All ten were completed with the results above. This review did not
modify Actions, fetch/execute a native release bundle, operate a real audio
device or DAW, or qualify physical acquisition, model fidelity or release rights.
The four downloaded artifacts are diagnostics, not installed native products.

The core source includes replay and CaptureTools; the later allocation, graph,
metadata-read and CLI delivery source is absent. The later local c352d68 focus
contains root's new test and the earlier accepted optimization/graph work, but
not concurrently edited delivery helpers. Keep each result bound to its actual
source and test selection.

Root should accept these two notes, update current hosted pointers, preserve the
original Windows failure, publish the coherent repaired source and observe its
new Windows job. Do not relabel the old failed run or infer a repaired platform
pass from neighboring native jobs. Continue the actual remaining assignments;
this review does not declare the sixty-agent session complete.
