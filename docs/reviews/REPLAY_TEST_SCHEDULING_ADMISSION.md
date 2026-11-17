# Native replay scheduling admission — A54, wave 9

## Decision and boundary

**Admit the scheduling-only `RUN_SERIAL TRUE` correction for exactly
`test_standalone_native_midi_replay` and
`test_standalone_workspace_replay`.** Root completed the required single,
unchanged isolated execution of each failing method: MIDI passed in 1.904
seconds and workspace passed in 4.048 seconds. A54 verified their successful
one-method logs and hashes against the
[isolated diagnostic receipt](../development/2026-11-16-heading-title-continuation/reports/combined-one-isolated-diagnostics.json);
no relevant input changed. The complete candidate suite remains pending.
Keep the already admitted
`test_standalone_app` property. No broader family isolation is justified by this
record. A54 did not execute native children, edit CMake or fixtures, change the
index, or perform remote mutations.

The original combined run remains **239/241**, exit 8, 502.324 seconds at the
root wrapper and 502.21 seconds reported by CTest. All 474 frozen code inputs
were unchanged. Its original log is 125,501 bytes, SHA-256
`e25e8b47838da8998aad0c1fd9df5dfcedcfa496e37b55d468b625355ea53c1c`.
This failure is not replaced by any later successful run. The
[machine-readable admission](../development/2026-11-16-heading-title-continuation/reports/a54-replay-scheduling-admission.json)
contains losslessly compressed, independently hashed original failure blocks,
the immutable input identities, and the exact diagnostic commands. The root
[coherent result](../development/2026-11-16-heading-title-continuation/reports/combined-final-coherent-results.json)
ties that original log and JUnit to the
[474-input receipt](../development/2026-11-16-heading-title-continuation/reports/combined-final-coherent-inputs.json).

## What actually failed

| CTest and original result | Observed failure | Requirement retained |
| --- | --- | --- |
| `test_standalone_native_midi_replay`: 15 methods, one failure; 44.47 seconds at CTest | `test_cc123_releases_only_its_external_division_and_preserves_ui` found no acknowledged musical observation in `[950,1230)` ms | At least one observation in the existing half-open interval whose applied sequence is at least its submitted sequence, followed by the exact held-owner assertion |
| `test_standalone_workspace_replay`: six methods, one failure; 50.58 seconds at CTest | `test_focus_memory_restores_drawbar_save_and_load_after_returns` first recorded the loaded state at 292 ms | The first observation must remain strictly earlier than 180 ms, with the existing acknowledged sequence and subsequent command-count requirements |

The MIDI fixture retains its 1,600 ms replay, seven UI events, connect event,
six note-on packets at 150 ms, and CC123 packets at 650, 950, and 1,250 ms. Its
copied diagnostics show an observation at 1,095 ms with applied sequence 13
and submitted sequence 14. The next recorded observation with applied and
submitted sequence 14 is at 1,259 ms. Thus the recorded data does fail the
existing interval predicate; successful eventual release would not satisfy
it. The earlier two interval assertions had returned before this failure.
The final-state, decoder-action, and retirement assertions following the
failed assertion were not established by this method execution. See the
[original fixture](../../apps/standalone/native_tests/test_standalone_midi_replay.py).

The workspace fixture retains its 3,750 ms journey, original 87 UI events,
workspace returns, drawbar focus memory, Save/Load, Flat mode, and 960×700
resize. Its first copied observation has elapsed 292 ms and
applied=submitted=resolved sequence 3. The exact control-path and held-path
checks precede `assert_commands` and returned; the loaded-state timing check
inside that helper failed. Later command-count, view-history, and saved-byte
assertions must not be reported as passed. This is distinct from the earlier
paint-copy omission and repaired Load chronology oracle. See the
[workspace fixture](../../apps/standalone/native_tests/test_standalone_workspace_replay.py).

## Scheduling inference and its limits

