# Independent T2 contract admission

**A10, 16 November 2026. Admitted for scoped implementation.** This review
admits the frozen geometry and comparison procedure, not an unbuilt candidate,
visual completion or whole-interface 1:1. The reviewed
[contract](../design/RACK_HEADING_T2_CONTRACT.md) SHA-256 is
`e7074c5fc0f930ace34317d54bcb0c9c0741d07d4c7ef174158635c71ad2dcef`.

## Independent observations

I read the full standing instructions, M0–M9 plan and current session entry;
inspected `InstrumentView.cpp`, `Drawing.cpp`, `FontData.h`, the two affected
rack tests and pinned SDL software COPY/FILL paths; and directly viewed the
unchanged reference and current full application image. The source identities
in the contract match the inspected files. No source, build or shared test was
changed or executed by this reviewer.

An independent Python calculation parsed the retained Serif glyph records,
rounded each arithmetic operation through `struct.pack/unpack('<f')`, and
reproduced the candidate pen positions. Pillow decoding of the exact original
and gallery bytes reproduced the contract's text-only regions, integer warm-ink
predicate, counts and bounds:

| Region | Reference bounds / pixels | Current gallery bounds / pixels |
| --- | --- | --- |
| Upper | `(223,285,496,297)` / 726 | `(214,284,457,296)` / 561 |
| Lower | `(734,285,1017,297)` / 734 | `(733,284,981,296)` / 581 |

At row 292, the independent strict-warm/750000-threshold observations also
reproduce `[140,205)`, `[513,564)`, `[662,715)` and `[1035,1083)`. These are
encoded image observations, not physical dimensions or a delivered candidate.

## Geometry decision

The two unchanged 21-byte strings each have twenty gaps. At canonical size,
binary32 natural widths are `246.00001525878906` and
`251.20001220703125`; tracked widths are `276` and
`285.20001220703125`. Starts are `222` and `732.9000244140625`.
The top is `281.8999938964844` and baseline `297.1000061035156`.
The proposed size, tracking, centers, one-`sy` descent and sixteen-`sx` rule gaps
are admitted exactly as written, including the grouped cursor update. Spaces
advance without glyph copies. Do not substitute a globally tracked font API,
fit the text again, or center the two runs in the old rack boxes.

Independent canonical COPY-rectangle unions are `(222,285,496,297)` and
`(733,285,1016,297)`. They bound possible writes, not actual warm ink; transparent
and antialiased glyph pixels still determine the measured candidate. Proposed
rules deliberately differ slightly from reference spans. The contract states
those residuals and requires improvement rather than claiming pixel equality.

## Containment and preservation

The support recipe is sound for the pinned SDL software path: scale logical
COPY coordinates and extents independently, truncate each, add physical
viewport origin, then intersect output/viewport/enabled clip. FILL extents use
`max(trunc(extent),1)` after the positive logical-extent guard. Include existing
small-glyph gutter padding. Keep old and new glyph/rule supports separate before
forming their union. No whole-panel mask or dilation is admitted.

The comparator must bind these calculations to its actual compiler, renderer
and fixture identities. Source equations alone do not promise cross-platform
pixel equality or authorize widening a mask after an escape. A floating-point
or renderer mismatch requires a named diagnosis and explicit review.

Preserve `reference_heading`, all non-rack callers, `centered`, Drawing/font
bytes, colors, geometry, controls and audio/state boundaries. The active
predicate, Flat/other-workspace behavior and enabled-empty clips are unchanged.
The contract's finite matrix, complete state records and full-frame review are
appropriate; neither atlas reading nor this arithmetic check executes them.

## Required narrow test transition and handoff

Only the heading probes in `full_frame_children` of
`test_standalone_upper_rack_material_raster.cpp` and
`test_standalone_lower_rack_material_raster.cpp` presently require the superseded
untracked ink. Their owners may replace those probes with an independent
literal, full-string tracked oracle using this frozen contract. Preserve every
other material, footage, numeric value, focus, geometry, clip and state
assertion; do not delete the heading coverage or call the production helper as
its oracle. Preserve the original baseline fixtures and failed outcomes.

A13 may implement T2 after root accepts this review and confirms exclusive
painter ownership. Root then rebuilds coherently and obtains actual paired
containment, reference-placement and independent visual results before product
acceptance. T3, literal whole-interface 1:1, real display/DPI/accessibility,
physical fidelity and complete M9 remain separate gates.
