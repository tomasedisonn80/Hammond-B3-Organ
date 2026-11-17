# Heading/title helper correction — Native VST3 qualification

17 November 2026. A54, wave 9, continuing as the same accepted worker.
**Accept all four Native VST3 platform families for published source
`6287055a111dc4e2747564da3d48edc9b65e2e3e`, run `44026516616`, attempt 1.**
This acceptance concerns that exact source and workflow. It does not attach
the results to a later documentation closure commit or qualify other
project workflows.

The [successor Native VST3 run](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44026516616)
and all four jobs are completed/success. All four acquired actual runners;
none failed, was cancelled, remained unassigned, or required a rerun. The
[machine-readable review](../development/2026-11-16-heading-title-continuation/reports/a54-helper-vst3-hosted.json)
binds complete logs, terminal metadata, original artifacts, actual native
test output, source/dependency provenance and independently inspected
package bytes. No native executable was run locally by this reviewer.

## Source identity and unchanged VST3 inputs

The independently fetched Git commit object identifies tree
`c96fe07c4241f5afe423306945508a114506f0c2` and sole parent
`03c70c103a4a0dd72b323529416b909c19a4e139`. These match root's
[helper publication receipt](../development/2026-11-16-heading-title-continuation/reports/helper-branch-publication.json)
and every actual job's downloaded `provenance.json`. All provenance records
name run `44026516616`, attempt `1`, Release configuration and the expected
runner OS/architecture.

The workflow fetched at the exact successor source matches the repository
bytes and original reviewed workflow, SHA-256
`6bc30e3fcb880d456a5ec4af98e2d2950d5c340285948cd01dc230ba3625d734`.
A separate [input comparison](../development/2026-11-16-heading-title-continuation/reports/a54-helper-vst3-hosted/input-comparison.json)
confirms identical modes, paths and Git blob IDs for **290 tracked files**
across the explicitly listed VST3 workflow, plugin, core, include, CMake,
tools, data and notice scopes. The comparison includes original `fba1911`, prior `03c70c1` and current
`6287055` and is scoped to those paths;
this successor acceptance additionally rests on its own executed jobs.

The original accepted A54 note, VST3 review/report, local scheduling and
preset reviews, sanitizer-budget admission, and Windows byte-retention
supplement, prior `03c70c1` review and all retained artifacts remain unchanged.
All **102 prior frozen files** were rehashed before and after this review.
Current helper-source evidence uses a separate folder and replaces neither
prior source's records.

## Actual platform results

| Actual hosted job | Compiler and independently verified module | CTests | Actual module validator | CTest elapsed |
| --- | --- | --- | --- | ---: |
| [Linux GCC — 133848046935](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44026516616/job/133848046935) | GNU 13.3.0; ELF64 x86_64; X64 runner | 8/8 | 47 passed, 0 failed | 5.01 s |
| [macOS ARM — 133848046857](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44026516616/job/133848046857) | AppleClang 17.0.0.17000013; Mach-O64 arm64; ARM64 runner | 7/7 | 47 passed, 0 failed | 4.58 s |
| [macOS Intel — 133848046789](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44026516616/job/133848046789) | AppleClang 17.0.0.17000013; Mach-O64 x86_64; X64 runner | 7/7 | 47 passed, 0 failed | 7.51 s |
| [Windows MSVC — 133848046537](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44026516616/job/133848046537) | MSVC 19.44.35230.0; PE32+ x86_64; X64 runner | 7/7 | 47 passed, 0 failed | 7.32 s |

These are **29 executed CTests**, with zero failures, disabled tests or
skipped tests. The seven common gates are `test_native_install`,
`hammond_vst3_validator`, `test_native_controller`, `test_native_abi`,
`test_native_behavior`, `test_native_automation` and
`test_native_concurrency`. Linux also executes `test_native_realtime`.
The ELF-specific interception test is not configured on the other three
families; it is not counted as a skipped or passing non-Linux test.

