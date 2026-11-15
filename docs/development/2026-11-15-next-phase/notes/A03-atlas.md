# A03 - Atlas pages 168-250 and scanner numerical continuation

**Assignment:** `/root/w01_a03`, wave 1, 15 November 2026.
**Observed checkout:** `/workspace/scratch/116ca0948095/Hammond-B3-Organ`.
**HEAD:** `138fca9af7feca46d10b0e2b65d891f4751a3904`; tree `d26e7ca86197750629b5e6f85fc548e03a815dd8`.
**Owned deliverable:** this note only. No shared source edit, configure, build, CTest run, index change, commit, fetch or publication was performed.

## Recommendation

**Proceed with a substantive, separately identified scanner FOH realization and a prepared host/internal-rate research pipeline.** The reviewed ideal graph, independent nodal reference, physical-state coordinates and frozen G5 budgets are available. This work does not need new physical measurements to compare numerical realizations. It is independent of the fidelity owner's M6 FOH, native MIDI checked-close and native deck work, and of the waveform owner's R4.

An executed in-memory feasibility experiment supports this choice: an exponential first-order-hold realization of the unchanged 36-state scanner passes the stationary same-Hz budget at every frozen positive-frequency/tap case in both return modes from **352,800 Hz** upward among the allowed rates. Existing bilinear v1 still has its recorded failure even at 1,536,000 Hz. The experiment is a candidate screen, **not a native implementation or full G5 pass**. Its remaining input-reconstruction error and the real interpolation/decimation policy must be qualified explicitly.

Use **16x host rate as the first complete rotating-output candidate**, subject to independent contract review and measured cost. The 8x candidate is worth retaining for cost comparison; its stationary result alone leaves less margin for rotating waveform and sideband budgets. Do not enlarge the allowed multiplier set, retune components, add unmeasured damping, change tolerances or reinterpret the old v1 failure. Keep Engine integration as G6 after the new G5 evidence passes.

## Reading and source identity

I read the entire live `AGENTS.md` (501 lines), complete `docs/PLAN.md` (272 lines), and this session's README. I recovered its checkpoint and six initial assignment records, current README/status/next-steps/handoff navigation and the latest development-log entry. Their older product-publication language is historical relative to the live next-phase routing; root owns its reconciliation. I inspected local HEAD/tree, status and configured remote, but made no live remote query.

I **personally read every page 168-250 inclusive**, using the complete form-feed-delimited text for each page. No preceding session's atlas summary substituted for this reading. The extraction has 501 chunks, 500 nonempty pages; all 83 assigned chunks are nonempty and contain their matching `N / 500` page footer.

| Input | Bytes | SHA-256 |
| --- | ---: | --- |
| Original `Hammond_B3_Leslie_Research_Atlas_500pp.pdf` | 21,248,265 | `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769` |
| `/workspace/scratch/116ca0948095/atlas/atlas.txt` | 1,298,588 | `e6ed8ed76663a8f12c487ae1e4d3ab69facc36971df240a15b1ba36eeb22485d` |
| Pages 168-250, joined with form feeds and one final form feed | 219,114 | `d9d27fe0d38f310a6fc1ecef914860a23c47511e881c01fdbb420569ad426a86` |

`pdfinfo` reports 500 A4 pages. Direct `pdftotext -f 168 -l 250 -layout <original.pdf> -` output was **byte-identical** to that assigned slice. I rendered and viewed original PDF pages **171, 177, 182, 194, 213 and 239** at 1,400-pixel maximum dimension. The p.171 return-voltage diagram and p.177 root-solve diagram reinforce the reference/state boundaries. Page 182 contains a historical patent mechanism plate, not a verified late-B-3 production netlist. Page 194's visible illustration is a valve photograph despite prose referring to a graph; it supplies no missing AO-28 endpoints. Pages 213 and 239 were visually checked for shared-bias/feedback and source-conflict text. These observations do not independently validate the atlas's underlying external source documents.

### Complete assigned coverage

