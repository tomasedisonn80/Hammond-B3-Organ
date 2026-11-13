# Console integration CI path repair

## Observed checkpoint

Commit `4ead76957c763afbbddde1bc96f1128384329e50` has exact tree
`c4890143cb7ea17bfcd1a8cfcbfdc3733d87784d`. A source archive checked against every
tracked Git blob passed all 30 Release CTest suites locally. The repository check
also passed all five groups with exactly 60 original-session notes. Continuation
notes 01-24 belong to a separate session.

Hosted [run 43369940466](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43369940466)
produced these observed results:

| Job | Result | Failure scope |
| --- | --- | --- |
| Linux GCC Release | Passed | None |
| Linux ASan/UBSan/leak checks | Passed | None |
| Windows MSVC, job 131703098071 | 29/30 suites passed | `python_test_render_fixture` |
| macOS AppleClang, job 131703098109 | 29/30 suites passed | `python_test_render_fixture` |

Both failed jobs ran all 30 suites. Their producer suite reported 47 subtest
failures and one subsequent dictionary lookup error across 27 methods. The lookup
error followed the earlier unsuccessful assertions; it was not an independent
rendering fault. The complete fetched job logs were inspected to isolate the
shared assertion. Engine, contact/percussion, migration, renderer, analytic PCM,
historical demo and independent bundle-verification suites passed on both runners.

## Cause and correction

The producer resolves its output directory before recording invocation paths.
The new exact-argv test constructed expected paths from the caller's unresolved
temporary-directory spelling. Windows supplied a short-name `RUNNER~1` path while
the recorded path used `runneradmin`. macOS supplied `/var/folders/...` while the
recorded path used `/private/var/folders/...`. Both refer to the intended resolved
location, but the test incorrectly required the original spelling.

The test helper now resolves the expected directory before constructing the exact
argument vector. All flags, ordering, numeric strings and filenames remain
checked. Producer and renderer behavior are unchanged by this repair.

A permanent real-render regression uses an existing parent directory followed by
`..`, so the same distinction is exercised on every runner without symlink
privileges. It checks the full success contract and separately requires canonical
profile, WAV and event paths. Before the helper repair it failed on Linux at the
same argv assertion. After the repair, all **28/28 producer methods** passed in
**4.355 seconds**, including that new case and the original integrity protections.

## Qualification boundary

The Linux regression establishes the corrected expected-path policy. A subsequent
hosted run must verify the Windows and macOS behavior before the integration can
claim a complete platform pass. The continuation ledger and development log record
that later result. Passing these software checks does not establish hardware
calibration, native host/device operation or a real-time deadline.
