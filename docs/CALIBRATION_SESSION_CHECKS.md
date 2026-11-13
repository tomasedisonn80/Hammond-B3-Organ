# Calibration session accounting

[`check_calibration_session.py`](../tools/check_calibration_session.py) validates
the retained [calibration manifest](development/2026-11-13-calibration/assignments.json)
and its declared completed files. It reads only this named session's accounting;
earlier sessions and unassigned notes cannot add participants or completed work.
It requires Python 3.10 or newer and the standard library, without Git, network
access or an installed audio toolchain.

From the repository root:

```sh
python3 tools/check_calibration_session.py --repo . --json
python3 tests/test_calibration_session_records.py
```

The callable API is `check(repo, expected_complete=None) -> report`, where `repo`
is a path to the repository root. The CLI uses that same API. `--repo` defaults
to the checkout containing the checker; `--json` produces one JSON report on
standard output. Without `--json`, a concise status/count summary goes to
standard output and validation errors go to standard error. Exit 0 means the
retained records passed this check; exit 1 means validation failed. Invalid CLI
argument syntax uses argparse's exit 2.

## Fixed session and state rules

The manifest has exactly `schema_version`, `session_id`, `baseline_commit`,
`requested_agents`, `requested_waves`, `concurrency` and `assignments` members.
Its identity is `2026-11-13-calibration`, its full starting commit is
`38c1fac949368fa54bd86c6c00a5997a73480f5e`, and its integer fields are schema 1,
60 requested agents, ten waves and three concurrent worker slots. A different
session or another valid-looking Git hash fails. Integers exclude booleans and
floating-point numbers. JSON rejects duplicate members and nonstandard
`NaN`/`Infinity` constants.

The assignments array contains exactly sixty rows in ascending order. Assignment
IDs are 1 through 60, and the wave is `(assignment - 1) // 6 + 1`. Each row has
exactly `assignment`, `wave`, `state`, `agent`, `scope`, `note` and `owned_files`.
The scope is nonempty text of at most 1,000 characters, without control characters.

| Declared state | Required identity and ownership | Required retained files |
| --- | --- | --- |
| `planned` | `agent` and `note` are null; `owned_files` is an empty array. A nonempty planning scope is permitted. | None. Existing drafts never promote the row to another state. |
| `running` | A distinct canonical identity, a numbered session-local note name, and an ownership list containing that note's full repository-relative path. | The declared files may still be absent while the worker writes them. |
| `complete` | The same identity, numbering and ownership rules as a running assignment. | The note and every declared owned file must exist as bounded regular files inside the repository. |

Canonical worker identities match this session's actual dispatch naming scheme:
`/root/cal_w1_a01` through `/root/cal_w10_a60`, with each row's own wave and
two-digit assignment ID. A worker identity cannot be counted twice or substituted
from an earlier session. This is a check on recorded strings, not an independent
observation that a worker was dispatched.

The note is a direct filename such as `11-session-checker.md`, starting with its
own two-digit assignment ID. Its remaining stem contains lowercase ASCII letters,
digits and single hyphens. The whole name is at most 160 characters. A complete
note must decode as UTF-8, contain no NUL, have at least 200 characters after
trimming surrounding whitespace, and mention its exact canonical identity as a
worker token. A longer identity containing that string as a prefix does not count.
The length/identity rule is a structural minimum; the integrator must still review
the note's substance, result and verification.

## File and resource bounds

| Input | Bound |
| --- | ---: |
| Manifest | 256 KiB |
| Completed note | 128 KiB |
| Each completed owned file | 64 MiB |
| Owned paths per assignment | 64 |
| Each repository-relative path | 512 characters |

Limits are inclusive. Owned files are inspected for type, location and size;
their contents are not treated as proof that an implementation is correct.
Only the manifest and completed notes are read as text. Text reads are bounded
again after opening, so growth beyond the bound fails.

Paths use normalized relative POSIX syntax. Absolute paths, `.`/`..` components,
empty components, backslashes, colons and control characters fail. Duplicate
owned paths fail. Every inspected path component below the resolved repository
root must be a real directory or, for its final component, a regular file.
Symbolic links and Windows reparse points are rejected even when their targets
stay inside the repository; directories, FIFOs and other special files cannot
stand in for completed files. A failed transfer to a file stream closes the
already acquired descriptor.
Spaces and Unicode in ordinary owned filenames or the repository location are
supported.

The checker reads the manifest once per call. It does not freeze the repository,
lock the live ledger, authenticate filesystem writers or attest dispatch timing.
A concurrent manifest/file update can require a new check after the integrator
finishes the checkpoint. The concurrency field records the session's configured
worker-slot limit; this tool does not reconstruct actual overlapping execution.

## Counts and completion gates

The report includes `status`, `counts` for `planned`/`running`/`complete`,
`distinct_actual_agents`, `completed_waves`, `expected_complete`, `errors` and
`error_count`. Counts describe the declared rows; the distinct identity count
contains only recognized canonical identities in dispatched states. Complete
waves are reported as a list of wave numbers with six declared complete rows.
If validation fails, reported counts may be partial and must not be accepted as
a completion gate.

An optional expected count is an **exact equality** test, accepting only an
integer from 0 through 60. For example, an expectation of five fails when six
rows declare completion, just as an expectation of sixty fails when six do.
Use a checkpoint's actual accepted count when one has been frozen:

```sh
python3 tools/check_calibration_session.py --repo . --expected-complete 60 --json
```

The final command is appropriate only after all sixty distinct assignments have
actually completed and the integrator has accepted their results. A planning
request, another session's sixty rows, a file appearing on disk or a favorable
test run never updates this manifest automatically. The checker writes nothing.

Every report retains `scope: retained_accounting_consistency_only`,
`external_dispatch_attested: false` and `physical_fidelity: not_established`.
A pass does not attest external execution, semantic correctness of the notes,
actual assignment acceptance, hardware acquisition, measured calibration, host
qualification or publication. Those claims require their own observed evidence.

## Independent regression fixtures

[`test_calibration_session_records.py`](../tests/test_calibration_session_records.py)
constructs its own temporary manifests, notes and owned files. It does not copy
the changing live manifest, manufacture session completion, or write outside its
temporary fixture directory. The tests cover valid partial/all-planned/full
states, exact CLI/API expectations, strict schemas and types, stale or duplicate
identities, missing and unassigned files, malformed JSON, unsafe paths, symlinks,
special files, Windows reparse metadata, stream-creation cleanup, Unicode paths
and inclusive/exceeded resource limits. Controlled Windows metadata tests run on
any platform; they are not a claim of an executed native Windows junction test.

The existing CMake `tests/test_*.py` discovery registers this file as
`python_test_calibration_session_records`; no new CMake entry is needed. The
assignment's executed results and one observed live-ledger state are retained in
[the checker evidence note](development/2026-11-13-calibration/11-session-checker.md).
