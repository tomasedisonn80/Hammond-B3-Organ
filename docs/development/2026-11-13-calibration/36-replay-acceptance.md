# Assignment 36 — independent complete-report replay acceptance

Actual worker identity: **`/root/cal_w6_a36`**, assignment **36**, logical
wave **6** in the `2026-11-13-calibration` session. This is one actual new
assignment. The session continued across midnight; this acceptance completed
on **2026-11-14 UTC**. Prior readers, fixture authors, subprocess probes and
test reruns are not counted as new workers.

Working directory: `/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ`.

## Ownership and source context

Owned files are exactly:

- `tests/test_capture_replay.py`
- `docs/CAPTURE_REPLAY_REVIEW.md`
- This assignment note.

No producer, contract, schema, checked-in example, shared status document,
session ledger, CMake file or Git ref was modified. Source-mutation tests use
temporary copied source trees; the repository implementation remains unchanged.
Root owns acceptance integration, shared progress and publication.

At initial observation the checkout was commit
`fd0fb58d2f882aa76c7e40e510f44766f762727c`, tree
`3329cf68bb9ea84479e254934778935bb5c44773`, with locally recorded `origin/main`
`0085e338388f2c7516a7d455f11692b94e9451f4`. At final test inspection the checkout
and locally recorded `origin/main` were
`955fc4c41f74ada094f14fbaf386c943811e9050`, tree
`70956d0f0e125d57abfbf1aed56460c067f8ef28`. Root performed the concurrent
integration/publication. This worker did not fetch or verify a remote push.
Neither checkout observation claims the then-uncommitted replay source/test
belonged to that commit; the exact byte identities below identify this result.

## Basis and contract clearance

Read the standing `AGENTS.md`, calibration scope and operational handoff,
project plan/atlas review and active status/next-step context, the complete
job and study contracts, the prior job-composition and hosted-portability
findings, and the complete frozen replay guide. Read fresh extracted atlas
text on pp. **355, 364, 484 and 486**. Those pages require preserving original
evidence boundaries, declared corrections/uncertainty, failed/inconclusive
results and code/data/setup identity. They do not prescribe this replay API
or its software limits. The six earlier actual readers own the full 500-page
coverage; this assignment claims no additional complete PDF reading or
original-page-image inspection.

The full replay contract was independently cleared at SHA-256
`1d855c9c734f0f8e9c3d73e4a735c9ef5d86066b734d1a74b95426545f3d3d88`
before grading. Its boundaries are explicit and compatible: strict canonical
saved-byte and envelope admission; original-input identity preflight; actual
public execution; complete canonical-byte comparison; source/runtime context
without inferred authenticity; and final replay-owned snapshots. No blocking
contract ambiguity or contract revision was requested.

The guide states that the public runner independently owns its artifact
snapshots through its return. Replay retains the report, original input and
source snapshots through its later return. A race between preflight and the
public read may perform bounded artifact work before rejecting the returned
consumed identity. The tests preserve this scope instead of inventing an atomic
preflight or a hostile-filesystem guarantee.

The producer announced readiness at `23dc1c…`; no missing or unready API was
graded as a failure. Main public-behavior tests were authored from the frozen
contract first. The complete producer was then read to review composition and
place targeted private-boundary/resource probes. It remained unchanged through
the final run. Root's earlier audio/corpus portability repairs are separate
accepted work, not findings or repairs by this assignment.

