# Waveform material timing: independent before/after acceptance

**Result: PASS for the scoped software-renderer timing gate.** A18 executed all
four prescribed pairs on 14 November 2026. No initial pair exceeded both p95
growth limits, so no repeat was justified or run. The largest percentage
increase was **3.5442%**, at 1280×900 Dimensional; the largest absolute increase
was **3.5283 ms**, at 1672×941 Dimensional. This result permits the next
coherent-source native gallery step alongside the separate
[A15 raster acceptance](WAVEFORM_MATERIAL_ACCEPTANCE.md).

The complete compact [machine record](../development/2026-11-14-waveform-continuation/reports/a18-material-timing.json)
retains all **2,400 measured total-draw samples** in their original order, every
process's median/p95/minimum/maximum, command, timestamps, return code, stderr,
resource observations, source/archive/binary hashes and layout fingerprints.
No result is borrowed from the previous material timing session.

## Exact source and build

The checkout was `/workspace/scratch/e3cacb90cc81/Hammond-B3-Organ`, with
HEAD `26ff2fbe66a50260bd7601cbfa54c1f5d35ff3a8` and HEAD tree
`530d5fcf777003f470f64558de9e5631d31a21a4`. The after renderer is an
uncommitted source change on that checkout; HEAD alone does not identify it.

| Input | SHA-256 |
| --- | --- |
| Exact before `baseline-ui/InstrumentView-before.cpp` | `428f74c4b2aae72e1ee048d1fa878575d0cd2edc064b1a3865ba40c446c30da2` |
| Current after `apps/standalone/InstrumentView.cpp` | `6570c97f1c62b555a1df3477954514e379d61165a36cf20f879dea5151ff866b` |
| Unchanged `tests/benchmarks/standalone_material_timing.cpp` | `58f6c7e0a7d940c9732b955df3b659cc84f45f4a3ac1dbb21abcc3d42d05b43a` |
| Shared Drawing archive | `06cde97b0ae59acac7b44437df920b3d12773b20004abedcda101d8da9a7ed36` |
| Shared support/UiModel archive | `14cdc87f1119b7d7bda9a0adc79a60bfdfca91e48a799d0c23424596c52311f2` |
| Shared SDL archive | `55ccb40daeebf75e429c7d8c693cdd5b4e2207a00393e35c66be992e752b03ed` |
| Shared core archive | `2e60507a07753f9d54b9451c13fe882a27fd4d8c1b82186a40afed360d787f24` |
| `material-before` executable | `0b9acdc44b65b0a332c0370440b8b42698551b7e14fac47b2e42b3acd08a4a21` |
| `material-after` executable | `a00fc6d7651c453a9f96e76c68c11ffeee77a6dbaaca13757ff0b0414edd959c` |

Both renderer translation units and the unchanged timing translation unit were
copied into sibling `a18-material-timing/` before compilation. The before source
also exactly matches `apps/standalone/InstrumentView.cpp` at the recorded HEAD;
the benchmark exactly matches its tracked HEAD bytes. The benchmark object was
compiled once and linked into both executables. Only the InstrumentView object
differs between the two link inputs.

Compiler: `/usr/bin/c++`, Debian GCC **14.2.0-19**, using
`-O3 -DNDEBUG -std=c++20 -Wall -Wextra -Wpedantic -Wconversion
-Wsign-conversion -Wshadow -Werror -DSDL_MAIN_HANDLED`. The include directories
and link order match the current native material test's Release build recipe.
Both binaries use the same Drawing, support, SDL and core archives from sibling
`build/`, plus `-lm -pthread`. All three direct compilations and both links
returned zero with empty stderr. A18 did not modify CMake, shared build inputs,
the benchmark or production code.

The record includes full command argument arrays, compiler executable hash,
shared header/source hashes and generated reference-art/header hashes. Source,
archive and shared header/source hashes were unchanged after measurement.

## Measurement protocol and environment

