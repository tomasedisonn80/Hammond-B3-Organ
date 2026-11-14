# Native rotary propagation continuation contract

**API accepted by the integrator after A12 review, 14 November 2026; implementation and runtime acceptance pending.**
This bounded M7 slice first independently qualifies native R2, then implements
R3 immutable-history geometry/roots under [rotary-numerics-v1](ROTARY_NUMERICAL_CONTRACT.md).
Its basis is the [A04 review](development/2026-11-14-reference-refinement/notes/A04-atlas-acoustics.md),
especially atlas pp. 289–294 and 301–324. It preserves the model, units and
numerical budgets. It does not connect Engine or the current audio callback,
change the 47 parameters/state4, or claim R4–R6 or physical qualification.

## 1. Public surface and ownership

Add `RotaryPropagation.h/.cpp`; reuse `Status`, `Vec3`, `MotionProfile`,
`MotionState`, `MotionSegment`, `MicrophoneProfile`, `PathBounds`, `PathResult`
and `SamplePosition`. Proposed declarations in `hammond::rotary`:

```cpp
inline constexpr std::size_t kMaxMotionSegments = 4097;

class MotionHistoryView {
public:
    Status prepare(const MotionProfile&, const MotionState& epoch_initial,
                   double sample_rate, std::span<const MotionSegment>,
                   std::uint64_t through_frame) noexcept;
    bool prepared() const noexcept;
    double sample_rate() const noexcept;
    MotionProfile profile() const noexcept;
    MotionState epoch_initial_state() const noexcept;
    std::uint64_t through_frame() const noexcept;
    Status state_at(SamplePosition, MotionState&) const noexcept;
    // Private: borrowed span, copied metadata, prepared flag.
};

Status evaluate_circular_source(const Vec3& origin_m, double radius_m,
                               const MotionState&, std::int8_t direction,
                               Vec3& position_m, Vec3& velocity_m_s) noexcept;

class PreparedRetardedPath {
public:
    Status prepare(const MotionHistoryView&, const Vec3& origin_m,
                   double radius_m, const MicrophoneProfile&,
                   double sound_speed_m_s, double reference_distance_m) noexcept;
    bool prepared() const noexcept;
    PathBounds bounds() const noexcept;
    Status solve(SamplePosition observation, PathResult&,
                 SamplePosition& emission) const noexcept;
    // Private: view by value, copied admitted geometry and bounds.
};
```

Default objects are unprepared. Add `[[nodiscard]]` to public return values.
Preparation is transactional and allocation-free, outside processing. The path
copies the small view, so the original view object need not survive. The backing
segment objects **must outlive every view/path copy and remain immutable**;
moving/reallocating their container invalidates the views. No ownership transfer,
concurrent mutation, automatic growth or live publication is supplied.

The 4,097-segment cap covers the oracle's initial anchor plus 4,096 offline
events. It is a separate finite-fixture capacity, not the 16,384-frame waveform
history cap or an arbitrary-duration event-stream claim. Preparation scans once;
queries use at most 13 binary-search comparisons and bounded motion evaluation.
There is no allocation, destruction, locking, logging, I/O or user callback in
queries. One history per rotor serves both microphones; four prepared paths
provide a two-rotor/two-receiver scene.

## 2. Historical trajectory admission

Require a supported rate, 1–4,097 segments, valid profile/seed and
`0 <= through_frame <= 86400*Fs`. Segment zero is anchored at zero with the
exact epoch seed. Later anchors strictly increase and do not exceed
`through_frame`. Every segment has the profile direction, a slow/fast target,
and the tau selected from target minus its initial speed. Its initial state
must equal the preceding segment's native evaluation at that anchor, including
turns; this API accepts canonical histories built with the existing native
helpers, not rounded serialized checkpoints. Evaluate the final covered endpoint
during preparation to detect turn overflow. Reject discontinuous trajectories.

The caller records `RotaryMotion::segment()` after commands, replaces equal-frame
anchors with the last effective segment, and omits identical segment snapshots.
This view does not replay events or own the current command clock. Exact anchor
queries choose the new segment; the old segment owns the preceding interval.

Negative positions use `evaluate_motion_prehistory_at` with the epoch seed and
constant seed speed, never a later accelerating segment. Nonnegative positions
select the greatest anchor not exceeding the position and call
`evaluate_motion_segment_at`. Coverage ends inclusively at
`{through_frame,0}`; later positions within the epoch return `InsufficientHistory`.
Check epoch bounds first: positions below `{-86400*Fs,0}` or above
`{86400*Fs,0}` return `TimelineOverflow`. Reset/rate replacement requires newly prepared
views/paths and a newly declared seed; no acoustic history is implied.

