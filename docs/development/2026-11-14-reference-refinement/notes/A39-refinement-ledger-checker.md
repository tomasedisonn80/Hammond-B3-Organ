# A39 — Strict refinement ledger checker

Actual assignment: `/root/w07_a39_refinement_ledger_checker`, wave 7. I read the
standing agent instructions, current refinement scope, checkpoint, actual manifest,
complete M0–M9 plan and source-review boundaries, then inspected the historical
interface checker as a robustness reference. This assignment owns only the new
checker, its focused tests and these A39 records. Root retains acceptance,
shared documentation, manifest changes and publication.

## Implementation and evidence boundary

`tools/check_refinement_session.py` consumes this session's exact existing schema
and canonical starting commit. Default execution requires A01–A60, sixty distinct
canonical worker names, six accepted IDs in each of ten waves, concurrency four,
existing session-local notes and exact declared SHA-256 matches. Explicit
`--in-progress` validates partial records and always reports completion false;
it cannot substitute for the strict completion gate. Both modes emit JSON with
declared counts, per-wave counts, actual note identities, aggregate identity,
checker and manifest hashes, errors and explicit claim limits.

Bounded parsing rejects duplicate JSON members, booleans masquerading as integers,
floating constants, unexpected fields, placeholders, duplicate IDs/names/paths,
incorrect wave mappings, missing accepted fields and changed note bytes. File
admission rejects traversal, outside-session notes, symbolic links, Windows
reparse metadata, special files, oversized input and observed changes during
reading. Accepted notes require 100 narrative words and 40 distinct words;
comments and fenced or indented code do not supply that floor. This structural
check does not prove dispatch, substantive acceptance, execution, publication,
visual equality, product readiness or physical fidelity. Existing notes were
read without modification or padding.

## Executed qualification

Working directory was the repository at
`/workspace/scratch/1bb6ee17ad7e/Hammond-B3-Organ`, with published HEAD
`f9c11a498ecd88886349415205fc5dccc627033e` and Python 3.12.14 on Linux.
`python3 tests/test_refinement_session.py -v` passed all twenty methods in
1.181 seconds. Fixtures are explicitly synthetic and exist only in disposable
temporary directories. They never populate the actual manifest or represent
real workers. The first retained run had three assertion failures because raw
DEL was correctly rejected before the tests' expected field-validation stage;
escaping that character in fixture JSON repaired the tests without weakening
the checker. Both logs are retained.

`python3 tools/check_refinement_session.py --repo . --in-progress --json` observed
41 recorded, 38 accepted, three running and 38 verified accepted notes, with zero
consistency errors and completion false. The same command without `--in-progress`
exited one with exactly the two expected completion-count/status errors. Reports
retain the exact input bytes' hashes, so these observations do not qualify later
manifest revisions. `reports/A39-refinement-ledger-checker.json` indexes both
commands, logs, source hashes and environment. No shared builds or broad test
suites were run; historical checkers and manifests remain untouched by this work.

## Next task

Root should review and publish the owned files, continue actual acceptance, and
enable the strict CI command only after all sixty actual results are accepted.
The final gate must execute against that exact completed manifest and notes.
Product, visual and physical claims retain their independent evidence gates.
