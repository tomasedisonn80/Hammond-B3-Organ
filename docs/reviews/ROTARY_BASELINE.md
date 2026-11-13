# Rotary session baseline qualification

On 13 November 2026 the integrator cloned the requested repository independently
of the active scanner and standalone checkouts. The starting source is commit
`96a37a977ef22b7adf38e1a841f57ffcf32519a7`, tree
`ab85e45d6776229c00fa394a540d72803daf8281`. A fresh remote ref inspection matched
that commit. An untouched `git archive HEAD` was extracted into a separate
source directory, so ongoing documentation edits did not affect the baseline.

The first configure attempt using bare `cmake` exited 127 because CMake was not
on the default PATH. Existing tools in the workspace were then located and
used without modifying another session's files. This was a setup error, not a
project test failure.

## Executed configuration

- Linux x86-64; GCC 14.2.0; CMake 4.4.4; Ninja
  `1.13.2.git.kitware.jobserver-pipe-1`; Python 3.12.14.
- Default SDK-independent Release configuration; optional native adapters not
  enabled by this gate.
- Configure, build and test commands (with the selected tools on PATH):

```sh
git archive 96a37a977ef22b7adf38e1a841f57ffcf32519a7 | tar -x -C "$BASELINE_SOURCE"
cmake -S "$BASELINE_SOURCE" -B "$BASELINE_BUILD" -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build "$BASELINE_BUILD" -j 4
ctest --test-dir "$BASELINE_BUILD" --output-on-failure --no-tests=error -j 3
```

The two destination directories were created before these commands. Actual
paths were `/workspace/scratch/c9f9d8cb3889/baseline-source` and
`/workspace/scratch/c9f9d8cb3889/baseline-build`; tool executables came from
`/workspace/scratch/1742da7072be/build-tools/bin`.

## Result and scope

**79/79 CTest suites passed**, zero failed, in 50.43 seconds. The build completed
117 Ninja steps successfully. This qualifies the named starting default source,
not new rotary code, unfinished workers' changes, native DAWs/devices or physical
instrument fidelity. Later checkpoints must identify and test their own coherent
source tree.

The supplied PDF has 500 pages, 21,248,265 bytes and SHA-256
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
The [new session](../development/2026-11-13-rotary/README.md) records its own
sixty actual assignments; none of the earlier sessions is counted again.
