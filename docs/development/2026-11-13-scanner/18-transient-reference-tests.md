# Assignment 18: independent transient-reference regression

**Wave:** 3 of 10. **Assignment:** 18 of 60. **Date:** 13 November 2026.
**Agent:** `/root/w03_a18_transient_reference_tests`.

## Owned work and inspected basis

Owned files are `tests/test_scanner_transient_reference.py`,
`docs/SCANNER_TRANSIENT_ACCEPTANCE.md` and this note. Read the standing rules,
current handoff/status/next steps, project plan, numerical contract and transient
implementation/docs. Freshly extracted and read atlas pp. 182–186; earlier wave 1
owns the separate complete 500-page review. No native production, graph, shared
CMake/status, Git history or other worker file was changed.

| Input | Identity |
| --- | --- |
| Observed integration HEAD | `80ea8cd2d7febe12fc4dd382e475a00ff4181eac` |
| HEAD tree | `d98d9baf666f048629f5c817ed0f040b215df0e4` |
| Final test SHA-256 | `b484f175854f2d461e334ac102e23a8df186b62bc466a85f142479c08e1842d0` |
| Reference source SHA-256 | `5d63941b4b85c28ebf4dce7427e87b87779c3538ae00ff2510014a1df1c45cda` |
| Graph SHA-256 | `1d236be5e6b63e938a9f147808386173949d167e09aee8e902c55002e4ea4604` |
| Frozen numerical contract SHA-256 | `3999a3a409d397401e135e8285704092bad130911468802370bf6da404d58ff9` |

The reference and test were new live-tree files, not part of that historical HEAD.
The hashes above identify the actual inputs tested; no whole-tree qualification
is inferred from the observed base commit. Root owns later coherent integration
and publication. Python 3.12.14, CMake 4.4.4, Ninja 1.13.2 and GCC 14.2.0 were
available. This assignment executes Python reference tests, not compiled C++ DSP.

## Independent verification delivered

The suite constructs expectations from literal documentary values and physical
KCL/energy laws. It does not reuse producer graph normalization, matrix stamps,
private branch lists, factors or analytical DC helpers. It checks all physical
coordinates, pre-inductor divider attachment and ground-reference/current signs.
The central independent checks are trapezoidal endpoint derivative identities
and full source-work/resistor-dissipation energy balance. The
[acceptance document](../../SCANNER_TRANSIENT_ACCEPTANCE.md) retains equations,
coverage, diagnostic metrics and limits.

Final execution from the repository root:

```sh
python3 tests/test_scanner_transient_reference.py
PATH=/workspace/scratch/1742da7072be/build-tools/bin:$PATH \
  cmake -S . -B /workspace/scratch/1742da7072be/a18-build \
  -G Ninja -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
PATH=/workspace/scratch/1742da7072be/build-tools/bin:$PATH \
  ctest --test-dir /workspace/scratch/1742da7072be/a18-build \
  --output-on-failure --no-tests=error \
  -R '^python_test_scanner_transient_reference$'
git diff --check
```

The final direct execution passed **21 methods in 2.617 seconds**. The isolated
required CTest passed **1/1 suite in 3.23 seconds**, with zero failures or skipped
methods. No compiled tool is an input to this Python-only gate. The initial
20-method run also passed; the final method independently separates RMS-only
from maximum-only convergence-budget failure.

A diagnostic rerun across 1,152 driven intervals measured maximum normalized
trapezoidal endpoint residual `1.7182063335053482e-14` and maximum independent
energy-balance residual `2.818391755075697e-23 J`. No production defect was found.
The suite retains 144 signed basis initializations, six exact DC equilibria,
all 18 ordered mode/rate cases, 76 rejected-call continuation checks and 4,096
bounded passive frames. This passivity subset is not presented as the complete
250 ms frozen acceptance grid.

## Refinement result and explicit next step

A real zero-input control needs two passing comparisons (8→16 and 16→32) before
reporting convergence. A 16-knot charged-C18 chorus experiment remains
**inconclusive** at factor 32: largest required RMS `6.716013244123893e-5` and
maximum `1.6632497807189672e-4`, exceeding the frozen `2e-6`/`1e-5` budgets.
The test preserves that result and never treats the finest trace as truth.
It also checks strict knot/time/input/mode matching, fixed current normalization,
all 55 required channels and separately reported return/current diagnostics.

Per coordinator ownership, no expensive full 2,400-knot refinement study was
started. The next numerical owner must execute all nine fixtures in both modes,
retain each actual refinement and conditioning state, and report convergence or
inconclusive limits before grading native continuous-time accuracy. Separate
native all-basis matched-step comparison remains necessary for G3; G5, rotor,
host integration and physical fidelity remain open. Output/CLI failure checks
passed, including actual POSIX symlinks and unconditional hardlink aliases.
On Windows the test explicitly limits symlink coverage to the portable cases;
it does not claim privileged Windows symlink execution.

The three files are ready for root integration; no commit/push was performed by
this worker and no shared completion ledger was changed.