The original CTest log shows the MIDI test starting while `scaled_view` was
still running, then `workspace_replay` starting before MIDI completed. After
the MIDI failure, `preset_raster` starts and finishes before the workspace
failure is reported. That establishes concurrent CTest work, including
overlap between the two failing suites. It does not measure CPU scheduling,
identify an exact blocking thread, or prove the cause of either missed
observation. Scheduling sensitivity is a hypothesis to test by the single
isolated diagnostics, not an established hardware or audio defect.

The existing
[native smoke scheduling admission](NATIVE_SMOKE_SCHEDULING_ADMISSION.md)
provides a narrowly scoped precedent: unchanged assertions, one isolated
pass, explicit generated `RUN_SERIAL` evidence, and observed exclusion of
other CTests. It is not a blanket permission to serialize every native test.
Other actual-app suites passed in the original combined run. Some also use
bounded observation windows, while others primarily require final state,
operation bounds, or input rejection. Their passing result does not prove
immunity to host load, but this record supplies no observed failure requiring
a policy change for them. A family-wide rule would change more scheduling
than the evidence supports.

`RUN_SERIAL` excludes other jobs in the same CTest invocation while that test
runs. It does not grant process priority, reserve hardware, exclude unrelated
processes, or guarantee real-time deadlines. The proposed correction retains
every application and fixture byte, all event timestamps, all observation
predicates, both nine-second process bounds, and both 90-second CTest bounds.

## Required diagnostic and acceptance sequence

1. After the frozen full run has finished, root executes each unchanged
   failing method **once**, sequentially, with no other project native job
   running. Use the actual executable named by the generated CTest metadata:
   `/workspace/scratch/5a28c3564dbf/build-native/apps/standalone/hammond_standalone`,
   SHA-256
   `2c64e585d8f1da521ff4c4dafe51613dd3aa0692461bfcb8d6450f9ca4971479`.
   The exact selectors are
   `NativeMidiReplayAcceptance.test_cc123_releases_only_its_external_division_and_preserves_ui`
   and
   `NativeWorkspaceReplayAcceptance.test_focus_memory_restores_drawbar_save_and_load_after_returns`.
   Capture command, executable and fixture hashes, exit, elapsed time, and
   complete bounded output separately from the original failure. If either
   fails again, this admission remains unfulfilled: retain its evidence and
   investigate before changing scheduling. Do not repeat until green.
2. If both pass, root may add only the two `RUN_SERIAL TRUE` properties in
   [the standalone CMake file](../../apps/standalone/CMakeLists.txt), with a
   factual comment linking this admission. Preserve test names, commands,
   environments, labels, target wiring, workloads, and timeouts. Retain the
   existing smoke-test serialization. Reconfigure the same build and record
   the exact source/input change and unchanged native executable and fixtures.
3. Capture fresh `ctest --show-only=json-v1` output after reconfiguration.
   Require both new properties to be boolean true; require their 90-second
   timeouts, labels, command vectors, and executable selection to match the
   original discovery. Verify the complete discovered test set remains 241.
   Source text alone is insufficient proof that CTest received the setting.
4. Run the complete candidate suite once with the original `--parallel 2`,
   `--output-on-failure`, `--no-tests=error`, and distinct JUnit/log output.
   Freeze and recheck its coherent inputs. Require all 241 tests to complete
   successfully without exclusions, retries, added timeouts, or test-oracle
   changes. Parse the start/completion sequence: each newly serial test must
   start with an empty active-test set, and no other test may start until it
   completes. Retain this observed nonoverlap evidence alongside generated
   metadata. Failure of either check leaves candidate qualification open.

The isolated-diagnostic admission condition is now satisfied. Root may
apply the two properties and begin the candidate qualification. Acceptance
of that candidate still requires steps 2–4 above; the machine-readable report
records subsequent evidence separately when root provides it. The original
failed run remains immutable. Local scheduling
qualification does not substitute for exact-published-source hosted runs,
all-host VST3 compatibility, physical MIDI/audio/display evidence, reference
calibration, signed packages, or literal whole-UI 1:1 acceptance.
