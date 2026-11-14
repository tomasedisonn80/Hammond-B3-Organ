# R4 build, test, install and CI integration plan

A12 integration review, 14 November 2026. This is a concrete change plan for
the integrator, not an implemented CMake change or an R4 acceptance result.
The inspected committed source is `26ff2fbe66a50260bd7601cbfa54c1f5d35ff3a8`;
the new renderer headers, streaming path and independent reference were an
uncommitted overlay. The [renderer contract](ROTARY_RENDERER_CONTRACT.md),
[independent acceptance](ROTARY_WAVEFORM_ACCEPTANCE.md) and
[session checkpoint](development/2026-11-14-waveform-continuation/CHECKPOINT.md)
own the interfaces, numerical budgets and actual execution status.

The required integration fits the existing C++20 core and Python standard
library. It adds no SDK, package, audio route, parameter, saved-state field or
runtime dependency. Preserve the default dry Engine, all 47 parameter
identities, `B3CONTROLS4` and readers 1–3. R4, R5, R6 and physical M7 remain
separate claims.

## 1. Existing behavior and exact additions

The root [CMakeLists.txt](../CMakeLists.txt) uses `CONFIGURE_DEPENDS` globs for
`src/*.cpp`, `tests/test_*.cpp` and `tests/test_*.py`. New production sources and
ordinary behavioral tests therefore enter existing targets after configuration.
There is no hand-maintained core source list to extend. Native probe files under
`tests/probes/` and command-line files under `tools/` require explicit targets.

| Source or interface | Target and integration action |
| --- | --- |
| `src/RotaryHistory.cpp`, `src/RotaryStreamingPath.cpp`, `src/RotaryRenderer.cpp` | Discovered into `hammond_core`; keep the existing `hammond_configure_target(hammond_core)` policy. Reconfigure and build a real consumer after all three implementations are present. |
| `include/hammond/RotaryHistory.h`, `include/hammond/RotaryRenderer.h` | Existing public include directory already exposes them. No new installed SDK/header package exists or is needed for R4. |
| `src/RotaryRendererInternal.h` | Private implementation and dedicated rollback-test input. Do not add `src/` to the public core include interface. A designated accessor test may use a target-private include directory or its explicit relative include. |
| `tests/test_rotary_history.cpp`, `tests/test_rotary_history_acceptance.cpp`, `tests/test_rotary_renderer_*.cpp` | Ordinary test glob creates executable/CTest names matching the stems, links `hammond_core`, includes `tests/`, applies strict flags and adds them to `check`. Do not explicitly create duplicate targets. |
| `tests/probes/rotary_waveform_probe.cpp` with `tests/reference/rotary_waveform_reference.h` | Add explicit `hammond_rotary_waveform_probe` inside `BUILD_TESTING`, link only `hammond_core`, add the private `tests/` include directory, configure the target and append it to `HAMMOND_TEST_TARGETS`. |
| Proposed `tests/test_rotary_waveform_acceptance.py` | The Python glob registers `python_test_rotary_waveform_acceptance`. Supply the exact probe path through a generator expression. Its ordinary invocation must clearly identify the bounded smoke; full qualification has a separate invocation below. |
| Planned A25 `tools/rotary_render.cpp` | Add explicit `hammond_rotary_render` outside `BUILD_TESTING`, linked to `hammond_core`, after its independent CLI/input/output contract is reviewed. Do not make it depend on the organ `nominal.b3p` unless that contract actually requires the file. |

Adding only the streaming path can still leave a static archive build successful
while history/renderer references remain unresolved until a consumer extracts
the relevant object. A successful `hammond_core` archive is consequently not
the link or execution gate. Build the probe and behavioral executables from one
coherent source snapshot before invoking CTest.

### Probe target

Place this beside the existing motion/propagation probes, before the C++ and
Python test-discovery loops. These names are the integrator's proposed stable
names; the implementation files do not all exist at the A12 checkpoint.

