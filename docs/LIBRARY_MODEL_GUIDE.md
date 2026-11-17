# LibraryModel developer guide

The implemented `LibraryModel` owns main-thread copied state and named-operation
receipts. `UiModel::recall_controls` publishes its validated control effect.
**Native browser and `main.cpp` integration are absent.** Current user-facing
named-file workflows remain the CLI and generic Load described in the
[registration guide](REGISTRATION_GUIDE.md). Generic Load restores the complete
file, including expression, regardless of suffix. The native `--library` option,
browser input routing and startup receipt hooks remain
[next implementation work](design/LIBRARY_NATIVE_INTEGRATION_NEXT.md).

Use the [frozen API](../apps/standalone/LibraryModel.h),
[implementation](../apps/standalone/LibraryModel.cpp),
[design](LIBRARY_MODEL_DESIGN.md) and
[source admission](reviews/LIBRARY_MODEL_SOURCE_ADMISSION.md) as authority.
Keep one model on the main thread. It owns no Session or filesystem handle and
performs no I/O; the caller executes scans and returned effects.

## Build the existing foundation

From the repository root, use CMake 3.21+, Python 3.10+ and a C++20 compiler.
The [support target](../apps/standalone/CMakeLists.txt)
`hammond_standalone_support` contains the model, UI helper, Session and storage;
this configuration needs no SDL2, RtMidi or VST3 SDK. Coordinate shared builds
with their owner; these commands describe a fresh developer build:

```sh
cmake -S . -B build-library -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_TESTING=ON -DHAMMOND_BUILD_STANDALONE=OFF \
  -DHAMMOND_BUILD_VST3=OFF -DHAMMOND_ENABLE_MIDI=OFF
cmake --build build-library --config Release --parallel 2 --target \
  test_standalone_library_model test_standalone_library_session \
  test_standalone_library_storage test_standalone_library_recall \
  test_standalone_library_roundtrip
ctest --test-dir build-library -C Release --output-on-failure --no-tests=error \
  -R '^test_standalone_library_(model|session|storage|recall|roundtrip)$'
```

## Keep identities separate

| Copied state | Meaning |
| --- | --- |
| `catalog`, scan status/staleness | Last complete admitted rows, plus the latest scan outcome |
| `selected_key`, `selected_preview` | Exact filename selected for inspection; selection submits nothing |
| `name_draft`, `save_scope` | Editable Save form; edits never retarget an accepted operation |
| `operation` | One captured target, sequence, phase and terminal outcome |
| `current_reference` | Independently proved Recall or acknowledged Save, with its own baseline and origin |

`controls_pending` tracks an unsubmitted/awaiting intention. Reference `modified`
compares actual admitted controls with its own scoped baseline; optimistic edits
do not establish modification. `missing` requires a complete admitted scan that
lacks the exact key. Scan failure preserves the prior reference and Missing flag.

Both scopes restore all four banks, pedals, routes, retained fixed memories and
percussion. **Registration** takes expression from the explicit latest
`ui.view().controls` at activation, including pending CC11. **Performance** takes
saved expression. Both files retain complete canonical `B3CONTROLS4` payloads;
neither stores notes, owners, phase or musical histories. See the
[scope contract](REGISTRATION_LIBRARY_CONTRACT.md).

## Track intention and proof

Call `note_control_intent` before every ordinary whole-control intention,
including equal values. Staged intentions with no post get no invented submission
result. Named Recall already returns its token: do not register it again.
Report **every actual post or disabled-gate result once**, synchronously, through
`submitted`, including direct MIDI and recovery failures. Only the matching
control post carries its token; tokenless success supplies no control basis.

Accepted means queued. Applied requires a newer coherent publication, both
`resolved_sequence` and `last_applied_sequence` covering the original nonzero
sequence, unchanged recovery/rejection/discard/submission-failure guards, and the
same desired revision with exact desired/actual controls. A larger unrelated
sequence cannot repair discarded proof. UiModel's resolved Pending flag is
weaker than LibraryModel's Applied receipt.

Every observation comes from that call site's just-completed
`Session::read_snapshot`; failure is `nullopt`, never cached display. Pass
monotonic milliseconds to timed calls. At the 2,000-ms deadline, Unconfirmed
precedes a newly arriving acknowledgement. Failed reads still advance timeout;
terminal receipts never reopen. Saturated guards and exhausted IDs fail named
mutations closed without disabling ordinary instrument operation.

Notify `audio_lifecycle_changed` at every real Stop/Start/Prepare boundary, even
without a sampled stopped state. All invalidate unproved bases and outstanding
waits; Prepare also invalidates proved bases. Stop/Start can retain an unchanged
proved past copy for a new Save. A pre-Start queued restore supplies no post-Start
proof: startup needs a new properly observed intention.

## One Recall journey

This is adapter pseudocode, not existing native wiring. Assume lifecycle hooks,
resolved root, a complete refreshed catalog and explicit selection. `gate` is
the actual dispatch gate; `now()` is monotonic milliseconds; `show` means caller
presentation. The [roundtrip harness](../apps/standalone/tests/test_standalone_library_roundtrip.cpp)
contains concrete existing examples.

