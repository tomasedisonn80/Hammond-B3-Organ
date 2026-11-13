# Assignment 59 — exact published platform gate and portable test cleanup

Owner: `/root/w10_a59_final_platform_gate`.

Assignment **59/60**, wave **10**, current pedal/native session. This worker
actually dispatched and acknowledged the task despite the spawning UI's aborted
label. This is one assignment; no replacement worker or subagent was spawned.

## Status and ownership

The assignment is complete: the exact final audited publication
`0ad7240a88803de9d97bc265a8fd2b6e5d5d7e2b` passed all four core and all three
native jobs, with the actual Windows two-junction output and ten independently
verified artifacts. Root owns acceptance of this record and the separate
sixty-complete ledger; this note does not claim that final metadata was already
published.

Initial ownership was this note and
[PEDAL_FINAL_PLATFORM.md](../../reviews/PEDAL_FINAL_PLATFORM.md). After this
worker observed and reported the real macOS build failure, root explicitly
authorized the additional single-file repair in
`plugins/vst3/tests/test_native_concurrency.cpp`. A subsequent actual core CI
failure led to explicit authorization for the fixture-only correction in
`tests/test_native_bundle_inventory.py`. No other code, shared status,
manifest, CMake, workflow, SDK or dependency setting was edited. No staging,
commit, push, job retry or cancellation was performed by this worker.

## Actual work and evidence

Read the repository's current agent rules, operational handoff, active status/
next steps/plan, exact core/native workflows and relevant inventory/concurrency
source and prior platform records. Read the cloud runtime and networking
guidance; no environment-status tool was exposed and the documented network
policy snapshot was absent. Existing authenticated GitHub connector reads and
normal supplied download routes worked. No credential, network or toolchain
configuration was changed.

Independently compared every file byte and executable bit in frozen wave-9 tree
`a8817841a0a348b6b742dfeb6668249aa9692a54`: all 549 tracked regular files match
and the snapshot had no extras. Compared its actual Git delta to qualified
wave-8 tree `5370890e32045a556cb61a88cdb1f04fb5a18f7e`; only the manifest and
the two inventory Python files are non-Markdown changes. Inspected the root's
retained two-suite/44-method local inventory/session result without converting
nonexistent regex aliases into tests.

Fetched the actual attempt-2 job metadata, full macOS core/native job logs and
artifact metadata for runs **43417681825** and **43417681882**. Downloaded core
artifact **14034700785** and native failure artifact **14034960204**, verified
their ZIP byte lengths and SHA-256 values, rejected unsafe ZIP paths/links,
and retained individual member hashes. The core last-test log independently
contains **71 passing suites / 548 Python methods / 57.99 s**. The native build
log establishes missing Apple standard-library `stop_token`/`jthread`, exit 2,
and no native CTest or bundle qualification. The review records exact IDs,
source/tree, toolchain, artifact hashes and the distinction between prior
runner-acquisition failure, actual code failure and copied job metadata.

## Focused repair commands and result

