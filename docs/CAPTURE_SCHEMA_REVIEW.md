# Capture schema and semantic consistency review

## Result and authority

Assignment 30 independently reviewed the capture-v1, corpus, policy and file-job
schemas against their frozen contracts and actual semantic validators. One
schema-only defect was found in the older v1 string patterns: a terminal LF could
be accepted where the unchanged runtime correctly rejected a control character.
The integrator repaired those patterns without changing v1 fields or validator
semantics. The repair is independently verified below.

The completed audit has **600 document cases, 24 original-byte/parser cases,
36 actual cross-tool compositions and five original-versus-repaired regressions**.
These are **665 audit cases**, not 665 newly installed unittest methods. No
unexpected outcome remains in that executed scope. The retained
[assignment evidence](development/2026-11-13-calibration/30-schema-consistency.md)
records source identities, commands, the initial audit-tool expectation mistake
and limitations. This is a finite review, not a proof that all possible schema
and semantic inputs have been enumerated.

The runtime validators remain the admission authority. A JSON Schema pass is
useful structural feedback, but does not authorize a corpus audit, a comparison
job, acquisition or a physical-fidelity claim. Relevant contracts are
[capture v1](CAPTURE_FORMAT.md), [corpus](CAPTURE_CORPUS_CONTRACT.md),
[comparison/policy](CAPTURE_COMPARISON_CONTRACT.md),
[file jobs](CAPTURE_JOB_CONTRACT.md) and
[declaration readiness](CAPTURE_READINESS.md). The last tool consumes unchanged
capture v1 and does not introduce another acquisition input schema.

## What was compared

The audit used Python 3.12.14 and the already installed `jsonschema` 4.26.0,
specifically `Draft202012Validator`. All four schema documents passed
`Draft202012Validator.check_schema`. Every `$ref` in these documents is local;
no remote reference retrieval or package installation was needed. This optional
audit package is not a project runtime or default-test dependency.

Document fixtures use explicit project contracts, supplied examples and
independently assembled dictionaries. They are submitted separately to each
schema and to its actual semantic entry point:

| Domain | Schema | Actual semantic check |
| --- | --- | --- |
| Acquisition declaration | `data/capture.schema.json` | `validate_capture.validate_capture(value)` |
| Corpus index | `data/capture-corpus.schema.json` | `capture_corpus.validate_corpus(value)` |
| Fixed policy | `data/capture-policy.schema.json` | `compare_capture.parse_policy(original_json_bytes)` |
| File job | `data/capture-job.schema.json` | `capture_job.validate_job(value)` |

No producer validator supplies the expected result. Expected acceptance is
declared from the contract and independently constructed mutations. The byte
matrix also calls the real bounded loaders, and the composition matrix executes
actual temporary corpus audits and file jobs with explicitly synthetic sample
bytes. It does not mock their observed hashes or reports.

### Document outcomes

| Domain | Cases | Both admit | Both reject | Schema admits; semantic validator rejects |
| --- | ---: | ---: | ---: | ---: |
| Capture v1 | 253 | 30 | 202 | 21 |
| Corpus | 87 | 24 | 53 | 10 |
| Policy | 152 | 28 | 110 | 14 |
| File job | 108 | 16 | 81 | 11 |
| **Total** | **600** | **98** | **446** | **56** |

There was no tested document admitted by its semantic validator but rejected by
its schema. The 56 remaining schema-admitted rejections have explicit semantic
or parser responsibility, listed below. They are not treated as successful
execution because a schema accepted their shape.

The 600 cases include 219 baseline/missing-key/extra-key cases across every
object in the representative documents; 18 Boolean numeric-type rejections;
18 exact-integer distinctions; 38 Unicode/text cases; 52 identifiers; 78 portable
paths; 27 digests; 14 UTC cases; 28 analysis shape/cross-field cases; five work
products; two channel-consistency cases; seven identity-uniqueness cases; one
aggregate-size case; five graph cases; 21 typed target/unit cases; 30 uncertainty
combinations; eight known/unknown-reason pairings; 12 boundary/unit cases; six
array-count boundaries; eight preserved v1 format tokens; and three supplied
examples. These categories sum to 600; subchecks are not recounted as cases.

