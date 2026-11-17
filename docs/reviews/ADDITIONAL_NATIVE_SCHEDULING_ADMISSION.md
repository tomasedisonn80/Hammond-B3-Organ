# Additional native scheduling admission — A54, wave 9 follow-up

## Decision

**Admit `RUN_SERIAL TRUE` for exactly `test_standalone_native_calibration`
and `test_standalone_midi_cli`.** Root has completed one unchanged isolated
invocation of each of the three newly failing methods. All three passed;
A54 verified their retained log hashes, successful one-method outputs, and
unchanged-input receipt. This admits a narrow scheduling correction, while
qualification of the next complete coherent suite remains open.

This is a separate review of newly observed failures. The earlier
[two-test admission](REPLAY_TEST_SCHEDULING_ADMISSION.md) and its receipt are
unchanged. The candidate subsequently completed **238/241**, exit 8, with
686.446 seconds at the root wrapper and 686.18 seconds reported by CTest.
All 474 frozen code inputs were unchanged. The two previously serialized
tests had the required generated metadata and actual nonoverlap; MIDI
replay passed. Workspace replay failed on a different missing semantic-view
transition. That separate runtime issue is not admitted as a scheduling
failure here and is not the earlier `<180 ms` failure.

The candidate's [original result](../development/2026-11-16-heading-title-continuation/reports/serialized-final-coherent-results.json)
and [log](../development/2026-11-16-heading-title-continuation/reports/serialized-final-ctest.log)
remain immutable. The log is 77,140 bytes, SHA-256
`ba6261b1c014a7fb28d01680f74a9de0c6c07e3cab8695931bcb28b3306751b1`.
The [additional admission receipt](../development/2026-11-16-heading-title-continuation/reports/a54-additional-native-scheduling.json)
preserves both complete relevant CTest failure blocks losslessly with their
hashes, source identities, generated properties, and exact commands.

## Decisive failures and successful isolated diagnostics

| Original method | Decisive failed assertion | Single isolated result |
| --- | --- | --- |
| `NativeCalibrationLifecycle.test_changed_route_retires_old_owners_and_rejects_old_wire_channel` | `decoder.unmapped_channels` was 0; required 2 | Passed; 2.618 seconds reported by unittest, 3.033 seconds at wrapper |
| `NativeCalibrationLifecycle.test_native_fault_retires_midi_owners_while_original_ui_owner_survives` | No copied observation simultaneously had overlay `none`, error count 1, and empty held owners after the original keyboard release | Passed; 3.384 seconds reported by unittest, 3.548 seconds at wrapper |
| `NativeMidiAcceptance.test_cli_expression_configuration_does_not_write_musical_expression` | The `inverted=True` 600 ms smoke returned 1 with `Native smoke failed`; required exit 0 | Passed with both original inversion subcases; 1.683 seconds reported by unittest, 1.846 seconds at wrapper |

The original calibration suite ran nine methods and ten native fixture
children, with two method failures. The original MIDI CLI/modal suite ran
23 methods and 159 application children, with one failed subcase. Neither
suite timed out: CTest reported 23.03 and 28.83 seconds respectively. The
three isolated methods were separate later diagnostics, not replacements
for either original failed CTest.

In the route method, common runtime and trace checks, reconnect transition,
two opens, new channels, and two decoder epochs returned before the failed
unmapped-channel assertion. Subsequent parameter-message, expression,
held-state, and forbidden-old-note assertions were not reached in the
original failed execution. In the fault method, the first witness preserving
the unrelated keyboard owner was present; the following empty-owner witness
failed. Later reopen, discard-count, packet, expression, and final-owner
assertions were not reached. The CLI runtime helper returned after its
common lifecycle checks, but the failed exit-code assertion preceded the
method's selected/configured calibration, expression, parameter-message, and
smoke assertions. Those previously unreached checks executed in the separate
successful isolated method invocations.

## Why this supports only a narrow scheduling adjustment

The log directly establishes overlap: MIDI CLI starts while the pedal-trace
Python test remains active; calibration starts before MIDI CLI completes;
percussion raster starts after calibration fails while MIDI CLI remains
active. This establishes concurrent CTest jobs. It does not establish an
exact CPU scheduling cause, process starvation, or the responsible thread.

