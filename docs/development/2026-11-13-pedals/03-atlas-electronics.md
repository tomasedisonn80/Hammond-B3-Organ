# Assignment 03: atlas electronics and next numerical boundaries

Owner: /root/w01_a03_atlas_electronics

Wave: 1. Assignment: 03 of the new sixty-worker pedal session.

## Scope, source and actual reading

Read every page of **169-252 inclusive (84 pages)** of the preserved
[research atlas](../../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=169).
This is a fresh review for this session, not reuse of an earlier worker's
participation. Page numbers below are one-based PDF/printed atlas pages.
The inspected baseline was `b4fc61ccfcc59724f14fb0cee947ed7bb7142075`.

The full text was read from the integrator's `pdftotext -layout` extraction in
seven untruncated twelve-page groups: 169-180, 181-192, 193-204, 205-216,
217-228, 229-240 and 241-252. Python selected each group by its explicit
`=== PDF PAGE n ===` delimiter. There was no skipped page in this assignment.

Rendered and visually inspected pages **170, 171, 177, 182, 235 and 248** with
`pdftoppm -f N -l N -scale-to 1400 -png` and `view_image`; 170-171 were rendered
together. The depth table, return-reference equation, coupled-root equations,
descriptor signs, inventory boundaries and routing exceptions agree with the
extracted text. The diagrams on 171 and 177 are explanatory/algorithm views,
not connected schematics; their arrows cannot establish electrical endpoints.
The patent plate on 182 is explicitly an invention embodiment, not production
connectivity. This is complete text coverage with selected visual review, not
an independent inspection of every cited external source.

Also inspected [AGENTS.md](../../../AGENTS.md), [PLAN.md](../../PLAN.md),
[ERRATA.md](../../research/ERRATA.md),
[ATLAS_REVIEW.md](../../research/ATLAS_REVIEW.md), current next-step/handoff
guidance, the latest development-log outcome, `Engine.h`, the actual source-frame
and coefficient paths in `Engine.cpp`, and the tracked `data/` inventory.
No source, profile, binary or test was changed by this assignment.

## Complete chapter coverage

| Pages | Chapter | Implementation conclusion |
| --- | --- | --- |
| 169-174 | 027: vibrato/chorus switching | Two routing tablets and six selector modes are separate controls. Great includes pedals; percussion joins downstream. Ground-referenced chorus taps already contain their return once. |
| 175-180 | 028: WDF implementation | Eighteen LC sections expose nineteen outputs. Use the explicit wave convention, independently derived root elimination, and both original-equation residuals; the printed external-paper equations have reported inconsistencies. |
| 181-186 | 029: state-space alternative | Preserve one auditable endpoint graph, signed descriptor stamping and physical energy coordinates. Do not invert singular E or interpret algebraic constraint modes as physical poles. Compare all nineteen taps, not only mixed scanner output. |
| 187-192 | 030: scanner calibration | Separate module and complete-organ capture boundaries, one rotor-phase reference, complex sidebands, repeatability and held-out modes/takes. No physical captures are supplied. |
| 193-198 | 031: AO-28 topology | Keep eight sockets V1-V8, section identities, A/B/H branches, scanner driver/return and T3 output load. The stage registry is a scaffold, not a connected netlist. |
| 199-204 | 032: loaded linear network | Linearize the connected circuit at a stated bias/control/load. T3 turns ratio, leakage and magnetizing data remain unknown. Qualified reduction must preserve phase and port behavior as well as gain. |
| 205-210 | 033: nonlinear devices | Device families, units, domain, derivatives and terminal-current conservation need independent evidence. Trial solver iterations must not commit reactive history. A bounded fallback is degraded output, not a passed nominal fidelity case. |
| 211-216 | 034: interactions/headroom | Shared nonlinear stages process combined physical buses. Headroom belongs to stated voltage, routing, controls and load, not arbitrary host dBFS. Preserve bias, feedback and charge history. |
| 217-222 | 035: supply/noise | Keep one coherent mains reference, distinct physical injection paths and sample-rate-aware noise units. A loaded supply and a decorative ripple must not both own the same effect. |
| 223-228 | 036: aging/specimens | Keep topology, inspected condition, dated service history, run variation and uncertainty distinct. Calendar age and an arbitrary random seed are not evidence of physical component drift. |
| 229-234 | 037: antialiasing | Contact switching can alias before a downstream oversampled stage. All coupled state must share its internal clock. ADAA has its own response/delay and is not a general substitution inside a multi-device circuit. |
| 235-240 | 038: extraction/netlists | Eighty-five stock records and 124 electrical placements establish neither package count nor connected circuit. Preserve unit/label conflicts, alternate revisions and independent pin-to-net review. |
| 241-246 | 039: hybrid methods | Every reduced/measured block needs explicit ports, loading, validity domain, state and one owner for each embedded response. Fit residuals only at aligned calibrated boundaries and qualify independent holdouts. |
| 247-252 | 040: dry-organ acceptance | Keep source, contact/bus, scanner and final-organ probes. Exact documentary routing, numerical model equivalence and hardware fidelity are separate gates. Preserve a dry-organ regression after adding cabinet processing. |

