# Calibration accounting and continuation audit

**Reviewer:** `/root/cal_w7_a42`, assignment 42, logical wave 7.
**Scope:** retained calibration-session accounting and future-agent handoff.
**Result:** both observed checkpoints pass the existing checker. Independent
recount and twelve focused private cases found no checker defect. The later
checkpoint has **39 accepted assignments, 3 running and 18 planned**: 21 results
remain unaccepted. This is an intermediate audit, not completion of the sixty
assignments or an independent attestation of worker launches.

The [session checker contract](../CALIBRATION_SESSION_CHECKS.md),
[manifest](../development/2026-11-13-calibration/assignments.json),
[scope](../CALIBRATION_SCOPE.md) and [standing instructions](../../AGENTS.md)
define the terms used here. The exact commands and source hashes are retained in
the [assignment note](../development/2026-11-13-calibration/42-accounting-audit.md).

## Two dated observations

Root was accepting results and registering newly dispatched workers during this
audit. The first manifest was copied byte for byte into a private snapshot;
complete owned files and review inputs were also copied. Its bytes did not change
during that capture. The second observation read the later working manifest and
ran the real CLI against the live repository; the manifest remained unchanged
through that check. These checkpoints are historical observations, not a demand
that subsequent work retain the same counts.

| Observation | First frozen snapshot | Follow-up working checkpoint |
| --- | --- | --- |
| UTC | 2026-11-14T00:21:10.476773+00:00 | 2026-11-14T00:24:22.634815+00:00 |
| Manifest bytes | 22,415 | 22,842 |
| Manifest SHA-256 | `e5b8715569d95e617272c429d580f8f9925860f71a090a82d9263383b2b860d1` | `9abf69fd379d79fcb82e39d2a6683ab661e534d4000c1287fd5dab834eaf8c5e` |
| Complete | 36: assignments 1–36 | 39: assignments 1–39 |
| Running | 4: assignments 37–40 | 3: assignments 40–42 |
| Planned | 20: assignments 41–60 | 18: assignments 43–60 |
| Distinct declared canonical identities | 40 | 42 |
| Completed logical waves | 1–6 | 1–6 |
| CLI expected-complete value | 36 | 39 |
| CLI exit / errors | 0 / 0 | 0 / 0 |

The first checkout HEAD was
`955fc4c41f74ada094f14fbaf386c943811e9050`, tree
`70956d0f0e125d57abfbf1aed56460c067f8ef28`. The already-fetched `origin/main`
pointed at `183fc9e2a5e1530787deb9a6bb823e8f6ef61c2e`, tree
`c2aee4e8ceb9bb945b255bb67388a7d6bab9f3f2`. Assignment 42 read these local Git
refs; it did not fetch or publish. The first working manifest included accepted
replay work beyond that published HEAD, so HEAD alone is not its byte identity.
The follow-up HEAD was `16d72e1b351e5cdf1730e90645a6ea37144d1be7`, tree
`5619bbb018830e071bc2ce45af84984cdd16bfc1`.

Root separately reported that assignments 1–42 had actually been dispatched as
distinct workers, in ten planned logical groups of six with at most three
workers concurrent. Root explained that the first snapshot preceded registration
of 41/42 and acceptance of completed 37–39. The follow-up independently verifies
the resulting retained records. The earlier gap is registration/acceptance lag;
it does not establish that the actual launches were absent. Conversely, the
later JSON rows do not independently prove historical launches.

Both checker reports explicitly retain:

```json
{
  "scope": "retained_accounting_consistency_only",
  "external_dispatch_attested": false,
  "physical_fidelity": "not_established"
}
```

The report field `distinct_actual_agents` counts admitted canonical identity
strings in running or complete records. Its name does not change that stated
scope. No active-agent inventory was treated as historical launch evidence.

## Accounting invariants independently inspected

All 60 first-snapshot rows are ordered 1–60. Every wave is
`(assignment - 1) // 6 + 1`; each of the ten waves therefore contains six slots.
Every nonplanned row has the expected identity
`/root/cal_w{wave}_a{assignment:02d}`. The 40 recorded identities are unique.
Planned rows have null identity/note and empty ownership. The declared concurrency
limit of three is scheduling configuration; the checker does not reconstruct a
historical concurrency maximum.

All 36 completed notes exist, decode as UTF-8, contain their own exact canonical
identity token and meet the bounded substantive-note requirement. Their trimmed
lengths are at least 4,098 characters; the largest is 19,034 bytes. All 100 unique
completed owned paths were present as regular files in the frozen copy. Those
observations establish existence and identity consistency, not independent
verification of every experimental claim inside each note.

