# Native named registration library contract

Contract identity: `standalone-named-control-library-v1`, 15 November 2026.
This is the Wave 2 implementation specification for the
[next-phase session](development/2026-11-15-next-phase/README.md); it is not an
implementation or an executed acceptance result. The independent
[A11 review](development/2026-11-15-next-phase/notes/A11-library-review.md)
accepts the amended contract as implementation input; root admission precedes
implementation. The companion
[browser contract](REGISTRATION_BROWSER_UI_CONTRACT.md) owns presentation,
geometry, focus order and the reference comparison.

## 1. Purpose and preserved boundaries

Provide a small native browser for explicitly named musical-control snapshots.
Selecting an entry, showing its details, opening or closing the browser,
refreshing, and moving previous/next are presentation operations. Only **Recall**
submits sound controls. **Save new** writes an explicitly named new entry from
acknowledged controls. Neither action is automatic on selection or application
exit.

The source basis is atlas pp. 409, 416 and 418, interpreted in the complete
[A05](development/2026-11-15-next-phase/notes/A05-atlas.md) and
[A06](development/2026-11-15-next-phase/notes/A06-atlas.md) readings. These readings
proposed different possible registration scopes. This contract chooses the
explicit whole-registration scope below; it does not implement the narrower
inactive-bank editing proposal. The reversed preset keys and documentary fixed
registration catalog retain their existing meanings.

Preserve all **47 parameter identities**, the unchanged **`B3CONTROLS4`** writer
and readers **1–3**, the 91 free-running sources and the nominal dry Engine.
The library adds no sound parameter, VST3 state field, factory catalog, Engine
route, or separate live musical-state owner. A copied entry is saved control
data, never an Engine checkpoint. The current field definitions are in
[`ControlState.h`](../include/hammond/ControlState.h) and the
[control-state format](CONTROL_STATE_FORMAT.md).

## 2. Exact scopes

| Current `ControlSnapshot` field | Registration | Performance — current controls |
| --- | --- | --- |
| `drawbars` — Upper A/B and Lower A/B, all 36 positions | Restore all | Restore all |
| `pedal_drawbars` — both retained mixture positions | Restore both | Restore both |
| `selected_banks` — both remembered bank selections | Restore both | Restore both |
| `route_enabled` — both manual route bits | Restore both | Restore both |
| `fixed_registrations` — both remembered fixed modes, including while cancelled | Restore both | Restore both |
| `percussion` — enabled, harmonic, volume and decay | Restore all four | Restore all four |
| `expression` | Preserve the latest desired current value | Restore saved value |

For a valid Registration entry, form one complete candidate by copying its
controls and replacing `candidate.expression` with `ui.view().controls.expression`
at the instant of Recall. This includes an already pending UI or MIDI CC11 edit;
using the older applied snapshot here would lose that intent. Performance copies
the entire entry. Validate the final candidate, then publish exactly one copied
`ControlSnapshot` through the existing Session command path. No per-field replay
or second raw MIDI event accompanies it. Future snapshot fields require an
explicit contract review rather than silently broadening either scope.

Registration is not a silent preparation operation: it can change sounding
routes, fixed modes and percussion controls when Recall is pressed. The preview
must say so. It does not move the UI's edited banks, keyboard target, octave,
workspace, focus, camera or presentation. Neither scope stores or changes audio
devices, MIDI ports/channels/calibration, output settings, physical profiles,
scanner/rotary/microphone configuration, held notes or owners, contact
trajectories, percussion readiness, source phase, delay/filter histories or the
processing clock. Settings absent from today's snapshot are not promised by
the label **Performance — current controls**.

## 3. One file per entry; no new musical format

Use one flat directory and the following exact, case-sensitive suffixes:

| Filename | Entry name and recall scope |
| --- | --- |
| `Sunday warm.b3registration` | `Sunday warm`; Registration |
| `Sunday warm.b3performance` | `Sunday warm`; Performance — current controls |

