# Product session ledger and strict-gate audit

## Decision and exact snapshot

**The retained records are internally consistent; this audit does not close the
session.** At the frozen A57 snapshot, the product manifest contains 57 distinct
session IDs and agent paths: A01–A54 accepted, A55–A57 running, A58–A60 absent.
Waves 1–9 each contain six accepted records; wave 10 contains three running
records. No planned row appears. All 54 accepted note hashes match their bytes.
The [exact progress output](../development/2026-11-15-product-continuation/reports/A57-progress-records.json),
[expected strict rejection](../development/2026-11-15-product-continuation/reports/A57-strict-incomplete.json)
and [audit receipt](../development/2026-11-15-product-continuation/reports/A57-ledger-audit.json)
retain that observation. Later actual dispatches and acceptances belong to the
live checkpoint; they must not rewrite these earlier outputs.

Reviewed the complete AGENTS/M0–M9 plan, active entry/checkpoint/assignments,
current navigation and recovery handoff, A46's checker, all 19 test methods,
its note/verification, all 54 accepted notes and the current CI record step.
The working directory was
`/workspace/scratch/5b7d983ac078/Hammond-B3-Organ`, Python 3.12.14. Read-only Git
checks observed HEAD and live `refs/heads/main` at
`d8c39f7986746eacc991747153c7dbb012bb9a32`, tree
`edf67b978f93e8dbea6537ce92d3928c171bc1f3`; the index was empty. The checker,
tests, ledger and other accepted working files were later, uncommitted inputs.
This is not an audit of an unchanged d8 checkout.

| Frozen input | Bytes | SHA-256 |
| --- | ---: | --- |
| `tools/check_product_session.py` | 20,345 | `49784fd2c7304dd1482a684b6a1750f8142bcf2283bec223341c7d7a24d8508c` |
| `tests/test_product_session.py` | 21,474 | `e96c052692bce5a69884629393cdee2d8cf1da5df9558f71f60979259eaa4f55` |
| Product `assignments.json` | 45,037 | `03644d673b3ac41dd83419f175184ab59fb9f2c691af0d26f529868d733b61a1` |
| `.github/workflows/ci.yml` | 9,276 | `dc0ca8ca102d099a3874d93837c9279ab7af66e92b9de03bc0c5c39642ce6d9e` |

## Accounting, notes and historical separation

The checker admits only `b3-product-session-v1`, this exact session/start commit,
the declared 60 workers/10 waves/three-worker concurrency metadata and exact
member types. IDs A01–A60 map in consecutive groups of six; canonical
`/root/wNN_aNN_name` paths must match each ID/wave and be unique inside this
manifest. Duplicate rows, IDs, agent paths and note paths fail. Only running,
review-complete and accepted states are admitted. Concurrency metadata is a
declared limit, not a measurement of the dispatch schedule.

Accepted/review-complete rows require task, acceptance, usable ownership, a
matching session-local note and its lowercase SHA-256. Every accepted note was
read during this audit. Their content identifies distinct work, source or
input basis, delivered results and limits; numerical, native, hosted and visual
claims remain qualified by their original evidence. This is a content review,
not a rerun of those workers' experiments or independent confirmation of every
assertion. The raw note hashes are all distinct. Atlas notes retain 753–920
whitespace-delimited words and their complete page ranges. Older accepted notes
are not retroactively subjected to the later 400-word handoff target.

The 100-word/40-distinct-word narrative floor excludes comments, fenced code
and indented code. It catches empty or repeated filler; it cannot establish
truth or substantive review. The 128 KiB byte limit is a read bound, not a word
ceiling. Running rows may have unwritten notes, while a declared hash must
already match. Reviewed candidates satisfy the same evidence structure as
accepted rows but cannot satisfy strict accepted counts.

Compared current names with all eleven other `assignments.json` manifests and
accepted-note byte hashes with 570 historical development Markdown files.
There are no historical note-byte matches. Five atlas task names recur in other
sessions, including `/root/w01_a02_atlas_console`; the receipt enumerates the
21 name occurrences. These canonical names are **session-scoped**, not globally
unique dispatch tokens. Reused spelling neither proves that a worker was
recounted nor independently proves a fresh dispatch. The product checker reads
only its fixed current manifest and `notes/Axx-name.md` paths beneath this
session; it never sums historical ledgers or admits historical note references.

**Source review, note hashes and structural consistency cannot attest actual
tool dispatch.** The integrator must reconcile every accepted row with the
actual collaboration history and substantive delivery. Even a fabricated but
well-formed current-session row can satisfy structural checks. The synthetic
complete fixture deliberately demonstrates structure only and expressly says
that none of its temporary rows represents a dispatched worker.

## Ownership and path safety

Ownership parsing preserves optional parenthesized scopes and real directories.
Accepted/reviewed paths must exist; a running assignment may name a new file.
Sixteen exact paths recur across historical assignments within this session,
with handoffs or authorized repairs recorded in the notes: painter A15→A18,
reference A17→A19, benchmark A27→A30, installer A31→A38, workflow A37→A43,
plotter A28→A48 and returned shared documentation. A40's gallery directory also
contains A41's two expressly authorized wording/identity files. The three
running audit assignments have distinct document/note paths at this snapshot.
These records agree with the integrator's temporal ownership policy; accepted
workers do not retain permanent control of their old paths.

