# Assignment 55 — independent final hosted qualification

Actual worker: **`/root/cal_w10_a55`**, assignment **55**, logical wave **10**,
calibration session `2026-11-13-calibration`. Work performed 2026-11-14 UTC.
Owned only this note and
[CALIBRATION_FINAL_HOSTED.md](../../reviews/CALIBRATION_FINAL_HOSTED.md).

## Result and retained scope

Independently retrieved all ten completed job metadata records and full decoded
logs for `d7f6100010eb4cdd028ec93000cd9e893ac6d190`, tree `0140c737de4db28288b118744c2beef57976697f`. All ten succeeded. Downloaded the four actual
core diagnostic ZIPs, verified API sizes/digests, embedded source revisions,
JUnit totals and exact 106-name selection, and read the complete nested test
summaries from `LastTest.log`. The source-qualified review retains the complete
matrix and limits. No project tests were rerun locally by this worker and no
other worker's execution is counted as its own.

Read AGENTS.md, scope, current handoff/status/next steps, development context,
README, complete PLAN and session atlas consolidation, prior hosted-package
review and note, actual workflow selections and affected test implementations.
The six actual first-wave readers own the full-PDF coverage; this reviewer does
not claim another complete reading or physical acquisition.

## Source and publication observation

Read-only GitHub commit lookup independently verified the published tree and
parents `7ec79fb1c80793cf2f1bd6418abc081a547528c5` and
`f4815a6372d103e92789a9732642345864543405`. Read-only local Git checks confirmed
all **22 selected workflow/build/production/test files** below equal the frozen
`48a19074b7a99ab6a50ea1e29c1114d5ba95fc0a`, tree
`3edea0838b75feb06c19e151ec8539e80646fc03`. The complete diff from that source
to the published source contains **40 paths**, all under docs/
or root AGENTS.md/README.md. Thus the complete production, tests, build, model
and data inputs are unchanged, while new documentary handoffs are present.

The earlier observed `7ec79fb1` push was independently identified as the
concurrent standalone closure on `27209a7`, not this final 106-suite source.
Its jobs were not downloaded or credited here. No success from the prior
103-suite source qualified changed calibration bytes.

All three actual runs were created 2026-11-14T01:09:54Z by push, attempt 1.
Final independent metadata observation: **2026-11-14 01:17:19 UTC**. API resources used:

```text
GET /repos/tomasedisonn80/Hammond-B3-Organ/commits/d7f6100010eb4cdd028ec93000cd9e893ac6d190
GET /repos/tomasedisonn80/Hammond-B3-Organ/actions/runs?head_sha=d7f6100010eb4cdd028ec93000cd9e893ac6d190&per_page=20
GET /repos/tomasedisonn80/Hammond-B3-Organ/actions/runs/43538885659
GET /repos/tomasedisonn80/Hammond-B3-Organ/actions/runs/43538885659/jobs?per_page=100
GET /repos/tomasedisonn80/Hammond-B3-Organ/actions/runs/43538885648
GET /repos/tomasedisonn80/Hammond-B3-Organ/actions/runs/43538885648/jobs?per_page=100
GET /repos/tomasedisonn80/Hammond-B3-Organ/actions/runs/43538885785
GET /repos/tomasedisonn80/Hammond-B3-Organ/actions/runs/43538885785/jobs?per_page=100
```

The connected job-log endpoint followed GitHub's redirect and returned decoded
full log text. SHA-256 below identifies its exact UTF-8 encoding, including BOM
and original newline characters, not an unretrieved compressed log archive.
Every decoded log contains the bound source SHA and post-job cleanup. Complete
metadata, raw decoded logs, ZIPs and finite extraction tables are in temporary
`/workspace/scratch/c9f3ead4c910/a55-hosted/`; durable identities and substantive
outcomes remain in these committed documents after temporary storage expires.

## Completed runs and all decoded log identities

