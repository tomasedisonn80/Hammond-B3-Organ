# A17 — Native reference rendering and MIDI presentation

Actual worker: `/root/w03_a17_reference_renderer`; MIDI/UI wave 3, assignment 17.
Owned implementation: `apps/standalone/Drawing.h`, `Drawing.cpp`, and
`InstrumentView.cpp`. The already-added `InstrumentView.h` MIDI fields and
`MidiOverlayLayout` declaration were preserved. This note is the only owned
document. No changes were made to `main.cpp`, `UiModel`, CMake, the core,
parameter identities, state formats, or shared status records. No commit was
made by this worker.

## Implemented behavior

The native renderer now follows A15's shared
`standalone-reference-player-layout-v1` geometry. The exact 1672 × 941
[source JPEG](../../design/atlas-cover-reference.jpg) was opened and visually
inspected before implementation. The actual reference-sized native capture was
then opened and compared with it; the default and minimum captures were also
opened and inspected.

- The source-derived wood cheeks frame charcoal panels with brass edges and
  screw details. The centered serif heading reads `TONEWHEEL ATLAS`, with the
  truthful `NOMINAL DRY ORGAN` secondary line. Header tablets remain SAVE,
  LOAD, HELP, AUDIO, MIDI and PANIC.
- Adjacent drawbar racks use the model's actual editor bank, applied sounding
  bank, corrected footage labels, values, and top-zero/bottom-eight cap
  positions. Recessed slots, metal shafts, raised caps and front edges are
  separate procedural paint. Cap colors retain the specified footage order.
- The percussion tablets retain their actual settings. Nominal expression and
  the two nominal pedal mixtures remain actual working controls. No scanner,
  microphone, rotary-speed, or other unavailable DSP control was painted.
- Both complete manuals and all 25 pedals retain shared rectangular hit
  geometry. Ivory/black planes, fronts, held state, and cyan focus stay inside
  each key's region. Bank rails are painted only when A15 places controls there;
  at minimum height the same buttons remain in the drawbar racks.
- The cabinet is the admitted decorative crop, painted only in
  `layout.cabinet_art`. Its caption reads `CABINET REFERENCE` and
  `ROTARY AUDIO NOT CONNECTED`; the explicit qualifier avoids confusing that
  boundary with the dry organ's nearby `AUDIO RUNNING` status. The service card
  uses copied audio configuration, MIDI backend/port/status/message count, and
  explicit unavailable scanner/rotary processing. It adds no hit targets.
- `Drawing::initialize` creates and uploads three optional static RGB24
  textures from the generated descriptors, after preparing the two font
  textures. Painting only copies those cached textures; it performs no image
  decoding, file I/O, texture creation, or upload. Destruction releases all
  owned textures. The existing app renderer-reset path reconstructs Drawing.
  Optional art preparation/copy failure leaves procedural decoration and all
  independently painted controls available.

The new 740 × 520 MIDI modal uses one exported rectangle set in exactly the
main application's order: previous port, next port, upper channel, lower
channel, pedal channel, Apply, Disconnect, Close. Main's existing focus paint
therefore matches the keyboard and pointer targets. The modal keeps selected
channels separate from actual connection state, shows repeated-channel
validation, wraps/elides backend strings inside their own regions, and explains
Apply/Disconnect semantics. The current app refreshes enumeration when the
modal opens; the renderer says to close/reopen to refresh instead of painting
an inoperative Refresh control. That explicit Refresh interaction remains a
contract residual for the integration owner.

## Executed checks and exact capture identity

Base checkout HEAD was `7b36cfac2565397191b3df5e07112611e7f1b0e1` with the
concurrent MIDI/layout changes in the shared working tree. Both owned C++
translation units passed `-fsyntax-only` using the native build's actual
`compile_commands.json`: GNU C++ 14.2.0, C++20, Release flags and strict project
warnings including `-Werror`, conversion, sign-conversion and shadow checks.
`git diff --check` passed for the owned implementation and this note.

The integrator completed the coherent linked native build and the one-line
caption rebuild using CMake 4.4.4 at:

```text
/home/agent/.cache/uv/archive-v0/kvsqq5-iHdbf13RC/cmake/data/bin/cmake
```

The actual capture executable was:

```text
/workspace/scratch/cd4bd06ce68f/build-native/apps/standalone/hammond_standalone
```

It includes pinned SDL 2.32.10 and enabled pinned RtMidi 6.0.0 with the prepared
ALSA dependency. The existing local build workaround remains `SDL_ALSA=OFF`;
this is separate from RtMidi's ALSA backend. Captures explicitly used SDL dummy
audio/video and the actual software renderer. No physical device was implied.

| Executed capture | Result | Observed callbacks / frames | Runtime images |
|---|---|---:|---:|
| 1672 × 941, 800 ms smoke | Exit 0, smoke passed | 80 / 40960 | 11 |
| 1280 × 900, 800 ms smoke | Exit 0, smoke passed | 76 / 38912 | 16 |
| 960 × 700, 800 ms smoke | Exit 0, smoke passed | 76 / 38912 | 25 |
| 960 × 700 MIDI modal, 1200 ms replay | Captured; replay **failed** on missing ALSA sequencer | See diagnostics | 29 |

All three smoke diagnostics report the screenshot taken while the UI note was
held, followed by an observed release, with zero reported errors. The original
BMP and byte-preserving PNG encoding are both retained in the scratch capture
folder; PNG encoding did not alter pixel dimensions or RGBA content.

