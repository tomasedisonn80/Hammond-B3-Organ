# Independent review of the workspace replay dwell repair

Reviewer: A22, `/root/w04_a22_replay_fix_review`, waveform continuation wave 4,
14 November 2026. **Accepted as a fixture-only observation-window repair.** The
retained failure supports the timing diagnosis; every original behavioral gate
remains present, and all thirty retained successful native cases independently
pass offline admission. This review launches no native process and establishes
neither a new full-suite pass nor a cross-platform latency guarantee.

## Failure and cause supported by the evidence

The [original full CTest output](../development/2026-11-14-waveform-continuation/reports/wave3-ctest-first.txt)
records **160 passed / 161 executed in 226.45 seconds**. Its sole failure is the
1672×941 subcase of
`test_pointer_header_matrix_preserves_keyboard_space_and_exact_save`. The six
workspace methods still executed thirty native processes; the workspace suite
failed because the first dimensional Play visit never painted both held targets.

The [complete failing diagnostics](../development/2026-11-14-waveform-continuation/reports/root-workspace-first-failure.json)
show the following copied observations:

| Observation, ms | Applied / submitted command | Painted workspace | Held Upper / Lower / Pedals |
| ---: | --- | --- | --- |
| 329 | 4 / 4 | Play | 1 / 0 / 0 |
| 426 | 4 / 5 | No new retained presentation transition | Copied musical state remains Upper-only |
| 527 | 5 / 5 | First Rotary paint | 1 / 1 / 0 |

Space was scheduled at 320 ms and initial navigation at 500 ms. That 180 ms
interval did not include a retained Play paint with the acknowledged second
note. The first Play visit contains only `(0,0,0), (0,0,0), (1,0,0)`, so the
required `(1,1,0)` correctly fails. Applying the current unchanged view checker
to this original evidence reproduces exactly that failure. Both note commands
are eventually acknowledged, the release sequence finishes, and diagnostics
show zero audio/render/session faults. These observations support insufficient
paint-observation time; they do not show a lost Lower owner.

527 ms is the first **observed acknowledged snapshot**, not a measurement of
the exact audio callback application instant. The separate
[A18 timing report](../development/2026-11-14-waveform-continuation/reports/a18-material-timing.json)
records reference-size dimensional software painting p95 127.332206 ms and total
p95 127.332737 ms. That establishes plausible pressure on the original interval;
it is a different experiment and cannot assign a precise paint duration or
callback latency to this failing replay.

## Exact scope of the change

The [retained four-hunk diff](../development/2026-11-14-waveform-continuation/reports/root-workspace-replay-fix.patch)
changes only `apps/standalone/native_tests/test_standalone_workspace_replay.py`.
It adds `HEADER_VISUAL_SETTLE_MS = 600`, adds that dwell to every header-journey
event originally scheduled at or after 500 ms, increases the corresponding full
journey duration by 600 ms, and moves the two release earliest-time expectations
by the same amount. It changes no product source.

| Header action | Original, ms | Repaired, ms |
| --- | ---: | ---: |
| Reverse-Tab focus presses | 50, 80 | 50, 80 |
| Upper A / Lower Space presses | 180, 320 | 180, 320 |
| Rotary / Flat / Service pointer presses | 500, 700, 900 | 1100, 1300, 1500 |
| F3 / RightBracket target changes | 1050, 1100 | 1650, 1700 |
| Play / Flat pointer presses | 1250, 1450 | 1850, 2050 |
| Space release / A release | 1600, 1800 | 2200, 2400 |
| Save press / release | 1950, 1970 | 2550, 2570 |
| Full replay duration | 2250 | 2850 |
| Per-process timeout | 9 seconds | 9 seconds |

All corresponding pointer and key releases move together. The new
Space-to-navigation interval is 780 ms. The 200 ms and shorter later observation
intervals retain their original spacing. The separate startup and Upper-only
prefixes remain 250 ms each.

The reviewer reversed all four hunks in memory and reproduced the recorded
original source hash exactly. AST comparison finds **132 identical assertion
calls** and the same six test methods. Independent enumeration of original and
repaired run requests confirms 23 unchanged requests and exactly seven changed
full header requests: each retains all 24 events in the same order, leaves six
early events unchanged, and shifts the remaining eighteen by exactly 600 ms.
All other invocation arguments and literal controls/coordinates are unchanged.

