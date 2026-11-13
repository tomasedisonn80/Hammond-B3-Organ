# Assignment 59 — final platform and evidence-scope review

Agent: `/root/w10_a59_final_platform_review`

Date: 2026-11-13 UTC. Continuation wave 10. This is one actual assignment;
continuing through the observed CI repair does not create an additional worker.

**Status: complete.** The repaired checker now passes its actual four-platform
hosted gate. This reviewer owns only this note and
[the final platform report](../../reviews/FINAL_CONTINUATION_PLATFORM.md).
Root owns the checker repair, shared status, manifest, staging and publication.

## Scope and source identities

Read the standing instructions, current handoff, plan/status context, prior
platform audit, CI workflow/presets and the allocation, install and benchmark
contracts. Inspected the actual install test, benchmark workload/timing boundaries
and allocation instrumentation. Reread complete extracted atlas pages 379, 383,
385 and 390 for their offline-versus-native qualification boundaries.

The frozen corrected-renderer source was tree
`08d944734efcd1b7a8ed5a93392deabca70a178f`, published as commit
`6bdce067ecdfa2b918113e254ed0ae706fdc9b43`, tree
`6f7948c1cc83945f2ca872b96e668de3796cf8a5`. The tested/published difference is
exactly four Markdown result records. All 35 selected core/build/allocation/
install/benchmark/trace/profile files match the earlier published `2046b93`
byte-for-byte. This does not include the intentionally changed renderer and
accounting tool/tests.

After the observed Windows finding, root published
`7469ebf759ced820cc34fc9012beff6f772e4b89`, tree
`096e2cd13c5aa3fc40e996c923ed80be36b0f622`. I independently verified all **347
archive blobs, 27,360,175 bytes**, against that Git tree. Beyond Markdown and
assignment records, only `tools/check_continuation.py` and
`tests/test_continuation_ledger.py` changed from the preceding candidate. Native
runtime, renderer, headers, build configuration and retained artifacts are unchanged.

## Actual hosted evidence and finding

Through the connected GitHub tools I fetched run/job metadata, actual sanitizer
and Windows job logs, and every retained diagnostic ZIP for:

- **Run 43376892064 / `2046b93`:** all four jobs passed 45/45 suites, with
  24 C++ suites, 21 Python suites and 358 Python methods per job.
- **Run 43380337294 / `6bdce06`:** Linux, macOS and sanitizer jobs passed all
  46 suites. Windows passed 45/46; only `python_test_continuation_ledger` failed.
  Every job executed 371 methods across 22 Python suites. Windows's twelve ledger
  methods had three failures and three errors; all 35 renderer methods passed.
- **Run 43380966473 / `7469ebf7`:** all four jobs passed 46/46 suites,
  24 C++ and 22 Python suites, and 372 Python methods per job. All 13 ledger
  methods and 35 renderer methods passed, with zero failed/disabled/skipped tests.

All twelve downloaded ZIP lengths and SHA-256 values matched GitHub metadata.
The report retains every artifact ID/hash, source SHA, job result and duration.
Complete LastTest blocks agree with JUnit names and CTest totals; the failed
Windows archive contains the matching failed-test list. There are no disabled or
skipped tests. Five passing JUnit outputs are truncated per archive, so method
counts use complete LastTest output rather than the abbreviated XML text.

The accounting failure was independently reproduced in a temporary one-complete-
slot manifest against the frozen uncorrected checker. LF note bytes passed;
explicit CRLF bytes with the same logical content failed canonical owner matching.
Inspection showed that the owner-line capture retained `\r`, while the value
matcher allowed only trailing spaces/tabs. Normalizing the captured line resolved
that match. The observed error and the complete Windows failure remain retained;
they are not a DSP or renderer failure.

Root's narrow correction normalizes CRLF only after the raw-byte bound and UTF-8
decode. I inspected its explicit-byte regression for complete/running notes and
its continued duplicate-owner rejection. It preserves raw byte limits and writes
no input files. Root's [repair record](../../reviews/CONTINUATION_CRLF_REPAIR.md)
retains the new regression's Linux failure before correction and the 13-method
pass afterward. That local result does not replace the hosted rerun.

