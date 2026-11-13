# M3 continuation acceptance contract

**Disposition: proposed acceptance gates, all unrun by this assignment.** This
document supports the active contact/percussion continuation; it does not select
a competing implementation, add a schema, or close M3. Its implementation owner
and sample convention are the separate [continuation ledger](development/2026-11-13-continuation/README.md)
and [continuation review 02](development/2026-11-13-continuation/02-atlas-085-168.md).
Bind each future result to the implementation contract actually integrated.

Code inspection is at **`6c3dd8bc923a3c11f6b234425b056e135fbe9f4b`**:
[`Engine.cpp`](../src/Engine.cpp), [`Engine.h`](../include/hammond/Engine.h),
[`Types.h`](../include/hammond/Types.h) and the control interfaces implement ideal
Boolean physical keys, four retained banks, Cancel and control-only persistence.
No contact/percussion module was present in the inspected local tree. Local
`main` and the existing `origin/main` tracking ref both named that commit; this
assignment did not fetch, refresh the remote, reset, build, or test the shared
branch. The separate ledger showed wave 02 in progress. A later contract must be
reviewed before applying these gates; absence here is not a claim about unseen
work in the other session.

## Source and identity boundaries

Read directly: all atlas chapters **017–024, PDF pp. 109–156**, from the supplied
page extractions. Source: [preserved atlas](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf),
evidence edition 2026-11-12, SHA-256
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
References below are one-based atlas pages. Its cited factory manuals and the
1967 C-3 contact study were not independently reacquired for this assignment.

| Atlas basis | Acceptance consequence |
| --- | --- |
| Ch. 017, pp. 109–114 | Evaluate distinct branches before source aggregation; preserve coherent amplitude addition and fixed headroom. Nominal gains are dimensionless, not measured transformer taps. |
| Ch. 018, pp. 115–120 | Nine histories per key share a mechanical gesture; make and break are separate. MIDI motion is synthetic; velocity may alter transitions, never settled organ gain. Phase, partial travel and switched-signal bandwidth need explicit tests. |
| Ch. 019, pp. 121–126 | Retain all banks; Cancel changes routing. Upper-B interlock changes notify percussion without resetting its history. Physical latch overlap needs a separate network model. |
| Ch. 020, pp. 127–132 | One upper-manual control process; keying is the **1-foot/ninth contact**, the eighth harmonic. Physical detector, route eligibility and charge/readiness are distinct. Zero-duration opening provides no recovery. |
| Ch. 021, pp. 133–138 | Reuse second/third-harmonic shared sources; separate percussion audio, sustained return, upper compensation, gain and decay/bias controls. Electrical RC products are not measured audible decay lengths. |
| Ch. 022–024, pp. 139–156 | Pedals retain their eight contacts/four buses; expression has a common path; ownership precedes contacts; persistent controls and running histories remain separate. |

Preserve `nominal-unmeasured-v1`, `ideal-shared-sine-v1`, `B3PROFILE 1`,
`B3CONTROLS1`, existing EventType values 0–7 and all 39 registry meanings.
New controls/models need their owner's explicit version/default/migration
decision; tests must reject unsupported versions. Do not silently extend strict
v1 files or reinterpret expression ID `0x2000` as physical pedal travel. Retain
an ideal-contact/percussion-off compatibility mode and the original profile/data
digests. See [profile](PROFILE_FORMAT.md), [controls](CONTROL_STATE_FORMAT.md),
[parameters](PARAMETERS.md) and [console](CONSOLE_EXTENSION.md) contracts.

## Common fixture and trace contract

Each gate names code/build identity, compiler/mode, source/profile/contract hashes,
contact and percussion model IDs, all parameters and evidence classes, initial
controls/history, seed/event identities, absolute event order, sample rate, block
partition, declared latency, output boundary, oracle, tolerance and result.
Synthetic fixture values are engineering inputs, never specimen measurements.

