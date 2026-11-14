# Calibration completion-accounting review

## Decision and immutable scope

**The accepted-to-date records are internally consistent and ready for the final
integrator closure. This is not a sixty-complete result.** Assignment 59,
`/root/cal_w10_a59`, audited an immutable archive of local commit
`6242c6d46062af8f137c9233dbdad96b71922bc2`, tree
`ad96d544d40687b720752849050a5bd22a6d8f12`. The snapshot contains **56 complete, three running and one planned assignment**,
with **59 distinct declared dispatch identities**; root had accepted 56 and 57.

The [actual manifest](../development/2026-11-13-calibration/assignments.json)
continues separately. The [assignment note](../development/2026-11-13-calibration/59-completion-accounting.md)
retains commands, identities and reproduction limits. Only these two records
were written; no manifest, source, maintained test, shared status or Git ref changed.

| Frozen manifest observation | Value |
| --- | --- |
| Session / starting commit | `2026-11-13-calibration` / `38c1fac949368fa54bd86c6c00a5997a73480f5e` |
| Requested organization | 60 rows, ten logical waves of six, three configured worker slots |
| Complete rows | 1–54, 56, 57 |
| Running rows | 55: hosted evidence; 58: runtime-context acceptance; 59: this audit |
| Planned row | 60: no identity, note or owned paths yet |
| Completed waves | 1–9; wave 10 has two accepted rows in this snapshot |
| Manifest identity | 27,147 bytes; SHA-256 `19e17f3137ec0fa42c3cfa8c442fee1ae689009b03989d33146b6ca6c0429683` |

## Actual accounting and preservation checks

A fresh `git archive` supplied **1,031 files / 40,554,346 bytes**. The independent
audit reconstructed each Git blob identity from its actual extracted bytes,
checked regular-file kinds and the exact path set, then repeated the inventory
after its checks. Every file remained unchanged. The checker used that snapshot, independent of live edits.

| Actual checker invocation | Exit / outcome | Meaning |
| --- | --- | --- |
| `--expected-complete 56 --json` | 0 / `passed`, zero errors | The frozen accepted count and retained records agree. |
| `--expected-complete 60 --json` | 1 / `failed`, one error | Intentional premature-completion probe: `expected 60 completed assignments, observed 56`. |

Both emitted empty stderr and preserve the [checker contract](../CALIBRATION_SESSION_CHECKS.md):
retained consistency only, `external_dispatch_attested: false` and
`physical_fidelity: not_established`. No row changed to obtain these results.

Independent checks, without importing the checker, established:

- Exact assignment IDs 1–60, wave `(assignment - 1) // 6 + 1`, and six rows per wave.
  Every dispatched identity matches its own `/root/cal_wN_aNN` slot; all 59 strings
  are distinct. The single planned row retains null identity/note and empty ownership.
- All **56 complete notes**, totaling **968,658 bytes**, are bounded UTF-8 regular
  files with their own exact worker token and required minimum length.
  This is not a new semantic acceptance of all their experiments.
- All **164 complete owned-file references** resolve to **153 distinct regular
  paths** without symlink components, traversal or missing files. Eight paths
  recur across sequential implementation/repair assignments, accounting for the
  eleven additional references. They are not eleven new deliverables or workers;
  their original source-specific evidence remains in the earlier notes.
- The current identity set has zero intersection with the agent strings in each
  of five other manifests: console continuation, native standalone, pedal,
  rotary and scanner. Their different schemas, row counts and outcomes are
  not imported into this session's total; the files were read and hashed only.

These checks cannot independently prove historical launches, scheduling overlap
or substantive acceptance; root's actual dispatch receipts and review decisions
own those observations. I was dispatched as assignment 59. A file's appearance
does not complete its row, and this note cannot accept itself.

## Full-source reading coverage is consistent

The [calibration consolidation](../research/CALIBRATION_ATLAS_REVIEW.md) points to
this session's six distinct reader notes. Their stated ranges, source hashes and
selected-image declarations agree:

| Reader | Inclusive text pages | Page count | Selected original images |
| --- | --- | ---: | ---: |
| 01 | 1–84 | 84 | 4 |
| 02 | 85–167 | 83 | 6 |
| 03 | 168–250 | 83 | 5 |
| 04 | 251–334 | 84 | 5 |
| 05 | 335–417 | 83 | 6 |
| 06 | 418–500 | 83 | 5 |
| Total | 1–500, contiguous and disjoint | 500 | 31 |

