# Continuation assignment-record checks

The [continuation manifest](development/2026-11-13-continuation/assignments.json)
records the owner's **new 60 assignments in ten waves of six**. It belongs only
to `2026-11-13-continuation`; the [original ledger](development/AGENT_LEDGER.md)
and its sixty notes remain a separate session. The human-readable
[continuation ledger](development/2026-11-13-continuation/README.md) retains the
development and publication history. The manifest stores current assignment
states without rewriting the earlier snapshots in individual notes.

## Run the checker

From the repository root, with Python 3 and its standard library:

```sh
python3 -B tools/check_continuation.py
python3 -B tools/check_continuation.py --json
python3 -B tools/check_continuation.py --root /path/to/source-archive --json
```

The default command permits work in progress and prints separate **complete**,
**running** and **planned** counts, distinct dispatched identities, and retained
numbered notes. A running worker can already have a note; its existence does not
promote that worker to complete. Completion can be noncontiguous while parallel
workers finish. A passing consistency check does not mean sixty completed agents.

The explicit final continuation gate is:

```sh
python3 -B tools/check_continuation.py --expected-complete 60 --json
```

This requires all sixty records complete, all sixty canonical identities distinct,
and exactly one matching retained note per assignment. `--expected-complete N`
also supports an exact intermediate completion count. Success exits zero;
inconsistency, missing input or a count mismatch exits one. Invalid CLI syntax
uses argparse's exit two. The tool writes no files and needs neither Git nor a
build directory. `--root` selects an archive root, not an alternate session.

The original checker remains unchanged and still checks the original sixty:

```sh
python3 -B tools/check_repository.py --expected-agents 60 --json
```

Run both final gates when publishing the complete continuation. Their results
refer to separate sets; do not add either one's notes to the other's total.

## Manifest contract and honest updates

`assignments.json` uses schema version 1 and the literal session name
`2026-11-13-continuation`. Its sixty records appear in ID order 1 through 60.
Wave is `(id - 1) // 6 + 1`. Each record contains exactly:

| Field | Meaning |
| --- | --- |
| `id` | Integer assignment ID, 1 through 60. |
| `wave` | Integer wave, 1 through 10; exactly six slots per wave. |
| `scope` | Actual dispatched scope, or explicitly planned scope pending dispatch. |
| `status` | `planned`, `running`, or `complete`. |
| `agent` | Actual canonical dispatch identity, or JSON `null` while planned. |
| `note` | Canonical Markdown basename relative to this session, or JSON `null` where allowed below. |

The integrator updates the manifest using actual dispatch/completion reports:

1. **Planned:** `agent` and `note` are both `null`. Keep a future review's scope
   explicitly tentative until assigned. A planned row cannot claim a note file.
2. **Dispatched:** record the actual `/root/wWW_aNN_task_name`, exact scope and
   `running` status. Set the assigned note basename, or retain `note: null`
   until one is assigned. The worker need not have created that file yet.
3. **Complete:** wait for the substantive final report, review its retained note
   and limitations, and then set `complete`. The matching note must exist.
   Do not infer this transition from a filename, a test count, a saved draft,
   a prior-session result or a worker's informal progress update.
4. Reconcile the human-readable session ledger and shared handoff with observed
   outcomes. Check the actual archive intended for publication. Commit, push,
   remote verification and hosted qualification remain distinct recorded actions.

Every retained numbered note begins with a heading such as
`# Assignment 55 — final review` (or `# 55 — final review`) and contains exactly one explicit owner line,
for example ``Agent: `/root/w10_a55_actual_dispatch_name` ``. Existing `Actual agent`,
bullet and bold owner-line forms are accepted. The heading's ID, filename prefix,
manifest ID, canonical identity's assignment and wave must agree. An arbitrary
mention of an agent elsewhere is insufficient. Actual task names come from
dispatch records; the checker never invents one.

Assignment 54 normalized only the missing/incomplete explicit owner lines in
notes 01, 02, 03, 17, 18 and 36 using identities confirmed by the integrator's
dispatch history. Each normalization is labeled, and the older evidence prose
is preserved. This annotation is not a claim that those older workers reran
their tasks during the accounting check.

## Checks, bounds and limits

The checker rejects missing or duplicate IDs, wrong wave assignments, reused or
misassigned actual identities, unsupported states, duplicate JSON fields,
noncanonical/misassigned note names, conflicting/missing note owners, wrong
heading IDs, absent completed notes, unassigned notes, and duplicate or extra
numbered notes. Paths are direct session-local basenames. No recursive repository
scan, old-ledger read, note-path traversal or session/manifest/note symlink is
accepted. Each manifest/note read is capped at **128 KiB**, and direct session
directory enumeration is capped at **256 entries**. Check a stable snapshot;
this is not a locking or adversarial concurrent-filesystem protocol.

This establishes **retained assignment-record consistency**. It cannot attest
external agent runtime identities, prove that an agent read the PDF, evaluate the
substance of a report, authenticate historical execution, or establish test,
publication, physical-model or product completion. The integrator remains
responsible for truthful states and source evidence. Completed planning/review
work can retain explicitly unrun proposed gates.

Run the focused permanent suite directly:

```sh
python3 -B tests/test_continuation_ledger.py
```

CMake's existing `tests/test_*.py` discovery also registers it as
`python_test_continuation_ledger`. Small synthetic fixtures exercise partial and
final gates, original-session separation, missing/duplicate/misassigned notes,
identity/allocation errors, bounded reads and controlled CLI failures. A source
archive smoke check validates its actual current manifest without assuming that
all planned work has already completed.
