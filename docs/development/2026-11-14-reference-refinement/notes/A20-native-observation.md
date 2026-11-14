# A20 — Applied held and pointer-capture observations

Worker `/root/w04_a20_native_observation_impl`; current scope and desktop contract
read. Base HEAD `e4968b2acd37b6f79683704356350070fe2fc329`, tree
`1aff4305e347b46c659dcbc27eb524649a4c54c8`; the shared checkout contains other
workers' changes, preserved. Root authorized the shared presentation validator
addition alongside the two originally assigned source files.

## Changes and meaning

Each successfully flushed presentation frame now copies Upper/Lower/Pedals
held-target counts from the exact `UiModel::view().applied` used for painting.
`held_targets` counts logical targets, not independent owners or audibility;
`inspection.snapshot_available` still distinguishes an observed snapshot from
default state. The frame also records `pointer_capture.sdl_captured` from the
application's `captured_` flag and `ui_captured` from `UiModel`.

Fixed-size saturating counters record SDL capture attempts, successful API
admissions, subsequently missing capture flags, and explicit release calls.
`losses` requires a formerly admitted capture; dummy refusal therefore has an
attempt without a success/loss/release. `release_calls` records the call, not a
successful OS return. Header clicks can acquire and release between paints;
counters preserve that distinction without claiming a held frame existed.
Changes to counts, flags or counters retain a presentation observation within
the existing 512-record limit. No Session reads, audio/control semantics,
timing hooks, parser limits or schema-version changes were introduced.

The shared exact schema validates additive fields, types, bounded target
counts, monotonic counters and successful-admission relationships. Workspace
acceptance requires painted holds in consecutive workspace/Flat visits,
including return visits and resize, retained count transitions, and the correct
pre-shutdown released state. It independently identifies dummy capture refusal.
Original note identities, ownership commands, Save bytes and deadlines remain.

## Executed verification

From the repository root, after coordinated exclusive build access:

```sh
../build-tools/cmake/data/bin/cmake --build ../build-native --target hammond_standalone --parallel 2
HAMMOND_STANDALONE_WORKSPACE_EVIDENCE="$PWD/docs/development/2026-11-14-reference-refinement/reports/A20-workspace-replay" ../build-tools/cmake/data/bin/ctest --test-dir ../build-native --verbose --output-on-failure --no-tests=error -R '^test_standalone_workspace_replay$'
```

Both exit zero. **1/1 CTest, 6 Python methods, 30 native processes passed**:
44.60 seconds CTest, 44.506 seconds Python. Each process used SDL dummy
audio/video, software rendering and the unchanged nine-second deadline;
CTest retained its 90-second deadline. There were 116 capture attempts, zero
admissions, and at most 23 retained presentation observations. All 30 processes
exited zero with empty stdout/stderr. `git diff --check` passed for owned code.

GCC 14.2.0 Release; SDL commit
`5d249570393f7a37e037abf22cd6012a4cc56a71`. Executable SHA-256:
`291c0cf0a9815ab029eaef8fd1a100aab9b35da40b094c1c45841f3e25af445e`.
Exact source, cache, dependency, argv, report and 122 retained replay-file
identities are in `reports/A20-source-build.json` and `reports/A20-result.json`;
raw build/CTest logs and scripts/diagnostics remain adjacent.

| Changed source | SHA-256 |
| --- | --- |
| `apps/standalone/main.cpp` | `c8a802218ea0980651c7fb46b1a2afd4a0da63a600385cbfc41fe0e865af9f5b` |
| `apps/standalone/native_tests/test_standalone_workspace_replay.py` | `28b61802b99233e5f7ee14d01f5456b15bdff235309038b2943e75863d6097f7` |
| `apps/standalone/native_tests/test_standalone_app.py` | `655d38d62d9018abbb2f4a1f8c09d9fc54427438ed472f0afd761cc446bcaf6a` |

## Remaining qualification and next task

Root must rebuild the desktop executable and retain new actual X11 frames and
diagnostics. Earlier desktop evidence identifies an earlier binary. Successful
capture admission alone does not establish persistent OS delivery; held
navigation, off-window release/return and held-pedal branch crossing require
their actual observed journeys. Full wide/minimum journeys, broader regression,
physical audio/MIDI, DPI and accessibility remain separate gates. This worker
used no GUI, committed nothing and released build-native after the targeted pass.
