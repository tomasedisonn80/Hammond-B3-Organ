# Capture validation: evidence and limits

The capture validator checks the project's proposed metadata contract and, when
explicitly requested, the identity of retained artifact bytes. It does not acquire
an instrument, authenticate a recording or establish physical fidelity. The atlas
describes these as separate gates (PDF pp. 349–360); its referenced companion
schema and validator were not supplied with this repository.

## Two explicit operations

```sh
python tools/validate_capture.py --input data/capture-planned-example.json
python tools/validate_capture.py --input /path/to/capture.json \
  --check-files --artifact-root /path/to/artifacts
```

The first operation validates metadata without reading artifact paths. A planned
manifest can therefore be reviewed before files exist. A recorded manifest can
also receive a structural check independently of artifact availability.

The second operation is only for a recorded manifest. It checks files under the
declared artifact root and compares their byte sizes and SHA-256 digests with the
manifest. Failure must not be reported as a successful verification.

| Result | What it supports | What remains unresolved |
|---|---|---|
| Structure accepted | Required metadata, types and declared relationships satisfy this contract | Accuracy or completeness of the declarations |
| Artifact bytes accepted | Accessible files match their declared sizes and hashes during this check | Originality, acquisition provenance or later immutability |
| Synthetic fixture accepted | The software handles a deliberately generated test case | Any measurement of a B-3, AO-28 or Leslie |

Neither operation resolves the authority behind a permission declaration, proves
an independent holdout across a corpus, checks a real electrical boundary, nor
qualifies the clock or acquisition chain. A hash is an integrity comparison, not
an authenticity certificate. Unknown specimen or calibration fields must retain
their explicit reasons instead of becoming zero, unity gain or an inferred value.

## Independent regression suite

Run the standalone standard-library suite from the repository root:

```sh
python tests/test_capture.py -v
```

CMake discovers `tests/test_*.py`; after configuring the project, the registered
suite can also be selected with:

```sh
ctest --test-dir build -R '^python_test_capture$' --output-on-failure
```

The tests construct their own manifests from the
[published contract](CAPTURE_FORMAT.md). They do not ask the producer's private
helpers to calculate expected validity, identities or digests. Temporary artifact
payloads are explicitly synthetic. One hypothetical
in-memory hardware declaration checks admission with unknown specimen/calibration;
it is never serialized or accompanied by a file. No actual hardware recording is
required, generated or shipped by this suite.

The suite exercises planned and recorded states, exact object keys, explicit
unknowns, numeric domains, UTC timestamps, local ancestry, partition inheritance,
strict bounded JSON parsing, path confinement and opt-in byte checking. CLI tests
check both useful errors and the distinction between structure and byte checks.
Acceptance and rejection checks also protect the caller's metadata from mutation.

## Observed local results

On 2026-11-13, the standalone suite passed **39 test methods** under Linux with
Python 3.12.14. An isolated native CMake Release configuration discovered the suite,
and the selected `python_test_capture` CTest gate passed **1/1**. This assignment
did not build or rerun unrelated C++/render suites and did not qualify macOS or
Windows. No tests were skipped and no runtime dependencies were added.

Root's integration review then reproduced a missing-identity gap: when descriptor
metadata returned a zero file ID, two real hardlinked paths could pass the alias
check. File verification now falls back to a usable path identity and rejects if
neither API supplies one. Two deterministic regressions cover independent copies,
real aliases and unavailable identities. The expanded **41-method suite passed**
locally without skips. This simulation does not claim a particular hosted Windows
filesystem returned zero IDs; full platform qualification remains a separate run.

The subsequent [hosted integration at 6c3dd8b](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43365901429)
passed this 41-method suite on Linux, macOS and Windows Release and in the Linux
ASan/UBSan/leak job. The capture checker is Python software, so the latter result
does not mean that the Python interpreter was sanitizer-instrumented.

## Interpretation of results

Passing tests establish only the exercised software behavior. They do not recover
the absent atlas companion files or inherit the atlas's printed historical test
results (PDF p. 360). A corpus-level cross-manifest lineage checker, actual signal
header/content validation, acquisition calibration and rights review require
separate evidence. See the [capture-format contract](CAPTURE_FORMAT.md) for the
exact v1 boundary. The test suite exercises the rejection of calibration claims on
planned/synthetic records; it supplies no accepted calibrated hardware fixture.

Executed commands and observed results for this assignment are retained in
[agent note 41](development/agent-notes/41-capture-tests.md). Hosted platforms and
other environments must be qualified by their own observed runs.
