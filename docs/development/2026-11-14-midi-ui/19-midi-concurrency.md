# A19 — MIDI inbox concurrency and allocation acceptance

Assignment: actual worker **A19**, logical wave **4**, session
`2026-11-14-midi-ui`; agent `/root/w04_a19_midi_concurrency`.
Date: 2026-11-14 UTC. Owned paths are this note and
[`test_standalone_midi_concurrency.cpp`](../../../apps/standalone/tests/test_standalone_midi_concurrency.cpp).
No production source, shared status, ledger, contract or build file was edited by
this worker. No commit or publication was performed.

## Result

The new SDK-free test builds under the project's strict Release warnings and
passes **ten repeated executions of the final source**. The same final source
passes **AddressSanitizer and UndefinedBehaviorSanitizer with leak detection
disabled**. No production defect was observed. The default sanitizer run failed
at LeakSanitizer shutdown because this environment uses ptrace; that failure is
retained below and is not a leak qualification.

The test exercises the actual `MidiInbox` and `MidiInput` implementation under
[`standalone-three-division-midi-v1`](../../MIDI_INPUT.md). It adds an independent
concurrency and allocation gate to the existing single-thread decoder/inbox
acceptance. The ordinary standalone test glob discovers it; enabling SDL, RtMidi
or a native MIDI SDK is unnecessary.

## Observed behavior

| Scenario | Concrete checks |
| --- | --- |
| Four lossless epochs | One actual producer and one actual consumer exchange **65,609 packets per epoch**, **262,436 total**. Each epoch traverses the 257-slot ring at least 255 times. A 64-packet acknowledgment window prevents scheduler-dependent overflow. |
| Payload publication and receipt order | Sixteen literal wire fixtures vary all message bytes, lengths 1/2/3, note/controller values and 64-bit timestamps. Every successful pop compares all bytes, size and timestamp with the expected sequence. Unused source bytes are poisoned; admitted short packets must contain zero tails after reuse. Zero, equal, decreasing and near-`UINT64_MAX` timestamps retain FIFO order. |
| Decoder results under transfer | Independent literal expectations check supported notes, velocity-zero Off, canonical raw Note Off velocity, pedal IDs, fixed namespaces, scoped CC123, CC11 and upper/lower/pedal parameter IDs. Unsupported system/program messages, malformed lengths/status/data, unselected channel and out-of-range pedal notes retain their distinct dispositions. Timestamp regression flags and all decoder counters are checked. |
| Concurrent invalid-size rejection | Each lossless epoch adds 256 empty/oversized pushes while transfer continues: **1,024** deliberate invalid-size attempts across the four epochs. They leave the accepted packet sequence unchanged. |
| Eight fault races | Each epoch first transfers 2,048 packets, parks 64 old packets, then rendezvous starts a producer, consumer and two independent fault-reporting threads. Backend and Disconnected reporters each signal 64 times. A finite 96-attempt producer tail mixes valid, empty and oversized messages. The consumer permits the contract's one already-admitted racing pop and verifies any returned payload. |
| Bounded fault admission | The parked tail plus even every racing attempt fits below capacity, so the fault test cannot depend on accidental overflow. Valid racing pushes must return Accepted or Faulted; invalid racing pushes must return InvalidSize or Faulted. After acquiring completion from both fault reporters, 24 further producer attempts must return Faulted and 32 consumer attempts must preserve their destination and return false. Both fault bits remain present; no overflow event is fabricated. |
| Joined retirement and new epoch | All four threads join before `reset_quiescent()`. At least 63 old packets remain for deterministic discard. The test verifies exact discard accounting, cleared fault state and an empty destination-preserving pop. A distinct 32-packet epoch then returns only its own bytes/timestamps; its lower initial timestamp must not inherit old decoder history. The queue and decoder are reused across all eight fault rounds. |
| Explicit overflow | A separate quiescent scenario accepts exactly 256 packets. Empty/oversized pushes still return InvalidSize while full. The next valid packet returns Overflow; 24 later valid/invalid attempts all return Faulted, and every pop preserves its destination. Reset discards exactly 256 packets, retains lifetime counters and allows a clean next sequence. |
| Counter truth | Expected results are collected by the producer and successful pops by the consumer, then compared after joins. Every diagnostic field is checked. Quiescent identities are `received = accepted + invalid_size + faulted + overflow` and `accepted = popped + discarded + pending`. Live observations are limited to the consumer's bounded `pending()` contract. |
| Finite execution | Every coordination/spin loop checks a 15-second steady-clock deadline; transfer/attempt counts are finite. CTest was also invoked with a 45-second process timeout. The normal transfer harness drains at most 32 packets per iteration. This is harness coverage of the declared budget, not qualification of the native application's loop. |

The racing results intentionally need not choose the same interleaving on every
execution. A pop already past its fault check may succeed; a push already past
its fault check may be accepted. Each is accounted for after quiescence. The
test does not reset a live queue or assume that independent live diagnostic
loads form one transaction.

