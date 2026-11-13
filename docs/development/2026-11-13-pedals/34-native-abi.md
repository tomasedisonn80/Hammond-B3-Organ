# Assignment 34 — actual native VST3 ABI gate

**Agent:** `/root/w06_a34_native_abi`

**Wave:** 6 of the current 60-assignment session

**Date:** 2026-11-13 UTC

**Outcome:** completed; final actual-module ABI test passed. SDK validator exited
zero with its reported 47/0 result and retained diagnostics described below.

## Owned scope

- `plugins/vst3/tests/NativeHarness.h`
- `plugins/vst3/tests/NativeHarness.cpp`
- `plugins/vst3/tests/test_native_abi.cpp`
- `docs/VST3_ABI_ACCEPTANCE.md`
- This assignment record

No production source, CMake, shared status, manifest, SDK source or other
worker's file was changed. No commit, push or child-agent dispatch was performed.
Root owns integration and publication. The spawn UI reported aborted, but the
worker was active; root was promptly notified to retain one actual assignment
and avoid a duplicate dispatch.

Read the standing instructions, current README/status/next steps, historical
handoff, plan, atlas review and development-log tail. Read the native spike and
processor contracts and both host-independent timeline/state contracts. Directly
read atlas text pp. 385–396; these describe the separate headless core/wrapper,
stable IDs, clock ownership, active state access and independent acceptance
reports. Inspected the actual locked SDK module loader, host interfaces and the
validator source paths relevant to its diagnostics.

## Implementation and review decisions

The maintained helper loads the actual bundle with `VST3::Hosting::Module` and
creates/queries native interfaces through its exported factory. It does not
include the production processor header. Expected FUIDs are separate literal
words from the approved contract. Fixtures provide borrowed event lists,
parameter queues, bounded count/accessor controls, partial stream transfers,
preallocated audio buffers and native instance lifecycle ownership.

Module and host lifetimes outlast initialized native instances. The helper
stops/terminates and releases controller/audio/component interfaces before module
unload; partial construction also cleans up in that order. Callback getters
only copy prepared test data. Fixture creation, mutation and serialization stay
off any future callback probe.

The ABI suite checks factory identities/classes, the full 45-control export,
2,002 conversion cases, three event buses/all 16 channels, partial streams,
explicit state 1/2/3 migration, route bits, pending/acknowledged saves and four-slot
queue saturation. Six explicit lifecycle sequences include rejected float64
setup followed by supported processing, stop/deactivation, termination and
same-instance reinitialization.

Three-rate audio uses a separately prepared plain Engine with hand-authored
physical events. Expected events do not use the production native adapter,
HostTimeline or note-owner translators. Registrations explicitly select A,
differentiate Upper/Lower harmonics and include both nominal pedal mixtures.
Each isolated division must produce nonzero audio; a disconnected interval is
followed by an audible pedal history probe. Samples, channel equality, output
tails and actual-sample silence flags are checked through native interfaces.

## Coherent source and exact commands

Assignment 33 handed off scratch `a33-native-source` and `a33-native-build`
after its own frozen module/build gate. The source base is tree
`06786b70f1cffcc6371600fd6e14306f16e8c985`, not a mixture of live headers and an
older library. Its runtime bytes match published `88c36b4a72a07f6498f73279f25023278accd350`.
The existing `a33-native-overlay.json` was preserved; SHA-256
`7d3e645a31698a42fb699f0a834f8a3cbadbea58c0e483c4bfb3112c313b50d6`.
Every overlay entry and all three owned C++ files were compared byte-for-byte
with their frozen/live counterparts before recording results.

Important production overlay identities:

| File | SHA-256 |
| --- | --- |
| `Processor.h` | `e85cdc6f7aaf70c05eda61630a5e3acee7c7f2fef2796a2c5f557ce034a54e72` |
| `Processor.cpp` | `a61e567798e7435c9d73ddab9bf925b6995396954e772c13f31571ad0a96f20b` |
| `Controller.cpp` | `24b71a4a49d6234def8f9336e22de927577bf75bb859769b9af4a7ff840d41d6` |
| `StateStream.cpp` | `c83fbf22ea26c0b7a89974d4c0aa590c1e46f44f4a6c457d6fee512740d02117` |
| `Factory.cpp` | `880d4d24d4d6fbf104e441400ebf571a77c15019ae5bc43571a4524c242250d1` |
| `PluginIds.h` | `2bc93839216f52d5920046931d83ba14fd2d01e15fdbdd477b71b15ebb8415fc` |

Commands ran from `/workspace/scratch/f364bc93d920/Hammond-B3-Organ`:

```sh
c++ -std=c++20 -DNDEBUG -DRELEASE=1 \
  -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror \
  -I include -isystem /workspace/scratch/f364bc93d920/vst3sdk -fsyntax-only \
  plugins/vst3/tests/NativeHarness.cpp plugins/vst3/tests/test_native_abi.cpp

/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake \
  -S /workspace/scratch/f364bc93d920/a33-native-source \
  -B /workspace/scratch/f364bc93d920/a33-native-build
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake \
  --build /workspace/scratch/f364bc93d920/a33-native-build \
  --target test_native_abi -j 4
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/f364bc93d920/a33-native-build \
  -R '^(test_native_abi|hammond_vst3_validator)$' -V \
  --output-log /workspace/scratch/f364bc93d920/a34-native-gate-first.log \
  --output-junit /workspace/scratch/f364bc93d920/a34-native-gate-first.xml
```

The configure step reverified the exact SDK root, four submodules, five primary
licenses and embedded JSON source without network access. The cached Release
build uses GCC 14.2.0, CMake 3.31.6, Python 3.12.14 and Linux x86-64. JACK was
not found and is not required for these headless targets.

