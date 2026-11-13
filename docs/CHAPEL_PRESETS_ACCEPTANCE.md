# Independent chapel catalog acceptance

The maintained [suite](../tests/test_chapel_presets.py) qualifies the strict
[documentary catalog](CHAPEL_PRESETS_CATALOG.md) through its public compiler,
publication API and actual command-line processes. Its literal eighteen-row
oracle comes from the independently frozen [reading B](research/CHAPEL_PRESETS_SOURCE_B.md)
and its footage/color guide. It does not import producer constants or use the
producer's serializer to construct expected semantic values.

## Required boundary

This catalog preserves the approved chapel arrangement printed on atlas p122:
nine upper and nine lower registrations, ordered C#, D, D#, E, F, F#, G, G#, A.
All 162 tap positions remain explicit digits 0–8 in nine-character strings;
sixteen registrations retain leading zeros. Unpublished registration names stay
null, and primary-document/specimen/loading/latch/percussion unknowns retain
their exact declared status. No Engine, saved control or audio behavior follows
from catalog admission. The [remaining M3 gate](M3_REMAINING_AND_SCANNER_GATE.md)
requires further selector/state/runtime and physical evidence.

## Maintained checks

| Boundary | Independent observable checks |
| --- | --- |
| Source matrix | Both frozen CSV hashes and all eighteen manual/key rows match literal reading-B values. All 162 individual in-range wrong-digit mutations reject. |
| Physical order | All nine one-based positions, footage strings and lead colors match the independent guide. Reordering, duplicate positions and relabeled colors reject. |
| Evidence identity | Exact model/variant, units, source/page/hash, primary-reference status and five limitations. Invented factory names or stronger measurement claims reject. |
| Schema declaration | Every scalar constant, required field, closed object and exact ordered array shape agrees with the independent semantic oracle. |
| JSON admission | Duplicate members at three depths, floats/exponents, Boolean/integer confusion, nonfinite tokens, wrong containers, missing/extra fields, malformed UTF-8/BOM, truncation, trailing data, deep nesting and huge integers. |
| CSV admission | Both input positions independently exercise altered cells, swapped/duplicate/missing/extra rows, field counts, malformed quoting/UTF-8 and semantically equivalent CRLF/quoting that violate frozen raw identity. |
| Determinism | Exact 4,837-byte default catalog and SHA-256; repeat replacement produces identical bytes. Different valid authoring formatting changes only raw identity/byte count while preserving canonical identity and semantics. |
| Bounded files | Valid authoring at exactly 65,536 bytes; rejection at 65,537. Both review inputs reject 16,385 bytes. Missing/directory/symlink/FIFO input leaves fail without blocking. |
| Paths/publication | Unicode/space paths, distinct review files, hardlink aliases, direct and resolved-parent input/output aliases, nonregular outputs, dangling links and missing parents. Rejected CLI operations preserve the complete fixture tree, file bytes and inodes. |
| Atomic failure | Injected create, short-write, flush, fsync and replace failures preserve prior output/inputs and remove the writer's temporary file. Actual filesystem operations surround the injected failing stage. |
| Writer bounds | Wrong text types, empty/oversized/non-UTF-8 payloads and wrong input-list lengths preserve the destination. Valid compiler-returned text remains the writer's documented precondition. |

The schema is inspected structurally; this suite is not an independent general
JSON Schema engine. Duplicate-key/token-syntax/file/review checks belong to the
compiler. JSON Schema's mathematical integer semantics can admit `1.0`; the
compiler deliberately rejects that floating-point spelling.

## Run from the repository root

Python 3.10 or newer suffices for the direct suite. No downloaded library,
native host SDK or SDL dependency is required:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tests/test_chapel_presets.py -v
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_BUILD_VST3=OFF
cmake --build build --target hammond_profile hammond_chapel_catalog
ctest --test-dir build -R '^python_test_chapel_presets$' \
  --no-tests=error --output-on-failure -V
```

Top-level CMake discovers `tests/test_*.py` and supplies the repository context.
Each subprocess has a five-second bound, private temporary paths and explicit
exit/stdout/stderr checks. Tests never mutate repository source fixtures.

## Executed scope and limits

Assignment 36 passed **18 methods, 111 CLI invocations, 234 public-API admission
rejections and five injected publication failures**, with no Linux skips. The
direct run took 6.051 seconds. Its fresh SDK-free CTest run passed 1/1 in 6.39
seconds. Exact source/tool identities and commands are retained in the
[assignment note](development/2026-11-13-next-phases/36-chapel-acceptance.md).

Real Linux symlink, hardlink and FIFO branches executed. Windows/macOS were not
run by this worker; a Windows symlink privilege error is an explicit fixture
skip, and FIFO fixtures require the operating system API. Fault injection does
not establish power-loss durability or safety against hostile concurrent file
mutation. The compiler checks the declared PDF identity, not the PDF bytes as a
fourth input. Independent factory Table IV verification, specimen wiring,
loaded gains, mechanical latches, percussion transitions and physical fidelity
remain open. No production defect or producer change was required by this gate.
