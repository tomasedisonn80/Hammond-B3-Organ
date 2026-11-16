# Contact conversion and Lower-material compatibility

**A18, wave 3. Scoped compatibility passes for the recorded inputs.** The
audited changes preserve the nominal dry Engine, musical identities and original
reference package. A newly executed genuine-before/current dry fixture has
identical complete WAV bytes and decoded PCM. This does not establish universal
audio equivalence, a physical model, visual acceptance or a callback deadline.

The [machine-readable receipt](../development/2026-11-16-conversion-material/reports/A18-compatibility.json)
records exact commands, observed timings, source and binary identities, original
file comparisons, all 48 reference-package entries and resource-crop metadata.
The [reproducer](../development/2026-11-16-conversion-material/reports/A18-compatibility.py)
uses standard-library Python and refuses to overwrite an existing report.
Base and audit-time HEAD are `a411268fd498f65c083203137831bf5afed83bd8`, tree
`37e37d8e038675597b4851961ee698168de435d5`, with an uncommitted overlay.

## Source and musical identities

Comparing every original tracked regular file's Git blob against the base finds
**4,120 of 4,124 byte-identical**. The four changed originals at audit time are
`AGENTS.md`, root CMake, standalone CMake and `InstrumentView.cpp`. Newly added
converter/tests/contracts are additive and are not counted as original files.
Later documentation or installation work may change this audit-time inventory;
the receipt retains its exact scope and input hashes.

| Boundary | Observed source evidence |
| --- | --- |
| Default dry Engine | **61/61** original `src/` and `include/` files match. The default preparation still uses the legacy console model and clears optional leakage configuration. ContactBank, source mixing and audio history are unchanged. |
| 91 shared sources | `Types.h` retains 91 sources. Unchanged TonewheelBank and Engine continue the same source histories; note ownership and contact targets do not add a phase reset or velocity-dependent steady gain. |
| 47 sound parameters | All **47 unique compiled descriptor IDs and names** are enumerated in the receipt. ParameterBridge, its header and the independent registry are unchanged. |
| Saved musical state | ControlState/ControlStateIO remain unchanged: canonical `B3CONTROLS4` writing and version 1–3 reading remain present. No transient contact history or presentation field enters saved controls. |
| Plugin identities and behavior | **20/20** original plugin files match. Processor FUID remains `19F9ADC0 533F42B4 B96BD51D 6547E838`; controller remains `0DEE76AB 26BC475A BF64F138 C89FB0E0`. |
| Native input and control semantics | **82/82** original standalone files other than painter/CMake match, including UiModel, session, input, audio and ownership paths. No hit geometry, control count, saved bank, held-note rule or routing state is changed by this slice. |
| Original evidence and tests | **164/164** original test files, **71/71** original data files and **644/644** original example files match. The unchanged PDF retains SHA-256 `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`. |

The CMake diff adds a standalone Lower fixture and supplies the existing native
grid-probe location to converter test discovery. It changes neither compiler
arithmetic flags nor the core/audio target sources. The painter selects only the
Lower surface in the existing active composition; source review of its numerical
field and visual admission belongs to A16/A17.

The two new production Python files import only the standard library and the
unchanged local `contact_switching_io`/`fractional_contact_reference` modules.
AST import inspection of all four modules finds no test/oracle dependency or
direct dynamic import call. A separate search of native runtime source finds no
reference to either new converter module. The converter is an explicit offline
research utility; it does not replace the original kernel or enter native audio.

## Original ContactReferenceTools component

All **48 original payload names and bytes** match the base, as does
`cmake/InstallContactReferenceTools.cmake`. This includes its six tools, four
documents, 36 fixtures, manifest and probes. The existing copy-only preflight,
`EXCLUDE_FROM_ALL` behavior and refusal to merge an existing package are
unchanged. A18 did not perform an installation run. The proposed separate
five-file conversion component requires its own installation/relocation gate.

## Executed dry fixture

Both the genuine preserved renderer and the current build were executed with
the same preserved profile, each into a fresh owned temporary destination:

```sh
../baseline/hammond_render --profile ../baseline/nominal.b3p \
  --output <fresh-before.wav> --frames 8192 --sample-rate 48000 \
  --block-size 64 --seed 0 --drawbars 888000000 --note 60 --fail-on-clip
../build-native/hammond_render --profile ../baseline/nominal.b3p \
  --output <fresh-current.wav> --frames 8192 --sample-rate 48000 \
  --block-size 64 --seed 0 --drawbars 888000000 --note 60 --fail-on-clip
```