Per-platform validation records retain actual commands, computed limits,
JUnit statuses and untruncated summaries:
[Linux](../development/2026-11-16-heading-title-continuation/reports/a54-helper-vst3-hosted/linux/validation.json),
[ARM macOS](../development/2026-11-16-heading-title-continuation/reports/a54-helper-vst3-hosted/mac_arm/validation.json),
[Intel macOS](../development/2026-11-16-heading-title-continuation/reports/a54-helper-vst3-hosted/mac_intel/validation.json),
and [Windows](../development/2026-11-16-heading-title-continuation/reports/a54-helper-vst3-hosted/windows/validation.json).
Architecture is established from actual runner provenance, the downloaded
inventory and independent parsing of the packaged module header. It is not
inferred solely from a matrix label.

## SDK and actual-module validator

Every job explicitly acquired SDK **3.8.1**, tag `v3.8.1_build_84`, and then
separately verified the acquired tree. Acquisition reports network use;
the independent verification reports none. Both records confirm five
primary licenses, the embedded JSON dependency and these exact checkouts:

| SDK path | Verified commit |
| --- | --- |
| Root | `3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96` |
| `base` | `fcf9da0bd27a16f7f03773a3a39822f28f5c8477` |
| `cmake` | `054c9143cbb8d47fc4694e473f2ee3b4d951a8f5` |
| `pluginterfaces` | `4f547e8e102b47de4a8b8aaf343c73b700786372` |
| `public.sdk` | `586dc5e6c8012c3e4b01c79389375cbe96bdb1da` |

Each downloaded lock is byte-identical to the repository lock, SHA-256
`ef3dfdf3feb5747967fe205ba196f5ef1b01457653f6ad7a62fffefd702ba965`.
The packaged primary SDK license and project notice also match their
expected original bytes.

The validator result is read from the **actual `hammond_vst3_validator`
CTest block**, whose command loads that platform's built `HammondB3.vst3`.
Its module/class scan reports VST 3.8.1, processor class
`19F9ADC0533F42B4B96BD51D6547E838` and controller class
`0DEE76AB26BC475ABF64F138C89FB0E0`. The SDK validator's build self-test is
not substituted for this executed module validation. Both packaged module
classes and their IDs match the lock.

The full actual-module validator output includes **16** occurrences of
`Failed to teardown test!` and **15** occurrences of
`64bit Audio Processing not supported.` on each platform. Those counts
match each corresponding original `fba1911` and prior `03c70c1` run exactly. Its explicit final result
is nevertheless **47 tests passed, 0 tests failed**, and CTest exits
successfully. The messages remain preserved and visible in the derived
records; this review does not claim a warning-free validator or infer the
cause of the teardown messages. Successful JUnit output may be truncated,
so these details come from complete `ctest.log` bytes.

## Native ABI, installation and real-time scope

Each independently executed ABI harness reports 47 descriptors, 701,642
assertions, 3,207 state round trips, 229,725 compared frames, 217,972 audible
frames and maximum audio error zero. Controller, behavior, automation and
concurrency completion summaries are retained in full, including the
concurrency cleanup probe. The fixed ABI summaries match the original
source's summaries; each successor result was separately executed.

All four installation CTests report **two Python methods run successfully**.
The unchanged exact-source fixture identifies them as
`test_install_move_and_load` and
`test_preflight_rejects_incomplete_bundle_without_mutating_prefix`.
They exercise explicit NativeVST3 component installation into a private
prefix, preservation of unrelated files and another plugin, refusal of
reinstallation without changing existing files, prefix relocation, and
loading the actual moved module from an unrelated working directory.
Every relocated ABI report equals that platform's direct ABI report.

The second method exercises real preflight failure paths: unqualified
installation does not implicitly stage the component; unbuilt, missing or
empty required payloads are rejected without changing the prefix; unsafe
library destinations are rejected. Complete installation JSON contains the
actual installed file hashes. A54 independently checked that these equal
the corresponding packaged file hashes, closing the link between installed,
relocated, inventoried and archived payloads.

