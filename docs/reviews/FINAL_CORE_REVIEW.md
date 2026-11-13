# Final core review: Agent 55

## Decision and reviewed snapshot

**One low-severity control-persistence defect was reproduced and repaired.** The
focused Release regression passed after failing against the original code. No
additional concrete correctness defect was found in the bounded core audit.
Publication and hosted qualification of the repair remain the integrator's gates.
This review does not certify a physical instrument, native audio host or concurrent
engine access.

The inspected published baseline was
`6c3dd8bc923a3c11f6b234425b056e135fbe9f4b`, observed on 2026-11-13. At the
start of review, tracked `src/`, `include/` and `CMakeLists.txt` had no changes
against that head. The working tree also contained the new factory-runtime test
and evidence/demo work. The inspected `tests/test_factory_runtime.cpp` SHA-256 was
`3b1bd39d1bf52f889b9e1ba5c1b1f171e6d1863fb7303d8d41fe9cd5d233212d`.

The review read the standing instructions, current status/next steps/plan,
development log, original [wave ledger](../development/WAVE_LOG.md), and distinct
[console continuation ledger](../development/2026-11-13-continuation/README.md).
The continuation's planned contact/percussion modules were not treated as
implemented. Source context included the retained atlas review and text of atlas
chapters 016, 024 and 063, PDF pages 103-108, 151-156 and 385-390. This was not
another complete atlas reading or a new visual/table transcription.

## Confirmed defect and repair

**C55-01: expression serialization depended on the caller's rounding mode.**
The original expression insertion in
[ControlStateIO.cpp](../../src/ControlStateIO.cpp), baseline lines 128-131, used
classic-locale stream formatting and `max_digits10` but inherited the caller's
floating-point rounding mode. The shared decimal parser deliberately selects
`FE_TONEAREST`. That mismatch could change a valid saved expression by one ULP,
contradicting the exact round-trip guarantee in the
[control-state format](../CONTROL_STATE_FORMAT.md).

A fixed-vector C++ probe used
`std::bit_cast<double>(std::uint64_t{0x3fbfd7f684a99224})`, an ordinary expression
of approximately `0.12438908327892101`, then called `serialize_controls` and
`parse_controls` under each mode. On this GCC 14.2.0/libstdc++ executor:

| Caller mode | Original serialized expression | Restored binary64 bits |
| --- | --- | --- |
| `FE_TONEAREST` | `0.12438908327892101` | `0x3fbfd7f684a99224` |
| `FE_DOWNWARD` | `0.124389083278921` | `0x3fbfd7f684a99223` |
| `FE_UPWARD` | `0.12438908327892101` | `0x3fbfd7f684a99224` |
| `FE_TOWARDZERO` | `0.124389083278921` | `0x3fbfd7f684a99223` |

Both original calls preserved the caller's mode; the lost bit came from output
conversion. A separate small-expression probe found the same issue, so it was
not specific to one numeric magnitude. Severity is low: this violates an exact
persistence contract but does not establish an audible fault or a callback failure.

The integrator expanded this assignment to repair the defect. Serialization now
uses the existing `detail::DecimalRounding` RAII guard only around expression
formatting. That selects nearest rounding to match parsing and restores the prior
mode at scope exit, including exception unwinding. Failure to select nearest
rounding returns a diagnostic before destination publication. The format remains
`B3CONTROLS1`; its fields, bounds and nearest-mode bytes are unchanged. No callback
code, source parameters, profile data or model identity changed.

The added [control I/O regression](../../tests/test_control_io.cpp) checks nine
fixed binary64 expressions under all four standard modes: the failing ordinary
value, positive/negative zero, minimum subnormal, maximum subnormal, minimum
normal, `0.1`, the predecessor of one, and one. It verifies exact result bits,
mode-independent serialized bytes and mode restoration after both serialization
and parsing. Rejected invalid-snapshot, aliased-output and nonzero-underflow cases
also preserve the mode and existing destination/diagnostic behavior. The new
round-trip assertion failed before the production repair, so this is an observed
regression test rather than a passing test added only after the fix.

## Contracts examined

### Profiles, decimal input and owned preparation

[Profile.cpp](../../src/Profile.cpp) bounds input at 128 KiB plus one lookahead
byte, uses explicit ASCII tokenization, enforces the exact record order, and parses
into a local candidate. Whole-document validation precedes destination assignment.
The fixed-size profile has owned identities, source values, gains and all 549
manual routes. Missing data does not create a fallback profile.

