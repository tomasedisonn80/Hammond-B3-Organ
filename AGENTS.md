# Standing instructions for every development agent

These instructions apply to the entire repository and all future agent sessions.
They implement the owner's standing handoff and publication requests of
2026-11-12 and 2026-11-13. Read them before modifying code or documentation.

## Current session and standing continuation rule

An independent [capture/calibration-readiness session](docs/development/2026-11-13-calibration/README.md)
starts at `38c1fac`. Its sixty new assignments advance the offline M0/M8 tools
under [CALIBRATION_SCOPE.md](docs/CALIBRATION_SCOPE.md): audio-file inspection,
cross-capture integrity and split auditing, fixed analysis and reproducible
acceptance evidence. It owns new capture/corpus/calibration tools and companion
contracts. Preserve the existing capture v1 meaning, unknown physical values and
all other active tracks. Synthetic test audio cannot close a hardware gate.
Its operational entry point is [CALIBRATION_HANDOFF.md](docs/CALIBRATION_HANDOFF.md).
Read the current session manifest before counting assignments or taking ownership.

A separate [rotary motion and propagation session](docs/development/2026-11-13-rotary/README.md)
starts at `96a37a9`. Its own sixty assignments advance a nominal M7 research
module under [ROTARY_SCOPE.md](docs/ROTARY_SCOPE.md). It owns rotary-specific
modules, tools, tests and records; it does not own the scanner or standalone
tracks. Read all active scopes before choosing work. Keep separate horn/drum
radiation-boundary inputs, one physical trajectory per rotor, explicit effect
ownership and unresolved M5/M6 dependencies. Its synthetic fixtures cannot be
promoted to factory dimensions, physical captures or an end-to-end fidelity pass.

An independent [native standalone session](docs/development/2026-11-13-next-phases/README.md)
also begins at `ba0d9c9`, with its own sixty actual assignments and ten waves.
Its [scope](docs/STANDALONE_SCOPE.md) advances the M9 adapter against the existing
nominal dry core while the scanner track continues. Inspect both current tracks
and their actual manifests before taking ownership. Standalone-specific code
belongs under `apps/standalone/`; it must not silently change Engine sound,
parameter identities, state formats or plugin UUIDs. Preserve the other track's
work and integrate observed remote advances before publication.

The standalone session also owns the dependency-ready documentary chapel
catalog under `data/registrations/`, its compiler/admission tests and explicit
control-file audition tooling. Preserve the distinction between atlas tap
assignments and current nominal drawbar gains. This source import must not be
reported as physical preset latching, loaded-gain calibration or a new saved-state
format. Its two independent readings do not independently verify the atlas's
underlying factory Table IV; that stronger primary-document gate stays visible.

Another active track is [2026-11-13 scanner development](docs/development/2026-11-13-scanner/README.md), starting at `6dc0702`. Its [actual assignment manifest](docs/development/2026-11-13-scanner/assignments.json) belongs only to this newly requested sixty-agent, ten-wave session. The completed [pedal session](docs/development/2026-11-13-pedals/README.md), original and console ledgers remain historical and must not be rewritten or recounted. Consult the newest session together with current status and next steps before starting work.

For every future development session, continue the next dependency-ready phase, retain the source basis and limits of the model, run meaningful checks, update status/next steps/development log and affected contracts, then commit and push the completed work to `main` under the owner's standing authorization. Inspect and integrate concurrent changes; never force-push. A user-requested agent count is the scope of that session, not permission to invent participation. Record the real assignment identity, owned files, result and verification. Publication and physical-fidelity claims each require their own observed evidence.

## Start here

