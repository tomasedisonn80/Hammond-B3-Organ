# T3 title contract: independent admission

**Decision: admit the exact proposed contract for implementation.** A16,
16 November 2026, reviewed
[TITLE_T3_CONTRACT.md](../design/TITLE_T3_CONTRACT.md), SHA-256
`6e45c095331e4d2a32cb111ebe2be74b7fad3dd7f6fb89a675d68c4a0310cae7`.
No blocking correction was found. This admits an attempt with the frozen
criteria; it does not accept a candidate or establish whole-interface 1:1.

The review read the complete repository instructions, M0–M9 plan, current
session README, A11's proposal and A09's compatibility analysis. It inspected
the original reference and the genuine current baseline at their native size,
then independently checked pixel counts, atlas metrics, painter arguments,
existing material assertions and the pinned SDL software COPY conversion.
No candidate was painted and no production or test source was changed.

## Independent image observations

The reference title has stronger, brighter strokes and more visible relief than
the application title. Their gross position and extent are already close. The
proposed emphasis on weight and relief while retaining size and anchors is
consistent with those observations. It remains an artistic approximation using
the existing live atlas, subject to the contract's actual-frame visual review.

Direct RGB decoding, without resizing or color transformation, reproduced the
following counts in the half-open ROI `x=590..1079, y=14..59`. The predicate is
exactly `2126R + 7152G + 722B >= threshold * 10000`; it has no hue restriction.

| Encoded Y′ threshold | Original reference | Historic app | Genuine current baseline |
| --- | ---: | ---: | ---: |
| 80 | 5,639 | 4,150 | 4,150 |
| 100 | 5,415 | 3,863 | 3,863 |
| 120 | 4,991 | 3,601 | 3,601 |
| 140 | 4,502 | 3,200 | 3,200 |
| 160 | 3,785 | 2,690 | 2,690 |

At threshold 100 the reference bounds are `(603,20,1067,53)` and both app
captures give `(602,20,1065,53)`, expressed as half-open bounds. The original
and historic image hashes reproduce the contract. The genuine capture at
`../baseline-gallery/images/play-reference-1672x941.png`, relative to the
repository root, has SHA-256
`b7f4ca213575c63a6c612c577e484bc591934558128ff30d1ee3c674335d509c`.
The differing full-frame identity does not alter these title observations.

The admitted inclusive candidate band `[4500,6000]` reduces absolute error
against 5,415 by at least **41.0438%** relative to 3,863. The contract's
at-least-40% statement is therefore correct. This is a bounded image statistic;
it is separate from the existing warm-ink geometry test and does not measure
physical luminance or overall fidelity.

## Palette, geometry and work

The five ordered passes preserve the old shadow, add one lower bevel, one
half-font-unit upper highlight and one font-unit horizontal weight pass, then
apply the main brass face. All RGBA values are valid literal bytes. Their
unblended encoded Y′ values, in order, are `4.7152`, `69.7696`, `232.7090`,
`174.8070`, and `195.1130`. The lower bevel is below the primary count threshold.
New offsets use isotropic `f`; the retained shadow alone keeps the existing
`sx, 2*sy` displacement. No proposed pass changes fitting or tracking.

The current `reference_header` still contains the original two title calls.
The inspected post-T2 painter SHA-256 is
`94186192085435a756f9e1854e3aefe807407befa49e1cc978c07968436ca5db`.
The contract preserves the existing control exclusions, binary32 width fit,
clamped center, Serif face and `42.75*f` / `11.5*sy` size/top calculations.
It also preserves the caption, rules, controls, shared header and active-layout
predicate. FontData and Drawing hashes independently match the contract.

Independent binary32 evaluation of the retained atlas at canonical size gives
glyph scale `1.068750023841858`, advance width `467.04376220703125`, first pen
`602.4781494140625`, and top `11.5`. There are 15 characters, with 14 nonempty
glyphs. Five passes therefore require at most 70 glyph copies, compared with
28 before: exactly 42 additional copies in an unclipped visible title. This
establishes a fixed draw-call bound; SDL command storage and clipped-copy
intermediate surfaces can allocate, as the contract already allows.

## Support and retained acceptance

The prescribed destination arithmetic matches `Drawing::text`: per-glyph
bearings, ascent 38, pixel height 40, conditional two-pixel atlas gutters and
assignment-rounded advances. SDL 2.32.10 scales each destination component,
truncates each to an integer, then applies the viewport origin and surface clip.
Flooring negative origins, rounding combined right/bottom endpoints, or using
an uncut image as a clipped-copy oracle would change that behavior.

At canonical scale, zero origin and no clip, the independently derived union
of all old and proposed copy rectangles contains **14,102 pixels** and has
outer half-open bounds `(602,19,1067,55)`. The outer rectangle is only a summary;
the per-glyph union is the admitted support. It was computed from source
metrics without any candidate pixels. Other transforms must use their own
derived union; inactive frames have no allowance.

The existing C++ predicate (`R>=130`, `G>=105`, `R>=G`, `10B<=9R`) remains
distinct from Y′ counting. Its unchanged title width, height, top, center,
caption separation and containment assertions remain binding, including the
24 complete and 16 clipped header cases. Nothing in this review promises that
the proposed pixels will pass them. A failed candidate must retain its original
report and receive the explicit revision procedure already specified.

## Handoff

Root should accept and freeze T2, retain actual immediately-pre-T3 binaries and
source identities, then implement these exact five passes. The current genuine
baseline resolves the historic count question; it does not replace the required
post-T2/pre-T3 binary receipt. The already specified paired support/state
comparison, affected tests, canonical count band and independent actual-frame
review determine candidate acceptance. No additional gate or relaxed tolerance
is introduced here. Physical audio, display/DPI, accessibility, platform and
release qualification retain their existing status.

Root separately admitted A15's `main.cpp` replay-observation repair after a
reproduced baseline focus-loss failure. Both sides of the T3 transition must
contain that same repair. The session-wide A09 inventory therefore records
`main.cpp` as a separately reviewed exception to the original baseline; the
T3 transition itself must preserve all 213 protected inputs. This distinction
does not relax any visual or state-preservation criterion.
