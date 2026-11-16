# A31 — keyboard rim pre-implementation admission

**16 November 2026. Decision: admit the bounded source/pipeline proposal and
`keyboard-rim-art-v1.1` fixture for a genuine pre-rim baseline. Candidate acceptance
remains a later, separate decision.** Root must preserve the baseline before any
rim production edit. A31 changed no production source, original artwork, existing
fixture or shared build configuration.

## Bound identities

| Item | Frozen SHA-256 |
| --- | --- |
| [Original A26 proposal, exact bytes](../development/2026-11-16-conversion-material/reports/A31-proposal-before-admission.txt) | `4b06e9d293040ce88082a718f01c7415cd793ec74f38cc5bf1d01bc61ceeaebf` |
| [Admitted contract](../design/KEYBOARD_RIM_CONTRACT.md) | `a56206a3ca326b2bc745055f91f8b61bd1930874113b25bc31c55b816e43581d` |
| [Exact new manifest, 2,436 bytes](../development/2026-11-16-conversion-material/reports/A31-keyboard-rim-manifest.json) | `0c13739aa8e16da1c0d3a1b80c2626319ce61e5c3de7202fe33b3442939532cc` |
| [New native fixture](../../apps/standalone/native_tests/test_standalone_keyboard_rim_raster.cpp) | `d860e19665bd806b5ef05770ecbb89109f79d782cc31d4e3341e9d825d5011ad` |
| [Independent matrix and source operations](../development/2026-11-16-conversion-material/reports/A31-rim-matrix.json) | `40de797843e868a83f6dca9f2e281d79e75cca0677e4f3a4687acbfc0e45d6b1` |
| Pre-rim T1 painter at admission | `a88e7576700ae306769849ceda36993969a61e848c015ba4fb98fa9c4a7e8cfa` |
| Unchanged Drawing.cpp | `9b788234405964f6675ab43428735e425b460c8045f2c6eb064c9e19b40a0a5f` |

The compiler owner copies the frozen manifest byte-for-byte to the admitted
asset directory and pins its hash. The asset identity stays
`standalone-keyboard-rim-decoration-v1`; the contract/fixture minor version records
the independently disproved clipping premise. These identities precede the rim
candidate. The root baseline receipt must bind actual binaries, generated headers,
complete linked-source identity, build options and SDL library, rather than
substituting this design admission for executable evidence.

## Source, extraction and decorative scope

A31 independently hashed the PDF, original JPEG, full decoded RGB, exact crop and
deterministic gzip. The [source receipt](../development/2026-11-16-conversion-material/reports/A31-source-identities.json)
also records the original compiler, manifest and three blobs to preserve.

| Input/payload | Checked identity |
| --- | --- |
| PDF | `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769` |
| Original 1672×941 JPEG, 412,664 bytes | `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187` |
| Full decoded RGB | `07a7e35a2fd6610d623bbc1da8c995f3f4d95c4b45a0a5c1f41ad1395584bbeb` |
| RGB24 crop, 57,996 bytes | `dda0291836a4f3b9a5569b0ed29badc7b02d723db8409c9447a1374450c7472a` |
| One-member gzip, 34,422 bytes | `91055667f153c277ee693e3b9e14515738c0f0640a96955c809f245c7f22ad83` |

The source rectangle is `[48,1122)×[510,528)`, 1074×18, pitch 3222. Actual authoring
versions match the proposal: Python 3.12.14, Pillow 13.0.0, libjpeg API 6.2,
libjpeg-turbo 3.2.0 and zlib compile/runtime 1.3.2. The gzip header is
`1f8b08000000000002ff`. Extraction uses the untransformed loaded RGB image and an
integer crop; it does not resample, retouch, color-adjust or composite.

A31 inspected the complete original image and complete actual T1 app images at
1672×941, 1400×820 and 1920×820. The crop contains the cheek shoulder, the slanted
join near x232, polished crest and recess. It has no text, tablets, keys or live
controls. The original is generated concept artwork, not measured organ material
or an app capture. The existing publication-rights gate remains open. The three
earlier artwork inputs, their pipeline and the exclusion of baked controls and
plinth lettering remain unchanged.

