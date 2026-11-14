# A31 — First complete combined integration gate

Actual worker `/root/w06_a31_integrated_gate`, logical wave 6, 2026-11-14.
Read the standing instructions, complete M0–M9 plan and source-review context,
current status/next steps, frozen preset contracts and accepted implementation/
review notes. A28 confirmed stable main/benchmark/native fixtures before copying.
A31 owns this note, the [integration review](../../reviews/PRESET_FIRST_INTEGRATED_GATE.md),
`reports/a31-*`, and two additional corrections expressly authorized by root:
`tests/test_realtime_console.cpp` and one link in `docs/STANDALONE_APP.md`.
No production algorithm, registry, source catalog, SDK or UI geometry was edited.
No commit, push, child agent or shared status/accounting edit occurred.

## Frozen source and exact commands

Working repository: `/workspace/scratch/a472c29da8b3/Hammond-B3-Organ`.
Private copied source: `/tmp/hammond-preset-a31/source`.
Fresh combined build: `/tmp/hammond-preset-a31/build`.

The copy enumerated `git ls-files --cached --others --exclude-standard -z`, copied
present regular-file bytes/modes, recorded every path/hash/size and compared all
1,287 copied files back to live source before configuring. Its original manifest
is [retained](reports/a31-source-first.json), SHA-256
`1f805c9257e2843c8ac1345938ff28603e2780e93831f0e2c02c907cc420ac8b`.
HEAD context was `35554c068492fe2b20c1f8a602d8354ae762dc42`; the uncommitted overlay
is identified by the manifest, not that baseline commit.

The following were executed. `cmake` and sibling `ctest` were the supplied
4.4.4 binaries in `/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin`.
Use a fresh source/build copy for a future run; preserve these evidence paths.

```sh
cmake -S /tmp/hammond-preset-a31/source -B /tmp/hammond-preset-a31/build \
  -G 'Unix Makefiles' -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_STANDALONE=ON \
  -DHAMMOND_SDL2_ROOT=/workspace/scratch/7ffc2842608b/SDL2 \
  -DHAMMOND_ENABLE_MIDI=ON \
  -DHAMMOND_RTMIDI_ROOT=/workspace/scratch/cd4bd06ce68f/rtmidi \
  -DSDL_ALSA=OFF \
  -DALSA_INCLUDE_DIR=/workspace/scratch/641ca55ce6de/native-sysroot/usr/include \
  -DALSA_LIBRARY=/workspace/scratch/641ca55ce6de/native-sysroot/usr/lib/x86_64-linux-gnu/libasound.so \
  -DHAMMOND_BUILD_VST3=ON \
  -DHAMMOND_VST3_SDK_ROOT=/workspace/scratch/1742da7072be/vst3sdk
ctest --test-dir /tmp/hammond-preset-a31/build -C Release \
  --show-only=json-v1 --no-tests=error
cmake --build /tmp/hammond-preset-a31/build --parallel 4 \
  --target all hammond_standalone_test_inputs hammond_vst3_test_inputs
ctest --test-dir /tmp/hammond-preset-a31/build -C Release \
  --verbose --output-on-failure --no-tests=error --parallel 1 \
  --output-junit /tmp/hammond-preset-a31/ctest-first.xml
```

Configure/build passed in 20.44 / 118.13 seconds. Discovery found 143 suites.
The original complete gate passed **141/143 in 385.91 seconds**. Its two failures
and reviewed fixes are explained in the integration review and exact retained
[realtime patch](reports/a31-realtime-correction.patch) /
[guide-link patch](reports/a31-guide-link-correction.patch).
After completion, only those two files were synchronized into the copied source.
The [corrected manifest](reports/a31-source-corrected.json) SHA-256 is
`db1001d3ab1b506c205aed06a347d2279d6aea0afa6f72b59949cf13e57eb8e5`.

```sh
cmake --build /tmp/hammond-preset-a31/build --parallel 4 \
  --target test_realtime_console
ctest --test-dir /tmp/hammond-preset-a31/build -C Release \
  --verbose --output-on-failure --no-tests=error --parallel 1 \
  -R '^(test_realtime_console|test_standalone_install)$' \
  --output-junit /tmp/hammond-preset-a31/ctest-corrected.xml
```

Only the realtime test compiled, in 4.70 seconds. The affected gate passed
**2/2 in 7.63 seconds**. The original full failure remains visible; there was no
unchanged retry or claimed final single 143/143 run. No CTest suite was skipped;
two audio-admission Python methods retained native capability skips.

## Handoff and evidence limits

The [machine record](reports/a31-integrated-gate.json) retains all commands,
exact pinned dependency commits, artifact hashes, suite results, source deltas
and hashes of the twelve retained raw/manifest/patch files. CTest and JUnit
whitespace is preserved verbatim. No raw log is normalized to hide diagnostics.
The SDK's 51 build selftests, 47 validator checks and 47 exported parameters are
separate counts. Sixteen validator teardown messages remain recorded and have
A29's baseline/SDK explanation.

A33 received the current built renderer and original source manifest for its
independent old-PCM comparison. A34 received the actual standalone executable,
original manifest and explicit notice that the two corrections do not affect
compiled standalone inputs. A36 may inspect/stage this qualified 17-file
MIDI-on component, but later runbook/payload changes require their own check.
Keep `/tmp/hammond-preset-a31` and the original baseline/native builds intact.

A32's later generator repair has separate admission tests and produces exactly
the same 2,099-byte fixed-data header. Later live source, capture producer, README,
CI and installation changes are not silently included in this frozen run.
A transient final-summary tool disconnect occurred after completed gates;
subsequent access succeeded and no test was repeated because of it.

Root retains final publication, platform/sanitizer qualification and sixty-worker
accounting. The hosted macOS modal timeout is still unclassified. This Linux
Release/dummy-driver gate does not establish physical-device timing, a DAW run,
semantic accessibility, literal reference equality, numerical scanner G5 closure
or measured organ/cabinet fidelity. No further broad rerun is needed for this
assignment; preserve the original result and the two affected corrections.
