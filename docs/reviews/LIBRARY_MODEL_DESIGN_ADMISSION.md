# LibraryModel design admission

**A10 independent review, 16 November 2026: ADMIT the exact API and design below
as implementation input for the copied-state/receipt foundation.** This is not
an implementation, build, test, native-browser or release acceptance. Root retains
integration and final admission.

## Reviewed source and scope

The source base is `9d60dbf462a90fe422fd4e69757fe202264acb7c`. I read the complete
standing agent instructions, M0–M9 plan and named-library contract, the complete
Session and UiModel public interfaces, relevant existing submission/observation
paths, storage scan/save behavior, and the complete new design/API. The current
[session](../development/2026-11-16-console-completion/README.md) assigns this
foundation separately from P1 material work and the other continuation's H1 work.

| Reviewed input | SHA-256 |
| --- | --- |
| [LibraryModel API](../../apps/standalone/LibraryModel.h) | `4ea94b611e4fdc27ea48c6bad47ddf9ed99761f2e12ae264b7482ac8d3b093e2` |
| [Concrete design](../LIBRARY_MODEL_DESIGN.md) | `b85e37d18725b8b357460a5a9caaa58f38cb0114573ae7c1c1266ce72b150852` |
| [Existing library contract](../REGISTRATION_LIBRARY_CONTRACT.md) | `4760d65b27aa154fd86ee09c2cda87bd30f532874cc1a35c62a5b359889703fa` |
| Existing RegistrationLibrary header | `6a3d75bd9fac8f70520c0847f8f98f4a33dd013a4d26fbaa3555e966880100eb` |
| Existing RegistrationLibrary implementation | `5a446bb7c3fde310fe4351ed891b3911197a4cd407ab548147f992e0b643fffc` |
| Existing Session header | `dc729465578ed02a8cb0640d07de679be33d731cdece947a09bce736bc84c929` |
| Existing UiModel header | `6d8c0b16ddb6f3059dc14aff41bfc615e37b43c53b2f6e88cc199255a6b674b1` |

The foundation has one main-thread owner for the copied catalog, draft,
selection, latest control-intent history, one named operation and the independent
current named reference. It executes no filesystem, SDL or Session operation.
Returned effects contain bounded owned values, and only the existing copied
ControlSnapshot belongs at the audio boundary. The PIMPL and copied view can
allocate on the main thread; neither is a callback object.

This leaves all 47 parameter identities, state4/readers1–3, 91 running sources,
UUIDs, musical transients and the nominal dry Engine unchanged. It also leaves
native browser rendering, main adapter wiring, held-input routing, real device
journeys and literal whole-interface equality as separate work.

## Why the acknowledgement boundary is adequate

An accepted Session post means queued, not applied. The design retains the
original pre-post publication, counters, desired revision and complete expected
controls with the accepted nonzero sequence. A later proof needs a newer coherent
publication, both resolved and last-applied sequence coverage, unchanged
recovery/rejection/discard/failure guards, the same latest desired revision and
exact expected controls. A later unrelated applied command cannot repair a
discarded control receipt by merely having a larger sequence.

Every complete control intention gets a new revision, including equal values.
Selection, draft, current reference and operation target are distinct. Thus an
equal-valued newer intent supersedes the earlier operation, while moving the
selected row cannot retarget it. Applied is established only by proof, and
Modified is calculated from actual acknowledged controls using the reference's
scope. Registration ignores expression only for that scoped comparison; the
complete recall candidate must still be acknowledged exactly.

Every actual post result, including direct MIDI, recovery and disabled-dispatch
results, has one reporting hook. Its failure revision closes the gap where a
synchronous rejection has no newer callback counter yet. Failed, old or
conflicting observations provide no proof. Saturated counters are not accepted
as evidence of unchanged history. Timeout is terminal Unconfirmed; late success
cannot revive it. Explicit lifecycle hooks cover stop/start cycles that occur
without an intermediate sampled stopped snapshot.

## Concrete review amendments incorporated

The author and reviewer resolved the following details before this admission:

1. **Observation and catalog admission are explicit.** The design validates
   snapshot control/revision/sequence/lifecycle relationships, monotonic relevant
   counters and complete equality for a repeated publication revision. Copied
   catalogs validate bounds, exact key/name/scope agreement, order, statuses and
   derived counts before replacing rows. Missing is inferred only from a complete
   admitted catalog; a failed scan cannot falsely make a current entry disappear.
2. **Committed disk truth survives faulty follow-up metadata.** A reported commit
   with inconsistent/missing committed-entry metadata is SavedWithWarning with a
   diagnostic and no false named-reference promotion. A failed postcommit refresh
   cannot become SaveFailed, trigger an automatic retry or undo the committed
   file. Duplicate or unknown operation results cannot overwrite another receipt.
3. **The real storage helper's generation-zero refresh is accommodated.** The
   existing helper calls `scan_registration_library(root)` after commit and
   returns its default generation zero. The model reserves its own post-save
   generation before issuing the effect and validates/remaps that compound result.
   It cannot replace a newer explicit refresh. If reservation is exhausted, the
   model emits no storage effect; a later real commit is never erased by an ID
   bookkeeping failure.
