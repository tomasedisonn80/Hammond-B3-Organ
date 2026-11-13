# Assignment 09: freeze scanner numerical criteria

## Identity and owned result

- Session `2026-11-13-scanner`, wave 2, assignment 09 of 60.
- Worker `/root/w02_a09_scanner_numerical_contract`.
- Inspected baseline commit `6dc0702d5473912268e8af8f852b9b9984198ef3`,
  tree `a4f1d4b300de236436e22b748b1d4c46ed501ceb`; local `origin/main`
  identified the same commit at inspection.
- Owned files: [SCANNER_NUMERICAL_CONTRACT.md](../../SCANNER_NUMERICAL_CONTRACT.md)
  and this note only. Concurrent graph, oracle and integrator edits were preserved.
- Contract ID: `scanner-numerics-v1`, declared before this session's runtime
  implementation was graded. Its frozen SHA-256 at handoff is
  `3999a3a409d397401e135e8285704092bad130911468802370bf6da404d58ff9`.

I read the standing instructions and current project context, the existing
scanner gate, fresh atlas reviews 03/05/06, and directly extracted atlas
pp. 181-186. Those pages distinguish the graph, descriptor equations,
physical states, discrete model, independent comparisons and remaining
hardware evidence. This assignment does not claim another full-PDF reading or
a primary-paper/source-image review.

## Decisions made before grading

The contract separates graph admission (G1), reference qualification (G2),
discrete runtime agreement (G3), rotor semantics (G4), audible numerical policy
(G5), Engine/native integration (G6), and physical M4. This prevents a correct
base-rate bilinear recurrence from being presented as accurate at the same
physical frequency merely because a warp-aware comparison passes.

The fixed stationary grid is 282 positive bins plus exact DC, both electrical
returns and all nineteen signed taps. The proposed inherited complex parity
bound remains `1e-8 + 1e-6*abs(reference)` and solve residual remains at most
`1e-9`. Scaling, conditioning, output polarity, common return and source-current
conventions are explicit. Phase eligibility is fixed at magnitude `1e-4`;
excluded bins remain in the report. Graph mutations cover errors that DC alone
cannot reveal.

G5 is deliberately separate and prospective. Same-hertz complex error uses
`1e-3 + 1e-2*abs(reference)`. Independent transient refinement must converge
well inside the runtime waveform budget: reference RMS/maximum limits are
`2e-6/1e-5`, versus runtime `1e-3/1e-2`, with fixed voltage/current scales.
The margin prevents a visibly unconverged reference from grading the runtime.
These numerical choices are engineering targets, not measured perceptual or
physical tolerances. A failure keeps G5 open; later revisions cannot erase it.

The contract fixes clock/input endpoint semantics, physical capacitor/current
coordinates, previous input, replay-state ownership and continuing rotor
phase. It specifies precharged rejection/rollback tests, exact fixed-rate
partition checks, stopped-rate migration, return switching and source-power-
aware energy checks. The single rotor requires independent center/interval/
wrap tests and verifies that chorus common return is included once.

The rotating-output grid includes five carriers through 19001 Hz, all six
modes and three host rates, independent refinement and retained legitimate
sidebands. Any future output-rate filter needs its own passband, stopband,
latency and persistent-state evidence. Research solver rates through host
rate times 16 are not additional supported host rates.

The first grid/parity conventions were communicated to root and oracle worker
08 before that worker finalized implementation. Worker 08 confirmed the
282-bin grid, infinity-norm residual/condition convention, phase floor and
segmented group-delay diagnostics. The completed contract was then sent to
both workers. No C++ signatures or a final optimized numerical implementation
were invented by this documentation assignment.

## Actual checks and limits

Working directory: repository root at
`/workspace/scratch/1742da7072be/Hammond-B3-Organ`.

Executed reads included `cat AGENTS.md`, bounded `sed` reads of the named
contracts and fresh review notes, the README/status/next-step/plan/research
entry points, `tail` of the development log, and:

```sh
pdftotext -f 181 -l 186 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
git status --short
git rev-parse HEAD
git rev-parse 'HEAD^{tree}'
git rev-parse origin/main
git diff --check
sha256sum docs/SCANNER_NUMERICAL_CONTRACT.md
```

An in-memory Python check executed the contract's grid construction and
confirmed 282 finite positive frequencies, sorted endpoints 20/20000 Hz and
separate DC. Local Markdown targets and owned-file whitespace were checked.
The initial combined context read exceeded its display allowance; relevant
scanner and review passages were reread in smaller batches. All six directly
extracted scanner pages were visible and read.

This assignment executed no scanner solve, reference convergence experiment,
runtime/rotor test, benchmark, hardware measurement, host test, commit or push.
It declares criteria rather than their achievement. Root owns substantive
acceptance, shared status, publication and any later contract revision.

## Next dependency-ready action

Qualify the admitted graph and independent AC reference, then implement the
prepared physical-state line against this frozen contract. Publish results
per gate, preserving failed, inconclusive and unrun G5/G6 scopes. Keep all
existing 45 control identities and dry-engine behavior unchanged until a
separately qualified integration and migration task is completed.
