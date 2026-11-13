# Coherent native ASan/UBSan audit

The frozen Linux Debug gate completed **92/94 CTest suites successfully** in
**222.23 seconds**; CTest returned **8**. Full acceptance did **not** pass.
Two native suites failed timing-sensitive screenshot/observation assertions.
The complete retained CTest log contains no ASan or UBSan diagnostic. This is
an executed instrumented result, not a blanket memory-safety or product pass.

## Exact source and instrumentation

| Input or output | Identity |
| --- | --- |
| Coordinator-local frozen commit | `387275289410d12af27cf235d6e45fd91f29bafa` |
| Frozen tree | `0d6da163edd6531338938e12e0d393841d569a80` |
| Source archive SHA-256 | `12dbed72602efa4edf07e4bcb540f756f3838a77f1b4a1002fdabac912a2ea87` |
| Instrumented executable SHA-256 | `04706e4298b10eaf8dd7e5eabfe0bffe959aab0ff58773fab4d7de0b793b94aa` |
| Main source SHA-256 | `560f3f12cd0b9a081748d601ec8ad42c69b4e73b3d68ab6d583e4d5e9be1ea88` |
| Compiled profile SHA-256 | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| Pinned SDL2 | 2.32.10, `5d249570393f7a37e037abf22cd6012a4cc56a71` |

The source was extracted with `git archive`; all **782** original blob identities
matched before execution, and their bytes and modes matched afterward. This
snapshot precedes the chapel control exporter/acceptance and later device-removal
work. It must not be represented as qualification of a newer published tree.

Linux x86-64 used GCC/G++ **14.2.0**, CMake/CTest **4.4.4**, Python **3.12.14**,
GNU Make **4.4.1**, and glibc **2.41**. Configure succeeded in 27.0 seconds and
the complete build in 128.903 seconds. Both native options were explicit:
standalone ON, VST3 OFF. The nominal profile and dependency verification passed.

`HAMMOND_ENABLE_SANITIZERS=ON` was supplemented with global C/C++ sanitizer
flags so the separately entered SDL C sources were covered. Every one of
**259** compile commands contains `-fsanitize=address,undefined` and
`-fno-omit-frame-pointer`: **19 core**, **17 standalone**, **47 other project
C++**, and **176 SDL C** translation units. Core, standalone support and SDL
archives each reference both sanitizer families; the executable dynamically
requires both `libasan` and `libubsan`. System libraries were not rebuilt.
This closes the instrumentation gap of the earlier
[adapter-only probe](../STANDALONE_AUDIO_ACCEPTANCE.md), without replacing its
historical evidence or implying that unexecuted paths were exercised.

## Executed gates and exclusions

One explicit leak-enabled `hammond_standalone --help` probe returned **23** in
0.125 seconds. LeakSanitizer reported a fatal error and its ptrace limitation.
The subsequent full suite used `ASAN_OPTIONS=detect_leaks=0:halt_on_error=1`
and `UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1`. **Leak checking is
unqualified.** No leak-enabled success is claimed.

The full discovered inventory had 94 entries, with zero disabled/skipped CTest
entries. All 82 entries outside the standalone group passed. Results within
that group are below; elapsed values are the individual CTest results.

| Standalone suite | Result | Seconds |
| --- | --- | ---: |
| Install and relocation | Pass | 4.231 |
| Session concurrency | Pass | 0.631 |
| Session behavior | Pass | 1.828 |
| State files | Pass, internal exclusion below | 0.042 |
| UI model | Pass | 0.043 |
| Benchmark admission | Pass | 15.912 |
| Actual SDL audio device | Pass | 3.693 |
| Actual callback allocation | Pass | 1.557 |
| Native application | **Fail** | 15.925 |
| Native workflows | **Fail** | 26.181 |
| Replay boundaries | Pass | 7.884 |
| Input replay helper | Pass | 0.172 |

The device suite exercised 15 rate/buffer combinations, 75 matrix callbacks,
59,520 frames, 31 rejected opens, two expected render faults and eight lifetime
cycles. The allocation suite observed 39 real callbacks, 936 calibration
allocations/frees and zero production-region C++ new/delete calls. Concurrency
observed 3,072 raced posts discarded in this execution; this single pass cannot
establish that a positive scheduling observation is deterministic on other runs.
State-file acceptance explicitly did **not** execute POSIX replacement failure
after a completed temporary write. Zero CTest skips does not close that gate.

## Failures and bounded diagnosis

`test_standalone_app` ran 18 methods and 164 application processes. Six subcases
failed `runtime.screenshot_while_held == true`, after their common success
assertions had passed:

- `test_reference_minimum_and_extreme_audio_smokes`: 1280×900 at
  48,000 Hz/512 frames, 44,100 Hz/2,048 frames, and 96,000 Hz/128 frames.
- `test_saved_controls_and_legacy_startup_on_unicode_paths`: state versions
  1, 2 and 3 at the default 1280×900, 48,000 Hz/512-frame configuration.

The minimum 960×700 smoke passed. Source inspection shows that the loop observes
the Session, advances the scheduled smoke release, then renders. Capture requires
`smoke_held_observed_ && !smoke_off_sent_`; a late loop can first observe the hold
and enqueue release before evaluating that capture predicate. This is a
source-supported timing explanation, not a measured frame trace.

`test_standalone_workflows` ran 11 methods and 15 application processes. Its
`test_resize_preserves_control_focus_and_original_note_release` 1600×1000
subcase expected held Upper MIDI 60 at the third control transition but recorded
empty holds. The 960×700 subcase passed. The fixture schedules the focused edit
at 1,050 ms and release at 1,250 ms; main records one changed snapshot after its
bounded event drain. That 200 ms interval does not guarantee an intermediate
UI observation under instrumentation. The retained result alone cannot identify
the exact frame delay or establish an incorrect audio-command order.

The maintained fixtures delete per-process temporary diagnostics after checking
them. Individual callback counts and observation timestamps for these failed
subcases therefore cannot be reconstructed from retained output. Suite durations,
subcase identities, assertion traces and aggregate invocation counts are retained.
No production/test edits, timeout changes, oracle weakening or reruns were made.

## Next concrete gate

Repair smoke capture sequencing and give the resize/held-control observation a
deterministic acceptance boundary while preserving ordinary musical behavior,
bounded replay delivery and joined shutdown. Retain these failed cases, then
qualify the repaired frozen source with coherent instrumentation and its actual
native tests. Run leak checking separately on a runner that supports it.
Dummy video/audio, software rendering and sanitizers do not establish physical
devices, deadlines, other platforms, accessibility, signing or acoustic fidelity.
The [assignment record](../development/2026-11-13-next-phases/42-native-sanitizers.md)
contains exact commands, raw-log identities and the handoff location.
