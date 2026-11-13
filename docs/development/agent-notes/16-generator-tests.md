# Agent 16 — independent generator tests

- Assignment: permanent `tests/test_tonewheel.cpp` and this evidence note only.
- Read standing documents, `ENGINE_API.md`, source/profile/type contracts, note13,
  `ATLAS_REVIEW.md` and relevant generator findings retained in notes01/02.
  No new PDF-page review, instrument capture or hardware calibration was done.
- Scope: `ideal-shared-sine-v1` with `nominal-unmeasured-v1`; normalized samples,
  frequency in Hz, phase in turns. These are software-model tests, not physical
  gearing, shaft coupling, pickup voltage, factory mapping or fidelity evidence.

## Permanent coverage

- Exactly 91 numeric IDs, zero-based conversion and every invalid uint8 ID;
  independent tone 1/13/46/58/70/73/82/91 frequency anchors at 44.1/48/96 kHz.
- Current-phase emission and next-sample diagnostics use a long-double oracle
  `wrap(initial + elapsed_frames * frequency / sample_rate)`, not a replicated
  accumulator. Phase tolerance is `8 * double_epsilon * (frames + 1)` turns;
  sample tolerance is `2*pi*phase_tolerance + 2e-15` normalized units.
- All 91 outputs are finite and amplitude-bounded throughout a full second at
  each rate. NaN-prefilled output detects omitted source writes. Analytical
  checks include the first 16 samples, every 251st sample and final sample/phase.
- Tone 46 has exactly 440 rising zero crossings over one second (N+1 samples).
  Interpolated frequency must be within 0.0001 Hz of 440 Hz, a numerical criterion.
- Three seed known-answer sets include seed 0, a nonzero seed and UINT64_MAX;
  exact hexadecimal offsets check early/late draws, including tones 46/90/91.
  Same-seed replay and explicit reprepare reproduce samples; another seed differs.
- Explicit base phases cover quadrants and the value immediately below 1 turn.
  Varied supplied frequencies/amplitudes include muted and near-Nyquist sources.
  An entirely muted bank advances all 91 phases for 4097 real frame calls.
- Four loop groupings compare 10003 actual `process_frame` calls and final phases
  exactly at each sample rate. Empty groups make no call; no block API is invented.
- Unprepared processing, preserved invalid-query destinations, unsupported rates,
  and 12 failed prepares are checked. Rejections preserve future samples against
  a control, including late-source increment underflow after 90 valid candidates.
- Caller profile mutation before the first sample and after advancement cannot
  alter bank samples/phases. `CHECK`/`CHECK_NEAR` remain enabled in Release.
- CMake's existing `test_*.cpp` discovery installs target/test `test_tonewheel`.
  Engine folding/coherent routing is agent 17's separate assignment.

## Executed evidence — 2026-11-13

- GCC 14.2.0 Debug and Release compiled successfully with repository strict
  conversion/sign-conversion/shadow warnings as errors; no implementation edits.
- CMake executable: `/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake`;
  CTest is its sibling `ctest`. Repo: `.../Hammond-B3-Organ`; builds:
  `/workspace/scratch/c871510c69b2/agent16-build/debug` and `.../release`.
- Configured each build with `cmake -S <repo> -B <build>`, the matching
  `-DCMAKE_BUILD_TYPE`, `-DBUILD_TESTING=ON -DHAMMOND_ENABLE_SANITIZERS=OFF`; then
  `cmake --build <build> --target test_tonewheel -j 2` and
  `ctest --test-dir <build> -R '^test_tonewheel$' --verbose --no-tests=error`.
- Both targeted CTest runs passed (Debug 1.46 s, Release 0.80 s).
  Max analytical errors: `1.76897394539e-11` sample units and
  `2.82768253257e-12` turns. Crossing estimates were 439.999999434,
  440.000000188 and 439.999999997 Hz at 44.1/48/96 kHz respectively.
- The concurrent Release make invocation emitted `jobserver mkfifo: /tmp/GMfifo5:
  File exists`; build and test both exited 0. No generator defect was exposed.
- Sanitizers, allocator/deadline instrumentation, platform/host tests and physical
  calibration were not run by this assignment. No commits, pushes or other edits.
