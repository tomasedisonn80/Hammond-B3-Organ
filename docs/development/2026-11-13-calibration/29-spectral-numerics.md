# Assignment 29 — independent spectral and numerical qualification

Actual identity: `/root/cal_w5_a29`, logical wave 5, assignment 29, on
2026-11-13. This worker owns only `tests/test_capture_numerics.py` and this note.
The integrator owns production repairs, shared documents, accounting, CMake,
coherent integration and Git publication. This worker did not change production,
contracts, shared files or Git refs, and did not dispatch additional workers.

All commands used
`/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ` as their working directory.
The new suite passed its first execution: **19 methods, zero failures, errors
or skips, in 0.703 seconds**. Two methods cross-check the independent oracle;
the other 17 exercise production behavior. These counts are methods, not the
many subcases, coefficient comparisons or assertion calls within them.

## Scope, reading and source identity

Read the standing `AGENTS.md`, current calibration scope/handoff, README,
status, next steps, latest development-log entry, complete M0–M9 plan, relevant
atlas review and the separate rotary/standalone ownership boundaries. Read the
entire frozen comparison contract, existing independent metric acceptance and
the producer's metric/admission implementation. Fresh source-text reading for
this assignment covered atlas pp. 364 and 484: preserve disagreement and raw
comparison meaning, freeze decision bounds, retain uncertainty, and distinguish
numerical agreement from physical evidence. The six session readers own the
complete 500-page review. This worker claims neither another complete reading
nor new original-page image inspection.

The existing 42-method comparison suite already checks the required literal
vectors, strict admission, report shapes and short complex-exponential sums.
This assignment extends numerical evidence with independent high-precision
transcendental arithmetic, a different polynomial evaluation strategy, closed
forms, longer cancellation, phase branches and additional resource compositions.
It does not recount the earlier suite as newly authored acceptance.

Initially observed `HEAD` was
`45f875d80b6cc78c89ecc8b665bf2aedf058a97c`, tree
`2dcfc0e8071cdc30d75f8fb9be340826296fcbaf`. The parent subsequently published
and aligned the checkout to `779fb6e13b8f60236cad4aedb9999ba16198f920`, tree
`f9baccbb54f51063b01a0859d2c10cdadfbd238b`; locally recorded `origin/main`
was that same commit at the final observation. This worker did not fetch or
independently attest remote publication. These surrounding commits do not
identify the then-uncommitted test file or qualify the full current worktree.

| Exact relevant file | Bytes | SHA-256 |
| --- | ---: | --- |
| `tools/compare_capture.py` | 33,448 | `220a593499539db5f1e635db2eb15ba3c0aa7c6d001c80407fbffe93f75a9a0a` |
| `tools/capture_common.py` | 9,625 | `e06dd82e37dd178863af61aa66bee877da1fc7e498a47b729e060215ca79c3f2` |
| `docs/CAPTURE_COMPARISON_CONTRACT.md` | 28,479 | `4ec3037aa0588528fe3c9e520d099cc48a82d78135fc86bd3851c2667860750c` |
| Earlier independent `tests/test_capture_comparison.py` | 36,503 | `fe0afc04bfbd2b8211580ee7960db49a5e83272ad2241bf8515ec39b59cf4095` |
| New `tests/test_capture_numerics.py` | 28,572 | `63ecee0b99d4f98482c44f7d47c1413ae41989817622bc24ba07e5c36977ddbc` |

The producer and dependency hashes were unchanged between initial reading and
the final post-test observation. No producer change was required by this suite.

## Independent oracle and cross-checks

The maintained test uses only the Python standard library. Expected coefficients
do not call producer helpers, `math.sin`, `math.cos`, `cmath.exp` or producer
reports. The independent arithmetic path is:

1. Compute pi with 90-digit `Decimal` arithmetic using the Machin identity
   `pi = 16*atan(1/5) - 4*atan(1/239)` and convergent alternating series.
2. Reduce the phase in Decimal, evaluate sine and cosine with Decimal Taylor
   series, and obtain one complex unit-circle point for the requested frequency.
   Float inputs enter with `Decimal.from_float`, retaining their exact stored
   binary64 value rather than replacing it with a rounded decimal spelling.
3. Express the symmetric Hann weights as `sin(pi*n/(N-1))**2`, with explicit
   zero endpoints, independently of the producer's `0.5*(1-cos(...))` expression.
