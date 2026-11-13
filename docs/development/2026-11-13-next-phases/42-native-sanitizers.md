# Assignment 42 — coherent native sanitizer audit

Worker: `/root/w07_a42_native_sanitizers`; logical wave **7**, assignment **42/60**.
A resumed turn continued this same assignment. This note and
[`STANDALONE_NATIVE_SANITIZERS.md`](../../reviews/STANDALONE_NATIVE_SANITIZERS.md)
are the only owned repository changes. Root owns integration and publication.

## Outcome and evidence boundary

The audit is complete. The qualified execution produced **92 passes and two
failed suites out of 94**, CTest exit **8**, in **222.23 seconds**. This is not a
full acceptance pass. There were no ASan/UBSan diagnostics in the complete test
log. An earlier explicit leak-runtime probe failed with the environment's ptrace
limitation; the full suite disabled leak detection and does not qualify leaks.

The immutable input was coordinator-local commit
`387275289410d12af27cf235d6e45fd91f29bafa`, tree
`0d6da163edd6531338938e12e0d393841d569a80`. Its 36,147,200-byte Git archive has
SHA-256 `12dbed72602efa4edf07e4bcb540f756f3838a77f1b4a1002fdabac912a2ea87`.
All 782 original blobs and modes remained unchanged. Later exporter, device-removal
and shared-record changes are outside this frozen execution.

## Executed setup and commands

The private audit root is
`/workspace/scratch/5ba97739b54c/a42-native-sanitizers`; `source/` contains the
extracted archive and `build/` the fresh instrumented build. CMake/CTest were
invoked by absolute path under
`/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin/`.
The external pinned SDL source was `/workspace/scratch/5ba97739b54c/SDL2`.
Reproduction requires the retained exact source snapshot and verified SDL2;
another source revision needs its own result. Equivalent commands, from that
frozen source root with these tools on PATH, are:

```sh
native_sanitizer_flags='-fsanitize=address,undefined -fno-omit-frame-pointer'
cmake -S . -B ../build -G 'Unix Makefiles' -DCMAKE_BUILD_TYPE=Debug \
  -DBUILD_TESTING=ON -DHAMMOND_ENABLE_SANITIZERS=ON \
  -DHAMMOND_BUILD_STANDALONE=ON -DHAMMOND_BUILD_VST3=OFF \
  -DHAMMOND_SDL2_ROOT=/workspace/scratch/5ba97739b54c/SDL2 \
  -DCMAKE_C_FLAGS="$native_sanitizer_flags" \
  -DCMAKE_CXX_FLAGS="$native_sanitizer_flags" \
  -DCMAKE_EXE_LINKER_FLAGS=-fsanitize=address,undefined \
  -DCMAKE_SHARED_LINKER_FLAGS=-fsanitize=address,undefined
cmake --build ../build --parallel 2
ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 \
  UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1 LSAN_OPTIONS=exitcode=23 \
  ../build/apps/standalone/hammond_standalone --help
ASAN_OPTIONS=detect_leaks=0:halt_on_error=1 \
  UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1 \
  ctest --test-dir ../build --no-tests=error --output-on-failure --parallel 2 \
    --output-junit ../ctest-junit.xml
```

The leak probe returned 23 with `LeakSanitizer has encountered a fatal error`
and the explicit ptrace hint. The full command ran only once; no success was
manufactured by repeating failed cases. Configure passed in 27.0 seconds;
build passed in 128.903 seconds. The test wrapper measured 222.285 seconds
including process setup; CTest's own total is 222.23 seconds.

Actual compile-command inspection checked all 259 translation units, including
all 176 SDL C units, for both sanitizer and frame-pointer flags. `nm -u` showed
ASan and UBSan references in core, support and SDL archives; `readelf -d` showed
both runtimes in the application. The 49,858,880-byte executable SHA-256 is
`04706e4298b10eaf8dd7e5eabfe0bffe959aab0ff58773fab4d7de0b793b94aa`.
Toolchain: GCC/G++ 14.2.0, CMake/CTest 4.4.4, Python 3.12.14, Make 4.4.1,
Linux x86-64, glibc 2.41; SDL2 2.32.10 at the locked commit.

## Retained evidence

All paths in this table are relative to the private audit root above. Full
`LastTest.log` is authoritative for successful-test output that JUnit truncates.

| File | SHA-256 |
| --- | --- |
| `configure.log` | `df2c23c74d579070ce647a9da6f92ea0b709cdee6fd3dc83316d308a5375fbba` |
| `build.log` | `6afcd602558c6e3a9a484d4318e93e527a7fafe011068aed474d3639953eef1a` |
| `ctest.log` | `f1cf64565ca22b14660e12a4a202eb677f5627baafb8b518d29c0c96be34ba86` |
| `ctest-junit.xml` | `07f0dd7f72410ec3435af68ac451507464bb5c0c8a8e898e7a2159bcabfc664c` |
| `build/Testing/Temporary/LastTest.log` | `1803d993f9a1402dd29a4dc1e4285f31045596f6dbf05c82dc8a750900d2d3b2` |
| `instrumentation.json` | `563f9db4de54cde44262363883c2bd58babf41c21417769f75916aabd3ffb6cf` |
| `lsan-probe.stderr` | `87d9a204a12098a57b4d855e48bdb90b6ede21d4714739fe19d0055611c3d450` |

`configure-argv.json`, `build-argv.json`, `test-command.json`,
`ctest-inventory.json`, `acceptance-summary.json`, archive symbol reports,
`application-dynamic.txt`, and `evidence-hashes.json` retain machine-readable
commands, counts and identities. No raw execution log or generated binary was
added to the repository by this assignment.

## Failure handoff and next action

The review records all six screenshot subcases and the 1600×1000 resize/held-note
subcase, exact assertion differences and source-supported timing explanations.
The app suite executed 18 methods/164 processes; workflows 11 methods/15
processes. Their temporary diagnostics were cleaned by the maintained fixtures,
so individual callback counts/observation timestamps were not retained. The
other ten standalone suites and all 82 non-standalone entries passed. The
state-file suite's explicit POSIX replacement-failure exclusion remains open.

Root should retain the failed result and assign the smoke/replay timing repair,
then qualify its exact repaired source. The independently reported scheduler-
sensitive concurrency concern is not closed by this run's observed positive
count. No production code, maintained test, shared ledger, commit or branch was
changed here. Actual device, platform, deadline, accessibility, distribution,
leak-runtime and physical-fidelity gates remain separate.
