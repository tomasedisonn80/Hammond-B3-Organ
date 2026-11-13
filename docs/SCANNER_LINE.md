# Prepared nominal scanner line

`hammond::ScannerLine` implements the 36 energy coordinates of the admitted
`atlas-late-b3-nominal-line-v1` circuit. Its realization identifier is
`scaled-physical-trapezoidal-scanner-line-v1`. The public API is
[`ScannerLine.h`](../include/hammond/ScannerLine.h); the implementation is
[`ScannerLine.cpp`](../src/ScannerLine.cpp). Both vibrato and chorus operators
are prepared before processing. The line exports nineteen signed tap voltages,
common-return voltage, source current and stored energy.

This is a separately identified nominal circuit module. The
[graph contract](SCANNER_GRAPH.md), [primary-source comparison](research/SCANNER_PRIMARY_REVIEW.md)
and [physical-coordinate derivation](development/2026-11-13-scanner/03-atlas-scanner-electronics.md)
establish its documentary basis. Component values come from the generated
private header `hammond/generated/ScannerLineData.h`; `authoring_sha256()`
identifies the fixture bytes used to build it. The
[frozen numerical contract](SCANNER_NUMERICAL_CONTRACT.md) defines acceptance;
the [current handoff](SCANNER_HANDOFF.md) owns the actual gate results.
The implementation's [producer evidence](development/2026-11-13-scanner/13-prepared-scanner-line.md)
does not replace those independent gates.

## Physical coordinates and algebraic reconstruction

The following mathematical indices are one-based. C++ arrays are zero-based:
`capacitor_volts[k-1]` stores `x_k`, and `inductor_amps[k-1]` stores `i_k`.

\[
x_k=V(p_k)-V(r),\qquad i_k:\ p_{k-1}\rightarrow p_k,\qquad k=1,\ldots,18.
\]

Define `u=V(p0)-V(g)`, `D_k=Rk+ + Rk-`, and

\[
\alpha=\frac{R_c}{R_c+D_1},\qquad
\beta=\frac{R_c D_1}{R_c+D_1}.
\]

With vibrato selected, `r=0`. With chorus selected, the return KCL gives
`r=alpha*u+beta*i1`. In both cases,

\[
I_{\rm in}=i_1+\frac{u-r}{D_1},\qquad p_k=r+x_k\ (k\geq1),\quad p_0=u.
\]

The state derivatives follow directly from KCL and branch voltage:

\[
L_k\dot i_k=p_{k-1}-p_k,
\]

\[
C_k\dot x_k=
\begin{cases}
i_k-i_{k+1}-x_k/D_{k+1},&1\leq k\leq5,\\
i_k-i_{k+1},&6\leq k\leq17,\\
i_{18}-x_{18}/R_t,&k=18.
\end{cases}
\]

The six divider observations are
`d_k=r+(p_(k-1)-r)*Rk-/D_k`. Consequently the nineteen ground-referenced
outputs are `d1..d6`, followed by `p6..p18`. Reconstruction includes the
common-return voltage once. The current output is positive from the ideal
voltage source into the line.

Only physical capacitor voltages and inductor currents are advanced. Return
and divider nodes are reconstructed algebraically at the observation endpoint.
There is no inverse of a singular descriptor energy matrix and no retained
alternating algebraic-constraint history. The reduction depends on this exact
ideal drive, return boundary and unloaded observation. A load, coil loss,
coupling or changed topology requires a new derivation and model identity.

## Scaling and trapezoidal preparation

Preparation expresses the current coordinates in voltage units with

\[
Z_{\rm ref}=\sqrt{0.5\ {\rm H}/(4\times10^{-9}\ {\rm F})}
\simeq11180.339887498949\ \Omega,
\qquad z=[x_1,\ldots,x_{18},Z_{\rm ref}i_1,\ldots,Z_{\rm ref}i_{18}]^T.
\]

The inverse map is `i_k=z_(18+k)/Zref`. Public checkpoints always store
physical volts and amperes; they do not store rate-dependent companion
histories or this scaled vector. Every accepted frame maps to scaled current
before the update and back to amperes before committing the result.

For each return mode the equations above yield `dz/dt=F*z+b*u`. At internal
rate `fs`, let `h=1/fs`:

\[
M=I-\frac h2 F,\qquad N=I+\frac h2 F,
\qquad T=M^{-1}N,\qquad q=M^{-1}\frac h2b.
\]

The notation denotes linear solves. Preparation factors `M` once using
row-scaled partial-pivot LU, solves its 36 transition columns and forcing
vector, checks every normalized solve residual against `1e-9`, and retains
`T` and `q`. No matrix inverse is formed as a preparation operation. Both
return modes are prepared into temporary fixed storage before either becomes
visible. `preparation_residual()` returns the largest accepted residual over
both operators. A valid-rate numerical preparation failure is `InvalidProfile`.

At an endpoint, processing performs only

\[
z_{\rm current}=Tz_{\rm previous}+q(u_{\rm current}+u_{\rm previous}).
\]

This is ordinary trapezoidal integration with both input endpoints and no
prewarp. The method is bilinear in frequency; it is not an exact continuous
solution for a linearly varying input. Its analog comparison frequency is
`fs/pi*tan(pi*f/fs)`. Same-hertz quality remains a separate acceptance question.

## Lifecycle, rates and clock

`prepare(fs)` constructs both mode operators and, on success, resets the
checkpoint to zero reactive state, zero previous input and zero completed
intervals. A failed preparation preserves the prior prepared flag, rate,
operators, residual and physical checkpoint. `reconfigure_sample_rate(fs)`
requires a prepared object and is stopped work: it prepares both new operators
while preserving every stored capacitor voltage, inductor current, previous
input and frame count exactly. An unchanged valid rate is a no-op. Neither
operation is concurrent with processing or observation.

Supported internal research rates are exactly the set produced by host rates
`44100`, `48000`, `96000` times multipliers `1`, `2`, `4`, `8`, `16`. There are
15 host/multiplier pairs and 11 distinct numeric rates. Duplicate products
remain separate experimental labels when comparing host configurations. This
set does not add host-rate support to `Engine` or any native adapter.

`frames` is a count of completed intervals, not a timestamp. The cold
checkpoint observes count 0. The first successful `process_frame` returns
count 1 and observes the endpoint **after** advancing one interval. For the
contract's constant-rate fixture, locate the cold checkpoint at `t=-1/fs`,
supply input knot `u[n]` at `t=n/fs`, and label its returned frame `n+1`.
There is no fitted one-frame delay. After a rate change, elapsed time must be
tracked from the actual rate schedule; dividing the retained count by the
new rate would reinterpret history.

`observe(mode, destination)` reconstructs the existing endpoint using the
checkpoint's `previous_input_volts`. It does not advance the count or change
physical state. A return-mode change preserves the energy coordinates and
reconstructs the return and taps for the selected boundary. The mode passed to
`process_frame` applies to the entire upcoming interval, including its
previous endpoint. The class does not retain a hidden mode or smooth a switch.
A replay therefore supplies the mode schedule in addition to the physical
checkpoint. A return switch may jump algebraic node voltages while preserving
capacitor voltage and inductor current.

## Admission bounds and transactional status

The following are explicit numerical engineering limits. They do not represent
measured Hammond operating limits, a calibrated normalized-signal conversion
or a clipping transfer function. Every inequality is inclusive.

| Quantity | Admission limit |
| --- | --- |
| Input and checkpoint previous input | finite, absolute value at most 64 V |
| Each capacitor voltage | finite, absolute value at most 65536 V |
| Each inductor current | finite, absolute value at most 2 A |
| Joint stored energy | finite, at most 1 J |
| Observed tap and return voltages | finite, absolute value at most 131072 V |
| Observed source current | finite, absolute value at most 4 A |

Energy is evaluated from the physical checkpoint as

\[
E=\tfrac12\sum_{k=1}^{18}C_kx_k^2+
  \tfrac12\sum_{k=1}^{18}L_ki_k^2.
\]

The energy bound applies jointly; satisfying each coordinate's separate bound
does not imply that a checkpoint is accepted. Limits reject the operation;
they never clamp coordinates or outputs. The admission region is not promised
to remain invariant under every bounded drive. A candidate frame exceeding a
limit is rejected before state or destination changes. A checkpoint at
`UINT64_MAX` is restorable and observable, but cannot advance.