In particular, the suite still requires all six consecutive Play/Rotary/Flat/
Service visits to paint both original held targets, exact two On/two Off and
four-command sequence growth, ordered acknowledged note prefixes, original
owner releases before shutdown, identical sound controls, six capture refusals,
and exact canonical Save bytes at each size. The fourteen short prefix runs
must leave their deliberately noncanonical input bytes untouched. No assertion,
test, size, process, deadline, or lifecycle gate was dropped.

## Retained successful execution and independent admission

The [targeted CTest output](../development/2026-11-14-waveform-continuation/reports/wave3-targeted-recheck.txt)
records **2/2 in 48.92 seconds**: workspace replay takes 48.91 seconds and the
separate final A17 streaming-path test passes. The
[retained raw LastTest output](../development/2026-11-14-waveform-continuation/reports/wave3-targeted-raw.txt)
records all six workspace methods passing, thirty actual subprocesses and
48.829 seconds inside unittest. The original failing run and successful recheck
name the same executable hash. These are separate executions; adding their
results does not produce a full-suite pass.

The [A22 evidence report](../development/2026-11-14-waveform-continuation/reports/a22-replay-evidence-review.json)
records offline admission of **all 122 retained files across all thirty cases**
in sibling `wave3-workspace-recheck/`, including strict duplicate/nonfinite JSON
rejection, source-generated script byte comparison, exact invocation arguments,
input/output state hashes, return codes, empty output, all retained common
schema/lifecycle checks and the unchanged method-specific assertions.

| Workspace method group | Native cases inspected |
| --- | ---: |
| Capture refusal closes a parameter gesture | 1 |
| Focus memory, Save and Load | 1 |
| Hidden Play regions reject changes | 4 |
| Pointer capture refusal preserves keyboard owner | 1 |
| Header matrix: startup, Upper-only, complete journey at seven sizes | 21 |
| Synthetic MIDI/UI ownership: startup and complete journey | 2 |
| **Total** | **30** |

All retained processes exit zero with empty stdout/stderr and durations between
0.326539 and 3.851062 seconds, below the unchanged deadline. Seven full header
runs first paint both notes at 368–443 ms, then first paint Rotary at 1109–1156 ms;
their individually measured gaps are 677–770 ms. The reference-size run paints
both notes at 432 ms and first Rotary at 1109 ms. Every complete visit and Save
gate passes. The exact same native executable bytes are present before and
after this review.

| Identity | SHA-256 |
| --- | --- |
| Original fixture, reconstructed from the exact patch | `28b61802b99233e5f7ee14d01f5456b15bdff235309038b2943e75863d6097f7` |
| Reviewed repaired fixture | `9a226a6b17b1d7eb84a079a113f5ef97a6f37935ba16d1d3f55876bed907d6f3` |
| Native executable, 3,628,544 bytes | `677acfa6a0244d3f7085eb96fa0737306a9f9e74febabb34f55fea99b303c51c` |
| All 122 retained case-file identities, canonical aggregate | `6ef5733eae159768c0347af2288b6796341b8a56fb1506355d4ce6694850270b` |
| Canonical saved control bytes | `4ccbf8d166b3dacf34a06ef50641d4c48fafa9507e19ccd0707b852af25a24cf` |
| Noncanonical prefix input/output bytes | `96921f6bea580a6bd0619f4b8000db5ca81a523e61f50fdf682c53e1fa64e97a` |

The JSON defines the aggregate unambiguously and retains each file hash/size,
case outcome, related fixture/source hashes and exact evidence/log identities.

## Limits and next gate

The fixed dwell provides tested observation margin for this Linux SDL 2.32.10
dummy-audio/dummy-video software renderer. It does not synchronize navigation
to an acknowledged painted state or guarantee success under arbitrarily slow
painting, sanitizer overhead, CPU starvation, Windows/macOS scheduling, real
displays, MIDI/audio devices or physical capture. Short startup prefixes and
later visit intervals still have finite timing assumptions. Repeated failures
must retain their diagnostics and resolve the concrete timing or behavior cause;
this review does not authorize relaxing assertions or increasing deadlines.

BMPs are temporary by existing fixture design. A22 verifies retained screenshot
metadata and the execution log, but cannot independently decode deleted BMP
bytes. This is neither screenshot-fidelity acceptance nor native device testing.

Root's earlier missing-private-include build repair is a separate setup event.
The pending final gate is a coherent frozen-source build and full CTest,
followed by actual hosted results on the intended platforms. Preserve the
160/161 failure, later 2/2 success, and this read-only admission separately.
The independent R4 numerical gate, R5/R6, physical fidelity and literal reference
image equality remain outside this review.
