# Fixed capture comparison studies v1

`tools/capture_study.py` executes a bounded, declared collection of
[capture jobs](CAPTURE_JOB_CONTRACT.md) against one exact corpus-index identity.
It retains every complete job result, including failures and inconclusive
outcomes. It does not fit a model, adjust a policy, acquire audio, apply a
correction or establish that any physical protocol is complete.

This is the **frozen project-proposed `capture-study-v1` contract**, written
before its implementation and independent acceptance. Its engineering choices
extend the [calibration scope](CALIBRATION_SCOPE.md), without changing capture
v1, the corpus, policy or public job contract. The source requirements are atlas
pp. 355, 364, 484 and 486: preserve original evidence boundaries, retain declared
analysis and uncertainty, keep failures, and identify the actual inputs and code.
The atlas does not prescribe these API names, fields or resource limits.

## Public API and exact input

Python 3.10 or newer and the existing standard-library-only capture modules are
sufficient. The public interface is:

```python
class StudyError(ValueError): ...

validate_study(value: object) -> None
load_study(path: str | pathlib.Path) -> dict
run_study(path: str | pathlib.Path) -> dict
main(argv: list[str] | None = None) -> int
```

`validate_study` checks exact values, shape, limits and entry uniqueness without
I/O or mutation. `load_study` reads one bounded strict JSON file, validates it,
and returns its parsed value unchanged; it does not read any declared job.
`run_study` performs the procedure below and returns a fresh complete report.
It never writes a file or changes an input. The expected admission, filesystem,
dependency, identity, output and resource failures become contextual
`StudyError`. Cancellation, including `KeyboardInterrupt`, propagates.

Every listed key is required and no additional key is admitted. The zero
digests here illustrate shape only; this is not a runnable acquired archive.

```json
{
  "schema_version": 1,
  "contract_origin": "project-proposed-capture-study-v1",
  "study_id": "fixed-validation-v1",
  "corpus_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
  "jobs": [
    {
      "job_id": "literal-offset-v1",
      "path": "jobs/offset.json",
      "sha256": "0000000000000000000000000000000000000000000000000000000000000000"
    }
  ]
}
```

| Field | Exact rule |
| --- | --- |
| Root | Exactly `schema_version`, `contract_origin`, `study_id`, `corpus_sha256`, `jobs`. |
| Version/origin | Exact integer `1` and literal `project-proposed-capture-study-v1`. |
| `study_id` | ID matching `[a-z][a-z0-9_-]{0,63}`. |
| `corpus_sha256` | Exactly 64 lowercase hexadecimal characters; expected original corpus-index bytes. |
| `jobs` | Exact list of 1..8 entries, retaining declared order. |
| Job entry | Exactly `job_id`, `path`, `sha256`; ID, portable relative path and exact lowercase digest. |

Job IDs, case-folded job paths and job digests must each be unique across the
study. An entry's `job_id` must equal the ID in its actually consumed job.
Every consumed job's `corpus.sha256` must equal `study.corpus_sha256`.
Different job-relative locators may reach copies of the same bound corpus;
each is independently checked by its ordinary full job audit. Equal hashes are
content identities, not proof of independent recordings or acquisition history.

Objects/lists/strings/numbers use exact built-in JSON/Python types. Reject
subclasses, tuples, Boolean substitutes for integers, cycles, nonfinite values,
unknown fields, duplicate JSON keys, BOM, invalid UTF-8, trailing documents,
unpaired surrogates and U+0000..U+001F/U+007F..U+009F in any string or key.
Generic strings are nonblank and at most 2,048 characters before narrower field
limits. Numeric tokens are at most 64 characters and finite magnitude `1e12`.

Input API paths are exact nonempty strings or `pathlib.Path` instances, not
bytes, generic path-like objects or string subclasses. Unicode absolute or
current-directory-relative input paths are allowed. The selected study leaf
must be a regular nonsymlink, non-reparse file. Its parent is the study root,
itself a nonsymlink/non-reparse directory. Ordinary aliases above that root may
be canonicalized. Every declared descendant directory and job leaf is separately
confined and admitted. Job paths are relative to the study root; subsequent job,
corpus and manifest roots retain their own contracts.

