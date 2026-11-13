# Agent 18 — permanent renderer regressions

## Assignment and inputs

Owned `tests/test_render.py` and this note only; no implementation changes,
commits, pushes or subagents. Read AGENTS, README, status/next steps/log/plan,
atlas review/errata, chapter 063 (PDF pp. 385-390), ENGINE_API, RENDER_FORMAT,
renderer/engine/source-bank code and agent 15's renderer evidence note.

## Retained coverage

- Twenty standard-library unittest cases launch the actual renderer from an
  unrelated temporary cwd, using paths containing spaces. CTest supplies
  `HAMMOND_RENDER_EXECUTABLE` and `HAMMOND_TEST_PROFILE`; direct execution accepts
  `--renderer`/`--profile` or infers `build/hammond_render` and its profile.
  Missing configured inputs are explicit errors; no CLI tests silently skip.
- Explicit little-endian RIFF fields/sizes plus an independent `wave` read;
  PCM16, equal stereo channels, exact frame count, one-frame and partial tails,
  block 65536, maximum unsigned seed, and 44100/48000/96000 Hz.
- Actual nonzero samples, default gesture equivalence, exact release silence,
  block-end and final-sample events, stable/reversed ties, initial registration
  order, initially muted lower drawbars and source continuity through silence.
- Same-build replay and identical WAV bytes/float metrics at blocks
  1/17/64/127/512/1024; a changed seed changes PCM. Dense scores contain 3261
  events, with exactly 1024 at frame zero and frame 17, and match a sparse
  equivalent at every requested partition. Initial controls do not consume
  score capacity. A 1025-event timestamp rejects before publication.
- Unknown/duplicate/missing flags, unsigned grammar/overflow/bounds,
  registrations, score names/fields/values/order/encoding and duration reject.
  Real 16 MiB+1, 262145-event and 4097-byte-line inputs exercise size gates.
  Empty/BOM/UTF-8-comment/whitespace and valid decimal forms are accepted.
- Missing/nonregular/malformed profile and score files, lexical/input/hard-link
  output collisions, existing files/directories and invalid parents preserve
  inputs and previous output. Every invocation checks for orphan output/temp
  paths; preflight failures use exit 1 and a diagnostic without JSON success.
- JSON identifies the supplied profile/digest and explicit unmeasured model.
  Float peak/RMS differ from PCM values within half an LSB for unclipped audio.
  A two-manual full-registration fixture clips at both PCM endpoints; a 1/16
  expression render independently bounds clipped-frame count and verifies float
  metric scaling. Fail-on-clip uses exit 2, matching float metrics and no output
  or temporary residue; unclipped fail-on-clip rendering succeeds.

## Executed evidence

Task-local CMake/CTest: `build-tools/cmake/data/bin/` under session scratch.
Configured `cmake -S . -B ../agent18-build -DCMAKE_BUILD_TYPE=Debug` and built
`cmake --build ../agent18-build --target hammond_render --parallel 2`: pass,
GCC 14.2/C++20 with the project's strict warning-as-error flags.

`python tests/test_render.py --renderer ../agent18-build/hammond_render
--profile ../agent18-build/nominal.b3p`: **20 passed in 1.092 seconds**.
After reconfiguration, `ctest --test-dir ../agent18-build
-R '^python_test_render$' --no-tests=error --output-on-failure`:
**1/1 CTest target passed in 1.04 seconds**, using injected paths.
Separate absent-executable/profile probes both fail clearly with no skips
(unittest returns exit 5 for zero tests plus setUpClass error in this runtime).
Whitespace checks on both assigned files were clean. No renderer defect found.

## Limits and handoff

These are Linux/GCC engineering regressions, not measured audio, hardware,
host, real-time deadline, cross-compiler identity or other-platform evidence.
The concurrent destination-publication race remains agent 15's separate probe;
this suite deterministically tests preexisting destinations and failure cleanup.
Coordinator owns CMake integration and shared status/log updates.
