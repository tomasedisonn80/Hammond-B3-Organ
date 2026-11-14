# A16 — native application MIDI integration

Actual assignment A16 in the new `2026-11-14-midi-ui` session, logical wave 3.
Owned files: `apps/standalone/main.cpp` and this note only. No shared header,
CMake, Engine, profile, parameter, state-format, renderer or test file was
changed by this worker. The integrator owns combined qualification, current
status and publication; no commit or push was performed by A16.

## Source and implementation boundary

The inspected checkout HEAD was
`7b36cfac2565397191b3df5e07112611e7f1b0e1`, with the concurrent A13–A15 MIDI
and geometry work present. The final A16 `main.cpp` SHA-256 is
`f57cad73282e37fa37a0eae6adc518d352062905dacabe1f8724195b2216bed4`.
This is a source-file identity, not a claim that the entire concurrent working
tree was frozen or that a native executable was qualified.

The implementation follows `docs/MIDI_INPUT.md`, `docs/MIDI_BACKEND.md` and
their declared interfaces. The current atlas review carries forward PDF
pp. 151–156, 379–396 and 417–438: independent owner scopes, one musical
producer/consumer boundary, shared desired controls and honest timing. Native
audio remains the existing nominal dry core. No scanner, rotary, sound-profile
or public-control behavior was added.

## CLI and modal operation

`--list-midi` runs before any SDL initialization. It prints the compiled backend
and exact enumerated names, distinguishes a successful empty list from backend
unavailability/failure, and returns failure for an unavailable or failed query.
It neither opens a MIDI port nor creates an SDL window. `--list-audio` and
`--list-midi` are mutually exclusive.

`--midi-port NAME` requests one exact input. Omission selects no input. The three
new options `--midi-upper-channel`, `--midi-lower-channel` and
`--midi-pedal-channel` accept only distinct one-based integers in 1–16, default
to 1/2/3, and reject invalid arguments before SDL. They are application setup,
not `B3CONTROLS3` content. Overlong names reject before backend work.

The appended `UiAppRequest::MidiSettings` and Ctrl+M/Command+M open the MIDI
overlay. It uses the existing `ViewOverlay::Midi`, `MidiOverlayLayout` and
`InstrumentViewInfo` fields without extending their shared contract. Keyboard
and pointer focus use eight shared rectangles, in this order:

1. Previous port.
2. Next port.
3. Upper channel.
4. Lower channel.
5. Pedal channel.
6. Apply.
7. Disconnect.
8. Close.

Tab/Shift+Tab, arrows, Home/End, Enter/Space and Escape operate the modal.
The first selection is **No input**; subsequent choices retain exact backend
names in enumeration order. Draft channels may temporarily coincide while
editing, but Apply rejects duplicates without changing the active transport or
routing. A duplicated port name also rejects before replacing an active port.
The backend performs the final open-time name validation. Apply leaves the
modal visible so the selected settings and result can be inspected. Disconnect
does not apply an invalid draft routing.

Opening a settings/help modal, ordinary focus loss, resize and control-file
load retain external ownership. These existing UI paths release only UI owners.
An audio restart explicitly retires MIDI and requires a later MIDI Apply.

## Main-thread dispatch and lifecycle

The main/UI thread remains the only `Session::post` producer. Each loop turn
drains at most `kMidiDrainBudget` (32) packets. Each decoded action is dispatched
before decoding the next packet. No timestamps are sorted or converted into
sample deadlines; messages apply at the existing next callback boundary.

Decoded note/scoped-release commands have their result checked directly. They
do not use `UiModel::submitted`, whose InvalidCommand recovery can request an
unrelated UI-owner release. MIDI parameter edits instead call
`UiModel::external_parameter` and dispatch its ordinary complete-snapshot action
once, including its existing acknowledgment path. No raw duplicate CC event is
posted. The main thread observes Session recovery both at its normal frame
observation and between accepted MIDI actions.

