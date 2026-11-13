# Project guide

The available program is a nominal dry-organ engine with an offline WAV renderer
and retained-bank console controls. Use it to build and test synthetic audio
fixtures. Playable VST3/device applications, native UI and measured instrument
fidelity retain separate gates in the [full plan](PLAN.md).

This guide explains where to find decisions and evidence. [STATUS.md](STATUS.md)
owns current implementation and verification; a historical note, proposed contract
or configured workflow does not supersede it.

## Start with the question you need to answer

| Question | Read |
| --- | --- |
| What is the full product plan? | [PLAN.md](PLAN.md): M0-M9 deliverables, dependencies and exit evidence. |
| What works, and what has actually passed? | [STATUS.md](STATUS.md), then [CI qualification](CI_QUALIFICATION.md) for revision-specific hosted results. |
| What should happen next? | [NEXT_STEPS.md](NEXT_STEPS.md), then the [session ledgers below](#session-ledgers-and-continuation) to check existing assignments. |
| How do I resume with exact commands and evidence? | [SESSION_HANDOFF.md](SESSION_HANDOFF.md), read with its dated inventory and the current status. |
| Which milestone gates are actually closed? | [ACCEPTANCE_MATRIX.md](ACCEPTANCE_MATRIX.md), which separates software, documentary and physical evidence. |
| Why was a choice made, and what failed? | [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md) and the linked or numbered agent evidence notes. |
| What must every development session preserve? | [AGENTS.md](../AGENTS.md): evidence boundaries, ownership, verification and durable handoff. |

## Build, render and install

Start at the [README quick start](../README.md) for the build and a two-second dry
render. The tools use a C++20 compiler, CMake 3.21+ and Python 3.10+; the core has
no audio/GUI framework or host-SDK dependency.

| Task | Practical reference |
| --- | --- |
| Build and test on Linux, macOS or Windows | [BUILD.md](BUILD.md): presets, explicit commands, generated profile, configurations and sanitizer limits. |
| Render a registration or an event score | [RENDER_FORMAT.md](RENDER_FORMAT.md): CLI options, event grammar, sample timing, output format and errors. |
| Try repeatable musical examples | [examples/README.md](../examples/README.md): five synthetic fixtures and their declared settings. |
| Hear the retained example and inspect its replay | [Four-second demo](../examples/rendered/nominal-two-manual-v1/README.md) and [DEMO_REPLAY.md](DEMO_REPLAY.md): exact retained bytes, independent checks and the observed local replay. |
| Retain the inputs and outputs of a render | [RENDER_EVIDENCE.md](RENDER_EVIDENCE.md): hashes, raw logs, metrics and the evidence bundle. |
| Install or move the offline tool locally | [OFFLINE_INSTALL.md](OFFLINE_INSTALL.md): exact eight-file component, explicit profile/event paths and relocation checks. |

Build before running CTest; CTest does not compile executables or create the
generated profile. Render to a new output filename: the CLI preserves existing
files and requires hard-link support for publication. The local install provides
offline file rendering; it does not package live device playback or a plugin.
Platform compatibility and current hosted gates remain in the qualification record.

## Find the contract behind a claim

| Area | Contracts and retained evidence |
| --- | --- |
| Initial architecture and model | [Implementation contract](IMPLEMENTATION_CONTRACT.md), [profile format](PROFILE_FORMAT.md) and [engine API](ENGINE_API.md). The nominal model is unmeasured; source IDs, MIDI notes and array indices are distinct. |
| Controls and saved state | [Console extension](CONSOLE_EXTENSION.md), [control-state format](CONTROL_STATE_FORMAT.md) and [parameters](PARAMETERS.md). Saved controls exclude held keys, source phase and transient DSP histories; internal IDs are not qualified host exports. |
| Manual and pedal routing | [Factory comparison](FACTORY_REFERENCE.md) and [pedal routing](PEDAL_ROUTING.md). Later independent transcriptions corroborate the reconstructed routes without changing original authoring provenance or proving physical calibration. |
| Exhaustive manual runtime routing | [Factory runtime acceptance](FACTORY_RUNTIME_ACCEPTANCE.md): CSV-selected routes, coherent cases, negative probes and the shared-source-oracle limitation. |
| Next M3 console integration | [M3 acceptance contract](M3_ACCEPTANCE_CONTRACT.md), [console dynamics](CONSOLE_DYNAMICS.md) and [compiled model metadata](MODEL_METADATA.md). Standalone model tests do not establish integrated renderer behavior. |
| Serialized audio and retained bundles | [PCM measurements](AUDIO_MEASUREMENTS.md) and [independent bundle verification](RENDER_VERIFICATION.md). Integrity and synthetic signal measurements do not establish a physical specimen match. |
| Processing limits | [Callback audit](REALTIME.md), [numerical bounds](NUMERICAL_BOUNDS.md) and [benchmark](BENCHMARKING.md). Read each observation's scope; these do not qualify live audio deadlines. |
| Physical acquisitions | [Capture format](CAPTURE_FORMAT.md), [capture validation](CAPTURE_VALIDATION.md) and [acquisition protocol](CAPTURE_PROTOCOL.md). Planned metadata, actual recordings, verified bytes and physical admission are separate states. |
| Repository and platform checks | [Repository checks](REPOSITORY_CHECKS.md), [CI workflow](CI.md) and [CI qualification](CI_QUALIFICATION.md). Passing links/hashes or one revision's matrix does not qualify later changes. |
| Final independent reviews | [Core](reviews/FINAL_CORE_REVIEW.md), [evidence tooling](reviews/FINAL_EVIDENCE_REVIEW.md), [claims](reviews/FINAL_CLAIMS_REVIEW.md), [integration](reviews/FINAL_INTEGRATION_REVIEW.md), [platforms](reviews/FINAL_PLATFORM_REVIEW.md) and [publication readiness](reviews/FINAL_READINESS_REVIEW.md). Each names its actual inspected revision and executed scope. |
| Future host, device and editor work | [Host integration proposal](HOST_INTEGRATION.md). This is a design handoff; its adapter acceptance cases remain unexecuted until implementation and evidence exist. |

Evidence classes describe inputs: `documented`, `measured`, `derived`, `proposed`
and `unknown`. Test outcomes describe execution: `pass`, `failed`, `blocked`,
`not_run` and `inconclusive`. Keep the exact code/data identity, setup, criterion,
observed result and limitation with every acceptance claim.

## Read the original source and complete reviews

The unchanged [500-page research atlas](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf)
is the original supplied source. The [source manifest](research/source-manifest.json)
retains its exact identity and the absence of referenced companion files at
baseline. The [chapter index](research/chapter-index.json) provides all 80 chapter
titles and page ranges; [errata](research/ERRATA.md) records implementation hazards.

The [complete atlas review](research/ATLAS_REVIEW.md) consolidates the original six
disjoint review ranges and links their detailed notes. It records the evidence
available during that review. For subsequent documentary routing corroboration,
read the [factory comparison](FACTORY_REFERENCE.md); for current engineering
results, read [STATUS.md](STATUS.md). The independent continuation has another
complete review in its own ledger below. Neither review recovers absent companion
data or substitutes for acquired instrument measurements.

## Check rights and distributed material

The [dependency and rights inventory](DEPENDENCIES_AND_RIGHTS.md) distinguishes
repository contents, the local install, CI dependencies and generated outputs.
[THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md) preserves identified notices;
the [research source-rights record](research/RIGHTS_AND_SOURCES.md) tracks supplied
and consulted material. No project-wide license has been selected. Source identity,
public availability and a build/test pass do not establish redistribution permission.
Use the inventory's gate before introducing a dependency, asset or release payload.

## Session ledgers and continuation

| Session | Assignment and evidence records |
| --- | --- |
| Original ten-wave implementation session | [AGENT_LEDGER.md](development/AGENT_LEDGER.md), [WAVE_LOG.md](development/WAVE_LOG.md) and [agent-notes](development/agent-notes/), with the original assignment IDs 01-60 and actual progress. |
| Independent 2026-11-13 continuation | [Continuation ledger](development/2026-11-13-continuation/README.md), with its own numbered review notes and contact/percussion work queue. |

Read the newest retained ledger and shared status before choosing work, especially
before starting M3 contact/percussion implementation: the independent continuation
may already have assigned or advanced it. Assignment numbers belong to their
session; the continuation's six review agents are not additional completions in
the original session. Research waves, development waves and M0-M9 milestones are
different organizations and do not measure the same progress.

Preserve existing histories when `main` advances. Record actual changes, commands,
failures and unrun gates in the assigned evidence note; the integrating agent owns
shared status and publication. A read-only navigation/data check is available as
`python3 tools/check_repository.py --json`; see its [scope and limits](REPOSITORY_CHECKS.md).
