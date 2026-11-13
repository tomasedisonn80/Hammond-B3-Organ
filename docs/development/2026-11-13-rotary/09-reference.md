# Assignment 09: independent motion and retarded-path reference

Worker `/root/w02_a09_reference`, wave 2, owns only
`tools/rotary_reference.py`, `docs/ROTARY_REFERENCE.md` and this note. No
production C++, shared status, other worker files, commits or remote refs were
changed by this assignment. Source review began at `96a37a9`; the integrator
advanced the checkout to `6b4b6bd3a881dd13e6e3b7f846993f0fbbb977f9` during work.

Read `AGENTS.md`, rotary scope, the complete wave-1 reviews 04/06, current
plan/status/next steps and actual atlas pages **289-294, 301-306, 319-324** in
complete six-page batches. The initial combined repository read truncated;
the affected source-note section was reread separately. This assignment did
not newly inspect PDF figures or acquire external source publications.

## Implemented boundary

The new oracle uses private 80-digit Decimal analytical motion with immutable
event anchors and independent binary64 Cartesian geometry plus bisection.
It retains complete per-rotor command histories, stable final-command tie
semantics, no reanchor on unchanged commands, uniform initial-speed negative
prehistory and optional initial turn count for epoch comparisons. The solver
bisects local delay, retains actual residual/causality/derivative diagnostics,
and defaults to 96 iterations and a 1e-14-second residual budget.

Coordination with assignments 07/08 fixed canonical `chorale`/`tremolo`
commands, SI mappings, the admitted geometry/speed envelope and a single-read
profile/hash adapter. Pure motion/path calculations import no production
implementation. The CLI admits strict bounded per-rotor frame events and
queries arbitrary Decimal times or exact frame/rate times. It explicitly
applies no hidden renderer latency. `microphone_incidence` uses the incoming
bearing `-u`; current receiver response remains unity.

The [reference guide](../../ROTARY_REFERENCE.md) provides API, equations,
commands, units, identities, rejection behavior, numerical limitations and
the next independent acceptance gate. No waveform interpolator or audio
renderer is claimed by this module.

## Actual checks

Executed Python 3.12.14 heredoc checks and CLI subprocesses from the repository
root. Results below concern this mathematical implementation, not the new C++
runtime or physical hardware. All listed assertions passed.

| Check | Retained result |
| --- | --- |
| Motion versus separately evaluated 200-digit closed form | 440 cases: five initial/target combinations, four taus, eleven `h/tau` values from `1e-30` to `1000`, both signs. Maximum relative speed error `1.8666878999322658e-80`; angle error `4.523506784774866e-80`; declared check limit `1e-73`. |
| Semigroup composition | 1,000 deterministic cases, seed `91703`, split intervals each in `[0,30]` seconds, taus in `[0.001,60]`, speeds in `[0,200]`, both signs. Maximum angle discrepancy `2e-76` rad and speed discrepancy `1e-77` rad/s. |
| Event and Decimal-context behavior | Four input commands collapse to two effective anchors; repeated command does not reanchor; initial-speed negative history agrees exactly. Result survives caller precision 1, ROUND_UP and an Inexact trap unchanged. |
| Static propagation and incidence | Fixed one-metre path agrees with `1/343` seconds within `1e-16`; ratio exactly one. Residual `-2.0816681711721685e-17` s. Incoming-axis sign returns +1 for a directly facing mic. |
| Moving path and differential relation | 303 roots at a requested `1e-16` residual tolerance; maximum observed residual `9.8879238130678e-17` s. Maximum centered finite-difference ratio discrepancy `7.329032936098656e-10` at a 10-microsecond step, below the declared `2e-9` check limit. |
| Derivative stencil convergence | Eight observation times, root tolerance `1e-17`: halving steps 100, 50, 25 and 12.5 microseconds yields maximum errors `5.629703903053951e-8`, `1.4074407417297152e-8`, `3.5186888958094187e-9`, `8.798275441534997e-10`. Each refinement improved by more than threefold. |
| Historical emission across command | Reception at `0.1001` s after a command at `0.1` s queries emission `0.096640108586880246...` s; the full result exactly matches the pre-command trajectory. |
| CLI and strict inputs | Three fixture times produce twelve causal paths; default-budget maximum residual `9.732666061967876e-15` s. A retained event-file query passed; five boolean/command/order/duplicate-key corruptions rejected with exit 2. |
| Epoch and endpoint | Signed initial turn count `-317` retains phase; the 86,400-second constant 200 rad/s negative-direction endpoint is exactly `-17,280,000` rad. |

The motion comparison taus were `0.001, 0.125, 1, 60`; ratios were
`1e-30,1e-24,1e-18,1e-12,1e-6,0.1,0.5,1,10,100,1000`. Initial/target pairs
were `0/40,4/40,40/4,40/0,200/200` rad/s. These are synthetic mathematical
choices. This sanity matrix supplements the frozen contract; it does not
replace its broader independently maintained native acceptance matrix.

Reproduce the CLI smoke check with:

```sh
python3 tools/rotary_reference.py \
  --profile data/rotary/nominal-research-v1.json \
  --time 0 --time 0.125 --time 1 --paths
```

The exploratory mathematical assertions were executed as heredocs rather than
added as a self-grading test suite inside the oracle. The next independent
assignment retains the regression tests and grades its own expected results.
A patch initially failed because a documentation context line differed; no
partial file change occurred. The corrected patch applied and its signed-turn
and maximum-duration probes passed. No numerical check was silently relaxed.

## Input and implementation identities

- Reference Python: 31,165 bytes; SHA-256
  `603f28969b6d59399c9295eaf7c1dbbefe31bf244e9c08aee38815c84beee352`.
- Admitted fixture: 19,988 bytes; SHA-256
  `c0473cb20604726d989d7c280700109f647f7b227edb71c61d275ed9bfd67443`.
- Frozen contract read for these checks: SHA-256
  `4c060088f0718586a7c6810e5c055c652d8924db4474db770237193ab459bd63`.
- Preserved atlas identity:
  `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.

## Next action and limits

Independently test reference admission, event/history semantics, small-argument
motion, geometry signs, root bracketing and failures; then compare native
motion/path results under the frozen R2/R3 contract. A root residual pass is
not interpolation, spectral, allocation or device evidence. The subsequent
same-cubic waveform reference must apply the runtime's explicit two-sample
latency and zero negative input samples. Measured rotor trajectories,
directivity, cabinet response, M5/M6 boundaries and native integration remain
open. Publication and shared handoff updates belong to the integrator.
