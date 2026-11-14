# Assignment 39 — actual hosted/platform recheck

Actual worker identity: **`/root/cal_w7_a39`**, assignment **39**, logical wave
**7**, in the `2026-11-13-calibration` session. The work was performed on
2026-11-14 UTC without creating another session or recounting earlier workers.

Owned files are exactly:

- `docs/reviews/CALIBRATION_HOSTED_RECHECK.md`.
- This assignment note.

No production source, acceptance test, fixture, schema, shared status/handoff,
ledger, CMake file or Git ref was changed by this worker. Root owns the isolated
demo-fixture repair, integration, acceptance and publication. No workflow was
dispatched/retried and no message was sent outside the collaborating agents.

## Scope and source basis

Read the standing `AGENTS.md`, calibration scope, current project/status/next-step
context, the M0–M9 plan, relevant parallel-track boundaries, original hosted
portability follow-up and both combined-source integration reports. Read the
complete three workflow definitions at the exact published source. Consulted
fresh atlas text on pp. 484–486: predeclared evidence, separate host/device and
release gates, and exact code/setup/result/reviewer change control. This worker
makes no additional complete-PDF or primary-reference review claim; six earlier
actual readers own the session's full 500-page coverage.

The source is published commit
`955fc4c41f74ada094f14fbaf386c943811e9050`, tree
`70956d0f0e125d57abfbf1aed56460c067f8ef28`. The local HEAD and fetched origin/main
were both that commit when independently checked. All hosted source review used
`git show` or `git diff` against named commits, preserving concurrent live replay/
installation work. A tree listing confirms that the new replay/install producers
and acceptance files are absent from `955fc4c`.

## Actual observations and commands

Authenticated read-only GitHub operations retrieved metadata for runs
**43531758072**, **43531758095** and **43531758175**, their job lists, and all
ten complete decoded job logs. The dedicated workflow-job-log operation follows
the documented log redirect; no generic log URL or browser fallback was needed.
Metadata explicitly identifies a push of the source above and run attempt 1.

Local inspection included:

```sh
git show 955fc4c41f74ada094f14fbaf386c943811e9050:.github/workflows/ci.yml
git show 955fc4c41f74ada094f14fbaf386c943811e9050:.github/workflows/standalone.yml
git show 955fc4c41f74ada094f14fbaf386c943811e9050:.github/workflows/native-vst3.yml
git diff 779fb6e13b8f60236cad4aedb9999ba16198f920 955fc4c41f74ada094f14fbaf386c943811e9050 -- tools/capture_audio.py tools/capture_corpus.py
git diff d68058d01272aadeea698a9cf788d261ba822285 955fc4c41f74ada094f14fbaf386c943811e9050 -- tests/test_capture_job.py tests/test_capture_readiness.py
```

The relevant admission and standalone-progress diffs were inspected separately.
Standard-library scripts computed exact committed-source and decoded-log hashes.
No local native build, producer execution or broad test rerun was necessary for
this source/log review. A failing guessed scope-file lookup and a truncated broad
diff were inspection setup issues; the authoritative current pointers and
narrowed relevant diffs supplied the actual scope. They are not project test
failures or executed acceptance methods.

The first observation had Windows Release still running and the macOS jobs
just acquired after their queue. The later metadata exposed the Windows failure;
its full log was fetched before diagnosing it. Subsequent macOS completion and
logs closed every pending job. The final metadata observation at
**2026-11-14 00:14:39 UTC** records **nine completed successes and one completed
failure**, with no pending job. The report provides every ID, URL, toolchain,
actual CTest total and completion time.

## Findings and exact failure preservation

- General Linux Release passes **101/101** suites in **77.59 seconds**; macOS
  Release passes **101/101** in **87.51 seconds**; Linux ASan/UBSan with leak
  checking passes **101/101** in **122.80 seconds**.
- Windows Release passes **100/101** suites in **163.15 seconds**. The original
  Windows audio/corpus canonical-output failures and Windows/macOS path-hook
  failures are resolved by their native suite passes at this source. The new
  failure is solely the demo's native symlink-target spelling assumption.
