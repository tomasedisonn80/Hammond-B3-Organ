# Remaining M3 work and the next scanner gate

This retained contract originally set reconstruction and independent review of
the **nominal scanner circuit** and its offline response oracle as the next
numerical task. Those modules now exist. Follow the [scanner handoff](SCANNER_HANDOFF.md)
and [current status](STATUS.md) for implemented source, executed gates and the
remaining G5 same-hertz failure before Engine integration. The contract below
remains authoritative; proposed milestones are not a current absence claim.

Complete M3 still needs physical preset and drawbar behavior, switching
bandwidth, loaded expression and pedal-network evidence. The later
[18-row chapel catalog](CHAPEL_PRESETS_CATALOG.md) and explicit
[ordinary-control auditions](CHAPEL_CONTROLS.md) preserve all 162 documentary
taps; they do not implement physical latching or calibrated loaded gains.
These tasks can progress in parallel; a scanner prototype does not close them.

This is an implementation and acquisition contract, not a report of an implemented
scanner or a measured instrument. The [project plan](PLAN.md) owns the complete
M0-M9 sequence. [Current status](STATUS.md), [next steps](NEXT_STEPS.md) and the
[scanner handoff](SCANNER_HANDOFF.md) own revision-specific execution results.
Proposed filenames and API names below do not imply that those files or APIs exist.

## 1. Preserve the working baseline

The current implementation already supplies the source, timing and ownership
foundation needed for this work:

| Existing boundary | What the next implementation must preserve |
| --- | --- |
| [Engine](../src/Engine.cpp) and [TonewheelBank](../include/hammond/TonewheelBank.h) | One shared frame of 91 free-running sources per rendered sample; silence, disconnected outputs and new effects cannot stop or restart that history. |
| [ControlState](../include/hammond/ControlState.h) | Four retained integer-position A/B banks, exclusive selection and routing-only Cancel. This is not the atlas's eleven-contact-key physical latch model. |
| [ContactBank](../include/hammond/ContactBank.h) | Ideal or named nominal linear travel, 1,098 separate manual contacts, make/break thresholds and partial-key targets. The nominal 8/12 ms durations and thresholds are unmeasured. |
| [PedalVoice](../include/hammond/PedalVoice.h) and [pedal Engine contract](PEDAL_ENGINE.md) | Twenty-five pedals, all 200 contact positions, four separate buses and two named nominal mixtures. The static matrix is not a reactor model; its two labels remain Pedal Mixture 1/2. |
| [Controls](CONTROL_STATE_FORMAT.md) and [parameters](PARAMETERS.md) | `B3CONTROLS3`, strict older-format migration and all 45 permanent records. Current expression is the normalized linear-gain surrogate; ID `0x2000` must not silently become measured pedal travel. |
| [HostTimeline](HOST_TIMELINE.md) and [StateExchange](STATE_EXCHANGE.md) | Whole-callback admission and rollback, stable event ordering, bounded storage, coherent UI/audio publication and control-only state loading. |

`Engine::rebuild_coefficients()` presently combines both manuals into one
per-source sustained coefficient array. `Engine::process()` sums that array,
adds the separate percussion contribution `Q`, conditionally adds nonzero pedal
`P`, then applies common output gain and expression. Splitting that accumulated
sum into `U + L` can change floating-point rounding even if the real-number algebra
is equal. Preserve the existing dry path and arithmetic when a new scanner model
is disabled; verify actual legacy WAV/PCM bytes after integration. Do not assume
that independently summed divisions reproduce the former byte sequence.

The existing [source profile](../data/profiles/nominal-unmeasured-v1.json),
[pedal map](../data/pedal-map.json), [registry](../data/parameter-registry.json),
old scores and retained evidence bundles remain immutable compatibility inputs.
New numerical or physical profiles need new identities and explicit units.

## 2. M3 work that remains

The source for this section is the preserved
[atlas](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf), pp. 109-126 and 139-150.
The [earlier M3 contract](M3_ACCEPTANCE_CONTRACT.md) preserves the contact and
percussion acceptance that led to the current nominal implementation; its dated
unimplemented-pedal statements do not supersede current code.

