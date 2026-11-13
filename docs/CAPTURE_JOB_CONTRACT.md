# Declared capture comparison job contract v1

**Frozen implementation target:** `capture-job-v1`, 2026-11-13. This proposed
offline wrapper composes the [audio](CAPTURE_AUDIO_CONTRACT.md),
[corpus](CAPTURE_CORPUS_CONTRACT.md) and
[comparison/policy](CAPTURE_COMPARISON_CONTRACT.md) contracts. It does not replace
their definitions or change [capture metadata v1](CAPTURE_FORMAT.md). A contract,
schema or illustrative example is not an executed acceptance result.

The source requirements are atlas pp. 355, 364, 367-372, 484 and 486: preserve
original identities and measurement boundaries, declare analysis before grading,
retain failures and uncertainty, and identify the code/data/setup of a result.
These API names, fields and limits are project decisions. This first job version
fixes `transform: "none"`; calibrated nuisance corrections and physical fitting
remain separate work under [the calibration scope](CALIBRATION_SCOPE.md).

## 1. Public interface and purpose

The implementation target is `tools/capture_job.py`, with Python 3.10+ standard
library dependencies and the existing project modules:

```python
class JobError(ValueError): ...

validate_job(value: object) -> None
load_job(path: str | pathlib.Path) -> dict
run_job(path: str | pathlib.Path) -> dict
main(argv: list[str] | None = None) -> int
```

`validate_job` checks exact shape, types, paths, intrinsic limits and analysis
work without I/O or mutation. `load_job` reads one bounded strict JSON document,
validates it and returns its unmodified parsed value. `run_job` performs the
complete procedure below and returns a new report, including valid failed or
inconclusive outcomes. It does not write a file, alter an input, acquire audio,
fit a parameter, contact a network or cache decoded samples on disk.

The comparison module additionally exposes
`parse_policy(policy_json: bytes) -> dict`. This additive helper performs all
intrinsic strict policy parsing, shape, geometry, target, unit, uncertainty and
resource checks from the comparison contract, and returns a fresh parsed value.
It needs no comparison, emits no verdict and performs no I/O. `evaluate_policy`
reuses it and additionally validates the actual comparison and exact analysis
agreement. Existing frozen metric/evaluator signatures remain unchanged. Job
preflight uses this helper, never an invented zero-valued comparison report.

Expected input, filesystem, dependency-admission and publication failures become
`JobError`, preserving useful underlying context. Cancellation such as
`KeyboardInterrupt` is not converted into success. Rejected input produces no
partial successful report. A valid leaking or incomplete corpus is a completed
audit outcome and is retained rather than converted into an input error.

## 2. Exact job input

All ten root keys and all nested keys shown here are required; unknown keys are
rejected. This is a shape example: its zero digests are illustrative expectations,
not observations or a runnable acquired archive.

```json
{
  "schema_version": 1,
  "contract_origin": "project-proposed-capture-job-v1",
  "job_id": "literal-offset-v1",
  "corpus": {
    "path": "corpus/corpus.json",
    "sha256": "0000000000000000000000000000000000000000000000000000000000000000"
  },
  "reference": {"capture_id": "reference", "file_id": "raw", "start_frame": 0},
  "candidate": {"capture_id": "candidate", "file_id": "raw", "start_frame": 0},
  "analysis": {
    "sample_rate_hz": 4,
    "channel_count": 1,
    "frame_count": 4,
    "window": "rectangular",
    "floor_fs": 1e-12,
    "frequencies_hz": [1]
  },
  "policy": {
    "path": "policy.json",
    "sha256": "0000000000000000000000000000000000000000000000000000000000000000"
  },
  "pairing": "index",
  "transform": "none"
}
```

| Object or field | Exact rule |
| --- | --- |
| Root | `schema_version` is exact integer 1; origin is the literal above; `job_id` is an ID; `pairing` is `index`; `transform` is `none`. |
| `corpus`, `policy` | Exactly `path` and `sha256`. The paths are relative to the job parent; hashes are expected exact file-byte identities. |
| `reference`, `candidate` | Exactly `capture_id`, `file_id`, `start_frame`; both IDs resolve within the one bound corpus; frame start is an exact integer in `0..134217727`. |
| `analysis` | Exactly the same six fields as policy analysis. Rate is an exact integer in `1..768000`; channels in `1..16`; frame count in `1..262144`. Window, floor and frequencies obey the comparison contract. |

