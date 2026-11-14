# Native rotary history and retarded propagation

`include/hammond/RotaryPropagation.h` and `src/RotaryPropagation.cpp` implement
bounded historical motion queries and direct point-path geometry for
`nominal-effective-mouth-rotary-v1`. The named native R2/R3 numerical workloads
pass on the identified GCC/Linux source below. These are **nominal, unmeasured
research primitives**; they produce path diagnostics and emission positions,
not delayed audio. They are compiled into the source-tree `hammond_core` target;
the repository does not install them as a public C++ SDK.

The frozen [numerical contract](ROTARY_NUMERICAL_CONTRACT.md) and
[propagation API contract](ROTARY_PROPAGATION_CONTRACT.md) retain their original
budgets and design history. [Motion](ROTARY_MOTION.md) explains the repaired R2
arithmetic. The current [scope](ROTARY_SCOPE.md) and
[session](development/2026-11-14-reference-refinement/README.md) distinguish
executed acceptance from earlier pending-design language. Atlas pp. 289–294
and 301–324 supply the model basis; [A04](development/2026-11-14-reference-refinement/notes/A04-atlas-acoustics.md)
and the [primary-source review](research/ROTARY_PRIMARY_REVIEW.md) preserve
its applicability limits. No code is inserted into Engine, and the 47 sound
parameters, state4/readers 1–3 and scanner G5 work remain separate.

## API and storage ownership

All operations are `noexcept`. Preparation validates once without allocation;
queries perform bounded work without allocation, locks, I/O or callbacks.
Callers serialize preparation and preserve the immutable backing storage.

| Interface | Responsibility |
| --- | --- |
| `MotionHistoryView::prepare(profile, epoch_initial, sample_rate, segments, through_frame)` | Borrows `std::span<const MotionSegment>` and copies admitted profile, seed, rate and inclusive coverage. |
| `MotionHistoryView::state_at(position, state)` | Selects the proper historical segment or constant-speed negative-time seed; publishes one state on success. |
| `evaluate_circular_source(origin, radius, state, direction, position, velocity)` | Evaluates the circular source at the supplied physical state. Both output vectors are staged. |
| `PreparedRetardedPath::prepare(history, origin, radius, microphone, sound_speed, reference_distance)` | Copies the small view and geometry after full-orbit admission. |
| `PreparedRetardedPath::solve(observation, result, emission)` | Solves one direct path and publishes `PathResult` and split emission position together. |

The segment objects must **outlive every view/path copy and remain stationary
and immutable**. A copied path does not depend on the lifetime of the original
view object, but still borrows its segment storage. Container reallocation,
moving the backing array, mutation or destruction violates that obligation.
The API provides no ownership transfer, growing queue or concurrent publication.
One independently owned history per rotor serves both microphones; four paths
form a two-rotor/two-receiver scene. Horn and drum do not share motion state.

Histories contain 1–4,097 segments. This is a finite offline capacity, separate
from the future 16,384-frame waveform-history cap. The first anchor is zero
with the exact epoch seed. Later anchors strictly increase through
`through_frame`; each seed equals the preceding segment's native evaluation
at that anchor, including integer turns. Direction, slow/fast target and tau
must agree with the profile and target-minus-current-speed rule. Preparation
also evaluates the last covered endpoint to catch turn overflow.

Build anchors with the qualified native helpers or `RotaryMotion::segment()`.
After ordered commands at the same frame, retain the final effective anchor;
omit unchanged segment snapshots. The view neither replays commands nor owns
the live command clock. Rounded serialized checkpoints are not a substitute
for the required native continuity. Lookup uses at most 13 binary-search
comparisons, selecting the new segment at exact anchor equality.

### Small source-tree caller

This synthetic example retains two anchors locally, solves while their storage
is alive, and returns only values. Every status is checked. The local array is
fully populated before any view is prepared and is then left unchanged.

