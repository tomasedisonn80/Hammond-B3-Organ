# Native registration browser: visual and input contract

**Status: independently reviewed and frozen implementation input, 15 November
2026; root admission precedes implementation.** A09 authored this document;
the [A12 review](development/2026-11-15-next-phase/notes/A12-browser-ui-review.md)
records the amendments and input/final identities. The companion
[library contract](REGISTRATION_LIBRARY_CONTRACT.md) owns storage, scope merging,
acknowledgment and operation outcomes. A disagreement between the two documents
is a review blocker, not an implementation choice.

This is a bounded M9 addition to the native standalone at the session's supplied
baseline `138fca9af7feca46d10b0e2b65d891f4751a3904`. It adds a real named-control
browser and the atlas's top-right selected-name affordance. It does not claim an
implemented feature, a new product capture, or whole-interface 1:1 acceptance.

## 1. Source, intent and ownership

Read the complete [standing instructions](../AGENTS.md), [M0–M9 plan](PLAN.md),
the [current session](development/2026-11-15-next-phase/README.md), and its A05/A06
reading notes before using this contract. Relevant atlas requirements are:

| Source | Binding interpretation for this slice |
| --- | --- |
| Atlas pp.409–410; original cover/page-409 JPEG | Walnut frame, charcoal plates, restrained brass, ivory text and a top-right name field with previous/next arrows are visual direction. Generated key counts, legends and fictitious controls are not engineering authority. |
| Atlas pp.416/418 | Modern saved registrations remain outside the reversed preset octave. Show the exact recall scope before activation; expression may change only when the displayed scope includes it. |
| Atlas pp.433–438 | Stable semantic identities, original press ownership, distinct focus/selection/applied cues, common paint/hit geometry and complete Flat operation. SDL keyboard support alone is not native accessibility qualification. |
| [A05 assessment](development/2026-11-15-next-phase/notes/A05-atlas.md), [A06 assessment](development/2026-11-15-next-phase/notes/A06-atlas.md) | Preserve legacy Save/Load clean-state tracking; opening this browser must not inherit ordinary modal note release. Their alternative Registration proposals are resolved by the explicitly enumerated scope in §2 and the companion contract. |
| Actual `UiModel`, `InstrumentView`, `main.cpp` and [current product gallery](../examples/demos/standalone-product-preview-v1/README.md) | Existing musical state, header extents, note ownership and controls are the implementation baseline. The retained gallery has its own earlier capture identity; it is not a capture of this proposed feature. |

The author directly inspected the unaltered reference JPEG, actual reference-size
Play PNG, minimum Play and minimum Flat PNGs. Input identities are retained in
the [A09 note](development/2026-11-15-next-phase/notes/A09-browser-ui-contract.md).

### Authorized implementation boundary after freeze

- New native-only `apps/standalone/RegistrationBrowserModel.h/.cpp` and
  `RegistrationBrowserView.h/.cpp` hold browser state, shared rectangles, focus,
  text editing and paint. The library module remains a distinct owner.
- `UiModel.h/.cpp`: append presentation identities/requests, change only header
  control allocations, add narrowly scoped gesture/modal-input and recall
  publication entry points, and update inventory/focus validation.
- `InstrumentView.h/.cpp`: consume copied browser/header view data, replace the
  header's utility allocation assumption, and delegate browser overlay paint.
- `main.cpp`: explicit open/close, input routing, text-input lifetime, library
  request/poll, command dispatch and snapshot-observation hooks. Root assigns
  exact integration ownership and build/test changes.
- No changes to deck/rack/manual/pedal/cabinet geometry, `Drawing` optimization,
  M6 FOH, native MIDI close, R4, Engine sound or shared navigation are authorized
  by this document. Those remain with their current owners.

The closed browser may change header pixels only, apart from existing dynamic
footer text reporting actual focus/status. Opening it adds an opaque modal panel
and an optional shadow no more than four logical pixels beyond that panel; no
full-window dimmer, camera animation or artwork overlay is part of this slice.
Underlying instrument controls keep their present layout and live held-note
indicators. Closing restores the underlying view without rebuilding sound.

### Explicit integration interfaces

The implementation handoff separates A14's `RegistrationLibrary.h/.cpp` storage
and pure scope primitives, A15's separate `LibraryModel.h/.cpp` catalog/receipt
authority, A17's new browser model/view, and A18's app, header and `UiModel`
integration. A13's scanner line and A16's scanner probe remain separate work.
These identifiers describe root's current assignment split, not additional
semantics. `LibraryModel` is the sole mutable catalog, draft, selection/current
reference and operation-receipt authority. The browser holds an immutable view
copy plus its presentation state; it must not introduce another mutable catalog,
name draft, selected-entry owner or receipt. Main orchestrates storage and Session
effects and returns copied results to `LibraryModel`.

