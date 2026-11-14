# A13 — workspace model and held-input continuity

Actual worker: `/root/w03_a13_workspace_model`, wave 3, assignment 13 of this
session's 60 distinct workers. Integrator owns publication and shared handoffs.

## Source and owned changes

Implemented against the reviewed workspace and geometry contracts, with checkout
HEAD `c83fe2336be931385f0d7ab82c55b30bfdfc8fc6`. This is a concurrent dirty source
tree; that commit alone does not identify the new implementation. Owned files:

- `apps/standalone/UiModel.h`
- `apps/standalone/UiModel.cpp`
- `apps/standalone/tests/test_standalone_workspaces_author.cpp`
- This note.

The model now retains all 68 control records and 147 playing keys in each
workspace. The ten common controls are Play/Rotary/Service, Save/Load/Help,
Audio/MIDI/Panic, and Flat, in that order. Play has 71 Tab stops; Rotary and
Service have ten. Hidden controls cannot receive pointer, direct activation or
keyboard navigation. The two legacy non-painted compatibility actions remain
directly usable only in Play. An inactive manual drawbar bank is also hidden;
programmatic callers must select its EditBank before focusing its drawbar.

Workspace/presentation setters validate before committing a complete layout,
return true without side effects for the current valid selection, and preserve
state on failure. Workspace changes restore semantic per-view focus memories;
visiting or clicking workspace tabs does not replace the outgoing remembered
body/tool target. Presentation changes through setters, F7, direct activation
and pointer activation preserve the prior focus and all workspace memories.
Resize also preserves focus and memories. A Tab-focused Flat button remains
focused when activated, while a pointer click from a body focus preserves the
body focus.

F4/F5/F6 select Play/Rotary/Service, and F7 toggles Dimensional/Flat. Existing
F1–F3, octave keys and physical computer-piano keys remain available in every
view. Releases still use their original owner/target before shortcut, modal or
modifier gates. View changes emit no actions and preserve musical controls,
pending/dirty state and held notes. A real view/presentation change or successful
resize closes a parameter drag and suppresses further Move input until the
original Up/CaptureLost, while preserving existing note ownership and capture.
An input begun on a hidden body cannot become a gesture after returning to Play.

Header geometry reserves the left group for three tabs and the right group for
two rows of three tools. Flat sits below the center title allowance. The new
`workspace_panel` spans the content body between header and footer.

`UiQuad::contains` is inline, finite-checked, and half-open, using double
intermediates for finite float endpoint interpolation. Playing keys now expose
`hit`, `top`, and `front`; hit testing consumes `hit`. **At this assignment's
boundary those quads intentionally remain rectangular, with `top == hit` and
empty `front`.** A19 owns the accepted homography implementation, and the
renderer/drawing agents own its appearance. No perspective or 1:1 visual claim
is made by this model assignment.

## Executed checks

GCC 14.2.0; CMake and CTest from the existing local tool bundle; Python 3.12.14.
The shared native build was not touched. A separate SDK-free Release build
occupied 6.7 MiB at completion, without cloning source or dependencies.

From the repository root:

```sh
g++ -std=c++20 -Wall -Wextra -Wpedantic -Werror -Iinclude -Iapps/standalone -fsyntax-only apps/standalone/UiModel.cpp
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/cmake -S . -B /workspace/scratch/601951e27dc3/build-a13-sdkfree -DCMAKE_BUILD_TYPE=Release -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_ENABLE_MIDI=OFF
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/cmake --build /workspace/scratch/601951e27dc3/build-a13-sdkfree --target test_standalone_workspaces_author --parallel 3
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/ctest --test-dir /workspace/scratch/601951e27dc3/build-a13-sdkfree --output-on-failure --no-tests=error -R '^test_standalone_workspaces_author$'
git diff --check -- apps/standalone/UiModel.h apps/standalone/UiModel.cpp apps/standalone/tests/test_standalone_workspaces_author.cpp
```

Results: strict syntax and diff checks passed; focused CTest **1/1 passed**, six
behavioral scenarios covering inventory/admission, focus traversal/memory,
hidden-body/global-key behavior, pointer/Space release ownership, closed-drag
suppression/idempotence and shared quad boundaries. The first syntax check found
one nested aggregate-initialization error, corrected before the passing build.

Reviewed file SHA-256 values:

| File | SHA-256 |
|---|---|
| UiModel.h | `1c51aaa46ee12be91ae8729fa739d7f4d102dc030bae61dbf15fd0cc1692a98d` |
| UiModel.cpp | `d623a20afcc2d56cca1f049618bee607d7dad6cf99bead45dd7a1d71d702d153` |
| test_standalone_workspaces_author.cpp | `b8c8fa0a491ad94815770976269b10ba66f98b18fb5a02f0c89344ea0ba723d2` |

## Next integration gates

A14/A19 can consume the shared quad type without another header edit. A18 must
adapt old inventory/header expectations and select EditBank A in the
`pending_saved_and_recovery` fixture before focusing its bank-A drawbar; retain
the pending-ack regression itself. Native mapping/replay, workspace rendering,
inspection, independent PCM/ownership acceptance, complete coherent-source
tests, actual screenshots and publication remain integrator-owned later gates.
This focused author test is not a native, platform, audible continuity, physical
calibration or visual-fidelity qualification. No commit or push was performed
by this worker.
