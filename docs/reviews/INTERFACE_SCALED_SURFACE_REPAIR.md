# Fractional-scale filled-surface repair

Actual worker: `/root/w06_a31_scaled_surface_repair`, A31 in wave 6 of the
current interface continuation. **The observed SDL software surface gaps are
repaired.** The corrected native build passes five affected suites, including
298 complete-target surface checks over 18,309,120 pixels. The original
1.5× interior probe now has no missing pixels, and both new full-view PNGs were
inspected. This is a scoped raster repair, not a display-DPI, physical-device,
accessibility, performance or atlas-fidelity qualification.

The [structured result](../development/2026-11-14-interface-continuation/reports/a31-scaled-surface-repair.json),
[final native log](../development/2026-11-14-interface-continuation/reports/a31-ctest-final.txt)
and [source/build identities](../development/2026-11-14-interface-continuation/reports/a31-final-identities.json)
retain the actual source, commands, first failure and recheck. Root owned the
source freeze and publication. A31 made no staged change or commit.

## Source and protected boundary

The starting working overlay was based on published `5d81199a9822874b55f3b0a124715cbd6eadf0e5`.
Its pre-repair `Drawing.cpp` was
`84b91089fa6938075e8b0cfde39d66266acc9c3e7ea026958deb9eaf6a9b16fe`.
A31 waited until root completed its 327-input coherent gate and pinned the
accepted source in the index before editing either assigned source file.
The only differences from that input freeze before the A31 build were
`Drawing.cpp` and `native_tests/test_standalone_drawing.cpp`.

| Final input/output | SHA-256 |
| --- | --- |
| `apps/standalone/Drawing.cpp` | `9b788234405964f6675ab43428735e425b460c8045f2c6eb064c9e19b40a0a5f` |
| `apps/standalone/native_tests/test_standalone_drawing.cpp` | `c49af9889f5f43e9f3ea20d42a3263b2f911ab1c7877b7b6ff42e99216823ebc` |
| Unchanged `Drawing.h` | `749e718436e61ad4a13a28e167c4b07e4dd789adf213a6229a503fc1f2bcf188` |
| Preserved A28 `InstrumentView.cpp` | `6b498c9ba2c47acf432216189159b928d2a5d31368ec34c1fe8dc906710e8a67` |
| Rebuilt `hammond_standalone` | `968938196bcf291270e1b1e32e36f08535281a959fb47ea731a216c56486d270` |
| Rebuilt `test_standalone_drawing` | `f273618fb835368744c817a95e316060b7e80c54fd94ca3c3d67b79ae3ef02f7` |

Seventeen relevant source hashes were unchanged from final build start through
the completed gate. The identity report also retains the drawing/support/core
archives, SDL archive and revision, generated assets/profile and compiler flags.
The compiler was GCC 14.2.0, C++20 Release, with the repository's conversion,
sign-conversion, shadow and other warnings treated as errors. SDL was the
existing pinned 2.32.10 software renderer. No dependency or SDK was copied.

No header, `InstrumentView`, `UiModel`, font/art asset, core, audio, parameter,
saved-state, CMake or registration change belongs to A31. In particular, A28's
physical preset-focus clip repair remains intact. The full M0–M9 plan and its
physical/model evidence gates remain unchanged.

## Original failure and independent reproduction

A28's [actual 1.5× images and diagnosis](INTERFACE_SCALE_TEXT_AUDIT.md) showed
horizontal clear walnut rows across dimensional panels, tablets and caps even
though its state, clip and value-presence checks passed. In a blank Generator
card patch, 9,500 of 28,500 pixels were the exact clear color; all 25 rows with
`y % 3 == 2` were missing.

The old `gradient` and `rounded` routines emitted rectangles one logical pixel
high. Pinned SDL's `SW_QueueFillRects` converts the scaled height to an integer:
1.5 becomes 1, while successive origins advance by one and then two physical
rows. The missing third row exposes the background.

