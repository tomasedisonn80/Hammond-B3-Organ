# Fixed registrations: build and operating guide

The current instrument is a **nominal dry organ** with eighteen documentary
fixed registrations, four retained adjustable banks, 47 public parameters and
`B3CONTROLS4` saved controls. Each manual has nine fixed choices and a twelve-key
reversed preset octave. The new controls use the existing nominal gain model;
they do not add scanner, AO-28 or Leslie processing. The
[selection contract](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/PRESET_SELECTION_CONTRACT.md)
defines the behavior and source limits.

This guide supplies the current preset, state and diagnostic instructions.
The [interface runbook](INTERFACE_RUNBOOK.md) covers Play/Rotary/Service, Flat,
focus, copied-state inspection and current background MIDI discovery.
Earlier galleries, state files and reports retain their original versions.
Links below use repository URLs so this guide remains navigable when installed
beside the application. Those linked references require network access.

## Start an installed application

Run `bin/hammond_standalone` beneath the selected installation prefix; Windows
uses `hammond_standalone.exe`. For example, from that prefix:

```sh
bin/hammond_standalone --help
bin/hammond_standalone --state ./my-controls.b3controls
```

Choose a writable regular state-file path. An existing valid file loads at
startup; an absent file gives the proposed audition registration: Upper B
`888000000`, Lower B `008000000`, pedals `80`. This is not a factory preset.
Save is explicit; exit never saves automatically. Without `--state`, the app
uses SDL's preference directory and `controls.b3controls`.

Audio defaults to SDL's default output, 48 kHz and 512 frames. **AUDIO / Ctrl+,**
selects an exact output, 44.1/48/96 kHz and 128/256/512/1024/2048-frame buffers.
`--list-audio` lists outputs. **MIDI / Ctrl+M** connects one explicitly selected
input when the physical backend is available; no port is selected by default.
`--list-midi` prints exact names. Opening MIDI requests nonblocking background
discovery; close and reopen for an explicit refresh. No input/Apply, Disconnect
and Close remain available while discovery is pending. Connect a physical port
only after the current discovery finishes. Upper/Lower/Pedal channels default to 1/2/3
and must be distinct values from 1 through 16. Apply staged device choices
explicitly. The obtained buffer setting is not a measured latency result.

## Build from source

Run these commands from the repository root, using new build directories.
Ordinary builds require a C++20 compiler, CMake 3.21+, Python 3.10+ and Git.
The native window also needs a C compiler and platform desktop/audio development
libraries. Optional VST3 requires CMake 3.25+. POSIX shell examples use `python3`;
Windows may use `python`. Multi-configuration generators require `--config
Release` for builds and `-C Release` for CTest; executable subdirectories also
contain `Release`, and Windows executable names end in `.exe`.

### Core, offline tools and host-independent tests

```sh
cmake -S . -B build-presets -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_BUILD_VST3=OFF -DHAMMOND_ENABLE_MIDI=OFF
cmake --build build-presets --config Release --parallel 3
ctest --test-dir build-presets -C Release --output-on-failure --no-tests=error
```

This configuration needs no SDL, RtMidi or VST3 SDK. It includes the
host-independent Session/UI tests and benchmark. The ordinary build generates
`nominal.b3p` and admits the fixed table from its frozen authoring file and both
independent CSV readings. No extra preset feature flag or runtime catalog file
is required. `cmake --build build-presets --config Release --target check`
is the alternative that builds required test inputs before running CTest.

### Native window and optional MIDI

Acquire the locked SDL 2.32.10 source into a new external directory whose parent
already exists. For an existing checkout, use `--verify-existing` instead of
`--destination`:

```sh
python3 tools/acquire_sdl2.py --destination ../SDL2
cmake -S . -B build-presets-native -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_STANDALONE=ON -DHAMMOND_SDL2_ROOT="$PWD/../SDL2" \
  -DHAMMOND_ENABLE_MIDI=OFF -DHAMMOND_BUILD_VST3=OFF
cmake --build build-presets-native --config Release \
  --target hammond_standalone_test_inputs --parallel 3
ctest --test-dir build-presets-native -C Release --output-on-failure \
  --no-tests=error -R '^test_standalone_'
```

