# Capture toolchain resource profile

## Conclusion and exact evidence

The bounded capture pipeline completes the twelve declared representative cases
on the observed shared Linux host, retaining all engineering outcomes and exact
source/input identities. The collected timings describe those workloads only.
The clearest actionable resource observation is the **16,789,913-byte traced
peak during replay of a 119,423-byte saved study report**. It motivates a narrow
metadata-read allocation investigation while preserving current admission and
snapshot guarantees. It is not a contract failure or a measured process-memory
limit.

The retained [collector and method](../../examples/benchmarks/capture-toolchain-v1/README.md)
and [actual JSON](../../examples/benchmarks/capture-toolchain-v1/results.json)
are the complete reproducible artifact. Actual assignment **40**,
`/root/cal_w7_a40`, logical wave 7, owns this review and its
[execution note](../development/2026-11-13-calibration/40-resource-profile.md).
The integrator approved the fixed workloads and measurement split before
collection. The collector was frozen at SHA-256 `33a4dd7dafd675165ee5f86d04c04145948859ce7d865d2312482e99341e0973` before the
single retained run. No threshold was chosen afterward.

## Source and scope

The project [M0–M9 plan](../PLAN.md), [calibration scope](../CALIBRATION_SCOPE.md),
and source atlas pp. 449 and 484–486 distinguish useful dependency-ready
engineering, physical calibration, actual product deadlines and evidence
retention. They do not prescribe this benchmark, these workloads or a speed
threshold. The audio/comparison/job/study/replay contracts supply the API behavior
and resource meanings. The original numerical stream is a software construction.

The checkout observed before collection was public
`955fc4c41f74ada094f14fbaf386c943811e9050`, tree
`70956d0f0e125d57abfbf1aed56460c067f8ef28`. Replay was subsequently authored
working-tree source at the exact hash below. Therefore that commit alone does
not identify all executed files. The collector copied the ten-file source closure,
verified the copy against originals before imports, and verified both again after
all calls. Its own source, nineteen generated input/report files and four arrays
also remained unchanged.

| Module | Bytes | SHA-256 |
| --- | ---: | --- |
| `capture_audio.py` | 29,951 | `b1f6228932c15f6483808cbb36a407dcdd6919f5894439d93f8888b01d66113c` |
| `capture_common.py` | 9,625 | `e06dd82e37dd178863af61aa66bee877da1fc7e498a47b729e060215ca79c3f2` |
| `capture_corpus.py` | 39,220 | `1c68ca13157f767847258ccb74f3a22f49cc1d56f323cddeebd52f3ab85ed5ba` |
| `capture_job.py` | 24,302 | `147002ac866a4451e6740eae69da9f914116339f89b657bae7d4c6ef41e3eded` |
| `capture_readiness.py` | 11,247 | `215b2abd3614195151c5751248f2d40850653d794af1786e95eaedccf13bdc76` |
| `capture_study.py` | 16,740 | `4b627a8c213ff43691e8011dca0a4206db8f4184dd32b5ea6edad4471f90e69d` |
| `compare_capture.py` | 33,448 | `220a593499539db5f1e635db2eb15ba3c0aa7c6d001c80407fbffe93f75a9a0a` |
| `make_capture_demo.py` | 22,329 | `d6006b6856ad484f5936e56786aeb5013c148c91fa49e373913ef1bb5484d204` |
| `validate_capture.py` | 24,827 | `a872e069ba9744f6f8078f87b78ea300df1ee28aec58e104859580cdc09877af` |
| `verify_capture_report.py` | 23,380 | `23dc1c316232c27345ce35beec667a1e604847dc30b31b9b0b8bfc63423dd2d4` |

The observation began at `2026-11-14T00:17:36.682302+00:00`. Runtime was
CPython 3.12.14, Linux x86_64 (`Linux-6.18.57-x86_64-with-glibc2.41`), with nine
logical CPUs reported and garbage collection enabled. No pinning, scheduling
isolation or fixed CPU-frequency policy was established. No other machine or
source revision was measured as a controlled baseline.

## Executed method

