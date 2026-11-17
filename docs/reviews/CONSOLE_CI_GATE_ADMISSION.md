# Console CI gate admission

**A51, wave 9 — the applied gate configuration is admitted for root's
source-specific qualification. Hosted and sanitizer acceptance remain unrun.**
This independent review inspected actual source, generated discovery and build
inputs in this checkout. It performed no configure, build, CTest, native process,
CI trigger or Git mutation. The [evidence receipt][audit] retains exact inventories,
commands, properties, input hashes and 71 passing inspection checks.

## Applied source and observed local evidence

Standalone CMake `927f48c1…` and workflow `d298ac55…` exactly match the
[A46 proposals][a46]. Independent CMake token-and-condition comparison reproduces
the additive union of base `9d60dbf…`, console recovery `3263b17…` and published
`03c70c1…`. Duplicate-key-refusing YAML parsing and Python AST inspection find
11 embedded blocks and 142 assertions. Every parent assertion expression remains;
normalizing only derived cardinalities leaves no missing expression. One repeated
wrapper-path assertion accounts for the difference from the 141-occurrence
parent expression multiset union.

The retained [full discovery][all] has **251 unique registrations**. Applying the
actual workflow filter selects exactly the [78 affected registrations][affected],
including all **55 mandatory platform names** and three Python comparator/capture
suites. Required names are enabled and have commands. Root's subsequently completed
[qualification receipt][qualification], matching raw log and JUnit XML record
**46/46 build steps and 78/78 affected passes**, with zero failures or skips.
This is not a 251-test execution. Earlier full-suite failures remain unchanged.

## Exact selection and generated inputs

The sanitizer environment declares **41 CTest names mapped to 37 executable
targets**; both sets and the **63-source provenance inventory** independently equal
the parent unions. The JSON retains every name and mapping. Nonidentity mappings
are:

| CTest wrapper | Executable target |
| --- | --- |
| Header statistics | `test_standalone_header_material` |
| Title density | `test_standalone_footage_typography_raster` |
| P1 numerical | `test_standalone_performance_plate` |
| Replay and semantic paint boundaries | `hammond_standalone` |
| Native calibration | `hammond_standalone_calibration_probe` |

Actual ordinary discovery confirms the Python script paths, `-B`, executable
arguments, child-timeout arguments and P1 `--candidate-only --after` command.
The three Python suites resolve to `tests/`; P1 numerical resolves to
`tools/compare_performance_plate.py`.

Current `compile_commands.json` and `build.ninja` confirm `LibraryModel.cpp`
appears once in support, all five library targets compile their own source, and
H1 material, grain and P1 each compile one fixture translation unit containing
exactly one real-painter include. Their targets do not additionally compile
`InstrumentView.cpp`. Required sources and nonempty ordinary objects exist.
Library links include support/core; P1 includes drawing/support/core/SDL; the app
and calibration probe link all six production archives. Fake-MIDI include
precedence, MIDI-off support and the apron fault seam also match the declarations.
These are ordinary-build observations; sanitizer instrumentation is still unrun.

## Retained execution policy

| Gate | Ordinary / sanitizer CTest seconds | Ordinary / sanitizer child seconds |
| --- | ---: | ---: |
| H1 material | 180 / 480 | — |
| Header statistics | 90 / 240 | 20 / 60 |
| Grain bounds | 30 / 90 | — |
| P1 fixture and numerical | 180 / 480 | Numerical: 60 / 60 |
| Title density | 90 / 240 | 20 / 20 |
| Both paint boundaries | 60 / 90 | 12 / 30 |
| Native calibration | 90 / 180 | 15 / 15 |

All 43 explicitly configured ordinary test-property groups match discovery;
all 22 sanitizer deadline assertions match CMake. The five library gates retain
no explicit timeout or labels. Both CI executions retain `--parallel 1`,
`--no-tests=error` and the 180-second global default. All six serial registrations
remain. Native jobs retain 40 minutes; sanitizer retains 35. Leak detection,
halt-on-error, LSAN exit 23, disabled-test/override refusals, object instrumentation,
archive-symbol and executable-runtime probes remain. Intentional quarantine stays
outside the sanitizer selection.

## Concrete CI inputs and remaining qualification

All 63 provenance files and 25 normal manifest/tool inputs exist; required
font, reference, PDF and apron hashes agree. Publication must include the P1
contract and `reports/p1-authoring.json`, which CI reads as source inputs.
No missing-file blocker was found. Windows uses Visual Studio x64, Release
configuration and `Release/hammond_standalone.exe`; CMake `TARGET_FILE` supplies
wrapper paths. The `.a`, `link.txt`, `ldd` and unsuffixed executable assumptions
belong exclusively to Linux sanitizer CI. This review supplies no Windows pass.

Actual workflow matrices require **six standalone, six core and four VST3 job
families**. Root must verify the published commit/tree/parents/contents and retain
each run ID, exact head, attempt, job identity, runner, raw logs and artifacts.
Keep failures, cancellations, timeouts and never-run steps distinct; preserve
original attempts. Earlier hosted results cannot qualify this combined source.
No retry, relaxed deadline, platform waiver or product-completion claim follows.

[audit]: ../development/2026-11-16-console-completion/reports/A51-ci-gates.json
[a46]: CONSOLE_BUILD_RECONCILIATION_ADMISSION.md
[all]: ../development/2026-11-16-console-completion/reports/combined-all-discovery.json
[affected]: ../development/2026-11-16-console-completion/reports/combined-affected-discovery.json
[qualification]: ../development/2026-11-16-console-completion/reports/combined-qualification.json
