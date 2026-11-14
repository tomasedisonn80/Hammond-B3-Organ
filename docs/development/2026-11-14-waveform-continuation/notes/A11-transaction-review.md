# A11 — Independent transaction and lifecycle review

## Actual assignment and source

- Worker: `/root/w02_a11_transaction_review`; wave 2; 14 November 2026.
- Workspace: `/workspace/scratch/e3cacb90cc81/Hammond-B3-Organ`.
- Observed HEAD and origin/main: `26ff2fbe66a50260bd7601cbfa54c1f5d35ff3a8`;
  observed HEAD tree: `530d5fcf777003f470f64558de9e5631d31a21a4`.
- Read standing agent instructions, the new scope/checkpoint/actual manifest,
  complete M0–M9 plan, current status/next-step pointers, complete frozen
  numerical and candidate renderer contracts, public history/renderer/motion
  declarations, motion lifecycle implementation, A04/A07 source/design notes,
  and the existing portable allocation-detector implementation.
- Owned `docs/reviews/WAVEFORM_TRANSACTION_REVIEW.md` and this note. The
  integrator subsequently authorized a narrow amendment to the private-test
  seam paragraph of `docs/ROTARY_RENDERER_CONTRACT.md`. No other contract
  paragraph, product/header/CMake/shared-record file or existing test changed.
  No nested agents, builds or commits were created.

## Decision and communication

**Accept the proposed public API and transaction design for implementation.**
No public signature blocker was found. The review records exact requirements
for admission precedence, legal overlap, event lifetime, zero/end-boundary
ordering, per-overwrite reverse journaling, partial writes, publication,
original reset seeds, stopped allocation failure and bounded process work.
This is source/design acceptance, not an executed renderer or runtime pass.

Reported one concrete testability gap to the integrator before renderer
implementation: a deliberately corrupted pre-call retained slot is overwritten
within one ring cycle, so it cannot prove a late rejection after multiple
complete wraps. The integrator accepted using the **existing** private friend
to shorten only the second motion ring's append limit. The contract paragraph
now explicitly permits that test, requires preservation of the injected
pre-state until restoration, and retains the separate late support-failure
fixture. No production failure hook or new public API was added.

Coordinated a signed-zero concern with A10. That reviewer checked the existing
motion zero-time branches and found they return the original initial/boundary
state deterministically; no defect was claimed. Both reviews retain the need
for field-level bit comparisons instead of default floating equality when
grading bit identity.

## Independent experiment design

[The review](../../../reviews/WAVEFORM_TRANSACTION_REVIEW.md) gives implementation-
ready A20/A29 recipes. For a stationary point at `3/128` m with `Fs=48000` and
`c=300`, the independent arithmetic gives delay `3.75` frames, `D=4`, `H=10`.
At pre-call frame 40, a poison at absolute waveform frame 39 first enters the
four supports at input frame 43, after three complete samples. A second motion
ring limit of 63 allows 23 complete appends before a 37-frame call fails after
24 live undo records. Slots 0–3 occur three times and slots 4–9 twice.

The late tests compare full physical slot/metadata snapshots, caller sentinel
bytes, copied state and diagnostics; they then remove only the injected fault
and compare accepted continuation with an untouched control. The allocation
plan separately calibrates real C++ interposition, observes accepted/early/late
process calls, and forces stopped prepare/rate-replacement failure on a working
nonzero-history renderer. All sixteen rate pairs and reset-after-replacement
original seeds are explicit requirements. No test copies the production rollback
algorithm as its expected-value oracle.

## Actual checks and inspected identities

No configure, compiler, shared build, CTest, sanitizer, allocation probe or
renderer process was run. The only calculation was Python 3 standard-library
arithmetic for the fixture above, with `math.ceil` and `collections.Counter`;
it confirmed the delay/capacity, first poisoned support and repeated slot counts.
Read-only `git status --short` and `git rev-parse` established the source above.
Formatting and exact hashes were checked with `Path.read_bytes()`, final-LF /
trailing-whitespace assertions and `hashlib.sha256`, from the workspace root.

| Inspected file | SHA-256 |
| --- | --- |
| `docs/ROTARY_NUMERICAL_CONTRACT.md` | `4c060088f0718586a7c6810e5c055c652d8924db4474db770237193ab459bd63` |
| `include/hammond/RotaryHistory.h` | `9e6930342a5c83bdcf99102aaeb0dc9b0714e85561bd8205a53155a7fca4a25b` |
| `include/hammond/RotaryRenderer.h` | `5f74af0a7ca629b433fe7f3d72a44a2b39daf90fd2d64afa579aecd26f48ccd0` |
| `src/RotaryMotion.cpp` | `a3f986892078254f6dfae936bbbf1b5e1c4967882d06c13b3b28649f2273cfa1` |

The renderer contract is concurrently owned by the integrator/reviewers; its
hash immediately after A11's authorized seam amendment was
`6e1556a481effbc01ce599249ad69dc0402d879516d2f495273c863ea1f84ebf`.
That identifies an observed worktree file, not a claimed final frozen revision.
The original A07 candidate hash remains in A07's own unchanged note.

Next: the integrator freezes the reviewed API; implementation owners preserve
these transaction/lifecycle rules; A20/A29 execute the independent experiments
on coherent source and retain actual late-progress and allocation evidence.
The prior 155-test baseline predates this API. R5, real-time/device/host R6 and
physical fidelity remain unqualified by A11.
