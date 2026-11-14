# One transaction for manual notes, pedals and controls

`process_performance_input()` accepts one ordered stream and advances the
Engine exactly once for its elapsed frame interval. It coordinates the existing
[manual ownership](NOTE_OWNERSHIP.md), [pedal ownership](PEDAL_NOTE_OWNERSHIP.md)
and ordinary musical controls without introducing another source clock.
Its model identity is **`bounded-single-clock-performance-input-v1`**.

The source basis is [atlas pp. 130, 132 and 151](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=130):
external ownership precedes physical targets, equal-time changes retain their
declared order, and only elapsed samples advance shared history. The bounded
input/rollback policy is an original software implementation. It supplies no
MIDI-byte decoder, native host ABI, measured contact behavior or concurrent UI
publication mechanism.

## Public interface

Include [PerformanceInput.h](../include/hammond/PerformanceInput.h):

```cpp
using PerformanceInputEvent =
    std::variant<HostNoteEvent, PedalNoteEvent, Event>;

PerformanceInputResult process_performance_input(
    Engine& engine,
    NoteOwnership& manual_ownership,
    PedalNoteOwnership& pedal_ownership,
    std::uint32_t frames,
    std::span<float> mono_output,
    std::span<const PerformanceInputEvent> input) noexcept;
```

Each variant's active record carries its complete offset and payload. All three
alternatives are value-owned and trivially copyable. They contain no dynamic
storage. `PerformanceInputResult` contains `status`, `input_events_consumed`
and `physical_events_consumed`, with `ok()` and an explicit Boolean conversion.

| Alternative | Meaning |
| --- | --- |
| `HostNoteEvent` | Existing two-origin, sixteen-channel manual ownership policy; releases retain their original manual after a bus remap. |
| `PedalNoteEvent` | Distinct checked `PedalId` values and two pedal-origin namespaces; no manual MIDI or native-bus convention is inferred. |
| `Event` | Ordinary controls only: `Drawbar`, `BankDrawbar`, `SelectBank`, `Cancel`, `Expression`, `Percussion`, `PedalDrawbar` and `SelectPreset`. |

