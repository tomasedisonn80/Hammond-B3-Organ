# A20 — bounded material and caption refinement

Actual worker `/root/w04_a20_material_refinement`, assignment 20 of this
session's 60. Owned `apps/standalone/InstrumentView.cpp` and this note/report.
The integrator owns shared geometry, integration, documentation, gallery and
publication. No staging, commit, sound/state/core change or asset edit occurred.

## Observed defects and changes

Read `AGENTS.md`, the three reviewed interface contracts, the current scope and
A17's renderer handoff. Visually inspected the unchanged atlas reference and
all five actual A17 captures before editing. The A17 design already preserves
the full instrument inventory and visible Service rows. Three bounded changes
addressed visible defects without changing any control region:

1. Tablet edges had a bright double frame which competed with their labels.
   Reduced the metal-frame contrast and added a shallow transparent highlight
   over the existing cap face. Button positions, states and label meaning stay
   live and unchanged.
2. Drawbar caps and narrow black playing keys lacked distinct side planes.
   Added light/dark cap edges and a restrained inner black-key face. Key bevels
   interpolate within the existing projected top quad; the exact hit geometry,
   front faces, held markings and inside-quad focus are unchanged.
3. Manual/pedal captions were fine 9.5-pixel serif text at the minimum size.
   They now use 10.5-pixel Sans. Percussion captions and eligibility rise to 10
   pixels; edit/sounding captions use 10.5 pixels and measure their actual font
   size before deciding on the existing compact wording.

Flat receives the clearer captions but no new ornamental treatment. The 24
preset key painters, labels and label-preserving focus code were not edited.
Service/Rotary row layout and copied-state semantics were not edited. All 28
Service rows, including the wrapped bank-memory row and final percussion row,
remain visible at 960×700; V, rpm and m units are not clipped. Availability and
evidence remain independently labeled. Inspection showed no further necessary
change to those cards in this bounded stage.

## Executed verification

Root released `build-native` after completing its A17 executable gate. Only then
rebuilt the application using the existing pinned SDL 2.32.10/GCC Release build:

```sh
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/cmake --build /workspace/scratch/601951e27dc3/build-native --target hammond_standalone --parallel 3
git diff --check -- apps/standalone/InstrumentView.cpp
```

Both passed. Five new actual 1,200 ms native smokes passed with the SDL dummy
video/audio drivers and software renderer. Each used a distinct initially absent
state path. Every diagnostic recorded a held screenshot, successful capture,
zero render/format/overrange/nonfinite audio failures, and no held notes after
shutdown. These are native software observations, not physical-device tests.

| Capture | Size | Mode | PNG SHA-256 |
|---|---|---|---|
| `play-reference.png` | 1672×941 | Play dimensional | `a2978ed218068fadd49e4deaed2b523dc41608ba2283b322a97528af2f39db2c` |
| `play-min.png` | 960×700 | Play dimensional | `f690fc29090a19f1023bb16e8e393cb4c170d2b825f6168e0f9dae5fff62c1ca` |
| `flat-min.png` | 960×700 | Play Flat | `21285b0473117ea322609a0ef7c4410d89d1139ee87f7fc0917a30566b8fafb0` |
| `service-min.png` | 960×700 | Service | `7c919d2acff08e8255c3e772aa3c9fe27a14d1327e220238e215cc21f60fecaa` |
| `rotary-min.png` | 960×700 | Rotary | `994b8911d8d3fd682d7e0465391316ce29fecaeceea2188db6d02c1c0ff2a23f` |

All five PNGs were visually inspected after the changes. Captures, schema-3
diagnostics, exact command arrays and logs are in
`/workspace/scratch/601951e27dc3/a20-renderer/`. BMPs were losslessly converted
to PNG and removed; the prior A17 captures were preserved. The preset raster
gate was not rerun because no preset paint/focus behavior changed; the
integrator's coherent acceptance follows separately.

## Source identity and handoff

The [compact report](reports/a20-material-refinement.json) records every source,
binary, capture and diagnostic identity and the actual screenshot-time view.
This is a worktree overlay, not a qualification of the published HEAD alone.

- `InstrumentView.cpp`: `5f5f209dbe33cb92e3c1d237258ba123d0a86e78c694d50c0634db8549d54407`
- `hammond_standalone`: `005db1e2006bd1929e07dff3acaa40a5a6e6fa60a2bc8f07eb992d972b04b364`
- Earlier A17 renderer identity: `1fccdc4ef3943be029e320571faad42b21cb053eb8e9ee205ce63808a51b7831`

No separate original A17 source-byte copy was retained before these changes;
its dated evidence remains bound to the A17 recorded hash. The final gallery
should qualify this new exact source. Renderer and native build are released
to the integrator after this note.

Literal 1:1 reference fidelity remains open: row heights, cabinet placement,
full 61+61-key inventory, 24 presets, 25 pedals and honest additional controls
still differ from the concept. This edit improves visible materials and
readability without changing that structural limit. The captures observe
Current snapshots; forced Retained/Stopped/Unprepared/Unavailable raster cases,
complete focus/resize acceptance, physical devices, native accessibility and
callback deadlines remain separate gates. Next work is the integrator's coherent
native gate and later independent reference/raster review using these captures.
