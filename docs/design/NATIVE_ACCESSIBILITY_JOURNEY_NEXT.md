# Next native display, input and accessibility journey

**Planning specification, 16 November 2026; no journey executed here.** A42
inspected published implementation `af2b74760ee195c9497b314a1a29172f5238dd44`
(tree `fb7d9ef7d1fcf24a70395c0671b75eb9c31558d4`) and retained evidence. This
work opened no application, browser, OS session, display, audio or MIDI device,
and ran no build or device test. Its [source/integrity receipt](../development/2026-11-15-streaming-continuation/reports/A42-source-audit.json)
identifies the inspected bytes. Hosted jobs were in progress when assigned;
their outcome does not substitute for this journey.

This is an executable operator sequence and a bounded next implementation brief,
not a new acceptance authority or an accessibility pass. The
[native interaction contract](../REFERENCE_REFINEMENT_DESKTOP.md),
[workspace contract](../INTERFACE_WORKSPACE_CONTRACT.md),
[current operator guide](../INTERFACE_RUNBOOK.md) and full
[M0–M9 plan](../PLAN.md) retain their requirements. Preserve 147 playing keys
(61 Upper, 61 Lower, 25 pedals), 24 presets, four retained banks, 68 ordinary
controls, 47 sound parameter identities, state4/readers 1–3 and original note
owners. Literal whole-interface 1:1 remains unmet.

## 1. What exists, and what still needs observation

| Boundary | Current source or retained evidence | Consequence for the next operator |
| --- | --- | --- |
| Native semantic bridge | `UiControlId`, focus, values and actions are internal C++ canvas data. The standalone target links its SDL drawing/input/audio/support components; inspection found no native accessibility provider, platform role/value/action export or accessibility-event publication. | Do not call the current UI screen-reader accessible. First inspect the native tree on the assigned OS and retain the actual result, including an empty/client-only tree. An OS-provided window name is not the instrument control inventory. |
| Visual and keyboard state | `InstrumentView.cpp` paints names, values, focus and status; `UiModel.cpp` owns keyboard/pointer behavior. | Painted cyan focus and a readable footer are visual evidence, not an exported focused accessible object. Keyboard operation can be qualified separately. |
| DPI | `main.cpp` creates a resizable `SDL_WINDOW_ALLOW_HIGHDPI` window, reads logical window and renderer-output sizes, applies their ratio with `SDL_RenderSetScale`, and handles size/display changes. Pointer coordinates enter the model as window coordinates. | Observe the actual logical-to-drawable mapping and hit alignment on each display. Neither the flag nor a scaled raster fixture proves OS behavior. |
| Reduced motion | The inspected UI exposes Dimensional/Flat and immediate view changes. No explicit reduced-motion option or OS preference query was found. Rendering also updates live counters/meters. | Exercise Flat and actual system reduced-motion settings separately. Do not invent a `--reduced-motion` flag or claim automatic preference support. Record motion, changing readouts and focus behavior actually observed. |
| Numeric entry | MIDI channels/endpoints and audio choices are painted controls operated with arrows, Home/End and activation. No `SDL_TEXTINPUT` handler or native numeric text field was found. | Test the existing value controls. Typing digits is not a supported numeric-entry workflow. Any later text field needs its own input/commit/cancel and release contract. |
| Current gallery | The [twelve-frame Upper-rack gallery](../../examples/demos/upper-rack-material-v1/README.md) uses executable SHA-256 `c29495e98148767c0d55cab4adc18a245659cea891deb0f37fa160ea976c3cc1`, dummy video/audio and MIDI OFF. | Use it as the current composition/state reference. Preserve its original source overlay and pixel identities; a new native-backend executable needs its own identity. |
| Earlier OS input | The [retained X11 review](../reviews/REFERENCE_REFINEMENT_NATIVE_INPUT.md) qualifies executable `6eea84ba830ea8710b550c14561b4dd887bea8aac489fa82a467e3708e071b13`. It observed a keyboard-held pedal across one resize and ordinary captured pointer in/out motion, but not the complete pre-held navigation/suppression journey. | Retain those bounded results. They do not qualify the current binary, DPI, semantic accessibility or the missing pointer-held resize/return/fresh-press sequence. The old bundle lacks per-step lossless desktop frames and a separate numeric exit receipt. |

