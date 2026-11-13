# Assignment 16 — Session acceptance

Actual worker: `/root/w03_a16_session_acceptance`, wave 3 batch 2,
13 November 2026. Owned files:

- `apps/standalone/tests/test_standalone_session.cpp`
- `docs/STANDALONE_SESSION_ACCEPTANCE.md`
- This report.

No production, CMake, shared-status, manifest or other worker files were changed.
No commit or push was attempted; root owns integration and publication.

## Result

Implemented the durable [acceptance suite](../../STANDALONE_SESSION_ACCEPTANCE.md)
against actual `Session.cpp`. The reference explicitly supplies physical events
to a separate Engine; it does not mirror Session's queue/owner implementation.
Tests compare complete public musical state, exact stereo floats, sequence and
discard acknowledgments, and future output after errors and lifecycle changes.
Coverage includes all three rates/partitions, FIFO/restore/zero-time behavior,
overlapping owners, transactional preparation, all 256 queue slots, consumer
payload/identity/capacity rejection, finite limits and invalid buffers/clocks.

Fresh strict Release build passed. Focused CTest **1/1 passed**, zero failures,
0.34 seconds. Deterministic output:

```text
9 rate/partition scores, 3277 successful renders, 156308 bit-exact stereo samples,
6432 partition samples, 7160 coherent snapshots, 3850 accepted posts,
41 rejected posts, 20 rejected renders, 61 future-output probes
```

No production defect was observed or correction requested. Allocation and
concurrency instrumentation were deliberately left to their assigned later
gates. Publication-exhaustion tests verify failed admission, preserved output
and unchanged failed-read destination; the interface does not expose the hidden
emergency-panic state after publication becomes unavailable.

## Executed commands and identities

Working directory: `/workspace/scratch/5ba97739b54c/Hammond-B3-Organ`.
Inspected HEAD: `96a37a977ef22b7adf38e1a841f57ffcf32519a7`; Session runtime and
the standalone integration were separate concurrent uncommitted additions.
The target rebuilt core and consumers together from current source. Root must
qualify the eventual integrated frozen tree separately.

Toolchain: Linux; GCC 14.2.0; CMake 4.4.4; Python 3.12.14. Actual test flags:
`-O3 -DNDEBUG -std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror`.
Link inputs are standalone support and core static archives; no SDL/host SDK.

```sh
/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin/cmake -S . -B ../build-session-tests -DBUILD_TESTING=ON -DCMAKE_BUILD_TYPE=Release -DHAMMOND_BUILD_STANDALONE=OFF
/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin/cmake --build ../build-session-tests --target test_standalone_session -j 4
/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin/ctest --test-dir ../build-session-tests -R '^test_standalone_session$' --output-on-failure --no-tests=error -V
```

| Input/output | SHA-256 |
| --- | --- |
| `apps/standalone/Session.cpp` | `247c6a63dc9bb6c4e60398b17779a2d985058563b8d981c5e06426eab977f6ae` |
| `apps/standalone/Session.h` | `0eed6c82d0cf5ffbeb0206f6f9702a93ef5a75cde6fd669b2862705dc7af84a0` |
| Acceptance test | `9cca5470a1db91fd024590a354d20378484130ce83c79ef982139fcde406f075` |
| Frozen Session contract | `a1e02204ab660103300cbbc32daf684450358bfdeea239d30fbe81d5825ac3df` |
| Built `nominal.b3p` | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| Rebuilt `libhammond_core.a` | `6d6f6a92c4f5a826dacff1314b984c1b28cdcdf021751f8d8770eab780cc9dd8` |
| Built acceptance executable | `7f3535f1ee3d46fd4106bacf01304d3d98f2b40f4c89fdd866cfcdbf959dc1bf` |

Next: integrate this target into the coherent wave checkpoint, then execute the
separately owned resource/concurrency tests and actual native backend/UI gates.
No real-device, race-detector, deadline, hardware-fidelity or full M9 claim is made.