| PDF pages | Chapter/content read | Consequence for the proposed work |
| --- | --- | --- |
| 168 | 026, scanner mechanism acceptance | Common-signal, one-hot support, continuing phase and higher-rate tests precede physical overlap claims. |
| 169-174 | 027, switching matrix | Four tablet routes, six modes, exact maps, one line/rotor history, percussion downstream and chorus return exactly once. |
| 175-180 | 028, WDF formulation and errata | Eighteen LC sections are distinct from nineteen outputs; preserve sign/unit/root derivation and separate mapped-frequency from same-Hz checks. |
| 181-186 | 029, state-space alternative | Preserve literal endpoints, physical energy coordinates, coupled loading, initialization, scaled residuals and independent transient convergence. |
| 187-192 | 030, scanner measurement/calibration | Full rotation and signed sidebands need one phase reference; numerical tests cannot replace unacquired specimen captures. |
| 193-198 | 031, AO-28 sockets/topology | V1-V8, V3A/V3B and A/B/H paths are distinct; registry is not a complete connected circuit. |
| 199-204 | 032, AO-28 linear network/transformer | Source/load conditions, bias, C22 feedback, expression and T3 multiport behavior must be explicit before fitting distortion. |
| 205-210 | 033, valve laws/solver | Device units/domains, current conservation, derivatives, bounded trial/commit and small-signal evidence are separate gates. |
| 211-216 | 034, connected nonlinear interactions | Shared bus nonlinearities, bias/supply histories and calibrated volts cannot be replaced by per-note saturation or arbitrary drive. |
| 217-222 | 035, supply/hum/noise | Shared mains phase, rail states, calibrated noise bandwidth and source ownership are required; unknown amplitudes remain unknown. |
| 223-228 | 036, condition profiles | Revision, service state, specimen variation and uncertainty stay separate; age is not a physical parameter law. |
| 229-234 | 037, oversampling/antialiasing | Rate conversion, state timing, passband/stopband response, transport latency and independently converged reference are deliverables. |
| 235-240 | 038, inventory/connectivity/provenance | 85 stock rows and 124 placements do not establish a netlist; preserve variants, SI conversions and C59/C56 and other source conflicts. |
| 241-246 | 039, hybrid boundaries | One owner per effect; candidate reductions retain ports, memory, validity domain and their detailed offline reference. |
| 247-250 | 040, dry-organ validation | Retain source/bus/scanner/organ diagnostics; cross six modes with four routes, keep Q downstream and do not hide errors with cabinet processing. |

## Current source assessment

I read `include/hammond/ScannerLine.h`, `src/ScannerLine.cpp`, `include/hammond/ScannerRotor.h` and `src/ScannerRotor.cpp`, plus the full scanner numerical contract, AC parity and transient-reference/acceptance documentation. I inspected `tools/scanner_ac_reference.py`, authoring data structure, qualifier boundaries and source searches for AO-28 implementation.

The current line is explicitly `scaled-physical-trapezoidal-scanner-line-v1`, not an AO-28 model. It prepares both 36-by-36 operators outside processing and stores 18 capacitor differences, 18 inductor currents, previous input and frame count. It reconstructs early dividers from pre-inductor nodes, the common return, all 19 signed taps, input current and physical energy. The two-endpoint recurrence is `x_new = T*x_old + b*(u_previous + u_current)`. Rejected processing prepares a candidate and commits only after state and output admission. Stopped-rate reconfiguration preserves the physical checkpoint.

The rotor keeps the three exact atlas p.170 maps and completed sixteen-position traversal `[0,1,2,3,4,5,6,7,8,7,6,5,4,3,2,1]`. The p.166 omitted-entry erratum is already explicitly retained and resolved by the recorded primary-source review; do not redo that as new implementation. Signed complementary interpolation and ground-referenced chorus output are present. It reads the current phase, then advances once. There is no Engine scanner route or dedicated complete host-rate scanner pipeline in the inspected source.

The independently stamped AC tool has 24/25 free-node solves, exact-rational DC and the frozen 282-positive-frequency grid. The transient tool independently uses full-graph companion stamping and separately reconstructs physical-state constraints. Those are suitable reference inputs. Its retained short charged-C18 refinement remains inconclusive; the full frozen reference refinements are not inherited as completed evidence.

`docs/SCANNER_AC_PARITY.md` retains G3 frequency/process success for the named old build and G5 failure at **every allowed research rate**. At 1,536,000 Hz it records 95 failing vibrato tap comparisons over twelve bins and eighteen chorus comparisons over four bins; the worst cited ratios at 7,075 Hz are about 5.2834 and 2.0204. I did not rerun that native experiment and do not reattribute its result to a changed realization.

Source search finds no connected AO-28 implementation in `include/` or `src/`; the nominal profile explicitly says `ao28: not-modeled`. Full M5 is not a better immediate implementation target: pp.196, 201, 235-240 require independently reviewed endpoints/revision, unknown T3 parameters and operating-point/loading evidence that the atlas's inventory does not supply. A generic valve saturation block would bypass those dependencies.

## Executed candidate feasibility check

**Scope:** an inline, in-memory Python experiment only, from the checkout above, run as `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -B`. Environment: Python **3.12.14**, NumPy **2.3.5**, SciPy **1.17.0**. It created no implementation or report file. SciPy is an exploratory offline dependency here, not a proposed new runtime dependency.

