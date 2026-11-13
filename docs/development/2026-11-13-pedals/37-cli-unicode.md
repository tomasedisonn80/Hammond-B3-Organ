# Assignment 37 — shared offline CLI Unicode boundary

## Ownership and starting point

- Wave: **7 of 10**; assignment: **37 of 60**.
- Actual agent: `/root/w07_a37_cli_unicode`.
- Starting published commit: `88c36b4a72a07f6498f73279f25023278accd350`.
- Read the root agent instructions/current handoff and
  [`PEDAL_WINDOWS_UNICODE.md`](../../reviews/PEDAL_WINDOWS_UNICODE.md) before editing.
- The parent had staged W6 native CMake changes. This worker changed only its
  assigned working-tree CLI CMake hunks and did not stage, commit, push, spawn
  another agent, or edit shared status/assignment files.

The parent dispatch UI initially reported this spawn as aborted, but this actual
canonical child was active, informed the parent, and performed the work below.
No replacement worker was requested or counted by this child.

## Implemented

Added private offline helper [`tools/CliArguments.h`](../../../tools/CliArguments.h)
and applied its strict Windows argument entry to `hammond_render`,
`hammond_benchmark`, `hammond_model_info`, `hammond_parameter_info`,
`hammond_console_trace`, and `hammond_pedal_trace`.

The helper reuses the renderer's measured and checked
`WideCharToMultiByte(CP_UTF8, WC_ERR_INVALID_CHARS, ...)` conversion. Converted
string ownership lasts through the original tool body. Path-valued flags use
explicit `char8_t` UTF-8 filesystem construction on Windows; POSIX entry/path
bytes are unchanged. The renderer's path diagnostic now emits the missing path
as UTF-8 on Windows. Its entry-level argument bounds and exact compatible
`invalid Unicode or oversized (maximum 4096 UTF-8 bytes)` wording are retained.
Other tools keep their existing parsers, byte/count/range limits and diagnostics.

Root CMake changes are limited to the six-tool MinGW `-municode` loop and the
missing benchmark/model/parameter executable environments and build dependencies
for the new Python suite. Existing renderer/trace environments, Threads linkage,
native hooks and the install tail were preserved. Assignment 38 owns the new
install module; the integrator can apply that separate hook after this freeze.

The parameter metadata schema, 45 records and IDs, binary stdout mode, help text
and normalized grammar were not changed. A separate later assignment may clarify
its SDK-free scope wording. No SDK, realtime code, signal computation, profile
format, collision check, temporary ownership or publication algorithm changed.

The user/developer contract and reproduction commands are in
[`CLI_UNICODE.md`](../../CLI_UNICODE.md). The new actual-executable test is
[`test_cli_unicode.py`](../../../tests/test_cli_unicode.py).

## Coherent frozen verification

The build used an isolated archive of the starting commit at
`/workspace/scratch/f364bc93d920/cli-unicode-a37/source`. The seven owned C++/header
files and new Python test were copied into that archive. Only this assignment's
two CLI CMake changes were projected onto the base CMake file; the concurrently
staged native W6 hooks were excluded from this scoped build. All six consumers
and their core were compiled together from that single tree. No live headers
were combined with a previously built core.

Observed tools: Linux x86-64, GCC 14.2.0, CMake/CTest 3.31.6, Python 3.12.14,
Release, project sanitizers off. The actual CMake executable was
`/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake` (CTest alongside it).

Commands, with `SOURCE` and `BUILD` denoting that frozen source and its sibling
`build` directory:

```sh
cmake -S "$SOURCE" -B "$BUILD" -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON -DHAMMOND_ENABLE_SANITIZERS=OFF
cmake --build "$BUILD" --parallel 3 --target hammond_render hammond_benchmark hammond_model_info hammond_parameter_info hammond_console_trace hammond_pedal_trace
ctest --test-dir "$BUILD" -R '^python_test_cli_unicode$' --output-on-failure --no-tests=error -V
ctest --test-dir "$BUILD" -R '^python_test_(cli_unicode|render|pedal_render_cli|console_trace|pedal_trace|console_benchmark|model_info|parameter_bridge)$' --output-on-failure --no-tests=error -V -j 3
```

### Actual failure and correction

The first Unicode suite run failed **one of 11 test methods** because the newly
written CSV row-count assertion counted 28 comment metadata lines together with
the header and 5292 data rows: observed 5321 lines versus an incorrect expected
5293. This was a test expectation error, not a tool failure. The correction counts
only lines without the format's `# ` metadata prefix for the row assertion.
The complete CSV, including all metadata, still must match the ASCII-path
reference byte for byte. No production change or weakened byte comparison was
used to resolve it. The failed run executed 76 actual subprocess invocations and
is retained as `unicode-first.log` in the verification directory.

### Final results

All six executables built successfully under the repository's strict warning
configuration. The final focused run passed **8/8 CTest suites, 114 Python test
methods**, with no skips, in 11.11 seconds on this machine.

