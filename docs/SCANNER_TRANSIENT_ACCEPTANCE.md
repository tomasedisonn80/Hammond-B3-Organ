# Independent transient-reference acceptance

The [independent regression](../tests/test_scanner_transient_reference.py)
checks the full-graph Python reference using literal documentary component
values, physical KCL, inductor voltage laws and discrete energy conservation.
The final local run passed **21 methods** under Python 3.12.14. Its isolated
required CTest gate passed **1/1 suite in 3.23 seconds**. The exact source,
commands and scope are retained in
[assignment 18](development/2026-11-13-scanner/18-transient-reference-tests.md).

This qualifies bounded reference behavior. It does not replace native matched-step
comparison, all frozen reference refinements, G5 audible numerical policy or a
specimen-specific physical claim. The [frozen numerical contract](SCANNER_NUMERICAL_CONTRACT.md)
and [current handoff](SCANNER_HANDOFF.md) own those separate gates.

## Independent expectations

The test imports only the producer's public line/state/trace/report interfaces.
Its expectations use separately retained literal values: 18 inductors of 0.5 H,
17 capacitors of 4 nF and the final capacitor of 1 nF, the six printed resistor
pairs, 15 kOhm termination and 22 kOhm common return. It does not import the
producer's normalized graph, private branch lists, matrix stamps, factors or
DC helper. The circuit and validation basis is the
[atlas](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf), pp. 157 and 182–186.

The independent common-return equation is obtained directly from resistor KCL:

```text
vibrato: r = 0
chorus:  r = (i1 + u/95000) / (1/22000 + 1/95000)
```

Each early divider is reconstructed between its **pre-inductor** node and r.
The remaining taps are ground-referenced p6 through p18. For all 36 coordinates,
the test derives continuous derivatives from KCL and `L di/dt = Vpositive - Vnegative`
and checks the actual old/new endpoints against the trapezoidal identity:

```text
state_new - state_old = (derivative_old + derivative_new) / (2*sample_rate)
```

Current differences are normalized by 1e-4 A and voltage differences by 1 V.
This verifies the claimed discrete method; it is not continuous-time convergence.

The independent energy test includes **all fourteen resistors** and input-source
work. With each voltage and current averaged between interval endpoints,

```text
energy_new - energy_old = h * (u_mid * Iin_mid - sum(Vbranch_mid^2 / Rbranch))
```

Using midpoint power is the trapezoidal circuit identity. Endpoint power alone
would describe a different experiment. Both input endpoints must be zero before
a trajectory is labeled zero-source passivity. Mode switching is checked through
physical-state reconstruction, without asserting zero switch work or continuity
of every ground-referenced voltage.

## Executed coverage

| Experiment | Observed scope |
| --- | --- |
| Exact DC equilibrium | Rational resistor-network values, both modes and 44.1/48/96 kHz; six equilibria each retained over 64 intervals. All taps, return and source current agree. |
| Signed physical basis | 36 coordinates × two signs × two modes = 144 initializations; independent observations before and after an interval. |
| Trapezoidal identities | 576 driven intervals across both modes and all three rates; every capacitor and inductor coordinate checked. |
| Source work and dissipation | 1,152 driven intervals across both modes and all three rates; independent stored-energy difference, source work and fourteen-resistor loss. |
| Passive charged states | Four prescribed charged families × two modes × 512 zero-drive intervals. The frozen per-step and total-growth limits pass. This 10.67 ms check is shorter than the separate required 250 ms suite. |
| Migration | All nine ordered host-rate pairs in both modes, precharged histories, exact physical checkpoint preservation, both return transitions and 16 subsequent frames against fresh restored controls. |
| In-frame topology selection | Explicit stopped switching and per-frame mode selection give identical outputs over 192 intervals. |
| Polarity | 256 paired driven intervals reverse all taps, return, current and physical states exactly; energy remains equal. |
| Failure continuation | 76 rejected input/mode/rate/state operations preserve nonzero state, observations, preparation selection and eight subsequent frames exactly. Saturated-counter rejection has its own replay check. |
| Input and time convention | All nine 2,400-knot fixture definitions, linear interpolation between the same knots, separate internal frame counts and first knot at time zero. |
| Comparison budgets | Each of the 55 required channels is independently perturbed; the fixed current scale, RMS-only failure and maximum-only failure are checked. Return/current diagnostics remain visible without changing the declared convergence gate. |
| Refinement reporting | Real zero-input control converges only after 8→16 and 16→32 pass. A real charged-C18 trace remains inconclusive. Malformed refinement orders, nonfinite data and alignment mismatches reject. |
| Output/CLI | Exact graph/tool/contract hashes, scope and clock metadata; source/hardlink aliases, directories, actual POSIX symlinks, nonfinite/oversized reports, failed atomic replacement and malformed CLI work preserve prior data. |

The diagnostics test retains the distinct physical/scaled companion and scaled
initial-MNA matrices, dimensions and computed condition estimates. It checks
that the conditioning flag follows the declared threshold; a small residual
is not substituted for a forward-error bound.

A separate short diagnostic harness using the same independently written KCL
and power functions observed maximum normalized endpoint-identity residual
**1.7182063335053482e-14** and maximum energy-balance residual
**2.818391755075697e-23 J** across 1,152 driven intervals. No production defect
or tolerance change was required.

## Retained refinement limit and next work

The 16-knot charged-C18 chorus experiment is intentionally outside the full
2,400-knot qualification grid. Its required-channel maxima were:

| Refinement | Largest normalized RMS | Largest normalized maximum |
| --- | ---: | ---: |
| 8→16 | 2.687299577331739e-4 | 6.653288808098345e-4 |
| 16→32 | 6.716013244123893e-5 | 1.6632497807189672e-4 |

Both exceed the frozen reference budgets (RMS 2e-6, maximum 1e-5). The returned
status is **inconclusive** and the finest trace is not called truth. The zero-input
control proves report mechanics, not accuracy for excited fixtures. Full nine-fixture,
both-mode 2,400-knot refinement is deliberately left to its dedicated numerical
qualification owner. Native all-coordinate matched-step parity is also separate.
No physical M4, G5 policy, rotor or host-integration pass follows from these tests.
