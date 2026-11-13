# Prepared processing boundary

`test_realtime` observes global C++ allocation and deallocation calls around
prepared `Engine::process` calls. Its Release run on 2026-11-13 passed **63 accepted
calls and 33 rejected calls**, with **216,255 processed frames, 23,919 consumed
events, and zero observed C++ allocations or deallocations**. This is an executed
software check of the current nominal dry engine. It does not establish a callback
deadline, concurrency safety, complete absence of system allocation, or hardware
fidelity. Exact commands and the initial compiler issue are retained in the
[Agent 28 note](development/agent-notes/28-realtime-boundary.md).

The boundary follows the lifecycle and timing requirements in atlas chapters
062-063, pp. 379-390 of the
[source PDF](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf), together with the
[engine API](ENGINE_API.md) and [implementation contract](IMPLEMENTATION_CONTRACT.md).

## What the executable measures

[tests/test_realtime.cpp](../tests/test_realtime.cpp) replaces the executable's
global scalar and array `new`/`delete` functions, including nothrow, sized-delete,
aligned, and aligned-sized variants. Non-allocating placement forms are not
replaced. Aligned storage uses checked over-allocation, `std::align`, and a retained
`malloc` base, avoiding dependence on a platform-specific aligned allocator.
Compiler-specific noinline annotations preserve these entry points on GCC, Clang,
and MSVC without disabling the project's warning gates.

A separate calibration explicitly exercises all eight allocation overloads and
all twelve deallocation overloads. It observes twelve allocations and twelve
deallocations, including zero-size requests and aligned sizes that are not
multiples of the alignment. Calibration counts are excluded from engine results.
Explicit calls through volatile function pointers keep this calibration from
depending on optimizable `new` expressions; volatile is not used as synchronization.

After calibration, recording uses trivial thread-local counters. For every engine
observation, preparation, profile loading, fixture construction, output allocation,
state snapshots, and argument construction finish before recording starts. The
recorded region contains one `process` call. Recording stops before status checks,
output/state assertions, diagnostics, and reporting. Counter checks remain active
in Release. The first process call on each prepared success-case instance is
observed, including the first sine evaluation in the executable's engine workload.

### Exercised requests

Every row is exercised at 44.1, 48, and 96 kHz using the compiled nominal profile.

| Request | Retained observation |
|---|---|
| First positive callback | All 122 manual keys, four full drawbar banks, enabled routes; consumes setup events and writes only the requested sample |
| Sustained connected output | Blocks of 17, 64, 257, 1024, and the admitted hard maximum of 65,536 frames; finite output and untouched trailing buffer |
| Dense routing changes | 1024 changed drawbar events at 1024 distinct offsets while all 122 keys remain held; exercises coefficient rebuilding each frame |
| Mixed controls | 1024 events covering all eight event types, both manuals, bank edits, selection, Cancel, expression, note release, and AllNotesOff |
| Same-offset events | 1024 events on one positive sample and 1024-event zero-frame flushes; stable supplied dispatch path |
| Zero frames | Empty, connected, and disconnected flushes; output, source phases, and frame clock do not advance |
| Disconnected positive calls | Sustained sources and dense controls; resulting controls, keys, all 91 phases, and clock equal a connected reference |
| Silence after release | Positive processing writes zeros while sources continue through the normal processing loop |
| Capacity and buffer rejection | Oversized block, short output, and 1025 events in positive and zero-frame calls |
| Invalid event rejection | Nonfinite final payload after 1023 valid events, unsorted offsets, end-boundary offset, nonzero zero-frame offset, unknown type, and unknown manual |
| Clock boundary | Last representable positive frame succeeds, the next frame rejects overflow, and a zero-frame flush remains accepted at the maximum clock |

Rejected requests consume no events and preserve the supplied output and copied
public state. The test observes every error status reachable from a prepared
engine: `BlockTooLarge`, `InvalidBuffer`, `TooManyEvents`, `TimelineOverflow`, and
`InvalidEvent`. `NotPrepared` and preparation errors are outside this chosen
boundary; ordinary engine/profile tests cover those contracts.

## Static callback call-graph audit

