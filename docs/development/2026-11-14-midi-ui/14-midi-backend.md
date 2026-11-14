# A14 — optional MIDI backend implementation

Actual worker: `w03_a14_backend_implementation`, wave 3 of the separate
`2026-11-14-midi-ui` session. This is the original A14 assignment, including its
continuation after the integrator checked an inconsistent live-worker listing.

## Ownership and source

Owned paths: `apps/standalone/MidiDevice.cpp` and this note. Headers, frozen
contracts, dependency preparation, CMake, shared status files and commits belong
to the integrator or their assigned workers. No other repository file was edited
by A14. The observed repository HEAD was
`7b36cfac2565397191b3df5e07112611e7f1b0e1`; this concurrent worktree was not a
frozen whole-project qualification snapshot.

Read `AGENTS.md`, the current README/status/next-step/log entry points, plan and
atlas review pointers, the current consolidated MIDI/UI atlas review,
[scope](../../MIDI_UI_SCOPE.md), [input contract](../../MIDI_INPUT.md),
[backend contract](../../MIDI_BACKEND.md), [dependency build](../../RTMIDI_BUILD.md),
and both frozen MIDI headers. Inspected the pinned RtMidi constructor fallback,
error/callback registration, enumeration, native open and native close paths.
No physical model, parameter identity or stored control format changes.

| Tested source | SHA-256 |
|---|---|
| `MidiDevice.cpp` | `48ee8dbe72a1a243fcc3bc1037df782690894cb26ef2291ba253611b48bfc324` |
| `MidiDevice.h` | `53ca2f5483c4574f0589c2d511f3fce2d68603671b4b89638f653a93a82c8942` |
| Concurrent `MidiInput.cpp` | `32e135e84a870dc0e7d6cd9f5a9804b6c75031d4b2fd8dcfcf4d0959bd210802` |
| `MidiInput.h` | `00a1e6d43f8db1721f7042b6c37b081f192dd85f55dc1bb999c81ee0a4014038` |
| Prepared RtMidi 6.0.0 source | `240705532b17e593dc17434259233a586c9136808724124f1d3af649eadea17a` |

## Implemented behavior

`HAMMOND_HAS_RTMIDI=1` enables the selected platform API: ALSA, WinMM or
CoreMIDI. Undefined or zero builds the same public class as an unavailable,
quiescent stub without including RtMidi or a native SDK. Unsupported platforms
also report unavailable. Capability/name accessors do not construct a client.
The adapter uses `<RtMidi.h>` as the ordinary include seam for independent
synthetic fault tests; no public test API was added.

Enumeration checks the compiled API set before construction and actual API
after construction. It preserves the destination on every failure, retains
exact names/order, and rejects the whole query for more than 256 ports or any
empty, over-1,024-byte or embedded-NUL name. Missing and duplicate selected names
cannot silently choose port zero or another API.

Open rejects invalid current state, exhausted generation and a nonempty/faulted
inbox before native work. It resolves the exact name again, installs error and
input callbacks, ignores SysEx/clock/sensing, and selects zero WinMM SysEx
buffers before activation. It checks index/name immediately before open and
checks native state, API, errors, complete name uniqueness and the original
index afterwards. Only a completed success advances generation. Failed
activation faults and closes that inbox epoch; the backend never clears it.

The input callback uses a stable PIMPL context, atomic entry accounting and a
nonblocking producer flag. An overlapping callback faults the epoch without
becoming another inbox producer. Complete one-to-three-byte messages are copied
into `MidiInbox`; null/empty/oversize payloads are counted and filtered. Checked
absolute `steady_clock` nanoseconds are diagnostics. The callback does not
allocate, format/log text, lock, wait, retain the vector, or enter UI/Session.
Error callbacks only update atomic state/counters and signal the inbox fault.
Atomic diagnostics saturate; they remain independent observations, not a
transactional snapshot.

Main-thread polling observes native state, inbox/backend errors and the current
unique exact-name set. It closes on fault or absence and never reconnects.
Names remain topology-dependent selection tokens, with the polling limitations
in the frozen contract.

Close shuts admission and faults the attached inbox before native close. The
context remains alive while close runs and while entered callbacks retire.
The wrapper wait begins after native close returns and is limited to 250 ms;
the OS close itself has no adapter-controlled bound. Only then can callback
cancellation and backend destruction occur. Ordinary close destroys resources
and detaches the inbox. An observed close exception/error, surviving native-open
state or callback timeout poisons the device, keeps `is_quiescent()` false and
refuses reopen. Destruction retains that one PIMPL only for this exceptional
case. Main must retain the caller-owned inbox too and require process restart.
This implements the contract's failure policy; it does not independently prove
every driver's native callback-retirement guarantee.

## Executed verification