Each file contains only the ordinary control document, with no prefix, envelope,
trailing metadata, sidecar or index. New saves call the existing serializer and
write canonical `B3CONTROLS4` bytes. The filename stem supplies the name and the
suffix supplies scope; these are native library presentation metadata. The same
stem may exist once in each scope, which the browser always identifies.

The full Registration payload retains the acknowledged expression value to keep
the canonical format intact, but library Registration recall ignores that saved
expression. An existing generic `--state` Load still restores the entire parsed
snapshot, regardless of filename suffix. This distinction is explicit in the
preview/help; this feature does not change the old reader's semantics.

For recognized library filenames, the unchanged parser may admit historical
versions 1–3 with their already defined migrations. Loading never rewrites them.
Unknown versions, malformed catalog identities and trailing data reject normally.
There is no new import UI in v1. Ordinary `.b3controls` files continue to belong
to legacy Save/Load; merely placing one in the directory does not infer a scope.

The CLI is `--library DIR`. Omission resolves to `registrations` under
the same SDL preference directory used for the default controls file, independently
of a custom `--state` path. Resolve a relative argument against the invocation's
working directory and retain an absolute root, resolving existing ancestors.
The resolved root is fixed for the invocation and is shown in the browser.
Existing symlink ancestors may resolve to a directory; a non-directory root is
invalid. If resolution fails, report Unavailable. No entry is
automatically recalled at startup. Opening or Refresh performs a scan; a missing
root reports Empty and creates nothing. Explicit Save new may create that one
root directory when its parent already exists. It does not recursively create
parents. Invalid roots and directory errors are reported without falling back
to the working directory or a different destination.

## 4. Finite names, scan and validation

Freeze these limits in the native library module:

| Bound | v1 value |
| --- | --- |
| `kRegistrationLibraryMaxNameBytes` | 48 ASCII bytes |
| `kRegistrationLibraryMaxEntries` | 128 candidate rows |
| `kRegistrationLibraryMaxDirectoryItems` | 512 directory items, plus at most one overflow sentinel |
| Per-entry document | Existing `kMaxControlStateBytes`: 16 KiB, with the existing one-byte overflow check |
| Temporary-name reservation attempts | 32 |
| Save/recall acknowledgment wait | Existing two-second native wait budget |
| Retained detailed diagnostic per row/operation | 256 bytes of display text; error category remains separately available |

A name has 1–48 bytes. Its first and last bytes are ASCII letters or digits;
interior bytes may additionally be spaces, hyphens and underscores. Accept the
literal name or reject it: do not silently trim, transliterate, truncate,
generate a name, append a numeric suffix or normalize it into another entry.
Reject the whole stems `CON`, `PRN`, `AUX`, `NUL`, `COM1`–`COM9` and
`LPT1`–`LPT9`, case-insensitively. Dots, separators, control bytes, non-ASCII text
and Windows path punctuation are already excluded by the character rule.
The text editor exposes this final-name restriction. Its separate bounded draft
may be empty, end in a space or temporarily equal a reserved stem while the user
types; Save new stays unavailable until the complete literal name is valid.
Invalid character input or an input/paste exceeding 48 bytes rejects the whole
edit without truncation. Draft editing never constructs a filesystem path.
Validation and case-folding use explicit ASCII ranges, independent of the process locale.
Inspect native filename code units before converting them to display strings;
an unrepresentable/non-ASCII stem is an invalid name, not an exception escaping
the scan or a lossy alias. A key is validated again at the file API boundary.

Scan nonrecursively on the main thread. Count every encountered directory item,
including unrelated files, directories, symlinks and temporary files, against
the directory bound. Every recognized-suffix item counts against the candidate
bound, including an invalid name or disabled row. Reject symlink or
other nonregular candidate files; do not follow them or traverse subdirectories.
Use the existing transactional bounded parser on each readable candidate.
File-size preflight is useful but never substitutes for the parser's byte bound.
Read from the same opened object whose regular-file identity is verified, using
a no-follow, nonblocking leaf open or an equivalent platform primitive. A
candidate replaced by a symlink or FIFO between inspection and opening must
neither be followed nor block waiting for a writer. The existing
`load_control_file` status-check-then-`ifstream` sequence alone does not meet this
requirement. Keep the read bounded to 16 KiB plus its overflow byte and feed that
copy to the unchanged parser. Report open/type/read/conversion errors explicitly.
This leaf guarantee does not claim isolation from arbitrary concurrent replacement
of ancestor directories or an adversarial filesystem namespace.

