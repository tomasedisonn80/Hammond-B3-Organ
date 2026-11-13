# Documentary pedal routing

[pedal-map.json](../data/pedal-map.json) is an explicit 25-by-8 reconstruction of
the rule printed on [atlas p. 140](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=140).
It is separate from the authoring/runtime organ profile. **The current Engine is
manual-only; this data does not add pedal events, voices, mixing or audio.** See
[the Engine API](ENGINE_API.md) and [console extension scope](CONSOLE_EXTENSION.md).

## Source identity and evidence

The source is `Hammond_B3_Leslie_Research_Atlas_500pp.pdf`, evidence edition
2026-11-12, SHA-256
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
All page locators below are one-based PDF pages, equal to printed atlas pages.
Chapter 022 spans pp. 139-144 and cites S022-01, the Hammond Organ Service Manual
for original console models. Those references identify what the atlas cites;
they do not themselves supply an independently transcribed manual. The later
[factory comparison](FACTORY_REFERENCE.md) retains two independent direct-image
readings and matches all 200 positions, including the five disconnections.

Page 139 scopes the table to the represented factory B-3/C-3 wiring. Page 140
supplies the complete constructive rule, five printed rows and bus membership.
Pages 142-144 identify the electrical model and acquisition/acceptance work.
The atlas's companion table was not supplied. The JSON therefore says `derived`,
`independent_factory_transcription_status: missing` and
`specimen_continuity_status: not-measured`; specimen identity is explicitly null.
These frozen fields describe the original authoring provenance. The later
collateral comparison attests to the exact retained digest without rewriting that
history. No software or documentary check establishes specimen measurement. A
separately versioned record is needed to incorporate new provenance or variants.

## Ordered contacts and buses

Pedal IDs are one-based 1..25. Each `sources` array has eight ordered positions;
its non-null values are **one-based generator source IDs**, bounded by 1..91.
They are neither MIDI notes nor physical terminal numbers. Column indices in
`bus_columns` are zero-based. The reconstruction uses source IDs 1..68 and does
not apply the manuals' low foldback rule to pedals (atlas pp. 139-140).

| Column index | Atlas table column | Diagram bus |
| ---: | --- | --- |
| 0 | Fundamental | brown |
| 1 | Third-contact | brown |
| 2 | Second | red |
| 3 | Fourth | red |
| 4 | Sixth | orange |
| 5 | Eighth | orange |
| 6 | Tenth | yellow |
| 7 | Twelfth | yellow |

For pedal `p`, the row is
`[p, third(p), p+12, p+24, p+31, p+36, p+40, p+43]` (atlas p. 140), where:

- Pedals 1..7 have `third(p) = p+12`, duplicating the second-harmonic source at column 2.
- Pedals 8..12 have `third(p) = null`, meaning an absent electrical connection.
- Pedals 13..25 have `third(p) = p+19`.

The 200 contact positions retain **195 connections and five nulls**. Null never
means source zero. The seven repeated source pairs at columns 1 and 2 remain
separate contact branches on different buses; neither a set nor a deduplicated
source list preserves that topology. The third-contact label is retained even
where its source differs from the expected harmonic. These exceptions and the
7/8 and 12/13 transitions are explicit acceptance checks (atlas pp. 140, 144).

Bus colors identify the atlas diagram; they do not certify the colors or
continuity of a repaired loom. Bus membership carries no summing weight,
conductance, physical gain, resistance or transfer coefficient (atlas p. 140).

## Validation contract and direct checks

The stdlib-only validator enforces schema version 1, the exact map identity and
provenance, required fields with no extras, ordered pedal IDs, all eight column
labels, all four bus memberships, counts, source bounds and every piecewise
route. Object key order is immaterial; row and column array order is fixed.
Numbers must be JSON integers. Booleans, fractions, exponent notation, nonfinite
tokens, duplicate object names and invalid UTF-8 are rejected. Input is bounded
to 32 KiB, including whitespace. Oversize, malformed and unreadable input fails
without writing the source file. Direct validation never mutates its argument.

```sh
python3 tools/validate_pedal_map.py --input data/pedal-map.json
python3 tests/test_pedal_map.py -v
```

The Python API is `load_pedal_map(path)` (read and validate, returning a dict)
and `validate_pedal_map(value)` (validate without changing it, returning `None`).
Both reject invalid data with `PedalMapError`, a `ValueError` subclass. CLI exit
status is 0 on success, 1 on invalid/unreadable input, and 2 for usage errors.
There is no write or compile operation and no audio-thread integration.

Tests retain the five printed p. 140 rows for pedals 1, 7, 8, 13 and 25 as
independent expected fixtures. Additional tests check all 200 positions, every
missing connection and duplicate path, exact metadata, malformed records, parser
limits and read-only CLI behavior. Formula consistency across the other rows is
an engineering check. The separate factory-reference suite now compares all 200
positions against both frozen readings; physical continuity remains unmeasured.

## Future M3 pedal audio needs evidence

Atlas pp. 139 and 142 describe eight contacts, four collecting buses and two
drawbars connected through a reactor/resistor mixture network. The later pedal
division should consume the existing shared, continuously running generator
sources, retain contact ownership and branch loading, and feed the lower-manual
path with its Great vibrato relationship. Pressing a pedal must not create or
restart an independent source (atlas pp. 139, 141).

Before assigning weights or loading, obtain the applicable production topology,
contact/source resistances in ohms, reactor inductance in henries and series loss
in ohms, drawbar-state loads, transformer input loading, and measured complex
bus-to-output transfers with stated levels, units and signal boundaries. Low-wheel
waveforms need phase-aware spectral evidence as well. These quantities remain
unknown; neither bus pairs nor patent examples supply calibrated gains. Keep
unknown values out of this identity-only map (atlas pp. 141-144).

Future tests need a declared linear fixture or a loaded network oracle, retained
shared phase, boundary contact state and independently checked factory/specimen
routes. No pedal waveform, equal-weight sum, drawbar mixture or loading model is
claimed by the present data and validator (atlas pp. 142-144).
