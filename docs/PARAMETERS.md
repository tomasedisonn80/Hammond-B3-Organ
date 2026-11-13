# Console parameter registry and adopted native mapping

[`data/parameter-registry.json`](../data/parameter-registry.json) defines an
**original, proposed internal registry of exactly 45 controls** for the retained
A/B console, percussion and nominal pedal mixture settings. Its schema version
is `3`, model is `exclusive-ab-percussion-pedal-console-v3`, and scope is
`implemented-console-subset`. The [console extension contract](CONSOLE_EXTENSION.md),
[nominal contact/percussion contract](CONSOLE_DYNAMICS.md) and
[pedal integration contract](PEDAL_INTEGRATION_CONTRACT.md), together with
[`ControlState.h`](../include/hammond/ControlState.h),
[`Percussion.h`](../include/hammond/Percussion.h) and
[`PedalVoice.h`](../include/hammond/PedalVoice.h), own the implemented control
semantics and defaults. This registry is independent of ideal versus nominal
contact travel; selecting either contact model does not change parameter identity.

This repository-authored registry is separate from the absent 62-entry companion
referenced by the atlas. The atlas's proposed IDs and continuous controls are
design guidance, not a recovered machine-readable specification. Every record
retains `evidence_class: proposed` and source page locators. The registry's
original provenance records the nominal B-3/AO-28 engineering subset and the
missing calibration and host evidence at authoring time. Those preserved fields
are not a live capability report, and no manufacturer calibration is inferred.

The optional [VST3 controller](VST3_CONTROLLER.md) now adopts all 45 IDs, units,
defaults and conversion laws. The [native ABI](VST3_ABI_ACCEPTANCE.md) and
[behavior](VST3_BEHAVIOR_ACCEPTANCE.md) reports record actual module inspections
for their named builds. Registry validation and the SDK-free
[parameter diagnostic](PARAMETER_BRIDGE.md) do not load a plugin and therefore
do not independently qualify any native artifact.

## Version and compatibility policy

Version 3 appends exactly two pedal mixture position records to version 2's 43
records. Every earlier ID, path, label, kind, unit, domain, default, normalized
law/meaning, event target and source/evidence field remains unchanged. Version 2
previously appended four percussion records to the original 39-control registry.

The immutable [version-2 registry fixture](../data/references/parameter-registry-v2.json)
was copied byte for byte from committed parent
`6768ef2388819ebbaaf7cc23bdf72265dc72c561` before editing the current registry.
Independent tests freeze both its raw bytes and every earlier complete record:

| Compatibility oracle | SHA-256 |
| --- | --- |
| Complete version-2 fixture bytes | `658858a8e0f3e722ae1deef1c80e799ab5761c60213af22d5e80696996fd50f5` |
| All 43 version-2 records, canonical encoding | `5e161206e203cce130330b993590d892182c4ead62daba50b468b5348d70bed2` |
| Original 39 records from commit `7a24a30`, canonical encoding | `61669b54e0a0499da950ece28c855e70ab4cb815d204f625f0aee8542d8b4f1b` |

The canonical encoding sorts those records by numeric ID, sorts object keys
recursively, uses compact JSON separators `(',', ':')` and ASCII JSON escaping,
then hashes the ASCII bytes. The frozen expected digests live in
[`tests/test_parameters.py`](../tests/test_parameters.py), independently of the
validator's expected-record generator. Preserve the fixture and digests; do not
regenerate them to approve an accidental change. Record ordering is free and
does not affect the canonical digest.

**The current validator accepts only schema 3 and the exact named model above.**
Whole schema-1 `ideal-exclusive-ab-console-v1` and schema-2
`exclusive-ab-percussion-console-v2` registry files are rejected visibly. There
is no implicit registry migration or missing-record default insertion. Consumers
must explicitly adopt the new metadata and two records. Each unchanged earlier
parameter record still works with the scalar conversion helpers.

Registry schema versioning is separate from the
[saved control format](CONTROL_STATE_FORMAT.md). The control-state reader accepts
`B3CONTROLS1` and `B3CONTROLS2` with explicitly muted pedal controls and writes
`B3CONTROLS3`; that migration does not imply acceptance of old registry documents.

## Stable identities and inventory

Each of the four manual/bank combinations owns nine permanent IDs. Selection,
visibility, parameter-array order and a Cancel action never change what an ID
means. The assignment is fixed for this internal version and has been explicitly
adopted by the optional native wrapper. Actual artifact/host qualification still
belongs to the named native and product gates. Never recycle an accepted identity
for a different control.

