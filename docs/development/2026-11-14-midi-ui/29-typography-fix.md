# A29 — Preserve narrow glyphs in SDL software drawing

Date: 2026-11-14. Actual worker: `/root/w05_a29_typography_fix`, MIDI/UI
wave 5, assignment 29. Owned files are `apps/standalone/Drawing.cpp`, the new
`apps/standalone/native_tests/test_standalone_drawing.cpp`, and this note.
The integrator owns CMake and performed the coordinated native builds. This
worker made no commits, shared-document edits, font regeneration, geometry
changes, or changes to `main.cpp`.

## Result and original failure

The P1 disappearance described in the
[independent reference review](../../reviews/MIDI_UI_REFERENCE_REVIEW.md)
is reproduced by an actual SDL software-renderer test and corrected in the
final native build. The final focused CTest passes **1/1** in **0.05 seconds**;
all **144 separately rendered glyph cases** pass. Four source-identified
native capture runs and a separate minimum-size registration-footer smoke
also pass. This repairs vanished raster coverage; it does not establish a
general typography, native-display, accessibility, or reference-fidelity pass.

Before changing `Drawing.cpp`, the worker copied its original bytes and
relevant font/layout inputs into
`/workspace/scratch/cd4bd06ce68f/a29-typography/baseline/`. The integrator built
the new regression against that unchanged source. The worker copied the
resulting test executable into the same private directory and executed it.
Its result was **exit 1, exactly 48 failures**, each reporting
`ink pixels=0, maximum red increase=0`:

| Original isolated failure | Sizes | Positions per size | Failures |
|---|---|---:|---:|
| Sans `l`, `i`, `-` | 9, 9.5, 10.5 pixels | 4 | 36 |
| Serif `-` | 9, 9.5, 10.5 pixels | 4 | 12 |

The other 96 isolated glyph draws, 18 normal-size labels, width/multiline/space
checks, and atlas-gutter checks passed against the original implementation.
The failure therefore demonstrates lost individual characters rather than an
empty sentence, a missing font, or a measurement discrepancy. Full stdout,
stderr, command, binary identity, and source identities remain in
`baseline-test.stdout.txt`, `baseline-test.stderr.txt`, and
`baseline-test-record.json` under the private evidence root above.

## Bounds inspection and correction

The worker read `tools/generate_standalone_font.py`, the atlas manifest,
the committed glyph records, and the drawing path before editing. The
generator sets `PADDING = 2`, checks every padded rectangle against the atlas
bounds, and rejects any nonzero alpha outside the ink rectangle within that
gutter. The new test independently decodes the committed alpha and checks
all 94 nonempty glyphs of each face, including transparent gutter pixels.

| Atlas | Dimensions | Union of two-pixel-padded glyph bounds |
|---|---|---|
| Sans, nominal height 32 | 512 × 256 | x `[0, 509)`, y `[0, 138)` |
| Serif, nominal height 40 | 512 × 256 | x `[0, 496)`, y `[0, 206)` |

The Sans `l` and `i` ink rectangles are 3 × 24 pixels; its hyphen is 9 × 3.
At 10.5 pixels the three-pixel extent becomes 0.984375 destination pixels;
at 9.5 it is 0.890625. The original tightly cropped `SDL_RenderCopyF` call
produced no raster coverage for those subpixel extents in SDL's software
renderer. `SDL_ScaleModeLinear` was already enabled.

The final change determines padding **independently for each axis**. If the
original glyph extent times the font scale is less than one pixel, that axis
includes the existing two transparent pixels on both sides. Its source origin
and bearing both subtract two source pixels, and its destination extent uses
the expanded source extent at the same scale. An axis already at least one
pixel uses the original copy coordinates and sampling. The existing
`advance_64`, baseline/line spacing, `text_width`, and dynamic text remain
unchanged. Wrapping/elision callers and all font/asset identities are unchanged.

An earlier candidate expanded both dimensions of every nonempty glyph.
It passed the entire isolated test and all four capture runs, but actual
minimum-size image inspection exposed changed sampling in the readable Serif
drawbar headings. It was rejected for that visual side effect. Its exact
source, test/application executables, passing test record, and screenshots
remain under `a29-typography/fixed/`, `fixed-test-record.json`, and `captures/`.
The final per-axis threshold avoids that side effect. These earlier passing
checks do not substitute for the final candidate's separate qualification.

## Independent drawing acceptance and CMake wiring

The test uses `SDL_Init(0)`, a known 640 × 96 RGBA surface, and
`SDL_CreateSoftwareRenderer`; it opens no window, audio device, MIDI device,
or Session. The observed implementation is **SDL 2.32.10, renderer software**.
Every isolated glyph gets a fresh background of RGB `(17,23,31)` and foreground
`(227,211,173)`, followed by actual `SDL_RenderReadPixels`. A pass requires
changed RGB pixels and a maximum red-channel increase of at least eight.

