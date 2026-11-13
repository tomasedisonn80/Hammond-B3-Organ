# Standalone session baseline — 13 November 2026

The new standalone session starts from remote commit
`ba0d9c9c75bd7a39152470f9f7ddb82287cb01b1`, tree
`51fd7b24d2f373a693ced8dbde0fba762a3cc434`. A separate local clone isolates this
work from the scanner session's unfinished worktree. No uncommitted scanner
files were copied into this checkout.

The root freshly configured and built the unchanged baseline on Linux x86-64
with GCC 14.2.0, CMake 4.4.4, GNU Make, and Python 3.12.14. All **77/77** registered
Release CTest suites passed, zero failures, in **44.44 seconds**. This is a core
baseline result, not standalone, device, physical-fidelity or native-VST3
qualification for the new work.

Commands, run with the repository as working directory:

```sh
cmake -S . -B ../build-baseline -G 'Unix Makefiles' \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build ../build-baseline --parallel 3
ctest --test-dir ../build-baseline --output-on-failure --no-tests=error -j 3
```

The actual CMake/CTest executables were the existing task-local 4.4.4 tools under
`/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin/`.
The new checkout and build live under `/workspace/scratch/5ba97739b54c/`.
The source PDF remains 21,248,265 bytes, 500 pages, SHA-256
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.

Six new readers freshly covered all 500 pages and inspected selected actual
rendered diagrams. Their notes and actual identities are in the
[new session ledger](../development/2026-11-13-next-phases/README.md). This
supports the [standalone scope](../STANDALONE_SCOPE.md); it does not assert that
every underlying external source or every figure has been independently checked.

An explicit exploratory acquisition of SDL2 `release-2.32.10`, commit
`5d249570393f7a37e037abf22cd6012a4cc56a71`, succeeded outside the source tree.
Its unmodified static library configured and built locally. The environment
lacks development headers for ALSA, PulseAudio, X11 and Wayland, so that build
has dummy/offscreen transport and OSS, not those real desktop backends. The
maintained optional build and independent acquisition verification remain the
next implementation tasks. No audio device or application window was tested in
this baseline step.
