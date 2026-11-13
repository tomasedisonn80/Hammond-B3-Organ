# Nominal scanner numerical acceptance contract

**Contract:** `scanner-numerics-v1`, declared 13 November 2026, before this
session's runtime grading. This specifies required experiments and budgets;
it reports no executed scanner pass. The [current handoff](SCANNER_HANDOFF.md)
owns results and remaining work. A change to a grid, bound, reference, input
reconstruction or alignment convention creates a new identified experiment.
Keep the old result; never turn a failure into a retrospective pass.

The model is `atlas-late-b3-nominal-line-v1`: the documentary reconstruction
of the ideal 18-inductor/18-capacitor line, 14 resistors, ideal drive, switched
return and 19 ground-referenced taps. The graph and evidence authority is
[the scanner gate](M3_REMAINING_AND_SCANNER_GATE.md), especially sections 3-6.
The unchanged [atlas](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf), pp. 157-192,
369-371 and 481-486, requires separate circuit, numerical, runtime and physical
claims. New bounds below are project engineering choices, not factory
tolerances, specimen measurements or results inherited from missing companions.

## 1. Claims and dependencies

| Gate | Claim permitted after its actual evidence passes |
| --- | --- |
| G1: graph | The named reconstructed endpoints, values, units, outputs and return states are admitted and independently reviewed. |
| G2: reference | The independently stamped nominal AC reference satisfies analytical limits, signs, loading mutations and its reported solve checks. |
| G3: discrete runtime | The bounded implementation matches the declared discrete model, physical-state semantics and warp-aware stationary reference. |
| G4: rotor | The named unloaded rotor obeys the three maps, sixteen positions, signed weighting and continuing phase contract. |
| G5: audible numerical policy | A stated internal rate, interpolation and output-filter policy meets same-hertz, transient and rotating-output budgets. |
| G6: integration | The opt-in Engine/native route preserves dry compatibility, public state, source clocks, allocation and whole-callback rollback. |
| Physical M4 | An identified specimen/load/capture comparison supports its separately declared physical claim. None of G1-G6 implies it. |

A base-rate bilinear line can pass G3 while failing G5. A research trace or
audible demonstration may disclose that distinction; it must not be labeled a
qualified full-band scanner integration. G6 remains separate work, with all
existing 45 parameter records, controls-format migrations, factory UUIDs and
legacy dry arithmetic preserved until an explicit append-only migration exists.

## 2. Common coordinates and clock convention

Use volts at `p0` relative to `g` as input `u`. Positive input current flows
from the ideal source into the line. Output `vk` is relative to `g`, never to
the moving return. Retain return voltage and input current alongside all taps.

For a physical-state realization, retain the eighteen capacitor voltages
`xk = V(pk)-V(r)` and eighteen currents `ik` oriented `p(k-1) -> pk`.
The separately derived reduction in
[review 03](development/2026-11-13-scanner/03-atlas-scanner-electronics.md)
gives, with `D1 = R1+ + R1-`,

```text
vibrato: r = 0
chorus:  r = Rc/(Rc+D1)*u + Rc*D1/(Rc+D1)*i1
Iin = i1 + (u-r)/D1
```

This is a checkable reduction of this ideal boundary, not permission to reuse
it after adding a load, parasitic or winding loss. Document any current/voltage
scaling used for numerical preparation and its inverse. Do not invert the
singular descriptor energy matrix. Prepare both return topologies off-thread;
never interpret a retained algebraic-constraint mode as a physical resonance.

For trapezoidal processing, a checkpoint describes the **previous input
endpoint**, its physical state and previous input. A frame call advances one
declared interval to the supplied current input, then reconstructs taps at
that endpoint. A cold checkpoint has zero reactive state and previous input
zero. The first frame is consequently an interval, not a free observation of
the initial state. An explicit stopped-state observation may be separate.
The report must give this endpoint time origin; no fitted one-frame correction
is allowed. Composite rotor output reads the reported phase before incrementing
that phase for the next frame.

All compared implementations use the same input reconstruction. In particular,
trapezoidal endpoint forcing and a zero-order-held drive are different
experiments. A frame count, previous input, physical states, rotor phase and
any resampler histories belong to a replay checkpoint, not ordinary saved
musical controls.

## 3. Frozen stationary grid and solve checks

The physical-frequency grid has **282 positive frequencies** and a separate
exact DC case. Generate the positive grid as the sorted set union below;
force the geometric endpoints to exactly 20 and 20000 Hz:

