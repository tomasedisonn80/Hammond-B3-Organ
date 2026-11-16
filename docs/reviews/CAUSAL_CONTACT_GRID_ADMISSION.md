# Causal contact grid: independent contract admission

**A10, 15 November 2026 — admitted for isolated implementation.** Reviewed the
complete [contract](../CAUSAL_CONTACT_GRID_CONTRACT.md), SHA-256
`ba851e6af0601b52aef73d4b9effb64dffac3ef5e230eff7015e10e58a4ecb4e`,
against the complete current `AGENTS.md`, M0–M9 plan, current session scope and
the earlier streaming proposal/review. No contract edit or blocking question is
needed. This admits its explicit integer domain and API; it is not an
implementation, callback, audio, binary64-equivalence or physical-fidelity pass.

## Arithmetic and finite capacity

- Integer position evaluation uses unsigned directional subtraction, widens
  before multiplication and clamps displacement before addition/subtraction.
  With `T=2^28`, `S=2^32-1`, `Q=2^48`, `T*S=1152921504338411520 < 2^60`.
  Position and threshold differences stay at most Q.
- A future quotient can reach Q. Compute `a+h` in 64 bits: its conservative
  upper bound `T+Q=281475245146112 < 2^49` is safe. Check direction, target
  reachability and `(b,e]` eligibility before narrowing. For a concrete trap,
  use speed 1, `on=target=2^32+1`, `off=2^32`, and a command at zero. One
  processed frame has no edge; narrowing the future root first invents tick 1.
- Proper fraction numerators are at most `2^32-2`, denominators at most
  `2^32-1`. The maximum comparison product is
  `18446744060824649730 < 2^64`; it need not fit signed 64-bit arithmetic.
  Cast before multiplying. Reduced zero is exactly `0/1`; a root at T has
  zero fraction. A 32-bit Euclidean gcd needs at most 64 remainder steps by
  the stated every-two-steps halving bound. No extended integer type is needed.
- The command budget bounds **all** movements, including those already active
  at call entry. Each active key has consumed a prior command, so
  `A <= previousCommandCount` and `A+M <= 512`. Every monotone movement can
  produce at most nine edges; initial holds produce none. Consequently both
  `E_call <= 9*(A+M)` and `E_epoch <= 9*M_epoch <= 4608` hold. No-op and
  endpoint commands consume budget without invalidating this argument.

For interval batch sizes `n_i <= 9K`, ordinary insertion sort uses at most
`sum(n_i*(n_i-1)/2) <= floor((9K-1)*E/2)` edge comparisons. Multiply before
integer division in a bound calculation. The absolute maximum is 80,640,
not a whole-call sort of 4,608 edges. The other traversal bounds follow from
at most `M+1` command-delimited intervals; tied groups may reduce that count.
At most 4,096 positive calls and 512 processing commands give 165,888 contact
examinations across an epoch. Rejections/empty calls retain only per-call bounds.

The edge and sorting maxima are jointly attainable for the prescribed traversal:
configure four speed-1 keys; for flattened contact index `i=9*key+contact`, set
`off=1+i`, `on=100-i`. Supply four commands at each `tick=128*j`, for
`j=0..127`, alternating target 128 and zero. In one frame, the 512 commands
create 128 batches of 36 edges, or 4,608 edges. Each batch is reverse-time
ordered when candidates are gathered by increasing key/contact index, requiring
630 insertion-sort comparisons; `128*630=80640`. All thresholds satisfy
`0 <= off < on`, and all travel completes before frame end.

## Causality, hysteresis and anchors

Resolved reachable states satisfy `open => position < on` and
`closed => position > off`. The band between thresholds permits either bit,
depending on history. Starting at zero with `off < on`, resolving incoming
equality and preserving bits during holds maintain these invariants. Therefore
an eligible outgoing crossing at an already resolved interval start cannot be
silently lost by the strict lower endpoint. Independently repeated/unsorted
thresholds need no shared bit or threshold sorting assumption.

