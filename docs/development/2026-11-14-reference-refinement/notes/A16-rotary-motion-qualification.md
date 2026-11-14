# A16 — Native R2 motion qualification and observed underflow repair

Actual worker: `/root/w03_a16_rotary_motion_qualification`, wave 3 of the newly requested reference-refinement session. This is one actual assignment; no historical worker is recounted. Root owns CMake, shared status, the manifest and publication. No commit, push or additional worker was created by A16.

## Result and owned boundary

The named **native R2 numerical and owner checks pass** on the source and binaries identified below. The final batched oracle run executes **3,780 requests in one native process**, including 24 multi-query timelines, and passes seven Python methods. The compiled owner suite separately passes 174 transactional rejection checks, 32 stopped rate replacements and **327,720 bit-identical sample-state comparisons**. Final focused CTest passes **2/2 in 0.56 seconds** (native 0.03 s, Python 0.53 s). The report-producing Python replay passes seven methods in 0.495 s.

Owned additions are `tests/probes/rotary_motion_probe.cpp`, `tests/test_rotary_motion_acceptance.py`, `tests/test_rotary_motion.cpp`, this note and the `A16-r2-*.json` reports. After observed failures were reported, root explicitly authorized the narrow scaling corrections in `src/RotaryMotion.cpp`. No parameter, saved state, Engine, native UI, header/API or oracle was changed. Root wired `hammond_rotary_motion_probe` and the `HAMMOND_ROTARY_MOTION_PROBE_EXECUTABLE` environment variable; the existing CMake glob supplies `test_rotary_motion`.

Read the current AGENTS/scope/checkpoint and actual assignment, complete project plan, rotary numerical/motion/reference and propagation contracts, the A04 source review, A10 API review, both motion headers, the complete motion implementation and independent reference. Source HEAD observed in this worktree was `e4968b2acd37b6f79683704356350070fe2fc329`. Other agents' concurrent files were preserved; HEAD alone does not identify this uncommitted worktree. The hashes below identify the exact relevant inputs.

## Independent experiments

The fixtures retain all frozen budgets without alignment, rescaling or raw-turn equality at epsilon-close wraps. Binary inputs are converted to Decimal with 120 significant digits, leaving 40 guard digits beyond the oracle. This avoids the oracle's 256-digit scalar representation cap for very small binary64 numbers. The imported oracle remains the existing independently converged series/exponential implementation at **80 digits**; the test explicitly rejects an oracle with less precision. It does not copy the native finite polynomial. True high-precision pi reconstructs angle with integer turns subtracted before conversion.

| Experiment | Final coverage |
| --- | ---: |
| Complete frozen sign/tau/time/regime grid | 1,152 cases: both signs; six taus; zero plus every power from 1e-12 through 1e2; rest, two acceleration cases, equality and two decays |
| Extra tiny acceleration, long decay, subnormal elapsed/increment | 516 cases, including observable-positive checks in addition to relative budgets |
| Full 86,400-second epoch, wraps and kernel-switch boundaries | 210 cases |
| Deterministic native split-interval semigroup | 1,024 cases; seed `20261114016`; total time at most 60 s |
| Sample positions at all four rates | 824 cases, including late epoch anchors, small/nonbinary fractions and minimum-positive fractions at frame zero |
| Constant-speed mathematical prehistory | 30 physical-time cases, plus sampled negative positions |
| Command reversal, repeated/tied commands and epoch-limit timelines | 24 timelines with 1,272 independently graded queries |

The synthetic fixture identity is `native-r2-synthetic-grid-v1`; its exact serialized native request stream has SHA-256 `3f29d0f51d0313bd55d7165c0ac8bc5fb74a9e03249a31843cb44d1c8ad6495c`. These parameter fixtures are not specimen measurements or a replacement for the separately admitted JSON acoustic profile.

The native owner suite exercises invalid rates, profile/state/segment fields, directions, commands, times, fractions, epoch limits, history coverage and checked turn overflow, with preserved owners/destinations on rejection. It verifies query immutability, reset versus current-state rate replacement, original reset seed retention, constant-speed negative history after commands, unchanged-command anchoring, target-minus-current-speed tau selection and one-day endpoint admission. Exact partition comparisons use every rate and both signs, blocks of 1/1024/4096 and irregular patterns, end-boundary/next-zero tied-command ordering, **131,760 block calls and 48 zero-frame calls**. This is a test wrapper around the motion owner; it does not implement or qualify R4 waveform transactions.

## Original failures retained, then repaired

