# Capture job v1 independent contract review

**Readiness verdict:** cleared for implementation at the exact contract and
schema identities below. The initial audit-composition blocker is resolved.
This is a contract review with independently executed schema, algebra, identity
and structural-budget checks. It is **not acceptance of an implemented job
runner**, a replayed capture archive or physical instrument evidence.

Reviewer: actual calibration assignment 22, `/root/cal_w4_a22`, wave 4,
2026-11-13. Implementation belongs to assignment 25 and independent acceptance
to assignment 26. The [assignment note](development/2026-11-13-calibration/22-job-contract-review.md)
records ownership, observed source state and execution limits.

| Reviewed artifact | SHA-256 |
| --- | --- |
| Initial author contract | `11f80a02597707d12423f6a02ff8f8574068827c17ce4fa62baa9e1abb76e012` |
| Cleared [job contract](CAPTURE_JOB_CONTRACT.md) | `ed0b34cbd45d737ea35b33d3049d1b8884f8f665d4f42caeb1e1406466217b84` |
| Unchanged [job shape schema](../data/capture-job.schema.json) | `af1046b9d50d18e6da553805972591a2cf330403b8196ca376a577bfdb7afa2a` |

## 1. Blocking composition finding and resolution

The initial section 4 could compose a separate index admission, the public
structural audit and the public full audit. The current public `audit_corpus`
loads the index and manifests on every call. That composition can read the
index three times, exceeding the stated two-read preflight/audit budget. More
seriously, the full public call could consume a changed index and enter manifest
or artifact work under the standalone limits before the wrapper checks its
returned index hash. A hash mismatch detected after artifact scanning does not
enforce the job's **64-capture and 256-reference preflight limits**.

The reviewer reported this as a blocker before implementation. Root revised
section 4; the reviewer reread the actual resulting text and its complete
surrounding contract. The cleared wording requires:

- One shared private full-audit core consumes the exact admitted parsed index
  and manifests, their observed hashes and retained file observations. The
  unchanged public corpus API calls that same core after its ordinary admission.
- The shared core still performs every actual artifact and requested audio read
  for this operation. Prepared declarations are never promoted to observed
  bytes, and an earlier operation's audit results cannot substitute for reads.
- If an implementation elects the explicitly bounded reread alternative, each
  index read must match the expected bytes and pass the 64-capture limit before
  manifests. Every manifest binds the bytes actually parsed; the 256-reference
  and aggregate limits pass again before artifact work. Final report-hash
  comparison alone is insufficient.
- The primary path reuses the admitted selected manifests for report context.
  The contract separately permits one context reread per distinct selected
  capture only when that read hashes and binds its own parsed bytes. Assignment
  25 should use the primary reuse path and avoid that extra read.
- The job retains each leaf's first admission observation and performs a final
  check over the job, index, policy, all consumed manifests, **all audited
  artifacts**, their confined parent chains and six project source files.
  Leaves compare type, usable identity, size, modification and change times
  through the same filesystem API. Directories compare type and usable identity;
  unrelated sibling activity must not invalidate them through parent timestamps.
  Constituent descriptor checks remain necessary.

This closes both the early admission and final snapshot gaps without changing
the public corpus signature, its report, capture v1 or numerical definitions.
The exact artifact-reference ceiling also bounds snapshot bookkeeping: at most
329 leaf-reference observations from three top-level inputs, 64 manifests,
256 artifact references and six source files, before deduplicating repeated
locators. Parent-chain observations remain separately necessary. These portable
checks require quiescent inputs; they are not an adversarial filesystem sandbox.

## 2. Cross-contract decisions verified

### Selected data and evidence

Both selections must resolve to recorded raw files or explicitly described
derivatives in the one bound corpus. Support files, missing selections, planned
selections and derivatives lacking their own audio descriptor reject. Complete
corpus byte/audio verification precedes the two selected windows; unrelated
artifacts and corpus failures cannot disappear from the report.