4. Evaluate the weighted finite polynomial with complex Horner recurrence at
   that one unit-circle point, using Decimal products and sums throughout.
   This differs from the producer's separate binary64 sine/cosine evaluation
   and `math.fsum` at every sample index.
5. Calculate magnitudes with Decimal square roots. Calculate phase with an
   independent Decimal atan2 using reciprocal/quadrant transformations and
   an argument-reduced arctangent series. No producer atan2 result is an oracle.

The first oracle check compares computed pi to an independently retained decimal
prefix, checks the four quadrants and `pi/3` against exact/square-root values.
The second checks Horner coefficients against separate geometric closed forms
for constant records, including a very small off-bin frequency. The rectangular
closed form is `(1-z**N)/(1-z)` with the removable value `N` at `z=1`.
The Hann closed form combines the rectangular sums at `f` and
`f +/- rate/(N-1)` with coefficients `1/2`, `-1/4`, `-1/4`, then divides by
the exact mathematical weight sum `(N-1)/2`. These checks agree within `1e-65`
in Decimal, far below the binary64 acceptance allowances.

For cancellation checks, expected DC and bias use exact `Fraction.from_float`
sums of the actual stored inputs. The RMS/normalized-error/dB fixture uses
90-digit Decimal squares, square roots and logarithms of dyadic inputs and
exactly representable differences. The explicit naive negative control uses
a sequential `+=` fold: Python versions that improve built-in `sum` cannot
accidentally invalidate that control.

## Fixed numerical allowances

Allowances were written before the first production execution. None was adjusted
after observing a producer result. They are engineering budgets for these
specified calculations and exercised platforms, not physical uncertainty or a
proof of every possible system math library.

Let `u = 2**-53`, `S = sum(w)`, `L = sum(abs(w*x))/S`, and
`T = 2*pi*abs(f)*(N-1)/rate`. The component allowance begins with:

```text
64*u*(1+T)*L
```

The `T` term allows absolute phase error to grow with argument magnitude rather
than applying a fixed tiny tolerance to an approximately 823,000-radian maximum
frame phase. The constant reserves argument formation, pi representation,
trigonometric rounding, products, compensated summation and final division.
This budget is deliberately much larger than a single ideally rounded operation,
while remaining much smaller than the fixture changes the tests distinguish.

For Hann, add the following absolute weight/normalization allowance, excluding
the exactly defined zero endpoints from the first sum:

```text
64*u*(sum(abs(x[1:-1]))/S + (N/S)*abs(D))
```

This avoids assuming a relative error bound for a tiny Hann endpoint-adjacent
weight, where subtraction in the producer can lose relative precision. Four
binary64 ulps of the expected component cover final oracle-to-float rounding
and comparison representation. The 90-digit oracle's own error is substantially
smaller; its independent closed-form checks retain that separation.

Magnitude and coefficient-difference checks use the component allowances and
the triangle inequality with a factor of two. Phase checks use the local
argument sensitivity to coefficient perturbations: four times the sum of
the two component allowances divided by their coefficient magnitudes, plus
`64*u`. Those phase fixtures have nonvanishing coefficients safely away from
the mask boundary. The separate floor tests instead use exact dyadic impulse
normalization and the adjacent binary64 values, so their mask decisions do not
receive a hidden epsilon. Circular phase distance handles equivalent numerical
representations at the branch cut; separate checks still require every actual
phase to lie in `(-pi, pi]` and preserve the expected wrap signs.

The independent RMS/ratio/logarithm fixture uses `32*u*abs(expected)` for its
nonzero values. Exactly representable cancellation, zeros, floor decisions,
identity fields and off-bin polarity's positive-pi mapping use exact assertions.
No tolerance is used to delete a bin, change a policy margin or promote a
numerical result into physical acceptance.

## Executed coverage and actual bounds

