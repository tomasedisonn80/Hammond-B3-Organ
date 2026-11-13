# Standalone benchmark build and source identity

[`StandaloneBenchmark.cmake`](../cmake/StandaloneBenchmark.cmake) adds the
SDK-free `hammond_standalone_benchmark` and its independent
[`test_standalone_benchmark`](../apps/standalone/tests/test_standalone_benchmark.py)
CTest suite. It is included by `apps/standalone/CMakeLists.txt` after the support
library/common test list and before optional SDL configuration. The target links
the existing support/core libraries, depends on the compiled nominal profile,
uses the project C++20/warning/sanitizer configuration and receives the portable
MinGW `wmain` link option. No dependency download or SDL initialization occurs.

## Normal build and acceptance

From the repository root, with CMake 3.21+, Python 3.10+ and a C++20 compiler:

```sh
cmake -S . -B ../standalone-benchmark-build -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_TESTING=ON -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_BUILD_VST3=OFF
cmake --build ../standalone-benchmark-build --config Release \
  --target hammond_standalone_benchmark --parallel 2
ctest --test-dir ../standalone-benchmark-build -C Release \
  -R '^test_standalone_benchmark$' --no-tests=error --output-on-failure
```

The target is available with `BUILD_TESTING=OFF`; its test registration is not.
With tests enabled, its executable is appended to the shared standalone input
list, so ordinary `check` and native `hammond_standalone_test_inputs` builds have
the binary before running CTest. The native CI regex includes this SDK-free suite.
The [benchmark contract](STANDALONE_BENCHMARK.md) defines invocation, workloads,
measurements and limits; the [acceptance contract](STANDALONE_BENCHMARK_ACCEPTANCE.md)
defines the independent CLI/accounting checks.

## Manifest construction

Configuration writes
`<build>/apps/standalone/standalone-benchmark-source-manifest.json` with schema 1:
sorted unique `entries` containing repository-relative `path` and file `sha256`,
plus `source_manifest_sha256`. The aggregate is SHA-256 of the exact UTF-8
concatenation `path:sha256\n`, including the final newline for every record.
The benchmark receives that aggregate as its compiled `_SOURCE_ID` macro.

| Included domain | Purpose |
| --- | --- |
| `src/*.cpp`, `include/hammond/*.h` | Current core sources and public contracts; both inventories track additions/removals. |
| `apps/standalone/Session.h`, `Session.cpp`, `benchmark.cpp`, `tools/CliArguments.h` | Actual measured boundary, workload/report implementation and portable CLI handling. |
| Pedal compiler, both validators, map, factory reference and both CSV readings | Actual documentary routing generation inputs from root CMake. |
| Scanner compiler, authoring graph and schema | Actual native scanner-constant generation inputs. |
| Profile compiler and authoring profile | Actual compiled nominal-profile inputs. |

There are 54 entries at the assignment-33 checkpoint. Paths use forward slashes;
absolute, parent/current-directory components, empty components and characters
outside the selected ASCII filename vocabulary reject. The checkout's enclosing
directory may contain spaces or Unicode. Manifest paths do not contain it.
File content changes trigger `CMAKE_CONFIGURE_DEPENDS`; source/header inventory
changes trigger CMake's `CONFIGURE_DEPENDS` globs. An ordinary subsequent build
refreshes the manifest and recompiles the benchmark with the new identity.

This fingerprint identifies the declared source domain. It does not authenticate
the compiler, system libraries, arbitrary extra build flags, CMake recipes or a
Git working tree. Build metadata separately reports exact compiler ID/version,
system/processor and selected configuration; an empty configuration is labeled
`Unspecified` in both executable and CTest expectations. The report's `NDEBUG`
and sanitizer fields describe their own declared scope. Retain the CMake cache,
compile commands and exact recipe/source identities when comparing measurements.

When another core module adds generated data, extend this explicit generation
input list with its actual authoring/compiler dependencies. A C++ glob cannot
discover those transitive data dependencies by itself.

## Executed qualification

Fresh Linux SDK-free Release passed **1/1 CTest suite, 9 methods and 111 actual
CLI invocations** in 3.26 seconds. Private-source probes changed one compiler
comment, then added/removed one header: plain builds regenerated the manifest,
recompiled the benchmark and restored the exact initial 54-entry identity after
restoration. The changed/restored suites passed independently. A separate build
without `CMAKE_BUILD_TYPE` produced an actual `Unspecified`, `NDEBUG=false`
report and matching CTest environment. Exact hashes, commands and observations
are in [assignment 33](development/2026-11-13-next-phases/33-benchmark-build.md).
Native aggregate execution, hosted platforms, physical devices and deadlines
remain separate gates; no elapsed-time correctness threshold is applied here.