IDs match `[a-z][a-z0-9_-]{0,63}`. Digests contain exactly 64 lowercase hex
characters. Dictionaries/lists and numeric values use exact built-in JSON/Python
types; subclasses, tuples and Boolean substitutes for numbers are rejected.
The two selections may name the same capture/file, including an exact
self-comparison. This is not independent evidence; the report exposes that fact.

`analysis.frame_count` is the one common count `N`. For each side require
`start_frame + N <= 134217728` intrinsically, and later require the sum not exceed
that actual inspected stream's frame count. The two starts are explicit selected
intervals, not a fitted relative delay. Every channel uses its side's same
half-open interval. All file channels participate in ascending index order.
No channel subset, relabeling, reorder, averaging, mixdown, padding or truncation
is admitted. Analysis remains in digital FS; no physical-unit conversion occurs.

The input must satisfy the intersection of the audio-window and metric bounds:
`C*N <= 1048576`, `N <= sample_rate_hz*600`, and, for `K` frequencies,
`C*N*K <= 16777216`. Hann requires `N >= 3`; frequencies are strictly increasing,
unique, finite and within `[0, sample_rate_hz/2]`; the floor is in `[1e-12,1e6]`.
All comparisons use the stated values without nearest-bin rounding or a hidden
epsilon. The policy's six analysis fields must equal the job's six fields;
admitted int/float frequency and floor values compare numerically.

## 3. Bounded input and path roots

| Resource | Inclusive job limit |
| --- | ---: |
| Job JSON bytes / value nodes / container depth | 65,536 / 4,096 / 8, with root depth 0. |
| Generic input container members / string characters | 4,096 / 2,048, before tighter fields. |
| Numeric token length / generic input magnitude | 64 characters / `1e12`, before tighter fields. |
| Corpus captures admitted by this wrapper | 64. The standalone auditor still admits its own 512-record limit. |
| Total artifact references over all admitted manifests | 256, counting repeats and support files. |
| Returned corpus graph edges | 4,096; never truncate a graph to fit. |
| Tool source files | Exactly six listed below, each at most 1,048,576 bytes. |
| Serialized report UTF-8 bytes / value nodes / depth | 16,777,216 / 1,048,576 / 32. |
| Combined report numeric magnitude | `4e18`; nested comparison values retain their own stricter `2e18` limit. |

The envelope number allowance accounts for a policy interval adding a margin of
at most `1e6` to an admitted nonnegative metric. It does not broaden sample,
policy or comparison admission. Every number remains finite. All corpus, v1,
audio and policy bounds still apply, including 1 MiB index, 64 KiB per manifest,
2 GiB aggregate artifact references and 256 MiB selected-audio references.

The 4,096-edge allowance follows a conservative bound without pairwise growth:
session and v1-group stars contribute at most `2*(64-1)=126`; the 64 captures
contain at most `64*32=2048` gesture/family label occurrences, hence at most that
many label-star edges; capture parents contribute at most `64*16=1024`; byte and
decoded-audio stars each contribute at most `256-1=255`. Their total is at most
**3,708**, already below 4,096. Distinct reasons remain distinct. A postcondition
still checks the actual count to catch an implementation or dependency error.

The job, corpus and policy inputs use strict UTF-8 JSON: no BOM, duplicate keys,
trailing content, nonfinite or overflowing number, overlong numeric token,
unpaired surrogate or control character in any string. Generic strings are
nonblank. Direct validation also rejects cycles and unsupported value types.
The [shape schema](../data/capture-job.schema.json) cannot establish all of these
byte/token/traversal properties.

The selected job is a regular nonsymlink, non-reparse leaf. Its parent is the
job root and is itself a nonsymlink/non-reparse directory. Ancestors above that
root may be canonicalized for ordinary OS aliases. `corpus.path` and
`policy.path` use the corpus/v1 portable path grammar: at most 240 ASCII
characters, at most eight slash-separated 1..64-character components, initial
alphanumeric followed by alphanumerics, `.`, `_`, `-`; no trailing dot or Windows
device stem, traversal, empty component, backslash, colon, absolute or UNC form.
Every descendant directory and leaf is independently admitted without following
symlinks/reparse points. The corpus parent then remains its own corpus root;
each artifact remains relative to its own manifest parent. Concatenated paths
do not replace those separately bounded root-relative declarations.