Repeated ownership of a path across accepted development stages is permitted.
The observed overlaps are `tools/compare_capture.py` in 15/20,
`tools/capture_corpus.py` in 14/25 and `tools/capture_job.py` in 25/31. The later
notes retain the accepted earlier source and explicit sequencing or release of
the added work: fixed-policy extension, shared corpus core, then bounded-study
binding. They are separate workers extending an existing module. They are not
duplicate canonical identities, and a historical ownership list is not proof
that two workers edited that path concurrently.

The [checker implementation](../../tools/check_calibration_session.py) and all
27 maintained acceptance methods were read. The checker validates fixed session,
baseline, schema, order, canonical identities, note paths and owned-file
requirements. Running assignments may have incomplete files. A substantive note
for a running row does not promote the row; root must accept its result. This
also permits a worker to have finished while its assignment awaits integration
review. Complete notes/owned files have bounded reads and path restrictions.
The checker reads the manifest once, but does not lock the whole repository or
attest external dispatch, historical note authorship or loaded-code provenance.

## Focused adversarial checks

The maintained 27-method suite was inspected rather than redundantly rerun. A
separate scratch harness exercised the concrete accounting risks raised by this
audit using an isolated copy, including actual CLI invocations. It did not edit
the production checker, maintained tests or live manifest.

| Case | Observed result | Meaning |
| --- | --- | --- |
| Frozen CLI with expected-complete 36 | Pass; 36/4/20 and 40 identities | The dated checkpoint is internally consistent. |
| Same CLI with expected-complete 60 | Rejected: expected 60, observed 36 | A partial ledger cannot claim final completion. |
| Copy ready assignment-37 note while its row remains running | Pass; complete count remains 36 | File presence does not accept a result. |
| Add the actual earlier pedal 60-row manifest | Pass; complete count remains 36 | Another session's rows do not contribute. |
| Set assignment 36's identity to assignment 35's | Rejected for canonical mismatch and duplicate identity | A worker cannot be counted twice. |
| Change assignment 36 to wave 7 | Rejected | Six-slot ordered wave membership is enforced. |
| Give planned assignment 43 a canonical worker identity | Rejected | Planned rows cannot claim dispatch. |
| Substitute an actual older pedal worker for assignment 1 | Rejected | A foreign session identity is not a current worker. |
| Replace the fixed baseline with another 40-character value | Rejected | The session starting source cannot silently change. |
| Remove completed assignment 36's note | Rejected | Completed evidence must exist. |
| Remove another completed owned file | Rejected | A note alone is insufficient for retained completion. |
| Replace the current manifest with the actual older pedal manifest | Rejected for current schema mismatch | A foreign ledger cannot satisfy the current checker. |

All **12 cases had the expected outcome; zero unexpected failures** occurred.
The expected-complete-60 rejection was an intentional negative check of a private
historical snapshot. It is not a successful final gate and does not qualify the
later working tree. The separate follow-up CLI passed with expected-complete 39.

## Earlier histories remain separate

The five other machine-readable manifests were read separately after the first
snapshot. None of their declared identity sets intersects the first snapshot's
40 calibration identities. Their byte hashes are retained in the assignment
note. These counts describe the observed records; they do not requalify those
sessions or assert that a row means an independently attested completed launch.

| Other session | Observed rows | Distinct declared identities | Overlap with first calibration snapshot |
| --- | ---: | ---: | ---: |
| 2026-11-13-continuation | 60 | 60 | 0 |
| 2026-11-13-next-phases | 59 | 59 | 0 |
| 2026-11-13-pedals | 60 | 60 | 0 |
| 2026-11-13-rotary | 60 | 15 | 0 |
| 2026-11-13-scanner | 23 | 23 | 0 |

Some older ledgers use different schemas; applying this calibration schema to
them is not their acceptance procedure. The original markdown
[agent ledger](../development/AGENT_LEDGER.md) also separates its historical
assignments from later sessions. Numeric original assignment IDs are not
invented canonical tool identities. This review changes none of those histories.

## Tested-source and publication mappings

The local acceptance commits and their published equivalents have different
commit identities but exactly equal Git tree identities. `git rev-parse` verified
all six trees, and `git merge-base --is-ancestor` verified that each published
commit below is an ancestor of the observed `183fc9e` remote ref.

