# Assignment 22 — unified manual, pedal and control transaction

Owner: /root/w04_a22_performance_input

Wave: 4 of 10. Assignment: 22 of 60. Scope complete; integration and publication
belong to the root agent. No commits, pushes, shared-status edits or child-agent
dispatches were performed.

## Scope and implementation

Read the standing instructions, current status/next steps, the project plan,
existing manual facade/ownership contracts, the frozen pedal owner interface,
Engine rules and relevant atlas pages 130, 132 and 151. The source describes
external note ownership before physical targets, a common timeline, retained
manual destinations and separate controls/physical/DSP histories. The new
bounded transaction is software policy, not measured contact behavior.

Owned files:

- `include/hammond/PerformanceInput.h`
- `src/PerformanceInput.cpp`
- `tests/test_performance_input.cpp`
- `docs/PERFORMANCE_INPUT.md`
- This evidence note.

The public header was frozen and sent to the integrator before deep testing.
`PerformanceInputEvent` is a fixed-storage variant of `HostNoteEvent`,
`PedalNoteEvent` and ordinary control `Event`. The direct Event alternative
rejects physical notes, partial-key input and panics to preserve owner authority.
The model ID is `bounded-single-clock-performance-input-v1`.

`process_performance_input()` checks global offsets and control kinds, translates
on value copies of both owner adapters, appends all emitted notes/controls in
the original global tie order, and calls Engine exactly once. It installs both
owner copies only after Engine accepts the complete prefix. Every failure
preserves both live owner objects, complete Engine state, caller output and
future audio, returning zero consumption counts. Both raw and combined emitted
work have independent 1,024-record bounds; each owner type retains its own
256-owner limit. An expanded channel panic cannot discard a release to fit.

No existing Engine, ownership, manual facade, renderer, build configuration or
saved-state file was changed. The new files are found by the existing CMake
source/test globs. The [contract](../../PERFORMANCE_INPUT.md) records exact
error precedence, zero-frame/disconnected behavior, reset coordination and
the future host adapter's responsibilities.

## Coherent verification inputs

The source copy at `/workspace/scratch/f364bc93d920/a22-source` was created from
the published wave-3 commit:

`e493b9fed9e3ed8a294fb5d95af447132776cb3a`

Its tree is `056a912a1e407d8d0a842442463fd487bf907690`. The copy overlays only
the explicitly frozen three C++ files from assignment 19 and the three C++
files owned by this assignment. Concurrent renderer/evidence changes are not
part of this source/build pair.

| Overlaid path | SHA-256 |
| --- | --- |
| `include/hammond/PedalNoteOwnership.h` | `3df590c6747f01a19651b2220b3c002422c8934ff06710bc97be8f47c4747d33` |
| `src/PedalNoteOwnership.cpp` | `a938f9d03a1a05d20cdf5d41567bd9c44bd3f5581ec446897ef79386d148acde` |
| `tests/test_pedal_note_ownership.cpp` | `417b7c61735c0d3c7cc66de20ffed9b8e7aec02471d9136a6e1ee24a1967aa15` |
| `include/hammond/PerformanceInput.h` | `f3b4185393da324ab1433514f141e42aab1056d7dac4fd402184b1c2d0dd04ae` |
| `src/PerformanceInput.cpp` | `fc9d3775ad1d3faf23beacb52c6c78108f967e8e7d209b74ef56e1a9caa44030` |
| `tests/test_performance_input.cpp` | `94c5f242c82b12294b7601048c24f89cd9e6682b99e6f69fc6cf62b2c812104c` |

All six live files were compared with these tested identities after execution.
The frozen production hashes were sent to assignment 24 for its independent
acceptance work. No production/API changes or failed test/build runs occurred
after the coherent source freeze.

## Commands and observed results

Toolchain: Linux, GCC 14.2.0, CMake 3.31.6, Python 3.12.14. The CMake executable
was `/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake`; `ctest` was
in the same directory. Actual equivalent commands:

```sh
cmake -S /workspace/scratch/f364bc93d920/a22-source \
  -B /workspace/scratch/f364bc93d920/build-a22 -DCMAKE_BUILD_TYPE=Release
cmake --build /workspace/scratch/f364bc93d920/build-a22 \
  --target test_performance_input test_note_ownership \
  test_pedal_note_ownership test_input_processor -j 4
ctest --test-dir /workspace/scratch/f364bc93d920/build-a22 \
  --output-on-failure \
  -R '^(test_performance_input|test_note_ownership|test_pedal_note_ownership|test_input_processor)$'
```

The first strict Release gate passed all four suites in 1.49 seconds. Before
final handoff, the independent physical-event oracle was extended to enable
upper percussion, so the partition checks include its active history. Production
header/implementation identities were unchanged. Rebuilt `test_performance_input`
and reran the same four-suite gate: **4/4 selected suites passed, zero failures,
in 1.06 seconds**:

| Suite | Actual result |
| --- | --- |
| `test_input_processor` | Passed, 0.95 s; existing manual facade unchanged. |
| `test_note_ownership` | Passed, 0.03 s; existing manual owner implementation unchanged. |
| `test_pedal_note_ownership` | Passed, 0.00 s; frozen assignment-19 dependency. |
| `test_performance_input` | Passed, 0.07 s; new transaction acceptance. |

The new suite reported **3,819 accepted calls, 45 atomic rejection/future-audio
checks, 26,250 bitwise audio comparisons, 8,463 bitwise source-phase comparisons,
and 42 partition cases**. Counts come from the executed test's output, retained
in `build-a22/Testing/Temporary/LastTest.log`; they are not planned coverage.

Expected physical events are hand-authored separately from both production
owner adapters. Checks include both contact models at 44.1/48/96 kHz, every
manual key and pedal concurrently, overlapping origins and note identities,
Cancel/reselection, enabled upper percussion, route changes retaining original releases, zero-frame
edits, disconnected output and preserved output tails. Rejections cover
forbidden direct-event kinds, malformed late payloads/identities/offsets,
buffers, block/clock limits, independent full owner tables and combined panic
expansion. A full 1,024-event emitted prefix accepts a final duplicate with no
emission; a required extra release rejects atomically. Rejected candidates are
compared with an untouched copy during a later rendered suffix.

## Limits and next step

This gate establishes the host-independent single-call transaction for the
tested nominal core. No actual SDK module, DAW, raw MIDI packet, hardware
measurement or audio-device deadline was tested. The implementation uses only
fixed storage and nonthrowing value copies; measured enabled-path allocation
and workload qualification remain separate assignments. Whole-callback rollback
across multiple automation slices also belongs to the future wrapper, not this
single-call facade.

The next steps are assignment 24's independent mixed-input review, root's
coherent combined wave-4 regression/publication, and the bounded automation
adapter in assignment 28. Preserve the frozen API and pass the exact Engine
and both owner objects through one coordinated lifecycle. Future snapshots
must continue to exclude owners, phase, moving contacts, readiness and time.

All five owned files passed UTF-8, LF, trailing-whitespace, local-link and owner-identity checks. All six overlaid code/test hashes still match the tested copy.
