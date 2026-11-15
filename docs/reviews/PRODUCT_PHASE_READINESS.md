# Whole-project phase readiness — A56

**Decision: this batch advances a bounded M9 product slice and the independent
M6 ideal passive-crossover foundation. It does not complete M6, M9 or the
identified B-3/AO-28/Leslie instrument.** The next independent model task is a
reviewed, versioned same-Hz electrical protocol with justified floors and
tolerances, followed by a separately identified numerical candidate. The first
native reliability task is A47-N1's below-RtMidi close-failure and callback-
retirement experiment. These tasks can proceed independently after current
session closure; neither requires or authorizes a new Engine route.

Actual reviewer `/root/w10_a56_phase_readiness`, wave 10, 15 November 2026 UTC.
This review changes only its assigned review, short note and bounded receipt.
It performs no build, runtime experiment, physical acquisition, commit or push.
Subsequent publication and actual worker counts belong to the
[live checkpoint](../development/2026-11-15-product-continuation/CHECKPOINT.md).

## Evidence basis and source boundaries

Read the entire [AGENTS.md](../../AGENTS.md), [M0–M9 plan](../PLAN.md), current
STATUS/NEXT_STEPS/PROJECT_GUIDE, setup/session records and the six current
[A01–A06 reading records](../PROJECT_GUIDE.md#source-and-reading-records).
Those records cover every atlas text page, 1–500. A56 rechecked the unchanged
21,248,265-byte PDF hash,
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`;
this is not a new personal reading or independent verification of every cited
factory drawing. The atlas's research waves, M0–M9 milestones and requested
ten six-worker implementation waves measure different things.

| Evidence inspected | What this review can rely on |
| --- | --- |
| Actual checkout and read-only `git ls-remote origin refs/heads/main` | Both identify `d8c39f7986746eacc991747153c7dbb012bb9a32`; local tree is `edf67b978f93e8dbea6537ce92d3928c171bc1f3`. Later working files are unpublished at this observation. The [publication receipt](../development/2026-11-15-product-continuation/reports/gallery-publication.json) binds its parent and guarded non-force update. |
| [d8 hosted receipt](../development/2026-11-15-product-continuation/reports/d8-hosted-status.json) and primary [Linux](PRODUCT_LINUX_HOSTED_REVIEW.md), [Windows](PRODUCT_WINDOWS_HOSTED_REVIEW.md), [macOS](PRODUCT_MACOS_HOSTED_REVIEW.md), [VST3](PRODUCT_VST3_HOSTED_REVIEW.md) reviews | Thirteen successful jobs at d8, including actually executed 21/21 native sanitizers. A56 reconciles retained evidence; the primary reviewers own log inspection. These results do not qualify the later A46/A48 working changes. |
| [Later coherent local receipt](../development/2026-11-15-product-continuation/reports/wave8-coherent-build.json) | 180/180 in 507.55 s at d8 plus A46/A48, GCC 14.2 Release, standalone ON, MIDI backend OFF, VST3 OFF and dummy SDL. A56 independently rehashed all 366 listed code/test/build/data inputs: none differed. This is hash applicability, not another test execution or later-source hosted pass. |
| [Numerical acceptance](../development/2026-11-15-product-continuation/reports/crossover-response-acceptance.json), [characterization](../LESLIE_CROSSOVER_CHARACTERIZATION.md), [admission review](PRODUCT_NUMERICAL_ADMISSION_REVIEW.md) | All six numerical source hashes still match. Warped-reference/processed-sine parity remains separate from same-Hz accuracy; 126 in-band points within 130 total per group are a finite grid. The admission repair and identical-pixel plot refresh neither change the numerical realization nor establish physical fidelity. |
| [Current UI acceptance](PRODUCT_UI_ACCEPTANCE.md) and [gallery admission](PRODUCT_GALLERY_ADMISSION.md) | Eleven actual frames retain capture source `d556da01` and application `7ded143b…`; they are not new d8 captures. Correct controls, source-bound raster checks and retained gaps coexist. A54 owns direct image inspection; A56 performed no new visual measurement. |
| [Native recovery review](PRODUCT_NATIVE_RECOVERY_REVIEW.md) | A47-N1 is a source-proven suppressed-close-result gap and a supported risk model. No native hardware failure or use-after-free was observed. The synchronous facade and d8 sanitizer passes do not establish upstream callback retirement. |

The [A56 receipt](../development/2026-11-15-product-continuation/reports/A56-phase-readiness.json)
records reviewed hashes, exact read-only checks and the separate dirty R4
checkout observation. Original b9 install/Windows failures, d556 sanitizer
**build** failure, local ptrace blocks and earlier source-specific results remain
as retained by [STATUS](../STATUS.md#earlier-product-checkpoints-and-retained-failures).
No new leak exception or retrospective pass is introduced.

## Reconciliation with every implementation milestone

The original milestone exits remain in [PLAN](../PLAN.md#milestones-and-exit-evidence).
This table assesses dependency readiness, without replacing that plan.

| Milestone and atlas intent | Present implementation and this batch's contribution | Exit still required |
| --- | --- | --- |
| **M0 — identifiable evidence and contracts** | Preserved atlas, complete reading records, nominal profiles, units/provenance/unknowns and acquisition tooling. This batch adds a source-qualified ideal 122 divider contract; its cited manufacturer drawing is not independently verified by that contract. | Select actual organ, AO-28 revision and cabinet/assembly; establish permissions, condition, connected configuration and calibrated boundaries. An ideal profile remains a separate identity. |
| **M1 — inspectable, testable core** | Prepared SDK-free Engine, bounded events, failure/lifetime contracts and offline rendering have software evidence. Current work preserves those interfaces. | Qualify every new processing route's own state, callback resource and deadline behavior. Existing tests do not cover hypothetical future connected models. |
| **M2 — 91 shared continuously running sources** | Nominal 12-TET/sine sources and corroborated documentary manual/pedal routing exist. Source phase continues through silence and note changes. | Production gear relationships and measured pickup waveforms, amplitudes/phases, filtering/loading and leakage. Table routing corroboration does not establish these physical quantities. |
| **M3 — console and loaded behavior** | Nominal contacts, four retained banks, exclusive fixed registration, momentary Cancel, shared percussion, pedals and scalar expression exist. Native CC120/121 and CC11 calibration improve input behavior. | Measured contact trajectories, physical latch/overlap and transformer-tap loading, continuous conductance, percussion/loaded expression and pedal-reactor behavior. Controller endpoint calibration does not implement the AO-28 expression circuit. |
| **M4 — scanner line and rotor** | Independent graph/reference, line and rotor research exist; G3/G4 have named numerical evidence. | Preserve the unresolved **G5 same-Hz failure at every investigated rate**. Combined-stage transitions, matched reconstruction/transients, sidebands, audible policy and physical evidence precede live integration. Coordinate through the [scanner handoff](../SCANNER_HANDOFF.md). |
| **M5 — complete organ electronics** | Documentary preparation exists. [Engine processing](../../src/Engine.cpp) still sums nominal source/contact/percussion/pedal contributions, then applies output gain and scalar expression; [Engine state](../../include/hammond/Engine.h) contains no connected scanner/AO-28/crossover/rotary stage. | Revision-specific connected graph, differential signs, transformer/load/feedback data, operating points, nonlinear/convergence/alias checks and calibrated dry G–G validation. The atlas's complete dry organ is a later target than today's nominal dry prototype. |
| **M6 — coupled Leslie electronics** | New independent four-state ideal crossover, floating A–H treble, W–B bass, reference/probe, transactional lifecycle/resource checks and six-file research component. | Freeze and meet a same-Hz numerical protocol; independently establish drawing/assembly applicability, losses, source impedance and complex driver loads; then qualify coupled amplifier/transformer/crossover/driver behavior. Keep 122 and 147 separate. |
| **M7 — moving acoustics** | R2 motion/R3 historical propagation have nominal evidence. R4 rendering and its CLI exist under a separate owner; published full-waveform evidence qualifies named inputs. | Reconcile that owner's unpublished acceptance and final source, then separate R5 audible/reconstruction/alias policy and R6 runtime integration. Physical rotor histories, radiation/directivity, cabinet, microphone and room evidence remain necessary, with one owner per effect. |
| **M8 — acquisition, fitting and held-out decisions** | Capture/corpus/split/policy/job/study/replay tools and procedures exist. No physical corpus was acquired by this batch. | Identified calibrated originals, uncertainty and repeatability, complete relationship-aware splits, supported parameter identification, untouched held-out confirmation and an actual listening protocol/result. Schema or synthetic-study success cannot substitute. |
| **M9 — usable adapters and qualified release** | Standalone/VST3, 47 stable parameters, state4/readers 1–3, scoped input/calibration, reference-led live controls, installed workflows and source-specific platform checks. | Current actual-sixty/final-source closure; native close/retirement; physical display/controller/audio and DAW journeys; native semantic accessibility; callback deadlines; rights/branding and signed distribution. Literal whole-interface 1:1 equality remains unmet. |

M6 numerical research can proceed without acquired hardware because its next
claim concerns the declared ideal electrical problem. Physical fitting must
still follow complete dry-organ validation and the relevant acquired boundaries.
Similarly, usable M9 behavior can progress while M4–M8 remain incomplete, but
an adapter or installation pass cannot close complete product release.

## Work order 0 — close only this authorized batch

The starting reviewer-time manifest was 56 dispatched / 53 accepted; later counts come
from the live records. Root must admit every remaining actual result, retain
the final strict product-checker output, switch the product CI step from
progress to strict only after those acceptances, and publish the exact accepted
source with expected-head/no-force protection. Required hosted results must
execute the added Python modules and strict ledger step at that source.

The existing commands, from the repository root, are:

```sh
python3 -B tools/check_product_session.py --repo . --allow-incomplete --json
# Only after all A01–A60 are actually accepted in ten six-worker waves:
python3 -B tools/check_product_session.py --repo . --json
```

Progress mode does not close the session; neither checker proves dispatch,
substantive quality or fidelity. Preserve the existing 180-test receipt and
run only required affected checks when inputs change. A fresh full suite solely
to repeat this documentary review is unnecessary. Root owns final publication,
observed CI and reconciliation of concurrent main advances.

## Work order 1 — freeze the next M6 electrical experiment

**First deliverable:** a reviewed protocol, before choosing or evaluating a new
realization. Proposed owned outputs are
`docs/LESLIE_CROSSOVER_SAME_HZ_PROTOCOL.md`,
`data/crossover/leslie-122-same-hz-protocol-v1.json` and
`docs/reviews/LESLIE_CROSSOVER_SAME_HZ_PROTOCOL_REVIEW.md`. These are proposed
future paths, not files created or accepted by A56. Assign one author and an
independent reviewer; do not edit the v1 circuit to make a candidate pass.

**Exact existing inputs:** [frozen contract](../LESLIE_CROSSOVER_CONTRACT.md),
[registry](../../data/crossover/leslie-122-ideal-v1.json),
[native header](../../include/hammond/LeslieCrossover.h),
[implementation](../../src/LeslieCrossover.cpp),
[independent reference](../../tools/crossover_reference.py),
[probe](../../tools/crossover_probe.cpp),
[acceptance harness](../../tests/test_crossover_acceptance.py), retained
numerical report and characterization linked above. The maintained
[native](../../tests/test_leslie_crossover.cpp),
[lifecycle](../../tests/test_leslie_crossover_lifecycle.cpp) and
[allocation](../../tests/test_leslie_crossover_allocation.cpp) tests supply
preservation obligations, not the missing same-Hz policy.

### Protocol acceptance, declared before candidate results

| Required declaration | Accept only when |
| --- | --- |
| Electrical question | Input `V(A)-V(B)`, treble `V(A)-V(H)`, bass `V(W)-V(B)` and input current/admittance have explicit signs, SI units and input reconstruction. No summed acoustic transfer is substituted. |
| Domain and independent grid | External rates, band/endpoints, load family, amplitude/history domain and immutable check-grid bytes are fixed. Existing v1 rates are 44.1/48/96/192 kHz; its six response load pairs are (16,16), (1,1), (1024,1024), (1,1024), (1024,1), (8,32) ohm. Retaining or changing that family needs an explicit engineering rationale. Candidate tuning data and independent confirmation points remain distinguishable. |
| Output error budget | Each port has numerical magnitude/phase limits above a declared gain floor and an absolute complex V/V limit below it. Define floor equality, zero/reference-null behavior and principal/wrapped phase handling. Justify the floor from the intended electrical observable, numerical conditioning and allocated engineering error; retain absolute errors at all points. |
| Source-loading error | Input admittance has its own A/V criterion and any independently justified floor/relative criterion. A V/V output limit cannot be reused as an admittance limit without dimensional justification. |
| Oracle and transient precision | Independent steady-state and precharged transient references use the same declared reconstruction; residual, settling and convergence evidence must be sufficient to resolve the selected limits. Unresolved precision yields inconclusive, not pass. |
| State, resources and failure | Physical state/previous-input semantics, rate transitions, energy behavior, partition equality, bounds, late-failure rollback and subsequent continuation are declared. State which allocation calls and runtime workload are observed and how their acceptance is decided. |
| Freeze and admission | Version/hash the protocol and independent grid before candidate evaluation; record independent acceptance and retain all failed/inconclusive points. Missing fields, wrong units, changed documentary values and post-hoc limit changes prevent acceptance. A new policy version never silently regrades an old result. |

This review deliberately supplies **no invented numerical or audible tolerance**.
The next author must state and defend concrete numerical limits before a candidate
can be graded. An explicit engineering design target is permissible when labeled
as such; it is not a measured audible threshold. Choosing a floor or budget from
the current worst-case error merely to obtain a pass is unacceptable. If the
intended electrical accuracy cannot yet be justified, finish with a reviewed
open policy decision and keep candidate acceptance blocked.

### Experiment outline after the protocol is accepted

Preserve `physical-trapezoidal-leslie-crossover-v1` and documentary L/C values.
Give the candidate its own reviewed identity and frozen code/build inputs.
Compare both the candidate response function and **actual processed output**
against independently formulated same-Hz references at every declared point;
include both load gains and input admittance. Retain settling bounds, signed
phase/complex residuals and every failure. Exercise precharged histories,
all declared stopped rate pairs, legal block partitions, energy behavior,
late failure followed by a valid continuation and measured bounded cost.

A higher internal rate needs a specified input reconstruction, conversion
filters, latency and clock/history transition policy. The existing 48→192 kHz
comparison is not a resampling-pipeline test; 176.4 kHz is outside v1, so a
44.1 kHz fourfold route requires a reviewed extension or different candidate.
Exact state transition under a different hold is a different experiment.
Single-point prewarping cannot be treated as full-band equality.

For a future owner-coordinated baseline check, the existing
[developer workflow](../CROSSOVER_DEVELOPER_GUIDE.md#4-run-the-affected-acceptance-gates)
builds `hammond_crossover_probe`, `test_leslie_crossover`,
`test_leslie_crossover_lifecycle` and `test_leslie_crossover_allocation` before
the named CTest selection. A new same-Hz candidate requires its own reviewed
harness; there is no existing command that can make the retained v1 report
establish that acceptance. No such build or sweep ran in A56.

**Prerequisites/blockers:** input artifacts are available now; protocol ownership
and an independently accepted numerical budget are the immediate prerequisites.
Missing hardware does not block ideal numerical comparison. It does block claims
about actual losses, source/load coupling, driver behavior and specimen fidelity.
Even a passing candidate leaves Engine unchanged; coupled M6 and live integration
need later contracts and the dry-organ prerequisites.

## Work order 2 — establish the native retirement boundary

**Priority:** first native reliability work, ahead of broad physical controller
qualification or further reconnect/lifecycle expansion. It can run alongside the
M6 protocol. Current source inspection supports a real observability gap, while
the dangerous interleaving remains an unexecuted risk model.

Use [A47-N1](PRODUCT_NATIVE_RECOVERY_REVIEW.md#a47-n1-native-close-failures-can-evade-quarantine-admission),
`apps/standalone/MidiDevice.cpp`, `apps/standalone/main.cpp`,
`apps/standalone/MidiInput.cpp`,
`apps/standalone/backend_tests/test_standalone_midi_backend.cpp`,
`apps/standalone/native_tests/calibration_lifecycle_driver.cpp`,
`apps/standalone/native_tests/test_standalone_native_calibration.py` and its
`apps/standalone/native_tests/fake_calibration/RtMidi.h` dependency. Also retain
`data/dependencies/rtmidi-lock.json`,
`tools/acquire_rtmidi.py` and `cmake/VerifyRtMidi.cmake`. The baseline dependency
is RtMidi 6.0.0 at `1e5b49925aa60065db52de44c366d446a902547b`, prepared source
hash `240705532b17e593dc17434259233a586c9136808724124f1d3af649eadea17a`.
Keep the borrowed locked checkout read-only. Proposed first outputs are
`docs/NATIVE_MIDI_RETIREMENT_CONTRACT.md` and an independently reviewed,
source-identified fault-injection harness under
`apps/standalone/native_tests/native_close_faults/`; assign them before editing.

The experiment must intercept WinMM reset/stop/close and CoreMIDI disposal
**below RtMidi**, then park a callback before it touches dependency storage or
enters the wrapper counter. First retain current behavior, then evaluate a
separately reviewed checked-close change. Fault fixtures require deterministic
barriers and retained ordering observations, not a sleep-dependent claim.

Predeclare these acceptance conditions: each injected native failure is observed
before destructive cleanup; native handles, RtMidi callback storage, adapter
context and inbox remain alive; poisoned state prohibits reopen and inbox reset;
late callbacks cannot enter freed storage; successful ordinary teardown remains
leak-free. Include partially opened connections, callbacks already admitted and
callbacks parked before wrapper entry, with original failure results retained.
Keep the existing named quarantine-only leak policy unchanged.

Successful return codes still require backend-specific callback-retirement
evidence. A wrapper counter protects only callbacks that reached the wrapper;
ASan/UBSan on the synchronous facade cannot prove the OS contract. Qualify named
Windows/CoreMIDI builds and platform ordering separately; current Linux-only
resources cannot supply those observations. If any required native retirement
guarantee remains unsupported, retain that blocker rather than release the
storage or claim a portable shutdown deadline. A47's 250 ms wrapper wait starts
after the unbounded native close returns.

## Parallel work with distinct prerequisites

| Work order | Exact starting inputs and experiment | Acceptance and dependency |
| --- | --- | --- |
| **Native display usability before more decoration** | [A54's next visual gate](PRODUCT_UI_ACCEPTANCE.md#precise-next-visual-gate), admitted eleven-frame gallery, [gap record](../design/PRODUCT_REFERENCE_GAPS.md), `InstrumentView.cpp`, `UiModel.cpp` and the [desktop journey](REFERENCE_REFINEMENT_NATIVE_INPUT.md#concrete-next-actual-displaydevice-journey). On an identified native display/backend cover 960×700, 1280×900, 1672×941 and minimum Flat; inspect small preset/Service/footer/modal text, 0/8 drawbars, edited/sounding/pending state and all 71/10/11 focus sets. | Freeze source/configuration and an absolute input-to-paint target before the run. Retain painted pre-held prefixes, both navigation/resize directions, off-window release/fresh press, deliberate focus loss and numeric joined shutdown. Existing 112–114 ms wide software paint observations are not a display-latency or 60-fps result. If text fails, own a bounded typography/contrast repair before deck/rim material work; recapture after changed production. |
| **Native semantic accessibility** | `UiModel`/shared geometry, [workspace](../INTERFACE_WORKSPACE_CONTRACT.md), [geometry](../INTERFACE_GEOMETRY_CONTRACT.md) and [inspection](../INTERFACE_INSPECTION_CONTRACT.md) contracts. Specify one platform's semantic bridge: stable roles/names, values/actions, bounds, focus and applied/pending/unavailable states. | Predeclare complete navigation/edit/release and assistive-technology journeys, then retain actual screen-reader observations. Keyboard focus and Flat/raster checks do not supply native semantics. Requires the platform accessibility API and assistive tool. |
| **Physical A1–A2 pilot, then A3–A6** | [Acquisition order](../CALIBRATION_NEXT_ACQUISITION.md), capture v1 schema and protocol. Actual first records are `support/specimen-lock.md`, `support/permissions.md`, `support/setup.md`, chain/clock calibration and untouched external-output pilot files in the real archive. | Actual instrument access, allowed scope and qualified equipment/personnel are missing inputs. Pilot variability and uncertainty determine a bounded main acquisition and justified later fitting criteria. Retain null unknowns, immutable originals and group-aware holdouts. A schema command or synthetic recording cannot create an acquired specimen. |
| **DAW, devices and release** | Current [VST3 primary review](PRODUCT_VST3_HOSTED_REVIEW.md), [native operating guide](../MIDI_EXPRESSION_GUIDE.md), [host contract](../HOST_INTEGRATION.md) and retained [release obligations](../RELEASE_READINESS.md). Freeze a named OS/DAW/device/build matrix and journey before execution: routing, automation, Save/reopen, migration, overlapping UI/MIDI owners, both release orders and explicit recovery. | Keep validator, installed-package, physical audio/MIDI, deadline and DAW outcomes separate. Declare measured workload and deadline/underrun criteria before timing. Native failure/retirement work above precedes claims about that failure boundary. Rights/branding, clean-target packaging and signing/notarization require their own actual decisions and results. |

The acquisition pilot can be organized while numerical/software work proceeds;
it need not wait for cosmetic changes. It cannot be executed from absent hardware
or fictional permissions. Further M5/M6 graph work uses independently traced
revision-applicable drawings and explicit unresolved transformer/load fields.
Do not use downstream cabinet fitting to conceal upstream dry-organ errors.

## Preserve the separate R4 owner and resolve navigation through root

A56 read the actual separate checkout at
`/workspace/scratch/e3cacb90cc81/Hammond-B3-Organ` without modifying it.
It retained HEAD `fd2f6060…`, **151 staged and four untracked entries**;
its checkpoint reported **41 dispatched / 38 accepted**, including later local
A27 lifecycle/symmetry, A29 allocation and A30 CLI results. These are owner-
retained observations, not independently reaccepted or published by A56.
The product checkout's older copy of that checkpoint does not describe every
later file in the owner's dirty index.

Thus “remaining R4 acceptance” includes reconciliation, final coherent source,
publication and the owner's actual ledger; it must not imply that those local
experiments were never attempted. Conversely, d8's successful published R4 job
does not accept, publish, discard or transfer the owner's later overlay. Keep
R5 audible policy, R6 Engine integration and physical acoustics separate.
Preserve `D+6` capacity, the 8,192-entry journal, `max(D)+4` flush and the
[implemented renderer contract](../ROTARY_RENDERER_CONTRACT.md) while that owner
finishes its work. No source, index, build or evidence there is a cleanup target.

Two navigation issues were sent to root: later paragraphs in the product
checkpoint lagged its newer top-level worker counts; and RELEASE_READINESS
opened on historical `fd2f6060`/v5 scope while current navigation linked to it.
Root corrected the current routing and clarified the separate R4 local-result
boundary in [the retained amendment](../development/2026-11-15-product-continuation/reports/recovery-routing-amendment.json).
A56 read the correction: the historical release body is preserved, and the
checkpoint now identifies its later 57-dispatched/54-accepted observation.
These corrections do not change source or acceptance criteria, overturn the
d8/180-test evidence or justify duplicating completed work. This review's
input hashes and starting observations remain dated; the active checkpoint owns
subsequent progress and closure.

The continuation decision is concrete: finish the actual batch and final-source
qualification, then freeze the M6 same-Hz protocol and assign the native
retirement experiment in parallel. Keep display/accessibility and acquisition
work moving against their real prerequisites. Full physical fidelity and release
remain open until their own declared exits are observed.
