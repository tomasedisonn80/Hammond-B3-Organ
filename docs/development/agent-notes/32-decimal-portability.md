# Agent 32 — portable decimal conversion

Wave 06, agent 32 of 60; 2026-11-13. Assignment: remove the observed macOS
floating `from_chars` build dependency without weakening numeric contracts.
Read AGENTS, current project handoff/API/contracts, the first hosted macOS log,
and atlas chapter 063 (pp. 385–390) for the stopped/processing boundary.

## Observed failure and change

At `b9c1cac`, AppleClang 17/Xcode 16.4 libc++ has no floating `from_chars`
overload; the retained macOS log fails at ControlStateIO.cpp:69.

Added `include/hammond/detail/Decimal.h` and routed only the three double
conversion sites in Profile.cpp, ControlStateIO.cpp and tools/render.cpp through
it. Unsigned integer `from_chars` calls are unchanged. Removed duplicated
floating grammar checks where the shared parser now owns those exact rules.
No dependencies, platform exclusions, warning waivers or CMake edits were added.

The shared parser prevalidates full ASCII decimal syntax, then extracts directly
to double using a private classic-locale stream. It preserves signed exact zero,
accepts representable subnormals, rejects nonzero values rounded to zero and
rejects overflow even if the stream saturates to maximum finite. A fully consumed
nonzero result no greater than minimum normal can succeed despite `failbit`,
accounting for libc++'s ERANGE propagation. No wide intermediate double rounding
is introduced. Nearest rounding is scoped and the caller's mode is restored.
Failed conversions and exceptions leave the destination unchanged. Allocation
remains outside processing. `docs/DECIMAL_PARSING.md` records this contract and
the upstream LLVM num_get rationale; all platforms use the same implementation.

Agent 31 independently patched Profile.cpp's read-exception catch. Narrow patches
preserved that edit; its regression also passed in this build. Shared handoff
documents, commit and publication are the integrator's responsibility.

## Verification performed locally

GCC 14.2.0, C++20 Release, all existing strict warnings treated as errors.
Native CMake/CTest: `/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/`.
Build: `/workspace/scratch/c871510c69b2/agent32-release`.

```sh
cmake -S . -B ../agent32-release -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build ../agent32-release --parallel 2
ctest --test-dir ../agent32-release --output-on-failure \
  -R '^(test_decimal|test_profile|test_control_io|python_test_render)$'
../agent32-release/test_decimal
ctest --test-dir ../agent32-release --output-on-failure
git diff --check
```

Required decimal/profile/control/renderer subset: **4/4 passed**, 1.01 s.
Full current tree: **16/16 passed**, 12.11 s; no test weakening.
`test_decimal`: **16,547 exact-value/round-trip accepts and 106 rejected tokens**.
Each rejection preserves finite, negative-zero and NaN-payload destinations.
Coverage includes independent binary64 vectors, exact halfway ties, minimum
normal/subnormal and maximum-finite boundaries, long balanced numbers, malformed
bytes/grammar, custom global comma/grouping facets, all four rounding modes,
every finite exponent with both signs and dispersed deterministic bit patterns.

Original JSON bytes remain SHA-256
`d17a266ed97cbbd3a2925ebebafafbd6c0e3f84763635732e0a9351d0eab2bff`,
matching `git show b9c1cac:data/profiles/nominal-unmeasured-v1.json`.
Compiled nominal.b3p is SHA-256
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`,
identical to the existing agent30 build; embedded canonical authoring digest
remains `49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83`.

## Pending gates

Hosted macOS and Windows verification of this replacement remains pending until
the integrator publishes and observes CI. Local Linux success does not prove
either hosted result. No hardware, native host, DSP fidelity or callback-deadline
qualification follows from this parser change. No commit or push was performed.
