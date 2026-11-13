# Assignment 19 — independent actual SDL device acceptance

- Identity: `/root/w04_a19_device_acceptance`, wave 4; 2026-11-13.
- Owned: `apps/standalone/native_tests/test_standalone_audio_device.cpp`,
  `docs/STANDALONE_AUDIO_ACCEPTANCE.md` and this note; no core/audio/CMake edits
  or commit. Root owns optional target wiring and shared status/publication.
- Starting HEAD: `96a37a977ef22b7adf38e1a841f57ffcf32519a7`, tree
  `ab85e45d6776229c00fa394a540d72803daf8281`, plus uncommitted standalone sources.
  Inspected AGENTS, current tracks/manifests, scope, contracts and note 15.
- Tools: Linux x86-64, GCC 14.2.0, C++20; actual static SDL2 2.32.10 source
  `5d249570393f7a37e037abf22cd6012a4cc56a71`. Dependency verification passed;
  no network acquisition. Runtime skill was read; status tool was unavailable.

## Implemented and observed

The [acceptance contract](../../STANDALONE_AUDIO_ACCEPTANCE.md) describes the
maintained public-API test. It links actual AudioDevice, Session and the existing
core with actual dummy SDL; there are no doubles or private callback injection.
All 15 rate/buffer combinations passed exact obtained float32 stereo admission,
paused preparation, real controls/manual/pedal application, positive finite peak,
live control/release, clock accounting, stopped quiescence and silent restart.
Enumeration, default/named opens, duplicate refusal, invalid configuration/profile
cleanup, counter retention and eight dedicated destruction cycles passed.
Actual timeline/publication exhaustion produced the expected render-failure
diagnostics; publication-exhausted start remained paused.

| Executed gate | Actual result |
| --- | --- |
| Strict independent optimized build | Passed with all project warning flags and `-Werror`. |
| Actual dummy execution | 15 combinations; 75 matrix callbacks; 59,520 frames / 119,040 counter-derived stereo samples; 31 rejected opens; two expected render faults; eight lifetime cycles; 2.878 s. |
| Unexpected matrix faults | Zero render, format, overrange and nonfinite failures. |
| Adapter ASan/UBSan | Same assertions/counts passed in 2.952 s, with uninstrumented unchanged core/SDL libraries. |
| LeakSanitizer | Blocked: runtime reported it cannot work under ptrace; not a leak pass. |

The first fixture run timed out because its note-off incorrectly carried velocity
100; the established host-note contract requires zero. Corrected the fixture and
reran the full suite. No production defect was found. `/usr/bin/time` was absent;
the recorded timing uses Bash's `time` keyword. These were harness/setup failures.

## Commands and coherent source basis

Repository cwd: `/workspace/scratch/5ba97739b54c/Hammond-B3-Organ`.
Copied the four production adapter files and this test source into
`/tmp/hammond-audio-device-19/snapshot` before compilation. Core/public headers
and nominal profile authoring had no diff against baseline `ba0d9c9`; only under
that checked condition was `../build-baseline/libhammond_core.a` reused.

```sh
python3 tools/acquire_sdl2.py --verify-existing ../SDL2
git diff --exit-code ba0d9c9 -- include src data/profiles/nominal-unmeasured-v1.json
g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion \
  -Wshadow -Werror -DSDL_MAIN_HANDLED \
  '-DHAMMOND_TEST_PROFILE="/workspace/scratch/5ba97739b54c/build-baseline/nominal.b3p"' \
  '-DHAMMOND_SOURCE_DIR="/workspace/scratch/5ba97739b54c/Hammond-B3-Organ"' \
  -Iinclude -Itests -I/tmp/hammond-audio-device-19/snapshot -I../SDL2/include \
  -I../sdl2-build/include-config-release/SDL2 \
  /tmp/hammond-audio-device-19/snapshot/test_standalone_audio_device.cpp \
  /tmp/hammond-audio-device-19/snapshot/AudioDevice.cpp \
  /tmp/hammond-audio-device-19/snapshot/Session.cpp \
  ../build-baseline/libhammond_core.a ../sdl2-build/libSDL2.a \
  -pthread -ldl -lm -o /tmp/hammond-audio-device-19/acceptance
time SDL_AUDIODRIVER=dummy /tmp/hammond-audio-device-19/acceptance
```

The sanitizer build replaced `-O2` with
`-O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer` and used output
`acceptance-sanitized`. It initially failed at LeakSanitizer teardown with
`ASAN_OPTIONS=detect_leaks=1:halt_on_error=1`; the successful rerun used
`SDL_AUDIODRIVER=dummy ASAN_OPTIONS=detect_leaks=0:halt_on_error=1
UBSAN_OPTIONS=halt_on_error=1` with that identical binary.

## Qualified SHA-256 inputs

| Input | SHA-256 |
| --- | --- |
| Test source | `a4614869017d16bf48439a8e4df9291a858b8a61a3813e41982a8c71855e6a6e` |
| `AudioDevice.cpp` | `3fda8dd26c643011e937c9ca3542a0da69eecca4716a01696412775543b44cef` |
| `AudioDevice.h` | `3820d6a294236af3b7486ed84870207c349d7aa114779c441b0807295937b3cd` |
| `Session.cpp` | `247c6a63dc9bb6c4e60398b17779a2d985058563b8d981c5e06426eab977f6ae` |
| `Session.h` | `0eed6c82d0cf5ffbeb0206f6f9702a93ef5a75cde6fd669b2862705dc7af84a0` |
| Baseline core library | `6d6f6a92c4f5a826dacff1314b984c1b28cdcdf021751f8d8770eab780cc9dd8` |
| Nominal compiled profile | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| SDL static library | `34c9ffb7b608a0a38294d97d06852b4f36f81a419fb5dc2e3b0bb0f92e690e85` |
| Optimized test binary | `e7d73c729ab076c178a84706b7d898cce62259c7b0e002e38b168881c52db9db` |

## Handoff and unrun gates

Root added the optional target with the requested profile/source definitions,
`SDL_MAIN_HANDLED`, explicit dummy environment and 15-second CTest timeout.
Its coherent integrated CMake/CTest run belongs to root; this assignment executed
the independent direct build above. Keep the native target outside SDK-free tests.
Captured final output/silence bytes, obtained-spec corruption, allocator/race
instrumentation, hardware/other-platform output, hotplug, deadlines and fidelity
remain unrun here. Leak detection needs a compatible runner. No audible playback,
complete M9, native hardware, publication or physical-match claim is made.
