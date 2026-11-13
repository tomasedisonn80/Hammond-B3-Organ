# Enabled pedal and host-boundary real-time audit

`tests/test_realtime_pedals.cpp` measures the enabled core, both note-owner
adapters, the combined performance facade, `HostTimeline`, and the audio side
of `StateExchange`. The 2026-11-13 coherent Linux Release run passed **180
measured API regions with zero observed global C++ allocations and zero
observed global C++ deallocations in every region**. Its simulated complete
callback contains queue peek, commit preflight, timeline rendering, atomic
control publication and copying the completed samples to host output.

This is bounded core evidence. It is not a native SDK callback qualification,
a complete allocator/lock/system-call trace, an audio-device test or a promise
that a callback meets a deadline. The underlying pedal, contact and percussion
models remain declared nominal surrogates. See [PEDAL_ENGINE.md](PEDAL_ENGINE.md),
[PERFORMANCE_INPUT.md](PERFORMANCE_INPUT.md), [HOST_TIMELINE.md](HOST_TIMELINE.md),
[STATE_EXCHANGE.md](STATE_EXCHANGE.md) and the earlier
[REALTIME.md](REALTIME.md) console audit.

## What is measured

The test executable replaces the scalar and array global C++ `new`/`delete`
families, including nothrow, aligned and sized deletion forms. It reuses the
portable interposition mechanism from `test_realtime_console.cpp`; its musical
fixtures and semantic expectations are separate.

Before observing production calls, calibration performs **12 allocation/free
pairs**, covering all **eight allocation overloads and 12 deletion overloads**.
It includes zero-size allocation, non-alignment-multiple sizes, and 64-byte
aligned storage. Explicit calls through volatile function pointers prevent
new-expression elision from making calibration vacuous. The probe must report
exactly 12 allocations and 12 frees; it then resets for every measured region.

Only the calling thread's global C++ replacements are counted. Placement
construction, direct `malloc`/`free`, custom allocators that bypass these
replacements, system allocation, other threads, locks and system calls are not
interposed. Successful counts cannot establish the absence of those operations.
The static always-lock-free requirement on the state exchange's 64-bit atomics
is a separate production prerequisite; this allocation test does not replace
its concurrency proof or race tests.

Profile parsing, object construction, large object allocation, fixture arrays,
state parsing/serialization, UI enqueue/save/read operations, snapshots,
reference rendering, assertions, hashing and printed diagnostics all occur
outside the recorded audio regions. `HostTimeline` is heap-allocated once
before probing and retains its own fixed workspace. No destruction of that
owner occurs in a measured callback. Stopped sample-rate migration is measured
separately and is not represented as a concurrent device-rate protocol.

`std::chrono::steady_clock` surrounds each region. The test requires a monotonic,
finite, nonnegative observation and records the total and maximum observed
microseconds. It sets **no wall-time pass threshold**. These observations include
probe/timer overhead and do not establish worst-case timing, a latency budget,
complete timing distributions, host scheduling behavior or available device
underflow counters.

## Workloads and independent semantic checks

| Boundary | Work actually exercised | Checks beyond allocation counts |
|---|---|---|
| `Engine` | 44.1/48/96 kHz; all 122 manual keys and 25 pedals; nominal moving contacts and enabled percussion; 1024 dense control/partial-key events; 65,536-frame output; zero-frame flush; disconnected output; pedal panic; clock overflow | Exact input consumption and frame advancement; 200 pedal contact bits; active counts; partial manual travel; routed percussion with changing readiness; finite, nonzero-energy audio; output tail preservation; all 91 source phases |
| Manual ownership | 256 simultaneous identities over 122 physical keys; duplicate identities; scoped panic; 1024 anonymous on/off transitions | Exactly 122 first-owner onsets, 122 final-owner releases and 1024 dense transitions; identity/capacity failures leave the owner table and destination intact |
| Pedal ownership | 256 identities over 25 pedals, split across two origin buses; duplicate identities; two scoped panics; 1024 anonymous transitions | Exactly 25 first-owner onsets; clearing the first bus preserves all pitches owned by the second; final panic emits 25 individual releases; destination tails and owners survive rejection |
| Combined facade | Both full owner tables, 512 owners total; 147 physical notes; 1024 control events; disconnected output; maximum block; scoped panics | Exact raw and physical counts; a late invalid control cannot release either early owner; capacity/buffer/block failures preserve both adapters and the Engine; future audio remains bit-identical |
| `HostTimeline` | Expression and discrete pedal automation; offset-N parameter and musical carry; 512 owners; 65,536-frame sampled expression; 1024 duplicate raw points and 1024 boundary carry records; zero/disconnected callbacks; rate/max-block migration | Independent 16-sample closed-form ramp rendered through plain Engine; exact audio and retained last-sample anchors; carry survives rejection and is consumed once; maximum-work accounting; owner/state/output preservation |
| `StateExchange` audio methods | Empty and full four-state batches; peek/preflight/commit; stale and foreign tokens; invalid snapshot; append after preflight; finite sequence/publication lifetime; invalid limits | Failed commits preserve publication and pending save state; a producer append remains pending after the prior batch commits; exact acknowledgements and publication revisions |
| Complete proposed callback | Four parsed pending restores, 512 note owners, sampled expression, candidate output, commit/publication and host copy; rejected callback; zero-frame carry; 32 subsequent callbacks with no UI reads, alternating connected/disconnected output | Rejection leaves all four states pending and host output untouched; successful callback acknowledges all four and publishes actual automated controls; no duplicated render time; 34 accepted/one rejected callbacks |