Linux's additional gate records **193 regions**, **12/12** overload
calibrations and **8,945,157 assertions**. Its eight measured processing-path
rows have zero intercepted C++ `new` and `delete` operations. Positive
processor/controller construction and release calibration is retained,
along with the complete rows and scope statement. This measures Linux
calling-thread global C++ allocation interception; its timings establish
no device deadline or corresponding interception guarantee on macOS or
Windows.

## Exact package bytes and retention

All eight downloaded outer artifact ZIPs match their GitHub metadata
digests. For each family, build and staged inventory bytes are identical;
the internal archive matches `archive.sha256`; every regular payload file
matches its inventory path, size, SHA-256 and mode; no extra, missing,
symlink or special-file payload was accepted. Linux has four payload files;
each macOS and Windows bundle has six.

| Platform | Internal `HammondB3-Release.tar.gz` SHA-256 |
| --- | --- |
| Linux | `11c7981fc2e9b44dae7190b400adcbafefbe90505320953660c632e1e41040fa` |
| ARM macOS | `6b31c9e6671f645341f2d6b06f8922d5665205729c27dcc52df181036745d1e0` |
| Intel macOS | `dc75daa43752815f8052a41dfd51865179a7c38253fa412cb2b2d4babf48ee4b` |
| Windows | `0f7d354e2c15eb9f378726f4ed716497b22de9d53187e056203db70687516b2b` |

Outer artifact ZIP identities and internal archive identities are recorded
separately. Linux and both macOS module binaries match their original
and `03c70c1` runs' module hashes. The new Windows module has SHA-256
`b2a943876c57b62cde247d3749be6d1b0ee5486dfc1704b45ed8b09082ffdbe2`,
which differs from both earlier Windows modules. This review assigns no
cause to that byte difference; its new bytes, x86_64 PE32+ header,
installation and actual native gates are independently verified. It makes
no claim of binary reproducibility across all four platforms.

Complete decoded job logs are retained as deterministic gzip, including
the Windows stream's original carriage returns. Four original diagnostic
ZIPs preserve all original diagnostic text bytes. Selected original bundle
inventory, module metadata and archive-digest bytes are retained as
deterministic gzip. Thus Windows CRLF text is preserved inside binary
containers without relying on a new text-normalization exception.
The evidence inventory records both stored and decoded identities. All
1,103,972 decoded job-log bytes are retained; the Windows log includes its
1,951 carriage returns. Every complete CTest line was independently found
in its corresponding complete job log in order, stripping timestamp prefixes
and line-ending whitespace for that comparison only. The original streams
remain byte-identical.

Temporary bundle ZIPs are removed only after complete inspection; their
digests, artifact IDs, retained metadata and package identities remain in
the receipt. The retained
[artifact inspector](../development/2026-11-16-heading-title-continuation/reports/a54-helper-vst3-hosted/inspect_artifacts.py)
only parses files and archive bytes. It does not load a plugin, invoke a
native test, install a package, or mutate Git. Repeating its original
inspection requires obtaining the identified bundle ZIPs again and using a
fresh output location; its original output files are deliberately created
without clobbering.

## Boundaries and next step

This helper-source VST3 acceptance does not erase the original coherent local
240/242 result, separately passing unchanged diagnostics, original standalone
Windows C4244 failure/sanitizer cancellation, or the prior `03c70c1` Windows
C4702 failure and Intel preset-raster timeout. The preset workload and normal
30-second guard remain unchanged. Current standalone and ordinary CI workflows
have their own owners and receipts; this review does not invent their final
aggregate result. SDK/native
success does not establish all-DAW compatibility, physical MIDI/audio
behavior, hardware deadlines, instrument calibration, release signing or
notarization, accessibility, a custom VST3 editor, or literal whole-UI
reference-photo equality. Those project gates remain separate.

Root owns integration, staging, commits, pushes and later publications.
Preserve this report's exact source identity when recording the final
documentation closure. A54 performed read-only GitHub/artifact access,
local byte inspection and owned evidence writes, with no native build or
execution, hosted rerun, remote mutation, or additional worker credit.
