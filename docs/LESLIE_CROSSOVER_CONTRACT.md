# Leslie passive crossover: frozen research contract

Contract `leslie-crossover-contract-v1` defines the next independent **M6** slice.
Its authoring registry is [leslie-122-ideal-v1.json](../data/crossover/leslie-122-ideal-v1.json).
This is a newly implemented numerical research model. It does not recover the
atlas's absent companion executable, connect cabinet audio to Engine, qualify a
complete Leslie amplifier, or supply measured driver or acoustic behavior.

## Evidence and selected network

The unchanged atlas, SHA-256
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`,
pp. 271–276, is the source actually inspected. It cites manufacturer drawings;
those drawings have **not** been independently inspected for this contract.
The selected documentary identity is the 1971 **052803** divider for Leslie 122.
The atlas's later **113860** identity is related documentary context, not an
interchangeable measured assembly or a separate admitted 147 profile.

| Element | Ordered nodes | Value in SI units | Evidence |
| --- | --- | --- | --- |
| L2 | A to H | 0.0032 H | Atlas documentary nominal, p. 271 |
| L3 | A to W | 0.0052 H | Atlas documentary nominal, p. 271 |
| C16A | H to B | 0.0000078 F | Atlas documentary nominal, pp. 271–272 |
| C16B | W to B | 0.0000125 F | Atlas documentary nominal, pp. 271–272 |
| Treble load RT | A to H | 16 ohm by default | Explicit ideal resistor fixture, p. 273 |
| Bass load RW | W to B | 16 ohm by default | Explicit ideal resistor fixture, p. 273 |

B is the mathematical reference. A–H is the **floating treble port**: grounding
H or placing its load across H–B changes the circuit. The ideal voltage source
sets `u = VA - VB`; it has zero source impedance only as a declared fixture
assumption. Winding resistance, capacitor losses, actual driver impedance,
acoustic polarity and specimen applicability remain unknown in the registry.
Their null measurements must never be read as measured zeroes.

## Physical state and port signs

Use binary64 values and the state order
`x = [vA, vB, i2, i3]`, where `vA = VH - VB`, `vB = VW - VB`,
`i2` flows A to H through L2, and `i3` flows A to W through L3. The overloaded
state labels are local capacitor labels; registry nodes retain their own names.

```text
dvA/dt = (i2 + (u - vA)/RT) / C16A
dvB/dt = (i3 - vB/RW) / C16B
di2/dt = (u - vA) / L2
di3/dt = (u - vB) / L3

VT = u - vA                  IT = VT / RT
VW = vB                      IW = VW / RW
Iin = i2 + IT + i3
E = (C16A*vA*vA + C16B*vB*vB + L2*i2*i2 + L3*i3*i3) / 2
```

Voltages are V, currents A, stored energy J and time s. `IT`/`IW` are resistor
load currents, not complete branch currents. Positive `Iin` enters the divider
from the source. Thus `dE/dt = u*Iin - VT*IT - VW*IW`. These orientations do not
assert acoustic speaker polarity. Expose both electrical load ports; introduce
no horn/drum response, propagation, room effect or artificial complementary sum.

## Numerical realization

Realization ID: `physical-trapezoidal-leslie-crossover-v1`. For `dx/dt = A*x + B*u`
and `h = 1/fs`, prepare

```text
F = solve(I - h*A/2, I + h*A/2)
G = solve(I - h*A/2, h*B/2)
x_next = F*x_previous + G*(u_next + u_previous)
```

Preparation performs any factorization. Use checked finite operators and a
normalized preparation residual at most `1e-12`. No prewarping, added damping,
oversampling or response compensation is part of v1. The input reconstruction
is the endpoint trapezoidal rule above, not an unstated zero-order hold.
The cold checkpoint is frame 0 with zero physical state and previous input 0.
Each processed sample completes one interval and reports its **right endpoint**;
the first processed sample reports frame 1. Observe and empty-block processing
advance no time. The previous input is part of the replay checkpoint.

For each linear solve `M*X=R`, the normalized residual is
`||M*X-R||inf / max(1, ||M||inf*||X||inf + ||R||inf)`, with the matrix infinity
norm equal to its largest absolute row sum (complex entries use magnitude),
and vectors using largest absolute entry. Preparation reports the maximum of
the F and G solve residuals. Response reports the same norm for its actual
recurrence solve. This is a numerical residual, not a physical-error bound.

Only 44100, 48000, 96000 and 192000 Hz are admitted. Stopped rate reconfiguration
rebuilds F/G while preserving all four physical coordinates, previous input and
completed-frame count exactly. It introduces no synthetic interval or rate-
dependent reinterpretation of stored charge/current. `prepare` starts a new
zero-state experiment; `restore_state` is an explicit research checkpoint
operation, never a musical preset restore.

## Exact native API surface

Implement `include/hammond/LeslieCrossover.h` and `src/LeslieCrossover.cpp` in
namespace `hammond`, using existing `Status` from `hammond/Types.h`:

```cpp
inline constexpr std::string_view kLeslieCrossoverModelId =
    "atlas-leslie-122-ideal-crossover-v1";