The [decimal helper](../../include/hammond/detail/Decimal.h) checks the complete
decimal grammar before conversion, isolates conversion from the caller's locale,
preserves signed exact zero, rejects nonzero underflow to zero and rejects
nonfinite/overflow results. Its treatment of subnormal stream `failbit` is explicit
and supported by fixed binary64 boundary tests. It assigns its destination last.
Loading and decimal conversion allocate outside processing. They are not no-throw
status APIs: resource failures and arbitrary custom-stream exceptions may escape;
destination publication remains transactional. Input-byte bounds do not bound
the latency of an arbitrary supplied stream.

The profile loader normalizes `ios_base::failure` and standard streambuf exceptions
when the stream confirms a read failure, including failure after the final payload
byte. A normal throwing EOF can still complete. The inspected profile/robustness
tests compare every semantic destination field, preserve caller locale/exception
masks, and recover on a fresh stream; they do not inspect structure padding.

[Engine::prepare](../../src/Engine.cpp) first prepares a local source bank and
publishes the fixed-size profile/spec/bank only after all validation succeeds.
The bank likewise validates and builds its entire local candidate before replacing
state. Existing tests mutate and expire caller profile storage, reject at the last
source, compare public state, and compare subsequent audio against an untouched
engine. They therefore exercise ownership and private cached-state preservation,
not just the returned error code.

### Shared sources, seed recurrence and numerical domain

[TonewheelBank.cpp](../../src/TonewheelBank.cpp) owns 91 source states. Unsigned
SplitMix64 arithmetic has deliberate modulo-2^64 wrap. Every ascending source ID
consumes one draw, including muted sources and seed zero; the top 53 bits produce
the initial phase offset. Key and control APIs have no path to reseed the bank.
Each processed frame emits all current-phase samples and advances all sources
once, including silence and disconnected output.

The computed increment is admitted only in `[2^-53, 0.5)` turns/sample, after
intrinsic data and Nyquist validation. Preparation rejects tiny positive sources
instead of installing a frozen oscillator. Initialization and advancement need
only one phase-wrap subtraction within their admitted domains. The render-clock
origin is independent of phase: it does not simulate preceding samples.

The [numerical contract](../NUMERICAL_BOUNDS.md) correctly distinguishes guaranteed
progress from accuracy near the floor. Its nominal finite-window bounds assume
ordinary binary64 nearest rounding without fast-math; they are not unlimited-time
or cross-platform bit-identity guarantees. The source tests combine frozen seed
answers, elapsed-time comparisons and a one-second crossing check. The numerical
test adds an exact integer modular elapsed-phase oracle at the nominal extremes,
avoiding a duplicate double-addition recurrence and avoiding dependence on wider
`long double` precision.

Successful re-preparation deliberately starts a new seeded field. Seamless
sample-rate migration and physical shaft/gearing relationships are future
contracts; they are not supplied by the current preparation method.

### Scheduling, rejection and clock boundaries

Engine preflight checks preparation, frame capacity, output extent, event count,
64-bit clock addition, ordered offsets and every payload before any event or
output mutation. Positive offsets are half-open; ties retain input order. No
sort, deferred queue or allocation occurs inside processing. A zero-frame flush
applies its events once and returns without source/clock advancement or output
writes; the caller owns removal of consumed events.

The clock check uses `frames > UINT64_MAX - frame_clock`, avoiding overflowing
addition. Processing can end at the maximum clock, then only zero-frame work is
accepted. The engine test explicitly exercises the last valid frames, rejected
overflow with a mutating event prefix, and an accepted flush at the maximum.
It also checks invalid final events, 1024/1025 capacity, short buffers, untouched
trailing output, connected/disconnected continuation, and a hand-written musical
schedule across several block partitions. Those cases distinguish timing behavior
from a comparison of two copies of the same event interpreter.

### Bounded processing work and resources

The inspected callback graph comprises fixed arrays, scalar arithmetic, range
checks, control updates, coefficient rebuilding and `std::sin`. No
project-controlled path performs file/stream work, logging, dynamic allocation,
ownership destruction, locks, worker submission or an unbounded retry.

There are at most 1024 accepted events and 65536 prepared frames per call. Every
positive frame evaluates 91 sources; connected output additionally mixes 91
contributions. A coefficient rebuild scans at most 2 x 61 x 9 branches, at most
once per event cluster before its sample. A conservative rebuild bound is
`min(frames, event_count + 1)`, allowing dirtiness from a prior flush/restore.
AllNotesOff scans only one 61-key manual. Valid normalized inputs bound the exact
worst coherent sum by 1098, far below float overflow; this is not a PCM clipping
guarantee.

The [allocation test](../../tests/test_realtime.cpp) records only the actual
process call, after fixture preparation, and calibrates its C++ allocation hooks.
Its maximum/dense/rejected paths are meaningful. The retained zero-allocation
result in [REALTIME.md](../REALTIME.md) is still limited to those hooks and runs:
C allocation, library internals, page faults, lock/I/O interception and deadline
qualification remain separate. This review did not rerun that instrumented suite.

