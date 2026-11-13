# Standalone UI state, input and layout contract

Contract identity: **`standalone-dry-ui-v1`**. The declaration surface is
[`apps/standalone/UiModel.h`](../apps/standalone/UiModel.h). This document freezes
the next implementation task; it does not claim that a renderer or input model
has been implemented or executed. The [standalone scope](STANDALONE_SCOPE.md)
and [`Session.h`](../apps/standalone/Session.h) own the surrounding product and
audio lifecycle boundaries.

The interface is SDK-free C++20, using fixed-capacity values. The main thread
owns `UiModel`, layout, display, input capture and files. Rendering reads its
copied view; it never enters a live Engine. The active product label is
**NOMINAL DRY ORGAN**. There are no working scanner, AO-28, rotary, room,
microphone, physical-expression or fixed-chapel-preset controls in this slice.
The initial musical settings remain the core defaults, including muted manual
and pedal drawbars; no arbitrary sounding preset is installed by opening a view.

## 1. Retained controls and visible identities

The UI exposes all **45 current parameter identities** through the same
[`ParameterBridge`](../src/ParameterBridge.cpp) laws. It displays nine manual
drawbars per manual, **18 visible at once**, while preserving all **36** retained
manual positions. Two separate pedal mixture controls bring the retained
drawbar total to 38. Editor selection, Cancel, Panic, notes, files and device
choices do not add parameter identities.

| Retained identity | Permanent IDs | Actual semantics |
| --- | --- | --- |
| Upper A drawbars | 4096–4104 | Nine integer positions 0–8 |
| Upper B drawbars | 4112–4120 | Nine independent integer positions 0–8 |
| Lower A drawbars | 4128–4136 | Nine independent integer positions 0–8 |
| Lower B drawbars | 4144–4152 | Nine independent integer positions 0–8 |
| Global expression | 8192 | Finite 0–1 normalized linear-gain surrogate |
| Upper/lower sounding bank | 8208, 8209 | 0=A, 1=B; selection reconnects that manual |
| Percussion enable | 12288 | 0=Off, 1=On |
| Percussion harmonic | 12289 | 0=Second, 1=Third |
| Percussion volume | 12290 | 0=Normal, 1=Soft |
| Percussion decay | 12291 | 0=Slow, 1=Fast |
| Pedal mixtures 1/2 | 16384, 16385 | Independent nominal mixture positions 0–8 |

Footage order is `16'`, `5 1/3'`, `8'`, `4'`, `2 2/3'`, `2'`, `1 3/5'`,
`1 1/3'`, `1'`. A full drawbar label identifies manual, bank, footage and
integer position. The pedal labels are **Nominal mixture 1/2**, not calibrated
16-foot/8-foot responses. Expression is **Nominal expression / gain**, not a
measured mechanical-pedal law. Registry IDs have holes: array position is not
an ID, and the atlas's proposed registry must not replace this table.

Use `parameter_descriptor`, `plain_to_normalized` and `normalized_to_event`
when resolving a parameter; do not introduce a second rounding rule. Discrete
normalized half thresholds choose the higher position. The UI draft may use a
local `ControlState`, with its existing validation and mutation semantics,
before emitting a complete copied `ControlSnapshot`. The UI never changes
source phase, percussion readiness or a live note ledger when editing controls.

Each manual displays **EDIT A/B** and **SOUNDING A/B** independently. EDIT changes
only `edited_banks`, the nine bindings and the inactive-bank summary. It emits
no musical action. SOUNDING selects a retained bank and sets the route enabled,
including reselecting the same bank after Cancel. The SOUNDING label comes from
the applied Session snapshot; pending desired changes carry a separate PENDING
mark. Cancel displays **SOUNDING CANCELLED — retained A/B** while retaining the
selection and all positions. It disables only that manual's route and preserves
held notes, the other manual and pedals. Panic clears all note owners while
preserving controls; it is visibly separate from the two Cancel buttons.

