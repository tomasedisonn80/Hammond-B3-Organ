# Agent 11 — strict authoring and compiler CLI tests

## Assignment and evidence boundary

Owned only `tests/test_compile_profile.py` and this note. Added no dependencies,
changed no compiler/schema/profile data, and made no commits or pushes.
Read `AGENTS.md`, current project handoff/plan, the profile-format contract,
compiler/schema/profile, atlas pp.61–66,98–99,102 and relevant review notes.
`docs/research/ATLAS_REVIEW.md` was absent at this checkpoint.

The six literal manual-row fixtures are independently transcribed from atlas
p.102: playing keys 1,13,43,44,56,61. They establish agreement with those printed
rows, not independent verification of the absent complete factory transcription.
Frequency checks validate the explicitly proposed 12-TET baseline; they provide
no measured tuning, phase, pickup, AO-28 or Leslie evidence.

## Delivered coverage

- 37 standard-library `unittest` methods; direct module import through the
  repository-relative `pathlib` path. CLI calls use `sys.executable`, unrelated
  temporary working directories and paths containing spaces.
- All 91 source identities/frequencies, independent anchors 1/13/46/73/91,
  monotonic order, inverse pitch equation and every available 12-step octave ratio.
- All 549 manual cells reject changed in-range values; all 91 source IDs and every
  source frequency/amplitude/base-phase field reject contradictory baseline data.
- Exact source/map/row/gain counts, map bounds, offsets/order, nominal gains,
  numeric ranges, and one-ULP frequency changes.
- Unknown properties and absent/unexpectedly-null required fields at every
  authoring object; versions/models/identity, units, evidence classes, unknown
  reasons, uncertainty/acquisition contradictions and invalid source locators.
- Boolean numeric fields, NaN/infinities, exponent overflow, huge integers,
  duplicate JSON keys (including escaped/equal/conflicting names), malformed
  UTF-8/JSON, invalid roots, surrogate strings and non-JSON imported objects.
- Exact 256-KiB input boundary including whitespace, over-limit input, bounded
  strings/depth/object width/arrays/node count and cyclic imported trees.
- Canonical SHA-256 includes Unicode metadata and follows the project's sorted,
  compact UTF-8 Python JSON convention; integer-vs-float authoring stays distinct.
  This is explicitly not an RFC8785 assertion. Reordered keys/whitespace and
  separate CLI hash seeds reproduce compiled bytes. API calls preserve inputs.
- Complete 160-line compiled interchange, ordered payload, one final LF and
  output below 128 KiB; structural schema checks without a JSON Schema dependency.
- CLI `--check` validates without writing and compares exact existing bytes;
  missing/stale/CRLF/alternative-number-spelling/oversized output rejects.
- Failed compilation preserves existing outputs and leaves absent outputs absent.
  Missing inputs, invalid output targets and directory write failures are clean.
  Same paths, lexical aliases, symlinks and hardlinks cannot replace authoring.

## Executed results

- `python3 tests/test_compile_profile.py`: **37/37 passed**, 4.754s; no skips.
- Configured an isolated temporary Debug build with `BUILD_TESTING=ON` using
  the installed CMake 4.4.4 and GCC 14.2.0; no shared build directory was changed.
- Actual CTest command: `ctest --test-dir <temporary-build> --output-on-failure
  --no-tests=error -R '^python_test_compile_profile$'`.
  Result: **1/1 CTest entry passed**, 4.16s, executing all 37 Python tests.
- Inspected the new test file: 37 test methods and no trailing whitespace.
- Reported results to agent 08 and the coordinator. No compiler defect emerged.

Only the Python authoring suite was run by this assignment. C++ runtime/engine
qualification belongs to its assigned tests; generic JSON Schema validation and
cross-platform Python/OS execution are not claimed. Link tests skip explicitly
on platforms where the OS cannot create the required alias type; neither skipped
in this Linux run. The physical-acquisition and factory-table gates remain open.
