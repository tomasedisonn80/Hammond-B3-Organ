# A04 - Full atlas rotary reading and R4 boundary constraints

## Assignment, source and complete coverage

- Actual worker: `/root/w01_a04_atlas_rotary`; session date: 2026-11-14.
- Owned deliverable: this note only. Starting inspected HEAD:
  `2e161dc3a60fc3442051799574feed37bffbfc5c`.
- Source: `Hammond_B3_Leslie_Research_Atlas_500pp.pdf`, unchanged evidence edition
  12 November 2026. SHA-256:
  `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
- Assigned extraction: `../atlas-text/part-4-251-334.txt`, 219,929 bytes,
  26,443 words and 4,961 lines. SHA-256:
  `e79ab1418059f285595478563950f2811a5bf81545bbfdee6b4d457f6b3965d2`.
- Read every word of PDF pp. 251-334, inclusive, in consecutive untruncated
  `sed -n` chunks: 1-500, 501-1000, 1001-1500, 1501-2000, 2001-2500,
  2501-3000, 3001-3500, 3501-4000, 4001-4500 and 4501-4961.
  This covers 84 pages, including chapter 040's final two pages, complete
  chapters 041-053, and chapter 054's first four pages; no page was sampled out.
- Read `AGENTS.md`, the current session README/checkpoint/actual manifest,
  complete `docs/PLAN.md` and `docs/research/ATLAS_REVIEW.md`, the full numerical
  contract, and the final R4 section of `docs/ROTARY_PROPAGATION.md`.
- Numerical-contract SHA-256:
  `4c060088f0718586a7c6810e5c055c652d8924db4474db770237193ab459bd63`.
- Propagation-document SHA-256:
  `29539c8395901fe0057c52fa28aceac0729ebc854874697e49665379b272d261`.

## Selected actual PDF image inspections

Used the PDF skill and Poppler to render and visually inspect pp. 272, 302 and
326 at 110 dpi. Reproduction: `pdftoppm -f P -l P -r 110 -png -singlefile
Hammond_B3_Leslie_Research_Atlas_500pp.pdf /tmp/atlas-pP` for each listed page.
Temporary previews were outside Git under the session scratch `tmp/pdfs/A04/`.

- **p. 272:** the electrical graph visibly places L2 and the treble driver in
  parallel between A and H, with C16A between H and B. H is a floating return;
  the caption explicitly distinguishes electrical voltage polarity from pressure.
- **p. 302:** path-length and pitch plots share one computed geometry. Their
  0.18 m radius, 1.4 m microphone radius, 6 rev/s and 343 m/s are illustrative
  settings, not measured Leslie dimensions or factory defaults.
- **p. 326:** model A places angular weights after persistent FIRs; model B
  places weights before them. The two signal orders are visibly different.
  Static agreement cannot qualify moving behavior or justify swapping them.

## Page-specific findings and ownership decisions

- **pp. 251-252 - upstream dry boundary:** expression, loading and nonlinear
  errors require separate identification. Preserve the direct-organ render and
  dry numerical/hardware gates when downstream rotary work proceeds.
- **pp. 253-258 - 122 identity/control:** the baseline drawing identifies the
  1971 036616 non-reverb configuration. V1 controls the relay; V2 handles audio.
  Differential voltage is the full `va-vb`, not half that quantity. Relay commands
  select future drive; they never reset phase or impose instantaneous speed.
  Detector thresholds, relay delays and disturbance captures remain unacquired.
- **pp. 259-264 - variant boundary:** the vintage 147 has a single-ended input,
  different loading/control and feedback connections. A common transformer part
  or qualitative brightness description cannot justify one generic transfer.
  OPEN/8/16-ohm console loading belongs to the input interface, not the crossover.
- **pp. 265-270 - amplifier/load coupling:** transformer windings, feedback,
  shared bias, supply and crossover impedance form a connected electrical model.
  An acoustic IR supplies no electrical loading. Terminal volts/current and
  volts-per-digital-unit calibration belong upstream of this R4 research boundary.
- **pp. 271-276 - crossover:** documented nominal values are L2=3.2 mH,
  L3=5.2 mH, C16A=7.8 uF and C16B=12.5 uF, with separate dated assemblies.
  The 800 Hz label is not a universal measured crossing or a Linkwitz-Riley rule.
  Preserve loaded complex outputs and terminal signs; do not force unity summation.
  Driver impedance, parasitics and acoustic polarity remain specimen-dependent.
- **pp. 277-282 - horn:** one stationary compression driver feeds one rotating
  horn; its opposite arm is a counterbalance, not another driven audio source.
  Effective mouth position is a reduced model, not a photographed phase center.
  Internal transit, radiation, cabinet, propagation and microphone ownership must
  be declared per response. Preserve angular gain, phase and removed-delay data.
- **pp. 283-288 - drum:** the woofer stays mounted while the lower deflector
  turns. A rotating-point outlet is a reduced approximation with its own evidence;
  its effective radius is neither the cone orbit nor automatically the drum radius.
  Low acoustic frequency alone does not prove zero fractional Doppler. Frozen
  angle keeps the stationary response audible; zero path excursion removes only
  the separately owned geometric frequency modulation.
- **pp. 289-294 and 319-324 - mechanical history:** horn and drum have separate
  targets, phases and transitions. Motor-shaft RPM and acoustic rotor RPM differ.
  Choose tau by target-minus-current speed, preserve momentum on rapid reversals,
  anchor segments at command times and retain earlier segments for delayed queries.
  The documented 5-8 s bass adjustment is not an exponential tau or horn value.
  Slow/Fast is baseline; stop/brake requires a separate identified extension.
- **pp. 295-300 - cabinet:** exterior dimensions and appearance cannot establish
  internal paths or measured acoustics. Each reflection/filter has one owner.
  Both rotors stationary must produce a time-invariant acoustic response; room
  bypass must retain cabinet effects. Panel changes alter physical profile identity.
- **pp. 301-306 - R4 source basis:** input is at the effective radiation boundary;
  horn transit and filters are assigned elsewhere. Solve emission time first and
  query one trajectory at each receiver's distinct emission time. The circular
  distance has the negative cosine cross term. Linear mu=0 must select x[k]; the
  cited paper's reversed listing is not a valid implementation template. Cubic
  nodes are k-1 through k+2, requiring retained history and explicit support/latency.
- **pp. 307-312 - directivity:** signed complex pressure adds coherently. The
  reference-distance/r law is pressure gain, not intensity attenuation. Directivity
  weights use emission geometry; fixed cabinet walls cannot rotate with the horn.
  Angle normalization erases real modulation, and phase spikes at acoustic nulls
  cannot be interpreted as mechanical acceleration without independent angle data.
- **pp. 313-318 - microphones:** every receiver can receive both branches.
  Capsule position, azimuth, aim and rotor phase are separate quantities; microphone
  incidence uses the opposite of the source-to-receiver ray. Preserve interchannel
  delay, polarity and signed summation. Coincident receivers, complete receiver
  swaps and rigid scene transforms supply useful synthetic invariants.
- **pp. 325-330 - future filters:** frozen-angle kernels do not define a unique
  moving operator. Keep persistent filter histories and declare input/emission/
  observation time for weights. A longer IR cannot repair wrong emission timing.
- **pp. 331-334 - excluded environment/extensions:** direct organ, cabinet scene
  and studio stereo reverb are distinct boundaries. Room paths need their own
  emission geometry and cross-channel responses. Optional 122RV spring output
  radiates from a fixed speaker; it must not inherit horn/drum Doppler.

## Concrete constraints for the frozen R4 implementation

1. Preserve dry Engine, all 47 parameter meanings, `B3CONTROLS4` and readers 1-3.
   R4 consumes separate normalized double horn/drum radiation streams; it adds
   no crossover, driver, directivity, microphone, cabinet or room filter.
2. Retain one bounded history per rotor and one waveform history per input.
   The R3 4,097-segment immutable fixture capacity is not an indefinite event queue.
   Prepare resources outside processing; retain every segment needed by any path.
3. Write input n, observe n-2, solve four paths, read all four cubic supports,
   apply `reference_distance/r`, then sum signed Horn-then-Drum contributions.
   Negative audio is declared zero; future support is never invented. No extra
   pitch oscillator, panner, gain normalization or output clamp is authorized.
4. Honor capacity `ceil(Fs*rmax/c)+2+4` within 16,384 frames, full-orbit clearance,
   and the existing bounded R3 solve. Preserve distinct algorithmic/physical delay.
5. Preserve ordered ties, offset-N and zero-frame events, unchanged-command anchors,
   silence advancement and deterministic suspension. Every failure preserves
   histories/state/diagnostics/caller audio and consumes zero events, including
   mid-render failures after nonzero history. Inputs may alias; outputs may not.
6. Reset restores initial state/silence. Stopped rate replacement retains physical
   state/commands but starts a new epoch with silent waveform history and explicitly
   discarded tails. Flush `ceil(Fs*rmax/c)+2+2` zero-input frames while motion runs.
7. Qualify endpoints, all j/256 fractions, degree-0..3 polynomials, signed indices,
   all ring supports and rejection preservation. Retain the complete static delay
   grid and >=10 s independent same-cubic comparisons at all four rates. Require
   normalized error <=2e-5 and bit-identical audio/state for prescribed partitions.
8. R4 parity does not pass R5 alias/reconstruction policy, R6 runtime/integration,
   M5/M6 completion or physical M7. Published 600/122A experiments, atlas synthetic
   fixtures and photographs cannot supply missing target-122 captures or constants.

## Outcome and next owner

Completed the assigned fresh full reading and three actual visual inspections.
This is source review, not an executed renderer test, build or hardware campaign.
Only this note was written; no code, shared records, source PDF or commits changed.
Next: integrator freezes bounded R4 history/API and independent reference ownership,
then implements and grades the stated waveform/transaction contracts unchanged.