The short automation oracle has expression
`e[n] = 1/4 + 3*n/64` and pedal mixture-two position `round(n/2)` for
`0 <= n < 16`. Its endpoint at 16 is not rendered until the next callback.
A separately prepared plain Engine receives these known sample values directly;
it does not call `HostTimeline` or reuse its interpolation implementation.

For rejection and disconnected-state checks, reference value copies are made
before the measured call. Assertions inspect musical controls, both manual
contact banks, all pedal contact bits, percussion diagnostics, last rendered
pedal diagnostics, all 91 phases, owner tables, curve anchors and carry where
applicable. Several rejected Engine/facade calls are followed by successful
rendering and bit-for-bit comparison against the preserved reference. The
measured output stream is additionally checked for finite samples and nonzero
energy when audible, and its float bit patterns contribute to a deterministic
run checksum. Raw object padding is not used as a state-equality oracle.

## Fixed storage and work bounds

The source definitions contain value-owned profiles, arrays and scalar state;
there is no owning heap pointer in Engine, either note adapter, or HostTimeline.
Compile-time assertions require those types, musical snapshots, input variants
and state-exchange batches to remain trivially copyable. `StateExchange` itself
is noncopyable because it owns atomics. The header inspection and type checks
support the fixed candidate-copy reasoning; trivial-copyability alone would not
prove ownership for an arbitrary pointer-containing type.

These are actual `sizeof` values from the recorded GCC 14.2.0 Linux x86-64 build,
not portable ABI requirements or resident-memory measurements:

| Type | Bytes |
|---|---:|
| `Engine` | 38,664 |
| `NoteOwnership` | 3,328 |
| `PedalNoteOwnership` | 2,112 |
| `HostTimeline` including live/candidate state and internal output | 416,632 |
| `StateExchange` | 736 |
| `StateExchangeBatch` | 264 |
| `ControlSnapshot` | 56 |

Each note ledger has 256 slots. The facade admits at most 1024 raw records and
1024 emitted physical events, uses fixed candidate ledgers and a fixed event
array, and calls Engine once. Per-record translation still copies the active
ledger and can scan/compact its bounded owner array; zero allocation does not
make that work free.

HostTimeline admits at most 45 parameter queues, four restores and 1024 total
fresh/carry raw records. Its live and candidate states, two retained carry
arrays, 1024-event work array and 65,536-float output array are already owned.
It copies the Engine once into candidate storage and once back after success;
internal render slices do not copy the whole HostTimeline. It previews musical
ownership before rendering and translates accepted notes again into candidate
state. Each translation uses the existing bounded owner adapter.

For positive `N`, at most `45*N` parameter evaluations can emit controls, and a
single musical record can conservatively emit at most 122 manual releases.
Thus `45*max(N,1) + 122*1024` is a loose finite upper bound on generated physical
records for one admitted call, not an event capacity silently imposed on the
whole reconstructed curve. Fixed internal slices retain all admitted events and
sum to exactly `N` elapsed frames. At `N=65536`, this loose bound is 3,074,048
records. The audit's long single-parameter ramp applies 65,536 sample values.

