# A28 — Native preset workflows and diagnostic migration

Actual worker `/root/w05_a28_native_workflows`, logical wave 5, 2026-11-14.
Repository: `/workspace/scratch/a472c29da8b3/Hammond-B3-Organ`.
Checkout context: `35554c068492fe2b20c1f8a602d8354ae762dc42`, tree
`6a6881eeee1943665694e988208b2d6710731919`. The tested implementation was an
uncommitted overlay; that commit alone does not identify its source.

## Implemented boundary

Read the standing instructions, complete M0–M9 plan, current status/next steps,
frozen selector/core/state/parameter contracts, adapter audit and retained hosted
baseline failures. Root owns shared status, actual accounting and publication.
No commit, push, child agent or preserved-baseline rebuild occurred.

Production changes are limited to `apps/standalone/main.cpp`,
`apps/standalone/benchmark.cpp` and the expressly authorized provenance correction
in `cmake/StandaloneBenchmark.cmake`:

- Native diagnostics become schema 3; the benchmark becomes
  `hammond-standalone-benchmark-v2` with workload version 1 unchanged.
- Every controls object adds raw `fixed_registrations` and checked, derived
  `preset_selections`. Remembered banks and route bits retain their meanings.
  An invalid copied snapshot emits `null` for a derived selection rather than
  falsely describing invalid data as Cancel.
- Replay diagnostics retain desired controls and the snapshot/running,
  pending-control and pending-save predicates before shutdown cleanup.
  Delivery/acknowledgment requirements and the two-second drain remain unchanged.
- Benchmark source identity now covers the fixed-data generator, strict chapel
  compiler/schema, authoring catalog and both admitted readings. Its existing
  independent manifest test requires those concrete inputs and actual hashes.

Seven affected native Python suites and the benchmark test were updated. Legacy
state1/2/3 inputs, archived reports and examples retain their bytes. Current Save
expectations use independent state4 literals/grammar. The chapel bank-copy
exporter remains state3 with a separate state4 native Save oracle. New actual
workflows cover all 24 preset keys, fixed/Cancel memory through live and cold Load
and audio restart, and MIDI B-bank edits during fixed/Cancel routing.
The current contract is [PRESET_NATIVE_WORKFLOWS.md](../../PRESET_NATIVE_WORKFLOWS.md),
with corresponding updates in [STANDALONE_APP.md](../../STANDALONE_APP.md) and
[STANDALONE_BENCHMARK.md](../../STANDALONE_BENCHMARK.md).

A25 independently owned the renderer repair and raster registration. A28's
accepted executable includes its final `InstrumentView.cpp`, SHA-256
`c4be416d5a0e715d26d0d582d6f4539224561e591220bbae165ea2b00a0246e7`.
A28 changed no geometry, renderer, UI model, Session or audio algorithm.

## Source and toolchain

The private copied source/build are `/tmp/hammond-preset-a28/source` and
`/tmp/hammond-preset-a28/build`. A preliminary build used A23's renderer; the
accepted gate used a synchronized copy with A25's final renderer and rebuilt
native executable. Neither preserved `build-baseline` nor `build-native` was
reconfigured or modified.

The eight-suite source manifest contains **1,260 files**, raw SHA-256
`6c4491586e4e0c48a8e88dbe92712077da9db50e25985a1b117dec3507443be8`.
Only two native test files changed for the correction gate. The
[final frozen manifest](reports/a28-source-final.json) SHA-256 is
`72874cd7ceeaada3da152297d265b501dc33517896b14d02883256508d48c6cd`.
A final comparison of all 1,260 frozen files against the live tree found only
four documentation/ledger differences: the standalone guide, two independently
owned VST3 guides and `assignments.json`. Every compiled source, data/configuration
input and accepted native test matched the live bytes.

