# A05 — Atlas runtime, calibration and native visual boundaries

## Assignment and inspected source

- Actual worker: `/root/w01_a05_atlas_ui_runtime`; wave 1, A05; 14 November 2026.
- Owned output: this note only. No product edits, shared-document edits, builds,
  test execution, commits, publication or nested workers were performed.
- Read `AGENTS.md`, the new waveform scope/checkpoint/actual assignments,
  the complete `docs/PLAN.md`, `docs/research/ATLAS_REVIEW.md`, current README,
  current status section, next steps, latest development-log entries and
  `docs/ROTARY_PROPAGATION.md` before drawing continuation conclusions.
- Observed HEAD: `2e161dc3a60fc3442051799574feed37bffbfc5c`;
  tree: `17f8e4d698f903c37bff09deee196ea73e0da108`.
  Local `origin/main` matched HEAD; no fresh remote fetch is claimed.
  The observed working changes were `AGENTS.md` and the new session directory.

### Exact SHA-256 identities

| Input | SHA-256 |
| --- | --- |
| Original 21,248,265-byte, 500-page PDF | `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769` |
| `atlas-text/part-5-335-418.txt`, 222,257 bytes | `cbe298036c55d32735144253d0667b69f7ff7dbe385fd209ae6950fb64576568` |
| `docs/design/atlas-cover-reference.jpg`, 412,664 bytes | `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187` |
| `docs/design/atlas-reference.json` | `896b09b07b794ecb02d9b3be350b3166a22136fa920432c99dc7a73904c3dc50` |
| `baseline-ui/play.png`, 679,822 bytes | `21da0d6340b408231d2080b8ab888907bb0d4aa58c98599908a2a0cf4252213a` |
| `baseline-ui/play.json` | `0c18cecfec6366f4cd5966b34b2ccf9c9fded8c166e95e6cb026f598b014b4ea` |
| `baseline-ui/identity.json` | `6db008a72155f51e983d93ad2968a077fc3e8e0c02578afca4aa6057c7debcad` |
| Current `apps/standalone/InstrumentView.cpp` | `428f74c4b2aae72e1ee048d1fa878575d0cd2edc064b1a3865ba40c446c30da2` |
| Baseline `build/apps/standalone/hammond_standalone` | `0ef37dd5a0501da08df302027b31791b7917705e00cb32017b035a145ceb3811` |
| Complete `docs/PLAN.md` | `5a7f8ecda549cbc1e5f738c00b8dbfb88356caa424c39de4d5c10031d389bd07` |

Text/capture/build paths above are under `/workspace/scratch/e3cacb90cc81/`;
repository-relative paths are under its `Hammond-B3-Organ/` checkout.
Binary, renderer and PNG hashes were independently recomputed and match the
supplied baseline identity record; this was not a new application launch.

## Full textual coverage and selected visual coverage

Read **every line 1–4,945**, in sequential `sed -n` ranges 1–400, 401–800,
801–1200, 1201–1600, 1601–2000, 2001–2400, 2401–2800, 2801–3200,
3201–3600, 3601–4000, 4001–4400, 4401–4800 and 4801–4945.
The first range was repeated alone after a combined output was clipped;
the completed atlas reading used untruncated ranges, not keyword excerpts.
An additional marker check confirms all **84 consecutive pages 335–418**.

| Fully read pages | Subject and evidence boundary |
| --- | --- |
| 335–348 | Room/transducer ownership and Leslie measurement/acceptance; synthetic fixtures do not identify hardware. |
| 349–366 | Acquisition, calibration, provenance, independent splits, identifiability and bounded fitting claims. |
| 367–378 | Independent regression oracles, timing, adversarial gestures and actual listening-study requirements. |
| 379–390 | Audio clock, bounded communication/lifetimes, performance evidence and framework-independent engine contracts. |
| 391–408 | Host adapters, stable automation/state, standalone recovery and separately qualified release artifacts. |
| 409–418 | Original art direction, material layers, retained controls, player workflows and input/focus ownership. |

Visually inspected the exact 1672×941 reference JPEG and exact 1672×941 current
native PNG. Rendered original PDF pages **409 and 415 only** with `pdftoppm`
at maximum dimension 1500 and inspected both whole pages. Page 409 explicitly
labels generated art as atmosphere; page 415 is a control placement study,
not a browser screenshot. No all-figure or underlying external-source audit
is claimed. Temporary page images are reproducible, outside the repository.

## Calibration and physical-evidence constraints

- **One owner per effect:** early/late windows must recombine the measured IR;
  driver, propagation, cabinet, microphone and room transfers cannot be applied
  twice (pp.335–340, 357–358, 386). Keep separate horn/drum input boundaries.
- **Static is insufficient for moving behavior:** frozen-angle agreement does
  not establish time-varying filter order. Use synchronized independent rotor
  angles and preserve emission-time history (pp.345–347, 353, 371).
- **Measured claims need a named object:** specimen, revision, fitted drivers,
  load, panel state, microphone scene, clock, conditions and calibration must
  travel with actual raw-file hashes (pp.343–356). Unknown remains null.
- **Preserve identifiability:** upstream loading and electrical boundaries must
  be accepted before downstream fitting. Output-only gain products do not
  identify separate internal gains; G–G service readings are not source-wheel
  amplitudes or emulator tolerances (pp.350, 355, 361–366).
- **Freeze independent evidence:** split whole acquisition groups/takes before
  fitting, retain transformations and uncertainty, and acquire a fresh final
  set when final failures influence revisions (pp.348, 354, 359, 366, 378).
