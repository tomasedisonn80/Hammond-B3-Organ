# Rotary research profile admission

The [authoring fixture](../data/rotary/nominal-research-v1.json) configures
`nominal-effective-mouth-rotary-v1` under `rotary-numerics-v1`. It is an
explicitly **synthetic, unmeasured research profile**, with distinct horn/drum
motion and effective radiation geometry. It does not identify a physical
Leslie specimen, electrical crossover, driver or complete cabinet response.
The [scope](ROTARY_SCOPE.md) and [numerical contract](ROTARY_NUMERICAL_CONTRACT.md)
define those boundaries.

## Authoring and evidence

Every physical scalar or three-coordinate vector is a quantity object:

```json
{
  "value": 343.0,
  "unit": "m/s",
  "evidence": {
    "evidence_class": "proposed",
    "applicable_variant": "synthetic-rotary-research",
    "source_pages": [301, 302],
    "source_role": "algorithm-and-boundary-only",
    "uncertainty": null,
    "measurement_reference": null,
    "reason": "Illustrative constant; no environmental measurement exists."
  }
}
```

Page references identify the atlas's algorithm and boundary proposals. They do
not claim that the proposed numeric value was measured or documented as a
factory default. This version fixes the page basis for each quantity family.
A source revision or measured model needs its own reviewed admission contract.
All objects reject unknown fields; unit strings are exact SI conventions.

`unknowns` retains eight required null values: selected cabinet, measured rotor
geometry, measured speeds, measured transition constants, measured directivity,
normalized-amplitude-to-pressure scale, the M6 input transfer and omitted
cabinet/room/microphone responses. Each records units, `unknown` evidence, a
missing-acquisition reason and a concrete acquisition requirement. Replacing a
null with an invented value does not upgrade this profile and is rejected.

The right-handed frame has +x to the right when facing the cabinet front,
+y toward the rear and +z upward. Phase zero points along +x; positive phase
is counterclockwise when viewed from +z. Each rotor has a separate direction
sign. Microphone array order is explicitly `left`, then `right`.

## Frozen admission domain

| Quantity or relationship | Accepted domain |
| --- | --- |
| Sound speed | 300–380 m/s |
| Rotor radius | 0–1 m; zero is a stationary point diagnostic |
| Rotor origin and microphone coordinates | Each component within −10–10 m |
| Slow and fast speed magnitudes | `0 <= slow <= fast <= 200` rad/s |
| Initial speed | 0–200 rad/s, independent of the initial command target |
| Upward/downward time constants | 0.001–60 seconds |
| Direction | Exactly −1 or +1 |
| Initial phase | `0 <= phase < 2*pi` radians |
| Full-orbit rim speed | `radius * max(initial, slow, fast) <= 0.25 * sound_speed` |
| Each of four rotor/microphone paths | Minimum distance at least 0.02 m; maximum at most 20 m |
| Distance-gain reference | 0.02–10 m |

For microphone displacement `(dx,dy,dz)` from an axis origin, the validator
computes `R = hypot(dx,dy)`, minimum distance `hypot(R-radius,dz)` and maximum
distance `hypot(R+radius,dz)`. Checking the entire circle prevents admission of
a path that intersects the microphone later even when the initial angle looks
safe. Both rotors are checked against both microphones. The rim-speed limit
includes initial speed, so a nonsteady start cannot bypass the subsonic bound.
These are declared numerical operating limits, not cabinet specifications.

Only `chorale` and `tremolo` commands exist. Zero speeds can describe stationary
diagnostic inputs; they do not introduce a physical STOP/brake command. Before
time zero, each trajectory continues backward at its declared initial speed.
Waveform samples before index zero are zero. The initial command begins its
future speed trajectory at time zero while preserving that initial state.

The signal boundary fixes unity omnidirectional response and the explicit
`reference_distance / path_distance` gain. It includes no hidden level match.
The separate normalized mouth inputs exclude organ/Leslie electronics,
electrical crossover, driver response, internal horn transit, measured
directivity, cabinet reflections, room, microphone response and physical brake.
The renderer's kernel, two-frame algorithmic latency, event/storage capacity
and rate policy belong to the numerical contract and are not mutable physical
profile values.

## Validator and normalized API

From the repository root with Python 3.10 or newer:

