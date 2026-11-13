# Assignment 40 — native automation interaction review

Owner: /root/w07_a40_native_automation_review

Wave: 07. Session: 2026-11-13 pedal development. This is one newly dispatched
worker in the current sixty-assignment, ten-wave session.

## Scope, source basis and initial gap

Owned only:

- `plugins/vst3/tests/test_native_automation.cpp`
- `docs/VST3_AUTOMATION_REVIEW.md`
- This assignment note.

No production source, shared harness, dependency checkout, shared status/ledger
or CMake file was modified by this worker. No subagent dispatch, staging, commit
or push was performed. Root added the requested native CMake target hook and
owns the combined gate and publication under [AGENTS.md](../../../AGENTS.md).

Read the standing instructions, current status/next steps, development-log
handoff, project plan, atlas review and relevant native contracts. Read the
complete extracted atlas pages **379–402**, covering callback ownership, the
framework-independent Engine, native timing/state and permanent parameter
compatibility. This is a focused source rereading, not another complete-PDF
assignment. The atlas's proposed continuous drawbars and different 62-control
registry do not replace the repository's frozen 45-ID discrete/continuous laws.

Reviewed `HostTimeline.cpp`, `Processor.cpp`, Engine control application, the
complete prior `test_native_behavior.cpp` and its acceptance record, and the
frozen NativeHarness. The prior native gate already covers broad malformed
input, all single-point mappings and short curves. The identified gap was
simultaneous curves across all 45 controls, generated work beyond 1,024 physical
events, noncanonical anchors surviving queue gaps, and those curves composed
with pending states, Cancel and old/fresh boundary work. No fabricated defect
was introduced to justify a production change.

## Implemented result

The [automation review](../../VST3_AUTOMATION_REVIEW.md) records the complete
equations, assertions, coverage and limits. The new test loads the actual native
bundle with A34's shared harness and uses only queried native interfaces.
Expected values come from integer/dyadic expressions and hand-written physical
Engine controls/notes; neither HostTimeline nor ParameterBridge nor their
descriptor/ownership helpers form the expected schedule.

At each supported rate, two score instances compare one 4,096-frame callback
with 45 irregular callbacks. All 45 queues are present, independently permuted;
36 retained manual bars, both pedal mixtures and all six switches traverse
their declared thresholds while expression changes every sample. Distinct
Upper A/B and Lower A/B registrations, explicit selectors, isolated division
windows and later nonzero continuations exclude a silent passing fixture.

The whole callback has 239 raw records but at least 4,096 distinct expression
events alone. This proves the workload requires internal slicing under the
inspected fixed-array contract. It is not a claimed read of a hidden slice
counter. Complete native samples and the future audible epoch agree bitwise
with a reference advancing exactly one sample at a time.

The gap extension leaves a normalized anchor at `17/1024` between plain
drawbar steps, with no future carry, then sends thirteen frames with absent
queues and seven with all 45 queues empty. Resumption uses
`q[i] = (17 + 25*(i+1))/1024`; reconstructing from rounded plain controls would
move actual threshold samples. A further audible continuation must match.

Three other loaded-module scenarios compose four pending states with retained
endpoints/notes, fresh duplicate zero points, 44 simultaneous curves and Lower
Cancel. Their reference explicitly restores controls/anchors, applies all
parameters, then carried notes, then fresh notes. Upper reconnects on an
explicit same-value selector; absent Lower selection preserves Cancel. A later
same-value Lower point produces measurable audio against an independently
rendered cancelled counterfactual from the same source epoch.

Source review found no concrete defect in monotonic admission, missing/empty
queue handling, stable global order, restore-first anchor setup, future-boundary
carry, zero-frame ownership or emitted-event slicing. Many current same-frame
control and note-target setters commute. Audio equality does not uniquely prove
the ordering of every commuting pair; precise parameters-before-carried-notes
ordering is additionally established by source inspection. This limitation was
reported to root and retained in the public review.

## Coherent inputs and unchanged artifact proof

