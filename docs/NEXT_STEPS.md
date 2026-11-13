# Next steps

## Resume here

Read [STATUS.md](STATUS.md), [PEDAL_HANDOFF.md](PEDAL_HANDOFF.md),
[RELEASE_READINESS.md](RELEASE_READINESS.md), [PLAN.md](PLAN.md) and
[AGENTS.md](../AGENTS.md), then inspect the actual checkout and remote head.
The implemented prototype is a nominal two-manual/25-pedal dry organ and optional
headless VST3 with 45 controls. It is ready for the dependency-ready scanner
numerical work below; physical M3 and the complete product remain open.

The sixty-worker pedal/native session is complete: **60 distinct new assignments,
ten waves of six, all accepted**, with one substantive note per worker. Its
[manifest](development/2026-11-13-pedals/assignments.json) retains those identities;
earlier original/console sessions are never recounted. Code/test repair
`0ad7240a88803de9d97bc265a8fd2b6e5d5d7e2b` is published with exact fetched tree
identity and all four core/three native jobs passed. Final handoff publication
changes only documentation and this session's completion metadata. A future
agent begins the product task below in a new, honestly scoped assignment record.

## First next product change: admit the scanner graph

**Deliverable:** an explicitly reconstructed nominal scanner fixture, strict
schema/compiler and an independently owned endpoint/source review. The detailed
acceptance authority is [M3_REMAINING_AND_SCANNER_GATE.md](M3_REMAINING_AND_SCANNER_GATE.md),
with the concise task in [release readiness](RELEASE_READINESS.md#first-next-product-task-scanner-graph-admission).
Do not infer original missing companion files from a newly authored replacement.

| Proposed file | Responsibility |
| --- | --- |
| `data/scanner/atlas-late-b3-nominal-v1.json` | Named topology, positive nominal R/L/C values, units, signed endpoints, outputs, source locators and explicit assumptions/unknowns. |
| `data/scanner-line.schema.json` | Strict bounded authoring contract; exact required fields and graph identities. |
| `tools/compile_scanner_line.py` | Deterministic, build-time admission and representation with destination preservation on rejection. |
| `tests/test_scanner_line_profile.py` | Independent literal endpoint/output expectations and meaningful malformed/topology mutation cases. |
| A separately owned source-review note | Actual page images and endpoint/value comparison, primary circuit comparison when available, exact evidence class and unresolved specimen applicability. |

Use the unchanged atlas, especially pages 157–159, 175 and 181–186, and the
[independent final source review](reviews/PEDAL_SOURCE_PLAN_FINAL.md).
Proposed model identity is `atlas-late-b3-nominal-line-v1`. Its source is a
candidate documentary reconstruction, not an acquired/calibrated circuit.

Acceptance for the first commit:

1. Preserve ground `g`, `p0..p18`, return `r` and `d1..d6`: **27 nodes,
   18 inductors, 18 capacitors and 14 resistors**. Ideal drive and return switch
   are explicit separate boundaries. Early divider branches attach before
   their inductors. Export exactly 19 ground-referenced signed taps.
2. Convert declared units once and preserve printed values/source locators.
   Treat the vibrato return short as a constraint/contraction. Winding resistance,
   mutual/stray coupling, drive/receiver loading and physical signal scaling
   remain explicit unknowns or named ideal approximations, never invented data.
3. Independently compare every endpoint/output/value/return state against the
   rendered atlas and an identified primary circuit when available. Preserve the
   missing primary/specimen gate if it cannot yet be closed.
4. Reject duplicate IDs/keys, dangling or missing references, unknown fields,
   nonfinite/nonpositive values, wrong units/counts, after-inductor divider
   mutations, return-referenced outputs and missing/wrong switch states. Bound
   source size and graph dimensions; failed writes preserve existing output.
5. Run meaningful compiler/source gates from coherent identified inputs.
   Preserve the original PDF/profile/maps/fixtures, all 45 parameter records,
   state migrations and Engine/native compiled inputs. Keep graph admission
   separate from scanner runtime and measured response acceptance.

## Dependency order after graph admission

| Step | Required work and evidence |
| --- | --- |
| Independent offline AC/transient oracle | Independently stamp both return states and all 19 signed outputs. Check exact-rational DC, finite-frequency topology mutations, loading/current sensitivity, conditioning/residuals and a converged transient reference. Freeze frequency grids and error budgets before grading runtime. |
| Prepared line runtime | A separately implemented bounded solver with physical capacitor/inductor state and prepared operators. Compare AC with declared frequency-warp treatment, transients, nonzero stored energy, partitions, all supported rates and stopped-rate state conversion. |
| Rotor and modes | One continuing phase/history, three depth maps and V1–V3/C1–C3 behavior. Resolve or explicitly label the atlas's 15-entry/16-position traversal discrepancy. Check signed common return, centers/intervals/wrap, sidebands and convergence. |
| Opt-in Engine/native integration | Define U/L/P/Q boundaries while preserving literal legacy dry accumulation when disabled. Preserve controls/state/UUID meanings, source clock and whole-callback rollback including precharged scanner state. Qualify newly enabled automation, allocation/concurrency and actual native paths. |

The independent DC solve establishes mathematical answers for the ideal graph;
it does not establish correct finite-frequency connectivity. A deliberately
misattached divider variant gives the same DC answers because inductors short
at DC. Keep independent source and AC checks in the exit criteria.

Do not add scanner parameters during graph/oracle work. When later integration
needs controls, specify stable identities and saved-state migrations first;
older states must retain the existing dry default.

## Work that can proceed independently

Physical M3 tasks include preset-latch/loading behavior, continuous drawbar
conductance, switching bandwidth, loaded expression and the pedal reactor
network. The present pedal mixtures and gain are named nominal fixtures;
documentary 25-by-8 wiring is not a measured 16-foot/8-foot voice model.

For acquisition, follow [CAPTURE_PROTOCOL.md](CAPTURE_PROTOCOL.md): identify the
organ/generator/AO-28/cabinet revision and condition; record calibration, units,
loading, physical clocks, uncertainty and permissions; retain raw/derived ancestry;
and keep complete takes/channels together across fitting, validation and untouched
holdouts. Metadata validation alone cannot admit physical fidelity.

M5 connected AO-28 precedes complete dry-organ validation; M6 selects a specific
Leslie 122 circuit/driver load while preserving 147 as a separate variant. M7
rotor/acoustic ownership must avoid counting propagation, filters and room effects
twice. M8 requires measured held-out evidence. M9 DAW/device operation, standalone
backend, accessible custom UI, runtime packaging, Windows icon/branding decision, project-license
choice and signing each retain distinct gates in [release readiness](RELEASE_READINESS.md).

## Required verification and handoff

Use the [operational commands](PEDAL_HANDOFF.md), configure/build the selected
inputs before CTest, and use `--no-tests=error` on a required filtered gate.
The completed session passed these exact record gates; use them to validate its
retained archive:

```sh
python3 tools/check_repository.py --root . --expected-agents 60
python3 tools/check_continuation.py --root . --expected-complete 60
python3 tools/check_pedal_session.py --repo . --expected-complete 60
```

The first two preserve earlier histories; only the final command checks the
pedal session. Record validation is not evidence of external dispatch or semantic
acceptance, which the integrator must verify separately. A later session needs
its own actual ledger and must not rewrite these completed identities.

Every future agent updates status, next steps, development log and affected
contracts with source identity, commands, results, actual failures and unrun gates.
Workers hand owned changes to the integrator. Commit and push completed authorized
work to main, inspect/integrate concurrent changes, use an expected-head guard,
never force-push and verify the fetched remote tree. No extra permission request
is needed for this standing authorized workflow unless repository protection or
a later user instruction changes it.
