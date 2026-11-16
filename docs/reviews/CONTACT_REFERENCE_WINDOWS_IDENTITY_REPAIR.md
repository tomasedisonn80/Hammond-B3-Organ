# Contact reference: Windows input identity repair

Author: `/root/w08_a45`, actual worker A45, Wave 8 of the streaming/material
continuation. Scope: the strict offline input boundary and its focused tests.
Root owns independent acceptance, the coordinated build, numerical requalification
and publication; A47 independently reviews this patch.

## Failure and primary-source diagnosis

At published source `af2b74760ee195c9497b314a1a29172f5238dd44`, Windows core
Release job `133024356072`, workflow run `43783034126`, used official CPython
**3.12.10 x64** and passed 184 of 185 CTests. The relocated-install method
`test_moved_package_runs_cli_and_full_study_admission_without_source_or_build`
failed at its single-fixture CLI invocation with
`contact-switching: input changed after path preflight`. The six new causal
suites passed. The original [failure receipt](../development/2026-11-15-streaming-continuation/reports/windows-core-af2b747-failure.json)
and [complete compressed log](../development/2026-11-15-streaming-continuation/reports/windows-core-af2b747.log.gz)
remain unchanged. The decoded log contains 526,325 bytes, SHA-256
`2858f8f90bb79736630bf72b0fdaca93156baf9f8496afe83cb7500adc47ba6d`.

The old preflight stored the complete `Path.stat()` tuple and compared it with
`os.fstat()` in `load_input()`. Inspection of the exact interpreter release
establishes that these APIs do not give the same meaning to every field:

