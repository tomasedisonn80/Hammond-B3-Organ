# Native VST3 behavior acceptance

The maintained `plugins/vst3/tests/test_native_behavior.cpp` executable loads
the actual Hammond bundle through the SDK hosting module and queried native
interfaces. Its 2026-11-13 Linux Release gate passed **1/1 CTest in 2.00 seconds**.
It accepted 1,030 native callbacks, checked 72 rejected callbacks, and compared
233,792 elapsed frames against independently scheduled plain Engine references.
All 610,510 compared channel samples were bit-identical to their stated
reference or counterfactual. The precise source, executable and module identities
are retained in [assignment 35](development/2026-11-13-pedals/35-native-behavior.md).

This qualifies the declared native wrapper behavior at that snapshot. The
instrument remains the existing nominal, unmeasured dry organ; this is not a
physical Hammond comparison, DAW session, device deadline or concurrency stress
result. The [ABI gate](VST3_ABI_ACCEPTANCE.md),
[processor contract](VST3_PROCESSOR.md), [host timeline](HOST_TIMELINE.md) and
[state exchange](STATE_EXCHANGE.md) define the related boundaries.

## Independent reference and actual module boundary

`NativePlugin` opens the built `HammondB3.vst3` through
`VST3::Hosting::Module`, constructs its original factory classes, queries
`IComponent`, `IAudioProcessor` and `IEditController`, and performs native
initialization and bus activation. This test includes no `Processor.h`, uses no
processor diagnostic escape hatch, and never constructs the processor directly.
Its supplied event lists, parameter queues and state streams are host fixtures.
The returned samples and serialized controls cross the actual module ABI.

The direct reference is a separately prepared plain `Engine` with the same
compiled nominal profile, seed zero, and explicit nominal contact model. It
receives hand-authored physical events and explicitly calculated control values.
The reference never calls `HostTimeline`, either ownership adapter, the combined
input facade, or `normalized_to_event`. It shares the existing DSP implementation
with the plugin; this gate independently checks wrapper scheduling, mapping and
state composition, rather than proposing another physical synthesis oracle.

Three other reference mechanisms serve different checks:

- Closed-form dyadic equations specify expected expression values and drawbar
  steps at individual samples. These do not reuse the production interpolator.
- Complete expected `ControlSnapshot` values independently specify the targets
  of all 45 permanent IDs, including both manual route bits. Native state saves
  must agree field-for-field; expression also compares its binary64 bits.
- A second, untouched loaded module provides the counterfactual for rejected
  native callbacks. It receives the same preceding valid inputs and all later
  valid probes, but never receives the rejected call.

Initial manual registrations explicitly select bank B and populate bank B.
Separate Upper, Lower and Pedal instances assert substantial nonzero output at
each of 44,100, 48,000 and 96,000 Hz. Those **nine isolated audible cases** prevent
a silent manual registration from being hidden by pedal audio. The observed
maximum absolute levels were Upper `0.015`, Lower `0.015`, and Pedal
`0.0096094`, in the nominal normalized float scale. The maximum over all compared
workloads was `0.0906279`; no compared sample reached full scale.

## Work actually exercised

