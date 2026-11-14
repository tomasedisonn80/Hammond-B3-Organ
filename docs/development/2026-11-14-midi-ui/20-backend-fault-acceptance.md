# A20 — actual adapter fault acceptance through the RtMidi header seam

Actual worker: `w04_a20_backend_fault_acceptance`, wave 4 of the separate
`2026-11-14-midi-ui` session. No earlier worker is recounted by this assignment.

## Ownership and executed boundary

Owned only:

- `apps/standalone/backend_tests/fake/RtMidi.h`
- `apps/standalone/backend_tests/test_standalone_midi_backend.cpp`
- This evidence note.

The observed HEAD was `7b36cfac2565397191b3df5e07112611e7f1b0e1`; the MIDI
implementation and other concurrent work were still uncommitted. A20 neither
changed production sources/CMake nor committed, edited shared status files, or
spawned another worker. The integrator owns target wiring and publication.

Read `AGENTS.md`, the current status/next-step/plan and atlas-review pointers,
the session scope, [backend contract](../../MIDI_BACKEND.md), both MIDI
headers/implementations, and [A14's actual implementation evidence](14-midi-backend.md).
The tests compile the **actual** `MidiDevice.cpp` and `MidiInput.cpp` in separate
translation units with `HAMMOND_HAS_RTMIDI=1`. An original minimal `RtMidi.h`
implements only the dependency API used by that adapter and records native
operations. It does not replace adapter logic, inspect private members, parse
production source text, or add a production testing API. No third-party source
is copied into the fake.

This run exercised the actual host's Linux/ALSA adapter branch. The fake provides
scripted port names, native flags, callback registration, exceptions, and errors
reported through the registered error callback. It never opens an OS MIDI port.
The result qualifies wrapper behavior under those stimuli; it does not qualify
ALSA's native reader join, physical input, hotplug, latency, or another platform.

## Acceptance observed

The executable has independent `--ordinary` and `--quarantine` modes; default
`--all` runs both. Fifteen named ordinary groups passed, followed separately by
six deliberate shutdown-failure cases.

| Boundary | Executed assertions and result |
|---|---|
| Metadata and closed object | Availability/name and constructing/closing/polling an unopened object do not construct a native client. Repeated close remains quiescent. Pass. |
| Enumeration | Exact bytes/order, Unicode bytes, duplicate names, successful empty list, 256 ports and 1,024-byte name boundary; reject 257 ports, empty name, 1,025 bytes and embedded NUL while preserving the caller's destination. Pass. |
| Enumeration errors | Constructor/count/name exceptions, returned error callbacks during setup/count/name/destruction, absent compiled API and unexpected selected API all fail. No native open or alternative API attempt occurs. Pass. |
| Open admission | Invalid selection bytes, nonempty/faulted inbox and already-open object are refused without corrupting the prior epoch or another inbox. A valid 1,024-byte selection at index 255 succeeds. Pass. |
| Exact selection | Case and surrounding spaces remain significant; only one exact name is selected, including an index other than zero. Missing and duplicate exact names never open. A reopened epoch resolves its index again and advances generation only after success. Pass. |
| Activation order | Error/input callbacks and ignore-types configuration precede opening. The Linux branch does not call the WinMM-only buffer setup. Actual open-time index is observed. Pass. |
| Topology races | Changed name/index immediately before opening prevents activation; reorder, ambiguity and disappearance during opening fail, fault the epoch and retain any already-delivered prefix. Pass. |
| Actual callback copies | Exact one-, two- and three-byte packets reach the real inbox in order with zeroed unused bytes. Mutation/reallocation of the native vector after callback return cannot alter the copy. Absolute steady-clock arrivals are bounded by the surrounding test readings; NaN, negative, infinite and large RtMidi delta timestamps are ignored. Pass. |
| Callback filtering | Null, empty, four-byte and 4,096-byte messages increment transport filtering without reaching the inbox. Delivered short content is copied without decoder interpretation. The test verifies `ignoreTypes(true,true,true)` configuration; it does not pretend the fake implements RtMidi's own filtering. Pass. |
| Saturation and backend error | The real 256-packet inbox fills, the next packet faults overflow, and further callbacks stop entering it. Error callbacks from a separate thread latch the backend fault and close admission; main polling then closes the transport. Queued data, fault evidence and counters remain observable. Pass. |
| Errors that return normally | Error callbacks from configuration, pre-open name verification, native opening and post-open enumeration cause refusal even without an exception. No successful generation is fabricated. Pass. |
| Partial activation | Standard/unknown exceptions, returned errors and a closed native flag after a delivered prefix all fail. Native close precedes cancellation/destruction; the caller must reset the quiescent faulted epoch before reopening, and no prefix is replayed. Pass. |
| Close during callback activity | A worker waits on a condition-variable barrier until the fake native close is entered, invokes the actual input callback, then releases the close barrier. Both waits have two-second bounds. Admission is already closed; the original queued message remains, the late message is rejected, and cancellation follows native-close return. Pass. |
| Poll scope | Healthy unique-name reordering keeps the connection and historical index. Missing/ambiguous names, a closed native flag, API change and enumeration failures close with the appropriate disconnected/faulted result. Polling does not clear/reset the inbox or retire an independently owned decoder; another inbox is untouched. Restoring the name does not reconnect. Pass. |
| Ordinary resource lifetime | Every ordinary successful native construction has one destruction; cancellation never occurs while the fake native port is open; destruction never sees an open port. Explicit repeated close and implicit device destruction release exactly once. Pass. |

An initial overstrict test assertion expected every preactivation error to
replace `Closed` with `Faulted`. The actual immediate pre-open name-check branch
preserves the prior state when either the selection changes or its error callback
fires. The contract requires refusal, no completed generation and an untouched
preactivation inbox, without specifying a new state for that case. The final
test checks those public guarantees and requires `Faulted` after activation.
No production repair was needed or made; the initial failed assertion is not
represented as a passing run.

## Deliberate quarantine cases

Each case starts with an open device and one queued packet, induces the named
failure, and observes `Faulted`, `is_quiescent()==false`, one close-error count,
no new construction/open on retry, and a restart diagnostic. Repeated close and
the public device destructor do not retry native teardown. The caller's inbox
is intentionally retained without a reset until process exit.

| Injected failure | Native destructions after public device destruction | Cancellation attempts |
|---|---:|---:|
| `closePort()` throws | 0 | 0 |
| `closePort()` invokes the error callback and returns | 0 | 0 |
| Native-open flag remains true after close | 0 | 0 |
| `cancelCallback()` throws after native close | 0 | 1 |
| `cancelCallback()` invokes the error callback and returns | 0 | 1 |
| Native destructor invokes the error callback | 1 | 1 |

The final case has already destroyed its native object; only its callback context
and caller-owned inbox need exceptional retention. The other five retain the
native object too. Each case invokes the saved actual input callback after failed
close, then invokes both saved callbacks on a joined worker **after the public
`MidiDevice` has been destroyed**. The packet never enters the inbox; ASan/UBSan
reports no use-after-free or undefined behavior in these executions. This is a
test of deliberate poisoned-object retention, not permission to invoke callbacks
after an ordinary successful native close.

The quarantine mode deliberately leaves six inboxes and their poisoned contexts
until process exit. It must not be used as an ordinary-path leak test. CTest
should keep a separate ordinary entry with its normal leak policy and apply any
`ASAN_OPTIONS=detect_leaks=0` exception only to the quarantine entry.

## Exact commands and outcomes

Working directory:
`/workspace/scratch/cd4bd06ce68f/Hammond-B3-Organ`.
Compiler: `g++ (Debian 14.2.0-19) 14.2.0`, C++20, Linux x86_64.
The direct executable needs no SDL/RtMidi SDK, profile, or core binary; the real
MIDI source/header dependencies are found through the project includes.

```sh
g++ -std=c++20 -O2 -g \
  -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror \
  -pthread -DHAMMOND_HAS_RTMIDI=1 \
  -Iapps/standalone/backend_tests/fake -Iapps/standalone -Iinclude \
  apps/standalone/backend_tests/test_standalone_midi_backend.cpp \
  apps/standalone/MidiDevice.cpp apps/standalone/MidiInput.cpp \
  -o ../a20-midi-backend
../a20-midi-backend --ordinary
../a20-midi-backend --quarantine
```

Strict optimized build: exit 0. Ordinary run: exit 0, **15 groups passed**.
Quarantine run: exit 0, **six injected failure paths passed** in its one named
group. The last ordinary line was:

```text
PASS 15 backend groups on ALSA; actual MidiDevice.cpp with fake RtMidi API; no native driver claim
```

Instrumented build and executions:

```sh
g++ -std=c++20 -O1 -g \
  -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror \
  -pthread -fsanitize=address,undefined -fno-omit-frame-pointer \
  -DHAMMOND_HAS_RTMIDI=1 \
  -Iapps/standalone/backend_tests/fake -Iapps/standalone -Iinclude \
  apps/standalone/backend_tests/test_standalone_midi_backend.cpp \
  apps/standalone/MidiDevice.cpp apps/standalone/MidiInput.cpp \
  -o ../a20-midi-backend-asan

ASAN_OPTIONS=halt_on_error=1 UBSAN_OPTIONS=halt_on_error=1 \
  ../a20-midi-backend-asan --ordinary

ASAN_OPTIONS=detect_leaks=0:halt_on_error=1 UBSAN_OPTIONS=halt_on_error=1 \
  ../a20-midi-backend-asan --ordinary
ASAN_OPTIONS=detect_leaks=0:halt_on_error=1 UBSAN_OPTIONS=halt_on_error=1 \
  ../a20-midi-backend-asan --quarantine
```

Instrumented build: exit 0. The first ordinary execution with normal leak policy
was **blocked**, exit 1: `LeakSanitizer has encountered a fatal error` and
`LeakSanitizer does not work under ptrace (strace, gdb, etc)`. This repeats A14's
runner limitation and is not evidence of a detected product leak or a leak pass.
The explicitly limited ordinary ASan/UBSan execution with leak detection disabled
passed all 15 groups, exit 0. The separate quarantine ASan/UBSan execution passed
all six failure paths, exit 0. No CMake leak policy was disabled by A20.

The source hashes below were observed before and after the executions; the four
production files did not change during these checks:

| Source | SHA-256 |
|---|---|
| `apps/standalone/MidiDevice.cpp` | `48ee8dbe72a1a243fcc3bc1037df782690894cb26ef2291ba253611b48bfc324` |
| `apps/standalone/MidiDevice.h` | `53ca2f5483c4574f0589c2d511f3fce2d68603671b4b89638f653a93a82c8942` |
| `apps/standalone/MidiInput.cpp` | `32e135e84a870dc0e7d6cd9f5a9804b6c75031d4b2fd8dcfcf4d0959bd210802` |
| `apps/standalone/MidiInput.h` | `00a1e6d43f8db1721f7042b6c37b081f192dd85f55dc1bb999c81ee0a4014038` |
| `apps/standalone/backend_tests/fake/RtMidi.h` | `50853e167c6a2e32f1475fc1180210ba32fa33af5b6dfc6389c1a366442fe6f3` |
| `apps/standalone/backend_tests/test_standalone_midi_backend.cpp` | `c55efada22c64bc049b8b58ac8a275047ad05a131b026774fe33ff437bf1a799` |

## Integration inputs and remaining limits

The parent target should compile the test, actual `MidiDevice.cpp` and actual
`MidiInput.cpp` with private definition `HAMMOND_HAS_RTMIDI=1`, include
`backend_tests/fake` before any actual RtMidi include path, and include the
standalone/project headers. `Threads::Threads` is required. Linking
`hammond_core` is compatible but no RtMidi or SDL library is needed. Two CTest
entries should invoke `--ordinary` and `--quarantine`, each with a 15-second
overall bound. The test has its own always-enabled assertions and does not need
profile/test-support macros. The parent owns recording any integrated CMake/CTest
execution; the direct commands above are the executions performed by A20.

Remaining acceptance is explicit:

- The real RtMidi/native OS shutdown guarantee, physical controller input,
  unplug/replug, audio interaction and latency remain unqualified by this seam.
  A14's no-device real-ALSA execution remains separate evidence.
- The bounded threaded-close case guarantees an actual callback during native
  close; it does not artificially stall inside the private adapter callback.
  The 250 ms entered-callback timeout branch and producer-contention branch were
  not deterministically induced. A native driver/sequencer harness or a separately
  justified instrumentation method is needed to qualify those branches without
  weakening the production interface.
- Counter/generation saturation and an unrepresentable steady-clock reading are
  not forced through private state or replacement clocks. Their implementation
  is not replaced by this test seam.
- The ordinary construction/destruction counts detect fake native-object leaks;
  a runner capable of LeakSanitizer is still needed for an ordinary full leak
  pass. Adapter-callback allocation instrumentation and TSan were not run here.
- This adapter test checks inbox/decoder noninterference, not audible UI-versus-
  MIDI note ownership. Session/application acceptance owns that separate gate.
- Windows and macOS executions remain unperformed. The test contains the
  platform-appropriate compile selection and WinMM configuration assertion, but
  that source provision is not an executed platform pass.
