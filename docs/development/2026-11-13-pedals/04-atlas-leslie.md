# 04 - Atlas Leslie electronics and rotary acoustics review

Owner: /root/w01_a04_atlas_leslie

Session: 2026-11-13 pedal development, wave 1, assignment 04 of 60.

## Scope, source and actual coverage

Read **every assigned PDF page 253-336 inclusive**, covering chapters 041-054
(84 pages). This is a new reading for this session, not a recount of an earlier
worker. The source is the repository's unchanged
[research atlas](../../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf), SHA-256
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
Page locators below are one-based PDF pages, matching its printed page numbers.

The local HEAD observed during this assignment was
`b4fc61ccfcc59724f14fb0cee947ed7bb7142075`. The integrator was concurrently editing
shared session/status files. This worker preserved those edits and wrote only
this note. The standing `AGENTS.md`, current plan/next-step context and relevant
current `Engine.cpp` source call/mixing locations were inspected.

Actual reading used the root's complete `pdftotext -layout` extraction, split on
form-feed page separators. The first two tool outputs truncated part of pages
257 and 270; both pages were immediately reread in full. Subsequent chunks were
small enough to return without truncation. The completed ranges were 253-264,
265-276, 277-284, 285-292, 293-300, 301-308, 309-316, 317-324, 325-332 and
333-336. The separate full rereads recovered all initially omitted text.

Rendered and visually inspected **pages 272, 274, 302, 322 and 334** with Poppler
at a 1400-pixel maximum dimension. This is selected visual inspection, not a claim
that every photograph, cited external manual or underlying measurement was
independently verified.

Commands actually used included:

```sh
cat AGENTS.md
git rev-parse HEAD
git status --short
sha256sum Hammond_B3_Leslie_Research_Atlas_500pp.pdf
rg -n 'process_frame|mixed|expression|coefficients_' src/Engine.cpp
rg -n 'M6|M7|M8|M9|dry organ|cabinet' docs/PLAN.md docs/NEXT_STEPS.md docs/research/ERRATA.md
```

The reading helper selected explicit inclusive page ranges from
`Path('/workspace/scratch/f364bc93d920/atlas-review/atlas.txt').read_text().split('\f')`
and printed each page with its numerical marker. Visual rendering used
`pdftoppm -f PAGE -singlefile -scale-to 1400 -png` against the unchanged PDF;
temporary images remained outside the repository under the session review area.
No native software test, hardware capture, external-manual fetch, commit or push
was performed by this assignment.

## Complete chapter coverage and downstream roadmap

| Chapter / pages | Main implementation requirement | Evidence or dependency still needed |
| --- | --- | --- |
| 041 / 253-258 | Separate vintage 122 differential audio, electrical command detection and mechanical rotation. Preserve full differential volts, per-leg coordinates and input loading. | Selected 1971 assembly identity, specimen applicability, source impedance, detector threshold/polarity, timing and dual-leg calibrated captures. |
| 042 / 259-264 | Give 147 a separate connected topology, single-ended input/return, console-load choice, signed transformer connections and adapter boundary. Share component code without conflating complete amplifiers. | Reconcile vintage and 1979 drawings, winding/feedback map, valve curves, taper and input/output captures. A generic brightness switch is insufficient. |
| 043 / 265-270 | Solve output valves, transformer, supply/bias, feedback and crossover/driver load as a coupled network. Establish DC and linear behavior before nonlinear optimization. | Transformer ratios/parasitics, specimen devices, supply impedance, load fits, convergence and held-out electrical captures. |
| 044 / 271-276 | Preserve the four documented reactive values, floating treble branch, signed multiport outputs and combined amplifier load. Begin with an independently checked resistive-load fixture. | Source-reviewed connectivity; measured losses, installed driver impedances, acoustic polarity and assembly applicability. |
| 045 / 277-282 | One stationary compression driver feeds the rotating horn; the opposite side is a counterbalance, not a second driven audio source. Retain angular complex response and the one rotor trajectory. | Target driver/diffuser identities, geometry, phase-preserving angular captures and synchronized moving validation. |
| 046 / 283-288 | Keep the woofer fixed and rotate its deflector. Model angular transmission, filtering and any propagation separately; zero speed leaves a stationary bass response. | Installed bass-only complex responses, deflector/cloth/panel identity, angle references, level dependence and held-out poses. |
| 047 / 289-294 | Separate horn/drum drives, direction, pulley ratios and motion states. Start with a named speed surrogate; use coupled torque/slip states only when observations identify them. | Independent command/shaft/rotor timing, both ramp directions, interrupted ramps, mechanical profile and accessory identity. |
| 048 / 295-300 | Separate appearance, surveyed geometry, cabinet air/structural response and room. Introduce additions only to explain retained residuals. | Specimen passport, panels, actual internal dimensions, calibrated kernel boundaries and held-out acoustic scenes. |
| 049 / 301-306 | Solve causal emission time from shared trajectory history, with bounded residual/error and explicit interpolation support/latency. Assign propagation once. | Admitted geometry/speed range, an independently executed numerical oracle, interpolation/alias qualification and target angle/audio captures. |
| 050 / 307-312 | Use signed complex angular responses with absolute gain and timing. Advance persistent basis states; evaluate radiation and delay from the same geometry/history. | Target radiation profiles, held-out angular/pose responses, null reliability criteria and dynamic bandwidth checks. |
| 051 / 313-318 | Define microphone positions, aim, calibration and output matrix separately. Sum physical paths at each receiver before output mixing; retain shared rotor/source identity. | Actual receiver calibration, synchronous channels, poses, polarity, clock alignment, held-out stereo/mono comparisons. |
| 052 / 319-324 | Own one persistent horn and one drum state on the audio timeline, with event-anchored segments and bounded historical queries. | Real adapter timing, capacity/overflow tests, rate-epoch/suspension policy, trajectory capture and physical residuals. |
| 053 / 325-330 | Declare the two-time convolution convention. Preserve basis/filter history, full tails, timing and calibrated gain through angle changes and profile replacement. | Target IR dataset, reversible preprocessing, numerical/alias/deadline qualification and held-out moving recordings. |
| 054 / 331-336 | Keep direct organ, cabinet/microphone scene, external room/studio effect and optional 122RV spring branch distinct. Use complete MIMO paths where declared. | Room/source/receiver boundaries, crossfeed kernels, spring/electronics/fixed-speaker captures and a named physical reference. |

