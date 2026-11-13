# Assignment 21 — independent fixed-policy acceptance

## Actual assignment and ownership

**Canonical identity:** `/root/cal_w4_a21`, assignment 21, calibration wave 4.
This is one distinct newly dispatched acceptance assignment in the current
sixty-assignment session. It is separate from policy producer 20, metric producer
15 and metric acceptance worker 18. Earlier workers are not recounted here.

Owned files are only:

- `tests/test_capture_policy.py`
- `docs/development/2026-11-13-calibration/21-policy-acceptance.md`

**Result:** the final independently authored suite passed **49/49 methods**,
with zero failures, errors or skips. No production defect was found in this
assigned policy-admission and decision scope. All test inputs are engineering
fixtures; no acquired hardware or physical uncertainty was qualified.

Read the repository agent instructions, calibration scope, whole frozen
[comparison contract](../../CAPTURE_COMPARISON_CONTRACT.md), current project
navigation, plan, handoff, status/next-step and latest development-log context,
and the current session's consolidated atlas review. The source basis remains
the separately retained full-PDF reading and frozen contract. This worker does
not claim another complete atlas reading or additional source acquisition.

The integrator explicitly coordinated the additive
`parse_policy(policy_json: bytes) -> dict` interface for file-job preflight.
It admits intrinsic policy semantics without a comparison report or verdict;
`evaluate_policy` reuses it and separately validates/matches the comparison.
The original frozen metric/decision definitions and contract bytes were not
changed by this assignment.

No production module, shared status/ledger, CMake file, other-track file or Git
ref was changed. Root owns coherent-source integration and publication.

## Source identities and environment

Working directory:
`/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ`.
At initial inspection, `HEAD` and locally recorded `origin/main` were both
`5026f671e788eb5e1a77c8ed4046a34afd539200`, tree
`2ed85b986f70895000f086039750f44773508819`. Root continued integration and
publication while this independent assignment ran. The policy implementation
was a live, not-yet-published change when tested; its complete-file hash below,
not the starting commit alone, identifies the actual executed source.

Before and after the final test subprocess, an independent wrapper hashed the
following four complete files and asserted that every hash remained unchanged:

| File | SHA-256 of final executed input |
| --- | --- |
| `tools/compare_capture.py` | `220a593499539db5f1e635db2eb15ba3c0aa7c6d001c80407fbffe93f75a9a0a` |
| `tools/capture_common.py` | `e06dd82e37dd178863af61aa66bee877da1fc7e498a47b729e060215ca79c3f2` |
| `docs/CAPTURE_COMPARISON_CONTRACT.md` | `4ec3037aa0588528fe3c9e520d099cc48a82d78135fc86bd3851c2667860750c` |
| `tests/test_capture_policy.py` | `bb7c48cb26b979bf8ab0a3feb68f3b783ac75119e7b1c575ea53fe7ecf282e79` |

Environment actually queried: **Linux x86_64, CPython 3.12.14**. The retained
test requires only the standard library. Producer 20 confirmed that its final
source was frozen at the same implementation hash before this final run.

## Independent expectations

The test suite was written from the frozen contract while the policy API was
still being implemented. It does not call `compare_signals` to obtain expected
metric values, call producer helpers to obtain expected decisions, or retain a
producer-generated golden evaluation. Comparison inputs are hand-built reports
for nonnegative constant-signal/DC examples, or one-frame examples whose complex
coefficient equals the sample at every selected frequency.

The four central decision examples use exactly representable binary64 values:

| Observed value | Margin | Upper bound | Expected closed interval | Expected decision |
| ---: | ---: | ---: | --- | --- |
| 0.25 | 0.125 | 0.375 | `[0.125, 0.375]` | pass |
| 0.5 | 0.125 | 0.25 | `[0.375, 0.625]` | fail |
| 0.25 | 0.125 | 0.25 | `[0.125, 0.375]` | inconclusive |
| 0.375 | 0.125 | 0.25 | `[0.25, 0.5]` | inconclusive |

Exact adjacent-float probes supplement these examples without adding a test
epsilon or rounding the observed value. Hash expectations use independent
`hashlib.sha256` over the supplied byte strings. Expected keys, units, target
names, reasons, role values and criterion ordering are literal contract values.

One deliberately edited structural report sets an always-known nonnegative
metric to the admitted report maximum `2e18`. This is expressly **not** claimed
to be an audio realization of that FS error. The evaluator grades supplied
structurally admitted reports; the test verifies that adding the allowed
`1e6` decision margin yields a finite interval upper endpoint greater than
`2e18` and a failed criterion, rather than incorrectly reapplying the
comparison-only numeric bound to the composed evaluation envelope.

## Executed checks and results

From the repository root:

