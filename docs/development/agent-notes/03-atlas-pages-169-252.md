# Atlas review 03: pages 169-252

## Coverage and evidence status

Read every page from **169 through 252 inclusive: 84 pages, chapters 027-040**, in seven complete twelve-page text batches. Page references below are the PDF's printed page numbers, which match its one-based PDF positions. Visually inspected rendered pages **170, 177, 185, 194, 230, 231, 239 and 242**. This report reviews the atlas; it does not claim independent verification of the primary documents cited by the atlas or execution of its proposed DSP tests.

Source: `Hammond_B3_Leslie_Research_Atlas_500pp.pdf`, evidence edition dated 12 November 2026.

| Pages | Chapter | Coverage |
| --- | --- | --- |
| 169-174 | 027: Vibrato/chorus switching | Tablet routing, six modes, depth maps, chorus return, state transitions, capture and acceptance contracts |
| 175-180 | 028: WDF scanner | Ladder structure, wave convention, root elimination, discretization, independent comparison, publication discrepancies |
| 181-186 | 029: State-space scanner | Circuit graph, descriptor equations, constraints, state migration, numerical and hardware gates |
| 187-192 | 030: Scanner calibration | Measurement boundaries, complex tap responses, sidebands, residual diagnosis, fitting and holdouts |
| 193-198 | 031: AO-28 topology | Eight sockets, section ownership, signal branches, revision selection, implementation order and unmeasured quantities |
| 199-204 | 032: AO-28 linear network | Loaded small-signal reference, transformer model, preparation, measurements and separate acceptance tiers |
| 205-210 | 033: Valve models | Manufacturer priors, triode/pentode domains, units, grid loading, bounded nonlinear solving and fitting |
| 211-216 | 034: AO-28 interactions | Electrical scale, shared nonlinear stages, bias/charge/feedback memory, headroom and recovery tests |
| 217-222 | 035: Supply and noise | Supply graph, coherent mains, rail load, stochastic units, capture protocol and condition profiles |
| 223-228 | 036: Aging/specimens | Revision versus age, mechanism ownership, correlated variation, immutable service history and attribution |
| 229-234 | 037: Antialiasing | Origin-specific error budgets, multirate state, ADAA limitations, reference convergence, runtime qualification |
| 235-240 | 038: Circuit provenance | Inventory versus connectivity, namespaces, unit conversion, source collisions and incomplete circuit handoff |
| 241-246 | 039: Hybrid modeling | Physical boundaries, bidirectional loading, measured residuals, compilation and model selection |
| 247-252 | 040: Direct-organ validation | Source reuse, routing, contact/percussion histories, scanner, expression/nonlinearity and event partitions |

### Principal conclusion

These pages support an early **semantically correct, deterministic organ architecture with explicit provisional models**. They do not supply a completed AO-28 circuit, validated device coefficients, a calibrated specimen, or a passed complete-organ test. First-phase development should establish ownership, routing, timing, units and evidence records before adding expensive circuit detail. Direct-organ validation precedes Leslie integration (pp. 246-247, 252).

Distinguish the following four evidence categories when reading this report. They are review categories, not a replacement schema: serialize model inputs using the implementation contract's `documented`, `measured`, `derived`, `proposed` and `unknown` values, with execution status stored separately.

| Class | What this range establishes | Limit |
| --- | --- | --- |
| Documentary | Atlas transcriptions of factory routing, socket identities, source assignments and a published late-B-3 scanner map | Applies to the selected document/revision; not automatically to every surviving instrument |
| Proposed model | Circuit derivations, software architecture, capture plans, numerical methods and acceptance procedures explicitly identified as original proposals | A useful implementation contract, not a measured factory characteristic |
| Atlas-reported executed calculation | Synthetic WDF algebra, idealized scanner AC calculation, narrow cubic/ADAA fixtures and inventory structural checks | Narrow numerical/document checks only; not locally reproduced by this review |
| Unresolved or unmeasured | Specimen revision, many loads/transformer parameters, fitted valve curves, hardware captures, acoustic tolerances and full-engine acceptance | Preserve `null`, `not_run` or `blocked`; do not fabricate a nominal measured value |

