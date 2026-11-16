# Native apron gallery — thirteen actual views

These are actual screenshots of the rebuilt native `hammond_standalone`, captured
on 16 November 2026 with SDL dummy audio/video and the software renderer. All
thirteen processes passed the schema-3 replay, state, painted-frame and shutdown
checks. The original twelve capture cases retain their order and inputs; the
explicit `play-wide-1920x1080` case is appended for the apron contract's large-size
inspection. Historical galleries and their manifests remain unchanged.

![Actual native application at 1672 × 941](images/play-reference-1672x941.png)

## Views

| Actual view | Dimensions | PNG |
| --- | --- | --- |
| Dimensional Play, reference | 1672 × 941 | [Open](images/play-reference-1672x941.png) |
| Dimensional Play, default | 1280 × 900 | [Open](images/play-default-1280x900.png) |
| Dimensional Play, minimum | 960 × 700 | [Open](images/play-minimum-960x700.png) |
| Service, reference | 1672 × 941 | [Open](images/service-reference-1672x941.png) |
| Service, minimum | 960 × 700 | [Open](images/service-minimum-960x700.png) |
| Rotary, reference | 1672 × 941 | [Open](images/rotary-reference-1672x941.png) |
| Rotary, minimum | 960 × 700 | [Open](images/rotary-minimum-960x700.png) |
| Flat Play, minimum | 960 × 700 | [Open](images/flat-minimum-960x700.png) |
| Dimensional Play, minimum active | 1400 × 820 | [Open](images/play-minimum-active-1400x820.png) |
| Flat Play, reference | 1672 × 941 | [Open](images/flat-reference-1672x941.png) |
| Dimensional Play, toolbar focus | 1672 × 941 | [Open](images/play-toolbar-focus-1672x941.png) |
| Dimensional Play, pedal focus | 1672 × 941 | [Open](images/play-pedal-focus-1672x941.png) |
| Dimensional Play, wide | 1920 × 1080 | [Open](images/play-wide-1920x1080.png) |

## Reproducible inputs and identity

The retained [controls](inputs/controls.b3controls) and six `.b3uireplay` files in
`inputs/` hold Upper notes 60/64, Lower note 67 and pedal 3 while editing the
retained Upper B 16-foot drawbar from 7 to 8. The two focus scenes add their own
fifth held target. The application writes no saved controls during capture.
The gallery records this established diagnostic scene; it does not demonstrate
importing the separate proposed registration pack into a native browser.

The [provenance](provenance.json) retains each exact command, environment,
diagnostic validation, native BMP identity, PNG identity and decoded pixel
identity. [Manifest](manifest.json) pins 61 payload files totaling 6,619,107
bytes, excluding itself and this subsequently authored review. Each BMP was
converted losslessly and then removed only after its PNG decoded to the same
mode, size and bytes. Original BMP bytes are therefore unavailable; their sizes
and hashes remain in provenance. No app screenshot was synthesized or composited.

| Identity | SHA-256 |
| --- | --- |
| Native executable | `82c6a9ffa056852b80d5505dec19aaec72f83965953d765bbee388cc8b1293c8` |
| Production input inventory | `7d6671ecd79e7f44e0727a7f4399721358b9345f3b00bce9d4af4fa72ad4e810` |
| Build input inventory | `b8b15531794d91f47c446203d72bcf7ef58707f2b3195169dd4c856a2e830ec3` |
| Capture provenance | `de60b735f3c91dadddaf461bb78d6dd3ad060a922c8e475b1499cdee189d3d2c` |
| Capture manifest | `a403767e0863f7aacf4c900ef24e289b582b2e5d0c108b97ecd64cb7fe18115b` |

All recorded executable/source/build/configuration/input/tool/report identities
were unchanged from capture start to finish. Git HEAD stayed
`54df95fe343d417dd89bb7a91f85e4f51c08dfe7`, committed tree
`b221dc8b565f5da04c7ad1fabc1d4d605f27b97e`; the recorded production overlay,
including untracked inputs, identifies the captured program more precisely than
HEAD alone. The copied [source qualification](inputs/source-qualification.json)
pins seventeen named sources and links, by repository-relative identity, to
root's completed build evidence. All 145 production inputs present in that
build report still matched; the three additional inventory entries are explicitly
listed. The capture utility observes these identities and does not independently
attest compilation.

From the repository root, reproduce into a **new** output directory:

```sh
python3 -B tools/capture_standalone_interface.py \
  --exe ../build-native/apps/standalone/hammond_standalone \
  --source-root . --build-root ../build-native \
  --source-qualification docs/design/native-gallery-preset-v1/inputs/source-qualification.json \
  --expected-exe-sha256 82c6a9ffa056852b80d5505dec19aaec72f83965953d765bbee388cc8b1293c8 \
  --output docs/design/native-gallery-preset-recapture --dummy-sdl
```

The command requires the named source/build identities; later changes require a
fresh source qualification. Runtime frame counters and meter values may differ
between runs. This live gallery is distinct from the deterministic
[25-case genuine paired admission](../../development/2026-11-16-preset-library-continuation/reports/apron-paired-final.json).

## A31 visual observations and limits

A31 inspected the full reference, minimum-active and 1920 × 1080 PNGs against the
[unchanged atlas concept](../atlas-cover-reference.jpg), plus the genuine
pre-change reference capture. The apron now shows the reference's irregular dark
wood grain around and below the live footer. No new gap or obvious join was
visible at its outer bounds in those three images. The thin bright upper edge
remains visible, and the live black footer occupies the central area. Status,
unsaved cue and meter remain visible; the baked `DESIGN CONCEPT` lettering and
its central ornament are absent.

Concrete remaining issues: the minimum-active footer text and top-right action
labels are very small; scaling compresses their fine strokes. The footer's dark
rectangle remains visually prominent. Across the full window, button/cap
shading, manual key depth and typography differ from the concept. These images
do not close literal whole-interface 1:1. Independent review is separate from
this capture-author observation.

The [apron contract](../REFERENCE_APRON_CONTRACT.md) governs this narrow surface.
Dummy-SDL capture supplies no hardware, real display/DPI/input, callback deadline,
native accessibility or measured instrument qualification. The source JPEG stays
byte-identical at SHA-256
`9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187`;
its original provenance and rights classification are unchanged.
