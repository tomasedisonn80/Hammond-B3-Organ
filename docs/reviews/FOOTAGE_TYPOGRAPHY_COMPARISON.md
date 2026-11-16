# T1 footage typography — independent paired comparison

**The scoped T1 preservation comparison passes all 110 pairs.** The candidate
changes 295,560 pixels, all inside independently declared glyph support. There
are **zero escaping pixels or channels**, and all **44 required exact whole
frames** remain byte-identical. This accepts the finite software transition
under the [admitted contract](../design/FOOTAGE_TYPOGRAPHY_CONTRACT.md). Actual
full-frame visual review and the separately reviewed Upper/Lower fixture
assertion transition remain additional gates. Literal whole-interface 1:1,
native display/DPI/accessibility, audio and physical fidelity remain open.

## Independence and fixed support

A29 read the full standing agent obligations, M0–M9 plan, active scope, contract,
font atlas, unchanged `Drawing::text`/`text_width`, layout endpoints, both native
fixture sources and pinned SDL software COPY implementation. The new
[comparator](../../tools/compare_footage_typography.py) imports no painter,
candidate helper, fixture helper or earlier material/composition mask.

The 66 original percussion cases and 44 supplemental typography cases are
declared as a literal independent inventory. The latter cover all 18 focused
manual drawbars, both banks, levels 0/4/8, pending/held state, reference/minimum/
larger/unequal logical sizes, fractional layout, positive and negative viewports,
fractional and unequal renderer scales, physical/logical glyph clips, enabled
empty/disjoint clips, five inactive layouts and two bounded maximum-size crops.

The comparator parses all 95 glyph metrics from the pinned original Serif atlas.
It evaluates the old fitted complete string and new five-run fraction geometry
with binary32 arithmetic. It includes actual `Drawing` baseline reconstruction,
bearings, conditional two-pixel transparent gutters, independent coordinate and
extent scaling, SDL software integer truncation and viewport translation. The
requested and reconstructed-baseline destination rectangles coincide in all
9,548 declared glyph records; both are still represented explicitly.

The allowance is the **union of old/new glyph-copy rectangles**, expanded by at
most one device pixel around each copy and intersected with the caller's
physical viewport, clip and output. It is never a complete label box, rack,
candidate-supplied region or changed-pixel-derived region. At canonical size,
the union contains **7,928 pixels**, versus 19,044 pixels in the eighteen label
boxes. The full source-derived declaration was written to
[mask.json](../development/2026-11-16-conversion-material/reports/A29-paired-comparison/mask.json)
**before the first native invocation**.

Each pair validates its independent case dimensions/transforms/state fields and
requires complete before/after metadata equality. Supplemental records serialize
the whole public copied model/layout without structure padding. Independent
checks include both bank identities, expected clocks/constants/held notes,
68 controls, 147 playing keys, 24 presets and all eighteen unchanged label,
value and hit rectangles. All RGBA channels outside the glyph union are exact.
Every cyan focus pixel is compared separately, including pixels inside an
otherwise admitted region. Full active glyphs also require nonempty opaque
bright ink; the unchanged native expectations provide the stronger per-glyph
literal/contrast tests under their actual clip transform.

## Observed clipping premise correction

Before any typography edit, the proposed fixture assumed a clipped glyph must
equal a crop of the unclipped rendering. It failed on the accepted Lower painter.
A25 retained the original fixture, contract and diagnostic. A29 independently
checked the failing point and SDL source; the
[independent clip receipt](../development/2026-11-16-conversion-material/reports/A29-clip-correction-review.json)
records the exact source hashes and geometry.

For Upper index 1's old `5`, the device-copy rectangle is
`[199,206) × [489,499)`. The differing pixel `(203,492)` is strictly inside it.
SDL's scaled COPY path clips source/destination proportionally and rounds the
source rectangle before resampling when the destination remains inside the
surface. Consequently, clipping can change interior glyph samples.

