# Continuation assignment 11: independent shared-percussion tests

Agent: `/root/w02_a11_percussion_tests`; wave 02, assignment 11 of the new
continuation session. Reviewed working-tree modules after baseline `5dcd942`.
This assignment changes only `tests/test_percussion.cpp` and this evidence note.
The integrator owns status, next steps, development log, integration and publication.

## Scope and oracle

Read the standing instructions, current status/next steps, new console contract,
percussion interface/implementation and atlas pp. 127-138. The source distinguishes
shared readiness history, selected harmonic audio, route eligibility and eventual
physical-circuit qualification. These tests exercise the **standalone nominal
readiness module**, not Engine routing, host note ownership or physical fidelity.

Constant detector segments are checked against direct elapsed-time solutions:
`q_end = q_start * exp(-duration/tau_decay)` and
`q_end = 1 - (1-q_start) * exp(-duration/tau_recovery)`.
The reference uses long-double elapsed time and does not reuse the implementation's
per-frame coefficients or multiply its recurrence. Recovery expectations continue
from the theoretical decay endpoint, so a decay defect cannot become an accepted
recovery starting value. A stable `expm1` form avoids subtraction loss in the oracle.

The numerical threshold is a declared project target: absolute readiness error
at most `1e-11` for these bounded scenarios. It is not a manufacturer tolerance,
measured envelope error or claim about arbitrary-duration accuracy. On platforms
where long double equals double, the direct closed-form calculation remains
structurally independent but does not provide extra precision.

## Permanent coverage

- Initial/current-sample gain uses `q[0] = 1` before the first advance. Defaults
  disable percussion and select Second/Normal/Slow; unprepared use is safe.
- One-second slow/fast decay and 0.1-second recovery at 44.1, 48 and 96 kHz;
  checkpoints include the first sample and non-round frame counts.
- Piecewise slow decay, fast decay, disabled recovery and resumed decay, with
  harmonic/volume changes preserving readiness and independent gain factors.
- Zero elapsed-time diagnostic/control queries preserve state exactly. Increasing
  positive release gaps recover monotonically from one common history. These
  module checks do not substitute for same-offset Engine event tests.
- Forty-one invalid profiles cover every tau/gain field, NaN/infinities, negative
  values and adjacent representable values outside the supported endpoints.
  Eight unsupported/nonfinite sample rates also reject atomically.
- All 762 invalid enum settings (values 2-255 across three enums) reject for both
  detector states. Connected detection while disabled rejects without mutation.
  Future mixed-mode evolution is compared to an untouched copy, detecting hidden
  coefficient/state damage as well as changes to exposed diagnostics.
- Supported minimum/maximum taus and gains remain bounded; zero gains are valid.
  The declared smallest-normal-double cutoff produces no retained nonzero
  subnormal readiness, reaches zero, and can recover on subsequent open samples.
- Mutating the caller's profile after prepare cannot alter gains or time constants.
  Copies have independent histories. Successful prepare is the explicit reset;
  ordinary settings/query operations do not reset readiness.

No Engine source selection, upper-B mask, contact detector aggregation, drawbar
independence, callback allocation, latency, host or hardware result is inferred
from this isolated module suite. Integration assignments own those gates.

## Executed verification

Toolchain: GCC 14.2.0, CMake 4.4.4, Python 3.12.14. The repository CMake strict
C++20 warning configuration, including `-Werror`, was applied. Commands used the
CMake/CTest binaries under
`/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/`:

```sh
cmake -S /workspace/scratch/60e8291da354/Hammond-B3-Organ \
  -B /workspace/scratch/60e8291da354/a11-percussion-release \
  -DCMAKE_BUILD_TYPE=Release
cmake --build /workspace/scratch/60e8291da354/a11-percussion-release \
  --target test_percussion -j 2
ctest --test-dir /workspace/scratch/60e8291da354/a11-percussion-release \
  -R '^test_percussion$' --output-on-failure
```

Configuration and build succeeded; **1/1 selected CTest suite passed** in the
isolated Release build. Its retained output reports **103 closed-form comparisons**,
**41 invalid profiles**, **762 invalid enum settings**, and maximum absolute q error
**`1.1582061807e-12`**, below the declared `1e-11` target. No implementation defect
was found and no core file was modified. No sanitizer or hosted platform run was
performed by this assignment. No commit or push was attempted.

`git diff --no-index --check /dev/null tests/test_percussion.cpp` emitted no
whitespace diagnostics (its status 1 denotes that the new file differs).

## Tested source identities

SHA-256 values at the successful test checkpoint:

| File | SHA-256 |
| --- | --- |
| `include/hammond/Percussion.h` | `725a530a578937b28bbe1fb8fb470852959b6c6b31fad7d5dbe288fc4e591039` |
| `src/Percussion.cpp` | `873b6e71ebf7e2535884bfe6d5d71a7a36fc101e536ed987f59b7cd87a446564` |
| `tests/test_percussion.cpp` | `801fa8b0ff14ed88bdee7380c1b2235feb83b0f295721bead78e6ff9c2de0c6a` |

Later API/algorithm changes require rerunning the affected suite. Exact Engine
integration, playback and physical-model comparison remain separate follow-up work.
