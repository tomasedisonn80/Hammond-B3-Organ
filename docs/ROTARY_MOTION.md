# Rotary motion primitives and event clock

`include/hammond/RotaryMotion.h` and `src/RotaryMotion.cpp` implement one
rotor's kinematics for `nominal-effective-mouth-rotary-v1`, under the frozen
[rotary-numerics-v1 contract](ROTARY_NUMERICAL_CONTRACT.md). They have no host,
audio, geometry or profile-file dependency. The source basis is the atlas's
first-order motion and persistent-clock discussion, especially pp. 292 and
319–324. The [research scope](ROTARY_SCOPE.md) retains the missing measured
motor, radiation, cabinet and upstream electrical evidence.

The module contains composable constant-command evaluations and a small
`RotaryMotion` owner. It does not retain an entire command history. The later
renderer must retain the anchors or snapshots needed for delayed emission
queries. Horn and drum each require their own owner and history.

## Admitted inputs and guarantees

The shared definitions remain in `RotaryTypes.h`. Native sample rates are
exactly 44,100, 48,000, 96,000 and 192,000 Hz. An epoch lasts at most 86,400
seconds. Speeds are finite magnitudes in `[0,200]` rad/s, slow speed cannot
exceed fast speed, each finite time constant lies in `[0.001,60]` seconds,
and direction is exactly `-1` or `+1`. Phase is finite and in `[0,2*pi)`.
There are only Chorale and Tremolo commands.

All public functions are `noexcept`, perform bounded work and use no dynamic
allocation, locks or I/O. Every rejected operation preserves its destination
and, for owner methods, the entire existing owner. The owner has value
semantics and is trivially copyable. It assumes serialized access; it is not
a concurrent command queue.

`validate_motion_profile` checks only the kinematic fields.
`validate_motion_state` admits any signed 64-bit completed-turn count, so
retained states can be composed without converting that counter to a double.
Neither validator establishes full scene admission, provenance, radiation
geometry, buffer capacity or physical fidelity. Preparation starts with zero
turns; pure helpers also accept nonzero turns for composition and rate epochs.

## Pure segment API

| Operation | Behavior |
| --- | --- |
| `make_motion_segment(profile, initial, command, anchor_frame, destination)` | Validates the inputs, selects the target and time constant, and publishes one constant-command anchor. |
| `evaluate_motion_segment(segment, elapsed_s, destination)` | Evaluates physical elapsed time in `[0,86400]` seconds and returns `MotionEvaluation`. |
| `evaluate_motion_segment_at(segment, position, sample_rate, destination)` | Evaluates an integer-frame-plus-fraction position relative to the supplied anchor. |
| `evaluate_motion_prehistory(initial, direction, seconds_before_zero, destination)` | Extrapolates uniformly at the epoch seed's current speed for a time in `[-86400,0]` seconds. |
| `evaluate_motion_prehistory_at(initial, direction, position, sample_rate, destination)` | Applies the same prehistory policy to a floor-index sample position. |

`MotionEvaluation` contains the resulting wrapped `MotionState` and a separate
signed `angle_increment_rad`. The latter makes very small motion observable
even when adding it to an existing phase would round to that same binary64
phase. It is the increment from the supplied segment seed, not an absolute
unwrapped angle. A zero-duration query returns the seed exactly and an
increment of zero.

The selected time constant follows **target minus current speed**: positive
error uses `tau_up_s`, negative error uses `tau_down_s`; equality uses the
upward constant, whose value then has no effect. A switch to Chorale while
the rotor is still below its slow target therefore uses the upward constant.

For initial speed `w0`, target `wt`, elapsed time `h`, direction `sigma`,
and `z=h/tau`, the continuous solution is

```text
w(h) = wt + (w0-wt)*exp(-z)
angle_increment = sigma * (wt*h + (w0-wt)*tau*(1-exp(-z)))
```

These formulas specify the analytical first-order model; the implementation
evaluates them with binary64 arithmetic. For `z < 1/8`, it uses
`q=-expm1(-z)` and a fixed polynomial for
`g=z+expm1(-z)=z^2/2!-z^3/3!+...+z^12/12!`, then evaluates
`w0+(wt-w0)*q` and `w0*h+(wt-w0)*tau*g`. This avoids cancellation of the
quadratic angle at a start from rest. For larger `z`, the direct exponential
speed residual retains small decays toward zero. The integrated long-time
form avoids cancellation between large terms. `fma` reduces local rounding
in the angle and speed calculations. There is no numerical iteration loop.

The angle increment is reduced using the shared binary64 `kTwoPi`, with a
wrapped phase and an integer turn change. Adding that change to the retained
counter is checked using integer arithmetic before publication. The complete
turn counter is never converted to double. A near-boundary result can round
to either equivalent phase/turn representation; comparison to the
[independent reference](ROTARY_REFERENCE.md) must use circular phase error or
an appropriate reconstructed angle, rather than demand identical raw turn
counts at a wrap. The separately returned increment retains the small-motion
information that wrapping cannot represent.

