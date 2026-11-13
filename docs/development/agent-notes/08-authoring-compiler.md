# Agent 08: strict nominal authoring compiler

## Assignment and evidence boundary

- Owned only `tools/compile_profile.py`, `data/profile.schema.json`,
  `data/profiles/nominal-unmeasured-v1.json`, and this note; no commits or pushes.
- Read repository instructions, implementation/profile contracts, current plan,
  status/next-step/log files, source manifest, and atlas review notes 01/02.
  `docs/research/ATLAS_REVIEW.md` was absent at review time. Atlas citations below
  inherit those page reviews; this assignment did not re-review the entire PDF.
- Atlas SHA-256 is exactly the source-manifest hash
  `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.

## Implemented contract

- Dependency-free Python 3 semantic compiler for schema/model version 1,
  `ideal-shared-sine-v1` / `nominal-unmeasured-v1` only.
- Public API: `load_profile(path) -> dict`, `validate_profile(dict) -> None`,
  `canonical_json(dict) -> bytes`, `authoring_sha256(dict) -> str`, and
  `compile_profile(dict) -> str`; errors use `ProfileError(ValueError)`.
- CLI: `--input PATH --output PATH`; `--check` permits omitted output and writes
  nothing. With output supplied, check requires identical existing compiled bytes.
- Strict UTF-8 JSON rejects duplicate keys, NaN/Inf/overflow, unknown/missing fields,
  incorrect versions/models, bool-as-number, invalid IDs/counts/ranges/units,
  evidence contradictions, and deviations from the declared nominal equations/map.
- Input is limited to 256 KiB; compiled/check input to 128 KiB; imported objects
  also have depth, node, array, object-field, and string bounds.
- Numeric invariants: 91 explicit `440 * 2**((tone_id-46)/12)` Hz values, unit peak
  normalized amplitudes, proposed zero base phases, proposed output gain 0.03,
  and explicit `g(0)=0`, `g(p)=10**(3*(p-8)/20)` for positions 1..8.
- 61x9 explicit routes use offsets `[0,19,12,24,31,36,40,43,48]`, low drawbar-one
  fold, and repeated high fold (atlas pp.98-99). Six printed rows on p.102 agree.
  Independent full factory-table verification remains false: companion/original
  transcription is absent. Formula comparison is not independent measurement.
- Specimen, AO-28 revision, and measurements remain null with acquisition reasons.
  Per-column source metadata applies units/evidence to every source row; model
  boundaries explicitly exclude pickup voltage/calibration, pedals, percussion,
  scanner, AO-28, and Leslie. Proposed values are not claimed to be factory data.
- Canonical authoring bytes are Python `json.dumps` with sorted keys, compact
  comma/colon separators, `ensure_ascii=False`, `allow_nan=False`, UTF-8, and no
  final newline. This project convention is not RFC8785. Binary64 round-trip
  decimal text follows PROFILE_FORMAT token order and ends with one LF.
- Validate completely before writing a temporary sibling, flush/fsync, then atomic
  replacement. Failed input/write/check preserves existing output; same-file
  input/output aliases reject. Python objects supplied to the API are not changed.
- Draft 2020-12 schema describes shape/ranges/identity/evidence. The semantic
  compiler additionally checks equations and ordered IDs; no generic validator
  implementation or JSON-Schema-only semantic assurance is claimed.

## Executed verification

```sh
python3 tools/compile_profile.py --input data/profiles/nominal-unmeasured-v1.json --output /tmp/hammond-agent08-nominal.b3p
python3 tools/compile_profile.py --input data/profiles/nominal-unmeasured-v1.json --check --output /tmp/hammond-agent08-nominal.b3p
python3 tools/compile_profile.py --input data/profiles/nominal-unmeasured-v1.json --check
git diff --check
```

- All listed commands passed. Authoring file: 19,627 bytes; compiled: 4,545 bytes.
- Canonical authoring digest:
  `49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83`.
- Compiled byte digest:
  `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.
- Executed an ephemeral stdlib Python assertion harness: 47 semantic rejection
  cases, 10 malformed CLI/unchanged-output cases, six independent printed-row
  fixtures, reordered-key/whitespace determinism, canonical hash/no-mutation,
  stale-check and same-path safety, injected fsync/replace failure atomicity: PASS.
- Available `jsonschema.Draft202012Validator` checked schema meta-validity and the
  nominal instance: PASS. It is a verification tool, not a project dependency.
- A symlink-loop output originally exposed a traceback; fixed error handling and
  reran the case: descriptive nonzero error and unchanged symlink, PASS.
- Agent 11 owns retained regression tests; agents 09/10 received the working CLI,
  interchange, and temp output for CMake/C++ integration. No hardware or factory
  frequency/phase/voltage verification was performed or claimed.
