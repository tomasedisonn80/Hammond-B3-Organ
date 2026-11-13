# Assignment 24 — independent combined-input acceptance

Owner: /root/w04_a24_input_acceptance

Wave: 4 of 10. Assignment: 24 of 60 in this pedal development session.

## Scope and decision

Added [test_performance_acceptance.cpp](../../../tests/test_performance_acceptance.cpp)
to independently qualify the new combined manual, pedal and control input
transaction. No production code, existing test, shared status file, build file,
fixture, profile or atlas bytes were edited by this assignment. The integrating
agent owns commits and publication.

The source basis is the shared-source and separate-contact requirement on atlas
pp. 139–140, the framework-independent bounded request on pp. 385–386, and the
musical-state/history distinction on p. 389. These pages were read from the
retained complete text extraction. The adopted implementation contracts are
[manual ownership](../../NOTE_OWNERSHIP.md),
[pedal ownership](../../PEDAL_NOTE_OWNERSHIP.md), and the frozen public
[PerformanceInput interface](../../../include/hammond/PerformanceInput.h).
This is software acceptance of those named policies, not physical pedal or
contact calibration and not native VST3 host qualification.

## Independent reference

The expected path feeds explicitly declared physical `Event` timelines into a
separate prepared Engine. It never invokes either ownership translator or the
combined facade. Controls appear in their declared global order; the physical
note/release list is written from the scenario's known owner history. The large
capacity fixture separately declares 122 manual targets and 25 pedal targets,
with the repeated-owner retirement order explained in its reference list.

Both paths receive the same profile, contact model, rate, seed and initial
clock. The test compares float audio by bits, all 91 source phases by bits,
complete copied observable Engine state, exact consumed counts, and untouched
output tails. The state record includes all manual targets/contact snapshots,
pedal targets and all 200 contact bits, musical controls, percussion diagnostics,
and the historically tagged last-rendered pedal frame.

This reference establishes input translation, ownership and transaction
equivalence to the core's physical-event interface. It does not independently
derive the Engine's DSP equations; that is the separate CSV/voice/source work in
earlier assignments. Source review also confirmed the facade contains one direct
`Engine::process` call after candidate translation, followed only by nonthrowing
owner commits. Clock and phase checks execute that single-timeline behavior.

## Executed cases

- A mixed performance with identified repetitions, overlapping channels and
  origins, anonymous FIFO release, missing releases, zero-velocity release,
  lower Cancel, independent pedal control changes, percussion, reselection and
  scoped channel panics. It runs at 44.1, 48 and 96 kHz with both ideal and nominal
  travel contacts. Four partition schedules include one-sample, irregular and
  single-block calls; samples are also compared directly with the whole render.
- Positive disconnected output followed by connected output, confirming equal
  future state/audio; zero-frame flushes and same-offset control/note ties;
  one supported stopped rate change with held pedal ownership.
- Manual route changes after ownership begins. Explicit owner rows verify that
  an anonymous release retires the oldest original Upper owner even after that
  origin routes new owners to Lower. Pedal origins remain a separate namespace.
- Simultaneous 256 manual plus 256 pedal owners covering all 122 manual physical
  keys and all 25 pedals. The 257th owner in each namespace rejects atomically.
  Scoped panics expand an 880-record input into exactly 1,024 physical events;
  one additional control rejects the 1,025-event candidate with owners intact.
- Exactly 1,024 raw unmatched releases, rejection at 1,025, hard-bound precedence,
  and a 65,536-frame disconnected call with an exact clock increment.
- Forbidden direct note, partial-key and division-panic alternatives; malformed
  control/host payloads; identity conflicts; cross-alternative decreasing offsets;
  positive end offsets; nonzero zero-frame offsets; undersized output; unprepared
  Engine; prepared block bound; and absolute-clock overflow.
- Every rejected request preserves both owner objects, the full observable
  Engine state and all output sentinels. The 39 prepared rejection cases also
  execute a subsequent accepted reference comparison to detect hidden changes
  that affect later audio. The two unprepared cases cannot render a future probe.

