# Heading/title continuation — exact-source Native VST3 qualification

17 November 2026. A54, wave 9, same worker throughout all local admission
follow-ups. **Accept the four Native VST3 platform families for published
commit `fba1911259346bfc6fd3ba7ec78b5cf6c4d1a6b2`, attempt 1.** This is
qualification of the named workflow and source, not a green result for every
project workflow or the complete local standalone suite.

The [Native VST3 run](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44016021543)
is completed/success. The
[machine-readable review](../development/2026-11-16-heading-title-continuation/reports/a54-vst3-hosted.json)
binds terminal job metadata, complete decoded job logs, original diagnostic
artifacts, actual provenance, SDK verification, complete CTest output, and
independently inspected bundle bytes. All four jobs acquired actual runners;
none failed, was cancelled, or remained unassigned. There was one attempt,
with no rerun requested by A54.

## Exact source and platform results

GitHub's exact commit object, root's
[publication receipt](../development/2026-11-16-heading-title-continuation/reports/source-publication.json),
and every downloaded `provenance.json` agree on source
`fba1911259346bfc6fd3ba7ec78b5cf6c4d1a6b2` and tree
`b62f212300d75633346ab8fc5ffdd722255fe00a`. The published parents are
`9d60dbf462a90fe422fd4e69757fe202264acb7c` and
`835755a9069c25ce55bc2c231547458b4b3ffce4`. Every provenance record names
run `44016021543`, attempt `1`, and Release configuration. The exact fetched
workflow hashes to
`6bc30e3fcb880d456a5ec4af98e2d2950d5c340285948cd01dc230ba3625d734`,
matching the reviewed workflow bytes.

| Actual hosted job | Compiler and module architecture | CTests | Actual module validator | Native CTest time |
| --- | --- | --- | --- | ---: |
| [Linux GCC — 133814025096](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44016021543/job/133814025096) | GNU 13.3.0; ELF64, x86_64; runner X64 | 8/8, zero skipped | 47 passed, 0 failed | 4.88 s |
| [macOS AppleClang — 133814025233](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44016021543/job/133814025233) | AppleClang 17.0.0.17000013; Mach-O64, arm64; runner ARM64 | 7/7, zero skipped | 47 passed, 0 failed | 3.82 s |
| [macOS Intel AppleClang — 133814024868](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44016021543/job/133814024868) | AppleClang 17.0.0.17000013; Mach-O64, x86_64; runner X64 | 7/7, zero skipped | 47 passed, 0 failed | 12.93 s |
| [Windows MSVC x64 — 133814025269](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44016021543/job/133814025269) | MSVC 19.44.35230.0; PE32+, x86_64; runner X64 | 7/7, zero skipped | 47 passed, 0 failed | 8.17 s |

These are 29 actual CTest executions across the four jobs. The seven common
tests are `test_native_install`, `hammond_vst3_validator`,
`test_native_controller`, `test_native_abi`, `test_native_behavior`,
`test_native_automation`, and `test_native_concurrency`. Linux additionally
executes `test_native_realtime`. The other platforms have no skipped
real-time testcase: that ELF-specific test is outside their configured set.

Architecture was checked three ways: actual runner provenance, the native
bundle inventory, and independent parsing of the downloaded module's
ELF/Mach-O/PE header. The table does not infer Apple Silicon merely from
the `macos-15` runner label. Per-platform detailed evidence is retained in
[Linux](../development/2026-11-16-heading-title-continuation/reports/a54-vst3-hosted/linux/validation.json),
[ARM macOS](../development/2026-11-16-heading-title-continuation/reports/a54-vst3-hosted/mac_arm/validation.json),
[Intel macOS](../development/2026-11-16-heading-title-continuation/reports/a54-vst3-hosted/mac_intel/validation.json),
and [Windows](../development/2026-11-16-heading-title-continuation/reports/a54-vst3-hosted/windows/validation.json).

## SDK identity and actual native execution

Each job explicitly acquired and then independently verified SDK **3.8.1**,
tag `v3.8.1_build_84`. The actual verification records contain the following
five checkouts, five verified primary licenses, and the verified embedded
JSON dependency. The acquisition record reports network use; the separate
verification record reports no network use. All downloaded lock-file bytes
match the repository lock, SHA-256
`ef3dfdf3feb5747967fe205ba196f5ef1b01457653f6ad7a62fffefd702ba965`.

| SDK path | Verified commit |
| --- | --- |
| Root | `3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96` |
| `base` | `fcf9da0bd27a16f7f03773a3a39822f28f5c8477` |
| `cmake` | `054c9143cbb8d47fc4694e473f2ee3b4d951a8f5` |
| `pluginterfaces` | `4f547e8e102b47de4a8b8aaf343c73b700786372` |
| `public.sdk` | `586dc5e6c8012c3e4b01c79389375cbe96bdb1da` |

