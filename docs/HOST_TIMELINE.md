# Bounded host automation and musical timeline

`HostTimeline`, model `bounded-linear-host-timeline-v1`, is the SDK-independent
whole-callback transaction specified in
[VST3_SPIKE_CONTRACT.md](VST3_SPIKE_CONTRACT.md), sections 3–5. It owns an Engine,
both note-owner adapters, 47 normalized automation anchors, retained boundary
records and fixed candidate/output storage. It accepts native-adapter inputs
without including a native SDK. The fixed-registration continuation consumes
the two appended selector identities from the shared
[state/parameter contract](PRESET_STATE_PARAMETER_CONTRACT.md); the timeline
does not add another instrument model or physical-fidelity claim.

The public interface is [HostTimeline.h](../include/hammond/HostTimeline.h);
[HostTimeline.cpp](../src/HostTimeline.cpp) implements it. This document records
the assignment-28 interface with its appended preset descriptors. The original
execution and source identities remain in
[the assignment note](development/2026-11-13-pedals/28-host-timeline.md); current
preset-specific checks are recorded in
[A17](development/2026-11-14-preset-continuation/17-host-publication.md).

## Inputs, ownership and lifecycle

Construct or allocate the object outside the audio callback. `prepare(profile,
spec, model)` validates a fresh musical epoch and initializes default controls,
empty ownership, empty carry and normalized anchors. The two-argument overload
selects the existing legacy console model, matching Engine. A native nominal
prototype must explicitly supply `make_nominal_console_model()` and retain its
declared model identity.

The host maximum in `spec.max_block_frames` must be 1–65,536. Internally Engine
is prepared for the fixed 65,536-frame maximum. `reconfigure(rate, host_max)`
changes supported stopped/same-thread setup while retaining source phase,
contacts, percussion history, owners, anchors, carry and frame clock. It does
not reseed. Rates are the existing 44,100, 48,000 and 96,000 Hz. Failed prepare
or reconfigure leaves all live state unchanged. Successful fresh preparation
resets the musical epoch; wrappers must not use it for ordinary block-size or
sample-rate changes.

The processing entry point is:

```cpp
HostTimelineResult process(
    std::uint32_t frames,
    std::span<float> mono_output,
    std::span<const HostParameterQueue> parameter_queues,
    std::span<const HostMusicalEvent> musical_events,
    std::span<const ControlSnapshot> restores = {}) noexcept;
```

| Input | Contract |
| --- | --- |
| Frame count | `0 <= N <= prepared host maximum <= 65536`; source-clock addition must fit `uint64_t`. |
| Output | Empty means disconnected. Otherwise the valid caller span has at least `N` samples. Only the first `N` samples are written after success; its tail is preserved. |
| Parameter queue | One of the exact 47 compiled IDs; at most one queue per ID, including empty queues. A view is borrowed only during this call. |
| Parameter point | Signed offset in `0..N`; finite normalized value in `[0,1]`. Points within a queue are nondecreasing. Last same-offset point wins. |
| Musical stream | A fixed-storage variant of `HostNoteEvent` and `PedalNoteEvent`, globally nondecreasing in `0..N`. All original tie order is preserved within this stream. |
| Raw work | Fresh parameter points + fresh musical records + all retained carry must total at most 1,024. Restores have a separate bound. |
| Restores | Zero through four valid copied `ControlSnapshot` records, applied in supplied order before automation. |

There is no direct physical `Event` alternative. Manual and pedal owner adapters
remain authoritative for physical press/release transitions. The manual adapter
retains two origin buses, 16 channels and 256 owners; the separate pedal adapter
retains its own two origins, 16 channels and 256 owners. Native Upper/Lower/Pedal
bus and pedal MIDI mappings remain wrapper policy. This layer does not filter
unsupported native messages or guess pitches.