| Work item | Smallest useful implementation | Evidence needed to close its broader gate |
| --- | --- | --- |
| Fixed presets and cradle | A typed `PresetKey` domain for C-sharp through B, plus a distinct Cancel action; a separately versioned, two-manual 9-by-9 fixed-registration matrix; an exclusive selector that preserves inactive banks and held keys. | Independently compare all 162 digits of atlas p. 122 with the identified factory Table IV source. Identify the actual specimen's wiring separately. Exercise all eighteen fixed registrations against corresponding single-bank settings. |
| Simultaneous physical latches | A fixed eleven-bit latch mask and explicit mechanical transition policy, initially testable without audio. Cancel empties the mask and never becomes a latched twelfth bit. | Actual contact-bearing routes, overlap timing, branch impedances and a loaded transformer solve. Multiple latched routes must not be rendered by summing independent preset programs. |
| Continuous drawbar travel and loading | Keep physical marking, continuous travel and contact conductance as distinct quantities; preserve the existing stationary nominal 3 dB reference. A separately named smooth-control surrogate can be developed independently. | Production contact/tap connectivity, transformer/source/load boundaries, forward/reverse travel traces and calibrated complex responses. Atlas p. 110's documented 1-ohm contact connection is not a complete transformer model. |
| Contact switching bandwidth | A bounded fractional-edge reference and rate-convergence experiment over the existing shared source field, before choosing an optimized renderer. Preserve independent make/break history. | Synchronized key position, all nine contact traces, source phase and dry output, with clock, bandwidth and probe loading. Both value jumps at source peaks and slope jumps at zero crossings need coverage. |
| Loaded expression | A separate model with pedal position, controller calibration, electrical profile and filter history; its first numerical gate is stationary loaded transfer, followed by movement. | AO-28 revision, loud/soft branch connectivity, receiver feedback including C22, capacitance-versus-position and parasitics, calibrated source/load and synchronized motion. The present scalar cannot establish this response. |
| Pedal reactor, contacts and low-wheel spectra | Preserve `PedalBusKernel` as a routing reference; build a separately identified four-input/two-output network model with persistent reactive state. | Production reactor/resistor/transformer connectivity, reactor henries and series ohms, source/contact impedance, control-dependent loading and calibrated complex low-wheel spectra. None is supplied by the static mixture coefficients. |

For fixed presets, the atlas p. 122 table is the **approved chapel arrangement**,
not a universal surviving-B-3 setting. Store nine-character registrations with
leading zeros; digits describe tap assignments. The existing source map must not
change when a preset changes. Upper-B eligibility, ninth-contact keying, upper
sustain compensation and percussion history must transition together at the
scheduled sample. Lower selection and Cancel leave pedal ownership and registration
alone. Physical re-entry behavior needs its own captures; the present nominal
percussion policy remains a named reference. [Atlas pp. 121-126.]

For switching bandwidth, render the source and contact operation at the chosen
internal time resolution before bandwidth reduction. Upsampling the already
switched base-rate result cannot qualify that earlier operation. A proposed
synthetic target is normalized RMS error at most `1e-4` against an independently
converged reference, after one declared gain/latency convention; the atlas gives
this as an engineering target, not a factory tolerance or executed result.
Preserve pending edge/filter tails across blocks, notes, rate changes and silence.
[Atlas pp. 115-120.]

For moving expression or scanner capacitance, charge uses `d(C*v)/dt`, including
`v*dC/dt`. A frozen-position filter approximation must be named and compared with
a charge-based reference before it is accepted. Applying a second expression
curve after a future AO-28 graph containing the same network would count the
effect twice. Downstream monitoring gain stays separate from expression drive.
[Atlas pp. 145-150, 165.]

For the pedal network, unit bus impulses and all 81 control pairs are useful
numerical tests, but the existing fixed matrix must remain available as its own
model. Intrinsic harmonics follow multiples of one wheel's phase; borrowed
generators keep their own shared phases and frequencies. Reusing a patent's
illustrative harmonic strengths or resistance values would not establish a
production B-3 profile. [Atlas pp. 139-144; [pedal voice contract](PEDAL_VOICE.md).]

## 3. First scanner commit: data and topology, with no Engine change

Create a reconstructed authoring profile, a strict compiler/validator and an
independent connectivity review. Suggested initial files are
`data/scanner/atlas-late-b3-nominal-v1.json`,
`data/scanner-line.schema.json`, `tools/compile_scanner_line.py`,
`tests/test_scanner_line_profile.py` and a source-review record. These are proposed
paths, not recovered atlas companions. The original `025-scanner-network.json`,
`scanner_ac_reference.py` and response JSON referenced in the atlas are absent.

