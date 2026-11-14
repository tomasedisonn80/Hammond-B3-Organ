# A12 — native integration baseline

**Result:** all **32/32** selected CTests passed in **49.68 seconds** on
2026-11-14, finishing at 07:49:10 UTC. This comprises eight VST3/native tests
and twenty-four standalone tests. The SDK validator separately reported
**47 passed, zero failed**. Both required aggregate input targets built
successfully before acceptance. The first discovery found the validator absent;
building `hammond_vst3_test_inputs` supplied it before the retained final inventory.

## Tested identity and environment

Production source matched commit `b79086f6bb0c42b97130c721c5c73c7c97a13887`,
base tree `b0210756bf704017d9e56ebca97f935cc9c451c9`, immediately before and
after execution. New session documentation and the unused test oracle were a
separate worktree overlay; the base tree is not asserted to identify that overlay.
This assignment changed no production source or shared status document.

The existing combined build was `/workspace/scratch/a472c29da8b3/build-native`:
Linux x86_64, GCC 14.2.0, CMake/CTest 4.4.4, Unix Makefiles, Release, sanitizers
off, standalone/VST3/MIDI enabled. CTest was the sibling of the configured CMake.

| Dependency | Actual clean source commit |
| --- | --- |
| SDL 2.32.10 | `5d249570393f7a37e037abf22cd6012a4cc56a71` |
| RtMidi 6.0.0 | `1e5b49925aa60065db52de44c366d446a902547b` |
| VST3 SDK | `3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96` |

[Exact identities](reports/native-baseline-identities.txt) retain dependency
paths, trees, SDK submodules, tool versions, cache settings and executable hashes.
[Runtime configuration](reports/native-baseline-runtime-config.txt) retains the
actual SDL configuration and prepared RtMidi source/patch hashes. Native MIDI
compiled against the supplied ALSA 1.2.14 development sysroot. SDL used the
existing explicit `SDL_ALSA=OFF` local configuration; its compiled audio drivers
were dummy/disk/OSS and video drivers dummy/offscreen.

## Commands and retained evidence

Run from `/workspace/scratch/a472c29da8b3/Hammond-B3-Organ`:

```sh
/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/cmake \
  --build /workspace/scratch/a472c29da8b3/build-native \
  --target hammond_vst3_test_inputs hammond_standalone_test_inputs --parallel 4
/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/a472c29da8b3/build-native -C Release \
  --no-tests=error -R '^(test_native_|hammond_vst3_|test_standalone_)' -N
/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/a472c29da8b3/build-native -C Release \
  --no-tests=error -R '^(test_native_|hammond_vst3_|test_standalone_)' \
  --parallel 4 --verbose --output-on-failure
```

The [build log](reports/native-baseline-build.txt),
[32-test inventory](reports/native-baseline-inventory.txt) and
[complete verbose execution](reports/native-baseline-tests.txt) retain commands,
timestamps, outputs and zero exit codes. Coverage includes native ABI,
controller/state, behavior, automation, concurrency, allocation interposition,
both installations, standalone publication/UI/device lifecycle, MIDI synthetic
replay, callback allocation and retained musical workflows. The enabled
standalone relocation check admitted its exact seventeen-file payload.

These are local engineering results using synthetic MIDI and SDL dummy devices.
They do not qualify physical controllers/audio/display, DAW operation, deadlines,
other platforms, accessibility or instrument fidelity. The existing state-file
test explicitly leaves POSIX replacement failure after a completed temporary
write untested. The broad SDK-free suite was not rerun by A12; its independently
retained integrator baseline remains separate. The integrator was notified as
soon as runtime checks completed so production wave 3 could begin. Rebuild both
input targets and repeat the affected gates after that implementation; this
baseline does not qualify later source changes.
