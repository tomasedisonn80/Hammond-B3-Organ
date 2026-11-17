# Starter Load: copied-state observation diagnosis

17 November 2026; A47, `/root/w08_a47`, wave 8. **Independent diagnosis:
the two retained failures expose a test-protocol assumption, not an observed
failure to apply or restore the complete controls.** A narrowly changed
observation oracle is admitted for implementation and root qualification below.
No runtime change, completed native rerun or retrospective pass is admitted.

The [bounded evidence receipt](../development/2026-11-16-heading-title-continuation/reports/a47-starter-load-diagnosis.json)
binds this decision to the original test, application, source and both raw logs.
The [original admission](STARTER_NATIVE_LOAD_ADMISSION.md) stays unchanged. Its
historical result remains valid for its named inputs; its statement that the
edited snapshot must be acknowledged **before Ctrl+O** is explicitly superseded
for this test by **a complete copied, applied edited state before the complete
copied, applied restoration, in actual observation and Session sequence order**.
This clarification does not establish when the callback applied the edits
relative to the main thread's Ctrl+O submission.

## Observed failure and unchanged workload

The original full run reports 237/240 passing CTests in 561.57 seconds. The
separate unchanged-source isolated Load run also fails. Both fail only the
`performance` subcase of
`test_materialized_scopes_keep_their_expression_when_generically_loaded`, at
the empty `acknowledged_edits` assertion. This is not evidence that removing
CTest concurrency repairs the issue.

Both used application `bfe8e36d16f4c5fd15009f2fc4707c06c93388f40870dc9f84696d3367447e7b`,
original main source `89b24fdeae438b77309904d12c32e3e2ae5e964e99968a8656c5b0a710e237c4`
and original test `22285ddcaec03adf61f97b1d65c7e70de4ee6c6437480267b4784ab8d360f5c7`.
The script is exactly 3,479 bytes / 152 actions, SHA-256
`489218ab81d669aa6899223bf0ed03b248c101e354083db841a566df54e66821`:
duration 2,700 ms, Ctrl+O at 2,200 ms, process bound nine seconds, unchanged
keyboard navigation and edits. There is no resize. H1's wide header treatment
is inactive at this 1280×900 layout. The separate resize/paint correction is
neither the cause nor a remedy credited by this review.

Here L is the entire independently specified loaded control snapshot, and E is
the entire independently specified edited snapshot, including the hidden bank,
both selectors/routes/fixed modes/presets, expression, pedals and percussion.

| Original observation | Full-run index / ms / applied | Isolated index / ms / applied |
| --- | --- | --- |
| Complete startup L | 0 / 72 / 1 | 0 / 58 / 1 |
| Complete edited E | 10 / 2,255 / 6 | 11 / 2,201 / 6 |
| Complete restored L | 11 / 2,383 / 7 | 12 / 2,323 / 7 |

Every listed applied sequence equals its resolved sequence. At E, submitted
sequence is already 7 in both runs; at restored L it is also 7. Complete final
controls, desired controls and the running endpoint equal L; final replay is
acknowledged, all 152 actions were pushed/delivered, and application/audio/session
fault checks preceding the failed oracle passed. The final resolved/applied
endpoint is 7. These are actual diagnostics, not inferred intermediate states.

The failing subcase does **not** establish successful execution of its later
file/script/directory assertions: `run_load` calls those only after
`assert_load_diagnostics`, which raised. Their assertions must remain and must
execute in qualification of the corrected test. Other passing subcases cannot
stand in for this one.

## Source argument

The [Session contract](../STANDALONE_SESSION.md) distinguishes accepted commands,
resolved outcomes and commands actually applied. `Session::post` copies each
accepted command and assigns an increasing nonzero sequence. `render` captures
a bounded queue prefix and applies it FIFO; it advances `last_applied_sequence`
only after a successful command. `publish` takes controls directly from
`engine_.controls_snapshot()` and publishes them with resolved/applied sequences
through atomic cells and a coherent revision. `read_snapshot` returns a coherent
copy or preserves its destination on failure. Consequently, resolved-only or
producer-desired evidence is insufficient, while copied E at applied 6 is
evidence that E really reached Engine.

In the retained `main.cpp`, `observe` copies a successful Session observation
into `snapshot_`. `record_replay_observation` stores that snapshot, not
`ui_.view().controls` or desired controls, alongside the main thread's current
submitted sequence and observation time. Its running/startup-restore guard
remains unchanged. A record can therefore combine the genuine previously
published applied state with a newer accepted command still pending.

