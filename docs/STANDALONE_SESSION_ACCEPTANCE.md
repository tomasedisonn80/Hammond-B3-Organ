# Standalone Session acceptance

[`test_standalone_session.cpp`](../apps/standalone/tests/test_standalone_session.cpp)
executes the actual SDK-free [`Session.cpp`](../apps/standalone/Session.cpp)
against the [frozen Session contract](STANDALONE_SESSION.md). The observed
13 November 2026 Linux Release run passed **1/1 CTest suites**, zero failures.
The [assignment evidence](development/2026-11-13-next-phases/16-session-acceptance.md)
records the exact source, profile, binary and toolchain identities.

## Independent oracle and observable boundaries

The oracle is a separately prepared direct `Engine`. Each scenario explicitly
declares its expected physical note/control timeline. It does not reuse the
Session command dispatcher, inspect private queue/owner state, or translate its
own expected events with Session's ownership processors. The test compares
every rendered float by its exact bits against both stereo channels, checks
guard samples, and compares every published control and physical held target,
sample rate, frame clock and peak. Future audio probes expose hidden phase,
percussion-history or stale-owner changes that an immediate snapshot could miss.

All assertions remain active in Release. Each score uses the same absolute
command boundaries at 44,100, 48,000 and 96,000 Hz. Large, one-frame and irregular
`7/13/64/127` partitions are split at those boundaries; therefore the partition
comparison does not move the UI's specified callback-time events.

| Gate | Executed assertions |
| --- | --- |
| Initial/default state | Revision-zero unprepared snapshot, nominal muted controls at all three rates, stopped preparation, lifecycle rejection order, and silent clock advancement. |
| Exact audio | Nine rate/partition scores, literal bit-identical L/R copies, guarded output bounds, positive/zero peak semantics, and an admitted two-manual fixture with peak above one to detect clipping. |
| FIFO/copy/restore | Complete four-bank/percussion/pedal restores, copied caller payloads, scalar edits after restores, interleaved On/Off/scoped release/Panic/new On, no source advance on repeated zero-frame flushes, and accepted-versus-published sequence distinction. |
| Ownership | Separate UI gestures on one key, identified repeats, both manuals and pedal origins, independent non-UI channels, repeated scoped release, final-owner release, anonymous repeated owners, velocity-zero release, routing-only Cancel and global Panic. |
| Lifecycle | Precharged stop/start retains controls, phase/readiness and clock; stop discards pending commands and clears owners; repeated stop is idempotent musically. Eight invalid specs and three invalid profiles preserve the stopped queue and future output. Successful reprepare at all rates resets DSP/defaults and retains lifetime sequences, faults and discard accounting. |
| Producer rejection | Nonzero offsets, forbidden physical Event kinds and invalid complete snapshots reject with sequence zero; valid queued commands survive; diagnostic counts and future output agree. |
| Render admission | Unprepared/stopped/block/output/timeline precedence, exact output-length validation, untouched caller buffers and pending commands, future phase parity, maximum supported block, and zero-frame commands at `UINT64_MAX`. |
| Queue pressure | Exactly 256 usable slots; the failed 257th note-off, restore or Panic never receives a sequence. Invalid rendering cannot acknowledge recovery. `RecoveryPending` persists until a valid boundary; accepted discards resolve without becoming successful load acknowledgments. Two further full batches exercise reuse and cursor laps after recovery. |
| Consumer rejection | Fifteen invalid payload/identity scenarios and the 257th simultaneous manual or pedal owner after both independent 256-owner namespaces are filled. Earlier applied expression survives, the suffix is discarded, all held targets clear, error status remains sticky and subsequent accepted notes produce the expected future audio. |
| Finite limits | Command allowances 0/2/4, exhaustion while playing or stopped, no sequence reuse after prepare, publication allowances 0/1/3/4, invalid overlarge publication limit, last-allowed success and permanent exhausted admission. Failed snapshot reads preserve the complete destination rather than returning a stale acknowledgment. |

Observed deterministic totals: **3,277 successful renders; 156,308 stereo float
comparisons; 6,432 partition sample comparisons; 7,160 successful snapshot
reads; 3,850 accepted posts; 41 rejected posts; 20 ordinary rejected renders;
61 future-output probes**. Publication-exhaustion rejection checks are additional
explicit assertions and are not included in the ordinary rejection counter.
The filtered CTest run took 0.34 seconds on this runner; that duration is not a
callback deadline measurement.

## Reproduce

From the repository root, with CMake 3.21 or newer, a C++20 compiler and Python
3.10 or newer:

```sh
cmake -S . -B ../build-session-tests -DBUILD_TESTING=ON -DCMAKE_BUILD_TYPE=Release -DHAMMOND_BUILD_STANDALONE=OFF
cmake --build ../build-session-tests --target test_standalone_session -j 4
ctest --test-dir ../build-session-tests -R '^test_standalone_session$' --output-on-failure --no-tests=error -V
```

The target uses the repository's strict warning configuration and links the
standalone support/core archives without SDL2 or a host SDK. Construction,
profile loading, vector allocation and lifecycle calls in this test all occur
on the single test thread; no claim about their callback admissibility follows.

## Separate remaining gates

This suite deliberately does not replace the later concurrent-producer/reader,
capture-boundary race, allocation-hook, race-detector or callback-deadline
assignments. Its successful copied snapshots are observed without contention.
After publication exhaustion the public interface intentionally makes snapshots
unavailable and all future rendering fails; these tests assert that observable
contract rather than claiming access to the unpublished emergency-panic state.
The no-wrap counter implementation and hidden emergency release still require
the corresponding source/concurrency review.

Actual audio devices, SDL callback transport, desktop interaction,
accessibility, platform qualification, physical latency and measured instrument
fidelity remain separate product gates. The audio oracle is the existing nominal
dry Engine, not a measured B-3/AO-28/Leslie reference.
