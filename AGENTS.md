# Standing instructions for every development agent

These instructions apply to the entire repository and all future agent sessions.
They implement the owner's request of 2026-11-12 to preserve a reliable, continuously
updated development handoff. Read them before modifying code or documentation.

## Start here

1. Read `README.md`, `docs/STATUS.md`, `docs/NEXT_STEPS.md`, the current
   `docs/CONTINUATION_HANDOFF.md`, and the latest entry in `docs/DEVELOPMENT_LOG.md`
   when those files exist.
2. Read `docs/PLAN.md`, `docs/research/ATLAS_REVIEW.md`, and the atlas chapters relevant
   to the task. The source PDF is `Hammond_B3_Leslie_Research_Atlas_500pp.pdf`.
3. Check the working tree and current remote branch. Preserve unrelated work and
   existing history. Never force-push or discard somebody else's changes.
4. Select the next dependency-ready milestone and declare the evidence needed to
   close it. Document missing inputs and continue independent useful work.

Use `docs/CONTINUATION_HANDOFF.md` for current operational commands and
`docs/M3_NEXT_GATE.md` for the next pedal-routing scope and acceptance criteria.
Read the separate continuation ledger at
`docs/development/2026-11-13-continuation/README.md` before selecting an assignment.
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
- Relevant design/data/test documentation whenever a contract changes.

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
For this continuation, update the actual states in
`docs/development/2026-11-13-continuation/assignments.json` and follow
`docs/CONTINUATION_CHECKS.md`. Run its separate checker with
`--expected-complete 60` only at the completed-session gate; the original
repository checker counts the earlier session and cannot substitute for it.
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
