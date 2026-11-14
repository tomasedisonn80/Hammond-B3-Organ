# A08 - Optional RtMidi backend API and source audit

## Actual assignment and owned outputs

Worker: `/root/w02_a08_backend_contract`, assignment A08, wave2 of the newly
requested MIDI/UI session. This is a new assignment, not an earlier worker
recount. The assigned work is declaration/contract/source review; implementation,
build integration and independent runtime qualification belong to later workers.

Authored only:

- [`apps/standalone/MidiDevice.h`](../../../apps/standalone/MidiDevice.h)
- [`docs/MIDI_BACKEND.md`](../../MIDI_BACKEND.md)
- This assignment note.

Read repository agent rules, session scope, existing Session/AudioDevice
interfaces, the paired new `MidiInput.h`, and pinned RtMidi source. The session
started at `0f7b90037e51e101d8fa0bfe31af40209d751659`. During the declaration
check the integrator's source-review checkpoint was
`7b36cfac2565397191b3df5e07112611e7f1b0e1`. No shared status, ledger, production
implementation or locked dependency checkout was changed by this assignment.
No commit or push was performed by A08.

## Frozen public interface

The SDK-free PIMPL header declares model
`standalone-rtmidi-short-input-v1`. Public operations are main-thread-only:
compiled backend availability/name, complete port enumeration, explicit exact-name
open, connection polling, close, open/quiescent state, copied information and
lifetime diagnostics. Native types and RtMidi do not enter the public header.

The caller retains its `MidiInbox` through callback closure. A07 and A08 directly
coordinated the inbox API: bounded `push`, `pop`, atomic fault publication,
`pending`, diagnostics and quiescent reset. The backend never enters Session;
main remains the sole musical producer. Its error callback can signal a fault
without becoming an SPSC packet producer.

Enumeration has explicit limits of 256 ports and 1,024 bytes per name; failure
preserves the destination. Successful zero-port enumeration differs from a
disabled/failing backend. Open rejects empty, missing, ambiguous or changing
selection rather than silently choosing port0. Input uses one selected native
API: Linux ALSA, Windows WinMM or macOS CoreMIDI. An unavailable build implements
an explicit stub through the same interface.

Callback packets are at most three copied bytes with absolute steady-clock
arrival nanoseconds. Timestamps remain diagnostic acquisition information;
current Session delivery is callback-boundary timing. The adapter callback does
not allocate, lock, log, throw, retain an upstream vector or call UI/Session.
Reentrant input faults the epoch instead of adding an SPSC producer. RtMidi's
own vector/native work is outside the audio callback and must not be described
as allocation-free merely because the small adapter callback is bounded.

## Concrete source findings and decisions

The separately acquired RtMidi checkout was verified at
`1e5b49925aa60065db52de44c366d446a902547b` (6.0.0).
Original `RtMidi.cpp` SHA-256:
`184d775e88e5d73b079897363fb42af155122e879f0bc9254a1c7edae4eadb3c`.
Permanent primary-source links and selected official platform documentation are
retained beside the corresponding claims in the backend contract.

### Callback cancellation is not a join

`MidiInApi::cancelCallback` clears ordinary callback, user-data and flag fields;
there is no synchronization barrier. Calling it while input can execute is not
a safe substitute for stopping the backend. The frozen order is admission closed,
native close with stable context alive, entered-callback retirement, then
callback cancellation/destruction. Queue reset follows observed quiescence.

ALSA `closePort` explicitly wakes and joins its reader thread. WinMM resets/stops
and closes native input; CoreMIDI disposes ports. These paths do not establish
identical error/retirement guarantees from inspection alone. The contract
retains their distinct source evidence and requires real platform qualification.
An atomic wrapper in-flight counter alone cannot prove that an OS will never
dispatch a later callback.

### Required CoreMIDI initialization correction

`MidiInCore::initialize` allocates `CoreMidiData` without value initialization,
then writes `client` and `endpoint`, while `closePort` also reads `port`. A
construct/enumerate/destroy path can therefore inspect an indeterminate handle.
The output initializer has the same allocation pattern.

There are exactly two matching allocations, at lines1183 and1518 of the pinned
file. The integrator accepted a required preparation correction that value
initializes both `CoreMidiData` objects in a generated build copy. The build owner
must gate this operation on the original hash and exact two-match count, retain
the prepared hash and reject unexpected dependency bytes. The locked upstream
checkout stays unchanged. A08 did not apply the correction itself.