| Area | Executed qualification |
| --- | --- |
| Off-bin coefficients | Rectangular and Hann records of 7, 18 and 65 frames; asymmetric dyadic samples; DC, tiny off-bin, ordinary off-bin, adjacent-below-Nyquist and Nyquist frequencies. Both coefficients, magnitudes and complex error are checked against Decimal expectations. |
| Distinct closed forms | Actual producer constant-record coefficients at 31 frames agree with Dirichlet and Hann frequency-shift closed forms, including a small non-bin-centered frequency. Repeated input retains exactly zero complex error. |
| Hann endpoints and normalization | Real 129-frame endpoint-only disagreement has exactly zero weighted coefficients while retaining the unwindowed 2e6 maximum error. Signed constant DC at 4, 32 and 257 frames checks even/odd weight normalization. |
| Long-record phase | An actual 262,144-frame, one-channel, one-frequency comparison at rate 768,000 and frequency 383,999.9375 Hz. Nonzero samples at frames 262,143 and 262,142 have separately calculated impulse coefficients. Actual RMS values are exactly 1024 and 512. |
| Nearby frequencies | Retains zero and the smallest positive binary64, adjacent binary64 values near 3.125 Hz, a resolvably separated 3.125001 Hz value, and adjacent Nyquist values. Resolvably different inputs produce different coefficients. Adjacent doubles are not falsely promised distinct output bits when their difference lies below roundoff resolution. |
| Cancellation and dynamic range | Actual 297-frame repeated large/tiny/opposite-large data retain exact rational reference/candidate DC and bias, as well as their DC coefficients. A 257-frame mixed-scale fixture checks RMS, error, normalized error and dB against Decimal. |
| Phase and masks | Both lead and lag cross the phase branch cut at three fixed neighboring frequencies; nonsinusoidal off-bin phases use independent Decimal atan2; off-bin polarity keeps positive pi. Adjacent floats below/equal/above the declared floor retain exact mask decisions under impulse normalization. Hann masking does not erase large pointwise disagreement. |
| Maximum report shape | Actual 16 channels by 64 frequencies, with different amplitudes and impulse locations for each channel. All 1,024 frequency rows and both coefficients per row are independently checked; JSON remains finite and physical fidelity stays unestablished. The actual work is `16*9*64 = 9,216`, not the maximum spectral workload. |
| Full admission composition | Real public inputs describe `C=16,N=262144`: exactly 4,194,304 scalar references per side. At `K=4` the spectral budget is inclusive and reaches the deliberately invalid first sample; at `K=5` it rejects for work before that sample is visited. Lists are reused and a sentinel stops traversal, so this does not claim a complete 8,388,608-scalar scan. |
| Completed reduced work limit | With the spectral cap explicitly reduced to 186, a real `2*31*3` comparison computes every row. A fourth frequency rejects rather than truncating, and both input arrays remain unchanged. This qualifies guard behavior at a small workload, not full-maximum performance. |

The largest actual single spectral calculation is 262,144 terms under the
contract's `C*N*K` accounting. The full 16,777,216-term maximum was not run,
timed or memory-qualified. The maximum-shaped report test is an actual complete
report, but is not a maximum-size serialized report or a maximum-frame,
maximum-channel run. These distinctions are intentional.

## Actual commands and result

Runtime: Python `3.12.14`, built with Clang `22.1.3`; `sys.platform` is `linux`
and machine is `x86_64`. No additional package, network service, hardware audio
device or instrument recording was used.

```sh
python3 -B tests/test_capture_numerics.py
```

Observed output:

```text
...................
----------------------------------------------------------------------
Ran 19 tests in 0.703s

OK
```

This was the first execution of the new suite. There was no earlier failing
production or test-harness run to suppress, and no changed tolerance or expected
value after inspection of results. No production defect was found in this
bounded numerical scope. The tests are not a benchmark, and the elapsed value
is an observation rather than a speed threshold.

## Integration and continuation

Root received the ready notice and exact observed result. Integrate these two
owned files into the normal Python-test discovery and qualify the final coherent
source alongside the existing comparison and policy suites. The integrator owns
shared accounting/status/handoff and authorized commit/push. A subsequent source
change requires relevant numerical reruns and updated identities; neither this
note nor a future source hash automatically qualifies changed calculations.

Remaining scope includes other native/platform math libraries, full maximum work
and memory behavior, long-record dense arbitrary signals beyond these fixtures,
physical clock/scale/synchronization, acquisition provenance and uncertainty,
reference-instrument recordings, held-out fitting, listening and fidelity.
The retained tests provide independent synthetic numerical evidence for the
specified cases only. Actual physical decision margins must still be justified
and frozen separately under the atlas's acquisition and acceptance procedure.
