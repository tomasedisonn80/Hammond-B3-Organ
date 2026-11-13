# Assignment 33 — SDK-free benchmark build and identity

Actual worker `/root/w06_a33_benchmark_build`; wave 6, assignment 33 of sixty.
Owns `cmake/StandaloneBenchmark.cmake`, `docs/STANDALONE_BENCHMARK_BUILD.md` and
this note. Root owns the application CMake include, shared state and publication.
No core/app/benchmark/test implementation changes or commits by this worker.
Read AGENTS, current status/next steps/handoffs, plan/source boundaries, benchmark
contracts and notes 29–30. Inspected actual generated-data dependencies in CMake.

Starting published HEAD `219821dfaca6bfee8ba0905993ed8deec7a66396`, tree
`f2db7aee1d45a897273e4e68a2fefc6a2de4d433`. Concurrent uncommitted work means that
HEAD alone is not the tested source. The identities below name the actual domain.

## Delivered contract and identities

The [build guide](../../STANDALONE_BENCHMARK_BUILD.md) records inclusion order,
SDK-free target/test/aggregate dependencies, exact manifest schema, scope and
automatic refresh rules. The module uses the actual root CMake generation input
variables, sorted safe relative paths, file SHA-256 and newline-delimited aggregate.
Both compile definitions and CTest receive identical compiler/configuration data.
Root inserted the include immediately before optional SDL. The final configuration
fallback compares exact empty text, preserving nonempty names such as `OFF`.

| Input/output | SHA-256 |
| --- | --- |
| Final module | `4e2661e495ab4b5745c8d7f676ee1531ef14be7f2119b7694972a96a366a407f` |
| Root app CMake observed after qualification | `04b5bee301b77af76cbef7fb212739e46b32ce8835e4bc5cb6f89a0ca42c42ce` |
| Benchmark source | `b9da06f92ec90bfe85ed2a4443605125fee0821dc7a9602e414526ae8dc92f80` |
| Independent acceptance script | `f3d9e1cc138034649ee65eeb860dce33a28f5139b32a523ee7cae3b59f8657b3` |
| 54-entry source aggregate | `3d37c970f157d2a5c0d13d62c77c88c035fddb3ebcdacd6ea562d24ee7092dca` |
| Generated manifest JSON bytes | `9b29de96827fde8d18a0d11e187aa0e8b62d256d4c7df8ec8032484df591deae` |
| Live and private restored Release executable | `2aa2ecbbf429608110b24f894136cc1046c0ee6c21764aa83bc4c0bfd2c7358f` |
| Compiled nominal profile | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |

Every live manifest entry was independently rehashed after execution and remained
unchanged. The complete 54-file domain is also retained in [assignment 29](29-session-benchmark.md).
Compiler: GNU 14.2.0, C++20, `-O3 -DNDEBUG`, strict project warnings; CMake/CTest
4.4.4, Python 3.12.14, Unix Makefiles `/usr/bin/gmake`, Linux/x86_64. Both SDK
options and project sanitizers were OFF. No dependency acquisition was needed.

## Actual commands and results

CWD `/workspace/scratch/5ba97739b54c/Hammond-B3-Organ`:

```sh
a33_cmake=/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin
"$a33_cmake/cmake" -S . -B ../build-a33-sdk-free -G 'Unix Makefiles' \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_BUILD_VST3=OFF
"$a33_cmake/cmake" --build ../build-a33-sdk-free \
  --target hammond_standalone_benchmark --parallel 2
"$a33_cmake/ctest" --test-dir ../build-a33-sdk-free \
  -R '^test_standalone_benchmark$' --no-tests=error --output-on-failure -V
```

Fresh actual target **PASS 1/1, 9 methods, 111 CLI invocations, 3.26 seconds**;
Python methods took 3.147 seconds. No skipped or failed tests. Logs are
`../a33-sdk-free-{configure,build,test}.log`. This closes the SDK-OFF canonical
integration gate left pending in notes 29–30, not the whole-project/native gate.

Private source `../a33-private-source` was a `git archive` of the named HEAD,
plus the stable benchmark/test/module and the same include placement. Its app
CMake SHA-256 is `084007277845dd566e45ce737e09e576abcebb27e355e7fbf31e638c5c522edd`;
all 54 inputs matched before mutation. No shared core files were touched.
An initial private Release CTest passed 1/1 in 2.80 seconds before the exact-empty
fallback clarification; all following probes used the final module above.

| Private probe | Observed result |
| --- | --- |
| Append `\n# Assignment 33 private configure-dependency probe.\n` to `tools/compile_profile.py`; invoke only `cmake --build ../build-a33-private --target hammond_standalone_benchmark --parallel 2` | Configure/generate reran automatically and benchmark recompiled. Only that entry changed; aggregate became `3f32fea8256659ccf5455488041255f3b11cbb5981f724dc0f1f168356473c24`. CTest passed 1/1, 9 methods/111 calls, 3.39 seconds total. |
| Add `include/hammond/Assignment33PrivateProbe.h` containing `#pragma once\n// Private source-inventory probe only.\n`; same plain build | CMake reported GLOB mismatch, reconfigured and recompiled; exactly one path added, 55 entries, aggregate `b2c44afe02829f4bcd46e73fb0b1373e6abe713cf111925bd78e6d712dab06f3`. |
| Delete that private header, restore exact compiler bytes; same plain build | GLOB refresh and rebuild restored the complete original manifest/54-entry identity. CTest passed 1/1, 9 methods/111 calls, 3.09 seconds total. |
| Configure `../build-a33-unspecified` from the restored private source with the same SDK/test options, omitting `CMAKE_BUILD_TYPE`; build target | Actual 100-render silence run at 48k/128, warmup 0, exited 0 and reported `configuration: Unspecified`, `ndebug: false`, and the original source aggregate. `ctest --show-only=json-v1` independently exposed matching expected configuration. |

The unspecified executable SHA-256 is
`041531ebabdbfda56f92db8fa43032bd5693d82f828709fa32d0c8a602192377`.
Command vectors and assertions are retained in `../a33-build-probes.py` and
`../a33-build-probes.json`; individual logs use `a33-private-*` and
`a33-unspecified-*`. All observed commands exited zero. No setup or production
failure occurred. No elapsed-time threshold was used to grade workload success.

## Next steps and limits

Root must run the native aggregate and hosted platform gates on its next coherent
published source. Extend the explicit generation-input list when core generation
dependencies change. Preserve the source-domain/toolchain distinction: the digest
does not identify CMake recipes, arbitrary external flags or a complete Git tree.
No native audio, hardware deadline/latency, macOS/Windows, sanitizer or physical
fidelity pass is established by this assignment's SDK-free Linux runs.
