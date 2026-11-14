# A04 — Atlas electronics, rotary acoustics and dependency review

## Assignment and inspected identity

Actual worker: `/root/w01_a04_atlas_acoustics`, wave 1 of the new reference-refinement session. The assignment owns only this note. Shared status, README, integration, commits and publication remain with the integrator. No earlier session's workers or results are counted as this assignment.

Inspected checkout: `8bd999efc13e309b932e6ac41d72ceb7b9b80a5f`, tree `c37da16cedbb91573476a44bd4eafe5a5e30134a`. At initial inspection the new reference-refinement directory was untracked; existing product source was unchanged. This is a local source observation, not an independent fresh remote-head or hosted-job verification.

Read `AGENTS.md`, the current top sections of `STATUS.md` and `NEXT_STEPS.md`, the complete `PLAN.md`, `research/ATLAS_REVIEW.md`, current recovery handoff and checkpoint, current session scope, latest development-log entry, rotary scope/numerical/motion/reference documentation, retained primary review and relevant errata. The current 47-parameter/state4 boundary takes precedence over historical rotary prose referring to 45 controls.

## Actual complete page coverage

Read **every extracted text page 253–336 inclusive: 84 pages**, covering all of chapters 041–054. The provided extraction was read sequentially in these bounded, untruncated spans:

| Read span | Pages |
| --- | ---: |
| 253–262 | 10 |
| 263–272 | 10 |
| 273–282 | 10 |
| 283–292 | 10 |
| 293–302 | 10 |
| 303–312 | 10 |
| 313–322 | 10 |
| 323–332 | 10 |
| 333–336 | 4 |
| **Total** | **84** |

The extraction is `/workspace/scratch/1bb6ee17ad7e/atlas-text/part4-253-336.txt`, 219,937 bytes, SHA-256 `bd0295415ea8897d04c037a119081d4ab3a983d2b4aa3d80eaf3725d9db9c526`. A separate marker check confirmed exactly 84 markers, equal to the complete integer sequence 253 through 336. This check supplements the full reading; it does not substitute for it.

The unchanged source PDF was freshly hashed: 21,248,265 bytes, SHA-256 `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`. Page citations below refer to that PDF. This assignment did **not** freshly render page images, inspect every diagram visually, reacquire external primary documents or recover the atlas's absent companion files. Figure and published-study distinctions below follow the complete atlas text and named repository reviews.

## Chapter findings and constraints

