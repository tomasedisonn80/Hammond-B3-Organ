# Upper-rack inner metal: prospective contract v1.1

**A08/A11, 15 November 2026. Status: independently admitted for fixture
authoring; no candidate paint or candidate acceptance is claimed.** This freezes the first
bounded candidate from [the material proposal](WHOLE_REFERENCE_MATERIAL_NEXT.md)
and its [independent conditions](../reviews/WHOLE_REFERENCE_MATERIAL_NEXT_REVIEW.md).
The scope is one surface in wide Dimensional Play. Literal whole-interface
**1:1 remains unmet and unwaived**.

The [A08 evidence note](../development/2026-11-15-streaming-continuation/notes/A08.md)
retains independently reproduced image statistics, original input identities,
actual baseline execution and source locators. Root owns coherent builds and
acceptance. The independent fixture/mask owner must freeze and run the new
before fixtures before the painter edit; this document is not their result.

The [A11 admission](../reviews/UPPER_RACK_MATERIAL_ADMISSION.md) retains the
original proposed v1 SHA-256
`cd742c7355cc0d1c47394497fa0c4caab2e9d6e20f19a463b6ed6e5533dea684`.
Revision v1.1 resolves only floating-point evaluation and half-tie rounding:
support, field/seed constants, matrix and all tolerances are unchanged.

## 1. Frozen scope and paint order

The existing Upper rack is canonical `(72,269,528,239)`. Its four-unit inset is
**`(76,273,520,231)`**, with half-open right/bottom edges `(596,504)`.
In `InstrumentView.cpp`, add a private opt-in to `reference_panel`, used only
for `layout.registration_panels[0]` in `paint_reference_composition`. Keep the
default path byte-identical for every other caller. This is a private painter
choice, not a parameter, saved field, control or user setting.

Replace only that call's inset gradient and grain. Keep the preceding five
shadow layers, rounded layers and their constants; keep the subsequent four
border accents and screws, then all headings, guides, wells, caps, footage,
values and focus operations in their existing order. Preserve `UiModel`,
`Drawing`'s existing public behavior, font/art data and every other panel.
Preserve all geometry, hit regions, semantic identities and state handling.

Activation is the existing predicate: Play + Dimensional, width in
`[1400,8192]`, height in `[820,8192]`. Every inactive frame must remain exactly
equal to its genuine before frame, including Flat, Rotary, Service, compact
sizes and the two immediate threshold neighbors. No fallback surface changes.

## 2. Bounded candidate surface

This is a procedural charcoal finish, not sampled reference artwork. Its
coordinates belong to the canonical Upper inset and do not depend on frame
clock, random device state, focus, controls, viewport origin or clipping.

### Directional field

Use 65 adjacent columns across the actual mapped inset. For column `j` in
`[0,65)`, set `u=(j+0.5)/65`. At each visible device row, use the same logical
pixel-center vertical fraction as `Drawing::gradient`:

```text
v = clamp((((device_row + 0.5) / renderer_sy) - inset.y - 0.5)
          / (inset.height - 1.0), 0, 1)
q = 22.4 + 7.6*u - 9.4*v
RGB = round_and_clamp_0_255(q+1, q, q-1); alpha = 255
```

`device_row` is relative to the physical viewport. Use binary64 for the field
and column interpolation after obtaining the actual binary32 inset. Evaluate
each arithmetic operation in the written order with a binary64 intermediate;
do not contract multiplication with addition/subtraction. `round_and_clamp`
means C++ `std::round` (half away from zero), then clamp each channel to
`[0,255]` before conversion to `uint8_t`. This rule also applies to grain colors.
For example, reference-size column 32, device row 388 has `q=21.5` and must
produce opaque RGB `(23,22,21)`, not ties-to-even RGB `(22,22,20)`. Column
boundaries are `ceil((double(inset.x) + double(inset.width)*j/65)*renderer_sx
- 0.5)`, clipped to the visible device interval; the same boundary ends one
column and starts the next. Paint integer spans at renderer scale one, using
a point for a one-pixel span and an inclusive line ending at `end-1` otherwise,
as `PixelRaster` does. Do not approximate these boundaries with independently
truncated SDL float rectangles. This partitions the field without strip gaps
or overlapping alpha. The field is sampled from the complete inset even when
clipped; clipping never renormalizes its illumination.

