# A13 — sidebar layout implementation

Actual worker `/root/w03_a13_layout_impl`, wave 3. Read current AGENTS, scope,
checkpoint/manifest, full M0–M9 plan, atlas review and approved layout/workspace/
geometry contracts. Started over `8bd999efc13e309b932e6ac41d72ceb7b9b80a5f`;
root published documentation checkpoint `d2972a5744c63219f785e118055b7992656cf8b3`
during implementation. Product changes were still uncommitted at verification.

Owned `apps/standalone/UiModel.h`, `UiModel.cpp`,
`tests/test_standalone_ui.cpp`, `tests/test_standalone_preset_ui.cpp` and this
note. Root additionally authorized exactly three wide landmark literals in
`tests/test_standalone_projection.cpp`; its independent rational oracle and
minimum/default expectations are unchanged. No commit, push or worker dispatch.

## Implemented behavior

Added `UiLayout::sidebar_pedals`, true exactly at width ≥1400 and height ≥820.
`show_cabinet` retains its width-only meaning. The active branch implements
the approved 31.1% cabinet column, 100-pixel header, extra six rack pixels,
fixed footer, deeper manuals and disjoint sidebar pedals. Both presentations
and all workspaces share this allocation. Other branches retain their original
arithmetic and literals, including short/wide windows. Cabinet art preserves
466:397, begins 48 pixels below the panel top and reserves 191 pixels below.
A14 received the field/API and exact art/pedal rectangles before renderer work.

At 1672×941 the manual panels are y520.76/704.88, height174.12, yielding
144.12-pixel key depth. Cabinet x1124.831312 and pedal y773.72/height105.28
match the reviewed contract. The 1400×820 minimum gives art height287.4 and
status height116. Controls, projection, hit/focus logic, note owners, Session,
47 parameters, state4/readers1–3 and audio behavior were not changed.

Updated only affected wide expectations, adding four independently calculated
fractional cases around both breakpoint axes and Flat checks across all sixteen
literal layouts. Decimal arithmetic gives the new reference key-space
x246.3362968, width860.4950152, y542.76 and depth144.12. The three authorized
projection literals therefore change:

| Landmark | Previous | New |
|---|---|---|
| Upper first back-left | 275.1013528,526.76 | 272.151147256,542.76 |
| Upper first front-left | 248.85784,635.24 | 246.3362968,686.88 |
| Upper last front-right | 1123.6416,635.24 | 1106.831312,686.88 |

The back-left uses `x + .03*width`; the front points use x and x+width at
y+depth. Existing native replay Flat points y88 remain within new y86–110
bounds and were left unchanged.

## Executed verification

Working directory: `/workspace/scratch/1bb6ee17ad7e/Hammond-B3-Organ`.
Root granted exclusive targeted-build access to existing `../build-native`;
Release, GCC14.2.0, CMake4.4.5 and Ninja1.13.2.git.kitware.jobserver-pipe-1.

```sh
../build-tools/cmake/data/bin/cmake --build ../build-native --parallel 2 --target test_standalone_ui test_standalone_preset_ui test_standalone_projection test_standalone_workspaces_author test_standalone_workspace_acceptance test_standalone_workspace_continuity
../build-tools/cmake/data/bin/ctest --test-dir ../build-native --output-on-failure --no-tests=error -R '^test_standalone_(ui|preset_ui|projection|workspaces_author|workspace_acceptance|workspace_continuity)$'
git diff --check
```

Build succeeded; **6/6 suites passed in 4.38 seconds**, no failures. Presets:
621,920 classified hits and 288 route transitions. Projection: 288 layouts,
42,336 playing-key and 6,912 preset records. Workspace acceptance: 5,740
hidden-input rejections; continuity: 719,289 exactly matched PCM frames,
1,662 presentation transitions and zero view commands. Diff check passed.
Shared build access was released immediately afterward.

Verified source SHA-256:

```text
UiModel.h d94e90be25812c6d21b61f37f2b0547704d14866c45fbbb21131ec70b6389bd3
UiModel.cpp 49c68995aad96aa5e316613412c93931a1082d0e4a3ad3758ac63484af963064
test_standalone_ui.cpp 785e5670da4786b7250c62c7ae7a5ad1a12bc2492f4d2b7476f3e6371c630bd9
test_standalone_preset_ui.cpp bb9e0d2879581eb630b9c703c5c308de216384e62bd17d8520c0f47152b28943
test_standalone_projection.cpp 2a103add377be40669a2fe150355a405325969f8c5d4345d49ecbe0d37541278
```

Next: independent layout review, coherent native renderer/replay tests and
actual minimum/default/reference/Flat captures. This assignment establishes
model engineering acceptance, not visual equality, real-device qualification
or physical fidelity.