Root's frozen W6 source tree was
`b2dae50dcde294bde8e7acb7addb14456197a779`, materialized at
`/workspace/scratch/f364bc93d920/checkpoint-w06/source`.
Compared all files under its `src/` and `include/`, all eight native production
headers/translation units, and both shared harness files against the matching
`a33-native-source` used for A33–A35's module/archive build: **45 input files
matched byte-for-byte**. A JSON scratch manifest records every path/hash.

The test source was copied into its own `a40-automation` directory and compiled
against the frozen W6 include/harness directories. It linked the matching
read-only A33 archives. No current mutable header was silently substituted for
the older library interface. The module/profile hashes were asserted against
the previously retained identities before execution; every archive/module/profile
hash was checked again afterward and remained unchanged.

The source review used unchanged production files:

| Input | SHA-256 |
| --- | --- |
| `HostTimeline.cpp` | `37941dc9d833cabc1ed7ca22327ad23240ea8c04e6de9fc3f447222d2ebb41dd` |
| `Processor.cpp` | `a61e567798e7435c9d73ddab9bf925b6995396954e772c13f31571ad0a96f20b` |
| `NativeHarness.h` | `0067515c5259288f1f711e4ce8c0921721682209863ca62ccbee4f50dbb2752a` |
| `NativeHarness.cpp` | `899d504d842e2e1b83d7f629e0bb4335b0c4f4191d7568df90980f27c09828b7` |

SDK root `3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96` and its four required
submodule pins remain the unchanged [dependency lock](../../../data/dependencies/vst3-sdk-lock.json).
This worker performed no network acquisition or SDK mutation. The source PDF,
compiled profile, stable IDs, UUIDs, state grammar and physical model values
were unchanged.

## Actual commands and execution

Environment: Linux x86-64, glibc 2.41, GCC `14.2.0-19` (14.2.0), Python
3.12.14. The root's native build uses CMake 3.31.6; this focused compile used
the already verified archives and the same strict Release compiler flags.

The exact compiler argv is retained in scratch `a40-automation/compile-command.json`.
Its command, with common directory prefixes assigned here for readability, is:

```sh
a40_base=/workspace/scratch/f364bc93d920
a40_frozen="$a40_base/checkpoint-w06/source"
a40_built="$a40_base/a33-native-build"
a40_work="$a40_base/a40-automation"
/usr/bin/c++ -Wno-multichar -O3 -DNDEBUG -std=c++20 -fPIE \
  -fvisibility=hidden -fvisibility-inlines-hidden -DSMTG_RENAME_ASSERT=1 \
  -Wsuggest-override -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion \
  -Wshadow -Werror -DRELEASE=1 \
  -I"$a40_frozen/plugins/vst3/tests" -I"$a40_frozen/include" \
  -isystem "$a40_base/vst3sdk" "$a40_work/test_native_automation.cpp" \
  -o "$a40_work/test_native_automation" \
  "$a40_built/lib/Release/libhammond_vst3_test_host.a" \
  "$a40_built/libhammond_core.a" \
  "$a40_built/lib/Release/libhammond_vst3_test_loader.a" \
  "$a40_built/lib/Release/libsdk_hosting.a" \
  "$a40_built/lib/Release/libsdk_common.a" \
  "$a40_built/lib/Release/libbase.a" \
  "$a40_built/lib/Release/libpluginterfaces.a" -lstdc++fs -lpthread -ldl

"$a40_work/test_native_automation" \
  "$a40_built/VST3/Release/HammondB3.vst3" "$a40_built/nominal.b3p"
```

The compiler and executable were launched with Python `subprocess.run` and
captured stdout/stderr. No shell-expanded command substitution or credential
data was involved. This was a direct executable gate, **not a CTest run**;
the root's subsequently registered target supplies the ordinary CMake/CTest
reproduction shown in the automation review.

The first strict compile and test both passed. That version had the all-control
score and restore/carry scenarios: 201 accepted callbacks, 88,029 main-reference
frames and 176,058 exact channel comparisons, exit zero in 0.455 seconds. Review
then identified the remaining absent/empty-queue normalized-anchor gap and added
the focused continuation above. No production fix or weakened assertion was
needed. The final strict compile also passed without diagnostics; the expanded
run returned exit zero in **0.417 seconds**.

