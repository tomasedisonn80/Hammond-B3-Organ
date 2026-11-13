# Assignment 25 — actual Engine pedal trace

Owner: /root/w05_a25_pedal_trace

Session: 2026-11-13 pedal development, wave 5, assignment 25 of 60.

## Scope and retained source basis

Implemented the bounded offline `hammond_pedal_trace` executable, its independent
Python acceptance suite, the [CSV/CLI contract](../../PEDAL_TRACE.md), and only
the corresponding CMake target/dependency/test-environment hook. Installation
packaging remains assigned separately. Root owns shared status, assignment
accounting, combined regression and publication; this worker made no commits or
pushes.

Read the standing instructions, current plan/status/next steps, preceding handoff,
latest log, atlas review and source atlas pp. 139–144. The relevant distinction is
one shared generator, four pedal buses, separate contact ownership and explicit
physical unknowns. [PEDAL_ENGINE.md](../../PEDAL_ENGINE.md) and
[PEDAL_VOICE.md](../../PEDAL_VOICE.md) provide the implemented, nominal contract.
The fixed matrix, unit weights, ideal contact policy and position/8 gain remain
unmeasured engineering choices.

Root approved the three scenarios and schema before acceptance execution.
`unmute` observes held muted pedals and later registration changes; `overlap`
combines pedals 1/25 with manual MIDI 48's source-25 branch; `routing` holds all
25 pedals through lower Cancel/reselection and independent division panics.
These scenarios last 120 ms at each supported rate. The source-25 manual route
is an explicit admission anchor; a supplied profile with another route rejects
before output creation.

Each row uses the actual `Engine::last_pedal_frame()` record after one sample,
paired with that actual mono float. The tool copies current controls, all 25
held targets, all 200 contacts and source-25 phase before rendering. The record's
frame/rate/position tags and Engine's next clock are checked. Source phase is
never evaluated independently or advanced for diagnostics. The 37 metadata
comments and 27 columns preserve actual compiled model/map/matrix/gain identities,
units, pre-render phase versus post-render clock, and declared profile provenance.

## Coherent source and commands actually run

Created `/workspace/scratch/f364bc93d920/a25-source` from `git archive` of published
wave-3 commit `e493b9fed9e3ed8a294fb5d95af447132776cb3a`, then overlaid only the
owned CMake file, new executable and new acceptance test. Concurrent wave-4
source/header/tool changes were excluded. The live and tested copies of those
three files were byte-compared after execution.

Toolchain: Linux, GCC 14.2.0, CMake 3.31.6, Python 3.12.14. The target inherits
project warnings treated as errors. The actual configure/build commands were:

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake \
  -S /workspace/scratch/f364bc93d920/a25-source \
  -B /workspace/scratch/f364bc93d920/build-a25 -DCMAKE_BUILD_TYPE=Release
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake \
  --build /workspace/scratch/f364bc93d920/build-a25 \
  --target hammond_pedal_trace -j 4
```

The initial native smoke ran the `routing` scenario at 96 kHz, seed zero. It
produced exactly 11,520 rows and 4,859,923 bytes. Reconfigured the same coherent
source after adding the test, then ran the focused CTest. Its first run failed
one test-helper assertion: a malformed-profile fixture expected a MIDI prefix
in a compiled manual-map row, but those rows contain only nine source IDs.
Corrected the fixture to mutate the third source cell of the thirteenth row.
The numerical/metadata/exporter cases had passed; no production repair was needed.
The final suite also includes the agreed symlink path-admission checks.

Final command:

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/f364bc93d920/build-a25 \
  -R '^python_test_pedal_trace$' --output-on-failure \
  --output-junit /workspace/scratch/f364bc93d920/a25-ctest.xml
```

**Observed result: 1/1 selected Release CTest passed, zero failures, disabled or
skipped tests, 6.09 seconds.** The Python suite executed **13 methods** in
5.852 seconds and **65 actual native CLI invocations**. This was the selected
trace gate, not the complete repository test suite.

## Independent expectations and observed results