Validly named candidates with invalid, oversize, unreadable or nonregular payloads
remain visible as disabled rows with a bounded reason. Invalid filename stems
are omitted and counted in a visible scan warning; they never become path inputs
from a truncated display label. Case-insensitive duplicate stem-plus-scope keys
are Ambiguous and all corresponding rows are disabled. Sort complete admitted
rows by ASCII case-folded name, then scope, then exact filename, making repeated
successful scans deterministic. Selection identity is the exact relative
filename, not a row index; scope is immutable for that identity.

Assemble a complete new catalog before publishing it to the model. Exceeding
either count bound or an enumeration failure does not publish an arbitrary
prefix. Preserve the previous copied catalog, label it stale with the actual
failure, and disable Recall/Save new until a complete scan succeeds. Initial
failure has no rows. Empty, Missing directory, Invalid entry, Capacity exceeded
and Directory unavailable are distinguishable. A scan does not alter current
controls, the legacy clean baseline or the current-entry reference.

Before Recall, re-read and validate the exact selected path on the main thread.
Compare its resulting complete control snapshot and derived scope/name with the
copied preview selected by this request. If changed, publish the new preview and
report **Entry changed — review and Recall again** without submitting anything.
If unavailable or invalid, retain the diagnostic and disable that row. Equivalent
whitespace or historical encoding with identical parsed controls does not alter
the musical preview. Do not silently load another row when selection disappears.

These bounds bound application work and memory; they do not assert a wall-clock
filesystem deadline or native device performance result.

## 5. Create-only atomic Save new

Save new is the only library mutation in v1. There is no Replace, Delete, Rename,
autosave or implicit overwrite. If the name already exists for its scope,
including a case-insensitive equivalent, return `NameExists` and retain the draft
so the user can choose a different name. A preflight existence check alone is
not the no-overwrite guarantee.

Main-thread publication proceeds in this order:

1. Validate scope, literal name and the acknowledged snapshot. Perform a fresh
   complete bounded scan for availability, capacity and case-insensitive name
   collisions; a stale copied catalog cannot authorize a new file. At 128
   candidates or 512 directory items, Save new is unavailable: the committed
   entry must fit after owned staging is removed. Derive the one filename inside the
   configured root; never accept an arbitrary path from a browser row or name
   editor.
2. Compare that destination and every path this operation would create (including
   a missing root, staging directory and staging file) against all configured
   protected paths: `--state`,
   `--diagnostics`, `--screenshot`, `--input-script` and `--midi-script`. Use the
   existing native path-alias policy as a base: resolved paths through existing
   ancestors, and filesystem equivalence for existing paths. For absent leaves,
   also compare existing parent-directory identities and portable ASCII leaf
   names case-insensitively; lexical path equality alone misses case aliases on
   Windows and commonly configured macOS volumes. Resolve missing-parent suffixes
   against their existing ancestor; reject conservatively if distinctness cannot
   be established. Do not call `equivalent` on two absent leaves and interpret an
   unsupported comparison as proof of distinctness. Reject aliases before the
   corresponding creation or write. A not-yet-existing requested output reserves
   its destination as a file, so root or temporary-directory creation cannot
   consume it. The caller passes these paths to the library file operation; the
   painter never decides collision policy.
3. Serialize the acknowledged copy using `serialize_controls`. Reserve a unique
   owned temporary directory beside the destination, with at most 32 attempts;
   write the complete temporary file, flush it and check close success. Preserve
   the existing destination on every failure. The staged file is on the same
   filesystem as its destination.
