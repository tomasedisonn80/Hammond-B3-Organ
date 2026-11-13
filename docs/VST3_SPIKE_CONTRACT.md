# Minimal VST3 instrument: pinned foundation and acceptance contract

**2026-11-13, assignment 15.** This is the implementation contract for an early
M9 wrapper smoke gate after the nominal pedal core. The selected SDK's headless
validator builds locally and its own 51 selftests pass. No Hammond VST3 module,
DAW session, device deadline, custom UI or release package is established by that
result. Those require the independent gates below.

The source basis is atlas pp. 379–402 and 450, reviewed in
[product review](development/2026-11-13-pedals/05-atlas-product.md) and
[closure review](development/2026-11-13-pedals/06-atlas-closure.md), together with
the selected SDK headers. The atlas's historical wrapper/license and 62-control
examples do not replace the current repository's identities or selected terms.

## 1. Dependency and build boundary

[The lock](../data/dependencies/vst3-sdk-lock.json) pins SDK 3.8.1, tag
`v3.8.1_build_84`, commit `3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96`, and the
four necessary submodules. All five primary `LICENSE.txt` files are identical
MIT texts, 1,094 bytes, SHA-256
`e86d79e19e4a33ebc442d2e0d083887dfc75a2a8de9fe17eeddedb84810ad74e`.
The embedded module-info parser `json.h` separately declares Unlicense; omitted
samples can contain still other dependencies. See the
[rights inventory](DEPENDENCIES_AND_RIGHTS.md) and
[retained notices](../THIRD_PARTY_NOTICES.md).

Acquire explicitly outside the repository; ordinary configure/build must never
download an SDK. The optional plugin switch is `HAMMOND_BUILD_VST3=OFF` by
default; `HAMMOND_VST3_SDK_ROOT` selects a separately acquired verified checkout.
Keep the ordinary project's CMake 3.21 floor. Enabling this SDK requires CMake
3.25 or newer, matching its pinned root `CMakeLists.txt`.

Explicit acquisition commands (run from a directory outside this repository):

```sh
git clone --branch v3.8.1_build_84 --single-branch --depth 1 \
  https://github.com/steinbergmedia/vst3sdk.git vst3sdk
git -C vst3sdk rev-parse HEAD
git -C vst3sdk submodule update --init --depth 1 \
  base cmake pluginterfaces public.sdk
git -C vst3sdk submodule status base cmake pluginterfaces public.sdk
```

Stop if the root commit or any required submodule identity differs from the
lock, or if the selected primary-license hashes differ. A tag name alone is not
the pin. Existing checkouts must be inspected without resetting unrelated work.
The later optional build integration must enforce these checks. This foundation
does not add an acquisition helper or implicit configure-time fetch.

The independent SDK foundation was built using:

```sh
cmake -S /path/to/vst3sdk -B /path/to/vst3-foundation-build \
  -DCMAKE_BUILD_TYPE=Release \
  -DSMTG_ENABLE_VSTGUI_SUPPORT=OFF \
  -DSMTG_ENABLE_VST3_PLUGIN_EXAMPLES=OFF \
  -DSMTG_ENABLE_VST3_HOSTING_EXAMPLES=OFF \
  -DSMTG_CREATE_PLUGIN_LINK=OFF \
  -DSMTG_RUN_VST_VALIDATOR=ON
cmake --build /path/to/vst3-foundation-build --target validator -j 4
/path/to/vst3-foundation-build/bin/Release/validator -selftest
```

Observed platform: Linux, GCC 14.2.0, CMake 3.31.6. Configure succeeded with an
informational missing-JACK message; JACK is not required for this headless
target. The SDK's atomic-header feature probe selected its fallback. Both the
build's selftest and a separate invocation reported **51 tests, zero failures**.
This checks the SDK host-test machinery, not a Hammond plugin.

The later optional build must use `smtg_add_vst3plugin`, link `hammond_core` and
the SDK `sdk` target, and enable position-independent core objects when needed
by the shared module. No DSP is copied into the wrapper. Do not initialize or
build GUI, plugin examples, hosting examples, documentation or tutorial modules;
do not create links in a user's system plugin directories. Keep generated
bundles and SDK sources outside versioned project inputs. A module-info file
and validation reports are build outputs with separate distribution inventories.

