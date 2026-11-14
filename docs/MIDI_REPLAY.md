# Bounded synthetic MIDI replay

Format identity: **`B3MIDIREPLAY1`**. The SDK-free declarations and parser are
[`MidiReplay.h`](../apps/standalone/MidiReplay.h) and
[`MidiReplay.cpp`](../apps/standalone/MidiReplay.cpp). The
[`test_standalone_midi_replay`](../apps/standalone/tests/test_standalone_midi_replay.cpp)
acceptance target covers the data boundary and selected real inbox/decoder paths.
The [MIDI input contract](MIDI_INPUT.md) continues to own musical routing,
ownership, decoder behavior, queue failure and scoped release requirements.

Replay supplies bounded synthetic input for native acceptance. It does not open
a MIDI device, qualify RtMidi or establish physical controller latency, hotplug,
dropout or sound fidelity. The parser performs no SDL operations, Session posts,
audio processing, waits or device callbacks. Runtime integration and its executed
native evidence are separate from parser acceptance.

## File grammar

A file starts with the exact magic on line 1 and one duration declaration on
line 2. Events follow in the desired source order:

```text
B3MIDIREPLAY1
duration_ms 1200
# Start explicitly; the source is initially disconnected.
0 connect
100 bytes 90 3C 64
100 bytes 91 40 64
100 bytes 92 24 64
500 bytes B0 0B 40
700 bytes 80 3C 00
700 bytes 81 40 00
700 bytes 82 24 00
900 disconnect
```

`duration_ms` is an unsigned decimal integer from **250 through 10000**,
inclusive. Event times are unsigned decimal integer milliseconds from the
replay origin. They must be **nondecreasing** and **strictly less** than the
declared duration. Decimal leading zeroes are permitted; signs, fractions,
exponents, hexadecimal times and numeric suffixes are rejected. Equal-time
records retain source order. The parser never sorts or deduplicates records.

| Record | Data retained in the plan |
| --- | --- |
| `N bytes HH` | One raw byte at time N. |
| `N bytes HH HH` | Two raw bytes in written order. |
| `N bytes HH HH HH` | Three raw bytes in written order. |
| `N connect` | An explicit request for a fresh synthetic MIDI epoch. |
| `N disconnect` | An explicit request to retire the current synthetic epoch. |
| `N fault backend` | A synthetic backend fault observation. |

Every `HH` is exactly two hexadecimal digits, `00` through `FF`; upper and lower
case are accepted. Prefixes such as `0x`, commas, quoted tokens, single-digit
bytes and fourth bytes are rejected. Words are case-sensitive. No other fault
name or action is admitted. In particular, there is no command execution,
include directive, file-writing instruction, device selector, code callback or
shell substitution in this format.

The byte record is one complete packet supplied to the existing inbox. The
parser deliberately accepts invalid MIDI semantics: `00 FF 80`, `90`, and
`90 80 01` are valid replay records. Their malformed dispositions belong to the
existing MIDI decoder. Similarly, `F8` is retained for its unsupported-message
path. The parser does not infer missing bytes, combine records into running
status, change high-bit data or create SysEx fragments.

Only printable ASCII, spaces, tabs, LF and CRLF are admitted. A carriage return
must be followed by LF; a final line need not have a line ending. The magic has
no leading or trailing whitespace. Subsequent fields may have leading,
separating and trailing spaces or tabs. After the two required header lines,
blank lines and lines whose first non-space/tab character is `#` are ignored.
Inline comments are not accepted. Header comments or blank lines cannot move
the magic or duration to another line.

## Bounds and transactionality

| Boundary | Exact allowance |
| --- | --- |
| Total source size | 1 through 65536 bytes, including comments and line endings. |
| Physical line size | At most 256 bytes, excluding LF or CRLF; applies to comments and blank lines too. |
| Event count | 0 through 2048 records; comments and blank lines do not count. |
| Duration | 250 through 10000 milliseconds. |
| Event time | 0 through `duration_ms - 1`, with nondecreasing order. |
| Byte payload | 1 through 3 raw bytes. |

`parse_midi_replay(source, destination, error)` validates into a local candidate.
Any failure preserves every destination field, including inactive array
entries, and supplies a nonempty error. Success replaces the complete
destination and clears the error. Each event owns its bytes; changing or
destroying the source string cannot alter an admitted plan. Non-byte events
have zero size and zero payload. Unused payload slots and inactive event
entries have their default zero values.

