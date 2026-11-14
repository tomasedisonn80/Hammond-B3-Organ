# Standalone MIDI input contract

Contract identity: **`standalone-three-division-midi-v1`**.
Declaration: [MidiInput.h](../apps/standalone/MidiInput.h).
This freezes the next implementation and independent acceptance work; a header
or policy is not an executed backend or physical-controller qualification.

The [MIDI/UI scope](MIDI_UI_SCOPE.md) advances M9 against the unchanged nominal
dry engine. The [full atlas review](research/MIDI_UI_ATLAS_REVIEW.md), especially
PDF pp. 151-156, 379-396 and 417-438, requires one musical owner, independent
input ownership, bounded transport, honest timing and retained parameter identity.
The [Session contract](STANDALONE_SESSION.md), adopted
[parameter bridge](PARAMETER_BRIDGE.md), [note ownership](NOTE_OWNERSHIP.md) and
[pedal ownership](PEDAL_NOTE_OWNERSHIP.md) remain authoritative.

## 1. Supported input and ownership

One selected MIDI input port supplies three configured, distinct **one-based**
wire channels. Each may be any number from 1 through 16. Invalid or duplicate
choices reject without altering the previous configuration, active state or
counters. This is three-division routing from one port; it is not arbitrary
sixteen-channel or multiple-device routing.

| Division | Default wire channel | Reserved internal origin | Accepted MIDI pitches |
|---|---:|---|---|
| Upper | 1 | Manual bus 0, channel 1 | 36-96 inclusive |
| Lower | 2 | Manual bus 1, channel 2 | 36-96 inclusive |
| Pedals | 3 | Pedal bus 0, channel 3 | 36-60 inclusive, translated to PedalId 1-25 |
| Native UI | Not a wire channel | Existing internal channel 0 | Existing UI contract |

A pitch outside its division's range is counted and ignored. There is no hidden
transposition, pitch clamp or extra foldback in the adapter. Displayed octave
names do not change numeric MIDI pitches or PedalIds. Other wire channels are
ignored and counted, including their controllers.

The decoder is inactive until `begin_epoch(routing)` succeeds. Calling it while
already active rejects without change. Routes remain immutable until
`end_epoch()` and the complete retirement sequence below. Configuration is
machine-specific setup, not part of `B3CONTROLS3`. No source/profile/state-format
or public parameter identity changes are required.

All incoming notes use **anonymous FIFO ownership** (`note_id = -1`), the
existing core policy. Repeated Note On messages create separate bounded owners;
one corresponding release removes the oldest matching owner. There is no
per-pitch deduplication. A physical key remains held while any UI or external
owner remains. Unmatched releases are accepted as no-ops by the existing core.
The core's 256 manual-owner and 256 pedal-owner limits still apply; input-queue
capacity is a different limit.

Positive velocities are forwarded as 1-127 under the existing nominal gesture
contract. They do not introduce piano-like sustained gain. Note On velocity zero
becomes an Off command. A raw Note Off's release-velocity byte is validated as
seven-bit data but canonicalized to core velocity zero. Every note command has
offset zero and retains the selected division's fixed internal namespace.
UI focus loss, resize, Help/Audio overlays, editor-bank changes and ordinary
control loads do not release these owners.

## 2. Complete messages and supported controls

The backend supplies complete MIDI messages. The adapter does **not** assemble
a running-status byte stream, buffer SysEx fragments or invent missing bytes.
An inbox packet stores 1-3 bytes and one integer receipt timestamp. Unused byte
slots are zeroed when copied. Decoder admission order is:

1. Count the decode call. If inactive, return `Inactive` without changing timing
   history or emitting an action.
2. For an active epoch, copy the receipt timestamp to the result. Compare it
   with the previous active decode's receipt timestamp, incrementing the
   regression counter if smaller, then retain it as the last observation.
   This observation also applies to subsequently malformed/unsupported packets.
3. A size outside 1-3, first byte below `0x80`, a wrong channel-message length,
   or any high-bit channel data byte returns `Malformed` without an action.
   Channel voice statuses `0xCn` and `0xDn` need two bytes; `0x8n`, `0x9n`,
   `0xAn`, `0xBn` and `0xEn` need three.
