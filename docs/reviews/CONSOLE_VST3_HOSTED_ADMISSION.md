# Console Native VST3 hosted admission

**A58, wave 10, 17 November 2026 UTC: ADMIT the four Native VST3 families at
`cf87a587d0002d106e5210b57a39fd1967245a8f`.** All four attempt-one jobs succeed,
with **29/29 CTests** and **47/47 actual-module validator checks per platform**.
This admission concerns VST3 only; standalone, core and the complete sixteen-job
matrix retain their separate outcomes and owners. The [machine receipt][receipt]
and [complete metadata][metadata] identify every run, job, artifact and source.

## Exact published source

Independent GitHub commit-API inspection verifies tree
`2565ac86f9d31b7ab9d24d0d5353289c2359bf12` and ordered parents
`6287055a111dc4e2747564da3d48edc9b65e2e3e` and
`8cd9034f7e1dd21dab373f0e4ad0d1be0bab61e7`. Read-only inspection of root-fetched
Git objects reproduces those identities. The [source boundary][source] compares
all **81 protected include/src/plugins files plus six native workflow/build/SDK
inputs**: all 87 match the preparation snapshot, working files and published
source. Their earlier comparisons against `9d60dbf`, `03c70c1` and `6287055` also
have zero differences. This is fresh hosted execution of unchanged native inputs;
earlier passes were not transferred.

The exact-ref workflow bytes equal the local file, SHA-256
`6bc30e3fcb880d456a5ec4af98e2d2950d5c340285948cd01dc230ba3625d734`.
SDK lock `ef3dfdf3…` selects **3.8.1 / v3.8.1_build_84**, root
`3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96`. Each runner's actual acquisition and
verification records match all five checkout commits, five primary licenses and
the embedded JSON parser identity. Verification reports no network use; explicit
acquisition reports network use. Complete lock bytes and records are retained.

## Observed matrix and gates

[Native VST3 run 44030833337](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44030833337)
is a completed successful `main` push run, attempt **1**. Every job names the exact
published head and has an acquired runner, executed build/tests, successful
inventory/archive steps and both successful artifact uploads.

| Family | Job ID | Observed compiler / module | CTests | CTest wall time |
| --- | ---: | --- | ---: | ---: |
| Ubuntu 24.04 x64 | 133862109626 | GCC 13.3.0 / ELF64 x86_64 | 8/8 | 4.94 s |
| Windows 2022 x64 | 133862109390 | MSVC 19.44.35230.0 / PE32+ x86_64 DLL | 7/7 | 7.43 s |
| macOS 15 ARM64 | 133862109757 | AppleClang 17.0.0.17000013 / Mach-O64 arm64 | 7/7 | 3.92 s |
| macOS 15 Intel | 133862109830 | AppleClang 17.0.0.17000013 / Mach-O64 x86_64 | 7/7 | 9.40 s |

All four run `test_native_install`, `hammond_vst3_validator`,
`test_native_controller`, `test_native_abi`, `test_native_behavior`,
`test_native_automation` and `test_native_concurrency`. Linux additionally runs
`test_native_realtime`. JUnit, individual passing rows and verbose discovery agree
exactly; there are **zero failed, erroneous, disabled or skipped CTests**. Only
the mutually exclusive other-OS configure step is skipped in each job. Intel's
initial queued/unacquired state is retained separately from its eventual execution.

Observed limits remain 180 seconds for validator/ABI/behavior/automation/realtime,
240 for install/concurrency and the 300-second default for controller. The workflow
retains 35-minute jobs, `fail-fast: false`, build parallelism two and
`--no-tests=error`. No retry, production change, relaxed criterion or timeout
change was performed by this reviewer.

## Actual module results and diagnostics

Each validator command explicitly loads that platform's `HammondB3.vst3`, scans
the original processor/controller class IDs and exports **47 parameters** before
its `47 tests passed, 0 tests failed` summary. The separately logged SDK
`validator -selftest` executes 51 tests during the build; it is not the module
admission result. The complete CTest line sequence in each downloaded job log
equals its diagnostics artifact, independently checked after timestamp removal.

Every actual-module result retains **16 teardown diagnostics, nine rejected-rate
ERROR messages and fifteen float64-not-supported messages**. The logs also retain
unsupported mono and absent optional interfaces. These messages do not become
failed CTests in this SDK, and this review makes no warning-free, float64 or
additional-rate claim. Linux additionally reports four upstream SDK integer-format
compiler warnings in `ustring.cpp`/`fstring.cpp`. Windows' negative pthread feature
probes are retained as configure observations. Full originals preserve their context.

Each ABI run reports **701,642 assertions**, 47 descriptors, 2,140 conversions,
3,207 state roundtrips and **229,725 compared frames with zero maximum audio
error**. The relocated-install ABI result equals that platform's ordinary ABI
result; both Python install methods pass. Controller, behavior, automation and
concurrency summaries remain complete in the per-family records. Concurrency
counts vary with observed scheduling; they are not forced into a common total.

Linux's positive allocation calibration observes module creation/release hooks.
Its eight measured processing paths total **193 regions**, with zero hooked C++
`new`/`delete`; twelve overload calibrations and 8,945,157 assertions are reported.
This is calling-thread Linux instrumentation, not other-platform allocation or
audio-device deadline qualification.

## Package evidence and retained boundaries

All **eight original artifact ZIPs** match GitHub's advertised size and SHA-256.
The four complete decoded job logs are retained losslessly as deterministic gzip,
alongside source/run metadata and selected compressed originals. The
[retention manifest][retention] identifies these intentional evidence archives.
No executable was extracted to run, installed locally or loaded by this reviewer.

For every bundle, the tar digest matches `archive.sha256`; the staged inventory
equals the build inventory byte-for-byte. Every regular tar member's path, mode,
size and digest matches the inventory and the relocated-install hash map. Native
header bytes independently confirm the architecture in the table. Payloads contain
4 Linux files / **484,241 bytes**, 6 Windows files / **679,834 bytes**, 6 ARM macOS
files / **477,584 bytes**, and 6 Intel macOS files / **482,512 bytes**. SDK license,
project notices, both class IDs and original opaque module-info bytes are retained.
macOS logs record SDK ad hoc signing; this establishes no distribution signature
or notarization. Inventory source labels are not independent binary-to-source
attestation.

The [predecessor Windows 66/68 failure][predecessor] remains separate, as do older
Windows failures, Intel timeout and sanitizer cancellation. None is erased by
these VST3 passes. Unchanged sources preserve `B3CONTROLS4`/readers 1–3, 91 shared
free-running sources, UUIDs and the nominal dry Engine. DAW/device journeys,
callback deadlines/retirement, native accessibility, physical fidelity, signed
release and literal whole-interface **1:1** remain unqualified. Root retains
integration, publication and the other workflows' acceptance.

[receipt]: ../development/2026-11-16-console-completion/reports/A58-vst3-hosted.json
[metadata]: ../development/2026-11-16-console-completion/reports/A58-vst3-hosted/observed-metadata.json
[source]: ../development/2026-11-16-console-completion/reports/A58-vst3-hosted/published-source-boundary.json
[retention]: ../development/2026-11-16-console-completion/reports/A58-vst3-hosted/retention.json
[predecessor]: ../development/2026-11-16-console-completion/reports/prepublication-628-windows-original.json
