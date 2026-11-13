# Agent 46 — proposed host integration contract

Assignment: wave 08, actual agent 46 of 60; own `docs/HOST_INTEGRATION.md`
and this note only. No SDK/framework, implementation, shared-root edit or commit.

## Inputs inspected

- Read `AGENTS.md`, README, STATUS, NEXT_STEPS, PLAN, latest DEVELOPMENT_LOG,
  ATLAS_REVIEW, chapter index, ENGINE_API, REALTIME, CONTROL_STATE_FORMAT,
  PARAMETERS and CONSOLE_EXTENSION.
- Read Engine/Types/Profile/ControlState/TonewheelBank headers, Engine.cpp and
  TonewheelBank.cpp; inspected parameter conversion and render scheduler source.
- Inspected existing timing/flush, rejection/overflow, disconnected-output and
  prepare/value-ownership engine tests, plus console/test coverage declarations.
- Read supplied atlas text using `pdftotext -layout`: pp. 379–402, 433–450,
  481–486. Page numbers checked against reconstructed chapter index.
  These were text inspections, not new visual or external-source verification.

## Deliverable and decisions

- Added a proposed SDK-agnostic host/device/editor boundary grounded in the
  actual 44.1/48/96 kHz, 65,536-frame and 1,024-event limits.
- Preserved stopped prepare/value ownership; separated existing same-owner
  operations from unimplemented command/snapshot/publication/retirement models.
- Defined checked clock/slice translation, stable cross-stream order, end carry,
  zero-frame consumption, transport independence, and explicit overflow recovery.
- Proposed bounded input-owner reconciliation and channels 1/2 for manuals;
  neither map is factory evidence, and pedal audio remains absent.
- Retained exactly 39 internal IDs, exact normalized-law compatibility, Cancel
  route bits, controls-only persistence and the held-key/checkpoint distinction.
- Listed focused adapter acceptance and dependency-ready tasks while retaining
  M3 contacts/percussion priority and M0/M9 physical/product gates.
- No native SDK APIs, versions or licensing conclusions are asserted; concrete
  wrappers still require primary-source verification and dependency review.

## Verification

- Executed document-only checks: `wc -w -l`, a Python local-link resolver, and
  `git diff --check --no-index /dev/null <file>` for each assigned new file.
  All 15 local links resolve; whitespace checks emit no diagnostics (exit 1 is
  the expected new-file difference). Document and note remain within their bounds.
- No build, DSP test, host/device, concurrency, accessibility or timing experiment
  was run for this documentation assignment.
- Existing test/audit results are linked as prior evidence only. Every proposed
  adapter acceptance case remains `not_run`.

## Handoff

Integrator owns shared navigation/status/log updates and publication. Reuse the
core contracts now; implement and test ownership transfer before any concurrent
UI, state-save or live graph-replacement claim. No new adapter stub was created.
