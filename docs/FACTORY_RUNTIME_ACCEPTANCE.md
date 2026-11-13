# Factory manual routing: runtime acceptance

**Observed result, 2026-11-13:** the new
[runtime test](../tests/test_factory_runtime.cpp) and existing
[frozen-reference suite](../tests/test_factory_reference.py) passed in an isolated
Linux GCC 14.2 Release build. The runtime test compares actual `Engine::process`
samples for **all 61 × 9 assignments on both manuals: 1,098 one-hot cases**.
The expected tone IDs come from the independently transcribed factory CSV.

This closes a software gate between the retained documentary reference and the
current ideal dry-engine routing/mix. It establishes neither measured instrument
sound nor pedal audio. The complete factory source identity, applicability,
transcription procedure and limitations remain in [FACTORY_REFERENCE.md](FACTORY_REFERENCE.md).

## Oracle and independence boundary

| Input | What the test uses it for | What it does not establish |
| --- | --- | --- |
| [Review A manual CSV](../data/references/review-a-manual.csv) | Every expected playing-key/drawbar tone ID | Source frequency, amplitude, phase or physical contacts |
| [Review B manual CSV](../data/references/review-b-manual.csv) | Independent retained reading; all cells must equal A | Independence by hash equality alone; review procedures establish that history |
| Unchanged compiled nominal profile | Source parameters, drawbar gains and fixed output gain | A calibrated pickup or console response |
| Separately prepared `TonewheelBank` | A synchronized vector of all 91 nominal source samples per frame | An independent implementation of source physics |
| Actual `Engine::process` output | Routing, branch addition, both manuals and Cancel/reselection behavior | Native audio-device, plugin-host, circuit or acoustic qualification |

The test reads both CSVs with an exact header, consecutive row identities, nine
integer IDs per row, the 13–91 source domain, and no trailing rows. The existing
Python suite separately pins their frozen hashes and compares every CSV cell
with authoring and compiled data. Run the two suites together for the retained
reference-to-runtime gate.

Expected routing never reads `RuntimeProfile::manual_map`, calls a production
mapper, or implements the atlas foldback formula. The sole production-map access
in this new test deliberately corrupts a local profile copy for a negative probe.
Factory keys and columns remain one-based; MIDI and zero-based source storage
are converted only at their respective API boundaries.

The source oracle and engine receive the same unchanged source parameters and
seed `0x0123456789abcdef`. The oracle bank is prepared separately and advances
without receiving any key or control events. Expected audio directly sums each
CSV-selected branch sample multiplied by its nominal drawbar gain, then applies
the nominal output gain. Duplicate branches remain separate summands. It does
not reproduce the engine's cached per-source coefficient calculation.

This intentionally reuses the production source bank: an error common to both
source-bank instances could pass this routing test. Independent source waveform,
phase, seed and numerical-support checks belong to
[test_tonewheel.cpp](../tests/test_tonewheel.cpp) and
[test_numerics.cpp](../tests/test_numerics.cpp), with the declared contract in
[ENGINE_API.md](ENGINE_API.md) and [NUMERICAL_BOUNDS.md](NUMERICAL_BOUNDS.md).
Those suites were not rerun for this narrow assignment.

## Exact case and frame budget

Every fresh engine first renders and checks 17 silent frames. One-hot and
coherent cases then render 128 compared frames, with the note and registration
applied at the first frame. This gives the source field a nonzero elapsed time
before the note. The reference bank advances through the same silence.

| Scope | Rate | Cases/stages | Compared output frames |
| --- | ---: | ---: | ---: |
| Every factory cell, upper manual | 48,000 Hz | 549 | 70,272 |
| Every factory cell, lower manual | 48,000 Hz | 549 | 70,272 |
| Both sides of eight routing transitions, both manuals | 44,100 Hz | 32 | 4,096 |
| Same selected transitions, both manuals | 96,000 Hz | 32 | 4,096 |
| Low duplicate drawbars, low overlapping keys and high duplicate drawbars, each manual | 48,000 Hz | 6 | 768 |
| Continuous two-manual addition/Cancel/reselection sequence | 48,000 Hz | 8 | 1,024 |
| **Accepted nominal audio** | | **1,176** | **150,528** |
| Deliberate in-memory wrong route and muted source | 48,000 Hz | 2 | 256, required to disagree |

There are **1,171 engine preparations**, each with 17 checked silent frames:
**19,907 silent frames**. Including accepted audio and the two rejected probes,
the test processes **170,691 engine frames**. The source oracle prepares one
1,041-frame timeline at 48 kHz and one 145-frame timeline at each other rate:
1,331 reference-bank frames total. This is a bounded routing gate, not a timing
benchmark or a long-duration source-accuracy test.

Routing data are independent of sample rate. The full 1,098-case matrix therefore
runs once at 48 kHz; the other rates target transitions where an index or
rate-dependent routing regression would be especially visible. Every one-hot
reference window must contain a sample with magnitude above `0.001` in nominal
normalized output units, so an all-zero expected window cannot pass unnoticed.

