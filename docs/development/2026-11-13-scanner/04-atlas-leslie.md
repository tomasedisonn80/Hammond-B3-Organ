# Assignment 04: fresh atlas review, Leslie and acoustic dependencies

## Identity, ownership and completed coverage

- Assignment: **04/60**, logical wave **1/10**, agent
  `/root/w01_a04_atlas_leslie`.
- Owned output: this note only. No production code, shared status, historical
  ledger, parameters or source asset was changed; no commit or push was made.
- Inspected checkout: commit `6dc0702d5473912268e8af8f852b9b9984198ef3`,
  Git tree `a4f1d4b300de236436e22b748b1d4c46ed501ceb`. The new scanner-session
  directory was untracked during this review; the commit does not identify it.
- Source: the unchanged [500-page atlas](../../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf),
  evidence edition 12 November 2026; 21,248,265 bytes; SHA-256
  `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
- **Fresh complete text reading: inclusive PDF pages 253-336, all 84 pages.**
  The page numbers below refer to the PDF, not the separate manuals it cites.
- Actual rendered-page visual inspections: **272, 283 and 326**, at 110 dpi.
  These selected inspections do not establish that every figure or cited
  external document was independently verified.

## Complete chapter coverage

| Chapter | Inclusive pages | Freshly reviewed subject and implementation consequence |
| --- | --- | --- |
| 041 | 253-258 | Vintage 122 input and command interface; retain full differential volts, loading, separate command detection and continuous mechanical state. |
| 042 | 259-264 | 147 identity, single-ended input, console loading, winding feedback and calibration; shared component types do not justify shared complete topology. |
| 043 | 265-270 | Coupled 6550 power stage, transformer, feedback, supply and electrical load; establish operating point and independent reference before optimization. |
| 044 | 271-276 | Source-linked four-element divider, floating treble return, driver impedance and electrical/acoustic ownership. |
| 045 | 277-282 | Stationary compression driver, one fed rotating horn, dummy counterbalance and phase-preserving angular response. |
| 046 | 283-288 | Stationary woofer and rotating deflector; separate radiation, propagation and cabinet effects. |
| 047 | 289-294 | Independent horn/drum mechanisms, speed ratios, proposed torque and reduced motion models, acquisition and optional braking. |
| 048 | 295-300 | Cabinet identity, fixed panels/louvres, air versus structural response, calibrated geometry and held-out acoustic evidence. |
| 049 | 301-306 | Emission-time propagation, moving-source frequency ratio, fractional delay, bounded solver/history and explicit latency. |
| 050 | 307-312 | Complex directivity, coherent signed paths, angular FIR bases, shared trajectories, sidebands and unreliable phase near nulls. |
| 051 | 313-318 | Independent microphone scene, path incidence, correlated stereo, mix matrices and absolute timing/calibration. |
| 052 | 319-324 | Persistent physical rotor states, event-anchored motion, host timing, historical queries and rate/suspension policies. |
| 053 | 325-330 | Two-time FIR operators, interpolation, persistent tails, warm profile changes and convolution scheduling. |
| 054 | 331-336 | Room ownership, reflected paths, complete MIMO kernels and a distinct optional 122RV spring/fixed-speaker branch. |

## Plan and electrical boundaries that scanner work must preserve

The broader sequence after the scanner is the connected AO-28 dry-organ model,
then an identified Leslie input/power/transformer/load system, independent horn
and drum motion, radiation and microphone/room rendering, physical calibration
and product qualification. This reading reinforces the existing M4-M9 dependency
order; it does not close the outstanding physical M3 tasks.

1. **Keep a declared voltage boundary and calibration status.** The 122 input
   uses full differential voltage `vd = va - vb`, with common mode
   `vc = (va + vb)/2`; reconstructing the legs uses `vc +/- vd/2` (p. 255).
   The power-stage input/output must retain actual port orientation and volts
   per digital unit (p. 265). Therefore a nominal scanner's normalized signal
   cannot silently become measured volts or authentic overdrive calibration.
   Preserve the scale and model identity so AO-28 drive/recovery can replace
   that approximation explicitly.
2. **Return loading to the stage that owns it.** The 122 input is proposed as a
   two-port admittance boundary, not just a one-way gain (p. 255). The power
   transformer sees the connected crossover and driver impedances (pp. 266,
   272-274). If a future integrated solve already applies a load, downstream
   code must not apply its attenuation a second time (p. 261). Ideal source
   and unloaded receiver assumptions in the scanner must remain named limits.
3. **Keep circuit identity separate from shared model code.** The 1971 122
   baseline identifies amplifier assembly 036616 at 60 Hz, with optional
   reverb excluded (p. 253). The 147 uses a different input and winding-feedback
   connection; even the shared 1979 transformer stock identifier does not
   establish the same closed-loop transfer (pp. 259-265). Modern 122H servo
   data cannot populate missing vintage parameters (pp. 253, 289).
4. **Retain signed electrical outputs.** The atlas's divider has `L2` and the
   treble load in parallel between A and H, `C16A` between H and B, `L3`
   between A and W, and `C16B` plus the bass load between W and B. The treble
   output is `VA - VH`, not a node voltage against B. The actual p. 272
   diagram confirms the floating H return. This is a downstream analogue of
   the scanner's need for explicit ground/common-return output conventions.
5. **Do not make the current scanner own later effects.** Its line response,
   rotor weighting and state should not absorb AO-28 recovery, Leslie input
   loading, speaker resonances or room response merely to make an early render
   sound more finished. Pages 274, 278, 296, 305, 325 and 331 require unique
   ownership for each fitted or simulated contribution.

## Time, phase and model ownership

The scanner rotor, Leslie horn and Leslie drum are different mechanisms. A
reusable clock/history design is appropriate; sharing one oscillator or phase
between them is not. Pages 280, 286, 292 and 319-324 require one mechanical
owner per Leslie rotor, while every microphone observes that owner's trajectory.
Notes, GUI refreshes, editor closure and unchanged commands must not restart
motion. Commands change future evolution while retaining current phase and speed.
The nominal scanner should establish the same discipline for its own state.

For future acoustic paths, a shared trajectory does not mean every microphone
uses the same current angle. Each path can observe a different emission time
from the same history (pp. 301-305, 322). The retarded constraint is
`t = e + distance(e)/c`; the source velocity and geometry are evaluated at `e`.
The atlas identifies two specific paper-listing hazards: the circular-distance
cosine sign (p. 302) and reversed endpoint weights in a linear interpolator
(p. 303). These are source-audit findings, not independently obtained
author-issued corrections in this assignment.

Numerical acceptance must exercise the evolving system. The p. 326 diagram
distinguishes weighting FIR outputs at observation time from weighting excitation
before convolution: identical static responses can produce different moving
tails. Preserve nonzero state across selections/rates and compare rotating
sidebands with a converged higher-rate reference. Smooth weights alone do not
establish low aliasing (pp. 286, 303, 310, 330).

Geometry remains separately qualified. The horn has one fed side (pp. 277-278);
the p. 283 image distinguishes the fixed woofer from its rotating deflector.
Complete kernels must declare included driver, propagation, cabinet, microphone
and room contributions, preserving signed pressure and common timing
(pp. 305, 313-318, 325, 331-333). The optional 122RV branch radiates through
a fixed speaker and must not receive rotor Doppler (p. 334).

## Verification boundaries and next useful work

This assignment completes source reading and selected visual inspection only.
It executes no scanner, amplifier, acoustic or host acceptance test. The atlas's
reported numerical fixtures on pp. 306, 312, 318, 324, 330 and 336 remain
claims about the atlas's separate synthetic work. Their named original scripts
and datasets are not recovered companion assets, and their results cannot be
recounted as executions of this repository.

Next: scanner graph admission, independent AC/transient oracle and bounded
physical-state runtime, preserving the dry path and stable controls. Later
M6/M7 needs a reviewed connected graph and loaded linear oracle, then driver/load
boundaries and continuous motion before acoustic fitting.

Unresolved physical inputs include specimen/revision applicability, source and
receiver impedance, transformer ratios/parasitics, fitted device curves, driver
impedance and acoustic polarity, motor/rotor motion, geometry, phase-preserving
angular responses and licensed calibrated captures. Horn data from a Leslie 600
or published 122A experiments cannot be relabeled vintage 122 measurements
(pp. 279, 287, 307). Training takes, validation takes and untouched final
evaluation must remain distinct (pp. 269, 281, 300, 317, 335-336).

## Executed commands and observations

Working directory for repository commands:
`/workspace/scratch/1742da7072be/Hammond-B3-Organ`.

```sh
cat AGENTS.md
pdfinfo Hammond_B3_Leslie_Research_Atlas_500pp.pdf
sha256sum Hammond_B3_Leslie_Research_Atlas_500pp.pdf
pdftotext -f 253 -l 253 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 254 -l 266 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 267 -l 273 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 274 -l 287 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 288 -l 301 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 302 -l 315 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 316 -l 329 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 330 -l 336 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
git rev-parse HEAD
git rev-parse 'HEAD^{tree}'
git status --short
```

The initial larger pp. 253-273 combined output was truncated by the tool budget;
the smaller complete readings listed above resolved that display limitation.
No page in this assigned range was skipped. A Python subprocess loop also ran
`pdftoppm -f PAGE -l PAGE -r 110 -singlefile -png` for PAGE 272, 283 and 326,
writing temporary images outside the repository; each image was displayed and
inspected. No source PDF was edited. Current README/status/next-step context and
the final pedal-session log were inspected; older claims remain historical.

Final local checks: `git diff --check` passed, source SHA-256 remained unchanged,
and the relative PDF link in this note resolves. No production build or test
was warranted for this documentation-only review; integration and publication
belong to the parent.
