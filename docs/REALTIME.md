# Prepared processing boundary

The historical `test_realtime` workload observes global C++ allocation and
deallocation calls around prepared `Engine::process` with **ideal contacts and
percussion off**. Its retained Release run on 2026-11-13 passed **63 accepted
calls and 33 rejected calls**, with **216,255 processed frames, 23,919 consumed
events, and zero observed C++ allocations or deallocations**. Those 96 calls are
the original scoped observation; they do not include the later enabled contact,
percussion or typed-input paths. The separate enabled-path observation below
qualifies those additions on its own frozen source. It does not establish a callback
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

## Current static callback call-graph audit

The continuation audit inspected immutable tree
`b9146546fcf756360e1da89d6698c4999359579f` and its reachable helpers. This tree
contains the published lifecycle core plus the partial-key/trace extension.
`noexcept` is an exception contract, not a real-time guarantee. The
[assignment 43 note](development/2026-11-13-continuation/43-enabled-realtime.md)
retains the scoped source identities and execution evidence.

| Reachable path | Work and storage |
|---|---|
| [Engine::process / preflight](../src/Engine.cpp) | Checks prepared state, bounded frame/event counts, output capacity, clock overflow, order, offsets, and payloads. Uses scalar values and borrowed spans; rejects before mutation. |
| Event payload helpers and [Types](../include/hammond/Types.h) | Enum/range checks, `std::isfinite`, and `std::trunc`; no diagnostics or string construction on error. |
| Engine::apply_event and [ControlState](../src/ControlState.cpp) | Changes fixed arrays and scalar controls, including partial targets and four percussion switches. Normal releases retain contact travel; AllNotesOff clears one bounded manual. |
| Engine::rebuild_coefficients | Clears both 91-element sustain and percussion arrays, copies a fixed control snapshot, and visits at most 2 × 61 × 9 contact routes. Upper-B eligibility selects the harmonic and one-foot mask. No container growth or ownership release. |
| [ContactBank](../src/ContactBank.cpp) | Fixed storage for 122 keys and 1,098 contacts. Nominal advancement visits each key; moving keys evaluate nine make/break histories. A changed connection marks Engine's coefficients dirty for the next sample. No motion calculation allocates or evaluates an exponential. |
| [PercussionState](../src/Percussion.cpp) | One shared readiness scalar, fixed settings and precomputed decay/recovery factors. The eligible detector scans at most 61 upper ninth contacts. Per-frame work uses arithmetic and clamping; exponentials belong to preparation or stopped rate changes. |
| [TonewheelBank::process_frame](../src/TonewheelBank.cpp) | Evaluates 91 shared sine sources and wraps their phases once per frame, including silence and disconnected output. Uses `std::sin`, scalar state, and a caller-owned array. |
| Connected mixing | Accumulates 91 sustain contributions and, when eligible, another 91 harmonic contributions weighted by current shared readiness. Applies profile gain and expression, then writes borrowed output. Disconnected processing still advances source, contact and readiness histories. |
| [NoteOwnership::translate](../src/NoteOwnership.cpp) | Preflights at most 1,024 inputs, then uses a fixed candidate and 1,024-event array. Each identity scan/compaction examines at most 256 owners. Capacity or identity failures return without committing output or ownership. |
| [process_owned_notes](../src/InputProcessor.cpp) | Copies fixed ownership, translates into a fixed event array, calls Engine, then commits ownership only on success. Nested fixed stack storage has no heap owner or SDK object. |
| [ParameterBridge](../src/ParameterBridge.cpp) | Searches at most 43 immutable literal descriptors, applies bounded exact threshold comparisons and writes a fixed Event/value. String views refer to program-lifetime literals; no JSON parsing occurs. |

No project-controlled path in that graph performs file/stream I/O, logging,
allocation/deallocation, mutex/condition-variable work, atomics, worker submission,
or an unbounded retry. Storage is owned by the engine or borrowed for the duration
of the call. No shared-pointer final release or dynamic-container destruction is
reachable. These findings apply to the source revision inspected, not all future
implementations or the internals of the platform math runtime.

The declared limits are 1,024 events and a prepared maximum no greater than
65,536 frames. Positive processing performs 91 source evaluations per frame.
Connected mixing visits 91 sustain entries and, while percussion is eligible,
91 harmonic entries. Nominal contact advancement examines 122 keys and at most
1,098 thresholds per frame; idle keys bypass their threshold loops.

