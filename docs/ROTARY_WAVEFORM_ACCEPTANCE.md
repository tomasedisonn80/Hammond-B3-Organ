# Independent R4 waveform acceptance

**Experiment:** `rotary-r4-full-stream-v1`. **Reference implementation:**
`independent-long-double-waveform-v1` in
[rotary_waveform_reference.h](../tests/reference/rotary_waveform_reference.h).
**Contract:** [rotary-numerics-v1](ROTARY_NUMERICAL_CONTRACT.md), unchanged.

This document fixes an executable acceptance specification and supplies reusable
offline expected-value mathematics. It does **not** declare that the native R4
renderer has passed. Executed results must identify the actual native executable,
its source inputs and the report. A reference self-check cannot replace a native
comparison. The independent renderer remains separate from the dry Engine,
R5 audible reconstruction, R6 integration/deadlines and measured physical M7.

## 1. Independent calculation and precision

The header includes only C++ standard-library headers. Its data types, motion
timeline, Cartesian geometry, local-delay solver and product-form interpolation
do not include or call `RotaryMotion`, `RotaryPropagation`, `RotaryHistory`,
`PreparedStreamingPath` or `RotaryRenderer`. A test adapter may copy admitted
profile **values** and events to both implementations; it must not copy native
states, roots, distance gains, support samples read from a native ring or output
samples into the expected-value calculation.

The input parameters are explicit `double` fields. They are promoted exactly to
the implementation's `long double`, preserving the binary64 values supplied to
the native adapter. The input signal returns `double` too, and its arithmetic
uses integers and dyadic fractions. No native renderer generates a fixture.

`long double` is a portability choice, **not an 80-digit arithmetic claim**. A
report must contain `radix`, `digits`, `digits10`, `max_digits10`, `sizeof`, the
corresponding `double` values, compiler/version/options, standard library and
platform. Some platforms use the same precision for both floating types. On such
a platform the reference remains separately implemented, but no extra precision
is inferred. Compile without fast-math; record floating contraction options and
rounding mode. A changed arithmetic environment has its own result identity.

Use the existing [80-digit Python motion reference](ROTARY_REFERENCE.md) to
cross-check selected actual query positions. Its default path geometry is
binary64; do not describe that path solve as 80-digit geometry. The separately
authored `sincos`/`geometry` functions in
[test_rotary_propagation_acceptance.py](../tests/test_rotary_propagation_acceptance.py)
provide the already-reviewed 100-digit Cartesian check. No requirement is made
to run Decimal transcendental operations at every one of the millions of audio
samples. The complete audio comparison still uses the independent C++ reference.

At minimum, cross-check all four paths at all four rates for frames
`{0,7,256,4096,Fs/2,2*Fs-1,2*Fs,4*Fs,6*Fs,9*Fs,10*Fs-1}`: 176 paths. Compare
motion at the returned split emission position, and separately compare roots at
the original observation position. Retain the actual maxima and worst indices.
Use the existing R2 angle/speed absolute-plus-relative budgets, R3 distance
`2e-12 m` and ratio `2e-10` budgets, and a root difference limit of `1e-14 s`
against the independently bisected Python path with target `1e-16 s`. Failure to
qualify the reference is a failed or blocked R4 comparison, never permission to
relax a budget after seeing native results.

## 2. Reference algorithm

The immutable offline timeline retains command anchors, not process-block
anchors. Event frame numbers remain integers, and local fractional offsets are
separate. For negative time it extrapolates only the profile seed's constant
speed; negative waveform indices return zero. Equal-frame events retain input
order, unchanged commands retain their anchor, and an end-boundary event changes
the final physical state without creating a sample at that boundary.

Motion uses the analytical first-order solution. For small elapsed/tau it sums
the integrated response series until the next term no longer changes the
`long double` sum. For longer intervals it uses `exp`/`expm1` directly. It imports
no production coefficients, approximation thresholds or wrapped-state update.
The angle is an offline unwrapped value, appropriate to the ten-second workload;
this header does not replace the original 80-digit long-decay and full-epoch R2
qualification.

Geometry forms source position and velocity in Cartesian coordinates, then
calculates the square root of the sum of three squared displacements. For each
receiver and each rotor the root variable is local delay:

```text
G(d) = d - norm(mic - q(t-d))/c
H(d) = norm(mic - q(t-d))/c
```

