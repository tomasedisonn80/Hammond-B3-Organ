# A23 — Synthetic MIDI replay in the native application

Actual assignment: `/root/w04_a23_native_midi_replay`, A23, logical wave 4 of
the `2026-11-14-midi-ui` session. Completed 2026-11-14 UTC. This is one actual
new worker; no previous worker or acceptance result is recounted.

## Owned result

Owned paths are [`apps/standalone/main.cpp`](../../../apps/standalone/main.cpp)
and this note. A22 owns the frozen replay header/parser and its acceptance;
A24 owns the UI replay `M` key and native MIDI CLI/modal acceptance. Root owns
CMake integration, shared status, source publication and the assignment ledger.
This worker made no commit, publication, subagent dispatch or shared-build
invocation, and did not edit another worker's source or tests.

**Implemented:** `--midi-script PATH` now runs the native SDL app against a
bounded synthetic MIDI source, through the actual `MidiInbox`, `MidiInput`,
`UiModel` and `Session` path. It uses the existing MIDI retirement and release
acknowledgment machinery. The native device is never opened or enumerated in
this mode, including when the user opens the MIDI modal or presses Apply.

The strict Release syntax checks passed. Four focused runtime author probes
passed on the first built candidate. After restoring two original UI-only error
messages, nine final probes produced their expected outcomes on the rebuilt
candidate. One earlier modal fixture was correctly rejected because its author
used the unsupported UI-script token `Enter` instead of `Return`; that fixture
failure is retained below. These are bounded author probes, not the later
independent native MIDI acceptance suite or physical controller qualification.

Read inputs included `AGENTS.md`, current README/status/next steps and session
scope, the MIDI/UI atlas summary, [`MIDI_INPUT.md`](../../MIDI_INPUT.md),
[`MIDI_BACKEND.md`](../../MIDI_BACKEND.md), the current main-loop lifecycle,
`MidiInput.h`, `MidiDevice.h/.cpp`, `ScriptedInput.h/.cpp`, `InstrumentView.h/.cpp`,
A22's frozen `MidiReplay.h`, and the subsequently written
[`MIDI_REPLAY.md`](../../MIDI_REPLAY.md). This note does not claim a separate
complete rereading of the atlas.

## Admission and bounded execution

`--midi-script` excludes `--midi-port`, `--list-midi` and `--smoke-ms`.
Combining it with `--input-script` requires both admitted plans to have the same
duration. Both complete input files are loaded before any output is opened.
The existing distinct-file guard now includes both scripts: canonical aliases,
existing hard links and leaf symlinks cannot make a script, state, screenshot or
diagnostic output overwrite another selected file. Unexpected identity-comparison
errors reject instead of being silently ignored. A22's loader owns the bounded
regular-file and nonsymlink admission of the MIDI input itself.

The synthetic source starts disconnected. Bytes supplied while closed increment
`ignored_while_closed`; they never enter a future epoch. Each explicit `connect`
requests a fresh epoch, even when the source is already active. Retirement first
stops decoding and synthetic admission, then resets the old inbox only with the
single main-thread producer quiescent. The same three MIDI scoped releases are
posted in their existing order. A pending new epoch waits for the actual release
sequence acknowledgment, confirmed global recovery or the existing joined audio
stop boundary. All following MIDI script records remain behind that pending open
barrier, including equal-time bytes.

Each main-loop turn visits at most **512 due MIDI script records**, then reaches
the unchanged common drain of at most **32 inbox packets**. The loop preserves
source order and its cursor. Producing before draining permits actual inbox
saturation: the 257th push faults a full 256-packet inbox. That fault retires the
epoch and discards its queued packets. No synthetic diagnostic is substituted
for an overflow. Backend fault records use the real inbox fault flag and the
same retirement path. Expected script backend faults and resulting inbox
overflow are separately counted without creating a generic execution error;
failed Session submissions, audio errors and incomplete runs still fail.

Global Panic, audio restart/removal/failure and observed Session recovery retain
their common `retire_midi()` entry point, which also cancels a pending synthetic
connection request. No failed or cancelled request is retried. Only a later
explicit script `connect` can request reopening. The routing remains the CLI
configuration throughout replay; modal Apply explains that the script controls
input and does not change routing, enumerate ports or open a native device.
Modal Disconnect performs the common retirement.

Replay completes only after its declared duration, all records delivered,
an empty inbox, no pending connect or retirement, and the existing last-submitted
Session sequence/control/save acknowledgment. Paired runs also require complete
UI-script delivery. The existing additional **2000 ms** drain interval bounds
failure to finish. An interrupted or incomplete run returns nonzero.

The app retains observations and final musical state before normal shutdown
cleanup. A legal held final state is therefore inspectable; the joined shutdown
must still clear all holds. MIDI-only runs participate in the same observation
and accepted-command accounting. UI-only observation capacity stays **512**;
MIDI-enabled runs reserve a bounded **8704** observations so the 2048-event MIDI
plan does not inherit the smaller UI-only allowance.

## Diagnostics and visible source identity