| Interface | Responsibility |
| --- | --- |
| `RegistrationBrowserModel::observe(const LibraryView&)` | Accept one copied library view; reconcile scroll and text-caret bounds to the authoritative selected key/draft without issuing a request. |
| `RegistrationBrowserModel::open(UiControlId return_focus)`, `close()` | Presentation-only modal lifetime; retain/return the original instrument focus. Draft name/scope remain in `LibraryModel`. |
| `RegistrationBrowserModel::resize(width,height)` / `layout()` | Publish the sole validated `RegistrationBrowserLayout` described below. |
| `RegistrationBrowserModel::key`, `text_input`, `pointer`, `wheel` | SDK-free input vocabulary, local focus/caret/scroll edits and explicit bounded `RegistrationBrowserIntent` results. Include PageUp/PageDown, Backspace/Delete and SelectAll/Paste commands even though today's `UiKey` lacks them; SDL/clipboard access remains in main. No Session or filesystem access. |
| `RegistrationBrowserIntent` | Select key/relative row, SetName, SetSaveScope, Refresh, Recall, SaveNew, Close or ToggleFlat, with copied bounded payload where needed. Main maps library intents to the companion `LibraryModel` APIs. |
| `RegistrationBrowserViewState` | Copied `LibraryView` plus browser focus, visible-row start and name caret/selection. A view copy is immutable during paint. |
| `paint_registration_browser(Drawing&, layout, view)` | New file's modal paint using shared layout only. Header helper reads the three new controls from `UiLayout`. |
| `UiModel::set_browser_input_active(bool)` | Suppress instrument keyboard/pointer activation after real physical-Down bookkeeping and before Escape or hit activation; ordinary Up handling remains first. Modal entry suppresses an already held pointer's motion until its real Up without releasing its note. Closing does not clear physical/suppressed state. This is separate from the text-entry-only flag. |
| `UiModel::close_parameter_gesture()` | Clear only the original parameter drag; retain note holds and signal that capture may end only when it belongs solely to that drag. Main owns the SDL release. |
| `UiModel::restore_focus(UiControlId)` | Validate a visible semantic target and restore focus without activating it or publishing sound. |
| `UiModel::recall_controls(candidate)` | Companion contract's single snapshot publication with legacy clean baseline preserved. |

Main applies each presentation intent to `LibraryModel` synchronously and feeds
its resulting `LibraryView` back before dispatching the next browser input event.
Otherwise consecutive text events or row moves could derive from a stale draft
or selection. `observe` itself never creates a Refresh, Recall or Save request.

Append `ViewOverlay::Registration` after the existing None/Help/Audio/Midi
values. `InstrumentViewInfo` may carry a const browser-view pointer whose
lifetime covers the synchronous paint; it must not retain a pointer to a live
filesystem operation or Engine. Main owns model lifetime, supplies copied
observation/submission results to `LibraryModel`, and owns text input and SDL
capture. A17 can implement and model-test the browser against `LibraryView`/intent
values without editing main/UiModel or A15's model; A18 connects them. Root owns
CMake.

## 2. Scope preview and explicit operations

The modal title is **Registration library**. This is a modern saved-control
feature, separate from the 24 reversed preset keys. A file's suffix declares its
scope under the library contract: `.b3registration` or `.b3performance`, each
containing the unchanged `B3CONTROLS4` payload. The browser displays the admitted
filename stem as the name; it never invents a factory registration or derives a
claim of physical fidelity from that name.

| Displayed scope | Fields restored by explicit Recall | Visible qualification |
| --- | --- | --- |
| **Registration**; default for Save new | All four manual drawbar banks (36 positions), both pedal positions, both remembered banks, both route-enable bits, both fixed registrations, and percussion enable/harmonic/volume/decay | **Expression stays at its current value.** Merge from the latest desired controls at the actual Recall action; opening or selecting the entry does not freeze expression. |
| **Performance — current controls** | Every existing `ControlSnapshot` field, including expression | **Includes expression.** This is current-controls recall, not complete atlas performance or calibration-profile recall. |

Neither scope contains held notes, physical key state, source phase, contact or
percussion history, device configuration, MIDI routing/calibration, editor bank,
focus, workspace, camera, output trim or specimen profile. Scanner, rotary and
microphone controls are absent from the current snapshot. Do not show selectors
for those absent fields, a disabled calibration-recall promise, or an imitation
Stop/speed/microphone control.

The preview always shows the full selected name, scope, all four nine-digit
drawbar strings, both manual route/fixed/remembered-bank states, pedal positions,
the four percussion settings, and expression treatment. A cancelled manual must
still expose its remembered bank and retained fixed registration; displaying
only its current silence loses relevant saved state. Applied SOUNDING captions
on the instrument remain independent of this preview.

### Selection and recall

1. Opening, selecting a row, moving list focus, using header arrows, scrolling,
   changing the Save new scope, Refresh and Close emit no musical command.