4. Recheck protected destinations and complete bounded name/capacity admission.
   Count the owned staging directory normally; it disappears on successful
   cleanup, leaving room for the committed entry within the directory-item limit.
   Then, as the last check immediately before commit, require the caller's final
   authorization described in section 6. An authorization/admission failure
   removes only owned staging and leaves the destination absent or unchanged.
5. Publish with an **atomic no-replace** primitive. POSIX uses a hard link from the
   completed temporary file to the new destination, then removes only the owned
   staging name. Windows uses a same-volume move without a replace-existing flag.
   An equivalent proven no-replace primitive is acceptable. An ordinary replacing
   rename preceded by `exists()` is not acceptable; the current
   [`save_control_file`](../apps/standalone/StateFiles.cpp) replacement helper must
   not be reused as if it were create-only. Unsupported atomic publication fails
   safely; it does not fall back to a truncating write or replacing rename.
6. Report Saved only after the no-replace commit succeeds, then refresh/select
   the actual new entry. Remove only this operation's known temporary file and
   directory on failed publication. After a successful commit, cleanup or refresh
   failure is **Saved with warning**, because the new file exists; do not report
   a failed save, retry it automatically or remove the committed file. Preserve
   the exact I/O failure and actual resulting state.

The contract promises complete-file visibility and preservation of an existing
destination, including a destination created by another process between preflight
and commit. It does not claim power-loss durability beyond the actual platform
write/flush/move behavior. An external concurrent edit may introduce ambiguous
case variants or exceed catalog capacity after final admission; the next scan
reports that condition without discarding files. Atomic no-replace arbitrates
the exact destination path, not a global case-folded namespace on a case-sensitive
filesystem. The bounded complete checks establish case-folded uniqueness at
observation time; they do not promise a cross-process transaction over the entire
directory. No broad security, lock-file or background-watcher subsystem is required.

## 6. Acknowledgment, actual state and legacy dirty tracking

[`Session.h`](../apps/standalone/Session.h) explicitly says acceptance is queued,
not applied. `resolved_sequence` includes rejected/discarded commands;
`last_applied_sequence` alone can belong to a later command. Named operations
therefore own a main-thread receipt, separate from selection and drawing:

```text
LibraryOperationReceipt
  operation_id, kind (Recall | SaveNew), target key/name/scope
  expected_controls, desired_revision, submitted_sequence
  starting publication_revision, recovery_count, rejected_commands,
  discarded_commands, submission_failure_revision, deadline, phase,
  result category and diagnostic
```

The request IDs, desired-control revisions and submission-failure revision are
monotonic and never wrap; exhaustion makes named mutations unavailable with a
specific diagnostic. A saturated Session counter cannot prove that no later
failure occurred: reject a new receipt when any captured recovery/rejection/
discard count is saturated.
`desired_revision` changes for every new whole-control intent, including ordinary
UI/MIDI controls and legacy Load, even if a later intent returns to the same values.
A library receipt is never acknowledged by an older receipt, a new row selection,
an unrelated status message or a late result for another operation. One library
save/recall may wait at a time. Selection/preview remain usable while mutation
actions report Busy; no unbounded operation queue or automatic retries exist.
Increment `submission_failure_revision` on every synchronous failed Session post,
including the MIDI path that bypasses `UiModel::submitted`, recovery submissions
and the disabled-audio gate. Capture and compare that revision rather than
waiting for a later callback to publish its counters. A failed `read_snapshot`
preserves the previous display but supplies no fresh proof for a new completion.

### Recall

Freshly observe the Session, revalidate the selected copied preview, merge the
scope into the latest desired controls, and dispatch one snapshot through the
ordinary `UiModel`/Session path. A valid accepted result with nonzero sequence
becomes Pending. Do not mark the requested name as the current applied entry at
queue acceptance. If audio commands are disabled or audio is stopped, return
**No Audio — start audio to recall**, without changing desired controls, queuing
anything or staging an automatic recall for restart. Legacy Load's existing
stopped-audio staging remains separate and unchanged.