Declared paths have at most 240 ASCII characters and eight slash-separated
components, each 1..64 characters, beginning with an ASCII alphanumeric and then
containing ASCII alphanumerics, `.`, `_` or `-`. Reject traversal, absolute/drive/
UNC/backslash/colon forms, empty components, trailing dots and Windows device
stems, including before an extension. The [shape schema](../data/capture-study.schema.json)
does not replace strict bytes, exact numeric types, cross-file identities or the
semantic execution checks.

## Admission, work and immutable execution

Use this order:

1. Admit/read/hash the study file once and validate exactly its parsed bytes.
   Observe the actual regular `capture_study.py` source file under a 1 MiB bound.
   Keep both first-admission snapshots until final return.
2. Read **every declared job file** under the already admitted study root,
   using each complete study-relative path. Match its exact consumed-byte SHA
   before accepting its parsed value. Apply the unchanged job validator, require
   its declared job ID and corpus digest to match the study, and sum the work
   below. Every job header and cumulative declared work must be admitted before
   the first artifact is opened, hashed or decoded. Preflight reads do not select
   separate job roots, avoiding duplicate root bookkeeping.
3. Execute jobs sequentially in their declared order, through one private
   bound-job entry point sharing the public job implementation. On its second
   and final job-file read, require the actual parsed-byte hash to equal the
   study's expected hash **immediately after job admission and before reading
   its corpus or policy**. The public `run_job(path)` signature and exact report
   remain unchanged. A final post-hoc report hash check alone is insufficient.
4. Each job independently performs its existing policy/manifest preflight,
   one fresh full-corpus byte/audio audit and its two selected window inspections.
   No previous artifact observation is substituted for this actual execution.
   Each job keeps its existing per-job bounds and whole-corpus findings. It may
   use a different policy, geometry, selected purpose or pair from another job.
   No study-level threshold, analysis, role or transform override exists.
5. Retain the full completed job report unchanged. Require its observed job and
   corpus identities to match preflight and the common expected corpus hash.
   Runtime identity and all six source observations must be identical across
   jobs. Retain valid failed and inconclusive reports and continue to subsequent
   jobs; there is no early numerical-success or numerical-failure exit.
6. After each added full job report, check the growing report envelope below.
   On overflow, reject without truncating any nested report or publishing a
   partial study. After the last job, form the complete report, validate it, and
   recheck the **entire shared snapshot set**, including every earlier job's
   inputs and sources. Only then return.

Step 2 admits all **job files**, not all their external policy/manifest data at
once. Step 4 admits each job's dependencies before that job's artifact work.
A later dependency rejection can therefore follow earlier computation, but no
study report is returned or published. That is an input-error outcome, distinct
from complete numerical failure/inconclusive results. This tool does not mutate
the archive or publish one report per completed job implicitly.

The private job core receives the study's shared snapshot object. It retains
the study file, first job-header observations, each actual job read, each index,
policy, every manifest, **every audited artifact**, confined parent chains and
all six job sources across all executions. The study source is added separately.
Earlier observations are never replaced by a later observation of the same path.
Final checks compare leaf type, usable identity, size, modification/change times
through the same filesystem API, and parent type/identity without directory
timestamps. Constituent reads preserve their descriptor and local checks too.
Unrelated sibling creation does not invalidate a directory merely by changing
its timestamp. These checks require quiescent input/source files; they are not
a hostile concurrent-filesystem sandbox, code signature or memory attestation.

| Resource | Inclusive limit or explicit composition bound |
| --- | ---: |
| Study JSON bytes / value nodes / container depth | 65,536 / 4,096 / 8, root depth zero |
| Generic study container members / string characters | 4,096 / 2,048, before tighter shape limits |
| Jobs / reads of each job file | 8 / two: study preflight and bound execution |
| One job JSON | 65,536 bytes and its unchanged job limits |
| Total selected window work, `sum(C*N)` over jobs | 8,388,608 |
| Total selected spectral work, `sum(C*N*K)` over jobs | 33,554,432 |
| Shared retained leaf snapshots / selected-root records | 3,000 / 64 |
| Each observed source file | 1,048,576 bytes |
| Canonical study report bytes / value nodes / container depth | 16,777,216 / 1,048,576 / 40 |
| Study report numeric magnitude | `4e18`, with stricter nested job/comparison bounds unchanged |

