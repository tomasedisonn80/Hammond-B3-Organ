# Independent rotary motion and propagation reference

`tools/rotary_reference.py` is the offline oracle
`decimal-motion-cartesian-bisection-rotary-reference-v1`. It supports the
separately identified `nominal-effective-mouth-rotary-v1` model and
[rotary-numerics-v1 contract](ROTARY_NUMERICAL_CONTRACT.md).
It uses Python 3.10 or newer and only the standard library.

The source basis is atlas pp. 289-294, 301-306 and 319-324. The source's
original companion programs are absent; this program is a new implementation,
with its own numerical results and limitations. The
[research scope](ROTARY_SCOPE.md) preserves the missing physical, upstream
electrical and product evidence. No fixture value is a measured cabinet value.

## Independence and precision

Motion uses an explicit, private **80-digit Decimal context**. Neither caller
precision/rounding nor host block partitions control the integration. Scalar
strings and `Decimal` values preserve decimal intent; a Python float is read
as its exact binary64 value with `Decimal.from_float`. Thus a normalized JSON
profile supplies the same binary64 parameter values intended for the C++ core.
Use decimal strings for separately specified exact mathematical examples.

The propagation calculation uses independently constructed Cartesian position,
velocity and norm operations in binary64, together with Decimal motion and
time differences. **It is not an 80-digit geometric or transcendental solver.**
It uses conservative bisection of local delay, without importing a production
solver or its stopping logic. The profile loader is shared for document
admission and source-byte identity only; no motion or geometric implementation
is imported from it.

The reference default is at most **96 bisections** and absolute local
travel-time residual at most **1e-14 seconds**. A tighter positive tolerance
can be requested for a convergence study; failure to meet it raises
`ReferenceError`. The runtime's separate residual budget remains 1e-11 seconds.
No threshold is changed according to an observed result.

## Motion API and timeline

```python
from decimal import Decimal
from tools.rotary_reference import CommandEvent, MotionProfile, RotorTimeline

profile = MotionProfile("4", "40", "0.7", "1.1", direction=1)
trajectory = RotorTimeline(
    profile,
    initial_phase_rad="0.25",
    initial_speed_rad_s="4",
    initial_command="chorale",
    events=(
        CommandEvent("0.5", "tremolo"),
        CommandEvent("0.9", "chorale"),
    ),
)
state = trajectory.state_at(Decimal("0.75"))
phase_rad, completed_turns = state.wrapped()
```

These illustrative values are synthetic. Public records use SI field names:

| API | Meaning |
| --- | --- |
| `MotionProfile(slow_rad_s, fast_rad_s, tau_up_s, tau_down_s, direction)` | Independent targets, time constants and sign for one rotor |
| `MotionState(angle_rad, speed_rad_s)` | Decimal unwrapped angle and nonnegative speed |
| `evaluate_segment(initial, target_rad_s, tau_s, direction, elapsed_s)` | Analytical evaluation of one constant-target interval |
| `CommandEvent(time_s, command)` | Absolute nonnegative Decimal event time and canonical command |
| `RotorTimeline(...).state_at(time_s)` | Physical state from the correct historical anchor |
| `RotorTimeline(...).command_at(time_s)` | Command active at the observation boundary |
| `frame_time(frame, sample_rate)` | Integer frame/rate relation evaluated in the private context |

`chorale` and `tremolo` are the only accepted command spellings. The initial
command establishes the target for time at or after zero, even when initial
speed differs from that target. For negative time, angle extrapolates the
**initial speed uniformly**, with the declared sign. It does not extrapolate
the first acceleration segment backward. This is the agreed synthetic startup
policy; no physical pre-start command history is asserted.

The optional keyword `initial_turns` retains an existing signed 64-bit turn
count when constructing an offline rate-epoch comparison. Authoring profiles
start at turn zero. A new timeline still starts a new time origin and explicit
prehistory; it does not recover discarded audio tails.

Events must arrive in nondecreasing absolute time order. At one timestamp,
the final command in input order has the positive-duration effect. A command
equal to the current command does not create a new anchor. An event preserves
angle and speed at its boundary; only the subsequent derivative changes. The
time constant is selected from target minus current speed, so a switch toward
Chorale may still accelerate a rotor that remains below its Chorale target.

The timeline, command events, motion parameters and states are immutable. Its
complete offline history allows at most 4,096 input events; it is not the
runtime's bounded delayed-history ring. Positive event/query time is limited
to 86,400 seconds. Mathematical motion queries also permit negative times
down to -86,400 seconds. Actual runtime startup needs only its finite
propagation and interpolation prehistory.

For elapsed `h`, `z=h/tau`, the reference evaluates the exponential solution.
Below `z=0.5`, it independently sums
`q=z-z^2/2!+z^3/3!-...` and `g=z^2/2!-z^3/3!+...`, then uses
`speed=w0+(target-w0)*q` and
`angle_increment=direction*(w0*h+(target-w0)*tau*g)`.
The series has an explicit 2,048-term offline bound and requires convergence
at the private precision. For larger `z`, the direct exponential speed
residual preserves very small decay tails and the integrated long-time form
avoids subtracting large nearly equal angle terms. Zero duration returns the
initial state exactly.

Motion states admit compact Decimal exponents through the private context's
smallest subnormal exponent (`-1000000078` at 80 digits). This is necessary for
a valid full-day decay with a 0.001-second time constant: its positive speed
tail has an exponent near -37.5 million. Ordinary scalar arguments retain the
tighter absolute exponent limit of 1,000,000. Both paths require finite values,
at most 256 significant digits and the same physical bounds; zero is stored
canonically. This corrects the independent review's rejected full-epoch decay
without dropping a positive tail or loosening numerical acceptance budgets.

