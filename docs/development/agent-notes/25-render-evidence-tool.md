# Agent 25 — reproducible render evidence wrapper

## Assignment and inputs

Owned `tools/render_fixture.py`, `tests/test_render_fixture.py`,
`docs/RENDER_EVIDENCE.md` and this note only. No commits, pushes or subagents.
Read AGENTS, README, status/next steps/log/plan, atlas review/errata,
RENDER_FORMAT, actual compiler/renderer/CMake contracts, prior renderer notes,
and atlas chapter 063 (PDF pp. 385-390). No physical fidelity claim.

## Implemented

- Stdlib CLI requires an explicit renderer and a new output directory; defaults
  to nominal authoring JSON and the C++ renderer's rate/block/seed/gesture.
  Optional events, note/registration/frame bounds, duplicate/unknown arguments,
  UTF-8 event grammar and retained-bank/Cancel payloads are preflighted.
- Exact authoring/event bytes are copied; the importable profile compiler produces
  the retained binary-contract text. Executable, inputs/copies, compiler/wrapper,
  compiled profile, logs and verified WAV have SHA-256 identities. Original inputs,
  copies, executable and tool bytes are checked again after invocation.
- Renderer uses argument-list execution and mandatory `--fail-on-clip`; raw stdout,
  stderr, actual JSON metrics, return code, timeout/truncation and errors persist.
  Preflight errors create no result; later failures retain failed/incomplete status.
  Existing output entries are untouched; only complete success gets a WAV record.
- Manifest schema 1 declares `synthetic_engineering`, parameters, UTC/Python/platform,
  Git HEAD/dirty context, and `binary_association: not_established` regardless of HEAD.
  The documentation specifies an independent consumer's checks without helper reuse.
- RIFF header/rate/count/stereo checks and exact integer PCM sum-of-squares stream
  64 KiB blocks. Prequantization engine metrics remain distinct from PCM metrics;
  comparison permits 1/32768 plus 1e-12 to cover rounding and positive saturation.
- Explicit bounds: 600 seconds audio, renderer timeout 1..600 seconds (default 120),
  16 MiB score, 512 MiB executable, 1 MiB/log, 16 KiB flat metrics JSON; existing
  profile limits apply. Overflow/truncation/malformed metrics cannot report success.

## Actual verification

Used `/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake`:
`-S . -B /workspace/scratch/c871510c69b2/agent25-debug
-DCMAKE_BUILD_TYPE=Debug -DBUILD_TESTING=ON`, then
`--build /workspace/scratch/c871510c69b2/agent25-debug --target hammond_render --parallel 2`:
**pass**, GCC 14.2/C++20 with the repository's strict warning gate.

`ctest --test-dir /workspace/scratch/c871510c69b2/agent25-debug
-R '^python_test_render_fixture$' --output-on-failure --no-tests=error`:
**pass**, 14 Python cases through CMake-injected real executable/profile; 2.28 s.
Direct runs against agent22 Debug also passed all 14 cases. Cases include replay
excluding timestamp/path metadata, all rates/max seed, exact event bytes, actual
clipping/CLI nonzero status, no-clobber, changed source/copy/executable bytes,
malformed WAV/metrics, launch failure, timeout and bounded log capture.
Missing both prerequisite environment variables deliberately failed with an explicit
build/CMake instruction (zero cases, exit 5), never skipped. Python compilation
and whitespace inspections were clean; new-file diff checks return 1 for additions.

Retained short smoke: `/workspace/scratch/c871510c69b2/agent25-retained-short/manifest.json`.
1031 frames, 48000 Hz, block127, seed7, upper `008000000`, note60; zero clipping.
WAV SHA-256: `36817d4c198d3d2f4e4b10458fdb4183047dcc665d2aa17255f8a02ee0a432ae`.
Float peak/RMS: 0.029999984428286552 / 0.018581136329633777;
PCM peak/RMS: 0.029998779296875 / 0.018581447639578395. Quantization checks pass.

## Limits and handoff

Only Linux/GCC/Python 3.12 was executed. This is no hostile-code sandbox or proof of
source/binary provenance, physical calibration or real-time performance.
Hashes cannot authenticate a forged bundle or detect changes restored between reads.
Independent verification belongs to agent30; see RENDER_EVIDENCE. Parent owns shared logs.