## Allocation, install and benchmark interpretation

All twelve actual hosted allocation reports agree: zero observed global C++
allocation/deallocation calls for 81 Engine calls, 45 facade calls, six standalone
translation calls, 137 parameter API calls and 14 stopped lifecycle calls.
The independent overload calibration observes 12 allocations and 12 deallocations.
The Engine/facade total is 126 calls and 422,829 elapsed frames. The source and
contract correctly exclude general C/system allocator, lock/I/O, other-thread,
native callback, deadline and concurrency claims.

The installed-tool gate genuinely checks the exact 16-file inventory, moved prefix
and unrelated directory, strips `HAMMOND_*` variables from installed execution,
compares same-build WAV/metadata/CSV/SVG outputs, and rejects missing installed
profiles without fallback. It does not qualify runtime-library bundling, native
plugin/device operation or signed distribution.

The benchmark gate performs six methods and 33 CLI invocations per hosted job;
maximum rational-position error is `1.1102230246251565e-16`. The 122-command
owned schedule has owner counts 122/244/122/0, with physical events only on first
acquisition/final release. Source inspection confirms construction and diagnostics
outside the timed call. Ordered finite observations are checked without a speed
threshold; no worst-case or native scheduling claim is made.

Each complete sanitizer build has 39 instrumented compilation commands and
29 instrumented executable links. Actual test-step environment enables ASan leak
checking, UBSan halt/stacktrace and LSan exit code 23. C++20 and strict warning
flags are present; all three audited sanitizer runs passed without sanitizer diagnostics.

## Audit procedure and limits

Audit intermediates are in `/workspace/scratch/60e8291da354/a59-platform/`.
`audit_archives.py` hashes the downloaded ZIP, checks its source revision, compares
complete LastTest/JUnit/CTest inventories, records Python method counts, checks
skip/failure states and inspects actual sanitizer compile/link flags. Its initial
format assumptions were corrected for Windows CRLF, empty test output, CTest 4's
shorter success summary and uppercase `CL.exe`; these were audit-script issues,
not repository test failures. The known Windows ledger failure is accepted only
as an explicit recorded failed-suite set, never silently counted as a pass.

No broad local suite, device/host run, timing campaign or physical measurement was
repeated. The temporary CRLF reproduction is a bounded independent check. Raw logs
and temporary downloads are not new product assets. Final documentation gets
scoped link, whitespace, encoding and identity checks before it is frozen.

## Final qualification and root's next action

Repaired-checker run **43380966473** completed successfully at `7469ebf7`.
Its four independently verified diagnostic archives agree on every per-suite
method count and contain no failed-test list. Full-suite elapsed times were
24.66 seconds on Linux, 27.36 on macOS, 44.51 on Windows and 42.82 under
ASan/UBSan/leak checking. The report retains all job/artifact identities and the
actual leak-enabled environment. The Windows CRLF failure remains a separate
historical result; no failure was removed from the record.

At this final pre-acceptance snapshot, `check_continuation.py --expected-complete 59 --json`
passed: 59 complete, this one slot still running, zero planned, 60 distinct
dispatched identities and 60 numbered notes. Root alone promotes this slot after
accepting the substantive report; note existence does not perform that transition.

Both owned documents passed scoped links, UTF-8/LF/final-newline/trailing-whitespace
checks before freezing. No additional product change was needed in this review.
Root can accept this substantive final report and transition this actual slot to
complete, then run the explicit 60-complete continuation gate alongside the
separate original-session check. Publish final records with an expected-head
guard and observe that final commit's CI. A documentation/accounting-only final
commit must preserve the qualified code/test/data identities and pass its own
applicable record checks.

No index, staging, commit, push, shared-document or manifest changes were made by
this reviewer, and no subagents were spawned. Full M3, physical calibration and
native product qualification remain open independently of assignment completion.