The experiment loaded the admitted registry and constructed scaled physical-state equations from capacitor KCL and inductor voltage laws. Currents were scaled internally by `sqrt(0.5/4e-9) ohms`; public meaning remained volts/amperes. With `D1=R1+ + R1-`, the return was zero in vibrato and `r=Rc/(Rc+D1)*u + Rc*D1/(Rc+D1)*i1` in chorus. Early divider outputs and later absolute taps retained this return exactly once.

First, its continuous state-space response was compared with `scanner_ac_reference.solve_ac` at all **282 frequencies in both modes**. Maximum absolute complex tap disagreement was **6.516356605792058e-14** (vibrato) and **5.6775603914504986e-14** (chorus). Maximum oracle scaled residual was **3.2486101684985267e-16**; maximum oracle scaled condition estimate was **1171.5379395201726**. This checks the exploratory reduction against independent graph stamping; it supplies no physical evidence.

For each allowed distinct internal rate, the script computed an augmented exponential. Given `dx/dt=A*x+B*u`, `h=1/internal_rate` and a linearly varying input over one interval:

```text
E = exp([[h*A, h*B, 0],
         [  0,   0, 1],
         [  0,   0, 0]])
T = E[0:36,0:36]
b_current = E[0:36,37]
b_previous = E[0:36,36] - b_current
x_new = T*x_previous + b_previous*u_previous + b_current*u_current

d = exp(-j*2*pi*f/internal_rate)
H_state(f) = solve(I-d*T, b_current+d*b_previous)
H_taps(f) = output_matrix*H_state(f) + direct_feedthrough
ratio = abs(H_taps-H_analog_same_hz)/(1e-3+1e-2*abs(H_analog_same_hz))
```

No state-matrix inverse, per-tap alignment, gain fit or physical component change was used. Every internal-rate endpoint was supplied from the test sinusoid; **this was not a host-input interpolation or output-decimation experiment**. The eleven distinct internal rates cover the fifteen permitted host/multiplier labels. It executed **6,204 digital response solves and 117,876 tap comparisons**, retaining the following aggregate outcomes:

| Internal rate, Hz | Vibrato failed taps | Vibrato maximum ratio | Chorus failed taps | Chorus maximum ratio |
| ---: | ---: | ---: | ---: | ---: |
| 44,100 | 2,280 | 9.13581746 | 3,626 | 42.10583422 |
| 48,000 | 2,246 | 8.04604722 | 3,583 | 34.68701095 |
| 88,200 | 1,717 | 2.98442962 | 2,594 | 9.44685094 |
| 96,000 | 1,323 | 2.56982035 | 2,275 | 7.93378392 |
| 176,400 | 0 | 0.81490038 | 162 | 2.30582047 |
| 192,000 | 0 | 0.69068953 | 127 | 1.94398282 |
| 352,800 | 0 | 0.20771243 | 0 | 0.57310957 |
| 384,000 | 0 | 0.17550264 | 0 | 0.48361724 |
| 705,600 | 0 | 0.05217284 | 0 | 0.14307050 |
| 768,000 | 0 | 0.04404987 | 0 | 0.12075698 |
| 1,536,000 | 0 | 0.01102331 | 0 | 0.03018006 |

At 352,800 Hz, worst vibrato/chorus absolute errors were **0.0002588949970141774 / 0.0024357796006532423**, both at 20,000 Hz, tap v2. Across digital comparisons the largest scaled residual was **4.709545818680727e-16**, and largest scaled condition estimate was **1426.4745142843055**. The simple exponential candidate therefore addresses the narrow resonance-warping failure without needing fabricated damping. Its remaining lower-rate failures show why an exponential alone does not eliminate the declared input-reconstruction error.

**Limits:** aggregate exploratory results are retained here; there is no admitted per-bin native report, independent matrix-exponential implementation, actual processed-output check, exact-DC check for this candidate, transient/refinement result, rotating sideband result, filter measurement, allocation instrumentation or timing result. A small residual does not establish native forward accuracy. This experiment does not pass G3, G5, G6 or physical M4.

## Concrete next implementation and acceptance

Allocate approximately 18-24 scanner workers across contracts, independent references, implementation and acceptance. The useful deliverable is a runnable research module/probe and rate-conversion pipeline, followed by its executed qualification; another report-only phase would leave the real numerical gap untouched.

