# Standalone reader participation and scheduler-independent progress

Assignment `/root/w09_a50_reader_progress` repairs the concurrency test's
remaining incidental overlap requirements. Session, Engine, production memory
ordering and public interfaces are unchanged. The maintained
[concurrency guide](../STANDALONE_CONCURRENCY.md) describes the current gate;
[assignment 50](../development/2026-11-13-next-phases/50-reader-progress.md)
retains the exact source identities and reproduction commands.

## Observed failure and complete positive-expectation audit

Root's hosted audit of published commit
`649b12c7d1faa7601fde1019e913347c65a6634a`, tree
`cf63327d857b02029e8c5c6f406cab3d3c6890d1`, retained the Linux Release
[job 132232481835](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43526206646/job/132232481835)
failure: **89/90 suites passed** in **71.21 seconds**; the concurrency test
failed `CHECK(reader.active_reads > 0)` at its former line 328. Its portable
exception-unwind stop/join probe had passed. Other platform/native successes
do not make that positive requirement portable. This assignment did not rerun
the old source until it failed or substitute a local reproduction for the
retained hosted failure.

The audit found three related scheduling assumptions and two reader-progress
checks without a participation handshake:

| Former expectation | Reason it was not guaranteed | Current evidence |
| --- | --- | --- |
| Each reader has a successful read and more than one revision | A created/ready thread can remain unscheduled until work is complete. | Every reader must acknowledge coherent, exact initial and final snapshots, whose revisions differ. |
| Every reader has `active_reads > 0` | A reader can run between all callbacks. The flag is stored before the public call and cleared after it. | Keep the observed statistic; require exact publication progress separately. |
| Free-running `overlapping_posts > 0` | The producer may run only while the flag is false; neither producer nor consumer owes the test a chosen interleaving. | Preserve 8,192 posts, sequence-specific controls and full FIFO reconciliation; report flag observations without a positive threshold. |
| `deferred_overflows > 0` | The counter additionally requires observing the activity flag around QueueFull; all valid bursts may happen after callback return. | One of the existing 16 rounds explicitly overflows after return and must remain pending until the next callback; 15 retain the race. |

A positive flag observation also cannot prove a call-internal overlap: the
consumer may be suspended between setting the flag and entering `render`, or
after return before clearing it. No pre-render pause is reported as an in-call
read. Zero flag observations are valid. This is separate from the existing
[assignment 46 repair](STANDALONE_CONCURRENCY_PORTABILITY.md), whose four
controlled recovery boundaries and sixty raced epochs are preserved exactly.

## Deterministic reader progress with public calls

Each phase captures its initial public snapshot before constructing the reader
threads. Both readers perform a single `read_snapshot`, run the complete oracle,
compare every snapshot field to that immutable initial value, and release an
atomic acknowledgment. The main thread acquires both acknowledgments before
permitting the consumer and producer workload to begin. A ready-thread count
alone cannot release that gate.

After the workload, the consumer stops and joins before the main thread captures
the final public snapshot. A release store to `final_ready` makes that otherwise
ordinary immutable snapshot visible to the readers. Each reader acquires the
flag, performs its own single public read, runs the same coherence/monotonicity
oracle, requires full equality with the final snapshot, and acknowledges the
exact newer revision. The main thread waits for both acknowledgments and joins
the readers before inspecting their non-atomic statistics.

The stable checkpoint reads are excluded from the activity-flag statistic.
Ordinary observations continue between the two checkpoints. Every successful
read checks exact frame-clock/revision agreement, complete controls, holds,
sequence ordering, diagnostics and same-revision payload equality. Every busy
read checks that every destination field is unchanged. All new main-thread
coordination polls use the existing deadline; the off-callback eight-second
watchdog and portable unwind probe remain unchanged. There are no added sleeps,
timeouts, private-state hooks or test retries.

In the first overflow round, the producer waits for the public callback to
return before submitting the existing burst. Exactly 256 commands must enter
the queue; QueueFull closes admission, the already completed callback cannot
have resolved those commands, subsequent probes must return RecoveryPending,
and the next callback must recover them with empty holds and exact accounting.
Its required controlled-deferred counter is one. The other 15 bursts remain
concurrent and retain both permissible recovery outcomes and all literal
control/sequence/hold assertions.

## First-run coherent qualification

