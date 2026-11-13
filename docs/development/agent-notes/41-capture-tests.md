# Agent 41 — independent capture-contract tests

Assignment: independently verify Agent 40's original proposed v1 capture contract.
Owned files: `tests/test_capture.py`, `docs/CAPTURE_VALIDATION.md`, and this note.
No producer, shared-status, commit or push ownership.

Read `AGENTS.md`, README, status, next steps, latest development log, plan, atlas
review and atlas chapters 57–58 (PDF pp. 349–360). The source distinguishes
metadata, retained byte integrity, physical evidence and actual rights clearance.
The absent atlas companion validator and its printed results are not inherited.

Implemented 39 standard-library test methods in `tests/test_capture.py`.
Fixture expectations come from `docs/CAPTURE_FORMAT.md`; schema root/definition
keys were inspected independently. No producer validation helper computes expected
validity or hashes. Temporary byte artifacts are generated four-byte synthetic
floating-point scalars. A hypothetical recorded-hardware API argument with unknown
specimen/calibration is never serialized and has no associated artifact. No
measured instrument record, accepted calibrated hardware fixture or acquisition
evidence is produced.

Coverage: planned/recorded/synthetic admission, every required/unknown object key,
exact types and Boolean-number rejection, finite/range/identity/text bounds,
known/unknown consistency, real UTC calendar checks, channel order and boundary
units, calibration state separation, file/parent limits, unique IDs/casefolded
paths, DAGs/raw ancestry, manifest-wide partition inheritance, strict UTF-8 JSON,
duplicates/nonfinite/deep/wide/oversized input, nonmutation, CLI status/reporting,
explicit byte size/hash checks, missing/nonregular files, symlink roots/components
and hardlink aliases. Default validation accepts absent artifacts.

Executed locally on 2026-11-13 with Linux and Python 3.12.14:

```sh
python tests/test_capture.py -v
```

Final observed result: **39 methods passed, 0.816 s**, no skips.
Native CMake configured an isolated Release tree successfully:

```sh
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  -S . -B /workspace/scratch/c871510c69b2/agent41-capture-build -DCMAKE_BUILD_TYPE=Release
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/c871510c69b2/agent41-capture-build \
  -R '^python_test_capture$' --output-on-failure
```

Final selected CTest result: **1/1 passed, 1.02 s**. No unrelated C++/render suite
was built or rerun. No external dependency, silent skip, producer failure or
producer edit was introduced by this assignment. Agent 40 independently hardened
portable path traversal; the final narrow runs include that implementation.

`docs/CAPTURE_VALIDATION.md` records usage, fixture design and evidence limits.
This is structural and retained-byte integrity evidence only. Header/content
checks, cross-manifest lineage/split audits, acquisition authenticity, actual
calibration, permissions, physical fidelity and macOS/Windows qualification remain
separate gates. Shared status files and commit/push remain the integrator's scope.