| Configuration | Actual job | Result | CTest elapsed |
| --- | ---: | --- | ---: |
| Linux Release | [132274559239](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43538885659/job/132274559239) | 106/106 passed | 67.65 s |
| macOS Release | [132274559424](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43538885659/job/132274559424) | 106/106 passed | 109.52 s |
| Windows Release | [132274559492](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43538885659/job/132274559492) | 106/106 passed | 193.57 s |
| Linux ASan/UBSan/leaks | [132274559498](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43538885659/job/132274559498) | 106/106 passed | 216.51 s |
| Standalone Linux | [132274499329](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43538885648/job/132274499329) | 14/14 passed | 77.50 s |
| Standalone macOS | [132274499513](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43538885648/job/132274499513) | 14/14 passed | 81.01 s |
| Standalone Windows | [132274499283](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43538885648/job/132274499283) | 14/14 passed | 92.39 s |
| VST3 Linux | [132274496366](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43538885785/job/132274496366) | 8/8 passed | 4.95 s |
| VST3 macOS | [132274496265](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43538885785/job/132274496265) | 7/7 passed | 4.86 s |
| VST3 Windows | [132274496494](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43538885785/job/132274496494) | 7/7 passed | 7.44 s |

| Job ID | Scope | Decoded UTF-8 bytes | SHA-256 |
| ---: | --- | ---: | --- |
| 132274496265 | Native VST3 (macOS AppleClang) | 288,693 | `4f70997357a5d557a09ee117bb1a2b91731ec9b900260fd2c2fa531a926bcdde` |
| 132274496366 | Native VST3 (Linux GCC) | 283,602 | `05e790e3ec0c23615bbee5fb757c7ed9c39441c96f4f4c70a4e5d800a845209f` |
| 132274496494 | Native VST3 (Windows MSVC x64) | 195,348 | `c0c02ba9ff258b2659e2345e461a450d0a99ec9d47dcf78d98656b9e41ff69af` |
| 132274499283 | Native standalone (Windows MSVC x64) | 243,568 | `651f86d6ae20bbff88658936ba31fecc05a9215d8d7a06abe508c189cd841c66` |
| 132274499329 | Native standalone (Linux GCC) | 546,467 | `f93a598a3ba1cb6dc505e7a9b6e5ae4e510f2af96f9131949ea772b2f3c9ef63` |
| 132274499513 | Native standalone (macOS AppleClang) | 534,587 | `763a119cb28ac38bfa52137224b2c587c910b2a9c68389db55f89ce9fed6019d` |
| 132274559239 | Release (Linux GCC) | 214,324 | `d0d6261110d7b99b65f2a4b09b4fe89dc49b2501a59a751195fa8a8a677eedad` |
| 132274559424 | Release (macOS AppleClang) | 194,606 | `344414a724a5876c5920127ab42bdc7b5bb248cd7d686f76e1508bcf9c3f52cf` |
| 132274559492 | Release (Windows MSVC) | 265,238 | `6af09a0ee619038afaf196a0d50d468be8742699ef0d47156510c8d82b65b532` |
| 132274559498 | Linux GCC ASan + UBSan + leaks | 222,091 | `76fcd737daf292ba73d4c85da956483b76bef23bba9f0c522c00704290647141` |

| Job ID | Started UTC | Completed UTC |
| ---: | --- | --- |
| 132274496265 | 2026-11-14T01:09:58Z | 2026-11-14T01:11:36Z |
| 132274496366 | 2026-11-14T01:09:57Z | 2026-11-14T01:11:06Z |
| 132274496494 | 2026-11-14T01:09:57Z | 2026-11-14T01:12:41Z |
| 132274499283 | 2026-11-14T01:09:57Z | 2026-11-14T01:14:23Z |
| 132274499329 | 2026-11-14T01:09:57Z | 2026-11-14T01:12:51Z |
| 132274499513 | 2026-11-14T01:09:58Z | 2026-11-14T01:13:14Z |
| 132274559239 | 2026-11-14T01:10:08Z | 2026-11-14T01:12:19Z |
| 132274559424 | 2026-11-14T01:10:09Z | 2026-11-14T01:13:03Z |
| 132274559492 | 2026-11-14T01:10:08Z | 2026-11-14T01:15:39Z |
| 132274559498 | 2026-11-14T01:10:08Z | 2026-11-14T01:14:51Z |

All ten completed job conclusions are `success`; no step concluded failure.
Conditional platform-specific setup steps marked skipped are not skipped tests.
CTest durations, unittest durations and overall job intervals are different
measurements and are not combined into performance or deadline claims.

## Actual diagnostic archive identities

Each downloaded ZIP equals the GitHub API digest and byte size. Its
`ci-logs/source-revision.txt` identifies the exact published SHA. Only named
diagnostic entries were read; no archive path was expanded into the repository
and no downloaded entry was executed. Temporary signed file URLs were used
only for the returned bytes and are not retained as public links.

