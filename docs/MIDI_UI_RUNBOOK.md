# MIDI and reference interface runbook

The optional native application plays the existing **nominal dry organ** through
SDL2. Optional RtMidi input controls that same engine. The reference-oriented
view adds dynamic player controls and decorative source art; it does not add
scanner, AO-28 or Leslie sound. The current instrument has 47 public parameter
identities and a `B3CONTROLS4` writer, with readers for versions 1–3. The first
45 parameter records retain their meanings.

This guide covers source setup, installed use, connection, recovery and bounded
engineering checks. The [interface guide](INTERFACE_RUNBOOK.md) covers current
Play/Rotary/Service, Flat and background MIDI discovery; the
[preset guide](PRESET_RUNBOOK.md) covers fixed registrations and saved controls.
The sibling [application guide](STANDALONE_APP.md),
[model guide](STANDALONE_MODEL.md) and [installation guide](STANDALONE_INSTALL.md)
provide the complete application, musical and staging contracts. Links to other
project documents use the canonical repository URL so installed copies remain
navigable without a source checkout. Those external links require network access.

## Prerequisites and platform backends

Source builds require **CMake 3.21+**, **Python 3.10+**, Git and a C++20 compiler.
Enabling the SDL application also requires a C compiler. The examples below use
a POSIX shell from the repository root. Windows uses `.exe` and, with the
project's Visual Studio 17 2022 x64 generator, places the selected executable in
`apps/standalone/Release/` beneath the build directory. Use the same
`--config Release` for building and staging. Python may be named `python` there.

| Platform | Native MIDI API selected by this project | Required native inputs |
| --- | --- | --- |
| Linux, excluding Android | ALSA | ALSA development headers/library and threads; usable ALSA sequencer access at runtime. SDL additionally needs the development packages for the desired desktop/audio drivers. |
| Windows desktop | WinMM | Windows SDK and `winmm`; the project's native CI uses the Visual Studio 17 2022 x64 toolchain. |
| macOS | CoreMIDI | Apple toolchain/SDK with CoreServices, CoreAudio, CoreMIDI and CoreFoundation; the project's native CI uses Clang. |

The [project native workflow](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/.github/workflows/standalone.yml)
provides this Ubuntu desktop/audio development-package setup, selected from the
locked SDL source's Linux instructions:

```sh
sudo apt-get update
sudo apt-get install --no-install-recommends -y \
  pkg-config libasound2-dev libpulse-dev libx11-dev libxext-dev \
  libxrandr-dev libxcursor-dev libxfixes-dev libxi-dev libxss-dev
```

Use the appropriate package manager and platform development environment for
other systems. A compiled ALSA backend does not prove `/dev/snd/seq` exists or
that the process can access it. The
[RtMidi build module](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/cmake/VerifyRtMidi.cmake)
selects only the API listed above; missing required dependencies and unsupported
enabled targets fail configuration. It does not choose JACK, a dummy MIDI API,
an alternate input or an application-created virtual port.

The inspected local Linux candidate used CMake 4.4.4, GCC 14.2 and a separately
provided ALSA development sysroot. Its `SDL_ALSA=OFF` setting was an explicit
local SDL/header compatibility workaround. It is **not** the normal setup recipe
or a recommendation to disable real platform backends. Retain the generated
SDL backend inventory and actual runtime driver names for the artifact being
tested. Native MIDI and SDL audio are separate dependencies and capabilities.

## Build from source

### Ordinary SDK-free build

The ordinary configuration acquires no SDL2, RtMidi or VST3 SDK and builds no
native window:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release --parallel 3
```

### SDL application without physical MIDI

Acquire the reviewed **SDL2 2.32.10** source into a new path outside this source
tree. The destination's parent must already exist; the destination itself must
not exist. If it was already acquired, run only the verification command:

```sh
python3 tools/acquire_sdl2.py --destination ../SDL2
python3 tools/acquire_sdl2.py --verify-existing ../SDL2
cmake -S . -B build-native -DCMAKE_BUILD_TYPE=Release \
  -DHAMMOND_BUILD_STANDALONE=ON \
  -DHAMMOND_SDL2_ROOT="$PWD/../SDL2"