Use `atlas-late-b3-nominal-line-v1` as a proposed model identity until the new
authoring contract is frozen. Evidence class is documentary reconstruction of
the atlas's published late-B-3 model. Actual specimen applicability remains
unknown. Import units once, retain printed values and source/page locators, and
keep independent review status separate from a JSON/schema pass.

### Exact candidate endpoint graph

The decomposition on **atlas p. 158**, checked together with pp. 157, 175 and 182,
supports the following explicit reconstruction. Its early divider is on the
**input side of each section**. This graph is ready for independent source
comparison; this document is not that second comparison against the cited paper
or the chosen production drawing.

Use electrical datum `g`, driven node `p0`, section nodes `p1` through `p18`, common
return `r`, and six divider midpoints `d1` through `d6`. Retain the positive and
negative endpoint of every voltage/current port.

| Elements | Positive endpoint | Negative endpoint | Documented nominal value / meaning |
| --- | --- | --- | --- |
| Ideal drive | `p0` | `g` | `V_in`; imposed voltage, with current retained as a probe |
| `Lk`, k = 1..18 | `p(k-1)` | `pk` | 500 mH = 0.5 H each |
| `Ck`, k = 1..17 | `pk` | `r` | 0.004 microfarad = `4e-9` F each |
| `C18` | `p18` | `r` | 0.001 microfarad = `1e-9` F |
| `Rk+`, k = 1..6 | `p(k-1)` | `dk` | Upper divider leg; values below |
| `Rk-`, k = 1..6 | `dk` | `r` | Lower divider leg; values below |
| `Rt` | `p18` | `r` | 15 kilohms = 15000 ohms |
| `Rc` | `r` | `g` | 22 kilohms = 22000 ohms |
| Vibrato return switch | `r` | `g` | Closed: constrain `r = g`; open: chorus returns through `Rc` |

| Divider k | `Rk+` in ohms | `Rk-` in ohms |
| --- | ---: | ---: |
| 1 | 27000 | 68000 |
| 2 | 56000 | 150000 |
| 3 | 39000 | 150000 |
| 4 | 33000 | 180000 |
| 5 | 18000 | 180000 |
| 6 | 12000 | 180000 |

There are **50 passive elements: 18 L, 18 C and 14 R**. The ideal source and ideal
switch are separate objects. There are 27 named nodes before any ground/short
contraction. These counts are consistency checks, not a reason to synthesize a
missing component. Model the ideal short by node contraction or an explicit
constraint; do not insert infinite conductance into floating-point arithmetic.

Export exactly nineteen **ground-referenced** outputs:

- `v1` through `v6` are `V(d1,g)` through `V(d6,g)`.
- `v7` through `v19` are `V(p6,g)` through `V(p18,g)`.

The output mapping is not nineteen LC sections, nineteen independent memories or
nineteen stator plates. There are at most 36 candidate energy coordinates from
the eighteen capacitor voltages and eighteen inductor currents; determine actual
rank and algebraic constraints from the admitted graph before reducing it.

The nominal fixture explicitly uses ideal coils, ideal drive and negligible
scanner loading. Those are approximations of this fixture. Actual winding
resistance, mutual/stray coupling, AO-28 drive impedance, scanner coupling and
recovery-stage loading remain **unknown physical quantities**, with reasons and
acquisition dependencies; do not fill those unknowns with measured-looking zeros.
An added load or loss creates a separately identified boundary/profile. No current
Engine normalized amplitude has a calibrated volts conversion.

### Admission failures that must be observable

Reject duplicate IDs, dangling endpoints, missing references, nonfinite values,
wrong units, nonpositive admitted R/L/C values, the wrong component/output count,
an early divider moved after `Lk`, an output referenced to `r`, and a missing or
misidentified return switch. Bound input bytes, strings, components and node counts;
reject unknown fields and failed provenance/mapping checks before generating any
runtime data. Preserve the previous destination/output on failure.

A generalized graph may legitimately differ from this fixture, but it cannot keep
this identity or its exact expected response. Tests should mutate actual graph
edges and unit prefixes, rather than merely repeat the producer's generated
arrays. An independently retained endpoint list and source-image locators make
the review auditable.

## 4. Independent numerical oracle before the real-time solver

