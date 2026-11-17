# A57 final combined source: Native hosted admission

**Decision: admit all six Native standalone hosted families at `523c1979334b0fbb624ce120128a0b8ada078383`, run `44043394005`, attempt 1.** The workflow, all six jobs, and every step are terminal. Each ordinary family passes 78/78 CTests; the strict sanitizer family passes 41/41. Together these are **431/431 CTest instances**, with zero failed, disabled, or skipped CTests. One Windows FIFO subcase is explicitly skipped and retained below.

These are fresh results for the final combined source, including its five changed Python inputs. No source-548 pass is transferred to this commit. This is the same actual A57 worker in wave 10 and adds no worker credit. Root retains final acceptance, documentary integrity and publication ownership; product and physical-device gates remain separate.

## Source and admission boundary

Independent commit API inspection verified:

| Identity | Value |
| --- | --- |
| Published commit | `523c1979334b0fbb624ce120128a0b8ada078383` |
| Tree | `893441fe87859b9dbad81a5d81a453f7c96030f8` |
| First parent | `8189a49eacab5d4e6ce6c178862e83b03bdec437` |
| Second parent | `54859886268ce83c36f359c43327f7c72a77ae82` |
| Native workflow | `.github/workflows/standalone.yml` |
| Native run / attempt | `44043394005` / `1` |

The head-SHA-filtered lookup and all-attempt jobs responses bind the six reviewed jobs to this source. There is one observed attempt and no failed or cancelled Native job. The final API result is success; the final observation is retained in `observation-terminal.json.gz`. Earlier queued and running observations remain in the numbered observation files.

Exact-commit file reads independently verified twelve relevant files. The workflow, standalone CMake, all three indexed C++ fixtures, capture source tests and H1 comparator match source 548 byte for byte. Five Python files differ: the two standalone readers, the two comparator test suites, and the P1 comparator's failure-summary output. Full bodies of those five files are retained once in `changed-sources.connector.json.gz`; unchanged bodies use immutable hash references. [source-identity.json](source-identity.json) records every API blob and SHA256 identity. Root's broader publication verification is separately recorded in [combined-indexed-publication.json](../combined-indexed-publication.json); this review does not substitute a local authored commit for the published SHA.

