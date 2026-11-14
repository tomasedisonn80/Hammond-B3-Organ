# Capture study v1 independent review and acceptance

**Verdict:** the frozen study contract is cleared and its bounded offline
implementation passes the independent Linux acceptance below. No production
failure was found. This qualifies the exact source bytes recorded here for
synthetic engineering use; it does not establish physical calibration, archive
authenticity, independent acquisition or an untouched final holdout.

Reviewer: actual calibration assignment **32**, `/root/cal_w6_a32`, logical
wave 6, 2026-11-13. Assignment 31 owns the producer. The reviewer owns only
this review, [the acceptance suite](../tests/test_capture_study.py), and the
[assignment evidence note](development/2026-11-13-calibration/32-study-acceptance.md).
The suite was authored from the cleared contract and earlier independent literal
archive fixtures before grading the implementation. Producer output did not
define expected hashes, work, status algebra, roles, policy decisions or fields.

| Qualified artifact | SHA-256 |
| --- | --- |
| [Frozen study contract](CAPTURE_STUDY.md) | `a60d8c6a92356f2381ea61ba39c0dab50048b0f88ee6dc75bf943c7f5c5198e3` |
| [Study input shape schema](../data/capture-study.schema.json) | `1805ad62f357ec7f828591dce0a968391beba42418b9ea4f20adfe4139389e3d` |
| `tools/capture_study.py` | `4b627a8c213ff43691e8011dca0a4206db8f4184dd32b5ea6edad4471f90e69d` |
| Private extension in `tools/capture_job.py` | `147002ac866a4451e6740eae69da9f914116339f89b657bae7d4c6ef41e3eded` |
| Final independent `tests/test_capture_study.py` | `19f3c58d91026292d353434b6c0ac0348361c7a4f645b7d62f71c470c45dd8c6` |

The evidence note identifies all seven implementation files and the reused
independent fixture authors. Its hashes identify the tested uncommitted bytes;
an earlier checkout commit is not a substitute for those identities.

## 1. Contract review before implementation

The full guide was read and cleared before the producer's API-ready notice.
The earlier [job contract](CAPTURE_JOB_CONTRACT.md), its complete independent
[composition review](CAPTURE_JOB_REVIEW.md), the accepted public job API and
independent job fixtures supplied the existing behavior that composition had
to preserve. The current calibration scope remains authoritative.

One preliminary composition question concerned the number of retained selected
roots. Calling the ordinary job reader once during upfront study admission and
again for every execution would add unnecessary root records. The final guide
requires upfront job reads confined under the **already selected study root**.
Execution then selects each job's own root through the existing job core. This
clarification was resolved before implementation; it was not an observed failing
producer test.

The guide also makes the admission boundary precise. Every original job file,
its expected byte hash, exact shape, declared ID, common declared corpus hash,
and cumulative work are checked before any artifact work. Each job subsequently
admits its own policy and corpus metadata before that job's artifacts. A later
bad policy can therefore follow an earlier job's computation. It must raise an
error without returning or publishing a partial study. The acceptance suite
tests that exact distinction.

The schema is explicitly a shape schema. Source inspection confirmed the exact
required fields, literals, local ranges and portable path definitions. Runtime
must additionally enforce exact built-in types, original-byte parsing, per-field
uniqueness, real file confinement, expected identities, cross-file agreements,
work products and snapshots. This review does not claim that a generic schema
validator establishes those runtime properties.

## 2. Composition invariants and observed acceptance

### Original bytes bind work before dependencies

The study accepts one through eight ordered job bindings. IDs, case-folded paths
and expected job hashes are independently unique. Different locators may reach
identical corpus copies, but each job must fully audit the bytes it uses.

The tests observe all upfront job reads before the first private job invocation.
Each job is read exactly twice in the ordinary path: once for study admission
and once by the bound job core. Every private call receives the original expected
hash and the same snapshot object. A trap verifies that the study never falls
back to the unbound public job call.

A controlled change to the second job after the first job completes is rejected
on that second job's consumed-byte hash, before its corpus or policy reader is
entered. This is the decisive check against an after-the-work hash comparison.
Other early rejection cases put an invalid hash, ID, corpus agreement, shape,
geometry or JSON document in the last job and trap every artifact/audio reader.
None of those readers is entered.