4. A status `0xF0` or greater is `Unsupported`; no system-message subprotocol
   is interpreted in this slice. Long backend messages never enter the inbox.
5. Resolve the one-based wire channel. Unselected channels return
   `UnmappedChannel`. Then apply the supported table below; otherwise return
   `Unsupported`. Out-of-range note pitches return `OutOfRange`.

An `Action` result contains exactly one `MidiAction`. For every other status,
its action field is irrelevant and must never be dispatched. Malformed packets
are counted and ignored; they do not manufacture a release, control reset or
successful input result. The explicit device-disconnect/Panic paths remain
available for a broken sender that does not supply valid releases.

| Message on a selected wire channel | Exact admitted behavior |
|---|---|
| `0x9n pitch velocity`, velocity 1-127 | Anonymous Note On in that division. |
| `0x9n pitch 0` or `0x8n pitch velocity` | Anonymous matching Off; core velocity zero. |
| CC11, value 0-127, any division | `MidiParameterEdit{8192, value / 127.0}` for the existing nominal expression. |
| CC16-24, upper | Existing upper **B** drawbars, IDs 4112-4120, in footage order. |
| CC16-24, lower | Existing lower **B** drawbars, IDs 4144-4152, in footage order. |
| CC16-17, pedals | Nominal pedal mixtures, IDs 16384-16385. CC18-24 have no pedal mapping. |
| CC123, any value 0-127 | One ordinary AllNotesOff scoped to that division's external origin. It is not global Panic or immediate physical sound suppression. |
| CC120, CC121 | Unsupported; no guessed All Sound Off or controller-reset semantics. |
| CC64, pitch bend, pressure, Program Change, all other controllers | Unsupported. No sustain extension, hidden registration recall or tuning change. |
| System/common/realtime/SysEx/active sensing | Unsupported/filtered by the declared backend; no clock or watchdog claim. |

Every mapped drawbar edit uses normalized `value / 127.0` and the existing
`normalized_to_event` law, including its discrete half-threshold policy. It
must not introduce another integer rounding rule. Fixed B-bank mapping is
independent of the currently edited or sounding bank. It never selects B,
re-enables a Cancelled route or rewrites A. CC11 is a shared nominal expression
control: all three admitted division channels address that same existing ID.

This bounded policy deliberately leaves broader MIDI behavior to a separately
specified extension. In particular, unsupported CC120 is not falsely advertised
as equivalent to CC123.

## 3. One main-thread producer and one desired control state

The backend callback writes only `MidiInbox`. It never calls Session, UiModel,
Engine, painting, files, logging or device enumeration. The main/UI thread
remains the **only `Session::post` producer**. The audio callback remains the
sole Session consumer and Engine owner.

The main loop pops and decodes at most **32 packets per turn**, preserving FIFO
order. This is a work bound, not a guarantee that Session always has 32 spare
slots. Dispatch each action before decoding the next packet. At the first
inbox fault or failed Session submission, stop the drain and enter recovery.
Do not continue a later Note On after its preceding Off failed. Do not batch
all arrivals and silently truncate them to remaining capacity.

### Notes and scoped releases

A decoded `SessionCommand` is posted once by the main owner. Its result is
checked immediately. MIDI posting must not pass through a handler that turns
an invalid MIDI command into `ReleaseUiNotes`: that would release the wrong
owner scope. Ordinary valid MIDI actions never need a UI-channel release.
QueueFull/RecoveryPending/SequenceExhausted use the existing Session emergency
contract; an unexpected InvalidCommand is an adapter fault that closes/retires
the device epoch and remains visible.

### Controller edits must join the UI's pending state

`UiModel` currently posts complete `ControlSnapshot` values. Posting a MIDI CC
directly as a partial Event, then posting a snapshot copied before that CC,
would silently undo the external edit. Merely observing Session on the next UI
frame is too late to prevent that ordering defect.

The required narrow integration API is proposed as:

```cpp
UiActions UiModel::external_parameter(std::uint32_t parameter_id,
                                      double normalized) noexcept;
```

