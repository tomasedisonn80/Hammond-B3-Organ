# Waveform material acceptance

**Independent result: pass for the frozen paint slice identified below.** A15
qualified the [accepted drawbar/key-front design](../WAVEFORM_UI_DESIGN.md)
against the actual before and after painters and native application captures.
Every observed material delta remained inside an original drawbar slot/cap
allocation or an idle natural-key front. Flat and hidden Play comparisons were
unchanged. This report does not qualify UI timing, physical displays/devices,
the other session's header work, or literal equality to the reference art.

Actual worker: `/root/w03_a15_material_acceptance`, wave 3, 14 November 2026.
The [assignment note](../development/2026-11-14-waveform-continuation/notes/A15-material-acceptance.md)
records ownership, execution and continuation.

## Exact source and setup

The before painter is byte-identical to `apps/standalone/InstrumentView.cpp`
at published `26ff2fbe66a50260bd7601cbfa54c1f5d35ff3a8`. The after painter was
copied before testing and its SHA-256 matched the integrator's accepted slice.
The inspected source diff contains only drawbar material layers/front depth and
the idle natural-front palette. No header, geometry, input, font, Drawing API,
audio, parameter or state implementation was edited by A15.

| Input | SHA-256 |
| --- | --- |
| Frozen before `InstrumentView.cpp` | `428f74c4b2aae72e1ee048d1fa878575d0cd2edc064b1a3865ba40c446c30da2` |
| Frozen after `InstrumentView.cpp` | `6570c97f1c62b555a1df3477954514e379d61165a36cf20f879dea5151ff866b` |
| Independent acceptance test | `1060ee4c062bb129ba58c082cc98921e478a7221a287acc4022401e41b13b81c` |
| Shared `Drawing.cpp` | `9b788234405964f6675ab43428735e425b460c8045f2c6eb064c9e19b40a0a5f` |
| Shared `Drawing.h` | `749e718436e61ad4a13a28e167c4b07e4dd789adf213a6229a503fc1f2bcf188` |
| Shared `UiModel.cpp` | `49c68995aad96aa5e316613412c93931a1082d0e4a3ad3758ac63484af963064` |
| Shared `UiModel.h` | `d94e90be25812c6d21b61f37f2b0547704d14866c45fbbb21131ec70b6389bd3` |
| Embedded font data | `f1a3121a2707a03a3b2e025c399e68c553ce9498f4b002ec13b18f512e334802` |
| Generated reference-art data | `d94cefd9ad69726c267d4674acd66912f4764ee9f88d1c21ecce4ed7befcbac6` |
| Original reference JPEG | `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187` |

Execution used Linux x86-64, kernel `6.18.57`, glibc `2.41`, GCC
`14.2.0` (Debian `14.2.0-19`), C++20, `-O3 -DNDEBUG`, and the existing pinned
SDL **2.32.10** static build. Strict project warnings, including conversion,
sign-conversion, shadow and `-Werror`, passed. The comparator uses SDL software
surfaces with `SDL_Init(0)`; it opens no window/audio device. The separate actual
application runs explicitly selected dummy video/audio and software rendering,
MIDI disabled, 48 kHz stereo float and 512-frame buffers.

Both painters linked these same existing archives, without rebuilding or
substituting their implementations:

| Archive | SHA-256 |
| --- | --- |
| `libhammond_standalone_drawing.a` | `06cde97b0ae59acac7b44437df920b3d12773b20004abedcda101d8da9a7ed36` |
| `libhammond_standalone_support.a` | `14cdc87f1119b7d7bda9a0adc79a60bfdfca91e48a799d0c23424596c52311f2` |
| `libSDL2.a` | `55ccb40daeebf75e429c7d8c693cdd5b4e2207a00393e35c66be992e752b03ed` |
| `libhammond_core.a` | `2e60507a07753f9d54b9451c13fe882a27fd4d8c1b82186a40afed360d787f24` |

## Independent method and coverage

The retained [test](../../apps/standalone/native_tests/test_standalone_waveform_material.cpp)
has a portable ordinary mode measuring only the new targets. Its optional
`HAMMOND_WAVEFORM_BASELINE` build links a second translation unit compiled from
the exact frozen before source, renaming only `paint_instrument`,
`audio_overlay_layout` and `midi_overlay_layout`. Both versions paint the same
copied model and fixed status through the same Drawing object and dependencies.
No live callback counter participates in this comparison. There is no excluded
header band or exemption for another session's changes.

The containment oracle evaluates long-double half-planes on public vertices at
output-pixel centers. It never calls `UiQuad::contains`, `ui_hit_test`, Drawing
span/raster helpers, or the production key-band/inset helpers. Rectangular bounds
only limit iteration; they do not admit a point outside a key quad. Natural
then accidental hit-quads establish visible ownership, so an accidental cannot
be excused by the front of a natural underneath it. Held natural fronts are
excluded from the permissible change mask. Drawbar allocations are independently
derived from the published track/control dimensions and unchanged cap contract.

