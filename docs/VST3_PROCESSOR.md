# Nominal native VST3 processor

`plugins/vst3/Processor.h/.cpp` implements the processor half of the early native
instrument in [VST3_SPIKE_CONTRACT.md](VST3_SPIKE_CONTRACT.md). Its model identity
is `nominal-vst3-processor-v1`. The processor delegates instrument behavior to
the existing SDK-independent [HostTimeline](HOST_TIMELINE.md) and concurrent
[StateExchange](STATE_EXCHANGE.md); it does not copy DSP into an SDK wrapper.

The source basis is atlas pp. 385–396: independent graph and wrapper ownership,
bounded callbacks, one render clock, automation anchors, active state calls,
explicit bus admission and separate host qualification. This implementation
uses the pinned SDK's `AudioEffect`, `IComponent`, `IAudioProcessor`,
`IEventList`, `IParameterChanges` and `IParamValueQueue` declarations. The
[dependency lock](../data/dependencies/vst3-sdk-lock.json) identifies their exact
root and submodule commits. The complete native build, factory/controller,
actual ABI harness and SDK validator are separate integration assignments.

## Declared instance and signal model

The factory constructs `hammond::vst3::Processor` outside the audio callback.
The original processor/controller FUIDs in `PluginIds.h` remain the identities
specified in the spike contract. No custom editor is required by this processor.

Initialization parses the generated `EmbeddedProfile.h` text using the existing
compiled-profile loader, with the 128 KiB profile bound. That generated text is
the nominal `.b3p` input, not a filesystem fallback or a second synthesizer
description. Parsing, temporary strings and SDK bus allocation occur off audio.
Initial setup explicitly selects `make_nominal_console_model()` and seed zero.
Manual contacts therefore use the existing proposed linear-travel profile;
pedals retain their existing ideal contacts and named nominal mixture. The
initial controls retain the registry defaults, including muted drawbars and
percussion Off. A useful audible fixture must supply a registration.

| Native surface | Implemented contract |
| --- | --- |
| Audio inputs | None. Positive or negative input-bus counts reject. |
| Audio output | One stereo `Dry stereo` bus; the two channels receive identical dry float32 samples. |
| Event inputs | `Upper` main bus 0, `Lower` auxiliary bus 1 and `Pedals` auxiliary bus 2; 16 channels each. All advertise `kDefaultActive`; the host activates buses through `activateBus`. |
| Event outputs | None. Supplied output event/parameter interfaces are not written or retained. |
| Parameters | Exactly 47 compiled IDs: the unchanged original 45 plus upper/lower preset selectors 20480/20481. Duplicate queues reject, including duplicate empty queues. |
| Rates | 44,100, 48,000 and 96,000 Hz. Other rates reject during setup. |
| Blocks | Host maximum 1–65,536; actual callback 0 through that maximum. |
| Precision | Float32 only. Float64 and unknown symbolic sizes reject. |
| Modes | Realtime and prefetch can alternate per callback; entering/leaving offline requires a stopped setup change. |
| Latency/tail | SDK base latency remains zero. `kInfiniteTail` is the conservative declaration for retained held voices without an automatic truncation policy; it does not introduce a delay, room, hum or cabinet model. |

Routing information maps every valid event bus/channel to audio bus zero, both
channels. Bus arrangement negotiation accepts only zero inputs and one stereo
output; an unsupported request leaves the declared layout unchanged. Bus
activation/deactivation is permitted only with processing stopped. Deactivation
does not release held owners or reset the generator.

## Native musical admission and filtering

Manual buses 0/1 map MIDI 36–96 to their existing typed ownership namespaces.
Pedal bus 2 uses the named software policy `vst3-pedal-midi36-v1`: MIDI 36–60
maps to one-based `PedalId` 1–25 and logical pedal origin bus zero. It is not a
claim about a physical controller's octave. Channels and note IDs retain their
ownership identities; repeated anonymous notes use the existing FIFO release
rules. A native note ID is `-1` or nonnegative.

Every supported note is validated before deciding whether its pitch lies in
the instrument's range. Channel must be 0–15; MIDI pitch must be 0–127; velocity
must be finite in `[0,1]`; tuning must be finite. Malformed notes reject the
whole callback, including malformed notes whose otherwise valid pitch would
be outside the manual/pedal range. On velocity zero becomes a release. Positive
velocity maps to a rounded 7-bit value with a minimum of one, so a tiny positive
velocity cannot become an accidental release. Sustained gain remains independent
of velocity. Release velocity is validated, then ignored by the core.

The profile fixes shared source frequencies. Native per-note tuning is accepted
when finite but ignored and counted when nonzero. The optional NoteOn `length`
is ignored; a NoteOff is still required, and there is no scheduled automatic
release. Neither field creates a per-note oscillator.

`vst3-valid-unsupported-and-pitch-filter-v1` is the explicit filter policy:

- Valid manual/pedal notes outside the supported instrument range are counted
  in `filtered_pitch_events` and omitted from typed musical input.
- Valid recognized unsupported kinds—SysEx data, poly pressure, note expression
  value/int/text, chord and scale—are counted in `filtered_unsupported_events`.
  Scalar ranges and required pointer/count shapes are validated. External
  data/text is neither read nor retained; this does not validate or interpret
  the unused string contents or SysEx payload. Custom note-expression type IDs
  have no advertised meaning in this processor.
- Unknown kinds, output-only `LegacyMIDICCOut`, malformed unsupported payload
  headers, invalid native bus indices, nonfinite PPQ positions and bad offsets
  reject. A supported in-range note sent to an inactive event bus also rejects;
  its release is never silently discarded because the bus was deactivated.

All raw native event records count against capacity, including filtered ones.
Every event offset must be nondecreasing and in `0..N`, even if that event will
be filtered. Known unsupported records at offset `N` are consumed as filtered
input in the current call; only admitted musical/parameter records need carry.

## Bounded automation and common time

Native queue count is signed and must be 0–47. Each queue pointer must be valid,
its ID must be a compiled descriptor, and its signed point count must fit the
remaining capacity. Each `getPoint` must succeed; its signed offset must be
nondecreasing in `0..N`, with finite normalized value in `[0,1]`. No host queue
or event view survives the callback. Checked values are copied into fixed arrays.

The raw budget is:

```text
native event count + native point count + previous carry count <= 1024
```

This check precedes rendering; filtering does not create extra capacity. State
restores have their separate four-entry bound. Overflow never becomes partial
admission or release dropping. Unknown IDs, negative counts, host accessor
failures and a malformed late record preserve the live transaction.

HostTimeline owns reconstruction from the previous sample at offset `-1`, exact
discrete thresholds, duplicate-point ties, parameter-ID ordering and the stable
musical stream. Offset-`N` parameter values serve as current interpolation
endpoints and retained next-boundary values. Zero frames apply admitted
offset-zero input once without advancing or recarrying it. The native wrapper
does not add smoothing, rerender separate divisions or adjust the source clock.

The two appended preset parameters are ordinary routing commands, not host
programs. At one sample, numeric-ID order places the old bank commands before
the higher-ID preset commands. An explicit repeated bank value exits fixed
mode and reconnects its bank. Absent queues and unchanged discrete interpolation
plateaus do not continually reassert either route. Raw automation anchors remain
separate from the applied route; whole-state restore reinitializes anchors using
remembered banks for old IDs and checked effective selections for new IDs.
The [fixed-selection contract](PRESET_SELECTION_CONTRACT.md) specifies Cancel,
retained bank data and percussion eligibility without changing note ownership.

## Output shapes and failure atomicity

Output admission runs before any input translation or state consumption. All
declared pointers must designate accessible, stable host storage for the whole
call; null/size checks cannot authenticate an arbitrary forged address.

| Shape | Policy |
| --- | --- |
| `numOutputs == 0` | Accepted disconnected output. Private rendering still advances every requested frame; no output pointer is dereferenced. |
| One active stereo output, positive frames | Requires a nonnull two-channel array and two nonnull valid sample spans. Both channels are completely written after success. |
| Exact L/R sample-pointer alias | Accepted; copy the identical mono render only once. |
| Distinct but partly overlapping L/R ranges | Rejected before processing. Checked `uintptr_t` ranges guard multiplication/addition; no unrelated-object pointer subtraction or comparison is used. |
| Inactive stereo output | Requires its two-channel pointer array. Individual sample pointers may be null. Private time advances; supplied sample memory and silence flags remain unchanged. |
| Zero-frame flush with zero channels | Accepted; no sample pointer is read, flags are zero because no output channel is described. |
| Zero-frame stereo output | Requires the channel pointer array; sample pointers may be null and are never dereferenced. The empty rendered block is silent. |
| Other count/channel/pointer/precision shapes | Rejected with host output and all live state unchanged. |

For an admitted callback the processor follows one transaction:

1. Validate output and every bounded native input; translate into fixed storage.
2. Peek the exchange batch and require `audio_can_commit` success.
3. Call HostTimeline once with copied inputs, `batch.snapshots()` and the
   processor's private mono output. Any timeline error leaves owners, controls,
   histories, anchors, carry, pending loads and caller output unchanged.
4. Publish `timeline.engine().controls_snapshot()` using the same batch. This
   call is nonfailing under the proved exchange preconditions: one audio owner,
   no intervening commit, valid Engine snapshot and append-only UI producer.
   The return value is deliberately not made into a new late admission gate.
5. Copy private samples into admitted active channels, then report silence from
   the actual rendered samples and replace the last successful diagnostic.

