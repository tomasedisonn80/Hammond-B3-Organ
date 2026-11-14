# A43 — Hosted fixture repair closure

Actual worker `/root/w08_a43_hosted_fixture_closure`, wave 8. Read standing
instructions, the complete project plan, current scope/checkpoint/manifest, atlas
review and A38's repair note/report. Owned this note, A43 reports and
`docs/reviews/REFERENCE_REFINEMENT_HOSTED.md`. Used connected GitHub GETs and
decoded job logs; no remote cancellation/rerun, source/test/workflow edit, build,
commit or push. Respected A41's two requested quiet timing intervals.

## Exact source and completed result

The initially assigned `f9c11a498ecd88886349415205fc5dccc627033e`, tree
`39ac16b12526143eee4136e4cc4a534b71013660`, completed six jobs successfully and
cancelled six. Windows Release run `43643877469`, job `132597198333`, passed the
repaired allocation fixture in **0.15 seconds**, then recorded **69/137** passed
before cancellation. Neither that job nor the incomplete native suites is
relabeled as passed.

Root identified the concurrent documentation commit
`26ff2fbe66a50260bd7601cbfa54c1f5d35ff3a8`, tree
`530d5fcf777003f470f64558de9e5631d31a21a4`. Independent API comparison and local Git
tree comparison agree: one direct child, eighteen documentation/record changes,
all **666 non-documentation entries identical**. The observed cancellation timing
is consistent with the workflows' `cancel-in-progress: true`; no API-confirmed
requester is asserted. Root authorized auditing the continuing runs.

All **twelve 26ff jobs** have complete passing primary logs:

- Core Linux/macOS/Windows Release and Linux sanitizer: **137/137 each**.
- Native standalone Linux MIDI OFF/ON, macOS ON and Windows ON: **41/41 each**.
- Native standalone sanitizer: **16/16**.
- Native VST3 Linux: **8/8**; Windows/macOS: **7/7 each**, with **47/47** internal
  SDK-validator checks on every platform.

Windows Release run **43644278142**, job **132598497386**, passes **137/137 in
228.22 seconds**, including allocation **0.14 seconds**. Actual compiler is
**MSVC 19.44.35230.0**, toolset directory **14.44.35207**; the build reports zero
warnings/errors. All four core jobs include native motion, propagation and
allocation plus both independent Python rotary acceptance tests, profile and
reference gates. Published allocation source SHA-256 remains
`022845759fe2e604ad4c8003dc0acf4e2b693d79933da86e25a0ac8e0f9f39d7`.

## Boundaries and retained evidence

The original `2e161dc` Windows failure remains **135/136**, allocation SEGFAULT
at **0.02 seconds**, in unchanged `root-windows-2e.log`; its SHA-256 was rechecked
against A38. The repaired pass closes the observed fixture regression, without
inventing an original Windows stack trace or proving its exact crash mechanism.

Configure's unused `CMAKE_BUILD_TYPE` warning, four Linux VST3 SDK format warnings
and macOS SDL deprecations remain recorded. A44 owns the deeper sanitizer audit.
The core sanitizer defaults to leak checking, but the existing intentional
`test_standalone_midi_backend_quarantine` exception disables leak detection for
that one gate; an exception-free claim for all 137 tests would be incorrect.

[Primary report](../reports/A43-hosted-fixture-closure.json) records every run/job/
head, test count, numerical result, toolchain, diagnostic and decoded-log hash.
Both Windows decoded logs are retained in full; all 24 jobs have bounded primary
extracts. These are connector-decoded UTF-8 bytes, not original artifact ZIPs.
[The review](../../../reviews/REFERENCE_REFINEMENT_HOSTED.md) provides the matrix
and exact job links. Parser checks require unique test IDs, matching totals and
successful CTest summaries; published-source comparisons and original-log hashes
also pass.

Neither audited head includes A40's header refinement. Next: publish that accepted
change and qualify its exact new head; retain A44's separate instrumentation
audit and all real-device, DAW, deadline, accessibility and physical-fidelity gates.