1. **Freeze an additive candidate contract.** Keep `scanner-numerics-v1` and original v1 bytes/results unchanged. Give the new realization, coefficient preparation and complete reconstruction/filter policy separate IDs. Preserve the same graph, 36 public physical coordinates, previous-input endpoint, interval origin, current signs, all nineteen outputs, return modes and rotor phase convention. Existing G3 bilinear warp matching remains evidence for v1; the new recurrence needs its own independent FOH identity checks before the unchanged G5 comparisons.
2. **Implement a separately named line.** Suggested owned paths are `include/hammond/ScannerLineFoh.h`, `src/ScannerLineFoh.cpp`, a new probe and distinct tests. Prepare both return operators with a bounded, reviewed exponential/phi-function method outside processing; use stable augmented blocks rather than formulas requiring `inverse(A)`. Retain bounded work, physical-state restore/rate migration, energy observation, input/state bounds and transactional late-failure behavior. Root owns shared CMake registration.
3. **Implement an explicit host/internal pipeline.** A separate research-stage owner composes line, one rotor and prepared conversion filters. Begin with 16x at 44.1/48/96 kHz, without modifying Engine or musical state. Declare the latency, initial padding/tail policy, input endpoint and rotor clocks, event ordering and filter histories. Simply subdividing host sample segments linearly preserves host-rate interpolation droop and cannot be presented as the successful internal-endpoint experiment above. Qualify the actual interpolator and decimator, including 20-20,000 Hz deviation <=0.01 dB and >=80 dB stopband attenuation from host Nyquist, under the frozen contract.
4. **Run unchanged numerical gates.** All 282 positive bins, exact DC, both modes and nineteen taps; unchanged same-Hz complex bound; independently checked actual process carriers; every frozen 2,400-knot transient fixture, with two successful reference refinements; all six rotating modes, three host rates and five specified carriers after the prescribed pre-roll. Preserve waveform RMS/max limits and complex sideband limits, all failures and exclusions, and one global known latency. A revised reference method needs its own identity and convergence evidence; a finest available trace is not automatically truth.
5. **Qualify state, routing and resources.** All physical basis states, zero-drive energy, both return transitions, depth-only changes, all ordered stopped-rate pairs, block partitions, zero-frame behavior and rejected-call continuation. The composed research route must cover four tablet combinations, shaped pedals with Great and Q outside scanner modulation, with no extra chorus dry copy. Test native allocations with a positive control and measure identified Release processing cost. At 16x the dense 36-state update may be expensive; report that cost before claiming a callback deadline or optimizing state representation.

The bounded implementation is dependency-ready. Whether its complete G5 policy passes is an experimental result still to be obtained. G6, loaded scanner/AO-28 coupling, physical specimen matching, M5-M8 acquisition, literal UI equality and other sessions' gates remain separate.

## Input hashes and check ledger

| Inspected/used file | SHA-256 |
| --- | --- |
| `data/scanner/atlas-late-b3-nominal-v1.json` | `1d236be5e6b63e938a9f147808386173949d167e09aee8e902c55002e4ea4604` |
| `docs/SCANNER_NUMERICAL_CONTRACT.md` | `3999a3a409d397401e135e8285704092bad130911468802370bf6da404d58ff9` |
| `include/hammond/ScannerLine.h` | `c249f7c5556d6a6c8c58978928f0b860be442cb1188d35e49c59575729af00c7` |
| `src/ScannerLine.cpp` | `4280db3caa3f7aa225c58a0fa64ec4ca31add55ab8bb46a27aca2deba4544336` |
| `include/hammond/ScannerRotor.h` | `3ca846fc72224114194d73272f410fa2cbe3c0cae94c4fb23105536c7afb4d5a` |
| `src/ScannerRotor.cpp` | `f1dbd65a92036fef9957d280d2aafe9bd8579414ef632a6e2c525e370907b2a0` |
| `tools/compile_scanner_line.py` | `56c60cf511144d552fdeb2708711b32469f350593b391c7619ebb92b41b6dd7e` |
| `tools/scanner_ac_reference.py` | `5472dbe96839a64e864e3d6275ea326b6a497fe5c06997f0a23a3d230763bd1e` |
| `tools/scanner_transient_reference.py` | `5d63941b4b85c28ebf4dce7427e87b87779c3538ae00ff2510014a1df1c45cda` |
| `tools/qualify_scanner_ac.py` | `33e32ca06d60a93be87fa7497f31b41be682bf2f1386d75697b29e4031a42548` |

Executed checks: SHA-256/byte counts; original-PDF metadata; direct range re-extraction equality; all 83 page-number checks; six visual page inspections; local source/status/HEAD/tree/remote-configuration inspection; independent-nodal versus exploratory reduced-analog comparison; full stationary-grid FOH feasibility described above. Repository/native test suites, builds, hardware, DAW, hosted CI and publication were **not run** by this assignment. Temporary PDF renders are isolated under `/workspace/scratch/116ca0948095/atlas/a03/`; the original PDF and extraction were not modified.