## Frame and fractional timing

`SamplePosition{frame, fraction}` means `(frame + fraction)/Fs`, where `frame`
is a signed integer and `fraction` is finite in `[0,1)`. Negative positions
use floor semantics: `{-1,0.75}` means one quarter of a sample before zero.
The positive epoch endpoint permits only fraction zero. Mathematical
prehistory is admitted down to the corresponding negative one-day endpoint;
the renderer's actual history requirement is much shorter and separately
bounded.

Sample queries subtract integer anchor frames before any floating conversion.
The elapsed frame count is divided into whole seconds and residual frames;
the latter are combined with the fractional sample only within that final
second. The helper evaluates the whole interval and then its fractional
tail. This preserves fractional timing late in an epoch, without forming a
large floating-point sample index. The split depends only on the original
event anchor and the query position, never on host block boundaries.

The physical-time helper has no sample rate. It admits an anchor only within
the largest supported epoch; the sample-position helper additionally checks
that anchor against the supplied rate. Passing a positive position earlier
than a retained segment's anchor returns `InsufficientHistory`. The segment
helper also returns that status for a negative position; explicit prehistory
uses its dedicated helper.

## Owner lifecycle and command semantics

```cpp
#include "hammond/RotaryMotion.h"

using namespace hammond::rotary;
RotaryMotion horn;
const MotionProfile motion{4.0, 40.0, 0.7, 1.1, 1}; // Synthetic example.
const auto prepared = horn.prepare(motion, 0.25, 4.0,
                                   SpeedCommand::Chorale, 48000.0);
if (prepared == Status::Ok) {
    const auto commanded = horn.apply_command(24000, SpeedCommand::Tremolo);
    if (commanded == Status::Ok) {
        MotionState predicted;
        const auto queried = horn.state_at({36000, 0.5}, predicted);
        // Inspect queried before using predicted. A query does not advance horn.
        (void)queried;
    }
}
```

The example values are mathematical examples, not measured instrument data.

| Method | Lifecycle effect |
| --- | --- |
| `prepare(...)` | Replaces the owner after admission, sets frame zero, and remembers the original state and command for reset. |
| `advance_to(frame)` | Observes the current segment at a nondecreasing integer frame; retains its original anchor. |
| `apply_command(frame, command)` | Observes the old segment at the event boundary, preserves phase and speed, and creates an anchor only if the command changes. |
| `state_at(position, destination)` | Performs a read-only query. Future predictions through the epoch endpoint are allowed. |
| `reconfigure_sample_rate(rate)` | For a stopped enclosing processor, preserves current phase, turns, speed and command, and starts a new frame-zero epoch at the accepted rate. |
| `reset()` | Restores the originally prepared state and command at the current sample rate and starts frame zero. |

Commands and advances earlier than the current observation frame reject.
Commands at the same frame are applied in input order; only the final target
has a positive-duration effect. Repeated unchanged commands may advance the
observation frame but never replace the original anchor or restart the
exponential. Zero-frame and end-of-block event transactions belong to the
enclosing renderer; the owner has no block-dependent time model.

Nonnegative queries before the owner's current segment anchor return
`InsufficientHistory`; an external history owner selects the earlier segment.
Negative queries always use the current epoch's seed and constant seed speed,
even if a command has since changed. They never extrapolate acceleration
backward. `state_at` does not change the observed frame or state and cannot
account for future commands not yet supplied.

A rate reconfiguration intentionally begins a new epoch even when the
accepted rate equals the existing rate. The enclosing processor decides when
an epoch replacement is appropriate. Its current state becomes the new
negative-time seed. Reset instead returns to the original preparation seed,
which remains distinct from that new epoch seed. Audio history disposal and
rebuilding, zero negative audio, and processing synchronization are outside
this class.

## Rejection and acceptance boundary

Invalid kinematic fields return `InvalidProfile`; an unsupported rate,
nonfinite/out-of-range physical duration, or invalid sample fraction returns
`InvalidSpec`. Invalid commands and backward owner mutations return
`InvalidEvent`. Out-of-epoch frame positions and checked turn overflow return
`TimelineOverflow`. Unprepared owner operations return `NotPrepared`.
Internal nonfinite or noncanonical arithmetic results return
`NumericalFailure`. These statuses preserve the existing owner and destination.

The [assignment evidence](development/2026-11-13-rotary/10-motion.md) records
strict compilation and focused author checks. Those checks do not qualify
the entire R2 domain. The next independent gate must compare the native
motion against the 80-digit oracle across the frozen grid and random
semigroup cases, retain worst-case locations, verify event/block invariance,
and exercise rejection and lifetime behavior. Geometry, retarded propagation,
waveform interpolation, audio processing, native adapters and physical
measurements have separate gates.
