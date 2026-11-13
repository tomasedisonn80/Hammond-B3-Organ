# Prepared engine microbenchmark

`hammond_benchmark` reports **observed elapsed wall-clock intervals around
prepared `Engine::process` calls**. It is an offline, single-instance C++20 CLI
for the current nominal dry engine. It does not run an audio device, emulate a
host callback, qualify a hard real-time deadline, or establish instrument fidelity.
No timing value changes the exit status, and there are no CI speed thresholds.

The explicit `console_motion`, `owned_input` and `console_all` selections add
nominal contact/percussion and transactional ownership workloads. They use the
separate `hammond-console-benchmark-v1` report described below. The default `all`
still selects exactly the four original ideal-contact/percussion-off cases and
retains its `hammond-benchmark-v1` structure and semantics.

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
| `--case` | `all` | Original `all`, `silence`, `all_keys`, `disconnected`, `dense_automation`; explicit `console_motion`, `owned_input`, `console_all` |

Warmup plus recorded work must fit **10,000 positive calls and 1,048,576 frames
per case**. Because at least one warmup is required, 10,000 recorded calls alone
cannot fit. All four cases together are therefore bounded by 40,000 positive
calls and 4,194,304 frames. Setup adds one unrecorded zero-frame flush per case.
Argument count is bounded; each value is at most 4,096 bytes and each number at
most 20 digits. Unknown/duplicate options, signs, whitespace, decimal/exponent
syntax, overflow, unsupported rates, missing values and excess work reject before
processing. A malformed profile or unsuccessful engine operation also exits
nonzero with a diagnostic on stderr. Success writes one JSON object to stdout.
Both JSON and help output are explicitly flushed and checked before success is
returned. A failed output stream can contain an incomplete prefix; consumers
must check the exit status before accepting any report.

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

## Explicit nominal console workloads

```sh
../benchmark-release/hammond_benchmark --case console_all --sample-rate 48000 \
  --block-size 384 --warmup 1 --iterations 7 --seed 71 > console-benchmark.json
../benchmark-release/hammond_benchmark --case owned_input --block-size 64 \
  --warmup 16 --iterations 128 > owned-input-benchmark.json
```

`console_all` runs exactly `console_motion` followed by `owned_input`. Selecting
one case preserves that case's complete input timeline and deterministic state/
sample sinks. It does not run any legacy case. The same per-case limits apply:
warmup plus recorded work fits 10,000 calls and 1,048,576 frames. The two-case
selection therefore admits at most 20,000 positive calls and 2,097,152 frames,
plus one unrecorded zero-frame setup per case.

Each case prepares a fresh Engine with `make_nominal_console_model()`, the
requested source profile, rate and seed. Setup flushes 18 selected-bank drawbar
settings to eight and four percussion settings to On / Second / Normal / Fast.
These **22 control events** hold no key, create no owner and advance no frame.
Upper and lower B banks are selected, routes are enabled and expression is one.
All nine sustained drawbars are retained on both manuals; eligible upper
percussion applies its declared one-foot mask and normal sustain compensation.

The arrays below are built once before warmup. Every command has offset zero.
Absolute call number `j` starts at zero for the first warmup call and continues
through recording without a reset or intervening flush.

| Case | Timed API | Fixed schedule |
| --- | --- | --- |
| `console_motion` | `Engine::process` | 122 direct `KeyPosition` events, one for every key on both manuals. Even `j` commands target 1; odd `j` commands target 0. The nominal travel preserves its current position and hysteresis across each reversal. |
| `owned_input` | `process_owned_notes` | 122 typed host commands per call; phase `j mod 4` adds first owners, adds second owners, releases first owners, then releases second owners. Only first acquisition and final release emit physical key events. |

The ownership fixture maps bus 0 to Upper and bus 1 to Lower. Channel 0 holds
the first owners and channel 1 the second. Keys visit MIDI 36–96 in manual order;
the corresponding identified note IDs are `0..121`. On velocity is 100 and Off
velocity zero. These are internal typed messages, not decoded MIDI bytes or a
native host ABI. After phases 0, 1, 2 and 3, owner counts are respectively
**122, 244, 122 and 0**; active physical targets are **122, 122, 122 and 0**.
The workload's 244-owner peak is below the adapter's 256-owner capacity.

There are no direct key commands in the owned-input case. Controls are applied
before the ownership timeline begins, so the adapter remains the sole authority
for its notes. No reset, rate change, route reassignment or serialization occurs
inside either timed workload. The two schedules are declared bounded exercises;
they do not establish the most expensive possible input or model state. Block
size determines elapsed motion between reversals. Small blocks may retain an
incomplete return or never cross a particular contact threshold.

### Console report and accounting

The new schema retains the common build, clock, interval and checksum fields,
and names `ideal-shared-sine-v1`, `nominal-linear-travel-v1`,
`shared-readiness-v1` and `bounded-fifo-note-ownership-v1`, with
`workload_version: 1`. The ownership identifier describes the included adapter;
the per-case `timed_api` distinguishes whether that adapter is actually called.
No model or parameter identity is inferred from the workload's audio.

For these cases, the common `events_per_call` is always 122, and
`event_offsets_per_call` is one. `input_event_domain` identifies whether
`events_consumed` counts direct physical-target events or typed host commands.
It equals `122 * recorded_calls` in both cases. The separately reported
`physical_events_consumed` is 122 per direct-target call, but only 122 on owned
phases 0 and 3 and zero on phases 1 and 2. Warmup input and physical counts are
reported separately and excluded from the recorded totals.

The common `active_keys` field retains its original meaning: the initial count
after setup, which is zero here. Additional `start_active_keys` and
`final_active_keys` describe the recording boundaries. `initial_owner_count`,
`start_owner_count`, `final_owner_count` and `max_observed_owner_count` distinguish
ownership from physical targets. The maximum observes completed warmup and
recorded calls; `workload_owner_bound` is 244 for owned input and zero for direct
motion. The known monotonic owner additions/removals also fit that bound inside
each call. Every call's actual consumed counts, owners and active targets are
checked outside timing; a mismatch fails the run.

The tracked diagnostic key is Upper MIDI 60. The report includes its final
position and target, final shared readiness, the number of recorded calls whose
position changed, and the sum of contact-bit changes between recorded call
boundaries. Each key receives at most one changed target at offset zero per
call, so motion is monotonic within that call. These observations are not a
per-frame trace of all 122 keys; use [CONSOLE_TRACE.md](CONSOLE_TRACE.md) for the
separate detailed diagnostic. A window can include held portions of the owned
schedule, and its reported motion count reflects that fact.

Event/view selection precedes the first clock read. Status checks, owner counts,
contact snapshots, finite-output checks, checksums and all statistics follow the
second clock read. No input construction, fixture allocation or diagnostic query
is inserted into the timed interval. Between-call observations still affect the
process's cache/load context, as do the legacy checksum reads. These reports do
not replace allocation interposition, platform telemetry, multi-instance load,
device underruns, long-tail measurements or a named-machine deadline campaign.

### Verification boundary

`tests/test_console_benchmark.py` invokes the actual executable, checks both
schemas and fixed workload counts, and independently computes key travel with
rational full-travel times. It covers all three supported rates, minimum and
maximum block sizes, the full unsigned seed range endpoint, repeated/single-case
sinks, early work/input rejection and portable readonly-stdout failures. It
checks nonnegative ordered timing statistics and their stated arithmetic without
setting a speed threshold. The [assignment 45 note](development/2026-11-13-continuation/45-console-benchmark.md)
retains the exact local source and observed results. Combined publication and
hosted-platform qualification belong to the integrating agent's ledger.
