# Agent 26 — short synthetic musical fixtures

Assignment: wave 05; own `examples/fixtures/*`, `examples/README.md`,
`tests/test_fixture_catalog.py` and this note. No shared build/status edits,
commits, pushes, new agents, imported samples or retained generated WAVs.

Read AGENTS, README, STATUS, NEXT_STEPS, latest DEVELOPMENT_LOG, PLAN,
ATLAS_REVIEW, relevant routing/contact review notes, ENGINE_API,
CONSOLE_EXTENSION, PROFILE_FORMAT, renderer source and updated executable help.
Physical evidence remains bounded by the nominal profile and atlas-derived map.

## Deliverables

- Five readable, versioned scores: two-manual C-F-G-C/registration demo;
  isolated A4; low-fold 1/2/3/1 coherent branches; held-key banks/Cancel/reselect;
  high-fold 1/2/3 coherent branches including the twice-folded top 1-foot route.
- `examples/fixtures/catalog-v1.json`: schema/profile identities, source hashes,
  explicit frames/rate/block/seed/registration, silence/audible spans, tone IDs,
  amplitude/phase/component expectations, limits and quantization tolerances.
- 48 kHz only; each score <=4 s; 12 s total, 61 events, 127-frame blocks.
  Uneven control frames make phase resets and timing mistakes observable.
- README commands create output parents and explicitly reject clipping;
  optional agent-25 wrapper command retains a provenance bundle in a new folder.
- Standard-library test validates actual catalog paths/hashes/profile/bounds,
  renders every score, checks PCM16/stereo identity/metrics/clip0 and all declared
  spans, fits isolated sines, compares coherent levels/absolute phases, and
  checks both-manual chord components and changed registration amplitudes.

## Executed evidence

Working directory: repository root. Renderer/profile inputs:
`/workspace/scratch/c871510c69b2/agent22-debug/{hammond_render,nominal.b3p}`.

- `python3 tests/test_fixture_catalog.py --renderer <above executable>
  --profile <above profile>`: 2 tests passed, 5 renders, 2.233 s observed.
- Same test using `HAMMOND_RENDER_EXECUTABLE` and `HAMMOND_TEST_PROFILE`:
  2 tests passed, 5 renders, 2.437 s observed. CMake already injects these vars.
- Explicit nonexistent renderer environment path: failed clearly, exit 5,
  “Missing renderer executable” / “Catalog audio assertions were not run”;
  no silent fallback or skip. This is intentional failure evidence.
- Separate bounded catalog render loop retained these actual float metrics:

| Fixture | Peak | RMS | Clipped frames |
|---|---:|---:|---:|
| two-manual-changes-v1 | 0.08130008727312088 | 0.02006219567993473 | 0 |
| a4-fundamental-v1 | 0.014999978244304657 | 0.008660254045408078 | 0 |
| low-fold-coherent-v1 | 0.04500000178813934 | 0.020066682292456544 | 0 |
| held-bank-cancel-v1 | 0.014999988488852978 | 0.006919664086282827 | 0 |
| high-fold-coherent-v1 | 0.04500000178813934 | 0.01867714815559926 | 0 |

All WAVs used temporary directories and were removed. `git diff --check` passed;
the test parsed successfully and no WAV was present in the fixture directory.
The catalog binds canonical authoring hash `49791eac...adda83` and compiled
hash `b36b0773...6389f`; their complete values are retained in the JSON.

Limits: normalized synthetic sines, ideal stepped gates/clicks and exclusive
banks only. No recorded-hardware sound, measured contact bandwidth/loading,
pedal/percussion/scanner/AO-28/Leslie model, host qualification, callback
performance, cross-toolchain bitwise identity or physical-fidelity pass claimed.
Integrator can run the auto-discovered CTest target and select the musical score
for the later final demo; the catalog intentionally contains source data only.