- **Acceptance outcomes stay separate:** numerical, host, physical and listening
  gates are distinct. Missing or unresolved measurement yields not-run or
  inconclusive; preference, nonsignificance and visual polish do not prove
  identity (pp.342, 347–348, 367, 372–378, 408).

## Runtime and host constraints for R4 and subsequent work

- One serialized audio context owns mutable state; each rotor has one physical
  trajectory queried by all receivers. GUI frames and additional microphones
  must never advance another clock (pp.379, 382, 385, 392).
- Zero-frame calls commit current controls once and advance no phase, envelope,
  smoothing, noise or delay history. Positive calls with disconnected outputs
  still advance declared time; half-open blocks retain end-boundary events
  (pp.370, 387, 393, 395, 400).
- Preserve absolute timing, stable tie order and full automation segments over
  partition/slicing changes. Compare control curves independently before audio;
  a final scalar target cannot certify the trajectory (pp.370, 387, 393, 400).
- Validate bounds before mutation; preallocate histories, scratch and transition
  resources. Keep allocation/free, file access, parsing, locks and GUI work out
  of processing. Retire resources only after every reader/tail finishes
  (pp.358, 379–381, 385, 388, 394).
- Queue saturation needs bounded explicit policies: never silently lose note-offs;
  telemetry loss cannot become complete-distribution evidence. An untimed UI
  coalescing rule is not permission to collapse timed musical events (p.380).
- Independent endpoint/static fractional-delay controls, retained tails,
  partition equivalence and stage traces precede rotary/audio acceptance
  (pp.336, 367, 370–372). Preserve faulty controls and first divergent samples.
- Current R4 requires two radiation-boundary inputs, bounded cubic history,
  observation at `n-2`, all-four-path atomic rendering and complete rollback;
  these are the repository's frozen contract, not newly inferred physical data.
  R5 reconstruction/alias policy and R6 Engine/host/device integration remain
  separate, as do scanner G5, M5/M6 connectivity and physical cabinet fidelity.
- Do not turn arithmetic counts, compiled headers, a smoke report or average CPU
  cost into deadlines. Timing needs exact platform/build/stimulus identities,
  transitions, maximum duration and declared unavailable counters (pp.382–390).

## Preserve the live UI contract during visual refinement

Current session scope preserves **47 parameters, state4 and readers 1–3**.
The atlas's 62-parameter proposal is historical design material, not permission
to replace the current registry (pp.397–402; current scope and plan).
Keep four independent banks, two pedal mixtures, 61+61 playing keys, 12+12
reversed presets and 25 pedals. Editing A/B is distinct from sounding selection;
Cancel preserves held ownership and bank values (pp.389, 410, 415–416).
Capture gesture identity until closure; tab/bank/resize changes cannot retarget
the drag or release another input owner's note (pp.399, 412, 417).
Outward continuous drawbar travel increases 0–8; caps, shafts and values agree.
Keep percussion positions visible while showing Upper-B eligibility separately;
do not move a stored 1-foot value to represent an audio interlock (pp.411, 418).
Preserve keyboard/focus, Flat/reduced-motion alternatives, readable editable
legends and truthful copied-state evidence; decoration cannot own audio time
(pp.411–415). Do not add art's Stop/brake or apparent rotary/mic controls to a
dry product without their separate supported model/integration contract (p.413).

## Observed practical visual gaps and bounded refinements

| Observed at 1672×941 | Practical refinement while preserving controls |
| --- | --- |
| Native panel borders are thin and regular beside the concept's deep recesses and narrow rim highlights. | Add bounded inset shading and directional edge highlights inside existing panel bounds; preserve all hit/focus geometry and contrast. |
| Native shafts read as thin grey lines; cap faces and sidewalls are simpler than the projected concept caps. | Separate recessed track, shaft, cap face and short projected edge; retain the same continuous position/value mapping and clickable footprint. |
| Full native manuals are now deep, but their front faces remain visually thinner and lighting more uniform. | Refine front-face shading and black-key bevels through shared paint/hit geometry; retain all 61 keys, visible held/focus states and preset legibility. |
| Reference heading rules, spacing and brass lighting are richer; the live tool row has denser small labels. | Refine existing text/rules and hierarchy without hiding Save/Load/Help/Audio/MIDI/Panic/Flat or replacing the nominal-dry caption. |
| Live cabinet art already matches the reference subject; lower status and 25-pedal composition differ. | Refine its frame/crop/inset relationship without removing useful device status, pedals or the explicit unconnected-rotary caption. |
| Correct native reversed presets, footages and functional tools differ from erroneous concept counts/legends. | Treat these as necessary semantic differences; never gain apparent image similarity by deleting controls or copying incorrect image text. |

The baseline diagnostics identify **SDL 2.32.10 dummy audio/video, software
rendering, MIDI OFF**, 48 kHz stereo float and 512-frame buffers. The captured
frame contains one held Upper target; its copied snapshot is current. The supplied
smoke report records observed hold/release and zero errors, but A05 did not rerun
it. Pointer-capture attempts are zero. Physical display/DPI, pointer capture,
MIDI/audio devices, DAWs, accessibility and deadlines are not established here.

Next: choose one bounded material refinement, qualify changed native pixels and
control/ownership behavior at reference and compact/Flat sizes, then retain a
source-identified actual gallery. Keep residual differences explicit; neither
this review nor the baseline establishes literal 1:1 visual equality.