- [CPython v3.12.10, `Python/fileutils.c`](https://github.com/python/cpython/blob/v3.12.10/Python/fileutils.c):
  `_Py_attribute_data_to_stat` maps Windows `CreationTime` to birth time and
  `ChangeTime` to `st_ctime`; `_Py_fstat_noraise` returns that descriptor result.
- [CPython v3.12.10, `Modules/posixmodule.c`](https://github.com/python/cpython/blob/v3.12.10/Modules/posixmodule.c):
  `win32_xstat` replaces `st_ctime` and its nanoseconds with birth time for
  compatibility. `os_fstat_impl` does not make that replacement. The path API
  also synthesizes execute bits for selected filename extensions.
- [CPython issue 157671](https://github.com/python/cpython/issues/157671)
  independently reports the path/descriptor timestamp mismatch on Windows and
  recommends consistent descriptor comparisons retaining both change and
  modification times. Its example concerns 3.14; the exact 3.12.10 source
  inspection above establishes applicability to this job.

These are source-level facts, not assumed filesystem timestamp rounding. The
original CI log does not print the individual stat fields; it cannot establish
their exact differing values. The portable regression reproduces the identical
diagnostic with distinct, stable path and descriptor change-time values. A fresh
Windows run at the repaired source remains required to close the hosted failure.

## Repair and preserved boundaries

[`contact_switching_io.py`](../../tools/contact_switching_io.py) now obtains the
input preflight token from an opened, read-only descriptor. Preflight checks the
descriptor's regular-file type and 256-KiB limit, verifies its device/inode against
the admitted path, and compares the full path signature again while the descriptor
is open. The descriptor closes in a `finally` block. The original path token is
retained separately in the immutable `OutputPlan`.

The signature still contains **device, inode, mode, size, modification time in
nanoseconds and change time in nanoseconds**. No field is removed or rounded, and
there is no Windows-specific acceptance bypass:

| Boundary | Comparison retained or added |
| --- | --- |
| Path admission through descriptor acquisition | Full path-to-path signature, plus device/inode identity between path and descriptor; both types and sizes admitted |
| Preflight through input load | Full descriptor-to-descriptor signature |
| Before and after bounded input read | Full descriptor-to-descriptor signature, including change time |
| Before temporary creation and before replacement | Fresh complete preflight compared with both original input signatures, original output signature, paths and parent identity |
| Input/output aliases | Existing resolved-path, hardlink, symlink and device/inode rejection preserved |
| Descriptor ownership on failure | Preflight closes raw descriptors; failed `os.fdopen` construction in `load_input` now also closes its raw descriptor |

The open flags remain read-only, binary where supplied, and nonblocking where
supplied. No report file is created before complete admission. Atomic replacement,
temporary cleanup, JSON/schema/domain/resource checks, source hashes and finite
report checks keep their previous behavior. This remains a metadata consistency
protocol with final-check-to-replacement race limits; it does not claim an atomic
transaction against an adversarial writer that can replace paths or forge all
metadata between observations.

## Focused verification

All commands ran from
`/workspace/scratch/177e78b1ac09/Hammond-B3-Organ`, with selected Python
`/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3.12`,
version **3.12.14**, Linux x86-64, and `PYTHONDONTWRITEBYTECODE=1`.

Before production changes, the eight new focused methods ran against the original
I/O module. They retained eight failing assertions/subcases, including the exact
Windows diagnostic, and exposed the existing descriptor leak when stream-wrapper
construction fails. The [before receipt](../development/2026-11-15-streaming-continuation/reports/A45-before-repair-tests.json)
binds the [unaltered log](../development/2026-11-15-streaming-continuation/reports/A45-before-repair-tests.log)
and its source/test identities. Some new negative cases explicitly require the
new descriptor-preflight boundary and therefore fail on the old implementation;
they are not additional observed hosted failures.

After the repair:

```sh
/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3.12 \
  -B tests/test_contact_switching_io.py -v
```

The [after receipt](../development/2026-11-15-streaming-continuation/reports/A45-after-repair-tests.json)
and [original log](../development/2026-11-15-streaming-continuation/reports/A45-after-repair-tests.log)
record **39 methods, 38 passed and one existing facility skip, in 0.911 s**.
The Unix-domain socket test could not create a socket because the environment
returned `EPERM`; it is not counted as executed acceptance. The eight added methods
exercise stable divergent timestamp/mode views, real rewritten input with restored
mtime, descriptor-only change-time mutations before load/publication and during
read, real in-read content mutation, same-byte file replacement, a wrong opened
file, path-only change-time mutation, and descriptor cleanup on exceptions.
Existing direct/hardlink/symlink aliases, path and parent mutation, work/storage
limits, report integrity and atomic-write failure cases also remain in this suite.
`git diff --check` passes for the two changed Python files.

No native build, broad CTest run, relocated-install acceptance, complete numerical
study, or Windows/macOS execution was performed by A45. Root owns those affected
integration and hosted gates. A47's independent review has its own evidence.

## Source identities and historical evidence

| File | Before SHA-256 | Repaired SHA-256 |
| --- | --- | --- |
| `tools/contact_switching_io.py` | `e3219265f1496a36b4f5d8a13941672b46ddc4116f331b7a1b99115a2dac9dc6` | `1281cd0726a6cf16dcc0ceea8445b4e42900ed995bb82dfea70c6dffdd104cc6` |
| `tests/test_contact_switching_io.py` | See Git source at `af2b747` | `ade725edc0d0b3f99714e10363f98c6454bacd7ed927698393fb2f1ed6410b81` |

The [preservation receipt](../development/2026-11-15-streaming-continuation/reports/A45-preservation.json)
compares **114 files** against `af2b747`: 113 are byte-identical, and only the I/O
module differs within that inventory. All **48 installed payload names** remain;
the other 47 payload files, numeric kernel, fixture/probe bytes, installers,
frozen tolerances and original execution-session reports are unchanged.

The existing [results page](../CONTACT_SWITCHING_RESULTS.md) and qualified study
retain the old I/O source hash. This patch does not rewrite or silently rebind
those results. Newly generated reports compute the new I/O implementation hash
automatically. A changed-source numerical or installed qualification needs a new
receipt and must preserve the earlier reports and their source identities.

If the fresh Windows job still rejects an unchanged input, retain that job's log
and capture one bounded diagnostic on the exact failing fixture: interpreter
version, `os.path.samestat(path_stat, fd_stat)`, and the six signature fields from
path-before, descriptor-before, descriptor-after and path-after. Read at most
256 KiB plus one byte and leave the report destination untouched. Compare the
observed differing field with the exact runtime source before further edits.
