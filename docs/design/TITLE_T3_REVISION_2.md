# T3 revision 2: reduce the fixed upper-highlight displacement

**Proposed for independent admission; no revised candidate has been rendered.**
A25, 17 November 2026. This document selects one implementation change after
the retained v1 rejection. The original [T3 contract](TITLE_T3_CONTRACT.md),
SHA-256 `6e45c095331e4d2a32cb111ebe2be74b7fad3dd7f6fb89a675d68c4a0310cae7`,
and its [admission](../reviews/TITLE_T3_ADMISSION.md) remain unchanged. Every
original geometry, density, support, state, compatibility and visual acceptance
requirement remains binding. A26 independently reviews this proposal before
root assigns implementation.

## Retained failure and cause

The [rejection receipt](../development/2026-11-16-heading-title-continuation/reports/t3-v1-rejection.json)
and [original native log](../development/2026-11-16-heading-title-continuation/reports/t3-affected-tests.log)
identify painter
`40de44893f3b88fef04732bf5a7607d4ce7db3cd4206f3712a5b71fa070a9029`.
The material suite records 1,317 checks and two failures: at 1400x820, renderer
scales 1 and 1.25 both give warm-ink top 16 against expected 17.1384788655 in
the receipt, an error of 1.1384788655 exceeding the unchanged maximum 1.
All other material checks pass. Canonical density 5,512 passes the original
[4,500,6,000] band, but cannot override the failed geometry.

The title anchor and font fitting are not displaced. The additional upward
highlight crosses a software-renderer destination boundary. In the unchanged
Serif atlas, `O` and `S` have `bearing_y=-30`; their first alpha rows have
maxima 252 and 251, with respectively seven and nine values at least 128.
These are ink-bearing rows, not transparent padding. At 1400x820, binary32
arithmetic gives `f=0.8373205661773682`, `g=size/40=0.8948863744735718`, and
`y=10.021254539489746`. `Drawing::text` computes the glyph destination top as
`float(float(pass_top + float(38*g)) + float(bearing_y*g))`.

| O/S pass | Destination top before renderer scale | Physical row at scale 1 | Physical row at scale 1.25 |
| --- | ---: | ---: | ---: |
| Unchanged main face | 17.180347442626953 | 17 | 21 |
| Rejected v1 highlight | 16.76168441772461 | 16 | 20 |
| Proposed revision 2 highlight | 17.075679779052734 | 17 | 21 |

Rows above omit the common integer viewport origin. The scale-1.25 rows map
back to logical 16.8 for the face/revision and 16 for v1. SDL multiplies each
destination component in binary32 and truncates toward zero. The exposed v1
O/S row has enough alpha to meet the warm predicate, as the native failure
confirms; later face copies begin below it. The material test's binary32
expected top is 17.1384792328, giving the same rejection as the receipt's
exact-ratio value. The correction addresses this destination/alpha interaction.

## Exact revised implementation

Change only the highlight coefficient from `0.5F` to `0.125F`. Keep all five
complete live `TONEWHEEL ATLAS` draws, their order, `size`, `TextFace::Serif`,
colors and other arguments exactly as follows:

| Order / purpose | x argument | top argument | RGBA |
| --- | --- | --- | --- |
| 1. Cast shadow | `x + scale.sx` | `y + 2.0F * scale.sy` | `(4,5,4,255)` |
| 2. Lower dark bevel | `x + scale.f` | `y + scale.f` | `(100,65,28,255)` |
| 3. Upper highlight | `x` | `y - 0.125F * scale.f` | `(255,231,184,255)` |
| 4. Added stroke weight | `x + scale.f` | `y` | `(212,171,103,255)` |
| 5. Main brass face | `x` | `y` | `(226,192,135,255)` |

One eighth is an exactly representable fixed nominal offset. It retains an
upper relief pass and corrects the offending minimum-active destination rows
without introducing a size branch, renderer query or state-dependent palette.
The canonical scale-1 highlight destinations remain identical to v1 after
integer conversion: O/S top 19 and the other title glyphs top 20. Thus all 70
canonical candidate COPY operations retain identical source rectangles,
integer destinations, modulation and order. This predicts the retained 5,512
canonical count; it is not a newly observed density result.