Before any repository edit, A31 compiled a small independent
[interior probe](../development/2026-11-14-interface-continuation/reports/a31-interior-probe.cpp)
against the unchanged drawing and SDL archives. Its oracle is a strict inner
rectangle that both shapes must cover; it does not duplicate the corner or
scanline implementation. The [original exit-1 result](../development/2026-11-14-interface-continuation/reports/a31-first-interior-failure.txt)
and [same-source corrected result](../development/2026-11-14-interface-continuation/reports/a31-interior-recheck.txt)
show:

| Scale | Required interior pixels per primitive | Missing before | Missing after |
| --- | ---: | ---: | ---: |
| 1× | 336 | 0 | 0 |
| 1.5× | 756 | 252 | 0 |
| 2× | 1,344 | 0 | 0 |

Each row applies independently to both `gradient` and `rounded`.

## Production correction and the first recheck

Both routines now reuse the existing output-pixel raster helper, renamed
`PixelRaster` because it also serves these filled surfaces. They visit the
clipped physical rows, transform each pixel center back into logical geometry,
and paint disjoint integer spans. The helper retains the actual physical
viewport/clip bounds while temporarily setting scale one, then restores the
caller scale. It does not rewrite the caller's viewport or clip.

Rounded corners use a double-precision circular inset at each sampled logical
y. Radius clamps to half the smaller extent; zero/negative radii produce the
same bounded rectangle. Finite input checks precede geometry conversion, and
iteration is bounded by the visible output intersection, including for huge
finite bounds. A fractional radius below one is sampled as its actual circle.

Gradient stops stay at the first and last logical pixel centers. The old
float color interpolation therefore remains identical for integer-aligned
scale-one gradients, while fractional scales sample a continuous ramp. Clips
do not move or renormalize the color stops. A height of at most one logical
pixel uses the first color. Fractional boundaries and previously truncated
rounded edges intentionally use the correct center-tested silhouette; the
repair does not claim every old boundary pixel is unchanged.

The [first rebuilt gate](../development/2026-11-14-interface-continuation/reports/a31-ctest-first.txt)
passed four suites but failed 48 newly added narrow-span cases. This exposed a
second concrete boundary defect in the reused helper: a one-pixel span used
`SDL_RenderDrawLine` with coincident endpoints. Pinned SDL's `SDL_BlendLines`
does not paint that closed endpoint, even with an opaque source color. The
helper now emits `SDL_RenderDrawPoint` for a one-pixel span and retains the
existing line path for wider spans. No oracle, tolerance or expected count was
relaxed. The first source and failed log remain retained.

## Meaningful regression and final native gate

The existing drawing test now checks entire RGBA targets rather than only
whether some ink appeared. Its rounded-shape oracle uses independent
two-dimensional circle distance, not production scanline insets or geometry
helpers. It distinguishes missing pixels, out-of-shape/clip paint and wrong or
multiply blended color.

The 288-case main matrix combines six transforms, three viewport/clip setups,
four shapes, opaque/translucent paint and both primitives. The transforms are
1×, 1.5×, 2×, 0.75×, 1.25× and nonuniform 1.25×/1.75×. Shapes include integer
and half-pixel boundaries, a partly offscreen fractional rectangle and a narrow
shape that becomes one physical pixel wide. Physical clips have odd edges;
viewports include positive and negative translations. Alpha 128 detects a
repair that covers missing rows by painting others twice.

Additional cases cover 15 literal gradient-stop samples, exact cropped versus
uncropped gradient pixels, zero/negative radii, subpixel height, nonfinite or
empty input, huge finite/offscreen geometry, an empty clip and a null renderer.
These produce 298 whole-target checks over 18,309,120 pixels. Renderer scale,
physical viewport/clip, clip enable and blend mode are checked after drawing.
The original 144 glyph cases, 18 label cases and 12 metric/space cases remain.