**Companion availability:** a repository search found none of `025-scanner-network.json`, `038-ao28-bom.json`, `ao28-component-values.json`, `scanner_ac_reference.py`, `scanner_nominal_response.json` or `wdf_algebra_reference.py`. The PDF has zero embedded files and no companion archive was found. Their existence/results are assertions in the atlas, not available local reproducibility artifacts. Obtain them or independently reconstruct and review the necessary data before relying on them.

## 1. Scanner control semantics are implementable now

The atlas attributes the following separation to the service manual: Swell selects upper sustained material; Great selects lower sustained **and pedal** material; percussion enters after the scanner; the selector has six modes and no OFF position (p. 169). Let `U`, `L`, `P` and `Q` denote upper, lower, shaped pedal and percussion buses:

| Swell | Great | Scanner input | Bypass input |
| --- | --- | --- | --- |
| Off | Off | 0 | U + L + P |
| On | Off | U | L + P |
| Off | On | L + P | U |
| On | On | U + L + P | 0 |

`Q` is outside every row. Treat this as a destination matrix, not a claim of equal electrical gains. Keep one shared scanner phase and one wet network history; individual effects per manual or independent pedal vibrato would be explicit extensions. Continue the scanner clock with both tablets off, and preserve electrical history with the appropriate zero-input evolution (pp. 169, 172-174).

The late-B-3 paper map transcribed on p. 170 is exact documentary data within that profile:

| Mode pair | Nine one-based ladder-node indices |
| --- | --- |
| V1 / C1 | 1, 2, 3, 4, 5, 6, 7, 8, 9 |
| V2 / C2 | 1, 2, 3, 5, 7, 9, 11, 12, 13 |
| V3 / C3 | 1, 2, 4, 7, 10, 13, 16, 18, 19 |

Validate all indices and make the conversion to zero-based storage explicit. The same-depth V/C pair shares a map; its electrical return condition differs. A depth change changes connections, not an interpolated sinusoidal-delay depth. Keep any smooth-switch or continuous-depth extension separate from the historical mode state (pp. 170, 172).

The chorus return is a high-risk architectural detail. The atlas derives `v_k = r + z_k`, where `r` is the line return and `z_k` is a local tap voltage. If scanner weights sum to one, the weighted absolute voltages already include `r` once. Adding another dry signal doubles that contribution; discarding `r` loses it. The cited model uses a 22 kOhm return resistor, but a universal 50/50 mix is not a circuit identity (p. 171). Expose voltage-reference identity in diagnostics so this error is observable.

**Immediate recommendation:** implement the controls, routing table, semantic mode data, shared phase ownership and assertions before choosing the final ladder solver. A simplified first-phase scanner must carry its approximation identity; its existence cannot be counted as a passed circuit or hardware gate.

## 2. Numerical scanner architecture: preserve one graph, choose a runtime realization

### Structure and state

The selected published schematic has **18 inductors, 18 capacitors and 19 observable node voltages**, including six early divider networks. The text's inconsistent reference to nineteen stages must not create an extra LC section (pp. 175, 181). A multi-output loaded network is required; an independent filter per tap or per played note loses electrical coupling. Divider branch `k` occurs before `Lk`, while `Ck` follows it (p. 182).

Use one reviewed graph with component IDs, endpoint nodes, voltage reference, current direction, source/load contracts and revision applicability. Generate an inspectable offline reference and a prepared runtime realization from it. Keep graph topology, tap map and mechanical angle under distinct ownership (pp. 175, 181-184). Nineteen observed voltages do not imply nineteen independent states; 36 reactive components suggest at most 36 energy coordinates before constraints and rank analysis (p. 181).

### WDF contract and publication hazards

