# Assignment 21 — independent evidence verifier migration

- Agent: `/root/w04_a21_evidence_verifier`.
- Wave: 04, the continuation's new assignment 21 of 60.
- Working baseline: `7a24a30acd111a8f85cb8df65ba2ca59ada456e3`, with the
  concurrent wave-03 engine/renderer integration and agent-20 producer changes.
- Outcome: implemented and locally verified strict schema-2 consumption while
  preserving historical schema-1 consumption. Integration/publication belongs
  to the root agent; this assignment made no commits or pushes.

## Scope and decisions

Owned files only:

- `tools/verify_render.py`.
- `tests/test_verify_render.py`.
- `docs/RENDER_VERIFICATION.md`.
- This note.

Read the standing instructions, shared status/plan/handoff, full-atlas review,
continuation ledger, console dynamics contract, producer and consumer code, and
their format documentation. Coordinated the frozen schema-2 contract directly
with `/root/w04_a20_evidence_producer`. The verifier continues to import only the
supported profile compiler; it does not import the producer or execute a renderer.

The integer manifest version now selects the complete parameter, invocation,
metric and event contract. Schema 1 keeps nine parameters, 18 invocation tokens,
15 renderer metrics and the original eight event types. Schema 2 requires 13
parameters, 26 tokens, 18 metrics and permits the upper-only percussion event.
All four initial console choices must be explicit valid strings and agree with
their exact ordered argv values. Both stdout and the manifest must carry integer
render schema 2, the contact model selected by the parameter and
`shared-readiness-v1`. Model identity remains present when percussion is off.

Percussion indices are unsigned integers 0–3. Values must parse as finite numbers
equal to 0 or 1, including equivalent decimal forms such as `1.0` and `1e0`.
Existing token, line, score, event-count and density bounds remain unchanged.
Historical schema 1 rejects all new fields/flags/events; version-2 records cannot
be weakened by simply changing the manifest version. Unsupported versions,
Boolean/floating-point versions, missing fields and mixed versions reject.

Existing independent hashing, compiled-profile reconstruction, PCM decoding,
quantization comparisons, path/inventory checks, log checks and observed file
stability checks remain active. A successful report returns the verified input
manifest's schema version. Integrity does not establish authentication, source
build association, actual replay, physical calibration or instrument fidelity.

## Executed evidence

An isolated GCC 14.2.0 Release build was configured at
`/workspace/scratch/60e8291da354/a21-verifier-build`. Python was 3.12.14.

```sh
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  -S . -B /workspace/scratch/60e8291da354/a21-verifier-build \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  --build /workspace/scratch/60e8291da354/a21-verifier-build \
  --target hammond_render -j 4
HAMMOND_RENDER_EXECUTABLE=/workspace/scratch/60e8291da354/a21-verifier-build/hammond_render \
HAMMOND_TEST_PROFILE=/workspace/scratch/60e8291da354/a21-verifier-build/nominal.b3p \
  python3 tests/test_verify_render.py
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/60e8291da354/a21-verifier-build \
  -R '^python_test_verify_render$' --output-on-failure --no-tests=error
```

Results: **34/34 Python methods passed in 1.754 seconds**, preserving all 27
previous methods and adding seven. The focused CTest gate passed **1/1** in
1.75 seconds. The seven additions cover:

1. Explicitly constructed schema-1 note/event grammar fixtures, with no old
   executable or checkout dependency in permanent tests.
2. A real nominal-contact score exercising all four percussion indices, release,
   repress and panic; its serialized audio is nonzero.
3. Actual rendering and independent verification of all 24 combinations of
   contacts, percussion, volume and decay choices.
4. Invalid/missing/extra schema-2 control parameters with strict scalar types.
5. Rejection of version-2 parameters, metrics, argv and percussion events in
   schema 1.
6. Rehashed missing/wrong model identities and renderer-schema type/value errors.
7. Rehashed invalid percussion manual, index, numeric payload and token forms.

The previous tests retain actual-file tampering, strict JSON, path escape,
symlink/inventory, argv/metric changes, current/missing/changed executable and
cross-API metadata observations. Their output remains independent of producer
validation helpers. This assignment made no core behavior change.

Tested identities:

| Item | SHA-256 |
| --- | --- |
| Current Release renderer | `b9c0acab7615820091bd7baaf782d894a8b85bb910a2dfba72b84463445d74c9` |
| Compiled nominal profile | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| Verifier source | `1869d6c81ab417abbb42772f50f255b81fc0ceb760b3bd9440978f12d9af0441` |
| Verifier test source | `52783b1bcc7171471d101ec7311d09a7bab045590f22387243b1c2f3407fa7cc` |

## Historical execution and producer cross-check

A separate scratch check extracted the actual schema-1 producer and compiler
from `7a24a30acd111a8f85cb8df65ba2ca59ada456e3`, then executed the retained
baseline renderer with SHA-256
`8e781cb1df6f87443c4b6c88587cfa0e7d2bc8e23d32b5ef0a0bfb84d9ee8be4`.
The new verifier accepted both genuinely emitted schema-1 bundles: one default
note and one score containing every old event type. Both used 259 frames,
48 kHz, block size 127 and seed 7. Their manifest hashes were:

- Note: `a981cc8e5fc36912038253dac45e5ac9aaff6c5b11aeb21ed3e53ac9e29b63e1`.
- Events: `9edf90269c4d770347324e8d73c18c843db28289226ccadfbba9e54aff54439f`.

This execution is distinct from the intentionally constructed permanent grammar
fixtures. Historical helper copies were outside the checkout; their unavailable
Git association was honestly recorded by the producer. The report still leaves
source/build association unestablished.

Agent 20's four real schema-2 smoke bundles—default, explicit-default, nominal
score and CLI invocation—also passed this independent verifier. Thus this check
accepted two old-schema and four new-schema bundles. Scratch reports are at
`/workspace/scratch/60e8291da354/a21-historical-2j0h30ip/verification-reports.json`;
they are temporary execution evidence, not required repository inputs.

`git diff --check` passed for the owned files. An initial attempted CTest-name
lookup found no literal registration because CMake discovers Python tests by
glob; no test ran in that lookup. The corrected explicit name above passed.

## Limits and next step

These checks establish documented retained-bundle consistency and consumer
compatibility. They do not establish that arbitrary internally consistent
records are truthful, that a renderer matches a source build, or that the nominal
console matches a physical B-3. This assignment ran only Linux Release; the
integrator must verify the complete combined tree and its hosted platform matrix.

Next: finish independent producer tests and reproducible console fixtures, then
publish the combined wave-03/04 checkpoint with updated shared status and the
observed full test/CI outcomes. Keep schema-1 consumption during later extensions;
do not reinterpret historical bundles or silently fill mandatory new fields.
