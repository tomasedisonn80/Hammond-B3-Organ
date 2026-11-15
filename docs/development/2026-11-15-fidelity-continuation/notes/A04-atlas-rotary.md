# A04 — complete atlas reading, pages 253–336

**Worker:** `/root/w01_a04_atlas_rotary`, wave 1 of the new
`2026-11-15-fidelity-continuation` session. This note records one actual assigned
reading and design review. It does not reuse the previous product session's A04.

## Scope, source identity and work performed

Read the entire current `AGENTS.md` and `docs/PLAN.md`, then every extracted page
from **253 through 336 inclusive**: 84 pages, 26,480 whitespace-delimited words,
chapters 041–054. The ordered page-marker check matched `range(253, 337)` exactly.
The first 253–264 tool result truncated a small passage, so pages 258–259 were
read again in full; no page remained omitted. Read current crossover contract,
characterization, public API and relevant implementation, plus current routing,
status/next-step/log/handoff entry sections. Rendered and personally viewed PDF
page 272 at 1,400-pixel maximum dimension to check the electrical figure against
the extracted node table. No external cited factory drawing or physical specimen
was independently inspected by this assignment.

| Input | Identity |
| --- | --- |
| Observed checkout HEAD | `878d3ce82a10a0ae335dab377683ec543f194957` |
| Observed HEAD tree | `7d63b272d7dd04be65869db5687a1d7f29994e1a` |
| Source PDF SHA-256 | `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769` |
| Complete assigned extract SHA-256 | `6719ad07377c8b2f6f7f466c0a392a70c95bb2268dfeccf69ffdc838f21bba62` |
| `include/hammond/LeslieCrossover.h` SHA-256 | `54efff218f873045bd07a2eb3270d07637e3f3fc5d2d51bac032b7efca53559c` |
| `src/LeslieCrossover.cpp` SHA-256 | `1a1bdde72af95709143afc4f62991c138ff3458cc78765fbe49a229d82693525` |
| `tools/crossover_reference.py` SHA-256 | `33eaa88da2534e52f88c044b5fbabf19828655bacb357dc55bbeb6510b580ec5` |
| `data/crossover/leslie-122-ideal-v1.json` SHA-256 | `f55fa98c246b4a19dce12ca829a141cff744f71242cccb68db12b404400319cc` |

The prepared extract is
`/workspace/scratch/63071f51f1e4/atlas-text/A04-pages-253-336.txt`.
The transient PDF render is under the same workspace's `a04-pdf/`; it is not a
new source asset. The working tree contained the new shared session directory;
this worker owns and writes only this note. Root owns live publication queries,
shared documentation and all builds. An observed local HEAD is not an independent
live remote verification by A04.

## Findings from every assigned chapter