| Chapter / pages | Findings that constrain implementation and claims |
| --- | --- |
| **041 / 253–258 — 122 input/control** | The selected documentary baseline is the June 1971 publication 044578, assembly 036616 at 60 Hz, excluding optional reverb; 053231 is the 50 Hz assembly. V1 control and V2 audio have distinct responsibilities. Full differential voltage is `va-vb`, while common mode is their average; source/loading ownership must be explicit. V1 senses one leg, so an ideal average-only detector is a surrogate. A relay command changes future drive without resetting rotor phase. Detector thresholds, delays and electrical switching disturbances remain unmeasured. Requested speed and actual model speed must remain separate UI states (p. 258). |
| **042 / 259–264 — 147 variant** | The vintage 147 has a separate unbalanced input, console-load branch and winding/feedback topology. OPEN/8/16 input loading is distinct from the speaker load. A shared valve or transformer stock number cannot justify a shared complete transfer function. The older manual and October 1979 publication remain separate until reconciled. A brightness switch or one leg of the 122 output is not a calibrated 147 adapter. Modern 122H/147-type data must not silently fill vintage gaps. |
| **043 / 265–270 — power stage** | Output-valve grid drive, shared bias/supply, signed transformer windings and crossover load participate in a connected network. Plate and screen currents need separate device functions; the 0C3 is a series-drop path, not an independent fixed screen rail. Start with DC and a linear reference before nonlinear fitting. Oversample the coupled nonlinear region, retain convergence failures, and separate numerical, electrical and perceptual acceptance. Transformer ratio/parasitics, specimen valve curves, supply impedance and real load are unresolved. |
| **044 / 271–276 — crossover** | Documentary values are L2 3.2 mH, L3 5.2 mH, C16A 7.8 μF and C16B 12.5 μF; dated assemblies 052803 and 113860 remain distinct. The treble load floats across A–H, parallel with L2; C16A connects H–B. Bass uses A–W through L3 and W–B through C16B/load. Preserve `VT=VA-VH`, `VW=VWnode-VB`, both complex outputs and combined input impedance. The ideal 16-ohm-load fixture is electrical algebra, not an 800 Hz textbook or measured acoustic split. Real impedances, losses and acoustic polarity remain absent. The named atlas companion is not supplied here. |
| **045 / 277–282 — horn** | A stationary compression driver feeds one rotating acoustic horn; the opposite horn is a counterbalance, not another driven feed. Reflector/diffuser configuration changes angular response and has its own identity. Moving-mouth geometry is an approximation. The Model 600/University ID-40 literature examples cannot calibrate the target vintage 122. Fixed-angle complex responses, their timing, actual geometry and synchronized rotation are missing. Do not infer dimensions or frequency-independent acoustic centers from an unscaled photograph. |
| **046 / 283–288 — drum** | The woofer remains fixed; its deflector/opening turns. A frozen angle still emits bass. Angle-dependent transmission, changing delay and interference must have declared ownership. Low frequency does not mathematically imply zero fractional Doppler; an effective path radius is neither cone motion nor necessarily drum radius. Use persistent, phase-preserving response states and independent drum history. Bass-only target captures and near/room boundary evidence remain missing. |
| **047 / 289–294 — motors** | Horn and drum need separate profiles, directions, speeds and ramp histories. Pulley/motor/supply identities matter; shaft RPM differs from rotor RPM. The 5–8-second bass fast-to-Chorale service criterion is not an exponential tau, horn value or universal settling definition. Start from a declared first-order surrogate, select tau from target minus current speed and preserve momentum through rapid reversals. Stop/coast/brake requires an identified extension, never an instantaneous zero-speed assignment. |
| **048 / 295–300 — cabinet** | Exterior nominal dimensions do not establish internal air volumes, panel thickness or material core. Appearance can be refined while hidden acoustic quantities remain null. Fixed cabinet surfaces, panel state, driver identities and response ownership constrain kernels; whole-cabinet rotation shortcuts are invalid. The published 122A experiment with its removed upper rear wall is a distinct condition. Source catalog counts and part numbers are not measured CAD or a manufacturing BOM. |
| **049 / 301–306 — propagation** | One physical trajectory serves microphone-specific emission times, solving `t=e+r(e)/c`. The coordinate expansion has the negative cosine cross term; linear interpolation must return sample `k` at fraction zero. Both source hazards have a retained repository primary review. A native solver needs a bounded residual-tested iteration policy, historical angles across commands, causal interpolation support and separate algorithmic latency. The atlas's 1,001-time fixture is reported synthetic mathematics, not local runtime/audio acceptance. |
| **050 / 307–312 — directivity** | Directivity, pressure distance gain and delay must use consistent emission geometry. Sum signed pressure and preserve complex phase; do not normalize every angle or rotate fixed walls with the horn. Persistent FIR bases and periodic weights are candidates, with rank/order determined by held-out residuals. Angular detail creates sidebands requiring separate bandwidth analysis. Phase spikes near amplitude nulls must not be fitted as motor acceleration. The printed Fourier fixture is a synthetic representation check. |
| **051 / 313–318 — microphones** | Receiver position, microphone aim and rotor angle are different quantities. For source-to-receiver unit vector `q`, microphone incidence uses its forward axis dotted with `-q`. Both branches may reach every receiver. Stereo uses one set of physical trajectories and relative timing; independent L/R LFOs invent another source. Mono fold-down and a single-mic scene need not coincide. Calibration, microphone inclusion flags, synchronized channels and held-out poses remain required. |
| **052 / 319–324 — persistent state** | Audio time owns one horn and one drum history. Command events preserve instantaneous phase/speed, retain prior anchors for delayed queries and do not reanchor unchanged commands. UI refresh, notes, transport and editor closure cannot restart motion. Suspension and sample-rate epochs need explicit policy. Musical presets are distinct from full transient checkpoints. The atlas's decimal/block fixtures are source-reported examples; native event translation, history and host gates require their own execution. |
| **053 / 325–330 — time-varying convolution** | Weighting persistent filter outputs at observation time and weighting inputs at emission time are different two-time systems. Static agreement cannot choose between them; an impulse whose tail crosses an angle change exposes the difference. Warm replacement histories and complementary amplitude fades preserve correlated outputs; equal-power fading identical outputs adds 3.0103 dB at midpoint. A longer IR cannot repair duplicated delay or wrong time indexing. The printed partition arithmetic and synthetic fixture are not a CPU benchmark or target convolver. |
| **054 / 331–336 — room/RV** | Cabinet, propagation, microphone and room contributions each need one owner. A two-input/two-output room matrix generally needs all four kernels and common time zero. Room bypass must preserve cabinet reflections. The optional 122RV spring branch starts at main amplifier output and returns through its own electronics and fixed speaker; it is separate from the baseline and must not inherit rotor Doppler. Early/late windows must recombine, with complete tails retained. Room/spring/lamp captures and a physical fidelity result remain absent. |

