# A06 - atlas 417-500 and bounded M9 recall

## Reading and evidence

Personally read every complete form-feed section for PDF ordinals 417-500,
including the source directory, plus page 416. Direct `pdftotext -layout -f 417
-l 500` from the original PDF matched all 84 sections in `atlas/atlas.txt`.
Visually inspected original-PDF renders of 416, 418, 424, 437, 440 and 453:
bank preparation, scope/eligibility, versioned activation, shared semantic
bindings, the illustrative control surface, and runtime ownership. These are
proposals/diagrams, not observed application screenshots.

PDF SHA-256: `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
Full extraction SHA-256: `e6ed8ed76663a8f12c487ae1e4d3ab69facc36971df240a15b1ba36eeb22485d`.
Range 417-500 SHA-256, UTF-8 sections joined by form feed without final separator:
`71ae24d0b7f4474b924fc38e1b67521c5053af0623d15df35aae1872553bb60a`.

| Read range | SHA-256 prefix, same joining rule |
| --- | --- |
| 417-428 | `a61cc961665db328` |
| 429-440 | `bd6fd9333f311684` |
| 441-452 | `fbcfb5fafb7c16a3` |
| 453-464 | `26916cb741449931` |
| 465-476 | `fccdec8ba6bf8f7f` |
| 477-488 | `d49486d6d2d54c50` |
| 489-500 | `64d165df5edf4c3f` |

Read complete AGENTS.md, PLAN.md, session README, checkpoint and assignments.
Baseline `138fca9` is the assigned identity; no independent Git operation occurred.
Inspected actual main.cpp, UiModel.h/.cpp, StateFiles, Session and ControlSnapshot,
plus native workflow/replay fixtures. Source SHA-256 prefixes: main.cpp
`937b837d4ef4317d`, UiModel.cpp `49c68995aad96aa5`, UiModel.h
`d94e90be25812c6d`.

## Roadmap assessment

Pages 445-456 and 481-492 require separate engineering, physical and release
decisions. M0 evidence identity supports M1 deterministic infrastructure and M2
shared sources; M3 retained controls can advance independently of missing M5
AO-28 connectivity. M4 numerical work needs independent signed, loaded,
same-frequency comparisons: page 483 explicitly rejects undeclared warped-to-
analog comparisons. ScannerLineFoh is therefore reasonable as an independently
identified realization, preserving v1 and frozen thresholds; it earns no Engine
route, rotating-capacitance, physical or complete G5 acceptance automatically.

M6 electrical loading, M7 motion/acoustics, M8 acquisition/calibration and M9
device/host/release remain separately gated. Pages 457-480 preserve unknown
connectivity, specimen, geometry, measurement and rights questions; source counts
or licensed images cannot close them. Leave fidelity-owned deck/M6 FOH/MIDI-close
and waveform-owned R4 paths untouched. Whole-interface 1:1 remains unmet. The
PLAN's older operational pointers need root reconciliation with this session's
explicit routing, without changing historical evidence.

## Recommended recall contract

Pages 416/418 directly support modern Save Registration/Save Performance outside
the reversed octave. Freeze explicit fields rather than letting “preset” imply
physical latches. A safe initial **Registration** copies the displayed selection
of drawbar banks/pedal positions only; default to the chosen edit bank, retain
sounding route, expression and percussion, and require an explicit separate
selection to sound it. **Performance** restores every current ControlSnapshot
field, visibly including expression and retained routing. Neither scope contains
device configuration, MIDI calibration, output trim, specimen profile, microphones,
held notes, source phase or percussion history. Do not promise future controls
that are absent from today's snapshot.

Keep all 47 parameter IDs and B3CONTROLS4/readers 1-3 unchanged. Store catalog
name/kind/scope in an independently versioned envelope or index around the existing
payload. Validate complete input off-callback; merge a registration into the latest
desired controls, preserving concurrent pending MIDI/UI edits. Publish one copied
ControlSnapshot through Session; no file I/O, strings or catalog traversal enter
the callback. Save only a coherent acknowledged copy, using existing replacement
semantics and preserving old files on failure.

Minimal browser: an explicit toolbar command, stable named rows, selected-item
details, target/scope text, Save, Recall, Refresh and Close. Navigation never
recalls. Use ordinary Tab/Shift+Tab, list arrows/Home/End and explicit activation;
restore focus on close. Show empty, invalid, unavailable and failed states. If
names are editable, add actual SDL text input while suppressing performance
shortcuts; the existing boolean text gate alone is not a text editor.

Request state is distinct from applied state. Display Pending after acceptance,
then Applied only for the matching sequence, unchanged recovery/rejection/discard
counters and expected acknowledged controls. A sequence merely being resolved
does not prove success. Save/reload must not erase a later edit or accept a stale
completion. Main's current immediate “Loaded saved controls” message after queue
acceptance is insufficient for this feature.

Two source hazards need dedicated handling: `open_overlay()` currently invokes
`lose_input()`, releasing UI owners; browsing during a held chord should close a
parameter drag without inheriting that release policy. `load_controls()` changes
the whole clean-file baseline before acknowledgment; scoped recall needs a
separate merge/publication operation that preserves ordinary Save dirty tracking.

## Acceptance and accessibility

Pages 417/420/433-438 require original press identity, key-up before modal gates,
focus distinct from selection, visible focus and equivalent flat controls.
Expose consistent names, target bank, value/range and outcome text; decoration
cannot carry unique information. SDL keyboard operation does not establish a
native semantic tree or screen-reader usability. Keep those platform journeys
unqualified until actually observed. Pages 439-444 distinguish state doubles,
real dispatch, reviewed pixels and assistive workflows.

Required end-to-end tests should drive the actual browser through SDL, Session
and files: hold UI plus external notes while preparing/recalling an inactive bank;
verify only scoped fields change and source/percussion continuity survives;
apply Performance and restore all retained banks/routes/expression; save, restart
and reload exact bytes; cancel/malformed input leaves sound and disk unchanged;
delayed acknowledgement, overflow/recovery and newer edits never report false
success. Include pending CC11 followed by registration recall, focus changes
before key-up, minimum/wide/Flat layouts and return focus. Retain actual traces,
source/executable/state/pixel identities and reviewed captures. Unit merge tests
and dummy SDL replays remain distinct from real-device, native accessibility and
physical-fidelity acceptance.

Executed here: source/extraction hashes, full-range PDF/text equality and visual
diagram inspection only. No builds, runtime tests, Git operations or shared edits.
