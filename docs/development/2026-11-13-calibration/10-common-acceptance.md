# Assignment 10: independent shared capture primitive acceptance

- Actual assignment identity: `/root/cal_w2_a10`; calibration wave 2, assignment 10.
- Date: 2026-11-13. Owned paths: this note and
  [tests/test_capture_common.py](../../../tests/test_capture_common.py) only.
- Observed checkout HEAD at assignment inspection:
  `08fa8de8f718584c4ee4ab3b392c779f3290289c`. The common module and acceptance
  suite were uncommitted work; their tested identities are recorded below.
- Scope: independently qualify the public API in
  [CAPTURE_COMMON.md](../../CAPTURE_COMMON.md). Production code, shared status,
  manifests, CMake, git staging and publication remained with the integrator.

## Basis and independent oracles

Read `AGENTS.md`, `CALIBRATION_SCOPE.md`, the complete shared primitive contract
and implementation, active track boundaries, and the current session record.
Inspected repository status and the CMake Python test registration. The new suite
uses the standard library and a direct `unittest.main` entry point; the existing
`tests/test_*.py` glob registers it as `python_test_capture_common` on configure.
This worker did not change CMake or run a native build/CTest qualification.

The principal encoding oracle is a manually written 112-byte literal covering
sorted keys, indentation, booleans, null, negative zero, UTF-8, quotes, newline
and backslash escaping, empty objects and the one final LF. Its source value has
a different insertion order. The reader oracle is a separate 30-byte literal
containing leading/trailing whitespace and an escaped Unicode spelling. These
two byte sequences were written from the contract, not captured from the
implementation. Expected identities use `hashlib.sha256` on these independent
literals, and are checked against actual output/read identities. No model
snapshot, audio hash, producer digest or generated fixture is used as an oracle.

| Independent literal | Bytes | SHA-256 |
| --- | ---: | --- |
| Canonical encoding | 112 | `30bd0bc66882796e8f526dfdd0efa7ffdab92df692bedb10409f2019c770a826` |
| Original JSON spelling | 30 | `4d36aeac1697801a0d110183e875a3d18da6916932282f179ae4b854e83d6e8c` |
| Existing binary-file sentinel | 18 | `d755c55acbdb5addc637edf01badc454765d8a84095bf66a53333efc10c0710c` |

## Executed coverage

The 49 test methods exercise all six public operations and the `DataError`
exception boundary:

- Exact binary reads, empty files, exact byte-limit admission/rejection,
  whitespace-sensitive JSON identity, and forwarding of every read/parse bound.
- Missing/invalid/nonregular paths, real input/output symlinks, dangling links,
  an actual FIFO, permitted ancestor aliases, and controlled reparse metadata.
  Descriptor observations independently reject nonregular/oversized files.
- Controlled changes to every recorded device, inode, mode, size and nanosecond
  timestamp observation, path disappearance, short/oversized reads, and POSIX
  path-versus-descriptor identity mismatch. File contents remain preserved.
- Exact byte input types; malformed JSON grammar; duplicate keys at root and
  nested object/array depths, including equivalent escaped key spellings; BOM,
  invalid UTF-8, lone surrogates and valid paired escapes; preservation of
  distinct Unicode normalization forms.
- Nonfinite/excessive numbers, inclusive custom/default numeric bounds,
  integer/float/Boolean distinction, negative zero and exactly 64-versus-65
  character number tokens. Direct inputs reject tuples, sets, numeric/string/
  container subclasses, bytes-like objects, non-string keys and invalid Unicode.
- Nonmutation, node counting including repeated references, root-container
  depth zero and scalar-leaf behavior, 0/1/32/128 depth edges, direct cycles,
  and controlled parser recursion failure. Maximum option values use small
  inputs; a mocked 16 MiB-plus-one file observation rejects before opening it.
  The suite does not allocate a maximum-size document or million-node graph.
- Repeated deterministic serialization against literal bytes, nested key
  ordering, larger canonical bounds and controlled serialization failures.
