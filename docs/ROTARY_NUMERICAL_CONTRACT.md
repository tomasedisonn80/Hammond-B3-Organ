# Rotary motion and propagation numerical contract

**Contract:** `rotary-numerics-v1`, declared 13 November 2026 before production
rotary code is graded. **Model:** `nominal-effective-mouth-rotary-v1`.
This specifies admission, behavior and experiments; it reports no executed
runtime or hardware pass. Limits below are project engineering choices, not
factory values or tolerances inferred from figures. A changed model, domain,
kernel, budget or alignment convention creates a new identified experiment.
Preserve earlier results, including failures.

The source basis is the unchanged [atlas](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf),
pp. 289-294, 301-324, 343-348, 449, 466-467 and 481-486, SHA-256
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
[ROTARY_SCOPE.md](ROTARY_SCOPE.md) defines the independent M7 boundary.
[RotaryTypes.h](../include/hammond/RotaryTypes.h) supplies common data types in
`hammond::rotary`; it does not extend existing Engine parameters, musical state,
VST3 identities or `hammond::Status`.

## 1. Separate claims and signal ownership

| Gate | Claim permitted after retained evidence passes |
| --- | --- |
| R1: admission | The proposed profile, provenance and SI projection satisfy structural and full-orbit constraints. |
| R2: motion | Continuous first-order motion and events match an independent high-precision reference. |
| R3: propagation | The finite solver finds the retarded direct point path and retains its residual. |
| R4: discrete rendering | History and cubic interpolation implement the specified signal, timing, gain and transaction contracts. |
| R5: audible policy | A separately identified reconstruction/filter/rate policy meets frozen static and dynamic spectral requirements. R4 alone does not pass R5. |
| R6: runtime/integration | Actual allocation, bounded-work, lifecycle and integration checks support their named interfaces and workloads. |
| Physical M7 | Identified cabinet/capture evidence and held-out comparisons support a specimen-specific claim. No R1-R6 pass implies this. |

Inputs are separate **double-precision normalized research waveforms** at the
horn's effective radiation point and drum's effective outlet. They are not
calibrated pascals or electrical outputs. Each reaches both microphones; the
balancing horn is not another feed. Signed paths add in Horn-then-Drum order.
Directivity and microphone response are named unity/omnidirectional diagnostics.
The only amplitude law is `reference_distance_m/distance_m`, using one fixed
profile reference distance. No automatic distance normalization, squared pressure
attenuation, stereo panner or extra pitch LFO is included. Crossover, driver,
horn transit, cabinet, room and directional filters are excluded and require
explicit ownership before later connection. M5/M6 and integrated fitting remain
separate dependencies.

## 2. Coordinates and admission

The right-handed frame has +x to the right when facing the cabinet front,
+y toward its rear and +z upward. Mouths move in their local horizontal plane.
Angle zero points along +x; positive angle is counterclockwise viewed from +z
toward the origin. Direction is a separate fixed sign. Mics are stationary
positions, independent of the visual camera. Every number must be finite.
Authoring quantities retain units, proposed evidence, applicable synthetic
variant, source pages and the reason measured uncertainty is missing.

| Quantity | Admitted domain |
| --- | --- |
| Audio rates | Exactly 44,100, 48,000, 96,000 or 192,000 samples/s |
| Each origin/mic coordinate | -10 to +10 m inclusive |
| Radius | 0 to 1 m; zero is a stationary-point diagnostic |
| Sound speed | 300 to 380 m/s |
| Reference distance | 0.02 to 10 m |
| Speed magnitudes | `0 <= slow <= fast <= 200` rad/s; initial independently in 0 to 200 rad/s |
| Up/down time constants | 0.001 to 60 s inclusive |
| Direction/initial phase | Sign exactly -1 or +1; phase `[0,2*pi)`; initial turns zero |
| Commands | Exactly `chorale` or `tremolo` per rotor; zero-speed diagnostics do not create STOP |
| Input samples | Finite in [-1,1]; no implicit clipping |
| Call bounds | At most 4,096 frames and 1,024 events; prepare may choose a smaller positive block bound |
| Clock epoch | At most 86,400 seconds, counted with integer frames |
| History | At most 16,384 frames per prepared history |