4. **Failed optimistic expression cannot leak into Registration recall.** Failed
   or recovered unproved intentions adopt actual controls into the tracked desired
   copy without inventing a revision or acknowledgement. Old completions cannot
   overwrite a newer valid pending intention. The final API additionally accepts
   explicit validated `latest_desired` from `UiModel::view().controls` at Recall,
   making that value the sole expression merge source. No cached/applied fallback
   is permitted, and invalid desired controls reject atomically.
5. **Single-file validation cannot clear directory ambiguity.** An Ambiguous row
   remains disabled until a complete admitted scan removes the case collision.
   Replacing a changed selected preview must retain consistent derived row counts.

These are reviewed specification decisions, not claims that an implementation
has passed them. The final API and design hashes above were independently read
back after the amendments.

## Save authority and irreversible outcomes

A Save cannot start from default/unproved controls, an invalidated intent or an
unsubmitted revision. It may wait for the original valid pending basis or use a
proved unchanged past copy, including a prepared stopped copy. It captures its
own target, desired revision, original basis and current failure guards.

ReadyToSave is not a disk write. Taking the effect requires another fresh guard
check and is consumable once. Immediately before atomic publication, the mandatory
storage authorizer must obtain a fresh Session read and prove the exact operation,
staged controls, sequence, counters, desired revision and deadline again. A failed
read cannot be replaced by the cached display. One true authorization is the
control-state linearization point; event pumping is forbidden before the
synchronous storage result.

Audio can publish after that point. The design therefore preserves an authorized
Saving receipt until its actual matching storage outcome arrives, even if later
controls, lifecycle or time change. This prevents a committed file being reported
as cancelled merely because audio advanced. A successful acknowledged save sets
origin AcknowledgedSave, does not post audio, and never calls `mark_saved` or
moves the legacy file baseline.

## Required implementation acceptance

The following are concrete future checks, not executed results of this review:

| Area | Required adversarial or behavioral check |
| --- | --- |
| Original proof | Begin with a prepared snapshot and sequence zero: Save must fail without proof. Queue an equal-value control and retain its pre-post revision: neither queue acceptance nor the same publication may prove it. Render through a real Session and require the new matching publication. |
| Sequence substitution | Discard/reject a control, then supply a larger unrelated applied sequence with matching controls. Guard changes must prevent Applied/Save proof. A failed direct-MIDI post without a control token must invalidate the active wait even before callback counters change. |
| Intent identity | Register a newer equal-value intent while Recall is pending; retain Superseded after the old acknowledgement. Selecting another row or editing the Save form must leave the original operation target unchanged. |
| Observation truth | Exercise failed reads, older revisions, conflicting copies at one revision, sequence contradictions, malformed controls, saturated counters and time regression. No invalid copy may replace actual display or certify a receipt. |
| Scope and rollback | Use different desired, applied and saved expression values. Registration takes the explicit latest desired expression; Performance restores saved expression. After rejection/recovery, an old optimistic expression must not be reused. Include all banks, pedal mixtures, cancelled fixed memory and percussion fields. |
| Catalog | Test generation zero, unsolicited/duplicate/out-of-order results, exact and over-limit counts, forged count arithmetic, sorting/key/scope mismatches, disabled rows, case collisions and full-range relative movement. A failed scan preserves rows and Missing; a removed selected key is not silently replaced. |
| Lifecycle and clocks | Exercise Stop/Start hooks without a sampled stopped state, Prepare, stopped proved Save, pending stopped Recall, 1999/2000 ms timeout boundaries, deadline overflow and late acknowledgement. All four ID limits need zero/last-issued/exhausted cases without wrap. |
| Save stages | Require one effect and one authorization. Change desired intent, failure revision or fresh-read availability during staging and refuse commit. After true authorization, change actual controls and retain the real committed outcome and correct Modified/Pending distinction. |
| Storage results | Return SavedWithWarning, absent/malformed committed metadata, failed refresh, generation-zero post-save scan, a newer explicit scan and duplicate/foreign completion IDs. Never promote a false reference, erase a committed result or automatically retry. |
| Existing behavior | Test the future named-recall UI helper separately from `load_controls`: it must emit one snapshot even for equal controls while retaining the legacy clean reference, note ownership, edited bank, focus and histories. Model tests alone do not establish native input behavior. |

Counter and count validation must perform bounds checks before arithmetic that
could overflow; a fabricated maximum-size count is not a complete catalog. Source
review should verify that no filesystem or live Session access was introduced
inside the model, and a real Session harness should cover held-note/clock
continuity for its returned control effect.

## Adapter obligations and next action

Current main has ordinary dispatch, direct MIDI posting and a recovery-submission
loop. All three require the future reporting hook, including their disabled-audio
branches. Current `UiModel::load_controls` moves `saved_controls_`; it is not the
named-recall helper. Future integration must deliver coherent observations to both
UI and library models in order, preserve original note releases through modal
entry/exit, and keep browser selection/current/operation labels distinct.

Root may now assign implementation against these exact inputs. Subsequent API or
semantic changes need review of the affected boundary. Source review, coherent
build/tests and exact-source publication remain necessary. I ran no build, native
test, filesystem mutation experiment, measurement or publication, and changed only
this admission and the assigned [A10 note](../development/2026-11-16-console-completion/notes/A10.md).