Percussion settings remain editable and visibly retained while ineligible.
Show **Requires sounding upper B** unless the applied upper route is enabled
and B is selected. When enabled and eligible, explain **Upper B 1' sustain is
suppressed** without moving its saved drawbar. Do not invent a recharge meter
or a measured decay time. These rules follow
[`ControlState`](../src/ControlState.cpp), [`Types.h`](../include/hammond/Types.h)
and [`Percussion.h`](../include/hammond/Percussion.h).

## 2. The action and acknowledgment boundary

`UiActions` contains at most four `UiAction` values. Each is either the exact
`SessionCommand` variant or an app request for Save, Load, Audio Settings or
Help. One ordinary event produces zero or one action; pointer glissando produces
two, **Off followed by On**. No event may silently truncate a batch. These bounds
leave capacity for a recovery action without an unbounded UI queue.

Dispatch the batch synchronously and in array order. Pass every Session command
to `Session::post`, then immediately pass its `SubmitResult` to
`UiModel::submitted`. On rejection, stop the original batch and dispatch only the
returned recovery action. Do not continue a glissando On after its Off failed.
Do not retry a full queue in a loop or coalesce note transitions. All input
offsets are zero: they request the next callback boundary, without a claim of
sample-accurate keyboard or hardware-MIDI acquisition.

An accepted whole control snapshot records its sequence. The desired display
stays PENDING until an applied snapshot resolves that sequence. The Session
snapshot supplies authoritative controls, held keys/pedals, state and recovery
counters; observation never echoes a control action. On a new recovery count,
discard stale desired/held gesture state, adopt applied controls and retain a
visible recovery indication. Session's overflow recovery is global, whereas
ordinary `ReleaseUiNotes` is scoped to UI channel 0. An `InvalidCommand` rejects
without automatic panic; the UI requests one `ReleaseUiNotes` and reports the
bug. Failure of that request does not create a retry loop.

`load_controls` accepts only a fully valid copied snapshot, emits one command
and keeps editor selection and note ownership independent. Off-thread parsing
uses the existing strict `B3CONTROLS3` format and its supported migrations.
Saved files contain all banks, selectors, route flags, percussion, expression
and pedals; they contain no held notes, focus, octave, geometry or DSP history.
`mark_saved` receives the exact successfully written copy, so a later change
cannot accidentally be marked clean. Save/load/device requests execute outside
the callback. Opening a modal window must use the ordinary UI focus-loss path
when the app loses performance focus; loading controls itself is not a note-off.

## 3. Performance ownership and input recovery

The visible manuals contain **61 playing keys each**, MIDI **36–96** inclusive.
There is no decorative reversed octave counted as playing keys. The pedalboard
contains **25** keys with explicit one-based `PedalId` **1–25**; pedal IDs are
not manual MIDI notes, tone-source numbers or storage indices. Both full manuals
and all pedals remain visible at the supported sizes.

The UI uses Session's reserved channel 0. Manual origin bus 0 is Upper and bus 1
is Lower, with no UI bus remapping. Pedals use pedal origin bus 0; its namespace
is independent. Computer-key owner IDs are `1 + chromatic key slot` (1–17), the
primary pointer is 100 and the focused-note Space audition is 101. They are
identified positive-velocity events, not anonymous FIFO owners. Velocity 127
means a full press; it is not a sustained loudness control in this core.

Every successful press stores its **original target, MIDI note or PedalId, and
owner ID**. Release derives its full bus/channel/note/ID from that record. It
never uses the current manual, octave, focus, editor bank or pointer position.
Keyboard and pointer owners can overlap on one physical note; releasing one
must leave the other held. The combined core ownership adapters, not a Boolean
UI key flag, determine the final physical release.

