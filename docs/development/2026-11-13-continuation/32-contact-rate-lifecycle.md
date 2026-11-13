# Assignment 32 — contact sample-rate lifecycle

Agent: `/root/w06_a32_contact_rate_lifecycle`

Wave: 06, assignment 32 of this continuation's 60 new agents

Date: 2026-11-13 UTC

Starting revision: `72b5062dd4d02acc42c30faf291465c7633b87d9`.
Concurrent assignments' files were preserved. This module was qualified from a
frozen archive of that revision with only the three source/test overlays listed
below, so its core and consumers used identical header definitions.

## Implemented contract

Added `ContactBank::reconfigure_sample_rate(double) -> Status` and the copied
`sample_rate()` diagnostic in samples per second. The diagnostic is zero before
a successful `prepare()`. Successful preparation installs the rate with its
fresh contact bank; rejected preparation retains the prior rate and state.

Rate reconfiguration is a stopped or same-processing-thread lifecycle operation.
It advances no time and preserves all 122 current positions, 122 targets and
1,098 independently hysteretic connection states exactly. It preserves the
selected model and every owned per-key threshold and duration. Its ordering is:

1. An unprepared bank returns `NotPrepared`, including for invalid rate inputs.
2. Any rate other than exactly 44100, 48000 or 96000 returns `InvalidSpec`.
3. The installed rate returns `Ok` as an exact no-op, including private segment
   origins and elapsed-frame counters.
4. A changed rate prepares every press/release step in a local candidate bank
   using the installed per-key durations. Each owned duration must satisfy the
   existing finite `[0.0001, 1]` second bounds; every resulting step must be finite
   and positive. A failed candidate would return `InvalidProfile`.
5. Each moving candidate segment takes its current position as its new origin
   and zero elapsed frames. Its target and direction remain intact. Stationary
   segment history is unchanged. The candidate bank and rate are installed only
   after all validation succeeds.

For a press duration `T`, the step is `1 / (sample_rate * T)` normalized travel
per sample; release uses its own duration. Remaining time scales with the
remaining normalized distance. A partial target therefore retains the same
full-travel speed in seconds rather than restarting a full-duration journey.
Migration never resolves thresholds or substitutes a nominal profile, resets a
key, changes a target, or resets hysteresis. Ideal mode keeps its existing
immediate endpoint semantics.

The method uses a fixed-size local candidate array; it introduces no dynamic
allocation, I/O, logging or concurrent publication protocol. The per-frame
`advance_frame()` implementation is unchanged. These properties follow from
the implementation scope; this assignment did not instrument allocations or
qualify an audio callback deadline.

## Source basis and model boundary

The supplied [atlas](../../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf), pp.
115–120 and 394, was read for this assignment. Pages 115–120 distinguish nine
contact histories, common key motion, separate make/break behavior and partial
holds. Page 394 motivates preparing rate-dependent coefficients before
activation while keeping transient dynamics separate from portable musical
controls. The PDF's SHA-256 remains
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.

This is lifecycle behavior for the existing `ideal-contacts-v1` and
`nominal-linear-travel-v1` software models described in
[CONSOLE_DYNAMICS.md](../../CONSOLE_DYNAMICS.md). Normalized positions, travel
durations and thresholds remain explicit engineering inputs. The migration
does not add measured geometry, bounce, velocity inference, sub-sample contact
events, antialiasing or physical B-3 qualification.

## Independent tests and results

The new `test_contact_rate` uses an elapsed-time oracle. From a preserved
boundary position, its expected monotone segment is current position plus or
minus `(elapsed_samples / new_rate) / owned_duration`, clamped to the unchanged
target. This is evaluated in `long double`; it does not repeat the implementation's
per-frame state update or segment counter. The absolute position tolerance is
`4e-15` normalized travel. Positions and targets stay within `[0, 1]`, and each
reference requires only a few bounded arithmetic operations. The allowance is
about 18 binary64 machine epsilons and accommodates platforms where `long double`
has binary64 precision as well as same-rate cases that retain their old origin.
State preservation and same-rate/failure future comparisons require exact equality.

Threshold timing fixtures independently place every threshold one quarter of a
new-rate sample beyond a known integer coordinate. The expected change occurs at
the following sample, leaving a substantial margin from floating-point boundary
ambiguity. Every contact is checked before, at and after that coordinate for
press and release across all nine rate pairs. Unsorted thresholds ensure a
contact cannot inherit another contact's state by rank.

| Check | Observed scope/result |
| --- | --- |
| Supported transitions | All nine old/new rate pairs in Ideal and LinearTravel |
| Mixed motion | Both manuals and all 122 keys, with partial presses, incomplete releases, held partial positions, full holds and per-key durations |
| Immediate state | Every tracked migration preserves position, target and all nine contact bits exactly |
| Owned parameters | Mutation of the caller's entire profile, including a NaN duration, cannot affect the installed bank's migration |
| Hysteresis | Equal upper/lower positions retain different contact histories across repeated rate changes without elapsed time |
| Reversals | Incomplete release reverses toward a partial target and follows the new rate's independently computed distance |
| Same-rate behavior | 12,288 calls during repeated partial-target changes preserve exact future state against an untouched copy |
| Timing | 18,630 contact/sample checks around new-rate threshold crossings |
| Duration boundaries | Both accepted duration endpoints, `0.0001` and `1` second, with exact target clamping at partial positions and full travel |
| Rejections | 115 checked migrations: unprepared precedence and unsupported, neighboring, nonfinite, subnormal and extreme rates |
| Failure atomicity | Retained rate, public state and future trajectory equal an untouched copy after every rejected migration and rejected preparation |
| Accepted tracked scenarios | 71, including same-rate entries in the pair matrix and repeated held-state boundaries |
| Position comparisons | 456,298; maximum absolute error `1.59459034518305564632e-16` normalized travel |
| Contact comparisons | 4,116,402, in addition to threshold-coordinate checks |
| Exact future comparisons | 14,028 paired frames, including later target changes |

