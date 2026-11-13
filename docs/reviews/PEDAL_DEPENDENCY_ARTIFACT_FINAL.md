# Final dependency and actual native artifact audit

## Outcome and exact scope

Assignment 52 independently inspected the locked SDK and the actual Linux and
Windows native bundle ZIPs from
[run 43415692247](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43415692247).
Both finite payloads pass the byte, size, mode, archive, module-header, identity
and notice checks described below. The two independently acquired SDK checkouts
match the lock. A concrete documentation defect was repaired:
[DEPENDENCIES_AND_RIGHTS.md](../DEPENDENCIES_AND_RIGHTS.md) still described an
eight-file offline install, diagnostic-only CI uploads and a future native
module. It now identifies the implemented boundaries and preserves the original
foundation observations as historical results.

The audited published source is
[`7fb9b6121b729f46a9e18d80e8620eb21dc0847b`](https://github.com/tomasedisonn80/Hammond-B3-Organ/commit/7fb9b6121b729f46a9e18d80e8620eb21dc0847b),
Git tree `19239e05f6c5219b50d3f398ba9a6eb3acc2a1ac`. Root's pending wave-8 and
later review changes are not substituted for that source. Fourteen relevant
source files, including the PDF, lock, notices, native build/IDs/factory,
acquisition/embedding helpers and parameter/profile definitions, were freshly
compared byte-for-byte with that commit. The actual downloaded bundles were
inspected directly; root's existing verification report was not used as the
oracle.

This assignment did not load a module, run a new DAW or device test, rebuild an
SDK/plugin, change its dependency lock/notices, establish signed-build
attestation or complete a product-rights clearance. Static payload evidence
and freshly observed hosted test logs have distinct roles.

## Locked SDK: primary sources and actual checkouts

The [lock](../../data/dependencies/vst3-sdk-lock.json) selects SDK **3.8.1**, tag
`v3.8.1_build_84`. Both external checkouts, `vst3sdk` and
`a36-sdk-checkout`, were inspected independently with Git, filesystem reads and
SHA-256, then with the project's read-only verification command. No acquisition,
reset, source change or SDK patch was performed.

| Required checkout | Verified commit |
| --- | --- |
| SDK root | `3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96` |
| base | `fcf9da0bd27a16f7f03773a3a39822f28f5c8477` |
| cmake | `054c9143cbb8d47fc4694e473f2ee3b4d951a8f5` |
| pluginterfaces | `4f547e8e102b47de4a8b8aaf343c73b700786372` |
| public.sdk | `586dc5e6c8012c3e4b01c79389375cbe96bdb1da` |

For every checkout, the inspected top-level directory and HEAD match the
expected identity. The four root gitlinks agree with the submodule HEADs;
tracked, untracked and ignored changes were absent. The five license files in
each checkout match their Git blobs and the lock: **1,094 bytes each**, SHA-256
`e86d79e19e4a33ebc442d2e0d083887dfc75a2a8de9fe17eeddedb84810ad74e`.
The [pinned root license](https://github.com/steinbergmedia/vst3sdk/blob/3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96/LICENSE.txt)
was freshly retrieved through GitHub; its bytes also match. It states MIT and
the 2026 Steinberg copyright. The selected primary source is distinct from the
atlas's historical licensing discussion.

The separately identified `public.sdk/source/vst/moduleinfo/json.h` remains
**100,775 bytes**, SHA-256
`098ca68126cb34f7369388d49890d0a5d5ba731b76fbae0c2790377a663e9d41`.
Both actual files match the lock and retain their embedded Unlicense notice.
The [project notices](../../THIRD_PARTY_NOTICES.md) distinguish that header
from the five MIT primary licenses. No blanket license classification is
applied to disabled SDK samples, runner images or compiler runtimes.

The [configuration verifier](../../cmake/VerifyVst3Sdk.cmake) calls only
`--verify-existing`. The separate [acquisition tool](../../tools/acquire_vst3_sdk.py)
requires a new external destination, checks the selected root before fetching
its four submodules, and preserves a failed new checkout for inspection.
The [native CMake](../../plugins/vst3/CMakeLists.txt) disables GUI support,
plugin/hosting examples and automatic plugin-directory links; it creates the
actual module and test tooling without placing the SDK source tree inside the
repository or package. The lock's `qualification` object is the dated
assignment-15 foundation result, not the latest product status. Its bytes were
preserved.

## Fresh remote observation and downloaded bytes

Fresh Actions API reads identified both artifacts as unexpired products of run
43415692247 at the exact source commit above. The Linux and Windows jobs were
`completed/success`; the macOS job was still queued at this observation. The
run therefore was not claimed as a completed three-platform success.

| Platform / artifact | ZIP bytes | ZIP SHA-256 from API and local bytes |
| --- | ---: | --- |
| Linux `14032125757` | 188,108 | `716a064d65e2127dbfb7ded5567d3d10a2c7dddd4a9c1afe494f6d1eb30561a9` |
| Windows `14032090890` | 412,681 | `cf2ffb94459991446f2ebe1a8b04749680957f216d8e74b88863748e88d742fa` |

Each ZIP contains exactly `HammondB3-Release.tar.gz`, `inventory.json` and
`archive.sha256`. The inner archive SHA-256 values are:

- Linux: `5a71117460660be3c4f940ae84433e76e26a26c63fd62f2e9fc4077b452ac799`.
- Windows: `5b8a611892337babbdaec5087117c9f5ee04504b256ee7ee7f99ace66930eb37`.

For each tar, an independent standard-library inspection rejected unexpected,
duplicate, absolute or parent-traversing file names and any link/special member.
Every actual regular file was read and checked for exact size, SHA-256 and tar
permission mode against the inventory. Directory entries were recognized
separately. Payload totals and the exact set of ten files across both bundles
match. This verifies those quiescent downloaded archives; it is not a filesystem
race-admission test.

| Actual module | Bytes | Independently observed format | SHA-256 |
| --- | ---: | --- | --- |
| Linux `Contents/x86_64-linux/HammondB3.so` | 446,696 | ELF64, little endian, ET_DYN, x86-64 | `b8efd0d0e93567f072ef7304734787ff20fdf096145f344dffa502035b9847ca` |
| Windows `Contents/x86_64-win/HammondB3.vst3` | 393,728 | PE32+, AMD64 | `a05435f0d76704c36c8af6f2d64556e7325e2141790a9d8b56c474f305d5cdad` |

The four-file Linux payload is **456,767 bytes**. The six-file Windows payload
is **658,056 bytes**. Each contains the module and three resources:
`moduleinfo.json`, `VST3_SDK_LICENSE.txt` and `THIRD_PARTY_NOTICES.md`.
Windows also contains the icon and `desktop.ini` identified below. There is no
SDK source, validator, module-info tool, test binary, Python interpreter, PDF or
hardware recording among either bundle's actual members.

### Metadata, saved state and embedded source profile

The exact resource bytes were preserved. The SDK's module-info writer uses
trailing commas; the independent inspection removed only such commas outside
quoted strings in a derived in-memory copy before parsing. This is explicit
handling of the observed SDK text, not a claim that it is strict JSON. Windows
uses CRLF; after CRLF-to-LF normalization solely for comparison, the two actual
metadata texts are otherwise identical.

Both list version `0.1.0`, SDK `VST 3.8.1`, one Audio Module Class and one
Component Controller Class with the unchanged locked identifiers:

- Processor: `19F9ADC0533F42B4B96BD51D6547E838`.
- Controller: `0DEE76AB26BC475ABF64F138C89FB0E0`.

Each actual module contains the complete **4,545-byte** compiled nominal profile
exactly once, SHA-256
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`,
and the `B3CONTROLS3` format marker. Static presence identifies bytes; runtime
state behavior is established by its separate executed tests. The inspected
source registry still has 45 records under schema 3. The downloaded job logs
contain actual ABI output for 45 descriptors and 2,002 conversions, along with
41,795 controller checks. This audit does not pretend module-info JSON itself
exports all parameter records or replace native execution with string searches.

### Notices and unbundled runtime dependencies

Both SDK license resources equal the locked primary license byte-for-byte.
Both project-notices resources equal the 7,887-byte source notice at the audited
commit, SHA-256
`a3aa1900ec8b584bfe0879d0d8c7c1af3148dc23729d01a62e26ed428b61c2f6`.
Those notices include the selected SDK text, embedded JSON header's notice,
SplitMix64 provenance and other explicitly scoped entries.

GNU Binutils 2.44 inspected import information without loading either module:

| Platform | Direct runtime imports observed |
| --- | --- |
| Linux, `readelf -d` | `libstdc++.so.6`, `libm.so.6`, `libgcc_s.so.1`, `libc.so.6` |
| Windows, `objdump -p` | `KERNEL32.dll`, `USER32.dll`, `ole32.dll`, `MSVCP140.dll`, `VCRUNTIME140.dll`, `VCRUNTIME140_1.dll`, and UCRT runtime, math, heap, string, stdio, filesystem and locale API-set DLL names |

No imported runtime DLL/shared-library file is present in the inspected bundle.
A package intended for a clean target OS still needs an explicit runtime-support
and redistribution decision. This is direct import-table inspection, not a
complete transitive dependency walk or a new clean-OS run.

## Actual Windows folder icon: a concrete packaging decision

The Windows `PlugIn.ico` matches the pinned CMake submodule's
[`templates/VST_Logo_Steinberg.ico`](https://github.com/steinbergmedia/vst3_cmake/blob/054c9143cbb8d47fc4694e473f2ee3b4d951a8f5/templates/VST_Logo_Steinberg.ico)
and its Git blob exactly: **254,170 bytes**, SHA-256
`1dda09aceb9fa930a3894cce4ad57edd8fa48ce58157c97ba5f971d2d4e79821`.
The 44-byte `desktop.ini` equals the SDK template, SHA-256
`3f3d19c85c40231d4dec0c6526b77d8325031eb7d52fcf141d68feaa3a88547f`.
It points to `PlugIn.ico`; it is not a project-authored branding asset.

The exact selected helper path is:

1. [`smtg_add_vst3plugin_with_pkgname`](https://github.com/steinbergmedia/vst3_cmake/blob/054c9143cbb8d47fc4694e473f2ee3b4d951a8f5/modules/SMTG_AddVST3Library.cmake)
   uses the SDK logo if `SMTG_PACKAGE_ICON_PATH` does not name an existing path.
2. [`smtg_target_make_plugin_package`](https://github.com/steinbergmedia/vst3_cmake/blob/054c9143cbb8d47fc4694e473f2ee3b4d951a8f5/modules/SMTG_AddSMTGLibrary.cmake)
   calls `smtg_target_add_folder_icon` in its Windows bundle branch when that
   path exists. The latter adds the actual two files and Windows attributes.

Setting `SMTG_PACKAGE_ICON_PATH` to an existing original project ICO before
`smtg_add_vst3plugin` is the supported replacement path in this selected SDK.
An empty or missing file path triggers fallback rather than omission. No direct
omit-icon option was found in these functions; disabling Windows bundle
creation also changes the resource/layout contract. No replacement setting or
asset was applied or tested here.

The freshly retrieved [pinned SDK README](https://github.com/steinbergmedia/vst3sdk/blob/3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96/README.md#trademark-and-logo-usage)
separately describes optional VST branding conditions. Its bytes match the
checkout: SHA-256
`83165df5693e3e77e58fad66b784a3e1b0c7eb8faedffd74fd5c4c453441f3b1`.
The practical release decision is to select and record an original owned icon,
or review the intended use of this actual SDK asset against the stated
conditions, then inspect the final staged Windows payload again. Neither an
MIT text match nor this file inventory establishes that branding decision.

## Hosted execution evidence and limits

The complete logs were inspected for these exact jobs:

| Job | Already executed result observed in the log |
| --- | --- |
| Linux `131852884056` | 8/8 native suites passed; 5.70 seconds; bundle inventory/copy/artifact completed |
| Windows `131852884109` | 7/7 applicable native suites passed; 5.80 seconds; bundle inventory/copy/artifact completed |

The extra Linux suite is its allocation interposition gate. Both logs retain
229,725 ABI-compared frames and zero maximum ABI audio error, all 45 descriptors
and conversions, plus the SDK validator's 47-passed/zero-failed summary. The
validator's documented teardown/unsupported-rate diagnostics remain in the
full logs; a passing summary is not a warning-free, arbitrary-format or DAW
qualification. This assignment observed these completed executions; it did not
rerun them or infer a macOS result.

The frozen wave-7 inventory tool inspected for this audit has SHA-256
`9f72e3c70b4b25008c40319b96e389b79cbcb6ab18821622c0f771b2c4071ad3`;
its test file has SHA-256
`c99f64ea9761e57ddf44a46981f728d310ff202e89a39d237adbcfff07a3f8af`.
Assignment 51 separately owns a later Windows reparse-point admission repair.
This audit's successful finite archive checks do not qualify that later change
or prove that the frozen live-filesystem admission handles every reparse type.
Use the current [status](../STATUS.md) for its exact integration and hosted gate.

## Retained evidence and next action

Fresh remote API observations, pinned README/license text, a separate finite
inspection script, structured results and import-tool output are retained under
`a52-dependency-artifact-audit` in the task workspace. The
[assignment note](../development/2026-11-13-pedals/52-dependency-artifact-audit.md)
records commands and hashes. Both external SDK sources, the original SDK lock,
notices, PDF and native implementation were left unchanged.

Integrate the documentation correction, qualify later inventory changes at their
own source revision, and inspect the final exact platform payload before any
release claim. The owner-selected project license, supplied PDF/source asset
permissions, future captures, intended names/branding, clean-system runtime
support, DAW/device operation and signing remain the specific open decisions in
[the project plan](../PLAN.md) and [rights inventory](../DEPENDENCIES_AND_RIGHTS.md).
