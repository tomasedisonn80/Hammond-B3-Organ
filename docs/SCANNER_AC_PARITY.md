# Independent native scanner frequency qualification

`tools/qualify_scanner_ac.py` compares the actual native scanner line against the
independently stamped full-graph circuit in `tools/scanner_ac_reference.py`.
The graph, electrical boundary and numerical budgets remain those of
[scanner-numerics-v1](SCANNER_NUMERICAL_CONTRACT.md). The tool rejects a changed
contract hash; it does not redefine a failed numerical budget after observing
results. The model is `atlas-late-b3-nominal-line-v1`, with the
`scaled-physical-trapezoidal-scanner-line-v1` realization.

This is part of G3 discrete implementation evidence. The independent physical
state/transient tests own the rest of G3. Same-hertz comparisons are a separate
G5 diagnostic; even a passed stationary same-hertz comparison does not qualify
transients, rotating output, interpolation, decimation filtering, Engine/native
integration or physical M4. Refer to the [current handoff](SCANNER_HANDOFF.md)
for the aggregate status.

## Comparison and retained data

The default run includes the exact 282-positive-frequency grid, separate
rational DC, both return states and every combination of host rates
44,100/48,000/96,000 Hz with research multipliers 1/2/4/8/16. The fifteen labels
contain eleven distinct internal rates. Each distinct rate is actually computed
once per mode, and every host/multiplier label names the cases that cover it.
This deduplication is explicit; it does not claim fifteen distinct rates.
The largest research rate is 1,536,000 Hz, with no change to public host support.

The native probe's response operation solves its actual prepared recurrence.
For each digital physical frequency `f`, the independent analog solve uses

```text
mapped_analog_hz = internal_rate_hz / pi * tan(pi * f / internal_rate_hz)
```

This is the unprewarped bilinear mapping, with `kappa = 2*internal_rate_hz`.
Every comparison retains all nineteen signed, ground-referenced taps, return
gain and input admittance. Input current is positive into the line. Current is
multiplied by 15,000 ohms for the frozen dimensionless complex comparison, and
the original A/V value is retained separately. No fitted gain, polarity, phase
or one-frame adjustment is allowed.

| Comparison | Frozen absolute plus relative bound | Required channels |
| --- | --- | --- |
| Exact DC | `1e-10 + 1e-9*abs(reference)` | Nineteen taps, return and dimensionless current |
| G3 mapped analog AC | `1e-8 + 1e-6*abs(reference)` | Nineteen taps, return and dimensionless current |
| G5 same physical hertz | `1e-3 + 1e-2*abs(reference)` | Nineteen taps |

The report keeps every bin, complex native and reference values, errors, bounds,
error/bound ratios and failed channel names. Native recurrence residuals and
conditions are separate from the reference's nodal residuals and scaled
conditions. Residuals must not exceed `1e-9`; a condition estimate times `2^-52`
above `1e-4` makes an otherwise successful result inconclusive. Exact DC records
retain rational numerator/denominator pairs and do not call the AC solver at a
small nonzero frequency.

For both mapped and same-hertz comparisons, phase eligibility requires both
compared magnitudes to be at least `1e-4`. Each eligible segment unwraps from its
own principal phase. Missing bins and reasons remain in the report, and group
delay never crosses a null. Secants use digital physical angular frequency for
both values, including the mapped-reference curve; this prevents comparing
derivatives in different frequency coordinates. Single-bin segments have no
group-delay estimate. These are diagnostics, not alternative acceptance bounds.

## Actual process path and startup convergence

The tool also invokes the probe's actual `process_frame` cosine experiment at
100, 997, 5,000 and 7,000 Hz for every distinct internal rate and both modes.
The probe fits cosine, sine and a constant; the complex transfer is
`(cosine_coefficient - j*sine_coefficient)/input_amplitude`. This operation does
not substitute the recurrence response helper for audio processing. Both half
window estimates, physical fit-residual RMS and the explicit endpoint convention
are retained.

The separate protocol `scanner-process-settling-refinement-v1` tries pre-rolls
of 0.125, 0.25, 0.5 and 1.0 seconds in order. A measurement lasts at least
0.125 seconds and eight carrier cycles. It stops only after two consecutive
runs have stable first/second-half estimates and their full-window estimates
agree, channel by channel, within `1e-8 + 1e-6*abs(later_estimate)`. These
convergence checks use actual process estimates, without looking for an
oracle-matching gain or time shift. Once settled, the final estimate is graded
against the independently mapped analog AC reference using the frozen G3 bound.
Every earlier attempt remains in the report. A cap reached without settling is
inconclusive, never an accepted finest result.