The public `run_job(path)` signature and six-source job report remain intact.
The new private core adds only optional expected-hash and shared-snapshot inputs.
Full nested job reports are retained without projection. The existing independent
job suite passed all **81 methods** after this extension, and the study suite
checks complete nested report retention, original job/policy copies, original
identities, source fields and runtime fields.

### Results remain complete and ordered

The numerical fixture uses the literal streams `[1, -1, 1, -1]` and
`[1.25, -0.75, 1.25, -0.75]`. RMS error is exactly `0.25 FS`. Its declared margin
is `0.125 FS`; bounds `0.375`, `0.25` and `0.0625 FS` independently yield pass,
inconclusive and failed job outcomes. Raw-byte and canonical decoded identities
are checked against four fixed literal SHA-256 values, not producer digests.

All **27 ordered three-job status combinations** execute actual jobs. The study
keeps their deliberately nonsorted IDs in declared order, every complete result,
and exact counts. The independent aggregation produces one pass, seven
inconclusive and nineteen failed studies. A failed job never hides an earlier or
later inconclusive result.

Whole-corpus findings remain effective. An unselected fit copy of a selected
validation stream causes split leakage and a failed study even when every pair's
numerical policy passes. An unrelated planned capture remains visible beside a
failed job. All four evaluation roles are counted; unassigned corpus evidence
keeps its inconclusive meaning. An eight-job all-fit study may pass its declared
engineering checks while reporting zero final-test jobs. The study invents no
required role set and establishes no physical protocol completeness.

The ten physical/provenance fields remain `not_established` at both study and
job levels. There is no fitting, threshold adjustment, hidden gain/delay,
resampling, channel reassignment or generated evidence.

### Original policies survive the extra envelope

A separate three-channel fixture declares 192 spectral criteria. Its compact
policy bytes fit the 65,536-byte input limit while the formatted equivalent
exceeds it. The acceptance hook observes those exact original compact bytes at
`evaluate_policy`; the retained policy digest agrees with the original buffer.
The study must not canonicalize a parsed policy and use that new serialization
as an input. This probe asserts byte preservation and does not require all
spectral quantities to be defined or the large policy to pass numerically.

### Every earlier observation survives until return

The shared snapshot object retains original study/job/index/policy/manifest/
artifact observations and source files through all constituent jobs and final
study verification. Each job still performs fresh whole-corpus artifact/audio
checks and its two selected window reads; previous audit output is not a cache.

Controlled mutations after the final job's own return are rejected for nine
input categories: study, first job, first policy, index, both selected manifests,
selected audio, unselected audio and unselected support. An earlier policy
changed between jobs is also rejected. Same-byte leaf replacement and parent
replacement are rejected; unrelated sibling creation remains admissible.

Every one of the seven source modules is changed in a **temporary copied source
tree**, both after job one and after the final job. All fourteen subprocess
probes reject and explicitly assert that the intended mutation boundary was
reached. No repository source is edited for a fault probe. Source/runtime
disagreement and returned job/corpus identity disagreement are separately
rejected through controlled observations.

These checks retain quiescent archive/source identity. They are not an
adversarial filesystem sandbox, a code signature or loaded-memory attestation.

## 3. Independent resource derivation

The guide counts work on one side of each comparison. For jobs with channel
count `C`, frame count `N` and frequency count `K`, the limits are:

| Quantity | Bound | Acceptance evidence |
| --- | ---: | --- |
| Jobs | 8 | Eight actual completed jobs; zero and nine reject. |
| Sum of `C * N` | 8,388,608 | Eight valid maximum-window job headers reach the execution sentinel; reduced real-work bounds accept equality and reject one less. |
| Sum of `C * N * K` | 33,554,432 | Two valid headers of 16,777,216 terms each reach the sentinel; one extra term rejects before any core execution. Empty frequency lists contribute zero. |
| Original study/job bytes | 65,536 each | Actual padded documents at the boundary execute; one additional byte rejects. |
| Shared leaf records | 3,000 | Bounds apply before appending; an actual maximal reference layout remains within the independently derived ordinary bound. |
| Shared selected roots | 64 | Bounds apply before appending; ordinary derivation is 58. |
| Final/growing report | 16 MiB; 1,048,576 nodes; depth 40; magnitude `4e18` | Source guards inspected; byte/node/depth checks exercised at independently measured reduced equality and excess boundaries. |

