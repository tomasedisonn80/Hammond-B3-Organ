# Assignment 43 — enabled console and input allocation audit

Agent: `/root/w08_a43_enabled_realtime`

Date: 2026-11-13 UTC. Wave 08, assignment 43 of this continuation's 60 workers.

## Scope and source boundary

Added [test_realtime_console.cpp](../../../tests/test_realtime_console.cpp) and
updated [REALTIME.md](../../REALTIME.md). No production, existing test, build,
shared status or other agent file was changed. The integrator owns staging,
publication and the combined hosted gate; this assignment made no index changes,
commits, pushes or subagents.

Read the standing instructions, current handoff/plan/review and relevant public
contracts. Read all of atlas pp. 379-390, whose proposals separate bounded prepared
processing, ownership, allocation checks, deadline measurements and stopped
lifecycle work. The test qualifies the implemented nominal core and typed
adapters; it does not inherit execution claims from the atlas's reference header.

The parent froze Git tree `b9146546fcf756360e1da89d6698c4999359579f`, containing
published lifecycle commit `53bb6e1` plus assignments 37-40's partial-key/trace
extension. Qualification extracted that exact tree into an isolated directory,
then added only this new test. All 290 base-tree blobs were checked against Git
after execution, and the test bytes matched the repository file. No later live
header was linked against this frozen library.

## Observed result

Strict GCC 14.2 Release compilation succeeded on the first build. The focused
CTest passed **1/1 suite in 0.68 seconds**, with no skipped tests, build failure,
runtime assertion failure or production defect. All checks remain active with
`NDEBUG`. Every guarded API observation reported **zero C++ allocations and
zero C++ deallocations**.

| Category | Accepted | Rejected | Successful work observed |
| --- | ---: | ---: | --- |
| Enabled `Engine::process` | 63 | 18 | 218,193 elapsed frames; 15,012 Engine events |
| `process_owned_notes` | 24 | 21 | 204,636 elapsed frames; 7,011 host commands; 6,879 physical events |
| Standalone `NoteOwnership::translate` | 3 | 3 | 1,312 host commands; 1,268 physical events |
| Parameter APIs | 130 | 7 | Descriptor enumeration plus lookup, normalized and plain conversion for all 43 controls |
| Stopped `reconfigure_sample_rate` | 6 | 8 | Same-rate and changed-rate success; invalid rate, profile and unprepared rejection |

There are 283 guarded API observations in total. The 126 Engine/facade processing
calls comprise 87 accepted and 39 rejected calls and 422,829 elapsed model frames.
Disconnected frames remain in those totals. Translation does not render frames;
its physical outputs are counted separately from facade outputs. Direct Engine
input counts include controls and key events, so they are not labeled translated
physical events. Parameter and standalone ownership APIs are rate-independent;
Engine, facade and ordinary rate scenarios run at 44.1, 48 and 96 kHz.

## Instrumentation and reached paths

The new executable reuses the existing test's portable global scalar/array,
nothrow, sized, aligned and aligned-sized `new`/`delete` replacements. Its
independent calibration exercised all eight allocation and twelve deallocation
overloads through volatile function pointers, observing exactly 12 allocations
and 12 deallocations. Checked over-allocation plus `std::align` retains a malloc
base for aligned storage. Calibration is excluded from the API counts; volatile
is not used as synchronization.

A guarded lambda contains one public API call. Fixture construction, profile
loading, preparation, output allocation/filling, snapshots, assertions and report
formatting are outside recording. Fixed thread-local counters record only calls
on the observed thread. The first positive Engine call includes the first source
sine evaluations in this executable's processing workload.

The Engine fixture exercises all 122 keys moving to partial holds, the harmonic
contact before the ninth detector, full press and shared decay, maximum 65,536-
frame processing, Cancel recovery with the physical detector still closed,
reselect, partial reversal, all 43 converted controls, 1,024 distinct-offset and
same-offset events, zero-frame calls, connected/disconnected state equivalence,
normal release and immediate panic. State assertions confirm that partial
contacts, detector gating and recovery paths were actually reached. Invalid
requests include the 1,024th event's nonfinite target, a finite out-of-range target,
ideal-mode partial rejection, insufficient output, excess block size and events.

Ownership reaches all 256 owner slots, preserves original routes after remapping,
releases channels, fills all 1,024 translated output slots and rejects an output
capacity of 1,023 without mutation. Facade coverage includes translator rejection
and a successful tentative physical release followed by Engine buffer rejection.
Both retain live ownership, copied Engine state and output. At an exhausted clock,
positive processing rejects while a zero-frame owned note is accepted. Owned-note
instances never receive uncoordinated direct partial-key or panic commands.