Implement a readable offline modified-nodal AC reference directly from the
reviewed endpoint list. Implement the runtime formulation independently, initially
in binary64. Sharing the admitted physical graph is appropriate; sharing stamping,
factorization or tap-reconstruction code between the two would weaken their
ability to detect the same sign/index error. A separately assembled SPICE netlist
is an additional check if a pinned simulator is selected and executed. No SPICE,
scanner AC or scanner time-domain pass is inherited from the atlas.

Use the signed descriptor contract from atlas pp. 182-186:

```text
C_N = A_C diag(C) A_C^T
G   = A_R diag(1/R) A_R^T
C_N dv/dt + Gv + A_L iL + A_V iV = i_injected
L diL/dt + R_L iL - A_L^T v = 0
A_V^T v = uV
E dz/dt + Kz = Bu
y = Pz + Du
```

Each incidence column is +1 at its declared positive endpoint and -1 at the
negative endpoint. Current injection is positive into a node. Keep ampere/volt
units explicit when scaling equations. `E` can be singular: do not compute its
inverse, and do not treat an algebraic constraint mode as a physical resonance.
At each test frequency solve `(j*omega*E + K) z = B u`; retain all nineteen complex
transfers and the input-current convention.

### Analytical known answers

The ideal DC limit supplies an oracle independent of matrix assembly. Inductors
short, capacitors open, and all `pk = V_in`. Define

```text
R_parallel = 1 / (1/Rt + sum(k=1..6, 1/(Rk+ + Rk-)))
r/V_in = 0                                      [vibrato]
r/V_in = Rc / (Rc + R_parallel)                 [chorus]
v_k/V_in = r/V_in + (1-r/V_in)*Rk-/(Rk+ + Rk-)  [k=1..6]
v_k/V_in = 1                                    [k=7..19]
```

For the exact nominal values above, independent rational arithmetic gives
`R_parallel = 9775.932618884532` ohms and chorus `r/V_in = 0.6923478931008726`.
Input resistance is `R_parallel` in vibrato and `R_parallel + Rc` in chorus.

| DC output | Vibrato `v_k/V_in` | Chorus `v_k/V_in` |
| --- | ---: | ---: |
| 1 | 0.715789473684 | 0.912562032776 |
| 2 | 0.728155339806 | 0.916366417542 |
| 3 | 0.793650793651 | 0.936516231910 |
| 4 | 0.845070422535 | 0.952335589072 |
| 5 | 0.909090909091 | 0.972031626646 |
| 6 | 0.937500000000 | 0.980771743319 |
| 7..19 | 1 | 1 |

These derived numbers are checks of the explicitly ideal candidate graph, not
observed organ voltages. They cannot expose every misplaced early divider;
finite-frequency and mutation tests are also required. The uniform lossless
section additionally gives `sqrt(L*C) = 44.72135955` microseconds,
`sqrt(L/C) = 11180.3398875` ohms and `1/(pi*sqrt(L*C)) = 7117.62543417` Hz.
That simplified section omits the finite ladder's dividers, termination and
smaller final capacitor. It is a units check, not the scanner's measured delay
or cutoff. [Atlas p. 159.]

### Required response and state report

| Gate | Required execution and retained result |
| --- | --- |
| Signs and loading | Both return states, all nineteen signed outputs, analytical DC limits, input current, and finite-frequency termination changes. A downstream load change must influence upstream nodes where the connected network predicts it. |
| Linear solve | Report equation scaling, conditioning and normalized residual `norm(Az-b)/(norm(A)*norm(z)+norm(b))`; handle the all-zero denominator explicitly. Initial proposed target: at most `1e-9` on admitted, well-conditioned fixtures, matching the atlas's proposed software target. |
| AC parity | Freeze a logarithmic physical grid from 20 Hz to 20 kHz plus refined resonance/null regions and the DC limit. Compare both topologies and all taps. For a bilinear runtime, first compare at analog `Omega = K*tan(omega_d/2)` to isolate graph/sign error, then at the same physical Hz to expose warping. |
| Initial numerical budget | Proposed warp-matched complex error: `abs(H_runtime-H_oracle) <= 1e-8 + 1e-6*abs(H_oracle)` per tap. Record every failed bin. These are new engineering targets to review before implementation, not achieved results or hardware tolerances. |
| Phase and delay | Retain complex values, magnitude, unwrapped phase and group delay. Declare a magnitude/excitation floor before grading phase or differentiating it; include excluded bins and reasons. Do not align every tap independently. |
| Transients | Zero-state step, impulse and finite-bandwidth multisine; nonzero initial capacitor/current states; silence decay; positive/negative excitation. Refine the independent integration step until the comparison converges under the same input reconstruction. |
| Energy and constraints | Fixed passive network with drive removed must dissipate or conserve energy within a stated numeric allowance. Return switching must preserve compatible capacitor voltages and inductor currents, reconstruct algebraic variables and account for source/switch energy. A changed observation map alone leaves physical state unchanged. |
| Rates and cost | 44.1, 48 and 96 kHz host rates, declared internal rate, regular/irregular block partitions, stopped rate changes, complete bounds and measured worst-case work. Same-hertz spectral and sideband error budgets must be frozen before choosing an internal-rate policy. |

