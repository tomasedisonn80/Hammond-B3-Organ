# P1 percussion/expression plate material contract

**Pre-candidate proposal by A08, 16 November 2026 (America/Halifax).**
Independent A11 review and root admission are required before production paint.
This file defines one complementary M9 surface, not an implemented result.
Read the [session scope](../development/2026-11-16-console-completion/README.md),
complete [plan](../PLAN.md) and [A05 atlas reading](../development/2026-11-16-console-completion/notes/A05.md).
The other continuation retains H1 header work and its original timing HOLD.

## 1. Evidence and exclusive scope

The unchanged [cover/page-409 JPEG](atlas-cover-reference.jpg), SHA-256
`9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187`, supplies
artistic material direction. [Provenance](atlas-reference.json) identifies PDF
image object 3 and the unchanged atlas hash. It supplies no measured material,
corrected control semantics or physical-fidelity evidence. Atlas pp.409/411/418
keep labels editable and require the correct independent percussion controls.

The genuine [published T3 capture](native-gallery-ui-delivery-title/images/play-reference-1672x941.png)
has SHA-256 `1df7d50cda9b61640702a4c4b516be1ae1b7be9879aa6bba0feb06c0bf9e5e60`.
Both inputs are 1672 by 941 pixels. The [pre-candidate report](../development/2026-11-16-console-completion/reports/p1-authoring.json)
retains their decoded identities, exact patch sufficient sums, unchanged-before
screens, proposed constants and decoder versions. No candidate was rendered or
measured during this proposal.

Only the interior of `layout.performance_panel` may select a new private
`ReferencePanelMaterial::PerformanceP1`. Its canonical panel is
`(72,125,1044,139)`; its four-unit inset is `(76,129,1036,131)`, half-open through
`(1112,260)`. Preserve the complete outer shadows, rounded layers, accents,
screws and every child operation/argument/order. Select P1 only at the existing
performance-panel call in `paint_reference_composition`.

Preserve `Original`, `UpperRack`, `LowerRack` and any independently accepted H1
branch byte-for-byte except the smallest necessary enum/dispatch insertion.
Do not edit `Drawing`, fonts, assets, layout, hit geometry, headings, controls,
labels or any other panel caller. Reuse existing `UpperRackRaster`,
`UpperRackColorGuard`, `upper_rack_binary64` and `upper_rack_mix` unchanged.

P1 is eligible only in the existing reference composition: Dimensional Play,
logical width 1400–8192 and height 820–8192. Additionally require finite,
positive renderer scales no greater than 2 in either component. A greater or
invalid scale uses the exact existing `Original` interior. Query this new guard
only for P1; existing selectors acquire no new queries or behavior.

## 2. Fixed continuous field and arithmetic

Use one bilinear RGB field, with literal binary64 knots below. Columns are
canonical y **129,155,210,239,259**. Intermediate regions obscured by illustrated
or live controls are artistic interpolation, not recovered hidden pixels.

| Canonical x | RGB at y129 | RGB at y155 | RGB at y210 | RGB at y239 | RGB at y259 |
| ---: | --- | --- | --- | --- | --- |
| 76 | 25,24,24 | 19,19,19 | 19,19,20 | 21,21,21 | 22,22,22 |
| 124 | 37,36,36 | 26,25,25 | 24,23,23 | 23,23,23 | 24,24,23 |
| 312 | 38,36,34 | 31,31,30 | 30,30,30 | 28,28,27 | 31,30,28 |
| 520 | 45,45,47 | 34,34,34 | 33,32,33 | 31,30,30 | 36,34,32 |
| 600 | 52,50,52 | 36,35,36 | 31,31,31 | 30,29,27 | 39,36,34 |
| 828 | 45,43,44 | 33,32,33 | 29,28,29 | 28,27,25 | 37,34,32 |
| 1036 | 43,42,44 | 28,27,28 | 28,27,28 | 24,23,21 | 33,31,29 |
| 1112 | 30,29,29 | 22,21,21 | 24,23,24 | 24,23,21 | 25,24,22 |

Let `r` be the unchanged volatile binary64 barrier, applied after each listed
operation. Define `lerp(a,b,t)=r(a+r(r(b-a)*t))`. Clamp the sample X/Y to the
knot extents; select half-open intervals, with the final endpoint in the last
interval at fraction 1. Fractions are `r(r(X-Xi)/r(Xi1-Xi))`, analogously for y.
For each channel, lerp in x at the two bracketing y knots, then lerp those two
values in y. Do not contract multiply/add, change the interpolation order,
smooth the field, incorporate text/shadows or introduce patch-specific branches.

Use **97 adjacent rendered columns**, with 98 shared boundaries:

```text
offset(j) = r(r(double(inset.width)*double(j))/97.0), j=0..97
edge(j) = raster.x_boundary(r(double(inset.x)+offset(j)))
u(j) = r(r(double(j)+0.5)/97.0), j=0..96
X(j) = r(76.0+r(1036.0*u(j)))
logical_y = raster.logical_y(device_row)
v = clamp(r(r(r(logical_y-double(inset.y))-0.5)
            / r(double(inset.height)-1.0)), 0.0, 1.0)
Y = r(129.0+r(130.0*v))
```

For inset height at most 1, define v=0. Use the existing raster's clipped,
center-based boundaries and integer spans; never narrow unclipped coordinates.
One-pixel spans are points; longer spans end inclusively at `end-1`. Sampling
uses the entire mapped inset and never changes with clip or output extent.

**Precompute the horizontal values once per call.** At each column X, store the
three x-lerped channels for all five y knots in a fixed `97*5*3` double array.
Select the y interval/fraction once per visible row, and apply the same final
y lerp to each stored column. This reproduces the literal order above exactly:
it removes repeated x searches and arithmetic without changing a sample,
rounding boundary or support. No persistent cache, heap storage or data-derived
coefficient adaptation is allowed. Final channels use `std::round` (half away
from zero), clamp to 0–255, then `uint8_t`; alpha is 255.

## 3. Fixed grain and resource bound

Visit exactly **4,096 pairs**, each bright then dark, in increasing order:

```text
seed = 0xB3A09C21
k = 4*i + 2*m, i=0..4095, m=0,1
cx = 78 + upper_rack_mix(seed ^ k) % 1032
cy = 131 + upper_rack_mix(seed ^ (k+1)) % 127
u = r(r(r(double(cx)+0.5)-76.0)/1036.0)
v = r(r(double(cy)-129.0)/130.0)
amplitude = r(12.0-r(6.0*v))
```

Evaluate the same full field at this u/v. Add `+amplitude` for m=0 and
`-amplitude` for m=1 through r before channel conversion. Paint one canonical
unit square with `reference_composition_point` and `Drawing::rect`, after the
raster guard restores the caller scale. Collisions retain order; no retries,
renumbering, rejection sampling, clock or random-device state. Grain support is
inside `[78,1110) x [131,258)`, strictly within the inset.

Application draw-call bound is **97R+8,192**, where R is the visible device row
count. Canonical scale 1 has R=131 and **20,899** primitives. The conservative
full-domain R ceiling is 2,300, hence **231,292** primitives; the independent
reviewer must verify that bound before admission. A bounded 64-row crop has
at most 14,400 primitives and is not full-frame containment evidence.

Named arrays use 98 ints, 1,455 cached doubles, 120 literal field doubles,
eight x knots and five y knots: **13,096 bytes** on the supported 32-bit-int,
64-bit-double ABI, plus fixed scalars/guards. There is no application-owned
allocation/free, file I/O, offscreen target, texture creation or image-sized
storage. The grain mixer performs 16,384 fixed calls. Empty intersections may
return before grain only after proving the full inset has no visible pixels.
Restore color, scale, viewport, clip rectangle/enable and blend state as required
by the existing guards and unchanged caller contract.

## 4. Frozen quiet-patch screens

Decode both images to RGB with the report's Pillow 13.0.0/libjpeg-turbo 3.2.0
path, with no alignment, resampling, ICC, gamma or EXIF operation. Define encoded
`Y'=(2126R+7152G+722B)/10000`. Fit an affine plane in each patch, using the
report's exact integer sufficient sums and rational arithmetic; residual RMS
is the population RMS after that plane, not raw standard deviation. These are
artwork image statistics, not physical reflectance or photometric measurements.

All rectangles below are half-open x,y,width,height. They avoid semantic ink,
live controls, source controls, divider, screws and outer accents in both
retained inputs. No failed patch may be removed or shrunk after observation.

| ID | Rectangle | Reference mean Y' / RMS | T3 before mean Y' / RMS |
| --- | --- | ---: | ---: |
| TL | 110,134,96,9 | 30.939490 / 2.115185 | 39.772721 / 0.589366 |
| L | 100,165,48,64 | 23.550103 / 1.549017 | 31.081698 / 0.541365 |
| LB | 100,233,48,14 | 22.732127 / 1.530863 | 24.609398 / 0.523452 |
| CL | 505,166,32,68 | 32.696582 / 2.077726 | 30.612801 / 0.578150 |
| DIVL | 535,166,12,72 | 31.910044 / 2.014703 | 30.347794 / 0.446094 |
| CT | 580,134,96,9 | 44.517655 / 2.844767 | 39.772721 / 0.572208 |
| CR | 576,169,12,69 | 31.784396 / 2.227415 | 30.075398 / 0.599915 |
| BL | 98,250,112,6 | 23.716279 / 1.361005 | 22.740217 / 0.414422 |
| BC | 580,250,128,6 | 34.326342 / 1.669410 | 22.740217 / 0.415285 |
| RM | 1074,165,16,70 | 26.659483 / 1.657267 | 30.614687 / 0.578809 |
| RB | 944,242,40,12 | 28.638783 / 1.305399 | 23.404017 / 0.532848 |
| RT | 988,134,96,9 | 36.388487 / 2.690247 | 39.787433 / 0.526372 |

