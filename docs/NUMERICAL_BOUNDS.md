# Dry-engine numerical bounds

This is an engineering contract for `ideal-shared-sine-v1`, not measured tuning,
pickup voltage, physical stability, or an audio-callback deadline result. The
atlas asks for continuously shared sources and bounded numerical error on
pp. 63-66 and 103-108. The following limits and tests are this implementation's
derived numerical decisions; they are not factory specifications.

## Accepted source increments

`TonewheelBank::prepare`, and therefore `Engine::prepare`, accepts a source only
when its computed binary64 increment satisfies

```text
delta = frequency_hz / sample_rate
2^-53 <= delta < 0.5 turns/sample
```

All existing profile conditions still apply: finite positive frequency, finite
normalized gains/amplitudes, base phase in `[0,1)`, valid identities/routes and a
supported rate of 44100, 48000 or 96000 Hz. A frequency at/above Nyquist is
rejected before source preparation. Division that rounds to `0.5` is also rejected.
Below-floor increments, including positive division results, return
`InvalidProfile`. The implementation neither clamps frequency nor installs a
frozen replacement. The rule applies to muted sources too.

The decision uses the **computed increment**, not a decimal approximation to a
frequency cutoff. The exactly representable frequencies `sample_rate * 2^-53`
give these accepted boundary values:

| Sample rate (Hz) | Boundary frequency (Hz; decimal display) |
|---:|---:|
| 44100 | 4.89608353859694034e-12 |
| 48000 | 5.32907051820075139e-12 |
| 96000 | 1.06581410364015028e-11 |

Loading and preparing have separate jobs. The compiled-text loader validates
intrinsic profile data without a sample rate. `validate_runtime_profile` adds
the supported-rate and frequency/Nyquist checks, but does not certify phase
integration. A profile containing `1e-300 Hz` can therefore load and pass that
validator while failing bank/engine preparation. Callers must check the prepare
status; successful parsing is not a prepared engine.

Preparation remains transactional. A failure at any source preserves every
previous source, prepared flag and future sample. Engine rejection also preserves
controls, held keys, profile, block limit and frame clock. A rejected first
preparation leaves the bank unprepared and silent.

### Why a full phase spacing

The stored phase lies in `[0,1)` turns. For binary64, spacing in `[0.5,1)` is
`2^-53` turns, the largest spacing anywhere in the stored interval. An increment
of at least that size reaches another representable phase from every starting
phase. At the largest phase below one, adding the minimum increment reaches one
and wraps to zero. Larger accepted increments either move forward or wrap;
they cannot disappear as a zero phase change.

With round-to-nearest/ties-to-even, the tighter no-stall threshold would be
**strictly greater than `2^-54`**; equality can round back to an even phase.
This implementation deliberately uses the simpler conservative full-spacing
floor. Some smaller increments could advance under that rounding mode and are
still outside the supported domain.

Progress is not relative frequency accuracy. For example, an increment of
`1.25 * 2^-53` near phase `0.75` rounds to a `2^-53` step, a 20% local shortfall.
The floor prevents a frozen oscillator; it does not make frequencies near that
floor accurate. Arbitrarily tiny frequencies would require a separately designed
and validated representation. No compensated accumulator or oscillator redesign
is introduced here, and no extra per-frame work is added.

The reported numerical error bounds assume ordinary binary64 round-to-nearest
arithmetic without fast-math transformations. Changed rounding modes or alternate
arithmetic/library implementations need their own qualification.

## Bounded nominal drift evidence

`tests/test_numerics.cpp` advances the actual nominal profile for **262144 frames
at each rate**, using seed zero. This is 5.94430839002 s at 44100 Hz,
5.46133333333 s at 48000 Hz and 2.73066666667 s at 96000 Hz. It checks the actual
lowest and highest frequencies, tone 1 (`32.70319566257483 Hz`) and tone 91
(`5919.91076338615 Hz`). It creates no WAV or large capture buffer. The existing
`test_tonewheel` separately checks all 91 sources over one second and the engine
suite checks coherent routing and block partitions.

Phase and source-sample bounds are inspected for both selected sources on every
frame. Numerical phase comparisons cover the first 16 positions and every 1024
frames through the final phase. Samples are compared at the same interior
positions. Maxima below are maxima of those checked positions, not a claim of
an exhaustive analytical-error search between checkpoints.

### Independent elapsed-time oracle and allowance

The oracle uses fixed seed-zero phase answers; it does not read the bank's phase
to form an expectation and does not repeat its double addition recurrence.
For each stored binary64 frequency, `frexp` yields an exact integer significand
`M` and exponent `e`, giving `frequency = M * 2^(e-53)`. At these two extremes
and three rates, `D = sample_rate * 2^(53-e)` fits a `uint64_t`. Overflow-safe
integer modular multiplication computes `(frames * M) mod D` exactly. Only then
does the oracle convert the remainder/denominator to `long double`, add the
known initial phase and reduce modulo one.

