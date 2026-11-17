# Combined workspace replay observation diagnosis

## Finding and status

**The combined suite fails a different assertion from the original missing
painted-view failure.** Its first restored musical observation is recorded at
292 ms; the unchanged `assert_commands` helper requires a value below 180 ms.
The retained diagnostics contain all nine exact expected painted visits,
including Play/Flat at 1280×900 before the resize. This review neither changes
the assertion nor converts the failed suite into a pass.

The completed combined run passed 239 of 241 tests in 502.324 seconds, with all
474 frozen code inputs unchanged. Its two failures are
`test_standalone_native_midi_replay` and `test_standalone_workspace_replay`.
This review owns only the latter diagnosis. Root owns native diagnostics,
scheduling decisions, any source changes, qualification and publication.

## Evidence identity

The [A53 receipt](../development/2026-11-16-heading-title-continuation/reports/a53-standalone-hosted.json)
records exact source, original and current diagnostic identities, counters,
visit sequences, and the completed full-suite identities. A bounded
[complete workspace failure block](../development/2026-11-16-heading-title-continuation/reports/a53-standalone-hosted/combined-workspace-failure.log)
retains the original traceback, command, 87-action script, copied diagnostics
and six-method result without altering the original
[full log](../development/2026-11-16-heading-title-continuation/reports/combined-final-ctest.log).

| Evidence | SHA-256 |
| --- | --- |
| Repaired application | `2c64e585d8f1da521ff4c4dafe51613dd3aa0692461bfcb8d6450f9ca4971479` |
| Current `main.cpp` | `361ae03aa9e1a369a8fd8d125c21b10e40841d08d768a4c5637b2a3ecf0232f3` |
| Unchanged workspace fixture | `9a226a6b17b1d7eb84a079a113f5ef97a6f37935ba16d1d3f55876bed907d6f3` |
| Complete 44,316-byte failure block | `b8f2b2a62696a9682886f665ad405acf9defe902abb2eacd50fbceb10874d98f` |
| Exact copied diagnostics in that block | `ceedc537c82eb782aeae54f97093a5f2985f209f529dcbdb242bb739cd5005df` |
| Completed combined-result receipt | `428196052978826fec9d55c275dfe10852196f71c29f5b923e703b800abfc7ed` |

The workspace executable ran 30 actual subprocesses across six methods.
Five methods passed. The focus-memory method's child completed in 3.867
seconds; its enclosing CTest finished failed after 50.58 seconds. The failure
occurs at the helper's first elapsed-time assertion, called after the full
control-path and empty-held-path checks.

## What the failing sample establishes

The first musical observation has elapsed time 292 ms and identical
submitted, applied and resolved sequence values of 3. It has the complete
fixed loaded controls, empty manual/pedal holds and zero errors. The full
control-path check has already verified all seven expected control states,
with the first Upper-B drawbar following `8 → 0 → 1 → 2 → 3 → 4 → 3` and every
other control unchanged.

This particular journey begins with 25 Tab presses and releases, scheduled
between 20 and 510 ms. Its first control edit is Home at 550 ms. The first
recorded submitted edit is sequence 4 at 617 ms, with sequence 3 still applied;
sequence 4 first appears applied at 741 ms. Consequently the retained 292 ms
sample supplies an acknowledged, unedited loaded-control observation. It
nevertheless violates the fixture's existing explicit 180 ms requirement.
Those are distinct findings, and both remain recorded.

The final submitted sequence is 9. The retained initial sequence 3 plus six
control commands accounts for that result, and the before-shutdown applied
and resolved sequences both equal 9. Accepted note-on/off counts are zero.
All 87 scheduled UI actions were pushed, replay delivery/completion/final
acknowledgment are true, controls and Save are no longer pending, and the
histories are not truncated. Application errors and audio format, render,
nonfinite and overrange failures are zero. These read-only checks do not
erase the failed elapsed-time assertion.

## Actual painted visits

Every row below is an actual retained presentation observation. Elapsed values
are the application's recorded observation values, not a new per-event or
callback timestamp trace. All overlays are `none`.

