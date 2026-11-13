# Native standalone test portability repair

Assignment 35 repairs test-harness portability discovered by the actual
[Native standalone run 43517181978](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43517181978)
at `219821dfaca6bfee8ba0905993ed8deec7a66396`, tree
`f2db7aee1d45a897273e4e68a2fefc6a2de4d433`. The worker retrieved both failed job
logs through the connected GitHub API; this report separates those observations
from the subsequent local repair check. Production code and warning policy are unchanged.

## Observed failures and narrow repairs

| Hosted observation | Retained correction |
| --- | --- |
| Windows job `132202000157`, MSVC 19.44.35230.0, CMake 3.31.6, Python 3.12.10: C4996 promoted by `/WX` for three `std::getenv` calls. | The three SDL-linked tests use SDL's existing `SDL_getenv` interface to inspect the explicitly selected dummy driver. No environment mutation or warning suppression. |
| The same Windows job: C4389 for two comparisons between `SDL_Event::type` (`Uint32`) and conditional SDL event enum values. | Expected event-type expressions are explicitly converted to `Uint32`. Expected values and all assertions remain the same. |
| macOS job `132202000415`, AppleClang 17.0.0.17000013, CMake 4.4.5, Python 3.12.10: its standard library has no `std::jthread` or `std::stop_token`. | The concurrency test's watchdog uses a nonmovable atomic-stop/`std::thread` owner with destructor stop-and-join, following the existing native VST3 test pattern. |

The watchdog still checks the same eight-second deadline every 20 milliseconds.
Its stop flag precedes the worker in member lifetime, tokens reference that flag,
and destruction requests stop before joining. A real exception-unwind probe
starts a worker, throws a local marker, and requires observed stop plus completed
worker execution after scope destruction. Existing producer/audio/reader workloads,
accepted-command accounting, musical expectations and numerical assertions are unchanged.

The changed sources are
[audio-device acceptance](../../apps/standalone/native_tests/test_standalone_audio_device.cpp),
[callback-allocation acceptance](../../apps/standalone/native_tests/test_standalone_callback_allocation.cpp),
[input-replay acceptance](../../apps/standalone/native_tests/test_standalone_input_replay.cpp)
and [Session concurrency](../../apps/standalone/tests/test_standalone_concurrency.cpp).
The reference ownership pattern remains in
[native VST3 concurrency](../../plugins/vst3/tests/test_native_concurrency.cpp).

## Executed repaired gate

CWD `/workspace/scratch/5ba97739b54c`; Linux x86_64, GCC 14.2.0, CMake/CTest
4.4.4, Python 3.12.14; existing coherent `build-native-app`, Release, sanitizers
OFF. Each changed translation unit's actual compile command retains C++20,
`-O3 -DNDEBUG -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror`.
SDL2 remains the pinned 2.32.10 source at
`5d249570393f7a37e037abf22cd6012a4cc56a71`; CTest explicitly selects dummy drivers.

```sh
cmake_bin=/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin
"$cmake_bin/cmake" --build build-native-app --parallel 4 --target \
  test_standalone_audio_device test_standalone_callback_allocation \
  test_standalone_input_replay test_standalone_concurrency
"$cmake_bin/ctest" --test-dir build-native-app \
  -R '^test_standalone_(audio_device|callback_allocation|input_replay|concurrency)$' \
  --no-tests=error --output-on-failure --parallel 2 -V
```

**PASS: 4/4 suites, zero failures, 2.94 seconds.**

| Repaired suite | Actual retained workload |
| --- | --- |
| Device | 15 rate/buffer combinations; 75 matrix callbacks; 59,520 frames; 31 rejected opens; two expected render faults; eight lifecycle cycles. |
| Allocation | 18 workload observations; 39 actual callbacks; 936 positive calibration allocations/frees; 1,070 main-thread posts and 777 snapshot reads; original production regions observed zero C++ allocation/deallocation. |
| Replay | 573 valid parses; 186 parser rejects; three regular loads; 12 file rejects; 51 forged plans; 116 queue actions; 13 markers; five expected runtime failures; four lifetimes. |
| Concurrency | New unwind cleanup passes; 8,192 ordered posts and 242 free callbacks; 64 recovery epochs; 14,976 accepted = 3,456 applied + 32 rejected + 11,488 discarded; 16 active-overflow rounds; 4,176 accepted = 80 applied + 4,096 discarded; 256 failed reads preserve destination. |

Scheduler-dependent callback/read counts describe this execution, not fixed
expectations. The [assignment record](../development/2026-11-13-next-phases/35-native-portability.md)
retains original/repaired source and actual executable identities. The local log
SHA-256 is `c3d33fd25c3ee95144834195bcb55a53458719d9b0eecaed24d7d49d5d782843`.

## Remaining gate

Root must publish the repaired inputs, run the actual hosted Windows/macOS jobs
and inspect their complete results; local Linux success is not a platform pass.
The original hosted failures remain valid observations of their named revision.
No production application, Session, AudioDevice, replay helper, core, parameter,
state-format or UUID change is part of this repair. Prior ThreadSanitizer evidence
belongs to its earlier named test source; this repair executes Release only.
Neither dummy callbacks nor this repair establishes physical-device deadlines,
latency, screen-reader access or instrument fidelity.
