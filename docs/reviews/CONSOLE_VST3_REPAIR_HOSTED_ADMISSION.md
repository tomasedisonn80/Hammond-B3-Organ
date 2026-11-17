# Console successor Native VST3 hosted admission

**A58 follow-up, 17 November 2026 UTC: ADMIT all four Native VST3 families at
`d2ed03b94114e35d0caa65968d11afe896a5e9f5`.** New attempt-one execution passes
**29/29 CTests**, with **47 passed / zero failed actual-module validator checks
on each platform**. This is a follow-up by the same actual worker, with no new
worker credit. The accepted [first-source admission][first] and its note, receipt
and original evidence remain unchanged. The [new machine receipt][receipt]
qualifies only this successor's VST3 jobs; other workflows retain separate owners.

## Independent source and dependency identity

GitHub's commit API and read-only root-fetched Git objects agree on tree
`45f3f2bc1bc844061be7d1303b13b10bfaba9938` and sole parent
`cf87a587d0002d106e5210b57a39fd1967245a8f`. This independently agrees with
[root's publication receipt][publication]. The [source comparison][source]
verifies all **87 native inputs**, including 81 protected include/src/plugins
files, against first-source hashes, successor Git blobs and current working bytes.
There are zero mismatches. Production native adapters/core, CMake, workflow,
acquisition helper and SDK lock remain unchanged.

The inspected code-domain difference contains exactly five test/validation paths:
the P1 fixture, capture-tool tests, header-comparator tests, P1-comparator tests
and the P1 comparator. Their before/after identities are recorded separately;
this VST3 review does not replace their independent repair admission. Workflow
SHA-256 remains `6bc30e3fcb880d456a5ec4af98e2d2950d5c340285948cd01dc230ba3625d734`.
Its unchanged policy source is referenced by hash, while all execution evidence
comes from the new run.

Every runner's actual SDK acquisition and subsequent verification agree with
the unchanged **3.8.1 / v3.8.1_build_84** lock, root commit
`3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96`. All five checkout commits, five primary
licenses and the embedded parser identity verify. Acquisition records network use;
verification records no network use. Those new records and exact lock bytes are
retained inside the original diagnostic archives.

## New hosted results

[Native VST3 run 44034656821](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44034656821)
is a successful `main` push run, attempt **1**. All four jobs are completed,
name the exact successor commit, and have actual runner/start/end identities.
Build, validation, inventory/archive and both artifact-upload steps succeed.

| Family | Job ID | Actual compiler / native header | CTests | CTest wall time |
| --- | ---: | --- | ---: | ---: |
| Ubuntu 24.04 x64 | 133874509035 | GCC 13.3.0 / ELF64 x86_64 | 8/8 | 5.10 s |
| Windows 2022 x64 | 133874509343 | MSVC 19.44.35230.0 / PE32+ x86_64 DLL | 7/7 | 7.27 s |
| macOS 15 ARM64 | 133874509381 | AppleClang 17.0.0.17000013 / Mach-O64 arm64 | 7/7 | 3.97 s |
| macOS 15 Intel | 133874509387 | AppleClang 17.0.0.17000013 / Mach-O64 x86_64 | 7/7 | 9.44 s |

All four execute install, actual-module validator, controller, ABI, behavior,
automation and concurrency CTests. Linux also executes realtime. Exact names,
individual passing rows, verbose output and JUnit agree; all **29** are enabled
and executed, with zero failures, errors or skips. Only the other-OS configure
branch is skipped. No job is cancelled or left unacquired at final observation.

The unchanged limits are observed directly: validator/ABI/behavior/automation/
realtime 180 seconds, install/concurrency 240, controller 300; jobs retain
35 minutes, `fail-fast: false` and `--no-tests=error`. No test, timeout or
acceptance threshold was changed for this review. No retry was requested.

## Actual module, installation and allocation

Each new `hammond_vst3_validator` command loads its actual generated
`HammondB3.vst3`, identifies both original class UUIDs and 47 parameters, and
reports **47 tests passed, zero failed**. The separately logged 51-test SDK
`-selftest` remains distinct. Each complete downloaded job log contains exactly
the diagnostic archive's CTest line sequence after timestamp removal.

Each ABI result reports 47 descriptors, **701,642 assertions**, 2,140 conversions,
3,207 state roundtrips and **229,725 compared frames with zero maximum audio
error**. Both install methods pass; the relocated ABI object equals that
platform's ordinary ABI object. Full controller, behavior, automation and
concurrency summaries are retained, including scheduling-dependent counts.

Linux's new run records positive processor/controller allocation-hook calibration,
**193 measured regions** across eight paths, twelve overload calibrations and
8,945,157 assertions. Every measured processing path has zero hooked C++
`new`/`delete`. This remains calling-thread Linux instrumentation; observed
timings establish no physical audio-device deadline or other-platform allocation
guarantee.

## Original diagnostics and package bounds

The four new module-validator logs each preserve **16 teardown diagnostics,
nine unsupported-rate ERROR messages and fifteen unsupported-float64 messages**.
Unsupported mono and absent optional interfaces remain visible. Linux retains
four upstream SDK integer-format compiler warnings. Windows' unsuccessful
pthread feature probes are configure observations. These are successful SDK
summaries with their original diagnostics, not warning-free or expanded-format
qualification. Both macOS builds record SDK ad hoc signing, not release signing
or notarization.

All **eight original ZIPs** match GitHub's sizes and SHA-256 digests. Independently
reading their tar members verifies safe regular-file paths, modes, sizes and hashes;
archive digest, staged/build inventory bytes and relocated-install hash maps agree.
Binary headers independently establish the architecture above. Payloads contain
4 Linux files / 484,241 bytes; 6 Windows files / 679,834 bytes; 6 ARM macOS files /
477,584 bytes; and 6 Intel macOS files / 482,512 bytes. Original module-info bytes,
SDK license and project notices remain present. New artifact identities are
recorded directly; cross-run binary or archive reproducibility is not claimed.

The [retention manifest][retention] preserves all four full decoded job streams
as lossless deterministic gzip, eight original archives and their inspection
records. No module was locally built, tested, installed or loaded. The archive
inspector differs from its retained first-source version only in the seven
source/tree/run/job identifiers, with unchanged checks.

All 59 first-source manifest entries and the accepted review/receipt/note hashes
still verify exactly. Earlier failures and cancellations retain their own source
identities; no older pass was promoted. These VST3 successes preserve the existing
47 controls, `B3CONTROLS4`/readers 1–3, 91 shared sources, UUIDs and nominal dry
Engine. DAW/device journeys, callback retirement/deadlines, accessibility,
physical fidelity, signed release and literal whole-interface **1:1** remain
separate. Root retains other-workflow acceptance, strict record closure and
publication of this follow-up evidence.

[first]: CONSOLE_VST3_HOSTED_ADMISSION.md
[receipt]: ../development/2026-11-16-console-completion/reports/A58-repair-hosted/summary.json
[publication]: ../development/2026-11-16-console-completion/reports/repair-publication.json
[source]: ../development/2026-11-16-console-completion/reports/A58-repair-hosted/published-source-boundary.json
[retention]: ../development/2026-11-16-console-completion/reports/A58-repair-hosted/retention.json
