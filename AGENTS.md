# Standing instructions for every development agent

These instructions apply to the entire repository and all future agent sessions.
They implement the owner's request of 2026-11-12 to preserve a reliable, continuously
updated development handoff. Read them before modifying code or documentation.

## Start here

1. Read `README.md`, `docs/STATUS.md`, `docs/NEXT_STEPS.md`, and the latest entry in
   `docs/DEVELOPMENT_LOG.md` when those files exist.
2. Read `docs/PLAN.md`, `docs/research/ATLAS_REVIEW.md`, and the atlas chapters relevant
   to the task. The source PDF is `Hammond_B3_Leslie_Research_Atlas_500pp.pdf`.
3. Check the working tree and current remote branch. Preserve unrelated work and
   existing history. Never force-push or discard somebody else's changes.
4. Select the next dependency-ready milestone and declare the evidence needed to
   close it. Document missing inputs and continue independent useful work.

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

Run the necessary checks, inspect the diff, and commit completed authorized work in
reviewable chunks. When pushing is authorized (as in the initial implementation task),
push to the agreed branch and verify the remote commit. Do not claim a push or CI pass
without observing it. If access or a gate blocks completion, record the exact blocker,
preserve the useful work, and give a precise handoff. Do not send messages or create
unsolicited issues on the owner's behalf.

## Scope of completion claims

A working offline renderer is an engineering deliverable. A playable VST3/standalone
product, native UI, measured AO-28/scanner/Leslie model, hardware fidelity, host
qualification, licensing clearance and signed installers each require their own
retained evidence. Mark them pending until that evidence exists.