The initial 48 kHz diagnostic exposed why this matters: the vibrato 7 kHz fit
after 125 ms had a largest complex error about 1.348 times the G3 limit, with
maximum tap fit-residual RMS `6.837118032414983e-7 V`. Its 250 ms estimate was
already within approximately 0.000145 times the same limit. That early failure
is retained in [assignment 17](development/2026-11-13-scanner/17-native-ac-parity.md)
and in full-run startup attempts. No numerical tolerance was relaxed. The
frozen contract requires reported startup/convergence; it does not prescribe a
particular pre-roll length for this process-path check.

## Reproduction

Build from the same source snapshot used for the comparisons:

```sh
cmake -S . -B build-scanner -DCMAKE_BUILD_TYPE=Release
cmake --build build-scanner --target hammond_scanner_line_probe
python3 tools/qualify_scanner_ac.py \
  --probe build-scanner/hammond_scanner_line_probe \
  --output /absolute/existing-directory/scanner-ac-full.json
```

For a multi-configuration generator, select `--config Release` and supply the
actual configuration-specific executable path. On Windows, include `.exe`.
The tool requires only Python's standard library. A complete report is compact
JSON and may be tens of megabytes; it preserves detailed failed bins rather
than replacing them with a favorable summary.

A bounded diagnostic subset is explicit in the report:

```sh
python3 tools/qualify_scanner_ac.py \
  --probe build-scanner/hammond_scanner_line_probe \
  --host-rates 48000 --multipliers 1 --mode chorus \
  --frequencies 20,997,5000,7000,20000 --skip-process \
  --output /absolute/existing-directory/scanner-ac-subset.json
```

A subset does not claim full grid coverage. `--skip-process` records `not_run`.
Repeated modes, unsupported host rates/multipliers, empty/unsorted/duplicated or
nonfinite frequency grids are rejected. The default run retains the frozen
selection without adaptive frequency additions.

Exit status 0 means the executed G3 frequency checks passed; a disclosed G5
same-hertz failure does not change that result. Exit 1 accompanies a written
report with failed or inconclusive executed G3 checks. Exit 2 means invalid
inputs, a failed operation or untrustworthy evidence; a previous output stays
intact. Existing regular report files may be atomically replaced. Symlink or
nonregular destinations, aliases of the source/probe and oversized/nonfinite
reports are rejected. The report limit is 128 MiB and native response output is
limited to 8 MiB per operation.

The report hashes the exact graph, frozen contract, compiler, generated header,
reference, line/probe source, supporting native headers, qualifier and native
executable. It checks those source/executable hashes again at completion and
rejects a changing run. Available CMake cache identity/flags and Python/platform
information accompany the report. These hashes identify the computation; the
caller must still associate the executable with a coherent source build. A
source manifest by itself cannot prove how an arbitrary binary was compiled.

## Observed full-grid result

The assignment-17 strict GCC 14.2 Release run passed G3 stationary comparisons
and all 88 distinct process carrier cases. It covered all fifteen host/factor
labels through eleven distinct rates, 6,204 unique positive native solves and
6,812 independent AC solves. The maximum mapped complex difference was
`1.0892198819708419e-12`; the maximum accepted process difference was
`1.520540673420773e-11`, including dimensionless input current. No required solve
failed its residual or conditioning budget. Five early process attempts outside
the complex budget remain recorded; all cases settled by 250 or 500 ms.

**Every investigated internal rate failed the G5 same-hertz grid.** At the
highest permitted research rate, 1,536,000 Hz, vibrato still failed 95 tap
comparisons across twelve frequency bins; chorus failed eighteen across four
bins. At 7,075 Hz, the worst error/bound ratios were approximately 5.2834 for
vibrato tap v5 and 2.0204 for chorus tap v11. This ideal lightly damped network
has sensitive high-frequency structure; multiplying the base rate alone has
not met the frozen budget. Choosing 16x and labeling it qualified would
contradict the observed result.

The next numerical-policy task must preserve this model and failed experiment,
then investigate an explicitly identified different numerical realization or
other justified policy. Adding unmeasured damping or changing tolerances cannot
silently turn this same model/contract into a pass. Independent transients,
rotating-output reference convergence and actual resampling/filter evidence
remain separate prerequisites before an integrated audible-policy claim.

## Maintained regression and current evidence

[`tests/test_scanner_native_ac.py`](../tests/test_scanner_native_ac.py) uses a
small but meaningful three-host-rate grid and all four required process
carriers. It independently checks rational DC values, ideal first-divider/KCL
identities, preserved same-hertz failures, signed-output mutations, residual and
conditioning failure states, phase gaps, malformed native identity/data,
source-change rejection and atomic output preservation. CTest supplies
`HAMMOND_SCANNER_LINE_PROBE_EXECUTABLE`; absence of the built executable is an
error, not a skip. This bounded suite does not replace the full offline grid.

Actual full-grid metrics, source/binary/report identities and the exact local
build commands are recorded in [assignment 17](development/2026-11-13-scanner/17-native-ac-parity.md).
Future optimization or rate-policy work must rerun the affected comparison from
its own coherent build, preserve failures and keep the remaining gates separate.
