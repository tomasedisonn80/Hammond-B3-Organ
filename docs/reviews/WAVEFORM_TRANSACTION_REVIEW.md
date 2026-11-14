# R4 transaction and lifecycle design review

**A11, wave 2, 14 November 2026 — accept the proposed API and transaction design
for implementation, with the test-seam clarification below.** No renderer
implementation, allocation workload, sanitizer run or device deadline is
qualified by this review. The unchanged
[numerical contract](../ROTARY_NUMERICAL_CONTRACT.md) remains authoritative;
the [renderer contract](../ROTARY_RENDERER_CONTRACT.md) supplies the concrete
admission and ownership rules.

## Decision and repaired test boundary

The public declarations need no signature change. Staged small motion owners
and diagnostics, prepared output scratch, and one reverse undo record for each
overwrite can provide the required whole-call guarantee. Each record must be
live before the first of that frame's four ring writes. Recording only the
first overwrite of each distinct slot, or restoring records in forward order,
would be incorrect when `N>H`.

The original retained-slot failure fixture had one coverage limitation: every
pre-call slot is overwritten within `H` appends. Such a fault cannot by itself
prove failure after multiple complete wraps. The integrator accepted a narrow
addition to the existing private test friend: shorten only the second motion
ring's private append limit. This forces an actual `process()` failure after
multiple wraps and partial writes without a shipping callback, failure switch,
new API or exposed rollback helper. Keep the retained-slot fixture as a separate
history/interpolation failure experiment. The amended contract now requires
both. This change clarifies testing; it does not enlarge the public input domain
or alter `rotary-numerics-v1`.

## Requirements for implementation acceptance

| Area | Required behavior and reason |
| --- | --- |
| Journal | Save both old sample values and both old original segments at `n%H` before any append; make that entry live before a helper can fail. Record each overwrite, including repeated indices. |
| Rollback | Replay every live entry in reverse, then restore all four pre-call ring clocks. Restore partially written frames too. Discard staged owners and diagnostics. |
| Preserved state | Preserve configuration, all ring metadata and slot values, physical owners, committed diagnostics and every caller-output byte. Scratch/journal work bytes are excluded and cannot affect later output before being overwritten. |
| Publication | Finish all samples, final owner advancement and ordered offset-`N` commands before publishing owners, diagnostics or either output. No operation capable of returning failure may follow the first publication. |
| Failure result | Return the originating primitive status and zero consumed events. Completed solves may contribute to the returned call maxima; rejected-call maxima never enter persistent diagnostics. |
| Stack and allocation | Allocate the fixed storage directly on the heap while stopped. Do not construct a storage-sized temporary for `make_unique`, copy a history on the process stack, or allocate a journal/output vector during processing. |
| Reset | Validate/stage original-seed owners before clearing histories. Preserve current rate/spec/capacity/geometry; return to original commands and original phase/speed with zero original turns. |
| Rate replacement | Copy existing motion owners and apply their stopped rate change, preserving their original reset seeds. Re-preparing owners from the current state would incorrectly replace those seeds. Initialize candidate storage fully before swapping it into the renderer. |
| Exceptions | The public lifecycle methods are `noexcept`; a failed storage allocation must become `AllocationFailure`, never termination. Construction failure must leave the previous pointer and all its contents intact. Constructor, process and reset remain allocation-free. |

These are implementation conditions, not newly invented acceptance budgets.
The current `RotaryMotion::reset` and `reconfigure_sample_rate` already distinguish
the original seed from the current epoch seed. The renderer must retain that
distinction when moving owners into replacement storage.

### Admission and overlap

The specified precedence is executable and should be tested with combined
defects, because a set of single-defect tests cannot prove ordering:

| Earlier defect plus a later defect | Required first status |
| --- | --- |
| Unprepared renderer plus excessive block/events | `NotPrepared` |
| Excessive block plus excessive events | `BlockTooLarge` |
| Admitted block, excessive events plus mismatched audio lengths | `TooManyEvents` |
| Bad lengths/audio overlap plus invalid event | `InvalidBuffer` |
| Exceeded epoch plus invalid event | `TimelineOverflow` |
| Invalid/unsorted event plus nonfinite input | `InvalidEvent` |
| Otherwise valid arguments with out-of-range/nonfinite input | `InvalidBuffer` |

All these rejections must preserve preexisting nonzero history and future
accepted output. Use valid backing arrays for ordinary overlap tests: identical
and partially overlapping inputs are accepted; any positive overlap involving
an output is rejected; exact adjacency and empty spans are accepted. Byte-range
end calculations require checked integer arithmetic before comparisons.
Unrelated-pointer subtraction is not a valid overlap test. Do not use invalid
object lifetimes or invented pointers as substitutes for real buffer fixtures.

