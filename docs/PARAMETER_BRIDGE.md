# Compiled parameter bridge and offline diagnostic

[`ParameterBridge.h`](../include/hammond/ParameterBridge.h) converts the
[47 retained console controls](PARAMETERS.md) into typed Engine events. Its
compiled table matches registry schema `4`, model
`exclusive-fixed-percussion-pedal-console-v4`. The diagnostic export below has its own
schema `2`; this is separate from registry, render-evidence and saved-control versions.
The SDK-free diagnostic verifies its compiled scalar mapping. It neither loads
a native module nor reports the verification status of an unrelated plugin
binary. The optional [VST3 controller](VST3_CONTROLLER.md) adopts these mappings;
its [loaded-module evidence](VST3_ABI_ACCEPTANCE.md) has a separate scope.

The bridge is stateless C++20 code with immutable literal metadata. It does not
read the registry, load files, allocate, lock, log or call a host SDK during
conversion. The lookup examines at most 47 descriptors, drawbar quantization
at most eight thresholds and preset selection at most eleven thresholds. These bounds describe the algorithm; they do not prove
an audio-device deadline or native-host qualification.

## API and ownership

| API | Meaning |
| --- | --- |
| `parameter_descriptors()` | Read-only span of all 47 descriptors, sorted by numeric ID |
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
bank after Cancel or fixed selection can reconnect its route and clear fixed mode.
There is no stateful deduplication.
The pedal IDs `0x4000` and `0x4001` emit `PedalDrawbar = 12`, canonical Lower,
indices 0 and 1. They remain independent of manual selection and Cancel.
The new IDs `0x5000` and `0x5001` emit `SelectPreset = 14` for Upper and Lower,
index 0, plain 0–11. Cancel remains an explicit action and is also value 0 of
these selectors. Manual/pedal AllNotesOff and pedal On/Off remain outside this
parameter inventory. No host program or whole-state recall is created.

## Exact conversion laws

Normalized input must be finite and in `[0,1]`. The 36 manual drawbar controls
and two pedal mixture position controls choose integer positions 0 through 8
under the existing `floor(8u + 0.5)` mathematical
law. The two legacy bank selectors and four percussion controls use `floor(u + 0.5)`.
Expression passes the finite scalar through unchanged, including signed zero.
No input is clipped into range and no position-to-audio gain law is applied.
The pedal voice separately owns `linear-pedal-position-v1`; sharing the divisor
eight does not make position normalization an audio-gain conversion.

The implementation compares against exactly representable thresholds:

| Class | Thresholds | Exact-boundary result |
| --- | --- | --- |
| Manual and pedal positions | `1/16, 3/16, 5/16, 7/16, 9/16, 11/16, 13/16, 15/16` | Higher adjacent integer position |
| Legacy bank selectors and percussion | `1/2` | Selection 1 |
| New preset selectors | Eleven frozen nearest-binary64 `(2*k+1)/22` values | Higher adjacent key, including downward-rounded thresholds |
| Expression | None | Original value |

This avoids an intermediate floating addition rounding a value immediately below
a half threshold upward. Conversion does not change the caller's floating-point
rounding mode, and the threshold decisions do not depend on that mode. The native
contract for the 45 older controls matches the Python helper's retained exact
integer-ratio quantizer. The new selector kinds have a separate literal-table branch.

Plain conversion accepts finite values within the descriptor's domain. Discrete
values must be integers. Older discrete controls use their unchanged exactly
representable division by 8 or 1; expression is passed through. New preset
selectors index a frozen table of nearest binary64 k/11 values. Their plain -0
canonicalizes to +0; older signed-zero behavior is unchanged. The returned normalized value is the canonical
representation of a plain setting. Quantization does not preserve an arbitrary
noncanonical normalized input through a round trip.

### Frozen selector values

The following literals are the exact binary64 selector contract. Both native and
Python conversion select a key by threshold comparison and return canonical
values by table lookup. They perform no division by 11 or intermediate rounding
operation, and never change the caller's floating-point rounding mode.

| k | Canonical normalized k | Threshold k to k+1 |
| ---: | --- | --- |
| 0 | `0x0.0p+0` | `0x1.745d1745d1746p-5` |
| 1 | `0x1.745d1745d1746p-4` | `0x1.1745d1745d174p-3` |
| 2 | `0x1.745d1745d1746p-3` | `0x1.d1745d1745d17p-3` |
| 3 | `0x1.1745d1745d174p-2` | `0x1.45d1745d1745dp-2` |
| 4 | `0x1.745d1745d1746p-2` | `0x1.a2e8ba2e8ba2fp-2` |
| 5 | `0x1.d1745d1745d17p-2` | `0x1.0000000000000p-1` |
| 6 | `0x1.1745d1745d174p-1` | `0x1.2e8ba2e8ba2e9p-1` |
| 7 | `0x1.45d1745d1745dp-1` | `0x1.5d1745d1745d1p-1` |
| 8 | `0x1.745d1745d1746p-1` | `0x1.8ba2e8ba2e8bap-1` |
| 9 | `0x1.a2e8ba2e8ba2fp-1` | `0x1.ba2e8ba2e8ba3p-1` |
| 10 | `0x1.d1745d1745d17p-1` | `0x1.e8ba2e8ba2e8cp-1` |
| 11 | `0x1.0000000000000p+0` | None |

