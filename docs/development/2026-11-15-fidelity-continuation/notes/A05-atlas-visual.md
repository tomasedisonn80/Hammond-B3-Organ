# A05 — Complete atlas reading, pages 337–420, and native visual direction

## Assignment and actual coverage

Worker `/root/w01_a05_atlas_visual`, wave 1 of the new fidelity continuation.
Owned output is this note only. The source checkout is
`/workspace/scratch/63071f51f1e4/Hammond-B3-Organ`, observed at commit
`878d3ce82a10a0ae335dab377683ec543f194957`, tree
`7d63b272d7dd04be65869db5687a1d7f29994e1a`. Root's initial checkpoint identifies
the same live-main baseline; A05 did not perform a separate remote query. The
new session directory was untracked at inspection and the historical session
records were preserved.

Read all of `AGENTS.md` and `docs/PLAN.md`, current README/status/next-step/log
and product-handoff entry material, the new checkpoint and actual manifest,
and the retained reference-gap review. Read **every PDF page 337–420**, in six
consecutive fourteen-page chunks: 337–350, 351–364, 365–378, 379–392, 393–406,
and 407–420. The prepared full extract contains exactly 84 contiguous page
markers, **25,955 whitespace-separated words** and **221,963 bytes**. The
word count includes headings, tables, source lines and page markers; it is not
a measure of independently verified external evidence.

Directly viewed the original 1672×941 cover/page-409 reference JPEG, the actual
1672×941 native Play PNG, and a freshly rendered complete PDF page 409. The
page render visibly confirms both the reference picture and its explicit
caption that generated art does not determine key counts or legends. Inspected
the existing wide-layout calculation in `UiModel.cpp` and the panel, drawbar
and key paint functions in `InstrumentView.cpp`. Root owns the separate X11
desktop journey; this reading note neither duplicates nor grades that work.

| Input | SHA-256 |
| --- | --- |
| Original 21,248,265-byte PDF | `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769` |
| Complete assigned text extract | `476832737151e0a09c0d1478d7fcd350f7e5609ca7a31cbbdf4518eadbbec5dd` |
| Original reference JPEG | `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187` |
| Current retained native Play PNG | `4dcb8e55dcfbc5f3e5d524bf0ea426312083f8f56e922716e6d0513fe08b9d19` |
| Inspected `UiModel.cpp` | `49c68995aad96aa5e316613412c93931a1082d0e4a3ad3758ac63484af963064` |
| Inspected `InstrumentView.cpp` | `3687f96db4490e600d6107e6b39d7b7d568bdeb183f16f6aa397535a5f688567` |

The native PNG retains its original `d556da01` capture identity from the gallery;
viewing it at this later checkout does not turn it into a new capture. The
temporary page-409 rendering is an inspection intermediate outside the repo,
not an authored or altered reference asset.

## Conclusions from every assigned chapter

