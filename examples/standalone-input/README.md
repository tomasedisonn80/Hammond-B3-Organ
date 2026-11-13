# Standalone input examples

These three small `B3UIREPLAY1` files send timed events through the standalone
application's own SDL queue. They operate the real UI, Session and audio
callback. They do not send global desktop keystrokes or provide sample-accurate
musical timing. See [workflow acceptance](../../docs/STANDALONE_WORKFLOWS.md)
and [the native application](../../docs/STANDALONE_APP.md).

| File | Visible workflow |
| --- | --- |
| [keyboard-notes.b3ui](keyboard-notes.b3ui) | Hold Upper C4 while new keys target Lower D5 and pedal 17; change target again, then release each original note. |
| [audio-settings.b3ui](audio-settings.b3ui) | Open Audio by keyboard, choose 96000 Hz / 128 frames, Apply, and play again after releasing the suppressed original key. |
| [save-controls.b3ui](save-controls.b3ui) | At the default 1280x900 layout, edit Upper B's first drawbar, Ctrl+S, change it, and Ctrl+O from the same selected state file. |

## Run an example

Build `hammond_standalone` with the pinned SDL dependency first. From the
repository root, this command uses explicitly selected dummy drivers and a
private directory; the replay exits at its declared duration after acknowledgment:

```sh
work=$(mktemp -d)
SDL_AUDIODRIVER=dummy SDL_VIDEODRIVER=dummy \
  build-native/apps/standalone/hammond_standalone \
  --state "$work/controls.b3controls" \
  --input-script examples/standalone-input/keyboard-notes.b3ui \
  --diagnostics "$work/keyboard.json"
```

Choose another listed script to run that workflow. Save/Load always uses the
explicit `--state` path. `save-controls.b3ui` intentionally writes that file,
then loads it; it leaves A held so normal application shutdown performs the
final release. Other examples do not save. A missing state starts the app's
proposed audition registration; an existing valid file supplies its controls.

The Audio example requests an actual device restart. Its 96000 Hz / 128-frame
choice is part of this engineering workflow, not a physical-device recommendation.
Dummy output is silent and establishes no physical latency, pointer-capture,
native accessibility or acoustic-fidelity qualification.

## Format

The first two physical lines are `B3UIREPLAY1` and `duration_ms N`, where
`N` is 250 through 10000. Later blank lines and full-line `#` comments are
allowed. Each event starts with a nondecreasing integer millisecond timestamp
strictly before the duration; tied events retain file order. Files are bounded
to 64 KiB and 256 events. LF and CRLF are accepted; inline comments are not.

Events are `key_down KEY MODIFIERS REPEAT`, `key_up KEY MODIFIERS`,
`mouse_down X Y`, `mouse_move X Y`, `mouse_up X Y`, `resize W H`,
`focus_lost`, or `quit`. The repeat value is `0` or `1`; modifiers are `none`
or distinct `shift`, `ctrl`, `alt`, `meta` names joined with `+`. Key names
are case sensitive: the app's physical playing keys and navigation keys use
names such as `A`, `F2`, `RightBracket`, `Tab`, `Return`, `Comma`, and `Slash`.
Pointer positions use logical window units and may be outside the window.
Resize changes the real window within its supported 960x700 through 8192x8192
limits. `--input-script` and `--smoke-ms` are mutually exclusive.
An explicit early `quit` interrupts replay and returns nonzero; these examples
instead finish automatically at the declared duration after acknowledgment.
