# A03 - Atlas electronics reading and R4 boundary review

## Assignment, source and coverage

- Session: `2026-11-14-waveform-continuation`; worker A03, wave 1. This is a fresh assignment, separate from the active `2026-11-14-reference-refinement` and all historical ledgers.
- Owned output: this note only. No product source, shared documentation, build, commit or publication was performed.
- Checkout and `origin/main` observed at start: `2e161dc3a60fc3442051799574feed37bffbfc5c`; initial `git status --short` was empty. Later concurrent edits belong to their owners.
- Read `AGENTS.md` and the entire `docs/PLAN.md`. Read the current reference-refinement scope/checkpoint and, for concrete continuation, the complete `docs/ROTARY_NUMERICAL_CONTRACT.md` and `docs/ROTARY_PROPAGATION.md`.
- Source PDF: `Hammond_B3_Leslie_Research_Atlas_500pp.pdf`, SHA-256 `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
- Assigned extracted text: `/workspace/scratch/e3cacb90cc81/atlas-text/part-3-169-250.txt`, SHA-256 `ab0705cd842e3aa2ec0c758f8fc8ab5c7678573de2cd81fe66f2a1d45035e25f`.
- **Full textual coverage: PDF pages 169-250 inclusive, all 82 pages, sequentially.** Read all 4,922 lines using consecutive ranges `1-500`, `501-1000`, `1001-1500`, `1501-2000`, `2001-2500`, `2501-3000`, `3001-3500`, `3501-4000`, `4001-4500`, `4501-4922`. No atlas chunk was truncated; searches did not replace reading.
- **Selected visual coverage:** rendered and inspected original PDF pages **171, 177, 182, 185, 194, 200, 212, 225, 230, 231, 242 and 250**, using Poppler `pdftoppm` 26.05.0 at a 1,500-pixel longest edge. This is not a claim to have visually inspected all 82 pages or the underlying external schematics.
- Frozen contract hash: `ROTARY_NUMERICAL_CONTRACT.md` SHA-256 `4c060088f0718586a7c6810e5c055c652d8924db4474db770237193ab459bd63`; propagation handoff SHA-256 `29539c8395901fe0057c52fa28aceac0729ebc854874697e49665379b272d261`.

The assigned interval contains scanner control/numerics/calibration, AO-28 electronics, provenance, hybrid boundaries and the beginning of dry-organ validation. It does **not** contain the later detailed Leslie amplifier/crossover chapters. Leslie findings below are limited to interfaces and dependencies explicitly stated here; this reading does not independently establish a 122 or 147 circuit.

| Pages fully read | Chapter and result relevant to continuation |
| --- | --- |
| 169-174 | Scanner tablet routing, six maps/modes, chorus reference, state and capture gates. |
| 175-180 | WDF network size, wave signs, coupled root, printed-source discrepancies and independent circuit comparison. |
| 181-186 | Descriptor/state-space formulation, rank, physical energy state, loaded AC/transient comparisons. |
| 187-192 | Scanner capture boundaries, shared angle, complex sidebands, noise/condition separation and held-out calibration. |
| 193-198 | AO-28 eight-socket identity, separate A/B/H entries, shared valve sections and revision-qualified topology. |
| 199-204 | Connected linear reference, T3 multiport/loading, differential/common-mode output and separate numerical/physical gates. |
| 205-210 | Valve families, model units/domains, grid/screen currents, bounded nonlinear solve and unperformed device fitting. |
| 211-216 | Shared nonlinear drive, bias/feedback memory, voltage scaling, headroom and history-dependent validation. |
| 217-222 | Supply graph, coherent mains phase, noise units/state and explicit absent measurements. |
| 223-228 | Configuration/condition/service separation and single ownership of already captured effects. |
| 229-234 | Alias sources, one clock for connected groups, ADAA response/delay and separately converged reference. |
| 235-240 | Inventory versus netlist, namespaces, unit conversion, unresolved values and source-conflict preservation. |
| 241-246 | Boundary-first hybrid models, two-way loading, one owner per response and evidence-qualified promotion. |
| 247-250 | Dry-organ finish line, coherent source reuse, temporal/percussion histories and fixed-versus-moving scanner tests. |

## Scanner requirements and exclusions from R4

1. The six-position selector has no OFF mode. Swell selects upper sustained material; Great selects lower sustained material **and shaped pedals**. Percussion joins downstream of scanning. The four tablet states route U/L/P as none/U/L+P/U+L+P to the shared scanner, with the complement bypassed. One scanner phase and wet history continue even with both tablets off (pp. 169, 172-174). An acoustic renderer must accept the upstream signal at its declared boundary without inserting another per-manual scanner or changing musical routing.
2. The published late-B-3 depth maps are V1/C1 `[1,2,3,4,5,6,7,8,9]`, V2/C2 `[1,2,3,5,7,9,11,12,13]`, V3/C3 `[1,2,4,7,10,13,16,18,19]`. These are one-based schematic node labels, not physical lugs or interpolated delay depths (p. 170). The selected line has **18 inductors, 18 capacitors and 19 observable voltages**; nineteen outputs do not imply nineteen stored-energy states (pp. 175, 181).
3. Chorus changes the return network: the cited research circuit uses a 22 kOhm return resistor. With absolute nodes `v_k = r + z_k` and normalized scan weights, the common return is already included once. A later dry copy would double it (p. 171). R4 must not add a corrective chorus/dry mix to compensate upstream errors; p. 250 reiterates this exclusion.
4. The network must retain loading, signs and physical state. A coupled root cannot be repaired by inserting arbitrary delay; early divider branches attach before their corresponding inductors. Printed WDF source/root, switch, inductance and prewarp inconsistencies require independent derivation (pp. 177-180, 182). Topology or rate changes preserve compatible capacitor voltages/inductor currents rather than reusing incompatible wave memories or resetting all state (pp. 172, 178, 184).
5. A stationary transfer does not establish rotating behavior. Compare all taps and both electrical states, then one shared angular trajectory and signed complex sidebands. The documentary 412 rpm nominal and 16-times-rotation plate-scale structure are not interchangeable measured rotation estimates (pp. 187-191). Six modes crossed with four tablet combinations, isolated U/L/P/Q signals, phase continuity and explicit return accounting remain separate tests (p. 250).

**Unknowns remain:** specimen harness correspondence, finite switch contact behavior, coil losses/parasitics, source/receiver impedances, bypass/recovery gain and polarity, repeatable phase-referenced captures and predeclared hardware tolerances (pp. 173-174, 186-192). Atlas algebra examples and nominal AC companions are limited software evidence. The current repository's scanner G5 issue is preserved by its handoff and is not addressed or regraded by this assignment.

## AO-28 and Leslie electrical boundaries

The documentary AO-28 inventory is exactly V1-V8: V1/V2 6AU6 input paths, V3 12BH7 line/output sections, V4 12AX7 around expression, V5/V6 6C4 percussion functions, V7 12AU7 percussion control sections and V8 6X4 rectification. Tube suffix/brand and actual operating point remain specimen fields. The prose ambiguity about V3 must not create a ninth socket (pp. 193-195, 198).

The separate non-vibrato A, vibrato B and percussion H entries, V3A scanner drive, V3B T3 output and V4 expression boundaries constrain future connection. Whole-bus saturation or independent per-note saturation cannot substitute for the actual branch/common-stage order. Shared glass alone does not prove crosstalk; traced supply, cathode-bias and feedback connections do require coupled behavior or an explicitly qualified approximation (pp. 194-196, 211-214).

| Required electrical evidence or behavior | Source basis | Consequence for independent R4 |
| --- | --- | --- |
| One selected revision and independently reviewed endpoint connectivity; documentary value placement is insufficient. | pp. 196, 235-240 | Do not derive a cabinet input signal by inventing missing AO-28 wiring. |
| DC operating point and connected small-signal response with source impedance, receiver load and controls recorded. | pp. 199-200, 202-204 | An acoustic success does not qualify the missing dry preamp. |
| Both T3 output legs, reference return, cable/load, differential polarity and common-mode behavior. | pp. 199, 201, 203 | A normalized R4 sample is not a calibrated G-G voltage port. |
| Identified transformer winding polarity, ratio, copper resistance, magnetizing/leakage/loss/capacitance behavior. | pp. 201, 204 | No guessed T3 ratio or duplicated downstream transformer response. |
| Family-specific device surfaces, derivatives, units, valid voltage domain, screen/grid currents and charge. | pp. 205-210 | No generic waveshaper inserted to make acoustic audition sound like a tube organ. |
| Host presentation gain distinct from volts-per-normalized-unit drive and condition-specific headroom. | pp. 195, 211, 215 | Preserve input identity and absolute numerical gain; do not normalize each fixture. |
| Connected supplies/bias/feedback and one owner for ripple/noise already present in captured data. | pp. 213, 217-222 | No decorative hum, sag, hiss or extra aging filter in R4. |

The AO-28 is a preamplifier/transformer-output chassis, **not the Leslie loudspeaker power stage** (p. 193). Its T3 must be checked with the intended cabinet input model (p. 194); a similarly named Leslie transformer is not AO-28 T3 (p. 199). A whole Leslie microphone recording combines downstream amplification, drivers, rotation and room, so it cannot uniquely identify AO-28 gain or headroom (pp. 197, 203, 215). Electrical blocks can exchange loading in both directions; a measured voltage-only output does not supply the input-current behavior needed for arbitrary reconnection (p. 242).

The atlas interval supplies no verified AO-28 absolute gain, clipping threshold, output wattage, fitted valves or measured T3 values (pp. 197, 201, 209-210, 216). It also supplies no Leslie revision-specific netlist, crossover transfer, real driver impedance, radiation calibration or physical cabinet comparison. The complete plan retains **M5 connected dry-organ validation before downstream fitting**, **M6 separately identified 122/147 electronics and loads**, and independent M7 acoustic rendering. The lack of M5/M6 inputs blocks an integrated physical claim while leaving declared synthetic R4 engineering useful.

## Evidence handling that must survive the continuation

- Preserve source namespaces, alternatives and missing values. The atlas's 85 stock records and 124 placement/section entries are neither complete connectivity nor a physical package count. Null quantity is not one (pp. 235-236).
- Resolve active units before a numerical electrical build. Documentary MF is converted only with corroboration; `1 MEG` must not become SPICE `1M` (milli). A capacitor rating is not an operating voltage. Unknown/conflicting active values block numerical export (p. 237).
- Keep the factory C59 versus redraw C56 collision, repeated catalog callout and unresolved resistance glyph as evidence records. Do not silently choose whichever simulation sounds convenient (p. 239).
- Configuration, dated condition and service history are different records. One specimen does not establish an aging population or covariance. Unknown uncertainty does not become random audible modulation (pp. 223-228).
- A captured waveform/transfer already includes its upstream hardware. An additional model for that same response duplicates it. Every runtime block therefore needs a boundary, ownership, validity domain, persistent state, approximation and replacement criterion (pp. 224, 228, 241-246).
- Preserve three result classes: documentary correctness, independent numerical consistency and measured specimen agreement. Attractive audio, illustrative plots and precision of a solver cannot substitute for missing captures (pp. 174, 180, 192, 198, 204, 210, 216, 240, 246-247).

## Concrete R4 continuation implications

These are implementation consequences read against `rotary-numerics-v1`, not new physical constants or replacement budgets.

1. **Freeze the acoustic boundary.** Consume separate double normalized research waveforms at the effective horn radiation point and drum outlet. The current contract deliberately excludes calibrated electrical outputs/pascals, crossover, drivers, horn transit, directional/microphone filters, cabinet and room. Each effect needs one future owner before connection (atlas pp. 241-246; numerical contract sections 1 and 4). Preserve the default dry Engine, all 47 parameters/state4 and readers 1-3.
2. **Implement the specified operator exactly.** Write input frame `n`, observe at `n-2`, solve each of four retarded paths, read nodes `k-1,k,k+1,k+2` at the returned split emission position, apply `reference_distance/r`, and sum signed Horn then Drum. Negative waveform time is declared zero. The path ratio is diagnostic; adding pitch modulation would duplicate propagation. No hidden clipping, normalization, panning or electrical processing belongs in this stage (contract sections 1, 4).
3. **Own streaming history explicitly.** One physical history per rotor serves its two receivers; horn/drum waveform histories remain separate. The existing 4,097-segment borrowed offline view is not an arbitrary-duration streaming queue. Preallocate capacity `ceil(Fs*rmax/c)+2+4`, maximum 16,384 waveform frames, and bounded rollback resources. Future reads and stale oldest-support reads must fail, not synthesize samples (propagation handoff next-phase section; contract sections 2-5).
4. **Make whole-call failure atomic.** Admit input ranges, timeline, buffers, aliases and ordered events before publishing any state. A late path/interpolation failure must preserve caller output, waveform/motion histories and diagnostics, with zero events consumed. Reset restores the initial silent epoch; stopped rate changes preserve current kinematics/commands but deliberately rebuild silent audio and discard tails. Flush length and moving state are explicit (contract section 5). These are R4 research policies, not observed hardware switching behavior.
5. **Retain exact independent parity evidence.** Test all interpolation fractions and polynomial degrees, ring boundaries/support availability, full static complex-delay grid, every admitted rate, at least ten seconds of independent same-cubic rendering, blocks 1/7/64/257/4096 and irregular partitions, all event boundary forms, nonzero-history rejection, receiver symmetries and all stopped-rate pairs. Preserve the frozen `2e-12` interpolation, `0.005` low-band diagnostic and normalized `2e-5` native/reference limits, actual errors and every failed high-band characterization (contract section 6).
6. **Keep R5/R6 and physical claims open.** The atlas distinguishes source/event aliasing, circuit integration, resampling and physical filtering. Oversampling a later stage cannot repair already folded input content; a high-rate reference must demonstrate convergence. ADAA also adds linear response/delay and is not a generic replacement for a coupled model (pp. 229-234). Thus same-cubic R4 parity is not ideal-delay accuracy, an alias-free audible policy, callback/deadline qualification or specimen fidelity. R5 needs separately frozen static/dynamic spectral budgets; R6 needs actual allocation/lifecycle/integration evidence. M4-M6, measured radiation/trajectory/geometry and held-out cabinet captures remain independent.

## Visual checks and remaining limits

The inspected original diagrams confirm chorus absolute-reference ownership (p. 171), the coupled root's two sweeps and delayed memory commit (p. 177), connected AO-28/feedback boundaries (pp. 200, 212), uncertainty as separate metadata (p. 225), two-way electrical boundary ownership (p. 242), and distinct fixed-circuit versus rotating-physical scanner reports (p. 250). These are explanatory diagrams, not netlists.

Page 182 contains a historical patent plate expressly labeled as an invention embodiment, not a verified selected production drawing. Page 194's text refers to a graph below, while the rendered page contains the valve photograph; no missing component connectivity was inferred from that reference. Page 185 visibly labels its four displayed nominal tap curves as a computed idealized model with no hardware measurement; the caption excludes rotation/depth switching. Pages 230-231 show explanatory alias-folding and ADAA linear-response plots. No graph-derived factory values or measured tolerances were imported.

## Executed work and next owner

Executed: source/contract hash checks, repository identity/status observation, complete sequential textual reading, selected Poppler rendering and visual review, and this evidence note. No build, DSP test, simulator, hardware measurement, fit, product change or publication was run. Historical results described by repository handoffs were read, not rerun by A03.

Useful reproduction commands, from the repository root:

```sh
sha256sum Hammond_B3_Leslie_Research_Atlas_500pp.pdf
sha256sum /workspace/scratch/e3cacb90cc81/atlas-text/part-3-169-250.txt
sed -n '1,500p' /workspace/scratch/e3cacb90cc81/atlas-text/part-3-169-250.txt
pdftoppm -f 171 -l 171 -singlefile -scale-to 1500 -png \
  Hammond_B3_Leslie_Research_Atlas_500pp.pdf /tmp/a03-atlas-p171
```

Continue the `sed` intervals listed in the coverage record without gaps. Repeat the render command for the listed selected pages if visual reinspection is needed; temporary renders are reproducible and are not physical captures.

**Next concrete task:** the integrator should freeze a reviewed R4 API/ownership contract and assign bounded waveform history, streaming trajectory retention, atomic renderer processing and an independent same-cubic oracle to separate owners. Acceptance should retain exact source/profile/oracle identities and all frozen section-6 evidence. A separate electronics/acquisition owner must establish the revision-specific M5/M6 ports before any later integrated or physical cabinet claim.
