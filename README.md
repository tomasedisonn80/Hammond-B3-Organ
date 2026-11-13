# Hammond B-3 Organ

A project to recreate a vintage Hammond B-3 and Leslie system, guided by the
repository's **500-page research and build atlas**.

**Current stage:** a working nominal dry-organ engine and offline WAV renderer,
with strict data contracts and independent tests. The core has 91 shared,
continuously running sources, two manuals, drawbars, sample-offset events and
explicit clock/error handling. Four retained A/B banks, routing-only Cancel and
versioned control snapshots provide early console behavior. Optional independent
contact travel, explicit partial-key targets and one shared percussion readiness
state extend the nominal console. Bounded typed note ownership, normalized control
mapping and phase-preserving rate changes support future host integration. Ideal
contacts and percussion off preserve the original renderer defaults.
The selected source and console profiles are **nominal and unmeasured**.

The current executable renders WAV files offline. The product plan targets a
playable VST3 instrument and audio-device standalone application, with an
inspectable organ/Leslie engine and the atlas's dimensional, accessible interface.
Scanner, AO-28 electronics, Leslie acoustics, physical calibration and the native
UI remain future work. No current result establishes a measured one-to-one
instrument match. Start with the [project guide](docs/PROJECT_GUIDE.md) for the
plan, practical workflows, evidence contracts and session history.

Start with the build below or the retained [two-second console demo](examples/rendered/nominal-console-v2/README.md).
The [current developer handoff](docs/CONTINUATION_HANDOFF.md) gives reproducible
render, trace, plot and install commands. The next dependency-ready development
task is the [prepared pedal-routing kernel](docs/M3_NEXT_GATE.md); **full M3
remains open**. The [current status](docs/STATUS.md) and separate
[continuation ledger](docs/development/2026-11-13-continuation/README.md) record
published checkpoints, actual checks and the completed sixty-worker continuation.
All **60 distinct assignments in ten waves** are complete, with a separate
[actual-state manifest](docs/development/2026-11-13-continuation/assignments.json)
and one retained note per worker. [AGENTS.md](AGENTS.md) makes the documented
handoff, verification and commit/push workflow mandatory for future agents.

## Build and test

Requirements: a C++20 compiler, CMake 3.21 or newer, and Python 3.10 or newer.
The core and authoring compiler need no downloaded audio/GUI framework.

```sh
cmake --preset debug
cmake --build --preset debug
ctest --preset debug
```

The build validates the authoring JSON and generates `build/nominal.b3p`.

Render a two-second dry registration (Linux/macOS single-configuration build):

```sh
cmake -E make_directory out
./build/hammond_render --profile build/nominal.b3p --output out/dry-organ.wav \
  --frames 96000 --sample-rate 48000 --block-size 64 --seed 0 \
  --drawbars 888000000 --note 60 --fail-on-clip
```

The output is stereo PCM16 with identical dry channels. Existing output files
are preserved; choose a new filename for another render. The CLI reports profile
identity, peak, RMS and clipping as JSON. See the [offline contract](docs/RENDER_FORMAT.md)
for event files, strict limits and the hard-link filesystem requirement.

See [build instructions](docs/BUILD.md) for explicit commands, Release and
sanitizer builds, and platform qualification limits.
The [OfflineTools local install](docs/OFFLINE_INSTALL.md) places the renderer,
inspection tools, trace plotter, compiled profile and event fixtures in a
relocatable prefix of your choice.

## Repeatable audio examples

Listen to the [two-second nominal console example](examples/rendered/nominal-console-v2/bundle/render.wav).
Its [evidence package and replay instructions](examples/rendered/nominal-console-v2/README.md)
demonstrate partial key travel, shared percussion, lower-manual independence,
Cancel/reselection and percussion masking. The schema-2 bundle retains the score,
profile, logs, identities and independent PCM checks. Its linked partial-key
CSV/SVG illustrates a **separate 120 ms diagnostic scenario**, not the WAV's score.
The [trace contract](docs/CONSOLE_TRACE.md) and [plot contract](docs/CONSOLE_TRACE_PLOTS.md)
explain exactly what these diagnostics show and how they are reduced for display.

