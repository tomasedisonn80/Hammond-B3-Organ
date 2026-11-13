# Scanner foundation: coherent wave2 integration

## Qualified source

Commit `74473facf8efc3332497ab969017c718458d6921`, Git tree `6c76bba650c033d9e8ade7ba3b2347ce569a10b6`, was checked out into the separate detached worktree `/workspace/scratch/1742da7072be/scanner-w2-source`. A new build at `/workspace/scratch/1742da7072be/scanner-w2-build` used only that committed source. Concurrent unfinished runtime headers/sources in the main working checkout were excluded. This report is a later documentation-only addition; the qualified production/test inputs below are unchanged.

Toolchain: GCC14.2.0, CMake4.4.4, Ninja1.13.2, Python3.12.14, Linux x86_64. The original source PDF remains unchanged and the new fixture remains documentary/unmeasured.

## Actual commands and results

```sh
git worktree add --detach /workspace/scratch/1742da7072be/scanner-w2-source 74473fa
cmake -S /workspace/scratch/1742da7072be/scanner-w2-source -B /workspace/scratch/1742da7072be/scanner-w2-build -G Ninja -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build /workspace/scratch/1742da7072be/scanner-w2-build --parallel 3
ctest --test-dir /workspace/scratch/1742da7072be/scanner-w2-build -C Release --parallel 3 --output-on-failure --no-tests=error
```

The configure/build succeeded. **73/73 CTest suites passed, zero failures, in50.00seconds.** This includes all71 earlier suites and the two scanner suites (19graph/compiler and16AC unittest methods). Root also ran both new suites directly and the existing repository-integrity check; all passed. The new graph generation command passed from a previously nonexistent generated-header directory.

The retained worker records report564 full-grid AC solves,10716 signed tap transfers, maximum normalized residual3.2486101684985267e-16 and maximum independently recursed ladder error5.6647284161045834e-14. Primary review compares all50passives,19outputs and27nodes. The schema duplicate-identity defect, its repair and regressions are retained in assignment11. No source/measurement status was promoted by numerical agreement.

The earlier optional native baseline also built. The initial native-filtered invocation passed eight suites but the SDK validator was not run because it was not built by the default target. Building `validator` passed its51SDK selftests; the missing actual-module validator CTest then passed1/1. This was a setup omission, not a product failure or an inherited scanner-enabled qualification. Future native checks should use `check_vst3` to build their inputs first. No new native scanner path exists in this checkpoint.

## Qualified input identities

| Input | SHA-256 |
| --- | --- |
| `data/scanner/atlas-late-b3-nominal-v1.json` | `1d236be5e6b63e938a9f147808386173949d167e09aee8e902c55002e4ea4604` |
| `data/scanner-line.schema.json` | `602d3b75f316d0c0523c1ecab49204607785ce8f83508a3e0014d22793221f29` |
| `tools/compile_scanner_line.py` | `56c60cf511144d552fdeb2708711b32469f350593b391c7619ebb92b41b6dd7e` |
| `tools/scanner_ac_reference.py` | `5472dbe96839a64e864e3d6275ea326b6a497fe5c06997f0a23a3d230763bd1e` |
| `tests/test_scanner_line_profile.py` | `6026225d5f4150446fc63b5442c8aaf911eea3c1ef25d141df829dd977fa5dca` |
| `tests/test_scanner_ac_reference.py` | `cbdea600b273cbf21d8d4d2d116c9f04ca0eac2f7f1e4787972baa5da84bfa1b` |
| `docs/SCANNER_NUMERICAL_CONTRACT.md` | `3999a3a409d397401e135e8285704092bad130911468802370bf6da404d58ff9` |
| `CMakeLists.txt` | `5450e69f593af64c5cb714b0e462d3ba2c31720531c699684cc85095dfdcfdb0` |

## Scope and next work

G1 graph and G2 reference requirements have their recorded nominal engineering evidence. The published numerical contract was frozen before runtime grading. Prepared C++ line, independently stamped transient reference, rotor, same-hertz/sideband/filter policy, Engine/native integration and measured physical M4 remain separate gates. All 45 existing parameter records, legacy state formats and Engine/native processing inputs remain unchanged from the starting commit.

The first twelve actual assignments are complete in the new session ledger; runtime assignments beginning with 13 are distinct ongoing work. This report does not attest all 60 requested assignments complete. Publication and hosted CI must be confirmed from the actual remote independently.
