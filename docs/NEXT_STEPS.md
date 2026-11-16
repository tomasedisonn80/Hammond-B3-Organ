# Next steps

**Post-review local update, 16 November 2026:** the [refreshed full suite](development/2026-11-15-streaming-continuation/reports/final-coherent-qualification.json) passes **210/210 in 191.90 seconds** after the missing-probe and sanitizer-selection repairs. The [publication-source receipt](development/2026-11-15-streaming-continuation/reports/publication-source-qualification.json) binds the sole later EOF whitespace cleanup, identical rebuilt resource binary and passing affected test. The earlier 191.89-second observation below retains its original inputs. Current-source hosted execution and final session publication remain pending.

## Finish the current streaming/material source

The [active scope](development/2026-11-15-streaming-continuation/SCOPE.md)
delivers the isolated `causal-contact-grid-v1` trajectory and the Upper-rack
inner-metal material change. Its [coherent local qualification](development/2026-11-15-streaming-continuation/reports/coherent-qualification.json)
rebuilt **131 steps** and passed **210/210 CTests in 191.89 seconds**, with all
505 recorded code/test/tool/data inputs unchanged. Independent trajectory,
lifecycle, resource, comparison, gallery and compatibility evidence is retained
in [current status](STATUS.md#current-tested-evidence-and-limits).

The current base is `4aac394cde4da40906b615573a8779aee2d9a37a`; the qualified
working overlay is identified by the receipt, not by HEAD alone. **Commit/push
and exact-source hosted CI remain pending.** The requested sixty distinct
workers in ten waves remain in progress. The [actual ledger](development/2026-11-15-streaming-continuation/assignments.json)
owns dispatch/acceptance counts; the [live checkpoint](development/2026-11-15-streaming-continuation/CHECKPOINT.md)
owns later source/publication observations. Earlier sessions and followups do not
count toward this request.

Root's immediate integration sequence is:

1. Preserve the qualified production inputs, genuine baseline binaries, frozen
   protocols, original failures and independent admissions. Resolve only concrete
   findings; later production/build/test edits require affected requalification,
   while prose/ledger edits require their integrity checks.
2. Finish the actual assignments, substantive acceptance and matching strict
   sixty-worker/ten-wave record check. Retain the result and each note/hash.
   A record-consistency pass alone establishes neither worker work quality nor
   implementation, physical or external-dispatch acceptance.
3. Inspect fresh remote advances and reconcile compatible work while preserving
   other owners' source, index, builds and evidence. Commit reviewable accepted
   paths and push to `main` with a fresh expected head, without force.
4. Independently fetch and verify exact remote commit/tree/parent and intended
   contents, then observe the required hosted jobs at that source. Record
   queued/unacquired, failed, cancelled and successful outcomes accurately.
   A workflow dispatch or older hosted pass is not current-source qualification.

These are already authorized project operations owned by root. The earlier
execution workspace's authentication observations are historical; inspect the
actual current publication path instead of assuming that its access state
applies here.

## Resume this workspace and its delivered tools

Writable source is **`/workspace/scratch/177e78b1ac09/Hammond-B3-Organ`**; the
single coordinated Release build is
**`/workspace/scratch/177e78b1ac09/build-native`**. SDL 2.32.10 at
`/workspace/scratch/ade21b726509/SDL2` is a **read-only dependency**. That other
workspace's checkout, index and build remain outside this session's ownership.

[Current workspace and setup](STATUS.md#current-workspace-and-setup) contains
the exact dependency verification and CMake configuration. This local build is
Ninja Release with testing/standalone ON, MIDI/VST3/sanitizers OFF and native
X11/Wayland/ALSA/PulseAudio/JACK backends disabled. To reproduce its completed
qualification after recovering the configuration, root uses:

```sh
cmake --build ../build-native --config Release --parallel 3
ctest --test-dir ../build-native -C Release --output-on-failure --no-tests=error --parallel 3
```

The 210-test result already qualifies its frozen inputs. Regenerate CMake before
building if test discovery or configuration changes; never test changed headers
against stale objects. Do not broaden testing without a concrete remaining risk.
For ordinary physical desktop use, follow the separate
[normal build-and-launch recipe](../README.md#build-and-launch-the-native-application)
and [platform/MIDI setup](MIDI_EXPRESSION_GUIDE.md#build-the-native-application),
with native backends enabled in a distinct clean configuration. Launch at
1672×941 for wide Dimensional Play; the default 1280×900 is compact. Dummy-SDL
recovery does not qualify a real display, controller, audio device or callback.

The [causal-grid developer guide](CAUSAL_CONTACT_GRID_GUIDE.md) gives a complete
native probe example, bounded CGGRID1 wire format, API lifecycle and focused
checks. Its probe is `../build-native/hammond_causal_contact_grid_probe`.
The inherited [offline reference guide](CONTACT_SWITCHING_GUIDE.md) and
[48-file installation guide](CONTACT_REFERENCE_INSTALL.md) retain their original
source/package identities; the grid/probe is not added to that component.
Use fresh report destinations and preserve the prior 36×4 study's numerical
evidence. The current actual-app gallery is
[upper-rack-material-v1](../examples/demos/upper-rack-material-v1/README.md);
the [whole-reference gallery](../examples/demos/whole-reference-layout-v1/README.md)
is the genuine prior baseline.

## Next engineering assignments

The isolated integer-grid trajectory and narrow Upper finish are implemented
and tested; repeating those tasks would not advance the remaining gates.
Root must first assign exclusive paths to each next owner and check the existing
ledgers. The proposed owners/modules below are future assignments, not claims
that workers or new files already exist.

### M3: conversion policy and causal audio

1. **Conversion/design owner — a separately named input converter and contract.**
   Use the [grid contract](CAUSAL_CONTACT_GRID_CONTRACT.md), its
   [independent admission](reviews/CAUSAL_CONTACT_GRID_ADMISSION.md),
   [implementation review](reviews/CAUSAL_CONTACT_GRID_IMPLEMENTATION_REVIEW.md),
   [offline model](FRACTIONAL_CONTACT_REFERENCE.md) and
   [earlier streaming review](reviews/CONTACT_STREAMING_DESIGN_REVIEW.md).
   Freeze how source time, travel, thresholds and speeds enter the integer
   domain: units, rounding, out-of-domain rejection, collisions, stable caller
   order and state retained across calls. Study quantization error and changes
   to threshold/crossing topology, including adjacent commands, tied/reversed
   targets, tiny/subnormal inputs and distinct exact times sharing a binary64
   display. No implicit clamp or conversion may silently redefine v1.
   Acceptance requires independent fixtures and declared error/topology limits
   before the converter is called equivalent to any reference subset.
2. **Audio-stage owner — proposed `include/hammond/research/ContactStream.h` and
   an isolated implementation/tests.** Those paths are prospective. Preserve
   `CausalContactGrid` and the frozen reference as identified inputs. Admit the
   signal, accumulation, lifecycle and work contract before code. The
   [D=16 proposal](CONTACT_STREAMING_NEXT_DESIGN.md) uses
   `z[m]=y_L[m−16]`: emit before integrating `[m,m+1)`, evaluate shared sources
   from absolute **input** time, and retain unfinished centered cells and their
   deterministic sums across every callback boundary. Declare ring retention/
   eviction, equality ordering and complete rollback of cells, cursor, history
   and output. The trajectory itself implements none of this filtering.
3. **Independent numerical owner — a new full-window oracle/protocol.**
   Preserve the existing `tools/contact_switching_oracle.py`, frozen fixture/
   probe set and original [results](CONTACT_SWITCHING_RESULTS.md). Independently
   reconstruct all **289 samples of every retained fixture**, including tails,
   under a separately admitted resource budget. Existing all-sample high-rate
   convergence and 64-probe continuous admission do not supply this missing
   full-window grade. Justify and freeze tolerances before inspecting candidate
   errors; the proposal's atlas `1e-4` limits are still unadmitted. Permit only
   declared D=16 alignment, with no fitted gain/delay or trimmed tails. Retain
   exact events, all arrays/refinements, scaled error/silence cases, response
   checks, failures and source/fixture/toolchain identities.
4. **Lifecycle/resource owner — actual filtered output and complete drainage.**
   Freeze nonempty N processing outputs plus **33 drain samples**, giving
   **N+33 outputs** for reference indices −16 through N+16; retain both endpoint
   zeros and the **N=0 empty exception**. At closure, preserve the already
   integrated left portion of the straddling cell and fill only its remaining
   portion with zero. Distinguish incoming equality edges, endpoint commands,
   the final trajectory snapshot and the raw-gate jump. Physical note release
   continues travel/source/filter evolution and never closes that gate.
   Test one-frame/irregular/maximum partitions, future-command causality,
   cancellation, partial/empty drains, repeated/invalid closure, late rejection,
   short-output retry and continued processing after failure. Reject active
   rate changes; specify stopped drain/reset/phase-origin policy. Measure actual
   prepared storage, allocation scope, bounded work and platform callback
   distributions against predeclared deadline/headroom criteria.

The current **four-key, 4096-frame, 512-command** epoch is deliberately finite.
The [resource admission](reviews/CAUSAL_CONTACT_GRID_RESOURCE_ADMISSION.md)
bounds that model; it supplies neither indefinite full-organ capacity nor an
audio deadline. A separate capacity owner must review clock/counter horizons,
event storage, full manual/pedal ownership and continued phase/history before
extending it. Only after the filtered numerical/lifecycle/resource gates should
an integration owner propose changes to `ContactBank`, `Engine`, standalone or
VST3: explicit scheduling/latency reporting, ownership and callback retirement,
plus unchanged-default PCM evidence. Preserve all 91 sources, 47 parameters,
state4/readers 1–3 and plugin identities. Physical bounce, resistance, tap
loading and specimen timing still require synchronized identified travel,
contact/source/dry captures and held-out evaluation.

### M9: subsequent materials, typography and actual display

| Proposed owner and modules | Inputs and bounded next work | Required acceptance |
| --- | --- | --- |
| Material owner: separately assigned `apps/standalone/InstrumentView.cpp` region | Use the current `c29495e9…` app, [Upper comparison admission](reviews/UPPER_RACK_COMPARISON_ADMISSION.md), [actual gallery admission](reviews/UPPER_RACK_GALLERY_ADMISSION.md) and original atlas cover/page 409. Choose and freeze the next Lower-rack/casework illumination or key/cap bevel/shadow scope; keep the already admitted Upper field as its baseline. | New independently admitted support/metrics, genuine same-state old/new binaries, full-frame review, source/executable/state/pixel bindings and preserved geometry/child order/inactive paths. Do not enlarge the frozen Upper mask to grade another surface. |
| Typography owner: separately assigned label/font/drawing paths | Measure the remaining small labels, density and readable live status against the original reference and current captures. Specify one coherent type/spacing change with explicit inventory and focus constraints before editing shared drawing code. | Actual app captures at reference, minimum-active, compact, Flat and supported scales; independent glyph/clip/contrast checks; all 147 keys, 24 presets, four banks and 68 controls remain truthful and operable. Decorative illustration labels cannot replace live semantics. |
| Display/input owner: normal native backend build and identified hardware | Execute the [concrete display/device journey](reviews/REFERENCE_REFINEMENT_NATIVE_INPUT.md#concrete-next-actual-displaydevice-journey): both resize/navigation directions, held owners, off-window release/fresh press, focus loss, keyboard use and joined shutdown. | OS/backend/display/DPI/device identities, actual step frames, input/diagnostic records and numeric exit status; assess label/focus usability at the observed scale. Dummy SDL provides no substitute for this evidence. |
| Accessibility owner: one platform's native semantic bridge | Freeze names, roles, values, actions, status announcements, focus order, keyboard behavior and reduced-motion/Flat handling from the current live inventory. | Actual screen-reader and keyboard journeys on the identified OS, including pending/applied controls and modal/numeric-entry exit behavior; semantic accessibility is separate from screenshot contrast. |

The current 96-pair/five-screen material result and twelve admitted app captures
close their declared software scopes only. **Literal whole-interface 1:1 remains
unmet and unwaived.** A whole-interface comparison needs its own complete
reference/source/state/dimension criteria; a protected crop, patch statistic or
decorative cabinet equality cannot close it.

### Validate this session's actual records

Use only this streaming session's
[actual assignments](development/2026-11-15-streaming-continuation/assignments.json).
Root must retain the matching validator's strict result for sixty distinct
accepted workers in ten six-worker waves, including substantive notes/hashes and
ownership/verification/acceptance. Until that exists, report progress without
claiming closure. A planned slot or repeated followup is not another worker.

```sh
python3 -B tools/check_repository.py --json
```

This read-only command checks repository integrity and local file links; it is
**not** a worker-count or external-dispatch attestation. Older
`check_product_session.py`, `check_continuation.py` and other session checkers
remain bound to their own schemas/ledgers. Do not repurpose their passing result
to close this one.

### Historical execution handoff — 15 November 2026

The prior [execution receipt](development/2026-11-15-execution-continuation/reports/coherent-qualification.json)
records **203/203 CTests in 191.37 s**, its installed 36×4 offline contact study
and canonical wide composition. Its dated handoff stated that worker closure,
publication and current-source hosted CI were pending, and proposed causal
streaming/material work next. Those are preserved historical observations,
not current streaming-session tasks or claims that its owner later completed
them. Consult that [owner's checkpoint](development/2026-11-15-execution-continuation/CHECKPOINT.md)
for later outcomes. [STATUS](STATUS.md#earlier-execution-continuation-snapshot--15-november-2026)
retains the source, original results and then-current workspace/setup.

Likewise, the earlier product session's
[strict record result](development/2026-11-15-product-continuation/reports/product-session-strict.json)
and thirteen successful hosted jobs at `80b8cce1773e4c31bf64cb6c2b7f43e8445ec3fe`
qualify only that ledger/source. They neither count workers nor qualify hosted
execution for this continuation.

## Next dependency-ready phase after session closure

**Retained independent M6 sequence:** the
[fidelity continuation](development/2026-11-15-fidelity-continuation/CHECKPOINT.md)
owns same-Hz numerical work. Recover its actual current source/results before
assigning changes. A new candidate still needs a versioned same-Hz protocol and
independent evaluation. The current ideal circuit, analog references and characterization
already supply the inputs for this engineering work. No new hardware data is
needed to compare declared numerical methods; physical-fidelity claims still
require acquisition.

### Inputs and affected boundaries

Use the [frozen crossover contract](LESLIE_CROSSOVER_CONTRACT.md),
[fixed registry](../data/crossover/leslie-122-ideal-v1.json),
[retained native/reference report](development/2026-11-15-product-continuation/reports/crossover-response-acceptance.json)
and [same-Hz characterization](LESLIE_CROSSOVER_CHARACTERIZATION.md).
The [developer workflow](CROSSOVER_DEVELOPER_GUIDE.md#5-continue-m6-through-explicit-gates)
gives the ordered numerical, acquisition and coupled-model gates. Relevant
modules are `LeslieCrossover`, the independent Python reference/native probe,
the response/lifecycle/allocation tests and their report identities. Agree
ownership before changing them. Preserve the fixed v1 registry, realization,
reports and nominal dry Engine as reproducible baselines.

### Concrete sequence and acceptance

1. **Freeze the experiment before changing the realization.** Declare input
   hold/reconstruction, external sample rates, signal boundaries, frequency band,
   load family and an independent check grid. Set justified magnitude/phase
   tolerances above a stated gain floor, absolute complex tolerances below it,
   and a separate input-admittance criterion. Record their engineering basis;
   no measured or audible threshold exists in the present report. An independent
   review must accept the protocol and the preserved failure/limitation record.
2. **Evaluate one explicit candidate.** State its realization identity and
   physical-state semantics. Compare actual processed output as well as response
   functions, with independent steady-state and precharged transient references.
   A higher internal rate requires explicit input reconstruction, conversion
   filters, latency and clock/history handling. The admitted v1 rates do not
   include 176.4 kHz; a 44.1 kHz fourfold path needs a reviewed extension or a
   different candidate. Preserve documentary L/C values instead of retuning them
   to hide numerical error.
3. **Accept only the declared result.** Retain all grid points and failures,
   signed port/polarity and admittance errors, transient-convergence evidence,
   energy behavior, stopped-rate state preservation, partition equivalence,
   late-failure rollback and subsequent continuation. Measure bounded storage,
   allocation scope and runtime cost on identified builds. A candidate passes
   only its frozen criteria; inconclusive or failed comparisons stay visible.
4. **Leave live integration for its own contract.** A better ideal curve does
   not supply amplifier source impedance, measured driver loading, acoustic
   response or a calibrated cabinet. Coupled M6 and runtime/Engine integration
   require their own ports, ownership and acceptance after the prerequisite
   electrical and dry-organ work.

## Separately owned and acquisition-dependent work

| Track | Next concrete action and inputs | Exit evidence |
| --- | --- | --- |
| M4 scanner | Coordinate with the [scanner handoff](SCANNER_HANDOFF.md) and [ScannerLineFoh owner](development/2026-11-15-next-phase/CHECKPOINT.md); recover their distinct source, graph, transient and [numerical contract](SCANNER_NUMERICAL_CONTRACT.md) identities before further combined-stage work. | Six modes/four tablet combinations, one continuing phase, Q outside modulation, one chorus return, precharged transitions and transactional continuation; then same-Hz/transient/sideband/filter/latency evidence under unchanged declared budgets. Preserve the existing G5 failure at every investigated rate. |
| M5 and physical M6 | Select the applicable primary drawings and actual AO-28/Leslie assembly; independently trace endpoints, differential signs, loads and revision boundaries. Acquire missing transformer, operating-point, source/load and component-loss data. | Reviewed connected topology and explicit unknowns before numerical export; independent loaded AC/nonlinear/alias tests and complete dry G–G validation before cabinet fitting. Leslie 122/147 remain separate. |
| M0/M3/M8 acquisition | Use [A1–A6](CALIBRATION_NEXT_ACQUISITION.md) with identified specimen, permission, calibrated chain/clock and repeatability plan. Begin an external-output pilot archive, then boundary-specific captures. | Immutable originals, source/condition/uncertainty records, admission and acquisition-group splits; justified fitting and untouched held-out/listening outcomes. Contact/latch/tap loading, physical expression and pedal-reactor behavior remain unmeasured. |
| M9 native callback retirement | Assign the [A47-N1 gate](reviews/PRODUCT_NATIVE_RECOVERY_REVIEW.md): in an isolated source-identified prepared RtMidi build, inject failed WinMM reset/stop/close and CoreMIDI disposal below the wrapper while holding a callback before wrapper entry. The suppressed-error gap is source-proven; no hardware failure or use-after-free was observed. | First retain current behavior, then review checked close that reports failure and preserves native handles, callback storage, adapter context and inbox before destructive cleanup. Require poison/no-reopen/no-reset behavior and ordinary leak-free teardown. Successful close also needs platform-specific callback-retirement evidence; return-code checks alone are insufficient. |
| M9 display and device behavior | Use the current native guides and [desktop journey](reviews/REFERENCE_REFINEMENT_NATIVE_INPUT.md#concrete-next-actual-displaydevice-journey) on an identified display/controller/audio system. Preserve painted pre-held input, both navigation/resize directions, off-window release/fresh press, deliberate focus loss and joined shutdown. | Actual step frames, input/diagnostic records and numeric exit status, with OS/backend/device identities. Dummy SDL and synchronous dependency fixtures do not qualify physical timing or driver concurrency. |
| M9 accessibility and further visual work | Use the [current admitted gallery](reviews/UPPER_RACK_GALLERY_ADMISSION.md) and canonical layout/inspection contracts. Treat [older reference gaps](design/PRODUCT_REFERENCE_GAPS.md) as dated evidence; measure current small-label display usability and specify one platform's native semantic bridge before implementation. | Correct live inventory, focus/actions/value/status semantics, actual screen-reader journeys and source-bound visual comparisons. The relative paint budget does not establish frame rate; literal 1:1 equality remains unmet. |
| M9 release | Review [release readiness](RELEASE_READINESS.md), [dependencies and rights](DEPENDENCIES_AND_RIGHTS.md), actual installed artifacts and named DAW workflows. | Device deadlines, DAW save/reopen, redistribution/branding decisions, platform signing/notarization and qualified distribution remain separately observed gates. |

## Preserve the independent R4 owner

Preserve the other owners' unfinished work: [harmonic source/racks](development/2026-11-15-playable-continuation/CHECKPOINT.md),
[scanner and registration library/browser](development/2026-11-15-next-phase/CHECKPOINT.md),
[crossover/native retirement/deck](development/2026-11-15-fidelity-continuation/CHECKPOINT.md)
and [audio continuation](development/2026-11-15-audio-continuation/CHECKPOINT.md).
The earlier [product closure](PRODUCT_CONTINUATION_CLOSURE.md) and
[setup handoff](PRODUCT_HANDOFF.md) retain their original source-specific results;
their old workspace paths are not this streaming workspace.

The [waveform session](development/2026-11-14-waveform-continuation/README.md)
and its [checkpoint](development/2026-11-14-waveform-continuation/CHECKPOINT.md)
retain their other checkout and actual worker ledger. The implemented
[renderer contract](ROTARY_RENDERER_CONTRACT.md) and
[waveform acceptance](ROTARY_WAVEFORM_ACCEPTANCE.md) govern lifecycle,
scene/receiver symmetry, calibrated allocation and independent
[offline CLI](ROTARY_RENDER_CLI.md) qualification. The owner has its own local
results for these areas; consult its actual current records. Integration,
publication and final acceptance of that work remain with the owner. Its
source-bound full-waveform experiment does not replace those steps or transfer
ownership.
The later [d8 Linux full-mode pass](reviews/PRODUCT_LINUX_HOSTED_REVIEW.md)
likewise qualifies only its published inputs; it does not accept or discard the
other owner's dirty checkout, integration/publication/final acceptance of its
separate results or actual worker ledger.

Preserve `D+6` history capacity (maximum 12,806), the 8,192-entry per-write
journal, `max(D)+4` flush and the reviewed trajectory/borrow/rollback boundary.
Dense changes to both rotors every frame require calls of at most 512 frames
under the 1,024-event cap; legal 4,096-frame calls, repeated wraps, all sixteen
ordered stopped-rate pairs and overflow retain distinct acceptance. R5 audible
policy, R6 runtime/Engine integration and physical cabinet fidelity stay separate.
Inspect compatible remote advances before publication; never edit or remove the
other owner's checkout to simplify integration.

## Historical qualification and completion workflow

Earlier source-bound results remain in [STATUS.md](STATUS.md#historical-results-and-source-boundaries)
and the chronological [development log](DEVELOPMENT_LOG.md). Use the
[completed reference-refinement closure](REFERENCE_REFINEMENT_CLOSURE.md),
[interface recovery](INTERFACE_RECOVERY_HANDOFF.md),
[standalone handoff](STANDALONE_HANDOFF.md), [pedal handoff](PEDAL_HANDOFF.md)
and [calibration handoff](CALIBRATION_HANDOFF.md) for their named inputs and
original failures. The v1–v5 galleries keep their actual capture sources.
Do not repeat a completed session or use its strict checker to count this one.

Every future agent reads the whole plan and [AGENTS.md](../AGENTS.md), claims a
dependency-ready bounded task, records actual source/data/tool identities and
outcomes, and updates the relevant setup/status/next steps/log. Build selected
inputs before CTest and require nonempty required selections. Preserve 47 sound
identities, state4/readers 1–3, 91 shared sources and musical ownership. The
integrator accepts the owned diff, preserves concurrent advances, commits and
publishes authorized work with a fresh expected head and no force, then verifies
publication and its actual required results. Checkpoint each wave and retain
compact evidence before removing only owned reproducible intermediates.
