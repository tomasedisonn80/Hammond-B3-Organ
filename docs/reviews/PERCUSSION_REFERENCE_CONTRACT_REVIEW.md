# Percussion reference contract admission

**Decision: admit version 1 for implementation; no required contract revision.**
This is A11's independent design/source review on 15 November 2026. It is not an
implementation, runtime, raster or whole-interface fidelity acceptance.

Reviewed [the contract](../PERCUSSION_REFERENCE_CONTRACT.md), complete `AGENTS.md`
and `PLAN.md`, A05's atlas/reference review, A09's author note, and the relevant
layout, paint, validation, parameter, pointer and keyboard paths in
`apps/standalone/UiModel.{h,cpp}` and `InstrumentView.cpp`. Directly viewed the
original reference JPEG and existing actual 1672x941 product PNG. No new app
capture was made. The inspected HEAD at completion was
`276664ee8570c208bb007cca59f496963ca13ef5`; the source hashes below bind this
review even if documentation commits move HEAD.

## Independent geometry findings

Recomputed the parent layout and proposed rectangles with explicitly rounded
binary32 arithmetic in a temporary Python process. The three authored checkpoint
rows agree within the contract's 0.002 logical-unit tolerance.

| Logical size | Outer width × height | Left edges, visual order | Top |
| --- | --- | --- | ---: |
| 1400×820 | 61.814117 × 47.400002 | 137.718246, 214.568237, 282.229614, 349.891022 | 150 |
| 1672×941 | 73.961494 × 48 | 164.647720, 256.599854, 337.557678, 418.515564 | 150 |
| 1920×1080 | 86.069016 × 48 | 179.935196, 286.939911, 381.150574, 475.361267 | 150 |
| 8192×820 | 92.5 × 47.400002 | 1229.181396, 1344.181396, 1445.431396, 1546.681396 | 150 |

A 90-case arithmetic matrix used widths 1400, 1400.25, 1400.5, 1401, 1536,
1672, 1920, 2560, 4096 and 8192, with heights 820, 820.25, 824.999, 825,
933.3333, 941, 1080, 2160 and 8192. Minimum sampled clearances were 4 logical
units below legends, 1.8472595 between neighboring legend rectangles and
49.4512939 between the last tablet and the subsection's right edge. This checks
the equations, not `make_ui_layout` execution or acceptance at those sizes.

At the exact active threshold, performance height is 90.4, leaving tablet height
47.4. Legend bottom is performance.y + 86.4, with four units below it. The
minimum between adjacent legend rectangles follows `7*s - 4`; it stays positive
through the active range. Heading bottom is performance.y + 21 and tablets
start at performance.y + 24. Once separate eligibility is admitted at strip
height 104, legend bottom is performance.y + 87 and eligibility starts at
performance.y + 88. The contract therefore removes the collision the existing
performance.y + 73 eligibility line would create with exterior captions.

The predicate correctly excludes 1399×820 and 1400×819, all Flat layouts, and
Rotary/Service. It includes 1400×820 and fractional sizes just above it. Width
alone is insufficient: implementation must apply the complete predicate in both
layout and paint. Existing layout rejects nonfinite, undersized and dimensions
above 8192 before replacing the destination.

## Input, focus and semantic findings

| Case | Independent finding / implementation acceptance condition |
| --- | --- |
| Identity and visual order | Existing percussion parameter mapping is `0x3000 + index`. Insert semantic IDs `[0,2,3,1]` in active visual order; do not rename parameters or reinterpret the state array. PERC/VOL/DECAY/HARM then map to ON/OFF, NORM/SOFT, SLOW/FAST and 2ND/3RD. |
| Shared rectangles | General control hit testing reads `bounds`; focus outline also reads `bounds`. `value_bounds` and exterior `label_bounds` provide paint geometry without expanding the target. Existing layout validation permits a label outside its own tablet. The intentionally empty track is not an interactive region. |
| Pointer boundaries | `UiRect::contains` includes left/top and excludes right/bottom. At the first threshold tablet, its right edge is approximately 199.53236 and bottom 197.4. Exact right/bottom, the two-unit gap below the tablet, exterior legend and inter-tablet gaps must not activate percussion. Existing repeated-down suppression and original note-release ownership remain applicable. |
| Tab and retained focus | Tab iterates the visible control array and finds current focus by semantic ID. Visual insertion order is sufficient; changing the focused index to its visual ordinal would be a defect. Existing resize/presentation replacement retains semantic focus, and workspace restoration uses remembered identities. |
| Keyboard activation | Existing Space/Enter activates focused percussion. Physical-key down suppression prevents repetition. Arrows/Home/End reach no percussion editing branch. Test down/up pairs and threshold crossings with each of the four semantic controls focused. |
| Applied eligibility | Eligibility is copied applied upper routing: enabled route, no fixed registration, bank B. Switch values remain copied retained/desired controls. An ineligible stored ON must remain visibly ON; it does not establish an active percussion route. |
| No new functionality | The proposed change adds no scanner, rotary or audio claims. The reference image's erroneous DECAY/HARM values are correctly excluded from the control domains. |

Existing tablet material drawing stays within its supplied outer rectangle;
the proposed contract does not require changing the shared painter. Separate
eligibility, combined heading and the selected/focused cases remain part of the
required paired raster checks, including noninteger drawable scales and clips.

## Required implementation evidence and remaining mismatch

Proceed with the bounded implementation, then independently exercise boundary
hits, every semantic focus state, forward/reverse Tab, keyboard activation,
threshold resize, Flat/Dimensional and workspace restoration, and retained
versus applied eligibility. Pair baseline/candidate rendering from identical
state and renderer inputs; require unchanged pixels outside the declared paint
regions and unchanged inactive layouts. Capture the actual changed application
with source, executable, state and image identities before updating the README
design evidence. These checks are required next steps, not results of this review.

The original has narrow ivory tablets with exterior captions; the existing
product PNG has wider tablets with legends inside. The contract addresses that
local difference and approaches the reference's horizontal landmarks. Its top
remains y150 against the concept's approximate y177. The approximately 27-unit
vertical mismatch and wider rack/manual/header composition work remain explicit.
Literal whole-interface 1:1 matching is still unmet and is not waived here.

## Reviewed identities

| Input | SHA-256 |
| --- | --- |
| Contract version 1 | `3d7e9414a6159b6c7ad966312f0d11d03ccc9e3122242735ea1df116851735d8` |
| `UiModel.h` | `d94e90be25812c6d21b61f37f2b0547704d14866c45fbbb21131ec70b6389bd3` |
| `UiModel.cpp` | `49c68995aad96aa5e316613412c93931a1082d0e4a3ad3758ac63484af963064` |
| `InstrumentView.cpp` | `3687f96db4490e600d6107e6b39d7b7d568bdeb183f16f6aa397535a5f688567` |
| `docs/design/atlas-cover-reference.jpg` | `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187` |
| Existing `play-reference-1672x941.png` | `4dcb8e55dcfbc5f3e5d524bf0ea426312083f8f56e922716e6d0513fe08b9d19` |

