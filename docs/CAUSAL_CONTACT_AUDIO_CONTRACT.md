# Causal contact audio grid v1: isolated stream contract

**16 November 2026; frozen proposal awaiting independent admission.** Model ID
`causal-contact-audio-grid-v1`, evidence class `synthetic`. This resolves the six
[A50 conditions](reviews/CAUSAL_CONTACT_AUDIO_NEXT_REVIEW.md) for an isolated
C++20 module. Implementation starts only after the independent contract review.
The [grid contract](CAUSAL_CONTACT_GRID_CONTRACT.md),
[offline reference](FRACTIONAL_CONTACT_REFERENCE.md),
[original validation](CONTACT_SWITCHING_VALIDATION.md) and
[conversion contract](CONTACT_GRID_CONVERSION_CONTRACT.md) retain their domains,
criteria and results. No Engine/host routing, physical model, callback deadline,
4096-frame audio extension or continuous-reference pass is authorized here.

## 1. Signal, finite domain and exact epoch origin

Use the existing grid's initial state, independent nine-contact hysteresis,
commands, incoming equality and ordering unchanged. Its 4096-frame capability is
not reduced; this wrapper admits **at most 256 input frames per epoch**.

| Quantity | Frozen audio domain |
| --- | --- |
| F; L; H; D | F=44100/48000/96000 Hz; L=256; H=16; D=16 frames |
| Keys / commands / physical edges | 1–4 keys; nine routes/key; 512 supplied targets including closure; 4608 edges/epoch |
| Sources | 1–36 unique IDs in 1..91; active source entries need not be sorted |
| Source fields | finite frequency 0..0.45F Hz, amplitude 0..1, phase 0..less-than-1 turns |
| Routes | Each active key/contact names a configured source ID; finite gain in [-1,1]; duplicate source routes stay separate |
| Origin | `int64_t frame`, inclusive [-2^48,+2^48], an exact label in host frames at this epoch's F |
| Output | N>0: N process samples plus 33 drain samples, all N+33; N=0: empty |

For exact epoch-local host coordinate u, source value is
`A*sin(2*pi*(phaseTurns + frequencyHz*u/F))`. The declared phase is **at this
epoch's origin**, not at global frame zero. The origin is a label: physical input
time is `(origin.frame+u)/F`; it never enters waveform arithmetic. Output index m
is emitted at label `origin.frame+m`, represents reference index `n=m-16`, and
has reference label `origin.frame+m-16`. Labels and additions fit int64_t.

Notes, silence, disconnected routes, callbacks and drains never restart phase.
Drain advances output m only; input remains at N. Stopped `reset(newOrigin)`
starts an **independent replay with the same configured phase values** at that
new label. It promises no phase continuity between epochs. Supplying different
phases requires stopped `prepare`. A changed rate may replace a ready configuration
before any input is consumed. Once input has been consumed, it requires complete
old-rate drain, then preparation; no implicit rate conversion or discarded-tail reset.

The ungated raw sum is over independent route products `gain*contact*source`.
There is no gain fitting, route-gain precombination, clipping or polyphony
normalization. Observation gates raw input to [0,N); closing is not release.
An exact-zero routing fast path may skip waveform work, but still advances all
trajectory, cell-index, output-length and lifecycle facts defined here.

## 2. Frozen C++20 surface (A50-C3/C4)

Implement `include/hammond/research/ContactAudioStream.h` and
`src/research/ContactAudioStream.cpp` in namespace `hammond::research`, using
`CausalContactGrid.h` types directly. Names, field types and signatures below are
normative; private layout remains implementation-owned.

