# Agent 10 — responsive MIDI discovery and macOS replay repair

Actual assignment: `/root/w02_a10_macos_replay_repair`, wave 2, 2026-11-14.
The isolated repair builds and passes five targeted Linux Release gates. The
original hosted macOS failure remains an explicit platform gate until a new
published macOS job completes. This note does not claim physical MIDI or macOS
qualification.

## Retained original failure

The published `d493e998e5dd7cf44db46854e87309745063ac54` macOS 15.8.2 arm64,
AppleClang, MIDI ON [job 132404712542](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43580730364/job/132404712542)
failed `test_modal_ctrl_and_command_m_open_then_escape_restores_playing` for
`modifier=meta`. Its 600 ms script scheduled eight events but pushed only three.
The two retained observations were at 44 ms and 4746 ms. No musical note-on or
note-off command had been accepted. Audio continued through 370 callbacks and
189,440 frames, with zero render, format, range or finite-value failures.

The observed error was:

> Input replay could not finish delivery and acknowledgment within its bounded drain interval

The compact [original evidence](reports/a10-original-macos-failure.json) retains
the job/source identity, original diagnostic line, full-log SHA-256, counters,
times and error excerpts. The full original log remains in the integrating
workspace as `baseline-hosted-macos-standalone.log`.

Source inspection found that opening the MIDI modal synchronously called
`MidiDevice::enumerate_input_ports` in the SDL event handler. That call constructs
an RtMidi query object, enumerates native ports and destroys the object before
returning. The failure is consistent with a stall across this boundary. The log
has no subcall instrumentation, so it does not establish whether construction,
port querying or teardown consumed the native delay. The two-second replay
drain policy correctly exposed the stalled event delivery and remains unchanged.

## Implemented behavior and ownership

[`MidiDiscovery.h`](../../../apps/standalone/MidiDiscovery.h) owns one joined
worker and one value result. The worker invokes only the static enumeration
query. It receives no live `MidiDevice`, `MidiInbox`, Session, UI or SDL object.
The query publishes completion with release/acquire synchronization; the owner
does not access its strings or vector before publication or joining. An unfinished
poll leaves the caller's destination untouched. The helper rejects a second
worker while the first job or its unconsumed result is outstanding.

The application gives each explicitly opened native MIDI modal a nonwrapping
generation. It accepts choices only when the completed generation still belongs
to the open modal. Closing or replacing the modal discards its UI result;
close/reopen queues only the newest explicit generation after the old query is
reaped. There is no automatic retry of a failed generation. The current exact
selected name, or explicit No input, is preserved when new names arrive. A
missing name never selects or opens the first returned device.

While discovery runs, the modal displays its searching state and remains
responsive. Explicit No input and Disconnect remain available. Apply cannot
connect a nonempty provisional or stale name before successful enumeration of
the current generation. The existing subsequent exact-name/duplicate admission
still applies. Later Apply/Disconnect results and changed fault status cannot be
overwritten by an older discovery result.

Enumeration failure always remains an application error, including a result
that arrives after the modal closes. Exceptions are contained in the worker,
failed partial name vectors are cleared, and the owner receives a failure. At
shutdown, audio stops before an outstanding query is joined; any late failure
is included before replay health and final diagnostics are computed. No worker
is detached. Native OS calls provide no portable cancellation or execution
deadline, so this shutdown join can wait for the OS. Event delivery no longer
waits for native enumeration; the replay delivery deadline was not widened.

The pinned RtMidi CoreMIDI source uses a process-level native client singleton.
The helper owns a separate RtMidi query object, not an independent CoreMIDI
client. Startup connection precedes the event loop; a nonempty modal Apply
requires completed discovery; only one discovery can execute. These constraints
avoid concurrent first-client initialization. Physical ports, hotplug and actual
CoreMIDI scheduling still need their own platform evidence.

Diagnostic schema 3 retains every prior field and adds `midi.discovery`:
requests, starts, completions, discarded results, failures, and pending/join
state around shutdown. Here pending means an outstanding joinable worker/result,
which may already have finished its native call. The exact recursive schema and
the exact no-input diagnostic expectations were extended, not relaxed. No sound
parameter, state version/reader, note ownership or replay assertion changed.

## Coherent source and executed checks

Other workers were changing UI model/layout headers. To avoid mixing those
headers with older libraries, this repair was built from one deliberate source
snapshot based on `c83fe2336be931385f0d7ab82c55b30bfdfc8fc6`. Only the seven overlays
listed and SHA-256 identified in [a10-source.json](reports/a10-source.json) were
applied. That includes the integrator's standalone `Threads::Threads` linkage;
it excludes later live UI/CMake additions. The unchanged atlas PDF and historical
report payloads were omitted from this build snapshot. No dependency was cloned.
Snapshot source occupied about 30 MB; its targeted build occupied about 33 MB.