Schema remains **2**, and every existing MIDI field remains present. Added MIDI
fields are `source`, `arrival_time_source` and `arrival_time_is_sample_time`.
Sources are explicitly `synthetic-replay`, `native` or `none`. Native device
information and callback counters retain their actual values: synthetic epochs
never set the native generation, port or state to an opened value.

An optional top-level `midi_replay` object appears only for `--midi-script`.
It retains completion/pass/delivery flags; scheduled and delivered records;
scheduled, offered, accepted, closed, rejected and discarded packets; connect,
disconnect and fault counters; pending-open barriers and cancelled intent;
512-record budget/observed maxima; pre-shutdown connected/faulted/pending state;
and the shared final sequence and musical observations. Its `failure_count`
retains application errors, distinct from intentional backend/overflow counts.
`dropped_packets` is closed bytes plus rejected pushes plus packets discarded
from the old queue. `delivered_events` counts consumed script records, including
records whose declared disposition is a counted drop or injected fault.

Receipt nanoseconds are sampled from `steady_clock` on the synthetic producer's
main thread. Both the source marker and explicit `arrival_time_is_sample_time:
false` identify them as synthetic diagnostic metadata. Script milliseconds do
not become Engine frames or sample offsets; the common next-callback-boundary
policy remains unchanged. Equal-time records from the separate UI and MIDI
streams do not define a globally merged or sample-accurate schedule.

The original top-level `replay` remains UI-script-specific: its scheduled/pushed
events and SDL delivery meaning are unchanged. Common results add the explicit
observation capacity. Original UI-only timeout/failure wording was restored
after A24 detected a fixture mismatch caused by an unnecessary generalized
message. MIDI-enabled failures use explicit MIDI replay wording.

Two actual 1280x900 backbuffers were inspected: a held three-division view and
the MIDI modal after Apply. They show **Synthetic replay** and **MIDI NOT
CONNECTED**, rather than claiming a physical connection. No cabinet/control
geometry was changed. Residual UI detail: the existing modal footer still gives
the generic native Apply instruction, while the replay status explicitly says
that only the script connects; the view also repeats the synthetic prefix in
that status. Those view details are outside this assignment's owned file.
This inspection is source-label evidence, not a new atlas-fidelity comparison.

## Executed author probes

All native invocations explicitly set `SDL_AUDIODRIVER=dummy` and
`SDL_VIDEODRIVER=dummy`, used an absent per-case state path, and had a ten-second
subprocess timeout. Positive cases required zero application errors, positive
actual audio callbacks, complete final acknowledgment, no holds after joined
shutdown, native generation/callback messages zero, and the explicit synthetic
source. Source and executable hashes were checked unchanged before and after
each group.

| First built candidate | Observed result |
| --- | --- |
| Three divisions and raw decoder outcomes, 600 ms / 9 records | Upper 60, Lower 64 and PedalId 1 held before shutdown; CC11 expression exactly 96/127. One each malformed, unmapped-channel, out-of-range and unsupported packet; 8 packets decoded, 4 actions, one epoch, 3 accepted note Ons. |
| Retirement and reconnect, 800 ms / 12 records | One explicit backend fault, one queued stale packet discarded, two closed bytes ignored, three epochs, two pending-open barriers, three release batches / nine accepted scoped releases. Final musical state empty; no automatic reconnect. |
| Real overflow and producer budget, 600 ms / 603 records | A 600-byte burst accepted 256 packets before the 257th attempt overflowed. Exactly 256 queued packets discarded, one rejected push, 343 later closed bytes ignored. Maximum producer work exactly 512 records in a turn; budget exhaustion counted. A later explicit connect delivered only Upper 64, with the stale Upper 60 absent. |
| Paired UI/MIDI ownership, 1000 ms | After UI focus loss, Lower 64 remained held by MIDI. A fresh UI Upper 60 survived the later MIDI disconnect and remained the final pre-shutdown hold. Both replays passed; three total accepted note Ons. |

Observed maximum common drains in these four runs were respectively 3, 1, 1
and 1, all below 32. The observed 512 producer maximum was tested, but these
author probes do not independently establish a full 32-packet drain boundary.
The actual retained audio callback counts were 63, 76, 58 and 95; those are
observations, not deadline expectations.

| Final rebuilt candidate | Observed result |
| --- | --- |
| Synthetic MIDI modal, 800 ms | Ctrl+M opens the actual modal, five Tab presses select Apply, Return activates it. Both replays pass; Upper 60 remains held; exactly one decoder epoch/connection, native generation zero and no native callback messages. |
| Three prohibited combinations | `--midi-port`, `--smoke-ms` and `--list-midi` each return 2, with the existing diagnostic sentinel bytes preserved. |
| Unequal paired durations | MIDI 800 ms / UI 500 ms returns 1 before output, preserving the sentinel. |
| Existing hardlink output alias | Diagnostics hardlinked to the MIDI input returns 1; input and alias bytes remain unchanged. |
| Symlink MIDI input | Returns 1 before output; input and diagnostic sentinel unchanged. |
| Interrupted UI-only replay | Returns 1 and retains `Native input replay failed or was interrupted`. |
| Interrupted paired replay | Returns 1 with `Native MIDI replay failed or was interrupted`. |