```cpp
inline constexpr std::string_view kContactAudioModelId =
    "causal-contact-audio-grid-v1";
inline constexpr std::uint32_t kContactAudioMaxFrames = 256;
inline constexpr std::uint32_t kContactAudioMaxSources = 36;
inline constexpr std::uint32_t kContactAudioOversampling = 256;
inline constexpr std::uint32_t kContactAudioDelayFrames = 16;
inline constexpr std::uint32_t kContactAudioTailFrames = 33;
inline constexpr std::uint32_t kContactAudioRingCells = 8194;
inline constexpr std::uint32_t kContactAudioCoefficientCount = 8193;

struct ContactAudioOrigin { std::int64_t frame{}; };
struct ContactAudioSource {
    std::uint32_t sourceId{};
    double frequencyHz{}, amplitude{}, phaseTurns{};
};
struct ContactAudioRoute { std::uint32_t sourceId{}; double gain{}; };
struct ContactAudioConfig {
    ContactGridConfig grid{};
    std::uint32_t sourceCount{};
    std::array<ContactAudioSource, 36> sources{};
    std::array<std::array<ContactAudioRoute, 9>, 4> routes{};
};
enum class ContactAudioPhase : std::uint8_t {
    unprepared, ready, active, closed, draining, drained
};
enum class ContactAudioStatus : std::uint8_t {
    ok, invalid_state, unsupported_environment, invalid_configuration,
    invalid_origin, frame_limit, command_limit, invalid_target,
    unordered_targets, output_too_small, drain_limit,
    arithmetic_overflow, numeric_failure
};
struct ContactAudioResult {
    ContactAudioStatus status{ContactAudioStatus::ok};
    std::uint32_t samplesWritten{}, requiredSamples{};
};
struct ContactAudioOpenRoute {
    bool closed{};
    ContactGridTime start{};
};
struct ContactAudioSnapshot {
    ContactAudioPhase phase{ContactAudioPhase::unprepared};
    ContactAudioConfig config{};
    ContactAudioOrigin origin{};
    ContactGridSnapshot grid{};
    std::uint32_t outputCursor{}, drainRemaining{};
    std::uint32_t firstRetainedCell{}, retainedCellCount{}, completedCellCount{};
    bool hasOpenCell{};
    std::uint32_t openCellIndex{};
    double openCellSum{}, openCellCompensation{};
    std::array<ContactAudioOpenRoute, 36> openRoutes{};
    double rawBound{};
    bool exactZeroRouting{};
    double terminalLeftValue{}, terminalGateJump{};
};
class ContactAudioStream {
public:
    ContactAudioStream() noexcept;
    ContactAudioStream(const ContactAudioStream&) = delete;
    ContactAudioStream& operator=(const ContactAudioStream&) = delete;
    [[nodiscard]] ContactAudioStatus prepare(
        const ContactAudioConfig&, ContactAudioOrigin) noexcept;
    [[nodiscard]] ContactAudioResult process(
        std::uint32_t frames, std::span<const ContactGridTarget> targets,
        std::span<double> output) noexcept;
    [[nodiscard]] ContactAudioStatus close_observation(
        std::span<const ContactGridTarget> endpointTargets) noexcept;
    [[nodiscard]] ContactAudioResult drain(
        std::uint32_t count, std::span<double> output) noexcept;
    [[nodiscard]] ContactAudioStatus reset(ContactAudioOrigin) noexcept;
    [[nodiscard]] ContactAudioSnapshot snapshot() const noexcept;
};
```

No optional origin, user limits, public state import or hard-abort operation.
Read/copy only active configuration entries; canonicalize inactive entries and
all zero-valued floating fields to positive zero. Source IDs are unique in the
source array, but may repeat in routes. The snapshot is an observation, not a
serialization/restore format: it omits private ring sample bytes and scratch.
Compare named fields, never ABI padding. `openRoutes[9*key+contact]` follows
configuration order. An inactive/open route has `closed=false,start={0,0,1}`.
`completedCellCount` counts all finalized cells since epoch start, including
ones evicted; retained cells are consecutive. Empty retention has
`firstRetainedCell=completedCellCount`. Closed/draining/drained epochs have no
open cell, zero open-cell fields and canonical open routes; physical bits remain
in `grid`. Terminal values are zero before closure. Ready/active state has one open cell
with index `256*grid.cursorFrames`; initially its sum/compensation are zero.
Before closure `drainRemaining=0`; after nonempty closure it is 33.
`outputCursor` is the next m to emit (N+33 after complete nonempty drain).
N=0 closure finalizes no cell: both completed/retained counts stay zero.
Unprepared fields have their aggregate defaults, including `exactZeroRouting=false`.

All access, including snapshots, is serialized and non-reentrant. Caller spans
are valid/stable, mutually nonoverlapping and outside the object throughout the
call; invalid memory/aliasing is a caller precondition, not a recoverable status.
Prepare, reset, replacement and destruction are stopped/off-thread operations.
No mutation allocates, frees, locks, logs, performs I/O or throws.

### Lifecycle, result lengths and precedence