The existing [benchmark](../../tests/benchmarks/standalone_material_timing.cpp)
implements the [UI timing contract](../WAVEFORM_UI_DESIGN.md#ui-timing-and-unchanged-musical-scope):
**30 warmups, then 300 measured draws per process**, with no timed capture,
file I/O, hashing, sorting, logging or model mutation. The measured total spans
`paint_instrument`, `SDL_RenderFlush` and `SDL_RenderPresent`. Paint and
flush/present summary statistics are also retained; the unchanged program emits
raw nanosecond samples for total time only. Median is the mean of sorted samples
150/151; p95 is nearest-rank sample 285 of 300. A18 independently recalculated
every total median and p95 from the retained samples.

The actual renderer was SDL **2.32.10 software**, flags 13, an offscreen RGBA32
surface reported as `SDL_PIXELFORMAT_ABGR8888`, batching enabled, scale `(1,1)`,
full-size viewport and no clip. `SDL_Init(0)` opens no video or audio subsystem.
All processes use Play, overlay `none`, the benchmark's identical copied state
and focus fixture, and the same current support/UiModel archive. Surface
allocation and Drawing initialization occur before warmup; pixel fingerprinting
occurs after measurement.

The identified shared managed machine reports Linux x86-64, kernel `6.18.57`,
host `e15497d83e17`, CPU model `AMD EPYC 9V74 80-Core Processor`. Available CPU
affinity was 0–8; the runner and all children were restricted to CPU 0 throughout
measurement. Root finished the shared incremental build before linking and
held CTest/native work. A16 reported its heavy work complete; A17 deferred final
executions until the window closed. This coordination does not establish
exclusive physical-host scheduling or a measured CPU quota/governor. The usual
sysfs CPU/cgroup information was unavailable; CPU identity came from
`/proc/cpuinfo`, and the record retains the unavailable cgroup reads.

The window ran **22:15:39.924–22:18:41.249 UTC**, approximately 181.33 seconds.
All eight processes returned zero with empty stderr. Maximum observed child RSS
was 14,304 KiB. Actual process timings and context-switch counts remain in the
record; observations were not discarded as outliers.

## Original results and ordering

All numbers below are milliseconds. The table always reports before then after;
the order column preserves the actual execution order. P95 growth is calculated
as `(after − before) / before`. Investigation requires **both** strict
conditions: growth **greater than 15%** and increase **greater than 2 ms**.

| Cell | Actual run order | Before median | After median | Before p95 | After p95 | p95 change | Trigger |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1672×941 Dimensional | 1 before, 2 after | 109.262530 | 111.071832 | 123.804439 | 127.332737 | +3.528298 / +2.8499% | No |
| 1672×941 Flat | 3 after, 4 before | 29.109862 | 29.243926 | 34.040047 | 33.445460 | −0.594587 / −1.7467% | No |
| 1280×900 Dimensional | 5 before, 6 after | 81.649777 | 82.590136 | 96.372286 | 99.787933 | +3.415647 / +3.5442% | No |
| 960×700 Dimensional | 7 after, 8 before | 46.895561 | 46.666731 | 57.402260 | 54.519466 | −2.882794 / −5.0221% | No |

The two positive absolute changes exceed 2 ms, but neither exceeds 15%; the
conjunctive investigation rule therefore does not trigger. There was no extra
trial, discarded first run or selected best repeat. The reference Dimensional
median increased by approximately 1.81 ms in this environment. These absolute
software-renderer times do not establish real-display smoothness or an audio
deadline.

## Geometry and final pixels

The existing benchmark hashes layout fields individually, including all control
bounds/tracks and manual/pedal hit/top/front quads, avoiding padded object bytes.
Each paired layout fingerprint is identical. Reference Flat also has identical
final surface fingerprints; changed Dimensional pixels are expected.

| Cell | Before and after layout FNV-1a-64 | Before final pixels | After final pixels |
| --- | --- | --- | --- |
| 1672×941 Dimensional | `96fb350bb7a123ae` | `133183231b1bc6eb` | `a89bf7516a08d958` |
| 1672×941 Flat | `9ac2bac0db68cf6f` | `3f81943e94dad8c0` | `3f81943e94dad8c0` |
| 1280×900 Dimensional | `ba92304603c433f6` | `d939c3f5cb7d6434` | `dbe9f0441b6ae43e` |
| 960×700 Dimensional | `8f5cecf84e3329b1` | `8692b423b0977268` | `7c488a5f2862094a` |

These fingerprints support equal benchmark geometry and unchanged Flat output;
the independent A15 lossless raster comparison owns exact pixel containment,
material target acceptance and additional presentation/viewport coverage. A18
did not rerun or recount those tests.

## Reproduction and next action

Use the recorded checkout and sibling `build/` archives, verify all hashes above,
and restore the exact before source if needed:

```sh
git show 26ff2fbe66a50260bd7601cbfa54c1f5d35ff3a8:apps/standalone/InstrumentView.cpp > ../a18-material-timing/InstrumentView-before.cpp
```

The report's `build.compile_results[].command` and
`build.link_results[].command` contain every executed compiler/link argument.
Frozen inputs, objects, executables, orchestration and original per-process
stdout remain in `/workspace/scratch/e3cacb90cc81/a18-material-timing/`, about
7.1 MiB at completion. The original orchestration command was:

```sh
python3 /workspace/scratch/e3cacb90cc81/a18-material-timing/run_pairs.py
```

Its fixed four-cell order is retained above and in `protocol.initial_orders`.
Each executable command is stored in `runs[].command`. A fresh run has its own
timestamps and samples and must not replace this accepted record. A reversed
repeat was permitted only for an actually triggered initial cell; none occurred.

**Next:** root can qualify the complete current native application, capture the
coherent-source gallery at the three contract sizes and required workspace/Flat
states, verify its provenance and musical/control observations, compare it with
the reference, then refresh README with actual application captures. Keep
residual material/layout differences explicit. This scoped timing pass does not
close literal 1:1 reference equality, physical display/audio/MIDI qualification,
R4 renderer numerical acceptance or the separate R5/R6 model/integration gates.