## 2. Stable identities and supported native surface

Freeze these original UUIDs in `plugins/vst3/PluginIds.h`; never substitute SDK
sample UUIDs or change these to solve a validation problem. Use the FUID words
through the SDK, rather than assuming platform-specific byte ordering.

| Class | UUID | FUID constructor words |
| --- | --- | --- |
| Processor | `19f9adc0-533f-42b4-b96b-d51d6547e838` | `0x19F9ADC0, 0x533F42B4, 0xB96BD51D, 0x6547E838` |
| Controller | `0dee76ab-26bc-475a-bf64-f138c89fb0e0` | `0x0DEE76AB, 0x26BC475A, 0xBF64F138, 0xC89FB0E0` |

| Surface | First instrument contract |
| --- | --- |
| Audio | No audio input; one stereo float32 output, identical dry samples on both channels. Reject unsupported float64; do not advertise conversion that is absent. |
| Timing | Rates 44,100, 48,000 and 96,000 Hz; activation maximum `1 <= H <= 65,536`; callbacks `0 <= N <= H`. |
| Event input | Three native buses: Upper, Lower, Pedals. Native bus count is not the size of `Manual`. Upper/lower use existing typed manual ownership; pedals use distinct `PedalId`. |
| Manual mapping | Native buses 0/1, MIDI 36–96 inclusive, all 16 channels retain ownership identity. |
| Pedal mapping | Native bus 2, named software policy `vst3-pedal-midi36-v1`: MIDI 36–60 maps to `PedalId` 1–25. This is a controller policy, not evidence of the physical pedal octave. |
| Velocity | Zero velocity releases; nonzero velocity does not scale sustained amplitude. Preserve identified-note and anonymous FIFO ownership semantics. |
| Parameters | Exactly the 45 compiled registry records after the pedal append. Preserve the previous 43 IDs, laws, bounds, units and defaults; append pedal IDs `0x4000` and `0x4001`. Schema 3/model `exclusive-ab-percussion-pedal-console-v3`. |
| Models | Use the existing nominal profile and declared console/contact model. Retain their identities; this first wrapper adds no scanner, AO-28, Leslie or calibrated response. |
| State | Write `B3CONTROLS3`; accept 1/2/3 with explicit migration of old states to muted pedals. Preserve both manual route-enable bits, not merely the 45 parameter values. |
| UI | Generic host parameter controls; no custom editor. Construction, headless processing and state save must work without opening an editor. |

Validate signed counts, bus indices, channel, note identity, pitch, finite
velocity, normalized values and offsets before unsigned conversion. Valid
out-of-range musical pitches and unsupported event kinds may be filtered only
under a named, counted policy. Malformed supported events reject the complete
call. Never drop a supported NoteOff because an earlier queue consumed capacity.
No MIDI echo/output bus is advertised. The registry's initially muted drawbars
remain unchanged; a demo must explicitly choose a registration.

## 3. One clock and transactional processing

Preparation, profile decoding, SDK construction and scratch allocation occur
outside `process`. The audio path owns Engine and manual/pedal ownership state.
Preallocate a candidate Engine, candidate owners, event/curve/carry storage and
a private mono output buffer. If value copies are used, prove their ownership
and allocation properties and measure their cost; do not accidentally copy an
owning heap pointer into shared mutable state.

Before live mutation, validate the **entire** callback, pending state candidate,
every queue point and event, capacities and clock bounds. Render all slices on
the candidate and private output. Commit Engine, owners, automation anchors,
carry, state-queue read cursor and output only after complete success. Late
malformed input, an Engine error or output-shape failure must leave all of these
unchanged. A separately documented panic/silence recovery transaction may follow
a failed admission; it is not a successful partial render.

Merge controls and manual/pedal events into one timeline. Never call two
ownership facades that each advance Engine for the same frame range. If a
callback is sliced, the slice lengths sum to exactly `N`; every source,
contact, percussion state and frame clock advances once per elapsed sample.
Prepare the core for the fixed 65,536-frame hard maximum, so a stopped host
block-size change does not force a new musical epoch. Supported stopped sample
rate changes use phase-preserving reconfiguration; initial construction alone
starts the fresh seeded epoch. Transport seeks, editor closure and output
silence do not reseed or issue implicit global NoteOff.

