# Assignment 28 — bounded host automation and musical timeline

Owner: /root/w05_a28_host_timeline

Session: 2026-11-13 pedal development, wave 5, assignment 28 of 60.
The assigned implementation and focused qualification are complete. Integration,
shared status/accounting, commits and pushes belong to the root agent. This
worker made no commit, push, shared-file edit or child-agent dispatch.

## Scope, source basis and present position

Owned files are `include/hammond/HostTimeline.h`, `src/HostTimeline.cpp`,
`tests/test_host_timeline.cpp`, [HOST_TIMELINE.md](../../HOST_TIMELINE.md) and
this evidence note. The implementation uses only existing Engine, parameter and
ownership interfaces. No native SDK dependency, CMake change, core/facade edit,
renderer modification or saved-state migration was introduced.

Read the standing `AGENTS.md` instructions, current next steps/project plan,
the entire [VST3_SPIKE_CONTRACT.md](../../VST3_SPIKE_CONTRACT.md), the existing
PerformanceInput/owner contracts and implementation, ParameterBridge, Engine
and the pinned SDK parameter-change declaration. The spike contract records
the atlas product basis on pp. 379–402 and 450 and its earlier source reviews.
This worker does not claim a new independent review of all 500 atlas pages.
The timeline is declared software host policy, not measured Hammond behavior.

Root approved the owning API and boundary ordering before freeze. An owning
Engine can remain prepared for the hard 65,536-frame limit while separately
enforcing a host's active callback maximum, so a stopped setup change need not
restart the instrument. Root also approved direct use of both owner adapters
to fill bounded physical slices, with zero-frame flushes for dense same-sample
panic expansion. The existing unified single-call facade remains unchanged.

The model ID is `bounded-linear-host-timeline-v1`. The public header exposes
borrowed queue/point views, a manual/pedal variant, value-owned carry diagnostics,
an optional restore span and explicit consumption/Engine-call counters. No
host pointer survives a callback. The header, implementation and focused test
were frozen and sent to root and assignment 30 before their combined work.
Assignment 29's four-snapshot batch integrates through an independent span;
there is no circular header dependency.

## Implemented behavior and decisions

- All 45 stable IDs retain their existing mapping. Queues reject duplicate IDs,
  unknown IDs, nonfinite/out-of-range values, negative/decreasing/out-of-range
  offsets and over-capacity raw work. Same-offset points use last supplied value.
- Previous rendered normalized values anchor sample `-1`. Continuous and
  discrete controls both interpolate before exact ParameterBridge mapping.
  Offset-`N` parameter points shape the current ramp and remain next-boundary
  points; the retained anchor is the actual value at `N-1`.
- Every raw endpoint record, including duplicate parameter points, occupies
  carry capacity. Old carry plus fresh points and music may not exceed 1,024.
  Zero-frame input applies zero once, consumes old carry and creates no new carry.
- Restores apply first and reset anchors. Per-ID carried points precede fresh
  points. Evaluated controls use stable ID order before all notes; carried notes
  precede fresh ties. Explicit same-value selector points may reconnect Cancel;
  an absent queue cannot. These cross-domain tie rules were clarified by root
  in the shared spike contract.
- Complete owner preview validates even future boundary notes before candidate
  rendering. Candidate Engine, owners, anchors, carry and private mono output
  isolate every slice. A failure preserves live state, caller samples and all
  consumption counts. Physical slices hold at most 1,024 emitted events;
  positive slice lengths sum to exactly `N`.
- Four or fewer valid snapshots restore controls while retaining held owners,
  physical contacts, percussion readiness, phases and clock. Stopped rate/block
  reconfiguration preserves that same history and pending carry. Preparation
  alone establishes a new epoch.