The lifecycle observations are separate stopped/same-thread work. They include
partial-motion continuity, exact same-rate no-ops, all three target rates,
unsupported/NaN rates, unprepared use and a source at 30 kHz that can prepare at
96 kHz but rejects 48 kHz. These observations do not authorize concurrent rate
publication or establish host/device transition behavior.

## Audit finding and correction

The current graph uses two fixed 91-element coefficient arrays for sustain and
percussion. Events and contact edges can mark them dirty. Nominal contact motion
can therefore trigger rebuilding without another input event. `REALTIME.md` now
states the general bound of **at most one complete rebuild per rendered frame**,
and identifies the old `min(frames, event_count + 1)` bound as ideal-contact scope.
The original 96-call result remains explicitly historical ideal/off evidence.
No runtime correction was needed.

The updated source audit follows Engine, ContactBank, PercussionState,
TonewheelBank, ControlState, NoteOwnership, InputProcessor and ParameterBridge.
It records fixed arrays, 122-key/1,098-contact traversal, at most 256 examined
owners per ownership operation, 1,024-event capacity and 43 literal descriptors.
No explicit project-controlled callback path performs allocation/free, file or
stream I/O, logging, locking, atomics, worker submission or unbounded retry.
Percussion exponentials are confined to preparation and stopped rate changes.

## Reproduction and retained identities

Commands actually run, with the frozen archive and single test overlay already
prepared:

```sh
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  -S /workspace/scratch/60e8291da354/a43-qualified-src \
  -B /workspace/scratch/60e8291da354/a43-qualified-build \
  -DCMAKE_BUILD_TYPE=Release
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  --build /workspace/scratch/60e8291da354/a43-qualified-build \
  --target test_realtime_console --parallel 3
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/60e8291da354/a43-qualified-build \
  --output-on-failure -V -R '^test_realtime_console$'
```

The test compile used `-O3 -DNDEBUG -std=c++20 -Wall -Wextra -Wpedantic
-Wconversion -Wsign-conversion -Wshadow -Werror`. CMake's existing test glob
registers the executable; no new dependency or build-system modification is needed.

| File / artifact | SHA-256 |
| --- | --- |
| New test | `b53fa32fedd85d72248a866cc4d84569bcd0e5edcfd3c2757f73410c8ec54d3f` |
| Frozen Engine.cpp | `53c07390447796f4c57e96e58b9d6720df76094e14a0e6240b284f62e4310ccf` |
| Frozen Engine.h | `efb8f0eb36dccbe5f0416186ef9478091be48e5634cfd6a8f0155b3dfd1c81c0` |
| Frozen ContactBank.cpp | `91747d963d6cec74b3be12549abd8e816f4c176ce172fba52f9cdbc593c6e9e1` |
| Frozen Percussion.cpp | `823685b879fad12492f86bbf5e78294668ee9b0567c58c26ac0b44aa28b1390a` |
| Frozen TonewheelBank.cpp | `ebc26e2e61cc88d5525e390abf3897ebeae38e652c13ea3ef02818b2b3849e0b` |
| Frozen NoteOwnership.cpp | `f16e7a2f1698898a5552f73004992fb16225b1247d4e0f3170cca201e78b5751` |
| Frozen InputProcessor.cpp | `d5543a2e4fbd34114da30ac28430130e4b5b5d00110c8c29cae80c85986a76fc` |
| Frozen ParameterBridge.cpp | `e6dc1b0e1721e00fd89b3f2614f97ecd9b4aaf9bffd998468185c15fd15627e5` |
| Qualified executable | `1db31782590b39b4c7b8219cec77518c365d37d116699559eb61987b54fd02c4` |
| Generated nominal.b3p | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |

Scratch paths identify this observed run; permanent reproduction uses the retained
repository test and a newly identified coherent checkout, not these directories.

## Limits and next gate

The hooks do not interpose C heap functions, operating-system allocation,
class-specific/custom allocators, independently linked runtimes or other threads.
They do not dynamically intercept locks or I/O. Static project-source inspection
does not prove the behavior of every platform's math/runtime internals. No timing
threshold, native host/device callback, concurrency, cold-start campaign, physical
measurement or fidelity claim follows from this short CTest run. The stopped
lifecycle observations are not callback deadline evidence.

The integrator should include the new suite in the exact combined staged-source
build and retain the actual Linux/macOS/Windows/sanitizer results. A prior hosted
run cannot qualify a test it did not contain. Further target work remains C/system
allocator and lock/I/O interception, actual bounded native callback telemetry,
loads and deadline qualification, and a separately verified concurrent ownership/
retirement protocol when live profile exchange is implemented.
