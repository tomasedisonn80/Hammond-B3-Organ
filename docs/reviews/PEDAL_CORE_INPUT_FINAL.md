# Final pedal core and combined-input review

## Result and scope

Assignment 49 found **no actionable production defect** in the inspected pedal
routing, nominal voice, Engine integration, note ownership, combined-input
transaction or control-migration paths. A focused execution of **20 existing
Release CTest suites passed in 2.98 seconds**, with zero failures, disabled tests
or skips. No production code or tests were changed merely to increase coverage.
Two stale current-contract passages were reported to the integrator for the
separately assigned handoff review; their historical wording is identified below.

This is a finite code and software-behavior review. It does not establish physical
pedal voicing, circuit loading, measured contact behavior, callback deadlines or
DAW/device qualification. Native host execution and artifact results belong to
their [separate native gate](../VST3_ABI_ACCEPTANCE.md),
[concurrency review](../VST3_CONCURRENCY.md) and
[platform record](PEDAL_NATIVE_PORTABILITY.md).

## Identified source and execution

The review used root's coherent `checkpoint-w07/source` archive, Git tree
`7c3e1e2e93932dfa59f20e2be8ee4ab7f46b8f73`, and its corresponding
`checkpoint-w07/build-default` Release binaries. Before execution, all **495
archived files** were independently hashed as Git blobs and matched against
`git ls-tree` for that tree. The source files and all 20 selected executable
hashes were checked again after execution and were unchanged.