## Concrete failed premise and admitted correction

The [single-file experiment](../development/2026-11-16-conversion-material/reports/A31-sdl-copy-preflight.cpp)
uses the exact raw crop, RGB24/static texture, one upload, blend NONE, linear
scale mode, and one `SDL_RenderCopyF`. It links only the existing pinned SDL
static library, not application production objects. It reproduces all twelve
proposed edge clip geometries with their declared physical/logical installation,
scales and origins. Full and clipped renders are independent. Direct physical
surface rows are compared after render completion.

The [build receipt](../development/2026-11-16-conversion-material/reports/A31-preflight-build.json)
records GCC 14.2, the shared native target's warning/optimization/include flags,
exact compile/run argument arrays, executable hash and SDL 2.32.10 commit
`5d249570393f7a37e037abf22cd6012a4cc56a71`. The linked static library hash was
`99c128d680ca704056dc09ff3b47c8f5374485e98f1202e687ceb9770002849b`.
Compilation and execution both returned zero; the disproved premise is retained
as measured data, not concealed behind the process exit code.

| Edge | Scale 1 differing interior pixels | Scale 1.5 | Scale 2 |
| --- | ---: | ---: | ---: |
| Left | 0 | 15 | 33 |
| Right | 0 | 30 | 36 |
| Top | 0 | 1,536 | 2,128 |
| Bottom | 0 | 1,573 | 2,053 |

The [corrected physical-readback result](../development/2026-11-16-conversion-material/reports/A31-sdl-copy-preflight.json)
contains **7,404 interior differences**, with **zero caller-exterior changes in
all twelve cases**. All four unscaled copies agree exactly with their full
companions. `SW_QueueCopy` truncates scaled destination components;
`SDL_PrivateUpperBlitScaled` clips source and destination proportionally and
rounds source bounds before scaling. Its unscaled branch instead directly blits.
Root independently reviewed the actual data and these SDL source paths before
admitting this correction.

The initial experiment incorrectly used viewport-relative
`SDL_RenderReadPixels(nullptr)` to populate a full-output-sized array. Its
[source](../development/2026-11-16-conversion-material/reports/A31-sdl-copy-preflight-v0-invalid-readback.cpp)
and [invalid counts](../development/2026-11-16-conversion-material/reports/A31-sdl-copy-preflight-v0-invalid-readback.json)
remain retained. Those counts are **not evidence for the renderer conclusion**.
Replacing that readback with locked physical backing rows resolved its spurious
exterior failures; it did not remove the real scaled interior differences.

Admission therefore retains the single-texture/single-copy proposal while
explicitly recording pinned SDL's scaled clipped sampling. Full-scene companion
differences are reported because unchanged scaled images/glyphs may also exhibit
this behavior. Same-clip repeats must remain exact. The following requirements
are not relaxed: exact raw transport, exact canonical isolated copy, exact
canonical unoccluded ROI, zero paired changes outside independently derived
operation support, zero caller-exterior changes, unchanged opaque foreground,
cyan focus, complete state/layout and live behavior. No changed-pixel mask,
whole-panel allowance or global renderer change is admitted.

## Independent rim and retained-shadow reconstruction

The [reproducer](../development/2026-11-16-conversion-material/reports/A31-rim-shadow-preflight.py)
reconstructs old wood gradients/stripes, pixel-center rounded shadow spans and
pinned SDL's separately truncated source/destination integer alpha products.
It consumes only the original JPEG and the actual pre-rim canonical app PNG;
it does not call production painting helpers or read a candidate image.

The [result with all 18 row profiles](../development/2026-11-16-conversion-material/reports/A31-rim-shadow-preflight.json)
matches **all 19,332 actual pre-rim RGBA pixels exactly**, with zero mismatch.
The consumed actual PNG hash is
`a5c39b07aec1bbf6e49cc2cc0617bdef678c0f221fa650017f03dff0974c467e`.
This validates both the source-derived coverage and the distinction between
the replacement payload and later composition.

