# Console parameter registry and adopted native mapping

[`data/parameter-registry.json`](../data/parameter-registry.json) defines an
**original, proposed internal registry of exactly 47 controls** for the retained
A/B console, exclusive fixed registrations, percussion and nominal pedal mixture
settings. Its schema version is `4`, model is `exclusive-fixed-percussion-pedal-console-v4`, and scope is
`implemented-console-subset`. The [console extension contract](CONSOLE_EXTENSION.md),
[nominal contact/percussion contract](CONSOLE_DYNAMICS.md) and
[pedal integration contract](PEDAL_INTEGRATION_CONTRACT.md),
[fixed-registration selection contract](PRESET_SELECTION_CONTRACT.md) and exact
[state/parameter contract](PRESET_STATE_PARAMETER_CONTRACT.md), together with
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

The optional [VST3 controller](VST3_CONTROLLER.md) consumes the compiled registry
bridge. Actual export of all 47 IDs and the two new conversion laws requires the
current continuation's native acceptance; previous 45-control evidence retains
its original source scope. The [native ABI](VST3_ABI_ACCEPTANCE.md) and
[behavior](VST3_BEHAVIOR_ACCEPTANCE.md) reports record actual module inspections
for their named builds. Registry validation and the SDK-free
[parameter diagnostic](PARAMETER_BRIDGE.md) do not load a plugin and therefore
do not independently qualify any native artifact.

## Version and compatibility policy

Version 4 appends exactly two exclusive preset selectors to version 3's 45
records. Every earlier ID, path, label, kind, unit, domain, default, normalized
law/meaning, event target and source/evidence field remains unchanged. Only root
provenance expands to describe the new scope. Version 3 appended two pedal
mixture positions to version 2's 43 records; version 2 appended four percussion
records to the original 39-control registry.

The immutable [version-2 registry fixture](../data/references/parameter-registry-v2.json)
was copied byte for byte from committed parent
`6768ef2388819ebbaaf7cc23bdf72265dc72c561` before editing the current registry.
Independent tests freeze both its raw bytes and every earlier complete record:

| Compatibility oracle | SHA-256 |
| --- | --- |
| All 45 version-3 records, canonical encoding | `13ba488bec90154c960c3fd700dc4a774aff5664caf5d68472821493f22d1cad` |
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

**The current validator accepts only schema 4 and the exact named model above.**
Whole schema-1 `ideal-exclusive-ab-console-v1`, schema-2
`exclusive-ab-percussion-console-v2` and schema-3
`exclusive-ab-percussion-pedal-console-v3` registry files are rejected visibly. There
is no implicit registry migration or missing-record default insertion. Consumers
must explicitly adopt the new metadata and two records. Each unchanged earlier
parameter record still works with the scalar conversion helpers.

Registry schema versioning is separate from the
[saved control format](CONTROL_STATE_FORMAT.md). The control-state reader accepts
`B3CONTROLS1`, `B3CONTROLS2` and `B3CONTROLS3` with both fixed modes initialized
to None, preserving each earlier percussion/pedal migration, and writes canonical
`B3CONTROLS4`. That migration does not imply acceptance of old registry documents.

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
| Upper preset selection | 20480 | `0x5000` | 1 | `select_preset`, `upper`, index 0 |
| Lower preset selection | 20481 | `0x5001` | 1 | `select_preset`, `lower`, index 0 |
| **Total** | | | **47** | |

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
| Two preset selectors | Integers 0–11, `preset-key-index` | 11 (Bank B) | 11 | Exclusive preset key index fraction |

`step_count` counts equal intervals between discrete values: eight intervals
yield nine drawbar positions; eleven yield twelve preset selections; one interval
yields two bank or percussion values. Zero denotes
the continuous expression scalar. These registry declarations are adopted by the
native controller, whose `ParameterInfo` exports have separate tests. Reading
this JSON alone is not an export test. Both manual routes initially start enabled;
the new selectors report the effective route, while raw route bits and retained
fixed modes remain separate snapshot fields.

Percussion values are dimensionless selection codes. Harmonic 0 selects Second,
not the fundamental; volume is not a linear amplitude, and decay is not seconds.
The engine's explicitly named percussion model owns gains, timing, routing and
continuous readiness. These four settings do not expose or serialize that history.

For each of the 44 pre-existing discrete controls with `N = step_count`, the
unchanged internal rule is:

```text
u = k / N
k = floor(u * N + 0.5), for finite 0 <= u <= 1
```

Thus drawbar `u = 0.5` sends **position 4**, not amplitude 0.5. The engine/profile
owns the position-to-gain lookup. The registry neither embeds nor applies that
gain lookup. Every half-step chooses the higher discrete value, including the
selector threshold `u = 0.5` choosing B. Inputs outside the domain, NaN, infinity
and booleans are rejected rather than clipped. For these existing kinds, the
Python helper computes the discrete result using the input float's exact integer
ratio, so intermediate
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

### Exact preset-selector normalization

