# Bounded capture toolchain resource observations

This original artifact records **one executed observation**, collected on
**2026-11-14** with CPython 3.12.14 on Linux x86_64. It profiles twelve fixed,
small or moderate offline cases from a coherent copy of the capture tools.
There is no speed threshold, physical recording, real-time suitability verdict,
maximum-workload claim or controlled comparison with another machine.

The [resource review](../../../docs/reviews/CALIBRATION_RESOURCE_PROFILE.md)
explains the findings and next optimization candidate. The
[assignment note](../../../docs/development/2026-11-13-calibration/40-resource-profile.md)
retains approval, exact execution, validation and source context. The capture
[scope](../../../docs/CALIBRATION_SCOPE.md) and [contracts](../../../docs/CALIBRATION_HANDOFF.md)
remain authoritative for tool semantics.

## Files and reproduction

- `collect.py` is the standard-library collector, frozen before collection.
- `results.json` is the actual retained observation, including every ordinary
  elapsed sample, separate warmup/tracing result, original input identity,
  complete API-output identity, source identity and resource constant.
- This README explains reproducibility and the measurement boundary.

From the repository root, choose a **new** output file whose parent exists:

```sh
python3 -B examples/benchmarks/capture-toolchain-v1/collect.py --tools-root tools --output /existing/new-resource-profile.json
```

The existing `results.json` must not be overwritten. Its destination is checked
before imports or profiling, and final publication uses the existing no-clobber
JSON writer. A missing parent is not created. Output inside the selected tools
directory is rejected. A file created by another writer after preflight wins;
publication fails rather than replacing it. The common writer's partial-delivery
and completed-publication cleanup limits still apply.

`--tools-root` is the directory containing the ten listed `.py` sources. It can
be a checkout's `tools/` or an installed CaptureTools package's `tools/`. The
collector itself is a separate benchmark artifact, outside that component's
fixed 57-file inventory. Absolute collector/tool/output paths support a foreign
working directory. Python 3.10 or newer is sufficient; no CMake, native SDK,
network, audio device or third-party Python package is used by this collection.

The collector copies all ten observed modules into a private temporary directory
before importing them. It verifies the original/copy identities before execution
and again afterward, and also checks every generated file, in-memory comparison
array and its own source. Only the requested new results file is retained;
its private generated raw streams, demo and saved study are removed with the
private temporary workspace. No original module, checked-in demo or package file
is edited. This is a quiescent-source consistency check, not code signing or a
hostile-filesystem sandbox. Run in a fresh Python process without an existing
allocation tracer.

## Fixed workloads

| Group | Fixed workload |
| --- | --- |
| Audio inspection, two cases | Interleaved raw float32 LE, stereo, declared 48 kHz; 16,384 or 65,536 frames, respectively 131,072 or 524,288 bytes. |
| Audio window, two cases | The same complete streams, returning 1,024 middle frames. Both APIs still validate and hash the complete stream. |
| Selected-frequency comparison, two cases | Stereo arrays with 1,024 or 8,192 frames; eight fixed frequencies; symmetric Hann; floor `1e-12` FS; candidate adds exactly `1/128` FS. |
| Complete pipeline, six cases | Full three-capture demo corpus; pass, inconclusive and failed jobs; the failed three-job study; matching replay of that failed study. |

Every generated scalar is the exact binary fraction
`(((frame * (channel + 1)) % 257) - 128) / 256`. Raw streams use frame-major
little-endian float32. Comparison inputs use the same rational sequence as Python
binary64, with the exact offset added to the candidate. Frequencies are
`[0, 187.5, 375, 750, 1500, 3000, 6000, 12000]` Hz. The largest comparison
has 16,384 samples and 131,072 selected-frequency terms **per side**. Both
arrays are processed; this work count follows the contract's one-side convention.

Array identities hash the literal `b"HAMMOND-CAPTURE-BENCH-ARRAYS-V1\x00"`,
then little-endian uint32 channel/frame counts and channel-major little-endian
float64 samples. This benchmark-specific identity does not replace the audio
contract's separate canonical decoded digest.

