# UI delivery hosted coverage review

**16 November 2026, America/Halifax — A26, wave 5.**

The missing sanitizer coverage is repaired in the
[standalone workflow](../../.github/workflows/standalone.yml). Both new gates
were already built or supported by the
[native CMake graph](../../apps/standalone/CMakeLists.txt) and selected by all
five ordinary native jobs. They were absent from the sanitizer job's explicit
inventory. Root subsequently assigned this workflow alone for the correction;
no CMake, production, fixture, capture or threshold change was necessary.
The [review receipt](../development/2026-11-16-ui-delivery/reports/ui-delivery-ci-coverage.json)
records exact identities, job names, coverage and the diff.

## Required published-source matrix

| Workflow/job | Runner labels and configuration | Jobs | Job limit |
| --- | --- | ---: | ---: |
| CI Release | `ubuntu-24.04` GCC; `macos-15` and `macos-15-intel` AppleClang; `windows-2022` MSVC | 4 | 20 min |
| CI full R4 | `ubuntu-24.04`, GCC Release | 1 | 35 min |
| CI sanitizers | `ubuntu-24.04`, GCC Debug, ASan/UBSan/leaks | 1 | 25 min |
| Native standalone | Same four runners, MIDI ON; additional Linux MIDI OFF | 5 | 40 min |
| Native standalone sanitizers | Linux GCC Release, MIDI OFF, instrumented project C++ and SDL C | 1 | 20 min |
| Native VST3 | Same four runners, Release and locked SDK | 4 | 35 min |

**All sixteen jobs require observation at the published changed source.**
The retained successful base-workflow aggregates belong to `6047723b…`;
the original renderer timeout and unchanged-source retry remain distinct.
No current changed-source hosted pass is established here.

## Repair and effective coverage

The sanitizer inventory now contains **30 CTest names and 29 executable targets**.
Title density maps to the existing `test_standalone_footage_typography_raster`;
header material adds its own executable. Discovery validates density's five
arguments: Python, `-B`, exact script, `--executable`, exact built fixture.
Source hashes, header instrumentation, linked runtimes, counts and
240/480-second property checks join the existing admission. All 28 previous
mappings, fourteen prior timeout checks and ASan/UBSan/leak policy remain intact.
Ordinary required-name assertions grow from 39 to 41.

Core Release and sanitizer jobs run the renderer-admission and capture-tool
Python suites through the unfiltered `tests/test_*.py` graph. Only the two Linux
core jobs execute the changed SIGCONT body; macOS and Windows deliberately skip
its Linux-specific methods. Native VST3 and full R4 selections do not cover these
UI changes. Ordinary native jobs already run serially, so `RUN_SERIAL TRUE`
preserves app isolation there without demonstrating a parallel contention case.

## Dependencies, limits and remaining evidence

Python 3.12 and locked SDL 2.32.10 suffice for the new gates; density uses only
the standard library. Native MIDI-ON jobs also acquire RtMidi 6.0.0. No workflow
installs Pillow: unit tests mock it, while fifteen-view capture
and paired image admission remain separate authoring gates.

Density retains 20-second child guards and 90/240-second suite limits; header
retains 180/480 seconds. Renderer completion remains 45 seconds inside its
90-second suite, and app smoke remains 60 seconds. No budget was increased;
actual sanitizer duration must establish fit within the unchanged 20-minute job.

LF checkout rules protect the density fixture hash. New fixture text is ASCII;
Windows binary frame mode and CMake target paths are present. Existing Unicode
checkout qualification covers the starter generator, not these native fixtures
or the fifteen-view utility. MSVC warning-clean compilation and both macOS
runner executions remain required; static inspection supplies no such pass.

Unique-key YAML parsing, **20 Bash syntax checks**, **11 embedded Python
compilations**, exact inventory/policy comparisons and whitespace checks passed.
No CI-contract test names this inventory; none needed updating.
No native execution, build, capture, external rerun or git operation
occurred. Whole-interface 1:1 and all separate product exits remain open.
