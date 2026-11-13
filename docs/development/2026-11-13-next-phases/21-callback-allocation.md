# Assignment 21 — calibrated actual SDL callback allocation probe

- Actual identity: `/root/w04_a21_callback_allocation`, wave 4, 2026-11-13.
- Owned: `apps/standalone/native_tests/test_standalone_callback_allocation.cpp`,
  `docs/STANDALONE_CALLBACK_ALLOCATION.md` and this note. No production/CMake/core
  edits or commits; root owns target wiring, shared status and publication.
- Starting HEAD/remote main: `96a37a977ef22b7adf38e1a841f57ffcf32519a7`, plus
  uncommitted standalone implementations. Read AGENTS, current tracks/status,
  scope, Session/AudioDevice contracts/runtime, atlas product/closure reviews
  and the calibrated replacement patterns in `tests/test_realtime.cpp`.
- Toolchain: Linux x86-64, GCC 14.2.0, C++20, `-O3 -DNDEBUG` and all project
  strict warnings with `-Werror`. CMake available: 4.4.4. Actual SDL2 2.32.10
  checkout `5d249570393f7a37e037abf22cd6012a4cc56a71`; existing-lock verification passed.

## Implemented boundary and executed result

Only a separate test AudioDevice translation unit aliases SDL_OpenAudioDevice to
an extern-C SDLCALL shim. The shim wraps its original callback/userdata and calls
real SDL_OpenAudioDevice. Real SDL threads/buffers, Session, ownership and Engine
execute; production callback source is unchanged. The shipped application has
no shim. This is explicitly a test-instrumented recompilation.
Thread-local global C++ new/delete counts surround only each original callback.
All scalar/array/aligned/nothrow/sized forms receive separate 12-allocation,
12-free calibration before and after every callback on that same actual thread.
Volatile function-pointer calls prevent allocation elision. Fixed arrays/atomic
aggregates, cold-first-call and callback-thread identity checks reject vacuity.

| Executed check | Observed result |
| --- | --- |
| Strict optimized independent build | Passed with zero diagnostics. |
| 128/2048 frames, 48 kHz | Eight workloads each: initial musical/percussion state, 256 commands, note-off, scoped release, Panic, rearm, pending-release overflow and authoritative rejection. |
| Actual render failures | Three timeline-overflow callbacks; two active successes then two publication-exhaustion callbacks; all rejected output exactly silent. |
| Callback probe | 18 observations; 39 real callbacks; 78 positive calibrations; 936 calibration allocations and 936 frees; original callback new/delete counts both zero. |
| Main-thread API probe | 1,070 posts and 753 snapshot reads, including empty/exhausted paths; zero new/delete calls; independently calibrated before/after. |
| Execution | Exit 0, Bash `time` wall 1.003 s; no production defect found. |

`/usr/bin/time` was absent: that initial command exited 127 before running the
test. Replaced only the timer invocation with Bash `time`; this was a setup
failure. No sanitizer, race, physical-device or other-platform run is claimed.

## Executed commands and inputs

Cwd `/workspace/scratch/5ba97739b54c/Hammond-B3-Organ`; build outputs only in
`../build-callback-allocation`. Production adapter hashes below matched before
and after compilation. Core/public headers and nominal authoring had no diff
against `ba0d9c9`, qualifying reuse of the named baseline core/profile artifacts.

```sh
git diff --exit-code ba0d9c9 -- include src data/profiles/nominal-unmeasured-v1.json
python3 tools/acquire_sdl2.py --verify-existing ../SDL2
mkdir -p ../build-callback-allocation
flags=(-std=c++20 -O3 -DNDEBUG -Wall -Wextra -Wpedantic -Wconversion
  -Wsign-conversion -Wshadow -Werror -DSDL_MAIN_HANDLED -Iinclude
  -Iapps/standalone -Itests -I../SDL2/include -I../sdl2-build/include-config-release/SDL2)
c++ "${flags[@]}" -c apps/standalone/AudioDevice.cpp \
  -DSDL_OpenAudioDevice=hammond_probe_open_audio_device -o ../build-callback-allocation/AudioDevice_probe.o
c++ "${flags[@]}" -c apps/standalone/Session.cpp -o ../build-callback-allocation/Session.o
c++ "${flags[@]}" '-DHAMMOND_TEST_PROFILE="/workspace/scratch/5ba97739b54c/build-baseline/nominal.b3p"' \
  '-DHAMMOND_SOURCE_DIR="/workspace/scratch/5ba97739b54c/Hammond-B3-Organ"' \
  -c apps/standalone/native_tests/test_standalone_callback_allocation.cpp -o ../build-callback-allocation/test.o
c++ -O3 -DNDEBUG ../build-callback-allocation/test.o ../build-callback-allocation/AudioDevice_probe.o \
  ../build-callback-allocation/Session.o ../build-baseline/libhammond_core.a ../sdl2-build/libSDL2.a \
  -lm -pthread -o ../build-callback-allocation/test_standalone_callback_allocation
time env SDL_AUDIODRIVER=dummy ../build-callback-allocation/test_standalone_callback_allocation
git diff --check
```

| SHA-256 input | Value |
| --- | --- |
| Test source | `a48f6ff4c8590d3eb8b31870d03f0ca23a3d5ca3276273c15b5873bedd5ec3c4` |
| AudioDevice.cpp | `3fda8dd26c643011e937c9ca3542a0da69eecca4716a01696412775543b44cef` |
| AudioDevice.h | `3820d6a294236af3b7486ed84870207c349d7aa114779c441b0807295937b3cd` |
| Session.cpp | `247c6a63dc9bb6c4e60398b17779a2d985058563b8d981c5e06426eab977f6ae` |
| Session.h | `0eed6c82d0cf5ffbeb0206f6f9702a93ef5a75cde6fd669b2862705dc7af84a0` |
| Baseline core library | `6d6f6a92c4f5a826dacff1314b984c1b28cdcdf021751f8d8770eab780cc9dd8` |
| Nominal compiled profile | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| SDL static library | `34c9ffb7b608a0a38294d97d06852b4f36f81a419fb5dc2e3b0bb0f92e690e85` |
| Optimized test binary | `25d570152569c9b51724a986d3d57ba5882fcee2ce613ce82d0a37cc017fafef` |

## Handoff and limits

Root has the exact shim signature and requested optional target wiring; keep the
alias private to its probe AudioDevice object, never the ordinary app/test TU.
Use explicit dummy environment and 15-second timeout; build before filtered
CTest with `--no-tests=error`. Integrated CMake qualification belongs to root.
The [contract](../../STANDALONE_CALLBACK_ALLOCATION.md) names workload assertions
and measured scopes. No C/system/custom allocation, locks, deadline, race,
hardware/other-platform, full-rate-matrix, audible or physical-fidelity pass
follows. Main-thread setup/lifecycle and calibration deliberately remain outside
the observed production regions. No full M9 or uninstrumented-binary claim.