| Cases | Executed coverage |
| --- | --- |
| 36 Dimensional Play states | All three sizes × scales 1/1.25/1.5/2 × values 0/4/8; all twenty visible drawbars, including brown/ivory/black manual caps and both brown mixtures |
| Three audition states | 1672×941, 1280×900, 960×700; Upper B `888000000`, Lower B `008000000`, pedals `80`, one held Upper key |
| Sixteen clipped/offset states | Minimum size at all four scales; focused held manual natural/accidental and focused idle pedal natural/accidental; 11-pixel viewport offsets; physical clips at scales 1/1.5, logical clips at 1.25/2 |
| Twelve additional Flat Play states | Minimum size × all four scales × values 0/4/8; exact before/after equality |
| Twelve additional non-Play states | Rotary/Service × Dimensional/Flat × all three sizes; exact before/after equality |

The 36-state matrix holds Upper and Lower indices 24/1 and pedal indices 12/13
(natural/accidental respectively). Cap focus is brown at scale 1, ivory at 1.25,
black at 1.5 and mixture at 2. Every family/value/scale is painted; every family
is focused at its stated scale. This is a bounded matrix, not a claim that every
possible focus/control/clip combination was exercised.

## Observed results

The final frozen comparison passed **79 pairs / 158 rendered frames**, with
**149,100,628 pixel comparisons** and **zero escaping deltas**. Its 5,382,830
changed pixels comprise **2,963,899 drawbar-allocation pixels** and
**2,418,931 idle-front pixels**. Every visible idle natural front and all twenty
drawbars changed in each full Dimensional frame. All **18 Flat pairs** and
**12 non-Play pairs** were byte-identical; those groups overlap in six cases.
Original top faces, held/accidental paint, labels, values, focus, presets,
header, wood, cabinet and other paint therefore retain their original pixels
outside the expressly allowed material regions.

| New measurable target | Before | After / result |
| --- | --- | --- |
| First Upper stem, x `[103,119)`, rows 350/365/380, encoded-RGB Y′ > 25 | 3 / 3 / 3 pixels | **9 / 9 / 9**, within 7–10 |
| Upper idle natural front, x `[708,715)`, y `[677,682)` | Median **159.0608** | **129.9874**, 29.0734 levels darker and within 125–140 |
| Adjacent top, x `[708,715)`, y `[653,658)` | Median **240.8184** | **240.8184**; all top pixels also covered by exact containment equality |
| Cap face/front join | Previous shallow front | **780** observed joins within one logical pixel of the independently calculated 7-unit manual / 6-unit mixture front |
| Exposed shaft body/edge | Narrow original strip | **830** exposed cross-sections meet width, narrow bright-edge and dark-body thresholds |
| Idle front center band, both ends of every division | Original lighter palette | **234** geometry-derived patches pass, including short minimum-size pedal fronts |
| Clip/viewport preservation and surviving focus | Same caller state | **16** cut focused states pass; zero paint outside the caller clip |

Y′ is `.2126R + .7152G + .0722B` on encoded RGB, not linear-light luminance
or a physical reflectance measure. The reference-art front anchor remains
119.48 under the accepted design; the new measured native anchor is about
10.51 levels away. These local samples do not establish whole-image similarity.

The final ordinary test passed **55 frames / 1,917 assertions** in **7.199 s**;
the optional comparison passed **2,219 assertions** in **19.896 s**. These are
whole test-process durations, including raster examination, and are **not**
the separately required 30-warmup/300-draw UI performance experiment. An initial
test compilation caught two baseline-only unused helpers; conditional
compilation corrected that fixture issue. No raster assertion or product repair
was needed. A prior comparison of the same assertions also passed; the final
rerun qualifies the final test's explicit baseline-mode reporting.

Compact final comparison record:

```json
{"cases":79,"frames":158,"checks":2219,"failures":0,"compared_pixels":149100628,"changed_pixels":5382830,"drawbar_changes":2963899,"idle_front_changes":2418931,"escaped_pixels":0,"flat_pairs":18,"hidden_pairs":12,"cap_joins":780,"shaft_sections":830,"front_patches":234,"focused_clips":16,"baseline_comparison":true}
```

## Actual native executable captures

Eight fresh actual processes completed smoke, screenshot, held-note observation,
release observation and shutdown successfully. Before executable SHA-256 is
`0ef37dd5a0501da08df302027b31791b7917705e00cb32017b035a145ceb3811`;
after is `677acfa6a0244d3f7085eb96fa0737306a9f9e74febabb34f55fea99b303c51c`.
The after binary was copied before running and matches the integrator's binary.
Each run used the existing audition registration and `--smoke-ms 1000`.

