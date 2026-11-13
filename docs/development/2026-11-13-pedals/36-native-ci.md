# Assignment 36 — native CI and bundle inventory

**Owner:** `/root/w06_a36_native_ci`

**Wave:** 6

**Session:** `2026-11-13-pedals`

## Ownership and implemented result

Owned only `.github/workflows/native-vst3.yml`,
`tools/native_bundle_inventory.py`, `tests/test_native_bundle_inventory.py`,
[VST3_CI.md](../../VST3_CI.md) and this note. Read the standing/current handoff,
native contract/build docs, SDK lock/notices, existing CI and actual macOS runner
record. No shared status, core CI, CMake, native source, SDK source, manifest or
DSP file was changed by this worker. No commit, push or child dispatch was made;
root owns integration and publication.

The separate workflow has Linux GCC, macOS AppleClang and Windows MSVC x64
Release jobs. It reuses the existing exact action pins, read-only contents
permission and nonretained checkout credentials. Acquisition explicitly selects
a new external SDK path; configure verifies that path without fetching. Root
provided the build-only `hammond_vst3_test_inputs` aggregate so one verbose native
CTest pass owns JUnit and complete logs without a stale CI executable list.
Fourteen-day diagnostic and bundle artifacts retain actual source/SDK/toolchain
identity, module-info, component notices, a bounded file inventory and a
mode-preserving tar payload. No SDK sources are packaged.

The inventory uses only the Python standard library. It independently hashes
actual regular files, checks the pinned license/source notice payload, observes
ELF/PE/Mach-O platform/CPU facts and publishes only a complete new report. Bounds,
symlink/special-file rejection, configuration/source provenance and limitations
are specified in [VST3_CI.md](../../VST3_CI.md). The tests require no SDK, network,
plugin loader or executable native fixture.

## Frozen code and source scope

The SDK-free test source is an isolated `git archive` of published W5 commit
`88c36b4a72a07f6498f73279f25023278accd350`, tree
`354b1e7660c25435f2f97617450cc86e76b26ce3`, with exactly the three code/workflow
overlays below. It does not consume concurrent workers' unfinished native files.
Source manifest `a36-source-overlay.json` is 866 bytes, SHA-256
`64a0f3cad1c8da8a850d8903496e2148cdbb85630460041eda70eca5891a9698`.
Live owned code and these frozen overlays were byte-identical at the final check.

| Owned executable input | Bytes | SHA-256 |
| --- | ---: | --- |
| `.github/workflows/native-vst3.yml` | 8261 | `2376f41bfd96ff5afa2c821299588de05e5c49221879aef91a82074955649721` |
| `tools/native_bundle_inventory.py` | 17028 | `2ecaf176fe8350868476f329e5d4d1d41cf08c6bd4c676e5d439b25654f72cce` |
| `tests/test_native_bundle_inventory.py` | 18331 | `a9b321d144a8cc1421c7e6588dc72e40d93fe7ea2db6cd490df5203b650c77cf` |

Local environment: Linux x86-64, GCC 14.2.0, Python 3.12.14, CMake/CTest 3.31.6.
The SDK-free source/build directories are `a36-source` and `a36-build` under
`/workspace/scratch/f364bc93d920`. CMake/CTest executables used the absolute
prefix `/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/`.

## Commands actually executed and results

Paths below use the common scratch parent `..` relative to the repository.

```sh
python3 tests/test_native_bundle_inventory.py
python3 tools/acquire_vst3_sdk.py --destination ../a36-sdk-checkout
python3 tools/acquire_vst3_sdk.py --verify-existing ../a36-sdk-checkout
cmake -S ../a36-source -B ../a36-build -DCMAKE_BUILD_TYPE=Release
ctest --test-dir ../a36-build -R '^python_test_native_bundle_inventory$' -V \
  --output-log ../a36-focused-test.log --output-junit ../a36-focused-test.xml
python3 tools/native_bundle_inventory.py \
  --bundle ../a33-native-build/VST3/Release/HammondB3.vst3 \
  --output ../a36-artifacts/actual-bundle-inventory.json \
  --source-manifest ../a33-native-overlay.json
```

The direct Python run passed **16/16 methods** in 0.301 seconds. The independent
SDK-free configure passed, discovered the new Python file through the existing
test registration, and its focused CTest passed **1/1**, all sixteen methods,
zero failures, in **0.72 seconds**. It did not build or claim the full C++ suite.
Linux exercised actual symlinks, a FIFO, a publication race, Unicode CLI paths
and case-colliding files. Windows fixtures have explicit fallback mode checks
when the filesystem cannot create privileged symlinks or POSIX special files;
those fallbacks must not be reported as actual native filesystem operations.

The sixteen methods also cover independent file hashes/counts/modes, opaque SDK
module-info bytes, six thin platform/CPU fixtures, 32/64-bit universal-Mach-O
tables and malformed slice extents, wrong/truncated headers, required resources,
license/notice tampering, extra payload, duplicate modules, strict lock shapes,
source identity, all configured bounds, no-clobber publication failures and
copy identity. Synthetic headers do not assert that those files can be loaded.

The fresh explicit SDK acquisition succeeded with `network_used: true`, all
five checkout commits, five primary license identities and embedded parser
verified. A separate read-only verification then succeeded with
`network_used: false`. The new destination was outside both the source tree and
the SDK used by other agents. No configure or build used this new checkout;
this check establishes actual helper acquisition/verification behavior. The
helper input SHA-256 was
`7e25134bde98d5a1886bd3724331495d1a07856526f87da606ae250b57f5bf86`.