| Visit | Workspace | Presentation | Size | Image | Elapsed ms |
| --- | --- | --- | --- | ---: | ---: |
| 1 | Play | Dimensional | 1280×900 | 1 | 0 |
| 2 | Rotary | Dimensional | 1280×900 | 7 | 845 |
| 3 | Service | Dimensional | 1280×900 | 11 | 1120 |
| 4 | Play | Dimensional | 1280×900 | 16 | 1508 |
| 5 | Play | Flat | 1280×900 | 21 | 1866 |
| 6 | Play | Flat | 960×700 | 32 | 2173 |
| 7 | Rotary | Flat | 960×700 | 51 | 2581 |
| 8 | Play | Flat | 960×700 | 68 | 2922 |
| 9 | Service | Flat | 960×700 | 81 | 3298 |

Independent parsing of the retained diagnostics reproduces the exact nine
visits, nondecreasing inspection frame clocks with overall progress, a
current snapshot somewhere in the history, and a current-or-retained final
snapshot. Thus the data support all predicates in this method's subsequent
`assert_views` call. The native unittest did not reach that call: these are
post-failure read-only observations, not a rerun or a passed native assertion.

The final exact saved-state byte assertion was also not reached. Its expected
bank-B replacement is still present unchanged in the fixture. Copied
diagnostics do not contain the saved file's bytes. Successful Save completion,
final controls and the earlier isolated pass cannot certify those bytes for
this failed invocation. That tail remains unqualified by this review.

## Relationship to A44, A45 and A46

The [original diagnosis](WORKSPACE_PAINT_REPLAY_DIAGNOSIS.md) concerns an eager
resize-prefix delivery path that could replace a changed semantic view before
ordinary painting. Its original failing payload omitted Play/Flat at 1280×900
entirely: image 13 was Play/Dimensional at 1740 ms and image 14 was already
Play/Flat at 960×700 at 2209 ms. Its first musical observation was 119 ms,
which satisfied the separate 180 ms requirement.

A46's admitted selective gate compares the actual last-painted workspace,
presentation and overlay before eager continuation. Its guarantee gives a
changed final semantic view an ordinary paint opportunity at the current size
before the next resize-separated prefix. It does not promise a first restored
musical observation before a particular clock boundary. Dimensions and
musical snapshot timing are deliberately outside that comparison.

A45's retained [genuine before](../development/2026-11-16-heading-title-continuation/reports/a45-before.json)
and [after](../development/2026-11-16-heading-title-continuation/reports/a45-after.json)
receipts independently establish the targeted paint-boundary behavior for two
timestamp-zero variants. Both genuine-old-app cases fail the three-visit
requirement; both repaired-app cases pass with unchanged inputs. The previous
[three-gate serial result](../development/2026-11-16-heading-title-continuation/reports/replay-repair-affected.json)
also records an unchanged workspace pass. Neither result replaces this
combined failure or proves a scheduling cause.

## Source distinction and next action

`record_replay_observation` records musical history only when a running
snapshot is available and its resolved sequence covers the intended restore.
The main loop and relevant input handlers sample that retained state. There
is no 180 ms guarantee in the A44 semantic-paint change. The evidence does not
identify the callback's exact restore time, exact marker or handler timing,
OS scheduling behavior, or CPU contention. Serial-versus-parallel outcomes
alone cannot establish one of those causes.

Root explicitly chose to preserve every fixture byte and the 180 ms
assertion. No clock relaxation, oracle replacement, expanded drain, longer
timeout, fabricated observation or retry was authorized for A53. Root's
admitted next investigation is one unchanged isolated diagnostic of each
failing method. Conditional on those results, root may consider only CTest
`RUN_SERIAL` scheduling for the two observed failing CTests, then require the
full `--parallel 2` suite to demonstrate nonoverlap and pass. That future
execution must be recorded separately and must retain this 239/241 result.

This diagnosis closes neither physical MIDI/device acceptance nor real
display, native accessibility, literal whole-interface 1:1, or release gates.
