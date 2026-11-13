# Complete standalone Session benchmark matrix

This is an executed **60-case functional and timing-observation matrix** for
published source `649b12c7d1faa7601fde1019e913347c65a6634a`, tree
`cf63327d857b02029e8c5c6f406cab3d3c6890d1`. It covers all four documented
workloads, all three sample rates and all five buffer sizes with **100 measured
calls and 16 warmup calls per process**. Every case ran once on 2026-11-13.

All 60 processes exited zero, with empty stderr and matching independent
workload/state/count checks. The record contains 6,000 chronological measured
intervals, 4,761,600 measured frames, 761,856 warmup frames and 9,523,200 measured
stereo samples. All 15 corresponding performance/dense pairs have identical
reported measured audio hashes and peaks. There are **26 intervals above the
arithmetic nominal callback period**; they are retained without filtering.
These shared-host observations do not qualify a device deadline or latency.

## Contents and independent verification

| File | Purpose |
| --- | --- |
| [matrix.json](matrix.json) | Complete parsed benchmark reports, common fields stored once, all raw measured intervals, 60 process identities and source/build/profile evidence. |
| [verification.json](verification.json) | Reconciled totals, independent compiled-profile byte audit, script identities and the retained collector preflight correction. |
| [verify_matrix.py](verify_matrix.py) | Standard-library arithmetic, state, coverage, silent-byte-hash and cross-workload parity verification; imports no project implementation or existing test oracle. |
| [collect_matrix.py](collect_matrix.py) | Executes each fixed matrix case once, retains raw process outputs and assembles this evidence shape. It requires fresh output paths. |

From the repository root:

```sh
python3 examples/benchmarks/standalone-session-matrix-v1/verify_matrix.py
```

The expected result is `status: passed`, 60 cases, 6,000 measured calls, 960
warmup calls, 4,761,600 measured frames and 26 above-period observations. This
command checks retained evidence; it does not execute new benchmark processes.

The JSON uses schema `hammond-session-matrix-evidence-v1`. To reconstruct a
complete parsed native report, merge `common_report` with one
`cases[i].report`; these maps are disjoint. The case's
`parsed_report_sha256` hashes that reconstructed object serialized with sorted
keys, UTF-8, no ASCII escaping and compact comma/colon separators. Each original
stdout's byte count and SHA-256 are also retained. Raw stdout formatting is not
recreated by the semantic merge; the complete parsed values are preserved.
`matrix.json` is 398,206 bytes, SHA-256:

```text
92e1da3c49fc763ace80740d731bc85471b0ea557b9b126903d1ec79a425505d
```

Every case retains all three stage counters and all four complete snapshots,
including controls, held-note identities, sequences, sticky recovery state,
frame clocks and revisions. All render distribution statistics and callback
period ratios are independently recomputed from the retained 100 chronological
intervals. The benchmark emits only summaries for its separate 1,000-pair
clock calibration; those summaries receive consistency checks, not a claimed
recomputation from unavailable calibration samples. Float audio itself is not
retained: the binary checks finite/identical stereo and reports its byte hash.
Silent workloads additionally match an independently calculated all-zero FNV
hash, and performance/dense workloads match one another at all 15 settings.

## Recollect from the same source

The collector is scoped to this frozen GNU Release build organization: 57
manifest inputs and 23 relevant compilation commands. A changed core/manifest
requires a new versioned matrix and reviewed expectations. Its 30-second
per-process watchdog bounds a stuck command; it is not an audio deadline.

The following recipe uses fresh paths, a disposable detached source worktree,
and the current checkout's retained collector. It requires Git, GNU C++20,
CMake and Python; no SDL or native window/device is needed. A different compiler
or host produces a separately identified observation, not an identical timing
sample or binary.

```sh
git worktree add --detach ../matrix-source-649b12c 649b12c7d1faa7601fde1019e913347c65a6634a
cmake -S ../matrix-source-649b12c -B ../matrix-build-649b12c \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
  -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_BUILD_VST3=OFF
cmake --build ../matrix-build-649b12c \
  --target hammond_standalone_benchmark --parallel 2
python3 examples/benchmarks/standalone-session-matrix-v1/collect_matrix.py \
  --repo . --commit 649b12c7d1faa7601fde1019e913347c65a6634a \
  --source-root ../matrix-source-649b12c \
  --binary ../matrix-build-649b12c/apps/standalone/hammond_standalone_benchmark \
  --profile ../matrix-build-649b12c/nominal.b3p \
  --source-manifest ../matrix-build-649b12c/apps/standalone/standalone-benchmark-source-manifest.json \
  --output ../matrix-observation-649b12c/matrix.json \
  --raw-dir ../matrix-observation-649b12c/raw
python3 examples/benchmarks/standalone-session-matrix-v1/verify_matrix.py \
  ../matrix-observation-649b12c/matrix.json
```

The collector verifies every tracked source blob and executable mode against
the specified Git commit before and after execution, verifies each benchmark
manifest input, records the existing compilation commands and preserves each
actual stdout/stderr/process record. It never rebuilds or modifies the supplied
source/build, never retries a benchmark and never removes a slow sample.

## Exact observation boundary

This retained run reused the [clean-setup audit's](../../../docs/reviews/STANDALONE_CLEAN_SETUP.md)
already built SDK-free executable read-only after its original paths had been
moved. All 842 tracked source files, executable and compiled profile remained
unchanged. The binary is 154,568 bytes, SHA-256
`0c97a79e8c49dbad961090727fe3ae1668a283bdc4d87f4d334fc9c604981f19`.
The 57-input fingerprint is
`5fd7837b44dbe8fd09bfbd9931c20065e29acfffee10f3adca1a622cb18b9bb8`.
The 4,545-byte profile has SHA-256
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.

The host was Linux x86-64, GCC 14.2.0 Release, glibc 2.41 and Python 3.12.14.
Allowed CPUs were 0–8; affinity, power/thermal state and concurrent work were
not controlled. Invalid SDL driver names were explicitly set, and this SDK-free
binary completed without initializing SDL. No build, host/device, sanitizer,
allocation or concurrent-UI gate is claimed by this matrix. The
[full review](../../../docs/reviews/STANDALONE_BENCHMARK_MATRIX.md) retains exact
commands, counters, outliers, the zero-invocation preflight correction and next
qualification requirements. The [benchmark contract](../../../docs/STANDALONE_BENCHMARK.md)
defines what is inside and outside the measured interval.