Validate buffers before dereference, including omitted/inactive buses, null
channels and aliased channels. A valid positive disconnected-output callback
still advances the timeline. The private mono render permits an explicit safe
copy policy for valid aliasing. No callbacks means no simulated wall-clock
catch-up. Zero-frame calls apply only admitted current-frame controls/events
once, with no source advancement or later replay. Report silence from actual
rendered output/current state; do not suspend free-running sources to optimize
a silence flag.

Freeze total admitted raw event/point/carry work at 1,024 records per callback.
An input that exceeds this limit rejects before any consumption; no partial
admission or endpoint-dropping policy is allowed. Control-state queue entries
are separately bounded to four. Establish explicit total ordering:

1. An admitted state restore establishes controls and automation anchors.
2. Retained previous-boundary events precede fresh same-offset events.
3. Parameter curves are evaluated before musical note events for that sample.
4. Parameter ties use stable parameter-ID order; musical ties preserve the
   native list's original order.

Callbacks may be segmented to keep emitted core-event arrays bounded even when
a small number of curves creates changes at many samples. This must not cause
extra advancement, missed thresholds or partial commitment. There is no heap
allocation/deallocation, lock, logging, filesystem access, string parsing,
SDK-object construction or unbounded retry in `process`/`setProcessing`.

## 4. Native automation, including previous and future boundary anchors

The pinned SDK's [`ivstparameterchanges.h`](https://github.com/steinbergmedia/vst3_pluginterfaces/blob/4f547e8e102b47de4a8b8aaf343c73b700786372/vst/ivstparameterchanges.h)
defines piecewise-linear curves. A point at sample `n` does not mean holding
the old expression until `n`. The previous block's final value is the implicit
anchor at sample `-1`; interpolate from that anchor to the first new point.
With anchor `a` and first point `(n,b)`, samples `i <= n` have
`a + (b-a)*(i+1)/(n+1)`. After the final point, hold its value; an absent queue
holds the last value. Explicit jumps use adjacent old/new sample points.

Keep 45 fixed curve states. Validate all queue IDs and all points before
rendering; reject duplicate queues for one ID and decreasing timestamps.
Same-offset points within one queue use its last supplied value. Exact
same-offset zero-frame updates are applied once and replace the anchor.
Evaluate discrete controls through the existing exact normalized thresholds;
do not silently change the drawbar law, default, or expression meaning.

The adapter admits offsets `0..N`; core positive blocks remain half-open.
An offset-`N` record is retained for next block's offset zero and counted in
bounded carry storage. **An expression point at `N` is also the right-hand
endpoint for interpolation of current samples `0..N-1`.** Hiding it until the
next callback produces an incorrect ramp. Its value is applied as the retained
boundary event before new offset-zero points in that next callback. Preserve
the actual last rendered value as the previous-sample anchor, not the future
endpoint. Failed admission preserves carry and anchors in full. Carry capacity
plus new records is checked atomically; no duplicated or consumed-on-failure
boundary event is allowed. Reject offsets below zero or greater than `N`.

## 5. State calls while audio is active

