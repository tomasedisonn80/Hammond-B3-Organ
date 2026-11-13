# Scanner line state and behavior acceptance

The independent native test in
[`tests/test_scanner_line.cpp`](../tests/test_scanner_line.cpp) passes the state,
analytic-limit and transactional-behavior portion of `scanner-numerics-v1` for
the source snapshot recorded in
[assignment 15](development/2026-11-13-scanner/15-line-state-tests.md).
This is a bounded G3 result. Full G3 also requires the separately assigned
matched-step circuit and warp-matched AC comparisons; G5 requires its own
continuous-time, same-hertz and rotating-output evidence. The
[numerical contract](SCANNER_NUMERICAL_CONTRACT.md) defines those gates, and the
[current handoff](SCANNER_HANDOFF.md) owns their current overall status.

The tested model is `atlas-late-b3-nominal-line-v1`, realized as
`scaled-physical-trapezoidal-scanner-line-v1`. Its documentary basis is the
[supplied atlas](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf), pp. 157-159 and
182-186, and the admitted
[nominal graph](../data/scanner/atlas-late-b3-nominal-v1.json). Passing this test
does not supply winding loss, source/receiver loading, measured component
tolerances, specimen captures or hardware fidelity.

## Independent expectations

The test uses literal source values: eighteen 0.5 H inductors, seventeen 4 nF
capacitors and the final 1 nF capacitor, a 15 kOhm termination, a 22 kOhm chorus
return, and the six divider pairs below. It does not read the generated C++
component arrays or reuse the runtime's coefficient assembly, factorization,
transition matrix or energy helper to construct expectations.

| Tap | Upper resistor, ohms | Lower resistor, ohms | Vibrato DC gain | Chorus DC gain |
| --- | ---: | ---: | --- | --- |
| 1 | 27000 | 68000 | `68/95` | `12463311899/13657495547` |
| 2 | 56000 | 150000 | `75/103` | `12515270267/13657495547` |
| 3 | 39000 | 150000 | `50/63` | `12790466267/13657495547` |
| 4 | 33000 | 180000 | `60/71` | `13006519067/13657495547` |
| 5 | 18000 | 180000 | `10/11` | `146030693737/150232451017` |
| 6 | 12000 | 180000 | `15/16` | `13394885717/13657495547` |
| 7-19 | Not a divider output | Not a divider output | `1` | `1` |

At DC the inductors are shorts and the capacitors are open circuits. The six
divider series pairs and termination give
`Rparallel = 92438660160000/9455738267` ohms. The exact chorus return gain is
`9455738267/13657495547`; vibrato return gain is zero. Input admittance is
`9455738267/92438660160000` A/V for vibrato and
`9455738267/300464902034000` A/V for chorus. These are retained rational
resistor-network answers, not a small nonzero frequency used as a DC surrogate.
Every complex comparison uses the frozen `1e-10 + 1e-9*abs(expected)` bound;
the input-admittance comparison first multiplies both values by 15000 ohms.

For arbitrary physical checkpoints, the test independently applies KCL at the
circuit boundary. With input `u`, first inductor current `i1` and common return
`r`, vibrato has `r=0`; chorus has

```text
r = (i1 + u/95000) / (1/22000 + 1/95000)
Iin = i1 + (u-r)/95000
```

It checks each divider by its two-resistor voltage equation and taps 7-19 by
`r+x6` through `r+x18`. Chorus additionally requires `Iin=r/22000`. This checks
the ground reference, current orientation and moving-return contribution.
It does not independently grade the time evolution of every state coordinate;
the separate matched-step circuit reference owns that comparison.

Stored energy is independently accumulated from physical units using
`sum(0.5*C*x*x + 0.25*i*i)` in `long double`. The production trajectory remains
binary64. Tests also verify the known energy of each single-coordinate initial
state, including the 1 nF exception, and voltage/current sign reversal without
negating energy.

