# Native VST3 controller and bounded state streams

The optional instrument's controller exposes **45 native parameters** through
the pinned SDK's `IEditController` interface. IDs, bounds, defaults, units and
discrete conversions come from the existing compiled
[parameter bridge](PARAMETER_BRIDGE.md). The controller does not change the
nominal sound model, create a custom editor or supply physical calibration.
The [native contract](VST3_SPIKE_CONTRACT.md) defines the wider processor,
automation, state and qualification requirements.

## Factory and interface ownership

`plugins/vst3/Factory.cpp` registers exactly two classes using the SDK factory
macros and `INLINE_UID_FROM_FUID`. The original identities remain:

| Class | UUID |
| --- | --- |
| `Hammond B3 Nominal` processor | `19f9adc0-533f-42b4-b96b-d51d6547e838` |
| `Hammond B3 Nominal Controller` | `0dee76ab-26bc-475a-bf64-f138c89fb0e0` |

The product version is `0.1.0`; the factory names the Hammond B3 Organ project
and its actual repository URL. It does not invent a contact email or use SDK
sample UUIDs. The processor is classified `Instrument|Synth`; the controller is
the separate component-controller class. FUID conversion belongs to the SDK,
including its platform-dependent byte representation.

`Controller` derives from the actual SDK `EditController` and implements the
complete native parameter interface directly over a fixed array of 45 doubles.
It creates no SDK `RangeParameter` objects, whose general conversion law is
not the repository's exact discrete law. It also creates no custom view or
parameter-observer graph. `createView` returns null so a host can present its
generic parameter controls. There is no independent custom-editor state;
optional controller `getState`/`setState` retain the SDK's `kNotImplemented`
behavior. The processor owns the musical state stream.

Every controller method requires the host's serialized UI/control thread.
The controller has no Engine pointer and does not access processing-thread
history. Repeated initialize without terminate rejects, including with a null
headless context. A later valid reinitialization restores the descriptor
defaults. Factory creation catches allocation failure and returns null.

## Native parameter contract

Enumeration follows increasing stable parameter ID. Full descriptor paths are
the title and short title; units are copied without rewriting their meaning.
All records use the root unit and `kCanAutomate`. There is no new Cancel,
per-key, panic or bypass parameter, and all initially muted drawbars stay muted.

| Control family | Count | Plain range | Native steps |
| --- | ---: | --- | ---: |
| Manual drawbars, four retained banks | 36 | Integer positions 0–8 | 8 |
| Expression | 1 | Finite normalized linear gain 0–1 | 0, continuous |
| Upper/lower bank selectors | 2 | 0=A, 1=B | 1 |
| Retained percussion switches | 4 | The existing two named states | 1 |
| Nominal pedal mixtures | 2 | Integer positions 0–8 | 8 |

Normalized-to-plain conversion calls `normalized_to_event`; plain-to-normalized
calls `plain_to_normalized`. Thus an exact drawbar midpoint selects the higher
position, with the same adjacent-binary64 and rounding-mode behavior as Engine
input. Bank and percussion midpoint `0.5` selects state 1. Plain discrete input
must be an exact integer. The SDK's scalar-return conversion methods cannot
return an error code; invalid IDs, invalid values and uninitialized calls return
the documented finite sentinel zero. Result-returning methods reject invalid
input and preserve their output/value destination.

`setParamNormalized` stores the admitted normalized scalar, including signed
zero. The host still receives the exact plain conversion when it requests a
display. No `beginEdit`, `performEdit`, `endEdit` or restart notification is sent
back to the host while reflecting a host change.

Display strings are numeric plain values in the classic locale. Expression
uses `max_digits10`, with the existing nearest-rounding guard during formatting
and parsing; the caller's floating-point rounding mode is restored. String
input is bounded to 127 ASCII code units followed by a terminator and uses the
strict existing decimal grammar. It rejects non-ASCII/full-width digits,
hexadecimal, NaN/infinity, suffixes, surrounding whitespace, unrepresentable
underflow and invalid control ranges. No locale-dependent numeric substitution
changes a musical control.

## Complete component-state restoration

`setComponentState` first parses a complete copied
[B3CONTROLS1/2/3 state](CONTROL_STATE_FORMAT.md). It then computes all 45
normalized values in a temporary fixed array. Only after every value succeeds
does one array assignment replace the controller values. This is an
all-or-nothing UI-thread operation; the absence of observers or host gestures
also prevents reentrant observation of a partially installed set.

