# Independent scanner FOH line contract

**Contract ID:** `scanner-foh-line-contract-v1`.  
**Status:** independently reviewed and accepted by A10 on 15 November 2026,
with the review corrections incorporated; ready for integrator freeze before
implementation grading. The [review record](development/2026-11-15-next-phase/notes/A10-scanner-review.md)
retains the original and reviewed hashes. This document specifies work; it
reports no native FOH acceptance result.

## 1. Deliverable and preserved boundaries

The bounded M4 phase delivers a runnable, independently qualified
`hammond::ScannerLineFoh`, an offline native probe, full stationary reports,
actual process measurements, physical-state/lifecycle/transient checks and
resource evidence. The new class advances the unchanged documentary circuit
under a first-order hold (FOH): the input varies linearly between supplied
internal-rate endpoints. It is an additive numerical realization.

| Identity or boundary | Required value or treatment |
| --- | --- |
| Physical model | `atlas-late-b3-nominal-line-v1` |
| New realization | `scaled-physical-exponential-foh-scanner-line-v1` |
| Preparation method | `scanner-augmented38-pade13-scaling-squaring-v1` |
| New probe | `scanner-line-foh-probe-v1` |
| New qualification | `scanner-foh-native-qualification-v1` |
| Existing numerical contract | `scanner-numerics-v1`, SHA-256 `3999a3a409d397401e135e8285704092bad130911468802370bf6da404d58ff9` |
| Existing implementation | Preserve `ScannerLine.h`, `ScannerLine.cpp`, the trapezoidal realization ID, its probe, tests and original reports unchanged. |
| Authoring graph | Preserve `data/scanner/atlas-late-b3-nominal-v1.json`, its admission/compiler, units and generated component values. |
| Product boundaries | Preserve the nominal dry Engine, 91 free-running sources, all 47 musical parameter identities, `B3CONTROLS4` and readers 1–3. |

The [graph](SCANNER_GRAPH.md), [physical equations](SCANNER_LINE.md),
[frozen numerical contract](SCANNER_NUMERICAL_CONTRACT.md) and
[primary-source review](research/SCANNER_PRIMARY_REVIEW.md) remain authorities.
No damping, load, component adjustment, fitted gain, polarity correction or
per-tap alignment belongs to this realization.

The [A03 feasibility experiment](development/2026-11-15-next-phase/notes/A03-atlas.md)
found stationary same-Hz success at allowed internal rates from 352,800 Hz
upward. It supplied every internal endpoint from a sinusoid. It supplied no
native, host-conversion, process, transient or rotating-output evidence.
The [original trapezoidal result](SCANNER_AC_PARITY.md) still fails the frozen
same-Hz grid at every investigated rate, including 1,536,000 Hz. Neither record
is rewritten or inherited as a pass by this implementation.

**Actual host interpolation, decimation and the complete rotating pipeline are
the next numerical phase unless separately qualified evidence already exists.**
A stationary line pass permits a stationary line claim. It does not close G5
audible policy, G6 Engine integration or physical M4. This phase introduces no
Engine route, musical controls, rotor owner or calibrated voltage mapping.

## 2. Implementation surface and public API

The implementation paths are `include/hammond/ScannerLineFoh.h` and
`src/ScannerLineFoh.cpp`; the probe path is
`tools/scanner_line_foh_probe.cpp`, target `hammond_scanner_line_foh_probe`.
Independent reference/qualification work belongs in
`tools/scanner_foh_reference.py` and `tools/qualify_scanner_foh.py`, with
separate FOH tests. Assignment of these paths and shared CMake registration
remains with the integrator. This contract does not assign workers ownership
of the old scanner files.

The new public header includes `hammond/ScannerLine.h` and reuses its
`ScannerReturnMode`, `ScannerLineState`, `ScannerLineFrame`,
`ScannerLineResponse`, dimensions, admission constants and rate predicate.
Their meaning and binary layout do not change. In namespace `hammond`, add
`kScannerLineFohRealizationId` and `kScannerLineFohPreparationId` with the
identities above, and the following additive interface:

```cpp
struct ScannerLineFohPreparation {
    double augmented_norm_one{0.0};
    std::uint32_t squarings{0};
    double normalized_residual{0.0};
    double condition_inf{0.0};
};

class ScannerLineFoh {
public:
    [[nodiscard]] Status prepare(double sample_rate) noexcept;
    [[nodiscard]] Status reconfigure_sample_rate(double sample_rate) noexcept;
    [[nodiscard]] bool prepared() const noexcept;
    [[nodiscard]] double sample_rate() const noexcept;
    [[nodiscard]] double preparation_residual() const noexcept;
    [[nodiscard]] std::array<ScannerLineFohPreparation, 2>
        preparation_diagnostics() const noexcept;
    [[nodiscard]] static std::string_view authoring_sha256() noexcept;
    [[nodiscard]] ScannerLineState state() const noexcept;
    [[nodiscard]] Status restore_state(const ScannerLineState&) noexcept;
    [[nodiscard]] Status observe(ScannerReturnMode,
                                 ScannerLineFrame& destination) const noexcept;
    [[nodiscard]] Status process_frame(double input_volts, ScannerReturnMode,
                                       ScannerLineFrame& destination) noexcept;
    [[nodiscard]] Status response(double frequency_hz, ScannerReturnMode,
                                  ScannerLineResponse& destination) const noexcept;
};
```

Preparation diagnostics are ordered `[Vibrato, Chorus]`. They describe the
38-dimensional Padé denominator solve, not the 36-dimensional frequency solve
and not a bound on exponential forward error. `preparation_residual()` is the
maximum of those two residual fields. Before preparation, the flag is false,
rate/residual/diagnostics are zero and the checkpoint is cold. No public
operator-mutation or test-fault API is added. Access is externally serialized;
there is no concurrent preparation/publication protocol in this class.

Accepted numeric internal rates are exactly
`44100, 48000, 88200, 96000, 176400, 192000, 352800, 384000, 705600, 768000,
1536000` Hz. Reports preserve all fifteen labels formed by hosts
`{44100,48000,96000}` and multipliers `{1,2,4,8,16}`, naming which of the eleven
distinct computations covers each label. Acceptance of a rate by the API is
computational admission, not same-Hz qualification or additional host support.

## 3. Coordinates, equations and exact endpoint convention

Use the existing 36 physical coordinates in their existing order:

```text
x[k-1] = V(pk)-V(r),                 k = 1..18, in volts
i[k-1] flows p(k-1) -> pk,           k = 1..18, in amperes
z = [x1..x18, Zref*i1..Zref*i18]
Zref = kScannerCurrentScaleOhms = 11180.339887498949 ohms
```

The inverse map divides the last eighteen entries by `Zref`. Public state is
always physical volts/amperes. The 38-dimensional preparation matrix below
adds two temporary input coordinates; these are not extra physical states or
retained DSP histories.

For `Dk=Rk+ + Rk-`, vibrato has `r=0`; chorus has
`r=alpha*u+beta*i1`, where `alpha=Rc/(Rc+D1)` and
`beta=Rc*D1/(Rc+D1)`. Both have `Iin=i1+(u-r)/D1` and `pk=r+xk` for `k>=1`.
The physical equations are

```text
L1 * di1/dt = (1-alpha)*u - beta*i1 - x1
Lk * dik/dt = x(k-1) - xk                              k = 2..18
Ck * dxk/dt = ik - i(k+1) - xk/D(k+1)                  k = 1..5
Ck * dxk/dt = ik - i(k+1)                              k = 6..17
C18 * dx18/dt = i18 - x18/Rt
```

For vibrato, use `alpha=beta=0`. These equations define the scaled continuous
operator `dz/dt=A*z+B*u`; they retain pre-inductor divider attachments. Outputs
are the six divider nodes `r+(p(k-1)-r)*Rk-/Dk`, followed by `p6..p18`, in
`v1..v19` order. They are signed, ground-referenced volts. The return appears
once; there is no additional chorus dry copy. Input current is positive from
the ideal voltage source into the line. Energy remains
`0.5*sum(Ck*xk*xk)+0.5*sum(Lk*ik*ik)` joules.

At step `h=1/fs`, use normalized interval time `tau in [0,1]` and
`u(tau)=u_previous+tau*(u_current-u_previous)`. Define

```text
M = [ h*A   h*B   0 ]       # dimensions 36 + 1 + 1
    [  0     0    1 ]
    [  0     0    0 ]
E = exp(M)
T          = E[0:36,0:36]
b_current  = E[0:36,37]
b_previous = E[0:36,36] - b_current
z_current  = T*z_previous + b_previous*u_previous + b_current*u_current
```

These are zero-based slices. The bottom initial augmented coordinates are
`[u_previous, u_current-u_previous]`. The unit superdiagonal is dimensionless;
neither replace it with `h` nor multiply the extracted forcing vectors by `h`
again. This exponential is the continuous linear-input interval flow, up to
numerical preparation error. It is not trapezoidal endpoint forcing, a
zero-order hold, a bilinear warp or a prewarped realization.

After computing a candidate, reconstruct observations with **the current
input endpoint**, then commit physical state, previous input, completed count
and destination together. The default cold checkpoint is at `t=-1/fs` with
zero state/input/count; supplying `u[0]` at `t=0` advances the first interval
and returns frame 1. It is neither an initial free observation nor a repeated
zero-input frame. `observe()` uses the stored previous input, returns the
existing count and advances nothing. A restored nonzero count is not an
absolute timestamp; rate schedules retain their own elapsed time.

