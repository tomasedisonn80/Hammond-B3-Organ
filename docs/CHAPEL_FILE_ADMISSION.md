# Chapel file admission across platforms

The [catalog compiler](CHAPEL_PRESETS_CATALOG.md) and
[control-file exporter](CHAPEL_CONTROLS.md) read bounded, nonsymlink regular
files before creating output. Their metadata checks now distinguish observations
made through a pathname from observations made through the opened descriptor.
The documentary model, output bytes, state format and publication policies are
unchanged.

## Observed failure and source basis

Windows core CI at `5b8e2419d23fe27c51709d717812060eafd44dcc` failed several
rewritten-input cases with `input changed before read` or `catalog changed before
its bounded read`. The original readers compared complete `lstat` and `fstat`
tuples directly, including `st_ctime_ns`.

Inspection of the exact runner version's CPython sources confirmed the mismatch.
In [v3.12.10 posixmodule.c](https://github.com/python/cpython/blob/v3.12.10/Modules/posixmodule.c),
`win32_xstat` copies birth time into ctime for the Windows deprecation period;
both path stat functions use it. In
[v3.12.10 fileutils.c](https://github.com/python/cpython/blob/v3.12.10/Python/fileutils.c),
the descriptor path returns metadata change time. A file can therefore remain
unchanged during a read while the two APIs report different ctime values.
The [Python 3.12 documentation](https://docs.python.org/3.12/library/os.html#os.stat_result)
and [upstream issue 157671](https://github.com/python/cpython/issues/157671)
describe the related Windows timestamp distinction. The source inspection does
not substitute for a new actual Windows execution of this repository.

## Admission contract

| Observation | Required agreement |
| --- | --- |
| Selected path versus initially opened descriptor | Exact device, inode, byte size and modification time. POSIX additionally requires ctime equality. Windows ctime is not compared across these two APIs. |
| Descriptor before versus after reading | Exact device, inode, byte size, modification time and ctime. |
| Path before opening versus path after reading | Exact device, inode, byte size, modification time and ctime. |
| File type and reparse status | Both initial and final observations must describe regular files without a reparse flag. Symlink leaves remain inadmissible. |

No timestamp check is removed from the before/after comparison within either
API. The initial compatible cross-API comparison plus both unchanged full stamps
also retains the common identity/size/mtime relationship at the end of the read.
Bounds remain 64 KiB for authoring/catalog inputs and 16 KiB per review CSV;
the returned byte count must match the opened file's observed size. Existing
POSIX no-follow/nonblocking opens, input distinctness and output alias checks
remain in force.

The readers own the raw descriptor immediately after `os.open`. If `os.fdopen`
raises before transferring that ownership to a file object, they now close the
descriptor before propagating the error. Successful wrapping still uses the
file object's ordinary context-manager cleanup. This correction was verified
with a real acquired descriptor, including a failing pre-repair probe.

These are bounded observations, not an atomic filesystem snapshot. Deliberate
metadata restoration, hostile concurrent path replacement and power-loss
durability remain outside the existing contract. The catalog publisher still
uses its validated temporary-and-replace policy; the exporter still uses
new-file-only hardlink publication. Neither policy was changed by this repair.

## Maintained acceptance

Each suite adds a positive Windows ctime-domain fixture and **38 rejection
probes**: one POSIX cross-API ctime mismatch, eight common-field mismatches,
28 descriptor/path changes across both platform branches, and one descriptor
wrapping failure. Post-read mutations cover all five stamp fields, file type
and reparse status; the tests require both post-read observations to be reached.
Fixtures isolate only the producer's OS reference, preserving the host's
`pathlib` behavior and global OS state.

Both suites also overwrite real files with three valid representations and
invoke the actual CLI. Expected catalog semantics and state bytes remain
independent literal oracles. Complete local results on Linux/Python 3.12.14:

| Suite | Result |
| --- | --- |
| Catalog compiler | 23/23 methods, 114 CLI calls, 272 API rejects, five publication fault probes; 6.946 seconds. |
| Control exporter | 20/20 methods, 273 CLI calls, 205 exact-state vectors, 302 API rejects, six publication fault probes; 18.300 seconds. |

Both exited successfully with no skipped methods. The 38 new reader probes are
included in each suite's API rejection count. The canonical 4,837-byte catalog
retains SHA-256 `f500fa0aaca0ba8652eeede330094deb888f6a516b5c51958fd2381778fb5a91`.
Run from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tests/test_chapel_presets.py -v
PYTHONDONTWRITEBYTECODE=1 python3 tests/test_chapel_controls.py -v
```

[Assignment 45](development/2026-11-13-next-phases/45-chapel-windows-reads.md)
retains the original failures, exact source/test/log identities and executed
scope. Root owns canonical CTest, publication and the actual Windows rerun.
Physical preset behavior and factory sound remain outside file admission.
