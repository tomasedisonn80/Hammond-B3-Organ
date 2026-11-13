# Agent 42 — physical acquisition and admission protocol

## Assignment and source reads

Actual wave-07 assignment: write `docs/CAPTURE_PROTOCOL.md` and this note only.
Read `AGENTS.md`, `README.md`, `docs/STATUS.md`, `docs/NEXT_STEPS.md`,
`docs/PLAN.md`, latest development-log entry, capture format/planned example,
capture validation documentation, atlas review, rights/source review and errata.
Inspected current `main`/`origin/main` and preserved unrelated wave-07 changes.
Read extracted atlas pages **109–156** completely (chapters 17–24, 48 pages)
and **349–366** completely (chapters 57–59, 18 pages): **66 source pages**.
Re-read pages 148–153 and 357–358 separately after larger output was truncated.
Used relevant prior review-note excerpts for navigation; no new visual-PDF or
external factory-source verification is claimed.

## Deliverable

- Prioritized technician-qualified external pilot, dry 91-source/1,098-route
  screening, drawbars/coherence, nine contacts, shared percussion and expression;
  presets/pedals and downstream scanner/AO-28/122/147 remain staged gates.
- Minimum specimen/revision/configuration/rights lock; concrete filenames, owners,
  setup checklist and v1 field mappings; no new schema keys or fabricated assets.
- Separates unloaded pickup, loaded source, G-G, voltage/current and pressure;
  digital header rate versus independently calibrated physical clock; scalar scale
  versus chain response/loading/synchronization and uncertainty.
- Distinguishes retained uncalibrated raw data, quarantine and physical-fit
  admission. A valid v1 role/manifest does not admit fitting.
- Requires whole-take/channel/rotor-run/derivative grouping, cross-manifest audit,
  distinct development-validation/final-test purposes, frozen final holdout and
  actual restore evidence; explains v1's limits and a dependency/pass-evidence queue.
- Communicated with Agent40; current contract fields, roles and bounds were
  confirmed stable. Detailed unsupported records remain support evidence/review.

## Checks and limitations

Executed `python tools/validate_capture.py --input data/capture-planned-example.json`:
structural pass; authenticity/calibration/fidelity remain `not_established`.
Parsed both documentation JSON fragments and inserted them into an in-memory
planned record with a proposed G-G channel; current `validate_capture` accepted
it with null timestamp and no files. No example hardware file was serialized.
Targeted Python checks passed: UTF-8 reads, no trailing whitespace, all 10 local
Markdown links resolve and this note is under 80 lines. Compared all cited v1
field/enum/unit/limit names with the contract; no additional schema keys proposed.
Both new-file `git diff --no-index --check` invocations emitted no whitespace
diagnostics; their difference status is not a test failure. Final scope inspection
confirmed the assignment's additions are only the two owned Markdown files.
No code, shared status files, raw captures, permissions or measurements created.
No physical, circuit, audio, host or platform test is performed by this assignment.
No dependency change, commit, push or child-agent delegation.
Root owns integration, shared handoff updates and publication.
