# A22 — Independent live-material and raster review

Actual worker `/root/w04_a22_material_independent`, wave 4. Owned only this
note and `reports/A22-*`. No source/test/CMake edit, GUI interaction, commit,
publication or child dispatch. Read the standing instructions, current scope,
checkpoint, complete M0–M9 plan, relevant source review, accepted layout/material
contracts, A14 implementation/failure record and the existing five native suites.
Root confirmed `InstrumentView`/`UiModel` were stable and released `build-native`
after A20; A21 used isolated compilation.

## Outcome and identity

The five existing native suites passed **5/5 in 22.07 seconds**. Their checked
material, key ownership, glyph and renderer-state paths remain sound. This is
partial acceptance: complete 1.25× projected-material coverage, short/wide
compact status, overlay Flat behavior and matched material timing remain open.

Observed HEAD/remote-tracking HEAD:
`e4968b2acd37b6f79683704356350070fe2fc329`; committed tree:
`1aff4305e347b46c659dcbc27eb524649a4c54c8`. Concurrent uncommitted work was
preserved; these identifiers do not describe the entire working tree.
Renderer SHA-256 is
`4127c0b2feb9b04f591fa9af82e4a6f3bbc162228205d7d92c8bdcca911ac45f`;
`UiModel.cpp` is
`49c68995aad96aa5e316613412c93931a1082d0e4a3ad3758ac63484af963064`.
All recorded renderer/test inputs stayed unchanged across the build and run.
[Exact identities](../reports/A22-native-identities.json) retain direct source,
binary and linked artifact hashes, commands, setup and before/after observations.

| Executed binary | SHA-256 |
|---|---|
| `test_standalone_drawing` | `d5825a9d3f65d09200a099990d0fb0fbbeabacf838fdce83a99b19963b97a8eb` |
| `test_standalone_quad_drawing` | `55ae6d4fd3ada6ad53d5a21fe3c8605c13b8cfb49d4fb93e26025a85a47ac65f` |
| `test_standalone_workspace_raster` | `bba1e99db4606620677913afa082544294f953a129fac2b9c71497e7060caa5b` |
| `test_standalone_scaled_view` | `a7bd9eb1bf8727c44642e0486437d5ff41a64170d01ff104a6019f75fc9cf9ee` |
| `test_standalone_preset_raster` | `b4ff2a7a794f57211bc50c45fe9d9fd4d5e46977a89240eb1a51696bcff2df54` |

## Actual visual observations

Directly opened the unchanged reference JPEG, every one of A18's six PNGs,
`desktop-refinement-startup.png`, and root's explicitly provisional
`/workspace/scratch/1bb6ee17ad7e/provisional-refinement.png`. File and decoded
RGBA hashes of all six A18 PNGs independently match their retained inventory.
The [review report](../reports/A22-material-review.json) names all nine image
identities and their distinct provenance. A18 frames are actual software
rendering-harness output without an application window/device. The 1280×900
startup frame has root's separate X11 application provenance; it is not a
retained desktop screenshot. The provisional 1672×941 image remains provisional.

At reference size, the deeper live natural fronts, dark accidental fronts and
fading rear recess create clearer depth. The small upper highlights remain
restrained. Main panels show low-amplitude texture without obscuring brass
headings, and the cabinet rim/status stop above the separate live pedals.
A18's held Upper C remains distinct; the pending Upper F outline and footer
clear after acknowledgment while the held key remains. The 960×700 Service
frames retain readable rows and summaries, including `1 target`; the pending
banner/footer and later fixed-F applied state are visually separate.

Visible differences remain: the concept has broader/sparser keys and controls,
softer local lighting, richer irregular surface texture, and a different
cabinet control area. The live application preserves its full musical
inventory, toolbar and truthful status instead. No literal 1:1 or physical
material/contrast claim follows from this comparison.

## Quantitative and source checks

| Existing suite | Observed checks; zero failures |
|---|---|
| Drawing | 144 glyph, 18 label, 12 metric cases; 298 surface checks over 18,309,120 pixels |
| Quad | 17 full-target coverage checks, including malformed/nonfinite/huge geometry and clipping |
| Workspace raster | 150 frames; 108 held, 108 held/focus, 108 front/Flat, 54 occlusion, 12 sloped-corner and 12 hidden-body checks |
| Scaled view | 168 frames/state checks; 90 clipped frames; 16 focus; 56 Service values/58 lines |
| Preset raster | 192 label/focus, 160 full-size accidental glyph, 752 isolation and 96 state cases, including both presentations at 1400×820 |

