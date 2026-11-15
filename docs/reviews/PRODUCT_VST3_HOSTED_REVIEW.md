# Product continuation: primary VST3 hosted review

## Result and exact source

**All three Native VST3 jobs passed for published commit
`d8c39f7986746eacc991747153c7dbb012bb9a32`, tree
`edf67b978f93e8dbea6537ce92d3928c171bc1f3`.** A52 independently fetched the
[run](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43668397341),
job metadata, complete decoded primary job logs, commit metadata and artifact
metadata. The commit's parent is `d556da017ea0a5d4f2d231416782dbc5066e58c2`.
The remote main reference agreed when inspected. The checkout logs name the
exact commit; the successful provenance step checks event-SHA equality and a
clean tracked checkout, then writes its tree identity to the diagnostics artifact.

No failed selected native test or compatibility regression was found. This is
qualification of the named **Release headless VST3 workloads**. It does not
establish a DAW journey, physical controller/audio-device acceptance or a later
source's qualification. A52 ran no local build or runtime test and changed no
production source, workflow or shared status file.

The [structured primary report](../development/2026-11-15-product-continuation/reports/A52-vst3-hosted.json),
[bounded original excerpts](../development/2026-11-15-product-continuation/reports/A52-vst3-primary-excerpts.txt)
and [independent compatibility receipt](../development/2026-11-15-product-continuation/reports/A52-vst3-compatibility.json)
retain identities, exact counters, timings, source comparisons and limitations.

## What each platform executed

| Job | Actual platform and compiler | CMake / Python | Selected CTest result |
| --- | --- | --- | --- |
| [Linux 132672792107](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43668397341/job/132672792107) | Ubuntu 24.04.5, x86_64; GCC 13.3.0, package `13.3.0-6ubuntu2~24.04.1` | 3.31.6 / 3.12.16 | **8/8**, 4.24 s |
| [macOS 132672791908](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43668397341/job/132672791908) | macOS 15.8.2, ARM64; AppleClang 17.0.0.17000013, driver `clang-1700.0.13.5`; Xcode 16.4 / MacOSX15.5 SDK | 4.4.5 / 3.12.10 | **7/7**, 4.09 s |
| [Windows 132672792119](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43668397341/job/132672792119) | Windows Server 2022, x64; MSVC 19.44.35230.0, tools directory 14.44.35207; Windows SDK 10.0.26100.0 | 3.31.6 / 3.12.10 | **7/7**, 7.05 s |

Linux/macOS use Unix Makefiles and `CMAKE_BUILD_TYPE=Release`; Windows uses
`Visual Studio 17 2022 -A x64` and the selected Release configuration. All
configure with testing and VST3 enabled. The workflow builds the
`hammond_vst3_test_inputs` aggregate before this required, nonempty selection:

```sh
cmake --build build-native --config Release \
  --target hammond_vst3_test_inputs --parallel 2 --verbose
ctest --test-dir build-native -C Release -V --no-tests=error --timeout 300 \
  -R '^(hammond_vst3_validator|test_native_)' \
  --output-junit "$GITHUB_WORKSPACE/native-ci-logs/ctest.xml"
```

The successful commands and the individual results are in the primary excerpts;
their definition is in the unchanged [workflow](../../.github/workflows/native-vst3.yml).
This selection does not execute the complete core or standalone suite. Native
VST3 Release results are also separate from the project's sanitizer jobs.

| Selected test | Observed scope on all three platforms, except where stated |
| --- | --- |
| `test_native_install` | **Two Python methods** per platform: explicit component staging, byte-preserving relocation and real-module ABI loading; invalid/incomplete-payload and no-clobber checks. The relocated ABI result matches the built-bundle ABI counters. |
| `hammond_vst3_validator` | **47 passed, 0 failed** per platform against the actual `HammondB3.vst3` bundle. |
| `test_native_controller` | **138,215 checks**, 3,984 threshold cases, 411 string round trips, 469 rejected streams and 1,600 selector restores per platform. |
| `test_native_abi` | **701,642 assertions**, 47 descriptors, 2,140 conversions, 3,207 state round trips, six lifecycle sequences and 229,725 compared frames per platform; maximum audio error 0. |
| `test_native_behavior` | **29,455,970 checks**, 234,185 direct-reference frames, 618,550 exact channel samples, 75 rejected callbacks, 71 rejected state loads and three rate changes per platform. |
| `test_native_automation` | Six retained legacy-45 score cases plus **72 preset commands**, 198 preset thresholds, three alias cases, three preset restores and nine preset partitions; 102,156 direct-reference frames and maximum error 0 per platform. |
| `test_native_concurrency` | Three rates, 24 controlled rounds, 3,072 stress accepted loads and 3,072 publication-only saves; cleanup observes worker stop and join. Each platform reports maximum audio error 0. Scheduling-dependent counters differ and remain separate in the report. |
| `test_native_realtime` | **Linux only:** 193 measured regions, 12/12 overload calibration, 8,945,157 assertions and zero observed calling-thread global C++ `new`/`delete` calls in the admitted paths. macOS and Windows do not register or execute this test. |