### Four banks, routing-only Cancel and controls-only state

[ControlState](../../src/ControlState.cpp) retains two independent banks per
manual. Direct hidden-bank edits change neither selection nor route enablement;
legacy Drawbar edits the selected retained bank. Selection reconnects. Cancel
only disables the addressed route. AllNotesOff releases that manual's boolean
keys without replacing its controls or shared phases. The coefficient cache is
marked dirty when these operations can change routing and is rebuilt before the
next audible sample. An unnecessary rebuild after a hidden edit is bounded and
does not change the resulting audio.

The control tests check held-key bank changes at exact offsets, hidden edits,
both manuals cancelled, later reselect without new notes, continued phase during
silence, and panic/reselect that cannot recreate released keys. Their legacy-event
audio reference is useful for the extension but shares the underlying Engine;
independent engine and factory-routing checks are complementary evidence.

[ControlSnapshot](../../include/hammond/ControlState.h) contains the 39 musical
controls and two route bits, with no keys, source phases or frame clock. Restore
validates before replacement and leaves those dynamic histories intact. The
bounded persistence parser publishes its complete candidate last and rejects
extra/versioned/malformed data. Its format intentionally omits profile identity,
host ownership and checkpoint compatibility. Saving/reloading it cannot establish
an exact DSP restart or a host project-state protocol.

## Independence of the new factory runtime gate

[test_factory_runtime.cpp](../../tests/test_factory_runtime.cpp) takes expected
route IDs from both frozen manual CSVs, not the production map or foldback formula.
It checks all 1098 manual/key/drawbar cases at 48 kHz, selected boundaries at the
other supported rates, coherent duplicate routes, two-manual addition and
Cancel/reselection. Expected sums retain duplicate branches and use a separately
advanced source timeline. Positive reference windows must contain nonzero audio;
wrong-route and muted-source probes must disagree substantially.

The reference timeline deliberately uses the same production `TonewheelBank`.
A defect common to both banks could pass this test. The
[factory-runtime report](../FACTORY_RUNTIME_ACCEPTANCE.md) already discloses that
boundary and assigns source correctness to the independent seed/waveform/numerical
suites. This is a sound separation of test responsibilities, not an independent
source-physics oracle. CSV equality alone does not establish independent historical
transcription; the retained review procedure and source provenance supply that
documentary claim. The new gate was inspected, not rerun by Agent 55.

## Executed checks and remaining gates

Executed on Linux with GCC 14.2.0; the focused CMake build was Release with the
repository's strict warnings. A bare `cmake` invocation initially failed because
it was absent from PATH. The existing installation at
`/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/` was then used; no
dependency was installed for this assignment.

| Check | Actual outcome |
| --- | --- |
| Scratch fixed-vector probe, original source, `-O3 -DNDEBUG` and strict warnings | Compiled; exit 1; downward/toward-zero changed the ordinary expression by one ULP |
| New `test_control_io`, original serializer | Failed the exact restored-expression bit check; CTest exit 8, 0/1 passed |
| Rebuilt `test_control_io`, repaired serializer | Passed; 338 malformed-input cases preserved destination semantics |
| `test_controls` | Passed |
| `test_decimal` | Passed; 16547 exact values/round trips and 106 rejected tokens |
| Combined selected Release CTest | 3/3 passed; no skipped selected suites |

Reproduction from the repository root, using the installed CMake/CTest binaries
on PATH or their explicit paths:

```sh
cmake -S . -B ../agent55-control-release -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build ../agent55-control-release --target test_control_io test_decimal test_controls --parallel 2
ctest --test-dir ../agent55-control-release -R '^test_(control_io|decimal|controls)$' -C Release --output-on-failure -V
```

The final source/document diff and whitespace were checked. The profile,
tonewheel, engine, numerics, realtime and factory suites were inspected but not
rerun for this assignment. No full-suite, new sanitizer, new hosted Linux/macOS/
Windows, allocation-failure injection or forced rounding-API-failure result is
claimed. Exception restoration follows the reused RAII guard; the new tests
execute ordinary successful and rejected operations, not injected output exceptions.

Remaining physical limits include unmeasured tuning/pickup data, ideal contact
edges and their added bandwidth, proposed drawbar/expression laws, and absent
AO-28/scanner/Leslie behavior. Remaining host limits include note-owner identity,
native automation curves, device callbacks and deadline measurement. Every
diagnostic, prepare/restore operation and mutable engine access still requires
stopped or same-processing-thread access. No concurrent publication/retirement
protocol, race test or live profile handoff is established. These are explicit
scope limits, not newly discovered failures of the current nominal engine.
