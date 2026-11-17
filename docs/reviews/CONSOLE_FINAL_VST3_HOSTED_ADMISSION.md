# Console final-source Native VST3 hosted admission

**A58 follow-up, 17 November 2026 UTC: ADMIT all four Native VST3 families at
`523c1979334b0fbb624ce120128a0b8ada078383`.** New attempt-one execution passes
**29/29 CTests** and **47 actual-module validator checks per platform, with zero
failed checks**. This is additional work by the existing A58 worker, with no new
worker credit. The [machine receipt][receipt] records this source's new execution;
the [first-source][first] and [successor][successor] admissions remain immutable.

## Exact source and unchanged policy

The commit API and read-only root-fetched Git objects independently agree on tree
`893441fe87859b9dbad81a5d81a453f7c96030f8` and ordered parents
`8189a49eacab5d4e6ce6c178862e83b03bdec437`, then
`54859886268ce83c36f359c43327f7c72a77ae82`. The [source boundary][source] verifies
all **87 native and policy inputs**, including 81 files under include/src/plugins,
against the previous admitted source, final Git blobs and working bytes. There
are zero mismatches. Native adapters/core, CMake, workflow, SDK acquisition,
inventory helper and SDK lock remain unchanged.

The inspected code-domain difference from `d2ed03b9` comprises three C++ fixture
serializers and six Python validation inputs. Relative to concurrent parent
`54859886`, only five Python validation inputs differ. Exact paths and before/after
hashes are retained; this admission does not replace those repairs' independent
reviews. Neither that parent's execution nor an earlier A58 pass is promoted.

Workflow SHA-256 remains
`6bc30e3fcb880d456a5ec4af98e2d2950d5c340285948cd01dc230ba3625d734`.
Its unchanged seven common CTests are install, actual-module validator,
controller, ABI, behavior, automation and concurrency; Linux adds realtime.
Exact CTest names and observed timeouts are recorded: validator/ABI/behavior/
automation/realtime 180 seconds, install/concurrency 240, controller 300. Jobs
retain 35 minutes, `fail-fast: false` and `--no-tests=error`. No predicate,
numerical criterion, deadline or required gate was relaxed.

Each runner newly acquires and verifies SDK **3.8.1 / v3.8.1_build_84**, root
`3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96`. All five checkout commits, five primary
licenses and the embedded parser identity agree with the unchanged lock. Actual
acquisition reports network use; subsequent verification reports none. Original
records and exact lock bytes remain in each diagnostic archive.

## Four completed jobs

[Native VST3 run 44043394002](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44043394002)
is a successful `main` push, attempt **1**, at the exact commit above. All jobs
are terminal success with actual runner, start/end and source identities. Build,
actual validation, inventory/archive and both artifact-upload steps succeed.

| Family | Job ID | Compiler / native header | CTests | CTest wall time |
| --- | ---: | --- | ---: | ---: |
| Ubuntu 24.04 x64 | 133903128269 | GCC 13.3.0 / ELF64 x86_64 | 8/8 | 6.68 s |
| Windows 2022 x64 | 133903128675 | MSVC 19.44.35230.0 / PE32+ x86_64 DLL | 7/7 | 7.58 s |
| macOS 15 ARM64 | 133903128533 | AppleClang 17.0.0.17000013 / Mach-O64 arm64 | 7/7 | 5.10 s |
| macOS 15 Intel | 133903128818 | AppleClang 17.0.0.17000013 / Mach-O64 x86_64 | 7/7 | 12.10 s |

All 29 CTests execute with zero failures, errors or skips. Individual passing
rows, verbose output and JUnit agree; each complete job stream contains exactly
its archive's CTest line sequence after timestamp removal. Only the other-OS
configure branch is skipped. No job is cancelled or unacquired. No retry was
requested.

Every actual `hammond_vst3_validator` command loads the generated
`HammondB3.vst3`, identifies the two original class UUIDs and **47 parameters**,
and reports **47 passed / zero failed**. The separately logged **51-test SDK
selftest** remains distinct from this module result.