```cpp
#include "hammond/RotaryPropagation.h"
#include <array>

using namespace hammond::rotary;

Status query_example(PathResult& result, SamplePosition& emission) noexcept {
    constexpr double rate = 48000.0;
    const MotionProfile profile{4.0, 40.0, 0.7, 1.1, 1};
    RotaryMotion rotor;
    Status status = rotor.prepare(profile, 0.25, 4.0,
                                  SpeedCommand::Chorale, rate);
    if (status != Status::Ok) return status;
    const MotionState seed = rotor.epoch_initial_state();
    std::array<MotionSegment, 2> segments{rotor.segment(), MotionSegment{}};
    status = rotor.apply_command(24000, SpeedCommand::Tremolo);
    if (status != Status::Ok) return status;
    segments[1] = rotor.segment();

    MotionHistoryView history;
    status = history.prepare(profile, seed, rate, segments, 48000);
    if (status != Status::Ok) return status;
    PreparedRetardedPath path;
    status = path.prepare(history, Vec3{0.0, 0.0, 1.0}, 0.18,
                          MicrophoneProfile{Vec3{2.0, -1.0, 1.2}}, 343.0, 1.0);
    if (status != Status::Ok) return status;
    return path.solve(SamplePosition{36000, 0.5}, result, emission);
}
```

The example was checked with an isolated C++20 syntax-only compilation;
[A30](development/2026-11-14-reference-refinement/notes/A30-rotary-docs-handoff.md)
retains the literal source and command. This check is not a runtime experiment.

## Time and query boundaries

`SamplePosition{frame,fraction}` denotes `(frame+fraction)/Fs`, with a signed
floor index and finite fraction in `[0,1)`: `{-1,0.75}` is one quarter-sample
before zero. Rates are exactly 44,100, 48,000, 96,000 and 192,000 Hz. Let
`N=86400*Fs`; both history queries and observations admit `{-N,0}` through
`{through_frame,0}`, inclusive, with `through_frame<=N`. The positive endpoint
has no nonzero fraction. Epoch bounds are checked before coverage bounds.

Negative queries use uniform motion at the epoch seed's speed and direction.
They never extend a later acceleration backward through an event. Nonnegative
queries choose the greatest anchor at or before the position. Queries beyond
coverage but within the epoch return `InsufficientHistory`; positions outside
the epoch return `TimelineOverflow`. Every **evaluated emission**, including
both bracket endpoints, must also be queryable. Thus an admitted observation
near the negative epoch boundary can still fail during solving.

Only the short local `delay*Fs` is split into integer and fractional parts and
subtracted with checked integer arithmetic and normalized borrow/carry. The
solver does not form a large floating sample index, subtract large absolute
times or convert the retained turn counter into an unwrapped double angle.
It inserts **no algorithmic latency**: R4 must supply observation `(n-2)/Fs`
when rendering output sample `n`. Reset or stopped rate replacement requires
new views/paths and the appropriate epoch seed; these classes retain no audio
tail or waveform history.

## Geometry, solver and returned units

The right-handed frame has +x toward cabinet right, +y rearward and +z upward;
angle zero is +x and positive angle is counterclockwise viewed from +z.
For radius `a`, direction `sigma` and emission state `(theta,w)`:

```text
q = origin + [a*cos(theta), a*sin(theta), 0]
v = sigma*w*[-a*sin(theta), a*cos(theta), 0]
r = norm(microphone-q); u = (microphone-q)/r
G(d) = d-r(observation-d)/c
```

Origin/microphone coordinates must be finite in `[-10,10] m`; radius is
`[0,1] m`, sound speed `[300,380] m/s`, reference distance `[0.02,10] m`.
For horizontal origin-to-receiver distance `R` and height difference `h`,
preparation checks the entire orbit:

```text
rmin = hypot(R-a,h) >= 0.02 m
rmax = hypot(R+a,h) <= 20 m
beta = a*max(epoch_seed_speed,slow_speed,fast_speed)/c <= 0.25
```

The actual epoch seed matters after a stopped rate change. Initial-angle-only
clearance cannot admit a path. `bounds()` returns these three admitted values;
its default unprepared zeros are not physical bounds. Radius zero is a
stationary-point diagnostic. The physical maximum travel time is `20/300 s`.

The solver bisects the delay bracket, widened only by
`32*ulp(max(1,rmax))` metres before division by `c`. It checks endpoint signs,
finite geometry and derivative `1-u.dot(v)/c` in `[0.75,1.25]`, allowing only
the frozen `2e-15` derivative roundoff margin. **Both endpoints and every
midpoint count toward 48 evaluations**. The internal early target is `1e-14 s`;
success always requires finite residual at most `1e-11 s`, positive delay and
emission strictly before observation. Stagnation/exhaustion without that final
acceptance fails. The selected evaluation is cached; publication adds no
uncounted evaluation or residual clamp.

