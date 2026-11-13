# Standalone output-device removal identity

The native application closes its audio transport only when an SDL removal event
identifies the output that is currently open. Removing an unopened output, an
unrelated output or a capture device must leave its current playback intact.
This repairs the former application condition, which closed any open transport
on every output-removal event regardless of the event's `which` value.

## Pinned SDL semantics

This contract uses the [locked SDL 2.32.10 source](STANDALONE_DEPENDENCY.md),
commit `5d249570393f7a37e037abf22cd6012a4cc56a71`. Its
[public event structure](https://github.com/libsdl-org/SDL/blob/5d249570393f7a37e037abf22cd6012a4cc56a71/include/SDL_events.h)
defines `which` as an enumeration index for `SDL_AUDIODEVICEADDED`, and an
`SDL_AudioDeviceID` for `SDL_AUDIODEVICEREMOVED`. Zero `iscapture` means output;
every nonzero value means capture.

The same pinned [audio implementation](https://github.com/libsdl-org/SDL/blob/5d249570393f7a37e037abf22cd6012a4cc56a71/src/audio/SDL_audio.c)
posts an opened device's ID from `SDL_OpenedAudioDeviceDisconnected`. Its
`SDL_RemoveAudioDevice` explicitly posts `which = 0` when the removed device was
not open, allowing applications to refresh their device lists. The zero event
is therefore a legitimate unopened-device notification, not evidence that this
application's active output has disappeared. Added-event indices cannot be
compared as though they were open handles.

## Internal adapter API

Both methods belong to the main-thread-owned
[`AudioDevice`](../apps/standalone/AudioDevice.h). They perform no allocation,
SDL calls, mutation or callback work; neither may race device lifecycle calls.

| Operation | Contract |
| --- | --- |
| `device_id()` | Current opaque SDL handle, or zero while closed. Successful open exposes the actual accepted handle. |
| `is_removed_by(event)` | True only for REMOVED, output, an open nonzero current ID, and exact equality between `event.which` and that current ID. |

The predicate matches while the device is paused or running. It classifies an
event without closing anything. A failed initial open leaves zero; a refused
duplicate open preserves the existing handle. Stop retains the open handle;
close clears it after SDL has joined the callback. Existing
[Session/device lifecycle ordering](STANDALONE_AUDIO.md) is unchanged.

SDL may reuse an ID after close. The value is not a hardware serial, enumeration
index, persistent setting or generation identifier. A later open returning the
same integer makes it the current handle again. This API alone cannot distinguish
an old queued event with that reused value from a current matching event.

| Event or device state | Predicate |
| --- | --- |
| Current open output's REMOVED event | True, paused or running |
| REMOVED with `which = 0` | False |
| REMOVED with a different ID | False |
| Capture removal, including a matching number | False |
| ADDED or any other event type | False |
| Closed device, including its former ID | False |

## Application handling

[`main.cpp`](../apps/standalone/main.cpp) retains an outer REMOVED type check
before reading the audio-event union member, then calls `is_removed_by`.
Matching removal follows the existing path: release UI ownership, close/join
audio, disable live commands, observe the stopped Session and show the Audio
settings restart message. Ignored events perform none of that cleanup. There
is no automatic reopen, new stored control or diagnostics-schema field.

## Executed engineering evidence

[Assignment 43](development/2026-11-13-next-phases/43-audio-removal.md) rebuilt the
actual application source with a scratch-only public SDL event-injection shim.
The shim delegates the real event wait, then pushes one event after 150 ms;
it uses no private SDL entry point and does not extend the replay grammar.

| Injected event | Old source at `5b8e241` | Repaired source |
| --- | --- | --- |
| Output REMOVED, ID zero | Closed audio; smoke failed, exit 1 | Audio stayed open/running; smoke passed |
| Output REMOVED, `UINT32_MAX` | Closed audio; smoke failed, exit 1 | Audio stayed open/running; smoke passed |
| Capture REMOVED, ID zero | Smoke passed | Smoke passed |
| Output ADDED, index zero | Smoke passed | Smoke passed |

All four repaired probes reported zero application/audio/session faults and
joined with no held notes. The ordinary unshimmed executable separately passed
its 600-ms dummy smoke. Existing audio-device and calibrated callback-allocation
CTest suites passed 2/2. Exact sources, binaries, counters and commands are in
the assignment record. The separate [maintained independent acceptance](STANDALONE_DEVICE_REMOVAL_ACCEPTANCE.md)
owns its actual ID, public event-queue, music and reopen checks.

## Next qualification

Build the native test inputs before running `test_standalone_device_removal` and
the affected application/device suites. The coordinator records combined-source
and hosted results separately. Real disconnect/reconnect, queued-event behavior
across rapid reopen, physical callback progress, desktop handling and multiple
native backends still need acquired device evidence. Synthetic SDL events and
dummy audio establish no physical hotplug or latency qualification.
