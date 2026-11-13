# Assignment 30 — transactional input processor acceptance

Agent: `/root/w05_a30_input_processor_tests`

Wave: 05, continuation assignment 30 of 60

Date: 2026-11-13 UTC

## Scope and source basis

This assignment owns only the new
[test](../../../tests/test_input_processor.cpp) and this note. It independently
checks the cooperation of `NoteOwnership` and `Engine` through
`process_owned_notes()`. It does not replace the separate ownership-policy,
contact/percussion, or core event-admission suites.

The public [ownership contract](../../NOTE_OWNERSHIP.md) and frozen headers were
read before test construction. The [wrapper documentation](../../INPUT_PROCESSOR.md)
was checked when its author completed it. Atlas pp. 130, 132 and 151 provide the relevant original proposal:
separate external ownership from physical keys, retain the original manual,
consume only elapsed time for shared percussion, define bounded repeated-note
policy, and retain event ordering across block partitions. These are software
acceptance criteria, not measured contact physics or native-host qualification.
The project plan, complete-review consolidation, current status/queue/log and
standing [agent workflow](../../../AGENTS.md) were also inspected.

Expected physical events are written explicitly in the test. The oracle neither
calls `NoteOwnership::translate()` directly nor reconstructs its search/erasure
algorithm. Production implementation source was copied for compilation and hashed,
not inspected to derive the expected event timeline. A second actual `Engine`
consumes the independently written physical events. This establishes adapter
integration behavior; it does not independently validate every core DSP formula.

## Implemented tests

Seven behavioral functions provide the following checks:

| Area | Independent expectation |
| --- | --- |
| Engine admission failures | A valid translated note cannot commit ownership when Engine reports InvalidBuffer, BlockTooLarge, TimelineOverflow or NotPrepared |
| Translation failures | Invalid payload/order/offset, late identified-pitch conflict, excess input count, transient 257th owner and output fanout beyond 1,024 reject the whole wrapper operation |
| Rollback | Both result counts are zero; all output bytes, all retained owners, controls, key/contact snapshots, 91 source phases, readiness/routing diagnostics and clock equal an untouched copy |
| Future behavior | Every rejected case continues with the same valid host sequence and produces bit-identical PCM and state; up to 1,024 future samples expose delayed contact/mix effects |
| Channel/bus ownership | Several owners produce one physical key; channel release preserves other owners; only the final owner emits a physical release |
| Manual remapping | Identified duplicates retain their old manual while new owners use the new route; later releases reach the original manual |
| Anonymous FIFO | Unidentified releases span old/new manual destinations in insertion order and cannot retire an identified owner |
| Zero/disconnected calls | Nonempty zero-frame output remains untouched; duplicates and unmatched releases are consumed; disconnected positive output advances exactly the same dynamics |
| Shared readiness | A zero-time off/on gives no recovery; a same-offset positive-call off/on advances exactly one decay sample, compared with the closed-form one-step result |
| Partitions | A fixed 21-command host score matches 12 hand-written physical events across six rate/mode combinations and eleven block/flush realizations per combination |
| Control-only edits | Cancel, hidden-bank changes, percussion changes and reselection coexist with retained ownership; a channel release while cancelled does not strand the other owner |

The failure fanout case uses five complete two-manual cycles: 620 valid host
commands would emit 1,220 physical events while never approaching 256 simultaneous
owners. It therefore checks the wrapper's fixed event-output bound separately
from input and owner capacity. The overflow-clock cases also consume the exact
remaining legal frames and then accept a zero-frame owner change at `UINT64_MAX`.

State comparisons use semantic fields and binary floating-point values, never
`memcmp` over object padding. Invalid calls compare every supplied storage sample,
including bytes outside a deliberately short exposed span. Successful calls check
untouched output tails. All paths under test use valid, non-overlapping caller
storage. Deliberate invalid memory aliasing is outside this API test contract.

## Coherent source snapshot