```text
fresh():
    SessionSnapshot s
    return session.read_snapshot(s) ? LibraryObservation{s, gate}
                                    : LibraryObservation{nullopt, gate}

entry = read_registration_entry(root, *library.view().selected_key)
o = fresh()
r = library.request_recall(entry, ui.view().controls, o, now())
if o.snapshot and library.view().observation_fresh: ui.observe(*o.snapshot)
if not r.recall: show(r.outcome, r.reason); return
token = r.recall->control_intent
actions = ui.recall_controls(token.expected_controls)
assert actions.count == 1
command = get<SessionCommand>(actions.items[0])
posted = gate ? session.post(command) : SubmitResult{SessionStatus::NotRunning, 0}
show(library.submitted(posted, token), posted)
recovery = ui.submitted(command, posted)
for action in recovery.span():             # existing bounded recovery, no retry loop
    c = get<SessionCommand>(action)
    p = gate ? session.post(c) : SubmitResult{SessionStatus::NotRunning, 0}
    show(library.submitted(p), p)           # no control token for ReleaseUiNotes
    ui.submitted(c, p)

# Subsequent loop turns after ordinary audio processing:
o = fresh()
library.observe(o, now())                   # also call with nullopt
if o.snapshot and library.view().observation_fresh: ui.observe(*o.snapshot)
show(library.view(), ui.view())             # receipt, actual controls and pending separately
```

The [UI helper](../apps/standalone/UiModel.cpp) rejects invalid snapshots atomically
and emits one complete action even for equal controls. It preserves presentation,
held owners and the legacy saved baseline; gesture closure remains separate
future browser work. Named Save never calls `mark_saved`. Consequently legacy
`controls_dirty` can remain true after named Save, independently of scoped
reference `modified`.

## Save one acknowledged copy

Set the literal name/scope, then call `request_save_new` with its own fresh
observation. It can wait for the original submitted basis or use a proved,
unchanged prepared copy, including stopped audio. Defaults, unsubmitted/staged
controls and invalidated bases cannot save. Readiness itself writes nothing.

`take_save_intent` requires another fresh read and releases one immutable effect.
Call `save_registration_entry_new(root, effect.name, effect.scope,
effect.acknowledged_controls, protected_paths, authorizer)` synchronously.
Inside its mandatory authorizer, take another fresh read and return
`authorize_save(effect.operation_id, observation, now())`. Include all configured
state, diagnostics, screenshot and replay paths in protection.

One true authorization fixes the acknowledged copy immediately before no-replace
publication. **No event pumping, post or asynchronous continuation may intervene
before the synchronous result.** Return that exact result once to `complete_save`.
Later audio/control/lifecycle changes cannot undo a committed file or replace
its staged contents.

`Saved` and `SavedWithWarning` both mean committed. Failed cleanup/refresh remains
a warning: inspect and refresh, never automatically retry or delete the output.
Inconsistent committed metadata also yields a warning without establishing a
false reference. Failed storage yields `SaveFailed`; `NotAuthorized` preserves an
existing refusal outcome. Foreign/duplicate completions return `StaleResult`.
The model assigns its reserved generation to the helper's generation-zero
post-save scan; a newer explicit Refresh wins.

## Recover explicitly; respect bounds

Refresh with `request_refresh` → `scan_registration_library(root, generation)` →
`replace_catalog`; only the newest outstanding generation publishes once. Failed
scans retain stale rows and disable mutation. Fix the cause and refresh. Resolve
case ambiguity through a complete scan; a successful leaf read cannot clear it.
`EntryChanged` requires preview review and another explicit Recall. Removed
selection clears without choosing a replacement. Known name/scope collisions
refuse as `InvalidInput`; storage `NameExists` becomes `SaveFailed`. Retain the
draft, refresh and choose a distinct name. New same-value intentions supersede
unresolved work; failures/recovery adopt actual controls, never guessed rollback.

[Storage bounds](REGISTRATION_LIBRARY_CONTRACT.md#4-finite-names-scan-and-validation) are 48 ASCII name bytes,
128 candidates, 512 directory items, 256 diagnostic bytes, 16-KiB documents and
32 temporary-name attempts. The model retains one named operation and bounded
copied catalogs; views/PIMPL may allocate on the main thread. No file work,
strings or model ownership belongs in the audio callback. These bounds establish
no filesystem or callback deadline.

## Evidence and next action

The [source-bound integrated receipt](development/2026-11-16-console-completion/reports/library-integrated-result.json)
records all five suites passing:

| Suite suffix | Evidence boundary |
| --- | --- |
| `model` | 32 groups; synthetic catalogs/observations |
| `session` | 12 groups; real Session reads/render, ownership and continuity |
| `storage` | Nine groups; real filesystem, synthetic control proof |
| `recall` | Nine groups; synthetic public UiModel boundary inputs |
| `roundtrip` | Four journeys; real UI/model/Session/storage, 24 posts/reports and seven authorizations |

The distinct [SDK-free qualification](reviews/CONSOLE_HEADLESS_ADMISSION.md) passed
12/12 selected suites. The first full run finished 246/247 with its original
report-link integrity failure retained; the combined source then passed 78/78
affected tests. Separate documentary qualification, publication and exact-source
hosted outcomes remain in the
[live checkpoint](development/2026-11-16-console-completion/CHECKPOINT.md).
Root owns final acceptance/publication. Next, independently admit the
[native integration plan](design/LIBRARY_NATIVE_INTEGRATION_NEXT.md), including
model-owned Save availability, post-Start proof and modal input/gesture hooks,
before implementation and actual native journeys. These harnesses close no
device, accessibility, physical-fidelity or whole-interface 1:1 gate.
