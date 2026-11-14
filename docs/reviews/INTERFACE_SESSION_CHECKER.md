# Interface session retained-record checker

[`tools/check_interface_session.py`](../../tools/check_interface_session.py) checks
the existing [interface manifest](../development/2026-11-14-interface-continuation/assignments.json).
Its default completion gate requires **exactly 60 distinct recorded assignments,
all declared accepted, in ten logical waves of six**, with substantive result
notes. It uses Python 3.10 or newer and the standard library. It writes no files,
changes no acceptance state, and has no CMake or CI hook.

## Commands and outcome

From the repository root, after root has substantively accepted A60 and all other
actual assignments:

```sh
python3 -B tools/check_interface_session.py --repo . --json
```

Root can retain that exact output as its final session-check report after the
manifest and notes are stable. A valid final report has `status: passed`,
`completion_valid: true`, 60 accepted records, 60 distinct identities, 60
substantive accepted notes, ten accepted waves and no errors. The command exits
zero only when this strict completion check passes.

During the session:

```sh
python3 -B tools/check_interface_session.py --repo . --in-progress --json
```

| Mode | Exit zero means | Incomplete records |
|---|---|---|
| Default strict completion | The exact 60-record completion contract passes. | Exit 1 with completion errors and `completion_valid: false`. |
| Explicit `--in-progress` | The recorded rows are structurally consistent. | `status: incomplete`, `completion_valid: false`, with running and missing counts visible. |

Malformed inputs return exit 1 in either mode. Invalid command syntax uses
argparse's exit 2. Without `--json`, the tool prints a concise result and errors.
The callable interface is `check(repo, in_progress=False)`.

## Exact schema and assignment rules

The checker preserves this session's actual schema: top-level `schema`, `session`,
`requested_agents`, `requested_waves`, `batch_size`, `base_commit`, `scheduling`
and `assignments`. The integer constants are 1, 60, 10 and 3, respectively. The
session is `2026-11-14-interface-continuation`, starting at
`d493e998e5dd7cf44db46854e87309745063ac54`. Booleans cannot replace integers;
floating-point JSON numbers, duplicate members and nonstandard numeric constants
are rejected. Missing or unexpected fields fail.

Each row needs `number`, `wave`, `agent`, `scope` and `status`. Accepted rows also
require nonempty `result` and `acceptance`; those two fields may be absent on
actual running rows. Present text fields are type-checked and bounded. No planned,
future, completed-but-unaccepted or placeholder state is admitted. The strict
gate rejects running rows through its exact accepted-count requirement.

Numbers are unique integers 1–60; the final set must contain every number. The
wave is exactly `(number - 1) // 6 + 1`. Array order is immaterial because this
session explicitly permits dependency-ready dispatch out of numeric order.
Progress mode lists absent numbers without manufacturing their rows. Agent
strings must be unique canonical `/root/wNN_aNN_name` identities whose wave and
number match the row. `batch_size: 3` records the configured worker-slot limit;
the checker does not reconstruct overlapping execution or count root integration.

## Retained notes and safe resolution

`result` is a normalized relative path below this session directory. Distinct
rows cannot reuse one result path. Absolute paths, `.`/`..`, empty components,
backslashes, colons, whitespace-only paths and control characters are rejected.
Every inspected component must be a real directory or final regular file;
symbolic links and Windows reparse points are rejected even if their targets
remain within the repository. Directories, FIFOs and other special files cannot
stand in for notes. Running rows can name a note that has not yet been written.

Accepted notes must exist, decode as UTF-8, contain no NUL or bare carriage
return, and retain at least **200 narrative characters and 30 words outside
fenced code and HTML comments**. This is a structural floor. It cannot establish
the truth or sufficiency of a report. The first six atlas records and later
accepted notes were inspected before choosing this rule: genuine notes use
varied headings and both `01-atlas-...` and `sessionNN-...` names; several do not
repeat the exact manifest agent token. No new title, filename numbering,
owner-token or section convention is imposed on them.

The manifest is bounded at 256 KiB and each note at 128 KiB. Reads are bounded
again after opening and check file identity/metadata across the read. Paths are
bounded at 1,024 characters; prose fields at 8,192. Use stable files for final
publication: this is not a filesystem sandbox, global snapshot or authentication
mechanism against concurrent writers.

## Machine-readable evidence and claim boundary

JSON retains deterministic counts, missing numbers, per-wave counts, error codes
and locations, `record_consistency_valid`, and `completion_valid`. It identifies
the exact checker bytes, manifest bytes and each successfully read accepted note
by SHA-256, with an aggregate checked-note identity. There are no timestamps or
random fixture paths in the report. Counts describe declared records; when
validation fails they remain diagnostics, not a completion result. Unassigned
files and earlier sessions never add accepted assignments.

Every result explicitly sets dispatch, semantic acceptance and product/model
readiness attestation to false. A syntactically convincing invented record
cannot be detected from text alone. Actual dispatch evidence and substantive
acceptance remain root/A59/A60 responsibilities. A consistency pass does not
prove atlas reading, code correctness, executed tests, publication, exact visual
equality, host/device qualification, accessibility, physical fidelity or whole
M0–M9 completion.

## Executed verification and next gate

The independent [CLI verification](../development/2026-11-14-interface-continuation/reports/a54-checker-verification.py)
constructs synthetic records in temporary directories outside the repository and
removes them afterwards. It imports no checker implementation or constants. The
[retained result](../development/2026-11-14-interface-continuation/reports/a54-checker-verification.json)
records **51 cases: four positive cases and 47 asserted nonzero rejections**.

Positive cases cover complete 60-row records, out-of-order dispatch, partial
accepted/running rows and an empty in-progress ledger. Identical complete inputs
emit byte-identical JSON. Negative cases cover duplicate/missing/out-of-range
numbers, wave/identity mismatches, duplicate/empty identities, disallowed states,
missing scope/acceptance/result, duplicate/missing/empty/insubstantial notes,
code/comment-only placeholders, invalid UTF-8, oversized files, unsafe paths,
linked files/parents/manifest, directory/FIFO notes, strict types, unknown fields,
duplicate JSON members and NaN.

At the actual A54 observation, manifest SHA-256
`b6d6f24638f704962c313e3313e131d1d81c18d24a8a876ffb38b5332a083c7f`
recorded **55 actual rows, 52 declared accepted and three running**. Both modes
found the recorded rows consistent. Strict completion returned **exit 1**;
progress returned exit 0 with **`status: incomplete` and `completion_valid: false`**.
The [source identity](../development/2026-11-14-interface-continuation/reports/a54-source-identity.json)
retains Python 3.12.14, checker/verifier hashes and the inspected checkout
HEAD/tree. These are checker results only. A49's 146/147 application gate and
A52's separate fixture repair retain their own evidence and outcomes.

The archived A54 verifier intentionally asserts that its live session is still
incomplete. After A60 acceptance, root's next gate is the strict command above on
the stable, reviewed real manifest, followed by publication of that output and
the independently reviewed accounting/handoff. No final completion output was
created by A54.