For each of four rotor/mic pairs, with horizontal displacement radius `R` and
height difference `h`, independently calculate:

```text
r_min = hypot(R-radius,h); r_max = hypot(R+radius,h)
beta = radius*max(initial_speed,slow_speed,fast_speed)/sound_speed
```

Require `r_min >= 0.02 m`, `r_max <= 20 m` and `beta <= 0.25` for every pair.
Initial-angle-only validation is insufficient. This prevents intersection and
ensures root derivative in [0.75,1.25], finite pressure gain and bounded memory.
Maximum delay is `20/300 s`, or 12,800 frames at 192 kHz. Capacity
`ceil(Fs*r_max/c)+2+4` covers propagation, fixed latency and cubic support and
fits the hard cap. Bounds were selected before runtime outcomes, not fitted to
a cabinet. An implementation may reserve the larger cap.

## 3. Motion, startup and events

Each rotor owns one history. Continuous angle is phase in `[0,2*pi)` plus
signed integer turns. A constant-command segment is anchored at its command
frame, never the host block boundary. For elapsed physical seconds `h>=0`:

```text
w(h) = wt+(w0-wt)*exp(-h/tau)
delta_theta = sigma*[wt*h+(w0-wt)*tau*(-expm1(-h/tau))]
```

Choose upward/downward tau from the sign of `wt-w0`; equal speed means constant
motion. Near `z=h/tau=0`, use the stable remainder form
`w0*h+(wt-w0)*tau*g(z)`, where `g(z)=z^2/2-z^3/6+z^4/24-...`, or an equally
qualified method. Preserve small positive decay instead of inventing a stop
threshold. The high-precision oracle must not copy a production approximation.

Profile initial states exist at frame zero; initial commands select the first
positive-time targets. Before time zero, speed stays at its initial value and
angle extrapolates backward at the fixed direction. Negative waveform indices
are zero. This is a declared synthetic startup history, not an inferred prior
cabinet state. Do not extrapolate a later accelerating segment across commands.

Events select exactly one rotor, carry a command and have nondecreasing offsets
in `[0,frames]`. Ties retain input order. At boundary `k`, change future target
before sample `k` while preserving angle/speed. An unchanged command does not
reanchor. A common switch becomes two equal-offset events; v1 has no `Both`.
An offset-N event applies after that call's samples at its end boundary and is
already effective next call. A following offset-zero event comes after it.
Zero-frame calls may apply offset-zero commands without advancing clock or
audio history. Empty queues retain commands. Silence advances time; suspended
processing freezes it. Notes, transport and GUI clocks do not own these states.

Use integer frame differences and separate fractional offsets. Forming a large
floating sample index and subtracting its integer part loses precision near the
epoch limit. `SamplePosition` retains signed floor-index and fraction `[0,1)`;
negative positions use floor rather than truncation toward zero.

## 4. Retarded path and waveform operator

Each microphone queries the same owning trajectory at its own emission time:

```text
q(e)=origin+[a*cos(theta(e)),a*sin(theta(e)),0]
v(e)=sigma*w(e)*[-a*sin(theta(e)),a*cos(theta(e)),0]
r(e)=norm(mic-q(e)); u(e)=(mic-q(e))/r(e)
t=e+r(e)/c; frequency_ratio=1/(1-u(e).dot(v(e))/c)
```

The circular norm has a negative cosine cross term. Frequency ratio lies in
[0.8,4/3] and is a diagnostic, not an extra processor; at rest it is exactly one
mathematically. Solve delay `d=t-e` in `[r_min/c,r_max/c]` using
`G(d)=d-r(t-d)/c`. A delay residual avoids large absolute-time subtraction.
Historical queries must cross earlier command boundaries correctly.

