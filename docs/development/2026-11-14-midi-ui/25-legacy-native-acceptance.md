# A25 — Retained native acceptance on schema 2 and the reference layout

Actual worker: `/root/w05_a25_legacy_native_acceptance`, MIDI/UI wave 5,
assignment 25. Owned the four retained native Python suites,
`examples/standalone-input-v2/`, and this note. No production code, CMake,
shared status, historical demo, or original fixture edits were made by this
worker. A23 supplied the frozen application diagnostics contract; root built
the coherent native executable.

## Accepted result

The complete retained group passes **4/4 suites, 40 existing test methods,
240 actual native application subprocesses**, plus 22 chapel exporter
invocations. All original test method identities remain present. Existing
musical control values, note owners, accepted-command counts, command-prefix
and acknowledgment checks, saved-state bytes, input preservation, and output
sentinel checks remain in force.

| Suite | Methods | Native subprocesses | CTest elapsed |
| --- | ---: | ---: | ---: |
| `test_standalone_app` | 18 | 164 | 9.28 s |
| `test_standalone_workflows` | 11 | 25 | 38.84 s |
| `test_standalone_replay_boundaries` | 9 | 29 | 5.24 s |
| `test_standalone_chapel` | 2 | 22 | 20.42 s |

The boundary suite retains 19 actual setup-rejection cases. The chapel suite
retains all eighteen documentary rows, paired-bank cases, exact binary64
expression serialization, silence at zero expression, and the held endpoint
that proves Upper survives Lower's release before joined shutdown.

## Diagnostics remain strict

`test_standalone_app.py` retains exact top-level and nested field sets, exact
types, duplicate-member rejection, finite-number checks, and all previous
runtime/audio/session/control/smoke validation. Its schema version is now 2.
The complete MIDI object is explicitly typed, including its channels, device,
inbox and decoder objects, plus A23's frozen `source`, `arrival_time_source`
and `arrival_time_is_sample_time` fields. Booleans cannot satisfy integer
counter fields. The unchanged recursive validator was moved to a test helper;
no production serializer or layout is imported.

All four suites use the same independent literal no-input expectations:
`source="none"`, empty requested/opened names, zero generation, no active
input before or after shutdown, stable quiescent shutdown, no pending releases,
zero lifecycle/device/inbox/decoder counters, default channels 1/2/3, drain
budget 32, inbox capacity 256, and no `midi_replay` object. Receipt time is
explicitly not sample time. A compiled ALSA/WinMM/CoreMIDI backend may remain
closed; a disabled build must report `unavailable` and its matching status.
Ordinary UI replay also requires integer `observation_capacity=512`.

This gate used the enabled ALSA build without selecting or enumerating a
MIDI port. Successful runs retained empty stderr and the exact inert MIDI
observations. The disabled-build expectation is present but was not executed
by this worker. These checks constrain no-input behavior; they do not qualify
a physical device, native port permission, hotplug, sample timing or hardware
behavior. The separately owned backend and MIDI CLI suites provide their
own instrumentation and source scopes.

## Independent literal geometry and fresh pixels

The reviewed [shared-layout implementation](15-reference-layout.md) puts the
default-size bank controls in the manual cheek. The retained acceptance uses
literal coordinates derived from that geometry, without calling it at test
runtime:

| Target | New literal point or focus count |
| --- | --- |
| Upper EDIT A, 1280×900 | `(58,508)` |
| Upper EDIT B, 1280×900 | `(130,508)` |
| Upper PLAY B, 1280×900 | `(130,536)` |
| Upper CANCEL, 1280×900 | `(94,564)` |
| PANIC, 1280×900 | `(1228,66)` |
| Upper C2 / MIDI 36, 1280×900 | `(202,580)` |
| Lower C2 / MIDI 36, 960×700 | `(36,560)` |
| First Upper drawbar from no focus | Twelve Tabs: six header controls, five bank controls, then the drawbar |

