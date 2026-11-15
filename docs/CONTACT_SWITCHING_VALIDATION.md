# Contact switching numerical validation v1

**Status:** predeclared independent acceptance protocol; no executed numerical pass.
Protocol ID: `contact-switching-validation-v1`, evidence class `synthetic`.
This qualifies only the bounded offline reference in
[FRACTIONAL_CONTACT_REFERENCE.md](FRACTIONAL_CONTACT_REFERENCE.md).
Basis: [atlas](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf), pp. 117–120;
[remaining M3 contract](M3_REMAINING_AND_SCANNER_GATE.md#2-m3-work-that-remains);
[A02's source review](development/2026-11-15-execution-continuation/notes/A02.md).
The atlas's proposed `1e-4` NRMSE is a later comparison target, not the reference
convergence criterion, a manufacturer specification or an achieved result.

## 1. Frozen experiment and independence

Retain input JSON bytes/hash, protocol and model IDs, every implementation/oracle
file hash, commit plus dirty-file identities, Python/platform, exact command,
timestamps and resource observations. Freeze all fixture bytes and probe indices
before viewing candidate errors; a report cannot silently substitute new inputs.
Use exact rational trajectory preparation and binary64 waveform/filter arithmetic
under the amended reference contract. No Engine, saved-state,
parameter, source-profile, build or real-time integration change is authorized.

The oracle author independently reconstructs key trajectories, crossings, source
evaluation, kernel and quadrature from the published equations. Do not import or
copy the candidate's crossing, cell-integral, filter or summation helpers, and do
not use candidate-produced edges as oracle integration boundaries. Sharing the
reviewed fixture definition and mathematical model is required; sharing their
implementation would weaken the check. Record the independent author/reviewer.

## 2. Exact signal, filter and time conventions

Use host coordinate `u=F*t`, F in `{44100,48000,96000}`, and the contract's
piecewise-linear travel with nine independent hysteretic contacts. Source
`s(u)=A*sin(2*pi*(phase+f*u/F))` runs from the common time-zero origin.
Evaluate connection histories before summing repeated source routes. The raw
signal is zero outside `[0,N)`; the terminal observation gate can create its
own jump and is not a key release. Physical and observation-gate edges stay distinct.

Freeze `H=16`, `beta=0.45`, and, for `abs(v)<H`,
`k(v)=2*beta*sinc(2*beta*v)*(.42+.5*cos(pi*v/H)+.08*cos(2*pi*v/H))`;
`k(v)=0` at/outside the endpoints, `sinc(z)=sin(pi*z)/(pi*z)`, `sinc(0)=1`.
The continuous reference is `r[n]=integral x(u)*k(n-u) du / integral k(v) dv`.
The candidate uses centered exact cell averages over `[(j-.5)/L,(j+.5)/L)`
and weights `k(r/L)/sum(k(s/L))`, at fixed L=`32,64,128,256`.
Do not substitute midpoint samples of the switched source for cell averages.

Outputs include every n from `-16` through `N+16`, inclusive: N+33 samples.
They represent physical time `n/F`; stored index zero has offset `-16/F`.
This is an offline acausal, zero-phase reference. A causal realization would
require its own latency contract; the stored-index shift is not measured latency.
Apply no fitted delay/gain, cross-correlation alignment, clipping, normalization
or tail trimming. Complete pre-ringing and release/observation tails are graded.

Independently verify kernel symmetry, finite support, positive finite normalizer,
DC gain and absolute coefficient sum. The discrete DC residual must be `<=2e-14`;
all coefficients/results must be finite. Retain both continuous and discrete
normalizers; their different quadrature definitions must not be conflated.
Report `sum(abs(w))` and the implied mathematical ideal `B*sum(abs(w))` bound;
it is not a certified floating-point sample/headroom gate. Compute exact rational
B_exact from the input products and round B upward to binary64 as specified in
the reference contract. B is not a polyphony gain control; exact-zero routing
means B_exact==0. Report observed peak separately.

## 3. Twelve frozen fixture recipes

Each row runs at all three rates with N=256; default P=400 microseconds,
R=600 microseconds, on=`.12,.22,...,.92`, off=`.04,.14,...,.84`.
Defaults: one source ID 7, A=1, f=997 Hz, phase=.137 turns; one key,
only contact 4 has gain 1. Default targets are `(0 seconds,1),(.0008 seconds,0)`.
All other gains are zero. Every key still retains all nine histories.
Serialize physical times as canonical frame/fraction pairs. These deliberately
short gestures and electrical gains are synthetic, not nominal factory timing.

| ID | Change from defaults and required discrimination |
| --- | --- |
| F00 | All gains zero: moving histories and exact zero audio, including tails. |
| F01 | f=0, phase=.25: DC pulse; plateau unity and finite-filter step/tail convention. |
| F02 | Phase=`(.25-997*.000208) mod 1`: make near a positive source peak; retain actual signed value/slope jumps. |
| F03 | Phase=`(-997*.000208) mod 1`: make near a zero crossing; small value jump does not remove the slope jump. |
| F04 | f=`.4*F`: high-frequency discretization and declared filter attenuation. |
| F05 | Key A has nine gains `1/18`; key B has only contact 4 gain `.5`, targets shifted by .0001 seconds. Both use source ID 7: ten separate audible contacts, coherent common phase. |
| F06 | Nine gains `1/9`; targets `(0,.5),(.0016,0)`: approach partial hold from below, four conducting contacts. |
| F07 | Nine gains `1/9`; targets `(0,1),(.0006,.5),(.0016,0)`: approach the same hold from above, five conducting contacts. |
| F08 | Nine gains `1/9`; targets `(0,1),(.00015,0),(.00024,1),(.00024,1),(.0012,0)`: reversal, release/repress and duplicate no-op. |
| F09 | Two keys, gains `+.5` and `-.5` on contact 4; on[4]=.5, off[4]=.375, P=`1/2048` seconds, R=`1/1024` seconds. Both start toward 1; at exact time `1/4096` seconds A receives targets 0 then 1, B receives 1 then 0; both release at .0012 seconds. Incoming threshold equality resolves before stable no-time commands; final targets differ. |
| F10 | on[4]=.5, off[4]=.375, P=`1/4096`, R=`1/2048` seconds; targets `(0,.51),(64.25/F,0)`. Threshold and target arrival fall within the same host cell at every rate: expose the incorrect clipped-endpoint interpolation root. |
| F11 | Nine gains `1/9`, P=`12/F`, R=`16/F` seconds; targets `(0,1),(256/F,0)`. Early edges create negative-time pre-ringing; held signal is truncated at N; the command at N consumes no travel time. |

The two equality durations in F09 are exact binary fractions, avoiding a
decimal-rounding substitute for the intended exact tie. In F02/F03, report the
actual phase residual rather than silently snapping a small value to zero.
F00–F09 use matched physical times/frequencies across rates except the explicitly
normalized-frequency F04; F10/F11 deliberately exercise rate-relative boundaries.
Different-rate audio is not expected to be byte-identical: filter bandwidth and
support in seconds change with F. Each rate is graded against its own oracle.

## 4. Independent edge and continuous quadrature oracle

Construct exact rational trajectory expectations from the admitted binary64
input values (`Fraction.from_float`, integer frames); solve full-velocity roots
and preserve all separate make/break events, including muted contacts. Compare
edge count, identity, direction, stable order and final contact bits exactly.
For finite coordinates, allow at most `32*ulp(max(1,abs(expected_u)))` host frames
in root conversion; this is a numeric comparison allowance, never event merging.
Verify threshold/target equality, target-clamped arrival, no-time duplicates,
empty N=0 flushes and equal thresholds on distinct contacts with short unit cases.

Independently check signed per-contact jumps `g*Delta(c)*s(t)` and
`g*Delta(c)*ds/dt(t)`; slope units are amplitude/second. Peak/zero fixtures must
preserve their different value/slope behavior. Allow value error `<=2e-12*B`
and slope error `<=2e-10*B*max(1,2*pi*f_max)`; retain gate jumps separately.

Integrate the continuous product directly with independently implemented
eight-point Gauss–Legendre quadrature. Split at every oracle-derived contact
edge in support, 0, N and `n-H,n+H`. Each resulting smooth interval is subdivided
into panels no wider than 1, then 1/2, then 1/4 host frame. Recompute the continuous
kernel normalizer independently at each refinement. Do not integrate a sampled,
interpolated or already filtered candidate output. Retain all three estimates.

Use exactly 64 deterministic distinct integer probes per nonempty fixture.
Mandatory probes: `-16,-15,-1,0,1,N-1,N,N+15,N+16`; floor and ceil of every
audible physical edge; and floor/ceil of `first_audible_edge-H` and
`last_audible_edge+H`, restricted to the returned range. Add, in order,
`-16+floor(i*(N+32)/63)` for i=0..63, then ascending remaining indices until 64.
For F00 there are no audible-edge additions. Duplicate probes count once.
If mandatory probes exceed 64, reject the fixture set instead of dropping edges.
Freeze the resulting arrays before rendering. Probe comparisons qualify these
probes; they are not an all-sample continuous-oracle claim.

## 5. Predeclared budgets and decisions

For an error vector e, report max absolute error, RMS error and reference RMS.
For B>0 normalize samples/errors by B before RMS squaring, and compute peak_B
in that normalized domain. NRMSE uses normalized RMS values only when normalized
reference RMS is at least `1e-8`. This avoids subnormal squares/floor products
underflowing. Below that floor, report absolute-only/ineligible status,
never a fabricated zero denominator or normalized pass. B=0 requires exact zero.
Every row/rate must pass separately; pooled RMS cannot hide a failed fixture.

| Gate | Frozen criterion and compared set |
| --- | --- |
| Oracle refinement | Width 1/2 versus 1/4: peak_B `<=1e-9`, eligible NRMSE `<=1e-7`, on all 64 probes. Retain width-1 differences too. |
| High-rate convergence | L128 versus L256: peak_B `<=6e-5`, eligible NRMSE `<=3e-5`, over all 289 samples. Retain L32→64 and L64→128 differences; report observed orders without assuming monotonic error. |
| Independent reference admission | L256 versus converged width-1/4 quadrature: peak_B `<=2e-5`, eligible NRMSE `<=1e-5`, on all 64 probes. Both preceding gates are necessary. |
| Output-range/tail preservation | Read the complete immutable render with `read_samples` in ranges 1,7,64,289 and an irregular split before/on/after floored edges; retain absolute time, all tails and identical edge/final-state facts. Concatenated output is identical. This range-export check does not qualify streaming convolution/filter state. |
| Mathematical isolation | Exact muted output; known constant/unswitched sine cell integrals, fractional cell clipping, symmetry, DC and complete support checks above. These do not substitute for switched fixtures. |

Pair agreement alone cannot establish correctness. Oracle failure blocks
reference admission; a numerical failure is retained as failure. A budget or
time overrun is incomplete. No threshold widening, fixture removal, probe
selection after results or private gain/delay adjustment is permitted in v1.
Repair a demonstrated implementation defect under a new code hash and rerun
affected gates while retaining the original result. A changed model, filter,
budget or fixture suite requires a separately reviewed protocol version.

## 6. Response and legacy characterization

At each L, report the mathematical filter's complex response on nu=`j/256`,
j=0..256 cycles/host frame, plus 1.5 and 2. Include the source cell-average
factor `sinc(nu/L)` when reporting the complete stationary renderer response.
Report DC error, sampled passband ripple for nu<=.30, transition response,
sampled stopband maximum for nu>=.60 and phase wherever magnitude>=1e-8.
The continuous response uses independent quadrature. These are finite-grid
characterizations, with no predeclared audio-fidelity or stopband pass claimed.
Report residual RMS/peak and unwindowed DFT residual energy of **L256 minus L128** over the full output
in bands `[0,.30]`, `(.30,.45]`, `(.45,.50]` cycles/frame, including tail energy.
Finite-window leakage is part of that diagnostic, not a physical alias estimate.

Retain a separately named `ceil-edge-same-kernel-v1` diagnostic: move each
physical edge to `ceil(u_edge)` with stable tie order, preserve source phase,
keep the same observation gate, and integrate through the same continuous
kernel on the same 64 frozen probes, at panel widths 1/2 and1/4 with the same
oracle convergence budgets. Count these evaluations in the 10 million ceiling;
reuse independently computed normalizers. Compare with the fractional continuous
reference and report actual errors without assuming success or failure. This
isolates a declared timing quantization comparison; it is not native Engine
parity or a pure alias measurement. Any unfiltered host-grid comparison must
be labeled total signal difference. Actual legacy Engine qualification requires
its own integer-command trajectory/output comparison against current source.
An atlas `1e-4` candidate grade requires an independently admitted full-window
reference; these 64-probe results alone cannot confer it.

## 7. Bounded execution, retained evidence and scientific limits

The main matrix is exactly 12 fixtures × 3 rates × 4 factors, N=256, 289 outputs.
Its convolution count is `36*289*(1025+2049+4097+8193)=159847056` products.
Reuse the complete immutable output for range reads; these are not four extra
full renders or evidence about a streaming API. Retain the contract's
per-invocation W<=20,000,000 admission.
Whole-suite ceilings: 180 million FIR products, 10 million oracle integrand
evaluations, 300 seconds elapsed, 256 MiB peak resident memory, 32 MiB retained
reports. Count response/normalizer quadrature too; stream per fixture/factor.
These are proposed limits, not measured performance. Record hardware and actual
counts/times/memory; an exceeded limit leaves a resumable incomplete record.

Retain complete output arrays, oracle probe values/refinements, edge and jump
records, all metrics/failed cells, response/DFT summaries, resource observations,
caps and source hashes in compact JSON. Test finite/strict input rejection,
N=0, capacity/overflow and output-preservation behavior under the companion
contract; rejection must not overwrite a prior artifact or emit a success report.
No new C++ build, native audio, callback deadline or platform result is implied.

The kernel is finite and is not strictly bandlimited. Converging its numerical
implementation proves neither that its bandwidth is sufficient nor that it
models a B-3 electrical load. No measured bounce, contact resistance, transformer
loading, harmonics, leakage, percussion, expression or physical keyboard fit is
established. Atlas p.119's synchronized gesture/contact/source/dry captures and
held-out evaluation remain required. Preserve the nominal dry Engine and all
existing identities; live integration needs its own reviewed acceptance.
