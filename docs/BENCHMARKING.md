# Prepared engine microbenchmark

`hammond_benchmark` reports **observed elapsed wall-clock intervals around
prepared `Engine::process` calls**. It is an offline, single-instance C++20 CLI
for the current nominal dry engine. It does not run an audio device, emulate a
host callback, qualify a hard real-time deadline, or establish instrument fidelity.
No timing value changes the exit status, and there are no CI speed thresholds.

The scope follows the distinction between measured time and work counts in atlas
chapter 062, pp. 379–384, and the stopped preparation/processing contract in
chapter 063, pp. 385–390 of the
[source PDF](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf). See
[ENGINE_API.md](ENGINE_API.md) for the processing contract and
[REALTIME.md](REALTIME.md) for the separate allocation observation and audit.

## Build and run

Use the normal C++20/CMake/Python prerequisites. The executable has no additional
dependency. CMake applies the existing strict warning flags, links the same
`hammond_core` as the renderer, and generates the nominal profile before building
the benchmark. It is an ordinary target regardless of `BUILD_TESTING`; it does not
change CTest discovery or require an optional executable from a Python test.

```sh
cmake -S . -B ../benchmark-release -DCMAKE_BUILD_TYPE=Release
cmake --build ../benchmark-release --target hammond_benchmark --config Release --parallel 2
../benchmark-release/hammond_benchmark > benchmark.json
```

With a multi-configuration generator, use
`../benchmark-release/Release/hammond_benchmark.exe` on Windows, or the generator's
corresponding configuration subdirectory. `--help` prints the accepted options.
The default uses 48 kHz, 64-frame blocks, seed zero, 16 warmup calls and 128 recorded
calls per case. It is a short screening workload; increasing observations does not
turn a finite run into a worst-case guarantee.

```sh
../benchmark-release/hammond_benchmark --sample-rate 96000 --block-size 1024 \
  --iterations 128 --warmup 16 --seed 42 --case dense_automation > dense.json
../benchmark-release/hammond_benchmark --block-size 65536 \
  --iterations 1 --warmup 1 --case disconnected > disconnected.json
```

| Option | Default | Accepted values |
|---|---|---|
| `--profile FILE` | Absolute path to this build's generated `nominal.b3p` | Readable regular compiled-profile file; loading is outside timing |
| `--sample-rate` | `48000` | `44100`, `48000`, `96000`, in samples/second |
| `--block-size` | `64` | `1..65536`, in frames |
| `--iterations` | `128` | `1..10000` recorded calls, subject to the combined limits below |
| `--warmup` | `16` | `1..1000` unrecorded calls, subject to the combined limits |
| `--seed` | `0` | Unsigned 64-bit decimal integer |
| `--case` | `all` | `all`, `silence`, `all_keys`, `disconnected`, `dense_automation` |

Warmup plus recorded work must fit **10,000 positive calls and 1,048,576 frames
per case**. Because at least one warmup is required, 10,000 recorded calls alone
cannot fit. All four cases together are therefore bounded by 40,000 positive
calls and 4,194,304 frames. Setup adds one unrecorded zero-frame flush per case.
Argument count is bounded; each value is at most 4,096 bytes and each number at
most 20 digits. Unknown/duplicate options, signs, whitespace, decimal/exponent
syntax, overflow, unsupported rates, missing values and excess work reject before
processing. A malformed profile or unsuccessful engine operation also exits
nonzero with a diagnostic on stderr. Success writes one JSON object to stdout.

## Fixed workloads

Each selected case prepares a fresh engine with the same profile, rate and seed.
Both manuals start with the selected B bank at `888888888`, enabled routes and
expression one. The inactive A banks retain their prepared zeros. Setup is an
unrecorded zero-frame flush; warmup uses exactly the case's recorded input shape.

| Case | Held keys and output | Events in each positive call |
|---|---|---|
| `silence` | No keys; connected output | None. The shared sources still advance. |
| `all_keys` | All 61 keys on each manual, 122 total; connected output | None. Nine selected-bank drawbars per manual remain at eight. |
| `disconnected` | The same 122 keys and registration; empty output span | None. Processing still advances the source field and clock. |
| `dense_automation` | The same 122 keys; connected output | Exactly 1,024 selected-bank drawbar changes, alternating both manuals and visiting all nine drawbars. |

