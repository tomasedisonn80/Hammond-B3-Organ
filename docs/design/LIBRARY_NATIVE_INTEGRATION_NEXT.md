# Native library integration: next implementation

**A33 planning handoff, 17 November 2026.** Root must assign and independently
admit the implementation below. This document changes no contract, source or
acceptance result. The [frozen library contract](../REGISTRATION_LIBRARY_CONTRACT.md),
[model design/API](../LIBRARY_MODEL_DESIGN.md) and
[browser contract](../REGISTRATION_BROWSER_UI_CONTRACT.md) remain authoritative.

## 1. Starting point and ordered ownership

`RegistrationLibrary` storage, the copied-state `LibraryModel`, and A26's
`UiModel::recall_controls` are present. Root's
[integrated receipt](../development/2026-11-16-console-completion/reports/library-integrated-result.json)
records five passing harnesses: `test_standalone_library_model`, `_session`,
`_storage`, `_recall` and `_roundtrip`. A28's
[real roundtrip source](../../apps/standalone/tests/test_standalone_library_roundtrip.cpp)
joins actual UiActions, Session reads/posts/render and create-only storage. Its
startup case deliberately requires a new post-Start intention. These are bounded
foundation checks; [main.cpp](../../apps/standalone/main.cpp) has no LibraryModel,
browser, `--library`, named storage or receipt hooks. Gesture/modal entry helpers
also remain absent. Earlier patch-only A26/A28 notes retain their dated meaning.

Implement in this dependency order, with one root-assigned owner per shared file:

| Step / bounded owner | Files and completion needed before dependents |
| --- | --- |
| 1. Integration contract owner | Review this hook/order plan against current source. Freeze a small read-only availability addition to `LibraryModel.h/.cpp` and its design: basis state/revision/sequence plus Save-request availability/reason. Current `LibraryView::controls_pending == false` cannot distinguish unproved startup from a proved stopped copy. Derive this projection inside the model; do not duplicate receipt guards in a browser or probe a mutating request during paint. This additive API needs independent admission. |
| 2. Input/model owner | `UiModel.h/.cpp`: add the browser-input gate, parameter-gesture closure and validated focus restoration specified below. Retain A26's helper unchanged unless a separately reviewed defect requires repair. SDK-free input tests precede native wiring. |
| 3. Adapter owner | `main.cpp`: own root/options, fresh observation, submission/lifecycle routing, startup proof and synchronous effects. No Session/Engine protocol change. Root serializes this owner's edits with step 2 and later header integration. |
| 4. Browser/painter owner | New `RegistrationBrowserModel.h/.cpp`, `RegistrationBrowserView.h/.cpp`; root-assigned `InstrumentView.h/.cpp` and UiModel header/layout edits. Browser owns focus/caret/scroll only and consumes copied `LibraryView`. Reconcile the older browser contract's header baseline with the current accepted title/header and the separate H1 owner before freezing paint support. |
| 5. Independent acceptance / root | New adapter/native journey tests, affected existing tests, CMake/CI and actual captures; root alone integrates, builds, accepts and publishes. Model/API, input, native paint and device acceptance remain distinct. |

Preserve 47 parameter IDs, `B3CONTROLS4`/readers 1–3, 91 shared free-running
sources, UUIDs and the nominal dry Engine. Retain all 147 playing keys, 24 presets,
four banks and 68 existing controls. The browser contract's explicit append-only
presentation additions do not renumber or remove that inventory. Contact/audio,
ScannerLineFoh, crossover/native MIDI retirement, R4/R5/R6, H1/material and native
accessibility owners retain their unfinished scopes; this plan transfers none.

## 2. Exact adapter hook map

References below are members of `Application` in [main.cpp][main] unless named
otherwise. Keep one LibraryModel alive for the application, including while the
panel is closed. Use `SDL_GetTicks64()` consistently for monotonic receipt time.