The tied-resize fixture still executes all seven actions at 200 ms: resize to
960×700, Lower C2 pointer Down/Up, Space Down, resize to 1280×900, Upper C2
pointer Down/Up. It still requires three accepted note-ons, two accepted
note-offs, the final 1280×900 dimensions, and **only Lower MIDI 36 held before
shutdown**. Each resize marker must take effect before its own pointer
coordinates; the original Space owner must survive the later Upper refocus.
The off-window pointer test still requires two note-ons/two note-offs and
preservation of the independent keyboard C4 owner until its own release.

The upper keyboard starts at `(188,496)` with 1068 natural-key units at
1280×900, or `(24,424)` with 912 at 960×700. C4, D4 and E4 have zero-based
natural ordinals 14, 15 and 16. The new probe interiors are below the
accidentals. Four **fresh actual native** held/idle captures independently
verified these points before the final full gate:

| Size | C4/D4/E4 x; shared y | Idle RGB, all three keys | Held C4 RGB | Held D4/E4 RGB |
| --- | --- | --- | --- | --- |
| 1280×900 | `618 / 648 / 678; 580` | `246,231,201` | `226,201,140` | `246,231,201` |
| 960×700 | `391 / 417 / 442; 466` | `248,233,203` | `214,182,124` | `248,233,203` |

The acceptance still parses each invocation's new BMP, checks exact dimensions,
header/stride/length and nonuniform rendering, requires a capture while C4 is
held, compares equal unheld D4/E4 pixels, and requires C4 to differ. It never
loads an old demo image as its pass criterion. Both sizes and the 44.1/48/96 kHz
smokes retain those checks; saved controls versions 1/2/3 retain the held-key
paint assertion even when the cancelled Upper route is silent.

## Fixture edition and historical preservation

Active workflow tests now use
[the v2 input examples](../../../examples/standalone-input-v2/README.md).
The directory edition does not change `B3UIREPLAY1` grammar or `B3CONTROLS3`.
Keyboard and audio scripts are byte-identical copies. The Save script changes
only its explanatory comment and the two pointer records from `(165,136)` to
Upper EDIT B `(130,508)`; its event times, four subsequent Tabs, held C4,
Save/edit/Load sequence and duration remain unchanged.

All **44 tracked original input/demo files** under `examples/standalone-input/`
and `examples/demos/` were compared byte-for-byte with HEAD and remain
unchanged. In particular, no historical screenshot or provenance record was
rewritten to present the new interface as an earlier capture.

| Fixture | SHA-256 |
| --- | --- |
| Original and v2 keyboard | `823a5618f104ffb4756ade749fb1990dcf087cc1319e35b5fc1ceac0af548384` |
| Original and v2 audio | `c24c7225a93381be0767b291f02161725c314da42f4bb0f073e165d2f0123702` |
| Original Save, unchanged | `b31bae7800d9fea2f05045f261bcbbbc9f68935705a2e5047ac80517b592191f` |
| v2 Save | `a62c4ecf1b4544597451db87b8d5fd5055a9ca15dd64cdf334579e8fae6abe23` |

## Failed observations and concrete corrections

1. The original tests rejected the new binary's extra `midi` object and schema
   version (`2 != 1`). This was observed in selected real app, workflow,
   boundary and chapel runs before editing. The initial binary hash was
   `48e308cfea28c7d26c9bf3efe99bf5a52eee80064db39c31f4b878e13bebd42e`;
   root then rebuilt A23's restored UI-only error wording into the final
   binary below.
2. After the strict schema update, the unchanged old image points failed all
   four smoke configurations: C4 equalled the unheld reference pixel. The old
   default row produced equal BGR `ad ca d8`; the minimum row produced equal
   `26 2a 29`. Old bank and Save clicks failed exact control paths; eleven
   Tabs failed the literal resize command-prefix oracle; the old pointer
   point accepted only one note-on instead of two. The old tied-resize point
   `(35,500)` ended with `[[],[]]` instead of `[[],[36]]`. The replacements
   above restore the original musical expectations rather than relaxing them.