Twelve fixed cases each received one warmup, three ordinary timings and one
separate allocation-traced call: **60 top-level profiled API invocations**, of
which **36** form the ordinary timing samples. The setup generator and setup
study report are two additional unprofiled API calls; final publication is a
separate unprofiled helper call. Internal producer composition is not recounted
as independent samples.

Ordinary timing uses `perf_counter_ns` immediately around the public API call,
through its returned result. Import/copy/setup, input hashing, garbage collection,
result validation and JSON serialization are outside. The APIs' own admission,
whole-file reads, computation, complete report assembly and final checks remain
inside. Every result is validated against fixed statuses and literal geometry/
metrics; every repeated/traced complete API dictionary serializes to exactly the
warmup's original bytes within that collection environment.

The comparison candidate adds the exact binary fraction `1/128` FS. Both channel
biases, RMS errors and maximum errors must equal **0.0078125 FS**; all eight
frequency rows per channel remain present. Full demo corpus, pass/inconclusive/
failed jobs, a failed study retaining all three outcomes and a matching failed-
study replay remain distinct. No policy, source, threshold or outcome was changed.

Tracing begins after input arrays and imports exist, using one traceback frame.
It measures traced Python allocations during one separate call, with the result
retained at measurement. It excludes pre-existing inputs, imports, untraced
native storage and process-wide memory. Traced elapsed times do not enter
ordinary statistics. The timer's advertised 1 ns resolution is not measurement
accuracy; three elapsed samples do not establish a distribution, confidence
interval, tail latency or a deadline.

## Observed values

| Case | Ordinary median (ms) | Three-sample range (ms) | Separate traced peak (bytes) | API JSON bytes | Outcome |
| --- | ---: | ---: | ---: | ---: | --- |
| `audio-inspect-16384` | 30.854 | 29.071–36.478 | 204,533 | 2,072 | inspected |
| `audio-window-16384` | 34.622 | 30.044–35.453 | 237,621 | 38,200 | inspected |
| `audio-inspect-65536` | 125.324 | 118.503–131.743 | 204,621 | 2,077 | inspected |
| `audio-window-65536` | 136.206 | 125.426–136.647 | 271,525 | 38,214 | inspected |
| `comparison-1024` | 10.396 | 10.373–11.069 | 165,464 | 30,984 | calculated |
| `comparison-8192` | 72.378 | 71.975–73.400 | 972,376 | 31,062 | calculated |
| `demo-corpus` | 3.416 | 3.407–3.541 | 1,059,367 | 7,277 | pass |
| `demo-job-pass` | 8.172 | 7.970–8.470 | 1,115,832 | 32,694 | pass |
| `demo-job-inconclusive` | 7.477 | 7.141–7.967 | 1,115,792 | 32,782 | inconclusive |
| `demo-job-fail` | 8.350 | 7.402–8.718 | 1,115,744 | 32,659 | failed |
| `demo-study` | 36.119 | 35.384–36.295 | 1,405,809 | 119,423 | failed |
| `demo-study-replay` | 73.251 | 72.161–76.723 | 16,789,913 | 4,260 | match |

The complete raw integer timing values, recorded warmups and separately traced
timings/current allocations are retained in the JSON. Values in this table are
rounded only for display.

### Full validation remains the dominant work for a small requested window

The two raw-float32 stereo inputs contain 32,768 and 131,072 scalar samples at
a declared 48 kHz, respectively 128 KiB and 512 KiB. Full inspection medians are
30.854 and 125.324 ms. The corresponding 1,024-frame window medians are 34.622
and 136.206 ms. A window selects returned samples but does not authorize skipping
invalid data or identity checks elsewhere in the stream; complete file admission
remains contractual. These timing observations therefore do not justify changing
window semantics into partial validation.

Full-inspection traced peaks were 204,533 and 204,621 bytes, while only about
5,294 traced bytes remained at return. Window calls retain 2,048 scalar samples
and had higher traced current/peak values. This is an observation at two specific
sizes with one storage format, not proof of a universal memory bound. Input
construction before tracing and process-wide storage remain outside this measure.

### Selected-frequency work is explicit and bounded

