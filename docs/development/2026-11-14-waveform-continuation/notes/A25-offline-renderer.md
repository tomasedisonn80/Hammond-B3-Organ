# A25 — Bounded native offline rotary developer renderer

## Actual assignment and ownership

- Worker: `/root/w05_a25_offline_renderer`, logical wave 5, 14 November 2026.
- Inspected HEAD: `0881d1f4c5a26ce9c75dda7a3adde46382e5ab6b`. The renderer and
  several other tracks were an uncommitted overlay; this HEAD alone does not
  identify their qualified bytes.
- Owned implementation: `tools/rotary_render.cpp`.
- Owned contract/operator documentation: `docs/ROTARY_RENDER_CLI.md`.
- Owned evidence: this note and `reports/a25-author-cli.json`.
- Private author workspace: `/workspace/scratch/e3cacb90cc81/a25-offline-renderer`.
  No shared `../build`, production renderer/header, CMake, CI, existing
  acceptance runner/oracle, musical-state source or Git HEAD was changed.

Read `AGENTS.md`, the current waveform README/checkpoint/actual manifest, the
complete project plan and atlas review, A04's retained rotary reading, the
frozen renderer contract, build plan, current status/next steps/development log,
the renderer/types/history interface, and the existing CLI path/Windows entry
pattern. The parent warned that the live checkpoint lagged active qualification;
this worker did not reinterpret its pending labels as actual new results.

Before implementation, sent the exact CLI/header proposal to the integrator.
It was accepted. Coordinated the generated-header interface directly with
actual A26 `/root/w05_a26_profile_compiler`; its compiler, header-generation
tests and independent CLI acceptance are separate work.

## Implemented behavior

The entry point is:

```text
hammond_rotary_render --horn FILE --drum FILE --sample-rate RATE \
  --output-dir NEW_DIRECTORY [--block-size 1..4096] [--events FILE]
```

Supported exact rates are 44,100, 48,000, 96,000 and 192,000 Hz. Default block
size is 64. Both inputs are explicit raw little-endian binary64 mono streams,
equal whole-frame lengths, finite and in closed `[-1,1]`, with a fixed 60-second
maximum. Empty input is allowed. Byte decoding/encoding is explicit, and the
audio workspace is fixed on the heap rather than proportional to file length.

Events have exactly three ASCII fields: `frame horn|drum chorale|tremolo`.
The file is bounded to 64 KiB, 64 bytes per line and 1,024 events. Empty files
are valid; blank lines, extra fields, unsupported tokens/encodings, decreasing
frames and frames outside inclusive `[0,input_frames]` reject. LF/CRLF and an
unterminated final line are accepted; bare CR is rejected. Equal-frame order
is retained, including all final-input-boundary commands before the tail.

Every invocation appends exactly the prepared renderer's explicit zero-input
tail while motion advances. The output directory and each output file are
created exclusively. Existing destinations and inputs are never overwritten;
ordinary error cleanup removes only the two files actually created by this
invocation and its new directory, without recursive deletion. Concurrent input
rewrites and crash recovery are outside the contract; detected input truncation
or extension rejects.

`stereo.f64le` retains signed, unclipped, unnormalized, unresampled double
left/right sums. `report.json` records the source profile SHA-256 and generated
function, renderer/numerical contracts, paths (including exact native path-byte
hex), rate/block size, separate input/tail/output counts, two-frame algorithmic
latency, separate physical travel bounds, final motion state, solver diagnostics,
output peaks/counts above unity, and explicit gain/synthetic-boundary warnings.

The generated include is `RotaryNominalProfile.h`; the consumed interface is
`hammond::rotary::generated::{kProfileId,kProfileSha256,nominal_profile}`. No
arbitrary runtime profile parser or dependency was added. Windows uses the
existing `wmain`/UTF-8 conversion and a wide exclusive output-file open; its
actual executable remains a separate platform gate. The Microsoft primary
[CRT documentation](https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/fopen-s-wfopen-s?view=msvc-170)
was checked for the wide `_wfopen_s` entry and exclusive `x` mode; this source
review is not a Windows execution result.

## Exact source and build identity

| Input/artifact | SHA-256 |
| --- | --- |
| `tools/rotary_render.cpp` | `3fd1a4e2a79cea4a0964394193aa4e993df5d91ff257415e380523206d514a97` |
| `data/rotary/nominal-research-v1.json` | `c0473cb20604726d989d7c280700109f647f7b227edb71c61d275ed9bfd67443` |
| A26 generated `RotaryNominalProfile.h` | `d51f3e6edf4f44f87ed65f9a80b9932299ee8d5fa52a2fad5b5d011a454a05a5` |
| Private GCC executable | `ea7ef59afe78c495c29cb5f80866b5d52800a6aa6c7da44eca4465e931008060` |

The machine report additionally hashes the exact production renderer/path/
history/motion sources, private storage header, public types and CLI helper.
The compiled native input is therefore identified independently of the dirty
worktree's Git HEAD. The author script and generated header are separately
hashed there; they are reproducible scratch inputs, not claimed as repository
test files.