## Constraints for the current pedal integration

1. **Preserve U, L, P and Q identities.** Pages 169 and 250 distinguish upper
   sustained U, lower sustained L, shaped pedals P and percussion Q. Great routes
   `L + P`; Swell routes U; Q remains downstream of scanner selection in every
   combination. A pedal is not a third manual and must not enter the upper ninth
   contact detector. Lower-manual Cancel is not a pedal panic.
2. **Keep the single source sample.** Page 248 requires collision branches to
   consume the same continuing waveform while retaining independent contact
   paths and gains. The current Engine calls `source_bank_.process_frame` once
   and separately adds the percussion contribution. A pedal implementation must
   consume this frame, never advance a second generator or process the Engine a
   second time.
3. **Do not conflate routing with voice calibration.** The pedal exceptions on
   page 248 are exact source assignments; that page explicitly keeps audible
   gain/waveform tolerances separate. The documentary 200-position map supplies
   no four-bus-to-two-control transfer. Any useful normalized mixture needs its
   own proposed identity, units, bounds, tests and replaceable boundary.
4. **Preserve legacy arithmetic deliberately.** At the inspected baseline,
   sustained upper/lower contributions are accumulated in one per-source
   `coefficients_` array. Future scanner routing needs separate division data,
   but splitting then summing can alter floating summation order. Keep the old
   no-pedal path or prove its intended compatibility with actual retained PCM
   comparisons. A changed order cannot be assumed bit-identical.
5. **Keep musical controls separate from physical history.** Pages 172, 184,
   226 and 252 require ongoing source/scanner/electrical state across controls
   and block changes. Pedal held/contact state should remain outside ordinary
   saved controls, and failed whole-call validation must not commit an owner or
   part of a gesture.
6. **Keep aliasing claims scoped.** The proposed binary/linear pedal routing
   fixture is an engineering reference. Pages 229-234 prohibit treating it as
   bandwidth-controlled switching or assuming later oversampling repairs
   already folded contact energy.

These points support the existing [next M3 gate](../../M3_NEXT_GATE.md); they do
not require postponing the useful nominal pedal runtime until measured electrical
voicing exists.

## A useful independent M4 boundary can proceed

After the pedal slice, a small **scanner routing and node-selection reference**
is dependency-ready as a separately named engineering deliverable:

- Accept explicit finite U/L/P/Q inputs and two Boolean tablet states; return
  wet/bypass/percussion branches without representing their physical voltage
  gains. Test all four route cases with distinct basis values so a wrong pedal
  destination cannot be hidden by a combined chord.
- Admit exactly six semantic selector modes, each selecting a depth and a
  chorus-return Boolean. There is no seventh historical Off selector value;
  bypass belongs to the tablets (169).
- Preserve the three nine-node maps from 170: depth 1 =
  `[1,2,3,4,5,6,7,8,9]`; depth 2 = `[1,2,3,5,7,9,11,12,13]`;
  depth 3 = `[1,2,4,7,10,13,16,18,19]`. Treat them as a reconstruction of the
  atlas's published-model transcription, with explicit 1-based node identity.
- A node-frame reader can consume nineteen synthetic ground-referenced inputs
  before the real ladder exists. Test equal-input unity, all selected indices,
  finite validation and atomic rejection. It is not a working physical scanner.
- If rotor interpolation is included, retain one independent continuing phase
  and explicitly resolve [E01](../../research/ERRATA.md). The inferred missing
  traversal entry is a declared source repair, not recovered factory wiring.

This boundary protects future pedal routing from being lost during an effects
integration. It does **not** close M4 and must not introduce a generic audio
delay chorus described as the circuit.

