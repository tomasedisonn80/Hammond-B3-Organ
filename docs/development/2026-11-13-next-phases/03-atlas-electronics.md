# Assignment 03: atlas electronics and dependency review

## Identity, scope and result

- Actual worker: `/root/w01_a03_atlas_electronics`.
- Session: `2026-11-13-next-phases`, wave 1, assignment 03.
- Owned path: this note only. No core, scanner, build, shared status or historical
  session files were modified; no commit or push was attempted by this worker.
- Inspected checkout: `ba0d9c9c75bd7a39152470f9f7ddb82287cb01b1`, tree
  `51fd7b24d2f373a693ced8dbde0fba762a3cc434`.
- Coverage: every page of the assigned inclusive PDF range **169-252**, 84 pages,
  containing chapters 027-040. This is a new reading for this session.
- Result: the AO-28 sequence and its missing inputs are clear. A connected AO-28
  runtime cannot be honestly reconstructed from the printed functional diagrams
  or tube roster alone. An independent standalone adapter is a useful next
  product slice while the other session continues scanner work. AO-28 evidence
  admission and source tracing can proceed independently as a separate M5 task.

The source is the unchanged [research atlas](../../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf),
500 pages, 21,248,265 bytes, SHA-256
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
Page citations below refer to one-based PDF pages, matching the printed numbers.

## Complete assigned chapter coverage

| PDF pages | Chapter | Implementation contract and evidence limit |
| --- | --- | --- |
| 169-174 | 027: switching | Swell routes upper sustained material; Great routes lower sustained plus shaped pedals. Percussion remains downstream. Six modes have no seventh OFF selector state. Both tablets off must not reset scanner phase/history. Absolute chorus tap voltages already contain the common return once. |
| 175-180 | 028: WDF | Eighteen LC sections and nineteen observable taps are different counts. Preserve port directions, source/root coupling, reactive signs and the explicit radians/hertz convention. Published algebra inconsistencies require independent derivation. Toy algebra checks do not establish a whole circuit or hardware pass. |
| 181-186 | 029: state space | Preserve one literal graph before reduction; 36 possible energy coordinates are not inferred from nineteen outputs alone. Algebraic constraints, loading, residual conditioning and physical-state migration need explicit treatment. One-frequency prewarping cannot correct the entire frequency grid. |
| 187-192 | 030: scanner calibration | Separate module captures from full organ output. Use a shared rotor reference, signed complex sidebands, phase-aware comparisons and held-out frequencies/modes. Factory nominal 412 rpm is documentary, not a newly measured rate. No physical captures were acquired for this chapter. |
| 193-198 | 031: AO-28 topology | Exactly V1-V8 for the selected drawing; V3A drives the line and V3B drives T3. V4 surrounds expression. A/B/H inputs and the scanner loop stay distinct. Socket/section registry is a scaffold; complete connected graph and operating point remain separate requirements. |
| 199-204 | 032: linear AO-28 | Linearize one loaded, connected circuit, including feedback and explicit source/load conditions. T3 winding ratio, losses, magnetizing/leakage and capacitance require evidence. Preserve both output legs and differential/common-mode meanings. Numerical and physical acceptance are distinct. |
| 205-210 | 033: nonlinear valves | Use family-specific terminal-current laws with voltage domains, signs, units and derivatives. Pentode screen current is an explicit port. Stable softplus and bounded Newton trials are numerical requirements. GE typical values are dimensional checks, not actual AO-28 bias or fitted coefficients. |
| 211-216 | 034: headroom | Sum signals where the connected circuit sums them before nonlinear processing. Preserve shared bias, feedback and charge histories. Internal volts-per-normalized-unit and host gain are separate. Headroom depends on excitation, controls and receiving load; no universal clipping threshold is supplied. |
| 217-222 | 035: supply and noise | Preserve T7, V8 and connected RC rail states or name an explicitly reduced surrogate. Shared mains phase and physically scaled noise must survive block/rate changes. Do not add decorative ripple twice. Supply/noise amplitudes and physical captures remain unknown. |
| 223-228 | 036: condition profiles | Separate identity, inspected configuration, dated condition and service events. Age is metadata, not an automatic distortion/noise model. Uncertainty is not audible randomness. Immutable before/after profiles preserve source and measurement ancestry. |
| 229-234 | 037: alias control | Separate source/contact/control, solver and decimation errors. Keep connected feedback on one internal clock. ADAA has its own response/delay and is not a generic replacement for a coupled tube circuit. Rate labels and toy cubic results cannot close the instrument alias gate. |
| 235-240 | 038: circuit extraction | The atlas describes 85 assembly records and 124 electrical placements, explicitly without complete connectivity. Keep stock, drawing and simulator namespaces distinct. Require reviewed units and a second terminal trace. Preserve conflicting readings and alternate revisions rather than merging them. |
| 241-246 | 039: model selection | Every block owns a declared boundary, physical responses once, persistent state and numerical validity domain. A one-way audio cascade approximates two-way electrical loading. Residual/learned models require actual captures and holdout validation. Complete the direct organ path before integrated Leslie fitting. |
| 247-252 | 040: dry-organ gate | Here dry means before Leslie/room, and includes scanner plus AO-28. Preserve source, bus, scanner-return and final organ diagnostics. Use one absolute event timeline across rates/blocks. Documentary, numerical and hardware gate results must be separate and retained. |

## Important visual inspections

Actual PDF pages 194, 200 and 239 were rendered with Poppler at 1,500-pixel
maximum dimension and inspected as images, not inferred from extracted text.

