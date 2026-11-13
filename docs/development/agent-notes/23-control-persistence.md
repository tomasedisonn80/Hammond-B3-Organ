# Agent 23 — bounded control persistence

## Assignment and scope

Wave 04: implement CONTROL-only persistence, independent of audio processing.
Owned only `include/hammond/ControlStateIO.h`, `src/ControlStateIO.cpp`,
`tests/test_control_io.cpp`, `docs/CONTROL_STATE_FORMAT.md` and this note.
Read repository instructions/current handoff, `CONSOLE_EXTENSION.md`, control
validation, profile parsing conventions and atlas pp. 151–156, 389, 401.
No Engine changes, file-writing helpers, dependencies, commits, pushes or spawns.

## Implemented contract

- APIs: `serialize_controls(snapshot, string, error)` and
  `parse_controls(istream, snapshot, error)`; full candidate validation uses
  `is_valid_control_snapshot`. Publication happens only after complete success.
- Exact `B3CONTROLS1` marker; expression, upper/manual A+B, lower/manual A+B,
  then `end`; all 39 controls plus two route bits; exactly 60 tokens.
- Inclusive 16,384-byte limit, at most 16,385 consumed characters; explicit A/B
  and 0/1 tokens, four fixed nine-position banks, strict ordering/trailing checks.
- Classic-locale canonical LF output with max_digits10 decimals, full-token
  locale-independent input, signed-zero/subnormal expression round trips.
- Invalid snapshots preserve prior output bytes. Invalid input/I/O failures
  preserve every snapshot field. Error text clears on success. Aliased output
  and error strings reject without mutation; allocation failures may propagate.
- Both operations allocate and require stopped/control-thread use on safely
  copied controls. The caller owns atomic file publication and overwrite policy.
- Excludes keys/ownership, phases, time, random history, reactive/rotor/tail state,
  profile identity, native host state and compatibility/checkpoint promises.

## Executed verification

Working directory: `/workspace/scratch/c871510c69b2/Hammond-B3-Organ`.
Commands used the repository's strict CMake configuration (GCC 14.2, C++20,
`-Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror`):

```sh
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake -S . -B /workspace/scratch/c871510c69b2/build-agent23-debug -DCMAKE_BUILD_TYPE=Debug -DBUILD_TESTING=ON
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake --build /workspace/scratch/c871510c69b2/build-agent23-debug --target test_control_io -j2
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/ctest --test-dir /workspace/scratch/c871510c69b2/build-agent23-debug -R '^test_control_io$' --output-on-failure
/workspace/scratch/c871510c69b2/build-agent23-debug/test_control_io
git diff --check
```

All commands passed. CTest: 1/1 passed. Direct test: 330 malformed inputs preserved
destination semantics, including every bank's invalid positions, selector/bound
errors, unknown versions, duplicates, truncations, trailing/oversized bytes and
injected stream failures before/during/after the complete payload. Tests cover
all 39 controls, both route bits, every A/B and route combination, exact canonical
fixtures, all nine positions, locale independence, EOF exceptions and bounded
consumption. No padding/memcmp oracle. Shared CMake globs discover both new files.

Release, sanitizer, host, callback timing and hardware qualification were not run
for this assignment. Engineering persistence is verified; full physical M3 and
native host compatibility remain open. Integrator owns shared handoff updates.