## Reproduced terminal-LF defect and accepted repair

Original schema SHA-256:

`2e33ff19c23b2c82d593073f6d24bd29889531c62acd2d8fcf08ec48c0ae7860`

Accepted repaired schema SHA-256:

`51fbfdbcc92d9cdb3b71d4b55618840a806e2847b49c93e6aa7d926621661a74`

Starting from the supplied planned example, either of these independent changes
was enough to demonstrate the defect:

```python
document["capture_id"] = "plan\n"
# Or, in a fresh copy:
document["status_reason"] = "plan\n"
```

The original schema admitted each complete document. The unchanged
`validate_capture` rejected each with `JSON string: control characters are
forbidden`. The final LF satisfies the older pattern's `$` boundary before that
last character; the earlier text expression therefore did not exclude the LF
from the whole supplied string.

The wider independent regression uses complete otherwise-valid declarations:

| Family | Original value followed by LF | Original schema | Repaired schema | Unchanged semantic validator |
| --- | --- | --- | --- | --- |
| Text | Planned `status_reason` | Admits | Rejects | Rejects |
| ID | `capture_id` | Admits | Rejects | Rejects |
| UTC | Recorded `acquisition.started_at_utc.value` | Admits without relying on a format checker | Rejects | Rejects |
| Portable file path | Recorded raw artifact `path` | Admits | Rejects | Rejects |
| Digest | Recorded raw artifact `sha256` | Admits | Rejects | Rejects |

Root changed only the schema: explicit forbidden-character exclusions for text
and IDs, ASCII exclusions for UTC/path fields, and exact lengths where needed.
The accepted v1 fields, genuine positive values, unknown reasons, synthetic
exemptions and runtime rejection rules remain unchanged. Positive Unicode text,
including an astral musical character, remains admissible. LF, CR, tab, C0/C1
controls, surrogate suffixes, invalid IDs and malformed hashes are separately
covered by the final matrix. The newer corpus/job ID and path schemas already
used explicit exclusions; they did not require this repair.

The original bytes are retained in public commit
`779fb6e13b8f60236cad4aedb9999ba16198f920`. A compact reproduction of the two
full-document failures, using the optional audit package, is:

```python
import copy
import json
from pathlib import Path
import subprocess
import sys
from jsonschema import Draft202012Validator

sys.path.insert(0, "tools")
from validate_capture import CaptureError, validate_capture

old = json.loads(subprocess.check_output([
    "git", "show",
    "779fb6e13b8f60236cad4aedb9999ba16198f920:data/capture.schema.json",
]))
new = json.loads(Path("data/capture.schema.json").read_text())
plan = json.loads(Path("data/capture-planned-example.json").read_text())
for field in ("capture_id", "status_reason"):
    value = copy.deepcopy(plan)
    value[field] = "plan\n"
    assert Draft202012Validator(old).is_valid(value)
    assert not Draft202012Validator(new).is_valid(value)
    try:
        validate_capture(value)
    except CaptureError:
        pass
    else:
        raise AssertionError("runtime must reject the terminal control")
```

Run that snippet from the repository root at the reviewed repaired source. It
does not read or alter capture artifacts, install a package or validate hardware.

## Remaining semantic and parser boundaries

The following **56** tested differences are deliberate or explicitly assigned
to the stricter checker. They must remain visible to callers of the schemas.

