# A18 — independent workspace acceptance and preserved UI fixtures

Actual worker: `/root/w03_a18_workspace_acceptance`, assignment 18 of this
session's 60 distinct workers, wave 3. The integrator owns shared status,
publication and native integration. This worker did not stage, commit or push.

## Scope and findings

Reviewed `AGENTS.md`, the project plan/current continuation, the workspace and
geometry contracts, A13's model note and the integrator's projection note.
The inspected checkout HEAD was `5d81199a9822874b55f3b0a124715cbd6eadf0e5`;
implementation was present in the concurrent dirty worktree. Exact reviewed
source and executable SHA-256 values are in [the result](reports/a18-result.json).
HEAD alone does not identify this implementation.

No production model defect was found in this assignment. `UiModel.h/.cpp`,
Session, core, parameters, saved controls and CMake were not edited. The actual
fixture defects fixed were:

- The old 20-element control-kind arrays indexed appended kinds 20 and 21;
  they now contain 22 entries and explicitly expect three workspace controls
  plus one presentation control.
- Ordinary/focus counts, initial/wrapped Tab targets, preset offsets and header
  positions still described the old 64/67-control interface. They now describe
  68 ordinary controls, 71 Play stops, the Play first tab and the common header.
- Legacy key samples assumed a rectangular manual. Input samples now use the
  exposed quad interior. Geometry expectations independently evaluate the
  reviewed 0.94 homography in double precision, with a 0.001 logical-pixel
  comparison tolerance; unchanged body coordinates remain literal fixtures.
  All 147 playing identities, overlap precedence, shared natural boundaries,
  accidental half-open edges and 24 preset identities remain asserted.
- `pending_saved_and_recovery` focused an invisible bank-A drawbar while editing
  B. It now explicitly selects Edit A before focusing that drawbar. Its earlier
  acknowledgment, dirty/saved, load, transport overflow and recovery assertions
  remain intact.
- Complete rollback comparison now includes workspace/presentation, the body
  panel and all hit/top/front quads.

Owned implementation files are `test_standalone_ui.cpp`,
`test_standalone_preset_ui.cpp`, and the new
`test_standalone_workspace_acceptance.cpp` under `apps/standalone/tests/`.
The only native fixture change is the preset raster focus loop's bound from
68 to 71 in `apps/standalone/native_tests/test_standalone_preset_raster.cpp`.

## Independent behavioral coverage

The new fixture crosses Play/Rotary/Service, Dimensional/Flat and seven sizes:
960×700, 1280×900, 1672×941, and all four 1399/1400 by 819/820 combinations.
It independently checks the exact ten common controls and 71/10 traversal,
all retained hidden controls/keys, all malformed byte values in the new IDs,
outgoing focus memory through pointer/direct/F-key entry, preservation while
visiting tabs and Flat, and release-first modal/modifier/repeat suppression.

Real Session runs overlap keyboard, pointer and Space owners with independent
external owners on Upper C, Lower C and pedal 25. Workspace/presentation/resize
transitions retain pending desired controls and the earlier applied snapshot;
an older real acknowledgment cannot clear the later pending edit. Load works
from Service. Each original UI release remains paired under changed target,
octave, geometry and modal/modifier state, and external owners survive until
their own releases. Separate drawbar, pedal-mixture and expression cases prove
that closed drags cannot mutate another bank/control or become glissandi before
the original Up. A press begun in a hidden body also requires a fresh Down.

Executed counters: **42** layout/view/mode cases, **5,740** hidden semantic and
pointer rejections, **56** focus-memory returns, **2,041** invalid atomic
operations, **14** real-Session owner/pending runs, **63** closed parameter
gestures and **120** shortcut suppression cases.

## Verification and handoff

Reused `/workspace/scratch/601951e27dc3/build-a13-sdkfree`; no new build tree or
dependency copy was created. GCC 14.2.0 and the existing local CMake/CTest bundle
were used. The new target initially required explicit CMake regeneration of
the test glob; configuration and subsequent build succeeded. This was a setup
retry, not a failing project assertion.

Commands from the checkout root:

```sh
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/cmake -S . -B /workspace/scratch/601951e27dc3/build-a13-sdkfree -DCMAKE_BUILD_TYPE=Release -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_ENABLE_MIDI=OFF
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/cmake --build /workspace/scratch/601951e27dc3/build-a13-sdkfree --target test_standalone_ui test_standalone_preset_ui test_standalone_workspace_acceptance --parallel 3
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/ctest --test-dir /workspace/scratch/601951e27dc3/build-a13-sdkfree --output-on-failure --no-tests=error -R '^test_standalone_(ui|preset_ui|workspace_acceptance)$'
```

The focused gate passed **3/3**. The original UI fixture retains nine behavioral
scenarios and all 47 published parameter IDs. The preset fixture still reports
12 layouts, 549,388 independently classified hit points, 288 route transitions,
48 keyboard activations, 144 focus-only moves, 753 invalid identities and 288
exact single-command pointer acknowledgments. [Build](reports/a18-build.txt),
[CTest](reports/a18-ctest.txt), [focused output](reports/a18-focused-output.txt)
and [source/binary hashes](reports/a18-result.json) retain the observed evidence.

This worker did not execute native preset raster acceptance; the completed A17
renderer/integrator gate owns that separate result. A19 owns fuller independent numerical projection
acceptance. This assignment does not qualify native screenshots, modal routing
in SDL, audible/PCM equivalence, physical devices, native accessibility or
literal reference fidelity. The next gate is the coherent integrated native
build and its actual raster/replay/capture acceptance.