| Retained identity | Decimal IDs | Hexadecimal IDs | Count | Engine event target |
| --- | --- | --- | ---: | --- |
| Upper A drawbars | 4096–4104 | `0x1000`–`0x1008` | 9 | `bank_drawbar`, `upper`, indices 0–8 |
| Upper B drawbars | 4112–4120 | `0x1010`–`0x1018` | 9 | `bank_drawbar`, `upper`, indices 9–17 |
| Lower A drawbars | 4128–4136 | `0x1020`–`0x1028` | 9 | `bank_drawbar`, `lower`, indices 0–8 |
| Lower B drawbars | 4144–4152 | `0x1030`–`0x1038` | 9 | `bank_drawbar`, `lower`, indices 9–17 |
| Global expression | 8192 | `0x2000` | 1 | `expression`, canonical `upper`, index 0 |
| Upper bank selector | 8208 | `0x2010` | 1 | `select_bank`, `upper`, index 0 |
| Lower bank selector | 8209 | `0x2011` | 1 | `select_bank`, `lower`, index 0 |
| Percussion enabled | 12288 | `0x3000` | 1 | `percussion`, `upper`, index 0 |
| Percussion harmonic | 12289 | `0x3001` | 1 | `percussion`, `upper`, index 1 |
| Percussion volume | 12290 | `0x3002` | 1 | `percussion`, `upper`, index 2 |
| Percussion decay | 12291 | `0x3003` | 1 | `percussion`, `upper`, index 3 |
| Pedal Mixture 1 | 16384 | `0x4000` | 1 | `pedal_drawbar`, canonical `lower`, index 0 |
| Pedal Mixture 2 | 16385 | `0x4001` | 1 | `pedal_drawbar`, canonical `lower`, index 1 |
| **Total** | | | **45** | |

The manual drawbar offset order is `16ft`, `5_1/3ft`, `8ft`, `4ft`, `2_2/3ft`, `2ft`,
`1_3/5ft`, `1_1/3ft`, `1ft`. These are control labels. A semantic path such as
`manual.upper.bank.B.drawbar.8ft` identifies the retained third drawbar of Upper B
(ID 4114), even while Upper A sounds or the upper route is cancelled. Flattened
event indices use `bank * 9 + drawbar`, with A = 0 and B = 1.

Expression is global. Its event uses `manual: upper` as a canonical valid filler
for the existing event structure; it does not define a separate upper expression
control. The legacy `drawbar` event addresses whichever bank is selected, so it
is deliberately not a registry target. `bank_drawbar` preserves fixed identity.

The percussion paths are `percussion.enabled`, `percussion.harmonic`,
`percussion.volume` and `percussion.decay`. Their IDs occupy unused space in this
repository's internal inventory. They do not copy the atlas's proposed allocation:
the atlas assigns different meanings in parts of these ranges, and its complete
62-entry companion remains absent. Actual VST3 export identity must be inspected
at the native boundary rather than inferred from these numbers alone.

The two pedal paths are `pedal.drawbar.mixture1` and `pedal.drawbar.mixture2`,
with labels **Pedal Mixture 1** and **Pedal Mixture 2**. Their targets are
independent of the manual banks. Canonical `lower` is an event admission
convention; it does not map pedals into lower-manual keys or make their controls
follow that manual's selector or Cancel state. The adopted nominal voice does
not justify calibrated footage labels.

## Domains, defaults and normalized conversion

| Control class | Plain domain and unit | Default | Internal `step_count` | Normalized meaning |
| --- | --- | --- | ---: | --- |
| 36 manual drawbar positions | Integers 0–8, `drawbar-position` | 0 | 8 | Position fraction; never audio amplitude |
| Global expression | Finite 0–1, `normalized-linear-gain-surrogate` | 1 | 0 | Existing ideal global linear gain surrogate |
| Two bank selectors | Integers 0–1, `bank-index-0=A-1=B` | 1 (B) | 1 | Ordinal bank fraction |
| Percussion enabled | Integers 0–1, `enabled-index-0=off-1=on` | 0 (Off) | 1 | Retained binary setting |
| Percussion harmonic | Integers 0–1, `harmonic-index-0=second-1=third` | 0 (Second) | 1 | Retained binary setting |
| Percussion volume | Integers 0–1, `volume-index-0=normal-1=soft` | 0 (Normal) | 1 | Retained binary setting |
| Percussion decay | Integers 0–1, `decay-index-0=slow-1=fast` | 0 (Slow) | 1 | Retained binary setting |
| Two pedal mixture positions | Integers 0–8, `drawbar-position` | 0 (Muted) | 8 | Position fraction; never audio amplitude |

`step_count` counts equal intervals between discrete values: eight intervals
yield nine drawbar positions; one interval yields two bank or percussion values. Zero denotes
the continuous expression scalar. These registry declarations are adopted by the
native controller, whose `ParameterInfo` exports have separate tests. Reading
this JSON alone is not an export test. Both manual routes initially start enabled;
route-enabled state is outside this scalar inventory.

