# A30 — independent native and portability review

Actual worker `/root/w05_a30_portability_review`, wave 5. Owned this note,
[the detailed review](../../../reviews/PRODUCT_CONTINUATION_CODE_REVIEW.md),
and root-authorized benchmark metadata correction after source archival.
Read standing instructions, the complete plan, active session records and MIDI,
crossover and visual contracts. Reviewed baseline `af006b0ae293c7c9a5f44b5dfe1dc9942fe9e12d`
through published `ff41d412d03f2c5767aa4057b29fa8ec1627449b`, tree
`6462343bb34a7d70d59de75ab349f8530196988c`, plus explicitly hashed A26/A27
supplemental files and CMake wiring.

No production defect confirmed in scoped sound-off admission/ideal lowering,
endpoint mapping, native calibration lifecycle, state preservation, crossover
preparation/response/transaction processing, or allocator pairing. Checked GCC,
Apple/POSIX and MSVC allocator branches, checked decimal/unsigned parsing,
floating limits, fixed storage, field-wise geometry hashing and exception
boundaries. Supplemental facade locking is consistent with its explicitly
synchronous callback schedule.

**One concrete low-severity finding:** ordinary current-only paint-benchmark
builds unconditionally reported `alternating_order:true`. They execute one
painter. Root archived A27's measured source/report in
`1080d15749f3a96d8259c0befcc0307aab7ea9a5`, then authorized A30 to serialize
the `paired` Boolean. Corrected tool SHA-256:
`d81eb9412d6d885807e57b4657c58519309a3e2b830c904ff1b36d6b40569338`.
Paired A27 timing evidence is unaffected; no timing rerun is needed.

After root rebuilt, the ordinary `hammond_standalone_paint_benchmark 960 700
flat zero` passed in 4.988 seconds: `paired:false`, `alternating_order:false`,
`before:null`, 30 warmups/300 samples, empty stderr and exit 0. Binary SHA-256:
`10d7592d2e6d9e75f4cc45171d5a4e82855839733fd545f9f01e4ce4a43bcfb6`.
This checks metadata only, without new timing qualification.

**Executed:** Python 3.12.14,
`python3 tests/test_crossover_reference.py CrossoverReferenceTests.test_near_dc_reactive_current_survives_equipotential_inductor_nodes`
from repository root: 1/1 passed in 0.002 seconds; 144 comparisons; maximum
normalized error `2.2204502844110104e-16`. Ground-return KCL correctly avoids
near-DC source-voltage cancellation and retains the independent physical graph.
All coherent-build source hashes still matched except the deliberately extended
standalone CMake file. The review preserves exact supplemental hashes.

Read retained root 176/176 Release, A25 allocation, A26 native lifecycle and A27
paint results; did not relabel them as A30 reruns. Local leak-enabled sanitizer
and its empty-main control remain ptrace-blocked, not passed. Root reports all
13 hosted jobs successful at `ff41d412`; primary logs were not independently
audited here. No production painter, build-tree,
index, commit or publication mutation; no broad tests or timing contention.

**Next:** root publishes the metadata correction, runs the required integrated
native calibration CTest and retains exact-source
AppleClang/MSVC/core/native/sanitizer results. No audibility, hardware, deadline,
accessibility, Engine integration or literal 1:1 claim follows from this review.