Events are borrowed only for the duration of the call. Their admission scan and
all later processing reads must finish before output publication; retaining an
event pointer or iterator for another call is forbidden. No extra event/audio
alias restriction is part of the API. Valid typed storage and lifetimes remain
caller preconditions, so an overlapping fixture must not manufacture undefined
C++ behavior through an incompatible `reinterpret_cast`. A local event array
that is destroyed or reused after a successful call supplies a straightforward
lifetime check. An event-copy allocation is neither necessary nor permitted.

### Zero and end boundaries

Preserve the ordered absolute event stream when changing block partitions.
An offset-`N` event belongs after the call's samples and before the following
call's offset-zero events. A zero-frame call must process every valid offset-zero
event in order, count all of them, leave the rings and physical frame unchanged,
and leave diagnostics unchanged. Empty zero-frame calls are also legal at the
full-day boundary. A nonempty call beyond that boundary rejects first at the
timeline stage.

Test alternating commands for one rotor at the same boundary, interleaved events
for the other rotor, and unchanged commands. Compare the final active segment
and its original anchor, not only the final command enum. Repeated unchanged
commands must not reanchor; different tied commands must not be merged or
omitted from `events_consumed`. Compare floating fields by their bit
representations where bit identity is required: default floating `operator==`
does not distinguish signed zeros and rejects equal NaN bit patterns. Do not
compare whole padded structs with `memcmp`.

## A20: independent late-failure experiments

The reference here is a closed-form stationary delay and a matched unmodified
renderer. The test must not implement another copy of the production undo loop.
Use heap-owned fixtures/snapshots and allocate all inputs, outputs and event
storage before the measured call.

### Common deterministic fixture

Use `Fs=48000`, `c=300`, zero rotor radius, both origins at zero, and both
microphones at `{3/128,0,0}` metres. Choose otherwise valid, explicitly recorded
motion seeds/profiles and reference distance. The exact mathematical delay is
`3.75` frames, so `D=4`, `H=10`, and the advertised flush is eight frames.
The fixed observation lag gives emission `n-6+0.25` and cubic supports
`{n-7,n-6,n-5,n-4}`. These relationships are independently derived from the
declared geometry and operator, not production ring traversal.

Prepare two identical renderers and feed distinct, bounded deterministic horn
and drum sequences through `F=40` accepted frames. This fills and wraps the
history before the rejection experiment. Include real command transitions.
Snapshot all public copied values and, through the private friend, every ring
field and physical slot, including unused backing slots. Store numeric field
bits and scalar fields; do not depend on object padding. Guard complete output
allocations with distinctive sentinels. Preserve a copy of the one injected
value for later restoration.

### Experiment 1: a later support read fails

1. Corrupt only the horn sample at absolute frame `39` to finite value `2.0`,
   outside the admitted sample range. Take the rejection snapshot **after**
   injection: the poison is part of the call's pre-state.
2. Submit a valid 37-frame block with early commands, same-offset ties and an
   offset-37 command. The first three samples query supports `33..36`, `34..37`
   and `35..38`. Sample `43`, the fourth attempted sample, first includes the
   poisoned frame `39`; its write slot is `3`, so the poison has not retired.
3. Expect `InvalidBuffer` from support admission, zero consumed events, unchanged
   caller bytes and exact preservation of the corrupt pre-state. Returned
   solver work must be nonzero; persistent diagnostics must remain the earlier
   accepted values. Record the calculated first read and actual observed late
   execution, rather than calling an ordinary input preflight failure late.
4. Restore only the injected sample, then submit the original valid block to
   both renderers. Require bit-identical outputs, copied physical state and
   diagnostics, and continue for more than two ring lengths. This exposes
   damage to history that a public-state snapshot alone would miss.

The finite poison avoids relying on NaN comparison behavior. A separate NaN
variant may be added, but then snapshot equality must compare the NaN bits.

### Experiment 2: partial-frame failure after repeated wraps

Start again from the common matched frame-40 state. Leave both physical owners'
limits and all other history fields unchanged. Set only the second motion
history's private `max_frame_` to `63`, and snapshot that injected pre-state.
Submit 37 valid frames. There are 23 permitted appends, at frames `40..62`.
At frame `63`, the undo record must already be live; earlier ring writes occur
before the second motion append rejects its endpoint with `TimelineOverflow`.

The failing transaction has 24 live records for slots
`0..9,0..9,0..3`: four slots are recorded three times and six twice. This catches
first-write-only journals, forward replay, incomplete partial-frame recovery
and clock restoration errors in one bounded call. Require zero events consumed,
untouched outputs, unchanged public state/diagnostics, and exact ring recovery
including the shortened limit. The injected limit is restored **after** those
assertions, then accepted continuation is compared with the unmodified control.