cmake --build build-native --config Release --target hammond_standalone --parallel 3
build-native/apps/standalone/hammond_standalone --help
```

Physical MIDI remains disabled. Keyboard/pointer operation and synthetic MIDI
replay are available. `--list-midi` reports backend unavailability and returns 1.
The [SDL dependency contract](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/STANDALONE_DEPENDENCY.md)
retains the exact commit, cleanliness requirements, notices and backend limits.

### Add explicitly enabled RtMidi

Acquire the reviewed **RtMidi 6.0.0** checkout separately. Its verifier checks the
locked commit, tag, source and license; it never upgrades or repairs the source:

```sh
python3 tools/acquire_rtmidi.py --destination ../rtmidi-6.0.0
python3 tools/acquire_rtmidi.py --verify-existing ../rtmidi-6.0.0
cmake -S . -B build-native-midi -DCMAKE_BUILD_TYPE=Release \
  -DHAMMOND_BUILD_STANDALONE=ON \
  -DHAMMOND_SDL2_ROOT="$PWD/../SDL2" \
  -DHAMMOND_ENABLE_MIDI=ON \
  -DHAMMOND_RTMIDI_ROOT="$PWD/../rtmidi-6.0.0"
cmake --build build-native-midi --config Release --target hammond_standalone --parallel 3
build-native-midi/apps/standalone/hammond_standalone --help
```

Only `--destination` performs network acquisition. CMake invokes offline
verification and prepares its separately identified RtMidi build copy, including
the reviewed CoreMIDI initialization correction. Keep the original checkouts
clean and build outside them. Do not edit dependency source or substitute a new
release to make verification pass. The
[RtMidi dependency contract](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/RTMIDI_BUILD.md)
records the correction, exact hashes and selected system libraries.

The following commands assume the MIDI-enabled single-configuration executable.
For SDL-only, installed or multi-configuration use, substitute the actual path.

## First launch and explicit connection

List audio and MIDI separately. `--list-midi` does not initialize SDL:

```sh
build-native-midi/apps/standalone/hammond_standalone --list-audio
build-native-midi/apps/standalone/hammond_standalone --list-midi
build-native-midi/apps/standalone/hammond_standalone
```

No MIDI input is selected by default, even when the backend is compiled. Copy
the complete name printed after the list index; the index itself is not the
selection token. Replace the placeholder below with that exact name:

```sh
build-native-midi/apps/standalone/hammond_standalone \
  --midi-port "EXACT NAME FROM --list-midi" \
  --midi-upper-channel 1 --midi-lower-channel 2 --midi-pedal-channel 3 \
  --state ./my-controls.b3controls --diagnostics ./my-session.json