### Source and transition boundaries

All **79 source IDs 13–91** occur in the CSV and are exercised by the exhaustive
one-hot matrix. No CSV manual assignment names source IDs 1–12. These statements
refer to source identities, not hertz or physical terminals.

The additional rate checks use these literal CSV cell coordinates. The displayed
source values are readings of those cells, not a generated expectation:

| Factory keys | Drawbar column | CSV tone IDs, before → after | Boundary |
| --- | --- | --- | --- |
| 12 → 13 | d1 | 24 → 13 | End of low fold |
| 43 → 44 | d9 | 91 → 80 | First high fold |
| 48 → 49 | d8 | 91 → 80 | First high fold |
| 51 → 52 | d7 | 91 → 80 | First high fold |
| 55 → 56 | d6 | 91 → 80 | First high fold |
| 55 → 56 | d9 | 91 → 80 | Second high fold |
| 60 → 61 | d5 | 91 → 80 | First high fold |
| 60 → 61 | d8 | 91 → 80 | Second high fold |

The six coherent cases check, separately on each manual:

- Key 1, d1 and d3 at position 8: two contributions from CSV tone 13.
- Keys 1 and 13, d1 at position 8: two held keys contributing CSV tone 13.
- Key 61, all nine drawbars at position 8: tone IDs
  `61,80,73,85,80,85,89,80,85`, including three contributions each from 80 and 85.

The two-manual sequence holds key 61 on both manuals, with upper drawbars all at
8 and lower positions `1,8,4,7,2,6,3,5,8`. Its eight successive 128-frame stages
are upper alone, both, lower alone after upper Cancel, both after upper B
reselection, upper alone after lower Cancel, both cancelled, lower reselected,
and both reselected. After the second stage both physical keys stay held.
The reference timeline continues through the fully cancelled interval. Audio,
held-key state, route enablement after both keys are established, retained
drawbar positions and the final frame clock are checked.

## Numerical criterion and observed sensitivity

Each nominal sample must agree within
`peak_bound × (2 × epsilon(float) + 32 × epsilon(double))`, where `peak_bound`
is the sum of the active branches' nominal peak amplitudes after drawbar and
output gains. This permits binary32 output rounding and small binary64
summation-order differences. It requires no extra precision from `long double`.
Both values must be finite. An empty active mix has zero tolerance and must
produce exact silence.

The observed maximum absolute nominal sample error was
**`1.41557759958e-08`** normalized output units. Two in-memory profile copies
demonstrate that the same comparator rejects plausible failures:

| Probe | Local mutation | Disagreeing frames | Maximum absolute error |
| --- | --- | ---: | ---: |
| Wrong route | Upper key 1/d1 changed from its CSV tone 13 to the CSV key 1/d2 tone 20 | 128/128 | `0.0497971664381` |
| Muted source | Source 85 amplitude set to zero; lower key 61/d9 still expects the unchanged nominal source | 128/128 | `0.0299972152215` |

Both probes must exceed 1,000 times their normal sample tolerance. They use the
unmodified oracle timeline and never write a profile, CSV or production source
file. They establish sensitivity to these two injected errors, not exhaustive
fault detection.

## Retained identities and reproduction

Observed input/output identities remain:

| Artifact | SHA-256 |
| --- | --- |
| Review A manual CSV, and independently Review B manual CSV | `23ade40234db10d0bf99cd5acf9ee0ff29e4656e847e61409ebe8717f7cb9dc6` |
| Nominal authoring JSON, raw bytes | `d17a266ed97cbbd3a2925ebebafafbd6c0e3f84763635732e0a9351d0eab2bff` |
| Canonical authoring identity, also checked by the C++ test | `49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83` |
| Generated `nominal.b3p` | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |

From the repository root, with native CMake and CTest on `PATH`:

```sh
cmake -S . -B ../factory-runtime-release -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build ../factory-runtime-release --config Release --target test_factory_runtime -j 2
ctest --test-dir ../factory-runtime-release -C Release \
  -R '^(test_factory_runtime|python_test_factory_reference)$' --output-on-failure -V
```

The existing CMake `test_*.cpp` discovery registers the new target automatically;
this assignment changes no CMake rules. The observed run used GNU 14.2.0 with
`-O3 -DNDEBUG`, C++20, and the repository's strict warning flags including
`-Wconversion -Wsign-conversion -Wshadow -Werror`. Checks remain active in
Release. The runtime suite passed in 0.19 seconds; the Python suite passed all
20 methods. **Both selected CTest suites passed.** These elapsed times describe
this one run and are not performance thresholds.

No Debug, sanitizer, macOS or Windows execution was performed for this assignment.
Cross-platform qualification requires the actual integration/CI results for the
committed test. No pedal runtime exists; the existing pedal CSV/data comparison
does not constitute pedal audio testing. Gearing, calibration, contacts, pickup
loading, percussion, scanner, AO-28, Leslie and measured fidelity remain outside
this gate.