Retain direct evidence that the expected prefix and partial frame ran. Where
the implementation leaves prepared scratch/journal entries available after
rollback, the private fixture may seed them with markers and inspect their
progression; these are test observations, not new persistent-state guarantees.
If scratch is deliberately cleared, use an equivalent test-build debugger or
coverage observation without a shipping callback or public counter. Merely
observing a final `TimelineOverflow` status is insufficient to prove late work.

Do not replace this whole-process experiment with a handwritten journal model.
A separate production-helper unit test would qualify only that helper, not
the actual partial-write/publication path.

## A29: allocation and failure experiments

### Calibrate the detector before interpreting zero counts

Use executable-local C++ allocation/deallocation replacements covering scalar,
array, nothrow, aligned, sized and matching deletion forms. Preserve a visible
interposition boundary under optimization. The existing portable
`test_rotary_propagation_allocation.cpp` supplies an applicable calibration
pattern: explicit calls through opaque function pointers avoid new-expression
elision, and calibration observes twelve allocations and twelve deallocations
in separate intervals. Validate alignment and returned storage as well as counts.

Build/prewarm every fixture, heap snapshot and report structure before arming
recording. Do not assert, format, log, construct containers or destroy fixtures
inside a measured interval. Measure actual calls with accepted nonzero audio,
zero-frame events, maximum block/event counts, repeated small-ring wraps,
largest admitted capacity, representative preflight rejections, and both A20
late failures. Require zero observed C++ allocations **and** deallocations for
each process interval; a valid-only measurement cannot qualify rejection paths.
Also check the allocation-free constructor and reset in separate intervals.

### Force lifecycle allocation failures

Use a calibrated test-only fail-next-allocation mechanism. A throwing allocation
must produce `std::bad_alloc`; a nothrow allocation must return null. Arm it only
around the lifecycle call after all expected-state snapshots exist. Disarm it
before diagnostics or assertions. Verify the failure was actually reached,
rather than reporting preservation from a call that never attempted allocation.

| Operation under forced failure | Required observation |
| --- | --- |
| First valid `prepare` | `AllocationFailure`; still unprepared, default copied values, no owned storage |
| Valid replacement `prepare` after nonzero history | `AllocationFailure`; complete old configuration/history/state preserved |
| Valid different-rate replacement | `AllocationFailure`; old rate, epoch, commands, original reset seeds and acoustic tail preserved |
| Valid same-rate replacement | Same failure guarantee; equal rate still requests a new epoch/storage |
| Invalid spec/profile/rate with failure armed | Specific admission status, no allocation attempt, unchanged object |

After each failed replacement, disable the fault and compare accepted output
against the untouched control for a suffix long enough to read the old tail.
Public snapshots alone cannot prove audio-history preservation. Successful
stopped replacement may allocate candidate storage and destroy old storage;
neither belongs inside the process allocation interval. If construction ever
gains another fallible allocation, test every reached failure point and prove
candidate cleanup without deleting the old storage.

For successful lifecycle coverage, exercise all sixteen old/new supported-rate
pairs, including equal rates. Establish nonzero turns and commands distinct
from the original ones before replacement. Verify physical state preservation,
frame-zero current-state epoch seed, silent replacement audio history, default
diagnostics and new `H`/flush values. Then reset: the original profile seeds and
commands must return at the **new** rate. Include an original initial speed
greater than both targets to catch geometry admission that loses the original
reset envelope after a slowed epoch.

The detector observes this thread's global C++ calls. It does not by itself
prove absence of arbitrary C/system allocation, other threads, locking or
deadline misses. Report that scope and inspect the concrete process source for
the excluded operations. Do not promote a zero-count result to device or host
qualification.

## Boundedness and retained evidence

The storage bound is independent of elapsed duration and event lifetime:
four fixed rings, `2*4096` output doubles and at most 4096 undo records.
Ring payload is `2*16384*(sizeof(double)+sizeof(MotionSegment))`; report actual
compiled sizes and stack usage rather than assuming one platform's ABI.
Processing must not copy that payload. Small active capacities are important:
a 4096-frame block can overwrite one slot hundreds of times, and the journal
still needs one record per attempted frame, not per distinct slot.

At most `4096*4*48 = 786432` path geometry evaluations are permitted by the
maximum block/solver bounds, plus bounded per-frame motion/history work and
at most 1024 ordered events. A late rejection adds at most 4096 undo records.
No duration-growing event list, sorting, full-history scan or recursive solve
is required. Record worst accepted/rejected timings and compiler stack evidence
for the actual implementation; these arithmetic bounds are not an executed
performance or deadline result.

The [A11 note](../development/2026-11-14-waveform-continuation/notes/A11-transaction-review.md)
records inspected identities and the small fixture calculation. A20/A29 should
retain exact source/build/profile hashes, statuses, poison/limit location,
observed late prefix, full snapshot/continuation comparison counts, calibrated
allocation counts and failures. R4 parity, R5 reconstruction, R6 host/device
integration and physical cabinet fidelity remain separate claims.
