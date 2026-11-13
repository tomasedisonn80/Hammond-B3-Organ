# Milestone acceptance and evidence matrix

**Current engineering position: a working nominal offline organ and partial M3
console. Full M3 and the measured/playable product remain open.** This matrix
reconciles the continuation with the [M0-M9 plan](PLAN.md); it does not reinterpret
a software pass as physical admission. The plan's source gates are in the
[atlas, pp. 445-450](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=445) and
[pp. 481-486](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=481).

Updated 2026-11-13. The latest independently qualified code checkpoint is
`7469ebf759ced820cc34fc9012beff6f772e4b89`; its [final platform review](reviews/FINAL_CONTINUATION_PLATFORM.md)
verifies all four complete diagnostic archives. Current status, later result
publication and assignment completion belong to [STATUS.md](STATUS.md) and the
[separate continuation ledger](development/2026-11-13-continuation/README.md).
The [current handoff](CONTINUATION_HANDOFF.md) contains commands and exact
qualification identities. The original [navigation review](development/2026-11-13-continuation/52-documentation-navigation.md)
retains its earlier documentation-only scope; the later executed results below
are separately attributed.

## Evidence attached to named revisions

| Evidence | Observed scope | What it establishes |
| --- | --- | --- |
| Final qualified code, `7469ebf759ced820cc34fc9012beff6f772e4b89` | [Run 43380966473](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43380966473): all four jobs pass 46 suites (24 C++ and 22 Python), with 372 Python methods and zero failed/disabled/skipped tests. The [final platform audit](reviews/FINAL_CONTINUATION_PLATFORM.md) verifies complete archives, actual instrumentation and the retained earlier CRLF failure. | The completed nominal software scope and its two final repairs on the named platforms. Native host/device, physical fidelity and full M3 remain open. |
| Published qualification checkpoint, `2046b9388f6aab1122e37646b2f20199b5c6079f` | The integrator observed all 45 local Release suites pass in 12.91 seconds and all four jobs in [run 43376892064](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43376892064) report 45 suites passed. The local frozen tree and Markdown-only publication differences are retained in the [handoff](CONTINUATION_HANDOFF.md). | Revision-specific offline engineering evidence, including enabled allocation checks, the 16-file install and explicit console/owned-input benchmark cases. Assignment 52 did not independently download those job archives; the later final platform audit verified them separately. |
| Independently audited prior checkpoint, `9a5c99a862daf26a2bab9b05613c98803727a3e7` | The [platform review](reviews/CONTINUATION_PLATFORM_REVIEW.md) checked all four complete job archives: 43 suites, 352 Python methods, zero failed/disabled/skipped tests per job. Linux/macOS/Windows Release and Linux ASan/UBSan/leak instrumentation were inspected. | Published partial-key, ownership, lifecycle, trace and plot behavior on the actual named runners. Later changes require their own checks. |
| Scoped runtime review | [Runtime boundary review](reviews/RUNTIME_BOUNDARY_REVIEW.md): coherent frozen-source inspection and six focused Release suites; no actionable defect found. | Admission, atomic ownership, event timing, partial-key history, rate changes and parameter conversion within the reviewed scope. |
| Independent legacy comparison | [Legacy audio review](reviews/CONTINUATION_LEGACY_AUDIO.md): 11 exact WAV/PCM comparisons against a fresh pre-continuation build, 11 default-versus-explicit ideal/Off comparisons and six additional partition comparisons. All 15 old JSON metric fields agree after removing the three schema-2 additions. | Same-toolchain compatibility of the retained nominal model and selected cases; not cross-toolchain bit identity or unchanged metadata schema. |
| New retained example | [Two-second console demo](../examples/rendered/nominal-console-v2/README.md): actual 96,000-frame audio, untouched schema-2 bundle, independent byte/PCM checks and matching block-64/block-127 WAVs. Its 120 ms partial trace/plot has a different schedule and registration. | A reproducible synthetic example. Its recorded source is `9a5c99a`; publishing the later demonstration does not change that provenance or establish hardware fidelity. |
| Complete source review and factory maps | [Atlas review](research/ATLAS_REVIEW.md), the continuation's separate six-range review and [factory comparison](FACTORY_REFERENCE.md). All 549 manual assignments and 200 pedal positions are corroborated by two independent factory-image readings. | Documentary coverage and routing agreement. Absent companion code, physical captures, production gearing and instrument calibration remain absent. |

The [original ledger](development/AGENT_LEDGER.md), [original acceptance note](development/agent-notes/49-acceptance-matrix.md),
[original CI qualification](CI_QUALIFICATION.md) and
[console CI repair](reviews/CONSOLE_CI_REPAIR.md) retain earlier snapshots and
failures. A later repair does not erase a failed run. Original assignment IDs
01-60 are separate from the continuation's new IDs; planned rows are not
completed participation.

