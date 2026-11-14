# Complete capture report replay

This is the frozen project-proposed **capture-report-replay-v1** contract,
written before its implementation and independent acceptance. It checks whether
one complete saved [job report](CAPTURE_JOB_CONTRACT.md) or
[study report](CAPTURE_STUDY.md) is reproduced by an actual new execution against
the original archive. The source basis is atlas pp. 355, 364, 484 and 486:
retain original identities, declared analysis, uncertainty, failures and the
actual code/setup. These replay fields and resource bounds are project choices.

A matching replay of a failed or inconclusive engineering result is a successful
reproduction of that result. It does not turn that result into a passing
comparison, establish historical authenticity, or establish physical fidelity.

## Public API and dependency boundary

Python 3.10 or newer, its standard library and the existing capture modules are
sufficient. The tool has no network, package-installation or acquisition step.
Its public interface is:

```python
class ReplayError(ValueError): ...

verify_report(kind: str, input_path: str | pathlib.Path,
              report_path: str | pathlib.Path) -> dict
main(argv: list[str] | None = None) -> int
```

`kind` is an exact string, either `job` or `study`. Each path is an exact nonempty
string or a `pathlib.Path` instance. Bytes, generic path-like objects and string
subclasses reject. Unicode absolute and current-directory-relative paths are
supported. `verify_report` returns a fresh complete verification summary and
never writes a file or mutates its arguments, the archive or the saved report.
Expected admission, I/O, identity, dependency, resource and publication failures
raise contextual `ReplayError`. Cancellation, including `KeyboardInterrupt`,
propagates. A rejected execution yields no partial verification summary.

The existing public `capture_job.run_job` or `capture_study.run_study` is executed
exactly once after preflight. Neither producer is changed, replaced by a cached
report, or monkey-patched for replay. Every ordinary corpus/audio/policy check,
resource bound, complete result and final snapshot check remains in force.
No threshold, role, window, gain, delay, channel or source override is offered.

## Saved report admission

The saved report is a regular nonsymlink, non-reparse file whose selected parent
is a nonsymlink/non-reparse directory. Ordinary aliases above that parent may
be canonicalized. Bounded confined reading binds the actually consumed bytes to
their digest/size and retains first pathname/parent observations until final
verification return. A directory, FIFO, socket, device or dangling link rejects.

Parse strict UTF-8 JSON with no BOM, duplicate key, trailing document, nonfinite
number, overlong numeric token or malformed Unicode. Exact built-in JSON value
types are required; direct Python object subclasses are not admitted by the
underlying guards. Generic report strings and keys may not contain U+0000..001F
or U+007F..009F. Only narrower declared fields below impose nonempty/length rules;
the report byte limit bounds other strings. Existing report semantics permit
an empty runtime `machine` string, which remains admitted.

| Saved or fresh report envelope | Inclusive limit |
| --- | ---: |
| UTF-8 bytes | 16,777,216 |
| Value nodes | 1,048,576 |
| Container depth, root depth zero | 32 for job; 40 for study |
| Finite numeric magnitude | 4e18 |
| Numeric token length | 64 characters |

The **original saved bytes must equal**
`capture_common.canonical_json_bytes(parsed_report)` exactly. A compact,
reordered, differently escaped, CRLF, extra-whitespace or missing-final-LF copy
is rejected before execution even when its parsed values would be equal.
This deliberate rule verifies a complete emitted report artifact and removes
encoding ambiguity. Retain the original report; do not normalize it in place.
The original saved-byte identity is still observed rather than inferred.

### Exact envelope and declared identities

A job report has exactly the root keys specified by the job contract:

```text
schema_version, job_contract, job_id, status, inputs, job, policy,
reference, candidate, self_comparison, corpus_report, evaluation,
runtime, tool_sources,
boundary_equivalence, synchronization, authenticity, specimen_identity,
calibration, permissions, independence, preregistration,
final_holdout_history, physical_fidelity
```

