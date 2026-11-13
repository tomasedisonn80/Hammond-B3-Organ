# Assignment 10: independent native pedal-routing oracle

Owner: /root/w02_a10_pedal_oracle

Wave 2; new pedal session. Owned only
[`tests/test_pedal_reference.cpp`](../../../tests/test_pedal_reference.cpp)
and this note. No implementation, data, shared status, commit or remote branch
was modified by this worker.

## Independent acceptance design

The test parses both retained factory pedal CSV readings directly using its own
native parser, including empty cells. It compares all 200 positions from each
reading against the generated native table, including pedal/contact identities,
explicit disconnections and an independently enumerated column-to-bus table.
It never obtains expected source numbers from the JSON, compiler, native table,
or constructive source-number formula. Literal rows for pedals 1, 7, 8, 12, 13
and 25 retain explicit exception-boundary checks. Compiled provenance identities
are checked against the frozen map, comparison and CSV hashes.

The scalar oracle traverses buses first, then pedals and selected columns in
reverse order. This differs from the runtime's flattened forward branch scan.
All 200 branch weights in the exact fixture have distinct binary-rational
magnitudes with mixed signs. Each isolated contact is tested against positive
and negative basis frames for all 91 sources, a mixed rational frame, and its
open-contact state. Thus the checks also exercise source IDs unused by the map.

Seven repeated-source pairs are tested as separate Brown and Red contributions:
first branch alone, both, second alone, and neither. The five disconnected
positions are toggled while all other contacts remain closed; their audible
output stays unchanged while retained contact counts change. Full occupancy
covers rational and unit weights, every positive source basis and both constant
polarities. The unit fixture independently confirms bus totals 45, 50, 50, 50
with all 200 contact positions retained.

For ordinary floating-point frames, the acceptance bound is fixed in source
before execution: `2 * gamma_100 * 50`, where
`gamma_100 = 100 * epsilon / (1 - 100 * epsilon)`. At most 50 products and 50
additions contribute to each bus, and each product has magnitude at most one.
Using binary64 epsilon rather than its half and allowing two differently
ordered sums gives a conservative **2.2204460492503624e-12** absolute bound.
The test does not require `long double` to be wider than `double`. It checks
96 deterministic contact masks, including full occupancy, with 32 independently
formed non-dyadic source frames each.

Three deliberate, structurally valid counterexamples calibrate the oracle:
a changed source number, a dropped repeated-source branch, and a changed branch
polarity must disagree with its documentary/weight expectation. Production
source files are not modified for these checks.

## Actual execution and source identity

Observed repository HEAD: `6a38805ea072627f383d9eb988d735dc259db472`.
The new kernel was an explicitly coordinated frozen working-tree addition.
Its header/source hashes remained unchanged before and after this build:

| Input | SHA-256 |
| --- | --- |
| `include/hammond/PedalRouting.h` | `e77c52f1c541ef301fff4c8b0fb9a9449f93be632630326f2d7640694384bea8` |
| `src/PedalRouting.cpp` | `8d05dedb9015863dfd88668e5ea27d6be42ea1fcdb600cf34787e446e14d22af` |
| New independent test | `a077fd174b5e2d262a53ae973bec9b374d3dad5e313a6533be39c62e0b8073ab` |
| Each retained pedal CSV | `b8177479a5af16f4e6b8759313d90148a1213657c83f8a6e6533422bfa104ca1` |

Executed with CMake 3.31.6, GCC 14.2.0 and Python 3.12.14, using the task-local
CMake executable and an isolated `build-a10` directory:

```sh
cmake -S . -B build-a10 -DCMAKE_BUILD_TYPE=Release
cmake --build build-a10 --target test_pedal_reference -j 2
ctest --test-dir build-a10 -R '^test_pedal_reference$' --output-on-failure -V
```

Strict warnings-as-errors core and test compilation passed. CTest reported
**1/1 passed, zero failures, 0.06 seconds**. The actual test reported:

| Executed observation | Result |
| --- | ---: |
| CSV/native cell comparisons | 400 |
| Independently isolated contacts | 200 |
| Exact binary-rational frame comparisons | 37,026 |
| Ordinary floating-point frame comparisons | 3,072 |
| Repeated-source pairs | 7 |
| Disconnected positions | 5 |
| Detected deliberate oracle counterexamples | 3 |
| Peak ordinary arithmetic difference | 2.6645352591003757e-15 |

`git diff --check` passed. No actionable routing defect was found in this scope.
This is an independently indexed software oracle over the retained documentary
readings; it does not reperform the historical reviewers' factory-image readings
or establish specimen continuity, electrical mixture, voicing, physical contact
timing or hardware fidelity. Source-history/allocation gates and root's complete
coherent regression/hosted publication are separate results. Proceed under the
[runtime contract](../../PEDAL_RUNTIME_CONTRACT.md) and subsequent
[integration contract](../../PEDAL_INTEGRATION_CONTRACT.md).
