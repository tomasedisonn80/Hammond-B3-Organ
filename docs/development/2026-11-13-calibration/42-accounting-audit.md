# Assignment 42 — independent accounting and handoff audit

**Actual assignment:** `/root/cal_w7_a42`, logical calibration wave 7,
assignment 42. This is one separately dispatched audit assignment. It does not
recount an earlier reader, producer, reviewer or session worker.

**Result:** the retained calibration records passed both dated CLI checks;
independent recount and twelve focused private cases produced the expected
outcomes. No checker repair is indicated by this audit. Documentation refreshes
were sent to root, which confirmed its accepted checkpoint already updates the
hosted and publication pointers. Final sixty-assignment completion remains open.

## Ownership and work performed

Only these repository files were created:

- `docs/reviews/CALIBRATION_ACCOUNTING_AUDIT.md`
- `docs/development/2026-11-13-calibration/42-accounting-audit.md`

Root owns acceptance, the shared manifest and current documents, coherent gates,
Git integration and publication. This worker edited no checker, test, schema,
runtime, CMake file, shared ledger or other-session record, and performed no Git
mutation, fetch, commit or push. Private snapshot/probe/harness files reside in
scratch outside the repository.

Read the complete current `AGENTS.md`, calibration scope/session README, checker,
checker contract and all 27 maintained checker acceptance methods. Read the
calibration status/next-step/handoff context and the consolidated atlas review.
Inspected the original ledger's counting rules and five other manifest formats
only for history separation. Read the later extension notes for overlapping
owned paths and assignment 39's retained hosted review. This assignment does not
claim another full 500-page PDF reading, complete re-audit of all historic notes,
fresh hosted log retrieval or execution of other workers' reported gates.

The full independent result is in
[CALIBRATION_ACCOUNTING_AUDIT.md](../../reviews/CALIBRATION_ACCOUNTING_AUDIT.md).
At this handoff that file is 14,949 bytes, SHA-256
`758320a71954effb36f17c41fa64ea340a69589b91288776b5443af1255567f0`.

## Observed accounting snapshots

The initial capture was made at **2026-11-14T00:21:10.476773+00:00**.
Manifest: 22,415 bytes, SHA-256
`e5b8715569d95e617272c429d580f8f9925860f71a090a82d9263383b2b860d1`.
It contains 36 complete, 4 running and 20 planned records; 40 distinct canonical
identities; and six completed waves. Running assignments are 37–40, planned are
41–60. The captured manifest remained stable during the copy. The private
snapshot includes all 100 unique completed owned paths and the source/documents
used for this audit.

The initial HEAD was `955fc4c41f74ada094f14fbaf386c943811e9050`, tree
`70956d0f0e125d57abfbf1aed56460c067f8ef28`; the locally fetched `origin/main`
was `183fc9e2a5e1530787deb9a6bb823e8f6ef61c2e`, tree
`c2aee4e8ceb9bb945b255bb67388a7d6bab9f3f2`. The live records included accepted
work beyond that HEAD, so the explicit manifest hash is the snapshot identity.

The follow-up was independently observed at
**2026-11-14T00:24:22.634815+00:00**. Manifest: 22,842 bytes, SHA-256
`9abf69fd379d79fcb82e39d2a6683ab661e534d4000c1287fd5dab834eaf8c5e`.
It contains **39 complete, 3 running and 18 planned records**, with 42 distinct
canonical identities and six completed waves. Running assignments are 40–42;
planned assignments are 43–60. HEAD was
`16d72e1b351e5cdf1730e90645a6ea37144d1be7`, tree
`5619bbb018830e071bc2ce45af84984cdd16bfc1`. The live manifest was unchanged
through the actual expected-complete-39 CLI execution, which exited 0 with no
errors.

Root had separately reported actual dispatch of 1–42. It explained the first
snapshot's registration of only 40 workers as ordinary concurrent registration
and acceptance lag. The follow-up corroborates the updated retained records.
The dispatch history remains a parent orchestration fact; neither the JSON
records nor this checker independently attest historical launches. Both reports
retain `external_dispatch_attested: false` and physical fidelity
`not_established`. Root continued accepting/dispatching work after these
observations; a later live count need not equal a historical checkpoint.