The strengthened final test was copied into the same frozen source and rebuilt
with the same target command. The final focused command was:

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/f364bc93d920/a33-native-build \
  -R '^test_native_abi$' -V \
  --output-log /workspace/scratch/f364bc93d920/a34-native-abi-final.log \
  --output-junit /workspace/scratch/f364bc93d920/a34-native-abi-final.xml
```

## Development failures and strengthened fixture

The first strict helper compile rejected four `iid` parameter names because
they shadowed SDK interface static members. Renamed only those formal parameters
to `requested_id`; the public signatures/layout were unchanged. The first ABI
syntax check needed an explicit `ivstunits.h` include for `kRootUnitId`.
The later isolated-voice fixture initially cast an event index to `uint16_t`,
while the existing Engine event field is `uint8_t`; the compiler caught the
narrowing and the fixture used the correct type. No production repair followed
any of these test-source compile failures.

The first actual linked run passed 2/2 selected suites in 2.24 seconds:
the ABI test in 0.77 seconds and validator in 1.47 seconds. Its ABI summary was
627,312 assertions and 208,221 compared frames. Self-review then found that the
fixture edited A-bank bars while retaining the default B-bank selection. Pedal
audio was exercised, but manual sound could remain muted. Before claiming
acceptance, the fixture explicitly selected A, differentiated upper/lower
registrations, and added required isolated audible Upper/Lower/Pedal probes.
The passing first run is not substituted for the stronger final evidence.

## Final result

Final ABI CTest: **1/1 passed, zero failures, 0.89 seconds**.

```json
{"suite":"native-abi-v1","instances":9,"assertions":691878,"descriptors":45,"conversions":2002,"accepted_callbacks":73,"rejected_calls":86,"state_round_trips":7,"lifecycle_sequences":6,"compared_frames":229725,"audible_frames":217972,"maximum_audio_error":0,"float_hash":"af029009868faa04"}
```

The module binary remained unchanged between the first validator execution and
the strengthened ABI test. Its SHA-256 is
`d87353b237e52c8d1f91af27933493a4cf78ba4a06af4a96c9930c0ecec1d3ff`
(434,168 bytes). The validator SHA-256 is
`bea796a46605330c6952b492c48ddea4c0d6ab892b255ca6c36378dddc3532f9`
(935,200 bytes). The matching compiled profile is 4,545 bytes, SHA-256
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.
The full artifact table is in [VST3_ABI_ACCEPTANCE.md](../../VST3_ABI_ACCEPTANCE.md).

| Retained scratch log | Bytes | SHA-256 |
| --- | ---: | --- |
| `a34-native-gate-first.log` | 20,205 | `991e29c0e3ed4e29db62956dada38fc78119143ebd54c66cbb3d3e914a2d83df` |
| `a34-native-gate-first.xml` | 1,922 | `f3ba94e2b3f139136f3a036fe53e7601e26efeb5cf220524d73528f42e2702ed` |
| `a34-native-abi-final.log` | 1,827 | `6bbbbfcff21903b0ff0931a8fcbee805a1cfffe13f74f24ef30949a4e43ab0dc` |
| `a34-native-abi-final.xml` | 643 | `32ff2f1dff83b37b9e445287bdf83df3a7a249b53325d0034b3f00bf2fcd9ecb` |

## SDK validator caveat retained

The actual bundle validator exited zero and summarized 47 passed, zero failed.
Counting its preserved log found 16 `Failed to teardown test!` lines and nine
`ERROR` lines for positive unsupported rates. The report links exact locked SDK
sources and lists the rates. `RepeatIdenticalStateTransitionTest` requires an
already inactive transition to fail, while `ProcessTest::teardown` unconditionally
requires that transition to succeed; the valid-transition test ends inactive,
and unsupported double-precision paths never activate. The rate test logs
unsupported setup without marking that branch failed. This is not a clean-log,
float64 or arbitrary-rate qualification. No SDK/plugin change hides it.

The maintained ABI gate independently proves the balanced supported lifecycle,
including cleanup/recovery after rejected unsupported setup, and explicitly
uses 44.1/48/96 kHz float32. Root and assignment 36 were told to retain both the
summary and diagnostic limits in hosted reporting.

## Frozen code and handoff

| Owned code | SHA-256 |
| --- | --- |
| `NativeHarness.h` | `0067515c5259288f1f711e4ce8c0921721682209863ca62ccbee4f50dbb2752a` |
| `NativeHarness.cpp` | `899d504d842e2e1b83d7f629e0bb4335b0c4f4191d7568df90980f27c09828b7` |
| `test_native_abi.cpp` | `afb51186f71622972953926e56d62d77efb56b0d2c603c0d429689520421245b` |

Assignment 35 received the frozen helper API and then the scratch source/build
handoff to add only its own behavior test. The handoff preserves source/module
identities and all existing named logs. No other worker edits the shared helper.

Next: integrate the behavior oracle, actual native callback allocation scope,
active state concurrency and platform CI; root then qualifies one complete
source tree, updates shared status and commits/pushes with remote verification.
No DAW, physical audio device, deadline, custom UI, signing or measured Hammond/
Leslie fidelity was exercised. Follow the standing repository workflow and keep
new module/test changes separate from this historical observation.


Final owned-file hygiene passed for all five deliverables: UTF-8, LF, final
newline, no trailing whitespace, per-file Git whitespace checks, valid local
Markdown links and the canonical assignment identity. The three code files
match the tested frozen snapshot; only these result documents were added after
that gate.
