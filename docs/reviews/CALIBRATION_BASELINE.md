# Capture/calibration session baseline

## Exact source and environment

- Published starting commit: `38c1fac949368fa54bd86c6c00a5997a73480f5e`.
- Starting tree: `e4ea07e5f731ba3f7ecd9ace1d37f459c9e3ea1f`.
- Source was exported with `git archive HEAD` before implementation; all build and
  test inputs came from that frozen archive, not concurrently edited checkouts.
- Linux x86-64; GCC 14.2.0; CMake/CTest 4.4.4; Python 3.12.14.
- Release, `BUILD_TESTING=ON`, `HAMMOND_BUILD_VST3=OFF`,
  `HAMMOND_BUILD_STANDALONE=OFF`. SDK-free standalone support tests are still
  registered by the actual project; these switches disable the native adapters.

## Reproduction

From a clean export of the named commit, with the stated tools on PATH:

```sh
cmake -S . -B ../baseline-build -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_TESTING=ON -DHAMMOND_BUILD_VST3=OFF -DHAMMOND_BUILD_STANDALONE=OFF
cmake --build ../baseline-build --parallel 3
ctest --test-dir ../baseline-build --output-on-failure --parallel 2 \
  --no-tests=error --output-junit ../baseline-ctest.xml
```

The actual commands used the absolute cached CMake/CTest executable because those
tools were installed but not on PATH. Configure and full build succeeded. The
complete CTest run passed **85/85 suites**, zero failures, in **61.53 seconds**.
This is the local baseline, not qualification of new calibration tools or actual
VST3/SDL devices. No new hardware capture, physical calibration or fidelity result
is supplied by this execution.

## Publication and concurrency

The scope checkpoint is published as
`08fa8de8f718584c4ee4ab3b392c779f3290289c`, tree
`f5cff4b89d19f36a73f9d2a8ddb966db487f832c`. Root used the authenticated GitHub
tree/commit/ref operations with expected head `38c1fac` and `force=false`, fetched
the result and verified exact local/remote tree equality. The local equivalent
commit `ffd0386` is preserved on a local provenance branch. These publication
observations do not establish any hosted CI outcome.