These chapters substantiate the existing [M6/M7 roadmap](../../PLAN.md), with
M8 capture/calibration and M9 runtime/host qualification as separate gates.
Source-backed documentary and numerical work can begin before all captures exist;
physical matching cannot.

## Constraints on the current pedal and dry-engine work

1. **Keep the dry organ as a meaningful boundary.** Pages 257, 263, 265 and 269
   call for electrical observations before interpreting microphone results.
   A pedal mixture cannot be justified by adjusting a downstream bass cabinet,
   microphone or room response until the output seems plausible. The present
   normalized dry model may remain useful, but its normalized amplitude is not
   calibrated AO-28 or Leslie volts. A later port needs an explicit volts-per-unit
   scale and loading assumption.

2. **Reuse the existing coherent source field.** Current `Engine.cpp` calls
   `source_bank_.process_frame(source_samples)` once per model frame, then uses
   that frame for sustained and percussion contributions. The new pedal path
   should consume that same frame and preserve its separate division identity
   until the declared dry summation. No later stereo, cabinet or microphone
   choice should add an unrelated source oscillator or restart musical phase.
   Pages 315 and 319-322 reinforce common electrical sources and separate,
   persistent downstream mechanical state.

3. **Keep expression, source scale and later overdrive causally distinct.**
   The current expression multiplication is a named normalized surrogate. Page
   265 requires expression/preamp drive/power-stage overdrive to remain related
   through declared port scales. Do not turn a later Leslie drive control into
   an undocumented replacement for expression, or silently fit lost pedal gain
   with a cabinet loudness adjustment.

4. **Preserve independent histories and ordinary state boundaries.** Page 322
   separates musical presets from complete offline checkpoints that contain
   trajectory history and timing. Adding pedal controls must not cause normal
   snapshot load to restore/reseed shared tone phases or invent future rotor
   history. Rate changes need physical-unit preservation and explicit new clock
   epochs for any future delay histories.

5. **Nominal pedal work need not wait for Leslie measurements.** Nothing in
   these chapters supplies missing pedal reactor/load coefficients. A clearly
   identified dimensionless routing/voicing fixture is an upstream software
   contract, and its useful tests can be completed independently. It must not
   inherit a physical cabinet/bass-fidelity claim from the published examples.

## Electrical and visual traps worth retaining

### Vintage identities and circuit boundaries

The atlas selects the 1971 117 V 60 Hz 122 reference assembly `036616`, without
optional reverb (pp. 253-258). It reports five main valve positions, four main
rectifiers, V1 as rotor control and V2 as the audio driver. The 147 is distinct in
input, control interface, cathode/transformer feedback and topology (pp. 259-270).
Modern 122H servo/preamp data must not fill vintage unknowns. These statements
are **atlas documentary accounts**, not a new independent factory-source audit.

For the p. 272 divider, the rendered schematic visibly agrees with its node table:

| Port/connection | Correct boundary |
| --- | --- |
| Divider input | `Vin = VA - VB` |
| A-H | L2 and treble driver impedance in parallel |
| H-B | C16A |
| A-W | L3 |
| W-B | C16B and woofer impedance in parallel |
| Treble output | `VT = VA - VH`, a floating return |
| Bass output | `VWnode - VB` |

The atlas reports L2 3.2 mH, L3 5.2 mH, C16A 7.8 microfarads and C16B
12.5 microfarads, with dated divider identities `052803` and `113860`
(pp. 271-273). The nominal "800 Hz, 16 ohms" label is not an exact acoustic
cutoff or a constant impedance. The illustrative 16-ohm resistive-load numbers
are algebra fixtures, and the referenced companion executable is not supplied
by this reading. The driver is `020305`; `020313` is a spacer (p. 295).

### Conceptual arrows are not connectivity

Visual inspection confirms that the compact diagrams can look like serial chains:

- **Page 274** draws successive treble/bass boxes, but its text and p. 272
  require parallel electrical branches and their combined load at the amplifier.
- **Page 322** places horn and drum histories in one row; they are separate
  state owners under the same audio clock, not horn feeding drum.
- **Page 334** places divider/rotating paths before spring boxes; the text
  specifies a branch from the main amplifier output to the optional spring/return
  amplifier and stationary speaker. The spring does not run after rotary
  acoustic rendering and its fixed speaker receives no rotor Doppler.

This independently supports the existing diagram caution in
[atlas errata E03](../../research/ERRATA.md).

## Acoustic and timing contracts for later implementation

- **One physical trajectory does not mean one observation angle.** Each
  microphone/reflection path solves its own emission time from the same rotor
  history. With fixed receiver position and subsonic motion, p. 302 uses
  `t = e + ||m - q(e)||/c` and derivative
  `F'(e) = 1 - u dot v(e)/c`. Its rendered circular geometry contains the negative
  cosine term. The atlas's reported external-paper sign discrepancy remains a
  source audit, not an author-issued erratum verified in this assignment.
- **Interpolation has observable endpoint semantics.** Page 303 gives linear
  weights `(1-mu, mu)` at samples `k, k+1` and flags reversed weights in the cited
  listing. A production implementation needs integer/ring endpoints, admitted
  latency/support and high-rate alias comparisons, not just a smooth plot.
- **No added arbitrary tremolo is required to create AM.** Radiation, distance,
  leakage, fixed-cabinet interference and microphone incidence create the
  specified signed pressure result. Independent left/right LFOs would describe
  different rotors. Magnitude-first summation destroys interference (pp. 308-316).
- **Do not infer rotation speed from phase spikes near nulls.** The published
  122A measurement and enclosure simulation are different figures/evidence
  classes (pp. 311, 329). The 122A and Leslie 600 datasets do not calibrate the
  selected vintage 122. Mechanical fitting uses independently synchronized
  angle traces (pp. 287, 293, 311, 323).
- **Convolution weight placement changes the model.** Output-time angular
  weights and input-time angular weights give the same frozen response but
  different moving tails (pp. 325-330). Do not commute them for FFT reuse.
  Preserve continuous fixed-filter states; warm replacement banks from retained
  input or a declared pre-roll, and use a defined transition.
- **Effects have single ownership.** A measured complete kernel may already
  contain driver, horn/drum, cabinet, propagation, microphone and room. Preserve
  that boundary or record reversible removal and reapply each removed factor
  once. A room bypass must leave cabinet reflections intact (pp. 278, 297-298,
  305, 325, 331-336).
- **Control and clock policy must be explicit.** Slow/Fast is the baseline.
  Stop/coast/brake requires its own extension/accessory identity; the reported
  5-8-second bass transition criterion is neither a universal tau nor horn timing
  (pp. 289-294, 319-324). Silence/editor closure cannot restart motion; rate
  changes preserve angle/physical speed and handle histories deliberately.

## Completion, useful next work and limits

This assignment closes its **complete page-reading and selected visual-review
scope**. It supplies no newly executed DSP acceptance, actual instrument
measurements, complete netlist, recoverable companion scripts or third-party
asset permission. The atlas's historical numerical results on pp. 306, 312,
318, 324, 330 and 336 remain source claims with narrow synthetic scope; none was
rerun or promoted to current repository evidence here.

The current pedal slice should therefore proceed with a separate named nominal
model, shared source frame, stable existing event/control meanings, explicit
normalized units and an independently checked dry reference. Retain the
upstream/downstream boundary in diagnostics and the handoff. Later dependency
work should qualify connected port/topology models before fitting cabinet/room
effects; acquire identified, calibrated records before any physical-fidelity
claim. The integrator owns shared status, next steps, execution gates and
publication for this session.
