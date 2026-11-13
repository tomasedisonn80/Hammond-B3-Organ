# Assignment 03: full atlas review, pages 169-252

## Identity, ownership and actual coverage

- Assignment: 03/60, wave 1/10; agent `/root/w01_a03_atlas_scanner_electronics`.
- Owned change: this note only. No production code, shared status, historical
  ledger, PDF, commit or remote ref was changed by this worker.
- Inspected starting commit: `6dc0702d5473912268e8af8f852b9b9984198ef3`;
  tree `a4f1d4b300de236436e22b748b1d4c46ed501ceb`.
- Source: root `Hammond_B3_Leslie_Research_Atlas_500pp.pdf`, 500 pages,
  21,248,265 bytes, evidence edition 12 November 2026. Independently checked
  SHA-256: `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
- Fresh text reading covered **every page 169-252 inclusive**, 84 pages,
  chapters 027-040. Supplemental text covered 157-159 and 163-168 to inspect
  the graph and traversal dependencies. Earlier review notes were not counted as
  this reading.
- Actual rendered-page inspection: **157, 158, 166, 170, 171, 175, 182, 183,
  184, 185, 186, 239 and 250**, using 1600-pixel Poppler PNGs. Full text
  coverage does not imply inspection of every image or of the external sources
  cited by the atlas.
- Read the standing instructions, plan/status/next-step context, current scanner
  gate and errata. The integrator owns the shared handoff and publication.

## Findings that control the next implementation

The dependency-ready work is an explicitly reconstructed nominal line graph,
an independently assembled numerical reference, a prepared physical-state
runtime and then the rotor/mode layer. The atlas requires fixed-tap circuit
agreement before rotating-response fitting (175-192). This review supports that
sequence. It does not close a hardware, complete AO-28 or complete product gate.

### Independent graph reading from the rendered atlas

Page 158's four-panel decomposition is legible and agrees with the candidate
graph in `docs/M3_REMAINING_AND_SCANNER_GATE.md`. Page 182 independently states
that divider k branches **before** Lk and Ck follows Lk. The graph is:

| Element | Positive endpoint | Negative endpoint | Value or constraint |
| --- | --- | --- | --- |
| Ideal drive | p0 | g | Imposed input voltage |
| Lk, k=1..18 | p(k-1) | pk | 0.5 H |
| Ck, k=1..17 | pk | r | 4e-9 F |
| C18 | p18 | r | 1e-9 F |
| Rk+, k=1..6 | p(k-1) | dk | Upper divider leg below |
| Rk-, k=1..6 | dk | r | Lower divider leg below |
| Rt | p18 | r | 15000 ohms |
| Rc | r | g | 22000 ohms |
| Return bypass | r | g | Closed for vibrato, open for chorus |

Page 157's rendered nominal table gives the six upper/lower resistor pairs,
in ohms: `(27000,68000)`, `(56000,150000)`, `(39000,150000)`,
`(33000,180000)`, `(18000,180000)`, `(12000,180000)`.
It preserves the printed kOhm/MOhm forms; those must not be interpreted as
SPICE's ambiguous `M` suffix (237).

The node set has 27 names: g, r, p0..p18 and d1..d6. There are 50 passive
elements: 18 inductors, 18 capacitors and 14 resistors; drive and switch are
separate boundaries. Outputs v1..v6 are V(d1,g)..V(d6,g); v7..v19 are
V(p6,g)..V(p18,g). The rendered panel explicitly states ground reference and
these output identities. Nineteen outputs are not nineteen LC stages,
nineteen rotating contacts or nineteen independent histories (158, 175, 181).

This is an independent comparison with the supplied atlas, **not** a fresh
comparison with the DAFx primary paper or a production schematic. The atlas
identifies its figure as an original decomposition of the paper's idealized
model. A separately consulted primary-source comparison and the selected
specimen's applicability remain open. Missing original companion graph/code
files cannot be treated as acquired evidence.

### Control and voltage boundaries

Pages 169-174 distinguish two routing tablets from the six-position selector.
Swell selects upper sustained U; Great selects lower sustained L plus shaped
pedals P. Percussion Q joins after the scanner in every case. Both tablets off
means no selected scanner input; it does not stop the shared phase/history.
The selector has six historical modes, without a seventh Off mode.

The rendered page 170 table gives these one-based output selections for nine
scanner terminals:

| Modes | Selected outputs |
| --- | --- |
| V1 / C1 | 1, 2, 3, 4, 5, 6, 7, 8, 9 |
| V2 / C2 | 1, 2, 3, 5, 7, 9, 11, 12, 13 |
| V3 / C3 | 1, 2, 4, 7, 10, 13, 16, 18, 19 |

Ground-referenced tap voltage is `v_k = r + z_k`, with z measured relative to
the line return. Complementary scanner weights already include r once.
Adding another dry copy or treating chorus as a universal 50:50 mix changes
this circuit (171, 250). The ideal line, AO-28 input/output impedances and
normalized engine amplitude must remain separately identified boundaries;
no calibrated volts-per-full-scale conversion is supplied (175, 194-204, 211).

### Traversal discrepancy confirmed visually

The actual code on rendered page 166 prints:

```text
[0,1,2,3,4,5,6,7,8,7,6,5,4,3,2]
```

It simultaneously indexes `floor(16*phaseTurns)` and wraps modulo 16. Counting
the printed list gives 15 entries. Appending `1` gives the 16-position
forward-and-return traversal consistent with the paragraph requiring terminal
2 to blend back to terminal 1 at wrap. This is a documented inference, not
independently recovered primary wiring. Keep erratum E01 and an explicit
inferred-model identity until that primary-source gate is closed.

Page 163's documented nominal 412 rpm gives `412/60` Hz. Neither six hertz
nor a separately reset phase per manual is supported. The baseline on 165-168
assumes two adjacent capacitive overlaps, negligible ladder loading and a
constant overlap-capacitance sum. It is not a sequence of metallic tap
switches. The loaded extension must retain `d(C*v)/dt`, including changing-C
terms, and cannot normalize away real angle-dependent gain.

## Numerical implications

Pages 182-186 specify signed incidence, volts/amperes and separate algebraic
unknowns versus stored energy. The descriptor capacitance matrix may be
singular: do not compute inverse(E). Contract the ideal return short or enforce
its constraint. The raw trapezoidal descriptor recurrence can retain
nonphysical alternating constraint error; reconstruct algebraic variables or
eliminate them before interpreting poles.

Use one convention for all reactive branches. At internal sample interval h,
the stated recurrence uses `M=E/h+K/2`, `N=E/h-K/2` and both input endpoints.
The bilinear analog comparison frequency is `Omega=kappa*tan(omega_d/2)`.
First compare at that warp-matched frequency to expose topology/sign errors;
then compare at the same physical hertz to report discretization error
(178-179, 183). A prewarp choice is a numerical setting, not a factory constant.

Preparation owns matrix scaling, factorization and state-conversion maps.
Runtime work has fixed dimensions, no allocation or symbolic elimination, and
a bounded rejection path. Mode changes preserve compatible capacitor voltages
and inductor currents, then reconstruct algebraic variables. Depth changes
alone leave line state intact; rate changes preserve physical state and angle
(172, 184). Fixed-network energy tests need zero supplied source power; switches
and sources have a separate energy account (159, 180, 185).

The atlas proposes a scaled residual below 1e-9 for well-conditioned binary64
synthetic fixtures (186). This is not a hardware tolerance. The response gate
needs all 19 signed taps, input current/loading, both returns, conditioning,
step/impulse/multisine and nonzero initial energy. Exclude phase/group-delay
bins by a declared magnitude/excitation floor before grading deep nulls
(179, 185-192). A final scanned waveform alone can conceal a bad tap sign.

### Separately derived physical-coordinate reduction

The following is this worker's derivation from the above ideal graph, not a
new statement attributed to the atlas. It is offered as a checkable path for
the runtime implementer, with a separately stamped AC oracle still required.

Let `x_k=V(pk)-V(r)` for k=1..18, and let `i_k` flow through Lk from
p(k-1) to pk. Define `D_k=Rk+ + Rk-` for k=1..6. The 36 physical
coordinates are x and i. For vibrato `r=0`. For chorus the whole-line KCL
and ideal source give:

```text
I_in = i_1 + (u-r)/D_1
r/Rc = I_in
r = Rc/(Rc+D_1) * u + Rc*D_1/(Rc+D_1) * i_1
```

With `p_k=x_k+r` and `p_0=u`, the physical derivatives follow directly:

```text
L_k * di_k/dt = p_(k-1) - p_k
C_k * dx_k/dt = i_k - i_(k+1) - x_k/D_(k+1)  [k=1..5]
C_k * dx_k/dt = i_k - i_(k+1)                 [k=6..17]
C_18 * dx_18/dt = i_18 - x_18/Rt
```

The divider outputs reconstruct as
`d_k=r+(p_(k-1)-r)*Rk-/D_k`. This explicitly retains common return and all
36 energy coordinates while avoiding algebraic-state advancement. Ideal
source/load assumptions make the reduction specific to this fixture; adding
winding losses, coupling or receiver loads requires a new derivation.

An in-memory Python check exercised 100 deterministic random instantaneous
states in each return topology (seed 30169). It checked return KCL and
`dE/dt = u*I_in - resistor_dissipation` from the stated branch formulas.
Maximum absolute return/current residual was `4.87890977618477e-19` A;
maximum energy-rate residual was `6.938893903907228e-18` W. These are
algebra checks on synthetic states, not time integration, AC parity, passivity
of an eventual numerical realization or hardware evidence.

Independent `fractions.Fraction` arithmetic also reproduced:

- Parallel DC resistance: `92438660160000/9455738267` ohms,
  approximately `9775.932618884532` ohms.
- Chorus DC return/input ratio: `9455738267/13657495547`, approximately
  `0.6923478931008726`.
- First six vibrato DC gains: `0.7157894736842105`, `0.7281553398058253`,
  `0.7936507936507936`, `0.8450704225352113`, `0.9090909090909091`,
  `0.9375`; taps 7..19 are unity.
- The 7075 Hz/44100 Hz prewarp example gives effective period
  `24.813259428098718` microseconds. Incorrectly using 7075 radians/second
  gives `22.724498246084217` microseconds, confirming the units distinction
  in page 178 without inheriting its claimed external execution.

## Complete assigned chapter digest

| Pages / chapter | Findings retained for the whole project plan |
| --- | --- |
| 169-174 / 027 | Two tablet routes, six semantic modes, one wet history, Q downstream, return once; actual routing/transition captures absent. |
| 175-180 / 028 | Coupled 18-L/18-C network; WDF leaf/root signs and prewarp require independent derivation. The reported 100-matrix algebra fixture is not a scanner pass. |
| 181-186 / 029 | Graph before reduction; singular descriptor/rank handling, physical state, all-tap AC and converged transient evidence, explicit residual/conditioning and hardware gates. |
| 187-192 / 030 | Scanner-module and whole-organ captures differ; complex stationary response precedes phase-resolved sidebands; one shared rotor reference and held-out complete takes/modes. No chapter hardware captures. |
| 193-198 / 031 | Eight AO-28 sockets V1..V8; V3A line drive and V3B transformer output share an envelope but not invented distortion. A/B/H routes, revision-specific graph and calibrated ports precede nonlinear models. |
| 199-204 / 032 | Connected loaded linear reference includes expression/feedback, T3 and receiver. Transformer ratios/inductance remain unknown; numerical and hardware agreement are different gates. |
| 205-210 / 033 | Device surfaces need units, fitted domain, slopes, terminal-current conservation and screen/grid behavior. Stable softplus and bounded trial/commit solving do not establish instrument parameters. |
| 211-216 / 034 | Physical headroom depends on routing, excitation and load. Shared nonlinear stages follow actual summing; preserve bias, feedback and stored charge. No universal clipping/drive constant. |
| 217-222 / 035 | Supply/noise are connected voltage/current sources with one coherent mains phase. Noise variance depends on rate/bandwidth. Nominal residue, condition defects and capture faults remain distinct. |
| 223-228 / 036 | Factory identity, inspected configuration, dated condition and service events are separate. Age is not a calibrated parameter; uncertainty is not automatically audible randomness. |
| 229-234 / 037 | Locate alias creation before choosing rate; preserve internal event/source clocks and reactive histories. ADAA is a distinct operator and needs stateful derivation. Toy cubic checks do not qualify AO-28. |
| 235-240 / 038 | Inventory, placements and netlist are different artifacts. Preserve units/revision namespaces, C59 versus duplicated redraw C56, and unresolved active values. A second trace is required. |
| 241-246 / 039 | Every reduced/measured block needs a physical boundary, load, memory and ownership contract. Residual learning requires actual captures and cannot hide topology/scale mistakes. |
| 247-252 / 040 | Validate the complete dry organ before Leslie; dry includes scanner. Cross six modes with four tablet states and separate U/L/P/Q basis signals; retain documentary, numerical and hardware results independently. |

## Commands, results and limitations

Working directory for all commands was
`/workspace/scratch/1742da7072be/Hammond-B3-Organ`.

- `cat AGENTS.md`, `pdfinfo Hammond_B3_Leslie_Research_Atlas_500pp.pdf`,
  `sha256sum Hammond_B3_Leslie_Research_Atlas_500pp.pdf`, `command -v pdftotext`
  and `command -v pdftoppm`: passed; identities/tools reported above.
- `pdftotext -f FIRST -l LAST -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -`
  ran for `169:186`, `175:180`, `187:198`, `199:210`, `211:222`,
  `223:234`, `235:246`, `247:252`, `157:159`, `163:168`, and `158:158`.
  The initial combined output was truncated; the smaller repeated batches
  recovered all omitted assigned scanner pages. The later 158-only read
  recovered the truncated supplemental paragraph. No assigned pages were skipped.
- A Python subprocess loop ran `pdftoppm -f PAGE -l PAGE -scale-to 1600
  -singlefile -png` for the 13 explicitly listed visual pages. All succeeded;
  every generated page was opened with `view_image`. Temporary images remain
  outside the repository at `/tmp/hammond-w01-a03/` and are not deliverables.
- `git rev-parse HEAD HEAD^{tree}` and `git status --short` identified the
  base and the concurrently created scanner-note directory; unrelated work was
  preserved.
- In-memory Python standard-library arithmetic checked the DC fractions,
  traversal counts, prewarp units and 200 synthetic physical-state KCL/energy
  identities described above. No numerical engine or external simulator ran.
- `git diff --no-index --check /dev/null` against this new note reported no
  whitespace diagnostics (exit 1 for the new-file difference). The integrator
  retains responsibility for the final staged repository check.

No new primary-source paper, factory drawing, original companion, physical
measurement, actual host/device run or fitted component profile was acquired
by this assignment. In particular, loading, coil loss, stray/mutual coupling,
finite switching, absolute voltage scale, overlap capacitance and specimen
speed remain unresolved physical inputs. This report closes its reading and
atlas-comparison task only. The next worker can author the nominal graph and
strict compiler using these endpoints while retaining the independent
primary-source, numerical and specimen gates.