The exact one-file overlay is frozen at
`/workspace/scratch/f364bc93d920/a59-final-platform-audit/repair/source` over the
wave-9 tree. Overlay SHA-256:
`d261ad69d0199cd5da4a9b2f050a7416b2c515c7838f8f26d3a036c9c8b8f0cc`.
It keeps cooperative stop and exception-unwind stop/join behavior using a
nonmoving test-local owner, and adds a bounded actual unwind-cleanup probe.

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake -S /workspace/scratch/f364bc93d920/a59-final-platform-audit/repair/source -B /workspace/scratch/f364bc93d920/a59-final-platform-audit/repair/build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON -DHAMMOND_BUILD_VST3=ON -DHAMMOND_VST3_SDK_ROOT=/workspace/scratch/f364bc93d920/vst3sdk
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake --build /workspace/scratch/f364bc93d920/a59-final-platform-audit/repair/build --target test_native_concurrency --parallel 2 --verbose
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/ctest --test-dir /workspace/scratch/f364bc93d920/a59-final-platform-audit/repair/build -C Release -V --no-tests=error --timeout 240 -R '^test_native_concurrency$' --output-junit /workspace/scratch/f364bc93d920/a59-final-platform-audit/repair/ctest.xml
git diff --check -- plugins/vst3/tests/test_native_concurrency.cpp
```

Fresh configure **1.402 s**, fresh native dependency build **32.341 s** and
focused CTest **1/1 passing in 0.33 s**, all exit zero. JUnit has zero failed,
disabled or skipped cases. Actual output contains the exception-unwind stop/join
marker and preserves the full three-rate concurrent workload; maximum audio
error remains zero across 64,207 compared audible frames and 6,168 future frames.
The new local module hash equals the earlier local Linux module hash because
the change is confined to the test host; no cross-platform byte-identity claim
is made. Full command arrays, exact source overlay, toolchain/configure/build
logs, JUnit and hashes are retained in `repair/results.json`,
`repair/source-overlay.json` and `repair/qualification.json` beneath the audit
directory. Root received the frozen file and successful result before publication.

Post-build inspection verifies the same 549 tracked file bytes/modes and the
single intended overlay. Two generated Python cache files now exist under the
private source's `tools/__pycache__`; they are retained, hashed separately and
not treated as code changes. Root's independent setup initially stopped because
the reported blob hash had not been stored as a Git object, then because its
strict whole-directory assertion found these caches. The overlay hash was
computed with `git hash-object` without `-w`; no stored-object claim was made.
Root records those setup stops and binds the actual tracked tree before
publication. This worker's own post-build proof is
`repair/post-build-source-proof.json`.

## Subsequent actual hosted fixture failure and repair

At published `feefe83be6df8cda8bcfc7f7292fdee9913aa8a1`, all three native
platforms passed their actual gates and uploaded verified bundles. The four core
jobs completed: Linux and sanitizers passed 71/71; macOS and Windows passed
70/71, failing only the inventory suite. All four actual last-test logs contain
549 attempted Python methods. The review preserves exact jobs, counts, times,
all actual downloaded artifacts and the warning-bearing native validator result.

The failures revealed unresolved-versus-canonical temp paths, incorrectly nested
Windows command quoting, and incomplete synthetic special-mode metadata. Root
authorized correcting these fixtures only. An actual local symlink-parent
negative control reproduced the two macOS failures. The repaired normal and
same-alias setups each passed all 20 existing inventory methods, with no skips.
Two forced one-method runs separately passed the synthetic FIFO and denied-link
fallback paths. The Windows command expression was inspected from the actual
AST and serialized with Windows argument rules; no local Windows runtime claim
is made. A two-success counter now prevents a failed subtest from printing the
actual-junction success marker.

Frozen repaired test SHA-256:
`0f5e64922be14d4aa0f6565989c0314798549c4f80551d68dbc450fb7f79fa92`.
Production `tools/native_bundle_inventory.py` remains
`ee46f979cb3070dcf39d976ab657be974d937f89e835a7927b384dcc755ad4a7`.
The exact one-file diff, before/after identities and frozen file are in
`a59-final-platform-audit/fixture-repair/`; full normal/alias/fallback execution
records and command inspection are in `fixture-repair-results.json`. Actual
failed Windows/macOS logs and diagnostic ZIPs were retained before publication
of the next repair. All seven preceding jobs had completed, so no pending job
needed cancellation.

## Final integration and acceptance boundary

The final inspected source tree is `41c0b421643d4076c65ecbac8a750b4aae4d5806`;
its exact qualified input tree is `43ac9f5ae25e30f91b45279995ef44ecf01c357e`.
Independent Git comparison finds only two Markdown result additions/updates
between them. Both final workflow APIs report completed/success at attempt 1,
with all seven actual jobs successful and real runner/step records. No audit
retry, cancellation or runner-label change was needed.

| Final job | Job ID | Actual result | CTest wall time |
| --- | --- | --- | --- |
| Core Linux | 131883228381 | 71/71; 549 Python methods | 57.00 s |
| Core macOS | 131883228283 | 71/71; 549 Python methods | 53.76 s |
| Core Windows | 131883228028 | 71/71; 549 Python methods | 69.71 s |
| Core ASan/UBSan/leaks | 131883228687 | 71/71; 549 Python methods | 133.30 s |
| Native Linux | 131883229118 | 8/8; two install Python methods | 6.55 s |
| Native macOS | 131883229476 | 7/7; two install Python methods | 4.47 s |
| Native Windows | 131883229403 | 7/7; two install Python methods | 4.23 s |

Each final JUnit has zero failed/disabled/skipped tests. All four full core logs
contain 33 Python summaries and 549 methods; counting only truncated JUnit output
would give 357. The Windows inventory suite passes all 20 methods and contains
the real two-junction marker guarded by the explicit success counter. All three
native logs contain the exception-unwind stop/join probe and unchanged three-rate
workload. Every validator retains 47/0 plus 16 teardown, nine unsupported-rate
ERROR and 15 unsupported-float64 informational diagnostics. Final API/artifact
observation time was 2026-11-13 12:27:16 UTC.

The four core diagnostic ZIPs and three native bundle/diagnostic pairs were all
downloaded and matched to fresh API run/source, sizes and SHA-256 values. All
16 regular native tar members match complete bytes/modes/hashes, with identical
build/staged inventories, exact source/tree/attempt provenance, five locked SDK
checkouts/licenses and one exact embedded nominal profile per module. Full
artifact, module and complete-log hash tables are in the companion review.
The two earlier macOS retry ZIPs and ten preceding `feefe83b` ZIPs remain
separately identified; the final result does not overwrite their failures.

The inspection used the actual GitHub run/jobs/artifacts/job-log read endpoints,
then a bounded independent ZIP/tar parser and XML/full-log parser. Inspection
scripts, exact receipts and all downloaded bytes are retained under the audit
directory. The final consolidation command was:

```sh
python3 /workspace/scratch/f364bc93d920/a59-final-platform-audit/final_audit.py
```

It asserts all seven exact-source job results, all ten API-matched ZIPs, complete
suite/method counts, real Windows marker plus successful suite, native cleanup
and validator diagnostics, SDK/source/package correspondences and the actual
sanitizer compile/environment policy. It exited zero. This parses retained
execution and package evidence; it does not rerun the hosted product tests.

Root can now accept assignment 59, update its final actual sixty-worker ledger
and status/next/log/handoff, run the affected final metadata checks, and commit/
push with an expected-head check. Preserve this source-qualified result and
explicitly describe any final documentation/ledger-only delta. Native Linux's
allocation/interposition test is not registered on Windows/macOS; no skipped
platform test is hidden by that distinction. Signed distribution, rights,
DAW/device behavior, deadlines and physical calibration remain separate gates.
