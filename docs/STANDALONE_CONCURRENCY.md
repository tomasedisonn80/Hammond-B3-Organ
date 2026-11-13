# Standalone Session concurrency acceptance

Assignment `/root/w04_a22_session_concurrency`, 13 November 2026, maintains
[`test_standalone_concurrency`](../apps/standalone/tests/test_standalone_concurrency.cpp)
against the actual [Session contract](STANDALONE_SESSION.md) and implementation.
No production code changed. This supplements [serial acceptance](STANDALONE_SESSION_ACCEPTANCE.md).

## Executed gate

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

Counts describe these executions and are printed by every run; scheduler-dependent
counts are not golden values. The test requires observed overlap and progress,
not a particular callback count, read-failure count or thread ordering.

## Independent checks

- One main-thread producer, one audio worker and two separate snapshot readers
  exercise actual Session calls. Lifecycle/destruction occurs only after joins.
- The free-running phase has no per-callback handshake. A rolling 128-command
  window avoids overflow while 8,192 accepted commands cross 32 full ring laps.
  Literal A/B patterns change every retained control, including all 36 drawbars;
  unique exact expression values identify each sequence. Every observed sequence
  must have its entire expected control value, not a hybrid of adjacent restores.
- Readers check valid controls, even monotonic revisions, monotonic sequence and
  diagnostic counts, applied <= resolved, finite peak, rate/lifecycle fields,
  and an independent exact frame-clock/revision relationship. Recovery readers
  additionally derive complete manual/pedal holds, controls and fault counts
  from the four-callback schedule; same-revision payloads must remain identical.
- Recovery setup is intentionally coordinated, then admission races the actual
  callback. Whole-snapshot rejection, real invalid core payloads and all 256 queue
  slots are exercised. Queued independent-channel manual/pedal releases and stale
  note-ons are discarded safely. Literal prefix counts independently reconcile
  every accepted command as applied, consumer-rejected or discarded.
- Sixteen further rounds fill the queue during a positive callback. Observed
  QueueFull calls inside active intervals leave recovery pending after that
  callback, proving these requests arrived after its captured prefix. The next
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
interleaving proof. TSAN qualifies this instrumented Linux run; weak-memory hardware,
other platforms, actual device/backend threads, callback deadlines and physical
fidelity remain unrun here. Allocation qualification is separately owned by assignment 21.
Exact commands, source/archive identities and handoff are in [assignment 22](development/2026-11-13-next-phases/22-session-concurrency.md).