Both comparison cases use two channels, eight declared frequencies and symmetric
Hann weighting. Their one-side work is **16,384** and **131,072** selected-frequency
terms, an eightfold increase. Observed medians are 10.396 and 72.378 ms; traced
peaks are 165,464 and 972,376 bytes. The output still contains sixteen frequency
rows and all pointwise metrics. The later case is only **1/128** of the admitted
spectral-work cap, and no maximum workload was executed. A trend across these
two cases is insufficient to predict all frequencies, data shapes, hosts or
operational deadlines.

### Complete evidence has a measurable cost, and outcomes remain intact

The three-capture corpus contains only 48 raw-audio bytes, but full execution
also performs metadata, identities, confinement and grouping work. Its observed
median is 3.416 ms. The three job medians span 7.477–8.350 ms while retaining
pass, inconclusive and failed outcomes. The full three-job study takes an
observed median 36.119 ms and returns 119,423 benchmark-encoded API JSON bytes.
The study still fails with one outcome of each kind.

Replay takes an observed median 73.251 ms and returns a 4,260-byte summary. It
executes the complete study, admits and compares the entire saved/fresh reports,
and records **match** while keeping both underlying engineering statuses
**failed**. No cached result substitutes for current execution. These timings
are not a component-by-component cost attribution or a callback benchmark.

### Narrow follow-up: investigate bounded metadata-read allocation

The separate traced replay peak is **16,789,913 bytes** (about 16.01 MiB), compared
with **1,405,809 bytes** for the study. The saved report itself is **119,423 bytes**.
Source inspection of `capture_corpus._read_confined_bytes` finds
`source.read(max_bytes + 1)` after bounded pathname/descriptor-size admission;
replay passes its 16 MiB report limit through `capture_job._read_observed`.
The common JSON reader uses a similar bounded request. This pattern is a plausible
contributor to the observed peak; aggregate peak tracing here does not prove
which call allocated each byte.

A dependency-ready next task is a separately reviewed controlled attribution
and size-aware/chunked-read experiment. Preserve exact original-byte hashes,
maximum-byte and growth detection, opened-descriptor/path identity, final stamps,
error ordering/context, descriptor cleanup and cancellation. Do not simply remove
the extra-byte/growth check or weaken the report limit. Retain the present source
and observation; qualify any later source with focused independent mutation/boundary
acceptance and a new output artifact. A lower traced peak would not itself prove
lower RSS, maximum memory safety or better real-time behavior.

No production code was changed in this assignment, and no bound was violated.
The declared limits remain engineering admission caps. This resource observation
is a useful next-step input rather than a new acceptance tolerance.

## Reproduction, validation and remaining gates

The actual single collection command, from repository root, was:

```sh
python3 -B examples/benchmarks/capture-toolchain-v1/collect.py --tools-root tools --output examples/benchmarks/capture-toolchain-v1/results.json
```

Exit was **0** on its first retained run. No setup/measurement failure, retry,
selective sample removal or changed expectation occurred. Static parse/text QA
and help completed before the frozen run. A separate post-run audit verifies
all twelve rows, timing min/median/max arithmetic, positive integer samples,
tracing separation, six pipeline outcomes and current source/file identities.
Three lightweight negative CLI checks reject an existing results file, a target
inside the selected tools directory and a nonexistent parent. They execute no
profiling and preserve the retained result and original sources.

Results are **33,658 bytes**, SHA-256
`c7749036186638b00a9fc77663d5c55e308e64da0d6a3bbced7693c5bbac9789`. Collector is **20,353 bytes**, SHA-256
`33a4dd7dafd675165ee5f86d04c04145948859ce7d865d2312482e99341e0973`. Each source and fixture identity is retained in the JSON.
Audio's complete API-output hash includes its actual temporary path; the additional
portable hash changes only that field, explicitly labeled. No numerical or
identity field is projected away. Hash equality is no authentication or signature.

The cache is uncontrolled and warmed by creation/hash/warmup. The host is shared,
tracing adds substantial execution cost, and only three ordinary samples per case
were taken. This is neither cold-storage profiling nor sustained-load/native-
platform qualification. No maximal admitted corpus/report/spectral scan, complete
format matrix, native macOS/Windows run, process-memory upper bound or controlled
cross-revision speed claim is established. Source/runtime changes require new
appropriately scoped observations. Acquisition, physical uncertainty, permissions,
independent holdout history, listening and specimen fidelity remain separate gates.