| Operation | Allowed entry phase; successful transition |
| --- | --- |
| prepare | unprepared/ready/drained -> ready, new configuration and epoch |
| process(0,{},out) | ready/active -> identical state; no writes |
| process(frames>0,...) | ready/active -> active; outputCursor and grid cursor each advance by frames |
| close_observation | ready/active -> closed for N>0; -> drained for N=0 |
| drain(0,out) | closed/draining/drained -> identical state; no writes |
| drain(count>0,out) | closed/draining -> draining if samples remain, otherwise drained |
| reset | drained -> ready, retain configuration and phases, independent replay at new origin |
| snapshot | all phases; no mutation |

Every other combination returns `invalid_state`, including repeated closure,
processing after closure, and reset/reprepare before complete drain. In drained,
positive drain returns `drain_limit` (the phase itself is allowed). N=0 closure
still counts/applies valid time-zero targets without travel, then has zero drain.

Commands occupy `[cursor*65536,(cursor+frames)*65536)`, nondecreasing by tick with
caller tie order. Incoming edges include the processing endpoint and belong to
that call. Closing targets have exactly `cursor*65536`; they alter target/anchor
only. Zero-frame processing rejects nonempty targets. The 512-command allowance
counts no-ops and closing targets.

On process/drain success write precisely the requested prefix and return
`{ok,count,count}`. Larger spans are accepted; every suffix byte is untouched.
Short output returns `{output_too_small,0,count}` without writes/state changes.
Other result failures return `{status,0,0}`. A zero count returns `{ok,0,0}`.

Precedence, before any caller write or committed-state change:

1. Allowed phase; then supported floating environment.
2. Process: remaining 256-frame allowance; remaining 512-command allowance;
   all target domains (including zero-frame rule); target ordering; output
   capacity; trial-grid defensive arithmetic; audio arithmetic/numerics.
3. Close: remaining command allowance; all endpoint target domains; trial-grid
   operation; terminal audio arithmetic/numerics.
4. Drain: `count<=drainRemaining`; output capacity; audio arithmetic/numerics.
5. Prepare: complete grid/source/route configuration; origin range; prepared
   coefficient/bound arithmetic and numerics. Reset: origin range only.

Configuration failures are `invalid_configuration`; origin failures are
`invalid_origin`. Numerical nonfinite values or coefficient admission failures
are `numeric_failure`; checked integer/internal capacity failures are
`arithmetic_overflow` and must be unreachable for admitted inputs. The private
grid's defensive status maps directly where names match. Use subtraction for
remaining quotas before adding or iterating. Invalid target domains win over
unordered targets even if the invalid target is last. The wrapper's output
capacity check deliberately precedes its expensive trial computation; standalone
grid error precedence remains unchanged.

## 3. Portable exact interval arithmetic and raw bound (A50-C1)

Freeze a separate `include/hammond/research/ContactAudioTime.h` with no stream
header dependency. Implementation may be in `src/research/ContactAudioTime.cpp`.
All functions are fixed-storage C++20 and `noexcept`:

```cpp
namespace hammond::research::contact_audio_detail {
struct UInt128 { std::uint64_t high{}, low{}; };
struct ExactRatio {
    UInt128 numerator{};
    UInt128 denominator{0, 1};
};
struct RawBoundProduct { double amplitude{}, gain{}; };
[[nodiscard]] int compare_time(const ContactGridTime&,
                               const ContactGridTime&) noexcept;
[[nodiscard]] bool time_width_frames(const ContactGridTime& left,
                                     const ContactGridTime& right,
                                     ExactRatio& result) noexcept;
[[nodiscard]] bool time_midpoint_frames(const ContactGridTime& left,
                                        const ContactGridTime& right,
                                        ExactRatio& result) noexcept;
[[nodiscard]] bool ratio_to_double(const ExactRatio&, double& result) noexcept;
[[nodiscard]] bool accumulate_raw_bound(std::span<const RawBoundProduct>,
                                        double& bound, bool& exactZero) noexcept;
}
```

`UInt128` means `high*2^64+low`. Time inputs are valid grid mixed fractions in
[0,2^24] ticks; a time at 2^24 has zero fraction. This is a precondition of
`compare_time`, which returns -1/0/+1 and uses the grid's exact comparator.
The bool time functions validate tick/fraction domains, require `left<=right`,
and leave `result` unchanged on failure. Fractions need not be reduced, but
`numerator<denominator`, positive denominator and integer `0/1` are required.
Equality produces width 0/1. Nonzero ratios need not be reduced. No binary64
endpoint subtraction, epsilon equality, saturated arithmetic or `__int128`.

