# A21 — independent sidebar layout acceptance

Actual worker `/root/w04_a21_layout_independent`, wave 4. Owned only
`apps/standalone/tests/test_standalone_reference_layout.cpp`, this note and
`reports/A21-layout-independent.json`. No production changes, shared-build
mutation, commit, push or worker dispatch.

Reviewed AGENTS, current scope/checkpoint/manifest, full M0–M9 plan, current
status/handoff and atlas review, the frozen layout/geometry contracts, A13's
implementation note, UiModel and existing independent projection/preset tests.
HEAD was `e4968b2acd37b6f79683704356350070fe2fc329`, tree
`1aff4305e347b46c659dcbc27eb524649a4c54c8`; concurrent unfinished work remained
untouched. **No production defect found.**

## Independent coverage and result

The new executable passed **78 layouts**: the full 3×3 grid of immediately
adjacent binary32 values below/at/above 1400 and 820, plus four independently
frozen active anchors, each in two presentations and three workspaces. The
explicit breakpoint truth table checks both axes without integer rounding.
The anchor values come from the reviewed contract; art/status dimensions were
separately resolved with decimal arithmetic and exact 466:397 aspect, including
height-limited and width-limited cases.

Executed counts: **11,466 playing-key records**, **5,304 ordinary-control
records**, including **1,872 preset records**; **2,366 focus stops** across
complete, unique 71-stop Play and 10-stop hidden-workspace cycles; **144 empty
cabinet/pedal-gap hits**; **eight fixed old-location classifications**; and
**24 literal-anchor layouts**. Every layout retains 61+61+25 playing keys,
24 presets and 68 controls. Labels, values and tracks fit their control bounds;
all focus identities resolve to visible hit geometry. Tab emits no command and
preserves controls. Cabinet/pedals remain disjoint with a 10-pixel gap. Both
reference manuals independently reach **144.12 pixels** of key depth. The
minimum active art/status heights are 287.4/116 pixels.

## Baseline preservation

Compiled unchanged `d2972a5744c63219f785e118055b7992656cf8b3:apps/standalone/UiModel.cpp`
and current UiModel separately against the same current header and copied core
archive. The header diff is solely the added sidebar flag; no changed inline
geometry implementation is borrowed. The test's optional `--legacy-snapshot`
mode explicitly serializes every prior layout field, excluding padding and that
new flag, without deriving an expected layout from current formulas.

All **78 non-sidebar layouts** matched byte-for-byte: 13 windows × two
presentations × three workspaces, covering minimum/default, short-wide,
fractional and 8192 limits. This compares **467,064 scalar fields / 1,868,256
bytes**, SHA-256
`ee17282335c9e93ed4f5e3ccfd247cca649b59dfab95c41462d957930db1d0f9`.
This is a same-toolchain comparison, not a portable frozen-float hash gate.

## Setup and retained evidence

Repository cwd: `/workspace/scratch/1bb6ee17ad7e/Hammond-B3-Organ`.
Used GCC 14.2.0, C++20, `-O3 -DNDEBUG` and the project's warning/error flags.
A20 confirmed stable archives; isolated executables live in
`../a21-layout-independent`. Exact compile/run arguments, baseline/current
source and binary hashes, outputs and durations are in the compact JSON report.
All recorded source hashes were unchanged after execution; `git diff --check`
passed.

Fresh existing independent suites also passed: projection **288 layouts,
42,336 keys, 6,912 presets**; preset UI **621,920 classified hits, 288 route
transitions, 48 keyboard activations, 144 focus moves and 753 invalid IDs**.
All three executables exited zero. No shared CMake build was run.

Qualified SHA-256 identities:

```text
UiModel.cpp 49c68995aad96aa5e316613412c93931a1082d0e4a3ad3758ac63484af963064
UiModel.h d94e90be25812c6d21b61f37f2b0547704d14866c45fbbb21131ec70b6389bd3
test_standalone_reference_layout.cpp e053edf405d11470db92396fdeabed111aeb5debe38c16632884f21eac32bdbf
```

Next: root's coherent auto-glob build/CTest and separate native material,
label/focus raster, desktop ownership and gallery acceptance. These results
qualify model geometry; they do not establish rendered text readability,
reference-image equality, native accessibility or physical fidelity.