| Chapter and complete page range | Findings and implementation consequences |
| --- | --- |
| **055, 337–342 — driver nonlinearities** | Documentary driver numbers and nominal 16-ohm ratings do not identify impedance, force factor, thermal constants or diaphragm motion. The proposed electrical/mechanical model derives both flux and force from one magnetic coenergy, including the inductance-derivative terms. Restoring force and tangent stiffness have distinct meanings. Coil/magnet heating has physical memory that continues through silence and presets. The chapter explicitly flags the manuscript's 0.039 copper coefficient against 0.00393/K at 20°C, without identifying the actual driver material. Preserve the floating treble load and shared amplifier/divider/driver coupling. The reported synthetic energy fixture belongs to the atlas and is not a newly executed repository or hardware result. |
| **056, 343–348 — Leslie validation** | A fidelity claim names the actual cabinet, revisions, fitted parts, electrical interface and microphone scene. Published Model 600/122A experiments do not supply the target 122 corpus. Static-angle capture, continuous motion and transitions are separate tests. Preserve calibrated voltage/current/pressure, full raw tails, angular trajectories, timing and changes introduced by isolation fixtures. Phase spikes near acoustic nulls do not establish motor acceleration. Freeze budgets after estimating measurement resolution and before holdout evaluation; unresolved uncertainty gives an inconclusive result. A favorable mean or listening nondetection cannot establish identity. |
| **057, 349–354 — physical acquisition** | Begin with identity, permissions, technician-reviewed boundaries and an external-output pilot. The historical service meter is across AO-28 G–G; range/loading and detector uncertainty prevent treating its figures as oscillator amplitudes. Qualify the entire recording chain, gain, clock, skew and clipping. Screen all routes and acquire repeated attack/release gestures, percussion histories, six scanner modes, expression/AO-28 loading and synchronized horn/drum motion. Preserve every configuration and service change. Split by physical takes/sessions, retain rejected records and explicit unknowns. This is a proposed campaign, not evidence it occurred. |
| **058, 355–360 — data/provenance** | Authoring, physical evidence, fitted profiles and compiled representations remain separate. Unknown is null with a reason, not zero or unity. Source identities are exactly 1–91 and differ from array indices/MIDI/terminals. Store waveform boundary and effect ownership, but a string registry cannot prove graph-level absence of duplicate processing. Strict parsing, actual byte/hash/header checks, units, reference resolution, partition/group inheritance and permission evidence precede off-thread compilation. The chapter's 39 metadata checks and synthetic silence WAV validate their stated fixtures only; no physical truth, complete lineage implementation or DSP result follows. |
| **059, 361–366 — fitting** | Establish which quantities observations identify; two cascaded unknown gains are ambiguous without an additional calibrated boundary. Fit upstream topology, loading and timing before downstream cabinet behavior. Declare units, covariance/nuisance policy, priors, bounds and numerical refinement; report data error separately from regularization. Shared calibration/clock errors do not vanish through repetition. Do not hide mismatch with per-note gain/time warping, phase resets or final EQ. Optimization termination is not parameter evidence or fidelity. Preserve full-take holdouts and reopen final evaluation after using failures to tune. |
| **060, 367–372 — regression** | Documentary, mathematical, engine, host and measured-fidelity tests need different oracles and status. Absolute events, stable tie order and shared state must survive callback partitioning and zero-frame flushes. Expose first-divergent-stage traces. Test continuous 91-source phase, coherent folded collisions, contact/percussion histories, Cancel without fake releases, and scanner ownership. Compare loaded crossover ports against an independent electrical reference before physical drivers. Deliberately faulty controls should prove tests can detect the relevant error. The atlas's stated documentary executions are historical; they are not this worker's new tests. |
| **061, 373–378 — listening** | Similarity, discrimination, practical equivalence and preference answer different questions. Use matched physical boundaries, independent hardware repeats, frozen levels/offset corrections, withheld take families, controlled reproduction and blinded coded assignment. Preserve attack/release and recovery rather than normalizing them away. Distinguish trained listening, performance behavior and UI usability. Predeclare margins, dependency-aware statistics, exclusions and stopping. Nonsignificance is not equivalence, and no score becomes an authenticity percentage. The chapter supplies no completed panel or trials. |
| **062, 379–384 — runtime budgets** | One serialized audio context owns time; UI, extra microphones and internal slices cannot advance extra clocks. Ban processing-time allocation/free, I/O and locks; bound queues, event density, retries, storage and recovery. Reserve retirement capacity before swapping prepared state and reclaim only after the last reader. Operation counts/SIMD packing do not establish CPU speed. Profile cold starts, long tails, queue/transition bursts and concurrent UI on named hardware with raw telemetry and explicit losses. The 0.40D/48kHz/64-frame target and thirty-minute run are proposals, not this source's measured capability. |
| **063, 385–390 — C++ architecture** | Keep one framework-independent engine behind offline, standalone and VST3 adapters. Fuse physically coupled solver regions or validate the decoupling approximation. Preserve declared units/port signs, continuous state and bounded half-open event timing. Zero-frame flush advances no time; disconnected positive-frame processing does. Parameter curves carry their previous-block anchor. Prepared generation handles, acknowledgment and non-audio reclamation govern borrowed storage. Ordinary control snapshots are not exact-render checkpoints. The atlas header's 19 static assertions did not implement DSP; the current repository's later source/evidence must be assessed separately. |
| **064, 391–396 — adapters** | Freeze actual dependencies and their licensing route; dated atlas license assertions are documentary context, not a new legal/current-version audit here. Keep stable product/bank IDs and editor-independent bus/state contracts. Preserve note ownership, explicit MIDI routing, native queue timing and sample-positioned parameter curves. Machine device setup is distinct from musical state. Correct tails, silence flags, bypass and suspension depend on the implemented model. Require separate SDK, DAW, offline and standalone-device reports; a build is not a musical or acoustic pass. |
| **065, 397–402 — compatibility** | The atlas's **62 proposed** parameters must not overwrite the repository's **47 implemented** identities. Four retained banks remain independently addressable; editing a view is not route selection. Normalize marked travel separately from physical loaded-gain law. Capture an edit gesture's original ID/bank and close it before rebinding. Keep stable enum thresholds, sample curves, zero-flush semantics and old-state migrations. Cancel changes routing without manufacturing key releases. Modern snapshots, wired presets and stopped numerical checkpoints have distinct scope. Metadata checking does not qualify host automation. |
| **066, 403–408 — release** | Explicit native lanes, minimum support envelopes, toolchain/source locks and matching engine/profile identities precede packages. Preserve whole VST3 bundles and immutable factory assets, writable user data and upgrade/rollback behavior. Sign/notarize the completed actual payload under separate platform gates; signed bytes differ from unsigned build identities. Inspect installed artifacts on clean machines and actual advertised hosts/backends, including Unicode/non-admin paths and duplicate bundles. Keep missing or failed gates visible. This atlas chapter reports no produced or qualified platform release. |
| **067, 409–414 — visual system** | Walnut/charcoal/brass/ivory define constructed depth and readable hierarchy; generated art proportions, counts and text are not engineering authority. Separate geometry, materials, semantic text and state. Drawbar cap, shaft and recessed track are separate live layers; 0 is near the upper edge and 8 extends toward the player. Use editable serif title/headings and clear interface text, explicit focus, a quiet/Flat alternative and truthful evidence labels. Editing A/B is independent from sounding route; preserve 61+61 playing keys, 12+12 momentary/selected presets and 25 pedals. Views share instrument state. Prototype parse success and blocked browser rendering are not native acceptance. |
| **068, 415–420 — player workflow** | Organize Play around preparing and selecting registrations, with explicit edited/sounding/unsaved meanings. Fixed presets retain their wiring while banks are edited. Preserve press-owner identity through focus, view, zoom, resize, glissando, outside release and editor close; UI loss must not release an independent MIDI owner. Show stored percussion controls plus route eligibility instead of overwriting their positions. Expression/trim and command/evolving rotor state are distinct. Microphone edits need deliberate scope, coordinates and non-drag alternatives once implemented. Validate real musical tasks with traces; decorative motion or usability cannot certify audio fidelity. |