An operation becomes Applied only when a newer coherent observation establishes
all of the following:

- `publication_revision > starting publication_revision`,
  `resolved_sequence >= submitted_sequence` and
  `last_applied_sequence >= submitted_sequence`;
- recovery, rejected-command and discarded-command counts equal the receipt's
  captured values, and `submission_failure_revision` is unchanged;
- the desired-control revision is still the receipt's revision, desired controls
  still equal its candidate, and observed controls exactly equal the candidate.

A post rejection reports Rejected with the actual `SessionStatus` and follows the
existing single recovery path. Changed recovery/rejection/discard counters reject
the receipt; adopt actual observed controls and do not restore a guessed old or
requested value. A newer desired edit makes an unresolved recall **Superseded**;
it does not prove the earlier command never ran. A two-second timeout is
**Unconfirmed**, not Applied or a fabricated rejection: a queued command may
still resolve later. Retain that outcome; a later snapshot updates actual controls
but cannot silently promote an expired receipt. The user may make a new explicit
Recall. Audio stop/restart cancels any outstanding named receipt; no restart
resurrects it. Closing the browser alone does not cancel accepted work.

### Save new

Capture the explicit name/scope, desired controls, desired revision, latest
control sequence and the same observation counters, then wait as the existing
`request_save/complete_save` discipline does. Save only the coherent observed
`snapshot.controls` after the desired copy and its latest control sequence are
acknowledged and all captured counters/revision still match. Require a prepared
Session and a proven acknowledged control copy, with no unresolved startup/legacy
Load intention. Require both `resolved_sequence` and `last_applied_sequence` to
cover the recorded nonzero control sequence and no pending desired controls.
Retain the latest control intent's submission-time expected controls, revision,
sequence and failure/recovery counters until its proof is established by the
same matching rules as Recall. A Save request may reuse that proved basis or
wait for its proof; it cannot manufacture proof by recapturing counters after
that intent was rejected/discarded and pointing to a later unrelated applied
command. Once established, the basis records a valid past acknowledged copy;
the Save receipt also captures current observation counters for its own wait.
Never save optimistic values or an unprepared/default UI copy.
A previously acknowledged, unchanged retained copy may be saved after audio has
stopped; a pending, discarded or staged copy may not.

Any newly observed control intent, recovery, rejection, discard, disappearance of
the acknowledgment basis or timeout cancels an uncommitted save. After staging,
the caller performs a fresh coherent Session read and checks the entire receipt
again immediately before authorizing the atomic commit. This read is the save's
control-state linearization point: the exact staged controls must equal that
proved acknowledged copy. A retained stopped-audio copy may use the same
publication revision when its original nonzero sequence remains proved. No event
pump, asynchronous continuation or new main-thread intent may intervene between
that authorization and commit. An unsuccessful fresh read does not authorize
commit from a cached display; retain the draft and report its actual outcome.

Audio may publish after the final read. This contract does not claim one atomic
transaction spanning Session and the filesystem: a subsequent edit or recovery
does not invalidate a valid past acknowledged snapshot or undo a committed file.
It updates the live controls/Modified indication on the next observation. Keep
the name draft and actual diagnostic on cancellation. Successful publication can
establish the named
**current-entry reference** from the acknowledged copy without submitting an audio
command. Its origin is `AcknowledgedSave`, distinct from `Recall`; report Saved
or Saved/current, not “Recall applied”. A later failed refresh cannot reverse the
already successful disk operation.

### Two independent clean references

Add a `UiModel::recall_controls(candidate)` semantic operation that validates and
publishes exactly one whole candidate, even when equal to current controls, while
preserving `saved_controls_`. This supplies a new nonzero sequence for each
explicit Recall. Do not implement
it by calling today's `load_controls`, which replaces that legacy clean baseline
before acknowledgment. Normal `--state` Save/Load, Ctrl/Command+S/O, the state path
and their existing dirty semantics remain intact. Library saving never calls
`mark_saved`, changes `--state`, or clears unrelated dirty controls.
The legacy dirty flag still reflects comparison with that retained baseline: if
an explicit named recall happens to restore exactly the old saved controls, it
may correctly become clean without moving the baseline.

