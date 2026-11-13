# Assignment 07: typed pedal routing kernel

Owner: /root/w02_a07_pedal_kernel

Wave 2. Implemented the first native portion of
[the prepared pedal gate](../../M3_NEXT_GATE.md), following the fresh atlas
reviews 01-03 and the standing repository instructions. The observed starting
revision was `d307bafb4b678bda572258fb4170365cf4617867`, the integrator's
wave-1 documentation checkpoint. No prior worker is counted as this assignment.

## Implemented boundary

Added `include/hammond/PedalRouting.h`, `src/PedalRouting.cpp` and
`tests/test_pedal_routing.cpp`. The public API was frozen with assignments 08
(compiler/CMake) and 09 (contracts) before implementation.

- `PedalId` is distinct from MIDI notes and tone IDs; checked conversions preserve
  their destination on invalid values. Its supported domain is 1-25.
- A canonical 200-record definition retains each pedal/contact position, its
  Brown/Red/Orange/Yellow bus, and an explicit `optional<ToneId>` connection.
  An engaged source zero rejects; a disconnected branch is `nullopt`.
- `PedalBusKernel::prepare` validates exact shape/order, bus membership, all
  engaged source IDs and all 200 supplied weights, then owns a complete copy.
  Failed preparation preserves previous state; successful preparation opens
  every contact. No implicit reference weights or physical mixture is supplied.
- Contact edits preflight the entire batch, accept at most 200 entries and
  preserve supplied ordering. Repeated positions use the final edit. All null
  branches retain independent contact state.
- Rendering checks all 91 source values before computing four bus sums in a
  local destination. Weights and sources are finite in [-1,1], giving at most
  50 unit-bounded terms per bus. Invalid sources preserve destination and state.
  Rendering owns no source bank, clock, envelope, heap, parser, lock or logger.
- The compiled table and immutable provenance views expose the generated input
  identities. Generic structural preparation does not itself attest that a
  caller-authored table is the factory map; assignment 08 owns exact data admission.

Model identity is `linear-pedal-bus-reference-v1`. These dimensionless four-bus
excitations are a linear engineering reference, not volts, a pedal reactor model,
a calibrated voice or a controller octave convention.

## Actual verification

Used GCC 14.2.0, CMake 3.31.6 and Python 3.12.14 in the isolated sibling
`build-a07` directory. The core and its consumer were built against the same
frozen new header/source and assignment 08's generated table.

```sh
cmake -S Hammond-B3-Organ -B build-a07 -DCMAKE_BUILD_TYPE=Release
cmake --build build-a07 --target hammond_core -j 2
cmake --build build-a07 --target test_pedal_routing -j 2
ctest --test-dir build-a07 -R '^test_pedal_routing$' --output-on-failure
```

The strict warning-as-error core and native test builds passed. The focused
CTest result was **1/1 passed, zero failures, 0.01 seconds**. Six test groups
cover checked identity conversion, fixed documentary boundary rows and retained
hashes, unprepared/error precedence, atomic contact and prepare rejection,
independent duplicate/null branches, owned input lifetime and the four bus bounds.
Every one of 200 weight positions and 91 source positions is challenged with
NaN, both infinities and the adjacent binary64 values outside either bound.
The generic all-connected test reaches exactly 50 on each bus; the actual map
with unit sources/weights yields 45,50,50,50 while retaining 200 closed states.

`git diff --check` passed. Observed file SHA-256 identities:

| File | SHA-256 |
| --- | --- |
| `include/hammond/PedalRouting.h` | `e77c52f1c541ef301fff4c8b0fb9a9449f93be632630326f2d7640694384bea8` |
| `src/PedalRouting.cpp` | `8d05dedb9015863dfd88668e5ea27d6be42ea1fcdb600cf34787e446e14d22af` |
| `tests/test_pedal_routing.cpp` | `72129a7e19c6afadb6348f4e1ebaf904dc16ded262ad3bf19fe7789ac296ecc3` |

## Remaining gate and handoff

This worker did not run the complete regression matrix, a fresh independent
200-cell CSV/native comparison, allocation instrumentation, source-history
integration, hosted CI or physical measurements. Assignments 10-12 and the
integrator own the kernel's remaining independent acceptance and publication.
Playable mixture, retained pedal controls, Engine events, ownership and offline
evidence remain subsequent checkpoints. Only the four assigned files were
written; no shared status file, data source, commit or remote branch was changed.