2. Selection only loads/displays an admitted preview. A first scan may select
   the first entry for preview; it does not establish an applied name. Refresh
   retains the same stable entry key when present, rather than its old row index.
3. **Recall** is the sole browser control that requests sound changes. A click
   or Enter/Space while Recall has focus submits one operation. List Enter,
   double-click, keyboard repeat and header arrows must never recall.
4. Recall is unavailable for no selection, invalid/ambiguous/stale entries,
   an incomplete scan, unavailable audio or a pending library mutation. State
   the reason in text. Audio stopped means **Start audio to recall**; named
   recall neither queues nor stages a control change for restart.
5. Pending library recall/save is single-flight. Selection and Close remain
   available; duplicate activation cannot create a second request. Closing
   hides the panel without cancelling or losing its operation identity.

### Save new

The persistent lower form contains Name, Save scope and **Save new**. Default
scope is Registration; its description says that future recall preserves
expression. Choosing Performance makes its expression inclusion explicit before
saving. Scope is read-only for an existing selected entry; changing the form's
scope does not reinterpret that entry.

Final Save name admission is the companion contract's exact 1–48 ASCII-byte policy:
letters, digits, interior spaces, hyphen and underscore; first/last characters
must be alphanumeric; Windows reserved whole stems are rejected. Do not silently
trim, truncate, substitute or normalize a user's name. Show rejected input and
duplicate-name reasons beside the form. Different case does not avoid the
library's same-name/same-scope collision rule. Editing uses the distinct bounded
draft policy in §6: an incomplete draft is not a file name and cannot enable Save.

Save new is create-only. There is no overwrite, replace, rename, delete or import
workflow in v1. It persists only a coherent acknowledged controls copy according
to the library contract. A successful save says **Saved / current**; it does not
say that Recall ran. A changed name draft or selection does not retarget a save
already in progress. A duplicate asks for another name and preserves the file.

Legacy SAVE/LOAD and Ctrl/Cmd+S / Ctrl/Cmd+O keep their existing `--state` target,
format and clean-file baseline outside the browser. The new Save new action
does not call `UiModel::mark_saved()` for that legacy baseline. The browser's
modal text context consumes those shortcuts while open; it neither invokes
legacy files nor silently rebinds them to Save new. Closing restores their
existing behavior. No new shortcut is required for browser completeness.

## 3. Three distinct identities and truthful outcome text

The copied browser view carries three separate identities: selected entry,
current named reference established by acknowledged recall/save, and operation
target. Selection must never overwrite either of the other two. Stable entry
keys survive sorting/refresh; row ordinals are not identities.

The header label explicitly names the **selected** scope and state. Its central
button displays the selected name or **Browse registrations**. The modal's
result band separately names the current reference, with **Modified** when
scope comparison of actual acknowledged controls no longer matches it.
Registration comparison excludes expression; Performance comparison includes it.
Unacknowledged desired changes have a separate **Controls pending** indication;
they do not establish Modified or Applied. Neither named operation moves the
legacy file's clean baseline. Its independent dirty flag can correctly become
clean when acknowledged controls exactly return to that retained baseline.
If the underlying file disappears, retain the
current reference with **Source missing** rather than claiming sound reverted.
An identical filename is not proof that a refreshed preview is the content that
established the current reference. If that file's parsed controls changed, keep
the old reference baseline, show the new preview as not recalled, and require a
new explicit Recall. Selection equality never manufactures an acknowledgment.

| State | Required feedback and meaning |
| --- | --- |
| No selection / empty | **Browse registrations** / **No saved entries. Enter a name to save current controls.** No fictional default applied name. |
| Selected, never applied/current | **Selected — not recalled**. The old current reference remains separately visible. |
| Pending Recall | **Pending recall: NAME**. Queue acceptance is not applied sound. Record the request identity and target independently of later selection. |
| Proven applied Recall | **Applied: NAME** only after the library's full receipt rule succeeds: a fresh newer publication, matching sequence/revisions, unchanged recovery/rejection/discard/submission-failure counters, and matching desired/acknowledged controls. Cached display values never prove this. |
| Acknowledged Save new | **Saved / current: NAME**; no implication of a recall or audio restart. |
| Committed save, later cleanup/refresh problem | **Saved with warning: NAME**. The file was committed; do not report a failed save or silently retry/delete it. |
| Later edit | **Modified** against actual acknowledged controls in the current entry's declared scope; **Controls pending** remains separate. Do not hide an unresolved operation behind either phrase. |
| Rejected / error | **Recall failed** or **Save failed**, named target and a concise reason. Keep the previous current reference; no optimistic active name or rollback. |
| Timeout | **Recall unconfirmed**. It may still reach audio later; do not claim cancellation, failure to apply, or automatic rollback. A late snapshot updates actual controls but never promotes the expired receipt. A save timeout is **Save cancelled — acknowledgment timed out**, with its draft retained. |
| Newer desired edit supersedes request | **Recall superseded by newer controls**. Never restore an older snapshot to make the label look successful. |
| Scan failure/overflow | **Library unavailable** or **Refresh incomplete**. Retained rows are visibly stale and cannot be recalled until a complete successful refresh. |