## Exact qualified identities

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `tools/verify_capture_report.py` | 23,380 | `23dc1c316232c27345ce35beec667a1e604847dc30b31b9b0b8bfc63423dd2d4` |
| `tools/capture_audio.py` | 29,951 | `b1f6228932c15f6483808cbb36a407dcdd6919f5894439d93f8888b01d66113c` |
| `tools/capture_common.py` | 9,625 | `e06dd82e37dd178863af61aa66bee877da1fc7e498a47b729e060215ca79c3f2` |
| `tools/capture_corpus.py` | 39,220 | `1c68ca13157f767847258ccb74f3a22f49cc1d56f323cddeebd52f3ab85ed5ba` |
| `tools/capture_job.py` | 24,302 | `147002ac866a4451e6740eae69da9f914116339f89b657bae7d4c6ef41e3eded` |
| `tools/capture_study.py` | 16,740 | `4b627a8c213ff43691e8011dca0a4206db8f4184dd32b5ea6edad4471f90e69d` |
| `tools/compare_capture.py` | 33,448 | `220a593499539db5f1e635db2eb15ba3c0aa7c6d001c80407fbffe93f75a9a0a` |
| `tools/validate_capture.py` | 24,827 | `a872e069ba9744f6f8078f87b78ea300df1ee28aec58e104859580cdc09877af` |
| Frozen `docs/CAPTURE_REPLAY.md` | 18,044 | `1d855c9c734f0f8e9c3d73e4a735c9ef5d86066b734d1a74b95426545f3d3d88` |
| Final `tests/test_capture_replay.py` | 62,858 | `ad4e364794e8fffda5e2959f90c046def0a0d6471b3ff049e2b9a93ea03e9d55` |
| Independent job fixture author | 78,683 | `0d74f5bff69bb094165992891d3da0c61b73c0543e21e311b36e792ec90e4f12` |
| Independent study fixture author | 70,397 | `19f3c58d91026292d353434b6c0ac0348361c7a4f645b7d62f71c470c45dd8c6` |
| Independent corpus fixture author | 52,143 | `a6b688b19e4fdd60d744c9f5b32cf03e526b3ae187b8ac0b91624e0a95b8ed9c` |

The last three files are `tests/test_capture_job.py`,
`tests/test_capture_study.py` and `tests/test_capture_corpus.py`. They are imported
as modules only for independent archive authoring; their `TestCase` classes are
not imported or recounted. This worker did not rerun those complete historical
suites or claim their earlier results as new acceptance.

Expected report-summary keys, statuses, context rules, byte identities and
runtime/source observations are assembled separately from the verifier. Literal
raw/decoded digests and `0.25 FS` RMS expectations come from the cleared job
contract. Existing public job/study executions produce the actual saved report
artifacts to be replayed; no replay output generates its own expected result.

## Commands, observed results and retained first failure

Runtime: **CPython 3.12.14, Linux x86_64**. Only standard-library tools and
existing project modules were used. No package or runtime dependency was added.

Commands from the working directory above:

```sh
python3 -B tests/test_capture_replay.py -v
python3 -B tests/test_capture_replay.py
```

| Actual run | Test source SHA-256 | Result |
| --- | --- | --- |
| First graded run | `82dd09e7c2ba246e49ba90edfb38e6286bfd96d22e7421d9cf1cd1f39023651a` | 69 methods in 7.584 s: 68 passed, one reviewer-fixture assertion failed; no errors or skips. |
| Corrected run | `050ca7b2db24f56db99feab549679fd9065feb435bef6d948e74ee60f53ee724` | **69/69 passed in 8.070 s**, no failures, errors or skips. |
| Final file after EOF formatting cleanup | `ad4e364794e8fffda5e2959f90c046def0a0d6471b3ff049e2b9a93ea03e9d55` | **69/69 passed in 8.946 s**, no failures, errors or skips. |

The first failure occurred in
`test_all_three_job_outcomes_match_without_relabeling_engineering_result`.
The assertion compared the RMS metric record
`{"value": 0.25, "unit": "FS", "undefined_reason": null}` directly with
`0.25`, before invoking replay in that method. The comparison contract represents
metrics as records. The sole correction selected the existing `value` field;
the exact expected value remained **0.25**. No producer, contract, source bound,
threshold, margin or other expectation changed. The complete unchanged
69-method scope was then rerun and passed. Final text QA subsequently identified
one redundant EOF blank line in the test. That one byte was removed, and the
exact final file was rerun as shown above. No executable test statement changed
in this formatting cleanup. The initial graded failure remains a harness lookup
failure, not a producer defect or an erased first result.

Before the first graded run, ordinary fixture authoring was reviewed against
the existing archive helpers. The artifact locator uses the established
`file_path` helper, and the rejected generic path-like object returns a real
path if invoked. A speculative help-plus-unknown precedence case was removed
before grading; independent help and unknown-option rules remain tested.
These were pre-run harness construction decisions, not production fixes.

An AST count identifies exactly 69 final test methods:

| Group | Methods |
| --- | ---: |
| Complete results and summary oracles | 13 |
| Saved/input envelope admission | 17 |
| Resource boundaries | 8 |
| Identity and filesystem observations | 15 |
| CLI and failure-preserving publication | 16 |