It must validate the existing permanent parameter ID/value, apply the existing
bridge and ControlState mutation to **`view_.controls`**, and use the same
`publish_controls` path as a local UI edit. It emits the ordinary copied
ControlSnapshot, sets pending/dirty state, and preserves editor-bank selection,
focus, note owners, saved-file reference and current gesture identity. Invalid
input emits no action and preserves state; unchanged values may emit no action.
A MIDI change is not a file load and must not mark controls clean.

The main thread intercepts `MidiParameterEdit`, calls this bridge, dispatches
its normal UI action and feeds the exact submission result to `UiModel::submitted`.
It **does not separately post the MIDI partial Event**. Thus UI and external
edits share one desired copy and one FIFO command order; their applied/pending
acknowledgments continue to use the existing sequence protocol. An external
edit to another control cannot be lost during an active UI drag. A later edit
to the same control follows the ordinary last admitted command order.

The method is implemented in [`UiModel.cpp`](../apps/standalone/UiModel.cpp),
with a retained [pending-control integration test](../apps/standalone/tests/test_standalone_external_control.cpp).
The application routes decoded edits through this method. The earlier A07 note
records the contract stage; subsequent implementation and acceptance notes
identify the actual executed code and checks.

## 4. Timing, ordering and diagnostics

`arrival_ns` is an unsigned **steady-clock nanosecond receipt observation**.
It is not an audio sample position, host timestamp or calibrated device time.
Zero, equal and decreasing values are representable and do not reorder messages.
A decreasing timestamp increments `timestamp_regressions` and marks the result;
the previous observation becomes that packet's value, rather than a high-water
mark. `begin_epoch`/`end_epoch` reset only the comparison history.

Messages always follow accepted inbox arrival order. There is no timestamp sort,
lookahead, future hold, latency compensation or frame conversion. A late Note
Off still requests release at the next admitted callback boundary. A future
numeric timestamp does not postpone an event. Session freezes its queued prefix
at each callback entry and applies its commands at offset zero; later posts
wait for a subsequent callback. No hardware latency or sample-accurate MIDI
claim follows from these timestamps.

Decoder counters are main-thread lifetime observations; they saturate at
`UINT64_MAX`. Rejected `begin_epoch` calls change no counters. Each `decode`
call increments `packets` and exactly one disposition counter (`actions`,
`unsupported`, `unmapped_channels`, `out_of_range`, `malformed`, `inactive`),
unless that counter is already saturated. Timestamp regressions and successful
epoch starts have separate counters. No diagnostic failure may block audio.

## 5. Inbox capacity and memory contract

`MidiInbox` holds **256 complete packets** in a fixed ring with one unused
storage slot to distinguish empty from full. One producer owns the write index;
one main consumer owns the read index. Release/acquire publication protects
ordinary packet payload. Read and write positions are bounded ring indices,
not unbounded counters whose wrap would invalidate ownership.

`push` first counts the attempt and checks latched faults. A faulted inbox
returns `Faulted`; otherwise empty or longer-than-three-byte inputs return
`InvalidSize` without copying any byte. An admissible packet is copied and
published once in FIFO order. The first attempt against a full ring returns
`Overflow`, increments its overflow counter and latches the Overflow fault.
All later pushes return `Faulted` until quiescent reset, even if storage became
available. `pop` on empty/faulted input returns false and preserves its output.

`signal_fault` may be called from a backend error-reporting context. It only
atomically ORs named fault bits; it never changes indices or clears data. Fault
inspection is safe concurrently. If a fault races an already progressing push
or pop, a packet can already have been published or returned: subsequent
retirement covers its owners. The API does not claim a global atomic event-time
cut between hardware failure and main-loop observation.

There are no retries, waits, allocations or hidden ownership transfers in the
queue. The implementation must demonstrate lock-free target atomics, FIFO
payload publication, capacity endpoints, destination preservation and concurrent
producer/consumer use. Lifetime diagnostic counters use independent atomic
loads/stores and saturate; their live snapshot is not transactional. After
quiescence, counter relationships can be checked exactly.

`pending()` belongs to the consumer. It provides a bounded momentary queued
count, exact after the producer is quiesced. It is not a reservation for the next
push. `reset_quiescent()` requires both participants stopped: count/discard the
remaining packets, clear indices/faults, increment resets and retain all other
lifetime counters. Clearing a live ring is forbidden.

