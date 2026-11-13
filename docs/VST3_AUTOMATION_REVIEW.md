# Native automation interaction review

The maintained [native automation test](../plugins/vst3/tests/test_native_automation.cpp)
loads the actual VST3 module and compares simultaneous control curves with a
separately scheduled plain Engine. Its focused Linux Release run on 2026-11-13
passed with **179,958 exact stereo channel-sample comparisons**, **89,979 elapsed
reference frames**, and zero sample error. Three individual 4,096-frame native
callbacks necessarily exceed the internal 1,024-event array. Their complete
audio and subsequent audible continuation agree with the independent schedule.

This review found **no concrete production defect** in the inspected automation,
carry, state composition or slicing implementation. It adds an acceptance gate,
not a change to the parameter laws, sound model, native ABI or state format. Exact
source, module, profile, compiler and execution identities are retained in
[assignment 40](development/2026-11-13-pedals/40-native-automation-review.md).

## Gap addressed

The existing [native behavior gate](VST3_BEHAVIOR_ACCEPTANCE.md) checks all 45
single-point mappings, 90 adjacent/exact threshold cases, a two-curve boundary
ramp, 128-frame expression partitions and 59 malformed-callback fixtures. Those
remain useful separate coverage. They did not supply an all-control curve score
that necessarily expands beyond the internal event array, or compose all-bank
curves, noncanonical retained anchors, active state restores and carried/fresh
notes in one set of independently calculated musical scenarios.

This gate therefore focuses on the following interactions:

| Workload | Acceptance evidence |
| --- | --- |
| All 36 active/hidden bank drawbars, expression, two selectors, four percussion controls and two pedal mixtures curve together | Literal permanent IDs feed independently written physical targets; every saved control and both route bits match the reference |
| Four rising/falling curve legs at 44.1, 48 and 96 kHz | Exact binary32 stereo output, with exact binary64 saved expression values |
| One 4,096-frame callback versus 45 irregular callbacks | Exact body and continuation; checkpoints before/on/after every rising drawbar threshold and Boolean/turning boundaries |
| More than 1,024 generated events from only 239 raw records in the whole callback | At least 4,096 distinct expression events require internal slicing; full expected elapsed interval and future audio agree |
| Offset-N endpoint, note carry and repeated zero-frame flush | Current last sample remains distinct from future endpoint; boundary applies once; later audio follows the expected epoch |
| Noncanonical normalized anchor followed by absent and empty queues | Both forms retain the curve anchor; resumed ramps cross drawbar/switch thresholds at the calculated samples |
| Four pending states plus old carry and fresh same-offset parameter ties | Restores establish controls/anchors first; old carry is superseded by the final fresh point where specified; complete state and audio match |
| Cancel, same-value selector and carried/fresh notes | Upper explicitly reconnects while Lower remains cancelled without its queue; a later same-value Lower selector produces an independently demonstrated audible contribution |

There are nine loaded-module scenario instances: two partition forms at each of
three rates, and one restore/carry scenario at each rate. Six gap sequences are
part of those score instances. Eighteen isolated division windows repeat the
three divisions across both partition forms and three rates; they are not
eighteen different instrument models or a count of unique physical tests.

## Reference independence

The test uses the frozen [NativeHarness](../plugins/vst3/tests/NativeHarness.h)
to open the actual bundle with the SDK loader, query its factory/interfaces and
activate all three native event inputs. It does not include `Processor.h`, read
private processor diagnostics or instantiate the processor directly.

The reference prepares one plain [Engine](../include/hammond/Engine.h) with the
same compiled nominal profile, seed zero and explicit
`make_nominal_console_model()`. Expected controls are integer/dyadic formulas
and physical `Event` records. Neither `HostTimeline`, `ParameterBridge`, the
compiled parameter descriptors, note-owner adapters nor their conversion
functions create expected values. The 45 permanent IDs are a literal test array,
separate from the independently specified manual/bank/index targets.

This independence concerns wrapper scheduling and mapping. The reference and
module intentionally share the existing DSP implementation and nominal profile;
the test is not an independent acoustic model or a physical Hammond comparison.
The reference can apply unchanged idempotent controls every sample, so it has no
production curve cursor, carry representation, change-elision policy or internal
event-slicing algorithm to reproduce.

## Closed-form score and thresholds

For global score sample `n`, define integer `r = (n + 1) mod 2048`, then
`t = r` when `r <= 1024`, otherwise `t = 2048 - r`. Thus `q[n] = t/1024`,
with initial previous-sample value `q[-1] = 0`. Over samples 0–4095, q rises,
falls, rises and falls in four 1,024-sample legs.

Every manual drawbar takes either `q` or `1-q`, using four distinct fixed
nine-bit patterns for Upper A, Upper B, Lower A and Lower B. Pedal mixture one
takes q and mixture two takes `1-q`. Upper selector, percussion enable and
volume take q; Lower selector, percussion harmonic and decay take `1-q`.
Expression is:

```text
expression[n] = 1/8 + q[n]/8
```

The reference represents every normalized value by integer `U` in units of
`1/8192`. It derives drawbar position by integer division `(U + 512) / 1024`
and switch position by `U >= 4096`. These are the repository's exact half-up
thresholds, applied independently of the production bridge. No error tolerance
is fitted from observed output. The formulas, endpoints, thresholds and products
are dyadic and small enough for exact binary64 arithmetic; the acceptance is
bitwise equality, not a visually similar waveform.

The whole callback supplies five points per queue: four turning points at
1023, 2047, 3071 and 4095, plus its right endpoint at 4096. Its fourteen musical
records bring raw work to **225 + 14 = 239**, well below the input bound. The
queue enumeration is deliberately permuted independently of stable ID order.
The irregular form adds mathematically equivalent endpoints at its boundaries;
the source formula remains global and never reads a production interpolator.

At the end of the score, the last actual expression sample is `1/8`, while its
offset-N endpoint is `1/8 + 1/8192`. Saved state must first report `1/8`. A
zero-frame flush then consumes all retained endpoints and the three musical
records at the boundary. A second empty zero-frame call must not replay them.
The following 2,048 frames are compared exactly and must contain more than
1,800 nonzero mono samples.

All four banks have distinct registration patterns, and initial selectors are
explicitly **Upper A / Lower B**. The prelude separately sounds Upper, Lower and
Pedals, releases each division, then holds all three for the curve score. Each
isolated 1,024-sample sounding window requires more than 400 nonzero samples and
RMS above `0.00001`. Those criteria were chosen before the run and prevent
silent manual routes from being hidden by pedal output.

## Why this necessarily exercises slicing

Expression differs at every one of the 4,096 score samples, including reversal
points. The test independently counts those differences and requires exactly
4,096 in each whole callback. Expression is a continuous double-valued physical
control, so those samples require at least 4,096 emitted expression events under
the [implemented timeline contract](HOST_TIMELINE.md). That count alone exceeds
the fixed 1,024-record event array; drawbar/switch changes and notes add more work.

This is a lower-bound proof of required slicing, not a claim that the actual
module exposes an internal Engine-call counter. The test deliberately uses only
public native interfaces. It does not invent an observed internal slice count.
The unsliced reference advances one frame per computed control set, checks its
exact frame-clock sum, and compares every native sample and the following audible
continuation. Therefore event loss, duplicated elapsed samples or extra source
advancement cannot be concealed by a silent stress workload. The irregular
partition case compares the same score and future sequence against the whole
callback, providing a second segmentation boundary.

## Gaps preserve normalized anchors

After the consumed score endpoint, q is `1/1024`. A 16-frame curve ends at
`q = 17/1024` on sample 15, with **no offset-N point and no carry**. Thirteen
frames omit parameter changes entirely; seven more supply all 45 empty queues.
Both must preserve the noncanonical normalized anchor, not recreate it from a
rounded drawbar/switch position.

The resumed 32-frame curve is independently specified as:

```text
q[i] = (17 + 25*(i+1))/1024, i = 0..31
```

It crosses actual drawbar and Boolean thresholds. Rounding the retained anchor
to its plain control before resumption would move transitions by rendered
samples. Every resulting sample/state and a further 257 audible frames match the
reference. The whole and irregular score runs also compare this complete gap
sequence against one another.

## State, carry and Cancel composition

The second scenario starts with sustained Upper, Lower and Pedal notes. A
31-frame primer retains four parameter endpoints and three notes. Four accepted
UI state loads then replace all banks, both pedal settings and percussion
controls, and cancel both manual routes while retaining selected bank B. Each
pre-consumption save must return the newest accepted state.

At the next accepted 128-frame callback, 44 active queues cover every control
except Lower selection. For the four parameters with old carry, two fresh
offset-zero points override the carry using their final value; their next
endpoint is at 128. The other curves interpolate from the restored previous
sample to their endpoint at 127, followed by an equal point at 128. All formulas
are exact integer multiples of `1/8192`:

```text
fresh-zero curves: start + (target - start)*i/128
restored-anchor curves: loaded + (target - loaded)*(i+1)/128
```

Fresh Upper selection ends at B, the same selection stored in the cancelled
state, and must reconnect Upper. Lower has no selector queue and must remain
cancelled through the other 44 curves, carried notes, zero flushes and the next
positive block. At sample 127, expression must be `319/512`; the future endpoint
`5/8` has not replaced the actual last-sample anchor. A later zero-frame call
combines those endpoints with duplicate fresh expression points, whose last
value `1/2` wins, and explicitly ordered carried/fresh notes.

A final same-value Lower-B point reconnects Lower without altering its held
target. A copy of the plain Engine from the same epoch renders a counterfactual
that remains cancelled. The native output matches the reconnected reference
exactly and must differ audibly from that counterfactual. This checks an audible
Lower contribution, not only a route-enable bit.