Require exact integer version 1, literal `capture-job-v1`, a valid job ID and
one of `pass`, `failed`, `inconclusive`. Validate the complete embedded `job`
through the existing `validate_job`, and require its ID to equal `job_id`.
`policy`, `reference`, `candidate`, `corpus_report` and `evaluation` are exact
objects; `self_comparison` is an exact Boolean agreeing with the embedded
reference/candidate selectors. No policy reserialization is passed to
`parse_policy`: an originally valid compact policy can exceed 64 KiB when pretty
printed. Its complete original identity is checked by the actual replay.

`inputs` has exactly `job`, `corpus`, `policy`. The job identity has exactly
`sha256` and `size_bytes`, with a lowercase 64-hex digest and exact integer size
in 1..65,536. The other two bindings have exactly `path`, `size_bytes`,
`expected_sha256`, `observed_sha256`. Their paths/digests agree with the embedded
job, expected and observed digests agree, and integer sizes are 1..1,048,576 for
corpus and 1..65,536 for policy. The corpus object must declare
`mode: files_and_audio_checked`, its `index_sha256` must equal that binding,
and its status is one of the three engineering statuses. The evaluation's
`policy_sha256` must equal its binding, its `evaluation_role` must be one of
`fit`, `validation`, `final_test`, `unassigned`, and its `numerical_verdict`
must be `pass`, `fail` or `inconclusive`. The job status must agree with the
unchanged failure/inconclusive precedence over those two declared outcomes.

A study report has exactly the root keys specified by the study contract:

```text
schema_version, study_contract, study_id, status, input, study, corpus,
work, summary, jobs, runtime, tool_sources,
boundary_equivalence, synchronization, authenticity, specimen_identity,
calibration, permissions, independence, preregistration,
final_holdout_history, physical_fidelity
```

Require exact integer version 1, literal `capture-study-v1`, a valid matching
study ID, a valid engineering status, and the complete embedded study admitted
by `validate_study`. `input` has exactly `sha256` and `size_bytes` with the same
65,536-byte rule. `corpus` has exactly `expected_sha256` and `observed_sha256`,
both equal to the embedded study's declared corpus hash. `work` has exactly
`window_samples` and `spectral_terms`, exact integers in the study's existing
bounds; recompute both sums from the nested jobs' embedded analyses.

`jobs` is an exact list matching the embedded study's 1..8 ordered entries.
Each element has exactly `job_id`, `path`, `expected_sha256`, `observed_sha256`,
`size_bytes`, `report`. Its ID/path/expected hash match the corresponding entry;
its observed hash and integer size match its nested job's `inputs.job` and the
expected digest. Admit each complete nested job envelope under the job rules
above. Its corpus binding matches the common study hash, and its source/runtime
observations agree with the corresponding study observations. `summary` has
exactly `jobs`, `pass`, `failed`, `inconclusive`, `roles`; the four role keys are
`fit`, `validation`, `final_test`, `unassigned`. Recompute exact integer counts
from the ordered nested statuses/evaluation roles, and enforce the ordinary
failed-before-inconclusive-before-pass study status.

In every job/study envelope, all ten listed claim fields must literally equal
`not_established`. `runtime` has exactly `python_implementation`,
`python_version`, `sys_platform`, `machine`, each exact string at most 128
characters without forbidden controls; only `machine` may be empty. Each source
record has exactly `module`, `size_bytes`, `sha256`, with an exact integer size
in 1..1,048,576 and a lowercase 64-hex digest. Job sources are exactly the sorted
six filenames `capture_audio.py`, `capture_common.py`, `capture_corpus.py`,
`capture_job.py`, `compare_capture.py`, `validate_capture.py`. A study has those
same six plus `capture_study.py`, also sorted. Unknown/duplicate/missing source
records reject rather than becoming an inferred version difference.

