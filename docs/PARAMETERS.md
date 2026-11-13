# Proposed internal console parameter registry

[`data/parameter-registry.json`](../data/parameter-registry.json) defines an
**original, proposed internal registry of exactly 39 controls** for the current
ideal console subset. Its schema version is `1`, model is
`ideal-exclusive-ab-console-v1`, and scope is `implemented-console-subset`.
The [console extension contract](CONSOLE_EXTENSION.md) and
[`ControlState.h`](../include/hammond/ControlState.h) own the implemented control
semantics and defaults.

This is not the absent 62-entry companion referenced by the atlas, and these IDs
are not verified VST3 exports. The atlas's proposed IDs and continuous controls
are design guidance, not a recovered machine-readable specification. Every
record carries `evidence_class: proposed` and source page locators. The registry's
provenance declares the applicable nominal B-3/AO-28 engineering subset, missing
calibration, and pending host work. No manufacturer calibration is inferred.

## Stable identities and inventory

Each of the four manual/bank combinations owns nine permanent IDs. Selection,
visibility, parameter-array order and a Cancel action never change what an ID
means. The proposed assignment is fixed for this internal version; a future
product must approve and verify its actual exported mapping before release.
Never recycle an accepted identity for a different control.

| Retained identity | Decimal IDs | Hexadecimal IDs | Count | Engine event target |
| --- | --- | --- | ---: | --- |
| Upper A drawbars | 4096–4104 | `0x1000`–`0x1008` | 9 | `bank_drawbar`, `upper`, indices 0–8 |
| Upper B drawbars | 4112–4120 | `0x1010`–`0x1018` | 9 | `bank_drawbar`, `upper`, indices 9–17 |
| Lower A drawbars | 4128–4136 | `0x1020`–`0x1028` | 9 | `bank_drawbar`, `lower`, indices 0–8 |
| Lower B drawbars | 4144–4152 | `0x1030`–`0x1038` | 9 | `bank_drawbar`, `lower`, indices 9–17 |
| Global expression | 8192 | `0x2000` | 1 | `expression`, canonical `upper`, index 0 |
| Upper bank selector | 8208 | `0x2010` | 1 | `select_bank`, `upper`, index 0 |
| Lower bank selector | 8209 | `0x2011` | 1 | `select_bank`, `lower`, index 0 |
| **Total** | | | **39** | |

The drawbar offset order is `16ft`, `5_1/3ft`, `8ft`, `4ft`, `2_2/3ft`, `2ft`,
`1_3/5ft`, `1_1/3ft`, `1ft`. These are control labels. A semantic path such as
`manual.upper.bank.B.drawbar.8ft` identifies the retained third drawbar of Upper B
(ID 4114), even while Upper A sounds or the upper route is cancelled. Flattened
event indices use `bank * 9 + drawbar`, with A = 0 and B = 1.

Expression is global. Its event uses `manual: upper` as a canonical valid filler
for the existing event structure; it does not define a separate upper expression
control. The legacy `drawbar` event addresses whichever bank is selected, so it
is deliberately not a registry target. `bank_drawbar` preserves fixed identity.

## Domains, defaults and normalized conversion

| Control class | Plain domain and unit | Default | Internal `step_count` | Normalized meaning |
| --- | --- | --- | ---: | --- |
| 36 drawbar positions | Integers 0–8, `drawbar-position` | 0 | 8 | Position fraction; never audio amplitude |
| Global expression | Finite 0–1, `normalized-linear-gain-surrogate` | 1 | 0 | Existing ideal global linear gain surrogate |
| Two bank selectors | Integers 0–1, `bank-index-0=A-1=B` | 1 (B) | 1 | Ordinal bank fraction |

`step_count` counts equal intervals between discrete values: eight intervals
yield nine drawbar positions; one interval yields two bank values. Zero denotes
the continuous expression scalar. These are internal declarations, not evidence
of a host `ParameterInfo` export. Both manual routes initially start enabled;
route-enabled state is outside this scalar inventory.

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

For expression, `x = u` and `u = x`. The current engine deliberately uses a
normalized linear-gain surrogate. This is not the atlas's proposed physical
pedal-travel/circuit model or measured expression response. Replacing that
surrogate requires an explicit version and compatibility decision.

