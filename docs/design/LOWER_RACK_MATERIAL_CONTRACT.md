# Lower-rack inner metal — candidate contract v1

**A08, contact conversion/material continuation. Status: ready for independent
protocol/fixture review; not implementation or visual acceptance.** This is the
next bounded L1 slice from [the proposal](REFERENCE_MATERIAL_TYPE_NEXT.md) and
[its review](../reviews/REFERENCE_MATERIAL_NEXT_REVIEW.md). A separate reviewer
must admit this version before the painter changes. Literal whole-interface
**1:1 remains unmet and unwaived**.

## 1. Inputs, observations and scope

The unchanged original [cover/page-409 JPEG](atlas-cover-reference.jpg) has
SHA-256 `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187`.
Root preserved the genuine current painter, app and raster binaries at
`../baseline`, bound by the new session's
[baseline identity](../development/2026-11-16-conversion-material/reports/baseline-identity.json).
Its current painter SHA-256 is
`30ac6cec988ec1834f36456d25d1e53113642071d844d53f81b62b3474cf2c37`.
The separate pre-Upper baseline is not this transition's source.

A08 inspected complete original and genuine baseline frames. The
[observation script](../development/2026-11-16-conversion-material/reports/A08-lower-observations.py)
and [receipt](../development/2026-11-16-conversion-material/reports/A08-lower-observations.json)
retain ten patches, exact sufficient statistics and source/decoder identities.
Run the script from the repository root; its optional positional argument names
a 1672×941 genuine baseline PNG. It performs no build or candidate grading.

Replace only the inner gradient/grain of **Lower** `registration_panels[1]`,
canonical panel `(600,269,516,239)`, four-unit inset `(604,273,508,231)`.
Activation remains the existing wide Dimensional Play predicate: logical width
1400–8192 and height 820–8192. Introduce a private surface enum if useful; keep
Original as the default and Upper's existing branch/arithmetic unchanged.
Preserve preceding shadows/rounded layers and subsequent border accents,
screws, headings, guides, wells, caps, footage, values and focus, with unchanged
arguments/order. No geometry, `UiModel`, font/art, sound, state, parameter or
host change belongs to L1. All inactive paths must remain pixel-exact.

Seven primary rectangles avoid numbers, heading glyphs, wells and caps. Their
locations were selected before this author's values were evaluated. Top strips
lie below the heading and above wells; lower corners lie beside the footage.
They deliberately retain broad illumination/JPEG variation. Encoded-channel
`Y′=(2126R+7152G+722B)/10000` is an image statistic, not physical luminance.

| Name; half-open `(x,y,w,h)` | Reference mean Y′ | Baseline mean Y′ |
| --- | ---: | ---: |
| L `(612,320,18,128)` | 27.929753038194445 | 31.805590798611110 |
| R `(1094,320,14,128)` | 20.590579464285714 | 32.013991852678570 |
| LT `(612,298,18,14)` | 31.056320634920635 | 38.496349206349200 |
| RT `(1094,298,14,14)` | 23.925342857142858 | 38.516326530612240 |
| CT `(800,302,112,6)` | 28.588978273809524 | 38.524605952380950 |
| LB `(612,460,18,20)` | 24.713884444444446 | 24.462615555555554 |
| RB `(1094,460,14,20)` | 17.745590714285714 | 24.530250714285714 |

The receipt's exact fractions, not rounded table values, own comparisons. The
long strips' reference horizontal slopes are **+0.067456761158411** and
**−0.131003434065934** Y′/pixel; vertical slopes are **−0.060897572528180** and
**−0.029729283948518**. The earlier bilinear initialization cannot reproduce
both horizontal signs. Section 2 adds finite localized edge curvature rather
than declaring that initialization a recovered illumination map.

Three additional bottom-interior witnesses `(704,492,12,8)`, `(852,492,14,8)`
and `(1047,492,12,8)` have reference means **32.529444 / 29.123223 / 22.381538**
versus baseline **22.418858 / 22.393561 / 22.325108**. They expose a warmer
interior reflection not identified by the two long strips or this first field.
Retain their full metrics descriptively; they are neither excluded from the
whole-window objective nor accepted as matched. This candidate does not add a
special strip/bloom fitted to them. No patch-specific paint is permitted.

## 2. Frozen bounded field and grain

The following are **chosen artistic constants**, informed by the observations;
they are not measured metal properties. Render 127 adjacent columns. For column
`j=0..126`, `u=(j+0.5)/127`. At visible viewport-relative device row `r`, with
incoming renderer vertical scale `ry`, use

```text
v = clamp((((r+0.5)/ry)-inset.y-0.5)/(inset.height-1), 0, 1)
```

For `inset.height<=1`, set `v=0`. Obtain the inset using existing binary32
layout/inset arithmetic; promote those stored results to binary64. Every
operation below rounds separately to binary64 in written parenthesization;
no multiply/add contraction. Decimal constants denote their nearest binary64
values. The unchanged `upper_rack_binary64`, raster and color guard may be
reused as mechanical helpers; do not change their existing behavior.

For each RGB channel, evaluate `base=((a+(b*u))+(c*v))+((d*u)*v)`:

| Channel | a | b | c | d |
| --- | ---: | ---: | ---: | ---: |
| R | 35.320924203 | −10.874155773 | −12.501738043 | 6.205237100 |
| G | 34.943428203 | −11.336804366 | −14.777279430 | 7.789951248 |
| B | 35.610452235 | −13.973112652 | −15.176662864 | 10.100565245 |

Compute common correction in this exact dependency order:

```text
t=v-0.48; t2=t*t; t3=t2*t
l=max(0,1-(5*u)); rr=max(0,1-(5*(1-u)))
left=((61*(u-(17/508)))*l)*l
right=((-74*(u-(497/508)))*rr)*rr
curve=((40-(52*u))*t3)+((4*u)*(t2-0.02581))
correction=(left+right)+curve
channel_value=base+correction
```

The divisions `17/508` and `497/508` are binary64 divisions, not integer ones.
Edge corrections and their first derivatives vanish at u=0.2/0.8. Their centers
match the long-strip centers; vertical curvature represents observed corner
changes. This chosen field does not identify the entire panel. Round channels
with C++ `std::round` (half away from zero), clamp 0–255; alpha is 255.

Column edges are `ceil((double(ix)+(double(iw)*j)/127)*rx-0.5)`, evaluated in
that order with binary64 intermediates, clipped to the physical visible box.
Use one shared edge for adjacent spans. Field rows run from
`ceil(double(iy)*ry-0.5)` to `ceil((double(iy)+double(ih))*ry-0.5)` exclusive.
Paint integer spans at scale one, a point for one pixel and an inclusive line
ending at `end-1` otherwise. Clips sample the full field; never renormalize u/v.

Grain has **2,304 bright/dark pairs**, one canonical unit square per mark.
The density `4608/(508*231)=0.039268…` and amplitude 8 give an ideal sparse
RMS about **1.5853**, near the observed 1.6480/1.4507 long-strip residuals;
collision, quantization and illumination effects still require actual grading.
This count is independently chosen from Lower area/statistics, not inherited
as an Upper acceptance fact. Seed is `0xB3160A08`. Use the existing unsigned
32-bit mix sequence, all multiplications modulo `2^32`:

```text
z^=z>>16; z*=0x7FEB352D; z^=z>>15; z*=0x846CA68B; z^=z>>16
```

For pair i=0..2303, mark m=0,1: `k=4*i+2*m`,
`cx=606+mix(seed^k)%504`, `cy=275+mix(seed^(k+1))%227`.
At `u=(cx+0.5-604)/508`, `v=(cy-273)/230`, evaluate the same RGB field, add
+8 (m=0) or −8 (m=1) to each unrounded channel, then round/clamp. Paint in
ascending i, bright then dark; collisions resolve by this order without retries.
Map origin through existing binary32 composition mapping and use `Drawing::rect`
with size `(sx,sy)` at restored caller renderer scale. Canonical support is
inside `[606,1110)×[275,502)`. No clock/random state, images, caches, uploads,
new dependency, image-sized buffer or per-device-pixel grain loop is allowed.

New work is at most **127*R+4608** drawing primitives and **9216** hash calls,
where R is visible inset device rows. A 128-integer edge array is fixed storage.
At admitted logical height≤8192 and renderer ry≤2, use conservative **R≤4028**;
resource fixtures expose at most 64 rows. This is a source work bound, not an
SDL allocation or frame deadline claim. Save/restore both scales and helper draw
color on every path. Leave viewport, clip storage, clip-enabled state and blend
untouched; read physical getters at scale one, never round-trip fractional clips
through logical getters. No texture state is touched. Empty intersections may
skip spans/marks after scoped restoration.

## 3. Independent operation-derived support

The independent checker must derive the old and new operations before comparing
pixels. Do not use changed-pixel masks, candidate allowances, Upper masks or the
old whole-composition mask. Let F round every indicated operation to binary32:

```text
sx=F(W/1672); sy=F(H/941)
bx=F(600*sx); by=F(269*sy)
bw=F(F(1116*sx)-bx); bh=F(F(508*sy)-by)
dx=F(4*sx); dy=F(4*sy)
ix=F(bx+dx); iy=F(by+dy)
iw=max(0,F(bw-F(2*dx))); ih=max(0,F(bh-F(2*dy)))
```

Old gradient/new field intrinsic box uses the binary64 ceil(center) boundaries
above. Enumerate old grain from the unchanged source's actual rows, columns,
square-root step, 2048-pair cap, binary32 coordinates and two rectangle sizes.
Enumerate all new marks. Pinned SDL 2.32.10 software fills use
`left=trunc(F(x*rx))`, `top=trunc(F(y*ry))`,
`w=max(trunc(F(width*rx)),1)`, `h=max(trunc(F(height*ry)),1)`.
Union the operation supports, expand by **exactly one device pixel** each side,
translate by the actual physical viewport origin, then intersect output,
viewport and enabled physical clip. Enabled empty clips have empty allowance.
Retain intrinsic/expanded counts separately and confirm the whole union lies
inside the mapped inset's one-device-pixel envelope.