## Direct visual comparison and concrete candidates

The current native image already has the right broad wood/charcoal/brass
palette, approximately matched title footprint and close cabinet-column
alignment. The largest visible material difference is the repeated thin bright
rectangular panel/well edging: the concept has broader, quieter dark metal
bevels and a more continuous recessed drawbar backing. Current keys have regular
front transitions and much narrower natural keys because the complete manuals
are present. The concept also shows different furniture and control text; those
differences cannot be solved by replacing working controls with the picture.

### Candidate 1: bounded deck and rack material refinement

After root's visible text/input check resolves any discovered usability faults,
freeze a wide-Dimensional-only treatment of the rack/deck regions. Keep exact
layout and hit quads, cap centers, 0/8 endpoints, all legend/readout bounds and
semantic state unchanged in this first candidate. Render a continuous dark
recess behind each nine-control rack, with individual shafts/walls layered
above it. Replace repeated equally bright thin outlines with a wider, asymmetric
dark bevel: restrained upper/left reflected light and deeper lower/right shadow.
Keep labels/focus painted last and outside all decorative masks.

The current `panel()` already has a bounded grain lattice of at most 2,048
point pairs and fixed gradients. Extend a declared bounded primitive sequence;
do not introduce frame-dependent noise, bitmap labels, per-paint asset loading
or a hidden texture cache without its own ownership/resource contract. A more
complex surface is acceptable only with fixed-state containment, complete text,
focus/held/pending-state checks and measured paint cost. Compact and Flat
should retain existing pixels unless a separately reviewed usability change
explicitly owns them. Do not claim a whole-frame 1:1 pass from scoped material
containment.