| Retained local commit | Published commit | Exact common tree |
| --- | --- | --- |
| `fd0fb58d2f882aa76c7e40e510f44766f762727c` | `340903a333ecfa5c684620ae8ac54e2e917a6217` | `3329cf68bb9ea84479e254934778935bb5c44773` |
| `1aef68489fc18b860bbab8fd06a65fdde8a4d6cd` | `783363f627afeb07f1401fcff042d1a24df094dd` | `5ed86b2f0eeee4e00926aebaaf4432ec61760328` |
| `12fc345730d2ec0dc2bf30ac2372b7af6fdf22b6` | `955fc4c41f74ada094f14fbaf386c943811e9050` | `70956d0f0e125d57abfbf1aed56460c067f8ef28` |

The [wave-5 report](CALIBRATION_WAVE5_INTEGRATION.md) owns the 99/99 local Release
result; the [study/demo report](CALIBRATION_STUDY_DEMO_INTEGRATION.md) owns the
subsequent 16/16 focused result. Assignment 42 verified their source mappings,
not fresh execution of those gates. A later merged or uncommitted source still
requires its own appropriate verification. The observed remote advance retains
calibration history and concurrent standalone development; integration should
preserve both under the standing non-force publication workflow.

## Handoff findings and concrete next steps

These are current-pointer and orchestration recommendations, not newly found
production-checker failures. They refer to the dated documents captured above;
root may have repaired them before this review is published.

1. **Register immediately after dispatch.** Record the actual canonical identity,
   explicit owned paths and running state before a later audit snapshots the
   ledger. Accept only after substantive review. The observed follow-up already
   resolves the 41/42 registration lag and 37–39 acceptance backlog. A running
   record may still await acceptance after its worker has finished.
2. **Refresh the hosted result pointer.** The first handoff/status still treated
   the earlier `779fb6e` portability recheck as outstanding. Assignment 39's
   accepted [955fc4c recheck](CALIBRATION_HOSTED_RECHECK.md) reports nine successful
   jobs and one failed Windows Release job at 2026-11-14 00:14:39 UTC. Its logs
   resolve the earlier output/path/concurrency cases within their stated scope
   and expose a separate demo symlink-target spelling assertion. Preserve both
   reports, link the new failure/repair boundary, and await an actual repaired
   Windows result for the next source. This review did not retrieve those logs.
3. **Label historical suite sizes and publication state.** The session README's
   current-work narrative retained earlier admission totals of 57 corpus and
   60 audio methods, while the later STATUS paragraph records 58 and 63,
   respectively, including two audio capability skips. Label the former as
   historical or update the current pointer; never equate suite/method/skip
   counts. Distinguish the already published first-34 checkpoint `955fc4c` from
   later replay, installation and review work awaiting its own publication/gate.
4. **Finish a coherent checkpoint before final claims.** Integrate the observed
   standalone advance, accept the remaining independent results, update STATUS,
   NEXT_STEPS, handoff and development log together, and record exact source/tree,
   commands, failure outcomes and unrun scopes. Then commit/push under the
   standing owner authorization, verify the fetched remote identity and inspect
   the resulting hosted checks. Preserve the original failing-source records.

**Integration response received after the follow-up:** root confirmed that
`16d72e1` already refreshes the hosted-review links in STATUS, handoff and the
development log, and separates the published `955fc4c` source from later
unqualified replay/installation work. Root will label the README's original
57/60 admission counts as historical. Root also reported that the concurrent
`183fc9e` advance adds another corpus Unicode method, making the integrated
corpus total 59; its new immutable 103-suite gate was running at that response.
Those are explicitly attributed integration updates, not new executions by this
reviewer or a claimed completed gate. Later acceptance and dispatch continue;
they do not invalidate either frozen checkpoint above.

The [standing instructions](../../AGENTS.md) and
[calibration handoff](../CALIBRATION_HANDOFF.md) already require future agents to
read current state, inspect the actual checkout/remote, take explicit ownership,
continue dependency-ready work, preserve other tracks, run meaningful gates and
document results/next steps. They require the integrator to commit and push
authorized completed work, integrate concurrent advances and never force-push.
They also distinguish session-specific sixty-agent accounting from every future
small task. No new approval rule or blanket sixty-worker requirement is needed.

At the follow-up observation, wave 7 has three accepted and three running slots;
waves 8–10 contain eighteen planned slots. Root must still review assignment 42
before accepting it. A final successful `--expected-complete 60` gate is not yet
supported. Once all sixty actual assignments have substantive accepted results,
run that gate on the final coherent retained records and publish its dated
source-qualified result. Neither that eventual check nor this audit establishes
physical acquisition, calibration, permissions, holdout chronology or fidelity.