For endpoints `(T_i,a_i,b_i)`, form `p_i=T_i*b_i+a_i` in uint64_t, then
`A=p_left*b_right`, `B=p_right*b_left`, `D=b_left*b_right` in unsigned limbs.
Return width `(B-A)/(D*2^16)` and midpoint `(A+B)/(D*2^17)`; canonicalize zero to
0/1. Comparison precedes unsigned subtraction. Signed int64_t cell-boundary
arithmetic handles the initial -128 ticks; gate-clip to zero **before** forming
a nonnegative time. Integer cell boundaries have denominator 1.

**Proof of storage.** `p_i<2^56`, `A,B<2^88`, `D<2^64`, width denominator <2^80
and midpoint denominator <2^81; midpoint numerator <2^89. A same-cell interval
is at most 256 ticks, so its width numerator is at most `256D<2^72`.
The generic width helper may receive the entire epoch and then needs <2^88
numerator, still within two limbs. Every intermediate fits 128 bits. Use checked
32-bit partial products/unsigned carry and borrow; even a uint64_t product must
be widened before any addition that can carry. No signed-overflow reasoning.

`ratio_to_double` returns correctly rounded nearest-even binary64, positive zero
for zero. Its admitted representation has numerator <2^89, denominator in
[1,2^81), and ratio in [0,256]; malformed/out-of-domain inputs return false
without changing output. A nonzero ratio is >=2^-81, hence conversion cannot
underflow. Do not shift a numerator by `52-exponent` into 128 bits: that can
require 134 bits. Instead perform restoring binary division, retaining an exact
remainder smaller than the denominator; generate leading/significand/guard bits
and use the nonzero remainder as sticky. A doubled remainder is <2^82. At most
89 integer-bit steps plus 81 leading-fraction steps plus 54 significand/guard
steps, **224 division steps**, suffice. Ties round to an even low significand
bit; a carry renormalizes exactly. An equivalent bounded algorithm needs the
same proof and independently checked rounding vectors.

`accumulate_raw_bound` accepts at most 36 finite pairs with A in [0,1] and gain
in [-1,1]; invalid inputs preserve both outputs. Compute the **exact** sum
`B_exact=sum(A*abs(gain))` from input binary64 bit patterns. Return the smallest
binary64 B>=B_exact and `exactZero=(B_exact==0)`. A zero rounded product or signed
cancellation never proves silence. In particular, two minimum positive
subnormal factors require `B=denorm_min`, `exactZero=false`.

A concrete fixed implementation decomposes each factor into integer significand
and power of two, accumulates exact nonnegative products at scale 2^-2148 in
34 uint64_t limbs, then rounds upward. Each exact product has at most 106 bits;
B_exact<=36, so the accumulator needs at most 2154 bits, below 2176. At most 36
products and 1224 limb-add/carry visits suffice. Underflow rounds a positive
bound upward to the minimum subnormal. This helper is prepare-only; there is no
callback big-integer dependency or input-size-dependent allocation.

## 4. Canonical cells, sums, filter and ring (A50-C1/C5)

Define `C[j]=256*integral x(u)du` over the centered cell
`[(j-.5)/256,(j+.5)/256)`, clipped to [0,N). Only j=0..256N can contribute.
Cell boundaries are exact integer ticks `256*j-128` and `256*j+128`.
The first/last cells are half cells; closure finalizes cell 256N's left half.

Keep one open cell, its two-double Neumaier accumulator, and each of 36 routes'
exact open start and contact bit. A connected interval ends only at its own
break, a cell boundary or observation closure. **An integer frame/call boundary
never finalizes or combines a pending contribution.** Commands themselves do
not split a constant connection, including no-ops and reversals before a root.

At a cell right boundary, finalize all incoming connected routes in ascending
key/contact order, finish/store that cell, clear its accumulator and start the
next cell. Then replay equal-time physical edges in their grid order. At a
physical break strictly inside a cell, finish that route's piece immediately;
at make, store its exact start. Zero-width pieces contribute nothing. Thus
canonical accumulation is chronological completed break pieces, then the active
routes at cell end. This cell-before-edge tie rule applies identically in every
partition. Simultaneous contacts are never collapsed into a combined gain.

Form exact width d and midpoint q first, then round each once using section 3.
Use `nu=frequencyHz/F`, `pi=0x1.921fb54442d18p+1`, `tau=2*pi`, and evaluate every
piece with this operation grouping, including full cells:

```text
s = sinc(nu*d)
a = tau * (phaseTurns + nu*q)
piece = gain * (((amplitude * (256*d)) * sin(a)) * s)
```

Here `sinc(v)` sets `x=pi*v`; for `abs(x)<1e-4`, use
`1+x*x*(-1/6+(x*x)*(1/120-(x*x)/5040))` with binary64 constants/divisions and
shown grouping; otherwise use `sin(x)/x`. A cache may reuse an identically
computed source interval value, but may not introduce a different full-cell
formula or factor/round combined route gains. The same input source ID therefore
has one common mathematical phase even when its independent contacts differ.

For each cell and each FIR output separately start `sum=correction=+0` and add x:
`t=sum+x`; if `abs(sum)>=abs(x)`, add `(sum-t)+x` to correction, otherwise add
`(x-t)+sum`; then set `sum=t`. Retain both terms across calls for an open cell.
Finalize once as `sum+correction`. Check all intermediates for finiteness and
canonicalize a zero final value to positive zero. This bounded compensated
policy is deliberately not a claim to reproduce Python `math.fsum` bitwise.

The prepared kernel is the original Blackman-windowed sinc, H=16, beta=.45:
`k(v)=.9*sinc(.9*v)*(.42+.5*cos(pi*v/16)+.08*cos(tau*v/16))` for |v|<16,
zero otherwise. Evaluate r=0..4096 at v=r/256, mirror the nonnegative half
exactly, and force both endpoints to positive zero. Sum raw coefficients in
ascending k with the Neumaier policy; normalize each coefficient by that single
positive finite sum. Admit only finite coefficients, compensated DC residual
<=2e-14 and absolute coefficient sum <=2. Endpoint zeros and mirrored bytes
are exact. Use no circular FIR convention or library phase assumption.

```text
y[n] = sum in ascending j of C[j] * c[n*256-j+4096]
z[m] = y[m-16] = sum in ascending j of C[j] * c[m*256-j]
```

Ignoring the zero endpoint coefficients, support is
`max(0,(m-32)*256+1) <= j <= min(256N,m*256-1)`. Emit z[m] **before** ingesting
[m,m+1). Its newest cell ends at `m-1/512`, so no unavailable input is read.
D=15 would require future input under this schedule; D=16 is the least integer
delay here. z[0] and z[N+32] are positive zero, but a forced 16-zero prefix is
incorrect: early nonzero ringing is valid.

Keep two complete fixed audio states (committed/trial), each with an 8194-double
ring and its indices; keep one immutable 8193-double coefficient array and 256
staged output doubles. After z[m], evict only cells below the next output's
lower bound `max(0,(m+1-32)*256+1)`, then ingest this frame and append completed
cells in ascending j. Before a process emission at most 8191 completed cells
plus the open cell are relevant. Closing may append its terminal half cell,
leaving at most 8192 completed cells. Thus 8194 slots suffice. Processing an
entire block's input before its early outputs is forbidden: it can evict history
still needed by those outputs. Empty sums and absent/gated future cells are zero.

For N>0 process emits m=0..N-1; drain emits **m=N..N+32 inclusive**, exactly 33.
For N=256 this is 289 outputs representing n=-16..272. Silent nonempty epochs
have the same length. N=0 is the explicit empty exception, first reference frame
0; never manufacture a 33-zero drain.

## 5. Private trial-grid composition and terminal state (A50-C2)

Add only a private `friend class ContactAudioStream;` declaration to
`CausalContactGrid`; preserve its public API, standalone validation/order,
4096-frame limits, noncopyability and existing tests. The wrapper embeds separate
committed and trial grid objects. It copies **only the committed `state_`** into
the trial object's `state_`; the trial public operation initializes its own
staging. Never accept/restore a caller snapshot, copy raw object bytes or commit
the public grid before audio validation.

For process: validate all wrapper inputs, copy committed audio/grid state into
fixed trial storage, call the trial grid once with its own 4608-edge output
array, and replay those edges starting from **entry** contact bits. The audio
sweep interleaves output and frame ingestion as section 4 requires; it consumes
the sorted edge array once, including endpoint equality. Check its resulting
physical bits against the trial grid. Stage every output. Only after all work
succeeds copy the trial grid's `state_` and complete audio state into committed
storage and publish the output prefix. These last fixed copies cannot fail.
Scratch/trial bytes may change on rejection; committed semantic state and every
caller output byte must remain unchanged. Retry starts by reseeding the trial.

