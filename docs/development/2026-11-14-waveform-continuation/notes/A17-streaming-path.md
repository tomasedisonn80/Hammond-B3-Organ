# A17 — Independent bounded streaming-path acceptance

## Assignment and scope

- Actual worker: `/root/w03_a17_streaming_path_acceptance`, waveform continuation,
  wave 3, A17 of the requested sixty actual assignments.
- Owned files: this note and `tests/test_rotary_streaming_path.cpp`.
- Observed HEAD: `26ff2fbe66a50260bd7601cbfa54c1f5d35ff3a8`. New streaming
  sources and headers are uncommitted worktree inputs identified below; HEAD
  alone does not qualify them.
- Read the standing instructions, current continuation scope/checkpoint and
  actual assignment manifest, complete M0–M9 plan, current status/next steps,
  numerical/propagation contracts, frozen renderer contract §§1–2 and public
  headers, native implementations, independent reference header, and A04's
  retained rotary atlas reading. This is not another complete atlas reading.
- No production source/header, shared CMake/build, manifest, shared status or
  publication changes. No nested workers were spawned.

**Passed:** strict direct compilation and both final executions, including a
512 KiB stack run, with byte-identical JSON reports. There are **345,828 checks,
3,952 graded successful path cases, 3,940 exact immutable-R3 comparisons,
2,804 independent reference comparisons, 73 preparation rejections and 109 solve
rejections**. No production defect was observed and no implementation was changed.

## Executed test design

The executable directly calls the actual `PreparedStreamingPath` implementation,
`MotionFrameHistory`, and qualified immutable `PreparedRetardedPath`. Every
immutable fixture is built with native original event segments before its
borrowed view is prepared. Its vector remains alive, stable and immutable until
all dependent paths are destroyed. Streaming histories and complete history
snapshots are heap allocated; no history-sized local stack objects are used.

The independent oracle is `tests/reference/rotary_waveform_reference.h`:
`independent-long-double-waveform-v1`, using its own motion integration,
Cartesian geometry and **pure bisection**, with target `1e-16 s`. It includes no
production headers or production mathematical functions. This platform's
`long double` has 64 significand bits, not 80 decimal digits. Its broader
high-precision qualification remains separately owned; this test does not
substitute for that gate.

### Matched motion and retarded-command fixtures

The two rapid/slow moving fixtures share origin `(-0.12,0.07,1.10) m`, radius
`0.18 m`, microphones `(1.35,-0.80,1.25)` and `(-1.20,-0.65,0.90) m`, sound speed
`343 m/s` and reference distance `1 m`:

| Fixture | Slow / fast rad/s | Up / down tau s | Initial phase rad | Initial speed rad/s |
| --- | --- | --- | ---: | ---: |
| Rapid commands | 5 / 70 | 0.001 / 0.01 | 0.31 | 7.25 |
| Long decay, seed above targets | 0 / 75 | 0.01 / 60 | 5.9 | 90 |

Both use initial Chorale and both directions at all four exact supported rates.
Each actual streaming history receives 4,096 intervals, with capacity 4,096.
The explicit ordered events are `(frame,command)`:

```text
(0,T), (0,C), (1,T), (31,C), (32,T), (32,C), (32,T), (63,T),
(64,C), (257,T), (1024,C), (1025,T), (2048,C), (3071,T), (4096,C)
```

Here `C=Chorale` and `T=Tremolo`; the canonical immutable fixture has eleven
segments. This covers equal-frame replacement, unchanged commands and an exact
final-boundary command. Twenty-five supplied observation positions include
negative prehistory, startup, fractions immediately below the next integer,
boundaries before/on/after commands, and exact final coverage. An additional
768 path solutions use **independently calculated receiver arrival times** for
emissions one sample before, on and one sample after eight command boundaries.
Before/after roots are explicitly checked to lie on the intended command side.

Exact R3 comparison checks every named `PathResult` double by binary64 bits,
the evaluation count, and both split emission fields. It also checks the
prepared object's bytes and complete retained-history equality across queries.
Independent comparisons separately grade the retarded root, frequency ratio,
split emission, native motion at the returned emission, and Cartesian geometry
at exactly the native supplied phase/speed. This separates native motion error
from geometry/root error. The reported motion contribution bound is
`radius*phase_error/(c*(1-beta))`.

### Additional independent cases and boundary behavior