inline constexpr std::string_view kLeslieCrossoverRealizationId =
    "physical-trapezoidal-leslie-crossover-v1";
inline constexpr std::size_t kLeslieCrossoverBlockCapacity = 4096;

struct LeslieCrossoverLoads {
    double treble_ohms{16.0};
    double bass_ohms{16.0};
    bool operator==(const LeslieCrossoverLoads&) const noexcept = default;
};
struct LeslieCrossoverState {
    std::array<double, 2> capacitor_volts{}; // H-B, W-B
    std::array<double, 2> inductor_amps{};   // A->H, A->W
    double previous_input_volts{0.0};
    std::uint64_t frames{0};
    bool operator==(const LeslieCrossoverState&) const noexcept = default;
};
struct LeslieCrossoverFrame {
    double treble_volts{0.0}, bass_volts{0.0};
    double treble_current_amps{0.0}, bass_current_amps{0.0};
    double input_current_amps{0.0}, energy_joules{0.0};
    std::uint64_t frame{0};
    bool operator==(const LeslieCrossoverFrame&) const noexcept = default;
};
struct LeslieCrossoverResponse {
    std::complex<double> treble_gain{}, bass_gain{}, input_admittance{};
    double normalized_residual{0.0};
    bool operator==(const LeslieCrossoverResponse&) const noexcept = default;
};
class LeslieCrossover {
public:
    Status prepare(double sample_rate, LeslieCrossoverLoads loads = {}) noexcept;
    Status reconfigure_sample_rate(double sample_rate) noexcept;
    bool prepared() const noexcept;
    double sample_rate() const noexcept;
    LeslieCrossoverLoads loads() const noexcept;
    double preparation_residual() const noexcept;
    LeslieCrossoverState state() const noexcept;
    Status restore_state(const LeslieCrossoverState&) noexcept;
    Status observe(LeslieCrossoverFrame& destination) const noexcept;
    Status process_frame(double input_volts, LeslieCrossoverFrame& destination) noexcept;
    Status process(std::span<const double> input_volts,
                   std::span<LeslieCrossoverFrame> destination) noexcept;
    Status response(double frequency_hz,
                    LeslieCrossoverResponse& destination) const noexcept;
};
```

These declarations specify the surface; the builder supplies private fixed
storage and `[[nodiscard]]` annotations. Do not introduce a PIMPL, host SDK,
external library, live JSON loading or audio callback connection.

### Admission, ownership and transactions

- Access is externally serialized. Prepare, rate changes, restore and response
  run stopped/offline. Caller spans stay valid and immutable throughout calls.
- L/C values are fixed by this model identity. Both loads must be finite in
  `[1, 1024]` ohm; alternatives are explicit resistor experiments, never driver
  measurements. A load change requires fresh `prepare` and resets history.
- `response` accepts finite `0 <= frequency_hz < sample_rate/2`, solves the
  **actual prepared recurrence** for a unit-volt endpoint sinusoid and changes
  no history. Its gains are complex V/V and admittance is complex A/V. DC uses
  the continuous limits of this same recurrence, not a singular `1/(s*C)` call.
- Computational bounds, **not device ratings or clipping thresholds**, are:
  `abs(input) <= 64 V`, each capacitor `<= 65536 V` in absolute value, each
  inductor `<= 256 A` in absolute value, and stored energy `<= 1e6 J`.
  Every admitted checkpoint includes a finite bounded previous input. All
  emitted port values and computed states must remain finite; an experiment
  reaching a computational boundary rejects without clipping.
- A method requiring preparation returns `NotPrepared` first. Invalid rates,
  loads or offline response frequencies return `InvalidSpec`; invalid restore
  returns `InvalidProfile`; invalid input/buffer/alias or failed finite/bounds
  admission during processing returns `InvalidBuffer`. A block over 4096 returns
  `BlockTooLarge`; insufficient uint64 frame capacity returns `TimelineOverflow`.
- Input and destination counts must agree. Empty spans succeed without changing
  any byte of state. Nonempty spans must not overlap in bytes; reject overlap
  before mutation. No out-of-range pointer arithmetic is allowed in admission.
- Block rejection precedence is: `NotPrepared`, unequal counts (`InvalidBuffer`),
  input count over capacity (`BlockTooLarge`), frame-counter overflow
  (`TimelineOverflow`), byte overlap (`InvalidBuffer`), then per-sample finite/
  computational admission (`InvalidBuffer`). A scalar frame checks preparation,
  frame overflow, then input/state admission in that order. Empty equal spans
  succeed even at the maximum frame count and do not examine storage.
- Every failing operation preserves all prior state/operators/configuration and
  caller destination values. Whole-block processing is one transaction, even if
  a bad input or numerical failure occurs on its final sample. Use fixed staged
  storage or a deterministic validate-then-replay pass; no heap allocation.
- Success is independent of legal block partitions and agrees with repeated
  `process_frame` calls. Neither method allocates/deallocates, locks, performs I/O,
  logs, fits coefficients or has an unbounded loop. Output and state may include
  finite subnormals; v1 specifies no undocumented flush-to-zero treatment.

## Independent references and acceptance

The following are required engineering gates, not already executed results.

1. **Registry/source admission.** Validate the four exact values, ordered graph,
   assembly identity, units, atlas SHA/pages, ideal assumptions and explicit null
   physical fields. Negative fixtures must reject swapped capacitor identities,
   grounded treble return, duplicate/missing elements and falsely measured values.
2. **Analog algebra.** Independently implement series/parallel equations and
   nodal KCL from the registry. For `s = j*2*pi*f`, use
   `PT = (s*L2 || RT)`, `PW = (1/(s*C16B) || RW)`,
   `BT = PT + 1/(s*C16A)`, `BW = s*L3 + PW`,
   `HT = PT/BT`, `HW = PW/BW`, `Yin = 1/BT + 1/BW`.
   Check 121 logarithmic points from 10–20000 Hz plus 400/800/1600 Hz, both
   complex outputs and admittance, using normalized error
   `abs(actual-reference)/max(1,abs(reference)) <= 2e-10` per SI quantity.
   At DC the explicit limits are HT=0, HW=1 and Yin=1/RW. The atlas's rounded
   points are a coarse sanity check: at 800 Hz approximately -4.60 dB/+110.17
   degrees treble, -4.89 dB/-111.46 degrees bass and `abs(Zin)=23.83 ohm`.
3. **Actual digital processing.** At every admitted sample rate, compare native
   recurrence response and settled processed sine fits with the analog reference
   at `f_analog = fs/pi*tan(pi*f_digital/fs)`. The recurrence/reference normalized
   budget is `2e-10`; settled sine fits use `2e-8` after independently bounding
   transient residue. Also retain ordinary same-Hz errors separately. A warped
   pass does not establish audible same-Hz accuracy or replace its measured
   error table. Verify both load ports and input current, including varied loads.
4. **State/transactions.** Exercise precharged checkpoints, all sixteen ordered
   rate pairs, repeated/split blocks, empty flush, late invalid inputs, aliasing,
   nonfinite/extreme data, frame overflow and next-valid-call continuation.
   Failed calls preserve destinations and complete state exactly. Track zero
   input decay over ten seconds at nominal loads and finite subnormal behavior.
5. **Passivity and resource bounds.** At interval midpoints the trapezoidal
   energy identity is `E_next-E_prev = h*(u_mid*Iin_mid - VT_mid*IT_mid -
   VW_mid*IW_mid)`. Require residual `<= 2e-11*max(1, abs(E_prev), abs(E_next),
   abs(h*u_mid*Iin_mid))` J on bounded accepted fixtures. Endpoint-power
   rectangular sums are not this identity. Calibrated allocation probes must
   observe no allocations or frees across successful and rejecting processing.

The independent reference must not call the native response helper or merely
copy its prepared matrices as its oracle. Preserve original failures and retain
source/configuration identities with reports. Actual driver fits, source-load
feedback with the Leslie power stage, same-Hz audible policy, hardware comparison
and horn/drum integration are following milestones with separate acceptance.