- **Page 194:** the prose says a graph appears below, but this rendered page
  displays a 12AX7 photograph. No complete circuit or functional graph can be
  recovered from that photograph. The accompanying text itself limits its
  intended graph to functional dependencies, not component connectivity.
- **Page 200:** the visible graph is an original dependency view with source
  impedance, scanner boundary, V4/expression, tone/output, T3/load and feedback.
  Its caption explicitly says it is not component connectivity. Its arrows
  cannot be promoted into a complete schematic netlist.
- **Page 239:** the source-conflict table is legible. It retains factory C59
  versus the redraw's duplicated C56, the repeated 6-6-43 callout, unresolved
  item-47 resistance and the separate no-code-letter AO-28 branch. These are
  distinct evidence issues, not an instruction to guess convenient values.

This assignment visually checked these selected pages only. It does not claim
an independent visual rereading of every referenced factory schematic or chart.

## Concrete M5 dependency gate

The order specified on pp. 196, 198, 202 and 235-240 is:

1. Choose one explicitly named documentary AO-28 revision, retaining unknown
   specimen identity and unselected alternatives.
2. Acquire the actual factory Figure 24 and source parts documents, record their
   hashes/pages, and trace the complete pin/net graph. Require an independent
   second trace before admitting active connectivity.
3. Keep physical packages, valve sections and electrical components distinct.
   The eight-socket roster does not imply eight computational stages.
4. Validate SI values, port polarity/reference, source/load contracts, shared
   rails, feedback and revision exclusivity. Unresolved active values block
   numerical export; transformer unknowns remain explicit.
5. Establish connected operating points and loaded small-signal AC/port tests,
   then a prepared runtime realization with physical-state continuity.
6. Add the device models and bounded nonlinear solve after the linear reference,
   retaining its small-signal limit and separately verifying alias error.
7. Grade physical agreement only against admitted, calibrated held-out captures.

At the inspected checkout, `rg --files data` shows no AO-28 netlist, stage registry,
component-placement registry or the atlas's named `038-ao28-bom.json` companion.
Searching `include`/`src` found statements that existing models are nominal and
not complete AO-28 circuitry, not a hidden AO-28 implementation. The missing
companions cannot be treated as acquired source data merely because the atlas
describes their contents. New reconstructions must retain their own identity.

## Recommended independent scope for this session

**Prefer an optional standalone product adapter using the existing nominal core**
if the parent selects product work. It does not require inventing AO-28 or Leslie
parameters and can coexist with scanner development. It should consume the
existing parameter/state/input contracts rather than fork the DSP implementation.
The atlas's relevant constraints are the immutable runtime plan and persistent
ownership on p. 244, and exact event timing/block partitioning on p. 252; the
product chapters assigned to the other reader must supply the UI/device details.

Predeclare useful acceptance before implementation:

- A known MIDI/control stream delivered through the standalone boundary agrees
  with the same event timeline processed by the core, including upper/lower/pedal
  routing, overlapping owners, state restore and panic/disconnect behavior.
- Audio-device setup, buffers, UI, serialization and file access remain outside
  processing; the selected callback path has bounded work and a calibrated
  allocation probe. Callback errors produce explicit status and bounded output.
- Closing an editor, changing a visual view or moving a window does not alter
  source phase, note ownership or audio routing.
- Device stop/restart and supported sample-rate changes preserve the documented
  lifecycle. A failed device open is distinguished from a failed DSP test.
- Tests use the actual adapter executable and its supported backend. A dummy/null
  backend establishes only its named scope; successful real hardware output and
  deadline/underrun claims require actual device evidence.
- State compatibility, all existing public parameters and historical dry renders
  remain intact; new product settings have an explicit independent contract.

If the parent chooses M5 instead, the dependency-ready deliverable is source-traced
evidence/graph admission and independent documentary comparison, followed only by
the numerical subset whose active connections and values have actually been
resolved. A generic saturation block is not a substitute for that sequence.

An isolated proposed rotary research module could be developed at a declared
synthetic boundary, but must not be called an integrated, validated Leslie phase.
Pages 246-252 explicitly retain the complete direct-organ gate before cabinet
integration and fitting. The currently named nominal dry engine covers a narrower
boundary than the atlas's complete dry-organ definition on p. 247.

## Commands and verification actually executed

Working directory: repository root `/workspace/scratch/5ba97739b54c/Hammond-B3-Organ`.

- Read `AGENTS.md`, README, plan/status/next-steps context, current scanner
  handoff, atlas-review record and the latest development-log entries.
- Read the entire extracted range from
  `/workspace/scratch/5ba97739b54c/atlas/part3.txt`: an initial character chunk,
  then complete page groups 178-192, 193-207, 208-222, 223-237 and 238-252. Page
  178 was deliberately reread in full after the first chunk ended mid-page.
  Later reads collapsed layout whitespace only; no paragraph content was omitted.
- Ran `git rev-parse HEAD HEAD^{tree}`, `git status --short`, `rg --files data`
  and the bounded source search described above.
- Recomputed the source PDF byte count and SHA-256 with Python `hashlib`.
- Rendered pages 194, 200 and 239 using
  `pdftoppm -f PAGE -l PAGE -singlefile -scale-to 1500 -png` and inspected them
  with `view_image`. Temporary images remain outside the repository.
- No compiler, runtime, unit-test, audio-device, hardware or external-source
  qualification was executed by this read-only assignment. No such pass is
  inferred from the atlas's prose or previous sessions' results.

The integrating agent owns acceptance of this note, current-session accounting,
scope selection and shared handoff updates. All scanner ownership remains with
the concurrent session until explicitly integrated by the parent.