3. The first complete updated gate was **3/4 in 38.75 s**. The app's directory
   rejection still expected `outputs must be regular files or new paths`;
   A23 intentionally extended the message to include replay-script paths.
   That assertion also prevented directory cleanup and caused the following
   subcase's `IsADirectoryError`. The test now requires the **complete exact**
   line `hammond_standalone: Screenshot, diagnostics, and replay script paths
   must be regular files or new paths` plus newline, and performs cleanup in
   `finally`. Expected exit 1, empty stdout and the complete unchanged-tree
   sentinel comparison remain mandatory. Root confirmed no production repair
   was needed. The complete final rerun passes, rather than counting the
   earlier passing subset as the finished result.

## Exact final verification and source boundary

Working directory: `/workspace/scratch/cd4bd06ce68f/Hammond-B3-Organ`.
Base checkout was `e09107414896c2c53dad124a74f60c8043fadfe4`, tree
`1f117a17cf561fae8978adeb612abf9ad29d7b64`. The tested native binary includes
root's coherent A23/A24 MIDI-replay additions; this is **not** a claim that the
base commit alone contains those changes. Root held the binary and main
source stable for the final checks. GNU C++ 14.2.0, CMake/CTest 4.4.4,
Python 3.12.14, Release, SDL 2.32.10, `HAMMOND_BUILD_STANDALONE=ON` and
`HAMMOND_ENABLE_MIDI=ON`; selected backend ALSA, no port selected.

```sh
/home/agent/.cache/uv/archive-v0/kvsqq5-iHdbf13RC/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/cd4bd06ce68f/build-native \
  -R '^test_standalone_(app|workflows|replay_boundaries|chapel)$' \
  --output-on-failure --no-tests=error -j 2 \
  --output-log /workspace/scratch/cd4bd06ce68f/a25-legacy-evidence/final-ctest.log
```

Result: **4/4, zero failures, 38.85 seconds**. All Python files compiled for
syntax, all original method names were compared by AST, new fixture byte/event
comparisons passed, and `git diff --check` passed for the owned changes.

| Final input or receipt | SHA-256 |
| --- | --- |
| Native executable | `e8871447021a1373e2bfdc262a513d12487e49fd0e833bad068f226a6938ed2d` |
| Frozen `main.cpp` | `22719975ed910b0b23db841617446e492890d89f2106cc04279fc9e46824f42e` |
| `UiModel.cpp` | `ac1a381367cfee7cce61e27ebd0b094c76a730806383e9ead609622687993e28` |
| `InstrumentView.cpp` | `82c7171626f16039ac4877a8cafc12928941d51fb295a37d0f23ac6c294c6e8e` |
| Final app test | `18d23c7e845424a410e99acc7bbb31efd8751dc0bfd93b9f64b5887f7955e9b7` |
| Final workflow test | `afe7d142b22e155a17ae0f990f3189509aad069979a3bb182e4ef54d4c0b16dd` |
| Final boundary test | `29f774df69a86628e91023c47c55bae29127289640255df3ad30b105ec78b163` |
| Final chapel test | `598171f83a4cef530339d86289a3e75de98df55b57a62d5ef08442f8c0f88d7e` |
| First integrated CTest log, failure retained | `6bc1c40b99a0a6c27248ed47ffe156b25482debb83f9299348a1661c257db88c` |
| Final CTest output log | `ead880704bb89b403b0d5a8e989e1b93f3610d6d464f94a8e11e704be3d417bd` |
| Final complete `LastTest.log` copy | `cc1a963595fe45fe130a1a7c486ae4101f39dcac934c1a77d850166cfc69e79a` |
| Fresh held/idle pixel receipt | `efe4384d05edda957c127c9c9e6d4e118f96c294fcd15f5b71086dd937b24ae1` |

Scratch logs, original test copies and the four pixel captures are in
`/workspace/scratch/cd4bd06ce68f/a25-legacy-evidence/`; the failures, corrected
oracles, input identities and final outcomes are retained above for the
repository handoff. Root owns complete source qualification, publication and
current native screenshot presentation. This acceptance establishes software
event delivery, rendering and musical-state behavior with explicit SDL dummy
drivers; physical MIDI/audio, platform accessibility, deadline/latency and
acoustic-fidelity gates remain separate.
