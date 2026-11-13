# Continuous integration

Two independent workflows run on pushes to `main`, pull requests and manual
dispatch. Both provide engineering verification of identified nominal software;
their results and artifacts have different scopes.

| Workflow | What it builds and checks |
| --- | --- |
| [CI](../.github/workflows/ci.yml) | SDK-free core, generated nominal profile, manual/pedal offline tools and all discovered ordinary C++/Python tests; three Release platforms plus Linux ASan/UBSan/leaks. |
| [Native VST3](../.github/workflows/native-vst3.yml) | Explicit pinned SDK acquisition, actual `HammondB3.vst3`, validator and native harnesses on three Release platforms, followed by bundle inventory/archive. |

Read [STATUS.md](STATUS.md) and the [operational handoff](PEDAL_HANDOFF.md) for
the latest identified source and remaining gates. A passing core workflow does
not establish native qualification; a passing native CTest step does not by
itself establish completion of its subsequent artifact stage.

## Core CI matrix and historical qualification

| Check | Hosted runner | Compiler / architecture | Configuration |
| --- | --- | --- | --- |
| Release (Linux GCC) | `ubuntu-24.04` | GCC / x64 | Release |
| Release (macOS AppleClang) | `macos-15` | AppleClang / arm64 | Release |
| Release (Windows MSVC) | `windows-2022` | Visual Studio 2022 MSVC / x64 | Release |
| Linux GCC ASan + UBSan + leaks | `ubuntu-24.04` | GCC / x64 | Debug, address/undefined/leak checks |