| Existing point | Required integration |
| --- | --- |
| `Options`, `usage`, `parse_options`; `initialize`, `choose_state_path` | Add `--library DIR`; resolve once with `resolve_registration_library_root`. Omission uses `SDL_GetPrefPath(...)/registrations` independently of custom `--state`. Retain resolution failure as unavailable, never choose a fallback. Opening/Refresh scans; startup recalls no entry and creates no library directory. |
| `dispatch` → every `ControlSnapshot` action | Before posting, call `note_control_intent(payload, just_completed_read)` once, even for equal payloads. This covers pointer/keyboard/preset edits, running legacy Load, startup/retained restore and `process_midi` → `external_parameter`. Empty UiActions are not posts. A named Recall carries its already issued token instead; never register it again. |
| `dispatch` ordinary post and its bounded recovery loop | Immediately report each real `SubmitResult` to `LibraryModel::submitted`, including `{NotRunning,0}` from the existing disabled gate, before another post. Preserve UiModel reporting, `record_accepted` and the existing single recovery batch. Stop the original batch on failure. Failed tracking disables named mutations, not ordinary instrument operation. |
| `post_midi_command`; `retire_midi`; `process_midi` | Report every direct note/release result to LibraryModel without a control token. Preserve the deliberate bypass of `UiModel::submitted` here; a MIDI rejection must not acquire a new UI-release policy. Retirement batches also use this path. CC11 continues through `external_parameter`/ordinary dispatch once; no second raw CC command. |
| `load_state` stopped branch; `load_startup_state` | Record a successfully parsed staged whole-control intention even though no post occurs. Keep `intended_controls_` explicit and Save unavailable; invent no submission result. The later real restore has its own post token. Preserve generic Load's complete-file expression and legacy baseline semantics. |
| `observe` and every receipt/request/effect/authorizer read | Split a side-effect-free fresh reader from observation-triggered MIDI retirement. Pass the actual optional read and `commands_enabled_`. Loop read failures still call `observe({nullopt, gate}, now)` so timeouts advance; request/effect APIs receive their own read result. Deliver the same admitted actual controls to UiModel. Never wrap cached `snapshot_` as fresh proof or dispatch recovery inside the storage authorizer. |
| `open_audio`; shutdown in `run`/destructor; `activate_modal`; device-removal branch; `monitor_audio` | Centralize lifecycle wrappers. Successful `AudioDevice::open` means real Prepare; successful `start` means Start. Every real close/stop, including failed-start cleanup, reports Stop and disables dispatch. Hook before accepting another intent/observation; a rapid restart cannot skip notification. No-op repeated close is not a new boundary. |

The lifecycle fact comes from [AudioDevice.cpp][audio] `open/start/stop/close`:
open prepares paused; start calls Session then unpauses; close joins callbacks
before Session stop. [Session.cpp][session] `Impl::prepare/start/stop`, `render`
and `discard_through` explain why accepted, resolved and applied differ. Keep
their code and callback ownership intact. Deferred observation side effects run
after the current receipt transition, outside the storage transaction, so a
failure is counted once and fresh copies remain ordered.

## 3. Startup/restart: require real post-Start proof

Current `open_audio` queues `restore` before `audio_.start`, then assigns
`intended_sequence_ = last_control_sequence_`. Start invalidates that unproved
LibraryModel basis even if the callback subsequently applies its bytes. A28's
`startup_requires_a_new_post_start_receipt` demonstrates this exact distinction.
Do not suppress the Start hook, reuse the old token, manufacture an accepted
sequence, or infer proof from the constructor/default/retained snapshot.

The proposed adapter preserves paused restore for initial sound, then issues
**one new ordinary whole-control intention after Start**. Freeze this ordering:

```text
capture immutable restore controls; open audio successfully
notify Prepare; fresh read; dispatch the existing paused restore with its token
start successfully; notify Start immediately
fresh read and observe the started state before issuing any new token
if read is valid/running, restore was accepted, and original failure guards match:
    dispatch ui.recall_controls(restore) as an ordinary new control intention
    retain this new revision/sequence as the startup proof requirement
else:
    leave named Save unavailable; show the actual failure/unconfirmed reason
```