```

Names may change after device topology changes and are not permanent hardware
identities. Duplicate exact names are ambiguous and rejected. There is no
default port-zero selection or fallback. Use three **distinct channels from 1
through 16**, matching the controller's transmitted channels. Defaults are upper
1, lower 2 and pedals 3. These wire channels are independent of the internal
UI/MIDI ownership namespaces and are not saved in a musical control file.

The application opens SDL's default output unless `--device "EXACT AUDIO NAME"`
is supplied. Supported rates are 44100, 48000 and 96000 Hz; supported buffers
are 128, 256, 512, 1024 and 2048 frames. Defaults are 48000 Hz and 512 frames.
Use **AUDIO** or **Ctrl+,** to change them. The displayed obtained configuration
is not a measurement of physical latency.

### MIDI dialog by keyboard or pointer

Select **MIDI** or press **Ctrl+M**; Command is also accepted for Ctrl. Opening
the modal starts background discovery; completed results list native ports
after **No input**. While searching, No input/Apply, Disconnect and Close remain
available. Applying a physical port requires the current discovery to finish.
Tab/Shift+Tab cycles these eight controls, with wraparound:

| Focus order | Control and action |
| ---: | --- |
| 1–2 | Previous/next exact port. Arrow keys browse; Home/End choose the first/last entry. |
| 3–5 | Upper/lower/pedal wire channel. Arrows adjust, Home selects 1, End selects 16. |
| 6 | **APPLY / CONNECT** validates all staged choices and requests a connection. |
| 7 | **DISCONNECT** retires MIDI input and releases its notes. |
| 8 | **CLOSE** closes the dialog. |

Enter/Space activates the focused control; clicking uses the same controls.
Clicking a channel advances its value. Left/Down decrement, Right/Up increment,
and channel values wrap at 1/16. Escape or Close discards unapplied choices;
Apply leaves the dialog open so its result can be inspected. Duplicate channels
reject without replacing active routing or losing the staged choices needed to
correct the error. Audio must be running before Apply can open an input.

There is currently no separate Refresh button: close and reopen the dialog to
enumerate again. Long names may be elided and the embedded font has limited
character coverage; `--list-midi` provides the exact emitted name. Successful
empty enumeration is distinct from an API/permission failure. A backend error
is shown as an error, not as an empty device list or successful connection.

## Playing, editing and the complete controller map

The two manuals retain **61 keys each, MIDI 36–96 inclusive**. The **25 pedals
accept MIDI 36–60**, translated internally to pedal IDs 1–25. Other pitches and
unselected wire channels are counted and ignored. The adapter adds no
transposition or pitch clamping.

| MIDI message on a mapped channel | Behavior |
| --- | --- |
| Note On, velocity 1–127 | Adds one note owner for that division. Velocity uses the existing organ gesture contract, without piano-like sustained gain. |
| Note On velocity 0, or Note Off | Releases the oldest matching MIDI owner. Repeated Note Ons need corresponding releases. |
| CC11, value 0–127 | Edits the single shared nominal expression using `value / 127.0`, from any mapped division. |
| Upper CC16–24 | Edits the nine retained upper **B** drawbars in footage order. |
| Lower CC16–24 | Edits the nine retained lower **B** drawbars in footage order. |
| Pedal CC16/17 | Edits nominal **Mix 1 / Mix 2**; pedal CC18–24 has no mapping. |
| CC123, any value 0–127 | Ordinary All Notes Off scoped to this division's MIDI owners; it does not release UI or another division's owners. |

Manual drawbar order is **16′, 5⅓′, 8′, 4′, 2⅔′, 2′, 1⅗′, 1⅓′, 1′**.
CC values pass through `value / 127.0` and the existing parameter bridge's
discrete 0–8 conversion. The adapter adds no alternate rounding law. CC123 is
a musical release, not immediate physical sound suppression or global Panic.

**Unsupported:** sustain CC64, All Sound Off CC120, Reset Controllers CC121,
bank/program changes, pitch bend, channel/polyphonic pressure, every other
controller, SysEx, system/common/realtime and active sensing. No unsupported
message recalls a registration, changes tuning, extends sustain or provides a
disconnect heartbeat. The backend supplies complete short messages; the
adapter does not reconstruct a running-status byte stream. The exact
[MIDI input contract](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/MIDI_INPUT.md)
defines decoding, timing, counters and owner limits.

**EDIT A/B** selects the retained bank displayed by the drawbar editors.
Preset **A#** sounds adjustable bank A and preset **B** sounds bank B; either
reconnects that manual and clears fixed mode. Preset **C#–A** selects one of nine
fixed rows for that manual, preserving both adjustable banks. Preset **C**
cancels the route while preserving held keys and stored bank/fixed memory.
MIDI drawbars always edit B: they neither select B, change A, leave fixed mode
nor reopen Cancel. Choose preset B explicitly to hear those edited B values.
MIDI and local edits share the desired control state and its pending/dirty
indicators.

For computer-key playing, use `A W S E D F T G Y H U J K O L P ;`, F1/F2/F3 for
upper/lower/pedals, and `[`/`]` for octave. Tab/Shift+Tab changes focus; arrows,
Home/End adjust controls or the focused playing key; Space holds that key.
Pointer keys and drawbars remain live. Escape and focus loss release UI notes.
Opening Help, Audio or MIDI also releases UI holds; these ordinary view actions
leave external MIDI ownership active.

**Save** or Ctrl+S explicitly writes acknowledged musical controls. Ctrl+O loads
the selected control file. Exit never saves automatically. `B3CONTROLS4` stores
the four drawbar banks, remembered banks, raw fixed choices, route bits,
expression, percussion and pedal mixtures, with the pinned registration catalog
identity. Readers 1–3 remain supported and migrate fixed modes to None; the
next explicit Save writes version 4. It does not store held notes, source
phases, transient envelopes, MIDI port/channels, audio settings, window geometry,
workspace, Flat presentation or focus. An absent selected state file gives the
proposed upper B `888000000`, lower B `008000000`, pedals `80`; this is an audition
choice, not a factory preset.

### Reference view and sound boundaries

The window starts at 1280 × 900 logical units, resizes down to 960 × 700 and
limits each dimension to 8192. At widths of at least 1400, a right-hand cabinet
composition appears. Walnut/charcoal/brass styling follows the generated design
concept on the supplied atlas cover/page 409, whose
[source identity](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/design/atlas-reference.json)
is retained. Only admitted wood/cabinet crops are decorative. The actual manuals,
pedals, drawbars, status, focus and bank selections remain live application
controls, with corrected key counts and legends.

The cabinet is an illustration with an explicit unavailable-sound status; it
does not provide rotary speed, scanner or microphone processing. The existing
nominal core still produces identical left/right dry audio. The
[earlier independent visual review](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/reviews/MIDI_UI_REFERENCE_REVIEW.md)
retains its source-specific screenshots, differences and original thin-glyph
finding. The [current interface status](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/STATUS.md)
records subsequent glyph, scale and preset-label repairs with their evidence. Concept pixels are not an
application screenshot, and this view does not establish one-to-one appearance
or measured instrument sound.

## Recovery and reconnect

| Situation | Result and next action |
| --- | --- |
| Normal MIDI Disconnect, missing port or backend/inbox fault | Retire the input epoch, discard old packets and release MIDI-owned notes. Wait for the release acknowledgment; resolve the device problem, reopen MIDI settings, select the current exact name and Apply. |
| **PANIC** | Globally release notes and retire MIDI so old queued Note Ons cannot undo Panic. Explicitly Apply to reconnect when ready. |
| Audio Apply/Restart, output removal or audio failure | Retire MIDI; restart working audio first, then explicitly Apply MIDI. Acknowledged controls survive an audio restart, while notes and transient DSP history reset. |
| Session queue recovery | Existing global emergency recovery may release UI notes as well. Resolve the visible recovery state, then explicitly Apply MIDI; no failed batch is retried. |
| MIDI shutdown cannot establish callback quiescence | The device is unavailable for further opens; restart the application. Do not treat this as an ordinary successful Disconnect. |
| No Audio | Use Audio settings for an explicit working output retry. Musical commands do not accumulate in a stopped Session. There is no automatic dummy-driver fallback. |

Normal scoped MIDI retirement preserves UI holds and musical controls. The
global Panic/Session emergency paths have the broader scope described above.
Reconnection starts an empty epoch: **no automatic reconnect and no resurrection
of old held notes**. Fresh physical Note Ons are required. Ordinary CC123 does
not retire the whole device, and ordinary Escape is not a global external-note
release. Saving/loading or changing the edited bank does not reconnect MIDI.

Device disappearance is best-effort detection, including periodic native state
and name checks. It cannot guarantee detection of a same-name replacement or an
unplug/replug between observations. Read the
[backend lifetime contract](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/MIDI_BACKEND.md)
before making physical hotplug or timing claims.

## Bounded checks without hardware

Choose fresh regular paths in an existing writable working directory. State,
both script inputs, screenshot and diagnostics must be distinct, including
existing hardlink aliases. Symlink leaves and special files are rejected.
Parsing and path admission precede audio activation and output writes.

### SDL smoke

```sh
SDL_AUDIODRIVER=dummy SDL_VIDEODRIVER=dummy \
  build-native-midi/apps/standalone/hammond_standalone \
  --state ./smoke-unused.b3controls --smoke-ms 600 \
  --diagnostics ./smoke.json
