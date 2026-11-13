# Assignment 15: offline contact/percussion renderer

Agent: `/root/w03_a15_renderer_extension`; continuation wave 03, 2026-11-13.

## Scope and changes

Owned only `tools/render.cpp`, `docs/RENDER_FORMAT.md`, and this note. Read the
standing instructions, current status/next-step context, console dynamics contract,
engine/control interfaces, and the existing complete renderer implementation.

- Added explicit `--contacts ideal|nominal`, `--percussion off|second|third`,
  `--percussion-volume normal|soft`, and `--percussion-decay slow|fast` options.
- Preserved default ideal contacts, disabled percussion, and all previous flag
  meanings. New options reject unknown values, missing values and duplicates.
- Derived the maximum argument count from the complete unique flag inventory;
  the existing note/score incompatibility remains a separate semantic check.
- Selected the validated C++ console factory at preparation. Initial processing
  applies nine drawbar events followed by four percussion events in one zero-frame
  flush. Scored events, including frame zero, have subsequent precedence.
- Added strict `percussion` score events: Upper only, indices 0-3 for enable,
  harmonic, volume and decay, each with integral value 0 or 1. Invalid inputs
  reject before creating output. Existing absolute timing, stable ties, dense
  subdivision and score capacities remain unchanged.
- Every summary now adds exactly `render_schema_version: 2`, `contact_model`, and
  `percussion_model`. Existing fields retain their meaning. The generator `model`
  remains `ideal-shared-sine-v1`; algorithm metadata is emitted even when the
  percussion control is disabled. Invocation/score identity still matters.
- Preserved WAV encoding, explicit clipping, input/output collision checks,
  temporary-file cleanup and atomic no-clobber publication.

## Actual verification

Strict GCC 14.2 / CMake 4.4.4 Release build:

```sh
cmake -S . -B ../agent15-renderer-build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build ../agent15-renderer-build --target hammond_render -j 3
```

The executed CMake binary was the task-local tool at
`/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake`.
The target built successfully with the repository's complete warning policy and
`-Werror`. The integrator owns publication of an immutable combined snapshot.

A bounded scratch Python driver invoked the actual new executable and the
integrator-retained earlier renderer. Command:

```sh
python3 /workspace/scratch/60e8291da354/agent15-renderer-check.py
```

Observed result: **passed**, with the following meaningful checks:

| Scope | Observed checks |
| --- | --- |
| Legacy compatibility | 12 exact WAV-byte comparisons: rates 44,100/48,000/96,000 Hz, blocks 1/257, registrations `888000000` at MIDI 60 and `008000000` at MIDI 96, seed 937, 4,097 frames. Removing the three new metadata fields leaves the exact previous JSON values. |
| New rendering | 13 checks: CLI settings equal equivalent initial score controls; frame-zero disable overrides a CLI enable; percussion-only audio is nonzero; nominal 8-foot contact onset is frame 123 at 48 kHz; lower-manual audio and upper-A ineligibility behave separately; dense scores match byte-for-byte for blocks 1/17/64/1,024/65,536; 1,024 tied score events remain accepted despite the separate 13-control initial flush; all simultaneously legal flags are accepted. |
| Rejection/publication | 26 checks: invalid/missing/duplicate new flags; lower-manual, out-of-range, fractional, nonfinite and malformed percussion score records; 1,025 tied events; preservation of an existing output; and a clipped nominal percussion render returning status 2 without publishing a WAV. Temporary render directories were absent after rejection. |

The new renderer executable's SHA-256 for this local build was
`b9c0acab7615820091bd7baaf782d894a8b85bb910a2dfba72b84463445d74c9`.
The tested renderer source SHA-256 was `b808397706399696a8598bcb55a0c4c281c6166235bf1c41ef3d778a01a0a8a5`.
The retained old executable came from the observed `7c2ad20` baseline build; its
SHA-256 is `8e781cb1df6f87443c4b6c88587cfa0e7d2bc8e23d32b5ef0a0bfb84d9ee8be4`.
The nominal compiled profile SHA-256 remains
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.

## Integration handoff and limits

Agent 18 owns independent permanent CLI regressions and the intentional update of
old exact-summary expectations. Evidence producer/consumer agents must explicitly
support the three new schema-2 fields and initial console controls; their old
strict metadata grammar is not silently loosened here. No existing tests,
producer, verifier, CMake file or shared status document was edited by this task.

Contact timing and readiness remain named unmeasured models. No physical circuit,
contact antialiasing, host, audio-device, sanitizer or native-platform pass follows
from these Linux offline checks. No commit, push or remote mutation was performed.
