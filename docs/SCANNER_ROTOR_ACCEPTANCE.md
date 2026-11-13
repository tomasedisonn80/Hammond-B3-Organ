# Independent scanner rotor acceptance

[`tests/test_scanner_rotor.cpp`](../tests/test_scanner_rotor.cpp) independently
checks the nominal unloaded rotor's three depth maps, signed angular weighting
and continuing clock. The strict GCC 14.2 Release execution recorded in
[assignment 20](development/2026-11-13-scanner/20-rotor-acceptance.md) passed its
required CTest target, **1/1 in 0.06 seconds**, with no skipped case or production
repair. Assertions remain active under `NDEBUG`.

This is the rotor/G4 software evidence for
`nominal-unloaded-triangular-scanner-rotor-v1`. The
[frozen numerical contract](SCANNER_NUMERICAL_CONTRACT.md), section 6, owns the
acceptance limits. The [current handoff](SCANNER_HANDOFF.md) owns overall gates;
this result does not qualify continuous-time line accuracy, an audible-rate or
filter policy, combined routing, the Engine/native callback, or a physical
scanner. The public API is in [`ScannerRotor.h`](../include/hammond/ScannerRotor.h).

## Independent expectations and source scope

The test freshly consulted atlas pp. 163–170 as extracted text, the retained
[primary source comparison](research/SCANNER_PRIMARY_REVIEW.md), and the
[source gate](M3_REMAINING_AND_SCANNER_GATE.md). It did not independently render
figures or reread the external primary PDF. Its literal one-based depth maps are:

| Mode pair | Terminal 1 through terminal 9 select line outputs |
| --- | --- |
| V1 / C1 | 1, 2, 3, 4, 5, 6, 7, 8, 9 |
| V2 / C2 | 1, 2, 3, 5, 7, 9, 11, 12, 13 |
| V3 / C3 | 1, 2, 4, 7, 10, 13, 16, 18, 19 |

The sixteen one-based terminal centers are
`1,2,3,4,5,6,7,8,9,8,7,6,5,4,3,2`. Terminal 1 is phase zero, with increasing
phase following that traversal. The primary review documents the paper's
one-sixteenth-turn origin shift and corroborates the completed cycle. Atlas
p. 166's printed fifteen-entry mismatch remains an erratum. Nominal speed is
the atlas's `412/60 Hz`; it is not a specimen measurement or a speed independently
confirmed by the paper's approximate 6 Hz.

The output oracle does **not** use the production map, traversal, mode helper,
interval selector or interpolator. It sums circular triangular basis functions.
For phase `p` and a terminal-occurrence center `c`, it calculates

```text
distance(p,c) = min(abs(p-c), 1-abs(p-c))
hat(p,c) = max(0, 1-16*distance(p,c))
```

Terminal 1 has its center at zero, terminal 9 at one-half turn, and terminals
2–8 each have centers at `j/16` and `1-j/16`, with `j=1..7`. Summing their
independently weighted, literally mapped tap voltages yields the expected
signed output. Computation uses `long double`; its precision is platform
dependent. A separate metadata check verifies the reported mechanical index,
terminal indices, line-output indices, complementary weights and used phase.

The frozen voltage comparison is
`abs(actual-expected) <= 2e-12 V + 2e-12*abs(expected)`.
There is no fitted gain, sign, phase or timing correction.

## Executed electrical and angular coverage

For each of six modes, the test uses 96 phases: all sixteen exact centers,
three interior quarter positions in each interval, and the nearest representable
phase on each side of every center. The left side of zero is represented by
`nextafter(1,0)`; negative phases and phase one are separately rejected.

