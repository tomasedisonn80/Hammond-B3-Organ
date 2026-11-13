# Agent 31 — core robustness review

## Assignment and scope

- Wave 06; baseline `b9c1cac`; reviewed 2026-11-13.
- Own `docs/CORE_REVIEW.md`, this note and targeted `test_core_robustness.cpp`.
- Read standing instructions, current status/plan/contracts, atlas chapter 063
  pp. 385-390, core headers/implementations and existing C++ coverage.
- Audited event/span boundaries, numeric/index bounds, value lifetimes,
  failed prepare/restore and profile stream exceptions. No plugin/hardware claim.

## Finding and coordinated fix

- Profile loading caught only `std::ios_base::failure`; an exception-enabled
  stream can rethrow its buffer's original `std::runtime_error` instead.
- Reported concrete cause and obtained integrator coordination before changing
  `src/Profile.cpp`. Agent 32 owns decimal conversion earlier in that file.
- Added a `std::exception` handler gated by `input.bad()`; confirmed read failure
  now returns the existing error without changing destination. Unrelated
  exceptions propagate. Existing clean-EOF behavior remains.
- New regression injects original exceptions at byte 0, midpoint and immediately
  after a complete valid profile, under three exception masks: nine cases.
- It verifies whole-profile preservation, locale/mask preservation, error update
  and healthy-stream recovery, including EOF exceptions.

## Actual verification

- Toolchain: GNU 14.2.0, CMake/CTest from `../build-tools/cmake/data/bin/`.
- Configured `../agent31-release` with Release and `BUILD_TESTING=ON`.
- Built new target and ran its CTest before the fix: failed with
  `Core robustness failure: injected original stream-buffer failure`.
- After fix, built targets `test_core_robustness test_profile test_engine
  test_controls test_control_io test_tonewheel` with `-j 2`.
- Ran CTest expression
  `^test_(core_robustness|profile|engine|controls|control_io|tonewheel)$`:
  **6/6 passed** after build completion.
- An earlier CTest call started while the last target was compiling; tonewheel
  was Not Run. Waited for build exit 0, then the six-suite run above passed.
- Configured `../agent31-sanitize` only. Integrator requested no further optional
  local sanitizer work; no sanitizer or leak result claimed for this change.
- Combined Agent 32 decimal edits require subsequent integrated verification.

## Other conclusions and open boundary

- Existing tests already cover atomic invalid event rejection, final clock
  boundary, profile mutation/expiration and restore continuation. No duplicate
  state suite or speculative ownership refactor added.
- Fixed-size value members make implicit copies/moves independent. Validated
  indices and counts precede narrowing; maximum mix is only 1098 bounded branches.
- Valid live spans and stopped/same-thread access remain caller obligations.
- A bounded scratch numerical probe confirmed an open extreme-frequency limit:
  tone 1 at `1e-300 Hz`, `48000 Hz` rate, seed 0 prepares, but its phase remains
  `0.88331080821364261` after 1024 frames; the positive increment rounds away.
- Reported this to the integrator for a supported lower-bound or accumulator
  decision. No impact established for the supplied nominal 12-TET profile;
  no test added that would canonize stalled phase as expected behavior.
- Full reasoning, test boundary and future numerical decision are retained in
  `docs/CORE_REVIEW.md`. No commit/push or shared status edits by this agent.
