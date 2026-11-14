# Assignment 40 — bounded capture resource observations

Actual worker: **`/root/cal_w7_a40`**, assignment **40**, logical wave **7**,
session `2026-11-13-calibration`. This is one actual newly dispatched worker;
repeated calls and earlier source readers are not additional assignments.
Execution occurred on 2026-11-14 UTC without creating a new session.

## Ownership and source basis

Owned files are exactly:

- `examples/benchmarks/capture-toolchain-v1/collect.py`
- `examples/benchmarks/capture-toolchain-v1/results.json`
- `examples/benchmarks/capture-toolchain-v1/README.md`
- `docs/reviews/CALIBRATION_RESOURCE_PROFILE.md`
- This assignment note.

No runtime producer, test, installer, schema, CMake file, shared document,
assignment ledger or Git ref was edited. Root owns integration, acceptance and
publication. No extra worker was spawned or counted by this assignment.

Read the standing agent instructions, active calibration scope, current
README/status/next-step and handoff context, M0–M9 plan, relevant audio/comparison/
corpus/job/study/replay contracts and actual exposed resource constants. Read the
actual source paths that bind complete audio, raw input windows and bounded
metadata reads. Fresh extracted atlas text on pp. 449 and 484–486 supports
separate physical/product gates and retained source/setup/outcome evidence.
The source does not supply these workloads or a performance threshold. The
session's six earlier workers own the complete 500-page reading; this worker
claims only that relevant subset, not another full PDF or primary-source review.

At the collector freeze, the observed checkout and fetched `origin/main` were
`955fc4c41f74ada094f14fbaf386c943811e9050`, tree
`70956d0f0e125d57abfbf1aed56460c067f8ef28`. Replay was a later working-tree
addition. The observation therefore identifies every actually executed module
by bytes/hash rather than attributing uncommitted code to that commit. Runtime
sources are the exact ten-file table in the [resource review](../../reviews/CALIBRATION_RESOURCE_PROFILE.md)
and retained JSON; they remained unchanged around collection.

## Predeclared procedure and freeze

Before measurement, sent root the twelve-case proposal: raw-float32 stereo
inspection/window at 16,384/65,536 frames; two-channel eight-frequency Hann
comparison at 1,024/8,192 frames; complete original demo corpus, three jobs,
failed study and matching failed-study replay. Root expressly approved one
warmup plus three ordinary samples per case and one separate traced call per
case, with no threshold or maximal-scan claim. It required tracing to start
after imports/input allocation and to remain distinct from process memory and
ordinary timing.

The collector was implemented entirely in the owned artifact path and frozen
before the first retained profiling invocation: **20,353 bytes**, SHA-256
`33a4dd7dafd675165ee5f86d04c04145948859ce7d865d2312482e99341e0973`. `ast.parse`, UTF-8/LF/trailing-whitespace inspection and its
`--help` path passed before collection. An authoring change before that freeze
separated corpus work metadata from job-specific window counts; it did not
follow or alter any measured result. No producer or frozen tool contract changed.

The collector uses only Python's standard library and the selected original
project modules. It copies all ten sources to a private temporary directory,
checks before/after byte identities and imports only from that copy. Generated
raw/demo/report fixtures and comparison arrays are prepared outside timing and
verified unchanged afterward. It refuses an existing output, an output inside
the tools directory or a missing parent. Final publication uses the unchanged
no-clobber JSON helper; private temporary material is cleaned independently of
the caller's result. No original package/demo/source is edited.

## Actual execution and validation

Working directory:
`/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ`.

```sh
python3 -B examples/benchmarks/capture-toolchain-v1/collect.py --tools-root tools --output examples/benchmarks/capture-toolchain-v1/results.json
```

The **first retained run passed**, exit **0**, beginning at
`2026-11-14T00:17:36.682302+00:00` on **CPython 3.12.14 / Linux x86_64**.
There were no unexpected setup errors, failed measurements, retries, rejected
samples or loosened expectations. No numerical threshold or empirical speed
criterion was introduced.