This is **strict envelope admission**, not independent recertification of all
nested corpus/metric facts. Other bounded nested contents remain complete,
unprojected data for comparison. Their presence or a claimed status is never
sufficient for replay success. No saved policy, manifest, numerical metric,
source digest or runtime string is treated as authenticated history. Actual
execution and comparison of every canonical byte are the decisive checks.

## Ordered execution and identities

1. Validate the API kind/path types. Read, hash, parse and admit the one saved
   canonical report with the above exact envelope rules.
2. Observe each actual associated runtime-tool source (six for job; seven for
   study) and `verify_capture_report.py`, each a bounded regular source file of
   at most 1 MiB. Retain their first snapshots through final return. Observe
   the current four-field runtime without hostname, timestamp or elapsed time.
3. Read the actual input file once under its ordinary 64 KiB, 4,096-node,
   depth-8, magnitude-1e12 rules; validate it with the public input validator.
   Bind its consumed byte hash, size, ID and complete parsed value to the saved
   report's declared original input. Reject a mismatch **before calling the
   job/study runner** and before its artifact work. Retain this first input
   observation until final return.
4. Call the ordinary public runner exactly once. It independently reads the
   original input again and performs all its declared work. Admit the fresh
   report under the same complete envelope and bounds; require its consumed
   input identity and embedded value to equal preflight. Require its source
   observations to equal the separately observed current associated source
   files, and its runtime to equal the observed current runtime.
5. Serialize the complete fresh report canonically and compare its **entire
   byte sequence** with the original admitted saved bytes. SHA-256 values in
   the summary identify each byte sequence; equality is not decided by a
   stored digest, status, selected metric or caller-supplied Boolean.
6. Form the bounded summary below. Verify every replay-owned saved-report,
   original-input and source snapshot, and require the current runtime to
   remain unchanged. Return only after all checks finish.

Public runners own and verify their complete archive snapshots through their
own return. Replay retains its saved report, original input and sources through
its later final return. It does not extend public-runner artifact snapshots or
claim an atomic multi-file transaction. Another writer can change the input
between replay preflight and the public runner's first read; the consumed-input
comparison and final snapshots reject the observed race, but bounded artifact
work may already have occurred. The ordinary job/study caps still govern that
work. No claim is made that every concurrent change rejects before artifact
processing, nor that deliberately restored changes are detected. Keep archives,
reports and coherent installed sources quiescent during the whole operation.

The replay's own snapshot set contains at most ten selected roots/leaves: saved
report, original input, up to seven associated tool sources and its own source.
It checks a defensive inclusive cap of twelve for each before appending. The
public runner's separate snapshot set retains its existing limits. There is no
recursive replay, retry, cache, dynamic source loading or inferred path from a
saved report; only the explicitly supplied original input is executed.

A source/runtime difference between saved and fresh reports is observable
context. It does not establish corruption, identify the cause of a numeric
difference or prove the saved identities were truthful. If the current archive
is rejected by its producer, replay rejects rather than fabricating a mismatch
summary from an incomplete execution. A changed input identity rejects at
preflight; source/runtime-only differences may produce a completed mismatch.

## Exact verification summary

Every returned summary has exactly these keys:

| Key | Required value |
| --- | --- |
| `schema_version` | Exact integer 1. |
| `replay_contract` | `capture-report-replay-v1`. |
| `kind` | Explicit `job` or `study`. |
| `status` | `match` when the full byte sequences agree, otherwise `mismatch`. |
| `verification_scope` | `complete_canonical_report_bytes`. |
| `exact_report_match` | Exact Boolean corresponding to `status`. |
| `input` | Original actual input observation: exactly `sha256`, `size_bytes`. |
| `saved_report` | Original consumed saved-byte observation: exactly `sha256`, `size_bytes`. |
| `replayed_report` | Fresh complete canonical-byte observation: exactly `sha256`, `size_bytes`. |
| `saved_engineering_status` | The admitted saved envelope's underlying `pass`, `failed` or `inconclusive`. |
| `replayed_engineering_status` | The actual replay's underlying engineering status. |
| `context` | Exact object described below. |
| `verifier_source` | Actual `verify_capture_report.py` observation: exactly `module`, `sha256`, `size_bytes`. |
| `verifier_runtime` | Current actual four-field runtime. |
| The ten job/study claim fields | Every value remains `not_established`. |

