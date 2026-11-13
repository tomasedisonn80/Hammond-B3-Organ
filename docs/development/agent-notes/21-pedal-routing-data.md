# Agent 21 — documentary pedal routing

Assignment: wave 04, independent pedal-map data, validator, tests and focused
documentation only. No C++/shared-document edits, commits, pushes or subagents.
Read AGENTS.md, required project handoffs, atlas review note 02 and extracted
atlas pp. 139-144, including the actual p. 140 text with five printed rows.

## Evidence and implementation

- Source: `Hammond_B3_Leslie_Research_Atlas_500pp.pdf`, edition 2026-11-12.
- Recomputed SHA-256:
  `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
- `data/pedal-map.json`: explicit 25x8 atlas-rule reconstruction with source
  identity, pages, variant, bus metadata and missing-evidence statuses.
- Row p is `[p, third(p), p+12, p+24, p+31, p+36, p+40, p+43]`.
  Third is p+12 for 1..7, null for 8..12 and p+19 for 13..25 (atlas p. 140).
- All 195 connected positions and five nulls are retained. The seven duplicated
  third/second source pairs remain separate contacts. Null is never source zero.
- Buses are brown columns 0/1, red 2/3, orange 4/5 and yellow 6/7 (p. 140).
  This adds membership, not weights, conductance, physical gain or audio.
- `tools/validate_pedal_map.py`: stdlib, exact versioned schema/provenance,
  ordered IDs, ranges, counts and every semantic route; read-only public API/CLI.
- Strict UTF-8 JSON is limited to 32 KiB; duplicate names, booleans as integers,
  fractional/exponent/nonfinite tokens, malformed data and unknown fields fail.
- `tests/test_pedal_map.py`: five independently copied p. 140 printed fixtures;
  all 200 wrong-source mutations and all 195 removal mutations rejected;
  disconnections, duplicates, exact metadata, parser/size and no-mutation tests.
- `docs/PEDAL_ROUTING.md` explains the contract and future M3 evidence gates.

## Actual verification

Commands ran from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tests/test_pedal_map.py -v
PYTHONDONTWRITEBYTECODE=1 python3 tools/validate_pedal_map.py --input data/pedal-map.json
sha256sum Hammond_B3_Leslie_Research_Atlas_500pp.pdf
```

Results: all 15 tests passed; CLI exit 0 reported 25 pedals, 200 positions,
195 connected and five disconnected. The PDF hash matched the recorded source.
No audio/render tests were required or performed for these documentary files.

## Remaining boundaries and integrator handoff

This is consistency with the atlas rule and five printed examples, not an
independent full factory Table III transcription. The absent companion table,
original-source review, specimen identity and continuity measurements remain
open (atlas pp. 139-144). The Engine remains manual-only.

Future M3 pedal weighting/loading needs revision-specific network topology,
contact/source resistances, reactor inductance/loss, drawbar and transformer
loads, low-wheel phase/spectra and measured transfer functions. No values were
invented. Integrator owns shared status/log updates and build-test registration.
