# A27 — native paint timing and resource qualification

Actual worker `/root/w05_a27_paint_performance`, wave 5; starting HEAD
`af006b0ae293c7c9a5f44b5dfe1dc9942fe9e12d`. Added the manual
`tools/standalone_paint_benchmark.cpp`; no production, CMake, shared-build,
commit or publication changes.

The [report](../reports/A27-paint-performance.json) pins sources, objects,
archives, binaries, exact compiler/run commands, hardware, load and all 3,600
unfiltered total-duration samples. The before painter is recoverable with
`git show af006b0:apps/standalone/InstrumentView.cpp`, SHA-256
`aae710a6e4eb8d7eccfe8fd7e5cf3cb98109ee1bc0143229e5b5b8b63f3c7a4c`.
Current painter SHA-256 is
`3687f96db4490e600d6107e6b39d7b7d568bdeb183f16f6aa397535a5f688567`.
Only the before translation unit's three public exports were compiler-renamed;
both painters share current Drawing, UiModel, headers, assets and SDL dependencies.

## Executed results

GCC 14.2 strict Release compilation/linking passed for separate timing and heap
variants; ordinary current-only syntax passed. The report retains the initial
harness-only `-Werror=address` failure and its explicit feature-flag correction.
Six invalid CLI inputs were refused. Independent raw-sample recalculation passed.

Each timing case used 30 warmups and 300 measured frames per painter, alternating
execution order. CPU 8 was pinned on the shared AMD EPYC 9V74 host; other workers
deferred heavy work. Measurements include real painting, flush and offscreen
surface present, with no timed capture, hashing, file I/O or allocation observer.

| Case | Median before → current, ms | P95 before → current, ms |
| --- | ---: | ---: |
| 1672×941 Dimensional, zero | 112.333 → 113.713 | 135.424 → 129.721 |
| 1672×941 Dimensional, eight | 112.295 → 113.386 | 130.259 → 127.045 |
| 1672×941 Dimensional, mixed/held | 111.538 → 112.441 | 128.252 → 131.616 |
| 1280×900 Dimensional, mixed/held | 81.589 → 81.521 | 97.620 → 91.041 |
| 960×700 Dimensional, mixed/held | 46.321 → 46.454 | 53.441 → 54.945 |
| 1672×941 Flat, mixed/held | 27.815 → 27.763 | 31.224 → 30.736 |

No case exceeded both 15% and 2 ms median growth. Largest increase: 1.380 ms,
1.228%. Compact/Flat pixel fingerprints match. A separate calibrated observer
measured 32 draws each: C++ allocations/frees per draw fell 21→19 for wide
Dimensional, stayed 12→12 compact and 21→21 Flat. Static rack captions and stack
digits add no observed C++ heap calls; texture initialization remains outside
painting. C allocation, other threads, leak freedom and hardware resources are
outside this observer.

Next: root integrates the ordinary manual target and publishes alongside A23.
Usage: `standalone_paint_benchmark WIDTH HEIGHT dimensional|flat zero|eight|mixed-held`.
`HAMMOND_PAINT_BASELINE` enables pairing; a separate `HAMMOND_PAINT_ALLOCATIONS`
build enables heap observation. Scale-1, overlay-None software timings qualify
neither physical UI latency, audio deadlines, literal reference equality nor
interactive frame rate.