The windows preserve their declared original start frames, common frame count
and every channel. Each full-stream window inspection must match the corpus's
size, raw-byte hash, format, rate, channel count, frame count and canonical
decoded identity. No hidden fitting, channel remapping or resampling is allowed.
Even samples outside the selected interval remain subject to full audio
admission. Exact self-comparison is exposed by selector equality and does not
establish independent evidence.

| Equal selected corpus purposes | Policy role |
| --- | --- |
| `fit` | `fit` |
| `validation` | `validation` |
| `final` | `final_test` |
| `unassigned` | `unassigned` |

The policy role is distinct from capture v1's broader `held_out` role used by
the corpus for validation/final manifests. Both-unassigned jobs retain the
corpus's inconclusive result. A synthetic numerical policy requires both
selected capture kinds to be synthetic; unrelated hardware records do not
change the selected kinds but their full-corpus findings remain visible.

For derivative selection the complete manifest remains present, with
`context_scope: ancestor_raw_stream_only`. Its raw channel, calibration and clock
declarations must never become the derivative's own physical mapping or scale.
The derivative's descriptor and observed stream provide its selected digital
geometry. All ten job-level physical/provenance claims remain
`not_established` for every numerical outcome.

### Identity, publication and replay

The job, corpus index, manifests and policy bind exact consumed bytes, including
whitespace. Requested hashes cannot substitute for reads. The policy's original
byte buffer must survive preflight and be passed unchanged to `evaluate_policy`.
Complete parsed job/policy/selected-manifest copies are retained without mutable
aliasing, but they cannot reconstruct original whitespace.

The report retains the complete corpus report and policy evaluation. It removes
only `input_path` from each complete selected audio inspection and serializes no
sample arrays. Runtime fields and six source hashes provide bounded replay
context; they do not identify the kernel/host, authenticate loaded memory,
establish platform qualification or defeat arbitrary monkey-patching.

The publication contract matches `capture_common.write_json_new`: serialize and
validate first, publish a complete new file without replacing an existing or
raced destination, then emit the same UTF-8 bytes to stdout. Existing parents
are required. A publication followed by temporary-cleanup failure preserves the
complete published file and reports the real failure with empty stdout. A later
stdout I/O failure can likewise leave a complete file; success cannot be claimed.
These were source/contract checks, not execution of the future job CLI.

The nine-case status table was independently enumerated: five combinations are
failed, three inconclusive and only corpus-pass/policy-pass is pass. Failure
dominates while all inconclusive findings remain in their subordinate reports.

## 3. Independent executed checks

Environment: Linux, Python **3.12.14**. The already installed **jsonschema
4.26.0** served only as an authoring/review tool; no runtime dependency was added.
Two inline `python3 -B` probes ran successfully. Review input hashes were taken
before and after the probes and remained unchanged during each probe.

### Schema admission and its limits

The actual Draft 2020-12 schema passed metaschema validation and **189 independent
cases: 30 expected admissions and 159 expected rejections**. Cases covered every
missing root/nested field and unknown field, fixed literals, IDs/digests, local
types/ranges, Hann length 2/3, start limits, duplicate numeric frequencies and
portable-path grammar. Path cases included 240/241 total characters, 64/65 per
component, eight/nine components, Windows device stems and extensions, traversal,
absolute/UNC/backslash forms, non-ASCII, controls and terminal newlines/dots.

Seven additional examples deliberately passed this **shape** schema while
violating runtime requirements: integer token `1.0`, integer-valued floating rate,
decreasing frequencies, frequency above the declared rate's Nyquist bound,
start-plus-count overflow, sample/spectral work products and the 600-second
window bound. These are explicitly documented implementation gates, not schema
defects. Raw duplicate keys, strict UTF-8/token limits, cycles, actual filesystem
roots, resolved IDs, hashes, external policy and physical evidence likewise
require runtime admission.

### Literal bytes and exact interval decisions

The probe independently constructed all three 16-byte raw float32 vectors from
literal values and hexadecimal bytes. It extracted the six printed hashes from
the actual contract and recomputed each without the decoder or a production
digest helper. The canonical preimage used the literal 27-byte prefix
`HAMMOND-CAPTURE-DECODED-V1` terminated by NUL, followed by `<IIQ` geometry
`(4,1,4)` and four little-endian binary64 samples. **All six hashes agreed.**