Static workflow checks used the already installed local YAML parser, without
adding a runtime/repository dependency. They checked the three triggers, exact
matrix/pins, credentials, permissions, timeout and artifact retention; all
**seven shell blocks** passed `bash -n`, and both embedded Python blocks compiled.
The aggregate target and JUnit invocation were present. These checks did not
execute GitHub actions or establish hosted native platform results.

## Actual Linux payload transport

The inventory operated on the existing assignment-33 bundle at
`a33-native-build/VST3/Release/HammondB3.vst3`: four regular files,
**444239 bytes**, ELF64 Linux x86-64. This worker did not compile that module.
The report labels its actual archive-plus-overlay source by
`a33-native-overlay.json`, 1835 bytes, SHA-256
`7d3e645a31698a42fb699f0a834f8a3cbadbea58c0e483c4bfb3112c313b50d6`;
it does not attribute the native binary to clean published W5 source.

| Bundle file | Bytes | Mode | SHA-256 |
| --- | ---: | --- | --- |
| `Contents/x86_64-linux/HammondB3.so` | 434168 | `0755` | `d87353b237e52c8d1f91af27933493a4cf78ba4a06af4a96c9930c0ecec1d3ff` |
| `Contents/Resources/moduleinfo.json` | 1090 | `0644` | `d621a2149b6c8b8bac9a84d40bed21ed8de9fbeb9a8708ad44cf890050e56184` |
| `Contents/Resources/VST3_SDK_LICENSE.txt` | 1094 | `0644` | `e86d79e19e4a33ebc442d2e0d083887dfc75a2a8de9fe17eeddedb84810ad74e` |
| `Contents/Resources/THIRD_PARTY_NOTICES.md` | 7887 | `0644` | `a3aa1900ec8b584bfe0879d0d8c7c1af3148dc23729d01a62e26ed428b61c2f6` |

Executed the workflow's copy/inventory/tar operations against this payload in
`a36-artifacts/staged/HammondB3.vst3`. The second inventory was byte-identical.
Opened the produced tar without extracting it and independently compared every
member's bytes, size and mode to the inventory: all four files matched, no
duplicate member or unexpected/special payload. The archive is 184095 bytes,
SHA-256 `589d2518d74d2aa876ec2edffc0903cfa5f0a7f828e0ae4291bb2ee45c1fffac`.
This identifies this one locally produced archive; archive reproducibility,
installability and signing were not tested.

The SDK writer's actual `moduleinfo.json` has trailing commas. Inspection led to
retaining it as opaque bytes; strict-JSON parsing or rewriting that SDK output
would impose an unsupported grammar. SDK lock parsing remains strict JSON.
All completed local gates above passed; no failed production test was hidden
or repaired by this assignment.

### Retained local receipts

These scratch receipts support the durable facts above; hosted jobs must create
and retain their own exact-revision artifacts after publication.

| Receipt | Bytes | SHA-256 |
| --- | ---: | --- |
| `a36-sdk-acquisition.log` | 2262 | `43fa7745371a0d1c33473ca06aade6783ba601d84ac06c9ed6a1e58d93b9d6a5` |
| `a36-sdk-verification.log` | 571 | `34a34f04c0c4a15cdb75190b1145188a8f21ae672b602193338859215036e9aa` |
| `a36-focused-test.log` | 4593 | `3092b408f2fd0442b76493eccf5d9b1730c0dd6e0613486bebff3e42a2a59f5e` |
| `a36-focused-test.xml` | 1509 | `c7cc3c7026895ea26b0e193391b235fd482c75c6ca82dfaab9762611aae34c8b` |
| `a36-artifacts/actual-bundle-inventory.json` | 1852 | `fd6cd061114e4801a149eba5ea8e3ad71f66b20f57bbd1a9d7b73862c51e00b4` |
| `a36-artifacts/transport-check.json` | 248 | `849bbc5e07086dd6039faa794b40f6bfefe726492b0808c9d5d17ffec2ff2e9e` |

## Validator and hosted evidence boundaries

Root's inspection of the pinned validator and actual module log establishes the
47-passed/0-failed/exit-0 summary together with **nine unsupported-rate
`setupProcessing` diagnostics and sixteen contradictory cleanup diagnostics**.
The workflow retains complete verbose/log/JUnit output; it does not filter,
reinterpret or hide these messages. The three supported rates, float32-only
processing and correct repeated-state behavior are unchanged. Assignments 34/35
own independent loaded-module ABI/behavior evidence; their native checks were
not rerun by this worker.

The existing W5 core run first failed to acquire a `macos-15` hosted runner, with
empty runner identity, zero steps and explicit capacity annotations. The single
targeted retry later actually ran and passed 65/65 suites in 45.86 seconds; W5
run 43404272839 attempt 2 concluded success. The
[runner record](../../reviews/PEDAL_RUNNER_AVAILABILITY.md) retains both events.
No platform label was changed to obscure infrastructure failure. This historical
core result is distinct from the new native workflow, **not yet run at freeze**.

## Handoff and next gate

Root should integrate these five frozen files with the completed native inputs,
verify the build aggregate/full native CTest from one coherent snapshot, update
shared status and publish under the standing authorization. Then observe the
three native hosted jobs and their complete artifacts, recording actual source
commit, runner architecture, SDK/validator diagnostics and any acquisition or
compiler/test failure. Do not infer a hosted pass from YAML checks or repeat a
capacity retry without new recovery evidence. Preserve the core SDK-free gate.

Future agents adding native tests must maintain CMake registration and the native
test naming contract, keep acquisition explicit and logs complete, and inventory
the exact newly built payload. A changed binary needs new qualification. DAW and
device operation, native UI, signatures/installers, runtime redistribution,
project-wide rights and physical calibration remain separate gates.