Retain one separate current-entry reference after a proved recall or acknowledged
save: key/name/scope, origin and its copied baseline controls. Compare actual
acknowledged controls to that reference using its scope. Expression-only changes
do not mark a Registration modified; they do mark a Performance modified. Pending
desired edits are a separate indicator until acknowledged. A removed file can
leave a labelled missing current-entry reference; it does not erase sound or
masquerade as a different row. A failed or superseded request never replaces a
previously proved reference. Selecting another row does not change it.

## 7. Native module and semantic API boundary

The following names define the interface roles; equivalent C++ names are allowed
only if the types, transactions and ownership remain explicit. No API below is
called by the audio callback.

Keep four native responsibilities separate: `RegistrationLibrary` owns storage,
admission and pure scope operations; `LibraryModel` owns the single mutable
catalog, draft, selected/current references and receipt transitions;
`RegistrationBrowserModel/View` owns presentation, focus and input intents; and
`main.cpp` orchestrates Session observation/submission, file operations and
capture. Browser intents route to the library model; only main executes their
I/O/audio effects and returns copied results to that same model. Do not duplicate
mutable catalog or receipt authority in the browser. Root assigns file/worker
ownership for these boundaries.

| API/data | Required meaning |
| --- | --- |
| `RegistrationScope { Registration, Performance }` | The exact table in section 2; no third inferred scope |
| `LibraryEntryKey` | Exact validated relative filename, stable across sorting/refresh |
| `LibraryEntry` | Owned key/name/scope, validity/reason, and optional validated copied `ControlSnapshot`; no live Engine pointer |
| `LibraryCatalog` | Complete bounded entries, scan generation/status and counted warnings |
| `scan_registration_library(root)` | Main-thread transactional bounded scan; failure does not replace the caller's previous catalog |
| `read_registration_entry(root, key)` | Main-thread bounded revalidation for selected preview/Recall; invalid key cannot escape root |
| `save_registration_entry_new(root, name, scope, acknowledged, protected_paths, authorize_commit)` | Section 5 create-only transaction; synchronous caller authorization after staging and immediately before commit; reports committed versus failed distinctly. An equivalent explicit staged-object/commit pair is permitted. |
| `merge_registration_controls(scope, entry, latest_desired, destination)` | Pure validated copy/merge; invalid input preserves destination |
| `registration_controls_equal(scope, a, b)` | Pure scoped comparison; Registration ignores expression only |
| `UiModel::recall_controls(candidate)` | One ordinary snapshot action, legacy clean baseline unchanged |
| `UiModel::close_parameter_gesture()` | Clears only a parameter drag; preserves note owners and emits no command. A physical pointer still down stays suppressed until its actual Up; an active note retains capture. |
| `LibraryModel::replace_catalog`, `select`, `select_relative`, `set_name`, `set_save_scope` | Main-thread presentation edits; no Session or filesystem calls |
| `LibraryModel::request_recall`, `request_save_new`, `request_refresh` | Produce explicit main-thread app intents; never become new Session variants |

The UI receives a copied `LibraryView`, not a filesystem iterator, file stream or
mutable library owner. Its bounded rows contain key/name/scope/validation/reason;
the selected preview contains the copied controls and explicit scope. Additional
fields are selection key, catalog generation/status, name draft and save scope
(Registration initially), independent current-entry key/name/scope/origin with
Modified/Missing flags, pending-desired indication, and operation
ID/kind/phase/target name/sequence/result. Full baselines and receipt bookkeeping
remain main-thread model/application data. Strings, paths, traversal, parsing,
formatting, allocation and file I/O never cross the Session/audio boundary.
The file module never acquires or owns a Session; the caller's synchronous
authorization hook supplies only a permit or a bounded failure result. Result
data distinguishes not committed, committed, and committed with cleanup/refresh
warning, and retains the committed key/scope/copied controls even if refresh fails.