### Fine grain

Replace the current regular row/column lattice with exactly 2,048 deterministic
bright/dark pairs. Each mark is one canonical unit square. Define `mix(z)` on
`uint32_t`, with every multiplication wrapping modulo `2^32`:

```text
z ^= z >> 16; z *= 0x7FEB352D;
z ^= z >> 15; z *= 0x846CA68B;
z ^= z >> 16;
```

For pair `i=0..2047` and mark `m=0,1`, let `k=4*i+2*m`, seed
`0xB3A08E11`, `cx=78 + mix(seed ^ k) % 516`, and
`cy=275 + mix(seed ^ (k+1)) % 227`. Paint pairs in increasing `i`, bright
then dark. Collisions are allowed and resolved by that fixed order; there is
no retry loop or collision table. At the mark's canonical center, evaluate the
same field with `u=(cx+0.5-76)/520`, `v=(cy-273)/230`; add `+8` for bright and
`-8` for dark to `q` before RGB rounding. Marks are opaque. Map each origin
with the existing binary32 composition scale and draw size `(sx,sy)` using
`Drawing::rect` at the original caller renderer scale. Their canonical union
is inside `[78,594) × [275,502)`, before device quantization.

This declares an irregular, spatially hashed distribution rather than a tiled
grain lattice. It does not assert mathematical randomness or visual success.
The constants are a first candidate; a failed screen or visible artifact must
remain recorded. A revised field/seed/operation support requires an explicitly
versioned amendment before its next candidate run, not a changed tolerance.

### Work and renderer state

The new work is at most `65 * R + 4096` drawing primitives, where `R` is the
visible device-row count of the inset, and exactly 8,192 hash evaluations.
Custom storage is constant; no image-sized allocation, texture upload, cache,
per-device-pixel grain loop or new dependency is needed. At admitted logical
height 8192 and renderer scale at most 2, `R` is bounded by the mapped inset
height plus endpoint quantization, not by an unbounded caller loop. A clipped
empty field can skip its spans and grain after validating the intersection.
This bounds new application work; it is not an allocation or deadline claim
about SDL's internal command queue or the rest of the UI.

A private scoped guard may temporarily set renderer scale to one. Preserve
both scale components, physical and logical viewport/clip observations, clip
enabled state and blend mode, including empty intersections and early returns.
Do not reconstruct fractional physical clip state from rounded logical getters.
Prefer leaving viewport, clip and blend untouched; restore the saved scale on
every path. Preserve draw color within the new helper if it changes it directly;
the existing whole-view painter itself does not promise draw-color preservation.

## 3. Independent physical mask, declared before paint

The checker must implement the following arithmetic independently of the new
painter and retain a mask manifest. It must not infer bounds from changed
pixels, read a candidate-produced allowance, use the prior whole-composition
v2 mask, or add old wood-line allowances.

Let `F` round each indicated operation to IEEE binary32. For logical `W,H`:

```text
sx=F(W/1672); sy=F(H/941)
bx=F(72*sx); by=F(269*sy)
bw=F(F(600*sx)-bx); bh=F(F(508*sy)-by)
dx=F(4*sx); dy=F(4*sy)
ix=F(bx+dx); iy=F(by+dy)
iw=max(0,F(bw-F(2*dx))); ih=max(0,F(bh-F(2*dy)))
```

Do not replace this inset-of-mapped-panel arithmetic with direct scaling of
`(76,273,520,231)`. They need not have identical binary32 endpoints.

Capture renderer scale `(rx,ry)` and read viewport `V` and enabled clip `C`
at scale one, restoring the original scale. The visible viewport-relative
device box is the intersection of `[0,V.w) × [0,V.h)`, the output extent
translated by `(-V.x,-V.y)`, and `C` when enabled. SDL queues viewport/clip
components with `floor`; record actual physical getters, not an inferred
rounded logical rectangle. Empty intersections have empty allowances.

The source-derived intrinsic supports, before caller intersection, are:

| Operation | Viewport-relative device coverage |
| --- | --- |
| Original inset `Drawing::gradient` and candidate field | `[ceil(double(ix)*rx-.5), ceil((double(ix)+double(iw))*rx-.5))`, with the analogous y interval. The addition is binary64, as in `Drawing.cpp`. |
| Original grain and new grain `Drawing::rect(x,y,w,h)` | `left=trunc(F(x*rx))`, `top=trunc(F(y*ry))`, `width=max(trunc(F(w*rx)),1)`, `height=max(trunc(F(h*ry)),1)`, then half-open extents. This is pinned SDL 2.32.10's `SDL_RenderFillRectsF` plus `SW_QueueFillRects`, not the gradient rule. |

Enumerate the original grain with its actual source formula: `rows=floor(bh/sy
-16)`, `columns=floor(bw/sx-21)`, the existing square-root step and 2,048-pair
cap, binary32 coordinates and both original rectangle sizes. Enumerate the new
marks from section 2. Translate every support by the physical viewport origin.
The allowance is the union of these intrinsic supports, expanded by **exactly
one device pixel** on each side, then intersected with the caller's physical
visible region and output. No logical padding is permitted. Retain intrinsic
and expanded counts separately; confirm every support stays within the mapped
inset's one-device-pixel envelope. At 1672×941, scale 1, origin zero and no clip,
the allowance is exactly `[75,597) × [272,505)`; its size is 121,626 pixels.

Outside the allowance require zero differing RGBA pixels and zero differing
channels. For inactive or empty-intersection cases require whole-frame exact
equality. Report differing pixels, maximum channel delta, bounding box, and
per-row difference counts; retain a lossless spatial difference for any failure.
Never enlarge this allowance after observing an escaping pixel. An incorrect
mask/painter requires an independently reviewed new version and retained failure.

## 4. Reference-size numerical screens

Decode the original JPEG directly to RGB without resampling, gamma conversion
or edits. On half-open patches use encoded-channel
`Y'=(2126R+7152G+722B)/10000`. Fit a plane `a+bx+cy` to every pixel and use
population RMS of its residual. These are image statistics, not luminance or
physical metal measurements.

| Patch | Unrounded reference mean | Unrounded reference residual RMS |
| --- | ---: | ---: |
| Left `(88,320,18,128)` | 18.29127847222222 | 1.3771611766012388 |
| Right `(572,320,14,128)` | 25.32330982142857 | 1.5633734337299345 |

The reference right-minus-left mean is **7.032031349206349**. Require each
candidate mean's absolute difference to be **≤2.0**, each RMS difference
**≤0.4**, and the right-minus-left difference's error **≤1.5**. Recompute from
the original pixels or the exact sufficient statistics in A08's note, not
three-decimal display values. Retain decoder identity, RGB/file hashes, raw
sums, residual SSE, full-precision metrics and every failed inequality.

Apply these screens only at 1672×941, renderer scale 1, origin zero, full clip,
with the declared quiet patches unobscured. No scaled-frame numerical grade is
implied. The actual baseline case 0 and admitted reference-size PNG both fail
all five screens: native means are 31.84118107638889 / 31.818605357142857,
RMS 0.48668373146712585 / 0.622113392689367, and lateral difference
−0.02257571924603141. That recorded failure is the intended before observation.

Independent full-frame inspection must also reject visible periodic grain,
banding, seams, sparkle, worse label/focus contrast or conspicuous new edges.
Inspect the complete application at reference and minimum-active sizes, not
only the two patches. Passing these local screens cannot prove whole-surface
material identity or whole-interface equality.

## 5. Existing fixtures and a finite gap set

Preserve `test_standalone_percussion_raster.cpp` and its original **66 indices**.
Pair the actual before executable
`/workspace/scratch/177e78b1ac09/baseline/test_standalone_percussion_raster`
with the coherently rebuilt current executable using its existing `--case N`
stream. Its SHA-256 is
`087f88b7f710239b553f794c79cc51ec4f813cb737e8c769f01866e01ff979c4`.
The old schema-1 `regions` describe percussion and are not this mask.