Canonical no-clip/origin-zero support is `[604,1112)×[273,504)` (117348 pixels);
expanded allowance is `[603,1113)×[272,505)` (**118830** pixels). Require zero
changed RGBA pixels/channels outside allowance; whole-frame equality for inactive
or empty/disjoint cases. Record counts, maximum delta, bounds and per-row changes;
retain lossless before/after/difference on failure. Never enlarge a mask because
a candidate escapes it. New versions retain the original failure.

## 4. Frozen reference screens

Use direct unresampled original RGB and canonical actual native raster input
at scale1, origin0, full clip; L/R and all primary patches must be unobscured.
Compute exact mean and least-squares plane sufficient statistics, with population
residual RMS. Preserve decoder/image hashes, raw sums and unrounded results.
For **each of seven primary patches**, require mean Y′ error≤**2.5** and each
RGB-channel mean error≤**3.0**. For L/R, additionally require:

- residual Y′ RMS error≤**0.50** (reference 1.648025041753251 / 1.450712070216063);
- horizontal slope error≤**0.060 Y′/pixel**;
- vertical slope error≤**0.025 Y′/pixel**;
- right-minus-left mean error≤**1.75** (reference −7.339173573908731).

These 35 Lower-specific authoring inequalities bound dark color, non-flat grain
and directional illumination while allowing quantization/JPEG variation; they
are not perceptual thresholds or surface identity. Retain every baseline failure,
all ten descriptive metrics and candidate outcome. Coefficient/seed/support
changes need a versioned amendment before rerunning; never loosen criteria to
pass a candidate.

Independent full-frame inspection at 1672×941 and 1400×820 must reject new seams,
striping, sparkle, obvious edge bands or worsened heading/footage/value/focus
legibility. Numeric passes cannot override a visual blocker.

## 5. Genuine fixture matrix and foreground preservation

Keep the genuine before/current **66-case percussion raster** pair unchanged;
only this checker derives Lower support. Add a new
`test_standalone_lower_rack_material_raster` harness, protocol
`lower-rack-material-v1`, **32 cases**. It may adapt the Upper fixture machinery,
never the candidate painter or its mask. Root first builds this same new harness
against the genuine unchanged painter and preserves its binary/source inputs.
Only then build it against the changed painter. This is a new supplemental
baseline, not a relabeling of an old executable.

Indices0–29 follow the complete state/size/scale/viewport/resource specification
of [Upper v1.1 §5](UPPER_RACK_MATERIAL_CONTRACT.md#5-existing-fixtures-and-a-finite-gap-set),
with these explicit Lower substitutions: applied/edit/pending preset ownership
and focused drawbar all use **Lower**; focus index=level (0/4/8); centers are
**685,734,782,830,878,927,975,1024,1074**; resource viewport translation derives
Lower's inset. All four retained banks still take the stated level; held notes,
percussion, expression, clock and copied diagnostics stay as specified there.
At scale1.5, edge logical clips are respectively `(602,300,4,160)`,
`(1110,300,4,160)`, `(618,271,474,4)`, `(618,502,474,4)`;
zero logical clip is `(604,273,0,0)`. Other physical clips derive Lower L/R/T/B
using the same four-pixel edge formula. No unspecified Upper coordinate survives.

Add index30: **1920×820**, rx=ry=1, origin(13,17), level4/B/no-pending/held;
and index31: **1672×941**, rx=1.5, ry=2, origin(13,17),
level8/A/pending/held. Both full clip, Dimensional Play. Normal output/viewport
uses independent x/y scales. These expose unequal composition and renderer scales.
All stream metadata, scale pairs, physical clips/viewports, copied state and
geometry must match the frozen specification, and before/after exactly.

Keep the newline-terminated JSON header plus exact RGBA byte stream; `--list`
reports protocol/count. No masks in candidate streams. Compare clipped outputs
with full-clip companions, exact repeat/fresh-renderer case28, and saved renderer
state including enabled-zero clips/blend. In full supplemental frames require
nonempty exact opaque well/cap probes at all Lower centers, using the same
canonical formulas and one-device-pixel inward erosion as Upper §6. Require exact
cyan focus-ink positions/count and independent strong glyph/contrast checks for
the Lower heading, all nine correct footages and dynamic values. Unchanged
antialiased edge RGB may composite differently inside support; unchanged source
arguments/opaque interiors must still be independently verified.

## 6. Acceptance and next boundary

Root builds/runs affected geometry/input/preset/percussion/product/material/
scaled/waveform raster gates, this harness and **98 genuine paired cases**, with
`--no-tests=error`. Preserve Upper history. Capture the real changed app at
reference/minimum-active sizes with admitted replay and source/dependency/
executable/state/pixel identities, inspect full frames, then update README.

Preserve 68 controls, 147 keys, 24 presets, four banks, 71 focus stops,
47 parameters, state4/readers1–3 and audio histories. Bottom reflections, other
materials/type, whole-interface1:1, native display/input/accessibility, devices/
hosts/deadlines and physical fidelity remain separate. Each later slice needs
L1's accepted genuine baseline and its own contract/support before editing.
