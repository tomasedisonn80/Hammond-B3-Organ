# Project plan: Hammond B-3 and Leslie

**Current authority — 15 November 2026:** the
[product continuation](development/2026-11-15-product-continuation/README.md)
advances M9 native MIDI channel modes, expression-controller calibration and
measured visual refinement, together with an independent M6 passive crossover.
Read its [checkpoint](development/2026-11-15-product-continuation/CHECKPOINT.md),
[actual assignments](development/2026-11-15-product-continuation/assignments.json),
[current status](STATUS.md) and [next actions](NEXT_STEPS.md) before choosing work.
The separately owned waveform session retains R4. Earlier completed sessions
remain source-specific history; their worker counts do not close this session.

## Product objective and evidence boundary

Build one inspectable C++ engine for a faithful recreation of an identified vintage
Hammond B-3/AO-28 organ and Leslie 122, then expose it through a VST3 plugin and a
standalone application with the atlas's dimensional instrument interface. Leslie
147 and other variants require separate profiles. A claim of a measured match must
name the specimen, revision, signal boundary and tested operating conditions.

The source is the 500-page research atlas, preserved unchanged. It organizes 80
chapters into ten **research** waves. Its implementation sequence is **M0-M9**
(PDF pp. 5, 445-456, 481-492). The 60-agent implementation session is yet another
work organization: ten waves of six actual assignments. These counts are not
interchangeable measures of product completion.

The baseline repository had no engine, companion JSON, reference C++ header,
measurement corpus or plugin. The PDF explicitly states that its original research
included no newly acquired instrument measurements (p. 2). New implementations and
reconstructions retain their own provenance; absent companion results are not tests
that this repository has executed.

