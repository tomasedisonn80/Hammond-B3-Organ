# Assignment 35 — independent Engine rate acceptance

Agent: `/root/w06_a35_engine_rate_tests`

Wave: 06, assignment 35 of the continuation's 60 new agents

Date: 2026-11-13 UTC

## Scope and independence

Added only [test_engine_rate.cpp](../../../tests/test_engine_rate.cpp) and this
note. No production, build-system, shared-status, historical-test or data edits
were made. No staging, commits, pushes or subagents were used. The integrator
owns publication and the combined checkpoint.

Expected behavior comes from the public Engine, source, contact, percussion,
profile and control interfaces, [SAMPLE_RATE_LIFECYCLE.md](../../SAMPLE_RATE_LIFECYCLE.md),
[ENGINE_API.md](../../ENGINE_API.md) and
[CONSOLE_DYNAMICS.md](../../CONSOLE_DYNAMICS.md). Production implementation bodies
were not used to construct the test expectations. `AGENTS.md`, the project
plan/status/next-step material and the retained atlas review establish the task
and its evidence boundary. This assignment does not claim another full-PDF review.

Tests use the compiled nominal source profile plus deliberately varied,
unmeasured per-key contact durations/thresholds and percussion coefficients.
They are engineering fixtures, not acquired physical calibration values.

## What the permanent test checks

The main matrix contains all nine old/new rate pairs, both contact modes and
both already-rendered and newly restored control conditions: **36 scenarios**.
In travel mode all 122 keys are exercised simultaneously: 42 sustained keys,
40 partially pressing and 40 partially releasing. The ideal mode checks their
immediate-command counterparts. Enabled percussion, four different retained
banks, both manuals and nonunity expression remain active.

Before and immediately after each successful transition, full public snapshots
compare every held-key flag/count, all 122 positions/targets/nine-contact arrays,
all 91 phases, every control and checked control accessor, percussion diagnostics,
contact mode and frame clock. Only the reported rate changes. The first rendered
sample is bit-identical to an untouched old-rate copy. A separate direct sum of
physical branches checks that sample against source sinusoids, the public routing
map, gains, current readiness and contact bits. It does not reproduce the engine's
cached per-source accumulation order.

Further checks cover:

- **36 detector-edge scenarios:** all nine rate pairs, both modes and press/release.
  A single upper key makes or breaks its ninth contact after migration. Continuous
  distance times the owned travel duration gives the crossing time; rounding up
  to the new sample grid gives the exact number of old-detector samples under the
  render-before-advance contract. Separate closed-form decay/recovery intervals
  therefore detect a one-sample readiness-update error. Chosen crossings are
  checked to remain away from ambiguous integer boundaries.
- **6,144 repeated same-rate calls:** two calls per frame across 512 frames for
  each rate/mode, including interrupted/reversed movement. Every subsequent
  audio sample and complete public state matches an untouched copy exactly.
  A copied Engine can also migrate and advance without changing its source copy.
- **14 mixed-rate segments:** rate changes, Cancel, selection of upper A,
  restored B controls, fast/slow percussion, disabled percussion, zero expression,
  zero-frame calls and connected/disconnected processing. Source phase and contact
  motion follow the sum of each segment's `frames / rate`; readiness follows
  piecewise decay or recovery. The frame clock counts frames, not final-rate seconds.
- **81 rejected changes:** 13 unprepared requests establish `NotPrepared`
  precedence over valid and invalid rates; 60 prepared cases cover unsupported,
  adjacent, negative, zero, NaN, infinite and denormal rates; eight prepared cases
  cover 30 kHz sources valid at 96 kHz rejecting both lower rates, and the
  `44100 * 2^-53` frequency valid at 44.1 kHz rejecting both increases. Source
  failures use the last of 91 entries. Prepared rejection preserves complete
  snapshots and later exact audio/state through control and note events. The
  unprepared sequence also retains normal future preparation/output behavior.
- **Six ownership cases:** after preparation, every caller-owned source-profile
  field and every caller-owned console-model field is poisoned. All later rate
  changes, contact trajectories, source phases, readiness and output still match
  an Engine prepared from the immutable originals. The initial prepare itself
  preserves the complete input values.
- Failed re-preparation and invalid control restore retain the installed rate
  and complete existing state/future. Maximum block size stays 257 after each
  supported change: 258 frames reject atomically, 257 succeed, and excess output
  remains untouched. A near-maximum clock reaches `UINT64_MAX`, survives another
  migration, rejects overflowing processing and still accepts zero-frame calls.
  Initial clock origin does not introduce simulated source history.

There are **79 paired future probes** in addition to the pair matrix, repeated
same-rate paths and ownership renders. Exact audio counts exclude untouched
suffix sentinels, which are checked separately.

## Independent formulas and observed bounds

