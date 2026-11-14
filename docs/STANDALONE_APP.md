# Native standalone application

`hammond_standalone` is an optional SDL2 instrument around the existing nominal
dry Engine, with optional explicitly enabled RtMidi input. The
[interface runbook](INTERFACE_RUNBOOK.md) gives current Play/Rotary/Service,
Flat, focus and read-only inspection workflows. The
[preset runbook](PRESET_RUNBOOK.md) gives build, registration and state procedures,
and the [MIDI/UI runbook](MIDI_UI_RUNBOOK.md) retains the controller map,
platform prerequisites and bounded replay procedure. The sibling
[installation guide](STANDALONE_INSTALL.md) and [model guide](STANDALONE_MODEL.md)
describe relocation and musical limits. The application entry point is
[`main.cpp`](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/apps/standalone/main.cpp); its audio, UI and file boundaries are
[`Session`](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/STANDALONE_SESSION.md), [`AudioDevice`](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/STANDALONE_AUDIO.md),
[`UiModel`](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/STANDALONE_UI.md), and the existing
[`B3CONTROLS` format](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/CONTROL_STATE_FORMAT.md). Scanner, AO-28, Leslie, physical
expression, hardware latency and native accessibility remain separate gates.

## Build and launch

The ordinary SDK-free build remains available. Acquire and verify the exact
external SDL2 source using [the dependency instructions](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/STANDALONE_DEPENDENCY.md),
then configure from the repository root:

```sh
cmake -S . -B build-native -DCMAKE_BUILD_TYPE=Release \
  -DHAMMOND_BUILD_STANDALONE=ON -DHAMMOND_SDL2_ROOT=/absolute/path/to/SDL2
cmake --build build-native --config Release --target hammond_standalone --parallel 3
build-native/apps/standalone/hammond_standalone --help
build-native/apps/standalone/hammond_standalone --list-audio
build-native/apps/standalone/hammond_standalone
```

The executable paths above use a single-configuration generator. For a
multi-configuration generator, use `apps/standalone/Release/` beneath the build
directory; Windows also adds the `.exe` suffix.

