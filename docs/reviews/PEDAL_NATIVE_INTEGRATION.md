# Native checkpoint integration — wave 6

## Exact source and scope

The integrator qualified staged tree `b2dae50dcde294bde8e7acb7addb14456197a779`,
archived into a separate source directory before any seventh-wave integration.
The final publication differs only in Markdown result records. Its frozen
manifest records 36 accepted workers; later actual worker states belong to
subsequent publication. The external SDK is the unchanged locked 3.8.1 build 84
checkout documented in [VST3_BUILD](../VST3_BUILD.md).

GCC 14.2.0, CMake 3.31.6 and Python 3.12.14 ran on Linux x86-64. Both builds
configured from the same archive and used Release. No live header/library mix
was used. The native build-only aggregate successfully built the module, SDK
validator, controller test, common SDK ABI harness and both host tests.

## Reproduction

The paths below assume an archived source at `checkpoint-w06/source`, an
explicit verified SDK at `vst3sdk`, and the working directory above both:

```sh
cmake -S checkpoint-w06/source -B checkpoint-w06/build-default -DCMAKE_BUILD_TYPE=Release
cmake --build checkpoint-w06/build-default --parallel 2
ctest --test-dir checkpoint-w06/build-default --output-on-failure --output-junit checkpoint-w06/default-ctest.xml --output-log checkpoint-w06/default-ctest.log
cmake -S checkpoint-w06/source -B checkpoint-w06/build-native -DCMAKE_BUILD_TYPE=Release -DHAMMOND_BUILD_VST3=ON -DHAMMOND_VST3_SDK_ROOT="$PWD/vst3sdk"
cmake --build checkpoint-w06/build-native --target hammond_vst3_test_inputs --parallel 2
ctest --test-dir checkpoint-w06/build-native -C Release --verbose -R '^(hammond_vst3_validator|test_native_controller|test_native_abi|test_native_behavior)$' --no-tests=error --output-junit checkpoint-w06/native-ctest.xml --output-log checkpoint-w06/native-ctest.log
```

| Gate | Observed result |
| --- | --- |
| SDK-free full Release | 67/67 suites, zero failures/skips, 78.43 s |
| Native focused Release | 4/4 suites, zero failures/skips, 5.23 s |
| SDK module validator | 47 passed, zero failed, exit 0; diagnostics below |
| Native controller | 41,795 checks; 3,720 threshold cases; 387 string round trips; 306 rejected streams |
| Native ABI | 229,725 exact frames, 217,972 audible; maximum audio error 0 |
| Native behavior | 233,792 direct-reference frames; 81,302 post-rejection channel comparisons; 59 rollback cases |

The independently rebuilt `HammondB3.so` is 434,168 bytes with SHA-256
`d87353b237e52c8d1f91af27933493a4cf78ba4a06af4a96c9930c0ecec1d3ff`.
The 4,545-byte compiled profile has SHA-256
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.
These match the accepted individual native gates. The bundle has four files,
444,239 bytes total, including the module, SDK metadata and scoped notices.

## Retained temporary log identities

The hosted workflow retains equivalent full logs and actual bundle inventories
for each execution. Local logs were retained in the checkpoint scratch directory;
these hashes identify that observation, not an independently durable artifact.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| default-ctest.log | 8038 | `2100c9fb8feaa7f8d21c0f0b99607f61a2cd7d0458d137c15a8a71900da695bd` |
| default-ctest.xml | 33184 | `6d3661a60ec22aafdbae1fe0bb6c57c6754c0f3289c8e362a1b938a58f4b54c3` |
| native-ctest.log | 22034 | `8811b1f46c7c932ff5718b677e9990fffd2478bcad7650405b31dbc2cbbfed6e` |
| native-ctest.xml | 2797 | `6360a593933148e993393fd2737a45b9773fe3d1fd168cb137d333ce56ab8ff4` |

## Limits and next gate

The validator prints sixteen teardown diagnostics from its conflicting repeated
inactive-transition expectations and unsupported float64 test branches. It also
prints nine ERROR-labelled rejections for rates outside 44.1/48/96 kHz, which
its own process-format test does not count as failures. These messages remain
in the actual verbose output; no SDK patch or expanded format claim hides them.
The independent loaded-module harness verifies the supported balanced lifecycle.

This is a nominal instrument with actual SDK ABI evidence. It does not establish
commercial-DAW behavior, operating-system audio-device deadlines, measured B-3
or Leslie fidelity, a custom accessible editor, signing, notarization or release
licensing. Seventh-wave native concurrency, allocation, deeper curve tests and
installation have separate gates. The first hosted native Linux/macOS/Windows
execution follows publication and must be observed at its exact commit.
