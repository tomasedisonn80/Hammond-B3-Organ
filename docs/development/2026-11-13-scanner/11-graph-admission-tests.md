# Assignment 11 - independent scanner graph admission tests

## Identity and ownership

Actual worker: `/root/w02_a11_graph_admission_tests`, assignment 11 of 60,
wave 2 of the `2026-11-13-scanner` session. Starting commit was
`6dc0702d5473912268e8af8f852b9b9984198ef3`, tree
`a4f1d4b300de236436e22b748b1d4c46ed501ceb`. The scanner additions were uncommitted
shared work; the inspected input hashes below identify the actual tested files.

Owned additions are
[`tests/test_scanner_line_profile.py`](../../../tests/test_scanner_line_profile.py)
and this note. The integrator owns CMake, shared status and publication. This
worker changed no producer, fixture, schema, other test, historical record or
Git state. The schema repair described below was made by the integrator after
this worker reported the defect.

## Independent source basis

Read the standing instructions, current scanner handoff/status/log context,
the graph contract and the compiler's actual implementation. Read atlas p. 157
as extracted text and directly inspected a newly rendered image of p. 158 at
1,700 pixels. The unchanged
[atlas](../../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf) is 21,248,265 bytes,
SHA-256 `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
This is a focused source check, not another full-PDF or primary-paper review.

The test contains all **50 literal signed component records**, including both
printed and independently written SI values, and all **19 literal signed tap
records**. It never calls the compiler's `expected_components` or
`expected_outputs` helpers to obtain its expectations. The table explicitly
places the first six divider branches before their inductors, keeps C18 at
1 nF, and places every output against ground. It also independently fixes the
27-node set, ideal source, open/closed return states, atlas identity and eight
explicit physical unknowns.

## Implemented regression scope

The 19 standard-library unittest methods cover:

- Complete authoring and normalized graph comparison against the literal
  component/output tables; source units and SI conversion; schema enumerations.
- Generated-header numeric arrays and source digest, deterministic output,
  canonical reordering, and deep nonmutation of the authoring record.
- Every one of the six after-inductor divider mutations, every tap incorrectly
  referred to the return, a reversed observation sign, dangling references,
  wrong counts and duplicate identities.
- Duplicate JSON keys, unknown fields at structural boundaries, booleans and
  floating tokens substituted for metadata, nonfinite/nonpositive values,
  wrong prefixes, false provenance, altered switch state, and fabricated
  values for physical unknowns.
- Byte, string, recursion/depth and value-count bounds, cyclic in-memory input,
  malformed UTF-8/JSON, and a simulated file-identity change during reading.
- Successful CLI publication of both formats, prior-output preservation after
  rejected inputs, input aliases and nonregular destinations, and injected
  flush/replace failures with temporary-file cleanup.
- Actual same-filesystem hardlink protection, plus POSIX-scoped output symlink
  and nonblocking FIFO rejection. Windows does not execute the POSIX-only
  branches; no Windows-specific filesystem qualification is claimed here.

The suite does not depend on `jsonschema`, a compiler executable, a native
runtime build or a host SDK. Its schema checks compare literal graph
enumerations and required identity cardinalities directly. Full JSON Schema
validation was separately executed below using the already available library.

## Defect found and verified repair

The original schema used `uniqueItems` for the three editable assumptions and
eight physical unknowns. Whole-object uniqueness did not require distinct IDs:
copying one record over another and changing its nonempty description/reason
produced two different objects with the same ID. The actual Draft 2020-12
validator admitted both malformed profiles. The Python compiler correctly
rejected them, so this was a schema/compiler contract mismatch, not a runtime
admission bypass.

Reported both reproductions to the integrator and producer. The integrator
added a `contains` cardinality clause for every required ID, with
`minContains = maxContains = 1`. Independent revalidation then rejected both
changed-prose duplicate cases, with two schema errors apiece. The correct
fixture and a fixture with reordered arrays remained valid. One dedicated
test now retains the required schema-ID constraints, and another preserves
the actual duplicate-prose compiler regression.

## Actual commands and results

Working directory: `/workspace/scratch/1742da7072be/Hammond-B3-Organ`.
Execution was local Linux x86-64 with Python 3.12.14.

```sh
pdftotext -f 157 -l 157 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftoppm -f 158 -l 158 -singlefile -scale-to 1700 -png \
  Hammond_B3_Leslie_Research_Atlas_500pp.pdf \
  /workspace/scratch/1742da7072be/a11-review/atlas158
python3 -B tests/test_scanner_line_profile.py
/workspace/scratch/1742da7072be/build-tools/bin/python -B tests/test_scanner_line_profile.py
git diff --check
```

The initial 18-method suite passed before the schema-cardinality regression
method was added. The 19-method suite passed in 6.325 seconds using the primary Python environment
and again in 7.186 seconds using the clean build environment. The final refinement
compares admitted authoring/schema records without imposing irrelevant array order;
all **19/19 methods passed again** in both environments afterward. `importlib.util.find_spec("jsonschema")` was **None** in
that second environment, confirming that the maintained suite has no hidden
schema-library dependency. There were no unittest failures or skips.

A separate inline Python check used jsonschema 4.26.0 and `jsonschema.Draft202012Validator` to check
the repaired schema itself, accept the original/reordered fixtures and reject
both changed-prose duplicate-ID mutations. Owned-file whitespace and repository
`git diff --check` passed. The temporary PDF image remains outside the repo.

| Tested input | SHA-256 |
| --- | --- |
| Authoring fixture | `1d236be5e6b63e938a9f147808386173949d167e09aee8e902c55002e4ea4604` |
| Repaired schema | `602d3b75f316d0c0523c1ecab49204607785ce8f83508a3e0014d22793221f29` |
| Compiler | `56c60cf511144d552fdeb2708711b32469f350593b391c7619ebb92b41b6dd7e` |
| Test file | `6026225d5f4150446fc63b5442c8aaf911eea3c1ef25d141df829dd977fa5dca` |

These checks establish independently tested graph admission and publication
behavior for the named ideal fixture. They do not establish a physical specimen
match, independent AC/transient agreement, scanner runtime/rotor behavior,
native host operation or a complete M4 pass. Those remain separately owned
gates. No commit or push was performed by this assignment.