## M0-M9 gates

“Software gate passed” means the named behavior has implementation and retained
execution evidence. It does not mean every requirement in that milestone is
finished. An open or unrun requirement is not labeled a failed test unless an
actual execution failed.

| Milestone | Implemented and checked scope | Remaining exit evidence |
| --- | --- | --- |
| **M0 — reference and contracts** | **Nominal contract gate passed.** The [profile contract](PROFILE_FORMAT.md), strict authoring/compiler/runtime checks, source manifest, evidence classes, units and explicit unknowns give the initial data a bounded identity. | **Specimen/reference lock open.** Identify the actual organ, generator, AO-28 and cabinet revisions, condition and modifications; acquire applicable drawings and rights. The [capture protocol](CAPTURE_PROTOCOL.md) is an acquisition queue, not completed measurements. |
| **M1 — testable skeleton** | **Scoped offline software gate passed.** The prepared [Engine](ENGINE_API.md), bounded sample-offset events, frame clock, atomic rejection, disconnected processing and renderer are exercised across partitions and supported rates. [Owned input](INPUT_PROCESSOR.md) commits ownership only after Engine success; [rate changes](SAMPLE_RATE_LIFECYCLE.md) preserve running state under the declared stopped/same-thread lifecycle. | **Host/device gate open.** No native SDK adapter, device callback, concurrent profile publication/retirement or actual deadline qualification exists. The [host proposal](HOST_INTEGRATION.md) supplies requirements; typed core tests do not execute them in a host. |
| **M2 — shared generator** | **Nominal generator and documentary map gates passed.** Ninety-one shared sources advance continuously. [Factory runtime acceptance](FACTORY_RUNTIME_ACCEPTANCE.md) exercises all 1,098 manual branches with CSV-selected routes and additional coherent/boundary cases. [Numerical bounds](NUMERICAL_BOUNDS.md) retain the support floor and finite-window drift evidence. | **Physical generator gate open.** Production gearing, mechanical/tooth phases, pickup spectra/levels/loading, leakage and specimen calibration remain unresolved. [Pedal data](PEDAL_ROUTING.md) is corroborated routing, with no current pedal audio consumer. |
| **M3 — console** | **Nominal contact/percussion and control gates passed; full M3 open.** [Console dynamics](CONSOLE_DYNAMICS.md) integrates 1,098 independent contacts, partial targets and one shared upper-B percussion readiness state. Four A/B banks, routing-only Cancel, sustain masking and snapshots are checked by [console acceptance](CONSOLE_ACCEPTANCE.md). [Forty-three IDs](PARAMETERS.md), the [parameter bridge](PARAMETER_BRIDGE.md), [bounded ownership](NOTE_OWNERSHIP.md) and `B3CONTROLS2` with legacy-v1 loading are implemented. | **Remaining software:** prepared pedal routing first, then separately specified playable pedal mixture/events/controls; physical preset latch semantics, continuous drawbar travel, switching bandwidth and a declared expression model. [M3_NEXT_GATE.md](M3_NEXT_GATE.md) fixes the next scope and acceptance. **Physical admission:** identified contact/drawbar/percussion/pedal/expression measurements and independent loaded-model comparisons; nominal timing and scalar expression are not calibrated hardware. |
| **M4 — scanner** | **Engineering not implemented; acceptance not run.** No scanner network, mode DSP or scanner acceptance suite is present. The [atlas review](research/ATLAS_REVIEW.md) and [errata](research/ERRATA.md) preserve traversal and algebra hazards. | Reconstruct selected connectivity, loads, depth routing and continuous scanner history. Resolve the printed 15-entry/16-position traversal issue, then compare signed outputs, all modes and transitions against an independent loaded solver. Physical scanner captures close a separate response gate. |
| **M5 — organ electronics** | **Engineering not implemented; acceptance not run.** The current output is normalized dry mixing with a linear expression surrogate. No connected AO-28 solver, transformer/valve model, alias protection or calibrated G-G output exists. | Select revision-specific connectivity before component solving; retain independent operating-point, loaded AC/transient, convergence and alias tests. Resolve loading/feedback/transformer/device unknowns, then admit calibrated dry G-G captures before cabinet fitting. A component list and service readings do not supply that graph or calibration. |
| **M6 — Leslie electronics** | **Engineering not implemented; acceptance not run.** No Leslie amplifier, crossover or coupled driver-load module is present. | Keep 122 and 147 variants distinct. Obtain selected circuit/driver identities, connected signed differential ports and actual loading; retain independent loaded AC/polarity and nonlinear stability evidence. Electrical validation does not itself establish acoustic response. |
| **M7 — rotary acoustics** | **Engineering not implemented; acceptance not run.** No rotor dynamics, moving-path delay, directivity, microphone or room DSP is present. | Independently test horn/drum histories, causal paths/interpolation, transitions, tails and stereo/mono/rate behavior. Acquire qualified rotor trajectories, stationary-angle response and geometry/room evidence. Identical dry channels are not rotary stereo validation. |
| **M8 — calibration** | **Metadata/byte-integrity tooling passed; physical calibration not run.** [Capture validation](CAPTURE_VALIDATION.md) checks declared metadata and optional retained bytes. [PCM analysis](AUDIO_MEASUREMENTS.md) measures synthetic serialized samples. | Acquire an admitted rights-qualified hardware corpus; verify chain, clock, boundary/load, ancestry and duplicates. Freeze whole-group fit/holdout splits and acceptance thresholds with uncertainty; retain upstream fits and untouched evaluations. Current tools do not enforce all corpus or physical admission gates. |
| **M9 — product/release** | **Offline installation and typed core foundations passed.** The [16-file OfflineTools component](OFFLINE_INSTALL.md) has actual install/relocation checks, four native tools, plotter, profile and fixtures. The 43 internal parameters, saved controls and lifecycle adapters have core tests. | **Playable product open.** Implement and qualify actual VST3/device binaries, host exports/migrations, concurrent lifecycle, callbacks, native dimensional/accessibility UI and real host/device coverage. Select dependency/release rights and qualify packaging/signing. The offline install and internal IDs are not released native host contracts. |