The state queue has four copied snapshots. Audio peek copies at most four;
publication encodes 48 fixed cells, writes an odd revision, those cells, then an
even revision. The audio methods have no retry loop. The independent observer
reader has at most eight attempts, each using fixed atomic cells; its work and
concurrency correctness are documented in
[STATE_EXCHANGE.md](STATE_EXCHANGE.md). The complete callback test includes the
audio publisher, while UI serialization and publication reads stay outside the
allocation region.

## Recorded Release observation

The source snapshot is published baseline
`6bcf35cd0c2a54eeb31fabfde8b40bdfcb5b1f51` plus the frozen assignment-28 and -29
headers/sources and this test. All were copied before configuration and the
library was rebuilt from that snapshot. It deliberately excludes the separate
renderer Unicode fix and other concurrent work. Exact hashes and commands are
in [assignment 30](development/2026-11-13-pedals/30-enabled-realtime.md).

The run used Linux 6.18.57 x86-64/glibc 2.41, an exposed Intel Xeon Platinum
8573C CPU model, GCC 14.2.0, CMake 3.31.6, Python 3.12.14, and
`-O3 -DNDEBUG -std=c++20` with project warnings treated as errors. This shared
container description is not a qualified minimum hardware, OS/host/driver,
power/thermal or audio-device configuration.

| Measured region | Accepted / rejected | Elapsed frames | Consumed records | Physical events | Observed total µs | Observed max µs |
|---|---:|---:|---:|---:|---:|---:|
| Engine | 41 / 17 | 202,091 | 3,663 | 3,663 | 426,078.546 | 159,660.058 |
| Manual owners | 4 / 2 | 0 | 1,538 | 1,268 | 62.152 | 26.653 |
| Pedal owners | 5 / 2 | 0 | 1,538 | 1,074 | 61.109 | 28.770 |
| Combined facade | 12 / 6 | 67,073 | 2,052 | 1,318 | 132,124.263 | 126,539.550 |
| Host timeline | 10 / 6 | 65,636 | 3,599 | 65,718 | 148,346.764 | 147,775.530 |
| State exchange methods | 17 / 12 | 0 | 3 | 0 | 3.023 | 0.359 |
| Complete callback | 34 / 1 | 3,072 | 515 | 1,172 | 8,110.812 | 3,661.779 |
| Stopped lifecycle | 7 / 4 | 0 | 0 | 0 | 534.471 | 267.356 |

Every row measured **zero allocations and zero deallocations**. “Frames” counts
elapsed DSP frames, so the owner translators report zero even when their input
validation receives a positive frame bound. Timeline/callback record totals
include consumed carry. Exchange records count consumed queued snapshots only
for the separate direct commit probes; the four restores inside the complete
callback are checked separately, not mislabeled as musical input records.
Nested Engine calls are not separately added to the Engine measurement row.

The executable checked 335,034 audio samples, produced checksum
`6c8e178dc115fd2a`, performed 881 exact audio comparisons and 7,189 source-phase
comparisons. Calibration was 12 allocations/12 frees. CTest reported one selected
test passed, 0.76 seconds total. Checksum equality is evidence for this compiler,
profile and stimulus; it is not a mandated cross-platform transcendental-result
ABI. Timings may change on every run and are not pass/fail thresholds.

## Reproduction and next gate

From a coherent checkout containing these changes:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --target test_realtime_pedals --parallel 2
ctest --test-dir build -R '^test_realtime_pedals$' -V
```

CMake already discovers `tests/test_*.cpp`; no production build-system edit is
required for this test. Rebuild the library and test together after any public
layout change. Future agents changing an enabled audio path should preserve the
calibrated probe, add the new path to meaningful finite workloads, rerun the
coherent gate, and update the evidence/limitations rather than carrying these
old measurements forward as current results.

The next step is the coordinator's complete repository gate and then the native
host adapter: allocate the full timeline/host buffers while stopped, validate
host-owned buffers and event/state capacities before mutation, preflight the
state batch before processing, publish only after successful rendering, and
copy output only after the guaranteed commit. Repeat the allocation scope around
the **actual native callback**, including its event collection, SDK conversion,
bus routing and error handling. Native SDK/validator builds, cross-platform
callback traces, lock/system-call instrumentation, device deadline/underflow
measurements and physical pedal calibration remain separate gates.