```cmake
add_executable(hammond_rotary_waveform_probe
    tests/probes/rotary_waveform_probe.cpp
    tests/reference/rotary_waveform_reference.h)
target_link_libraries(hammond_rotary_waveform_probe PRIVATE hammond_core)
target_include_directories(hammond_rotary_waveform_probe PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/tests")
hammond_configure_target(hammond_rotary_waveform_probe)
list(APPEND HAMMOND_TEST_TARGETS hammond_rotary_waveform_probe)
```

The probe can include `reference/rotary_waveform_reference.h`. Keep the oracle
header out of `hammond_core` and all shipping targets. The probe is a standalone
native program in the ordinary core configuration, with no SDL2 or VST3
requirement. Do not register the full workload twice as both a C++ test and its
Python wrapper.

After the Python glob, add the following wiring. The proposed runner interface
is `--mode smoke|full --probe PATH --report-dir DIR --timeout-seconds N`;
`smoke` is its ordinary CTest mode, with an explicit smoke experiment identity.
The runner must reject a missing probe, incomplete required output or changed
source hashes instead of skipping or substituting Python-generated native data.

```cmake
if(TEST python_test_rotary_waveform_acceptance)
    set_property(TEST python_test_rotary_waveform_acceptance APPEND PROPERTY ENVIRONMENT
        "HAMMOND_ROTARY_WAVEFORM_PROBE_EXECUTABLE=$<TARGET_FILE:hammond_rotary_waveform_probe>"
        "HAMMOND_ROTARY_WAVEFORM_REPORT_DIR=${CMAKE_BINARY_DIR}/rotary-waveform/$<CONFIG>/smoke")
    set_tests_properties(python_test_rotary_waveform_acceptance PROPERTIES
        TIMEOUT 120 LABELS "rotary;waveform;smoke")
    add_custom_target(check_rotary_waveform_full
        COMMAND "${Python3_EXECUTABLE}"
            "${CMAKE_CURRENT_SOURCE_DIR}/tests/test_rotary_waveform_acceptance.py"
            --mode full
            --probe "$<TARGET_FILE:hammond_rotary_waveform_probe>"
            --report-dir "${CMAKE_BINARY_DIR}/rotary-waveform/$<CONFIG>/full"
            --timeout-seconds 1500
        DEPENDS hammond_rotary_waveform_probe
        WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
        USES_TERMINAL VERBATIM)
endif()
```

`$<TARGET_FILE:...>` and `$<CONFIG>` are required for Visual Studio and other
multi-configuration generators. Do not construct `build/Release/name.exe` or
assume that a PATH executable belongs to the build. The report directory is a
parent for fresh run directories, not permission to overwrite prior evidence.
Use a deterministic `latest.json` pointer only if its contents identify the
specific completed run; archive that run's actual report and artifacts.

The full target builds its own native input and remains outside the ordinary
fast `check` workload. Its failure must propagate through Python and CMake.
Report both the fast CTest outcome and the separately executed full gate; a
larger CTest pass count alone never implies complete R4 parity.

### Compiler and process constraints

Apply the existing `hammond_configure_target` to every new native target. It
sets C++20 and, on MSVC, `/W4 /WX /permissive- /Zc:__cplusplus`; on GCC/Clang/
AppleClang it sets `-Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion
-Wshadow -Werror`. Sanitizer configurations compile with
`-fsanitize=address,undefined -fno-omit-frame-pointer` and propagate the runtime
link requirement. Do not relax these flags for numeric casts or allocation
interposition. Use the existing portable allocation test's no-inline boundary
and matching overload strategy where appropriate.

The current policy does not explicitly select floating contraction or an MSVC
`/fp:` mode. Record the actual options, rounding mode, `double`/`long double`
precision and standard library in the acceptance report; reject fast-math.
If an explicit floating policy is subsequently needed, qualify both production
and reference under it before changing numerical evidence. An oracle-only flag
does not describe the core's arithmetic. MSVC `long double` must not be reported
as having extra precision without checking `numeric_limits`.

