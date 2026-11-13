# Assignment 30 — enabled pedal and host-boundary allocation audit

Owner: /root/w05_a30_enabled_realtime

Session: 2026-11-13 pedal development, wave 5, assignment 30 of 60.

## Scope and current position

Owned only `tests/test_realtime_pedals.cpp`,
[PEDAL_REALTIME.md](../../PEDAL_REALTIME.md), and this note. No production code,
CMake, shared status, manifest or other worker file was edited. This worker did
not commit, push or spawn agents; root owns integration and publication.

The allocation/timing gate is implemented and its complete isolated Release
run passed. It includes the frozen assignment-28 HostTimeline and assignment-29
StateExchange in one rebuilt library/test snapshot. The core APIs and proposed
complete callback were measured; no native SDK callback, host/device deadline
or all-platform gate is claimed by this assignment. The next phase is the
coordinator's full repository gate, followed by native wrapper integration and
actual native callback instrumentation.

Read `AGENTS.md`, current README/status/next steps/development log/plan, atlas
review and prior handoff, the complete pedal Engine and performance-input
contracts, the existing real-time contract and allocation-interposition test,
and the actual Engine/owner/control/timeline/exchange interfaces and relevant
implementations. Read atlas pp. 379–390 in full for callback budgeting, fixed
communication, preparation/lifetime, one clock, curve ownership and musical
state transfer. The complete 500-page source review is owned by earlier review
assignments; this note does not claim this worker independently reread all 500
pages.

Agent 28 supplied frozen header/source hashes after its independent oracle
suite passed. Agent 29 supplied frozen header/source hashes after its focused
Release test; its subsequent ThreadSanitizer qualification is separate evidence
in [assignment 29](29-state-exchange.md), not a run performed by this worker.
Root's Windows renderer Unicode correction and other wave-5 work were excluded
from this focused source snapshot to avoid live-source or layout mixing.

## Implementation and decisions

The test reuses only portable global C++ allocation interposition and the
explicit-overload calibration mechanism from the older console audit. Twelve
allocation/free pairs cover eight `new` overloads and all twelve `delete`
overloads. Each subsequent measured scope must individually observe zero
allocations and zero frees. All fixtures, copied references, profile loading,
state serialization/parsing, UI enqueue/save/read operations and assertions
remain outside audio probes.

Enabled Engine workloads include all 122 manual keys, 25 pedals/200 closed
contact positions, moving nominal contacts, routed percussion, 1024 dense
control/partial-key events and the 65,536-frame bound at each of 44.1/48/96 kHz.
The two owner adapters each reach 256 live identities; facade and timeline
fixtures reach 512 combined owners and exactly 147 physical notes. Accepted,
rejected, zero, disconnected, dense, overflow and stopped rate-lifecycle cases
have explicit consumption, state and future-audio expectations.

The short automation oracle supplies plain Engine with independently computed
`e[n]=1/4+3*n/64` and pedal position `round(n/2)` for 16 samples. It compares exact
samples and phases against HostTimeline and checks that offset-16 parameter and
musical events remain carry until the next accepted call. A separate long
ramp applies 65,536 expression sample values. Raw density and retained carry
both reach 1024; rejection preserves output and carry, and a zero-frame call
consumes carry once without advancing sources.

The complete measured callback includes `audio_peek`, `audio_can_commit`,
HostTimeline processing into a private output buffer, `audio_commit` with the
valid Engine control snapshot, atomic publication and final host copy. Four
queued parsed restores survive a deliberately rejected callback. The next
successful callback consumes all four, retains 512 owners, publishes actual
automated controls and renders audible output. Thirty-two later callbacks make
no UI read and alternate connected/disconnected output. Direct exchange probes
exercise stale/foreign tokens, invalid controls/limits, finite counter lifetime
and append-after-preflight preservation.

Snapshots compare typed values, all manual and pedal contacts, percussion,
last rendered pedal diagnostics, all 91 source phases, owners, curve anchors and
carry. They do not compare raw object padding. Future output checks after
rejection/disconnection are bit-exact. Output hashing and energy checks prevent
silent or unused work from masquerading as enabled-path evidence.