| Existing indices | Relevant coverage and limitation |
| --- | --- |
| 0–17 | Reference size, all 16 percussion combinations at scale 1, plus scales 1.5/2; adjustable A/B, fixed D, Cancel, pending/applied routes and held notes. Focus remains percussion. |
| 18–23 | Minimum active and 1920×1080, each at scales 1/1.5/2. |
| 24–33 | Both threshold neighbors and compact 960×700/1280×900; exact inactive preservation. |
| 34–51 | Flat, Rotary and Service; exact inactive preservation. |
| 52–53, 60–65 | Fractional dimensions and retained historical eligibility-height neighbors. |
| 54–59 | Physical/logical clips at origin `(7,7)`, entirely above the Upper inset. Their material allowance is empty; they must remain wholly equal. They do not test any Upper-rack edge. |

There are 38 logically active cases, but only 32 have a nonempty surface
intersection. The 28 inactive cases plus six clipped active cases require
whole-frame equality. Existing drawbars contain the sequence 0..8; they do
not exercise every cap at each of 0/4/8 or focus on the changed surface.

Add one versioned native fixture, provisionally
`test_standalone_upper_rack_material_raster`, reusing the existing software
surface, `Drawing`, copied-state, transform-query and JSON-line-plus-RGBA
stream pattern. It must invoke the real painter, not an alternate material
implementation. Freeze the following **30 additional cases**, not a full
Cartesian expansion. All are Dimensional Play.

For all cases, set all four retained manual banks to the listed `level`,
expression 0.625, pedal mixtures `{3,7}`, percussion On/Second/Normal/Slow,
frame clock 38400, sample rate 48000, peak 0.125, revision 4 and prepared/running
true. Keep the existing fixture's fixed `InstrumentViewInfo` strings. `held=1`
means Upper key index 24, Lower 36 and pedal 12; `held=0` clears them. Applied
route is the listed Upper preset. Edit A for route A, otherwise B. Pending
requests A if applied route is B, otherwise B, without acknowledging it.
Focus the Upper drawbar whose index equals `level` (0, 4 or 8), in the edited
bank, using normal focus traversal. Assert the copied desired/applied snapshots
and all geometry exactly match before/after.

| IDs | Size | Scale | Physical viewport origin | Level / applied route / pending / held |
| --- | --- | --- | --- | --- |
| 0,1,2 | 1672×941 | 1,1.5,2 respectively | `(13,17)` | `0/B/0/0`, `4/A/1/1`, `8/D/0/1` |
| 3,4,5 | 1400×820 | 1,1.5,2 respectively | `(13,17)` | `4/Cancel/1/0`, `8/B/0/0`, `0/A/1/1` |
| 6,7,8 | 1920×1080 | 1,1.5,2 respectively | `(13,17)` | `8/D/1/1`, `0/Cancel/0/0`, `4/B/1/0` |
| 9–20 | 1672×941 | For each left/right/top/bottom edge, 1,1.5,2 in that order | `(13,17)` at 1/2; `(0,0)` at 1.5 | `4/B/0/1` |
| 21,22,23 | 1672×941 | 1,1.5,2 | `(13,17)` | `4/B/0/1`; disjoint clip, enabled zero physical clip, enabled zero logical clip respectively |
| 24,25,26 | 8192×8192 logical, 64×64 output | 1,1.5,2 | Negative viewport translation described below | `4/B/0/1` |
| 27,28,29 | 1672×941 | 1 | `(0,0)` | `0/B/0/0`, `4/B/0/1`, `8/D/1/1`; full clip, also numerical-screen cases |

Unspecified clips are disabled. Normal output is `ceil(W*scale)+2*origin.x`
by `ceil(H*scale)+2*origin.y`, and viewport extent is `ceil(W*scale)` by
`ceil(H*scale)`. Set viewport at scale one before restoring the test scale.
For resource cases 24–26 use physical viewport origin `(-L,-T)`, where `L,T`
are the independently derived inset's intrinsic device left/top before adding
an origin, and viewport extent `ceil(8192*scale)` in each dimension. This
exercises maximum logical dimensions with a bounded output allocation; it
does not benchmark a full 8192×8192 display.