Dense events are generated once before warmup. For event index `i` in `0..1023`,
the offset is `floor(i * block_frames / 1024)`. Sorted events occupy exactly
`min(block_frames, 1024)` distinct offsets; small blocks intentionally contain
ties. Each pair changes one drawbar `8 → 7 → 8`. The array ends with every drawbar
at eight, so every event changes a value again on the next call. Events at one
offset preserve input order; the engine rebuilds coefficients after the cluster.
This is a declared dense routing workload, not proof of the most expensive
possible future engine or host workload. It excludes note traffic, bank swaps,
zero-frame timing, cold first use, concurrency and multi-instance contention.

## Timing and report interpretation

The timed region contains a call between two `std::chrono::steady_clock::now()`
reads. Preparation, profile I/O, event construction, output/timing-vector
allocation and initialization, and all warmup calls precede recorded samples.
Output and event storage have fixed sizes and lifetimes during processing.
Status checks, finite-sample checks, checksum reads, phase diagnostics, sorting,
formatting, destruction and reporting occur outside the clock interval. There is
no vector growth or statistics computation in `Engine::process`.

The timer is a portable wall-clock observation, not a platform-qualified device
callback timer. Its read overhead is not subtracted; its reported tick period is
the C++ clock's nominal period, not measured resolution or accuracy. The process
is not pinned, paced, given real-time priority, or run with a controlled power or
thermal policy. Scheduling interruptions are included in elapsed intervals.
Between-call checksum work and fixed case order can affect cache and thermal
conditions even though their own duration is excluded. Warmup excludes startup
behavior from these distributions. No allocation, lock, I/O or system-call
interposition is performed by this executable.

The JSON uses schema `hammond-benchmark-v1`. Each case reports accepted call,
processed-frame and consumed-event counts, setup/warmup success, initial held-key
count, connected-output state, and start/end frame clocks. `processed_frames`
excludes warmup; `start_frame` is `warmup * block_frames`. A successful report
requires the engine's observed clocks and consumed-event counts to agree with
the requested work, and every observed connected sample/final phase to be finite.

`call_time_ns` contains the minimum, median, p95 and maximum elapsed call times,
in nanoseconds. The even-count median is the arithmetic mean of the middle two
sorted observations. P95 uses nearest rank `ceil(0.95 * count)`, with ranks
starting at one. A one-call run necessarily gives the same value for every
statistic; short runs cannot characterize rare tails.

`nominal_frame_interval_ns = block_frames / sample_rate_hz * 1e9` provides a
reference interval. The p95/max interval fractions divide those observations by
this reference. The interval is **not** a claim that a host grants the entire
interval to this engine, an end-to-end latency, a CPU-utilization measurement, or
an acceptance threshold. `hard_realtime_guarantee` and `timing_threshold_applied`
are explicitly false. Host/device underruns and runtime machine identity are
`null`, because the executable does not observe them.

The sample checksum consumes every recorded connected sample outside timing.
The final source-phase checksum consumes all 91 phases after recording and also
provides an observable sink for disconnected processing. Both are FNV-1a over
native object bytes, serialized as 16 hexadecimal digits. They are same-build
diagnostics, not cryptographic provenance or cross-platform audio fingerprints.
Disconnected sample checksum is `null`. Identical rate/block/call/seed inputs
should have the same final phase checksum across the four cases. Selecting a
single case preserves that case's setup and measured timeline. JSON consumers
must preserve 64-bit integers when reading the seed and counts.

## Retain the evidence actually available

The report records CMake's compiler ID/version, target OS/processor, selected
configuration, C++ language value, `NDEBUG`, and the project sanitizer option.
These identify configured build properties; the target processor is not a
runtime CPU model, and the sanitizer option does not detect arbitrary externally
injected compiler flags. Full flags remain in the build's `compile_commands.json`
and CMake cache. Debug or sanitizer runs remain labeled and should not be compared
as optimized Release capacity results.

`source_revision` and `binary_sha256` are deliberately `null`: this portable
executable does not discover Git state or hash its own binary. The profile ID and
authoring digest are retained profile fields, not authentication of unseen source
JSON. For retained comparisons, collect the actual binary and compiled-profile
SHA-256, source commit **plus dirty-tree state**, relevant uncommitted diff/untracked
source contents, exact command, compiler flags, raw report, CPU/OS and available
load/power context. Do not label a binary built from changed files as the
unmodified `HEAD` commit. Rebuild from a clean identified snapshot for stronger
provenance, and rerun after changes to the core, profile, toolchain or workload.

The [Agent 35 note](development/agent-notes/35-benchmark-tool.md) records the
initial Linux Release smoke, CLI invariants, observed values and dirty-worktree
identity limitations. This CLI supplies repeatable screening observations; native
host/device callbacks, cold starts, long-tail/load campaigns and platform-qualified
telemetry remain separate future evidence.