```

Use an absent state file for the proposed registration. Success exits **0** and
prints `Native SDL smoke passed` with actual counters. Diagnostics have
`schema_version: 3`, `smoke.passed: true`, positive audio callback/frame counts,
`errors.count: 0` and `session.held_after_shutdown: false`. Without a requested
MIDI input, `midi.source` is `none`. Optional `--screenshot ./smoke.bmp` captures
an actual rendered held-key frame; a screenshot failure or missing required
held frame fails smoke. The duration bounds event-loop time, with setup,
shutdown and file I/O additional.

Dummy audio/video tests real application handlers and callbacks without
audible hardware output or physical MIDI. They do not measure latency,
underruns, native screen-reader access or acoustic fidelity.

### Synthetic MIDI example

Save this complete text as `example.b3midi` in the repository root:

```text
B3MIDIREPLAY1
duration_ms 1200
0 connect
100 bytes 90 3C 64
100 bytes 91 40 64
100 bytes 92 24 64
300 bytes B0 0B 40
600 bytes 80 3C 00
600 bytes 81 40 00
600 bytes 82 24 00
800 disconnect
```

It explicitly connects, plays upper 60/lower 64/pedal 36 on the default channels,
sets shared expression to 64/127, releases those notes and disconnects. Run:

```sh
SDL_AUDIODRIVER=dummy SDL_VIDEODRIVER=dummy \
  build-native-midi/apps/standalone/hammond_standalone \
  --state ./replay-unused.b3controls --midi-script ./example.b3midi \
  --diagnostics ./example-midi.json