Use bounded regular-file reads and portable before/after pathname, descriptor
and parent identity checks. Preserve corpus hardlink checks. A direct audio
call's acceptance of an absolute path is not a substitute for confinement.
Before/after directory checks compare type and usable identity rather than
timestamps changed by unrelated sibling activity. Close every owned descriptor
on success, rejection or cancellation. These observations require quiescent
inputs; they are not a hostile concurrent-filesystem sandbox or a signature.

## 4. Admission order, complete audit and selected windows

The implementation must satisfy this order; helpers may share already admitted
metadata without duplicating definitions or returning unverified observations.

1. Read and hash exactly the job bytes parsed, validate the job, and admit the
   job-relative corpus/policy paths. Read the corpus index and policy under their
   bounds; hash their actual consumed bytes and match both expected hashes.
   Validate the corpus index and call `parse_policy` before any artifact scan.
   Reject more than 64 captures before reading their manifests.
2. Admit all capture manifests, binding their exact parsed bytes to the index
   and unchanged capture v1. Preflight every declared artifact/reference limit,
   the 256-reference limit, selections, purposes, evidence class and selected
   descriptor geometry. Check job/policy analysis agreement and all declared
   window/work bounds before artifact hashing or decoding. Reuse admitted corpus
   metadata and validation helpers; retain the parsed index and manifests with
   their observed hashes and file observations. This prepared metadata is not
   credited as a file audit. Calling the public structural auditor after a
   separate index read is not an exemption from the read and preflight limits.
3. Execute the **entire** corpus audit with `check_files=True, check_audio=True`.
   The primary composition path is one shared private corpus-audit core operating
   on exactly the already admitted parsed index/manifests and observed hashes.
   The unchanged public `audit_corpus` signature and report use that same core
   after their ordinary metadata admission. Sharing metadata must not skip,
   normalize, fabricate or reuse a previous operation's artifact observations:
   the core performs every actual file/audio read required for this operation.
   If an implementation instead elects bounded metadata rereads, each index read
   must match the expected byte hash and the 64-capture limit **before** reading
   manifests; every manifest must bind its own parsed bytes, and all 256-reference
   and aggregate preflight limits must pass again **before** artifact work. A
   final report-hash comparison alone is too late to enforce those limits.
   Call the full audit core once, not once per selected file. Every declared
   support artifact is byte checked and every selected raw/derived stream is
   decoded, including artifacts unrelated to the selected comparison pair.
4. Resolve both selected files in that complete audit. Each capture must be
   `recorded`; each file must be `raw` or `derived`, never support. A derivative
   must have its own explicit `derived_audio` descriptor. Both selections must
   have `audio_status: verified` and actual observations. Check their observed
   format/rate/channel geometry against their own expected descriptor and the
   job analysis. Check both original windows against observed frame counts.
5. Read each selected window with `read_audio_window`, retaining every channel
   and the exact requested interval. Check corpus-relative confinement before
   and after the read. The resulting full-stream inspection must match the
   corpus observation in size, byte SHA, format, rate, channel count, frame count,
   digest version and decoded SHA. Every sample outside the window is still
   subject to the audio contract. Matching reference/candidate selections may
   share a cached read only when every selector, interval and descriptor agrees.
6. Pass the two unchanged channel-major sample lists to `compare_signals` with
   the exact job analysis. Pass its complete result and the original admitted
   policy bytes to `evaluate_policy`. Retain all metrics, masked bins, criteria,
   uncertainty and failed/inconclusive results. The evaluation's policy hash
   must equal the independently observed bound policy hash.
7. Form the report below and recheck the complete input/source snapshot set:
   the job, index, policy, every consumed manifest, **all** audited artifacts
   (at most 256 references), their confined parent chains, and the six project
   source files. Retain each leaf's first admission observation and compare
   type, usable identity, size, modification and change times through the same
   filesystem API; directories compare type and usable identity, not timestamps
   changed by sibling activity. Preserve the constituent descriptor checks too.
   A root-only or selected-pair-only final check is insufficient. Apply envelope
   limits and canonical serialization. No success is returned before all required
   checks finish. Source files and input bytes are never rewritten to make
   identities agree.

The job and policy are each consumed once into a bounded byte buffer. The primary
prepared-metadata path reads the index/manifests once and reuses those same parsed
values for selected context and the full audit. An alternative metadata preflight
and full audit may each read them once, at most two total reads, subject to the
before-work identity/limit checks above. A separate selected-manifest context read
is permitted once per distinct selected capture only if it independently hashes
its actual parsed bytes and binds the same expected identity; reuse is preferred.
There is no unbounded retry loop.
The two window operations add at most two full audio inspections after the
single full corpus audit. All constituent byte/work bounds still apply. There
is no load-dependent wall-clock acceptance threshold.