| Coordinate or observation | Required meaning |
| --- | --- |
| Manual/key/contact | Upper/lower; MIDI 36–96 and physical key index 0–60 are recorded separately; contact index 0–8 follows drawbar order. Source ID 1–91 is neither MIDI nor terminal number; source array index is ID minus one. |
| Time | Absolute unsigned frame plus fractional frame if supported; seconds are elapsed frames divided by rate. Retain rounding and edge-order rules. Integer-only models cannot pass a fractional-edge claim. |
| Motion/contact | Normalized position/target and connection weight are dimensionless. Thresholds, make/break durations, optional bounce and edge origin identify their proposed or measured basis. Conductance, if used, is in siemens; resistance is in ohms. |
| Percussion | Physical detector `D`, routed eligibility `E`, routed detector `g`, shared readiness `q`, gain and harmonic source sum are separate observables. `q` in [0,1] is dimensionless; it is not capacitor volts. A voltage model instead records volts and reference node. Time constants use seconds. |
| Audio/expression | Baseline source peak, mix and expression scalar use declared normalized units. Physical voltage/pressure comparisons require calibrated units, boundary/load and uncertainty. Expression position, legacy gain surrogate and downstream monitoring gain are different quantities. |

Trace event application order/outcome, physical key target and position, all nine
contact states, source IDs and relevant phases, `D/E/g`, shared state before and
after advancement, sustained/percussion contributions and final output. Diagnostic
copying follows same-thread/stopped access; allocate trace storage before running.
Observe state independently of audible gain: zero drawbars, Cancel, expression
zero and disconnected output cannot serve as evidence that contacts stopped.

Use the continuation's declared convention: at sample `n`, apply the already
merged stable-order events, resolve contacts/routes, render from the current
source frame and `q[n]`, then advance motion, readiness and sources once for
`1/Fs`. Ideal events can change contacts immediately; trajectory target changes
do not themselves advance time. A zero-frame flush applies/reconciles events once
but advances no motion, readiness, source phase or clock. The existing core
retains supplied ties; an eventual host adapter's route-first merge policy from
p. 153 must not silently reorder legacy core lists.

For the **existing continuation proposal**, `D` is the OR of upper contact 8,
`E = percussion_enabled && upper_route_enabled && upper_bank == B`, and
`g = E && D`. Its independent mathematical oracle is
`q(t+dt) = target + (q(t)-target)*exp(-dt/tau)`, with target 0 during routed
keying and 1 during recovery. These are a nominal policy and surrogate from
pp. 128–129, not established held-key hardware switch behavior. Preserve the
actual adopted gain function separately from `q`; use a unity routing probe
before testing it. Any replacement contract needs an explicit gate mapping.

### Parameterized timeline notation

`N0` is a declared absolute frame origin; `Tmake(v)` and `Tbreak` come from the
selected contact test profile. `Nsettle` is the independently predicted first
sample after every intended contact settles. Let `R` be the first sample whose
resolved detector is released; a command's NoteOff time is not necessarily `R`.
Let `Dframes` be the exact count of rendered decay samples and `L` the exact count
of released-detector samples. No physical contact order or measured duration is
assumed. Every fixture instantiates these symbols in its retained input record.

For recovery sweeps, use separate identical initializations and
`L ∈ {0, 1, round(Fs*tau_recover/10), round(Fs*tau_recover),
round(4*Fs*tau_recover)}`; retain actual distinct integer counts and their seconds.
These are synthetic sample choices. In the ideal reference, after a hold from
`q=1`, `q0=exp(-Dframes/(Fs*tau_decay))`, and re-entry after `L` open samples uses
`1-(1-q0)*exp(-L/(Fs*tau_recover))`. The oracle compares state, not raw waveform
peaks at unrelated source phases.

## Required event/history scenarios

All IDs below are **proposed tests, not existing CTest target names or results**.
Run contact tests with percussion/leakage bypassed unless the scenario says
otherwise. Independent expected histories must not call the implementation's
trajectory, detector or envelope helpers to derive their answers.

