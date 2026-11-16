# Causal contact grid v1: trajectory and API contract

**Status: proposed for independent review, 15 November 2026.** Model identity
`causal-contact-grid-v1`; evidence class `synthetic`. This specifies an isolated
C++20 integer trajectory module, separately from
[fractional-contact-reference-v1](FRACTIONAL_CONTACT_REFERENCE.md).
Basis: the [streaming proposal](CONTACT_STREAMING_NEXT_DESIGN.md), its
[review](reviews/CONTACT_STREAMING_DESIGN_REVIEW.md), and this session's
[A04](development/2026-11-15-streaming-continuation/notes/A04-atlas-numerics.md)
and [A06](development/2026-11-15-streaming-continuation/notes/A06-atlas-completion.md).

No converter, waveform, routing, filter, drain/tail API or Engine connection.
Preserve existing contact models, 91 sources, 47 parameters, `B3CONTROLS4`/readers
1–3 and default dry PCM.

## 1. Domain and initial state

| Quantity | Admitted domain |
| --- | --- |
| Host rate F | Integer 44100, 48000 or 96000 Hz; fixed within an epoch |
| Time | 65536 ticks per host frame; absolute epoch ticks, starting at zero |
| Position Q | Integer units, 0 through `2^48` inclusive; `2^48` is full travel |
| Keys / contacts | 1–4 keys in configuration order; exactly nine independent contacts per key |
| Thresholds | Each contact has integer `0 <= off < on <= 2^48`; no sorting or distinctness requirement across contacts |
| Speeds | Independent press/release `uint32_t` units per tick, each 1 through `UINT32_MAX` |
| Targets | Integer tick, key input index and position in the domains above |
| Epoch / call | At most 4096 host frames; each process count is an integer number of frames |
| Supplied commands | At most 512 per epoch, including ties, no-ops and closing endpoint targets |

Initially time, positions, targets and anchors are zero; all contacts are open.
Arbitrary initial states are excluded. Rate maps tick time to seconds by
`t=tick/(65536*F)` without rescaling speed. Inputs are already grid values:
no rounding, clamping or binary64 conversion. Key/contact histories stay separate.

## 2. Exact travel, crossing arithmetic and order

A key retains integer anchor tick `a`, anchor position `p`, and target `q`.
At integer `t >= a`, position is `p +/- min(abs(q-p),(t-a)*speed)`, using
unsigned addition/subtraction branches and press/release speed for `q>p`/`q<p`.
For `q==p` hold. Arrival clamps exactly to the target without rebasing the anchor.
Travel between anchors is continuous and affine until arrival; contacts are
right-continuous. Integer-time evaluations remain integer-valued.

At a command tick, finish incoming motion through equality. Repeating the current
target is an exact no-op, including its anchor. Otherwise set anchor position to
current integer position, anchor tick to command tick, and replace the target.
Apply tied commands in supplied order without travel, including intermediate
changes. Only their resulting target controls outgoing travel. Commands create
no edge.

Open contacts close upward at `on`; closed contacts open downward at `off`.
Holds preserve bits. Exact arrival/command/reversal/process-endpoint equality
emits the incoming edge. Resolve **all** incoming equal-time edges before tied
commands. Sort by exact time, key index, then contact index; no epsilon merging.

For an eligible threshold `theta`, use **unsaturated** speed and original
command anchor. Put `D=abs(theta-p)`, `h=D/speed` and
`r=D%speed`. Crossing time is `a+h+r/speed` ticks. Represent this as a whole tick
plus a reduced proper fraction: `0/1` if `r==0`, otherwise
`(r/gcd(r,speed))/(speed/gcd(r,speed))`. Its denominator is positive and numerator
is smaller. On incoming interval `(b,e]`, admit only `b < root <= e`, thresholds
reached before/at the target, and the required incoming contact bit. Compare
whole ticks first, then compare fractions with
`uint64_t(n1)*d2` and `uint64_t(n2)*d1`. No float or `__int128` is needed.

**Overflow proof.** The epoch endpoint is `4096*65536=2^28` ticks. An evaluated
integer displacement is at most `2^28*(2^32-1) < 2^60`; cast before multiplying.
All positions and distances are at most `2^48`. Clamp displacement before
adding/subtracting it, so position stays in range. A future crossing quotient
can be as large as `2^48`: compute `a+h` in `uint64_t` (less than `2^49`), and
establish that a root is reached within the current interval/target before
narrowing its whole tick to `uint32_t`. Emitted whole ticks are at most `2^28`;
a root there must have zero fraction. Numerators and denominators are at most
`2^32-1`; their comparison products are strictly below `2^64`. Computing a
32-bit Euclidean gcd takes at most 64 remainder steps (start with the larger
operand; every two steps at least halve it). Unreached future roots need not
be stored. Check before narrowing; never wrap, saturate time or drop an edge.

## 3. Public C++20 surface

Implement `include/hammond/research/CausalContactGrid.h` with these names/types/
signatures and implementation-owned fixed private storage. No host/UI dependency.

