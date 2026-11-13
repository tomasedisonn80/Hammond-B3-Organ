# Assignment 20 — fixed policy implementation

**Actual assignment:** `/root/cal_w4_a20`, calibration wave 4, assignment 20.
This is one distinct newly dispatched producer assignment. It does not recount
the earlier metric author or the separate policy acceptance worker.

**Result:** implemented strict policy preflight and uncertainty-aware evaluation,
the companion shape schema, retained literal synthetic example and operating
guide. Author checks and the unchanged metric suite pass. Independent policy
acceptance and coherent publication remain separately owned by worker 21 and root.

## Ownership and source basis

Owned paths only:

- `tools/compare_capture.py`
- `docs/CAPTURE_POLICY.md`
- `data/capture-policy.schema.json`
- `data/capture-policy-synthetic-example.json`
- `docs/development/2026-11-13-calibration/20-policy-implementation.md`

Working directory was
`/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ`. Read `AGENTS.md`, the calibration
scope and handoff, current status/next-step/development-log context, the full
frozen comparison contract, accepted comparison implementation and common JSON
primitives. The inherited context retains the complete project plan and other
track ownership. Also read the extracted source text of atlas pp. **364** and
**484**, which distinguish declared shared corrections and uncertainty-aware
predeclared bounds from physical evidence. This assignment does not claim another
full-PDF reading or verification of the atlas's external references.

The initial local commit was
`0a4e0b156fdb8d08246a2fe2ed032cebbdee335a`, tree
`cfc2036c30ee627ed4a7c6137ffc928ea590b513`; locally recorded `origin/main` was
`5026f671e788eb5e1a77c8ed4046a34afd539200`. Root had frozen that accepted wave-3
source before this assignment could edit the live producer. Root subsequently
integrated a concurrent standalone advance; a later direct observation found
local `HEAD` `8864c051d19556e37dffcd7366fd859606958bc3`, tree
`e4f56a7c722dcad4eda9269d907715b8526dd8cd`, and locally recorded `origin/main`
`5b8e2419d23fe27c51709d717812060eafd44dcc`. This worker performed no Git mutation,
fetch or publication. The new implementation was uncommitted when checked, so
its complete file hash is the executed-code identity.

| Complete file bytes at producer handoff | SHA-256 |
| --- | --- |
| `tools/compare_capture.py` | `220a593499539db5f1e635db2eb15ba3c0aa7c6d001c80407fbffe93f75a9a0a` |
| `tools/capture_common.py`, unchanged | `e06dd82e37dd178863af61aa66bee877da1fc7e498a47b729e060215ca79c3f2` |
| Frozen comparison contract, unchanged | `4ec3037aa0588528fe3c9e520d099cc48a82d78135fc86bd3851c2667860750c` |
| `data/capture-policy.schema.json` | `2a1b0fd959f5f760d9460c7c960d48d7d4adbbd27918c9b4df6849646c8a9678` |
| `data/capture-policy-synthetic-example.json` | `e091dca3b3fdf3c3675383096007c5f95b848fa6294dedd3906705d061884316` |
| `docs/CAPTURE_POLICY.md` | `ea762fb1a65c99727fbcdf573ff47e86b004089d37d71ff72067f83e30c72a4c` |

No shared documentation, ledger, CMake, capture-v1 files, engine, other-track
sources or Git refs were modified. The earlier comparison-guide paragraph that
called policy implementation pending belongs to root's shared integration update;
this worker did not change that unowned file.

## Implemented behavior and reviewed composition

The module now exposes `parse_policy(policy_json: bytes) -> dict` and the frozen
`evaluate_policy(comparison, policy_json: bytes) -> dict`. The former is an additive
preflight helper approved by root after worker 19 identified the need to admit a
policy before scanning audio. It returns the freshly parsed policy unchanged and
performs all intrinsic shape, geometry, target and uncertainty checks. It does
not accept a synthetic placeholder comparison or issue a verdict.

Strict policy parsing reuses `capture_common.parse_json_bytes` with 65,536 bytes,
4,096 value nodes, depth 8 and numeric magnitude `1e6`, followed by policy text,
container, exact-field and semantic admission. It checks typed targets and units,
selected channel/frequency membership, unique criterion IDs/target triples,
ordered frequencies, combined work, freeze-evidence known/unknown shape and all
three uncertainty bases. The source bytes remain the policy identity.

`evaluate_policy` calls that helper, admits the complete comparison through the
existing report validator, and checks all six analysis fields. It retains every
criterion in policy order, including failures and inconclusive cases. Missing
metrics take precedence over missing uncertainty without discarding either
original reason. Known intervals use exactly `max(0, v-u)` and `v+u`, with no
rounding or hidden tolerance. A fail dominates the overall numerical verdict;
otherwise any inconclusive criterion dominates pass.

The complete comparison and each criterion's target, uncertainty and observed
metric are copied into independent returned containers. Physical fidelity and
preregistration remain `not_established`, even with a known freeze-evidence text
or a numerical pass. The evaluator performs no file/audio/network operation,
correction, fitting or external-state mutation.