The Linux allocation result covers the calibrated ELF/module interposition and
calling thread. It does not cover every allocator, another thread or another
platform. Its timings are recorded observations, explicitly not device deadlines.

## SDK identity and validator interpretation

Every job explicitly acquires and verifies the locked **Steinberg VST3 SDK
3.8.1**, tag `v3.8.1_build_84`. Acquisition reports network use; the subsequent
verification and CMake admission report no network use. The five verified Git
checkouts are identical across all three logs:

| SDK checkout | Commit |
| --- | --- |
| Root | `3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96` |
| `base` | `fcf9da0bd27a16f7f03773a3a39822f28f5c8477` |
| `cmake` | `054c9143cbb8d47fc4694e473f2ee3b4d951a8f5` |
| `pluginterfaces` | `4f547e8e102b47de4a8b8aaf343c73b700786372` |
| `public.sdk` | `586dc5e6c8012c3e4b01c79389375cbe96bdb1da` |

Each verifier admits five primary licenses and the embedded JSON dependency.
The [lock](../../data/dependencies/vst3-sdk-lock.json) supplies their identities;
the bundled SDK license SHA-256 is
`e86d79e19e4a33ebc442d2e0d083887dfc75a2a8de9fe17eeddedb84810ad74e`.
The build separately runs **51 SDK validator self-tests with zero failures** on
each platform. Those 51 are SDK self-tests, not another 51 Hammond checks and
not additional CTest entries.

The 47-check plug-in validator explicitly reports **no MIDI Mapping interface,
no MIDI Learn interface, no exported programs and no `IUnitInfo`**. It also
reports that 64-bit audio processing is unsupported, and that mono output is
unsupported with stereo proposed. These accepted capability declarations do not
become implemented features merely because their validator checks succeed.
The inspected processor accepts 32-bit sample processing at its existing
44.1/48/96 kHz rates. There is no custom VST3 editor; the standalone gallery
does not depict a plugin editor.

## Bundle, factory exports and packaging

The SDK loader and native ABI fixture open each real bundle, validate its
structure, inspect the factory and instantiate its two expected classes. The
fixture rejects an unknown class identity and verifies the processor's separate
controller relationship. The unchanged [factory](../../plugins/vst3/Factory.cpp)
and [identity definitions](../../plugins/vst3/PluginIds.h) expose version 0.1.0:

- Processor: `19f9adc0-533f-42b4-b96b-d51d6547e838`, **Hammond B3 Nominal**,
  `Instrument|Synth`.
- Controller: `0dee76ab-26bc-475a-bf64-f138c89fb0e0`, **Hammond B3 Nominal Controller**.

This is executed factory/loader evidence. No separate complete `nm` or `dumpbin`
symbol-table audit was performed by A52. The inventory tool itself reads binary
format/CPU facts; it does not substitute for the actual loader's export checks.

The executed [install fixture](../../plugins/vst3/tests/test_native_install.py)
installs `NativeVST3` into a private prefix, preserves unrelated files and an
unrelated plugin, refuses overwrite, moves the prefix, and loads the moved bundle
from an unrelated working directory using a copied reference profile. It compares
all payload hashes before and after loading. This is local staging/relocation
qualification, with no installation into a user's DAW plugin directory.

| Platform | Inventoried payload | Native module SHA-256 |
| --- | --- | --- |
| Linux | **4 files, 479,087 bytes**, ELF x86_64; module `Contents/x86_64-linux/HammondB3.so` | `3205e1d2979cfe474f4dbfe76eecb57d3a4042bd6f1734fde1a682d90da8dd7b` |
| macOS | **6 files, 475,598 bytes**, Mach-O ARM64; module `Contents/MacOS/HammondB3` | `41e75f25a2b0bd5741553803a750f9616960fecf2db8f15b3552db1cae452488` |
| Windows | **6 files, 674,712 bytes**, PE x86_64; module `Contents/x86_64-win/HammondB3.vst3` | `3712087838cbb7cfd58feeebdd9f75f984a435724d2321e5b1b775e369ecd990` |

All carry `moduleinfo.json`, `VST3_SDK_LICENSE.txt` and
`THIRD_PARTY_NOTICES.md`. macOS additionally has its plist and signature resource;
Windows has `PlugIn.ico` and `desktop.ini`. The macOS log shows SDK **ad-hoc
`codesign --sign -`**, not Developer ID or notarization qualification. This macOS
run qualifies ARM64 only, not x86_64 or a universal bundle.

The packaging step inventories the built bundle and its staged copy, requires
byte-identical inventory JSON, and writes a tar archive and its SHA-256 sidecar.
All six artifact uploads succeeded and their API digests match the logged upload
digests. The [primary report](../development/2026-11-15-product-continuation/reports/A52-vst3-hosted.json)
retains all artifact IDs, sizes and digests; bundle artifacts are
[Linux 14143048278](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43668397341/artifacts/14143048278),
[macOS 14143202991](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43668397341/artifacts/14143202991)
and [Windows 14143052163](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43668397341/artifacts/14143052163).
At inspection the artifacts were unexpired, with expiry on 29 November 2026.

