# Assignment 29 — bounded concurrent control state exchange

Owner: /root/w05_a29_state_exchange

Session: 2026-11-13 pedal development, wave 5, assignment 29 of 60.

## Scope, current position and source basis

Implemented only `include/hammond/StateExchange.h`, `src/StateExchange.cpp`,
`tests/test_state_exchange.cpp`, [STATE_EXCHANGE.md](../../STATE_EXCHANGE.md) and
this record. Root owns CMake, combined qualification, shared status, commits and
pushes. This worker made no commit, push, shared-file edit or subagent spawn.

Read `AGENTS.md`, current project status/next steps, the preceding handoff,
relevant `ControlState`/`ControlStateIO`/Engine interfaces and the complete state
and lifecycle contract in [VST3_SPIKE_CONTRACT.md](../../VST3_SPIKE_CONTRACT.md),
sections 5–6. Relevant atlas reading covered concurrent control publication,
generation stress, state load/restore and retained identity on pp. 389–390,
393–394 and 400–401. The repository-wide atlas review belongs to the preceding
source-review assignments; this record does not claim a new independent reading
of all 500 pages.

The SDK-independent state handoff is implemented and its focused Release and
ThreadSanitizer tests passed. It is ready for the native processor's callback
transaction and the separately owned allocation/timing gate. A native plugin,
validator/host lifecycle pass or cross-platform run is not claimed here.

Root approved the public API and immutable finite-lifetime limits before freeze.
Agent 28's independent `HostTimeline` accepts up to four copied restores and
resets automation anchors; no circular header dependency was introduced.
Agent 30 received the frozen header and source before instrumentation.

## Decisions and proof obligations

- Four copied, validated UI snapshots use monotonically increasing accepted
  sequences. Full/invalid/exhausted enqueue preserves pending records and the
  newest UI save value. Plain slots have release/acquire publication and reuse
  ownership; peek does not consume.
- An opaque value-owned batch binds its origin, consumer range and publication
  revision. `audio_can_commit` checks every resource/token condition before
  candidate processing. UI appends cannot invalidate a valid token. Sole audio
  ownership and a valid Engine snapshot make post-success commit nonfailing.
- Audio publishes 45 control cells, both route bits and the acknowledged
  sequence through **48 atomic uint64 cells** and an atomic odd/even revision.
  Every publication operation is sequentially consistent; there is no plain
  payload seqlock. Compile-time assertions require lock-free 64-bit atomics and
  binary64. Readers attempt at most eight times and preserve destination on
  failure; a stalled reader owns no buffer and cannot stall audio.
- Save returns the newest accepted load while pending. After acknowledgement,
  each successful save uses the latest coherent audio publication, including
  automation. Parsing/serialization remain off audio in existing state I/O.
- Accepted-state and publication limits never wrap or reset. Maximum defaults
  are `UINT64_MAX` and `UINT64_MAX/2`; smaller limits exercise the identical
  exhaustion paths. An invalid publication limit fails closed. Destruction or
  object replacement requires actual producer/consumer quiescence.

The full ownership proof, SC total-order proof, field mapping, nonfailing commit
argument and caller preconditions are in [STATE_EXCHANGE.md](../../STATE_EXCHANGE.md).
These arguments accompany stress evidence; sanitizer success alone is not the
proof of correctness for every possible interleaving.

## Coherent inputs and actual commands

Created `/workspace/scratch/f364bc93d920/a29-source` from `git archive` of published
wave-4 commit **`6bcf35cd0c2a54eeb31fabfde8b40bdfcb5b1f51`**, then overlaid only the
three new code/test files. An initial configure using the entire live CMake file
failed because it referenced another W5 worker's `tools/pedal_trace.cpp`, absent
from the archived base. Replaced only the scratch CMake copy with the base
version plus root's approved focused `find_package(Threads REQUIRED)` and
`Threads::Threads` linkage for `test_state_exchange`. Live CMake remained owned
by root. Thus the successful gate excludes evolving unrelated W5 sources.

Toolchain: Linux, GCC 14.2.0, CMake 3.31.6, Python 3.12.14. Project warnings are
treated as errors. The first test compile identified a narrowing conversion in
a test's aggregate `PedalId`; an explicit bounded `uint8_t` conversion fixed it.
Production code compiled without changes. Actual successful commands:

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake \
  -S /workspace/scratch/f364bc93d920/a29-source \
  -B /workspace/scratch/f364bc93d920/build-a29 \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake \
  --build /workspace/scratch/f364bc93d920/build-a29 \
  --target test_state_exchange -j2
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/f364bc93d920/build-a29 \
  -R '^test_state_exchange$' --output-on-failure -V