| Artifact ID | Name | ZIP bytes | ZIP SHA-256 |
| ---: | --- | ---: | --- |
| 14091047181 | ci-ubuntu-24.04-release-1 | 52,890 | `d51e3090883b225beedab0059df0cb4570eb1b704462002c96caf6ca454277b4` |
| 14091115855 | ci-macos-15-release-1 | 57,518 | `dc6566be1efb718f3902dd16967269a48c9d593b854270f67f98901c39def6dc` |
| 14090729395 | ci-windows-2022-release-1 | 57,339 | `2ad9915bb44c01f60230717b8f35ce8f3d1b0aa23ae7c1f0de8aa14cd4878d09` |
| 14090929162 | ci-linux-gcc-sanitizers-1 | 53,664 | `9ed9356413cf3b2dac9f0e2e8d14290e3348e15214bb5824c95bd4e6165d4238` |

| Artifact ID | LastTest bytes | LastTest SHA-256 | JUnit bytes | JUnit SHA-256 |
| ---: | ---: | --- | ---: | --- |
| 14091047181 | 143,800 | `87a9d6a07cb4f5a1b5ca813576bfd787fb587520ffbf6ae512d6d3f72cfc38a5` | 52,321 | `91894a4a6295e406b280b62ed31f338c8e0ada62124fd8d2d06a01850dbe0318` |
| 14091115855 | 143,627 | `31f29b56a40f0343027c31b14d3cfe66a7056a77a05bb612c6209f6754333fc5` | 52,275 | `02669001e063c72195dd79b3ed9e0dfab8df7988379d448a1bd2c2d40b3364b9` |
| 14090729395 | 149,302 | `46ca754a6189322eb71d5e04115d261dbe958c55aabec0f7eb1c78c0ffd622bb` | 53,158 | `d49c16d9e0cb2300206220a801e61ef688f4b475ead7a21bd43151b5af5ac286` |
| 14090929162 | 144,091 | `3415735cc296467a8fbaf1118b7c950dcc66a2d52c972809d6b33c58975336ef` | 52,259 | `42749054eb92cb9d27829c85184f2fbff5600d2e89fca2c360264ac98c4a7714` |

Each API artifact expires on 2026-11-28 at its upload time. The four JUnit
documents report 106 tests, zero failures, zero disabled and zero skipped
outer entries. Their sorted complete test-name sets exactly equal root's
retained 106-name source selection. That comparison input is root's 52,305-byte
JUnit from its full local gate, SHA-256
`9a12a066e312c62dde559cb372afbd4e9a96183c97a4309d7d8d07b16714b27d`.
This is independent inspection of root's artifact, not a new local execution.

## Complete capture unittest observations

| Suite suffix | Methods | Linux Release | macOS Release | Windows Release | Linux sanitizers |
| --- | ---: | --- | --- | --- | --- |
| `audio` | 41 | OK | OK | OK | OK |
| `audio_admission` | 63 | OK (skipped=1) | OK (skipped=1) | OK (skipped=5) | OK (skipped=1) |
| `cli_pipeline` | 9 | OK | OK | OK | OK |
| `common` | 49 | OK | OK | OK (skipped=2) | OK |
| `comparison` | 42 | OK | OK | OK | OK |
| `corpus` | 47 | OK | OK | OK | OK |
| `corpus_admission` | 59 | OK | OK | OK (skipped=6) | OK |
| `demo` | 43 | OK | OK | OK | OK |
| `graph_scale` | 7 | OK | OK | OK | OK |
| `install` | 16 | OK | OK | OK (skipped=1) | OK |
| `job` | 81 | OK | OK (skipped=1) | OK (skipped=2) | OK |
| `metadata_read` | 24 | OK | OK | OK | OK |
| `numerics` | 19 | OK | OK | OK | OK |
| `policy` | 49 | OK | OK | OK | OK |
| `readiness` | 65 | OK | OK | OK | OK |
| `replay` | 69 | OK | OK | OK (skipped=1) | OK |
| `study` | 61 | OK | OK | OK (skipped=1) | OK |

These are emitted unittest method counts and summary skip counters. Capability
skips can represent subcases; do not subtract them mechanically to claim an
exact number of fully executed method bodies. The Windows POSIX `DESTDIR`
installation case is explicitly skipped. Complete successful summaries of the
new real-process, metadata and graph tests bind their actual final source and
are not inferred from a neighboring green job. The retained review explains
the literal binary-copy installation repair and prior failure separately.

Additional non-capture unittest skips in the four downloaded core diagnostics:

