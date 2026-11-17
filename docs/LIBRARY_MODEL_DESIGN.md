# LibraryModel copied-state and receipt design

**A07 implementation input, 16 November 2026. Independent A10 review and root
admission are required before implementation.** This makes the existing
[named-library contract](REGISTRATION_LIBRARY_CONTRACT.md) concrete at the
`LibraryModel` boundary. It does not amend its storage, scope, browser or release
requirements. The exact API is [LibraryModel.h](../apps/standalone/LibraryModel.h).

## 1. Delivered boundary and integration still required

This bounded M9 phase implements the single main-thread authority for copied
catalog, draft, selected entry, independently proved current reference, and one
named operation. It contains no filesystem calls, Session ownership, SDL,
callbacks, event pumping, worker thread or audio submission. Ordinary controls
remain owned by `UiModel`/`Session`; the model retains only copies and the
intent history needed to evaluate named-operation truth. Only a copied
`ControlSnapshot` may eventually cross the existing audio command boundary.

The implementation may allocate main-thread storage and uses the standard
library. Its PIMPL is not an audio-thread object. Counts and copied diagnostics
remain bounded by the existing storage constants. All 47 parameter identities,
state4/readers1–3, 91 shared sources, UUIDs, note owners, musical histories and
legacy saved-file baseline remain unchanged.

Native browser/main wiring is **not delivered by model tests**. That integration
must report every control intent, every actual post result and every audio
lifecycle boundary using this API; pass fresh coherent observations; dispatch
returned effects once; preserve legacy Save/Load and original key/pointer Ups;
and execute the existing browser/input/native qualification. A missing integration
hook cannot be compensated by a permissive model acknowledgement rule.

## 2. Owned identities and finite state

The model retains four separate identities:

| Identity | Establishment and lifetime |
| --- | --- |
| Selected key/preview | Explicit selection or admitted first catalog; presentation only |
| Latest control intent | Every valid ordinary or Recall whole-control intent, even equal values; monotonic desired revision |
| Named operation | One Recall or SaveNew, exact captured target/name/scope; never retargeted by selection/draft edits |
| Current reference | Proved Recall or successful acknowledged Save; independent copied baseline and origin |

IDs start at one, never wrap, and obey constructor limits for exhaustion tests.
Four counters are independent: operation IDs, desired revisions, synchronous
failure revisions and catalog generations. Zero is never a valid token. Reaching
a last issuable ID does not invalidate that issued operation; an attempted
increment beyond its limit permanently fails named mutation tracking closed with
`Exhausted`. Invalid arguments do not consume a desired revision. A failed post
does consume a failure revision even when it has no control token. Tracking
failure never blocks the existing instrument's ordinary UI/audio path.

One active named operation is allowed. `AwaitingSubmission`,
`AwaitingAcknowledgment`, `ReadyToSave` and `Saving` are busy phases. The last
terminal operation remains visible as `Finished` until a new accepted operation
replaces it. Refused/Busy requests have their own `action_outcome/reason` and do
not overwrite the active or previous receipt. Presentation selection, name and
scope changes never retarget or acknowledge an operation.

An internal receipt retains operation ID/kind/target, expected complete controls,
desired revision, original control sequence, starting publication revision,
recovery/rejection/discard counters, synchronous-failure revision, started/deadline
milliseconds, phase/outcome, and storage-effect/authorization consumption flags.
Save additionally retains its original acknowledgement basis and reserved
post-save catalog generation. The public view omits these full guard/baseline
copies while preserving selected, current and operation identities together.

## 3. Catalog, selection and untrusted copied inputs

`request_refresh` issues a unique generation and marks rows stale until its
result. `replace_catalog` accepts only the newest outstanding exact generation
once. Unsolicited, duplicate and late results return false and do not replace
rows, status, selection or a newer result. A complete admitted result replaces
the catalog transactionally. A failed or malformed result retains the last
complete catalog, sets `catalog_stale`, and records the actual latest failure.
Recall/Save are unavailable until a complete scan is admitted again.

Validate copied values even though normal callers use `RegistrationLibrary`:

- Every enum must be recognized. Complete catalogs contain at most 128 rows,
  at most 128 candidates and at most 512 directory items. Candidate count equals
  rows plus omitted invalid names; candidates do not exceed directory items.
  Invalid-entry and ambiguous counts agree with the respective row statuses.
  `Ready` has rows, `Empty` has no rows, and `MissingDirectory` has no rows/counts.