For the A25 CLI, follow `tools/CliArguments.h` and existing `wmain`/UTF-8
filesystem handling. Add `hammond_rotary_render` to the existing executable-only
MinGW `-municode` list when its entry point follows that convention. If the
test-only probe takes report paths through argv, give it the same path handling
and its own conditional MinGW option; do not apply startup flags to the static
core or every C++ test. File records and Windows stdout binary streams must use
binary mode. Python must use argument arrays and retain exact nonzero exits.

## 2. Private source copies and install boundaries

The [CaptureTools acceptance](../tests/test_capture_install.py)
`PrivateProject` copies complete `src/`, `include/`, `apps/`, `tools/` and other
configuration inputs, but copies only its own root test plus all
`tests/probes/`. It deliberately does not copy the entire root test tree. This
fixture configures the real project with `BUILD_TESTING=ON` without building
native targets.

Add the independent reference directory to that private copy alongside the
existing probe copy:

```python
shutil.copytree(ROOT / "tests" / "reference",
                self.source / "tests" / "reference")
```

This is required by the explicit header listed in the proposed probe target and
keeps the fixture complete if the probe includes that header. All new production
sources and `RotaryRendererInternal.h` already arrive through the `src/` copy.
The new `.cpp` probe already arrives through the `tests/probes/` copy. New
ordinary root behavioral tests are intentionally absent from this fixture and
are not configured there. Keep additional explicit root test/acceptance sources
inside the appropriate `if(TEST ...)` guard, or add their exact inputs to the
copy. Do not solve missing-source configuration errors by silently disabling
`BUILD_TESTING` or dropping the native acceptance target in the real project.

The other install fixtures do not configure the root project:

| Fixture/helper | Consequence for this R4 change |
| --- | --- |
| `tests/test_install.py::test_preflight_preserves_existing_prefix` | Builds a tiny private project containing five named stub tools and includes `InstallHammondTools.cmake`. No R4 source copy is needed while the fixed OfflineTools inventory stays unchanged. |
| `apps/standalone/native_tests/test_standalone_install.py::fixture` | Uses an imported standalone executable and explicit metadata copies. It needs no history, oracle or probe sources. |
| `plugins/vst3/tests/test_native_install.py` | Uses a private bundle/tiny install project. No new R4 inputs are required. |
| `cmake/InstallCaptureTools.cmake` | Exact 57-file source-only payload remains unchanged; the configure-only test still has a 180-second CTest timeout and 90-second child-command timeout. |
| `cmake/InstallStandalone.cmake` | Installs the standalone binary and its fixed capability/notices payload. Linking extra independent archive objects does not add a rotary device capability or install a research tool. |

The A12 recommendation is to keep `hammond_rotary_render` a build-tree research
tool for this R4 demonstration. Do not append it, the probe or the oracle to
OfflineTools, CaptureTools, Standalone or NativeVST3. OfflineTools currently
preflights and installs five executable targets, two plotters, the organ profile
and its fixture sets; several tests explicitly enforce that contract. An
installed rotary CLI would need its own reviewed payload/relocation contract
after A25 defines its input/output files. It is not a prerequisite for the
bounded offline demonstration and should not expand this integration patch.

If A25 adds `tests/test_rotary_render.py`, supply
`HAMMOND_ROTARY_RENDER_EXECUTABLE=$<TARGET_FILE:hammond_rotary_render>` only to
that suite and append the CLI to `HAMMOND_TEST_TARGETS`, so `check` builds it.
Exercise explicit horn/drum inputs, Unicode/space paths, format limits,
nonfinite rejection and new-output admission there. The existing organ CLI's
PCM16/clipping behavior is not an acceptable implicit format decision for
unclipped R4 pressure sums. A25 must freeze normalized input and float output
policy before any exact demo command or output claim is published.

## 3. Stack and allocation portability