A standalone state-space implementation is the recommended first runtime because
physical-state reconstruction remains directly inspectable. Prepare both return
topologies, their scaled/factored operators and physical-state conversion maps
off the callback. Solve with a bounded prepared plan; no symbolic work, dynamic
allocation, file access or retries belongs in `process_frame`.

If WDF is chosen instead, resolve [erratum E02](research/ERRATA.md) explicitly:
`a=v+Rp*i`, `b=v-Rp*i`, positive `Rp`; capacitor reflection is the previous incident
wave, inductor reflection its negative. Verify open, short and source constraints,
both simultaneous root equations and the noncommuting order `I-Phi*S11`.
Prewarp uses angular frequency `2*pi*f`, not a hertz value relabeled radians.
Changed port resistances require physical-state conversion; copying old waves
unchanged is insufficient. [Atlas pp. 175-180.]

## 5. Rotor, selection and chorus reference

Keep three domains distinct: **19 line outputs, 9 selected terminals and 16
mechanical positions**. The atlas p. 170 depth table is:

| Semantic modes | One-based line outputs for terminals 1..9 |
| --- | --- |
| V1 and C1 | 1, 2, 3, 4, 5, 6, 7, 8, 9 |
| V2 and C2 | 1, 2, 3, 5, 7, 9, 11, 12, 13 |
| V3 and C3 | 1, 2, 4, 7, 10, 13, 16, 18, 19 |

Use exact semantic mode values. There is no seventh historical Off selector:
bypass belongs to Swell/Great tablets. Convert one-based output identity to array
index once after validation. An automated depth change selects another connection
map; it does not interpolate integer tap indices.

Page 166 prints fifteen traversal entries while indexing sixteen. The explicitly
**inferred** corrected zero-based traversal is:

```text
[0, 1, 2, 3, 4, 5, 6, 7, 8, 7, 6, 5, 4, 3, 2, 1]
```

Retain the original fifteen-entry text and [E01](research/ERRATA.md). Require a
separate comparison with the cited paper/factory mechanism before calling the
traversal documentary-verified. A synthetic interpolator may use this completion
under a name such as `inferred-triangular-scanner-v1`; its length/range tests do
not supply that missing documentary verification.

For the first unloaded approximation, interpolate the two neighboring terminal
voltages with complementary linear weights. This models capacitive overlap, not
metallic contact clicks. Define phase zero at terminal 1, direction and whether
each sample reads before advancement; use one continuing rotor phase in turns.
The atlas's documented nominal 412 rpm converts to `412/60` Hz. It is not a
measured specimen speed or a reason to round to 6 Hz. [Atlas pp. 163-168.]

Test all sixteen centers and intervals, wrap from terminal 2 to terminal 1,
one-hot terminal excitation, equal-terminal unity, negative signals and phase
continuity through silence, tablet bypass, selector changes and rate changes.
The two endpoint terminals appear once per cycle; each intermediate terminal
appears twice. Use an independently written phase/weight oracle, including values
immediately either side of a center and wrap. Reject nonfinite/out-of-range
inputs transactionally. Compare rotating sidebands with a converged higher-rate
reference and report the decimator's actual response/latency before integrating
the audio path.

For chorus, `v_k = r + z_k`, where `z_k` is relative to the common return and
`v_k` is relative to ground. Normalized scanning of the exported `v_k` already
includes `r` exactly once. A second arbitrary dry copy or a fixed 50:50 chorus mix
is not this circuit. Test a synthetic nonzero return with distinct local taps and
compare `sum(w*v)` to `r + sum(w*z)`. [Atlas p. 171.]

## 6. Proposed runtime boundary and later Engine integration

The first core module should own only the admitted line and rotor state. A useful
interface sketch is:

```cpp
// Proposal; no such API is implemented by this document.
Status prepare(const ScannerProfile&, const ScannerSpec&) noexcept;
Status reconfigure_sample_rate(double host_rate) noexcept; // stopped; atomic
Status process_frame(double input_volts, ScannerMode,
                     ScannerFrame& destination) noexcept;
```

`ScannerFrame` should copy nineteen ground-referenced tap voltages, common return
voltage, selected terminal identities, output, phase used, frame tag, sample rate
and model/boundary identity. Retain local-relative values separately if useful.
Preparation validates the complete candidate and leaves the previous prepared
model untouched on failure. Runtime histories include previous input, physical
reactive coordinates, rotor phase and any resampler tails; ordinary saved musical
controls contain none of them. Define finite input bounds and output/intermediate
bounds from the admitted network before accepting processing calls.

Set no public automation IDs in the first numerical commit. Once the module is
qualified, prepare a separate append-only parameter/state migration for two
tablets and six modes. Old states must default to both tablets off, preserving
their dry sound. Keep all existing parameter IDs, normalized thresholds, factory
UUIDs and legacy model meanings. Any control-count change also affects the fixed
HostTimeline anchors, StateExchange publication cells, native exports and their
independent tests; increasing the registry alone is incomplete integration.

Before audible integration, provide separate same-frame division quantities:

| Swell / Great | Scanner input | Direct sustained/pedal bypass | Percussion |
| --- | --- | --- | --- |
| Off / Off | 0 | U + L + P | Q remains downstream |
| On / Off | U | L + P | Q remains downstream |
| Off / On | L + P | U | Q remains downstream |
| On / On | U + L + P | 0 | Q remains downstream |

These are routing identities, not calibrated voltage gain equalities. The first
integration must name any normalized-unit-to-volt reference scale and its nominal
status. The later AO-28 graph owns actual drive/recovery/bypass gains and loading.
Use basis signals for U, L, P and Q so a rich chord cannot conceal misrouting.
Do not model a second scanner for the second manual or a private pedal scanner.
[Atlas pp. 169-174.]

Preserve the exact legacy output branch when the scanner is disabled. For the
newly enabled model, the shared line and rotor still advance when outputs are
disconnected. If both tablets are off, feed zero into the nominal line, retain
its decay and rotor clock, and mute only its audible wet contribution under the
explicit nominal bypass policy. Re-enabling a tablet exposes the preserved state;
it must not synthesize a cold start. Later circuit review may refine this boundary
under a new profile. Keep one common expression stage after the appropriate
combination; the present scalar is still a named surrogate.

Retain current event limits and stable same-sample order. A zero-frame flush
changes controls without advancing source, line or rotor clocks. At host scope,
failed fresh events, automation or state restores must preserve owners, controls,
carry, scanner state and future audio together. Expand meaningful rollback tests
with precharged line state; a silent output buffer alone cannot prove preservation.
The native allocation probe, concurrency test and audible partition tests need
the scanner-enabled path before their existing claims can cover it.

## 7. Acquisition records that can be prepared now

Use [CAPTURE_FORMAT.md](CAPTURE_FORMAT.md) and
[CAPTURE_PROTOCOL.md](CAPTURE_PROTOCOL.md). A planned hardware record has no
recorded timestamp, files or calibrated values. Missing specimen identity,
operator, permissions or calibration remains explicit. Existing v1 support/text
fields can point to a detailed schedule; do not add unofficial schema keys.

