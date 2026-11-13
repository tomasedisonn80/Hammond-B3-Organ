# Assignment 52 — Complete Session benchmark matrix

- **Actual agent:** `/root/w09_a52_benchmark_matrix`
- **Wave:** 9 of 10; new assignment 52 of 60.
- **Outcome:** complete; all 60 distinct workload/rate/buffer cases executed
  once and passed independent functional and arithmetic verification. This
  result contains no timing pass threshold, device or physical-fidelity claim.
- **Source:** published `649b12c7d1faa7601fde1019e913347c65a6634a`, exact tree
  `cf63327d857b02029e8c5c6f406cab3d3c6890d1`.

## Owned files

- `examples/benchmarks/standalone-session-matrix-v1/README.md`
- `examples/benchmarks/standalone-session-matrix-v1/collect_matrix.py`
- `examples/benchmarks/standalone-session-matrix-v1/verify_matrix.py`
- `examples/benchmarks/standalone-session-matrix-v1/matrix.json`
- `examples/benchmarks/standalone-session-matrix-v1/verification.json`
- `docs/reviews/STANDALONE_BENCHMARK_MATRIX.md`
- `docs/development/2026-11-13-next-phases/52-benchmark-matrix.md`

No production/test/CMake/shared-status/ledger file changed. The worker made no
commit or remote publication. Assignment 49's frozen source/builds were used
read-only; no other agent's original paths were moved or restored.

## Executed work and evidence

The [full review](../../reviews/STANDALONE_BENCHMARK_MATRIX.md) records commands,
exact identities, workload formulas, timing observations, limits and the next
qualification task. The [artifact](../../../examples/benchmarks/standalone-session-matrix-v1/README.md)
retains every complete parsed report, all 6,000 measured intervals, the 57-input
source manifest, process records and independent collector/verifier scripts.

All 842 tracked frozen-source blobs and executable modes matched Git before and
after execution. All 57 manifest hashes and the combined source fingerprint
were independently recomputed. All 23 relevant compile commands showed GNU
Release optimization and no sanitizer flags. The reused 154,568-byte benchmark
has SHA-256 `0c97a79e8c49dbad961090727fe3ae1668a283bdc4d87f4d334fc9c604981f19`;
the 4,545-byte profile has SHA-256
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.
Both remained unchanged. No new build was performed by this worker.

Actual collection ran 2026-11-13 23:39:14.499292–23:39:26.786989 UTC on Linux
6.18.57 x86-64, glibc 2.41, GCC 14.2.0 Release and Python 3.12.14. Each of
silence/performance/dense/recovery ran at all 3 rates × 5 buffers, with 16 warmup
and 100 measured calls. Every process exited zero with empty stderr.

- 6,000 measured calls / 4,761,600 frames / 9,523,200 stereo samples.
- 960 warmup calls / 761,856 additional frames.
- Measured commands: 777,000 accepted = 393,000 applied + 384,000 discarded.
- 1,500 intentional measured recoveries, plus 240 warmup recoveries.
- All 240 snapshots match exact controls, ownership, clocks, sequences,
  diagnostic accounting and advancing coherent publication revisions.
- All 15 performance/dense setting pairs have identical measured audio hashes
  and peaks; all silent/recovery hashes match independent zero-byte arithmetic.
- All 6,000 chronological intervals and their 26 above-period observations
  remain. Summary distributions, ratios and totals independently recompute.

The initial collector preflight used the guessed compile-target name
`hammond_standalone_core.dir`, which failed its 23-command assertion before any
benchmark invocation. Actual build metadata identified
`hammond_standalone_support.dir`; only that selector was corrected. The original
empty raw directory and correction record remain in private scratch. No
benchmark was retried, and no functional expectation, source, binary or budget
was relaxed. The retained collection and subsequent verifier both passed.

`matrix.json` is 398,206 bytes, SHA-256
`92e1da3c49fc763ace80740d731bc85471b0ea557b9b126903d1ec79a425505d`.
The artifact's `verification.json` records the profile byte audit and script
digests; raw process outputs remain at
`/workspace/scratch/5ba97739b54c/a52-benchmark-matrix/raw/`.

## Limits and concrete handoff

The retained matrix is scoped to the published source and reused originating
build. It does not qualify subsequent source changes, concurrent rendering,
native devices, callback deadlines, allocation behavior, platform compatibility
or physical sound. Audio floats and raw clock-calibration samples are not
emitted; their complete parsed summary/hash evidence is retained with that
limit. Long intervals are observations whose individual causes were not
diagnosed. CPU affinity, thermal/power behavior and other agent work were not
controlled.

Root should review these seven paths, commit/push them with the named source
scope, and retain the separate final-source and hosted gates. The next timing
task requires a specific target machine/device/backend and predeclared actual
callback, concurrent-UI, underrun and latency criteria. Use the documented
collector on a coherent build first; preserve all outcomes rather than using
the present container values as a device budget.