A52 inspected **artifact metadata and the primary job output**, not downloaded
archive bytes. The successful packaging step writes the inner tar's hash but
does not print it, so no independently recomputed inner-archive hash is claimed.
The per-file module/payload hashes above are the executed install fixture's
observations. This evidence does not establish signed distribution or rights
clearance.

## Compatibility since A29

A52 compared the actual `ff41d412d03f2c5767aa4057b29fa8ec1627449b` source
reviewed by [A29](../PRODUCT_COMPATIBILITY.md) with published `d8c39f7` and the
current protected working files. All **20 VST3 files, 54 core/header files and
30 authoring-data files** are unchanged. The VST3 workflow, SDK acquisition,
bundle inventory, profile embedding, fixed-registration compiler and native
install rules also match. The receipt retains 28 selected source hashes.

The actual later non-documentary delta contains **15 paths**: standalone build
rules and test fixtures, standalone/crossover installation, capture admission,
characterization plotting and paint-benchmark tooling. Root CMake adds the
separate CrossoverTools install include. No VST3 mapping, state, DSP, factory or
plugin-test source changes occur in that delta. The newly registered native
calibration probe remains behind standalone build/test conditions; these VST3
jobs do not execute it.

Independent literal inspection matched all **47** compiled descriptors to the
schema-4 registry in order: IDs, paths, kinds, units, maxima, defaults and step
counts agree, and registry minima remain zero. Exact ID/path pairs and hashes
are retained in the compatibility receipt.

| Retained ID range | Meaning | Count |
| --- | --- | ---: |
| 4096–4104 / 4112–4120 | Upper A / B drawbars | 18 |
| 4128–4136 / 4144–4152 | Lower A / B drawbars | 18 |
| 8192 | Global expression | 1 |
| 8208–8209 | Remembered Upper/Lower A/B bank selection | 2 |
| 12288–12291 | Percussion controls | 4 |
| 16384–16385 | Pedal mixtures | 2 |
| 20480–20481 | Upper/Lower effective preset selection | 2 |

The unchanged common serializer writes **`B3CONTROLS4`** and reads **1–4**.
The current native ABI fixture actually exercises separate literal migration
oracles for versions 1–3, partial streams and exact version-4 output; its 1,600
fixed-registration/bank/route combinations retain pending and acknowledged state.
The version-4 catalog remains `atlas-chapel-nominal-v1`, authoring SHA-256
`c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf`.

The preset path remains the two existing parameter IDs into `SelectPreset`,
covering Cancel, nine documentary fixed rows and A/B per manual. Controller
restoration derives effective preset values from the common snapshot while
retaining remembered bank and fixed memory. The successful native automation
fixture covers preset boundaries, aliases, state restoration and partitioning;
this is **not a VST3 program-list implementation**.

Endpoint/inversion calibration and CC120/121 handling remain in native
`MidiInput`. They neither add parameter IDs nor enter the control-state grammar.
The VST3 controller exposes the common descriptors; its processor consumes native
note events and parameter queues through the unchanged HostTimeline and rejects
output-only Legacy MIDI CC events as input. The primary validator's absence of
MIDI Mapping/Learn agrees with that source boundary. Host automation of existing
expression ID 8192 remains available without importing the native calibration
policy.

## Retention and next gate

The retained whole-log hashes cover UTF-8 encoding of the connector-returned
decoded text, preserving its BOM and newline form. They do not identify an
unfetched redirect archive. The bounded excerpts preserve 227 selected original
lines in total, with their original line numbers and timestamps.

| Job log | Decoded UTF-8 bytes | SHA-256 |
| --- | ---: | --- |
| Linux | 290,780 | `8d798bb60bb99097e3679311257e2cc6bad4c4ae1c42f91fb683e15b622d90e3` |
| macOS | 295,562 | `8aec47353b3309a5a761b840553ec933eb91e2233fa53fccafc9df44cc687ff0` |
| Windows | 199,414 | `eeb426eb847ceac77d92a4bbed5ffe15e821521845bb9c813187d385451a501b` |

The integrator's later A46 record-checker/A48 plot-admission changes are outside
this published run. Qualify the final published source through its appropriate
hosted workflow and retain exact commit/tree, actual selected counts, original
failures and artifact identities. Do not carry the `d8c39f7` matrix forward as
execution of changed source.

The next product qualification is an identified host/version/platform journey:
discover and instantiate the bundle, operate its generic parameter controls,
automate expression and both preset selectors, save/reload an actual host
project, compare state/render continuity, and retain device/buffer observations
and failures. Hardware timing, native accessibility, physical/acoustic fidelity,
release signing and installers remain separate gates.