1. Read `README.md`, `docs/STATUS.md`, `docs/NEXT_STEPS.md`, the relevant current
   handoff (`docs/STANDALONE_HANDOFF.md`, `docs/CALIBRATION_HANDOFF.md`,
   `docs/SCANNER_HANDOFF.md`, or the separate active track's scope), and the latest entry in `docs/DEVELOPMENT_LOG.md`.
   If a later session replaces the operational entry point, follow the explicit
   current-status pointer while preserving earlier handoffs as dated history.
2. Read `docs/PLAN.md`, `docs/research/ATLAS_REVIEW.md`, and the atlas chapters relevant
   to the task. The source PDF is `Hammond_B3_Leslie_Research_Atlas_500pp.pdf`.
3. Inspect `git status --short`, the actual `HEAD` commit/tree and the current
   remote branch. Preserve unrelated work and existing history. Never force-push
   or discard somebody else's changes. A historical report does not identify an
   uncommitted worktree or qualify changed code.
4. Select the next dependency-ready milestone, agree owned paths with the
   integrator when working concurrently, and declare the evidence needed to
   close it. Document missing inputs and continue independent useful work.

Use the newest session ledger and `docs/NEXT_STEPS.md` for the active scope.
[SCANNER_HANDOFF.md](docs/SCANNER_HANDOFF.md) records the scanner continuation.
[PEDAL_HANDOFF.md](docs/PEDAL_HANDOFF.md) retains the dry-organ build, render,
trace/plot, installation and native commands. The concrete next model contract
is [M3_REMAINING_AND_SCANNER_GATE.md](docs/M3_REMAINING_AND_SCANNER_GATE.md);
its graph, numerical and acquisition requirements remain authoritative; current
implementation and executed results are in the scanner handoff and status.
Use the frozen scanner numerical contract before grading new runtime behavior.
`docs/CONTINUATION_HANDOFF.md` retains the preceding console checkout commands;
`docs/M3_NEXT_GATE.md` retains the original pedal-kernel acceptance contract.
The separate `docs/development/2026-11-13-continuation/README.md` is completed
history and must not substitute for the current assignment manifest.
`docs/SESSION_HANDOFF.md` and `docs/development/AGENT_LEDGER.md` preserve the original
session's handoff and sixty-assignment history. Historical snapshots do not
replace inspecting current code, ownership and the exact revision's actual test
results. Make the next work and its required evidence concrete enough to resume.

## Evidence and architecture

- Follow atlas implementation milestones M0-M9; its ten research waves are a
  different organization. Keep engineering completion and physical fidelity separate.
- Every physical value needs units, evidence class, applicable variant, source/page
  locator and an uncertainty or explicit missing-evidence reason. Unknown is not zero.
- Name provisional models and their replacement path. Never call a synthetic render,
  a formula-derived routing table, or a passing software test a measured instrument.
- Keep source numbers, physical terminals, MIDI notes and storage indices distinct.
  Tone sources are shared and free-running; notes never restart their phase.
- Preserve B-3/AO-28 and Leslie 122/147 variant boundaries. Do not infer complete
  circuits, factory tuning, or companion files from prose that only references them.
- Keep the core independent of a host SDK. Preparation, file access, allocation,
  destruction, locks, logging and UI operations stay outside audio processing.
- Tests must cover meaningful behavior: timing, block partition invariance,
  boundary handling, numerical safety, musical state and declared limitations.
- Do not add dependencies or redistribute third-party assets without recording
  version, provenance and applicable rights. Preserve the supplied PDF unchanged.

## Finish every task with a durable handoff

Before claiming completion, update all of the following as appropriate:

- `docs/STATUS.md`: current milestone, implemented behavior, verified behavior,
  provisional assumptions, blocked/not-run gates and known limitations.
- `docs/NEXT_STEPS.md`: the next concrete task, its inputs, affected modules,
  acceptance criteria and dependencies; distinguish engineering from acquisition.
- `docs/DEVELOPMENT_LOG.md`: actual changes, commands run, results, failures,
  limitations, and relevant commit or report identifiers.
- Relevant design/data/test documentation whenever a contract changes. Replace
  stale current next-step claims with the implemented contract and its evidence;
  preserve earlier dated observations, failures and unrun scopes.

A handoff must name the actual commit or frozen tree, toolchain and relevant data
or dependency identities; list owned files and concrete commands with their
working directory and prerequisites; distinguish execution from source inspection;
and state the next task's inputs and acceptance criteria. Separate setup failures,
project failures, queued/unacquired runners and completed tests. An artifact hash
or workflow dispatch alone is not a host, platform, timing or fidelity pass.
Do not invent a configure option or reuse a stale test count: inspect the actual
CMake inputs and discover the selected configuration. Build test inputs before
CTest, and use `--no-tests=error` for a required filtered acceptance gate.

Subagents write their assigned evidence note and report to the integrating agent;
the integrator owns the shared status files and prevents conflicting edits. Record
actual assignments and outcomes. Never fabricate agent participation or test results.

The owner's standing repository workflow is to run the necessary checks, inspect the
diff, commit completed development work in reviewable chunks, and push it to `main`.
Apply this workflow in future development sessions unless a later user instruction
or repository protection requires a different branch/review path. Verify the remote
commit; do not claim a push or CI pass without observing it. If access or a gate
blocks completion, record the exact blocker, preserve the useful work, and give a
precise handoff. Do not send messages or create unsolicited issues on the owner's
behalf.

## Scope of completion claims

A working offline renderer is an engineering deliverable. A playable VST3/standalone
product, native UI, measured AO-28/scanner/Leslie model, hardware fidelity, host
qualification, licensing clearance and signed installers each require their own
retained evidence. Mark them pending until that evidence exists.

## Continuing across sessions

Read the newest retained session ledger under `docs/development/` as well as the
shared status files. A continuation must preserve previous assignment identities
and execution results; do not count an earlier agent as a newly dispatched agent.
The original and 2026-11-13 continuation each requested sixty assignments in ten
waves. That is their session scope, not a requirement to dispatch sixty agents
for every later task. Report actual dispatched/completed work separately from
planned rows and preserve the latest user-authorized scope.
Update actual states in the newest session's manifest. The completed console
continuation uses `docs/development/2026-11-13-continuation/assignments.json` and
`docs/CONTINUATION_CHECKS.md`; its checker does not count the current pedal session.
The completed pedal session has its own [record checker](docs/PEDAL_SESSION_CHECKS.md):

```sh
python3 tools/check_pedal_session.py --repo . --json
```

This checks retained consistency and reports actual declared states; it does not
attest external dispatch or substitute for the integrator's substantive acceptance.
Use `--expected-complete 60` only after all sixty actual assignments in that named
session have completed and been accepted. Earlier checkers cannot substitute for
a new session's accounting. A later distinct session must retain its own ledger
and applicable validation rather than rewriting this one.
If `main` advances during work, inspect and integrate the new commits, rerun the
affected checks, and publish with an expected-head guard. Never overwrite another
session's completed work or clear an unresolved gate merely to close a wave.

Concurrent header changes can alter object layout. Qualify a core, its consumers
and tests from one coherent frozen source snapshot, or coordinate an explicit
source freeze. Never link an older library against later live headers and treat
that result as a product defect. Publication gates must identify the staged tree
they tested and keep unfinished workers' files outside that checkpoint.

When introducing a new nominal model, preserve its model identity, parameter units,
source-page basis and limitations with the code. Ordinary saved controls must remain
separate from contact trajectories, percussion readiness, source phase and other
transient DSP histories. Specify migrations before changing a saved-state format.
