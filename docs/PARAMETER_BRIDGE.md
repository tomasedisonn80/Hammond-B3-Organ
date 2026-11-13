# Native internal parameter bridge

[`ParameterBridge.h`](../include/hammond/ParameterBridge.h) converts the
[45 proposed internal controls](PARAMETERS.md) into typed Engine events. Its
compiled table matches registry schema `3`, model
`exclusive-ab-percussion-pedal-console-v3`. The diagnostic export below has its own
schema `1`; this is separate from render-evidence and saved-control versions.

The bridge is stateless C++20 code with immutable literal metadata. It does not
read the registry, load files, allocate, lock, log or call a host SDK during
conversion. The lookup examines at most 45 descriptors and drawbar quantization
at most eight thresholds. These bounds describe the algorithm; they do not prove
an audio-device deadline or native-host qualification.

## API and ownership

| API | Meaning |
| --- | --- |
| `parameter_descriptors()` | Read-only span of all 45 descriptors, sorted by numeric ID |
| `parameter_descriptor(id, destination)` | Copy the requested descriptor; return false for an undefined ID |
| `normalized_to_event(id, u, offset, destination)` | Validate and convert one normalized scalar into its permanent event target |
| `plain_to_normalized(id, x, destination)` | Validate a plain scalar and return its canonical normalized value |

All functions are `noexcept`; failed checked operations leave their entire
destination unchanged. The span and descriptor string views refer to immutable
program-lifetime storage. Copied descriptors cannot mutate the table. Array order
is not parameter identity, and gaps between the defined numeric ranges reject.

Each descriptor contains ID, semantic path, kind, unit, maximum, plain default,
step count and event type/manual/index. Every minimum is zero. Text metadata and
defaults describe the existing registry; they do not add physical calibration.

For example:

```cpp
hammond::Event event;
if (hammond::normalized_to_event(4114, 0.5, 32, event)) {
    // BankDrawbar, Upper, index 11, value 4, offset 32.
    // Append in the caller's stable event order, then submit to Engine.
}
```

The supplied offset is copied exactly, including the uint32 boundary. The bridge
has no block length or clock and cannot decide whether that offset is admissible.
`Engine::process` validates the whole event sequence, half-open block bounds,
ordering, capacity and output before mutation. A successful scalar conversion
does not establish that an event was dispatched or consumed.

The event target depends only on the permanent ID. Editing Upper B remains an
Upper B edit while A is selected or the route is cancelled. Conversion emits a
selector event even when its scalar value equals a prior value: reselecting that
bank after Cancel can reconnect its route. There is no stateful deduplication.
The pedal IDs `0x4000` and `0x4001` emit `PedalDrawbar = 12`, canonical Lower,
indices 0 and 1. They remain independent of manual selection and Cancel.
Cancel, manual/pedal AllNotesOff and pedal On/Off remain explicit actions
outside this parameter inventory.

## Exact conversion laws

Normalized input must be finite and in `[0,1]`. The 36 manual drawbar controls
and two pedal mixture position controls choose integer positions 0 through 8
under the existing `floor(8u + 0.5)` mathematical
law. The two selectors and four percussion controls use `floor(u + 0.5)`.
Expression passes the finite scalar through unchanged, including signed zero.
No input is clipped into range and no position-to-audio gain law is applied.
The pedal voice separately owns `linear-pedal-position-v1`; sharing the divisor
eight does not make position normalization an audio-gain conversion.

The implementation compares against exactly representable thresholds:

| Class | Thresholds | Exact-boundary result |
| --- | --- | --- |
| Manual and pedal positions | `1/16, 3/16, 5/16, 7/16, 9/16, 11/16, 13/16, 15/16` | Higher adjacent integer position |
| Selectors and percussion | `1/2` | Selection 1 |
| Expression | None | Original value |

This avoids an intermediate floating addition rounding a value immediately below
a half threshold upward. Conversion does not change the caller's floating-point
rounding mode, and the threshold decisions do not depend on that mode. The native
contract matches the Python helper's exact integer-ratio quantizer.