Percussion values are dimensionless selection codes. Harmonic 0 selects Second,
not the fundamental; volume is not a linear amplitude, and decay is not seconds.
The engine's explicitly named percussion model owns gains, timing, routing and
continuous readiness. These four settings do not expose or serialize that history.

For a discrete control with `N = step_count`, the internal rule is:

```text
u = k / N
k = floor(u * N + 0.5), for finite 0 <= u <= 1
```

Thus drawbar `u = 0.5` sends **position 4**, not amplitude 0.5. The engine/profile
owns the position-to-gain lookup. The registry neither embeds nor applies that
gain lookup. Every half-step chooses the higher discrete value, including the
selector threshold `u = 0.5` choosing B. Inputs outside the domain, NaN, infinity
and booleans are rejected rather than clipped. The Python helper computes the
discrete result using the input float's exact integer ratio, so intermediate
floating-point rounding does not move a value just below a threshold upward.

All four percussion controls use `k = floor(u + 0.5)` and `u = k`. At the exact
threshold `u = 0.5`, enabled chooses On, harmonic chooses Third, volume chooses
Soft and decay chooses Fast. The immediately smaller binary64 value chooses
the zero selection. All four normalized defaults are exactly `0.0`.

Both pedal parameters use `k = floor(8u + 0.5)` and `u = k / 8`, with exactly
representable thresholds `1/16, 3/16, ..., 15/16`. Equality selects the higher
position; each immediately smaller binary64 value selects the lower position.
Their normalized defaults are `0.0`. The registry creates a position event,
such as `u = 0.5` becoming position 4. The voice separately applies the named
`linear-pedal-position-v1` audio-gain law. These are separate contracts even
though the current formulas both involve division by eight.

For expression, `x = u` and `u = x`. The current engine deliberately uses a
normalized linear-gain surrogate. This is not the atlas's proposed physical
pedal-travel/circuit model or measured expression response. Replacing that
surrogate requires an explicit version and compatibility decision.

**Difference from atlas p. 398:** the fuller proposal uses continuous marked
drawbar travel, and its documented discrete host rule is
`k = min(N, floor(u * (N + 1)))`. This internal subset instead uses the current
integer drawbar controls and the round-half-up rule above. Do not silently treat
the two rules as interchangeable. The [native wrapper](VST3_SPIKE_CONTRACT.md)
explicitly adopts the retained internal law above; [HostTimeline](HOST_TIMELINE.md)
reconstructs normalized curves before applying it. A later replacement needs an
explicit identity/law migration, and real DAW automation remains separately qualified.

## Event mapping and Cancel

The [console extension](CONSOLE_EXTENSION.md) assigns `BankDrawbar = 5` and
`SelectBank = 6`, with fixture names `bank_drawbar` and `select_bank`. Expression
retains its existing `Expression = 3` semantics. The JSON records names, manual
and index, while the plain converted value becomes the event's value field.

The [percussion extension](CONSOLE_DYNAMICS.md) assigns `EventType::Percussion = 8`
and fixture name `percussion`. Each of its four records targets `manual: upper`
with indices 0–3 as listed above. Upper is a required target for this event;
the Lower manual and fractional switch values are invalid. Sending a setting
changes only that retained control. Percussion eligibility is derived by the
engine from enabled state, the upper route and upper B selection. Changing
selection, Cancel or another percussion switch never rewrites a parameter ID or
its stored meaning. A scalar conversion creates an event; it does not reset
readiness or advance the engine clock.

The [pedal integration contract](PEDAL_INTEGRATION_CONTRACT.md) appends
`EventType::PedalDrawbar = 12`, named `pedal_drawbar`, with canonical `lower`,
mixture index 0 or 1 and integer position 0–8. A setting changes only its retained
pedal position. It does not edit a manual bank, close a pedal contact, change
percussion readiness or advance a source. Held pedal state and inaudible pedal
settings survive manual selection and Cancel. Pedal On, Off and AllNotesOff are
actions outside this scalar inventory.

Editing a bank changes only that retained position. Selecting A or B enables
the corresponding manual route and uses that bank's retained positions. Sending
a selector's already-retained value can therefore be meaningful after Cancel.
The current [HostTimeline](HOST_TIMELINE.md) and native adapter retain that
explicit reselect behavior. Merely observing that a selector's scalar value is
unchanged cannot establish that no operation is needed.

**Cancel is an action and has no persistent parameter ID here.** The console's
`cancel` event disconnects one manual route, preserving bank selection, all
drawbar positions, expression, held keys and source phase. Cancel is different
from AllNotesOff and from setting every drawbar to zero. Do not invent a latched
Cancel toggle or a third selector value to represent it. The exclusive A/B model
also does not implement the physical multi-preset latch/loading network.

