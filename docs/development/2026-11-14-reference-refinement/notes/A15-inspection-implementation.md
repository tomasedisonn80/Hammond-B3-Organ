# A15 — Held-target inspection wording

Worker `/root/w03_a15_inspection_impl`, wave 3. Inspected base HEAD
`d2972a5744c63219f785e118055b7992656cf8b3` and the current shared worktree.
Owned only `apps/standalone/InspectionModel.cpp`,
`apps/standalone/tests/test_standalone_inspection_author.cpp`,
`apps/standalone/tests/test_standalone_inspection_acceptance.cpp`, and this note.
Concurrent layout, material, contract and session-record changes were preserved.
No commit, push, additional worker or capture was created by this assignment.

Read the standing instructions, current scope/checkpoint/manifest, complete
M0–M9 plan, current status/next steps, recovery handoff, atlas review and A11
inspection contract. Reviewed the copied inspection document, Session snapshot,
UiModel note actions and production MIDI decoder before changing source.

## Implemented behavior

The production change is one assignment in `held_count`, after its existing
unobserved early return and observed decimal count: one held target selects
`target`; every other count selects `targets`. All three row definitions retain
their original plural defaults. Availability, evidence, row IDs/order, bounded
text formatting, snapshot precedence and copying remain unchanged. This is a
presentation repair; it changes no state format, parameter, note ownership,
clock, routing or sound implementation.

Author coverage now independently exercises Upper, Lower and pedals at 0, 1,
2 and full capacity (61/61/25), checking the other divisions remain zero.
Singular fixtures use each array's final element. All sixteen combinations of
available/prepared/read-success/running flags now carry nonzero backing arrays
in every division: unavailable or unprepared values remain `Not observed`,
plural, NotObserved/Unknown; observed retained copies keep singular wording.
Fourteen invalid-control fixtures retain separately observed single targets,
with Available/Software evidence. Existing allocation and immutability checks
remain in the executed suite.

Independent acceptance uses synthetic MIDI packets through the production
`MidiInput` decoder and real `Session::post`/render/read publications, together
with actual `UiModel::key` actions. Upper, Lower and pedals each retain one
target with simultaneous UI/MIDI owners, through both release orders; only
the last release produces zero. Two distinct endpoints produce two targets,
then complete queued note inventories produce 61/61/25. All releases return
to zero without faults. Existing Cancel/selection and stopped-clearing checks
remain. The real publication-exhaustion read failure now retains singular
counts in all three divisions while desired controls remain pending.

## Executed verification

Working directory: `/workspace/scratch/1bb6ee17ad7e/Hammond-B3-Organ`.
Root released the shared build after A13; A15 returned it immediately after
this focused gate. Existing `../build-native` uses GCC 14.2.0, CMake 4.4.5,
Ninja and Release, with standalone ON, MIDI/VST3/sanitizers OFF.

```sh
../build-tools/cmake/data/bin/cmake --build ../build-native --target test_standalone_inspection_author test_standalone_inspection_acceptance --parallel 2
../build-tools/cmake/data/bin/ctest --test-dir ../build-native -R '^test_standalone_inspection_(author|acceptance)$' --output-on-failure --no-tests=error
git diff --check -- apps/standalone/InspectionModel.cpp apps/standalone/tests/test_standalone_inspection_author.cpp apps/standalone/tests/test_standalone_inspection_acceptance.cpp docs/development/2026-11-14-reference-refinement/notes/A15-inspection-implementation.md
```

Build exited 0; both rebuilt suites passed, **2/2 in 0.01 seconds**. Whitespace
verification exited 0. Reviewed source SHA-256 identities:

| File | SHA-256 |
| --- | --- |
| `InspectionModel.cpp` | `b0a288d045f66f809e65f3b8330f6e68feba247e964b1a543fb0023fc62a0fd8` |
| `test_standalone_inspection_author.cpp` | `a356cf8b5627fb7eaed2c7d8ee672bd42b8b34659183ee97aeaacc1ebaae5908` |
| `test_standalone_inspection_acceptance.cpp` | `b52b5f8fcc52d32994b945437fc7c760894588c82f37ef0a239224fb066902fd` |

Next: A18 implements the genuine pending/acknowledged native rendering harness
specified by A11; the integrator then rebuilds coherent inputs and reviews its
retained pixels. This string/ownership gate does not qualify native capture,
desktop interaction, physical MIDI/audio hardware or instrument fidelity.
