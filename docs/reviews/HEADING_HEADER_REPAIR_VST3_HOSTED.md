# Heading/title repair — successor Native VST3 qualification

17 November 2026. A54, wave 9, continuing as the same accepted worker.
**Accept all four Native VST3 platform families for published source
`03c70c103a4a0dd72b323529416b909c19a4e139`, run `44021714644`, attempt 1.**
This acceptance concerns that exact source and workflow. It does not attach
the results to a later documentation closure commit or qualify other
project workflows.

The [successor Native VST3 run](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44021714644)
and all four jobs are completed/success. All four acquired actual runners;
none failed, was cancelled, remained unassigned, or required a rerun. The
[machine-readable review](../development/2026-11-16-heading-title-continuation/reports/a54-repair-vst3-hosted.json)
binds complete logs, terminal metadata, original artifacts, actual native
test output, source/dependency provenance and independently inspected
package bytes. No native executable was run locally by this reviewer.

## Source identity and unchanged VST3 inputs

The independently fetched Git commit object identifies tree
`f639acf69061a4b66a0bd3d2219b1ed890e74e42` and sole parent
`fba1911259346bfc6fd3ba7ec78b5cf6c4d1a6b2`. These match root's
[repair publication receipt](../development/2026-11-16-heading-title-continuation/reports/hosted-repair-publication.json)
and every actual job's downloaded `provenance.json`. All provenance records
name run `44021714644`, attempt `1`, Release configuration and the expected
runner OS/architecture.

The workflow fetched at the exact successor source matches the repository
bytes and original reviewed workflow, SHA-256
`6bc30e3fcb880d456a5ec4af98e2d2950d5c340285948cd01dc230ba3625d734`.
A separate [input comparison](../development/2026-11-16-heading-title-continuation/reports/a54-repair-vst3-hosted/input-comparison.json)
confirms identical modes, paths and Git blob IDs for **290 tracked files**
across the explicitly listed VST3 workflow, plugin, core, include, CMake,
tools, data and notice scopes. The comparison is scoped to those paths;
this successor acceptance additionally rests on its own executed jobs.

The original accepted A54 note, VST3 review/report, local scheduling and
preset reviews, sanitizer-budget admission, and Windows byte-retention
supplement remain unchanged. The successor evidence uses a separate folder
and does not replace the original source's records.

## Actual platform results

| Actual hosted job | Compiler and independently verified module | CTests | Actual module validator | CTest elapsed |
| --- | --- | --- | --- | ---: |
| [Linux GCC — 133832484798](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44021714644/job/133832484798) | GNU 13.3.0; ELF64 x86_64; X64 runner | 8/8 | 47 passed, 0 failed | 5.11 s |
| [macOS ARM — 133832485032](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44021714644/job/133832485032) | AppleClang 17.0.0.17000013; Mach-O64 arm64; ARM64 runner | 7/7 | 47 passed, 0 failed | 4.08 s |
| [macOS Intel — 133832485052](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44021714644/job/133832485052) | AppleClang 17.0.0.17000013; Mach-O64 x86_64; X64 runner | 7/7 | 47 passed, 0 failed | 13.25 s |
| [Windows MSVC — 133832485061](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44021714644/job/133832485061) | MSVC 19.44.35230.0; PE32+ x86_64; X64 runner | 7/7 | 47 passed, 0 failed | 7.47 s |

These are **29 executed CTests**, with zero failures, disabled tests or
skipped tests. The seven common gates are `test_native_install`,
`hammond_vst3_validator`, `test_native_controller`, `test_native_abi`,
`test_native_behavior`, `test_native_automation` and
`test_native_concurrency`. Linux also executes `test_native_realtime`.
The ELF-specific interception test is not configured on the other three
families; it is not counted as a skipped or passing non-Linux test.

Per-platform validation records retain actual commands, computed limits,
JUnit statuses and untruncated summaries:
[Linux](../development/2026-11-16-heading-title-continuation/reports/a54-repair-vst3-hosted/linux/validation.json),
[ARM macOS](../development/2026-11-16-heading-title-continuation/reports/a54-repair-vst3-hosted/mac_arm/validation.json),
[Intel macOS](../development/2026-11-16-heading-title-continuation/reports/a54-repair-vst3-hosted/mac_intel/validation.json),
and [Windows](../development/2026-11-16-heading-title-continuation/reports/a54-repair-vst3-hosted/windows/validation.json).
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
match each corresponding original run exactly. Its explicit final result
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
| Linux | `2e5960f1a64accb331816d05e8df37001f9a06431db5d9c6532a0f7a5b71d28e` |
| ARM macOS | `7b4b5a033b1e5095b4c571bc87965323b6a6679cbb88e5a9c7da8385f3925d58` |
| Intel macOS | `b699a7d7debe79754d48f7954e08cbd8523afe0850f34e7c112e5fb06107c49d` |
| Windows | `4d1ac4fc8fb11c0508aac0e8ab4574476f8f90a93194b03264c2db3aff867fd4` |

Outer artifact ZIP identities and internal archive identities are recorded
separately. Linux and both macOS module binaries match their original
run's module hashes. The new Windows module has SHA-256
`76ab6ba96a2ccd800c94552e2b671c85f30e5f2d3667c33405a614d02e28d429`,
which differs from the original Windows module. This review assigns no
cause to that byte difference; its new bytes, x86_64 PE32+ header,
installation and actual native gates are independently verified. It makes
no claim of binary reproducibility across all four platforms.

Complete decoded job logs are retained as deterministic gzip, including
the Windows stream's original carriage returns. Four original diagnostic
ZIPs preserve all original diagnostic text bytes. Selected original bundle
inventory, module metadata and archive-digest bytes are retained as
deterministic gzip. Thus Windows CRLF text is preserved inside binary
containers without relying on a new text-normalization exception.
The evidence inventory records both stored and decoded identities.

Temporary bundle ZIPs are removed only after complete inspection; their
digests, artifact IDs, retained metadata and package identities remain in
the receipt. The retained
[artifact inspector](../development/2026-11-16-heading-title-continuation/reports/a54-repair-vst3-hosted/inspect_artifacts.py)
only parses files and archive bytes. It does not load a plugin, invoke a
native test, install a package, or mutate Git. Repeating its original
inspection requires obtaining the identified bundle ZIPs again and using a
fresh output location; its original output files are deliberately created
without clobbering.

## Boundaries and next step

This successor VST3 acceptance does not erase the original coherent local
240/242 result, separately passing unchanged diagnostics, or the original
standalone workflow's failure/cancellation. The successor standalone and
ordinary CI workflows have their own owners and receipts. SDK/native
success does not establish all-DAW compatibility, physical MIDI/audio
behavior, hardware deadlines, instrument calibration, release signing or
notarization, accessibility, a custom VST3 editor, or literal whole-UI
reference-photo equality. Those project gates remain separate.

Root owns integration, staging, commits, pushes and later publications.
Preserve this report's exact source identity when recording the final
documentation closure. A54 performed read-only GitHub/artifact access,
local byte inspection and owned evidence writes, with no native build or
execution, hosted rerun, remote mutation, or additional worker credit.
