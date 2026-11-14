# Assignment 31 — fixed, identity-bound capture studies

Actual worker identity: **`/root/cal_w6_a31`**, assignment 31 of logical wave 6
in the 2026-11-13 calibration session. This is one actual new assignment; earlier
workers, acceptance reruns and source readers are not recounted.

Working directory:
`/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ`.

This worker owns only these repository changes:

- `tools/capture_study.py`
- `data/capture-study.schema.json`
- `docs/CAPTURE_STUDY.md`
- This assignment note.
- The expressly released minimal private binding/shared-snapshot extension in
  `tools/capture_job.py`.

The worker did not change any other production code, existing schema, test,
shared status, CMake file, session ledger or Git ref. Root owns integration,
acceptance, shared documents and publication. The scratch author-check harness
is development evidence, not an installed tool or new maintained acceptance suite.

## Source basis, ownership release and contract review

At first observation the checkout was commit
`779fb6e13b8f60236cad4aedb9999ba16198f920`, tree
`f9baccbb54f51063b01a0859d2c10cdadfbd238b`; locally recorded `origin/main`
was the same commit. Job ownership was explicitly held while root froze accepted
wave-5 code. Root then committed/archived that code as
`d68058d01272aadeea698a9cf788d261ba822285`, tree
`87ce5e7edefdb4267d947b65569e42b5c2197517`, and expressly released the minimal
private-core extension. No job source was edited before that release.

Read the standing `AGENTS.md`, current scope/handoff and status context, project
plan, entire job contract and guide, comparison/policy contract, corpus contract,
job/common implementation and relevant corpus confinement helpers. Read fresh
atlas text on pp. 355, 364, 484 and 486. Those pages require original evidence
boundaries, explicit corrections/uncertainty, retained failures and code/input
identity. They do not prescribe this study schema or software resource limits.
The six earlier actual readers own the fresh complete 500-page reading; this
worker does not claim another full reading or original-page image inspection.

The study proposal was approved by root before implementation. The complete
[study contract](../../CAPTURE_STUDY.md) was then written and frozen at SHA-256
`a60d8c6a92356f2381ea61ba39c0dab50048b0f88ee6dc75bf943c7f5c5198e3`.
Independent worker 32 read and cleared the entire guide before grading code.
Its preliminary review specifically checked the distinction between all-job
header/work admission and each job's later dependency admission, and independently
confirmed the 2,642-leaf/58-root bookkeeping derivation. There was no unresolved
blocking contract ambiguity at implementation readiness.

## Implemented behavior

The public module exposes `StudyError`, `validate_study`, `load_study`,
`run_study` and `main`. The exact input contains a study ID, one expected
corpus-index digest and one through eight job ID/path/digest bindings. IDs,
case-folded paths and digests are each unique. All input bytes use bounded
strict UTF-8 JSON, exact built-in types and the existing portable path grammar.
The original study bytes are identified rather than a normalized reserialization.

Before artifact work, the study reads and admits **every job file**, matches
its actual byte digest, validates the unchanged job shape, requires its job ID
and declared corpus digest to match, and checks the cumulative window/spectral
work. These preflight reads remain confined under the already selected study
root; they do not append an extra selected root per job. Each job later admits
its policy/manifests before that job's artifacts, preserving the existing job
contract. A later dependency error may follow earlier computation, but no partial
study report is returned or published.

The public `run_job(path)` retains its signature and delegates to one private
`_run_bound_job` implementation. The private core optionally receives the exact
expected job SHA and the shared snapshot object. It checks the actually consumed
job SHA immediately after the bounded job read, before any corpus or policy read.
The complete existing execution tail and error handlers remain unchanged. An
AST comparison against the released `d68058d` job confirms the public arguments
and return annotation, the complete execution tail after the new gate and its
exception handlers are identical. No report field or six-source observation was
added to the ordinary job report.

One shared snapshot set lives through the complete study. It retains the study,
both job-file observations, every constituent index/policy/manifest/artifact,
confined parent chains and all source observations. Earlier snapshots are never
replaced. Every constituent job performs its existing checks; final study
verification additionally retains every earlier input through final return.
Hard bounds reject before adding more than 3,000 leaves or 64 selected roots.
The contract derives ordinary maxima of 2,642 leaves and 58 roots for eight
maximal jobs. Directory identity, rather than timestamps changed by siblings,
defines the directory checks. Quiescent-file checks are not a hostile-filesystem
sandbox, code signature or loaded-memory attestation.