## Commands, outcomes and bounded coverage

Work took place in `/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ`.
For the initial CLI the working directory was the frozen snapshot
`/workspace/scratch/c9f3ead4c910/a42-accounting-snapshot`:

```sh
python3 -B tools/check_calibration_session.py --repo /workspace/scratch/c9f3ead4c910/a42-accounting-snapshot --expected-complete 36 --json
```

Result: exit 0, 36/4/20, 40 canonical identities, six complete waves, zero errors.
The isolated audit harness was then actually executed:

```sh
python3 -B /workspace/scratch/c9f3ead4c910/a42-accounting-audit.py
```

It uses two real checker CLI invocations and ten in-process private-case checks.
Its 12-case result has **zero unexpected failures**. The cases cover expected
36 versus intentionally invalid expected 60, a ready running note, a separate
older sixty-row manifest, duplicate/wrong-session worker identities, wrong wave,
planned identity claims, wrong baseline, missing completed note/owned file and
replacement by a foreign-session manifest. The review retains every case and
observed outcome. The private manifest/files were restored after probes; the
immutable snapshot manifest was unchanged. The checker source remained equal to
the inspected version.

The later working checkout was checked with expected-complete 39 and `--json`;
its raw manifest and checker result were retained separately. This fourth actual
checker CLI invocation in the audit passed with 39/3/18 and 42 identities.
The 27 maintained methods were read but not rerun: the selected cases resolve
the concrete count/state/history risks without repeating the entire earlier
acceptance campaign. No native build, maximum resource test, performance gate,
CI run or physical experiment is credited to this assignment.

Independent recount verified ordered slots, exact six-member wave formula,
unique canonical identities, planned null fields, completed identity tokens,
substantive UTF-8 notes and owned-file existence. The smallest completed trimmed
note is 4,098 characters and the largest note is 19,034 bytes. File existence
and minimum length do not establish authorship or correctness of all note claims.

Read-only `git rev-parse` comparisons verified exact tree equality for local and
published source pairs `fd0fb58`/`340903a`, `1aef684`/`783363f` and
`12fc345`/`955fc4c`. Read-only `git merge-base --is-ancestor` verified all three
published commits are ancestors of the observed `183fc9e` ref. Their complete
identities and qualified 99-suite/16-suite report references are in the review.

Two read-only document lookups initially used nonexistent guessed handoff/review
names. `rg --files` located `docs/CALIBRATION_HANDOFF.md` and
`docs/reviews/CALIBRATION_HOSTED_RECHECK.md`, which were then read successfully.
No code or test failure followed from those path lookups. The expected-complete-60
and malformed-input failures in the private harness are intended rejection
outcomes, not concealed failed acceptance runs.

## Exact inspected source and evidence identities

These first-snapshot hashes identify the bytes actually reviewed, even as root
updates live documentation. The maintained source and contract are durable
repository inputs; scratch hashes identify this assignment's temporary evidence.

