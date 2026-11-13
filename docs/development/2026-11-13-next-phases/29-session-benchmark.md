# Assignment 29 — reproducible offline Session benchmark

Canonical agent `/root/w05_a29_session_benchmark`; wave 5 of actual60/10.
Owns only `apps/standalone/benchmark.cpp`, `docs/STANDALONE_BENCHMARK.md`, and this note.
Root owns CMake, production Session/main, shared status and publication; no commit by this agent.
Read AGENTS, current handoffs/status, actual `tools/benchmark.cpp`, CLI handling,
Session header/implementation/contract and atlas chapter 062, PDF pp.379–384.
This implements the existing nominal Session workload; core/parameters/state remain unchanged.

## Source, environment and commands actually used

CWD `/workspace/scratch/5ba97739b54c/Hammond-B3-Organ`; inspected HEAD
`738162f0bc36f88f8c76268d04831862a8118d10`, tree `915e55dc7c3ad022042b188498aa41f2a7f40795`.
New benchmark plus concurrent uncommitted work means HEAD alone is not the qualified source.
Source manifest SHA-256: `3d37c970f157d2a5c0d13d62c77c88c035fddb3ebcdacd6ea562d24ee7092dca`.
It contains 54 sorted `relative-path:sha256\n` records: `src/*.cpp`, `include/hammond/*.h`,
`apps/standalone/{Session.h,Session.cpp,benchmark.cpp}`, `tools/CliArguments.h`,
`tools/{compile_pedal_routing,validate_pedal_map,validate_factory_reference,compile_scanner_line,compile_profile}.py`,
`data/pedal-map.json`, `data/references/{factory-table-iii.json,review-a-pedal.csv,review-b-pedal.csv}`,
`data/scanner/atlas-late-b3-nominal-v1.json`, `data/scanner-line.schema.json`, and `data/profiles/nominal-unmeasured-v1.json`.
All 54 byte identities were checked unchanged after the matrix; no old-library/new-header mixture.
Benchmark source SHA-256 `b9da06f92ec90bfe85ed2a4443605125fee0821dc7a9602e414526ae8dc92f80`.
Session source SHA-256 `247c6a63dc9bb6c4e60398b17779a2d985058563b8d981c5e06426eab977f6ae`.
Probe binary SHA-256 `2aa2ecbbf429608110b24f894136cc1046c0ee6c21764aa83bc4c0bfd2c7358f`.
Compiled profile SHA-256 `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`;
4,545 bytes/FNV-1a64 `bf38a44e8d31695a`, ID `nominal-unmeasured-v1`, retained authoring digest
`49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83`.
Linux x86_64 kernel 6.18.57; `/proc/cpuinfo` reports Intel Xeon Platinum 8573C.
GCC 14.2.0 Debian14.2.0-19; CMake4.4.4; Ninja1.13.2.git.kitware.jobserver-pipe-1; Python3.12.14.
Shared virtual/container runner, unpinned CPU, unmeasured power/thermal/background load; Release, no project sanitizers.

```sh
a29_cmake=/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin/cmake
"$a29_cmake" -S . -B ../build-a29-benchmark -G Ninja -DCMAKE_MAKE_PROGRAM=/workspace/scratch/1742da7072be/build-tools/bin/ninja -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF -DHAMMOND_BUILD_STANDALONE=OFF
"$a29_cmake" --build ../build-a29-benchmark --target hammond_standalone_support hammond_profile --parallel 2
g++ -std=c++20 -O3 -DNDEBUG -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror -Iinclude -Iapps/standalone -Itools \
  '-DHAMMOND_STANDALONE_BENCHMARK_CONFIGURATION="Release"' '-DHAMMOND_STANDALONE_BENCHMARK_COMPILER_ID="GNU"' '-DHAMMOND_STANDALONE_BENCHMARK_COMPILER_VERSION="14.2.0"' \
  '-DHAMMOND_STANDALONE_BENCHMARK_TARGET_SYSTEM="Linux"' '-DHAMMOND_STANDALONE_BENCHMARK_TARGET_PROCESSOR="x86_64"' '-DHAMMOND_STANDALONE_BENCHMARK_SOURCE_ID="3d37c970f157d2a5c0d13d62c77c88c035fddb3ebcdacd6ea562d24ee7092dca"' \
  -DHAMMOND_STANDALONE_BENCHMARK_SANITIZERS=0 apps/standalone/benchmark.cpp ../build-a29-benchmark/apps/standalone/libhammond_standalone_support.a ../build-a29-benchmark/libhammond_core.a -o ../build-a29-benchmark/hammond_standalone_benchmark
```