`context` has exactly `same_runtime`, `same_tool_sources`, `saved_runtime`,
`replayed_runtime`, `saved_tool_sources`, `replayed_tool_sources`. The first two
are exact equality Booleans; the other four retain the complete admitted source
and runtime envelopes from the saved/fresh reports. Both equalities can be true
while other report bytes differ. Neither context flag overrides a full mismatch.
There is no projected-result-only comparison, a report copy hidden in a field,
absolute path, timestamp, hostname, elapsed time or unbounded mismatch list.

The summary is limited to 65,536 canonical bytes, 8,192 value nodes, depth 12 and
finite magnitude 4e18. It retains no mutable aliases to caller data. Exact source
identity makes a verifier source edit observable in its next summary; no source
observation authenticates the already loaded memory or supplies a signature.

## CLI and failure-preserving publication

From the repository root, or using an absolute script path:

```sh
python3 tools/verify_capture_report.py --kind job --input /archive/job.json --report /reports/job-report.json
python3 tools/verify_capture_report.py --kind study --input /archive/study.json --report /reports/study-report.json --output /existing/new-verification.json
```

Only required `--kind`, `--input`, `--report`, optional `--output` and help exist.
Each value option may occur once only. Empty, duplicate, abbreviated and unknown
options reject. `main` accepts only `None` or an exact list of exact strings,
and returns an integer rather than leaking normal parser `SystemExit`.

| Exit | Result |
| ---: | --- |
| 0 | Complete `match` summary, or help. A matched underlying failed/inconclusive result remains failed/inconclusive in the summary. |
| 1 | Complete `mismatch` summary with empty stderr; or rejected input, execution or publication with no summary and contextual `replay error: ...` stderr. |
| 2 | Usage error, no summary and a usage diagnostic. |

There is no replay exit 3: underlying inconclusive is preserved explicitly,
while replay itself has match/mismatch or rejected-input semantics. Normal
stdout is exact canonical sorted-key two-space UTF-8 JSON plus one final LF.
Real streams use their binary buffer regardless of terminal encoding/newline
translation; text-only redirected streams receive equivalent Unicode text.
No progress message is mixed into JSON.

Optional output uses `capture_common.write_json_new` after the whole bounded
summary is ready and **before stdout**. Its parent must exist and support hard
links. Existing files, directories, symlinks, inputs and raced destinations are
preserved; no directories are created. File bytes equal stdout. The helper's
explicit disclosure of a completed publication followed by cleanup failure is
preserved, and the complete new file is not removed. Stdout failure can leave
partial delivered bytes and a complete published file; return nonzero and
identify stdout delivery failure. Failure of stderr may prevent another
diagnostic but never changes failure into success. Cancellation propagates.

## Independent acceptance and continuation

Independent acceptance should first derive envelope, identity, outcome and
canonical-byte expectations from the existing job/study contracts. Exercise
matching pass/failed/inconclusive jobs and a mixed-result study, unchanged
relocation, changed saved metrics/status/source/runtime, malformed and
noncanonical reports, original input mismatch before runner entry, current
source/input/report changes around execution, late runner-consumed input
identity mismatch, full byte comparison, resource rejection, strict CLI,
Unicode/foreign-directory use, no-clobber output and partial-publication errors.
Use temporary source copies for mutation cases. Retain concrete initial failures
and corrected harness assumptions; do not erase a failed source revision.

Successful replay is current software reproducibility evidence. It does not
prove when the saved report or threshold was created, who acquired audio,
physical channel equivalence, metrology, permission, independence, untouched
holdout use, listening acceptance or specimen-specific fidelity. Future source,
input or environment changes require an explicit new execution and retained
comparison; an old exact hash does not qualify changed code.
