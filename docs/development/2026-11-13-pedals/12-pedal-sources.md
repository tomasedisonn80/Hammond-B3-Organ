# Assignment 12: shared sources and pedal lifecycle harness

Owner: /root/w02_a12_pedal_sources

Wave 2. Owned files: [the native harness](../../../tests/test_pedal_sources.cpp)
and this note only. Reviewed the standing instructions, current session/baseline,
[runtime contract](../../PEDAL_RUNTIME_CONTRACT.md),
[next M3 gate](../../M3_NEXT_GATE.md), actual source/kernel APIs and implementation,
and atlas p. 144's linear shared-phase acceptance requirement. The inspected
repository HEAD was `6a38805ea072627f383d9eb988d735dc259db472`; the new kernel and
compiler were coordinated frozen worktree additions from assignments 07/08.

## Independent fixture and scope

The test supplies one `TonewheelBank::process_frame` result to both a simple
manual reference and `PedalBusKernel`. Ten explicitly written pedal contact
fixtures select cells from the retained factory CSV reading, including pedal 1's
two separate source-13 branches, pedal 13's shared source 13, pedal 8's null
position, and upper-range sources 65/68. Their source identities are checked
against the compiled routes. The other 190 weights are explicitly zero; all 200
contacts are nevertheless exercised. This is a declared signed, binary-rational
engineering stimulus, not a physical mixture or drawbar law. No production
pedal-routing formula generates the expected source choices.

Three independently declared manual branches use sources 13, 25 and 68, checked
against the nominal profile's fundamental routes. A second oracle collects all
intended manual/pedal contributions by source and performs one long-double dot
product. It uses independently maintained intended contact states, not the
kernel's route or contact outputs as its mathematical oracle.

Before execution, the test fixes a coherence bound of
`512 * binary64 epsilon = 1.1368683772161603e-13`: fewer than 64 nontrivial
multiply/add roundings per evaluation, at most 13 nonzero terms, and an absolute
term sum below seven. This remains conservative when `long double` has only
binary64 precision. It is not a measured acoustic tolerance.

## Exercised behavior and observed results

A 2,053-frame schedule is run from each supported initial rate using one-frame,
64-frame and irregular block partitions. Half-open block handling preserves
three same-frame edits in their supplied order. A fourth run omits pedal output
evaluation during two intervals, including contact changes while disconnected,
then compares all reconnected samples. A source-only control bank advances once
per modeled frame alongside the actual shared bank.

Every modeled frame compares all 91 source samples and phases bit-for-bit.
Contact edits consume zero source time. A silent interval has exactly zero
manual/pedal contribution while the source field continues. All nine supported
rate pairs, including same-rate requests, retain phases and pedal state. Rejected
192 kHz and NaN changes preserve subsequent samples; repeated kernel evaluation
of the same frame changes neither sources nor contact history.

| Actual observation | Result |
| --- | ---: |
| Source frames compared with the source-only control | 30,414 |
| Individual phase values compared | 3,188,913 |
| Coherent combined-frame comparisons | 24,141 |
| Nonzero combined frames above absolute 0.01 | 22,534 |
| Deliberately unused pedal-output frames | 495 |
| Zero-time contact-edit batches | 228 |
| Supported rate-change operations | 57 |
| Partition/output-connection runs | 12 |
| Maximum observed coherence error | `3.81639164714897561e-16` |
| Fixed acceptance bound | `1.1368683772161603e-13` |

All connected partition results, source histories and final contact states
matched exactly where bitwise equality was required. No implementation defect
was observed in this scope.

## Actual build and verification

Used CMake 3.31.6, GCC 14.2.0 and Python 3.12.14, with a fresh isolated build of
the core and this consumer from the same frozen header/source interface:

```sh
cmake -S . -B build-a12 -DCMAKE_BUILD_TYPE=Release
cmake --build build-a12 --target test_pedal_sources -j 2
ctest --test-dir build-a12 -R '^test_pedal_sources$' --output-on-failure
```

The strict-warning Release build passed. Focused CTest: **1/1 passed, zero
failures**, 0.12 seconds for the test and 0.13 seconds total. The observations
above were read from that run's retained `LastTest.log`, not a separate invented
or inherited run. Direct UTF-8/LF, final-newline, trailing-whitespace, note-owner
and local-link checks also passed.

Observed SHA-256 identities:

| File | SHA-256 |
| --- | --- |
| `tests/test_pedal_sources.cpp` | `6df49bca992536d64bb23f53a85543ff1bdb92b0673e7b652734248095e0a361` |
| `include/hammond/PedalRouting.h` | `e77c52f1c541ef301fff4c8b0fb9a9449f93be632630326f2d7640694384bea8` |
| `src/PedalRouting.cpp` | `8d05dedb9015863dfd88668e5ea27d6be42ea1fcdb600cf34787e446e14d22af` |
| `include/hammond/TonewheelBank.h` | `694acaece901e18b4e089264218d8f217cfe3d2f8ea2a9adfb5ff6773b2f756b` |
| `src/TonewheelBank.cpp` | `ebc26e2e61cc88d5525e390abf3897ebeae38e652c13ea3ef02818b2b3849e0b` |

## Handoff and limits

This verifies the **frame-level kernel and source-harness contract**. It does not
verify a later Engine pedal integration, actual host callback scheduling, pedal
voicing, controller mapping, physical contact motion, reactor loading or measured
instrument fidelity. Assignment 10 owns exhaustive independent CSV/native route
acceptance; assignment 11 owns allocation instrumentation. Root owns integrated
regression, hosted qualification, shared status and publication. No implementation,
data, historical ledger or shared status file was changed, and no commit or push
was performed by this worker.
