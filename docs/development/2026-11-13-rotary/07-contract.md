# Assignment 07: frozen rotary contract and common types

Worker `/root/w02_a07_contract`, wave 2, assignment 07. Owned files are
[the numerical contract](../../ROTARY_NUMERICAL_CONTRACT.md),
[RotaryTypes.h](../../../include/hammond/RotaryTypes.h) and this note. No runtime
implementation, existing core type, shared status, CMake file or previous
session record was edited by this worker. Publication belongs to the integrator.

The observed starting source was `96a37a977ef22b7adf38e1a841f57ffcf32519a7`,
tree `ab85e45d6776229c00fa394a540d72803daf8281`. The worktree also contains
concurrent authorized work; this note does not qualify that changing tree.
Read `AGENTS.md`, rotary scope, complete wave-1 notes 04/06 and the pertinent
atlas motion/history/interpolation pages, including 303-304 and 320-322.
Recomputed PDF SHA-256 remains
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.

## Decisions frozen before runtime grading

- Model `nominal-effective-mouth-rotary-v1`, numerical contract
  `rotary-numerics-v1`; separate `hammond::rotary` types and error vocabulary.
- Separate horn/drum normalized double inputs and two omnidirectional receivers;
  one trajectory per rotor; coherent signed sum and explicit fixed-reference
  `r_ref/r` gain. No electrical, cabinet, room or calibrated directional claim.
- SI profile fields, full-orbit clearance/distance checks, Mach bound 0.25,
  four supported rates, 4,096 frames/1,024 events per call, 16,384-frame history
  cap and one-day integer-frame clock epochs. All are engineering bounds.
- Continuous event-anchored exponential motion, stable small-increment formula,
  direction-dependent tau selected from target error, canonical Chorale/Tremolo
  only, stable duplicate events, explicit offset-N and zero-frame behavior.
- Constant-initial-speed negative-time geometry, zero negative-time waveform,
  signed integer/fraction sample positions and historical emission queries.
- Cubic Lagrange support and two frames of declared algorithmic latency;
  root residual <=1e-11 seconds and at most 48 evaluations. The illustrative
  split is at most 12 safeguarded Newton plus 36 bisection evaluations, leaving
  residual margin without an extra hidden midpoint evaluation.
- Whole-call rejection preserves object/history/diagnostics/output, without
  mandating expensive whole-history copying. Stopped rate changes preserve
  instantaneous motion/commands and explicitly reset silent acoustic history.
- Separate high-precision motion, independent root, same-cubic audio and
  spectral gates. The audio error metric is normalized by maximum path gain
  sum; actual output is never automatically normalized. A broad-band/alias-free
  production claim remains outside the cubic research acceptance.

Coordinated field names, limits, startup and command policies directly with
assignment 08's strict profile author and assignment 09's independent reference
author. The latter's physical-time CLI deliberately has no implicit two-frame
latency; renderer comparisons request observation frame `n-2`. An independent
native audio oracle may be checked against sparse high-precision queries;
Decimal evaluation is not required at every audio sample.

## Executed checks and scope

Compiled an stdin translation unit including both existing `Types.h` and new
`RotaryTypes.h` with GCC 14.2.0, C++20, `-Wall -Wextra -Wpedantic -Wconversion
-Wsign-conversion -Wshadow -Werror -Iinclude -fsyntax-only`. Static assertions
checked trivial-copyability of Profile/MotionState/PathResult, separate status
types, four paths and sufficient fixed history capacity. **Exit 0.** No binary,
runtime process, allocation probe or hardware test was executed.

Checked all numerical-contract relative links, trailing whitespace, source hash
and `git diff --check`. All passed. Independent arithmetic gives 12,806 frames
for worst-case delay/support versus the 16,384 cap, and approximately
`1.2126596023639042e-12 s` for the last midpoint residual bound after 36
bisection evaluations, below 1e-11 seconds. This is a bound calculation, not a
runtime solver result.

Retained artifact identities at acceptance preparation:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| Numerical contract | 16,456 | `4c060088f0718586a7c6810e5c055c652d8924db4474db770237193ab459bd63` |
| Common header | 8,414 | `b27ce4934188c24ebe557469fa5191dd7cdcd98a1c3fdbe274b0d7585e4578b4` |

Next: implement motion and geometry/delay primitives, then independently execute
the frozen R2-R4 gates with exact source/profile/reference identities. Keep
R5 production filtering, M5/M6 coupling, measured M7 and native integration
pending until their own evidence exists. No commit or push was performed by
this worker.