An explicit port replacement ends the old decoder epoch, closes the backend,
preserves observed fault bits, and resets the inbox only after
`is_quiescent()`. It posts the three declared MIDI-owner releases once in order.
The explicit pending Apply request may open the next epoch only after the final
release is resolved/applied, a Session recovery is observed, or the existing
joined audio-close/Session-stop lifecycle has cleared all owners and queued
commands. A partial or failed release batch cannot satisfy that acknowledgment
with its last accepted partial sequence. A full queue is never spun or retried.

Backend faults, inbox faults, MIDI submission failures, deliberate global
Panic, observed Session recovery, audio failure/removal/restart and application
shutdown retire the input epoch and discard its unconsumed prefix. Fault and
Panic paths cancel pending Apply requests. There is no automatic reconnect or
old-note replay. Healthy active connections are polled approximately every
250 ms, with prompt fault polling. Polling has the backend contract's
best-effort hotplug limits.

`MidiLifetime` owns one dynamically allocated inbox followed by one device.
Every normal close destroys those objects normally. If native teardown cannot
establish quiescence, the application marks shutdown failure, disables further
input/open attempts and requires restart. It never resets that inbox or creates
a replacement device. On destruction the single exceptional inbox is retained
with the backend's quarantined context until process termination, so a late
callback cannot reference freed queue storage. The quarantine is explicit in
diagnostics and yields a failing application exit status.

## Native diagnostics

The JSON schema is now **2**. Existing runtime/audio/session/control/smoke/replay
objects retain their meanings. The new `midi` object reports copied device,
inbox and decoder counters; requested port and configured channels; backend
availability; before/after-shutdown state; pending/accepted scoped-release
information; retired fault bits; maximum drain observed; setup/shutdown failures;
and the callback-boundary/steady-clock diagnostic timing policy.

Final counters are copied after close. The report explicitly marks whether
quiescence was achieved and whether those observations are stable. A quarantined
callback context is not mislabeled as joined, and a successful zero-port
enumeration is not mislabeled as an unavailable backend. These counters do not
constitute physical controller, latency or drop-out measurements.

## Executed checks and next qualification

Working directory:
`/workspace/scratch/cd4bd06ce68f/Hammond-B3-Organ`.
Compiler: Debian GCC/C++ **14.2.0-19**. The existing native build supplies the
pinned SDL include/configuration and generated embedded-profile header.

The following strict translation check passed with exit status 0 and no output:

```sh
c++ -std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion \
  -Wshadow -Werror -DSDL_MAIN_HANDLED \
  -I/workspace/scratch/cd4bd06ce68f/build-native/apps/standalone/generated \
  -Iapps/standalone -Iinclude \
  -I/workspace/scratch/cd4bd06ce68f/build-native/_sdl2/include \
  -I/workspace/scratch/cd4bd06ce68f/build-native/_sdl2/include/SDL2 \
  -I/workspace/scratch/cd4bd06ce68f/build-native/_sdl2/include-config-release/SDL2 \
  -fsyntax-only apps/standalone/main.cpp
git diff --check -- apps/standalone/main.cpp
```

The whitespace check also passed. This worker did **not** execute or claim a
linked native MIDI application, screenshot comparison, live MIDI controller,
audio device, failure-quarantine backend fixture or OS hotplug test. No temporary
renderer/backend stub was linked to imply native acceptance.

The integrator's next combined build needs A14's real/disabled `MidiDevice.cpp`
wiring and A17's `midi_overlay_layout`/painting implementation. Subsequent native
acceptance must update the schema-1 assertions and verify default no-input,
disabled listing with invalid SDL drivers, exact port/channel rejection,
modal navigation, owner preservation, explicit replacement acknowledgment,
global recovery/Panic/audio restart retirement, bounded draining and shared CC
state. MIDI replay/injection work belongs to the next wave. Actual backend
platform and physical controller qualification remain separate gates.