Toolchain: GNU C++ **14.2.0**, CMake/CTest **4.4.4**, Python **3.12.14**, Unix
Makefiles, Linux x86_64, Release. SDL **2.32.10**, commit
`5d249570393f7a37e037abf22cd6012a4cc56a71`; RtMidi **6.0.0**, commit
`1e5b49925aa60065db52de44c366d446a902547b`, with the existing admitted CoreMIDI
initialization patch. Native MIDI backend: ALSA. Windowed cases explicitly use
SDL dummy audio/video. SDL's ALSA audio driver is disabled locally; the separate
RtMidi ALSA backend is enabled.

## Executed gate

Below, `cmake` and `ctest` denote the supplied binaries in
`/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin`.
Commands were launched from the repository or the copied source directory.

```sh
cmake -S /tmp/hammond-preset-a28/source -B /tmp/hammond-preset-a28/build \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_STANDALONE=ON \
  -DHAMMOND_SDL2_ROOT=/workspace/scratch/7ffc2842608b/SDL2 \
  -DHAMMOND_ENABLE_MIDI=ON \
  -DHAMMOND_RTMIDI_ROOT=/workspace/scratch/cd4bd06ce68f/rtmidi \
  -DSDL_ALSA=OFF \
  -DALSA_INCLUDE_DIR=/workspace/scratch/641ca55ce6de/native-sysroot/usr/include \
  -DALSA_LIBRARY=/workspace/scratch/641ca55ce6de/native-sysroot/usr/lib/x86_64-linux-gnu/libasound.so \
  -DHAMMOND_BUILD_VST3=OFF
cmake --build /tmp/hammond-preset-a28/build \
  --target hammond_standalone hammond_standalone_benchmark -j4
ctest --test-dir /tmp/hammond-preset-a28/build -N --no-tests=error \
  -R '^test_standalone_(app|benchmark|midi_cli|native_midi_replay|workflows|replay_boundaries|chapel|install)$'
ctest --test-dir /tmp/hammond-preset-a28/build --verbose \
  --output-on-failure --no-tests=error -j2 \
  -R '^test_standalone_(app|benchmark|midi_cli|native_midi_replay|workflows|replay_boundaries|chapel|install)$' \
  --output-junit /tmp/hammond-preset-a28/native-first.xml
```

Discovery found exactly eight required suites. Configure/build succeeded. The
first selected gate passed **6/8 in 82.95 seconds**, without skips. After the two
test-coordinate corrections below, only affected suites were rerun:

```sh
ctest --test-dir /tmp/hammond-preset-a28/build --verbose \
  --output-on-failure --no-tests=error -j2 \
  -R '^test_standalone_(app|replay_boundaries)$' \
  --output-junit /tmp/hammond-preset-a28/native-corrected.xml
```

The correction gate passed **2/2 in 9.04 seconds**, with no skips or production
changes. This qualifies the eight-suite set by a retained initial run and affected
recheck; it is not a claimed final single 8/8 execution.

| Accepted suite | Python methods | Accepted duration |
| --- | ---: | ---: |
| Benchmark | 9 | 3.18 s |
| Relocated native installation | 8 | 7.57 s |
| Native application | 18 | 9.03 s, corrected run |
| MIDI CLI/modal | 15 | 11.02 s |
| Native MIDI replay | 12 | 23.41 s |
| Native musical workflows | 13 | 64.36 s |
| Replay boundaries | 9 | 5.16 s, corrected run |
| Native chapel bank-copy/Save | 2 | 20.15 s |
| **Distinct accepted methods** | **86** | Concurrent durations are not additive wall time. |

Accepted application/CLI launch counters: 164 native application, 95 MIDI CLI,
17 MIDI replay, 52 musical workflows, 29 replay-boundary and 22 chapel-native.
These exclude installation child commands and benchmark invocations. Pre-SDL
rejections are CLI launches, not windowed musical performances. The new
minimum-size matrix checks all **24** preset commands with both original manual
owners still held, exact complete controls and no implicit file save.

## Original findings and repairs

