# Assignment 19 — nominal unloaded scanner rotor

- **Worker:** `/root/w04_a19_scanner_rotor`
- **Wave:** 4; assignment 19 of this session's requested 60.
- **Status:** completed for integrator review on 13 November 2026.
- **Owned paths:** `include/hammond/ScannerRotor.h`, `src/ScannerRotor.cpp`,
  `docs/SCANNER_ROTOR.md`, this note.
- **Inspected base:** commit `80ea8cd2d7febe12fc4dd382e475a00ff4181eac`, tree
  `d98d9baf666f048629f5c817ed0f040b215df0e4`; the local remote-tracking ref matched.
  The coordinated line header/runtime from assignment 13 were live uncommitted
  dependencies, not files claimed present in that base commit.
- **Shared changes:** none; no Engine/native/controls, CMake, shared status,
  ledger or Git mutations, and no spawned workers. Root owns integration/publication.

## Source and implementation

Read the required standing/project/current documents, scanner graph/runtime
contracts and primary review. Extracted and read relevant atlas pp. 163–171,
including the printed fifteen-entry order, nominal speed, simplified overlap,
three depth maps, routing tablets and chorus return. This worker did not claim
a fresh full-PDF or new primary-paper visual review; those retained readings
belong to the dedicated source assignments.

Implemented all six semantic modes, checked mode/return/depth helpers, three
literal depth maps and the primary-corroborated sixteen-position traversal.
The rotor preserves signed ground-referenced voltages, reports both selected
terminal/tap indices and complementary weights, reads before advancing, and
retains one phase through mode and stopped-rate changes. Every rejected call
preserves state/destination; a saturated counter remains observable but cannot
advance. Static observation is separate from the advancing clock.

The linear unloaded overlap and `412/60 Hz` remain named nominal assumptions.
The source review's pi/8 phase shift and speed discrepancy are retained. No
measured loading, capacitance map, specimen speed, source voltage calibration,
audible-rate/filter policy or Engine integration is inferred.

## Frozen inputs

| Input | SHA-256 |
| --- | --- |
| `ScannerRotor.h` | `3ca846fc72224114194d73272f410fa2cbe3c0cae94c4fb23105536c7afb4d5a` |
| `ScannerRotor.cpp` | `f1dbd65a92036fef9957d280d2aafe9bd8579414ef632a6e2c525e370907b2a0` |
| Consumed `ScannerLine.h` | `c249f7c5556d6a6c8c58978928f0b860be442cb1188d35e49c59575729af00c7` |
| Frozen numerical contract | `3999a3a409d397401e135e8285704092bad130911468802370bf6da404d58ff9` |
| Unchanged 500-page atlas | `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769` |

## Executed producer evidence

Linux GCC 14.2.0, C++20, `-O3 -DNDEBUG`, all repository warning classes treated
as errors. The independent acceptance worker received the exact API, failure
precedence and source hashes before writing/finishing its tests.

| Producer check | Actual result |
| --- | --- |
| Strict standalone source compile | Passed. |
| All mode/position centers | 96 evaluations passed literal selected-tap expectations. |
| Quarter/half/three-quarter intervals | 288 evaluations passed; maximum blend error was zero for the binary-exact synthetic vector. |
| All fifteen rate labels | 150,000 frames processed, changing modes every frame; old-phase/read-before-advance and completed counts passed. |
| Phase diagnostic | Largest circular difference from a long-double elapsed-time calculation after up to 10,000 frames was `1.567634910770721e-13` turns. This is a finite producer diagnostic, not a universal long-run error bound. |
| Rejected calls with nonzero history | 46 cases passed state/destination preservation; each of the fifteen rate paths retained exact subsequent 31-frame continuation against an untouched clone. |
| Rate migration and wrap | Exact checkpoint preservation through stopped changes to 48 kHz; the interval immediately below phase one selected terminal 2 toward terminal 1, then wrapped correctly. |
| Counter limit | Last representable interval succeeded; the next rejected without state/destination changes. |
| Local object sizes | Rotor 40 bytes, selection 64 bytes, frame 80 bytes; ABI-specific. |

The smoke source/executable were temporary analysis inputs at
`/workspace/scratch/1742da7072be/a19_rotor_smoke.cpp` and `a19_rotor_smoke`.
The maintained independent acceptance suite belongs to assignment 20; this
producer smoke does not replace its frozen complete grid or allocation checks.

Actual source compile, from the repository root:

```sh
g++ -std=c++20 -O3 -DNDEBUG -Wall -Wextra -Wpedantic -Wconversion \
  -Wsign-conversion -Wshadow -Werror -I include -c src/ScannerRotor.cpp \
  -o /workspace/scratch/1742da7072be/a19-rotor.o
```

Fresh CMake integration commands used CMake 4.4.4, Ninja 1.13.2 and Python
3.12.14 from the session's build-tools environment:

```sh
cmake -S . -B /workspace/scratch/1742da7072be/a19-build -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build /workspace/scratch/1742da7072be/a19-build \
  --target hammond_core -j 3
```

The isolated core target build completed successfully. No full-repository
CTest, hosted platform, sanitizer, allocation or audible sideband qualification
is claimed by this assignment. Root's coherent integration owns broader results.

## Next step

Accept assignment 20's independently derived triangular-weight tests without
changing the frozen budgets. Compose this rotor with the physical-state line,
requiring equal completed counters on a combined checkpoint and preserving the
line's physical state on any failed frame. Avoid copying prepared matrices per
sample. Keep routing and future public control/state migration separate until
their exact behavior and G5 numerical policy have their own retained evidence.