Only `preset_selector` uses the new law. For normalized `u`, count the frozen
nearest-binary64 values of `(2*k+1)/22`, for k=0..10, that are less than or equal
to `u`. Equality always selects the higher key. Plain integer k maps to the frozen
nearest binary64 k/11. Both implementations use literal tables, with no runtime
division by 11 or rounding-mode changes. The exact hex tables are published in
[the frozen state/parameter contract](PRESET_STATE_PARAMETER_CONTRACT.md#4-exact-binary64-conversion-law).

The distinction matters at 3/22, 5/22, 7/22, 15/22 and 17/22: each nearest
binary64 threshold lies below the mathematical midpoint, yet equality selects
the higher key. Applying the old integer-ratio half-up formula with eleven
steps would produce the wrong result at these five values. The old kinds retain
their original law. Normalized -0 selects Cancel; new-selector plain -0 maps to
canonical +0. The existing expression and older discrete signed-zero behavior
is unchanged. Finite/range/integrality validation remains mandatory.

The new records have labels `Upper preset selection` and `Lower preset selection`,
kind `preset_selector`, unit `preset-key-index`, and normalized metadata:

```text
minimum=0.0 maximum=1.0 default=1.0
meaning=exclusive-preset-key-index-fraction
to_plain=count(u >= nearest-binary64((2*k+1)/22), k=0..10)
to_normalized=nearest-binary64(x / 11)
```

Their exact source pages are `[50,52,121,122,124,126,153,389,397,398,401,402,410,415,418]`.

| Plain value | Routing action |
| ---: | --- |
| 0 | C/Cancel; retain bank and fixed mode, disable route |
| 1–9 | C#, D, D#, E, F, F#, G, G#, A; select that fixed row and enable route |
| 10 | A#/bank A; clear fixed mode, select A and enable route |
| 11 | B/bank B; clear fixed mode, select B and enable route |

Fixed key A and adjustable A#/bank A are different identities. The selectors
are ordinary routing parameters, not host programs or whole-state recall.

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
engine from enabled state, the upper route, fixed mode None and remembered upper B selection. Changing
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

Editing a bank changes only that retained position, including while a fixed row
sounds. Old bank IDs 8208/8209 retain their 0/1 conversion and permanently target
`SelectBank`. Selecting A or B clears fixed mode, enables the corresponding
manual route and uses that bank's retained positions. Sending
a selector's already-retained value can therefore be meaningful after Cancel.
The current [HostTimeline](HOST_TIMELINE.md) and native adapter retain that
explicit reselect behavior. Merely observing that a selector's scalar value is
unchanged cannot establish that no operation is needed.

`EventType::SelectPreset = 14`, spelled `select_preset`, takes either manual,
index 0 and integral values 0–11. It does not release notes, reset source phase,
advance time or reset percussion readiness. Legacy `Cancel` remains an explicit
action; new selector value 0 invokes the same route disconnection while retaining
both remembered bank and fixed mode. It is distinct from AllNotesOff and zeroing
drawbars. There is no independently stored Cancel toggle.

The 47 scalars still cannot replace a complete control snapshot: the effective
selector collapses cancelled routes to 0 and therefore does not encode the
remembered fixed row behind Cancel. A sounding fixed row also cannot encode the
remembered adjustable bank. Restore the separate raw fixed modes, remembered
banks and route bits coherently through the snapshot/state contract. The physical
multi-latch/contact/loading model, measured preset gains, scanner, organ/Leslie
circuits, microphones and software output controls remain separate work.

## Validator and scalar helpers

Run from the repository root with Python 3.10 or newer:

```sh
python3 tools/validate_parameters.py data/parameter-registry.json
python3 tests/test_parameters.py -v
```

The validator uses only the standard library. It checks the exact version,
model, scope, status and evidence metadata; all 47 identities and permanent
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
| `normalized_to_value(parameter, u)` | Validated plain manual/pedal position, bank/percussion/preset selection or expression scalar |
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
normalized_to_event(registry, 20480, 0.5)
# {"type": "select_preset", "manual": "upper", "index": 0, "value": 6}
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
rejection and independent 39-/43-/45-record compatibility digests plus the frozen
version-2 document. New selector tests cover all eleven thresholds and neighbors,
all twelve canonical values, the five downward-rounded equality cases, all four
native rounding modes and independent rational verification. The historical
pedal catalog remains unchanged and compares its complete old45 subset with the
current47 registry.
The current focused implementation evidence is retained in
[assignment 16](development/2026-11-14-preset-continuation/16-parameter-bridge.md).
These are software metadata/conversion checks; full host timeline, publication
and native export acceptance remain separate continuation gates.

The historical native controller/ABI/behavior gates exercise their named exported IDs and
units, selected and hidden banks, callback curve timing, zero-frame processing,
retained percussion settings, independent pedal controls, same-value reselect
and compatible state migration. Their source, toolchain, artifact and scenario
bounds remain explicit in those reports; they do not establish every host or
platform result. Custom-editor gesture closure, actual DAW project save/reopen,
audio-device scheduling and physical console fidelity remain separate product
or acquisition gates. Preserve retired IDs and historical normalized laws after
a release freeze.

Sources: [atlas](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf) pp. 50–52 and
121–126 (exclusive fixed-registration source and adjustable-bank distinction),
p. 153 (control interaction), pp. 127–138
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
