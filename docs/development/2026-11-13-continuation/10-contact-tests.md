# Assignment 10: independent contact-bank tests

## Scope and ownership

- Actual agent: `/root/w02_a10_contact_tests`; continuation wave 02.
- Reviewed `AGENTS.md`, current status/next steps, the M3 console contract,
  `ContactBank.h/.cpp`, the existing test support and atlas pp. 37-42 and 115-120.
- Added only `tests/test_contact_bank.cpp` and this note. No core implementation,
  shared handoff, build configuration, PDF or remote reference was changed.
- This is verification of the named nominal software model, not contact physics,
  recorded key timing, source-waveform switching or an instrument-fidelity gate.

## Independent expectations

The seven test families cover:

1. **Checked/unprepared access:** operations reject invalid manuals, notes and
   contact indices; every checked query preserves its supplied destination.
2. **Ideal compatibility:** every manual/key switches all nine contacts immediately;
   duplicates are idempotent, advancement does nothing, interior position targets
   reject, and upper-manual panic leaves lower-manual contacts intact.
3. **All 1,098 contact identities:** a one-hot partial-hold fixture visits every
   manual/key/contact combination. Its selected contact has a lower threshold
   than its neighbors, deliberately independent of physical index order. Each
   fixture checks all keys, individual contact queries and aggregate detector
   queries against the expected single closed connection, then verifies release.
4. **Analytic timing at 44.1/48/96 kHz:** independently derive first make and break
   sample indices from threshold distance, duration and sample rate. These nominal
   edge positions are explicitly non-integral, avoiding ambiguous rounding at an
   exact lattice boundary. Compare every contact's observed first transition;
   compare positions to long-double elapsed-time equations within `3e-16`.
   Check the connection-change return flag against observed before/after masks.
5. **Partial holds and reversals:** approaching position 0.5 from below closes four
   nominal contacts; approaching from above retains five through hysteresis.
   Check a stationary hold, interrupted press/release/repress against independent
   piecewise travel distances, repeated targets without rebasing, and repeated
   same-time target edits without advancing position or contacts.
6. **Exact endpoints and panic:** equal make/break thresholds close/open as specified;
   contact thresholds at 1/0 change at full endpoints. Non-integral durations stop
   on the expected frame at each rate. Minimum/maximum supported durations reach
   their endpoints; panic clears only one manual while the other keeps the same
   subsequent trajectory as an untouched comparison.
7. **Rejection and ownership:** 45 malformed profile cases cover both modes,
   last-key/last-contact values, invalid enum, nonfinite values, duration bounds,
   threshold bounds and equality. Six unsupported rates, invalid targets and invalid
   destinations also reject. Failure checks compare subsequent trajectories, not
   just immediate diagnostics. Caller-profile ownership uses independently prepared
   authoring objects, corrupts only one caller's data, and checks 700 subsequent
   frames against the separate reference. Successful preparation resets all keys.

The timing oracle does not copy `advance_frame()`'s segment calculation or infer
expected states from another instance. Comparison instances are used specifically
for idempotency, failure preservation and retained-state contracts. Contact-source
foldback, generator phase and host-block partition behavior belong to later engine
integration tests because the contact bank has no source or block API.

## Executed verification

Toolchain: GCC 14.2.0; CMake 4.4.4; C++20; repository warning set including
`-Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror`.
Build directory was outside the repository at `../agent10-release`.

```sh
cmake -S Hammond-B3-Organ -B agent10-release -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build agent10-release --target test_contact_bank -j 2
ctest --test-dir agent10-release -R '^test_contact_bank$' --output-on-failure
```

The executed CMake/CTest binaries were under
`/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/`, with absolute source
and build paths. Compilation succeeded with the full warning policy. The registered
suite passed **1/1**, reporting **0.04 seconds** in this run. Release checks remain
active through the project's `CHECK`/`CHECK_NEAR` helpers.

No contact implementation defect was found in this scope. Before the first build,
the new test code was corrected to sequence its advance/read explicitly and to
use separate authoring memory for the ownership oracle. These were test-authoring
corrections, not suppressed product failures. `git diff --check` was clean.

## Remaining boundaries

No sanitizer, allocation instrumentation, deadline, native platform or host result
is claimed by this assignment. The integrator owns combined and hosted validation.
The model has binary sample-grid edges; measured bounce, fractional edge timing,
band-limited switching and high-rate audio convergence remain unimplemented gates.
The atlas's proposed normalized audio-error criterion is not exercised by a state
unit test and is not claimed to pass. Per-key measurement and calibrated hardware
contact traces remain absent.