The SDK [`IComponent` declaration](https://github.com/steinbergmedia/vst3_pluginterfaces/blob/4f547e8e102b47de4a8b8aaf343c73b700786372/vst/ivstcomponent.h)
explicitly permits UI-thread `setState` and `getState` during Processing. A
direct concurrent Engine snapshot, plain-payload seqlock, or unconditional
active-state rejection does not satisfy this gate. An atomic processing flag
alone is not mutual exclusion.

Implement a bounded single-UI-producer/single-audio-consumer queue of four
value-owned, validated `ControlSnapshot` records and sequence identities.
Parse a bounded state stream outside audio (initial limit 16 KiB), migrate
1/2 to zero pedal mixtures, and validate every field before accepting a write.
On a full queue, report failure and preserve all pending entries. The producer
publishes a completed slot with release semantics; audio acquires it and does
not free the slot until callback commitment. Apply no more than four pending
snapshots at the next accepted boundary, before ordinary input. Restore only
musical controls; preserve owners, physical contacts, percussion readiness,
source phases and clock. Reset automation anchors to the loaded control values.

Publish a coherent controls snapshot and acknowledged sequence back to UI after
commit. One acceptable implementation uses fixed `atomic<uint64_t>` payload
cells for the 45 control values, two route bits and acknowledged sequence,
plus an odd/even atomic publication sequence. Encode doubles by bit-preserving
conversion. Require lock-free 64-bit atomics on advertised targets; all fields,
including payload, are atomic. A sequentially consistent implementation gives
a simple initial proof: audio writes a fixed number of cells without waiting;
UI copies between matching even sequence values. UI may retry a bounded number
of times (eight initially), then return an explicit failure. A plain non-atomic
payload is forbidden because concurrent failed reads still constitute a C++
data race. Define sequence exhaustion without an ABA wrap. An equivalently
proved fixed-slot ownership protocol is acceptable.

`getState` selects the newest accepted UI snapshot while it is pending and the
coherent published snapshot once its sequence is acknowledged. This preserves
an accepted stopped/suspended load even if no callback has yet consumed it,
while later audio automation appears in subsequent saves. A full snapshot
ring that permanently stops publishing when UI does not read is insufficient:
a later save must not return stale controls. Initialize publication to the
registry defaults before activation. Never retain an `IBStream*` for audio use.

Controller `setComponentState` updates its parameter values off audio without
echoing a new automation gesture. Route-enable flags are processor state even
though Cancel is not a native parameter. All v1/v2/v3 round trips must preserve
this distinction. Lifecycle transitions establish actual quiescence before
preparation or destruction; `setProcessing` remains bounded and allocation-free.

## 6. Files and independent closure gates for the implementing wave

| Work item | Intended ownership/API boundary | Required evidence |
| --- | --- | --- |
| SDK build/factory | Optional root build hook and `plugins/vst3/CMakeLists.txt`, `PluginIds.h`, `Factory.cpp`; exact lock verification | Default SDK-free build; explicit wrong/missing-pin rejection; native bundle with frozen FUIDs; correct exported factory entry points. |
| Processor | `plugins/vst3/Processor.h/.cpp`, based on SDK `AudioEffect`; composed Engine/owners/curve and state handoff objects | Supported buses/rates/formats, one-clock processing, bounded rejection, null/inactive/aliased outputs, lifecycle. |
| Controller | `plugins/vst3/Controller.h/.cpp`, SDK edit controller and compiled descriptor iteration | All 45 native descriptors agree with registry; generic host UI, exact conversions, component-state migration, no custom editor dependency. |
| Automation/input | Host-independent fixed-capacity preparation/translation where useful | Independent sample-by-sample expression oracle; previous anchor, offset-N endpoint/carry, same-offset order, discrete thresholds; all three bus/owner overlap cases. |
| State/concurrency | Explicit UI/audio ownership protocol; existing controls IO off callback | v1/v2/v3 migration, held-note preservation, pending/acknowledged saves, queue full, delayed UI, concurrent reads/writes and supported lock-free atomics. |
| Qualification | Separate SDK-aware native harness, allocation instrumentation and retained report | Load actual module/factory, initialize controller/processor, exercise legal host calls, run SDK validator against that exact bundle; retain artifact/source/toolchain identity and truthful exclusions. |

The native harness must exercise 44.1/48/96 kHz; zero, one, irregular and maximum
blocks; overlapping upper/lower/pedal owners; all parameter records; old-state
loads; no editor; stopped rate changes; boundary carry; full capacities and one
over; late invalid input; and restoration under active processing. Compare
audio/clock/ownership with one direct-core reference, instrument allocations and
deallocations on the actual callback, and retain failed-call state/output
sentinels. An independent automation oracle must not reuse the production
interpolator. Run the SDK validator on the built Hammond module, not just
`validator -selftest`.

Those checks establish an early native SDK/ABI smoke gate only. Actual DAW
project save/reopen, host scheduling quirks, musical use, audio-device
underruns/deadlines, clean-machine install, Windows/macOS builds, UI usability,
signing and physical fidelity remain separately named pending gates until
observed. Report each result against the exact staged tree and artifact hash;
do not inherit a result from a different live header/library combination.