## Current implementation inspected

The implemented rotary scope is a **numerical foundation**, not a connected cabinet renderer:

- `include/hammond/RotaryTypes.h` freezes `nominal-effective-mouth-rotary-v1` / `rotary-numerics-v1`, two rotor identities, two receiver identities, two-state commands, four admitted sample rates and explicit geometry/history/iteration limits. Proposed normalized radiation-boundary inputs are distinct from calibrated terminal volts or pascals.
- `include/hammond/RotaryMotion.h` and all of `src/RotaryMotion.cpp` implement the constant-command motion primitive and serialized owner. Tau follows target minus current speed; small-angle cancellation uses an explicit remainder polynomial; a direct exponential preserves decaying speed; phases and integer turns remain separate. Repeated commands preserve the anchor. Preparation/reset and stopped rate changes have different seeds. Rejections are staged before publication. These are source observations, not fresh native R2 qualification.
- `RotaryMotion` retains only its current anchor. Earlier positive-time queries return `InsufficientHistory`; negative-time queries use the epoch seed at constant speed. It cannot by itself serve a delayed path crossing an earlier command. A separate retained-history owner is required, as its comments and contract already state.
- `tools/rotary_reference.py` supplies the independent 80-digit Decimal motion timeline and a Cartesian/bisection retarded-path oracle. Geometry/trigonometry use binary64, not 80-digit transcendental functions. The local delay residual avoids large absolute-time subtraction. The oracle has complete bounded offline event history and preserves different receiver emission times. It supplies no waveform interpolation or rendered audio.
- `data/rotary/nominal-research-v1.json` explicitly labels the profile proposed, synthetic and unmeasured; it declares unity/omnidirectional directivity and omitted electronics, crossover, driver, horn transit, cabinet, room, microphone and brake. The strict validator and schema maintain those boundaries.
- The current source inventory contains no native rotary geometry/path/history/renderer module, no `ROTARY_PROPAGATION.md`, and no dedicated native rotary acceptance test. `tests/test_rotary_profile.py` and `tests/test_rotary_reference.py` exist. The retained rotary handoff records the first 12 accepted assignments and leaves native R2 onward open. Historical planned or running rows are not new work by this session.

Inspected current UI boundaries are consistent with that state. `InspectionModel.cpp` labels cabinet audio **Not connected**, horn/drum speeds **Unavailable**, microphone geometry **Not acquired**, and stop/brake **Not modeled**. `InstrumentView.cpp` paints the source cabinet as **ATLAS CONCEPT / DECORATIVE** and draws read-only inspection facts; it does not claim a live calibrated rotary instrument. `src/Engine.cpp` has no rotary connection. Preserve this truth during visual changes.

## Dependency-ready continuation

### Immediate M9 reference refinement

Continue the current layout/material and complete desktop-ownership work while preserving all 47 sound parameters, state4/readers 1–3, 91 shared sources, fixed-registration semantics and note-release ownership. Visual similarity to the cover/page-409 reference is a separate acceptance target from measured acoustic/physical equality. This assignment has not freshly measured that visual comparison. The current status's manual-depth, lighting, texture, bevel, composition, singular-count and pending-capture gaps remain live inputs for the visual workers.

