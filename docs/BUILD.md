# Building the engineering baseline

The core uses C++20 and the standard library. Authoring tools use Python's
standard library. The default build requires no downloads, host SDKs, audio
drivers or external libraries. It includes the nominal manual/pedal engine and
offline tools. An [optional native VST3 build](#optional-native-vst3-build)
uses a separately acquired pinned SDK; configuration never fetches dependencies.
The nominal profile and synthetic output are engineering fixtures, not measured
instrument evidence. [PEDAL_HANDOFF.md](PEDAL_HANDOFF.md) connects the build to
current rendering, tracing, installation and resume procedures.

## Prerequisites

- CMake 3.21 or newer, including its matching `ctest` executable.
- A C++20 compiler and build tool: GCC/Make, Clang/Make or Ninja, or MSVC/MSBuild.
- Python 3.10 or newer, discoverable by CMake as a Python 3 interpreter.

For `HAMMOND_BUILD_VST3=ON`, additionally use CMake 3.25+ and the exact external
SDK/submodules in [vst3-sdk-lock.json](../data/dependencies/vst3-sdk-lock.json).
The default switch is `OFF`. Native SDK sources and their generated outputs stay
outside this repository and outside each other's directories.

CMake enables strict warnings and treats them as errors for GCC, Clang,
AppleClang and MSVC. This exposes portability problems instead of hiding them.
The [verification record](#verification-record) separates historical local checks
from later hosted qualification. [STATUS.md](STATUS.md), [CI.md](CI.md) and the
[current handoff](PEDAL_HANDOFF.md) identify tested revisions and remaining gates;
[CI_QUALIFICATION.md](CI_QUALIFICATION.md) retains the original session's history.

## Linux and macOS

From the repository root:

```sh
cmake --preset debug
cmake --build --preset debug --parallel 2
ctest --preset debug
```

The default generator is selected by CMake. To select one explicitly, append
`-G "Unix Makefiles"` or `-G Ninja` on the first configure in an empty build
directory. A generator change requires a different build directory.

Equivalent explicit commands, useful with a local CMake executable:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug -DBUILD_TESTING=ON
cmake --build build --parallel 2
ctest --test-dir build --output-on-failure
```

To use a particular compiler, pass `-DCMAKE_CXX_COMPILER=clang++` on the first
configure of a separate directory. To select Python, pass
`-DPython3_EXECUTABLE=/absolute/path/to/python3`.

The optional POSIX Makefile wraps the same commands:

```sh
make build
make test
make profile
make clean
make test CMAKE=/absolute/path/to/cmake BUILD_DIR=build-local JOBS=4
```

`CMAKE`, `BUILD_DIR`, `CONFIG`, `JOBS` and `CMAKE_ARGS` are overridable. `make clean`
uses CMake's generated clean target in the selected build directory; it preserves
configuration and source files. It does not recursively delete a supplied path.

## Windows

Run these commands in a Visual Studio developer terminal with a C++20-capable
MSVC installation and Python available. The preset uses CMake's discovered
generator; a Visual Studio generator uses the explicit Debug configuration in
the build and test presets.

```powershell
cmake --preset debug
cmake --build --preset debug --parallel 2
ctest --preset debug
```

The explicit equivalent is:

```powershell
cmake -S . -B build -DBUILD_TESTING=ON
cmake --build build --config Debug --parallel 2
ctest --test-dir build -C Debug --output-on-failure
```

With a single-configuration generator such as Ninja, also pass
`-DCMAKE_BUILD_TYPE=Debug` when configuring. Executables live directly under the
build directory for single-configuration generators and normally under `Debug/`
or `Release/` for Visual Studio. The compiled profile remains at the build root.
The POSIX Makefile is optional; Windows does not need it.
All six native CLI programs use the explicit Unicode argument boundary described
in [CLI_UNICODE.md](CLI_UNICODE.md); use the selected configuration's executable
and preserve quoting around paths containing spaces.

## Targets and generated data

| Target | Purpose |
|---|---|
| `hammond_core` | Static framework-independent core from `src/*.cpp` |
| `hammond_profile` | Validate authoring JSON and write `build/nominal.b3p` |
| `hammond_pedal_routing` | Validate/compile the reviewed 200-position pedal routing data into the private generated header |
| `hammond_render` | Offline WAV renderer from `tools/render.cpp` |
| `hammond_model_info` | Compiled console and pedal model metadata |
| `hammond_parameter_info` | All 45 core parameter mappings; diagnostic output does not inspect native host exports |
| `hammond_console_trace` | Actual sample-by-sample console diagnostics |
| `hammond_pedal_trace` | Actual pedal unmute, overlap and routing diagnostics |
| `hammond_benchmark` | Bounded prepared-engine timing measurements; see [BENCHMARKING.md](BENCHMARKING.md) |
| `test_*` | One standalone executable for each `tests/test_*.cpp` |
| `check` | Build the required profile/tools/tests, then run all registered CTest entries; requires `BUILD_TESTING=ON`, and includes native inputs/tests when enabled |
| `HammondB3` | Optional actual VST3 module and bundle resources; requires `HAMMOND_BUILD_VST3=ON` |
| `hammond_vst3_test_inputs` | Optional build-only aggregate for the module, validator and all native harnesses |
| `check_vst3` | Build that aggregate, then run the focused validator and `test_native_*` entries |

The profile compiler runs as:

```sh
python3 tools/compile_profile.py --input data/profiles/nominal-unmeasured-v1.json --output build/nominal.b3p
```

CMake uses its selected `Python3_EXECUTABLE` for this command and tracks both
input files as dependencies. The output is always `<binary-directory>/nominal.b3p`.
Normal builds generate it; C++ test targets and the renderer depend on it.
Building only `hammond_core` does not require a generated profile.

CMake rechecks source/test globs during builds. New `src/*.cpp`, `tests/test_*.cpp`,
`tests/test_*.py`, and the renderer source trigger regeneration. Each C++ test has
the core library and test include directory, plus quoted `HAMMOND_TEST_PROFILE`
and `HAMMOND_SOURCE_DIR` path definitions. `TestSupport.h` supplies `CHECK`,
`CHECK_NEAR(actual, expected, absolute_tolerance)` and global `load_test_profile()`.
Checks remain active with `NDEBUG`; non-finite inputs fail approximate checks.

Each Python test script is invoked directly with the selected Python interpreter
from the source root, so it must run its test runner when invoked as `__main__`.
CTest exposes the same profile/source paths as environment variables and disables
Python bytecode output. Run a build before calling `ctest` directly; CTest does
not compile test executables or generate input files itself. The `check` target
performs those prerequisites automatically.

The [OfflineTools install component](OFFLINE_INSTALL.md) installs the five native
offline tools, compiled profile, catalogs/scores and its declared plotting scripts
into a selected local prefix. Its CTest exercises actual installation, relocation,
PCM identity and explicit data use. The separately enabled
[NativeVST3 component](VST3_LOCAL_INSTALL.md) stages a complete built bundle;
neither component supplies an audio-device application or compiler runtime
package. Their current manifests own the file lists; older file counts describe
only their recorded historical revisions.

## Release and sanitizer builds

```sh
cmake --preset release
cmake --build --preset release --parallel 2
ctest --preset release

cmake --preset sanitizers
cmake --build --preset sanitizers --parallel 2
ctest --preset sanitizers
```

The sanitizer preset enables `HAMMOND_ENABLE_SANITIZERS=ON` in a separate
`build-sanitizers` directory. It instruments C++ code with ASan and UBSan and
retains frame pointers. CMake checks that the selected GCC/Clang driver can
compile and link both runtimes. Unsupported compiler drivers, including MSVC
and clang-cl, fail configuration with an explicit message. Sanitizer support
must also exist in the installed toolchain and execution environment.

## Optional native VST3 build

Use [VST3_BUILD.md](VST3_BUILD.md) for the exact SDK identity, license checks and
platform-specific build boundaries. The reviewed SDK is 3.8.1,
`v3.8.1_build_84`, root commit
`3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96`; the lock also pins all four required
submodules. Acquire into a new external directory whose parent already exists:

```sh
python3 tools/acquire_vst3_sdk.py --destination /absolute/path/to/vst3sdk
python3 tools/acquire_vst3_sdk.py --verify-existing /absolute/path/to/vst3sdk
cmake -S . -B build-native -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_VST3=ON -DHAMMOND_VST3_SDK_ROOT=/absolute/path/to/vst3sdk \
  -DCMAKE_INSTALL_LIBDIR=lib
cmake --build build-native --config Release --parallel 2 \
  --target hammond_vst3_test_inputs
ctest --test-dir build-native -C Release --output-on-failure --no-tests=error \
  -R '^(hammond_vst3_validator|test_native_)'
```

For an already acquired SDK, run only `--verify-existing`; the acquisition helper
deliberately refuses existing destinations and never resets them. Both modes
check the root/submodule pins, raw license/parser identities and tracked,
untracked or ignored changes. GUI/sample/hosting applications and automatic
system-plugin links remain disabled. Do not build inside the SDK worktrees.

The commands retain the configuration for Visual Studio; replace the SDK path
with its actual local spelling and use PowerShell continuation syntax where
needed. `cmake --build build-native --config Release --target check_vst3`
combines the input build and focused test run. A module-only build is not a
validation result. The generated
`build-native/hammond-vst3-path-Release.txt` records the exact platform bundle
path. Native tests are conditional on the option; the selective native allocation
audit is additionally Linux-specific. Read test discovery and logs rather than
assuming a historical count applies to every platform or revision.

The current instrument supports three event input buses, 45 controls and dry
float32 stereo at 44.1/48/96 kHz with generic host controls. See the
[native contract](VST3_SPIKE_CONTRACT.md) for input limits and state migration.
Hosted native builds have a [separate workflow](VST3_CI.md) and a retained
[portability repair record](reviews/PEDAL_NATIVE_PORTABILITY.md).

## Install into a selected local prefix

Install does not build missing inputs. After building the corresponding tools
or bundle, select the component and a new local destination explicitly:

```sh
cmake --install build-release --config Release --component OfflineTools \
  --prefix "$HOME/hammond-offline-stage"
cmake --install build-native --config Release --component NativeVST3 \
  --prefix "$HOME/hammond-native-stage"
```

The first command assumes the Release preset's `build-release` directory; use
the actual configured directory if different. Keep `CMAKE_INSTALL_MODE` unset or
`COPY` so the payload can move without referring to build-tree symlinks. Offline
installation can replace selected files in an existing prefix; native staging
refuses an existing destination `HammondB3.vst3`. The native example's explicit
`CMAKE_INSTALL_LIBDIR=lib` yields `lib/vst3/HammondB3.vst3` below its prefix.
Neither command registers the module with a DAW. The component documents retain
the preflight, relocation, configuration and evidence details.

## Verification record

The [original build-foundation note](development/agent-notes/09-build-foundation.md)
records historical local checks on Linux with GCC 14.2.0, GNU Make 4.4.1,
Python 3.12 and a task-local CMake 4.4.4. macOS/AppleClang and Windows/MSVC were
not executed for that initial assignment. Its results cover that foundation;
they do not describe the qualification of later engine, renderer or test changes.

Subsequent hosted runs exercised Linux, macOS, Windows and Linux sanitizers at
specific revisions. Consult [current status](STATUS.md), [current handoff](PEDAL_HANDOFF.md)
and [both workflow scopes](CI.md) for observed passes, retained failures and
pending reruns. A result applies to its recorded revision, platform
and scope; it does not automatically qualify the working tree. The
[development log](DEVELOPMENT_LOG.md) records the intervening changes and local
evidence. No verification pass is implied by the commands on this page.

A successful build does not establish real-time deadlines, host compatibility,
physical fidelity, product release readiness or sanitizer coverage of unexecuted
paths. For practical render/install workflows and the related evidence contracts,
see the [project guide](PROJECT_GUIDE.md).