Equality selects the higher key at all eleven thresholds. In particular,
3/22, 5/22, 7/22, 15/22 and 17/22 round down as binary64; applying the legacy
integer-ratio half-up formula with eleven steps would select the wrong key at
those exact threshold values. The new branch is limited to `preset_selector`.
Normalized -0 is valid and produces positive-zero Cancel; plain -0 also maps to
canonical +0 for the new kind. All rejection paths preserve the destination.

The source atlas's pp. 397-402 motivate permanent identities and frozen laws. Its
fuller proposal on p. 398 uses continuous drawbar travel and a different discrete
host conversion. This bridge preserves this repository's existing internal law.
The optional [native wrapper contract](VST3_SPIKE_CONTRACT.md) explicitly adopts
this repository's IDs and conversion law. Its controller and loaded-module tests
inspect the actual exports, while this scalar API and diagnostic alone cannot
qualify a native binary. Future changes still require an explicit compatibility
migration; the atlas's differing proposal must not silently replace this law.

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
| `schema_version` | Integer 2 for this diagnostic export |
| `registry_schema_version` | Integer 4 |
| `model` | `exclusive-fixed-percussion-pedal-console-v4` |
| `scope` | `implemented-console-subset` |
| `status` | `proposed-internal`, the unchanged registry authoring status |
| `verification_scope` | `sdk-free-core-parameter-mapping` |
| `host_exports_verified` | False: this invocation does not inspect a plugin export |
| `native_host_curves_verified` | False: this invocation does not exercise native automation |
| `normalized` | Parsed input value |
| `parameters` | All 47 compiled records in numeric ID order |

### Diagnostic schema migration

Schema 2 adds `verification_scope` and replaces the schema-1 root field
`native_host_curves_implemented` with `native_host_curves_verified`. The old name
incorrectly suggested that an offline inspection executable could determine the
whole project's implementation status. Both current verification flags remain
false because this command exercises neither native exports nor native curves.
A false result here does not deny the implemented [HostTimeline](HOST_TIMELINE.md)
or separate loaded-module evidence.

Consumers must accept diagnostic schema 2 explicitly and update their exact
root-field inventory. There is no `--schema 1` compatibility mode. That earlier
diagnostic migration preserved registry schema 3 and all 45 existing records.
The fixed-registration continuation now reports registry schema 4 and 47 records
under the same diagnostic schema 2; the CLI numeric grammar, argument limits
and failure behavior remain unchanged. The frozen registry's
original provenance is retained as an authoring record; it is not a live
capability report. Diagnostic `status` continues to quote that record.

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
for this extension belongs in
[assignment 16](development/2026-11-14-preset-continuation/16-parameter-bridge.md).
The [pedal development ledger](development/2026-11-13-pedals/README.md) and
[earlier assignment 17](development/2026-11-13-pedals/17-pedal-parameters.md)
retain their 45-control evidence. An interface or test description is not a
completed gate.

The scalar bridge itself supplies no automation queue or clock. The separate
[HostTimeline](HOST_TIMELINE.md) owns sample-linear curves, callback admission and
carry; [StateExchange](STATE_EXCHANGE.md) owns concurrent control transfer; and
the [optional VST3 module](VST3_BUILD.md) exports the controls through a real SDK
boundary. Exact supported native behavior belongs to the controller, ABI and
behavior reports for their named builds. Custom-editor gesture handling, real
DAW project recall and audio-device qualification remain product gates.
The 47 scalar records expose effective routing, but not the raw fixed mode
remembered behind a cancelled route; replaying selectors cannot replace a coherent
[control snapshot](CONTROL_STATE_FORMAT.md) restore. Contact travel, held pedal
contacts, percussion readiness, note ownership,
source phase and the render clock remain separate. The version-2 JSON fixture
and independent 39-/43-record compatibility guards remain. A further complete-record
digest, `13ba488bec90154c960c3fd700dc4a774aff5664caf5d68472821493f22d1cad`,
freezes all 45 pre-selector records. The historical pedal catalog retains its
original bytes, schema and count while tests compare that explicit old45 subset
of the current47 registry.

The numeric IDs, defaults and normalized domains are proposed engineering choices
for the unmeasured console subset. The source remains the
[preserved atlas](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf), pp. 50-52, 121-126, 139-153 and
397-402, the [fixed-registration contract](PRESET_SELECTION_CONTRACT.md),
the [pedal contract](PEDAL_INTEGRATION_CONTRACT.md), and the
existing [registry contract](PARAMETERS.md); no absent companion file or measured
manufacturer mapping was recovered.