Strict GNU C++ 14.2.0 Release compilation passed with the repository's warning
flags treated as errors. The new lifecycle suite and unchanged historical
`test_contact_bank` passed **2/2 CTest suites in 0.08 seconds**, with no skipped
tests. No build, assertion or test failures occurred in this scoped qualification.
The direct executable invocation emitted the counts and numerical maximum above.

All public ways to install a profile already reject invalid owned durations, and
the accepted duration/rate ranges yield finite positive steps. Consequently the
defensive `InvalidProfile` branch inside migration is not reachable through a
valid public preparation. The tests do not corrupt private storage to manufacture
that branch; they instead check late-key bad-profile rejection, caller ownership
and complete rejected-rate future behavior.

## Exact qualification procedure

The immutable source snapshot was created with this Python command from the
repository root. `git archive` supplied the base; only this assignment's owned
header, implementation and test were overlaid. Concurrent unpublished source and
CMake changes were excluded.

```sh
python - <<'PY'
from pathlib import Path
import hashlib, io, shutil, subprocess, tarfile
repo=Path('/workspace/scratch/60e8291da354/Hammond-B3-Organ')
frozen=repo.parent/'a32-frozen-src'
frozen.mkdir()
base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
archive=subprocess.check_output(['git','archive',base],cwd=repo)
with tarfile.open(fileobj=io.BytesIO(archive)) as data:
    data.extractall(frozen,filter='data')
print('base_commit='+base)
for name in ['include/hammond/ContactBank.h','src/ContactBank.cpp','tests/test_contact_rate.cpp']:
    shutil.copy2(repo/name,frozen/name)
    print(hashlib.sha256((frozen/name).read_bytes()).hexdigest()+'  '+name)
print('frozen_source='+str(frozen))
PY
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  -S /workspace/scratch/60e8291da354/a32-frozen-src \
  -B /workspace/scratch/60e8291da354/a32-frozen-build \
  -DCMAKE_BUILD_TYPE=Release
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  --build /workspace/scratch/60e8291da354/a32-frozen-build \
  --parallel 2 --target test_contact_rate test_contact_bank
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/60e8291da354/a32-frozen-build \
  -R '^(test_contact_rate|test_contact_bank)$' --output-on-failure
/workspace/scratch/60e8291da354/a32-frozen-build/test_contact_rate
git diff --check -- include/hammond/ContactBank.h src/ContactBank.cpp
```

These commands describe the observed run; a future run should choose a fresh
snapshot/build path, pin its intended base revision and record its own hashes.
Permanent tests use the repository's CMake-provided paths and have no dependency
on these session directories.

## Retained identities

SHA-256 values from the qualified snapshot and build:

| File | SHA-256 |
| --- | --- |
| `include/hammond/ContactBank.h` | `a083dcd65d989cc5be78a393fad74f40cbb530e33f89492d523e406f477be99d` |
| `src/ContactBank.cpp` | `91747d963d6cec74b3be12549abd8e816f4c176ce172fba52f9cdbc593c6e9e1` |
| `tests/test_contact_rate.cpp` | `2f705093ace99f22fd90f888fb380a148cc0466fddd8ab59e701ffb1d78626cb` |
| Scoped `test_contact_rate` executable | `26b8271c7487c4a9acd1609df8e5aa68ff5de68cb5a5c5fea122581cafe43c2c` |
| Scoped `test_contact_bank` executable | `fb935567e8a9799c5cae9c56f80e6e7fb5bfdaf2370cfe44d53606ecb722e056` |
| Generated `nominal.b3p` | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |

## Files and integration handoff

Changed only [ContactBank.h](../../../include/hammond/ContactBank.h),
[ContactBank.cpp](../../../src/ContactBank.cpp),
[test_contact_rate.cpp](../../../tests/test_contact_rate.cpp) and this note.
No Engine, TonewheelBank, Percussion, CMake, shared-status or existing test edits
were made. No staging, commits, pushes or subagents were used in this assignment;
the integrating agent owns the authorized publication and shared handoff updates.

Assignment 34 can compose this stable API with source and percussion candidates
inside `Engine::reconfigure_sample_rate`. The Engine must keep its old live state
until every module accepts the candidate rate, preserve musical controls and its
render clock, and reject the whole migration atomically when any source module
cannot support the new rate. Its first post-change contact snapshot must remain
the exact pre-change snapshot. Later motion must use the newly installed rate.

The next acceptance gate is a coherent combined-source build and Engine lifecycle
tests, followed by the integrator's full publication suite and exact revision CI.
This module gate does not establish native device/host behavior, concurrent calls,
callback deadlines, cross-platform execution or measured physical fidelity.
