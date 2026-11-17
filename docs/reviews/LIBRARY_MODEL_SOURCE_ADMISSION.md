# LibraryModel independent source admission

**A21, 17 November 2026 UTC: ADMIT the exact source below as a bounded
main-thread copied-state and receipt foundation.** I identified no blocking
implementation defect in this review. This admission remains contingent on the
remaining storage, combined regression, sanitizer and exact-source platform
gates. Native browser presentation and main/UiModel integration are not delivered
by this source or the supporting tests.

Root retains integration, final acceptance and publication. The
[current session](../development/2026-11-16-console-completion/README.md),
[frozen design](../LIBRARY_MODEL_DESIGN.md) and
[A10 input admission](LIBRARY_MODEL_DESIGN_ADMISSION.md) define this boundary.
The complete M0–M9 plan and literal whole-interface 1:1 obligations remain open.

## Reviewed identities and method

The inspected checkout was
`/workspace/scratch/21cce69f7784/Hammond-B3-Organ`, on `main`, HEAD
`9d60dbf462a90fe422fd4e69757fe202264acb7c`, base tree
`6bfdb87625ea7626e1b7c30ce9e78bad622a5978`. The new model and its tests were
working-tree additions; the base commit alone does not identify them. These
independently recomputed SHA-256 identities bind this verdict:

| Input | SHA-256 |
| --- | --- |
| [LibraryModel.cpp](../../apps/standalone/LibraryModel.cpp), all 1,060 lines | `ae5348c731b0559a6816b75cc190622918ca89d1fe938dd56445d51591904b98` |
| [LibraryModel.h](../../apps/standalone/LibraryModel.h) | `4ea94b611e4fdc27ea48c6bad47ddf9ed99761f2e12ae264b7482ac8d3b093e2` |
| [LIBRARY_MODEL_DESIGN.md](../LIBRARY_MODEL_DESIGN.md) | `b85e37d18725b8b357460a5a9caaa58f38cb0114573ae7c1c1266ce72b150852` |
| [A10 design admission](LIBRARY_MODEL_DESIGN_ADMISSION.md) | `4244b3ec75daa722e43bf582259cbce521979af29bdfd1a28776461a4a3ddec9` |
| [Named-library contract](../REGISTRATION_LIBRARY_CONTRACT.md) | `4760d65b27aa154fd86ee09c2cda87bd30f532874cc1a35c62a5b359889703fa` |
| [Session.cpp](../../apps/standalone/Session.cpp) | `256c0ef82e5a6639b3437d01754a0b27673a9d4096fe099a8b66351818ef2ae3` |
| [Session.h](../../apps/standalone/Session.h) | `dc729465578ed02a8cb0640d07de679be33d731cdece947a09bce736bc84c929` |
| [RegistrationLibrary.cpp](../../apps/standalone/RegistrationLibrary.cpp) | `5a446bb7c3fde310fe4351ed891b3911197a4cd407ab548147f992e0b643fffc` |
| [RegistrationLibrary.h](../../apps/standalone/RegistrationLibrary.h) | `6a3d75bd9fac8f70520c0847f8f98f4a33dd013a4d26fbaa3555e966880100eb` |

I read the entire standing AGENTS instructions and M0–M9 plan, current scope,
checkpoint, actual ledger and atlas coverage receipt; the complete frozen
API/design/admission and named-library contract; the entire model, Session and
storage implementations; the complete independent A16, A19 and newly delivered
A20 test sources; and their retained result/failure records. Relevant main,
UiModel, Engine restore and control-validation paths were inspected directly.
I traced state transitions and arithmetic independently; the test counts were
not used as a substitute for that source argument. The compact
[review report](../development/2026-11-16-console-completion/reports/library-model-source-review.json)
records further evidence identities and gate limits.

This was source and evidence inspection. I ran no build, executable, filesystem
mutation experiment, native journey or sanitizer. Root's observed executions
below remain distinct from my review. Production, tests, build inputs and other
workers' files were left unchanged.

## Receipt truth and intent identity

`new_basis`, `submitted`, `receive`, `same_basis` and `proved_now` preserve the
original pre-post publication, sequence floor, complete expected controls,
desired revision and failure guards. A first prepared snapshot initializes a
displayed/desired copy without supplying a control basis. A failed original read
sets `original_observation_valid` false; matching later values or a larger
unrelated sequence cannot repair it. An accepted tokenless note post advances
submission sequencing without becoming a control acknowledgement.