## Executed coverage

The recorded strict GCC 14.2 Release run passed one selected CTest target in
0.56 s. The test uses `TestSupport.h` checks that remain active under `NDEBUG`.
No case was skipped and no production repair was required by this assignment.

| Experiment | Actual coverage and result |
| --- | --- |
| Default and preparation | Zero checkpoint; cold observation at completed-interval count 0; first processed interval at count 1; explicit successful preparation resets; every method requiring preparation returns `NotPrepared` before malformed-argument errors. |
| Research-rate preparation and DC | All 15 host/factor combinations from `{44100,48000,96000} * {1,2,4,8,16}`; both return modes, giving 30 DC responses. This union contains 11 distinct internal rates and does not extend the public Engine host-rate set. |
| DC error | Maximum complex error `1.9008557748667609e-13` across all nineteen taps, common return and dimensionless input admittance. Every response residual and condition estimate passed the frozen bounds. |
| Physical coordinate basis | All 36 coordinates, both signs, two modes and three host rates: 432 paths, each advanced for 64 frames, giving 27,648 processed basis frames. Every state/output was finite and the physical output reconstruction and polarity checks passed. |
| Driven polarity | 1024 samples at each host rate with positive/negative input pairs and repeated return-mode changes; state, taps, current, return, energy and previous-input signs checked. |
| Passive energy | Four prescribed charged states, both modes and three host rates: 24 trajectories and 376,200 frames, each lasting 250 ms. Details below. |
| Stopped rate changes | All nine ordered host-rate pairs after 127 nonzero-history frames; exact preservation of C/L state, previous input and completed count. Both-mode observations before/after were identical and subsequent processing matched a freshly prepared/restored control exactly. |
| Return-mode observation | Both transition directions reconstruct the new algebraic return and KCL without advancing or changing the physical checkpoint. Ground-referenced outputs may change; capacitor differences and inductor currents stay fixed. |
| Rejection transactions | 237 prepared-object rejected calls, with status checks, preserved destination where applicable, and continuation against an untouched clone. These include twelve candidate-energy failures and two counter-overflow failures. Ten additional unprepared calls check precedence and preservation. |
| External frame grouping | Exact outputs/final checkpoints across group sizes 1, 64, 127 and repeating `[1,17,64,3,127,2,31]`, for 1024 driven frames at each host rate: twelve paths. Intervening observations of both modes advance no history. |

The grouping test drives the frame API externally. There is no line-level block,
zero-frame control callback, rotor/depth control or host callback in this API;
the result therefore does not qualify those future interfaces.

## Passive energy evidence

Each fixture starts with previous input zero, and both endpoints of every
processed interval have zero input. The return topology is fixed within each
trajectory. Initial energy is `2e-9 J` for `x1=+1 V`, `5e-10 J` for `x18=-1 V`,
and `2.5e-9 J` for either `i1=+1e-4 A` or `i18=-1e-4 A`. All unlisted
coordinates start at zero.

The permitted per-step increase is `1e-12*Einitial + 1e-24 J`; growth above
the initial energy is bounded by `1e-10*Einitial + 1e-24 J`. Both checks passed
at every step. The maximum **positive** increment, clamped below at zero, was
zero for every trajectory. Final energies are retained below in joules; these
are computational observations, not measured decay targets.