The mode passed to `process_frame` applies to the **whole upcoming interval**,
including its previous endpoint. There is no retained hidden mode. Switching
return mode preserves capacitor differences/current coordinates but may jump
algebraic ground-referenced nodes. `observe(new_mode)` performs that endpoint
reconstruction without a step. Depth and rotor phase are absent from this API.

## 4. Bounded off-thread exponential preparation

Use fixed-size binary64 arithmetic and degree-13 diagonal Padé scaling and
squaring. The polynomial coefficients and evaluation order follow Nicholas
J. Higham, [*The Scaling and Squaring Method for the Matrix Exponential
Revisited*](https://doi.org/10.1137/04061101X), Algorithm 2.3, pp. 1185–1186
([author-hosted paper](https://eprints.maths.manchester.ac.uk/634/1/covered/MIMS_ep2006_394.pdf)).
This contract chooses a fixed degree, a conservative norm target and a fixed
work cap; it does not claim to implement the paper's complete adaptive method.

For each mode, retain `norm_one(M)` and find the smallest integer `s` in
`0..16` such that `norm_one(M)/2^s <= 0.5`, by at most sixteen halvings. If no
such integer exists, reject preparation. Form `X=M/2^s` using power-of-two
scaling. Do not shift the trace, balance coordinates, truncate small entries
or introduce an eigendecomposition. With coefficients indexed from zero:

```text
c = [64764752532480000, 32382376266240000, 7771770303897600,
     1187353796428800, 129060195264000, 10559470521600,
     670442572800, 33522128640, 1323241920,
     40840800, 960960, 16380, 182, 1]
X2 = X*X
X4 = X2*X2
X6 = X2*X4
U = X*(X6*(c13*X6 + c11*X4 + c9*X2)
       + c7*X6 + c5*X4 + c3*X2 + c1*I)
V = X6*(c12*X6 + c10*X4 + c8*X2)
    + c6*X6 + c4*X4 + c2*X2 + c0*I
Q = V-U
P = V+U
solve Q*R=P
repeat s times: R=R*R
E=R
```

Coefficient normalization by the common positive `c0` before evaluating both
polynomials is permitted and must be documented. Solve the 38 right-hand
sides through one independently row-scaled, partial-pivot LU factorization of
`Q`; do not form `inverse(A)` or invert a singular descriptor energy matrix.
Each row is scaled by its largest absolute entry. A zero/nonfinite row scale,
nonfinite arithmetic, or scaled pivot magnitude at or below
`8*numeric_limits<double>::epsilon()` rejects preparation. Apply the complete
row permutation consistently to each right-hand side.

Before squaring, report the maximum normalized infinity residual over all
38 columns on the row-scaled `Qs, Ps` system. Require finite residual
`<=1e-9`. Compute the infinity condition estimate of **that same scaled Q**
using its 38 inverse-column solves; require finite positive condition and
`condition_inf*2^-52 <=1e-4` for preparation admission. A zero residual
denominator yields zero only when its numerator is also zero. Check every
matrix product, extracted coefficient and diagnostic for finiteness.

Prepare both mode operators and diagnostics in temporary storage. Only after
both succeed may `prepare()` replace the prepared object and reset its
checkpoint. There is no fallback to trapezoidal integration, lower precision,
altered damping, a different rate or a partial topology. Exhausting a bound
or failing numerical admission returns `InvalidProfile` and preserves the
previous prepared object exactly. Reconfiguration prepares a complete
candidate and preserves the existing physical checkpoint on success.

The fixed bound is two 38-dimensional factorizations, at most 76 right-hand
side solves per topology including conditioning, and at most
`2*(6+16)=44` dense matrix multiplications. Bounds are independent of input
audio. Preparation/response are stopped operations. A small Padé solve
residual is not a guarantee about matrix-exponential forward accuracy; the
independent operator, response and process checks below are mandatory.

## 5. Admission, status precedence and atomic failure

Reuse all existing inclusive line limits: input and previous input `64 V`,
each capacitor `65536 V`, each inductor `2 A`, joint energy `1 J`, each tap
and return `131072 V`, input current `4 A`. Every real quantity must be
finite. These computational limits reject; they do not clip or describe a
measured operating range. `UINT64_MAX` remains restorable and observable.

| Operation | Validation order and result |
| --- | --- |
| `prepare(rate)` | Unsupported/nonfinite rate -> `InvalidSpec`; valid-rate preparation failure -> `InvalidProfile`; success -> `Ok`, both operators installed and cold checkpoint restored. |
| `reconfigure_sample_rate(rate)` | `NotPrepared`; then rate -> `InvalidSpec`; equal valid rate -> exact no-op `Ok`; otherwise transactional preparation, with complete checkpoint preserved. |
| `restore_state(state)` | `NotPrepared`; then all physical/input/energy bounds -> `InvalidProfile`; success replaces checkpoint only. It does not implicitly change topology, prepare coefficients or add output-state admission absent from the old state API. |
| `observe(mode,destination)` | `NotPrepared`; then mode -> `InvalidEvent`; rejected complete observation -> `InvalidBuffer`; success replaces destination only. |
| `process_frame(input,mode,destination)` | `NotPrepared`; then mode -> `InvalidEvent`; then input -> `InvalidBuffer`; then count overflow -> `TimelineOverflow`; then candidate state/observation -> `InvalidBuffer`; otherwise commit both and return `Ok`. |
| `response(f,mode,destination)` | `NotPrepared`; then mode -> `InvalidEvent`; then nonfinite frequency or outside `0<=f<fs/2` -> `InvalidSpec`; failed solve/nonfinite output/residual admission -> `InvalidBuffer`; otherwise replace destination only. |

Every rejected operation leaves the prepared flag, coefficients, diagnostics,
rate, physical checkpoint and any destination unchanged. Check logical fields
and continuation, rather than uninitialized object padding. A class copy is
an independent replay clone. Tests start with nonzero history and compare
later valid output to an untouched clone. A rejected `prepare` must not clear
an already prepared line. No call allocates a new topology inside processing.

## 6. Offline recurrence response and native probe

For unit input at the discrete endpoint, with
`d=exp(-j*2*pi*f/fs)`, the response helper solves

```text
(I-d*T)*Z = b_current + d*b_previous
```

It converts current coordinates back to amperes and reconstructs all outputs
with unit current-endpoint input. It never substitutes the continuous `A`
response for the prepared recurrence. Row-scaled residual and infinity
condition follow the existing `ScannerLineResponse` convention. Require
finite outputs and residual `<=1e-9`. Return a finite conditioning-limited
estimate as diagnostic evidence; the independent qualifier must mark that
case inconclusive unless stronger forward-error evidence is supplied.
No physical state, count or previous input changes during response evaluation.
At DC this is still a numerical solve, to be compared with exact rational DC.

The new probe retains the old probe's three operations (`response`, `sine`,
`trace`), strict decimal/Unicode argument handling, classic locale,
`max_digits10`, nearest-rounding policy, complete JSON-before-stdout behavior,
stderr failures and bounded offline allocations. It links the same freshly
built core. It identifies the new realization/probe/preparation method and
never calls a gate passed. It does not accept a replacement graph.

`response` retains 1–1024 supplied frequencies, including optional exact zero,
and their order/repetitions. `sine` exclusively uses actual `process_frame`
calls with `u[n]=amplitude*cos(2*pi*f*n/fs)`; it must not call `response()` or
use its prepared transfer as output. Preserve the whole/half-window complex
cosine/sine/constant fits, physical fit residuals, final state and actual
startup lengths specified by [the original probe contract](SCANNER_PROBE.md).

`trace` adds **only an offline fixture adapter**:
`--subdivisions m`, default 1, with `m in {1,2,4,8,16}`. `--sample-rate`
continues to mean the actual internal line rate. For each supplied knot,
generate exactly `m` consecutive endpoints

```text
u_j = u_previous + (u_knot-u_previous)*(j/m),  j=1..m
```

and call the line once at each endpoint. Emit the last frame of the group;
do not emit or process `j=0`. Force `u_m=u_knot` exactly rather than relying
on cancellation in the interpolated expression. The previous group endpoint
is used once as history, never repeated as an extra frame. Report
`input_knot_rate_hz=sample_rate_hz/m`,
`initial_endpoint_seconds=-m/sample_rate_hz`, and knot time
`knot_index/input_knot_rate_hz`. The first emitted frame is
`initial_frame+m`; frame counts always count internal intervals. With `m=1`,
the base cold clock is unchanged. With `m>1`, the initial observation belongs
to the explicitly earlier fixture endpoint, with no fitted time correction.

Keep trace input at 1–16,384 knots and at most 128 bytes per line; permit at
most 262,144 internal steps. Validate the entire bounded input, multiplication
and `initial_frame+knots*m` before processing. Serialize the initial state and
observation and every emitted endpoint's input, all nineteen taps, return,
current, energy, full physical state and count. No output interpolation or
sample-deletion claim is hidden in this adapter: it samples the requested
original fixture endpoints exactly, and contains no rotor or antialias filter.

The CLI admits at most thirteen named options, 32,768 bytes per argument,
16,777,216 total sine frames and 64 MiB of output. Defaults and all remaining
constraints of the old probe apply to this separately named executable.
Irrelevant `--subdivisions` on `response`/`sine` rejects. Output stream failures
may follow a partial OS write; the caller still owns atomic file publication.

Common FOH JSON fields are `schema_version:1`, `probe_id`, `model_id`,
`realization_id`, `preparation_method_id`, `authoring_sha256`,
`evidence_scope:"synthetic_nominal_engineering"`, `operation`,
`sample_rate_hz`, `mode`, `clock_convention`, `preparation_residual` and the
two `preparation_diagnostics` objects matching the public struct fields.
`input_reconstruction` is `piecewise_linear_between_internal_endpoints`;
trace also records its original-knot adapter and subdivision count. Complex
values remain `[real,imaginary]`. The new probe schema must never use the old
`trapezoidal_endpoint_forcing` label or claim a bilinear mapping.

For `response` and `sine`, retain the old probe's exact `clock_convention`
string. For `trace`, use
`previous_endpoint_at_minus_one_input_knot;first_emitted_knot_at_zero;frame_counts_completed_internal_intervals`,
including when `m=1`. Here one input knot spans `m` internal intervals.
The common clock label, initial-observation time, emitted knot time and frame
count must agree; the old minus-one-internal-sample label is false for `m>1`.

## 7. Independent qualification protocol

### 7.1 Reference identity and independence

Use the existing independently stamped nodal
[`scanner_ac_reference.py`](../tools/scanner_ac_reference.py) and its exact
rational DC limit unchanged for physical same-Hz comparisons. Keep the
synthetic attachment, termination and sign mutations required by
`scanner-numerics-v1`; those validate the circuit reference, not a changed
nominal fixture.

FOH discrete parity additionally needs an independent reference. Identify
it separately as `scanner-full-graph-foh-reference-v1`. Derive its continuous
state/observation maps from the admitted full graph by separately stamping
resistor KCL, prescribed inductor currents and capacitor voltage constraints;
derive capacitor derivatives from solved branch currents and inductor
derivatives from branch voltages. Use named graph observation endpoints.
Sharing admitted component data is allowed. Importing native reduced `A/B`,
native coefficients, factorization, reconstruction or probe response as the
expected answer is not.

Use an independently implemented exponential evaluation rather than porting
the native Padé kernel. One implementable reference is a high-precision,
bounded Taylor exponential of the independently derived augmented generator:
fixed norm target `<=0.5`, at most sixteen scaling halvings, 64 Taylor terms,
including the identity term (`k=0..63`), then the declared squarings. Use independently scaled coordinates
`[x/1 V, i/(1e-4 A)]`. Report arithmetic precision; compare preparation at
50 and 80 decimal digits before using its result. Require coefficient
agreement `<=1e-12+1e-10*abs(reference)` in those normalized coordinates.
This is a newly declared reference-admission bound, fixed before native
grading. It is not a replacement for frozen waveform/reference refinement.

That precision comparison covers every entry of `T`, `b_previous` and
`b_current` at every reference rate used, with the 80-digit result as the
reference. When comparing different coordinate systems, let `D` be diagonal
with first eighteen entries `1` and last eighteen entries `10000/Zref`:
`T_normalized=D*T_native*inverse(D)` and `b_normalized=D*b_native`.
This is diagonal unit conversion, not a state-matrix inverse. Convert final
states back to physical volts/amperes before checking public observations.

The reference must pass independent exact DC, continuous nodal AC, physical
basis/observation, KCL and signed-output checks. If its chosen method, precision,
work cap or dependency differs, freeze that reference variant with its own
identity and review before grading; retain previous results. An independent
implementation of the exact continuous flow is useful evidence only when
its graph derivation and numerical error are themselves checked.

### 7.2 Full stationary grid and process path

Retain the frozen 282 positive frequencies, separate DC, eleven distinct
internal rates and both modes. This gives 6,204 positive native cases and
22 native DC cases, covering all fifteen host/multiplier labels. Every
positive case retains nineteen signed taps, signed return and original A/V
input admittance; dimensionless current is `15000 ohms * admittance`.

| Comparison | Required bound and channels |
| --- | --- |
| Exact rational DC | `1e-10+1e-9*abs(reference)` for all taps, return and dimensionless current. |
| New independent FOH discrete parity | `1e-8+1e-6*abs(reference)` for all taps, return and dimensionless current. This is the new realization's discrete test, not v1's bilinear warp comparison. |
| Frozen same-Hz stationary criterion | `1e-3+1e-2*abs(analog_reference)` for all nineteen taps. Retain return/current same-Hz differences as diagnostics without inventing a G5 bound for them. |
| Every numerical solve | Finite normalized residual `<=1e-9`; retain scaled condition and `condition_inf*2^-52>1e-4` flag. A flagged case is not silently passed. |

Generate the required grid literally from frozen contract section 3. Neither
the native probe's list nor the candidate's best bins define coverage.
No bilinear mapping applies: report `bilinear_kappa:null` and
`analog_frequency_mapping:"same_physical_hz"`. Keep FOH-reference and analog
same-Hz references as different comparison objects. Preserve per-channel
complex values/errors/bounds/ratios and every failure. Phase/group-delay
diagnostics retain the existing `1e-4` joint magnitude floor, excluded bins,
contiguous unwrap and physical-frequency secants; no fitted delay is allowed.

For this phase, the predeclared line-only stationary candidate labels are
**8x at all three host rates**: 352,800, 384,000 and 768,000 Hz. They require
their own observed native success. Report all other rates, including failures;
16x labels remain a separately reported cost/accuracy alternative. A failure
of a selected candidate remains a failure rather than prompting an unreported
rate change. No selected label confers host-pipeline or rotating acceptance.

Run actual processed 100, 997, 5000 and 7000 Hz cosines at all eleven rates
and both modes: 88 distinct carrier cases. Reuse the separately identified
`scanner-process-settling-refinement-v1` schedule: pre-rolls
0.125/0.25/0.5/1.0 s; measurement at least 0.125 s and eight cycles; two
successive runs with stable first/second halves and full estimates within
`1e-8+1e-6*abs(later)` channel by channel. Retain all attempts. Once settled,
compare the actual process estimate to the independent FOH reference using
the discrete bound. Comparison with `response()` is an additional consistency
check, never its independent expected answer. Unsettled at cap is inconclusive.

### 7.3 Transient and physical-state evidence

Execute all nine frozen 2400-knot, 48,000-Hz fixture families in both modes,
with the exact previous endpoint `-1/48000` and input definitions from
frozen section 5. The full suite includes both step/pulse polarities, the
five-frequency multisine, charged C1/C18 and energized L1/L18. Never reinterpret
the triangular pulse as an impulse or insert a free first frame.

The independent continuous reference uses subdivisions `8,16,32`, continuing
through `64,128` only if needed, and requires two successive passing
refinements. This may be the retained full-graph trapezoidal reference or the
independently admitted new continuous-flow reference; each result names its
actual method and hash. Preserve the old short charged-C18 inconclusive
experiment. A new reference does not retrospectively pass it.

At identical original knots, every tap and all 36 physical coordinates must
meet the unchanged reference-convergence RMS `<=2e-6` and maximum `<=1e-5`,
with volts normalized by 1 V and currents by `1e-4 A`. Reaching the cap without
two passes is inconclusive. Native-versus-converged-reference limits remain
RMS `<=1e-3` and maximum `<=1e-2` on the same fixed scales and all 55 channels.
Return/current observations remain retained diagnostics. Report per-channel
metrics and extrema locations, not only a maximum over all channels.

For the frozen transient suite, use native rates `48000*m`,
`m in {1,2,4,8,16}`, with the explicit probe fixture adapter above: ninety
native fixture/rate/mode cases. It preserves the **same 48-kHz input polygon**
at every subdivision. It does not manufacture higher-rate sinusoidal input
endpoints or prove the host interpolation policy. The remaining internal
rates receive their own basis/lifecycle/process coverage; traces with a
changed knot grid are additional experiments, not the frozen 48-kHz suite.

At all eleven rates, require each of the 36 physical basis states, both signs
and both modes for 64 frames, compared with independently assembled FOH flow
using normalized error `<=1e-8+1e-6*abs(reference)`. Cover signed observations,
algebraic return KCL and exact current orientation. This extends the frozen
three-host-rate minimum without weakening it.

Each basis fixture has exactly one coordinate set to `+1 V` or `-1 V` for a
capacitor, or `+1e-4 A` or `-1e-4 A` for an inductor; every other coordinate
and both input endpoints are zero. Also check the two independent forcing
columns through public one-frame calls from zero reactive state with
`(previous_input,current_input)=(1,0)` and `(0,1)` at every rate/mode, using
the same normalized discrete-parity bound and independent observations.
These checks admit the prepared transition and both endpoint vectors without
requiring a public coefficient accessor or a live fault-injection interface.

Run each of the four prescribed charged states for 250 ms at every supported
rate and both fixed modes, with both input endpoints zero. Per-step energy
increase is at most `1e-12*Einitial+1e-24 J`; total increase is at most
`1e-10*Einitial+1e-24 J`. Retain final energy without inventing decay-time
targets. The trapezoidal midpoint source-work identity does not apply to FOH;
any driven-energy balance needs separately integrated actual interval power.

### 7.4 Lifecycle, rollback and resources

Exercise all 121 ordered pairs among the eleven internal rates, including
same-rate no-ops, from nonzero checkpoints. Test both return transitions,
observation without advancing, input endpoint continuity, restored counters
including `UINT64_MAX`, and continuation after reconfiguration. Immediate
state preservation is exact by copying; the frozen physical tolerances
(`1e-12 V+1e-12*abs(x)`, `1e-15 A+1e-12*abs(i)`) remain the external limit.
There is no rotor phase in this class to reset or qualify.

Partition identical frame/mode sequences into `1`, `64`, `127` and repeating
`[1,17,64,3,127,2,31]`; require exact output/final-state equality. Empty batches
call no frame and advance no history. Include invalid modes/rates, NaN,
infinities, `nextafter` just outside every caller-supplied input/state bound, joint-energy
rejection, combined-error precedence and late candidate rejection. Compare
destinations and later valid frames with untouched precharged clones. Test
numeric helper failures with isolated synthetic matrices where necessary;
do not add a live runtime fault switch merely to reach a test branch.
Output and energy limits remain mandatory admission checks. A particular
output-limit rejection that is unreachable from an admitted physical state
must be identified with its algebraic bound, and can be checked on an isolated
observation validator; do not claim that a public input fixture reached it.

Persistent operators occupy exactly `2*(36*36+2*36)=2736` binary64 scalars
(21,888 bytes), plus physical checkpoint, diagnostics and scalar metadata.
Require `sizeof(ScannerLineFoh)<=24 KiB`, simultaneously live preparation
scratch `<=512 KiB`, response scratch `<=96 KiB`, process scratch `<=4 KiB`,
with actual compiler sizes and counting method retained. No heap storage is
required within the class. Any revised bound needs review before grading.

Each frame has one dense 36-by-36 matrix/vector product (1296 products),
72 forcing products, bounded conversions/admission/observation and no
input-dependent iteration. Processing must perform no allocation/deallocation,
factorization, exponentiation, locks, logging, parsing, I/O or host/UI work.
Instrument allocation with a positive control, then both modes, nonzero
histories, switches and rejection paths. Report actual zero-allocation
observations separately from a source audit.

Measure Release processing with three 0.25-s runs per distinct internal
rate/topology, retaining all 66 times, workload, CPU, compiler, flags and
maximum. Sanitizer runs are correctness evidence, not timing evidence.
Timings are descriptive and are not flaky CTest thresholds. A line-only
microbenchmark cannot establish an entire callback deadline or highest-rate
host suitability. The existing rotor's six-mode resource tests remain its
own evidence; combined line/rotor/filter costs are next-phase work.

## 8. Report admission and phase acceptance

The FOH qualifier uses `schema_version:1` and
`qualification_id:"scanner-foh-native-qualification-v1"`. A report must retain
the following independently checkable fields; nested names are normative:

| Field | Required contents |
| --- | --- |
| `contracts` | IDs and SHA-256 for this reviewed contract, unchanged `scanner-numerics-v1`, reference and settling protocols. |
| `identities` | Model/realization/preparation/reference IDs; authoring file and compiled authoring hashes; generated-header hash; all relevant source/test/tool hashes; native executable hash; coherent commit/tree or explicit source-manifest identity; build receipt. |
| `environment` | OS/CPU, compiler/version, CMake configuration and flags, binary64 properties, estimator/reference precision and any offline dependencies with versions. |
| `selection` | Complete requested host/multiplier labels, distinct internal rates, modes, full frequency list, fixture names, subdivisions, process schedule, selected stationary candidate labels and explicit `full_grid`/`full_transient_suite` booleans. |
| `conventions` | Input reconstruction, physical coordinate/current scaling, output signs/units, prior endpoint, frame/time convention, `bilinear_kappa:null`, phase origin and latency/filter fields explicitly `not_applicable_line_only`. |
| `preparation` | Both mode diagnostics for every distinct rate, with matrix dimensions, row scaling, norm/squaring count, residual/condition and actual admission. |
| `stationary_cases` | One keyed rate/mode group with separate DC and all 282 bins; native, independent FOH and same-Hz analog values; channel errors/bounds/ratios/status; each numerical solve's residual/condition, scaling and precision; exact rational DC marked as such rather than assigned a fabricated solve residual; every excluded phase/group-delay bin and reason. |
| `process_cases` | All 88 required keys in a complete run, every actual startup attempt and half estimate, convergence decision, actual process-versus-independent-reference values, residuals and final checkpoint. |
| `transient_cases` | Every required fixture/mode/rate key, exact inputs/initial state or content-addressed trace, performed reference refinement pairs, per-channel metrics/extrema, convergence and native comparison status. |
| `lifecycle`, `resources` | Actual coverage and check results; rejected-call continuation evidence; allocation positive control/counters; size/scratch/work counts; all Release timing observations. |
| `artifacts` | Relative names, byte lengths and SHA-256 of any child report/trace/log needed to reproduce the aggregate. Missing, malformed or mismatched children invalidate admission. |
| `summary` | Separate statuses for `foh_discrete_parity`, `same_hz_stationary_by_rate`, `selected_stationary_candidate`, `process`, `transients`, `lifecycle`, `resources`, `bounded_phase`, `G5_complete`, `G6` and `physical_M4`. |
| `source_snapshot_verified_unchanged` | True only after rechecking source/data/reference/probe/executable identities at the end. |

Statuses are exactly `passed`, `failed`, `inconclusive`, `blocked` or
`not_run`, with explicit reasons and failed/excluded item lists. Counts are
recomputed from the actual complete case keys, not trusted producer totals.
Missing required cases cannot pass. A failed required case dominates an
otherwise passed aggregate; conditioning or unresolved convergence prevents
a pass. A diagnostic subset is visibly a subset and cannot set
`bounded_phase:"passed"`. Valid lower-rate same-Hz failures remain visible
even when the separately selected line-only rate labels pass.

All-rate DC, FOH discrete parity, actual process, transient, lifecycle and
resource gates are required for this bounded phase. Same-Hz success is
required at each of the three predeclared 8x labels; the other rate labels
retain their individual same-Hz statuses as characterization. An unselected
rate's same-Hz failure alone therefore does not fail `bounded_phase` or force
exit 1. A selected-rate failure, missing required case or any other failed
required gate does. The all-rate discrete-parity requirement is unchanged.

`G5_complete`, `G6` and `physical_M4` remain `not_run` in the line qualifier.
Their fields cannot be inferred from the selected stationary status. Report
return/current values at every bin even though the frozen G5 same-Hz bound
grades taps. All reported numbers are finite; undefined diagnostics are null
with a reason. Reject booleans masquerading as numbers, malformed complex
vectors, duplicate/missing cases, changed IDs/contracts, inconsistent metrics,
invented coverage and success flags contradicted by detailed rows.

Use bounded JSON (128 MiB per qualification document; 64 MiB per child),
atomic replacement of regular destinations after complete validation, and
source/probe alias and symlink protection. Capture native stdout without
truncating a previous report before success. A changed source/executable,
failed native invocation or malformed report is an operation/admission error,
not a numerical pass. Exit 0 means every requested in-scope acceptance gate
passed; exit 1 retains a valid report of failed/inconclusive executed gates;
exit 2 rejects invalid/untrustworthy work and preserves the previous output.
Explicitly skipped suites are `not_run` and do not imply full phase closure.

The integrator may close the bounded phase only after: the contract/reference
reviews; the native line and probe; full independent stationary and actual
process evidence; complete frozen transient/reference evidence; physical
basis, lifecycle, rollback and resource checks; report-admission mutation
tests; coherent build integration; and a retained reproduction/acceptance
record identifying those exact inputs. A valid inconclusive report is useful
work, but leaves its corresponding acceptance gate open.

## 9. Next phase and unchanged G5 requirements

A later owner prepares a genuine host/internal pipeline with persistent
interpolator/decimator histories, declared latency, padding/tails, one rotor
clock and event order. Subdividing host segments linearly preserves host-rate
input reconstruction; it is not the higher-rate endpoint experiment which
passed A03's screen. Actual conversion filters must separately meet the
frozen 20–20,000-Hz deviation `<=0.01 dB` and stopband attenuation `>=80 dB`
beginning at host Nyquist, with their transition region and state documented.

The complete rotating gate still requires five carriers
`137,997,3113,6971,19001 Hz`, all six modes and three host rates, fixed 0.25-s
pre-roll and retained 2 s, one shared phase origin and one declared global
filter latency. Its independent reference needs two successful refinements.
The unchanged waveform limits are normalized RMS `<=1e-3`, maximum `<=1e-2`;
the Hann projections at `carrier+m*rotor`, `m=-16..16`, retain complex error
`<=1e-6 V+1e-2*abs(reference)` where reference magnitude is `>=1e-4 V`.
Keep lower-level coefficients, full residual/spectrum and all exclusions.

The four tablet routes, Great/pedal association, percussion downstream,
depth-only continuity, six-mode resource behavior and complete callback
rollback require their own composed implementation. Scanner/AO-28 loading,
specimen measurements and all broader M5–M9 gates remain separate. Neither
this document nor a completed worker count supplies that evidence.
