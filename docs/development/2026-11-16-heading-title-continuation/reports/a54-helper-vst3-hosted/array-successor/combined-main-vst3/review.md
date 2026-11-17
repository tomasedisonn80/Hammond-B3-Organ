# Combined-source VST3 hosted review

A54 follow-up, 17 November 2026 UTC. This is the same accepted worker, with no
additional staffing credit. The original note and all predecessor reviews remain
frozen.

## Outcome and exact source

**All four required native VST3 platform jobs pass at source
`54859886268ce83c36f359c43327f7c72a77ae82`**, tree
`f5f8f037af301f8b1ff5b9b4a00ff5581647667a`. Its parents are
`d2ed03b94114e35d0caa65968d11afe896a5e9f5` and
`ea02c5465b6c6a896cbbc83b55479d6f62bbf8c9`.
The [guarded main-publication receipt](../../../combined-main-publication.json) and independently
retrieved [terminal API metadata](final-metadata.json) bind this result.

[Native VST3 run 44038196255](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44038196255)
is **attempt 1**, event `push` on `main`, and terminal `success`. Every job has
an actual assigned runner and completed build, native acceptance, inventory and
artifact steps. There are no failed, cancelled or unacquired jobs in this run.
The workflow and SDK lock are retained as [exact source bytes](source-workflow.txt)
and [SDK lock](sdk-lock.json). Earlier sources supply no reused pass.

| Platform family | Actual job | Independently parsed module | Native CTests | CTest wall time |
| --- | ---: | --- | ---: | ---: |
| Linux GCC | 133886097578 | ELF64 x86_64 | 8/8 | 5.09 s |
| macOS Apple Silicon | 133886097561 | Mach-O64 arm64 | 7/7 | 6.00 s |
| macOS Intel | 133886097249 | Mach-O64 x86_64 | 7/7 | 8.44 s |
| Windows MSVC x64 | 133886097530 | PE32+ x86_64 | 7/7 | 7.07 s |

The actual tools are GNU 13.3.0 on Ubuntu 24.04; AppleClang 17.0.0.17000013
on both macOS architectures; and MSVC 19.44.35230.0, Visual Studio 17 2022 x64,
on Windows 2022. Provenance records name the actual runner architecture,
image/version, Python, source commit/tree, run and attempt. The ELF, Mach-O and
PE headers independently agree with those architectures.

## SDK, actual validator and native behavior

All four jobs acquire and then separately verify **Steinberg VST3 SDK 3.8.1,
tag `v3.8.1_build_84`**, root commit
`3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96`. Each receipt verifies the root
and all four required submodule checkouts, five primary licenses and the embedded
JSON dependency. Acquisition reports network use; the verify-existing operation
reports no network use. The artifact's SDK lock is byte-identical to the
published source lock, SHA-256
`ef3dfdf3feb5747967fe205ba196f5ef1b01457653f6ad7a62fffefd702ba965`.

Each actual validator command names its built `HammondB3.vst3` bundle, loads
the module and reports **47 tests passed, zero failed**. This is module
validation, not the SDK validator self-test. The processor/controller identifiers
remain `19F9ADC0533F42B4B96BD51D6547E838` and
`0DEE76AB26BC475ABF64F138C89FB0E0`; both classes report SDK 3.8.1.

The original diagnostics remain explicit: each validator block prints **16**
`Failed to teardown test!` messages and **15**
`64bit Audio Processing not supported.` messages. Their counts match the
retained predecessor observations. This review records the actual 47/0 outcome
and retains those messages; it makes no warning-free or teardown-cause claim.

All seven common CTests execute: install/relocation, actual module validator,
controller, ABI, behavior, automation and concurrency. Linux executes the
eighth real-time interception gate. Across the four jobs there are **29 executed
CTests, zero failures, zero skips and zero disabled tests**.

The ABI result is identical on each platform: **nine instances, 701,642
assertions, 47 descriptors, 2,140 conversions, 1,673 accepted callbacks,
88 rejected calls, 3,207 state round trips and six lifecycle sequences**.
It compares **229,725 frames**, including **217,972 audible frames**, with
**maximum audio error zero**. Controller, behavior, automation and concurrency
summaries are retained in the four platform reports and original logs; the
concurrency schedule-dependent counters are not forced into a cross-platform
identity claim.

## Installation, relocation and Linux interception

Each platform executes both original installation methods:
`test_install_move_and_load` and
`test_preflight_rejects_incomplete_bundle_without_mutating_prefix`.
The install summary binds every payload SHA-256, and the ABI result from the
moved installation equals that platform's direct ABI result exactly.
This covers the two actual installation tests and relocation; it is not a
signed distribution or every-host installation claim.