`load_midi_replay(path, destination, error)` has the same destination guarantee.
It rejects an empty path, embedded path NUL, missing input, directory, leaf
symlink/reparse point, FIFO and non-regular device. A symlink in a parent
directory is permitted; the policy applies to the opened leaf. It opens the
leaf with the platform's nonsymlink mode and validates that same handle before
reading, so a separate path-status/open race cannot substitute a pipe or
symlink leaf. POSIX opening is nonblocking to avoid waiting on a FIFO before
type validation.

The loader checks the initial regular-file size, reads at most 65537 bytes and
requires the observed byte count to match the initial size and the 65536-byte
cap. A detected size change rejects. This is a bounded data read, not a claim
of an immutable filesystem snapshot: a same-size rewrite during reading is
not independently detected. Write an acceptance script completely before
starting its bounded run.

The public plan is a value type and contains no cursor or runtime references.
Only its first `event_count` records are active. Code that changes a plan after
successful parsing is responsible for retaining the contract; the application
uses the parsed plan without modifying its records. Parsing and file access
belong before replay on the control thread, never in an audio callback.

## Runtime contract

The native application owns due-event processing, the current cursor, duration,
diagnostic observations and the existing release-acknowledgment protocol.
The synthetic source starts **disconnected**, even if its first event is a byte
packet. Bytes while closed are counted and dropped; they are not buffered for
a later connection. Routing uses the same configured upper/lower/pedal wire
channels as ordinary MIDI input.

Every `connect` record requests a fresh synthetic epoch. When a previous epoch
is still active, the runtime retires it first. An accepted release post is not
yet an applied release. The runtime pauses following replay records while
the old epoch's scoped release acknowledgment or confirmed global recovery is
pending. A later byte record, including one with the same scheduled time,
must not cross this barrier into an unretired epoch. Only then may the decoder
begin the requested new epoch against an empty, fault-free inbox.

`disconnect` and `fault backend` stop the synthetic producer, discard queued
old-epoch packets and follow the same scoped retirement requirements as the
ordinary device lifecycle. The synthetic producer is owned by the main thread;
there is no physical callback to join. Explicit reconnect is required for later
input. UI channel-zero ownership and the existing shared desired-control state
retain their normal contracts. A deliberate global Panic, Session recovery or
audio restart may also retire the current epoch under the application lifecycle.

The runtime visits at most **512 due replay records per main-loop turn**,
preserving its cursor and source order. Byte records feed the existing
`MidiInbox`; the common main-thread drain remains at most **32 packets per
turn**. Producing a burst before draining permits an actual sequence of 256
accepted packets followed by a 257th overflow attempt. There is no replay
`overflow` command that could substitute a fabricated diagnostic for this
capacity boundary. Barriers may reduce the number processed in a turn.

Injected backend faults and resulting inbox capacity faults remain visible as
synthetic diagnostics. Expected injection itself does not establish an
application execution failure; failed submissions, unresolved retirement,
audio failure or an incomplete bounded replay remain failures according to
the native acceptance criteria. Counter expectations and actual musical state
must be checked by the native test rather than treating any finished process
as a lifecycle pass.

Scheduled milliseconds determine when a main-loop event becomes due. They are
not audio frame offsets or a calibrated hardware receipt clock. The inbox and
decoder retain their receipt-observation/FIFO contract, and Session still
applies admitted commands at callback boundaries. No sample-accurate dispatch
or latency guarantee follows from the script schedule.

## Native command composition

The application integration uses `--midi-script PATH`. It rejects pairing this
option with `--midi-port` or `--smoke-ms`. It may run with the existing
`--input-script PATH` UI replay only when both files declare the same duration.
The two streams each preserve their own order. Equal times across different
streams do not declare a sample-accurate or globally merged ordering; native
tests must use actual observations and suitable acknowledgment margins.

A representative invocation after building the native executable is:

```sh
SDL_AUDIODRIVER=dummy SDL_VIDEODRIVER=dummy \
  ./build-standalone/apps/standalone/hammond_standalone \
  --midi-script acceptance.b3midi \
  --diagnostics acceptance-midi.json
```

This command is a usage example, not retained evidence of an executed native
run. The [A22 parser record](development/2026-11-14-midi-ui/22-midi-replay.md)
lists actual source identity, commands and results. Native pairing, reconnection,
fault retirement and final acknowledgment observations belong to the integrating
application's acceptance record. Physical MIDI and native platform qualification
remain separate gates.
