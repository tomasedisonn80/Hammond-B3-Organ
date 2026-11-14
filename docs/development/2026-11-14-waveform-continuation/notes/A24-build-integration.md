# A24 — Waveform build integration

Actual worker `/root/w04_a24_build_integration_review`, wave 4 of this waveform
continuation. Owned only this note,
[WAVEFORM_BUILD_INTEGRATION.md](../../../reviews/WAVEFORM_BUILD_INTEGRATION.md)
and [a24-build-integration.json](../reports/a24-build-integration.json).
No source, CMake, workflow, fixture, shared status, manifest, index or commit was
changed by A24; no nested worker was created. Read the standing instructions,
complete M0–M9 plan, active scope/checkpoint, current handoffs, A12 build plan
and relevant probe/runner/build/install sources. Earlier atlas readings remain
their original workers' evidence.

## Frozen source and setup

Waited for the integrator's explicit merge confirmation before configuration.
Base HEAD was `0881d1f4c5a26ce9c75dda7a3adde46382e5ab6b`, with a dirty waveform
overlay identified by **82 exact file hashes**. These hashes and HEAD remained
stable throughout this task's build and smoke. The report retains every input
hash, exact command array, generated graph check and raw evidence identity.

Work stayed in sibling `a24-build-integration/{core-on,testing-off}`. Reused
CMake 4.4.5 and Ninja `1.13.2.git.kitware.jobserver-pipe-1` from the existing
`/workspace/scratch/1bb6ee17ad7e/build-tools/` roots; compiler was `/usr/bin/g++`
14.2.0 and Python was 3.12.14. Both configurations disabled standalone, VST3,
MIDI and sanitizers and kept SDK root entries empty. No network acquisition or
SDK build occurred. The shared native cache was read only to confirm its
standalone-ON/SDL2 configuration differs from this independent core-only gate.

## Commands and actual results

Expanded argument arrays, working directory and elapsed times are in the report.
The effective reproduction commands, from the source checkout, are:

```sh
a24_cmake=/workspace/scratch/1bb6ee17ad7e/build-tools/cmake/data/bin/cmake
a24_ctest=/workspace/scratch/1bb6ee17ad7e/build-tools/cmake/data/bin/ctest
a24_options=(-S . -G Ninja -DCMAKE_MAKE_PROGRAM=/workspace/scratch/1bb6ee17ad7e/build-tools/bin/ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER=/usr/bin/g++ -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_BUILD_VST3=OFF -DHAMMOND_ENABLE_MIDI=OFF -DHAMMOND_ENABLE_SANITIZERS=OFF -DPython3_EXECUTABLE=/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3)
"$a24_cmake" "${a24_options[@]}" -B ../a24-build-integration/core-on -DBUILD_TESTING=ON
"$a24_cmake" "${a24_options[@]}" -B ../a24-build-integration/testing-off -DBUILD_TESTING=OFF
"$a24_cmake" --build ../a24-build-integration/core-on --target hammond_rotary_waveform_probe --parallel 2 --verbose
"$a24_ctest" --test-dir ../a24-build-integration/core-on -C Release --no-tests=error -V -R '^python_test_rotary_waveform_(acceptance|report_admission)$' --output-junit /workspace/scratch/e3cacb90cc81/a24-build-integration/waveform-ctest.xml
```

Both fresh configurations passed, in 0.572/0.477 seconds. Only the probe and
its core/generated dependencies were built, passing in 11.279 seconds.
**2/2 CTests passed in 3.47 seconds**, including all **nine admission methods**.
The smoke completed four rates/24 partitions, 98,328 native frames, 360 events,
163,880 exact scalar comparisons and 64 selected Decimal path checks. Maximum
normalized error was `1.20659368074701270776e-9`. Its 2.940-second wrapper and
2.377-second native child retained 302,538 bytes, within the stated bounds.

## Integration findings

All 18 generated-configuration checks pass. Core/test globs include the new
sources once; only the two renderer suites receive private `src/`; only the
BUILD_TESTING probe lists the independent oracle. Exact target-file smoke
environment, Release report directory, 120-second smoke and 30-second admission
timeouts resolve correctly. The full target depends on the probe and uses
1,500 seconds; ordinary `check` excludes full execution. OFF configuration
omits test-only targets. PrivateProject copies probes and reference; install
payload helpers remain unchanged. No installer suite was repeated.

A24 found missing ordinary smoke upload directories. The integrator added both
Release and sanitizer paths before freezing source. Structured workflow review
confirms prior job fields and artifact paths preserved, plus an unconditional
Linux Release full job with 35-minute job/30-minute step limits and raw receipt
uploads. This is workflow inspection, not hosted success or branch-protection
verification.

The independent source-binding audit verified 25 actual core/probe command
records, all required rotary sources, stable metadata/executable hashes and no
unsafe floating flags. C++20/strict warnings remain intact; contraction uses the
compiler default. Metadata alone does not prove rebuild freshness; this task
observed the fresh compile/link. Numerical full-mode metadata admission was
checked without invoking full waveform rendering.

## Evidence identities and limits

| Item | SHA-256 |
| --- | --- |
| Root CMake | `167342e2e0a406c4cb3c684abada08cc2cfb98c875144bf4c15f0405febfa4ed` |
| Repaired CI | `7429018fbe0f372fdac6f9d89f524e83b906926146abf64d4073be51a43fa7b5` |
| Probe executable | `3c057118d714f5131d1d8c01278d441830fc218acde3044c9a0e55f0cbe037a3` |
| Smoke qualification receipt | `4f8142939447024e1650b9b297cd8ff092e148c0af1b29acebd3a55c73b834d0` |

Raw logs and receipts remain under `../a24-build-integration/`; the exact run is
`core-on/rotary-waveform/Release/smoke/smoke-20261114T224717.116013Z-aa6b6838/`.
This review did not run full rendering, C++ behavior suites, installers, hosted
CI, Windows/macOS or sanitizers. A14's grid was admitted as retained evidence.
Root owns the ongoing frozen full run, its timing/artifact review and subsequent
published-source CI checks. R5/R6, device and physical gates remain separate.