| Rebuilt CTest suite | Final result | Elapsed |
| --- | --- | ---: |
| `test_standalone_drawing` | All original glyph/metric checks and 298 surface checks pass | 0.13 s |
| `test_standalone_quad_drawing` | 17 complete-target coverage checks pass | 0.01 s |
| `test_standalone_workspace_raster` | 150 frames; held/focus/front/occlusion/hidden checks pass | 9.21 s |
| `test_standalone_scaled_view` | 168 frames/states, 90 clip, 16 focus, 56 value and 58 line checks pass | 19.80 s |
| `test_standalone_preset_raster` | 96 label/focus, 376 isolation and 48 state checks pass | 11.54 s |
| **Affected gate** | **5/5 suites pass** | **40.70 s** |

These elapsed observations do not establish a frame-rate or deadline claim.
The complete app was rebuilt in the same source window. Runtime checks were
serialized with A33/A35's separate native observations.

## Inspected native proof and reproduction

The final A28 test executable produced these newly identified injected frames
during the corrected gate:

- [Play at 960×700 logical / 1440×1050 physical / 1.5×](../development/2026-11-14-interface-continuation/reports/a31-injected-renderer-play-960x700-at-1p5.png)
- [Service at the same dimensions and scale](../development/2026-11-14-interface-continuation/reports/a31-injected-renderer-service-960x700-at-1p5.png)

Both actual PNGs were opened and inspected. The repeated horizontal clear rows
are absent across the visible deck, cards, buttons and caps. Their gradients
are continuous, rounded borders remain bounded, and visible cyan focus remains
inside its control. The tiny preset accidental legends remain the distinct A34
readability follow-up.

The [same-patch comparison](../development/2026-11-14-interface-continuation/reports/a31-surface-gap-comparison.json)
measures `x=60..439, y=444..518`: clear walnut pixels fell from **9,500/28,500 to
0/28,500**. This proves coverage of that interior; it is not a complete visual
quality score. The [proof identity record](../development/2026-11-14-interface-continuation/reports/a31-proof-images.json)
retains BMP, decoded-pixel and PNG hashes and exact lossless conversion checks.
The PNGs total **590,550 bytes**. Only A31's reproducible intermediate BMPs were
removed. A28's original failing images remain unchanged.

The images call actual `paint_instrument`/`Drawing` on software surfaces with
injected copied state. They are **not application-window screenshots**: labels
such as `AUDIO RUNNING` and `CURRENT SNAPSHOT` describe the fixture, not observed
physical devices. The complete-view suite allocates at most 1920×1400, using
tiles for its larger virtual view. This worker retained only the two 1440×1050
proofs.

From the repository root, after coordinating exclusive use of the native build:

```sh
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/cmake \
  --build ../build-native --target hammond_standalone test_standalone_drawing \
  test_standalone_quad_drawing test_standalone_workspace_raster \
  test_standalone_scaled_view test_standalone_preset_raster -j 3
HAMMOND_SCALED_VIEW_CAPTURE_DIR=/tmp/a31-fresh-proof-directory \
  /workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/ctest \
  --test-dir ../build-native \
  -R '^test_standalone_(drawing|quad_drawing|workspace_raster|scaled_view|preset_raster)$' \
  --output-on-failure --no-tests=error -V
```

The optional proof directory must not already exist. Exact executed commands
and the independent probe compile/run commands are in the structured result.
No CMake option or target was added.

## Handoff and limits

Build-native and the native CPU window were released to root/A35 after the
successful recheck; no further A31 production changes are planned. Root owns
shared status, actual application-gallery refresh, integrated qualification,
publication and the next source freeze. A35's MIDI observation repair and A34's
preset-label correction have separate evidence and ownership.

The algorithm accepts arbitrary positive finite scales through the existing
raster helper, but executed coverage is the six stated transforms plus the
full-view 1×/1.5×/2× matrix. GPU backends, real monitors and cross-monitor DPI,
physical audio/MIDI, screen readers, platform timing and physical instrument
fidelity remain unqualified here. The retained source concept's structural
differences and the whole project's outstanding M0–M9 gates remain explicit.
