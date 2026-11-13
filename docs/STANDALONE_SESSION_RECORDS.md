# Standalone session record checks

`tools/check_standalone_session.py` validates only the actual assignment manifest
at `docs/development/2026-11-13-next-phases/assignments.json`. It does not count
historical ledgers or infer participants from other files. Python 3.10 or newer
and the retained source PDF are required; no network, build or third-party package
is needed. The checker never changes records or promotes their declared status.

Run from the repository root:

```sh
python3 tools/check_standalone_session.py --repo . --json
python3 tests/test_standalone_session_records.py
```

The normal command accepts a valid ongoing session. Its result reports actual
`running`, `completed` and `blocked` counts, distinct dispatched agents, remaining
undispatched assignments, per-wave counts and completed waves. A blocked row is
reported as blocked even when its report exists. An absent running/blocked report
is allowed. Unlisted report files never add a participant or completion.

After the integrator accepts all sixty actual assignments, use the closure gate:

```sh
python3 tools/check_standalone_session.py --repo . --expected-complete 60 --json
```

`--expected-complete N` requires exactly N completed records, with N from 0 to 60.
Sixty requires all sixty distinct assignments and all ten waves completed.
Successful validation exits 0; malformed or inconsistent records and unmet
expectations exit 1. `--json` emits a structured result for either outcome.

## Admission rules

- The manifest schema, session ID, baseline commit, sixty-assignment request,
  ten-wave request and concurrency limit of three must match this session.
  Its assignment list contains only dispatched rows; there is no planned status.
- Numbers are unique integers 1–60. Wave is `(number - 1) // 6 + 1`. Canonical
  `/root/wNN_aNN_name` agent names are unique and must encode the same wave and
  number. Only `running`, `completed` and `blocked` statuses are admitted.
- Reports use numbered Markdown names in this session directory. Owned paths
  and report paths must be normalized relative paths without traversal, drive
  prefixes, backslashes, control characters or existing symlinks/reparse points.
  Each assignment owns its report and lists no duplicate owned paths. Missing
  owned implementation files are allowed because ownership is a declaration.
- Every completed report exists and contains its exact canonical agent token
  outside fenced examples. No uniform title, headings or narrative length is
  imposed. Report filenames and encoded agent identities establish the number;
  the checker does not grade the substance of the narrative.
- Duplicate JSON keys, non-integer JSON numbers, unsupported fields, malformed
  text and text inputs above 128 KiB are rejected. Run against a quiescent
  checkout; these path checks are not a concurrent filesystem security boundary.
- The actual PDF bytes must hash to
  `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.

## Retained atlas coverage and limits

Completed reports 1–6 must retain that source hash and their respective inclusive
ranges: **1–84, 85–168, 169–252, 253–336, 337–420 and 421–500**. These explicit
reference ranges are contiguous and disjoint; they sum to 500 pages. The reported
`retained_atlas_pages` counts only ranges whose completed reports pass validation.
The checker inherits those recorded declarations; it does not perform or claim
a fresh reading, page-image inspection or underlying-source verification.

A pass establishes retained consistency. Real dispatch, substantive acceptance,
test execution, publication, native-device qualification and physical fidelity
require separate evidence. The integrator owns manifest changes and acceptance.
The standard CMake `tests/test_*.py` discovery includes the fixture suite.
