# Standalone Session concurrency acceptance

Assignments `/root/w04_a22_session_concurrency`,
`/root/w08_a46_concurrency_oracle` and `/root/w09_a50_reader_progress`,
13 November 2026, maintain
[`test_standalone_concurrency`](../apps/standalone/tests/test_standalone_concurrency.cpp)
against the actual [Session contract](STANDALONE_SESSION.md) and implementation.
No production code changed. This supplements [serial acceptance](STANDALONE_SESSION_ACCEPTANCE.md).

## Current reader participation and publication-progress gate

Hosted Linux Release at `649b12c7` failed the remaining positive
`reader.active_reads > 0` assertion, with 89/90 suites passing. Scheduling can
legitimately let a reader run only between callbacks. The activity flag brackets
a public `render` call; neither a positive observation nor a ready-thread flag
proves that a read occurred inside that call. Requiring nonzero flag observations
confused incidental scheduling with the Session contract.

Each of the two readers now performs one coherent, exact full-snapshot read
before the consumer is allowed to start. An atomic acknowledgment confirms the
read itself, not merely thread creation. After the actual workload the consumer
is stopped and joined; the main thread captures the final publication and makes
it visible through a release/acquire handoff. Both readers must read that exact
snapshot and acknowledge its strictly newer revision before they join. This
proves **12 initial/final checkpoints** across the three phases. Every successful
read still runs the complete cross-field, FIFO/musical-state and monotonicity
oracle; every failed read must preserve all destination fields.

Ordinary reader attempts and producer posts still record observations of the
callback activity flag. These statistics have no required positive minimum.
They exclude the forced checkpoint reads and are not described as proof of
execution inside `render`. The free-running phase retains all 8,192 posts and
its rolling credit window without a per-callback handshake. Of the existing
16 overflow rounds, the first now waits for a callback to return before filling
the queue: it requires 256 accepted commands, pending closure and recovery on
the next callback. The other 15 retain concurrent bursts and complete outcome
accounting. The required controlled deferred count is one; flagged/deferred
race observations may both be zero.

Fresh coherent `649b12c7` plus the single test overlay passed **1/1 Release**
in **0.17 seconds total**, **1/1 Linux one-CPU Release** in **0.54 seconds**, and
**1/1 fully rebuilt ThreadSanitizer** in **0.89 seconds**, without a race
diagnostic. In the constrained execution, both readers observed **zero** activity
flags in the recovery and overflow phases, flagged/deferred overflow counts were
both zero, and all 5,760 raced late posts arrived after acknowledgment. Every
deterministic checkpoint and recovery/accounting requirement still passed.
No gate was retried, sleep added or eight-second watchdog extended. The
[reader-progress review](reviews/STANDALONE_READER_PROGRESS.md) and
[assignment 50](development/2026-11-13-next-phases/50-reader-progress.md) retain
the failure, exact counts, source identities, commands and qualification limits.
Hosted qualification of the assembled change remains separate.

## Retained recovery-boundary repair — assignment 46

The original test required a positive number of concurrent late posts to be
discarded. [Hosted Linux Release at `5b8e241`](reviews/STANDALONE_PLATFORM_FOLLOWUP.md)
showed that this particular race outcome need not occur: the consumer can finish
rendering before the producer runs again. A ready flag set before `render` does
not prove the consumer has captured its queue prefix or remains in the call.

The maintained repair retains 64 recovery epochs and the exact four-callback
musical/publication oracle. Four epochs establish controlled public-call
boundaries; the remaining sixty keep the actual concurrent late-post race:

| Schedule | Required result for 96 late attempts |
| --- | --- |
| Overflow pending; consumer held before render | All 96 return RecoveryPending; no accepted sequence. |
| Invalid payload queued; consumer held before render | All 96 are admitted, then discarded when the consumer rejects the earlier payload. |
| Overflow recovery already returned and acknowledged | All 96 are admitted above the published resolved sequence. |
| Consumer-rejection recovery already returned and acknowledged | All 96 are admitted above the published resolved sequence. |
| Sixty unscheduled race epochs | Every attempt is classified as pending, admitted-and-discarded, or accepted after acknowledgment; their total is exactly 5,760. |

Controlled counters remain separate from concurrent observations. No minimum is
required for one incidental race outcome. Every epoch still checks literal
controls, empty recovered holds, sticky faults, exact sequences and accepted =
applied + rejected + discarded. The 8,192-post free-running phase, two readers,
16 active-overflow rounds, 256 forced failed reads and unwind cleanup remain.

Fresh coherent builds of published `5b8e241` plus only the repaired test passed
**1/1 Release** in **0.13 seconds total** and **1/1 ThreadSanitizer** in
**0.75 seconds total**, with no race diagnostic. All 23 actual core/support/test
objects were instrumented in the latter; archive symbols and executable runtime
linkage were verified. [Assignment 46](development/2026-11-13-next-phases/46-concurrency-oracle.md)
and the [repair review](reviews/STANDALONE_CONCURRENCY_PORTABILITY.md) retain
exact hashes, commands, observed counts and exclusions. Hosted rerun remains a
separate gate; these checks establish no physical-device or deadline result.

## Retained original executed gate — assignment 22

Fresh SDK-free builds used Linux x86_64, GCC 14.2.0, CMake 4.4.4 and Python 3.12.14.
Final Release CTest passed **1/1**, 0.12 seconds (total 0.13); the complete
ThreadSanitizer build passed **1/1**, 0.96 seconds (total 0.97), with no race report.
Core and Session source remained frozen; all 20 relevant compilation commands
in the TSAN build carried `-fsanitize=thread`. Neither run linked SDL or a host SDK.

