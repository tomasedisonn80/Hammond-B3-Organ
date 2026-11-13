# Assignment 31 — phase-preserving source-rate lifecycle

Agent: `/root/w06_a31_source_rate_lifecycle`

Wave: 06, assignment 31 of the continuation's 60 new agents

Date: 2026-11-13 UTC

Reviewed starting revision: `4ead76957c763afbbddde1bc96f1128384329e50`, with
concurrent wave-05 files left intact and unstaged.

## Implemented contract

Added `TonewheelBank::reconfigure_sample_rate(double) -> Status` and the copied
`sample_rate()` diagnostic. The diagnostic reports samples per second, or zero
before the first successful preparation. A successful `prepare()` stores its
rate only after all existing preparation checks have passed. Its seed and sample
generation algorithms are unchanged.

Reconfiguration requires stopped or same-processing-thread access. It advances
no samples, draws no new seed values, and preserves all 91 current phases,
frequencies, amplitudes and cached source samples. It changes only the increments
and installed rate after validating every candidate increment. In order:

1. An unprepared bank returns `NotPrepared`.
2. A rate other than exactly 44100, 48000 or 96000 returns `InvalidSpec`.
3. The already installed rate returns `Ok` without changing any state.
4. A computed increment outside finite `[2^-53, 0.5)` turns/sample returns
   `InvalidProfile`, including for a muted source.
5. All valid candidates are installed together. Every failure preserves future
   source output and the previously installed rate.

The implementation uses one fixed array of 91 candidate increments. It adds no
allocation, parsing, file access, locking, logging or per-frame processing work.
The existing `process_frame()` body is unchanged. Preservation of its private
cached sample is visible in the mutation scope; public tests verify the preserved
phase/amplitude through exact first-sample identity, rather than claiming direct
access to that private cache.

## Source and reasoning

The [atlas](../../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf), pp. 63-66, was
read for this assignment. Page 63 explicitly requires phase continuity through
sample-rate changes and separates source integration from note/transport resets.
Pages 64 and 66 require prepared validation, persistent shared sources and
bounded numerical error. These statements support the lifecycle behavior, not a
new physical tuning or measured phase claim.

The accepted increment interval is the existing implementation decision in
[NUMERICAL_BOUNDS.md](../../NUMERICAL_BOUNDS.md). Reconfiguration applies that
same computational support boundary to already owned source frequencies. It does
not clamp an invalid source or replace it with a newly seeded oscillator.

## Independent tests and observed results

The new test uses closed-form elapsed-time phase and sinusoidal sample oracles.
It neither reproduces the source PRNG nor runs a second per-sample phase
recurrence as its expectation. Continuity checks capture the current public
phase before changing rate; later expectations integrate the retained frequencies
over elapsed time. Error bounds include binary64 accumulation and reference
arithmetic, including platforms where `long double` equals `double` precision.

| Check | Observed scope/result |
| --- | --- |
| Supported transitions | All nine old/new rate pairs, using both the nominal profile and synthetic varied amplitudes/base phases |
| Current state | All 91 phases remain bit-identical; first post-change source frame equals an untouched old-rate copy |
| Same-rate calls | 24,576 repeated calls, with exact output and final-phase identity |
| Tracked reconfiguration scenarios | 42 accepted scenarios, including mixed-rate time and numerical boundaries |
| Rejections | 80 reconfiguration cases: unprepared, unsupported/nonfinite/adjacent rates, Nyquist and minimum-increment failures |
| Rejection atomicity | Complete public phases/rate and exact subsequent samples compared with an untouched copy |
| Numeric admission | 30 kHz sources valid at 96 kHz reject both lower rates; tiny accepted sources reject rate increases; exact floor and just-below-Nyquist boundaries accept |
| Candidate ordering | Invalid or boundary sources at indices 0, 45 and 90, including muted sources |
| Phase oracles | 15,561 comparisons; maximum circular error `2.459699111057e-13` turns |
| Sample oracles | 15,561 comparisons; maximum absolute error `1.2362302208389e-12` normalized amplitude |
| Exact future frames | 61,772 paired frames, including rejection, same-rate and explicit fresh-prepare checks |
| Ownership and silence | Caller profile mutation cannot alter migration; discarded samples still advance; mixed-rate history follows elapsed time |

The new test and unchanged historical `test_tonewheel` and `test_numerics`
passed **3/3 CTest suites in 1.12 seconds**, zero skipped tests. Strict GCC 14.2.0
Release compilation passed with repository warnings treated as errors. No
implementation or test failure was observed in this scoped build.

Actual commands, from the repository root:

```sh
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  -S . -B /workspace/scratch/60e8291da354/a31-source-rate-build \
  -DCMAKE_BUILD_TYPE=Release
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  --build /workspace/scratch/60e8291da354/a31-source-rate-build \
  --target test_source_rate test_tonewheel test_numerics -j 4
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/60e8291da354/a31-source-rate-build \
  -R '^(test_source_rate|test_tonewheel|test_numerics)$' \
  --output-on-failure -j 3
/workspace/scratch/60e8291da354/a31-source-rate-build/test_source_rate
```

The direct invocation exports the numerical counts and maxima above. Permanent
tests use CMake-provided paths and contain no session-path dependency.

## Retained identities

SHA-256 values at the scoped check:

| File | SHA-256 |
| --- | --- |
| `include/hammond/TonewheelBank.h` | `694acaece901e18b4e089264218d8f217cfe3d2f8ea2a9adfb5ff6773b2f756b` |
| `src/TonewheelBank.cpp` | `ebc26e2e61cc88d5525e390abf3897ebeae38e652c13ea3ef02818b2b3849e0b` |
| `tests/test_source_rate.cpp` | `9b74e82af097441b6b4576be3f81f1fc0cf6d0d8e1ef3bb65f6075fcb952f17c` |
| Scoped `test_source_rate` executable | `023e4e4cd285dd8ccfdf4cfe7ebde2e94791e7b69c24d4812daabc3e92d3d43c` |
| Generated `nominal.b3p` | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |

## Changed files and next step

Only [TonewheelBank.h](../../../include/hammond/TonewheelBank.h),
[TonewheelBank.cpp](../../../src/TonewheelBank.cpp),
[test_source_rate.cpp](../../../tests/test_source_rate.cpp) and this note changed.
No Engine, Profile, CMake, shared-status, historical test or generated-binary
edits were made; no staging, commits, pushes or subagents were used.

Assignment 34 should compose this API with the separate contact and percussion
rate transitions, validating candidates before changing the live Engine. The
integrator must retain musical controls, contact/readiness history and render
clock through that operation, and reject an invalid source rate atomically.
This module gate is neither that Engine integration nor native audio-device,
host/concurrency, allocation-instrumentation, callback-deadline, cross-platform
or physical calibration qualification. Full combined-source and hosted checks
remain separate publication gates.