## Coherent source and commands

The base is published commit
`e493b9fed9e3ed8a294fb5d95af447132776cb3a`, tree
`056a912a1e407d8d0a842442463fd487bf907690`. It was exported with `git archive`
into `/workspace/scratch/f364bc93d920/a24-input-acceptance/source`. Only the four
explicitly frozen dependency files below and this new test were overlaid. The
freeze came directly from assignments 19 and 22; active renderer/evidence/test
edits were excluded. Every copied file was hash-checked again against the live
frozen source after execution.

| Overlay file | SHA-256 |
| --- | --- |
| `include/hammond/PedalNoteOwnership.h` | `3df590c6747f01a19651b2220b3c002422c8934ff06710bc97be8f47c4747d33` |
| `src/PedalNoteOwnership.cpp` | `a938f9d03a1a05d20cdf5d41567bd9c44bd3f5581ec446897ef79386d148acde` |
| `include/hammond/PerformanceInput.h` | `f3b4185393da324ab1433514f141e42aab1056d7dac4fd402184b1c2d0dd04ae` |
| `src/PerformanceInput.cpp` | `fc9d3775ad1d3faf23beacb52c6c78108f967e8e7d209b74ef56e1a9caa44030` |
| `tests/test_performance_acceptance.cpp` | `52ec55dd6a560a4bf93d9e46b7ba5e4b7af450521705ade996509b3ebe75aa9e` |

The build used GCC 14.2.0 and CMake 3.31.6. The executed CMake commands were
issued by a checked `subprocess.run` sequence; the exact invocations were:

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake -S /workspace/scratch/f364bc93d920/a24-input-acceptance/source -B /workspace/scratch/f364bc93d920/a24-input-acceptance/build -DCMAKE_BUILD_TYPE=Release
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake --build /workspace/scratch/f364bc93d920/a24-input-acceptance/build --target test_performance_acceptance -j 4
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/ctest --test-dir /workspace/scratch/f364bc93d920/a24-input-acceptance/build -R '^test_performance_acceptance$' --output-on-failure -V --output-junit /workspace/scratch/f364bc93d920/a24-input-acceptance/ctest.xml
```

The observed compile flags include `-O3 -DNDEBUG -std=c++20 -Wall -Wextra
-Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror`. Release assertions
remain active through the repository's `CHECK` support.

## Actual result

**Final Release CTest: 1/1 passed, zero failures, 0.60 seconds total.** The
individual test reported 0.59 seconds. No production defect, build failure or
runtime repair was found. The first run also passed; its counter display was
then refined to distinguish all rejected calls from the prepared subset that
can execute future audio, followed by the focused rebuild and final run above.

| Executed comparison | Count |
| --- | ---: |
| Accepted facade calls with exact counts/output/state | 12,660 |
| Atomic rejection cases | 41 |
| Post-rejection accepted future probes | 39 |
| Bitwise facade/reference audio samples | 68,102 |
| Direct whole-versus-partition audio samples | 49,152 |
| Bitwise actual source-phase comparisons | 1,162,434 |
| Complete observable state pairs | 12,778 |
| Explicit surviving owner rows | 1,035 |
| Partition runs across three rates/two contact modes | 24 |

The existing CMake test glob discovers this test without a build-system edit.
The fixture uses ordinary test-only vectors; no allocation or callback-deadline
claim follows from its timing. Enabled-path allocation instrumentation and the
later native module remain separately assigned gates.

## Handoff

Root should include this frozen test with assignments 19–23 in the coherent
wave-4 regression and publish only the qualified source tree. Preserve the
separate typed owner domains, controls-only direct-event arm, stable global
timeline and all-or-nothing owner/Engine/output contract when building the next
automation/native adapter. Native event-bus conversion, automation interpolation,
concurrent state publication and actual host/device operation are outside this
assignment's executed scope.