The independently corroborated prepaint correction preserves exact non-glyph
companion pixels and strict caller-exterior/state behavior, records interior
glyph differences separately, and checks surviving strong literal glyph pixels
using the same caller clip. It changes **no T1 before/after allowance**. The
completed before fixture retains 125 interior clipped/full differences; the
candidate retains 128. Neither number is an escaping before/after pixel count.
The original failure is not rewritten as a pass. The full reasoning and original
evidence remain in [A25's admission](FOOTAGE_TYPOGRAPHY_ADMISSION.md).

## Executed results

Root explicitly froze native sources, HEAD, build inputs and all four binaries.
A29 then ran the complete comparator in **102.260894 seconds**, exit 0. The
[complete report](../development/2026-11-16-conversion-material/reports/A29-paired-comparison/report.json)
contains every case, metadata/RGBA hash, per-label observations, focus identity,
material statistics and native invariant result. All recorded source, executable
and build identities remained unchanged throughout the run. Root's separate
coherent build evidence establishes compilation; hashes alone do not.

| Gate | Observed result |
| --- | --- |
| Paired cases | **110/110 pass**: 66 original percussion + 44 typography |
| Compared / protected pixels | **286,098,649 / 285,470,445** |
| Changed pixels | 295,560, all inside the declared glyph union |
| Escaping pixels / channels | **0 / 0** |
| Required exact whole frames | **44/44** |
| Cyan focus pixels | **100,433 exact positions/colors** across the paired matrix |
| Material patches | **12/12 exact RGB and exact derived statistics** |
| Original percussion invariant runs | Both 66/66 pass; 1,410 literal glyph checks per run |
| New typography invariant runs | Both 44/44 pass; 59 state restorations and 11 clip companions per run |
| Full active protected probes | 936 opaque probes / 231,858 pixels per typography run |
| Typography literal checks | Before 2,094 / candidate 2,097; partial clips account for different visible counts |
| Typography strong-ink samples | Before 42,143 / candidate 45,208 |
| Typography focus / repeat cases | 26 focus cases / both same-renderer and fresh-renderer repeats pass |
| Retained paired output | 15,495,455 bytes, below the fixed 80 MiB cap |

The twelve material samples are the two retained Upper quiet strips and the ten
Lower v2 rectangles, including the descriptive bottom reflection samples.
They compare **same-state pre/post T1 bytes**, with exact encoded-luma mean,
variance and horizontal/vertical least-squares slopes. This preserves the
accepted material stage; it does not reinterpret the retained Lower v1 failure
or introduce new reference thresholds.

### Canonical per-label ink observations

These are actual copied-state case 0 measurements at 1672×941 after subtracting
the fixture's viewport origin `(13,17)`. Bounds are half-open canonical pixel
rectangles. Counts include opaque pixels with encoded-channel `Y' > 100` inside
the independently derived copy rectangles. They are descriptive content checks,
not a universal readability metric or a whole-reference score.

| Manual / index | Complete label | Before ink bounds | Candidate ink bounds | Bright pixels before → candidate |
| --- | --- | --- | --- | ---: |
| Upper / 0 | `16'` | `[145,470,170,484)` | `[145,473,171,488)` | 99 → 116 |
| Upper / 1 | `5 1/3'` | `[186,472,225,484)` | `[187,472,224,487)` | 93 → 121 |
| Upper / 2 | `8'` | `[246,470,260,484)` | `[245,473,261,488)` | 67 → 81 |
| Upper / 3 | `4'` | `[293,470,308,484)` | `[293,473,309,488)` | 51 → 66 |
| Upper / 4 | `2 2/3'` | `[330,472,370,484)` | `[331,472,369,488)` | 106 → 127 |
| Upper / 5 | `2'` | `[392,470,406,484)` | `[391,473,407,488)` | 52 → 66 |
| Upper / 6 | `1 3/5'` | `[429,472,468,484)` | `[431,472,467,488)` | 95 → 112 |
| Upper / 7 | `1 1/3'` | `[478,472,517,484)` | `[479,472,516,488)` | 89 → 102 |
| Upper / 8 | `1'` | `[541,470,554,484)` | `[540,473,555,488)` | 46 → 49 |
| Lower / 0 | `16'` | `[672,470,697,484)` | `[671,473,698,488)` | 101 → 117 |
| Lower / 1 | `5 1/3'` | `[714,472,753,484)` | `[715,472,752,487)` | 95 → 122 |
| Lower / 2 | `8'` | `[774,470,788,484)` | `[773,473,789,488)` | 67 → 81 |
| Lower / 3 | `4'` | `[821,470,836,484)` | `[821,473,837,488)` | 51 → 66 |
| Lower / 4 | `2 2/3'` | `[857,472,897,484)` | `[858,472,896,488)` | 106 → 130 |
| Lower / 5 | `2'` | `[919,470,933,484)` | `[918,473,934,488)` | 52 → 67 |
| Lower / 6 | `1 3/5'` | `[955,472,994,484)` | `[957,472,993,488)` | 94 → 112 |
| Lower / 7 | `1 1/3'` | `[1004,472,1043,484)` | `[1006,472,1042,488)` | 88 → 101 |
| Lower / 8 | `1'` | `[1067,470,1080,484)` | `[1067,473,1081,488)` | 46 → 48 |

Ordinary labels now occupy the reference-led y473–488 neighborhood, while the
mixed labels retain distinct numerator, slash, denominator and apostrophe runs.
No musical string was changed. A visual reviewer must still inspect the complete
application frames and native-scale fractions; these numeric observations cannot
override illegibility or collision found in an actual image.

## Checker adversaries and provenance

The [selfcheck source](../development/2026-11-16-conversion-material/reports/A29-checker-selfcheck.py)
and [passed receipt](../development/2026-11-16-conversion-material/reports/A29-checker-selfcheck-initial.json)
record **61/61 checks**, including ten genuine before-only frame preflights.
Adversaries cover one-bit protected changes in each RGBA channel, exact inactive
frames, missing complete glyphs, one altered focus pixel, a changed material
pixel, wrong protocol/focus/route/clock/inventory/geometry metadata, altered font
provenance and attempts to overwrite existing evidence. Source calculations cover
negative COPY truncation, zero extents, subpixel gutters, logical clips and
binary32 activation boundaries. An inside-mask mutation passes only the
containment subcheck; that is explicitly not whole-candidate acceptance.

| Binding | SHA-256 |
| --- | --- |
| Admitted contract | `e000682c74c3ef488cf89dd60396a3d129f8c525cf41a049334cc62030cb3f8a` |
| Independent admission | `a9c5c3bf7274c628dafc9ce92dc602ed60c203fd79b0bc784e74e84392c80d3d` |
| Genuine before fixture source | `facc85f516454964ed55e406f95db4046923d7a2441fdf72e65719b3685fec4f` |
| Accepted Lower before painter | `45b710a9c207f456701732f55ec1086487d63bdb9a8b6ed995f4de12cd5bdb10` |
| Candidate T1 painter | `a88e7576700ae306769849ceda36993969a61e848c015ba4fb98fa9c4a7e8cfa` |
| Before / candidate typography executable | `3e8fcd80bc1715a124fd4a506d31a35ac6abde2a4d4a34c35f95e856c62c924c` / `1220cfa7a48cfe0ff1a9948a455ba9bc4111f8c090e0f2cd632d05fa2244c720` |
| Before / candidate percussion executable | `2bb6c0b613a63588575295e80108341e3eaf37b3b2897c3aa7c762bb3f58a051` / `8edf87754277d2d5b34b9fd8ae8dbad67916a78340ff344c9e2c772f7f854a9d` |
| Comparator | `768ad4a5c022038c75414527961d5437bc3990a11d80772ce6fed6fc5a1534a1` |
| Predeclared mask | `ea94601dc53d692c3fd91ef29e996b6d215e31c35e947b185515079db47130dc` |
| Complete paired report | `ed06af81aa835c9953be26a832a42ae6ae805a874f9ae79065e2a03989356c25` |

The observed HEAD was `3520c96adcdcf4ce4bcb860082354bf0050a89c3`, tree
`1013bbd914a0957ca2c164ef02ca5410a8dcde6b`, with the explicitly hashed uncommitted
T1 source overlay above. Root's
[genuine before receipt](../development/2026-11-16-conversion-material/reports/typography-before-identity.json)
binds the old executable and passing `--before` result. The admission's subsequent
appendix records that observed gate; it does not modify the frozen contract,
fixture or painter. Successful raw RGBA streams were transient; exact stream
hashes and measurements are retained. No success PNGs are fabricated, and no
failed paired case occurred. A failure would retain lossless before/after and
absolute RGBA/maximum/outside-allowance PNGs within the output cap.

## Reproduction and next owner

The comparator's module docstring gives the exact command and prerequisites.
Use a new output directory; the completed report/mask/log are immutable evidence.
The [A29 note](../development/2026-11-16-conversion-material/notes/A29.md) and
[compact receipt](../development/2026-11-16-conversion-material/reports/A29-result-summary.json)
retain commands, identities and limits.

The explicit native/source freeze was released after completion. Root combines
this result with A28 source review, actual 1672×941/minimum/unequal-aspect images,
A32's independent old material-fixture assertion transition, and coherent native
gates before accepting the complete T1 slice. Preserve the genuine accepted T1
stage before starting another painter change. Do not use this pass to close
remaining warm reflection, heading, rim, wood/key/cabinet, whole-interface,
real-device, accessibility, audio or physical-model work.