Root highlighted a composition boundary: a structurally valid comparison metric
can be `2e18`, and adding a policy margin up to `1e6` can exceed the comparison's
numeric ceiling while remaining finite. The evaluator therefore does not apply
the comparison-only guard to its complete result. An explicit author probe retains
that larger finite interval and a failing verdict. Later wrappers must use their
separately declared envelope bounds.

All **20** pre-existing top-level functions/classes in `compare_capture.py` are
AST-identical to the frozen wave-3 commit; only module imports/constants/docstring
and the new policy implementation were added. No metric or report-admission
definition was adjusted to pass policy tests.

## Actual author verification

Environment: Linux, Python **3.12.14**, standard library for the implemented tools
and author numerical checks. A separate optional schema-authoring probe used the
already installed `jsonschema` **4.26.0**. That package is not imported by the
production module and is not a new runtime dependency.

Commands from the working directory above:

```sh
python3 -B /tmp/calibration-policy-a20-smoke.py
python3 -B tests/test_capture_comparison.py
git diff --check -- tools/compare_capture.py docs/CAPTURE_POLICY.md data/capture-policy.schema.json data/capture-policy-synthetic-example.json
sha256sum tools/compare_capture.py tools/capture_common.py docs/CAPTURE_COMPARISON_CONTRACT.md docs/CAPTURE_POLICY.md data/capture-policy.schema.json data/capture-policy-synthetic-example.json
```

The temporary author harness has SHA-256
`eed2e66bc96d6153ff078adba3518959a1f1aaea11dd986b352daf8f72e66f8b`.
It printed **`PASS 143 author policy assertions; Python 3.12.14`**, exit 0, on
both its initial and final execution. The retained metric suite passed
**42/42 methods**, zero skips; the final repeated run reported **0.372 seconds**.
The author assertions are not separately authored acceptance methods and are not
added to worker 21's independent count.

| Author probe area | Observed outcome |
| --- | --- |
| Four frozen binary-representable interval boundaries plus explicit synthetic zero | Exact endpoints, expected pass/fail/inconclusive verdicts and reason codes. |
| Unknown uncertainty at zero; undefined relative metric with unknown uncertainty | Inconclusive retained; metric absence has the required precedence and both source reasons remain. |
| Multi-criterion policy and margin monotonicity | Every criterion/order retained; fail dominates; widening margins across a 25-case grid never creates a pass from a nonpass. |
| Policy byte identity | SHA-256 equals independently hashed exact bytes; leading whitespace changes identity without changing evaluated rows. |
| Known freeze text and Unicode rationale | Intrinsic declaration admitted without changing `preregistration`. |
| Fresh parse results and evaluation copies | Mutating one result does not change another parse, caller report, or the separately retained observed/full-comparison branch. |
| Actual public parser composition | A wrapping spy observed one `parse_policy` call from `evaluate_policy`. |
| Finite interval beyond `2e18` | A hand-edited, structurally admitted normalized-error report with value `2e18` and margin `1e6` retains `2e18 + 1e6` and fails. This diagnostic is not claimed to have come from actual arrays. |
| Strict bytes/JSON and policy admission | Wrong byte container, BOM, invalid UTF-8, duplicate keys, nonfinite/overflow tokens, surrogate, excessive depth, unknown keys/types, invalid IDs/text/units/targets/uncertainty/analysis reject with `ComparisonError`. |
| Inclusive byte limit | Valid policy padded to 65,536 bytes admitted; 65,537 rejected. |
| Analysis match and spectral target types | Each of six mismatched analysis fields rejects; all three spectral target types grade literal sine/cosine coefficients against independent expected values. |
| Retained example | Frozen literal example parses and grades repeated arrays pass, with exact example-byte SHA and unchanged claim boundaries. |

The schema probe executed `Draft202012Validator.check_schema`, validated the
example, rejected **20** curated shape/branch/type/unit fixtures in both schema
and runtime, and admitted all **three** uncertainty branches in both. It also
verified the documented distinction that schema integer type admits `1.0` while
the runtime requires an integer token. This is a shape check, not a claim of full
semantic/schema equivalence.

A separate AST comparison against
`0a4e0b156fdb8d08246a2fe2ed032cebbdee335a:tools/compare_capture.py` confirmed
all 20 existing definitions unchanged. The guide's compact package-import example
was actually executed and serialized with `allow_nan=False`; it returned the
literal example hash recorded above. No author-check failure was observed.

## Remaining gates and handoff

APIs and the frozen producer hash were sent to root and worker 21 before final
handoff. Worker 21 owns independently authored strict-policy/report/decision tests;
root owns their acceptance, coherent-source integration and publication. The new
schema is a structural companion, with byte/token, bounded traversal, dynamic
cross-field membership and uniqueness/work rules explicitly delegated to runtime.

No native Windows/macOS execution, full maximum-work processing, corpus-to-policy
file workflow, source-audio replay, hosted CI, chronology verification or physical
calibration ran in this assignment. No acquisition, fitted model or hardware
fidelity result was created. Next compose these APIs into the reviewed file-job
contract, retain exact policy bytes and all corpus findings, and requalify the
accepted metric/report suite after any later implementation change.
