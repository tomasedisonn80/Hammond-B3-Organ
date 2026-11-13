# Calibration wave 4 integration

## Reviewed source and exact scope

The first four logical waves contain 24 actual accepted workers. Their records
and identities are in the calibration session manifest; neither retained
consistency checks nor old session manifests attest new dispatches. Three
subsequent workers were running when this checkpoint was frozen.

The wave-4 source was committed as
`1c2ea32f24f978c8ce78aaf04bdb2daa23af359a`, tree
`e90b63736485766bb94636b5afa096cb5eff3b46`, then extracted with `git archive`
to a separate immutable source directory. It includes fixed policy parsing and
evaluation, the reviewed job contract, and the independently found audio and
corpus repairs. It excludes the later file-job implementation, private corpus
core refactor, readiness tool and their unfinished acceptance.

The focused gate configured Release with `BUILD_TESTING=ON`,
`HAMMOND_BUILD_VST3=OFF`, and `HAMMOND_BUILD_STANDALONE=OFF`. It built
`hammond_render` before the legacy analyzer's actual renderer integration.
GCC 14.2.0, CMake/CTest 4.4.4 and Python 3.12.14 were used on Linux x86_64.

## Frozen focused result

From the repository root, using CMake/CTest from the available task toolchain:

```sh
cmake -S /workspace/scratch/c9f3ead4c910/w4-source -B /workspace/scratch/c9f3ead4c910/w4-build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON -DHAMMOND_BUILD_VST3=OFF -DHAMMOND_BUILD_STANDALONE=OFF
cmake --build /workspace/scratch/c9f3ead4c910/w4-build --target hammond_render -j 4
ctest --test-dir /workspace/scratch/c9f3ead4c910/w4-build --output-on-failure --no-tests=error --output-junit /workspace/scratch/c9f3ead4c910/checks/w4-ctest.xml -R '^python_test_(audio_analysis|capture|capture_audio|capture_audio_admission|capture_common|capture_comparison|capture_corpus|capture_corpus_admission|capture_policy|calibration_session_records|repository_integrity)$'
```

Configure and build succeeded. The focused gate passed **11/11 CTest suites**
in **12.57 seconds**, with no failed suite. These are suites, not individual
methods. Audio admission contains 62 methods with two explicit capability skips:
Unix socket creation was denied and native Windows reparse execution requires
Windows. Corpus admission ran all 57 methods with no skips. Existing independent
sample/graph/metric suites and legacy analyzer/capture checks also passed.

The frozen manifest check with `--expected-complete 24` reports 24 complete,
three running, 33 planned and 27 distinct actual identities, with zero retained
consistency errors. Its external-dispatch-attested field remains false.

| Local evidence file | Bytes | SHA-256 |
| --- | ---: | --- |
| w4-configure.log | 697 | 82f8b3d40d5211b579173f6b57a0b469b341d5d15192567e95194ae693d5bc99 |
| w4-build.log | 2253 | b2cd34682197e487c070c0179f4d33533fe27dcd3de4a670435912c1b15d475f |
| w4-ctest.log | 1518 | 62a8b25eef445e1827183c2315509c988deb89d34b5fd2ab1dc0a314aa7915e8 |
| w4-ctest.xml | 4687 | ec34aae24a7e575f4b6c07de9ec7ca7e738bca21a2306fad41e83668114b41de |

## Repairs and boundaries

Assignment 23 reproduced a newly opened leaf descriptor leak when its directory
close failed. Root transferred descriptor ownership before fallible closes and
retained primary failure plus cleanup context; cancellation remains cancellation.
Assignment 24 reproduced unsupported-width rejection at byte 34 masking an
earlier malformed byte rate at byte 28. Root restored field-position precedence
while retaining the contract's explicit unsupported-tag priority. Both original
failures, unchanged expectations and passing regressions are retained in the
worker notes. The contracts were not weakened to match the defects.

The numerical policy tests preserve exact original policy bytes, all criteria,
closed uncertainty intervals and fail-over-inconclusive precedence. The independent
job-contract review additionally requires one admitted metadata snapshot, original
policy bytes through evaluation and final checks of every admitted artifact and
source. A compact admissible policy can become too large when pretty printed;
reserialization is not an acceptable replacement for its original byte buffer.

Sparse file-size gates, declared resource maxima, reduced-bound instrumentation
and synthetic numerical fixtures retain their stated limits. No physical capture,
clock/channel qualification, untouched final-test history, rights clearance or
instrument fidelity is established by this checkpoint. Native VST3/SDL adapters
were disabled here, and no hosted CI result follows from these local commands.

## Concurrent publication integration

After the focused freeze, remote main advanced from `5b8e241` to
`649b12c7d1faa7601fde1019e913347c65a6634a`. Root inspected and merged that
standalone device/removal/portability checkpoint without changing its ownership.
It also contains a Windows short-TEMP-path correction to the independently
injected session-checker fixture, with an assertion that the hook was reached.
The combined source is commit
`45f875d80b6cc78c89ecc8b665bf2aedf058a97c`, tree
`2dcfc0e8071cdc30d75f8fb9be340826296fcbaf`. A separate immutable source and
full SDK-free Release build qualify that composition. Configure and the complete
default build succeeded. The unfiltered CTest gate passed **96/96 suites** in
**177.43 seconds**, zero failed suites. This is the completed observed result,
not an extrapolation from the earlier focused gate.


```sh
cmake -S /workspace/scratch/c9f3ead4c910/w4-combined-source -B /workspace/scratch/c9f3ead4c910/w4-combined-build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON -DHAMMOND_BUILD_VST3=OFF -DHAMMOND_BUILD_STANDALONE=OFF
cmake --build /workspace/scratch/c9f3ead4c910/w4-combined-build -j 4
ctest --test-dir /workspace/scratch/c9f3ead4c910/w4-combined-build --output-on-failure --no-tests=error --output-junit /workspace/scratch/c9f3ead4c910/checks/w4-combined-ctest.xml
```

The source is a `git archive` of the combined commit above. Native standalone
support tests remain part of the SDK-free build; the SDL device executable and
VST3 adapter are disabled. Their native device/host outcomes remain separate.
All new code and retained failures in the wave-4 focused gate are included, while
subsequent file-job/readiness work remains excluded from this frozen result.

| Combined evidence file | Bytes | SHA-256 |
| --- | ---: | --- |
| w4-combined-configure.log | 706 | 027c9722d4d708bc62d2b0fa7b27a36509cbea2b9b0c4920f4c12139443372eb |
| w4-combined-build.log | 12141 | d0d7aba2243e3bbc34e3493dcaae4125afe7fe4b461604fdfbfbdfa77093849e |
| w4-combined-ctest.log | 11893 | 2b17a4bb6aaf7dd59659997f535da29d852cf531dc361bfa61473536e71bfcb2 |
| w4-combined-ctest.xml | 49164 | 407af8e98540956bdcbbeae6df8e327fa99f7dcfa88c61012d0b0a038ef7333d |