## Source review findings and observability limits

Inspected [HostTimeline.cpp](../src/HostTimeline.cpp) and
[Processor.cpp](../plugins/vst3/Processor.cpp) against the
[spike contract](VST3_SPIKE_CONTRACT.md):

| Review area | Finding |
| --- | --- |
| Monotonic admission | Native and host-independent layers reject decreasing queue points and decreasing global musical offsets before rendering. Equal point timestamps are admitted and collapsed to the last value. No new malformed-input matrix was duplicated here. |
| Queue gaps | Inactive/empty curves retain their normalized anchor; active values after the final point hold. The new audible gap sequence agrees with that behavior. |
| Global ordering | Parameter slots are addressed by permanent ID, evaluated in compiled stable ID order, then carried notes and fresh notes are processed. Host queue enumeration cannot reorder that schedule. |
| Restore before curves | Candidate restores precede anchor initialization; old carry participates afterward at zero, and last fresh same-ID zero points supersede it. The native state exchange preflights commitment before candidate rendering. |
| Future boundaries | Offset-N points remain interpolation endpoints while their raw records are retained; actual rendered values, not future endpoints, update anchors. |
| Zero frames | Exactly one boundary evaluation applies admitted zero-offset work; no new carry is retained and the Engine receives zero elapsed frames. |
| Internal capacity | Before event-array exhaustion, the implementation renders the strict earlier-frame prefix and applies any current-frame tail without time; the final positive lengths cover the requested interval. The dense curve score tests its audible result. |
| Cancel semantics | Unchanged implicit selector values emit no event; explicit selector points still emit, permitting a same-value reconnect. |

The test reference orders parameters before all notes, including old carried
notes. However, many current control setters and physical note-target setters
commute within an unrendered sample. Audio equality alone cannot distinguish
every permutation of commuting operations. The precise parameter-before-note
ordering therefore rests on the inspected source in addition to the observed
combined timeline. No instrumentation or unique audio proof is claimed where
the present nominal Engine provides no distinguishing observation.

## Observed focused result

| Measurement | Result |
| --- | ---: |
| All-control score / restore-carry / embedded gap sequences | 6 / 3 / 6 |
| Accepted native callbacks / zero-frame callbacks | 231 / 18 |
| Successful complete state reads | 261 |
| Plain Engine main-reference elapsed frames | 89,979 |
| Exact native stereo channel-sample comparisons | 179,958 |
| Whole/irregular mono-sample comparisons | 19,407 |
| Audible-continuation channel comparisons | 39,948 |
| Nonzero samples among native channel comparisons | 157,150 |
| Whole callbacks necessarily requiring internal slicing | 3 |
| Guaranteed distinct expression events in those callbacks | 12,288 |
| Isolated division sounding windows | 18 |
| Minimum Upper / Lower / Pedal RMS in those windows | 0.00402141 / 0.00655038 / 0.00172213 |
| Largest Lower reconnect/cancel counterfactual difference | 0.0238609 |
| Maximum compared audio error | 0, bitwise equality |
| Peak absolute native sample | 0.198746 |
| Observed stream checksum | `5ea365699a5717c9` |

The three 1,024-frame cancelled counterfactuals are additional reference branches;
they are not counted as elapsed native/main-reference frames. The checksum and
observed levels identify this toolchain/stimulus, not required cross-platform
transcendental bit patterns. Expected behavior and pass thresholds are written
independently in the test, rather than inferred from those observed numbers.

## Reproduction and next gate

After explicit pinned SDK acquisition, the integrator's optional CMake hook
registers `test_native_automation` with the normal native aggregate:

```sh
cmake -S . -B build-native -DCMAKE_BUILD_TYPE=Release \
  -DHAMMOND_BUILD_VST3=ON -DHAMMOND_VST3_SDK_ROOT=/absolute/path/to/vst3sdk
cmake --build build-native --config Release --target test_native_automation --parallel 2
ctest --test-dir build-native -C Release -R '^test_native_automation$' -V
```

The focused worker run compiled the test with the strict Release flags and linked
verified matching frozen core/harness archives read-only; it executed the module
directly, not through CTest. Its exact command and byte identities are in the
assignment note. The next gate is root's coherent combined archive build and
actual Linux/macOS/Windows native CI on the published test source. Do not inherit
that result from the preceding native checkpoint.

This suite does not add allocation, concurrency, device-deadline, actual DAW,
custom-editor, signing or physical-fidelity evidence. The pinned SDK validator
was not rerun here; its retained 47-passed/zero-failed summary still accompanies
**16 teardown diagnostics and nine unsupported-rate error-labelled messages** in
the [native build record](development/2026-11-13-pedals/33-native-build.md).
Neither this review nor its passing audio comparisons erase those observations.
