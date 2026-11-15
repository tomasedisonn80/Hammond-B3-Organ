# Product continuation sanitizer coverage — A37

**The focused native sanitizer job now requires 21 gates, preserving its previous
16 and adding five product gates. Source wiring and checker behavior are
verified; execution of this expanded hosted selection remains pending.**

Actual assignment: `/root/w07_a37_sanitizer_ci_coverage`, wave 7 of the
[product continuation](../development/2026-11-15-product-continuation/CHECKPOINT.md).
The reviewed base is `b9d352a82ac1afdec70c76ec5b1987785a37762e`, tree
`b3b8b68e4c1f8312d46962924b5096f4ea10c4d2`, with the working changes below.

| Reviewed input | SHA-256 |
| --- | --- |
| [Standalone workflow](../../.github/workflows/standalone.yml) | `8049819e4383dfa13e28622678a7d457e6d1165198ca4b6579173b4c174b1d59` |
| [Standalone CMake](../../apps/standalone/CMakeLists.txt), including the integrator's concurrent MinGW probe link option | `772f75acd307d955cd632afc01ec7c5221859aa997aa97bd4d108a69deafc94c` |

A37 owns the workflow, this review, its assignment note, and only the five-line
sanitizer timeout addition in CMake. The fixture portability repairs and MinGW
link option have separate integration ownership. Probe identities are read from
the actual build, allowing that reviewed fixture repair to retain the same
strict coverage contract.

## Selection and the executable boundary

The old native selection listed sixteen C++ executables and assumed their build
target names equaled their CTest names. Those sixteen remain:

```text
test_standalone_ui                    test_standalone_preset_ui
test_standalone_workspaces_author     test_standalone_workspace_acceptance
test_standalone_projection            test_standalone_inspection_author
test_standalone_inspection_acceptance test_standalone_workspace_continuity
test_standalone_drawing               test_standalone_quad_drawing
test_standalone_workspace_raster      test_standalone_scaled_view
test_standalone_preset_raster         test_standalone_reference_layout
test_standalone_inspection_raster     test_standalone_material_acceptance
```

The explicit `HAMMOND_SANITIZER_TEST_TARGETS` map adds:

| CTest name | Build target | Source-checked coverage |
| --- | --- | --- |
| `test_standalone_channel_modes` | Same name | Scoped CC120 ownership, other-owner continuity, percussion and typed admission. |
| `test_standalone_expression_calibration` | Same name | CC11 endpoint/inversion boundaries, immutable epochs, pending controls and CC121 reset. |
| `test_standalone_channel_acceptance` | Same name | FIFO capacity, overflow recovery, rejected scopes, continuity and CC121 across partial acknowledgments. |
| `test_standalone_product_visual` | Same name | Current native paint, legends, caps, clipping, focus, pending-route feedback and inventory assertions. The ordinary target does not link the historical comparison painter. |
| `test_standalone_native_calibration` | `hammond_standalone_calibration_probe` | Python acceptance around the real native application, substituted RtMidi dependency, real SDL dummy callbacks and native reconnect/epoch observations. |

The calibration driver includes unchanged `main.cpp` in its instrumented
translation unit and compiles `MidiDevice.cpp` with `HAMMOND_HAS_RTMIDI=1`.
Its test-only RtMidi include directory precedes the ordinary standalone include
directory. The shipped backend remains configured OFF for this sanitizer job.
This checks the application path with deterministic synchronous dependency
offers; physical devices and asynchronous driver races require separate work.

Provenance stores the 21 unique test-to-target pairs and the derived build list.
Only those 21 executable inputs and their dependencies are requested, using two
build workers. Exact anchored CTest discovery must find all 21 names, with built
commands, no disabled test, and the expected timeout properties. Direct commands
must resolve to their mapped binary. The Python command must use `cmake -E env`,
the exact built probe assignment, an existing interpreter and the expected script.
The suite runs serially with `--no-tests=error`.

The four ordinary Release matrix rows retain their existing all-standalone
execution. Their required-presence set grows from 24 to 31, adding the five
gates above plus `test_standalone_expression_diagnostics` and
`test_standalone_waveform_material`. All other Release steps remain unchanged.

## Instrumentation and retained evidence

The existing C++ sanitizer helper and explicit SDL C flags remain:
`-fsanitize=address,undefined -fno-omit-frame-pointer`. The job checks every
selected compile command and nonempty object, and now verifies the actual new
source groups, including the driver, `MidiDevice.cpp`, `InstrumentView.cpp`,
`Session.cpp`, `MidiInput.cpp`, `AudioDevice.cpp` and `ScriptedInput.cpp`.