| ID | Reproducible timeline | Falsifiable result and retained evidence |
| --- | --- | --- |
| **C1 — nine histories** | From all-open, press one key at `N0`, wait beyond `Nsettle`, release; repeat for both manuals and candidate profile boundary keys. In separate synthetic trials stop at a declared partial target; reverse before make completes and again during break. Exercise ties and distinct threshold orders without declaring either physical. | Trace all `2×61×9` addressable contacts, shared per-key motion and separately parameterized make/break. Only the independently predicted subset conducts; reversal starts from current state, not a new attack origin. Supported bounce/replay preserves every ordered edge across block boundaries; absent bounce/fractional support is recorded. [pp. 117–120] |
| **C2 — phase and collisions** | Isolate upper MIDI 36 contact indices 0 and 2, both source 13 in the retained map. Replay each branch alone and both from identical source histories; stagger their edges, then release one while the other holds. Separately place a synthetic edge at a known source peak and zero crossing. | Nominal coefficient is `c0*gain(p0)+c2*gain(p2)` before multiplying the same source sample. Distinct states survive the collision; settled equal branches give twice amplitude, without key-count normalization. Both drawbars at zero give exactly zero intended contribution. Compare analytic value jump and slope behavior; a zero value jump alone does not pass antialiasing. No source/filter reset on release. [pp. 111, 116, 120; factory row key 1] |
| **C3 — velocity** | With identical seed, `N0`, registration and fully settled evaluation window, render separate nonzero velocities 1, 64 and 127; include release before settling. Compare absolute-time windows beginning after the slowest `Nsettle`. | Trajectories follow the selected nominal velocity law, if enabled; steady branch coefficients and steady audio are equal. Legacy ideal mode remains unchanged. Velocity zero retains the current core's release meaning; host interpretation is tested separately. [pp. 117, 152] |
| **R1 — retained banks/Cancel** | Give all four banks distinguishable positions. Hold upper and lower keys; edit hidden upper A, select A, Cancel upper, edit its selected bank, then reselect A without another NoteOn. Repeat on lower. | Hidden edits do not change the active registration; selection never copies a bank. Cancel preserves held keys, pending contacts, phases and all controls while suppressing that route. Editing does not reconnect; reselect does. Other manual remains active. Percussion state follows R3, never an automatic reset. [pp. 114, 121–126] |
| **P1 — detector and eligibility** | Use zero drawbars, upper B and percussion enabled. Through an explicit synthetic partial/contact realization, vary upper contact 8 separately from the selected harmonic contact; repeat with upper A, route cancelled, lower-only keys and eventually pedal-only keys. | `D` follows upper contact 8 even with its drawbar at zero; contact 7 is not the detector. `E` follows the versioned route/tablet truth table; `g` is separately visible. Selected harmonic audio can be absent while keying is present or vice versa. Lower/pedal contacts never enter the upper detector. [pp. 127–128] |
| **P2 — one shared decay** | Fully recovered upper B: press `k1`; at `N0+J` during decay press `k2`; release `k1` while `k2` remains; add/release another note. Include same-key duplicate physical NoteOn. | No joining note or duplicate resets shared `q`. Current selected-harmonic contacts join the existing envelope; the first note's source sum is not frozen. One remaining detector contact prevents recovery under fixed eligible routing. Releasing a non-last key leaves decay history intact. [pp. 129–132] |
| **P3 — finite recovery** | Establish the same `q0` using `Dframes`, release every upper key, determine actual `R`, then repress after each prescribed `L`. Repeat while lower keys remain held and, once implemented, with pedals held. | Compare the exact state recurrence above, `0≤q≤1`, finite long-hold/long-gap limits and monotonic recovery versus actual open-contact time. A NoteOff whose contact has not opened supplies no release interval. Lower/pedal activity changes no upper recovery. No arbitrary all-up Boolean recharge. [pp. 129–132, 135] |
| **P4 — same-frame order** | At a decayed held-key state, submit `[off(k), on(k)]` at frame `N`; repeat `[on(k), off(k)]`, `[off(k1), on(k2)]`, and explicit tied contact edges. Run each once inside a positive block and once in an offset-zero flush followed by rendering. | Preserve input/stable edge order and the corresponding final targets/contact states. Both orders consume **zero** recovery time at `N`; any later opening is determined by the trajectory. Compare `q` immediately before/after flush exactly. Replaying the consumed flush is a caller error, not a second timed interval. [pp. 130, 153, 156] |
| **R2 — harmonic/audio routes** | First use a unity-envelope routing probe, then the actual gain model. Sweep second/third selection, selected sustained drawbar 0–8, upper/lower 1-foot registrations, normal/soft and fast/slow, including changes during a held chord. | Reuse mapped shared sources at indices 3/4; selected drawbar changes sustained return without directly scaling percussion. Return is added exactly once. Upper-B 1-foot mask is route-specific; lower stays intact. Normal compensation affects only the upper sustained path, not lower/percussion. Rate and bias, percussion gain and compensation are separately observable and versioned; no invented numeric ratios. [pp. 134–138] |
| **R3 — held routing history** | Begin with known decayed state and held upper key. At `N1`, B→A; after `L` rendered samples return to B. Repeat Cancel/reselect, percussion off/on, same-frame pairs and lower-only selections; repeat with an actual fixed preset when available. | Retain shared state at each switch. Under the continuation's nominal routed-detector policy, ineligible intervals recover according to their actual length; re-entry uses that state. Test mask, compensation and harmonic route at the same event sample. Lower selection cannot enable upper percussion. Pass labels **nominal policy only**; physical transient/charge-path agreement stays unresolved until captured. [pp. 124, 128, 131–132] |
| **E1 — expression** | During a held chord and ongoing percussion, apply legacy expression values 1→0→0.5→1 at known offsets, including rapid reversal and an offset-zero flush. Compare against identical unattenuated state history. | Current scalar multiplies the common mix once; zero output does not stop source/contact/recharge evolution. No reset/retrigger. A future physical expression profile requires its own units/version and preamp-boundary tests, stationary/gesture transfer and downstream-drive evidence; do not substitute this scalar test. [pp. 145–150] |
| **S1 — ownership and persistence** | Retain legacy repeated physical press/release behavior. When a host adapter exists, two independent owners hold one key; release one, change input mapping, then release the original owner. During live sound apply the same valid control snapshot twice; try an invalid snapshot/version. | Adapter keeps one physical depression until last release, retains original destination and has bounded duplicate/unmatched/overflow policy. Current live control restore preserves keys/phases/time; extension must preserve contact/readiness history. No ordinary save contains owners, pending edges, `q` or phases. A fresh project starts with no held keys. Invalid restore is atomic. [pp. 130, 151–156] |