Accepted control results must carry a nonzero increasing sequence and match the
latest unsubmitted token in revision and complete controls. An old, duplicate or
mismatched token cannot attach its sequence to a different intention. The narrow
stale-success path preserves a newer pending desired copy while still terminating
the named receipt with ProtocolError; a genuine failed post changes failure
history regardless of token age. Failure reporting includes tokenless results,
so a synchronous direct-MIDI or recovery failure can reject a wait before the
audio callback publishes its counters.

Every valid new whole-control intention allocates a revision even when its values
are equal. `note_control_intent` supersedes an unresolved operation before
receiving its pre-post observation. Selection, draft and Save-scope edits do not
alter an operation's captured target. The model's selected row, latest desired
copy, operation and current named reference have distinct storage and lifetimes.

New proof requires a newer coherent publication, both sequence fields covering
the original sequence, unchanged nonsaturated original guards, the same desired
revision and equal desired/actual complete controls. `receive` evaluates changed
guards before success. Once resolution covers an awaiting sequence without the
remaining proof, it invalidates that basis and leaves a terminal outcome. This
agrees with real `Session::render` and `discard_through`: resolution consumes a
slot, successful application separately advances `last_applied_sequence`, and
reject/recovery paths publish their changed counters. A later applied note can
cover a discarded control numerically without proving that control ever applied.

The retained
[resolved-receipt amendment](LIBRARY_RESOLVED_RECEIPT_ADMISSION.md) is therefore
justified by the real Session semantics. Its original A16 failure expected a
consumed-but-unapplied command to remain awaitable. The amended test separately
keeps an actually unconsumed command Awaiting and requires terminal Unconfirmed
for the resolved-only case, including a refusal to revive it with a later larger
applied sequence. The implementation hash is unchanged. This is a stronger
distinction between pending and consumed input, not a relaxed success condition.

The [recovered A16 text](../development/2026-11-16-console-completion/reports/source-history/test_standalone_library_model-A16.cpp.txt)
hashes exactly to the contemporaneously recorded `c26e8655…` identity. Root
reconstructed it by reversing the sole known amendment; it is not an untouched
original file or an original execution artifact. I independently checked the
full hash and the one-hunk difference against the current test. The
[restoration record](../development/2026-11-16-console-completion/reports/source-history/A16-source-restoration.json)
preserves that provenance, while the original failure log remains separate.

## Fresh copies, lifecycle and finite arithmetic

`valid_snapshot` rejects invalid controls, odd publication revisions, a prepared
revision zero, impossible running/unprepared state, applied-above-resolved
sequences, unsupported prepared sample rates, nonfinite/negative peaks, unknown
fault bits and unknown core status. Older publications and decreasing sequence,
recovery, overflow, rejection or discard counters are not admitted. Repeated
publication revisions require equality in every current SessionSnapshot field;
expression, sample rate and peak additionally compare their floating-point bits.
Invalid/failed copies retain actual display and cannot prove a transition.

The design deliberately trusts the caller to supply a just-completed read. A
copied value does not authenticate its origin. Source validation also does not
replace the explicit Stop/Start/Prepare hooks: a Prepare at the same rate, with
equal controls and a later clock, need not be inferable from snapshots alone.
Observed running/prepared/rate/clock changes provide a conservative backstop.
Unproved bases and unresolved named waits are cancelled at lifecycle boundaries;
Prepare invalidates even a proved basis. Stop/Start may retain an unchanged proved
past copy for a new stopped, prepared Save.

`admit_time` applies the two-second deadline before examining an arriving
acknowledgement. Failed reads still permit expiry; a terminal operation never
reopens. Regressing time supplies no proof, and request deadline addition is
checked against `UINT64_MAX - 2000` before arithmetic. Each of the four issuance
counters checks `counter < limit` before incrementing. Zero is never issued;
the last permitted token stays usable until another issuance attempt exhausts
tracking. An already authorized storage operation retains its real result even
when later tracking exhausts.