Exact `Fraction` arithmetic independently established bias, RMS error and
maximum error as `1/4` for the quarter-offset vector and `1/2` for the half-offset
vector. Four interval cases passed:

| Metric, margin, limit | Exact interval | Decision |
| --- | --- | --- |
| `1/4`, `1/8`, `3/8` | `[1/8, 3/8]` | pass |
| `1/2`, `1/8`, `1/4` | `[3/8, 5/8]` | fail |
| `1/4`, `1/8`, `1/4` | `[1/8, 3/8]` | inconclusive |
| `3/8`, `1/8`, `1/4` | `[1/4, 1/2]` | inconclusive; equality at the lower endpoint is not fail |

### Resource composition and report bounds

Independent arithmetic reproduced the conservative **3,708-edge** bound below
4,096. It checked the sample-window intersection and exact spectral ceiling
`16 * 16384 * 64 = 16777216`. At 64 manifests the individual 64 KiB cap also gives
a 4 MiB maximum, below the unchanged 16 MiB aggregate manifest allowance.

A hand-authored **structural scaffold**, not audio-derived metrics, exercised
the existing report validator, policy parser/evaluator and canonical serializer
at 16 channels, 64 frequencies and 256 distinct policy targets:

| Object | Value nodes | Maximum container depth | Canonical UTF-8 bytes |
| --- | ---: | ---: | ---: |
| Comparison shape | 43,809 | 6 | 1,557,872 |
| Policy shape | 3,921 | 3 | 104,893 |
| Evaluation shape | 50,220 | 7 | 1,852,283 |
| Evaluation nested in an envelope | 50,221 | 8 | 1,980,305 |

The valid policy's actual compact input was **65,437 bytes**, within 65,536,
although its canonical formatted copy was **104,893 bytes**. Re-serializing that
parsed policy and supplying the result to the evaluator would violate both its
byte identity and input limit. Keep and reuse the original admitted bytes.

Nine direct common-helper boundary checks passed: 1,048,576 nodes accepted and
1,048,577 rejected; depth 32 accepted and 33 rejected; finite envelope values
through exact `4e18` accepted, `4e18 + 1` and infinity rejected; and
`2e18 + 1e6` accepted by the envelope but rejected by the comparison-only bound.
Exact integer arithmetic established `2000000000001000000 > 2e18` and `< 4e18`.

These profiles establish compatibility of the dominant nested report shapes
with their guards. They do not execute or authenticate a complete file job and
do not prove every otherwise admissible archive fits 16 MiB. The wrapper must
still enforce actual full-report bytes/nodes/depth after preserving every
required result, rejecting excess without truncation. The generic common
serializer alone is insufficient: its depth and numeric limits are looser than
the job's 32 and `4e18`, and it does not enforce the job's 16 MiB serialized cap.

## 4. Required implementation and acceptance follow-through

Assignment 25 may now implement against the cleared hash. Its shared private
corpus refactor must preserve the standalone signature, report semantics,
confined reads, descriptor ownership and hardlink checks. The prepared path
must retain exact parsed metadata and first-admission snapshots through the
final job checks. Preserve original policy bytes throughout evaluation.

Assignment 26 must independently exercise real file archives and the job API/CLI,
including trapped scanners proving rejection before artifact work; whole-corpus
failure/inconclusive precedence; selected and unselected metadata/artifact
changes after their reads; source changes; raw/derived context; all role/evidence
combinations; explicit windows and invalid samples outside them; relocation;
source/runtime records; output bounds; and non-replacing publication with cleanup
and stdout failures. The existing independent corpus tests must also pass after
the shared-core refactor. Native Windows/macOS behavior remains separate from
portable logic inspected on Linux.

No job execution, complete replay, live filesystem-race acceptance, hosted CI,
new acquisition, calibration, listening result or physical-fidelity result is
claimed by this review. Root owns integration, shared progress records and the
authorized commit/push checkpoint.