```sh
python3 tools/validate_rotary_profile.py --input data/rotary/nominal-research-v1.json
python3 tools/validate_rotary_profile.py --input data/rotary/nominal-research-v1.json --normalized
```

The CLI emits one JSON object. Success has `status: admitted` and exit 0;
invalid input or arguments have `status: rejected`, an actionable error and
exit 2. Help is ordinary argparse text. No output file is overwritten.
Raw file SHA-256 and canonical authoring SHA-256 are separately named.
Canonical authoring uses sorted keys, compact separators, UTF-8, no final
newline and `allow_nan=False`; it is a project convention, not RFC 8785.

The standard-library module exposes:

- `validate_profile(value)`: admit an already parsed mapping, return the same
  object and never mutate it; raise `RotaryProfileError` on invalid input.
- `load_profile(path)`: read and validate a bounded UTF-8 regular file.
- `load_profile_with_digest(path)`: return the admitted mapping and SHA-256 of
  the **same bytes read once**, avoiding a separate hash/load read race.
- `normalized_profile(value)`: return a fresh, independently owned SI mapping.
- `canonical_json(value)` and `authoring_sha256(value)`: identify validated
  authoring without changing it.

| Authoring location | Normalized field |
| --- | --- |
| `speed_of_sound.value` | `sound_speed_m_s` |
| `signal_boundary.reference_distance.value` | `reference_distance_m` |
| `rotors.<name>.geometry.axis_origin.value` | `rotors.<name>.origin_m` |
| `rotors.<name>.geometry.radius.value` | `rotors.<name>.radius_m` |
| `motion.slow_speed/fast_speed.value` | `motion.slow_rad_s/fast_rad_s` |
| `motion.tau_up/tau_down.value` | `motion.tau_up_s/tau_down_s` |
| `motion.direction.value` | `motion.direction` as −1/+1 integer |
| `initial_state.angle/speed.value` | `initial_phase_rad/initial_speed_rad_s` |
| `initial_command` | Unchanged command string |
| `microphones[i].position.value` | `microphones[i].position_m` |

The normalized top level also retains schema/model/contract/profile identities,
the two prehistory policies and the fixed directivity/gain identities. Consumers
must use the same admitted source identity and their own typed conversion;
normalization does not implement runtime preparation or prove numerical parity.

## Parsing and schema limits

Admission bounds a regular file to 128 KiB, depth to 16, visited JSON values to
8,192, collections to 64 entries and strings to 1,024 characters. The parser
rejects invalid UTF-8, a BOM, duplicate JSON keys, NaN/Infinity, embedded
control characters, lone Unicode surrogates and invalid JSON. Direct Python
inputs also reject cycles, non-JSON types and booleans used as numbers. No
value is clamped, unit-converted, default-filled or silently repaired.

The [JSON Schema](../data/rotary-profile.schema.json), draft 2020-12, documents
structural types, exact field names, quantity units, evidence and scalar ranges.
Use the semantic validator for cross-field ordering, rim-speed/full-orbit
geometry equations, raw-byte bounds and exact parsed numeric types. A generic
schema may regard `1.0` as the integer constant `1`; this validator requires an
actual integer for schema and source-page metadata. Schema conformance alone
is not model admission, measured provenance or a physical-fidelity pass.

## Retained synthetic fixture

| Field | Horn | Drum |
| --- | --- | --- |
| Origin, metres | `(0, 0, 0.7)` | `(0, 0, 0.2)` |
| Effective radius | 0.18 m | 0.22 m |
| Slow/fast targets | 4 / 38 rad/s | 3 / 32 rad/s |
| Upward/downward tau | 0.45 / 0.8 s | 1.1 / 1.7 s |
| Direction | +1 | −1 |
| Initial phase/speed | 0 rad / 4 rad/s | 1 rad / 3 rad/s |

The two proposed receivers are `(-0.65,-1.2,0.8)` and `(0.65,-1.2,0.8)` metres;
sound speed is 343 m/s and distance-gain reference is 1 m. All are illustrative
test choices with missing measurement reasons. Do not relabel them as factory
dimensions, vintage rotation speeds or fitted acceleration constants.

Next acceptance is independent malformed-input/schema testing and conversion
into the bounded runtime profile, then motion and propagation comparisons under
the frozen numerical contract. This authoring layer does not close any of those
runtime, audio, host or hardware gates.