Actual `Modified` compares the current admitted snapshot with the independently
captured reference using its scope. Registration ignores expression only in that
comparison. Recall still requires proof of the complete merged snapshot, and
the merge takes the explicit validated latest desired expression supplied at
activation. Optimistic Pending is not an actual modification claim.

## Catalog admission, ownership and bounds

`valid_complete_catalog` bounds all row/count fields before adding rows and
omitted-name counts. The largest admitted row/candidate count is 128; directory
items are at most 512. Derived invalid/ambiguous counts are recomputed from
validated rows. Exact name/key/suffix/scope agreement, strict storage order,
unique exact keys and disabled case-fold collisions are checked before adoption.
Valid rows require a valid whole snapshot; disabled rows must not carry controls.
This matches the real scanner's omitted invalid names, disabled candidate rows,
scope ordering and separate ambiguity counts.

Only the newest outstanding explicit generation publishes once. Malformed or
failed scans retain the last complete catalog and its generation, label it stale,
and cannot newly infer Missing. Selection follows the exact key. A disappearing
selection clears without choosing a replacement; the first nonempty scan alone
may choose its first row. Relative movement widens both operands before addition
and clamps within at most 128 rows, including full-range positive/negative `int`.
Single-file revalidation cannot clear a catalog-level Ambiguous row. Changed
usable previews require a second explicit activation and recompute row counts.

All returned views, intents, references and receipts own their values. No live
Session, Engine, filesystem handle, callback, worker or iterator is stored.
The complete model contains no Session submission, filesystem operation, SDL
call, event pump or clock read. Its pure storage-helper calls validate/merge/
compare copies only. Names and keys are validated before copying; retained
diagnostics are limited to 256 bytes. Traversals are bounded by the admitted
catalog size. PIMPL construction and copied views may allocate on the main thread;
this review makes no callback-use, allocation-failure recovery or wall-clock
deadline claim.

## Save authority and truthful storage completion

`request_save_new` admits only a valid submitted original basis or an unchanged
proved one, with a fresh prepared observation and the current operation's own
failure guards. It cannot recapture counters to rehabilitate a discarded intent.
It fixes name, scope, key and controls independently of later form edits. The
copied catalog is a bounded preflight; the real helper performs fresh complete
capacity/name/protected-path checks before publication.

`take_save_intent` rechecks fresh proof, reserves its post-save catalog generation
before releasing an effect, and changes ReadyToSave to Saving once.
`authorize_save` requires the matching effect ID, Saving state, unconsumed
permission, valid time and the original proved basis under another fresh read.
Changing intent, guards, lifecycle or fresh-read availability before permission
refuses publication. A second effect or authorization is unavailable.

The existing storage implementation stages complete serialized bytes, verifies
write/flush/close and final admission, then invokes the synchronous authorizer
immediately before POSIX no-replace `link` or Windows move without a replace
flag. The model authorizes a past acknowledged copy at that point; it does not
pretend to make Session and the filesystem one atomic transaction. After true
authorization, later controls, time and lifecycle changes update display/basis
without changing the staged copy or cancelling the outstanding storage receipt.

`complete_save` accepts only the matching issued effect once. Foreign/duplicate
IDs cannot retarget the receipt or reference. Recognized failures report
SaveFailed, while a prior authorization refusal survives the matching
NotAuthorized completion. Reported commits with absent/malformed/mismatched
metadata or missing permission become SavedWithWarning and cannot establish a
false current reference. A valid authorized commit establishes AcknowledgedSave
from the staged copy without posting audio or moving the legacy saved baseline.
Malformed/absent/failed refresh cannot undo a committed file or trigger a retry.

The helper's real generation-zero postcommit scan is remapped to the reserved
generation. A newer explicit refresh wins. The new reference's Missing floor
prevents a precommit scan from retroactively claiming the new path absent; the
owned compound scan or a subsequently requested complete scan may establish
actual absence. This keeps committed disk truth, catalog availability and named
reference provenance separate.

## Independently inspected execution evidence

All executions in this table were performed by root and read back by A21. I read
the complete test sources as well as the logs and recomputed their hashes.