Keep every existing calculation through `x`, `y` and `size` in its original
binary32 order, including width fitting, mapped control exclusions and centered
clamping. Activation, title string, caption, side rules, T2 headings, shared
header, Drawing, font atlas, hit geometry and all state remain unchanged. No
clipping workaround, texture, font regeneration or renderer-state mutation is
introduced. The bound remains five text calls, at most 70 glyph copies and
42 additional copies over the genuine two-pass pre-T3 baseline.

## Exact support consequences

The original support rule remains the union of the genuine pre-T3 two-pass
destinations and the revised five-pass destinations, derived independently
before reading candidate differences. Apply the same binary32 glyph arithmetic,
component-wise SDL truncation, viewport origin, output/viewport intersection
and enabled clip, including empty clips. Inactive layouts still have no
allowance. Rejected-v1 destinations must not enlarge a revision-2 comparison
mask; the old v1 comparator is retained as historical evidence.

Read-only calculation from raw atlas metrics gives the following zero-origin,
unclipped unions. Counts describe destination support, not changed pixels.

| Logical size / renderer scale | v1 union pixels | Revision 2 union pixels | Revision 2 outer half-open bounds |
| --- | ---: | ---: | --- |
| 1672x941 / 1 | 14,102 | 14,102 | `(602,19,1067,55)` |
| 1400x820 / 1 | 9,534 | 9,490 | `(504,17,893,45)` |
| 1400x820 / 1.25 | 15,185 | 15,129 | `(630,21,1117,57)` |

The outer bounds are summaries, never replacement masks. The shifted highlight
has unchanged x/width/height and lies between its original top and the unchanged
face top. On the admitted domain those equal-width rectangles overlap, so this
revision adds no support outside the v1 union. Each case must nevertheless use
its own exact, possibly smaller, revised union. Other scales do change copy
destinations: for example, canonical scale 1.25 moves the twelve highlight
glyphs with bearing -29 down one physical row. No scale, unequal-aspect, partial
clip or resource-crop case can be omitted on the strength of canonical equality.

## Preservation and remaining gates

Keep the [genuine pre-T3 identity receipt](../development/2026-11-16-heading-title-continuation/reports/t3-baseline-identity.json),
its accepted painter `94186192085435a756f9e1854e3aefe807407befa49e1cc978c07968436ca5db`
and the five original binaries at `../t2-native`. Keep the rejected source,
six binaries at `../t3-rejected-native`, original reports and thirteen-image
`native-gallery-heading-title-v1` gallery. The separately saved
[v1 painter](../development/2026-11-16-heading-title-continuation/inputs/InstrumentView-t3-v1.cpp)
and [v1 comparator](../development/2026-11-16-heading-title-continuation/inputs/compare_title_typography-v1.py)
must also remain unchanged. Revision 2 needs distinct identities and evidence.

After independent admission, root must assign the single painter edit and the
comparator's exact revised pass declaration, then build coherently and execute
the original gates. These include the unchanged warm-ink width `464*f +/-3`,
height `33*f +/-1`, top `11.5*sy+8.5*f +/-1`, center `width/2-f +/-2`, pixel
count, caption and control/header containment assertions; baseline density
3,863 and revised [4,500,6,000] density with all five threshold/bounds records;
all 158 genuine paired support/state cases and their original required
transforms/inactive equalities; affected control/input/native suites; all 213
protected inputs, including the identical replay repair on both sides; and
independent actual-frame visual admission with the reference and genuine
before frames. Filled counters, halos, muddy strokes, clipping, lost subtitle
or disproportionate brightness remain grounds for rejection.

No revised render, build, test or acceptance is claimed here. README capture
refresh, final qualification and publication belong to root after acceptance.
Literal whole-interface 1:1 remains unmet and unwaived; physical/model,
real-display/DPI, native accessibility, platform/host/device and release gates
retain their separate status.
