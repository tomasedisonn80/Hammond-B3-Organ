# Assignment 05: acquisition, runtime and product atlas review

## Identity, coverage and actual observations

- Session: `2026-11-13-scanner`, wave 1, assignment 05.
- Actual worker: `/root/w01_a05_atlas_product`.
- Starting commit: `6dc0702d5473912268e8af8f852b9b9984198ef3`.
- Starting tree: `a4f1d4b300de236436e22b748b1d4c46ed501ceb`.
- Owned change: this note only. No engine, tests, source data, shared status, historical ledger or publication changes.
- Fresh reading: **every PDF page 337-420 inclusive**, 84 pages, chapters 055-068. Seven consecutive twelve-page text reads completed without truncating the PDF content.
- Actual visual inspection: rendered pages **357, 381, 409 and 415** at a maximum dimension of 1,600 pixels. The remaining pages were read as extracted text; this is not a claim of inspecting every figure or verifying every underlying external source.
- Canonical source: [Hammond_B3_Leslie_Research_Atlas_500pp.pdf](../../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf), 500 pages, 21,248,265 bytes, evidence edition 12 November 2026.
- Freshly observed SHA-256: `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.

All page references below are one-based pages of that unchanged PDF. Descriptions of external papers, SDKs, standards and licenses report what this atlas says; this assignment did not independently retrieve or establish their present status. The atlas's referenced companion files are not treated as recovered files or executed repository tests.

## Complete assigned chapter coverage

| Chapter and pages | Read subject | Consequence for the project |
| --- | --- | --- |
| 055, pp. 337-342 | Speaker nonlinearities and identification | Driver electrical, mechanical, acoustic and thermal states need consistent units, power accounting and specimen evidence. A nominal impedance label is not a measured driver model. |
| 056, pp. 343-348 | Leslie measurement validation | Name the actual cabinet and scene; separate stationary transfer from moving-system evidence; freeze uncertainty-aware acceptance before final tests. |
| 057, pp. 349-354 | Physical acquisition campaign | Preserve identity, permissions, chain loading, timing, calibration, raw files, failed runs and whole-take dataset splits. All acquisition in the chapter remains proposed. |
| 058, pp. 355-360 | Dataset schemas and provenance | Strict structure is only the first gate. Preserve source/derived/compiled identities, missing values, physical ports, effect ownership and lineage. |
| 059, pp. 361-366 | Calibration and fitting | Fit from identified upstream boundaries outward. Solver convergence and a low objective do not establish identifiability or fidelity. |
| 060, pp. 367-372 | Regression and adversarial musical tests | Separate documentary, mathematical, engine, host and measured evidence. Use independent oracles, stage traces, failure controls and deterministic absolute timelines. |
| 061, pp. 373-378 | Listening and claim protocol | Similarity, discrimination, equivalence and preference ask different questions. No panel, physical capture or perceptual fidelity result is supplied. |
| 062, pp. 379-384 | Performance, memory and latency | One audio owner advances state; compilation and destruction remain outside processing; bounded queues and real measured callback budgets need explicit failure behavior. |
| 063, pp. 385-390 | Framework-independent engine contracts | Preserve electrical coupling, units, half-open event ownership, no-time flushes and lifetime rules. A checked interface is not an implemented engine. |
| 064, pp. 391-396 | VST3 and standalone adapters | Thin adapters share engine semantics. State, automation, silence, tails, lifecycle, devices and licenses require distinct evidence. |
| 065, pp. 397-402 | Parameter and preset compatibility | Freeze IDs and normalized meanings, retain all banks, close gestures against their original identity, and keep musical state distinct from full DSP checkpoints. |
| 066, pp. 403-408 | Build, packaging and release | Qualify exact installed artifacts and real platform/host/device lanes. A native build, validator result or signature does not imply complete product qualification. |
| 067, pp. 409-414 | Dimensional art direction | Walnut/charcoal/brass appearance is original product design. Actual control semantics override generated image labels or key counts. |
| 068, pp. 415-420 | Player workflow | Editing focus and sounding route remain independent. Preserve held-note ownership, stable control identities, accessible alternatives and evidence-based usability results. |

## Findings governing the scanner implementation now

### 1. Admit a named numerical model without inventing calibrated voltage

The proposed importer distinguishes original bytes, documentary interpretation, fitted parameters and compiled representation (pp. 355-358). Every scalar carries units and evidence or an explicit unknown reason. Neither a valid schema nor a shaped hexadecimal digest establishes physical truth or the existence of its claimed asset (pp. 355, 358, 360).

For the scanner specifically, p. 386 requires **18 LC sections and 19 ground-referenced output voltages**, with the chorus return retained separately. Those absolute outputs already contain the return contribution. A second arbitrary dry term would count part of the circuit again. Node IDs, output numbers and terminal-selection identities are separate domains, just as source numbers, array indices and physical terminals are separate upstream.

The current dry-engine normalization cannot silently become volts. Page 386 distinguishes a voltage-scaled waveform from a dimensionless gain, and p. 350 requires a signed node-pair boundary, direction, receiving load and acquisition transfer. Future AO-28 loading can require a larger coupled solve; a convenient scanner API does not prove physical independence (p. 385). The first ideal-source/high-impedance scanner therefore needs an explicit nominal boundary and a replacement path.

The visually inspected p. 357 diagram identifies waveform boundary, graph assets and effect ownership as separate inputs to an offline compiler. Its prose explicitly distinguishes an AO-28 component registry from a complete connectivity netlist. Do not promote either a list of values or the scanner graph into a complete AO-28 model.

### 2. An independent numerical oracle must expose shared mistakes

Page 371 calls for independently assembled stationary scanner transfer checks including **absolute polarity and common-return loading**. Pages 367 and 372 require a declared evidence level, observable boundary and independent oracle per test. Agreement between two implementations sharing the same incorrect indexing or sign convention cannot close that gate.

The useful sequence for this session is graph/source admission, independent AC and transient references, prepared runtime, then rotating-mode and integration checks. Keep numerical error, physical-model approximation and missing measurements separate. A synthetic finite-frequency or transient pass is useful engineering evidence, even while a specimen match remains unestablished.

For sidebands and aliasing, p. 371 requires a higher-rate reference whose comparison has itself stabilized under refinement, with documented filtering and delay compensation. Legitimate modulation sidebands must remain distinct from folded artifacts. Unrestricted time warping, per-tap phase alignment or per-registration gain normalization can conceal the delay and amplitude error being tested (pp. 364, 371, 375). Freeze the numerical grid, excitation, phase floor and permissible corrections before grading the implementation.

Pages 347 and 365 require budgets to be chosen before held-out grading; hardware budgets additionally need measured uncertainty and coverage. An uncertain capture cannot certify the model by making its acceptance band arbitrarily wider. Preserve pass, fail, inconclusive and not-run as different outcomes (pp. 347-348, 366, 372).

### 3. Preserve one time history and meaningful state

Page 369 explicitly includes scanner mode and route changes in adversarial tests: retain state, preserve the common return, and avoid duplicate dry addition. Page 379 assigns circuits and sources to one serialized audio execution context; an additional receiver, hidden editor or internal slice cannot advance another clock.

The positive-block interval is `[start,start+N)`; end-boundary events stay for the next block. A zero-frame flush consumes current-frame controls once while advancing no oscillator, rotor, envelope, smoothing or delay history. A positive block with disconnected outputs still advances declared time (p. 387). Fixed-rate partition tests should compare both samples and state checkpoints; across rates, compare common physical times and declared latency using explicit tolerances, rather than comparing unequal grids bitwise (p. 370).

For a scanner line, preserve physical reactive coordinates and rotor history across supported changes. Musical controls are not a restart image of capacitors, phases or delay memories. Pages 389, 394 and 401 distinguish ordinary presets from a separately versioned stopped-engine checkpoint. Unsupported migration should require stopped preparation or an explicit failure; it must not become an unexplained phase reset (pp. 381, 389).

### 4. Prove the bounded processing path separately from preparation

Pages 358, 381 and 388 keep parsing, topology compilation, coefficient generation, allocation, file access and final destruction outside processing. The visually inspected p. 381 lifetime diagram sends retired handles back to a non-audio owner only after the final reader and transition tail finish. A `noexcept` declaration or lock-free atomic alone is not a bound on a full callback (pp. 380, 388).

Use fixed dimensions and an admitted input envelope; validate the candidate before replacing an already prepared model. A prepared numerical plan should not perform symbolic topology work, allocate a matrix or retry without a bound during sample processing. Runtime admission/failure tests need nonzero prior state so rollback is observable in later audio, not merely in a zero output buffer.

Allocation/lifetime/sanitizer correctness and Release performance measurements answer different questions (pp. 383-384). Record rate, block distribution, model identity, event load, transition state, compiler, CPU and timing instrumentation. The atlas's illustrative 48 kHz/64-frame `0.40D` target is a proposal, not an executed scanner benchmark, platform guarantee or measured deadline (p. 384).

### 5. Preserve current parameter semantics while adding scanner controls later

The atlas describes a **proposed 62-parameter companion registry** (pp. 397, 401). That statement does not establish that the companion exists in this checkout, nor does it authorize replacing the repository's current 45 stable records with those proposals. The current repository handoff correctly requires graph/oracle work before a separate append-only scanner/state migration.

For later integration, p. 398 specifies one six-state selector in stable `V1,V2,V3,C1,C2,C3` order and independent Swell/Great toggles; Great includes pedals. The selector being set while both routes are off is a valid retained state, which the UI should explain without changing the mode (p. 418). The normalized mapping and boundary thresholds are compatibility promises, alongside numeric IDs (pp. 397-400).

Do not silently relabel the existing normalized expression gain as calibrated mechanical pedal travel. Pages 398 and 418 distinguish physical expression travel, its downstream circuit law and software output trim. Similarly, continuous drawbar marking/travel is not itself an amplitude law; pending physical M3 behavior remains open when a scanner module works.

## Acquisition and calibration requirements retained for later phases

Pages 349-354 specify a campaign with an identified organ, AO-28, mains configuration, cabinet, fitted parts, condition and permissions. Internal electrical fixtures belong to a qualified technician's reviewed plan. The agent can prepare scripts and data checks; it cannot infer that an inaccessible node was measured. This review performed no physical acquisition.

For scanner captures, retain six modes, all Swell/Great combinations, stationary and moving electrical references, excitation, relevant controls and phase/position evidence (p. 352). Each port needs polarity, load, clock and calibration; header sample rate is distinct from a calibrated physical clock (pp. 350-351, 356). Missing calibration is unresolved, not unity gain. Raw bytes, channels, timestamps, synchronization and all derived transformations need reproducible identities.

Fit upstream boundaries before downstream coloring (p. 362). Wrong scanner polarity or source routing must not be repaired with cabinet equalization. Optimizer success says that a stopping rule was met; it does not establish unique physical parameters or agreement with an instrument (pp. 361, 365-366). The simple two-gain example on p. 361 shows why end-to-end output alone may identify a product of gains without identifying either internal gain.

Holdout membership is frozen by physical take/session and shared ancestry, including synchronized channels and derivative crops (pp. 354, 359, 366). The atlas explicitly says its proposed per-file checks do not supply a full corpus lineage traversal (p. 359). A scanner reconstruction, rendered example or new schema must remain synthetic/documentary unless an actual specimen capture closes the separate gate.

The downstream driver chapter adds another boundary warning: nominal 16-ohm markings do not supply impedance, thermal constants or nonlinear curves (p. 337). Speaker reciprocity, stored energy and thermal memory belong to connected models with their own evidence (pp. 338-342). Scanner qualification does not close those later Leslie dependencies.

## Product and UI plan, with actual visual findings

The product remains one engine exposed through offline, VST3 and standalone adapters, with an editor that consumes state rather than owning audio time (pp. 385, 391-396). Actual installed artifacts require separate scan/lifecycle, automation/state, device recovery, accessibility, packaging and platform evidence (pp. 403-408). A validator pass cannot establish a stable custom editor, standalone device recovery or physical B-3 sound. The atlas's dependency/license statements are dated documentary context; this assignment makes no new current licensing determination.

The actual rendered **p. 409** concept shows the intended warm wood frame, dark deck, ivory controls and cabinet view. Its caption expressly marks it as generated art direction. It also visibly includes a **STOP** control and approximate legends/key inventory. Pages 413 and 419 restrict a stop function to a separately selected accessory/extension profile. Thus the artwork must not override the semantic contract or silently add Stop to the baseline product.

The actual rendered **p. 415** is labeled as an original placement study, not a browser screenshot. It presents four retained manual banks, playing/preset-key separation, scanner/percussion summaries and an optional pedal drawer. Its layout supplies design intent, not evidence of a running audio UI or verified browser rendering.

The practical future interface invariants are:

- Editing a bank and selecting its sounding route are separate actions; preparing an inactive bank cannot change accompaniment (pp. 410, 416).
- Capture one semantic ID at gesture start and close against it before rebinding, including lost capture and editor teardown (pp. 399, 412, 416).
- Preset Cancel changes routing without manufacturing note releases; pedal controls remain independent (pp. 410, 416).
- UI notes retain per-owner press identity. Closing the editor releases UI-owned notes without releasing external MIDI ownership (pp. 412, 417).
- Stored percussion/scanner settings stay visible even when routing makes them inaudible; display eligibility without inventing envelope or measured-response telemetry (pp. 413, 418).
- Motion-disabled and flat alternatives preserve every musical action; legends remain semantic text, and keyboard/non-drag controls supplement sculpted visuals (pp. 411-414, 419-420).

Any future scanner service view can now display model identity, signed outputs, nominal topology and actual numerical diagnostics. It must not advertise an authenticity percentage, a calibrated physical meter or measured geometry without corresponding evidence. Pages 373-378 also prohibit treating a similarity/preference score or a nonsignificant listening result as a universal fidelity percentage.

## Concrete handoff for the current session

1. Admit the exact named scanner graph and bounds with source-page provenance and independent edge/output tests.
2. Freeze independent AC/transient and rotor test inputs, numerical budgets and comparison conventions before accepting runtime results.
3. Retain line, common-return, current and rotor traces so failures can be localized to their first divergent boundary (pp. 367, 369, 372).
4. Keep preparation, finite-state rejection, callback partition behavior, stopped-rate transitions and allocation measurements as separately observed gates.
5. Preserve the existing dry engine, 45 control meanings and legacy state fixtures while this module is qualified. Define any later public scanner controls and migration explicitly.
6. Publish exact source/data/toolchain identities, commands, observed failures and remaining gates. Hardware capture, full AO-28/Leslie models, host/device qualification and native accessible UI remain separate work unless newly retained evidence closes them.

## Commands and result scope

Working directory: `/workspace/scratch/1742da7072be/Hammond-B3-Organ`.

```sh
cat AGENTS.md
sha256sum Hammond_B3_Leslie_Research_Atlas_500pp.pdf
pdfinfo Hammond_B3_Leslie_Research_Atlas_500pp.pdf
git rev-parse HEAD
git rev-parse 'HEAD^{tree}'
sed -n '1,120p' docs/PLAN.md
pdftotext -f 337 -l 348 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 349 -l 360 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 361 -l 372 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 373 -l 384 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 385 -l 396 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 397 -l 408 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 409 -l 420 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
mkdir -p /tmp/hammond-scanner-a05
pdftoppm -f 357 -l 357 -scale-to 1600 -singlefile -png Hammond_B3_Leslie_Research_Atlas_500pp.pdf /tmp/hammond-scanner-a05/page357
pdftoppm -f 381 -l 381 -scale-to 1600 -singlefile -png Hammond_B3_Leslie_Research_Atlas_500pp.pdf /tmp/hammond-scanner-a05/page381
pdftoppm -f 409 -l 409 -scale-to 1600 -singlefile -png Hammond_B3_Leslie_Research_Atlas_500pp.pdf /tmp/hammond-scanner-a05/page409
pdftoppm -f 415 -l 415 -scale-to 1600 -singlefile -png Hammond_B3_Leslie_Research_Atlas_500pp.pdf /tmp/hammond-scanner-a05/page415
sed -n '1,90p' README.md
sed -n '1,100p' docs/STATUS.md
sed -n '1,95p' docs/NEXT_STEPS.md
tail -95 docs/DEVELOPMENT_LOG.md
git diff --check
```

The source identity, PDF extraction and four renders completed successfully; all four PNGs were actually viewed. The combined repository-context output exceeded its display allowance; no PDF-reading batch did. The current operational handoff and source/plan summaries were also available in inherited parent context. Temporary page images remain outside the repository and are not deliverables.

This assignment executed no scanner implementation, numerical test, native host/device test, hardware capture, listening study, commit or push. The integrator owns the independent acceptance of this review, current-status updates and publication. Claimed results in the PDF's original research remain attributed research statements, not this repository's observed execution.
