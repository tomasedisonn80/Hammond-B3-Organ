# Assignment 25 — bounded external note ownership

Agent: `/root/w05_a25_note_ownership`

Wave: 05, assignment 25 of this continuation's 60 new agents

Date: 2026-11-13 UTC

Disposition: scoped implementation and initial smoke complete; independent
permanent tests and Engine transaction integration remain separate assignments.

## Inputs and scope

Read `AGENTS.md`, README, current status/next-step/log, `PLAN.md`, the retained
atlas review, `ENGINE_API.md` and `CONSOLE_DYNAMICS.md`. Read the complete extracted
atlas pp. 130, 132 and 151. They propose fixed host ownership, explicit repeated-note
policy, stable event order and retention of a held note's original destination.
The implementation labels these as software policy, not physical measurements.
The source PDF remains unchanged; its retained SHA-256 is
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.

Owned changes only:

- `include/hammond/NoteOwnership.h`
- `src/NoteOwnership.cpp`
- `docs/NOTE_OWNERSHIP.md`
- This note

No Engine, existing types, CMake, shared status, other tests, commits or pushes
were changed. The integrator publishes and updates the shared handoff. No child
agents were spawned. The public API was frozen and sent to the integrator before
implementation for the independent test/wrapper assignments.

## Implemented decisions

`bounded-fifo-note-ownership-v1` admits typed On/Off/channel-AllNotesOff commands
on two buses and sixteen channels per bus, within manual MIDI 36–96. Signed
32-bit note IDs accept -1 for unidentified notes and nonnegative identified notes.
Default bus routes are Upper/Lower. The public contract is fully documented in
`NOTE_OWNERSHIP.md` and the header.

The adapter stores at most 256 owners in surviving insertion order. Identified
duplicates are idempotent; conflicting pitch reuse rejects. Unidentified repeats
add owners and release FIFO without touching identified owners. Both release
kinds accept an absent match as a no-op. Each owner retains its original manual
through route changes. First and final physical ownership emit NoteOn/NoteOff;
intermediate changes emit nothing. Channel AllNotesOff retires only its original
bus/channel owners and emits final releases in retirement order, never an Engine
manual panic. Positive-velocity NoteOn passes that first owner's velocity through;
the engine's sustained-amplitude independence remains unchanged.

Structural preflight precedes bounded candidate-state application. The caller's
output and installed state are untouched until all commands succeed. Invalid
payload, offset, ordering, identity conflicts or exhausted input/owner/output
capacity return zero consumed/emitted counts. Output capacity is capped at 1,024
even if a larger span is supplied, and its untouched tail is preserved. Maximum
block length is 65,536, using the existing half-open/zero-frame offset convention.

Private fixed physical counts bound every key at 256 owners. Individual lookup
and removal scan at most 256 records; channel retirement compacts in one pass.
There is no allocation, file operation, logging, lock, source or percussion state
in this implementation. This is a source-inspection property; an instrumented
enabled-path allocation/deadline audit remains a separate gate.

No internal overflow counter changes on rejection because complete-state atomicity
is required. Callers can count returned failures outside this state. There is no
reset API that silently leaves Engine keys stranded; global panic/replacement
must coordinate both layers explicitly.

## Executed checks

From the repository root:

```sh
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  -S . -B /workspace/scratch/60e8291da354/a25-ownership-build \
  -DCMAKE_BUILD_TYPE=Release
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  --build /workspace/scratch/60e8291da354/a25-ownership-build \
  --target hammond_core -j 4
c++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion \
  -Wsign-conversion -Wshadow -Werror -I include \
  /workspace/scratch/60e8291da354/a25-ownership-smoke.cpp \
  /workspace/scratch/60e8291da354/a25-ownership-build/libhammond_core.a \
  -o /workspace/scratch/60e8291da354/a25-ownership-smoke
/workspace/scratch/60e8291da354/a25-ownership-smoke
```

Observed GCC 14.2.0 Release core compilation: passed under the repository's strict
warnings-as-errors configuration. Concurrent Make emitted a jobserver FIFO
already-exists notice, but all compilation/link steps completed successfully with
exit status zero. No source repair or weakened compiler setting was needed.

Observed smoke result: **35 assertions passed**. They cover default and rejected
routes, identified duplicate and absent release, FIFO release across remapping,
channel-only AllNotesOff while another channel holds the same key, late identity
conflict rollback, untouched output, zero-output-capacity rollback, copied query
failure behavior, 256 live owners, 257th-owner rejection, 1,025-input rejection,
half-open/maximum block offsets and a generated 1,144-output case rejected despite
a supplied 2,048-entry output span. `NoteOwnership` is trivially copyable.

Observed sizes on this build: `sizeof(NoteOwnership) == 3328` bytes;
`sizeof(Event) == 16` bytes. Translation's fixed event scratch array is 16,384
bytes, plus the candidate object and ordinary local variables. These are observed
build sizes, not a cross-platform ABI or stack-budget qualification.

| Initial checked artifact | SHA-256 |
| --- | --- |
| `include/hammond/NoteOwnership.h` | `03baaa46de8c24d346c86a64a09e0503e85b78854d143a1cd616aeda38e4b1dc` |
| `src/NoteOwnership.cpp` | `f16e7a2f1698898a5552f73004992fb16225b1247d4e0f3170cca201e78b5751` |
| Scratch smoke source | `80409679440b7b3e7b85a8b5a3fde697dc6f3f8cbf5099fa093d734cbe23fe17` |
| Scratch smoke executable | `5c6fce633529b8c89fe4ead85b82c86e01250384adcaab7a0e61d62687522ac6` |

The scratch smoke is initial author verification, not the independently authored
permanent acceptance suite. It is not a repository or CI dependency. Later edits
must be checked against their own identities rather than inheriting these hashes.

## Next step and open gates

Assignment 26 should exercise the frozen public API independently, including
all malformed domains, capacities, FIFO identity separation, channel/bus isolation,
remapped releases, stable ties, output tail preservation and block partitioning.
Assignment 29 should stage an ownership copy, translate, process its exact output
prefix with Engine, then commit the copy only on Engine success. Invalid Engine
buffers/specification/timeline state must leave external ownership unchanged.

No sustain controller, pedal playing ownership, raw MIDI parser, timestamped route
automation, gesture re-strike or native host export is implemented. The adapter
alone provides no physical calibration, callback deadline, device/DAW or complete
M3/M9 qualification. Direct Engine note/panic commands must not compete with this
ownership authority without an explicit coordinated policy.