Wrapping uses a long mathematical `2*pi` constant. Compare native phase with
circular error or an unwrapped angle including turns. Within floating-point
error of a wrap boundary, a native phase/turn pair need not have the oracle's
raw turn integer while representing the same physical angle.

## Geometry and retarded path

```python
from tools.rotary_reference import CircularGeometry, solve_retarded_path

mouth = CircularGeometry(origin_m=(0, 0, 0.8), radius_m=0.2)
result = solve_retarded_path(
    trajectory, mouth, microphone_m=(1.3, -0.4, 1.0),
    observation_time_s="0.75", sound_speed_m_s=343,
    reference_distance_m=1,
)
assert abs(result.residual_s) <= 1e-14
```

Coordinates use the declared right-handed frame with the circular path in
the XY plane. At emission time `e`, the reference forms the Cartesian source
position and tangential velocity from the historical state, then calculates
`r=norm(microphone-position)` and the unit vector `u` from source to microphone.

For observation time `t`, the root variable is **delay** `d=t-e`:

```text
G(d) = d - r(t-d)/c = 0
G'(d) = 1 - dot(u, velocity)/c
received_frequency/source_frequency = 1/G'(d)
```

Subtracting `d` from a large observation time occurs in Decimal arithmetic.
The residual is calculated from local delay and distance, avoiding a loss of
precision caused by binary64 subtraction of large absolute timestamps. The
two circular-distance extrema bracket the root. A 32-ULP geometric rounding
margin widens the bracket only; source distance and residual are not clamped.
The bisection result must satisfy its residual, positive-delay and causal
emission-time gates, or the call fails.

All four scene paths must remain between 0.02 and 20 metres over a complete
orbit. Coordinates are within +/-10 metres, radius is within 0-1 metre,
sound speed is 300-380 m/s and the maximum initial/target tangential speed
cannot exceed one quarter of sound speed. Consequently the accepted
retarded derivative lies between 0.75 and 1.25, apart from the stated
binary64 rounding allowance. These are research admission limits, not
cabinet specifications.

`PathResult` retains emission and observation times, delay, distance, actual
local residual, derivative, diagnostic Doppler ratio, position, velocity,
source-to-microphone unit vector, emission state, iterations and final bracket
width. Its pressure gain is exactly `reference_distance/distance`. There is
no automatic loudness normalization, independent pitch LFO, microphone
directivity, cabinet response or room stage.

The diagnostic incoming bearing at the microphone is `-u`.
`microphone_incidence(forward_axis, u)` checks unit-vector arguments and
returns `dot(forward_axis, -u)`. It does not apply a directional gain: the
current profile defines an ideal unity/omnidirectional receiver. Horn and
drum share no state; each microphone can query a different emission time
from the same owning rotor's trajectory.

## CLI queries and strict event files

From the repository root:

```sh
python3 tools/rotary_reference.py \
  --profile data/rotary/nominal-research-v1.json \
  --time 0 --time 0.125 --time 1 --paths
```

The command writes one JSON result with profile-byte SHA-256, model/contract
identities, precision and residual policy, physical status `unmeasured`,
and the actual queried states and paths. Decimal values are strings to
preserve their precision; binary64 geometric values are JSON numbers.
Without `--paths`, only motion is queried. Errors produce a JSON rejection
and exit code 2. Success is exit code 0. No result file is silently replaced.

A frame-range query is also available:

```sh
python3 tools/rotary_reference.py \
  --profile data/rotary/nominal-research-v1.json \
  --sample-rate 48000 --start-frame 23999 --frames 3 --step 1 --paths
```

These are **physical observation-time queries**: frame `n` means `n/Fs`.
No algorithmic latency is silently applied. To compare runtime output at
sample `n`, call `solve_retarded_path` at `frame_time(n-2, Fs)`, reflecting the
runtime's separate two-sample latency. Its waveform still needs the separate
same-cubic reference and zero samples at negative indices. This tool does
not implement waveform interpolation or audio rendering.

`--events path.json` accepts the following separate reference event format:

```json
{
  "schema_version": 1,
  "events": [
    {"frame": 0, "rotor": "horn", "command": "tremolo"},
    {"frame": 0, "rotor": "drum", "command": "tremolo"},
    {"frame": 24000, "rotor": "horn", "command": "chorale"}
  ]
}
```

Frames use `--sample-rate`, are globally nondecreasing and select exactly one
rotor. A common switch is represented by two ordered events. Duplicate keys,
unknown fields, nonfinite constants, booleans used as integers, unknown
commands and descending frames reject. Event input must be a regular file no
larger than 1 MiB with at most 4,096 rows. Its hash describes the same retained
bytes that were parsed. At most 4,096 query times can be requested. A file
containing no events still validates its sample rate.

`scene_from_normalized` adapts the admitted SI mapping supplied by the
[profile validator](ROTARY_PROFILE.md) into independent reference classes.
`load_profile_with_digest` provides the source mapping and digest from one
bounded byte read, avoiding separate read/hash identities.

## Verification boundaries and next gate

The [assignment record](development/2026-11-13-rotary/09-reference.md) retains
the actual initial checks. A tighter bisection tolerance and finite-difference
step refinement demonstrate numerical behavior of this program; they are
neither physical measurements nor qualifications of new C++ code.

The next acceptance work must independently test this API, compare native
motion and geometry against it under the frozen contract, and retain the
complete error locations. Actual delayed audio needs a separately identified
same-cubic oracle and continuous/spectral convergence study. Profile-history
capacity, transaction rollback, runtime allocation, native adapters and
hardware fidelity remain their own gates.
