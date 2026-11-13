# Assignment 22 — independent file-job contract review

**Actual worker:** `/root/cal_w4_a22`, calibration wave 4, assignment 22,
2026-11-13. This is one newly dispatched independent review, not a reuse or
renaming of an earlier worker. The launch wrapper initially reported an aborted
response, but this actual child started, sent its identity to root and completed
the work recorded here.

**Outcome:** cleared the root-revised `capture-job-v1` contract for assignment
25 implementation. One real composition blocker was reported early and resolved
in root-owned contract edits. No producer implementation or job acceptance is
claimed. See [the complete review](../../CAPTURE_JOB_REVIEW.md).

## Ownership and observed checkout

Working directory: `/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ`.
Owned only:

- `docs/CAPTURE_JOB_REVIEW.md`
- `docs/development/2026-11-13-calibration/22-job-contract-review.md`

Read `AGENTS.md` and the full job schema and initial/final job contracts. Read
the complete frozen audio, corpus and comparison contracts and examined relevant
current JSON, publication, metadata admission, graph, audio inspection and
policy APIs. Existing author checks were treated as author evidence, not counted
as this reviewer's independent checks. This worker did not reread the entire
500-page atlas; that task belongs to the earlier documented full-reading waves.

Initially observed local `HEAD` was
`8864c051d19556e37dffcd7366fd859606958bc3`, tree
`e4f56a7c722dcad4eda9269d907715b8526dd8cd`; locally recorded `origin/main` was
`5b8e2419d23fe27c51709d717812060eafd44dcc`. Root continued integrating and
committing concurrent work during review. A later read observed local
`091ad20c632209053c337a06544f82a829644800`, tree
`8679418135946193b2b989a89e60ac6099b00125`, with the same locally recorded remote
tracking ref. These observations are not a fresh remote verification. New
job/policy work was uncommitted during the probes, so the exact file identities
below, rather than either commit alone, identify reviewed content.

No production/shared/schema/contract file was edited by this worker. No fetch,
commit, push, branch change, install or additional agent dispatch was performed.

## Finding, repair and independent recheck

Initial contract SHA-256:
`11f80a02597707d12423f6a02ff8f8574068827c17ce4fa62baa9e1abb76e012`.

The proposed sequence could combine separate index admission, public structural
audit and public full audit: three index reads and an unbound later read capable
of entering work above the wrapper's 64/256 limits before a post-hoc hash check.
The reviewer reported this blocker and proposed a shared private core consuming
the exact preflighted parsed metadata and observed identities, with unchanged
public corpus behavior. The reviewer also required selected context to bind the
bytes actually parsed and a complete final snapshot set rather than a root-only
or selected-pair-only check.

Root accepted and edited section 4. The reviewer read the actual revised text:
it selects the shared prepared-metadata core as primary, tightly binds any
alternative rereads before work, reuses selected metadata, and explicitly
retains/rechecks job/index/policy, all manifests, **all audited artifacts**, their
confined parent chains and six sources. The final reviewed contract is
`ed0b34cbd45d737ea35b33d3049d1b8884f8f665d4f42caeb1e1406466217b84`;
the schema remained unchanged. No remaining implementation-blocking contradiction
was identified at that exact pair of identities.

Root separately integrated audio malformed-field precedence and corpus descriptor
ownership repairs while this review ran. Their final file hashes are recorded
below. Those repairs did not change the job's public dependency meanings; this
review does not claim independent acceptance of those separate fixes.

## Exact independently executed work

Environment: Linux, Python **3.12.14**, already installed **jsonschema 4.26.0**.
Two inline `python3 -B - <<'PY'` probes ran with no bytecode files or retained
sample/report artifacts. All reported assertions completed successfully.

1. Validate the actual schema against Draft 2020-12; extract the literal example
   from the actual contract; apply **189 independently authored shape cases**:
   30 expected valid, 159 expected invalid. Cover every missing/extra root/nested
   field; fixed literals; IDs/hashes; path grammar and all size/component
   boundaries; scalar/range/Boolean errors; numeric frequency duplicates;
   Hann and start boundaries.
2. Demonstrate **seven intentional semantic-only schema admissions**: two
   integer-token distinctions, frequency ordering, relative Nyquist, window sum,
   work products and duration. The runtime must reject these where applicable.