| Artifact configuration | Separate suite | Methods | Actual summary |
| --- | --- | ---: | --- |
| ci-windows-2022-release-1 | `python_test_calibration_session_records` | 27 | OK (skipped=1) |
| ci-windows-2022-release-1 | `python_test_rotary_reference` | 33 | OK (skipped=1) |

Windows common JSON acceptance explicitly names unsupported FIFO creation and
its POSIX-only pre-open path/descriptor inode comparison. Other nonverbose
unittest suites report counters rather than individual skip reasons, so this
review does not invent a complete reason list from the abbreviated output.

No native product artifact was downloaded or executed. The native job logs
themselves retain successful nine-file standalone inventory/relocation/smoke,
bundle inventory/archive and SDK validator observations. Windows standalone
explicitly reports its unsupported FIFO subcase; Linux-only native realtime
selection and all physical-device/host/fidelity limits remain separate.

## Actual hosted toolchain observations

The following are the four diagnostic `toolchain.log` records and compiler
identification lines from their actual configure logs. The sanitizer configuration
uses ASan/UBSan and leak detection; no matching failure diagnostics appeared in
its complete decoded log. The selected toolchains are observations, not new
minimum-version promises.

### ci-ubuntu-24.04-release-1

```text
cmake version 3.31.6

CMake suite maintained and supported by Kitware (kitware.com/cmake).
ctest version 3.31.6

CMake suite maintained and supported by Kitware (kitware.com/cmake).
Python 3.12.16
Linux-7.0.0-1014-aws-x86_64-with-glibc2.39
x86_64
-- The CXX compiler identification is GNU 13.3.0
```

### ci-macos-15-release-1

```text
cmake version 4.4.5

CMake suite maintained and supported by Kitware (kitware.com/cmake).
ctest version 4.4.5

CMake suite maintained and supported by Kitware (kitware.com/cmake).
Python 3.12.10
macOS-15.8.2-arm64-arm-64bit
arm64
-- The CXX compiler identification is AppleClang 17.0.0.17000013
```

### ci-windows-2022-release-1

```text
cmake version 3.31.6

CMake suite maintained and supported by Kitware (kitware.com/cmake).
ctest version 3.31.6

CMake suite maintained and supported by Kitware (kitware.com/cmake).
Python 3.12.10
Windows-2022Server-10.0.20348-SP0
AMD64
-- The CXX compiler identification is MSVC 19.44.35230.0
```

### ci-linux-gcc-sanitizers-1

```text
cmake version 3.31.6

CMake suite maintained and supported by Kitware (kitware.com/cmake).
ctest version 3.31.6

CMake suite maintained and supported by Kitware (kitware.com/cmake).
Python 3.12.16
g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0
Copyright (C) 2023 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
-- The CXX compiler identification is GNU 13.3.0
```

## Qualified relevant source inputs

These exact files were read from immutable Git objects, then compared with the
published revision before accepting its hosted matrix. The whole-repository
diff check separately confirms that all other non-documentary paths match.