The original session's historical four jobs passed their then-registered 26 suites at `61c6ecb` in
[run 43368537860](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43368537860).
Those historical archives contain 274 Python methods per job and zero test skips.
The [final platform audit](reviews/FINAL_PLATFORM_REVIEW.md) retains exact
source/artifact identities, actual tools, complete method counts and sanitizer flags.
Those counts do not describe the newer pedal/native source or its current suite.
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
of 3.21; enabling the optional pinned native SDK requires 3.25+. The workflows
log their exact versions, Python, the compiler selection,
and the tested revision. Stable OS labels still receive image and tool updates;
this matrix does not pin every compiler or Python patch release. Runner labels
and architectures follow the [official runner inventory](https://github.com/actions/runner-images#available-images).

## What the core workflow runs

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

A green core workflow requires all three Release jobs and the sanitizer job to pass.
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
These core artifacts are diagnostics, not plugin or application packages. Native
bundle archives have their separate workflow and inventory described below.

The original portable decimal converter and Windows evidence repairs have
historical MSVC/AppleClang results at the commit above. Exact nominal `pow` comparisons,
differing `long double` precision and filesystem behavior remain relevant when
the compiler or platform changes. Fix demonstrated defects in their source/test
contract; do not suppress a job or warning to manufacture qualification.

## Actual native VST3 workflow

The [native workflow](../.github/workflows/native-vst3.yml) has separate jobs for
`ubuntu-24.04` GCC/x64, `macos-15` AppleClang/arm64 and `windows-2022` MSVC/x64.
Each is limited to 35 minutes, with matrix `fail-fast` disabled. It selects
Python 3.12 and records the actual runner, source, tools and configuration.
The SDK is acquired explicitly into the runner's temporary directory, then
verified against the checked-in
[dependency lock](../data/dependencies/vst3-sdk-lock.json). Ordinary CMake
configuration never downloads the SDK.

The workflow builds `hammond_vst3_test_inputs`, then performs one verbose CTest
run matching `^(hammond_vst3_validator|test_native_)`, with a 300-second timeout,
JUnit and complete success/failure logs. The aggregate builds the actual module,
validator and all registered native harness inputs without running them twice.
Discovery changes with the source and platform. The initial wave-7 Linux
snapshot registered eight focused entries: validator, controller, ABI, behavior,
dense automation, concurrency, selective allocation and actual install/relocation.
The selective allocation audit is Linux-only. A four-suite hosted result from
the preceding revision does not establish execution of these later entries.

After successful native tests, the workflow inventories the generated bundle,
copies it into a staging directory, verifies the copied inventory agrees, and
creates a `tar.gz` archive with an external SHA-256 record. It retains diagnostics
and bundle payloads as separate artifacts for 14 days, using names containing
the platform, architecture, source SHA and attempt. The inventory includes the
actual linked module, SDK metadata and retained notices. SDK `moduleinfo.json`
is preserved as opaque tool output; its grammar can include trailing commas.

[VST3_CI.md](VST3_CI.md) documents the bounded inventory and publication rules.
The inventory's source SHA is caller-declared; byte hashes and a supported
module header do not authenticate its build or load it in a host. Actual native
harness results supply a distinct execution record. These artifacts are unsigned
engineering bundles, with no implied DAW registration, runtime bundling,
notarization, project-wide license grant or release approval.

Native reproduction after explicit SDK acquisition/verification:

```sh
cmake -S . -B build-native -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_VST3=ON -DHAMMOND_VST3_SDK_ROOT=/absolute/path/to/vst3sdk
cmake --build build-native --config Release --parallel 2 \
  --target hammond_vst3_test_inputs
ctest --test-dir build-native -C Release -V --no-tests=error --timeout 300 \
  -R '^(hammond_vst3_validator|test_native_)' \
  --output-junit native-ctest.xml
```

Use the same platform generator/compiler choices as the core workflow and a
fresh build directory when changing them. [VST3_BUILD.md](VST3_BUILD.md) gives
the exact SDK helper commands and generated bundle-path file;
[VST3_LOCAL_INSTALL.md](VST3_LOCAL_INSTALL.md) covers explicit local staging.
Configure/build/CTest success is separate from any actual installed-host test.

### Observed pedal/native portability sequence

The following are dated records inspected during assignment 46, not a claim
that the latest `main` has already passed every gate. The
[portability review](reviews/PEDAL_NATIVE_PORTABILITY.md), current status and
development log own subsequent repair identities and results.

| Source / workflow | Observed result |
| --- | --- |
| `d7b886103f8c9d4649ffa1c35930b79808217a3d`; [core run 43411073429](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43411073429) | Linux, macOS and sanitizer jobs succeeded. Windows passed 65/67 suites; inventory's cross-API metadata comparison and a read-only Git-fixture cleanup failed. |
| Same source; [native run 43411073407](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43411073407) | Linux succeeded. macOS controller linkage lacked CoreFoundation; Windows controller round trips failed under an inherited SDK fast-math option. Other executed Windows native checks were retained rather than treated as a full job pass. |
| Repair `9403debd754f771bf39bc8cd771ecfd86c0f14d6`; [core run 43413518927](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43413518927) | Linux, macOS and sanitizer jobs succeeded. Windows passed 66/67 suites, failing final bundle stability in two synthetic cases within the inventory suite; the SDK-fixture cleanup repair passed. |
| Same repair; [native run 43413518971](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43413518971) | All four native CTest entries passed on all three platforms. Complete Linux/macOS jobs succeeded. Windows failed the later artifact inventory with `bundle changed during inventory`; no complete three-platform native workflow pass is established by this run. |
| Published wave-7 `7fb9b6121b729f46a9e18d80e8620eb21dc0847b`; [core run 43415692328](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43415692328) and [native run 43415692247](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43415692247) | Both were queued when publication and fetched local/remote identity were confirmed. This later source includes the fresh-path inventory repair and new native/install tests. Actual outcomes belong in current status and the portability review; no pass is inferred from dispatch. |

The published repair restored strict project floating-point policy without
modifying SDK dependencies, linked CoreFoundation for the controller test,
compared metadata within each stat API while checking cross-API identity/type/
size, and preserved the read-only Git fixture by moving it. The subsequent
inventory work checks fresh path metadata instead of Windows enumeration-cached
`DirEntry` metadata and retains bounded field diagnostics. It is included in
published wave-7 source `7fb9b612…`; its actual new hosted results must be recorded
before closing the remaining gate.

Do not collapse these failures into a green validator summary. The retained
actual-module SDK validation reported 47 passed, zero failed and exit 0, while
also printing 16 teardown diagnostics and nine unsupported-rate `ERROR` messages.
Only float32 at 44.1/48/96 kHz is supported. The separate SDK selftest's 51 passes
do not test the Hammond module. Later Linux allocation/TSAN/automation evidence
has its own scopes in [VST3_REALTIME.md](VST3_REALTIME.md),
[VST3_CONCURRENCY.md](VST3_CONCURRENCY.md) and
[VST3_AUTOMATION_REVIEW.md](VST3_AUTOMATION_REVIEW.md); it is not an unconfigured
native sanitizer CI job.

## Workflow trust and maintenance

Both workflows use `contents: read`, opt out of persisted checkout credentials,
and do not access repository secrets, publish releases, deploy, or write back
to the repository. Pull requests run under `pull_request`; there is no trusted
`pull_request_target` or follow-up workflow executing their code. No dependency
cache is shared between these runs. Only named diagnostics and native-artifact
paths are uploaded.

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
is vendored by these workflows. The native workflow explicitly acquires the
reviewed external SDK into temporary storage.

The core workflow remains SDK-free; the native workflow builds and tests the
actual VST3 adapter. Neither supplies a device-audio standalone product, custom
native UI, signed installer or measured scanner/AO-28/Leslie model. Actual DAW
project behavior, device deadlines and physical fidelity retain their separate
[M0–M9 acceptance gates](PLAN.md).
