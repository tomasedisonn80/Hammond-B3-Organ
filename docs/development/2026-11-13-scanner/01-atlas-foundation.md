# Assignment 01: fresh atlas foundation review

## Identity and scope

- Session: `2026-11-13-scanner`, wave 1, assignment 01.
- Actual worker: `/root/w01_a01_atlas_foundation`.
- Starting source commit: `6dc0702d5473912268e8af8f852b9b9984198ef3`.
- Owned change: this note only; no production, data, shared-status, or historical-ledger edits.
- Read coverage: every PDF page **1-84 inclusive**, front matter and chapters 001-012. Text was read in bounded page batches; initially truncated passages were reread separately. This is a new review, not a recount of an earlier assignment.
- Direct visual inspection: rendered PDF pages **4, 51, and 73**, at a 1,500-pixel maximum dimension. Other pages were read as extracted text; this note does not claim independent examination of every figure or any external primary source.
- Canonical source: [Hammond_B3_Leslie_Research_Atlas_500pp.pdf](../../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf), 500 pages, 21,248,265 bytes, evidence edition 12 November 2026.
- Observed PDF SHA-256: `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.

All page references below are one-based pages in this PDF. The original PDF was not modified. References to an external manual or paper describe the atlas's account, not a fresh verification of that external source.

## Whole-project intent and implementation order

The target is an identified vintage electromechanical B-3, a selected AO-28 revision, and a vintage Leslie 122. Leslie 147, regional mains variants, modern B-3 instruments, and modified specimens need separate identities and applicability evidence (pp. 2-3, 13-18, 55-60). The atlas explicitly reports that no physical instrument was measured during its research (p. 2). This remains the evidence boundary for the atlas itself regardless of later software progress.

The roadmap on p. 5 distinguishes ten research waves from ten implementation milestones. Implementation proceeds through reference lock, testable skeleton, shared generator, console behavior, scanner, organ electronics, Leslie electronics, rotary acoustics, calibration, and product/release. Dependency completion requires retained evidence; a demonstration or attractive interface does not replace electrical or acoustic validation (pp. 5, 12). Current repository documentation places the next dependency-ready engineering work at nominal scanner graph admission, followed by an independent numerical reference.

The visually inspected responsibility map on p. 4 is explicitly conceptual. It preserves shared sources, contacts/presets, drawbars/pedals, scanner/AO-28 paths, Leslie electronics, crossover/drivers, independent rotating paths, and microphones/room. It does **not** establish serial circuit connectivity or permit loading to be discarded. Dry organ output and cabinet microphone output need different validation suites.

Three correspondence claims are separate: functional controls/routing, calibrated specimen audio, and physical appearance (p. 13). Final release also needs deployment, state, host, performance, interface, and held-out evidence (pp. 12, 18). An engineering nominal model can advance while these independent claims remain open.

## Findings that govern the scanner work

| Source basis | Consequence for this session |
| --- | --- |
| pp. 19-24: select drawing applicability; transcribe connectivity before markings and numerical normalization | Keep graph endpoints, printed values, SI conversion, evidence class, variant, source page, and unknowns as explicit records. A readable redraw or atlas reconstruction is not automatically a specimen netlist. |
| p. 27: scanner patents contain alternative circuits, including a possible 24-section line | Do not import that section count or patent constants into the separately selected production-line reconstruction. The current proposed 18-inductor graph needs its own source review. |
| p. 27: line network, angular weighting, and rotating assembly are separate evidence objects | Develop the LC graph and independently checked static response before rotor animation or six-mode integration. Each mechanism needs a named boundary and its own tests. |
| p. 27: weighted-tap summation is a proposed abstraction; loading may require solving coupling capacitances with the line | Normalized rotor weights cannot substantiate a circuit-exact loaded response. Preserve receiver/loading assumptions and the replacement path. |
| p. 51: one shared six-mode scanner; independent Swell/Great enable flags; Great vibrato includes pedals | Future engine routing must exercise all four enable combinations for each V1-V3/C1-C3 mode. Independent upper/lower scanner clocks would be a declared extension. |
| pp. 4, 28, 51: percussion is a separately governed path | Do not assume that scanning a summed upper-manual output automatically preserves the selected AO-28 percussion route. Resolve its injection and bypass boundary against the selected circuit. |
| pp. 15-16, 67-70: values carry units and source boundaries; normalized waveforms do not establish calibrated volts | The current nominal dry signal cannot silently become a physical scanner drive voltage. Name any normalized-to-drive assumption and retain unavailable electrical scale/load evidence. |
| pp. 46, 63-66, 70, 82: shared source histories advance continuously | Scanner preparation, mode changes, bypass, state changes, and errors must preserve engine source ownership and timing. Do not create duplicate oscillators or reset phases. |

The directly inspected p. 51 table gives these scanner admission sets: neither switch enabled admits neither manual nor pedals; Swell only admits Swell; Great only admits Great and pedals; both admit all three. This is a documented routing target in the atlas, not evidence that the current engine already implements scanner processing.

## Broader dependencies and interpretation hazards

**Evidence contracts.** Pages 15 and 21 require parameter origin, units, conditions, uncertainty, source identity, and revision. Unknown values stay unknown across serialization; they are not zero. Page 22 orders node/terminal extraction before component interpretation and fitting. Page 24 treats traceability as distinct from audio correspondence and requires unresolved acquisitions to remain concrete. These rules support strict scanner schema admission without fabricated winding losses or measured tags.

**Source and control identity.** Pages 43-48 distinguish 91 electrical sources, 96 physical disk positions, 48 rotating assemblies, 24 drive gears, and five balancing blanks. Source numbers are not terminals, MIDI notes, or storage indices (pp. 61-66). The p. 62 rational table is attributed to a pinned software comparison, not a newly verified factory gear inventory. A scanner extension must preserve the existing nominal source-model identity rather than implying that the extension validates upstream gearing.

**Console approximations remain visible.** Page 50 presents a mutually exclusive selector as an initial proposal while also acknowledging physical multiple latching and referring that refinement to chapter 019. Page 52 describes continuous-contact drawbars and a nine-gain approximation; it explicitly says that smoothing alone does not reproduce transformer loading. Those pending physical M3 tasks do not vanish when the scanner runs. Pages 37-42 also separate measured contact motion from MIDI-inferred trajectories.

**Port and effect ownership.** Pages 67-78 distinguish induced source voltage, loaded terminal voltage, filters, and downstream loads. A filtered terminal waveform must not receive the same filter again. The inspected p. 73 table identifies separate filter families and makes the legacy `mf`/`mfd` microfarad interpretation explicit. The later bulletin is a separate revision, not a universal substitution (p. 74). The numerical 0.1 dB/1 degree target on p. 78 is proposed, not a factory specification or an achieved test result. Scanner error budgets likewise need declared purpose and scope.

**No arbitrary leakage layer.** Pages 79-84 require injection-point and shared-source identity, signed/phase-aware transfers, and identifiable fitted coefficients. Physical neighbors need not be neighboring semitones, and a terminal capture can already contain leakage. Scanner/organ fitting must not absorb upstream leakage, loading, or phase errors into unexplained downstream constants.

**Visual assets are not circuit or geometry evidence.** Pages 6, 31-36, and 58 distinguish reference pictures, retouched derivatives, generated UI concepts, and measured dimensions. The UI consumes audio-owned snapshots; a hidden mesh or stalled render must not alter sound (p. 34). The p. 36 companion inventory counts are references to absent companion material, not proof that this checkout contains or has verified that inventory.

## Dependency-ready acceptance advice

1. Admit the named nominal scanner graph with independent literal endpoint, value, output-polarity, and return-state expectations. Keep the graph's documentary reconstruction class and unresolved physical applicability explicit.
2. Build an independently stamped offline frequency/transient reference at the same ports and loading assumptions. Report residuals, conditioning, and convergence; retain topology mutations that can evade DC-only checks.
3. Define and test prepared runtime state before animation: finite behavior, sample-rate policy, block partition behavior, initial energy, mode/return-state transitions, and bounded processing with no callback allocation or file access.
4. Implement one continuing rotor history only after line behavior is established. Specify six-mode routing and the lower/pedal dependency without changing existing parameter/state meanings silently.
5. Keep physical acquisition separate: AO-28/scanner revision, component/winding losses, loading, calibrated levels, rotor geometry/weights, and stationary/running captures need identified evidence. Neither code compilation nor nominal oracle agreement closes those gates.

## Commands and observed outcomes

Working directory: repository root at `/workspace/scratch/1742da7072be/Hammond-B3-Organ`.

```sh
cat AGENTS.md
pdfinfo Hammond_B3_Leslie_Research_Atlas_500pp.pdf
sha256sum Hammond_B3_Leslie_Research_Atlas_500pp.pdf
pdftotext -f 1 -l 28 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 6 -l 20 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 5 -l 5 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 29 -l 42 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 43 -l 56 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 57 -l 70 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 71 -l 84 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 21 -l 21 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 35 -l 36 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftoppm -f 4 -l 4 -scale-to 1500 -singlefile -png Hammond_B3_Leslie_Research_Atlas_500pp.pdf /tmp/hammond-a01/page004
pdftoppm -f 51 -l 51 -scale-to 1500 -singlefile -png Hammond_B3_Leslie_Research_Atlas_500pp.pdf /tmp/hammond-a01/page051
pdftoppm -f 73 -l 73 -scale-to 1500 -singlefile -png Hammond_B3_Leslie_Research_Atlas_500pp.pdf /tmp/hammond-a01/page073
git rev-parse HEAD
git status --short
git diff --check
```

All commands completed successfully. The first combined read exceeded its output allowance, and the p. 29-42 display lost a small middle passage; the subsequent smaller reads above recovered those passages. The three PNGs were opened and visually inspected through the image viewer. Temporary rendered images are outside the repository and are not deliverables. Current README, operational handoff, latest development-log entry, plan, status, next steps, and existing atlas review were consulted as repository context.

No engine test, scanner solver test, primary-source acquisition, hardware measurement, host qualification, commit, or push was performed by this assignment. The root integrator owns substantive acceptance, shared-status updates, and publication.