3. Independently pack three literal float32 vectors, reconstruct the specified
   decoded preimages and compare **all six hashes** with values extracted from
   the contract table. No production audio/digest helper supplied expectations.
4. Use exact `Fraction` arithmetic for **four interval decisions** and the two
   quarter/half-offset pointwise bias/RMS/max derivations. Enumerate all **nine
   status combinations**. Recompute the **3,708-edge** conservative bound,
   sample/work boundaries, manifest aggregate implication and numeric envelope.
5. Hand-author a **structural** 16-channel/64-frequency comparison scaffold and
   256-criterion policy; exercise existing validation/parsing/evaluation and
   canonical serialization solely to check composition budgets. Comparison:
   **43,809 nodes**, depth 6, **1,557,872 canonical bytes**. Policy: **3,921 nodes**,
   **65,437 original compact bytes**, **104,893 canonical bytes**. Evaluation:
   **50,220 nodes**, depth 7, **1,852,283 bytes**; nested evaluation: **50,221 nodes**,
   depth 8, **1,980,305 bytes**. These are not measured audio or a fabricated
   successful job. The larger canonical policy copy makes preserving the
   original admitted policy bytes an explicit implementation requirement.
6. Run **nine common-helper boundary cases**: report nodes at/above 1,048,576,
   container depth 32/33, finite magnitudes at/above `4e18`, infinity, and the
   stricter `2e18` comparison bound. All behaved as required. The wrapper must
   still apply its full report guard and 16 MiB byte cap.
7. Hash review inputs before and after each probe to verify stable contents
   during execution; read exact source files, root repair wording and identities.
   Check whitespace on the two owned notes after writing them.

These counts are **189 schema cases, seven documented schema limitations, six
hash comparisons, four interval examples, two offset derivations, nine status
combinations and nine guard-boundary cases**. They must not be added to the
project's implemented-job test-method count. Structural profiling is separately
identified above.

## Final reviewed input identities

| Input | SHA-256 |
| --- | --- |
| Job contract | `ed0b34cbd45d737ea35b33d3049d1b8884f8f665d4f42caeb1e1406466217b84` |
| Job schema | `af1046b9d50d18e6da553805972591a2cf330403b8196ca376a577bfdb7afa2a` |
| Audio contract | `1766ed93f26eb5fa4db21397f6dd74002970ec567e7ff4541536911598d026cc` |
| Corpus contract | `a524a38eedf8b18decd39845df844cc86ad98f8409216523e9917bb372bfb8b2` |
| Comparison contract | `4ec3037aa0588528fe3c9e520d099cc48a82d78135fc86bd3851c2667860750c` |
| `capture_audio.py` | `c02c1a5e6023e0278dddca09ad1841541fbb0ece66d7950198f93be7846dc7ac` |
| `capture_corpus.py` | `ba39a47499df0df837b71d744f773bfbefe14d0eb1a0c471a373900b6c284e7b` |
| `capture_common.py` | `e06dd82e37dd178863af61aa66bee877da1fc7e498a47b729e060215ca79c3f2` |
| `compare_capture.py` | `220a593499539db5f1e635db2eb15ba3c0aa7c6d001c80407fbffe93f75a9a0a` |
| Unchanged `validate_capture.py` | `a872e069ba9744f6f8078f87b78ea300df1ee28aec58e104859580cdc09877af` |

The first probe hashed all ten entries before/after. The second structural probe
also bound its contract, schema, comparison and common-helper inputs before/after.
No file changed within either observed probe interval.

## Handoff and limits

Assignment 25 can implement the cleared contract, including the minimal shared
private corpus core and complete job snapshot set. Retain original policy bytes,
never reserialize them for evaluation, and preserve every full subordinate
report. Assignment 26 must independently qualify real archives, ordered early
rejection, all context/role/evidence cases, whole-corpus outcomes, identity races,
report limits and exact no-clobber CLI behavior. Rerun existing independent
corpus qualification after the shared-core refactor.

No `capture_job` producer, job CLI, actual file-comparison archive, publication
race, full replay, native Windows/macOS execution or hosted workflow was executed
by this assignment. No source-memory attestation, acquired specimen, physical
calibration, permission, listening outcome or instrument fidelity is established.
Root owns shared ledger/handoff updates, coherent integration and authorized
commit/push. Future agents must preserve these distinctions and the standing
repository workflow.