It renders each of `l`, `i`, and `-` at 9, 9.5, 10.5, 16, 24, and 32 pixels
for Sans and Serif at four fractional origins: 0, 0.25, 0.5, and 0.75.
That is 144 independent glyph cases. Eighteen additional normal-size label
draws cover `TONEWHEEL ATLAS`, `NOMINAL DRY ORGAN`, and `16' 5 1/3' 8'` at
16/24/32 pixels in both faces. Twelve face/size combinations verify frozen
pre-repair width values, multiline maximum width, empty width, and transparent
spaces. The baseline execution verifies the frozen expected metrics before
the production correction is applied.

The integrator introduced `hammond_standalone_drawing` with `Drawing.cpp` and
the generated `${HAMMOND_REFERENCE_ART}` header. It exposes
`SDL2::SDL2-static`, the standalone source include directory, and
`${PROJECT_SOURCE_DIR}/include`; the generated-header directory is private.
The app and `test_standalone_drawing` link this same drawing library.
The test defines `SDL_MAIN_HANDLED`, uses the strict project target settings,
has a 15-second timeout and `standalone;native` CTest labels, and participates
in the native test-input aggregate. Its observed link line contains only
the drawing library, pinned SDL, `libm`, and pthreads; no core, profile, audio,
or MIDI library is needed by this test.

The native build used GNU C++ **14.2.0**, C++20 Release (`-O3 -DNDEBUG`),
`-Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror`.
The integrator used the pinned CMake 4.4.4 executable and retained the final
successful build log as
`/workspace/scratch/cd4bd06ce68f/drawing-refined-build.log`. The same configured
targets can be rebuilt with:

```sh
/home/agent/.cache/uv/archive-v0/kvsqq5-iHdbf13RC/cmake/data/bin/cmake \
  --build /workspace/scratch/cd4bd06ce68f/build-native \
  --target test_standalone_drawing hammond_standalone --parallel 2
```

The worker's final executed test command was:

```sh
/home/agent/.cache/uv/archive-v0/kvsqq5-iHdbf13RC/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/cd4bd06ce68f/build-native \
  -R '^test_standalone_drawing$' --output-on-failure --no-tests=error -V \
  -O /workspace/scratch/cd4bd06ce68f/a29-typography/final-ctest.log
```

It reports zero failures across every case above. The final source/test/binary
hashes and command are also retained in `final-test-record.json`.

## Actual native comparison

The worker opened the original reference JPEG, A17's original minimum modal
and registration-footer images, all four
[A28 baseline captures](../../../examples/demos/standalone-midi-ui-v1/README.md),
the first candidate's minimum images, and all final images. The A28 gallery
remains unchanged. The final evidence root is
`/workspace/scratch/cd4bd06ce68f/a29-typography/final-captures/`.

From the repository root, the executed final capture command was:

```sh
python3 tools/capture_standalone_reference.py \
  --exe /workspace/scratch/cd4bd06ce68f/a29-typography/final/hammond_standalone \
  --source-root /workspace/scratch/cd4bd06ce68f/Hammond-B3-Organ \
  --build-root /workspace/scratch/cd4bd06ce68f/build-native \
  --output /workspace/scratch/cd4bd06ce68f/a29-typography/final-captures \
  --dummy-sdl \
  --expected-exe-sha256 33728f0df9688ed82e8e5e9446465ff98acbef60ca2d5438b1f22de4db1de4bb \
  --source-context /workspace/scratch/cd4bd06ce68f/a29-typography/final-test-record.json
```

All four 1400-ms replay cases exited zero, passed the capture tool's actual
diagnostic checks, and retained unchanged recorded source/build/dependency/input
identities. The three player cases acknowledge UI Upper 60 and Lower 64; the
modal case uses explicitly synthetic MIDI and real modal keyboard actions,
with Apply focused. Every capture reports software rendering and dummy
video/audio. BMP-to-PNG conversion preserved every decoded pixel, and original
BMP bytes are retained in lossless archives.

| Final image | Result | PNG SHA-256 |
|---|---|---|
| `reference-1672x941.png` | Passed, 141 callbacks / 72192 frames | `f1068c5161e62acfc8fdab9e2479284cba846c24d65ea2f6b87300fc4e5e6c6f` |
| `default-1280x900.png` | Passed, 125 callbacks / 64000 frames | `ce688276f0a79d0421ac2a4ae672971d63ae00f9efa8c074cd12f62aafb05c43` |
| `minimum-960x700.png` | Passed, 119 callbacks / 60928 frames | `5e5440ec015fb95739f69f4163f69919b1fa6e6413dd3273db93d28fd4104709` |
| `midi-synthetic-960x700.png` | Passed, 132 callbacks / 67584 frames | `97584a4b0e05a989958df789ab75bb0f7eace82fe3b1e3436036235f18765095` |