Linux's ELF gate observes **193 regions**, succeeds in **12/12 overload
calibrations** and executes **8,945,157 assertions**. All eight processing-path
rows have zero intercepted C++ allocations/deallocations. The positive module
create/release probes register the expected one allocation and one deallocation,
so absence in processing is not inferred from an uncalibrated hook.
The actual scope is **Linux calling-thread global C++ new/delete**. Reported
timings are observations; other threads, arbitrary C allocators, hardware
audio callbacks and device deadlines are not established by this gate.

## Package and byte evidence

All **eight original provider artifact ZIPs** are retained and independently
verified against their provider byte counts and SHA-256 digests. Each bundle ZIP
has exactly `archive.sha256`, `inventory.json` and
`HammondB3-Release.tar.gz`. Every inner archive digest, allowed relative path,
payload count, length, SHA-256 and stored mode agrees with the inventory.
The pre-copy build inventory and staged inventory are byte-identical. Linux
contains four payload files; the other platforms each contain six.

Both plugin class records, module architecture, SDK license and
`THIRD_PARTY_NOTICES.md` are verified from the actual payload. The SDK metadata's
legal trailing commas are parsed without rewriting its original bytes.
Raw Windows text remains in original ZIPs or deterministic gzip, preserving CRLF.

| Module | Bytes | SHA-256 |
| --- | ---: | --- |
| Linux GCC | 459,048 | `cb83fb90758ad73f27100d59f0e36a72690a4b925da25d2e30d0cb45ffbf8639` |
| macOS Apple Silicon | 448,688 | `7b710fd3290ea325c383522a62fe8d9a26869ba48c6b61a20f558c68ffd6cfe4` |
| macOS Intel | 453,616 | `176c76437fcefe8843919d2ad14436d14d9aa4cd94a7acf6c9c5759aecaf42e9` |
| Windows MSVC x64 | 400,384 | `860e8d75b025cd3aed3c112ea464e5a7b315495d1f2a6bbcfd74337c0f1b5374` |

| Inner package archive | Bytes | SHA-256 |
| --- | ---: | --- |
| Linux GCC | 198,147 | `0fdc26e0cb806b01a597c72387f9742f845f49c079602da340d556850c32ee54` |
| macOS Apple Silicon | 164,389 | `f4840b0c3b2d8016312b4f3f4bd7860d66a1489ae78c23efb6c5777c48226086` |
| macOS Intel | 178,187 | `8fe890bbef2d4b18958cfcc970551eebe5309183e5c1d0d973f8c545632e5a98` |
| Windows MSVC x64 | 420,769 | `934e7c89205e8db99a40d9c5f4d55d3c16d490f5542364d2eca34a3c45a3b57d` |

The Linux and both macOS module bytes equal the retained predecessors; the
Windows module bytes differ. Its actual metadata, ABI, native tests and install
evidence pass at this source. No cause or reproducible-build claim is inferred
from the changed Windows digest.

The [broad input comparison](input-comparison.json) retains all **292** selected
current paths. Relative to `d2ed`, 290 are identical and the two comparator
tools differ; relative to `628`, 288 are identical and four tool paths differ.
This deliberately broad scope includes standalone authoring tools. The new
executions qualify the new source regardless of earlier byte equality.

## Retention, preservation and next action

The four complete decoded job logs contain **1,108,369 bytes**, retained in
**130,632 bytes** of deterministic gzip with mtime zero and no embedded filename.
All **1,806** artifact CTest lines appear in order in the matching complete job
log after timestamp/line-ending comparison only. Both original streams remain
unchanged. Each platform report retains commands, limits, exact CTest XML/log
identities, native summaries, package inventory and original module metadata.

[Byte-retention inspection](git-byte-retention.json) checks Git's read-only
check-in conversion against original evidence bytes; the binary containers
preserve original Windows text without a global attribute change.
All **143 pre-existing A54 records** in the [frozen input manifest](preexisting-evidence.json)
still match. This follow-up writes only its assigned new evidence folder.
It executes no native binary, build, project test, retry or remote mutation.

The [summary](summary.json) links every platform validation and complete log.
Root still owns the other workflow families and final documentary publication.
The eventual current-doc patch must use the actual complete sixteen-job matrix
and explicit code/input-equivalence receipt; this VST3 result alone supplies
neither. Any later documentary descendant is separate from the tested source.

This is bounded SDK/native workflow qualification. It establishes no all-DAW
compatibility, physical audio/MIDI-device behavior, hardware callback deadline,
measured instrument calibration, signing/notarization or whole-interface
1:1 acceptance. Those product gates remain unchanged.