`C*N` counts one side's selected channel/frame geometry; two sample arrays are
compared by each job. `C*N*K` uses the same one-side work convention as the
comparison contract. An empty frequency list contributes zero spectral terms.
Both totals are exact integer sums of all preflighted job declarations; they
are checked before artifact work and are not rounded, truncated or inferred
from a returned report. Each individual job still satisfies its own geometry,
window-duration and spectral limits. Checking an aggregate after running an
unbound changed job would not enforce this contract.

With eight jobs, the existing per-job declarations permit at most **16 GiB**
aggregate artifact-reference bytes and **2 GiB** aggregate corpus selected-audio
reference bytes, counting repeated work. There are at most **16 additional
selected-window inspections**, each under the audio tool's per-file limits.
These are conservative composition bounds, not allocations, unique-byte totals,
measured workloads, wall-clock promises or a claim that all maxima can occur
together. No caching or deduplication is credited toward these limits.

The ordinary snapshot-count upper bound is **2,642 leaves**: study/source (2),
upfront job files (8), and eight jobs each with six sources, one job, one index,
one policy, at most 64 manifests and at most 256 artifacts:
`2 + 8 + 8*(6+1+1+1+64+256) = 2642`. Each snapshot retains its confined parent
chain. The root bound is **58**: study and study-source roots (2), plus eight
jobs each selecting its job root and six source roots, `2 + 8*7 = 58`.
Preflight reads under the already selected study root add no root record.
Hard caps are checked before appending; no retained observation is discarded to
stay under a cap. These assertions also detect unexpected dependency growth.

Each individual job report is already bounded. The study checks its growing
envelope after each job, so it never retains eight unchecked maximum reports.
The incoming bounded job and the preceding bounded study can coexist during
that check. An oversized combined result is an explicit error, not a partial
or passing study. There is no unbounded retry, recursive job/study inclusion,
plugin loading, expression evaluation, network access or hidden file output.

## Exact report and outcome

Every returned report has exactly these root keys:

| Key | Required content |
| --- | --- |
| `schema_version` | Exact integer `1`. |
| `study_contract` | Literal `capture-study-v1`. |
| `study_id` | Same ID as the consumed study. |
| `status` | `pass`, `failed` or `inconclusive` by the precedence below. |
| `input` | Exactly `sha256`, `size_bytes`, observed from the original consumed study bytes. |
| `study` | Complete parsed study, retained unchanged without mutable input aliasing. |
| `corpus` | Exactly `expected_sha256`, `observed_sha256`; expected is the study declaration, observed is the actual common index hash in every full job report. They must match. |
| `work` | Exactly `window_samples` and `spectral_terms`, the preflight integer sums defined above. |
| `summary` | Exact counts described below. |
| `jobs` | Complete ordered job-entry result objects described below. |
| `runtime` | The exact common four-field runtime object from every actual job report. |
| `tool_sources` | Seven actual source observations, sorted by `module`. |
| `boundary_equivalence`, `synchronization`, `authenticity`, `specimen_identity`, `calibration`, `permissions`, `independence`, `preregistration`, `final_holdout_history`, `physical_fidelity` | Each literal `not_established`. |

`summary` has exactly `jobs`, `pass`, `failed`, `inconclusive`, `roles`.
The first four are nonnegative integer counts; the three status counts sum to
`jobs`, the number of complete retained results. `roles` has exactly `fit`,
`validation`, `final_test`, `unassigned`, with each integer count taken from the
actual nested evaluation's `evaluation_role`. All four keys remain present,
including zero counts; they also sum to `summary.jobs`.

Every `jobs` element has exactly:

```text
job_id, path, expected_sha256, observed_sha256, size_bytes, report
```

The first three values come from the unchanged entry. Observed hash/size come
from the actual bound job bytes in `report.inputs.job`, and must agree with the
first preflight read. `report` is the entire returned `capture-job-v1` report,
without projection, status rewriting, omitted failures or reserialized original
policy bytes. Raw and derivative selection contexts remain unchanged. Samples
are absent because ordinary job reports do not serialize them. Declared job
order is retained even if the IDs would sort differently.

`runtime` retains `python_implementation`, `python_version`, `sys_platform` and
`machine` exactly as the actual job runtime. The seven source records each have
exactly `module`, `size_bytes`, `sha256`: the six unchanged job source names
(`capture_audio.py`, `capture_common.py`, `capture_corpus.py`, `capture_job.py`,
`compare_capture.py`, `validate_capture.py`) plus `capture_study.py`.
Each nested job still lists exactly its six sources. The study's own source
identity comes from its observed regular file, not a caller declaration.
Source and runtime disagreement across jobs rejects instead of silently choosing
one version. No hostname, timestamp, absolute path, output pathname or elapsed
time is inserted. No source observation authenticates patched process memory.