The first complete batch against the original motion source retained **30 failures** in [A16-r2-original.json](../reports/A16-r2-original.json). Every ordinary frozen numerical budget already passed, but observable positive values were erased. Twenty-four failures were long-decay speed and six were tiny angle increments. Original source SHA-256: `9c8c98dc66a66088d39b43a52d025289d4dd241ebba583bd4200aba3b539ac4d`; original isolated probe: `50b9d021fbd702fad37667484bdd7f8527694383192f18fd3c25ceba0cc399b1`.

| Exact example | Original outcome | Independent reference | Final native outcome |
| --- | --- | --- | --- |
| w0=200, target=0, tau=1, h=746 s | Speed zero | 2.07656961903165648e-322 rad/s | 2.08e-322 rad/s |
| w0=0, target=200, tau=60, h=1e-161 s | Increment zero | 1.66666666666666676e-322 rad | 1.7e-322 rad |

The first repair factors `tau*g(z)` as `elapsed*(g(z)/z)`, so `z*z` cannot underflow before the scale factor is applied. For `z>700`, it evaluates the same decaying residual using two `exp(-z/2)` factors; a separately underflowing `exp(-z)` no longer erases a representable scaled tail. The threshold chooses arithmetic only; it is not a stop threshold. Its complete original 3,388-request replay passes and is retained in [A16-r2-repaired-isolated.json](../reports/A16-r2-repaired-isolated.json), identifying intermediate source `ec8d3feab44704e05816a896c6674c0a54a31da00eb5b2d5fe82fefc403a90ea`.

A concrete boundary audit then found division of minimum-positive elapsed time by tau could itself become zero. Root requested the corresponding minimum-positive `SamplePosition` fraction check: division by sample rate had the same issue. The expanded experiment retains **36 further failures against that intermediate source** in [A16-r2-subnormal-time-original.json](../reports/A16-r2-subnormal-time-original.json): eight physical-time speeds, 24 fractional-time speeds, and four positive constant-motion phases. The first report remains unchanged.

For subnormal normalized elapsed time, speed now evaluates the initial slope times elapsed before division can erase it. For a subnormal fractional sample tail with no whole residual frame, the helper scales the linear speed/angle terms per frame before applying the fraction. Higher-order curvature at these magnitudes is below binary64 representability; the frozen absolute allowance and explicit positive-result check both remain unchanged. For minimum binary64 elapsed, target 200 and tau 60, native speed is now `1.5e-323` versus the oracle's `1.64688548613748848e-323`. For the minimum fraction at 44,100/48,000 Hz, target 200 and tau 0.001, native speeds are `2.5e-323` / `2e-323`, versus `2.24066052535712714e-323` / `2.05860685767186056e-323`. A constant 200 rad/s at fraction `1e-319`, 48,000 Hz, preserves phase `4.15e-322` rather than zero.

[A16-r2-summary.json](../reports/A16-r2-summary.json) retains exact stdin reproducer lines, observed final native values, 80-digit reference results, all three source revisions and the individual report hashes. [A16-r2-final-isolated.json](../reports/A16-r2-final-isolated.json) retains the final direct compilation replay. Final shared-build numerical results are [A16-r2-native.json](../reports/A16-r2-native.json); owner counts/build details are [A16-r2-lifecycle.json](../reports/A16-r2-lifecycle.json). Earlier reports keep their earlier fixture counts and executable/source/test identities. The late-epoch fraction and subnormal-time additions are explicitly additional cases, not retroactive claims about the first run.

## Measured errors

Each report contains maximum/RMS values and exact worst-case coordinates for every metric. The last column is the greatest error/budget ratio for that metric, not necessarily the ratio at the largest absolute error.

| Metric | Maximum absolute error | RMS error | Largest budget used |
| --- | ---: | ---: | ---: |
| Frozen grid speed (rad/s) | 1.30860295e-14 | 4.19066781e-15 | 0.100662% |
| Frozen grid increment (rad) | 6.5579497e-12 | 2.80112732e-13 | 2.60251% |
| Day/wrap increment (rad) | 7.45058064e-10 | 1.07358686e-10 | 1.67816% |
| Sample-position reconstructed increment (rad) | 1.41867913e-09 | 4.25192607e-10 | 2.05234% |
| Native semigroup angle difference (rad) | 9.08606523e-13 | 5.43191912e-14 | 0.454303% |
| Native semigroup speed difference (rad/s) | 2.84217094e-14 | 7.35907895e-15 | 0.142109% |