The selected name remains in the header even when the pending/error target is a
different entry. A compact header may show **Other recall pending**. The result
band retains separate current-reference and operation-target lines; a short
actionable reason/category may replace footer guidance while an error is active.
Retain the complete bounded diagnostic in `LibraryView` and native diagnostic
output. Do not try to squeeze an arbitrary 256-byte filesystem diagnostic into
the two-line result band or silently drop the error category. Measure the full
48-byte current/target names and concise state text at the minimum size; the
selected name remains complete in its preview even when the header ellipsizes.
No spinner, color or icon carries the only meaning. Errors persist until a new
explicit operation meaningfully supersedes them; selection does not erase a
receipt, and errors do not disappear
after an arbitrary animation timeout.

Library/file work runs on the main thread only, outside audio processing, under
the companion contract's finite synchronous scan/read/write bounds. File calls
may delay the next event poll; this contract does not claim a wall-clock
filesystem or release-latency bound. They must not discard, synthesize or gate
queued physical Ups: every actual release reaches the original owner path when
the loop handles it. Acknowledgment waiting uses normal event-loop polling.
Paint and hit testing consume copied, bounded data and perform no directory
traversal or file reads. An async filesystem worker is outside this v1 contract.

## 4. Header geometry: only the existing header allocation changes

All dimensions below are logical window units. `UiRect` remains left/top
inclusive, right/bottom exclusive; focus/edge/shadow paint does not enlarge a
hit region. Geometry is calculated once and used by paint, hit testing, keyboard
focus and future semantic bounds. Physical pixels use the existing renderer
transform; no independent rounded-pixel hit layout is permitted.

Keep `layout.header`, `show_cabinet`, `sidebar_pedals`, margins and every
nonheader rectangle exactly as currently calculated. Let `H` be that existing
header and `R = H.x + H.width`. The **wide** header means
`layout.sidebar_pedals == true`, independent of Flat/Dimensional. Other admitted
sizes use the compact header. Workspace tabs keep their existing rectangles.

| Rectangle / allocation | Wide header | Compact header |
| --- | --- | --- |
| Selected-name group | `(R−370, H.y+26, 370, 40)` | `(R−328, H.y+18, 328, 28)` |
| Previous selection | Left 40 units of group | Left 32 units of group |
| Open browser/name | Middle 290 units of group | Middle 264 units of group |
| Next selection | Right 40 units of group | Right 32 units of group |
| Selected scope/status label; read-only | `(R−370, H.y+8, 370, 14)` | `(R−328, H.y+2, 328, 12)` |
| Legacy utility row | SAVE, LOAD, HELP, AUDIO, MIDI, PANIC; six 56×24 hits with 6-unit gaps, beginning `(R−366, H.y+72)` | FLAT, SAVE, LOAD, HELP, AUDIO, MIDI, PANIC; seven 52×28 hits with 4-unit gaps, beginning `(R−388, H.y+48)` |
| Flat control | `(H.x, H.y+74, 70, 24)` below workspace tabs | First control in the seven-button utility row |

The name group is one recessed charcoal field with subtly divided arrow ends,
matching the reference's upper-right composition. Its three distinct hits may
abut, with their shared boundary owned by the right-hand rectangle. Arrow ink
and the name stay at least six units inside their hit. Do not add a settings
cog with an undefined action; Audio/MIDI/Help retain explicit existing controls.

| Window | Existing header `(x,y,w,h)` | New central name hit `(x,y,w,h)` |
| --- | --- | --- |
| 960×700 | `(16,16,928,82)` | `(648,34,264,28)` |
| 1280×900 | `(16,16,1248,82)` | `(968,34,264,28)` |
| 1672×941 | `(71.896,16,1528.208,100)` | `(1270.104,42,290,40)` |

At 1672×941 the group's left edge is 1230.104, close to the source image's
top-right field. This is a declared design allocation, not a new measured
similarity result or physical dimension. At minimum size the shorter utilities
retain their complete labels and at least the existing 28-unit utility height.

Header title fitting must now derive its right boundary from the name group's
left edge minus 12, **not the SAVE button**. Its left boundary remains 12 after
the Service tab. The wide title stays symmetric about the window center and
retains the existing font, 42.75-unit Dimensional sizing and vertical placement
when it fits; its truthful **NOMINAL DRY ORGAN** caption retains the existing
374-unit target width and vertical placement. Moving Flat to the left must not
drive the existing `flat_left` caption calculation negative. Give title and
caption explicit shared allocations instead of relying on unrelated controls.