Each final run contains **six actual replay CLI processes** and **nine
temporary-source mutation subprocesses**. In-process `main` calls, subcases and
the first/final reruns are not additional distinct methods or workers. All native
Linux capabilities exercised here were available; future unavailable link/FIFO
capabilities produce explicit skips.

## Coverage and practical limits

The detailed reasoning is retained in
[CAPTURE_REPLAY_REVIEW.md](../../CAPTURE_REPLAY_REVIEW.md). Meaningful checks
include all three job outcomes and a mixed study; all-fit zero-final coverage;
literal source/audio identities; exact complete summaries; Unicode relocation;
fresh returned-copy ownership; and preservation of every original file.

Complete-byte comparison is tested with changed metrics, removed comparison
content and changes in each retained nested area. A controlled fresh-return
case uses integer `1` versus saved floating `1.0`: Python value equality is true
but canonical bytes differ, so replay must mismatch. This prevents selected
field or dictionary equality from substituting for complete-byte comparison.

Admission covers strict bytes and exact job/study envelopes, every required
root field and physical claim, invalid built-in types, source/runtime shapes,
identity bindings, outcome precedence, ordered nested jobs, work and role
counts. Preflight traps prove rejected saved reports and changed original
input do not invoke the public runner. Current archive rejection yields an
error, never a fabricated mismatch summary.

The actual saved-report boundary probe reads an exactly **16 MiB** canonical
envelope containing bounded extra nested data and reaches an explicit execution
sentinel. One extra byte rejects. This is not a naturally generated maximum-size
job report or a maximum matching replay. Actual **64 KiB input** and **1 MiB
associated-source observation** boundaries are separately exercised. The latter
redirects the associated file observation to a temporary padded file; it does
not claim authentication or execution of changed loaded Python memory.

Report/summary node/depth limits use independently counted real values and
reduced equality/one-less guards. A nested job exceeding its own depth bound
rejects within an otherwise admissible study depth. Exact integer magnitude
boundaries avoid float rounding. Ordinary replay counts are nine observations
for a job and ten for a study, separately from the public runner's snapshot set;
reduced caps prove rejection rather than dropped observations.

A real 192-criterion original compact policy fits 64 KiB while its formatted
copy exceeds that limit. Job execution and replay preserve its original bytes;
the verifier does not reparse a formatted substitute. No maximal audio or
spectral workload is inferred from these small numerical fixtures.

Final-boundary changes to saved report and original input, same-byte leaf
replacement, runtime changes and incompatible fresh-return identities reject.
Harmless sibling activity remains valid. A public-read race actually consumes
changed input after preflight and performs bounded work, then rejects: the
contract's composition limit is tested without claiming earlier rejection.
All intended mutation hooks are explicitly reached. Paths are canonicalized
before hook targeting to avoid the earlier macOS/Windows temporary-alias error.

Seven copied-source probes change each job dependency or the verifier after
public return. An eighth covers the study's additional source; a ninth changes
a source before the public read but after replay inventory. No live repository
source is mutated. These controlled changes are not exhaustive scheduling,
native Windows reparse coverage or hostile-filesystem security evidence.

CLI checks retain the distinction between `match`/`mismatch` and the underlying
engineering status. Canonical UTF-8/LF output survives ASCII/CRLF wrappers and
foreign Unicode paths. Existing/raced outputs, original inputs, links and
directories remain intact; missing parents are not created. Complete output
survives cleanup or later stdout failure, with explicit failure disclosure.
Cancellation propagates and short output is not reported as success.

## Handoff

The contract is cleared and the announced producer passes this independent
acceptance without a production repair. Root and assignment 35 received the
first failure classification, final passing result and exact source identities.
Root should include these three files in the coherent integration source,
verify configured test discovery, qualify the installed/relocated workflow,
update shared status/next steps/log/ledger and perform the authorized commit/push.
All installed source dependencies and original archive bytes must remain
available together; a saved report cannot reconstruct their original whitespace.

No native macOS/Windows execution, installed-prefix acceptance, hosted CI,
full maximum audio/spectral workload, complete maximum report generation,
historical chronology, physical acquisition, specimen identity, permissions,
calibration, listening, host/device qualification or physical fidelity is claimed.
Future source/runtime/input changes require a new explicit replay and retained
result; an old digest does not qualify changed code.