The full admission/error precedence, curve equation, fixed-storage proof,
boundary examples and state-queue commit sequence are in
[the API contract](../../HOST_TIMELINE.md). The native wrapper must preflight
`StateExchange::audio_can_commit` before processing and publish/acknowledge only
after success, with no intervening sole-consumer operation. Under the exchange's
proof, UI appends cannot invalidate that preflight and the final valid Engine
snapshot cannot introduce a new commit failure. Native-private audio is copied
to host channels after publication.

## Coherent source and toolchain

The isolated copy `/workspace/scratch/f364bc93d920/a28-source` was created from
published wave-4 commit **`6bcf35cd0c2a54eeb31fabfde8b40bdfcb5b1f51`**, tree
`1c0f6bc62fbc2ff09f1fc9088cc301970daa8b9d`, using `git archive`, then overlaid
only this assignment's three C++ header/source/test files. It excludes active
assignments 25–27 and 29–30 and the root's renderer repair. All libraries and
tests were built against this one source copy. The base CMake source/test globs
discover the new files without a build-system edit.

Toolchain: Linux, GCC 14.2.0, CMake 3.31.6, Python 3.12.14, C++20, existing
warnings-as-errors including conversion and shadow checks. The CMake/CTest
executables were under
`/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/`.

| Frozen file | SHA-256 |
| --- | --- |
| `include/hammond/HostTimeline.h` | `690e88fc73602b7edc39133f1a27e100ce1e1427dfcaa4543f318c208f681f9d` |
| `src/HostTimeline.cpp` | `37941dc9d833cabc1ed7ca22327ad23240ea8c04e6de9fc3f447222d2ebb41dd` |
| `tests/test_host_timeline.cpp` | `170aaf29d77e0cd8524cd2b8547df6886a04f5c04f9bfd65b92828cdb1b89538` |

## Actual commands and results

The initial core-only Release build passed. The first focused test compile
identified one shadowed local in the test's carry-comparison helper. Renamed
the local; no production change was required. The strict focused build and test
then passed. Actual successful commands, using the executable directory above:

```sh
cmake -S /workspace/scratch/f364bc93d920/a28-source \
  -B /workspace/scratch/f364bc93d920/build-a28 -DCMAKE_BUILD_TYPE=Release
cmake --build /workspace/scratch/f364bc93d920/build-a28 \
  --target test_host_timeline -j 2
ctest --test-dir /workspace/scratch/f364bc93d920/build-a28 \
  -R '^test_host_timeline$' --output-on-failure
/workspace/scratch/f364bc93d920/build-a28/test_host_timeline
cmake --build /workspace/scratch/f364bc93d920/build-a28 \
  --target test_performance_input test_note_ownership \
  test_pedal_note_ownership -j 2
ctest --test-dir /workspace/scratch/f364bc93d920/build-a28 \
  --output-on-failure \
  -R '^(test_host_timeline|test_performance_input|test_note_ownership|test_pedal_note_ownership)$'
```

Focused Release result: **1/1 passed, zero failures, 0.38 seconds CTest total**.
The final four-suite gate passed **4/4, zero failures, 0.46 seconds**:

| Suite | Result |
| --- | --- |
| `test_host_timeline` | Passed, 0.35 s. |
| `test_note_ownership` | Passed, 0.03 s. |
| `test_pedal_note_ownership` | Passed, 0.00 s. |
| `test_performance_input` | Passed, 0.08 s. |

The new suite's actual output was:

```text
host timeline: accepted=4759, oracle_frames=9216, phase_values=11648, exact_samples=22401, rejections=43, future_probes=39, threshold_cases=933, partitions=21, max_audio_error=0, max_curve_error=0, sizeof(HostTimeline)=416632
```

The separate long-double barycentric oracle does not call the production
interpolator. Expected event targets and discrete thresholds are hand-authored,
and physical-note reference events do not use the production owner translators.
The 9,216 rendered oracle frames cover both console models at all three rates.
Audio comparisons allow `2e-7` absolute float error; observed maximum was zero.
The reported curve error is for checked final normalized anchors, with an
eight-binary64-epsilon tolerance; its observed maximum was zero. The 933
threshold cases test threshold neighbors/equality across every stable ID.
The 21 dyadic partition cases use bitwise audio and full live-state comparison.

