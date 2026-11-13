# Building the engineering baseline

The core uses C++20 and the standard library. Authoring tools use Python's
standard library. No package downloads, host SDKs, audio drivers or external
libraries are required by this build. The nominal profile and synthetic output
are engineering fixtures; they are not measured instrument evidence.

## Prerequisites

- CMake 3.21 or newer, including its matching `ctest` executable.
- A C++20 compiler and build tool: GCC/Make, Clang/Make or Ninja, or MSVC/MSBuild.
- Python 3.10 or newer, discoverable by CMake as a Python 3 interpreter.

CMake enables strict warnings and treats them as errors for GCC, Clang,
AppleClang and MSVC. This exposes portability problems instead of hiding them.
The [verification record](#verification-record) separates historical local checks
from later hosted qualification. [STATUS.md](STATUS.md) and
[CI_QUALIFICATION.md](CI_QUALIFICATION.md) identify the tested revisions and
remaining gates.

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

## Targets and generated data

| Target | Purpose |
|---|---|
| `hammond_core` | Static framework-independent core from `src/*.cpp` |
| `hammond_profile` | Validate authoring JSON and write `build/nominal.b3p` |
| `hammond_render` | Offline WAV renderer from `tools/render.cpp` |
| `hammond_benchmark` | Bounded prepared-engine timing measurements; see [BENCHMARKING.md](BENCHMARKING.md) |
| `test_*` | One standalone executable for each `tests/test_*.cpp` |
| `check` | Build the profile and C++ tests, then run CTest; requires `BUILD_TESTING=ON` |

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

The [OfflineTools install component](OFFLINE_INSTALL.md) installs the renderer,
compiled profile and event fixtures into a user-selected local prefix. Its CTest
smoke exercises actual installation, relocation, PCM identity and explicit data
use. It adds no audio-device application, plugin or platform runtime packaging.

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

## Verification record

The [original build-foundation note](development/agent-notes/09-build-foundation.md)
records historical local checks on Linux with GCC 14.2.0, GNU Make 4.4.1,
Python 3.12 and a task-local CMake 4.4.4. macOS/AppleClang and Windows/MSVC were
not executed for that initial assignment. Its results cover that foundation;
they do not describe the qualification of later engine, renderer or test changes.

Subsequent hosted runs exercised Linux, macOS, Windows and Linux sanitizers at
specific revisions. Consult [current status](STATUS.md) and the
[CI qualification record](CI_QUALIFICATION.md) for observed passes, retained
failures and pending reruns. A result applies to its recorded revision, platform
and scope; it does not automatically qualify the working tree. The
[development log](DEVELOPMENT_LOG.md) records the intervening changes and local
evidence. No verification pass is implied by the commands on this page.

A successful build does not establish real-time deadlines, host compatibility,
physical fidelity, product release readiness or sanitizer coverage of unexecuted
paths. For practical render/install workflows and the related evidence contracts,
see the [project guide](PROJECT_GUIDE.md).