The single-configuration executable is
`build-presets-native/apps/standalone/hammond_standalone`. Building only
`hammond_standalone` creates the app without all acceptance executables.
The [SDL contract](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/STANDALONE_DEPENDENCY.md)
and [platform prerequisites](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/MIDI_UI_RUNBOOK.md#prerequisites-and-platform-backends)
give dependency checks and platform packages.

For physical MIDI, acquire locked RtMidi 6.0.0 and configure a separate build:

```sh
python3 tools/acquire_rtmidi.py --destination ../rtmidi-6.0.0
cmake -S . -B build-presets-midi -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_STANDALONE=ON -DHAMMOND_SDL2_ROOT="$PWD/../SDL2" \
  -DHAMMOND_ENABLE_MIDI=ON -DHAMMOND_RTMIDI_ROOT="$PWD/../rtmidi-6.0.0" \
  -DHAMMOND_BUILD_VST3=OFF
cmake --build build-presets-midi --config Release \
  --target hammond_standalone_test_inputs --parallel 3
```

Run the same standalone CTest filter against `build-presets-midi`. Linux uses
ALSA, Windows WinMM and macOS CoreMIDI. A compiled backend does not establish a
working device connection. The
[RtMidi contract](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/RTMIDI_BUILD.md)
owns source identities, the prepared build copy and required system libraries.
CMake verifies dependencies offline; acquisition tools perform the explicit
network step. Keep dependency checkouts clean and build outside them.

### Optional VST3

```sh
python3 tools/acquire_vst3_sdk.py --destination ../vst3sdk
cmake -S . -B build-presets-vst3 -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_VST3=ON -DHAMMOND_VST3_SDK_ROOT="$PWD/../vst3sdk" \
  -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_ENABLE_MIDI=OFF
cmake --build build-presets-vst3 --config Release --target check_vst3 --parallel 3
```

For an existing SDK, use `acquire_vst3_sdk.py --verify-existing ../vst3sdk`.
`check_vst3` builds the bundle, validator and native test inputs before running
the required filter. `hammond-vst3-path-Release.txt` in the build directory names
the actual bundle. No build command installs it into a host's plugin directory.
See the [VST3 build](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/VST3_BUILD.md)
and [local staging](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/VST3_LOCAL_INSTALL.md)
guides. The native plugin exposes 47 controls through host interfaces; its custom
editor and actual DAW/device qualification remain separate work.

## Select, edit and play

The small reversed octave on each manual's left cheek controls that manual's
route. These keys are separate from the 61 playing keys on each manual and the
25 pedals.

| Key | Plain selector | Action |
| --- | ---: | --- |
| C | 0 | Cancel the manual route; retain its fixed choice and adjustable bank. |
| C# | 1 | Select that manual's fixed C# row. |
| D | 2 | Select fixed D. |
| D# | 3 | Select fixed D#. |
| E | 4 | Select fixed E. |
| F | 5 | Select fixed F. |
| F# | 6 | Select fixed F#. |
| G | 7 | Select fixed G. |
| G# | 8 | Select fixed G#. |
| A | 9 | Select fixed A. |
| A# | 10 | Sound retained adjustable bank A. |
| B | 11 | Sound retained adjustable bank B. |

**Fixed A and adjustable A#/bank A are different controls.** Selecting a fixed
row reconnects the route without copying into either adjustable bank. Selecting
A# or B reconnects that bank and clears fixed mode, including an explicit
reselection of an already remembered bank. C is momentary and remains visually
unlatched; the caption says `CANCELLED`. Selection and preset-key release do not
create or release playing notes, reset phase, or reset percussion readiness.

**EDIT A/B** chooses the bank shown by the drawbar editors. Its caption is
separate from the applied sounding choice. Editing a bank during fixed selection
or Cancel leaves that route unchanged. MIDI CC16–24 likewise edits the
corresponding manual's retained **B** bank; explicitly choose preset B to hear it.
MIDI program changes and MIDI-note preset switching are not mapped. The two new
host parameters are Upper **20480** and Lower **20481**, plain values 0–11.
They are ordinary routing parameters, not host programs or whole-state recall.

Click a preset once, or focus it with Tab and activate with Enter/Space.
Left/Right moves preset focus; Home/End focuses C/B; Up/Down focuses the same
pitch on the other manual. Those navigation keys do not select a route.
In Play, Tab/Shift+Tab traverses 71 stops, including three roving playing-key
groups. Rotary and Service traverse ten common header controls. F4/F5/F6 selects
Play/Rotary/Service; F7 toggles Flat. Workspace and presentation changes preserve
held-note release ownership and sounding controls; hidden preset keys cannot
receive new activation outside Play. Each workspace remembers its non-tab focus.
The applied key stays selected while a different requested key has an amber
pending outline. The separate two-tone outline denotes keyboard focus.

Computer keys `A W S E D F T G Y H U J K O L P ;` play notes; F1/F2/F3 chooses
Upper/Lower/Pedals and `[`/`]` changes octave. Escape releases UI notes. Help,
Audio and MIDI dialogs also release UI holds; independently held external MIDI
notes retain their owners. Preset C cancels a route and is not global Panic.

Percussion sounds only when enabled on the connected Upper B route with no
fixed registration. Stored tablet choices remain visible while ineligible,
with `REQUIRES UPPER B`. Lower presets do not change upper percussion. Returning
to B uses the current readiness history; it does not manufacture a fresh trigger.

## Save, Load and recovery

**SAVE / Ctrl+S** waits for acknowledged controls and writes canonical
`B3CONTROLS4`. **LOAD / Ctrl+O** reads the selected file. Versions 1, 2 and 3
remain readable and migrate both fixed modes to None; the next explicit Save
writes version 4. Files are not silently rewritten at startup or exit.

Version 4 retains all four banks, remembered banks, raw fixed choices, route
bits, expression, percussion and pedal mixtures. It pins catalog
`atlas-chapel-nominal-v1` to its exact authoring SHA-256. A mismatched catalog or
malformed file rejects instead of substituting another table. Cancelled fixed
memory survives Save/Load. Held notes, phase, contact/readiness history, devices,
workspace, presentation and UI focus are not saved. Live Load changes controls while preserving current
histories; cold Load creates no held notes. Audio restart preserves controls
but deliberately releases notes and restarts the existing audio lifecycle.
The [format contract](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/CONTROL_STATE_FORMAT.md)
contains exact grammar and migration rules.

| Situation | Action |
| --- | --- |
| An edited bank is inaudible | Inspect the sounding caption. Choose A# or B explicitly; an edit alone does not leave fixed mode or Cancel. |
| Percussion is stored On but silent | Enable the Upper B route; fixed registrations and Cancel are ineligible. |
| State Load rejects | Preserve the file and inspect the diagnostic. Use an intact supported file; do not repair it by changing only its version header or catalog digest. |
| No Audio or output failure | Choose a working output in AUDIO and Apply. Musical commands do not accumulate while the Session is stopped. |
| MIDI fault, Panic or audio restart | Resolve the device problem and explicitly Apply MIDI again. Old packets/notes are retired; fresh Note Ons are required. |
| Session queue recovery | The specified emergency path may release all note owners. Resolve the visible recovery state; do not retry a failed batch blindly. |
| MIDI shutdown cannot establish quiescence | Restart the app before another open. This is distinct from a successful ordinary Disconnect. |

## Reproduce a preset workflow without hardware

Use a fresh `out/preset-example` directory. Save the following exact script as
`out/preset-example/preset.b3ui`; these literal pointer points are for the
specified **960×700** layout:

```text
B3UIREPLAY1
duration_ms 1200
100 key_down A none 0
300 mouse_down 44 440
310 mouse_up 44 440
600 mouse_down 34 468
610 mouse_up 34 468
800 key_down S ctrl 0
810 key_up S ctrl
```

It holds Upper C4, selects Upper C#, cancels that route, and explicitly saves
the still-remembered registration. Start with an absent `controls.b3controls`:

```sh
SDL_AUDIODRIVER=dummy SDL_VIDEODRIVER=dummy \
  build-presets-native/apps/standalone/hammond_standalone \
  --width 960 --height 700 --state out/preset-example/controls.b3controls \
  --input-script out/preset-example/preset.b3ui \
  --screenshot out/preset-example/preset.bmp \
  --diagnostics out/preset-example/preset.json
```

Expected: exit 0, native diagnostics **schema 3**, all replay completion/delivery/
acknowledgment/pass flags true, and zero application errors. Before shutdown,
Upper note 60 remains owned, `fixed_registrations` is `[1,0]`,
`preset_selections` is `[0,11]`, `selected_banks` is `[1,1]`, and routes are
`[false,true]`. Shutdown then releases notes. The saved file is state4 with
`manual upper selected B fixed_registration C# route_enabled 0`.
The BMP comes from the actual application renderer.
Dummy drivers establish this software workflow without physical sound or MIDI.

The [native diagnostic contract](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/PRESET_NATIVE_WORKFLOWS.md)
distinguishes raw remembered controls, derived selection, desired state and
pre-shutdown acknowledgment predicates. Retain the complete JSON on failure.
UI replay is wall-clock scheduling, not sample-accurate automation. The existing
two-second completion drain is a bound, not a display or audio latency promise.
State, scripts, screenshot and diagnostics must be distinct admissible paths;
use new output names for each retained run.

### Offline audio and verification

Create the `out` parent if needed, then choose an unused result directory:

```sh
cmake -E make_directory out
python3 tools/render_fixture.py --renderer build-presets/hammond_render \
  --output-dir out/preset-selector-evidence \
  --events examples/fixtures/presets/selector-events-v1.txt \
  --frames 96000 --sample-rate 48000 --block-size 127 --seed 7 \
  --drawbars 000000000 --pedal-drawbars 00 --percussion off
python3 tools/verify_render.py out/preset-selector-evidence
```

The current producer must report `succeeded`; the independent verifier must
report `verified_retained_bundle`. Its byte checks do not run the recorded
commands or establish physical fidelity. Offline evidence stays **schema 3**;
this is separate from saved-control version 4 and native diagnostic schema 3.
The event form is `frame select_preset upper|lower 0 value`, with integer value
0–11 and stable file order at equal frames. See the
[offline contract](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/PRESET_OFFLINE.md)
for the exact admission and retained evidence rules.

## Staging and the next qualification

Stage the native app explicitly into a new prefix:

```sh
cmake --install build-presets-native --config Release --component Standalone \
  --prefix /absolute/path/to/new-stage
```

The executable embeds its nominal profile, immutable rows, glyphs and admitted
decorative assets; normal use needs no Python or source checkout. Platform
runtime libraries/drivers remain required. Preserve the package's notices,
locks, capability metadata and guides. The
[installation contract](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/STANDALONE_INSTALL.md)
owns the exact payload and relocation checks; staging is not a signed installer.

The SDK-free Session benchmark now writes
`hammond-standalone-benchmark-v2`, retaining workload version 1 and the existing
four workload definitions. Its timing observations are not device deadlines;
see the [benchmark guide](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/STANDALONE_BENCHMARK.md).

Use the [preset handoff](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/PRESET_HANDOFF.md)
and [current status](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/STATUS.md)
for exact qualified source and remaining work. Actual reference comparison,
native accessibility, physical controllers/audio, DAWs, connected electronics,
scanner/rotary integration and measured fidelity retain separate gates. A
documentary registration or a passing synthetic run closes none of those gates.