`steady_clock` measures finite nonnegative elapsed observations with no timing
pass threshold. Type assertions and header inspection establish fixed value
ownership; the contract documents object sizes, candidate-copy costs and finite
work bounds. Neither global C++ interposition nor the timings claim complete
`malloc`/system-call/lock coverage, cross-thread coverage or audio deadlines.

## Coherent source identity

Base published commit:
`6bcf35cd0c2a54eeb31fabfde8b40bdfcb5b1f51`.

Its `git archive` was extracted with Python `tarfile` using `filter='data'` into
`/workspace/scratch/f364bc93d920/a30-source`. The following four frozen
production files and this test were copied in, with hashes verified before
configuration. No old object library was reused with new headers.

| File | SHA-256 |
|---|---|
| `include/hammond/HostTimeline.h` | `690e88fc73602b7edc39133f1a27e100ce1e1427dfcaa4543f318c208f681f9d` |
| `src/HostTimeline.cpp` | `37941dc9d833cabc1ed7ca22327ad23240ea8c04e6de9fc3f447222d2ebb41dd` |
| `include/hammond/StateExchange.h` | `dfb4ec233f816edc223dfdf5b14da05cbca8a64534d5d725d307c2dff6d9933a` |
| `src/StateExchange.cpp` | `10a85957cad8e87e00f8ada543f697b9db4d59590b306baaae05fc0120a2a2bf` |
| `tests/test_realtime_pedals.cpp` | `b11b5857faeba3f34a37cee56da114e54ca80cbc21b89495d6abbd8ab644317b` |

Supporting unchanged identities:

- Engine header: `b2aea1dae1e54654cacb8576295b27d47673c87a9a01e17fd3eba7a843fa188c`.
- PerformanceInput header: `f3b4185393da324ab1433514f141e42aab1056d7dac4fd402184b1c2d0dd04ae`.
- PerformanceInput source: `fc9d3775ad1d3faf23beacb52c6c78108f967e8e7d209b74ef56e1a9caa44030`.
- Compiled `nominal.b3p`: `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.
- Release test executable: `c1023a67484f09d9d789f7f271594e0f8e4082e5094b5fba2e69783d5aac45ff`.
- Recorded CTest output log: `eb2fc1b6cbf0f1ef12cb7ae084e1a9c8d27bd31d6ae857cfbadfa632c2cffe61`.

The complete stimulus is the hashed test source. Nominal Engine seeds/origins
are 37/1000 (three rates), 87/700 (combined), 119/900 (short curve), 121/0
(maximum timeline) and 311/8000 (complete callback), plus the explicit
`UINT64_MAX-8` clock-overflow fixture. The profile compiler reported model
`nominal-unmeasured-v1`; its retained authoring identity is
`49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83`.
The pedal routing compiler checked 200 positions, 195 connected and five
explicit disconnected positions before building the core.

## Actual validation commands and results

Environment: Linux 6.18.57 x86-64, glibc 2.41; exposed CPU model Intel Xeon
Platinum 8573C; GCC 14.2.0; CMake 3.31.6; Python 3.12.14. Actual target flags:
`-O3 -DNDEBUG -std=c++20 -Wall -Wextra -Wpedantic -Wconversion
-Wsign-conversion -Wshadow -Werror`.

Successful final commands:

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake \
  -S /workspace/scratch/f364bc93d920/a30-source \
  -B /workspace/scratch/f364bc93d920/build-a30 -DCMAKE_BUILD_TYPE=Release
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake \
  --build /workspace/scratch/f364bc93d920/build-a30 \
  --target test_realtime_pedals -j 2
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/f364bc93d920/build-a30 \
  -R '^test_realtime_pedals$' -V \
  --output-log /workspace/scratch/f364bc93d920/a30-release-test.log
```