The 45 scalars alone are not a complete control snapshot: they do not include
the separate `route_enabled` bits. Replaying selector parameters as a substitute
for snapshot restoration could reconnect a cancelled route. Use the separately
validated control snapshot/persistence contract for coherent state restoration;
this registry is neither a snapshot serializer nor an exact DSP checkpoint.
Factory presets, scanner, organ/Leslie circuits, microphones and software output
controls are outside this subset.

## Validator and scalar helpers

Run from the repository root with Python 3.10 or newer:

```sh
python3 tools/validate_parameters.py data/parameter-registry.json
python3 tests/test_parameters.py -v
```

The validator uses only the standard library. It checks the exact version,
model, scope, status and evidence metadata; all 45 identities and permanent
targets; unique uint32 IDs, paths and targets; finite domains, units, defaults
and normalized meanings; and the complete expected key set at every object
level. Record order is immaterial. File input is bounded to 256 KiB and rejects
duplicate JSON keys, malformed UTF-8, invalid JSON and nonfinite numbers.
Unknown fields and unsupported versions fail visibly. Validation is read-only.

The module's public API is:

| Function | Result |
| --- | --- |
| `load_registry(path)` | Bounded parse and full validation; returns the registry |
| `validate_registry(registry)` | Validates without mutation; returns `None` |
| `normalized_to_value(parameter, u)` | Validated plain manual/pedal position, bank/percussion selection or expression scalar |
| `value_to_normalized(parameter, x)` | Validated canonical normalized value; fractional discrete values reject |
| `normalized_to_event(registry, parameter_id, u)` | Independent untimed event dictionary; performs no dispatch |

All rejected inputs raise `ParameterError`, a `ValueError` subclass. The CLI
returns 0 for accepted metadata and 1 for validation/file failure. The event
helper validates the complete registry before mapping an ID. For example:

```python
registry = load_registry("data/parameter-registry.json")
normalized_to_event(registry, 4114, 0.5)
# {"type": "bank_drawbar", "manual": "upper", "index": 11, "value": 4}
normalized_to_event(registry, 12289, 0.5)
# {"type": "percussion", "manual": "upper", "index": 1, "value": 1}
normalized_to_event(registry, 16384, 0.5)
# {"type": "pedal_drawbar", "manual": "lower", "index": 0, "value": 4}
```

The dictionary intentionally has no frame or block offset. The caller owns
timing, ordering and admission. Python parsing and validation belong outside
audio processing. These scalar helpers do not implement native automation
queues, interpolation, implicit previous values, gestures, smoothing or UI
binding. They do not prove that a renderer or C++ engine consumes the dictionary.

## Evidence and remaining gates

The retained tests cover metadata rejection, complete bank/percussion/pedal target coverage,
canonical round trips, exact half-step boundaries and adjacent floats,
nonfinite/out-of-range rejection, stable ID meaning through registry reordering
and selector-payload creation, the position-versus-amplitude distinction, all four
percussion defaults and two muted pedal defaults, explicit historical registry
rejection and independent 39-/43-record compatibility digests plus the frozen
version-2 document.
Those are software metadata/conversion tests; actual engine state transitions
are covered by separate console tests.

The native controller/ABI/behavior gates now exercise actual exported IDs and
units, selected and hidden banks, callback curve timing, zero-frame processing,
retained percussion settings, independent pedal controls, same-value reselect
and compatible state migration. Their source, toolchain, artifact and scenario
bounds remain explicit in those reports; they do not establish every host or
platform result. Custom-editor gesture closure, actual DAW project save/reopen,
audio-device scheduling and physical console fidelity remain separate product
or acquisition gates. Preserve retired IDs and historical normalized laws after
a release freeze.

Sources: [atlas](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf) pp. 127–138
(shared percussion, routing and coupled controls), pp. 139–150 (pedal routing
and controls), p. 418 (retained settings versus eligibility), pp. 389 and 397–402
(retained banks/state domains, permanent identities, normalized laws, gesture
binding, native curves, state and verification scope); the retained
[agent 05 review](development/agent-notes/05-atlas-pages-337-420.md); and the
[console extension contract](CONSOLE_EXTENSION.md),
[nominal contact/percussion contract](CONSOLE_DYNAMICS.md) and
[pedal integration contract](PEDAL_INTEGRATION_CONTRACT.md). Atlas page locators
support the architectural/control concepts; they do not establish this repository's
numeric IDs, startup choices or normalized law as manufacturer values. The original source remains
unchanged, and the absent companion's reported static checks are not local
test results.
