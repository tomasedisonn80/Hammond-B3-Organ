# Pedal-session retained-record checks

[`tools/check_pedal_session.py`](../tools/check_pedal_session.py) checks the
records for the **2026-11-13-pedals** session. It reads the
[actual assignment manifest](development/2026-11-13-pedals/assignments.json)
and that directory's assigned notes. Both earlier sixty-worker sessions remain
separate historical records and cannot supply credit here.

This is a record-consistency check. The integrator still verifies actual
dispatch, accepts each substantive result, inspects the relevant test evidence,
and observes publication. A file, a declared state or a passing checker cannot
independently prove that a worker executed or that its technical claims are true.
The standing workflow is in [AGENTS.md](../AGENTS.md); the
[session README](development/2026-11-13-pedals/README.md) describes the actual
scope and ten logical waves.

## Commands and exit behavior

Python 3.10 or newer and the standard library are sufficient. From the repository:

```sh
python3 tools/check_pedal_session.py --repo .
python3 tools/check_pedal_session.py --repo . --json
```

The default `--repo` is the resolved parent repository of the script, so it also
works from another current directory or a source archive without Git metadata.
An explicitly selected repository root is resolved first. The tool only reads
the designated session below that root and writes its report to the console.
It does not edit the manifest, notes, Git index or other files.

Use an expected count for a particular checkpoint. The complete-session gate is:

```sh
python3 tools/check_pedal_session.py --repo . --expected-complete 60 --json
```

Run that gate only after the integrator has accepted and recorded all sixty
actual assignments. An incomplete but internally consistent session passes the
ordinary command and fails an unmet explicit expected count. An existing running
note never promotes its assignment to complete. Completion order can reflect
parallel work; records may appear in any order and later waves may be running
while an earlier checkpoint is published.

| Exit code | Meaning |
| --- | --- |
| `0` | All selected-session records are consistent, including any requested exact completed count |
| `1` | Missing/unreadable input, malformed content, inconsistent records or an unmet count |
| `2` | Command-line syntax/type error reported by `argparse`, such as a noninteger expected count |

Human success reports go to standard output; human failures go to standard
error. `--json` emits a version-1 success or failure object on standard output
for normal validation outcomes. CLI syntax errors retain `argparse`'s standard
error behavior. A failure object's diagnostic is bounded to 1,000 characters.

The success report includes declared state counts, distinct dispatched owners,
retained complete/running note counts, each wave's state counts, completed waves,
the selected expected count, the fixed session/baseline identities and an explicit
claim boundary. `completed_waves` counts a wave only when all six slots are
complete.

## Manifest contract

The top-level fields are exactly `schema_version`, `session_id`,
`baseline_commit`, `requested_agents`, `requested_waves`, and `assignments`.
Schema version is integer `1`; session ID is `2026-11-13-pedals`; baseline is
`b4fc61ccfcc59724f14fb0cee947ed7bb7142075`; the request is exactly 60 agents in
10 waves. The checker verifies the recorded baseline string, without fetching
or authenticating Git history.

There are exactly 60 unique integer `assignment` values from 1 through 60.
Wave is `(assignment - 1) // 6 + 1`, giving six slots in every wave. Each record
has exactly `assignment`, `wave`, `state`, `agent`, `scope`, and `note`.
Booleans, duplicate JSON fields, floating-point/nonfinite numbers and additional
fields do not substitute for these types.

| State | Required retained metadata |
| --- | --- |
| `planned` | `agent`, `scope`, and `note` are all `null`; no numbered note claims this slot |
| `running` | A distinct canonical agent identity and nonempty scope; note may be `null`, named but absent, or an unfinished bounded regular file |
| `complete` | A distinct canonical agent identity, nonempty scope and an existing assigned completion note satisfying the checks below |

Canonical worker identities have the form
`/root/w08_a48_session_checker`. Their two-digit wave and assignment numbers
must match their own row. Identities are unique across dispatched slots and
bounded to 256 characters. Scope text is bounded to 1,000 characters, contains
no NUL, and has visible nonwhitespace content.

## Notes, ownership and minimum evidence structure

Notes use a direct lowercase session-local name such as
`48-pedal-session-checker.md`, with the matching two-digit assignment prefix.
Absolute paths, subdirectories, `..`, backslashes, renaming another slot and
noncanonical case/characters reject. Names are bounded to 160 characters.
Duplicate, extra, noncanonical or unassigned numbered notes reject; unnumbered
supporting files such as `README.md` are not assignments.

A complete note must contain:

1. A first top-level title identifying its own assignment. Existing forms such
   as `# Assignment 01: …` and `# 04 - …` are accepted. Ownership metadata may
   precede that title, as in an existing atlas review.
2. An explicit matching owner, agent, worker or actual-assignment line.
   Plain, bold, bullet and backtick forms used by the actual notes are accepted.
   Every canonical `/root/…` identity on such ownership lines must match the
   assigned worker. An incidental reference elsewhere is insufficient.
3. At least two populated second-level narrative sections, each containing at
   least eight word tokens outside fenced examples and ownership lines.

These minimum structural checks help catch a missing, empty or placeholder
report. They do not judge whether the reported work was useful, whether commands
were executed, or whether a conclusion follows from its evidence. The integrator
must review the real scope, changes, commands, observed results, limitations and
next step before changing state to `complete`.

Fenced examples cannot supply the title, ownership or narrative for the report
itself. Running drafts are not subjected to completed-note content checks, which
allows a worker to write its note incrementally. Their names, file type, byte
bound and encoding are still checked if the declared file exists.

## Bounds and platform behavior

| Input | Bound/handling |
| --- | --- |
| Manifest | 64 KiB, exact schema, duplicate-field rejection and bounded integer parsing |
| Each retained note | 128 KiB of original UTF-8 bytes |
| Session directory | At most 256 direct entries; no recursive repository scan |
| Complete assignment set | Exactly 60 unique slots, ten fixed waves |
| Line endings | LF and CRLF accepted; CRLF normalization happens only in memory |

The resolved root's `docs/development/2026-11-13-pedals` components must be real
directories. Referenced manifest/notes must be regular files; symlinks and
Windows reparse points reject. The reader checks file identity/type/size between
path and descriptor APIs and compares full metadata before/after within each
API. This avoids treating legitimate Windows path/descriptor timestamp
representations as a modification. Reads remain byte-bounded, and actual
identity/size or within-API metadata changes reject.

Use a quiescent checkout or frozen archive for a publication gate. The checker
does not provide a hostile-filesystem sandbox or an atomic snapshot of several
concurrently changing files. Native Windows/macOS execution is established by
the relevant hosted results, separately from explicit CRLF and synthetic
cross-API tests performed on Linux.

## Verification and integration

The independent fixture suite is
[`tests/test_pedal_session.py`](../tests/test_pedal_session.py):

```sh
python3 -B tests/test_pedal_session.py
ctest --test-dir build -R '^python_test_pedal_session$' --output-on-failure --no-tests=error
```

The existing CMake Python-test glob registers the suite on a fresh configuration;
it requires no compiled audio or SDK inputs. Fixtures cover honest progress,
all sixty complete, out-of-order records, CRLF, ownership/title/structure,
both older sessions, exact schema and slot identities, path escape, native
symlinks, bounded input, malformed JSON, unchanged bytes and controlled CLI
failures. The actual source archive is also checked without assuming that it
already has sixty completed workers.

The [assignment 48 record](development/2026-11-13-pedals/48-pedal-session-checker.md)
retains its exact commands and observed results. Root's coherent combined gate
and later exact-commit hosted runs provide the subsequent integration evidence.
