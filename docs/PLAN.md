# Project plan: Hammond B-3 and Leslie

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

## Future user interface

The art direction on pp. 409-444 specifies a walnut/charcoal/brass instrument,
readable drawbars and manuals, a cabinet view, player and service workspaces,
resize support, keyboard access, reduced motion and a flat usable alternative.
Build controls from stable verified parameter identities. A camera movement or
editor closure must never change audio routing or clock state. Generated concept
art is design intent; it is neither hardware dimensional evidence nor a working UI.

## Keeping the plan alive

`AGENTS.md` is mandatory for every future development session. The integrator
updates [STATUS.md](STATUS.md), [NEXT_STEPS.md](NEXT_STEPS.md) and
[DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md) after each substantial milestone, records
actual commands/results, and commits/pushes authorized changes. Every acceptance
result names its code and data identities; changing a dependency can invalidate
only the affected claims. Never change a status to pass merely because a plan or
an interface exists.