## Numerical, compatibility and failure gates

| Gate | Exact required comparison |
| --- | --- |
| **N1 — partition/time** | Replay every applicable timeline at 44,100/48,000/96,000 Hz using absolute timestamps. At one rate/build, compare blocks 1, 7, 64 and the prepared maximum plus irregular splits immediately before/on/after edges. Include nonzero clock origin, zero-frame flushes and disconnected output. Require identical discrete histories/source phase and the adopted contract's float agreement; preserve existing bitwise ideal-mode comparisons. Across rates compare physical elapsed times with the declared integer/fractional timing budget, not byte-identical audio. |
| **N2 — bounds/atomicity** | Probe zero/nonfinite/negative timing constants, invalid thresholds/contact indices/units, malformed traces, unsorted/out-of-range events, exactly-full and overfull storage, short output, block overflow and 64-bit clock/pending-edge overflow. For invalid prepared profiles or core requests require zero consumption and unchanged outputs, controls, source phases, clock, contacts, pending edges and percussion state. Follow with a valid suffix to expose hidden mutation. Future adapter overflow recovery is separately bounded and cannot weaken core atomicity. |
| **N3 — numerical/reference** | Compare readiness to an independent exponential oracle over held, released and changing-mode segments; declare tolerance before running. Require exact no-time state preservation, finite bounded long runs and no block-based Euler drift. Compare switched audio to scalar routing first. A bandlimited/fractional fidelity claim additionally needs a converged high-rate oracle, reported latency/cost and predeclared nonzero-reference normalized RMS target (atlas p. 120 proposes `1e-4`, an engineering target). Near-zero references need an absolute residual criterion, not division by zero. An integer nominal model may leave that latter gate blocked. |
| **N4 — real time/compatibility** | Require zero callback allocation/deallocation, locks and file I/O over maximum contacts/events, rejection and long release/recharge histories; retain measured callback scope, not an unconditional deadline claim. Run existing engine, controls, persistence, profile, numerical, factory-routing, renderer/evidence and allocation regressions with ideal contacts/percussion off. Execute the full configured Release matrix and applicable sanitizer gate for the integrated commit; retain failures and platform limits. |

Tests must also demonstrate that registration, key release, expression and
disconnected output do not prepare/reseed any of the 91 sources. Preparation is
the documented fresh initialization; no live sample-rate migration exists at the
inspection baseline. A future migration API needs state/phase continuity tests
before that separate claim, rather than treating a fresh `prepare` as migration.

## Dependencies that remain visible