**Difference from atlas p. 398:** the fuller proposal uses continuous marked
drawbar travel, and its documented discrete host rule is
`k = min(N, floor(u * (N + 1)))`. This internal subset instead uses the current
integer drawbar controls and the round-half-up rule above. Do not silently treat
the two rules as interchangeable. A future wrapper must specify its host law,
retained internal meaning and any migration; actual host automation is pending.

## Event mapping and Cancel

The [console extension](CONSOLE_EXTENSION.md) assigns `BankDrawbar = 5` and
`SelectBank = 6`, with fixture names `bank_drawbar` and `select_bank`. Expression
retains its existing `Expression = 3` semantics. The JSON records names, manual
and index, while the plain converted value becomes the event's value field.

Editing a bank changes only that retained position. Selecting A or B enables
the corresponding manual route and uses that bank's retained positions. Sending
a selector's already-retained value can therefore be meaningful after Cancel.
A future host adapter must account for that reselect command behavior; merely
observing that its scalar value is unchanged cannot establish that no operation
is needed.

**Cancel is an action and has no persistent parameter ID here.** The console's
`cancel` event disconnects one manual route, preserving bank selection, all
drawbar positions, expression, held keys and source phase. Cancel is different
from AllNotesOff and from setting every drawbar to zero. Do not invent a latched
Cancel toggle or a third selector value to represent it. The exclusive A/B model
also does not implement the physical multi-preset latch/loading network.

The 39 scalars alone are not a complete control snapshot: they do not include
the separate `route_enabled` bits. Replaying selector parameters as a substitute
for snapshot restoration could reconnect a cancelled route. Use the separately
validated control snapshot/persistence contract for coherent state restoration;
this registry is neither a snapshot serializer nor an exact DSP checkpoint.
Pedal drawbars, factory presets, percussion, scanner, organ/Leslie circuits,
microphones and software output controls are outside this subset.

## Validator and scalar helpers

Run from the repository root with Python 3.10 or newer:

```sh
python3 tools/validate_parameters.py data/parameter-registry.json
python3 tests/test_parameters.py -v
```

The validator uses only the standard library. It checks the exact version,
model, scope, status and evidence metadata; all 39 identities and permanent
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
| `normalized_to_value(parameter, u)` | Validated plain integer position/bank or expression scalar |
| `value_to_normalized(parameter, x)` | Validated canonical normalized value; fractional discrete values reject |
| `normalized_to_event(registry, parameter_id, u)` | Independent untimed event dictionary; performs no dispatch |

All rejected inputs raise `ParameterError`, a `ValueError` subclass. The CLI
returns 0 for accepted metadata and 1 for validation/file failure. The event
helper validates the complete registry before mapping an ID. For example:

```python
registry = load_registry("data/parameter-registry.json")
normalized_to_event(registry, 4114, 0.5)
# {"type": "bank_drawbar", "manual": "upper", "index": 11, "value": 4}
```

The dictionary intentionally has no frame or block offset. The caller owns
timing, ordering and admission. Python parsing and validation belong outside
audio processing. These scalar helpers do not implement native automation
queues, interpolation, implicit previous values, gestures, smoothing or UI
binding. They do not prove that a renderer or C++ engine consumes the dictionary.

## Evidence and remaining gates

The retained tests cover metadata rejection, complete bank/target coverage,
canonical round trips, exact half-step boundaries and adjacent floats,
nonfinite/out-of-range rejection, stable ID meaning through registry reordering
and selector-payload creation, and the position-versus-amplitude distinction.
Those are software metadata/conversion tests; actual engine state transitions
are covered by separate console tests.

Before host automation is a supported product feature, verify actual exported
IDs and units, selected versus hidden bank behavior, balanced gesture closure,
native curve timing through block partitions and zero-frame calls, explicit
same-value reselect/Cancel behavior, compatible state migration and real DAW
project recall. Preserve retired IDs and historical normalized laws after a
release freeze. These host gates and physical console fidelity remain pending.

Sources: [atlas](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf) pp. 389 and 397–402
(retained banks/state domains, permanent identities, normalized laws, gesture
binding, native curves, state and verification scope); the retained
[agent 05 review](development/agent-notes/05-atlas-pages-337-420.md); and the
[console extension contract](CONSOLE_EXTENSION.md). The original source remains
unchanged, and the absent companion's reported static checks are not local
test results.
