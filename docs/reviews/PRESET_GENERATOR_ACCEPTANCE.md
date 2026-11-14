# Independent fixed-data generation boundary

A32 (`/root/w06_a32_generator_boundary`) found and repaired one reproducible
source-cache defect in the fixed-registration generator. The admitted catalog,
both readings, C++ runtime and generated header bytes are unchanged. This is an
offline generation/build result, not another musical or physical-fidelity gate.

## Observed defect and bounded repair

`compile_fixed_registrations.py` originally imported the adjacent strict chapel
compiler normally. After that import creates a timestamp `.pyc`, Python can
reuse its older code when the source changes size-preservingly within the same
integer second. CMake can notice the newer nanosecond timestamp and rerun the
generator while Python still executes the older admission rules.

The isolated reproduction first built the correct header. It then changed the
strict compiler's last expected row from `427866244` to `427866243`, preserving
source size and setting newer quarter/three-quarter timestamps in the same
verified integer second. The authoring inputs stayed unchanged. The actual CMake
build incorrectly returned **0** and ran its dependent consumer. Removing only
the cached bytecode made the identical changed-source build return **2** and
reject the mismatching authoring row. The previous valid header survived that
rejection. The [original result](../development/2026-11-14-preset-continuation/reports/a32-cache-result.json)
and [transcript](../development/2026-11-14-preset-continuation/reports/a32-cache-same-second-stale.txt)
retain this observed difference.

The repaired generator reads the adjacent strict compiler's source once,
compiles those bytes, and executes them in a private module namespace. It neither
reads nor deletes a local compiler bytecode cache. The strict compiler imports
only Python standard-library modules; there is no repository-local transitive
import left outside this source-loading boundary. Normal admission, exception
aliasing within the generator, atomic publication and CLI behavior are retained.
No CMake production rule or strict-compiler source was changed.

This is a developer source-freshness guarantee for the adjacent dependency. It
does not make arbitrary repository code safe, promise hostile filesystem-race
protection, or turn source hashes into an independent physical source.

## Focused regression

[`test_fixed_registration_source_admission.py`](../../tests/test_fixed_registration_source_admission.py)
creates caches using Python's public compiler API. A separate ordinary-import
process first proves that each cache actually supplies the old rule. The real
fixed-data CLI must then follow current source in both directions:

| Cached rule / current source | Required result |
|---|---|
| Valid old rule / currently mismatching rule | Reject the catalog and preserve the existing output. |
| Mismatching old rule / currently valid rule | Generate the original exact header. |

Both directions run with **timestamp** and **unchecked-hash** bytecode, for four
cases and eight actual subprocesses. Against the original frozen generator, the
new test reports **four failed subcases**; against the repair it passes **1/1
method in 0.477 seconds**. The original failure is retained in the
[before-repair log](../development/2026-11-14-preset-continuation/reports/a32-regression-before.txt).
The existing fixed-generator suite also passes **17/17 methods in 2.287 seconds**,
including source admission, aliases and atomic failure cleanup. These are the
affected tests; no complete runtime suite was repeated by A32.

## Actual CMake dependency gate

A fresh small CMake project includes the actual copied
`CompileFixedRegistrations.cmake`. Its dependent `hammond_core` test target writes
a marker; it does not substitute another generator or compile a C++ consumer.
The gate ran **25 configure/build commands**, including **eight expected
rejections**. It verified:

- A clean build creates the original header; a no-change build leaves its
  timestamp untouched.
- Changes to all six declared dependencies trigger generation: the fixed and
  strict compiler sources, schema, authoring JSON and both readings.
- Mutating or removing each of the three admitted data inputs blocks the
  dependent target. Aliasing the two reading paths is also rejected.
- The demonstrated stale-helper cache now blocks the dependent target when the
  current compiler source rejects the unchanged catalog.
- Every rejected build preserves the old header, leaves no temporary output and
  prevents the consumer marker. Restoring valid inputs permits the build again.

The schema is a declared rebuild dependency; the strict compiler's exact
in-code specification remains the actual admission logic. The gate does not
misdescribe whitespace-only schema changes as a new admitted model.

The [structured gate](../development/2026-11-14-preset-continuation/reports/a32-boundary-result.json)
and [ordered transcripts](../development/2026-11-14-preset-continuation/reports/a32-cmake-transcript.txt)
contain every actual command and result. The
[assignment record](../development/2026-11-14-preset-continuation/32-generator-boundary.md)
identifies the copied inputs and reproduction script.

## Integration identity and remaining limits

The repaired valid output contains **2,099 bytes** and is byte-for-byte identical
to A31's untouched frozen combined-build header:
`66cbb1a23cb5ebf14844afd6f98e13829c9f69c1511b09d5974ca5a4527157c6`.
This equality was actually checked; it is not inferred from matching row counts.
A31's original runtime qualification therefore retains its own source identity,
with this independently qualified generation change recorded as a delta.

This gate used Linux, Python 3.12.14, CMake 4.4.4 and Unix Makefiles. Windows/macOS,
other Python implementations and other build generators retain their actual
platform gates. The automatic Python-test glob discovers the new regression.
No historical catalog, CSV, source PDF, fixture, baseline build, A31 source/build
or other worker's files were changed. Factory Table IV, specimen wiring, physical
latches and loaded gains remain separate evidence requirements.
