# Standalone audio-device acceptance

The maintained independent test is
[`test_standalone_audio_device.cpp`](../apps/standalone/native_tests/test_standalone_audio_device.cpp).
It links the actual [AudioDevice](STANDALONE_AUDIO.md),
[Session](STANDALONE_SESSION.md), unchanged nominal core and pinned SDL2.
It uses public APIs and the real SDL dummy callback thread; it supplies no
Session/core/backend doubles and does not call a private callback directly.

## Run the optional native gate

Prerequisites are the separately verified
[SDL2 checkout](STANDALONE_DEPENDENCY.md), a C++20 compiler and CMake 3.21+.
From the repository root, with the checkout at `../SDL2`:

```sh
cmake -S . -B build-native -DCMAKE_BUILD_TYPE=Release \
  -DHAMMOND_BUILD_STANDALONE=ON -DHAMMOND_SDL2_ROOT=../SDL2
cmake --build build-native --target test_standalone_audio_device
ctest --test-dir build-native --no-tests=error \
  -R '^test_standalone_audio_device$' --output-on-failure -V
```

CMake generates the nominal profile, supplies `HAMMOND_TEST_PROFILE`,
`HAMMOND_SOURCE_DIR` and `SDL_MAIN_HANDLED`, and applies the strict project
compiler flags. This target lives in `native_tests/`, outside the ordinary
SDK-free test glob, and exists only with the optional standalone build enabled.
CTest explicitly supplies `SDL_AUDIODRIVER=dummy` and a 15-second timeout.
For direct invocation, supply that environment setting yourself; the test refuses
a missing/different value. Neither this fixture nor production code silently
changes driver-selection environment variables.

## Assertions and evidence

| Gate | Maintained assertions |
| --- | --- |
| Full supported matrix | All 44,100/48,000/96,000 Hz × 128/256/512/1,024/2,048 frames; exact requested/obtained values on this dummy backend, native float32, two channels and exact stereo byte extent. |
| Prepared pause | No callbacks over an observed two-buffer interval (minimum 5 ms); queued registration and manual/pedal notes do not apply before start. |
| Actual rendering | Both manuals and a pedal hold apply; finite positive Session peak; live expression update and an independent manual release apply by sequence acknowledgment. |
| Clock accounting | After callback quiescence, rendered frames equal callbacks × obtained buffer, and the Session clock equals initial clock plus rendered frames. |
| Stop/restart | Stop releases every hold, preserves controls/clock, clears peak and prevents callbacks during observation; restart advances that same clock with no restored holds or catch-up. |
| Admission/cleanup | Uninitialized audio, unsupported rates/buffers, embedded-null/missing device names, duplicate opens/starts and invalid profiles reject. Failed preparation preserves stopped music and permits a subsequent real open. |
| Device selection | Copied enumeration matches SDL's names; default and named opens both run. Reopen preserves transport lifetime counters while resetting the prepared source clock. |
| Lifetime | Active close and active destructor stop/join before Session teardown; repeated close is harmless; counters stay still after explicitly closed Session destruction. Eight dedicated cycles supplement matrix shutdowns. |
| Real failures | Actual timeline overflow and actual publication exhaustion increment render-failure counts without successful frames; exhausted start leaves the backend paused. |

Main-thread polling uses a monotonic 1.5-second deadline and `SDL_Delay(1)`.
Progress is condition-based; the suite does not require an exact callback count
or assume a sleep schedules a callback. Quiet-state checks are bounded observed
intervals. SDL global quit occurs only after every device and Session is gone.
Diagnostics are compared as a coherent collection only after callbacks quiesce.

## Executed result and limits

[Assignment 19](development/2026-11-13-next-phases/19-device-acceptance.md)
records source hashes and the independent direct build. GCC 14.2.0 on Linux
x86-64 with SDL2 2.32.10 passed all 15 cases in **2.878 seconds**: **75 matrix
callbacks, 59,520 rendered frames**, 31 rejected opens, two expected render
faults and eight lifetime cycles. Successful matrix runs had zero render,
format, overrange or nonfinite failures. The frame count represents 119,040
stereo sample values; positive peaks come from the real Session snapshot.
Counts describe that observed schedule and are allowed to differ on another run.

The test, AudioDevice and Session also passed ASan/UBSan in **2.952 seconds**
against the unchanged, uninstrumented core/SDL static libraries. LeakSanitizer
could not operate under this environment's tracing; leak detection remains
blocked and was disabled only for the separately reported ASan/UBSan run.

The dummy backend discards audio. This gate validates obtained stereo format,
real processing and fault diagnostics; it does not capture final output buffers
or independently prove the contents of failure-silenced buffers. The separate
Session acceptance establishes its sample mapping/parity. Deliberately corrupted
obtained specs, malformed callback buffers and transport clipping/nonfinite
fault injection remain separate acceptance work. Actual hardware negotiation,
audible playback, hotplug/recovery, deadlines/underruns, allocation/race probes,
other platforms and measured instrument fidelity are not qualified here.
