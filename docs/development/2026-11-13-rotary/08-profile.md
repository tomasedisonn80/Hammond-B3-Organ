# Assignment 08: strict rotary research profile

Worker `/root/w02_a08_profile`, wave 2, owns these five deliverables:

- `data/rotary-profile.schema.json`
- `data/rotary/nominal-research-v1.json`
- `tools/validate_rotary_profile.py`
- `docs/ROTARY_PROFILE.md`
- This note.

Read `AGENTS.md`, current status/next steps/scanner handoff, plan and rotary
scope, plus wave 1 source reviews. The initial observation was commit
`96a37a977ef22b7adf38e1a841f57ffcf32519a7`, tree
`ab85e45d6776229c00fa394a540d72803daf8281`. Other workers' changes remained
outside this assignment's ownership. Publication and a coherent combined-tree
gate belong to the integrator; this worker did not commit or push.

## Implemented contract

Coordinated model ID, bounds, field mapping and prehistory with assignment 07
before admission checks. Coordinated the normalized representation and
same-read raw digest API with the independent-reference owner, assignment 09.
The [profile guide](../../ROTARY_PROFILE.md) gives the full schema, exact
units, fixture values, normalization map and executable commands.

Every physical scalar/vector has proposed evidence, applicable synthetic
variant, fixed atlas algorithm/boundary pages, null measured uncertainty and
an explicit missing-measurement reason. Eight required null acquisition gaps
remain separate. The prototype has two independent rotors, two named receivers,
Chorale/Tremolo commands, unity directivity and explicit inverse-distance gain.
It does not infer a physical brake or filled-in M5/M6/cabinet response.

The standard-library validator rejects unknown/missing fields, wrong units,
boolean/nonfinite values, duplicate JSON keys, unsupported provenance, invalid
source identities, filled physical unknowns and bad command/state values.
Cross-field admission checks slow/fast ordering, the initial/target rim-speed
envelope and all four rotor/microphone **full-orbit** distance bounds.
File, nesting, node, collection and string bounds apply before use; direct
Python object cycles and invalid Unicode also fail. Rejection never mutates
authoring or silently repairs a value. Normalization produces detached data.

`load_profile_with_digest` returns admission and the SHA-256 of the same
bounded regular-file bytes. Raw and canonical digests have distinct names.
The CLI writes one JSON admission/error result with exit 0/2; help is ordinary
help text. No files are overwritten by validation.

## Executed evidence

Python 3.12.14 executed:

```sh
python3 tools/validate_rotary_profile.py --input data/rotary/nominal-research-v1.json
python3 tools/validate_rotary_profile.py --input data/rotary/nominal-research-v1.json --normalized
```

The valid fixture admitted. An in-process smoke script verified unchanged
authoring, identity return, independent normalized arrays and same-read raw
digest. Fourteen deliberately invalid semantic mutations all rejected:
boolean, nonfinite, extra field, wrong unit, reversed speed ordering, excessive
rim speed, intersecting orbit, excessive path distance, duplicate mic identity,
false measured classification, filled unknown, STOP, phase at `2*pi` and
oversized reason string. Eight byte/CLI cases rejected with parseable JSON and
exit 2: duplicate keys, invalid UTF-8, BOM, oversized file, extreme nesting,
NUL, empty input and NaN. Invalid path types/embedded NUL and missing CLI
arguments also produced the declared error type/result.

The already-installed `jsonschema` 4.26.0 checked draft-2020-12 schema validity
and the admitted fixture. It is not a production dependency. Schema admission
alone cannot enforce the cross-field equations or all exact lexical/resource
rules; that limitation is explicit in the schema and guide.

Fixture size is 19,988 bytes. Raw SHA-256:
`c0473cb20604726d989d7c280700109f647f7b227edb71c61d275ed9bfd67443`.
Canonical authoring SHA-256:
`a281cf308caf7928c7690f22925987f80ceebdb9f90b10693b8d2512c38b21bf`.
The atlas identity remains
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
Python syntax parsing and whitespace checks passed. These focused author
checks precede the separately assigned maintained independent regression.

## Limits and next step

No C++ processing, renderer, native host, physical capture or timing gate was
executed by this assignment. Numeric proposals have no measured uncertainty;
admission establishes data consistency, not truth of a specimen claim. Next:
independent malformed-input/schema tests, reviewed runtime projection and
motion/propagation execution under the frozen numerical contract. Preserve the
named fixture, source pages, model boundary and all missing acquisitions.