CTest passed **1/1 selected tests**, reported **0.76 seconds total**. The actual
measurement report is preserved here because the external build/log paths are
scratch rather than repository evidence:

```text
compiler=GCC-14.2.0 pointer_bits=64 clock=steady_clock timing=observed-only
calibration=12-allocations/12-frees (8-new-overloads,12-delete-overloads)
engine calls=58 accepted=41 rejected=17 frames=202091 records=3663 physical=3663 new=0 delete=0 elapsed_us=426078.546 max_us=159660.058
manual-owners calls=6 accepted=4 rejected=2 frames=0 records=1538 physical=1268 new=0 delete=0 elapsed_us=62.152 max_us=26.653
pedal-owners calls=7 accepted=5 rejected=2 frames=0 records=1538 physical=1074 new=0 delete=0 elapsed_us=61.109 max_us=28.770
combined calls=18 accepted=12 rejected=6 frames=67073 records=2052 physical=1318 new=0 delete=0 elapsed_us=132124.263 max_us=126539.550
timeline calls=16 accepted=10 rejected=6 frames=65636 records=3599 physical=65718 new=0 delete=0 elapsed_us=148346.764 max_us=147775.530
exchange calls=29 accepted=17 rejected=12 frames=0 records=3 physical=0 new=0 delete=0 elapsed_us=3.023 max_us=0.359
complete-callback calls=35 accepted=34 rejected=1 frames=3072 records=515 physical=1172 new=0 delete=0 elapsed_us=8110.812 max_us=3661.779
stopped-lifecycle calls=11 accepted=7 rejected=4 frames=0 records=0 physical=0 new=0 delete=0 elapsed_us=534.471 max_us=267.356
storage_bytes Engine=38664 NoteOwnership=3328 PedalNoteOwnership=2112 HostTimeline=416632 StateExchange=736 StateExchangeBatch=264 ControlSnapshot=56
audio_samples=335034 audio_hash=6c8e178dc115fd2a exact_audio_comparisons=881 phase_comparisons=7189
scope=calling-thread-global-C++-new/delete; no C-heap/locks/syscalls/SDK/device guarantee
```

There were **180 measured calls: 130 accepted and 50 rejected**. No production
change was needed to obtain the pass. Earlier audit-development failures were
corrected before this final snapshot: an initial syntax check treated the flat
200-bit pedal-contact array as nested; a dense partial-travel fixture had opened
all upper detector contacts, so key 96 was retained fully pressed to exercise
actual routed percussion; and a per-rate output-tail sentinel needed refilling
between iterations. The isolated core-only diagnostic then passed with 267,368
checked samples/checksum `2bbc489237c371da` before the complete 28/29 integration.
That diagnostic was not presented as the final full test.

Final owned-file UTF-8/LF, trailing-whitespace, internal-document-link and frozen
source equality checks were performed after documentation completion. CMake
already discovers this native test; no shared build edit was required.

## Limits and next action

These timings describe one instrumented shared-container run. No power/thermal
control, scheduling-tail study, actual host, audio driver, device underrun count,
thread migration test or physical recording was supplied. No all-allocator,
lock or system-call tracer was installed. Only the calling thread's global C++
replacements were measured. UI parsing/serialization and UI enqueue/save/read
calls were deliberately outside the audio probe. The test does not claim a
concurrent UI race proof; assignment 29 provides that separate argument/stress
evidence. Nominal pedal mixture gains and contact/percussion coefficients remain
unmeasured and require later acoustic/circuit calibration.

Root should include these three owned files with the frozen 28/29 dependency
set, run the complete repository gate, update shared status/manifest and
commit/push. The native wrapper must use the preflight-before-candidate and
publish-after-success order, retain all output privately until commit, allocate
buffers while stopped, and expand the same calibrated scope to the actual
native callback. Native bus/event validation and SDK calls need their own
allocation and lifecycle evidence; core success is not a substitute. Future
agents changing any covered audio path must rerun a coherent source/header
build and update the run identity, measured workload and remaining limits.
