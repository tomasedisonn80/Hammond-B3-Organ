# Chapel preset matrix: independent atlas transcription A

The [transcription](../../data/registrations/review-a-chapel.csv) records all
eighteen fixed registrations printed on page 122 of the unchanged
[research atlas](../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf). This is a new
direct visual import of the atlas table, not a recovered companion file, an
independent inspection of factory Table IV, or a specimen measurement.

## Evidence identity and import contract

| Field | Value |
| --- | --- |
| Reviewer | `/root/w06_a31_chapel_source_a` |
| Review date | 2026-11-13 |
| Atlas edition | Evidence edition, 12 November 2026 |
| Atlas identity | 500 pages; 21,248,265 bytes |
| PDF SHA-256 | `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769` |
| Numerical locator | One-based PDF/printed page 122, chapter 019, complete three-column table |
| Context read | Complete pages 119-126; original page 122 image inspected |
| CSV SHA-256 | `dc2a8fd4e9750133c982bb42fd6cc7c12908f011154826035bb623f52d8de694` |
| Review scope | One independently frozen direct visual atlas transcription; no other worker's transcription consulted |

The atlas describes an **approved chapel arrangement**, attributes it to source
S019-01 (Hammond Organ Service Manual, factory early-console compilation), and
reports its own visual comparison to Table IV, printed page 4-1. That underlying
manual was not independently inspected for this assignment. Its hash, revision
and any printed registration names are therefore unverified here. Atlas p122
proposes `factory_chapel_table_iv` as a profile name; that is an atlas proposal.

CSV columns are exactly `manual,preset_key,preset_name,drawbars,page`. Rows are
upper then lower, each in the source's C#, D, D#, E, F, F#, G, G#, A order.
The `drawbars` field is a nine-character string: retain its leading zeros and
never convert it to a decimal integer. All 162 positions are explicit digits
0-8. Every `page` is 122. The page publishes no registration names, so every
`preset_name` is empty; this records missing source information and does not
claim that no historical names existed. Derived display labels must be marked
as application labels rather than imported factory names.

## Ordered harmonic positions

These are documentary physical drawbar order and lead-color labels from p122.
The footage is expressed in feet; colors are not independent continuity evidence.

| CSV digit position (one-based) | Footage | Lead color |
| ---: | --- | --- |
| 1 | 16 | brown |
| 2 | 5 1/3 | red |
| 3 | 8 | orange |
| 4 | 4 | yellow |
| 5 | 2 2/3 | green |
| 6 | 2 | blue |
| 7 | 1 3/5 | violet |
| 8 | 1 1/3 | gray |
| 9 | 1 | white |

Tap digits identify connections. They are not linear amplitude multipliers or
measured gains. A separately identified transformer/drawbar calibration owns
their gain interpretation. The source-wheel/contact map remains unchanged when
a preset changes (pp123-124).

## Behavioral and physical limits

Page 121 distinguishes nine fixed keys C#-A from A#/B, which expose the two
retained drawbar banks without copying them. C is a momentary Cancel action with
no electrical contacts; it empties the latch state while preserving held playing
keys and generator state. Ordinary selection is exclusive. Simultaneous physical
depression can latch multiple contact-bearing keys, but their sound requires a
loaded electrical model, not the sum of independent preset outputs (pp121,123).

Upper B selection also changes percussion eligibility, compensation and keying
connectivity; a nine-gain replacement alone does not implement that transition.
Re-entry during held notes needs electrical charge/contact history and acquired
evidence. Lower selection must not enable upper percussion, and either manual's
Cancel must preserve the other manual and pedals (pp121,124-125).

No specimen identity, continuity photographs, contact overlap timing, branch
impedance, transformer loading or measured B-interlock transition is provided
by this import. Page 125 requests all eighteen fixed registrations versus
equivalent banks, held-key Cancel/reselection, inactive-bank association,
B exit/re-entry, and separately authorized simultaneous-latch observations.
Page 126 separates persistent musical settings from held keys and DSP histories.

## Acceptance and next dependency

The frozen CSV passes structural checks: 18 unique manual/key pairs, nine rows
per manual, 162 digits in range, all pages 122, 16 leading-zero registrations,
and 18 explicitly absent names. Every image-transcribed nine-digit string also
occurs in supplementary extraction of the same PDF; this is not a second source.
The [assignment note](../development/2026-11-13-next-phases/31-chapel-source-a.md)
records commands and the independent freeze.

Next compare an independently frozen second import cell by cell, then retain a
separate direct factory Table IV comparison before claiming that stronger source
gate. A future compiler must validate the complete matrix and source identity.
Runtime selection needs its own contract/tests and explicit state migration;
this import changes no Engine, parameter, state, UI, latch or audio behavior.
The [remaining M3 contract](../M3_REMAINING_AND_SCANNER_GATE.md) owns those gates.
