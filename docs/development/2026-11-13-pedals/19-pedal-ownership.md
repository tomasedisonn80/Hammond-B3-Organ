# 19 — typed pedal note ownership

Owner: /root/w04_a19_pedal_ownership

Wave: 4. Assignment: 19 of the new session's 60.

## Scope and implementation

Implemented an independent typed pedal ownership adapter with two logical origin
buses, sixteen channels per origin, 256 fixed owners and explicit one-based
`PedalId` input. The public header was frozen and sent to the integrator before
the deeper test work. No manual enum, MIDI octave, core event value or existing
manual ownership behavior changed.

First-owner/final-owner emission, idempotent identified repetitions, conflicting
identity rejection, anonymous FIFO releases and scoped channel panic preserve
overlapping owners. Output contains only canonical-Lower `PedalOn`/`PedalOff`.
The translator validates the entire static payload/timeline, simulates on a
private value copy, and commits only after owner/output capacities and identity
checks succeed. It preserves output tails and all live state on failure.

Owned files only:

- `include/hammond/PedalNoteOwnership.h`
- `src/PedalNoteOwnership.cpp`
- `tests/test_pedal_note_ownership.cpp`
- `docs/PEDAL_NOTE_OWNERSHIP.md`
- This assignment note.

The existing CMake source/test glob discovers these files. No CMake, shared
status/manifest, Engine, manual ownership, renderer or other worker file was
edited. No commit, push or child-agent dispatch was performed by this worker.

## Coherent source and commands

Copied the root's frozen wave-3 source tree
`24f80c3e8405fa0a49500a080967279e615a9b97` from
`/workspace/scratch/f364bc93d920/checkpoint-w03/source` to
`/workspace/scratch/f364bc93d920/a19-source`, then overlaid only the three owned
C++ header/implementation/test files. Concurrent renderer/evidence work was not
included. This avoids linking a core against a different live header layout.

Exact verification commands:

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake \
  -S /workspace/scratch/f364bc93d920/a19-source \
  -B /workspace/scratch/f364bc93d920/build-a19 -DCMAKE_BUILD_TYPE=Release
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake \
  --build /workspace/scratch/f364bc93d920/build-a19 \
  --target test_pedal_note_ownership test_note_ownership --parallel 3
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/f364bc93d920/build-a19 \
  -R '^(test_pedal_note_ownership|test_note_ownership)$' --output-on-failure -V
```

Toolchain: GCC 14.2.0, CMake/CTest 3.31.6, Python 3.12.14, Linux x86-64.
The normal project warnings are errors. The build completed without warnings
or repairs. Both selected Release suites passed on their first execution:
**2/2 passed, zero failures, 0.03 seconds**.

| Executed new-suite observation | Count |
| --- | ---: |
| Accepted calls checked with declared physical output and untouched tails | 74 |
| Rejected whole calls checked for unchanged state/output and future events | 59 |
| Exact physical event comparisons | 1,454 |
| Exact surviving owner rows | 1,073 |
| Positive block partition sizes compared with whole-call output/state | 7 |
| `sizeof(PedalNoteOwnership)` on this ABI | 2,112 bytes |

The acceptance scenarios include every one of 25 pedals across all 32 logical
origin/channel pairs, endpoint velocities and identities, repeated anonymous and
identified owners, shared-pedal scoped panics, equal-offset release/repress,
all malformed field categories, late invalid rollback, one-over owner capacity,
release-then-reuse, exactly 1,024 emitted events, and a 1,025-output rejection
despite fewer than 1,024 raw inputs and a larger caller buffer. An unchanged
manual adapter test also passed its existing 2,127 accepted-call and 2,264
atomic-rejection cases; those are prior tests, not new pedal case counts.

The new type's trivial copy and nonthrowing value operations are compile-time
checked. Runtime allocation counters were not added in this assignment.

## Tested file identities

| File | SHA-256 |
| --- | --- |
| `include/hammond/PedalNoteOwnership.h` | `3df590c6747f01a19651b2220b3c002422c8934ff06710bc97be8f47c4747d33` |
| `src/PedalNoteOwnership.cpp` | `a938f9d03a1a05d20cdf5d41567bd9c44bd3f5581ec446897ef79386d148acde` |
| `tests/test_pedal_note_ownership.cpp` | `417b7c61735c0d3c7cc66de20ffed9b8e7aec02471d9136a6e1ee24a1967aa15` |

The retained focused build has a matching header, core and consumers. Root's
combined checkpoint must still test its final merged source and observe the
published revision's hosted results.

## Handoff and remaining scope

The next dependency-ready step is a unified manual/pedal/control input
transaction: copy both owner adapters, translate and merge in stable order,
process the elapsed frame range once, and install owners only after Engine
accepts the full call. Keep direct physical panic/reprepare coordinated with
both owner ledgers. The header provides the value-copy, query and snapshot
surface needed for that integration.

This adapter does not decode MIDI, implement native VST3, render audio, save
musical controls, advance sources, measure pedal loading/contact behavior or
establish a callback deadline. Those gates remain with the implementing and
independent qualification assignments. All software-origin policy is explicit
and separate from the atlas's physical pedal evidence.