## 5. Declared purposes and evidence classes

The reference and candidate purposes must be equal, including the possibility
that both are `unassigned`. They must match the policy's declared role through
this exact map; a mismatch is rejected input, never a silent reassignment:

| Both selected corpus purposes | Policy `evaluation_role` |
| --- | --- |
| `fit` | `fit` |
| `validation` | `validation` |
| `final` | `final_test` |
| `unassigned` | `unassigned` |

Equal purposes do not require equal effective corpus groups and do not establish
independence. The full corpus may contain other purposes. Its unrelated or
transitively connected failures/inconclusive findings remain in the job outcome.
Both-unassigned jobs therefore remain inconclusive even if their numerical
criteria pass. A `final` declaration and a policy hash do not prove untouched
final-test history or a policy frozen before inspecting outcomes.

A `synthetic_numerical_fixture` policy requires **both selected capture kinds**
to be `synthetic`. Either selected `hardware` capture makes that policy a rejected
input, even if its bytes were generated elsewhere or a synthetic uncertainty
margin would pass. `digital_comparison` may compare synthetic and/or hardware
declarations under its existing margin rules; it still cannot establish physical
fidelity. Other unselected hardware records in the complete corpus do not change
the selected pair's declared kind, but their audit findings remain visible.

## 6. Exact report and context preservation

The report has exactly these root keys:

| Key | Required content |
| --- | --- |
| `schema_version` | Exact integer 1. |
| `job_contract` | Literal `capture-job-v1`. |
| `job_id` | Same ID as the consumed job. |
| `status` | `pass`, `failed` or `inconclusive`, using section 7. |
| `inputs` | Exact identity object below. |
| `job` | Complete parsed job, retained without mutable aliasing. |
| `policy` | Complete parsed policy, including rationale and freeze evidence. |
| `reference`, `candidate` | Exact selection/context records below. |
| `self_comparison` | Boolean: true exactly when capture ID, file ID and start frame agree on both sides; common count/pairing already agree. |
| `corpus_report` | Complete actual `files_and_audio_checked` corpus report, unchanged. |
| `evaluation` | Complete actual policy evaluation, including its complete comparison, unchanged. |
| `runtime` | Exact stable runtime object below. |
| `tool_sources` | Exact six source observations below, sorted by module name. |
| `boundary_equivalence`, `synchronization`, `authenticity`, `specimen_identity`, `calibration`, `permissions`, `independence`, `preregistration`, `final_holdout_history`, `physical_fidelity` | Each literal `not_established`. |

`inputs` has exactly `job`, `corpus`, `policy`. Its `job` has exactly
`size_bytes` and `sha256`, observed from the exact parsed job bytes. Its `corpus`
and `policy` each have exactly `path`, `size_bytes`, `expected_sha256`,
`observed_sha256`. Paths are the unchanged job-relative declarations; expected
hashes come from the job; observed size/hash come from actual consumed bytes.
Expected and observed hashes must agree in every returned report. The observed
corpus hash equals `corpus_report.index_sha256`, and the policy hash equals
`evaluation.policy_sha256`. No requested hash is copied into an observation to
replace a read. No report self-hash or output pathname is inserted.

Each selection record has exactly:

```text
capture_id, file_id, purpose, capture_kind, file_kind
manifest_path, manifest_sha256, artifact_path
capture_manifest, context_scope
window, inspection
```

IDs/purpose/kinds come from admitted matching records. `manifest_path` is the
unchanged corpus-relative path, `manifest_sha256` is observed from the actual
manifest bytes, and `artifact_path` is the unchanged manifest-relative path.
`capture_manifest` is the **complete** validated v1 value parsed from those same
bound bytes, not a newly synthesized summary. `window` has exactly
`start_frame`, `frame_count`, `end_frame`, with the original half-open bounds.
`inspection` is the complete actual audio inspection **minus only `input_path`**;
all other fields, full-stream statistics and claim limits remain unchanged.
This explicit projection removes a machine path without removing byte/sample
identity. Sample arrays themselves are not serialized into the report.