```cpp
#include <array>
#include <cstdint>
#include <span>
#include <string_view>

namespace hammond::research {
inline constexpr std::string_view kCausalContactGridModelId =
    "causal-contact-grid-v1";
inline constexpr std::uint32_t kContactGridTicksPerFrame = 65536;
inline constexpr std::uint64_t kContactGridFullTravel = std::uint64_t{1} << 48;
inline constexpr std::uint32_t kContactGridMaxKeys = 4;
inline constexpr std::uint32_t kContactGridContactsPerKey = 9;
inline constexpr std::uint32_t kContactGridMaxFrames = 4096;
inline constexpr std::uint32_t kContactGridMaxCommands = 512;
inline constexpr std::uint32_t kContactGridMaxEdges = 4608;

struct ContactGridThreshold { std::uint64_t off{}, on{}; };
struct ContactGridKeyConfig {
    std::uint32_t pressUnitsPerTick{}, releaseUnitsPerTick{};
    std::array<ContactGridThreshold, 9> contacts{};
};
struct ContactGridConfig {
    std::uint32_t sampleRateHz{}, keyCount{};
    std::array<ContactGridKeyConfig, 4> keys{};
};
struct ContactGridTarget {
    std::uint32_t tick{}, keyIndex{};
    std::uint64_t position{};
};
struct ContactGridTime {
    std::uint32_t tick{}, numerator{};
    std::uint32_t denominator{1};
};
struct ContactGridEdge {
    ContactGridTime time{};
    std::uint32_t keyIndex{}, contactIndex{};
    bool closedAfter{};
};
enum class ContactGridPhase : std::uint8_t {
    unprepared, ready, active, closed
};
enum class ContactGridStatus : std::uint8_t {
    ok, invalid_state, invalid_configuration, frame_limit, command_limit,
    invalid_target, unordered_targets, output_too_small, arithmetic_overflow
};
struct ContactGridResult {
    ContactGridStatus status{ContactGridStatus::ok};
    std::uint32_t edgesWritten{}, requiredEdges{};
};
struct ContactGridKeySnapshot {
    std::uint64_t position{}, target{}, anchorPosition{};
    std::uint32_t anchorTick{};
    std::array<bool, 9> closed{};
};
struct ContactGridSnapshot {
    ContactGridPhase phase{ContactGridPhase::unprepared};
    ContactGridConfig config{};
    std::uint32_t cursorFrames{}, commandCount{}, edgeCount{};
    std::array<ContactGridKeySnapshot, 4> keys{};
};
class CausalContactGrid {
public:
    CausalContactGrid() noexcept;
    CausalContactGrid(const CausalContactGrid&) = delete;
    CausalContactGrid& operator=(const CausalContactGrid&) = delete;
    [[nodiscard]] ContactGridStatus prepare(const ContactGridConfig&) noexcept;
    [[nodiscard]] ContactGridResult process(
        std::uint32_t frames, std::span<const ContactGridTarget> targets,
        std::span<ContactGridEdge> output) noexcept;
    [[nodiscard]] ContactGridStatus close_observation(
        std::span<const ContactGridTarget> endpointTargets) noexcept;
    [[nodiscard]] ContactGridStatus reset() noexcept;
    [[nodiscard]] ContactGridSnapshot snapshot() const noexcept;
};
} // namespace hammond::research
```

Indices are zero-based. Validate/read only active configuration entries;
canonicalize inactive configuration/snapshot entries to zero. Copy configuration;
borrow spans for the call. Snapshots expose all semantic state without mutation.
Compare fields, not padding; no serialization/import API is implied. Unprepared
snapshots are zero with phase `unprepared`. Access must be serialized and
non-reentrant, including snapshots. Spans require valid, stable, nonoverlapping
storage outside the object; memory validity is a caller precondition.

## 4. Lifecycle, endpoints and transactional failures

| Operation | Allowed phase and result |
| --- | --- |
| Construction | `unprepared`, empty snapshot |
| `prepare(config)` | `unprepared`, `ready` or `closed` only; validate/copy configuration and start a fresh `ready` epoch |
| `process(0, {}, output)` | `ready` or `active`; exact identity, zero edges, no output writes |
| `process(frames>0, targets, output)` | `ready` or `active`; on success advance the cursor and enter/remain `active` |
| `close_observation(endpointTargets)` | `ready` or `active`; apply endpoint commands without travel and enter `closed` |
| `reset()` | `closed` only; retain configuration and restore the initial `ready` epoch |
| `snapshot()` | Every phase; no mutation |

Other combinations return `invalid_state`, including empty processing/repeated
closure when closed and preparation while active. Close before resetting or
reconfiguring active state. Prepare/reconfigure/destruct off the callback.

For entry frame `c` and `end=c+frames`, commands must be nondecreasing by tick in
`[65536*c,65536*end)`, preserving caller tie order. Finish incoming motion through
each command tick before applying its group, then through `65536*end`. Emit new
edges in `(65536*c,65536*end]`. Endpoint edges belong to this call; endpoint
commands belong to the next call or closure. No duplicate endpoint edge is
allowed. The new snapshot includes equality but no unsubmitted commands.