Require all **62 inequalities**:

- Each patch: mean Y' absolute error at most **3.0**, each of three RGB mean
  absolute errors at most **4.0**, and residual-RMS absolute error at most **1.2**.
- Equal-patch-weight mean Y' error at most **2.228881792818929**, exactly half
  the original 4.457763585637858 error. The report's exact rational ratio owns
  the decision; the displayed decimal is only a reader aid.
- Equal-patch-weight RMS error at most **0.6968632531987865**, half the original
  1.393726506397573 error. Calculate each exact SSE/N, convert once to binary64,
  take `math.sqrt`, then aggregate the 12 binary64 absolute errors with
  `math.fsum` and divide once by 12.0 in the report's fixed patch order.

The retained T3 image passes **28** and fails **34** of these proposed screens.
That is a source-image baseline observation, not native fixture execution.
Before paint, root must compile the new identical fixture against genuine
pre-P1 production and retain its executable/source identities. Its canonical
quiet patch RGB bytes must exactly reproduce the listed T3 patch hashes, or the
baseline discrepancy must be resolved and independently reviewed first.

## 5. Frozen native preservation matrix

Use the real `paint_instrument` and model, with one fixed case protocol shared
by genuine before and current executables. Default copied state is all four
banks at level 4; Upper/Lower applied and edited B; routes enabled; no fixed
registration; percussion On/Second/Normal/Slow; expression 0.625; pedal levels
3 and 7; held Upper key 24, Lower key 36 and pedal index 12; frame clock 38400,
sample rate 48000, publication revision 4, peak 0.125, prepared/running true.
No pending request; focus Upper drawbar index 4; fixed information strings.

Twenty-four main cases are required. Default scale is (1,1), viewport origin
(0,0), full clip disabled, BLEND, Dimensional Play. Ordinary output size is
ceil(W*rx)+2abs(ox) by ceil(H*ry)+2abs(oy), and viewport extent is ceil(W*rx) by
ceil(H*ry), installed at scale 1 before restoring the test scales.

| Case | Logical size and changes |
| ---: | --- |
| 0 | 1672x941; canonical numerical screen and unchanged default state |
| 1 | 1400x820; focus Percussion enabled; stored percussion Off |
| 2 | 1920x1080; focus Percussion harmonic; Third selected |
| 3 | 1920x820; focus Percussion volume; Soft selected |
| 4 | 1400x1080; focus Percussion decay; Fast selected |
| 5 | 1672x941; scales(1.5,1.5), origin(13,17); focus Expression; expression 0 |
| 6 | 1672x941; scales(2,2), origin(-13,-17); focus PedalDrawbar0; pedal levels0/8 |
| 7 | 1672x941; scales(1.25,0.75), origin(13,-17), NONE blend; focus PedalDrawbar1 |
| 8 | 1672x941; scales(2.01,1); complete Original fallback equality |
| 9 | 1672x941; scales(1,2.01); complete Original fallback equality |
| 10 | 1672x941; scale1.5, origin(13,17); left-edge physical clip |
| 11 | 1672x941; scale2, origin(-13,17); right-edge physical clip |
| 12 | 1672x941; scales(1.25,0.75), origin(-13,-17); top-edge physical clip |
| 13 | 1672x941; scale1, origin(13,-17); bottom-edge physical clip |
| 14 | 1672x941; enabled empty physical clip |
| 15 | 1672x941; disjoint physical clip |
| 16 | 8192x8192; scale2, bounded64x64 output; viewport origin(-L,-T), extent16384x16384; resource case only |
| 17 | 1399x820; inactive width; whole-frame equality |
| 18 | 1400x819; inactive height; whole-frame equality |
| 19 | 960x700; inactive compact; whole-frame equality |
| 20 | 1280x900; inactive default; whole-frame equality |
| 21 | 1672x941 Flat Play; whole-frame equality |
| 22 | 1672x941 Rotary; whole-frame equality |
| 23 | 1672x941 Service; whole-frame equality |