```sh
python3 -B tests/test_capture_policy.py -v
python3 -B tests/test_capture_policy.py
```

The first complete API-ready run passed **48 methods** in **0.292 seconds**.
A subsequent focused matrix added strict nested-object type rejection and
extended text coverage. The final hash-bracketed subprocess passed **49 methods**
in **0.444 seconds**, exit 0, with zero failures, errors or skips. The wrapper
printed `Input hashes stable: True`. These are independent maintained methods;
producer author assertions and earlier metric tests are not included in this
count.

| Maintained group | Methods | Executed scope and observed result |
| --- | ---: | --- |
| Policy parsing | 25 | Exact bytes, fresh parsed values, no sample/report dependency, strict UTF-8/JSON, duplicate keys at each object level, BOM/nonfinite/overflow/numeric-token rejection, inclusive byte limit, deep/oversized rejection, required/unknown keys, exact nested object types, IDs and all text branches, constants/roles/classes, geometry/frequency/Hann/work bounds, 256 criteria, uniqueness, all seven typed targets, units, numeric limits and all uncertainty branches. Passed. |
| Policy decisions | 17 | Four literal interval examples, synthetic zero versus unknown uncertainty, lower-end zero clipping, adjacent-float boundaries, margin widening, missing-metric precedence, retained phase masks, complete ordered criteria, fail/inconclusive precedence, separate channels, exact byte hashes, unestablished chronology, all six analysis matches, exact frequencies, complete untargeted metrics, near-floor ratios and the composed numeric bound. Passed. |
| Policy composition | 7 | Public intrinsic-parser reuse, rejection of invalid untargeted report fields, bounded/cyclic/deep comparison admission, input and cross-call nonaliasing, preservation after invalid policy/report calls, an existing caller-owned report file left unchanged, and repeat deterministic finite output. Passed. |

The byte-limit test admits a policy padded with legal whitespace to exactly
65,536 bytes, hashes those same bytes, and rejects one additional byte. The
numeric-token test admits a 64-character finite token and rejects the
65-character counterpart. The 256-criterion fixture uses distinct typed targets
across 16 channels and 16 frequencies, with one-frame reports. Both its accepted
256-entry form and the rejected 257-entry form are explicitly asserted to remain
below 65,536 bytes, so the count rejection is not accidentally a file-size test.
The valid analysis at the exact spectral-work product 16,777,216 is admitted by
the intrinsic parser; its adjacent excessive declaration is rejected. This is
policy preflight, not execution or timing of that entire spectral workload.

All seven admitted upper-bound targets are exercised with their exact units.
Signed/diagnostic metrics, arbitrary expressions or paths, absent channels and
bins, wrong target kinds, incorrect units and duplicate numerical targets are
rejected rather than skipped. An invalid untargeted comparison metric also
rejects the evaluation, so a favorable selected criterion cannot hide a malformed
neighbor. A failed criterion remains decisive beside masked and unknown-margin
criteria; all of their observations and original reasons remain present.

Known freeze-evidence text and all four declared roles leave
`preregistration: "not_established"`. The test explicitly allows an `unassigned`
policy's numerical criteria to pass while retaining that role; corpus eligibility
is the later wrapper's responsibility. All evaluated rows and complete reports
retain `physical_fidelity: "not_established"`.

### Fixture correction before the first complete run

During fixture construction, the initial 256-criterion example used the normal
long explanatory strings and exceeded the policy's 64 KiB byte limit. A direct
fixture-size probe measured 100,360 bytes; shortening strings while retaining
the original target distribution still measured 66,568 bytes. Neither was
submitted as an expected-valid qualification case.

The final fixture uses short valid text, compact IDs and a 16-channel by
16-frequency target distribution, measured at 64,822 bytes. Its 257-entry
counterpart also stays within the byte limit. This corrected the test fixture's
simultaneous constraints before the first full test run. It did not change a
production limit, criterion-count expectation, numeric tolerance or contract.
No failing production execution was found or concealed.

## Limits and handoff

Root should rerun this suite with the separately maintained 42-method metric
suite from the coherent integration source, then compose it with the corpus and
file-job acceptance. This worker did not execute CTest, native hosts, Windows or
macOS, complete maximum spectral workloads, file-job replay, physical acquisition
or hosted CI. No report is claimed to authenticate source audio merely because
its shape is admissible. Source-byte and window binding belong to the file job
and replay tools; corpus role/lineage qualification remains separate.

No schema-runtime dependency was introduced. No independent schema-parity claim
is made here. Missing physical calibration, coverage/correlation justification,
specimen identity, permissions, untouched final-test history and instrument
fidelity remain open. The final result and exact identities were sent to the
integrator and producer before this assignment was closed.
