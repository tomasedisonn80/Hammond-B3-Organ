# Assignment 20 — independent nominal rotor acceptance

- Agent: `/root/w04_a20_rotor_acceptance`
- Session: `2026-11-13-scanner`, wave 4, assignment 20 of 60.
- Result: **complete**; independent strict Release acceptance passed. No production defect, tolerance change or skipped case was observed.
- Owned files: `tests/test_scanner_rotor.cpp`, `docs/SCANNER_ROTOR_ACCEPTANCE.md`, and this note.

## Inputs and independence

Read standing instructions, current README/status/next steps/handoff, the session
README, plan and atlas review, frozen numerical contract section 6, source gate
maps, and the retained primary phase-origin review. Freshly extracted and read
atlas pp. 163–170 as text. This assignment did not render their figures or
independently reread the external paper. It retains the source review's limited
documentary support for the sixteen-position cycle and speed uncertainty.

The oracle sums circular triangular basis functions around each terminal's
occurrence centers, with separately transcribed one-based source maps. It does
not reuse the production interval selector, interpolation, traversal arrays,
mode helpers or generated data. [The acceptance document](../../SCANNER_ROTOR_ACCEPTANCE.md)
explains equations, exact coverage, limits and next work.

The observed parent HEAD was `80ea8cd2d7febe12fc4dd382e475a00ff4181eac`, tree
`d98d9baf666f048629f5c817ed0f040b215df0e4`, also the locally fetched remote head.
Scanner runtime and this test were uncommitted additions during execution;
that HEAD alone does not identify them. Worker 19 explicitly froze its header
and source before the isolated build. Relevant exact bytes are recorded below.

| Input | SHA-256 |
| --- | --- |
| `tests/test_scanner_rotor.cpp` | `b7c04d4c91c09f27bc8701831cf889fed5e1e29d4cf59150ba58100505db5926` |
| `include/hammond/ScannerRotor.h` | `3ca846fc72224114194d73272f410fa2cbe3c0cae94c4fb23105536c7afb4d5a` |
| `src/ScannerRotor.cpp` | `f1dbd65a92036fef9957d280d2aafe9bd8579414ef632a6e2c525e370907b2a0` |
| `include/hammond/ScannerLine.h` | `c249f7c5556d6a6c8c58978928f0b860be442cb1188d35e49c59575729af00c7` |
| Frozen numerical contract | `3999a3a409d397401e135e8285704092bad130911468802370bf6da404d58ff9` |
| Nominal line authoring fixture | `1d236be5e6b63e938a9f147808386173949d167e09aee8e902c55002e4ea4604` |

## Commands and observed results

Working directory: `/workspace/scratch/1742da7072be/Hammond-B3-Organ`.
Toolchain: GCC 14.2.0, CMake 4.4.4, Ninja 1.13.2 and Python 3.12.14. The configured
project's strict warning flags and C++20 applied; `TestSupport.h` checks remain
active in Release. The isolated build directory was `../a20-build`.

```sh
PATH=/workspace/scratch/1742da7072be/build-tools/bin:$PATH cmake -S . -B ../a20-build -G Ninja -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
PATH=/workspace/scratch/1742da7072be/build-tools/bin:$PATH cmake --build ../a20-build --target test_scanner_rotor -j 3
PATH=/workspace/scratch/1742da7072be/build-tools/bin:$PATH ctest --test-dir ../a20-build --output-on-failure --no-tests=error -R '^test_scanner_rotor$'
../a20-build/test_scanner_rotor
```

Initial build and test passed. A focused test improvement then added an actual
running wrap at every internal-rate label and retained the pre-rejection control
for overflow replay. The final rebuild passed; required CTest passed **1/1 in
0.06 seconds**. Direct final output reported:

| Metric | Observed |
| --- | ---: |
| Direct stateless cases | 23,616 |
| Synthetic chorus return cases | 288 |
| Largest direct angular-oracle error | `5.55111512312578270212e-17 V` |
| Largest chorus-return error | `1.11022302462515654042e-16 V` |
| Checked clock frames | 76,800 |
| Largest analytical phase discrepancy | `5.62909636438180260853e-14 turns` |
| Prepared-object rejected calls | 716 |
| Exact continuation frames | 29,766 |
| Ordered host-rate migration pairs | 9 |
| Exact partition comparison paths | 12 |

All fifteen research-rate labels, six modes, nineteen line-output indices,
required signed vectors, center/interior/nearest-boundary phases, mode helpers,
voltage/phase/rate bounds, unprepared precedence and interval overflow are
covered. No root CMake, status, manifest, Engine, controls, native adapter or
production source was edited. Git index, commits and remote refs were untouched.
Final owned-file whitespace, trailing-newline and all eight local documentation
links passed. The producer header/source still matched their frozen hashes.

## Handoff

This is the independent rotor/G4 portion of `scanner-numerics-v1`, under the
named unloaded triangular approximation. The parent must integrate it into a
coherent frozen build, update shared status and publish under the standing
workflow. Combined routing, actual bypass/disconnected-call scheduling,
allocation, G5 line/sideband/filter policy, G6 Engine/native behavior and measured
M4 remain separately owned. Retain failures and inconclusive results; no
electrical accuracy limit or source claim was broadened to close this assignment.
