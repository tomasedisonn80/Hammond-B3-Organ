# Final continuation runtime review

Reviewed by `/root/w10_a55_final_runtime_review` on 2026-11-13 UTC.
This review uses frozen source tree
`805900d2339eb3975019581de5f8469e72e7509f`. All 23 files under `include/` and
`src/` were independently checked byte-for-byte against published commit
`2046b9388f6aab1122e37646b2f20199b5c6079f`. The 72 frozen core, header, test and
CMake files also match the stated staged tree. No live headers were used with
an older library.

## Verdict and evidence scope

**No actionable runtime defect or inconsistent completion claim was found in the
reviewed boundaries.** The contact, shared percussion, partial-key and rate-change
implementations agree with their declared nominal contracts. All six selected
existing acceptance executables passed, with exit zero and empty stderr. Their
aggregate observed wall time was 1.613 seconds; this is a local verification
observation, not a processing deadline or benchmark.

The inspected build is GCC 14.2.0 Release with C++20, `-O3`, and the project's
strict warnings including `-Werror`. Its CMake source directory points to the
frozen archive above; sanitizers are off for this local check. Root built the
archive. This worker ran the individual test executables to avoid modifying
CTest logs while the integrator ran its separate full gate.

The [assignment 55 record](../development/2026-11-13-continuation/55-final-runtime-review.md)
retains the actual commands, timings and source checks. This review does not
claim a new full-suite, hosted-platform, sanitizer, allocator or physical-capture
result. The preceding [runtime boundary review](RUNTIME_BOUNDARY_REVIEW.md) remains
an earlier, independently scoped record.

## Boundaries checked directly

| Boundary | Observed implementation and acceptance |
| --- | --- |
| Physical detector | Engine ORs upper-manual physical contact index 8, the ninth contact and 1-foot/eighth-harmonic branch. Drawbar position does not erase this contact. Lower activity does not enter the detector. |
| Harmonic audio | Eligible upper-B percussion sums the current second/third-harmonic contacts at indices 3/4 from the existing shared source frame, independently of their sustained drawbar gains. Detector connectivity does not become an extra audio gate. |
| Mask and compensation | Eligibility requires percussion enabled, upper route enabled and bank B. Only the eligible upper sustained index-8 branch is masked; its stored value and physical connection survive. Normal compensation affects eligible upper sustain, not lower sustain or percussion. |
| Same-frame ordering | Complete preflight precedes dispatch. Equal-offset events retain their supplied order; one current-state sample follows the cluster. The source bank emits its current sample and advances once; readiness and contact motion advance once afterward, including disconnected output. |
| Zero elapsed time | Zero-frame calls apply commands but do not advance source phase, contact travel, readiness or clock. Off/on at one offset creates no recharge interval. Panic opens the selected manual immediately while preserving readiness until elapsed samples recover it. |
| Partial targets | Finite targets in [0,1] are accepted in nominal travel mode; ideal mode accepts only endpoints. Identical targets preserve the current segment. Target changes retain current position and hysteresis; a positive NoteOn commands full press after a positive partial hold. |
| Rejection | Engine validates the entire event list before mutation, including late invalid events after valid ones. Failed process, prepare and control restore preserve state and future behavior. Checked invalid diagnostics preserve their destination. |
| Changed rate | Engine validates its owned source profile and all three copied module candidates before installation. Sources retain phase, contacts retain current position/target/bits, and percussion retains readiness. Moving segments rebase at the current position using their owned durations. |
| Same rate and admission | Unprepared status precedes invalid-rate status. Supported rates are exactly 44.1, 48 and 96 kHz, subject to source increment bounds. Same-rate requests return before coefficient work or trajectory rebasing. Rejected rates preserve later output. |
| Clock and ownership | Reconfiguration advances no frames and keeps the independent frame counter; elapsed seconds across rates require a caller-retained segment schedule. Musical controls remain separate from dynamic histories, and all access requires stopped or same-processing-thread use. |

These findings follow direct inspection of
[Engine.cpp](../../src/Engine.cpp), [ContactBank.cpp](../../src/ContactBank.cpp),
[Percussion.cpp](../../src/Percussion.cpp),
[TonewheelBank.cpp](../../src/TonewheelBank.cpp), and their public contracts:
[Engine.h](../../include/hammond/Engine.h),
[ContactBank.h](../../include/hammond/ContactBank.h),
[Percussion.h](../../include/hammond/Percussion.h),
[console dynamics](../CONSOLE_DYNAMICS.md) and
[sample-rate lifecycle](../SAMPLE_RATE_LIFECYCLE.md).

### Cases that must remain intentional

