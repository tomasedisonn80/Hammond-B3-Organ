# A56 combined indexed-array regressions

The two resolved test files passed their first source-only invocations on 2026-11-17: **71/71 P1 tests** and **41/41 header tests**, with no skips or retries. All nine test/tool/reader/fixture inputs were identical before and after execution, and remained identical when this report was written. This is the same A56 worker continuation, with no additional ledger credit.

## Source reconciliation

The inputs are local candidate `4378fff74a3a11de400e3a38b877d170bad6c57e` and published source `54859886268ce83c36f359c43327f7c72a77ae82`. The complete merge-base, local-qualified, published, and initial conflict files are retained as compressed byte archives. No merged commit is claimed here.

| Test file | Published methods preserved exactly | Distinct additions | Final methods | SHA-256 |
| --- | ---: | ---: | ---: | --- |
| `tests/test_compare_performance_plate.py` | 64 | 7 | 71 | `edcf02e99ce66a9910e8f3173d6a66e929390321280581678e91fb277f93a4ba` |
| `tests/test_compare_header_material.py` | 32 | 9 | 41 | `b33b44d2a2459a274fad35580e0a9ce08fb6b3df834b388b51fa98e01a1473e4` |

All 96 published test method bodies are AST-identical in the resolved files. The original 54 P1 method bodies remain identical. Of the original 24 header methods, the published current-checkout assertion intentionally expanded to admit the exact indexed fixture and its repair variant; that complete published expansion is preserved, as are the other 23 original method bodies. Published setup reconstructs historical sources while retaining the actual indexed current checkout. Temporary historical ROOT redirection from the earlier local candidate is not carried forward.

## Admission policies covered

P1 uses the published public constants and `p1-helper-constexpr-else-indexed-array` metadata. The exact indexed fixture reverses through the helper-only predecessor to the genuine original. Indexed and helper-only fixtures remain candidate-only; the original fixture remains valid in both modes. The additions exercise independently reviewed constants, strict byte types, repinned structural mutations, relocation, unrelated bytes, simultaneous intermediate repinning, incorrect complete identity and an identity/read race.

The published paired H1 comparator intentionally admits the exact indexed `8c8226...` → helper `86acc0...` → cast `96149c...` → genuine original `a6b65d...` chain. The old local test that expected indexed H1 rejection is therefore replaced by positive chain agreement between readers and a negative simultaneous-repinning case. The genuine paired baseline remains required. Earlier local receipts describe their earlier candidate policy and remain immutable.

Both standalone readers keep the active indexed `FIXTURE_SHA256` and separately expose the historical `ORIGINAL_FIXTURE_SHA256`. Tests bind both identities, whole-file reversal, strict source types, refusal before process access, and stability after mocked capture. The empty second drawbar bank and boolean-for-integer substitutions remain invalid. Mocked capture cases do not claim native or numerical execution results.

Overlapping local P1 positive/schema/type/post-pin/prelaunch tests are represented by the unchanged published cases. Only distinct additional risks are added; existing refusal expectations are preserved.

## First execution evidence

| Suite | Result | Unittest time | Process time |
| --- | --- | ---: | ---: |
| P1 | 71 individual `ok` records; exit 0 | 0.703 s | 1.011 s |
| Header | 41 individual `ok` records; exit 0 | 0.746 s | 1.083 s |

The two authorized invocations ran once each on Linux with Python 3.12.14, from 07:49:03.489 UTC to 07:49:04.576 UTC. Complete stdout/stderr, exact commands, source hashes and before/after identity checks are in `source-only-qualification.json`. No further tests were run while preparing this report. `source-preparation.json` deliberately retains its earlier `tests_executed: 0` snapshot.

## Files and limits

`combined-indexed-regressions-report.json` records the policies, source retention and execution results. `combined-from-published.patch` contains the resolved additions relative to the complete published files. `retained-inputs.json` binds each compressed stage archive to its byte and Git-blob identities. `evidence-inventory.json` hashes all evidence files other than itself.

A56 changed only the two assigned tests and this new evidence directory, and performed no staging, commits, ref changes, CI requests, native execution or builds. The earlier accepted A56 note and source-specific Core/array reports were verified unchanged. Source-only passes do not establish Windows/native/sanitizer or later published-source acceptance. Root owns the affected qualification and final acceptance; A59's independent source review is recorded separately.