| Boundary | Executed behavior | Independent acceptance |
| --- | --- | --- |
| Musical input | All three native buses; identified overlaps across channels; duplicate identified presses; repeated anonymous presses and FIFO releases; valid filtered pitch/pressure; ignored finite tuning | Explicit first-owner on/final-owner off physical timeline; exact audio through onset, partial travel and release |
| Velocity | Smallest positive float presses a manual key and pedal; zero velocity releases the named owner | Same physical targets and sustained output as ordinary positive velocity |
| Output/time | Zero, one, irregular and 65,536-frame callbacks at all three rates; disconnected output; inactive output with null sample pointers; exact L/R alias | Exact direct-core samples or exact subsequent audio after the unobserved interval; complete sample tails and silence flags checked |
| Lifecycle | Stop/start without a reset; stopped supported rate and maximum-block changes; one-over-new-maximum rejection | Held notes, contact/percussion history and source epoch remain consistent with the phase-preserving direct Engine |
| Parameters | All 45 IDs delivered in reverse queue enumeration order, with duplicate same-offset points | Complete manually populated controls snapshot and subsequent exact audio; no production mapping helper in the expected values |
| Thresholds | Three native drawbar targets at all eight thresholds and both adjacent doubles; two selectors and four percussion switches around `1/2` | **90 native threshold cases**, exact plain values in saved state, plus audio continuation; signed-zero expression save is checked separately |
| Cancel | Both manual routes cancelled by state; absent selector; explicit same-value upper selector | Absence retains Cancel; explicit point reconnects only the upper route, preserving lower Cancel and held notes |
| Automation | Previous-sample anchor, offset-N current interpolation and retained endpoint, last-wins fresh zero ties, discrete ramp, carried notes before fresh notes | Closed-form sample values and manually ordered physical events; exact last-rendered controls before endpoint consumption |
| Partitioning | Three partitions of one 128-frame curve at each of three rates, with points at each block's N boundary | **Nine cases** match a direct per-sample equation and the unpartitioned native output bit-for-bit; final endpoint flush applies once |
| Active state | Four pending loads, newest-pending save, fifth-load rejection, malformed state rejection, failed callback retention, restore before automation, v1/v2 migrations | Complete saved controls, exact future audio with moving contacts and consumed percussion readiness; held pedal survives old-state mute and later unmute |
| Delayed UI | 32 consecutive publications without an intervening save, at each rate | Later save reports the last acknowledged automation rather than a stale state |
| Raw work/carry | 1,024 duplicate endpoint records, carry plus one rejection, 1,024 valid filtered events, 1,025 raw records, 1,023 filtered records plus a supported release, 1,024 same-sample physical transitions | No endpoint or release is dropped; exact audio and successful retry after a rejected call |
| Owners/state composition | 256 manual plus 256 pedal owners over all 122 keys and 25 pedals; each 257th owner; four queued restores while all 512 owners remain held | Explicit 147-target physical schedule, exact audio after capacity failures/restores, and all 512 final releases |

The SDK's `NoteOn.length` is not used as an automatic release. The test supplies
explicit releases and does not interpret filtered SysEx/text data. Unsupported
musical kinds and pitches remain the named processor policy, not new MIDI
features inferred by this suite.

## Automation equations and boundary evidence

The short simultaneous expression/pedal ramp starts with expression `1/4` and
pedal-mixture-one position zero. Its first normalized endpoint is at offset
15 with value one. For the current 15 rendered samples `i = 0..14`, the
reference supplies:

```text
expression[i] = 1/4 + 3*(i+1)/64
pedal_position[i] = floor((i+2)/2)
```

The native expression save after that callback must be `0.953125`, its actual
last sample, while the value one remains a pending boundary point. A subsequent
zero-frame callback combines the carried endpoint/notes with fresh duplicate
expression points, a fresh pedal position and releases of carried onsets. The
reference applies parameters first, carried music second and fresh music last.
The fresh last expression point wins; a following empty zero callback must not
replay the consumed boundary or advance the source epoch.

The partition equation is:

```text
expression[global_sample] = 1/8 + (global_sample + 1)/512
```

Each block supplies the corresponding value at its offset N. Current samples
still stop at N-1, and the retained point participates in the next block.
Partitions `[128]`, `[1,7,13,29,78]` and `[17,31,2,63,15]` have exact dyadic
values, so this fixture requires bitwise equality. It does not promise universal
bitwise invariance for host endpoints rounded differently when reparameterizing
an arbitrary curve.

A separate late-invalid-curve test has neither pending restores nor old carry
that could mask a wrongly changed anchor. After rejecting the malformed curve,
the next valid curve must reconstruct from the untouched previous-sample value.

## Rejection is checked beyond the return code