At minimum size, `Close`, `Full`, and `--list-midi` now contain the previously
absent narrow strokes; the modal keyboard-help line and undimmed footer also
retain them. A pixel comparison checks all ten `l`/`i`/hyphen boxes in the
refresh instruction: their former maxima of red 35–36 (background only)
become 67–68 after the repair. The precise rectangles and values are retained
in `a29-typography/pixel-comparison.json`.

The same comparison verifies **zero changed pixels** in the title, both
drawbar headings, and corrected footage-label regions at all three sizes.
The entire focused Apply-button rectangle `(138,514,252,40)` also matches the
A28 baseline exactly. The main controls, key planes, focus, nominal labels,
and cabinet status retain their observed arrangement; no new overlap was
seen in these static captures.

A separate 800-ms minimum smoke used a nonexistent private state path to
reproduce A17's exact undimmed `Proposed audition registration: Upper B
888000000 / Lower B 008000000 / Pedals 80.` footer. It exited zero with
75 callbacks / 38400 frames, zero errors, a held-state screenshot, and the
same explicit dummy/software drivers. The worker opened its native PNG and
verified the previously missing strokes in `audition`, `registration`, and
`Pedals`. Its command and diagnostic record remain in
`a29-typography/registration-footer/record.json`; its PNG SHA-256 is
`566e58eb88edebda84dfa601554504d6c57225e9b21256441f793bfdbe92afd7`.

## Exact identities and retained limits

The checkout HEAD during qualification was
`e09107414896c2c53dad124a74f60c8043fadfe4`, with concurrent uncommitted
MIDI/UI integration work. The named file hashes and capture inventories,
not HEAD alone, identify these tests and pixels.

| Input or executable | SHA-256 |
|---|---|
| Original `Drawing.cpp` | `4d13a5eb312799b341e44a41f52960e44c04da1a7b05ecfdda86bc635e1ecda9` |
| Original failing test executable | `56167b3e67a78280fdde9e71d417f263725a8c17568d996d8b0952ab8a96e431` |
| A28 baseline application used for image comparison | `e8871447021a1373e2bfdc262a513d12487e49fd0e833bad068f226a6938ed2d` |
| Rejected full-padding candidate `Drawing.cpp` | `8fc8b8745f789de89a5bea4c60986f330445154280983cb4af46392db362c952` |
| Rejected candidate app executable | `a2b2deb4da098bb2219c2d9ce43c407e504563275a138de9eb1da8fc5f5d137e` |
| Final `Drawing.cpp` | `c1460212ccc220c77842e7340c83639e97194134ff520626999c8decd97f4616` |
| Regression source, unchanged between baseline and final | `a06f29a8d7a614ed32264d8e90c369479111540e714232d393a4b293e3427fcf` |
| Final test executable | `b893a87d48dee060dbb166fde27eb587e6322587ab1313cfdadfb49c9cb2ef20` |
| Final application executable | `33728f0df9688ed82e8e5e9446465ff98acbef60ca2d5438b1f22de4db1de4bb` |
| Unchanged `FontData.h` | `f1a3121a2707a03a3b2e025c399e68c553ce9498f4b002ec13b18f512e334802` |
| Unchanged generated `ReferenceArtData.h` | `d94cefd9ad69726c267d4674acd66912f4764ee9f88d1c21ecce4ed7befcbac6` |
| Pinned SDL static library used by both test builds | `1e471c6f7a2c14eba9230c44e743e27c5dc68a243308427e5004d4e446db9324` |

`final-captures/provenance.json` has SHA-256
`6a492e9d7dd66c64d9d54c8a9fe5e53cb8364f2cf5a89d5297e29a64c8b64eb7`;
its manifest has SHA-256
`28e4237e553527c3d95f2b898a93d20944e84b418e62b6f9d3d07fa6f15921e0`.
The final CTest log has SHA-256
`d89ba356ced08a3ae7ccc6d80ca8e235147deaff4c005c49644be3385bef5faf`.

Small captions remain thin because they are downsampled from the unchanged
ASCII atlas. Their restored strokes do not all reach the nominal text color;
the measured maxima above make that limit explicit. No size-specific hinting,
Unicode coverage, larger layout type, or physical-display contrast evaluation
is claimed. The original comparison's panel proportions, material rendering,
stretched left wood, rectangular key perspective, and lower-right substitutions
remain. The lack of explicit MIDI Refresh and exact-name inspection also
remains outside this assignment. This is not one-to-one reference matching.

The screenshot states qualify dummy/software execution, not physical MIDI/audio,
native accessibility, held-gesture resize transitions, Windows/macOS, or hardware
renderer recovery. Root owns integration/publication; A39 is to retain the final
corrected gallery separately from A28's unchanged initial gallery.
