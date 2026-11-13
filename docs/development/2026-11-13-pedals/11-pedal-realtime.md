# Assignment 11: calibrated pedal allocation audit

Owner: /root/w02_a11_pedal_realtime

Wave 2. This is a new assignment in the pedal session, separate from earlier
console/runtime audits. Owned files are `tests/test_pedal_realtime.cpp` and this
note. No implementation or shared status files were changed.

## Implemented acceptance scope

Added a dedicated CTest executable for the frozen
[pedal routing API](../../../include/hammond/PedalRouting.h) and
[runtime contract](../../PEDAL_RUNTIME_CONTRACT.md). It reuses the established
portable test-only global C++ allocation interposition convention: scalar/array,
throwing/nothrow, aligned and corresponding ordinary/sized/nothrow delete
overloads. Explicit calls through volatile function pointers calibrate all paths
before any kernel observation, detecting exactly **12 allocations and 12
deallocations**. This prevents allocation-elision from making calibration vacuous.

Fixtures, expected states, timing calls, assertions and diagnostics are outside
recording regions. Every measured operation ends recording before checking its
result. The first compiled-table/identity accesses and first successful preparation
are observed without an unmeasured successful warm-up.

The audit covers:

- Unprepared render/edit/query and checked query destination preservation.
- Preparation, open-contact rendering, empty edits, all 200 closed contacts,
  repeated full edits, copied snapshots and every checked contact query. The five
  disconnected positions remain visible in the diagnostic count.
- Invalid final source, edit, route and weight; 201 edits and 199 routes. Rejected
  operations preserve the occupied kernel and prior output.
- A 4,096-frame full-occupancy workload using alternating binary-exact source
  frames of +1 and -0.5. Every result is consumed and checked, yielding exact
  checksum **199680**. The documentary map produces sums 195 and -97.5.
- Two hundred ordered edits to one position, complete release, and successful
  re-preparation resetting contacts.
- A separately labeled all-connected synthetic definition reaching exactly
  **50 per bus**, exercising the structural 200-branch ceiling. This fixture is
  not described as factory wiring or physical gain.

## Actual execution

Ran an isolated coherent Release build using CMake 3.31.6, GCC 14.2.0 and Python
3.12.14, with the core, generated table and test compiled from the same frozen
header/source interface. Commands, with the task-local CMake binary selected:

```sh
cmake -S . -B build-a11 -DCMAKE_BUILD_TYPE=Release
cmake --build build-a11 --target test_pedal_realtime -j 2
ctest --test-dir build-a11 -R '^test_pedal_realtime$' --output-on-failure -V
git diff --check
```

Strict compilation and the focused CTest passed: **1/1 test, zero failures**,
0.01 seconds total CTest time. Actual stdout records **4,130 measured regions**,
**4,111 accepted and eight rejected status calls**, **4,102 rendered frames** and
**1,000 accepted contact edits**, with **zero observed C++ allocations or
deallocations**. The remaining eleven regions are metadata/diagnostic queries.

The full-occupancy interval was **0.001312063 seconds** in this run, including
probe and assertion overhead. It is an observation only, with no timing pass
threshold. Reported ABI-specific fixed sizes were kernel **2,808 bytes**, source
frame **728**, bus frame **32**, and a 200-edit batch **600**. These are object
sizes, not compiler stack-frame measurements or portable ABI guarantees.

Source identity at execution: published base `6a38805ea072627f383d9eb988d735dc259db472`
plus the new working-tree kernel/compiler and this test. Exact SHA-256 values:

| File | SHA-256 |
| --- | --- |
| `include/hammond/PedalRouting.h` | `e77c52f1c541ef301fff4c8b0fb9a9449f93be632630326f2d7640694384bea8` |
| `src/PedalRouting.cpp` | `8d05dedb9015863dfd88668e5ea27d6be42ea1fcdb600cf34787e446e14d22af` |
| `tools/compile_pedal_routing.py` | `f34bcb9cd9641359b188c5f33c807256e70d23a8f66e513f544d8eb5dc0582b9` |
| `tests/test_pedal_realtime.cpp` | `9afea70e591c8ec1e3ab878e265318089749eb0e7c6f9f760d2be43ca4482068` |

## Limits and handoff

The probe observes this thread's replaced **global C++ new/delete** calls. It
does not interpose arbitrary C/system allocators, other threads, locks, file
access or scheduling, and does not prove audio-device deadlines. Preparation is
still a stopped/same-thread lifecycle operation; this test does not authorize
concurrent publication. Source-history and independent CSV/numerical evidence
belong to the separate wave-2 assignments. No implementation defect was found
in this scope. Full regression, sanitizers, hosted platforms, Engine integration,
physical fidelity and publication remain separate root-owned gates. No commit
or push was performed by this worker.