The current session's A01–A06 notes retain complete textual coverage of pages
1–500, with individual page ranges and extract hashes in the
[reading map](PROJECT_GUIDE.md#source-and-reading-records). The unchanged PDF
SHA-256 is `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
Reading the atlas does not independently verify every cited drawing or supply
missing specimen measurements.

## Milestones and exit evidence

| Milestone | Engineering deliverable | Required exit evidence | Physical/evidence dependency |
|---|---|---|---|
| **M0 — reference and contracts** | Versioned target/profile identities, source hash, evidence classes, explicit unknowns, acquisition queue, permanent agent rules | Validated nominal profile, source traceability, missing-input and rights records | Actual specimen serial, AO-28 revision, condition, cabinet identity and measurement permissions remain unresolved |
| **M1 — testable skeleton** | Framework-independent prepared graph, bounded sample events, offline WAV rendering, profile validation, diagnostics | Executed scheduler/flush/overflow/lifetime/error tests; repeatable render with identities; no callback allocation in tested path | No physical audio claim; choose and label a nominal surrogate when data is absent |
| **M2 — shared generator** | 91 continuously running shared sources, separate IDs and arrays, explicit manual and pedal mapping, profile-defined frequencies | Pitch/phase/coherent-sum tests, low/high/double-fold boundaries, callback partition equivalence | Factory routing is corroborated by the retained independent comparison; production gear relationships, measured pickup waves/levels/phases and leakage remain open |
| **M3 — console behavior** | Nine-contact trajectories per manual key, four retained drawbar banks, preset latches, pedals, percussion, expression | Held-key and repeated-note interactions, non-panic cancel, shared percussion/recharge, routing and state tests | Contact capture, transformer tap loading, pedal shaping, expression and percussion circuit evidence |
| **M4 — scanner** | Verified LC and scanner topology, one scanner phase/history, V1-V3/C1-C3 routing, stable numerical model | Independent loaded AC and time-domain comparisons, mode transitions and long-run numerical tests | Revision-specific connectivity/loading and actual scanner captures; resolve printed pseudocode erratum first |
| **M5 — organ electronics** | Connected AO-28 graph, linear networks before nonlinear stages, loading/feedback, dry G-G diagnostics, oversampling | Operating-point/convergence/alias tests; complete dry organ validation before cabinet fitting | Component placements are not a complete netlist; transformer data, operating points and dry captures required |
| **M6 — Leslie electronics** | Separate 122/147 models, amplifier/transformer/crossover/driver loading, differential voltage ports | Polarity, impedance/load, independent AC and nonlinear stability tests | Identified cabinet revision, real driver impedance, electrical measurements |
| **M7 — rotary acoustics** | Independent horn/drum dynamics; rotating directivity, propagation, microphone geometry, optional room | Causal moving-path/interpolation tests, stereo/mono, transitions, tails, sample-rate checks | Rotor trajectories, angle/position captures, cabinet/room separation |
| **M8 — calibration** | Immutable captures, train/held-out grouping, fitting and uncertainty reports, listening protocol | Predeclared tolerances, retained raw/derived ancestry, held-out results including failures/inconclusive cases | Physical acquisition cannot be replaced by synthetic audio or a schema pass |
| **M9 — product and release** | VST3 and standalone adapters, stable automation/state, accessible resizable 3D/flat UI, packaging | Actual validator/DAW/device runs, callback deadlines, state migrations, native accessibility, licenses and platform builds | Separate qualification for each platform, host and published fidelity claim |

## Dependency rules

M0 engineering contracts enable M1. M1 enables M2. The first audible deliverable
is a **nominal dry engine**, with explicit model identities and normalized output.
It is useful for testing timing and routing while the physical corpus is missing.

M3 behavioral work follows stable M2 identities. M4 numerical research can proceed
in parallel once its ports and ownership are fixed. M5 must validate the complete
dry organ before fitting downstream cabinet effects. M6 documentary work can
proceed earlier; M7 acoustic rendering needs explicit effect ownership so delays,
filters and room responses are not counted twice. M8 calibration is incremental,
but only acquired evidence can close a specimen-specific fidelity gate. An M9
adapter smoke test may start after M1/M2; that does not complete product release.

## Current ownership and source

| Session | Responsibility and recovery authority |
| --- | --- |
| Product continuation, starting `647ae1b2b6ad8d30ee28ab348b94f974fb6aadbb` | Active M9 MIDI/calibration/visual work and independent M6 crossover; [scope](development/2026-11-15-product-continuation/README.md), [checkpoint](development/2026-11-15-product-continuation/CHECKPOINT.md), [actual manifest](development/2026-11-15-product-continuation/assignments.json). Its own 60-agent, ten-wave request is still in progress. |
| Waveform continuation, starting `2e161dc3a60fc3442051799574feed37bffbfc5c` | Separate R4 implementation and acceptance; [scope](development/2026-11-14-waveform-continuation/README.md), [checkpoint](development/2026-11-14-waveform-continuation/CHECKPOINT.md), [actual manifest](development/2026-11-14-waveform-continuation/assignments.json). Preserve its other checkout and unfinished work. |
| Completed reference refinement | Historical M9/R2/R3 and combined-source qualification; [closure](REFERENCE_REFINEMENT_CLOSURE.md) and [completed checkpoint](development/2026-11-14-reference-refinement/CHECKPOINT.md). All 60 accepted workers remain closed historical records. |

The published product checkpoint at this reconciliation is
`d8c39f7986746eacc991747153c7dbb012bb9a32`, tree
`edf67b978f93e8dbea6537ce92d3928c171bc1f3`; its
[publication receipt](development/2026-11-15-product-continuation/reports/gallery-publication.json)
records the verified parent and non-force update. All
[13 hosted jobs succeeded](development/2026-11-15-product-continuation/reports/d8-hosted-status.json),
with primary [Linux](reviews/PRODUCT_LINUX_HOSTED_REVIEW.md),
[Windows](reviews/PRODUCT_WINDOWS_HOSTED_REVIEW.md),
[macOS](reviews/PRODUCT_MACOS_HOSTED_REVIEW.md) and
[VST3](reviews/PRODUCT_VST3_HOSTED_REVIEW.md) evidence. The expanded native
sanitizer selection actually passed 21/21; the material fixture is 1,293
assertions/109 frames and Standalone inventory is 16 files MIDI-OFF/20 MIDI-ON.

The later [coherent local run](development/2026-11-15-product-continuation/reports/wave8-coherent-build.json)
passed 180/180 in 507.55 s at d8 plus accepted A46/A48 checker/admission changes,
with 366 frozen code/test/build/data inputs unchanged. Those repairs still
need publication and their own hosted result. [STATUS.md](STATUS.md) preserves
the original b9 install/Windows failures, d556 sanitizer build failure and
earlier ff41 feature result under their exact source identities. The live
checkpoint owns later progress; sixty-worker closure is still pending.

The integrator owns the current checkout/build and shared publication. Read the
active checkpoint and [concurrent handoff](development/2026-11-14-reference-refinement/CONCURRENT_HANDOFF.md)
before overlapping source, paint, gallery or build work. Use the
[setup/recovery handoff](PRODUCT_HANDOFF.md), [native operating guide](MIDI_EXPRESSION_GUIDE.md) and
[crossover developer guide](CROSSOVER_DEVELOPER_GUIDE.md) for current commands;
an old setup path or test count is not a current acceptance result.

## Current implementation design choices

See [IMPLEMENTATION_CONTRACT.md](IMPLEMENTATION_CONTRACT.md) for the initial API and
model scope. Use C++20 standard-library code without host or UI dependencies in the
core. Python standard-library tools handle rich authoring data and reproducible
offline workflows. Add external dependencies only when a specific milestone needs
them, with a pinned version and license record.

The first generator uses 12-TET, ideal sine waves, reproducible proposed phases and
normalized amplitude. The atlas gives tone 1=MIDI 24 and tone 46=MIDI 69 as test
anchors (p. 61). Manual wiring is reconstructed from pp. 98-99 and compared with
six printed rows on p. 102. A later [factory comparison](FACTORY_REFERENCE.md)
matches all 549 manual assignments and 200 pedal positions to two independent
direct-image transcriptions. The atlas's absent companion table remains absent;
the new evidence has its own source identity and provenance.

Source phase advances during silence and disconnected-output processing. Note
velocity does not scale steady organ loudness. Drawbar branches add coherently;
polyphony-dependent normalization must not disguise source-sharing mistakes.
Data loading and profile replacement happen with processing stopped until a
separately tested publication/retirement protocol exists.

## Current M6 foundation and next numerical phase

The [ideal Leslie crossover](LESLIE_CROSSOVER_CONTRACT.md) is implemented as an
independent four-state electrical module, with fixed documentary L/C values,
floating treble A–H output, bass W–B output and ideal 16-ohm default loads.
Independent analog/reference, actual recurrence/sine, lifecycle, energy and
allocation checks are retained. [CrossoverTools](CROSSOVER_INSTALL.md) supplies
an explicit six-file copy-only component. Neither the module nor its installation
connects an amplifier, driver or cabinet to Engine.

The [same-Hz characterization](LESLIE_CROSSOVER_CHARACTERIZATION.md) retains the
frequency differences separately from accepted warped-reference parity. After
this session's closure, the first independent M6 task is to freeze a versioned
electrical-accuracy protocol, then evaluate a separately identified realization
against it. [NEXT_STEPS.md](NEXT_STEPS.md#next-dependency-ready-phase-after-session-closure)
names the available inputs, affected modules and acceptance. Preserve v1 and its
documentary values. Component losses, source impedance, complex driver loads and
assembly/specimen applicability remain acquisition-dependent unknowns; numerical
improvement cannot close full M6 or authorize a live audio route.

The [numerical admission review](reviews/PRODUCT_NUMERICAL_ADMISSION_REVIEW.md)
repairs acceptance of incomplete or contradictory replacement reports while
preserving the original numerical report, six source identities, probe and
thresholds. The response grid is 126 in-band points out of 130 per group.
Root's [plot refresh](development/2026-11-15-product-continuation/reports/crossover-plot-admission-refresh.json)
changes only generator-hash metadata; every decoded pixel remains identical.
This is evidence admission, not a new numerical realization or physical result.

## Current rotary implementation and remaining model gates

Native [R2 motion](ROTARY_MOTION.md) and
[R3 historical propagation](ROTARY_PROPAGATION.md) are implemented and
independently qualified for the named nominal numerical workloads under the
[frozen contract](ROTARY_NUMERICAL_CONTRACT.md). They return motion and path
facts; they contain no waveform rendering and insert no rotary audio into
Engine. Separate horn/drum radiation-boundary inputs, one physical trajectory
per rotor and explicit effect ownership remain required for later M7 rendering.

The waveform session has implemented R4 bounded histories, cubic fractional
delay, transactional stereo rendering and an [offline developer tool](ROTARY_RENDER_CLI.md).
Its accepted [renderer contract](ROTARY_RENDERER_CONTRACT.md) and
[waveform acceptance](ROTARY_WAVEFORM_ACCEPTANCE.md) govern the implemented module.
The earlier [brief](ROTARY_RENDERER_PLAN.md) and
[independent implementation proposal](ROTARY_RENDERER_IMPLEMENTATION_PLAN.md) remain
planning inputs with their own stronger storage assumptions. The full waveform
experiment has passed its exact frozen inputs; remaining lifecycle, symmetry,
allocation, CLI and platform acceptance stays with the waveform owner. R5 audible
policy and R6 runtime/Engine integration retain separate gates. The playable
Engine remains nominal and dry.

The later full R4 job in the [d8 Linux audit](reviews/PRODUCT_LINUX_HOSTED_REVIEW.md)
also passes its published inputs. It does not close the other owner's unfinished
checkout or transfer its acceptance and worker-ledger ownership.

The scanner's [G5 same-hertz failure](SCANNER_HANDOFF.md) remains unresolved
under its [numerical contract](SCANNER_NUMERICAL_CONTRACT.md); do not connect
it to Engine by treating an earlier numerical pass as audible acceptance.
Complete revision-specific M5/M6 electrical graphs, real cabinet evidence and
the [physical acquisition sequence](CALIBRATION_NEXT_ACQUISITION.md) remain
separate dependencies. Numerical primitives and documentary artwork do not
close M5–M8 fidelity gates.

## User interface direction and current implementation

The art direction on pp. 409-444 specifies a walnut/charcoal/brass instrument,
readable drawbars and manuals, a cabinet view, player and service workspaces,
resize support, keyboard access, reduced motion and a flat usable alternative.
Build controls from stable verified parameter identities. A camera movement or
editor closure must never change audio routing or clock state. Generated concept
art is design intent; it is neither hardware dimensional evidence nor a working UI.

The optional [native standalone](INTERFACE_RUNBOOK.md) implements a resizable
reference-led instrument with keyboard/pointer and optional MIDI input,
Play/Rotary/Service workspaces, shared perspective hit/paint geometry, transient
Flat presentation and truthful copied-state inspection. It retains **147 playing
keys** (61 Upper + 61 Lower + 25 pedals), **24 reversed presets**, four drawbar
banks, fixed registrations, percussion, expression, device settings and explicit
Save/Load. All **47 sound parameters**, the **`B3CONTROLS4`** writer and readers
1–3 preserve their meanings; presentation changes do not migrate sound state.

The current [visual refinement](PRODUCT_VISUAL_REFINEMENT.md) adds fitted
footage legends, 32-pixel manual caps, distinct EDIT BANK/SOUNDING rows and
restrained natural-key lighting in wide Dimensional views. Compact/Flat paths
retain their accepted pixels. The separate MIDI modal adds endpoint/inversion
settings and eleven focus stops; the [operating guide](MIDI_EXPRESSION_GUIDE.md)
explains selected, configured, active and pending state. Calibration is adapter
configuration, not a saved musical parameter or an AO-28 expression model.

The [reference-gap review](design/PRODUCT_REFERENCE_GAPS.md) and
[independent gallery admission](reviews/PRODUCT_GALLERY_ADMISSION.md) distinguish
scoped raster/timing evidence from physical display acceptance. The current
[eight normal views](../examples/demos/standalone-product-preview-v1/README.md)
and [three MIDI overlays](../examples/demos/standalone-product-preview-v1/midi-overlay/README.md)
are admitted actual `d556da01` captures from application `7ded143b…`; README
displays current Play and MIDI views. Their source, executable, replay, state and
PNG/native-pixel identities remain retained; original BMP intermediates are
unavailable. No new capture at the later publication is claimed.

The admitted [v5 gallery](../examples/demos/standalone-interface-preview-v5/README.md)
is historical `487064d2` capture evidence; v4 belongs to `0881d1f4`, and earlier
galleries retain their original identities. No older image is a capture of the
new calibration modal or painter. The [earlier native-input review](reviews/REFERENCE_REFINEMENT_NATIVE_INPUT.md)
retains its distinct X11 scope and incomplete desktop journeys.

The reference supplies visual direction, while the engineering inventory remains
61+61+25 playing keys, 24 presets and 68 controls including those presets.
**Literal whole-interface 1:1 visual equality remains unmet.** Connected rotary audio,
native semantic accessibility, real display/controller/audio-device acceptance,
DAW journeys, callback deadlines and signed distribution retain separate
product gates in [release readiness](RELEASE_READINESS.md).

The [native recovery review](reviews/PRODUCT_NATIVE_RECOVERY_REVIEW.md) also
retains A47-N1: pinned WinMM/CoreMIDI close paths can suppress native failure
results before clearing state. It is a source-proven observability gap and risk
model, not an observed hardware failure or use-after-free. The next bounded
adapter task injects faults below RtMidi and reviews checked close with preserved
dependency storage and platform callback-retirement evidence. The existing
synchronous fixtures and sanitizers do not establish that OS lifetime guarantee.
Use [NEXT_STEPS.md](NEXT_STEPS.md) for the next concrete adapter/model contracts;
the implementation milestones above remain the complete project plan.

## Keeping the plan alive

`AGENTS.md` is mandatory for every future development session. The integrator
updates [STATUS.md](STATUS.md), [NEXT_STEPS.md](NEXT_STEPS.md) and
[DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md) after each substantial milestone, records
actual commands/results, and commits/pushes authorized changes. Every acceptance
result names its code and data identities; changing a dependency can invalidate
only the affected claims. Never change a status to pass merely because a plan or
an interface exists.

The active checkpoint owns subsequent observed publication and hosted results;
primary logs own detailed test/instrumentation claims. Preserve original failures,
source-bound timings and the [completed refinement evidence](REFERENCE_REFINEMENT_CLOSURE.md).
Later documentation or ledger changes require their affected integrity checks,
and changed build/test sources require appropriate coherent qualification.
Finish this product session with its own 60 actual accepted records and strict
[product-checker gate](NEXT_STEPS.md#validate-this-sessions-actual-records).
Progress mode is available during acceptance; strict mode is required only after
all ten six-worker waves are accepted. Historical checkers, planned assignments
and an in-progress result cannot close this session.