- Actual complete publication, exact returned size/digest, a same-directory
  temporary file, and observed write/flush/fsync/close before hard-link creation.
  Existing regular files, directories and dangling symlinks are preserved, as
  is a competing destination installed at the link boundary.
- Temporary creation, stream construction, partial-write-with-error, flush,
  fsync and link failures; descriptor ownership; normal temporary cleanup;
  preservation of unrelated original bytes; and explicit behavior when cleanup
  itself fails before or after publication.

The filesystem hooks wrap actual opened streams or change specific observed
stat values. They do not assert detection of arbitrary concurrent changes that
are restored between observations. Actual symlink/hard-link/FIFO capabilities
are attempted, with explicit capability skips where unavailable; this run had
no skips. Mock reparse metadata is not a native Windows reparse-point test.

## Findings retained from the first implementation

Before the full suite, focused reproductions found four failure cases in two
production areas. The actual initial output was:

```text
cleanup link_failed=False OSError injected cleanup failure target_exists=True
cleanup link_failed=True OSError injected cleanup failure target_exists=False
read_fdopen DataError descriptor_leaked=True
write_fdopen DataError descriptor_leaked=True temporary_exists=False
```

The cleanup branch leaked a raw `OSError`; when link creation had also failed,
the cleanup error hid the primary failure. Failure to construct either read or
write streams left the already-open descriptor owned but unclosed. The worker
reported these reproductions to `/root` without editing production code.

The integrator added explicit descriptor ownership, wrapped cleanup failures,
retained primary and cleanup reasons together, and documented that a complete
published target remains present if removing its temporary name fails. The
suite retains four focused regression methods for these observed defects.
All four pass against the recorded corrected implementation. The initial
failures are not erased by that later pass.

## Verification record and tested identities

Working directory for the commands was the repository root. Executed:

```sh
python3 -B tests/test_capture_common.py
```

The final execution returned exit 0 and:

```text
Ran 49 tests in 0.029s

OK
```

All 49 methods reported `ok`; no skipped test was reported. Runtime was
**CPython 3.12.14**, built with **Clang 22.1.3**, on
**Linux 6.18.57 x86_64 / glibc 2.41**. The earlier full execution also passed
49 methods in 0.024s before small test-only portability/type-coverage edits.

A separate standard-library script computed source/literal identities from
bytes, parsed test literals with `ast.literal_eval`, and checked UTF-8, a final
LF and no trailing whitespace. That command returned exit 0. Relevant tested
file identities were:

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `tools/capture_common.py` | 9625 | `e06dd82e37dd178863af61aa66bee877da1fc7e498a47b729e060215ca79c3f2` |
| `docs/CAPTURE_COMMON.md` | 3923 | `5ae7a7fffb05829c8758d82ac74460ca14834acbe1fa4f2b6e4b1648623bb805` |
| `tests/test_capture_common.py` | 37834 | `02642e399396227234694ad56a4c79cb8c4ceb1262788d4592c0139a67a43df6` |

These hashes identify the files tested here; they do not identify an integrated
commit or establish native-platform, crash-recovery or physical qualification.
Python 3.10/3.11 and Windows/macOS execution were not performed. The test code
uses Python 3.10-compatible standard-library APIs and explicit platform/capability
conditions, which is a portability intention rather than an executed platform
matrix. No new package, runtime dependency or network operation is required.

## Handoff

The corrected public primitives satisfy this scoped independent suite. The
integrator should retain the source identities above, include the suite in the
next coherent configured CTest run, and update acceptance after any subsequent
production/contract change. An inability to remove a temporary file is a reported
failure with the documented residual state, not a promise of universal cleanup.

Artifact confinement remains the caller's responsibility. Adversarial filesystem
sandboxing, crash recovery, directory fsync, multi-file transactions, actual
audio semantics, corpus/split analysis and physical acquisition/calibration are
outside this assignment. Passing these tests does not qualify a specimen or
close any instrument-fidelity gate. No commit, push or shared-ledger modification
was made by `/root/cal_w2_a10`.