The native before/after pairs were also checked separately with long-double
half-planes from the public geometry, with accidental occlusion and held Upper
index 24 excluded. Actual app deltas were **75,180 / 72,931 / 32,654** at the
three sizes, respectively, with **zero escapes**. The actual minimum Flat pair
has **zero changed pixels**. These app-frame counts are separate from the fixed
surface comparator's counts; each captured application pair was graded directly
against its own pixels. The isolated front/top/stem anchors
match the fixed-surface values above.

| Lossless actual application PNG | SHA-256 |
| --- | --- |
| Before 1672×941 | `7f81ae88ba26fd757b465d7fa9ded630b58d062eca45f91b4f021fd6c9ed91d3` |
| After 1672×941 | `e46ea2a4418b6131550cf1b1d2eb0a8754b191eaab5d0410e990cbc98756b439` |
| Before 1280×900 | `027b133d0a9fe88dd7fd3341a0e2cdafb15b228d188b1cff54a143acbbb641f4` |
| After 1280×900 | `6a92200bef4f1176fe7d0f5c194cc69252d2d09363644d6158eefbf8395c8642` |
| Before 960×700 | `4cfccb416cef6bbb07279fdcc161afc8b647c2abe20bdd0f439ab2ddb26db2e4` |
| After 960×700 | `de1127d98f0e7cca8e0f8542d5ab238f78f0725fc8e583ca8ea04f82838136f3` |
| Before and after Flat 960×700 | `aeba6e5af7a5e454bd0e3fc2066b5933bc76dded6258b76d11633aac97ffecae` |

A15 viewed the original reference, both supplied reference-size application
PNGs and the fresh default/minimum/Flat after captures. The reference-facing
improvement is localized and visible. Cap silhouette, projection, key counts,
layout, lighting, typography, texture and functional inventory still differ from
the concept. Full reference equality remains unmet.

## Reproduction and retained evidence

Working directory was
`/workspace/scratch/e3cacb90cc81/Hammond-B3-Organ`. Reused libraries are under
`../build`; the existing pinned SDL source is
`/workspace/scratch/1bb6ee17ad7e/SDL2`. All large captures, frozen copies,
command arrays and raw logs remain in sibling `../a15-material/`; root owns the
later coherent gallery. The compact results and input hashes are retained here.

The integrator owns CMake registration for `test_standalone_waveform_material`:
its sources are the assigned native test plus `InstrumentView.cpp`, linked to
`hammond_standalone_drawing` and `hammond_standalone_support`, with
`SDL_MAIN_HANDLED`. Its ordinary target needs no historical source. Subsequent
CTest invocation is:

```sh
ctest --test-dir ../build -R '^test_standalone_waveform_material$' --output-on-failure --no-tests=error
```

A15 executed direct strict compilation/linking, rather than changing shared
CMake or running the integrator's aggregate. Exact command argument arrays are
in `../a15-material/compile-commands.json` and `link-commands.json`. To reproduce
the optional comparison, recover the before source with `git show
26ff2fbe66a50260bd7601cbfa54c1f5d35ff3a8:apps/standalone/InstrumentView.cpp`,
verify its hash, and compile it with only these symbol definitions:

```text
-Dpaint_instrument=paint_instrument_before
-Daudio_overlay_layout=audio_overlay_layout_before
-Dmidi_overlay_layout=midi_overlay_layout_before
```

Compile the test with `-DHAMMOND_WAVEFORM_BASELINE`, compile the hash-verified
after painter normally, and link both objects with the shared archives listed
above, `-lm -pthread`. Optional `--capture-dir EXISTING_DIRECTORY` saves the
three fixed audition before/after BMP pairs. The exact frozen after source is
required; a later integrated header revision is a different input and must not
be excused by weakening the comparison mask.

| Final executed evidence | SHA-256 |
| --- | --- |
| Comparator executable | `b9c61f57d8b51e39ab8249ea9a07da28129c4d89f8a0583e4c53747b30242ff8` |
| Ordinary executable | `16a56d1639fe6d4918a3851c7b8382ce080c42980f511bdf29078de19cea50e8` |
| `baseline-final.jsonl` | `bd08461618478920ddc2d8fe7721f8dd7864cc16111a1428db91b338c0478dfe` |
| `default-final.jsonl` | `042e31843f0d32d19705cdcca22e3ac05750958609221732c1cedfd0d617f257` |
| Public geometry used for separate application masks | `e0917c6964c09f1264a12ca41dd34287873e52a308c51573cb4c0e8b222fe0ab` |

No existing geometry, material, contrast, held/focus or rejection gate was
changed. Root's earlier six-suite pass is separate author evidence; A15 did not
relabel it as an independent rerun. Root's coherent native suite, timed paint
experiment and final integrated gallery are the next checks. This acceptance
does not establish physical DPI/device behavior, accessibility, new sound,
connected rotary audio or completion of M9.