| Source path | Bytes | SHA-256 |
| --- | ---: | --- |
| `.github/workflows/ci.yml` | 5,898 | `4835cbd72231c81c082c6545bde58e1514843626ffe4c9b88078c380f79dc87e` |
| `.github/workflows/native-vst3.yml` | 8,261 | `2376f41bfd96ff5afa2c821299588de05e5c49221879aef91a82074955649721` |
| `.github/workflows/standalone.yml` | 19,893 | `b7f8c70ff9a4ee38d36427999efdbfd39b8c6a06a2e4921c5196e3b8604b5eba` |
| `CMakeLists.txt` | 16,412 | `98843ed4e797cc4ce7caac14d995d8962492ed50b8756d3a6d8b19d0c316aed0` |
| `CMakePresets.json` | 1,711 | `ff1fd841008624021f39ab22342560bf1e422477dd2ff1ee05dce71ac82c6fe8` |
| `cmake/InstallCaptureTools.cmake` | 11,069 | `b7658c5ac2083e7661dd01d6ebf1cb66ee838a73e71fa2300c6d9b1affd5f015` |
| `tests/test_capture_cli_pipeline.py` | 22,054 | `bfff3005af05ede0b48258de9be1b1560384f6fec618fa6b29aad6dc75d41cb6` |
| `tests/test_capture_metadata_read.py` | 25,785 | `afc907049aba369aa477bd459dbdd7a29b8a1eed7dfd933472c723c3ec2caf3a` |
| `tests/test_capture_graph_scale.py` | 30,384 | `f85b0d233e36d84e7d63c61b682fb649acef77d11c7d0bf7557aa9e8495ad1b6` |
| `tests/test_capture_install.py` | 34,298 | `c7731f8bbcec56ed65243bb483cf59031048d978ebd0b9a7582ea6a429ea3602` |
| `tests/test_capture_demo.py` | 39,162 | `a0b5ed53d59ef91e224d477b5996ca1f7f594d8f3d4a7592559e0352bba03112` |
| `tests/test_capture_replay.py` | 62,858 | `ad4e364794e8fffda5e2959f90c046def0a0d6471b3ff049e2b9a93ea03e9d55` |
| `tools/capture_audio.py` | 30,313 | `f6f059a81078982d1061637c84836bef9564d51215cb37e0c120046ba0d7b216` |
| `tools/capture_common.py` | 12,774 | `f583dbfde3d164157d7e5aa1c601878e3f7d44b4eb7fb059426b92045ac793ab` |
| `tools/capture_corpus.py` | 39,476 | `baf4aac2fc87e322d2e5d663f4de9da8118559100ad7de1e6f77feba606779a8` |
| `tools/capture_job.py` | 24,433 | `a12645460b4c35400e5f851ac61f7bf273741a3c8d249ee186e93c46ba43a92b` |
| `tools/capture_readiness.py` | 11,630 | `816ae53470e54c428cf53bbcf566ddf9a46ad422e427f3bfb28d9b47ca7e64e1` |
| `tools/capture_study.py` | 16,849 | `5147b3f7b959ff6e2e1c7ca4b49154579a212af1cf2604bb6272fd9a212f5f98` |
| `tools/compare_capture.py` | 33,448 | `220a593499539db5f1e635db2eb15ba3c0aa7c6d001c80407fbffe93f75a9a0a` |
| `tools/make_capture_demo.py` | 25,734 | `67a49b81f009677a7d2ac62c7f6b95a50e5dd885dca0cc2ac04ca42655f79535` |
| `tools/validate_capture.py` | 28,237 | `f17ac8e24c98c792364bfdcc10c41bf410853ba19654eaa36482596d5881f3aa` |
| `tools/verify_capture_report.py` | 23,489 | `6c100e976cbe9fa4748a66fe7c6a9488f4e87b4227edc2d88ddf83913b8e91ba` |

## Review procedure and corrections retained

1. Read the actual source/scopes and frozen gates. Fetch commit and run/job
   metadata, rejecting a mismatched head or incomplete job as a completed result.
2. Fetch complete job logs only once the job metadata is completed. Preserve
   exact decoded bytes and hashes, bound SHA, cleanup, selected counts and actual
   successful steps. A later current main does not change these dated identities.
3. Download each core diagnostic ZIP with the purpose-built artifact tool.
   Compare API SHA-256/size, embedded source, JUnit counts and the complete 106
   selected names. Read full LastTest output for nested method counts/skips.
4. Compare the published source with the frozen 106-suite source, then write
   only the owned review/note. Root integrates actual accepted counts, updates
   shared handoffs, commits and publishes under the existing standing rule.

An initial read-only filename query used `native-standalone.yml`; the repository
actually names that workflow `standalone.yml`. The query returned a missing-file
error and was corrected before inspecting workflow behavior. An initial parser
looked for nested summaries in JUnit `system-out`. The actual verbose common
suite output is truncated there after 1024 bytes, so its 49-method summary was
absent from that preliminary extraction. The parser was corrected to read the
complete LastTest sections for every nested summary, retaining raw LastTest
hashes and using JUnit only for outer counts/names. Neither observation was a
production failure, altered test outcome or reason to rerun a hosted job.

No production, tests, workflows, package inventories, shared status, session
manifest, staging, commits or Git refs were changed by assignment 55. No workflow
was triggered, retried or cancelled by this worker. No external message or issue
was sent. Later code changes require their own affected qualification; physical
acquisition, calibrated fitting, listening, host/device and accessibility gates
remain open even though this exact software matrix succeeds.

## Final owned-file verification

The final review and note decode as UTF-8, use LF, end with a newline, have no
trailing whitespace or conflict markers, and resolve all nine local Markdown
links. A separate final digest comparison confirms all 22 selected current
inputs still equal the frozen/published bytes. The retained three run records
each explicitly have the exact source SHA, completed/success and attempt 1.
All four diagnostic extraction checks and the ten completed-log identity checks
finish without an exception. These are evidence/document checks, not new
executions of the project test suite.