Core/support were freshly compiled by CMake with identical strict warnings, C++20, `-O3 -DNDEBUG`.
The direct link preceded root's target wiring. Initial configure omitted `CMAKE_MAKE_PROGRAM`
and failed because Ninja was absent from PATH; the explicit path above resolved this setup failure.
`lscpu` could not read this runner's `/sys`; CPU identity was read from `/proc/cpuinfo` instead.
Strict compile passed without warnings. Four initial 48k/512 smokes used iterations100/warmup2.
The retained matrix used the following exact argument pattern, invoked serially by Python subprocess:

```sh
../build-a29-benchmark/hammond_standalone_benchmark --profile ../build-a29-benchmark/nominal.b3p --sample-rate RATE --buffer-frames FRAMES --iterations 100 --warmup 4 --workload WORKLOAD
```

`RATE/FRAMES/WORKLOAD` take each row below, in this order. Raw stdout/command vectors and
manifest are at `/workspace/scratch/5ba97739b54c/a29-evidence`; concatenated raw reports SHA-256
`1db4d24bba5562d8d0c277b785a00738768a9564a8278758ec164500a9f5978f`.

## Observed results — all durations are unadjusted nanoseconds

| Hz/frames | Workload | Median | p95 | p99 | Max | Sum of 100 renders | Measured loop elapsed |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 44100/512 | silence | 913673 | 1451246 | 1610242 | 1977918 | 99748678 | 100452780 |
| 44100/512 | performance | 1028744 | 1533338 | 1728846 | 1736754 | 107945433 | 108671124 |
| 44100/512 | dense | 1017261.5 | 1372832 | 1821209 | 2135018 | 106040062 | 107320194 |
| 44100/512 | recovery | 971926.5 | 1793268 | 4407974 | 5617455 | 114679324 | 116356014 |
| 48000/512 | silence | 866676 | 1093245 | 1397898 | 1599340 | 91399112 | 92126223 |
| 48000/512 | performance | 963201.5 | 1527104 | 2396921 | 2692149 | 105376609 | 106104746 |
| 48000/512 | dense | 1053858 | 1755201 | 2386580 | 2739199 | 120372842 | 121722298 |
| 48000/512 | recovery | 955270.5 | 1184684 | 1486376 | 4239026 | 101026021 | 102897651 |
| 96000/512 | silence | 776381 | 936893 | 1215536 | 1217125 | 80133842 | 80814140 |
| 96000/512 | performance | 794037 | 873695 | 889460 | 945142 | 80364487 | 81076864 |
| 96000/512 | dense | 901115 | 1273507 | 1853356 | 1862212 | 96630203 | 98033706 |
| 96000/512 | recovery | 814383 | 898947 | 1268209 | 1278039 | 83603062 | 85177979 |
| 48000/128 | dense | 268335 | 354229 | 459958 | 489255 | 28584558 | 29380250 |
| 48000/2048 | recovery | 3777731.5 | 4953053 | 5780763 | 6395461 | 397131587 | 401365425 |

All 14 exited0: 1,400 measured callbacks, 56 warmups. Each 512-frame run ended at frame53,248;
128/2048 endpoints were13,312/212,992. Clock-pair median22ns throughout, maximum59–251ns;
those separate calibration observations were never subtracted. Zero observed render intervals
exceeded their nominal `N/Fs` period; this supplies no real-device deadline/underrun guarantee.
Each dense measured stage applied25,600 controls. Each recovery measured stage applied600
rearm note-ons, discarded25,600 controls, completed100 recoveries and observed100 each of
expected QueueFull/RecoveryPending. Snapshots proved empty holds, retained controls and zero
peak after each recovery, and every stop preserved clock while clearing holds/peak.
At each rate performance/dense audio checksums matched: 44.1k `64c9dae40f980f61`,
48k `f900da37f6bc9d85`, 96k `2e7ecbea34920c81`; no render-outlier removal or normalization.

## Handoff and limits

Agent30 independently owns CLI/count/state/statistics acceptance; none is claimed here until observed.
Root must qualify the actual CMake target and integrate its source-manifest definition before publication.
No SDL/device, deadline, underrun, latency, concurrency, Windows/macOS, sustained thermal test,
sanitizer test or physical-fidelity result follows from these short serial offline measurements.
The [benchmark contract](../../STANDALONE_BENCHMARK.md) defines the complete timing boundary.
