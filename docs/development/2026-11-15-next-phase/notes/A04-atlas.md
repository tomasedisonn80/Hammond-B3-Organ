# A04 - Atlas pages 251-333 and compatible continuation

## Reading and evidence

Personally read all 83 assigned pages, 251-333 inclusive, from the supplied
form-feed extraction, including tables, equations, captions and acceptance
statements. Checked all 83 printed page footers. Rendered the unchanged original
PDF and visually inspected pages 272, 273, 302 and 326: floating treble wiring,
complex crossover response, retarded propagation, and the two convolution
weight placements. Read the complete `AGENTS.md` and `docs/PLAN.md`, this
session's README, checkpoint and actual assignments, then current navigation
and relevant source. Starting commit `138fca9af7feca46d10b0e2b65d891f4751a3904`
is the integrator's declared baseline; this worker did not query Git.

| Pages personally read | Material and consequential finding |
| --- | --- |
| 251-252 | Connected dry-organ calibration: preserve absolute level, expression/load boundary and sample-event timing; nonlinear attribution requires unchanged topology and phase. |
| 253-270 | Separate vintage 122/147 input, control, feedback and supply identities. Differential volts, loading and transformer polarity are explicit; numerical agreement is distinct from hardware matching. |
| 271-276 | Four documented crossover values and the floating A-H treble branch. Resistive-load algebra is a nominal reference; bilinear warping must be reported at supported rates. |
| 277-288 | One driven horn plus counterbalance; a stationary woofer feeds the rotating deflector. Angular responses retain gain, phase and owned delay; photographs supply no unmeasured acoustic dimensions. |
| 289-300 | Independent motor/rotor profiles, continuous phase, direction-specific ramps and cabinet/panel identity. The documented bass 5-8 second adjustment is neither a universal time constant nor a horn measurement. |
| 301-318 | Historical emission-time geometry, interpolation endpoint audit, complex directivity, shared rotor trajectories and microphone-specific reception. Synthetic algebra checks do not validate a target cabinet. |
| 319-330 | Event-anchored motion, persistent histories, sample-rate epochs and separate musical presets/checkpoints. Input-time and observation-time convolution weights describe different moving systems. |
| 331-333 | Room/cabinet ownership, separate reflected-path emission times and complete cross-channel convolution kernels; independent normalization or peak alignment destroys calibration. |

## Comparison with current source

`ScannerLine.h/.cpp` currently identify a 36-coordinate physical-state
trapezoidal realization. Preparation builds both return topologies off-thread;
processing combines previous/current input endpoints, reconstructs signed
ground-referenced taps and commits only an admitted candidate. Its checkpoint
contains physical capacitor/inductor coordinates, prior input and frame count.
`SCANNER_NUMERICAL_CONTRACT.md` already freezes the 282-frequency grid, same-Hz
complex bound, endpoint timing, independent transient refinement and rotating
output criteria. `SCANNER_HANDOFF.md` retains failure at every allowed research
rate, including 1,536,000 Hz. Reading that record is not rerunning it.

The inspected `LeslieCrossover` interface and preparation/output source agree
with the atlas's critical floating treble boundary: output is input minus H-B
capacitor voltage; input current includes both branches. Its documentary
3.2/5.2 mH and 7.8/12.5 microfarad values should remain untouched. This validates
the relevance of preserving physical coordinates and explicit boundaries, not
the implementation's numerical accuracy. M6 FOH remains the other owner's work.

`RotaryMotion.cpp` already uses event anchors, stable exponential evaluation,
separate direction, and target-minus-current-speed selection of acceleration
time constants. Rate changes retain physical state while starting another
epoch. Consequently registration recall must not call preparation/reset or
restore trajectory checkpoints. The R4 renderer remains separately owned.

The existing `ControlSnapshot` excludes held notes, contacts, percussion
readiness, source phases and clocks. `ControlStateIO.h` explicitly preserves
`B3CONTROLS4` and readers 1-3; `Engine::restore_controls` replaces validated
controls and marks coefficients dirty. `StateExchange.h` already offers bounded
copied-state enqueue, pending acknowledgement and whole-callback commit.
These are concrete foundations for modern named registration recall without
changing historical reversed-key preset semantics.