```

This also works in the SDL-only build. Replay starts disconnected; bytes before
`connect` are counted and dropped. It never enumerates or opens hardware. Success
exits **0**, and a replay need not print a success line. Inspect the JSON:

| Field | Expected for this example |
| --- | --- |
| `schema_version` / `midi.source` | `3` / `synthetic-replay` |
| `midi_replay.completed`, `.delivered`, `.passed`, `.final_acknowledged` | All `true` |
| `midi_replay.scheduled_events` / `.delivered_events` | `9` / `9` |
| `midi_replay.scheduled_packets` / `.accepted_packets` / `.dropped_packets` | `7` / `7` / `0` |
| `midi_replay.connections_started` / `.disconnect_events` | `1` / `1` |
| `midi_replay.accepted_note_on_commands` / `.accepted_note_off_commands` | `3` / `3` |
| `midi_replay.before_shutdown.manual_notes` / `.pedal_ids` | `[[], []]` / `[]` |
| `midi_replay.before_shutdown.controls.expression` | `64 / 127` (about `0.503937`) |
| `midi.generation` / `midi.device.callback_messages` | `0` / `0`, because no native device opened |
| `errors.count` / `session.held_after_shutdown` | `0` / `false` |

The format admits 0–2048 events, a 250–10000 ms duration and at most 65536 input
bytes. Times are nondecreasing and strictly below the declared duration; each
`bytes` record holds 1–3 exact hexadecimal byte pairs. The runtime offers at
most 512 due records and drains at most 32 MIDI packets per main-loop turn.
Receipt timestamps and scheduled milliseconds do not become sample offsets.
Completion requires delivery, declared duration, an empty inbox, resolved
retirement and final Session/control acknowledgment, with a further bounded
two-second drain. The
[full replay contract](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/MIDI_REPLAY.md)
defines fault injection and all parsing limits.

`--midi-script` excludes `--midi-port`, `--list-midi` and `--smoke-ms`.
A paired `--input-script` must declare the same duration; each stream retains its
own order, without a sample-accurate ordering promise across streams. In this
mode modal Apply leaves script routing unchanged; only a later script `connect`
opens a synthetic epoch. Modal Disconnect still retires it. Current standalone
UI fixtures live under
[`examples/standalone-input-v2/`](https://github.com/tomasedisonn80/Hammond-B3-Organ/tree/main/examples/standalone-input-v2)
and still use `B3UIREPLAY1`; the original directory is retained historical input.

### Exit status and expected failures

| Outcome | Exit status |
| --- | ---: |
| Successful help, enumeration (including an empty list), smoke or replay | 0 |
| Failed CLI enumeration or requested startup MIDI open, invalid script/path, unequal paired durations or failed/incomplete bounded run | 1 |
| Unknown/duplicate option, malformed/out-of-range integer, duplicate wire channels or mutually exclusive CLI options | 2 |

For example, `--midi-upper-channel 2` conflicts with the default lower channel
and returns 2. `--midi-script ./example.b3midi --smoke-ms 600` also returns 2.
On the inspected local Linux environment, `--list-midi` printed `MIDI backend:
ALSA` and returned 1 because `/dev/snd/seq` was absent. That is a real native
enumeration failure, not a successful zero-port run. Earlier modal acceptance
correctly expects the same environment error; synthetic replay remains a
separate path. Resolve device/driver access before using a physical controller.
An interactive dialog may show a recoverable error without exiting the app;
inspect `errors.count`, the status and the device state in its final diagnostics.

## Installed use and operational handoff

The explicit `Standalone` component stages the selected built executable:

```sh
cmake --install build-native-midi --config Release --component Standalone \
  --prefix /absolute/path/to/new-stage
