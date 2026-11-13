# Standalone native checkpoint after assignment 27

This integration report covers accepted standalone work through assignment 27.
The ledger records actually dispatched later workers as running; their unfinished
files are excluded from this publication. Root owns CMake, app integration,
shared status and publication. Worker notes preserve independent test ownership.

## Executed source scopes

| Gate | Exact scope and observed result |
| --- | --- |
| Full frozen Release | Local commit `738162f0bc36f88f8c76268d04831862a8118d10`, tree `915e55dc7c3ad022042b188498aa41f2a7f40795`; new 685-file archive and native build; **83/83 suites**, zero failures, 78.62 seconds. |
| Subsequent native group | Stable Session/UI/device sources plus accepted assignments 21–27, native install and final path-admission repair; **9/9 suites**, zero failures, 8.62 seconds with two CTest workers. |
| App input identity | Final repaired `main.cpp` SHA-256 `fd7095bde479c4acf3079f0972d6f907034f546a6a1d1cef398caad92eb0b212`; actual executable `f820e7a619be733cd72ac9c3e0a12f2c5391518897608934cf055f94e9c03ce9`. |
| Independent app acceptance | 18 methods, 164 actual executable invocations; no Linux skips. The assembled repeat passed in 8.61 seconds. |
| Relocation | Three maintained installation methods; exact nine-file component, relocated executable and dummy smoke; assembled repeat passed in 2.72 seconds. |
| Allocation and concurrency | Real SDL callback calibration and zero original-callback C++ allocation/deallocation; separately coherent core/Session ThreadSanitizer pass. See the linked contracts for finite workload and instrumentation limits. |
| Replay helper | 573 valid parses, 186 parser rejects, file/forged-plan boundaries and actual SDL queue/marker behavior. Integrated native CTest passed in 0.02 seconds. |

The later gate does not replace the preceding full gate with a new whole-tree
claim. Engine/public core headers, source data and control/UUID identities are
unchanged by these additions. Replay application behavior and benchmark remain
subsequent work. New hosted workflow execution is pending, distinct from the
successful earlier workflows for `96a37a9`.

## Commands and environment

Working directory: `/workspace/scratch/5ba97739b54c`. CMake/CTest 4.4.4, GCC
14.2.0, Python 3.12.14, Linux. CMake lives under the existing build-tools
directory because it is not on the shell PATH. SDL2 is the verified external
2.32.10 checkout at `5d249570393f7a37e037abf22cd6012a4cc56a71`.

```sh
cmake_bin=/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin
"$cmake_bin/cmake" --build build-native-app \
  --target hammond_standalone_test_inputs --parallel 4
"$cmake_bin/ctest" --test-dir build-native-app -R '^test_standalone_' \
  --no-tests=error --output-on-failure --parallel 2
```

Native tests select SDL's dummy audio/video explicitly. Container compilation
lacks the development headers for real Linux desktop/audio backends. The new
hosted workflow requires those compiled backends but still labels its execution
as software-only dummy smoke. Neither kind of check establishes hardware sound,
device latency, physical capture, native accessibility or instrument fidelity.

## Repairs, history and next steps

Independent app acceptance exposed state/output aliases through nonexistent
leaves and symlinked parents, then a dangling state symlink targeting an output.
Root compares weakly canonical absolute paths, retains existing-hardlink checks
and rejects selected symbolic-link leaves before opening audio or writing output.
All rejection fixtures preserve the complete original filesystem trees. This
does not promise safety against adversarial concurrent filesystem mutations.

The frozen full gate predates those admission repairs; the final app identity
and focused repeat above identify their actual verification. Earlier interrupted
CTest and configure setup issues remain recorded in the development log and
worker reports. Publication must inspect and incorporate remote `main` advances,
preserve their scope, and verify fetched tree equality without force-pushing.

Next: connect replay to main, execute scripted musician workflows, wire and
independently validate the benchmark, inspect hosted platforms, retain final
screenshots and complete the remaining real assignments. The operational
[handoff](../STANDALONE_HANDOFF.md) names prerequisites and build commands.
