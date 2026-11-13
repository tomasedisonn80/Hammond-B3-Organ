# Standalone benchmark acceptance

The maintained [Python suite](../apps/standalone/tests/test_standalone_benchmark.py)
checks the SDK-free `hammond_standalone_benchmark` CLI, report structure and
declared workload accounting against the [benchmark contract](STANDALONE_BENCHMARK.md)
and [Session contract](STANDALONE_SESSION.md). It applies no speed threshold.
The independent Linux Release run passed **9/9 methods and 111 CLI invocations**
in 2.792 seconds. This was the frozen direct executable; canonical CMake/CTest
integration remained pending at the assignment handoff. Exact tested identities are in
[assignment 30](development/2026-11-13-next-phases/30-benchmark-acceptance.md).

## Independent expectations

The test declares musical registrations, held targets and command counts from
the frozen workload contract. It does not read private Session state, implement
the benchmark clock, duplicate its quantile algorithm or infer a passing speed
from the current runner. JSON must have exact documented members and types;
duplicate members, nonfinite values and malformed or extra output reject.

| Boundary | Acceptance |
| --- | --- |
| CLI admission | Required profile; help alone; duplicate, missing, unknown, partial, overflowing and out-of-range options fail without success JSON. No output option or implicit file writes. |
| Profile boundary | Malformed, truncated, trailing-token, oversized and unsupported-at-selected-rate inputs fail; private fixture bytes survive. A valid copied profile supports Unicode and space paths. |
| Identity | Rehash every entry of the supplied sorted source manifest and recompute its aggregate SHA-256; compare exact configured compiler/version, configuration and target values. Independently hash the actual profile bytes and verify retained authoring provenance. |
| Configuration | Supported sample rates and all buffer choices retain exact requested values; defaults remain explicit in the report. An impossible SDL driver setting does not block SDK-free execution. |
| Timing | Finite nonnegative ordered minimum, quantiles and maximum, correct sample count and callback period; steady-clock and unadjusted-time declarations. No elapsed-time correctness budget. |
| Work accounting | Setup, warmup and measured work retain separate command, render, rejection, frame and recovery counts. Zero-frame work never advances the sample clock. |
| Musical results | Silence remains quiet; performance and dense workloads retain the six declared held targets and registration; recovery clears holds while retaining installed controls. |
| Output failure | An unwritable stdout descriptor returns nonzero and preserves an existing private sink. |

Dense work admits 256 expression commands before each positive render. Recovery
first admits six note-ons and flushes them at zero frames outside the measured
interval; the later full queue produces one `QueueFull` and one
`RecoveryPending` response. Its positive callback discards 256 queued controls,
recovers once and clears the six held targets. This re-arming is necessary for
each recovery sample to exercise a real held-note release. Warmup activity must
not be reported as measured work. `stages.measured` accounts for the entire
measurement loop, including its explicitly counted outside-timer rearm flushes;
`timing.samples_ns` contains only the positive render intervals.

The callback period is exactly `buffer_frames / sample_rate_hz` seconds. Sample
clock assertions use positive renders only; a setup or re-arming zero-frame
flush contributes no frames. Timing comparisons only check report consistency
and ordering, including tails. They do not demand a minimum measurable timer
tick or compare callback duration with that period as a pass/fail condition.

## Reproduce

From the repository root with the ordinary C++20/Python/CMake prerequisites:

```sh
cmake -S . -B ../build-standalone-benchmark -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_TESTING=ON -DHAMMOND_BUILD_STANDALONE=OFF
cmake --build ../build-standalone-benchmark \
  --target hammond_standalone_benchmark hammond_profile --parallel 2
ctest --test-dir ../build-standalone-benchmark -C Release \
  -R '^test_standalone_benchmark$' --output-on-failure --no-tests=error -V
```

CTest supplies `HAMMOND_STANDALONE_BENCHMARK_EXECUTABLE`, `HAMMOND_TEST_PROFILE`,
`HAMMOND_STANDALONE_BENCHMARK_SOURCE_MANIFEST`, `HAMMOND_SOURCE_DIR`, and exact
`HAMMOND_STANDALONE_BENCHMARK_EXPECTED_*` configuration/compiler/target values.
Direct invocation requires those inputs; binary/profile paths must name existing
files, and missing prerequisites fail instead of silently skipping. The suite
uses Python's standard library and private `TemporaryDirectory` fixtures. Tests
normally request 100 measured callbacks; the default-options check exercises
the documented 500. The CTest timeout is 60 seconds and is a stuck-test bound,
not an audio deadline.

## Scope

This suite exercises a serialized, synthetic Session workload on the current
runner. It does not qualify SDL transport, hardware audio, actual device callback
timing, latency, scheduler interference, host underruns or real-time deadlines.
The nominal dry core remains the audio model; no measured B-3, AO-28, scanner or
Leslie fidelity follows. Concurrency and callback-allocation gates retain their
separate maintained tests and evidence.