The original [four-second dry-organ example](examples/rendered/nominal-two-manual-v1/bundle/render.wav)
and its [evidence package](examples/rendered/nominal-two-manual-v1/README.md) remain
available for the earlier ideal-contact, percussion-off behavior.

[Five short event fixtures](examples/README.md) exercise both manuals, A4 pitch,
coherent foldback, and bank/Cancel behavior. The [evidence wrapper](docs/RENDER_EVIDENCE.md)
retains exact inputs, renderer hashes, logs and WAV statistics. The independent
[PCM analyzer](docs/AUDIO_MEASUREMENTS.md) measures serialized samples and can
check the steady portion of a declared single-tone fixture. The independent
[bundle verifier](docs/RENDER_VERIFICATION.md) checks retained artifacts, claims
and metrics without trusting the producer’s Boolean assertions. These outputs are
synthetic engineering evidence.

[CI](docs/CI.md) qualifies Linux GCC, macOS AppleClang and Windows MSVC Release,
plus Linux ASan/UBSan with leak checking. The corrected published code
`7469ebf759ced820cc34fc9012beff6f772e4b89` passed **all 46 suites and 372 Python
methods in each of the four jobs**, with zero failed/disabled/skipped tests in
[run 43380966473](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43380966473).
The [final platform audit](docs/reviews/FINAL_CONTINUATION_PLATFORM.md) retains
complete diagnostic-log and archive verification, including the earlier Windows
CRLF failure and its repair. Qualification belongs to the named revision and
executed scope; [current status](docs/STATUS.md) records later outcomes.

## Project navigation