| Rate, Hz | Return | Final, x1=+1 V | Final, x18=-1 V | Final, i1=+1e-4 A | Final, i18=-1e-4 A |
| ---: | --- | ---: | ---: | ---: | ---: |
| 44100 | Vibrato | `2.8251081157097834e-27` | `1.0039546162841046e-28` | `8.9411328914383298e-28` | `1.6109367269850059e-27` |
| 44100 | Chorus | `1.3122264356150478e-26` | `1.0466039514035091e-27` | `2.5276030499916156e-27` | `1.6802239252088292e-26` |
| 48000 | Vibrato | `8.9145912516772513e-28` | `3.1623540822582485e-29` | `2.8098519914150722e-28` | `5.0620584577684396e-28` |
| 48000 | Chorus | `4.4617293452908281e-27` | `3.5663869948587658e-28` | `8.5777563138636155e-28` | `5.7182262345570223e-27` |
| 96000 | Vibrato | `3.3356778923444644e-30` | `1.1857110799747064e-31` | `1.054598913333375e-30` | `1.8999207075598236e-30` |
| 96000 | Chorus | `2.423375649447886e-29` | `1.9350216862994481e-30` | `4.6681870892660888e-30` | `3.106757238374487e-29` |

## Bounds and rejection evidence

The public bounds are computational admission limits: finite input/history
within ±64 V, capacitor differences within ±65536 V, individual currents within
±2 A, and total reactive energy at most 1 J. The joint energy limit can reject
a state whose individual coordinates all satisfy their limits. In particular,
the loose capacitor coordinate limit is not a promise that a 65536 V charged
capacitor satisfies the energy limit. The test admits the exact 1 J boundary
with `i18=±2 A` and admits both ±64 V input/history endpoints.

Rejected arguments include NaN, both infinities, unsupported rates, invalid
enum values, Nyquist and out-of-range response frequencies, and the immediately
representable values outside each input/state coordinate bound. Every one of
the 37 floating checkpoint fields is checked independently for nonfinite data
and both signs outside its bound. A joint-energy rejection uses individually
legal `+1.5 A` and `-1.5 A` currents, whose total energy is 1.125 J.

A separate process-path rejection starts with `i10=±1.999999999 A`, other
coordinates and previous input zero, and completed count 127. A legal ±64 V
input produces an inadmissible next energy at each host rate and return mode.
An admitted half-amplitude process verifies by linear scaling and independent
physical-energy accumulation that the full candidate exceeds `1 J + 1e-10 J`,
while every individual C/L coordinate remains in bounds. This establishes a
finite forcing margin rather than relying on last-bit rounding at 1 J. The
failed full-amplitude process leaves state and destination intact; its next
41 admissible frames match an untouched control exactly.

Overflow checks restore count `UINT64_MAX-1`, successfully complete the last
representable interval and reject the next process with `TimelineOverflow`.
Count `UINT64_MAX` is itself a valid restorable/observable checkpoint. To
compare successful continuation after saturated-count rejection, the test
restores the same physical endpoints at a usable count in the two controls.
It does not wrap the counter or infer a valid process interval beyond its limit.

## Reproduce and continue

Use a coherent frozen source/header snapshot, C++20, CMake, Ninja and the
project's Python compiler prerequisites. From the repository root:

```sh
cmake -S . -B build/scanner-state -G Ninja -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON -DCMAKE_INSTALL_DATADIR=share
cmake --build build/scanner-state --target test_scanner_line --parallel 2
ctest --test-dir build/scanner-state -C Release -R '^test_scanner_line$' --output-on-failure --no-tests=error
```

The test prints all 24 passive final energies and aggregate counts; CTest
retains them in `Testing/Temporary/LastTest.log`. Its source and tested input
hashes, exact executed commands and tool versions are in
[the assignment evidence](development/2026-11-13-scanner/15-line-state-tests.md).
The explicit install-data directory also makes repeated configuration robust
with the CMake 4.4.4 environment used during this assignment.

Next, compare the same frozen runtime against the independently assembled
matched-step circuit recurrence on all 36 signed state bases, and against the
full frozen AC grid with both warp-matched and same-hertz results retained.
Converged transient, rotor, rate/filter policy, allocation, performance, Engine
rollback, native/DAW qualification and physical acquisition remain separate
work. A change to runtime, graph, numerical contract or tested behavior requires
fresh affected evidence; these recorded results cannot qualify a later revision
solely because its model name is unchanged.
