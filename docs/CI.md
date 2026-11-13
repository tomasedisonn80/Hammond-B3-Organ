# Continuous integration

The [CI workflow](../.github/workflows/ci.yml) builds and tests the current
framework-independent core, generated nominal profile, offline renderer, and
registered C++/Python tests. It runs on pushes to `main`, pull requests, and
manual dispatch. This is engineering verification of the nominal model.

## Supported CI matrix and observed qualification

| Check | Hosted runner | Compiler / architecture | Configuration |
| --- | --- | --- | --- |
| Release (Linux GCC) | `ubuntu-24.04` | GCC / x64 | Release |
| Release (macOS AppleClang) | `macos-15` | AppleClang / arm64 | Release |
| Release (Windows MSVC) | `windows-2022` | Visual Studio 2022 MSVC / x64 | Release |
| Linux GCC ASan + UBSan + leaks | `ubuntu-24.04` | GCC / x64 | Debug, address/undefined/leak checks |

All four jobs passed their 26 registered suites at `61c6ecb` in
[run 43368537860](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43368537860).
The complete archives contain 274 Python methods per job and zero test skips.
The [final platform audit](reviews/FINAL_PLATFORM_REVIEW.md) retains exact
source/artifact identities, actual tools, complete method counts and sanitizer flags.
The first run exposed macOS decimal parsing and Windows evidence assumptions;
those failures and their fixes remain in the development log and agent notes.
Qualification requires the actual jobs for the exact commit under review. At the
earlier checkpoint `7c2ad20`, two jobs exposed failures; the complete archive,
skip audit and passing repair integration are retained in
[CI_QUALIFICATION.md](CI_QUALIFICATION.md). On a
pull request, the default checkout tests GitHub's merge revision; the diagnostic
artifact records `git rev-parse HEAD`. Never transfer a passing result to a later
commit without rerunning the affected checks. Shared observed results belong in
[STATUS.md](STATUS.md) and [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md).