Calibration source provides useful evidence discipline: `compare_capture.py`
compares supplied samples without fitted corrections, retains floor-dependent
phase masks, hashes exact policy bytes and reports unknown uncertainty as
inconclusive. `capture_study.py` binds jobs to one corpus and distinguishes
fit/validation/final-test roles. Neither makes a physical-fidelity claim.

## Bounded next assignments

1. Freeze a separately identified scanner FOH experiment before implementation.
   Preserve the graph, old realization and failed report. Specify linear input
   reconstruction, previous/current endpoint forcing, first-frame time origin,
   response equation and physical checkpoint semantics. Compare against the
   independent AC oracle and independently refined full-graph transient source;
   retain all signed taps, return/current, conditioning, DC and original bins.
   A stationary improvement alone cannot close G5: rotating output, filtering,
   actual processing, allocation and G6 integration remain separately graded.
2. Define modern registration storage as named musical-control snapshots using
   the existing format and handoff. Freeze recall scope, pending/applied display,
   malformed-file behavior and replacement policy first. Verify retained hidden
   banks, fixed selections, Cancel, pedals and percussion controls while held
   musical ownership and free-running histories survive. Any future physical
   profile selection needs revision identity and a separate prepared transition.

## Limits and checks

Executed reading, page-footer coverage, SHA-256 calculation and four original
PDF raster inspections only; source comparison was inspection. No build, test,
Git operation or model experiment ran. No new acquisition occurred. Atlas
companion references are not proof those files exist here. Source-document
transcription, numerical quality, physical matching and product acceptance stay
separate. R4, M6 FOH, native MIDI close and main-deck visual work remain outside
this assignment. The sole repository edit is this note.

## SHA-256 identities

Range hash is UTF-8 encoding of `"\f".join(atlas_text.split("\f")[250:333])`,
without an appended form feed. The extraction has 500 nonempty page chunks and
one empty final chunk.

```text
PDF: 4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769
Entire atlas.txt: e6ed8ed76663a8f12c487ae1e4d3ab69facc36971df240a15b1ba36eeb22485d
Pages 251-333: 36ab8d4c15f55990c80ab6eff083aa7f91c0d82a75bc0861f3455b4651ba5b2b
docs/SCANNER_NUMERICAL_CONTRACT.md: 3999a3a409d397401e135e8285704092bad130911468802370bf6da404d58ff9
src/ScannerLine.cpp: 4280db3caa3f7aa225c58a0fa64ec4ca31add55ab8bb46a27aca2deba4544336
include/hammond/ScannerLine.h: c249f7c5556d6a6c8c58978928f0b860be442cb1188d35e49c59575729af00c7
src/LeslieCrossover.cpp: 1a1bdde72af95709143afc4f62991c138ff3458cc78765fbe49a229d82693525
src/RotaryMotion.cpp: a3f986892078254f6dfae936bbbf1b5e1c4967882d06c13b3b28649f2273cfa1
include/hammond/ControlState.h: aab82b082f9cf77dadf763148cade9eae04f6f7df68b302b1832f21f78034856
include/hammond/ControlStateIO.h: 7e96c7b27906f7dfe0b9e8337888d5305fc4610f5009301b42cfae563e3ab081
include/hammond/StateExchange.h: 106dec7df367a4dd3351d243cacd26a6c8041c7ac8e874bba99a6fa26a4ac1d0
src/Engine.cpp: ea94f27be2ce6e374537c616bdde34c32c3276df6f7f24e112f52a35d1a4bd3a
tools/compare_capture.py: 220a593499539db5f1e635db2eb15ba3c0aa7c6d001c80407fbffe93f75a9a0a
tools/capture_study.py: 5147b3f7b959ff6e2e1c7ca4b49154579a212af1cf2604bb6272fd9a212f5f98
tools/scanner_transient_reference.py: 5d63941b4b85c28ebf4dce7427e87b87779c3538ae00ff2510014a1df1c45cda
```
