# Reference refinement completion gate review

## Decision and exact evidence

A53 found no blocking defect in the published refinement checker's strict
record-consistency gate. The source review covers identity, six assignments per
wave, accepted note bytes and structure, safe paths, and progress versus strict
semantics. It does **not** certify session completion: the one executed A53 check
used an immutable copy of the actual partial ledger at **2026-11-14 22:29:22 UTC**.
That snapshot contains **54 recorded identities, 51 accepted notes and three
running records**, with zero consistency errors and `completion_valid: false`.
The live [manifest](../development/2026-11-14-reference-refinement/assignments.json)
and [checkpoint](../development/2026-11-14-reference-refinement/CHECKPOINT.md)
own subsequent progress; this dated observation does not advance with them.

The reviewed [checker](../../tools/check_refinement_session.py) and its
[existing tests](../../tests/test_refinement_session.py) match published source
`0881d1f4c5a26ce9c75dda7a3adde46382e5ab6b`, tree
`f8144b771cda1264a8788f8297f5bfec999f4a08`. Their SHA-256 values are respectively
`5bd5f420bd8bbad37f7e469b94f9695cd38106d7de8c2c5d9cdb8a2faf453e42` and
`33c5e845971af9396a50a03c9550af8a9e93df59086b34fe19f92046b9522df7`.
They also match the retained [A39 author evidence](../development/2026-11-14-reference-refinement/reports/A39-refinement-ledger-checker.json).
A49's [original CTest log](../development/2026-11-14-reference-refinement/reports/A49-LastTest.log)
records all twenty synthetic checker methods passing, with 1.430 seconds inside
Python and 1.57 seconds for the registered CTest entry, within its single
157/157 full run. A53 inspected that evidence and the test bodies; no synthetic
suite, CTest run, product build or GUI session was repeated.

The [snapshot audit](../development/2026-11-14-reference-refinement/reports/A53-snapshot-audit.json)
retains the exact command, environment, original and copied source identities,
all 51 note identities, and unchanged-before/after snapshot verification. The
[raw progress JSON](../development/2026-11-14-reference-refinement/reports/A53-in-progress.json)
has SHA-256 `a8b0becfea4535fd7c290002458ff7e56977b37f0f53a9003f8a6e3c379b984a`.
The [original manifest bytes](../development/2026-11-14-reference-refinement/reports/A53-manifest-snapshot.json)
have SHA-256 `b057202555602d1904bcd93e358f2a6a1f2d0482f097d6523001e6877978c589`.
This retained copy is historical audit input, not the live assignment ledger.

| Wave group at the snapshot | Recorded | Accepted | Running |
| --- | ---: | ---: | ---: |
| Waves 1–8, each wave | 6 | 6 | 0 |
| Wave 9, A49–A54 | 6 | 3 | 3 |
| Wave 10, A55–A60 | 0 | 0 | 0 |
| Entire session | 54 | 51 | 3 |

A52–A54 were running. A55–A60 were absent, not planned rows credited as work.
All 51 accepted notes passed the declared hash and structural floor. The exact
sorted note-record aggregate is
`edf05d1f03c8048738895090ae671bd5d16cda3830b7b525dd67eb203c5e71f3`.

## What the gate establishes

The checker fixes this session's directory and full starting commit
`8bd999efc13e309b932e6ac41d72ceb7b9b80a5f`; it does not discover or add rows from
other manifests. Exact schema members, integer values and bounded text prevent
boolean/float substitutions, extra completion flags and malformed placeholder
records. Duplicate JSON members are rejected before field checks.

Strict success requires exactly A01–A60, sixty distinct canonical
`/root/wNN_aNN_name` strings, and correct wave/ID mappings. The formula
`(ID - 1) // 6 + 1` assigns each consecutive group of six to one of ten waves.
Duplicate IDs, identities or note paths are errors. Strict completion also
requires sixty accepted records, sixty verified accepted notes, and exactly six
recorded and accepted entries per wave. No running row can satisfy completion.
The manifest's concurrency field must be integer four, but the checker has no
collaboration-service history with which to prove actual concurrency or dispatch.

Each accepted row requires scope, result, a session-local `Axx-name.md` path and
the lowercase SHA-256 of that note's exact raw bytes. LF-normalized text is used
only for narrative analysis; the digest still distinguishes CRLF from LF.
The recorded note aggregate includes sorted note paths, statuses, hashes, sizes
and structural results. Counts and `accepted_waves` describe declared rows;
readers must examine the status and errors before treating them as valid records.

Path admission rejects traversal, absolute/drive syntax, alternate separators,
control characters, wrong session or note directories, wrong assignment names,
symlink/reparse components, and nonregular leaves. Manifest reads are bounded to
256 KiB and note reads to 128 KiB. Reads compare file identity, size and relevant
metadata before/open/after, request no-follow/nonblocking flags when available,
and reject observed changes. The existing tests include FIFOs, oversized files,
symlinked parents, Windows reparse metadata, open/read mutations and descriptor
cleanup. These are practical file-admission protections, not an atomic snapshot
of the entire ledger or a guarantee against arbitrary hostile filesystem races.
Final qualification should use a frozen checkout or an immutable copied input set.

## Existing adversarial coverage and its limits

