# A10: independent literal preset oracle

**Worker:** `/root/w02_a10_independent_oracle`, 2026-11-14. Inspected base
`b79086f6bb0c42b97130c721c5c73c7c97a13887` plus the current uncommitted selection
and core API contracts. Owned only this note and
[`tests/PresetTestOracle.h`](../../../tests/PresetTestOracle.h).

## Source and result

Read original one-based PDF/printed page 122 of
`Hammond_B3_Leslie_Research_Atlas_500pp.pdf` using both `pdftotext -layout` and
a freshly rendered, visually inspected PNG. The source is chapter 019, evidence
edition 12 November 2026; its observed SHA-256 remains
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.

The fixture contains only literal `constexpr` arrays in `preset_test_oracle`:
`kKeys[9]` is C#, D, D#, E, F, F#, G, G#, A; `kPositions[2][9][9]` is
Upper then Lower, in that key order. Drawbar positions follow the page's physical
footage order: 16, 5 1/3, 8, 4, 2 2/3, 2, 1 3/5, 1 1/3, 1 feet. No production
header, generator, lookup, compiler or gain helper supplies expected values.

All **18 manual/key identities and 162 tap positions agree exactly** with the
original image, extracted PDF table, both retained CSV readings and the
authoring JSON. All sixteen rows beginning with zero retain nine positions.
The source notes A/B and catalog guide agree with the physical order and absent
voice names. This review directly reread the atlas; it does not claim a blinded
third transcription or a second underlying documentary source.

| Checked input | Observed SHA-256 |
|---|---|
| `tests/PresetTestOracle.h` | `c2361bc68ff297977e246da391872fc69fe380d8bdd6230efb6a77a9aad61274` |
| Each of `review-a-chapel.csv`, `review-b-chapel.csv` | `dc2a8fd4e9750133c982bb42fd6cc7c12908f011154826035bb623f52d8de694` |
| `atlas-chapel-nominal-v1.json` | `c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf` |

These are **documentary transformer tap indices, not measured gains or linear
amplitude multipliers**. The atlas attributes the arrangement to S019-01,
factory Table IV, printed page 4-1. That underlying page, universal B-3 wiring,
specimen continuity and loaded gains remain unverified here.

## Actual checks

From the repository root:

```sh
pdftotext -f 122 -l 122 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftoppm -f 122 -l 122 -scale-to 2000 -png -singlefile Hammond_B3_Leslie_Research_Atlas_500pp.pdf tmp/pdfs/a10-page122
sha256sum Hammond_B3_Leslie_Research_Atlas_500pp.pdf
```

The PNG was opened with `view_image`; temporary rendering/probe files were
removed. Observed Poppler versions: `pdftotext` 25.03.0, `pdftoppm` 26.05.0.
A temporary standalone C++20 probe compiled the header using GCC 14.2.0 with
`-Wall -Wextra -pedantic`, asserted dimensions 2 x 9 x 9, and printed the literal
rows. A Python standard-library comparison matched those emitted rows to the
PDF extraction, both CSVs and authoring JSON, including order, page 122 and absent
names. All checks completed successfully. No Engine/runtime acceptance or CTest
suite was run by this assignment.

## Actionable runtime scenarios for later independent testers

1. **All 18 rows versus Bank A.** Fill a reference engine's Bank A directly from
   `kPositions`, with no fixed mode and percussion disabled. Use identical
   profiles, seeds, sample rates and absolute event timelines in the fixed and
   reference engines. For every manual/key, compare all nine public lookup
   positions and PCM for held chords including MIDI 36/48/60/72/84/96 foldback
   cases. Do not populate the reference from production lookup results. Require
   bit-identical PCM under the unchanged arithmetic contract; independently test
   None/invalid lookup destination preservation. Repeat meaningful timelines
   under different block partitions and the supported-rate acceptance set.
2. **Partial contacts and retained edits.** In LinearTravel mode, reach position
   0.5 from both released and fully pressed histories, preserving their distinct
   contact masks. Select fixed/Cancel/reselect at zero frames; require exact
   target, position, hysteresis and key-state preservation. Continue against a
   Bank A reference with the same history. Editing retained banks while fixed
   sounds must preserve fixed PCM, then appear on explicit bank selection.
3. **Held phase, Cancel and pedals.** Sustain both manuals and a pedal, render
   first, then snapshot all 91 source phases, clock and contact/key histories.
   Zero-frame selections must preserve these histories. Across rendered Cancel
   intervals, compare phase evolution to a continuously running reference;
   only the selected manual route is muted. Reselection must resume the held
   registration without a note event or phase reset, with the other manual and
   pedal unchanged.
4. **Upper B to fixed to B percussion.** Begin with a held detector and depleted
   readiness. Compare B/fixed/B against B/equivalent-Bank-A/B at matched elapsed
   samples. Fixed selection must immediately remove diagnostic eligibility and
   all upper-B sustain masking/compensation; use every literal tap position,
   including the ninth.
   Equal-offset and separate zero-frame B/fixed/B sequences add no recovery;
   rendered fixed intervals recover by the existing nominal readiness law.
   Return through the legacy `SelectBank B` event to catch a stale remembered-B
   no-op. Lower fixed selections must preserve upper eligibility/readiness.

The integrator owns contract freeze, runtime integration, shared status and
publication. This fixture qualifies the literal documentary inputs only.