| Suite | Passed test methods | Additional observed execution evidence |
| --- | ---: | --- |
| `python_test_cli_unicode` | 11 | 81 actual invocations across all six tools |
| `python_test_render` | 35 | Full existing renderer suite, including argument bounds and output preservation |
| `python_test_pedal_render_cli` | 19 | 364 actual renderer invocations; existing Unicode tests retained |
| `python_test_console_benchmark` | 6 | 33 CLI calls; no timing threshold |
| `python_test_console_trace` | 10 | 62 CLI calls; 67,716 independently checked rows |
| `python_test_pedal_trace` | 13 | 65 CLI calls; 79,236 independently checked rows; three symlink cases exercised |
| `python_test_model_info` | 10 | Existing metadata and rejection checks |
| `python_test_parameter_bridge` | 10 | 98 actual diagnostic CLI calls |

New-suite invocation counts: renderer **19**, benchmark **14**, model information
**5**, parameter information **13**, console trace **15**, pedal trace **15**.
The new suite checked accented/CJK/supplementary Unicode executable, cwd and file
names; absolute and relative arguments; exact WAV/CSV/metadata/help bytes against
ASCII-path runs; all benchmark fields except the three timing fields; strict
full-width numeric/sign/option/enum rejection; UTF-8 byte limits; renderer missing
path spelling; existing output preservation; and one complete reference output
from two competing publishers, with no extra files or modified inputs.

`git diff --check` on owned tracked changes passed. At freeze, each working code
and test file still matched the corresponding built snapshot hash below.

## Frozen inputs and logs

Hashes are SHA-256. The working CMake includes the parent's already-staged W6
native additions; the tested projected CMake intentionally does not. Their
different hashes do not represent a code/header mixture in the test build.

| File | SHA-256 |
| --- | --- |
| `tools/CliArguments.h` | `8ac5d91ebf66c31456159f028bce3c1c4b0dcd0c09118ac8c8d55c53a8912a47` |
| `tools/render.cpp` | `d84366dcb47f250569a67c8c8aa2fdfeba1b9c1abdc56819038a554b6a030cde` |
| `tools/benchmark.cpp` | `a5682a789db22b1b6f978e4a87c1ac11a8c458a67286b30aac90fc26949ea00d` |
| `tools/model_info.cpp` | `be01d2a5a2d4b938fa90eb92909e6a84b4617c693112e927f448ba6dbaac6f44` |
| `tools/parameter_info.cpp` | `9d29cdae650899a25c6cf6da3b4df6d8341729cd68d1525ed96e51ecde1bc91b` |
| `tools/console_trace.cpp` | `5d709c208c4e93cf3eaafc77dea68772da803e7f7c40c788cab917387b10af4d` |
| `tools/pedal_trace.cpp` | `2130ba1c79a6f417305f55181c280cde70c98f8b69bd1a05a340ee243d3db01a` |
| `tests/test_cli_unicode.py` | `ece7e2a5498d7d8050bb8989fe1a3aca123f338efd2b6a716f37e540e3f576db` |
| Working `CMakeLists.txt` at freeze | `47db428553191f62e586d70d9a7b2e88485640da4c1facc1d7ff751821b5876e` |
| Base-plus-CLI projected `CMakeLists.txt` | `1d525161abdc166e6377cca2cca9ffeb9affaedd438202b01cfd39666a7e8eca` |
| CLI-only CMake unstaged diff at freeze | `975799bbd0f12f87d58f282cfbc2f7ecd705a84888fd8a2dc44441f9a9074f56` |
| `docs/CLI_UNICODE.md` | `4803a9ce06a9cd84e84b0a1c51651076eb6121468ef51b2e091163990006c820` |
| `build.log` | `0b168e86041897998c71b59dfe1606c6def9ea5fc41c2b50da36f0c1f2cd3102` |
| `unicode-first.log` | `7df341c2929849e44f6db63f871e64ec92746865b574edb14548ede0be3a6ce0` |
| `focused-final.log` | `94bf5078031091baf07ce5ac3442675e33fe2faf20329aa8280dbdf75df49402` |

The three logs and `snapshot.json` are under
`/workspace/scratch/f364bc93d920/cli-unicode-a37/`. This note retains the results,
failure explanation, reproduction commands and hashes in the repository.

## Handoff and next gate

**Frozen for root integration; not independently committed or pushed.** The
integrator owns combining concurrent work, full-tree verification, shared status,
the real commit/push and hosted CI reconciliation. The new CTest suite discovers
all six tools and participates in the normal `check` dependency graph.

Required next evidence is native Windows CI against the integrated commit,
including the new Unicode suite and existing renderer Unicode/oversized tests.
This Linux run did **not** execute `wmain`, `WideCharToMultiByte`, Windows filesystem
conversion or MinGW startup linkage. Invalid UTF-16 rejection is enforced by
strict conversion flags but was not executed here; the portable tests do not
pretend that an embedded NUL can be passed inside an OS argument. Unicode
build-directory literals, SDK/DAW paths, GUI hosts, hardware fidelity and measured
organ behavior remain outside this assignment's claim.