## Allocation observation

The executable borrows the proven thread-local global C++ allocation hooks from
[`tests/test_realtime.cpp`](../../../tests/test_realtime.cpp). The probe includes
scalar/array, ordinary/aligned, throwing/nothrow and sized delete forms, retaining
the project's noinline and volatile-function-pointer calibration boundaries.
Calibration separately observes **12 allocation calls and 12 deallocation
calls** on the main thread and on every worker thread before measured work.

Only individual `push`, `pop`, `decode` and `signal_fault` calls lie inside probe
regions. Fixture preparation, thread construction/join, clock checks, yielding,
counter assertions, decoder-result inspection and logging are outside. Each
worker owns its measurement tally; the parent combines them only after joining.
Successful, empty, invalid, unsupported, inactive, overflow and faulted paths
are included. Every measured region asserts zero observed allocations and
deallocations before its result is checked.

One final Release execution recorded:

```text
Standalone MIDI concurrency: 262436 FIFO transfers across 4 epochs; 8 joined fault races; explicit capacity overflow passed.
Observed 281887 pushes, 351871 pops, 279113 decodes, 1026 fault signals: zero C++ allocations/deallocations in every measured operation.
```

The successful sanitizer execution recorded 281,887 pushes, 299,117 pops,
279,115 decodes and 1,026 fault signals with zero observed C++ allocations or
deallocations. Empty pop attempts and the admitted racing pop count vary with
scheduling; successful ordered transfer counts and all conservation assertions
remain fixed by their contracts.

This instrumentation observes global C++ allocation/deallocation calls in the
measured calling thread. It does not observe arbitrary C allocation, OS calls,
locks, elapsed callback deadlines or uninstrumented third-party backend work.

## Exact source and tools

Repository HEAD and observed `origin/main` at inspection were
`7b36cfac2565397191b3df5e07112611e7f1b0e1`, tree
`f6fe5ec715fe113d581e188834d51f9a30f52046`. The executed MIDI implementation and
test were an **uncommitted overlay**, not that commit alone.

Builds used a private 1,096-file source snapshot at
`/workspace/scratch/cd4bd06ce68f/a19-midi-concurrency-source`, with final manifest
SHA-256 `0bbacc7afd8e2bfca3724c93b4ce6ad289b49a22e1455395d074e0ce7e3540e4`.
All snapshot files were rechecked against that manifest after execution.
The fingerprint covers 56 entries: compiled project inputs and the two CMake
paths (sorted relative path + NUL + file SHA-256 + newline). Its SHA-256 is
`a0eb0499f115db580f766717bebc86c5078b83d9e66c6ec70a432bd2553429bf`.
Compiler depfiles supplied the project source/header set; system headers and
generated build files are outside this particular digest.

| Input | SHA-256 |
| --- | --- |
| `apps/standalone/tests/test_standalone_midi_concurrency.cpp` | `76a5553892ed45229a51d6ec2dd5a26677103610e492e2350a9430464e678c0b` |
| `apps/standalone/MidiInput.h` | `00a1e6d43f8db1721f7042b6c37b081f192dd85f55dc1bb999c81ee0a4014038` |
| `apps/standalone/MidiInput.cpp` | `32e135e84a870dc0e7d6cd9f5a9804b6c75031d4b2fd8dcfcf4d0959bd210802` |
| `apps/standalone/Session.h` | `0eed6c82d0cf5ffbeb0206f6f9702a93ef5a75cde6fd669b2862705dc7af84a0` |
| `CMakeLists.txt` | `797f4923b755d4ae02258540be74a887fd308f97266d9561a9958984ac0f082b` |
| `apps/standalone/CMakeLists.txt` in the snapshot | `1adc4a299dd4bc6480b0036b24cdd01ec58635b2bda58d39c77888c47e9e19d7` |
| `docs/MIDI_INPUT.md` | `19f6f616f814e295f0c4d5c88bcb9ae1c352d12ece6f7e1e9bc06664404a0a69` |
| Borrowed allocation hook source, `tests/test_realtime.cpp` | `974c826c84ba912325cdf2653138906416bf12af4b20d515360aec214ab9d9cc` |
| Inspected thread acceptance, `apps/standalone/tests/test_standalone_concurrency.cpp` | `a309882bb248add7d2dc1e6bbec679482d66d162c2d1eb54b4c455d5194355e3` |

Environment: Linux x86-64; GNU C++ 14.2.0 (`Debian 14.2.0-19`); CMake/CTest
4.4.4; Python 3.12.14. Release compilation used C++20, `-O3 -DNDEBUG` and
`-Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror`.
The Debug sanitizer build enabled the existing
`HAMMOND_ENABLE_SANITIZERS=ON` configuration with ASan and UBSan for project
targets. Optional standalone, VST3 and physical MIDI builds stayed disabled.