`PathResult` reports delay/residual in seconds, distance in metres, emission
phase in radians, radial speed in m/s positive toward the receiver, dimensionless
`frequency_ratio=1/(1-radial_speed/c)`, `distance_gain=reference_distance/r`,
and total evaluations. The ideal admitted ratio lies in `[0.8,4/3]`.
These diagnostics add no pitch LFO or amplitude processing. Later audio takes
separate horn/drum radiation-boundary waveforms; crossover, driver, horn transit,
directivity, cabinet, room and microphone response remain explicitly excluded.

## Transactional failures

Preparation publishes metadata only after every admission and endpoint check
succeeds. Geometry stages both vectors; origin may alias either destination,
but the two destinations must differ. Solving stages every intermediate result
and leaves the prepared object, backing history and both caller destinations
unchanged on **any** failure, including after a successful first endpoint.
Failed queries do not publish partial iterations or persistent diagnostics.

| Status | Native R2/R3 use |
| --- | --- |
| `NotPrepared` | Querying an unprepared owner/view/path or preparing a path with an unprepared view. |
| `InvalidSpec` | Unsupported rate, empty/oversized segment span, invalid fraction or physical duration. |
| `InvalidProfile` | Invalid kinematics/geometry, wrong segment target/tau/direction, discontinuity or full-orbit failure. |
| `InvalidEvent` | Invalid command/backward owner mutation, nonzero first anchor, unordered anchors or anchors beyond declared coverage. |
| `InvalidBuffer` | Identical geometry-vector destinations. |
| `TimelineOverflow` | Epoch/anchor limits, checked turn overflow or checked time subtraction overflow. |
| `InsufficientHistory` | An otherwise valid positive query beyond coverage or before an individual retained segment. |
| `NumericalFailure` | Nonfinite/noncanonical arithmetic, invalid derivative/bracket, noncausal result or failed residual. |

More specific motion-helper errors propagate. `TooManyEvents`, `BlockTooLarge`
and `AllocationFailure` exist in the common vocabulary but are not emitted by
these allocation-free primitives. They do not imply that a waveform processor
already exists. [A28](development/2026-11-14-reference-refinement/notes/A28-contract-admission-audit.md)
audited the exits and added a passing regression where the first bracket
endpoint succeeds and the second requires a turn below `INT64_MIN`;
`TimelineOverflow` preserves both outputs and all retained object/history bytes.

## Retained qualification and failures

[A17](development/2026-11-14-reference-refinement/notes/A17-rotary-propagation-implementation.md)
records implementation and original author checks. The final
[A19 native report](development/2026-11-14-reference-refinement/reports/A19-r3-native.json)
passes six independent Python methods: 1,440 geometry fixtures, 4,466 native
roots, 1,728 history queries, seven rejection fixtures and 96 receiver pairs.
It uses 100-digit independent Cartesian geometry and native-history bisection
to isolate solver error, then independent 80-digit motion to measure its separate
contribution. The workload contains 124,673 requests in 46 batches through one
native process, with all four rates, startup, commands and full-day fractions.

| R3 measurement | Maximum observed | Frozen limit |
| --- | ---: | ---: |
| Identical-state geometry distance error | `2.273e-15 m` | `2e-12 m` |
| True native residual | `9.980e-15 s` | `1e-11 s` |
| Identical-motion delay error | `1.484e-14 s` | `2e-11 s` |
| Identical-motion frequency-ratio error | `4.979e-12` | `2e-10` |
| Independent oracle residual | `4.997e-15 s` | `1e-14 s` |
| Native evaluations, including endpoints | 41 | 48 |

Both offline solvers used at most 40 bisections; their counts exclude endpoints
and must not be compared directly with native total evaluations. Separate motion
phase error reached `1.419e-9 rad`, with root contribution bound
`a*abs(phase_error)/(c*(1-beta)) <= 2.600e-12 s`. Total independent-motion delay
and ratio discrepancies were `2.487e-12 s` and `4.770e-10`; the latter is a
separate reported diagnostic, not the identical-motion ratio acceptance test.
The report retains RMS values, worst coordinates and derivative-stencil
convergence. No fitted alignment or rescaling was used.

Qualified propagation SHA-256 is
`dcc36819747b8d215130c5031a955e4b00af29a114832d0bf273ca60eaaf0c2e`;
motion SHA-256 is
`a3f986892078254f6dfae936bbbf1b5e1c4967882d06c13b3b28649f2273cfa1`.
Reports identify exact headers, contracts, oracle, executable and request/output
streams. Their final-run HEAD `e4968b2` alone does not identify the additional
uncommitted source tested. Current publication is recorded in the session
checkpoint, independently of these source-specific numerical results.

