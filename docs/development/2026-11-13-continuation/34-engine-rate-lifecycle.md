# Assignment 34 — transactional Engine sample-rate lifecycle

Agent: `/root/w06_a34_engine_rate_lifecycle`

Wave: 06, assignment 34 of this continuation's 60 new agents

Date: 2026-11-13 UTC

Qualification base: `72b5062dd4d02acc42c30faf291465c7633b87d9`, with exactly the
eight frozen production overlays identified below. The integrating agent
published wave 05 as `093d985` during this assignment. That later revision was
not silently substituted into this scoped qualification; assignments 35/36 and
the integrator own the later combined-source gate.

## Implemented contract

Added `Engine::reconfigure_sample_rate(double) -> Status` and a copied
`sample_rate() -> double` diagnostic. The latter returns zero until the first
successful preparation, then the currently installed samples per second.
Failed preparation and failed reconfiguration preserve that installed value.
Both require stopped or same-processing-thread access, with a transition
occurring between processing calls.

The implementation follows this admission and commit sequence:

1. An unprepared Engine returns `NotPrepared`, including for invalid inputs.
2. Anything except exactly 44100, 48000 or 96000 returns `InvalidSpec`.
3. The installed rate returns `Ok` as an exact no-op, without recomputing
   coefficients or rebasing contact segments.
4. Validate the Engine's owned `RuntimeProfile` at the proposed rate.
5. Copy each of the source bank, contact bank and percussion state to a local
   candidate, and call its `reconfigure_sample_rate()`. Propagate the first
   rejection before changing any installed state. Source increments retain the
   existing finite `[2^-53, 0.5)` turns-per-sample support bounds.
6. Install all three accepted candidates and change only `spec_.sample_rate`.

Success advances no sample, reseeds no source and resets no key or readiness
state. It preserves all 91 source phases, source parameters and cached samples;
all held keys, contact positions, targets and connection histories; readiness;
retained banks, selected routes, expression and percussion settings; the maximum
block size, seed and initial frame origin; and the current render clock.
The module candidates update source increments, contact travel steps and
moving-segment origins, and percussion decay/recovery coefficients. A transition
does not evaluate a contact edge.

Engine's sustained/percussion coefficient arrays, dirty flag and eligibility
cache remain valid because source amplitudes, controls, routing and current
contact connections have not changed. These fields are left untouched. Failure
preserves the complete Engine and its future output. Fixed value copies and
arithmetic introduce no allocation, file access, logging or locking in this
path; allocation instrumentation and callback deadline measurements were not
performed by this assignment.

`frame_clock()` remains a count of rendered frames. Mixed-rate elapsed model
time is the sum of each segment's rendered frames divided by its rate. It cannot
be recovered by dividing the final frame count by the most recent rate; the
caller must retain the rate-change schedule and any external seconds-to-event
conversion. This API does not change the offline score format or add native
audio-device negotiation. See [SAMPLE_RATE_LIFECYCLE.md](../../SAMPLE_RATE_LIFECYCLE.md)
for the public lifecycle and ownership contract.

## Source basis and limits

The supplied [atlas](../../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf), complete
pages 105, 135, 385 and 394, was read for this assignment. Page 105 requires
explicit source phase ownership across changes of sampling interval. Page 135
describes continuous percussion state and rate-dependent integration of
time constants. Pages 385 and 394 separate the host-independent core from
wrapper preparation and host lifecycle handling. The existing nominal contact
and readiness models remain the scope; this work supplies no measured B-3,
AO-28, scanner, cabinet or native host result.

The source, contact and percussion APIs were coordinated directly with their
owners before the source freeze. Assignment 32 confirmed its header/source
hashes and assignment 33 confirmed its production files remained unchanged
after qualification. This assignment did not edit any of those modules or their
tests. It did not use a later live header against the frozen library.

## Observed verification

