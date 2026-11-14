# Project plan: Hammond B-3 and Leslie

**Combined-source continuation:** the [completion and integration record](REFERENCE_REFINEMENT_CLOSURE.md)
records all 60 accepted agents, the integrated `487064d` R4/material source,
the fresh v5 native gallery and its separate qualification. Source-specific
`0881d1f4`/v4 results below remain historical evidence for those exact inputs.

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

## Current ownership and accepted source

Two owner-requested sessions continue different parts of this plan. Each retains
its own actual assignment manifest; neither supplies workers or completion credit
to the other. Read the [concurrent handoff](development/2026-11-14-reference-refinement/CONCURRENT_HANDOFF.md)
before overlapping interface, build, gallery or shared-documentation work.

| Session and starting source | Current responsibility and live records |
| --- | --- |
| Reference refinement, `8bd999efc13e309b932e6ac41d72ceb7b9b80a5f` | Accepted M9 layout/material/inspection and measured-header work, native R2/R3 qualification, exact-source capture/admission and remaining session closure; [scope](REFERENCE_REFINEMENT_SCOPE.md), [checkpoint](development/2026-11-14-reference-refinement/CHECKPOINT.md), [actual manifest](development/2026-11-14-reference-refinement/assignments.json). |
| Waveform continuation, `2e161dc3a60fc3442051799574feed37bffbfc5c` | Independent R4 waveform implementation and its separately verified subsequent native visual work; [scope](development/2026-11-14-waveform-continuation/README.md), [checkpoint](development/2026-11-14-waveform-continuation/CHECKPOINT.md), [actual manifest](development/2026-11-14-waveform-continuation/assignments.json). |

The accepted measured-header product source is
`0881d1f4c5a26ce9c75dda7a3adde46382e5ab6b`, tree
`f8144b771cda1264a8788f8297f5bfec999f4a08`; its
[publication receipt](development/2026-11-14-reference-refinement/reports/root-header-publication.json)
retains the observed remote identity. Use the
[setup handoff](REFERENCE_REFINEMENT_HANDOFF.md),
[operating guide](INTERFACE_RUNBOOK.md) and both live checkpoints for exact
commands and subsequent accepted results. The [complete refinement atlas review](research/REFERENCE_REFINEMENT_ATLAS_REVIEW.md)
preserves the completed 500-page reading; later session work does not replace
the milestone exits above or the original source facts.

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

The current [reference refinement](development/2026-11-14-reference-refinement/README.md)
adds deeper wide manuals, a disjoint cabinet/pedal arrangement, live material
refinement, singular inspection labels and the accepted measured wide header.
The preceding [v4 gallery](../examples/demos/standalone-interface-preview-v4/README.md)
contains eight native views from the published `0881d1f4` source above.
[A50's independent admission](reviews/REFERENCE_REFINEMENT_FINAL_GALLERY.md)
passes 611 retained-evidence checks and records exact musical, source,
executable and pixel identities. Its dummy SDL audio/video and software-renderer
captures establish their stated application scope. The
[native-input review](reviews/REFERENCE_REFINEMENT_NATIVE_INPUT.md) separately
audits the earlier X11 executable: keyboard-held pedal resize and persistent
mouse capture/release are observed. That OS journey has no painted pre-held
keyboard prefix for Service/Flat; it supplies no new v4 OS-input run. Preserve
those distinct scopes.

The v1/v2/v3 and earlier MIDI/chapel galleries remain unchanged historical
evidence. The exact source cabinet artwork supplies decoration; controls and
state remain live. **Literal whole-interface 1:1 visual equality remains unmet**,
including after the measured header improvement. Connected rotary audio,
native semantic accessibility, real display/controller/audio-device acceptance,
DAW journeys, callback deadlines and signed distribution retain separate
product gates in [release readiness](RELEASE_READINESS.md).
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

[A49's full 157/157 CTest result](development/2026-11-14-reference-refinement/notes/A49-coherent-final-build.md)
qualifies its recorded frozen repository inputs and `0881d1f4` product sources.
Later documentation and ledger changes require their affected integrity checks;
they do not inherit that frozen Markdown identity. The live checkpoint owns
later hosted observations, and exact primary logs own test/instrumentation
claims. Preserve the earlier 154/155 run, separate 1/1 repair and all original
failures. Finish each active session with its own actual acceptance records and
strict completion gate; historical ledgers do not close a new session.