The atlas derives waves as `a = v + Rp*i`, `b = v - Rp*i`, with positive `Rp`, and reconstructs physical volts/current explicitly. Under its convention, an adapted capacitor returns the previous incident wave; an adapted inductor returns its negative. `Rp` is `1/(K*C)` and `K*L`, respectively, with default `K = 2*internalFs` (p. 176).

The coupled source/switch root must close instantaneous constraints without an invented sample delay. For the atlas's partition, prepare `M = I - Phi*S11`, then obtain the reduced operators using linear solves. The order of `Phi` and `S11` matters. Retain a residual against the original simultaneous equations (p. 177). The atlas identifies printed inconsistencies in the research paper's root equation, source signs, switch labels, inductor expression and adaptation coefficients; this review has not independently audited the paper. Do not copy those expressions without deriving and testing the selected convention (pp. 177, 180).

### Descriptor alternative

The proposed MNA system keeps node voltages and selected branch currents, with `E*z_dot + K*z = B*u`. `E` may be singular: do not invert it. Preserve or eliminate algebraic constraints deliberately; raw trapezoidal descriptor stepping can retain nonphysical alternating constraint errors. Use one discretization convention across the complete coupled network, factor fixed systems outside the callback, and reconstruct physical states when configurations change (pp. 182-184).

Both formulations require old reactive histories to remain unchanged during calculation and to be committed only after the new result is accepted. Mode/rate changes must preserve compatible capacitor voltage and inductor current; unchanged wave memories after changing port resistances are not generally equivalent physical state. An output crossfade can conceal a wrong state conversion and therefore cannot serve as its correctness test (pp. 172, 178, 184).

### Comparison strategy

Compare all nineteen taps, both return topologies, with an independently assembled circuit solve. First compare on the bilinear warp-matched grid to isolate sign/topology errors; then compare at identical hertz to measure discretization error. Use common timestamps and explicit resampler delay, rather than independently shifting taps. Test nonzero stored energy and converged transient references as well as zero-state AC responses (pp. 179, 185-186).

The atlas's prewarp examples distinguish hertz from radians/second; at 44.1 kHz, 7075 Hz and 7075 rad/s produce different effective periods. These are arithmetic demonstrations, not selected calibration values (p. 178). Its proposed normalized solve-residual target below `1e-9` applies to a well-conditioned double-precision synthetic fixture, not every mixed-unit circuit or hardware fit (p. 186).

The reported `1.11e-16` root error covers 100 synthetic matrices only (p. 180). The nominal AC result is an idealized calculation not compared with SPICE, WDF or hardware in this edition (p. 185). The visual chart on p. 185 explicitly labels itself a computed idealized model; it must not become a measured response asset.

## 3. AO-28 needs a revision-specific connected model

The factory-derived inventory in this range is eight sockets, not a Leslie loudspeaker power amplifier (pp. 193-198):

| Socket | Family | Role in selected drawing |
| --- | --- | --- |
| V1 | 6AU6 | Non-vibrato input |
| V2 | 6AU6 | Vibrato input |
| V3 | 12BH7 | A: scanner-line driver; B: transformer-output driver |
| V4 | 12AX7 | Common gain sections around expression |
| V5 | 6C4 | Percussion audio |
| V6 | 6C4 | Percussion keying/charge control |
| V7 | 12AU7 | Two percussion-control sections |
| V8 | 6X4 | Supply rectification |

Keep physical socket identity separate from electrical section identity. An inconsistent theory paragraph is not evidence for an extra output socket. A shared envelope does not by itself establish shared distortion, while traced bias/supply nodes do establish an electrical connection (pp. 195, 213).

Preserve A/non-vibrato, B/vibrato and H/percussion entries, scanner drive/return, expression between V4 sections, feedback and T3 output/loading. A single mixed bus through one generic saturation stage loses these distinctions. Nonlinear processing occurs after signals meet at their real shared stage: per-note saturation omits the cross-products of a common amplifier (pp. 194-196, 211-214).

Build the loaded linear reference before nonlinear devices. Store DC operating point, electrical scale, source impedance, receiver load, control positions and transformer polarity. T3 parameters must not be inferred from its symbol or from winding resistance ratios. Choose either coupled inductances or a derived ideal-ratio/equivalent network without double-counting magnetic energy; fit against multiple loads and require a physically admissible inductance matrix (pp. 199-204).