Runtime work is capped at **48 iterations**, with finite residual
`abs(G(d)) <= 1e-11 s`. Early success is allowed. One valid strategy uses at
most 12 safeguarded Newton evaluations followed by up to 36 pure bisection
evaluations. The largest initial bracket `20/300 s` and derivative bound leave
the last evaluated midpoint comfortably below the required residual without
an extra uncounted evaluation. Alternative methods need the same evidence.
Missing history and failed residuals are reported, never silently accepted.

Fixed algorithmic latency is **two frames**, separately reported from physical
travel time. This conservative research choice is retained even when physical
clearance already supplies support. At frame `n`, write input then use
observation `t=(n-2)/Fs`. For solved emission sample position `k+mu`, v1 uses
cubic Lagrange nodes `k-1,k,k+1,k+2`:

```text
w_j(mu)=product over l in {-1,0,1,2}, l!=j of (mu-l)/(j-l)
y_path=(reference_distance/r(e))*sum_j w_j(mu)*x[k+j]
```

Every support sample must exist or be declared negative-time zero. No future
sample is invented. Integer endpoints select `x[k]`. A separately identified
linear diagnostic must use `(1-mu)*x[k]+mu*x[k+1]`. No interpolation/output
clamp or normalization is hidden. Cubic absolute weight sum reaches 1.25;
the admitted two-path bound can approach 1,250 normalized output units before
roundoff. File adapters must declare format and clipping policy.

## 5. Transactions and lifecycle

Preparation validates all profile/spec values and allocates histories, scratch
and rollback resources outside processing. Processing has bounded storage/work
and no allocation, destruction, locks, files, logging or UI calls. Profile,
geometry and capacity changes require a stopped preparation boundary; v1 claims
no smooth live microphone-edit transition.

Admit frame/timeline bounds, events/order, finite sample range and buffers before
mutation. Inputs may alias each other; outputs must not overlap each other or
inputs. Zero-frame spans may be empty. Every rejected call, including detected
mid-render numerical failure, preserves object, histories, persistent diagnostics
and caller audio exactly; report zero events consumed and return failure details.
Publish successful audio/state together. This is behavior, not a copying mandate:
bounded output scratch and an overwritten-history journal are one option.

Reset restores profile initial states and silent history. A stopped rate change
preserves current phase, turns, speed and commands, starts frame zero of a new
epoch, and rebuilds **silent** waveform history plus constant-current-speed
negative-time motion. Old acoustic tails are explicitly discarded; this is not
a transparent live transition. Invalid/allocation-failed changes preserve the
previous object. Time constants remain seconds. Musical presets do not contain
these histories; complete replay checkpoints need a separate future format.
An explicit zero-input flush of `ceil(Fs*r_max/c)+2+2` frames covers the tail
and cubic support while motion continues.

## 6. Frozen experiments and budgets

Comparisons preserve absolute phase/time/gain/polarity: no fitted alignment,
rescaling or frequency remapping. Report maximum/RMS errors, worst coordinates,
source/profile/reference identities, exclusions and every failure.

### R2: motion

Use at least 80 decimal digits independently. Cover both signs; taus
`{0.001,0.01,0.1,1,10,60}` s; rest, acceleration, equal speed and decay; and
`h/tau=0` plus powers of ten from `1e-12` through `1e2`. Separately cover the
86,400-second limit, wraps and reversals. Speed budget is
`5e-12+4e-14*abs(reference_speed)` rad/s; angle-increment budget is
`5e-12+4e-15*abs(reference_increment)` rad. Cancellation/long-decay probes with
an exactly observable near-zero result must also meet relative error `2e-12`,
with absolute allowance `1e-300` for subnormal-scale cases. The ordinary floor
must not allow a small positive trajectory to become zero.

