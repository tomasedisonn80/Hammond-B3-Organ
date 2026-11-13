# Assignment 10: allocation-free rotary motion

Worker `/root/w02_a10_motion`, assignment 10/60, wave 2, owns only
`include/hammond/RotaryMotion.h`, `src/RotaryMotion.cpp`,
`docs/ROTARY_MOTION.md` and this note. No common types, CMake files, maintained
tests, shared status files, commits or remote references were changed by this
assignment. Publication and shared handoff updates belong to the integrator.

Read the standing instructions, rotary scope, complete frozen numerical
contract and common types, relevant project status/plan/handoff material,
and atlas motion/startup guidance on pp. 320 and 324. The inherited source
review covers the entire 500-page atlas; this assignment did not independently
reread all pages or acquire physical measurements. Source review began from
the session at `96a37a9`. The observed checkout during compilation and checks
was `6b4b6bd3a881dd13e6e3b7f846993f0fbbb977f9`, tree
`a2fd40769d47444bc2fc5b5e8ad16e3703388041`, with the new wave-2 files still
uncommitted. The source hashes below identify the actual checked additions.

## Implemented result

The module validates kinematics, evaluates exact first-order model segments
in binary64 with a stable small-argument angle polynomial and direct
long-decay speed residual, and retains phase plus checked signed turns.
`MotionEvaluation` exposes signed angle increments separately so tiny motion
is observable without claiming it remains representable atop every existing
phase. Integer frame differences and a separate fractional tail preserve
late-epoch sample resolution.

`RotaryMotion` retains one event anchor, current observation, command,
original reset seed and current epoch seed. Repeated commands do not
reanchor; changed targets preserve phase/speed and select tau from signed
speed error. Negative time uses constant current-epoch seed speed. A stopped
rate change preserves physical state and command in a new epoch; reset
restores the original prepared seed at the current rate. All rejected calls
preserve caller output and owner. The public API and these semantics were
coordinated with the integrator and assignment 09's independent reference.

The [module guide](../../ROTARY_MOTION.md) explains the public API, equations,
units, sample-position convention, status meanings and external-history
responsibilities. The owner permits read-only future predictions; earlier
positive segments require the renderer's external history. Reconfiguring to
the same accepted sample rate also explicitly starts a new epoch. There is
no Engine, renderer, audio, UI or plugin integration here.

## Actual author checks

All commands ran from the repository root with `/usr/bin/g++`, Debian
14.2.0-19, and Python 3.12.14. Build products and focused author harnesses were
kept outside the repo at `/workspace/scratch/c9f9d8cb3889/a10-build`.

Strict translation-unit compilation passed with exit zero:

```sh
/usr/bin/g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic \
  -Wconversion -Wsign-conversion -Wshadow -Werror -I include \
  -c src/RotaryMotion.cpp \
  -o /workspace/scratch/c9f9d8cb3889/a10-build/RotaryMotion.o
```

The temporary `smoke.cpp` and `spot_probe.cpp` harnesses were each compiled
with those same flags, `-I include`, and `src/RotaryMotion.cpp`. The smoke
binary exited zero with:

```text
author smoke passed; tiny angle=4.22222e-27; late fractional phase delta=1.97886e-11
```

| Observed check | Result |
| --- | --- |
| Tiny acceleration and long decay | A start from rest retains the positive angle at `h=1e-14` s; decay toward zero at `h/tau=100` retains positive speed. |
| Turn representation and overflow | Extreme signed turn seeds remain intact at zero duration; positive/negative overflowing additions reject without changing output. Tiny signed negative increment remains observable. |
| Event anchors and target logic | Intermediate observations and direct observation produce equal owners; unchanged commands retain the same segment; a Chorale command below the slow target selects upward tau. |
| Rejection rollback | Backward commands, invalid command enumeration and invalid rate preserve the entire owner. Invalid endpoint fraction preserves destination. |
| Lifecycle and prehistory | Rate change preserves state and makes it the epoch seed; reset restores original seed/command at the new rate. Negative floor-index fractional query matches constant-speed history. |
| Long-epoch fractional timing | At 192 kHz, one frame before the one-day endpoint, fractions `1e-7` and `2e-7` remain distinguishable; observed phase difference `1.97886e-11` rad agrees with the expected difference within `1e-13` rad. |
| Value semantics | Compile-time `is_trivially_copyable_v<RotaryMotion>` assertion passed. |

The independent reference was imported with
`sys.path.insert(0, 'tools'); import rotary_reference as r`. A subprocess
fed the native probe tuples `(w0, wt, tau, h, direction)`. In a private
80-digit Decimal comparison context, 38 cases passed the frozen speed and
signed-angle budgets. The cases use tau `0.001, 0.45, 60`, ratios `h/tau`
`1e-30, 1e-12, 0.124999999, 0.125, 1, 100`, and speed/direction tuples
`(0,200,+1)` and `(200,0,-1)`. Two additional cases use the 86,400-second
endpoint. Float parameters were converted by the oracle as exact binary64
values. Results were:

- Maximum absolute speed error: `1.942702157135419e-14` rad/s.
- Maximum absolute signed-angle error: `1.0000000041633363e-9` rad, within
  the magnitude-dependent frozen budget for the long interval.
- Maximum relative tiny start-from-rest angle error: `1.1977899622350148e-16`,
  below `2e-12`; no tested positive decay tail at ratio 100 disappeared.
- No rejected case or numerical assertion failure in that matrix.

The exploratory scripts are temporary author probes, not the independently
maintained acceptance suite. Their result file was
`a10-build/spot-results.json` outside the repository. The first combined tool
output was truncated; the same matrix was rerun with a short explicit result
and exit zero. No threshold was changed to obtain a pass. CMake integration,
full R2 acceptance, allocation instrumentation and sanitizer qualification
are pending the subsequent independent assignments.

## Checked source identities

| Input | SHA-256 |
| --- | --- |
| `include/hammond/RotaryMotion.h` | `7bc81331f84b7ce490bf9047114336e633f3da91a39bbfd2a13e3fd406f61d36` |
| `src/RotaryMotion.cpp` | `9c8c98dc66a66088d39b43a52d025289d4dd241ebba583bd4200aba3b539ac4d` |
| `include/hammond/RotaryTypes.h` | `b27ce4934188c24ebe557469fa5191dd7cdcd98a1c3fdbe274b0d7585e4578b4` |
| `docs/ROTARY_NUMERICAL_CONTRACT.md` | `4c060088f0718586a7c6810e5c055c652d8924db4474db770237193ab459bd63` |
| `tools/rotary_reference.py` | `603f28969b6d59399c9295eaf7c1dbbefe31bf244e9c08aee38815c84beee352` |
| Temporary `smoke.cpp` | `ec27e17aee4b316088980ad80f83cc3079ce99a0a5719a069aa8bca44b58cc0f` |
| Temporary `spot_probe.cpp` | `6159946bb2c15952626f97963d6f48eca28e2021085e76bff69d11f117301a6f` |

The unchanged atlas SHA-256 is
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.

## Next action

Build an independent maintained R2 test driver against this API and the
80-digit reference. Cover the frozen grid, 1,000 random semigroup cases,
both directions, phase wraps, endpoint/fraction arithmetic, signed overflow,
invalid inputs, equal-frame command order, block partition invariance,
negative startup, stopped rate epochs and original-seed reset. Retain worst
error locations and the tested coherent source tree; author probes alone do
not close R2. A later history owner must select the correct older motion
segment for retarded emission queries and preflight whole transactions before
publishing output. Geometry and physical fidelity remain independent gates.
