# A03 — complete atlas electronics reading

## Identity and coverage

- Actual agent: `/root/w01_a03_atlas_electronics`; wave 1, assignment A03.
- Inspected source: `647ae1b2b6ad8d30ee28ab348b94f974fb6aadbb`.
- Read the complete `AGENTS.md` and `docs/PLAN.md`, then **every page 169–252 inclusive**: chapters 027–040, 84 pages. Reads used consecutive 12-page text batches; page 173 was reread separately after output truncation. This is complete textual coverage, not a new independent visual transcription of the cited factory drawings.
- Unchanged PDF SHA-256: `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
- Assigned page-extract SHA-256: `351ad8d4cc158d8934f844dc12ba7cfd5d62c7b5b86e4f6caa6ae3c16cc5eb65`.
- Reviewed current `ScannerLine`/`ScannerRotor` APIs, line preparation implementation, Engine rendering, independent transient reference, scanner numerical contract/AC parity/handoff, model metadata and current next steps. No build or runtime experiment was performed; no product source changed.

## Requirements recovered from all fourteen chapters

| Pages / chapter | Implementation requirement and evidence boundary |
| --- | --- |
| 169–174 / 027 | Swell routes U, Great routes L+P; Q joins downstream. Six selector modes have no OFF position. One scanner phase/history continues with both tablets off. Chorus return is included exactly once. |
| 175–180 / 028 | Eighteen LC sections produce nineteen observable taps. Preserve signed wave conventions, coupled instantaneous source/switch solve, explicit prewarp units and physical state. Printed algebra/leaf inconsistencies require independent derivation. The atlas's algebra examples do not validate a complete circuit. |
| 181–186 / 029 | Keep audited endpoint incidence, 36 potential energy coordinates, physical state reconstruction and loaded output polarity. Do not invert singular descriptor E. Distinguish input reconstruction, algebraic constraints and analog versus discrete response. |
| 187–192 / 030 | First qualify static line, then shared rotor phase/complex sidebands, then withheld physical captures. Preserve uncertainty, calibration and quiet-state residue. No hardware captures were supplied. |
| 193–198 / 031 | AO-28 has V1–V8, including separate V3A line drive and V3B T3 output; no extra tube resolves contradictory prose. A/B/H entries, scanner return and expression remain connected electrical boundaries. Socket registry is not a netlist. |
| 199–204 / 032 | Build a connected loaded small-signal reference at declared bias before nonlinear fitting. T3 needs winding polarity, load and independently evidenced parameters. Unknown turns ratio/inductance remain unknown. |
| 205–210 / 033 | Family-specific voltage/current models require supported domains, conserved terminal currents and checked Jacobians. Use stable softplus and bounded iterative solves; only accepted trials commit histories. Generic waveshaping is insufficient. |
| 211–216 / 034 | Nonlinear processing follows actual shared buses and feedback. Host gain cannot redefine valve drive. Preserve bias/charge recovery and zero fallback events in accepted fixtures. No universal headroom is established. |
| 217–222 / 035 | Supply rails and noise injection have specific owners/units. Share mains phase, preserve seeded stochastic histories, and retain physical noise bandwidth across rates. Do not add arbitrary sag or double-count ripple. |
| 223–228 / 036 | Factory identity, inspected topology, dated condition and service events are distinct. Calendar age does not imply electrical drift. Keep immutable as-found/restored evidence; uncertainty is not automatically audible randomization. |
| 229–234 / 037 | Budget source/contact/nonlinear/decimation errors separately. Keep coupled feedback on one internal clock. ADAA changes low-level response/delay; oversampling alone proves neither fidelity nor convergence. |
| 235–240 / 038 | The cited 85 stock records and 124 placements are different inventories, neither connectivity-complete. Preserve namespaces, unknown quantities and alternate circuits. Factory C59 conflicts with the redraw's duplicate C56. Active unresolved values block numerical export. |
| 241–246 / 039 | Choose representations at explicit loaded ports; each physical response occurs once. Reduced/learned blocks need domains, state, source/latency identities and held-out evidence. Complete direct organ validation precedes qualified Leslie integration. |
| 247–252 / 040 | Retain source/bus/scanner/final-organ diagnostics, absolute event timing and block invariance. Issue separate documentary, numerical and hardware dry-organ gates. Atlas “dry” includes scanner and AO-28 before the cabinet; today's nominal dry prototype does not complete that target. |

## Current gaps and useful next tasks

`ScannerLine` implements a separately identified 36-state trapezoidal nominal line; `ScannerRotor` supplies the continuing six-mode observation. Engine currently sums nominal source/contact/percussion/pedal contributions and applies expression/output gain, without scanner, AO-28 or Leslie processing. No complete AO-28/Leslie electrical model appears in `src`, `include` or `data`.

The retained G3 frequency/process qualification passes, while G5 same-hertz fails every allowed researched rate, including 1,536,000 Hz. Do not replace that result with an assumed 16× pass, retune components, add unmeasured damping or connect the research line as qualified live audio.

1. **Dependency-ready M4:** build an independent combined line/rotor research module, leaving Engine unchanged. Acceptance: all six modes/four tablet combinations; Q outside modulation; one clock; chorus return once; precharged state/rate transitions; atomic failure preservation and subsequent continuation; partition invariance; bounded storage and calibrated allocation checks. Compare to the independently stamped transient reference with identical input reconstruction.
2. **Following G5:** investigate a distinctly identified numerical realization under unchanged physical graph/budgets; retain all failed bins and qualify transients, rotating sidebands and actual resampling/latency separately.
3. **M5 documentary preparation:** acquire the selected factory schematic and independently trace component endpoints/revisions. Admit source/load/polarity and unresolved T3/device fields before numerical export. Do not fabricate the atlas's absent companion files or calibrated tube parameters.

These tasks are independent of the other session's R4 rotary waveform ownership. UI work may proceed while these sound gates remain open; its labels and README must continue describing the actual nominal audio path.