Engine performs at most **one complete coefficient rebuild per rendered frame**.
The dirty flag can come from an event cluster, a previous zero-frame flush or
contact edges produced after the preceding sample. Moving nominal contacts can
therefore rebuild coefficients even when there are no new events. The earlier
`min(frames, event_count + 1)` bound described the ideal-contact path; the general
conservative bound for the enabled nominal model is `frames`. Zero-frame flushes
set targets and dirty flags but perform no coefficient rebuild. These are bounded
work counts, not CPU timings or guarantees that a host budget fits.

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

## Enabled console and typed-input observation

[tests/test_realtime_console.cpp](../tests/test_realtime_console.cpp) reuses the
portable overload replacements and all-overload calibration in a separate test
executable. Every observed region contains one public API call. Fixture creation,
profile loading, preparation, fixed-state snapshots, output filling, result checks
and reporting remain outside recording. The first positive Engine call is
observed, including its first source sine evaluations in this executable.

The frozen-tree GCC 14.2 Release gate on 2026-11-13 passed **1/1 CTest suite in
0.68 seconds**, with zero observed C++ allocations/deallocations in every category:

| Observed category | Accepted | Rejected | Additional scope |
| --- | ---: | ---: | --- |
| Enabled Engine processing | 63 | 18 | 218,193 elapsed frames; 15,012 consumed Engine events |
| Owned-input processing | 24 | 21 | 204,636 elapsed frames; 7,011 consumed host commands; 6,879 translated physical events |
| Standalone ownership translation | 3 | 3 | 1,312 consumed host commands; 1,268 physical events; no Engine time advancement |
| Parameter APIs | 130 | 7 | All 43 descriptors, normalized-to-event and plain-to-normalized conversions, plus invalid inputs |
| Stopped sample-rate lifecycle | 6 | 8 | Same-rate no-ops, all three transition destinations, invalid rate/profile and unprepared rejection |

The 126 Engine/facade calls include **87 accepted and 39 rejected requests** and
422,829 elapsed model frames. Frame totals include disconnected processing.
Parameter and standalone ownership APIs are rate-independent; Engine, owned-input
and ordinary lifecycle scenarios are exercised at 44.1, 48 and 96 kHz. The
14 stopped lifecycle observations are reported separately from processing. No
native host/device transition or callback deadline is established by them.
Calibration independently observed 12 allocations and 12 deallocations, excluded
from all category counts.

The enabled fixtures cover all 122 moving keys, partial harmonic contact closure
before the ninth detector, full press and shared decay, Cancel recovery while the
physical detector remains closed, reselect, partial reversal, all 43 converted
controls, 1,024 distinct-offset events and same-offset zero-frame dispatch,
connected/disconnected equivalence, release, panic and the maximum 65,536-frame
block. Rejected Engine requests include a nonfinite final partial target after
1,023 valid events, out-of-range partial targets and ideal-mode partial rejection.
Checks ensure the intended contact/readiness paths were reached; this suite does
not replace the independent numerical/PCM acceptance tests.

Ownership observations exercise 256 retained owners, remapped bus destinations,
channel release, all 1,024 translated output slots and output-capacity failure.
The facade rejects both translator errors and an Engine buffer error after a
successful tentative release; ownership, copied Engine state and output remain
unchanged. Clock exhaustion rejects positive work but permits a zero-frame owned
note command. Direct partial/panic commands use a different Engine instance from
owned-note scenarios, preserving the sole-note-authority contract.

This local scope has no C/system allocator, lock or I/O interception and no timing
threshold. The project-controlled call graph contains none of those explicit
operations, but platform runtime internals and cold-start behavior outside the
observed entry points remain separate questions. The original test's hosted
results do not automatically qualify this new executable. The integrator must
retain its combined source gate and observed hosted matrix separately.

## Reproduction

From the repository root, with a C++20 compiler and the normal CMake prerequisites:

```sh
cmake -S . -B ../agent28-release -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build ../agent28-release --target test_realtime --parallel 2
ctest --test-dir ../agent28-release -R '^test_realtime$' -C Release --output-on-failure -V
```

CMake discovers `test_realtime.cpp` through the existing `test_*.cpp` rule; this
work adds no build-system dependency or CMake edit.

The enabled-path test uses the same normal CMake test discovery:

```sh
cmake -S . -B ../enabled-realtime-release -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build ../enabled-realtime-release --target test_realtime_console --parallel 2
ctest --test-dir ../enabled-realtime-release -R '^test_realtime_console$' \
  -C Release --output-on-failure -V
```

Both commands should be run from a coherent identified source checkout. Rebuild
the library and test together after a public header or callback dependency changes.
