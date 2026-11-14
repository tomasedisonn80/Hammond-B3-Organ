# Declared capture comparison jobs

`tools/capture_job.py` runs a complete corpus audit and compares two explicitly
selected audio windows under an identity-bound policy. It preserves the complete
corpus, numerical and uncertainty results in one report. Every input remains
unchanged. A successful engineering result does not establish a physical match.

The exact interface, input/report fields, admission order and resource limits
are defined by [capture-job-v1](CAPTURE_JOB_CONTRACT.md), independently reviewed
in [CAPTURE_JOB_REVIEW.md](CAPTURE_JOB_REVIEW.md). The
[implementation record](development/2026-11-13-calibration/25-file-job-implementation.md)
identifies its source, author checks and independent-acceptance handoff.

## Setup and commands

Use Python 3.10 or newer and keep these six project files together in `tools/`:
`capture_job.py`, `capture_corpus.py`, `capture_audio.py`, `capture_common.py`,
`compare_capture.py` and `validate_capture.py`. The job has no third-party or
network dependency. Run from the repository root:

```sh
python3 tools/capture_job.py --input /path/to/archive/job.json
python3 tools/capture_job.py --input /path/to/archive/job.json --output /existing/directory/new-report.json
```

An absolute script path works from another working directory. Unicode archive
root names are allowed. Paths *declared inside* JSON use the narrower portable
relative-path grammar in the contract. Keep the input archive and project sources
quiescent during a run.

`--output` publishes a complete new report in an existing directory. It never
creates directories or replaces an existing file, directory, symlink or a
destination created concurrently. The output file and normal stdout contain the
same canonical UTF-8 bytes: sorted keys, two-space indentation and one final LF.
The output location does not change report identity. No analysis, gain, delay,
sample-rate, purpose or hash override exists on the command line.

| Exit | Meaning | Stdout |
| --- | --- | --- |
| `0` | Completed engineering pass. | Complete JSON report. |
| `1` | Completed failed corpus/policy outcome. | Complete JSON report; stderr empty. |
| `1` | Rejected input, observed change, dependency or publication failure. | Empty before output begins; contextual `job error: ...` on stderr. |
| `2` | Invalid command-line usage, including unknown/abbreviated options. | Empty; usage diagnostic on stderr. |
| `3` | Completed inconclusive corpus/policy outcome. | Complete JSON report. |

`--help` exits zero. Normal completed reports have empty stderr. Retain failed
and inconclusive reports as evidence. If publication succeeds but temporary-file
cleanup fails, the complete published file remains and the error explains that
state. A later stdout I/O failure can also leave a complete published file; an
output stream cannot be made atomic with file publication.

## Prepare the archive

Start with complete [capture v1 manifests](CAPTURE_FORMAT.md), their actual
artifacts and a [corpus companion](CAPTURE_CORPUS.md). Preserve the original
bytes, ancestry, recorded/planned status, synthetic/hardware declaration and
unknown physical values. Use a [fixed policy](CAPTURE_POLICY.md) whose analysis
and role describe the intended comparison. The job schema is available at
[`data/capture-job.schema.json`](../data/capture-job.schema.json); runtime
validation supplies the semantic checks a shape schema cannot establish.

The job has ten required fields: `schema_version`, `contract_origin`, `job_id`,
`corpus`, `reference`, `candidate`, `analysis`, `policy`, `pairing`, `transform`.
The complete shape example is in the contract. Its illustrative zero digests
must be replaced with hashes of actual files; the example is not an acquired
archive. These relationships determine the archive:

| Declaration | Meaning |
| --- | --- |
| `corpus.path`, `policy.path` | Paths relative to the job file's parent. Each associated SHA-256 binds that file's exact bytes. |
| Corpus `manifest_path` | Path relative to the corpus index's parent. Its expected digest binds the exact parsed v1 manifest. |
| Manifest artifact `path` | Path relative to that manifest's parent, preserving raw/derived/support ancestry. |
| Each selection | A corpus capture ID, one raw or explicitly described derived file ID, and the original start frame. |
| `analysis` | The common sample rate, all-channel count, frame count, window, floor and ordered frequencies; all six agree with the policy. |
| `pairing`, `transform` | Exactly `index` and `none`. No fitted correction or channel remapping occurs. |

Compute expected SHA-256 values from the actual file bytes, for example:

```sh
python3 -c 'import hashlib,pathlib,sys; p=pathlib.Path(sys.argv[1]); print(hashlib.sha256(p.read_bytes()).hexdigest())' /path/to/archive/policy.json
```

Changing JSON whitespace changes its byte identity even when parsed values are
equal. Freeze and retain original job, policy, index and manifest files together
with the audio. A parsed report copy cannot recover their original whitespace.

Both selected captures must be recorded and use the same corpus purpose.
The policy role is `fit`, `validation`, `final_test` or `unassigned` for corpus
purpose `fit`, `validation`, `final` or `unassigned`, respectively. A synthetic
numerical policy requires both selected capture kinds to be synthetic. A digital
comparison policy may use hardware declarations under its own uncertainty rules,
without authenticating those declarations. Both-unassigned selection remains
inconclusive through the corpus audit.

