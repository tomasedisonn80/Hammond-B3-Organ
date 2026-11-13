# Nominal unloaded scanner rotor

`ScannerRotor` implements the named approximation
`nominal-unloaded-triangular-scanner-rotor-v1`. It selects two neighboring
terminal voltages with complementary linear weights while retaining one
continuing mechanical phase. It does not own the LC line, a receiver load,
Engine routing, a public parameter, a resampler or an output filter.

The source is [ScannerRotor.h](../include/hammond/ScannerRotor.h) and
[ScannerRotor.cpp](../src/ScannerRotor.cpp). The [frozen numerical
contract](SCANNER_NUMERICAL_CONTRACT.md) separates G4 rotor behavior from G5
audible numerical policy, G6 integration and physical M4 fidelity.

## Documentary basis and limits

The unchanged [atlas](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf), pp. 163–171,
distinguishes sixteen mechanical positions, nine scanner terminals and nineteen
line outputs. The [independent primary review](research/SCANNER_PRIMARY_REVIEW.md)
corroborates the maps and full traversal from the original paper's Table 2 and
Figures 1/3. It retains the fifteen-entry printed atlas error in
[E01](research/ERRATA.md#e01--scanner-traversal-has-15-entries-for-16-positions).
The implemented zero-based traversal is:

```text
0,1,2,3,4,5,6,7,8,7,6,5,4,3,2,1
```

These arrays encode the reviewed simplified circuit model, not newly recovered
production wiring. The three maps below use **one-based line-output labels**;
the C++ selection record uses zero-based indices.

| Mode pair | Outputs selected by terminals 1 through 9 |
| --- | --- |
| V1 / C1 | 1, 2, 3, 4, 5, 6, 7, 8, 9 |
| V2 / C2 | 1, 2, 3, 5, 7, 9, 11, 12, 13 |
| V3 / C3 | 1, 2, 4, 7, 10, 13, 16, 18, 19 |

The six semantic modes contain no Off value. Bypass belongs to the Swell/Great
tablets. Internal enum values are not physical dial positions or new host
parameter IDs. `scanner_mode_return` maps V modes to the grounded vibrato return
and C modes to the floating chorus return; the caller applies that topology to
the line. Selecting C on the rotor alone does not alter an arbitrary input
voltage vector.

Phase zero is the center of terminal 1. Increasing phase follows the listed
forward/return cycle. The primary paper's plotted angle is shifted:
`theta_paper = (2*pi*phase_turns + pi/8) modulo 2*pi`. Nominal speed is the atlas's
`412/60 Hz`. The paper's approximate 6 Hz does not independently verify 412 rpm;
no specimen speed, regional drive, jitter or uncertainty interval was acquired.

The unloaded, symmetric linear overlap assumes negligible ladder loading and
a constant sum of two neighboring coupling capacitances (atlas pp. 165–166).
Measured overlap, gaps, fringing, residual neighbors, capacitance, receiver
impedance and rotational asymmetry remain unknown. This implementation adds
no smoothing or contact clicks.

## Selection and signed output

For admitted phase `p` in `[0,1)`, the selector takes position `floor(16*p)` and
fraction `16*p - floor(16*p)`. The current and following positions select two
terminals, whose depth map selects two line outputs. Weights are `1-fraction`
and `fraction`. The last interval blends terminal 2 back to terminal 1.

`ScannerRotorSelection` reports phase, mechanical position, both terminal
indices, both tap indices and both weights. Positions are zero-based `0..15`,
terminals `0..8`, and taps `0..18`; none is a wire label. `ScannerRotorFrame`
adds the signed output voltage and completed-interval count.

The output uses `std::lerp` to evaluate the finite complementary blend without
rectification. All nineteen input taps must be finite and within
`+/-kScannerMaxOutputVolts` (131072 V), including unselected taps. This inherited
limit is defensive numerical admission, not a physical voltage specification.

Inputs are relative to ground. In chorus, `v=r+z` already contains the common
return. Since the weights sum to one, blending these taps includes `r` once;
the rotor adds no further dry signal or fixed chorus mix (atlas p. 171).

## API, clock and checkpoint

| Operation | Successful behavior |
| --- | --- |
| `prepare(rate)` | Accept a line-supported research rate and reset phase/count to zero. |
| `reconfigure_sample_rate(rate)` | Replace the increment while retaining phase and count exactly. |
| `state()` / `restore_state(state)` | Read/restore `phase_turns` and completed `frames`; these are transient replay state. |
| `observe(taps, mode, frame)` | Read the current phase with the current count; advance nothing. |
| `process_frame(taps, mode, frame)` | Read the old phase, then advance by `(412/60)/rate` and increment the count once. |
| static `select(phase, mode, selection)` | Compute the connection/weight record without preparation or advancing time. |
| static `evaluate(phase, taps, mode, frame)` | Evaluate an explicit phase; report frame count zero because there is no clock. |

Supported rates are the fifteen host/multiplier pairs
`{44100,48000,96000} * {1,2,4,8,16}` (eleven distinct numeric rates). They are
internal research rates and do not extend the Engine/native host-rate API.

The first processed frame has count **1** and observes phase **0**. Its retained
state holds the next phase. After any processing, `observe` reads that retained
upcoming phase, not an automatically cached copy of the last returned output.
This matches the line's completed-interval count while preserving the declared
read-before-advance rotor convention. A combined caller must document its
stopped observation convention explicitly.

Mode/depth changes only select another map. They neither reset phase nor create
another clock. Call the rotor for every elapsed sample, including silence and
muted/disconnected routes; routing belongs to the combined module. Observations
and control-only calls advance no history. At a rate change the physical angle
is preserved exactly, while its subsequent increment follows the new rate.

`phase_turns` must be finite and in `[0,1)`. Explicit phase 1 and negative values
reject rather than being wrapped or clamped; `nextafter(1,0)` is admitted.
`UINT64_MAX` is a restorable/observable completed count, but cannot advance.
The mode conversion helpers return `bool`, preserve their output on invalid
modes, and use zero-based depth `0..2`. `scanner_mode_name` returns an empty
string view for an invalid mode.

## Failure, storage and work

Every rejected operation preserves the complete prepared object and destination.
Methods requiring preparation return `NotPrepared` before other errors.
`prepare` and the static diagnostics do not require preparation.

| Invalid input | Status |
| --- | --- |
| Unsupported/nonfinite preparation or reconfiguration rate | `InvalidSpec` |
| Invalid restored phase | `InvalidProfile` |
| Invalid semantic mode | `InvalidEvent` |
| Invalid explicit phase in static selection/evaluation | `InvalidSpec` |
| Nonfinite or out-of-range tap/output | `InvalidBuffer` |
| Advancing a saturated completed counter | `TimelineOverflow` |

Static selection checks mode before phase. Evaluation then checks all nineteen
taps. Prepared processing checks the overflow condition after those checks and
commits only after successful evaluation. The same rules apply with nonzero
history; rejection is never implemented as a reset.

All storage is fixed. Processing performs one fixed nineteen-tap validation
loop, constant-size index/weight calculation, one interpolation, one bounded
phase wrap and one counter increment. There is no parsing, matrix solve,
allocation, destruction of owned resources, I/O, lock or unbounded retry.
The local GCC x86-64 build measured 40 bytes for `ScannerRotor`, 64 for its
selection record and 80 for its frame; these are ABI observations, not portable
layout guarantees. Dynamic allocation instrumentation and full-callback timing
remain separately assigned evidence.

## Verification and next step

[Assignment 19](development/2026-11-13-scanner/19-scanner-rotor.md) retains the
producer's strict build and bounded smoke results. Independent assignment 20
owns the complete frozen one-hot, boundary, polarity, return and lifecycle
acceptance. Combined line/rotor routing and allocation qualification follow;
the [current handoff](SCANNER_HANDOFF.md) owns their actual status. No producer
smoke closes G5, G6 or physical fidelity.
