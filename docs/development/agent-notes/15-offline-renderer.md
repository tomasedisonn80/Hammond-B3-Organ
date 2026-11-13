# Agent 15 — portable offline renderer

## Assignment and inputs

Owned `tools/render.cpp` and this note only; no commits, pushes or subagents.
Read AGENTS, README, status/next steps/log/plan, implementation and render/API
contracts, current Types/Profile/Engine headers, atlas review/errata and atlas
chapter 063 (PDF pp. 385-390). This is a new M1/M2 engineering client, not a
measured organ, cabinet, device application or plugin.

## Implemented behavior

- Required profile/output; defaults 48000 Hz, block64, four seconds at the
  selected rate, seed0, upper registration888000000 and MIDI60. Supported rates,
  frame/block/note bounds, unsigned flag grammar, duplicates, unknown flags and
  explicit note/events conflict are checked before any output is created.
- Profile and score must be regular bounded files. Preflight rejects output/input
  collisions, existing output entries (including symlinks), invalid parent paths,
  malformed/unsorted/out-of-duration scores and invalid payload names/ranges.
- Score limits: 16 MiB, 262144 events, 4096 bytes per line, 128 bytes per numeric
  token and 1024 actual events at one frame. UTF-8/ASCII, an initial UTF-8 BOM,
  blank lines and full-line comments are accepted; NUL/invalid UTF-8 are rejected.
  Frame/index tokens are unsigned integers; values are finite decimal numbers
  with integral values required for note velocity/drawbars. No silent coercion.
- Initial upper drawbars use a separate zero-frame engine call. Lower drawbars
  remain muted. Default note-off is at floor(3*frames/4); score input replaces
  the gesture. Stable ties, exact absolute sample positions, positive subdivision
  of dense blocks and partial final blocks are preserved.
- PCM16 uses explicit little-endian RIFF sizes and identical dry stereo channels.
  Quantization rounds sample*32768 to nearest, ties away from zero, then saturates
  to [-32768,32767]. Float peak/RMS precede conversion; clipped frames count
  samples outside [-1,1] once, with doubled channel count separately reported.
- JSON stdout identifies `ideal-shared-sine-v1`, unmeasured evidence status,
  profile ID/supplied authoring digest, actual rate/block/frames/seed and metrics.
  Success is status `ok`; fail-on-clip is status `clipped`, stderr and exit2.
  Other errors use stderr and exit1. Source/file/executable hashes remain the
  separately assigned Python wrapper's responsibility.
- A temporary sibling directory is atomically reserved, then its WAV is streamed
  and closed. Successful publication uses standard C++20 `create_hard_link`,
  which refuses an existing destination even if another writer wins a race.
  No overwrite fallback exists. Filesystems without hard-link support fail
  explicitly; completed output is never published on clipping-policy failure.
  Temporary cleanup uses RAII. All file/string/vector work is outside process.

## Executed verification

Task-local CMake executable:
`/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake`.
Ran `cmake -S . -B /workspace/scratch/c871510c69b2/agent15-build
-DCMAKE_BUILD_TYPE=Debug -DBUILD_TESTING=OFF`, then
`cmake --build /workspace/scratch/c871510c69b2/agent15-build
--target hammond_render --parallel 2`: **pass** with GCC14.2/C++20 and
`-Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror`.

Scratch Python subprocess/struct/wave probes passed:

- 3856-event score, including 1024 events at frame0: byte-identical WAV and
  float metrics for blocks1/17/64/257/65536; 4099 frames verifies a partial tail.
- RIFF/data lengths, little-endian PCM16, both identical channels, all three
  supported rates; default gesture equals its explicit absolute-event score.
- 33 malformed CLI/score and existing/input-alias output rejections; separate
  16 MiB+1 and 262145-event rejection probes; empty/BOM/UTF-8-comment silence.
- Full two-manual registration: peak7.883309364318848,
  RMS2.7847720285203716, 698 clipped frames/1396 clipped channel samples.
  PCM reaches both saturation endpoints; fail-on-clip preserves these metrics
  and leaves neither final output nor temporary directory.
- A competing destination created during rendering remained byte-for-byte
  intact; publication failed and temporary output was removed.
- `git diff --no-index --check /dev/null tools/render.cpp`: clean.

Scratch probe directories have prefixes `agent15-smoke-`, `agent15-clip-` and
`agent15-race-` under the session scratch root. Permanent CLI tests belong to
agent18. Only this Linux/GCC environment was executed; other platforms,
cross-compiler floating identity and physical fidelity remain unverified.