| Group | Actual coverage |
| --- | --- |
| Analytic stationary paths | 1,080 queries; all rates, both directions, sound speeds 300/343/380, reference distances 0.02/1/10; zero radius with moving phase, zero-speed nonzero radius, exact 0.02 m minimum path and 20 m maximum path, independent Cartesian norm/delay/gain, zero radial speed and unit ratio |
| Geometry grid | Radii 0/0.02/0.18/1 m, four phase quadrants, both directions, three sound speeds, all rates, receivers near minimum clearance/on the other side/above the orbit, and zero-radius or admitted Mach-limit initial speeds |
| Original anchor retirement | All rates and both directions; capacity 512, 4,096 real appends, oldest frame 3,584, real command anchor 31 retained unchanged in the oldest and latest slots; 56 positive/negative queries compared with immutable R3 and the independent reference |
| Missing coverage | Old observations, the exact retained oldest observation whose earlier emissions are gone, future observations, fractional time after the exact final endpoint, and negative prehistory that remains available after positive retirement |
| Complete bracket admission | A stationary nonzero-radius root is retained, but the analytical upper bracket endpoint reaches retired history; streaming solve correctly rejects with `InsufficientHistory` after a prior endpoint succeeds, preserving both destinations |
| Epoch boundaries | Eight coherent 2,048-slot final-day windows, both directions at all rates; a real native original segment at zero and a command 1,000 frames before the endpoint; 64 exact R3 comparisons at negative/positive day limits; invalid epoch endpoints reject |
| Split precision | At the positive one-day limit, observation differences of `2^-30` frame survive exactly in returned fractional emissions; no absolute frame-to-double conversion is used in the expected check |
| Alternate seeds and stopped rates | Sixteen accepted same-path uses across the four rates, including initial speeds 0/40/70 under an original envelope of 70 and a stopped epoch with nonzero turns; changed phase/command is admitted; a seed one binary64 step above the envelope rejects |
| Mach extrema | Sixteen tangent paths at `radius=0.375 m`, speed `200 rad/s`, `c=300 m/s`, exact `beta=0.25`; both directions and approaching/receding signs; analytic radial speeds `+75/-75 m/s` and ratios `4/3` and `0.8` |

The full-day friend accessor only creates a finite, coherent retained window
from native original segments. It does not claim billions of executed appends,
long-duration waveform processing, or a replacement R2 long-epoch oracle.

### Rejection and preservation

Preparation checks cover each origin/microphone coordinate, radius, every
motion speed and tau, direction, phase, initial command, sound speed and reference
distance; NaN/infinity and out-of-domain values; slow greater than fast; a clear
initial pose with a colliding full orbit; distance beyond 20 m; and Mach overflow
caused independently by a target or the original seed. Every rejected reprepare
keeps the entire previous prepared path byte-identical and reproduces its earlier
accepted result exactly. Rejected preparation of a default path also preserves
the unprepared object.

Solve rejection checks unprepared path/history, all five mismatched motion
profile fields, seed speed just above the original admitted envelope, invalid
fractions, retired/future positive coverage, full signed integer extremes, the
one-day endpoints and emission outside the negative epoch. Both caller
destinations retain their exact sentinel bits, including signed zero, and the
prepared path remains unchanged. Whole histories are compared where relevant.

## Frozen limits and numerical results

Results are from final direct native execution at 2026-11-14 22:19:13 UTC.
All checks passed in the initial run and the final source-identified runs. The
final test-only review improves printed fractional coordinates, adds default
path preparation preservation, and expresses the diagnostic ratio range using
the exact frozen derivative allowance. No numerical acceptance limit was
relaxed in response to an observed failure.

| Quantity | Acceptance limit | Observed maximum | Observed RMS |
| --- | ---: | ---: | ---: |
| Independent root delay difference | `2e-11 s` | `1.1574636191044813e-14 s` | `4.5696009673681923e-15 s` |
| Independent frequency-ratio difference | `2e-10` | `9.970751546455048e-12` | `9.239067326440657e-13` |
| Same-state Cartesian distance difference | `2e-12 m` | `3.859759734048396e-16 m` | `1.130944897267993e-16 m` |
| Same-state Cartesian ratio difference | `2e-10` | `1.676176558662590e-16` | `6.557551512998372e-17` |
| Same-state pressure-gain difference | supplemental `1e-10` | `5.198272368112100e-14` | `4.467801781353296e-15` |
| Independent motion angle difference | `5e-12 + 4e-15*abs(reference_angle)` rad | `3.537318007951207e-15 rad` | `6.494225820937170e-16 rad` |
| Independent motion speed difference | `5e-12 + 4e-14*abs(reference_speed)` rad/s | `2.374489493917054e-14 rad/s` | `3.454883301725997e-15 rad/s` |
| Motion contribution to root error | separately reported | `4.959724457068772e-18 s` | `6.728297217698874e-19 s` |
| Analytic stationary delay difference | `2e-11 s` | `3.756286189211810e-16 s` | `1.568857134109866e-16 s` |
| Analytic stationary distance difference | `2e-12 m` | `6.342582709040201e-17 m` | `3.769435887005150e-17 m` |
| Analytic stationary gain difference | supplemental `1e-10` | `1.040834085586084e-14` | `2.714740200190487e-15` |