| Document | Purpose |
|---|---|
| [Project guide](docs/PROJECT_GUIDE.md) | Practical reading order, workflows, evidence boundaries and session ledgers |
| [Status](docs/STATUS.md) | What is implemented, what passed, and what remains provisional |
| [Next steps](docs/NEXT_STEPS.md) | Next concrete tasks, dependencies and acceptance evidence |
| [Current operational handoff](docs/CONTINUATION_HANDOFF.md) | Current identities, render/trace/install commands, ownership and publication procedure |
| [Next M3 gate](docs/M3_NEXT_GATE.md) | Prepared pedal-routing kernel, independent acceptance and later playable-pedal integration |
| [Acceptance matrix](docs/ACCEPTANCE_MATRIX.md) | M0-M9 requirements, actual evidence and open gates |
| [Original session handoff](docs/SESSION_HANDOFF.md) | Preserved commands and evidence for the original session's dated checkpoint |
| [Original assignment ledger](docs/development/AGENT_LEDGER.md) | Original 60 assignment slots; separate from the new continuation |
| [Development log](docs/DEVELOPMENT_LOG.md) | Actual changes, commands, results and limitations |
| [Full project plan](docs/PLAN.md) | Atlas M0-M9 implementation sequence and exit gates |
| [Agent instructions](AGENTS.md) | Mandatory workflow and durable handoff for every future agent |
| [Implementation contract](docs/IMPLEMENTATION_CONTRACT.md) | Initial scope and architecture |
| [Profile contract](docs/PROFILE_FORMAT.md) | Typed, bounded authoring/runtime boundary |
| [Engine interface](docs/ENGINE_API.md) | Timing, key ownership, source/mix behavior |
| [Console controls](docs/CONSOLE_EXTENSION.md) | Retained banks and Cancel/panic separation |
| [Control state format](docs/CONTROL_STATE_FORMAT.md) | Bounded control-only save/load |
| [Console dynamics](docs/CONSOLE_DYNAMICS.md) | Independent contacts, shared percussion, timing and evidence boundaries |
| [Console acceptance](docs/CONSOLE_ACCEPTANCE.md) | Independent PCM and evidence-bundle checks for the nominal model |
| [Console traces](docs/CONSOLE_TRACE.md) | Sample-by-sample contact, readiness, routing, phase and audio diagnostics |
| [Trace plots](docs/CONSOLE_TRACE_PLOTS.md) | Bounded standalone SVG views of key motion, contacts, readiness and audio |
| [Model metadata](docs/MODEL_METADATA.md) | Export the actual compiled nominal factory values and units |
| [Internal parameters](docs/PARAMETERS.md) | 43 proposed permanent control identities; original 39 preserved |
| [Native parameter bridge](docs/PARAMETER_BRIDGE.md) | Allocation-free conversion of normalized controls into fixed Engine targets |
| [Note ownership](docs/NOTE_OWNERSHIP.md) | Bounded channel/note-ID ownership and original-route retention |
| [Input transaction](docs/INPUT_PROCESSOR.md) | Commit note ownership only after Engine accepts the block |
| [Sample-rate lifecycle](docs/SAMPLE_RATE_LIFECYCLE.md) | Preserve phases, contact history and shared readiness across supported rate changes |
| [Pedal routing](docs/PEDAL_ROUTING.md) | Reconstructed 25-by-8 data; pedal audio remains pending |
| [Factory comparison](docs/FACTORY_REFERENCE.md) | Two independent Table III readings and complete routing comparison |
| [Factory runtime gate](docs/FACTORY_RUNTIME_ACCEPTANCE.md) | All manual routes exercised against CSV-selected expectations |
| [Console demo](examples/rendered/nominal-console-v2/README.md) | Two-second schema-2 audio bundle and a separate partial-key diagnostic plot |
| [Original demo replay](docs/DEMO_REPLAY.md) | Retained four-second example, independent integrity checks and local replay |
| [M3 acceptance contract](docs/M3_ACCEPTANCE_CONTRACT.md) | Contact, percussion and history requirements behind the implemented nominal console |
| [Capture contract](docs/CAPTURE_FORMAT.md) | Planned/recorded metadata, explicit unknowns and optional byte verification |
| [Acquisition protocol](docs/CAPTURE_PROTOCOL.md) | Prioritized physical captures, admission gates and holdout grouping |
| [Offline format](docs/RENDER_FORMAT.md) | Renderer and event-fixture contract |
| [Numerical bounds](docs/NUMERICAL_BOUNDS.md) | Preparation limits and finite-window drift evidence |
| [Benchmark](docs/BENCHMARKING.md) | Bounded workload timing with explicit limitations |
| [Repository checks](docs/REPOSITORY_CHECKS.md) | Source, navigation, local links and data integrity |
| [Continuation record checks](docs/CONTINUATION_CHECKS.md) | Separate actual assignment states in the [continuation manifest](docs/development/2026-11-13-continuation/assignments.json) and its explicit final completion gate |
| [Dependencies and rights](docs/DEPENDENCIES_AND_RIGHTS.md) | Actual distributed material, provenance, notices and unresolved permissions |
| [Complete atlas review](docs/research/ATLAS_REVIEW.md) | Full 500-page coverage, milestone interpretation and source limits |
| [Source manifest](docs/research/source-manifest.json) | Preserved PDF identity and missing companion assets |
| [Review notes](docs/development/agent-notes/) | Actual agent assignments and retained evidence |
| [Console continuation](docs/development/2026-11-13-continuation/README.md) | New sixty-agent, ten-wave ledger and integration checkpoints |

## Source and evidence

The [research atlas](Hammond_B3_Leslie_Research_Atlas_500pp.pdf) contains 80 chapters
across 500 pages. Six disjoint review assignments covered every page and visually
checked important tables/figures. The PDF's referenced companion files were not
included in the baseline repository; new code/data are labeled reconstructions.

The baseline generator profile specifies 91 shared sources, explicit 61-by-9 manual
routing, normalized amplitude, proposed initial phases and 12-TET tuning. Hardware
identity, production gearing, pickup calibration, contact timing, circuit response,
rotor behavior and acoustics remain acquisition/validation work. Historical G-G
service readings are not used as oscillator amplitudes.

Two independent direct-image factory-table transcriptions now corroborate every
manual assignment and pedal position in the retained data. Their comparison is
documentary routing evidence; source tuning and physical calibration remain open.
The [dependency and rights inventory](docs/DEPENDENCIES_AND_RIGHTS.md) and
[third-party notices](THIRD_PARTY_NOTICES.md) record applicable source boundaries
and unresolved permissions; this repository has no selected project-wide license.

Every future development session must update status, next steps and the development
log, retain real verification evidence, and commit/push completed work under the
standing repository workflow in `AGENTS.md`.
