# Assignment 39 — independent partial-key acceptance

Agent: `/root/w07_a39_partial_key_tests`

Wave 07, assignment 39 of this continuation's 60 new agents. Date: 2026-11-13 UTC.

## Scope and source basis

Added only [test_partial_key.cpp](../../../tests/test_partial_key.cpp) and
[test_partial_key_render.py](../../../tests/test_partial_key_render.py), plus this
note. No production, existing test, build-system, shared-status or index changes
were made. No subagents, commits or pushes were used by this assignment.

Read the standing instructions, current status/next steps/plan, console contract
and complete atlas pages 115-120. The atlas calls for separate contact histories,
partial depression, preserved shared-source phase and block-independent replay.
The tested normalized targets, thresholds, travel times and percussion response
are the declared nominal model; these tests provide no hardware calibration,
fractional switching, bounce or antialiasing evidence.

Assignment 37 owns the Engine extension and assignment 38 owns offline grammar
and evidence validation. Their production files were frozen before qualification.
Expected states use explicit public contracts and independent formulas. The
C++ audio oracle reads the current public source phase and evaluates an isolated
sine route; it does not call `TonewheelBank`, copy its PRNG, or reconstruct the
Engine's coefficient cache. Python uses the producer only to generate real
fixtures. It never uses producer parsing or validation helpers as an oracle.

## Permanent acceptance

| Boundary | Covered behavior |
| --- | --- |
| Event identity | Static assertions retain event values 0-8 and append `KeyPosition = 9` |
| Both manuals, all three rates | Approaching target 0.5 from below closes four contacts; approaching from above retains five; the isolated fifth-contact audio agrees with that history |
| Shared phase | Different gestures with equal elapsed frames preserve all 91 phases; flushes, reversal and panic advance no source |
| Partial percussion | A 0.5 hold passes the second harmonic while contact 8 remains open and readiness stays exactly 1; positive NoteOn still commands full travel |
| Sample convention | The independently calculated ninth-contact make frame still has pre-decay readiness; the following 101 rendered frames match the closed-form decay |
| Motion commands | Same-target duplicates preserve exact continuation; same-offset reversal advances no time; ordinary release preserves currently closed contacts and follows the release slope; panic opens immediately |
| Atomic admission | Invalid target/manual/note payloads and ideal-mode interior targets preserve all public state, output sentinels and subsequent audio; ideal endpoints match existing note commands |
| Partitioning | One 17-event timeline with reversals, both manuals, stable ties, duplicate targets and panic gives exact audio/state at block sizes 1, 31, 257 and 1024 at every supported rate |
| Offline audio | Actual partial-harmonic renders at 44.1/48/96 kHz match onset timing and an independent 880 Hz two-basis fit; block sizes 1 and 127 produce identical WAV bytes |
| Files and preflight | Ten invalid CLI scores create no output or leftover temporary file; existing output bytes survive; three producer rejections neither launch a renderer nor create a bundle directory |
| Versioned evidence | Two actual schema-2 bundles retain their scores and existing 13-parameter/18-metric/26-argument structure; the independent verifier rejects a coherent metadata mutation that falsely declares ideal contacts |
| Historical evidence | The committed schema-1 demo still verifies; temporary copies with updated hashes/counts reject both endpoint and interior `key_position` commands at the event-grammar boundary |

The mutated bundles are negative parser fixtures, not claims that a historical
renderer produced new grammar or that modified metadata authenticates audio.

## Observed result

Strict GCC 14.2.0 Release compilation succeeded with the repository's warnings
treated as errors. Python was 3.12.14. **Both focused CTest suites passed: 2/2 in
0.41 seconds**, with no skipped tests. The Python suite passed all **7 methods**.
No compile failure, failing test or production defect was observed.

| Observation | Result |
| --- | --- |
| Complete exact public-state pairs | 234 |
| Bit-identical rendered float samples | 51,513 |
| Independent isolated current-phase samples | 768; maximum absolute error `9.29094e-10`, tolerance `5e-9` |
| Rejected Engine calls with preserved future output | 51 |
| Direct actual renderer invocations | 19 |
| Additional producer-created, independently verified schema-2 bundles | 2 |
| Independent PCM amplitude comparisons | 3 rates; maximum absolute amplitude error `7.02819526653e-7` |

The PCM fit uses the full two-by-two sine/cosine normal system. Its amplitude
bound comes from the inverse-system row norms and a per-sample allowance of half
a PCM16 step plus `1e-8` for float/trigonometric arithmetic. Every fitted residual
is below one PCM16 step. These are finite-window nominal software checks, not
universal numerical error bounds or physical tolerances.

## Coherent qualification identity

The qualification source was a clean archive of
`53bb6e1e37eedf84f566ffb8bd9037b50f123a20`, overlaid with exactly the six frozen
production files below and the two new tests. No later live headers or tools were
used. Every overlay was byte-compared with its qualified copy after the tests.

| Frozen file | SHA-256 |
| --- | --- |
| `include/hammond/Types.h` | `a8f86c3b0910a5e0921b1ff583b4c947573dfecb955bff2c8341613ffdf95fe0` |
| `include/hammond/Engine.h` | `efb8f0eb36dccbe5f0416186ef9478091be48e5634cfd6a8f0155b3dfd1c81c0` |
| `src/Engine.cpp` | `53c07390447796f4c57e96e58b9d6720df76094e14a0e6240b284f62e4310ccf` |
| `tools/render.cpp` | `6838b1e8b406935cc8f69bd78aedc57b91ae55280c62d73220813f6d01d601bb` |
| `tools/render_fixture.py` | `9e4a63808a7d754a038b503242dfa078c5cfaeaa1bc9ca9b80c3646d7c56fd36` |
| `tools/verify_render.py` | `332d7cbc694ab457ed607f4473f688ea6d86c8cf2765e706ec463fef18dc20db` |
| `tests/test_partial_key.cpp` | `31f45af4c124214400e030654eeee47ecb3d560b3e90549ceffa71891f1a4917` |
| `tests/test_partial_key_render.py` | `07e14113838a00c03019f7cbff2b7048233b37207c923eeb2aeb3c1f1477e8f1` |

Commands actually executed:

```sh
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  -S /workspace/scratch/60e8291da354/a39-qualified/source \
  -B /workspace/scratch/60e8291da354/a39-qualified/build -DCMAKE_BUILD_TYPE=Release
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  --build /workspace/scratch/60e8291da354/a39-qualified/build \
  --target test_partial_key hammond_render -j 3
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/60e8291da354/a39-qualified/build \
  --output-on-failure -R '^(test_partial_key|python_test_partial_key_render)$' -j 2
```

The qualified renderer SHA-256 was
`cc0f7a98cdc23694e18c8b53a1241704a876331677688950dea0e7cd6a498efd`;
the compiled nominal profile remained
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.
Scratch paths identify this observed run only. Permanent tests use CMake-provided
inputs and repository data, with no dependency on these session directories.

## Next gate and limits

The integrator must include these files in the coherent wave-07 staged source,
run the complete applicable gate, update shared status/next steps/log, publish
with the expected-head guard, and observe that revision's hosted results.
Existing CMake test discovery already registers both files. This focused run
does not establish cross-platform or sanitizer qualification, native host/device
operation, calibrated position input, allocation bounds or callback deadlines.