For cabinet presentation, preserve stationary driver/woofer versus moving horn/deflector responsibilities, the single driven horn, and optional-stop identity. Do not add decorative speed readouts that look measured or imply connected sound. If a later real trajectory is exposed, snapshots must distinguish requested command from actual modeled speed and keep the UI independent of its clock (pp. 258, 283, 294, 319–322). Refresh README images from the affected native executable after acceptance, retaining reference art and historical captures separately.

### Independent M7 engineering sequence

1. **Native R2 qualification is immediately ready.** Compare `RotaryMotion` with the existing independent reference under the frozen grid: both signs, all specified taus, rest/acceleration/decay, tiny and full-day intervals, wraps, reversals, 1,000 seeded semigroup cases, unchanged commands, all rates and rejection preservation. Retain actual maxima and locations. Add meaningful native probe/test inputs; the two Python passes below do not close this gate.
2. **R3 can follow with separately owned geometry/history primitives.** Admit full orbits, retain earlier command anchors, solve the local-delay equation with at most 48 iterations and residual at most `1e-11 s`, and compare against the independent bracketed oracle. Include roots straddling commands, both directions, clearance/Mach limits and distinct microphone emission times. Keep geometry errors separate from motion errors.
3. **R4 requires causal waveform history and a transactional dual-rotor renderer.** Preserve the frozen cubic operator, two-frame algorithmic delay, negative audio zeros, explicit end-boundary/zero-frame events, full rejection rollback, output range and complete flush. Qualify actual output with an independent same-cubic reference across the frozen block/rate cases before any Engine connection.
4. **R5/R6 remain separate after discrete parity.** Freeze production passband/alias/filter/latency policy before grading it; compare against a converged higher-rate reference. Then qualify actual allocation, bounds, lifecycle, interfaces and device deadlines at their own stated scope. Smooth motion or cubic parity alone cannot establish acceptable audible error.

### Electrical and physical prerequisites

An independent M6 documentary task can prepare a dated 122/147 source registry and the ideal four-element divider oracle with combined input admittance and both signed outputs (pp. 253–276). Direct review of the selected factory drawings is required before calling that registry independently source-verified. Do not use a generic split or claim measured losses from zeros. M5 connected AO-28 and complete dry G-G validation must precede downstream cabinet fitting; M6 source/load/driver boundaries must be explicit before integration. The separate scanner G5 failure still blocks its Engine integration under the current plan.

Physical M7/M8 progress requires an identified specimen and immutable calibrated captures: both electrical legs/ports and real driver impedances; separate synchronized horn/drum trajectories including interrupted ramps; measured geometry and panel state; phase-preserving fixed-angle and rotating horn/drum responses; microphone poses/calibration/common time; and held-out angles, poses, levels and transitions. Preserve uncertainty, nulls and response inclusion flags. A numerical fixture, decorative model, historical literature experiment or passing session ledger cannot supply these inputs.

## Executed verification and limits

Working directory: repository root. Python: **3.12.14**. Fresh commands:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tests/test_rotary_profile.py
PYTHONDONTWRITEBYTECODE=1 python3 tests/test_rotary_reference.py
```

Results: profile **33/33 passed in 1.782 s**; reference **33/33 passed in 1.765 s**, both exit 0. They are fresh structural/reference regression results, not native motion parity, waveform audio, visual, device or physical passes. No production code, test, parameter/state definition or UI asset changed in this assignment. No native build, desktop journey, new screenshot, hardware capture or external source verification was performed.

Relevant inspected bytes: `src/RotaryMotion.cpp` SHA-256 `9c8c98dc66a66088d39b43a52d025289d4dd241ebba583bd4200aba3b539ac4d`; `tools/rotary_reference.py` SHA-256 `4c8bbcdf279f87aaad5b730d60a82958321ba3c1a92e5318eb5e37b1e83c8b0d`; proposed profile SHA-256 `c0473cb20604726d989d7c280700109f647f7b227edb71c61d275ed9bfd67443`.

The integrator can accept this as complete 84-page text coverage plus a current-source dependency review. Commit/push, current README screenshots, shared handoff updates and complete session accounting remain the root's integration work.