/absolute/path/to/new-stage/bin/hammond_standalone --help
/absolute/path/to/new-stage/bin/hammond_standalone --list-midi
```

Use a fresh destination. Ordinary installation continues to select OfflineTools.
The executable embeds its nominal profile, glyphs and admitted reference art;
running it does not require Python, the source checkout or dependency sources.
Platform runtime libraries/drivers are still required. The sibling
[installation guide](STANDALONE_INSTALL.md) owns the exact enabled/disabled
payload, source/notice verification, overwrite preflight and relocation checks.
Its `standalone-capabilities.json` records compile-time capability and source
identities, not an observed hardware connection. Preserve the supplied guides,
locks, source manifests and notices with the executable. Local staging is not a
signed installer or release-distribution qualification.

An operational handoff should retain the exact revision or frozen source tree,
executable hash, toolchain, dependency identities, compiled backend inventory,
OS, command, exit status and copied diagnostics. For a physical run, also record
the actual controller/audio device, transmitted channels, exact enumerated port,
observed sustained-note and reconnect behavior, and measurement method for any
timing claim. Keep an original failure alongside its repair evidence. Refer to
the [current interface session](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/development/2026-11-14-interface-continuation/README.md)
and [status](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/STATUS.md)
for completed versus pending work; this guide does not certify all sixty
assignments, a new hosted CI run or a new physical device.

Literal equality with the reference remains open. Hosted platform results and
visual repairs qualify only their named source revisions; consult current status
for the latest observed results. Physical MIDI/audio, native accessibility,
scanner G5, connected AO-28/Leslie models and measured acoustic fidelity retain
their own gates. See the [model guide](STANDALONE_MODEL.md) before interpreting the
decorative cabinet or an engineering test as evidence of those features.