The study is `failed` if any job is `failed`; otherwise it is `inconclusive` if
any job is `inconclusive`; otherwise it is `pass`. Every job is retained in a
returned report, including inconclusive neighbors beside a failure. Role counts
do not change this precedence. **An all-fit study, a study with no final-test
job, or any other incomplete physical-protocol role set can pass its requested
engineering checks.** No required-role policy is inferred. Such a pass does not
complete calibration, prove independence or establish untouched final-test use.
Each numerical policy continues to claim only its listed criteria.

Repeated execution and relocation of an unchanged complete archive under the
same source/runtime identities produce equal report values and canonical bytes.
Input whitespace changes its exact identity. Different Python/platform math may
change final numerical bits; universal cross-platform byte identity is not
promised. Retain original study/job/index/manifests/policies/artifact bytes and
the source context for replay. Parsed report copies cannot reconstruct their
original whitespace or prove when a threshold was chosen.

## Command line and publication

Run from the repository root or use an absolute script path from another working
directory:

```sh
python3 tools/capture_study.py --input /path/to/archive/study.json
python3 tools/capture_study.py --input /path/to/archive/study.json --output /existing/directory/new-study-report.json
```

Only required `--input`, optional `--output`, and `-h`/`--help` exist. Unknown or
abbreviated options reject. An input/output option may occur at most once;
empty option values reject as usage. `main` accepts only `None` or an exact list
of exact strings and returns an integer; it does not leak normal parser
`SystemExit`. No argument overrides an analysis, role, bound, correction or hash.

| Exit | Meaning and output |
| ---: | --- |
| 0 | Complete `pass` report, or help requested. |
| 1 | Complete `failed` report with empty stderr; or rejected input/publication with no report and one contextual `study error: ...` stderr line. |
| 2 | CLI usage error with no report and a usage diagnostic. |
| 3 | Complete `inconclusive` report with empty stderr. |

Normal stdout is exactly canonical sorted-key, two-space-indented UTF-8 JSON,
`ensure_ascii=False`, finite numbers and one final LF. Real standard streams
receive UTF-8 bytes independently of terminal text encoding; redirected
text-only streams receive the same Unicode text. Progress never mixes into JSON.

With `--output`, the complete bounded report is published using
`capture_common.write_json_new` **before** stdout. Its parent must already exist
and support hard links. No directory is created and no existing file, directory,
symlink, input alias or concurrently created destination is replaced. File bytes
equal normal stdout. Failed/inconclusive reports use the same publication rules.
Preserve the helper's explicit disclosure if a complete new report is published
but temporary cleanup fails; never delete that complete report to disguise the
outcome. An ordinary rejection before stdout leaves stdout empty. An actual
stdout failure may leave partial delivered bytes and a complete published file;
return failure, retain the file and identify stdout delivery as the failure.
If stderr itself fails, another diagnostic cannot be promised; return nonzero.
Cancellation is not translated into an ordinary successful/rejected result.

## Independent acceptance and continuation

Independent acceptance must calculate expected identities, work/counts and
outcomes separately from this producer. Include one and eight actual jobs,
all status combinations and declared order, original-byte changes, strict
schema/API cases, shared-corpus/ID mismatches, all-job preflight before a trapped
artifact reader, a bound job changed between reads, cumulative work limits,
source/runtime consistency, shared snapshots for earlier unselected artifacts,
metadata and source changes, relocation, output preservation and resource/error
precedence. Source mutation fixtures use temporary copied sources rather than
editing the production checkout. Literal offset examples from the job contract
supply a numerical oracle without inventing hardware data.

The schema provides exact shape and local field limits, but cannot establish
strict original bytes, integer token types, unique IDs/paths/digests by field,
cross-file binding, work products, filesystem confinement, actual audio,
chronology or physical evidence. Existing corpus/job/metric contracts remain
authoritative. Shared-correction fitting, physical unit conversion, actual
acquisition, reviewed metrology, listening acceptance and specimen-specific
fidelity remain later gates.
