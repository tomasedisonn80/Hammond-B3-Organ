# Assignment 15 — SDL2 audio device transport

- Identity: `/root/w03_a15_audio_device`, standalone wave 3; 2026-11-13.
- Owned: `apps/standalone/AudioDevice.h`, `AudioDevice.cpp`,
  `docs/STANDALONE_AUDIO.md` and this note. No core/build/commit changes.
- Source start: `2e917509b378d48c85cc1d52c3aa446eef9552c8` plus the live
  standalone work. Standing instructions, scope, Session contract, source reviews,
  current scanner/standalone tracks and actual checkout were inspected.
- Toolchain: Linux x86-64, GCC 14.2.0, C++20, pinned static SDL2 2.32.10.
  SDL source `5d249570393f7a37e037abf22cd6012a4cc56a71` passed the local
  dependency verifier; no network/dependency acquisition occurred.

## Implemented result

The [transport contract](../../STANDALONE_AUDIO.md) defines copied device names,
requested/obtained configuration, paused preparation, explicit application
registration, start-before-unpause and callback-quiescence-before-stop/close.
One existing Session supplies all DSP. Partial opens clean up, open objects
reject reopening, and the application retains SDL global subsystem ownership.
Callback guards admit exact native float32 stereo buffers; render failures
silence. Finite outliers clamp only to [-1,1], with counted clips and no gain.
Any nonfinite sample silences the whole callback. Lock-free, saturating counters
and copied off-callback device information expose the actual outcome.

## Executed checks

Commands used repository cwd `/workspace/scratch/5ba97739b54c/Hammond-B3-Organ`.
Both probes below are temporary independent harnesses, not maintained test targets.

```sh
python3 tools/acquire_sdl2.py --verify-existing ../SDL2
g++ -std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion \
  -Wshadow -Werror -Iinclude -Iapps/standalone -I../SDL2/include \
  -I../sdl2-build/include-config-release/SDL2 \
  -fsyntax-only apps/standalone/AudioDevice.cpp
SDL_AUDIODRIVER=dummy /tmp/hammond-audio-device-15/probe
SDL_AUDIODRIVER=dummy /tmp/hammond-audio-device-15/real_session \
  ../build-baseline/nominal.b3p
```

The real probe was compiled with the same warnings plus `-O2`, using copied
`AudioDevice.cpp/.h` and `Session.cpp/.h` under
`/tmp/hammond-audio-device-15/snapshot`, `-Iinclude`, both SDL include paths,
`real_session.cpp`, the libraries below and `-pthread -ldl -lm`.
The earlier `probe.cpp` supplies an explicit Session double and links only
AudioDevice plus the actual SDL library; it cannot establish core parity.

| Observed gate | Result |
| --- | --- |
| Strict compile and dependency identity | Passed; no warnings, verified SDL pin. |
| Real Session/core + SDL dummy | All 15 supported rate/buffer combinations passed; 30 callbacks, 23,808 frames, zero render/format/nonfinite failures. |
| Actual startup and stopped lifecycle | Queued controls/note applied after start; no paused callbacks; stop released holds, preserved controls/clock and prevented catch-up; restart/default/named/reopen passed. |
| Actual failed preparation | Invalid profile closed partial device, preserved stopped Session controls/clock, and subsequent open succeeded. |
| Actual failing callbacks | Timeline overflow and publication exhaustion produced expected transport render diagnostics. |
| Transport double with actual dummy SDL | All 15 combinations plus in-flight stop, close and destructor joined before Session stop; duplicate/uninitialized/invalid-config/unavailable-device rejection passed. |
| Paused callback fault injection with double | Six malformed pointer/length cases skipped Session; finite samples unchanged, counted clipping, whole-buffer nonfinite silence, failed/short-render silence and counter saturation passed. |

The real callback count is one observed schedule, not a deadline guarantee.
Core/header/profile sources had no changes relative to the baseline commit
`ba0d9c9`; the baseline core library was reused under that checked condition.
The Session implementation became available during this assignment, and the
real run used its copied source rather than waiting on or linking a partial build.
The first run used Session SHA-256
`a30b6b158fd0f048daa0da0b93204a572515340ebdc7e82cd031b4fbe2b7148f`.
After its producer CAS gained acquire/release ordering, the complete matrix was
rebuilt and rerun against the final hash below: the same 30 callbacks/23,808 frames
and all listed assertions passed again.

## Qualified input identities (SHA-256)

| Input | SHA-256 |
| --- | --- |
| `AudioDevice.cpp` | `3fda8dd26c643011e937c9ca3542a0da69eecca4716a01696412775543b44cef` |
| `AudioDevice.h` | `3820d6a294236af3b7486ed84870207c349d7aa114779c441b0807295937b3cd` |
| Copied `Session.cpp` | `247c6a63dc9bb6c4e60398b17779a2d985058563b8d981c5e06426eab977f6ae` |
| Copied `Session.h` | `0eed6c82d0cf5ffbeb0206f6f9702a93ef5a75cde6fd669b2862705dc7af84a0` |
| `../build-baseline/libhammond_core.a` | `6d6f6a92c4f5a826dacff1314b984c1b28cdcdf021751f8d8770eab780cc9dd8` |
| `../build-baseline/nominal.b3p` | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| `../sdl2-build/libSDL2.a` | `34c9ffb7b608a0a38294d97d06852b4f36f81a419fb5dc2e3b0bb0f92e690e85` |
| Temporary `probe.cpp` | `5e16e2dcda99d1e4514aed149f331b55e574b632098458758e88dc0540ee5684` |
| Temporary `real_session.cpp` | `41106ebb90a9254d310849b34594098874f69707feb82091d98e82ff3a5cfd97` |

## Next acceptance and limits

The main application can now use the published API and display actual diagnostics.
Root owns optional-target integration and the coherent final source checkpoint.
Retain maintained independent transport tests, obtained-spec corruption cases,
calibrated callback allocation/race evidence and actual application startup.
Actual hardware, hotplug, timing/underruns, other OS backends and acoustic output
remain unqualified. Source inspection finds no callback allocation/lock/I/O;
that is not an executed allocation or race-detector result. The nominal dry core
and all parameter/state/plugin identities are unchanged. No physical fidelity,
publication or complete M9 claim is made by these tests.