Use original command anchors and unsaturated speed for each root. Integer
command positions are exact even after an arrival clamp; ordinary processing
must not rebase an anchor. Repeating the current **target**, including while
moving, preserves its anchor. Tied changes away and back reanchor at the tie
time even when the final target equals the original target. For example,
speed 1 with `(tick,target)=(0,100),(3,100)` retains anchor `(0,0)`; adding
`(3,0),(3,100)` changes it to `(3,3)`. Both are valid in a one-frame call.
Coalescing the second sequence to its final target would corrupt snapshots.

Endpoint ownership is consistent with all partitions. For speed 1,
`off=32768`, `on=65536`, and target 131072 at zero, the first one-frame call
owns the closing edge at 65536. A target zero at 65536 belongs to the next
call and produces the opening edge at 98304. One two-frame call with both
commands must produce the same edges and final anchors. Closing observation
at 65536 with the target-zero command instead preserves position 65536 and
the closed bit: closure creates no travel. Incoming edges always precede
all commands at that time, including reversals and tied changes.

Thus concatenating `(start,end]` edge intervals neither drops nor duplicates
boundary edges. Exact arithmetic from persistent anchors gives partition
invariance; future commands cannot alter earlier motion or incoming equality.
Sorting exact roots by time/key/contact is sufficient. As a comparison trap,
the roots `200000000+1/(2^32-1)` and `200000000+1/(2^32-2)` are distinct and
ordered although their binary64 displays coincide. No display-time comparison
or epsilon merge is admissible.

## API, lifecycle and transactional obligations

The surface exposes the state needed to compare positions, targets, anchors,
bits, cursor and epoch counters. Copy only active configuration entries into
zero-initialized storage; inactive configuration and key snapshots must remain
canonical zero even when inactive caller fields contain invalid values. Compare
semantic fields, never object padding. All supported rates retain the same tick
trajectory; rate only defines its time in seconds.

Construction is unprepared; successful preparation starts a zero-history ready
epoch. Preparation is allowed while ready or closed and forbidden while active.
Reset is allowed only while closed and restores zero counters/history with the
retained canonical configuration. Closure from ready supports N=0 and counts
time-zero targets without moving a key. Closed processing, repeated closure and
ready/active reset are invalid-state operations, including empty processing.

Complete validation must preserve the declared precedence. In particular, a
late invalid domain beats an earlier decreasing tick; oversized count beats
target validation; nonempty zero-frame targets are invalid only after phase,
frame and count checks. Check size/frame allowances by subtraction before
addition, narrowing or iteration. Closing ticks are all the current cursor,
so no separate closing-order ambiguity exists.

Stage every state change and edge before touching caller output. Short output
returns the **actual** E and leaves output bytes and every semantic field
unchanged; capacity below the conservative bound succeeds when actual E fits.
Other failures return zero counts. The future-root example above must succeed
with an empty output span. Failed prepare/close/reset likewise retain the old
configuration/history. Retry starts from live state, not residual staging.
Arithmetic-overflow status is defensive; no admitted-domain input should reach
it. The valid/stable/nonoverlapping memory and serialized-access preconditions
are explicit and do not imply concurrent publication or callback retirement.

## Executed review and next acceptance

Performed exact integer/Fraction scratch calculations, no native build or
candidate execution. Checked the numeric extremes above; dynamic programming
over every `E=0..4608` and batch size 1..36 confirms the comparison ceiling,
including odd E. Independently advanced rational positions in 1/6-tick steps
for 56,250 streams: every `0 <= off < on <= 4`, press/release speeds 1..3,
and four targets in 0..4 at integer ticks 0..3. This mesh resolves all those
crossings exactly without a candidate root helper. The hysteresis invariants
and one-edge-per-command bound held. These small-domain mathematical checks
support, but do not replace, the full-domain proofs above.

A13 may implement the frozen surface and traversal. Acceptance still requires
the independent exact-rational oracle, three-rate partition/causality cases,
canonical inactive fields, all lifecycle/status precedence cases, late-invalid
and short-output rollback/retry, retained no-op/tied anchors, exact maximum
capacity stress, actual operation/storage/allocation receipts and portable
source review. Preserve the existing reference, Engine, source/parameter/state
identities. Filter/drain scheduling, conversion-error studies, full-organ or
indefinite capacity, platform deadlines and physical/host integration remain
separate gates.
