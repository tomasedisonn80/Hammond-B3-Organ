# A17 — native workspace and dimensional renderer

Actual worker: `/root/w03_a17_native_renderer`, assignment 17 of this session's
60 distinct workers. Owned `apps/standalone/InstrumentView.h/.cpp` and this
note. Root owns integration, CMake, the shared handoffs, publication and the
final source freeze. No commit, staging, push, sound/core/state change or
historical gallery replacement was performed here.

## Implemented slice

Read `AGENTS.md`, the continuation scope, all three accepted interface contracts,
the current checkpoint and relevant plan/source. Inspected the unchanged
1672×941 atlas source and the parent's actual baseline capture before painting.
Starting published HEAD was `5d81199a9822874b55f3b0a124715cbd6eadf0e5`, tree
`52b4ec72b77e4442efe2e9e1b089b7b0ea6e638b`; the implementation is a concurrent
working-tree overlay, not that published commit alone.

- The shared header now paints Play/Rotary/Service tabs on the left, two rows of
  Save/Load/Help and Audio/MIDI/Panic on the right, the centered title, nominal
  caption and selected Flat toggle. Every ordinary control and playing-key
  painter admits its semantic ID through `ui_control_visible`. Hidden Play
  bodies and preset focus ink are absent from Rotary and Service.
- All 147 playing keys use their shared `hit`, `top` and `front` quads. Ivory
  gradients, darker fronts, accidental bevels, held highlights and focus follow
  those shapes. Focus first interpolates the original sides at the inset y
  positions; it never paints the old AABB. All 24 presets retain their qualified
  rectangular selection, pending-request and label-preserving focus paths.
- Flat retains the complete control inventory and uses plain panel, button,
  drawbar, preset and rectangular key surfaces. It removes ornamental wood
  grain, projected playing keys, key fronts and heavy control shadows. The
  optional cabinet decoration remains explicitly documentary.
- Added exactly the agreed `const InspectionDocument* inspection{nullptr}`
  field and forward declaration. A16 supplies this immutable copied document.
  The renderer neither reads Session/Engine nor opens devices. Service paints
  all six cards and 28 Service rows; Rotary paints the six read-only rows and
  the retained cabinet crop. The status banner distinguishes Current,
  Retained, Stopped, Unprepared and Unavailable, shows pending desired controls,
  and omits unobserved frame/revision numbers. Availability and evidence have
  separate labels and a visible legend. Unknown physical values remain words
  with units, with no substitute zeros, fake speed controls or rotor animation.
- Service uses three columns and two rows at ordinary sizes, including 960×700;
  a tall narrow body uses two columns and three rows. Rotary explicitly says
  cabinet audio is disconnected and no specimen captures qualify fidelity.
  Help documents F4–F7; the footer names focused musical controls and keys.

The source decorative crops are unchanged. The new reference-size capture has
real sloping ivory planes and front thickness compared with the rectangular
baseline. Cabinet placement, rack/manual heights, the correct full key/preset/
pedal inventory, real legends and the additional tools still differ from the
concept. This is substantive material/geometry progress, not literal 1:1 or
physical fidelity acceptance.

## Executed checks and retained captures

Reused the coordinated `build-native` Release build with GCC strict warnings,
pinned SDL 2.32.10 and its software renderer. A first compilation caught one
local `-Wshadow` tick variable; renaming it fixed the error. The following
build and focused raster gate then passed:

```sh
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/cmake --build /workspace/scratch/601951e27dc3/build-native --target hammond_standalone test_standalone_preset_raster --parallel 3
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/ctest --test-dir /workspace/scratch/601951e27dc3/build-native --output-on-failure --no-tests=error -R '^test_standalone_preset_raster$'
git diff --check -- apps/standalone/InstrumentView.h apps/standalone/InstrumentView.cpp
```

Raster CTest **1/1 passed**, 10.96 seconds. It preserves all 24 preset labels and
focus indicators, accidental/other-manual isolation, applied versus pending
selection, Cancel and rejection behavior at 960×700, 1280×900, 1672×941 and
1400×820. No assertions were weakened or raster test files edited.

Five native 1,200 ms dummy-driver smokes passed, including held-note observation
and the later release. Each ran the same executable with a distinct initially
absent `--state` path, `--screenshot` BMP and `--diagnostics` JSON in
`/workspace/scratch/601951e27dc3/a17-renderer/`, using
`SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy`. Flags were:

