# Standalone device-removal acceptance

The maintained independent test is
[`test_standalone_device_removal.cpp`](../apps/standalone/native_tests/test_standalone_device_removal.cpp).
It qualifies the [device-removal contract](STANDALONE_DEVICE_REMOVAL.md) with the
actual AudioDevice, Session, nominal core and pinned SDL2. It covers current
handle identity, event classification and callback/owner lifetime. The dummy
backend and explicitly injected events do not establish physical hotplug.

## Independent basis

SDL 2.32.10's `include/SDL_events.h` defines a removed event's `which` as an
`SDL_AudioDeviceID`; an added event instead carries an enumeration index.
Its `src/audio/SDL_audio.c` emits zero for removal of an unopened device and a
nonzero opened ID for an opened-device disconnect. `include/SDL_audio.h`
documents that a closed ID can be immediately reused. These primary sources
were inspected in the [pinned dependency](STANDALONE_DEPENDENCY.md), commit
`5d249570393f7a37e037abf22cd6012a4cc56a71`.

Expected cases are literal test fixtures, not values returned by the production
predicate. `SDL_GetAudioDeviceStatus` independently confirms that the exposed ID
names a paused or playing actual SDL device and becomes stopped after close.
All 93 queued fixtures make a public `SDL_PushEvent`/`SDL_PeepEvents` round trip;
the test checks their type, ID and capture flag. No private callback, substitute
Session/backend or private-memory access is used.

The fixture applies its own small close-if-matched action. An incorrect positive
match therefore closes the actual device and fails preservation checks. This is
an adapter fixture, not execution of the application's complete event handler.
Main's type guard and predicate call were independently inspected in source;
assignment 43 retains its separate actual-application probe evidence.

## Maintained checks

| Case | Required observed behavior |
| --- | --- |
| Closed or failed open | ID zero; removal never matches; uninitialized audio, invalid rate and invalid profile reject without acquiring an exposed handle or changing stopped music. |
| Opened, initially paused | Nonzero ID resolves to SDL's paused device; duplicate open preserves it; queued controls/notes stay unapplied; matching query has no side effect. |
| Unopened or unrelated output removal | Zero and a different nonzero ID do not match; actual device status, controls and note ownership survive. |
| Capture events | Flags 1, 2 and 255 reject, including when the numerical ID equals the current output. |
| Added events | Current-ID-shaped, zero and unrelated `which` values reject; an enumeration index cannot close an output handle. |
| Actual running output | Both manuals and an independently owned pedal apply by sequence acknowledgment; ignored events preserve all holds and positive finite audio while the sample clock advances. |
| Stop and restart | Stop retains the ID, pauses/joins callbacks, clears all holds and preserves controls/clock; ignored events remain harmless; restart advances time without resurrecting notes. |
| Matching removal | A current output event matches; the fixture closes the actual backend, joins callbacks and clears all owners, including non-UI channels. Controls survive and subsequent old-ID events reject while closed. |
| Reopen and reuse | A successful reopen revalidates the current ID. If SDL reused the previous integer, it identifies the current device; the test neither assumes nor promises unique generations. |

Three cycles exercise 44,100 Hz / 128 frames, 48,000 Hz / 256 frames and
96,000 Hz / 512 frames. The existing [audio-device matrix](STANDALONE_AUDIO_ACCEPTANCE.md)
separately covers all fifteen supported rate/buffer combinations.

After callback quiescence, each cycle requires rendered frames to equal its
callback count times the obtained buffer size, and the Session clock to equal
the requested initial clock plus those frames. Quiet intervals observe that
paused/closed counters and stopped snapshots remain unchanged. Every successful
cycle requires zero render/format/nonfinite/overrange failures, queue overflows,
rejections, recovery, discarded commands and Session faults.

Polling has a 1.5-second monotonic progress deadline and one-millisecond sleeps
on the test main thread. The test waits for actual acknowledgment/progress;
wall time and callback counts are not device-latency or deadline measurements.
No handle-generation, stale-event authentication or automatic reconnect policy
is invented. A software removal fixture does not itself disconnect SDL.

## Reproduce

Use the [standalone prerequisites](STANDALONE_APP.md), with the separately
verified SDL checkout at `../SDL2`, from the repository root:

```sh
cmake -S . -B build-native -DCMAKE_BUILD_TYPE=Release \
  -DHAMMOND_BUILD_STANDALONE=ON -DHAMMOND_SDL2_ROOT=../SDL2
cmake --build build-native --target test_standalone_device_removal --parallel 2
ctest --test-dir build-native -R '^test_standalone_device_removal$' \
  --no-tests=error --output-on-failure -V
```

CTest explicitly supplies `SDL_AUDIODRIVER=dummy`, a 15-second timeout and
`standalone;native` labels. The test refuses a missing or different driver
setting. CMake supplies the generated profile, source/test includes and strict
project compiler options; the maintained target is an input to the native
aggregate. Ordinary SDK-free builds do not acquire SDL or build this target.

## Executed result and limits

[Assignment 44](development/2026-11-13-next-phases/44-audio-removal-acceptance.md)
records the coherent source and exact artifacts. Its first strict build and
execution passed **1/1 CTest**, zero failures/skips, in **0.23 seconds**:
3 lifecycle cycles, 93 queued events, 78 ignored events, 10 matching pure queries,
3 matched joined closes and 10 rejected opens. The run observed 2 reused IDs,
12 callbacks and 3,584 rendered frames. Timing and callback counts may vary.

No production or fixture repair was needed by this independent test. Root owns
the separately executed assembled-source gate and publication. Physical device
disconnect/reconnect, actual app recovery on each desktop platform, deadline and
latency measurements, native accessibility and acoustic fidelity remain separate
gates under the [M9 plan](PLAN.md). No sanitizer or other-platform pass is claimed
by this ordinary Linux Release execution.