The MIDI replay clicked the real MIDI tablet, traversed port/channel controls
with Tab, changed selected channels to 2/3/4 using Right, and ended with visible
focus on Apply. All 18 replay events were delivered and final acknowledgment was
observed. This computer has no `/dev/snd/seq`, so enumeration reported
`MidiInAlsa::initialize: error creating ALSA sequencer client object.` The modal
correctly displayed that error and `MIDI NOT CONNECTED / ALSA`; the application
returned 1 and explicitly marked the replay failed. This is a visual/error
presentation observation, **not a successful MIDI backend or replay gate**.

An earlier attempt used `key_down M ctrl 0`, which ScriptedInput rejected before
launch because its admitted key vocabulary does not yet include `M`. The
capture record retains that failed attempt and its exact script. Main implements
Ctrl+M, but replay support for the new shortcut is a concrete next integration
task. The successful delivery of the pointer-opened modal does not erase either
failure.

Scratch evidence folder, to be incorporated by the later capture-bundle owner:

```text
/workspace/scratch/cd4bd06ce68f/a17-render-checks/
  capture-record.json
  native-1672x941.bmp / .png / .json
  native-1280x900.bmp / .png / .json
  native-960x700.bmp / .png / .json
  native-960x700-midi.bmp / .png / .json
  midi-modal.b3uireplay
```

`capture-record.json` retains complete commands, both driver selections,
stdout/stderr/exit statuses, dimensions, source hashes, BMP/PNG byte hashes and
RGBA pixel hashes. A representative actual smoke command is:

```sh
SDL_AUDIODRIVER=dummy SDL_VIDEODRIVER=dummy \
  /workspace/scratch/cd4bd06ce68f/build-native/apps/standalone/hammond_standalone \
  --width 1672 --height 941 --smoke-ms 800 \
  --state /workspace/scratch/cd4bd06ce68f/a17-render-checks/native-1672x941.b3controls \
  --screenshot /workspace/scratch/cd4bd06ce68f/a17-render-checks/native-1672x941.bmp \
  --diagnostics /workspace/scratch/cd4bd06ce68f/a17-render-checks/native-1672x941.json
```

| Frozen input/output | SHA-256 |
|---|---|
| `Drawing.h` | `5f338b1fe85be0b2c2766efaf1595931391465f164ec88b56425dc4919ba6e10` |
| `Drawing.cpp` | `4d13a5eb312799b341e44a41f52960e44c04da1a7b05ecfdda86bc635e1ecda9` |
| `InstrumentView.h` preserved MIDI seam | `9a248ce4934990292a2134cad3be9a8b5f9379edd7d821ab4e39214cbe80b819` |
| `InstrumentView.cpp` | `82c7171626f16039ac4877a8cafc12928941d51fb295a37d0f23ac6c294c6e8e` |
| Captured native binary | `072f52ad299592f997af2aaeb2a140a3417e4a77542dd6afbfbae9fd4a60eb4b` |
| Generated `ReferenceArtData.h` | `d94cefd9ad69726c267d4674acd66912f4764ee9f88d1c21ecce4ed7befcbac6` |
| Final 1672 × 941 PNG | `87ce06e8b791cb6041a87c7d4ae211a4f6a46daaa6054f2ff949b75178036755` |
| Final 1280 × 900 PNG | `0460093e4b216a50bfcc856a8d48f56678e7628cd131f3a0b189461cae5543d6` |
| Final 960 × 700 PNG | `bf722384d52ed70e71d8f246a51eee75bd056e6fc312db90543ec4071451f503` |
| MIDI error-state PNG | `668263c830ce88e135257f7781fe6f2407edfa0ae94fd0ca3e6eaa3f741ba352` |

## Visual comparison, limits, and next work

The native captures now reproduce the reference's major composition: walnut
cheeks, brass/charcoal framed panels, centered serif name, light percussion
caps, neighboring drawbar banks, two stacked manuals with left bank rails, and
the right cabinet photograph. No clipped control legend or overlapping control
was observed at the three inspected sizes. At 960 × 700 the cabinet/rails are
absent, and the bank buttons fit in the compact rack rows. The MIDI dialog fits
inside that minimum window and its backend error remains inside the status box.

This is not pixel-identical source reproduction. Procedural controls and keys
are flatter than the source photograph, use rectangular playable planes, and
have less material texture. The DejaVu serif face and small metadata typography
differ from the concept. The admitted 24-pixel left wood strip is scaled to the
layout's cheek width. Actual 61+61+25 inventory, corrected legends and direction,
independent EDIT/SOUNDING controls, visible pedals, nominal expression/mixtures,
and factual device status intentionally replace inaccurate or unavailable source
features. Default/minimum layouts intentionally omit the cabinet.

The minimum MIDI capture also exposes a specific typography residual: some
thin glyph strokes disappear in the small secondary instructions and footer
when the cached font atlas is downscaled by the software renderer. Main modal
controls and channel readouts remain clear. A21/A29 should review those small
sizes and font sampling; this capture does not establish a complete text-legibility
pass.

The retained font atlas still covers printable ASCII only. Non-ASCII backend
names have the existing glyph limitation; unusually long names/errors are
wrapped then visibly elided, with `--list-midi` identified for exact full port
names. Full native Unicode and an in-modal full-name inspection affordance
remain separate interface work. Forced texture-allocation/upload failure and
live renderer-reset recovery were source-reviewed but not injected in this
bounded pass. Native screen-reader semantics, physical controller/device
operation, exhaustive gesture/resize transitions, performance qualification,
and physical/acoustic fidelity remain unqualified here.

Next: A21 independently compares the actual captures and interaction geometry;
A28 retains a durable source-identified capture bundle. The integration owner
should add replay `M` coverage and decide the explicit Refresh/full-port-name
interaction, then execute the combined native controls, mixed ownership,
resize/focus and recovery gates from one coherent source snapshot.
