# Assignment 35 — actual native behavior acceptance

**Agent:** `/root/w06_a35_native_behavior`

**Wave:** 6 of the current sixty-assignment, ten-wave pedal session

**Date:** 2026-11-13 UTC

## Owned scope and starting inputs

Owned only:

- `plugins/vst3/tests/test_native_behavior.cpp`
- `docs/VST3_BEHAVIOR_ACCEPTANCE.md`
- This assignment note.

No production source, shared status/manifest, CMake file, dependency checkout or
other worker file was changed. No commit, push or subagent dispatch was performed.
The root integrator owns publication under [AGENTS.md](../../../AGENTS.md).

Read the standing instructions, active status/next steps, project/atlas plan,
native spike and processor contracts, HostTimeline and StateExchange documents,
the actual processor implementation, Engine/control interfaces, permanent
parameter targets and the frozen native test harness. The relevant source basis
is atlas pp. 385–401 and the pinned SDK interfaces retained by assignments 15,
31–34. This assignment does not add an independent full-atlas rereading claim.

Assignment 34 supplied its reusable actual-module host fixtures. Assignment 33
supplied the optional CMake target hook and coherent native source/build pair.
The native implementation had already linked and passed the SDK validator's
47 counted tests, with its separately retained 16 teardown diagnostics. The
new gate here loads that actual module and exercises functional behavior through
queried interfaces; it does not construct `Processor` or inspect private state.

## Implemented evidence

The maintained test uses the same nominal profile/seed/contact model in a plain
Engine, with hand-scheduled physical events and independent closed-form control
values. It never invokes the production host timeline, owner translators or
parameter conversion routine to create expected results. A second, untouched
loaded module supplies counterfactual future audio for rejected native calls.

The [complete acceptance document](../../VST3_BEHAVIOR_ACCEPTANCE.md) records
the cases and numerical formulas. Executed coverage includes:

- All three rates and nine isolated audible Upper/Lower/Pedal registrations,
  explicit bank-B selection, identified/channel/anonymous ownership overlaps,
  tiny positive velocity, zero-velocity release and selected valid filtering.
- One, zero, irregular and maximum 65,536-frame callbacks; disconnected and
  inactive output; exact channel aliasing; phase-preserving stopped rate and
  maximum changes; active silence flags and untouched output tails.
- All 45 actual native parameter targets, reversed queue enumeration, duplicate
  point ties, 90 adjacent/exact threshold cases, signed-zero expression and
  same-value selector reconnection of Cancel.
- Previous-sample anchors, simultaneous expression/discrete ramps, offset-N
  interpolation/carry, carried/fresh zero ties, no replay after zero flush,
  unmasked anchor preservation after malformed input, and nine dyadic partition
  comparisons at the three supported rates.
- Active four-entry state loading, pending and acknowledged saves, failed
  callback queue retention, old-state migration, retained pedal owners through
  muted migration, and publication during 32 callbacks without UI reads.
- 1,024-record work/carry limits, explicit one-over rejection, filtered records
  consuming raw budget, retryable releases, 1,024 same-sample transitions,
  256+256 simultaneous owners and four pending restores while they remain held.
- 59 malformed native fixtures with full output/flag sentinels, a still-full
  state queue after rejection, and later audible owner/clock/history probes.

Every comparison uses a declared reference. Native phase/clock/contact tables
are not exposed by this ABI harness; their preservation is observed through
exact audio continuation and musical state, rather than claimed as direct
diagnostic reads. The underlying Engine's own separate tests cover its private
source/history contracts.

## Coherent source and actual commands

The shared native snapshot began with root's archived W5 code tree
`06786b70f1cffcc6371600fd6e14306f16e8c985`, followed by the frozen assignment
31–33 native/build overlay and assignment 34's harness and ABI test. The W5
code is also present unchanged in published `88c36b4a72a07f6498f73279f25023278accd350`.
The overlay manifest was `a33-native-overlay.json`, SHA-256
`7d3e645a31698a42fb699f0a834f8a3cbadbea58c0e483c4bfb3112c313b50d6`.
It records each overlaid production/build file; the later A34/A35 test additions
are identified separately below.

Before reusing the handed-off build, compared every file under `src/` and
`include/hammond/`, all eight native production headers/translation units, and
both harness files between the shared working tree and the frozen snapshot.
Every comparison matched. The only A35 source copied into that snapshot was
the owned behavior test. No older library was linked with a later live header.

Executed with Linux x86-64/glibc 2.41, GCC 14.2.0, CMake 3.31.6 and Python
3.12.14:

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake \
  -S /workspace/scratch/f364bc93d920/a33-native-source \
  -B /workspace/scratch/f364bc93d920/a33-native-build \
  -DCMAKE_BUILD_TYPE=Release -DHAMMOND_BUILD_VST3=ON \
  -DHAMMOND_VST3_SDK_ROOT=/workspace/scratch/f364bc93d920/vst3sdk