Both processes returned **0** with empty stderr, zero clipped frames and zero
clipped channel samples. Complete JSON stdout is retained in the receipt. Peak
was `0.076829910278320312`; RMS was `0.031813211947603344`. Both WAVs are stereo
signed 16-bit PCM, 48 kHz, 8,192 frames. Whole WAV bytes match; the maximum
absolute difference is **0 across all 16,384 decoded samples**.

| Equal before/current artifact | SHA-256 |
| --- | --- |
| Renderer, 172,528 bytes | `928205dc3b31e57faa7664cb39e691659d1c7f7430b5555ade70b4a9830835bf` |
| Nominal profile, 4,545 bytes | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| Complete WAV, 32,812 bytes | `35a460e99da4c9354e23ec13bb53a70c99f5cd5b70ecf337ec3926c422c7025d` |
| Decoded PCM, 32,768 bytes | `5ce533bce565ede2bd3e2744a1f3cd97aead5c8cd456f762d7dfb0e511e95f9c` |

The original newly rendered WAV bytes were compared and hashed before removing
only A18's owned temporary directory. Raw WAVs are not retained. The source
identity argument and this one-note fixture are separate findings; neither is
a universal or physical sound claim.

## Lower-painter resource boundary

Independent source inspection confirms the existing raster's boundary function
clamps the field's row and column endpoints to the physical visible intersection
before its loops. The Lower field has 127 columns, one fixed **128-int edge
array**, and small fixed channel values. The grain loops visit exactly
**2,304 pairs / 4,608 marks / 9,216 mix calls** without retries or viewport-sized
storage. Their phase remains anchored to canonical coordinates.

The admitted drawing-primitive ceiling is **`127*R + 4608`**, where R is visible
inset rows. The contract's `R <= 4028` gives **516,164 primitives** at its
maximum geometry; independent binary32 mapping at height 8,192 and renderer
scale 2 gives 4,022 unclipped rows. A 64-row output crop has the conservative
ceiling **12,736 primitives**. The measured ABI uses four-byte C ints, so the
edge array is 512 bytes on that ABI. This is not a compiler stack measurement,
an SDL allocation result or a bound on the entire application painter.

The genuine-before and current Lower fixture were each run for cases **24, 25
and 26**: logical **8192×8192**, output **64×64**, renderer scales **1, 1.5 and
2**. All six processes returned 0 with empty stderr and exactly 16,384 RGBA
bytes. Before/current metadata, including copied controls and renderer state,
matches for each pair. Observed process times include startup and the complete
fixture paint:

| Case / renderer scale | Before seconds | Current seconds |
| --- | ---: | ---: |
| 24 / 1 | 0.163215 | 0.100906 |
| 25 / 1.5 | 0.412898 | 0.288931 |
| 26 / 2 | 0.241892 | 0.301481 |

Each is a single process observation under concurrent session activity. These
values are not a benchmark comparison, performance regression decision or frame
deadline. The crops contain no protected exterior pixels, so they do not prove
external pixel containment. A17 owns that full paired comparison. SDL/internal
allocation, physical high-DPI rendering and audio callback deadlines were not
instrumented here.

## Scope and next gates

This review binds painter
`45b710a9c207f456701732f55ec1086487d63bdb9a8b6ed995f4de12cd5bdb10`,
numerical converter `77d48ab503daf4ebaf89e1195685d0a78957989ce7fe67e8881c68928ea81c93`
and CLI `604eae2c20fd4fc0e7f9d8604558f6d196cc808c7451642d963323bee3b90e6f`.
Those production sources and the frozen Lower fixture stayed unchanged during
the audit. The receipt names both actual resource-fixture executables.

The frozen right-strip sampling failure remains open and unwaived by this
review. Root must collect separate numerical/native-grid/resource adversary,
transactional CLI, new installation, full paired raster and actual-gallery
acceptance, followed by coherent build/test and exact published-source hosted
qualification. No broad suite or build ran in A18. Literal whole-interface 1:1,
physical calibration, native semantic accessibility, real devices and live
callback qualification remain distinct requirements.