For compact headers, the caption's right boundary is the utility row's left
edge minus 12. Center its text on the window when it fits, then clamp inside
that interval. Fit the title in its declared interval; clip/ellipsis neither
the product name nor the nominal-dry qualification. New selected-name text
may ellipsize, with the complete name shown in the browser and focus caption.

Header Previous/Next traverse the same ordered admitted row set as the browser,
including invalid-payload rows for inspection; invalid filename stems are omitted
and counted in the scan warning under the library contract. They stop at either
end. Their names are
**Previous saved entry** and **Next saved entry**, not previous/next sound.
Empty or edge-disabled controls retain focus and expose a reason. Neither
activates Recall nor changes workspace, edit bank or note owners.

## 5. Modal geometry and visual treatment

`RegistrationBrowserModel` publishes one validated `RegistrationBrowserLayout`.
`RegistrationBrowserView` and main input dispatch consume it directly. Reject
nonfinite/out-of-range window inputs transactionally, matching the existing
960×700 through 8192×8192 layout admission. Resizing recomputes only presentation
rectangles, retains selection/draft/focus/operation identity and closes any
browser scrollbar drag against its original capture.

Let `B.w = min(1040, W−64)`, `B.h = min(640, H−64)`, and center `B` in the
window. Let `L = clamp(floor(0.34×(B.w−72)), 280, 328)`. Coordinates below are
relative to `B` unless stated otherwise.

| Region | Shared rectangle / rule |
| --- | --- |
| Title | `(24,18,B.w−160,28)`; **Registration library** |
| Close button | `(B.w−112,16,88,32)` |
| Directory/scan summary | `(24,56,B.w−48,20)`; read-only, path may ellipsize, scan state must remain explicit |
| List viewport | `(24,96,L,320)`; eight 40-unit rows; no whole-row hit extends into the 12-unit scrollbar strip |
| Row `i` | `(24,96+40×i,L−12,40)` for `i=0…7`; semantic entry key is independent of visible slot |
| Scrollbar | Last 12 units of list; thumb at least 24 units high; no separate Tab stop |
| List count | `(24,416,L,20)`; e.g. **1–8 of 128** admitted rows, or **0 entries**; distinguish omitted-name/candidate warnings in the scan summary |
| Selected preview | `(44+L,96,B.w−68−L,B.h−296)` |
| Result band | `(24,B.h−188,B.w−48,48)`; current reference and operation outcome are distinct readable lines |
| Name label / scope label | At `y=B.h−132`, height 16, above their corresponding fields |
| Name field | `(24,B.h−110,B.w−412,32)` |
| Save-scope control | `(B.w−376,B.h−110,208,32)`; Registration / Performance |
| Save new button | `(B.w−156,B.h−110,132,32)` |
| Refresh button | `(24,B.h−54,112,32)` |
| Recall button | `(B.w−144,B.h−54,120,32)` |
| Footer guidance | `(152,B.h−54,B.w−312,32)`; **Selection previews. Recall applies.** |

The selected preview is a read-only plate, not an editor that changes stored
values. Use up to two lines for the complete 48-character name, then explicit
scope/expression treatment, compact manual rows (route/fixed/remembered plus A/B
drawbar strings), pedal/percussion rows and exclusions. Its 340-unit minimum
height must fit the complete declared fields with 13–14-unit body text and at
least 18-unit line spacing. Invalid rows replace control details with the full
bounded admission reason and recovery action. No field is silently omitted to
fit; overflow is a layout test failure. The form's scope uses a short label,
while the preview spells out **Performance — current controls**.

Scroll position is an integer first-visible-row index in
`[0,max(0,row_count−8)]`. For at most eight rows the thumb fills its track and
does not drag. Otherwise its height is `max(24,320×8/row_count)` and its top is
`track.y + first/(row_count−8)×(320−thumb_height)`. Clamp drag results to that
range and round to the nearest row; a track click moves at most one eight-row
page toward the pointer. Wheel input affects only the hovered list/scrollbar,
moves by signed row steps with clamping, and never changes selection or recalls.
Honor SDL's flipped direction in main; ignore horizontal-only/nonfinite input.

| Window | Panel `B` | List viewport | Selected preview |
| --- | --- | --- | --- |
| 960×700 | `(32,32,896,636)` | `(56,128,280,320)` | `(356,128,548,340)` |
| 1280×900 | `(120,130,1040,640)` | `(144,226,328,320)` | `(492,226,644,344)` |
| 1672×941 | `(316,150.5,1040,640)` | `(340,246.5,328,320)` | `(688,246.5,644,344)` |

Dimensional style reuses existing charcoal, ivory, brass and cyan tokens and
pinned fonts. Use shallow inset framing, an opaque near-black text plate,
restrained warm highlight and a thin walnut outer accent. The new panel does
not import generated texture assets or add reflections under operational text.
Header name text uses the existing serif face at 20 units wide / 16 compact;
body and state text use the existing sans face. Utility labels use 12 units and
must be measured to fit their padded hits; selected-name ellipsis never shrinks
body text. Selected rows use a warm plate or brass edge plus a selection marker.
Focus is a separate two-unit cyan inset outline, visible even on the selected
row. Invalid/disabled controls have text explanations and remain legible.

