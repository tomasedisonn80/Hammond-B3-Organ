# A44 — Hosted sanitizer closure audit

Actual worker `/root/w08_a44_hosted_sanitizer_audit`, wave 8. Read standing
instructions, complete M0–M9 plan, current scope/checkpoint, rotary runbooks,
A27/A29/A38 records and hosted workflow/CMake/probe sources. Own only current
qualification wording in `ROTARY_MOTION.md`, `ROTARY_PROPAGATION.md`,
`ROTARY_SCOPE.md`, this note and A44 reports. No build, tests, dependency
acquisition, product/workflow edits, commit, push or remote write.

## Exact hosted result

**PASS for the required rotary and exact sixteen native sanitizer gates.**
The [audit report](../reports/A44-hosted-sanitizer-audit.json) retains primary
job statuses, source hashes, guard inspection and bounded
[core](../reports/A44-core-sanitizer-extract.log) /
[native](../reports/A44-native-sanitizer-extract.log) decoded-log extracts.
Independently fetched both jobs with the GitHub log connector; reused A43's
same-job scratch cache, matching decoded character counts. Full decoded-log
hashes identify the retained extracts' inputs; no ZIP or binary bytes claimed.

| Run / job | Observed result |
| --- | --- |
| `43644278142` / `132598497275` | GCC 13.3 Debug core **137/137**, 268.61 s; native motion, propagation, repaired allocation and both independent Python acceptance gates pass. Allocation CTest: 0.57 s. |
| `43644278159` / `132598531735` | GCC 13.3 Release native **16/16**, 272.49 s; includes 78-layout acceptance, six pending/acknowledged frames with 947 assertions and material acceptance with 901 checks/zero failures. |

Both check out `26ff2fbe66a50260bd7601cbfa54c1f5d35ff3a8`, tree
`530d5fcf777003f470f64558de9e5631d31a21a4`, the documentation-only child of
`f9c11a498ecd88886349415205fc5dccc627033e`. Every A16/A19 numerical source,
header, oracle and frozen-contract hash matches. A38's allocation source is
exactly `022845759fe2e604ad4c8003dc0acf4e2b693d79933da86e25a0ac8e0f9f39d7`.

## Policy and evidence boundaries

Job defaults remain `ASAN_OPTIONS=detect_leaks=1:halt_on_error=1`,
`UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1`, `LSAN_OPTIONS=exitcode=23`.
The core suite has one **pre-existing explicit leak exception**:
`test_standalone_midi_backend_quarantine` sets `detect_leaks=0` for deliberately
retained failed-close callback contexts. Therefore 137/137 does not mean every
core test individually ran leak detection. Required rotary gates and all sixteen
selected native gates have no such override, skip or waiver.

Primary native steps successfully enforce instrumented C++/SDL C objects,
ASan/UBSan archive references, executable flags/runtime links, and exactly sixteen
unique built commands. Discovery rejects disabled tests and sanitizer overrides;
the existing raster limits and 60-second pending/material limits remain exact.
No numerical budget or policy changed. Missing native oracle probes fail rather
than skip. System libraries are outside the rebuild; dummy SDL surfaces do not
qualify real devices. The core log suppresses passing fixture stdout, so detailed
allocation counts remain the retained A27/A38 evidence for the identified source.

A27's original complete local sanitizer process still **failed/environment-blocked**
at LSan thread-attach EPERM, with PTY exit 134. Its original reports and stricter
one-off stack/abort/string/no-recovery options remain unchanged; the hosted
standard-policy result is separate. [A43](A43-hosted-fixture-closure.md) preserves
the original `2e161dc` Windows 135/136 failure and `f9c11a4` cancellations
separately from all twelve completed `26ff2fb` jobs.

The locally accepted, unpublished A40/A41 `f323c8c2` header and modified material
fixture are excluded. Next qualify their eventual published revision separately.
The concurrent waveform session owns R4; R5, R6/Engine, deadlines, physical
cabinet fidelity and scanner G5 remain separate. No audio/state identity changes.