The modular reduction prevents large elapsed phase from consuming the oracle's
fractional precision. It does not depend on `long double` being wider than
`double`; an allowance of eight `long double` epsilons covers the final bounded
conversions/division/addition. This is an oracle for integrating the stored
frequencies, not an independent measurement of their physical correctness.

For one production step, the phase-plus-increment sum is below 1.5, so binary64
rounding contributes at most `2^-53` turns. Dividing a frequency below Nyquist
contributes at most `2^-55` turns/sample. Subtracting one after a wrap is exact.
The circular phase-error allowance at frame `n` is therefore

```text
phase_allowance(n) = n * (2^-53 + 2^-55) + 8 * epsilon(long double)
sample_allowance(n) = amplitude *
    (2*pi * phase_allowance(n) + 8 * epsilon(double))
```

The sine bound uses `|sin(a)-sin(b)| <= |a-b|`; its additional double-epsilon
term allows sine/argument evaluation error on the tested library. It is not a
portable correct-rounding guarantee for every implementation of `std::sin`.
At 262144 frames with the observed 64-bit `long double` significand, the phase
allowance is `3.6379788938278867505e-11` turns and the unit-amplitude sample
allowance is approximately `2.28582731692127616e-10`. The allowance grows with
the tested frame count; these results are not an unlimited-duration drift claim.

### Observed results, 2026-11-13

Linux x86-64, GCC 14.2.0, Release with the repository's strict warning flags;
binary64 double and 64-significand-bit long double. Baseline commit `b9c1cac`
plus the working-tree wave-06 fixes. These results do not claim Windows/macOS
execution or bitwise equivalence between compilers, platforms, libraries or
future optimized reductions.

| Rate (Hz) | Tone | Maximum checked phase error (turns) | Maximum checked sample error (normalized) |
|---:|---:|---:|---:|
| 44100 | 1 | 4.37381793109981042988e-12 | 2.71935487653986911541e-11 |
| 44100 | 91 | 1.62222692961025427572e-12 | 1.00781642349534981962e-11 |
| 48000 | 1 | 2.94995560097544018419e-12 | 1.81957633427434913552e-11 |
| 48000 | 91 | 1.08684795104702081048e-12 | 6.65298986556170021678e-12 |
| 96000 | 1 | 5.44049039759991748255e-12 | 3.36449091650021722688e-11 |
| 96000 | 91 | 7.72218156390100385345e-12 | 4.79478160175333912793e-11 |

Compiled nominal profile SHA-256 remains
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.
No nominal parameter, seed convention or sample-generation operation changed.

## Maximum all-keys mix

The dry graph has at most `2 manuals * 61 keys * 9 drawbars = 1098` connected
branches. A branch gain, source peak, profile output gain and expression each
lie in `[0,1]`. By the triangle inequality, its exact-arithmetic output obeys

```text
abs(output) <= output_gain * expression * sum(branch_gain * source_peak)
            <= 1098 normalized units.
```

Shared-source collisions add coherently and still obey this bound. No
polyphony normalization or hidden limiter is assumed. The bound is far below
float overflow but far above PCM full scale; it is not a no-clipping promise.

The test uses a deliberately synthetic runtime profile: all 1098 branches route
to source 13, that source has unit amplitude and a quarter-turn initial phase,
its frequency is one-quarter of the sample rate, and gains/expression are one.
All 122 keys and all 18 active drawbars are enabled. At each rate, 256 samples
remain finite and attain `+1098` and `-1098`. The test allows one output-float
ULP at the bound (`1098.0001220703125` in this build). This exercises maximum
coherent numerical load; it is not nominal console wiring, a measured organ
level, a performance benchmark, or a hardware/host qualification.

## Regression and verification record

- Before the preparation fix, `test_numerics` failed because a positive
  `1e-300 Hz` source still prepared successfully. Agent 31's preceding probe had
  observed a seed-zero tone-1 phase stuck at `0.88331080821364261` for 1024 frames.
- At all three rates, predecessor/exact/successor boundary frequencies divide
  to predecessor/exact/successor increments around `2^-53`. Below-floor inputs
  reject after 90 valid candidates without changing a working bank's future.
  Fresh rejection remains silent; engine rejection preserves musical state,
  phase, clock, previous block limit and subsequent output.
- At and immediately above the floor, phases starting at 0, 0.25, 0.5, 0.75 and
  `nextafter(1,0)` advance on every checked frame, including the wrap case.
- After the fix, the strict Release build and CTest expression
  `^test_(numerics|tonewheel|engine|profile)$` passed **4/4 suites**. The new suite
  took approximately one second in this executor; that is test-run context only.
- No new sanitizer, native audio, long-duration, alternate-rounding or
  cross-platform result is claimed here. The integrator owns combined CI results.

Reproduce from the repository with an out-of-source Release build, build targets
`test_numerics test_tonewheel test_engine test_profile`, then run the CTest
expression above with `--output-on-failure`. Run `test_numerics` directly or use
CTest `-V` to retain the complete numerical report.