For later dependency ordering and source-page locators, use
[M3_NEXT_GATE.md](M3_NEXT_GATE.md) and [PLAN.md](PLAN.md). Physical acquisition
may proceed alongside software work; the final calibration claim still requires
its own admitted evidence.

## Limits of the strongest existing checks

**Routing:** the factory chain includes independent image readings, compiled-map
comparison and actual manual runtime samples selected from the retained CSVs.
The runtime test reuses `TonewheelBank` for its source waveform oracle. It is
independent routing evidence, not an independent source-physics implementation
or a pedal-audio test. Keep the original profile/map authoring provenance and
later [attestation](FACTORY_REFERENCE.md) distinct.

**Processing:** [REALTIME.md](REALTIME.md) preserves the original 96 ideal/Off
observations and the separate enabled-path audit. The latter observes 126
Engine/owned-input calls plus separate translation, parameter and stopped
lifecycle calls, with zero intercepted C++ allocation/deallocation calls.
It does not intercept all C/system/custom allocation, prove concurrency, or
measure device deadlines. The bounded [benchmark](BENCHMARKING.md) reports
elapsed observations and errors without a performance pass threshold.

**Timing and state:** [Engine](ENGINE_API.md), [input](INPUT_PROCESSOR.md) and
[lifecycle](SAMPLE_RATE_LIFECYCLE.md) gates preserve declared same-offset ordering,
whole-call rejection and non-advancing zero-frame operations. Rate changes
preserve phase, contact history, readiness and frame count; elapsed seconds across
rate changes require the caller's segment record. These APIs require coordinated
note authority and stopped/same-processing-thread use.

**Evidence artifacts:** the producer, [independent verifier](RENDER_VERIFICATION.md)
and [PCM analyzer](AUDIO_MEASUREMENTS.md) check different claims about inputs,
bytes and signal statistics. Hash consistency does not authenticate source
provenance or turn synthetic audio into a specimen measurement. The
[trace](CONSOLE_TRACE.md) records state after events and before same-sample render
and advance. The [plotter](CONSOLE_TRACE_PLOTS.md) preserves exact contact/target
transitions and documented extrema reductions, retains the CSV hash, and does
not reconstruct every omitted trajectory/audio sample.

## Next actionable gate and durable handoff

Implement the first contract/admission step in [M3_NEXT_GATE.md](M3_NEXT_GATE.md):
typed 25-by-8 pedal routes and 200 independent connection states, followed by a
fixed-storage kernel returning four normalized bus excitations from the existing
single 91-source frame. The selected reference model supplies no guessed physical
mixture. Its tests must compare all 200 positions with both retained CSVs, check
disconnections/coherent branches, atomic failures, source-history preservation
and bounded processing.

Only after that gate should the next contract add the explicit four-bus/two-drawbar
transfer, public pedal events, ownership and saved-state migrations. Neither
step alone closes full M3. Current ownership and actual review/accounting states
are recorded in the [continuation manifest](development/2026-11-13-continuation/assignments.json)
and its ledger. The [separate record checker](CONTINUATION_CHECKS.md) must pass
its explicit sixty-complete gate before the continuation is declared finished;
that session gate does not close any additional product milestone.

Every subsequent task follows [AGENTS.md](../AGENTS.md): read current plan/status
and source pages, declare required evidence, preserve others' work, build coherent
snapshots, update shared status/next steps/log/contracts, commit and push completed
authorized work with expected-head and remote verification, and report actual
blocked or unrun gates.