| Input or retained scratch evidence | SHA-256 |
| --- | --- |
| `tools/check_calibration_session.py` | `f5d53fe357406456c1335b55ccab9e6db885c68b055b12c6d71138bf73e7fb19` |
| `tests/test_calibration_session_records.py` | `72959bf61f4c1c1effecb6b3daab1c7889300cbd6a569c587cca4e2fed59193b` |
| `docs/CALIBRATION_SESSION_CHECKS.md` | `d8eb93bf2e6d2e3fecccab80eaa4ef190c5299ceb53f85884367bd1de3d08b5f` |
| `AGENTS.md` | `d04aac1baaf5503bc87ffaa1bfe20ac994160f3834cc2cd0e8deda6397c822ad` |
| `docs/STATUS.md` | `4e30f5bdd3980e9438e29c0f61b32e6b7b45754f3bcaf7d3a11cb2fa1736dde6` |
| `docs/NEXT_STEPS.md` | `a43b2274221bbe860a9e51de5c3f9a3fcf3e0abe36b0e1340d9aa9370bd6d9c3` |
| `docs/CALIBRATION_HANDOFF.md` | `0995eeb137a4b5c3b5c046a2ca2e008c0f7f1466f186724bbda2e43935933fbf` |
| `docs/CALIBRATION_SCOPE.md` | `a6d9f05dd5cf24de297210e65597e15d02cd2197f422b9da2889c0211643bb35` |
| Session `README.md` | `9674444dbd259b1a17296be8f2b97620f191a6a5b291c04c37884c2cfc873a4d` |
| Scratch `a42-accounting-audit.py` | `c69655e2b8d108c4fe87a3503ae8fa4a226954f34fcf69e724744763f63c91d2` |
| Scratch `a42-accounting-audit-results.json` | `6169c131ccb48e0ebbc0bd28e6c68dca513eed0208e328ecc58909543cd41b2e` |
| Scratch `a42-history-comparison.json` | `84b45b15388643830c5265f3dd87a21c85d69d8860e7b4598c28cd24b53b53f8` |
| Scratch `a42-followup-observation.json` | `57c8fd622d7f7ca67be79f9cd80f16b14414f79e039f86bdab0210aeeb2dba7e` |

The other-session manifests below were separately read after the initial
snapshot. Their observed row/identity counts and zero overlap with the initial
40 calibration identities are in the review. These hashes establish which
records were compared; they do not independently attest those sessions' work.

| Other session manifest | SHA-256 |
| --- | --- |
| `2026-11-13-continuation/assignments.json` | `3e60721d3743321aae88310fdddd5c894c81321d17af6093e2df81264c2e15cf` |
| `2026-11-13-next-phases/assignments.json` | `fd73ece2197a29cb15e0dfc83d0081e2950cc6fd7e7423dbeea86dd8b5567878` |
| `2026-11-13-pedals/assignments.json` | `c77121b23bed9400ae82be13d778ef7a59b60a6de66d133c4e926d620af6ed8f` |
| `2026-11-13-rotary/assignments.json` | `ed7a1516aa1c5f7251e2e846ecda600a42994ed4acf24ba8cb14dfa353d20d8f` |
| `2026-11-13-scanner/assignments.json` | `cb0ebabdca6b1eb96269f011abd445923e75a5ccfab302a0afa68149768b7bdf` |

## Findings delivered and next integration action

Recommend immediate post-dispatch registration, while keeping acceptance a
separate substantive review. Ready files must not automatically promote running
rows. The first lag is documented and the follow-up is consistent with root's
explanation; it is not an accusation that the actual dispatch was missing.

Recommend updating the current hosted pointer to assignment 39's retained
`955fc4c` result, preserving the earlier `779fb6e` failures and distinguishing the
new Windows demo-fixture failure from resolved earlier platform cases. Root
confirmed `16d72e1` already updates STATUS, handoff and the development log and
separates published `955fc4c` from later replay/installation qualification.

Recommend labeling the session README's original 57 corpus / 60 audio method
totals as historical. The frozen STATUS later records 58 corpus / 63 audio,
with two audio capability skips. Root subsequently reported the concurrent
`183fc9e` addition makes the integrated corpus total 59 and said its new immutable
103-suite gate was running. Those source-qualified integration updates do not
retroactively change the frozen counts, and no completed 103-suite result is
claimed here.

The future workflow already persists in AGENTS and the handoff: read current
state and ownership, continue the next dependency-ready phase, preserve other
tracks and evidence limits, record meaningful commands/results/failures, update
shared current documents, then have the integrator commit/push completed
authorized work and verify the fetched remote. Integrate concurrent advances
without force-pushing. The current sixty-assignment requirement belongs to this
session; it is not a mandatory sixty-worker expansion of every future small task.

Root should review these two owned files, accept assignment 42 when satisfied,
and include them with its next coherent checkpoint. The later observed ledger
still had 21 unaccepted results. The final successful
`python3 tools/check_calibration_session.py --repo . --expected-complete 60 --json`
gate must wait until all sixty actual assignments have accepted substantive
results. This note's private negative probe does not meet that gate. Physical
measurement, calibration, rights, holdout history and instrument fidelity remain
separate evidence requirements.
