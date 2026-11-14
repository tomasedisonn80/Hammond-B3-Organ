# A24 — Independent native R2 repair review

Actual worker: `/root/w04_a24_motion_independent_review`, wave 4 of the current
reference-refinement session. Owned files are this note and
`reports/A24-motion-independent-review.json`. No production, budget, shared
status, build, CTest log, commit or publication change was made; no worker was
spawned. The root integrator owns acceptance and publication.

## Result

**The identified GCC/Linux source and executable support the frozen R2 numerical
qualification.** Independent review found no blocking defect in the four repaired
arithmetic paths. All **66 original failed inputs** pass when regenerated from
their retained input records; their independently recomputed reference values
match all 66 original reference strings exactly. The six literal reproducer
lines in A16's summary return exactly the recorded final native values.

The final oracle replay passes **7/7 methods, 3,780 native requests**, including
24 timelines / 1,272 queries, 1,152 frozen-grid cases and 1,024 deterministic
semigroup cases (seed `20261114016`). It reports zero failures; every metric and
the complete output stream match A16's retained final native report. The greatest
error/budget fraction is **0.03362431425105119**, in reconstructed frozen-grid
angle. No alignment, rescaling or relaxed budget was introduced.

The separate owner executable passes **174 rejected-call checks, 32 stopped rate
replacements and 327,720 bit-identical sample-state comparisons**, over 131,760
partition calls and 48 zero-frame calls. These are motion-owner checks; they do
not qualify a waveform renderer or actual audio callback.

## Review basis and arithmetic assessment

Read AGENTS, the current scope/checkpoint/assignment material, complete M0–M9
plan, atlas review and rotary scope, frozen numerical and motion documentation,
both motion headers, the complete production implementation, native probe,
acceptance and lifecycle tests, independent Decimal motion implementation, A16's
note and original/subnormal/final reports. The complete native diff is limited
to the arithmetic described below. Admission and publication order are unchanged.

* **Small angle:** the existing alternating polynomial now evaluates `g(z)/z`;
  the caller supplies the other factor as elapsed time. Thus
  `difference * elapsed * (g(z)/z)` is the same analytical contribution as
  `difference * tau * g(z)`, without prematurely squaring tiny `z`. The series
  truncation bound remains below `4e-20` relative for `0 < z < 1/8`; floating-point
  roundoff is independently graded. At zero elapsed the existing exact seed
  return still precedes this path.
* **Extreme decay:** above `z=700`, two `exp(-z/2)` factors preserve a scaled
  subnormal tail that an independently rounded `exp(-z)` could erase. This is
  an arithmetic switch, with no zero-speed threshold. Underflow of the first
  scaled factor or the half exponential cannot hide a representable final
  decaying residual, since the remaining factor is at most one.
* **Minimum elapsed:** for subnormal normalized elapsed, evaluating
  `fma(difference/tau, elapsed, start)` avoids losing the duration before the
  angular acceleration is applied. The omitted quadratic speed term is far
  below minimum binary64 subnormal. The angle still uses the scaled polynomial.
* **Minimum sample fraction:** the special path is restricted to zero residual
  whole frames and subnormal fractional duration. It applies linear speed and
  angle terms per frame before the small fraction; whole seconds were already
  evaluated. At either new linear branch the omitted speed/angle curvature is
  below `1e-607`, versus minimum binary64 subnormal about `4.94e-324`.

The admitted bounds make `z <= 86,400,000`, `abs(difference/tau) <= 200,000`,
`abs(difference*tau) <= 12,000`, and physical displacement at most 17,280,000 rad.
For the fractional branch, `tau*rate` lies between 44.1 and 11,520,000: no zero
denominator or unbounded intermediate is introduced. The existing checked
integer turn addition and canonical phase validation remain in force.
Destinations are published only after successful validation and angle addition;
owner methods retain their candidate-before-publication structure. Work remains
bounded with no added allocation or iteration.

