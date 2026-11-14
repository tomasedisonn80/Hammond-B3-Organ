# Bounded standalone input replay

`--input-script PATH` reproduces native UI workflows through the application's
SDL event loop. It is mutually exclusive with `--smoke-ms`. This is wall-clock
UI scheduling, not a musical sample timeline or an audio oracle. The optional
SDL layer leaves the core, public controls and saved-state format unchanged.

## Exact file grammar

The first physical line is exactly `B3UIREPLAY1`; the second is `duration_ms N`,
where N is an integer from 250 through 10000. Leading/trailing spaces or tabs
are allowed on the second line and subsequent records, but not the header.
Use printable ASCII with tabs and LF or CRLF; a final newline is optional.
After the first two lines, blank lines and full-line comments beginning with
`#` after optional horizontal whitespace are ignored. Inline comments fail.

Files contain at most 65536 bytes and 256 action records. Every event begins
with an integer millisecond offset `T`, where `0 <= T < N`. Times must be
nondecreasing; equal times preserve source order. Decimal integer fields allow
leading zeroes; leading `+`, fractional, exponent and nonfinite values fail.
Negative coordinates are allowed; negative time, duration and sizes fail.

| Record after T | Meaning and bounds |
| --- | --- |
| `key_down KEY MODIFIERS REPEAT` | Physical key press; REPEAT is exactly `0` or `1`. |
| `key_up KEY MODIFIERS` | Physical key release; repeat is always false. |
| `mouse_down X Y` | Left-button press at integer logical window coordinates. |
| `mouse_move X Y` | Pointer motion at integer logical window coordinates. |
| `mouse_up X Y` | Left-button release, including outside the window. |
| `resize W H` | Request actual SDL window size; W=960..8192, H=700..8192. |
| `focus_lost` | Queue this window's `SDL_WINDOWEVENT_FOCUS_LOST`. |
| `quit` | Queue `SDL_QUIT` through the ordinary shutdown path. |

Coordinates X and Y each range from -8192 through 16384. KEY is case-sensitive:
`A W S E D F T G Y H U J K O L P M Semicolon Tab Left Right Up Down Home End
Space Return Escape LeftBracket RightBracket F1 F2 F3 F4 F5 F6 F7 Comma Slash`.
MODIFIERS is `none` or `+`-joined `shift`, `ctrl`, `alt`, `meta` in any order,
without duplicates or empty components. The adapter sets canonical left-side
modifier bits and consistent physical scancodes/unshifted US keycodes. It does
not send modifier-key events, OS keystrokes, or change global SDL key state.

F4/F5/F6 select Play/Rotary/Service, and F7 toggles Dimensional/Flat. These
presentation shortcuts have the same repeat, physical-release, modifier and
modal gates as native keyboard input. They leave sound controls and held owners
unchanged. F1/F2/F3, octave shortcuts and computer-piano keys remain available
in every workspace. `M` admits the established Ctrl/Command+M MIDI shortcut.
The optional `--workspace play|rotary|service` and `--flat` switches select the
initial presentation before device startup; invalid values fail during CLI
admission. The default is Play/Dimensional.

```text
B3UIREPLAY1
duration_ms 1000
# Open and close Help; then release a playing note on focus loss.
0 key_down Slash shift 0
5 key_up Slash shift
100 key_down Escape none 0
105 key_up Escape none
200 key_down A none 0
400 focus_lost
410 key_up A none
500 resize 960 700
```

Unknown, repeated header/duration, partial, trailing, unsorted, out-of-range,
oversized and invalid-character input fails transactionally. Parsing/loading
preserves the caller's destination plan on failure. Loading opens and inspects
the same native file handle, rejecting symbolic/reparse leaves, directories,
FIFOs/devices and growth beyond the byte limit. Parent-directory symlinks are
not forbidden. Loading runs before the event loop; plans own a fixed array.

## Main-thread execution contract

`ScriptedInput::initialize(plan, window, error)` validates even caller-created
plans, copies the plan and registers a unique SDL event type. Failed or repeated
initialization preserves the existing helper. The live window must outlive it.
`pump(elapsed_ms, error)` posts a bounded due prefix once, in order. Equal
elapsed values are allowed; decreasing elapsed time fails permanently. A
filtered or refused SDL push also fails permanently; no prefix is retried.

Pass every polled event to `acknowledge(event)` before normal dispatch. It
consumes this helper's markers only. Resizing first requires a marker proving
the preceding prefix was consumed; the helper then calls `SDL_SetWindowSize`,
queries `SDL_GetWindowSize`, queues those actual dimensions, and waits for a
second marker before later actions. This preserves geometry order across tied
resizes and SDL's native resize-event coalescing. Native size notifications can
also occur. Actual dimensions may reflect window-manager constraints.

The final marker follows the last accepted action immediately, even before
the requested duration. `delivered()` becomes true when `acknowledge` consumes it;
an empty plan is delivered at initialization. `completed(elapsed_ms)` also
requires the duration to elapse and no failure. Counts describe script actions,
excluding markers and SDL-generated notifications; resize counts after its
explicit event push succeeds. A resize can already have changed the window if
that push fails. The application separately waits for Session acknowledgment
and enforces bounded shutdown/grace. Delivery alone proves neither of those.

Motion state reflects the script's last left-button down/up; its relative
coordinates use the previous mouse record, or zero when none exists. Focus
loss clears the synthetic held button but preserves its last coordinate.
These values do not change SDL's global mouse state or OS capture behavior.
Dummy-backend capture failure exercises failure/release handling only. Physical
mouse capture, real device timing, accessibility, cross-platform execution and
acoustic fidelity need separate evidence. See the [assignment note](development/2026-11-13-next-phases/26-input-replay.md).

## Presentation and inspection observations

Diagnostics retain schema version 3 and all existing musical replay semantics.
The separate top-level `presentation` object records `initial_workspace` and
`initial_presentation`, plus `last_painted`, `screenshot`, `before_shutdown` and
up to 512 transition `observations`. A frame record contains its elapsed time,
one-based rendered-image number, workspace (`play|rotary|service`), presentation
(`dimensional|flat`), overlay, logical window dimensions and copied inspection
status. Absent painted/captured records are JSON null. `screenshot` is set only
after a BMP succeeds; `before_shutdown` freezes the last successfully flushed
frame before ordinary note/device cleanup. The later joined Session snapshot
does not replace these records.

`inspection` records whether any Session copy is available, whether the latest
actual snapshot read succeeded, the document's snapshot state
(`unavailable|unprepared|retained|stopped|current`), pending controls, copied frame
clock and publication revision. A failed read retains the preceding copied
state and marks it retained when prepared. The document is rebuilt each frame
from the loaded profile, UiViewState and those two read flags, without Engine
access or a second device query.

History retains the first painted frame and changes to workspace, presentation,
overlay, size, snapshot status or pending status. It omits clock-only changes;
it is neither a musical timeline nor every frame. `observations_truncated`
signals a full history without changing playback, shutdown deadlines or the
exact latest/captured records. Several events consumed before one paint may
therefore appear as one resulting frame, not as unpainted intermediate views.