## ABI, runtime, installation and allocation

Each ABI reports **701,642 assertions**, 47 descriptors, 2,140 conversions,
3,207 state roundtrips and **229,725 compared frames with zero maximum audio
error**. Both install methods succeed, and every relocated ABI object equals its
platform's ordinary ABI object. Controller tests report 138,215 checks and 3,984
threshold cases. Behavior reports 29,455,970 checks, 1,066 accepted callbacks and
234,185 direct-reference frames; automation reports 879 callbacks, 954 state
reads and 102,156 direct-reference frames with zero maximum error.

Scheduling-dependent concurrency counts are preserved individually:

| Family | Callbacks | Compared frames | Maximum audio error |
| --- | ---: | ---: | ---: |
| Linux | 1,469 | 67,342 | 0 |
| Windows | 2,162 | 96,329 | 0 |
| macOS ARM | 3,588 | 155,894 | 0 |
| macOS Intel | 3,171 | 138,529 | 0 |

All four retain the exception-unwind cleanup probe, 24 controlled rounds and
3,072 accepted stress loads. Complete runtime summaries remain in the evidence.
Linux records positive processor/controller allocation-hook calibration,
**193 measured regions** across eight paths, twelve overload calibrations and
8,945,157 assertions. Every measured processing path has zero hooked C++
`new`/`delete`. This is Linux calling-thread instrumentation; timing observations
establish no physical-device deadline or other-platform allocation guarantee.

## Honest diagnostics and package evidence

Each new module-validator stream retains **16 teardown diagnostics, nine
unsupported-rate `ERROR` messages and fifteen unsupported-float64 messages**.
Unsupported mono and absent optional interfaces remain visible. Linux retains
four upstream SDK integer-format warnings. Windows' unsuccessful pthread
feature probes remain configure observations. The successful 47/0 summaries
are not warning-free or expanded-format acceptance. Both macOS builds retain
SDK ad hoc signing, with no release-signing or notarization claim.

All **eight original ZIPs** match GitHub's sizes and SHA-256 digests. Independent
tar-member inspection verifies safe regular-file paths, modes, sizes and hashes.
Archive digests, staged/build inventory bytes and relocated-install hash maps
agree. Native headers establish the architectures above. Payloads contain
4 Linux files / 484,241 bytes; 6 Windows files / 679,834 bytes; 6 ARM files /
477,584 bytes; and 6 Intel files / 482,512 bytes. SDK license, project notices and
original opaque module-info bytes remain present. Actual new binary/archive
identities are recorded; cross-run reproducibility is not claimed.

The [retention manifest][retention] covers the eight original archives, four
complete decoded job streams as lossless gzip, original API responses and
inspection records. The inspector changes only seven source/tree/run/job
identifiers from its previous retained version; its checks are unchanged. No
module was locally built, tested, installed or loaded.

Both earlier manifests verify unchanged: **59 first-source files and 58
successor files**, plus six accepted document identities. Original failures and
cancellations keep their own source identities. The preserved 47 controls,
UUIDs, `B3CONTROLS4`/readers 1–3, 91 shared sources and nominal dry Engine are
unchanged. Other workflows, DAW/device journeys, callback retirement/deadlines,
accessibility, physical fidelity, signed release and whole-interface **1:1**
remain separate. Root owns other-workflow admission, strict record closure and
publication of these final review artifacts.

[receipt]: ../development/2026-11-16-console-completion/reports/A58-final-hosted/summary.json
[source]: ../development/2026-11-16-console-completion/reports/A58-final-hosted/published-source-boundary.json
[retention]: ../development/2026-11-16-console-completion/reports/A58-final-hosted/retention.json
[first]: CONSOLE_VST3_HOSTED_ADMISSION.md
[successor]: CONSOLE_VST3_REPAIR_HOSTED_ADMISSION.md
