# Assignment 29 — transactional ownership and Engine processing

Agent: `/root/w05_a29_input_processor`

Wave: 05, assignment 29 of the continuation's 60 new assignments

Date: 2026-11-13 UTC

## Scope and evidence basis

Read the standing instructions, current handoff/plan, atlas review, public
ownership and Engine contracts, and the complete extracted atlas pp. 130, 132
and 151. These pages separate host ownership from physical keys and dynamic
history, require retained destinations and deterministic ordering, and distinguish
software bookkeeping evidence from physical instrument behavior.

The assigned work was a small allocation-free transaction joining the already
implemented `NoteOwnership` and `Engine` APIs. No Engine, Types, ownership-module,
CMake, shared status/log, registry or persistence changes were authorized or made.
No commits, pushes, index changes or subagents were made by this assignment.

## Implemented files and contract

- `include/hammond/InputProcessor.h`
- `src/InputProcessor.cpp`
- `docs/INPUT_PROCESSOR.md`
- This assignment note.

The frozen API is:

```cpp
InputProcessResult process_owned_notes(
    Engine&, NoteOwnership&, std::uint32_t frames,
    std::span<float> mono_output,
    std::span<const HostNoteEvent> input) noexcept;
```

`InputProcessResult` returns `status`, `host_events_consumed` and
`physical_events_consumed`, with `ok()` and an explicit Boolean conversion.
Both counts are zero on any rejection. All host commands are consumed on success,
including accepted no-ops; a channel release can emit several physical events.

The wrapper copies ownership, translates into a fixed 1,024-event array, invokes
Engine with exactly the emitted prefix, and installs ownership last. It relies
on Engine's whole-call preflight, so it does not copy the complete engine for
every audio block. The ownership type must remain trivially copyable, enforced
by `static_assert`. No fallible operation follows Engine success.

Translation runs before Engine admission; this fixes error precedence, including
`InvalidEvent` ahead of `NotPrepared` when both apply. The API introduces no
input retry, silent output clearing, owner reset, manual panic or arbitrary
note/control stream merge. Existing zero-frame, disconnected-output, stable-tie
and suffix-preservation semantics remain effective.

The documentation specifies single note authority, exact safe channel-release
payloads, coordinated preparation/panic requirements and retained routing. It
keeps raw MIDI, native host qualification, thread publication and callback
deadlines outside the implemented claim. This is software policy, not a new
physical model or a measured parameter set.

## Build and focused checks

The initial strict Release `hammond_core` build against the working source passed.
While that build completed, another assigned agent added a sample-rate field to
`TonewheelBank`. The first scratch harness was then compiled against the changed
live header but linked to the earlier static library. It failed its inline
`Engine::frame_clock()` assertion. The library's timestamp preceded the changed
header by about 16 seconds. The additional member changes Engine member offsets;
mixing those headers and objects is not a coherent executable.

This failed scratch artifact was retained and reported to the integrator and
independent test agent. No production behavior or assertion was changed to make
it pass. Verification was moved to a frozen source snapshot so that concurrent
header edits could not affect attribution.

The coherent snapshot uses staged base tree
`81bbceb5b01673f1412026fefb83da1442ce5aae` plus four explicit overlays:

| Overlay | SHA-256 |
| --- | --- |
| `include/hammond/NoteOwnership.h` | `03baaa46de8c24d346c86a64a09e0503e85b78854d143a1cd616aeda38e4b1dc` |
| `src/NoteOwnership.cpp` | `f16e7a2f1698898a5552f73004992fb16225b1247d4e0f3170cca201e78b5751` |
| `include/hammond/InputProcessor.h` | `2a454e05652d166602120f5ed912ba85575738d65b5fa9563ce20dc92fc1c8df` |
| `src/InputProcessor.cpp` | `d5543a2e4fbd34114da30ac28430130e4b5b5d00110c8c29cae80c85986a76fc` |

The frozen inputs are in `/workspace/scratch/60e8291da354/a29-frozen-src`;
their manifest is `/workspace/scratch/60e8291da354/a29-input-build/frozen-inputs.json`.
No in-flight sample-rate lifecycle changes are included in that scoped evidence.

Executed commands:

```sh
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  -S /workspace/scratch/60e8291da354/a29-frozen-src \
  -B /workspace/scratch/60e8291da354/a29-frozen-build \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  --build /workspace/scratch/60e8291da354/a29-frozen-build \
  --target hammond_core hammond_profile -j 4
c++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion \
  -Wsign-conversion -Wshadow -Werror \
  -I /workspace/scratch/60e8291da354/a29-frozen-src/include \
  /workspace/scratch/60e8291da354/a29-input-build/smoke.cpp \
  /workspace/scratch/60e8291da354/a29-frozen-build/libhammond_core.a \
  -o /workspace/scratch/60e8291da354/a29-frozen-build/smoke
/workspace/scratch/60e8291da354/a29-frozen-build/smoke \
  /workspace/scratch/60e8291da354/a29-frozen-build/nominal.b3p
```

The coherent strict GCC 14.2.0 Release build passed. The unchanged scratch harness
then passed **17,844 assertions**, with no wrapper or Engine change. The count
includes repeated comparisons of all 122 keys/contact snapshots and all 91 source
phases; it is not a count of independent musical scenarios.

The smoke covers both ideal and nominal contact models with enabled percussion:

- Two owners produce one physical press; identified duplicates consume host
  commands without emitting an extra physical event or freezing elapsed audio.
- First-owner release retains the key; final-owner zero-frame release preserves
  source time and output while changing only the intended physical target.
- Disconnected lower-manual processing agrees with explicitly supplied physical
  events in every inspected dynamic state.
- Engine rejection for short output, prepared block limit and clock overflow
  preserves ownership, all output entries, all inspectable state and subsequent
  one-frame behavior against an untouched Engine copy.
- A late identified-pitch conflict and a 257th owner reject the complete call.
- Unprepared Engine rejection and translation-before-Engine error precedence.
- Channel release retires all 256 same-key owners with one final physical release.
- Successful output leaves its unused suffix untouched.

Observed object sizes are 3,328 bytes for ownership, 16 for Event and 12 for the
result. The wrapper and nested translator declare two ownership copies and two
1,024-event arrays, totaling 39,424 bytes before other locals, stack frames or
compiler optimization. This is a build observation, not an exact portable stack
budget or an allocation-instrumentation result.

All four owned files passed explicit UTF-8, final-newline and trailing-whitespace
checks; all seven local documentation links resolved. The no-index Git comparison
against `/dev/null` emitted no whitespace diagnostics. Its normal new-file
difference status is 1; the scratch hygiene checker initially expected 0 and was
corrected to distinguish that status from an actual diagnostic. No repository
file change was needed for that checker correction.

## Handoff and remaining gates

Assignment 30 received the frozen API, status precedence and the coherent-source
snapshot. It subsequently reported a passing frozen-source Release CTest gate
(1/1) with no wrapper mismatch; its own note retains the independent methods,
counts and source identities. Those tests own wider ownership/Engine interaction,
partitioning, rejection and future-audio evidence. The integrator should include
the four files above in the wave-05 checkpoint, compile the complete exact staged
source, run the full applicable gate and observe hosted CI before qualification.

Later lifecycle integration must rebuild every affected consumer against the
same headers. Allocation instrumentation, stack/deadline measurement on actual
hosts, platform qualification, native event decoding, transport/sustain policies
and physical contact/percussion fidelity remain separate tasks.
