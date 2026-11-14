# A14 — bounded quad painting and inside focus

Actual assignment: `/root/w03_a14_quad_drawing`, wave 3, worker 14 of this
interface continuation. Completed 2026-11-14. The integrator owns publication,
shared status, CMake registration and the final application comparison.

## Scope and source

Implemented the two drawing primitives accepted in
[INTERFACE_GEOMETRY_CONTRACT.md](../../INTERFACE_GEOMETRY_CONTRACT.md), after
reading the standing `AGENTS.md` instructions and coordinating the shared
`UiQuad` header with A13. Owned implementation files are
`apps/standalone/Drawing.h`, `apps/standalone/Drawing.cpp` and
`apps/standalone/native_tests/test_standalone_quad_drawing.cpp`. A13 supplied
`UiQuad`; this assignment did not edit its header. The integrator registered
the target and its 30-second CTest timeout.

The tested base HEAD was
`c83fe2336be931385f0d7ab82c55b30bfdfc8fc6`, with the recorded uncommitted source
overlay. Relevant source/header/CMake hashes were identical before and after
the final build and test. The exact hashes, commands, executable identity and
toolchain flags are in [reports/a14-result.json](reports/a14-result.json).
This qualifies the coordinated primitive target; it is not a claim that all
other live working-tree changes were tested.

## Implemented behavior

`Drawing::quad(shape, top, bottom)` paints a vertical RGBA gradient over the
same half-open horizontal-edge quad that `UiQuad::contains` admits. It samples
output-pixel centers and emits horizontal integer spans. This avoids the
pinned SDL software geometry backend's fractional-vertex truncation, which
could otherwise move a sloping edge outside the shared shape.

`Drawing::quad_outline(shape, color, thickness)` paints the outer shape minus
an inside inset. It first evaluates each original sloping side at the current
y, then applies the horizontal inset; top and bottom bands use a vertical
inset. Thickness is bounded by half the shape height and its narrowest end
width. The bands do not overlap, so translucent corners receive one blend.
The outline follows the actual shape rather than its bounding rectangle.

Both operations reject invalid/empty/nonfinite geometry. Invalid, nonpositive
or nonfinite outline thickness is also a no-op. The shared validator remains
the single geometry admission policy. Double intermediates preserve finite
calculations even when float endpoints have opposite extreme magnitudes.

Work is intersected with the current output, viewport and clipping rectangle
before any edge-to-integer conversion or scanline iteration. Widened integer
arithmetic protects the viewport/clip intersection. Each admitted scanline
spans only visible pixels, including for `FLT_MAX` inputs. The helper reads
physical viewport/clip edges at scale one, emits physical-pixel spans, and
restores the caller's original rendering scale on every exit. Viewport, clip
and blend mode are preserved. These remain main-thread drawing operations.

## Executed acceptance

Environment: Linux, GCC 14.2.0, CMake 4.4.4, C++20 Release with the repository's
strict warning flags including `-Wconversion`, `-Wsign-conversion`, `-Wshadow`
and `-Werror`. SDL 2.32.10 at
`5d249570393f7a37e037abf22cd6012a4cc56a71` was reused from the already pinned
shared dependency. The software renderer paints a 128 × 96 RGBA surface.
The test constructs no window, audio device, MIDI device, Session, font texture
or decorative asset.

**Result: 1/1 focused CTest passed; 17 complete-target coverage comparisons;
zero reported failures.** The final CTest completed in 0.01 seconds overall.

| Risk | Executed evidence |
|---|---|
| AABB substitution or missing slopes | Every pixel checked against a literal trapezoid oracle with sides moving 16 pixels over 72 rows. |
| Wrong gradient or top/front seam | Three explicit gradient samples; distinct adjacent top/front planes; their union exactly preserves the original silhouette. |
| Focus outside the key | Complete mask of all four inside bands; transparent interior and unchanged outside corners. |
| Overlapping translucent focus strips | Every changed focus pixel has the expected single-blend color. |
| Narrow accidental collapse | A four-pixel top width with requested thickness 100 clamps safely and keeps an unpainted center. |
| Ambiguous shared-edge ownership | Two adjacent translucent rectangles place their shared edge and outside edges exactly on pixel centers; no gap or double blend. |
| Invalid input conversion | Nine empty/nonfinite/malformed shapes and four invalid thickness values paint nothing; null-renderer calls return safely. |
| Scale or clip corruption | Full masks at scale 1, 1.5 and 2 with translated viewport and clip; scale/viewport/clip/blend state checked after both operations. |
| Unbounded source extent | `FLT_MAX` quad with a partly off-target viewport and small clip; offscreen focus edges, empty clip and fully offscreen extreme shapes all return with the expected mask. |

The test's shape expectations use explicit fixture equations rather than
calling the production containment helper. Coverage compares the complete
software surface after `SDL_RenderFlush`, including pixels outside the active
viewport, so unintended outside paint is observable.

The initial build invocation preceded regeneration of the shared CMake cache
and reported that the newly registered target did not exist. Regenerating the
existing Release cache succeeded. The first focused build/test then passed;
one exact shared-edge fixture was added and the final build/test below passed.
The retained final build also records normal CMake regeneration when A15's
separate SDK-free test source appeared; the recorded primitive inputs remained
unchanged. These setup events were not product test failures.

## Reproduction

Working directory: `/workspace/scratch/601951e27dc3/Hammond-B3-Organ`.
Prerequisites are the shared configured Release native build and pinned SDL
source. Do not run concurrent mutations of that build directory. Regenerate
CMake after newly registered targets before naming them in a build command.

```sh
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/cmake \
  -S /workspace/scratch/601951e27dc3/Hammond-B3-Organ \
  -B /workspace/scratch/601951e27dc3/build-native

/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/cmake \
  --build /workspace/scratch/601951e27dc3/build-native \
  --target test_standalone_quad_drawing -j 3

/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/601951e27dc3/build-native \
  -R '^test_standalone_quad_drawing$' --output-on-failure --no-tests=error -V
```

Retained output: [build](reports/a14-build.txt),
[CTest](reports/a14-ctest.txt), [source and result](reports/a14-result.json).
The target needs only `hammond_standalone_drawing`, which already links the
pinned SDL static library; it requires no full Session/UI support linkage.

## Next integration and limits

A19 supplies the contracted perspective `hit`, `top` and `front` shapes. A20
should paint `key.top` and `key.front` with `quad`, then paint focus with
`quad_outline(key.hit, ...)`; passing the AABB would defeat the shared
silhouette. Flat keys use the same primitive and their empty front is a no-op.
Preserve natural-before-accidental paint order and independent held-state
colors when adding those renderer calls.

After integration, build the complete application and affected tests from one
coherent source, inspect actual dimensional/flat captures at representative
sizes, retain the original reference comparison and update README screenshots.
This assignment provides software raster evidence for primitives. Hardware
GPU behavior, other native platforms, complete application appearance,
physical instrument accuracy and literal 1:1 reference fidelity remain outside
this result. The parent integrates the note into status/next steps and publishes
the completed checkpoint. No child commit or push was performed.
