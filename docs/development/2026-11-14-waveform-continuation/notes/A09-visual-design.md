# A09 — Bounded native material refinement design

- Actual worker: `/root/w02_a09_visual_design`; wave 2, 14 November 2026.
- Owned outputs: this note and `docs/WAVEFORM_UI_DESIGN.md` only.
- Delivered [implementation-ready design](../../../WAVEFORM_UI_DESIGN.md):
  deepen drawbar recess/stem/cap separation, then darken idle natural-key fronts.
  Product edits, builds, test execution, app launches, shared-doc edits, commits,
  publication and nested workers were not performed.

## Read and inspected

Read `AGENTS.md`, complete `PLAN.md`, `ATLAS_REVIEW.md`, current waveform
scope/checkpoint/manifest, README, current status/next steps/latest log,
waveform A05/A06 readings, existing reference layout/material contracts,
`InstrumentView.cpp` material/key/header/layout callers, `Drawing.h` and its
text/raster implementation, `UiModel.h` and geometry generation. Inspected
existing material-acceptance and native target declarations to avoid inventing
test entry points. These source inspections are not executed acceptance.

Viewed both original complete 1672×941 files directly: exact reference JPEG and
`/workspace/scratch/e3cacb90cc81/baseline-ui/play.png`. Inspected baseline identity
and diagnostics. A09 recomputed hashes and measured original decoded pixels with
Python/Pillow; no image was edited or substituted for native output.

Initial HEAD/local origin were `2e161dc3a60fc3442051799574feed37bffbfc5c`, tree
`17f8e4d698f903c37bff09deee196ea73e0da108`. Root integrated concurrent records
during this task; subsequently observed HEAD/local origin
`26ff2fbe66a50260bd7601cbfa54c1f5d35ff3a8`, tree
`530d5fcf777003f470f64558de9e5631d31a21a4`. A09 did no fetch or integration.
The product source hashes below remained the inspected baseline. Existing
staged/unpublished files were preserved.

| Inspected input | SHA-256 |
| --- | --- |
| Reference JPEG | `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187` |
| Current native baseline PNG | `21da0d6340b408231d2080b8ab888907bb0d4aa58c98599908a2a0cf4252213a` |
| `InstrumentView.cpp` | `428f74c4b2aae72e1ee048d1fa878575d0cd2edc064b1a3865ba40c446c30da2` |
| `Drawing.h` | `749e718436e61ad4a13a28e167c4b07e4dd789adf213a6229a503fc1f2bcf188` |
| `Drawing.cpp` | `9b788234405964f6675ab43428735e425b460c8045f2c6eb064c9e19b40a0a5f` |
| `UiModel.h` | `d94e90be25812c6d21b61f37f2b0547704d14866c45fbbb21131ec70b6389bd3` |
| `UiModel.cpp` | `49c68995aad96aa5e316613412c93931a1082d0e4a3ad3758ac63484af963064` |
| A36 visual review | `5d696f9aba17a8c1ec8dcd9f61bd8a4772af438de38e2be11762a604c87c0850` |

## Findings and ownership adjustment

The previous layout/material pass is already in the live product. Upper key depth
is already 144.12; the visible remaining depth gap comes from optical treatment,
not permission to resize keys. The original 3.5-unit shaft rasterizes as three
bright pixels in the measured baseline. Its dark surround and short cap front
read as a flat slider; a broader dark body with a narrow edge and a 7-unit manual
cap front can improve the reference relationship inside the current footprint.

Seven 7×5 unobstructed upper key patches were sampled at x beginnings
`699,708,750,777,816,852,925`, top y653–658 and front y677–682. Native medians were
uniformly **240.82 top / 159.06 front**; reference tops were **236.40–242.69** and
fronts **107.49–125.36**. The stable top and lighter native front support changing
only idle front color. They do not establish a global similarity or physical
material measurement. The contract uses the x708 patch as its explicit anchor.

Root notified A09 that concurrent reference-session A40/A41 owns wide-header
typography. A09 then read [the integrated A36 review](../../../reviews/REFERENCE_REFINEMENT_VISUAL.md)
and excluded all header/heading/font edits. Wood/panel/cabinet layers remain
unchanged. This preserves disjoint function ownership while recording those
remaining appearance gaps. The initial prioritized recommendation and ownership
adjustment were sent to root before document completion.

## Reproduce the pixel measurements

Run at repository root with Python and Pillow; original images are read only.
The baseline sibling path is local evidence and must be retained or replaced by
the exact PNG bytes before reproducing. Coordinates are half-open, and Y′ is
computed directly from encoded RGB rather than linearized luminance.

```python
from pathlib import Path
from PIL import Image
from statistics import median
import hashlib

paths = {
    "reference": Path("docs/design/atlas-cover-reference.jpg"),
    "baseline": Path("../baseline-ui/play.png"),
}
level = lambda p: .2126*p[0] + .7152*p[1] + .0722*p[2]
for name, path in paths.items():
    im = Image.open(path).convert("RGB")
    print(name, im.size, hashlib.sha256(path.read_bytes()).hexdigest())
    for x in (699, 708, 750, 777, 816, 852, 925):
        values = [median(level(p) for p in im.crop(box).get_flattened_data())
                  for box in ((x,653,x+7,658), (x,677,x+7,682))]
        print(x, [round(value, 2) for value in values])
    if name == "baseline":
        print("stem widths", [sum(level(im.getpixel((x,y))) > 25
              for x in range(103,119)) for y in (350,365,380)])
```

Observed stem widths were `[3,3,3]`; the x708 native/reference values were
`[240.82,159.06]` / `[242.40,119.48]`. The design sets after targets, not after
results. It separates fixed-state raster containment, real application captures,
unchanged control/ownership behavior and same-geometry UI timing. Root owns
implementation assignment, acceptance, actual README captures and publication.
R4/R5/R6, musical semantics, real-device/deadline/accessibility and literal 1:1
visual equality remain separate gates.