For close: seed both trial states, run trial `close_observation`, finalize the
pending cell at the terminal gate and compute terminal diagnostics, then commit
both states together. An incoming break at N has already completed its left
piece even if its final bit is open; a make at N has zero audible duration even
if its final bit is closed. Endpoint targets create no new travel/edge. Record
bits immediately **before** incoming endpoint edges during processing, so
`terminalLeftValue` is the ungated x(N-) from those bits, in canonical route
order; `terminalGateJump=-terminalLeftValue`. It is not computed from post-edge
or post-command bits. For N=0 both are positive zero. Terminal diagnostic
failure rolls back closure too. Drain stages audio state/output; grid state is
unchanged. Prepare/reset stage complete fresh state before publication.

No private seam may expose an externally callable state-restoration facility.
Independent review must inspect both grid and wrapper diffs and rerun the old
grid suites. A late numeric failure must be exercised through a test-only fault
hook or test accessor with no enabled production backdoor; it cannot be claimed
covered only by an early malformed-input rejection.

## 6. Floating environment and source-bound resources (A50-C5)

Require IEC 60559 binary64 (`sizeof(double)==8`, 53 significand bits), nearest-even
rounding, gradual underflow, no excess-precision evaluation, no fast-math and
no multiply-add contraction. Compile numerical translation units with the
platform's matching strict options. Before each mutator, after phase checking,
validate rounding mode and an evaluated volatile normal/subnormal multiply/add
probe; an unsupported environment returns `unsupported_environment` without
changing its control state or exception flags. Save and restore the floating
environment around that probe; this requirement applies to the probe, not to
ordinary inexact flags produced by successful signal evaluation. Nontrapping
floating exceptions are a caller/environment precondition: the C++ standard
offers no portable trap-mask query, and callers must not enable synchronous
floating traps around these APIs. Snapshot performs no floating arithmetic. Named compiler/library
builds need their own observations; C++ does not promise a universal libm error
bound or cross-platform identical transcendental results.

Fixed arrays belong to the object, not the callback stack. `sizeof` the complete
stream must be **<=1,048,576 bytes** on each admitted ABI; maximum additional
stack use of any API/helper path **<=16,384 bytes**. All embedded grid, rollback,
edge, coefficient, route, bound and output storage counts. A concrete envelope
is two grid objects <=262144 bytes, one edge array <=147456, two rings 131104,
coefficients 65544, samples 2048, and all remaining state/padding <=131072,
total <=739368 bytes. These are ceilings to verify, not measured sizes. Do not
hide an allocation or put a whole object copy on the stack to meet them.

Let R=9K<=36, E<=4608, and C=256N+1 for N>0. In addition to the unchanged grid
bounds, the complete accepted epoch including closure/drain has these ceilings:

| Count | Bound at N=256, K=4 |
| --- | --- |
| New cell finalizations | C=65537 |
| Cell-boundary route visits | R*C=2359332 |
| Edge replay visits | E<=4608 (one sweep; no per-cell edge rescan) |
| Nonzero-width piece evaluations | <=R*C+E=2363940; no list of all pieces is stored |
| Per-cell completed-piece count | <=R+E=4644; a two-double accumulator has no piece-capacity overflow |
| FIR terms, including drain | <=(N+33)*8191=2367199 |
| Exact time conversions | <=2*(R*C+E), each <=224 division steps |
| Stored pending routes | 36 exact starts/bits; no 2304-piece burst allocation |
| Per-call staged edges / samples | 4608 / 256 (drain count <=33) |

The reviewed 512-command burst (four keys, off=0/on=1, both speeds UINT32_MAX,
commands to 1 on even and 0 on odd ticks 0..127) has 4608 edges and 2304
connected pieces in cell zero's positive half. It is admitted without enlarging
storage or silently dropping muted physical edges. At most 256 positive process
calls, one close and 33 positive drain calls occur per epoch; each may make fixed
state copies. Arbitrarily many empty/rejected calls have per-call bounds only.
Validation reads at most 512 target entries; excess span counts reject before
iteration. Rejection after late staging may spend a whole bounded call.

Retain allocation **and free** hooks for success, empty, rejection, retry,
closure, split drain, reset and prepare. Inspect fixed memory and stack on named
builds, not just one observed workload. Work bounds and allocation hooks provide
no device callback deadline, scheduler headroom or host-retirement evidence.

## 7. Independent exact-grid admission (A50-C6)

