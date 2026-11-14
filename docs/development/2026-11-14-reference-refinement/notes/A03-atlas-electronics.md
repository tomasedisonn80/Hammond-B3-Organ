# A03 — complete atlas reading, pages 169–252

## Assignment and evidence identity

- Actual worker: `/root/w01_a03_atlas_electronics`.
- Session: `2026-11-14-reference-refinement`, wave 1, assignment A03.
- Inspected checkout HEAD: `8bd999efc13e309b932e6ac41d72ceb7b9b80a5f`.
- Canonical PDF: `Hammond_B3_Leslie_Research_Atlas_500pp.pdf`, SHA-256 `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
- Assigned extracted-text file: `part3-169-252.txt`, SHA-256 `351ad8d4cc158d8934f844dc12ba7cfd5d62c7b5b86e4f6caa6ae3c16cc5eb65`.
- Ownership: this note only. No production source, shared status, parameter, state or historical evidence was changed.

I read **every extracted-text page from 169 through 252 inclusive**, using seven complete 12-page outputs (169–180, 181–192, 193–204, 205–216, 217–228, 229–240 and 241–252). Each output completed without truncation. This was not a keyword-only review. I additionally rendered and visually inspected original PDF pages 171 and 194 at 1300 pixels on the long edge. The rest of this assignment has full text coverage, not a claim of visual inspection of every page.

## Complete coverage and substantive findings

| PDF pages | Chapter | Implementation consequences |
|---|---|---|
| 169–174 | 027, switching matrix | Swell routes upper sustain; Great routes lower sustain **and pedals**. Percussion joins after the scanner. The six selector modes have no Off position; bypass belongs to the two tablets. V/C pairs share a nine-terminal depth map. Preserve one scanner phase and one wet-channel electrical history. Absolute chorus tap voltages already contain the floating return; adding another dry contribution duplicates it. |
| 175–180 | 028, WDF implementation | The selected network has 18 LC sections and 19 output voltages. Coupled source/switch algebra must be independently derived; the atlas records several published sign/algebra inconsistencies. Prepare root factorizations off-thread and preserve physical states across changed port resistance. Warp-matched and same-hertz comparisons answer different questions. |
| 181–186 | 029, state-space alternative | Preserve an auditable graph, explicit branch incidence and up to 36 energy coordinates. Do not invert the singular descriptor energy matrix or treat algebraic constraint modes as resonances. Stamp the early divider before each relevant inductor. Whole-network trapezoidal integration, state migration and loaded reference validation are separate requirements. |
| 187–192 | 030, scanner calibration | Separate module-level electrical observations from complete organ-output captures; retain calibration, source/load, rotor phase and routing. Fit stationary transfer before overlap/rotor parameters. Full-cycle sidebands are spaced by the rotor frequency; plate-passage structure is not the rotor fundamental. No physical scanner captures were acquired by the atlas. |
| 193–198 | 031, AO-28 topology | Exactly eight sockets V1–V8 belong to the selected drawing. V3A drives the scanner line and V3B drives T3; do not invent an extra output valve from inconsistent prose. A/B/H entries, expression, common stages, loading and feedback must remain connected. The supplied registry is not a complete netlist. |
| 199–204 | 032, linear network/transformer | Establish a revision-specific loaded DC/AC reference before distortion. Preserve both T3 output legs, return, source/load impedances and polarity. Unknown ratio, magnetizing/leakage inductance and capacitance remain unknown. Different receiving loads are needed to distinguish transformer parameters. |
| 205–210 | 033, nonlinear devices | Manufacturer curves are priors, not an AO-28 operating point. Retain separate triode/pentode schemas, screen/grid currents, voltage domains and derivatives. Bound Newton work, preserve reactive history during trials, commit only accepted states and count degraded fallbacks. No device fitting or completed nonlinear AO-28 is supplied. |
| 211–216 | 034, interactions/headroom | Headroom belongs to a calibrated route, registration, expression position and receiving load. Shared nonlinear stages must act after actual summation; independent per-note saturation loses cross-products. Preserve shared bias/supply and feedback. Do not add generic sag or magnetic effects without identifiable evidence. |
| 217–222 | 035, supply/noise | Supply rails consume connected currents and own their capacitor states. A common mains reference underlies coherent hum paths; do not add a second ripple signal to an already coupled supply model. Noise amplitudes require physical spectral-density/bandwidth units and rate-aware variance. Quiet captures and capture-chain contamination remain separate. |
| 223–228 | 036, aging/profiles | Identity, inspected configuration, dated condition and service events are distinct. Calendar age does not establish physical drift. A captured transfer already includes its upstream condition; adding it again duplicates the effect. Preserve immutable before/after evidence, model boundaries and fixed-profile reproducibility. |
| 229–234 | 037, anti-aliasing | Assign separate alias/error ownership to sources, contacts, nonlinear groups and decimation. Connected feedback groups share one internal clock. First-order ADAA changes even the identity transfer to a two-sample average; it is not a generic transparent replacement inside a coupled circuit. A fixed oversampling factor is not an error bound. |
| 235–240 | 038, provenance/netlists | Stock rows, schematic instances and physical packages are different namespaces/counts. The stated 85 stock records and 124 placements do not establish connectivity. Resolve units before numerical export. Preserve alternatives, nulls and conflicts: factory C59 versus redraw C56, duplicated 6-6-43, ambiguous item 47 and the no-code AO-28 branch. Source conflicts should remain visible in Service. |
| 241–246 | 039, hybrid boundaries | Each numerical/measured block needs ports, load, units, validity region, state and effect ownership. A measured voltage output alone cannot supply arbitrary input-current behavior. Learned residuals require real captures and held-out evidence. Complete the direct organ path before adding the separately qualified cabinet chain. |
| 247–252 | 040, dry-organ validation | The atlas's physical “dry organ” includes scanner vibrato/chorus before Leslie; the current repository's nominal dry engine has a narrower disclosed scope. Preserve coherent source reuse, contact/percussion histories, all scanner routes and expression/load behavior. Documentary, numerical, physical and musical gates have separate results. Retain the direct-organ diagnostic output after future cabinet integration. |

The original page-171 diagram confirms that absolute voltage reconstruction combines local tap voltages and return before scanner output. Page 194 contains a tube photograph below prose referring to a graph; it does **not** supply a detailed component connectivity graph. Neither image can fill the missing AO-28 netlist or measured parameters.

## Current code and dependency check

I inspected `AGENTS.md`, the current sections of `docs/STATUS.md` and `docs/NEXT_STEPS.md`, `docs/PLAN.md`, `docs/SCANNER_HANDOFF.md`, `docs/SCANNER_NUMERICAL_CONTRACT.md`, `docs/SCANNER_AC_PARITY.md`, `docs/ROTARY_SCOPE.md`, `include/hammond/Engine.h`, `include/hammond/ScannerLine.h`, `include/hammond/ScannerRotor.h`, `include/hammond/RotaryMotion.h` and the complete `apps/standalone/InspectionModel.cpp` plus its header.

The source matches the documented separation:

- `ScannerLine` is an independently identified 18-section/19-tap/36-coordinate nominal research module with physical checkpoints, continuing rate reconfiguration, bounded frame processing and explicit numerical admission bounds.
- `ScannerRotor` has exactly six modes, one continuing phase, complementary signed weighting and no extra dry term. Its header explicitly excludes Engine routes, controls, load and resampling.
- The retained G5 report says the same-hertz budget failed at every investigated rate. At 1,536,000 Hz it still failed 95 vibrato tap comparisons across twelve bins and eighteen chorus comparisons across four bins. These are **existing report observations**, not fresh executions in A03. A larger multiplier alone is not an accepted fix.
- `Engine.h` explicitly disclaims an integrated scanner, AO-28 or cabinet model. Its shared sources, controls and diagnostic semantics are compatibility boundaries for this UI session.
- `RotaryMotion` supplies bounded, separately owned kinematics and continuous trajectory semantics; its API does not itself establish a complete electrical cabinet/acoustic renderer.
- `InspectionModel.cpp` truthfully labels scanner and AO-28 as not connected, Leslie cabinet audio as not connected, unknown rotor speeds as unavailable and specimen measurements as not acquired. Artwork is identified as decorative. Preserve these distinctions through visual refinement.

## Concrete next work

**Recommended slice for this session: M9 measured visual refinement and truthful inspection.** Its inputs are already present: preserved cover/page-409 art, current live geometry, copied-state inspection and native replay acceptance. Refine manual depth/material/panel geometry against measured reference landmarks while preserving live controls and all existing state/parameter identities. Correct singular held-target wording at the formatting boundary and retain an actual pending-state capture. Acceptance must use genuine native screenshots, layout/hit/focus consistency, owner release and exact audio/state continuity; aesthetic resemblance cannot close any model gate.

**Separate dependency-ready model experiment:** preserve the current scanner and G5 failure, then evaluate an explicitly named alternative numerical realization with unchanged graph, SI parameters, all 282 frequency bins, both return states and all nineteen signed taps. Retain declared input reconstruction, all failures, conditioning and independent AC/transient references. Only after same-hertz, transient and rotating-output/filter budgets pass should a new explicit integration contract be considered. Altering damping, dropping bins or loosening the existing budget is not an in-place repair.

**Blocked physical-model work:** full AO-28/Leslie fidelity still requires identified revisions, independently reviewed connected schematic instances, transformer/load/device evidence, calibrated source/receiving boundaries and acquired held-out captures. Structural tooling or nominal experiments can continue under a distinct identity; this review neither invents those inputs nor authorizes claiming them measured.

## Executed verification and limits

- Full assigned text was displayed in seven untruncated tool reads.
- `pdftoppm` rendered pages 171 and 194 successfully; both images were actually viewed.
- SHA-256 identities and `git rev-parse HEAD` were observed.
- Read-only source inspection was performed; **no build, DSP test, desktop test or hardware measurement was executed by A03**.
- Temporary page renders remain outside the repository. This note is the only deliverable owned by the assignment.
