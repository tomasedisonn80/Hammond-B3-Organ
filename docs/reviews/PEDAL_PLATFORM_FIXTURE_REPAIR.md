# Native inventory regression fixture portability repair

## Observed published-source failures

This repair follows published/fetched commit
`feefe83be6df8cda8bcfc7f7292fdee9913aa8a1`, exact tree
`c5090f0786eb87019c964f45c254b0e30a859088`. Root independently observed every
job completed before preparing another publication, so no pending run was
cancelled to obtain these results.

| Actual job at that revision | Result |
| --- | --- |
| [Core Linux 131878608461](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43423372813/job/131878608461) | 71/71 passed, 55.53 seconds. |
| [Core sanitizers/leaks 131878608120](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43423372813/job/131878608120) | 71/71 passed, 124.34 seconds. |
| [Core macOS 131878608364](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43423372813/job/131878608364) | 70/71, 62.86 seconds. Two failed subtests in the inventory suite. |
| [Core Windows 131878608488](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43423372813/job/131878608488) | 70/71, 76.76 seconds. Four failed subtests plus one error in the inventory suite. |
| [Native Linux 131878608871](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43423372834/job/131878608871) | 8/8 passed, 6.87 seconds; actual bundle/inventory uploaded. |
| [Native macOS 131878608877](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43423372834/job/131878608877) | 7/7 passed, 5.86 seconds; repaired concurrency cleanup and actual bundle/inventory passed. |
| [Native Windows 131878608531](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43423372834/job/131878608531) | 7/7 passed, 7.32 seconds; actual bundle/inventory uploaded. |

The failed core jobs attempted all 549 Python methods across their 33 Python
suites. They are not full-matrix passes. All actual native payloads and their
complete logs were independently inspected by assignment 59; exact artifact
records are retained in that final platform audit. The validator still reports
47 passed/zero failed with its documented 16 teardown, nine unsupported-rate
and 15 float64 messages. The earlier native macOS compilation failure and
portable stop/join helper are preserved in the
[preceding repair record](PEDAL_REVIEW_REPAIR_INTEGRATION.md).

## Concrete causes and bounded correction

Only `tests/test_native_bundle_inventory.py` changes executable content.
`tools/native_bundle_inventory.py`, all production C++/SDK/CMake inputs, native
fixtures and source data remain unchanged.

1. **Aliased temporary roots:** macOS's `/var` alias and Windows's short 8.3
   temporary path can differ textually from the canonical paths used by the
   inventory walker. Synthetic metadata patches selected the unresolved spelling,
   so two descendant/module probes missed their intended files. Root probes still
   worked. The test setup now resolves its existing temporary directory before
   creating the fixture. Deliberate root/file/directory symlinks and actual
   junctions remain distinct explicit rejection cases.
2. **Actual Windows command quoting:** embedding the whole `mklink` command in
   one argv entry introduced escaped nested quotes. The test now passes
   `cmd.exe`, `/d`, `/c`, `mklink`, `/J`, alias and target as separate arguments.
   This is test-process construction only; production inventory does not invoke
   `mklink` or a shell.
3. **Synthetic Windows metadata:** constructed `os.stat_result` values can expose
   `st_file_attributes=None`, unlike the real path metadata admitted here. The
   special-file and denied-symlink fallback fixtures now retain the actual identity,
   size and timestamps with their synthetic mode and explicit integer attribute
   word zero. Production reparse rejection and all stability checks are unchanged.
4. **Truthful success marker:** unittest subtests continue after failures, so the
   previous text marker could print even when a junction case failed. An explicit
   counter must now equal two after successful creation, rejection, alias-only
   cleanup and target preservation before the real-Windows-junction marker prints.
   Complete passing test evidence remains required in addition to that marker.

The old fixture reproduced the two macOS-style failures locally under a real
symlinked temporary parent. That negative-control log is retained; it was not
silently replaced by the repaired result. No actual local Windows execution is
claimed from Linux command serialization.

## Qualified inputs and actual local results

The qualified input tree is
`43ac9f5ae25e30f91b45279995ef44ecf01c357e`: published `feefe83` plus this single
test file, Git blob `75d9b06205afbad0f4be467e6b6c3f894ba648b8`.
The test is 26,365 bytes, SHA-256
`0f5e64922be14d4aa0f6565989c0314798549c4f80551d68dbc450fb7f79fa92`.
Root compared the working file with the independently frozen tested copy and
confirmed the production tool still exactly matches the published blob, SHA-256
`ee46f979cb3070dcf39d976ab657be974d937f89e835a7927b384dcc755ad4a7`.
Final publication adds only this report and the chronological log to that tree;
unfinished final-session documents and live assignment metadata remain excluded.

| Executed local check | Result | Retained log SHA-256 |
| --- | --- | --- |
| Full inventory suite, ordinary temporary directory | 20/20, 0.410115 seconds | `e29de6da8367f3699554bbc34a692dde88383d2d69ae2443807d88f5cefbc36a` |
| Full inventory suite under a real symlinked temporary parent | 20/20, 0.360312 seconds | `b995434e0668764b8e10ffb0bd8c8fa9b74c819cbe1f4d3e5ea3535448a88e71` |
| Forced synthetic special-mode fallback | 1/1, 0.000987 seconds | `4f1d12a0667a27f2cd083fed6e0cd0ce2722f0d900c799cf2d87f08963fd5f96` |
| Forced denied-symlink fallback | 1/1, 0.001008 seconds | `842df7873c3b837f8c53eba095f501eb5aa23c94358907deaa8561bf57af9b39` |

Every execution had zero failures, errors or skips. The command-list inspection
used the actual test AST and Python's Windows command serialization with paths
containing spaces; it retained separate alias/target quoting and no escaped nested
quotes. This is source/serialization inspection, not Windows command execution.

Receipts are `a59-final-platform-audit/fixture-repair-results.json`, the four
named logs, `macos-alias-negative-control.log`, and the independently frozen
`fixture-repair/source-proof.json` plus root's `root-source-proof.json`.
The permanent regression is executable from the repository root:

```sh
python3 tests/test_native_bundle_inventory.py
```

## Next observed gate and publication rule

Publish the exact repaired tree with an expected-parent reference update, fetch
and compare its tree, then inspect the new core/native runs. Require actual
macOS inventory success and Windows creation/rejection/cleanup of both junctions
with zero failures in the complete inventory suite. The already passed native
module execution remains scoped to its own source; no later result is assumed.
Preserve both failed core jobs and every actual follow-up outcome in the final
platform audit and current status before closing the session.