```python
geometric = [round(20.0 * 1000.0 ** (j / 120.0), 12) for j in range(121)]
geometric[0], geometric[-1] = 20.0, 20000.0
frequencies_hz = sorted(set(geometric) | set(range(5000, 9001, 25)))
```

Run both return states and every signed tap. The dense 5-9 kHz region surrounds
the ideal ladder's derived approximately 7.12 kHz scale; it is fixed before
viewing runtime results. Additional diagnostic bins are welcome, but retain
these required bins and do not use adaptive additions to conceal a failed bin.
Evaluate actual internal rates corresponding to host rates 44100, 48000 and
96000 Hz. Research multipliers may be selected from `{1,2,4,8,16}`, through
1536000 Hz; these are internal solver experiments, not additional host-rate
support. Report the multiplier and preserve the physical grid.

For `Az=b`, report the matrix convention, equation/unknown scaling and
infinity-norm residual

```text
rho = ||Az-b||inf / (||A||inf * ||z||inf + ||b||inf).
```

When the denominator is zero, define `rho=0` only if the numerator is also
zero; otherwise fail. Require finite `rho <= 1e-9` at every required solve.
Report `kappa_inf(A)` or a clearly identified estimate on the same scaled
matrix. Residual alone cannot establish forward accuracy. If
`kappa_inf(A) * 2^-52 > 1e-4`, flag the bin as conditioning-limited and seek
higher-precision or independently bounded evidence before claiming that bin
qualified. Do not drop it from the denominator or call a warning a pass.

Exact-rational DC uses the independently derived resistor limit, not the
finite-frequency solver at an arbitrarily small frequency. Compare finite
runtime DC gains to those answers within `1e-10 + 1e-9*abs(expected)`.
Require independent finite-frequency experiments at 1000, 5000 and 7000 Hz:
move the first six upper divider attachments after their inductors; vary `Rt`
to 7500 and 30000 ohms; and reverse one output's observation sign. Report
actual differences in taps, upstream nodes and input current. The shifted
divider may retain DC answers, but it must be distinguishable at finite
frequency. Such variants are synthetic experiments with different identities,
not admissible changes retaining the nominal fixture identity.

## 4. Discrete parity and physical-frequency quality are separate

For a bilinear runtime with declared `kappa`, digital frequency
`omega_d = 2*pi*f/fs_internal` corresponds to analog angular frequency
`Omega = kappa*tan(omega_d/2)`. With no prewarp, `kappa=2*fs_internal`.
If prewarping is used, report its angular-frequency formula and matching
frequency; one global mapping applies to every reactive branch.

**G3 warp-matched bound:** at each positive grid frequency and every tap,

```text
abs(Hruntime(f)-Horacle(Omega/(2*pi))) <= 1e-8 + 1e-6*abs(Horacle).
```

Apply the same bound to return gain. For current, compare the dimensionless
quantity `15000 ohms * Iin/u`, retaining the original ampere-per-volt result
as well. No per-tap polarity, gain, phase or latency fit is permitted. An
analytical transfer of the prepared recurrence must be supplemented by actual
frame processing at 100, 997, 5000 and 7000 Hz in both return states, with
reported startup removal/convergence and complex sinusoid estimation. A
frequency-response helper alone does not prove the process path.

Always also report `Hruntime(f)` against `Horacle(f)` at the **same physical
hertz**, including every failed bin. This reveals warping instead of correcting
it away. **G5 same-hertz engineering bound:** for all nineteen taps,

```text
abs(Hruntime(f)-Horacle(f)) <= 1e-3 + 1e-2*abs(Horacle(f)).
```

This 1% relative plus 0.001 absolute budget is a predeclared nominal engineering
target for selecting the internal-rate policy, not evidence of perceptual
equivalence. Retain both complex errors and magnitude/phase plots, including
deeply attenuated bins governed by the absolute term.

For phase and group delay, the oracle excitation is one volt and eligibility
requires both compared transfer magnitudes at least `1e-4` (-80 dB relative
to unity). Preserve excluded bins and reasons. Unwrap only contiguous eligible
segments; do not bridge a null. Compute group delay by central secants in
physical angular frequency, with one-sided differences at segment ends.
A one-bin segment has no group-delay estimate. For warp-matched reports,
use the mapped analog response as a function of **digital physical frequency**
before differentiation, rather than comparing derivatives in different
coordinates. Complex bounds are the acceptance test; phase and group delay
are retained diagnostics, without a separate loosely chosen escape tolerance.