The post-Start helper call is a baseline-preserving forced snapshot publisher,
not a named Recall: it creates no selected/current entry. Its own newer coherent
publication, nonzero resolved **and** applied sequence coverage, unchanged
recovery/rejection/discard/synchronous-failure guards and exact desired/actual
controls must prove it. The initial legacy `load_controls` alone sets its saved
baseline. No input/MIDI drain intervenes in this short sequence. A failed read,
post or start triggers no automatic reassertion loop; a later explicit valid edit
or Recall can establish a new basis. A later edit supersedes the startup token
and must not be overwritten by delayed restore work.

Replace the startup-completion use of `observe`'s current sequence/value shortcut
with the reviewed model-owned proof projection. Tag `intended_controls_` with its
startup/restart/stopped-Load origin and the matching revision/sequence. Clear an
in-flight restore only on its proof or an explicit newer running control intent
that supersedes it; the latter must never replay the old restore. Preserve a
newer stopped Load's separate staging identity. Prepare invalidates even a proved
copy. Stop/Start without Prepare may retain a previously proved unchanged copy
for a new Save, but never revive an outstanding named operation. Stopped named
Recall returns No Audio without changing desired controls or staging work.

## 4. Browser entry, focus and original releases

Add dedicated `open_registration_browser`/close routing. Existing `open_overlay`
calls `lose_input(FocusLost)` and is unsuitable. In [UiModel.cpp][ui], `key`
handles Escape before its text gate, and `pointer` currently hit-tests every
fresh Down. Add `set_browser_input_active` after real Down bookkeeping but before
Escape/performance/hit activation; keep actual Up/CaptureLost handling first.
This is separate from `set_text_entry_active`.

`close_parameter_gesture` clears only `drag_`, keeps its last desired value,
suppresses a physically held pointer until its real Up and emits no command.
It reports whether capture belonged solely to that drag. Main releases that
capture once, retaining pointer-note capture and keyboard/Space owners. Modal
motion cannot glissando a pre-held note, including after Close until Up.
Never simulate Up, Escape, ReleaseUiNotes, Panic or MIDI retirement on entry/exit.

In `handle_key`/`handle_event`, forward every real keyboard/Space Up and primary
pointer Up to original UiModel ownership first, then browser bookkeeping even
after Close. Maintain browser physical-Down bookkeeping outside the modal too,
so pre-held keys cannot acquire a browser action by repeating. Browser Downs
record suppression without playing; keys held through Close cannot activate on
repeat. Consume the opening event once. Track the single
pointer's instrument-versus-scrollbar capture; genuine capture/window loss keeps
the established release policy. Add SDL text/paste/wheel routing only to the
browser, with whole-edit 48-byte validation and its frozen repeat rules. Apply
each browser intent to LibraryModel and return its new copied view before the
next input event. MIDI and fresh observation continue normally.

Remember/restore a validated instrument focus; first opening focuses List and
later openings restore browser focus. Resize/Flat changes close only relevant
gestures, preserving selection, draft, receipts and original owners. Closing
the panel hides accepted work without cancelling it. Preserve existing
Audio/MIDI/Help modal behavior and eleven MIDI focus stops.

## 5. Recall, Save enablement and disk completion

Refresh uses `request_refresh` → bounded `scan_registration_library(root,
generation)` → `replace_catalog`; no partial catalog is installed. Selection is
the exact key, never row index; disappearing selection clears without replacement.
Failed scans retain visibly stale rows and disable mutation. Only a complete
scan may mark the retained current reference Source missing. Ambiguous rows stay
disabled until a complete scan resolves their collision; a successful leaf read
cannot clear ambiguity.

Recall re-reads that exact selected key, takes a fresh observation and the latest
`ui_.view().controls`, then calls `request_recall`. EntryChanged updates preview
and requires another explicit Recall. Pass its returned token through exactly
one `ui_.recall_controls` action. Registration retains current **desired**
expression, including pending CC11; Performance restores saved expression.
Neither edits banks/focus/owners/history. Generic legacy Load still restores all
fields regardless of suffix. Applied/current changes only on model proof.