Six archives must contain both ASan and UBSan references: SDL2, core, standalone
support, drawing, audio and replay. The last two are newly required because the
native probe links them. Every selected executable must have the sanitizer link
option and both dynamic runtimes. The probe link command must name all six
archives. System libraries are not rebuilt.

Artifacts retain compile commands, source/object inventory, archive and binary
hashes, link commands, runtime reports, discovery JSON, verbose CTest/JUnit and
native calibration evidence. Successful calibration acceptance must report
**10 subprocesses, seven complete named lifecycle scenarios and two deliberately
failed application replays**, with the same probe hash as instrumentation.
Both deliberate replay failures return application status 1. An additional
check rejects ASan, UBSan, LSan or `runtime error:` text in every retained native
scenario's stderr, preventing that expected application status from masking a
sanitizer failure after diagnostics were written.

The job environment remains `ASAN_OPTIONS=detect_leaks=1:halt_on_error=1`,
`UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1`, and `LSAN_OPTIONS=exitcode=23`.
Discovery rejects sanitizer overrides in CTest environment properties,
environment modifications and command arguments. No new override, suppression
or exception was added. The existing named
`test_standalone_midi_backend_quarantine` exception remains outside this
21-test selection and unchanged in CMake. The separate core sanitizer job still
builds and runs its registered tests, including the globbed crossover tests;
this change does not replace that gate.

## Bounded time and verification

| Gate | Ordinary CTest limit | Sanitizer CTest limit |
| --- | ---: | ---: |
| Product visual | 90 s | Existing 240 s, preserved |
| Native calibration | 90 s | 180 s, added with integrator approval |
| Workspace / scaled / preset raster | 60 / 60 / 30 s | Existing 180 / 360 / 300 s, preserved |

The native calibration suite retains its 15-second limit for each of ten
subprocesses. The 180-second total permits that bounded aggregate plus harness
overhead. The product visual allowance remains a memory-checking budget; it
does not establish rendering performance. The job's 20-minute ceiling is
unchanged. A timeout or sanitizer diagnostic remains a failure.

A37 performed the following bounded checks from
`/workspace/scratch/5b7d983ac078/Hammond-B3-Organ`:

- Parsed all three workflow YAMLs; `bash -n` accepted all 42 run blocks, and
  Python AST/compilation accepted all 13 embedded Python blocks.
- Compared the working workflow with `git show HEAD:.github/workflows/standalone.yml`:
  all sixteen earlier gates, sanitizer environment, job ceiling, Release matrix
  and unaffected Release steps are retained.
- Queried the integrator's existing Release build with CTest `--show-only=json-v1`
  and `--no-tests=error`. Its 48 standalone registrations contain all 31 required
  names; all 21 selected commands map correctly to existing binaries.
- Read existing Release compile commands and objects: 240 translation units in
  the selected executable/dependency set are present, all eight specifically
  required source groups match, the probe's define/include ordering matches,
  and all six archive paths exist. These Release objects do not establish
  sanitizer instrumentation or runtime success.
- Executed the exact final summary-check block against the retained
  [A26 Release summary](../development/2026-11-15-product-continuation/reports/A26-root-native-calibration.json)
  and its original stderr. It accepted that record and rejected six independent
  mutations: wrong failure count, wrong binary hash, missing scenario, and ASan,
  UBSan or LSan diagnostics appended after an expected application error.
  This validates checker behavior; no application was executed by these checks.

The exact read-only inventory command was:

```sh
/workspace/scratch/1bb6ee17ad7e/build-tools/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/5b7d983ac078/build-native -C Release \
  --show-only=json-v1 --no-tests=error -R '^test_standalone_'
```

A38's independent review caught the initial draft's incorrect single-failure
summary expectation. The final guard requires the two failures present in both
the fixture source and retained A26 evidence.

## Hosted acceptance still required

The [ff41 hosted status receipt](../development/2026-11-15-product-continuation/reports/implementation-hosted-status.json)
qualifies that earlier revision's job statuses. Its native sanitizer selection
contained sixteen gates. Neither it nor the previous-selection b9 runs execute
this expanded job. Existing b9 failures and the separately reviewed fixture
repairs retain their own evidence.

Local leak-enabled execution and the independent empty-main control were already
[blocked by ptrace](../development/2026-11-15-product-continuation/reports/A25-local-sanitizer-blocked.txt),
with the [control result retained](../development/2026-11-15-product-continuation/reports/A25-local-sanitizer-control.txt).
A37 did not repeat those controls, disable leaks, configure or build a sanitizer
tree, or claim a local sanitizer pass.

After publication, audit the exact revision's native sanitizer artifact: all
instrumentation checks, 21/21 leak-enabled CTest results, retained seven-scenario
calibration summary and clean captured sanitizer diagnostics must pass. Preserve
the actual commit/tree, job ID and original failures. Until that observation,
the expanded hosted gate is **pending**.