- Each retained row has a valid exact name, scope and key equal to that name
  plus its exact scope suffix. Keys are unique, sorted by the storage contract's
  ASCII folded-name/scope/exact-key order. Case-fold-equivalent name/scope rows
  must all be `Ambiguous`; neither may advertise valid controls.
- A `Valid` row requires a valid complete snapshot. Nonvalid rows carry no
  usable controls. A forged `Valid`/empty or invalid snapshot cannot enable an
  effect. Per-row/result detailed diagnostics are copied with a maximum of
  256 bytes; diagnostics may be truncated, never keys or names.
- A failed catalog's partial rows are never adopted. Preserve its recognized
  failure category and a bounded reason, without treating its rows or counters
  as a new complete directory observation.

Retain selection by exact key after refresh. The first successful nonempty scan
may select its first row, including a disabled row for inspection. If an existing
selected key disappears, clear selection and do not choose a replacement behind
the user. Later selection remains explicit. `select_relative` clamps in admitted
row order, does not wrap and handles the full `int` range without overflow; from
no selection a positive move chooses first, a negative move chooses last, and zero
does nothing. Failed scans can still display/select their retained stale rows.

Drafts use `is_valid_registration_name_draft`, allowing incomplete names; invalid
bytes or excess length reject the entire edit. Save uses the stronger final-name
policy. Scope changes accept only Registration/Performance and affect the Save
form alone. A current reference becomes Missing only from a **complete admitted
catalog** that lacks its exact key; scan failure preserves the prior Missing
flag. A catalog containing its disabled/changed row means the path is present,
not that its stored contents still equal the proved reference.

## 4. Fresh observations and the original control proof

`LibraryObservation` contains the result of the caller's just-completed
`Session::read_snapshot` and the actual command-enabled gate. `nullopt` represents
a failed read and cannot certify a completion from cached display. Supplying a
cached value as a fresh read violates the adapter contract; the model does not
claim to authenticate external reads. A same-revision fresh read is permitted
for a retained proved Save, but never newly acknowledges a post.

Validate snapshot controls, publication revision (even and nonzero for prepared
observations), `running => prepared`, `last_applied_sequence <= resolved_sequence`,
and monotonic publication/sequence/recovery/rejected/discard counters. Revision
zero is allowed only for an initial unprepared observation and provides no proof.
Two copies with the same publication revision must agree in **all fields**,
including holds, clock, sample rate, peak, lifecycle, counters, faults and status.
An older, malformed, conflicting or failed observation leaves the displayed
actual copy unchanged and sets freshness false. No such copy proves a basis or
receipt. Saturated recovery/rejected/discard counters cannot be captured as
unchanged-failure proof. Future same-value increments cannot be ruled out there.

The first admitted observation may initialize the tracked desired copy, but
creates **no control acknowledgement basis**. `note_control_intent` is called
before every ordinary complete-control intention and allocates a fresh desired
revision even for equal controls. It captures expected controls and the supplied
pre-post observation's publication/counters/failure revision. If that read fails,
the intention is still recorded but has no valid basis; a later matching snapshot
cannot manufacture the missing pre-post proof. A new intention supersedes every
unresolved named operation except storage already authorized at its linearization
point. It never submits anything itself.

`submitted` receives every real post/gate result exactly once. Accepted results
require nonzero strictly increasing sequences across reported posts. An ordinary
note result without a control token advances that sequencing observation but
cannot acknowledge controls. A control result must match the latest unsubmitted
revision **and** complete expected controls. Duplicate/stale/mismatched tokens
cannot attach a later sequence to an old intention. They fail named proof closed
with `ProtocolError`. A non-Ok result always advances synchronous-failure history,
including direct MIDI/recovery and the disabled-audio gate; do not report it a
second time through another hook. Non-Ok with nonzero sequence or Ok with zero
sequence is malformed, never accepted proof.

Only a fresh observation establishes an unproved control basis when all hold:

1. It is newer than that intent's **pre-post** publication revision.
2. Both resolved and last-applied sequences cover the exact accepted control
   sequence, which is nonzero.
3. Recovery/rejection/discard and synchronous-failure revisions equal the
   intent's captured values, and none was saturated.
4. Latest desired revision and complete desired/observed controls still equal
   that intent and its expected controls.

