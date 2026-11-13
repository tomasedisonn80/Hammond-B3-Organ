# Agent 28 — prepared callback allocation boundary

## Assignment and scope

Wave 05, assignment 28 of 60. Owned only `tests/test_realtime.cpp`,
`docs/REALTIME.md`, and this note. No core, shared handoff, CMake, or PDF edits;
no commits, pushes, or subagents. Read AGENTS, README, status/next steps, latest
development log, plan, atlas review, and atlas chapters 062-063 (pp. 379-390).
Reviewed Engine, Types, Profile, TonewheelBank, ControlState, and existing tests.

## Delivered

- Global scalar/array C++ new/delete replacements include nothrow, sized, aligned,
  aligned-sized, and aligned-nothrow forms. Portable aligned storage uses checked
  malloc over-allocation plus std::align and a retained base pointer.
- Separate hook calibration covers all eight allocation and twelve deallocation
  overloads, observing twelve allocations/deallocations; zero-size and nonmultiple
  aligned sizes are included. Calibration does not contribute callback counts.
- Recording surrounds only each prepared process call; construction, prepare,
  snapshots, assertions, reporting, and destruction stay outside that interval.
- Workloads cover all three supported rates; all 122 keys; four full banks;
  1024 per-frame routing changes; all eight event types; positive, zero-frame,
  disconnected, silent, hard-maximum, and clock-boundary requests.
- Rejections cover every prepared error status plus late invalid payload,
  unsorted/end/zero-frame offsets, and unknown enums. Output/public state remain
  unchanged; connected/disconnected dense final state is compared.
- REALTIME.md records the source call graph, bounded storage/work, excluded
  loaders/serialization, reproducible commands, results, and remaining gates.

## Commands and observed results

Working directory: `/workspace/scratch/c871510c69b2/Hammond-B3-Organ`.
Native tools: `/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/`.

```sh
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake -S /workspace/scratch/c871510c69b2/Hammond-B3-Organ -B /workspace/scratch/c871510c69b2/agent28-release -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake --build /workspace/scratch/c871510c69b2/agent28-release --target test_realtime --parallel 2
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/ctest --test-dir /workspace/scratch/c871510c69b2/agent28-release -R '^test_realtime$' -C Release --output-on-failure -V
```

Configure passed with GNU C++ 14.2.0, C++20, Release and strict warnings.
First build failed on GCC's mismatched-new-delete diagnostic after it inlined
malloc-backed new through vector allocation. Kept replacement entry points
noinline on GCC/Clang/MSVC; retained all warning flags. Repeated build passed.
Targeted CTest passed 1/1: 63 accepted and 33 rejected observations, 216,255
processed frames, 23,919 consumed events, zero observed C++ allocations and
deallocations. Retained verbose log: `agent28-release/Testing/Temporary/LastTest.log`
outside the checkout. No timing criterion was applied. No additional optional
builds or measurements were run. No engine bug was found during this assignment.

## Evidence boundary and next risks

This is scoped Linux software evidence, not a complete real-time qualification.
The probe does not cover direct C/system/custom allocation, other threads, dynamic
locking/I/O, deadlines, host/device underruns, or hardware fidelity. Static source
review found no project-controlled I/O, locks, allocation/free, worker dispatch,
or unbounded retry in the reachable callback graph; platform math internals remain
outside that claim. No concurrent access/publication guarantee is made.
Next: target-specific allocator/lock/I/O interception and actual callback telemetry;
qualified Windows/macOS builds; ownership/retirement evidence before live exchange.
The integrator owns shared status updates, integration tests, and publication.