| Boundary | Cases | Concrete executed example and ownership |
| --- | ---: | --- |
| Exact integer type/token | 18 | Schema mathematical integer `1.0` can satisfy an integer constraint; all four tools reject it where an exact Python/JSON integer is required. Boolean substitutes are separately rejected by both. |
| Policy surrogate admission | 2 | Escaped unpaired high/low surrogates in criterion rationale pass the policy schema's text shape but reject in the strict original-byte parser. The schema description explicitly assigns surrogate admission to that parser. |
| Additional capture-v1 portable paths | 6 | `con.wav`, `AUX`, `Com9.x`, `lpt1/f`, `raw.`, and `raw./file` retain the v1 schema's documented weaker shape; the validator rejects reserved device stems and trailing dots. New corpus/job path schemas also reject them structurally. |
| Calendar validity | 4 | Non-leap February 29, April 31, hour 24 and second 60 have the timestamp shape but fail the runtime calendar check. The audit runner has no registered `date-time` format checker; see the setup correction below. |
| Analysis relationships | 6 | Unsorted frequencies, a value just above actual Nyquist, a target channel outside the declared count, or a frequency absent from the selected list requires semantic comparison between fields. |
| Work/window products | 5 | Excess spectral product in policy/job, excess job window scalars, a 601-second window at 1 Hz and a start-plus-count over the stream bound reject before execution. No large audio workload was executed for these declarations. |
| Channel order/count | 2 | A declared count of two with one channel, and channel index one in position zero, reject despite locally valid field ranges. |
| Selected-property uniqueness | 7 | Duplicate capture IDs, case-folded locators, manifest hashes, derivative file IDs, criterion IDs or criterion targets can occur in otherwise different objects. Whole-object `uniqueItems` is insufficient. |
| Aggregate artifact bytes | 1 | Three separately identified 256 MiB raw declarations exceed capture v1's 512 MiB total; no corresponding large files are created or scanned. |
| Ancestry and resolution | 5 | Missing/self file parents and missing/self/cyclic capture parents require actual ID resolution and complete graph traversal. |
| **Total** | **56** | Runtime rejection remains required after a schema pass. |

These are not all fundamentally inexpressible in every possible schema.
Character exclusions and some local conditionals are expressible and were used
where specified. Exact original token spelling, byte identity and filesystem
observations are not properties of an already parsed JSON value. Standard shape
constraints also do not perform the project's general graph traversal, arbitrary
cross-field arithmetic or external-file verification. The contracts explicitly
place those gates in the bounded semantic tools.

### Calendar audit setup correction

The first larger audit incorrectly expected that constructing `FormatChecker()`
would validate `date-time` automatically. Its four invalid-calendar fixtures
therefore produced unexpected schema admissions. Inspection showed that
`"date-time"` is absent from this installation's registered checkers and the
optional `rfc3339_validator` module is absent. An unknown format was consequently
left unasserted by this audit package.

That was an audit expectation/setup mistake, not an additional production defect.
All four exact invalid timestamps remained unchanged and still had the required
runtime rejection. Their classification was corrected to the already documented
calendar gate; no production code, acceptance requirement or timestamp was
weakened, and no dependency was installed. The final audit records
`date_time_format_checker_registered: false`. This limitation also means the
report does not claim that another validator, installed extras or a different
JSON Schema implementation has the same format behavior.

## Original-byte admission and resource composition

There are **24 executed parser cases**: for each of four input families, a valid
document padded with JSON whitespace to its exact byte maximum is admitted;
one more byte, a duplicate root key, UTF-8 BOM, invalid UTF-8 and a trailing
second JSON document are rejected. Capture, policy and job limits are 65,536
bytes; the corpus index limit is 1,048,576 bytes. These are actual bounded byte
reads or policy-buffer parses, not lowered-limit simulations.

A schema sees a JSON value after parsing, so it cannot recover discarded
duplicate keys or original whitespace. It cannot establish whether a reported
hash came from those parsed bytes. The unchanged semantic tools and job wrapper
must retain that responsibility. In particular, an admitted compact policy must
remain its original byte buffer; a formatted copy can have a different identity
and exceed the policy byte limit.

Other resource intersections remain explicit:

| Layer | Important independent bounds | Checked by this audit |
| --- | --- | --- |
| Capture v1 | 4,096 value nodes, depth 16, 32 files, 256 MiB per file, 512 MiB aggregate | Exact byte boundary; local field/types; declaration-only aggregate excess. Existing parser/file suites qualify the other operational paths. |
| Corpus | 65,536 value nodes, depth 16, 512 captures, 16 MiB manifest total, 2 GiB artifact references, 256 MiB selected-audio references | Actual 512-entry direct validation and 513-entry rejection; small actual manifest/audio compositions. No maximum aggregate scan. |
| Policy/metrics | 4,096 policy nodes, depth 8, 256 criteria, 16 channels, 262,144 frames, 64 frequencies; `C*N*K <= 16,777,216` | Actual 256-criterion original-byte admission and 257 rejection under 64 KiB; declaration-only spectral excess. |
| File job | 64 captures, 256 artifact references, `C*N <= 1,048,576`, at most 600 seconds, complete original-file/source checks | Intrinsic window/work excess and small real complete jobs. The independent job suite owns full wrapper admission/failure qualification. |
| Declaration readiness | Unchanged capture-v1 input; at most 69 checks and a separately bounded report | Source/contract consistency review only; assignment 28 supplies its independent runtime acceptance. |

