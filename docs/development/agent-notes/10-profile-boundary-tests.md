# Agent 10 — permanent profile boundary tests

## Scope and evidence

- Wave 02 assignment; edited only `tests/test_profile.cpp` and this note.
- Read AGENTS, README, STATUS, NEXT_STEPS, latest log, PLAN, implementation and
  profile contracts, Types/Profile headers, Profile.cpp, and atlas review note02.
  `docs/research/ATLAS_REVIEW.md` was absent at review time.
- Agent 09 supplied the always-active CHECK helpers and CMake test discovery;
  Agent 08 supplied the strict compiler and nominal authoring/compiled profile.
- No implementation edits, commits, pushes, or hardware-fidelity claims.

## Permanent coverage

- All 91 frequencies use independent chromatic anchors plus exact octave scaling;
  all amplitudes/phases, nine gains, output gain, and profile identity are checked.
- Six manual rows are fixed from atlas p.102: keys 1,13,43,44,56,61. Seven additional
  explicit transition vectors are calculated regressions, not factory evidence.
  All 549 entries are checked for range and consecutive/fold-transition behavior.
- A separately encoded profile varies every source field and manual entry, then
  compares every parsed field. Atomicity checks compare all metadata bytes, gains,
  all source values and map entries; no padding-sensitive memcmp is used.
- 2,601 malformed stream cases cover every truncated token prefix, all source
  positions, all map positions, duplicate/out-of-order/unknown records, unsupported
  versions, count mismatches, metadata syntax, decimal syntax/ranges/nonfinite
  spellings, overflowing IDs, extra tokens, NUL/non-ASCII input and UTF-16 bytes.
- Exact 128 KiB text accepts; one extra byte rejects. ASCII whitespace/CRLF,
  signed/scientific decimals and a comma-locale stream verify portable text
  handling. This was not executed on a big-endian machine.
- Failed streams, exceptions at ordinary EOF, injected mid-read I/O failures with
  and without exceptions, valid files and a missing-file path are covered.
- Runtime checks exercise every source and map field, metadata arrays, finite
  ranges, supported 44.1/48/96 kHz rates, exact/above/below Nyquist for every source,
  positive subnormal frequency and strict phase/drawbar endpoints.
- Tone-ID conversions cover all 256 byte values; invalid MIDI/manual domains
  preserve destination indices. CHECK remains active with Release/NDEBUG.
- A syntactically valid replaced digest and varied numeric payload are accepted
  deliberately: C++ checks safety and syntax; Python owns nominal semantics and
  authoring provenance. An embedded digest alone does not authenticate payloads.

## Executed results

- Toolchain: GCC 14.2.0, C++20, task-local CMake 4.4.4 at
  `/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake`.
- PASS Debug: configure `-S . -B build -DCMAKE_BUILD_TYPE=Debug`, then
  `--build build --target test_profile -j 1`; CTest `--test-dir build`
  `-R '^test_profile$' --output-on-failure`: 1/1 passed, final source.
- PASS Release: configure external `agent10-release` with
  `-DCMAKE_BUILD_TYPE=Release`, build target and run `test_profile`:
  2,601 malformed cases passed. Compile database confirms `-O3 -DNDEBUG`.
- Both builds use `-Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion`
  `-Wshadow -Werror`. Final test source is 362 lines.
- PASS ASan+UBSan: external `agent10-sanitize`, Debug,
  `-DHAMMOND_ENABLE_SANITIZERS=ON`; CTest 1/1 passed with
  `ASAN_OPTIONS=detect_leaks=0`. Default LeakSanitizer could not finalize:
  it reported that leak detection does not work under ptrace. No leak pass claimed.
- Initial named-target build required CMake reconfiguration for newly added test
  discovery. One initial calculated key 60 fixture typo was corrected: its fifth
  route is 91, so the boundary does not fold. No parser implementation bug found.
- `git diff --check` passed. No engine/callback/host/audio tests were part of this
  assignment. Factory transcription, physical measurements, other compilers and
  actual big-endian execution remain unverified; the integrator owns shared logs.
