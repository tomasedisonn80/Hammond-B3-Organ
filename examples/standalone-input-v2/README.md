# Standalone input examples — reference-player layout

These active workflow fixtures use the current native reference-player layout.
The `v2` directory identifies this fixture edition; the input format remains
`B3UIREPLAY1`, and saved musical controls remain `B3CONTROLS3`.
The [original input examples](../standalone-input/README.md), their bytes, and
the historical native demo captures/provenance remain unchanged.

| File | Real application workflow |
| --- | --- |
| [keyboard-notes.b3ui](keyboard-notes.b3ui) | Hold Upper C4, Lower D5 and pedal 17 under their original owners, then release them after target/octave changes. This is a byte-identical copy of the original fixture. |
| [audio-settings.b3ui](audio-settings.b3ui) | Open Audio, choose 96000 Hz / 128 frames, Apply, and play after releasing the suppressed original key. This is a byte-identical copy of the original fixture. |
| [save-controls.b3ui](save-controls.b3ui) | Click Upper EDIT B at `(130,508)` in the default 1280×900 manual cheek, Tab four times to its first drawbar, then edit, save, change and reload while C4 remains held. Only this fixture's pointer coordinates and explanatory comment changed. |

After building the native app with the pinned SDL dependency, run from the
repository root with a private state path:

```sh
work=$(mktemp -d)
SDL_AUDIODRIVER=dummy SDL_VIDEODRIVER=dummy \
  build-native/apps/standalone/hammond_standalone \
  --state "$work/controls.b3controls" \
  --input-script examples/standalone-input-v2/keyboard-notes.b3ui \
  --diagnostics "$work/keyboard.json"
```

Choose the other listed script for its workflow. `save-controls.b3ui` explicitly
writes the selected state file and leaves C4 held until normal joined shutdown;
the other fixtures do not save. These scripts select no MIDI port and do not
initialize a hardware input. A backend-enabled or backend-disabled build must
report an inactive MIDI source with zero input/lifecycle counters.

The [native workflow acceptance](../../docs/STANDALONE_WORKFLOWS.md) keeps its
literal expected controls, canonical saved bytes, original note owners,
acknowledged command prefixes and pre-shutdown holds. The
[layout/schema reconciliation record](../../docs/development/2026-11-14-midi-ui/25-legacy-native-acceptance.md)
identifies the changed geometry and exact checks. SDL dummy drivers exercise
software event delivery and rendering; they establish no physical MIDI, audio
device, latency, native accessibility or acoustic-fidelity qualification.
