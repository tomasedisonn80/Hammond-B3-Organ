# A19 — Independent native R3 numerical acceptance

Actual worker: `/root/w04_a19_rotary_independent_oracle`; wave 4, 14 November
2026. Owned the propagation batch probe, Python acceptance suite, four A19 JSON
reports and this note. Read the standing instructions, current scope/checkpoint,
complete plan, frozen numerical/propagation contracts, native implementation and
original independent reference. No production changes, budget changes, commits
or publication. Observed HEAD: `e4968b2acd37b6f79683704356350070fe2fc329`;
the accepted numerical sources were uncommitted and are separately hashed.

## Independent method and fixtures

The C++20 adapter owns stable immutable segment storage and exposes native
geometry, histories and roots through one persistent stdin/stdout process. It
contains no oracle or root approximation. Python uses a converged 100-digit
Decimal sine/cosine series and Cartesian square root for geometry/residual
grading. Its separately implemented bisection queries native history in batches,
isolating solver error on identical motion. The original independent 80-digit
motion timeline and offline solver then quantify motion's separate contribution.
Both offline solvers allow 96 bisections, exclude two endpoint evaluations from
that count and use `5e-15 s` internally before the frozen `1e-14 s` residual gate.
Every native endpoint/midpoint counts toward the unchanged 48-evaluation limit.

Executed 1,440 geometry fixtures, 4,466 native roots, 1,728 history queries and
seven full-orbit/cross-field rejection fixtures. The complete radius/sign/phase/
sound-speed/speed grid includes both horizontal sides, exact above/below
clearance, tangent radial motion and maximum-distance geometry. Historical
fixtures cover all four rates, fast acceleration/decay, ties and repeated
commands, both sides of earlier command arrivals, startup, and fractional samples
through the 86,400-second endpoint. Ninety-six receiver pairs borrow the same
owning history and produce distinct emission times. Two four-point derivative
stencils retain convergence tables across six step sizes and four root targets.

## Commands and actual outcomes

Working directory: `/workspace/scratch/1bb6ee17ad7e/Hammond-B3-Organ`.
Compiler: Debian GCC 14.2.0-19. Direct compilation passed with warnings as errors:

```sh
g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion -Wshadow -Werror \
  -Iinclude src/RotaryMotion.cpp src/RotaryPropagation.cpp \
  tests/probes/rotary_propagation_probe.cpp -o /tmp/a19-rotary-propagation-probe
python3 tests/test_rotary_propagation_acceptance.py \
  --probe /tmp/a19-rotary-propagation-probe \
  --report docs/development/2026-11-14-reference-refinement/reports/A19-r3-isolated.json
python3 tests/test_rotary_propagation_acceptance.py \
  --probe /workspace/scratch/1bb6ee17ad7e/build-native/hammond_rotary_propagation_probe \
  --report docs/development/2026-11-14-reference-refinement/reports/A19-r3-native.json
```

The first isolated run passed six methods in 12.682 seconds, with a harness
stdout-close warning retained in its outcome. Closing that stream removed the
warning: final isolated **6/6 passed in 13.040 seconds**; root-built CMake Release
**6/6 passed in 12.950 seconds**. Each run used **124,673 requests in 46 batches
and one native process**. Their numerical output hashes match. No numerical
failures occurred. An initial shared-build invocation used an incorrect in-repo
path and failed the required-probe check; correcting it to the sibling build
directory produced the retained native pass. The explicit missing-probe check
also exited 1 with zero skipped gates, as required. No shared build or CTest
mutation was performed by this worker.

| Quantity | Maximum observed | Frozen limit |
| --- | ---: | ---: |
| Identical-state geometry distance | `2.273e-15 m` | `2e-12 m` |
| True native residual | `9.980e-15 s` | `1e-11 s` |
| Identical-motion delay difference | `1.484e-14 s` | `2e-11 s` |
| Identical-motion frequency-ratio difference | `4.979e-12` | `2e-10` |
| Independent oracle residual | `4.997e-15 s` | `1e-14 s` |
| Native total evaluations | 41 | 48 |

Separate maximum motion phase error was `1.419e-9 rad`; its
`radius*abs(phase_error)/(c*(1-beta))` root bound was `2.600e-12 s`.
Total independent-motion delay discrepancy was `2.487e-12 s`. Both offline
solvers used at most 40 bisections. All maximum/RMS errors and exact worst
coordinates remain in [the native report](../reports/A19-r3-native.json).

## Identities and next task

The native executable SHA-256 is
`0dc6fc73e98c40d0c20003dfaa22a435749f180d6cd25cde159863a874cd0e59`.
Propagation source is
`dcc36819747b8d215130c5031a955e4b00af29a114832d0bf273ca60eaaf0c2e`;
motion source is
`a3f986892078254f6dfae936bbbf1b5e1c4967882d06c13b3b28649f2273cfa1`.
Reports retain every relevant source/oracle/contract hash and the complete batch
input/output identities; source remained unchanged during qualification.

Root should run the wired coherent CTest gates and integrate A16/A17/API evidence
before accepting R3. Next design: R4 waveform history/interpolation and
transactional rendering. These numerical primitives do not close R4–R6,
real-device timing, audible policy or physical cabinet fidelity.