## 5. Independent transient and physical-state experiments

The reference must be independently implemented from circuit equations;
do not reuse the runtime's stamping, prepared transition matrix, factorization
or tap reconstruction. Sharing the admitted component data is appropriate.
Document its integration method and input reconstruction. A second copy of
the native recurrence is not a converged continuous-time reference.

Use a fixed 48000 Hz knot grid, previous endpoint `t=-1/48000`, and 2400
reported knots `t=n/48000`, `n=0..2399`. The drive is linear between knots:

| Fixture | Knot values and initial physical state |
| --- | --- |
| Positive/negative step | Previous input zero; all later knots +1 V, then separately -1 V; zero initial reactive state. |
| Positive/negative pulse | Only knot 0 is +1 V, then separately -1 V; all other knots and prior input zero; zero state. This is a finite triangular pulse, not a Dirac impulse. |
| Multisine | Sum of `sin(2*pi*f*n/48000)/5` at 137, 997, 3113, 5087 and 6971 Hz; zero initial state and prior input. |
| Charged capacitor | Zero drive; `x1=+1 V`, then separately `x18=-1 V`, with all other coordinates zero. |
| Energized inductor | Zero drive; `i1=+1e-4 A`, then separately `i18=-1e-4 A`, with all other coordinates zero. |

Run both return states. Refine the independent reference at subdivisions
`8,16,32`, continuing to `64,128` only when convergence is not established.
Compare at the identical output knots. For every tap and state coordinate,
require **two successive refinements** to differ by normalized RMS at most
`2e-6` and normalized maximum error at most `1e-5`. Normalize volts by
1 V and currents by `1e-4 A`; this is a fixed scale, not each output's fitted
gain or its potentially vanishing RMS. If the cap is reached without these
bounds, report the fixture inconclusive and improve the reference independently.
Never silently use the finest available trace as truth.

Against a converged reference, **G5 transient bounds** are normalized RMS
`<=1e-3` and normalized maximum error `<=1e-2` for all taps and physical
coordinates, with the same fixed scales. Report return and input current too.
These are intentionally looser than reference convergence. A correctly
implemented coarse discrete model may fail them; retain that evidence when
choosing an internal rate. Matched-step recurrence/algebra tests can still
qualify G3 and must be labeled as such.

For physical-state G3 admission, additionally exercise all 36 coordinate
basis initializations for 64 frames at each host rate, both polarities
and return states, checking finite outputs, signs and reconstruction. Compare
an independently assembled matched-step circuit recurrence with normalized
state error `<=1e-8 + 1e-6*abs(reference)`, using the fixed voltage/current
scales above; this is discrete parity, not continuous-time accuracy.
The four charged states above also drive 250 ms zero-input
energy tests at each supported rate. Define energy in joules as
`0.5*sum(Ck*xk*xk) + 0.5*sum(Lk*ik*ik)`. With both input endpoints zero and
fixed topology, permit per-step increase only up to `1e-12*Einitial + 1e-24 J`,
and total growth above initial energy only up to `1e-10*Einitial + 1e-24 J`.
Report final energy; do not invent a measured decay-time target. A first zero
sample following a nonzero input has nonzero interval source work and is not
eligible for a zero-source-power assertion.

Return switches and stopped-rate changes preserve compatible capacitor
voltages and inductor currents, previous input and rotor angle. For immediate
state comparison require absolute error at most `1e-12 V + 1e-12*abs(x)` and
`1e-15 A + 1e-12*abs(i)`; circular phase error is at most `1e-12` turns.
Reconstruct the new algebraic return and verify its KCL; ground-referenced
node voltages can jump while capacitor differences remain continuous.
Retain switch/source work separately rather than asserting that every switched
output must be continuous. Test all ordered rate pairs among 44100, 48000 and
96000 Hz, both return transitions, and depth-only changes after precharge.

At a fixed rate and event sequence, compare samples and final state exactly
across block partitions `1`, `64`, `127`, and repeating `[1,17,64,3,127,2,31]`.
Control-only zero-frame calls advance no line, rotor, previous-input or frame
history. A rejected frame/preparation/state restore preserves the complete
previous prepared object, histories and destination; compare subsequent valid
audio to an untouched clone. Include NaN, infinities, invalid mode/rate and
values immediately outside published input/state bounds. Tests start with
nonzero history so an accidental reset cannot pass silently.

