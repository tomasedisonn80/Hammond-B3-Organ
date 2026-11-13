# Assignment 57 — final offline evidence review and renderer stdout repair

Agent: `/root/w10_a57_final_evidence_review`

Date: 2026-11-13 UTC. Continuation wave 10, assignment 57 of its separate sixty
actual assignments. Root owns shared status, accounting, integration and publication.

## Scope and files

Independently reviewed renderer/evidence producer/verifier, trace/plot contracts,
the actual retained console demo and schema1 compatibility against frozen tree
`805900d2339eb3975019581de5f8469e72e7509f`. Read the standing workflow, current
handoff/plan/evidence documentation and all text on atlas pp. 355–360. This is not
another full-PDF reading or a new count of earlier reviewers.

Original ownership was this note and
[FINAL_CONTINUATION_EVIDENCE.md](../../reviews/FINAL_CONTINUATION_EVIDENCE.md).
After the actual stdout-failure reproduction, root explicitly extended ownership
to `tools/render.cpp`, `tests/test_render.py` and `docs/RENDER_FORMAT.md` for the
narrow repair, regression and publication-boundary explanation. No core/header,
profile, retained demo, other test, shared status or manifest was changed.

## Actual findings and checks

- Independently verified all **338 frozen source blobs** against the Git tree.
  All **16 provenance inventory entries**, five Python tool hashes and the
  retained/original score equality passed.
- The genuine schema2 console and schema1 original bundles both verified, six
  artifacts each. Their historical external executables currently matched;
  the verifier explicitly reports that it performs no replay.
- Performed actual two-second producer replay at **block size 257** using the
  frozen build, then repeated with the repaired build. Both new bundles passed
  independent verification. All 384,044 WAV bytes equal the retained block-127
  artifact: SHA-256
  `3cbfc2a80ee5ed014782d9abe33d5afc2cd7e494f3efdba280939b4d3d8f56b5`.
- Independently decoded PCM for all five retained windows. Peak, RMS, nonzero
  counts and endpoint counts agree. Channels are identical; the final 7,680
  frames are exactly silent. The retained pitch-estimator value was hash-checked,
  not independently recalculated in this assignment.
- Fresh actual trace and plot exactly reproduce retained CSV/SVG hashes
  `dbaa075fcd7bea24b4a61a5df8f55faab53053244ad1e59126ba3f4d80fd89b2` and
  `76d8583e00977856e54e61fbb1691ff2f7ffb3e2e9f86e0ee5f807e9bdc203a4`.
  Confirmed 5,760 rows, separate 120 ms schedule, all sustained drawbars zero,
  four versus five closed contacts at target/position 0.5, and the SVG's exact
  CSV identity and reduction declarations. XML has no external resource.
- Seven actual no-clobber probes passed: existing regular files and dangling
  symlinks for renderer/trace/plot, plus an existing producer directory. All
  returned 1, preserved existing content/targets and left no temporary residue.

## Reproduced defect and narrow repair

The frozen renderer returned **0 with empty stderr** when stdout was a read-only
file descriptor, both for help and the small JSON summary. Its WAV was already
published. The stream was checked before buffered bytes were flushed. The new
permanent method reproduced both failures against the old binary: **one method,
two failing subcases, 0.007 seconds**. This is retained failure evidence, not a
claim that the old full suite caught the missing case.

Added explicit flush/check for help and the summary. Failure returns 1 with a
useful stdout diagnostic. The regression checks preservation of the sink and
input, no temporary residue, and the valid complete WAV that remains after the
later summary error. The contract now explicitly distinguishes WAV publication
from summary delivery; successful evidence requires both exit success and a
valid summary, and an output file alone cannot prove success.

Root authorized the repair before edits. It was built in a private complete copy
of the frozen tree, with only the two source/test overlays. The shared frozen
archive/build and other workers' files were untouched. GCC 14.2 Release and Python
3.12.14 observed:

| Check | Result |
| --- | --- |
| Coherent strict configure/build | Passed |
| New focused stdout method, both paths | Passed, 0.006 seconds |
| Entire renderer suite | **35 passed**, zero skips, 2.174 seconds |
| Repaired producer/verifier replay | Passed; byte-identical retained WAV |
| Post-run identity | 338 original blobs unchanged; 336 non-overlay repaired-copy blobs unchanged |

Tested overlay SHA-256 identities:

- `tools/render.cpp`: `292d277dd6728ed5241af2ca163a943140c0165711a399c08ce3c82c8168490f`.
- `tests/test_render.py`: `db8411241338a3e9ad51c0b34abd5afb675f179f22416f9ba19a45d0830a8ac7`.
- Repaired renderer: `eee31ffdef6275165fe6b492b34e04c9739e7d6bec6199fbebd16901550a129b`.

The full review retains source identities, actual commands, artifact and PCM
results, failure semantics and limitations. Scoped whitespace and local-link
checks passed before final handoff. All five owned files are frozen for root.

## Limits and exact next step

No claimed source/build authentication, physical calibration, audible listening
trial, plugin/device operation, callback deadline, new visual rendering, broad
CTest matrix or native cross-platform repair qualification. The example remains
synthetic; its diagnostic plot has a different score/registration from its WAV.
No additional actionable artifact-integrity defect was found in the inspected
scope. The original unmodified historical bundles and their hashes remain intact.

Root must integrate the two source/test repairs and contract text, qualify the
combined frozen archive, publish using its expected-head guard, observe hosted
results and update the final sixty-assignment gate. This worker did not stage,
commit, push, change accounting/shared status, or spawn another agent.