Valve datasheets are priors, not measured AO-28 coefficients. The GE 12AX7 example is a dimensional check; neither it nor a printed supply voltage establishes headroom. Retain device-family schemas and valid voltage domains. The triode Koren form shown needs stable softplus, a guarded fractional power, its factor-of-two convention and `KVB` in volts squared; the similarly named pentode parameter has different units. Preserve pentode screen current/voltage and connected positive-grid loading, including any resulting capacitor charge (pp. 205-209).

A nonlinear solver needs scaled residuals, verified derivatives, bounded iterations/damping, warm starts and a bounded failure policy. Trial iterations cannot partially commit reactive history. Any fallback may contain the failure but fails nominal fidelity acceptance. Its small-signal limit must reproduce the qualified linear network, and convergence alone does not establish spectral accuracy (pp. 208, 210, 214, 216).

**First-phase implication:** establish these branches and electrical/profile interfaces now. Defer claims of circuit-level AO-28 accuracy until the active connectivity, source/load values, operating points and device fits exist. No output wattage, absolute gain, clipping threshold or fitted valve parameters are verified by these chapters (pp. 197, 210, 216).

## 4. Provenance and mechanism ownership are required architecture

The atlas reports **85 inventory records**: 84 stock rows plus a heading, with 70 part-number fields resolved and 15 unresolved. It separately reports **124 electrical placements/valve sections across alternatives**. Neither count establishes installed package count, quantity or complete connectivity. Unknown quantities stay null (p. 235). The complete independently reviewed per-instance circuit trace remains unfinished (pp. 238, 240).

Keep stock numbers, assembly callouts, schematic designators, physical packages and simulator instances in separate namespaces. Preserve document checksums, printed text, canonical SI value, units, source locator, revision, competing interpretations and review status. Active unresolved numerical values block that circuit's numerical export; they need not block a clearly scoped behavioral prototype (pp. 236-240).

Concrete source/unit hazards to retain as regression fixtures:

- The selected factory supply capacitor is C59; the 1995 redraw duplicates C56 at that location. Preserve both observations and the selection rationale (pp. 217, 239).
- Catalog `6-6-43` appears for two component types; do not merge their instances. An item-47 resistance glyph and the primary R62 reading remain unresolved (pp. 236, 239).
- The solid P-D and no-code AO-28-1 networks are alternatives, including differing C32 values. Select a verified revision instead of combining convenient parts (pp. 196, 236).
- `0.33 MF`, where corroborated as microfarads, is `3.3e-7 F`; `4.7K pF` is `4.7e-9 F`; `40/450` is capacitance plus voltage rating; `1 MEG` is `1e6 ohm`. The atlas warns that SPICE `M/m` means milli; emit reviewed exponent notation and verify round trips (p. 237).

Give every physical response exactly one owner. A loaded generator waveform already includes its upstream loading; an amplifier capture may already include its transformer/load; an IR or learned residual may include microphone response. Re-applying those mechanisms creates double counting (pp. 224, 241-244). Strongly interacting electrical stages require a coupled solve or a justified interconnection; a voltage-only measured map cannot supply missing input-current behavior under arbitrary loads (p. 242).

Profiles should separate documentary identity, inspected configuration, dated condition, service events, operating variation, uncertainty and artistic options. Calendar age is metadata, not evidence for drift. The Bulletin 16 serial threshold and retrofit possibility demonstrate why inspected topology outranks birth year (p. 223). Do not redraw physical component values per note, turn uncertainty into audible randomness, or infer a population distribution from one specimen (pp. 225-228).

## 5. Multirate, noise and runtime contracts must survive future detail

Assign separate numerical budgets to source representation, contact/control events, nonlinear solve and decimation. Aliases produced at a base-rate contact discontinuity cannot be repaired by later upsampling. Generate events and sources at the necessary internal resolution, retain intended click bandwidth, and filter before each rate reduction (p. 229).

