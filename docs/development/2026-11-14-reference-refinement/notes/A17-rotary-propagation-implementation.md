# A17 — Native historical propagation implementation

Actual worker: `/root/w03_a17_rotary_propagation_impl`; wave 3, 14 November 2026.
Owned files: `include/hammond/RotaryPropagation.h`, `src/RotaryPropagation.cpp`,
`tests/test_rotary_propagation.cpp`, and this note. Root retains shared build,
documentation, CMake and publication ownership. The observed repository HEAD
after qualification was `e4968b2acd37b6f79683704356350070fe2fc329`; the new files
were uncommitted. Exact source hashes below identify the tested worktree.

## Implemented behavior

Read the standing instructions, current scope/checkpoint, complete accepted
propagation API, frozen numerical contract, native motion implementation and
independent Decimal/Cartesian oracle. Added the bounded borrowed history and
prepared direct-path primitives without Engine, parameter, state or audio-path
changes. Histories admit 1–4,097 immutable canonical segments, exact native
continuity, the complete covered endpoint, and all four rates. Queries preserve
negative startup motion and select command anchors with at most 13 binary-search
comparisons. Every failure stages state and leaves existing objects/outputs intact.

Path admission checks the complete orbit and the actual epoch seed's speed.
Solving subtracts only local delay from split sample positions, retaining
fractional resolution through the full day. The analytical bracket is widened
only by the specified 32-ulp distance allowance. Both endpoints and every
midpoint count toward the 48-evaluation cap. The chosen cached evaluation is
published with emission time, residual, radial speed, frequency ratio and pressure
gain; no extra final evaluation or algorithmic latency is inserted.

## Executed verification

Working directory: `/workspace/scratch/1bb6ee17ad7e/Hammond-B3-Organ`.
Compiler: Debian GCC 14.2.0-19, C++20, optimized build, warnings as errors.
Waited for A16's scaling repair to become stable before coherent compilation:

```sh
g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion -Wshadow -Werror \
  -Iinclude -DHAMMOND_TEST_PROFILE='"unused"' -DHAMMOND_SOURCE_DIR='"."' \
  src/RotaryMotion.cpp src/RotaryPropagation.cpp tests/test_rotary_propagation.cpp \
  -o /tmp/a17-propagation-tests
/tmp/a17-propagation-tests
```

Compilation and the author executable passed: **65,664 history queries,
162 rejection/transaction checks, 369 solved paths**. Coverage includes all
rates/signs, maximum segment capacity, exact/between-anchor queries, seed and
continuity failures, invalid fields, covered and epoch endpoints, turn overflow,
unchanged commands, replacement of tied anchors, view-copy lifetime with valid
storage, startup, positive-time command-crossing roots and day-end fractions.
Geometry tests check coordinate/sign conventions, output alias rejection and
input/output staging. Stationary analytical paths include the exact clearance
and maximum-distance limits. Independent long-double constant-speed Cartesian
bisection cases exercise radius and Mach boundaries.

Maximum constant-speed delay discrepancy was `1.0403136685432912e-14 s`;
maximum retained residual was `9.4906721370691116e-15 s`; maximum total
evaluations was **41**. No shared build directory was used. The executable
SHA-256 is `c036893b1487d7f1da883e53a8126b207890a6267d1720a106dd2ec93dbd791f`.

| Tested source | SHA-256 |
| --- | --- |
| `RotaryPropagation.h` | `c304a1ac99eed6e6e3f80b5107d026880aeb2b5b18499af0a6a7ed3018521a4a` |
| `RotaryPropagation.cpp` | `dcc36819747b8d215130c5031a955e4b00af29a114832d0bf273ca60eaaf0c2e` |
| `test_rotary_propagation.cpp` | `3736361b538ebc8e7f2a5d64af4e96293628aa384c3ce44a773f9f00fa5205e9` |
| A16's `RotaryMotion.cpp` | `ec8d3feab44704e05816a896c6674c0a54a31da00eb5b2d5fe82fefc403a90ea` |

## Next gate and limitations

The next worker must independently grade the complete R3 geometry/root fixture
against the 80-digit motion and separately bounded Cartesian oracle, preserving
motion-phase and solver contributions, all source identities, worst coordinates,
receiver-specific emissions and derivative convergence. Root must build and run
the discovered CMake target coherently. Allocation and sanitizer qualification
remain separate; this author suite does not close R3 by itself, R4–R6, host/device
timing or physical cabinet fidelity. Backing segment storage must remain alive,
stationary and immutable for every view/path copy. Streaming history ownership,
waveform interpolation and rendering remain the subsequent R4 design.