| Experiment | Actual coverage and result |
| --- | --- |
| Required vectors | Nine positive and nine negative one-hot terminal vectors, equal-terminal +1 and -1, and one unequal signed vector at every phase/mode: 12,096 evaluations. Unselected line outputs hold distinct nonzero values to detect an incorrect map. |
| Line-output basis | Every one of the nineteen source outputs individually excited, including unselected outputs, at every phase/mode: 10,944 evaluations. |
| Voltage bounds | 576 alternating-polarity endpoint-limit evaluations use ±131072 V and verify finite convex output bounds. These are computational admission limits, not operating-voltage claims. |
| Total direct evaluations | **23,616**, maximum angular-oracle error **5.551115123125783e-17 V**. |
| Center visits | At all sixteen centers in every mode, endpoints occur once and intermediate terminals twice; the active weight is exactly one and the adjacent weight zero. |
| Chorus return | Unequal local taps plus `r=0.375 V`, all phases and depths: **288** cases. Ground-referenced interpolation agrees with `r + weighted(local)`; maximum error **1.110223024625157e-16 V**. No second dry or return term is added. |
| Mode semantics | Six names/depth/return mappings are literal expectations. All 250 other byte-valued enum representations reject, and failed checked conversions preserve their destinations. |

V/C mode pairs share the rotor map. The line owns their different return
topologies; the synthetic return test does not replace an electrical line test.

## Clock, lifecycle and failure coverage

All fifteen host/multiplier labels from
`{44100,48000,96000} * {1,2,4,8,16}` are prepared. They contain eleven distinct
internal rates and do not enlarge the Engine/native host-rate API.

The suite checks **76,800 clocked frames**: 4096 from zero and 1024 from a
near-wrap checkpoint for every label. Every rate crosses a running wrap. A
processed frame reports the pre-advance phase and incremented interval count;
an observation reports the current count and advances nothing. Mode/depth
changes occur during processing. Silent, driven and deliberately discarded
outputs retain identical rotor states when called for the same intervals.
This establishes input/output independence of the rotor clock; a routing or
host caller must still prove that it actually invokes the rotor during bypass.

The nominal increment is independently checked against `(412/60)/rate`.
The largest accumulated phase discrepancy from an analytical `long double`
clock was **5.629096364381803e-14 turns**. The clock check permits at most
`4*N*binary64_epsilon` turns after `N` additions as an explicit arithmetic
rounding allowance. That allowance is separate from the frozen direct-angle
voltage budget, which remains unchanged.

All nine ordered stopped-rate pairs among 44.1/48/96 kHz preserve phase/count
exactly and continue identically to a newly prepared/restored control.
Successful `prepare` resets; `reconfigure_sample_rate` preserves history.
All six observations after nonzero history leave that history unchanged.
Inclusive phase boundaries include signed zero, the smallest positive
subnormal and the largest representable phase below one.

**716 prepared-object rejected calls** cover invalid phase restores, unsupported
and nonfinite preparation/rate changes, every invalid mode, and NaN, infinities
and both immediately-outside voltage bounds in every one of the nineteen taps.
Invalid unselected taps also reject. Each call preserves the complete visible
preparation, phase/count and destination, then compares 41 valid frames exactly
against an untouched copy. Together with rate migration and overflow replay,
the suite checks **29,766 continuation frames**. Static failure destinations and
multi-error status precedence are separately checked; unprepared calls retain
`NotPrepared` precedence where the API requires preparation.

Counter tests process the last representable interval, observe/restore
`UINT64_MAX`, then reject advancement with `TimelineOverflow` without changing
the clock or destination. Future replay restores the same phase at a usable
count in both the rejected object and its untouched pre-rejection control.

External frame grouping at each host rate gives **twelve exact comparison
paths**: groups 1, 64, 127 and repeating `[1,17,64,3,127,2,31]`. All 4096 outputs
and final checkpoints match, with silent intervals, mode changes and
non-advancing observations between groups. This API has no block callback,
tablets or disconnected-output parameter; their integration remains separate.

## Reproduce and continue

From the repository root, using the standard project toolchain:

```sh
cmake -S . -B build-rotor -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build build-rotor --config Release --target test_scanner_rotor
ctest --test-dir build-rotor -C Release --output-on-failure --no-tests=error -R '^test_scanner_rotor$'
```

The next owners must qualify the combined line/rotor routing and precharged
transactions, separately instrument allocation, and preserve any G5 same-hertz,
transient or rotating-output failure. The test does not measure overlap
capacitance, receiver loading, plate gaps, asymmetry or actual speed. Neither
this local Release run nor its source inspection establishes another platform,
callback deadline, hardware fidelity or product release.