Independent AST inspection of those exact remote bodies confirms that all **96 published source-test method bodies remain identical**: 64 P1 and 32 H1 methods. Seven P1 and nine H1 methods are added, producing 71 and 41. The standalone readers retain every existing numerical/equality function and top-level assignment; only `main` changes and a bounded `admit_fixture_bytes` helper plus four constants are added. P1 changes only `execute` to expose at most eight failure rows with bounded labels/details when a failure exists. The successful numerical summary and predicates remain unchanged. See [combined-python-source-review.json](combined-python-source-review.json) and [A59's independent combined admission](../A59-copied-state-followup/combined-admission.json).

Static inspection is separate from execution. The hosted observations below execute the new source suites and canonical readers on each ordinary platform, and the new canonical readers again in the strict sanitizer lane.

## Six actual hosted outcomes

| Family | Job | CTests passed | Required names present and passed | CTest wall time |
| --- | ---: | ---: | ---: | ---: |
| Linux GCC, MIDI OFF | 133903129190 | 78/78 | 55/55 | 499.09 s |
| Linux GCC, MIDI ON | 133903129162 | 78/78 | 55/55 | 412.77 s |
| Windows MSVC x64, MIDI ON | 133903129277 | 78/78 | 55/55 | 549.92 s |
| macOS ARM64 AppleClang, MIDI ON | 133903129154 | 78/78 | 55/55 | 456.23 s |
| macOS Intel AppleClang, MIDI ON | 133903129393 | 78/78 | 55/55 | 574.83 s |
| Linux GCC ASan, UBSan and leaks | 133903128857 | 41/41 | 41/41 | 785.99 s |

All five ordinary jobs actually execute and pass **45 capture, 41 H1 comparator and 71 P1 comparator methods**. These 157 methods run within three of the 78 selected CTests; they are not added to the CTest total. Every required name is present. All five LibraryModel/recall/roundtrip/session/storage suites pass in all six families.

The original discovery JSON, result XML, verbose CTest output and LastTest log remain in each diagnostic ZIP. Each `job-…-review.json` records every test name, result, duration, deadline, serial property and workflow-step disposition. Aggregate success is supported by those detailed outputs.

### Actual runners

| Family | OS / machine | Compiler / Python | Runner image |
| --- | --- | --- | --- |
| Linux OFF | Azure kernel 7.0.0-1017, x86_64 | GCC 13.3.0 / Python 3.12.16 | `20261111.370.1` |
| Linux ON | AWS kernel 7.0.0-1014, x86_64 | GCC 13.3.0 / Python 3.12.16 | `20261111.127.1` |
| Windows | Server 2022, AMD64 | MSVC 19.44.35230.0 / Python 3.12.10 | `20261112.366.7` |
| macOS ARM64 | macOS 15.8.2, arm64 | AppleClang 17.0.0.17000013 / Python 3.12.10 | `20261112.0539.3` |
| macOS Intel | macOS 15.7.9, x86_64 | AppleClang 17.0.0.17000013 / Python 3.12.10 | `20260824.0482.1` |
| Strict sanitizer | Azure kernel 7.0.0-1017, x86_64 | GCC 13.3.0 / Python 3.12.16 | `20261111.370.1` |

These are the observed runner identities. Timings remain attached to their source and runner; the later passes do not establish a repaired cause for historical timing failures or repeated timing stability.

## Windows source suites and canonical readers

The Windows full log records all three changed-source acceptance suites, with no source-suite skip:

| Source-only suite | Methods passed | Reported unittest time |
| --- | ---: | ---: |
| Capture standalone interface | 45/45 | 3.709 s |
| H1 comparator | 41/41 | 1.315 s |
| P1 comparator | 71/71 | 0.976 s |

Compilation, backend verification and all native acceptance gates pass. Title evaluates and passes all **18 cases**. The H1 fixture passes **48 cases / 10,542 checks**; canonical H1 completes its protocol/copied-state validation and passes **103/103 numerical inequalities**. The P1 fixture passes **34 cases / 53,648 checks**; P1 numerical evaluates **191 checks with zero failures**, including **62/62 candidate screens**. Post-acceptance source/dependency verification, relocated smoke, diagnostic upload and package upload all succeed. See [windows-result.json](windows-result.json).

The actual emitted title and H1 admission objects prove the new reader branches executed. Both report `variant: indexed-array-v1`, `candidate_only: true`, and `whole_file_reversal_verified: true`:

| Reader | Actual indexed fixture SHA256 | Distinct standalone-reader original and reconstructed SHA256 |
| --- | --- | --- |
| Title | `9e3a8fb643194e8ce4dcefb8059e82fef2b0140183c9175449098bf8941a2ecb` | `facc85f516454964ed55e406f95db4046923d7a2441fdf72e65719b3685fec4f` |
| H1 statistics | `8c8226b04931569cdbff78cddcfd6241fd334c1f15c764a04d016d958bc912aa` | `86acc068fa23826fb39f245f9327e919c076660f315bed5d57f63e586d6d3ac6` |

The active fixture-pin fields match the observed indexed hashes. H1 also reports the exact new reader-source hash `c3b52ee56645e51d4144c296d4fd0b6579c93e13b11b117fb4d67f2a98a9c4bd`. The H1 standalone-reader original is distinct from its paired historical baseline; those identities are not substituted for each other. The same admission objects and successful numerical coverage are observed in every other final-source family.

The original cf87 compilation failure, d2ed empty drawbar-list leaves, and d2ed unidentified P1 non-screen failure remain preserved in the earlier receipts. The new source passes, but this does not retroactively identify that old P1 failure or establish a precise MSVC mechanism. The native P1 failure-summary branch is not claimed to execute in these passing jobs, and no new helper-absent native runtime is claimed.

## Strict sanitizer proof

The strict job's actual discovery, instrumentation and provenance were inspected independently of its success badge. Its **41 test names, 37 executable targets, 63 source-input names and test-to-target mapping** exactly match the unchanged policy. Compared with the original source-548 hosted provenance, exactly five input hashes change and all five match the final-source API bodies; the remaining **58 hashes are unchanged**. No later working-tree bytes are used as tested-source evidence.

The compile database contains 411 generated entries. The **291 selected commands across 44 groups** match the recorded compiled-source lists and carry address/undefined sanitizer flags plus frame pointers. Every selected group has a matching nonempty instrumented-object count. This includes **196 SDL C sources and 196 instrumented SDL objects**. The retained CI symbol-check record covers seven archives with ASan/UBSan references. All **37 executable link records** use sanitizer flags, and all **37 retained runtime records** contain ASan and UBSan with no missing library. The post-acceptance source and locked-SDL re-verification step passes.

The actual strict environment remains:

```text
ASAN_OPTIONS=detect_leaks=1:halt_on_error=1
UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1
LSAN_OPTIONS=exitcode=23
```

No selected strict test is disabled or supplies a sanitizer-environment override. No actual sanitizer diagnostic appears in the CTest stream or seven retained calibration stderr streams. Calibration still exercises **10 subprocesses / seven lifecycles**, including two deliberately failing application replays with their expected exit status and passing common assertions. Their original stderr is explicitly retained in the strict job review. These expected application failures are not hidden or relabelled as sanitizer failures.

System libraries are not rebuilt. The calibration boundary remains the real application/adapter, SDL dummy callbacks and substituted MIDI; it does not establish physical hardware or driver-timing behavior.

## Unchanged deadlines and visible skips

The independently verified workflow and standalone CMake hashes remain:

- Workflow: `d298ac55d78ae242b97c5de73be138b4a87c4d4fb343872e58a5c0bd5dc08659`.
- Standalone CMake: `927f48c1feba27889a63c73d7b8223b40b33c8851a07ac3b7feec9a88e713e07`.

Ordinary jobs retain a 40-minute allowance and the strict job 35 minutes. CTest remains verbose and serial, with `--no-tests=error` and the 180-second global timeout. Every selected deadline and serial property matches the previous source's unchanged policy.

| Gate | Ordinary deadline | Strict deadline | Actual strict duration |
| --- | ---: | ---: | ---: |
| Title density | 90 s | 240 s | 14.47 s |
| H1 fixture | 180 s | 480 s | 121.89 s |
| H1 statistics | 90 s | 240 s | 1.78 s |
| P1 fixture | 180 s | 480 s | 72.24 s |
| P1 numerical | 180 s | 480 s | 2.12 s |
| Scaled view | 60 s | 360 s | 84.10 s |
| Preset raster | 30 s | 300 s | 72.17 s |
| Native calibration | 90 s | 180 s | 21.43 s |

Intel ordinary preset raster passes in **19.09 seconds under the unchanged 30-second guard**. Child-process limits remain title 20 seconds; H1 20 ordinary/60 strict; P1 60; native calibration 15; and replay/semantic paint boundaries 12 ordinary/30 strict. The full mandatory-name lists, selected targets, 63-file inventory and bounds remain in [the immutable policy receipt](../A57-native-hosted/source-policy-preflight.json).

Windows retains one FIFO creation subcase skip inside `test_standalone_replay_boundaries`, because FIFO creation is unsupported on that platform. The subcase line and `OK (skipped=1)` refer to the same single skip; its CTest passes. The other five jobs have no method-skip lines. All six XML files report zero skipped and zero disabled CTests.

The ordinary MIDI backend quarantine retains `ASAN_OPTIONS=detect_leaks=0:halt_on_error=1`. It is excluded entirely from the strict selection. This ordinary exception is disclosed separately from the strict leak policy. Only OS-inapplicable setup/configuration and external RtMidi acquisition for MIDI-OFF are skipped workflow steps; every applicable acceptance, source verification, smoke and package step succeeds.

## Package outcomes, original retention and limits

All five ordinary jobs successfully install, stage, relocate, smoke and upload their executable package. The staged payload exactly equals the installed byte inventory: **17 files for MIDI-OFF and 21 files for each MIDI-ON family**. Help succeeds and the 600 ms dummy smoke passes. Retained smoke diagnostics verify dummy audio/video, software rendering, note-on and release observation, and completed shutdown. These are software-smoke observations.

The six complete decoded original job streams contain **6,572,863 UTF-8 bytes**, retained losslessly in **734,082 gzip bytes**. Each decompressed stream equals its retained original connector envelope without line normalization or clipping. Six original diagnostic ZIPs total **2,256,038 bytes**, each matching the GitHub API's byte count and SHA256 digest. Full XML, provenance, discovery, verbose output, compiler/instrumentation evidence, runtime records, available stderr and numerical summaries are retained. The five successful package artifacts are recorded by API identity and digest; their payload ZIPs were not redundantly downloaded because their installed/staged inventories and smoke evidence are retained. [artifacts-index.json](artifacts-index.json) makes that retention boundary explicit.

The workflow does not upload raw native title/H1/P1 frame streams or the complete temporary P1 report. Their absence is recorded; no raw payload or missing failure detail is reconstructed. The full available stdout and derived numerical JSON remain retained separately.

All **155 inventoried files** across the cf87, d2ed and source-548 evidence directories rehash unchanged. The original accepted A57 report, review and 3,530-byte note also match their accepted hashes. See [immutable-prior-evidence.json](immutable-prior-evidence.json). This follow-up changes only its exclusively assigned evidence directory. It performs no production/test/workflow/navigation edit, Git/index/ref mutation, local native build or repository-test invocation, CI rerun, cancellation, or timeout change.

The admission covers these six hosted families at source 523 only. Physical MIDI/audio/display qualification, driver timing, OS callback retirement, native browser/main integration, accessibility, DAW journeys, measured Hammond fidelity, signed distribution and literal whole-interface **1:1** remain separate and unwaived.

The machine-readable result is [report.json](report.json). [evidence-inventory.json](evidence-inventory.json) records the size and SHA256 of every retained file. Root can now perform documentary integrity after this authoring and admit the final source-bound receipt.