A first live-tree strict compile succeeded, but it was not used for runtime
qualification. Assignment 29 reported that concurrent sample-rate work had changed
the source-bank layout after an earlier library build. This assignment therefore
built the actual runtime gate from one coherent frozen source tree:

- Base commit: `4ead76957c763afbbddde1bc96f1128384329e50`.
- Archive source: `/workspace/scratch/60e8291da354/a30-frozen-src`.
- Only five completed files were overlaid: ownership header/source, input-processor
  header/source, and this new test. In-flight lifecycle changes were excluded.
- The test was then strengthened to continue rejection probes until nominal
  contacts can close at 96 kHz, and that assigned test file was rebuilt in the same
  otherwise frozen source tree before the qualifying run.

| Frozen input/output | SHA-256 |
| --- | --- |
| `include/hammond/NoteOwnership.h` | `03baaa46de8c24d346c86a64a09e0503e85b78854d143a1cd616aeda38e4b1dc` |
| `src/NoteOwnership.cpp` | `f16e7a2f1698898a5552f73004992fb16225b1247d4e0f3170cca201e78b5751` |
| `include/hammond/InputProcessor.h` | `2a454e05652d166602120f5ed912ba85575738d65b5fa9563ce20dc92fc1c8df` |
| `src/InputProcessor.cpp` | `d5543a2e4fbd34114da30ac28430130e4b5b5d00110c8c29cae80c85986a76fc` |
| `tests/test_input_processor.cpp` | `56411bdc29a6af5788eb93c762b2028ea879971a143d35cb450c94c6a0750614` |
| Built test executable | `f8a475d9b22cf77ff21441252f008eff1d95fe54db459a5b6e5d9d86aaa8d648` |
| Compiled nominal profile | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |

These are observed build identities, not cross-toolchain binary promises. The
permanent test contains no scratch path or saved-binary dependency.

## Commands and observed result

CMake was available through the existing tool installation rather than PATH:

```sh
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  -S /workspace/scratch/60e8291da354/a30-frozen-src \
  -B /workspace/scratch/60e8291da354/a30-frozen-build \
  -DCMAKE_BUILD_TYPE=Release
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  --build /workspace/scratch/60e8291da354/a30-frozen-build \
  --target test_input_processor -j 4
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/60e8291da354/a30-frozen-build \
  --output-on-failure -R '^test_input_processor$' -V
```

The strict GCC 14.2.0 Release build passed with warnings treated as errors. The
focused CTest gate passed **1/1 in 0.89 seconds**, with no skips or implementation
mismatch. Observed test counters:

| Check | Count |
| --- | ---: |
| Wrapper processing calls | 66,072 |
| Rejected whole transactions | 44 |
| Unchanged-future probes after those rejections | 44 |
| Complete public-state comparisons | 814 |
| Hand-authored reference-event applications | 816 |
| Block/zero-flush variants | 66 |
| Bit-exact sample comparisons, including guards | 459,896 |

Both contact modes and 44.1, 48 and 96 kHz were exercised. The timing score is
3,072 samples long; its partitions use 1, 7, 64, 127, 1,024 and 3,072-frame blocks,
with and without boundary flushes as specified by the test. The rejection future
probes consume up to 1,024 samples, or the entire remaining legal interval for the
near-overflow case. No runtime defect was found. The live-tree build's result is
kept separate from this coherent snapshot's observed gate.

## Limits and next step

The caller must keep this ownership adapter as the sole note authority for its
physical keys. These tests do not assert synchronization with arbitrary direct
Engine note, partial-key, manual-panic, replacement or reprepare operations.
Control-only same-thread edits are explicitly tested. Native VST3/DAW/device
behavior, byte-level MIDI decoding, concurrent publication, physical fidelity,
allocation instrumentation and callback deadline qualification remain separate
work. Test helpers allocate outside the wrapper; this suite is not an allocation
audit or timing benchmark.

The integrator should include this test and note in the wave-05 checkpoint, run
the complete combined-source gate and observe hosted qualification. Later
sample-rate and partial-key changes require their own integrated checks. No
production files, shared documentation, CMake, index state, commits or pushes
were changed by this assignment.