The complete-orbit bounds bracket `G`. Roundoff widens only that initial bracket;
it does not clamp geometry or a residual. Because `abs(H'(d)) <= beta <= 1/4`,
the fast route uses a bounded fixed-point update inside the retained bracket.
It evaluates both bracket endpoints, then at most 24 contraction candidates and
at most 96 bisection candidates. Every accepted result must meet the fixed
`5e-15 s` target, which is below the independent `1e-14 s` limit. There is no
sample-to-sample warm-start state. A failure throws instead of returning an
unqualified expected value.

The `PureBisection` route disables the contraction update and permits up to 96
bisections. Compare the two routes at all four rates and four paths for frames
`{0,1,7,64,257,4096,Fs/2-1,Fs/2,Fs/2+1,2*Fs-1,2*Fs,3*Fs+17,4*Fs,6*Fs-1,6*Fs,6*Fs+1,9*Fs,10*Fs-1}`:
288 root pairs. The pure-bisection target is `1e-16 s`; the difference limit is
`2e-14 s`. Keep observed residuals, maximum evaluation counts and both targets.

For output sample `n`, observation is precisely `(n-2)/Fs`. The reference
subtracts local delay in split sample coordinates, reads all four independently
defined input values at `k-1,k,k+1,k+2`, and evaluates the defining Lagrange
product. It rejects future support. It multiplies by
`reference_distance_m/distance_m` and sums Horn then Drum for each receiver.
No output clipping, fitting, gain normalization, time shift or frequency remap
is allowed. The diagnostic frequency ratio is never applied as another effect.

### Reusable interface

| Header interface | Acceptance use |
| --- | --- |
| `Scene`, `Rotor`, `Event` | Independently owned binary64 fixture parameters and absolute integer events |
| `Timeline::at(Position)` / `command_at(frame)` | Historical motion and exact final-boundary command |
| `path_bounds` / `cartesian_geometry` | Independent full-orbit bounds and Cartesian path evidence |
| `solve_path(..., SolveMethod, target)` | Contractive/bracketed or pure-bisection offline root |
| `cubic_weights(mu)` / `cubic(values,mu)` | Product expression on nodes `{-1,0,1,2}`, including `mu=1` |
| `bounded_polynomial(degree,x)` | Analytic independent polynomial `(x/2)^degree`, degree 0 through 3 |
| `cubic_frequency_response` / `ideal_frequency_response` | Complex static characterization in cycles/sample |
| `Renderer::at(n,input)` | Four independent paths and the two expected output samples |
| `Renderer::normalization(channel)` | Fixed per-channel `G=sum(reference_distance/r_min)` |
| `full_scene`, `full_events`, `full_input` | Frozen complete ten-second workload |
| `ErrorSummary::observe` | Streamed count, maximum/RMS, normalized maximum/RMS and worst frame |

The native adapter owns conversion to `hammond::rotary` types and calls the
actual native interfaces. An adapter must use the actual renderer's reported
algorithmic latency only as a check that it is two; it cannot use a changed
reported latency to realign this reference.

The reference `Frame.paths` is channel-major (`2*channel+rotor`). Native
`RendererDiagnostics` and `path_bounds()` use rotor-major (`2*rotor+channel`).
Map explicitly when comparing diagnostic paths:

| Physical path | Reference index | Native index |
| --- | ---: | ---: |
| Horn to Left | 0 | 0 |
| Drum to Left | 1 | 2 |
| Horn to Right | 2 | 1 |
| Drum to Right | 3 | 3 |

## 3. Frozen primitive and complete static grids

| Experiment | Required complete set | Acceptance |
| --- | --- | --- |
| Polynomial reproduction | Four degrees, every `mu=j/256`, `j=0..256`; 1,028 points | Native error against both independent product expression and analytic polynomial `<=2e-12` |
| Integer endpoint | `mu=0` and `mu=1` with independent support tuples, including signed values and impulses at each of four nodes | Exact selected sample where representable; report all four support-node behavior |
| Additional bounded support | Mixed-sign tuples, alternating `{-1,1,-1,1}`, node impulses and deterministic bounded tuples at all 257 fractions | Native product-expression error `<=2e-12` |
| Static complex ideal-delay grid | Every `mu=j/64`, `j=0..64`, every `f=k/1024`, `k=0..511`; 33,280 points | Retain the complete complex/error grid |
| Static low band | `k=0..102`, all 65 fractions; 6,695 points | Complex error `<=0.005` |