Every valid job is executed in declared order and its full result is retained,
including failed/inconclusive results and unrelated whole-corpus findings.
Runtime identity and all six actual source observations must agree across jobs.
The study adds its own observed regular source file as the seventh source, while
nested job reports remain unchanged. After each completed job the growing report
is bounded at 16 MiB, 1,048,576 value nodes, depth 40 and magnitude 4e18. No result
is truncated or discarded to produce an admissible passing report.

Failure dominates inconclusive, which dominates pass. Exact job/status/role
counts remain visible, including zero roles. An all-fit or otherwise incomplete
physical-protocol role set can pass the requested engineering checks. It does
not establish physical calibration, held-out independence or untouched final
use. All ten top-level physical/provenance claims remain `not_established`.
No fitting, threshold editing, gain/delay adjustment, resampling or channel
reassignment is introduced.

The CLI admits only input, optional new output and help. It rejects duplicate,
empty, abbreviated or unknown options. Reports are canonical UTF-8 bytes even
under an ASCII-configured text wrapper. Fresh no-clobber file publication precedes
stdout, with the existing helper's explicit completed-publication cleanup failure
behavior preserved. Existing destinations and inputs remain unchanged. An actual
stdout failure may leave delivered partial bytes or a complete already published
file and is not reported as success. Cancellation propagates.

## Frozen implementation and dependency identities

Root separately repaired audio/corpus CLI byte emission and canonical temporary
path targeting in independent admission fixtures after observing hosted
Windows/macOS failures. This worker did not author or edit those repairs.
Their final hashes were explicitly supplied by root before the final regression
repeat. Only those frozen final results below qualify this producer handoff.

| Exact file | Bytes | SHA-256 |
| --- | ---: | --- |
| `tools/capture_study.py` | 16,740 | 4b627a8c213ff43691e8011dca0a4206db8f4184dd32b5ea6edad4471f90e69d |
| `tools/capture_job.py` | 24,302 | 147002ac866a4451e6740eae69da9f914116339f89b657bae7d4c6ef41e3eded |
| `tools/capture_audio.py` | 29,951 | b1f6228932c15f6483808cbb36a407dcdd6919f5894439d93f8888b01d66113c |
| `tools/capture_corpus.py` | 39,220 | 1c68ca13157f767847258ccb74f3a22f49cc1d56f323cddeebd52f3ab85ed5ba |
| `tools/capture_common.py` | 9,625 | e06dd82e37dd178863af61aa66bee877da1fc7e498a47b729e060215ca79c3f2 |
| `tools/compare_capture.py` | 33,448 | 220a593499539db5f1e635db2eb15ba3c0aa7c6d001c80407fbffe93f75a9a0a |
| `tools/validate_capture.py` | 24,827 | a872e069ba9744f6f8078f87b78ea300df1ee28aec58e104859580cdc09877af |
| `docs/CAPTURE_STUDY.md` | 19,910 | a60d8c6a92356f2381ea61ba39c0dab50048b0f88ee6dc75bf943c7f5c5198e3 |
| `data/capture-study.schema.json` | 2,102 | 1805ad62f357ec7f828591dce0a968391beba42418b9ea4f20adfe4139389e3d |
| `tests/test_capture_job.py` | 78,683 | 0d74f5bff69bb094165992891d3da0c61b73c0543e21e311b36e792ec90e4f12 |
| `tests/test_capture_corpus.py` | 52,143 | a6b688b19e4fdd60d744c9f5b32cf03e526b3ae187b8ac0b91624e0a95b8ed9c |
| `tests/test_capture_corpus_admission.py` | 51,275 | a0a445ed56279944c959760cc56b4d990429edf864a4ee6cf480cadc7e0e75c2 |

The cleared job contract remains
`ed0b34cbd45d737ea35b33d3049d1b8884f8f665d4f42caeb1e1406466217b84`.
The implementation and guide hashes above were observed unchanged after the
final executions. Commit/tree observations name concurrent checkout context;
they do not imply these then-uncommitted bytes were present in an earlier tree.

## Executed checks and retained failure history

Runtime: Python 3.12.14 on Linux x86_64. No new runtime dependency or package
installation was needed. The schema itself passed `Draft202012Validator.check_schema`
using already installed `jsonschema` 4.26.0 as an authoring audit tool only; that
package is not imported by the study and is not a runtime requirement. Both
edited Python files passed `ast.parse`.

From the working directory given above, the final commands were:

```sh
python3 -B tests/test_capture_job.py
python3 -B tests/test_capture_corpus.py
python3 -B tests/test_capture_corpus_admission.py
python3 -B /workspace/scratch/c9f3ead4c910/study-author-check.py
```

