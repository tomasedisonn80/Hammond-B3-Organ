# T3 live title weight and brass relief contract

**Proposed for independent admission; no implementation or candidate pass.**
Author A11, 16 November 2026, continuation based on
`113c29b7b14c8fde0859bc405ef8e4141a131ea6`. A16 independently reviews this
contract before the assigned painter edit. The root owns integration and the
genuine immediately-pre-T3 baseline. T2 must be accepted and frozen separately;
its changed headings are outside T3's support.

## 1. Scope and observed inputs

Change only the `TONEWHEEL ATLAS` glyph passes in the wide Dimensional Play
`reference_header` in `apps/standalone/InstrumentView.cpp`. Keep the current
reference-composition predicate: Play, Dimensional, width >=1400 and height
>=820. Other workspaces, Flat and smaller layouts retain their existing pixels.
Do not change the shared `header`, `Drawing`, font atlas, text measurement,
layout, state, hit geometry, title rules, caption or utility controls.

The unchanged [reference](atlas-cover-reference.jpg), SHA-256
`9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187`, is the
atlas's generated art direction. It has heavier, brighter title strokes and
visible relief; it is not calibrated material/lighting evidence. The retained
[application frame](native-gallery-preset-v1/images/play-reference-1672x941.png),
SHA-256 `6ac89798b41026533b474bbd523424134873af903a7bd1f9a58d09a583e0923a`,
has comparable gross extent but thinner, comparatively flat strokes.

A11 independently decoded both original images without resampling and counted
pixels in the half-open rectangle `(590,14,490,46)`. The predicate is encoded
`Y'=(2126R+7152G+722B)/10000 >= threshold`, **without an additional hue predicate**.
This preserves the authoring observation's definition; it differs from the
existing C++ warm-ink geometry predicate. Counts are image statistics, not
physical luminance, font-weight measurements or whole-interface similarity.

| Y' threshold | Reference pixels | Retained application pixels |
| --- | ---: | ---: |
| 80 | 5,639 | 4,150 |
| 100 | 5,415 | 3,863 |
| 120 | 4,991 | 3,601 |
| 140 | 4,502 | 3,200 |
| 160 | 3,785 | 2,690 |

At threshold 100, reference/application half-open bounds are respectively
`(603,20,1067,53)` and `(602,20,1065,53)`. The frozen title anchors already fit
the reference; increasing the font size is not this slice's remedy.

Pinned unchanged glyph inputs:

- `FontData.h`: `f1a3121a2707a03a3b2e025c399e68c553ce9498f4b002ec13b18f512e334802`.
- `Drawing.cpp`: `666e998cc61a9d501238783c8f2917d9be30db0bac76739f91bc23eb54f34b0a`.
- Inspected pre-T2 painter: `63bede9eb5fccde155d6d6ddfbbcbfa7566ab06dcf2726d92b84bc7ad0e72a77`.

The existing DejaVu Serif Book 2.37 atlas remains unchanged, including license
and coverage. This contract acquires no font or image asset. Root must separately
identify the actual post-T2/pre-T3 painter and genuine baseline binaries.

## 2. Frozen geometry and pass order

Retain every current `reference_header` calculation through `x`, `y` and `size`,
in its existing binary32 operation order: mapped control exclusions, symmetric
available width about `836*sx`, initial `size=42.75*f`, existing width-fit branch,
measured title width, clamped centered `x`, and `y=11.5*sy`, where
`sx=layout.width/1672`, `sy=layout.height/941`, `f=min(sx,sy)` as already defined
by the reference-composition helper. Do not insert tracking, stretching, a new
baseline or a shift of the whole title. Both old and new use `TextFace::Serif`.

Replace the existing two title calls with exactly these **five calls in order**.
Each call draws the entire same live ASCII string, using the unchanged `size`.
All colors below are literal RGBA bytes; no frame/time/state input modifies them.

| Order / purpose | x argument | top argument | RGBA |
| --- | --- | --- | --- |
| 1. Retained cast shadow | `x + sx` | `y + 2.0F*sy` | `(4,5,4,255)` |
| 2. Lower dark bevel | `x + f` | `y + f` | `(100,65,28,255)` |
| 3. Upper highlight | `x` | `y - 0.5F*f` | `(255,231,184,255)` |
| 4. Added stroke weight | `x + f` | `y` | `(212,171,103,255)` |
| 5. Main brass face | `x` | `y` | `(226,192,135,255)` |

The cast shadow preserves the old anisotropic offset. New relief/weight offsets
use the isotropic font scale to avoid exaggerated bevels in unequal-aspect
windows. The dark bevel remains below the primary Y' threshold before blending.
The final face covers overlapping highlight/weight interiors while leaving their
exposed edges. These are proposed artistic values, not a measured metal shader.