For edge cases at scale 1/2, let `[L,R) × [T,B)` be the inset's intrinsic
viewport-relative device rectangle. Install physical clips at scale one:
left `(L-2,T-2,4,B-T+4)`, right `(R-2,T-2,4,B-T+4)`,
top `(L-2,T-2,R-L+4,4)`, bottom `(L-2,B-2,R-L+4,4)`.
At scale 1.5 install logical clips after setting scale, respectively
`(74,300,4,160)`, `(594,300,4,160)`, `(90,271,490,4)` and
`(90,502,490,4)`. Case 21's physical disjoint clip is `(R+4,T+4,8,8)`;
case 22 uses physical `(L,T,0,0)`; case 23 uses logical `(76,273,0,0)`.
For case 23 only, start with draw blend mode NONE; all others use BLEND.
Restore the exact incoming mode in every case.

For each clipped case, the ordinary fixture also renders a full-clip companion
with the same output, viewport and state, and compares its pixels inside the
visible clip exactly. This checks clipping does not shift grain or illumination.
It is an internal companion, not an additional claimed fixture index. Repeat
case 28 after other states and on a fresh renderer; require identical RGBA.

Keep the stream simple: `--list` emits schema, protocol and case count;
`--case N` emits one newline-terminated JSON header followed by exactly
`width*height*4` RGBA bytes. Header fields identify protocol, case ID, logical
size, output size, scale pair, viewport and clip in physical coordinates,
clip-enabled/blend, level/route/pending/held/focus, and byte count. Emit floats
with `max_digits10`. Compare metadata against the frozen case specification;
the checker derives masks from its own arithmetic. Report state-restoration
failures on stderr and fail the process. Do not embed masks or old painter code
in a candidate stream.

The existing preserved executable cannot emit these additional cases. Root
must build this same new harness once against the preserved before painter
and its matching inputs, retain that executable/source receipt, and then
against the candidate. Do not relabel the newly built supplemental baseline
as the original 66-case executable. Preserve original expectations and failures.

## 6. Children, captures and acceptance

Unchanged child draw operations can produce different antialiased edge RGB
over the new background inside the allowance. That does not authorize moving
or recoloring children. Independently review the source diff and require
unchanged font/art hashes, child arguments/order, layout snapshots and hits.

In full-frame supplemental cases, compare opaque child interiors exactly.
For each canonical Upper center `158,206,254,302,351,400,449,498,548`, use the
well interior `(center-12,320,4,130)` and cap interior
`(center-10,327+118*level/8-10,20,12)`, mapped independently and eroded inward
by one device pixel. These lie inside existing opaque child painting; require
nonempty probes and exact before/after RGBA. Compare actual cyan focus ink
positions/count in the declared focused control, and independently render the
existing Upper heading, nine literal footage labels and dynamic values to
check strong glyph coverage and contrast using the existing harness's method.
Do not compare the entire alpha-blended child rectangle for equality or accept
merely one nonempty glyph pixel. All 68 controls, 147 playing keys, 24 presets,
71 Play focus stops, 47 parameter meanings and state readers remain unchanged.

Root's later capture set must include the actual changed application's
reference and minimum-active views and retain source overlay, executable,
dependencies, state/replay, diagnostics and decoded-pixel hashes. Replay the
admitted scene: Upper 60/64, Lower 67, pedal 3, retained Upper B 16-foot 7→8
while fixed C# sounds, expression 0.75, mixtures 8/0 and
On/Second/Normal/Slow percussion. Preserve the old gallery. Application runtime
counters are not deterministic comparison inputs; use copied snapshots for
exact raster pairing and the real replay for product evidence.

Before scoped acceptance, root builds coherent inputs and runs the affected
geometry/input, material acceptance, product visual, scaled-view, preset and
percussion raster, and waveform-material suites, plus the new fixture and
paired checker. Required CTest selections use `--no-tests=error`. Retain all
five numerical outcomes, containment/equality counts, child checks, state
restoration and independent full-frame inspection. Update actual screenshots
only after their new provenance is admitted.

A pass qualifies this Upper inset and the declared software preservation
matrix. It does not close other metal, wood, cap/key shading, typography,
whole-interface 1:1, native display/DPI/input usability, semantic accessibility,
audio-device/host behavior, connected scanner/rotary audio or physical fidelity.