| Capture stem | Size | Startup options | Observed result |
|---|---|---|---|
| `play-min` | 960×700 | `--workspace play` | Pass; full inventory visible |
| `play-reference` | 1672×941 | `--workspace play` | Pass; live projected manuals and cabinet |
| `service-min` | 960×700 | `--workspace service` | Pass; all six cards and final rows visible |
| `rotary-min` | 960×700 | `--workspace rotary` | Pass; all six facts and limitation visible |
| `flat-min` | 960×700 | `--workspace play --flat` | Pass; full planar controls and held indication |

Converted the actual BMP captures to PNG without changing their pixels and
visually inspected all five. In minimum Service, the bank-memory value wraps
once; the final contact family and percussion values remain above each card's
summary. Root independently inspected reference Play, minimum Service and Flat
and confirmed these observations. PNG and schema-3 diagnostics remain in the
scratch capture directory for the integrating gallery author; no historical
capture was overwritten.

| PNG | SHA-256 |
|---|---|
| `play-min.png` | `6ecf04eedbd6dd03a3696933123e9b97334046af1835a284a12f52bc875e5353` |
| `play-reference.png` | `484bf0d81f5f50225a34fe29df9840a466671e2e20c0eb43f2e06fc0c0739348` |
| `service-min.png` | `83ab56fbd51674859496f575e54e4e32cbc53e341723a4705f51cb685e70e530` |
| `rotary-min.png` | `cb366121145f0374603a6ea9e8867f2c60bbf8963f449a81352b9460be1e34c8` |
| `flat-min.png` | `e1ba73001ba3eff7a172b133fee154e9bf6168da6573384ebee322e8737a3573` |

## Exact source and binary identities

Hashes identify the released A17 renderer checkpoint before subsequent A20
polish. Root was informed that both owned source files and the native build were
released; its integrated application/MIDI gates run separately against the
listed executable and are not claimed as this worker's results.

| File | SHA-256 |
|---|---|
| `InstrumentView.h` | `416b9b6679901326cdf30370a37f3c2c13d720f6fc24fa904d182fe12ddb7932` |
| `InstrumentView.cpp` | `1fccdc4ef3943be029e320571faad42b21cb053eb8e9ee205ce63808a51b7831` |
| Shared `UiModel.h` | `1c51aaa46ee12be91ae8729fa739d7f4d102dc030bae61dbf15fd0cc1692a98d` |
| Shared `UiModel.cpp` | `c536c460c6157197bc98c12c1d9d865584c043c44d1c7d3ca6d3d539f74dc0c3` |
| Shared `Drawing.h` | `749e718436e61ad4a13a28e167c4b07e4dd789adf213a6229a503fc1f2bcf188` |
| Shared `Drawing.cpp` | `84b91089fa6938075e8b0cfde39d66266acc9c3e7ea026958deb9eaf6a9b16fe` |
| Shared `InspectionModel.h` | `d16fe12811c399fd9edc03286ec00767e086268447e03f40fa9d9cdf9badddb9` |
| Shared `InspectionModel.cpp` | `59df4b36e7b565a6f07f2efee63634953b55112b24927292d2f884ddddda8645` |
| `hammond_standalone` | `ca095152e8e94b4b1a51fa26f0e1fca346cbb2a7acfd7ec48b0a5839d83151fd` |
| `test_standalone_preset_raster` | `6a0ad2de173a09bf66d6b1f2818788ae1893c43d50fd294955a6964843027416` |
| Atlas reference JPEG | `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187` |
| Parent baseline PNG | `09703903629120dfe77f3a12b6d86c8d3ca118759a304a0fa7b98b5234f2a3ce` |

## Remaining qualification

The five smokes observed Current inspection snapshots, not forced native
Retained/Stopped/Unprepared/Unavailable branches. Their distinct renderer
captions are implemented; independent inspection/raster acceptance still owns
those states, malformed-data cases and the complete resize/focus matrix.
Minimum inspector text is deliberately compact (10–10.5 logical pixels for
metadata/values); later A20 visual acceptance can improve hierarchy and wrapping
without removing required values or changing shared hit geometry. No claim is
made for native accessibility, physical audio/MIDI devices, callback deadlines,
all extreme-size raster combinations, connected scanner/Leslie audio, measured
hardware behavior or exact concept-image equality.