The validator checks declared references, not a Git diff or historical ownership
schedule. It does not establish that a worker changed only assigned files,
detect every cross-row scope conflict, hash owned implementation files or
authenticate authorizations. Those are integrator/source-review obligations.

Source and negative tests cover normalized relative POSIX paths, traversal,
globs, backslashes, drive syntax, malformed scopes, symlink leaves/parents,
Windows reparse metadata, special files, wrong note identity, invalid UTF-8,
forbidden controls and byte limits. The bounded reader checks ordinary-file
metadata before/after opening and reading and detects changed path identities.
Raw-byte hashes remain correct for CRLF notes. Duplicate JSON members, floats,
nonfinite numbers, oversized integers and excessive nesting fail closed.

This is bounded local-file admission with per-read change detection. It is not
an adversarial filesystem transaction or a frozen-source guarantee across the
whole checkout. Windows reparse behavior is exercised with mocked metadata in
the reviewed tests; this audit executed no Windows filesystem experiment.
Root held the manifest stable across the two actual CLI reads, and both outputs
contain identical checker/manifest/checked-note identities.

## Meaningful verification and mode semantics

The reviewed 19-method suite covers complete/partial synthetic fixtures,
identity/schema/status mutations, missing or tampered evidence, narrative
filler, accepted versus running ownership, path/file attacks, exact read bounds,
changed-during-open inputs and CLI exit behavior. The complete fixture also
proves that progress mode declines closure even with sixty accepted rows.
No additional concrete gap justified another mutation or a repeated suite.

The checker/test hashes match A46's retained
[19/19 focused verification](../development/2026-11-15-product-continuation/reports/A46-verification.json)
and root's [366-input coherent receipt](../development/2026-11-15-product-continuation/reports/wave8-coherent-build.json).
The latter's original CTest log includes `python_test_product_session` passing
in 1.29 seconds within the 180/180, 507.55-second run. Those are retained
executions, not A57 reruns. A57 executed only the two read-only checker commands:

```sh
python3 -B tools/check_product_session.py --repo . --allow-incomplete --json
python3 -B tools/check_product_session.py --repo . --json
```

| Mode on the frozen actual records | Exit/status | Consistency | Closure |
| --- | --- | --- | --- |
| Progress | 0 / `incomplete`; zero errors | true | false |
| Strict | 1 / `failed`; count, status and wave completion errors | true | false |

Strict failure with `record_consistency_valid:true` is intentional: the records
are consistent, while completion requirements remain unsatisfied. Strict success
requires all sixty accepted, verified notes and all ten six-worker waves with
no structural errors. It still cannot attest dispatch, test execution,
publication, product readiness or visual/physical fidelity.

The current Linux Release CI step uses progress mode and `set -o pipefail`, then
retains JSON under `ci-logs/`. Thus a checker error is not hidden by `tee`.
Historical interface/refinement gates remain separate. The published d8 hosted
results precede this added checker step and cannot qualify its future hosted
execution.

## Finding and precise root closure

**A57-L1, corrected:** A07/A08's optional result text still said review was
underway, and A19's said its final note was pending despite accepted evidence.
Root corrected only those strings before the frozen reads. The
[repair receipt](../development/2026-11-15-product-continuation/reports/ledger-narrative-repair.json)
retains before/after manifest identities; status, note bytes/hashes and ownership
were unchanged. No checker defect requiring a source/test change was found.

1. Dispatch the remaining real A58–A60 work and substantively accept all remaining
   deliveries. Keep the actual tool-history reconciliation separate from this
   file audit. Update each final note hash only after its owned result is reviewed;
   do not create planned rows or count follow-ups/history as new workers.
2. Freeze all sixty accepted note bytes and the final manifest. From the
   repository root run and retain the successful strict output:

   ```sh
   python3 -B tools/check_product_session.py --repo . --json > docs/development/2026-11-15-product-continuation/completion-check.json
   ```

   Require exit 0, `mode:strict_completion`, `status:passed`, both validity flags
   true, 60 distinct IDs/agents/note paths, 60 accepted/verified notes, no missing
   IDs/errors and six accepted records in each of ten waves. Retain the exact
   checker/manifest/checked-note identities. Any later accepted-note or ledger
   change requires a fresh strict result.
3. Remove `--allow-incomplete` only from the product CI step, preserve its
   failure propagation/artifact capture and check the changed workflow block.
   Preserve the existing 180-test evidence; rerun broader local gates only for
   concrete changed inputs. Publish the accepted tree through root's fresh
   expected-head/non-force procedure and verify exact remote commit/tree/parent.
4. Observe the exact publication's required hosted jobs and primary strict
   product JSON. Confirm discovery/execution of the new product-session and
   plot-admission Python modules. Neither d8's old green matrix nor this expected
   incomplete result closes the final-source gate. A later evidence-only commit
   must continue naming the source actually tested.
5. Update closure/handoff with the actual final source and preserved limits:
   literal whole-interface 1:1 remains unmet, Engine remains nominal/dry,
   A47 native retirement and physical/device/DAW/accessibility gates remain open,
   scanner G5 stays failed and the separate R4 checkout/ledger remains owned by
   its session. Accounting completion does not waive any of those gates.

A57 changed only this review, its short note and bounded A57 reports. No checker,
tests, workflow, manifest, accepted notes, shared build, other checkout, index,
commit or publication was modified by this worker.