Header selected name, selected preview, current-entry provenance and operation
result must be representable simultaneously. A single `current_preset_name`
string or one “success” boolean is insufficient. No catalog is duplicated as
mutable DSP state and no selection is encoded as a new sound parameter.

## 8. Browser entry and held-input continuity

Use the companion browser contract's presentation-only opening path. The current
`main.cpp::open_overlay` calls `lose_input(FocusLost)`, and `UiModel::key` processes
Escape before the text-entry gate; neither behavior can be inherited blindly.
Opening/closing/refreshing/selecting must not emit `ReleaseUiNotes`, Panic, MIDI
retirement or fabricated NoteOff/Up events.

Close an active parameter gesture without changing its last desired value. Keep
keyboard and Space-audition owners, original press identities and an active
pointer-note owner/capture until their real release. If the pointer owned only a
parameter drag, its capture can end without generating a musical release. Browser
key Downs, including Escape, enter modal navigation/text handling before
instrument activation while still maintaining physical-down/suppressed bookkeeping.
Every actual key Up and pointer Up is forwarded to the original owner-release
path before modal, focus, text or modifier gates. Do not resume a key held through
browser closure without a new physical Down. MIDI continues normally while the
browser is open. Actual window deactivation, capture loss, device removal, Panic
and transport recovery retain their existing, separately justified release policy.

## 9. Required implementation acceptance

| Gate | Required evidence |
| --- | --- |
| Scope and compatibility | Independent literal field expectations cover all four banks, pedals, cancelled fixed memory, route bits and percussion; pending CC11 is preserved by Registration and restored by Performance. All 47 IDs and existing version 1–4 fixtures retain meaning. |
| Baselines | Named recall/Save new preserve the legacy baseline; dirty reflects comparison with that baseline, including both retained unsaved expression and an exact return to saved values. Explicit legacy Save/Load retain their own behavior. Registration/Performance modified comparisons differ only for expression. |
| File admission | Empty/missing/unavailable roots, exact limits and one-over-limit cases, malformed/old/future payloads, invalid/reserved/nonrepresentable names, symlinks/nonregular files including replacement-before-open and FIFO, duplicate case variants, stable sort/selection and changed-before-recall cases. |
| Atomic create | Two concurrent creators of the same target yield exactly one complete valid winner and one collision; the loser preserves winner bytes. Inject write/flush/close/commit failures, inspect owned temporary cleanup, protected-path aliases including absent case-variant outputs and root/staging collisions, stale catalog capacity, and Saved-with-warning after committed cleanup/refresh failure. Run platform-specific path/publication checks; no check-then-overwrite path is accepted. |
| Receipt truth | Delayed acknowledgment, stale/failed snapshots and IDs, equal-control explicit Recall, queue acceptance without application, rejection/discard/recovery including the direct MIDI post path, same-values-newer intent, exhausted IDs/counters, timeout, stopped audio and restart. Inject changed receipts during staging and verify precommit cancellation; changes after final authorization never undo a committed file. Observe actual values and retained outcomes; no optimistic Applied name or automatic retry. |
| Input continuity | Actual SDL browser journey preserves independent keyboard/Space/pointer/MIDI owners through opening, preview, scope details and closing; original Ups release exactly their owners. Escape closes without scoped/global release. Drag closes without a forged musical event. |
| Runtime boundary | File work is confined to the main thread; only the existing fixed-size snapshot reaches Session. Verify no note resurrection, clock/phase reset or percussion-history reset caused by recall. |
| UI and release evidence | Companion minimum/wide/Flat captures and focused operation tests with source/executable/state/pixel identities; root retains actual failures, platform exclusions and unrun gates. |

These are required future checks, not results reported by this document. Scoped
browser acceptance does not close the whole-interface 1:1 objective, native
semantic accessibility, physical MIDI/display/audio-device usability, callback
deadlines, connected rotary audio or physical model fidelity.
