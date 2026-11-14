# A57 — Independent R4 implementation boundary review

Actual worker `/root/w10_a57_r4_plan_independent_review`, wave 10 of the
reference-refinement session. Owned paths are
[`ROTARY_RENDERER_IMPLEMENTATION_READINESS.md`](../../../reviews/ROTARY_RENDERER_IMPLEMENTATION_READINESS.md),
this note and `reports/A57-*`. Root owns acceptance, shared navigation, ledger,
git and publication. The concurrent waveform session owns actual R4 code.

## Source and review method

Inspected HEAD and local `origin/main` were
`0881d1f4c5a26ce9c75dda7a3adde46382e5ab6b`, tree
`f8144b771cda1264a8788f8297f5bfec999f4a08`. The worktree contained other workers'
documentation, workflow and evidence changes, which were preserved. Read the
complete AGENTS and M0–M9 plan, concurrent handoff, both session entries and
checkpoints, current status/next actions/log entry and retained atlas review
basis. Read A42's note and implementation plan, the concurrent owner's brief,
both frozen rotary contracts, all three native rotary headers and both native
implementations. The receipt records exact relevant hashes and comparison to
HEAD rather than treating that commit alone as the whole dirty worktree.

The review independently derived the widened-bracket support and flush bounds,
checked native event/segment and stopped-rate behavior, and traced the lifetime
and transaction requirements against actual declarations. A small Python 3.12.14
calculation in `/workspace/scratch/1bb6ee17ad7e` checked rational boundary cases,
binary64 maximum-bracket arithmetic, wrap counts and the sixteen ordered rate
pairs. Its retained source and results are
[reproducible evidence](../reports/A57-r4-boundary-proof.json), not simulated or
observed waveform output. No build, CTest, native probe, allocation workload,
sanitizer or audio experiment was run.

## Concrete findings

The capacity proof survives independent scrutiny: `0<delay_frames<D+1` gives
an oldest cubic tap no earlier than `n-D-4`, while a `D+6` ring retains from
`n-D-5`. The maximum remains 12,806 cells. A42's precise widening number is a
mathematical margin contribution; the new review supplies a conservative
rounding allowance for the actual capacity/endpoint operation order without
adding cells or changing numerical budgets. The absolute cubic-weight sum
derives to `1+mu*(1-mu)`, preserving the 1.25 bound and possible 1,250-unit
two-path output.

Four implementation preconditions are explicit. A geometry-only streaming
path must remain bound to compatible rotor/epoch/rate/profile metadata because
the native Mach admission depends on the actual epoch seed. Every immutable
borrow must end before the next write or rollback. Exact restoration must
include initialized cell representations, metadata and canonical scratch;
ordinary member-value copies alone must not be assumed to prove byte identity.
Flush ownership must distinguish ordinary per-call transactions from a
potential multi-call convenience operation.

The smallest admitted nine-cell ring can visit one slot 456 times during a
4,096-frame call, yet the per-write journal remains bounded by 8,192 entries.
Reverse replay restores repeated overwrites; unique-slot counting is not the
proposed algorithm. Dense command changes for both rotors require at most
512 frames per call under the 1,024-event bound, so this stress is separate
from the maximum-block partition fixture. The prescribed `D+4` flush includes
its final possibly nonzero cubic tail; the following frame is guaranteed to
have only zero support. All sixteen rate pairs include same-rate epoch changes,
and reset must still use the original preparation seed.

## Acceptance and limits

[The documentary receipt](../reports/A57-r4-plan-independent-review.json)
retains source identities, arithmetic scope, local-link/whitespace checks and
the substantive-note count. A42's history, the owner's brief, both frozen
contracts and all native sources were not modified. No R4 implementation,
native correctness, runtime bound observation or device deadline is claimed.

The next acceptance is the waveform owner's API resolution followed by the
full frozen polynomial/static-grid, ten-second all-rate same-cubic, partition,
history-seam, rejection, symmetry, lifecycle and allocation evidence. A private
failure seam must exercise real late rollback exits without expired storage or
relaxed limits. R5 audible policy, R6 integration, physical M7, M5/M6 and scanner
G5 remain separate. The nominal dry Engine, 47 parameters and state4/readers
1–3 remain unchanged. Root will link the accepted review from the current
handoff and handle publication.