| Input | Frozen behavior |
| --- | --- |
| Computer-key Down | Ignore OS repeat and duplicate Down, even if repeat metadata is missing. Capture the current valid target and note once. |
| Computer-key Up | Release its original record before checking text-entry, modifiers, focus or shortcut gates. Unmatched Up is a no-op. |
| Manual/octave change while held | Affects future presses only; original holds stay sounding until their matching Up. |
| Pointer Down on a key | Request OS capture and press one owned note. v1 supports one primary mouse pointer. |
| Captured movement to a different key | Release the pointer's old note before pressing the new one; crossing manuals or pedals is allowed. |
| Captured movement outside all playing keys | Release the pointer's note, keep capture until Up, and permit re-entry to press again. Moving over a button does not activate it. |
| Pointer Up outside the window | Release the stored pointer note and end capture. The app must forward the event. |
| Capture loss/failure | Release only the pointer note and close any drag; keyboard owners remain. Require a new pointer Down. |
| Internal focus movement | Changes focus only; it neither presses nor releases notes. |
| Resize | Changes rectangles and closes a parameter drag; preserves captured note identities and focus. It emits no musical action. |
| Window deactivation/close, Escape | End gestures and issue `ReleaseUiNotes` across both manual buses and pedal origins, channel 0 only. |
| Panic button | Issue Session `Panic`, clear local note/capture records and suppress held input until release. |
| Transport recovery | Clear local records; suppress every still-down physical input until Up. Adopt the recovered snapshot; never automatically replay notes. |

The app must deliver `CaptureLost` if OS capture fails. After focus returns it
may use the backend's observed physical state to send Up for keys actually
released while unfocused; it must not synthesize Down or resurrect owners.
An Escape recovery is separate from Cancel; neither silently selects a bank.
An eventual external-MIDI backend can use other channels, but no MIDI-device
transport or multi-touch support is implemented or claimed by this contract.

## 4. Keyboard operation and visible focus

Tab/Shift+Tab move through control groups in reading order: top actions, upper
registration controls, lower registration controls, percussion/expression/pedal
mixtures, keyboard target/octave, Upper manual, Lower manual, pedalboard. Every
non-key control is reachable. Each manual and the pedalboard have one Tab entry,
with a retained roving focused key. Focus is outlined in cyan with a geometric
border; held keys, selected buttons, EDIT and SOUNDING use distinct labels and
shapes, rather than a shared color-only cue.

Inside a manual or pedalboard, Left/Right moves the focus by one semitone,
Up/Down by an octave, and Home/End goes to the first/last note, with clamping.
Navigation does not sound a note. Space Down explicitly auditions the focused
note with owner 101; Space Up releases the original audition even if focus has
moved. Enter/Space activates focused buttons; repeats are ignored. A visible
footer names the focused manual/note or pedal ID and states its available action.

For drawbars, Up/Right adds **one integer position**, Down/Left subtracts one,
and Home/End chooses 0/8. Shift does not invent fractional drawbar positions.
Expression uses 0.05 per arrow, Shift+Arrow 0.01, and Home/End 0/1; all values
are clamped, finite and displayed as nominal gain. Buttons expose both their
name and state, including percussion's Second/Third, Normal/Soft and Slow/Fast.

Computer playing keys are physical US-position scancodes in chromatic order:

| Semitone | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Key | A | W | S | E | D | F | T | G | Y | H | U | J | K | O | L | P | ; |

F1/F2/F3 select Upper/Lower/Pedals for future computer-key presses. Brackets
lower/raise the current target's octave. Manual base starts at MIDI 60, ranges
36–84 in steps of 12, and is shared between manual targets. Pedals use
`1 + 12 * pedal_octave + semitone`, octave 0–2. A derived value beyond the
instrument's range is ignored, never wrapped or clamped to a duplicate note.
The toolbar displays target and base note/ID; local keyboard labels may describe
the actual keyboard layout without changing physical identity. Control/Alt/Meta
chords and active text entry suppress new performance shortcuts. Releases
always remain active. Text-entry contexts also suppress navigation shortcuts
owned by the text field. This custom canvas contract does **not** supply a
native accessibility tree or establish screen-reader/assistive qualification.

## 5. Geometry, scaling and gesture identity