`set_manual_bus_route()` changes only the destination of future manual owners;
existing owners retain their original release destination. It requires prepared,
same-thread/quiescent access. Owner snapshots, `engine()`, `normalized_anchor()`
and `carry_event()` are diagnostics for that same owner thread. They are not a
concurrent UI publication interface. Checked copied diagnostics preserve the
destination on failure. No caller queue or event pointer survives `process()`.

## Curves and exact control mapping

The curve policy follows the pinned SDK primary header identified in the
[spike contract](VST3_SPIKE_CONTRACT.md#4-native-automation-including-previous-and-future-boundary-anchors).
For each active queue, the actual normalized value from the previous rendered
sample is the implicit point at offset `-1`. Between consecutive distinct
points `(l,a)` and `(r,b)`, evaluate each integer sample `i` as

```text
a + ((b - a) * (i - l)) / (r - l)
```

An explicit endpoint uses its exact supplied double. After the final endpoint,
hold that value. An absent or empty queue with no carry preserves the existing
anchor and emits nothing. A state restore resets every anchor from the restored
plain controls before queued automation is evaluated. Old bank IDs derive from
the remembered bank. New preset IDs derive from the checked effective-selection
helper: Cancel while disabled, a fixed key when enabled with a fixed mode,
otherwise bank A/B. Preparation uses the same extraction for defaults.

The implementation uses binary64 arithmetic, multiplying before division. It
clamps interpolation roundoff to the two admitted endpoint values. This is a
normalized-curve roundoff guard, not an audio limiter. An anchor tracks the
normalized curve even when its mapped discrete control has not changed. Ordinary
callback completion never reconstructs anchors from Engine controls. For example,
an old bank anchor of 0.6 remains exactly 0.6 after a new selector chooses a fixed
route. Applied selection and raw host anchors are separate diagnostics.

All controls, including discrete ones, follow the same piecewise-linear curve.
Each evaluated normalized value then passes through the existing
`normalized_to_event()` law. Drawbars use the existing exact half-up thresholds
`1/16, 3/16, ..., 15/16`; Boolean/old bank selectors use `1/2`; the two new preset
selectors use the eleven frozen nearest-binary64 midpoint thresholds specified
in the shared contract, with equality selecting the higher key. Expression
retains the normalized double. No alternate smoothing, quantizer, gain law or hysteresis is
introduced. Mapped unchanged values need no emitted event, except at explicit
points: an explicit point applies its control even when the mapped value is
unchanged. An explicit old-bank point clears fixed mode and reconnects that bank
even if the remembered bank and raw anchor were unchanged. An absent/empty queue
or unchanged discrete interpolation plateau does not reassert that command.

The 47-ID order is the compiled ascending stable order: 36 manual bank bars,
expression, Upper/Lower bank selectors, four percussion controls, two pedal
mixtures, then Upper/Lower preset selectors. At a sample with both old bank and
new preset commands, the higher-ID preset command acts last regardless of host
queue enumeration. Unsupported IDs, duplicate queues, decreasing offsets, nonfinite
values and out-of-range values reject the complete callback.

### Boundary points, zero frames and tie order

For positive `N`, a point at offset `N` serves two purposes. It is the current
curve's right endpoint while rendering samples `0..N-1`, and it becomes a
retained point at offset zero of the next accepted callback. The current anchor
must remain the actual value at `N-1`, not the unrendered endpoint. Musical
records at `N` likewise remain pending until the next accepted callback.

Every raw endpoint record is retained, including duplicate parameter ties.
Ties still resolve to one effective value; retaining their raw records keeps
the shared 1,024-record work budget explicit. Existing carry plus fresh work is
checked before any consumption. A failure consumes nothing. For example, 1,024
retained parameter points admit an empty current callback but reject one more
fresh note; the rejected note cannot force a carried release to disappear.

The common ordering at each sample is:

1. At the callback boundary, apply all supplied control restores in order.
2. For each parameter ID, its carried point at zero precedes fresh points at
   zero; the last fresh point wins a same-ID tie.
3. Evaluate/apply parameters in ascending stable parameter-ID order before
   every musical record at that sample.
4. Apply carried musical records before fresh same-offset musical records,
   preserving the order within each list.

Fresh parameter controls therefore precede carried notes at zero. A note
cannot depend on which host queue happened to be enumerated first. Carried
parameters and fresh parameters for different IDs use the same stable ID
ordering. A zero-frame callback admits only offset zero, applies that boundary
once, updates controls/anchors/owners, clears consumed carry, and retains no
new carry. Sources, contact trajectories, percussion time and frame clock do
not advance.

## Transaction and bounded slicing

Admission checks the complete output shape, block and clock limits, restores,
queue identities, raw capacities and every point/event before candidate
rendering. Both owner adapters are previewed on value copies for the entire
musical stream, including offset-`N` records. Thus a malformed or conflicting
future note rejects the current callback immediately. Its future ownership
transition is still deferred until the next accepted boundary.

After admission, the implementation copies the live Engine, owners, anchors
and carry into owned workspace. All restores, mapped automation and physical
events affect only that candidate. Output goes to its private 65,536-float
buffer. A single physical event array holds at most 1,024 emitted records.

Mapped changes accumulate across samples. Before this array would overflow,
the timeline renders its earlier-frame prefix and, if needed, applies its
current-frame tail with a zero-frame Engine call. It can then continue the
same sample without advancing it. This also handles dense typed channel panics:
a manual panic may expand to 122 distinct releases and a pedal panic to 25.
The raw work budget does not silently become a release-dropping policy.

The implementation uses the existing `NoteOwnership` and `PedalNoteOwnership`
translators directly to form these physical slices. The existing
[`process_performance_input()` facade](PERFORMANCE_INPUT.md) retains its
single-call contract and also admits `SelectPreset`. Calling that facade separately for each
owner domain would advance Engine twice; the host timeline instead owns one
common cursor. Positive slice lengths sum to exactly `N`; zero-frame flushes
sum to zero. Every source and musical history advances once per elapsed sample.

Only after all slices succeed are the live Engine, owners, anchors and carry
replaced, followed by the bounded caller-output copy. Every error returns all
consumption counters as zero and leaves live state and caller output unchanged.
Opaque workspace may change on failure; no reference to it is published.
The successful result reports fresh raw records admitted, old carry consumed,
restores applied, physical events applied and Engine calls. Admission of an
offset-`N` record counts as fresh input consumed even though its musical/control
boundary application remains pending. Engine-call counts include zero-frame
flushes and the final call.

### Admission error order

The checked order is deterministic:

| Order | Failure class |
| --- | --- |
| 1 | `NotPrepared`. |
| 2 | `BlockTooLarge` for host/hard frame limits. |
| 3 | `InvalidBuffer` for an invalid nonempty output shape. |
| 4 | `TimelineOverflow` for source-clock addition. |
| 5 | `TooManyEvents` for queue count, restore count, or initial music-plus-carry bound. |
| 6 | `InvalidEvent` for invalid nonempty views or malformed restores. |
| 7 | Per queue in supplied order: identity/duplicate check, raw capacity, view, then all point payloads/offsets. |
| 8 | Global musical offsets, then full owner preview; the existing adapters supply payload/identity/capacity status. |
| 9 | Candidate restores, mapping and Engine slices; any failure discards the whole candidate. |

Valid C++ spans and accessible backing storage remain caller preconditions;
checking size/null does not make an arbitrary forged address safe to read.

## Concurrent state integration

`HostTimeline` has no atomics, state parser or UI access. The separate
[`StateExchange`](STATE_EXCHANGE.md) provides the four-entry producer/consumer
protocol. A native wrapper must use the following single-audio-owner sequence:

1. Validate native counts, buses, formats and all host-output destinations;
   translate into bounded callback-local inputs.
2. `audio_peek(batch)` and `audio_can_commit(batch)` before timeline processing.
3. Pass `batch.snapshots()` to `process()`, using native-private output storage.
4. On success, `audio_commit(batch, timeline.engine().controls_snapshot())`,
   then copy the private mono output to admitted host channels.

Under the exchange's sole-consumer contract, no intervening consumer operation
occurs. Producer appends cannot invalidate the preflight, and Engine supplies a
valid controls snapshot. The final exchange commit is consequently nonfailing;
there is no new fallible operation between timeline success and host-output
publication. On timeline failure, do not acknowledge or publish. Headers remain
independent and no state queue is copied into Engine. State parsing and save
serialization stay off audio. Restores retain owners, phases, moving contacts,
percussion readiness, frame clock and the historical last-pedal diagnostic.

## Storage, bounded work and qualification limits

All persistent storage is value-owned fixed arrays. Compile-time checks require
Engine, both adapters, carry variants and HostTimeline to be trivially copyable;
Engine and carry copies are also required to be nonthrowing. The runtime retains
no owning heap pointer, host view or SDK object. `process()` contains no allocator,
lock, logging, file access, parsing, unbounded retry or SDK call. Construct the
large object outside callback stack frames and hold it for the instance lifetime.

Historical Linux/GCC 14.2 sizes from the original 45-ID source are:

| Object | Bytes |
| --- | ---: |
| Engine | 38,664 |
| Manual ownership | 3,328 |
| Pedal ownership | 2,112 |
| Event / carry variant / control snapshot | 16 / 24 / 56 |
| Private mono buffer | 262,144 |
| Physical event array | 16,384 |
| One retained anchor/carry set | 24,944 |
| Complete HostTimeline, including live and candidate state | 416,632 |

These original ABI observations are retained as history, not current preset-build
sizes or a portable serialized format. A17 records the current build's sizes.
Workspace copying
occurs at callback transaction boundaries; Engine is not copied for every
automated sample. Each musical record is previewed and then translated using
the existing bounded owner algorithms. Curve scanning has at most
`47 * max(N,1)` parameter visits. A conservative emitted-event bound is
`47 * max(N,1) + 122 * 1024`, safely within result counters; emitted storage is
still 1,024 records per slice. These finite bounds establish capacity, not an
audio-device deadline.

The focused test uses a separate long-double barycentric curve evaluator,
hand-authored parameter-to-event mapping and explicit physical-note reference.
It exercises both existing console models at all three rates, endpoint anchors,
zero frames, ordered ties, 1,024-record carry, full owner capacities, dense panic
expansion, the 65,536-frame maximum, disconnected output and late invalid input.
Dyadic ramps compare bitwise across 21 callback partitions. Arbitrary curve
comparisons use an explicitly bounded tolerance; equivalent host curves supplied
with differently rounded/reparameterized endpoints are not promised universally
bit-identical. Signed zero is preserved for explicit values/restores; no claim
is made that every interpolated signed-zero representation is invariant.

The preset extension preserves the named old45 threshold oracle and adds a
separate literal preset oracle plus reverse-enumerated current47 queues. It
checks both new IDs at all eleven thresholds and their adjacent binary64 values,
all twelve canonical values, all 1,600 restored fixed/bank/route combinations,
raw fractional old-bank anchors, explicit repeats, absent/empty queues, both
directions of alias plateaus, Cancel memory, restore-before-carry/fresh ties,
complete rejection continuation and 42 additional selector-curve partitions
across both console models and all supported rates.

The separate enabled-path instrumentation and native SDK harness must qualify
allocation counts, copy cost, composed state exchange, actual plugin processing,
SDK/ABI, host output layouts and lifecycle. No DAW, device deadline, platform
installer, Windows/macOS execution or physical measurement is established by
this host-independent gate. Future agents must preserve the curve, carry,
ordering and transaction rules, update the relevant contract when changing
them, and retain coherent source/build identities under [AGENTS.md](../AGENTS.md).
