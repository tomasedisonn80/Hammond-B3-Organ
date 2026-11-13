# Assignment 04: complete Leslie chapter reading and standalone boundaries

## Assignment identity and observed inputs

- Agent: `/root/w01_a04_atlas_leslie`; new next-phases session, wave 1,
  assignment 04. This does not recount an earlier session's reader.
- Owned output: this note only. No production code, shared status file,
  assignment manifest, commit or remote branch was changed by this worker.
- Inspected checkout: `ba0d9c9c75bd7a39152470f9f7ddb82287cb01b1`, tree
  `51fd7b24d2f373a693ced8dbde0fba762a3cc434`.
- Source: [preserved research atlas](../../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf),
  evidence edition 12 November 2026, 500 pages; SHA-256
  `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
- **Complete assigned text coverage: PDF pages 253-336 inclusive, 84 pages,
  chapters 041-054.** Text was read sequentially in bounded chunks, including
  an additional read of the first output's truncated section. This is not a
  claim that every underlying external source or every figure was independently
  verified.
- Actual PDF images rendered and visually inspected: **272, 283, 326**.
  Page 272 confirms the floating treble return and the explicit A/H/W/B graph;
  page 283 shows the fixed driver above the separate lower deflector;
  page 326 shows the different input-time and output-time weighting operators.
- Read the repository's standing instructions, current README, status, next
  steps, plan, scanner handoff and latest development-log entries. Checked
  `src/ParameterBridge.cpp` and `include/hammond/ControlStateIO.h` against the
  proposed standalone scope. The contemporaneous scanner work remains owned by
  the separate session.

## Complete chapter coverage and plan

The book's Leslie work is a sequence of electrical, mechanical and acoustic
contracts. It does not provide one calibrated effect that can be enabled by
adding an attractive cabinet panel. The following covers every assigned chapter.

| Chapter and PDF pages | Required implementation and evidence boundary |
| --- | --- |
| 041, 253-258: 122 input/control | Identify the 1971 036616/117 V/60 Hz baseline separately from other assemblies and optional reverb. Preserve full differential voltage, individual input legs, source loading, the audio driver and the control detector as separate responsibilities. Commands select drive conditions without resetting motion. |
| 042, 259-264: 147 differences | Retain a distinct single-ended source/load boundary, connected phase driver, bias and transformer feedback. Keep dated source revisions separate. A generic brightness switch does not represent the electrical differences. |
| 043, 265-270: power stage | Build a connected driver/6550/transformer/load/supply network; establish DC and linear references before nonlinear reduction. Bound the coupled solve and test convergence, aliasing and physical port scales. Transformer/device/supply measurements are absent. |
| 044, 271-276: divider/load | Preserve the source-transcribed floating treble return, four reactive values, dated divider identity and simultaneous driver loading. Compare complex transfer and input admittance to an independent ideal-resistor reference before admitting measured loads. |
| 045, 277-282: horn | One stationary compression driver feeds one driven rotating horn; the opposite horn is the counterbalance. A moving-mouth surrogate and angular filters may be implemented provisionally. Geometry, driver/diffuser identity and calibrated angle responses are required for a measured claim. |
| 046, 283-288: lower rotor | The woofer basket stays fixed while the deflector rotates. Retain direction-dependent filtering, possible changing delay and cabinet/room interference as explicitly owned contributions. A scalar tremolo or orbiting woofer is insufficient. |
| 047, 289-294: motors/belts | Horn and drum have independent motion profiles and states. Begin with an identified speed surrogate, retain angle and momentum through commands, then increase mechanical model order only when measurements identify it. Slow/Fast is the baseline; stopping accessories are separate. |
| 048, 295-300: cabinet | Separate visible appearance from measured geometry. Identify panels, driver/rotor replacements and internal boundaries. Build one fixed-angle response first, then signed horn/drum summation, angular variation and receiver movement. Add reflected paths or structural modes only for an identified residual. |
| 049, 301-306: propagation | Solve emission time for each path from the same rotor trajectory. Preserve distance, derivative sign, interpolation support, history and bounded residual work. The text identifies source-sign/interpolation issues that must be resolved mathematically instead of copied. |
| 050, 307-312: directivity | Retain complex angle-dependent response and gain; a scalar volume curve is only an explicit approximation. Persistent FIR bases and periodic weights are a proposed realization. Higher-rate comparisons must separate alias error from acoustic uncertainty. |
| 051, 313-318: microphones | A scene owns capsule positions, axes, calibration, relative timing and output mixing independently of organ/cabinet identity. Both channels read the same physical trajectories at their own emission times. Mono fold-down and a single receiver are distinct scenes. |
| 052, 319-324: rotor state | Event-anchored horn/drum histories are independent of note activity, host block boundaries and UI refresh. Historical queries may cross an earlier speed command. Rate changes and suspension require declared policies; ordinary presets are not full DSP checkpoints. |
| 053, 325-330: varying convolution | Declare whether angular weights act at input time or observation time. Persistent filter history, warm replacement, phase-preserving data and bounded transitions are required. Equal fixed-angle responses do not imply equal rotating behavior. |
| 054, 331-336: room/RV | Assign each direct/cabinet/microphone/room contribution once. Keep full MIMO cross-channel kernels and absolute timing when that boundary requires them. Optional 122RV spring electronics radiate through a separate fixed speaker; they are not the baseline 122 or a generic studio room effect. |

The explicitly printed synthetic checks on pp. 306, 312, 318, 324, 330 and 336
are source-reported mathematical fixtures. Their missing companion files are
not recovered by this reading, and those printed results are not tests executed
against this repository. The reviewed chapters repeatedly state that no new
target hardware captures were acquired.

## Concrete decision for the standalone application

The current [plan](../../PLAN.md) permits an M9 adapter after the existing
M1/M2 engineering contracts. The new standalone can therefore be useful now
against the existing dry Engine while the scanner, AO-28 and Leslie work
continues. It must expose the behavior that the actual core implements.

The inspected registry contains 36 retained manual-bank drawbars, expression,
two A/B selectors, four percussion settings and two pedal mixture drawbars:
45 controls in total. No registered Leslie, microphone, room or scanner control
exists at this inspected revision. Cancel and note/panic actions have separate
event/ownership semantics and must not be invented as new permanent parameter
IDs merely to draw buttons.

| Standalone surface | Truthful behavior at the inspected baseline |
| --- | --- |
| Upper/lower manuals and pedals | Send bounded musical input to the existing ownership adapters. Show the source's held-note state separately from a saved registration. |
| Four manual A/B banks | Edit the actual retained bank and preserve selection independently; drawbar positions are discrete 0-8. |
| Pedal drawbars | Use the implemented mixture names and positions. Do not rename their nominal responses as measured footage curves. |
| Expression/percussion | Use the existing model and labels. Expression remains a normalized linear-gain surrogate; percussion retains the current upper-B eligibility contract. |
| Registration save/load | Save the existing control snapshot. Do not claim restoration of held notes, source phase, contact history, readiness, audio clock or future rotor histories. |
| Output and meters | Identify the signal as nominal dry organ output. Matching left/right samples are dual-mono transport; two meters do not establish a Leslie microphone scene. |
| Cabinet artwork/section | It may communicate design intent or future scope. Mark unavailable cabinet DSP visibly, and prevent interaction from suggesting an audible change. |
| 122/147, rotor speed, microphone pose, room/RV controls | Omit or clearly disable them until actual admitted modules and their control/state contracts exist. An educational illustration must be identified as such. |
| Audio-device controls | Show actual obtained device/rate/buffer state and explicit failures. These are application settings, separate from historical instrument controls. |

A short visible description such as **Nominal dry organ** gives a user the
relevant sound-model boundary. An unavailable cabinet section should state
that the Leslie path is not implemented. Detailed evidence and research
identities belong in the service/about/help surface, with source links and
unavailable states; ordinary playing should not require reading an engineering
log.

No Leslie animation is justified as live DSP telemetry while the renderer does
not own Leslie states. Later, requested speed and observed simulated speed
must be distinct. The UI can interpolate display snapshots but cannot advance
the audio clock or integrate a competing rotor trajectory (pp. 258, 292, 294,
319, 322). Closing or redrawing the window must not reset notes or source phase.

## Future audio contracts the adapter must leave intact

1. **Identity and units precede a selector.** Organ, amplifier, mechanical,
   cabinet and microphone-scene identities are separate. The 122 input uses
   full differential volts and explicit per-leg loading; the 147 input is a
   distinct single-ended boundary. Normalized samples need a declared physical
   conversion before either is called calibrated (pp. 255, 261, 265).
2. **One owner for each effect.** Driver response, propagation, cabinet
   filtering, microphone coloration and room contributions cannot appear twice
   in a chain. Every future IR/profile needs included-response metadata and
   time/reference-plane information (pp. 278, 296, 305, 325, 331).
3. **Persistent audio-owned motion.** One horn trajectory and one drum
   trajectory serve all receivers. A command changes future evolution, not
   current speed or phase. Note activity and GUI refresh do not own mechanics
   (pp. 292, 319-324).
4. **Meaningful event timing.** Preserve ordered sample-stamped commands,
   including mid-ramp reversals. A future Slow/Fast selector is discrete;
   continuous service parameters require a separate curve contract. Queue
   exhaustion must have a visible bounded policy (p. 321).
5. **Explicit historical and rate semantics.** Delayed paths can query motion
   before the latest command. Rate changes preserve physical time/speed/angle
   while rebuilding or deliberately transitioning sample-indexed histories.
   Suspension has a documented deterministic freeze policy unless a distinct
   catch-up policy is selected (pp. 304, 322).
6. **Presets retain controls, not histories.** The existing `B3CONTROLS3`
   serializer already separates these concerns. Future parameter additions and
   migrations need an append-only identity review; no unused knob requires an
   invented state field now (p. 322 and `ControlStateIO.h`).
7. **Prepared resources and bounded callbacks.** No parsing, allocation,
   coefficient fitting, file access or UI calls occur in audio processing.
   Prepare complete replacement resources away from the callback and retain
   explicit transition timing (pp. 256, 262, 280, 298, 304, 328).

## Standalone acceptance recommended to the implementing waves

These are proposed checks for the new application, **not checks executed by
this reading assignment**.

- Use identical canonical events to compare standalone processing to the
  existing Engine at each supported rate. Preserve legacy dry output when the
  new frontend is inactive; retain the actual source/profile identities.
- Vary GUI refresh, window visibility and callback block partitions without
  changing source phase, held-note authority or audio under the declared event
  timing policy. UI timing must not become a hidden modulation input.
- Exercise overlapping computer-keyboard/mouse note ownership, focus loss,
  key repetition, rapid release and queue saturation. Note release/panic must
  affect its intended authority and leave registration controls intact.
- Verify that every enabled control changes the corresponding actual control,
  and every unavailable cabinet/scanner/room control produces no pretend
  audible or saved-state change.
- Save and restore all hidden A/B banks, route bits, percussion settings and
  both pedal mixtures through the existing state format. Test rejection of
  malformed data without replacing current controls. Perform serialization and
  disk operations off the audio thread.
- Distinguish selected device/rate from the obtained callback configuration;
  verify callback format, bounds, failure silence, clean start/stop and shutdown
  quiescence. A dummy backend test establishes software behavior, not physical
  device playback or deadline reliability.
- Record actual channel behavior. Identical dry L/R output must not acquire
  a spatial-acoustic claim because the application has two meters.
- Record the optional SDL dependency's exact source/version/license and the
  tested platform. Default core builds must remain independent of that SDK.
  An executable build, a screenshot, a dummy callback and a real device run are
  four different observations.

## Concrete later Leslie work

After the standalone adapter, useful independent M6 research can begin with
strict versioned 122 input/divider graphs and an independent offline complex
reference. The source provides the nominal divider values and graph on pp.
271-274: L2 3.2 mH, L3 5.2 mH, C16A 7.8 uF, C16B 12.5 uF; the treble load is
across A-H and has a floating return. Constant 16-ohm loads are an explicitly
idealized numerical fixture, not real driver impedance. Do not replace that
graph with a generic 800 Hz crossover or label its electrical outputs as
microphone pressure.

Electrical integration then needs actual source/load conventions, reviewed
amplifier connectivity, DC/convergence tests and distinct 122/147 identities.
Physical fitting requires specimen, installed driver and transformer identities,
calibrated voltage/current captures, source impedance, raw timing and held-out
conditions (pp. 257, 263, 269, 275).

M7 provisional mechanics/acoustics can have their own bounded mathematical
tests, but promotion to a measured cabinet requires synchronized horn/drum
angles, geometry, installed polarity, phase-preserving angular responses,
microphone calibration and panel/room metadata. Published Model 600, 122A,
modern 122H and different-driver data cannot become target vintage-122
measurements by renaming them (pp. 279, 287, 289, 307, 313). Complete dry-organ
qualification and the plan's upstream-first fitting order remain separate
dependencies; a finished standalone window closes neither M6 nor M7.

## Commands and result scope

Commands ran from the assigned repository unless an absolute path is shown:

```sh
cat AGENTS.md
git rev-parse HEAD
git rev-parse 'HEAD^{tree}'
git status --short
sha256sum Hammond_B3_Leslie_Research_Atlas_500pp.pdf
wc -l -w /workspace/scratch/5ba97739b54c/atlas/part4.txt
sed -n '1,700p' /workspace/scratch/5ba97739b54c/atlas/part4.txt
sed -n '190,330p' /workspace/scratch/5ba97739b54c/atlas/part4.txt
sed -n '701,1250p' /workspace/scratch/5ba97739b54c/atlas/part4.txt
sed -n '1251,1850p' /workspace/scratch/5ba97739b54c/atlas/part4.txt
sed -n '1851,2450p' /workspace/scratch/5ba97739b54c/atlas/part4.txt
sed -n '2451,3050p' /workspace/scratch/5ba97739b54c/atlas/part4.txt
sed -n '3051,3650p' /workspace/scratch/5ba97739b54c/atlas/part4.txt
sed -n '3651,4250p' /workspace/scratch/5ba97739b54c/atlas/part4.txt
sed -n '4251,4800p' /workspace/scratch/5ba97739b54c/atlas/part4.txt
sed -n '4801,5043p' /workspace/scratch/5ba97739b54c/atlas/part4.txt
pdftoppm -f 272 -l 272 -r 110 -singlefile -png \
  Hammond_B3_Leslie_Research_Atlas_500pp.pdf \
  /workspace/scratch/5ba97739b54c/atlas/a04/page272
```

The same rendering command was run for pages 283 and 326, and all three PNGs
were opened with the image inspection tool. The extracted part has 5,043 lines
and 26,480 whitespace-delimited words. Production source inspection used
bounded `sed` reads and `cat` for the named header. This assignment performed
source/document review and image inspection only; no project build, audio-device
run, external-primary-source verification or physical-fidelity test is claimed.
