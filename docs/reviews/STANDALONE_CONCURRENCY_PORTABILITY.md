# Standalone concurrency oracle portability repair

Assignment 46 repairs an observed test-oracle failure without changing Session,
Engine, its memory ordering or the musical contract. The maintained
[concurrency guide](../STANDALONE_CONCURRENCY.md) describes the current gate;
this review preserves the failure and exact repair evidence.

## Original hosted failure and diagnosis

Published source `5b8e2419d23fe27c51709d717812060eafd44dcc`, tree
`880682248c467a51cce14d920189cf0009b68d22`, failed the Linux GCC Release
[job 132222981693](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43523378849/job/132222981693).
The workflow reported **89/90 suites passed** in 52.24 seconds. The concurrency
test failed at its former line 629: `counts.raced_discarded > 0`. Its earlier
portable exception-unwind cleanup and exact recovery/accounting assertions had
not reported failures. See the [root follow-up](STANDALONE_PLATFORM_FOLLOWUP.md).

The consumer stored `entered` immediately before calling `Session::render`.
After observing that flag, the producer attempted 96 late posts. The operating
system may let the consumer complete the whole call, including recovery
acknowledgment, before the producer resumes. All those posts then legitimately
belong to the new epoch. Requiring a positive raced-discard count confused one
possible schedule with the public contract. Successful earlier runs and TSAN
cannot establish that every future scheduler will choose that ordering.

## Narrow change and preserved invariants

All **64 recovery epochs and 256 callbacks** remain. An atomic permit holds the
consumer outside `render` for the first two recovery epochs. Their 96 late
attempts must respectively be blocked by pending overflow or admitted then
discarded behind an invalid payload. In the next two epochs the producer waits
for the actual render to return before posting; both sets of 96 must be accepted
after the acknowledged boundary. The other **60 epochs** retain the unscheduled
late-post race. The permit is already open for those callbacks.

Each attempt is counted exactly once as RecoveryPending, admitted-and-discarded,
or accepted above the resolved sequence. The 60 concurrent epochs must account
for exactly **5,760 attempts**. Controlled outcomes are separately required as
**96 pending, 96 discarded and 192 accepted after acknowledgment**. No private
Session state or timing sleep is used to force an internal race, and no counter
is falsely described as a post made inside the consumer's captured prefix.

Every prior per-epoch control, hold, sequence, rejection, overflow and exact
accepted-command reconciliation remains. Valid new-epoch commands drain before
a FIFO Panic; empty later output retains the recovered controls and counters.
The unchanged free-running phase still posts 8,192 complete controls across 32
ring laps with two readers. Sixteen active-overflow rounds, coherent/failed-read
checks, finite audio, quiescent cleanup and the portable stop/join unwind probe
remain. Production code and the eight-second watchdog were not changed.

## Actual coherent qualification

Archived the named published source, overlaid only the maintained test, and
built separate fresh SDK-free Release and RelWithDebInfo/TSAN trees. All **830
frozen files** matched the retained inventory after execution. Both first
configure/build/test sequences succeeded; no test retry or fixture adjustment
was needed. Linux x86-64, GCC 14.2.0, CMake/CTest 4.4.4, C++20 strict project
warnings with `-Werror`; SDL and VST3 were OFF.

| Observed workload | Release | TSAN |
| --- | ---: | ---: |
| CTest result / total time | 1/1 pass / 0.13 s | 1/1 pass / 0.75 s |
| Ordered posts / free callbacks / observed active posts | 8,192 / 1,340 / 8,119 | 8,192 / 442 / 8,182 |
| Recovery accepted = applied + rejected + discarded | 14,990 = 3,648 + 32 + 11,310 | 15,072 = 3,648 + 32 + 11,392 |
| Controlled pending / discarded / after-ack accepted | 96 / 96 / 192 | 96 / 96 / 192 |
| Concurrent pending / discarded / after-ack accepted | 2,962 / 2,798 / 0 | 2,880 / 2,880 / 0 |
| Active-overflow accepted = applied + discarded | 4,176 = 80 + 4,096 | 4,177 = 81 + 4,096 |
| Active overflow / deferred recovery observations | 16 / 16 | 16 / 16 |
| Successful coherent reads / busy reads preserved | 352,344 / 5,111 | 156,266 / 1,741 |
| Forced exhausted reads preserved | 256 | 256 |

Both runs also require 64 immediate invalid posts and 32 queue overflows.
Concurrent observations vary legally; these values are retained outcomes, not
new expected constants. This local pair did observe raced discards; it does not
claim an executed zero-race-discard case. Source classification permits zero
while still requiring all controlled boundary outcomes and total accounting.

All **23 actual compilation units** in the TSAN gate carried
`-fsanitize=thread -fno-omit-frame-pointer`: 19 core sources, Session, UI model,
state files and this test. Both static archives reference the runtime and the
test executable links `libtsan`; `TSAN_OPTIONS=halt_on_error=1` was used. There
was no race diagnostic or runtime suppression. A first auxiliary object-matching
audit used an incorrect relative-output assumption and raised `StopIteration`;
resolving `-o` against each compile command's directory corrected that audit.
The maintained source, successful test runs and compiler instrumentation did not
change. Exact commands and identities are in [assignment 46](../development/2026-11-13-next-phases/46-concurrency-oracle.md).

## Remaining gate

Root must rebuild and execute the focused test in its assembled source, then
publish and inspect actual platform reruns. This repair removes the demonstrated
incidental positive requirement; bounded concurrent stress is not an exhaustive
interleaving proof. Weak-memory hardware, native backend threads, callback
deadlines and physical fidelity remain outside these SDK-free Linux results.
