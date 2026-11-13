# Assignment 02 - fresh atlas reading and independent scanner graph review

## Identity, ownership and scope

- Session: `2026-11-13-scanner`, wave 1, assignment 02 of 60.
- Actual worker: `/root/w01_a02_atlas_scanner_graph`.
- Owned file: this note only; no production, shared status, earlier ledger or source assets changed.
- Inspected baseline commit: `6dc0702d5473912268e8af8f852b9b9984198ef3`.
- Its actual Git tree: `a4f1d4b300de236436e22b748b1d4c46ed501ceb`.
- Source: `Hammond_B3_Leslie_Research_Atlas_500pp.pdf`, 500 pages, 21,248,265 bytes.
- Source SHA-256 freshly computed: `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
- **Fresh text coverage: every page 85-168 inclusive, 84 pages, chapters 013-026.** The first large extraction was truncated; pages 85-96 were re-read in complete six-page extracts. Pages 97-102 were fully visible in the original extraction; all remaining pages were read in complete six-page batches.
- **Actual visual inspection:** rendered pages 157, 158 and 166. Page 158 was inspected at 2,000 pixels; pages 157/166 at 1,600 pixels. The temporary PNGs are review aids under `/tmp/hammond-a02`, not new source evidence or deliverables.
- Read `AGENTS.md`, the current status/next-step context, plan and atlas review inherited in the task, the relevant README/handoff/log sections, the complete scanner graph and numerical/rotor portions of `M3_REMAINING_AND_SCANNER_GATE.md`, and `docs/research/ERRATA.md`.

This is an independent comparison with the **supplied atlas**, including its actual circuit drawing. No newly retrieved primary paper, production drawing, specimen measurements, companion netlist or missing original scripts were acquired in this assignment. Those are separate evidence gates.

## Complete assigned chapter coverage

| Chapter / pages | Main finding and implication |
| --- | --- |
| 013 / 85-90 | Shared mechanical timing, shaft residuals and pickup-gap modulation are separate from scanner/Leslie motion and hum. Preserve generator history when an effect is bypassed. Half-cycle forcing rates are derived, not measured sideband depths. |
| 014 / 91-96 | Observations, editable profiles, compiled immutable data and advancing playback state are separate. Validate duplicate names, exact identities, units, references and unknowns before publication. Table V G-G readings cannot become pickup gains. |
| 015 / 97-102 | Source IDs, terminal positions, MIDI notes and storage indices are distinct. Manual foldback repeats octave subtraction; shared-source collisions retain separate contact/load branches. |
| 016 / 103-108 | One 91-source field per sample supplies both manuals; notes never reset phase. Preparation and retirement are off-thread. Parameter-only zero-frame calls do not advance physical state. |
| 017 / 109-114 | Integer drawbars use a named nominal 3 dB law initially; the production mechanism is a tapped-transformer/contact network. Coherent shared-source paths add amplitude. Physical travel/loading remains open. |
| 018 / 115-120 | Contact transients depend on phase at actual edges, including derivative jumps at zero crossings. Nine histories share a mechanical cause. High-rate switching must precede bandwidth reduction; already aliased audio cannot be repaired by later upsampling. |
| 019 / 121-126 | Cancel unlatches registration without clearing held keys or generator history. A physical eleven-bit latch mask differs from a normal exclusive selector. The 162-digit chapel matrix is documentary and not universal specimen wiring. |
| 020 / 127-132 | Percussion has one upper-manual detector/control history behind upper B. Ninth physical drawbar/1-foot keying corresponds to the eighth harmonic, not the eighth drawbar. Equal-time off/on has no recharge duration. |
| 021 / 133-138 | Borrowed percussion source, sustained return, upper attenuation and 1-foot mask have separate ownership. The percussion audio branch bypasses scanner. RC products are electrical surrogates, not observed audible decay. |
| 022 / 139-144 | Pedals consume the shared source field through 25-by-8 wiring, four buses and a separate reactor/mix network. Preserve 195 connections, five nulls and duplicate-source branches; lower/Great routing owns their later vibrato relationship. |
| 023 / 145-150 | Expression is a coupled capacitive preamp network with loading and feedback, not just final output gain. Motion needs `d(Cv)/dt`, including `v*dC/dt`. It must not reset scanner, generator or percussion histories. |
| 024 / 151-156 | Separate controls, key ownership and physical DSP histories. Use one timestamped command timeline. Ordinary patches do not restore held notes or transient histories; a replay checkpoint is a separate contract. |
| 025 / 157-162 | Nominal late-B-3 scanner is an explicit connected 18L/18C network with 19 signed outputs, a common return, compensated early taps and termination. A correct nominal solver is an engineering milestone, not specimen equivalence. |
| 026 / 163-168 | Distinguish 19 line outputs, 9 selected terminals and 16 mechanical positions. Capacitive overlap is not hard metallic switching. The printed traversal has a real 15-versus-16 error. |

## Independent transcription of the scanner graph

I first extracted pp. 157-168 and inspected the rendered p. 158 diagram, then compared the transcription with the repository gate. The drawing visibly places early divider branches **before** each inductor, labels the return resistor and switch, identifies the final smaller capacitor, and explicitly says all 19 output voltages use ground as their reference. The existing candidate graph agrees with that drawing.

The local naming convention is `g` for electrical datum, `p0` for the driven node, `p1..p18` for the section junctions, `r` for shared return, and `d1..d6` for early divider midpoints: **27 named nodes** before ground/short contraction. The `d` names are local reconstruction names. Direction below declares current/voltage sign; it does not pretend a passive resistor drawing itself imposes a unique arrow.

### Reactive elements: all 36 endpoint pairs

The printed inductor value is **500 mH** (0.5 H) for every row. The printed capacitor value is **0.004 microfarad** (4e-9 F) except the final **0.001 microfarad** (1e-9 F). Values are from p. 157; all endpoint patterns and final exception are visible on p. 158.

| Section | Inductor: positive -> negative | L in H | Capacitor: positive -> negative | C in F |
| ---: | --- | ---: | --- | ---: |
| 1 | L1: p0 -> p1 | 0.5 | C1: p1 -> r | 4e-9 |
| 2 | L2: p1 -> p2 | 0.5 | C2: p2 -> r | 4e-9 |
| 3 | L3: p2 -> p3 | 0.5 | C3: p3 -> r | 4e-9 |
| 4 | L4: p3 -> p4 | 0.5 | C4: p4 -> r | 4e-9 |
| 5 | L5: p4 -> p5 | 0.5 | C5: p5 -> r | 4e-9 |
| 6 | L6: p5 -> p6 | 0.5 | C6: p6 -> r | 4e-9 |
| 7 | L7: p6 -> p7 | 0.5 | C7: p7 -> r | 4e-9 |
| 8 | L8: p7 -> p8 | 0.5 | C8: p8 -> r | 4e-9 |
| 9 | L9: p8 -> p9 | 0.5 | C9: p9 -> r | 4e-9 |
| 10 | L10: p9 -> p10 | 0.5 | C10: p10 -> r | 4e-9 |
| 11 | L11: p10 -> p11 | 0.5 | C11: p11 -> r | 4e-9 |
| 12 | L12: p11 -> p12 | 0.5 | C12: p12 -> r | 4e-9 |
| 13 | L13: p12 -> p13 | 0.5 | C13: p13 -> r | 4e-9 |
| 14 | L14: p13 -> p14 | 0.5 | C14: p14 -> r | 4e-9 |
| 15 | L15: p14 -> p15 | 0.5 | C15: p15 -> r | 4e-9 |
| 16 | L16: p15 -> p16 | 0.5 | C16: p16 -> r | 4e-9 |
| 17 | L17: p16 -> p17 | 0.5 | C17: p17 -> r | 4e-9 |
| 18 | L18: p17 -> p18 | 0.5 | C18: p18 -> r | 1e-9 |

### Resistive elements: all 14 endpoint pairs

| Element | Positive -> negative | Printed value | SI ohms |
| --- | --- | --- | ---: |
| R1+ | p0 -> d1 | 27 kOhm | 27000 |
| R1- | d1 -> r | 68 kOhm | 68000 |
| R2+ | p1 -> d2 | 56 kOhm | 56000 |
| R2- | d2 -> r | 0.15 MOhm | 150000 |
| R3+ | p2 -> d3 | 39 kOhm | 39000 |
| R3- | d3 -> r | 0.15 MOhm | 150000 |
| R4+ | p3 -> d4 | 33 kOhm | 33000 |
| R4- | d4 -> r | 0.18 MOhm | 180000 |
| R5+ | p4 -> d5 | 18 kOhm | 18000 |
| R5- | d5 -> r | 0.18 MOhm | 180000 |
| R6+ | p5 -> d6 | 12 kOhm | 12000 |
| R6- | d6 -> r | 0.18 MOhm | 180000 |
| Rc | r -> g | 22 kOhm | 22000 |
| Rt | p18 -> r | 15 kOhm | 15000 |

The total is **50 passive elements: 18 inductors, 18 capacitors, 14 resistors**. An ideal drive between `p0` and `g` imposes `V(p0)-V(g)=Vin`; it is a separate boundary, not a 51st passive. The ideal return switch connects `r` to `g`: **closed in vibrato, open in chorus**. Rc remains in the graph and is shunted when the switch closes. The short must be a constraint/contraction, never an infinite floating-point conductance.

### All 19 output identities and polarity

| Output | Signed voltage |
| --- | --- |
| v1 | V(d1) - V(g) |
| v2 | V(d2) - V(g) |
| v3 | V(d3) - V(g) |
| v4 | V(d4) - V(g) |
| v5 | V(d5) - V(g) |
| v6 | V(d6) - V(g) |
| v7 | V(p6) - V(g) |
| v8 | V(p7) - V(g) |
| v9 | V(p8) - V(g) |
| v10 | V(p9) - V(g) |
| v11 | V(p10) - V(g) |
| v12 | V(p11) - V(g) |
| v13 | V(p12) - V(g) |
| v14 | V(p13) - V(g) |
| v15 | V(p14) - V(g) |
| v16 | V(p15) - V(g) |
| v17 | V(p16) - V(g) |
| v18 | V(p17) - V(g) |
| v19 | V(p18) - V(g) |

Do not substitute `r` for `g`. In chorus the return is generally moving; returning local capacitor/divider voltages changes the intended electrical signal. Nineteen outputs do not imply nineteen energy stores: the initial physical accounting is 18 capacitor voltages plus 18 inductor currents, subject to the chosen graph's actual algebraic constraints (p. 159).

## Source and numerical hazards confirmed

1. **Off-by-one divider mutation:** Rk+ must originate at `p(k-1)`, not `pk`. Page 158 explicitly says the divider loads the input side. At DC every ideal inductor shorts, so a wrong after-inductor graph can pass the same DC checks. Preserve independent literal endpoint tests and finite-frequency mutation tests.
2. **Stage-count inconsistency:** p. 157 reports that the paper's prose says nineteen stages while its table and figures enumerate eighteen. Retain 18L/18C/19 outputs; this assignment does not independently re-check the external paper.
3. **Traversal mismatch is printed, not an extraction artifact:** I inspected p. 166. Its list is `[0,1,2,3,4,5,6,7,8,7,6,5,4,3,2]` (15 entries), while its loop indexes 16 positions and wraps modulo 16. Adding final `1` is consistent with its wrap sentence and endpoint counts, but remains an **inferred correction** pending primary documentary comparison. Existing erratum E01 is justified.
4. **Finite-bandwidth concern:** triangular overlap is continuous but changes slope at plate centers (p. 166). One selected internal rate must be justified against converged sideband evidence; arbitrary smoothing changes the model.
5. **Mode switching:** return topology changes preserve compatible capacitor/inductor histories; a depth-map change is downstream observation and must not erase energy or phase (pp. 160, 166).
6. **Unmeasured boundaries:** ideal source, ideal coils and negligible scanner loading are named approximations. Coil loss, mutual/stray coupling, drive/receiver impedance, capacitance versus angle, and actual specimen scaling remain unknown (pp. 158, 161-162, 165, 167-168). Engine normalized amplitude is not calibrated volts.
7. **Capacitive motion:** the general rotor equation differentiates charge, retaining changing-capacitance terms; normalized triangular weights apply only to the explicitly unloaded limiting approximation (p. 165).

## Independent arithmetic check actually executed

I used Python standard-library `fractions.Fraction`, separately entering the six resistor pairs and Rt/Rc from the p. 157 table. With inductors short and capacitors open:

- `Rparallel = 92438660160000 / 9455738267` ohms = `9775.932618884532` ohms.
- Chorus return ratio `r/Vin = 9455738267 / 13657495547` = `0.6923478931008726`.
- Vibrato input resistance is `Rparallel`; chorus input resistance is `Rparallel + 22000` ohms.

| Tap | Vibrato DC ratio | Chorus DC ratio |
| ---: | ---: | ---: |
| 1 | 0.7157894736842105 | 0.9125620327760375 |
| 2 | 0.7281553398058253 | 0.9163664175419848 |
| 3 | 0.7936507936507936 | 0.9365162319097039 |
| 4 | 0.8450704225352113 | 0.9523355890719661 |
| 5 | 0.9090909090909091 | 0.9720316266455339 |
| 6 | 0.9375 | 0.9807717433188046 |
| 7-19 | 1 | 1 |

These agree with the existing gate document. This is independent ideal-graph arithmetic, **not** an AC solve, transient solve, runtime acceptance or measured voltage report. The node/component/output arithmetic also returned 27/50/19, with 36 candidate reactive coordinates.

## Consequences for the next implementation

Proceed with strict admission of this named documentary reconstruction, then an independently stamped AC reference and independent runtime formulation (pp. 160-162). Reject wrong prefix conversion, duplicate IDs/keys, omitted or misattached elements, return-referenced outputs and wrong switch states. Preserve previous output files on rejection; keep parsing/preparation outside the audio path (pp. 94-96, 160).

Preserve upper/lower/pedal/percussion routing boundaries in eventual integration: percussion bypasses scanner (pp. 134, 138); pedals participate through the lower/Great path (pp. 139, 142); shared sources and all unrelated histories continue through bypass and silence (pp. 103-108, 148, 166). A later effect must not become another authority for note ownership or ordinary saved-state history (pp. 151-156).

The graph is suitable for a **nominal engineering module**. Complete M4 physical acceptance still needs a selected production assembly, primary circuit comparison, calibrated per-tap complex responses under both return states, source/probe/receiver loads, rotor-angle transfer and held-out captures (pp. 161-162, 167-168). Complete M3 additionally retains loading, latch, contact-bandwidth, expression and pedal-network acquisition gaps described above.

## Commands and actual outcomes

All repository commands ran from `/workspace/scratch/1742da7072be/Hammond-B3-Organ`.

- `cat AGENTS.md`; repository contract read.
- `pdfinfo Hammond_B3_Leslie_Research_Atlas_500pp.pdf`; reported 500 pages, PDF 1.4, unencrypted, 21,248,265 bytes.
- `sha256sum Hammond_B3_Leslie_Research_Atlas_500pp.pdf`; digest recorded above.
- `pdftotext -f 85 -l 102 -layout ... -`; initial aggregate output truncated. Re-read 85-90 and 91-96 completely; 97-102 fully visible in initial output.
- Complete `pdftotext -f FIRST -l LAST -layout ... -` reads for ranges 85-90, 91-96, 103-108, 109-114, 115-120, 121-126, 127-132, 133-138, 139-144, 145-150, 151-156, 157-162 and 163-168. All commands exited 0.
- `pdftoppm -f 158 -singlefile -scale-to 2000 -png ... /tmp/hammond-a02/p158`, and corresponding 1,600-pixel renders of pages 157/166; all exited 0 and all three images actually inspected.
- `pdftotext -v`; Poppler 25.03.0.
- `git rev-parse HEAD HEAD^{tree}` and `git status --short`; baseline identities recorded; another worker's session directory was already untracked and left intact.
- Python inline exact-rational calculation described above; completed successfully, no files created.
- `git diff --no-index --check /dev/null docs/development/2026-11-13-scanner/02-atlas-scanner-graph.md`; returned 1 for the new-file difference, with no whitespace diagnostics. A direct Python trailing-whitespace/final-newline assertion also passed.

No project tests were needed for this source-only note and none are claimed. No remote mutation, commit, push or extra agent dispatch occurred. The integrator owns acceptance, shared status and publication.
