# Independent streaming renderer implementation review

Reviewer: actual A16, `/root/w03_a16_renderer_review`, 14 November 2026.
Basis: frozen [renderer contract](../ROTARY_RENDERER_CONTRACT.md), unchanged
[numerical contract](../ROTARY_NUMERICAL_CONTRACT.md), public headers, and the
actual linked implementation identified in the [session note](../development/2026-11-14-waveform-continuation/notes/A16-renderer-review.md).

## Result and scope

**No production defect was found in this bounded review.** Six independent
renderer suites pass with strict GCC 14.2 C++20 compilation, both with the normal
stack and a 1 MiB stack. The reviewer changed only
`tests/test_rotary_renderer.cpp`, this review, and the assigned session note.
No production source, frozen API, shared build, manifest or status file was
changed by A16.

This accepts the inspected renderer structure and the executed behavior below.
It does not complete R4: the ten-second moving same-cubic comparisons at all
rates, complete partition matrix, symmetry/rate-pair matrix, actual late
failure rollback and calibrated allocation tests retain their assigned owners.
R5 reconstruction policy, R6 deadlines/integration and physical M7 remain
separate. All profiles in this test are synthetic SI fixtures defined in the
test source; no measured cabinet value is inferred.

## Contract review

| Area | Inspection and executed evidence | Assessment |
| --- | --- | --- |
| Preparation | Small motion/path candidates admit spec, both full rotor projections and all four full-orbit paths before allocating the heap storage. Replacement occurs after history initialization. Tests reject both rotor seeds, either microphone, hidden full-orbit collision, overlong path and excess original-seed Mach; maximum path/rate admits H=12,806 and flush=12,804. | Matches sections 2–3. |
| Getter ownership | Profile, spec, state, bounds and diagnostics return values. Tests check unprepared defaults and independently mutate returned profile/state values. | No borrowed storage escape. |
| Admission precedence | Actual calls combine conflicting errors to cover NotPrepared, BlockTooLarge, TooManyEvents, InvalidBuffer, TimelineOverflow, InvalidEvent, then invalid input samples. The tests include exact/partial forbidden output overlaps and accepted complete/partial input overlap with adjacent output ranges. | Matches section 4. |
| Ordered events | Every per-frame boundary advances both staged owners before applying events in supplied order. The final boundary handles offset-N; zero-frame calls publish only commands/owners. Tests compare end/zero/next-zero ordering with the equivalent joined stream, preserve unchanged anchors, and consume 5,120 alternating zero-frame events beyond R3's fixture limit. | No event coalescing, lost consumption or lifetime event cap observed. |
| Audio operator | Inputs are written before observing n−2. Paths run Horn/Left, Horn/Right, Drum/Left, Drum/Right; each reads its own waveform and receives its own pressure gain. The sums retain Horn-then-Drum order. Independent stationary Cartesian geometry/product-form cubic tests include separate inputs, signed impulses, cancellation, frozen nonzero radii and overshoot above 900 output units. | No hidden clamp, normalization, squared-distance gain or extra modulation found. |
| Undo journal | Before either waveform or motion write, the code saves both doubles and both original segments and increments the live record count. Reverse replay restores every overwrite and all four clocks; owners/diagnostics remain staged and caller outputs remain untouched. The bounded arrays are in prepared heap storage. | Source structure matches section 5; actual late failure acceptance belongs to A20. |
| Publication | All event reads, final owner advances, interpolation/solve checks and finite output checks precede committed owner/diagnostic assignment and output copying. No fallible operation follows publication. | Whole-call serialized visibility is preserved by structure. |
| Diagnostics | Only successful sample paths update staged last-path data and epoch maxima. Zero calls leave diagnostics unchanged. Tests compare diagnostics bit by bit across boundary partitions and rejected calls, and check observation n−2 plus path delay/gain/sign at rest. | Matches sections 3–4. |
| Reset | Existing owners are reset in small local copies before any history clear. Under admitted storage invariants, both waveform resets and frame-zero motion-history preparations cannot fail. Tests compare resumed output with a fresh renderer and restore original seeds at the current rate after two rate epochs. | Matches section 6; the ignored history statuses rely on the stated admitted invariants. |
| Rate replacement | Copies of current owners retain original reset seeds; new storage starts clocks at zero with current state/turns/commands, silent audio and default diagnostics. Original geometry/envelope is reused and H/flush are recalculated. Both changed-rate and equal-rate epochs are exercised. | Current state and later original reset behavior both pass. |
| Tail and epoch | Explicit zero input consumes ordinary frames and continues motion; the declared flush leaves subsequent output silent. A test-only friend advances an already filled stationary silent ring and all four clocks to the exact one-day boundary. | Timeline and zero-frame behavior pass; the endpoint fixture is accelerated, not a continuous full-day render. |

