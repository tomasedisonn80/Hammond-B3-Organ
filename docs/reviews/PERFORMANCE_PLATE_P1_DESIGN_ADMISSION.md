# P1 performance plate — independent design admission

Reviewer **A11**, wave 2, 17 November 2026 UTC. This review precedes production
paint. It covers the [P1 contract](../design/PERFORMANCE_PLATE_P1_CONTRACT.md)
and [A08 authoring report](../development/2026-11-16-console-completion/reports/p1-authoring.json).

## Decision

**ADMIT the frozen design for implementation after root verifies the genuine
pre-P1 fixture and its canonical quiet-patch bytes.** The design has no remaining
blocking correction. This admission does not accept a candidate, execute a
native test, establish measured performance, or close whole-interface 1:1.
Root must review A12's actual fixture before authorizing production paint.

The accepted contract SHA-256 is
`20c8839d38229bf24d983eac0baad7381f601c4e6763bbbe556bcdfa6c75ae45`.
The unchanged authoring report SHA-256 is
`f25c5c479c6c1ffb304028c8a306a7873f155eec6f6d5f9831ed6e93862290e2`.
The [independent audit](../development/2026-11-16-console-completion/reports/p1-design-audit.json)
SHA-256 is `a5204bca1a85e61911e573e5eaad5646a96d0dfce8ce9ba6ec575b5e5295a4fa`.

## Evidence and independent numerical check

I directly inspected both complete 1672×941 images. Their file identities
match the proposal:

| Input | SHA-256 |
| --- | --- |
| Original reference JPEG | `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187` |
| Published T3 native PNG | `1df7d50cda9b61640702a4c4b516be1ae1b7be9879aa6bba0feb06c0bf9e5e60` |

Pillow 13.0.0/libjpeg-turbo 3.2.0 reproduces both decoded RGB identities and
all 24 patch RGB hashes. Literal independently transcribed rectangles reproduce
every RGB sum/mean, encoded-luma sum/mean, affine-plane sufficient sum,
exact residual mean-square value and binary64 RMS. No producer functions or
candidate pixels were used. Sixteen reported residual ratios are unreduced;
their exact rational values agree with the independently reduced fractions.

All twelve patches avoid foreground in both images. TL/CT/RT stop above heading
and rule ink; L/LB remain left of the percussion buttons and captions; CL/DIVL
stay between the last percussion button and divider; CR stays left of the live
expression track and illustrated scanner buttons; BL/BC avoid eligibility ink
and the bottom border; RM/RB avoid the illustrated controls and live pedal
tracks. These observations apply to the retained canonical inputs. The future
fixture still must prove the same source patch bytes before painting.

| Recomputed quantity | Result |
| --- | ---: |
| Individual patch inequalities | 60 |
| Aggregate inequalities | 2 |
| T3 pass / fail | **28 / 34** |
| Equal-patch luma-mean MAE | **4.457763585637858** |
| Exact luma-mean MAE | **6324946007329 / 1418860800000** |
| Exact half-error threshold | **6324946007329 / 2837721600000** |
| Equal-patch residual-RMS MAE | **1.393726506397573** |
| Half RMS-error threshold | **0.6968632531987865** |

The exact mean-error ratio owns its aggregate decision. Summing rounded
binary64 mean differences instead produces a last-bit difference; that is not
the specified calculation. RMS uses exact rational population mean square,
one binary64 conversion and square root, then fixed-order `math.fsum`/12.
All 62 recorded decisions and displayed differences reproduce. No patch,
threshold, denominator, statistic or failed baseline screen was changed.

## Field, geometry and resources

The eight-by-five literal RGB table and all knot, column, grain and seed values
agree between contract and report. Bilinear interpolation is continuous at the
shared knots; the 97 columns share boundaries, so there is no independent edge
rounding gap. The fixed horizontal cache preserves the stated x-then-y
arithmetic. Sampling remains anchored to the full inset under clipping.
This establishes the design's consistency; actual frames must still reject
visible bands, seams, bright grain clusters or detached lighting.

