# Assignment 11: retained calibration-session checker

## Actual assignment and owned outputs

- Session: `2026-11-13-calibration`, wave 2, assignment 11.
- Actual canonical worker: `/root/cal_w2_a11`.
- Session starting commit: `38c1fac949368fa54bd86c6c00a5997a73480f5e`.
- Observed checkout HEAD while testing: `08fa8de8f718584c4ee4ab3b392c779f3290289c`;
  that commit's tree is `f5cff4b89d19f36a73f9d2a8ddb966db487f832c`.
- The four outputs below were new working-tree files during this task. The HEAD
  above identifies their base, not a committed or fully qualified integration of
  these additions. The integrator owns acceptance, shared status and publication.

Owned files:

1. `tools/check_calibration_session.py`
2. `tests/test_calibration_session_records.py`
3. `docs/CALIBRATION_SESSION_CHECKS.md`
4. `docs/development/2026-11-13-calibration/11-session-checker.md`

No session manifest, shared status document, CMake file or earlier session record
was changed by this worker. No commit or push was attempted.

## Implementation and contract

The checker follows the existing rotary checker's `check(repo,
expected_complete=None)` report shape and CLI, while fixing the calibration
session identity and full baseline explicitly. It accepts exactly sixty ordered
assignment rows, grouped as six per wave, with strict members, integer types and
planned/running/complete states. Planned rows cannot claim an agent, note or
ownership. Dispatched rows use this session's actual canonical wave/assignment
naming convention, and identities cannot be counted twice.

Completed rows require a substantive retained note containing the exact canonical
worker token and every declared owned file. Files must be regular, bounded and
inside the repository. Path checks reject traversal, alternate separators,
control characters, links or Windows reparse points in any inspected component,
directories and FIFOs. Failed stream creation closes its acquired descriptor.
The manifest and note reads are separately bounded after opening. Running files
can still be absent; a draft appearing does not promote completion.

`--expected-complete` is exact equality for integers 0 through 60. Both an
underestimate and an overestimate fail. Duplicate JSON members, nonstandard
constants, stale session metadata, wrong worker identities and unrecognized
fields fail. Only this manifest determines counts; historical ledgers and
unassigned notes are ignored. The checker reads the manifest once, writes
nothing and always retains its accounting-only and no-physical-fidelity claims.

The [contract](../../CALIBRATION_SESSION_CHECKS.md) documents the fixed metadata,
per-state requirements, inclusive size limits, read-only behavior, report fields,
CLI exit codes and remaining review obligations. No hardware, captured audio,
external dispatch or substantive worker acceptance is attested by a pass.

## Independent fixtures and executed verification

All commands below ran from
`/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ` with Python **3.12.14** on the
shared Linux runner. The test file constructs its own temporary manifests and
files; it never copies or mutates the live session ledger. These synthetic worker
names represent fixture strings only and are not counted as real dispatches.

```sh
python3 -B tests/test_calibration_session_records.py
```

Final result: **27 tests passed**, zero failures or skips, **0.910 seconds**,
exit 0. Earlier 24- and 25-test runs also passed. Author review tightened the
1,000-character scope bound to count surrounding whitespace and added an
independent positive boundary case. The integrator then identified two specific
gaps: ownership of the descriptor if `os.fdopen` fails, and Windows reparse-point
aliases. Both are fixed, with focused controlled regressions in the final run.

Coverage includes valid partial/all-planned/full ledgers; exact count failures in
both directions; CLI JSON/human output and exit codes; strict root/row schemas and
types; ordered assignments and six-slot waves; stale/cross-session/duplicate
identities; planned-state false ownership; missing complete notes/files; wrong
note number or identity-prefix substitution; malformed, duplicate-member,
nonstandard and deeply nested JSON; normalized paths; Unicode paths; size limits
at and beyond their exact bounds; directory/FIFO rejection; and symlinked files,
owned parents and session directories. Controlled failures also prove descriptor
cleanup and rejection of Windows reparse metadata on parent/leaf components.
That metadata simulation is portable regression coverage, not an executed native
Windows junction test. Old session records and unassigned notes never promote
counts in the independent fixtures.

The existing CMake `file(GLOB ... CONFIGURE_DEPENDS tests/test_*.py)` registration
was inspected and will discover `python_test_calibration_session_records`.
No CMake configure, build, CTest integration, other platform or full-repository
qualification was run by this assignment. Those remain integrator checks.

## One observed live session state

Executed once after the initial 25-test suite passed, before the two integrator
review refinements:

```sh
python3 -B tools/check_calibration_session.py --repo . --json
```

The checker returned **passed**, exit 0, with zero errors and these declared
counts: **9 complete, 3 running, 48 planned**; **12 distinct recorded canonical
identities**; completed waves **[1]**; `expected_complete: null`.
This observation belongs to the changing worktree at the time of the call. It
does not assert that those counts remain current or count this worker as already
accepted. The manifest was not edited to create the observed result, and the
checker was not rerun to chase an advancing count. This observation used checker
SHA-256 `ad61c9022a1ba3df8c7da4ba8cf211f15cbf577c84ab57040078372065ad9951`;
the final revised checker is identified separately below.

## Exact tested file identities

The following SHA-256 values identify the final fixture-tested files. The note
itself was updated afterward to retain these observations.

| File | SHA-256 |
| --- | --- |
| `tools/check_calibration_session.py` | `f5d53fe357406456c1335b55ccab9e6db885c68b055b12c6d71138bf73e7fb19` |
| `tests/test_calibration_session_records.py` | `938964e787615e71610e1601ce9c820f747a76ac522c994f526efab71a78964d` |
| `docs/CALIBRATION_SESSION_CHECKS.md` | `d8eb93bf2e6d2e3fecccab80eaa4ef190c5299ceb53f85884367bd1de3d08b5f` |

`git rev-parse HEAD HEAD^{tree}` and `sha256sum` supplied those identities.
`git diff --check` returned exit 0 for the tracked live worktree; it does not
replace fixture execution or qualify the uncommitted repository as a whole.

## Limits and concrete next steps

The length/identity check cannot establish that prose is truthful or sufficiently
substantive. The integrator must observe the real dispatch, review each result
and accept the applicable work. The tool also does not reconstruct execution
timing, freeze concurrently changing files or authenticate filesystem writers.
Its bounded file checks are retained-record validation, not a claim of an
adversarially race-free filesystem snapshot.

The integrator should review these four owned files, record acceptance under the
existing actual identity, and rerun the checker on the next coherent checkpoint
with that checkpoint's exact accepted count. Build the required selected inputs
before the repository's CTest gate; this suite is available under its automatic
test name. Use `--expected-complete 60` only after all sixty distinct assignments
actually complete and their results are accepted. Preserve separate engineering,
physical acquisition, calibration, host and publication gates throughout.