Python is selected as `3.12` through the pinned official setup action, including
the selected interpreter's absolute path in CMake configuration. CMake and CTest
come from the hosted image; CMake configuration enforces the repository minimum
of 3.21. The workflow logs their exact versions, Python, the compiler selection,
and the tested revision. Stable OS labels still receive image and tool updates;
this matrix does not pin every compiler or Python patch release. Runner labels
and architectures follow the [official runner inventory](https://github.com/actions/runner-images#available-images).

## What runs and how failures propagate

Each job configures an out-of-source directory, builds the selected preset with
two parallel workers, then invokes CTest. Release uses the `release` preset;
instrumented Linux uses `sanitizers`. Both enable `BUILD_TESTING` and generate
the compiled nominal profile before running tests. Visual Studio receives the
Release configuration through the build/test presets.

CMake discovers `src/*.cpp`, `tests/test_*.cpp`, and `tests/test_*.py`. New tests
following those conventions enter CI without another workflow edit. CTest runs
the entire registered suite, including Python tests that launch the renderer;
there is no hand-maintained test allowlist. An empty suite is an error. Two tests
may run concurrently. Each Release test has a 300-second timeout; each sanitizer
test has 600 seconds. Whole jobs are limited to 20 and 25 minutes respectively.

ASan and UBSan instrument the C++ targets through
`HAMMOND_ENABLE_SANITIZERS=ON`. The Linux job explicitly sets
`ASAN_OPTIONS=detect_leaks=1:halt_on_error=1`,
`UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1`, and
`LSAN_OPTIONS=exitcode=23`. Reports are failures. The local executor's previously
recorded ptrace/LeakSanitizer limitation is not used to disable leak checking on
GitHub-hosted runners. A sanitizer pass covers only executed instrumented paths;
it does not instrument the Python interpreter or prove the absence of all bugs.

Jobs use Bash with GitHub's `-e -o pipefail` behavior, so piping output through
`tee` preserves configure/build/test failures. Matrix `fail-fast` is disabled
to retain the other platforms' evidence after one fails. New runs cancel older
runs for the same pull request or branch; a canceled run is not a passing check.

## Reproduce locally

Use a C++20 toolchain, CMake/CTest 3.21 or newer, and Python 3.12 to match CI.
The project's general Python minimum remains 3.10; see [BUILD.md](BUILD.md).
From the repository root, the common Release commands are:

```sh
cmake --preset release
cmake --build --preset release --parallel 2 --verbose
ctest --preset release --parallel 2 --timeout 300 --no-tests=error
```

On the first configure of an empty build directory, add
`-G "Unix Makefiles" -DCMAKE_CXX_COMPILER=g++` for Linux, or
`-G "Unix Makefiles" -DCMAKE_CXX_COMPILER=clang++` for macOS. On Windows with
Visual Studio 2022 installed, use `-G "Visual Studio 17 2022" -A x64`.
To choose the same Python explicitly, add
`-DPython3_EXECUTABLE=/absolute/path/to/python3.12` with the appropriate local
path. Changing generators or compilers requires a fresh build directory.

Linux GCC sanitizer reproduction:

```sh
cmake --preset sanitizers -G "Unix Makefiles" -DCMAKE_CXX_COMPILER=g++
cmake --build --preset sanitizers --parallel 2 --verbose
ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 \
UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1 \
LSAN_OPTIONS=exitcode=23 \
ctest --preset sanitizers --parallel 2 --timeout 600 --no-tests=error
```

For a focused failure, run `ctest --preset release -R 'test_name' -V` or the
equivalent sanitizer preset with the same environment. Retain the original
failure and explain any reproduction difference. A run with leak detection
disabled cannot qualify the hosted leak-checking gate.

## Read the result and diagnostics

A green workflow requires all three Release jobs and the sanitizer job to pass.
A parser check of the YAML, a successful configure, or an unexecuted workflow
does not establish this. Inspect the run's commit, job conclusions, test counts,
and any skips before recording qualification. Python unittest skips can appear
inside a CTest test that otherwise passes; specifically, the profile compiler's
symlink/hardlink permission checks may report unsupported-platform skips. Those
cases must be reported as unexecuted coverage, not silently counted as tested.
The renderer's hard-link publishing behavior remains a required integration check.

Each non-canceled job uploads `ci-<platform>-<configuration>-<attempt>` diagnostics
for 14 days, including tool/revision records, configure output, verbose build
output, CTest console output and JUnit XML. CMake's configuration diagnostics,
cache, and CTest `LastTest.log` / `LastTestsFailed.log` are included when produced.
An early failure may leave some files absent; inspect the first failing step.
The full test log is useful even when the console only prints failed tests.
Artifacts are diagnostics, not distributable plugin or application packages.

The portable decimal converter and Windows evidence repairs now have observed
MSVC/AppleClang results at the commit above. Exact nominal `pow` comparisons,
differing `long double` precision and filesystem behavior remain relevant when
the compiler or platform changes. Fix demonstrated defects in their source/test
contract; do not suppress a job or warning to manufacture qualification.

## Workflow trust and maintenance

The workflow uses `contents: read`, opts out of persisted checkout credentials,
and does not access repository secrets, publish releases, deploy, or write back
to the repository. Pull requests run under `pull_request`; there is no trusted
`pull_request_target` or follow-up workflow executing their code. No dependency
cache is shared between these runs. Only named diagnostic paths are uploaded.

Official GitHub actions are pinned to verified full commit SHAs. As checked
against their release tags and manifests on 2026-11-13:

| Action | Release | Verified commit | License |
| --- | --- | --- | --- |
| `actions/checkout` | `v7.0.1` | [`3d3c42e5aac5ba805825da76410c181273ba90b1`](https://github.com/actions/checkout/commit/3d3c42e5aac5ba805825da76410c181273ba90b1) | [MIT](https://github.com/actions/checkout/blob/3d3c42e5aac5ba805825da76410c181273ba90b1/LICENSE) |
| `actions/setup-python` | `v7.1.0` | [`6d4fd22b20465ccc0f7354476588e8df7c9ca0e0`](https://github.com/actions/setup-python/commit/6d4fd22b20465ccc0f7354476588e8df7c9ca0e0) | [MIT](https://github.com/actions/setup-python/blob/6d4fd22b20465ccc0f7354476588e8df7c9ca0e0/LICENSE) |
| `actions/upload-artifact` | `v7.0.2` | [`cf430e030ddbb5b0abf93d22962f4752f3646cd9`](https://github.com/actions/upload-artifact/commit/cf430e030ddbb5b0abf93d22962f4752f3646cd9) | [MIT](https://github.com/actions/upload-artifact/blob/cf430e030ddbb5b0abf93d22962f4752f3646cd9/LICENSE) |

For an update, verify the official release tag resolves to its commit, inspect
the release notes and action manifest, then change the SHA and human-readable
version comment together. Their Node 24 manifests target current hosted runners;
self-hosted runner qualification is outside this matrix. No third-party source
is vendored by this change.

This workflow does not build a VST3 adapter, a device-audio standalone product,
native UI, signed installer, or measured scanner/AO-28/Leslie model. It supplies
no DAW/device qualification, physical-fidelity result, or real-time deadline
guarantee. Those retain their separate [M0-M9 acceptance gates](PLAN.md).