## 6. Rotor and rotating-output qualification

Use the three depth maps in the scanner gate and one phase shared by all
modes. Phase zero is terminal 1; positive phase follows the declared forward
then return traversal. The nominal speed is the atlas's `412/60` Hz, not a
specimen measurement. Retain the 15-entry printed erratum and the separate
source-review status of its sixteen-entry completion.

At every center `k/16`, `k=0..15`, and fractional positions
`(k+q)/16`, `q in {0.25,0.5,0.75}`, test each of the nine one-hot terminal
vectors, their negatives, equal-terminal +1/-1 V, and a signed unequal vector.
Also test the nearest representable phases on both sides of each center and
wrap. Compare a separately written triangular phase/weight reference within
`2e-12 V + 2e-12*abs(expected)`. Verify endpoint terminals occur once and
intermediate terminals twice per revolution. Weights are complementary and
nonnegative; signed input voltages do not become absolute magnitudes.

For chorus, use nonzero synthetic return `r=0.375 V` and unequal local taps.
Verify `sum(w*(r+z)) = r + sum(w*z)` within the same bound, with no additional
dry term. Depth changes alter observation only; neither the line nor phase
restarts. Silence, muted routes, disconnected output, stopped-rate change and
mode changes retain one advancing phase under the declared clock convention.

**G5 rotating fixtures:** use 1 V peak sinusoidal drives at 137, 997, 3113,
6971 and 19001 Hz, all six modes and all three host rates. After a fixed 0.25 s pre-roll,
retain 2 s; share one phase origin and one declared global filter latency.
Refine the independent high-rate line/rotor reference by factors of two until
two successive refinements meet the transient reference bounds, or report
inconclusive at the declared resource cap. Compare host-grid waveforms with
normalized RMS `<=1e-3` and maximum error `<=1e-2`, normalized to the 1 V drive.

Retain complex Hann-windowed projections at `fcarrier+m*frot`, `m=-16..16`,
for positive frequencies below host Nyquist. Use identical window times and
normalization; report legitimate sidebands instead of treating them as noise.
For reference coefficients of magnitude at least `1e-4 V`, require complex
coefficient error `<=1e-6 V + 1e-2*abs(reference)`. Retain lower-level coefficients
without grading relative phase. This finite projection set does not by itself
bound every possible alias. Preserve the full waveform residual and spectrum.

If oversampling/downsampling is selected, qualify its actual filter separately:
20-20000 Hz passband deviation at most 0.01 dB, stopband beginning at host
Nyquist at least 80 dB below unity, declared transition region, latency,
boundary extension and persistent filter state. A rate label or downsampling
by sample deletion is not that evidence. These are prospective G5 integration
criteria; a research-only base-rate module can leave them unrun explicitly.

## 7. Bounded work and retained evidence

Publish accepted rates, input/state bounds, frame-count limits, scratch/storage
sizes, prepared topology count and the maximum process work from fixed loop
dimensions. The callback may not parse, factor matrices, allocate/deallocate,
lock, perform I/O, log or retry without a bound. Test allocation instrumentation
with a positive control, then both return states, all six modes, precharged
states, transitions and rejection paths. A core probe does not qualify a
future host callback containing more work.

Measure Release processing separately from sanitizer/correctness runs. Use
three 0.25 s runs per rate/topology, publish all observations and the maximum,
and identify CPU, toolchain, flags and workload. Do not make wall-clock cloud
timings a flaky CTest pass/fail. A product callback deadline claim needs a
separately selected target platform, full callback workload and predeclared
deadline/headroom; this contract establishes no universal real-time percentage.

Every report retains contract ID/hash, code commit or coherent frozen-tree
identity, authoring/compiled graph hashes, reference implementation identity,
toolchain, precision, rates, `kappa`, input reconstruction, initial states,
phase origin, latency/filter conventions, all required bins/fixtures, metric,
bound and actual result. List failed and excluded items explicitly. Distinguish
passed, failed, inconclusive, blocked and not-run gates. No chart normalization,
per-tap alignment or omission may change the graded data.

Physical M4 still needs identified scanner/AO-28 revision, winding loss and
coupling, source/receiver/probe loading, calibrated voltage and clock scales,
stationary and rotating captures, uncertainty and held-out validation. The
current ideal boundary cannot establish those quantities. Broader M3, connected
AO-28, Leslie, native device/DAW, accessible UI and release gates remain governed
by [the project plan](PLAN.md) and actual current-status evidence.
