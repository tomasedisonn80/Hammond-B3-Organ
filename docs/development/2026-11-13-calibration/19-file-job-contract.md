# Assignment 19 — declared file-comparison job contract

**Actual assignment:** `/root/cal_w4_a19`, calibration wave 4, assignment 19.
This is one newly dispatched contract-authoring assignment. It started while
the final wave-3 acceptance workers finished; it does not claim that their work
was already complete or recount any earlier assignment.

**Outcome:** froze the `capture-job-v1` implementation target and strict input
shape schema, reconciled the policy preflight API with root, and executed the
schema/algebra/hash checks below. No job producer or job acceptance suite is
claimed by this assignment.

## Ownership and source

Owned files only:

- `docs/CAPTURE_JOB_CONTRACT.md`
- `data/capture-job.schema.json`
- `docs/development/2026-11-13-calibration/19-file-job-contract.md`

Working directory: `/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ`.
Initial `HEAD` and locally recorded `origin/main` were
`5026f671e788eb5e1a77c8ed4046a34afd539200`, tree
`2ed85b986f70895000f086039750f44773508819`. Existing producer/test/root edits
were present and preserved. Root advanced local/publication refs and integrated
concurrent standalone work during this task; these three owned files remained
uncommitted and outside that checkpoint. The hashes below identify this work,
not the starting commit alone. This worker performed no fetch, commit or push.

Read standing instructions, calibration scope/handoff, other active ownership
scopes and the entire three frozen audio/corpus/comparison contracts. Reviewed
their current APIs, admission/identity/report implementation and the common JSON
publisher, with capture-v1 channel/derivation semantics. The initial exact
dependency identities were:

| Input | SHA-256 |
| --- | --- |
| Audio contract | `1766ed93f26eb5fa4db21397f6dd74002970ec567e7ff4541536911598d026cc` |
| Corpus contract | `a524a38eedf8b18decd39845df844cc86ad98f8409216523e9917bb372bfb8b2` |
| Comparison contract | `4ec3037aa0588528fe3c9e520d099cc48a82d78135fc86bd3851c2667860750c` |
| `capture_audio.py` | `967ecc3c5b8ea3e12d71341c28edc22ced8da4316c2a81a9059f6eafa19851c2` |
| `capture_corpus.py` | `68c710c8afdb2985446ef25b4d0ed7d690970dc8be33535facf0a5ee1747adbe` |
| Metric-only `compare_capture.py` | `5165543a66c42ae0dbb1200e38b26cb739bbaa0dfcb3878cc05ce4f665132e3d` |
| `capture_common.py` | `e06dd82e37dd178863af61aa66bee877da1fc7e498a47b729e060215ca79c3f2` |
| Unchanged `validate_capture.py` | `a872e069ba9744f6f8078f87b78ea300df1ee28aec58e104859580cdc09877af` |

Relevant original atlas text was reread at pp. **355, 364, 367, 368, 484 and
486**, from the current session's per-page extraction. The complete 500-page
reading remains the separate assignments 1–6; this task does not claim another
full reading or new external-source verification. The source supports retained
boundaries/identities, declared corrections, independent evidence and fixed
decision criteria. The new API, schema and limits remain explicit project choices.

## Frozen integration decisions

The API is `JobError`, `validate_job`, `load_job`, `run_job`, and `main`.
Exactly ten input fields bind one corpus and one policy by expected exact-byte
hash, select reference/candidate capture and file IDs, declare separate original
start frames and one common six-field analysis, and fix index pairing with
`transform: "none"`. There are no command-line overrides for analysis, sources,
roles, gain, delay, channels or policy identity.

The procedure preflights strict job/index/policy/manifests and all declared
counts, geometry, roles and work before artifact scans. It then performs one
complete corpus byte/audio audit and up to two bounded whole-stream/window
inspections. Every actual window's full byte/sample identity must agree with
the admitted corpus observation. Failed or inconclusive full-corpus findings
remain visible beside the computed selected-pair evaluation.

Root explicitly approved these design decisions before finalization:

- Add `parse_policy(policy_json: bytes) -> dict` to the comparison module for
  intrinsic strict admission without a report or verdict. `evaluate_policy`
  reuses it. This avoids duplicating policy semantics or constructing an
  invented zero-comparison result merely to preflight a policy.
- Limit this wrapper to **64 captures and 256 total artifact references**,
  counting repeats and support. The standalone corpus contract stays unchanged.
- Require equal selected purposes and the exact policy-role mapping, including
  `final` to `final_test`. Both-unassigned remains allowed but inconclusive.
- Permit a synthetic numerical policy only when **both selected capture kinds**
  are synthetic. Digital-comparison policies retain their existing margin rules.