Plain conversion accepts finite values within the descriptor's domain. Discrete
values must be integers. Their division by 8 or 1 is exactly representable;
expression is passed through. The returned normalized value is the canonical
representation of a plain setting. Quantization does not preserve an arbitrary
noncanonical normalized input through a round trip.

The source atlas's pp. 397-402 motivate permanent identities and frozen laws. Its
fuller proposal on p. 398 uses continuous drawbar travel and a different discrete
host conversion. This bridge preserves this repository's existing internal law.
A future host wrapper must explicitly approve its exported mapping and any
compatibility migration; these internal IDs are not asserted VST3 exports.

## Inspect the compiled mapping

Build with the standard project requirements:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --target hammond_parameter_info
./build/hammond_parameter_info
./build/hammond_parameter_info --normalized 0.49999999999999994
```

On a multi-configuration generator, select `--config Release` and use the
generator's configuration-specific executable path. No profile or JSON input is
required. The command reports the mapping compiled into the executable.

Accepted forms are exactly no arguments, `--help` alone, or `--normalized U`.
The default `U` is `0.5`. A numeric token is at most 128 bytes and uses the
repository's strict decimal grammar: optional sign, decimal significand and
optional decimal exponent. Spaces, hexadecimal notation, trailing data,
nonfinite values and nonzero underflow to zero reject. Repeated flags, missing
values, positional data and combinations with help reject. Invalid input returns
status 1 and a diagnostic on stderr, with no JSON on stdout.

Successful JSON has these exact root fields:

| Field | Value |
| --- | --- |
| `schema_version` | Integer 1 for this diagnostic export |
| `registry_schema_version` | Integer 3 |
| `model` | `exclusive-ab-percussion-pedal-console-v3` |
| `scope` | `implemented-console-subset` |
| `status` | `proposed-internal` |
| `host_exports_verified` | False |
| `native_host_curves_implemented` | False |
| `normalized` | Parsed input value |
| `parameters` | All 45 compiled records in numeric ID order |

Each record has `id`, `path`, `kind`, `unit`, `minimum`, `maximum`, `default_plain`,
`default_normalized`, `step_count` and `event`. Its event has `offset` equal to
zero, the registry's `type` and `manual` strings, `index` and converted plain
`value`. No implicit array-index mapping is needed.

The exporter constructs its entire output before writing. It uses a classic
locale, nearest-rounding formatting, binary64 `max_digits10`, ASCII JSON escaping
and an LF terminator. Output must be smaller than 32 KiB. Windows stdout is placed
in binary mode to retain LF bytes. Construction, size and stdout failures return
status 1. All stream construction and parsing occur in this offline executable,
outside the scalar bridge.

## Verification and remaining work

The native and cross-language tests are discovered by CMake; it supplies
`HAMMOND_PARAMETER_INFO_EXECUTABLE` to the Python suite. They independently compare
compiled metadata with the registry and exercise threshold neighbors, failure
atomicity, offsets, defaults and Engine application. Actual execution evidence
belongs in the [pedal development ledger](development/2026-11-13-pedals/README.md)
and [assignment 17 note](development/2026-11-13-pedals/17-pedal-parameters.md);
an interface or test description is not a completed gate.

This bridge does not supply automation queues, curve interpolation, smoothing,
balanced UI gestures, native plugin exports or DAW project recall. Those retain
the host gates in [HOST_INTEGRATION.md](HOST_INTEGRATION.md). The 45 scalar records
also omit route-enable bits; replaying selectors cannot replace a coherent
[control snapshot](CONTROL_STATE_FORMAT.md) restore. Contact travel, held pedal
contacts, percussion readiness, note ownership,
source phase and the render clock remain separate. The version-2 JSON fixture
and independent complete-record digest preserve all 43 earlier controls; only
the two pedal records are appended.

The numeric IDs, defaults and normalized domains are proposed engineering choices
for the unmeasured console subset. The source remains the
[preserved atlas](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf), pp. 139-150 and
397-402, the [pedal contract](PEDAL_INTEGRATION_CONTRACT.md), and the
existing [registry contract](PARAMETERS.md); no absent companion file or measured
manufacturer mapping was recovered.