The [calibration driver](../../apps/standalone/native_tests/calibration_lifecycle_driver.cpp)
compiles the real application entry and native lifecycle with a test-only
RtMidi dependency. Its
[dependency fixture](../../apps/standalone/native_tests/fake_calibration/RtMidi.h)
offers callbacks synchronously at native API boundaries. In the route
scenario, the two old-route packets and new-route packets are offered only
on the third `isPortOpen()` query after reopening; the first two queries
belong to activation. Production connection polling has a nominal 250 ms
interval. A fixed-duration run therefore depends on application progress
through polling and decoding. However, a final counter mismatch is not
merely a timestamp predicate. The original CTest failure block did not
retain the temporary per-case dependency trace or diagnostic object, so it
does not establish whether the third query, offers, or drain occurred.
That evidence gap must remain explicit.

The fault method requires intermediate ownership observations inside a
fixed 3,200 ms replay, with original key-down at 80 ms, key-up at 1,100 ms,
MIDI opening at 1,300 ms, and Apply at 2,200 ms. The route method retains
its original 2,400 ms script and Apply at 1,500 ms. CLI retains two 600 ms
smokes. Their unchanged isolated successes are consistent with sensitivity
to concurrent test work. They do not prove repeated stability or establish
that serialization repairs a product defect. No assertion, timestamp,
fixture callback threshold, replay duration, or expected result is relaxed.

No additional family is admitted. Keep the three previously serialized
tests; add only the two CTests with newly observed failures. `RUN_SERIAL`
prevents simultaneous jobs in the same CTest invocation. It does not reserve
CPU, exclude unrelated processes, guarantee deadlines, or qualify physical
MIDI/audio hardware. The independent workspace semantic-view correction
requires its own runtime review and regression evidence.

## Reproducible diagnostics and candidate requirements

The exact diagnostic command arrays and environments are retained in the
[root diagnostic receipt](../development/2026-11-16-heading-title-continuation/reports/additional-native-one-isolated-diagnostics.json).
Each command ran from the repository, sequentially, with no other project
native job. Calibration selected
`HAMMOND_STANDALONE_CALIBRATION_PROBE=/workspace/scratch/5a28c3564dbf/build-native/apps/standalone/hammond_standalone_calibration_probe`;
CLI selected
`HAMMOND_STANDALONE_EXECUTABLE=/workspace/scratch/5a28c3564dbf/build-native/apps/standalone/hammond_standalone`.
Each command used `python3 -B`, its unchanged Python fixture, and the exact
method selector in the table. The fixtures set dummy SDL audio/video drivers
internally; calibration selects its own scenario and private trace. CLI's
method retains both `False` and `True` inversion subcases and two children.

The probe hash was
`886aa8eedd7242e35fd5e169fa9aa257bf399c42a7f6d1818f184aad0d22dca3`;
the ordinary app hash was
`2c64e585d8f1da521ff4c4dafe51613dd3aa0692461bfcb8d6450f9ca4971479`.
Both identities match the original failed-suite banners. The source and
fixture hashes remained unchanged through the isolated diagnostics. This
is evidence about the genuine pre-runtime-edit binaries. Any subsequent
runtime repair must produce and record its own coherently built application
and probe identities.

Root may now add only the two scheduling properties and explanatory comment
in [standalone CMake](../../apps/standalone/CMakeLists.txt). Retain CLI's
12-second child bound, calibration's 15-second child bound, both normal
90-second CTest bounds, and calibration's existing 180-second sanitizer
bound. Preserve commands, environments, test labels, names, scenarios,
fixture bytes, and workload. Source repairs admitted independently must be
listed separately from this scheduling delta.

After reconfiguration, capture actual `ctest --show-only=json-v1` metadata.
Require boolean `RUN_SERIAL=true` for the two new tests and retain the three
existing settings; compare original command vectors, environments, labels,
and timeouts. No original discovered test may disappear. Any separately
admitted regression additions must be identified explicitly. Freeze the
complete candidate inputs and binary identities, then run the complete
suite once with `--parallel 2`, `--output-on-failure`, and `--no-tests=error`,
retaining distinct log and JUnit outputs. Require every discovered test to
pass without retries, exclusions, weakened oracles, or extended deadlines.
For each serialized test, retain log evidence that it starts with no active
test and no other test starts until it completes. A continued failure
requires its own investigation; this admission is not permission to keep
rerunning until green.

A54 performed only read-only inspection and these owned report writes.
Root owns diagnostics, source edits, builds, integration, and publication.
Hosted exact-source VST3 qualification remains a separate pending duty;
this review makes no claim about all hosts, signing, hardware, calibration
measurements, or literal whole-UI 1:1 acceptance.