For example, the largest frozen-grid increment error occurs at w0=0, target 200, tau 60 s, h=600 s, direction -1. The largest semigroup angle discrepancy occurs at w0=179.31772511070272, target=198.860149773988, tau=46.2635603335506, direction +1, intervals 26.21796875810181 and 15.650066692493525 s. No fitted phase or time shift is applied.

## Reproduction and exact identities

Working directory: `/workspace/scratch/1bb6ee17ad7e/Hammond-B3-Organ`. Shared setup is GCC 14.2.0, C++20 Release (`-O3 -DNDEBUG`), warnings including conversion/sign-conversion/shadow treated as errors, standalone ON, MIDI OFF and VST3 OFF. Dependencies/build tree were reused after coordinating with root/A14/A15/A17. The independent direct probe used `g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Werror -I include tests/probes/rotary_motion_probe.cpp src/RotaryMotion.cpp -o /tmp/a16-rotary-motion-probe-final`.

```sh
../build-tools/cmake/data/bin/cmake --build ../build-native --target hammond_rotary_motion_probe test_rotary_motion -j2
../build-tools/cmake/data/bin/ctest --test-dir ../build-native --no-tests=error -R '^(test_rotary_motion|python_test_rotary_motion_acceptance)$' --output-on-failure
PYTHONDONTWRITEBYTECODE=1 python3 tests/test_rotary_motion_acceptance.py --probe ../build-native/hammond_rotary_motion_probe --report docs/development/2026-11-14-reference-refinement/reports/A16-r2-native.json
../build-native/test_rotary_motion
```

The Python gate fails if the native executable is missing; there is no skip or Python-only fallback. One stdin batch handles all scalar cases. Final probe SHA-256: `fccdc98a447f5e51294ba6670d56438bee7ab6914886162311f311f7fa94beb9`. Final owner-test executable SHA-256: `1bf5df00a00c1e64d6fc8e7163565b274f7874819a0822fd40c47d1caf3f357f`. The native output stream hash is `d3204e84223dfd65918a9b25ce4c88229f115f062578c1ee87789f7bb0b653ea`.

| Relevant input | SHA-256 |
| --- | --- |
| `include/hammond/RotaryTypes.h` | `b27ce4934188c24ebe557469fa5191dd7cdcd98a1c3fdbe274b0d7585e4578b4` |
| `include/hammond/RotaryMotion.h` | `7bc81331f84b7ce490bf9047114336e633f3da91a39bbfd2a13e3fd406f61d36` |
| `src/RotaryMotion.cpp` | `a3f986892078254f6dfae936bbbf1b5e1c4967882d06c13b3b28649f2273cfa1` |
| `tools/rotary_reference.py` | `4c8bbcdf279f87aaad5b730d60a82958321ba3c1a92e5318eb5e37b1e83c8b0d` |
| `tests/probes/rotary_motion_probe.cpp` | `2af57d1ade547be7d8ea97c5c272e8bff7b76490f1b5eaffa718a76bb195848e` |
| `tests/test_rotary_motion_acceptance.py` | `c29d2856b456dd485b81edfe7481c7cce450c674a503e15c5c35e7e19945d366` |
| `docs/ROTARY_NUMERICAL_CONTRACT.md` | `4c060088f0718586a7c6810e5c055c652d8924db4474db770237193ab459bd63` |
| `docs/ROTARY_PROPAGATION_CONTRACT.md` | `0834909ad8ea4b2b9696f0047d739d03976da3adb4a2eb48f2b7556737bccdcc` |
| `tests/test_rotary_motion.cpp` | `e8095db59203e88023bd4d3cd56b75882b6cf88b111b3bf8af77574fa1de2a82` |

`git diff --check` passes. The final source hash was communicated to A17 and A19, and the shared build was released to root after the targeted checks. Reconstructed native histories must use their qualified source revision; the algebraic reordering can alter last-bit rounding, so this is not a claim of cross-revision bit identity.

## Limits and next concrete task

This qualifies the identified nominal motion slice and finite workloads on this GCC/Linux build. It does not close R3, R4, R5, R6 integration, allocation/deadline/sanitizer/platform gates, hardware fidelity or measured cabinet motion. The missing physical M5/M6/M7 evidence, scanner gate and complete M0–M9 plan remain separate.

A19 should independently inspect the probe/oracle boundaries, frozen budgets and actual source identities, then qualify the immutable-history retarded-path implementation against its R3 contract. Root should integrate accepted R2 evidence into shared status and published source. Continue to R4 only under a reviewed waveform/history/transaction contract; no motion or propagation code is connected to the dry Engine by this assignment.