Additional cases execute 1,024 duplicate endpoint records and one-over rejection,
256 simultaneous manual owners and 256 pedal owners, 1,168 physical events from
1,024 dense raw records, and the full 65,536-frame block with connected and
disconnected output. Tests cover restoration/Cancel/reselection, retained release
routes, state history, rate changes, fresh epochs, clock exhaustion, malformed
late/future notes and output sentinels. Rejections compare all 45 anchors, carry,
owners, control/history diagnostics, contacts, phases and clock; 39 also compare
subsequent rendered audio against an untouched copy. The remaining cases cannot
legally run that standard future probe because preparation or clock bounds do
not permit it.

Rebuilt the same complete core and focused test with AddressSanitizer and
UndefinedBehaviorSanitizer:

```sh
cmake -S /workspace/scratch/f364bc93d920/a28-source \
  -B /workspace/scratch/f364bc93d920/build-a28-sanitize \
  -DCMAKE_BUILD_TYPE=Debug -DHAMMOND_ENABLE_SANITIZERS=ON
cmake --build /workspace/scratch/f364bc93d920/build-a28-sanitize \
  --target test_host_timeline -j 2
ASAN_OPTIONS=detect_leaks=0:halt_on_error=1 UBSAN_OPTIONS=halt_on_error=1 \
  ctest --test-dir /workspace/scratch/f364bc93d920/build-a28-sanitize \
  -R '^test_host_timeline$' --output-on-failure -V
```

**ASan/UBSan result: 1/1 passed, zero failures, 2.79 seconds total, no sanitizer
finding; the same counters were observed.** The initial command used
`detect_leaks=1` and failed at exit with LeakSanitizer's explicit fatal report
that it does not work under ptrace in this environment. The successful rerun
therefore disables leak scanning only. This is not a successful LeakSanitizer
qualification. No application sanitizer report was suppressed.

A separate `sizeof` probe compiled against the same source headers observed
Engine 38,664 bytes, manual owners 3,328, pedal owners 2,112, Event 16, carry
variant 24, ControlSnapshot 56 and complete HostTimeline 416,632. These figures
quantify fixed storage for this ABI; they are not portable format guarantees.
Source static assertions establish trivial/nonthrowing value-copy properties.
Enabled callback allocation/deallocation and copy-time measurements belong to
assignment 30; these tests make no device-deadline claim.

## Limits, integration and next action

This is a focused host-independent software gate, not the complete repository
regression or a native plugin validation. No actual VST3 bundle, SDK validator,
DAW project, audio device, Windows/macOS execution, installer or measured
instrument was tested here. Exact bitwise partition equality is established for
the tested dyadic curves; arbitrary differently rounded host curve descriptions
retain ordinary binary64 arithmetic limits. The timeline has one processing
thread; UI must use StateExchange, not read Engine concurrently.

Assignment 30 can now qualify the exact frozen timeline/state-exchange path.
The next native implementation must explicitly select the nominal model,
validate native output/input before timeline commitment, use the preflighted
exchange batch, supply the host maximum independently from the hard core bound,
and keep host-output copying after successful publication. Its SDK-aware harness
must cover bus/format/pointer policy and actual factory/lifecycle behavior.

Root must integrate the five owned files with the frozen wave, run the combined
gate, update shared status/next steps/manifest and commit/push under the user's
standing authorization. Future agents must retain the explicit source basis,
counter and carry limits, curve/tie semantics, quiescent lifecycle and complete
callback rollback. Follow `AGENTS.md` and the newest session handoff, preserve
concurrent work, and record any changed contract with the corresponding new
evidence rather than inheriting results from a different header/library pair.

Final owned-file checks passed for UTF-8, LF endings, trailing whitespace,
per-file `git diff --no-index --check`, local Markdown links and owner identity.
All three live C++ files still match the frozen isolated source byte for byte.
