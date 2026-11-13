# Assignment 35 — native test portability

Canonical agent `/root/w06_a35_native_portability`; wave 6, assignment 35 of
the current sixty-assignment session. Owned only four standalone test sources,
`docs/reviews/STANDALONE_PORTABILITY_REPAIR.md` and this note. No production,
CMake, shared status, ledger edits or commits were made by this worker.

Read standing instructions, current inherited plan/status/handoff context and
the Session concurrency/allocation contracts. Retrieved the actual Windows and
macOS job logs, inspected affected sources and the repository's existing portable
native VST3 thread-ownership implementation. Root owns integration/publication.

## Baseline and observed failures

Starting HEAD `219821dfaca6bfee8ba0905993ed8deec7a66396`, tree
`f2db7aee1d45a897273e4e68a2fefc6a2de4d433`; root's later application/benchmark
changes were present concurrently and are not identified by that HEAD alone.
The four original test sources still matched the failed hosted checkpoint.

[Native standalone run 43517181978](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43517181978):
Windows job `132202000157` reports three C4996 `getenv` diagnostics and two C4389
signed/unsigned comparisons, promoted by strict `/WX`. macOS job `132202000415`
reports unavailable `jthread`/`stop_token` types in the watchdog. Both stop before
their CTest/package stages. Retrieved decoded logs contain 175,857/434,642
characters respectively. These are actual compiler failures, not setup guesses.

## Owned source identities

All hashes are SHA-256. Source basenames resolve under `apps/standalone/`:
the first three are in `native_tests/`, concurrency is in `tests/`.

| Source | Original | Repaired |
| --- | --- | --- |
| `test_standalone_audio_device.cpp` | `a4614869017d16bf48439a8e4df9291a858b8a61a3813e41982a8c71855e6a6e` | `f4e3fa8b06d61e7605c96caed19fa19dca393fb2dbe72b1443889f18d2b4825f` |
| `test_standalone_callback_allocation.cpp` | `a48f6ff4c8590d3eb8b31870d03f0ca23a3d5ca3276273c15b5873bedd5ec3c4` | `8ff65e97e66b8d1bf61b01c5b43f09d25df44fe0f0a52375e4de073a2bc057e8` |
| `test_standalone_input_replay.cpp` | `42564eff6d7c5c9c296079ec593fc26c340415af518b366efea5752996b110af` | `b2ef12e8ee2dabe1322ea9e745f39583921b9f3bf1cedb374faa72c1533ea893` |
| `test_standalone_concurrency.cpp` | `07aee8ebe64dc3594c1438b0681c7a748488feaf639819829a978819ae6a334e` | `ded6a4be5a4376e04f211e3ca7970b01120ec04135ff9b64bb19788185a0dff0` |

`Session.cpp` remains `247c6a63dc9bb6c4e60398b17779a2d985058563b8d981c5e06426eab977f6ae`;
`AudioDevice.cpp` remains `3fda8dd26c643011e937c9ca3542a0da69eecca4716a01696412775543b44cef`;
`ScriptedInput.cpp` remains `ed6987b1b134737842028e611ed5f03ea67e9b232984284d885ca2c29d27809e`.

## Changes and executed evidence

Use SDL's existing environment reader in SDL-linked tests and `Uint32` expected
event types. Replace only the watchdog's unsupported library helper with a
nonmovable atomic-stop/`std::thread` owner. Destructor cleanup requests stop and
joins while the flag is alive; a new actual exception-unwind probe verifies
cooperative stop and completion. All previous workloads/assertions remain.

Linux GCC 14.2.0, CMake/CTest 4.4.4, Python 3.12.14; Release with sanitizers OFF.
SDL2 source remains locked at `5d249570393f7a37e037abf22cd6012a4cc56a71` (2.32.10).
Inspected actual compile commands for all four tests: every normal strict warning
and `-O3 -DNDEBUG -std=c++20` is present. No warning suppression was introduced.

CWD `/workspace/scratch/5ba97739b54c`; the exact build/CTest commands are retained
in the [repair report](../../reviews/STANDALONE_PORTABILITY_REPAIR.md).
Build exited 0. Filtered canonical CTest with `--no-tests=error -V --parallel 2`
passed **4/4 suites**, zero failures, **2.94 seconds**. Explicit SDL dummy
environment comes from the maintained CTest properties.

| Executable in `build-native-app/apps/standalone/` | SHA-256 |
| --- | --- |
| `test_standalone_audio_device` | `99e254abc9ba0060c755bcb76e4a2655efae92ac7ef5fc1af670a79def243836` |
| `test_standalone_callback_allocation` | `217420e2c3fcbb1ea87214bf4473f0a81863c0024e24f28bc2ef9d06272e8297` |
| `test_standalone_input_replay` | `2ec777d581d4696e2b7fbdf4b432c4e6123d26f4dc18809435c5de019662bc94` |
| `test_standalone_concurrency` | `871ecff33127c8cffbae7d77239a2b059fc2ecb032554b3138ec6cb091fbe781` |

Retained scratch logs: `a35-portability-build.log`, `a35-portability-tests.log`.
The latter hashes to `c3d33fd25c3ee95144834195bcb55a53458719d9b0eecaed24d7d49d5d782843`.
Observed original-callback allocations/deallocations remain zero over 39 actual
callbacks with 936 positive calibration allocations/frees. Device/replay and
all concurrency recovery totals are retained in the repair report. The unwind
probe reports stop observed and worker joined. Final whitespace/link checks pass.

## Handoff and limits

Files are stable for root's exact-source integration. Publish the repair with
the current accepted app/benchmark work and inspect a real hosted rerun. Windows
and macOS repaired compilation/execution remain unrun at this handoff; the earlier
failed run must not be relabeled successful. No physical device, deadline,
native accessibility or fidelity claim follows. Earlier concurrency TSAN results
retain their earlier source identity; this worker did not rerun that configuration.