Source anchors: [`UiModel.h`](../../apps/standalone/UiModel.h),
[`UiModel.cpp`](../../apps/standalone/UiModel.cpp) (`move_tab_focus`, `key`,
`pointer`, `resize`, `set_workspace`, `set_presentation`),
[`main.cpp`](../../apps/standalone/main.cpp) (`resize`, `handle_event`,
`open_overlay`, `modal_key`, `record_painted_presentation`),
[`InstrumentView.cpp`](../../apps/standalone/InstrumentView.cpp)
(`focused_control_caption`) and
[`standalone CMake`](../../apps/standalone/CMakeLists.txt). Internal use of the
word “semantic” does not itself implement a native accessibility bridge.

## 2. Reserve one actual machine and an identified build

Root assigns the build/display owner and freezes the intended source. Use the
[normal desktop recipe](../../README.md#build-and-launch-the-native-application)
and [platform setup](../MIDI_EXPRESSION_GUIDE.md#build-the-native-application):
SDL 2.32.10; RtMidi 6.0.0 only if physical MIDI is included. Preserve the
current coordinated dummy build. Its X11/Wayland and native audio backends are
disabled and it cannot become display evidence by changing an environment
variable. Prepare a separately assigned native configuration with the normal
backends, rather than copying the dummy recovery flags.

Before launch, retain commit/tree plus any overlay inventory, dependency and
executable SHA-256, build/configuration/toolchain, exact argv/environment,
starting state bytes, UTC times, OS/version, desktop/window manager, video
backend/renderer, display model/resolution/refresh/scaling and keyboard/pointer
identities. Record audio driver/device or explicitly dummy audio; MIDI OFF or
No input is a valid display-only scope. A real MIDI connection is a separate
extension, not an implicit prerequisite for the keyboard journey.

For an already prepared Linux/macOS native build, this ordinary launch uses a
new output directory and a copy of the current gallery's registration. Run it
from an actual desktop terminal; substitute the assigned executable path:

```sh
journey_app="$PWD/build-native-midi/apps/standalone/hammond_standalone"
journey_dir="$PWD/out/native-journey-01"
mkdir -p out
mkdir "$journey_dir"
cp examples/demos/upper-rack-material-v1/inputs/controls.b3controls "$journey_dir/controls.b3controls"
sha256sum "$journey_app" "$journey_dir/controls.b3controls" > "$journey_dir/start-sha256.txt"
"$journey_app" --state "$journey_dir/controls.b3controls" \
  --width 1672 --height 941 --workspace play \
  --diagnostics "$journey_dir/diagnostics.json" \
  > "$journey_dir/stdout.txt" 2> "$journey_dir/stderr.txt"
journey_exit=$?
printf '%s\n' "$journey_exit" > "$journey_dir/exit-code.txt"
```

On a host without `sha256sum`, use its actual SHA-256 utility and record the
command. The [platform guide](../MIDI_EXPRESSION_GUIDE.md) supplies Windows
multi-configuration paths; record `$LASTEXITCODE` immediately after the app
there. Use fresh directories for repeat runs and stop if the chosen directory
already exists. Keep replay and smoke options absent. If supervision terminates
the app, retain the signal/timeout result separately; it is not ordinary close.

The optional `--screenshot` writes one eligible application BMP. In this ordinary
launch it is a startup frame, not a per-step recorder. Capture lossless OS desktop
frames separately after each marked action, without changing focus while a hold
is under observation. A capture method that deactivates the app changes the
journey and must be recorded. Do not substitute `SDL_PushEvent`, a dummy capture
or a released atomic-drag endpoint for actual press/hold/move/release evidence.

## 3. Display and DPI configurations to record

These are proposed observation configurations, not additional numerical release
thresholds. Use the real OS setting, record the actual available mode, and mark
unavailable rows blocked. A desktop must accommodate the entire client plus
window decoration; a full app BMP does not prove the window fits the display.

| Run | Native configuration and client sizes | Exact observations to retain |
| --- | --- | --- |
| D1: baseline | One native display at 100% where available; 1672×941, 1400×820, 1280×900 and 960×700 logical clients. | Full desktop and client, visible edges/close control, all manuals/pedals/presets, small footage fractions, 0–8 ticks/values, EDIT/SOUNDING, pending/unsaved and model-limit labels, focus at both ends of each group. |
| D2: fractional scale | A real 125% or 150% OS scale if supported, with sufficient work area; repeat reference and minimum clients. | Requested/actual OS scale, actual logical and drawable dimensions and ratio, glyph clipping/blur, focus stroke continuity, accidental/natural hit boundaries and drawbar endpoints. Record any compositor scaling that differs from the requested ratio. |
| D3: dense display | A real 200%/high-density display mode where available; repeat reference and minimum clients. | The same values and actions remain reachable; pointer and paint agree after scaling exactly once. Retain OS and app pixel dimensions independently. |
| D4: layout branches | Cross 1399↔1400 width at height 820, and 819↔820 height at width 1400; also 1672×941↔960×700. | The canonical composition activates only with both thresholds in Dimensional Play. Record before/after focus identity, moved toolbar/pedals, and held-note observations from J2/J3. |
| D5: display transfer | If two displays with different scales exist, move the running window between them in both directions, then repeat a fresh key/slider hit. | Before/after display identity, client/drawable sizes, focus, note release, pointer capture and hit alignment. If the transfer causes focus/capture loss, grade the cleanup path separately; it does not prove uninterrupted preservation. |

Repeat the reference/minimum views in Flat, Rotary and Service. For each
readability finding, record the exact label/control ID, state, size, physical
display setting, image crop within its retained full frame, and what the operator
could or could not read/activate. Do not turn “looks readable” into a measured
contrast ratio or screen-reader result. The current material gallery's small-label
and lighting observations remain distinct.

## 4. Current focus inventory and proposed native semantics

### Existing keyboard order

Start a fresh Play launch with no pointer click; the first Tab reaches Play.
Record one complete forward and reverse traversal. These are **one-based Tab
positions**, not permanent IDs. [`move_tab_focus`](../../apps/standalone/UiModel.cpp)
uses the current visible control array, then three roving note groups.

| Positions in Play | Current controls and identity |
| --- | --- |
| 1–10 | Play, Rotary, Service, Save, Load, Help, Audio, MIDI, Panic, Flat. These alone remain in Rotary/Service. |
| 11–12; 13–24; 25–33 | Upper Edit A/B; Upper presets C, C#, D, D#, E, F, F#, G, G#, A, A#, B; Upper drawbars in footage order. |
| 34–35; 36–47; 48–56 | Lower Edit A/B; the same twelve Lower presets; Lower drawbars in footage order. |
| 57–60 | Wide Dimensional: enable, volume, decay, harmonic. Compact/Flat: enable, harmonic, volume, decay. Preserve control identity across a layout change; do not assume an unchanged ordinal means an unchanged control. |
| 61–63 | Nominal expression; nominal pedal mixtures 1 and 2. |
| 64–68 | Computer-key target Upper, Lower, Pedals; octave down/up. |
| 69–71 | Roving Upper key, Lower key, pedal. Arrows/Home/End reach all 61/61/25 keys; these are not 147 separate Tab stops. |

Footage order is 16', 5 1/3', 8', 4', 2 2/3', 2', 1 3/5', 1 1/3', 1'.
The actual inventory remains 68 controls plus 147 playing keys, not 71 controls.
Changing the edited bank rebinds nine visible drawbars to their existing bank
IDs; it does not create another nine controls. Legacy `SoundingBank` and
`CancelManual` compatibility actions are not extra painted focus stops.

### Mapping to freeze before a native bridge is implemented

The following names/roles/actions are **proposed bridge requirements**, not
currently exported objects. A platform owner should review their concrete native
API mapping before code. Use stable `UiControlId`/note identity, full spoken
labels and the existing main-thread action/acknowledgment boundary. Never derive
accessible identity from screen coordinates or transient Tab position.

| Object/name pattern | Proposed role, value and action | Events/observations required |
| --- | --- | --- |
| “Play/Rotary/Service workspace” | Three selectable tabs; selected workspace and exposed panel; activate existing workspace action. | Focus and selection changes; hidden Play controls cannot receive native focus/actions. Return restores the remembered visible ID. |
| Save, Load, Help, Audio settings, MIDI settings, Panic; “Flat presentation” | Named buttons; Flat is a checked toggle. Preserve exact existing actions and shortcuts. | Invocation result/status; Flat checked state; modal opened/closed; no silent sound-control change from presentation. Panic has its existing all-owner scope. |
| “Upper/Lower edit bank A/B” | A choice group distinct from sounding registration; activate changes editor bank only. | Selected edit bank and newly bound drawbar names/values. No sounding-selection event merely because EDIT changes. |
| “Upper/Lower preset C: Cancel”, “… C#: fixed registration”, “… A#: adjustable bank A”, “… B: adjustable bank B” | Twelve selectable choices per manual. Arrow navigation focuses only; Enter/Space selects. Include full fixed-row identity for C#–A. | Focus separately from desired selection, pending acknowledgment and applied sounding selection. Cancel retains held notes and memories; do not announce Panic. |
| “Upper bank B drawbar 5 1/3 feet” and corresponding banks/footages | Integer range control 0–8, step 1; increment/decrement, endpoints and reviewed set-value route through the existing bridge. Eighteen visible, 36 retained positions. | Full identity, desired value, pending flag and acknowledged applied value; never present pending as sounding/applied. |
| “Nominal pedal mixture 1/2”; “Nominal expression/gain” | Mixtures 0–8 step 1. Expression 0–1 with percentage speech, normal arrows 0.05, Shift+arrows 0.01, Home/End 0/1. | Value/range and pending/applied changes; no calibrated pedal, voltage or loudness claim. |
| “Percussion enable/harmonic/volume/decay” | Enable checked On/Off; named two-state choices Second/Third, Normal/Soft, Slow/Fast. Existing Enter/Space toggles. | Announce retained value and eligibility separately: requires connected Upper B without a fixed row. Do not invent a recharge/readiness meter. |
| “Computer-key target Upper/Lower/Pedals”; “Octave down/up” | Target choice and octave buttons; expose manual base MIDI or pedal base ID. | Changed future-press target/base; an already-held note retains its original identity. |
| “Upper manual C4, MIDI 60”; “Pedal 25 of 25” | Grouped momentary playing-key objects with roving keyboard focus and applied held state. Focus and Space down/up retain owner 101. | Focus is not note-on; pressed/held is an applied logical target, not an owner count or proof of sound. A native Invoke must not create an indefinite latch: review a press/release or bounded-audition policy before adding an Invoke mapping. Existing keyboard audition can be tested meanwhile. |
| Service/Rotary cards and footer status | Read-only groups/text, including snapshot freshness, availability/evidence, pending/unsaved and explicit “Not connected/Not acquired/Not observed”. | On-demand reading and meaningful status changes. Keep changing frame counters/meters out of unsolicited per-frame speech; do not add hidden model controls. |

A single current semantic focus should correspond to the painted focus ID. A
screen reader must be able to query complete names, roles, range/value/selection,
enabled/visible state and available actions. Attach status announcements to
actual user actions, errors, acknowledgment and connection changes; retain the
event stream to assess ordering and repeated announcements. Pixel equality
cannot establish any of these properties.

Modal mapping must preserve the current source inventory:

| Modal | Current focus order and operations to expose |
| --- | --- |
| Audio | Six stops: previous output, next output, sample rate, buffer frames, Apply, Close. Rates 44100/48000/96000 Hz; buffers 128/256/512/1024/2048 frames. Arrows cycle, Home/End choose endpoints. Apply restarts audio, clears notes and requires explicit MIDI reconnect; it is not a presentation-only action. |
| MIDI | Eleven stops: previous port, next port, Upper/Lower/Pedal channels, expression minimum/maximum/direction, Apply/Connect, Disconnect, Close. Channels wrap 1–16; endpoints clamp 0–127; direction Normal/Inverted. Use the [exact operations](../MIDI_EXPRESSION_GUIDE.md#edit-the-midi-dialog). |
| Help | One effective Close target; source reuses modal slot 5, starts there and ignores Tab. Enter/Space/Escape closes. Do not misreport six Help controls from the shared Audio rectangle array. |

Expose a modal dialog boundary with its own focus, label numeric controls as
value controls rather than editable text, and keep selected/configured/active/
reconnect-pending MIDI facts separate. Closing returns to the retained underlying
UI focus; a shortcut opener need not have been the focused header button.

## 5. Manual journeys on the current native UI

Run J1–J6 on D1; repeat the focused display/layout checks on D2–D5 as available.
For every numbered transition, retain an action/time record and a lossless
desktop frame **while the relevant hold still exists**, plus its matching typed
observation when present. Pause long enough to observe a painted applied state;
do not infer a missed state from later zero counts. Use independent note
identities to distinguish owners visually.

| ID | Operator sequence | Required observations and limits |
| --- | --- | --- |
| J1: keyboard and controls | Traverse the complete forward/reverse focus inventory. In each key group use Home, End, arrows and Space down/up; move focus while Space stays down, then release. Change F1/F2/F3 and octave while a computer key is held, then release that original key. Exercise each bank's first/last drawbar at 0/8 and expression at 0/1 with fine steps. | Correct full footer name, visible focus and range; navigation alone produces no note; original releases survive target/focus changes; all four banks retain separate values. Preset arrows only focus; selection requires activation. Record the actual percussion order for each layout. |
| J2: pre-held navigation | Start a fresh Play/Dimensional run at 1672×941: hold computer A on default Upper C4 (MIDI 60) and primary pointer on Upper C2 (MIDI 36). Retain both applied holds before F5→F7→F6→F4. Resize to 960×700, then use F6→F5→F7→F4 while still held to return through the reverse route to Play/Dimensional. Repeat in a fresh run starting at minimum and resizing toward reference. | Both original note identities survive each view/size change without new hidden-note acquisition; clocks/controls do not reset. Service counts alone do not identify notes, so pair with action records and Play frames before/after. This fills the old X11 run's missing pre-held prefix. |
| J3: capture, return and moved pedals | After a J2 view/size transition, move the still-down pointer outside, release outside, return button-up, move over a different key, then freshly press/release it. In a separate fresh press, test ordinary in/out/in/out movement without intervening layout change. Repeat the branch crossing with pointer-held pedal 25. | The suppressed post-transition pointer keeps its original note until Up/capture loss; button-up return does not resurrect it; a fresh press works. Ordinary unsuppressed motion releases/reacquires targets while capture persists. Retain capture attempts/successes/losses/release calls and each held endpoint. A keyboard-held pedal does not qualify the pointer-held pedal case. |
| J4: drags and deliberate cleanup | Start a drawbar drag on a named bank; resize or change view while down, then move. Release and start a fresh drag. Separately hold a keyboard note and a distinct pointer note, deliberately deactivate/minimize, release outside and return. Repeat with Escape and with Panic. | Layout change closes the parameter drag; subsequent motion cannot edit a newly exposed bank/control. Focus loss/Escape clears UI owners and suppresses still-down inputs until original Up; return produces no new note. Panic clears all owners. Record capture loss/failure only when actually observed; do not simulate it with dummy SDL and call it OS evidence. |
| J5: modal/numeric cleanup | Hold A plus a pointer or Space note before opening Help, Audio, then MIDI in separate trials. Keep A physically down while closing, then release/repress. Traverse each modal forward/reverse, change numeric endpoints with arrows/Home/End, try F4–F7 and piano keys while open, then close. In MIDI set minimum equal to maximum, activate Apply, correct the pair, close without Apply and reopen. | Opening releases UI notes; modal keys cannot start notes or navigate underlying workspaces; release still works. Existing numeric controls are not text fields. Invalid Apply preserves configured/active settings and keeps staged values for correction; closing discards staged edits; reopening copies configured settings. A MIDI-OFF build should truthfully report unavailable/inactive state, not a connection. |
| J6: ordinary shutdown | In a fresh ordinary launch, retain an unheld endpoint, then close via the actual window close control. Optionally run a separately labeled held-close trial. Retain process exit immediately. | Numeric exit, timeout/signal status, final snapshot availability, stopped/unheld joined state, callback/error/fault/overflow/rejection/discard counts and observation truncation. Retain any nonzero discard with its unknown identity; do not infer all commands applied. Alt+F4 alone does not qualify the close-control case. |

For a pointer-held resize/transfer, establish an OS window-manager operation
that changes size/location without releasing the primary button or deliberately
deactivating the window; record the exact method. Releasing the note to grab a
resize handle does not execute J3. If the available tool/window manager cannot
perform or retain the intermediate held steps, mark those steps blocked. If
capture or focus is lost, the valid observed cleanup is a different result from
uninterrupted continuity. Keyboard-held resize can use the ordinary mouse edge.

J5's Audio Apply is a separate lifecycle subcase: keep a copied controls baseline,
observe the explicit restart message, released notes and preserved acknowledged
controls, and reconnect MIDI only through its explicit workflow. A no-device
setup may qualify modal editing/close without qualifying Apply to real audio.
Keep intentional validation-error trials separate from a fresh healthy ordinary
close run; retain their expected error reports instead of requiring zero errors
or silently deleting them.

For optional physical MIDI overlap, record the exact port, routing and controller.
Hold Upper C4 from UI and MIDI simultaneously; release UI then MIDI, and repeat
in reverse order. The target remains held after the first release and clears
after the second. Record the audible output path separately. UI held counts,
synthetic MIDI and software callbacks alone do not establish physical audio.

## 6. Flat, reduced motion and native semantic journeys

**Flat/reduced-motion observation:** run J1 and J5 at 960×700 and 1672×941 with
`--flat`, then toggle F7 during J2. Record identical sound-control meanings,
complete inventory, focus, release ownership and readable status. On the same
machine, record the actual OS reduced-motion preference, observe a short declared
idle interval and the same navigation with it enabled, then compare Dimensional
and Flat. List decorative motion, transitions and essential live readout changes
separately. Current source has no preference integration; an observed static
view cannot turn that absence into an implemented preference feature. Any
needed motion-policy work stays outside this documentation change.

**S0 — current semantic baseline:** choose one platform first. A Linux native
backend with a named AT-SPI inspector and Orca is a practical initial assignment
because the retained OS evidence is X11; Windows/macOS need their own providers
and observed journeys. Record actual inspector/screen-reader versions, settings,
input mode and process/executable. Start at the application window and export
the tree, focused object and event log. Attempt Tab to Play, first drawbar and
Upper key; open/close MIDI. If only the window/client is exposed or no child
focus/value events exist, retain that observed gap and mark S1–S4 blocked by the
missing bridge. Do not manufacture a control tree from screenshots/OCR.

**S1 — inspect and navigate after reviewed bridge implementation:** export the
tree in Play, Rotary, Service, both presentations and each modal. Compare every
visible control identity and all discoverable playing-key identities with
section 4; preserve the existing 71/10 keyboard focus behavior. Traverse forward
and backward with screen-reader speech/events enabled, then use roving navigation
to manual MIDI 36/96 and pedals 1/25. Record announced full name, role, current
value/selection, range/actions and corresponding painted focus. Hidden Play
controls cannot remain actionable through the provider. Informational cards must
be readable without inventing new musical focus stops.

**S2 — values and truthful status:** edit an inactive bank while a fixed preset
sounds; activate a different preset; change expression/percussion; Save then
Load using a fresh state copy. Retain the requested value, pending status when
actually observed, applied value and completion/error announcements. Distinguish
EDIT from SOUNDING, clean from saved-to-disk, pending from applied and unavailable
from zero. Ordinary callbacks may acknowledge too quickly to capture a native
pending announcement; mark that transition unobserved and use a separately
reviewed deterministic bridge harness for ordering. Do not stop audio artificially
and present the result as ordinary native timing. Retain event counts so a live
counter or meter cannot silently become a continuous speech stream.

**S3 — modal and numeric semantics:** repeat J5 with screen reader on, including
all eleven MIDI stops and the invalid equal-endpoint pair. Observe dialog entry,
focus restriction, exact value/range/state changes, error announcement, continued
correction, close and restoration to the retained underlying focus. Read selected,
configured, active and pending facts independently. Test Help's one effective
Close and Audio's six stops. If a future text editor exists, separately exercise
typing, commit, cancel and physical key release; that is not supported by the
current inspected source.

**S4 — screen-reader keyboard interaction and cleanup:** repeat the Space audition,
original-key release, focus loss and held-modal parts of J1/J4/J5 with the named
screen reader running. Record its browse/pass-through mode and any intercepted
shortcut, including F-keys and letter keys. A delivered OS key and a screen-reader
command are different inputs. Preserve momentary-note release on all exits and
retain focus/value/status events through resize and Flat changes. A failed or
undelivered action stays a reported usability gap; a screenshot cannot close it.

## 7. Evidence record and bounded next assignments

For each step, retain: run/step ID, operator action, timestamp, before/after
workspace/presentation/size, focused `UiControlId` or proposed provider ID, note
identities and known input owners, desired/applied controls, result and a reason
for failed/blocked/unobserved steps. Bind full-frame image, native tree/event log,
screen-reader speech transcript or recording, and diagnostics with hashes.
Keep observation and expectation in separate fields.

Current schema-3 diagnostics provide final logical/drawable size and
`presentation.observations` with logical size, workspace/presentation/overlay,
snapshot freshness, pending state, frame clock/revision, held-target **counts**,
capture counters and modal focus. They do **not** export ordinary focus IDs,
individual pointer coordinates/owner identities, a per-step drawable-size/DPI
history, native accessibility trees or speech events. Supplement those with
actual operator/platform evidence; do not fill absent fields by inference.
`sdl_captured` is the application's admitted-capture flag;
`release_calls` is an explicit release-call count, not its return status.
The observation buffer holds 512 records: retain `observations_truncated`, and
use shorter separate runs if needed rather than presenting a truncated history
as complete. Preserve original outputs and all failures.

| Priority and owner | Bounded deliverable | Review boundary |
| --- | --- | --- |
| 1 — native display owner | One identified native build; D1 and J1–J6 with genuine intermediate holds, fresh press, ordinary close and lossless step frames. | Existing desktop contract; explicitly missing D2–D5/device/semantic rows remain open. |
| 2 — platform accessibility owner | S0 tree/event baseline, then a reviewed one-platform mapping/provider design using section 4 and existing action/copy boundaries. Resolve momentary key actions and status publication before implementation. | Source implementation, native inspector evidence and S1–S4 are separate deliverables. Canvas labels alone cannot satisfy the bridge. |
| 3 — display/input owner | Real fractional/high-density and cross-display observations, targeted label/hit/focus fixes only when findings identify them. | Requalify changed inputs on the affected display; retain current galleries and original failures. |
| 4 — accessibility/input owner | Source-identified bridge implementation and actual screen-reader/keyboard/Flat/modal journeys; decide any missing reduced-motion or numeric text-entry work in a separately reviewed scope. | No new parameter/state/owner identities; no hardware, deadline, DAW, physical-fidelity or whole-interface-equality claim follows. |

Root admits only the specific source/platform/configuration and steps actually
observed. A42 delivers the source-grounded plan and documentation integrity
receipt; all native execution and semantic-provider implementation above remain
unrun or unimplemented here.