Actual compiler: `g++ (Debian 14.2.0-19) 14.2.0`.
Working directory: `/workspace/scratch/e3cacb90cc81/Hammond-B3-Organ`.
The A26 generated directory was consumed read-only. Executed build, exit 0:

```sh
g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion \
  -Wsign-conversion -Wshadow -Werror -I include \
  -I /workspace/scratch/e3cacb90cc81/a26-profile-compiler/generated \
  tools/rotary_render.cpp src/RotaryMotion.cpp src/RotaryPropagation.cpp \
  src/RotaryHistory.cpp src/RotaryStreamingPath.cpp src/RotaryRenderer.cpp \
  -o /workspace/scratch/e3cacb90cc81/a25-offline-renderer/hammond_rotary_render
```

No warnings were emitted. No third-party dependency, permissive warning flag,
shared CMake configuration or renderer-source modification was needed.

## Executed author checks

Executed:

```sh
python3 /workspace/scratch/e3cacb90cc81/a25-offline-renderer/author_checks.py
```

Result: **83 CLI subprocess cases passed in 5.399838432 seconds**, with exact
exits and bounded diagnostics retained in
[`a25-author-cli.json`](../reports/a25-author-cli.json). This is author evidence,
not the independent A26 acceptance or the integrator's running full R4 campaign.

The substantive checks were:

- All four rates × blocks 1/7/64/257/4096, using 8,193 distinct signed input
  frames and ordered/tied/internal/final-boundary commands. Every alternate
  partition had exactly equal output bytes, final state and full reported
  diagnostics at the same rate. The canonical hashes below retain the result.
- Empty input and frame-zero/tied terminal events at each rate, an empty event
  file, and exactly 1,024 same-frame commands. Counts, final commands, output
  length, silent output and explicit continuing tail were checked.
- Both positive and negative unity inputs were accepted. Sustained signed
  outputs exceeded unity, were exact sign inverses, and retained matching peak
  and above-unity statistics. No output clamp or normalization was observed.
- NaN, both infinities and both nearest out-of-range values placed after 8,192
  valid frames rejected and removed the partially written output directory.
  Partial frames, unequal lengths, directory input and sparse files one frame
  beyond each tested 60-second bound rejected before successful output.
- Twenty-three malformed event classes rejected, including missing/extra
  tokens, whitespace/embedded blank lines, unknown rotor/command, signed/
  fractional/overflow frames, decreasing/past-end frames, NUL/BOM/non-ASCII/
  vertical-tab/form-feed/bare-CR input, long lines, 1,025 events and oversized
  files.
- Unicode/space input and output paths round-tripped through valid JSON. A
  native invalid-UTF-8 POSIX byte remained exact in the report's hex field.
  Existing files/directories/input paths, ordinary and dangling symbolic links,
  and a missing parent were rejected without overwriting the preserved data.
- Required/unknown/duplicate/oversized options and invalid rates/block sizes
  rejected. An actual POSIX file-size-limit write failure, with `SIGXFSZ`
  ignored in the child, returned nonzero and removed its partial output.
- Input files and events retained their exact original hashes after all runs.

| Rate | Input frames | Tail frames | Output frames | Canonical stereo SHA-256 |
| ---: | ---: | ---: | ---: | --- |
| 44,100 | 8,193 | 222 | 8,415 | `a21e50e5dff07e70c59b05d3c73bfcf952bd992519d1c6b454ee23ddba696ea1` |
| 48,000 | 8,193 | 242 | 8,435 | `c18351aec88be310809fe73aa93a559ced292704090c85766abad056d59b4ff8` |
| 96,000 | 8,193 | 479 | 8,672 | `4e873429d55d7efff5029d7bee94cbe17d92edd61b837a59e2432514c491c3c0` |
| 192,000 | 8,193 | 953 | 9,146 | `46f61e61e7e7fa190ac991029d50faa394c598062fc30dc85cb0c5c7519d6f50` |

Also executed the documentation's 4,800-frame synthetic example, using private
absolute paths. Exit 0; 242 explicit tail frames; 5,042 output frames; 80,672
audio bytes. Stereo SHA-256:
`d063f76998193a6febba12419a44bf30623e43db1e123cfcef007d102abc50da`.
The exact native invocation and observed first eight zero frames are retained
in the machine report. The example does not validate organ or cabinet sound.

## Remaining work and limits

The integrator owns CMake/header generation dependencies, the target's strict
platform flags/MinGW Unicode startup, CTest environment and coherent build.
Actual A26 owns independent compiler/CLI acceptance. They were notified that
the source and private executable were ready; those results must be recorded
under their actual owners and exact tested bytes.

Not run by A25: a successful full 60-second render, big-endian host execution,
Windows/MSVC or macOS executables, sanitizer qualification of this new CLI,
independent same-cubic/full R4 comparison, R5 audible reconstruction, R6
integration/deadlines/devices, or physical cabinet acceptance. These are not
inferred from byte-format code, partition checks, zero observed errors or
existing renderer evidence. The whole project's dry Engine, 47 parameters,
state4/readers 1–3, physical unknowns and remaining M0–M9 gates are preserved.

No commit, publication, remote update or shared status edit was attempted.
