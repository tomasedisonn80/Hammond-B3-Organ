# Assignment 17 — independent standalone UI acceptance

Actual assignment: `/root/w03_a17_ui_acceptance`, wave 3, second batch of the
independent sixty-assignment standalone session. Owned only
`apps/standalone/tests/test_standalone_ui.cpp`,
`docs/STANDALONE_UI_ACCEPTANCE.md`, and this report. No production edits.

Read the repository instructions, current standalone/session/UI contracts,
actual headers/implementation, retained product review, and relevant parameter
chapter evidence. The existing 45-control registry is authoritative; the
atlas's larger proposed registry is not adopted. Integrator owns shared status,
manifest updates, coherent integration and publication.

## Result

- Added the maintained `test_standalone_ui` target source, discovered by the
  standalone CMake test glob with both optional native adapters disabled.
- Seven focused public-API scenarios cover complete literal parameter and
  pitch inventories, retained banks, physical original-note ownership,
  repeats/text/modifiers, pointer capture/glissando, Space audition, scoped
  focus release/Panic, captured drags, saved/pending state, real queue overflow
  and real InvalidCommand cleanup, geometry and keyboard/app navigation.
- Real Session/Engine zero-frame boundaries verify held ownership, Cancel,
  other-channel preservation, recovery and command acknowledgments. There is
  no substitute model or mocked Engine. Test inventories do not reuse the
  implementation's accidental or playing-key table, or its ID formula.
- Fresh Release configure/build and focused CTest passed **1/1**, seven
  scenarios, **0.01 seconds**. Strict production/test compiler warnings passed.
  `git diff --check` passed. No production defect was found in this scope.
- An initial complete pass also succeeded; the final pass follows test-only
  refinements for reverse pedal glissando, actual held-state Cancel, and a
  repeated real rejection. No acceptance threshold or production law changed.

## Exact execution and source identity

Working directory: `/workspace/scratch/5ba97739b54c/Hammond-B3-Organ`.
Observed HEAD: `96a37a977ef22b7adf38e1a841f57ffcf32519a7`; production sources
from the coordinated wave 3 live worktree were compiled fresh in their entirety.
Toolchain: Debian GCC 14.2.0-19, CMake 4.4.4, Python 3.12.14, C++20 Release.
Actual CMake/CTest directory:
`/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin`.

```sh
cmake -S . -B ../build-ui-tests -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_BUILD_VST3=OFF
cmake --build ../build-ui-tests --target test_standalone_ui --parallel 3
ctest --test-dir ../build-ui-tests -R '^test_standalone_ui$' -C Release --output-on-failure --no-tests=error
```

SHA-256 identities at the final build/run:

| Input | SHA-256 |
| --- | --- |
| `UiModel.cpp` | `c42aee8edcd3663f5925581cd738997bf83438a2fdcc13072b8a40f5407997c1` |
| `UiModel.h` | `55affdc2df63918909c6412763abc26dd15a57601263faca97c8007d8def9f93` |
| `Session.cpp` | `247c6a63dc9bb6c4e60398b17779a2d985058563b8d981c5e06426eab977f6ae` |
| `Session.h` | `0eed6c82d0cf5ffbeb0206f6f9702a93ef5a75cde6fd669b2862705dc7af84a0` |
| Acceptance source | `8ccc0718ed9a2202d8bfc8678409e73d38777fc8a8b15ddabdf8a4b86b468efc` |
| Compiled nominal profile | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |

## Limits and next handoff

This focused live-tree pass does not establish a frozen all-suite result,
SDL/application event dispatch, native accessibility, physical-device latency,
platform distribution or physical fidelity. Those remain separate assigned
gates. Root should integrate these three files, rerun the target from its
coherent source checkpoint, and retain actual device/render/accessibility
evidence independently. No commit or publication was made by this worker.