Silence is true only when every actual sample equals zero. It is not inferred
from note count. The processor still renders silent and disconnected intervals;
an output flag never suspends shared sources. Rejected callbacks do not write
silence flags, consume queued state, issue a panic or replace the previous
successful diagnostic.

## State calls and lifecycle

`setState` and `getState` run on one serialized UI/main thread, including while
audio processing is active. The stream helper parses/serializes off audio with
the existing 16 KiB control-state limit. A parsed state is copied into the
four-entry exchange; full or invalid loads fail without displacing pending
entries. No `IBStream*` is retained. `getState` saves the newest accepted UI
load while pending, then the coherent published audio controls after
acknowledgement. Bounded publication-read contention can return explicit failure
without writing the destination stream; retry belongs to the host/UI side.

The writer emits `B3CONTROLS4`; readers accept 1/2/3/4 with the explicit
[migrations](CONTROL_STATE_FORMAT.md). Legacy input initializes raw fixed modes
to `None`; version 4 also requires the pinned catalog identity. StateExchange
preserves both raw fixed modes, remembered banks, route bits and every retained
bank value. The effective Cancel/0 parameter value alone cannot reconstruct
that memory. Restore never resets held owners, moving contacts, percussion
readiness, phases or frame count. Controller synchronization uses its own
`setComponentState`, without an echoed automation gesture.

Lifecycle calls require the host to establish actual quiescence. Plain
`initialized_`, `active_` and `processing_` flags check legal sequencing; they
are not locks and do not make an overlapping lifecycle call safe. UI state
calls access only the exchange, not these mutable audio histories.

- First successful setup prepares one fresh seeded epoch. Subsequent supported
  setups, while inactive and stopped, use phase-preserving `reconfigure`.
- `setActive` requires preparation and a changed active state. Repeated identical
  activation/deactivation and activation while processing reject.
- `setProcessing` requires an initialized, prepared active instance. It is a
  bounded Boolean change; repeated values are accepted and never reset sound.
- Termination requires stopped/inactive state. Repeated initialization while
  initialized and repeated termination reject. Reinitializing the same retained
  object recreates SDK buses but preserves its already prepared musical epoch
  and accepted state queue. Destruction followed by new construction creates a
  new instance and epoch.
- Transport context and wall-clock time are not used to reseed or catch up.
  No callbacks means no simulated elapsed frames. No editor action owns time.

## Qualification and next gate

The [assignment 31 record](development/2026-11-13-pedals/31-native-processor.md)
retains the exact strict compiler check and source hashes. A syntax check
establishes compilation of this translation unit against the pinned SDK; it
does not establish a linked module or host behavior. The composed core's earlier
allocation/concurrency tests likewise do not qualify a native callback.

That syntax result is historical. The complete [optional native bundle](VST3_BUILD.md)
has historical [loaded-module ABI](VST3_ABI_ACCEPTANCE.md) and
[behavior](VST3_BEHAVIOR_ACCEPTANCE.md) gates covering the three event buses,
45 descriptors, block boundaries, alias admission, active state migration,
late rejection and stopped rate changes against independent core references.
Further [dense automation](VST3_AUTOMATION_REVIEW.md),
[concurrent native state](VST3_CONCURRENCY.md), [actual callback allocation](VST3_REALTIME.md)
and [bundle relocation](VST3_LOCAL_INSTALL.md) records identify their own code,
module, dependency, compiler and instrumentation scopes. The [pinned validator record](VST3_BUILD.md#recorded-local-qualification-and-current-gates)
retains its actual summary together with the unsupported-rate and teardown
diagnostics; it is not a warning-free or arbitrary-format result.

The current [preset integration](reviews/PRESET_VST3_INTEGRATION.md) qualifies
47 exports, state4/legacy streams, held-note selector/alias histories, callback
allocation and concurrent raw publication in eight native suites. The
[independent acceptance](reviews/PRESET_VST3_ACCEPTANCE.md) compares its retained
validator diagnostics with the baseline and exact SDK source. Neither the
processor lifecycle nor supported precision/rates was expanded to silence those
messages. These newer records do not rewrite the earlier 45-parameter results.

The [coherent wave-8 integration](reviews/PEDAL_WAVE8_INTEGRATION.md) passed
71 ordinary and eight focused native suites locally. Use [current status](STATUS.md)
and the [portability review](reviews/PEDAL_NATIVE_PORTABILITY.md) to identify
which later hosted source/platform and artifact gates actually ran. Required
next work is to preserve these interfaces through the dependency-ready model
changes in [NEXT_STEPS.md](NEXT_STEPS.md), qualify any changed adapter or package,
and execute the still-open DAW/device, deadline, accessible custom UI, signing
and specimen-calibration gates. Existing software evidence does not close them.

Future agents must preserve these ordering, capacity and lifecycle contracts,
record changed evidence in the current session, and follow [AGENTS.md](../AGENTS.md)
for review, documentation and verified publication.