| Reviewed obligation | Existing evidence in the twenty-method suite |
| --- | --- |
| Strict versus progress behavior | Partial strict CLI rejection; explicit progress success with completion false; complete synthetic sixty-record strict success; progress remains non-completing even for that complete fixture. |
| This session's identity and six-per-wave accounting | Exact schema and starting identity; row types/statuses; duplicate and malformed IDs, agents and waves; other sessions and unassigned notes contribute no workers. |
| Exact note content and narrative structure | Altered bytes and CRLF identity; required text and digest syntax; missing accepted notes; optional running evidence; comments, fences, indented code, repetition and placeholder rejection. |
| Bounded parsing and file admission | Duplicate JSON members, invalid encoding/depth/numbers; exact size boundaries; unsafe paths; directories, symlinks, reparse metadata, FIFOs, observed read changes and failed descriptor wrapping. |
| Result provenance | Exact checker/manifest/note/aggregate hashes; input immutability; explicit false dispatch/execution/readiness attestations. |

The suite's synthetic identities are confined to private temporary fixtures;
its successful sixty-row fixture never enters the real manifest. The common
record-validation path supplies both modes. A49's passing synthetic suite
qualifies the checker implementation at its frozen source, while the final
strict command must separately inspect the actual completed ledger.

The narrative floor is **100 regex word tokens and 40 distinct tokens**, with
HTML comments and directly detected fenced/indented code excluded. It is not a
complete Markdown semantic parser, a prose-quality score or a substitute for
reviewing the assigned work. The snapshot's minimum was 197 narrative and 154
distinct tokens. Previously accepted A07–A11 are below 300 narrative tokens but
meet the published structural contract. A task's stronger note requirement,
including A53's minimum 300 narrative words, remains the integrator's separate
acceptance obligation. Do not pad or silently rehash earlier accepted notes to
manufacture a stronger historical claim.

Different canonical paths and recorded names do not prove different people,
independent authorship or unique substantive content. A hash binds retained
bytes, not the truth of the claims within them. This checker cannot establish
actual dispatch, substantive acceptance, test execution, publication, visual
equality, product readiness or physical/model fidelity. It intentionally emits
those limits. R4, scanner G5, real devices, hosts, accessibility, deadlines,
signing, asset rights and literal 1:1 reference equality keep their own evidence
gates under the [complete project plan](../PLAN.md).

## Strict Linux CI integration

At this review's source, [.github/workflows/ci.yml](../../.github/workflows/ci.yml)
requires the historical interface checker in Linux Release and retains
`ci-logs/` through its existing artifact step. It does not yet run the new real
refinement completion check. A55 owns that additive integration; A53 changed
neither workflow nor checker. Retain the historical interface command and all
other sessions' manifests unchanged.

After the sixty actual outcomes have been accepted, add a separate required
Linux Release step after the Release tests and before artifact upload:

```yaml
- name: Verify the completed refinement session
  if: runner.os == 'Linux'
  run: |
    set -o pipefail
    python tools/check_refinement_session.py --repo . --json | tee ci-logs/refinement-session-completion.json
```

The command deliberately omits `--in-progress`. Preserve `pipefail` so `tee`
cannot hide the checker's nonzero exit. Do not add `continue-on-error`, a fallback
progress command or a `|| true` override. Keep the existing artifact retention
on success and failure; if an earlier job step fails or a run is cancelled, an
absent or skipped checker is not a pass. Keep JSON stdout separate from any
stderr diagnostics. Retain the actual source revision and inspect this step's
observed result on the final published commit before claiming hosted closure.
An upload succeeding proves neither the gate ran nor the contents passed.

For local closure, root runs the existing strict CLI from the repository root
against the final accepted records and retains its JSON and exit code. Require
`mode: strict_completion`, `status: passed`, both validity booleans true, zero
errors, sixty accepted/verified/distinct identities and six accepted entries in
each wave. Compare the checker, manifest and note identities with the published
records. A progress command exits zero for a consistent partial ledger but
always reports completion false; it cannot be the closure artifact.

## Recovery without weakening the gate

| Observation | Required response |
| --- | --- |
| `completion_count` or `completion_status` | Finish and review real remaining assignments. Preserve incomplete reports; no copied historical identity, planned row or premature accepted status supplies missing work. |
| Session, schema, identity or wave error | Reconcile the exact actual dispatch/acceptance record through root. Preserve other session ledgers and the canonical starting identity. |
| `note_hash_mismatch` | Inspect the byte diff, including line endings. Restore the exact accepted bytes or review an intentional amendment before root updates its digest. Do not automatically bless changed bytes. |
| `note_substance` or missing evidence | Obtain the actual substantive result and source/check/limit narrative. Numeric padding or copied notes do not establish acceptance. |
| Unsafe path, special file, missing input or observed concurrent change | Recover real regular files within the correct session, freeze or snapshot the input set, then rerun the affected command. Preserve its original error rather than relaxing path or size checks. |
| Cancelled/setup-blocked/skipped CI step | Retain that actual state and arrange the required gate on the exact final revision. A request or dispatch is not execution evidence. |

After all new notes and documentation are final, root runs the affected
repository-integrity gate and the real strict refinement check, then follows the
authorized source/publication workflow. A49's frozen documentation identity does
not cover later notes. A changed manifest, accepted note or checker invalidates
the corresponding previous completion input identity and requires a new strict
result. No second full product build/test campaign is justified by this review
alone; reopen an affected implementation gate only for a changed relevant source
or a concrete defect.