The unoccluded ROI `(48,515,1073,10)` has 10,730 pixels and zero later shadow
coverage. Across the whole band, 11,420 pixels have no shadow and 7,912 have one
or more layers. The layer histogram for counts 0–6 is
`11420,1961,1934,1935,1040,1038,4`. Rack shadows end at y515; upper-manual shadows
start at y525; the cabinet shadow reaches x1121. The ROI excludes these boundaries.

The predicted future 19,332-pixel composed RGB band has SHA-256
`477864c7f452b622e1d6e4caa6faf5c8b47fdd182bb5209d7fac55eb9df90590`.
This is **a frozen prediction, not candidate evidence**. It predicts 7,912
source differences at retained shadow boundaries. The future independent checker
must verify actual output and report these differences; the implementer must not
move the rim later in paint order, erase shadows or tune artwork to hide them.
The complete raw/isolated band, unoccluded final ROI and composed full band are
three separate claims.

## Matrix and native/pipeline review

The independent [matrix reproducer](../development/2026-11-16-conversion-material/reports/A31-rim-matrix.py)
declares all 32 cases and computes the old gradient/fill and new-copy supports
from binary32 endpoint mapping and pinned SDL raster rules. It consumes no app
frame. Canonical intrinsic support is 19,332 pixels; the maximum one-device-pixel
envelope is 21,520. The new fixture emits observations and complete serialized
copied model/layout state, never an acceptance mask.

The exact matrix contains 105,280,361 output pixels in aggregate, processed one
bounded case at a time. Maximal 8192×8192 logical geometries use 64×64 centered
resource outputs. The fractional/negative-origin case has output 2105×729,
viewport `[-7,11,2091,707]`, and intrinsic union `[60,382,1343,14]`. Full-scene,
edge, disjoint, enabled-empty, anisotropic, fractional, extreme-aspect, both-manual
focus and canonical/minimum repeat cases are fixed before implementation.
Nonresource outputs include protected exterior. The fixture includes six
independent opaque neighboring probes per full scene and exact cyan-focus outlines.
It does not depend on obsolete pre-T1 footage glyph positions.

Expected structural counts are 32 cases, 53 paint/state restorations, 15 clip
companions, 84 opaque probes, 14 full focused scenes and 4 same/fresh-renderer
repeat comparisons. Root's genuine baseline records actual pixel/check counters
and qualifies all cases before the rim edit. Retained earlier fixtures continue
to supply inactive workspace/presentation/breakpoint and live-label evidence.

The admitted compiler must bound all inputs, verify immutable manifest/source/
gzip/raw identities, reject trailing/multiple gzip members, and publish output
transactionally. The ordinary path stays standard-library-only. The native
addition reuses the unchanged RGB24/static/linear preparation path once, with
separate optional ownership/destruction and exact old procedural fallback.
Texture lifecycle/fault interposition, complete canonical isolated copy and
failed-copy fallback remain required post-implementation native evidence; this
source review does not claim those future tests have already passed.

## Next ownership and remaining gates

1. **Root:** complete the accepted T1/old-fixture transition, wire/build this exact
   source, preserve the genuine pre-rim baseline, source/build receipts and actual
   metadata, and resolve any concrete pre-edit fixture failure before release.
2. **A34:** after that release, copy the manifest exactly, implement the separate
   locked compiler/blob and bounded optional texture, then replace only the one
   admitted rim call with its exact old fallback. Preserve all other pixels and
   behavior, source assets and existing pipeline bytes.
3. **A35:** independently qualify paired frames using source-derived support;
   verify metadata/model, exact protected foreground/focus, canonical source ROI,
   the full predicted shadow composition, repeatability and the explicit scaled
   clipping distinction. Freeze checker criteria before inspecting candidate deltas.
4. **A36/root:** qualify compiler transactions, isolated transport and native
   lifecycle/failure/recreation; inspect complete actual app frames for joins,
   stretching, doubled shadows and contrast; update gallery/README only after
   scoped acceptance and publish coherent source/evidence.

Future agents must preserve this failure history and all frozen input/fixture
identities. A changed input or failed criterion needs a separately reviewed,
pre-implementation correction, not a retrospective tolerance. Literal whole-UI
1:1, physical display/input/DPI, accessibility, audio/host/device calibration,
rights and signed-distribution gates remain open.
