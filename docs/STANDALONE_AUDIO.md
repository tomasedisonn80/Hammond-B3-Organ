# Standalone SDL2 output transport

[`AudioDevice`](../apps/standalone/AudioDevice.h) connects the existing
[`Session`](STANDALONE_SESSION.md) to the explicitly enabled, pinned
[SDL2 dependency](STANDALONE_DEPENDENCY.md). It owns no Engine, note ledger,
resampler, effect or replacement DSP. The active sound remains the existing
nominal dry organ; device safety conversion is described below.

## Application ownership and configuration

The main thread owns every device operation, SDL initialization/termination,
device enumeration, copied display information and error strings. Initialize
`SDL_INIT_AUDIO` before enumeration/open and close all devices before SDL quit.
The Session must outlive its AudioDevice. Neither object is copyable or movable.
Lifecycle also requires the Session's snapshot readers to be quiescent.

| Setting | Accepted value |
| --- | --- |
| Output name | Empty for SDL's default, or one copied device name; embedded null bytes reject. |
| Requested rate | 44,100, 48,000 or 96,000 Hz. |
| Requested buffer | 128, 256, 512, 1,024 or 2,048 frames. |
| Obtained callback format | Native-endian IEEE float32, two interleaved channels, zero-byte silence. |
| Obtained rate/buffer | Must remain among the supported values; SDL negotiation may select another supported value. |
| Obtained byte count | Exactly `buffer_frames * 2 * sizeof(float)`. |

`enumerate_output_devices` copies output names and preserves its destination
on failure. Enumeration is never performed in the callback. No implicit dummy
driver selection or retry occurs. Tests opt in with `SDL_AUDIODRIVER=dummy`.
Driver availability belongs to the actual SDL build and host, not this list.

## Lifecycle

1. `open(session, profile, config, error)` refuses an existing open device.
   SDL opens paused. All obtained fields are validated before Session preparation;
   the Session receives the obtained rate/frame bound and requested seed/clock.
   Every failed open closes its partial SDL device without retaining the Session.
2. The application explicitly posts its proposed initial or loaded controls
   while paused. Preparation itself retains the core's muted registration.
3. `start(error)` starts Session before unpausing SDL. Duplicate start rejects.
   A Session start failure leaves the device paused.
4. `stop()` pauses SDL, acquires/releases its callback lock to establish completed
   callback quiescence, then calls Session stop. The device stays open for restart.
   The Session releases owners/pending commands and preserves controls/source clock.
5. `close()` calls `SDL_CloseAudioDevice`, which waits for callbacks to return,
   before stopping/detaching Session. Destruction follows this same order.
   SDL global subsystems are never quit by AudioDevice.

To change device/rate/buffer/profile, copy desired controls, close, open, post
those controls, and start. Reprepare resets DSP as specified by Session. Device
removal and reconnect recovery are application actions; no automatic reopening
or wall-clock catch-up is implemented here.

## Callback admission and output policy

The SDL callback is the sole serialized Session consumer. It validates a nonnull
float-aligned pointer, positive byte length, complete stereo frames and a length
at or below the obtained buffer bound before forming an exact float span. Shorter
complete buffers render their exact frame count; no chunking or extra advance
occurs. Format/length rejection never enters Session. Failed or short Session
renders silence the supplied byte extent. Null/nonpositive buffers are counted
without dereference; SDL remains responsible for the pointer's writable extent.

Nominal Session output passes unchanged when finite and within **[-1, +1]**.
Finite samples outside that device range clamp to the nearest endpoint; there is
no hidden gain, normalization or limiter. Any NaN/infinite sample silences the
entire callback. Session peak remains the original nominal engineering peak,
which can exceed one; it is not calibrated acoustic level or post-clamp peak.

The callback performs no allocation, destruction, lock, I/O, logging, enumeration
or string formatting. Supported targets must have always-lock-free 64-bit and
status atomics. Counters have one callback writer, bounded load/store updates,
and lifetime saturation instead of wrap or reset during reopen.

`diagnostics()` copies callback/rendered-frame counts, render/format failure
counts, overrange/nonfinite callback and stereo-sample counts, the latest render
error and latest Session lifecycle result. Overrange counts include finite
outliers in a callback later silenced for nonfinite output. Rendered frames count
Session successes even when device safety subsequently silences them. Individual
atomic reads can span a callback; this is not a coherent musical snapshot.
`info()` copies driver, requested name/default label, obtained format/rate/buffer
and open/running state on the main thread. A default label is not a resolved
hardware name. Buffer duration is not measured device or round-trip latency.

## Executed evidence and remaining gates

[Assignment 15](development/2026-11-13-next-phases/15-audio-device.md) records
strict compilation, real Session/core dummy execution at all 15 rate/buffer
combinations, and separately identified transport fault-injection checks.
Physical audio, hotplug/recovery, actual device negotiation, deadline/underrun
qualification, calibrated allocation/race instrumentation and other platforms
remain separate gates. Dummy execution does not establish audible playback.