Direct physical note, `KeyPosition` and division-panic `Event` alternatives
reject with `InvalidEvent`, even if they would be valid for Engine alone.
They would bypass the two external owner ledgers. Scoped releases instead use
the corresponding typed `AllNotesOff` command; another channel's owners survive.
Control payloads retain Engine's existing rules, including canonical Lower for
pedal mixtures and Upper for percussion. `SelectPreset` accepts either manual,
index zero and a finite integral value 0–11 under the
[core selection contract](PRESET_CORE_API.md#4-event-and-engine-integration).
Engine remains the authoritative payload validator; a later invalid selector
rejects the entire candidate owner/control transaction.

## Ordering and counts

Offsets must be globally nondecreasing across the variant stream. Equal offsets
preserve the supplied order across all alternatives; the facade neither sorts
the stream nor inserts a control-before-note priority. A host adapter that needs
a priority must establish that input order explicitly. A later old-bank command
therefore overrides an earlier fixed selection at the same offset here. The
separate host parameter timeline orders descriptor commands by numeric ID.

Positive blocks require `offset < frames`. Zero-frame calls admit only offset
zero. There is no retained offset-at-end carry here; the implemented
[HostTimeline](HOST_TIMELINE.md) provides that separate host-level policy.
Offsets here remain relative to this single Engine call.

Success consumes every raw input, including duplicate identified presses,
unmatched releases and empty channel panics. `physical_events_consumed` counts
all ordinary controls plus the note changes actually delivered to Engine.
It may be smaller than the input count, or larger when a scoped panic emits
several final-owner releases. Counts are both zero on every failure.

## Whole-call admission and commit

[PerformanceInput.cpp](../src/PerformanceInput.cpp) performs this sequence:

1. Check the hard frame bound and raw input count, then the complete stream's
   offsets, ordering and allowed control kinds.
2. Copy both ownership adapters. Translate each active note record on its
   candidate and append its emitted prefix in original order to a fixed array.
   Append each ordinary control in that same order.
3. Call `Engine::process()` **once** with the original frame count, output span
   and complete combined event prefix. Engine admits its full request before
   applying controls, rendering or advancing history.
4. Install both ownership candidates only after Engine succeeds.

No complete Engine copy is needed by this facade. The post-render assignments
cannot fail; compile-time checks require both ownership types to remain
trivially copyable and nonthrowing on copy assignment. A rejected translation,
expansion or Engine request changes neither live owner ledger, any Engine state
nor any caller output element. Earlier valid inputs in the rejected call are
not consumed or replayed. The caller may separately choose a recovery policy.

| Admission stage | Error and bounds |
| --- | --- |
| Hard frame bound | `BlockTooLarge` above 65,536 frames, before other checks. |
| Raw count | `TooManyEvents` above 1,024 variant records. |
| Global preflight | `InvalidEvent` for unsorted/out-of-range offsets or forbidden direct Event kinds. |
| Candidate translation | Each adapter validates its payload/identity and its independent 256-owner limit. Combined emitted notes and controls cannot exceed 1,024. Identity/payload failures use `InvalidEvent`; owner/output exhaustion uses `TooManyEvents`. |
| Engine admission | Existing prepared-state, prepared block limit, output, clock and control-payload precedence from [ENGINE_API.md](ENGINE_API.md). |

This order is deliberate: a translation failure precedes Engine admission.
Control kinds and global chronology are checked before candidate simulation;
other control payload fields are finally checked by Engine. Thus a later
ownership-capacity failure can precede an earlier malformed control value.
The result is still whole-call rejection with no mutation. No capacity limit
silently discards a required final release or admits a partial prefix.

The independent owner capacities allow 256 manual owners and 256 pedal owners
simultaneously. The raw/expanded event capacities are shared across their
streams. An empty remaining output span can admit a duplicate/no-op with no
physical event; a required emission at that point rejects the complete call.

## Clock, disconnected output and lifecycle

Even an empty input calls Engine once for the elapsed interval. Empty output
means disconnected output, not suspended time: sources, contact motion,
percussion history and the frame clock still advance. A zero-frame call applies
admitted edits once while preserving those histories and the previous actual
pedal diagnostic frame. An output span longer than `frames` retains its tail.

Use this interface on the sole processing thread or while stopped. Both
adapters must remain the coordinated authority for their physical notes.
Do not combine this function with uncoordinated direct Engine note/partial-key/
panic calls, replace an owner ledger while retaining its physical targets, or
reprepare Engine while retaining old owners. A deliberate full reset coordinates
all three objects at a quiescent boundary. Control-only snapshots preserve
owners and histories and are not a reset protocol.

The existing [manual-only facade](INPUT_PROCESSOR.md) is unchanged. Do not call
that facade and this one independently for the same elapsed interval. The
implemented [HostTimeline](HOST_TIMELINE.md) maintains its own Engine/ownership
candidates, renders bounded internal slices and commits the complete callback
only after all slices succeed. It does not call this facade. Its slice lengths
sum to the elapsed interval; boundary flushes add no elapsed frames. This facade
continues to promise one Engine transaction for one call. The native processor
calls HostTimeline once per admitted callback rather than processing the same
interval again through this function.

All storage and loops are bounded. It copies both adapters once and the active
adapter for each translated record, with linear searches/compaction bounded by
256 owners and at most 1,024 records. It performs no allocation, deallocation,
locking, I/O, parsing or SDK operation. That design statement does not establish
a device deadline; enabled-path allocation instrumentation and workload timing
are separate gates.

## Executed acceptance and remaining work

[test_performance_input.cpp](../tests/test_performance_input.cpp) compares actual
Engine output and all 91 phase bit patterns against explicitly authored physical
events, without generating the expectations through either ownership adapter.
It covers both contact models at all three supported rates, all 122 manual keys
and 25 pedals, overlapping origins, Cancel, route retention, zero-frame flushes,
disconnected output, exact output tails and 42 block-partition cases.

The [A17 extension](development/2026-11-14-preset-continuation/17-host-publication.md)
adds direct mixed-note/pedal/preset event expectations, fixed/old-bank tie order,
retained bank editing and cancelled fixed memory. It exercises all twelve preset
commands on both manuals as zero-frame flushes with held owners and checks
unchanged phase, readiness and clock. Eleven invalid manual/index/value payloads
each reject both zero-frame and positive calls after otherwise valid owner and
selector changes; every rejection compares the future audio to an untouched copy.

Late malformed controls/notes, identities, timing, buffers, clock bounds,
256-owner exhaustion, 1,024 raw events and expanded 1,024/1,025 boundaries are
checked with state/output sentinels and future rendered suffixes. The local
coherent Release gate passed this suite plus both ownership suites and the
unchanged manual facade suite. Exact source identities and executed counts are
in [assignment 22](development/2026-11-13-pedals/22-performance-input.md).

The later [independent mixed-input acceptance](development/2026-11-13-pedals/24-input-acceptance.md)
uses its own authored physical timeline and reference Engine. The
[enabled-path audit](PEDAL_REALTIME.md) measures the declared core allocation
regions, while [HostTimeline](HOST_TIMELINE.md), [StateExchange](STATE_EXCHANGE.md),
[actual native ABI](VST3_ABI_ACCEPTANCE.md), [native behavior](VST3_BEHAVIOR_ACCEPTANCE.md)
and [native concurrency](VST3_CONCURRENCY.md) retain their separate executed
host conversion, automation and publication evidence. They do not turn this
facade into an SDK or concurrent UI API.

The [wave-8 integration record](reviews/PEDAL_WAVE8_INTEGRATION.md) identifies
its complete 71-suite ordinary and eight-suite native local execution; consult
[current status](STATUS.md) for later exact-source hosted results and open gates.
Device deadlines, actual DAW sessions and physical calibration remain separate
work. Musical snapshots still exclude held owners, source phase, contact
trajectories, percussion history and time.