## Actual scanner circuit: ordered next numerical work

1. Reconstruct a revision-tagged endpoint graph and independently review it.
   Pages 175/181 specify **18 inductors, 18 capacitors and 19 observable taps**,
   not nineteen stages. Page 182 states early divider k branches **before Lk**
   and Ck follows Lk. Each port needs signed node pair, current direction, SI
   values, source impedance and receiver-load assumptions.
2. Prepare both electrical return topologies. Page 171 gives the published
   model's 22 kOhm chorus return. Reconstruct `v_k = r + z_k`; normalized scanner
   weighting already includes r once. Do not append another dry copy.
3. Retain a direct descriptor/AC reference and a separately implemented runtime
   realization. Page 179 asks for every output in both return states, first on
   a warp-matched grid, then at common physical Hz. Deep response zeros require
   a stated phase/magnitude floor. Independently converged transients need
   consistent input reconstruction and nonzero stored-energy cases.
4. Keep preparation/factorization outside processing. WDF leaves use
   `a=v+Rp*i`, `b=v-Rp*i`, `Rp>0`; capacitor reflection is a positive one-sample
   memory, inductor a negative memory (176). The coupled root in 177 uses
   `M=I-Phi*S11`, not a reordered product. Open/short/source constraints and
   the two defining root equations supply falsifiable tests.
5. Declare conditioning, residual, precision, state-transition and rate policies
   before qualification. Page 183 warns that unconstrained descriptor
   trapezoidal updates can preserve an unphysical alternating constraint error.
   Compare dynamic poles only after valid reduction. Stored capacitor voltages
   and inductor currents survive supported topology/rate changes; copying
   incompatible WDF wave memory does not prove this.
6. Only after numerical admission fit specimen loading, coil losses, overlap and
   rotor behavior. Pages 187-192 require identified captures and uncertainty;
   neither the atlas's historical algebra result nor an absent companion
   program can satisfy those gates.

The current `data/` inventory contains no scanner endpoint graph, component
registry, `scanner_ac_reference.py` or nominal response corpus. Their mentions
on 175/182/185/245 remain claims about absent companion material. Reconstruction
must be new, named work with independently executed evidence.

## AO-28 dependencies and unresolved evidence

M5 should retain three separate A/B/H entries, scanner-driver/receiver loading,
V4 expression/feedback and the V3B/T3 output boundary (193-204). The eight sockets
are V1/V2 6AU6, V3 12BH7, V4 12AX7, V5/V6 6C4, V7 12AU7 and V8 6X4. The theory
prose does not justify an extra output socket (195).

Before circuit export, obtain two agreeing pin-to-net traces for the selected
factory revision, resolve active values, retain separate P-D versus no-code
alternatives, and distinguish assembly callouts from electrical instances
(235-240). The duplicate redraw C56 conflicts with factory C59; unresolved
R62/other glyphs remain blockers on applicable active paths. A voltage annotation
must not become an unrelated ideal source. Unknown T3 ratio/inductances remain
unknown (201), and the chosen source/load plus volts-per-normalized-unit scale
must be explicit (199-204, 211).

Static device evaluators and bounded solvers are useful independent numerical
work only with an explicit fixture domain. No fitted tube model, device
digitization, identified transformer, whole-AO-28 connected solve, calibrated
headroom or specimen capture was produced by these chapters. Nominal DSP may
advance, but these gaps cannot be represented by measured labels or zero-valued
unknowns. Noise, aging and hybrid corrections likewise require their own
evidence and must not duplicate responses already embedded upstream.

## Actual result and handoff

- Completed fresh text coverage: 84/84 assigned pages, chapters 027-040.
- Completed selected visual checks: six pages named above.
- Inspected baseline source/frame/coefficients and relevant contracts; identified
  the compatibility and future division-boundary risks above.
- **No implementation or DSP tests executed in this assignment.** No inherited
  atlas/repository test is claimed as a newly run test. No hardware comparison,
  external-paper verification, commit or push was performed.
- Only this evidence note was added; the integrator owns shared plan/status,
  actual assignment accounting, implementation decisions and publication.

Recommended order is prepared pedal kernel, explicitly nominal playable pedal
integration with preserved bus identity, then scoped scanner routing/selection
and independently reviewed numerical topology. Keep complete M3, complete M4,
AO-28 fidelity and native-product qualification open until their own evidence
exists.