| Condition | Status |
| --- | --- |
| Method requiring preparation called before `prepare` | `NotPrepared` |
| Unsupported/nonfinite rate or frequency outside `0 <= f < fs/2` | `InvalidSpec` |
| Invalid `ScannerReturnMode` value | `InvalidEvent` |
| Nonfinite/out-of-range input, rejected candidate frame/observation, failed offline response solve | `InvalidBuffer` |
| Invalid restored checkpoint or failed operator preparation at an admitted rate | `InvalidProfile` |
| Advancing a checkpoint with count `UINT64_MAX` | `TimelineOverflow` |
| Accepted operation | `Ok` |

Preparation is checked first for every method that requires it. Methods taking
a mode check that mode before their remaining arguments. `process_frame`
checks the input before count overflow, then validates the complete candidate
state and frame before committing either. `restore_state` validates its whole
candidate before assignment. `observe` and `response` commit their destination
only on success. No rejected call partially updates a destination or the
line's state, rate or operators.

`ScannerLineState` is a replay checkpoint with thirty-six physical coordinates,
the previous input and completed count. It is separate from saved musical
controls; no controls-format migration is introduced by this module.

## Offline response diagnostics

For a unit sinusoid with `d=exp(-j*2*pi*f/fs)`, `response()` solves the
**prepared discrete recurrence**:

\[
(I-dT)Z=q(1+d).
\]

It converts scaled currents back to amperes and uses the same public endpoint
observation equations. `taps` contains nineteen complex volt/volt transfers,
`return_gain` is return volts per input volt, and `input_admittance` is amperes
per volt. DC is accepted exactly at `f=0`; it is still a numerical recurrence
solve, to be compared with the independent exact-rational resistor limit.
Nyquist itself is excluded. The helper does not modify the checkpoint.

For its complex matrix `A`, each original row is divided by its largest
coefficient magnitude, producing `As` and `bs`. The reported residual is

\[
\rho=\frac{\|A_sZ-b_s\|_\infty}
{\|A_s\|_\infty\|Z\|_\infty+\|b_s\|_\infty}.
\]

A zero denominator is accepted only with a zero numerator. `condition_inf`
is the infinity condition of this same row-scaled matrix in the stated
current-scaled coordinates. It computes the inverse norm through 36 unit
right-hand-side solves; this diagnostic does not advance the DSP or use the
analog derivative matrix in place of the discrete recurrence. Condition and
residual use binary64 arithmetic. The helper requires finite results; the
caller applies the contract's residual and conditioning thresholds and keeps
failed or conditioning-limited bins in the report.

This analytical helper is useful for comparing every signed tap, but actual
`process_frame` experiments must independently qualify its implementation.
The contract also requires independent transient comparisons and same-hertz
error reporting. Warped agreement alone cannot select an audible-rate policy.

## Runtime and build boundary

The class uses fixed `std::array` storage and C++20 library types. One frame
uses a dense 36-by-36 matrix-vector product, bounded coordinate conversion,
admission checks and output reconstruction. It does not allocate, factor a
matrix, lock, perform I/O or loop according to user-controlled dimensions.
Preparation, rate reconfiguration and response diagnostics are stopped/offline
operations. Access to an instance must be externally serialized. A fixed cost
does not itself establish a real-time deadline at the highest research rate.

From the repository root, with CMake, Ninja, Python 3 and a C++20 compiler:

```sh
cmake -S . -B build-scanner-line -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF \
  -DCMAKE_INSTALL_DATADIR=share
cmake --build build-scanner-line --target hammond_core
```

The core target depends on `hammond_scanner_data`; generation validates the
fixture and writes its private header into the build directory. Public
consumers include only `hammond/ScannerLine.h` and link `hammond_core`.

```cpp
hammond::ScannerLine line;
if (line.prepare(48000.0) != hammond::Status::Ok) return;
hammond::ScannerLineFrame endpoint;
if (line.process_frame(1.0, hammond::ScannerReturnMode::Vibrato, endpoint)
    != hammond::Status::Ok) return;
// endpoint.frame == 1; endpoint.taps_volts contains v1..v19 after the interval.
```

This module provides no rotor, tablet routing, musical selector, interpolation,
output filter, native callback route, or measured loading/voltage scale.
Independent G3 results are prerequisites for those next numerical decisions;
G4-G6 and specimen fidelity retain their own acceptance evidence.