Archived the named published commit, overlaid only the repaired test and built
fresh SDK-free Release and TSAN trees. All **842 inventoried source files**
retained their bytes and modes. Release ran once at normal affinity and once
through Linux `taskset -c 0`; CPU 0 belonged to the original permitted set
0–8, and CTest and its child threads inherited that single-CPU constraint.
TSAN then rebuilt the core, Session support and test from the same source.
No unchanged failed acceptance gate was retried.

Linux x86-64, kernel 6.18.57, glibc 2.41, GCC 14.2.0, CMake/CTest 4.4.4,
Make 4.4.1, Python 3.12.14 and C++20 project warnings with `-Werror`.
SDL and VST3 remained OFF.

| Observed workload | Release | One-CPU Release | TSAN |
| --- | ---: | ---: | ---: |
| CTest result / total seconds | 1/1 pass / 0.17 | 1/1 pass / 0.54 | 1/1 pass / 0.89 |
| Ordered posts / free callbacks | 8,192 / 468 | 8,192 / 176,706 | 8,192 / 484 |
| Posts observing activity flag | 8,166 | 8,064 | 8,192 |
| Recovery epochs / callbacks | 64 / 256 | 64 / 256 | 64 / 256 |
| Recovery accepted = applied + rejected + discarded | 15,072 = 3,648 + 32 + 11,392 | 17,952 = 9,408 + 32 + 8,512 | 15,072 = 3,648 + 32 + 11,392 |
| Controlled pending / discarded / after-ack accepted | 96 / 96 / 192 | 96 / 96 / 192 | 96 / 96 / 192 |
| Concurrent pending / discarded / after-ack accepted | 2,880 / 2,880 / 0 | 0 / 0 / 5,760 | 2,880 / 2,880 / 0 |
| Immediate invalid posts / queue overflows / pending posts | 64 / 32 / 3,008 | 64 / 32 / 128 | 64 / 32 / 3,008 |
| Overflow rounds / callbacks / controlled deferred | 16 / 48 / 1 | 16 / 48 / 1 | 16 / 48 / 1 |
| Flagged QueueFull / flagged deferred observations | 15 / 15 | 0 / 0 | 15 / 15 |
| Overflow accepted = applied + discarded | 4,176 = 80 + 4,096 | 4,176 = 80 + 4,096 | 4,176 = 80 + 4,096 |
| Coherent reads / busy reads preserving destination | 478,837 / 1,430 | 58,502 / 128 | 145,718 / 1,266 |
| Required exact initial/final checkpoint reads | 12 | 12 | 12 |
| Forced exhausted reads preserving destination | 256 | 256 | 256 |

Both readers independently acknowledged the following revisions. These are
actual observed endpoints, not fixed expected callback counts:

| Phase | Release | One-CPU Release | TSAN |
| --- | --- | --- | --- |
| Free-running | 4 → 940 | 4 → 353,416 | 4 → 972 |
| Recovery | 4 → 516 | 4 → 516 | 4 → 516 |
| Overflow | 4 → 100 | 4 → 100 | 4 → 100 |

The constrained execution directly exercises a previously rejected legal
schedule: **both readers recorded zero activity-flag attempts in the recovery
and overflow phases**, all sixty raced recovery epochs admitted their late
posts after acknowledgment, and all flagged/deferred overflow observations
were zero. The exact checkpoints, controlled boundaries and complete outcome
oracles passed. Free-running callback counts remain scheduler-dependent; this
experiment is not a callback-deadline or device-performance measurement.

All **23 actual compiled objects** carried `-fsanitize=thread
-fno-omit-frame-pointer`: 19 core units, Session, UI model, state files and the
test. Compiler output paths were matched against existing objects. Both static
archives reference TSAN and the executable links `libtsan`.
`TSAN_OPTIONS=halt_on_error=1` was used; no race diagnostic or suppression was
reported/configured. The first auxiliary source-inventory audit assumed there
would be no generated files and rejected two new Python bytecode caches from
profile compilation. The corrected audit records those additions explicitly
and verifies all 842 original paths, bytes and modes. No source or successful
configure/build/test result changed, and no test fixture needed repair.

## Required next gate and limits

Root must build and execute the focused suite from its assembled frozen source,
publish the reviewed change, then inspect actual Linux/macOS/Windows jobs.
This worker changed only its four assigned files and did not commit or publish.
The Linux affinity execution covers one observed legal serial schedule; it is
not exhaustive scheduling coverage or an affinity result on another OS. TSAN
qualifies the identified instrumented run. Weak-memory hardware, native device
threads, callback deadlines, physical audio fidelity and whole-product release
remain separate qualification requirements.