Protocol ID `contact-audio-exact-grid-validation-v1`. Freeze generated fixture
bytes, all expected discrete facts, this document hash and oracle source before
viewing candidate errors. The independent Python-standard-library oracle uses
`Fraction` for trajectory, exact clipping, width/midpoint and B; it may use
binary64 `math` transcendentals and `math.fsum`. It must independently reconstruct
trajectories, intervals, coefficients and output from these equations, without
importing candidate/native/reference-renderer crossing, integral or kernel
helpers or using candidate edges as integration boundaries. This is an exact
**grid/trajectory**, discrete-L256 comparison, not exact real arithmetic or a
continuous quadrature admission. Record shared libm limitations explicitly.

### Frozen fixture authority and native cases

The separately owned [validation protocol](CAUSAL_CONTACT_AUDIO_VALIDATION.md)
and `tests/reference/contact_audio_cases.py` are the sole recipe/fixture-byte
authority: G01–G12 at all three rates plus explicitly named small/extreme cases.
They are frozen and independently admitted before candidate errors. These new
grid fixtures neither replace nor silently convert the original F00–F11 rows.
The validation protocol must retain exact zero, DC, source peak/zero crossing,
high frequency, coherent duplicate routes, cancellation, partial holds,
no-ops/reversals/ties, half-cell/root/host/closure equality, N=0/1/256, ring wrap,
4608-edge/2304-piece burst, subnormal products and the two wider-rational examples
from A50. A fixture's full nine-contact configuration, all binary64 source/gain
bytes, commands, origin and expected outcomes are normative inputs.

Additional rational helper vectors cover zero/equality, integers, maximum
denominators, reversed endpoints, midpoint rounding ties (both parities),
guard/sticky carry and every invalid helper domain. Source-uniqueness,
36-source and invalid-source tests are required API cases separate from the
waveform matrix. The smallest-product fixture must prove
`B=denorm_min,exactZero=false` even when audio rounds to zero. Cancellation
and equal-display-root fixtures need their special discrimination criteria
below; a loose bound-normalized error alone cannot detect their disappearance.

For each fixture, independently check every edge's exact time/identity/order,
all grid snapshot fields and final target/bit facts. Because the stream has no
public edge output, the native probe may separately run the unchanged grid and
compare that trace with the stream's grid snapshot; the oracle never consumes
that trace as its authority. Native arithmetic tests compare exact ratio limbs
and binary64 conversion bits with independent `Fraction` expectations.

Each nonempty native row runs: one N-frame call; all one-frame calls; and
repeating `[1,7,3,32,2,19]` truncated to N, inserting empty calls. Split targets
only by their global tick, never reround them; endpoint targets go to close.
Run drains `[33]`, 33 calls of1, and `[0,7,0,13,13,0]`. Require bit-identical
concatenated samples and equal snapshots at common input/output cursors on the
same strict build; different partitions need not have identical scratch bytes.
Compare actual persistent ring/state through a test-only inspection or equivalent
continuation tests after rejection. Require unchanged output sentinels/suffixes,
short-output retry, last-invalid target, all status precedence pairs, repeated
close/premature reset, max limits, origin endpoints, reset replay, ready-state rate
replacement and rate changes only after drain once input has been consumed, and
a late injected numeric failure in process and close.
For causal-prefix tests, alter only targets at/after a shared cursor and require
all already emitted samples/physical history to remain identical.

### Numerical gates and reporting

All complete N+33 outputs are compared after **only D=16 index translation**.
For B>=2^-900, require `max(abs(candidate-oracle))/B <= 1e-10`.
Normalize by B before squaring; eligible NRMSE is RMS(error/B)/RMS(oracle/B)
when RMS(oracle/B)>=1e-8, and must be <=1e-9. Below that RMS floor report
ineligible, never zero or a manufactured pass. The declared
`[1,2^-54,-1]` cancellation fixture additionally uses its known residual scale
2^-54 in the peak bound. Equal-display-root and wider-rational thin-pulse cases
additionally require nonzero candidate output and peak error <=1e-9 times the
oracle's nonzero output peak.
B_exact=0 requires every output to be exact positive zero.

For 0<B<2^-900 use a separately labeled underflow tier:
`max(abs(error)) <= 1e-10*B + 2^18*2^-1074`, evaluated as exact rational
arithmetic, plus exact upward B/exactZero checks. Report peak/B diagnostically,
but confer **no nominal relative-error or NRMSE pass** on these rows. The absolute
floor bounds accumulated subnormal rounding rather than asserting relative
accuracy of unrepresentably small products. Nonfinite output always fails.