The SDK validator's build self-test is not substituted for validation of
HammondB3. The retained complete `ctest.log` records the validator command
against the actual built bundle and its **47 passed / 0 failed** result on
each platform. It reports SDK 3.8.1 and the unchanged processor/controller
class IDs `19F9ADC0533F42B4B96BD51D6547E838` and
`0DEE76AB26BC475ABF64F138C89FB0E0`.

Every native ABI execution separately reports 47 descriptors, 701,642
assertions, 3,207 state round trips, 229,725 compared frames, 217,972 audible
frames, and maximum audio error zero. Controller, behavior, automation, and
concurrency summaries are preserved in full. Their positive completion is
read from actual executable output and CTest results, not inferred from
the bundle merely compiling.

Linux's additional ELF gate records 193 checked regions, all 12/12 overload
calibrations, 8,945,157 assertions, and zero intercepted C++ `new`/`delete`
operations in the measured processing paths. Positive module construction
and destruction calibration is retained. Its explicit scope is Linux
calling-thread global C++ allocation interception; measured timings do not
establish audio-device deadlines or equivalent interception on other systems.

JUnit truncates long successful output in several cases. A54 therefore used
the complete, untruncated `ctest.log` to read the actual validator result,
installation JSON, and Linux real-time summary. The original JUnit is also
preserved, with zero failures, disabled tests, or skipped tests in every job.

## Installation, relocation, and packaging evidence

All four `test_native_install` executions report **two Python methods run
successfully**. The exact-source
[fixture](../../plugins/vst3/tests/test_native_install.py) stages only the
explicit NativeVST3 component into a private prefix, preserves unrelated
files and another plugin, refuses a repeated install without altering the
prefix, relocates the prefix, and loads the real moved module from an
unrelated working directory. Its relocated ABI report equals the original
ABI report on every platform, including 47 descriptors and zero audio error.

The second method exercises actual install preflight: unqualified install
does not implicitly stage the native component; unbuilt, missing, and empty
required payloads are rejected without mutating the prefix; unsafe install
library paths are rejected. These are executed negative tests, not a
packaging checklist inferred from file presence.

A54 downloaded both artifacts for every platform, checked each ZIP against
its GitHub artifact digest, and compared the build and staged inventory
bytes exactly. The bundle's internal archive digest matches `archive.sha256`.
Every regular file in each archive matches the inventory's path, byte count,
SHA-256, and mode; no extra payload files were accepted. Linux has four
payload files; each macOS bundle and Windows bundle has six.

| Platform | Internal `HammondB3-Release.tar.gz` SHA-256 |
| --- | --- |
| Linux | `b8e0a81399bf6b3cd0dd01c6f5660229e5f965a8e2082f8f998906e86da90ba1` |
| ARM macOS | `2c10e5fb79227bab90c272e6b98de44c11441fe23c325d5b265cbf875cd82f97` |
| Intel macOS | `12a49e29adcc157f0006d8e76537f50c0c987c93c5dae982e28097ba6ee16165` |
| Windows | `ee5fd88f1e0c8a965166627d387c9813711b6988ed9aee91a178f0d14aa1a31c` |

These are internal package hashes, distinct from GitHub's outer artifact ZIP
digests. Both are recorded in the machine-readable evidence. Original
diagnostic ZIPs and complete compressed job logs are retained; temporary
downloaded bundle ZIPs are removed after inspection. Their identities,
inventories, metadata, artifact IDs, and remote retention dates remain.

## Boundaries and handoff

This original-source acceptance does not erase the coherent local
**240/242** result or its three separately passing unchanged diagnostics.
The three local scheduling admissions and
[preset timing review](PRESET_RASTER_LOCAL_TIMING_REVIEW.md) remain unchanged.
The separate standalone/core workflows retain their own outcomes. Any later
source publication requires an explicit source/input comparison and its own
reported hosted evidence; this review must not be silently relabeled with a
successor SHA.

No native DAW session, physical MIDI/audio device, hardware deadline,
calibrated instrument match, supported-host matrix, release signing,
notarization, accessibility, or literal whole-UI 1:1 result is established.
macOS build signatures and signature resources are not Developer ID release
qualification. The headless VST3 adapter's passing SDK/UI-interface checks
do not qualify the standalone reference-photo presentation or a custom
plugin editor. The project's remaining phase and fidelity gates remain open.

Root owns repairs, final integration, commits, pushes, and future source
releases. A54 used read-only GitHub access, read-only artifact inspection,
and owned documentation writes only: no native execution, local build,
remote mutation, rerun, or additional worker credit. The new
[A54 note](../development/2026-11-16-heading-title-continuation/notes/A54.md)
records this handoff and the same worker's earlier bounded reviews.