| Family | Required observables and units | Intended comparison / independence rule |
| --- | --- | --- |
| Preset wiring | Organ and AO-28 identity; every manual/preset/harmonic/tap assignment; image region, wire color, continuity evidence and reviewer. | All 162 fixed assignments; retain unknown connections. The chapel table does not identify the specimen. |
| Drawbar/contact motion | Position coordinate or physical displacement with calibration; contacts/conductance; source reference and dry volts; time in seconds with synchronized clocks. | Both motion directions, make/break, partial/repeated gestures and held collisions; preserve whole takes and related channels together. |
| Pedal electrical | Four bus voltages, known source/injection reference, two control positions, reactor H/ohms, loads in ohms/siemens and complex transfer. | Atlas p. 143 proposes 425 axis states plus 50 paired states = 475, not acquired files. Retain onset/sustain/release and held-out pedals/mixtures. |
| Expression | Heel/toe/angle mapping; loud/soft capacitance in farads; input/output volts, load, feedback revision and synchronized motion. | Stationary positions first, then slow/fast reversals and several input levels. Preserve absolute calibrated versions as well as normalized analysis. |
| Scanner identity | Line assembly, connected AO-28 revision, mains region, component changes and terminal-to-schematic crosswalk. | Compare the selected paper model and production circuit explicitly; historical patent topology is a different profile. |
| Stationary scanner line | Synchronized drive and each accessible tap in volts; ground/return polarity; source, receiver and probe impedance; both return states. | Complex transfer, uncertainty and repeatability before fitting; retain simultaneous input reference if taps require separate runs. |
| Rotor and six modes | Angle in turns/radians with phase origin, physical timebase, drive/output volts, actual speed, four tablet combinations and V1-V3/C1-C3. | Entire repeated revolutions and unseen frequencies/registrations held out; one shared angle estimate, not a private fitted phase per tone. |
| Quiet and transition records | Unaveraged quiet/driven channels, timestamped controls, pre-event phase/state, acquisition gain and noise floor. | Distinguish source modulation, hum, brush residue and switching from the nominal line; no denoising overwrites raw evidence. |

Internal electrical acquisition remains an evidence request for a qualified
technician using an approved setup, not a live servicing procedure. Capture
manifests must record V/FS or A/FS calibration, physical clock Hz and uncertainty,
not just a WAV header rate. The current per-file validator checks declarations
and optional artifact bytes; it cannot establish loading, synchronization, rights,
physical admission or corpus-wide holdout independence.

Freeze grouping before fitting. One take, synchronized channels, repeated exports
and all derivatives remain in one lineage/group. Reserve complete repetitions,
selected frequencies and mode/control conditions for development validation and
untouched final evaluation. Numerical simulations are labeled synthetic and never
substitute for the missing hardware rows. Fit line response before rotor overlap,
then combined modes; retain one parameter set across modes and report correlated
or unidentified parameters. [Atlas pp. 161, 167, 173, 187-192.]

## 8. Ordered implementation tickets and exit evidence

| Order | Owned change | Required exit evidence |
| --- | --- | --- |
| **Next: scanner graph admission** | New authoring schema/profile/compiler and independent endpoint review; no Engine, registry or state-format changes. | All 50 elements and 19 output references checked against p. 158 and an independently consulted primary circuit; SI conversion, bounded malformed-input and graph-mutation tests. Explicit unresolved source/load/coil/scanner fields. |
| **Then: offline AC oracle** | Readable independent graph stamping and all-tap response report. | Both return states, rational DC known answers, scaled residuals, conditioning, load sensitivity and complete source/code/result identities. |
| **Then: standalone prepared line** | Fixed-storage C++ line, both topologies and physical-state migration. | Independent AC parity, converged transients, energy/constraint checks, rates, rejection preservation and allocation bounds. |
| **Then: rotor and six-mode reference** | Typed maps, one phase and explicitly scoped overlap model. | Resolve E01 documentary gate; one-hot/unity/wrap tests, signed chorus return once, bypass history and higher-rate sideband comparison. |
| **Then: opt-in Engine/native integration** | U/L/P/Q boundary, state/parameter migration and actual host surface. | Exact disabled-path legacy audio; all routing cases; state/automation/carry rollback with nonzero circuit energy; actual native enabled allocation/concurrency/partition gates and exact platform qualification. |
| **Parallel: remaining M3 data and numerical work** | Independently reviewed chapel matrix, latch state, branch/travel contracts, loaded expression/pedal reference models. | Separate data, behavior, numerical and acquisition results; no guessed specimen or silent replacement of the current nominal models. |
| **After acquired evidence: physical fit** | Admitted raw corpus, uncertainty-aware fitting and held-out report. | Predeclared criteria derived from repeatability; full failed/inconclusive results; no claim of complete M3/M4 or instrument fidelity before these pass. |

Every ticket must read the latest handoff and declare file ownership, freeze a
coherent source before qualification, retain commands and failures, then provide
the integrator with status, next action and evidence. Commit/push remains governed
by [AGENTS.md](../AGENTS.md). This plan changes neither the completed agents'
participation nor any historical qualification result.

## Review record

[Assignment 47](development/2026-11-13-pedals/47-next-model-gate.md) records the
66 freshly reopened atlas pages, eleven actual rendered-page inspections,
inspected code/data identities, arithmetic checks and limits. This assignment
implemented no scanner, acquired no hardware and ran no scanner DSP or host test.
