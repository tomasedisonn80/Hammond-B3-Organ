# A20 — independent crossover lifecycle acceptance

Actual agent `/root/w04_a20_crossover_lifecycle`, wave 4. Starting HEAD
`af006b0ae293c7c9a5f44b5dfe1dc9942fe9e12d`; reviewed standing instructions,
the full M0–M9 plan, checkpoint, complete frozen crossover contract, native
implementation and existing author coverage. Owned only
`tests/test_leslie_crossover_lifecycle.cpp` and this note.

The new test independently computes capacitor charge, inductor flux, electrical
ports and energy from public physical coordinates. Its midpoint power check
does not use the implementation's reported current or energy as its oracle and
does not reconstruct the implementation's prepared matrices. It exercises all
16 ordered rate pairs across seven resistor pairs, including all four 1/1024-ohm
corners and unequal fractional loads. Precharged, nonzero-input checkpoints
retain coordinates, frame and observed endpoint exactly; subsequent scalar,
whole and mixed partition processing also matches freshly prepared/restored
twins exactly.

Admission checks cover both signs of all five coordinate limits and adjacent
outward doubles, adjacent invalid rates/loads, final-sample block rejection,
response at DC/smallest positive double/just below Nyquist, and untouched-twin
continuation. Destination preservation includes NaN payloads and signed zero.
Six overlapping double subobjects reject; disjoint spans touching in either
byte order succeed. The last legal block reaches `UINT64_MAX` exactly; the next
overflowing block commits nothing and empty processing remains legal.

## Executed verification

From the repository root:

```sh
g++ -std=c++20 -O2 -DNDEBUG -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror -Iinclude -Itests '-DHAMMOND_TEST_PROFILE="/workspace/scratch/5b7d983ac078/build-native/nominal.b3p"' '-DHAMMOND_SOURCE_DIR="/workspace/scratch/5b7d983ac078/Hammond-B3-Organ"' tests/test_leslie_crossover_lifecycle.cpp /workspace/scratch/5b7d983ac078/build-native/libhammond_core.a -o /workspace/scratch/5b7d983ac078/a20-crossover-lifecycle
/workspace/scratch/5b7d983ac078/a20-crossover-lifecycle
```

Passed: **112 rate/load transitions, 30,240 physical intervals, 53 rejected
transaction continuations, 10 exact boundary checkpoints and six alias cases**.
Maximum scaled charge/flux residual `1.1713406869342906e-18`, midpoint energy
residual `7.1091475263053427e-18`, independent port/energy error
`3.5410042953376575e-16`. Whitespace check passed; no production defect found.

SHA-256: test `b618ae41356a081891b1ab23e8a84feff508996f5c2c2a9360f9db2fe4004138`;
implementation `1a1bdde72af95709143afc4f62991c138ff3458cc78765fbe49a229d82693525`;
header `54efff218f873045bd07a2eb3270d07637e3f3fc5d2d51bac032b7efca53559c`;
linked root-built core `d110f7523afcc3ae1ab6053da7dfc86dfcddc66d4bfe19aabf1f0458fb1bd13f`.

Next: root's ordinary CMake glob discovers this test; rebuild and run
`ctest -R '^test_leslie_crossover_lifecycle$' --output-on-failure --no-tests=error`.
Shared build, production code, commits and other checkouts were untouched.
Allocation, physical fidelity and same-Hz audible acceptance are separate gates.
