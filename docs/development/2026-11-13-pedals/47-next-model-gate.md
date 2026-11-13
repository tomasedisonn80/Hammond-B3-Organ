Owner: /root/w08_a47_next_model_gate

# Assignment 47: remaining M3 and a concrete scanner implementation gate

Wave: 8. Assignment: 47 of the current sixty-assignment pedal/native session.
Scope: inspect actual atlas pages/figures and current interfaces, then prepare a
dependency-ready M3/M4 implementation and acquisition contract. Only this note and
[M3_REMAINING_AND_SCANNER_GATE.md](../../M3_REMAINING_AND_SCANNER_GATE.md) are owned.
No source, schema, profile, shared handoff, manifest or historical ledger is edited.

## Sources actually reopened

Read `AGENTS.md`, the complete `docs/PLAN.md`, current status/next steps, README,
the preceding console handoff and latest development-log checkpoint. Revisited
the complete [atlas review](../../research/ATLAS_REVIEW.md) and
[errata](../../research/ERRATA.md), assignment 02's complete console review and
the source/frame, routing and numerical sections of assignment 03. Historical
unimplemented-pedal statements were interpreted against current source rather
than copied into the new plan.

Freshly read the full extracted text of **66 atlas pages**: 109-126 (18),
139-150 (12) and 157-192 (36). These cover the complete drawbar, contact, preset,
pedal, expression and six scanner chapters. The source was the unchanged
[500-page PDF](../../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf),
21,248,265 bytes, SHA-256
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
One-based PDF and printed page numbers agree. Text came from the root's retained
`pdftotext -layout` extraction, selected by form-feed pages; it has no artificial
`=== PDF PAGE` delimiters. The selected groups were read without truncation.

Rendered and visually inspected **eleven actual pages** at maximum dimension
1800 pixels: **110, 112, 116, 122, 142, 146, 158, 166, 170, 171 and 182**.
All eleven Poppler operations exited zero. The actual page-158 circuit diagram
was especially useful: it fixes the early divider before `Lk`, capacitor after
`Lk`, shared return, termination and nineteen ground-referenced outputs. It
supports an explicit candidate endpoint table, rather than a guess based on
serial prose. The p. 171 arrows remain an explanatory responsibility diagram;
the p. 182 patent plate is a historical embodiment. The p. 146 photograph is
explicitly excluded from geometry evidence by its caption.

This is a focused fresh 66-page review with selected visual checks, not another
claim to have reread all 500 pages or independently verified every cited external
source. No primary-paper or production-drawing retrieval was performed here.
Those independent comparisons are explicit next-ticket gates.

## Actual current-code inspection

Inspected `Engine::process()` and `rebuild_coefficients()`, control and contact
headers, pedal voice constants, source-profile and registry declarations, source
inventory, the control-state contract, M3 acceptance contract, capture format and
the protocol's downstream/holdout/admission limits. The first source-identity
observation occurred during root's checkpoint publication: local HEAD was
`33d0326ea20dc6a80b9096079e5e61b9ac3193af`, while the observed local remote ref was
still `9403debd754f771bf39bc8cd771ecfd86c0f14d6`. I did not fetch, change branches,
stage files or interfere with publication. The inspected relevant bytes were:

| File | SHA-256 |
| --- | --- |
| `src/Engine.cpp` | `e082d07323c506f58c726c76a8459bbbec9b01fcb7b20ca6d6323c065fa6664c` |
| `include/hammond/ControlState.h` | `2fb1b7b7fc39363f7e53eb81e2edf3ddb88944b4aa20969b92a90f5c584b2edb` |
| `include/hammond/ContactBank.h` | `a083dcd65d989cc5be78a393fad74f40cbb530e33f89492d523e406f477be99d` |
| `include/hammond/PedalVoice.h` | `694961946eac838c689547fc403c84e49a429f3337816ea9ad3a751bf305ddaf` |
| `data/profile.schema.json` | `064beb58d186bb9ace5b2271c00c1b6f7d06c5ef43a403b6319344d92c1057af` |
| `data/profiles/nominal-unmeasured-v1.json` | `d17a266ed97cbbd3a2925ebebafafbd6c0e3f84763635732e0a9351d0eab2bff` |
| `data/parameter-registry.json` | `a80b0f391a37dd9264dc6962131e61c6ba8a0b8ce570d15e89042abe13d148c4` |
| `data/capture.schema.json` | `2e33ff19c23b2c82d593073f6d24bd29889531c62acd2d8fcf08ec48c0ae7860` |

The tracked `*scanner*` / `*Scanner*` file search returned no scanner files. The
profile still declares scanner not modeled. A preliminary file enumeration
included the nonexistent directory `core`, which produced an `rg` diagnostic;
subsequent actual source reads used `src` and `include`. No conclusion relies on
the failed directory operand. No source or test was changed to satisfy the plan.

