# Native interface: operating guide

The standalone application has three workspaces over one **nominal dry organ**:
Play for performance and editing, Rotary for cabinet reference information, and
Service for read-only inspection. Dimensional and Flat presentations use the
same musical controls. The interface preserves all **47 sound parameters**, the
**`B3CONTROLS4`** writer and readers for versions 1–3; changing a view does not
change sound state or recall a registration.

Use this guide for the current interface. The installed
[preset guide](PRESET_RUNBOOK.md) gives source-build commands and complete
registration/state workflows; the [application guide](STANDALONE_APP.md) lists
CLI options and diagnostic fields; the [model guide](STANDALONE_MODEL.md)
defines the nominal sound. The [MIDI guide](MIDI_UI_RUNBOOK.md) retains the
controller map and platform prerequisites. The current discovery procedure is
also described below. Source-only references use repository URLs so links in
the installed guides remain usable; those references require network access.

## Start and play

From an installed prefix, run:

```sh
bin/hammond_standalone --help
bin/hammond_standalone --state ./my-controls.b3controls --workspace play
```

Windows uses `bin/hammond_standalone.exe`. For a source build, substitute the
actual target path, normally `build-native/apps/standalone/hammond_standalone`;
multi-configuration builds add `Release/` before the executable. Build and
dependency commands are in the [preset guide](PRESET_RUNBOOK.md#build-from-source).
Keep the complete payload together when moving an installation, as specified
by the [installation guide](STANDALONE_INSTALL.md).

Choose a writable regular state-file path. A valid existing file loads at
startup. An absent file starts the proposed audition registration: Upper B
`888000000`, Lower B `008000000`, and pedal mixtures `80`. This startup choice
is not a factory preset. Without `--state`, SDL's preference directory supplies
`controls.b3controls`. Save is explicit; closing the application does not save.

Audio initially requests the default SDL output at 48 kHz with 512-frame
buffers. Open **AUDIO / Ctrl+,**, select an output/rate/buffer, and Apply when
a different configuration is needed. The obtained format is displayed, but
the buffer setting is not a physical latency measurement. A failed output
leaves the settings controls available for an explicit retry.

For a first interface check, press and hold computer key **A** in Play, then
press **F6** to enter Service. The held Upper target remains owned while the
Service card reports the copied held-target count. Press **F7** to change
presentation, then **F4** to return to Play and release **A**. Navigation does
not create another note or change the original release target. Opening Help,
Audio or MIDI has a different, deliberate behavior: it releases UI holds and
suppresses still-down physical keys until their releases.

## Workspaces, Flat and focus

| Workspace | Operation | Available body |
| --- | --- | --- |
| Play | Click **PLAY** or press **F4**. | Live drawbars, preset octaves, percussion, expression, pedal mixtures, two manuals and pedals. |
| Rotary | Click **ROTARY** or press **F5**. | Decorative cabinet reference and six read-only facts about its implementation and evidence. Cabinet audio is not connected. |
| Service | Click **SERVICE** or press **F6**. | Six simultaneous read-only cards: Generator, Contacts/routing, Scanner, AO-28, Leslie and Retained controls. |
| Flat | Click **FLAT** or press **F7** in any workspace. | A complete alternate presentation. Play keys become rectangular and ornamental grain/depth is reduced; all musical controls retain their meanings. |

The ten common header controls are Play, Rotary, Service, Save, Load, Help,
Audio, MIDI, Panic and Flat. They remain available in every workspace. The
layout retains **68 ordinary control records**, including all **24 reversed
preset keys**, and **147 playing keys**: 61 Upper, 61 Lower and 25 pedals.
Tab/Shift+Tab traverses **71 stops in Play**: its 68 controls and three roving
playing-key groups. Rotary and Service traverse only the **ten common stops**;
their information cards add no focus targets.

Each workspace remembers its latest visible non-tab focus. Returning restores
that target, or focuses the workspace's own tab when no target is remembered.
Selecting the already active workspace leaves focus in place. Flat and resize
preserve focus. A hidden Play control cannot receive a new click, Space
audition or arrow edit from Rotary or Service.

Computer-piano playing remains available in all three workspaces:

| Input | Action |
| --- | --- |
| `A W S E D F T G Y H U J K O L P ;` | Play seventeen chromatic positions using physical scancodes. |
| `F1`, `F2`, `F3` | Choose Upper, Lower or Pedals for subsequent computer-key presses. |
| `[` / `]` | Change the octave for subsequent computer-key presses. |
| `Tab` / `Shift+Tab` | Traverse visible controls and, in Play, the roving key groups. |
| Arrows, `Home`, `End` | Adjust or navigate the focused control. Preset-key navigation changes focus; Enter/Space makes the selection. |
| `Space` | Activate a focused button, or hold a focused playing key until Space is released. |
| `Enter` | Activate a focused button. |
| `Escape` | Release UI notes and close an open modal. |
| **PANIC** | Release every note owner, including external MIDI; reconnect MIDI explicitly afterward. |
| `Ctrl+S`, `Ctrl+O`, `Ctrl+,`, `Ctrl+M` | Save, Load, Audio, MIDI. Command is also accepted. |
| `Shift+/` | Open Help. |

F4–F7 do not operate underneath an open modal or with Ctrl/Alt/Meta held, and
key repeat does not repeat their actions. Original key-up and pointer-up
releases remain paired with the original note even after target, octave,
workspace, Flat or size changes. Switching view closes an active parameter
drag; release and start a new gesture to continue editing. A held pointer note
keeps its original owner until release/capture loss, rather than gliding through
controls exposed by the new view. Focus loss and Panic retain their explicit
release behavior.

Startup accepts `--workspace play`, `--workspace rotary` or
`--workspace service`, with Play as the default. Add `--flat` for Flat startup;
otherwise the presentation is dimensional. Unknown workspace values reject
before device initialization or output writes. Workspace, presentation, focus,
edited-bank choice and window dimensions are transient UI state, outside the
saved musical controls and sound parameter registry.

## Registrations, applied values and pending edits

On each manual, preset **C** cancels the route, **C#–A** selects one of nine
fixed rows, **A#** sounds adjustable bank A, and **B** sounds adjustable bank B.
The two manuals therefore offer eighteen fixed registrations. Fixed A and
adjustable A#/bank A are different choices. **EDIT A/B** selects which retained
bank the drawbars edit; it does not change the sounding route. Editing a bank
while a fixed row or Cancel is selected preserves that route. All four banks
remain stored. The [preset guide](PRESET_RUNBOOK.md#select-edit-and-play) gives
the full mapping, percussion eligibility and MIDI editing rules.

The selected preset indication describes applied controls. An amber pending
outline identifies a requested selection awaiting acknowledgment; a separate
two-tone outline identifies keyboard focus. Service's **Sound** value comes
from the applied snapshot, while **Edit** identifies the UI bank selection.
**DESIRED CONTROLS PENDING** means a desired edit is still awaiting the ordinary
control acknowledgment. It does not relabel that desired value as applied.

Service shows the four retained bank strings in Upper A/B then Lower A/B order.
These memories are not the connection taps of a sounding fixed registration.
Cancel disconnects the route while retaining bank/fixed memory and held notes.
Percussion choices are retained independently of eligibility: the connected
Upper B route with no fixed choice is eligible. Readiness history is not an
inspected value.

**SAVE / Ctrl+S** waits for acknowledged controls and writes canonical state4.
**LOAD / Ctrl+O** validates supported state versions before applying controls.
Versions 1–3 migrate the fixed modes to None; the next explicit Save writes
version 4. Save/Load excludes held notes, phase, contact/percussion histories,
device selections, workspaces, presentation and focus. Live Load changes musical
controls while preserving the existing histories; it does not return to a saved
UI workspace. An audio restart preserves acknowledged controls but deliberately
clears notes and starts a new audio lifecycle.

**UNSAVED** in the footer marks controls changed from the current clean reference;
it is independent of pending acknowledgment. The audition baseline can be clean
before any file exists, so Save explicitly to create one. **Loaded saved
controls.** confirms file loading; pending indicators show whether audio has
applied the request. A Save success message confirms the write. A cancelled or
timed-out Save requires a new Save request.

## Read Service and Rotary correctly

The banner identifies what kind of copied software observation is visible:

| Banner | Meaning |
| --- | --- |
| **CURRENT SNAPSHOT** | A coherent prepared/running copy was read successfully for the paint cycle. This is an observed software state, not a physical timing measurement. |
| **RETAINED SNAPSHOT** | A previous prepared copy exists, but the latest bounded read did not succeed. Displayed frame/revision identify that retained copy. |
| **STOPPED SNAPSHOT** | The successful copied observation says the prepared Session is stopped. Retained musical values can still be inspected. |
| **UNPREPARED SNAPSHOT** | A copy exists but is not prepared. Applied controls and held counts say **Not observed**. |
| **SNAPSHOT UNAVAILABLE** | No coherent copy is available. Applied values say **Not observed**, without substituting zero. |

The order matters: no copy is unavailable; an unprepared copy is unprepared;
a failed latest read of a prepared copy is retained even when that copy says
stopped. A nonzero frame/revision alone does not establish freshness. Loaded
profile values and compiled model facts can remain visible without an applied
observation; the banner labels the profile as **Loaded profile**.

Each row separately labels **A = Availability** and **E = Evidence**.
Availability distinguishes Available, Not observed, Not integrated, Not acquired
and Invalid. Evidence distinguishes Software, Documented, Derived, Proposed and
Unknown. Available means the row has its stated information; it does not mean
the value was measured from hardware. Invalid data remains visibly invalid
instead of becoming a default or a numeric zero.

| Card or readout | What it means in this application |
| --- | --- |
| Generator | The shared sine family and 91-source inventory are software facts. Tone 46 frequency in Hz and normalized output gain come from the loaded nominal profile and remain proposed/unmeasured. |
| Contacts/routing | The active standalone family is `ideal-contacts-v1`. Held counts are logical targets, not physical contact counts, owner counts or proof of audible sound. |
| Scanner | The separate research module is identified, while its audio path says **Not connected** and specimen captures **Not acquired**. |
| AO-28 | The complete circuit is **Not connected**. Percussion is a nominal surrogate. Specimen/revision and physical voltage remain unacquired/unavailable; V is the unit, not a measured reading. |
| Leslie | Cabinet audio is **Not connected**. The documentary target is Leslie 122 with 147 separate. Horn/drum speeds are **Unavailable** in rpm; microphone geometry is **Not acquired** in m. |
| Rotary | The cabinet artwork is decorative atlas concept material. Rotor speeds are unavailable, microphone geometry is unacquired and Stop/brake is **Not modeled**. There are no editable speed, microphone or brake controls. |

These cards do not edit physics, create a new audio path, sample private engine
history or acquire measurements. Their units and source/evidence labels keep
unknown physical quantities distinct from ordinary user controls. The
[inspection contract](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/INTERFACE_INSPECTION_CONTRACT.md)
defines the exact copied-state and evidence boundary.

## MIDI discovery and recovery

Open **MIDI / Ctrl+M** to request native input discovery. The query runs away
from the event loop; **Searching MIDI inputs** does not freeze modal navigation,
painting or audio. Opening the modal releases UI holds; computer playing resumes
after it closes. Existing external MIDI ownership follows its own connection
lifecycle.

Select one exact, unique input name and distinct Upper/Lower/Pedal channels
1–16 (defaults 1/2/3), then Apply. A physical port can be applied only after
the current discovery finishes and audio is running. While discovery is pending,
**No input**, **Apply** for that No input choice, **Disconnect**, and **Close**
remain usable. Closing and reopening requests an explicit refresh. A late result
does not automatically connect a port or replace a later Apply/Disconnect result.

No port is selected automatically at ordinary startup. A build with MIDI disabled
says its backend is unavailable; keyboard/pointer and explicit synthetic replay
remain usable. `--list-midi` is a separate explicit command that lists exact
names; its native enumeration is not the modal's background query. Shutdown joins
an outstanding discovery after audio closes, so native enumeration has no claimed
hard operating-system deadline.

Dummy SDL audio and video do not replace the compiled native MIDI backend.
On Linux without an accessible ALSA sequencer, opening MIDI settings can report
**Cannot enumerate MIDI input ports** even when **No input** is selected. Leave
No input selected and use Apply or Disconnect, then Close to resume computer
playing. Correct the native MIDI environment before reopening the dialog to
request another discovery.

That discovery error remains in diagnostics after recovery. A scripted
`B3UIREPLAY1` run that records it returns nonzero with `replay.passed=false`;
preserve that failure. Ordinary dummy runs that do not need MIDI discovery can
leave the dialog closed. Explicit synthetic MIDI replay uses its separately
documented script-controlled route.

Normal Disconnect releases MIDI owners while preserving independently held UI
notes. A fault, Panic or audio restart retires old MIDI input; resolve the cause
and explicitly Apply again. Reconnection needs fresh Note Ons. A failed shutdown
that cannot establish callback quiescence requires an application restart.
Compiled backend availability, a successful synthetic replay and a responsive
discovery dialog each remain separate from physical controller qualification.

## Sizes, screenshots and reproducible qualification

The default size is 1280×900 logical units; the minimum is 960×700, with each
dimension limited to 8192. The reference comparison size is 1672×941. Play hides
its optional cabinet column below width 1400 and moves Edit controls into the
racks below height 820. Both presentations retain the complete instrument.
Perspective manual keys use the same visible shape for painting, pointer input
and inset focus. Flat supplies rectangular playing keys.

The [current eight-image preview and reproduction commands](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/examples/demos/standalone-interface-preview-v2/README.md)
cover Play at reference/default/minimum sizes, Rotary and Service at
reference/minimum sizes, and minimum Flat Play. The
[provisional v1 gallery](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/examples/demos/standalone-interface-preview-v1/README.md)
remains unchanged historical evidence. The source
[capture utility](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/tools/capture_standalone_interface.py)
requires a matching source qualification report and expected executable digest,
then writes a fresh gallery. Use the exact source-specific command in that
preview; a later renderer needs a new matching report and a new output directory.
Python/Pillow are capture-authoring dependencies, not runtime requirements.

For a bounded single-view check, choose new distinct output names and an absent
state path. Run this from a built source checkout:

```sh
SDL_AUDIODRIVER=dummy SDL_VIDEODRIVER=dummy \
  build-native/apps/standalone/hammond_standalone \
  --state /tmp/b3-interface-unused.b3controls \
  --workspace service --flat --width 960 --height 700 --smoke-ms 600 \
  --screenshot /tmp/b3-interface-service.bmp \
  --diagnostics /tmp/b3-interface-service.json
```

This exercises the actual native renderer and copied-state path with dummy
drivers. Native diagnostics retain schema 3 and a separate `presentation`
object: initial choices, observations, last painted view, screenshot view and
the view before shutdown. The screenshot record names the view actually painted;
final shutdown controls cannot substitute for that observation. UI replay uses
the existing `B3UIREPLAY1` grammar with F4–F7 admitted, and its wall-clock timing
is not sample-accurate automation. See the
[application guide](STANDALONE_APP.md#scripted-interaction-and-observations).

The current gallery records published product source and its exact executable
identity; it does not automatically qualify a changed executable. Current
publication and execution evidence is
in the [status](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/STATUS.md)
and [interface session](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/development/2026-11-14-interface-continuation/README.md).
Literal 1:1 equality with the concept remains open: the live full key/pedal
inventory, control labels, panel proportions, materials and cabinet composition
retain differences. Native display/DPI behavior, screen-reader integration,
physical MIDI/audio, callback deadlines, connected scanner/AO-28/Leslie models,
calibration, signing and release rights each require their own evidence.