There are **59 distinct native rejection fixtures**. They cover signed counts,
missing or malformed output shapes, exact versus partial overlap, misalignment,
unsupported precision/mode, negative and excessive frame counts, host accessor
failures, unknown/duplicate queues, invalid values and offsets, unsorted events,
invalid bus/channel/pitch/identity/velocity/tuning/PPQ, malformed filtered input,
unknown/output-only event kinds, a conflicting identified note at offset N, and
point/filtered-event attempts to exceed the carry-inclusive budget.

Every fixture begins with audible held notes and consumed percussion readiness,
then retains one parameter endpoint and two musical records. Four valid state
loads are queued before the invalid callback. Its output buffers are filled with
a sentinel and its silence flags with a different sentinel. The call must fail
without changing either buffer or those flags. The newest accepted pending state
must still save correctly, and a fifth load must still reject, proving that the
failed callback did not retire pending queue slots.

The subject and untouched module then process three positive blocks: one consumes
the existing state/carry, another explicitly releases the preceding owners and
starts a fresh identified note, and the final block releases that note and lets
contacts settle. This last probe can expose an unintended hidden owner created
by partially admitted input. These post-rejection blocks compare **81,302
channel samples** exactly. An additional **61,360 channel samples** compare the
two instances during their valid setup; those are reported separately and are
not mislabeled as subsequent-audio evidence.

The dedicated raw-carry and full-owner tests add further capacity rejections.
Together with the three-rate output/curve/state cases, the suite records 72
rejected callbacks in total. Pending-state tests also reject 68 state loads;
those are separate UI operations and are not counted as audio callbacks.

## Observed final result

| Measurement | Observed result |
| --- | ---: |
| Accepted native callbacks | 1,030 |
| Rejected native callbacks | 72 |
| Accepted zero-frame callbacks | 123 |
| Plain Engine elapsed reference frames | 233,792 |
| Exact channel-sample comparisons, all scopes | 610,510 |
| Paired valid-setup channel comparisons | 61,360 |
| Paired post-rejection channel comparisons | 81,302 |
| Nonzero samples among compared values | 575,944 |
| Successful state reads | 542 |
| Rejected UI state loads | 68 |
| Threshold / partition / rate-change cases | 90 / 9 / 3 |
| Isolated audible division cases | 9 |
| Maximum observed sample error | 0, bitwise comparisons |
| Stream checksum | `3c4b24caebfdd1b9` |

The executable also performs 29,046,845 assertion checks. Most of that larger
number comes from verifying complete sentinel-filled buffer tails after small
callbacks. It is not a count of independent musical scenarios. The checksum is
a retained observation for this toolchain and stimulus, not a required
cross-platform transcendental-result identity.

## Reproduction and remaining gates

Use the pinned dependency and explicit optional build described in
[VST3_BUILD.md](VST3_BUILD.md), then run:

```sh
cmake -S . -B build-native -DCMAKE_BUILD_TYPE=Release \
  -DHAMMOND_BUILD_VST3=ON -DHAMMOND_VST3_SDK_ROOT=/absolute/path/to/vst3sdk
cmake --build build-native --config Release --target test_native_behavior --parallel 2
ctest --test-dir build-native -C Release -R '^test_native_behavior$' -V
```

CTest passes the actual bundle path and exact compiled profile to the test.
The ordinary SDK-free build does not discover or compile this native test.
Keep library, plugin, host test and public headers from one coherent snapshot.

This suite uses UI state calls sequentially while native processing is active.
It does not race those calls against a physical audio thread; actual native
concurrency stress remains separate. It observes native timing/history through
audio and saved musical controls, without direct native phase, clock, contact
or owner-table introspection. Core diagnostics provide their separately scoped
source-state evidence. Allocation/lock/system-call tracing, deadline/underrun
measurements, actual DAW use, device operation, installers, signing, the custom
interface and physical calibration remain separate gates.

The pinned SDK validator is not rerun by this test. Its retained result is
47 tests passed, zero failed, with 16 teardown diagnostics explained in the
[build record](development/2026-11-13-pedals/33-native-build.md) and independent
ABI review. No warning-free validator result is inferred here. Future agents
must preserve the actual failure and exclusion records and follow
[AGENTS.md](../AGENTS.md) when changing or publishing this native boundary.
