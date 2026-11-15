# Native MIDI expression: setup and operating guide

The native standalone accepts one explicitly selected MIDI input, with distinct
wire channels for Upper, Lower and Pedals. **CC11 controls one global expression
value**, shared by all three divisions. Endpoint calibration converts that
controller's raw 0–127 values to normalized expression before the existing
musical control path applies them.

This guide covers the implemented `midi-expression-endpoints-v1` calibration
and the native CC120/121/123 subset. These adapter features leave the **47 musical
parameters**, **`B3CONTROLS4`** and readers 1–3 unchanged. They do not add a VST3
controller mapping or alter the nominal dry Engine. See the
[interface guide](INTERFACE_RUNBOOK.md) for general playing and the
[preset guide](PRESET_RUNBOOK.md) for registrations and Save/Load.

## Build the native application

Use a C++20 compiler, C compiler, CMake 3.21+, Python 3.10+ and Git. The reviewed
dependencies are **SDL 2.32.10** and, when physical MIDI is enabled, **RtMidi
6.0.0**. The acquisition tools fetch locked sources; CMake verifies them offline.
Keep those checkouts clean and separate from build directories. The
[SDL contract](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/STANDALONE_DEPENDENCY.md)
and [RtMidi contract](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/RTMIDI_BUILD.md)
retain exact source identities and the prepared RtMidi build-copy correction.