## Decisions recorded in the deliverable

1. Select data/topology admission plus an independent AC oracle as the next
   numerical commit. Do not start by adding an unqualified generic delay chorus
   to the existing native product.
2. Preserve the present dry accumulation order: upper/lower sustained coefficients
   already collapse into one array. New U/L/P/Q diagnostics and scanner routing
   need a deliberate compatibility path, not an assumed exact reassociation.
3. Specify all candidate nominal endpoint patterns and values from the actual
   atlas diagram: 18 L, 18 C, 14 R, 27 pre-contraction named nodes, nineteen
   ground-referenced outputs and separate drive/return switch.
4. Retain the E01 fifteen-entry mismatch and inferred trailing `1` explicitly;
   the same-depth V/C maps, one rotor phase and return voltage counted once are
   separate falsifiable requirements.
5. Provide independent rational DC known answers, signed descriptor equations,
   mutation tests, proposed residual/complex-error targets, transient convergence,
   physical-state migration, bounded runtime and enabled-native acceptance.
6. Keep fixed-preset/multi-latch, continuous drawbar, fractional switching,
   expression and pedal-reactor work visible as separate M3 tasks. Existing
   physical gaps cannot become zeros, copied patent values or invented captures.
7. Specify capture quantities, units, ancestry and holdout gates using the existing
   schema; no unofficial keys or new manufactured planned/recorded evidence.

## Commands and observed arithmetic

The visual workflow executed the following pattern for each listed page, then
opened every generated PNG for inspection:

```sh
pdftoppm -f 158 -l 158 -scale-to 1800 -singlefile -png \
  Hammond_B3_Leslie_Research_Atlas_500pp.pdf \
  /workspace/scratch/f364bc93d920/a47-next-model/page-158
```

Read-only Python `hashlib.sha256` checks produced the source identities above.
`git rev-parse HEAD`, `git rev-parse origin/main`, `git status --short` and
`git ls-files '*scanner*' '*Scanner*'` established the observed working context.
Shared dirty files belonged to other workers and were preserved.

An original Python `fractions.Fraction` calculation used exactly these six
divider pairs in ohms:

```python
from fractions import Fraction

pairs = [(27000, 68000), (56000, 150000), (39000, 150000),
         (33000, 180000), (18000, 180000), (12000, 180000)]
R_parallel = 1 / (sum(Fraction(1, a+b) for a, b in pairs)
                  + Fraction(1, 15000))
r = Fraction(22000) / (R_parallel + 22000)
vibrato = [Fraction(b, a+b) for a, b in pairs]
chorus = [r + (1-r)*Fraction(b, a+b) for a, b in pairs]
```

Observed `R_parallel = 9775.932618884532` ohms and
`r/V_in = 0.6923478931008726`; all twelve first-six-tap ratios appear in the
deliverable. Python `math` independently recomputed the ideal-section units
checks: `sqrt(0.5*4e-9) = 4.4721359549995795e-05` seconds,
`sqrt(0.5/4e-9) = 11180.339887498947` ohms,
`1/(pi*sqrt(0.5*4e-9)) = 7117.62543417177` Hz. These are arithmetic checks of
explicit nominal assumptions; no circuit solve or measured response is claimed.

Counting the printed and inferred traversal yielded 15 and 16 entries. In the
inferred cycle the endpoint counts are one each, the seven intermediate counts
are two each, and all sixteen cyclic neighboring index differences are one.
`412/60` yielded `6.866666666666666` Hz. Counting passives yielded 50 and the
chosen pre-contraction node naming yielded 27. These checks establish internal
consistency, not independent factory wiring.

## Validation, limits and handoff

The two-file inspection found **30 resolving relative Markdown links** (26 in
the gate, four in this note), valid UTF-8, LF-only text, final newlines, no NULs
and no trailing whitespace. A final recheck confirmed all nine inspected source
identities, including the PDF, unchanged. At that observation root's local and
remote-tracking HEAD both equaled `7fb9b6121b729f46a9e18d80e8620eb21dc0847b`;
this is an observed identity, not a CI claim. No C++, DSP, real-time, scanner,
SPICE, hardware, plugin-host or cross-platform test was executed for this
documentation-only assignment.
No library, SDK, dependency, capture, production data or user setting was added.
No commit or push was made; root owns those actions and the shared status.

The next worker should take the first ticket in the gate: declare ownership of
the new scanner authoring data/compiler/tests and independently source-review
the reconstructed endpoint graph before runtime integration. Root may assign
fixed-preset data/latch work in parallel with separate file ownership. The
completed nominal pedal/native session does not establish complete M3, M4 or
specimen fidelity.
