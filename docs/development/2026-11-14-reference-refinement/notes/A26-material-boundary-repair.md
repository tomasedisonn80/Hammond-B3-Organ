# A26 — Independent material boundaries and Flat overlay repair

Actual worker `/root/w05_a26_material_boundary_repair`, wave 5. Read standing
instructions, current scope/checkpoint/manifest, full M0–M9 plan, relevant atlas
review, accepted layout/material contracts and complete A22 note/report. Owned
the new native test, the narrow `InstrumentView.cpp` repair, this note and
`reports/A26-*`. Root owns CMake. No GUI, child dispatch, commit or publication.

## Result and concrete defect

The new `test_standalone_material_acceptance` passes **901 checks / 56 frames**;
filtered CTest passes **1/1 in 4.00 seconds**. Its unchanged final assertions
first reported **36 Flat overlay material failures** against renderer
`4127c0b2feb9b04f591fa9af82e4a6f3bbc162228205d7d92c8bdcca911ac45f`.
Audio, MIDI and Help all inherited dimensional panel/button defaults.

The sole production change forwards `layout.presentation == Flat` to those
existing panel/button calls. Existing selection, warning, face and ivory
arguments retain their default meanings. No labels, modal hit rectangles,
owners, layout, parameters, state or audio source changed. The six dimensional
overlay full-frame FNV-1a fingerprints at 1×/1.25× remain unchanged. These are
comparison fingerprints, not cryptographic capture identities.

## Independent acceptance

All frames call public `paint_instrument` on bounded SDL software surfaces,
without window/audio subsystems. Key ownership uses long-double half-plane
cross products on public vertices, natural-first/accidental-last precedence,
and inverse output transforms; it never calls production contains/hit helpers.

| Gate | Executed result |
|---|---|
| 1.25× projected materials | 960×700 translated viewport and 1400×820 cropped/translated caller clip; both presentations; all **588 held-key cases**, **24 held/focus cases**, **72 front/Flat samples**, and **8 sloped corners** pass. |
| Clip and renderer state | **56** scale/physical-and-logical viewport/clip/blend preservation checks; **6,543,712 aggregate outside pixels** retain the declared clear color. Four additional clips cut a focused accidental, including clips supplied in logical units. |
| Front contrast | Minimum paired mean weighted sRGB differences **63.8004 natural / 14.6426 accidental**; no physical-luminance claim. |
| Compact status | Actual **101-pixel** card at 1920×700 in both presentations; four frames, offsets **31/49/67/85**, 14-pixel budgets, all rows visible. Final rotary text matches the independently requested literal font raster; **2,048 aggregate final-row ink pixels** remain inside. |
| Long strings | Injected 2,048-character strings plus maximal integer configuration fields change only their allocated compact rows/footer; zero pedal changes or status ink below the card. These are display fixtures, not valid device configurations. |
| Flat modals | All three panels and all fifteen buttons at 1×/1.25×; **16,873 panel / 3,514 button sampled pixels** exactly match uniform Flat palettes. Six dimensional control frames retain material variation. |

## Preserved failures and exact identities

The initial test compile rejected four ambiguous aggregate overloads; explicit
test-only `UiRect` types resolved them. The first raster run had 40 failures:
36 product failures plus four test false positives. Diagnostic output identified
a fractional SDL rectangle's exposed rightmost panel column, not escaped text.
Excluding one background edge pixel retained all complete content-band,
below-card and full-frame long-string delta assertions. Both original logs,
the diagnostic run and the subsequent 36-failure pre-repair run remain retained.

Observed HEAD is `e4968b2acd37b6f79683704356350070fe2fc329`, tree
`1aff4305e347b46c659dcbc27eb524649a4c54c8`; concurrent uncommitted work is separate.

| Final input/output | SHA-256 |
|---|---|
| `InstrumentView.cpp` | `428f74c4b2aae72e1ee048d1fa878575d0cd2edc064b1a3865ba40c446c30da2` |
| New test source | `cc00920fa567460999821d9118d3b8c752b9df22be83d63969dd810f5273b252` |
| Executed native binary | `9ef666c2a2eb659bfb5bd1df24e9abdfab2e7b86031436fd6e855e82d0401fc9` |

[Result](../reports/A26-material-boundary-result.json),
[before repair](../reports/A26-before-repair.json),
[identities and exact commands](../reports/A26-identities.json), and
[final CTest](../reports/A26-final-ctest.log) retain source, binary, linked archive,
setup and observed outcomes. A14's original failure SHA-256 remains
`9b0bfcd8a09e9a0504a208fb07abbb1e86f8bd81b7f4d8a1961c87886bc80692`;
all six A18 PNG byte hashes also remain unchanged.

## Reproduction and remaining gates

From the repository, with exclusive `build-native` access, GCC 14.2.0 Release,
SDL 2.32.10, MIDI/VST3 OFF:

```sh
../build-tools/cmake/data/bin/cmake --build ../build-native --parallel 3 --target test_standalone_material_acceptance
../build-tools/cmake/data/bin/ctest --test-dir ../build-native -R '^test_standalone_material_acceptance$' --no-tests=error --output-on-failure -V
```

Root granted and received back the shared build slot. `git diff --check` passes.
A25 received the stable final renderer hash for matched timing. Native gallery,
actual display/high-DPI/accessibility, physical audio/MIDI, model fidelity and
release gates remain separate. This CTest duration is not the material benchmark.
Next: integrate this bounded repair and qualify the new Flat modal appearance in
the source-identified application gallery; preserve A14/A18 as historical evidence.