The native static response is measured by calling its interpolation primitive
on the real and imaginary parts of `exp(i*2*pi*f*j)` at the four nodes. The
ideal value is `exp(i*2*pi*f*mu)`. Preserve this sign convention and all complex
values. The `mu=1` row is the next integer endpoint and cannot be dropped. If a
history API canonically accepts only `[0,1)`, shift its integer position and
support correctly; the primitive or adapter still must cover that endpoint.

Retain a compact, compressed CSV or equivalent lossless table with all 33,280
rows: integer fraction/frequency indices, native real/imaginary response,
independent ideal real/imaginary response, and complex error. Save its digest and
dimensions in the JSON report. Include the worst full-band coordinate, maximum
and RMS. Values above 0.1 cycles/sample remain required characterization; the
low-band limit is not asserted as a broadband pass. A complete reference-only
grid establishes expected cubic behavior, but does not qualify native code.

Test histories independently at negative signed indices, ring wrap, the oldest
retained sample, every support node and missing/overwritten/future support.
Adversarial fractional queries near integer boundaries must retain floor
semantics. These behavior tests supplement numerical polynomial agreement.

## 4. Complete waveform fixture

The following values are synthetic engineering inputs. They do not claim
factory dimensions, speeds, time constants or calibrated pressure.

| Rotor | Origin m | Radius m | Slow / fast rad/s | Up / down tau s | Direction | Initial phase / speed |
| --- | --- | ---: | --- | --- | ---: | --- |
| Horn | `(-0.12,0.07,1.10)` | 0.18 | 4.2 / 40.5 | 0.67 / 1.10 | +1 | 0.31 rad / 7.25 rad/s |
| Drum | `(0.09,-0.05,0.35)` | 0.22 | 3.1 / 31.0 | 1.40 / 2.60 | -1 | 4.40 rad / 5.75 rad/s |

Both initial commands are Chorale. Left microphone is `(1.35,-0.80,1.25)` m;
Right is `(-1.20,-0.65,0.90)` m. Sound speed is 343 m/s and the one fixed
reference distance is 1 m. The header is the executable fixture definition;
serialize these exact binary64 values and all events in the report.

Render **every frame** `0..10*Fs-1` at each of 44,100, 48,000, 96,000 and
192,000 samples/s. This is 3,801,000 output frames, 7,602,000 output scalar
comparisons and 15,204,000 path solutions. The same ten-second stream contains
all of the following; three separate ten-second runs per rate are unnecessary.

| Input interval | Exact content and purpose |
| --- | --- |
| 0 through 2 s | Horn impulse `+1` at frame 0, Drum impulse `-1` at `Fs/2`, Horn `-0.5` at `Fs`, Drum `+0.75` at `3*Fs/2`; otherwise zero. Each isolated impulse has ample time for its own tail. |
| 2 through 9 s | Separate bounded Horn and Drum sequences, each a fixed dyadic mixture of deterministic integer-hash noise, a triangle and a square wave. Their continuous signal bound is 0.875. |
| `6*Fs` through `6*Fs+floor(Fs/8)-1` | Explicit common silence while clock, commands and motion continue; observe the nonzero-history transition and tail. |
| 9 through 10 s | Explicit common silence and complete tail, with a Horn command at 9 s; final states must show continued motion. |

Noise uses the fixed 64-bit seed `0x726f746172792d34`, the exact unsigned
`mix64` arithmetic in the header and separate Horn/Drum salts. Triangle/square
periods and every dyadic coefficient are fixed there. Input samples are bounded
without clipping, finite, independent between rotors and reproducible from
their absolute frame; no random device or platform transcendental computes them.

There are 35 ordered commands per rate. Their absolute boundaries include
`0`, `1`, `6/7/8`, `63/64/65`, `256/257/258`, `4095/4096/4097`, boundaries
around `Fs/2`, tied changes at 4 s, transitions during the bounded inputs and
silence, and two events at the final `10*Fs` boundary. Retain the full ordered
event list, not just this summary. The final two commands must be applied even
though there is no output sample at frame `10*Fs`.

For each receiver calculate `G=sum_rotors(reference_distance/r_min)` from the
complete-orbit scene. Compare actual and expected outputs at the same integer
frame; require `max(abs(native-reference))/G <=2e-5`. Record `G`, maximum/RMS
absolute error, maximum/RMS normalized error, the actual/reference values at
the worst frame, the exact channel/rate, and reference root residual/evaluation
maxima. Retain nonzero comparison counts for the impulse and bounded intervals
so an accidentally silent harness cannot pass through a small difference.

## 5. Block/event, transaction and lifecycle coverage