All states in a connected feedback group share one internal timeline. Recompute phase increments, envelope times, reactive coefficients and noise scaling from the actual internal rate. Quality changes preserve specimen parameters and registration, with explicit state migration and measured technical latency alignment (pp. 230, 232, 234, 244). The atlas's JUCE factor example is an API-version-specific caution, not a dependency selection for this repository (p. 230).

First-order ADAA is not transparent even for `f(x)=x`: it becomes `(1+z^-1)/2`, adding half an internal sample of delay and cosine magnitude loss. Its near-equal-input limit uses the midpoint. Applying it to coupled valve or feedback systems requires a separate derivation; a scalar identity does not qualify the whole circuit (pp. 231-232). The p. 233 cubic alias demonstration and p. 234 quadrature error of at most `8.89e-15` are narrow toy checks, not evidence that 2x processing suffices for an organ.

Supply ripple, heater coupling and magnetic pickup need one coherent mains reference with separately evidenced paths. Use either coupled supply behavior or an identified surrogate without adding the same ripple twice. Preserve each rail's load and charge state; do not substitute Leslie-stage sag (pp. 217-219). Physical noise needs units, bandwidth and deterministic per-source state: with the atlas's flat one-sided PSD convention, discrete standard deviation scales as `sqrt(S1*Fs_internal/2)`. Match integrated output bandwidth across quality/rate changes and keep unmeasured amplitudes null or explicitly proposed (pp. 220-222).

Prepare immutable model plans, buffers, coefficients, topologies and state conversion outside the audio callback. Runtime work has fixed maximum cost, no allocation, file access, fitting, training or unbounded retries. A learned recurrent model also needs a qualified rate and persistent history; running it at a new rate changes its physical time interpretation (pp. 172, 184, 202, 208, 226, 244).

## 6. Recommended first-phase deliverables and gates

### Build now

The coordinator's `docs/IMPLEMENTATION_CONTRACT.md` selects a narrower M0-M2 deliverable: a framework-independent continuous-source engine and offline renderer, with scanner, percussion/contact detail, AO-28 and Leslie gates deferred. The recommendations below establish foundations and future interfaces; they do not require expanding that authorized implementation milestone into a complete electrical model.

1. **Evidence/profile schema:** revision and hash, source locators, numeric units, confidence/status, explicit unresolved fields, approximation scope and physical ownership. Never serialize `unknown` as a fabricated zero.
2. **Absolute event timeline:** stable same-sample ordering, sample-stamped controls, physical-key owner accounting and traces independent of host block partition.
3. **Continuous source/state ownership:** shared source identity across foldback collisions, persistent generator phase and separately owned manual/contact paths. Reserve future scanner-phase and percussion-charge ownership without fabricating those missing models.
4. **Exact routing/mode specifications:** retain the four tablet combinations, six semantic modes and nine-node maps above as the later scanner's test contract; percussion remains downstream when implemented.
5. **Observable direct-organ pipeline:** source, bus and final-organ outputs now, with scanner-return observation when that stage exists. Declare the normalized presentation scale and explicit absence of an electrical calibration in the initial engine. Retain the direct render after adding Leslie.
6. **Gate manifests:** reference tier, profile/input/output hashes, event script, initial state, rate, block partition, calibration, tolerance, result and unresolved cause. Separate documentary, numerical, hardware and musical results.

These recommendations derive from pp. 169-174, 226, 244, 247-252. A playable first-phase approximation can proceed with a declared scope while measured-fidelity gates remain open.

### Test matrix with concrete oracles