- Retain the complete selected v1 manifests and mark derivative context
  `ancestor_raw_stream_only`; never inherit raw calibration/channel meaning as
  the derivative's own physical context.
- Preserve full corpus and policy-evaluation reports, with the latter's complete
  comparison; project only the audio inspection's absolute `input_path` away.
- Observe six project source files and stable Python/platform fields for replay,
  without treating those observations as signatures, loaded-memory attestation
  or platform qualification.
- Bound the combined report to **16 MiB UTF-8, 1,048,576 value nodes, depth 32**,
  with numeric envelope magnitude **4e18**. The comparison's own **2e18** bound
  stays unchanged; the envelope permits the policy interval's added margin.

The conservative edge bound is independently explicit:

```text
session/group stars:  2 * (64 - 1) = 126
label occurrences:    64 * 32      = 2048
capture parents:      64 * 16      = 1024
byte/audio stars:     2 * (256 - 1)= 510
total upper bound:                 3708 < 4096
```

This is an inequality argument using occurrences, not a quadratic pair graph
or a claim that all upper bounds can be attained simultaneously. The producer
still checks the actual edge count and never truncates evidence.

## Actual author verification

Environment: Linux, **Python 3.12.14**. The existing environment's
**jsonschema 4.26.0** was used only for schema-authoring checks; the proposed
runtime tool has no third-party dependency.

An inline `python3 -B - <<'PY'` probe loaded the actual schema, ran
`jsonschema.Draft202012Validator.check_schema`, extracted the contract's literal
JSON example and completed **91 schema cases**, all with the expected result.
Cases covered the valid example; every missing root/nested key; unknown keys;
portable-path traversal, aliases, separators, device names, control/Unicode and
length/component limits; IDs; wrong scalar/enum/range values; duplicate numeric
frequencies; Hann length 2/3; and start-frame bounds. The probe separately
demonstrated three intentionally semantic-only cases that the shape schema
admits: integer token `1.0`, decreasing frequencies, and an excessive channel ×
frame product. The contract requires the runtime validator to reject them;
they are not silently described as schema-enforced properties.

The same probe checked the exact **3,708** edge bound and **four Fraction-based
interval cases**, without calling any producer/evaluator:

| `v`, `u`, `L` | Expected result |
| --- | --- |
| `1/4`, `1/8`, `3/8` | pass |
| `1/4`, `1/8`, `1/4` | inconclusive |
| `1/2`, `1/8`, `1/4` | fail |
| `3/8`, `1/8`, `1/4` | inconclusive at the lower-endpoint equality |

It independently formed three literal 16-byte raw float32 vectors, their full
byte hashes and decoded preimages from the literal digest prefix plus
`struct.pack("<IIQ", 4, 1, 4)` and four `<d` samples. Those **six hash values**
are now printed in the contract. A final repeat extracted the actual printed
hex/digests from that table, reconstructed every preimage and passed all six
hash comparisons, plus the final metaschema and example validation. No decoder,
comparison producer, report fixture or production digest helper was used as
the expected-value oracle.

Additional actual checks:

```sh
git diff --check -- docs/CAPTURE_JOB_CONTRACT.md data/capture-job.schema.json
sha256sum docs/CAPTURE_JOB_CONTRACT.md data/capture-job.schema.json
python3 --version
```

Whitespace checking passed. No schema/algebra/hash failure was observed in these
author checks. These are **91 schema cases, six hash comparisons and four exact
interval examples**, not an implemented job's independently passed test count.

| Final authored artifact | SHA-256 |
| --- | --- |
| `docs/CAPTURE_JOB_CONTRACT.md` | `11f80a02597707d12423f6a02ff8f8574068827c17ce4fa62baa9e1abb76e012` |
| `data/capture-job.schema.json` | `af1046b9d50d18e6da553805972591a2cf330403b8196ca376a577bfdb7afa2a` |

## Next dependency and limitations

Worker 22 independently reconciles this contract/schema against its dependencies
before worker 25 implements the job and worker 26 writes independent acceptance.
Worker 20 supplies the additive policy parser and evaluator. Tests must exercise
the complete actual archive, both raw and derived selection, role/evidence
rejection, whole-corpus fail/inconclusive precedence, bounded preflight, exact
identities, relocation and non-replacing publication. A successful schema probe
does not close any of those runtime gates.

No job producer, CLI execution, artifact scan, filesystem-race test, no-clobber
job publication, full report replay, native Windows/macOS run or hosted workflow
was executed by this assignment. No acquired specimen, permission, physical
calibration, fixed correction, listening result or instrument-fidelity claim
was supplied or inferred. Root owns shared status, source integration, coherent
verification and authorized publication; all other tracks remain preserved.