The audit read the current implementation and its reachable helpers, rather than
treating `noexcept` as a real-time guarantee.

| Reachable path | Work and storage |
|---|---|
| [Engine::process / preflight](../src/Engine.cpp) | Checks prepared state, bounded frame/event counts, output capacity, clock overflow, order, offsets, and payloads. Uses scalar values and borrowed spans; rejects before mutation. |
| Event payload helpers and [Types](../include/hammond/Types.h) | Enum/range checks, `std::isfinite`, and `std::trunc`; no diagnostics or string construction on error. |
| Engine::apply_event and [ControlState](../src/ControlState.cpp) | Changes fixed arrays and scalar controls through checked accessors. Note release and AllNotesOff scan bounded manual storage. |
| Engine::rebuild_coefficients | Clears 91 coefficients, copies a fixed-size control snapshot, and visits at most 2 × 61 × 9 active routing branches. No container growth or ownership release. |
| [TonewheelBank::process_frame](../src/TonewheelBank.cpp) | Evaluates 91 shared sine sources and wraps their phases once per frame, including silence and disconnected output. Uses `std::sin`, scalar state, and a caller-owned array. |
| Connected mixing | Accumulates 91 source contributions per frame, applies fixed profile gain and expression, and writes the supplied output. |

No project-controlled path in that graph performs file/stream I/O, logging,
allocation/deallocation, mutex/condition-variable work, atomics, worker submission,
or an unbounded retry. Storage is owned by the engine or borrowed for the duration
of the call. No shared-pointer final release or dynamic-container destruction is
reachable. These findings apply to the source revision inspected, not all future
implementations or the internals of the platform math runtime.

The declared limits are 1024 events and a prepared maximum no greater than 65,536
frames. Positive processing performs 91 source evaluations per frame; connected
mixing additionally visits 91 contributions. At most one coefficient rebuild
follows an event cluster before a sample. A conservative bound on rebuilds is
`min(frames, event_count + 1)`, allowing a dirty cache from a preceding zero-frame
flush. These are work counts, not CPU timings or guarantees that a host budget fits.

### Work outside this boundary

[Profile loaders](../src/Profile.cpp) and
[control serialization](../src/ControlStateIO.cpp) perform parsing, stream/file
access, and string allocation. They are not called from `process`. Preparation
validates and copies fixed profile/source values, but its cost is not included in
the callback result. Loading, preparation, replacement, serialization, object
destruction, and UI work remain outside active processing. Diagnostic access and
control restoration require stopped or same-processing-thread access; no live
publication, snapshot transfer, or retirement protocol is implemented.

## Limits and next evidence

The hooks count calls to the global C++ allocation/deallocation functions on the
recorded thread. They do **not** interpose `malloc`, `calloc`, `realloc`, `free`,
mapping/system APIs, class-specific/custom allocators, or independently linked
runtime allocators. Direct C allocation inside a math library could escape these
counters. Source review found no such explicit operation in the project callback
graph; this does not prove its absence in every linked library or target runtime.

There is no dynamic lock or I/O interceptor in this test. No timing threshold is
used, and its short CTest duration is not a deadline result. Page faults, scheduling,
denormal costs, math-library initialization, instrument overhead, host/device
underruns, and concurrent access remain separate target-specific evidence needs.
No native audio callback, host, hardware instrument, Windows build, or macOS build
was qualified by this scoped Linux Release run. Sanitizer and race checks require
separate runs and do not replace deadline measurements.

Next, retain C/system allocator and lock/I/O interception on each chosen target,
and measure the actual adapter callback with qualified bounded telemetry under
declared loads. Establish ownership/retirement tests before adding concurrent
profile exchange. Re-run this test and update the call-graph audit whenever a
callback dependency changes.

## Reproduction

From the repository root, with a C++20 compiler and the normal CMake prerequisites:

```sh
cmake -S . -B ../agent28-release -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build ../agent28-release --target test_realtime --parallel 2
ctest --test-dir ../agent28-release -R '^test_realtime$' -C Release --output-on-failure -V
```

CMake discovers `test_realtime.cpp` through the existing `test_*.cpp` rule; this
work adds no build-system dependency or CMake edit.