Published wave-7 commit
[`7fb9b6121b729f46a9e18d80e8620eb21dc0847b`](https://github.com/tomasedisonn80/Hammond-B3-Organ/commit/7fb9b6121b729f46a9e18d80e8620eb21dc0847b)
has tree `19239e05f6c5219b50d3f398ba9a6eb3acc2a1ac`. Its later repairs did not
change the audited `src/`, `include/`, `data/` or C++ test files; neither did the
live wave-8 work at this review. This assignment did not rebuild the binaries,
rerun the complete default/native matrix, or treat the full published tree as
identical to the earlier archive. The evidence is a new focused execution of
identified unchanged compiled inputs, not an inherited test result.

The actual generated build files identify GCC 14.2.0, CMake 3.31.6, C++20,
`-O3 -DNDEBUG`, all project warning flags with `-Werror`, the frozen source path
and the explicit compiled profile. Test assertions use `TestSupport.h`'s active
`CHECK` functions, rather than C `assert` disabled by `NDEBUG`. The profile is
4,545 bytes with SHA-256
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.
The [assignment note](../development/2026-11-13-pedals/49-core-input-audit.md)
retains exact commands, source/binary identities and local log hashes.

## Risk review

### One source clock and preserved documentary branches

[PedalRouting.cpp](../../src/PedalRouting.cpp) owns neither an oscillator nor a
clock. Preparation admits exactly 200 canonical rows, validates every weight
and connected source before assigning anything, copies all data by value, and
opens every contact. A disconnected position still has retained contact state.
The frame renderer validates all 91 source values, accumulates each connected
branch independently in canonical order, and publishes its four bus outputs
only after successful calculation. Repeated source numbers remain separate
branches; a null route never becomes source zero.

[Engine.cpp](../../src/Engine.cpp) calls the shared source bank once per rendered
sample and feeds that exact frame to manual/percussion and pedal paths. It does
so even with disconnected output or muted controls. Pedal actuation only edits
eight closures in the existing kernel. Pedal and manual held-state arrays,
manual Cancel and the different panic commands are distinct. Pedal activity
cannot retrigger the upper percussion state or reseed sources.

The independent [pedal reference test](../../tests/test_pedal_reference.cpp)
reads both retained CSV transcriptions, uses literal bus-column membership,
reverses summation order, and selects source numbers from CSV rather than the
production compiler/table or its constructive formula. Literal boundary rows
protect pedals 7/8 and 12/13. Its isolated signed source-basis cases distinguish
misrouting from an audio-scale coincidence. The executed gate confirmed all
400 CSV cells, all 200 isolated contacts, seven repeated-source pairs and five
disconnections. The separate source harness checked 3,188,913 phase values,
228 zero-time edit batches and 57 rate changes; these counters describe that
suite's actual workload, not distinct independent physical measurements.

### Bounds and nominal arithmetic

The kernel has at most 50 bounded branch terms per bus. The fixed nominal
mixture rows in [PedalVoice.h](../../include/hammond/PedalVoice.h) are convex
combinations of those four buses; each mixture stays within the declared
absolute limit 50, and two unit-gain positions give a conservative output bound
100. [PedalVoice.cpp](../../src/PedalVoice.cpp) validates buses even when muted,
validates both control positions before indexing, and only then assigns the
result. Both muted controls produce canonical positive zero while preserving
mixture diagnostics.

Engine adds the pedal contribution only when it is nonzero. This preserves the
older dry accumulation order and signed-zero behavior when the new division is
inaudible. That compatibility mechanism is separate from the legacy waveform
replays retained in the [legacy identity review](PEDAL_LEGACY_FINAL.md).
The fixed mixture matrix and linear position gains remain named, dimensionless
engineering fixtures. They do not substitute for the reactor/resistor network,
source loading or complex low-wheel spectra described in atlas pages 141–144.

### Transaction admission and late failures

Engine's complete preflight precedes all mutation and output writes: prepared
state, configured frame bound, output size, event count, frame-clock overflow,
then all event offsets, order and payloads. Positive blocks are half-open;
zero-frame flushes admit only offset zero. The frame-clock subtraction avoids
unsigned overflow, and a rejected call consumes zero events. An accepted
zero-frame call changes musical targets without advancing sources, contact
travel, percussion readiness, the frame clock or the last actual pedal frame.

[PerformanceInput.cpp](../../src/PerformanceInput.cpp) first checks hard bounds,
raw count, global chronology and the allowed control alternatives. Both owner
ledgers are copied before translating any note. The combined emitted array is
bounded to 1,024, including ordinary controls and all final releases generated
by a channel panic. A no-op may use an empty remaining span; a required emission
cannot. Exactly one Engine call follows the full translation, and only its
success permits both nonthrowing ledger assignments. Thus a late malformed
control, output shortage, clock overflow, identity conflict or expanded-capacity
failure cannot install an early owner change.

The [independent mixed-input test](../../tests/test_performance_acceptance.cpp)
feeds a separately authored physical timeline to a second Engine; neither
production translator generates the expected events. It checks output tails,
all visible state and exact phase bits, then renders a future suffix after
rejection. Its capacity scenario retains 256 manual plus 256 pedal owners at
once, expands 880 raw records to exactly 1,024 physical events, and rejects a
1,025th required event without retiring the owners. The facade's separate raw
count boundary also rejects 1,025 no-op records. These cases exercise different
limits and are not interchangeable.

The facade deliberately checks some ownership failures before Engine control
payload admission. A later owner-capacity error can therefore take precedence
over an earlier malformed control value. This matches the documented contract;
no partial acceptance follows from that precedence. Direct physical Event
alternatives are rejected by the facade because they would bypass ownership.

### Release identity and retained routes

Both note adapters use `(origin, channel, note_id)` for identified ownership.
Duplicate positive On for the same physical target is idempotent, including at
capacity; conflicting target reuse rejects. Anonymous releases select the
oldest matching anonymous owner and never consume an identified owner. Stable
compaction preserves surviving insertion order. A scoped panic emits individual
final releases only as each physical count reaches zero, so another origin or
channel can retain the same key/pedal.

Manual owners additionally retain their original destination. Changing a bus
route affects only later owners; duplicates and releases keep the existing
owner's stored manual. The inspected and executed combined test explicitly
places anonymous owners of the same bus/channel/pitch on opposite manuals
across a remap, then retires them in FIFO order. Pedal ownership uses its own
one-based domain and cannot alias a manual MIDI pitch. Each physical count is
bounded by the 256-owner maximum, well within its `uint16_t` storage.

### State, rates and diagnostic history

[ControlStateIO.cpp](../../src/ControlStateIO.cpp) parses into a fresh candidate.
Versions 1 and 2 therefore acquire explicit muted pedal positions independently
of the previous destination; a malformed version-3 pedal record cannot fall
back to migration. Complete control validation precedes restore. Ordinary state
contains no held owners, source phases, moving-contact trajectories or clock.
Restoring controls marks Engine coefficients dirty without changing those
histories. The retained 16 KiB stream limit and strict end-token grammar remain.

Engine rate changes use local source/contact/percussion candidates and install
none until every module accepts. Same-rate changes are exact no-ops. Pedal
routing and the fixed voice have no rate-dependent state. Last-frame pedal
diagnostics retain the rate and controls of the sample actually rendered, even
through a zero-frame edit, restore or later rate transition; the next rendered
sample replaces them. The separate rate and pedal-integration suites exercise
both accepted and rejected transitions with audible future comparisons.

## Observed focused evidence

All 20 selected suites passed. Representative directly observed counters are:

| Executed gate | Observed evidence |
| --- | --- |
| Pedal reference | 400 CSV-cell comparisons, 200 isolated contacts, 37,026 exact and 3,072 ordinary frames; three oracle counterexamples |
| Pedal Engine integration | 2,203 independent oracle frames, 32,600 contact checks, 200,837 exact phase checks, 17,676 exact partition samples, ten late-invalid transactions |
| Manual / pedal owners | 2,127 / 74 accepted calls; 2,264 / 59 atomic rejection and future checks |
| Combined input | 3,819 accepted calls, 45 atomic rejection/future checks, 26,250 exact audio samples, 42 partition cases |
| Independent combined acceptance | 12,660 accepted calls, 41 rejections, 39 future probes, 68,102 exact audio samples, 1,162,434 exact phase comparisons, 24 partition runs |
| Pedal controls | 105 round trips, 162 legacy migrations, 133 rejected documents and 494 rejected snapshots, preserving destinations |
| Engine rate lifecycle | 36 rate-pair scenarios, 81 rejected transitions, 6,144 same-rate calls and 32,603 exact future-audio frames |
| Enabled allocation instrumentation | Twelve allocation/free calibration pairs detected; 180 measured API regions observed zero global C++ new/delete calls |

Exact comparisons and tolerance-based numerical oracles are different evidence.
For example, pedal integration's peak bus/voice/audio errors against its
independent numerical reference were approximately `7.65e-15`, `3.40e-15` and
`1.08e-7`; this is not a claim of zero error against every independent model.
Allocation observations apply to calling-thread global C++ new/delete only;
they exclude C heap calls, arbitrary locks/syscalls, all thread interleavings,
SDK/device execution and real-time deadline guarantees.

## Handoff findings and next action

At the reviewed snapshot, two current contract pages had stale cross-references:

- [PEDAL_NOTE_OWNERSHIP.md](../PEDAL_NOTE_OWNERSHIP.md), sections “Input domains,”
  “Combining ownership with Engine” and “Executed acceptance and remaining gates,”
  describe native mapping and unified input as future or under development.
- [PERFORMANCE_INPUT.md](../PERFORMANCE_INPUT.md), final “Executed acceptance and
  remaining work” paragraph, describes independent acceptance, allocation and
  native conversion as subsequent gates without linking their existing results.

Root acknowledged these exact locators and assigned the current-contract wording
to assignment 55. Historical result records should remain dated. The production
API already implements [combined input](../PERFORMANCE_INPUT.md), and native
mapping has its [processor contract](../VST3_PROCESSOR.md); this review did not
edit those files outside its ownership.

The next core change should follow the new
[M3/scanner gate](../M3_REMAINING_AND_SCANNER_GATE.md), preserving existing source,
control and state identities and the old dry arithmetic order. Repeat only the
affected gates when a concrete code/model change occurs, then qualify the final
integrated source and published platforms through root's release process. No
further speculative core repair is requested by this review.
