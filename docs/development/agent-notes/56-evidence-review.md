# Agent 56 — final Python evidence review

Actual original-session wave-10 assignment, 2026-11-13. Baseline `6c3dd8b`;
reviewed the integrating working tree and Agent 51's completed demo/verifier work.
The separate console continuation's assignment IDs remain separate history.

## Scope and ownership

Read standing instructions, status, next steps, plan, acceptance matrix, contracts,
demo/replay records and continuation ledger. Inspected the six Python production
modules and relevant assertions for compiler, factory, capture, producer, analyzer,
verifier and demo. Initial ownership was this note and
`docs/reviews/FINAL_EVIDENCE_REVIEW.md`; root explicitly authorized the two repairs,
their tests and narrow related contract updates after receiving reproductions.

Changed production: `tools/verify_render.py`, `tools/validate_factory_reference.py`.
Changed tests: `tests/test_demo_bundle.py`, `tests/test_factory_reference.py`.
Updated contracts: `docs/RENDER_VERIFICATION.md`, `docs/FACTORY_REFERENCE.md`,
`docs/DEMO_REPLAY.md`. Added the final review and this note. No shared status/log,
frozen artifact, profile, CSV or attestation edits; no staging, commit or push.

## Findings and before/after evidence

F56-1: a real regular file replacing a historical build directory caused its
absent executable child to raise `NotADirectoryError` and fail retained verification.
Reproduced only on a copied demo; the new demo regression also errored before repair.
Added only `NotADirectoryError` to historical availability cases. The eighth demo
method now reports unavailable/replay not performed; present-file checks still pass.

F56-2: factory JSON accepted escaped lone surrogate strings/keys, then a mutated
profile reason reached canonical hashing and raised uncaught `UnicodeEncodeError`.
Before repair, four parser subcases failed to reject and the public target method
errored. `_json` now validates UTF-8 encodability for every string/name inside its
existing error boundary. Two new methods cover both halves/positions, a valid pair,
public comparison rejection, clean CLI exit 1 and unchanged temporary input bytes.

No additional blocking defect found in the inspected scope. Existing root capture
identity fallback plus two regressions were inspected, not rerun. Scope conclusions,
file/race/numeric/ancestry limits and exact reproductions are in the final review.

## Executed commands and results

Before repair:
`python3 tests/test_demo_bundle.py DemoBundleTests.test_absent_historical_renderer_below_regular_file_is_unavailable -v`
errored with `NotADirectoryError` (1 method).
`python3 tests/test_factory_reference.py FactoryReferenceTests.test_json_rejects_unpaired_surrogate_strings_and_keys FactoryReferenceTests.test_surrogate_target_fails_through_public_api_and_cli -v`
failed with 4 subcase failures and 1 `UnicodeEncodeError` (2 methods).

After repair, local Linux/Python 3.12.14:
`PYTHONDONTWRITEBYTECODE=1 python3 tests/test_factory_reference.py -v`: 22 passed.
`PYTHONDONTWRITEBYTECODE=1 python3 tests/test_demo_bundle.py -v`: 8 passed.
`PYTHONDONTWRITEBYTECODE=1 HAMMOND_RENDER_EXECUTABLE=/tmp/hammond-wave07-asuv11lz/build/hammond_render HAMMOND_TEST_PROFILE=/tmp/hammond-wave07-asuv11lz/build/nominal.b3p python3 tests/test_verify_render.py -v`: 27 passed.
All 57 methods passed with zero skips. The existing verifier suite rendered its
small real fixtures with the preserved Release executable; this agent did not build it.

The demo gate rechecked the seven frozen hashes and original dirty `6c3dd8b` record.
Manifest remains `74ad49caa3cc5170870bed1002ea64ffaaf8a202c0614095b31fdcd8308da2ce`;
WAV remains `9c46d82dc8da8ba5be078e895765e98672b51a30da52e0684d75a293aa4d84fd`.
Factory tests preserved original profile/compiler identities and all compiled routes.
Scoped diff/whitespace checks passed; all 28 local links in the changed docs resolve.
The review/note distinguish inspected, executed and not-run evidence.

## Limits and handoff

No broad suite, fresh build, native platform/sanitizer CI, original factory-PDF
reinspection, playback/listening, host/device session or physical acquisition.
Relevant compiler/capture/producer/analyzer assertions were inspected; their full
suites were not rerun here.
The earlier 21-suite hosted result belongs to `6c3dd8b`; the new 23-suite integration
needs its own actual revision/results. Root owns publication and shared handoff.
Software integrity remains separate from physical/authentic/build provenance.