| Final execution against the frozen dependencies | Result |
| --- | --- |
| Existing independent job suite | 81 methods passed, 0 failures/errors/skips, 5.778 seconds. |
| Existing independent corpus suite | 47 methods passed, 0 failures/errors/skips, 1.216 seconds. |
| Existing independent corpus admission | 58 methods passed, 0 failures/errors/skips, 2.162 seconds. |
| Author study smoke | 61 assertions in eight groups and seven actual CLI subprocesses passed, exit 0. |

The author harness SHA-256 is
`9b45e802c26c1e982fa3f1c54c87c855f49a10c0a62eea62447536dc662192f9`.
It uses temporary archives and existing independently authored fixture writers
solely to construct inputs. Its expected literal outcomes, counts, byte hashes,
work and source identities are computed independently of the study's helpers.
It is producer-authored smoke evidence, not assignment 32's independent acceptance.

| Smoke group | Actual observed scope |
| --- | --- |
| One literal job | The quarter-offset vector passes with margin 0.125 and bound 0.375. The full retained job report equals an ordinary public job execution; input/source hashes and all unknown claims match. |
| Eight real jobs | Four passing, two failed and two inconclusive literal policies produce failed study status while retaining all eight in declared order. Exact totals are 32 selected window samples and 32 spectral terms. The same snapshot instance retains **114 actual leaves and 58 roots**. Repeat and Unicode relocation produce identical canonical bytes. |
| Bound identity | A wrong expected job hash rejects before a trapped corpus/policy reader. A job modified after upfront admission rejects rather than driving unbound work. |
| Cumulative work | Two actual bounded job headers declaring 16,777,216 spectral terms each reach the execution sentinel at the inclusive 33,554,432 total. A third rejects before any job executes. No maximum spectral calculation or large audio scan occurs in this admission probe. |
| Role boundary | A one-job all-fit study passes its numerical checks, reports zero final-test jobs and retains every physical/provenance limit. |
| Strict value shape | Invalid root/version/field forms, terminal controls and duplicate job ID/path/digest reject with `StudyError`. |
| Final shared checks | A first job file changed after the last job's return but before study return is rejected by the final shared snapshot verification. A deliberately lowered report-byte cap rejects instead of truncating. |
| Real CLI | Foreign working directory, Unicode archive roots and retained Unicode reason text survive `PYTHONIOENCODING=ascii`/`PYTHONUTF8=0`; output equals canonical report bytes. Actual pass/failed/inconclusive and usage exits are checked. A pre-existing report is preserved with empty stdout on rejection. |

The first author-smoke attempt exited 1 because the test fixture incorrectly
assigned a nonnull `rights.unknown_reason` while retaining a known rights value.
The unchanged capture validator correctly rejected it with
`rights.unknown_reason: expected None`, before a study report existed. The author
changed the fixture to an explicit null value with its intended unknown reason;
no production source, contract or expected numerical outcome changed. The
corrected harness then passed, and passed again after root's portability freeze.
This setup failure is retained rather than reclassified as a producer defect.

Earlier development repeats passed job 81, corpus 47 and the then-current 57-method
corpus admission suite, before root completed the portability work. They are not
claimed as final frozen qualification or additional distinct acceptance methods.
The final 81/47/58 repeat above resolves that changing-dependency boundary.

## Handoff and remaining gates

Root and independent worker 32 received the API-ready notice, exact source
identities and final regression results. Worker 32 owns separately authored
study acceptance; its tests do not inherit this smoke as independent evidence.
The guide's complete snapshot, before-work binding and report-retention rules
must remain authoritative when a later defect is found. Preserve the original
counterexample and expectation; do not silently weaken a contract to obtain pass.

Root should accept the producer only with the independent result, verify test
discovery and a coherent integration source, update current status/next steps/log/
ledger, and commit/push under the standing authorized workflow. Packaging must
retain the seven observed source files together. Later demo/replay work should
retain the original study/job/policy/corpus/artifact bytes and every valid failed
or inconclusive outcome; a parsed report is not an original archive.

No native Windows/macOS execution, hosted CI, installed-prefix acceptance, complete
maximum 16 MiB report workload, maximum artifact/audio scans, maximum spectral
calculation or hostile-filesystem stress was executed by this worker. Its source
and fixture observations are engineering evidence only. Real acquisition,
reviewed physical metrology and permissions, independent holdout chronology,
listening acceptance and specimen-specific fidelity remain open.
