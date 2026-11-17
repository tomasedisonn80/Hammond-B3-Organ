# T3 revision 2: independent admission

**Decision: admit the exact revision for implementation.** A26, 17 November
2026, independently reviewed
[TITLE_T3_REVISION_2.md](../design/TITLE_T3_REVISION_2.md), SHA-256
`e06ddb46f48a4d75c5c305474699223b41a0febc3e3db7d077048841356554e9`.
No blocking correction was found. This authorizes the specified attempt, not
candidate acceptance. The [original contract](../design/TITLE_T3_CONTRACT.md)
and [original admission](TITLE_T3_ADMISSION.md) retain every acceptance limit;
the rejected attempt remains rejected.

The only implementation change is the upper-highlight coefficient from `0.5F`
to `0.125F` in `reference_header`. All five complete live title draws, their
order, palettes, x positions, font size and face remain as specified. The
geometry calculations, width fitting, title anchor, caption, rules, T2 headings,
activation predicate, shared Drawing/font inputs and model remain unchanged.
No renderer-dependent branch or clipping workaround is admitted.

## Independent diagnosis

The retained [native log](../development/2026-11-16-heading-title-continuation/reports/t3-affected-tests.log)
records two failed material checks out of 1,317. Both are the 1400x820 active
title, at renderer scales 1 and 1.25. Its warm-ink top is 16, versus the
receipt's expected 17.1384788655, exceeding the unchanged one-unit maximum by
0.1384788655. The C++ expression evaluates to 17.1384792328 in binary32 and
gives the same rejection. The [rejection receipt](../development/2026-11-16-heading-title-continuation/reports/t3-v1-rejection.json)
correctly separates this failure from the passing canonical density.

I independently parsed the raw Serif metrics and decoded its alpha RLE in
memory, then reproduced Drawing and SDL arithmetic with binary32 rounding
after each operation. `O` and `S` have `bearing_y=-30`; their first alpha rows
have maxima 252 and 251, with seven and nine samples at least 128. These rows
carry ink. At 1400x820, `f=0.8373205661773682`, `g=0.8948863744735718` and
`y=10.021254539489746`. The destination calculation is
`fl(fl(pass_top + fl(38*g)) + fl(bearing_y*g))`.

| O/S pass | Logical destination y | Observed or derived top at renderer 1 | At renderer 1.25 |
| --- | ---: | ---: | ---: |
| Unchanged main face | 17.180347442626953 | 17 | 16.8 |
| Rejected highlight | 16.76168441772461 | 16 | 16 |
| Revision 2 highlight | 17.075679779052734 | 17 | 16.8 |

The last two columns remove the common integer viewport origin and divide the
truncated physical destination by renderer scale. The rejected row is confirmed
by native evidence; the revised row is a source calculation, not a new render.
The unchanged face begins below the rejected upper row, so it cannot cover that
exposed highlight. Reducing the fixed displacement addresses this cause without
moving the title anchor or changing its geometry test.

## Canonical result and exact support

At unscaled 1672x941, the proposed O/S destination changes from
19.5499992371 to 19.9249992371, which both truncate to 19. The twelve other
highlight glyphs still truncate to top 20. I independently compared all 70
source rectangles, integer destinations, colors and call positions: they are
identical to the rejected candidate at this canonical transform. This predicts
its same density, while leaving a fresh revision-specific observation required.

Direct decoding of the existing images reproduced the following counts in
the original half-open ROI `(590,14,490,46)`, using only
`2126*R + 7152*G + 722*B >= threshold*10000`:

| Existing image | Y' 80 | Y' 100 | Y' 120 | Y' 140 | Y' 160 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original reference | 5,639 | 5,415 | 4,991 | 4,502 | 3,785 |
| Genuine accepted T2 | 4,150 | 3,863 | 3,601 | 3,200 | 2,690 |
| Rejected T3 v1 | 5,774 | 5,512 | 5,304 | 5,029 | 4,694 |

At threshold 100 the corresponding half-open bounds are
`(603,20,1067,53)`, `(602,20,1065,53)` and `(602,19,1066,53)`.
The last row remains evidence of v1 only. The original `[4500,6000]` band and
separate warm-ink predicate are unchanged.

My independent per-glyph union calculation reproduces the revision's declared
zero-origin, unclipped support:

| Logical size / renderer scale | Old two-pass plus revised five-pass union | Outer half-open bounds |
| --- | ---: | --- |
| 1672x941 / 1 | 14,102 pixels | `(602,19,1067,55)` |
| 1400x820 / 1 | 9,490 pixels | `(504,17,893,45)` |
| 1400x820 / 1.25 | 15,129 pixels | `(630,21,1117,57)` |

The genuine pre-T3 calls and revised calls alone define the allowance. Including
rejected-v1 destinations would incorrectly retain the minimum-size upper row.
Outer boxes, changed-pixel masks and arbitrary dilation remain inadmissible.
Positive renderer scales preserve the revised top between its original top and
the face top; their equal-width glyph rectangles overlap throughout the admitted
domain, so the revision introduces no support beyond the old v1 union. This
does not permit reusing that larger union. Every transform must independently
apply component-wise binary32 scaling, truncation toward zero, viewport origin
and output/viewport/enabled-clip intersection; enabled empty clips remain empty.

Canonical renderer 1.25 changes twelve highlight destinations, and other
unequal layouts also change destinations. Canonical equality therefore supplies
no exemption from the original matrix. Partial texture clipping still uses
SDL's actual clipped-copy behavior, not a crop of an uncut resampling.

## Work bound and retained gates

The change preserves five text calls and at most 70 nonempty glyph copies,
42 additional copies over the genuine two-pass baseline. It adds no loop,
storage, explicit allocation, asset, renderer query or audio work. Existing SDL
command/intermediate allocation and frame deadlines remain outside this bound.

Root must retain and execute all original requirements at coherent, stable
revision-specific inputs:

- The unchanged material suite, including 24 complete and 16 clipped header
  cases, keeps width `464*f +/-3`, height `33*f +/-1`, top
  `11.5*sy+8.5*f +/-1`, center `width/2-f +/-2`, more than 1,000 warm title
  pixels, caption separation/geometry, fifteen caption letters and zero escapes.
- All 158 genuine pairs remain: 44 typography, 66 percussion and 48 supplemental
  clip cases, with both original default clip assertion runs. Preserve exact
  inactive frames, all original scale/origin/clip cases, state/model/renderer
  checks and maximum-size crop limitations. The old T2 baseline remains the
  comparison baseline; the rejected candidate cannot replace it.
- Baseline density and bounds must reproduce; record all five candidate
  thresholds/bounds and require the original density band. Preserve all 213
  protected inputs, including the identical separately admitted replay repair,
  and run the affected control/input/native gates.
- Independent actual-frame review at canonical, minimum-active and wide sizes,
  with reference/before images and compact/Flat checks, must still reject filled
  counters, halos, muddy strokes, clipping, a lost subtitle or excess brightness.

No revised candidate was implemented, built or executed during this review.
Original failure evidence, source, six rejected binaries and thirteen images
remain preserved. Root can now assign the exact painter change and independent
comparator revision, followed by qualification and actual README captures.
Literal whole-interface 1:1 remains unmet and unwaived; physical, real-display,
accessibility, platform/host/device and release gates remain separate.