Physical MIDI is independently **OFF by default**. After explicit acquisition
and verification of the pinned RtMidi 6.0.0 checkout, add
`-DHAMMOND_ENABLE_MIDI=ON -DHAMMOND_RTMIDI_ROOT=/absolute/path/to/rtmidi-6.0.0`
to the native configure command. CMake verifies the local source and prepares
the reviewed copy; it does not download dependencies. The
[runbook prerequisites](MIDI_UI_RUNBOOK.md#prerequisites-and-platform-backends)
identify the selected native APIs and platform requirements. The SDL-only app
still supports keyboard/pointer playing and synthetic MIDI replay.

The native target embeds the same compiled nominal profile. The generated
header retains the historical `hammond::vst3::kEmbeddedProfileText` namespace;
loading it through `load_runtime_profile(std::istream&, ...)` requires no VST3
SDK. The native text uses the [embedded font atlases](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/STANDALONE_FONTS.md).

| Option | Exact behavior |
| --- | --- |
| `--help` | Prints usage without initializing SDL. |
| `--list-audio` | Initializes the selected SDL audio driver, prints its actual output names, and exits without a window. |
| `--list-midi` | Prints the compiled MIDI backend and exact input names without initializing SDL. Enumeration failure or a disabled backend returns 1. A successful empty list returns 0. Mutually exclusive with `--list-audio`. |
| `--midi-port NAME` | Requests one exact, unambiguous input name. Omission selects no MIDI input. Startup open failure returns 1. |
| `--midi-upper-channel N`, `--midi-lower-channel N`, `--midi-pedal-channel N` | Select distinct one-based wire channels 1–16; defaults are upper 1, lower 2 and pedals 3. |
| `--device NAME` | Requests that exact output name. Omission selects SDL's default output. |
| `--sample-rate N` | Accepts 44100, 48000, or 96000; default 48000 Hz. |
| `--buffer-frames N` | Accepts 128, 256, 512, 1024, or 2048; default 512. |
| `--state PATH` | Selects the musical file used at startup and by Save/Load. |
| `--width N` | Initial logical width, 960 through 8192; default 1280. |
| `--height N` | Initial logical height, 700 through 8192; default 900. |
| `--workspace NAME` | Initial `play`, `rotary` or `service` workspace; default `play`. This is transient presentation state. |
| `--flat` | Start in Flat presentation; default is dimensional. Musical controls are unchanged. |
| `--smoke-ms N` | Runs the actual window and device for a bounded 250 through 10000 ms smoke interval. |
| `--input-script PATH` | Reads a bounded `B3UIREPLAY1` event script, runs the ordinary application handlers and stops after delivery, duration and command acknowledgment. Mutually exclusive with `--smoke-ms`. |
| `--midi-script PATH` | Reads bounded synthetic `B3MIDIREPLAY1` input. Starts disconnected and never opens a native MIDI device. Excludes `--midi-port`, `--list-midi` and `--smoke-ms`; paired UI/MIDI scripts require equal declared durations. |
| `--screenshot PATH` | Writes one BMP from the rendered backbuffer before `SDL_RenderPresent`. |
| `--diagnostics PATH` | Writes copied JSON diagnostics after joining and closing the device. |

Options with values require separate arguments; unknown options, duplicates,
partial integers and out-of-range values return 2. Fatal startup/shutdown and
requested smoke/replay failures return 1. Interactive dialogs can retain a
visible recoverable error without terminating the process; inspect the copied
diagnostic error count as well as the eventual exit status.
State, both script inputs and requested output files must be distinct. An ordinary interactive run
writes requested diagnostics when it closes. A screenshot without smoke is
taken from its first complete frame; it does not close the application.
With an input script, capture occurs at successful replay completion before
automatic shutdown cleanup, so a deliberately held final note can be shown.

## Scripted interaction and observations

The [input format](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/STANDALONE_INPUT_REPLAY.md) admits at most 256 ordered actions
and a declared duration from 250 to 10000 milliseconds. Parsing completes before
state-directory selection, audio opening or output writes. Missing or malformed
input returns 1; combining replay with smoke returns 2. Script input participates
in the same alias preflight as state, screenshot and diagnostics. A replay
injects its own events and never adds the automatic smoke note.

Events enter the actual SDL queue and ordinary keyboard/pointer/modal handlers.
Consumed-prefix markers preserve geometry ordering around real window resizes;
each main-loop poll remains bounded to 256 events. The final marker establishes
queue delivery. Successful completion also requires the declared wall time,
coherent acknowledgment of all accepted commands, completed Save, a running
device and fault-free joined shutdown. A two-second bounded drain follows the
declared duration; interruption or a missed gate returns 1.

Only a requested UI script adds a `replay` object to schema-3 diagnostics. It retains
delivery/completion, accepted note-command counts, successful device starts, the
last submitted sequence, the snapshot before shutdown and up to 512 changed
musical observations with elapsed wall time. Each observation contains absolute
manual MIDI notes, one-based pedal IDs, copied controls and sequence markers.
Preparation defaults are excluded until the explicit startup/reopen control
restore has been acknowledged. Observation overflow fails the run visibly.
These observations can miss short states between reads and do not measure
sample-accurate input latency or audibility. Accepted posts and observed holds
remain distinct facts.

Synthetic MIDI uses the separate
[`B3MIDIREPLAY1` format](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/MIDI_REPLAY.md), at most 2048 records and a
250–10000 ms duration. `connect`, `disconnect`, raw `bytes` and `fault backend`
records exercise the ordinary inbox, decoder, control bridge and retirement
path without a physical MIDI callback. The main loop offers at most 512 due
records and drains at most 32 packets per turn. An optional `midi_replay`
diagnostics object records delivery, packet dispositions, explicit epochs,
faults, final acknowledgment and the musical snapshot before shutdown. MIDI
replay expands the shared observation bound to 8704; UI-only replay keeps 512.
Successful completion additionally requires an empty inbox and no pending
connection or retirement. The runbook includes a complete bounded example and
its expected counters. Script milliseconds and receipt nanoseconds are not
sample offsets or measured controller latency.

A held final script state is legal. The pre-shutdown snapshot and accepted-note
counts are frozen before automatic close cleanup; final top-level Session data
describe joined shutdown with all notes released. An immediately queued scoped
cleanup command may be discarded by `Session::stop`; that lifecycle count is
not itself a lost scripted note. The [independent workflows](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/STANDALONE_WORKFLOWS.md)
check the original note identity, modal release, Save/Load, selected versus
edited banks, Cancel, Panic and actual device reopen through these interfaces.

Windows uses `wmain` and `tools/CliArguments.h` for validated UTF-16 to UTF-8
arguments and native filesystem paths. MinGW needs the target's `-municode`
link option. POSIX paths retain native bytes. This implementation choice is
not a claim of an executed Windows or macOS build.

## Playing and editing

The resizable window starts at **1280 × 900 logical units**, has a minimum of
**960 × 700**, and limits each dimension to 8192. The drawing scale comes from
the actual drawable size; pointer input and the model use window coordinates.
Both the renderer and input use the same `UiLayout` control regions and playing
key quadrilaterals. Dimensional manuals have sloped sides and front faces;
Flat uses rectangular playing keys with the same semantic note identities.

| Input | Behavior |
| --- | --- |
| `A W S E D F T G Y H U J K O L P ;` | Seventeen chromatic positions, C through E, using physical scancodes. |
| `F1`, `F2`, `F3` | Select upper manual, lower manual, or pedals for new computer-key presses. |
| `F4`, `F5`, `F6` | Select Play, Rotary or Service. Computer-piano playing remains available in each workspace. |
| `F7` | Toggle Dimensional/Flat presentation without changing musical controls. |
| `[` / `]` | Move the computer keyboard octave within the model's limits. |
| `Tab` / `Shift+Tab` | Traverse 71 visible stops in Play, including three roving keyboard groups; traverse ten common controls in Rotary/Service. |
| Arrow keys, `Home`, `End` | Adjust the focused drawbar/expression or move the focused playing key. |
| `Space` | Activate a button, or hold the focused manual/pedal key until release. |
| `Enter` | Activate a focused button. |
| `Escape` | Release UI notes; close an open modal. |
| `Ctrl+S`, `Ctrl+O`, `Ctrl+,` | Save, Load, Audio settings. Command is also accepted. |
| `Ctrl+M` | Open MIDI settings. Command is also accepted. |
| `Shift+/` | Open Help. |

Note release always reaches `UiModel` before modifier, focus or modal gates.
Changing target, octave or focus cannot retarget an existing note's release.
Workspace, Flat and resize changes also preserve the original release owner.
Each workspace remembers its non-tab focus; hidden Play controls reject new
pointer, Space and arrow activation in Rotary/Service. Changing presentation
closes a parameter drag and suppresses further moves until its original release.
Pointer playing requests OS capture; a failed request immediately delivers
`CaptureLost`. Release outside the window, window deactivation/minimization,
lost capture and shutdown release the model's UI ownership safely. Escape is
a scoped UI release; the visible Panic control releases every owner.

Core and `UiModel` defaults remain muted. This application explicitly posts a
**proposed audition registration** after device preparation: upper B
`888000000`, lower B `008000000`, and pedal mixtures `80`. It leaves the two A
banks muted and retains the existing default expression/percussion controls.
This is a convenience for the nominal model, not a factory preset or a change
to saved-state defaults. An existing valid state replaces that proposal.

The current Play view uses walnut decoration, dark panels, brass headings,
adjacent drawbar racks and stacked manuals. At widths of at least 1400 logical
units it also shows the source-art cabinet and an explicit unavailable-sound
status card. The source is the atlas cover/page 409 generated concept, retained
with [provenance](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/design/atlas-reference.json). Only admitted cabinet/wood crops
are decorative; all keys, controls, values and focus states remain dynamic.
The source's inaccurate legends and key counts do not override the correct
61+61 manuals, 25 pedals or actual control semantics. The
[current native gallery](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/examples/demos/standalone-interface-preview-v1/README.md)
retains actual Play, Rotary, Service and Flat frames with source/executable/input
identities and remaining reference differences. Earlier galleries retain their
own dated observations. A source image is not a runtime screenshot or a verified
one-to-one appearance result.

The layout keeps 68 ordinary controls, including 24 reversed preset keys, plus
147 playing keys. Play exposes the performance body; Rotary exposes cabinet
reference facts and Service exposes six copied-state cards. Both inspection
bodies are read-only. Their current/retained/stopped/unprepared/unavailable
captions, availability/evidence labels and pending/applied distinction are
explained in the [interface guide](INTERFACE_RUNBOOK.md#read-service-and-rotary-correctly).
Neither workspace adds physical telemetry or connects scanner/AO-28/Leslie audio.

## MIDI settings, controllers and recovery

Choose **MIDI** or **Ctrl+M**. Opening the dialog requests background discovery
of exact native input names after **No input**. The query does not block the UI
event loop, painting or audio. Close and reopen to request an explicit refresh.
While **Searching MIDI inputs** is visible, No input/Apply, Disconnect and Close
remain usable; selecting a physical port requires the current query to finish.
A late result does not automatically select/open a port or overwrite a newer
Apply/Disconnect outcome. The eight focus positions
are previous port, next port, upper channel, lower channel, pedal channel,
Apply/Connect, Disconnect and Close. Pointer activation and Tab/Shift+Tab use the
same controls. Arrows change selected values, Home/End select endpoints, and
Enter/Space activates; Escape closes without applying staged changes. Channels
wrap from 16 to 1. Duplicate channel choices or ambiguous exact names reject
without replacing the active route. Audio must be running before a port can be
applied. The dialog stays open so the connection result can be inspected.

Mapped upper/lower notes are MIDI 36–96; pedals are 36–60. CC16–24 address the
respective manual's **B** drawbars in footage order, irrespective of EDIT or
SOUNDING selection. Pedal CC16/17 address the two nominal mixtures. CC11 from
any mapped division edits the same shared expression control. These changes
join the UI's desired controls and dirty/Save state; they do not select B or
re-enable a Cancelled route. CC123 releases only that mapped division's MIDI
owners. Unsupported controls include sustain, CC120/121, bank/program changes,
pitch bend, pressure and SysEx; there is no hidden registration or tuning map.
The [MIDI contract](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/MIDI_INPUT.md) defines the complete admission rules.

Disconnect, observed device loss, backend/inbox fault, Panic, Session recovery
and audio Restart retire the MIDI epoch and discard old queued packets. Normal
MIDI retirement releases upper/lower/pedal MIDI owners while preserving UI
channel-zero holds; global Panic/Session recovery have their wider existing
scope. Reconnect explicitly with Apply after audio is running and retirement
has resolved. No automatic reconnect or held-note replay occurs. If shutdown
cannot establish callback quiescence, the app requires process restart.
An ordinary Escape, focus loss or opening an overlay releases UI notes and
leaves the MIDI epoch active. Loading controls does not reconnect or release
MIDI. The [backend contract](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/MIDI_BACKEND.md) records best-effort hotplug
detection and native qualification limits.

## Audio settings and recovery

Audio shows Default output followed by exact names returned by SDL, plus the
three supported rates and five supported buffer sizes. If an output is open,
the dialog starts with its obtained rate and buffer. The footer reports the
actual driver and obtained callback format. Neither number is a measurement
of physical latency.

The six modal focus positions are previous device, next device, rate, buffer,
Apply and Close. Tab/Shift+Tab traverses them; arrows cycle a focused value;
Home/End choose its endpoints; Enter/Space activates it; Escape closes. Help
has one visibly focused Close button, also operated by Enter, Space or Escape.
Painting and clicks share `audio_overlay_layout`. Opening Help, Audio or MIDI releases
UI notes and retains physical-key suppression until the corresponding key-up.

Apply closes and joins the old callback, observes the resulting coherent
controls, then opens and prepares the requested output. The explicit copied
restore precedes device start. Acknowledged musical controls survive; notes
are cleared and fresh DSP preparation resets source phase and other transient
history. MIDI is retired before this restart and requires explicit Apply to
reconnect. Failed open retains the requested choices and initial/loaded intent
for an explicit retry. No dummy-driver retry occurs. An output-removal event,
invalid callback output, or two seconds without callback progress stops the
device and leaves a readable No Audio state.

While audio is unavailable, app requests and focus remain operable. Musical
commands receive a local `NotRunning` submission result; they do not accumulate
in a stopped Session. During normal or paused-start dispatch, every command is
posted then immediately delivered to `UiModel::submitted` in array order. A
failed submission stops the original batch and processes at most one returned
recovery batch. It never retries a queue or replays discarded notes.

## Musical files and thread ownership

Without `--state`, `SDL_GetPrefPath("B3Workshop", "HammondStandalone")` supplies
the directory for `controls.b3controls`. A missing file starts the proposed
registration. A malformed or unreadable existing file displays an error and
preserves that proposal and the file. Save is explicit; exit never saves.

Load validates the whole existing B3CONTROLS1/2/3/4 file through `StateFiles` on
the main thread, then submits a copied snapshot. Loading while offline retains
the validated controls for the next explicit device start. Save uses only an
acknowledged coherent `SessionSnapshot.controls`. If edits are pending, it
waits at most two seconds; changed controls, rejection or recovery cancel the
request. The exact successfully written copy becomes the clean-file reference.
Held keys, owners, MIDI port/channel selections, audio/window settings and DSP
histories, workspace, Flat presentation and focus are never saved. All 45 previous
parameter records retain their meanings;
two appended preset selectors bring the current count to 47. The writer emits
`B3CONTROLS4`, while readers 1/2/3 remain available. See the
[fixed-registration native workflow contract](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/PRESET_NATIVE_WORKFLOWS.md) for raw
fixed memory, effective selection and independent migration checks.

The main thread owns SDL initialization, window/events, UI, painting, parsing
and file I/O. Only `AudioDevice` and `Session` enter the audio callback. Device
close joins callbacks before Session destruction; glyph textures die before
the renderer, then the window, and finally `SDL_Quit`. No file or SDL graphics
operation is added to the callback by the application.

## Reproducible smoke and diagnostics

```sh
SDL_AUDIODRIVER=dummy SDL_VIDEODRIVER=dummy \
  build-native/apps/standalone/hammond_standalone \
  --state /tmp/b3-unused-controls.b3controls --smoke-ms 600 \
  --screenshot /tmp/b3-reference.bmp --diagnostics /tmp/b3-reference.json
```

Choose a nonexistent state path when checking the proposed registration. The
test sends SDL scancode A down and up through the real event loop, observes
the corresponding held state in callback snapshots, renders actual frames,
and joins the actual SDL output. It captures a requested image while the note
is held in the copied state used to paint that frame. A queued key-up does not
change the already painted frame. Every successful smoke with a requested
screenshot must contain that held-key image; if no held frame is observed, the
application captures the final available frame and reports a failed smoke.
`runtime.screenshot_while_held` describes the captured keyboard indication,
not the callback's concurrently changing state at the instant the file is written.
The time bound describes the event-loop interval;
window/device setup, shutdown and file writing are additional work.

JSON schema version 3 records `profile`, `runtime`, `audio`, `midi`, `presentation`, `session`,
`controls`, `smoke`, `state_path`, `status`, and `errors`. Runtime includes the
actual video driver, renderer, window/drawable sizes and rendered image count.
Audio includes requested and obtained configurations, native float32 format,
callback/frame counts and all format/render/nonfinite/overrange counters.
Session includes the final coherent revision, sequence/recovery/fault counters,
frame clock, maximum observed peak and held state after shutdown. Controls
include all four banks, remembered `selected_banks`, raw `fixed_registrations`,
separately derived `preset_selections`, routes, expression, percussion and pedals.
The new raw values 0–9 retain fixed memory during Cancel; effective values 0–11
report Cancel/fixed/bank routing. Archived schema-2 reports remain unchanged.
Replay records also retain the pre-shutdown snapshot/running, pending-control
and pending-save predicates and desired controls used by the acknowledgment
barrier. These copied values make a failed replay diagnosable before shutdown
cleanup changes state; they do not weaken the completion requirement.
The final device counters are copied after callbacks have joined.

`presentation` keeps initial choices, a bounded observation history,
`last_painted`, `screenshot` and `before_shutdown` records. Each painted record
identifies workspace (`play|rotary|service`), presentation (`dimensional|flat`),
overlay, logical size and copied inspection status/frame/revision. Screenshot
identity is frozen from the actual painted frame; final shutdown data does not
replace it. These fields do not change sound-control or saved-state meanings.

`midi` identifies the compiled backend, requested and observed port, selected
channels, connection/retirement state, decoder/inbox/device counters and the
source (`none`, `native` or `synthetic-replay`). Backend availability means
compiled capability, not successful physical enumeration. Synthetic input keeps
native generation and native callback counts at zero. Optional `replay` and
`midi_replay` objects retain their respective completion results; neither is
present merely because MIDI support was compiled.

The MIDI `discovery` fields distinguish requests, starts, completions, discarded
results, failures and pending/join state at shutdown. Shutdown joins outstanding
native discovery after audio closes; the operating-system query has no promised
hard deadline. The separate `--list-midi` command still performs explicit native
enumeration rather than using the modal's background workflow.

Smoke exits nonzero for an output that is not open/running before shutdown,
missing callbacks or rendered frames, missing observed
note press/release, session faults, callback render/format/nonfinite/overrange
failures, a requested screenshot failure, or a diagnostics write failure.
Ordinary user registrations can be silent; the held-state check does not force
a gain change. Final queued shutdown release commands may be counted as
discarded by the stopped lifecycle even on a successful run.

The native acceptance tests compare the pictured middle-C key with neighboring
unheld white keys, in addition to checking copied diagnostics. Resize workflows
use an acknowledged held endpoint followed by a separate released endpoint;
each sampled observation must match a legal accepted-command prefix. A released
observation after a focused control edit is valid once the scripted key-up is
acknowledged. The [timing repair report](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/reviews/STANDALONE_TIMING_REPAIR.md)
retains the earlier failed gate and the repair's exact verification scope.

The [assignment evidence](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/development/2026-11-13-next-phases/18-native-app.md)
records actual software/dummy execution. Dummy callbacks and rendered BMPs
establish neither a visible OS desktop nor audible hardware output, physical
latency, underruns, assistive-technology support, distribution readiness or
acoustic fidelity.

### Path identity and file admission

State, script inputs, screenshot and diagnostics must name distinct files. Existing parent
aliases are resolved even when a filename is new; existing hardlinks are also
checked. Symbolic-link leaves are rejected for these selected paths, whether
they currently resolve or dangle. Screenshot/diagnostic outputs must be regular
files or new paths. These checks precede audio activation and output writes.
They preserve the selected musical file under these admitted path cases; they
do not claim protection against concurrent hostile filesystem changes.