**Presets:** R1 covers the existing exclusive A/B model. A full fixed-preset gate
requires reviewed 18×9 assignments, leading zeros and profile identity; p. 122's
chapel matrix is optional documentary data, not universal wiring. Test fixed
versus equivalent drawbars, inactive-bank edits and B interlock histories.
Simultaneous physical latches require branch/loading evidence, not a sum of two
gain vectors. Physical Cancel preserves pedals as well as the other manual
(pp. 121–126); the current manual-only engine cannot execute that pedal clause.

**Pedals:** require all 200 mapped positions, 195 connections/five nulls,
explicit 7/8 and 12/13 boundaries, separate duplicate-source contacts, four buses
and two drawbars. Then test pedal/manual coherent shared-phase sums against a
declared linear oracle, or against a loaded-network oracle for that model.
Preserve held pedals across manual Cancel/selection and exclude them from the
upper detector. [Pedal routing data](PEDAL_ROUTING.md) supplies identities, not
reactor values, mixture weights or measured low-wheel spectra (pp. 139–144).

These dependencies and calibrated expression remain open after nominal
contact/percussion acceptance. Scanner-bypass routing of percussion has its own
integration gate once a scanner exists (p. 138); it is not currently executable.

## Implementation-to-acquisition bridge and acceptance record

Use the existing [capture format](CAPTURE_FORMAT.md) and
[acquisition protocol](CAPTURE_PROTOCOL.md); add no v1 fields in this document.
Keep command timelines in `stimulus` descriptions and support schedules, with
exact control/initial-history, model/profile and trace identities. Measured sensor
streams are raw artifacts; extracted contact events are derived artifacts with
parents and analysis version. A command timestamp is not a measured edge.

| Software scenario | Minimum physical evidence to upgrade its claim |
| --- | --- |
| C1–C3 | Synchronized position, nine contacts, source phase and dry output; make and break, partial/struck/repeated gestures, white/black keys on both manuals, sensor latency/bandwidth/loading and held-out keys/takes. A 1967 C-3 observation does not calibrate the target B-3 (pp. 115–120). |
| P1–P4/R2–R3 | Identified AO-28 revision; fixed-gain dry captures and actual open-contact intervals; second/third × normal/soft × fast/slow, overlapping notes, recovery sweep and held B/tablet/Cancel transitions. Retain incomplete releases, sustained return and steady upper attenuation separately; neither nominal RC products nor broadband onset RMS identifies the complete envelope (pp. 131, 133–138). |
| E1/preset/pedals | Calibrated expression position and complex response at stationary/moving positions; actual preset wiring and switch traces; pedal bus/shaping and manual-unison evidence. Keep unresolved loading, reactor/capacitance values and production revision explicit (pp. 125, 139–150). |

Require specimen/configuration identity, permission scope, signal boundary/load,
chain and physical-clock calibration, synchronization uncertainty and untouched
raw bytes before admitting a physical fit. Keep whole takes, synchronized
channels and derivatives in one split group. Freeze criteria using repeatability
and intended scope before held-out evaluation; no per-take renormalization may
erase fast/slow, normal/soft or expression differences. Audio-only captures may
support a scoped behavioral comparison while internal contact parameters remain
unidentified. Metadata/byte verification is not physical admission.

The future integrator must map each ID to an actual test/command and retain
inputs, independent oracle version, state/audio traces, observed errors, logs,
artifact hashes and exact code/data identities. Run the adopted contact and
percussion unit suites, then the history scenarios and existing regressions,
then the integrated Release/sanitizer matrix. Record each result independently
as `pass`, `failed`, `blocked`, `not_run` or `inconclusive`; input evidence classes
remain `documented`, `derived`, `proposed`, `measured` or `unknown`.

After registering those tests, the existing local commands are
`cmake --preset release`, `cmake --build --preset release`, and
`ctest --preset release`; use the corresponding sanitizer preset where supported.
Retain the enumerated test list
and gate-to-test mapping so a green suite cannot conceal absent M3 scenarios.
These commands are instructions for the future integration, not runs here.

A rejected malformed request passes its negative test only when the required
unchanged-state evidence exists. A missing implementation/capture is `blocked`
or `not_run`, never an expected pass. Insufficient timing resolution, a noise-floor
limited response or indistinguishable candidate networks is `inconclusive` with
the unresolved quantity named. Synthetic success can accept a named nominal
continuation; only qualified held-out acquisitions can support its separately
scoped physical claim. No gate in this document has been executed here.