| Platform | MIDI backend | Native prerequisites |
| --- | --- | --- |
| Linux, excluding Android | ALSA | ALSA development headers/library, threads and SDL desktop/audio development packages; usable ALSA sequencer access at runtime. The existing [Linux package recipe](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/MIDI_UI_RUNBOOK.md#prerequisites-and-platform-backends) lists the project's desktop dependencies. |
| macOS | CoreMIDI | Apple compiler/SDK and CoreServices, CoreAudio, CoreMIDI and CoreFoundation. |
| Windows desktop | WinMM | Visual Studio 17 2022 x64 C/C++ tools, Windows SDK and `winmm`. |

### Linux or macOS, single-configuration build

From the repository root, choose new dependency and build destinations. The
dependency destinations' parent must already exist:

```sh
python3 tools/acquire_sdl2.py --destination ../SDL2
python3 tools/acquire_rtmidi.py --destination ../rtmidi-6.0.0
cmake -S . -B build-native-midi -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_STANDALONE=ON -DHAMMOND_BUILD_VST3=OFF \
  -DHAMMOND_SDL2_ROOT="$PWD/../SDL2" \
  -DHAMMOND_ENABLE_MIDI=ON -DHAMMOND_RTMIDI_ROOT="$PWD/../rtmidi-6.0.0"
cmake --build build-native-midi --config Release \
  --target hammond_standalone --parallel 3
build-native-midi/apps/standalone/hammond_standalone --help
```

For already acquired dependencies, replace the two acquisition commands with
`python3 tools/acquire_sdl2.py --verify-existing ../SDL2` and
`python3 tools/acquire_rtmidi.py --verify-existing ../rtmidi-6.0.0`.
Do not reacquire into an existing checkout.

### Windows, PowerShell and a multi-configuration build

Acquire or verify the same locked sources. For a fresh setup:

```powershell
python tools/acquire_sdl2.py --destination ../SDL2
python tools/acquire_rtmidi.py --destination ../rtmidi-6.0.0
$b3SdlRoot = (Resolve-Path ../SDL2).Path
$b3MidiRoot = (Resolve-Path ../rtmidi-6.0.0).Path
cmake -S . -B build-native-midi -G "Visual Studio 17 2022" -A x64 `
  -DBUILD_TESTING=ON -DHAMMOND_BUILD_STANDALONE=ON -DHAMMOND_BUILD_VST3=OFF `
  "-DHAMMOND_SDL2_ROOT=$b3SdlRoot" `
  -DHAMMOND_ENABLE_MIDI=ON "-DHAMMOND_RTMIDI_ROOT=$b3MidiRoot"
cmake --build build-native-midi --config Release --target hammond_standalone --parallel 3
.\build-native-midi\apps\standalone\Release\hammond_standalone.exe --help
```

Visual Studio, Xcode and other multi-configuration generators select the
configuration with `--config Release`; their executable path includes `Release/`.
Use `-C Release` with CTest. To build the standalone acceptance inputs and run
the existing native test group, use:

```sh
cmake --build build-native-midi --config Release \
  --target hammond_standalone_test_inputs --parallel 3
ctest --test-dir build-native-midi -C Release --output-on-failure \
  --no-tests=error -R '^test_standalone_'
```

The last block uses POSIX line continuations; in PowerShell put each command on
one line or use its backtick continuation. Building only `hammond_standalone`
does not build every acceptance executable.

For keyboard/pointer use and synthetic MIDI checks, configure a separate native
build with `-DHAMMOND_ENABLE_MIDI=OFF` and omit `HAMMOND_RTMIDI_ROOT` and RtMidi
acquisition. SDL is still required. That build accepts calibration settings and
synthetic replay, but cannot open a physical MIDI port. Enabling a backend alone
does not establish a working controller connection.

For an installed payload, substitute `bin/hammond_standalone` or
`bin/hammond_standalone.exe` in the commands below. Keep its companion payload
together as described in the [installation guide](STANDALONE_INSTALL.md).

## Choose a port and reproducible startup settings

Run `hammond_standalone --list-midi` using the actual executable path. Copy the
complete exact port name after its list index; the index is not a selection
token. No port is automatically selected, and duplicate exact names are refused.
Names can change when devices change. Choose three distinct wire channels from
1 through 16, matching the controller; defaults are **Upper 1 / Lower 2 /
Pedals 3**.

The following values are **illustrative**, not measured pedal endpoints. Replace
the port placeholder and use the endpoint/direction values appropriate to the
controller:

```sh
build-native-midi/apps/standalone/hammond_standalone \
  --midi-port "EXACT NAME FROM --list-midi" \
  --midi-upper-channel 1 --midi-lower-channel 2 --midi-pedal-channel 3 \
  --expression-min 20 --expression-max 100 --expression-invert \
  --state ./my-controls.b3controls --diagnostics ./my-session.json
```

Use a writable state path and a distinct diagnostics path. An existing valid
state file loads musical controls at startup; an absent state file starts the
proposed audition registration. Save is explicit. Audio initially requests SDL's
default output at 48 kHz with 512-frame buffers. Change it through **AUDIO /
Ctrl+,** if needed. The obtained buffer size is not a physical latency reading.

| CLI option | Meaning | Default |
| --- | --- | --- |
| `--expression-min N` | Lower raw CC11 endpoint, decimal integer 0–127. | `0` |
| `--expression-max N` | Upper raw CC11 endpoint, decimal integer 0–127. | `127` |
| `--expression-invert` | Reverse direction after endpoint saturation; this flag takes no value. | Normal when absent. |

The complete pair must satisfy **0 ≤ minimum < maximum ≤ 127**. There is no
automatic endpoint swapping. Missing, negative, fractional, overflowing or
trailing-text integers and repeated options, including a repeated invert flag,
are refused with exit **2**. Validation happens before SDL/device initialization
or output writes, even with no input selected. For example,
`--expression-min 100 --expression-max 20` is invalid.

## Understand endpoints and direction

Minimum and maximum mean the lower and upper **raw numbers**, not physical heel
and toe positions. In Normal direction, minimum becomes expression 0 and maximum
becomes expression 1. Values below or above that interval saturate at the
corresponding end. Inverted direction then replaces the result with `1 - result`.

```text
normal = clamp(raw - minimum, 0, maximum - minimum) / (maximum - minimum)
expression = inverted ? 1 - normal : normal
```

For the illustrative minimum **20**, maximum **100**:

| Raw CC11 | Normal expression | Inverted expression |
| ---: | ---: | ---: |
| 0, below minimum | 0 | 1 |
| 20, minimum | 0 | 1 |
| 40 | 0.25 | 0.75 |
| 60, midpoint | 0.5 | 0.5 |
| 100, maximum | 1 | 0 |
| 127, above maximum | 1 | 0 |

Expression is a normalized musical control, not a measured voltage or sound
pressure. Default 0/127/Normal gives exactly the previous `raw / 127.0` mapping.
Calibration affects only mapped CC11; it does not remap drawbar controllers,
notes or velocity. The app has no automatic learning, raw-message monitor,
response curve, smoothing or added dead-zone control. It does not measure a
physical pedal's travel.
The [endpoint contract](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/MIDI_EXPRESSION_CALIBRATION.md)
defines the exact mapping and its adapter boundary.

## Edit the MIDI dialog

Open **MIDI / Ctrl+M**; Command is also accepted. Opening the dialog releases
UI-held notes and suppresses still-down computer keys until their original
releases. Existing MIDI notes follow the connection lifecycle described below.
The dialog works at the 960×700 minimum window in both Dimensional and Flat.

Native discovery runs in the background. Wait for the current discovery result
before applying a physical port. **No input**, Apply for No input, Disconnect
and Close remain available while searching. Close and reopen for an explicit
refresh; there is no separate Refresh button or automatic port selection.

Tab/Shift+Tab wraps through **eleven focus stops**. Enter/Space activates the
focused control, and pointer clicks use the same displayed controls:

| Stop | Control | Operation |
| ---: | --- | --- |
| 1 | Previous port | Click/activate selects the previous entry. Arrows browse; Home/End select the first/last entry. |
| 2 | Next port | Click/activate selects the next entry; the same arrow and Home/End browsing applies. |
| 3 | Upper channel | Click/activate increments. Left/Down decrement; Right/Up increment. Values wrap at 1/16; Home/End choose 1/16. |
| 4 | Lower channel | Same channel operations. |
| 5 | Pedal channel | Same channel operations. |
| 6 | **EXPRESSION MIN** | Click/activate increments by one. Left/Down decrement; Right/Up increment. Values clamp at 0/127; Home/End choose 0/127. |
| 7 | **EXPRESSION MAX** | Same endpoint operations. |
| 8 | **EXPRESSION DIRECTION** | Click, Enter, Space or any arrow toggles Normal/Inverted. Home chooses Normal; End chooses Inverted. |
| 9 | **APPLY / CONNECT** | Validate and request the selected settings; keep the dialog open to show the result. |
| 10 | **DISCONNECT** | Retire MIDI input and release its note owners. |
| 11 | **CLOSE** | Close without applying outstanding edits. Escape also closes. |

Endpoint edits may temporarily make an invalid pair, so either value can be
entered first. The dialog displays an error and retains the staged values for
correction. Invalid Apply leaves configured settings, active routing and the
active connection unchanged. Closing leaves edits unapplied; opening again
copies the latest configured settings into the selection.

### Selected, configured, active and pending are different

| Term | What it tells you |
| --- | --- |
| **Selected** | Values currently staged in the dialog. They can be invalid or differ from the active connection. Editing alone does not configure MIDI. |
| **Configured** | Settings retained by the application for connection requests in this process, initially from CLI. They can exist with No input selected or after an open failure. They are not proof of an active input. |
| **Active calibration** | Values installed in the currently active decoder epoch. **None (inactive)** means no epoch is using them. |
| **Reconnect pending** | A copied port/channel/calibration request is waiting to open after the old MIDI releases have been acknowledged. It is not a successful connection. |

Read the actual status after Apply. A healthy active input with the **same exact
port, channel map and calibration** makes Apply a no-op: it preserves its epoch
and held MIDI notes. Changing any one of those settings performs this transition:

1. Stop the old input, join its backend callbacks and discard its retired inbox.
2. Release MIDI owners in all three divisions and wait for the Session's applied
   release acknowledgment or recovery barrier.
3. Open a fresh input epoch with the copied settings.

Packets from the old input are not reinterpreted with the new calibration.
Reconfiguration deliberately releases MIDI-held notes, so play fresh Note Ons
after reconnecting. Ordinary MIDI retirement itself preserves UI ownership,
musical controls, source phase and percussion history; opening the dialog has
the separate UI-release behavior already described.

**Apply sends no expression edit.** After a successful calibration change, the
current musical expression stays where it was until the next admitted CC11
uses the new mapping. CC121 or an ordinary expression edit/Load can also change
that musical value through their existing paths. Merely changing endpoints,
choosing No input, connecting or reconnecting does not move it.

Diagnostics written with `--diagnostics` expose these distinctions under
`midi.expression_calibration`: `model`, `configured`, `selected`, `selected_valid`,
nullable `active`, `reconnect_pending`, `release_pending` and nullable `pending`.
A pending object includes its exact port, channels, calibration and whether it
is synthetic. `pre_shutdown_active` retains the calibration observed before
cleanup; final `active` is normally `null` because shutdown retires the input.
Use that pre-shutdown field or the recorded replay/presentation observations
when checking what was active during a run.

## Channel-mode messages and ownership

This is a declared native subset, not complete MIDI/General MIDI conformance.
Only the three mapped wire channels act. Upper and Lower manual notes accept
MIDI pitches 36–96; Pedals accepts 36–60. Repeated Note Ons create separate
owners, and ordinary Note Off releases the oldest matching MIDI owner. Input
keeps arrival order; admitted commands apply at an audio callback boundary,
without turning MIDI receipt timestamps into sample offsets.

| Message on a mapped channel | Accepted value | Behavior |
| --- | --- | --- |
| **CC11, Expression** | 0–127 | Apply the active endpoint/direction mapping to the **single global expression**. A message from any mapped division affects the whole instrument. |
| **CC120, All Sound Off** | **0 only** | Retire the addressed division's MIDI owners. In this standalone's admitted ideal-contact model, their final-owner contributions are absent from the first rendered sample after application. Other owners remain. |
| **CC121, Reset All Controllers** | **0 only** | Reset the single declared expressive controller, global expression, to normalized **1.0**, bypassing endpoint calibration and inversion. Notes, calibration, routing and other settings remain. |
| **CC123, All Notes Off** | 0–127 | Release the addressed division's MIDI owners. The MIDI-defined value is 0; other values remain accepted as this receiver's compatibility extension. |

Nonzero CC120/121 values are counted as out of range and perform no action.
CC122 and CC124–127 remain unsupported; sustain CC64, bank/program changes,
pitch bend and pressure are also unmapped. CC121 does not reset drawbar banks,
fixed selections, percussion or pedal mixtures, and does not reload saved
controls. Its expression edit shares the normal pending/acknowledgment path,
preserving concurrent desired UI edits.

CC120 and CC123 act on MIDI ownership, not every owner of a pitch. A UI owner of
the same physical key can keep it sounding, and another division remains
unaffected. These messages leave the connection active and do not establish a
persistent mute; a fresh Note On can play. CC120's immediate-contribution promise
is specific to this ideal-contact standalone, not a guarantee for finite-travel
contacts, shared effect tails, a physical instrument or VST3 delivery. **PANIC**
has the separate global scope below. The
[channel-mode contract](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/MIDI_CHANNEL_MODE_CONTRACT.md)
defines the exact boundary.

## Save, disconnect and recover

Musical **expression is saved** with the other acknowledged controls in
`B3CONTROLS4`. Endpoint minimum/maximum/direction, MIDI port and wire-channel map
are **volatile adapter configuration**: Save/Load does not store or restore
them. There is no separate calibration preference file. Calibration remains
configured across ordinary MIDI reconnect and audio restart within the same
process. After quitting, supply the same CLI arguments to reproduce it; a
launch without them uses 0/127/Normal.

| Situation | Result and next action |
| --- | --- |
| Apply fails validation | Correct the selected endpoints or repeated channels, then Apply. The prior configuration/epoch remains. |
| A requested open fails | The input is inactive; the attempted configuration may remain configured, but it is not active. Resolve the port/backend problem and explicitly Apply again. The consumed request is not automatically retried. |
| **No input** and Apply | Retain valid configured channels/calibration without opening an input; retire any old MIDI epoch. |
| Ordinary **Disconnect** | Stop input, discard queued bytes and release MIDI owners. It does not reset musical expression or calibration. Reconnect explicitly and send fresh notes. |
| Port disappearance or backend/inbox fault | Retire the old epoch and its MIDI owners. Resolve the cause, close/reopen MIDI for discovery if needed, and Apply explicitly. |
| Audio Apply/restart or audio failure | Restart working audio first, then Apply MIDI again. Acknowledged controls and configured calibration remain, while the audio restart clears notes and resets the audio lifecycle/source phase. |
| **PANIC** | Release every note owner, including UI and MIDI, and retire MIDI admission. Apply MIDI explicitly when ready; old queued notes cannot undo Panic. |
| Session emergency recovery | The existing global recovery may release UI owners too. Resolve the visible recovery state before explicitly reconnecting. |
| MIDI shutdown cannot establish callback quiescence | Restart the application before another MIDI open. This is different from an ordinary successful Disconnect. |

There is no automatic reconnect or replay of previously held notes. Discovery
errors remain in diagnostics after recovery. On Linux, dummy SDL drivers do not
create ALSA sequencer access; native enumeration can still fail. A MIDI-disabled
build reports backend unavailability. Neither state means that a physical input
connected successfully.

## Bounded reproduction without physical MIDI

This example works with either native build above, including MIDI disabled.
Create a fresh writable `out/expression-example` directory and save this exact
text as `out/expression-example/expression.b3midi`:

```text
B3MIDIREPLAY1
duration_ms 800
0 connect
100 bytes 90 3C 64
200 bytes B0 0B 28
500 bytes 80 3C 00
```

The byte pairs are hexadecimal: `28` is raw CC11 **40**. The script connects
synthetic input, holds Upper note 60, sets expression and releases the note.
Start with an absent `unused.b3controls` file:

```sh
SDL_AUDIODRIVER=dummy SDL_VIDEODRIVER=dummy \
  build-native-midi/apps/standalone/hammond_standalone \
  --state out/expression-example/unused.b3controls \
  --midi-script out/expression-example/expression.b3midi \
  --expression-min 20 --expression-max 100 --expression-invert \
  --diagnostics out/expression-example/inverted.json
```

In PowerShell, set `$env:SDL_AUDIODRIVER = "dummy"` and
`$env:SDL_VIDEODRIVER = "dummy"`, then run the arguments on one line using the
Windows executable path. Clear those environment overrides before a later
physical audio/display run. No native MIDI enumeration or device open occurs
in this synthetic mode.

Expected exit is **0**, with these diagnostics:

| Field | Expected |
| --- | --- |
| `schema_version`, `midi.source` | `3`, `synthetic-replay` |
| `midi_replay.completed`, `.delivered`, `.passed`, `.final_acknowledged` | All `true` |
| `midi_replay.before_shutdown.controls.expression` | **0.75** |
| `midi_replay.before_shutdown.manual_notes`, `.pedal_ids` | `[[], []]`, `[]` |
| `midi.expression_calibration.configured`, `.pre_shutdown_active` | `{"minimum":20,"maximum":100,"inverted":true}` |
| `midi.expression_calibration.active` | `null` after shutdown |
| `midi.generation`, `midi.device.callback_messages` | `0`, `0`; native transport was unopened. |
| `errors.count`, `session.held_after_shutdown` | `0`, `false` |

Omit `--expression-invert` and choose a fresh diagnostics filename to obtain
**0.25** instead. To check controller reset, insert `400 bytes B2 79 00` before
the note-off line in a new script. This sends CC121 value 0 on mapped Pedal
channel 3; the final global expression is **1.0** even with inversion enabled,
and the configured calibration is unchanged.

Replay starts disconnected, and each script `connect` starts a fresh epoch with
the CLI configuration. Valid modal Apply during replay reports that the script
controls connection changes and leaves its configured routing/calibration
unchanged; invalid selected settings still report their validation error first.
Modal Disconnect works, and only a later script `connect` can reopen the input.
`--midi-script` excludes `--midi-port`, `--list-midi` and `--smoke-ms`; a paired
`--input-script` must have the same duration. Script timing is wall-clock input
scheduling, not sample-accurate automation or a latency measurement. The
[replay contract](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/MIDI_REPLAY.md)
specifies its bounded format and completion drain.

### Executed evidence and limits

The three 800 ms examples above were checked with dummy SDL and the existing
Linux executable SHA-256
`7ded143b676e9d51a29549dae12184763042a1f12192f72802db7927fa707852`;
all passed with final expression 0.25, 0.75 and 1.0 respectively. The
[A32 note](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/development/2026-11-15-product-continuation/notes/A32-midi-operating-guide.md)
records the source identity, parser checks and scope. These were existing-binary
checks; the platform build recipes were checked against repository instructions,
not rerun as part of this guide.

Broader executed coverage is retained in
[A24's native CLI/replay acceptance](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/development/2026-11-15-product-continuation/notes/A24-native-midi-acceptance.md)
and [A26's real-main lifecycle fixture](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/development/2026-11-15-product-continuation/notes/A26-native-calibration-lifecycle.md).
The maintained
[CLI suite](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/apps/standalone/native_tests/test_standalone_midi_cli.py),
[MIDI replay suite](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/apps/standalone/native_tests/test_standalone_midi_replay.py)
and [native calibration suite](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/apps/standalone/native_tests/test_standalone_native_calibration.py)
cover modal input, channel modes and epoch transitions. A26 uses a test-only
RtMidi facade with real application code and SDL dummy callbacks; it is not a
physical pedal test. Hardware MIDI/audio, OS callback concurrency, actual pedal
endpoints, callback deadlines, physical latency and measured organ fidelity
remain unqualified by these examples and fixtures.