`kMaxHistoryFrames` is 16,384, independent of the active ring capacity.
`WaveformHistory` contains 131,072 bytes of double storage before metadata.
`MotionFrameHistory` contains `16384*sizeof(MotionSegment)` bytes before
metadata. With the usual 56-byte layout of the current segment this is 917,504
bytes; one waveform plus one motion payload already totals 1,048,576 bytes.
These are layout-derived estimates, not a measured `sizeof` result for every
compiler. Record actual sizes in the new native report.

Allocate histories, whole-ring snapshots, the renderer's private storage and
its journal directly on the heap before measured processing. In particular,
avoid `auto before = *history`, a history-bearing return-value fixture, or
`make_unique<History>(History{})`, which first creates a large temporary. Use
direct heap construction and heap-to-heap snapshot copies outside the observed
interval. Do not add `/STACK` or increase test thread stacks to conceal it.
`RendererState` and diagnostics are deliberately small copied inspection values;
they are not full retained-history snapshots.

This addresses an observed portability risk: the preceding propagation fixture
used a 693,904-byte GCC frame and failed at a tightened 512 KiB child stack; its
repair reduced the frame to 5,872 bytes with the original workload preserved.
The original Windows failure did not include a stack trace, so that diagnosis
remains qualified in [A38's record](development/2026-11-14-reference-refinement/notes/A38-windows-allocation-repair.md).
The new histories are larger than that fixture. Run actual Windows Release
behavior/allocation tests and Linux ASan/UBSan/leak checks; a Linux
limited-stack check is supplementary, not an MSVC result. All allocation
instrumentation and injected late-failure accessors remain test-local.

## 4. CI placement, time limits and retained artifacts

The current [.github/workflows/ci.yml](../.github/workflows/ci.yml) builds every
default target and runs every registered test on Linux GCC, macOS AppleClang and
Windows MSVC Release, plus Linux Debug sanitizers. Thus new glob-discovered
behavior tests and the Python smoke enter those jobs without a new filter.
The Release command has `--timeout 300`; sanitizers use `--timeout 600`.
Use explicit per-test budgets for the new suites and preserve leak detection.
An initial smoke budget of 90 seconds for the native child and 120 seconds for
CTest is proposed, not measured performance evidence. Small native behavior
tests should begin with a bounded 120-second Release/300-second sanitizer cap;
confirm or revise those administrative limits from actual workloads, never by
reducing the frozen experiments or numerical thresholds.

The full fixture needs separate scheduling. The required one-pass oracle is
3,801,000 frames, 7,602,000 output scalar comparisons and 15,204,000 reference
path solves. Repeating all native frames across the six required block patterns
means 22,806,000 native frames and 91,224,000 native path solves. Launching a
process per sample or running the full workload in every unittest method would
multiply this cost incorrectly.

Add one required `rotary-waveform-full` Linux GCC Release job to `ci.yml`, using
the already-pinned checkout/Python actions and the existing core-only Release
configuration. Build `hammond_rotary_waveform_probe`, then invoke
`check_rotary_waveform_full`. A provisional job cap of 35 minutes, full-step cap
of 30 minutes and native child cap of 1,500 seconds leave room for configuration,
build and selected Python high-precision checks. The first actual full run must
retain timings and settle these limits before a hosted completion claim. A
timeout is a failed/incomplete full gate, never a successful smoke. Full MSVC
and AppleClang qualification, if not executed, remains explicitly unrun even
when their smoke and behavioral tests pass.

Retain full reports on both success and failure with the existing pinned
`actions/upload-artifact` and 14-day retention. Add an explicit
`build-release/rotary-waveform/Release/full/` path to that job's diagnostics;
ordinary Release/sanitizer diagnostics should also retain their small smoke
report directory. Do not upload a whole build, `.git`, the PDF, static libraries
or all temporary canonical audio. Missing required reports/artifacts must fail
the runner's completeness check before artifact upload; upload warnings are
not acceptance. Preserve partial failure evidence under a failed-run identity.

The existing native workflows are intentionally different:

| Workflow | Existing selection and required action |
| --- | --- |
| `standalone.yml` Release | Builds `hammond_standalone_test_inputs`, then selects `^test_standalone_`. This does not build/run the R4 probe. Keep R4 in core CI; actual UI changes still use these standalone gates. |
| `standalone.yml` native sanitizers | Builds and requires exactly 16 named interface targets with matching cardinality/assertions and selected timeout checks. No R4 additions belong in that fixed interface list. A genuinely new UI test must update the list, its count and discovery assertion together. |
| `native-vst3.yml` | Builds `hammond_vst3_test_inputs`, then selects `^(hammond_vst3_validator|test_native_)`. This is neither full R4 coverage nor a reason to expose the renderer through the plugin. |

### Storage and evidence bounds

Use one native process and one rate at a time. Generate source samples by their
absolute integer indices. Keep one current block, metrics and the small oracle
event timeline; keep only one canonical stereo binary64 stream for direct
partition comparisons. Its maximum size is 30,720,000 bytes at 192 kHz. The
33,280-row static response grid must remain complete, preferably losslessly
gzip-compressed using Python's standard library. For deterministic gzip bytes,
control its timestamp/header metadata. Retain all high-band rows even when only
the low-band error has a pass budget.

Failure records may use complete lossless per-channel frame bitmaps; the largest
two-channel bitmap is 480,000 bytes. A first-N failure log alone is incomplete.
Set an initial run-directory budget of 64 MiB for reproducible scratch and
32 MiB for compact retained evidence, excluding an explicitly selected demo
audio file. Measure actual bytes and report a budget violation; never truncate
required grid rows or failed indices to make an archive fit. Store verbose
stdout/stderr in bounded files rather than retaining unbounded subprocess
capture buffers. A probe should emit aggregate records and selected traces,
not millions of sample JSON lines.

Keep build output, canonical temporary audio and intermediate grids in the
owned build/work directory. Delete only the current run's reproducible
canonical stream after complete comparisons and compact evidence are retained.
The checked-in evidence can contain final reports, compressed complete grid,
small selected traces and a bounded demo. Existing `.gitignore` excludes WAV;
do not globally unignore arbitrary render output. Any deliberately retained
demo WAV needs an explicit reviewed add and exact byte identity. New raw
binary64/bitmap formats also need binary Git attributes if retained, as existing
`.gitattributes` already does for `.f32`, `.wav` and `.b3p`.

## 5. Native capture interaction

[capture_standalone_interface.py](../tools/capture_standalone_interface.py)
already recursively inventories all files under `src/` and `include/`, including
untracked overlays. It therefore sees the three new sources and the private
header without changing `REQUIRED_QUALIFIED_SOURCES`. Its build inventory sees
the current Linux core archive. Source/header changes during its eight cases
are detected as drift, even though the R4 module is not connected to Engine.

Finish the coherent rebuild and agree a production-source freeze before actual
UI captures. Generate a fresh qualification JSON for the current binary and
reviewed UI sources; the earlier baseline binary hash is not usable. Capture
into a new directory, preserve existing galleries and retain the utility's
12-second per-process default (allowed range 4–60 seconds) separately from R4
test timing. The eight cases each run a 1,800 ms replay. Pillow remains the
already-optional image-authoring dependency; no waveform/core job needs it.

The current utility records selected `.a` archives, not a complete cross-platform
`.lib`/multi-configuration build inventory. Use its retained Linux capture
boundary honestly; do not infer MSVC source-to-binary attestation from it.
Concurrent test/install-rule/docs work is excluded from its production
inventory, but those files still belong in the separate R4 report's source
identity where they affect execution. Neither a native gallery nor the fixed
57-file CaptureTools package is a waveform oracle.

## 6. Integrator execution order and concrete commands

The following commands are for the integrator **after** the new sources,
runner, proposed targets and fixture copy are implemented and frozen. A12 did
not execute them. The existing local CMake is absent from the ordinary PATH;
the actual reused executable is below. These commands reuse the session build
and do not acquire or modify other sessions' dependencies.

```sh
cd /workspace/scratch/e3cacb90cc81/Hammond-B3-Organ
wave_cmake=/workspace/scratch/1bb6ee17ad7e/build-tools/cmake/data/bin/cmake
wave_ctest=/workspace/scratch/1bb6ee17ad7e/build-tools/cmake/data/bin/ctest

"$wave_cmake" -S . -B ../build
"$wave_cmake" --build ../build --config Release --parallel 3
"$wave_ctest" --test-dir ../build -C Release --show-only=json-v1 \
    -R '^(test_rotary_|python_test_rotary_)'
"$wave_ctest" --test-dir ../build -C Release --output-on-failure \
    --no-tests=error -R '^(test_rotary_|python_test_rotary_)'
"$wave_ctest" --test-dir ../build -C Release --output-on-failure \
    --no-tests=error \
    -R '^(python_test_capture_install|python_test_install|test_standalone_install|python_test_repository_integrity|python_test_capture_standalone_interface)$'
"$wave_cmake" --build ../build --config Release \
    --target check_rotary_waveform_full
"$wave_ctest" --test-dir ../build -C Release --output-on-failure \
    --no-tests=error --parallel 3
```

The cached session configuration is Ninja, Release, standalone ON, MIDI OFF,
VST3 OFF, sanitizers OFF, locked SDL2 at
`/workspace/scratch/1bb6ee17ad7e/SDL2`, and `SDL_ALSA=OFF`. Preserve these facts
when interpreting the local test result. The first configure command reuses
them; it is not a clean multi-platform reproduction or an enabled-device run.
Use the existing hosted sanitizer job and the separate platform builds for
their named claims. Confirm discovered test names/commands before a required
filtered run; `--no-tests=error` remains mandatory.

For a core-only full CI run, the proposed commands are:

```sh
cmake --preset release -G "Unix Makefiles" -DCMAKE_CXX_COMPILER=g++
cmake --build --preset release --parallel 2 --target hammond_rotary_waveform_probe
cmake --build --preset release --target check_rotary_waveform_full
```

Add the workflow's exact `Python3_EXECUTABLE` as it already does. Every report
must name actual source/worktree hashes, executable hash, compiler/options,
configuration, oracle identity, required counts, timing and result; changing
HEAD or source after a run does not retroactively qualify the new bytes.

## 7. Remaining prerequisites and evidence limits

1. History/renderer implementations, the native probe, Python runner and A25
   CLI are not implemented by this plan. Final API acceptance and the new
   private header must precede one coherent link/execution gate.
2. Add `tests/reference/` to `PrivateProject` in the same CMake integration
   change. Otherwise its real configure can fail on the new explicit header
   before capture installation is tested.
3. Full-workload runtime and memory have not been measured. The proposed limits
   are bounded administration; the frozen experiment remains complete at all
   four rates and six block patterns, with all static rows and selected
   independent high-precision cross-checks.
4. A25 must define the normalized horn/drum input and floating output contract,
   rate/frame/file-size admission, explicit tail handling and deterministic
   demonstration before `hammond_rotary_render` can be built or advertised.
   Existing dry-organ render syntax must not be presented as that future CLI.
5. Actual Windows, macOS, hosted sanitizer and full R4 outcomes remain unrun
   for these new modules. Local stack-risk reasoning, earlier hosted results,
   the 155/155 baseline and the remote fixture repair do not replace them.

The inspected baseline is **155/155 in 152.15 seconds** at `2e161dc`, before
these R4 modules. After integrating `f9c11a4`, the three affected local checks
passed **3/3 in 2.80 seconds**: propagation allocation, retained interface
capture validation and repository integrity. The [A12 note](development/2026-11-14-waveform-continuation/notes/A12-build-scope.md)
records this audit's exact owned files and its inspection-only qualification.
