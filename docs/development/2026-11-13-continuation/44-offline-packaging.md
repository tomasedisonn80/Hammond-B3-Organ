# Assignment 44 — expanded offline installation and relocation

Agent: `/root/w08_a44_offline_packaging`

Date: 2026-11-13 UTC. Continuation wave 08, assignment 44 of its 60 new workers.

## Scope and implementation

Expanded `OfflineTools` from eight to exactly **16 installed files**: the renderer,
model metadata exporter, parameter metadata exporter, console trace executable,
standalone trace plot script, compiled profile, both fixture catalogs and all
eight event scores. The original files retain their existing paths and bytes.
The console catalog and three scores occupy `fixtures/console/`; the plotter is
`bin/plot_console_trace.py` under the default relative `GNUInstallDirs` layout.

CMake checks all four built executables, the compiled profile and source plot
script before copying component files. It retains configuration-aware target
paths, relative destination validation and ordinary CMake install semantics.
The test receives the exact additional metadata executable paths. The existing
trace target and its test registration were preserved.

`tests/test_install.py` now checks the exact payload, unchanged data/script bytes,
and actual operation after the prefix is renamed. Every installed invocation runs
from an unrelated directory with all `HAMMOND_*` variables removed. Python plotting
uses `sys.executable`, so it does not rely on file association or executable suffix
behavior. The installed script has no repository-relative imports.

`docs/OFFLINE_INSTALL.md` supplies Linux/macOS and PowerShell build/install/run
commands, runtime requirements, the complete payload, nominal percussion rendering,
metadata inspection, tracing, plotting, and the scope of relocation evidence.
The four native tools do not require Python at runtime; plotting requires Python
3.10+ and its standard library. No benchmark, core SDK, framework, native installer,
compiler runtime bundle or physical-calibration claim was added.

The atlas basis is pp. 450 and 453: product/release capabilities require their own
observed evidence, and preparation/file workflows stay outside processing. This
local offline package does not close native host/device or redistributable-product
gates.

## Coherent source boundary

Qualification used a `git archive` of immutable tree
`b9146546fcf756360e1da89d6698c4999359579f`, followed by only the four overlays below.
This tree already contains the published lifecycle and frozen partial-key/trace
runtime. Core, executables and the test were built from that one source directory.
Assignment 42 supplied its frozen plotter hash before it was copied. No older
library was linked against live headers.

| Overlay | SHA-256 |
| --- | --- |
| `CMakeLists.txt` | `c68903718fb3e77a192a20a5d0fedcae88b90e086391bbc05214ec8ee4a142df` |
| `tests/test_install.py` | `3b22c69f4c763f555081af831df59ce63faf9c6d365c704621bc389d87a23505` |
| `docs/OFFLINE_INSTALL.md` | `613dc59e549c8a60d3d23ed42b20d45db3059f261ea5319962e43f5c15a6d231` |
| Assignment 42's `tools/plot_console_trace.py` | `e7cf4603acbf2707b7752f781314a97293b89567675eb19cae772f4db37d3720` |

Every overlay was rehashed after the gate and still matched its live owned file.
The integrating agent's staged wave-seven CMake SHA-256 remained
`f37c6bd8dedb1325db4f79ed15162b837139254b1f1c2ac100e105b8a2dbfeac`.
This assignment made no index changes.

## Actual verification

Linux x86_64, GCC 14.2.0, CMake 4.4.4 and Python 3.12.14. Strict Release compilation
passed on the first build. The focused gate passed **1/1 CTest suite in 1.54 s**;
its one Python method passed in 1.446 s with zero skips. The method performs
16 actual subprocess invocations, including installation and all five tools.

| Check | Observed result |
| --- | --- |
| Install before building | Expected nonzero build-first diagnostic; destination prefix remained absent |
| Successful install | Exactly 16 files, no symlinks; all profile/catalog/score/script bytes preserved |
| Relocation | Original prefix absent after rename; all tools ran from an unrelated working directory |
| Original A4 fixture | Same-build and installed metrics, PCM and complete WAV bytes identical |
| Nominal percussion fixture | Explicit catalog model controls; both actual renders audible, unclipped and byte-identical |
| Metadata exporters | Same-build and installed output identical; two console factories and all 43 parameter mappings present |
| Console trace | Two 5,760-row partial traces produced identical CSV bytes |
| Plotting | Installed script and source script produced identical SVG from the retained trace; XML parsed, trace hash retained, output within 1 MiB |
| Explicit installed profile | Synthetic zero-gain/digest mutation affected identity and produced silence; original bytes restored afterward |
| Missing profile | Both installed renderer and trace executable failed without creating output |

The successful audio calls rendered 300,000 frames in total, including the existing
zero-gain probe. Trace calls rendered 11,520 frames. Comparisons are same-build
identity checks, not new DSP numerical or physical oracles. No production defect,
compile failure or unexpected test failure occurred. The unbuilt-install rejection
was an intentional admission check.

Commands actually run (line wrapping added for readability):

```sh
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  -S /workspace/scratch/60e8291da354/a44-offline-qualification/source \
  -B /workspace/scratch/60e8291da354/a44-offline-qualification/build \
  -DCMAKE_BUILD_TYPE=Release
# Before building: expected rejection with no created prefix.
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  --install /workspace/scratch/60e8291da354/a44-offline-qualification/build \
  --component OfflineTools \
  --prefix /workspace/scratch/60e8291da354/a44-offline-qualification/unbuilt-prefix
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  --build /workspace/scratch/60e8291da354/a44-offline-qualification/build \
  --parallel 4 --target hammond_render hammond_model_info \
  hammond_parameter_info hammond_console_trace
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/60e8291da354/a44-offline-qualification/build \
  --output-on-failure -R '^python_test_install$'
```

The snapshot manifest SHA-256 is
`03c5cf02df2c09213509fad4429376623e862bfb4e87df3835710f1b6c7d5ed0`.
The generated `nominal.b3p` retains SHA-256
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.
Scratch paths identify this observed qualification; permanent tests do not depend
on those directories surviving.

## Files, limits and next gate

Changed only the install/install-test environment sections of `CMakeLists.txt`,
`tests/test_install.py`, `docs/OFFLINE_INSTALL.md`, and this note. Assignment 42's
plotter was consumed unchanged. No shared status files, core source, existing data,
other agents' files, staging, commits or pushes were modified by this worker.

The integrator must retain the wave-seven CMake snapshot for its current checkpoint,
then stage these install changes with the completed wave-eight scope, run the
combined source gate, publish under the expected-head workflow, and observe new
hosted results. This local run does not substitute for macOS/Windows qualification,
sanitizer installation, cross-machine runtime compatibility, redistributable
bundles, signing, actual plugin/device operation or physical-model evidence.