The demo is produced by the existing original generator. Its sixteen files,
48 raw-audio bytes, policies and literal expectations remain unchanged. Its
complete pipeline outcomes are **pass, pass, inconclusive, failed, failed,
match**. The matching replay explicitly retains underlying **failed** engineering
status. Timed entry points are Python APIs, not CLI startup or stdout delivery;
no timed CLI-process count is claimed.

## Measurement boundary

Each case has one recorded warmup, then three ordinary `perf_counter_ns` samples.
The median/min/max use only those three samples. Setup, source copying, imports,
fixture generation, input hashing, serialization, validation and garbage
collection are outside each timed interval. Garbage collection remains enabled
during the call; `gc.collect()` runs before each interval. The call includes
its normal admission, file reads, computation, report construction and internal
checks through return.

There are **48 warmup/ordinary calls** and **12 additional traced calls**:
60 top-level profiled API invocations. Setup separately invokes demo generation
once and study execution once to prepare the original saved replay report.
Result publication is another unprofiled helper call. Internal nested job/audio
calls are not counted as additional independent measurements.

Each allocation probe is a separate call under `tracemalloc.start(1)`. Tracing
starts **after setup, imports and input allocation**. Current and peak traced
bytes cover Python allocations observed during that call with its returned
result retained. They exclude pre-existing input arrays and imports, untraced
native allocations, and total process memory. They are **not RSS, an upper memory
bound or a maximum-allocation qualification**. Instrumented elapsed times are
retained separately and never enter ordinary timing statistics.

The timer reports `clock_gettime(CLOCK_MONOTONIC)`, monotonic, not adjustable,
with advertised resolution 1 ns. That resolution is not an accuracy or
uncertainty claim. The shared host was not pinned or isolated. Files were
created and hashed before timing, followed by one warmup; cache state was
uncontrolled, not a cold-storage experiment. Three samples provide an observed
range, not a percentile, confidence interval or worst-case deadline.

## Retained results

Times below are rounded to milliseconds; `results.json` retains integer
nanoseconds. Allocation peaks belong to the separate instrumented calls.

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

The fourfold audio input increase also increased full-inspection median from
30.854 to 125.324 ms. Returning a small window did not remove complete-stream
work. The eightfold comparison frame/work increase had medians 10.396 and
72.378 ms. These observations are consistent with the contracts' bounded work
model; they do not prove general scaling or supply a real-time guarantee.

Replay of the 119,423-byte study report had a separate traced peak of
**16,789,913 bytes**, while the study's peak was **1,405,809 bytes**. Source
inspection finds a bounded metadata reader requesting `max_bytes + 1`, with
replay supplying a 16 MiB limit. This is a concrete candidate for a separately
reviewed allocation investigation. This profile alone does not attribute the
peak to one allocation, and no production repair or new memory bound is claimed.

## Identities and practical limits

Collector: **20,353 bytes**, SHA-256
`33a4dd7dafd675165ee5f86d04c04145948859ce7d865d2312482e99341e0973`.

Results: **33,658 bytes**, SHA-256
`c7749036186638b00a9fc77663d5c55e308e64da0d6a3bbced7693c5bbac9789`.

The JSON retains exact identities for all ten source files, nineteen generated
fixture/report files and four in-memory input arrays. Complete API-output hashes
include the audio report's actual temporary `input_path`, so those full hashes
can change across collection locations. A second, explicitly labeled portable
hash replaces **only** that audio path with its fixture-relative name. It does
not remove metrics, statuses, source/runtime identities or other report content.
Other report projections make no change. Both identities are computed after
timing. The benchmark JSON encoding is sorted, indented UTF-8/LF; it is not the
audio CLI's compact encoding.

The largest measured audio file is 1/512 of the admitted 256 MiB ceiling; the
largest measured comparison spectral work is 1/128 of its 16,777,216-term limit.
Actual source constants are retained in `declared_source_limits`. Those caps
bound admission; they are not measured durations or process-memory budgets.
No maximum audio/corpus/study/report workload, WAV-format performance matrix,
native Windows/macOS collection, cold-cache storage, sustained load or numerical
accuracy campaign was run by this artifact. Existing independent acceptance
qualifies correctness separately. Physical calibration, acquisition, permissions,
holdout chronology, listening and instrument fidelity remain unestablished.