- All native standalone jobs pass **14/14** suites: Linux **62.46 seconds**,
  Windows **75.65 seconds**, macOS **68.27 seconds**. Their completed workflows
  also retain the actual nine-file installation/relocation/dummy-smoke check.
- Native VST3 passes **8/8** on Linux in **6.68 seconds**, **7/7** on Windows in
  **8.04 seconds**, and **7/7** on macOS in **4.23 seconds**. Linux additionally
  registers `test_native_realtime`; no nonexistent eighth test is credited on
  another platform. The SDK's nested 47-test summary is a different count.
- Core passing-suite stdout is not verbose, so no universal no-skip claim is
  made. Windows native standalone explicitly reports its unsupported FIFO
  subcase as skipped. Dummy devices and real host devices remain separate.

The Windows log identifies
`DemoAcceptance.test_existing_dangling_symlink_is_preserved` at source line 471.
Its `Path.readlink()` returned a `//?/C:/...` Windows namespace spelling, while
the test expected the requested `C:/...` target. The expected generator rejection
and symlink-presence assertion completed before that equality failure; the later
absent-target assertion was not reached. The diagnosis therefore concerns the
fixture's spelling assumption, not demonstrated producer overwrite.

The complete failure log is
`/workspace/scratch/c9f3ead4c910/a39-hosted/955-windows-release.log`,
**264,378 bytes**, SHA-256
`4f8bee84cdc42e003fb6735a0ec1b763544945d640c7253e932c348989e6a190`.
Its public job link and the counterexample are retained in the durable review.
All ten decoded logs are retained locally with exact identities in that review.

Root was notified immediately with the concrete assertion and proposed repair.
The independent installation reviewer was also informed of the native spelling
boundary; that reviewer's snapshots already preserve actual before/after link
strings. Neither notification is an additional worker or a new acceptance test.

## Post-observation root repair

Root subsequently captured the actual native target immediately after symlink
creation and compared that exact value after rejected generation. This reviewer
inspected the diff and verified the live repaired test identity:
**38,714 bytes**, SHA-256
`2ebc86c18997da96b4d70894ca193949d77de7ade68655e4ae4cfcad2ef0904d`.
The original hosted test remains identified as
`c2928c63f8ad11ad550d8aacec84643d82925a6bb8e96085417520ddee3343df`.
No generator or other production source changed for this repair.

Root reported a complete local **43-method pass in 1.223 seconds**, and an
original/repaired native-spelling mechanism probe with one original failure
versus a repaired pass, two reached readlinks and unchanged actual target.
Those are explicitly root's executions, not this worker's independent test
methods or a native Windows pass. The failed `955fc4c` job remains failed;
publication and fresh Windows execution are the next gate.

## Deliverable identities and next step

The completed review at this handoff is 15,103 UTF-8 bytes,
SHA-256 `ec816955f5c87539362f945c5d854161946b2e6a9ad9271b1d37d1353b7cb450`. The scratch final metadata observation is
5,210 bytes, SHA-256 `f2a101324c62e34231f2335423ce7e5a5f33570d33a2b778f1f1b937fc4dc746`.
Both owned documents have UTF-8/LF text and one final newline; exact file checks
and `git diff --check` are documentation verification, not runtime acceptance.

Root should accept the review, retain the original failure and isolated fixture
repair, update shared status/next steps/log/ledger, qualify the next coherent
source including replay/installation, publish under the expected-head guard,
and inspect the new native Windows outcome. Do not transfer the old 101-suite
or native package successes to files absent from that tested tree.

No artifact was downloaded or locally replayed by this worker. No maximum
workload, physical capture/calibration, real-device deadline, every-DAW behavior,
native accessibility, legal clearance, untouched holdout or instrument-fidelity
gate is closed by this review. The useful outcome is exact completed hosted
scope, observed resolution of earlier defects, a preserved new counterexample
and a concrete remaining native recheck.
