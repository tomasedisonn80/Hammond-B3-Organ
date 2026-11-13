# Assignment 22 — Session concurrency

Actual worker: `/root/w04_a22_session_concurrency`, wave 4, 13 November 2026.
Owned only `apps/standalone/tests/test_standalone_concurrency.cpp`,
`docs/STANDALONE_CONCURRENCY.md`, and this report. No production/CMake/shared-status
edit, commit or publication. Root owns integration and the final frozen checkpoint.

Read AGENTS, current status/handoffs, the standalone Session contract and runtime,
core ownership/control implementation, and assignments 16/17 acceptance scope.
The relevant atlas engineering basis is inherited from the Session contract
(pp. 379–396, 425, 433–434, 442, 450, 453); no physical model change is made.

## Result

The maintained [concurrency gate](../../STANDALONE_CONCURRENCY.md) passes against
actual Session/core calls. Free-running SPSC overlap, two independent readers,
32 full storage laps, 64 rejection/overflow epochs, and 16 active-callback
overflow requests exercise complete control coherence, literal FIFO sequence
identity, clock/hold/diagnostic consistency and exact command outcome accounting.
Final quiescent Panic/drain/stop checks leave every held key/pedal clear.
Finite publication exhaustion verifies 256 unchanged failed-read destinations.

Final Release CTest: **1/1 passed**, 0.12 seconds, total 0.13.
Final full-core/Session TSAN CTest: **1/1 passed**, 0.96 seconds, total 0.97,
zero race diagnostics. Preliminary passes preceded the active-overflow/watchdog
additions; the figures and hashes here identify the final test source.
No production defect was observed or correction requested.

| Final reader | Release coherent / busy | TSAN coherent / busy |
| --- | ---: | ---: |
| Free reader 0 | 1,649 / 112 | 2,469 / 25 |
| Free reader 1 | 1,747 / 160 | 2,453 / 34 |
| Recovery reader 0 | 73,943 / 247 | 54,519 / 412 |
| Recovery reader 1 | 73,465 / 249 | 48,017 / 988 |
| Active-overflow reader 0 | 87,902 / 29 | 34,808 / 204 |
| Active-overflow reader 1 | 129,921 / 47 | 22,926 / 34 |

Both executions accepted 14,976 recovery commands: 3,456 applied, 32 consumer
rejections and 11,488 discarded, including 3,072 raced admitted note-ons. They
observed 64 immediate rejects, 32 full queues and 3,104 RecoveryPending returns.
All 16 additional QueueFull calls occurred inside active callback intervals;
all 16 recoveries followed that callback. Their 4,176 accepted commands reconcile
as 80 applied plus 4,096 discarded. Free-running results were 8,192 restores,
173/305 callbacks and 8,179/8,192 posts observing active callback intervals
(Release/TSAN). Exact schedule counts are observations, not fixed test thresholds.

## Commands, toolchain and source identity

Working directory: `/workspace/scratch/5ba97739b54c/Hammond-B3-Organ`.
Linux x86_64; Debian GCC 14.2.0-19, CMake 4.4.4, Python 3.12.14, C++20.
Both builds retain strict `-Wall -Wextra -Wpedantic -Wconversion
-Wsign-conversion -Wshadow -Werror`; Release uses `-O3 -DNDEBUG`, TSAN uses
RelWithDebInfo plus the explicit instrumentation flags below. A tiny joined-thread
TSAN probe first compiled and exited zero. All 20 actual core/Session/test
compilation commands were then checked for instrumentation in the fresh TSAN build.

```sh
cmake_bin=/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin
"$cmake_bin/cmake" -S . -B ../build-concurrency-tests -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_BUILD_VST3=OFF
"$cmake_bin/cmake" --build ../build-concurrency-tests --target test_standalone_concurrency --parallel 3
"$cmake_bin/ctest" --test-dir ../build-concurrency-tests -R '^test_standalone_concurrency$' --output-on-failure --no-tests=error -V
"$cmake_bin/cmake" -S . -B ../build-concurrency-tsan -DCMAKE_BUILD_TYPE=RelWithDebInfo -DBUILD_TESTING=ON -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_BUILD_VST3=OFF '-DCMAKE_CXX_FLAGS=-fsanitize=thread -fno-omit-frame-pointer' -DCMAKE_EXE_LINKER_FLAGS=-fsanitize=thread
"$cmake_bin/cmake" --build ../build-concurrency-tsan --target test_standalone_concurrency --parallel 3
"$cmake_bin/ctest" --test-dir ../build-concurrency-tsan -R '^test_standalone_concurrency$' --output-on-failure --no-tests=error -V
```

Initial HEAD was `96a37a977ef22b7adf38e1a841f57ffcf32519a7`; during verification
root committed its separate runtime checkpoint `738162f0bc36f88f8c76268d04831862a8118d10`,
tree `915e55dc7c3ad022042b188498aa41f2a7f40795`, excluding this unfinished gate.
Root froze core/Session; all 41 `include/**/*.h`, `src/**/*.cpp` and Session source
hashes matched before/after. SHA-256 of their sorted `path digest\n` inventory:
`50741c1da1e413f3ab0ed13063050a77707ec88e9f69715051523701e18f572f`.

| Verified input/output | SHA-256 |
| --- | --- |
| Session.h | `0eed6c82d0cf5ffbeb0206f6f9702a93ef5a75cde6fd669b2862705dc7af84a0` |
| Session.cpp | `247c6a63dc9bb6c4e60398b17779a2d985058563b8d981c5e06426eab977f6ae` |
| Concurrency test | `07aee8ebe64dc3594c1438b0681c7a748488feaf639819829a978819ae6a334e` |
| Compiled nominal.b3p | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| Release core archive | `6d6f6a92c4f5a826dacff1314b984c1b28cdcdf021751f8d8770eab780cc9dd8` |
| TSAN core archive | `0c79adb24242281b7fa71fd97b0d651b3257a78c0291274671e3bf2b0f7d7f49` |
| Release executable | `42587a74efd467cc79db25c9cdbe5db046a9d58467c1fa13095ccac3c8b02575` |
| TSAN executable | `77d277b9c386b73ac36804056d9f673a1271d2568369c4d9ef4a3cb522a89cf2` |

Parallel GNU Make printed an existing `/tmp/GMfifo6` FIFO warning; both builds and
tests exited zero. No TSAN environment failure, mixed stale library/header build,
or suppressed race was used. A separate source audit explains the slot handoff,
recovery epoch and all-atomic snapshot ordering; stress does not prove every
interleaving. Backend/device concurrency, other platforms, deadline/allocation
qualification and physical fidelity are unrun here. Root should accept these
three files and rerun the focused gate at its coherent integration checkpoint.