The ordinary maximum leaf count, without deduplicating repeated observations, is:

`2 + 8 + 8 * (6 + 1 + 1 + 1 + 64 + 256) = 2,642`.

The first two records are study and own source; eight are upfront job reads.
Each bound job contributes six sources, job, index, policy, up to 64 manifests
and 256 artifact references. Selected roots are:

`2 + 8 * (6 + 1) = 58`.

The actual reference-layout test executes all eight jobs over 64 manifests and
256 artifact references, retains all eight full reports, and checks snapshot
counts against those derived upper bounds. Its files and audio windows are
deliberately tiny. It does not execute maximum declared artifact bytes, audio
bytes or spectral calculations.

After each job, the growing report is checked before continuing. A reduced cap
of one byte proves rejection after the first complete job, with no second job,
no truncated report, no output file and no stdout. Byte/node/depth equality and
one-below-limit checks use the reviewer's independent serializer and value-node/
container-depth traversal. This does not prove that every admissible eight-job
archive fits the report envelope; an excessive complete result must reject.

## 4. Filesystem, CLI and publication boundary

The suite executes native Linux symlink, hardlink and FIFO cases. A linked study
leaf, selected root, job leaf or job parent rejects before execution. An ordinary
alias above the real selected root remains valid. Nonregular inputs reject
without waiting. An actual opened study descriptor is closed when wrapping it
raises either `OSError` or cancellation. Native capability cases use explicit
skips if their host cannot create the required object; there were **zero skips**
in the final run.

Four actual study CLI processes exercise all three outcome exits and a foreign
working directory with Unicode archive/output names and an ASCII-configured
text environment. Reports remain canonical UTF-8 with LF and equal the complete
new output file. Fourteen additional Python subprocesses exercise source
mutation; these are API fault probes, not additional CLI runs.

In-process CLI tests cover exact argument types, help, missing/unknown/duplicate/
abbreviated/empty options, override attempts, text-only streams and all outcome
codes. Input errors produce no report. Existing files, directories, input paths,
hardlink aliases and dangling output links survive no-clobber rejection.
Missing parents are not created; a destination created at the publication race
point wins unchanged. Successful publication precedes stdout.

A controlled cleanup failure after actual publication preserves the complete
published file and reports the failure with empty stdout. Later stdout failure
also preserves that file. Short stdout delivery can leave partial bytes and is
reported as failure. Unavailable stderr/help streams never yield success.
Cancellation propagates without publication or a fabricated report.

## 5. Executed qualification and next integration step

From `/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ`, using Python 3.12.14 on
Linux x86_64:

```sh
python3 -B tests/test_capture_study.py
python3 -B tests/test_capture_job.py
```

The final study file at the hash above passed **61 methods in 7.879 seconds**;
the existing job suite passed **81 methods in 4.112 seconds**. Both had zero
failures, errors and skips. The original 58-method study suite also passed;
the additions made source phases and native capability accounting explicit.
The evidence note retains the exact run history and fixture-authoring changes.
No production repair or weakened expected behavior was needed.

Root should integrate the tests into discovery, qualify the coherent source
snapshot with its normal build/install checks, retain all seven source files in
packaging, update the shared status/next steps/log/ledger, and commit/push under
the owner's standing authorization. A later synthetic demo/replay should retain
original study/job/policy/corpus/manifest/artifact bytes and every valid failed or
inconclusive result; report dictionaries cannot recreate original whitespace.

This worker did not execute native Windows/macOS acceptance, installed-prefix
qualification, hosted CI, full maximum scans, maximum spectral work, a maximum
16 MiB report, or hostile-filesystem stress. Physical acquisition, permissions,
specimen identity, reviewed metrology, holdout chronology, listening acceptance
and instrument fidelity remain separate open gates.