The retained basis is either unsubmitted, awaiting proof, proved, or invalid;
an invalid basis never becomes proved from a later unrelated sequence. Rejection
or recovery adopts actual observed control values both for display and the
tracked desired copy, clears optimistic pending state, and invalidates the
affected unproved basis. A synchronous failure uses the last admitted actual
copy, then a fresh observation updates it; it must not leave a failed optimistic
expression as the model's desired value. Adoption is not a new control intent
and does not manufacture a new proved basis. An older publication or completion
for a superseded intention must not overwrite a newer valid pending intention.
The future adapter supplies the same admitted actual observations to UiModel
and this model and reports failure/recovery in order, so their desired copies
agree before Save. Later ordinary
valid intentions can establish a new basis. A proved unchanged past copy can
survive unrelated later failures for a **new** Save request; that new request
captures the current fresh counters and still requires current controls to equal
the proved copy. An already-waiting Save is cancelled by the intervening failure.

`controls_pending` represents an actual unsubmitted/awaiting tracked intention,
not a difference from the named baseline. `current_reference.modified` compares
the latest admitted actual controls with its own baseline using the exact scope;
expression is ignored only for Registration. Failed reads preserve those actual
values and expose freshness false.

## 5. Recall transaction

The app first re-reads the exact selected key and passes that result plus a fresh
Session read and `UiModel::view().controls` at activation to `request_recall`.
The explicitly supplied latest desired controls are the sole expression merge
source; never substitute cached model or observed expression. Invalid latest
desired controls reject atomically. A new Recall intention does not retroactively
repair an absent or invalid previous acknowledgement basis. Reject a mismatched key/name/scope structure;
never load another selection. If the matching file is invalid/unavailable, update
that selected row's disabled diagnostic and issue no effect. If valid parsed
controls, name or scope differ from the preview, update the preview and return
`EntryChanged`; a second explicit Recall is required. Equivalent bytes/old format
with identical parsed controls are not a changed preview.

A catalog-level `Ambiguous` selected row stays non-recallable until a complete
admitted scan removes its collision. Reading one file successfully cannot clear
that directory-level condition. Updating a selected preview keeps the catalog's
derived invalid/ambiguous counts consistent; it changes no other row's identity.

Refuse before changing desired controls when busy, stale/unavailable catalog,
invalid entry, unavailable fresh observation, exhausted tracking, unprepared or
stopped audio, or disabled command dispatch. `NoAudio` neither stages a restart
intent nor allocates an audio command. A valid request captures its exact target,
merges scope from the **explicit latest desired expression**, allocates one named ID and
one desired revision, and returns exactly one `LibraryRecallIntent`. Its phase
is `AwaitingSubmission`, never Applied. The caller invokes the future
`UiModel::recall_controls` helper once and reports its single post result with
the returned control token. Do not call `note_control_intent` again for it.

After accepted post it waits for the original proof in section 4 and a fresh
receipt observation with matching guards. Only then set Applied and establish
the current reference with origin Recall. Selection and browser visibility do
not participate in the proof. A failed post or changed failure/recovery counters
produces Rejected; a newer desired intent is Superseded, which does not claim
the earlier queued command never executed. Stop/start/prepare cancels the wait.
Timeout is Unconfirmed and never promoted by a later snapshot.

## 6. Save transaction and its linearization point

`request_save_new` captures the exact valid draft name/scope, current desired
revision/controls, original control basis and fresh current counters. It requires
a complete nonstale catalog, a prepared observation and either the latest valid
pending basis or a proved unchanged retained basis. Unsubmitted, invalid or absent
bases cannot save. Candidate/directory capacity must allow one new entry; storage
still performs its mandatory fresh admission and atomic no-replace transaction.
A known current case-folded name/scope collision refuses with a diagnostic and
retains the draft. No optimistic default/UI copy is a Save source.

A waiting original basis moves to ReadyToSave only after proof. A proved unchanged
copy may already be ReadyToSave, including after audio has stopped. Readiness
does not write. `take_save_intent` performs another fresh guard check and moves
ReadyToSave to Saving **once**, returning the exact acknowledged snapshot and
captured target. It reserves a new catalog generation for the storage operation's
post-save scan. If reserving that generation fails, no storage effect is issued.

The app executes `save_registration_entry_new` synchronously with this copied
effect. Its mandatory authorizer calls `authorize_save(operation_id, fresh_read,
now_ms)`. It verifies the same operation and Saving phase, unconsumed permission,
deadline, latest desired revision/controls, original proved basis, current fresh
observed controls, control sequence coverage, prepared state and unchanged
receipt failure/counter guards. A failed read or changed guard returns false,
retains the name and exact reason, and cannot authorize cached values. The same
publication revision is sufficient for an already proved retained stopped copy.

**One true authorization is the linearization point.** It consumes the permission.
No main-thread event pump or asynchronous continuation is allowed before the
synchronous storage result. The audio callback may publish later; that later
observation cannot revoke the already valid past copy or undo a committed file.
Consequently an authorized Saving receipt survives subsequent control edits,
lifecycle notifications and timeout for the sole purpose of receiving its actual
matching storage result. Those events update current controls/basis normally;
the completed reference can correctly appear Modified. No second authorization,
storage effect or named request is allowed while the result is outstanding.