Call `Drawing::text` directly or through a private title-only helper receiving
these exact arguments. Do not add a clipping pass, texture, rasterized title,
font generation, global color change, offscreen target or direct renderer-state
mutation outside the existing `Drawing::text` behavior.
The existing final caption calls continue to set their own texture modulation.

## 3. Exact support and bounded work

The string contains 15 ASCII characters, 14 with ink. The old title makes two
text calls and 28 glyph copies. The new title makes five text calls and at most
70 nonempty glyph copies: **42 added copies**, independent of window dimensions,
time or audio state. The title helper adds no application-owned storage, explicit
allocation, loop over output pixels, randomness, device query, file access or
audio-thread work. SDL's existing main-thread command queue may allocate; this
draw-call bound is not a transitive allocation or frame-deadline guarantee.

For each old/new pass independently, reproduce the unchanged `Drawing::text`
binary32 arithmetic. Let `g=size/40`, `baseline=pass_top+38*g`; initialize the
pen at `pass_x`. For each glyph, its copy destination is
`(pen+(bearing_x-padding_x)*g, baseline+(bearing_y-padding_y)*g,
(width+2*padding_x)*g, (height+2*padding_y)*g)`. Padding is two atlas pixels in a
dimension only when that glyph dimension times `g` is less than one. Advance
the pen by `float(advance_64)*g/64`, preserving each assignment and operation order.
Spaces advance but have no copy. Do not infer support from a font-size box.

The permitted change set is the union of these actual destinations for **both
old calls and all five new calls**, transformed and intersected with the caller's
viewport, enabled clip and target according to the pinned SDL 2.32.10 software
COPY conversion: multiply each destination x/y/width/height separately by its
renderer scale with binary32 rounding, truncate each toward zero, add the
physical viewport origin to x/y, then intersect the resulting half-open rectangle
with the physical viewport, enabled clip and output. Zero/negative copy extents
paint no pixels; do not use a ceiling expansion or floor a negative origin.
The independent comparator derives that union before reading
candidate differences; no changed-pixel-derived mask, broad title/header box,
arbitrary dilation or older material allowance is admitted. Report the derived
support size and actual changed pixels separately. Enabled empty clips stay empty.

Outside this union, every same-state paired RGBA pixel must remain identical.
No old/new support is admitted for an inactive layout. Renderer scale, viewport,
clip enable/rectangle and blend state must survive; painting must not alter the
model or session snapshot. For cut glyphs, use the pinned SDL clipped-copy result;
do not assume a clipped texture is a crop of an uncut resampling.

## 4. Acceptance frozen before implementation

1. **Meaningful canonical improvement.** On the actual unscaled 1672x941 native
   software frame at zero viewport origin and no clip, use the exact ROI and Y'
   predicate from section 1. The pre-T3 baseline must reproduce the recorded
   3,863 count and bounds, or root must resolve the different baseline explicitly
   before implementation. Candidate threshold-100 count must lie in **[4,500,
   6,000] inclusive**. Every value in this band reduces the original absolute
   count error against 5,415 by at least 40%; it is a predeclared bounded visual
   target, not an equality or fidelity claim. Record all five thresholds and
   bounds even when the primary band passes.
2. **Existing geometry remains binding.** Keep the C++ material suite's warm-ink
   width `464*f +/-3`, height `33*f +/-1`, top
   `11.5*sy+8.5*f +/-1`, center `width/2-f +/-2`, more than 1,000 title pixels,
   separated caption, fifteen distinct caption letters and zero control/header
   escapes. Do not relax those thresholds to admit this candidate. The Y' count
   predicate and these warm-ink limits are separate checks.
3. **Preservation.** Paired genuine baseline/candidate frames must pass the exact
   support/state requirements at canonical and minimum-active 1400x820, larger
   1920x1080, unequal layouts 1920x820/1400x1080, fractional logical sizes,
   renderer scales 0.75, 1.25 and unequal 1.5x2, positive/negative origins,
   intersecting/disjoint/empty clips, and supported maximum-size resource crops.
   Compact, Flat, Rotary, Service and immediately-below-active boundaries must
   have whole-frame equality. Resource crops do not establish full-window bounds.
4. **Visual admission.** Independently inspect actual full frames at canonical,
   minimum-active and wide sizes, with reference and genuine before images.
   Reject filled counters, muddy/haloed strokes, clipping, lost subtitle or a
   disproportionately bright title even if the numeric band passes. Inspect
   unchanged compact/Flat views. Update README with the final actual app captures.
5. **Compatibility.** Retain the 213-file protected inventory, control/input and
   affected native raster/material tests. Preserve the complete state/parameter,
   musical ownership and dry Engine boundaries in the session README. Run coherent
   builds before tests; source-specific platform results remain separately required.

A missed criterion is a failed candidate. Keep its sources, original report and
images before proposing an independently reviewed revision; never relabel that
attempt or silently tune this contract after observing it. T3 acceptance does
not establish whole-interface 1:1, real display/DPI or accessibility acceptance,
physical audio fidelity, or release qualification.