Flat uses the identical geometry, fields, interactions and focus. It removes
ornamental gradients/shadows and uses solid fills/edges; no function or status
is hidden. No animation is required. Minimum-size fit and measured contrast
are acceptance observations, not a claim of WCAG/native accessibility compliance.

## 6. Semantic inventory and keyboard focus migration

Preserve all numeric values of existing `UiControlKind` 0–21 and append:

| New kind | Numeric value | Canonical identity / purpose |
| --- | --- | --- |
| `RegistrationBrowser` | 22 | Upper/A/index 0; open selected-name browser |
| `RegistrationPrevious` | 23 | Upper/A/index 0; select previous entry |
| `RegistrationNext` | 24 | Upper/A/index 0; select next entry |

Append `UiAppRequest::RegistrationBrowser = 5`, `RegistrationPrevious = 6` and
`RegistrationNext = 7` after existing MIDI settings; do not renumber existing
requests. None maps to a musical parameter. Reject malformed
manual/bank/index combinations as for existing global controls. Keep old
SoundingBank/Cancel compatibility actions and the preset identities untouched.

| Inventory | Before | Required after |
| --- | ---: | ---: |
| Sound parameters | 47 | 47 |
| Ordinary visible/control slots, including 24 presets | 68 | 71 |
| Common visible controls in every workspace | 10 | 13 |
| Play Tab stops, including three roving playing-key groups | 71 | 74 |
| Rotary/Service Tab stops | 10 | 13 |
| Existing MIDI-modal stops | 11 | 11 |
| Separate registration-modal stops | 0 | 7 |

Update `kUiMaxControls`, `kUiCommonControlCount`, validation, semantic-name
switches, workspace visibility, focus arrays, model fixtures, native raster/
replay inventories and operating documentation through their assigned owners.
Blindly changing only an expected count is insufficient. The sound-ID registry,
state version/readers and playing-key inventory do not migrate.

Common Tab order is Play, Rotary, Service, Previous saved entry, Registration
browser, Next saved entry, Save, Load, Help, Audio, MIDI, Panic, Flat; then the
existing Play-only order and three roving key groups. Existing controls keep
their relative order. All new header controls are reachable in all workspaces
and both skins. Every new header/browser target owns a positive, nonoverlapping
hit; existing playing-key overlap and its accidental-first hit policy stay intact.

The browser has separate semantic kinds List, Name, SaveScope, SaveNew, Recall,
Refresh, Close. Tab/Shift+Tab wrap through those seven stops in that order.
Disabled actions remain focusable for their explanatory text and emit no action.
The list is one roving Tab stop, with stable selected entry key and scroll
position. Decorative panels, status, preview text and scrollbar are not extra
Tab stops. Retain these semantics as the future native-accessibility binding;
do not claim a platform accessibility tree already exists.

| Input | Browser behavior |
| --- | --- |
| Up/Down in list; Home/End | Select preceding/following or first/last row; keep it visible. No Recall. |
| PageUp/PageDown in list | Move selection by eight rows, clamped. Wheel scrolls the list without recalling. |
| Enter/Space in list | Keep preview selection; never a default Recall action. |
| Left/Right or Home/End on SaveScope | Choose Registration/Performance; Enter/Space toggles between them. |
| Enter/Space on an action button | One explicit enabled action; repeated Down is ignored. |
| Enter in Name | Keep the draft; no implicit save or recall. |
| Escape / Close | Close panel, stop SDL text input, restore prior instrument focus; no note release. |
| F7 | May toggle the existing Flat presentation through its normal presentation-only path while keeping modal focus and owners; no other performance shortcut passes through. |

Use actual `SDL_TEXTINPUT` delivery for Name, not printable `SDL_KEYDOWN`
approximations. Implement caret/selection, Left/Right/Home/End, Backspace/Delete,
Shift with caret navigation to extend selection, Ctrl/Cmd+A and bounded explicit
paste. Start SDL text input only while Name is focused; stop it when focus leaves
or the panel closes. The **editing draft** may contain zero through 48 ASCII
bytes from letters, digits, spaces, hyphens and underscores in any position.
Temporary trailing/leading spaces and reserved partial stems are allowed so
`Sunday warm` and `CONtemporary` can be typed normally. Save new stays unavailable
until the complete literal draft satisfies final-name admission. Validate the
whole proposed replacement after applying the caret selection: invalid bytes
or length above 48 reject that event atomically, preserving draft and selection
and showing why. Never trim or truncate input. Draft editing constructs no path
and never forwards typed playing letters as note On. Draft text and scope survive
closing/reopening in `LibraryModel`; caret/selection belong to the browser.