The final Release executable SHA-256 is
`52d66e3cb970afbde470c5750c38c1bb9e97eb32e6030f4326ede346b933cc80`;
the final sanitizer executable is
`a215fce7d1c97bb0fcc32242d063359e0db2e1b07bec980992120f6ef6b8cbd8`.

## Commands and retained outcomes

Working directory was `/workspace/scratch/cd4bd06ce68f/Hammond-B3-Organ`.
`cmake` and `ctest` below resolve to
`/home/agent/.cache/uv/archive-v0/kvsqq5-iHdbf13RC/cmake/data/bin/`.
The source snapshot contains the final test overlay and all required project
inputs; builds are outside both the repository and other workers' builds.

```sh
cmake -S ../a19-midi-concurrency-source -B ../a19-midi-release \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build ../a19-midi-release --target test_standalone_midi_concurrency -j4
ctest --test-dir ../a19-midi-release -R '^test_standalone_midi_concurrency$' \
  --repeat until-fail:10 --output-on-failure --no-tests=error --timeout 45 \
  --output-log ../a19-midi-release-final-ctest.log

cmake -S ../a19-midi-concurrency-source -B ../a19-midi-sanitize \
  -DCMAKE_BUILD_TYPE=Debug -DBUILD_TESTING=ON -DHAMMOND_ENABLE_SANITIZERS=ON
cmake --build ../a19-midi-sanitize --target test_standalone_midi_concurrency -j4
ctest --test-dir ../a19-midi-sanitize -R '^test_standalone_midi_concurrency$' \
  --output-on-failure --no-tests=error --timeout 45 \
  --output-log ../a19-midi-sanitize-ctest.log

ASAN_OPTIONS=detect_leaks=0:halt_on_error=1 \
UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1 \
ctest --test-dir ../a19-midi-sanitize -R '^test_standalone_midi_concurrency$' \
  --verbose --output-on-failure --no-tests=error --timeout 45 \
  --output-log ../a19-midi-sanitize-no-leaks-ctest.log
```

| Executed gate | Outcome |
| --- | --- |
| Initial strict Release implementation | Build passed; 10/10 repetitions passed in 2.10 s. Before final qualification the test added an explicit fault rendezvous, stricter racing result classes and lower-timestamp restart fixtures. No production repair was required. |
| Final strict Release | Build passed; **10/10 repetitions passed**, CTest summary 1/1 selected test, total 1.57 s. Individual executions were 0.09–0.22 s. These observed durations are not performance guarantees. |
| Default final ASan/UBSan run | **Failed**, CTest exit 8, after `LeakSanitizer has encountered a fatal error` and `LeakSanitizer does not work under ptrace (strace, gdb, etc)`. No leak pass is claimed. |
| Same final binary, leak detection disabled | **Passed 1/1**, 0.86 s total, with ASan/UBSan halt-on-error options and the zero-allocation observations above. |
| Build environment warning | One concurrently launched GNU Make rebuild emitted `jobserver mkfifo: /tmp/GMfifo6: File exists`; both builds subsequently completed successfully. This was not a compiler or test failure. |
| Final file checks | Both owned files have no whitespace diagnostics; all report links resolve. The first check wrapper incorrectly required status zero from `git diff --no-index` for a new file; its empty diagnostic output and expected difference status 1 passed the corrected wrapper. |

Scratch logs were retained as `a19-midi-release-final-ctest.log` (SHA-256
`428055623ba6162135bf8d0c161ec8e9a29ce1ba88a6339df5cd54546bfe6667`),
`a19-midi-sanitize-ctest.log`
(`28682f84a83cb9ea0c1f5f96d97d870943ea479d7848698828e5b9346f521ac8`), and
`a19-midi-sanitize-no-leaks-ctest.log`
(`3dc93e2b5d1673fd2f1e2776304d7efe0f9df177caab2e560e136f68fe027d20`).
The report preserves substantive outcomes even after those scratch logs expire.

## Limits and next integration step

This is finite synthetic acceptance, not a proof of every weak-memory
interleaving. Backpressure uses an acknowledgment window as required to separate
ordinary transfer from deliberate overflow. **ThreadSanitizer was not run**.
Windows and macOS were not executed. Counter saturation near `UINT64_MAX` was
not forced. The test never intentionally violates the reset-quiescence contract.
Backend close/join correctness, physical controller input, hotplug, native UI
behavior, callback latency/deadlines and full application release behavior need
their separate gates.

After execution, all compiled source/header inputs still matched the live
worktree; the sole difference among the 56 input entries was the concurrently
extended standalone CMake file. Inspection showed the added independent fake
backend test targets; this worker's test target and support-library definition
were unchanged. That later build integration is not silently folded into the
frozen source result above.

The integrator should freeze the combined MIDI/backend work, build the ordinary
test inputs, and rerun this exact filtered gate together with the decoder,
Session and backend acceptance tests. Keep a separate native/backend lifecycle
and physical-device qualification. A compatible runner is required for the
still-open LeakSanitizer and ThreadSanitizer gates. The integrator owns shared
status/next steps, session accounting and guarded publication.
