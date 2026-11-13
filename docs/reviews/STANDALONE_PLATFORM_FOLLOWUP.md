# Standalone checkpoint platform follow-up

This record starts with observed hosted results for published commit
`5b8e2419d23fe27c51709d717812060eafd44dcc`, tree
`880682248c467a51cce14d920189cf0009b68d22`. A successful standalone job does not
override failures in the separate core workflow. Later repairs and reruns must
retain their own source identities.

## Observed core failures

[CI run 43523378849](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43523378849)
completed its Linux ASan/UBSan/leak job successfully. The Linux and Windows
Release jobs built successfully but failed test execution:

| Job | Actual result | Failure |
| --- | --- | --- |
| Linux GCC `132222981693` | 89/90 suites passed, 52.24 seconds | Session concurrency required `counts.raced_discarded > 0` at line 629; this particular scheduling outcome was not observed. |
| Windows MSVC `132222981820` | 87/90 suites passed, 109.52 seconds | Calibration session-record mock, chapel catalog admission and chapel control-file admission. |
| macOS AppleClang `132222981898` | 89/90 suites passed, 86.86 seconds | The same calibration metadata mock failed all three path subcases. |

The Linux concurrency suite printed successful exception-unwind stop/join
cleanup before the later assertion failed. The exact recovery/accounting
assertions before that line did not report a failure. The test must retain
deterministic recovery-boundary coverage and classify every accepted late post;
requiring one incidental scheduler ordering is not a valid portable oracle.
The frozen sanitizer qualification and later repair remain separate evidence.

Windows calibration acceptance reported three subcase failures in
`test_windows_reparse_metadata_rejects_parent_and_leaf_aliases`; the checker
returned `passed` because the injected metadata marker was not encountered.
The fixture used the runner's `RUNNER~1` temporary path, while the checker first
resolves the repository root. Root repaired the test fixture to mark that same
resolved path and added an assertion that its injected metadata was actually
observed. The production checker and rejection policy are unchanged. The full
27-method suite passed locally in **0.904 seconds**; actual Windows rerun is
still required. The original run also records one platform-specific fixture skip.
The later macOS log shows the equivalent `/var` versus resolved `/private/var`
temporary-root alias. The same resolved-fixture repair addresses that path form;
actual macOS verification is also required.

Windows chapel catalog acceptance failed three cases and errored one while
reading rewritten inputs; messages were `input changed before read`. The
exporter suite failed its rewritten-catalog boundary case with `catalog changed
before its bounded read`. Existing immutable/catalog/native audition cases
passed, which narrows the defect but does not excuse these failures.

Both readers compared a full path `lstat` tuple directly to a descriptor `fstat`
tuple, including `st_ctime_ns`. Python documents Windows ctime deprecation, and
the upstream [CPython issue 157671](https://github.com/python/cpython/issues/157671)
records differing creation/change-time semantics across those APIs. The
[Python 3.12 stat documentation](https://docs.python.org/3.12/library/os.html#os.stat_result)
also separates birth time and metadata-change time. These sources inform the
repair; they do not independently execute this repository's Windows regression.
The required correction must keep full before/after stamps within each API,
compatible cross-API file identity, size/mtime checks, bounded reads and rejection
of observed replacement, mutation, symlinks and reparse points. No unsupported
hostile-filesystem race guarantee is introduced.

## Qualified narrow repairs

The [chapel reader repair](../CHAPEL_FILE_ADMISSION.md) now compares compatible
cross-API identity fields while retaining all five fields in each API's own
before/after stamps. Both readers also close a raw descriptor when stream
wrapping fails. Pre-repair probes reproduced false rejection and descriptor
leakage; repaired complete suites passed 23 catalog and 20 exporter methods,
with 38 new reader-rejection probes apiece and unchanged canonical output bytes.

The [concurrency oracle repair](STANDALONE_CONCURRENCY_PORTABILITY.md) preserves
64 recovery epochs, with four controlled boundary schedules and sixty concurrent
ones. All 5,760 concurrent late attempts must reconcile; the test no longer
demands an incidental positive outcome. First Release and coherent TSAN runs
passed, with all 23 TSAN objects instrumented and no race report. Session/core
production files are unchanged.

Root rebuilt the exact concurrency/catalog inputs and ran the canonical chapel
catalog, chapel exporter, calibration-record and concurrency suites together:
**4/4 passed**, total **17.28 seconds**. Per-suite times were 6.71, 17.28, 1.72
and 0.15 seconds respectively. The generated catalog retains its original
4,837-byte SHA-256 `f500fa0aaca0ba8652eeede330094deb888f6a516b5c51958fd2381778fb5a91`.
This Linux integration does not substitute for the repaired Windows/macOS runs.

## Follow-up gates

Native standalone Linux `132222980756` and Windows `132222981043` finished
successfully, including tests, installation/relocation and package upload.
macOS `132222981098` failed compilation before tests/package steps: AppleClang
treated unused `kPanel` and `kLine` namespace constants in `InstrumentView.cpp`
as errors under the existing strict warnings. Root removed those two unused
declarations. No drawing expression, color used by a control or runtime branch
changed. Actual macOS compile/test/package qualification still requires a rerun.

Retain the original failures above, qualify each narrow repair locally, publish
the completed changes and inspect actual Windows/Linux/macOS reruns. The
separate Native standalone run `43523378962` already demonstrated the earlier
Windows compilation repair through successful build, tests and package steps;
its complete per-platform result and artifacts need a named final audit. Real
desktop/audio hotplug, callback deadlines, native accessibility and physical
fidelity remain outside these hosted dummy-driver checks.