`complete_save` must match operation ID and captured key/name/scope/controls.
Known failed storage before authorization is SaveFailed; a matching failed result
after authorization also reports its real failure. A prior authorization refusal
keeps its original cancelled/unconfirmed outcome when storage returns
NotAuthorized. Unknown IDs and duplicate results are StaleResult and cannot
replace the current reference or terminal outcome. A reported successful commit
without the expected committed-entry metadata is **SavedWithWarning** with an
explicit inconsistent-result diagnostic; do not establish a false current
reference, claim the file is absent, automatically retry, or remove it.

A valid committed result establishes origin AcknowledgedSave from the staged
proved copy, with Saved or SavedWithWarning according to actual storage status.
It never submits audio, calls `UiModel::mark_saved`, or moves the legacy clean
baseline. This newly committed reference initially has Missing false; an older
pre-save catalog cannot establish its subsequent absence. A successful refresh
selects the exact new key. The returned storage
catalog normally has generation zero; the model validates it as a compound
result and assigns the generation reserved when its effect was issued. A newer
explicit Refresh, if one was issued, wins; the older compound catalog cannot
overwrite it. Failed refresh preserves existing rows/staleness and cannot turn
the already committed Save into a failed disk operation. The current reference
is retained even if the committed path becomes missing/invalid immediately.

## 7. Time, failure ordering and lifecycle

Use supplied monotonic integer milliseconds, never the wall clock. Store the
last admitted time. Regressing input cannot prove a transition or start an
operation. A request must allow `now_ms + 2000` without overflow; otherwise
return InvalidInput and issue nothing. No wraparound arithmetic is accepted.
At `now_ms >= deadline` an unresolved receipt is Unconfirmed **before** testing
a newly arriving acknowledgement. Failure to read does not stop timeout checks.

For a fresh pending observation, classify loss of tracking/invalidating intent,
lifecycle cancellation and changed failure guards before testing success. Preserve
the specific reason; new desired intent is Superseded, observed reject/recovery
is Rejected, stopped/disabled Recall or lifecycle change is Cancelled. Saturation
can never count as unchanged failure history. A malformed/old observation supplies
no proof and retains the prior actual display; a valid monotonic time can still
expire the pending receipt. Once terminal, none of those later observations
silently reopens it.

`audio_lifecycle_changed` must be called at every real Stop/Start/Prepare boundary,
including a rapid stop/start with no sampled stopped publication. It cancels
unresolved named waits and invalidates unproved bases. Prepare invalidates even
a proved basis. Stop/Start may retain a proved unchanged copy, which a new Save
must check against a fresh prepared observation. Observed running/prepared
transitions perform the same conservative cancellation as a backstop. Closing
the browser is not a lifecycle event and needs no model cancellation.

## 8. Required foundation acceptance

These are future gates, not executed results:

| Gate | Required independent cases |
| --- | --- |
| Catalog/draft identity | First/empty/missing/failed scan, stable selected key, removed selection, out-of-order/duplicate generations, malformed key/count/scope/order, exact bounds, invalid draft atomicity, current Missing only from complete scan |
| Scope and provenance | Literal expectations for all four banks, pedals, cancelled fixed memories, routes/percussion; pending expression preserved only by Registration; selected/current/operation names never substitute for one another |
| Original acknowledgement | Real Session delayed render; equal-control Recall has a new nonzero sequence; unrelated note sequence, discarded/rejected controls and recaptured later counters never create proof; startup has no default proof |
| Interleaving | Same-value newer desired intention, direct-MIDI failure without token, failed/stale/conflicting observations, stopped/disabled Recall, rapid stop/start hook, prepare invalidation, two-second boundary, late result, all four injected exhaustion limits |
| Save authority | Waiting versus proved basis, stopped proved copy, one effect/one authorization, precommit changed intent/failure/read, no overwritten target, retained SavedWithWarning and failed refresh, changed controls after authorization, inconsistent/late storage results |
| Runtime separation | No Session/SDL/filesystem calls in model; real Session harness confirms scope restore leaves original held-note owners and frame/phase continuity; no native-browser/input/platform claim from those tests |

Root owns CMake and coherent execution. The foundation's pass is a completed
copied-state/receipt layer; the browser, main adapter hooks, real SDL input
journeys, whole-interface 1:1 and release gates retain their separate acceptance.
