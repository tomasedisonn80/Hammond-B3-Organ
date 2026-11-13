# Wave 7 coherent integration and focused repairs

Assignments 37–42 add the shared six-tool Unicode boundary, explicit offline and
native staging, actual-module allocation/automation/concurrency gates and final
legacy compatibility review. This checkpoint excludes the live wave-8 demo,
plotter, handoff and session checker.

## Exact local source and observed results

Root archived staged tree `7c3e1e2e93932dfa59f20e2be8ee4ab7f46b8f73` and built
separate SDK-free and locked-SDK native Release configurations with GCC 14.2.0,
CMake 3.31.6 and Python 3.12.14. The default build completed successfully. Its
first full CTest run passed **67/68 suites in 70.98 seconds**, with one failure
and no skips. `python_test_install` still asserted parameter diagnostic schema 1
although assignment 42 intentionally changed that diagnostic to schema 2. The
other 67 suites passed. Root updated the installed-tool assertion to schema 2,
its exact `sdk-free-core-parameter-mapping` verification scope, both false native
verification flags and the absence of the obsolete implementation flag.

The separate native build used `hammond_vst3_test_inputs` and passed **8/8 native
suites in 6.68 seconds**, with zero failures or skips. Those suites execute local
bundle staging/relocation, the actual SDK validator, controller, loaded-module
ABI/behavior/automation/concurrency and Linux allocation gates. The validator's
retained unsupported-rate and repeated-deactivation diagnostics remain scoped
limitations, not an inferred warning-free result.

The repaired staged tree is `e50351633caddecc212aef3a934378aeda498870`.
Its only changes from the compiled-input tree are `tests/test_install.py`,
`tests/test_native_bundle_inventory.py` and `tools/native_bundle_inventory.py`.
Every CMake, compiled source, header, SDK lock, generated-input and profile byte
is unchanged. The inventory repair is explained in the [platform review](PEDAL_NATIVE_PORTABILITY.md).
Root archived this new tree and ran both changed Python test files with the
original configured CTest environment and unchanged binaries. The install suite
passed **2 methods in 3.067 seconds**; inventory passed **19 methods in 0.203
seconds**, including actual resource-byte and membership mutation rejection.
Both exited zero. These are focused follow-up results, not a claimed second
68/68 full CTest execution. The next exact-source hosted matrix is a separate gate.

The later publication differs from this repaired tree only in Markdown result
records. Its staged manifest remains the historical seven-wave freeze; newer
live worker states and unfinished artifacts are outside the checkpoint.

## Commands and retained local records

With the task-local CMake and CTest executables on PATH, the original commands
configure SDK-free `checkpoint-w07/build-default` and SDK-enabled
`checkpoint-w07/build-native` from the same `checkpoint-w07/source` archive:

```sh
cmake -S checkpoint-w07/source -B checkpoint-w07/build-default -DCMAKE_BUILD_TYPE=Release
cmake --build checkpoint-w07/build-default --parallel 4
ctest --test-dir checkpoint-w07/build-default --output-on-failure --output-junit checkpoint-w07/default-ctest.xml
cmake -S checkpoint-w07/source -B checkpoint-w07/build-native -DCMAKE_BUILD_TYPE=Release -DHAMMOND_BUILD_VST3=ON -DHAMMOND_VST3_SDK_ROOT="$PWD/vst3sdk"
cmake --build checkpoint-w07/build-native --target hammond_vst3_test_inputs --parallel 2
ctest --test-dir checkpoint-w07/build-native -C Release --output-on-failure -R '^(hammond_vst3_validator|test_native_)' --no-tests=error --output-junit checkpoint-w07/native-ctest.xml
```

The follow-up ran the two Python files from `checkpoint-w07/source-repaired`
using the configured CTest environment, including `HAMMOND_TEST_CMAKE`, executable
paths and the compiled profile. `focused-repair-results.json` retains the exact
interpreter, source tree, three-file delta, commands, exit codes and timings.
The two focused logs retain every method result.

| Local record | SHA-256 |
| --- | --- |
| default-ctest.log | `5809915d97651d66e51d7883984e010df48983f76af057ad9e9a91d5663097d4` |
| default-ctest.xml | `a5525a406bcd659e366198a004869d96737d226d19161a60e0114a60c56920b7` |
| native-ctest.log | `6fb448d8af84fd2c28c7ebbfc0df2cf015f12c48fafcd4817e807e2979caf586` |
| native-ctest.xml | `5640d5af5c85460c25696061e9f3562e47f8a7da8e3c09b927d7453c5a88bc66` |

## Remaining gate

Publish with an expected-parent guard, verify the fetched exact tree, and inspect
all four core and three native hosted jobs. Specifically observe Windows bundle
inventory and the uploaded native payload, rather than treating native CTest
success alone as completed packaging. Preserve any failure and its diagnostics.
Wave 8 then integrates the separately accepted pedal demo/plots and handoff.
