# Qualified-final MIDI failures and two isolated diagnostics

**The full run remains 240/242, with the original preset-raster timeout and
native MIDI replay failure retained. Both exact unchanged isolated MIDI methods
pass, one invocation each.** A52, same wave-nine worker, 17 November 2026 UTC.
This is a completed diagnostic comparison, not a complete local-suite pass or an
admission to change timing windows, source, properties or assertions.

The [independent evidence receipt](qualified-midi-failure-review.json) binds the
[terminal full-run result](../qualified-final-coherent-results.json), all
[475 frozen code inputs](../qualified-final-coherent-inputs.json), both original
failure diagnostics and scripts, and the
[root's two isolated observations](../qualified-midi-one-isolated-diagnostics.json).
A52 independently rehashed every frozen code and build input: none changed.
The original combined-run review and A52's original note remain untouched.

## Source and execution identity

| Input | SHA-256 |
| --- | --- |
| Current application | `1fa2a247e6e90379540ad431776241a885b93223430ac3b0798480d58e96a28a` |
| Current main | `0c02c619bd04e69ed70aa7c50cbb8345cbc41a188619e94ca6b8a56a24547537` |
| Unchanged MIDI fixture | `fa2e957bc49fc104aaba2b9a16cc671549018a133157841ad3f58d7362602fcf` |
| Current standalone CMake | `642655110b803592e0943d6bb1aa367cd74c81d72b6ebef0b3f1058916157a96` |
| Unchanged H1 painter | `0bf731a692b7cb7c88c200afea86f4ca14239f20a7000f06be484f2a11ebc20d` |

The full 242-test invocation returned eight after 740.263708 seconds in root's
wrapper. Native MIDI replay took 44.70 seconds, executing 15 methods through
33 application children, with two expected interrupted replays. CC120 and the
real-overflow method failed; CC123 passed in this run. The MIDI CTest was
`RUN_SERIAL TRUE`. Root's complete scheduling receipt confirms nonoverlap, and
A52 independently found no other CTest active during the MIDI interval.
Serialization therefore did not guarantee these observation windows.

Local recovery commit `045c95d…` has main `361ae03a…`; historical published
`9d60dbf…` and `6047723…` have main `89b24fde…`. The MIDI fixture and Core CI
workflow bytes are identical across those local immutable Git objects and the
current candidate. The current main differs. These comparisons are local object
inspection, not a fresh remote-head claim. Earlier hosted passes cannot qualify
this current candidate; its exact published-source observation remains pending.

## What failed and what the data establishes

Both exceptions are empty fully acknowledged candidate sets in `assert_window`.
Neither failure reaches the subsequent held-state equality comparison. The
oracle requires a copied observation inside its interval with applied sequence
at least submitted sequence; final completion cannot substitute for it.

| Method | Required first interval | Original decisive observations | One isolated observation |
| --- | --- | --- | --- |
| CC120 scoped release | [370,630) ms | At 594 ms: submitted 12, applied 11. Correct full-owner state acknowledged at 719 ms, 89 ms past the endpoint. | Correct state acknowledged at 466 ms; later required gaps pass at 758 and 1060 ms. |
| Real overflow and reconnect | [150,480) ms | At 203 ms: submitted 7, applied 3. Correct initial owners acknowledged at 519 ms, 39 ms past the endpoint. | Correct initial state acknowledged at 256 ms; required post-overflow gap passes at 639 ms. |

The original CC120 child returns zero in 1.939 seconds, delivers ten events,
accepts nine packets and finishes at sequence 15 with Upper 60, Lower 62 and
Pedal 5. No packets are dropped or rejected. The original overflow child returns
zero in 1.752 seconds, delivers all 607 events and finishes at sequence 11 with
Upper 60, Lower 69 and no pedals. It records the intended real overflow:
260 accepted packets, one rejected packet, 256 discarded queued packets,
344 packets ignored while closed, two epochs and an explicit reconnect. The
512-event budget is actually reached. No stale Upper 64 or unrequested Lower 70
appears in its observations.

Both native diagnostics mark delivery, completion and final acknowledgment true.
Both preserve default controls, report zero application errors and zero reported
audio processing failures. Common process, schema, shutdown and literal-file
assertions execute before yield and passed. After the first failed window, later
window, final-state, count and lifecycle assertions are **unreached in the
original methods**. A52 independently evaluated every such predicate against
the retained JSON; all are true. This does not turn either failed method into a
pass. Neither the nine-second child deadline nor the 90-second MIDI CTest guard
was reached.

The complete original MIDI failure block is retained as
`qualified-midi-original-failure.log.gz`: 93,915 uncompressed bytes, SHA-256
`197c2be046e7dc864a6890f40436eca2f359f4063d9b9ed0a1e669d85a628416`.
Both original JSON substrings and literal scripts have separate bounded files
and exact offsets/hashes in the receipt.

## Complete isolated observations

Root ran exactly one original method at a time after the complete suite and the
separate preset diagnostic. Each method invokes one application child and keeps
the fixture's original nine-second limit. No source, schedule, assertion,
property, duration or timeout was changed. The evidence environment only retains
the fixture's existing diagnostic copies. A52 did not execute an application.

| Method | Child wall time | Unittest wall time | Root wrapper wall time | Result |
| --- | ---: | ---: | ---: | --- |
| CC120 | 1.775548 s | 1.813 s | 2.031860 s | One method and one child passed |
| Overflow | 1.708183 s | 1.737 s | 2.037486 s | One method and one child passed |

A52 verified every member of both deterministic lossless archives against the
root receipt and retained files. MIDI and UI scripts are byte-identical to the
original failed scripts. Both logs report one executed method, one child, zero
expected interruptions and `OK`; process records show zero exit and empty
standard streams. All method assertions, including the previously unreached
tail, now execute. Independent predicate evaluation confirms every required
window, final owner/control/count assertion, overflow retirement/reconnect count
and stale-note exclusion. These are complete one-shot method observations;
they are not a second full suite or repeated attempts until green.

## Interpretation and handoff

The main loop copies Session state before due MIDI delivery, and identical
musical observations are deduplicated. Retained timestamps identify main-thread
delivery and copied observations, not exact callback application times. The
literal scripts have no workspace, presentation or overlay transition; F2/F3
select musical targets. The new semantic-transition drain branch is not selected
by those actions. Neither CPU utilization nor a callback application clock is
recorded. Do not assign a precise CPU or scheduling cause.

The isolated observations demonstrate successful complete methods at unchanged
inputs while preserving the full-run timing failures. No further diagnostic
invocation or correction is proposed. Root can report the exact **240/242 plus
two separate isolated passes**, decide publication admission and obtain hosted
qualification at the verified published SHA/tree. A52 retains the six Core CI
families for that follow-up; no new worker credit is created. Physical devices,
callback deadlines and whole-interface 1:1 remain separate open gates.
