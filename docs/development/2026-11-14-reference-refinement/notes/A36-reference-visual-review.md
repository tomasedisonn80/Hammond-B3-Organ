# A36 — Measured reference and native visual review

Actual worker `/root/w06_a36_reference_visual_review`, wave 6. Read current
standing instructions/scope/checkpoint/manifest, complete M0–M9 plan, reviewed
layout/material contracts and reference provenance. Owned the new visual review,
this note and A36 measurement script/report only. No product/test/build/GUI,
image editing, commit or push occurred.

## Source and method

Directly inspected the original cover/page-409 JPEG and all eight original v3
PNGs. Qualified product is `2e161dc3a60fc3442051799574feed37bffbfc5c`; executable
SHA-256 is `97ed35cbf618792155c15106862d8bc5f416b7cf6d073c9e37e94babdf8bc9a9`.
The [report](../reports/A36-reference-visual-review.json) retains nine source and
decoded-image identities, dimensions, selected code hashes, coordinates and
font metrics. All four inspected source files match captured qualification and
published blobs. Measurement used Python 3.12.14/Pillow 13.0.0 without resizing.

Reference panel/key landmarks have explicit ±2/±3-pixel visual uncertainty.
Native coordinates are reviewed logical allocations cross-checked visually,
not falsely labeled direct hardware measurements. Header ink uses a reproducible
warm-light mask in named half-open ROIs. No global difference score was used:
the two images have different valid control inventories.

## Findings and concrete recommendation

The cabinet left edge and approximately 144-pixel upper-manual depth now closely
follow the reference. The identical source cabinet crop is displayed at scale
0.985564, with its original aspect. Upper keys remain about five pixels higher,
lower keys about seven pixels lower; the rack remains higher/shorter. Correct
61+61+25 keys, 24 reversed presets, real tools and unconnected-model labels must
remain, so literal pixel equality remains unmet.

All eight views visibly fit their content. Both Service views show correct
singular “1 target”; both Rotary views retain decorative/read-only/unavailable
labels. Minimum preset legends remain tiny, requiring real display/DPI usability
review. Inspection does not qualify device, input, accessibility or physical
sound behavior.

The exact reference title mask is `[603,20,1067,53]` (464×33); all three native
reference-sized views give `[617,28,1051,59]` (434×31). Subtitle footprints are
371×12 at y71 versus 119×7 at y93. These are different strings with the same
hierarchical role, not a glyph-equality assertion.

[The detailed review](../../../reviews/REFERENCE_REFINEMENT_VISUAL.md) proposes
one narrow wide-Dimensional header treatment: Serif 42.75 at `header.y−4.5`,
retained safe fitting; exact **NOMINAL DRY ORGAN** in Sans 17/brass at
`header.y+51.5`, centered and tracked to 374 advance. Frozen metrics predict the
reference-sized ink targets; a rendered candidate is still required. Flat and
non-sidebar paint, all common geometry/focus and sound state stay unchanged.
Root must explicitly amend the text-size freeze, assign implementation, qualify
fixed-state raster/scale/clipping and timing, then retain fresh native captures.

Two later proposals are bounded key-edge bevel strips and less regular deck
grain within existing caps. Their actual visual/performance benefit is untested.
No numerical tolerance, material budget or underlying geometry was relaxed.

## Reproduction and handoff

Working directory: `/workspace/scratch/1bb6ee17ad7e/Hammond-B3-Organ`.

```sh
python docs/development/2026-11-14-reference-refinement/reports/A36-measurements.py
```

Exit 0 produced the retained deterministic JSON. The script is read-only; it
does not generate or overwrite images. Root owns all shared status, subsequent
implementation, acceptance and authorized publication. Historical galleries and
the separate genuine pending-state harness remain unchanged.