```

**Release result: 1/1 selected test passed, zero failures, 0.04-second test time
(0.07-second CTest total).** The concurrency run reported 6,356 audio commits,
8,993 successful UI saves, 28,931 successful observer reads and 94,118 explicit
bounded read failures. These scheduling-dependent counts are observations;
the fixed acceptance requirements are exact complete snapshots, monotonic
acknowledgements/revisions and unchanged destinations on failure.

A minimal GCC ThreadSanitizer two-thread atomic probe compiled and ran with
exit zero, establishing that its runtime was usable here. Then rebuilt **all
core sources and this test** with sanitizer instrumentation from the same
frozen source copy:

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake \
  -S /workspace/scratch/f364bc93d920/a29-source \
  -B /workspace/scratch/f364bc93d920/build-a29-tsan \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo -DBUILD_TESTING=ON \
  '-DCMAKE_CXX_FLAGS=-fsanitize=thread -fno-omit-frame-pointer' \
  -DCMAKE_EXE_LINKER_FLAGS=-fsanitize=thread
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake \
  --build /workspace/scratch/f364bc93d920/build-a29-tsan \
  --target test_state_exchange -j2
TSAN_OPTIONS=halt_on_error=1 \
  /workspace/scratch/f364bc93d920/tooling/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/f364bc93d920/build-a29-tsan \
  -R '^test_state_exchange$' --output-on-failure -V
```

**ThreadSanitizer result: 1/1 selected test passed, zero failures, 0.49 seconds,
no sanitizer report.** This run observed 8,136 commits, 1,791 successful UI saves,
2,955 successful observer reads and 40,718 bounded read failures. No detector
suppression, custom synchronization annotation or disabled case was used.

## Acceptance evidence

Both builds executed the following same cases:

| Area | Executed requirement |
| --- | --- |
| Defaults and ownership | Initial coherent controls before audio; four copied records survive caller mutation; full queue preserves every pending state. |
| Transaction | Default/foreign/stale/empty-reused tokens reject; UI append after preflight preserves its success; rejected callback retains queued records and acknowledgement. |
| Exact controls | All 45 controls and two route bits round-trip; signed zero and adjacent expression values preserve bits; invalid enums, bars, pedal positions and nonfinite/out-of-range expression reject atomically. |
| Lifetime | Limits `(2,2)`, `(0,1)`, `(1,0)`, maximum defaults and invalid publication limits execute exact fail-closed/exhaustion paths without private mutation. |
| Old state | Versions 1/2 migrate with explicit percussion/pedal defaults; version 3 retains pedals; exact canonical v3 bytes save and parse again; future state versions reject before enqueue. |
| Engine history | Three held manual targets, two pedals, moving contacts and decayed readiness survive all three queued restores; all manual contacts, 200 pedal positions, 91 source phases, readiness, last pedal frame and clock compare exactly. |
| Candidate failure | Invalid event leaves output sentinel unchanged; candidate is discarded; live Engine and exchange remain unchanged. |
| Future output | A successful restore's next 128 samples and dynamic state match a separate Engine copy given the equivalent final restore exactly. |
| Delayed UI | 24,000 publications occur with no UI reads; the final successful read/save returns publication 24,000, revision 48,000. |
| Concurrency | One UI producer, one audio consumer and one atomic-only observer exercise 12,000 accepted snapshots; all accepted records arrive in order and all successful reads match complete generated values. |

Test-only thread scheduling yields and deadline checks are outside the production
algorithm; they are not audio waits. The test's final main-thread UI access
occurs after joining the producer, establishing a quiescent ownership transfer.

## Frozen files and next action

Live and isolated test inputs were SHA-256 compared after successful execution:

| File | SHA-256 |
| --- | --- |
| `include/hammond/StateExchange.h` | `dfb4ec233f816edc223dfdf5b14da05cbca8a64534d5d725d307c2dff6d9933a` |
| `src/StateExchange.cpp` | `10a85957cad8e87e00f8ada543f697b9db4d59590b306baaae05fc0120a2a2bf` |
| `tests/test_state_exchange.cpp` | `026a04e8734030a03b28e453d8009b947eccf8543032558de17dce8280037dfe` |

`git diff --check` passed at source freeze; per-file `git diff --no-index --check`
and explicit trailing-whitespace checks also passed for all five new owned
files. The selected tests are not a complete repository regression. Root must
integrate the focused Threads linkage, combine
the W5 frozen inputs, run the combined gate and record/publish the resulting
commit. No elapsed CTest time above is an audio-deadline or cross-platform claim.

The native adapter's next implementation step is: validate host buffer/input,
peek and preflight the exchange, process HostTimeline into private output with
the batch restores, publish/acknowledge only on success, then copy admitted host
audio. State load/save must use the serialized UI producer methods and existing
bounded parser/serializer outside audio. The instrumented real-time owner can
measure pending-state and empty-publication paths using the frozen API.

Future agents must retain the single producer/consumer contract, all-atomic
payload, finite nonwrapping lifetime and preflight order. Changing these is a
protocol change requiring an updated proof and corresponding concurrent gate;
replacing atomic payload cells with plain fields, caching a permanently stale
save fallback or acknowledging before callback success would invalidate this
qualification. Continue from the shared status/handoff and `AGENTS.md`, and let
the active integrator own shared publication/accounting.
