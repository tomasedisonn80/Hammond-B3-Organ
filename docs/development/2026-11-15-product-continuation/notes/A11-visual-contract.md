# A11 - Wide native visual contract

Actual assignment `/root/w02_a11_visual_contract`, wave 2. Reviewed the complete
agent instructions and M0-M9 plan, session scope/checkpoint, A05/A06 readings,
existing layout/material/waveform contracts and current drawing/layout code.
Inspected source at `a3d10bf49ef878a1eb3c08460d244ba68a8143eb`; only the two
assigned documentation files were written. No shared build was used, and no
runtime test, implementation, new screenshot or commit was performed.

Directly inspected the original reference JPEG and actual v5 Play PNG. Verified
their SHA-256 values against the retained readings. The new
[contract](../../../PRODUCT_VISUAL_REFINEMENT.md) records those exact identities,
source-derived geometry and concrete implementation/acceptance requirements.

The permitted branch is `sidebar_pedals && Dimensional` only, equivalent to
width at least 1400 and height at least 820. Preserve every layout rectangle,
68 controls, 24 presets, 147 playing keys, focus/release ownership, 47 parameters
and state4. Compact and Flat paths remain unchanged; the separate MIDI-overlay
feature has its own explicit comparison boundary.

Source arithmetic exposes a real constraint: label end to track top is only
14px, while track bottom to numeric row is 18px. Naively increasing 26px caps
would overlap those bands. The contract reserves the upper 20px label box,
fits complete serif footage toward 16-17px, proposes 32px caps with unchanged
centers, and bounds shadows before the numeric row. ASCII fraction construction
is allowed; unsupported Unicode glyphs are not. Distinct EDIT and applied
SOUNDING rows fit the existing 32px header area.

Idle manual naturals gain restrained quad-contained side lighting and a lighter
rear recess. Existing fronts, held colors, accidentals and pedals remain intact.
Acceptance requires endpoint/scale/clip containment, unchanged-region identity,
all legacy behavior gates, the retained UI timing budget and fresh actual native
captures before README promotion. Literal 1:1 equality is not claimed.

Product-source SHA-256 values at review:

- `UiModel.cpp`: `49c68995aad96aa5e316613412c93931a1082d0e4a3ad3758ac63484af963064`.
- `InstrumentView.cpp`: `aae710a6e4eb8d7eccfe8fd7e5cf3cb98109ee1bc0143229e5b5b8b63f3c7a4c`.