Run the complete native stream at fixed blocks **1, 7, 64, 257 and 4,096**, and
at the repeating irregular sequence
`3,1,511,7,4096,64,257,1023,2,389,11,2048,5,127`. Shorten only the final block.
Keep the absolute event stream identical. Compare every audio sample by its
binary64 bit pattern, and compare all final physical fields and commands by
their exact values/bits on the same executable. Do not compare call-local
diagnostic maxima or counters as if they were partition-invariant state.
The independent expected waveform need be computed only once per rate.

Supplement the full stream with explicit calls placing commands immediately
before, on and after block boundaries; equal-offset ties; offset-N followed by
offset-zero; zero-frame command-only calls; repeated unchanged commands; and
silence. Report consumed events and final physical state. Boundary scheduling
must be admitted by the real native API; a fixture helper cannot silently move
events to make a comparison pass.

The following remain mandatory R4 behavioral tests, using nonzero history when
the property involves retained history:

- Independent Horn-only and Drum-only routing; coincident microphones; complete
  receiver swap; signed cancellation for identical rotor trajectories/geometry;
  rigid translations and allowed rotations within the admitted scene domain.
- The exact two-frame latency and all four causal cubic support points; complete
  explicit zero-input flush and tail termination while motion continues.
- Reset to the original seed and commands with silent histories.
- Every stopped supported-rate pair, including the four identity-rate pairs
  (16 ordered pairs). Preserve current phase/turns/speed/commands, start the new
  epoch at zero, and verify deliberately discarded tails and constant-speed
  negative-time motion. Preserve the old object on invalid/failed replacement.
- Invalid bounds, event values/order, nonfinite or excessive input values,
  wrong-sized/overlapping buffers, exhausted timeline and injected late failures.
  Every rejection must preserve caller buffers, copied state, diagnostics,
  histories and exact future accepted output, consuming zero events.

Allocation/deallocation probes and bounded native capacities should accompany
their interfaces, but remain named R6 evidence. A timed offline qualification
does not establish an audio-device deadline.

## 6. Bounded execution and retained evidence

Use one native executable and one C++ process for the full workload where
possible. Do not launch a process per frame or send millions of decimal sample
records through Python. Python can orchestrate the executable, hash its inputs,
perform the selected high-precision checks and validate the compact result.

Process one rate at a time. Generate input samples from their integer indices;
keep at most one native block, its expected samples and running metrics. The
reference retains only the small command timeline. For exact partition replay,
a temporary canonical two-channel binary64 stream at 192 kHz occupies
30,720,000 bytes, the maximum for one rate. Stream each alternate partition
against it, record the complete equal-sample count and final-state comparison,
then discard this owned reproducible temporary after its compact evidence is
retained. A digest alone is provenance; direct bit comparisons supply the
claimed partition result.

Do not retain millions of successful JSON sample records. Keep all required
static-grid values, fixture/source identities, maxima/RMS/worst coordinates,
selected cross-check traces, exact counters and failures. If a waveform budget
fails at many frames, retain a lossless per-channel failed-frame bitmap (or
equivalent complete index set), its count/digest and the worst-value records;
do not silently omit failures after the first N. A two-channel failed-frame
bitmap for the longest rate needs at most 480,000 bytes. Record every failed
behavioral fixture and any setup, exception, missing-history or residual error.

The report must contain at least:

- experiment/model/contract/reference IDs and invocation;
- observed Git HEAD plus SHA-256 for **every relevant worktree source**, including
  the native headers/sources, adapter, oracle header, runner, this specification,
  numerical contract and high-precision reference; check stability after the run;
- native executable digest, compiler/build settings, precision/environment facts,
  exact fixture values, ordered events, signal seed and generated input digest;
- complete frame/path/sample counts, all block patterns, channels and durations;
- all numerical metrics and worst coordinates, budgets, native/reference residual
  maxima, evaluation maxima, selected convergence/cross-check results;
- complete static-grid artifact identity, audio/input stream digests, direct
  partition comparison counts, final physical states and behavioral results;
- wall time and resource observations, exact failure records and separate
  `pass`, `fail`, `blocked` or `not_run` status for each required group.

A reduced smoke has a different explicit name and frame count. Missing an
executable, a required rate, a grid row or a required partition fails completeness
instead of skipping. Hashing a source tree, generating this document or passing
the oracle's own checks does not establish native R4 completion. The integrator
owns the actual CMake/CTest wiring and authoritative session result.
