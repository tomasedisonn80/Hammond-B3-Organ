# Combined native MIDI replay failure diagnosis

**The original combined run remains 239/241. The MIDI failure is an empty
acknowledged-observation window, although its native child completes and reaches
the expected final musical state.** A52, 17 November 2026 UTC. An unchanged
isolated comparison is pending execution by root; it cannot replace this result.

The [independent diagnosis receipt](../development/2026-11-16-heading-title-continuation/reports/a52-core-hosted/midi-original-failure-diagnosis.json)
binds the complete original failure block, copied diagnostic, literal input
scripts, source hashes, generated CTest properties, observation table and
independently evaluated predicates. The retained compressed block expands to
44,950 bytes with SHA-256
`599dcd0795390efd46ef206f186567bec7338f55e46e749cc53808316fc3f549`.
Its diagnostic JSON substring is 38,853 bytes with SHA-256
`025c9ee393f96a185670ea4ecb39e19795719a4bac5f0aee31fdc29677533724`.
These are bounded copies from the terminal combined log, whose entire hash is
also recorded. No successful rerun has been substituted for the failure.

## Original execution and exact predicate

Root ran all 241 discovered tests with CTest parallelism two. The terminal result
is 239 passed, two failed, exit code eight, 502.21 seconds CTest wall time
(502.324 seconds in the root wrapper). The 474 frozen code inputs did not change
during that run. The native MIDI gate took 44.47 seconds and ran 15 unittest
methods through 33 actual application subprocesses, including two expected
interrupted replays. Its one failing method is
`test_cc123_releases_only_its_external_division_and_preserves_ui`. The corresponding
CC120 method passed. The other full-suite failure, workspace replay, has a
separate diagnosis and is not reclassified by this review.

The failing 1,600 ms replay child used executable SHA-256
`2c64e585d8f1da521ff4c4dafe51613dd3aa0692461bfcb8d6450f9ca4971479`.
It returned zero in a reported 1.886 seconds; its subprocess guard is nine seconds
and its containing CTest guard is 90 seconds. Neither guard fired. The exception
is from `assert_window`, reached through `scoped_channel_release` in
[`test_standalone_midi_replay.py`](../../apps/standalone/native_tests/test_standalone_midi_replay.py):
`No acknowledged musical observation in [950, 1230) ms`.

That oracle requires an actual copied observation in the specified interval,
with applied sequence at least submitted sequence. It then compares the last
such observation's held notes to literal expectations. An earlier state carried
forward would not satisfy this rule. Its three checks give the following exact
results when evaluated against the retained JSON:

| Required interval, ms | Expected Upper / Lower / Pedals | Acknowledged observations | Result |
| --- | --- | --- | --- |
| [370, 630) | 60,64 / 62,65 / 5,6 | 474 ms | Pass |
| [650, 930) | 60 / 62,65 / 5,6 | 709 ms | Pass |
| [950, 1230) | 60 / 62 / 5,6 | None | Failure retained |

At 1,095 ms the copied state has submitted sequence 14 but applied sequence 13;
it still holds Lower 62 and 65. At 1,259 ms an observation has submitted and
applied sequence 14, with the expected Upper 60, Lower 62 and Pedals 5,6.
That correct acknowledged intermediate state is 29 ms beyond the required
exclusive endpoint. Another observation at 1,259 ms then records submitted
sequence 15 and applied sequence 14. At 1,381 ms sequence 15 is acknowledged
and the final pedal state is 5. The failure is therefore the absence of an
acknowledged observation inside the required quiet gap, not an incorrect final
held state.

## Completion evidence and its limits

The native diagnostic records all ten scheduled events delivered, nine packets
accepted, nine note-on commands, zero note-off commands, and no dropped or
rejected packets. The three CC123 records perform scoped releases; they are not
note-off commands. Completed, delivered, passed and final-acknowledged flags are
true. Before shutdown, submitted, resolved and applied sequence are 15, held
notes are Upper 60, Lower 62 and Pedal 5, and controls equal the fixture defaults.
The decoder reports nine actions and one epoch; retirement count is one.

The dummy audio path records 150 callbacks and 76,800 frames at 48 kHz, with
zero reported rendering, format, overrange or nonfinite failures. The software
renderer records 15 images at 1280×900. There are no application errors.
These are useful synthetic execution observations; they establish neither
physical device behavior nor callback deadlines.

All common assertions, process status, empty standard streams, literal input
file preservation, absence of unexpected output files, and the elapsed-duration
check occur before the context manager yields to the failed window assertion.
They executed and passed. The explicit final-state, command-count, control,
decoder-action and retirement assertions after the failed window did **not**
execute in that method. A52 independently evaluated those exact predicates
against the retained diagnostic and recorded that they are true; this is an
offline evidence check, not a completed unittest method.

## Source and scheduling interpretation

[`main.cpp`](../../apps/standalone/main.cpp) copies a Session snapshot in
`observe()` before delivering due MIDI events in the main-loop turn. MIDI
delivery and the turn's ending observation record the currently copied snapshot;
unchanged observations are deduplicated. Consequently, the retained timestamps
describe main-thread observations and delivery, not exact audio callback
application times. The [MIDI replay contract](../MIDI_REPLAY.md) explicitly
distinguishes scheduled due times from audio-frame or calibrated hardware clocks.

The literal UI workload ends at 370 ms. F2 and F3 select Lower and Pedals keyboard
targets, respectively; they do not select workspaces. No resize, overlay or
presentation transition appears in this scenario. The changed wide-title paint
path is inactive at 1280 px. Those facts narrow the affected behavior; they do
not prove that every source change is irrelevant.

The containing MIDI CTest overlaps scaled-view and workspace-replay CTests in
the combined log. Individual child intervals are not timestamped against those
other tests, and there is no CPU utilization trace. Concurrency is established;
CPU starvation as the cause is unproven. Generated CTest properties serialize
the previously admitted timing-sensitive application smoke, but do not serialize
this MIDI gate. The hosted standalone workflow already requests parallelism one.
The [smoke scheduling admission](NATIVE_SMOKE_SCHEDULING_ADMISSION.md) is relevant
precedent for controlled isolation, not proof of this failure's cause.

The earlier H1 full-suite log records this MIDI CTest passing in 41.50 seconds,
within a different 237/240 run and earlier application source. It contains no
successful per-method diagnostic history. The prior 23-method MIDI CLI suite is
a different gate. Neither observation qualifies this exact combined executable.

## Next step and acceptance boundary

Root owns one unchanged isolated observation of the failing method after the
complete combined run. Retain its command, executable and source identities,
literal scripts, diagnostic and original oracle result as a separate comparison.
A pass would support context sensitivity; it would not erase the original
failure or prove CPU causality. No source edits, timeout/window extensions,
weakened acknowledgment checks, stale-state substitutions or repeated attempts
until green are admitted here. Exact-source hosted qualification, physical
hardware and whole-interface visual equivalence remain separate open gates.