Run at least 1,000 deterministic split-interval cases with recorded seed and
total time <=60 s: semigroup budgets are `2e-10 rad` and `2e-11 rad/s`.
Compare continuous or circular angle with turns accounted for; an epsilon-near-
wrap representation need not share a higher-precision oracle's raw turn integer.
Identical event streams across block partitions on the same executable require
identical sample states.

### R3: geometry and roots

Use a separately implemented Cartesian norm and offline bracketed solver with
up to 96 bisections and residual <=`1e-14 s`. Include radii `{0,0.02,0.18,1}` m,
both signs, phase extrema, microphones above/on either side of the plane,
clearance limits, sound speeds `{300,343,380}` and valid zero/Mach-limit speeds.
Reject full-orbit collisions and invalid cross-field combinations.

On identical trajectory inputs, require distance agreement <=`2e-12 m`,
runtime residual <=`1e-11 s`, delay difference <=`2e-11 s` and diagnostic
frequency-ratio difference <=`2e-10`. For independently computed motion plus
path, also report motion phase error and its root contribution bound
`radius*abs(phase_error)/(c*(1-beta))`; do not call motion error solver error.
Check roots on both sides of commands and distinct receiver emission times.
Finite-difference derivative checks must show stencil/root-precision convergence.

### R4: interpolation and rendering

Test integer endpoints; all fractions `j/256`, `j=0..256` (the final value is
the next integer endpoint); and independent degree-zero through degree-three
polynomials. For fixtures with four support samples bounded by one, error
against the specified cubic expression must be <=`2e-12`. Test signed indices,
ring wrap, oldest history, all four support samples and unavailable queries.

Retain static complex ideal-delay error on fractions `j/64`, `j=0..64`, and
frequencies `k/1024` cycles/sample, `k=0..511`. The low-band diagnostic budget
for `f<=0.1*Fs` is complex error <=`0.005`. The remaining complete grid is
required characterization, including failures, not a broadband pass.

Compare native processing with an independent **same-cubic** reference at all
four rates, using separate impulses, bounded deterministic signals, nonzero
history and commands for at least ten seconds. Let
`G=sum_rotors(reference_distance/r_min)` for the output channel. Require
`max(abs(native-reference))/G <= 2e-5`. This conservative normalized budget
includes the root residual at 192 kHz and bounded cubic slope; retain actual
observed errors rather than only pass. It is discrete parity, not ideal-delay
or measured acoustic fidelity.

Use blocks 1, 7, 64, 257 and 4,096 plus recorded irregular partitions. Include
events before/on/after boundaries, ties, offset-N, zero frames and silence.
Same-executable audio/final physical state must be bit identical. Verify separate
inputs, coincident microphones, complete receiver swaps, signed cancellation,
and rigid scene transforms within admission bounds. Nonzero-history rejection
must preserve future accepted output exactly. Test every stopped rate pair.

### R5 and R6 remain separate

R5 needs static/moving spectra against a demonstrably converged continuous or
oversampled reference, frozen passband/stopband/alias budgets, actual filters
and their latency. The local bound `f<Fs/(2*max_ratio)` alone does not exclude
time-varying sidebands. This cubic research contract declares no alias-free
production policy; a future policy must be identified and frozen before grading.

R6 needs a calibrated allocation/deallocation probe on actual accepted/rejected
calls, bounded-capacity stress, lifecycle tests and recorded performance loads.
No allocation result is an audio-device deadline pass. Integration needs dry
compatibility, explicit controls/state/latency and actual host/device evidence.
Physical M7 separately needs identified motion/geometry acquisition, then static
and moving captures with uncertainty and held-out groups.

## 7. Next implementation gate

Implement motion, geometry/root, fractional history and renderer separately
against these types. First qualify primitives, then historical queries and
whole-call transactions, then same-cubic rendering and separate spectral work.
Retain source identities, commands and results in the
[session](development/2026-11-13-rotary/README.md). The integrator owns shared
status/next steps/log and verified publication. Worker count and absent atlas
companion results never replace these gates.