The run executed twelve warmups, **36 ordinary samples** and twelve separately
traced calls: **60 top-level profiled API invocations**. Setup additionally called
the original generator once and study runner once to prepare the saved replay
report. Result publication is a further unprofiled helper call. Internal nested
calls are not additional independent observations. No timed tool CLI subprocess
or CLI-startup performance is claimed.

A separate author arithmetic/text audit after collection confirmed:

- Exactly twelve rows and three positive integer ordinary samples per row.
- Stored min/median/max equal recomputation from those original samples.
- Warmups and tracing remain excluded from ordinary statistics.
- Traced peak is no smaller than traced current bytes at return.
- Pipeline outcomes are exactly pass, pass, inconclusive, failed, failed, match;
  the replay preserves both underlying failed statuses.
- Collector/result hashes, all ten current source hashes and retained identity
  checks agree; each original/copy/fixture/array was unchanged.

Three additional actual CLI invocations deliberately targeted the existing
result file, a new filename inside `tools/`, and a nonexistent parent. Each
returned **1** with empty stdout and the expected contextual rejection before
profiling. The retained result bytes and sources were unchanged; no forbidden
output or missing parent was created. These are boundary checks, not extra
profiling samples or producer tests.

Results are **33,658 bytes**, SHA-256
`c7749036186638b00a9fc77663d5c55e308e64da0d6a3bbced7693c5bbac9789`. The source/runtime/clock, nineteen generated file identities,
four array identities, raw integer timings, output identities and source caps
are all retained in that actual file. No generated audio payload is
checked into the repository; literal formulas reproduce the inputs.

## Findings and integration handoff

The complete table is in the review and artifact README. Full raw stereo scans
had ordinary medians **30.854 / 125.324 ms** at 128/512 KiB. Returning a middle
1,024-frame window still validates the full stream and had **34.622 / 136.206 ms**
medians. Two comparison sizes had **10.396 / 72.378 ms** medians for 16,384 /
131,072 selected-frequency terms per side. All exact offset errors stayed
**0.0078125 FS**.

The failed three-job study had an ordinary median **36.119 ms**; its matching
replay had **73.251 ms**. Every pass, inconclusive and failed nested outcome
remained visible. These are three-sample observations on an uncontrolled shared
host, not deadlines, percentiles, universal scaling or cross-machine evidence.

The separate replay trace peaked at **16,789,913 bytes** while the saved study
was **119,423 bytes**; the separate study peak was **1,405,809 bytes**. The
bounded reader's `read(max_bytes + 1)` with a 16 MiB replay ceiling is a plausible
allocation contributor found by source inspection. This aggregate profile does
not prove exact allocation attribution and does not show a contract violation.
Root received this actionable candidate with that limitation. A follow-up may
investigate size-aware or chunked bounded reads while preserving all growth,
identity, snapshot, error and cleanup rules. No production fix was attempted here.

Root should review the five owned files, retain this exact source/result pair,
record assignment acceptance and publish under the standing authorized workflow.
The collector is a separate observation artifact and does not change CaptureTools'
57-file inventory or existing runtime APIs. Later source changes require a fresh
result in a new destination; do not overwrite this historical observation or
claim a speedup from different uncontrolled environments.

Tracing starts after setup/import/input construction, so its current/peak values
are neither total process memory nor RSS. Instrumented time is excluded from
ordinary samples. Files were created/hashed before timing and warmed once; cold
storage and sustained load remain unmeasured. Maximum admitted audio/report/
corpus/spectral workloads, the complete WAV-format performance matrix, native
Windows/macOS, hardware/device deadlines, calibration, permissions, holdout
chronology, listening and physical fidelity remain outside this assignment's
evidence. Passing these software observations clears no physical gate.