The frozen contract, independent oracle and Engine implementation/header match
HEAD byte for byte. The original and all repaired reports use the same absolute,
relative, semigroup and observable-sign/nonzero budgets. The probe only parses,
invokes native APIs and serializes results; it contains no copied approximation.
The reference independently converges its 80-digit series/exponential rather
than copying the native polynomial. No rotary processing enters Engine.

## Reproduction and identities

Working directory: `/workspace/scratch/1bb6ee17ad7e/Hammond-B3-Organ`.
Observed HEAD: `e4968b2acd37b6f79683704356350070fe2fc329`; it does not identify
the concurrent uncommitted worktree by itself. Existing shared binaries were
used directly, with no rebuild or shared CTest invocation.

```sh
PYTHONDONTWRITEBYTECODE=1 HAMMOND_ROTARY_MOTION_PROBE_EXECUTABLE=/workspace/scratch/1bb6ee17ad7e/build-native/hammond_rotary_motion_probe python3 tests/test_rotary_motion_acceptance.py --report /tmp/A24-motion-oracle.json
../build-native/test_rotary_motion
```

The Python suite reports 0.462 seconds. The 66-case replay used each retained
failure's `inputs` through `request_text`, preserving original IDs and binary64
values; it freshly recomputed each 80-digit reference and graded sign/nonzero
and the unchanged `2e-12*abs(reference)+1e-300` budget. The compact report records
the original report hashes, input IDs, replay stream hashes and literal six-case
requests/results. It references A16's full identical metric report rather than
duplicating it. The original failures remain unchanged: 30 in the first report
and 36 in the subnormal extension.

| Identity | SHA-256 |
| --- | --- |
| Final `src/RotaryMotion.cpp` | `a3f986892078254f6dfae936bbbf1b5e1c4967882d06c13b3b28649f2273cfa1` |
| Native CMake probe | `fccdc98a447f5e51294ba6670d56438bee7ab6914886162311f311f7fa94beb9` |
| Native owner executable | `1bf5df00a00c1e64d6fc8e7163565b274f7874819a0822fd40c47d1caf3f357f` |
| Frozen numerical contract | `4c060088f0718586a7c6810e5c055c652d8924db4474db770237193ab459bd63` |
| Independent reference | `4c8bbcdf279f87aaad5b730d60a82958321ba3c1a92e5318eb5e37b1e83c8b0d` |
| Final 3,780-request stream | `3f29d0f51d0313bd55d7165c0ac8bc5fb74a9e03249a31843cb44d1c8ad6495c` |
| Final native output stream | `d3204e84223dfd65918a9b25ce4c88229f115f062578c1ee87789f7bb0b653ea` |
| Compact A24 report | `3988560c63d82ead219ed46917bc887b9b6ab3241adb613897d5d706a7af6bdc` |

All relevant source/test hashes are retained in the compact report. Actual
compiler is GCC 14.2.0, Linux x86_64/glibc 2.41; the observed motion compile
flags are `-O3 -DNDEBUG -std=c++20 -Wall -Wextra -Wpedantic -Wconversion
-Wsign-conversion -Wshadow -Werror`, without fast-math.

## Concrete follow-up and limits

Root should update `docs/ROTARY_MOTION.md`: its arithmetic-order description
still explains the older `tau*g` evaluation and its final paragraph still calls
R2 qualification the next gate. This documentation follow-up does not invalidate
the retained numerical result.

Later CI must run the same underflow, oracle and owner checks on Windows/MSVC
and AppleClang. Their decimal parsing, exponential and fused arithmetic behavior
has not been executed here. Preserve gradual underflow and prohibit fast-math
or reassociation in qualifying configurations; present CMake warning settings do
not prevent externally supplied `/fp:fast` or `-ffast-math`. An enclosing runtime
that changes the floating-point environment also needs its own qualification.
Require frozen numerical tolerances and same-executable partition identity,
without demanding these Linux output hashes on other platforms.

R3, R4, R5, R6 integration/allocation/deadlines, sanitizers, physical cabinet
motion and specimen fidelity remain separate gates. Once root accepts this R2
slice, continue dependency-ready historical propagation and platform work under
their existing contracts; do not connect this module to the dry Engine.
