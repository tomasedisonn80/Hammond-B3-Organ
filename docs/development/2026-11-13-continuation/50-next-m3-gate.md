# Assignment 50 — next dependency-ready M3 gate

- Agent: `/root/w09_a50_next_m3_gate`.
- Continuation wave 09, assignment 50 of 60; 2026-11-13 UTC.
- Scope: new [M3_NEXT_GATE.md](../../M3_NEXT_GATE.md) and this evidence note only.
- Review began against the published `9a5c99a` interfaces; the shared checkout
  reached `2046b9388f6aab1122e37646b2f20199b5c6079f` during review. This was a
  documentation/data review of the working tree, not an isolated binary test.

## Decision and concrete next action

The next slice is a prepared, fixed-storage pedal routing kernel that consumes
the same 91-source frame as the manuals and returns four normalized bus
excitations. The proposed identity is `linear-pedal-bus-reference-v1`. Its first
reviewable step is a typed pedal-runtime contract and executable admission test
for the complete existing 25-by-8 map. Then implement separate contact states,
caller-supplied dimensionless reference weights, a bounded scalar sum and
independent CSV/phase/coherence/failure checks.

This is useful implementation work without inventing pedal mixture coefficients,
reactor values or controller octaves. It does not supply two playable drawbars or
claim a physical pedal voice. The plan separately defines their following
Engine/control/ownership integration gate and the later physical admission gate.
The operational-handoff author, assignment 51, and the integrator received this
scope before publication.

## Sources actually inspected

Read `AGENTS.md`, README, the current status and next steps, latest development
log entries, project plan, consolidated
atlas review and errata, pedal routing and factory-reference contracts,
`M3_ACCEPTANCE_CONTRACT.md`, the saved-control/parameter contracts and retained
continuation review 06. Read the relevant findings and remaining-boundary
sections of continuation review 02; did not recount those agents' full page
coverage as this assignment's reading. Reviewed the assignment 48 legacy-audio
note to preserve the existing compatibility boundary.

Inspected the actual pedal JSON and both complete pedal CSVs; the factory
comparison manifest and its interpretation are documented in
[FACTORY_REFERENCE.md](../../FACTORY_REFERENCE.md). Inspected current
`Types.h`, `Profile.h`, `TonewheelBank.h`, `Engine.h`, `ControlState.h`,
`NoteOwnership.h`, `ParameterBridge.h`, `ControlStateIO.h`, the current
`Engine::process` and coefficient rebuilding paths, profile validation,
`validate_pedal_map.py` and CMake's generated-data/test integration. In particular,
the Engine advances one shared source frame before summing the current manual
and percussion contributions; its existing event/ownership destinations are
manual-only, and its saved controls contain no pedal fields.

Read these **40 complete extracted atlas pages** directly, including every page
used by the plan: **109–126, 139–150, 445–450, 465, 484–485 and 488**. They cover
drawbar/network boundaries, switching and contact references, presets, pedals,
expression, ordered milestones, scanner corrections and physical/product gates.
The page files were the existing individually numbered text extractions in
`atlas-review/page-NNN.txt` outside the repository. No page range was inferred
from titles alone. This assignment did not reread all 500 pages or render figures;
the retained full-range reviewers' separate visual checks remain their evidence.

The cloud environment runtime skill was read. Its advertised environment-status
tool was unavailable in this worker; local execution and repository paths were
observed directly. No environment configuration or dependencies were changed.

## Findings that determine the task boundary

1. **Documentary identities are ready.** All 200 pedal positions agree with the
   retained independent transcriptions. The five blanks are pedal IDs 8–12,
   second contact column (`c2`, zero-based column 1). The first seven pedals have
   repeated source numbers on distinct Brown/Red branches. None may be deduplicated
   before its connection state and bus membership are evaluated.
2. **Physical weights remain missing.** Bus-color membership comes from atlas
   p. 140; the source-number comparison does not establish conductor color,
   contact timing, impedance or a four-to-two transfer. Pages 141–144 retain
   unknown low-wheel spectra, reactor/contact/load values and explicitly permit
   a linear routing fixture. Normalized test coefficients therefore have a useful
   but limited role. They are not default factory parameters.
3. **Compatibility has existing owners.** Keep `Manual` at Upper/Lower, existing
   events 0–9, all 43 current internal control IDs, `B3PROFILE1` and old musical
   snapshot meanings. First-kernel processing needs no host mapping or new saved
   format. Actual pedal integration needs those decisions explicitly; source
   pitch identity cannot establish the missing pedal MIDI convention.
4. **The physical network remains a later dependency.** Pages 121–126 prevent
   treating multiple preset latches as summed registrations; pp. 145–150/488
   prevent treating arbitrary expression EQ as a solved AO-28. These limits do
   not block the selected independent routing work or a declared nominal model.

## Checks actually executed

Commands ran from the repository root:

```sh
python tools/validate_pedal_map.py --input data/pedal-map.json
python tools/validate_factory_reference.py
```

The first reported 25 pedals, 200 positions, 195 connected and five disconnected.
The second returned `status: exact-match`, zero A/B and target mismatches for
both manual and pedal comparisons, and `original_authoring_provenance_changed:
false`. It reported `source_pdf_check: not-checked; source PDF not supplied`.
This is verification of the retained comparison inputs, not independent
reacquisition or visual inspection of the external factory manual.

Python `hashlib.sha256` independently recomputed these actual local bytes:

| Input | Size, bytes | SHA-256 |
| --- | --- | --- |
| Preserved 500-page atlas | 21,248,265 | `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769` |
| `data/pedal-map.json` | 3,267 | `58a30850c08933a075cfcec04faeb2cb479f60bd9dda82ace3246552221623bd` |
| Each retained pedal CSV | 677 | `b8177479a5af16f4e6b8759313d90148a1213657c83f8a6e6533422bfa104ca1` |

The factory validator also reproduced canonical pedal-map digest
`7b2631a0c7d55a18f8225d4ee420e472c23b9f2809eec69865474eafce6f5fb2`.
The original map's frozen historical provenance was not rewritten to incorporate
the later attestation. New runtime consumption must link both records.

The two new Markdown files were checked for existing relative-link targets and
trailing whitespace. No C++ build, runtime test suite, native host, callback
deadline, physical capture or acoustic comparison was executed by this
documentation assignment. Proposed future tests in the plan are not reported
as passes here.

## Handoff

Start the next engineering assignment with the contract/admission step in
[M3_NEXT_GATE.md](../../M3_NEXT_GATE.md), then implement its kernel and focused
acceptance checks. After that gate, implement the separately specified playable
pedal contract without silently changing old controls or source ownership.
Keep remaining preset, drawbar, switching and expression gates visible.

Only the two assigned documentation files were created. No shared status/index,
code, data, source PDF, commit or push was changed by this worker. The integrator
owns shared handoff links, verification and publication. No subagents were used.
M3 and physical fidelity remain incomplete.