## Execution and retained evidence

The job consumes each top-level input and each manifest once, retaining the
actual bytes' identities and parsed metadata. It checks the policy, capture and
reference limits, selected roles, evidence class and declared geometry before
opening artifacts. It then invokes the same private audit core as the public
corpus auditor. This core performs fresh byte checks for **every** declared
artifact and complete inspection of every declared audio stream. An unrelated
support file, leaking fit capture or planned record therefore remains relevant
to the outcome.

After the full audit, each selected window receives a complete audio inspection.
The selected inspection must match the corpus's actual byte size, byte hash,
format, rate, channel count, frame count and canonical decoded identity. Every
sample outside the requested interval is still checked. A hidden NaN or malformed
trailing payload cannot be made acceptable by selecting an earlier window.

The comparison receives the original channel-major samples, every channel in
index order, and the exact two half-open intervals. There is no gain correction,
normalization, alignment search, resampling, padding or truncation. The policy
evaluator receives the original admitted policy **bytes**, preserving its hash
and byte bound; formatting a parsed policy again can exceed that bound.

The report includes the complete job, policy, corpus report and policy evaluation,
including all comparison metrics and masked bins. Each side retains its complete
bound v1 manifest and full-stream audio inspection, with only the machine-specific
`input_path` field removed. Sample arrays are not serialized.

For a raw selection, `context_scope` is `selected_raw_stream`. For a derivative,
it is `ancestor_raw_stream_only`: the manifest's raw channel, calibration and
clock metadata are preserved as ancestor context. The derivative's own descriptor
and inspected file establish its digital geometry. Raw physical context is never
promoted into verified derivative calibration. Exact self-comparison is marked
explicitly and is not independent evidence.

The overall result is failed if the full corpus fails or any numerical criterion
fails. Otherwise any inconclusive constituent makes the job inconclusive; only
two passing constituents produce pass. Both complete subordinate outcomes remain
available even when one determines the top-level result.

Ten claim fields always remain `not_established`: boundary equivalence,
synchronization, authenticity, specimen identity, calibration, permissions,
independence, preregistration, final holdout history and physical fidelity.
Unknown physical quantities remain unknown. A policy hash does not prove when
the policy was chosen or whether final-test data was previously inspected.

## Bounds and filesystem checks

| Resource | Inclusive limit |
| --- | ---: |
| Job JSON bytes / value nodes / container depth | 65,536 / 4,096 / 8 |
| Corpus captures in a job | 64 |
| Artifact references, including repeated references and support files | 256 |
| Aggregate declared artifact/audio bytes | 2 GiB / 256 MiB |
| Common selected window | 262,144 frames, 1,048,576 channel samples, 600 seconds |
| Selected frequencies / channel-frame-frequency work | 64 / 16,777,216 |
| Actual corpus graph edges | 4,096 |
| Each of six project source files | 1 MiB |
| Canonical report bytes / value nodes / depth | 16 MiB / 1,048,576 / 32 |

All constituent corpus, v1, policy, metric and audio limits continue to apply.
Job inputs use exact built-in JSON types, finite values and strict UTF-8, rejecting
duplicate keys, nonfinite numbers, controls and unpaired surrogates. Excess report
size, depth, nodes or magnitude causes rejection; observations are never truncated
to manufacture a report.

The job parent, each confined descendant directory and every input leaf are
checked independently against symlinks/reparse points and inappropriate types.
Ordinary OS aliases above the selected root may be canonicalized. Existing
corpus descriptor-identity and within-manifest hardlink checks remain active.
First-admission snapshots cover the job, index, policy, every manifest, every
audited artifact and all six project sources. Final checks compare each leaf's
identity, type, size and modification/change times, and each parent directory's
type and identity. Sibling activity does not fail a run merely by changing a
directory timestamp.

These portable observations require quiescent files. They are not a hostile
filesystem sandbox, cryptographic code signature or loaded-memory attestation.
Cancellation propagates instead of returning a successful partial report.

## Python API and replay

Add the project `tools` directory to the importing application's module path,
then use:

```python
from capture_job import JobError, load_job, run_job, validate_job

job = load_job("/path/to/archive/job.json")
validate_job(job)  # Exact value/shape/work admission; no filesystem operations.
report = run_job("/path/to/archive/job.json")  # Reads only; never publishes.
```

`JobError` represents rejected input, identity, dependency or resource checks.
A report whose status is `failed` or `inconclusive` is a completed result rather
than an exception. `main(argv)` is the CLI entry point and returns its exit code.

Each report records Python implementation/version, platform token and machine
string, plus the actual size/SHA-256 of the six source files. No host name,
timestamp, output path or elapsed time enters report identity. Repeated runs and
relocation of an unchanged archive under the same runtime/source identities
produce the same canonical bytes. Other Python/platform math environments may
change final numerical bits; cross-platform byte identity is not promised.

Preserve failures and source identities when continuing development. Assignment
26 independently accepts actual job archives and the CLI; later study/replay and
clean-install work can build on those observed results. Acquisition chronology,
physical fitting, listening results and specimen-specific fidelity remain
separate gates under [CALIBRATION_SCOPE.md](CALIBRATION_SCOPE.md).