The first modal attempt returned 1 at input admission with `Input replay line
15: unsupported key, modifiers, or repeat (0 or 1)`. The probe used `Enter`;
the existing UI-script grammar correctly accepts `Return`. Only that fixture
was corrected. No production parser allowance or acceptance criterion changed.
In total the worker launched **14 processes**: four initial expected successes,
one retained invalid author fixture, then nine final expected outcomes. No
production defect was found by these probes. The two compatibility error-text
changes were the only production changes after the four initial passes.

## Reproduction and exact identities

Working directory: `/workspace/scratch/cd4bd06ce68f/Hammond-B3-Organ`.
Observed repository HEAD was `e09107414896c2c53dad124a74f60c8043fadfe4`.
All checks used the concurrent uncommitted MIDI/UI candidate, not that commit
alone. Root performed the coordinated native builds; A23 only ran strict syntax
checks and the resulting executable. No new remote/publication qualification is
claimed here.

Compiler: GNU C++ **14.2.0**. The configured native build is Release with
`HAMMOND_BUILD_STANDALONE=ON` and `HAMMOND_ENABLE_MIDI=ON`, using root's prepared
RtMidi/ALSA dependency and SDL2 tree. Syntax checks reconstructed the exact
`main.cpp` command from `build-native/compile_commands.json`, removed the object
output/compile-only arguments and appended `-fsyntax-only
-Wunused-const-variable=1`. The retained flags include C++20, `-O3 -DNDEBUG`,
`-Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror`.
Both the first and final main-source syntax checks passed.

The runtime command shape was:

```sh
SDL_AUDIODRIVER=dummy SDL_VIDEODRIVER=dummy \
  /workspace/scratch/cd4bd06ce68f/build-native/apps/standalone/hammond_standalone \
  --state /workspace/scratch/cd4bd06ce68f/a23-native-midi-smoke/CASE.b3controls \
  --midi-script /workspace/scratch/cd4bd06ce68f/a23-native-midi-smoke/CASE.b3midi \
  --diagnostics /workspace/scratch/cd4bd06ce68f/a23-native-midi-smoke/CASE.json
```

Paired/modal cases additionally used their `--input-script CASE.b3ui` file.
The divisions/modal captures also supplied `--screenshot CASE.bmp`. Scratch
records `evidence.json` and `final-evidence.json` retain exact counters and the
before/after source hashes; case inputs, JSON, BMPs and stderr accompany them.
`modal-invalid-enter.stderr` retains the invalid fixture failure. These scratch
probes are not committed acceptance tests.

| Qualified input | SHA-256 |
| --- | --- |
| Initial `main.cpp`, four behavioral probes | `8152793358e85840110b4191c5058c1b5cf661851271120b5e0a618d7a766e44` |
| Initial native executable | `48e308cfea28c7d26c9bf3efe99bf5a52eee80064db39c31f4b878e13bebd42e` |
| Final `main.cpp`, two restored UI-only messages | `22719975ed910b0b23db841617446e492890d89f2106cc04279fc9e46824f42e` |
| Final native executable, nine expected outcomes | `e8871447021a1373e2bfdc262a513d12487e49fd0e833bad068f226a6938ed2d` |
| Frozen `MidiReplay.h` | `c0a62c0d33e7b0c3b90237e82cf631222d3d5274bb6b45fa797906e1e77a3948` |
| A22 `MidiReplay.cpp` | `a61047fcb0da050eae35a10e86205a496d13ea7d00fb8b113c8682d1556a88db` |
| A24 `ScriptedInput.cpp`, final group | `7c143db56b1eda113886a3e2cd63ec3570483921adc2b57e1a4c8f0ef6235531` |

`git diff --check` also passed for the candidate. These hashes identify the
specific supplied source and binaries, not a complete frozen repository tree.
The four original positive probes were not needlessly repeated after changes
limited to failure text; the final modal and interrupted-run probes specifically
exercise the rebuilt integration and both affected failure-message branches.

## Limits and next work

Independent native replay acceptance should now exercise the final integrated
source with exact packet conservation and state expectations: channel remapping,
duplicate ownership, mixed UI/control edits, maximum event plans, the full drain
budget, same-time fresh epochs, pending intent cancellation by global Panic,
audio restart and Session recovery, and deliberate failed bounded completion.
It must retain actual pre-shutdown state and last-sequence acknowledgment rather
than accepting only process exit. A31 owns that forthcoming broad native work;
A25 owns legacy native-suite schema reconciliation.

No physical MIDI device, MIDI callback timing, hotplug, driver failure, audio
hardware, Windows/macOS runtime, whole-repository test run, sanitizer gate or
atlas-fidelity comparison was qualified by this worker. The replay source uses
real application queues and callbacks with explicit dummy audio/video; it does
not become a hardware or acoustic fidelity pass.