For clips, derive inset intrinsic device boundaries independently with the
same public float coordinate inputs but no candidate-produced mask:
`ceil(inset_edge*renderer_scale-0.5)`, before viewport translation. Denote them
L,T,R,B. Edge clips are respectively `(L-2,T-2,4,B-T+4)`,
`(R-2,T-2,4,B-T+4)`, `(L-2,T-2,R-L+4,4)`, `(L-2,B-2,R-L+4,4)`;
empty clip is `(L,T,0,0)`, disjoint is `(R+4,T+4,8,8)`. Install physical clips
at scale 1 before restoring test scale. Each nonempty clipped case also gets
an uncut companion. Compare quiet material intersections exactly; glyph-copy
fragments retain the pinned SDL clipped-text behavior, not an invented equality.
Repeat case0 after all other cases and on a fresh renderer; require exact RGBA
and copied state. Record case0 with upper applied A, cancelled and fixed D as
three additional state witnesses, preserving stored percussion independently
of the changing eligibility row. These are witnesses, not additional main cases.

Require zero changed pixels outside the independently derived mapped/clipped
inset and complete equality for inactive/fallback/disjoint/empty cases. Restore
scale, physical/logical viewport and clip, clip enable and blend. Source review
and a helper-scope observation establish color restoration. Compare all copied
model/snapshot/control values, layout, key/hit geometry, focus and musical state
before/after painting; no byte comparison over unspecified struct padding.

Inside the allowed inset, independently derive nonempty opaque-core probes for
all four percussion buttons, expression track/handle, both pedal tracks/caps,
divider, screws and rule segments. Require exact RGBA and all focused-control
cyan positions/counts. Check all unchanged text arguments/positions/fonts and
opaque glyph cores, including both headings, four underlabels, expression,
pedal values and eligibility. Antialiased edges may blend with the changed
background; that allowance never covers altered geometry, text or opaque ink.

## 6. Timing and final visual admission

The field cache above is part of the implementation contract, not an optional
optimization. It avoids repeated per-span knot searches while preserving every
literal operation. Resource bounds do not establish measured paint speed.

After coherent builds and comparisons, root reserves a quiet interval and runs
the unchanged `hammond_standalone_paint_benchmark` with **30 warmups and 300
measurements** per process. Use genuine retained pre-P1 and coherent candidate
binaries with reviewed source/object/dependency identities, identical toolchain,
configuration and benchmark code. No heap observer, sanitizer or profiler.
Run one process at a time on the same allowed logical CPU, recording affinity,
host/configuration, relevant SDL environment, load, exits, raw stdout/stderr,
UTC bounds and before/after input hashes. Shared-host isolation is not assumed.

Freeze this single eight-process batch before observing new timing:

| Order | Case | Side | Arguments |
| ---: | --- | --- | --- |
| 1 | Canonical | Before | `1672 941 dimensional mixed-held` |
| 2 | Canonical | After | `1672 941 dimensional mixed-held` |
| 3 | Minimum active | After | `1400 820 dimensional mixed-held` |
| 4 | Minimum active | Before | `1400 820 dimensional mixed-held` |
| 5 | Wide | Before | `1920 1080 dimensional mixed-held` |
| 6 | Wide | After | `1920 1080 dimensional mixed-held` |
| 7 | Flat control | After | `1672 941 flat mixed-held` |
| 8 | Flat control | Before | `1672 941 flat mixed-held` |

Require matching scene/layout/state/renderer metadata, `paired:false`, no
instrumentation, and exact Flat pixels. Independently recompute total median
from sorted positions 150/151 and nearest-rank p95 from 285. Report every
minimum/maximum, median, p95 and supplied paint/flush summary. Apply the existing
material investigation screen to both median and p95: growth **strictly greater
than 2 ms AND 15%** is HOLD for investigation; preserve all signals and the next
action. Do not pool different cases, trim samples or repeat to obtain a pass.
Any further run needs a separately reviewed prospective reason/protocol. Eight
processes provide descriptive comparisons, not confidence, equivalence, display
smoothness, audio-deadline or full-domain performance proof. A visible regression
rejects the scoped result regardless of numerical screens.

Independently inspect actual full frames at canonical, minimum-active, wide,
unequal-aspect, compact, Flat, Rotary and Service sizes. Reject vertical seams,
interpolation bands, bright speckle clusters, unreadable controls/eligibility,
detached panel lighting or altered child appearance. Numerical patches cannot
override full-frame rejection. Execute affected drawing/scaled-view/material,
percussion, UI geometry/state/preset and existing panel suites without weakening
old assertions. Preserve failed reports, genuine baseline binaries and current
source/executable/state/pixel identities; update README only with admitted actual
application captures.

Preserve 47 parameter identities, state 4/readers 1–3, 91 running sources, plugin
UUIDs, nominal dry Engine, four banks, 147 playing keys, 24 presets, 68 controls and
all M0–M9 exits. P1 closes no whole-interface 1:1, native accessibility, physical
fidelity, hardware-device, DAW or signed-release gate.
