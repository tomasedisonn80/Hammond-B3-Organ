# Assignment 22 — independent schema-2 producer verification

Agent: `/root/w04_a22_evidence_producer_tests`

Wave: 04, assignment 22 of this continuation's 60 new assignments

Date: 2026-11-13

Starting published HEAD: `7a24a30acd111a8f85cb8df65ba2ca59ada456e3`

## Scope and inputs

Owned files are `tests/test_render_fixture.py` and this note. Agent 20 owns the
producer implementation and evidence-format document; agent 21 owns independent
bundle verification. No producer, renderer, engine, CMake or shared status file was
modified by this assignment. No commit, push or index operation was performed.

Read `AGENTS.md`, the current README/status/next-step/log documents, the project
plan, atlas-review evidence boundaries, continuation ledger and the relevant
console/evidence contracts. The source basis for acceptance-record identities and
explicit software/physical boundaries is retained in the atlas review, especially
atlas pp. 355–360, 372 and 481–486. This assignment does not claim another complete
PDF reading or physical-instrument verification.

The producer's frozen v2 contract was coordinated with agent 20. Tests independently
spell out its 13 parameter keys, 18 renderer-metric keys, two contact identities,
shared-readiness identity, integer version fields and fixed argument ordering.
They do not obtain those expectations from the producer's schema constants.

## Changes and observations

All **19 previous methods remain**. Eight new methods bring the suite to **27**.
Every successful-run assertion now checks exact v2 field sets and types, model
binding, every explicit console flag, fixed copied-file paths and the mutually
exclusive final score/note arguments. Existing hash, PCM, replay, CRLF, Windows
metadata, file-race, no-clobber, clipping, process-failure and bounded-capture
checks remain in place.

New independent checks cover:

- Implicit and explicit ideal/off/normal/slow defaults, compared against a direct
  real-renderer invocation using only the older flags: complete WAV bytes and all
  current metrics agree. The expected default parameter record is a fixed literal.
- All **24** contact/percussion/volume/decay combinations, rendered through the
  actual C++ executable with sustained drawbars zero. Disabled percussion is
  silent; enabled percussion produces audio; nominal harmonic contacts begin only
  after their documented travel thresholds. Soft audio is half Normal within one
  PCM integer step. Harmonic and decay selections produce distinct PCM.
- Exact BOM/CRLF score retention and all four percussion indices with accepted
  finite integer spellings (`1.0`, `1e0`, `+1`, `01`). Frame-zero score controls
  override initial choices and match a separately initialized render byte for
  byte; a frame-zero disable produces silence while the manifest retains the
  requested initial selection.
- A 12-event nominal-contact score with overlapping notes, tied release/repress,
  Cancel/reselect and percussion changes, replayed at three sample rates and four
  block sizes. WAV bytes and metrics other than block size agree within each rate.
- **56** invalid API choice/type cases, **25** invalid percussion scores and
  **20** invalid CLI cases. They reject before output-directory creation;
  API/score checks also assert the renderer is never launched. Duplicate, missing,
  abbreviated and case-mismatched options remain errors.
- **19** captured-metric mutations after actual successful C++ execution:
  missing/extra/mixed-version fields, wrong version values/types and incorrect
  contact/percussion model identities. Each retains the actual mutated stdout and
  its hash, records a metrics-stage failure and supplies no successful WAV record.

The eight added methods execute 62 real renderer calls, including the 19 deliberate
post-execution metric mutations. Temporary bundles and audio are cleaned by the
tests. Permanent tests contain no session-specific executable or filesystem path.

## Executed verification

The existing isolated Release renderer built by assignment 18 was used. Command:

```sh
HAMMOND_RENDER_EXECUTABLE=/workspace/scratch/60e8291da354/a18-renderer-build/hammond_render \
HAMMOND_TEST_PROFILE=/workspace/scratch/60e8291da354/a18-renderer-build/nominal.b3p \
python3 tests/test_render_fixture.py
```

Observed result: **27 tests passed in 4.401 seconds**, zero skips. Scoped
`git diff --check -- tests/test_render_fixture.py` passed. No producer defect was
found; agent 20 received the results.

| Observed input | SHA-256 |
| --- | --- |
| Release renderer | `b9c0acab7615820091bd7baaf782d894a8b85bb910a2dfba72b84463445d74c9` |
| Compiled nominal profile | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| Producer at verification | `56369c6516065e9f7521cd3cd5a80ba509fae4803333ece801a85893571e3fa1` |
| Updated test source | `51efafa99b7a8aecdfa6b69f8e5e17d8c117cae11ba5ab10d793a54625f819eb` |

These hashes identify observed files; published HEAD alone does not identify the
uncommitted integration under test. Exact combined-tree publication and hosted
qualification belong to the integrator.

## Limits and next step

The legacy-flag comparison uses the current executable with console flags omitted;
it is a permanent default-selection regression, not a historical binary claim.
Historical-renderer compatibility was separately checked by assignments 18 and 20.
Model timing and gain assertions verify the named nominal software factories.
They do not establish physical contact mechanics, measured percussion circuitry,
audio-device deadlines, VST3 qualification, authenticity or reproducible builds.

Next: integrate these two files with the producer and independent v1/v2 verifier,
run the full suite against a fresh build of the exact staged tree, then publish
with the expected-head guard and observe the complete hosted platform matrix.