1. A preliminary new Save test held physical S, then sent Ctrl+S and S-up. The
   application correctly released the original S note owner. The test now holds
   D instead, preserving release-before-modifier semantics. The corrected case
   passed its three actual live/cold/restart processes. The
   [original failure](reports/a28-preliminary-workflow-failure.txt) is retained.
2. Minimum-size smoke sampled old C4 x=391 after the permanent preset rail moved
   the playing keyboard. An actual fresh BMP at y=466 had old C4/D4/E4 samples
   all `cceaf9` in stored BGR; current points x=489/510/531 were `8ecbe4`,
   `cceaf9`, `cceaf9`. Production painted the held key correctly. Literal current
   interior points replaced the obsolete fixture; the assertion was preserved.
3. The tied-resize fixture clicked old Lower C2 `(36,560)`, now the real Lower
   Cancel key. Its route change was correct. The fixture now uses Lower C2
   `(198,560)` and default-size Upper C2 `(214,580)`, preserving source order,
   resize markers, the original Lower owner and exact note-on/off counts.
4. At baseline `35554c0`, hosted macOS missed an acknowledged observation in
   `[400,590)` ms while the full focus/resize/Help/MIDI replay completed with
   correct owners. Four completed, acknowledged prefixes now require the
   critical states at 380, 590, 990 and 1750 ms. Each preserves original action
   bytes/order, required owners and channel state; the full original timeline
   remains. This test-policy repair passed locally. It does not claim a display
   or callback latency bound.
5. The separate hosted macOS modal Escape timeout remains **unclassified**. A
   focused local ALSA test completed delivery/acknowledgment with two expected
   enumeration errors; it did not reproduce CoreMIDI. Runtime/modal assertions
   now retain copied JSON, and schema 3 exposes the actual pre-shutdown barrier
   predicates/desired controls. No timeout was enlarged. The next actual hosted
   result must be inspected before closing that gate.
6. Benchmark identity omitted the new generated fixed-data inputs. The concrete
   generator/catalog/schema/readings and independent manifest requirements were
   added; old workload and score arithmetic remain unchanged.

## Evidence and handoff

[Structured qualification](reports/a28-native-workflows.json) records source,
toolchain, dependencies, counts, hashes and limits. Retained evidence includes
[the initial log](reports/a28-native-first.txt),
[initial JUnit](reports/a28-native-first.xml),
[corrected log](reports/a28-native-corrected.txt), and
[corrected JUnit](reports/a28-native-corrected.xml). Raw CTest/JUnit whitespace
remains verbatim rather than normalized.

| Artifact | SHA-256 |
| --- | --- |
| Native executable | `557acb27d16cfc77815c278778335f8418b471b563d1b93a47bf3051eae68c82` |
| Benchmark executable | `30447605aa6f913699e8f51a6148243ca68a8115e4bf356807314a02dc24574d` |
| Compiled nominal profile | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| Benchmark manifest file | `ed6087529c26057f049a59271b42c2c31643f322559ee3651699798dd1b0ee11` |

The executable is `/tmp/hammond-preset-a28/build/apps/standalone/hammond_standalone`;
the benchmark is its sibling. A30 received those paths for bounded operation
checks. Owned source/doc whitespace and Python syntax checks passed.

After every implementation and evidence write above succeeded, the first attempt
to write this final note failed because the executor transport disconnected and
recovery timed out after 45 seconds. The workspace returned; the existing
structured record was verified present and this previously absent note was
written. No test or source gate was rerun because of that infrastructure event.

Main/benchmark schemas and current exact fixtures are ready for integrated source,
A34's gallery producer and the operating guide. The older gallery producer's
schema-2 migration belongs to that separately assigned owner. Root retains final
integration, actual macOS/Windows qualification, sanitizers, publication and real
sixty-worker accounting. The unresolved hosted modal timeout remains visible.
A later renderer refinement needs its own affected checks and source identity.
No physical device, DAW, deadline, measured organ, accessibility or 1:1 visual
qualification follows from these Linux dummy-driver results.