/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake \
  --build /workspace/scratch/f364bc93d920/a33-native-build \
  --target test_native_behavior -j 2

/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/f364bc93d920/a33-native-build \
  -R '^test_native_behavior$' -V \
  --output-log /workspace/scratch/f364bc93d920/a35-native-behavior-final.log
```

Configure independently reported all five pinned checkout identities and
primary licenses verified, embedded JSON verified and no network use. It retained
the SDK's informational missing-JACK message; this headless gate does not use JACK.
The actual compiler command used `-O3 -DNDEBUG -std=c++20 -fPIE`, the SDK's
visibility flags, and project warnings including
`-Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror`.
SDK headers were system includes; the test remained subject to strict warnings.

CTest executed:

```text
a33-native-build/bin/Release/test_native_behavior
  a33-native-build/VST3/Release/HammondB3.vst3
  a33-native-build/nominal.b3p
```

## Actual results and refinements

The first compile and runtime gate both passed. Its CTest reported 1/1 in
1.66 seconds, 1,021 accepted callbacks and 72 rejected callbacks. Before final
freeze, root requested explicit isolated audibility for every division so a
wrong manual bank could not hide behind pedal output. Made bank-B selection
explicit and added nine isolated division tests across the three rates.

The first draft's paired comparison counter included valid setup samples as
well as post-rejection probes. Split those counters before publishing evidence:
61,360 setup channel samples and 81,302 genuinely post-rejection channel samples.
No assertion was weakened and no production defect was found. Both refinements
used the same unchanged native module. The final strict rebuild and CTest passed.

Final executable report:

```text
native behavior checks=29046845
accepted_callbacks=1030 rejected_callbacks=72 zero_callbacks=123
direct_reference_frames=233792 exact_channel_samples=610510
paired_setup_channel_samples=61360 future_audio_samples=81302
audible_samples=575944 state_reads=542 rejected_state_loads=68
threshold_cases=90 rollback_cases=59 partition_cases=9 rate_changes=3
isolated_division_cases=9 division_peaks=0.015,0.015,0.0096094
peak=0.0906279 checksum=3c4b24caebfdd1b9
```

**1/1 test passed, zero failed.** CTest reported 1.99 seconds for the selected
test and 2.00 seconds total. Sample comparisons are exact binary32 checks; the
largest observed error is zero. The 29,046,845 assertion count includes extensive
sentinel-tail checks and is not a number of independent musical scenarios.
No separate sanitizer, allocation or deadline result is claimed by this run.

## Frozen identities

| File/artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `test_native_behavior.cpp` | 53,084 | `f9c44fb1e15a4c3ce7ec9fb9a6c9360840171d63db0c3c3a90319bb6c9422e26` |
| `NativeHarness.h` supplied by A34 | 8,411 | `0067515c5259288f1f711e4ce8c0921721682209863ca62ccbee4f50dbb2752a` |
| `NativeHarness.cpp` supplied by A34 | 15,072 | `899d504d842e2e1b83d7f629e0bb4335b0c4f4191d7568df90980f27c09828b7` |
| Final A34 ABI test in the same snapshot | — | `afb51186f71622972953926e56d62d77efb56b0d2c603c0d429689520421245b` |
| A35 test executable | 450,448 | `cb3f0ba106e69fee2274644523d33f8cbb4fead97678b25b9e4eabfeb0efcf68` |
| Loaded `Contents/x86_64-linux/HammondB3.so` | 434,168 | `d87353b237e52c8d1f91af27933493a4cf78ba4a06af4a96c9930c0ecec1d3ff` |
| Compiled nominal profile | 4,545 | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| First selected CTest log | 1,910 | `1aa87026b4e1b99dda597433dea40178778724d25b6bbb405e7220d8ce7ab3a5` |
| Final selected CTest log | 2,007 | `103109b9015df8109ccc9194b075da551c10229c6718b036374c625c1c94670c` |

The SDK root remains `3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96`, with the four
required module pins from the unchanged dependency lock. The wrapper sources,
fixed UUIDs, parameter identities, source profile, source phases policy and
physical model values were not altered by this assignment.

## Handoff and honest limits

Root can include the frozen test and two evidence records in the coherent
wave-6 archive, run its complete gate, update shared status/next steps, and
commit/push under the standing workflow. The scratch native source/build pair
has been handed back; A35 no longer owns a running build there. Preserve this
source/module binding when interpreting these results.

The next native work is the actual callback allocation audit, actual concurrent
UI/audio stress, hosted platform qualification and package review. The state
calls here are sequential while processing is active; this is not a data-race
proof or a device-thread scheduling test. The suite does not establish direct
native diagnostics for every source, arbitrary curve partition equality, every
MIDI extension, custom UI, DAW project reopening, audio-device deadlines,
underruns, signing, physical pedal shaping or measured instrument fidelity.

SDK validator teardown diagnostics remain in A33/A34 records. This test neither
patches the pinned SDK nor reclassifies those messages as a warning-free result.