Version 1 migrates percussion to Off/Second/Normal/Slow and both pedal mixtures
to zero. Version 2 preserves its percussion choices and migrates pedals to
zero. Version 3 preserves all current musical controls. A failed or truncated
load leaves all previously displayed values unchanged.

The two manual route-enable bits remain processor state. A snapshot with a
cancelled manual still displays its retained selected bank and retained
drawbars. Loading that controller state does not invent a selector gesture that
would reconnect the route. Held keys/pedals, ownership, contacts, readiness,
source phases and clock never enter this controller state projection.

## Shared native stream helpers

`StateStream.h/.cpp` supplies these functions in `hammond::vst3`:

```cpp
Steinberg::tresult read_control_state(
    Steinberg::IBStream*, ControlSnapshot&) noexcept;
Steinberg::tresult write_control_state(
    Steinberg::IBStream*, const ControlSnapshot&) noexcept;
```

Both are control-thread operations and may allocate. Neither retains the
`IBStream*`, touches Engine, seeks the stream, or schedules parsing on audio.
The processor uses the copied result with
[StateExchange](STATE_EXCHANGE.md); it must not call these helpers in `process`.

Reading starts at the supplied current position and consumes at most 16,385
bytes: the inclusive 16 KiB state bound plus one byte to detect overflow.
Successful short reads continue. A zero-byte result with `kResultOk` or
`kResultFalse` is the explicit EOF convention; `IBStream` has no distinct EOF
enumerator. Other result codes, failure with positive bytes, negative counts,
overreported counts, oversized input and invalid grammar reject. The entire
snapshot destination is unchanged on failure. The stream position may advance;
an arbitrary external stream offers no general rollback.

Writing validates and serializes the entire snapshot before its first external
write. Successful partial writes continue; zero progress, error status or
inconsistent counts fail. Invalid snapshots cause no write. An external write
failure can leave a prefix in the stream, so this helper does not claim atomic
file publication or truncation. The caller owns that policy.

Both helpers map `std::bad_alloc` to `kOutOfMemory` and other caught exceptions
to `kInternalError`. Null streams return `kInvalidArgument`. The bounded loops
require progress on each nonterminal iteration and cannot retry indefinitely.

## Executed focused evidence

The maintained test is
[`plugins/vst3/tests/test_native_controller.cpp`](../plugins/vst3/tests/test_native_controller.cpp).
It compiles the actual controller and stream helper against the pinned SDK and
core. Its expected 45 metadata records are independent literals read from the
versioned JSON registry, not the production compiled table. Its stream fixture
implements `IBStream` with deliberate short transfers and malformed replies.

The coherent GCC 14.2.0 Release execution passed **41,795 checks**, including
**3,720 exact discrete-threshold cases across all four standard rounding
modes**, **387 native string round trips**, and **306 rejected stream/load
cases**. It covers all 45 descriptors, defaults and valid discrete positions;
native reference-query creation; lifecycle; quiet state 1/2/3 migrations;
signed zero and subnormal expression; exact 16 KiB admission and one-byte
overflow; every incomplete final-state prefix; current-position reads; partial
I/O; failure/count/progress/exception handling; and unchanged destinations.

The [assignment record](development/2026-11-13-pedals/32-native-controller.md)
retains exact source/build identities and initial test-fixture corrections.
This focused executable is not a dynamically loaded module/DAW test. Actual
module factory loading, processor behavior, validator runs, concurrent active
state calls, callback allocation and platform builds have separate assignments.

With the optional build integration and a verified SDK checkout:

```sh
cmake -S . -B build-vst3 -DCMAKE_BUILD_TYPE=Release \
  -DHAMMOND_BUILD_VST3=ON -DHAMMOND_VST3_SDK_ROOT=/path/to/vst3sdk
cmake --build build-vst3 --target test_native_controller --parallel 2
ctest --test-dir build-vst3 -C Release -R '^test_native_controller$' --output-on-failure
```

The implementation was checked against the pinned primary SDK definitions for
[`IEditController`](https://github.com/steinbergmedia/vst3_pluginterfaces/blob/4f547e8e102b47de4a8b8aaf343c73b700786372/vst/ivsteditcontroller.h),
[`IBStream`](https://github.com/steinbergmedia/vst3_pluginterfaces/blob/4f547e8e102b47de4a8b8aaf343c73b700786372/base/ibstream.h),
and the SDK's
[`factory macros`](https://github.com/steinbergmedia/vst3_public_sdk/blob/586dc5e6c8012c3e4b01c79389375cbe96bdb1da/source/main/pluginfactory.h).
Future edits must preserve permanent IDs and the declared host-thread contract,
repeat the affected focused/native gates, and update the actual evidence.
