# A03 - Complete atlas reading: scanner and organ electronics

## Assignment and evidence identity

- Actual assignment: `/root/w01_a03_atlas_scanner`, wave 1, assignment 03 of this session.
- Read-only implementation baseline: `b79086f6bb0c42b97130c721c5c73c7c97a13887`.
- Owned deliverable: this report only. No production code, shared status, Git refs or prior-session records were changed.
- Source: [unchanged 500-page atlas](../../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf), 21,248,265 bytes, evidence edition 12 November 2026.
- PDF SHA-256: `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
- **Complete inclusive text coverage: PDF pages 169-252, 84 pages**, covering chapters 027-040. PDF page numbers match the printed atlas pages.
- Actual visual inspection: pages **171, 177, 182, 200, 212 and 250**, rendered from the PDF at 110 dpi. This is selected diagram inspection, not a claim that every figure or underlying external source was independently checked.

The complete range was extracted with Poppler `pdftotext` 25.03.0 using `-f 169 -l 252 -layout`. All 84 nonempty page fragments were read, in six consecutive 14-page groups: 169-182, 183-196, 197-210, 211-224, 225-238 and 239-252. The extracted file contains 221,100 characters and has SHA-256 `0720101fdcc379c1ac0b2748d0a40127ca531d9528d00ebe59c092370a508d14`. Rendering used `pdftoppm` 26.05.0. Python 3.12.14 split and counted the pages. Extracted text and page images are disposable scratch intermediates; the unchanged PDF and this report are the retained evidence.

`AGENTS.md`, the current atlas review and scanner handoff, and the latest development-log entry were read. Current README/status/next-step/plan context is consistent with a nominal dry organ, a separately owned scanner research track and the proposed next M3 fixed-registration slice. A03 does not re-count any earlier atlas reader as a worker in this session.

## Coverage and findings by chapter

| Chapter and pages | Findings retained from the full reading |
| --- | --- |
| 027, pp. 169-174: vibrato/chorus switching | Swell selects upper sustained material; Great selects lower sustained plus shaped pedals. Percussion is a separate downstream contribution. There are six historical selector modes and two routing tablets, rather than a seventh selector OFF mode. V/C at a given depth share the nine-node map; chorus changes the return topology. Ground-referenced chorus includes its return contribution exactly once. Selection must preserve shared rotor phase and electrical energy. |
| 028, pp. 175-180: WDF realization | Eighteen LC sections provide nineteen observable voltages. Connectivity and loading must survive reduction. The atlas flags source-equation, leaf-sign, root-elimination and prewarp-unit inconsistencies. Derive physical port constraints independently; prepare topologies outside processing. Algebra fixtures are narrower evidence than a complete circuit or specimen comparison. |
| 029, pp. 181-186: state-space alternative | A descriptor graph must retain endpoint orientation, units and physical reconstruction. Nineteen outputs do not imply nineteen energy states. Algebraic constraints need appropriate reduction; blindly inverting a singular descriptor matrix is invalid. Topology and rate changes preserve compatible capacitor voltages, inductor currents and scanner angle. Numerical residual, passivity, transient and measured-response gates remain distinct. |
| 030, pp. 187-192: scanner calibration | Module-level and complete-organ measurements have different boundaries. Six-mode routing, stationary tap response, complex sidebands, quiet residue and switching captures are separate experiments. A single shared angular reference is required. Fitting follows routing and numerical qualification, with complete held-out conditions and explicit uncertainty. The chapter supplies no physical capture pass. |
| 031, pp. 193-198: AO-28 topology | The documentary roster is V1-V8; V3 is a two-section 12BH7, not an extra undocumented output valve. The A, B and H entries, line/scanner loop, V4 expression region and T3 output remain distinct. The roster and dependency graph are not complete connectivity or measured operating points. A connected linear reference precedes nonlinear/aging work. |
| 032, pp. 199-204: linear network/transformer | Source impedance, selected circuit variant, operating point, expression setting and receiving load determine the reference. T3 cannot receive invented turns ratios or inductances. Its split-secondary polarity and both leg voltages matter. A circuit-reference pass and a measured-instrument pass are different gates. |
| 033, pp. 205-210: nonlinear valves/solver | Device families are modeling priors, not fitted specimen parameters. Terminal currents, units, validity domains and derivatives need explicit contracts. A 6AU6 includes a screen port. Trial iterations cannot partially commit reactive history; iteration and fallback work are bounded. Solver convergence does not prove alias suppression or physical accuracy. |
| 034, pp. 211-216: shared interactions/headroom | Headroom belongs to a declared calibrated excitation, routing, control and load condition. Shared nonlinear processing follows actual connection points; per-note saturation loses cross-products. Bias, feedback and charge histories remain connected. Generic sag, extra distortion and unexplained gain correction are not justified by valve names. |
| 035, pp. 217-222: supply/hum/noise | Supply rails consume the connected stage currents. Mains-related mechanisms need a shared phase reference and separate injection paths. Noise sources have physical units, stable identities and persistent random/filter state. Unknown noise amplitudes remain unknown; decorative ripple cannot duplicate modeled supply ripple. |
| 036, pp. 223-228: condition/profiles | Identity, installed configuration, dated condition and service events are separate records. Calendar age does not define component drift. Registration and specimen profile remain separate; registrations refer to a profile identity rather than copying its component values. Immutable profile publication preserves phase and uses an explicit state-transfer policy. |
| 037, pp. 229-234: numerical anti-aliasing | Event/contact modulation, source generation, nonlinear solving and decimation need separate budgets. A fixed oversampling factor is not an alias-free claim. Quality changes retain registration and physical parameters. Rate/block changes must not lose events or restart phases. The cited cubic and ADAA examples are limited mathematical checks. |
| 038, pp. 235-240: provenance/netlists | Inventory rows, stock numbers, schematic instances and physical packages are different counts/domains. The 85 inventory records and 124 placement/section records do not provide complete connectivity. Active unresolved units or values block numerical export. C59 versus duplicate C56 and alternate no-code-letter branches retain their source conflicts and revision scope. |
| 039, pp. 241-246: hybrid choices | Every runtime block declares physical boundary, ownership, supported domain, persistent state and replacement criterion. A one-direction audio cascade can discard loading. Measured responses cannot be counted again downstream. Complete direct-organ validation precedes fitting the separately qualified Leslie chain. |
| 040, pp. 247-252: organ validation | Documentary, numerical, specimen and musical evidence are separate. Shared tone identities remain coherent through collisions and foldback. Percussion needs routed contact and continuous recharge histories. The atlas explicitly calls for B/other/B while held, but requires a physical oracle before claiming its hardware transition. Absolute event timing must survive block partitions; dry-organ evidence is retained after future cabinet integration. |

## Diagram observations

The rendered page-171 graph confirms that local tap and common-return voltages contribute to one ground-referenced scanner output. Its explanatory arrows do not supply a replacement factory netlist. Page 177 shows upward/root/downward processing followed by memory commitment; the root closes the electrical source/switch constraint, not mechanical rotation. Page 182 contains a historical patent plate expressly labeled as an invention embodiment, not a verified production drawing.

Pages 200 and 212 show connected source/load, expression, feedback and shared-supply dependencies. These are functional model diagrams, so their boxes must not be converted into independent unloaded filters or new fabricated coupling strengths. Page 250 distinguishes the stationary-circuit oracle from the moving-scanner/physical-output comparison. None of these visuals establishes the missing AO-28 operating points, transformer parameters or physical fixed-preset transition.

## Constraints on this fixed-registration phase

1. **Keep signal ownership intact.** Fixed selections alter a sustained manual registration, not the location of percussion or the lower/pedal association. Percussion stays outside the scanner path when that path is eventually integrated (pp. 169, 173-174, 194, 250). No new scanner, tube saturation, aging or cabinet effect is justified by selecting a preset.
2. **Preserve continuously evolving history.** A selection is a control event. It cannot re-prepare the Engine, restart a source, clear a physical contact, reset the percussion readiness surrogate, or synthesize elapsed recovery time. The atlas repeatedly requires continuing phase and state through controls (pp. 172, 184, 198, 226, 234, 248-252).
3. **Keep documentary taps distinct from loaded gains.** The admitted chapel rows can select the existing nominal registration path. Their use does not establish a measured transformer loading network, physical latch transition or calibrated gain. This chapter range gives no new gain constants that justify modifying the current profile.
4. **Keep ordinary controls separate from runtime state.** Persist selection and retained banks under the agreed migration contract; do not serialize tone phase, contact trajectories, readiness, DSP clocks or unrelated device configuration as musical controls. Preserve the specimen/profile identity distinction on p. 226.
5. **Keep the existing numerical scope.** The next M3 selector can proceed while the scanner and connected AO-28 remain independent unfinished tracks. The [scanner handoff](../../SCANNER_HANDOFF.md) retains the same-hertz failure; the selector is not evidence for closing it or adding that model to the dry Engine.
6. **Label held-key switching honestly.** Page 249 specifically says that switching preset/percussion controls under held keys needs an acquired physical oracle. Preserve the existing nominal readiness policy and test it deterministically, while retaining physical transition qualification as pending.

## Current source review and implementation hazards

The following observations identify the inspected baseline; they are not new executed runtime tests.

- [`PercussionState`](../../../include/hammond/Percussion.h) owns one readiness value. `prepare` initializes it to one; setting controls does not. `advance_frame` uses current readiness for rendering first, then decays with an eligible detector or recovers with an open/ineligible detector. The comments explicitly mark held-key routing recovery as nominal pending captures.
- [`Engine::process`](../../../src/Engine.cpp) validates the entire request before any event is applied, dispatches same-offset events in input order, and rebuilds coefficients once before rendering that sample. Zero-frame events change controls without advancing source phase, contacts, readiness or the frame clock. Disconnected output still advances these histories.
- **Two eligibility sites must change together:** `rebuild_coefficients()` and `percussion_diagnostics()` currently use enabled percussion, an enabled upper route and retained bank B. If fixed selection leaves retained bank B intact, both sites need to recognize that the sounding route is fixed and therefore ineligible. Otherwise rendering or copied diagnostics could incorrectly report active percussion.
- **Returning to the already retained bank must leave fixed mode.** The current `SelectBank` event checks only whether the retained bank differs or the route is disabled. If B was retained when a fixed registration was selected, choosing B again must not be swallowed by that old no-op guard. Explicit selection semantics should distinguish retained editing state from the sounding route.
- [`ControlState`](../../../include/hammond/ControlState.h) retains four bank arrays; editing does not select or reconnect. Preserve that behavior while fixed sound is active. Queries must distinguish retained drawbar values from active fixed values; `active_drawbar_position` currently returns the selected bank or zero when canceled.
- `restore_controls` currently installs a validated control snapshot and marks coefficients dirty without replacing DSP state. New selector fields should preserve that transactional boundary, including every invalid-selector case.

Inspected production SHA-256 identities:

| File | SHA-256 |
| --- | --- |
| `include/hammond/Percussion.h` | `5eb87fdd2342410b63f7e6ec55ac11c645d2b7185287fb49ff8e5e53095a2722` |
| `src/Percussion.cpp` | `823685b879fad12492f86bbf5e78294668ee9b0567c58c26ac0b44aa28b1390a` |
| `src/Engine.cpp` | `e082d07323c506f58c726c76a8459bbbec9b01fcb7b20ca6d6323c065fa6664c` |
| `include/hammond/ControlState.h` | `2fb1b7b7fc39363f7e53eb81e2edf3ddb88944b4aa20969b92a90f5c584b2edb` |
| `src/ControlState.cpp` | `d297545788fa62b0167fc0a9c07081b1f8af79bd1252ceb66d0d1326dd214e58` |

## Recommended falsifiable selector checks

| Fixture | Required software observation |
| --- | --- |
| Every upper/lower fixed row against an independently initialized equivalent bank | Same sustained output at matched source phases and controls. Disable percussion or use an ineligible bank-A oracle for upper comparisons; copying a fixed row into upper B with percussion enabled is deliberately a different route. |
| Held chord, B -> fixed -> B | All note/contact owners and source phases continue. Fixed mode has no upper-B percussion gain, sustain compensation or 1-foot mask. Returning B restores eligibility without initializing readiness. |
| Partial decay followed by a fixed interval | Readiness recovers by the existing open-detector law for actual rendered frames, then resumes its eligible behavior on B. Compare against an independent analytic/replayed-history oracle, not a freshly prepared state. |
| B -> fixed -> B at one offset, or zero-frame controls | Deterministic supplied ordering; no artificial elapsed decay/recovery and no phase/contact clock movement. The final route determines the next sample. |
| Re-select B while B is still the retained bank | The fixed route exits despite the retained bank already being B. Test both enabled and canceled routes. |
| Edit any of four A/B banks during fixed playback | Stored bank values change without altering the active fixed registration, selecting a bank or reconnecting a canceled route. Returning to that bank exposes its retained edits. |
| Cancel and re-selection during held notes | Only the specified manual route disconnects; upper/lower keys, pedals, expression, fixed identity and unrelated manual ownership follow the agreed contract. Cancel must not become Panic. |
| Invalid selector after a valid event in one process call | Whole-call preflight rejects before mutation; output, clocks, owners, contact/readiness history and future audio match an untouched control engine. |
| Old state versions and new-state restore | Old states migrate to their original A/B behavior; new selected fixed controls round-trip exactly. Restoring ordinary controls leaves transient histories unchanged. Malformed state preserves the destination and future behavior. |
| One absolute timeline over several partitions and supported rates | Fixed-rate partitions retain exact event samples and the declared floating-point budget. Atlas pp. 249/252 suggest release gaps and blocks including 1, 17, 64, 127, 512 and 1024; those are diagnostic choices, not manufacturer constants. |

The maintained `test_controls.cpp`, `test_console_engine.cpp`, `test_percussion_controls.cpp`, `test_percussion.cpp` and `test_control_io.cpp` already provide related state, history and failure-continuation patterns. New acceptance must use coherent source and genuinely exercise fixed selection; passing unchanged tests alone is insufficient. No build, sound comparison or acceptance suite was executed by A03 because this assignment owns source review only.

## Handoff

The dependency-ready deliverable is a typed exclusive fixed-registration route integrated into retained musical controls, Engine routing, append-only automation and the native UI under an explicit migration contract. Preserve all old identifiers and legacy dry behavior when no fixed registration is selected. Use the separately reviewed catalog for row values and source status; this range does not re-transcribe that catalog.

Numerical selector acceptance can close its declared engineering slice. Physical preset latching/loading, held-key switching measurements, connected AO-28/scanner qualification and specimen sonic fidelity remain separate gates. Page 249 is the explicit source for retaining the held-key physical uncertainty rather than manufacturing an audible pass criterion.
