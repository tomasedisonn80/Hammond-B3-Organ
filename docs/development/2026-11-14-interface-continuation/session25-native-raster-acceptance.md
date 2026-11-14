# A25 — independent native workspace raster acceptance

Actual worker `/root/w05_a25_native_raster_acceptance`, assignment 25 of this
session's 60. Added only
`apps/standalone/native_tests/test_standalone_workspace_raster.cpp` and this
note/report/evidence. Root registered the target and owns shared documentation,
integration and publication. No production, preset-test, sound/state, asset,
staging or commit changes were made by this worker.

## Observed result and exact scope

**The new focused CTest passes 1/1 in 8.80 seconds, with zero failures across
150 actual `paint_instrument` frames.** The unchanged 60-second timeout has
ample margin on this named Linux runner. Release compilation passes GCC 14.2.0
with the project's strict warnings, including `-Wconversion`,
`-Wsign-conversion`, `-Wshadow` and `-Werror`. The existing pinned SDL 2.32.10
software renderer paints RGBA32 surfaces without a window, audio or MIDI device.

Read the standing instructions, current M0–M9 plan, accepted workspace/geometry/
inspection contracts, relevant atlas interface pages, and A14/A17/A19/A20
handoffs before implementation. Reused the shared native build only after A24
released it. Released that build after the final focused run; A28 owns the
subsequent scale/text qualification. The existing 24-preset raster gate was
preserved and was neither duplicated nor rerun by A25.

The matrix uses 960×700, 1280×900 and 1672×941 in both Dimensional and Flat.
For each manual, literal natural indices are `0,29,60` and accidentals
`1,30,58`; pedal naturals are `0,12,24` and accidentals `1,13,22`. These cover
left, center and right positions of all three divisions.

| Feature risk | Executed acceptance |
|---|---|
| Held paint leaves its silhouette or affects another key | 108 representative held cases; every frame pixel compared against independently owned visible key masks. Separate natural/accidental batches preserve the occlusion distinction. Each selected key changes its top, shows brass held ink and changes its dimensional front. |
| Focus paints an AABB, neighboring key or over an accidental | 108 held-plus-focus cases. Every changed pixel outside the legitimate footer caption must be cyan, belong to that key's visible silhouette, and lie at least one pixel inside its original quad. |
| Top/front planes disappear or Flat retains depth | 108 surface cases. Nine paired central-plane samples require mean top/front contrast of at least 20 for naturals or 8 for accidentals, with at least six of nine front samples darker. Flat requires nine exact uniform-fill samples through the former front area and an empty front quad. |
| Accidental/natural paint order is reversed | 54 cases independently identify both underlying naturals and require visible dark accidental samples above them. Natural held/focus changes cannot alter those occluded pixels. |
| Extreme slopes become rectangles | 12 dimensional exposed-corner sets within the extreme natural AABBs must retain the literal dark key-bed RGB `(7,9,8)` at every pixel outside the silhouette. |
| Hidden performance body paints in Service/Rotary | 12 pairs change all 147 copied held bits; the entire frame must remain byte-identical with fixed/null inspection input. |

The containment oracle uses long-double convex half-plane cross products at
pixel centers with explicit half-open top/left versus bottom/right ownership.
It consumes shared quad coordinates but never calls production `contains`, hit
testing, projection or raster helpers. This isolates native paint acceptance
from A19's independent all-147-key numerical projection gate and A18's input/
ownership gate. No boundary tolerance was added. The observed minimum
nine-sample mean contrasts are **53.1049 natural** and **20.0227 accidental**
on a weighted 0–255 RGB luminance scale; these are presentation checks, not
physical material measurements.

## Retained initial failure and oracle correction

The [first run](reports/a25-ctest-first.txt) finished in 9.33 seconds with six
failures, all from a new single-pixel top/front contrast assumption for short
accidental pedals at minimum/reference sizes. Containment, focus, occlusion,
Flat and hidden-body assertions already passed. The
[diagnostic run](reports/a25-contrast-diagnosis.txt) preserves actual coordinates
and colors:

| Fixture, pedal index 1 | Top height | Original 80% cap-tail probe | Central cap probe | Front probe |
|---|---:|---|---|---|
| 960×700 | 11.36 px | `(84,613)` → `(25,27,24)` | `(84,609)` → `(45,45,40)` | `(84,619)` → `(19,20,16)` |
| 1672×941 | 23.3136 px | `(149,842)` → `(30,31,27)` | `(149,835)` → `(44,44,39)` | `(149,850)` → `(23,23,19)` |

The fixed 80% probe selected the shaded tail of an otherwise visibly brighter
cap. The contract requires distinct planes, not a fixed brightness relationship
between every tail/gloss pixel. Replaced that assumption with nine central
top/front sample pairs, retaining both original numeric contrast thresholds and
adding the six-of-nine darker-pair requirement. Flat likewise gained nine
literal-color samples. No production change, geometric tolerance, skipped case
or deadline extension was needed. The original test/diagnostic hashes and both
failed transcripts remain in the [machine-readable report](reports/a25-native-raster-acceptance.json).

## Source identity and reproduction

Published base HEAD is `5d81199a9822874b55f3b0a124715cbd6eadf0e5`; this result
qualifies the recorded working-tree overlay, not that commit alone. All recorded
test, renderer, drawing, model, inspector and CMake hashes were stable across the
final gate. Full hashes, command arrays, toolchain, initial outcomes, final
counts and image identities are in the report.

| Tested input/output | SHA-256 |
|---|---|
| New test source | `4013b25b53d15ee649804056d817e0936c8251fd5894656cef319e832bfe6c23` |
| `InstrumentView.cpp` | `5f5f209dbe33cb92e3c1d237258ba123d0a86e78c694d50c0634db8549d54407` |
| `Drawing.cpp` | `84b91089fa6938075e8b0cfde39d66266acc9c3e7ea026958deb9eaf6a9b16fe` |
| Test executable | `79884188406c30012f66918f8b9abcd926573dde3ffa935a958589bff672243e` |

Working directory: `/workspace/scratch/601951e27dc3/Hammond-B3-Organ`.
Prerequisite: root-registered target in the existing coordinated native Release
build, with the pinned shared dependencies. Do not configure/build that directory
concurrently with another owner.

```sh
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/cmake \
  -S /workspace/scratch/601951e27dc3/Hammond-B3-Organ \
  -B /workspace/scratch/601951e27dc3/build-native
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/cmake \
  --build /workspace/scratch/601951e27dc3/build-native \
  --target test_standalone_workspace_raster --parallel 3
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/601951e27dc3/build-native \
  -R '^test_standalone_workspace_raster$' --output-on-failure --no-tests=error -V
```

Retained [configuration](reports/a25-configure.txt), [build](reports/a25-build.txt)
and [final CTest](reports/a25-ctest.txt) output accompany the result. Test image
output is normally off. An optional capture-directory argument, or
`HAMMOND_WORKSPACE_RASTER_CAPTURE_DIR` in the CTest environment, saves exactly two
reference-size BMP frames. The final gate used
`/workspace/scratch/601951e27dc3/a25-native-raster`; lossless RGB conversion to
the retained PNGs was checked byte-for-byte.

## Native picture proof and remaining gates

The [Dimensional](reports/a25-native-renderer-test-dimensional.png) and
[Flat](reports/a25-native-renderer-test-flat.png) pictures are **native renderer
test frames with injected/copied UiModel state**, not full application captures.
Both show nine held accidentals across the two manuals/pedals and cyan focus on
Upper index 30 / MIDI 66. Visual inspection confirms the projected surfaces and
fronts in Dimensional, planar surfaces in Flat, and contained focus. No image
generation was used. A22's separate eight full-application captures remain
untouched.

This gate establishes representative scale-one software paint behavior. It does
not individually render every one of the 147 keys in every focus/hold state,
qualify scaled display behavior, or test inspector text correctness through the
fixed/null document. A19, A18 and the preserved preset gate retain their distinct
coverage; A28 addresses scale/text. OS window dispatch, hardware GPU behavior,
physical devices, hosts, accessibility, callback deadlines, specimen fidelity
and literal concept-image equality remain separate gates. Root integrates this
evidence into the coherent source, shared handoffs and publication.