A nominal key held at position 0.5 from below has its second-harmonic contact
closed while its ninth contact remains open. The percussion audio therefore
uses recovered readiness and can continue at that partial hold. A later full
press continues the trajectory and begins decay only when the detector closes.
The [partial-key acceptance](../../tests/test_partial_key.cpp) checks that
sequence at all three rates against current-phase audio formulas. Adding a
Boolean detector gate to suppress this audio would change the declared model.
The physical transition still requires hardware evidence.

Contact history also outlives the held-target Boolean. A target-zero key can
retain closed contacts while rising. The detector continues its decay branch
until the physical ninth contact opens; ordinary NoteOff must not be treated as
instantaneous detector release. Cancel or upper-A selection makes the routed
detector ineligible while retaining physical state. Recovery during those
intervals is an explicit nominal routing policy, not a verified universal switch
transient. The [console tests](../../tests/test_console_engine.cpp) distinguish
these cases and compare readiness with independent exponential formulas.

Moving contacts can cross thresholds during a block that has no input events.
Engine marks the mix coefficients dirty on such crossings and rebuilds before
the following sample. The conservative bound is one complete rebuild per rendered
frame. The handoff and [allocation audit](../REALTIME.md) state this scope; no
native callback deadline follows from fixed storage or the present test timings.

## Observed focused verification

| Executable | Actual retained result from this run |
| --- | --- |
| [test_console_engine](../../tests/test_console_engine.cpp) | 1,179 source/audio oracles; 318 closed-form readiness checks; 42 partition/disconnected comparisons; 16 failure-preservation cases. |
| [test_partial_key](../../tests/test_partial_key.cpp) | 234 exact state pairs; 51,513 exact audio samples; 768 isolated current-phase samples; 51 rejected calls. Maximum observed audio error: 9.29094e-10. |
| [test_engine_rate](../../tests/test_engine_rate.cpp) | 36 rate-pair and 36 detector-edge scenarios; 81 rejected changes; 6,144 same-rate calls; 32,603 exact audio frames. Maximum phase error: 5.5595068479408205e-14 turns; readiness error: 5.5177433802566789e-14. |
| [test_contact_rate](../../tests/test_contact_rate.cpp) | 71 tracked migrations; 115 rejected migrations; 12,288 same-rate no-ops; 456,298 position and 4,116,402 contact comparisons; 14,028 exact future frames; 18,630 threshold samples. Maximum position error: 1.59459034518305564632e-16. |
| [test_percussion_rate](../../tests/test_percussion_rate.cpp) | 234 tracked migrations; 250 rejected changes; 20,736 same-rate calls; 1,305 analytic comparisons; 7,488 instantaneous gain checks; 152,544 exact future frames. Maximum readiness error: 6.3501070721172503e-14. |
| [test_source_rate](../../tests/test_source_rate.cpp) | 42 transitions; 80 rejections; 15,561 phase and 15,561 sample oracles; 61,772 exact future frames. Maximum phase error: 2.459699111057e-13 turns; sample error: 1.2362302208389e-12. |

The reviewed tests use both exact paired continuation and independent formulas.
The Engine rate gate checks all 91 sources and 122 keys, including accepted
transitions with pending control changes, detector crossings after a rate change,
caller-profile mutation, and rejection at both Nyquist and the minimum supported
source-increment boundary. Thus a matching status code alone is not the rollback
oracle. No new test was added merely to mirror unchanged implementation.

## Atlas alignment and remaining work

This review reread the complete extracted text of atlas pages **115, 117, 120,
127, 128, 135, 394 and 447**. They support the chosen separation of contact
histories, shared source phase, detector routing, percussion state, core lifecycle
and later host integration. Page 135 specifically distinguishes isolated RC time
constants from audible decay lengths and a complete loaded valve circuit.
The current `shared-readiness-v1` dimensionless state and gain law remain labeled
as a surrogate; the selected contact timings/thresholds remain proposed.

The [atlas](../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf),
[plan](../PLAN.md), [status](../STATUS.md) and
[current handoff](../CONTINUATION_HANDOFF.md) correctly leave full M3 open.
This review does not validate contact bounce, fractional edges, switching
bandwidth, measured finger trajectories, physical preset latches, runtime pedal
audio, loaded expression, complete percussion/AO-28 transfer, scanner, Leslie,
native host/device operation, concurrent publication or hard deadlines.

**Next action:** retain this scoped review, complete the remaining final reviews,
and qualify/publish the combined candidate through the integrator. The next
product change is the [prepared pedal-routing/reference kernel](../M3_NEXT_GATE.md):
first admit all 200 map positions into typed fixed storage and then consume the
existing shared source frame. Preserve all current event/control identities and
these contact/percussion timelines. Physical model claims require their separate
acquisition and comparison gates.
