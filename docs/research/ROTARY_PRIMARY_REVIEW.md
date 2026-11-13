# Rotary primary-source review

Reviewed on 2026-11-13 by `/root/w02_a12_reference_tests` (assignment 12,
wave 2). This review checks the source behind atlas pp. 301–303 and the
separation between a numerical research model and physical evidence.

## Primary source and exact locators

Julius Smith, Stefania Serafin, Jonathan Abel and David Berners,
[Doppler Simulation and the Leslie](https://www.dafx.de/paper-archive/2002/DAFX02_Smith_Serafin_Abel_Berners_doppler_leslie.pdf),
DAFx-02, 2002, printed pp. DAFX-13–20 (eight PDF pages). The publisher PDF
text was retrieved directly; no copy, figure or measurement dataset is
redistributed here. PDF positions below are one-based.

| Locator | Finding |
| --- | --- |
| §3.3, PDF p. 3 / DAFX-15, fractional-read listing | Its fraction is the pointer minus its floor, but its sample weights are reversed. |
| §4.1, Eq. (18), PDF p. 4 / DAFX-16 | The denominator prints a positive cosine term despite the stated source and receiver coordinates. |
| §4.2, PDF pp. 4–5 / DAFX-16–17 | Measurements concern a Model 600 horn in free field, at fixed angles spaced by 15 degrees, with in-plane and axial microphones. |
| §4.3, PDF pp. 5–6 / DAFX-17–18 | The fitted response separates fixed base leakage from angle-dependent horn output. |
| §5, PDF pp. 6–7 / DAFX-18–19 | Woofer-port and in-cabinet measurements are not presented; extension methods are discussed. |

## Independent mathematical checks

These are project deductions, not an author-issued erratum. For a source
`q = (a*cos(theta), a*sin(theta), 0)` and receiver `m = (R, 0, h)`, expanding
the coordinate differences gives:

```text
|m-q|² = (R-a*cos(theta))² + (a*sin(theta))² + h²
       = R² + a² - 2*R*a*cos(theta) + h².
```

At zero angle and zero height, the distance is `|R-a|`; at half a turn it
is `R+a`. The maintained near/far endpoint test uses those hand-derived
distances. Cartesian distance avoids inheriting the disputed printed sign.

For adjacent samples `x[k]` and `x[k+1]`, evaluating exactly at `k` must
return `x[k]`. Therefore the linear weights are `(1-mu, mu)`, with
`mu = position-floor(position)`. The endpoint condition decides their
order without a DSP library or reference implementation. The current
motion/path reference has no waveform interpolator: this is a documented
requirement for subsequent interpolation tests, not a reported audio pass.

## Applicability and maintained verification

The source does not supply identified measurements of this project's
chosen cabinet, motor transition constants or bass radiation. A fitted
horn study cannot turn synthetic profile values into observations of a
vintage 122. Retain the explicit `proposed`/`unmeasured` boundary and acquire
identified, synchronized specimen data before physical qualification.

[The maintained tests](../../tests/test_rotary_reference.py) independently
check motor ODE balance and convergence; constant and signed motion;
event history and startup; private Decimal context; static, axial,
tangent and mirrored paths; historical emission; finite-difference
Doppler convergence; admission failures; CLI identity and isolation.
Constructed tangent cases reach both admitted Doppler-ratio endpoints.

This qualifies bounded numerical behavior only. It does not qualify
native parity, waveform interpolation, dynamic aliasing, real-time cost,
cabinet directivity or physical fidelity. See the
[numerical contract](../ROTARY_NUMERICAL_CONTRACT.md),
[reference boundary](../ROTARY_REFERENCE.md), and
[assignment record](../development/2026-11-13-rotary/12-reference-tests.md)
for exact execution evidence and remaining gates.