`handle_key` dispatches Ctrl+O through `load_state`, then records a replay
observation. The next normal `observe` happens after the bounded SDL event
drain. `load_state` queues the complete parsed controls through the existing
Session path; it does not require an empty queue. This is consistent with the
[generic expression policy](../REGISTRATION_GUIDE.md#3-choose-expression-behavior-explicitly):
generic Load restores the full payload regardless of suffix. Materialization's
Registration/current-expression policy remains separate.

The [replay contract](../STANDALONE_INPUT_REPLAY.md) posts each due prefix in
order. `ScriptedInput::pump` uses `at_ms <= elapsed_ms`; this is an eligibility
time, not a promised callback or observation deadline. The event loop may
consume several due events before its next Session copy. A record observed
after 2,200 ms consequently does not imply that its applied edit occurred
after the Load application. Conversely, nothing here proves an earlier
callback timestamp or the stronger historical pre-submission assertion.

## Exactly what may change

Retire only these assumptions in the edited-state selection:

1. E must have `elapsed_ms < LOAD_MS`.
2. E must have `last_submitted_sequence == last_applied_sequence`; a queued
   later Load does not invalidate the already applied E.

Do **not** remove equality between E's resolved and applied sequences. Do not
substitute desired controls, a final-only comparison or sorted observations.
Keep the startup L observation below 750 ms and the restored L observation at
or after `LOAD_MS`, as neither existing check is implicated by this failure.
No timestamp, duration, timeout, navigation count, expected control value,
native process count, CLI operation, data byte or runtime recording guard changes.

The replacement must enforce all these conditions:

- Inspect the recorded history in its existing array order. Elapsed time,
  submitted, resolved and applied sequences are nonnegative and nondecreasing;
  resolved/applied values cannot exceed their associated submitted value or the
  final submitted sequence. A change of controls at an unchanged applied
  sequence is invalid for this fixed workload. Equal observation times are
  allowed; tied records occur in the retained evidence.
- Select startup L, then complete E, then restored L at strictly increasing
  indices and strictly increasing **applied** sequences. Each selected sequence
  is positive, resolved equals applied, and applied does not exceed submitted.
  Startup still precedes 750 ms. Restored L still occurs at or after 2,200 ms,
  with applied/resolved/submitted equal to the final submitted sequence.
- Do not accept E after an already observed restoration at the final sequence.
  Any later control change at that sequence or any sequence regression rejects.
  A cached valid applied E before restoration is useful past-state evidence;
  a stale or reordered E after restoration is not.
- Retain full-snapshot equality, final endpoint and desired-state comparisons,
  pending-save/control, final acknowledgment, delivery, no-MIDI/no-note,
  callback/paint progress, zero-error/fault, stopped/unheld shutdown, unchanged
  file/script bytes and directory inventory assertions. Resolved-but-not-applied
  commands, missing E, or desired E without copied E must fail.

An exact literal command count or `E.sequence == final_sequence - 1` is not
needed: full copied states, FIFO source semantics and strictly increasing
applied sequences provide the relevant proof. Adding such a count contract is
outside this minimal correction.

## Required qualification and remaining limits

Before native execution, retain the original test bytes from the current HEAD
and the immutable original admission/log identities. Implement the helper and
pure fixtures in the assigned test only. Pure fixtures must accept a normal
chronology and the genuine delayed E / pending Load pattern, including tied
elapsed times. They must reject missing or incomplete E, startup-only/final-only
history, reversed array order, elapsed or sequence regression, equal transition
sequences, resolved-only acknowledgment, impossible applied/submitted ordering,
wrong expression/hidden-bank/percussion values, restored L at the wrong final
sequence, E appearing after restoration, and changed controls at one applied
sequence. Desired controls alone must never manufacture a qualifying E.

Root must replay both retained diagnostic objects through the actual original
checker and changed checker: original must reproduce its assertion, changed
must pass every retained diagnostic assertion. This offline check cannot
execute the temporary-file assertions or qualify a new native process. Root
then runs the unchanged 2,700 ms workflow with all four standalone and two CLI
processes against a coherent named application, retaining each result. A direct
changed-test run against the preserved original application isolates this
correction from A46's unrelated runtime edit. The integrated affected/full
gates and exact-source hosted qualification remain root-owned.

If a later run never publishes/copies a full E before restoring L, this oracle
must still fail. Neither FIFO reasoning alone nor a later final-state match
may fill that observation gap. This review supplies no general callback
deadline, native-device result, new Load behavior or closure of M9, literal
whole-interface 1:1, physical calibration or release requirements.
