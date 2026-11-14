# Optional MIDI backend and lifecycle contract

Contract identity: **`standalone-rtmidi-short-input-v1`**. The declaration is
[`MidiDevice.h`](../apps/standalone/MidiDevice.h). This document freezes the
implementation and acceptance requirements for the new MIDI/UI continuation.
The adapter is implemented in [`MidiDevice.cpp`](../apps/standalone/MidiDevice.cpp);
the [implementation evidence](development/2026-11-14-midi-ui/14-midi-backend.md)
records the disabled-backend and prepared ALSA compilation and no-device checks.
Physical-controller qualification remains separate and unperformed here.
The [MIDI input contract](MIDI_INPUT.md),
[`MidiInput.h`](../apps/standalone/MidiInput.h), and
[session scope](MIDI_UI_SCOPE.md) own translation and musical recovery.

## Dependency and available backend

Use RtMidi **6.0.0**, upstream commit
`1e5b49925aa60065db52de44c366d446a902547b`, with the explicitly reviewed CoreMIDI
zero-initialization correction described below. Keep the original checkout
unchanged and compile a separately identified prepared source copy. Record the
license, source identities, preparation operation and resulting hash in the
dependency/build records. Do not fetch or change a dependency during ordinary
configuration. [Pinned upstream source](https://github.com/thestk/rtmidi/tree/1e5b49925aa60065db52de44c366d446a902547b)
is the API authority for this contract, not an unpinned current tutorial.

| Build platform | Selected RtMidi API | User-facing backend name |
|---|---|---|
| Linux | `LINUX_ALSA` | ALSA |
| Windows | `WINDOWS_MM` | WinMM |
| macOS | `MACOSX_CORE` | CoreMIDI |
| Dependency disabled or unsupported platform | No physical MIDI API | unavailable |

The optional dependency must not enter the core or the ordinary SDK-free build.
The disabled implementation keeps the same header and explicitly reports backend
unavailability. `backend_available()` and `backend_name()` describe the selected
compiled backend without constructing a native client. They do not attest to
devices, permissions, a running ALSA sequencer or measured latency.

Check the compiled API list before constructing the requested API, and verify
`getCurrentApi()` afterwards. The pinned constructor can fall back when the
requested API is unavailable, so passing its enum alone is insufficient. No
automatic JACK, dummy, alternative-device or virtual-port fallback is allowed.
The first slice opens one existing input port, not an application-created virtual
port, multiple devices or MIDI 2.0. [Constructor behavior](https://github.com/thestk/rtmidi/blob/1e5b49925aa60065db52de44c366d446a902547b/RtMidi.cpp#L617-L657)
defines the relevant dependency behavior.

## Public ownership and enumeration

One long-lived `MidiDevice` belongs to the application main thread. Its PIMPL
keeps RtMidi and native types out of the public header. All public methods,
including diagnostics, are main-thread operations. Enumeration, connection,
file-independent error formatting, allocation and destruction never run on the
audio callback. The caller-owned `MidiInbox` must outlive the device and every
backend callback; declare it before the device in an aggregate so reverse member
destruction closes the device first.

`enumerate_input_ports(destination, error)` constructs an ephemeral client for
the selected backend and returns exact backend names in enumeration order.
Successful zero-port enumeration is different from a failed or unavailable API.
Failure preserves the caller's vector. Reject the entire query for more than
256 ports, an empty name, a name above 1,024 bytes or an embedded NUL; do not
truncate, silently omit entries or select another API. Names are retained as the
backend's UTF-8 byte strings. Building strings and vectors here is permitted.

The chosen name is a selection token for the current enumeration, **not a
persistent hardware identity**. ALSA includes client/port numbers; WinMM normally
appends its enumeration index; CoreMIDI constructs a display name. Names and
indices can change after topology changes, and duplicate names can occur.
[ALSA naming](https://github.com/thestk/rtmidi/blob/1e5b49925aa60065db52de44c366d446a902547b/RtMidi.cpp#L2110-L2137),
[WinMM naming](https://github.com/thestk/rtmidi/blob/1e5b49925aa60065db52de44c366d446a902547b/RtMidi.cpp#L2959-L2990)
and [CoreMIDI naming](https://github.com/thestk/rtmidi/blob/1e5b49925aa60065db52de44c366d446a902547b/RtMidi.cpp#L1443-L1468)
must remain separate from physical-device provenance.

## Opening one explicit input epoch

`open(inbox, exact_port_name, error)` has the following sequence:

1. Reject an already-open or poisoned object, invalid name, exhausted successful
   generation counter, nonempty inbox or nonzero inbox fault bits without
   changing prior state. There is no implicit default/port zero.
2. Construct the selected backend outside processing; enumerate again and require
   exactly one byte-for-byte name match. Retain the matched name and index as the
   observed open-time selection.
3. Before activation, install a stable callback context and error callback,
   configure `ignoreTypes(true, true, true)`, and register the input callback.
   The pinned header recommends callback registration before opening to prevent
   a prefix entering the dependency's separate internal queue. Do not alternate
   between callback and `getMessage()` modes while live.
4. For WinMM's short-message-only scope, set the SysEx buffer count to zero using
   `setBufferSize(1024, 0)` before opening. The pinned implementation uses the
   count literally: zero avoids allocating/queueing SysEx buffers and their
   partial-open/unprepare paths. This does not disable ordinary short-message
   input. This deliberate source-supported choice still requires a Windows
   acceptance case; it is not a physical-device result.
5. Verify the chosen index's exact name immediately before opening. Open that
   index, then require the expected API, native open state, no latched backend
   error, and unchanged unambiguous index/name after opening. This narrows a
   topology race; the portable API cannot make enumeration/open atomic.
6. Only a successful completed open advances the nonwrapping lifetime generation.
   Callbacks may have arrived during activation. Main does not translate any
   queued prefix until the complete open transaction succeeds. Failed activation
   faults and closes that epoch; queued data must not be replayed on retry.

Backend errors must become a failed result with an understandable main-thread
error. Construction and allocation can fail outside processing. Installing the
RtMidi error callback changes its error behavior: the pinned `error()` calls the
callback and returns instead of throwing. Consequently, absence of an exception
is not open success; examine both the latched error and actual native state.
[Error dispatch](https://github.com/thestk/rtmidi/blob/1e5b49925aa60065db52de44c366d446a902547b/RtMidi.cpp#L759-L788)
and [callback registration](https://github.com/thestk/rtmidi/blob/1e5b49925aa60065db52de44c366d446a902547b/RtMidi.h#L329-L342)
are the retained source basis.

## Callback and timestamp boundary

The private input callback reads its stable context, enters an atomic in-flight
guard, verifies admission, and copies the complete received message through
`MidiInbox::push(span, arrival_ns)`. It never retains the upstream vector or
stores a pointer into it. Zero-length or more-than-three-byte payloads are counted
and rejected without accumulation. The callback performs no logging, string
construction, UI calls, Session calls, sleeping, locks or allocation. It must not
throw across the native callback boundary.

Use a nonblocking contention check for unexpectedly overlapping callbacks. A
second callback faults the epoch and returns instead of becoming a second SPSC
producer, spinning or waiting for the first callback. An error callback may run
on a different thread; it only records fixed atomic diagnostics and signals
`MidiInboxFault::Backend`. It never changes queue indices or rewrites callback
registration while input is live.

The timestamp is the callback's absolute `std::chrono::steady_clock` arrival in
nanoseconds, with checked representability. RtMidi's `double` delta timestamps
are not Engine frames and are not silently accumulated into an audio deadline.
The decoder preserves arrival order and reports regressing supplied timestamps;
the current Session still applies all messages at the next callback boundary.
There is no new sample-accurate scheduling, latency, clock-drift or physical
timestamp claim. [Pinned timestamp API](https://github.com/thestk/rtmidi/blob/1e5b49925aa60065db52de44c366d446a902547b/RtMidi.h#L383-L395)
documents the dependency's different timestamp quantity.

The allocation restriction above belongs to **our adapter callback**. RtMidi
itself uses vectors and native operations before calling it; that upstream input
thread is distinct from the audio render callback. Do not claim that the complete
third-party MIDI acquisition stack is allocation-free.

## Disconnection and main-thread recovery

The app calls `poll_connection(error)` about every 250ms while open and promptly
after an inbox/backend fault. It checks the fault latch/native state and queries
the current exact-name set. Missing or ambiguous selected names, failed
enumeration, a closed port, or a backend error faults and closes the transport.
Absence is `Disconnected`; API/close failures are `Faulted`. It returns false
when already closed and never reconnects on its own.

Polling is conservative best-effort detection. The pinned `isPortOpen()` is a
stored connection flag, not a universal live USB-health probe. An unplug/replug
between polls, replacement with the same name, or a driver that does not update
its listing can escape detection. MIDI silence is not treated as disconnection;
there is no fabricated heartbeat or active-sensing timeout. These limitations
remain visible in physical-controller qualification.

On fault or explicit disconnect, main stops decoding, calls `close()`, and checks
`is_quiescent()`. Only after actual quiescence may it reset/discard the inbox.
It retires the old decoder epoch and submits the three commands returned by
`midi_release_commands()` in order. These release upper internal channel1,
lower channel2 and pedal channel3, preserving UI channel0. The next epoch waits
until those releases are acknowledged or the existing Session global recovery
has been observed. No stale held notes are replayed. If Session cannot admit the
release sequence, retain its existing observable global overflow/recovery policy
rather than claiming device-only recovery.

`MidiDevice` does not own that musical sequence and never calls `Session::post()`.
It also never changes a routing configuration, decoder, UI gesture or control
snapshot. This keeps one producer and separates backend lifetime from audible
state recovery.

## Close ordering, failure and platform evidence

`close()` is idempotent and main-thread-only. It first closes callback admission
and faults an attached inbox, keeps all callback storage alive, invokes native
port close, waits for entered adapter callbacks to leave, and only then detaches
the inbox and cancels/destroys backend callbacks. Destruction follows the same
order. Queue reset is always the caller's later quiescent operation.

**`cancelCallback()` is not a shutdown barrier.** In RtMidi6.0.0 it directly
rewrites ordinary callback/user-data/flag fields. Calling it concurrently with
input can race those fields. Its invocation belongs after native closure and
callback quiescence, never before closure as a substitute for joining.
[Exact implementation](https://github.com/thestk/rtmidi/blob/1e5b49925aa60065db52de44c366d446a902547b/RtMidi.cpp#L807-L837)
is the reason for this order.

After the native close call returns, the adapter's in-flight wait is limited to
250ms. It may yield on main; it never waits on audio. Any close error, surviving
native-open state or guard timeout poisons the device, keeps `is_quiescent()`
false and prevents reopen. Keep its single possibly referenced backend/context
alive rather than freeing it. The one-device application reports MIDI shutdown
failure and requires process restart; it must not create repeated replacement
objects or reset the old inbox. If destruction cannot establish quiescence, the
exceptional context is retained until process termination. Ordinary successful
close must free its resources, and tests must distinguish this exceptional
bounded retention from an ordinary-path leak. The underlying OS close itself
has no adapter-controlled latency bound.

| Native path inspected | What the source establishes | What still needs qualification |
|---|---|---|
| ALSA | `closePort()` unsubscribes, stops its input queue, wakes the reader and calls `pthread_join` when the reader exists. | Real backend failure/hotplug, cleanup under activity and instrumented wrapper ownership. |
| WinMM | `closePort()` calls reset/stop, unprepares queued SysEx buffers, then closes. This slice's zero-buffer configuration avoids the SysEx loop. | Close result/failure behavior, callback retirement and no-buffer short input on Windows. |
| CoreMIDI | `closePort()` disposes endpoint/port and clears its stored flags. A zero-initialization correction is required even for no-open destruction. | Actual callback retirement and error behavior on macOS; stored flags alone do not prove every native error path. |

The [ALSA close source](https://github.com/thestk/rtmidi/blob/1e5b49925aa60065db52de44c366d446a902547b/RtMidi.cpp#L2310-L2337),
[WinMM close source](https://github.com/thestk/rtmidi/blob/1e5b49925aa60065db52de44c366d446a902547b/RtMidi.cpp#L2910-L2937)
and [CoreMIDI close source](https://github.com/thestk/rtmidi/blob/1e5b49925aa60065db52de44c366d446a902547b/RtMidi.cpp#L1274-L1289)
do not provide the same evidence. Microsoft documents that
[reset returns pending buffers through callbacks](https://learn.microsoft.com/en-us/windows/win32/api/mmeapi/nf-mmeapi-midiinreset)
and [close may fail while buffers remain queued](https://learn.microsoft.com/en-us/windows/win32/api/mmeapi/nf-mmeapi-midiinclose).
Apple's [port-disposal documentation](https://developer.apple.com/documentation/coremidi/midiportdispose(_:))
states disposal and an OSStatus result; it does not itself establish the stronger
all-callbacks-joined claim. An in-flight wrapper counter cannot independently
prove that a native API will never invoke a future callback. Record the native
dependency assumption and executed platform evidence instead of inventing a
universal guarantee from source inspection.

## Required prepared-source correction

Original `RtMidi.cpp` SHA-256:
`184d775e88e5d73b079897363fb42af155122e879f0bc9254a1c7edae4eadb3c`.

The original `MidiInCore::initialize` allocates `CoreMidiData` without value
initialization, then sets only `client` and `endpoint`. `closePort()` also reads
`port`, including after enumeration when no port was opened. The corresponding
output initializer has the same allocation pattern. Replace both exact
allocations with value-initialized `new CoreMidiData{}` in the generated build
copy, gated by original file hash and exact expected occurrence count **two**.
The two original occurrences are lines1183 and1518 in the pinned source.
Do not modify the locked external checkout or quietly change upstream identity.

This correction eliminates an indeterminate-handle read in the inspected code;
it does not by itself qualify native callback shutdown, every possible driver
failure or physical-device operation. Retain both original and prepared hashes,
the preparation tool identity, an exact patch description and a negative test
rejecting unexpected dependency bytes.

## Independent acceptance to complete

1. Disabled build: help/list/open distinguish unavailable from successful empty
   enumeration, preserve outputs on failure, close idempotently and remain
   quiescent without touching native APIs.
2. Admission: empty/invalid/ambiguous names, stale/reordered indices, port-count
   and name-size boundaries, API fallback, failed constructor/open and success
   with a latched error. An invalid request cannot corrupt an existing device.
3. Callback: exact short-byte copies, borrowed-vector lifetime, diagnostic
   timestamps, zero/oversize payloads, queue saturation, overlapping invocation
   fault, error-callback fault and no Session/UI entry.
4. Lifecycle: callback activity while closing, close-before-cancel ordering,
   stale-epoch discard, faulted refusal of reopen, observed quiescence before
   reset, failure quarantine, no ordinary-path resource leaks, and no automatic
   reconnect or note resurrection.
5. Full app: main remains the sole producer; UI holds survive device release;
   device holds survive focus loss; control edits share desired UI state;
   callback-boundary ordering and Session overflow remain observable.
6. Platform evidence: compile/run the selected implementation on each named
   platform, then qualify actual controller/audio hardware separately with its
   version, transport, clock, latency/dropout and unplug/replug observations.

The inspected source and declaration check are documentary engineering evidence.
Only actual implementation/test records may change the status of these gates.