| Chapter and pages | Complete-range interpretation and implementation consequence |
| --- | --- |
| **041, 253–258 — 122 input/control** | The selected documentary baseline is the 1971 117 V rotor amplifier 036616, separate from optional reverb, 50 Hz assembly and modern 122H. V1 senses one input leg for rotor control; V2 carries balanced audio. Full differential voltage is `va-vb`, while common mode is `(va+vb)/2`; reducing these incorrectly changes drive by a factor of two. Model source loading and detector coupling separately, preserve timestamped relay-to-motion continuity, and acquire dual-leg/transition measurements before claiming detector thresholds or rejection. Topology, numerical agreement and hardware match are three separate gates. |
| **042, 259–264 — 147 differences** | A 147 uses a single-ended input and its own phase-driving, bias and winding-feedback connections. Its OPEN/8/16 console-load selector belongs to the input boundary, independently of the cabinet speaker load. Shared transformer inventory cannot justify a shared complete transfer function. Trace one dated circuit, preserve its revision and loading contract, establish linear operating point before nonlinear fitting, and validate voltage gain, intermodulation and recovery without silently normalizing drive. Neither qualitative brightness nor modern Heritage data determines the vintage model. |
| **043, 265–270 — power stage** | The 6550 pair, shared bias, screen current, supply, transformer and crossover form an interacting electrical network. Winding polarity and full-primary versus half-primary turns conventions are essential. The 0C3 is in a series-drop path rather than an independent ideal screen rail. Fit linear connected topology and DC first; add nonlinear currents and any supported magnetic memory later. Oversample the complete coupled nonlinear region and measure its convergence/alias budget. Valve datasheet curves initialize a model but do not characterize a cabinet's fitted valves, transformer or supply. |
| **044, 271–276 — crossover** | The atlas supplies four documentary values and a floating treble topology: L2 3.2 mH and treble load in parallel A–H, C16A 7.8 μF H–B, L3 5.2 mH A–W, C16B 12.5 μF and bass load in parallel W–B. Keep 052803 (1971) and 113860 (1979) identities distinct. `VT=VA-VH`, `VW=VWnode-VB`; both branch currents contribute at the input. Constant 16-ohm loads are an explicit algebra fixture. The nominal 800 Hz label does not prescribe generic textbook filters or complementary acoustic summation. Numerical acceptance requires both complex output ports, input admittance, energy/state behavior and declared sample-rate treatment. Actual losses, complex loads, polarity and serial applicability remain unknown. |
| **045, 277–282 — horn** | One stationary compression driver feeds one rotating horn; the other horn is a mechanical counterbalance, not a second electrical radiator. A moving acoustic mouth is a reduced model, with emission-time geometry and angle-dependent complex response. Published Leslie 600/University ID-40 data support methods rather than a calibrated target 122. Preserve angular gain/phase, separate every included driver/horn/propagation/cabinet/microphone factor, and require fixed-angle and synchronized moving held-out captures. |
| **046, 283–288 — bass rotor** | The woofer stays mounted while a deflector rotates. Orientation-dependent transmission, path delay and enclosure interference require separate declared ownership. Low frequency does not mathematically imply zero fractional Doppler; effective delay radius is not physical cone orbit. Persistent FIR bases with periodic angular weights are a useful provisional implementation. Keep the static-angle output, wrap, sidebands, delay removal and shared stereo motion testable. Published horn data do not supply a bass model. |
| **047, 289–294 — motors/belts** | Horn and drum have separate drive assemblies, pulley/line-frequency identities, speeds and transition parameters. Distinguish shaft and rotor speed. Begin with an identified exponential-speed surrogate and analytic angle integration; move to torque/slip/inertia only when measurements identify it. Select upward/downward time constant from target minus actual speed, retain momentum during reversals, and evaluate with stable `expm1` arithmetic. The 5–8 second bass service criterion is not a universal time constant. Stop/coast/brake require named accessory profiles and never mean instantaneous speed zero or angle reset. |
| **048, 295–300 — cabinet** | A specimen passport and panel state precede acoustic CAD. Equal external envelopes do not establish internal volume, louvres or response. Keep visible texture, measured geometry, air paths, structural modes and room separate; retouched artwork supplies no dimensional evidence. Start with fixed-angle complex horn/drum kernels, then moving interpolation and microphones; add reflection or panel branches only for an identified residual. Hold out poses, angles and transitions and retain signed summation. Missing dimensions, construction and calibration remain null. |
| **049, 301–306 — retarded propagation** | Solve `t=e+r(e)/c` using the shared historical trajectory, including pre-command motion. The chapter independently audits a coordinate-sign and a linear-interpolation endpoint error in its cited material. Bound root iterations, waveform/history capacity and any extra algorithmic latency. Cubic Lagrange is a useful prototype with measurable high-band error, not an ideal delay. The atlas reports only a particular synthetic root/derivative fixture; it does not supply production interpolation, alias or physical acceptance. |
| **050, 307–312 — directivity** | Radiation is a complex transfer at a defined electrical/acoustic boundary. Use the same emission geometry for angular response, distance and propagation; fixed cabinet walls cannot rotate with the horn. Periodic real FIR/Fourier bases preserve signed phase and gain, with order chosen from held-out residuals. Angular order times speed adds modulation bandwidth. Do not infer motor accelerations from instantaneous-frequency spikes at interference nulls. The chapter's tiny synthetic algebra errors do not qualify a 122 radiation profile. |
| **051, 313–318 — microphones/stereo** | MicSceneProfile is independent of instrument/amplifier identity. Source-to-mic bearing and microphone incidence have opposite signs; retain capsule coordinates, orientation and channel timing. Stereo channels query one physical rotor at their own emission times. Mono cancellation may be physically correct, and polarity reversal is not broadband time alignment. Sum arriving paths with their own directional receiver response before the output matrix. Physical motion and a convenience scene crossfade need separate policies. Numerical incidence/comb checks do not validate actual microphone responses. |
| **052, 319–324 — rotor execution** | Persistent physical state and event-anchored segments make timing independent of note events, host blocks and GUI refresh. Preserve phase/speed at commands, keep historical segments for delayed paths, and use explicit suspension/rate-epoch policies. Ordinary musical presets are separate from complete numerical checkpoints. Actual host translation and bounded queues need their own tests; synthetic event-reference agreement is not plug-in or physical qualification. Accessory braking cannot be inferred from an asymptotic zero target. |
| **053, 325–330 — varying convolution** | Frozen-angle data do not identify a time-varying operator. Applying angle weights to current filter outputs and applying them to each historical input produce different moving systems. Never move weights across convolution merely to share FFTs. Keep persistent FIR/overlap history, periodic weights, reversible delay decomposition, prepared warm replacement banks and a fixed activation sample. Complementary amplitude fades preserve identical coherent outputs; equal-power fades raise their midpoint. Published arithmetic workload is not a CPU benchmark, and the atlas's small partitioned-convolution fixture is not a production/deadline/fidelity pass. |
| **054, 331–336 — room/RV** | Room, cabinet and microphone contributions each need one owner. Reflected paths have individual emission geometry. A two-input/two-output room requires all four kernels unless absent crossfeed is established. Preserve common time zero, full tails and algorithmic versus acoustic delay. Optional 122RV spring reverb branches from the main amplifier through a lamp/tank/return-amplifier path to a fixed speaker; it is neither generic room reverb nor a rotor-fed wet branch. Complementary early/late windows and controlled FDN loss are separate proposals; no room, RV, FDN, deadline or physical measurements were performed by that chapter. |