Toolchain: GCC 14.2.0, C++20, CMake 4.4.4 at
`/home/agent/.cache/uv/archive-v0/kvsqq5-iHdbf13RC/cmake/data/bin/cmake` on Linux.
The isolated real build used ALSA 1.2.14 headers/library from
`/workspace/scratch/641ca55ce6de/native-sysroot/usr`. It invoked
`hammond_add_rtmidi` against `/workspace/scratch/cd4bd06ce68f/rtmidi`, verified
upstream commit `1e5b49925aa60065db52de44c366d446a902547b` offline and created a
fresh prepared copy with the two reviewed CoreMIDI zero-initialization fixes.
No unpatched dependency source was compiled.

| Executed check | Observed result |
|---|---|
| Undefined macro, no SDK: compile `MidiDevice.cpp` with repository strict warnings | Pass, including `-Werror`. |
| Enabled adapter: compile against prepared RtMidi header with strict warnings | Pass. |
| Isolated Release stub executable using `MidiDevice.cpp` and `MidiInput.cpp` | Build/link/run pass without SDL, RtMidi or a native MIDI SDK. |
| Fresh prepared-source ALSA Release library and adapter executable | Configure/compile/link/run pass. |
| Stub list/open | Both fail explicitly as unavailable; destination, empty/fault-free inbox and generation zero are preserved. |
| Actual ALSA list/open with absent `/dev/snd/seq` | Both report actual sequencer-client construction failure; enumeration does not fabricate success with zero ports. |
| Actual preactivation failure lifecycle | State is Faulted; backend-error count is one for the failed device open; generation remains zero; inbox is unchanged; device remains quiescent. |
| Both smoke paths: closed poll and repeated close | Closed poll fails with a diagnostic; two closes leave the object quiescent with zero close errors. |
| Explicit `HAMMOND_HAS_RTMIDI=0`, ASan/UBSan | Build/run pass with `detect_leaks=0` and both sanitizers set to halt on error. |
| Fully instrumented prepared ALSA + adapter, ASan/UBSan | Build/run of the same real unavailable-sequencer path passes with `detect_leaks=0`. |
| Initial `detect_leaks=1` stub run | Environment failure: LeakSanitizer reports that it cannot run under ptrace. This is retained as a blocked leak gate, not a leak pass. |

The real dependency prints its ALSA/RtMidi constructor diagnostics on the main
thread before our code can install an error callback. The adapter catches the
exception and returns, for example, `MIDI input enumeration failed:
MidiInAlsa::initialize: error creating ALSA sequencer client object.`

Temporary smoke inputs and builds are under
`/workspace/scratch/cd4bd06ce68f/midi-backend-check-a14`. Its CMake project
compiles only the two current MIDI implementation sources and `smoke.cpp`,
sets C++20 plus the repository warning flags, and conditionally calls the
reviewed dependency helper. The harness checks every behavior listed above.

Commands were run from the project root; `cmake` below denotes the executable
identified above and `check` is the temporary smoke source directory:

```sh
cmake -S ../midi-backend-check-a14 -B ../midi-backend-check-a14/off -DCMAKE_BUILD_TYPE=Release
cmake --build ../midi-backend-check-a14/off -j3
../midi-backend-check-a14/off/a14_smoke

cmake -S ../midi-backend-check-a14 -B ../midi-backend-check-a14/on \
  -DCMAKE_BUILD_TYPE=Release -DA14_NATIVE=ON \
  -DALSA_INCLUDE_DIR=/workspace/scratch/641ca55ce6de/native-sysroot/usr/include \
  -DALSA_LIBRARY=/workspace/scratch/641ca55ce6de/native-sysroot/usr/lib/x86_64-linux-gnu/libasound.so.2.0.0
cmake --build ../midi-backend-check-a14/on -j3
../midi-backend-check-a14/on/a14_smoke
```

The `asan` build repeats the enabled configure with Debug and
`-DCMAKE_CXX_FLAGS=-fsanitize=address,undefined\ -fno-omit-frame-pointer` plus
`-DCMAKE_EXE_LINKER_FLAGS=-fsanitize=address,undefined`. The explicit-zero smoke
was compiled directly with the same sanitizers and `-DHAMMOND_HAS_RTMIDI=0`.
Successful sanitized executions used `ASAN_OPTIONS=detect_leaks=0:halt_on_error=1`
and `UBSAN_OPTIONS=halt_on_error=1` after retaining the leak-check environment
failure above.

## Remaining acceptance

The next independent worker should inject enumeration/open/close faults through
the header seam, count ordinary constructor/destructor balance, verify callback
bytes/timestamps/contention and epoch failure, and prove close-before-cancel
ordering and exceptional context retention with synthetic hooks. The integrator
owns CMake integration and the main-thread inbox/decoder/release lifecycle.
Successful native input, physical controllers, hotplug, latency, Windows/macOS
execution and a leak-capable runner remain unqualified. This no-device Linux
execution is not a physical MIDI pass or whole-application acceptance.
