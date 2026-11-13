# Assignment 18 — independent pedal Engine acceptance

Owner: /root/w03_a18_pedal_integration

Wave: 3 of 10. Assignment: 18 of 60. Status: complete.

## Scope and outcome

Added `tests/test_pedal_integration.cpp`, automatically discovered by the existing
CMake test glob. The actual Engine passes the independent integration checks
against both retained 200-cell documentary CSV maps. No production file was
changed and no runtime defect was found. This result concerns the explicitly
unmeasured nominal model in [the integration contract](../../PEDAL_INTEGRATION_CONTRACT.md).
It does not establish measured pedal voicing, physical fidelity, CLI support or
native-host completion.

## Independent oracle and coverage

The test reads both `review-a-pedal.csv` and `review-b-pedal.csv`, checks their
complete equality and five disconnected positions, and uses the CSV cells to
select source IDs. Literal column pairs define the four buses. A separate
TonewheelBank receives the same profile, seed and rate, advances exactly once
per sample, and supplies the expected shared source frame. Reversed summation
and the equations `(4B+2R+O+Y)/8`, `(B+4R+2O+Y)/8`, followed by explicit position
gain `p/8`, form the expected voice. Neither the generated routing table, the
constructive routing formula, the production matrix/gain table nor the voice
rendering function supplies expected values.

- All 25 isolated pedals and all 200 closed/open contact states, including the
  five unconnected positions, at 44.1, 48 and 96 kHz; all-pedal polyphony.
- Upper/lower manual and pedal source-13 collisions with coherent source frames;
  all 91 phase histories compared bitwise to the separately clocked source bank.
- Lower Cancel, retained-bank reselection and manual panic preserve held pedals;
  pedal panic preserves the held manual contribution. Pedal events leave upper
  percussion diagnostics and readiness exactly unchanged.
- Held muted pedals become audible through zero-frame control edits, without
  retriggering. Tied events retain order; zero-frame operations preserve time,
  source/contact/readiness histories and the previous rendered diagnostic.
- Supported and rejected rate changes, including same-rate no-op. Historical
  frame/rate/position tags survive edits and rate changes until the next sample;
  disconnected positive rendering updates them with actual rendered values.
- v3 restoration and v1/v2 migration preserve held pedals, manual contact travel,
  readiness, phases and clock. Historical versions explicitly migrate pedal
  controls to zero despite a nonzero parsing destination.
- Single-sample, regular and irregular partitions produce bitwise-identical
  output and final public state, with a fixed disconnected output interval.
- Ten late-invalid batches preserve the output sentinel, controls, contacts,
  phases, clock, readiness and diagnostic record, then produce bitwise-identical
  future audio to an untouched Engine copy.

The fixed double allowance is `2e-12` absolute. Audio adds
`2 * float_epsilon * abs(expected)` for float rounding. These thresholds were
declared before execution and were not adjusted after observing results.

## Executed verification

Built a coherent source copy at `/workspace/scratch/f364bc93d920/a18-source`
from published checkpoint `6768ef2388819ebbaaf7cc23bdf72265dc72c561`, overlaid
only with the frozen Engine/Types, PedalVoice and ControlState/IO files and this
test. Assignment 16 explicitly confirmed the runtime freeze before copying.
The concurrently edited parameter bridge was not copied into this build.

GCC 14.2.0, CMake 3.31.6, Python 3.12.14; Release with the project's warnings as
errors. The following commands completed successfully:

```text
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake -S /workspace/scratch/f364bc93d920/a18-source -B /workspace/scratch/f364bc93d920/build-a18 -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake --build /workspace/scratch/f364bc93d920/build-a18 --target test_pedal_integration -j 4
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/ctest --test-dir /workspace/scratch/f364bc93d920/build-a18 -R '^test_pedal_integration$' -V --no-tests=error
```

CTest: **1/1 passed**, 0.08 seconds. Observed counts: **2,203** independent
oracle frames, **32,600** explicit contact checks, **200,837** bitwise phase
checks, **17,676** bitwise partition audio comparisons and **10** rejected
transaction/future-audio cases. Maximum absolute bus, voice and float-audio
errors were respectively `7.64666108210576567e-15`,
`3.40005801291454191e-15` and `1.08423013451923456e-07`.

Frozen runtime SHA-256 identifiers:

| File | SHA-256 |
| --- | --- |
| `include/hammond/Types.h` | `c533cc0b59838e22aff1dd081e30482df76c747407ea76d4b1788e0536a3ef7b` |
| `include/hammond/Engine.h` | `b2aea1dae1e54654cacb8576295b27d47673c87a9a01e17fd3eba7a843fa188c` |
| `src/Engine.cpp` | `e082d07323c506f58c726c76a8459bbbec9b01fcb7b20ca6d6323c065fa6664c` |
| `include/hammond/PedalVoice.h` | `694961946eac838c689547fc403c84e49a429f3337816ea9ad3a751bf305ddaf` |
| `src/PedalVoice.cpp` | `88fb5afa936784be351b2940ee6f81216975112f860b007d40f3b6a3d9f7c6ba` |
| `include/hammond/ControlState.h` | `2fb1b7b7fc39363f7e53eb81e2edf3ddb88944b4aa20969b92a90f5c584b2edb` |
| `src/ControlState.cpp` | `d297545788fa62b0167fc0a9c07081b1f8af79bd1252ceb66d0d1326dd214e58` |
| `include/hammond/ControlStateIO.h` | `2b42270c1d32bb57f3240ed48db5a45b182aaa5cec0c501d65d9f698b7016127` |
| `src/ControlStateIO.cpp` | `a1043d29d2321cccad4e994afbf62e16d93ce6cd15ce5c7593556daff1b0a8cf` |
| `tests/test_pedal_integration.cpp` | `176606fc4438b297a3cac3beab54bc79bcf369dbc6772779339ae6de9af77853` |

## Handoff

The integrator should include this test in the combined phase gate after all
wave-3 scopes are frozen, then publish the reviewed checkpoint. This focused
result is not a claim that the full suite or remote CI ran against that eventual
combined tree. CLI event support, benchmark instrumentation and host integration
remain separate follow-on gates. Assignment 18 made no commit or push.