## Next M6 numerical candidate: explicit FOH research realization

**Recommendation, not an implemented or accepted result:** evaluate a separate
physical-state realization with an exact continuous linear transition under
piecewise-linear endpoint input, usually called first-order hold (FOH). Preserve
`physical-trapezoidal-leslie-crossover-v1`, its API semantics, all reports and
the fixed documentary registry. A separate candidate ID/class avoids quietly
changing v1's sound, checkpoints or energy test. The candidate remains outside
Engine and acquires no new physical status.

For the existing literal KCL system `dx/dt=A*x+B*u`, define interval duration
`h=1/fs`, input endpoints `u0` and `u1`, and `u(t)=u0+(u1-u0)*t/h` for
`0<=t<=h`. Then:

```text
Phi = exp(A*h)
Gamma0 = integral[0,h] exp(A*(h-t))*B*(1-t/h) dt
Gamma1 = integral[0,h] exp(A*(h-t))*B*(t/h) dt
x1 = Phi*x0 + Gamma0*u0 + Gamma1*u1
```

The four coordinates remain capacitor volts H–B/W–B and inductor amps A–H/A–W.
The previous endpoint and completed-frame count remain explicit checkpoint
fields. Reconfiguration prepares new operators while stopped, retaining those
physical coordinates and endpoint exactly; it creates no synthetic interval.
Endpoint output uses the original signed electrical port equations.

An augmented matrix exponential for `[x, u, du/dt]` supplies both forcing
integrals without forming a fragile inverse of A. Preparation belongs off the
processing path. The runtime needs one fixed matrix-vector operation and two
input vectors per frame, with the same explicit admission, bounded work and
whole-block transaction obligations. This is a design suggestion; no numerical
conditioning, workload or allocation result was executed by A04.

