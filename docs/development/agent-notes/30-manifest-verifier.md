# Agent 30 — independent retained-render verifier

## Assignment and boundary

Wave05 Agent30 owned `tools/verify_render.py`, `tests/test_verify_render.py`,
`docs/RENDER_VERIFICATION.md`, and this note. No commits, pushes, producer edits,
shared status edits, or delegated agents. Read AGENTS/status/next-step/plan/log,
atlas evidence-boundary review, the relevant acquisition/schema review notes,
render/profile contracts, finalized producer schema and Agent25 retained smoke.

## Implemented

- Standard-library consumer with no producer imports or verification helpers.
- Strict bounded JSON/schema/type validation and success/null-error/synthetic
  scope gates; exact artifact inventory, nonsymlink paths, size/SHA-256 checks.
- Reused only the supported profile compiler for canonical authoring identity
  and exact compiled-profile reconstruction; independent event grammar parser.
- Exact recorded argv/parameters/flags/capture reconciliation; retained stdout
  equality, named unmeasured model, zero clipping and finite bounded metrics.
- Independent streamed PCM16 header/channel/frame/integer-statistics checks and
  recomputed normalized metrics/quantization comparisons; no whole-audio buffer.
- Current renderer rehash when available. Missing/unreadable/non-native external
  renderer explicitly reports unavailable while retained-bundle checks can pass.
- Relocated bundles retain historical argv; artifacts use fixed local names.
- Machine-JSON CLI, exit 1 on failure; importable `verify_bundle` API.

## Executed evidence

Native CMake/CTest directory:
`/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/`

```sh
cmake -S . -B /workspace/scratch/c871510c69b2/agent30-release \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build /workspace/scratch/c871510c69b2/agent30-release \
  --target hammond_render -j 2
ctest --test-dir /workspace/scratch/c871510c69b2/agent30-release \
  -R '^python_test_verify_render$' --output-on-failure --no-tests=error -V
python3 tools/verify_render.py \
  /workspace/scratch/c871510c69b2/agent25-retained-short/manifest.json
```

GCC14.2 Release renderer build passed. The consumer suite passed all 27 unittest
methods, including real generated fixtures and targeted mutations, with no skips.
Real fixtures cover all three rates, UINT64_MAX seed, partial blocks, empty events,
all event types and literal paths. Mutations include rehashed altered files so
the suite tests semantic checks beyond digest comparison. Metadata observations
also test a file changed after reading and stable cross-API timestamp differences.

Agent25 retained 1031-frame bundle passed; its available renderer hash matched.
Manifest SHA-256: `e83a0273401dbcaf0f8380d5a7a8957c2f14bcd9143618e15a42f3571d6c08b8`.
WAV SHA-256: `36817d4c198d3d2f4e4b10458fdb4183047dcc665d2aa17255f8a02ee0a432ae`.
No producer discrepancy was found in this Linux scope.

## Limitations and handoff

Root reported a Windows producer metadata failure under native CI; Agent33 owns
that producer repair. This consumer compares path and descriptor metadata within
each API and uses POSIX device/inode agreement only where applicable. Windows
reparse paths are rejected. A simulated metadata test is not native Windows/macOS
qualification; those platforms remain unexecuted in this assignment.

Verification reports retained-byte consistency, never replay or authentication.
Original source/tool paths are typed historical records, not reverified files.
An internally consistent forged bundle is possible without independent trust.
Source-to-binary provenance, reproducible builds, linked libraries, physical
fidelity, host/device behavior and real-time deadlines remain unestablished.
The integrator owns shared handoff documents and any subsequent integration tests.