### No implicit API fallback or exception-only success

The RtMidi constructor may fall back if the requested API is not compiled.
Check availability first and the actual API after construction. The installed
error callback makes `MidiApi::error` report-and-return instead of throwing;
successful open therefore requires both open state and no error latch. Merely
reaching the next statement does not establish native success.

### Short-message-only WinMM configuration

RtMidi always allocates/queues its configured SysEx buffers during WinMM open,
even when SysEx input is ignored. Its partial allocation/unprepare failure paths
need careful handling. For this declared short-message slice the contract uses
`setBufferSize(1024, 0)` before opening plus `ignoreTypes(true, true, true)`.
The inspected loops use the zero count literally, avoiding SysEx buffer allocation
and unprepare loops while preserving ordinary short MIDI input. Windows
qualification must exercise this configuration; source inspection is not a
controller pass.

### Polled names are not durable hardware identities

ALSA names include client/port numbers, WinMM appends an enumeration index, and
CoreMIDI derives display names. The selected name is recorded exactly and checked
before/after open and on approximately 250ms polls. Missing/ambiguous names or
backend faults close the device epoch. Polling cannot guarantee detection of a
same-name replacement or unplug/replug between polls. Silence is not a fabricated
disconnect signal, and `isPortOpen` alone is not a physical-health probe.

## Concrete bounded failure and recovery contract

`is_quiescent()` is explicit; `is_open()==false` alone never authorizes inbox
reuse. After the native close returns, the adapter's in-flight wait is limited
to 250ms. A failure poisons the device, keeps quiescence false, prevents reopen,
and retains its one potentially referenced context instead of freeing memory
that a callback may still use. The one-device application reports failure and
requires process restart rather than creating replacements. Normal close frees
all ordinary resources; exceptional retention has its own observable failure
and test. Native OS call duration itself is not falsely bounded by the wrapper.

The backend never clears/reset/discards a live inbox or posts note releases.
After quiescent close, main retires the decoder epoch, discards queued packets,
posts A07's exact three scoped release commands, and observes their acknowledgment
or existing Session global recovery before activating a new epoch. UI channel0
remains independent from external owner channels1/2/3. No reconnect or held-note
resurrection is automatic.

## Executed verification

Executed a declaration-only strict C++20 compile with both new headers:

```sh
g++ -std=c++20 -Wall -Wextra -Wpedantic -Wconversion \
  -Wsign-conversion -Wshadow -Werror -Iinclude -Iapps/standalone \
  -x c++ -fsyntax-only -
```

The supplied translation unit included `MidiDevice.h` and `MidiInput.h`, asserted
noncopyable/nonmovable device semantics, and checked the frozen port capacity,
inbox capacity and guard-time constant. Compiler: **GCC14.2.0**, Debian
`14.2.0-19`. Result: exit0, no diagnostics. This validates declarations together;
it is not a link, backend execution or hardware test.

Checked both authored files for trailing whitespace and all relative Markdown
links for target existence. Result: pass. Inspected the paired A07 header on disk
after coordination; the agreed inbox names match.

At the final declaration check:

| Authored file | SHA-256 |
|---|---|
| `MidiDevice.h` | `53ca2f5483c4574f0589c2d511f3fce2d68603671b4b89638f653a93a82c8942` |
| `MIDI_BACKEND.md` | `e01291c94a753de0e75791f99b4f220588b3c09651652d0decaedfc89c3bde11` |

No native MIDI implementation, port opening, physical controller, platform close,
audio callback, visual comparison or timing acceptance was run by A08. Those
gates remain explicitly open for implementation and later independent workers.

## Next implementer handoff

Implement `MidiDevice.cpp` against these declarations and A07's frozen inbox.
The build owner prepares/hash-checks the CoreMIDI correction and optional native
dependency. Preserve an SDK-free unavailable stub. Independent acceptance must
exercise failed/ambiguous selection, error-latched open, borrowed-message copying,
overflow/reentrancy, close-before-cancel, failed-close poison, quiescent reset,
ordinary resource cleanup and no automatic reconnect. Main integration then
proves scoped musical retirement and control-state reconciliation through the
actual Session/UiModel paths. Physical hardware and every platform keep their
own observed qualification records.
