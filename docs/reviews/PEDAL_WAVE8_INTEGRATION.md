# Wave 8 coherent integration

## Qualified source and actual execution

Root archived staged Git tree `5370890e32045a556cb61a88cdb1f04fb5a18f7e`,
containing 534 files. The freeze includes completed assignments 43–48, the
original retained demo and three trace SVGs, the independent demo/plot/session
checks, the current handoff and scanner gate, and root's 23-file OfflineTools
integration. It excludes wave-9 reviews and subsequent tool repairs. Its actual
manifest has 48 complete, three running and nine planned assignments: 51 distinct
newly dispatched workers and eight complete waves.

The original repository checker, preceding console-session checker and this new
pedal-session checker each passed their separate scopes. The explicit new-session
command was `python3 tools/check_pedal_session.py --expected-complete 48`; earlier
sixty-worker records provided no completion credit to it.

Fresh SDK-free and pinned-SDK native Release configurations were built from the
same archive with GCC 14.2.0, CMake 3.31.6 and Python 3.12.14. Both builds succeeded.

| Executed scope | Observed result |
| --- | --- |
| All registered SDK-free Release suites | **71/71 passed**, 54.37 seconds; zero failures, disabled tests or skips |
| Focused actual native module suites | **8/8 passed**, 7.87 seconds; zero failures, disabled tests or skips |
| Original/console/pedal record checks | All passed; current pedal count explicitly 48 complete |

The default run includes the new retained-demo, plotter and session-checker
suites. The actual install/relocation test checks exactly 23 files, unchanged
payload bytes, installed commands from an unrelated directory without Hammond
environment variables, all three pedal traces and their source/installed SVGs,
embedded CSV hashes, failed replacement preservation and missing-script
preflight preservation. The actual native run separately stages and relocates
the bundle and executes validator/controller/ABI/behavior/automation/concurrency
and Linux allocation gates. No DAW, audio-device, custom-interface or physical
fidelity qualification is inferred.

The local module remains byte-identical to the previously qualified local module:
434,168 bytes, SHA-256
`d87353b237e52c8d1f91af27933493a4cf78ba4a06af4a96c9930c0ecec1d3ff`.
The unchanged 4,545-byte compiled profile has SHA-256
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.
This is observed local identity, not a promise of compiler-independent binaries.
The SDK validator's unsupported-rate and teardown diagnostics remain retained.

## Reproduction commands

With the task-local CMake/CTest executables on PATH:

```sh
cmake -S checkpoint-w08/source -B checkpoint-w08/build-default -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build checkpoint-w08/build-default --config Release --parallel 3
ctest --test-dir checkpoint-w08/build-default -C Release --output-on-failure --no-tests=error --parallel 2 --output-junit checkpoint-w08/default-ctest.xml
cmake -S checkpoint-w08/source -B checkpoint-w08/build-native -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DHAMMOND_BUILD_VST3=ON -DHAMMOND_VST3_SDK_ROOT="$PWD/vst3sdk"
cmake --build checkpoint-w08/build-native --config Release --parallel 2 --target hammond_vst3_test_inputs
ctest --test-dir checkpoint-w08/build-native -C Release -V --output-on-failure --no-tests=error -R '^(hammond_vst3_validator|test_native_)' --timeout 300 --output-junit checkpoint-w08/native-ctest.xml
```

The root orchestration retained exact absolute arguments, exits and measured
command durations in `checkpoint-w08/default-results.json` and
`checkpoint-w08/native-results.json`; configure/build/CTest logs and JUnit files
are alongside them. The CTest summary timings above differ slightly from the
orchestration's process wall time because process setup/teardown is included
only in the latter.

| Retained local record | SHA-256 |
| --- | --- |
| default-ctest.log | `b3b1fe390404bb2fe2927521a0d00f950e34bd31d1996c2eb922f55265b88ae6` |
| default-ctest.xml | `92bff799c7a0521015ef006f850e184710f2e402f4d85ec28abd6596d276945f` |
| native-ctest.log | `77e2ea25667950b4f650bdf134f0f03c48faadae700d7223eb551695d88daf52` |
| native-ctest.xml | `c42a1b1558bea08c6cbd350fa384427cf7600fca0b6cdf5ac9227c0ce349f096` |

Final result publication differs from the qualified tree only in Markdown.
The manifest remains the exact 48-complete freeze; later accepted worker notes,
manifest changes and code repairs stay outside this checkpoint. Publication
uses an expected-parent update and fetched tree comparison. Hosted results
must be observed at that exact published commit.

## Next action

Finish the twelve actual wave-9/10 assignments, qualify any concrete repairs,
observe the four core and three native jobs and their real artifacts, then run
the explicit sixty-complete session gate and publish the final handoff. The
[remaining M3/scanner contract](../M3_REMAINING_AND_SCANNER_GATE.md) specifies the
next product change after that session. It is a plan with documentary/nominal
inputs and numerical acceptance criteria, not an implemented scanner runtime.
