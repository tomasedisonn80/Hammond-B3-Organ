# Calibrated standalone callback allocation acceptance

The maintained native test
[`test_standalone_callback_allocation.cpp`](../apps/standalone/native_tests/test_standalone_callback_allocation.cpp)
observes global C++ allocation and deallocation calls made by the production
`AudioDevice` callback on an actual SDL2 dummy audio thread. It executes real
Session, ownership, Engine and SDL implementations with the nominal profile.
The [assignment record](development/2026-11-13-next-phases/21-callback-allocation.md)
retains the executed source/library identities, commands and results.

## Transparent test boundary

The test links a separately compiled `AudioDevice.cpp` object with the **private,
translation-unit-only** definition
`SDL_OpenAudioDevice=hammond_probe_open_audio_device`. Its test executable includes
ordinary SDL headers and exports this matching shim:

```cpp
extern "C" SDL_AudioDeviceID SDLCALL hammond_probe_open_audio_device(
    const char*, int, const SDL_AudioSpec*, SDL_AudioSpec*, int);
```

The shim retains the requested callback and userdata in fixed storage, substitutes
an observing trampoline, and delegates to the real `SDL_OpenAudioDevice`. SDL
still opens the device, creates its audio thread, supplies the stream and invokes
callbacks. The trampoline arms thread-local counters immediately before calling
the original callback with its original userdata and actual SDL buffer; it stops
recording immediately afterward. Callback implementation/source remains unchanged.
This is a test-instrumented recompilation, not qualification of a shipping binary.
The normal application target receives no alias, replacement callback or probe.

Global scalar, array, nothrow, sized-delete and aligned new/delete replacements
follow the portable patterns in `tests/test_realtime.cpp`. Before **and** after
every original callback, including each device's first callback, separate scopes
explicitly exercise all forms through volatile function pointers. Each calibration
must see 12 allocations and 12 nonnull frees, with valid aligned storage. This
avoids optimized-away new expressions and fails if instrumentation is inactive.
Calibration also verifies that the callback thread differs from the main thread.
No assertion, formatting or fixture allocation runs inside a measured API scope.
Fixed arrays and atomic aggregates retain evidence without dynamic recording.

## Required workloads

At obtained 48,000 Hz native float32 stereo, both **128 and 2,048 frame** bounds run:

| Boundary | Required observation |
| --- | --- |
| First callback | Preposted controls, both manuals, pedals and enabled upper-B percussion; nonzero finite stereo output. |
| Full queue | Exactly 256 accepted restores applied in FIFO order, with no rejection/discard and retained active owners. |
| Ordinary release | Independent manual and pedal note-offs preserve remaining owners. |
| Scoped release | `ReleaseUiNotes` releases UI channel 0 while an independent channel-2 owner survives. |
| Panic | Global owner release; callback processing remains active. |
| Overflow recovery | Reestablished active owners, 255 pending restores plus a pending release; the next release returns QueueFull and further post returns RecoveryPending. Actual callback discards all 256, releases every owner and preserves prior controls. |
| Core rejection | An accepted zero-offset invalid-bus note reaches authoritative core admission; callback publishes recovery and discards its following command. |

Additional actual 128-frame callbacks hit timeline overflow and publication
exhaustion. The latter follows two successful active callbacks, so the emergency
path has held notes to release. Callback output inspection verifies complete
silence for those render failures; no fake Session or private callback is used.
Ordinary and rejected `Session::post` and snapshot reads during callback activity
and after exhaustion are counted on the main thread, including an empty Session.
Busy reads are permitted during publication; observing one is not required.
Construction, preparation, lifecycle, profile loading and SDL setup are outside
these observations. Main-thread SDL pause/lock operations make queued-prefix
fixtures deterministic while retaining Session's running musical state.

## Build and execution

Enable the pinned optional native build as described in
[standalone dependencies](STANDALONE_DEPENDENCY.md). The integrator owns the CMake
target, which must link the probe AudioDevice object, standalone support/core and
actual SDL2, without also linking the ordinary AudioDevice library. Supply the
same test profile/source definitions as other tests and `SDL_MAIN_HANDLED`.
Select `SDL_AUDIODRIVER=dummy` explicitly and impose a 15-second test timeout.
The retained assignment also provides the executed independent direct build.

Observed GCC 14.2 Release result: **18 workload observations, 39 actual callbacks,
78 positive callback-thread calibrations and 936 allocation/free pairs**. Every
measured production callback, 1,070 main-thread posts and 753 snapshot reads
reported zero C++ new/delete calls. Execution took 1.003 seconds; read/callback
counts can vary with scheduling and are guarded by minimum/exact relations.

## Qualification limits

This gate observes intercepted global C++ allocation/deallocation calls only.
C heap/system allocations, custom allocators, locks, deadlines, underruns, races,
hardware audio, hotplug, audible output and other platforms require separate
evidence. Calibration deliberately allocates outside the measured original
callback and changes timing, so this executable supplies no timing guarantee.
It does not establish an allocation-free uninstrumented binary, the full rate
matrix, complete M9 readiness or measured instrument fidelity.
