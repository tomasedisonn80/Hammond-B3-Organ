# Assignment 15 - independent scanner state tests

## Identity, source and ownership

- Actual worker: `/root/w03_a15_line_state_tests`, assignment 15 of 60, wave 3 of 10.
- Owned files: `tests/test_scanner_line.cpp`, `docs/SCANNER_LINE_ACCEPTANCE.md`,
  and this note. No production source, CMake, shared status or historical ledger
  was edited. No child agent was dispatched and no git mutation was performed.
- Initial local `HEAD` and observed remote `main` were
  `6dc0702d5473912268e8af8f852b9b9984198ef3`, committed tree
  `a4f1d4b300de236436e22b748b1d4c46ed501ceb`.
- The integrating agent advanced the shared checkout during this assignment.
  At final execution on 13 November 2026, approximately 19:18 UTC, local `HEAD`
  was `80ea8cd2d7febe12fc4dd382e475a00ff4181eac`, committed tree
  `d98d9baf666f048629f5c817ed0f040b215df0e4`.
- The new scanner source/header and this test were uncommitted during the run.
  Those commit IDs alone do not identify the tested scanner implementation;
  its actual file hashes are retained below. Agent 13 explicitly declared the
  production header/source stable before the first compilation. Both were
  compiled together with the test in a fresh isolated build directory; no old
  library was linked against a later header.

Read the standing `AGENTS.md`, current status/next steps/handoff, plan and source
review context, the complete frozen
[numerical contract](../../SCANNER_NUMERICAL_CONTRACT.md), and atlas pp. 157-159
and 182-186. The session's dedicated source readers own the complete PDF review
and primary-source verification. This assignment does not claim another full
500-page reading or any physical acquisition.

## Work and independent expectations

Implemented native state and behavior tests against the frozen public API of
agent 13. Exact rational DC answers are derived from literal documented
resistors. Arbitrary-state observations are checked by an independent circuit
boundary KCL calculation, the two-resistor divider equations and physical
capacitor differences. Energy is accumulated independently from literal C/L
values in `long double`. None of these expectations reads generated component
arrays or reuses runtime matrix assembly, factorization, transition operators
or energy calculations.

The test covers:

- Cold/default state, preparation reset, all allowed host/factor preparations,
  frame-count origin, zero-drive output and `NotPrepared` error precedence.
- Both return modes' nineteen exact DC tap gains, common return, signed input
  admittance, response nonmutation and the frozen residual/conditioning bounds.
- All 36 physical basis coordinates with both signs, both modes and all three
  host rates, each advanced for 64 frames. Known initial capacitor/inductor
  energies, finite reconstruction, signs and common-return KCL are checked.
- Positive/negative driven input symmetry, changing return modes and preserved
  previous-input sign.
- The frozen four charged-state 250 ms zero-input energy experiments, checking
  every step against both energy-growth budgets and printing every final energy.
- All nine ordered stopped host-rate changes, both return observations after
  precharge, exact physical checkpoint preservation and exact future frames
  against independent preparation/restoration at the destination rate.
- NaN, infinities, invalid modes/rates/frequencies, every checkpoint field's
  nonfinite and immediately out-of-bound values, joint-energy rejection,
  inclusive 1 J and ±64 V boundaries, and usable/saturated frame counts.
- Twelve deterministic next-candidate energy rejections: `i10=±1.999999999 A`,
  previous input zero, completed count 127, then input ±64 V, at all host rates
  and both modes. An admitted half-amplitude step verifies by linear scaling
  that the rejected full candidate exceeds `1 J + 1e-10 J` while each individual
  C/L coordinate remains legal. The energy expectation uses physical units,
  not the producer's energy helper. This is admission-path evidence, not an
  independent continuous-time trajectory reference.
- Exact state/destination preservation and 41 subsequent valid frames against
  an untouched control after applicable rejection paths. Overflow continuation
  restores the same physical checkpoint at a usable frame count before comparing
  against a control that did not experience a rejected process call.
- Exact externally driven frame grouping at sizes 1, 64, 127 and repeating
  `[1,17,64,3,127,2,31]`, with intervening nonadvancing observations. The line
  has no block/zero-frame control API, so this does not claim host callback
  transactional qualification.

The companion [acceptance report](../../SCANNER_LINE_ACCEPTANCE.md) retains
the actual rational answers, all 24 final energies, bounds, API scope and next
dependencies. Test checks use `TestSupport.h` and remain active in Release.

## Executed setup and commands

Working directory: `/workspace/scratch/1742da7072be/Hammond-B3-Organ`.
Isolated build: `/workspace/scratch/1742da7072be/a15-build`.
The integrating session had already installed the required build tools; this
worker added no dependency. Observed tools:

| Tool | Observed version |
| --- | --- |
| C++ compiler | Debian GCC 14.2.0-19 |
| CMake | 4.4.4 |
| Ninja | `1.13.2.git.kitware.jobserver-pipe-1` |
| Python compiler prerequisite | 3.12.14 |
| Language/optimization | C++20, `-O3 -DNDEBUG` |
| Warnings | `-Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror` |

The actual configure command used a fresh directory:

```sh
PATH=/workspace/scratch/1742da7072be/build-tools/bin:$PATH cmake -S . -B /workspace/scratch/1742da7072be/a15-build -G Ninja -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
```

The test target and required filtered acceptance gate were then built/run:

```sh
PATH=/workspace/scratch/1742da7072be/build-tools/bin:$PATH cmake --build /workspace/scratch/1742da7072be/a15-build --target test_scanner_line --parallel 2
PATH=/workspace/scratch/1742da7072be/build-tools/bin:$PATH ctest --test-dir /workspace/scratch/1742da7072be/a15-build -C Release -R '^test_scanner_line$' --output-on-failure --no-tests=error
```

The first strict build and its initial state tests passed. Subsequent runs
graded the added numerical-boundary, detailed energy-reporting and untouched
overflow-continuation cases. The **final source identified below passed 1/1
selected CTest target in 0.56 s**, exit 0. No failed/skipped test or production
defect was observed. The elapsed time is ordinary test-run evidence; it is not
a Release callback benchmark or deadline/headroom claim.

A small temporary diagnostic in the isolated build explored candidate-energy
rejection from large legal interior-inductor states. It compiled/ran successfully
and guided the retained regression fixture. Its diagnostic results are not
substituted for the final regression assertions.

Fresh default configuration succeeded. CMake 4.4.4 recorded an empty cached
`CMAKE_INSTALL_DATADIR`; agent 13 separately reported that later explicit
reconfiguration can reject that empty value under the existing project check.
No such reconfiguration failure occurred in this worker's commands. The
companion's future reproduction command explicitly sets
`-DCMAKE_INSTALL_DATADIR=share`. After this worker's final execution, the integrator
reported fixing the shared repeated-configuration issue and independently
rerunning this target successfully in its own build. Those later shared edits
are outside the CMake hash and worker-run timing recorded here.

The final test output retained in `a15-build/Testing/Temporary/LastTest.log`
includes:

```text
scanner line state acceptance passed
dc_responses=30 maximum_dc_complex_error=1.9008557748667609e-13
basis_paths=432 energy_paths=24 energy_frames=376200
maximum_zero_drive_energy_increase_joules=0 maximum_final_energy_joules=1.6802239252088292e-26
retune_pairs=9 rejected_calls=237 external_partition_paths=12
```

The 237 prepared rejections comprise 8 invalid inputs, 3 invalid-mode calls,
20 invalid prepare/retune calls, 6 invalid response frequencies, 111 nonfinite
checkpoint fields, 74 immediately out-of-bound checkpoint fields, 1 joint-energy
restore, 12 candidate-energy processes and 2 saturated-counter processes.
Ten additional unprepared calls cover valid/malformed argument precedence.

All 24 energy trajectories reported zero positive energy increments. No final
energy was omitted: the companion's six-row table contains all four fixtures
for both modes and all three rates. The maximum DC error includes the
dimensionless `15000 ohms * input_admittance` quantity.

## Tested source identities

| Tested input | SHA-256 |
| --- | --- |
| `include/hammond/ScannerLine.h` | `c249f7c5556d6a6c8c58978928f0b860be442cb1188d35e49c59575729af00c7` |
| `src/ScannerLine.cpp` | `4280db3caa3f7aa225c58a0fa64ec4ca31add55ab8bb46a27aca2deba4544336` |
| `tests/test_scanner_line.cpp` | `7f5fb41717258e131b3649449d131a93510546ee8024643ab9e527133231efa0` |
| `tests/TestSupport.h` | `8869acab1e7492699b656984c7b24eb6d33f09dad6f989814a8a0c04e3c86be5` |
| CMake project | `5450e69f593af64c5cb714b0e462d3ba2c31720531c699684cc85095dfdcfdb0` |
| Graph compiler | `56c60cf511144d552fdeb2708711b32469f350593b391c7619ebb92b41b6dd7e` |
| Nominal authoring graph | `1d236be5e6b63e938a9f147808386173949d167e09aee8e902c55002e4ea4604` |
| Built `generated/hammond/generated/ScannerLineData.h` | `d508e3856e637a8e107364ad2a8fed09893a2e50ae05d99db3d4b3da37a5a082` |
| `scanner-numerics-v1` contract | `3999a3a409d397401e135e8285704092bad130911468802370bf6da404d58ff9` |

The nominal line uses trapezoidal endpoint forcing with `kappa=2*sample_rate`
and no prewarp. A checkpoint is the previous endpoint with physical C/L state,
previous input and completed-interval count. This test applies no fitted gain,
polarity, phase, delay or one-frame correction. Rotor phase and resampling
latency are absent from this line API.

`git diff --check` passed. Because ordinary diff checking omits untracked files,
the three owned files were also checked directly for trailing whitespace and
final newlines; all relative Markdown links resolved. The production/test
hashes above were rechecked after documentation completion and were unchanged.

## Limits and next dependency

This worker supplies the G3 analytic/state/transaction evidence slice. It does
not independently solve the full matched-step recurrence, grade the positive
282-frequency AC grid, establish continuous-time convergence, or select a G5
rate/filter policy. The 432 basis paths here check finite physics, signs and
reconstruction; a separate independent recurrence must still compare their
state trajectories under the frozen contract.

The next dependency is the independent circuit-reference comparison against
this frozen runtime and its actual process path, retaining all required bins,
both return modes, all coordinates, warp-matched and same-hertz errors, and the
declared fixed-scale transient convergence evidence. Rotor/depth controls,
allocation instrumentation, performance, Engine/native rollback, host/device
qualification and physical acquisition belong to separate assignments/gates.

The integrator owns coherent full-suite qualification, shared current status,
the actual assignment manifest, commit and push. This worker makes no claim
that the entire repository was tested, that main was published by this worker,
or that the mathematical model is a measured scanner.