Public source geometry maps the performance panel `(72,125,1044,139)` and then
applies the existing four-unit inset. Renderer scale must be finite, positive
and at most two in each component. P1 alone receives that new guard; greater
or invalid scales select the existing Original interior. Existing active-layout
limits and all other selectors remain unchanged.

The full-domain row bound is conservative. At logical height at most 8192,
`sy <= float32(8192/941) = 8.705632209777832`. The existing endpoint mapping and
inset operations have accumulated absolute rounding error below 0.001 logical
unit, giving inset height at most `131*sy + 0.001 < 1140.5`. Center-based spans
at renderer scale at most two therefore have at most **2281** rows. Clipping
only reduces this count, so the frozen ceiling **2300** is valid. Direct
float32 evaluation at the maximum-height corner also gives 2281 rows.

| Resource | Independently verified bound |
| --- | ---: |
| Named fixed-array payload | **13,096 bytes**, plus fixed guards/scalars |
| Grain marks / mixer calls | **8,192 / 16,384** |
| Canonical draw primitives, 131 rows | **20,899** |
| Full-domain conservative primitives, 2300 rows | **231,292** |
| Bounded 64-row crop primitives | **14,400** |

The grain support lies strictly inside the inset. The scoped raster restores
scale before the grain uses `Drawing::rect`; the color guard covers both
operations. Existing raster/color/mixer helpers must remain unchanged.
No heap, image-sized storage, texture, persistent cache or I/O is permitted.
These are source/design bounds, not measured allocation or timing results.

## Required implementation and acceptance gates

1. Freeze and independently review A12's fixture, build it against genuine
   pre-P1 production, retain executable/source identities, and match all
   canonical quiet-patch bytes to T3. Resolve and independently review any
   discrepancy before implementation. A different model's screenshot cannot
   silently replace the retained source baseline.
2. Change only the private P1 selector/material and the existing performance
   call in `paint_reference_composition`. Preserve borders, shadows, screws,
   headings, all child arguments/order and correct live semantics. The source
   illustration's erroneous percussion labels are not implementation targets.
3. Execute all 24 main cases, all nonempty clip companions, repeat/fresh renderer
   cases, and applied A/cancel/fixed-D witnesses. Including an uncut companion
   for the nonempty but disjoint clip is appropriate. Root/A12's planned 34
   records cover these cases without dropping a requirement.
4. Independently derive masks from public float geometry; require exterior
   equality and complete inactive/fallback/empty/disjoint equality. Preserve
   opaque child cores, focus, semantic state, geometry and hit targets. Observe
   helper-only color restoration as well as full-renderer state; final frame
   rendering can otherwise hide a helper's color leak. Do not invent equality
   for pinned SDL clipped glyph fragments or exempt opaque ink as antialiasing.
5. Run the frozen eight timing processes in order: canonical before/after,
   minimum after/before, wide before/after, Flat after/before. Each uses the
   unchanged 30-warmup/300-measurement benchmark, one process at a time on the
   same allowed CPU. Retain identities, metadata, affinity, environment, load,
   UTC bounds, exits and all raw samples. Require `paired:false` and exact Flat
   pixels. Recompute median from positions 150/151 and nearest-rank p95 from
   position 285. Growth strictly above both 2 ms and 15% in either statistic
   means investigation HOLD. No trimming, pooled scenes or rerun-for-pass.
6. Independently inspect all required full-frame views and run affected existing
   suites without weakening assertions. Actual accepted app captures, with
   honest remaining gaps, may then update the README.

## Corrections and boundaries

A11 reported two editorial defects; root corrected both before this admission:
the stray `+` in `accents,+screws`, and nonexistent caller name
`paint_reference_instrument` (actual source: `paint_reference_composition`).
Neither correction changed a measurement, criterion, field constant or scope.

This review ran no native executable, build, benchmark, paint, capture or
allocation observer. The separate H1 owner and original timing HOLD remain
untouched. Preserve the standing 47 parameters, state 4/readers 1–3, 91 running
sources, plugin UUIDs, nominal dry engine, four banks, 147 playing keys,
24 presets and 68 controls. Physical calibration, host/release qualification,
native accessibility and whole-interface visual fidelity remain separate gates.