The nominal margins are selected engineering headroom: at most 4644 pieces per
cell, 8191 FIR products per output, |C|<=B in real arithmetic and kernel absolute
sum<=2 bound rounding amplification. Compensation removes first-order ordinary
sum-length loss; the remaining basic-operation scale is far below 1e-10 on
regular inputs. This is motivation, not a portable libm theorem: named builds
must demonstrate the frozen limits. Require independent coefficient symmetry,
endpoint bytes, DC residual<=2e-14, and max coefficient difference<=5e-16.
No threshold changes, fitted gain/delay, omitted rows or post-error fixture edits.

Freeze exact-grid oracle suite ceilings: 180 million FIR products, 180 million
cell/route visits, 600 seconds external elapsed, 512 MiB exact-child peak RSS,
64 MiB retained report bytes; per-row W<=20 million using the original count
formula, whose N256/K4/M512/L256 maximum is 4744518. Retain generated inputs,
all samples/edges/snapshots/metrics, counters, failures, resource observations,
contract/oracle/native/header/build/config hashes and commands. An overrun is
incomplete, not a numeric pass/fail, and does not silently enlarge a budget.
These counters and elapsed limits cover independent numerical reconstruction;
the separate native partition, lifecycle and allocation invocations have their own
observed costs and must satisfy section 6. The sole fixture/resource authority is
the validation protocol, including its separate exact-grid full-continuous job.
The oracle/native source independence is reviewed separately from these counts.

## 8. Separate conversion and full continuous gate (A50-C6)

The exact-grid grade above cannot satisfy the old binary64 fixture or full
continuous grade. Integer speed s corresponds to exact duration `2^32/(F*s)`
seconds, generally non-dyadic and possibly outside the old parser's domain.
Never round it into that parser and call the resulting trajectory equivalent.

For the 36 original F00–F11/rate rows retain their original bytes and every
conversion acceptance/refusal, including F09 equality failures. Admit converted
rows only through the existing converter's complete topology and error
certificate; refusal remains refusal. Separately compare original and converted
**L256** outputs over all 289 samples, requiring conversion-only peak/B<=2e-5
and eligible NRMSE<=1e-4 under the original normalization rules. A trajectory
certificate alone supplies no audio budget. Report all 36 rows; a refused or
failed row cannot be dropped to assert completion of the original matrix.

Freeze the distinct future protocol ID
`contact-audio-full-window-continuous-v1`: independently reconstruct original
binary64 trajectories and eight-point Gauss–Legendre quadrature, splitting at
all true contact/gate/support boundaries. Retain widths 1,1/2,1/4 and independent
continuous normalizers, but evaluate **every n=-16..272 for every original row**.
No candidate boundary, interpolation or sampled-filter output may drive it.
The original 64-probe protocol/reports and 10-million ceiling remain unchanged.

| Full-window gate | Required criterion, every row and all 289 samples |
| --- | --- |
| Continuous refinement, widths1/2 versus1/4 | peak/B<=1e-9; eligible NRMSE<=1e-7; retain width1 differences |
| Original L128->L256 convergence | peak/B<=6e-5; eligible NRMSE<=3e-5; retain L32/L64 and response/tail diagnostics |
| Original L256 versus converged quadrature | peak/B<=2e-5; eligible NRMSE<=1e-5 |
| Converted native candidate versus original converged quadrature | peak/B<=1e-4; eligible NRMSE<=1e-4; conversion/topology and all preceding gates required |

Use the original B=0, RMS floor1e-8 and normalization semantics; only D=16
alignment, no gain fit or tail trim. Retain full samples/refinements, responses,
DFT/tail diagnostics and original failures. The **new** protocol separately
permits 256 million FIR products (original factors plus converted L256),
256 million cell/route visits, 64 million integrand evaluations including
normalizers/responses/retained legacy diagnostics, 600 seconds, 512 MiB peak RSS
and 64 MiB reports. These
predeclared proposed limits neither rebind nor enlarge an old result. The full
protocol needs its own independent source/resource admission before grading;
no unrun gate is inferred from this contract or the discrete test suite.

Physical contact bounce/resistance/loading, specimen calibration, indefinite
clocks, full-organ capacity, Engine scheduling, real audio devices, host latency
and callback retirement remain separate milestones. Preserve the nominal dry
Engine, 91 source identities, 47 parameters, `B3CONTROLS4`/readers1–3 and UUIDs.