Workspace sampling reports minimum mean Rec.709-weighted **sRGB level**
top/front differences of **65.8713 natural** and **15.9033 accidental**. These
are native raster samples, not measured luminance or display accessibility.
The unchanged preset suite now preserves all glyph ink at the original failing
1400×820 lower-manual positions. A14's original 14 failures remain untouched in
`A14-first-native.log`, SHA-256
`9b0bfcd8a09e9a0504a208fb07abbb1e86f8bd81b7f4d8a1961c87886bc80692`.

Source inspection confirms finite/positive material guards, at most **2,048
grain pairs / 4,096 mark rectangles per panel**, deterministic local spacing,
disjoint light/dark marks and no new texture/cache/allocation in the material
loops. Light alpha 6–10 and dark alpha 10–18 yield conservative integer channel
bounds of 8 and 4 against the deck gradient. A separate read of the actual A18
acknowledged Play header patch `[440,22,600,100)` measured a maximum **3-level
RGB deviation from its same-row median** over 12,480 pixels (501 varied).
That is a local grain observation, not an old/new whole-image comparison.

All new key bands interpolate the original top/front quads. Existing native
checks find no sampled sloped-corner, held/focus, viewport or clip escape at
their tested scales. Main workspace Flat paths bypass new panel grain,
key fronts, wood, cap bevels and cabinet rim; its sampled key interiors are
uniform. Compact status offsets 31/49/67/85 with 14-pixel bounds end at 99,
inside the legacy 101-pixel card by source arithmetic.

## Concrete open gates and next worker handoff

1. **1.25× projected material:** Drawing tests include 1.25× rectangles/gradients,
   but quad and complete-view tests use 1/1.5/2×; scaled focus uses 1.5/2×.
   A26 should render public `paint_instrument` at 1.25× with bounded surfaces,
   using independent half-plane pixel ownership, sloped-corner, held/focus,
   front contrast, caller viewport/clip and renderer-state assertions. Do not
   derive expected ownership by calling production `contains()`/hit helpers.
2. **1920×700 compact status:** the existing workspace matrix stops at three
   ordinary sizes. A26 should probe the actual 101-pixel card, preserve visible
   final rotary text, inject long status strings, and reject ink beyond its
   allocated bands or over pedal keys. The 99-pixel budget above is source
   inspection, not a fresh raster pass.
3. **Flat overlays:** `midi_overlay()` and generic Audio/Help `overlay()` call
   `panel()`/`button()` without passing presentation. Their default `flat=false`
   path therefore inherits refined grain/bevels in a Flat workspace. The
   dimensional overlay behavior predates A14; it cannot support a complete
   current Flat-absence claim. Root assigned A26 an independent native probe,
   preservation of original evidence and narrow presentation propagation if
   reproduced. No production change was made by this reviewer.
4. **Timing/display:** retain the contract's same-geometry/backend 30 warmup
   plus 300 timed draws, median/p95, and investigation threshold. This CTest
   wall time is not that benchmark. A new accepted application gallery, actual
   high-DPI/display and native accessibility gates remain separate.

Root explicitly deferred the bounded new harness to A26, preserving A22's
reviewer role. No redundant broad suite was run.

## Reproduction

From `/workspace/scratch/1bb6ee17ad7e/Hammond-B3-Organ`, after exclusive shared
build release, used GCC 14.2.0 Release, SDL 2.32.10, MIDI OFF and VST3 OFF:

```sh
../build-tools/cmake/data/bin/cmake --build ../build-native --parallel 3 --target test_standalone_drawing test_standalone_quad_drawing test_standalone_workspace_raster test_standalone_scaled_view test_standalone_preset_raster
../build-tools/cmake/data/bin/ctest --test-dir ../build-native -R '^test_standalone_(drawing|quad_drawing|workspace_raster|scaled_view|preset_raster)$' --no-tests=error --output-on-failure -V -j 2
```

The build performed three needed relinks; all five tests used SDL software
surfaces without window/audio subsystems. Retained logs are
[build](../reports/A22-build.log) and [CTest](../reports/A22-ctest.log).
