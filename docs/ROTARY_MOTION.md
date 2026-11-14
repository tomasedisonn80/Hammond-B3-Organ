# Rotary motion primitives and event clock

`include/hammond/RotaryMotion.h` and `src/RotaryMotion.cpp` implement one
rotor's kinematics for `nominal-effective-mouth-rotary-v1`, under the frozen
[rotary-numerics-v1 contract](ROTARY_NUMERICAL_CONTRACT.md). They have no host,
audio, geometry or profile-file dependency. The source basis is the atlas's
first-order motion and persistent-clock discussion, especially pp. 292 and
319–324. The [research scope](ROTARY_SCOPE.md) retains the missing measured
motor, radiation, cabinet and upstream electrical evidence.

The module contains composable constant-command evaluations and a small
`RotaryMotion` owner. It retains only its current command anchor. The implemented
[`MotionHistoryView`](ROTARY_PROPAGATION.md) borrows caller-retained canonical
anchors for delayed emission queries; streaming retention and waveform histories
remain R4 work. Horn and drum each require their own owner and history. These
are source-tree C++ research interfaces, not an installed public SDK.

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
`g(z)/z=z/2!-z^2/3!+...+z^11/12!`, where `g(z)=z+expm1(-z)`.
The angle is evaluated as `fma((wt-w0)*h, g(z)/z, w0*h)`, then signed by
`sigma`. This is algebraically the `tau*g(z)` contribution, but avoids forming
`z*z` before a representable small angle can be scaled. Ordinary small-time
speed uses `fma(wt-w0,q,w0)`. When `z` is subnormal or has rounded to zero,
it instead uses `fma((wt-w0)/tau,h,w0)`; the omitted curvature at that scale
is below binary64 representability.

For larger `z`, speed uses the direct exponential residual. Above `z=700`,
the residual is multiplied by two `exp(-z/2)` factors, preserving a scaled
subnormal decay that a separately rounded `exp(-z)` could erase. This threshold
selects arithmetic, never a stop state. The long-time angle uses
`fma((w0-wt)*tau,q,wt*h)`. Equal-speed motion is linear, and zero elapsed time
returns the seed exactly. These are fixed-work arithmetic paths with no
numerical iteration loop. [A16](development/2026-11-14-reference-refinement/notes/A16-rotary-motion-qualification.md)
and the [independent A24 review](development/2026-11-14-reference-refinement/notes/A24-motion-independent-review.md)
retain the original underflow failures and qualified repairs.

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

If that tail has no residual whole frame and `fraction/Fs` is subnormal or
rounds to zero, the implementation applies speed slope and constant-speed
angle **per frame before multiplying by the fraction**. Whole seconds have
already been evaluated. This preserves the qualified minimum-positive sample
fractions without introducing a zero-motion cutoff; higher-order curvature is
unrepresentable at that scale.

The physical-time helper has no sample rate. It admits an anchor only within
the largest supported epoch; the sample-position helper additionally checks
that anchor against the supplied rate. Passing a positive position earlier
than a retained segment's anchor returns `InsufficientHistory`. The segment
helper also returns that status for a negative position; explicit prehistory
uses its dedicated helper.

## Owner lifecycle and command semantics

The [complete C++ caller example](ROTARY_PROPAGATION.md#small-source-tree-caller)
prepares an owner, applies a command, retains both anchors and queries a path
while the borrowed storage remains alive. Its values are synthetic.

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

## Qualified native R2 evidence

The [A16 report](development/2026-11-14-reference-refinement/reports/A16-r2-native.json)
and [A24 independent replay](development/2026-11-14-reference-refinement/reports/A24-motion-independent-review.json)
pass the named GCC 14.2.0/Linux R2 workload: seven Python methods, 3,780 native
requests, the 1,152-case frozen grid, 1,024 semigroup cases (seed `20261114016`),
all four rates, day-end fractions, and 24 event timelines with 1,272 queries.
The oracle uses 80 decimal digits; no alignment, rescaling or relaxed budget
was applied. The greatest error/budget fraction is `0.0336243143` in
reconstructed frozen-grid angle.

| Metric | Maximum absolute error | RMS error |
| --- | ---: | ---: |
| Frozen-grid speed | `1.308603e-14 rad/s` | `4.190668e-15 rad/s` |
| Frozen-grid angle increment | `6.557950e-12 rad` | `2.801127e-13 rad` |
| Day/wrap angle increment | `7.450581e-10 rad` | `1.073587e-10 rad` |
| Sample-position reconstructed increment | `1.418679e-9 rad` | `4.251926e-10 rad` |
| Native semigroup angle difference | `9.086065e-13 rad` | `5.431919e-14 rad` |
| Native semigroup speed difference | `2.842171e-14 rad/s` | `7.359079e-15 rad/s` |

The [owner evidence](development/2026-11-14-reference-refinement/reports/A16-r2-lifecycle.json)
separately records 174 transactional rejections, 32 stopped rate replacements
and 327,720 bit-identical sample-state comparisons across 131,760 partition
calls and 48 zero-frame calls. This tests the motion owner, not audio output.

Original failures remain visible: [30 initial failures](development/2026-11-14-reference-refinement/reports/A16-r2-original.json)
erased 24 positive long-decay speeds and six tiny angle increments; the
[36-case extension](development/2026-11-14-reference-refinement/reports/A16-r2-subnormal-time-original.json)
found eight physical-time speeds, 24 fractional-time speeds and four
constant-motion phases erased at subnormal scales. A24 regenerated all 66
inputs, matched their original reference strings, and passed them on the final
source. The [summary](development/2026-11-14-reference-refinement/reports/A16-r2-summary.json)
retains literal reproducers and every original/intermediate/final identity.

Qualified `src/RotaryMotion.cpp` SHA-256 is
`a3f986892078254f6dfae936bbbf1b5e1c4967882d06c13b3b28649f2273cfa1`.
The final reports observed HEAD `e4968b2` with additional uncommitted numerical work;
their input hashes identify the qualified source, not HEAD alone. The original
[2026-11-13 author checks](development/2026-11-13-rotary/10-motion.md) remain
historical evidence. Reproduction commands, the implemented R3 boundary and the
next R4 task are in [ROTARY_PROPAGATION.md](ROTARY_PROPAGATION.md).

These results require the qualified floating-point behavior: preserve gradual
underflow and avoid fast-math/reassociation. CMake's warning flags do not prevent
externally supplied incompatible flags or a caller changing the floating-point
environment. Windows/MSVC and AppleClang need their own numerical runs;
same-executable partition identity does not require cross-platform output hashes.
R4 waveform rendering, R5 audible policy, R6 integration/device deadlines and
physical measurements remain separate. Nothing here connects the dry Engine or
resolves the separate scanner G5 gate.