The test reads both retained pedal CSV transcriptions, checks their agreement,
and reads both manual CSVs for the source-25 collision anchor. It computes the
raw/canonical map and two reference hashes from retained source bytes. Expected
bus contributions come from counted CSV branches; no generated routing table,
production mixture matrix or production voice function supplies the expected
results.

Frozen hexadecimal initial phases for source IDs 1–68 were derived using a
separate arbitrary-precision integer evaluation of the documented SplitMix64
convention. IDs 1/46/91 were cross-checked against the retained source-bank
known-answer table. The committed acceptance test contains no PRNG recurrence.
It uses closed-form elapsed-time phase, independently arranged integer-numerator
mixture equations, explicit position/8 gain, actual profile gains and a separate
binary32 rounding operation.

| Executed evidence | Count/result |
| --- | ---: |
| Independent numerical rows | 79,236 |
| Contact-bit positions compared exactly | 15,847,200 |
| Normal scenarios/rates | All 3 scenarios × all 3 rates |
| Additional numerical inputs | Maximum uint64 seed; modified compiled source-25 peak/output gain |
| Actual symbolic-link cases | 3; creation privilege was available |
| Largest tested complete trace | 5,113,994 bytes, below 8,388,608 |
| Concurrent same-destination publication | Exactly one winner; identical complete bytes; no leftover temporary directories |

The routing trace exposes all 200 closed positions, including all five null
connections. Exact checks retain all targets through lower Cancel/reselection
and manual panic, keep Upper held after pedal panic, and verify the silent tail.
The unmute trace has nonzero pre-control mixtures while output is exactly muted.
Malformed CLI/domain/profile/route inputs create no output; existing destinations,
profile aliases and dangling links retain their contents/targets.

| Quantity | Criterion fixed before execution | Maximum observed absolute error |
| --- | ---: | ---: |
| Source-25 phase, turns | `4e-12` | `1.389166559562227e-13` |
| Four buses | `2e-9` | `1.4811263326919288e-11` |
| Two mixtures | `2e-9` | `8.240519377977762e-12` |
| Separate pedal contribution | `4e-9` | `5.431211036466266e-12` |
| Actual mono float | `4e-7` | `2.9103830456733704e-11` |

These are numerical software criteria. They are not physical/perceptual response
tolerances. Tags, discrete controls, held targets, contacts and silent output
use exact comparisons. All rates' maximum-row scenarios fit the advertised byte
bound. The test records an unavailable Windows symlink-creation privilege
explicitly if encountered; it does not relabel unexecuted symlink cases as passes.

## Frozen identities and handoff

| File/artifact | SHA-256 |
| --- | --- |
| `tools/pedal_trace.cpp` | `9fd14f19b75b6d761f2659a5ec406fcb41c74e7ce335357820a61c6b4ee24bfa` |
| `tests/test_pedal_trace.py` | `cc5459fa0a7ef29d39f6e2749206e4632dfbe9395d14c04619122f72662058ff` |
| Tested `CMakeLists.txt` | `9b916789268c0e9fca099be68c638e5c4b008423b84c14aa96419a33020c9a4f` |
| Local native trace executable | `e231a10e15b94cf790fada38e0c4807420c82ce1b114f934c36f7c50a504745b` |
| Compiled nominal profile | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| Complete final `LastTest.log` | `842e34e32817dcd23aabffa3f4e54fa7d737c184da0e3c7b05aa0d4420dfb241` |

The complete local test output is retained under
`/workspace/scratch/f364bc93d920/build-a25/Testing/Temporary/LastTest.log`; the
CTest XML truncates long successful stdout and therefore is not the source of
the full invocation/error summary. Source/profile/reference/PDF inputs are
unchanged. Owned files pass UTF-8/LF/whitespace and local-link checks.

Next: root integrates this frozen scope into the complete wave-5 snapshot and
publishes only after its combined gate. The later install scope must add this
executable and exercise prefix relocation. Enabled-path allocation, native ABI/
DAW/device qualification, physical pedal loading and measured timbre retain
separate acceptance gates. The trace itself provides no callback deadline,
acquired measurement, plotter or native UI transport.