The policies and jobs have input schemas. Their result envelopes and nested
comparison/corpus/selection data have separate runtime contracts; the input
schemas must not be presented as output-report validators. This audit did not
execute maximum spectral work, 2 GiB scans, 16 MiB job reports or every possible
node/depth boundary. Existing admission notes keep those distinctions explicit.

## Purpose, derivative and evidence consistency

The 36 real composition cases used temporary manifests, exact independently
computed hashes and tiny original raw-float32/support files. The expected role
maps were literal tables, not values read back from producer helpers.

| Corpus purpose | Required v1 role | Required policy evaluation role |
| --- | --- | --- |
| `fit` | `fit` | `fit` |
| `validation` | `held_out` | `validation` |
| `final` | `held_out` | `final_test` |
| `unassigned` | `unassigned` | `unassigned` |

All **12** corpus-purpose/v1-role combinations were actually audited: the four
required mappings admit and the eight mismatches reject. Every standalone
document in that matrix passes its own input schema. All **16**
corpus-purpose/policy-role combinations were then run through `run_job`: the
four prescribed mappings admit and the other twelve reject. Valid both-unassigned
jobs remain inconclusive; they cannot become a passing holdout through matching
role text. Other valid aligned jobs in this explicitly synthetic fixture pass
their stated numerical criterion while physical fidelity stays `not_established`.

The remaining **eight** composition cases establish these concrete boundaries:

- A raw acquisition declared at 4 Hz/one channel and a derivative at 8 Hz/two
  channels retain separate observed geometry. The derivative uses its own index
  descriptor, never the raw acquisition's rate or channel count.
- Omitting the derivative descriptor leaves its verified bytes but produces
  `derived_audio_not_declared`, partial audio coverage and an inconclusive audit.
- A derivative descriptor naming a raw file, a support file or a missing file
  rejects. Each index is structurally schema-valid; manifest resolution owns the
  rejection. Support bytes are checked but never decoded.
- Selecting the changed-geometry derivative in an actual job retains
  `ancestor_raw_stream_only` context. The copied manifest still declares its raw
  one-channel stream; the selected actual inspection has two channels. Neither
  declaration is rewritten to match the other.
- A v1 FLAC declaration remains valid metadata and can pass byte checking.
  Requesting audio checking rejects the unsupported format under the current
  audio contract. Removing FLAC from capture v1 would change preserved metadata
  meaning; pretending to decode it would exceed implemented audio scope.

The synthetic job policies in these checks preserve `transform: none`; no
resampling, nuisance fitting, gain adjustment or implicit boundary conversion
occurs. Their numerical results do not establish that a policy was frozen before
inspection, that sessions are independent, that permission text is valid, or
that any actual organ was captured. The atlas requires those distinct evidence
gates (PDF pp. 355, 364, 372 and 484); this audit preserves them.

## Continuation

Retain the repaired schema and the original counterexamples together. Keep the
semantic validators mandatory in every CLI, study, replay and installed workflow,
even when a caller already used JSON Schema. Do not auto-coerce integer-valued
floats, normalize paths or replace original policy bytes to reconcile an input.
Changing a contract, schema or validator requires rechecking the affected
positive, negative and composition cases at the resulting source identities.

The integrator should include this review and assignment note in the coherent
wave-5 gate, update the current handoff and publish under the standing guarded
workflow. No additional code repair is requested by this review. Native
Windows/macOS execution, hostile-filesystem behavior, actual acquisition,
calibration, permission, held-out chronology and instrument fidelity remain
outside this audit's qualification.
