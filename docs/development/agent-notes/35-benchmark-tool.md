# Agent 35 — prepared engine microbenchmark

Assignment: wave 06, portable bounded C++20 timing CLI and documentation.
Read `AGENTS.md`, current handoff/API/realtime documents, atlas review, and
chapter 062–063 text (PDF pp. 379–390). No engine or shared-status edits.

## Changes

- Added `tools/benchmark.cpp` and ordinary `hammond_benchmark` target; shared
  strict flags/core/generated-profile dependency apply. CTest discovery unchanged.
- Four fresh-engine workloads: silence, all 122 keys/nine selected-bank drawbars,
  disconnected output, and 1,024 changing drawbar events per positive call.
- Warmup, fixed buffer/event construction, diagnostics, sinks and statistics are
  outside timed `process` calls. JSON reports compiler/configuration, rate, block,
  seed, status/counts, clocks, checksums, min/median/p95/max and nominal interval.
- Strict unsigned arguments and combined limits: 10,000 positive calls and
  1,048,576 frames per case. Default: 128 recorded +16 warmup at 48 kHz/64 frames.
- `docs/BENCHMARKING.md` defines distributions, native-byte sink limits, absent
  provenance/machine fields, timing overhead and the separate future host gates.

## Executed commands and checks — 2026-11-13

From the repository root, CMake executable was
`/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake`:

```sh
cmake -S . -B /workspace/scratch/c871510c69b2/agent35-release -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build /workspace/scratch/c871510c69b2/agent35-release --target hammond_benchmark --parallel 2
```

Both succeeded. The native CMake path above replaces `cmake` in these commands.
A `python3 -` subprocess/JSON harness executed the default CLI, checked counts,
status vocabulary, finite ordered statistics, build fields and common final phases.
It compared each individually selected case to its `all` counterpart at
rate/block pairs `(44100,1)`, `(48000,17)`, `(96000,1024)`, `(48000,65536)` with
one recorded/one warmup call and seed `18446744073709551615`: **16 matches**.
It also observed **29 nonzero rejections** for missing/duplicate/unknown options,
malformed/overflow numbers, unsupported rates, bad block/call/warmup limits,
combined-work overflow, bad case names, oversized paths and missing/directory
profiles; `--help` succeeded. No timing threshold was asserted. `git diff --check`
passed. No Python CTest or optional-binary test dependency was added.

## Observed default run, not a deadline result

Debian GNU/Linux 13.6, Linux x86_64; `/proc/cpuinfo` reported AMD EPYC 9V74
80-Core Processor. Shared cloud scheduling, load/power/thermal conditions were
uncontrolled. GNU 14.2.0, C++20, Release `-O3 -DNDEBUG`, strict warnings/errors;
project sanitizers disabled. Build flags retained in `compile_commands.json`.
Overall subprocess wall time was 0.0767843 s; this is separate from call timings.
Recorded: 512 accepted calls, 32,768 frames, 131,072 automation events; zero
rejections. An additional 64 warmup calls and four setup flushes were excluded.
Per-call nominal frame interval: 1,333,333.333 ns. Raw JSON was retained at
`../agent35-release/benchmark-default.json`.

| Case | Min ns | Median ns | P95 ns | Max ns |
|---|---:|---:|---:|---:|
| silence | 79,888 | 81,850.5 | 198,583 | 880,259 |
| all_keys | 80,088 | 81,666 | 135,219 | 384,547 |
| disconnected | 75,952 | 78,000 | 289,778 | 2,045,427 |
| dense_automation | 123,422 | 126,046 | 213,084 | 1,209,123 |

The disconnected maximum exceeded the nominal interval; no pass/fail conclusion
is drawn. Instrument overhead is unqualified; no host/device/xrun was observed.

## Identity and handoff

This was an active **dirty shared-worktree build**, not an unmodified-HEAD result.
Initial HEAD was `b9c1cac`; it advanced to `9c8068c95f6843dce95f7f22d729738eef8074f6`
during shared work. Bank edits predate the bank object by filesystem timestamps,
but no immutable input snapshot was captured. Rebuild the final combined source.
Source revision and binary hash remain null in CLI JSON; the CLI does not discover
them. Observed SHA-256 values for this temporary build:

- Binary: `28e99dcf662b4420c60202772a61f436fc12c6086129aadf1dbe8b3f3436f9b0`
- Compiled profile: `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`
- `tools/benchmark.cpp`: `f7e285b2920f099131d2f291ad3b26a119b3bb4b657ec25a09ce41cb3eb97513`

No commits/pushes, new dependency, hosted/macOS/Windows execution, native callback
qualification, hardware fidelity or hard real-time claim. Integrator owns final
shared handoff and clean-build evidence.