### Candidate 2: reviewed wide geometry, separate from the material pass

The retained comparison reports approximate reference rack span **y267–509**
at 1672×941; inspected live layout computes **y240.92–472.76**. Its 28-pixel
keyboard toolbar then consumes y482.76–510.76 before the manual panels begin.
Simply translating/enlarging the racks would collide with that live toolbar or
push the manuals farther away from the reference.

One concrete proposal is to place the five keyboard target/octave controls and
their hint in an added lower band of the performance strip for the wide/tall
layout, reclaiming the separate toolbar row between racks and manuals. Then
solve rack bounds and both manual projection/chrome regions together against
declared reference landmarks. This is a proposal requiring geometry-owner
review, not accepted coordinates or permission to delete controls. Recalculate
the reference equations rather than adding isolated offsets: panel bounds,
61-key projected hit/paint geometry, rail/preset bounds, keyboard toolbar and
cabinet/sidebar alignment are coupled.

Test both sides of the 1400-width and 820-height breakpoints, minimum/default/
reference sizes, Flat, all views and held/focused owners. The geometric oracle
must retain all 68 ordinary controls including 24 presets, 147 playing keys,
71 Play/ten common focus stops and the separate eleven MIDI-modal stops.
Changes must preserve four banks, 47 parameters, state4/readers1–3 and phase/
ownership. A parameter/state migration has no role in this visual task.

### Evidence needed before README promotion

Keep the original reference unchanged, capture the changed native app using
matched dimensions and declared state, bind images to exact source/build/
executable/replay/state/pixel identities, and independently admit the frames.
Retain before/after material and geometry findings, observed small-label
failures, timings and unresolved differences. Root's native journey can provide
actual display/backend evidence for its identified conditions; a remote
software display does not automatically establish a physical monitor, device,
assistive-technology or deadline result. The literal whole-interface 1:1 request
remains open until its own comparison is actually satisfied.

## Independent model and product consequences

The assigned chapters reinforce the next M6 numerical phase: compare the
existing ideal circuit's signed treble **VA−VH**, bass **VW−VB** and input
admittance with a separately identified numerical candidate under a frozen
reconstruction/rate/load/error contract. Numerical accuracy and physical
amplifier/driver coupling are different gates. No generic speaker saturation,
thermal coefficient, fake scanner/microphone control or animated rotary meter
should be added to make the visual/audio product seem more complete.

Retain current explicit unavailable/unconnected captions. Source-dependent
same-Hz failure, R4 ownership and later physical acquisition/DAW/device/
accessibility/release gates are not closed by this reading or by new paint.
The atlas's absent companion files and historical synthetic executions are not
newly recovered or rerun by A05.

## Verification and handoff

Executed: complete text reading and contiguous-page assertion; SHA-256/size
checks of the six listed inputs; source inspection; one PDF page render; direct
viewing of the two original image files and the rendered page; owned-note
whitespace/format inspection. No application was launched by A05, no shared
build was configured or used, no numerical/sanitizer/CI/hardware test ran, and
no commit or publication was attempted. Only this assigned note is changed.

Root subsequently reported a bounded baseline X11 observation on a 1364×1024,
96-DPI virtual display at 1280×900 and 960×700: Play/Service/MIDI/Flat,
modal Tab/Shift+Tab, drawbar Home/End, no obvious text crop, and several small
preset/helper/evidence labels. A05 inspected the report's top-level structure
and the retained numeric exit file (**0**), not its entire state history.
Root retains errors 0 and no held owners after shutdown in its own evidence.
There is no full 1672-wide display, absolute-latency or complete per-stop focus
qualification from that observation; it must not be promoted to full native
acceptance.

Next: root integrates all six full-reading findings and the bounded baseline
display observation, then assigns a frozen material/geometry candidate
and independent acceptance. M6 protocol/candidate and native MIDI close work
can proceed under separate owners. These recommendations are inputs to those
contracts, not completed implementation or acceptance claims.