Native maximum absolute residual is `9.996344030316351e-15 s` against
`1e-11 s`, with at most **41 total evaluations** against 48. Independent
maximum residual is `9.998376909389761e-17 s` against its deliberately tighter
`1e-16 s` target, with at most **47 total evaluations**. Selected reference
roots use its separate count convention; they are not required to match native
counts. Exact R3 parity does require identical native/R3 counts.

The worst independent delay case is `Fs=44100`, direction `+1`, radius `1 m`,
phase `pi/2`, `c=343 m/s`, microphone `(-2,0.3,0) m`, observation `{0,0}`.
The worst independent ratio case is `Fs=44100`, direction `-1`, radius `1 m`,
phase zero, `c=300 m/s`, microphone `(1.020001,0,0) m`, observation `{0,0}`.
The largest split-emission discrepancy is `2.222421580100331e-9 frames` at
192 kHz in the same radius/phase/c/microphone case as the delay maximum.
The source-defined fixture and report retain all remaining worst coordinates.

## Reproduction and exact source identity

Working directory:
`/workspace/scratch/e3cacb90cc81/Hammond-B3-Organ`.
Compiler: GCC `g++ (Debian 14.2.0-19) 14.2.0`; Linux x86_64, glibc 2.41.
This test requires only C++20 and the listed repository sources/reference;
there are no downloaded dependencies, generated profiles or random seeds.
All fixture values and command sequences are deterministic and defined in the
hashed test source.

```sh
mkdir -p ../a17-streaming-path
g++ -std=c++20 -O2 -fno-fast-math -ffp-contract=off \
  -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror \
  -Iinclude tests/test_rotary_streaming_path.cpp \
  src/RotaryMotion.cpp src/RotaryPropagation.cpp src/RotaryHistory.cpp \
  src/RotaryStreamingPath.cpp \
  -o ../a17-streaming-path/test_rotary_streaming_path
../a17-streaming-path/test_rotary_streaming_path
```

The constrained-stack run used Python `resource.setrlimit` before executing the
same binary. Reproduction of that exact stack setting:

```sh
python3 - <<'PY'
import resource
import subprocess

def bounded_stack():
    _, hard = resource.getrlimit(resource.RLIMIT_STACK)
    resource.setrlimit(resource.RLIMIT_STACK, (512 * 1024, hard))

subprocess.run(['../a17-streaming-path/test_rotary_streaming_path'],
               preexec_fn=bounded_stack, check=True)
PY
```

| Final execution | Result | Wall time |
| --- | --- | ---: |
| Strict native compilation | Exit 0; no diagnostics | 4.915402 s |
| Normal execution | Exit 0; empty stderr | 0.121482 s |
| 512 KiB-stack execution | Exit 0; empty stderr; stdout exactly identical | 0.136113 s |

These wall times describe this bounded offline test only. They are not a device
deadline or benchmark claim. CPU-heavy work was held while A18 acquired its
separate paired UI timing cells.

Actual local evidence, relative to the repository working directory, is in
`../a17-streaming-path/results.json`, `verification.json`,
`source-identities-final.json`, and the two stdout/stderr pairs. The verification
record contains the exact compiler argv, UTC, platform, durations, source
identities, native report, executable/report hashes and output-equality result.

- Executable: 151,184 bytes; SHA-256
  `c9d8a3d0a24d0370f39d80543785e2487c8c75816c63e9289cd20a47fb21888e`.
- Native JSON report SHA-256:
  `cf6d00b81f5846d66803c1d8a21d1511bf873c5b2b110d10f05e37149cacfb0c`.

All fifteen relevant source hashes below were captured immediately before the
final direct compilation and verified **unchanged after both final executions**:

The prior test hash, captured before compilation, is
`ce1d9e035077314ad45ad4a0a1ba4d86effde1877f438c65c552565f7054d17f`.
Its sole subsequent source change replaces the supplemental ratio bounds
`0.8-2e-15` / `4/3+2e-15` with the contract-derived
`1/(1.25+2e-15)` / `1/(0.75-2e-15)`. The local
`pre-bound-edit-to-final.diff` and `verification.json` retain the exact hunk
and both identities; reversing that hunk matches the actual earlier hash.
Root reported that its concurrently started 160-test suite uses the pre-edit
binary. That outcome and the subsequent final-source target rebuild/filtered
recheck must be recorded separately by root; this worker claims neither run.
The final test is frozen and every production input is unchanged.

| Input | SHA-256 |
| --- | --- |
| `tests/test_rotary_streaming_path.cpp` | `ab6526e628018a52a89a8bfc23eec8337ce8e9b152811ba8bc28d8787fb04dfa` |
| `tests/reference/rotary_waveform_reference.h` | `3c24792f80f86f903926622f4bf016984caf44d727ad3913e4570738ac9c8f21` |
| `include/hammond/RotaryTypes.h` | `b27ce4934188c24ebe557469fa5191dd7cdcd98a1c3fdbe274b0d7585e4578b4` |
| `include/hammond/RotaryMotion.h` | `7bc81331f84b7ce490bf9047114336e633f3da91a39bbfd2a13e3fd406f61d36` |
| `include/hammond/RotaryHistory.h` | `9e6930342a5c83bdcf99102aaeb0dc9b0714e85561bd8205a53155a7fca4a25b` |
| `include/hammond/RotaryPropagation.h` | `c304a1ac99eed6e6e3f80b5107d026880aeb2b5b18499af0a6a7ed3018521a4a` |
| `include/hammond/RotaryRenderer.h` | `5f74af0a7ca629b433fe7f3d72a44a2b39daf90fd2d64afa579aecd26f48ccd0` |
| `src/RotaryMotion.cpp` | `a3f986892078254f6dfae936bbbf1b5e1c4967882d06c13b3b28649f2273cfa1` |
| `src/RotaryHistory.cpp` | `4f3c4fbd957f7cc9131b1f4e7c6e77f69df1b7e85c9ba4073de59fe52322a0f5` |
| `src/RotaryPropagation.cpp` | `dcc36819747b8d215130c5031a955e4b00af29a114832d0bf273ca60eaaf0c2e` |
| `src/RotaryStreamingPath.cpp` | `ed79d6ce3653f52f5f9a7d43d4f5cf9743f18cc3c9458ee7734928e42dcbae50` |
| `docs/ROTARY_RENDERER_CONTRACT.md` | `52eaaeda293376abd47af3f788e3bd5967452b176cba021f23ab7bc3b1e141a9` |
| `docs/ROTARY_PROPAGATION_CONTRACT.md` | `0834909ad8ea4b2b9696f0047d739d03976da3adb4a2eb48f2b7556737bccdcc` |
| `docs/ROTARY_NUMERICAL_CONTRACT.md` | `4c060088f0718586a7c6810e5c055c652d8924db4474db770237193ab459bd63` |
| `docs/ROTARY_WAVEFORM_ACCEPTANCE.md` | `fa4288d586a2a40d803740408177f9c0a085bd4deb9ae0bdfc832e6d58b0c1aa` |

## Limits and root integration needs

This is bounded path acceptance, not complete R4 waveform rendering. It does
not execute ten seconds of every audio sample, all block partitions, waveform
history/interpolation, renderer transactions, actual allocation instrumentation,
sanitizers, host/device deadlines, R5 reconstruction policy, R6 integration, or
physical Leslie fidelity. A19/A28 own the full waveform work. No finite-difference
derivative convergence claim is added; the qualified immutable R3 result and
explicit analytic tangent extrema retain their distinct evidence.

Root should run this target in the coherent integrated build. The existing
`tests/test_*.cpp` CMake glob discovers `test_rotary_streaming_path` and its
CTest name automatically; no special profile or extra include path is needed.
Build the target before invoking `ctest --test-dir ../build
-R '^test_rotary_streaming_path$' --output-on-failure --no-tests=error`.
Root owns any CI/sanitizer selection, shared records and publication. Preserve
the source-specific report when accepting this worker and retain the separate
full R4, R5, R6 and physical gates.