| Evidence | Observed result and limit |
| --- | --- |
| [A16 first run](../development/2026-11-16-console-completion/reports/library-model-first-test-receipt.json) | 32 groups / 3,225 assertions, one failed group at original test hash `c26e865596cfe60626ec0fe4eec37d57b2d7ec19ab1682ef94d9450b645b5dca`. Original failure is retained; recovered source contents are explicitly labelled reconstruction as described above. |
| [A16 amended run](../development/2026-11-16-console-completion/reports/library-model-resolution-result.json) | 32 groups / 3,250 assertions, zero failed groups; test hash `3229fee7d3cd0154eb27db6b550d3d34aff400156ec475afd68221c56199590d`. Pure copied catalogs/observations with independent literal scope expectations. |
| [A19 real Session run](../development/2026-11-16-console-completion/reports/library-session-result.json) | 12 groups / 42,634 assertions, zero failed groups; test hash `1419ac417025600ea40262151a8d9b19a88d15812fb1ce0ee32255ae12237279`. Real fresh reads, 150 manual renders, actual overflow/rejection/discard and lifecycle paths. |
| [A20 storage run](../development/2026-11-16-console-completion/reports/library-storage-result.json), delivered during this review | Nine groups / 1,115 checks, zero failures; test hash `01143f1a7b0e64f00083bd2c07b0afe0cfbad7f9e044c44eb316e534c01c1793`. Real create-only filesystem with explicitly synthetic control-proof inputs. |

A19's audible fixture compares the returned effect against separately specified
controls in a second Session and physical events in an Engine. It includes
nonzero-audio checks, original overlapping-owner releases, silent/disconnected
advancement, all three Session rates and separate nominal phase/percussion
recurrences. Its 6,252 paired stereo samples, 10,101 phase checks and 60 history
checks remain bounded software observations. Hidden Session phases are not
directly exposed, and this supplies no native browser/device or physical claim.

A20 checks literal canonical bytes before authorization, a fresh read inside the
actual storage callback, existing and late exact-path collisions, all five
staging refusal classes, stale effect IDs, generation-zero refresh and a genuine
committed capacity-warning result. Its injections occur before final permission;
later control changes are introduced after the synchronous storage call returns.
It does not join real Session proof and disk publication in one adapter journey
or execute every platform/fault path of the existing storage contract.

## Concrete remaining integration and admission work

1. Root must qualify the coherent model/Session/storage consumers together,
   including existing related suites, required sanitizer selections and actual
   exact-source Windows/macOS/Linux gates. Preserve failures and unacquired or
   unrun jobs distinctly. A20's Linux boundary pass does not replace platform
   no-replace, path-alias and native filesystem qualification.
2. Add and independently test `UiModel::recall_controls` with one forced complete
   command even for equal values and the legacy saved reference unchanged.
   Today's `load_controls` assigns `saved_controls_` and is unsuitable. Add the
   separately specified parameter-gesture closure without releasing notes.
3. Wire each whole-control intent exactly once and every actual post result at
   ordinary dispatch, direct MIDI, recovery and disabled-audio branches. The
   returned named token must not be registered a second time. Deliver fresh
   observations and real lifecycle hooks in order, including failed reads.
4. Review startup/restart ordering explicitly: current `open_audio` queues its
   restore before `audio_.start`, whereas the frozen Start hook invalidates any
   unproved basis. A future adapter must establish a valid basis across that
   boundary and test it; pre-Start queue acceptance alone cannot authorize Save.
5. Bind synchronous storage to the exact emitted operation ID and immutable
   controls, obtain the final just-completed read inside the authorizer, and
   report the actual result once without event pumping after permission. Run a
   combined real-Session/create-only-storage journey at this adapter boundary.
6. Implement the separate browser/input contract. Existing `open_overlay` calls
   `lose_input(FocusLost)`, and UiModel handles Escape before its text gate. A
   library browser cannot inherit those paths unchanged: original key/pointer
   Ups, Space/MIDI owners and modal Down suppression need their own tests and
   actual native journeys, followed by source-bound captures.

No browser/main hook, native accessibility provider, callback deadline/retirement,
physical fidelity, release, publication or whole-interface 1:1 gate is closed by
this admission. The nominal dry Engine, 91 shared sources, 47 parameter identities,
state4/readers1–3, UUIDs and musical ownership are unchanged by this isolated
foundation. Changing any pinned source or its boundary semantics requires review
of the affected claim before reusing this verdict.
