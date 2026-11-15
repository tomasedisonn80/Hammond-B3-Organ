# A04 - Complete atlas reading: electrical cabinet and rotary boundaries

Actual worker: `/root/w01_a04_atlas_rotary`. Wave 1, assignment A04.
Reviewed checkout: `647ae1b2b6ad8d30ee28ab348b94f974fb6aadbb`.
This assignment changes only this note; it performs no build, runtime test,
measurement, product edit or publication.

## Complete coverage and source identity

Read every page **253-336 inclusive**, 84 pages, chapters 41-54. Reading covered
seven consecutive twelve-page ranges: 253-264, 265-276, 277-288, 289-300,
301-312, 313-324 and 325-336. Page 258 was reread after an output clipped its
heading. No page was omitted. Also read the complete `AGENTS.md` and
`docs/PLAN.md`; inspected current status, next-step context, development log,
renderer contract/header and native inspection/painter implementation.

| Input | SHA-256 |
| --- | --- |
| Original 500-page PDF | `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769` |
| Complete assigned extraction `part04-253-336.txt` | `bd0295415ea8897d04c037a119081d4ab3a983d2b4aa3d80eaf3725d9db9c526` |

## Requirements established by this reading

| Pages | Required project behavior and evidence limit |
| --- | --- |
| 253-270 | Identify the vintage 122 amplifier revision separately from 147 and modern 122H. Preserve full differential volts, actual input loading, control-detector separation, winding polarity, shared bias and supply dependencies. A serial soft clipper is not a connected 6550 circuit. No target hardware captures were performed. |
| 271-276 | Transcribe the four-element crossover and its floating treble return before choosing digital filters. Nominal 800 Hz is not an exact crossover transfer. Electrical driver impedances and acoustic transfer need separate ownership. Unknown parasitics stay null. |
| 277-288 | One stationary compression driver feeds one driven horn; the opposite horn is a counterbalance. The bass woofer stays fixed while its deflector turns. Acoustic radius is not automatically photographed physical radius. Keep common timing, signed phase, independent horn/drum inputs and acquired-response ownership. |
| 289-300 | Horn and drum have independent motion profiles and continuous phase. The documented bass 5-8-second service criterion is not a universal exponential time constant. Cabinet appearance, measured geometry, internal acoustics and room are separately evidenced. Unknown dimensions cannot be inferred from concept art. |
| 301-324 | Solve emission-time propagation against one history per rotor, with microphone-specific past observations. Validate interpolation endpoints, passband and aliases separately. Continuous motion cannot be driven by UI refresh. Commands, sample-rate epochs and suspension require explicit continuity policies. |
| 325-336 | Input-time and output-time angular weighting describe different time-varying systems. Retain FIR history, full tails, phase, gain, reversible preprocessing and all MIMO paths. Room, cabinet and microphone effects have one owner each. Optional 122RV spring electronics and stationary wet speaker remain separate from baseline 122 and studio reverb. |

The atlas's synthetic algebra fixtures and referenced companion filenames are
documentary evidence of its original work. They do not prove that missing files
were recovered or that the present application passed those experiments.

## Current implementation boundary

`include/hammond/RotaryRenderer.h` explicitly describes an independent nominal
R4 research renderer. `docs/ROTARY_RENDERER_CONTRACT.md` limits it to separate
radiation-boundary inputs, direct-point propagation, cubic interpolation and
distance gain. It supplies no connected electrical, driver, directivity,
cabinet, room or microphone-filter model. R5 numerical-audio policy, R6 runtime
integration and physical M7 evidence remain separate gates. The other session
owns R4 implementation and remaining acceptance; this assignment does not
duplicate or modify that work.

`apps/standalone/InspectionModel.cpp` already reports cabinet audio **Not
connected**, horn/drum speed **Unavailable**, microphone geometry **Not
acquired**, and Stop/brake **Not modeled**. `InstrumentView.cpp::paint_rotary`
paints those read-only facts beside explicitly decorative cabinet artwork.
These statements correctly describe the currently dry Engine.

## Consequences for the requested reference interface

Atlas pp.258, 294 and 322 distinguish a requested speed from actual estimated
speed; future animation must follow copied model state. Pages256, 289 and294
make Slow/Fast the vintage baseline and require a named accessory/extension
for Stop or braking. Therefore cosmetic reference refinement must not activate
fictional microphone or speed controls, display invented rpm/metres, or animate
an unrelated rotor clock. Preserve readable unavailable-state wording and all
existing musical identities while improving materials and typography.

## Concrete next milestone and acceptance

For this session, M9 legibility/material work and adapter-only MIDI/controller
improvements can proceed without waiting for physical cabinet acquisition.
Acceptance must retain source-identified actual screenshots, unchanged dry
audio/state meaning, truthful Rotary facts, shared hit/paint geometry and
keyboard/held-note ownership.

A subsequent independent **M6 passive-network foundation** is documentary-ready:
review the dated crossover graph against its primary drawing, retain
L2=3.2 mH, L3=5.2 mH, C16A=7.8 microfarads and C16B=12.5 microfarads with
page provenance, then implement an offline nodal reference with explicitly
ideal 16-ohm resistive loads. Require independent complex output/admittance,
polarity, floating-return and energy checks before a prepared runtime model.
This neither connects cabinet audio nor validates measured driver loads;
specimen losses, impedance, polarity and acoustic captures remain outstanding.