The smoke harness was intentionally kept outside the repository because
assignment 35 owns independent permanent Engine acceptance tests. It used the
frozen source's public headers and linked only the library built from that same
snapshot. Its non-default seed was `1138137`, initial frame `971`, and maximum
block size `257`. Every prepared fixture enabled upper percussion, retained
distinct bank controls, held an upper detector key, and had other upper/lower
keys pressing and releasing. Both ideal and nominal contact modes were covered.

| Check | Observed scope/result |
| --- | --- |
| Accepted transitions | 37: all nine old/new pairs in both contact modes with ordinary and pending control-cache changes, plus a `uint64_t` clock-boundary case |
| Immediate continuity | Exact copied controls, all 122 held-key/contact snapshots, all 91 source phases, complete percussion routing diagnostics and frame clock |
| First post-change sample | Bit-identical to an untouched old-rate copy in all 36 pair scenarios |
| Source next state | 3,276 checks against current phase plus frequency times the new sampling interval; maximum circular error `1.0375814790686277e-16` turns, tolerance `3e-16` |
| Percussion next state | 36 checks against current readiness times the closed-form fast-decay factor; maximum absolute error `6.0173220572945496e-17`, tolerance `2e-16` |
| Contact next state | 144 upper/lower press/release checks against current position and the new interval; maximum absolute error `5.1499603193061461e-17` normalized travel, tolerance `3e-16` |
| Exact same-rate calls | 186 calls interleaved with rendered frames; current and subsequent state match an untouched copy exactly |
| Rejected rate calls | 95: 15 unprepared precedence cases, 72 unsupported/nonfinite/extreme inputs on prepared engines, and eight source-profile or increment-bound rejections |
| Source rejection cases | An owned 30,000 Hz source at 96 kHz rejects both lower rates, including after caller-profile mutation; a source at the minimum increment at 44.1 kHz rejects both higher rates after profile-level validation succeeds |
| Exact future audio | 137,788 paired float samples compared by bits, including first-sample checks, same-rate/rejection continuations, and connected/disconnected advancement |
| Retained block limit | All 36 pair scenarios still reject 258 frames, preserve state and leave guarded output untouched |
| Clock exhaustion | A rate change succeeds at `UINT64_MAX` without advancing the clock; one rendered frame still returns `TimelineOverflow`, while a zero-frame flush succeeds without state changes |

The one-step mathematical oracles use `long double` evaluation of elapsed time,
not a second copy of the module's per-frame recurrence. Their small local
tolerances cover binary64 arithmetic for these bounded, one-step cases; they do
not claim a long-duration or universal platform error bound. Exact equality is
required for preserved state and paired future behavior. The private caches are
not exposed by a new diagnostic: code inspection establishes their mutation
scope, and output continuation checks exercise their observable behavior.

Strict GNU C++ 14.2.0 Release compilation passed for the core, the compiled
nominal profile, the smoke executable and three historical Engine consumers.
`test_engine`, `test_console_engine` and `test_core_robustness` passed **3/3 CTest
suites in 0.42 seconds**, with no skipped tests. The smoke passed with the counts
above. Its first compilation rejected a dangling reference to a temporary
`ConsoleModel` in the scratch harness; copying that key's parameters fixed the
harness. No production source changed in response, and no core assertion or
runtime test failure occurred.

The valid public preparation contracts already constrain contact/percussion
parameters so every supported rate yields valid coefficients. This smoke does
not corrupt private storage to manufacture those defensive rejection branches.
Source-rate failures are reachable through valid preparation and exercise
Engine's validation and failure-atomic continuation. Module-specific independent
suites and assignment 35 provide separate acceptance evidence.

## Exact qualification commands and identities

The snapshot was created by `git archive` of the pinned base, followed by copying
only these eight frozen header/source files into the extracted tree. Each copied
file was hashed, and the live file was rehashed to confirm it had not changed.
The metadata was written to
`/workspace/scratch/60e8291da354/a34-rate-qualification/snapshot.json`.
No Git staging or index operation was used.

