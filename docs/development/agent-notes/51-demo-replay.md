# Agent 51 — independent demo consumption and local replay

Actual assignment: wave 09 of the original 60-agent session, 2026-11-13.
Read AGENTS, current status/queue, both ledgers, render evidence/verifier
contracts, atlas review, and atlas pp. 481–486. The newer continuation ledger
remains distinct; this work does not invent a continuation assignment.

## Changes and observed results

- Added `tests/test_demo_bundle.py`: seven bounded standard-library methods,
  auto-discovered by CMake; no current renderer is required or launched.
- The gate independently consumes Agent 50's pristine seven-file demo, pins its
  retained identities, checks full four-second settings/profile/34-event score,
  decoded stereo PCM, timeline/silence, zero clipping and explicit scope.
- Copied-bundle CLI and historical/foreign path cases preserve original metadata;
  unavailable executables do not claim verification or replay of that binary.
- Reproduced a concrete consumer defect before editing: absent executable under
  a real symlinked ancestor failed with `directory is not a regular nonsymlink
  directory`. Reported it to root and received direction to make the narrow fix.
- `tools/verify_render.py` now probes the final external path's availability
  before strict ancestor checks. Present file hash/type/ancestry/stability checks
  remain active. The real reproduction then returned `unavailable` with
  `FileNotFoundError`, retained integrity verified, and replay not performed.
- Added [the complete replay record](../../DEMO_REPLAY.md), with exact commands,
  reproduction, setup, hashes, metrics, limits and native CI handoff.

## Executed checks

- `PYTHONDONTWRITEBYTECODE=1 python3 tests/test_demo_bundle.py -v`:
  7/7 methods passed, 0 skips, 0.525 s.
- `PYTHONDONTWRITEBYTECODE=1 HAMMOND_RENDER_EXECUTABLE=/tmp/hammond-wave07-asuv11lz/build/hammond_render HAMMOND_TEST_PROFILE=/tmp/hammond-wave07-asuv11lz/build/nominal.b3p python3 tests/test_verify_render.py -v`:
  affected existing verifier suite 27/27 passed, 0 skips, 0.899 s.
- Native CMake 4.4.4 configured the current tree in a separate `gate-build`;
  `ctest --test-dir /tmp/hammond-a51-replay-xuy_r2pb/gate-build -C Release -R '^python_test_demo_bundle$' --output-on-failure --no-tests=error`:
  selected CTest passed 1/1 in 0.52 s, without building unrelated targets.
- Owned-file syntax, trailing-whitespace, local-link and scoped diff checks passed.

## Actual fresh build/replay

- Clean `git archive` of `6c3dd8bc923a3c11f6b234425b056e135fbe9f4b` extracted
  to `/tmp/hammond-a51-replay-xuy_r2pb/source`; no `.git` or local edits copied.
- GCC 14.2.0 Release (`-O3 -DNDEBUG`), CMake 4.4.4, Python 3.12.14;
  sanitizers and test targets off; built only renderer/core/profile. Exit 0.
- Archived wrapper actually rendered retained inputs/settings into a new
  `/tmp/hammond-a51-replay-xuy_r2pb/rerender`; wrapper and verifier exited 0.
- Original/fresh renderer bytes agree, SHA-256
  `8e781cb1df6f87443c4b6c88587cfa0e7d2bc8e23d32b5ef0a0bfb84d9ee8be4`.
- Original/fresh complete WAV bytes agree, SHA-256
  `9c46d82dc8da8ba5be078e895765e98672b51a30da52e0684d75a293aa4d84fd`.
- Interleaved PCM SHA-256
  `1c2216be3fced52b677be9e09393d0edccf98292529668019f88495a7c88600f` agrees.
- All input/compiled/log bytes, parameters, float metrics and PCM metrics agree.
  Float peak/RMS: `0.08130008727312088` / `0.02006219567993473`;
  integer peak/sum squares: `2664` / `82976846092`; zero clipping.
- Agent 50's manifest stayed unchanged at SHA-256
  `74ad49caa3cc5170870bed1002ea64ffaaf8a202c0614095b31fdcd8308da2ce`.

No full-suite repetition, sanitizer/native Windows/macOS run, audio playback,
host qualification or physical validation was performed. Historical paths and
Linux simulations do not close native hosted CI. Same local toolchain equality
establishes neither authentication/build provenance nor cross-platform bitwise
reproducibility. No dependencies, source-data edits, commits, pushes or subagents.
Root owns integration, shared status/log updates, publication and hosted results.