Reference logical window size is **1280 × 900**; supported minimum is
**960 × 700**, with each dimension at most **8192** logical units. The app enforces
these bounds. `make_ui_layout` rejects nonfinite, smaller or larger dimensions
without changing its destination. Rendering and input
share `UiLayout`; no independently reconstructed keyboard is permitted.
Coordinates are logical window units. SDL window/pointer coordinates must be
converted once into that domain, while the renderer maps once to drawable
pixels for high DPI. Do not double-apply drawable scaling.

Use a walnut frame, charcoal `#242725` opaque label surfaces, ivory `#F2E7CF`,
brass `#D6B67C` accents and cyan `#A5E4DF` focus. Walnut `#553624` is an original
UI token, not measured wood. Keep text separate from decoration; no asset or
font is introduced by this contract. A separately admitted, licensed prebuilt
glyph atlas will supply text. No runtime font dependency is required here.

The layout uses margin 24 at widths at least 1120, otherwise 16; inter-section
gap 12; header height 56; keyboard toolbar 32; footer 40. At heights at least
820 the rack is 248 high and pedals 112; otherwise they are 208 and 88. The
remaining height, after six gaps, is split evenly between the two manuals.
The rack contains upper and lower registration panels side by side, followed
by a performance panel 288 wide at widths at least 1120, otherwise 236. The
two registration panels share the remaining width with two gaps of 12.
This yields manual panel heights 146 at the reference size and 86 at minimum.
Each contains a readable name strip and its complete keyboard. Within the rack,
adapt labels and fraction line breaks before reducing text size or hiding keys.
All ordinary buttons target at least 32 logical units in height; the dense
playing keys have the roving-focus/Space alternative. These are layout targets,
not an executed contrast, scaling or accessibility pass.

All rectangles are half-open: left/top belongs, right/bottom does not. Draw
natural keys first and accidental keys last; hit-test accidentals before
naturals. Adjacent edges must not trigger two notes. Manual keys use the
chromatic C-to-C pattern (36 naturals/25 accidentals); the pedalboard uses
15 naturals/10 accidentals. Decorations do not change hit regions.

At parameter pointer-down, capture the permanent control identity and the
current track. A vertical drawbar's 0 endpoint is top and 8 is bottom, toward
the player; expression uses its labeled 0-to-1 track. Quantization uses the
existing bridge. Keep the captured bank while dragging. Changing the edited
bank, resizing, losing capture or closing the window ends that gesture before
rebinding; later motion cannot edit the newly visible control until a fresh
Down. A model/UI snapshot update must not begin a gesture. No pointer release
is inferred from merely leaving a slider rectangle while OS capture remains.

## 6. Next implementation and acceptance

Implement `UiModel.cpp` against these declarations, then the SDL translator and
renderer against the same geometry. Keep callback ownership and transport in
Session. The initial acceptance must independently check:

1. Every parameter ID/label/range, all four retained banks and the 18 visible
   drawbars; inactive editing, selection, Cancel and upper-B percussion rules.
2. Original-key release after target, octave and focus changes; repeat/duplicate
   rejection; overlapping owners; Space audition; text entry; pedal IDs 1–25.
3. Captured off-window release, failure/loss, glissando Off/On ordering,
   bank change mid-drag, resize and scoped focus recovery.
4. Rejection between glissando actions, overflow/global recovery, suppression
   until physical Up, and coherent PENDING/applied state without echo commands.
5. Half-open edges and accidental precedence using the real shared layout;
   actual executable screenshots and input at 1280×900 and 960×700, plus a named
   high-DPI case. Inspect clipping, all key counts, labels and visible focus.
6. Keyboard reachability, actual save/load round trips, malformed-load
   preservation and actual app requests outside the callback.

The source basis is atlas PDF pp. 397–402, 409–420 and 433–438, reconciled with
the real core by [assignment 05](development/2026-11-13-next-phases/05-atlas-product.md)
and [assignment 06](development/2026-11-13-next-phases/06-atlas-closure.md).
Atlas continuous drawbars, 62 parameters, additional preset keys and cabinet
features are proposals or later models; they do not redefine this dry product.
Native accessibility, physical-device latency, musician usability, physical
fidelity and signed distribution each require their own retained evidence.