The null/range-overflow guards were inspected, without fabricating nonempty
spans whose backing C++ object ranges are invalid. Event storage is never
retained and all events are read before output publication; no stricter alias
condition is imposed in the implementation. These are source-review findings,
not additional executed malformed-storage or event/audio-storage experiments.

The reset invariant is a maintenance constraint: if future changes introduce
new possible rejection conditions in the history clear/preparation steps, those
conditions must be admitted before the first clear. There is no reachable
rejection there for the currently admitted renderer state, so this review does
not request a production change.

## Independent analytical method and results

The test oracle uses long-double Cartesian source positions and a direct
Euclidean norm. It obtains the stationary emission coordinate from
`n−2−Fs*distance/c`, evaluates the four-node Lagrange polynomial using generic
products over the other three nodes, then applies `reference_distance/distance`
and the ordered signed sum. It does not call `PreparedStreamingPath`, either
history interpolation routine, the production cubic kernel or a native motion
helper for this expected waveform. There is no fitted alignment, rescaling or
frequency adjustment.

Nine analytical fixtures cover 57,568 output samples: horn alone, drum alone
and separate mixed deterministic signals for integer and half-frame travel
times; a frozen nonzero-radius scene; a high-gain overshoot scene; and signed
separate impulses. The independent impulse locations explicitly include both
the physical travel time and two algorithmic frames. Every 4,096-frame static
call exceeds twice its active history capacity, so ordinary accepted calls
exercise repeated physical ring overwrites.

| Measurement | Observed value |
| --- | ---: |
| Analytical output samples | 57,568 |
| Maximum absolute error | 1.4698916354916047e-09 |
| RMS absolute error | 2.0352041431145979e-10 |
| Worst coordinate | Fixture 8, left channel 0, frame 8 |
| Fixture at worst coordinate | Reference distance 10 m; coincident stationary sources; receivers at x=0.02734375 m; c=375 m/s; four samples −1,+1,+1,−1; all remaining input zero |
| Per-sample analytical allowance | 5e-9 times the channel's sum of static path gains |
| Rejected process calls | 31 |
| Rejected lifecycle calls | 36 |
| Accepted event consumption | 5,149 |

The 31 process rejections are preflight failures. Snapshots retain both complete
waveform histories and both complete motion histories on the heap. Comparisons
check every sample/segment floating field by bit representation, all ring
metadata, owner equality, copied physical state/diagnostics and watched output
bytes. Accepted continuation also matches an identically seeded control bit
for bit after the nonzero-history rejection series. These results do not stand
in for late partial-frame or multi-wrap rejection experiments.

Rate replacement at 96 kHz preserves nonzero turns and current speed, then its
first accepted sample's negative-time emission phases agree with independent
constant-current-speed extrapolation. A further equal-rate replacement clears
the epoch again. Reset then reproduces the original 96 kHz seeded renderer's
output exactly. The test does not claim all sixteen rate pairs; that matrix is
assigned separately.

## Reproduction and remaining gates

The [session note](../development/2026-11-14-waveform-continuation/notes/A16-renderer-review.md)
contains the compiler command, exact hashes and both observed run results.
The focused executable has no generated-profile or external-data dependency;
the existing test-support macros are defined for compilation but its profile
loader is not called. The normal and 1 MiB-stack runs produce identical JSON.

Next owners should integrate this standalone test into the shared CMake/CTest
configuration, retain the late-failure seams, execute the moving reference and
complete partition/symmetry/rate matrices, and calibrate both allocation and
deallocation detection. The integrator owns source-coherent build/hosted runs
and publication. No sanitizer or hosted outcome is claimed by A16.
