# A26 — paired-session musical continuity

Actual worker: `/root/w05_a26_musical_continuity`, assignment 26, wave 5.
Owned source: `apps/standalone/tests/test_standalone_workspace_continuity.cpp`.
The integrator owns CMake, shared status and publication. This worker changed no
production source and did not stage, commit or push.

## Executed result

The new SDK-free test passes **63 scores at 44.1/48/96 kHz**: 36 registration
scores covering all twelve selectors on both manuals, three actual 47-parameter
edit sweeps, and 24 isolated percussion scores covering the eight enabled
harmonic/volume/decay combinations. All four retained drawbar banks, both pedal
mixtures, expression, fixed modes, adjustable A/B and Cancel participate.

Each score prepares two real Sessions with identical profiles, seeds, controls,
commands and callback partitions. Only one UiModel changes workspace, Flat,
dimensions and focus between callbacks; the control remains Play/Dimensional at
1280×900. Keyboard, pointer and Space owners overlap independent external owners.
Original releases follow changed target/octave/focus, and external owners continue
until their own releases. Six owners share Upper C in the isolated scores.

Observed totals are **719,289 frames**, **1,438,578 bit-exact paired stereo
samples**, **1,872 callbacks**, **1,419 matched commands**, **1,662 presentation
transitions with zero commands**, **141 real parameter edits**, and **14,190
canonical state-byte comparisons**. There are 81 zero-frame flushes; positive
callbacks vary from one to 1,024 frames. All six workspace/presentation pairs
and seven contract sizes are visited. Save/parse roundtrips, desired/applied
controls, dirty/pending state, clocks, peaks, publications and held targets agree.

An independent **Engine input oracle** receives explicitly planned physical-note
events, without Session's dispatcher or ownership adapters. Its samples match
both Sessions exactly. A separate accumulator checks all 91 source phases
170,352 times; closed-form decay/recovery checks readiness 1,872 times. The
271,224 isolated percussion samples also match an analytic source/envelope
reference, including continued tails and renewed attacks after silent recovery.
The smallest isolated score energy is **0.4465459572**; the smallest score peak
is **0.0093686711**, preventing silent comparisons from passing as audible music.
Thirty-six upper-Cancel blocks match the same Engine history with Upper notes
removed while other parts stay audible. Cancelled-only passages are silent.

## Source and verification

The observed HEAD is `5d81199a9822874b55f3b0a124715cbd6eadf0e5`, with the concurrent
interface overlay. [The machine-readable report](reports/a26-musical-continuity.json)
records exact source/profile/binary hashes, every score, tolerances and limits.
UiModel, Session and all recorded production inputs stayed stable through the
gate; all **114 protected files** still match the A12 boundary inventory.

- Test source SHA-256: `e231c62715369592028f4403a665816faab34b629378e0274929a31b0c0d0a05`.
- Executable SHA-256: `4d81cd3c14559dad30b118574840f5659595f19406ef2460c4baea96c989ed27`.
- Aggregate observed stereo PCM FNV-1a64: `9b6fbb0939b79179` (diagnostic identity,
  not a portable golden-file assertion).

Reused `build-a13-sdkfree`, GCC 14.2.0 and CMake/CTest 4.4.4. Configure/build
succeeded; [CTest](reports/a26-ctest.txt) passed **1/1 in 4.58 seconds**.
Commands, from the checkout root:

```sh
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/cmake -S . -B /workspace/scratch/601951e27dc3/build-a13-sdkfree -DCMAKE_BUILD_TYPE=Release -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_ENABLE_MIDI=OFF
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/cmake --build /workspace/scratch/601951e27dc3/build-a13-sdkfree --target test_standalone_workspace_continuity --parallel 3
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/ctest --test-dir /workspace/scratch/601951e27dc3/build-a13-sdkfree --output-on-failure --no-tests=error -R '^test_standalone_workspace_continuity$'
```

The [first run](reports/a26-first-run.txt) exposed one fixture expectation error:
variant 11 eventually leaves only held Lower Cancel, which must be silent. Its
explicit energy expectation was corrected; production and exact PCM/state
assertions were unchanged. No production defect was found.

## Limits and handoff

Session intentionally exposes no live phase/readiness API. Its history evidence
is exact continuation PCM plus state/owner probes; direct phase/readiness checks
belong to the Engine input oracle. These are nominal ideal-contact dry-engine
fixtures, not physical measurements. This Linux Release result does not qualify
native devices, SDL pointer capture, hosts, concurrent execution, sanitizers,
other platforms, accessibility or fidelity. The next step is inclusion of this
target in the integrator's coherent-source gates; no further model change is
needed for this assignment.