For Save new, combine model-owned availability with the app's unresolved staged
startup/Load gate. Availability requires a valid literal draft/scope, complete
nonstale catalog, capacity/no known name collision, no busy/exhausted operation,
fresh prepared observation and a valid submitted awaiting or proved basis.
An awaiting basis may accept a Save request but cannot emit storage yet. A proved
unchanged stopped copy may save; unprepared/default/staged/discarded copies may
not. The button's copied availability is advisory: every activation rechecks a
fresh read. Do not derive authorization from `controls_pending`, a selected name
or legacy `PendingSave`; do not move receipt authority into the browser.

At request and later loop turns, call `request_save_new` and then
`take_save_intent` only with their own fresh reads. Execute the one returned
effect synchronously, bound to its immutable ID/name/scope/controls:

```text
result = save_registration_entry_new(root, effect.name, effect.scope,
    effect.acknowledged_controls, all_five_protected_paths, [&] {
        return library.authorize_save(effect.operation_id, fresh_read(), now());
    })
library.complete_save(effect.operation_id, result)  // exactly once
```

Use the real [RegistrationLibrary.cpp][storage] helper's final authorization
after staging/admission, immediately before `publish_new`. Protect `--state`,
diagnostics, screenshot and both replay inputs, including absent aliases and
root/staging creation. No SDL event pump, replay delivery, MIDI drain, post,
async continuation or reentrant general `observe()` may intervene between true
authorization and commit/returned completion. The callback may publish afterward;
this does not undo the valid saved past copy. Main may process deferred recovery
and queued physical Ups after the synchronous result; measure the actual delay.

Report disk failures and NotAuthorized truthfully, retain the draft, and require
an explicit retry. Committed cleanup/refresh failure is SavedWithWarning; never
delete/retry the committed file. Let `complete_save` handle its reserved catalog
generation and current reference. Named Save never calls `mark_saved` or changes
`--state`. Legacy dirty remains comparison with its own saved baseline; named
Modified uses actual controls and ignores expression only for Registration.
Keep selected preview, current origin, pending controls and operation target/result
visible separately. Same-value new intentions supersede waits; timeout is terminal
Unconfirmed, late observation updates actual sound only, and recovery adopts
actual controls without guessing rollback or erasing the previous proved name.

## 6. Required acceptance before describing native integration as complete

Run source-bound adapter tests and **actual application routing**, not just the
five existing harnesses:

1. Startup with default/file/missing/invalid state; successful and failed Start;
   post-Start proof before Save; failed reads, stopped legacy staging, rapid
   Stop/Start and Prepare. Prove no pre-Start/default basis or late resurrection.
2. Held keyboard, Space, pointer and MIDI owners with same-pitch overlap through
   open/close/Escape/typing/resize/Flat/Refresh/Recall. Deliver original Ups over
   and after the modal; check no extra release/retrigger and exactly-once capture.
3. Both scopes with pending CC11, equal Recall/newer equal intent, delayed/failed
   reads, direct-MIDI rejection, overflow/recovery, timeout and a different
   selection during pending work. Compare actual controls and both baselines.
4. Real named save/readback; stopped proved Save; missing root, invalid/stale/
   ambiguous/changed selection, collision and protected paths; precommit intent/
   failure/lifecycle/read refusal, postcommit warning and queued physical Ups.
5. Frozen browser focus/text/geometry cases and minimum/default/reference/Flat
   captures, before/after containment and full-frame independent review. Retain
   source/executable/state/pixel identities and original failures; update README
   only from admitted actual captures. Run affected coherent regression,
   sanitizers and exact-source Linux/Windows/macOS storage/native paths.

Dummy SDL and SDK-free tests qualify their recorded software scopes only. Real
display/DPI/input/audio/MIDI journeys, native accessibility, callback deadlines/
retirement, physical fidelity, signed release and literal whole-interface 1:1
remain open until separately observed and accepted. Planning closes none.

[main]: ../../apps/standalone/main.cpp
[ui]: ../../apps/standalone/UiModel.cpp
[audio]: ../../apps/standalone/AudioDevice.cpp
[session]: ../../apps/standalone/Session.cpp
[storage]: ../../apps/standalone/RegistrationLibrary.cpp