Final actual output:

```text
native automation: score_cases=6 restore_cases=3 gap_cases=6
callbacks=231 zero_callbacks=18 state_reads=261
direct_reference_frames=89979 exact_channel_samples=179958
partition_mono_samples=19407 future_channel_samples=39948
nonzero_channel_samples=157150 long_callbacks=3
guaranteed_expression_events=12288 isolated_windows=18
division_min_rms=0.00402141,0.00655038,0.00172213
reconnect_difference=0.0238609 maximum_error=0 peak=0.198746
checksum=5ea365699a5717c9
```

The 3,072 extra frames in cancelled counterfactual branches are excluded from
the main elapsed-reference count. Repeated isolated windows and per-sample
comparisons are not relabelled as independent musical scenarios. Exact sample
equality and predeclared audible guards passed; timing is an observed process
duration, not an audio-device deadline threshold.

`python3 -B tools/check_repository.py --json` passed with zero errors, including
270 Markdown files and 1,572 local links in the then-current shared checkout.
That source-integrity check's historical 60-note count is not a current-session
completion claim. All three owned files passed whitespace inspection and the
compiled test copy matched the repository source byte-for-byte. An initial
whitespace-helper invocation treated `git diff --no-index --check` exit 1 as an
error even though it emitted no diagnostic; exit 1 denotes the expected new-file
difference. Correcting that helper's exit interpretation completed the check
without changing source or weakening a whitespace rule.

## Frozen test, artifacts and retained scratch records

| File/artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `test_native_automation.cpp` | 30,122 | `7e26bd08a071522fc6403d4c7ec17cafbfeff53b9980740cf02e5ffda68f5ca3` |
| Focused test executable | 342,840 | `4324256048874560af9fc31d63a1ec10f7f06dc5069ffe311dfbcde2fd36a9e3` |
| Loaded `HammondB3.so` | 434,168 | `d87353b237e52c8d1f91af27933493a4cf78ba4a06af4a96c9930c0ecec1d3ff` |
| Compiled nominal profile | 4,545 | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| Matching `libhammond_core.a` | 215,370 | `81caa16956fd968a83b1d5633efec15c6e8ecf87051f01cd29db0fc5c870ef91` |
| Matching `libhammond_vst3_test_host.a` | 81,348 | `65853d189cf52d93043dc5975ffe4ac20978b86eded065b07e73addd3e774ca1` |
| Input/archive coherence manifest | 7,792 | `fe4d205a30b54c70e4c6158e61d446b153224c6c91722eb9f6e3897cbafc0fa5` |
| Exact compiler argv JSON | 1,326 | `0795f2490ce1b9e14cd1695122e844373314e5a62c30bf4b07439cd10c551828` |
| Initial execution log | 497 | `4bbdfc173c92e78ebb19bf212e7243ae051c20ec6f80d0c0e6df92c478d3e711` |
| Final execution log | 509 | `d0f9f4741d452472aec36e24ed3fcabc6febd8b38edde2ea9371c4e411e537b7` |

The final compiler log was empty, SHA-256
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
Scratch records are in `/workspace/scratch/f364bc93d920/a40-automation`;
durable reproduction source, equations, actual results and identities are in
the three owned repository files. No binary or dependency was added to Git.

## Handoff and next step

Root can freeze these three files together with its CMake hook, include
`test_native_automation` in the native aggregate, run the coherent combined
gate, update shared status/next steps/log and publish under the standing workflow.
Then observe this exact test source on actual native Linux, macOS and Windows
jobs. The earlier W6 module result does not qualify the newly added test on
platforms where it has not run.

Continue the separately owned native allocation and concurrency gates, install
relocation, musical evidence and eventual actual DAW/device qualification. No
allocation, race-detector, deadline, DAW, custom-UI, signing or calibration result
is claimed by this worker. The model is the existing nominal, unmeasured dry
organ. SDK validator results remain separately scoped: the retained summary is
47 passed/zero failed with **16 teardown diagnostics and nine unsupported-rate
error-labelled messages**; no warning-free validator claim or dependency patch
is introduced here.