Original failures remain retained: [R2's 30 plus 36 underflows](ROTARY_MOTION.md#qualified-native-r2-evidence)
were repaired and independently replayed without changing budgets. A19's
first isolated pass retained a stdout-close warning; the corrected harness
passes, while its initial wrong shared-build path and
[missing-probe rejection](development/2026-11-14-reference-refinement/reports/A19-missing-probe-check.json)
remain documented. They are setup/harness outcomes, not numerical failures.

[A27's allocation/lifetime summary](development/2026-11-14-reference-refinement/reports/A27-r3-summary.json)
records zero observed C++ allocations/deallocations during 40 preparations,
82,320 admitted queries, eight copy intervals and 856 rejections. Calibration
detected 192 allocations and 192 deallocations. The immutable arrays stayed
alive after original view/path objects were destroyed. This observes the test
thread's C++ allocation calls, not arbitrary system allocation or device deadlines.

**The complete local ASan/UBSan/LSan gate failed and is environment-blocked.**
The instrumented workload finished, then LeakSanitizer could not attach to its
thread (`errno 1`, EPERM), failed to suspend threads and aborted; PTY retry
exited 134. Leak checking remained enabled and no finding was waived. The
precise policy causing EPERM is unresolved. A hosted run permitting thread
inspection subsequently passed for the published repaired fixture below; that
does not relabel this original local process or its one-off flags as successful.

### Hosted sanitizer follow-up — 14 November 2026

[A44's primary-log audit](development/2026-11-14-reference-refinement/reports/A44-hosted-sanitizer-audit.json)
qualifies commit `26ff2fbe66a50260bd7601cbfa54c1f5d35ff3a8`, tree
`530d5fcf777003f470f64558de9e5631d31a21a4`. Its eighteen changes from parent
`f9c11a4` are documentation/records only. All A16/A19 source, oracle and frozen
contract hashes match; the hosted allocation fixture is A38's exact repaired
`022845759fe2e604ad4c8003dc0acf4e2b693d79933da86e25a0ac8e0f9f39d7` source.

| Hosted GCC 13.3 job | Primary result and covered workload |
| --- | --- |
| [Core Debug, run 43644278142 / job 132598497275](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43644278142/job/132598497275) | **137/137**, 268.61 s. Native R2, R3, repaired allocation and both independent Python acceptance gates pass; allocation CTest takes 0.57 s. |
| [Native Release, run 43644278159 / job 132598531735](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43644278159/job/132598531735) | **16/16**, 272.49 s. Includes reference layout, six-frame pending/acknowledged inspection and 901-check material acceptance. Uses dummy audio/video and SDL software surfaces. |

Both jobs retain `ASAN_OPTIONS=detect_leaks=1:halt_on_error=1`,
`UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1` and `LSAN_OPTIONS=exitcode=23`.
The core suite's pre-existing `test_standalone_midi_backend_quarantine` exception
sets `detect_leaks=0` for intentionally retained failed-close contexts; therefore
137/137 is not a claim that every core test individually enables leak detection.
All five required rotary gates and all sixteen selected native gates retain leak
checking, with no skipped or waived gate and no relaxed numerical budget.

The native job successfully checks instrumented project C++ and pinned SDL2 C
objects, ASan/UBSan archive symbols, executable link flags and loaded runtimes.
Its exact-sixteen discovery rejects missing commands, disabled tests and
sanitizer environment overrides; pending/material timeouts remain 60 seconds.
These are successful hosted workload gates, not a general proof of leak freedom.
The bounded extracts retain complete decoded-log hashes; passing core output
does not print the fixture's detailed workload JSON.

The [A43 matrix](development/2026-11-14-reference-refinement/reports/A43-hosted-fixture-closure.json)
keeps the original `2e161dc` Windows **135/136** failure and `f9c11a4`
cancellations distinct from the completed `26ff2fb` results. The unpublished
A40/A41 header (`InstrumentView.cpp` SHA-256 beginning `f323c8c2`) and changed
material fixture are outside these jobs. The concurrent
[waveform continuation](development/2026-11-14-waveform-continuation/README.md)
owns R4; no waveform, audible-policy, Engine/integration or physical gate is
closed by this sanitizer audit.

## Reproduce the native and Python gates

Run from the repository root with CMake 3.21+, a C++20 compiler and Python
3.10+. The commands below select a fresh single-configuration Linux core build;
no SDL2, RtMidi or VST3 SDK is required. Coordinate ownership before reusing any
shared build. Retained runs used GCC 14.2.0, Release without fast-math and the
sibling `../build-native` tree; the linked notes preserve their exact commands.

```sh
cmake -S . -B build-rotary -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_ENABLE_MIDI=OFF -DHAMMOND_BUILD_VST3=OFF
cmake --build build-rotary --target hammond_rotary_motion_probe test_rotary_motion \
  hammond_rotary_propagation_probe test_rotary_propagation \
  test_rotary_propagation_allocation --parallel 2
ctest --test-dir build-rotary --no-tests=error --output-on-failure \
  -R '^(test_rotary_motion|test_rotary_propagation|test_rotary_propagation_allocation|python_test_rotary_motion_acceptance|python_test_rotary_propagation_acceptance)$'
PYTHONDONTWRITEBYTECODE=1 python3 tests/test_rotary_motion_acceptance.py \
  --probe build-rotary/hammond_rotary_motion_probe --report /tmp/rotary-r2-replay.json
PYTHONDONTWRITEBYTECODE=1 python3 tests/test_rotary_propagation_acceptance.py \
  --probe build-rotary/hammond_rotary_propagation_probe --report /tmp/rotary-r3-replay.json
```

CTest supplies the two probe paths through
`HAMMOND_ROTARY_MOTION_PROBE_EXECUTABLE` and
`HAMMOND_ROTARY_PROPAGATION_PROBE_EXECUTABLE`. The Python gates fail if native
probes are unavailable; there is no skipped or Python-only substitute.
Report paths above are new replay artifacts and do not overwrite original evidence.

For a sanitizer replay, use a separate GCC/Clang build with
`HAMMOND_ENABLE_SANITIZERS=ON`, build `test_rotary_propagation_allocation`, and
run that exact CTest target with `--no-tests=error` and leak detection enabled.
[A27](development/2026-11-14-reference-refinement/notes/A27-rotary-realtime.md)
retains the direct compile flags, runtime options, diagnostics and hashes.
Preserve gradual underflow; qualify changed source, compiler options and
floating-point environments separately rather than requiring this Linux
executable's hashes.

## Next concrete phase: R4 waveform history and rendering

Use sections 4–6 of the unchanged [numerical contract](ROTARY_NUMERICAL_CONTRACT.md)
to review and implement the missing renderer boundary:

1. Own bounded streaming motion retention and separate horn/drum double waveform
   histories. The 4,097-segment immutable fixture view is not an arbitrary-duration
   event queue. Prepare capacity, scratch and rollback resources outside calls;
   waveform capacity is `ceil(Fs*rmax/c)+2+4`, within 16,384 frames.
2. Write input sample `n`, observe at `n-2`, solve all four paths, and read cubic
   nodes `k-1,k,k+1,k+2` at the solved emission fraction. Negative audio is zero;
   future support must never be invented. Apply `reference_distance/r` and add
   signed Horn-then-Drum paths without hidden clipping or normalization.
3. Admit buffers, finite `[-1,1]` inputs, block/event/timeline bounds and aliasing
   before mutation. Keep ties, offset-N and zero-frame events ordered. A failure
   at any stage must preserve state, histories, diagnostics and caller audio,
   with zero events consumed. Define reset, stopped rate replacement with silent
   history and discarded tails, and the complete zero-input flush.
4. Execute the frozen integer/fraction/polynomial and ring-support checks,
   full static delay grid, and at least ten seconds of independent same-cubic
   parity at every rate. Retain normalized error `<=2e-5`, bit-identical audio
   and state across blocks 1/7/64/257/4096 and irregular partitions, nonzero-history
   rejection, separate-input/stereo symmetry and every stopped rate pair.

R4 discrete parity is followed by a separately identified, frozen **R5 audible
filter/reconstruction/alias policy**, then **R6 runtime and Engine/host/device
integration** with actual allocation, lifecycle, controls/state/latency and
deadline evidence. R2/R3 primitives and the allocation probe do not close those
gates. Complete M5 dry-organ validation, explicit M6 electrical/driver ownership,
identified cabinet captures and the separate scanner G5 resolution retain their
own prerequisites; numerical fixture success is not physical M7 fidelity.
