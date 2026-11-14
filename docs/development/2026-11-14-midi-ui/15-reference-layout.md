# A15 — Shared reference-player geometry

Actual worker: `/root/w03_a15_reference_layout`; MIDI/UI wave 3, assignment 15.
Owned paths: `apps/standalone/UiModel.h`, `apps/standalone/UiModel.cpp`,
`apps/standalone/tests/test_standalone_ui.cpp`, and this note. No shared status,
renderer, native-main, CMake, public parameter or saved-state changes were made
by this worker. The parent's pre-existing `external_parameter` bridge and its
independent test were preserved unchanged.

## Result

Implemented `standalone-reference-player-layout-v1` from
[`REFERENCE_UI_DESIGN.md`](../../REFERENCE_UI_DESIGN.md). Performance is above
adjacent manual drawbar racks. The cabinet appears at width 1400; the five bank
controls for each manual move into its cheek at height 820. Below that height,
each bank-control row remains in its drawbar panel. The default stays 1280 × 900,
the minimum stays 960 × 700, and all 61 + 61 + 25 playing keys remain visible.

The five specified layout fields are present: `show_cabinet`,
`bank_controls_in_cheeks`, `cabinet_panel`, `cabinet_art`, and
`manual_rail_panels`. Hidden decorations are empty. All 46 controls, labels,
values, tracks, and playing keys remain in the shared paint/hit geometry.
`MidiSettings` is appended to both private enums and emits its app request;
the 45 public parameter identities and existing musical state paths are intact.

At the minimum strip height, each pedal mixture retains 24 units of vertical
track travel. Its numeric value sits beside its track, keeping labels, values
and raised caps apart. Bank-button heights are explicitly 24 in cheeks or 26
in racks; toolbar controls are 28. Tests check these new contractual heights
per kind rather than retaining the superseded blanket 32-unit expectation.

**Extreme-aspect correction agreed with the integrator:** cabinet art retains
the 466:397 aspect and its exact reference destination. When natural artwork
height would consume the service card, it shrinks and centers horizontally,
leaving 176 units below it. At 1920 × 700 and 8192 × 700 the artwork height is
320. At 1672 × 941 its destination is approximately
`{1153.6416, 154, 434.4624, 370.1321}`. This avoids overflow without changing
the reviewed reference composition.

## Executed checks

A separate copied source snapshot was configured and built to avoid mixing
concurrent live headers and older objects. Base checkout HEAD was
`7b36cfac2565397191b3df5e07112611e7f1b0e1`; the build includes the parent's
then-current MIDI work. Toolchain: GNU C++ 14.2.0, CMake 4.4.4, Python 3.12.14,
Release, strict project warnings, native/VST3/physical-MIDI options off.

```sh
cmake -S /workspace/scratch/cd4bd06ce68f/a15-layout-source \
  -B /workspace/scratch/cd4bd06ce68f/a15-layout-build \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_BUILD_VST3=OFF \
  -DHAMMOND_ENABLE_MIDI=OFF
cmake --build /workspace/scratch/cd4bd06ce68f/a15-layout-build \
  --target test_standalone_ui test_standalone_external_control -j 4
ctest --test-dir /workspace/scratch/cd4bd06ce68f/a15-layout-build \
  -R '^test_standalone_(ui|external_control)$' --output-on-failure --no-tests=error
```

The actual CMake/CTest executable directory was
`/home/agent/.cache/uv/archive-v0/kvsqq5-iHdbf13RC/cmake/data/bin`.
Both tests passed, **2/2 in 0.04 seconds**; UI acceptance reports eight scenarios.
The first compile identified a copied range-loop variable in the new test under
`-Werror=range-loop-construct`; changing it to a const reference resolved that
warning before the successful build. `git diff --check` passed for owned code.

Twelve independent literal-coordinate fixtures cover reference, default,
minimum, 1399/1400 × 819/820, 1920 × 700/1080, and both extreme dimensions.
They check every region, all 46 control identities, label/value/track
containment, nonoverlap, decorative non-targets, complete key spelling,
half-open boundaries, and accidental precedence. A new real-Session scenario
crosses seven sizes while overlapping UI and MIDI manual owners and an external
pedal remain held. It checks parameter-drag closure, preserved focus, bank,
octave, dirty/pending state and acknowledgment, then original-owner releases.
The prior musical, saved-control and recovery scenarios remain in place.

Frozen file SHA-256 identities:

| Input | SHA-256 |
|---|---|
| `UiModel.h` | `fac0dd9bfa1baf77d1efda2fbb8839c5a223d9ab0c3580c10dda184317f7da3c` |
| `UiModel.cpp` | `ac1a381367cfee7cce61e27ebd0b094c76a730806383e9ead609622687993e28` |
| `test_standalone_ui.cpp` | `2289bfa944e7e5a186f20b32f736dcc886299e4464c80ab4af1e577726a5103e` |
| Unchanged external-control test | `d79ac2b836f8bc431ee9a5ab8f6814ad639aef704e496417dd8dd80ab2e33c1b` |
| Compiled nominal profile | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |

The 1086-file frozen source inventory SHA-256 is
`03d19aa721f456c77480df6ed91120c5ca149cbd7ea1feb38c8eedb1d7970768`:
sorted relative paths, each followed by NUL, file SHA-256 and newline; Python
bytecode caches excluded. The three owned code files and unchanged external
test matched their tested copies on final audit.

## Handoff boundary

The parent owns renderer/main integration, native captures and the combined
source gate. These headless checks establish shared geometry and model behavior;
they do not establish actual glyph fit, native input, physical MIDI operation,
accessibility, measured sound fidelity or pixel-identical reference matching.
Next: rebuild the native consumers coherently, compare actual 1672 × 941,
1280 × 900 and 960 × 700 captures, and retain remaining visual differences.
