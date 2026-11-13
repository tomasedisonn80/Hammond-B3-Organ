# Agent 20 — proposed internal parameter registry

## Assignment and sources

Owned only `data/parameter-registry.json`, `tools/validate_parameters.py`,
`tests/test_parameters.py`, `docs/PARAMETERS.md`, and this note. Read `AGENTS.md`,
README, status/next steps/plan/log, atlas review and note05, console extension,
`ControlState.h`, existing types/renderer/profile contracts. Extracted and read
atlas PDF pp.397–402 directly. Inspected `main` and the shared dirty tree;
preserved unrelated work. No commits, pushes or subagent assignments.

## Delivered scope

- Original **proposed** schema1 / `ideal-exclusive-ab-console-v1` registry for
  `implemented-console-subset`: exactly36 permanent manual/bank drawbars,
  one global expression and two A/B selectors (39 total).
- IDs: upper A4096–4104, upper B4112–4120, lower A4128–4136,
  lower B4144–4152; expression8192; selectors8208/8209. Drawbars default0,
  expression1, selectorsB(1). Every record has units, domains, steps,
  conversion, target and proposed evidence/page locators.
- Fixed bank targets flatten `bank * 9 + drawbar` to0–17; no selected-bank
  alias. Cancel remains a route action; complete snapshots also need route bits.
- Strict stdlib loader rejects duplicate JSON keys, unknown fields, bad
  versions/models/scopes, identity/target collisions, nonfinite domains,
  wrong defaults and amplitude substitutions. Bounded input is256 KiB.
- Scalar helpers map normalized values to untimed event dictionaries and
  canonical values, reject invalid input, and never dispatch into Engine.
  Exact integer-ratio half-up rounding protects adjacent-float thresholds.
- Documentation distinguishes internal integer drawbars/half-up law from
  atlas p.398 continuous travel and its different host discrete conversion.
  Expression retains the explicitly named linear-gain surrogate.

## Executed evidence

`python3 tools/validate_parameters.py` — passed:39 proposed internal records.
`python3 tests/test_parameters.py -v` — **19 tests passed**, covering all IDs,
banks/targets/defaults; collisions and strict metadata; parser/CLI failures;
nonfinite/bool/range rejection; normalized round trips and all half-step
thresholds plus adjacent floats; permanent targets and position-not-amplitude.
Inspected all bank-range endpoints; all five files have final LF and no trailing
whitespace. Registry SHA-256:
`e7a7a9938ff38fbd43cb18aa9a7da482628cb41550d56fd37f9c1d3216547e8e`.

No C++/Types/Engine code changed. These results establish metadata and scalar
conversion only. They do not exercise native host curves, exported VST3 IDs,
actual engine event dispatch, UI gestures or physical fidelity. The62-entry
atlas companion remains absent; no recovery or inherited test pass is claimed.
Integrator owns shared status/next steps/log and build/test registration.
