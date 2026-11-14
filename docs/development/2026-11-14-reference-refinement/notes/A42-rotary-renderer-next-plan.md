# A42 — Independent proposed R4 implementation review

Actual worker `/root/w07_a42_rotary_renderer_next_plan`, wave 7 of this
reference-refinement session. Owns
[`docs/ROTARY_RENDERER_IMPLEMENTATION_PLAN.md`](../../../ROTARY_RENDERER_IMPLEMENTATION_PLAN.md),
this note and `reports/A42-*`. No product, CMake, test, frozen contract,
shared status or other worker's file was changed. No build, dependency
acquisition, native/numerical test, commit or push was performed.

## Source and concurrent ownership

Read AGENTS/current scope/checkpoint/manifest, the complete M0–M9 plan, atlas
reviews, both complete frozen rotary contracts, all three native rotary headers,
both native implementations, A30's note and both runbooks. Existing R2/R3
primitives remain nominal and unconnected to Engine; R4 is not implemented or
accepted by this assignment.

Initial HEAD/origin was `f9c11a498ecd88886349415205fc5dccc627033e`, tree
`39ac16b12526143eee4136e4cc4a534b71013660`. Root subsequently integrated the
separate waveform-continuation documentation at
`26ff2fbe66a50260bd7601cbfa54c1f5d35ff3a8`, tree
`530d5fcf777003f470f64558de9e5631d31a21a4`. I read its renderer brief, scope
and checkpoint after integration and cross-linked the actual files. This
independent review supplies implementation input to that track; its workers,
code ownership and future results remain separate. A40/A41's pending UI work
and A39's checker are untouched. Local activity paused for A41's timing cells
until root released it; no duplicate experiment was run.

## Result and unresolved decisions

The plan recommends per-frame copies of original event-anchored segments with
separate rotor ownership. It explicitly rejects treating the 4,097-anchor
immutable R3 fixture view as mutable streaming storage. A new short-lived
window view and geometry-only streaming path need API review; no declaration
is presented as already available.

Derived capacities are 2,946/3,206/6,406/12,806 frames at the four supported
rates. The proof includes the solver's 32-ulp bracket margin: at worst
`7.275957614183426e-11` extra frames, still covered by the frozen `D+6` rule.
It separately proves latest/oldest cubic support and the `D+4` flush. The
proposed journal stores at most 8,192 overwritten rotor cells, including
repeated wraps within a single call; output scratch holds at most 8,192
doubles. All state, histories, caller audio, diagnostics and persistent scratch
are covered by rejection restoration.

The plan specifies two-input/four-path rendering, split positions, exact
two-frame latency, event ties/endpoints/zero calls, stopped reset/rate semantics,
source-identified independent tests and six narrow implementation packets.
API placement, copy/move policy, exact capacity reservation, span/status rules,
failure observations and private fault injection remain explicit review choices.
The full frozen all-rate ten-second comparison, 33,280-cell static grid,
partition identity, late-failure rollback and all 16 rate pairs are planned,
not executed. R5, R6, M5/M6, physical fidelity and scanner G5 remain separate.

## Executed documentary validation and next step

Working directory: `/workspace/scratch/1bb6ee17ad7e/Hammond-B3-Organ`.
Read-only inventory, `git rev-parse`, source diff/hash inspection, exact arithmetic,
local Markdown targets/fragments, word count and whitespace checks were run.
The reproducible source/link check is:

```sh
python3 docs/development/2026-11-14-reference-refinement/reports/A42-validate-plan.py
```

Its [JSON receipt](../reports/A42-rotary-renderer-plan.json) retains actual
results, commands and source identities. Both frozen contracts and all five
native rotary files match the initial published baseline. No runtime gate
is claimed by these checks. Next, the waveform owner reviews the proposed
streaming API and independent oracle boundary before assigning history,
solver-seam and renderer implementation. Root owns acceptance and publication.