| Observed final execution | Release | TSAN |
| --- | ---: | ---: |
| Whole-control FIFO posts / free-running callbacks | 8,192 / 173 | 8,192 / 305 |
| Posts observing an active callback interval | 8,179 | 8,192 |
| Coordinated recovery epochs / callbacks | 64 / 256 | 64 / 256 |
| Recovery accepted = applied + rejected + discarded | 14,976 = 3,456 + 32 + 11,488 | Same |
| Immediate invalid posts / full-queue requests / pending posts | 64 / 32 / 3,104 | Same |
| Raced accepted posts discarded before acknowledgment | 3,072 | 3,072 |
| Raced posts accepted after acknowledgment | 0 | 0 |
| Active-callback overflows / deferred recoveries | 16 / 16 | 16 / 16 |
| Active-overflow accepted = applied + discarded | 4,176 = 80 + 4,096 | Same |
| Successful reader snapshots / busy reads preserving destination | 368,627 / 844 | 165,192 / 1,697 |
| Deterministic exhausted reads preserving destination | 256 | 256 |

Counts describe those original executions. Later hosted review identified the
original positive raced-discard threshold as an invalid scheduling assumption;
the current gate above replaces it with explicit boundary coverage and complete
classification. Assignment 50 additionally replaces incidental reader/overlap
requirements with the explicit publication checkpoints described above.

## Independent checks

- One main-thread producer, one audio worker and two separate snapshot readers
  exercise actual Session calls. Both readers prove initial/final publication
  progress through atomic acknowledgments. Lifecycle/destruction occurs only
  after joins; checkpoint snapshots remain immutable while readers use them.
- The free-running phase has only initial/final participation handshakes and
  no per-callback handshake. A rolling 128-command
  window avoids overflow while 8,192 accepted commands cross 32 full ring laps.
  Literal A/B patterns change every retained control, including all 36 drawbars;
  unique exact expression values identify each sequence. Every observed sequence
  must have its entire expected control value, not a hybrid of adjacent restores.
- Readers check valid controls, even monotonic revisions, monotonic sequence and
  diagnostic counts, applied <= resolved, finite peak, rate/lifecycle fields,
  and an independent exact frame-clock/revision relationship. Recovery readers
  additionally derive complete manual/pedal holds, controls and fault counts
  from the four-callback schedule; same-revision payloads must remain identical.
- Recovery setup is intentionally coordinated. Four controlled epochs now prove
  before/after-call boundaries, and sixty retain concurrent late admission.
  Whole-snapshot rejection, real invalid core payloads and all 256 queue
  slots are exercised. Queued independent-channel manual/pedal releases and stale
  note-ons are discarded safely. Literal prefix counts independently reconcile
  every accepted command as applied, consumer-rejected or discarded.
- Sixteen further overflow rounds retain exact sequences, literal controls,
  ownership release and accepted = applied + discarded. One explicitly waits
  for callback return before filling the queue and proves pending closure until
  the next callback. Fifteen race a positive callback and classify whether it
  acknowledged recovery or left it pending. Activity-flag/deferred observations
  remain statistics; no particular race outcome is required. The recovery
  callback releases all owners and resolves the suffix; no suffix notes reappear.
- Each phase ends with joined workers, a FIFO Panic, a zero-frame drain, an empty
  follow-up and stopped state. Failed reads compare every public field; forced
  publication exhaustion supplies deterministic failure checks alongside real busy reads.
  Fixed work and an off-callback eight-second watchdog bound stalled execution.

## Memory-order audit: source reasoning, separate from execution

In [`Session.cpp`](../apps/standalone/Session.cpp), the producer writes an ordinary
slot before its release CAS on `queue_state_`; the consumer acquires the captured
cursor before reading it. `consumed_cursor_` release follows the last slot read,
and producer acquisition precedes reuse. The 512-position cursor distinguishes
empty/full while preserving all 256 slots; lifetime command sequences do not wrap.

Commit and recovery closure share one atomic modification order. Rejection's
acquire/release `fetch_or` captures raced committed slots and closes admission.
Uncommitted producer writes remain outside that captured range. Acknowledgment
follows publication and flips an epoch bit, so a producer suspended across
closure cannot CAS its old open state successfully. With the sole producer
suspended, the emptied queue cannot generate a second command-driven recovery;
lifecycle requires quiescence and exhaustion remains latched.

All 22 snapshot payload words are atomic. Acquiring an even revision orders its
preceding payload stores before the reader. Seeing a later payload release also
orders that publication's preceding odd revision before the final revision load;
atomic coherence prevents accepting the older even revision. Nonwrapping revisions
avoid ABA. Readers commit only a locally unpacked successful copy. Engine/lifecycle
fields used outside atomics are audio-owned or stable throughout concurrent use.

These are bounded stress observations and a C++ ordering audit, not an exhaustive
interleaving proof. The one-CPU execution uses Linux affinity and is not a claim
about another operating system's scheduling. TSAN qualifies the identified
instrumented Linux run; weak-memory hardware,
other platforms, actual device/backend threads, callback deadlines and physical
fidelity remain unrun here. Allocation qualification is separately owned by assignment 21.
The original commands, source/archive identities and handoff remain in
[assignment 22](development/2026-11-13-next-phases/22-session-concurrency.md);
[assignment 50](development/2026-11-13-next-phases/50-reader-progress.md) owns
the current reader-progress qualification.