For raw selection, `context_scope` is `selected_raw_stream`. The retained
manifest includes its declared channel IDs/boundaries, port references,
calibration/clock status, signal path, stimulus, synchronization, initial-state
description if supplied, rights and raw/derived ancestry. These are retained
declarations, not authenticated facts. For derived selection, `context_scope` is
`ancestor_raw_stream_only`: that same manifest's digital channel/calibration and
clock metadata describe the raw stream. **Never inherit them as the derivative's
channel mapping, physical scale or clock calibration.** Its own selected format,
rate and channel count come from its explicit derivative descriptor and actual
inspection; its derivation is retained in the manifest. Missing derivative
physical context stays unestablished and cannot be repaired by a matching shape.

`runtime` has exactly `python_implementation`, `python_version`, `sys_platform`
and `machine`, obtained respectively from `sys.implementation.name`,
`platform.python_version()`, `sys.platform` and `platform.machine()`. Retain the
actual strings, including an empty machine string when the platform reports no
value. Each is at most 128 characters with no control characters or unpaired
surrogates; only `machine` may be empty. Include no host name, kernel build,
timestamp, absolute path or elapsed
time. The identity is useful replay context, not a complete platform description
or host qualification.

`tool_sources` contains one object with exactly `module`, `size_bytes`, `sha256`
for each of `capture_audio.py`, `capture_common.py`, `capture_corpus.py`,
`capture_job.py`, `compare_capture.py`, `validate_capture.py`. Observe the actual
regular, bounded source files associated with the imported project modules;
hash the bytes read and retain no machine path. Check their identities around
the job operation and reject observed changes. These are source observations,
not code signatures, loaded-memory attestations or an external trust anchor.
Run from a coherent quiescent installation; source hashes cannot authenticate
arbitrary monkey-patched process state.

## 7. Outcome, publication and deterministic CLI

The job status is **failed** if `corpus_report.status == "failed"` or
`evaluation.numerical_verdict == "fail"`; otherwise it is **inconclusive** if
either corresponding result is inconclusive; otherwise it is **pass**. Always
retain both full subordinate reports, including inconclusive findings beside a
failure. A pass is limited to the requested engineering checks and listed policy
criteria. No physical claim field changes as a result of that numerical outcome.

Commands from the repository root, or using an absolute script path:

```sh
python3 tools/capture_job.py --input /path/to/job.json
python3 tools/capture_job.py --input /path/to/job.json --output /existing/directory/new-report.json
```

No analysis, role, corpus, hash, gain or alignment override flag exists. Unknown
or abbreviated options reject. Help exits 0. Ordinary CLI usage errors exit 2.
Normal stdout is exactly `capture_common.canonical_json_bytes(report)`: sorted
keys, two-space indentation, `ensure_ascii=False`, `allow_nan=False`, UTF-8 and
one final LF. Write those UTF-8 bytes independently of terminal text encoding.
No progress or source/path diagnostic is mixed with JSON stdout.

| Exit | Outcome and stdout |
| ---: | --- |
| 0 | Complete `pass` report. |
| 1 | Complete `failed` report, or empty stdout for rejected input/publication with one contextual `job error: ...` diagnostic on stderr. |
| 2 | Usage error with empty stdout and a usage diagnostic. |
| 3 | Complete `inconclusive` report. |

For normal completed reports, stderr is empty. `--output` is the only file-write
option and uses `write_json_new` after complete validation/serialization and
before stdout. It creates a new report in an already existing parent, supports
failed/inconclusive reports too, never creates directories and never replaces an
existing file, symlink, directory or concurrent destination. The destination's
bytes exactly equal normal stdout. Output location is not part of the report.
Keep the common helper's explicit failure distinction if publication completed
but temporary cleanup failed: preserve the complete published file and report
the actual failure, without pretending the write did not occur or deleting it.
An output-stream I/O failure after publication can leave a complete report file;
it cannot guarantee an atomic stdout stream and must not be reported as success.

Repeated runs and relocation of an unchanged whole job archive under the same
runtime/tool source identities produce the same report values and canonical
bytes. A moved archive's job-relative paths remain unchanged. A changed job or
policy's whitespace changes its exact observed identity even when values match.
Different Python/platform math environments can change final numerical bits;
the underlying comparison contract promises numerical budgets, not universal
cross-platform byte identity. Retain original job/index/manifests/policy/audio
bytes for replay; parsed report copies cannot reconstruct their whitespace.

## 8. Independent acceptance and later work

Independent tests must construct source bytes, manifests, graph expectations,
window selections and policy decisions separately from this producer. At least:

1. Use mono raw float32 `[1,-1,1,-1]` and
   `[1.25,-0.75,1.25,-0.75]`, rate 4, count 4, one channel. With equal
   `validation` purposes and a synthetic policy, pointwise bias/RMS/max error
   are exactly `0.25`. Margin `0.125`, limit `0.375` passes; limit `0.25` is
   inconclusive. Candidate `[1.5,-0.5,1.5,-0.5]`, margin `0.125`, limit `0.25`
   fails. Independently form original-byte and canonical decoded hashes.
2. Put different finite prefix/suffix samples around those four frames and
   choose different explicit start frames on the two sides. The selected metric
   stays the same, the retained original bounds/full-stream hashes change, and
   no fit or silent cropping occurs. A NaN outside either window rejects.
3. Add an unselected fit capture with duplicate reference audio or declared
   lineage. Retain the complete resulting split failure even while the selected
   pair's numerical criterion passes. Add an unrelated planned/unassigned record
   to obtain an inconclusive corpus and preserve that finding beside any failure.
4. Exercise all purpose mappings, both-unassigned selection, hardware/synthetic
   combinations, exact self-comparison and different windows of one file.
   Mismatched purposes/role or synthetic policy with either hardware selection
   rejects; no physical field becomes pass.
5. Select a derivative with its own changed format/rate/channel descriptor;
   verify its geometry and `ancestor_raw_stream_only` context. An omitted
   descriptor, support selection, missing ID or planned selection rejects.
   Raw calibration must never appear as a verified derivative calibration.
6. Mutate job, policy, index, manifest or artifact bytes, including insignificant
   JSON whitespace; expected/observed binding must fail at the appropriate
   boundary. Preflight invalid policy, excess captures/references/work and
   declared geometry before a trapped artifact scanner is entered.
7. Verify safe foreign-directory/Unicode-root invocation and archive relocation;
   reject job-root/descendant symlink/reparse aliases and nonregular inputs.
   Exercise controlled identity changes, descriptor cleanup and root checks.
8. Check exact report fields/projections, all nested results, stable source/runtime
   observations, byte-identical new-file publication, existing-destination/raced
   destination preservation, cleanup failure disclosure, all four exits and
   no partial stdout for input or pre-publication errors. Exercise report bounds
   without truncating observations or serializing sample arrays.

For acceptance vector 1, these independent complete 16-byte raw float32 inputs
and canonical identities are fixed. All use rate 4, one channel and four frames;
the decoded preimage is the literal 27-byte digest prefix followed by
`struct.pack("<IIQ", 4, 1, 4)` and the four normalized binary64 samples.

| Vector | Raw little-endian bytes | Complete raw-byte SHA-256 | Canonical decoded SHA-256 |
| --- | --- | --- | --- |
| Reference | `0000803f000080bf0000803f000080bf` | `fd801740524b1e1c23a61b5400725b76428652827ba1261b83243eb5ce551402` | `786665f3cf05b2f9b33e7cadee75e7176e122d62ad82133c72737c76261dd440` |
| Quarter offset | `0000a03f000040bf0000a03f000040bf` | `bac1c395abe23908b8c106a28b6c151bc25b9473d470f4d942775b5dfdf523e2` | `79d8014af588d583abcc570598d3e073413543ef518b339cbca37dbb5eb6bd0c` |
| Half offset | `0000c03f000000bf0000c03f000000bf` | `36d231b4ecc15924aea04f08725924f18ae4346fd287747791d7396eca3d5758` | `52c3450c9c276f60b8ed6dc728977cfe33b4b0702ce8332927169d25f18e4db8` |

The schema enforces shape, enums, local numeric/string/array limits and portable
paths. It does not distinguish integer token `1.0` from mathematical integer 1,
validate strict bytes/duplicates, compute products, resolve IDs, check relative
roots, prove graph/group consistency, bind actual hashes, validate the external
policy, inspect audio or establish physical evidence. The implementation must
perform every semantic gate above even after schema validation.

Assignments 25/26 implement and independently qualify this contract after the
separate cross-contract review. Subsequent study/replay tooling can consume its
identities and complete outcomes. Fixed shared corrections, physical-unit
conversion, calibration fitting, acquisition chronology, listening results,
device/host qualification and a specimen-specific fidelity verdict remain open.
The [assignment record](development/2026-11-13-calibration/19-file-job-contract.md)
retains the actual authoring, consulted identities and schema/algebra checks.