The configuration was Release, GCC 14.2, Python 3.12, SDL 2.32.10 at
`5d249570393f7a37e037abf22cd6012a4cc56a71`, and RtMidi 6.0.0 at
`1e5b49925aa60065db52de44c366d446a902547b` with the existing recorded CoreMIDI zero
initialization patch. MIDI was ON. `SDL_ALSA=OFF` was retained for the separately
documented local SDL/header mismatch; the native MIDI backend remained ALSA.
All windowed acceptance used dummy SDL video/audio.

| Gate | Observed result |
| --- | --- |
| `test_standalone_midi_discovery` | Passed: 4096 owner polls while the probe is deliberately blocked; one-worker admission; exact ordered/duplicate names; zero-port success; backend failure; exception; 32 sequential generations; joined cleanup. |
| `test_standalone_app` | Passed: 18 Python cases, 164 native subprocesses, including strict diagnostic schema. |
| `test_standalone_midi_cli` | Passed: 15 cases, 95 subprocesses. This container retained 13 enumeration errors and 11 expected failed UI replays; it reported zero successful native-enumeration UI replays. |
| `test_standalone_native_midi_replay` | Passed: 12 cases, 17 subprocesses, including one expected interrupted replay. Synthetic MIDI acceptance is separate from physical ports. |
| `test_standalone_replay_boundaries` | Passed: nine cases, 29 subprocesses, including 19 preserved setup rejections. |

CTest reported **5/5 passed in 48.28 seconds**. The [summary](reports/a10-ctest.txt),
[complete selected test output](reports/a10-targeted-tests.txt) and
[machine-readable result](reports/a10-result.json) retain actual outcomes.
Final ownership-wording-only edits were rebuilt and produced the identical
tested executable SHA-256:
`1630dd3edeacc7ea3013b84b32c56c95eaa3bceb61f26e1f9b7446db75f870f7`.

An additional [retained execution of the original eight-event sequence](reports/a10-linux-original-sequence.json)
delivered all eight events, accepted one note-on and one note-off after Escape,
and completed acknowledgement. Its process still exited 1 and `replay.passed`
remained false because this container lacks `/dev/snd/seq`; the ALSA enumeration
error was correctly retained. This demonstrates the error-preservation behavior
and local event path, not successful CoreMIDI enumeration.

## Reproduction and next step

The integrating workspace contains:

```text
/workspace/scratch/601951e27dc3/midi-checkpoint-source
/workspace/scratch/601951e27dc3/build-midi-checkpoint
```

The actual configure/build commands were:

```sh
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/cmake \
  -S /workspace/scratch/601951e27dc3/midi-checkpoint-source \
  -B /workspace/scratch/601951e27dc3/build-midi-checkpoint \
  -DCMAKE_BUILD_TYPE=Release -DHAMMOND_BUILD_STANDALONE=ON \
  -DHAMMOND_SDL2_ROOT=/workspace/scratch/7ffc2842608b/SDL2 \
  -DHAMMOND_ENABLE_MIDI=ON \
  -DHAMMOND_RTMIDI_ROOT=/workspace/scratch/cd4bd06ce68f/rtmidi \
  -DALSA_INCLUDE_DIR=/workspace/scratch/641ca55ce6de/native-sysroot/usr/include \
  -DALSA_LIBRARY=/workspace/scratch/641ca55ce6de/native-sysroot/usr/lib/x86_64-linux-gnu/libasound.so \
  -DSDL_ALSA=OFF
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/cmake \
  --build /workspace/scratch/601951e27dc3/build-midi-checkpoint \
  --target hammond_standalone test_standalone_midi_discovery -j4
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/601951e27dc3/build-midi-checkpoint \
  --no-tests=error --output-on-failure \
  -R '^(test_standalone_midi_discovery|test_standalone_app|test_standalone_midi_cli|test_standalone_native_midi_replay|test_standalone_replay_boundaries)$'
```

The integrator should publish the coherent MIDI repair checkpoint, run the
existing native macOS AppleClang/MIDI ON workflow against the exact published
commit, and retain its original modal and all selected native acceptance results.
Success requires complete event delivery, preserved note counts, unchanged
deadline, joined query cleanup and no hidden native enumeration error. A job
dispatch or this Linux pass does not close that gate. Physical device
open/disconnect/hotplug qualification remains separate.

Owned changes: `MidiDiscovery.h`, its C++ test, targeted `main.cpp` MIDI ranges,
the static-query ownership comments in `MidiDevice.h`, strict discovery schema
additions in `test_standalone_app.py`, the discovery section of
`docs/MIDI_BACKEND.md`, this note and `reports/a10-*`. The integrator owns shared
status, setup/next-step entry points, CMake, commit/publication and hosted result
follow-up. Current task status: implementation and bounded local validation
complete; macOS publication/observation remains for integration.