Activation, scope toggles, Tab, Escape, F7, SelectAll and Paste require one fresh
nonrepeating Down and ignore duplicate Downs until the actual Up. List navigation
and Name caret/deletion may accept platform repeat events only after that key's
initial fresh Down was admitted in this browser context. A key held before
opening cannot acquire a browser action by repeating. SDL text events are each
handled once while Name has focus; no additional key-to-character path or custom
repeat timer runs. Forward actual Ups to the browser's input bookkeeping after
the instrument owner-release path, including after close, without activating an
action. The event that opens the browser is consumed by its original context and
is not redispatched into the new panel.

## 7. Input ownership and event order

Opening this browser is not window focus loss. **Do not call the existing
`open_overlay()` unchanged:** it invokes `lose_input(FocusLost)`, which posts
`ReleaseUiNotes`, sends pointer CaptureLost and releases SDL capture. Add a
dedicated browser entry path that remembers the current `UiControlId`, closes
only the parameter gesture, and enters modal input mode.

Closing a parameter gesture discards its captured drag binding without another
parameter edit and requires a new physical Down to restart it. Preserve its
original manual/bank/parameter identity until that closure. It must not clear
keyboard holds, audition holds, pointer-note holds or external MIDI owners.
If capture belongs only to the parameter drag, release it exactly once while
retaining physical-down suppression until the real Up. If it belongs to an
active pointer note, retain it until that note's actual Up/capture-loss event.
That held pointer remains motion-suppressed through browser closure until Up;
closing over a playing key cannot create a new glissando destination.

Required dispatch order:

1. Physical keyboard Up always reaches `UiModel::key()` before modal, modifier,
   text, focus, selected-bank or workspace gates. Its original owner/note is
   released exactly once, including Space audition. Browser controls do not
   reinterpret Up from a pre-existing playing press.
2. Primary pointer Up and genuine CaptureLost always reach the instrument's
   ownership bookkeeping, then close any browser drag. Release SDL capture once
   if still owned; an already observed OS capture loss is not a second release
   call. Pointer motion inside the open browser does not glissando the held
   instrument pointer into a different note or release it early.
3. For browser Down, record the real physical state/suppression in `UiModel`
   without executing performance actions, then dispatch to the browser. Do not
   pass Escape through the existing `UiModel::key()` Down path first: it calls
   `release_ui()` **before** the present text-entry gate. A narrowly named
   modal-input operation must preserve bookkeeping while suppressing that
   action. No fabricated Up events, synthetic Escape, owner reset or blanket
   suppression reset is an acceptable substitute.
   Modal primary pointer Downs likewise pass through a bookkeeping-only
   `UiModel::pointer` gate before browser hit dispatch, so a browser click held
   through Close cannot become an instrument press. Main tracks whether capture
   belongs to the instrument or browser scrollbar; the single primary pointer
   cannot acquire both. Close/resize may end only the browser's own scrollbar
   drag, with physical-down suppression retained until Up.
4. New playing-key Down while modal/text entry is active produces no note.
   Closing while it is held does not retrigger it on repeat; only a subsequent
   real Up followed by a fresh Down can start a new note. A playing key held
   before opening retains its original note until its real Up.
5. MIDI reception, controller merges and copied snapshot observation continue.
   The browser does not reset MIDI owners or swallow MIDI note Off. Registration
   recall preserves the latest desired expression, including pending CC11.
6. Genuine window deactivation, hide/minimize, audio-device removal, recovery,
   quit and explicit Panic retain their established policy. Distinguish those
   events in evidence from opening/closing this browser.

Browser pointer actions are restricted to the panel. Clicking outside it does
nothing and cannot play a key or activate an underlying header control. Opening
while a pointer note is held therefore works through a keyboard-focused browser
button, or another already-authorized presentation input, until the original
pointer is released. Opening while a parameter drag is held likewise requires
a keyboard action; a second primary Down must not be fabricated.

First opening focuses List; reopening restores its last browser focus if valid.
Close restores the saved instrument focus when still visible; otherwise it
focuses the common RegistrationBrowser control. Resize, Flat toggling and
renderer recreation do not restore suppressed presses or change the current
named reference. Main owns browser lifetime so pending results remain observable
after panel closure. Existing Audio/MIDI/Help modal policies are not silently
changed by this feature.

## 8. Required independent acceptance and evidence

Implementation starts only after independent review freezes both contracts.
The reviewer must inspect real source paths and reject hidden scope additions.
Builds remain root-coordinated and must use one coherent frozen source. The
following are required gates, not claims that A09 executed them.