For an endpoint sinusoid with `z=exp(j*2*pi*f/fs)`, the candidate's actual
recurrence response is independently expressible as:

```text
X = solve(I - Phi/z, Gamma0/z + Gamma1)
Y = C*X + D
```

Use the appropriate C/D for each voltage port and input current. Do not call the
native response helper the independent oracle. An independently stamped ODE,
converged integration with the same input segments, and a separate analytic
frequency calculation can test the implementation and transient reference.

### What this candidate resolves and what it does not

FOH separates integration error from external input reconstruction. It removes
the trapezoidal method's nonlinear frequency map from the **declared continuous
piecewise-linear-input experiment**. It does **not** reproduce an ideal
continuous sinusoid between sparse endpoints, so its same-Hz sinusoidal error
must still be measured. A small integration residual is not a full-band accuracy
pass. Similarly, merely substepping trapezoidal integration with linearly
interpolated endpoints tends toward this FOH experiment; more substeps do not
erase its external reconstruction error.

Freeze a versioned acceptance protocol before implementing or tuning the
candidate. The protocol must retain two distinct comparisons:

1. **Hold-matched numerical accuracy:** actual processed outputs and precharged
   state against an independent continuous FOH reference, with its convergence
   error bounded separately from the candidate error.
2. **Same-Hz electrical usefulness:** signed complex treble gain, bass gain and
   input admittance against the original analog sine reference at the same Hz.
   Publish all points, not just 800 Hz. Use separately justified magnitude/phase
   criteria above declared gain floors and absolute complex criteria below them;
   current has its own A/V budget. A failed band or load remains failed.

Keep the existing four external rates and declared resistor domain unless a
reviewed protocol explicitly changes them. Include independent check frequencies,
near-DC and near-Nyquist observations, the six current load pairs and extreme
admitted loads where the candidate promises support. No threshold in this note
is claimed as an audible or manufacturer specification.

The v1 trapezoidal midpoint energy identity is not an FOH energy oracle. Use
continuous integrated source work and resistor dissipation under the declared
ramp, or an independently converged quadrature, and test zero-input precharged
decay with a zero previous endpoint. Preserve rejection rollback, next-valid
continuation, rate transitions, block partition invariance, subnormal policy and
calibrated allocation checks. Report algorithmic latency explicitly if later
band-limited interpolation/filtering is introduced to address residual same-Hz
error; that would be a further realization with filter history and rate-transition
obligations.

## Integration boundaries and immediate handoff

The existing [characterization](../../../LESLIE_CROSSOVER_CHARACTERIZATION.md)
shows why both relative and absolute quantities matter: at 44.1 kHz/20 kHz, the
retained v1 bass magnitude difference is about −27.15 dB at an already attenuated
port, while the treble complex difference is about 0.05049 V/V despite a tiny
magnitude change. These are quoted prior report observations, not rerun results.
The full input-admittance criterion cannot be inferred from either output.

The parent can assign a protocol author/reviewer followed by independent native
candidate and reference owners. The prerequisite inputs are already present:
fixed registry, KCL state/ports, v1 executable/reference and original failures.
No missing specimen data blocks this nominal numerical experiment. Missing
source impedance, winding/capacitor losses, actual driver impedances, amplifier
operating points and acoustic captures still block the coupled M6/physical claim.

M7 R4 remains owned by the separate waveform session. This reading supplies
constraints for later R5/R6 work, not permission to take over its checkout or
connect ideal crossover output to the live dry Engine. Preserve 47 parameter
identities, state4/readers1–3 and 91 shared sources. M9 visuals may advance using
their own current contract without inventing working speed, microphone or room
controls or letting GUI animation own the rotor clock.

## Verification and limits

Executed only bounded text reads, the complete ordered page-marker check,
source/extract hashes, local source inspection, one PDF page render and direct
image inspection, and note whitespace/status checks. No compilation, native
processing, mathematical candidate experiment, CTest, callback measurement,
physical capture or publication was performed by A04. The proposed FOH method
needs its own independently frozen contract and observed acceptance; this note
does not claim a same-Hz improvement or a completed model gate.
