# Capture/calibration wave 3 integration

## Qualified source and scope

Root accepted assignments 13–18 and froze local source commit
`0a4e0b156fdb8d08246a2fe2ed032cebbdee335a`, tree
`cfc2036c30ee627ed4a7c6137ffc928ea590b513`. A fresh `git archive` of that
commit was extracted to `/workspace/scratch/c9f3ead4c910/w3-source` and built
in the separate `/workspace/scratch/c9f3ead4c910/w3-build` directory.
Live wave-4 changes were excluded. This report is a later documentation-only
addition and does not retroactively change the tested source identity.

This checkpoint implements complete-stream audio inspection and windows,
immutable corpus admission and split auditing, and fixed array comparison
metrics. It includes independently authored acceptance and operating guides.
It does not yet include policy evaluation, file-comparison jobs, study replay,
installation, or the later adversarial suites. No core or native adapter source
was changed by this checkpoint.

## Environment and actual commands

Linux x86_64; GCC **14.2.0**, CMake/CTest **4.4.4**, Python **3.12.14**.
The CMake executable was
`/home/agent/.cache/uv/archive-v0/kvsqq5-iHdbf13RC/cmake/data/bin/cmake`;
CTest was its sibling executable. CMake selected
`/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3.12`.
The following commands show the actual arguments, using `cmake` and `ctest`
as abbreviations for those absolute executables:

```sh
cmake -S /workspace/scratch/c9f3ead4c910/w3-source -B /workspace/scratch/c9f3ead4c910/w3-build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON -DHAMMOND_BUILD_VST3=OFF -DHAMMOND_BUILD_STANDALONE=OFF
cmake --build /workspace/scratch/c9f3ead4c910/w3-build --target hammond_render --parallel 3
ctest --test-dir /workspace/scratch/c9f3ead4c910/w3-build --output-on-failure --no-tests=error --output-junit /workspace/scratch/c9f3ead4c910/checks/w3-ctest.xml -j 3 -R '^python_test_(audio_analysis|capture|capture_audio|capture_common|capture_comparison|capture_corpus|calibration_session_records|repository_integrity)$'
```

Configuration and the fresh renderer/profile build passed. CTest supplied that
build's renderer and compiled profile to the legacy analyzer integration. The
focused gate passed **8/8 suites**, zero failures, in **4.14 seconds**:

| Required suite | Observed result |
| --- | --- |
| `python_test_audio_analysis` | Passed; all 15 methods including the actual C++ renderer integration. |
| `python_test_capture` | Passed; 41 legacy capture-v1 methods. |
| `python_test_capture_audio` | Passed; 41 independent sample/format/identity/window methods. |
| `python_test_capture_corpus` | Passed; 47 independent corpus/lineage/split methods using actual files and decoder. |
| `python_test_capture_comparison` | Passed; 42 independent metric/report methods. |
| `python_test_capture_common` | Passed; retained strict JSON and no-clobber publication acceptance. |
| `python_test_calibration_session_records` | Passed; 27 session-record methods. |
| `python_test_repository_integrity` | Passed; 41 repository/source-integrity methods. |

The three new independent suites total **130 methods**. Producer smoke assertions
are separate evidence in their notes and are not added to that method count.
Root also repeated all three suites directly before freezing the source.
This is a focused eight-suite qualification; it is not a claim that the entire
repository test set was rebuilt or rerun. The separate starting-source full
Release run remains [85/85 suites](CALIBRATION_BASELINE.md).

From the frozen source directory, these explicit checks also passed:

```sh
python3 -B tools/check_calibration_session.py --repo . --expected-complete 18 --json
python3 -B tools/check_repository.py --root . --json
```

The current-session checker reported 18 complete assignments, complete waves
1–3, 20 retained actual identities, two running assignments and 40 planned rows
at this frozen snapshot. Later live dispatches are recorded separately. The
checker verifies retained consistency, not external dispatch. The repository
checker independently confirmed the unchanged 21,248,265-byte, 500-page atlas,
its declared SHA-256, 80-chapter index and 2,598 local links across 459 Markdown
files. Its older sixty-note check belongs to the historical session and is not
used as this session's count. The staged diff check was clean.

## Retained setup failure and repairs to test expectations

Before the frozen build, root ran the legacy analyzer directly in the live
checkout. Its first 14 methods passed, but renderer integration could not start:
`HAMMOND_RENDER_EXECUTABLE` and the default checkout build were absent. That run
ended with one setup error and did not establish an integration pass. Building
the renderer/profile from the frozen source and rerunning through CTest resolved
the setup issue; the final 15-method analyzer result above is the executed gate.

The independent audio and metric authors each corrected an auxiliary control
that had incorrectly assumed Python's built-in `sum` was naive sequential
addition. Their independent expected values and production tolerances were
preserved. The corpus author corrected an expected graph that had overlooked
byte equality when the same raw bytes were interpreted with different geometry.
The corrected test requires the byte relationship and distinct decoded
identities together. All original failures and corrections remain in the
assignment notes; no production change was needed to pass these three suites.

## Limits and continuation

Deep malformed/resource/filesystem admission, reusable policy parsing and
uncertainty evaluation, exact file-job composition, replay and installation are
later assignments. Maximum admitted workloads, native Windows/macOS behavior,
physical recorder/device operation and hardware fidelity were not qualified by
this gate. Reports retain explicit unknown physical claims. No current hosted
CI pass is inferred from these local results or from a queued workflow.

Continue with the [operating handoff](../CALIBRATION_HANDOFF.md) and the
[actual session](../development/2026-11-13-calibration/README.md). Publish this
reviewed checkpoint with an expected-head guard, verify the fetched tree, and
retain separate source identities when later policy or parser changes are tested.

## Concurrent standalone integration before publication

Before the planned push, root observed remote `main` advance to
`5b8e2419d23fe27c51709d717812060eafd44dcc` (standalone replay, benchmark, chapel
catalog/controls and retained package evidence). Root fetched and inspected that
commit, then merged it without conflicts while preserving the live wave-4 work.
The combined local source is commit
`8864c051d19556e37dffcd7366fd859606958bc3`, tree
`e4f56a7c722dcad4eda9269d907715b8526dd8cd`.

A new `git archive` was extracted to
`/workspace/scratch/c9f3ead4c910/w3-combined-source`, with a separate
`w3-combined-build`. Under the same toolchain and Release/BUILD_TESTING/native-OFF
options above, configuration, the **complete default build**, and the unfiltered
required CTest command passed:

```sh
cmake --build /workspace/scratch/c9f3ead4c910/w3-combined-build --parallel 3
ctest --test-dir /workspace/scratch/c9f3ead4c910/w3-combined-build --output-on-failure --no-tests=error --output-junit /workspace/scratch/c9f3ead4c910/checks/w3-combined-ctest.xml -j 3
```

Observed result: **93/93 suites passed**, zero failures, in **59.29 seconds**.
The native adapters were OFF; this is not a new SDL-device, native VST3 or DAW
qualification. The incoming track's independent native evidence keeps its own
revision and scope. The complete source, core consumers and tests came from this
one archive, with no live-header/older-library mixture.

Wave-4 reviewers subsequently found a corpus descriptor-ownership failure path
and an audio malformed-field error-precedence defect. Their later production
repairs are **not** part of this 93-suite source identity. Root repeated the
41-method audio and 47-method corpus suites successfully on the repaired files;
new adversarial acceptance and the later coherent wave-4 gate qualify those
changes separately. The earlier passing snapshot is preserved as evidence,
not presented as a pass for a later implementation.