| Gate | Required independent evidence |
| --- | --- |
| Scope and musical preservation | Registration with expression changing before/during recall; Performance including expression; all four banks, fixed/cancelled routes, pedal/percussion fields; exact historical state1–4 compatibility and all 47 IDs. No notes/source/percussion-history reset from browse/save/recall. |
| Selection versus application | Header arrows, list arrows, Enter/double-click, scope edit and Refresh never post controls. Delayed acknowledgment, rejection, overflow/recovery, no audio, timeout, supersession and selection changing during an operation never produce a false Applied/current name. |
| Legacy behavior | Existing Save/Load controls and shortcuts keep target, staging and dirty-baseline meaning; library save/recall leave that baseline independent. Save new never overwrites; malformed/ambiguous/stale entries remain explainable. |
| Held-input journeys | Separate keyboard, Space audition, pointer and synthetic/external MIDI holds, plus same-pitch UI/MIDI overlap. Open/close/resize/refresh/name typing/recall with those owners active; deliver physical Up over the modal and after close. Verify owner identity, no stuck/retriggered notes, unchanged source continuity and exactly-once capture release. Include Escape specifically. |
| Focus and geometry | All 74 Play, 13 Rotary/Service and seven browser stops both directions; unchanged eleven MIDI stops. Verify semantic uniqueness, positive bounds, selected/disabled/error focus, all row endpoints, scrollbar, every half-open shared edge, long names and return focus. |
| Text editor and input rate | Actual SDL text events and paste; caret/Shift-selection deletion; exact 48-byte limit and whole-event rejection; type `Sunday warm`/`CONtemporary` through incomplete drafts, then reject final reserved names; duplicate casefolded names; Name Enter does not save; fresh-Down versus permitted navigation/edit repeat, stale held keys and opening-event consumption; typing A/W/S/etc. makes no new notes. |
| Responsive/Flat | 960×700, 1280×900, 1672×941 in both skins; breakpoint neighbors including 1399/1400 width and 819/820 height; logical/drawable scales 1, 1.5 and 2. Invalid geometry preserves prior state. Existing deck/key quads and nonheader allocations remain identical. |
| Paint containment and text | Independent literal text/rect oracle for header and modal at the required sizes/scales. No unbounded full-textbox exemptions; complete selected name/scope/preview/reasons, unclipped focus and all legacy labels. Closed-browser same-state pixels outside the declared header/footer-text differences remain unchanged. |
| Native path | Real application event routing through SDL, library/files, `UiModel`, Session and acknowledged snapshots; unit merge tests alone do not establish the modal behavior. Exercise original Ups during pending acknowledgment, and queued Ups around bounded synchronous file work; record observed delays separately. |
| Runtime boundaries | No callback filesystem/catalog/string/UI work; copied lifetime-safe views; generation-safe late completions; opening/closing does not reconstruct Engine. Preserve the existing timing thresholds and record actual UI responsiveness separately. |

Existing relevant fixtures include `test_standalone_ui`, reference-layout,
workspace continuity/acceptance, external-control, preset-concurrency, scaled
view, input replay, workflows, native material/raster and install tests under
`apps/standalone/`. Update only the contract-affected expectations and add
meaningful browser-specific ownership, lifecycle and raster cases. Do not
weaken original thresholds or exempt whole header text regions to get a pass.

Capture the actual changed executable, not a mockup: closed selected-name
header and open browser at minimum/default/reference sizes; minimum Flat;
maximum-length name; selection differing from current; pending Recall; Applied;
Saved/current; Modified; invalid/empty/stale/No Audio and failure/unconfirmed
states. Use a compact admitted gallery plus deterministic raster/state evidence
where several states would otherwise duplicate full-size images. Retain the
source/tree or frozen production hashes, executable hash, compiler/configuration,
font/asset hashes, replay and saved-input identities, logical/drawable sizes,
backend, PNG and decoded-pixel hashes, commands and original failures.

Independent admission must compare the new reference-size header directly with
the unaltered 1672×941 JPEG and before image, review the three required sizes
and Flat, and document the exact bounded improvement. Root updates README and
current handoff only after that admission, preserving prior gallery identities.

## 9. Remaining 1:1 and product gaps stay visible

This proposal targets the absent top-right named-selection structure and adds
functional modern recall. The retained source has a PRESET label, a name and a
settings cog; this product needs explicit selection/application/scope meaning
and retains Save/Load/Help/Audio/MIDI/Panic/Flat. Those necessary functional
differences remain visible, even if the field placement and materials improve.

The reference's incorrect key counts/legends, scanner/rotary/microphone controls
and Stop button cannot replace the real 61+61+25 playing keys, 24 reversed
presets, correct footage and 0-to-8 drawbar direction. Deck/rack placement,
manual shaping, walnut/rim material, small-text/native-display usability and
broader composition remain outside this header slice and with their current
owners. The new modal itself has no complete reference counterpart.

**Literal whole-interface 1:1 equality remains unmet and unwaived.** Neither
this contract, a future scoped raster pass, nor an agent count closes native
semantic accessibility, real display/MIDI/audio-device usability, callback
deadlines, platform/DAW journeys, physical fidelity or signed distribution.
Those retain their existing source-specific gates in the full plan.
