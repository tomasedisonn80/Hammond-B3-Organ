# Independent preset Session publication acceptance

A27, `/root/w05_a27_session_concurrency`, 2026-11-14. The new
[`test_standalone_preset_concurrency.cpp`](../../apps/standalone/tests/test_standalone_preset_concurrency.cpp)
passes its focused Linux Release CTest. **No production defect was found.**
This accepts the tested raw-control publication and recovery behavior; it is
not a complete concurrent-memory proof, sanitizer result or device timing gate.

## Risk and independent oracle

The [preset contract](../PRESET_SELECTION_CONTRACT.md) retains two raw fixed
modes independently of the effective selector, route bits and remembered A/B
banks. Session adds these bytes beside the last four lower-bank drawbar bytes
inside its existing atomic publication. A cancelled fixed choice must survive
both ordinary observation and a later copied Save. A correct effective Cancel
value alone cannot prove that memory survived.

The test creates immutable, uniquely stamped whole-control snapshots before
starting workers. Every bank, both raw modes, remembered banks, route bits,
percussion fields and pedal positions vary; an exactly representable expression
stamp distinguishes each sequence. Expected values use no production packer,
unpacker or fixed-row lookup. This deliberately tests publication coherence
rather than repeating A18's exhaustive 1,600-state single-thread matrix.

One main producer, one serialized audio thread and one copied-snapshot reader
run at each of 44.1, 48 and 96 kHz. The reader checks all retained controls against
the immutable oracle indexed by the published applied sequence. It also checks
both manuals' held keys, the independent pedal owner, counters, sample rate,
lifecycle and the exact clock/revision relationship for alternating positive
and zero-frame callbacks. Accepted sequences and revisions must not regress.
A bounded failed read must preserve every destination field, including floating
point bits. Failed worker assertions stop and join both threads before reporting.

Each rate has 64 controlled rounds: the producer posts a complete restore while
the audio thread is parked, verifies that the published state is unchanged,
then permits the callback and waits for the independent reader's acknowledgment.
The following 1,024 restores use a conservative 192-command credit bound and
exercise repeated ring reuse with scheduler-dependent frozen callback prefixes.
No post or render call waits inside production code.

The reader also saves selected safely copied observations as state4 while audio
continues. Literal catalog and manual-line checks distinguish hidden fixed
memory, bank and route; reloading must preserve every control and expression
bit. These allocating serialization calls run only on the reader, never in the
callback. Final stopped observations retain all controls and release owners.

## Queue and rejection boundary

Six separate cases use the three rates and either cancelled nonzero fixed
memory or cancelled `None`. An invalid hidden fixed mode rejects immediately;
subsequent audio and held-owner observations agree with a twin Session.
The exact 256-slot ring then fills with replacement snapshots. The next selector
returns `QueueFull`, a further restore returns `RecoveryPending`, and an invalid
buffer leaves output, pending commands and the published snapshot intact.

The next valid zero-frame callback discards all 256 queued replacements,
preserves the original raw controls and frame clock, and publishes the exact
recovery acknowledgment. **Queue overflow deliberately performs global owner
recovery** under the existing Session contract; it does not preserve held notes.
An independently requested Panic supplies the twin's corresponding owner
release. New bank/fixed selections and notes then produce bit-identical, audible
future output across several block sizes. The test does not mistake discarded
restores for applied commands.

## Actual execution

The fresh coherent source/build and exact commands are in
[A27's execution record](../development/2026-11-14-preset-continuation/27-session-concurrency.md).
GNU C++14.2.0, CMake/CTest4.4.4 and Python3.12.14 built the SDK-free Release target
with all repository strict warnings, including `-Werror`.
The final selected CTest passed **1/1 in 0.03 seconds total wall time**, without
skips. Time is an observation, not an acceptance threshold for audio hardware.

| Stable scenario count | Result |
| --- | ---: |
| Rates / controlled pending checks | 3 / 192 |
| Complete restores in concurrent runs | 3,264 |
| Explicit queue recovery cases | 6 |
| Discarded pending restores | 1,536 |
| Rejected calls | 24 |
| Exact future stereo-sample comparisons | 1,524 |
| Separate exact priming stereo samples | 768 |

Scheduling-dependent final observations were 297 callbacks, 14,568 successful
reader copies, 252 bounded busy reads, 17 copied state4 saves, 194 changed
cancelled-fixed observations and 19 changed cancelled-None observations.
All 2,292 compared stereo samples in the deterministic continuation cases were
nonzero. The test does not assert those scheduling-dependent counts.

An initial successful run preceded a test-only refinement: its single output
counter included 768 priming samples under a future-sample label. The final test
separates those counters and adds an immediate-invalid-restore continuation and
owner check before queue saturation. The changed test alone was rebuilt and
rerun; both original and final logs remain identified. No production repair or
unchanged failure retry occurred.

## Limits and next step

This run uses the SDK-free Session with nominal ideal contacts; it does not test
SDL, native MIDI, a DAW, callback allocation, physical timing, Windows/macOS,
TSan, ASan or UBSan. The 20-second internal process guard prevents indefinite
test waits; it is not a performance requirement. Source and test inputs remain
coherent, but a stress test cannot prove every legal interleaving.

The automatic test glob registers the `test_standalone_` name for both ordinary
core CI and the hosted standalone selection. The integrator must include it in
the final coherent source and the affected platform/sanitizer gates, retaining
their distinct executed evidence. No source catalog, physical fidelity, UI
pixel-equality or complete project claim follows from this test.