## 6. Device retirement, recovery and reconnect

A selected device's normal close, observed disconnect, backend fault, inbox
overflow, app audio restart, routing replacement or shutdown ends its epoch.
The backend contract specifies real callback quiescence; a Boolean `is_open`
or setting `cancelCallback` is not by itself a joined-lifetime guarantee.

The main owner performs this bounded sequence:

1. Stop normal MIDI draining and call decoder `end_epoch()`.
2. Close the backend and establish that all callbacks have returned. Keep the
   inbox alive throughout. No worker may clear it while a callback is active.
3. Reset the now-quiescent inbox, discarding every unconsumed packet from the
   failed/old epoch. Preserve the failure/counter information in copied device
   diagnostics before clearing the fault bits.
4. Submit `midi_release_commands()` once in this fixed order: upper manual
   bus0/channel1, lower manual bus1/channel2, pedal bus0/channel3. Each is an
   offset-zero scoped AllNotesOff with canonical zero pitch/PedalId and velocity,
   anonymous note ID. UI channel0 is untouched; controls and source phase remain.
5. Observe the accepted release sequence as resolved/applied before starting a
   new epoch, or observe confirmed Session global recovery if submission failed.
   Never spin/retry a full Session queue. If the audio device is stopped, the
   application's already-defined quiescent stop/flush lifecycle owns resolution;
   the MIDI callback cannot render or mutate Engine to force it.
6. A new explicit port/routing action may call `begin_epoch`, then open the
   backend against an empty fault-free inbox. Failed open ends that attempted
   epoch. No automatic reconnect or replay of old notes is implied.

A successful `Session::post` means queued, not applied. A later reported Session
recovery retires the device epoch too: queued/new input must not resurrect stale
holds. The actual application must check recovery-count changes while MIDI is
active, including a UI-originated Session overflow. The pre-existing global
emergency behavior may release UI notes; report it separately from a successful
scoped device disconnect.

A normal UI Escape/focus loss uses `ReleaseUiNotes` and leaves MIDI active. The
application's deliberate global Panic also retires/discards the current MIDI
epoch so old buffered Note Ons cannot immediately undo it. Reopening is explicit.
File save/load and cosmetic view changes leave the active MIDI epoch intact.

## 7. Independent acceptance required

| Gate | Concrete observation |
|---|---|
| Namespace and all route choices | Configured wire channels1 and16, every division, adjacent range endpoints, invalid/duplicate configurations, unchanged active configuration on rejection. |
| FIFO owners | On/On/Off/Off; velocity-zero Off; nonzero release velocity; unmatched release; UI and MIDI hold the same note in both release orders. |
| Exact controls | All128 values of CC11 and each admitted drawbar; compare adopted bridge IDs/thresholds; fixed-B targeting while A is edited/sounding/Cancelled. |
| Shared desired state | MIDI CC then unrelated UI edit before callback; UI edit then MIDI CC; multiple CCs before acknowledgment; external edits during drag; dirty/Save behavior. |
| Message admission | Missing/extra bytes, high-bit data, no running status, unsupported families, wrong channels, pedal/manual range rejection and destination preservation. |
| Timing policy | Equal/decreasing/zero/far-future timestamp streams preserve original order and exact callback-boundary outcomes; counter resets only at epoch change. |
| Inbox fault | Exactly256 accepted,257th faults, no stale dequeue/re-admission after fault, queued On/Off discarded, callback race followed by scoped release, quiescent counter identities. |
| Lifecycle | Held external chord survives UI focus/resize/modal; disconnect releases only external owners; restart has no stale replay; repeated close/open; app Panic and Session recovery retire input. |
| Concurrency and bounded work | One actual producer/consumer stress path, allocation probe for queue/decoder, at most32 packets per loop; backend-close lifetime checked separately. |
| Physical controller | Named device, OS/backend, actual sustained playing/hotplug/timing/dropout observations. Synthetic injection and no-device startup do not close this gate. |

Record exact source, compiler/dependency identities, commands, original failures,
repairs and unavailable scopes. The integrator owns the current status, next task,
README captures and guarded publication; this contract alone establishes none of
those runtime outcomes.