The complete union, image uniqueness and per-reader bounds pass; `pdfinfo`
independently reports 500 pages. The actual PDF is **21,248,265 bytes**, SHA-256
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
This checks retained coverage and source identity, not a seventh complete
reading, new figure inspection or verification of every external reference.

## Tested sources, publication and counters stay distinct

Four local/public pairs have exactly equal complete Git trees. This audit also
verified that the first three public objects, the session baseline and concurrent
`7ec79fb` are ancestors of `d7f6100` in the locally available Git graph.

| Local source → equivalent public source | Exact common tree | Accepted / dispatched in that source manifest |
| --- | --- | ---: |
| `16d72e1` → `7caee9e` | `5619bbb018830e071bc2ce45af84984cdd16bfc1` | 39 / 42 |
| `459bfac` → `d377fab` | `3325af558b040759c1b432ec0806a80785af9713` | 44 / 47 |
| `48a1907` → `5e19022` | `3edea0838b75feb06c19e151ec8539e80646fc03` | 48 / 51 |
| `2671fa5` → `d7f6100` | `0140c737de4db28288b118744c2beef57976697f` | 52 / 55 |
| This audit: `6242c6d` | `ad96d544d40687b720752849050a5bd22a6d8f12` | 56 / 59 |

The [integration record](CALIBRATION_WAVE8_INTEGRATION.md) supplies full IDs,
actual commands and root's fetched publication observation. This worker checked
local objects and ancestry; it did not query or update the remote ref. An object
existing locally or on a server is not itself proof of branch publication.

The **40 changes** from full `48a1907` to public `d7f6100` are AGENTS/README or
documents/records; production, tests, build, models and data are unchanged. The
**15 changes** from d7 to this snapshot are documents/records, outside the
package's 21 copied contract documents. The checker and its regression file
also match d7 byte for byte. These claims apply only to these exact comparisons.

The recorded **106/106** full Release gate belongs to local `48a1907` and its
exact public equivalent `5e19022`. I read root's retained JUnit: 106 entries,
zero failure/error/skipped elements, **52,305 bytes**, SHA-256
`9a12a066e312c62dde559cb372afbd4e9a96183c97a4309d7d8d07b16714b27d`.
This is inspection, not a new run. Older 103-suite hosted
sources, the focused allocation gate, nested Python methods/skips and the new
d7 hosted jobs retain their separate scopes. Do not sum these different count units.

## Findings and final integrator gate

No accounting, source-mapping or PDF-coverage defect was found in the frozen
accepted-to-date records. The earlier shared headline count of 54 was already a
known integrator update. This audit additionally found two stale README pointers
that still described job/readiness composition as future work; root reported
correcting them in the working tree. Preserve that observation as a documentation
correction, not an unreported production failure.

After the snapshot, root reported all ten d7 hosted jobs successful and assignment
58's finite runtime checks passing. Their own retained reviews and root acceptance
remain required; this audit does not borrow those executions or rewrite its
frozen rows.

Final integrator closure requires these distinct observations:

1. Accept every remaining actual result, including this audit and the actual
   final worker; complete the same real rows and preserve failures/source scopes.
2. Reconcile STATUS, NEXT_STEPS, handoff, session README, navigation and log.
   Keep actual pilot/chain/clock/uncertainty inputs and other track owners visible.
3. Only then run `--expected-complete 60 --json` and retain its exact output:
   ten complete waves, zero running/planned, 60 distinct identities, still no
   external-dispatch or physical-fidelity attestation.
4. Verify one coherent final snapshot and affected gates. Documentation-only
   changes must not relabel an old full suite as a new execution.
5. Commit, inspect/integrate concurrent advances, publish with the expected-head
   non-force guard, then fetch and verify the final commit/tree and ancestry.

[AGENTS.md](../../AGENTS.md) makes that evidence, handoff and publication workflow
mandatory for future agents. The sixty-worker session, research waves and product milestones are distinct.
Accounting cannot establish physical fidelity, device/DAW, accessibility or release acceptance.
