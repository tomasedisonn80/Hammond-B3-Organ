# A06 - Atlas pp. 419-500: UI, implementation and release

## Identity and exact reading coverage

- Assignment: `/root/w01_a06_atlas_release`, wave 1, fresh review on 2026-11-14; owns only this note.
- Repository: `/workspace/scratch/e3cacb90cc81/Hammond-B3-Organ`; observed HEAD and local `origin/main` ref: `2e161dc3a60fc3442051799574feed37bffbfc5c`; tree: `17f8e4d698f903c37bff09deee196ea73e0da108`.
- Preserved PDF: `Hammond_B3_Leslie_Research_Atlas_500pp.pdf`, evidence edition 2026-11-12, 21,248,265 bytes, SHA-256 `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
- Assigned text: `/workspace/scratch/e3cacb90cc81/atlas-text/part-6-419-500.txt`, 225,115 bytes, 4,846 lines, 25,408 whitespace-delimited words; SHA-256 `dcc129b68d5db57fafbb1c8fe47aa073df0d271ac260d1bd430cd6ae2b4cd0f1`.
- Fully read every word of all 82 pages, including headers, tables, captions, equations, footers and the complete eight-page source directory. This is a new textual reading, not inherited review coverage.
- Contiguous output batches: 419-424, 425-430, 431-436, 437-442, 443-448, 449-454, 455-460, 461-466, 467-472, 473-478, 479-484, 485-490, 491-496, 497-500. No assigned atlas batch was truncated or replaced with a search/summary.
- Python split the supplied text only at `===== PDF PAGE n =====` boundaries; a separate marker check confirmed exactly `list(range(419, 501))`. Recomputed PDF/text hashes matched at completion.
- Read `AGENTS.md`, current session README/checkpoint/manifest, root README, STATUS, NEXT_STEPS, complete PLAN, ATLAS_REVIEW, ERRATA, source manifest, latest development-log entry, ROTARY_PROPAGATION and the complete `rotary-numerics-v1` contract.
- Existing `AGENTS.md` edits and other workers' continuation files were preserved. No build, test suite, native UI run, external-source verification, commit or publication was performed by A06.

## Actual selected PDF visual inspection

Used the PDF skill and system `pdftoppm -f N -l N -singlefile -r 110 -png PDF PREFIX`; viewed each resulting full-page PNG. These are source-page inspections, not application captures or measurement evidence.

| Actual page viewed | Observation checked against its complete text |
| --- | --- |
| 428 | Visible conversion is `(x_author, z_author, -y_author)`, determinant `+1`; stable asset/parameter IDs and measured pivots remain separate. P002 is a context photograph, not a dimensional calibration. |
| 437 | Responsibility diagram separates bounded snapshots, semantic view model, both skins, native accessibility and commands; the prose forbids the renderer from owning audio clocks. |
| 465 | Nineteen signed tap outputs, reactive-leaf signs, corrected Gamma/Theta elimination and Hz-to-radians prewarp are legible and agree with the extraction. |
| 467 | Retarded-time equation, negative cosine cross term and endpoint-correct linear interpolation are printed exactly as extracted; no cubic kernel or physical calibration is established by this page. |
| 486 | Change-control prose and pseudocode retain required-evidence checks and actual execution before pass/fail/inconclusive decisions; release and physical claims remain separate. |

## Remaining player, service, asset and accessibility requirements

- **419-420:** Chorale/Tremolo is the requested command; horn/drum states evolve separately. Microphone selection is editing focus; geometry validation precedes publication, moving a mic preserves phase, and distance controls cannot hide level matching. Stop requires an identified accessory/extension profile. Non-drag editing and motion-disabled operation are explicit tasks.
- **420:** Musical acceptance needs held accompaniment, inactive-bank edits, bank changes during drag, Cancel during a chord, outside-window release and restore after editor close. Record traces, wrong-bank actions, missed targets and actual participant observations; usability cannot prove sound fidelity.
- **421-424:** SERVICE identifies assembly, evidence, active model/profile and unavailable observations. Inspection does not change sound or trigger excitation. Physical parts, stock numbers, model modules and revisions have separate IDs; UNKNOWN remains null plus reason. Draft edits preserve source transcription, versioned provenance, undo and activation acknowledgments.
- **423:** Overlays require matching ports/terminals, units, load, timing, calibration and analysis settings. G-G service data cannot become pickup data. Preserve raw recordings and parent hashes; residuals and uncertainty remain distinct, with non-color plot identification and numerical export.
- **425-426:** Audio publishes bounded snapshots; FFT/formatting/export stays off callback. Stale timestamps and sequence gaps must remain visible; full telemetry may drop diagnostics, never musical events. Late draft results cannot replace newer profiles. Evidence-only inspection precedes unavailable live/physical features; preserve focus and meaningful status announcements.
- **427-432:** Separate specimen geometry from artistic styling. P005/P020 cannot establish dimensions; patent embodiments are not production CAD. Use persistent semantic IDs, actual pivots, metre/radian units and a single handedness-preserving conversion. A visual camera is not an acoustic microphone.
- **429-432:** Materials are proposed appearance recipes, not inferred chemistry. Texture transfer functions/ORM channels, LOD bindings, decoded memory, context recovery and rendering budgets need actual qualification. The 100k triangles/120 draws/64 MiB/60-or-30 fps figures are proposed starting targets. Asset-format validation cannot establish fidelity or access.
- **433-434:** Build one semantic model for all 36 manual drawbars and both skins. Editing a hidden bank must not reassign IDs or set host `kIsHidden`. Numeric, pointer and assistive edits address the same retained parameter. Focus does not sound notes; explicit audition is a software aid. Close the original gesture before bank rebinding.
- **434:** Capture each UI note's original owner, ignore autorepeat, release only UI owners on deactivation/close and preserve external MIDI. Cancel/focus changes must not manufacture unrelated note-offs. The proposed 0.1/0.01 keyboard steps are input resolutions, not physical detents or a new current parameter contract.
- **435-438:** Contrast, focus visibility, target alternatives, scaling, reflow and reduced motion require observed matrices. Web WCAG/ARIA references do not establish native accessibility. Flat must remain a complete control skin; decorative motion freeze is not an audio brake. Test actual screen readers, touch assistance, host shortcuts and coordinate conversions separately.
- **436-438:** Visible, accessible and hit-test bounds share the layout transform. Resizing, skin changes, editor absence and rendering failure preserve sources, rotor clocks and note ownership. Record OS/backend/host/scale/input details; no screenshot alone proves accessibility.
- **439-444:** Atlas reports 25/28 initial and 28/28 corrected JavaScript checks under a limited DOM/event/storage double. Corrections concern Shift mid-drag jumps, motion preference consistency and roving focus. Browser execution/layout remained blocked; original diagrams are not screenshots, and the two-mic no-audio study is not a production registry export.
- **442-444:** Engine bridge needs stable IDs, explicit events, bounded commands and acknowledgments; display indices are not identities. Pointer capture, gestures, focus, browser/native layout and audio/host coupling need their own actual tests and source hashes.

## Complete M0-M9 implementation plan

The ten research waves, ten implementation milestones and this session's ten worker waves are different organizations. The source plan is pp. 445-456, reaffirmed on 481-492; `docs/PLAN.md` retains the repository's complete plan.

| Milestone | Required implementation and exit boundary |
| --- | --- |
| M0, p. 445 | Lock B-3/AO-28/122 identity, variants, hashes, units, evidence and acquisition queue. Keep nominal engineering and specimen-fidelity statuses separate; unknown is not zero/unity. |
| M1, p. 446 | Compile immutable profiles and deterministic offline render/event traces; half-open blocks, stable same-frame order, non-advancing zero-frame flush, partition/overflow/lifetime checks and callback allocation evidence. |
| M2, p. 446 | One shared continuously running 91-source bank; separate source, terminal and MIDI identities; exact routing including null contacts. Candidate frequencies and G-G readings are not measured pickup calibration. |
| M3, p. 447 | Ordered contact trajectories, four retained banks, latch/routing state, pedals, shared percussion recharge and loaded expression. Cancel preserves physical note ownership; named behavioral surrogates permit work before complete AO-28 connectivity. |
| M4, p. 447 | Reviewed 18-section/19-output scanner, six modes, explicit ground/return ports, corrected algebra and independent loaded numerical comparisons. Return is counted once; specimen validation remains separate. |
| M5, p. 448 | Complete selected AO-28 graph, loaded linear reference, operating points and nonlinear stages; preserve feedback/loading or qualify approximation. Validate dry G-G behavior before fitting cabinet responses. |
| M6, p. 448 | Separate 122/147 amplifier/crossover/driver models; retain floating treble `VA-VH` and bass `VW-VB`, complex loads, polarity and independent AC/nonlinear tests. Resistive fixtures are not real driver evidence. |
| M7, p. 449 | Independent horn/drum histories, one trajectory per rotor shared across receivers, distinct emission times, causal moving-path rendering and explicit propagation/directivity/cabinet/room ownership. Nominal math is not physical M7. |
| M8, p. 449 | Immutable calibrated captures, upstream-first fitting, whole-group held-out conditions and preregistered uncertainty-aware decisions. Insufficient resolving power is inconclusive; listening supplements boundary measurements. |
| M9, p. 450 | Shared-engine VST3/standalone adapters, real IDs/automation/state, accessible dimensional/flat UI, lifecycle/deadline tests, native host/device qualification and reproducible rights-cleared packages. Every advertised capability needs its own report. |

M1/M2 allow early adapter smoke tests; M3 and M4 can proceed in parallel after routing/ports freeze. M6 documentary and M7 provisional work can proceed while acquisitions continue. Complete dry-organ validation still precedes integrated cabinet fitting (pp. 447-450, 454, 492).

## Errata, contracts and interpretation hazards

- **451-456, 489:** Prepare/resolve/allocate off callback; active DSP has one mutable owner. Preserve all borrowed storage through retirement acknowledgment. Schema success cannot prove physical meaning, acquisition or permission; unknown required fields reject that algorithm or select an explicitly separate surrogate.
- **458, 463, 466, 488:** AO-28 source is upper Figure 24, printed 3-50/source PDF 129. The 124 placement/section records and 85 stock rows are not a netlist or installed count. Retain C59/T7 and exclusive P-D/no-code alternatives; R62, expression law and transformer evidence remain unresolved.
- **462, 464, 491:** Keep already resolved corrections closed: seven double-fold sites; all 91 historical G-G readings independently transcribed in the atlas; 020305 driver versus 020313 spacer. Their measured interpretation/installed applicability remains open. Current repository factory evidence has its own later provenance.
- **465:** Scanner has 18 LC sections/19 ground-relative outputs, 50 passive records, a distinct nine-terminal depth map and 16 scan positions. `Gamma=S21*solve(I-Phi*S11,Phi*S12)+S22`; correct source/open/short and reactive memory signs; `2/K=24.8133 us` for the stated 44.1 kHz/7075 Hz case. These are atlas derivations, not author-issued errata verified here.
- **466-467:** Five-to-eight seconds is a specific bass deceleration adjustment, not universal tau. Choose ramp direction from target minus current speed. Retarded timing uses `t=e+|m-q(e)|/c`; linear interpolation selects both correct endpoints; circular squared distance has `-2*R*a*cos(theta)`.
- **467:** Frozen-angle agreement cannot prove moving convolution order: `w[n-l]` and `w[n]` are different operators. Preserve fixed cabinet geometry and source/mic incidence signs; Leslie 600 horn research does not calibrate a 122. Driver variable-inductance energy requires both stated terms; coil calibration remains absent.
- **461 versus 439-444/482/491:** Earlier “072 pending” wording is stale; later source pages retain 28 scoped passes. This agrees with repository ERRATA E04 and does not establish an executable companion or current repository pass.
- **468, 481-486:** Prior-block automation anchors and zero-frame semantics remain contractual. Preserve old reports when inputs change and repeat only affected gates; failed/blocked/not_run/inconclusive remain distinct. No retroactive threshold or shape-compatible surrogate inherits a physical pass.

## Source directory and absent original companions

All directory text on pp. 493-500 was read. It is a navigation/index layer; full access status, exact external locators, claim support and rights are assigned to the absent original source catalog. No external source was independently opened in this task.

| Pages | Directory coverage and implication |
| --- | --- |
| 493-494 | Original/alternate Hammond and Leslie manuals, patents, source photographs, modern-model manuals, source/filter and synthesis work. Mirrors are not independent evidence; modern/retouched material retains its variant/use limits; US2828659A remains labeled unresolved. |
| 495-496 | Scanner/WDF/MNA, tube and nonlinear references; Leslie electrical/acoustic/motion studies; Lagrange, STK and JUCE delay references. Citation presence supplies neither original code nor executed numerical qualification. |
| 497-498 | Time-varying convolution, driver/thermal, metrology, acquisition, schema/fitting, listening, real-time/host APIs and dependency licenses. These support distinct methods and contracts, not a single acoustic or product pass. |
| 499-500 | Platform packaging/signing, graphics/glTF, accessibility, browser procedures, photograph provenance, CC/font terms, uncertainty, JSON and processor lifecycle references. Native access, rights and distribution remain separately reviewable gates. |

Checked exact paths and searched the repository inventory: original `AGENT_MISSION.txt`, `TECHNICAL_AUDIT.md`, `risk_register.json`, `INTEGRATION_REVIEW.md`, `acceptance_matrix.json`, `source_catalog.json` and `drawing_locator.html` are absent.
Also absent: `interface_prototype.html`, both `verify_interface_*.mjs` companions, `INTERFACE_VERIFICATION.md`, original `data/parameter_registry.json`, `data/ao28-component-values.json`, `data/photo_capture_checklist.json`, and original `reference_code/engine_contract.hpp`, `ENGINE_CONTRACT.md`, `DATA_CONTRACTS.md`, `retarded_path_reference.py`, `rotor_state_reference.py`.
Repository replacements have separate names/provenance; the source manifest already records baseline companion absence. The atlas's 62 proposed parameters, 19 static assertions, 39 schema outcomes, 28 UI checks and 88 unacquired photo task families cannot replace current 47-parameter contracts or local execution (pp. 452, 474, 482, 491).

## Concrete continuation: independent R4 and separately verified native refinement

- Preserve `nominal-effective-mouth-rotary-v1`, frozen `rotary-numerics-v1`, qualified R2/R3 and the current dry Engine. Do not add parameters, change `B3CONTROLS4`/readers 1-3, connect cabinet audio or clear scanner G5 in this slice.
- R4 owns streaming motion retention plus separate double waveform histories. Prepare scratch/rollback off callback; reserve `ceil(Fs*rmax/c)+2+4` within the 16,384-frame cap. Immutable 4,097-segment R3 views alone are not an arbitrary-duration event queue.
- Write input `n`, observe at `n-2`, solve all four paths and read cubic nodes `k-1,k,k+1,k+2`. Negative waveform history is zero; future support must exist. Apply `reference_distance/r`; sum signed Horn then Drum without hidden clipping, normalization, panning or pitch processing.
- Admit finite input, aliasing, timeline, event and buffer bounds before mutation. Failure anywhere preserves histories, object, diagnostics and caller audio with zero events consumed. Preserve ties/offset-N/zero-frame order, silent advancement, reset, stopped rate replacement and complete tail flush.
- Execute independent polynomial/endpoint/ring-support tests, full static delay grid and at least ten seconds of same-cubic parity at every supported rate. Keep frozen normalized `2e-5` budget, bit-identical partition results for 1/7/64/257/4096 and irregular blocks, receiver/input symmetries, nonzero-history rejection and every stopped rate pair.
- Report high-band static characterization, failures and worst coordinates. R4 parity closes only its discrete operator; R5 needs separately frozen audible filtering/reconstruction/alias evidence, R6 needs runtime/integration evidence, and physical M7 needs acquired identified captures (pp. 449, 467, 483).
- Native refinement must preserve semantic IDs, note owners, paint/hit/focus geometry and Flat operation. Compare actual changed-app frames with the retained cover/page-409 reference, retain exact source/executable/pixel identities and residual differences, then let root refresh README. Source diagrams and the five PDF checks above are not native screenshots.

## Acceptance, release and publication constraints

- **469-474, 490:** Acquisition closes a named claim only with identity, coverage, uncertainty, permissions and review. Preserve masters/derivatives, original state/restored condition, physical clock and whole-group ancestry. All source photo tasks remain unacquired; image volume is not circuit or acoustic evidence.
- **475-480:** Engineering authority and reuse rights are independent. Retain each image's creator, exact terms, alterations, original/distributed hashes and intended use. Build the release manifest from staged deliverables; repeat integrity/exclusion checks after final assembly. Historical audit scope does not qualify a later package.
- **456, 478:** Licensing observations are dated atlas claims. Recheck selected dependency revisions, notices, fonts/assets, intended distribution, branding and acquired-corpus rights. SDK permissions do not cover frameworks or photographs; this task performs no legal clearance or signing.
- **481-486, 492:** Every result names code/profile/data identities, setup, criterion, actual outcome, reviewer and limits. Native validator, real DAWs/devices, deadlines, pointer/DPI/accessibility, save/reopen, tails, bypass, installers and platform signing remain separate release gates.
- Current source is a nominal engineering instrument; literal 1:1 reference equality and specimen sonic fidelity remain open. Neither completed readings/workers nor existing numerical/library checks close those gates.
- Root owns shared README/status/next-steps/log, coherent-source acceptance and publication. Preserve concurrent work and historical failures, inspect remote advances, commit accepted work in reviewable chunks, push without force using a fresh expected head, then observe the actual remote SHA and hosted outcomes.
- Future agents retain this same complete-plan, bounded-ownership, exact-evidence, actual-screenshot and verified-publication workflow. A06 delivers this source review only; implementation, tests and publication are next owners' work.
