# 53 — Identity and migration compatibility audit

- **Wave:** 09 of the 60-assignment continuation.
- **Agent:** `/root/w09_a53_identity_compatibility_audit`.
- **Date:** 2026-11-13.
- **Status:** complete; no runtime/data/test change required.
- **Owned files:** this note and [CONTINUATION_IDENTITY_REVIEW.md](../../reviews/CONTINUATION_IDENTITY_REVIEW.md).
- **Publication:** parent coordinator owns staging, commits, and pushes. This
  agent did none and created no subagents.

## Assignment and source inspected

Audit invariant identities against original source
`9c8068c95f6843dce95f7f22d729738eef8074f6` and published continuation
`2046b9388f6aab1122e37646b2f20199b5c6079f`. Read repository agent instructions,
the profile/parameter/control/pedal provenance contracts, actual authoring and
fixture data, current C++ types and control parser, existing migration tests,
render verifier, and retained factory CSVs. Rechecked atlas p.140's full pedal
rule; independently confirmed that the supplied PDF has 500 pages and the
expected hash. This focused assignment does not claim another full-PDF reading.

The coherent executable source tree was
`0c722f1ffa2a2f04522438a4cb86cec6b8d3e392`; published tree was
`759ddcaf93be2047a5732034663e565f728fb5ad`. Their differences were limited to
three Markdown result/index files. All 96 tracked code, header, tool, test,
data, and CMake files examined matched the published source at audit time.

## Work and results

| Check | Observed result |
| --- | --- |
| Actual baseline/published/live bytes | PDF, authoring profile, schema/compiler, pedal map, original catalog and all five score files identical; complete SHA-256 values in the review |
| Canonical and compiled profile | Independently recomputed canonical digest `49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83`; coherent-build compiled digest `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`; both match catalog/header contracts |
| Literal wiring | 549 manual cells and 200 pedal positions match each of two retained factory transcriptions; 195 pedal connections and exactly five nulls at rows 8–12, zero-based column 1 |
| Parameter preservation | All fields of original 39 records unchanged; canonical original-record digest `61669b54e0a0499da950ece28c855e70ab4cb815d204f625f0aee8542d8b4f1b`; only IDs 12288–12291 appended |
| Compiled descriptors | All 43 exported descriptors match registry identity, ranges/defaults, step counts and event targets at normalized input 0.5 |
| Event history | Original baseline 0–7 preserved; intermediate console integration adds percussion 8; current source preserves 0–8 and adds KeyPosition 9 |
| Saved-control migration | Two existing suites passed, including v1 migration across all 16 prior percussion combinations, canonical v2 output, and restore without resetting dynamic history |
| Retained schema-1 bundle | Current verifier passed all six artifacts; no replay; schema-2 changes checked separately in producer/verifier source |

There were no contract mismatches and no proposed corrective code edits.
The raw authoring JSON hash differs intentionally from its canonical digest.
The schema-2 parameter validator intentionally rejects whole schema-1 registry
documents; this is distinct from accepting legacy `B3CONTROLS1` saves and
schema-1 render bundles. The original baseline never contained event value 8;
comparison with console-integration commit
`4ead76957c763afbbddde1bc96f1128384329e50` establishes that additional invariant.

## Reproduction and bounded validation

Read-only comparison used `git show <revision>:<path>` for both revisions and
live file bytes, then SHA-256. JSON records were compared as complete decoded
objects keyed by parameter ID. Canonicalization details and exact source links
are in the review. The one-off inspection script and JSON export were scratch
intermediates at `/workspace/scratch/60e8291da354/a53-identity-audit/`; durable
results are contained in the two owned documents.

Commands below were run from the repository root. The build path and CTest
path identify this session's coherent tools, not portable installation paths.

```sh
pdfinfo Hammond_B3_Leslie_Research_Atlas_500pp.pdf
/workspace/scratch/60e8291da354/checkpoint-w08-build/hammond_parameter_info --normalized 0.5
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/ctest --test-dir /workspace/scratch/60e8291da354/checkpoint-w08-build -R '^(test_control_io|test_percussion_controls)$' --output-on-failure
python tools/verify_render.py examples/rendered/nominal-two-manual-v1/bundle
```

CTest reported 2/2 passing in 0.04 seconds. The retained bundle verifier
reported `verified_retained_bundle`, schema 1, 192,000 frames at 48 kHz.
It explicitly did not perform replay or establish authentication, original
source/build association, or physical fidelity. No full suite, audio matrix,
platform qualification, or new tests were run by this assignment.

Read-only inspection corrections: an initial script treated `manual_map` as a
list; inspection confirmed the matrix is under `manual_map.tone_ids`. Two
guessed documentation/tool paths did not exist; file discovery located the
actual `tools/render_fixture.py`. A large combined read was truncated and the
required sections were reread in bounded calls. None of these attempts changed
repository state; the final data comparison and validation commands succeeded.

## Handoff and next task

The next pedal or host implementation must preserve the exact IDs and version
boundaries listed in the review. Begin by specifying the new input/parameter
and saved-state migration contracts, retaining the 25×8 literal pedal map and
its five disconnections. Keep documentary factory-wiring agreement separate
from nominal pitch/amplitude/phase assumptions and unmeasured physical gains.
The review grants no pedal-audio, native-host, measurement, or DSP-resume claim.

The parent coordinator can integrate these two Markdown files and link the
review from the shared handoff. No external permission, measurement, or code
decision is required to publish this completed audit.