Phase expectations use current public phase plus frequency times accumulated
elapsed seconds, reduced modulo one turn. Contact expectations use current
position plus or minus elapsed seconds divided by the retained full-travel
duration, clamped to the target; threshold hysteresis is checked separately.
Readiness uses `q0 * exp(-t / decay_tau)` or
`1 - (1 - q0) * exp(-t / recovery_tau)` over declared detector intervals.
No expected path duplicates a per-sample production recurrence or source PRNG.

| Measurement | Observed count | Maximum observed absolute error |
| --- | ---: | ---: |
| Complete public snapshots | 13,776 | Exact equality where preservation is required |
| All-source phase comparisons | 12,740 | `5.5595068479408205e-14` turns, circular distance |
| Contact-position comparisons | 17,080 | `1.5943192946399343e-16` normalized travel |
| Contact-bit oracle comparisons | 153,720 | Exact |
| Readiness comparisons | 140 | `5.5177433802566789e-14` |
| Independent current-sample comparisons | 140 | `2.7298798391023251e-08` normalized amplitude |
| Paired rendered audio samples | 32,603 | Bit-identical, including floating zero sign |

The finite-window tolerances are `3e-11` turns for phase, `3e-13` normalized travel,
`3e-12` readiness, and `2e-6 * max(1, abs(expected))` for float audio. They permit
ordinary accumulation, reference-trigonometry and final float rounding, including
platforms where `long double` has double precision. They are not physical-fit or
indefinite-duration accuracy thresholds.

## Coherent source identity and commands

Assignment 34 confirmed the lifecycle production interfaces and implementations
were frozen. Root supplied immutable Git tree
`4370375d5dfe2161d8eefbf492cd692f2613d9c6`, containing the completed wave-05
checkpoint `093d985150a5d7e18b9c210126af0f08504024ce` plus the eight lifecycle
header/source changes and their supporting material. This test was copied on top
of an archive of that tree. The core and all four selected consumers were then
built together from that single frozen directory; no older library was linked
against later live headers. Permanent test code contains no scratch paths.

The final source directory was created with Python `subprocess.check_output`
running `git archive 4370375d5dfe2161d8eefbf492cd692f2613d9c6`, extracted using
`tarfile.extractall(..., filter='data')` into
`/workspace/scratch/60e8291da354/a35-qualified-src`, followed by `shutil.copy2`
of the repository's `tests/test_engine_rate.cpp` into the archive's test directory.

Exact final qualification commands:

```sh
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  -S /workspace/scratch/60e8291da354/a35-qualified-src \
  -B /workspace/scratch/60e8291da354/a35-qualified-build \
  -DCMAKE_BUILD_TYPE=Release
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  --build /workspace/scratch/60e8291da354/a35-qualified-build \
  --target test_engine_rate test_engine test_console_engine test_core_robustness -j 4
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/60e8291da354/a35-qualified-build \
  -R '^(test_engine_rate|test_engine|test_console_engine|test_core_robustness)$' \
  --output-on-failure -j 3
/workspace/scratch/60e8291da354/a35-qualified-build/test_engine_rate
```

Strict GCC 14.2.0 Release compilation passed with all repository warnings treated
as errors. **4/4 CTest suites passed in 0.63 seconds**, zero skipped tests.
The direct invocation emitted the counts and maxima above. Initial frozen-source
passes also succeeded before adding the targeted detector-edge coverage and
separating audio-frame counts from output-suffix sentinel checks. No production
defect, compile failure or failing test was observed. The repository test was
byte-compared with the qualified source and checked for trailing whitespace.

| Retained identity | SHA-256 |
| --- | --- |
| `include/hammond/Engine.h` | `9f8581865a263b4f10d2caa67cad0decf8cdf35e1f0c3a7ccbe21563518420f7` |
| `src/Engine.cpp` | `d072fe3d33201345982ddef375399d3932f4ec5b1f641095eb9d4e95b8cf3c65` |
| `tests/test_engine_rate.cpp` | `78fe4833d01c0b20f703de799ae3a9767a2a5545dc3f06d8092d819d6a371dfe` |
| Qualified `test_engine_rate` executable | `86e4b40643d9b54f05e9d01092619e2d26c9a513e1343101770b5daf6fee2da8` |
| Generated `nominal.b3p` | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |

## Next gate and limits

Integrate this test with the lifecycle implementations and assignment 36's
complementary owner/input checks. Qualify one exact staged combined tree, update
shared status/next steps/log, publish under the standing expected-head workflow,
and observe that revision's hosted platform results. CMake's existing test glob
already discovers the new file; no build-system edit is needed.

This scoped local gate does not establish concurrent rate publication, host/device
reactivation, resampling, a live wrapper, callback deadlines, allocation auditing,
cross-platform or sanitizer qualification, physical fidelity, or private cache
byte identity. Private cache behavior is observed through public state and future
audio. The current Engine note interface supplies endpoint targets; partial
positions here arise from interrupted travel, not an unimplemented Engine
partial-position event.