## 3. Geometry, time and solver

Use the frozen coordinate/sign equations. The pure geometry helper validates
finite coordinates in `[-10,10] m`, radius in `[0,1] m`, motion state and direction
exactly `-1` or `+1`, and stages both output vectors;
identical vector destinations reject with `InvalidBuffer`.

Path preparation admits all coordinate, radius, sound-speed and reference-distance
limits and the **entire orbit**:
`rmin=hypot(R-radius,h) >= 0.02 m`,
`rmax=hypot(R+radius,h) <= 20 m`, and
`beta=radius*max(epoch_seed_speed,slow,fast)/c <= 0.25`.
Using the actual history seed also covers stopped rate epochs. Initial-angle-only
checks cannot admit a path. `bounds()` reports these three quantities; its
default unprepared value is zero and is not an admitted bound.

Solve local seconds `G(d)=d-distance(t-d)/c`. Widen only the analytical distance
bracket by `32*ulp(max(1,rmax))` metres before dividing by `c`, matching the
reference's roundoff allowance. Check endpoint signs; never clamp geometry or
residual. Pure bisection is sufficient. Count **all** evaluations, including both
endpoints, in `PathResult::iterations <= 48`; reuse the selected evaluation's
cached state/geometry/result without an uncounted final evaluation. Success
requires finite `abs(residual_s) <= 1e-11`, positive delay and emission strictly
before observation. Check the derivative's admitted range with the reference's
`2e-15` roundoff allowance. Exhaustion/stagnation without success rejects.
Use `1e-14 s` as the internal early-exit target to leave room for the frequency
ratio budget during rapid ramps; the frozen acceptance limits remain unchanged.

Subtract only the bounded local `d*Fs` from the split observation: separate its
integer/fractional parts, subtract integers with checked arithmetic, and normalize
fractional borrow/carry. Never form `double(observation.frame)+fraction`, absolute
seconds subtraction, or an unwrapped double angle. Every evaluated emission must
be covered; this includes the bracket endpoints. Observations themselves must
lie within the prepared history's query range. The solver applies **no two-frame
latency**; that belongs to R4's caller.

Publish `PathResult` and emission together. Distance is metres, delay/residual
seconds, phase radians, radial speed metres/second positive toward the receiver;
frequency ratio is `1/(1-radial_speed/c)` and pressure gain is
`reference_distance/distance`. Both are diagnostics, with no waveform processing.

## 4. Rejection contract and acceptance

Every failure preserves the complete prepared object and all caller destinations
exactly; queries also leave history and diagnostics untouched. Use existing
statuses: `NotPrepared`; `InvalidSpec` for rate/count/fraction; `InvalidProfile`
for invalid geometry, kinematics or discontinuity; `InvalidEvent` for anchor
ordering; `TimelineOverflow` for epoch/turn overflow; `InsufficientHistory` for
uncovered positive time; `NumericalFailure` for arithmetic/bracket/residual
failure. Preserve more specific existing motion-helper failures.

Independent acceptance must retain executable/source/profile/oracle hashes,
commands, deterministic seeds, maximum/RMS errors, worst coordinates and failures:

1. **R2 first:** execute the complete frozen tau/sign/time grid, tiny positive
   acceleration/decay, full-day/wrap/reversal probes, 1,000 seeded semigroup cases,
   all rates, event partition identity and rejection/lifecycle checks. Apply all
   frozen absolute and near-zero relative budgets; Python-only tests do not pass R2.
2. **History/API:** query before/on/after anchors and zero; test equal-frame
   replacement, unchanged commands, maximum capacity, all invalid fields,
   coverage endpoints, copied-view lifetime while storage remains valid, and
   failed reprepare preserving earlier results. Do not deliberately dereference
   expired storage. Check split fractions near the full-day endpoint independently.
3. **R3:** use every frozen radius/sign/pose/clearance/sound-speed/Mach fixture.
   Compare geometry at identical supplied motion states (`2e-12 m` distance),
   then roots (`2e-11 s` delay, `1e-11 s` residual, `2e-10` frequency ratio).
   Retain the separate motion phase/root contribution bound. Include command-
   crossing roots, startup, distinct receiver emission times, and converging
   finite-difference derivative stencils. Independently grade the 96-bisection,
   `1e-14 s` oracle and preserve its separate iteration-count convention.

An allocation probe and sanitizers may qualify these named primitive calls.
They do not close R6 integration/device timing. R4 interpolation, transactional
audio, tails and streaming history remain the next separate design after R3.