| Frozen overlay | SHA-256 |
| --- | --- |
| `include/hammond/Engine.h` | `9f8581865a263b4f10d2caa67cad0decf8cdf35e1f0c3a7ccbe21563518420f7` |
| `src/Engine.cpp` | `d072fe3d33201345982ddef375399d3932f4ec5b1f641095eb9d4e95b8cf3c65` |
| `include/hammond/TonewheelBank.h` | `694acaece901e18b4e089264218d8f217cfe3d2f8ea2a9adfb5ff6773b2f756b` |
| `src/TonewheelBank.cpp` | `ebc26e2e61cc88d5525e390abf3897ebeae38e652c13ea3ef02818b2b3849e0b` |
| `include/hammond/ContactBank.h` | `a083dcd65d989cc5be78a393fad74f40cbb530e33f89492d523e406f477be99d` |
| `src/ContactBank.cpp` | `91747d963d6cec74b3be12549abd8e816f4c176ce172fba52f9cdbc593c6e9e1` |
| `include/hammond/Percussion.h` | `5eb87fdd2342410b63f7e6ec55ac11c645d2b7185287fb49ff8e5e53095a2722` |
| `src/Percussion.cpp` | `823685b879fad12492f86bbf5e78294668ee9b0567c58c26ac0b44aa28b1390a` |

Commands actually run from the repository directory; line wrapping is for
readability:

```sh
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  -S /workspace/scratch/60e8291da354/a34-rate-qualification/source \
  -B /workspace/scratch/60e8291da354/a34-rate-qualification/build \
  -DCMAKE_BUILD_TYPE=Release
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  --build /workspace/scratch/60e8291da354/a34-rate-qualification/build \
  --parallel 2 --target hammond_core hammond_profile \
  test_engine test_console_engine test_core_robustness
c++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion \
  -Wsign-conversion -Wshadow -Werror \
  -I /workspace/scratch/60e8291da354/a34-rate-qualification/source/include \
  -I /workspace/scratch/60e8291da354/a34-rate-qualification/source/tests \
  -DHAMMOND_TEST_PROFILE='"/workspace/scratch/60e8291da354/a34-rate-qualification/build/nominal.b3p"' \
  -DHAMMOND_SOURCE_DIR='"/workspace/scratch/60e8291da354/a34-rate-qualification/source"' \
  /workspace/scratch/60e8291da354/a34-rate-qualification/smoke.cpp \
  /workspace/scratch/60e8291da354/a34-rate-qualification/build/libhammond_core.a \
  -o /workspace/scratch/60e8291da354/a34-rate-qualification/smoke
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/60e8291da354/a34-rate-qualification/build \
  --output-on-failure -R '^test_(engine|console_engine|core_robustness)$'
/workspace/scratch/60e8291da354/a34-rate-qualification/smoke
```

Scratch harness SHA-256:
`ca0b8b1ab867a46ec0c9d1602c44e97942137dfcc4e8e7dd66cef6259be389f7`.
Snapshot metadata SHA-256:
`dd7d31e23dc80caf80385109e0bf1baf17d61bab4497e57738263acbc339d0ef`.
These temporary paths identify the observed run. Permanent acceptance must use
assignment 35's repository test and a freshly recorded coherent snapshot, not
depend on these session directories surviving.

## Files and concrete handoff

Changed only [Engine.h](../../../include/hammond/Engine.h),
[Engine.cpp](../../../src/Engine.cpp),
[SAMPLE_RATE_LIFECYCLE.md](../../SAMPLE_RATE_LIFECYCLE.md) and this note.
No shared status, CMake, module, permanent test, schema or control-format file
was edited. No staging, commits, pushes or subagents were used by assignment 34.
The integrator owns the authorized publication and current shared handoff.

Assignment 35 must independently qualify the public Engine contract against
the frozen wave-06 source. Assignment 36 and the integrator must inspect and
qualify the complete staged wave after integrating all module/test files and
current consumers, then record the exact committed/pushed revision and actual
hosted results. New Engine work must start from that coordinated boundary;
rebuild core and every consumer together if a header subsequently changes.
Concurrent hot swaps, device changes, native SDK activation, cross-platform
numeric results, physical calibration and callback deadline qualification
remain separate gates.