| Gate | Recommended falsifiable test | Reference/status boundary |
| --- | --- | --- |
| Source identity | Manual key 61 maps to `[61,80,73,85,80,85,89,80,85]`; keys 1 and 13 at 16-foot both select source 13 while keeping distinct contacts | Documentary exact source IDs, not hertz; p. 248 |
| Pedal exceptions | Pedals 1-7 duplicate the second source in the third-contact column; pedals 8-12 disconnect that contact | Exact mapping fixture; p. 248 |
| Routing | Isolate U, L, P, Q for all four tablet states and all six modes | Documentary destinations; gains need separate calibration; pp. 169, 174, 250 |
| Chorus reference | Reconstructed return appears once; distinguish local/absolute voltages | Model algebra first, loaded reference later; pp. 171, 174 |
| State continuity | Note, selector, tablet, block and quality changes cannot silently reset shared phase/history | Deterministic software contract; hardware switching transients remain unresolved; pp. 172, 184, 250 |
| Event ownership | Repeated MIDI pitches do not create additional presses of an already-held physical key | Event/contact contract; p. 249 |
| Percussion history | Legato overlap, release-gap sweep, control changes during decay and preset B/other/B while held | Gaps 0-1000 ms are proposed experiments; held-control hardware oracle still needed; p. 249 |
| Rate/block behavior | Repartition one absolute event stream, including first/last frames, at blocks 1, 17, 64, 127, 512, 1024 and rates 44.1/48/96 kHz where supported | Same-rate event equality and declared floating-point budget; cross-rate reconstruction/latency required; p. 252 |
| Circuit solver | All nineteen taps, both return states, physical signs/units, scaled residuals, energy and transient convergence | Independent numerical reference, not duplicate implementation; pp. 179-186 |
| AO-28 integration | Small-signal limit, multiple loads, expression positions, paired inputs and burst recovery | Qualified circuit first; specimen measurements later; pp. 204, 210, 216, 251 |
| Spectral/runtime | Converged high-rate comparison, separate alias/total-error metrics, finite output, zero fallback in accepted fixtures, worst-case bounded callback | No universal oversampling factor or supplied acoustic threshold; pp. 229-234 |
| Physical fidelity | Calibrated repeated captures with held-out modes, sessions, registrations and loads | Explicitly `not_run` until recordings and evaluation exist; pp. 192, 204, 240, 252 |

The intended final direct-organ statuses are `D40-D` documentary, `D40-N` numerical and `D40-H` hardware (p. 252). Do not collapse them into one green indicator. This review has executed coverage and visual inspection only; the table recommends implementation tests and does not report them as passed.

### Later dependencies

After the foundation, obtain/reconstruct the scanner component graph and independent AC/transient reference, choose a qualified runtime realization, and only then calibrate rotating coupling. Scanner identification needs one shared angle estimate, complex sidebands and repeatability; the nominal 412 rpm is documentary, while sixteen-times-rotation plate structure is not the fundamental vibrato rate (pp. 187-192).

Next complete the AO-28 instance graph and transformer/load evidence, establish its linear baseline, fit device families, and qualify connected nonlinear behavior. Supply/noise and dated specimen deviations then require their own captures. Learned corrections, population/aging models and artistic drive/condition extensions are later options with separate identities and validity domains (pp. 193-246).

All acquisition-dependent stages need calibrated absolute levels, source/load boundaries, control snapshots, warm-up/condition metadata, repeat captures and untouched holdouts. Numeric and acoustic tolerances must be chosen for their own evidence and uncertainty, rather than borrowed from toy examples or adjusted after final evaluation (pp. 173, 187-192, 197, 203, 209, 215, 221, 227-228, 245).

## Visual/source-quality notes

- Page 170 visually confirms the exact table values and separate panel tablets/selector.
- Page 177's diagram is an original algorithm flow; it does not supply component connectivity.
- Page 185's response plots are explicitly computed idealized responses, including only selected taps in the illustration.
- Page 194 refers to a graph below but displays a tube photograph. The text and cited schematic must carry the functional interpretation; the photograph cannot establish wiring.
- Pages 230-231 explicitly illustrate numerical alias folding and ADAA coloration, not measured instrument spectra.
- Page 239 retains source collisions and unresolved readings; page 242 illustrates modeling boundaries rather than a literal netlist.

No implementation files were modified for this review. Only this report was authored; no commits or hardware-fidelity claims were made.