Closing targets must have tick `65536*cursorFrames`; apply/count them in caller
order. Incoming equality is already resolved. Close preserves position/contact
bits, changes targets/anchors as commanded, and creates no travel, edge or audio
event. For **N=0**, close with time-zero targets: positions stay zero and contacts
open. Zero-frame process cannot carry targets. Release uses an ordinary target
toward zero followed by processing; close does not simulate release.

**All mutating operations are whole-call transactions.** Validate complete input,
then use fixed state/edge staging. Write output only after all computation/capacity
checks succeed. Process commits state, writes only `output[0..E)`, and returns
`{ok,E,E}`. Capacity below **actual** E returns `{output_too_small,0,E}`; capacity
below the conservative bound is allowed when E fits. Other process failures return
`{status,0,0}`. Failure preserves output bytes and all semantic state/configuration;
scratch may change. A retry is identical to a first try.

Validation precedence is: phase; process frame allowance; remaining command
allowance; all target domains; then target ordering. Use subtraction checks
(`frames <= 4096-c`, `targets.size() <= 512-commandCount`) before additions or
iteration. `frame_limit` covers any excess frame count. `command_limit` covers
any excess supplied count, even no-ops. `invalid_target` covers key/position/tick
bounds and nonempty targets on a zero-frame process. After all target domains
pass, decreasing ticks return `unordered_targets`. Preparation uses phase first,
then `invalid_configuration` for unsupported rate/count, zero speed or invalid
thresholds. Close uses phase, count, then target-domain validation. Reset checks
phase only. Defensive checked-arithmetic failure returns `arithmetic_overflow`
transactionally; it must be unreachable for an admitted call under section 2.
No partial acceptance, truncation, implicit reset or exception is permitted.

## 5. Fixed storage and work ceilings

Let M be the supplied commands in a call, K its configured keys and A the keys
still moving at entry (`position != target`). Each monotone movement can cross
each of its nine contacts at most once. Every new movement requires a supplied
command; an incoming movement requires a previously accepted command. Therefore

`E_call <= 9*(A+M) <= 9*512 = 4608`, and `E_epoch <= 9*M_epoch <= 4608`.

Initial holds and closure add no edges. The second inequality uses
`A <= previous commandCount`; it does not add K movements to all 512 commands.

Embed fixed staging for 4608 edges, live/staged state for four keys and at most
36 temporary interval edges; preparation only validates/copies. All methods,
including rejection,
must not allocate/deallocate, lock, perform I/O/logging or throw. No whole-epoch
history or per-tick/frame stepping is needed. Publish actual object/scratch bytes
and allocation-hook scope; bounded storage is not a measured callback deadline.

A bounded traversal visits M+1 or fewer command-delimited intervals, evaluates
each key and examines its contacts once per interval. Normalize reached roots;
insertion-sort each interval's at most 9K edges before appending. Per-call ceilings:

| Counted operation | Bound | Absolute maximum |
| --- | --- | --- |
| Target validation/application | M each | 512 each |
| Key position evaluations | K(M+1) | 2052 |
| Contact candidate examinations | 9K(M+1) | 18468 |
| Reached roots / gcd normalizations | E | 4608 |
| Euclidean remainder steps | 64E | 294912 |
| Edge ordering comparisons | at most `(9K-1)*E/2` | 80640 |
| Committed edge copies | E | 4608 |

All syntactically admitted v1 calls meet these work limits. At most 4096 positive
calls fit an epoch, bounding their contact examinations by
`36*(4096+512)=165888`. Arbitrarily repeated empty calls/rejections have per-call
bounds only. A different algorithm needs a reviewed equivalent bound.

## 6. Required acceptance and remaining gates

For the same input, single-frame/irregular/maximum-block partitions plus closure
must give identical concatenated edges and final snapshot, including anchors and
counters. Empty/rejected calls cannot change that result. At a common cursor,
identical earlier commands give identical emitted edges through equality there;
commands at or after that cursor cannot revise those edges (future causality).

Require an independent exact-rational oracle without candidate crossing helpers.
Cover three rates; speed/position extremes; unsorted/repeated thresholds;
exact/fractional arrivals; equal and close distinct roots; command/endpoint/
reversal ties; partial holds; no-op anchors; tied changes; N=0; limits; lifecycle
errors; late-invalid input; short output and retry. Retain source/input/oracle
identities, edges, snapshots, operation/allocation receipts and portable arithmetic
review. This document reports no implementation test pass.

This **separate identity** is not full binary64-reference equivalence. A future
converter needs rounding/collision and error/topology studies: small perturbations
can change equality, order or bits. No audio-error/aliasing/latency/physical grade
follows. Later gates retain the proposal's D=16 schedule, partial-cell integration,
33-sample nonempty drain, full-window continuous comparison, rate/phase policy and
deadlines. Bounce/resistance/loading, physical acquisition, full-organ/indefinite
capacity and Engine/host lifecycle integration remain unresolved.
